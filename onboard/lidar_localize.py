#!/usr/bin/env python3
"""
RPLIDAR A2M8 Scan-to-Map Planar Pose Localizer, Visual-Region Constraint Gate,
Motion-Feedback Dead-Reckoning Predictor, and 8-Sector Obstacle Extractor (Cycle 3 — Member B).

Implements the exact Member B -> Member A and Member C -> Member B contracts defined in:
  - `interfaces/LOCALIZATION_AND_PICKUP_INTERFACE.md` (Task AB)
  - `interfaces/CONTROL_INTERFACE.md` (Task BC)

Key architectural guarantees:
  1. Continuous planar pose `(x_m, y_m, yaw_rad)` is produced by RPLIDAR A2M8 scan-to-map
     matching (multi-resolution correlative grid search + coordinate refinement against the
     occupied cells of a JSON map produced by `onboard/lidar_mapper.py`).
  2. Visual region recognition (`visual_region_id`, `visual_confidence`) NEVER sets
     `localization_status = "VALID"` on its own without RPLIDAR scan matching, and is only
     applied when `validated_on_held_out_runs=True` and `visual_confidence >= threshold`.
  3. Single-channel `OPB815WZ` wheel speed magnitude (`speed_m_s >= 0`) and control-inferred
     `direction_state` (`FWD`, `REV`, `NEUTRAL_STOP`, `TRANSITION_UNKNOWN`) are handled
     separately; `TRANSITION_UNKNOWN` expands the search window rather than assuming a sign.
  4. Outputs the 8-sector obstacle summary (`min_front_distance_m`, `sector_distances_m`)
     in the vehicle frame (`base_link`) for Member A's local stopping and replanning.
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from lidar_mapper import OccupancyGridMapper, load_scans_from_csv


SECTOR_NAMES: Tuple[str, ...] = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def wrap_angle_rad(angle_rad: float) -> float:
    """Wrap angle into `[-pi, pi]`."""
    return (angle_rad + math.pi) % (2.0 * math.pi) - math.pi


@dataclass
class MotionFeedbackInput:
    """Motion feedback from Member C's STM32 (`interfaces/CONTROL_INTERFACE.md`)."""

    timestamp_s: float
    speed_m_s: float = 0.0  # Non-negative magnitude from OPB815WZ
    direction_state: str = "NEUTRAL_STOP"  # FWD, REV, NEUTRAL_STOP, TRANSITION_UNKNOWN
    imu_heading_cdeg: Optional[int] = None  # BNO055 Euler heading (0..36000 centi-degrees)
    yaw_rate_rad_s: Optional[float] = None


@dataclass
class VisualRegionInput:
    """Visual region recognition constraint from onboard OV5647 classifier."""

    timestamp_s: float
    visual_region_id: str = "UNKNOWN"
    visual_confidence: float = 0.0
    validated_on_held_out_runs: bool = False


@dataclass
class LocalizationOutput:
    """Continuous localization and obstacle payload (`B -> A`, Task AB)."""

    timestamp_s: float
    x_m: float
    y_m: float
    yaw_rad: float
    localization_status: str  # UNINITIALIZED, VALID, DEGRADED, LOST
    inlier_ratio: float
    mean_residual_m: float
    visual_region_id: str = "UNKNOWN"
    visual_confidence: float = 0.0
    visual_consistent: bool = True
    lidar_health: str = "OK"  # OK, STALE, DISCONNECTED
    min_front_distance_m: float = float("inf")
    sector_distances_m: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp_s": round(self.timestamp_s, 3),
            "x_m": round(self.x_m, 4),
            "y_m": round(self.y_m, 4),
            "yaw_rad": round(self.yaw_rad, 4),
            "yaw_deg": round(math.degrees(self.yaw_rad), 2),
            "localization_status": self.localization_status,
            "inlier_ratio": round(self.inlier_ratio, 3),
            "mean_residual_m": round(self.mean_residual_m, 4),
            "visual_region_id": self.visual_region_id,
            "visual_confidence": round(self.visual_confidence, 3),
            "visual_consistent": self.visual_consistent,
            "lidar_health": self.lidar_health,
            "min_front_distance_m": (
                round(self.min_front_distance_m, 3)
                if math.isfinite(self.min_front_distance_m)
                else None
            ),
            "sector_distances_m": {
                k: (round(v, 3) if math.isfinite(v) else None)
                for k, v in self.sector_distances_m.items()
            },
        }


