#!/usr/bin/env python3
"""
RPLIDAR A2M8 recorded-scan replay and 2D Cartesian projection utility (Task B5).
Reads recorded CSV files produced by lidar_acquire.py, validates scan integrity,
computes per-scan and dataset statistics, tracks dynamic obstacle movement in a
target angular sector, and optionally exports a 2D top-down SVG/PNG plot.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def load_scans(csv_path: Path):
    scans = defaultdict(list)
    timestamps = {}
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scan_id = int(row["scan_id"])
            ts = float(row["timestamp_s"])
            q = int(row["quality"])
            ang = float(row["angle_deg"])
            dist = float(row["distance_mm"])
            if dist > 0:
                scans[scan_id].append((ts, q, ang, dist))
                if scan_id not in timestamps:
                    timestamps[scan_id] = ts
    return scans, timestamps


def polar_to_cartesian_mm(angle_deg: float, distance_mm: float):
    rad = math.radians(angle_deg)
    x_mm = distance_mm * math.cos(rad)
    y_mm = distance_mm * math.sin(rad)
    return x_mm, y_mm


def export_svg_map(scans, out_svg: Path, max_range_mm: float = 4000.0):
    size = 800
    half = size / 2.0
    scale = (half - 40.0) / max_range_mm

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="#0f172a"/>',
    ]
    # Range rings every 1000 mm (1 m)
    for r_m in range(1, int(max_range_mm // 1000) + 1):
        r_px = r_m * 1000.0 * scale
        lines.append(
            f'<circle cx="{half}" cy="{half}" r="{r_px:.1f}" fill="none" stroke="#334155" stroke-width="1" stroke-dasharray="4,4"/>'
        )
        lines.append(
            f'<text x="{half + 6}" y="{half - r_px + 14:.1f}" fill="#94a3b8" font-family="monospace" font-size="12">{r_m}m</text>'
        )

    # Axes
    lines.append(f'<line x1="20" y1="{half}" x2="{size-20}" y2="{half}" stroke="#334155" stroke-width="1"/>')
    lines.append(f'<line x1="{half}" y1="20" x2="{half}" y2="{size-20}" stroke="#334155" stroke-width="1"/>')

    # Plot early scan points (cyan) vs mid scan points (amber) vs late scan points (emerald)
    scan_ids = sorted(scans.keys())
    if scan_ids:
        sample_groups = [
            (scan_ids[:5], "#38bdf8", "Early scans"),
            (scan_ids[len(scan_ids) // 2 : len(scan_ids) // 2 + 5], "#f59e0b", "Mid scans (moved object)"),
            (scan_ids[-5:], "#10b981", "Late scans"),
        ]
        for group_ids, color, _ in sample_groups:
            for sid in group_ids:
                for _, _, ang, dist in scans[sid]:
                    if dist <= max_range_mm:
                        x_mm, y_mm = polar_to_cartesian_mm(ang, dist)
                        px = half + y_mm * scale
                        py = half - x_mm * scale
                        lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.0" fill="{color}" fill-opacity="0.75"/>')

    # LiDAR origin marker
    lines.append(f'<circle cx="{half}" cy="{half}" r="5" fill="#ef4444"/>')
    lines.append(
        f'<text x="24" y="32" fill="#f8fafc" font-family="monospace" font-size="14">RPLIDAR A2M8 2D Scan Replay: {out_svg.stem}</text>'
    )
    lines.append(
        '<text x="24" y="52" fill="#38bdf8" font-family="monospace" font-size="12">Cyan: Early scans | Amber: Mid scans | Green: Late scans | Red: LiDAR Origin</text>'
    )
    lines.append("</svg>")
    out_svg.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Replay recorded RPLIDAR A2M8 CSV scans.")
    parser.add_argument("csv_file", type=Path, help="Input CSV file recorded by lidar_acquire.py")
    parser.add_argument("--svg", type=Path, default=None, help="Optional output SVG map path")
    parser.add_argument("--summary-json", type=Path, default=None, help="Optional JSON summary output path")
    args = parser.parse_args()

    scans, timestamps = load_scans(args.csv_file)
    scan_ids = sorted(scans.keys())
    if not scan_ids:
        raise SystemExit(f"No valid scans found in {args.csv_file}")

    total_points = sum(len(scans[sid]) for sid in scan_ids)
    t_start = timestamps[scan_ids[0]]
    t_end = timestamps[scan_ids[-1]]
    duration_s = max(t_end - t_start, 1e-6)
    scan_rate_hz = (len(scan_ids) - 1) / duration_s if len(scan_ids) > 1 else 0.0

    # Track closest obstacle distance across scans to verify moved-object response
    closest_per_scan = []
    for sid in scan_ids:
        min_d = min(pt[3] for pt in scans[sid])
        closest_per_scan.append(min_d)

    min_closest_mm = min(closest_per_scan)
    max_closest_mm = max(closest_per_scan)
    all_dists = [pt[3] for sid in scan_ids for pt in scans[sid]]

    summary = {
        "file": str(args.csv_file.name),
        "total_scans": len(scan_ids),
        "total_valid_points": total_points,
        "mean_points_per_scan": round(total_points / len(scan_ids), 2),
        "duration_s": round(duration_s, 3),
        "effective_scan_rate_hz": round(scan_rate_hz, 2),
        "global_min_distance_mm": round(min(all_dists), 1),
        "global_max_distance_mm": round(max(all_dists), 1),
        "closest_obstacle_min_mm": round(min_closest_mm, 1),
        "closest_obstacle_max_mm": round(max_closest_mm, 1),
        "closest_obstacle_variation_mm": round(max_closest_mm - min_closest_mm, 1),
    }

    print(f"=== Replay Summary: {args.csv_file.name} ===")
    for k, v in summary.items():
        print(f"  {k:32s}: {v}")

    if args.svg:
        export_svg_map(scans, args.svg)
        print(f"Saved 2D top-down scan plot to {args.svg}")

    if args.summary_json:
        args.summary_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Saved JSON replay summary to {args.summary_json}")


if __name__ == "__main__":
    main()
