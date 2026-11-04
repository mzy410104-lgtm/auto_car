# Raspberry Pi Software Entry Point

This directory contains the Raspberry Pi 4 onboard software for RPLIDAR A2M8 scan acquisition, motor control, and recorded-scan replay.

## Verified Raspberry Pi Environment (2026-11-02)

- **Hardware**: Raspberry Pi 4 Model B
- **Hostname / User**: `yann`
- **OS**: Debian GNU/Linux 13.4 (trixie), 64-bit (`aarch64`), Kernel `6.12.75+rpt-rpi-v8`
- **Python**: `Python 3.13.5` (virtual environment at `~/auto_car_lidar/venv` with `pyserial` and `rplidar-roboticia`)
- **Power Status**: Verified on external 5V USB-C supply (`vcgencmd get_throttled` reported `throttled=0x0` before, during, and after RPLIDAR A2M8 operation)
- **RPLIDAR A2M8 Interface**: Enumerates via Silicon Labs CP210x UART Bridge (`ID 10c4:ea60`) as `/dev/ttyUSB0` at `115200` bit/s (`8N1`). Reported device info: `model: 40`, `firmware: (1, 28)`, `hardware: 7`, `serialnumber: 83B3ED93C0EA98C6C2E29EF571694061`, health: `('Good', 0)`.
- **Onboard Monocular Camera (Verified 2026-11-03)**: Raspberry Pi Camera Module v1 (Rev 1.3, OmniVision `OV5647` 5 MP sensor) connected to the Raspberry Pi 4 `CAMERA` MIPI CSI-2 port via 15-pin (`1.0 mm` pitch) ribbon cable. Enumerates at `/base/soc/i2c0mux/i2c@1/ov5647@36` via `libcamera v0.6.0+rpt20251202` (`640x480 @ 58.92 fps`, `1296x972 @ 46.34 fps`, `1920x1080 @ 32.81 fps`, `2592x1944 @ 15.63 fps`).

## Files

- [`lidar_acquire.py`](lidar_acquire.py): Connects to RPLIDAR A2M8 over `/dev/ttyUSB0`, starts the motor using A2 PWM packet (`0xA5 0xF0`) and DTR control, records timestamped 360° scans (`timestamp_s,scan_id,quality,angle_deg,distance_mm`) to CSV, prints real-time closest-obstacle distance, and cleanly stops the scan and motor on exit.
- [`lidar_replay.py`](lidar_replay.py): Replays recorded CSV scan datasets, computes scan rate and obstacle range variations, and exports a 2D top-down Cartesian SVG visualization.
- [`lidar_live_web.py`](lidar_live_web.py): Live browser-based radar visualizer serving real-time RPLIDAR A2M8 360° scans over HTTP (`http://<pi-ip>:8080`).
- [`spin_test.py`](spin_test.py): Standalone hardware diagnostic utility for verifying RPLIDAR A2M8 serial response and motor start/stop control.
- [`stm32_comm_test.py`](stm32_comm_test.py): Bidirectional Raspberry Pi ↔ STM32 NUCLEO-F103RB serial diagnostic and USB disconnect/reconnect test script over `/dev/ttyACM0` (`115200 8N1`).
- [`camera_live_web.py`](camera_live_web.py): Live MJPEG camera web streamer (`http://<pi-ip>:8081`) with automatic `rpicam-vid` watchdog recovery, 180° orientation flip, and one-click session-separated dataset frame capture (`manifest.csv`).
- [`vision_manifest.py`](vision_manifest.py): Dataset manifest loader, 14-column schema validator, and strict session-leakage checker (`--self-test`, `--check-files`, `--require-held-out-splits`).
- [`requirements-vision.txt`](requirements-vision.txt): Reproducible Python package specification for the vision dataset and training preparation environment (`Task B4`).
- [`CAMERA_AND_DATASET_RULES.md`](CAMERA_AND_DATASET_RULES.md): Monocular camera technical requirements, verified OV5647 hardware record (`Task B1`), and session-separated region dataset labelling rules (`Task B2`).

## Reproducible Startup & Restart Instructions

### 1. Environment Setup
```bash
mkdir -p ~/auto_car_lidar && cd ~/auto_car_lidar
python3 -m venv venv
source venv/bin/activate
pip install pyserial rplidar-roboticia
```

### 2. Acquire and Save Real Scans (Run 1 & Re-acquisition Run 2)
```bash
# Acquire 15 seconds of scans and automatically stop motor on exit
~/auto_car_lidar/venv/bin/python3 lidar_acquire.py --port /dev/ttyUSB0 --duration 15 --out scan_run1_moved_object.csv

# Re-acquire 10 seconds of scans without unplugging hardware
~/auto_car_lidar/venv/bin/python3 lidar_acquire.py --port /dev/ttyUSB0 --duration 10 --out scan_run2_reacquire.csv

# Emergency / standalone motor stop if needed
~/auto_car_lidar/venv/bin/python3 lidar_acquire.py --port /dev/ttyUSB0 --stop-only
```

### 3. Replay Recorded Scans and Export 2D Top-Down Plot
```bash
~/auto_car_lidar/venv/bin/python3 lidar_replay.py scan_run1_moved_object.csv --svg scan_run1_moved_object.svg
~/auto_car_lidar/venv/bin/python3 lidar_replay.py scan_run2_reacquire.csv --svg scan_run2_reacquire.svg
```

### 4. Onboard Camera Live Stream, Dataset Capture & Manifest Validation (Tasks B1, B2, B4)
```bash
# Verify OV5647 camera detection on Raspberry Pi
rpicam-hello --list-cameras

# Start live MJPEG web streamer and labelled frame recorder on port 8081
/usr/bin/python3 onboard/camera_live_web.py --http-port 8081 --width 640 --height 480 --fps 20 --out-dir ~/camera_dataset

# Run built-in dataset manifest schema & session-leakage validator self-test
python3 onboard/vision_manifest.py --self-test

# Validate an existing dataset manifest and verify on-disk JPEG files
python3 onboard/vision_manifest.py ~/camera_dataset/manifest.csv --check-files
```

## Related Agreements and Test Records

- Pickup request, localization, and obstacle interface (`Task AB`): [`../interfaces/LOCALIZATION_AND_PICKUP_INTERFACE.md`](../interfaces/LOCALIZATION_AND_PICKUP_INTERFACE.md)
- Pi–STM32 communication & motion-feedback agreement (`Task BC`): [`../interfaces/CONTROL_INTERFACE.md`](../interfaces/CONTROL_INTERFACE.md)
- RPLIDAR A2M8 acquisition and replay test record (`Tasks B3 & B5`): [`../tests/records/2026-11-02_pi_rplidar_a2m8_baseline.md`](../tests/records/2026-11-02_pi_rplidar_a2m8_baseline.md)
- Pi–STM32 serial communication and reconnect test record (`Tasks BC & C5`): [`../tests/records/2026-11-02_pi_stm32_usart2_comm.md`](../tests/records/2026-11-02_pi_stm32_usart2_comm.md)
- OV5647 camera verification and vision manifest test record (`Tasks B1, B2, B4, B6`): [`../tests/records/2026-11-03_pi_camera_ov5647_and_vision_manifest.md`](../tests/records/2026-11-03_pi_camera_ov5647_and_vision_manifest.md)
