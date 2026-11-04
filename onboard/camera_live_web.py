#!/usr/bin/env python3
"""
Raspberry Pi 4 + Camera Module Rev 1.3 (OV5647) Live Web Stream & Dataset Capture Tool.

Provides:
  - Live MJPEG video stream over HTTP (/stream.mjpg) via Picamera2
  - Interactive browser UI (http://<pi-ip>:8081) with live FPS, resolution, and orientation flip
  - One-click labelled frame capture that saves JPEGs and appends session-separated metadata
    to a dataset manifest CSV (for Tasks B1, B2, B4, and Cycle 2 region dataset collection)
"""

import argparse
import csv
import io
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from PIL import Image


MANIFEST_COLUMNS = [
    "image_id",
    "relative_path",
    "timestamp_s",
    "iso_utc",
    "session_id",
    "region_id",
    "heading_sector",
    "viewpoint_offset",
    "lighting_condition",
    "motion_state",
    "split",
    "width",
    "height",
    "camera_model",
]


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TT-02 Onboard Camera (OV5647) Live Stream & Dataset Recorder</title>
<style>
  :root {
    --bg: #0b1020;
    --panel: #131b33;
    --border: #25335a;
    --accent: #38bdf8;
    --green: #22c55e;
    --amber: #f59e0b;
    --text: #e2e8f0;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 18px;
  }
  header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
  }
  h1 {
    font-size: 1.25rem;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .badge {
    font-size: 0.78rem;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.15);
    color: var(--green);
    border: 1px solid rgba(34, 197, 94, 0.4);
    font-weight: 600;
  }
  .layout {
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 18px;
  }
  @media (max-width: 960px) {
    .layout { grid-template-columns: 1fr; }
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
  }
  .video-wrap {
    position: relative;
    width: 100%;
    background: #050811;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 360px;
  }
  .video-wrap img {
    width: 100%;
    max-height: 72vh;
    object-fit: contain;
    display: block;
  }
  .stats-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 12px;
    font-size: 0.85rem;
    color: var(--muted);
  }
  .stats-bar span strong { color: var(--text); }
  .form-group { margin-bottom: 11px; }
  label {
    display: block;
    font-size: 0.8rem;
    color: var(--muted);
    margin-bottom: 4px;
  }
  input, select {
    width: 100%;
    padding: 8px 10px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: #0b1020;
    color: var(--text);
    font-size: 0.9rem;
  }
  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  button {
    cursor: pointer;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: opacity 0.15s;
  }
  button:hover { opacity: 0.92; }
  .btn-primary {
    width: 100%;
    background: var(--accent);
    color: #061224;
    margin-top: 6px;
  }
  .btn-secondary {
    background: #1e293b;
    color: var(--text);
    border: 1px solid var(--border);
  }
  .log-box {
    margin-top: 12px;
    padding: 10px;
    border-radius: 6px;
    background: #070b16;
    border: 1px solid var(--border);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.78rem;
    max-height: 150px;
    overflow-y: auto;
    color: #cbd5e1;
  }
</style>
</head>
<body>
<header>
  <h1>
    <span>TT-02 Onboard Camera: Raspberry Pi Cam Rev 1.3 (OV5647)</span>
    <span class="badge" id="statusBadge">LIVE STREAMING</span>
  </h1>
  <div>
    <button class="btn-secondary" onclick="toggleFlip()">Flip 180° (Upside-Down Toggle)</button>
  </div>
</header>

