#!/usr/bin/env python3
"""
Unified Real-Time Perception, Scan-to-Map Localization & Obstacle Service (Cycles 4–5 — Member B).

Integrates all Member B perception and localization modules into one live service for
Member A's navigation planner and operator monitoring:
  1. RPLIDAR A2M8 360° scan stream (`--lidar-port /dev/ttyUSB0`) OR real-time recorded CSV
     replay (`--replay-csv data/raw/scan_run1_moved_object.csv`).
  2. Optional STM32 motion feedback stream (`--stm32-port /dev/ttyACM0` @ 115200 8N1) reading
     `BNO055` Euler heading (`H_cdeg=...`) and wheel-speed / control direction state (`Task BC`).
  3. Optional OV5647 visual region classifier (`--vision-model region_model.json`) running
     periodic frame classification (`Task B1/B2/B4/Cycle 3`).
  4. Continuous scan-to-map pose tracker (`LidarMapLocalizer`) + 8-sector obstacle extractor.
  5. HTTP JSON API & live 2D browser dashboard (`http://<pi-ip>:8082`) implementing the exact
     `Task AB` contract (`interfaces/LOCALIZATION_AND_PICKUP_INTERFACE.md`):
       - `GET  /api/localization`   -> Latest `LocalizationOutput` + aligned scan points
       - `GET  /api/pickup_poses`   -> Mapped pickup stopping poses & dispatch readiness
       - `POST /api/resolve_pickup` -> Validates `pickup_id` and localization health (`VALID`)
       - `POST /api/set_pose`       -> Resets/seeds initial `(x_m, y_m, yaw_deg)` pose
"""

import argparse
import io
import json
import math
import re
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from PIL import Image

from lidar_localize import (
    SECTOR_NAMES,
    LidarMapLocalizer,
    LocalizationOutput,
    MotionFeedbackInput,
    VisualRegionInput,
    wrap_angle_rad,
)
from lidar_mapper import OccupancyGridMapper, load_scans_from_csv
from vision_region_model import VisualRegionClassifier


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TT-02 Live Localization & Obstacle Service (Member B)</title>
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
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    background: var(--bg);
    color: var(--text);
    padding: 16px;
  }
  header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }
  h1 { margin: 0; font-size: 1.2rem; }
  .badge {
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.85rem;
    background: #1e293b;
  }
  .grid {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 16px;
  }
  @media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
  }
  .card h2 {
    margin: 0 0 10px 0;
    font-size: 0.95rem;
    color: var(--accent);
    text-transform: uppercase;
  }
  canvas {
    width: 100%;
    max-width: 620px;
    aspect-ratio: 1 / 1;
    background: #090d1a;
    border-radius: 8px;
    border: 1px solid var(--border);
    display: block;
    margin: 0 auto;
  }
  .kv {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 12px;
  }
  .kv-box {
    background: #0d1428;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 10px;
  }
  .kv-label { font-size: 0.72rem; color: var(--muted); }
  .kv-val { font-size: 1.05rem; font-weight: 700; margin-top: 2px; }
  .sectors {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
  }
  .sec-item {
    background: #0d1428;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px;
    text-align: center;
    font-size: 0.8rem;
  }
</style>
</head>
<body>
<header>
  <div>
    <h1>TT-02 Continuous Localization & Obstacle Service (Cycles 4–5)</h1>
    <div style="font-size:0.8rem;color:var(--muted)" id="subHeader">Connecting to /api/localization...</div>
  </div>
  <div class="badge" id="statusBadge">INITIALIZING</div>