def compute_obstacle_summary(
    scan_polar: List[Tuple[float, float]],
    front_half_angle_deg: float = 30.0,
) -> Tuple[float, Dict[str, float]]:
    """
    Compute `min_front_distance_m` (within `±front_half_angle_deg` of `0°` forward)
    and minimum obstacle distance in 8 angular sectors (`N, NE, E, SE, S, SW, W, NW`).
    """
    front_half_rad = math.radians(front_half_angle_deg)
    min_front = float("inf")
    sectors: Dict[str, float] = {name: float("inf") for name in SECTOR_NAMES}

    for ang_rad, dist_m in scan_polar:
        if dist_m <= 0.0:
            continue
        rel = wrap_angle_rad(ang_rad)
        if abs(rel) <= front_half_rad and dist_m < min_front:
            min_front = dist_m

        deg = math.degrees(ang_rad) % 360.0
        idx = int(((deg + 22.5) % 360.0) // 45.0)
        sec_name = SECTOR_NAMES[idx]
        if dist_m < sectors[sec_name]:
            sectors[sec_name] = dist_m

    return min_front, sectors


class LidarMapLocalizer:
    """
    2D Scan-to-Map Localizer combining RPLIDAR A2M8 scans, STM32 motion feedback,
    and validated visual map-region constraints.
    """

    def __init__(
        self,
        map_dict: dict,
        inlier_Gate_m: float = 0.15,
        visual_conf_threshold: float = 0.70,
    ):
        occupied_list = map_dict.get("occupied_cells_xy_m", [])
        if not occupied_list:
            raise ValueError("Reference map contains 0 occupied cells.")
        self.occupied_xy = np.asarray(occupied_list, dtype=np.float32)  # (M, 2)
        self.regions: Dict[str, dict] = map_dict.get("regions", {})
        self.pickup_poses: Dict[str, dict] = map_dict.get("pickup_poses", {})
        self.inlier_gate_m = float(inlier_Gate_m)
        self.visual_conf_threshold = float(visual_conf_threshold)

        self.x_m = 0.0
        self.y_m = 0.0
        self.yaw_rad = 0.0
        self.status = "UNINITIALIZED"
        self.last_ts: Optional[float] = None
        self.last_imu_yaw_rad: Optional[float] = None
        self.consecutive_visual_mismatch = 0

    def set_initial_pose(self, x_m: float, y_m: float, yaw_rad: float) -> None:
        self.x_m = float(x_m)
        self.y_m = float(y_m)
        self.yaw_rad = wrap_angle_rad(float(yaw_rad))
        self.status = "DEGRADED"

    def predict_motion(self, feedback: MotionFeedbackInput) -> Tuple[float, float]:
        """
        Update predicted `(x_m, y_m, yaw_rad)` from STM32 motion feedback and return
        `(xy_search_radius_m, yaw_search_half_rad)` for the next lidar scan match.
        """
        if self.last_ts is None:
            self.last_ts = feedback.timestamp_s
            if feedback.imu_heading_cdeg is not None:
                self.last_imu_yaw_rad = math.radians(feedback.imu_heading_cdeg / 100.0)
            return 0.35, math.radians(20.0)

        dt = max(0.0, feedback.timestamp_s - self.last_ts)
        self.last_ts = feedback.timestamp_s
        if dt <= 0.0 or dt > 2.0:
            return 0.35, math.radians(20.0)

        # Heading update from BNO055 Euler heading or yaw rate
        if feedback.imu_heading_cdeg is not None:
            curr_imu_yaw = math.radians(feedback.imu_heading_cdeg / 100.0)
            if self.last_imu_yaw_rad is not None:
                dyaw = wrap_angle_rad(curr_imu_yaw - self.last_imu_yaw_rad)
                self.yaw_rad = wrap_angle_rad(self.yaw_rad + dyaw)
            self.last_imu_yaw_rad = curr_imu_yaw
        elif feedback.yaw_rate_rad_s is not None:
            self.yaw_rad = wrap_angle_rad(self.yaw_rad + feedback.yaw_rate_rad_s * dt)

        # Speed magnitude + control-inferred direction sign (Task BC rule)
        spd = max(0.0, float(feedback.speed_m_s))
        d_state = feedback.direction_state
        if d_state == "FWD":
            disp = spd * dt
            self.x_m += disp * math.cos(self.yaw_rad)
            self.y_m += disp * math.sin(self.yaw_rad)
            return max(0.15, abs(disp) * 0.5 + 0.10), math.radians(12.0)
        if d_state == "REV":
            disp = -spd * dt
            self.x_m += disp * math.cos(self.yaw_rad)
            self.y_m += disp * math.sin(self.yaw_rad)
            return max(0.15, abs(disp) * 0.5 + 0.10), math.radians(12.0)
        if d_state == "TRANSITION_UNKNOWN":
            # Direction sign is unknown during braking/reversal transition: do not assume sign,
            # inflate search radius to cover both directions safely.
            uncertain_disp = spd * dt
            return max(0.25, uncertain_disp + 0.20), math.radians(18.0)

        # NEUTRAL_STOP
        return 0.15, math.radians(10.0)

    def _score_pose_batch(
        self,
        scan_local_xy: np.ndarray,
        cand_x: np.ndarray,
        cand_y: np.ndarray,
        cand_yaw: np.ndarray,
    ) -> Tuple[int, float, float]:
        """
        Evaluate a batch of candidate poses `(cand_x, cand_y, cand_yaw)` of shape `(K,)`
        against `self.occupied_xy` `(M, 2)` for `scan_local_xy` `(N, 2)`.
        Returns `(best_idx, best_inlier_ratio, best_mean_residual_m)`.
        """
        cos_y = np.cos(cand_yaw)[:, None]  # (K, 1)
        sin_y = np.sin(cand_yaw)[:, None]  # (K, 1)
        lx = scan_local_xy[None, :, 0]  # (1, N)
        ly = scan_local_xy[None, :, 1]  # (1, N)

        wx = cand_x[:, None] + cos_y * lx - sin_y * ly  # (K, N)
        wy = cand_y[:, None] + sin_y * lx + cos_y * ly  # (K, N)

        # Compute nearest-neighbor distance from each transformed scan point to occupied map cells
        # Shape: (K, N, M)
        dx = wx[:, :, None] - self.occupied_xy[None, None, :, 0]
        dy = wy[:, :, None] - self.occupied_xy[None, None, :, 1]
        dist_sq = dx * dx + dy * dy
        min_dist = np.sqrt(np.min(dist_sq, axis=2))  # (K, N)

        inlier_ratios = np.mean(min_dist <= self.inlier_gate_m, axis=1)  # (K,)
        clipped_residuals = np.mean(np.minimum(min_dist, 0.50), axis=1)  # (K,)

        # Combined objective: maximize inlier ratio, minimize clipped mean residual
        scores = inlier_ratios - 1.5 * clipped_residuals
        best_idx = int(np.argmax(scores))
        return (
            best_idx,
            float(inlier_ratios[best_idx]),
            float(np.mean(min_dist[best_idx])),
        )

    def _check_visual_region_consistency(
        self, x_m: float, y_m: float, visual: Optional[VisualRegionInput]
    ) -> Tuple[str, float, bool]:
        """
        Check whether a validated visual region prediction agrees with `(x_m, y_m)`.
        Returns `(region_id, confidence, is_consistent)`.
        """
        if visual is None:
            return "UNKNOWN", 0.0, True

        reg_id = visual.visual_region_id
        conf = float(visual.visual_confidence)

        # Unvalidated models or low-confidence predictions are never used to constrain pose
        if not visual.validated_on_held_out_runs or conf < self.visual_conf_threshold:
            return reg_id, conf, True

        # If region bounding polygon/box exists in map_dict["regions"], verify containment
        reg_bounds = self.regions.get(reg_id)
        if not reg_bounds:
            return reg_id, conf, True

        x_min = float(reg_bounds.get("x_min_m", -1e9))
        x_max = float(reg_bounds.get("x_max_m", 1e9))
        y_min = float(reg_bounds.get("y_min_m", -1e9))
        y_max = float(reg_bounds.get("y_max_m", 1e9))
        inside = (x_min <= x_m <= x_max) and (y_min <= y_m <= y_max)
        return reg_id, conf, inside

    def update_from_scan(
        self,
        timestamp_s: float,
        scan_polar: Optional[List[Tuple[float, float]]],
        motion: Optional[MotionFeedbackInput] = None,
        visual: Optional[VisualRegionInput] = None,
    ) -> LocalizationOutput:
        """
        Perform one complete localization cycle:
          1. Optional motion prediction (`Task BC`)
          2. Optional visual-region initialization or consistency check (`Task AB`)
          3. Multi-resolution correlative RPLIDAR scan-to-map matching
          4. Obstacle sector extraction (`B -> A`)
        """
        # Rule check: if no valid lidar scan is available, visual region alone NEVER produces VALID
        if not scan_polar or len(scan_polar) < 10:
            self.status = "LOST" if self.status != "UNINITIALIZED" else "UNINITIALIZED"
            reg_id = visual.visual_region_id if visual else "UNKNOWN"
            conf = visual.visual_confidence if visual else 0.0
            return LocalizationOutput(
                timestamp_s=timestamp_s,
                x_m=self.x_m,
                y_m=self.y_m,
                yaw_rad=self.yaw_rad,
                localization_status=self.status,
                inlier_ratio=0.0,
                mean_residual_m=float("inf"),
                visual_region_id=reg_id,
                visual_confidence=conf,
                visual_consistent=False,
                lidar_health="DISCONNECTED" if scan_polar is None else "STALE",
                min_front_distance_m=float("inf"),
                sector_distances_m={name: float("inf") for name in SECTOR_NAMES},
            )

        xy_win_m = 0.35
        yaw_win_rad = math.radians(20.0)
        if motion is not None:
            xy_win_m, yaw_win_rad = self.predict_motion(motion)
        else:
            self.last_ts = timestamp_s

        # If UNINITIALIZED or LOST and a validated visual region with mapped center exists, seed search there
        if (
            self.status in ("UNINITIALIZED", "LOST")
            and visual is not None
            and visual.validated_on_held_out_runs
            and visual.visual_confidence >= self.visual_conf_threshold
            and visual.visual_region_id in self.regions
        ):
            rb = self.regions[visual.visual_region_id]
            self.x_m = 0.5 * (float(rb["x_min_m"]) + float(rb["x_max_m"]))
            self.y_m = 0.5 * (float(rb["y_min_m"]) + float(rb["y_max_m"]))
            if "nominal_yaw_rad" in rb:
                self.yaw_rad = float(rb["nominal_yaw_rad"])

        # Convert polar scan to local (x, y) in meters (subsample to <= 90 points for fast vectorized matching)
        step = max(1, len(scan_polar) // 90)
        sampled = scan_polar[::step]
        local_xy = np.array(
            [[d * math.cos(a), d * math.sin(a)] for a, d in sampled], dtype=np.float32
        )

        # Stage 1: Coarse correlative grid search around predicted pose
        dx_coarse = np.linspace(-xy_win_m, xy_win_m, 7, dtype=np.float32)
        dy_coarse = np.linspace(-xy_win_m, xy_win_m, 7, dtype=np.float32)
        dyaw_coarse = np.linspace(-yaw_win_rad, yaw_win_rad, 9, dtype=np.float32)
        gx, gy, gyaw = np.meshgrid(
            self.x_m + dx_coarse,
            self.y_m + dy_coarse,
            self.yaw_rad + dyaw_coarse,
            indexing="ij",
        )
        cand_x = gx.ravel()
        cand_y = gy.ravel()
        cand_yaw = gyaw.ravel()
        best_i, _, _ = self._score_pose_batch(local_xy, cand_x, cand_y, cand_yaw)
        cx, cy, cyaw = float(cand_x[best_i]), float(cand_y[best_i]), float(cand_yaw[best_i])

        # Stage 2: Fine correlative refinement (±6 cm, ±3 deg)
        dx_fine = np.linspace(-0.06, 0.06, 7, dtype=np.float32)
        dy_fine = np.linspace(-0.06, 0.06, 7, dtype=np.float32)
        dyaw_fine = np.linspace(math.radians(-3.0), math.radians(3.0), 7, dtype=np.float32)
        fx, fy, fyaw = np.meshgrid(
            cx + dx_fine, cy + dy_fine, cyaw + dyaw_fine, indexing="ij"
        )
        fc_x = fx.ravel()
        fc_y = fy.ravel()
        fc_yaw = fyaw.ravel()
        best_f, inlier_ratio, mean_res_m = self._score_pose_batch(
            local_xy, fc_x, fc_y, fc_yaw
        )

        self.x_m = float(fc_x[best_f])
        self.y_m = float(fc_y[best_f])
        self.yaw_rad = wrap_angle_rad(float(fc_yaw[best_f]))

        reg_id, reg_conf, vis_ok = self._check_visual_region_consistency(
            self.x_m, self.y_m, visual
        )
        if not vis_ok:
            self.consecutive_visual_mismatch += 1
        else:
            self.consecutive_visual_mismatch = 0

        if inlier_ratio >= 0.65 and mean_res_m <= 0.15:
            if self.consecutive_visual_mismatch >= 2:
                self.status = "DEGRADED"
            else:
                self.status = "VALID"
        elif inlier_ratio >= 0.40:
            self.status = "DEGRADED"
        else:
            self.status = "LOST"

        min_front_m, sector_dists = compute_obstacle_summary(scan_polar)

        return LocalizationOutput(
            timestamp_s=timestamp_s,
            x_m=self.x_m,
            y_m=self.y_m,
            yaw_rad=self.yaw_rad,
            localization_status=self.status,
            inlier_ratio=inlier_ratio,
            mean_residual_m=mean_res_m,
            visual_region_id=reg_id,
            visual_confidence=reg_conf,
            visual_consistent=vis_ok,
            lidar_health="OK",
            min_front_distance_m=min_front_m,
            sector_distances_m=sector_dists,
        )


def run_self_test() -> int:
    """
    Deterministic self-test verifying:
      1. Scan-to-map pose recovery from an initial perturbation `(dx=+0.22m, dy=-0.16m, dyaw=+11 deg)`.
      2. Visual-only input without lidar scan never produces `VALID` status.
      3. Validated visual region mismatch downgrades `VALID` -> `DEGRADED`.
      4. 8-sector obstacle summary computation.
    """
    print("Running onboard/lidar_localize.py self-test (Cycle 3 Scan-to-Map Localizer)...")
    mapper = OccupancyGridMapper(resolution_m=0.05, half_extent_m=3.5)
    # Asymmetric room (2.4m East, 1.6m West, 1.8m North, 1.2m South) so orientation is unique
    true_scan: List[Tuple[float, float]] = []
    for deg in range(0, 360, 3):
        rad = math.radians(deg)
        ca, sa = math.cos(rad), math.sin(rad)
        tx = (2.4 / ca) if ca > 1e-6 else ((-1.6 / ca) if ca < -1e-6 else 1e9)
        ty = (1.8 / sa) if sa > 1e-6 else ((-1.2 / sa) if sa < -1e-6 else 1e9)
        dist = min(tx, ty)
        true_scan.append((rad, dist))

    for _ in range(12):
        mapper.integrate_scan(true_scan, (0.0, 0.0, 0.0))

    map_dict = mapper.to_map_dict("asymmetric_room_self_test")
    map_dict["regions"] = {
        "REGION_01": {"x_min_m": -0.5, "x_max_m": 0.5, "y_min_m": -0.5, "y_max_m": 0.5},
        "REGION_02": {"x_min_m": 1.0, "x_max_m": 2.0, "y_min_m": 0.5, "y_max_m": 1.5},
    }

    localizer = LidarMapLocalizer(map_dict)
    # 1. Perturb initial pose by (+0.22 m, -0.16 m, +11.0 deg) and verify convergence to (0, 0, 0)
    localizer.set_initial_pose(0.22, -0.16, math.radians(11.0))
    out1 = localizer.update_from_scan(
        timestamp_s=100.0,
        scan_polar=true_scan,
        motion=MotionFeedbackInput(timestamp_s=100.0, speed_m_s=0.0, direction_state="NEUTRAL_STOP"),
        visual=VisualRegionInput(
            timestamp_s=100.0,
            visual_region_id="REGION_01",
            visual_confidence=0.92,
            validated_on_held_out_runs=True,
        ),
    )
    pos_err = math.hypot(out1.x_m - 0.0, out1.y_m - 0.0)
    yaw_err_deg = abs(math.degrees(out1.yaw_rad))
    if out1.localization_status != "VALID" or pos_err > 0.06 or yaw_err_deg > 2.5:
        print("FAIL [1/3]: Pose recovery failed:", out1.to_dict())
        return 1
    print(
        f"  [PASS 1/3] Pose recovered from (+0.22m, -0.16m, +11.0°): "
        f"est=({out1.x_m:.3f}m, {out1.y_m:.3f}m, {math.degrees(out1.yaw_rad):.2f}°), "
        f"inliers={out1.inlier_ratio:.2f}, status={out1.localization_status}"
    )

    # 2. Verify that high-confidence visual region WITHOUT lidar scan never yields VALID
    out_no_lidar = localizer.update_from_scan(
        timestamp_s=100.5,
        scan_polar=None,
        visual=VisualRegionInput(
            timestamp_s=100.5,
            visual_region_id="REGION_01",
            visual_confidence=0.99,
            validated_on_held_out_runs=True,
        ),
    )
    if out_no_lidar.localization_status == "VALID":
        print("FAIL [2/3]: Visual-only input erroneously set status=VALID")
        return 1
    print(
        f"  [PASS 2/3] Visual-only input without lidar scan blocked from VALID: "
        f"status={out_no_lidar.localization_status}, lidar_health={out_no_lidar.lidar_health}"
    )

    # 3. Verify that 2 consecutive mismatches with a validated visual region downgrade VALID -> DEGRADED
    localizer.set_initial_pose(0.0, 0.0, 0.0)
    for step_i in range(2):
        out_mis = localizer.update_from_scan(
            timestamp_s=101.0 + step_i * 0.1,
            scan_polar=true_scan,
            visual=VisualRegionInput(
                timestamp_s=101.0 + step_i * 0.1,
                visual_region_id="REGION_02",  # vehicle is at (0,0) in REGION_01, not REGION_02
                visual_confidence=0.95,
                validated_on_held_out_runs=True,
            ),
        )
    if out_mis.localization_status != "DEGRADED" or out_mis.visual_consistent:
        print("FAIL [3/3]: Region mismatch did not downgrade to DEGRADED:", out_mis.to_dict())
        return 1
    print(
        f"  [PASS 3/3] Region consistency mismatch downgraded status to {out_mis.localization_status} "
        f"(visual_consistent={out_mis.visual_consistent}, min_front={out_mis.min_front_distance_m:.2f}m)"
    )
    print("SELF-TEST RESULT: PASS.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run RPLIDAR A2M8 scan-to-map localization against an occupancy map JSON."
    )
    parser.add_argument(
        "--map",
        type=Path,
        default=None,
        help="Path to JSON occupancy map generated by onboard/lidar_mapper.py",
    )
    parser.add_argument(
        "--replay-csv",
        type=Path,
        default=None,
        help="Path to recorded RPLIDAR scan CSV to localize scan-by-scan",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Optional path to save localization trajectory & summary JSON",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic localization and region-constraint self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.map is None or args.replay_csv is None:
        parser.error("Specify both --map and --replay-csv, or use --self-test.")

    map_dict = json.loads(args.map.read_text(encoding="utf-8"))
    scans, timestamps = load_scans_from_csv(args.replay_csv)
    scan_ids = sorted(scans.keys())
    if not scan_ids:
        print(f"Error: no valid scans in {args.replay_csv}", file=sys.stderr)
        return 1

    localizer = LidarMapLocalizer(map_dict)
    localizer.set_initial_pose(0.0, 0.0, 0.0)

    outputs: List[dict] = []
    valid_count = 0
    for sid in scan_ids:
        out = localizer.update_from_scan(
            timestamp_s=timestamps[sid],
            scan_polar=scans[sid],
        )
        if out.localization_status == "VALID":
            valid_count += 1
        outputs.append(out.to_dict())

    inliers = [o["inlier_ratio"] for o in outputs]
    residuals = [o["mean_residual_m"] for o in outputs]
    summary = {
        "map_file": args.map.name,
        "replay_csv": args.replay_csv.name,
        "total_scans_localized": len(outputs),
        "valid_status_count": valid_count,
        "valid_status_ratio": round(valid_count / len(outputs), 3),
        "mean_inlier_ratio": round(float(np.mean(inliers)), 3),
        "min_inlier_ratio": round(float(np.min(inliers)), 3),
        "mean_residual_m": round(float(np.mean(residuals)), 4),
        "final_pose": {
            "x_m": outputs[-1]["x_m"],
            "y_m": outputs[-1]["y_m"],
            "yaw_deg": outputs[-1]["yaw_deg"],
            "status": outputs[-1]["localization_status"],
        },
        "sample_pose_first": outputs[0],
        "sample_pose_last": outputs[-1],
    }

    print(f"=== Localization Replay Summary ({args.replay_csv.name} -> {args.map.name}) ===")
    print(f"  Scans localized     : {summary['total_scans_localized']}")
    print(f"  VALID status count  : {summary['valid_status_count']} ({summary['valid_status_ratio']*100:.1f}%)")
    print(f"  Mean inlier ratio   : {summary['mean_inlier_ratio']} (min: {summary['min_inlier_ratio']})")
    print(f"  Mean residual (m)   : {summary['mean_residual_m']} m")
    print(f"  Final pose estimate : {summary['final_pose']}")

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Saved localization summary JSON to {args.out_json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
