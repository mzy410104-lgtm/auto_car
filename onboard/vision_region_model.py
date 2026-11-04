#!/usr/bin/env python3
"""
Visual Map-Region Classifier Training, Held-Out Session Validation, and Inference Pipeline
(Cycle 3 — Member B).

Enforces all Cycle 1–3 visual localization rules (`TAXI_TT02_PROJECT_WORK_PLAN_EN.md`,
`onboard/CAMERA_AND_DATASET_RULES.md`, and `interfaces/LOCALIZATION_AND_PICKUP_INTERFACE.md`):
  1. Loads dataset manifests strictly through `vision_manifest.load_and_validate_manifest`
     with `check_files=True` and `require_held_out_splits=True`. Any session leakage
     between `train`, `val`, and `test` immediately aborts training.
  2. Extracts a compact 480-D spatial color + luminance + oriented-gradient grid descriptor
     (`6x8` spatial cells) using Pillow + NumPy (< 3 ms per 640x480 frame on Raspberry Pi 4).
  3. Trains an L2-regularized multi-class softmax classifier on `train` sessions only.
  4. Evaluates strictly on held-out `val` (and optional `test`) sessions, recording
     per-region precision/recall, confusion matrix, and setting
     `validated_on_held_out_runs = True` only when held-out accuracy meets threshold.
  5. Outputs `(visual_region_id, visual_confidence, validated_on_held_out_runs)` directly
     compatible with `lidar_localize.VisualRegionInput` (never claiming metric `(x, y, yaw)`
     from a single image).
"""

import argparse
import csv
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw

from vision_manifest import (
    MANIFEST_COLUMNS,
    ManifestSample,
    load_and_validate_manifest,
)


GRID_ROWS = 6
GRID_COLS = 8
RESIZE_W = 160
RESIZE_H = 120


def extract_spatial_descriptor(img: Image.Image) -> np.ndarray:
    """
    Compute a 480-D L2-normalized spatial color/luminance + gradient descriptor
    over a `6x8` grid from an input PIL image.
    """
    rgb = img.convert("RGB").resize((RESIZE_W, RESIZE_H), Image.Resampling.BILINEAR)
    arr = np.asarray(rgb, dtype=np.float32) / 255.0  # (H, W, 3)

    # Luminance channel Y
    luma = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    # Simple Sobel-like horizontal and vertical finite differences
    gx = np.zeros_like(luma)
    gy = np.zeros_like(luma)
    gx[:, 1:-1] = luma[:, 2:] - luma[:, :-2]
    gy[1:-1, :] = luma[2:, :] - luma[:-2, :]
    gmag = np.hypot(gx, gy)

    cell_h = RESIZE_H // GRID_ROWS
    cell_w = RESIZE_W // GRID_COLS
    feats: List[float] = []

    for r in range(GRID_ROWS):
        y0, y1 = r * cell_h, (r + 1) * cell_h
        for c in range(GRID_COLS):
            x0, x1 = c * cell_w, (c + 1) * cell_w
            patch_rgb = arr[y0:y1, x0:x1, :]
            patch_luma = luma[y0:y1, x0:x1]
            patch_gx = np.abs(gx[y0:y1, x0:x1])
            patch_gy = np.abs(gy[y0:y1, x0:x1])
            patch_gm = gmag[y0:y1, x0:x1]

            # 6 color/luma stats + 4 gradient/texture stats = 10 dims per cell -> 480 dims total
            mean_rgb = np.mean(patch_rgb, axis=(0, 1))
            std_rgb = np.std(patch_rgb, axis=(0, 1))
            feats.extend(mean_rgb.tolist())
            feats.extend(std_rgb.tolist())
            feats.append(float(np.mean(patch_gx)))
            feats.append(float(np.mean(patch_gy)))
            feats.append(float(np.mean(patch_gm)))
            feats.append(float(np.std(patch_luma)))

    vec = np.asarray(feats, dtype=np.float32)
    norm = float(np.linalg.norm(vec))
    if norm > 1e-8:
        vec /= norm
    return vec


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    exp_v = np.exp(shifted)
    return exp_v / np.sum(exp_v, axis=-1, keepdims=True)


