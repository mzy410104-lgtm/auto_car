#!/usr/bin/env python3
"""
Interactive TT-02 Classroom, Onboard Camera AI & LiDAR Localization Simulator.

Proves the entire Member B AI + LiDAR pipeline end-to-end in a virtual 6.0m x 4.0m
classroom divided into 4 visual regions (REGION_01 .. REGION_04):
  1. Synthesizes realistic first-person 640x480 camera views from any `(x_m, y_m, yaw_rad)`
     pose in the classroom using a vectorized 2.5D perspective raycaster (colored walls,
     doors, whiteboard, windows, pillars, floor/ceiling shading).
  2. Automatically records a session-separated dataset (`train`, `val`, `test` across
     separate sessions), validates it with `vision_manifest.py`, and trains the real
     `VisualRegionClassifier` (`vision_region_model.py`).
  3. Builds the 2D occupancy grid map of the virtual classroom using `lidar_mapper.py`.
  4. Runs the real `LidarMapLocalizer` (`lidar_localize.py`) fused with the live
     `VisualRegionClassifier` predictions and Ackermann vehicle kinematics.
  5. Serves an interactive web simulator (`http://127.0.0.1:8085`) with:
       - Top-down 2D classroom map, region zones, true vs. localized car pose, and 360° LiDAR rays
       - Live First-Person Onboard Camera feed (what the car sees as it drives)
       - Live AI Region Classifier probability bars (`REGION_01..04`) + held-out validation metrics
       - Manual driving (`W/A/S/D` or buttons), Auto-Patrol, and a "Kidnap / Teleport Car" button
         that demonstrates how the Camera AI detects a pose mismatch and recovers localization!
"""

import argparse
import csv
import io
import json
import math
import os
import signal
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import numpy as np
from PIL import Image

from lidar_localize import (
    LidarMapLocalizer,
    MotionFeedbackInput,
    VisualRegionInput,
    wrap_angle_rad,
)
from lidar_mapper import OccupancyGridMapper
from vision_manifest import MANIFEST_COLUMNS
from vision_region_model import (
    VisualRegionClassifier,
    train_and_validate_from_manifest,
)


# Virtual Classroom: x in [-3.0, +3.0] m, y in [-2.0, +2.0] m
# Divided into 4 quadrants:
#   REGION_01 (NW: x < 0, y >= 0): Red Door & Blue Lab Locker
#   REGION_02 (NE: x >= 0, y >= 0): Green Whiteboard & Cyan Window
#   REGION_03 (SE: x >= 0, y < 0): Purple Projector Wall & Orange Bench
#   REGION_04 (SW: x < 0, y < 0): Yellow Bookshelf & Teal Pickup Station
CLASSROOM_REGIONS: Dict[str, dict] = {
    "REGION_01": {
        "name": "NW Quadrant (Red Door & Blue Locker)",
        "x_min_m": -3.0,
        "x_max_m": 0.0,
        "y_min_m": 0.0,
        "y_max_m": 2.0,
        "nominal_yaw_rad": 2.35,
    },
    "REGION_02": {
        "name": "NE Quadrant (Green Whiteboard & Window)",
        "x_min_m": 0.0,
        "x_max_m": 3.0,
        "y_min_m": 0.0,
        "y_max_m": 2.0,
        "nominal_yaw_rad": 0.78,
    },
    "REGION_03": {
        "name": "SE Quadrant (Purple Screen & Orange Bench)",
        "x_min_m": 0.0,
        "x_max_m": 3.0,
        "y_min_m": -2.0,
        "y_max_m": 0.0,
        "nominal_yaw_rad": -0.78,
    },
    "REGION_04": {
        "name": "SW Quadrant (Yellow Shelf & Teal Pickup)",
        "x_min_m": -3.0,
        "x_max_m": 0.0,
        "y_min_m": -2.0,
        "y_max_m": 0.0,
        "nominal_yaw_rad": -2.35,
    },
}