<div class="layout">
  <div class="card">
    <div class="video-wrap">
      <img id="streamImg" src="/stream.mjpg" alt="Live OV5647 CSI Stream">
    </div>
    <div class="stats-bar">
      <span>Sensor: <strong id="stSensor">ov5647 (CSI-2)</strong></span>
      <span>Resolution: <strong id="stRes">-</strong></span>
      <span>Stream FPS: <strong id="stFps">-</strong></span>
      <span>Saved Frames: <strong id="stCount">0</strong></span>
      <span>Flip 180°: <strong id="stFlip">OFF</strong></span>
    </div>
  </div>

  <div class="card">
    <h2 style="margin-top:0;font-size:1.05rem;">Labelled Frame Capture (Task B2/B4)</h2>
    <div class="form-group">
      <label>Session ID (keep unique per run to prevent train/val leakage)</label>
      <input type="text" id="session_id" value="20261103_session01">
    </div>
    <div class="row-2">
      <div class="form-group">
        <label>Map Region ID</label>
        <input type="text" id="region_id" value="REGION_01">
      </div>
      <div class="form-group">
        <label>Dataset Split</label>
        <select id="split">
          <option value="train">train</option>
          <option value="val">val</option>
          <option value="test">test</option>
        </select>
      </div>
    </div>
    <div class="row-2">
      <div class="form-group">
        <label>Heading Sector</label>
        <select id="heading_sector">
          <option value="N">N (0°)</option>
          <option value="NE">NE (45°)</option>
          <option value="E">E (90°)</option>
          <option value="SE">SE (135°)</option>
          <option value="S">S (180°)</option>
          <option value="SW">SW (225°)</option>
          <option value="W">W (270°)</option>
          <option value="NW">NW (315°)</option>
        </select>
      </div>
      <div class="form-group">
        <label>Viewpoint Offset</label>
        <select id="viewpoint_offset">
          <option value="center">center</option>
          <option value="left_offset">left_offset</option>
          <option value="right_offset">right_offset</option>
        </select>
      </div>
    </div>
    <div class="row-2">
      <div class="form-group">
        <label>Lighting Condition</label>
        <select id="lighting_condition">
          <option value="artificial_indoor">artificial_indoor</option>
          <option value="daylight_indoor">daylight_indoor</option>
          <option value="mixed_indoor">mixed_indoor</option>
          <option value="dim_indoor">dim_indoor</option>
        </select>
      </div>
      <div class="form-group">
        <label>Motion State</label>
        <select id="motion_state">
          <option value="stationary">stationary</option>
          <option value="low_speed">low_speed</option>
        </select>
      </div>
    </div>
    <button class="btn-primary" onclick="captureFrame()">Capture & Log Frame to Manifest</button>
    <div class="log-box" id="logBox">Ready. Click "Capture & Log Frame" to save JPEG + CSV manifest row.</div>
  </div>
</div>

<script>
function logMsg(msg) {
  const box = document.getElementById('logBox');
  const ts = new Date().toLocaleTimeString();
  box.innerHTML = `[${ts}] ${msg}<br>` + box.innerHTML;
}

async function pollStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('stRes').textContent = `${d.width}x${d.height}`;
    document.getElementById('stFps').textContent = d.fps.toFixed(1);
    document.getElementById('stCount').textContent = d.saved_count;
    document.getElementById('stFlip').textContent = d.flip_180 ? 'ON' : 'OFF';
    const badge = document.getElementById('statusBadge');
    if (d.fps < 0.5) {
      badge.textContent = 'RECONNECTING CAMERA...';
      badge.style.color = '#f59e0b';
      document.getElementById('streamImg').src = '/stream.mjpg?t=' + Date.now();
    } else {
      badge.textContent = 'LIVE STREAMING';
      badge.style.color = '#22c55e';
    }
  } catch (e) {}
}

async function toggleFlip() {
  const r = await fetch('/api/flip', { method: 'POST' });
  const d = await r.json();
  document.getElementById('stFlip').textContent = d.flip_180 ? 'ON' : 'OFF';
  logMsg(`Orientation flip_180 set to ${d.flip_180}`);
}