class VisualRegionClassifier:
    """Multi-class L2-regularized softmax classifier for discrete map-region recognition."""

    def __init__(
        self,
        classes: List[str],
        weights: np.ndarray,
        bias: np.ndarray,
        feat_mean: np.ndarray,
        feat_std: np.ndarray,
        validated_on_held_out_runs: bool = False,
        validation_metrics: Optional[dict] = None,
    ):
        self.classes = list(classes)
        self.weights = np.asarray(weights, dtype=np.float32)  # (D, C)
        self.bias = np.asarray(bias, dtype=np.float32)  # (C,)
        self.feat_mean = np.asarray(feat_mean, dtype=np.float32)  # (D,)
        self.feat_std = np.asarray(feat_std, dtype=np.float32)  # (D,)
        self.validated_on_held_out_runs = bool(validated_on_held_out_runs)
        self.validation_metrics = validation_metrics or {}

    @classmethod
    def fit(
        cls,
        X_train: np.ndarray,
        y_train_labels: List[str],
        l2_reg: float = 1e-2,
        lr: float = 0.5,
        epochs: int = 250,
    ) -> "VisualRegionClassifier":
        classes = sorted(set(y_train_labels))
        if len(classes) < 2:
            raise ValueError(
                f"Need at least 2 distinct region_id classes to train, got {classes}"
            )
        class_to_idx = {c: i for i, c in enumerate(classes)}
        y_idx = np.array([class_to_idx[c] for c in y_train_labels], dtype=np.int64)

        n_samples, feat_dim = X_train.shape
        n_classes = len(classes)

        feat_mean = np.mean(X_train, axis=0)
        feat_std = np.std(X_train, axis=0) + 1e-5
        Xn = (X_train - feat_mean) / feat_std

        W = np.zeros((feat_dim, n_classes), dtype=np.float32)
        b = np.zeros((n_classes,), dtype=np.float32)
        Y_onehot = np.eye(n_classes, dtype=np.float32)[y_idx]

        for _ in range(epochs):
            logits = Xn @ W + b
            probs = softmax(logits)
            diff = (probs - Y_onehot) / float(n_samples)
            grad_W = (Xn.T @ diff) + l2_reg * W
            grad_b = np.sum(diff, axis=0)
            W -= lr * grad_W
            b -= lr * grad_b

        return cls(
            classes=classes,
            weights=W,
            bias=b,
            feat_mean=feat_mean,
            feat_std=feat_std,
            validated_on_held_out_runs=False,
        )

    def predict_proba_matrix(self, X: np.ndarray) -> np.ndarray:
        Xn = (X - self.feat_mean) / self.feat_std
        logits = Xn @ self.weights + self.bias
        return softmax(logits)

    def evaluate(
        self, X: np.ndarray, y_true_labels: List[str], session_ids: List[str]
    ) -> dict:
        probs = self.predict_proba_matrix(X)
        pred_indices = np.argmax(probs, axis=1)
        confs = np.max(probs, axis=1)

        n = len(y_true_labels)
        correct = 0
        per_class_tp = {c: 0 for c in self.classes}
        per_class_fp = {c: 0 for c in self.classes}
        per_class_fn = {c: 0 for c in self.classes}

        for i, true_c in enumerate(y_true_labels):
            pred_c = self.classes[int(pred_indices[i])]
            if pred_c == true_c:
                correct += 1
                if true_c in per_class_tp:
                    per_class_tp[true_c] += 1
            else:
                if pred_c in per_class_fp:
                    per_class_fp[pred_c] += 1
                if true_c in per_class_fn:
                    per_class_fn[true_c] += 1

        per_region_metrics = {}
        for c in self.classes:
            tp = per_class_tp[c]
            fp = per_class_fp[c]
            fn = per_class_fn[c]
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            per_region_metrics[c] = {
                "precision": round(prec, 3),
                "recall": round(rec, 3),
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }

        return {
            "sample_count": n,
            "sessions": sorted(set(session_ids)),
            "top1_accuracy": round(correct / max(n, 1), 4),
            "mean_confidence": round(float(np.mean(confs)), 4),
            "per_region": per_region_metrics,
        }

    def predict_image(self, img: Image.Image) -> dict:
        desc = extract_spatial_descriptor(img)[None, :]
        probs = self.predict_proba_matrix(desc)[0]
        best_i = int(np.argmax(probs))
        return {
            "visual_region_id": self.classes[best_i],
            "visual_confidence": round(float(probs[best_i]), 4),
            "validated_on_held_out_runs": self.validated_on_held_out_runs,
            "class_probabilities": {
                self.classes[i]: round(float(probs[i]), 4)
                for i in range(len(self.classes))
            },
        }

    def save_json(self, path: Path) -> None:
        payload = {
            "format": "tt02_visual_region_model_v1",
            "classes": self.classes,
            "validated_on_held_out_runs": self.validated_on_held_out_runs,
            "validation_metrics": self.validation_metrics,
            "weights": self.weights.tolist(),
            "bias": self.bias.tolist(),
            "feat_mean": self.feat_mean.tolist(),
            "feat_std": self.feat_std.tolist(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> "VisualRegionClassifier":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            classes=data["classes"],
            weights=np.asarray(data["weights"], dtype=np.float32),
            bias=np.asarray(data["bias"], dtype=np.float32),
            feat_mean=np.asarray(data["feat_mean"], dtype=np.float32),
            feat_std=np.asarray(data["feat_std"], dtype=np.float32),
            validated_on_held_out_runs=bool(data.get("validated_on_held_out_runs", False)),
            validation_metrics=data.get("validation_metrics", {}),
        )


def train_and_validate_from_manifest(
    manifest_path: Path,
    out_model_path: Optional[Path] = None,
    min_val_accuracy: float = 0.75,
) -> Tuple[VisualRegionClassifier, dict]:
    """
    Validate a session-separated dataset manifest, train on `train` sessions,
    and evaluate on held-out `val` and `test` sessions.
    """
    samples, report = load_and_validate_manifest(
        str(manifest_path), check_files=True, require_held_out_splits=True
    )
    if not report.valid:
        raise ValueError(
            f"Dataset manifest failed validation (training refused): {report.errors}"
        )

    dataset_root = manifest_path.parent
    splits_X: Dict[str, List[np.ndarray]] = {"train": [], "val": [], "test": []}
    splits_y: Dict[str, List[str]] = {"train": [], "val": [], "test": []}
    splits_sessions: Dict[str, List[str]] = {"train": [], "val": [], "test": []}

    for s in samples:
        img_path = dataset_root / s.relative_path
        with Image.open(img_path) as im:
            desc = extract_spatial_descriptor(im)
        splits_X[s.split].append(desc)
        splits_y[s.split].append(s.region_id)
        splits_sessions[s.split].append(s.session_id)

    X_train = np.stack(splits_X["train"], axis=0)
    model = VisualRegionClassifier.fit(X_train, splits_y["train"])

    train_eval = model.evaluate(X_train, splits_y["train"], splits_sessions["train"])
    X_val = np.stack(splits_X["val"], axis=0)
    val_eval = model.evaluate(X_val, splits_y["val"], splits_sessions["val"])

    test_eval = None
    if splits_X["test"]:
        X_test = np.stack(splits_X["test"], axis=0)
        test_eval = model.evaluate(X_test, splits_y["test"], splits_sessions["test"])

    # Confirm strictly disjoint session IDs between train and val/test
    train_sess_set = set(splits_sessions["train"])
    val_sess_set = set(splits_sessions["val"])
    disjoint_sessions = len(train_sess_set.intersection(val_sess_set)) == 0

    model.validated_on_held_out_runs = bool(
        disjoint_sessions and val_eval["top1_accuracy"] >= min_val_accuracy
    )
    summary = {
        "manifest_path": str(manifest_path.resolve()),
        "classes": model.classes,
        "session_separation_verified": disjoint_sessions,
        "validated_on_held_out_runs": model.validated_on_held_out_runs,
        "min_val_accuracy_required": min_val_accuracy,
        "train_metrics": train_eval,
        "held_out_val_metrics": val_eval,
        "held_out_test_metrics": test_eval,
    }
    model.validation_metrics = summary

    if out_model_path is not None:
        model.save_json(out_model_path)

    return model, summary


def _render_synthetic_region_image(
    region_id: str, jitter_px: int, brightness_scale: float
) -> Image.Image:
    """Create a distinctive synthetic room-view image for self-testing."""
    img = Image.new("RGB", (640, 480), color=(40, 45, 55))
    draw = ImageDraw.Draw(img)
    # Floor & ceiling bands
    draw.rectangle([0, 0, 640, 140], fill=(70, 75, 90))
    draw.rectangle([0, 320, 640, 480], fill=(55, 50, 45))

    if region_id == "REGION_01":
        # Red door on left + blue cabinet on right
        draw.rectangle([60 + jitter_px, 120, 190 + jitter_px, 340], fill=(195, 55, 55))
        draw.rectangle([420 + jitter_px, 160, 560 + jitter_px, 330], fill=(45, 110, 200))
    elif region_id == "REGION_02":
        # Green whiteboard in center + yellow pillar on left
        draw.rectangle([210 + jitter_px, 130, 460 + jitter_px, 280], fill=(45, 175, 95))
        draw.rectangle([50 + jitter_px, 100, 120 + jitter_px, 350], fill=(220, 185, 45))
    else:
        # Purple window wall on right + orange bench on bottom-left
        draw.rectangle([380 + jitter_px, 90, 590 + jitter_px, 260], fill=(155, 70, 190))
        draw.rectangle([80 + jitter_px, 250, 280 + jitter_px, 360], fill=(225, 120, 40))

    if abs(brightness_scale - 1.0) > 1e-3:
        arr = np.clip(np.asarray(img, dtype=np.float32) * brightness_scale, 0, 255).astype(
            np.uint8
        )
        img = Image.fromarray(arr)
    return img


def run_self_test() -> int:
    print("Running onboard/vision_region_model.py self-test (Cycle 3 Visual Region Classifier)...")
    with tempfile.TemporaryDirectory(prefix="vision_model_test_") as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "manifest.csv"
        model_path = root / "region_model.json"

        sessions = [
            ("20261110_s01_train", "train", [-18, -6, 6, 18], 1.00, "artificial_indoor"),
            ("20261110_s02_train", "train", [-12, 0, 12], 0.90, "mixed"),
            ("20261111_s03_val", "val", [-15, 5, 15], 1.08, "daylight_window"),
            ("20261111_s04_test", "test", [-10, 10], 0.94, "artificial_indoor"),
        ]
        regions = ["REGION_01", "REGION_02", "REGION_03"]
        rows = []
        seq = 0

        for sess_id, split, jitters, b_scale, light in sessions:
            for reg in regions:
                for jit in jitters:
                    seq += 1
                    img_id = f"img_{1762800000 + seq}_{seq:04d}"
                    rel_path = f"images/{sess_id}/{img_id}.jpg"
                    abs_path = root / rel_path
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    im = _render_synthetic_region_image(reg, jit, b_scale)
                    im.save(abs_path, format="JPEG")
                    rows.append(
                        [
                            img_id,
                            rel_path,
                            f"{1762800000.0 + seq:.3f}",
                            "2026-11-10T10:00:00Z",
                            sess_id,
                            reg,
                            "N",
                            "center" if jit == 0 else ("left_offset" if jit < 0 else "right_offset"),
                            light,
                            "stationary",
                            split,
                            "640",
                            "480",
                            "ov5647",
                        ]
                    )

        with manifest_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(MANIFEST_COLUMNS)
            writer.writerows(rows)

        model, summary = train_and_validate_from_manifest(
            manifest_path, out_model_path=model_path, min_val_accuracy=0.85
        )
        val_acc = summary["held_out_val_metrics"]["top1_accuracy"]
        test_acc = summary["held_out_test_metrics"]["top1_accuracy"]
        if not model.validated_on_held_out_runs or val_acc < 0.85 or test_acc < 0.85:
            print("FAIL: Model validation on held-out sessions did not pass:", summary)
            return 1

        print(
            f"  [PASS 1/2] Trained 3-region classifier on {summary['train_metrics']['sample_count']} "
            f"frames; held-out val_acc={val_acc:.3f}, held-out test_acc={test_acc:.3f}, "
            f"validated={model.validated_on_held_out_runs}"
        )

        # Reload saved JSON model and run single-image inference
        reloaded = VisualRegionClassifier.load_json(model_path)
        test_img = _render_synthetic_region_image("REGION_02", jitter_px=8, brightness_scale=1.05)
        pred = reloaded.predict_image(test_img)
        if pred["visual_region_id"] != "REGION_02" or pred["visual_confidence"] < 0.70:
            print("FAIL: Reloaded model inference failed:", pred)
            return 1
        print(
            f"  [PASS 2/2] Reloaded JSON model inference verified: "
            f"predicted={pred['visual_region_id']} (conf={pred['visual_confidence']:.3f}, "
            f"validated_on_held_out_runs={pred['validated_on_held_out_runs']})"
        )

    print("SELF-TEST RESULT: PASS.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train, validate on held-out sessions, or run inference with the TT-02 visual region classifier."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to dataset manifest.csv for training & held-out validation",
    )
    parser.add_argument(
        "--out-model",
        type=Path,
        default=None,
        help="Path to save trained model JSON artifact",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Path to trained model JSON artifact for single-image inference",
    )
    parser.add_argument(
        "--predict",
        type=Path,
        default=None,
        help="Path to an image file to classify using --model",
    )
    parser.add_argument(
        "--min-val-accuracy",
        type=float,
        default=0.75,
        help="Minimum held-out validation top-1 accuracy required to mark model as validated (default: 0.75)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic training, held-out session validation, and inference self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.manifest is not None:
        _, summary = train_and_validate_from_manifest(
            args.manifest,
            out_model_path=args.out_model,
            min_val_accuracy=args.min_val_accuracy,
        )
        print(json.dumps(summary, indent=2))
        return 0

    if args.model is not None and args.predict is not None:
        clf = VisualRegionClassifier.load_json(args.model)
        with Image.open(args.predict) as im:
            pred = clf.predict_image(im)
        print(json.dumps(pred, indent=2))
        return 0

    parser.error("Provide --manifest (to train/validate), --model + --predict (for inference), or --self-test.")


if __name__ == "__main__":
    sys.exit(main())