# Colored 2D line segments `(x1, y1, x2, y2, (R, G, B), stripe_rgb)` forming the classroom walls & landmarks
WALL_SEGMENTS = [
    # North wall (y = +2.0): NW half (REGION_01) vs NE half (REGION_02)
    (-3.0, 2.0, -1.5, 2.0, (210, 50, 55), (245, 190, 190)),    # Red door panel (NW)
    (-1.5, 2.0, 0.0, 2.0, (45, 105, 215), (180, 215, 250)),    # Blue lab locker (NW)
    (0.0, 2.0, 1.8, 2.0, (40, 185, 95), (220, 250, 230)),      # Green whiteboard (NE)
    (1.8, 2.0, 3.0, 2.0, (45, 195, 220), (200, 245, 255)),     # Cyan window (NE)
    # East wall (x = +3.0): NE half (REGION_02) vs SE half (REGION_03)
    (3.0, 2.0, 3.0, 0.0, (50, 200, 130), (210, 250, 225)),     # Emerald NE wall
    (3.0, 0.0, 3.0, -2.0, (165, 65, 205), (235, 195, 250)),    # Purple projector wall (SE)
    # South wall (y = -2.0): SE half (REGION_03) vs SW half (REGION_04)
    (3.0, -2.0, 1.5, -2.0, (230, 120, 40), (255, 215, 175)),   # Orange bench wall (SE)
    (1.5, -2.0, 0.0, -2.0, (180, 75, 190), (240, 200, 245)),   # Magenta cabinet (SE)
    (0.0, -2.0, -1.5, -2.0, (225, 190, 40), (255, 245, 180)),  # Yellow bookshelf (SW)
    (-1.5, -2.0, -3.0, -2.0, (35, 165, 155), (185, 240, 235)), # Teal pickup wall (SW)
    # West wall (x = -3.0): SW half (REGION_04) vs NW half (REGION_01)
    (-3.0, -2.0, -3.0, 0.0, (215, 170, 45), (250, 235, 175)),  # Gold SW wall
    (-3.0, 0.0, -3.0, 2.0, (200, 60, 75), (250, 195, 200)),    # Crimson NW wall
    # Two interior classroom pillars/desks for asymmetric LiDAR landmarks
    (-0.9, 0.7, -0.5, 0.7, (190, 80, 80), (240, 200, 200)),
    (-0.5, 0.7, -0.5, 1.1, (70, 130, 220), (200, 220, 250)),
    (0.7, -0.9, 1.2, -0.9, (225, 135, 50), (250, 220, 190)),
    (1.2, -0.9, 1.2, -0.5, (160, 75, 200), (230, 200, 245)),
]


def ground_truth_region_for_xy(x_m: float, y_m: float) -> str:
    if x_m < 0.0 and y_m >= 0.0:
        return "REGION_01"
    if x_m >= 0.0 and y_m >= 0.0:
        return "REGION_02"
    if x_m >= 0.0 and y_m < 0.0:
        return "REGION_03"
    return "REGION_04"