async function captureFrame() {
  const payload = {
    session_id: document.getElementById('session_id').value.trim(),
    region_id: document.getElementById('region_id').value.trim(),
    split: document.getElementById('split').value,
    heading_sector: document.getElementById('heading_sector').value,
    viewpoint_offset: document.getElementById('viewpoint_offset').value,
    lighting_condition: document.getElementById('lighting_condition').value,
    motion_state: document.getElementById('motion_state').value,
  };
  const r = await fetch('/api/capture', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const d = await r.json();
  if (d.ok) {
    logMsg(`Saved <b>${d.image_id}</b> (${d.relative_path}) [${d.split}/${d.region_id}]`);
    pollStatus();
  } else {
    logMsg(`<span style="color:#f87171">Error: ${d.error}</span>`);
  }
}

setInterval(pollStatus, 1000);
pollStatus();
</script>
</body>
</html>
"""


class CameraStreamer:
    def __init__(self, width: int, height: int, fps: int, out_dir: str):
        self.width = width
        self.height = height
        self.target_fps = fps
        self.out_dir = os.path.abspath(out_dir)
        self.images_dir = os.path.join(self.out_dir, "images")
        self.manifest_path = os.path.join(self.out_dir, "manifest.csv")
        os.makedirs(self.images_dir, exist_ok=True)
        self._init_manifest()

        self.lock = threading.Condition()
        self.latest_jpeg = None
        self.latest_pil = None
        self.frame_count = 0
        self.measured_fps = 0.0
        self.flip_180 = False
        self.running = True
        self.saved_count = self._count_existing_rows()
        self.session_splits = self._load_session_splits()
        self.last_frame_mono = time.monotonic()
        self.restart_count = 0
        self.proc = None
        self.proc_lock = threading.Lock()

        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.watchdog_thread.start()

    def _spawn_rpicam(self):
        with self.proc_lock:
            self._kill_rpicam_unlocked()
            cmd = [
                "rpicam-vid",
                "-n",
                "--width",
                str(self.width),
                "--height",
                str(self.height),
                "--framerate",
                str(self.target_fps),
                "--codec",
                "mjpeg",
                "-t",
                "0",
                "--flush",
                "-o",
                "-",
            ]
            if self.flip_180:
                cmd.extend(["--rotation", "180"])
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=0,
            )
            self.last_frame_mono = time.monotonic()
            return self.proc

    def _kill_rpicam_unlocked(self):
        if self.proc is not None:
            try:
                self.proc.kill()
                self.proc.wait(timeout=1.0)
            except Exception:
                pass
            self.proc = None

    def trigger_restart(self, reason: str):
        print(f"[Watchdog] {reason} -> restarting rpicam-vid subprocess...", flush=True)
        self.restart_count += 1
        with self.proc_lock:
            self._kill_rpicam_unlocked()

    def _watchdog_loop(self):
        while self.running:
            time.sleep(0.8)
            if time.monotonic() - self.last_frame_mono > 2.2:
                self.measured_fps = 0.0
                self.trigger_restart("CSI frame timeout (>2.2s)")

    def _init_manifest(self):
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(MANIFEST_COLUMNS)

    def _count_existing_rows(self) -> int:
        if not os.path.exists(self.manifest_path):
            return 0
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return max(0, sum(1 for _ in f) - 1)

    def _load_session_splits(self) -> dict:
        mapping = {}
        if not os.path.exists(self.manifest_path):
            return mapping
        with open(self.manifest_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = row.get("session_id", "")
                sp = row.get("split", "")
                if sid and sp:
                    mapping[sid] = sp
        return mapping

    def _capture_loop(self):
        SOI = b"\xff\xd8"
        EOI = b"\xff\xd9"
        while self.running:
            proc = self._spawn_rpicam()
            buf = bytearray()
            last_t = time.monotonic()
            frames_since = 0
            try:
                while self.running and proc.poll() is None:
                    chunk = proc.stdout.read(16384)
                    if not chunk:
                        break
                    buf.extend(chunk)
                    while True:
                        start = buf.find(SOI)
                        if start == -1:
                            if len(buf) > 2:
                                del buf[:-2]
                            break
                        end = buf.find(EOI, start + 2)
                        if end == -1:
                            if start > 0:
                                del buf[:start]
                            break
                        jpeg_bytes = bytes(buf[start : end + 2])
                        del buf[: end + 2]

                        now = time.monotonic()
                        self.last_frame_mono = now
                        with self.lock:
                            self.latest_jpeg = jpeg_bytes
                            self.frame_count += 1
                            self.lock.notify_all()

                        frames_since += 1
                        if now - last_t >= 1.0:
                            self.measured_fps = frames_since / (now - last_t)
                            frames_since = 0
                            last_t = now
            except Exception:
                pass
            if self.running:
                time.sleep(0.3)

    def save_labelled_frame(self, meta: dict) -> dict:
        session_id = meta.get("session_id", "").strip() or "default_session"
        region_id = meta.get("region_id", "").strip() or "REGION_01"
        split = meta.get("split", "train").strip()
        heading_sector = meta.get("heading_sector", "N").strip()
        viewpoint_offset = meta.get("viewpoint_offset", "center").strip()
        lighting_condition = meta.get("lighting_condition", "artificial_indoor").strip()
        motion_state = meta.get("motion_state", "stationary").strip()

        if split not in ("train", "val", "test"):
            return {"ok": False, "error": f"Invalid split '{split}'"}

        # Enforce strict session-separation rule (Task B2)
        if session_id in self.session_splits and self.session_splits[session_id] != split:
            prev = self.session_splits[session_id]
            return {
                "ok": False,
                "error": (
                    f"Session leakage blocked: session_id '{session_id}' is already assigned "
                    f"to split '{prev}'. Change session_id before recording for '{split}'."
                ),
            }

        with self.lock:
            if not self.latest_jpeg:
                return {"ok": False, "error": "No camera frame available yet"}
            jpeg_copy = self.latest_jpeg

        now_ts = time.time()
        iso_utc = datetime.fromtimestamp(now_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.saved_count += 1
        image_id = f"img_{int(now_ts * 1000)}_{self.saved_count:04d}"
        rel_dir = os.path.join("images", session_id)
        os.makedirs(os.path.join(self.out_dir, rel_dir), exist_ok=True)
        rel_path = os.path.join(rel_dir, f"{image_id}.jpg")
        abs_path = os.path.join(self.out_dir, rel_path)

        with open(abs_path, "wb") as f:
            f.write(jpeg_copy)
        self.session_splits[session_id] = split

        row = [
            image_id,
            rel_path,
            f"{now_ts:.3f}",
            iso_utc,
            session_id,
            region_id,
            heading_sector,
            viewpoint_offset,
            lighting_condition,
            motion_state,
            split,
            self.width,
            self.height,
            "ov5647",
        ]
        with open(self.manifest_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)

        return {
            "ok": True,
            "image_id": image_id,
            "relative_path": rel_path,
            "session_id": session_id,
            "region_id": region_id,
            "split": split,
            "saved_count": self.saved_count,
        }

    def close(self):
        self.running = False
        with self.proc_lock:
            self._kill_rpicam_unlocked()


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def make_handler(streamer: CameraStreamer):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                body = HTML_PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/api/status":
                payload = json.dumps(
                    {
                        "sensor": "ov5647",
                        "width": streamer.width,
                        "height": streamer.height,
                        "fps": streamer.measured_fps,
                        "saved_count": streamer.saved_count,
                        "flip_180": streamer.flip_180,
                        "out_dir": streamer.out_dir,
                    }
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
            elif parsed.path == "/stream.mjpg":
                self.send_response(200)
                self.send_header("Age", "0")
                self.send_header("Cache-Control", "no-cache, private")
                self.send_header("Pragma", "no-cache")
                self.send_header(
                    "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
                )
                self.end_headers()
                try:
                    last_sent = -1
                    while streamer.running:
                        with streamer.lock:
                            streamer.lock.wait(timeout=1.0)
                            if streamer.frame_count == last_sent or not streamer.latest_jpeg:
                                continue
                            frame = streamer.latest_jpeg
                            last_sent = streamer.frame_count
                        self.wfile.write(b"--FRAME\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(frame)))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.send_error(404)

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/flip":
                streamer.flip_180 = not streamer.flip_180
                streamer.trigger_restart("Rotation flip toggled")
                payload = json.dumps({"ok": True, "flip_180": streamer.flip_180}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
            elif parsed.path == "/api/capture":
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length > 0 else b"{}"
                meta = json.loads(raw.decode("utf-8"))
                result = streamer.save_labelled_frame(meta)
                payload = json.dumps(result).encode("utf-8")
                self.send_response(200 if result.get("ok") else 400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_error(404)

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Live OV5647 CSI Camera Web Stream & Dataset Recorder")
    parser.add_argument("--http-port", type=int, default=8081, help="HTTP port (default: 8081)")
    parser.add_argument("--width", type=int, default=640, help="Frame width (default: 640)")
    parser.add_argument("--height", type=int, default=480, help="Frame height (default: 480)")
    parser.add_argument("--fps", type=int, default=20, help="Target stream FPS (default: 20)")
    parser.add_argument(
        "--out-dir",
        type=str,
        default=os.path.expanduser("~/camera_dataset"),
        help="Output dataset directory (default: ~/camera_dataset)",
    )
    args = parser.parse_args()

    streamer = CameraStreamer(
        width=args.width, height=args.height, fps=args.fps, out_dir=args.out_dir
    )
    server = ReusableThreadingHTTPServer(("0.0.0.0", args.http_port), make_handler(streamer))

    def handle_sig(sig, frame):
        print("\nStopping camera stream...")
        streamer.close()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    print(
        f"OV5647 Live Camera Stream running at http://0.0.0.0:{args.http_port} "
        f"({args.width}x{args.height} @ {args.fps} FPS, dataset: {streamer.out_dir})"
    )
    try:
        server.serve_forever()
    finally:
        streamer.close()
        server.server_close()


if __name__ == "__main__":
    main()
