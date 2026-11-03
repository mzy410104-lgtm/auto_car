#!/usr/bin/env python3
"""
Real-time 360-degree RPLIDAR A2M8 Web Radar Visualizer for Raspberry Pi 4.
Streams live scans at ~10 Hz over HTTP to an interactive HTML5 Canvas radar dashboard.
"""
import argparse
import json
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from rplidar import RPLidar

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RPLIDAR A2M8 — Live 360° Radar</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0b0f19;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100vh;
    overflow: hidden;
  }
  header {
    width: 100%;
    padding: 12px 24px;
    background: #111827;
    border-bottom: 1px solid #1f2937;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .title { font-size: 18px; font-weight: 700; color: #38bdf8; }
  .stats { display: flex; gap: 20px; font-size: 14px; }
  .stat-box {
    background: #1e293b;
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid #334155;
  }
  .stat-val { font-weight: 700; color: #10b981; }
  .closest-val { font-weight: 700; color: #f43f5e; }
  .controls { display: flex; gap: 10px; align-items: center; }
  button, select {
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #475569;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
  }
  button:hover { background: #334155; }
  button.danger { background: #dc2626; border-color: #ef4444; }
  button.danger:hover { background: #b91c1c; }
  button.success { background: #059669; border-color: #10b981; }
  button.success:hover { background: #047857; }
  main {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    padding: 10px;
  }
  canvas {
    background: radial-gradient(circle, #0f172a 0%, #090d16 100%);
    border-radius: 50%;
    border: 2px solid #1e293b;
    box-shadow: 0 0 40px rgba(56, 189, 248, 0.08);
  }
</style>
</head>
<body>
<header>
  <div class="title">RPLIDAR A2M8 Live 360° Radar</div>
  <div class="stats">
    <div class="stat-box">Scan: <span id="scanId" class="stat-val">0</span></div>
    <div class="stat-box">Rate: <span id="rateHz" class="stat-val">0.0</span> Hz</div>
    <div class="stat-box">Points: <span id="ptCount" class="stat-val">0</span></div>
    <div class="stat-box">Closest: <span id="closest" class="closest-val">-- cm</span></div>
  </div>
  <div class="controls">
    <label for="maxRange">Max Range:</label>
    <select id="maxRange">
      <option value="1500">1.5 m</option>
      <option value="3000" selected>3.0 m</option>
      <option value="6000">6.0 m</option>
      <option value="12000">12.0 m</option>
    </select>
    <button class="success" onclick="controlLidar('start')">Start LiDAR</button>
    <button class="danger" onclick="controlLidar('stop')">Stop LiDAR</button>
  </div>
</header>
<main>
  <canvas id="radar" width="760" height="760"></canvas>
</main>
<script>
const canvas = document.getElementById('radar');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;
const CX = W / 2;
const CY = H / 2;

function resizeCanvas() {
  const size = Math.min(window.innerWidth - 40, window.innerHeight - 90);
  canvas.style.width = size + 'px';
  canvas.style.height = size + 'px';
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

async function controlLidar(action) {
  await fetch('/api/' + action, { method: 'POST' });
}

function drawRadar(data) {
  const maxRangeMm = parseFloat(document.getElementById('maxRange').value);
  const scale = (CX - 30) / maxRangeMm;

  ctx.clearRect(0, 0, W, H);

  // Range rings
  const stepMm = maxRangeMm <= 1500 ? 250 : (maxRangeMm <= 3000 ? 500 : (maxRangeMm <= 6000 ? 1000 : 2000));
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  ctx.fillStyle = '#64748b';
  ctx.font = '12px monospace';

  for (let r = stepMm; r <= maxRangeMm; r += stepMm) {
    const px = r * scale;
    ctx.beginPath();
    ctx.arc(CX, CY, px, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillText((r / 1000).toFixed(2).replace(/\\.00$/, '') + 'm', CX + 6, CY - px + 14);
  }

  // Crosshair axes & 30-deg spokes
  for (let deg = 0; deg < 360; deg += 30) {
    const rad = (deg - 90) * Math.PI / 180;
    const x2 = CX + Math.cos(rad) * (CX - 30);
    const y2 = CY + Math.sin(rad) * (CY - 30);
    ctx.beginPath();
    ctx.moveTo(CX, CY);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = deg % 90 === 0 ? '#334155' : '#162032';
    ctx.stroke();

    const lx = CX + Math.cos(rad) * (CX - 15);
    const ly = CY + Math.sin(rad) * (CY - 15);
    ctx.fillStyle = '#94a3b8';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(deg + '°', lx, ly);
  }
  ctx.textAlign = 'start';

  // Plot scan points (0 deg = UP, clockwise)
  const pts = data.points || [];
  for (let i = 0; i < pts.length; i++) {
    const ang = pts[i][0];
    const dist = pts[i][1];
    if (dist <= 0 || dist > maxRangeMm) continue;
    const rad = (ang - 90) * Math.PI / 180;
    const x = CX + Math.cos(rad) * dist * scale;
    const y = CY + Math.sin(rad) * dist * scale;

    // Color by proximity
    if (dist < 300) {
      ctx.fillStyle = '#f43f5e';
    } else if (dist < 800) {
      ctx.fillStyle = '#f59e0b';
    } else {
      ctx.fillStyle = '#38bdf8';
    }
    ctx.beginPath();
    ctx.arc(x, y, 3.2, 0, Math.PI * 2);
    ctx.fill();
  }

  // Highlight closest obstacle
  if (data.min_dist_mm && data.min_dist_mm <= maxRangeMm) {
    const rad = (data.min_angle_deg - 90) * Math.PI / 180;
    const mx = CX + Math.cos(rad) * data.min_dist_mm * scale;
    const my = CY + Math.sin(rad) * data.min_dist_mm * scale;

    ctx.strokeStyle = '#f43f5e';
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(CX, CY);
    ctx.lineTo(mx, my);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(mx, my, 8, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Center LiDAR origin
  ctx.fillStyle = '#10b981';
  ctx.beginPath();
  ctx.arc(CX, CY, 6, 0, Math.PI * 2);
  ctx.fill();
}

async function pollScan() {
  try {
    const res = await fetch('/api/scan');
    const data = await res.json();
    document.getElementById('scanId').textContent = data.scan_id;
    document.getElementById('rateHz').textContent = data.rate_hz.toFixed(1);
    document.getElementById('ptCount').textContent = data.points.length;
    if (data.min_dist_mm) {
      document.getElementById('closest').textContent =
        (data.min_dist_mm / 10).toFixed(1) + ' cm @ ' + data.min_angle_deg.toFixed(0) + '°';
    } else {
      document.getElementById('closest').textContent = data.running ? '-- cm' : 'STOPPED';
    }
    drawRadar(data);
  } catch (e) {}
  setTimeout(pollScan, 75);
}
pollScan();
</script>
</body>
</html>
"""


def pwm_pkt(pwm: int) -> bytes:
    payload = struct.pack("<H", pwm)
    pkt = bytearray([0xA5, 0xF0, 0x02]) + payload
    cs = 0
    for b in pkt:
        cs ^= b
    pkt.append(cs)
    return bytes(pkt)


class LidarWorker:
    def __init__(self, port: str, baud: int = 115200, pwm: int = 660):
        self.port = port
        self.baud = baud
        self.pwm = pwm
        self.lock = threading.Lock()
        self.running = True
        self.alive = True
        self.latest_scan = {
            "scan_id": 0,
            "rate_hz": 0.0,
            "points": [],
            "min_dist_mm": None,
            "min_angle_deg": None,
            "running": True,
        }
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _start_motor(self, lidar: RPLidar):
        lidar._serial.dtr = False
        time.sleep(0.05)
        lidar._serial.write(pwm_pkt(self.pwm))
        lidar.motor_running = True

    def _stop_motor(self, lidar: RPLidar):
        try:
            lidar._serial.write(b"\xA5\x25")
            time.sleep(0.1)
            lidar._serial.dtr = True
            lidar._serial.write(pwm_pkt(0))
            time.sleep(0.1)
            lidar._serial.dtr = False
            lidar._serial.write(pwm_pkt(0))
            time.sleep(0.1)
            lidar.motor_running = False
        except Exception:
            pass

    def _loop(self):
        lidar = None
        while self.alive:
            if not self.running:
                if lidar is not None:
                    self._stop_motor(lidar)
                    try:
                        lidar._serial.close()
                    except Exception:
                        pass
                    lidar = None
                with self.lock:
                    self.latest_scan["running"] = False
                time.sleep(0.2)
                continue

            try:
                lidar = RPLidar(self.port, baudrate=self.baud)
                lidar.start_motor = lambda: self._start_motor(lidar)
                lidar.stop_motor = lambda: self._stop_motor(lidar)
                self._start_motor(lidar)
                time.sleep(1.5)
                lidar.clean_input()

                scan_id = 0
                last_time = time.time()
                rate_hz = 0.0

                for scan in lidar.iter_scans(max_buf_meas=3000):
                    if not self.running or not self.alive:
                        break
                    now = time.time()
                    dt = now - last_time
                    last_time = now
                    if dt > 0:
                        rate_hz = 0.8 * rate_hz + 0.2 * (1.0 / dt) if scan_id > 0 else (1.0 / dt)

                    pts = []
                    min_d = None
                    min_a = None
                    for q, ang, dist in scan:
                        if dist > 0:
                            pts.append((round(ang, 1), round(dist, 1)))
                            if min_d is None or dist < min_d:
                                min_d = round(dist, 1)
                                min_a = round(ang, 1)

                    scan_id += 1
                    with self.lock:
                        self.latest_scan = {
                            "scan_id": scan_id,
                            "rate_hz": round(rate_hz, 2),
                            "points": pts,
                            "min_dist_mm": min_d,
                            "min_angle_deg": min_a,
                            "running": True,
                        }
            except Exception as e:
                print(f"LiDAR worker warning: {e}")
                time.sleep(1.0)
            finally:
                if lidar is not None:
                    self._stop_motor(lidar)
                    try:
                        lidar._serial.close()
                    except Exception:
                        pass
                    lidar = None

    def stop_all(self):
        self.running = False
        self.alive = False


def main():
    parser = argparse.ArgumentParser(description="Live Web Radar for RPLIDAR A2M8")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port")
    parser.add_argument("--http-port", type=int, default=8080, help="HTTP server port")
    args = parser.parse_args()

    worker = LidarWorker(args.port)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *a):
            pass

        def do_GET(self):
            if self.path == "/api/scan":
                with worker.lock:
                    payload = json.dumps(worker.latest_scan).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
            else:
                payload = HTML_PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(payload)

        def do_POST(self):
            if self.path == "/api/stop":
                worker.running = False
            elif self.path == "/api/start":
                worker.running = True
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

    HTTPServer.allow_reuse_address = True
    server = HTTPServer(("0.0.0.0", args.http_port), Handler)
    print(f"Live Radar running at http://0.0.0.0:{args.http_port} (Press Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down Live Radar and stopping LiDAR motor...")
        worker.stop_all()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