def raycast_classroom(
    x_m: float, y_m: float, ray_angles_world: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized 2D raycaster against `WALL_SEGMENTS`.
    Given origin `(x_m, y_m)` and 1D array `ray_angles_world` `(R,)`,
    returns `(distances_m, hit_u_coord, segment_indices)` each of shape `(R,)`.
    """
    n_rays = len(ray_angles_world)
    dx = np.cos(ray_angles_world)  # (R,)
    dy = np.sin(ray_angles_world)  # (R,)

    best_t = np.full(n_rays, 20.0, dtype=np.float32)
    best_u = np.zeros(n_rays, dtype=np.float32)
    best_seg = np.zeros(n_rays, dtype=np.int32)

    for seg_i, (x1, y1, x2, y2, _, _) in enumerate(WALL_SEGMENTS):
        sx = x2 - x1
        sy = y2 - y1
        # Ray: P + t * d = A + u * s  (t > 0, 0 <= u <= 1)
        denom = dx * sy - dy * sx
        valid_denom = np.abs(denom) > 1e-7
        ox = x1 - x_m
        oy = y1 - y_m

        t = np.where(valid_denom, (ox * sy - oy * sx) / np.where(valid_denom, denom, 1.0), 20.0)
        u = np.where(valid_denom, (ox * dy - oy * dx) / np.where(valid_denom, denom, 1.0), -1.0)

        hit = valid_denom & (t > 0.05) & (u >= 0.0) & (u <= 1.0) & (t < best_t)
        best_t = np.where(hit, t, best_t)
        best_u = np.where(hit, u, best_u)
        best_seg = np.where(hit, seg_i, best_seg)

    return best_t, best_u, best_seg


def render_first_person_camera(
    x_m: float,
    y_m: float,
    yaw_rad: float,
    width: int = 320,
    height: int = 240,
    fov_deg: float = 70.0,
    brightness: float = 1.0,
) -> Image.Image:
    """
    Render a synthetic first-person RGB camera frame from `(x_m, y_m, yaw_rad)` inside
    the virtual classroom using 2.5D perspective raycasting.
    """
    half_fov = math.radians(fov_deg * 0.5)
    cam_offsets = np.linspace(half_fov, -half_fov, width, dtype=np.float32)
    world_angles = yaw_rad + cam_offsets
    raw_dist, hit_u, seg_idx = raycast_classroom(x_m, y_m, world_angles)
    perp_dist = np.maximum(0.15, raw_dist * np.cos(cam_offsets))

    # Build color lookup tables for segments
    base_colors = np.array([seg[4] for seg in WALL_SEGMENTS], dtype=np.float32)
    stripe_colors = np.array([seg[5] for seg in WALL_SEGMENTS], dtype=np.float32)

    img_arr = np.zeros((height, width, 3), dtype=np.float32)
    half_h = height // 2

    # Ceiling gradient
    img_arr[:half_h, :, :] = np.array([45.0, 52.0, 68.0], dtype=np.float32)

    # Floor color tinted slightly by classroom quadrant so downward view also carries region cue
    reg = ground_truth_region_for_xy(x_m, y_m)
    floor_tints = {
        "REGION_01": np.array([85.0, 55.0, 60.0], dtype=np.float32),
        "REGION_02": np.array([50.0, 82.0, 70.0], dtype=np.float32),
        "REGION_03": np.array([75.0, 60.0, 88.0], dtype=np.float32),
        "REGION_04": np.array([88.0, 80.0, 52.0], dtype=np.float32),
    }
    img_arr[half_h:, :, :] = floor_tints[reg]

    # Wall heights in pixels
    wall_h = np.clip((height * 0.75) / perp_dist, 8, height - 2).astype(np.int32)
    top_y = np.clip(half_h - wall_h // 2, 0, height - 1)
    bot_y = np.clip(half_h + wall_h // 2, 1, height)

    # Distance fog / attenuation factor
    shade = np.clip(1.15 - 0.12 * perp_dist, 0.35, 1.0)

    for col in range(width):
        s_i = int(seg_idx[col])
        u_val = float(hit_u[col])
        y0, y1 = int(top_y[col]), int(bot_y[col])
        if y1 <= y0:
            continue
        c_base = base_colors[s_i] * float(shade[col])
        c_stripe = stripe_colors[s_i] * float(shade[col])

        # Vertical landmark pattern (stripes + middle feature band)
        is_v_stripe = (int(u_val * 10.0) % 2) == 1
        img_arr[y0:y1, col, :] = c_stripe if is_v_stripe else c_base

        # Horizontal accent band in middle of wall
        band_y0 = y0 + (y1 - y0) // 3
        band_y1 = y0 + 2 * (y1 - y0) // 3
        img_arr[band_y0:band_y1, col, :] = c_stripe if not is_v_stripe else c_base

    img_arr = np.clip(img_arr * brightness, 0, 255).astype(np.uint8)
    out = Image.fromarray(img_arr)
    if (width, height) != (640, 480):
        out = out.resize((640, 480), Image.Resampling.BILINEAR)
    return out


def simulate_lidar_scan(
    x_m: float, y_m: float, yaw_rad: float, n_rays: int = 120, noise_std_m: float = 0.008
) -> List[Tuple[float, float]]:
    """Simulate a 360-degree RPLIDAR A2M8 scan `[(angle_rad, dist_m), ...]` in vehicle frame."""
    rel_angles = np.linspace(0.0, 2.0 * math.pi, n_rays, endpoint=False, dtype=np.float32)
    world_angles = yaw_rad + rel_angles
    dists, _, _ = raycast_classroom(x_m, y_m, world_angles)
    if noise_std_m > 0:
        rng = np.random.default_rng(int(abs(x_m * 1000 + y_m * 100 + yaw_rad * 10)) % 100000)
        dists = dists + rng.normal(0.0, noise_std_m, size=n_rays).astype(np.float32)
    scan_polar: List[Tuple[float, float]] = []
    for a_rad, d_m in zip(rel_angles.tolist(), dists.tolist()):
        if 0.15 <= d_m <= 6.50:
            scan_polar.append((float(a_rad), float(d_m)))
    return scan_polar


SIM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TT-02 Classroom AI & LiDAR Localization Simulator</title>
<style>
  :root {
    --bg: #0b1020;
    --panel: #131b33;
    --border: #25335a;
    --accent: #38bdf8;
    --green: #22c55e;
    --amber: #f59e0b;
    --red: #ef4444;
    --text: #e2e8f0;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 16px;
  }
  header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding-bottom: 12px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--border);
  }
  h1 { margin: 0; font-size: 1.2rem; }
  .badge {
    padding: 6px 14px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.85rem;
    background: #1e293b;
  }
  .layout {
    display: grid;
    grid-template-columns: 1.25fr 1fr;
    gap: 16px;
  }
  @media (max-width: 1024px) { .layout { grid-template-columns: 1fr; } }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
  }
  .card h2 {
    margin: 0 0 10px 0;
    font-size: 0.92rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  canvas {
    width: 100%;
    background: #080d1a;
    border-radius: 8px;
    border: 1px solid var(--border);
    display: block;
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
  }
  button {
    background: #1e293b;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.82rem;
  }
  button:hover { border-color: var(--accent); }
  button.primary { background: #0284c7; border-color: #38bdf8; }
  button.warn { background: #b45309; border-color: #f59e0b; }
  .prob-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    font-size: 0.82rem;
  }
  .prob-bar-bg {
    flex: 1;
    height: 12px;
    background: #090d1a;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--border);
  }
  .prob-bar-fill {
    height: 100%;
    background: var(--accent);
    transition: width 0.2s;
  }
  .kv {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 10px;
  }
  .kv-box {
    background: #0b1224;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 10px;
  }
  .kv-label { font-size: 0.72rem; color: var(--muted); }
  .kv-val { font-size: 0.96rem; font-weight: 700; margin-top: 2px; font-family: monospace; }
</style>
</head>
<body>
<header>
  <div>
    <h1>TT-02 Classroom AI & LiDAR Localization Simulator</h1>
    <div style="font-size:0.8rem;color:var(--muted)" id="subText">
      Use W/A/S/D or buttons below to drive the car, or toggle Auto-Patrol!
    </div>
  </div>
  <div style="display:flex;gap:8px;align-items:center">
    <div class="badge" id="modelBadge">AI MODEL: VALIDATED</div>
    <div class="badge" id="locBadge">LOCALIZATION: VALID</div>
  </div>
</header>

<div class="layout">
  <div class="card">
    <h2>Top-Down 2D Classroom Map (6.0m × 4.0m) + Live RPLIDAR A2M8 Scan</h2>
    <canvas id="topCanvas" width="660" height="440"></canvas>
    <div class="controls">
      <button class="primary" onclick="sendCmd('patrol_toggle')" id="btnPatrol">Pause Auto-Patrol</button>
      <button onclick="sendCmd('forward')">▲ Forward (W)</button>
      <button onclick="sendCmd('left')">◀ Turn Left (A)</button>
      <button onclick="sendCmd('right')">▶ Turn Right (D)</button>
      <button onclick="sendCmd('backward')">▼ Reverse (S)</button>
      <button class="warn" onclick="sendCmd('kidnap')">⚡ Kidnap / Teleport Car (Test AI Recovery)</button>
    </div>
    <div class="kv">
      <div class="kv-box">
        <div class="kv-label">True Classroom Pose (x, y, yaw)</div>
        <div class="kv-val" id="truePose">--</div>
      </div>
      <div class="kv-box">
        <div class="kv-label">LiDAR+AI Estimated Pose (x, y, yaw)</div>
        <div class="kv-val" id="estPose">--</div>
      </div>
      <div class="kv-box">
        <div class="kv-label">Pose Tracking Error / Inliers</div>
        <div class="kv-val" id="errBox">--</div>
      </div>
      <div class="kv-box">
        <div class="kv-label">Ground-Truth vs AI Predicted Region</div>
        <div class="kv-val" id="regMatch">--</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Onboard OV5647 Camera View (First-Person Raycast)</h2>
    <img id="camImg" src="/api/camera.jpg" style="width:100%;border-radius:8px;border:1px solid var(--border);aspect-ratio:4/3;object-fit:cover" />
    <h2 style="margin-top:12px">Live AI Visual Region Classifier Output</h2>
    <div id="probContainer"></div>
    <div class="kv" style="margin-top:10px">
      <div class="kv-box">
        <div class="kv-label">Held-Out Val / Test Accuracy</div>
        <div class="kv-val" id="valAccBox" style="color:var(--green)">--</div>
      </div>
      <div class="kv-box">
        <div class="kv-label">Min Front Obstacle (LiDAR)</div>
        <div class="kv-val" id="frontBox">--</div>
      </div>
    </div>
  </div>
</div>

<script>
const topCanvas = document.getElementById('topCanvas');
const ctx = topCanvas.getContext('2d');

async function sendCmd(action) {
  await fetch('/api/control', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action})
  });
  pollState();
}

window.addEventListener('keydown', (e) => {
  const k = e.key.toLowerCase();
  if (k === 'w' || k === 'arrowup') sendCmd('forward');
  else if (k === 's' || k === 'arrowdown') sendCmd('backward');
  else if (k === 'a' || k === 'arrowleft') sendCmd('left');
  else if (k === 'd' || k === 'arrowright') sendCmd('right');
});

async function pollState() {
  try {
    const r = await fetch('/api/state');
    const d = await r.json();
    document.getElementById('camImg').src = '/api/camera.jpg?t=' + Date.now();

    const tp = d.true_pose;
    const ep = d.localization;
    document.getElementById('truePose').textContent = `(${tp.x_m.toFixed(2)}m, ${tp.y_m.toFixed(2)}m, ${tp.yaw_deg.toFixed(0)}°)`;
    document.getElementById('estPose').textContent = `(${ep.x_m.toFixed(2)}m, ${ep.y_m.toFixed(2)}m, ${ep.yaw_deg.toFixed(0)}°)`;
    document.getElementById('errBox').textContent = `${(d.pos_error_m*100).toFixed(1)} cm | ${(ep.inlier_ratio*100).toFixed(0)}% inliers`;

    const matchOk = tp.true_region_id === ep.visual_region_id;
    const rm = document.getElementById('regMatch');
    rm.textContent = `True: ${tp.true_region_id} | AI: ${ep.visual_region_id} (${(ep.visual_confidence*100).toFixed(0)}%)`;
    rm.style.color = matchOk ? '#22c55e' : '#f59e0b';

    document.getElementById('valAccBox').textContent = `Val: ${(d.model_metrics.val_acc*100).toFixed(1)}% | Test: ${(d.model_metrics.test_acc*100).toFixed(1)}%`;
    document.getElementById('frontBox').textContent = ep.min_front_distance_m !== null ? `${ep.min_front_distance_m.toFixed(2)} m` : 'CLEAR';
    document.getElementById('btnPatrol').textContent = d.auto_patrol ? 'Pause Auto-Patrol' : 'Resume Auto-Patrol';

    const lb = document.getElementById('locBadge');
    lb.textContent = 'LOCALIZATION: ' + ep.localization_status;
    lb.style.color = ep.localization_status === 'VALID' ? '#22c55e' : '#f59e0b';

    // Probability bars
    const pc = document.getElementById('probContainer');
    pc.innerHTML = '';
    for (const [reg, prob] of Object.entries(d.vision_prediction.class_probabilities || {})) {
      const pct = (prob * 100).toFixed(1);
      const isTop = reg === ep.visual_region_id;
      pc.innerHTML += `
        <div class="prob-row">
          <div style="width:92px;font-weight:${isTop ? '700' : '400'};color:${isTop ? '#38bdf8' : '#e2e8f0'}">${reg}</div>
          <div class="prob-bar-bg"><div class="prob-bar-fill" style="width:${pct}%;background:${isTop ? '#22c55e' : '#38bdf8'}"></div></div>
          <div style="width:48px;text-align:right;font-family:monospace">${pct}%</div>
        </div>`;
    }

    drawClassroom(d);
  } catch (e) {}
}

function worldToCanvas(x_m, y_m) {
  const W = topCanvas.width, H = topCanvas.height;
  const scale = 95.0; // pixels per meter
  return [W / 2 + x_m * scale, H / 2 - y_m * scale];
}

function drawClassroom(d) {
  const W = topCanvas.width, H = topCanvas.height;
  ctx.clearRect(0, 0, W, H);

  // Draw 4 quadrant region backgrounds
  const quads = [
    {id: 'REGION_01 (NW)', x0: -3, y0: 2, x1: 0, y1: 0, fill: 'rgba(210, 50, 55, 0.10)'},
    {id: 'REGION_02 (NE)', x0: 0, y0: 2, x1: 3, y1: 0, fill: 'rgba(40, 185, 95, 0.10)'},
    {id: 'REGION_03 (SE)', x0: 0, y0: 0, x1: 3, y1: -2, fill: 'rgba(165, 65, 205, 0.10)'},
    {id: 'REGION_04 (SW)', x0: -3, y0: 0, x1: 0, y1: -2, fill: 'rgba(225, 190, 40, 0.10)'},
  ];
  for (const q of quads) {
    const [px0, py0] = worldToCanvas(q.x0, q.y0);
    const [px1, py1] = worldToCanvas(q.x1, q.y1);
    ctx.fillStyle = q.fill;
    ctx.fillRect(px0, py0, px1 - px0, py1 - py0);
    ctx.strokeStyle = '#1e293b';
    ctx.strokeRect(px0, py0, px1 - px0, py1 - py0);
    ctx.fillStyle = '#94a3b8';
    ctx.font = 'bold 12px monospace';
    ctx.fillText(q.id, px0 + 10, py0 + 20);
  }

  // Occupied grid cells from lidar_mapper
  ctx.fillStyle = '#64748b';
  for (const [mx, my] of d.map_cells || []) {
    const [px, py] = worldToCanvas(mx, my);
    ctx.fillRect(px - 2, py - 2, 4, 4);
  }

  // Live LiDAR scan points (cyan)
  ctx.fillStyle = '#38bdf8';
  for (const [sx, sy] of d.scan_world_xy_m || []) {
    const [px, py] = worldToCanvas(sx, sy);
    ctx.beginPath();
    ctx.arc(px, py, 2.2, 0, Math.PI * 2);
    ctx.fill();
  }

  // Ground-truth car pose (white outline circle)
  const [tx, ty] = worldToCanvas(d.true_pose.x_m, d.true_pose.y_m);
  ctx.strokeStyle = '#f8fafc';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(tx, ty, 9, 0, Math.PI * 2);
  ctx.stroke();

  // Estimated car pose arrow (green)
  const [ex, ey] = worldToCanvas(d.localization.x_m, d.localization.y_m);
  const hx = ex + 22 * Math.cos(d.localization.yaw_rad);
  const hy = ey - 22 * Math.sin(d.localization.yaw_rad);
  ctx.strokeStyle = '#22c55e';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(ex, ey);
  ctx.lineTo(hx, hy);
  ctx.stroke();
  ctx.fillStyle = '#22c55e';
  ctx.beginPath();
  ctx.arc(ex, ey, 5, 0, Math.PI * 2);
  ctx.fill();
}

setInterval(pollState, 300);
pollState();
</script>
</body>
</html>
"""


class ClassroomSimulator:
    """Builds the simulated classroom map & AI dataset, trains the region classifier, and runs the live car loop."""

    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.running = True
        self.auto_patrol = True
        self.patrol_t = 0.0

        # Ground-truth car state in classroom
        self.true_x_m = -1.4
        self.true_y_m = 0.9
        self.true_yaw_rad = 0.4

        print("[1/3] Building 2D Occupancy Grid Map of virtual classroom via lidar_mapper.py...")
        self.map_dict = self._build_classroom_occupancy_map()

        print("[2/3] Recording session-separated visual dataset & training AI via vision_region_model.py...")
        self.vision_clf, self.model_summary = self._build_and_train_vision_model()

        print("[3/3] Initializing LidarMapLocalizer fused with trained VisualRegionClassifier...")
        self.localizer = LidarMapLocalizer(self.map_dict)
        self.localizer.set_initial_pose(self.true_x_m, self.true_y_m, self.true_yaw_rad)

        self.latest_jpeg: bytes = b""
        self.latest_vision_pred: dict = {}
        self.latest_loc_dict: dict = {}
        self.latest_scan_world: List[Tuple[float, float]] = []
        self._step_simulation(dt=0.0)

    def _build_classroom_occupancy_map(self) -> dict:
        mapper = OccupancyGridMapper(resolution_m=0.05, half_extent_m=3.5)
        sample_poses = [
            (-1.8, 1.0, 0.0),
            (1.8, 1.0, 0.0),
            (1.8, -1.0, 0.0),
            (-1.8, -1.0, 0.0),
            (0.0, 0.0, 0.0),
        ]
        for px, py, pyaw in sample_poses:
            scan = simulate_lidar_scan(px, py, pyaw, n_rays=180, noise_std_m=0.003)
            for _ in range(6):
                mapper.integrate_scan(scan, (px, py, pyaw))

        md = mapper.to_map_dict("simulated_classroom_6x4m")
        md["regions"] = CLASSROOM_REGIONS
        md["pickup_poses"] = {
            "PICKUP_01": {
                "target_x_m": -1.8,
                "target_y_m": -1.2,
                "target_yaw_rad": -2.35,
                "arrival_xy_tol_m": 0.15,
                "arrival_yaw_tol_rad": 0.25,
            },
            "PICKUP_02": {
                "target_x_m": 1.8,
                "target_y_m": 1.2,
                "target_yaw_rad": 0.78,
                "arrival_xy_tol_m": 0.15,
                "arrival_yaw_tol_rad": 0.25,
            },
        }
        return md

    def _build_and_train_vision_model(self) -> Tuple[VisualRegionClassifier, dict]:
        dataset_dir = self.work_dir / "sim_camera_dataset"
        manifest_path = dataset_dir / "manifest.csv"
        model_path = dataset_dir / "region_model.json"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Representative poses inside each of the 4 classroom regions looking toward the region walls
        region_Anchor_poses = {
            "REGION_01": (-1.5, 1.0, math.radians(135.0)),
            "REGION_02": (1.5, 1.0, math.radians(45.0)),
            "REGION_03": (1.5, -1.0, math.radians(-45.0)),
            "REGION_04": (-1.5, -1.0, math.radians(-135.0)),
        }

        sessions = [
            ("20261104_sim_train_s01", "train", [(-0.2, -0.1, -0.12), (0.0, 0.0, 0.0), (0.2, 0.1, 0.12)], 1.00, "artificial_indoor"),
            ("20261104_sim_train_s02", "train", [(-0.15, 0.15, -0.08), (0.15, -0.15, 0.08)], 0.92, "mixed"),
            ("20261104_sim_val_s03", "val", [(-0.1, 0.05, -0.05), (0.1, -0.05, 0.05)], 1.06, "daylight_window"),
            ("20261104_sim_test_s04", "test", [(0.0, 0.08, 0.04), (-0.08, -0.08, -0.04)], 0.95, "artificial_indoor"),
        ]

        rows = []
        seq = 0
        for sess_id, split, offsets, b_scale, light in sessions:
            for reg_id, (bx, by, byaw) in region_Anchor_poses.items():
                for dx, dy, dyaw in offsets:
                    seq += 1
                    img_id = f"img_{1762900000 + seq}_{seq:04d}"
                    rel_path = f"images/{sess_id}/{img_id}.jpg"
                    abs_path = dataset_dir / rel_path
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    im = render_first_person_camera(
                        bx + dx, by + dy, byaw + dyaw, brightness=b_scale
                    )
                    im.save(abs_path, format="JPEG", quality=90)
                    rows.append(
                        [
                            img_id,
                            rel_path,
                            f"{1762900000.0 + seq:.3f}",
                            "2026-11-04T17:00:00Z",
                            sess_id,
                            reg_id,
                            "N",
                            "center",
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

        return train_and_validate_from_manifest(
            manifest_path, out_model_path=model_path, min_val_accuracy=0.80
        )

    def _step_simulation(self, dt: float) -> None:
        with self.lock:
            if self.auto_patrol and dt > 0.0:
                self.patrol_t += dt * 0.45
                # Smooth oval patrol path visiting all 4 quadrants of the classroom
                new_x = 1.65 * math.cos(self.patrol_t)
                new_y = 1.05 * math.sin(self.patrol_t)
                vx = -1.65 * math.sin(self.patrol_t)
                vy = 1.05 * math.cos(self.patrol_t)
                # Point camera slightly outward toward the quadrant walls as it patrols
                outward_yaw = math.atan2(new_y, new_x)
                tangent_yaw = math.atan2(vy, vx)
                self.true_x_m = new_x
                self.true_y_m = new_y
                self.true_yaw_rad = wrap_angle_rad(0.65 * outward_yaw + 0.35 * tangent_yaw)

            # 1. Render first-person OV5647 camera frame & run AI Region Classifier
            cam_img = render_first_person_camera(
                self.true_x_m, self.true_y_m, self.true_yaw_rad
            )
            buf = io.BytesIO()
            cam_img.save(buf, format="JPEG", quality=85)
            self.latest_jpeg = buf.getvalue()

            vis_pred = self.vision_clf.predict_image(cam_img)
            self.latest_vision_pred = vis_pred

            # 2. Simulate 360-deg RPLIDAR A2M8 scan & run LidarMapLocalizer fused with AI region
            scan_polar = simulate_lidar_scan(
                self.true_x_m, self.true_y_m, self.true_yaw_rad, n_rays=120
            )
            now_s = time.time()
            loc_out = self.localizer.update_from_scan(
                timestamp_s=now_s,
                scan_polar=scan_polar,
                motion=MotionFeedbackInput(
                    timestamp_s=now_s,
                    speed_m_s=0.35 if self.auto_patrol else 0.0,
                    direction_state="FWD" if self.auto_patrol else "NEUTRAL_STOP",
                    imu_heading_cdeg=int(round(math.degrees(self.true_yaw_rad) * 100.0)) % 36000,
                ),
                visual=VisualRegionInput(
                    timestamp_s=now_s,
                    visual_region_id=vis_pred["visual_region_id"],
                    visual_confidence=vis_pred["visual_confidence"],
                    validated_on_held_out_runs=vis_pred["validated_on_held_out_runs"],
                ),
            )
            self.latest_loc_dict = loc_out.to_dict()

            world_pts: List[Tuple[float, float]] = []
            for a_rad, d_m in scan_polar[::2]:
                wang = loc_out.yaw_rad + a_rad
                world_pts.append(
                    (
                        round(loc_out.x_m + d_m * math.cos(wang), 3),
                        round(loc_out.y_m + d_m * math.sin(wang), 3),
                    )
                )
            self.latest_scan_world = world_pts

    def apply_control(self, action: str) -> dict:
        with self.lock:
            if action == "patrol_toggle":
                self.auto_patrol = not self.auto_patrol
            elif action == "kidnap":
                # Teleport car to the opposite quadrant and force localizer status=LOST
                # so the AI visual region constraint seeds global recovery on the next step!
                self.auto_patrol = False
                self.true_x_m = -self.true_x_m
                self.true_y_m = -self.true_y_m
                self.true_yaw_rad = math.atan2(self.true_y_m, self.true_x_m)
                self.localizer.status = "LOST"
            else:
                self.auto_patrol = False
                step_m = 0.22
                if action == "forward":
                    nx = self.true_x_m + step_m * math.cos(self.true_yaw_rad)
                    ny = self.true_y_m + step_m * math.sin(self.true_yaw_rad)
                    self.true_x_m = max(-2.6, min(2.6, nx))
                    self.true_y_m = max(-1.6, min(1.6, ny))
                elif action == "backward":
                    nx = self.true_x_m - step_m * math.cos(self.true_yaw_rad)
                    ny = self.true_y_m - step_m * math.sin(self.true_yaw_rad)
                    self.true_x_m = max(-2.6, min(2.6, nx))
                    self.true_y_m = max(-1.6, min(1.6, ny))
                elif action == "left":
                    self.true_yaw_rad = wrap_angle_rad(self.true_yaw_rad + math.radians(20.0))
                elif action == "right":
                    self.true_yaw_rad = wrap_angle_rad(self.true_yaw_rad - math.radians(20.0))

        self._step_simulation(dt=0.0)
        return {"ok": True, "action": action}

    def get_state_payload(self) -> dict:
        with self.lock:
            pos_err = math.hypot(
                self.latest_loc_dict["x_m"] - self.true_x_m,
                self.latest_loc_dict["y_m"] - self.true_y_m,
            )
            return {
                "auto_patrol": self.auto_patrol,
                "true_pose": {
                    "x_m": round(self.true_x_m, 4),
                    "y_m": round(self.true_y_m, 4),
                    "yaw_rad": round(self.true_yaw_rad, 4),
                    "yaw_deg": round(math.degrees(self.true_yaw_rad), 1),
                    "true_region_id": ground_truth_region_for_xy(self.true_x_m, self.true_y_m),
                },
                "pos_error_m": round(pos_err, 4),
                "localization": self.latest_loc_dict,
                "vision_prediction": self.latest_vision_pred,
                "model_metrics": {
                    "val_acc": self.model_summary["held_out_val_metrics"]["top1_accuracy"],
                    "test_acc": self.model_summary["held_out_test_metrics"]["top1_accuracy"],
                },
                "scan_world_xy_m": self.latest_scan_world,
                "map_cells": self.map_dict["occupied_cells_xy_m"],
            }


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def make_sim_handler(sim: ClassroomSimulator):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                body = SIM_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/api/state":
                body = json.dumps(sim.get_state_payload()).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/api/camera.jpg":
                with sim.lock:
                    jpg = sim.latest_jpeg
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(jpg)))
                self.end_headers()
                self.wfile.write(jpg)
            else:
                self.send_error(404)

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/control":
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length > 0 else b"{}"
                req = json.loads(raw.decode("utf-8"))
                res = sim.apply_control(req.get("action", ""))
                body = json.dumps(res).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404)

    return Handler