</header>
<div class="grid">
  <div class="card">
    <h2>2D Map Frame Pose & Live RPLIDAR Scan Overlay</h2>
    <canvas id="mapCanvas" width="600" height="600"></canvas>
  </div>
  <div class="card">
    <h2>Planar Pose & Visual Region Constraint (Task AB)</h2>
    <div class="kv">
      <div class="kv-box"><div class="kv-label">Pose X (map)</div><div class="kv-val" id="valX">0.000 m</div></div>
      <div class="kv-box"><div class="kv-label">Pose Y (map)</div><div class="kv-val" id="valY">0.000 m</div></div>
      <div class="kv-box"><div class="kv-label">Heading Yaw</div><div class="kv-val" id="valYaw">0.0°</div></div>
      <div class="kv-box"><div class="kv-label">Inliers / Residual</div><div class="kv-val" id="valFit">--</div></div>
      <div class="kv-box"><div class="kv-label">Visual Region</div><div class="kv-val" id="valReg">UNKNOWN</div></div>
      <div class="kv-box"><div class="kv-label">Min Front Obstacle</div><div class="kv-val" id="valFront">-- m</div></div>
    </div>
    <h2>8-Sector Obstacle Distances (base_link)</h2>
    <div class="sectors" id="sectorGrid"></div>
    <h2 style="margin-top:14px">API Endpoints for Member A</h2>
    <div style="font-size:0.78rem;color:var(--muted);line-height:1.6">
      • <code>GET /api/localization</code> — Live pose, status, region & 8-sector obstacles<br>
      • <code>GET /api/pickup_poses</code> — Station stopping poses & dispatch readiness<br>
      • <code>POST /api/resolve_pickup</code> — Validate <code>{"pickup_id": "PICKUP_01"}</code>
    </div>
  </div>
</div>
<script>
const canvas = document.getElementById('mapCanvas');
const ctx = canvas.getContext('2d');
let mapCells = [];

async function poll() {
  try {
    const r = await fetch('/api/localization?include_map=1');
    const d = await r.json();
    if (d.occupied_cells_xy_m && d.occupied_cells_xy_m.length > 0) {
      mapCells = d.occupied_cells_xy_m;
    }
    const loc = d.localization;
    document.getElementById('valX').textContent = loc.x_m.toFixed(3) + ' m';
    document.getElementById('valY').textContent = loc.y_m.toFixed(3) + ' m';
    document.getElementById('valYaw').textContent = loc.yaw_deg.toFixed(1) + '°';
    document.getElementById('valFit').textContent = `${(loc.inlier_ratio*100).toFixed(0)}% / ${(loc.mean_residual_m*100).toFixed(1)}cm`;
    document.getElementById('valReg').textContent = `${loc.visual_region_id} (${(loc.visual_confidence*100).toFixed(0)}%)`;
    document.getElementById('valFront').textContent = loc.min_front_distance_m !== null ? loc.min_front_distance_m.toFixed(2) + ' m' : 'CLEAR';
    document.getElementById('subHeader').textContent = `Mode: ${d.mode} | Updates: ${d.update_count} | LiDAR: ${loc.lidar_health}`;

    const badge = document.getElementById('statusBadge');
    badge.textContent = loc.localization_status;
    badge.style.color = loc.localization_status === 'VALID' ? '#22c55e' : (loc.localization_status === 'DEGRADED' ? '#f59e0b' : '#ef4444');

    const sg = document.getElementById('sectorGrid');
    sg.innerHTML = '';
    for (const [sec, dist] of Object.entries(loc.sector_distances_m || {})) {
      const div = document.createElement('div');
      div.className = 'sec-item';
      const txt = dist !== null ? dist.toFixed(2) + 'm' : 'inf';
      div.innerHTML = `<div style="color:#94a3b8">${sec}</div><div style="font-weight:700;margin-top:2px">${txt}</div>`;
      sg.appendChild(div);
    }

    drawMap(loc, d.scan_world_xy_m || []);
  } catch (e) {}
}

