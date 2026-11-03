# Raspberry Pi Software Entry Point

This directory contains the Raspberry Pi 4 onboard software for RPLIDAR A2M8 scan acquisition, motor control, and recorded-scan replay.

## Verified Raspberry Pi Environment (2026-11-02)

- **Hardware**: Raspberry Pi 4 Model B
- **Hostname / User**: `yann`
- **OS**: Debian GNU/Linux 13.4 (trixie), 64-bit (`aarch64`), Kernel `6.12.75+rpt-rpi-v8`
- **Python**: `Python 3.13.5` (virtual environment at `~/auto_car_lidar/venv` with `pyserial` and `rplidar-roboticia`)
- **Power Status**: Verified on external 5V USB-C supply (`vcgencmd get_throttled` reported `throttled=0x0` before, during, and after RPLIDAR A2M8 operation)
- **RPLIDAR A2M8 Interface**: Enumerates via Silicon Labs CP210x UART Bridge (`ID 10c4:ea60`) as `/dev/ttyUSB0` at `115200` bit/s (`8N1`). Reported device info: `model: 40`, `firmware: (1, 28)`, `hardware: 7`, `serialnumber: 83B3ED93C0EA98C6C2E29EF571694061`, health: `('Good', 0)`.

## Files

- [`lidar_acquire.py`](lidar_acquire.py): Connects to RPLIDAR A2M8 over `/dev/ttyUSB0`, starts the motor using A2 PWM packet (`0xA5 0xF0`) and DTR control, records timestamped 360° scans (`timestamp_s,scan_id,quality,angle_deg,distance_mm`) to CSV, prints real-time closest-obstacle distance, and cleanly stops the scan and motor on exit.
- [`lidar_replay.py`](lidar_replay.py): Replays recorded CSV scan datasets, computes scan rate and obstacle range variations, and exports a 2D top-down Cartesian SVG visualization.
- [`lidar_live_web.py`](lidar_live_web.py): Live browser-based radar visualizer serving real-time RPLIDAR A2M8 360° scans over HTTP (`http://<pi-ip>:8080`).
- [`spin_test.py`](spin_test.py): Standalone hardware diagnostic utility for verifying RPLIDAR A2M8 serial response and motor start/stop control.
- [`stm32_comm_test.py`](stm32_comm_test.py): Bidirectional Raspberry Pi ↔ STM32 NUCLEO-F103RB serial diagnostic and USB disconnect/reconnect test script over `/dev/ttyACM0` (`115200 8N1`).

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

## Related Agreements and Test Records

- Pi–STM32 communication agreement: [`../interfaces/CONTROL_INTERFACE.md`](../interfaces/CONTROL_INTERFACE.md)
- RPLIDAR A2M8 acquisition and replay test record: [`../tests/records/2026-11-02_pi_rplidar_a2m8_baseline.md`](../tests/records/2026-11-02_pi_rplidar_a2m8_baseline.md)
- Pi–STM32 serial communication and reconnect test record: [`../tests/records/2026-11-02_pi_stm32_usart2_comm.md`](../tests/records/2026-11-02_pi_stm32_usart2_comm.md)