def run_self_test() -> int:
    print("Running onboard/classroom_ai_simulator.py self-test...")
    with tempfile.TemporaryDirectory(prefix="classroom_sim_test_") as tmpdir:
        sim = ClassroomSimulator(Path(tmpdir))
        val_acc = sim.model_summary["held_out_val_metrics"]["top1_accuracy"]
        test_acc = sim.model_summary["held_out_test_metrics"]["top1_accuracy"]
        if val_acc < 0.90 or test_acc < 0.90:
            print("FAIL: Simulated classroom AI accuracy below 0.90:", sim.model_summary)
            return 1
        print(
            f"  [PASS 1/2] Virtual classroom 4-region AI trained & validated on held-out sessions: "
            f"val_acc={val_acc:.3f}, test_acc={test_acc:.3f}"
        )

        # Test kidnap / teleport recovery across quadrants using AI region seeding + LiDAR scan matching
        sim.apply_control("kidnap")
        state = sim.get_state_payload()
        if (
            state["localization"]["localization_status"] != "VALID"
            or state["pos_error_m"] > 0.12
            or state["true_pose"]["true_region_id"] != state["localization"]["visual_region_id"]
        ):
            print("FAIL: Kidnapped robot recovery failed:", state)
            return 1
        print(
            f"  [PASS 2/2] Kidnapped-robot recovery verified: AI recognized "
            f"{state['localization']['visual_region_id']} (conf={state['localization']['visual_confidence']:.2f}) "
            f"and LiDAR snapped to true pose (err={state['pos_error_m']*100:.1f} cm, status={state['localization']['localization_status']})"
        )
    print("SELF-TEST RESULT: PASS.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the interactive TT-02 Classroom Camera AI & LiDAR Localization Simulator."
    )
    parser.add_argument("--http-port", type=int, default=8085, help="HTTP port (default: 8085)")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "tt02_classroom_sim",
        help="Working directory for generated simulation dataset and model",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic classroom AI + kidnapped-robot recovery self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    sim = ClassroomSimulator(args.work_dir)

    def bg_loop():
        while sim.running:
            sim._step_simulation(dt=0.25)
            time.sleep(0.25)

    t = threading.Thread(target=bg_loop, daemon=True)
    t.start()

    server = ReusableThreadingHTTPServer(("0.0.0.0", args.http_port), make_sim_handler(sim))

    def handle_sig(sig, frame):
        sim.running = False
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    print(f"\nTT-02 Classroom AI & LiDAR Simulator running at http://127.0.0.1:{args.http_port}")
    try:
        server.serve_forever()
    finally:
        sim.running = False
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