function drawMap(loc, scanPts) {
  const W = canvas.width, H = canvas.height;
  const half = W / 2;
  const maxR = 4.0;
  const scale = (half - 24) / maxR;
  ctx.clearRect(0, 0, W, H);

  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  for (let r = 1; r <= 4; r++) {
    ctx.beginPath();
    ctx.arc(half, half, r * scale, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.beginPath();
  ctx.moveTo(0, half); ctx.lineTo(W, half);
  ctx.moveTo(half, 0); ctx.lineTo(half, H);
  ctx.stroke();

  // Occupied map cells (blue-grey squares)
  ctx.fillStyle = '#475569';
  for (const [mx, my] of mapCells) {
    const px = half + my * scale;
    const py = half - mx * scale;
    ctx.fillRect(px - 2, py - 2, 4, 4);
  }

  // Live aligned scan points (cyan)
  ctx.fillStyle = '#38bdf8';
  for (const [sx, sy] of scanPts) {
    const px = half + sy * scale;
    const py = half - sx * scale;
    ctx.beginPath();
    ctx.arc(px, py, 2.2, 0, Math.PI * 2);
    ctx.fill();
  }

  // Vehicle pose arrow
  const vx = half + loc.y_m * scale;
  const vy = half - loc.x_m * scale;
  const hx = vx + 18 * Math.sin(loc.yaw_rad);
  const hy = vy - 18 * Math.cos(loc.yaw_rad);
  ctx.strokeStyle = '#22c55e';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(vx, vy);
  ctx.lineTo(hx, hy);
  ctx.stroke();
  ctx.fillStyle = '#ef4444';
  ctx.beginPath();
  ctx.arc(vx, vy, 5, 0, Math.PI * 2);
  ctx.fill();
}

setInterval(poll, 350);
poll();
</script>
</body>
</html>
"""


class LocalizationServiceEngine:
    """Thread-safe coordinator for live RPLIDAR, STM32 feedback, OV5647 region inference, and scan-to-map localization."""

    def __init__(
        self,
        map_dict: dict,
        mode: str,
        lidar_port: Optional[str] = None,
        replay_csv: Optional[Path] = None,
        stm32_port: Optional[str] = None,
        vision_model_path: Optional[Path] = None,
        loop_replay: bool = True,
    ):
        self.map_dict = map_dict
        self.mode = mode
        self.lidar_port = lidar_port
        self.replay_csv = replay_csv
        self.stm32_port = stm32_port
        self.loop_replay = loop_replay

        self.localizer = LidarMapLocalizer(map_dict)
        self.localizer.set_initial_pose(0.0, 0.0, 0.0)

        self.vision_clf: Optional[VisualRegionClassifier] = None
        if vision_model_path is not None and vision_model_path.is_file():
            self.vision_clf = VisualRegionClassifier.load_json(vision_model_path)

        self.lock = threading.Lock()
        self.running = True
        self.update_count = 0
        self.latest_motion: Optional[MotionFeedbackInput] = None
        self.latest_visual: Optional[VisualRegionInput] = None
        self.latest_scan_world: List[Tuple[float, float]] = []
        self.latest_output = LocalizationOutput(
            timestamp_s=time.time(),
            x_m=0.0,
            y_m=0.0,
            yaw_rad=0.0,
            localization_status="UNINITIALIZED",
            inlier_ratio=0.0,
            mean_residual_m=float("inf"),
            lidar_health="STALE",
            sector_distances_m={k: float("inf") for k in SECTOR_NAMES},
        )

        self.threads: List[threading.Thread] = []

    def start(self) -> None:
        if self.stm32_port:
            t_stm = threading.Thread(target=self._stm32_loop, daemon=True)
            t_stm.start()
            self.threads.append(t_stm)

        if self.vision_clf is not None:
            t_vis = threading.Thread(target=self._vision_loop, daemon=True)
            t_vis.start()
            self.threads.append(t_vis)

        if self.mode == "replay":
            t_lid = threading.Thread(target=self._replay_loop, daemon=True)
        else:
            t_lid = threading.Thread(target=self._live_lidar_loop, daemon=True)
        t_lid.start()
        self.threads.append(t_lid)

    def stop(self) -> None:
        self.running = False

    def _process_scan(self, ts: float, scan_polar: List[Tuple[float, float]]) -> None:
        with self.lock:
            motion = self.latest_motion
            visual = self.latest_visual
            out = self.localizer.update_from_scan(
                timestamp_s=ts,
                scan_polar=scan_polar,
                motion=motion,
                visual=visual,
            )
            # Project subsampled scan into world coordinates for dashboard visualization
            step = max(1, len(scan_polar) // 90)
            world_pts: List[Tuple[float, float]] = []
            for ang_rad, dist_m in scan_polar[::step]:
                wang = out.yaw_rad + ang_rad
                wx = round(out.x_m + dist_m * math.cos(wang), 3)
                wy = round(out.y_m + dist_m * math.sin(wang), 3)
                world_pts.append((wx, wy))
            self.latest_scan_world = world_pts
            self.latest_output = out
            self.update_count += 1

    def _replay_loop(self) -> None:
        assert self.replay_csv is not None
        scans, timestamps = load_scans_from_csv(self.replay_csv)
        scan_ids = sorted(scans.keys())
        if not scan_ids:
            return
        while self.running:
            for sid in scan_ids:
                if not self.running:
                    break
                self._process_scan(time.time(), scans[sid])
                time.sleep(0.09)
            if not self.loop_replay:
                break

    def _live_lidar_loop(self) -> None:
        """Connect to RPLIDAR A2M8 over `/dev/ttyUSB0`, spin motor (PWM=660), and stream 360° scans."""
        from rplidar import RPLidar

        def set_a2_pwm(lidar_obj, pwm: int):
            payload = struct.pack("<H", pwm)
            req = bytes([0xA5, 0xF0, len(payload)]) + payload
            checksum = 0
            for b in req:
                checksum ^= b
            req += bytes([checksum])
            lidar_obj._serial_port.write(req)
            lidar_obj._serial_port.flush()

        lidar = None
        try:
            lidar = RPLidar(self.lidar_port, baudrate=115200, timeout=3)
            lidar._serial_port.dtr = False
            lidar.start_motor()
            set_a2_pwm(lidar, 660)
            time.sleep(1.0)
            for scan in lidar.iter_scans(max_buf_meas=1500):
                if not self.running:
                    break
                polar: List[Tuple[float, float]] = []
                for quality, angle_deg, dist_mm in scan:
                    dist_m = dist_mm / 1000.0
                    if quality >= 1 and 0.15 <= dist_m <= 6.50:
                        polar.append((math.radians(angle_deg), dist_m))
                if len(polar) >= 15:
                    self._process_scan(time.time(), polar)
        except Exception as exc:
            print(f"[LiDAR Loop] Error: {exc}", file=sys.stderr)
            with self.lock:
                self.latest_output.lidar_health = "DISCONNECTED"
                self.latest_output.localization_status = "LOST"
        finally:
            if lidar is not None:
                try:
                    lidar.stop()
                    time.sleep(0.1)
                    set_a2_pwm(lidar, 0)
                    lidar._serial_port.dtr = True
                    lidar.stop_motor()
                    lidar.disconnect()
                except Exception:
                    pass

    def _stm32_loop(self) -> None:
        """Read periodic `H_cdeg=...` and `STATUS` lines from STM32 over `/dev/ttyACM0`."""
        import serial

        euler_re = re.compile(r"H_cdeg=(-?\d+)")
        esc_re = re.compile(r"ESC_US=(\d+)")
        while self.running:
            try:
                with serial.Serial(self.stm32_port, 115200, timeout=0.5) as ser:
                    direction_state = "NEUTRAL_STOP"
                    while self.running:
                        raw = ser.readline()
                        if not raw:
                            continue
                        line = raw.decode("ascii", errors="ignore").strip()
                        m_esc = esc_re.search(line)
                        if m_esc:
                            esc_us = int(m_esc.group(1))
                            if esc_us > 1520:
                                direction_state = "FWD"
                            elif esc_us < 1480:
                                direction_state = "REV"
                            else:
                                direction_state = "NEUTRAL_STOP"
                        m_eu = euler_re.search(line)
                        if m_eu:
                            h_cdeg = int(m_eu.group(1))
                            with self.lock:
                                self.latest_motion = MotionFeedbackInput(
                                    timestamp_s=time.time(),
                                    speed_m_s=0.0,
                                    direction_state=direction_state,
                                    imu_heading_cdeg=h_cdeg,
                                )
            except Exception:
                time.sleep(1.0)

    def _vision_loop(self) -> None:
        """Periodically capture one JPEG frame via `rpicam-still` and classify the map region."""
        while self.running and self.vision_clf is not None:
            try:
                proc = subprocess.run(
                    [
                        "rpicam-still",
                        "-n",
                        "--width",
                        "640",
                        "--height",
                        "480",
                        "-t",
                        "200",
                        "-o",
                        "-",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    timeout=3.0,
                    check=False,
                )
                if proc.returncode == 0 and proc.stdout.startswith(b"\xff\xd8"):
                    with Image.open(io.BytesIO(proc.stdout)) as im:
                        pred = self.vision_clf.predict_image(im)
                    with self.lock:
                        self.latest_visual = VisualRegionInput(
                            timestamp_s=time.time(),
                            visual_region_id=pred["visual_region_id"],
                            visual_confidence=pred["visual_confidence"],
                            validated_on_held_out_runs=pred["validated_on_held_out_runs"],
                        )
            except Exception:
                pass
            time.sleep(1.5)

    def get_state_dict(self, include_map: bool = False) -> dict:
        with self.lock:
            payload = {
                "mode": self.mode,
                "update_count": self.update_count,
                "localization": self.latest_output.to_dict(),
                "scan_world_xy_m": self.latest_scan_world,
            }
            if include_map:
                payload["occupied_cells_xy_m"] = self.map_dict.get(
                    "occupied_cells_xy_m", []
                )
            return payload

    def get_pickup_poses_dict(self) -> dict:
        with self.lock:
            loc = self.latest_output
            dispatch_ready = (
                loc.localization_status == "VALID" and loc.lidar_health == "OK"
            )
            return {
                "dispatch_ready": dispatch_ready,
                "localization_status": loc.localization_status,
                "lidar_health": loc.lidar_health,
                "pickup_poses": self.map_dict.get("pickup_poses", {}),
            }

    def resolve_pickup_request(self, pickup_id: str) -> Tuple[int, dict]:
        """
        Validate a pickup request against the Task AB boundary rules:
          1. Rejects unknown or unmapped `pickup_id` (`STATION_UNMAPPED` / `UNKNOWN_PICKUP_ID`).
          2. Rejects if `localization_status != VALID` or `lidar_health != OK` (`LOCALIZATION_UNAVAILABLE`).
          3. Returns mapped target stopping pose `(target_x_m, target_y_m, target_yaw_rad)` and current vehicle pose.
        """
        pickup_id = (pickup_id or "").strip()
        pickup_table = self.map_dict.get("pickup_poses", {})
        if not pickup_id or pickup_id not in pickup_table:
            return 404, {
                "accepted": False,
                "pickup_id": pickup_id,
                "reason": "UNKNOWN_PICKUP_ID",
            }

        target = pickup_table[pickup_id]
        if (
            target is None
            or target.get("target_x_m") is None
            or target.get("target_y_m") is None
            or target.get("target_yaw_rad") is None
        ):
            return 409, {
                "accepted": False,
                "pickup_id": pickup_id,
                "reason": "STATION_UNMAPPED",
            }

        with self.lock:
            loc = self.latest_output.to_dict()

        if loc["localization_status"] != "VALID" or loc["lidar_health"] != "OK":
            return 409, {
                "accepted": False,
                "pickup_id": pickup_id,
                "reason": "LOCALIZATION_UNAVAILABLE",
                "localization_status": loc["localization_status"],
            }

        return 200, {
            "accepted": True,
            "pickup_id": pickup_id,
            "reason": "ACCEPTED",
            "target_stopping_pose": target,
            "current_vehicle_pose": {
                "x_m": loc["x_m"],
                "y_m": loc["y_m"],
                "yaw_rad": loc["yaw_rad"],
            },
        }


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def make_handler(engine: LocalizationServiceEngine):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send_json(self, code: int, data: dict) -> None:
            body = json.dumps(data).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                body = DASHBOARD_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/api/localization":
                inc_map = "include_map=1" in (parsed.query or "")
                self._send_json(200, engine.get_state_dict(include_map=inc_map))
            elif parsed.path == "/api/pickup_poses":
                self._send_json(200, engine.get_pickup_poses_dict())
            else:
                self.send_error(404)

        def do_POST(self):
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                req = json.loads(raw.decode("utf-8"))
            except Exception:
                self._send_json(400, {"ok": False, "error": "Invalid JSON"})
                return

            if parsed.path == "/api/resolve_pickup":
                code, resp = engine.resolve_pickup_request(req.get("pickup_id", ""))
                self._send_json(code, resp)
            elif parsed.path == "/api/set_pose":
                x_m = float(req.get("x_m", 0.0))
                y_m = float(req.get("y_m", 0.0))
                yaw_rad = math.radians(float(req.get("yaw_deg", 0.0)))
                with engine.lock:
                    engine.localizer.set_initial_pose(x_m, y_m, yaw_rad)
                self._send_json(
                    200, {"ok": True, "x_m": x_m, "y_m": y_m, "yaw_rad": yaw_rad}
                )
            else:
                self.send_error(404)

    return Handler


def run_self_test() -> int:
    """
    End-to-end self-test verifying the live HTTP Localization & Obstacle Service (`Task AB` + Cycles 4–5):
      1. Builds a synthetic room map + temporary scan CSV with 1 mapped station (`PICKUP_01`)
         and 1 unmapped station (`PICKUP_02`).
      2. Starts `LocalizationServiceEngine` + HTTP server on an ephemeral port.
      3. Verifies `/api/localization` reaches `localization_status == "VALID"`.
      4. Verifies `POST /api/resolve_pickup` accepts `PICKUP_01`, rejects unmapped `PICKUP_02`
         (`STATION_UNMAPPED`), and rejects unknown `PICKUP_99` (`UNKNOWN_PICKUP_ID`).
    """
    import urllib.error
    import urllib.request

    print("Running onboard/localization_service.py self-test (Cycles 4–5 Live Service)...")
    mapper = OccupancyGridMapper(resolution_m=0.05, half_extent_m=3.0)
    scan_rows = ["timestamp_s,scan_id,quality,angle_deg,distance_mm"]
    scan_polar: List[Tuple[float, float]] = []
    for deg in range(0, 360, 3):
        rad = math.radians(deg)
        ca, sa = math.cos(rad), math.sin(rad)
        tx = (2.2 / ca) if ca > 1e-6 else ((-1.5 / ca) if ca < -1e-6 else 1e9)
        ty = (1.7 / sa) if sa > 1e-6 else ((-1.3 / sa) if sa < -1e-6 else 1e9)
        dist_m = min(tx, ty)
        scan_polar.append((rad, dist_m))
        for sid in range(1, 6):
            scan_rows.append(
                f"{1762800000.0 + sid*0.1:.3f},{sid},15,{deg:.2f},{dist_m*1000.0:.1f}"
            )

    for _ in range(10):
        mapper.integrate_scan(scan_polar, (0.0, 0.0, 0.0))

    map_dict = mapper.to_map_dict("service_self_test")
    map_dict["pickup_poses"] = {
        "PICKUP_01": {
            "target_x_m": 1.10,
            "target_y_m": 0.45,
            "target_yaw_rad": 0.0,
            "arrival_xy_tol_m": 0.15,
            "arrival_yaw_tol_rad": 0.25,
        },
        "PICKUP_02": {
            "target_x_m": None,
            "target_y_m": None,
            "target_yaw_rad": None,
        },
    }

    with tempfile.TemporaryDirectory(prefix="loc_service_test_") as tmpdir:
        csv_path = Path(tmpdir) / "test_scans.csv"
        csv_path.write_text("\n".join(scan_rows) + "\n", encoding="utf-8")

        engine = LocalizationServiceEngine(
            map_dict=map_dict,
            mode="replay",
            replay_csv=csv_path,
            loop_replay=True,
        )
        engine.start()
        server = ReusableThreadingHTTPServer(("127.0.0.1", 0), make_handler(engine))
        port = server.server_address[1]
        srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
        srv_thread.start()

        try:
            # Wait for first scan localization update
            deadline = time.time() + 3.0
            loc_data = None
            while time.time() < deadline:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/api/localization", timeout=1.0
                ) as resp:
                    loc_data = json.loads(resp.read().decode("utf-8"))
                if loc_data["update_count"] >= 1:
                    break
                time.sleep(0.05)

            if not loc_data or loc_data["localization"]["localization_status"] != "VALID":
                print("FAIL [1/3]: Service did not reach VALID status:", loc_data)
                return 1
            print(
                f"  [PASS 1/3] Live HTTP /api/localization verified: "
                f"status={loc_data['localization']['localization_status']}, "
                f"pose=({loc_data['localization']['x_m']}m, {loc_data['localization']['y_m']}m), "
                f"min_front={loc_data['localization']['min_front_distance_m']}m"
            )

            def post_resolve(pid: str) -> Tuple[int, dict]:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/resolve_pickup",
                    data=json.dumps({"pickup_id": pid}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=1.0) as r:
                        return r.status, json.loads(r.read().decode("utf-8"))
                except urllib.error.HTTPError as e:
                    return e.code, json.loads(e.read().decode("utf-8"))

            code1, res1 = post_resolve("PICKUP_01")
            if code1 != 200 or not res1.get("accepted"):
                print("FAIL [2/3]: PICKUP_01 should be accepted:", code1, res1)
                return 1
            print(
                f"  [PASS 2/3] Mapped station PICKUP_01 accepted -> "
                f"target={res1['target_stopping_pose']}"
            )

            code2, res2 = post_resolve("PICKUP_02")
            code3, res3 = post_resolve("PICKUP_99")
            if (
                code2 != 409
                or res2.get("reason") != "STATION_UNMAPPED"
                or code3 != 404
                or res3.get("reason") != "UNKNOWN_PICKUP_ID"
            ):
                print("FAIL [3/3]: Rejection rules failed:", code2, res2, code3, res3)
                return 1
            print(
                f"  [PASS 3/3] Unmapped/unknown station rejection verified: "
                f"PICKUP_02->{res2['reason']} (HTTP {code2}), PICKUP_99->{res3['reason']} (HTTP {code3})"
            )
        finally:
            engine.stop()
            server.shutdown()
            server.server_close()

    print("SELF-TEST RESULT: PASS.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the TT-02 Live Perception, Scan-to-Map Localization & Obstacle HTTP Service."
    )
    parser.add_argument(
        "--map",
        type=Path,
        default=None,
        help="Path to occupancy map JSON generated by onboard/lidar_mapper.py",
    )
    parser.add_argument(
        "--lidar-port",
        type=str,
        default=None,
        help="Live RPLIDAR A2M8 serial port (e.g. /dev/ttyUSB0)",
    )
    parser.add_argument(
        "--replay-csv",
        type=Path,
        default=None,
        help="Replay a recorded scan CSV instead of spinning the physical LiDAR",
    )
    parser.add_argument(
        "--stm32-port",
        type=str,
        default=None,
        help="Optional STM32 serial port for live IMU/motion feedback (e.g. /dev/ttyACM0)",
    )
    parser.add_argument(
        "--vision-model",
        type=Path,
        default=None,
        help="Optional trained visual region model JSON from onboard/vision_region_model.py",
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8082,
        help="HTTP port for dashboard and JSON API (default: 8082)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic end-to-end HTTP API & localization self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.map is None or (args.lidar_port is None and args.replay_csv is None):
        parser.error(
            "Provide --map along with either --lidar-port (live hardware) or --replay-csv (recorded replay), or use --self-test."
        )

    map_dict = json.loads(args.map.read_text(encoding="utf-8"))
    mode = "replay" if args.replay_csv is not None else "live_hardware"
    engine = LocalizationServiceEngine(
        map_dict=map_dict,
        mode=mode,
        lidar_port=args.lidar_port,
        replay_csv=args.replay_csv,
        stm32_port=args.stm32_port,
        vision_model_path=args.vision_model,
    )
    engine.start()
    server = ReusableThreadingHTTPServer(("0.0.0.0", args.http_port), make_handler(engine))

    def handle_sig(sig, frame):
        print("\nStopping Localization Service...")
        engine.stop()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    print(
        f"TT-02 Localization & Obstacle Service ({mode}) running at http://0.0.0.0:{args.http_port}"
    )
    try:
        server.serve_forever()
    finally:
        engine.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
