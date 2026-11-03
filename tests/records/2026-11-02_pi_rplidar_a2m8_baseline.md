# Raspberry Pi 4 and RPLIDAR A2M8 Baseline Acquisition, Stop/Re-acquisition, and Replay Test

- Related task / Issue: Cycle 1 Tasks B3 & B5 / Issue #8 (Raspberry Pi and RPLIDAR A2M8 baseline acquisition and recorded-scan replay)
- Operator and date/time: Member B (Mahdi), 2026-11-02 14:33–14:39 CET
- Actual time spent: 3.0 h (B3 system verification, motor PWM/DTR control debugging, stationary & moved-object scan acquisition) + 1.0 h (B5 recorded-scan replay script & 2D Cartesian SVG projection)
- Test goal and prerequisites:
  1. Verify Raspberry Pi 4 standalone OS environment and power health (`vcgencmd get_throttled`) on external 5V USB-C bench power with vehicle actuators isolated.
  2. Verify RPLIDAR A2M8 USB adapter enumeration, device identification, health status, and clean software motor start/stop control.
  3. Acquire and save a 15-second stationary scan series while moving a test object within the scan plane (`scan_run1_moved_object.csv`), stop the scan and motor completely, and after a 3-second pause re-acquire a 10-second scan series (`scan_run2_reacquire.csv`).
  4. Replay both recorded CSV datasets using `onboard/lidar_replay.py` and generate 2D top-down Cartesian visualizations.
- Equipment, physical wiring and supply source:
  - Raspberry Pi 4 Model B powered via external 5V USB-C supply (vehicle propulsion battery and LM2596S buck converter disconnected).
  - RPLIDAR A2M8 connected via its SLAMTEC CP210x USB adapter board to a Raspberry Pi 4 USB 2.0 port (`Bus 001 Device 008: ID 10c4:ea60 Silicon Labs CP210x UART Bridge`, enumerated as `/dev/ttyUSB0`). No auxiliary 5V barrel plug was required once CP210x DTR + A2M8 `SET_MOTOR_PWM` (`0xA5 0xF0`, PWM=660) commands were sent.
- Software/firmware commits and actual configuration:
  - Raspberry Pi OS: `Debian GNU/Linux 13.4 (trixie)`, Kernel `6.12.75+rpt-rpi-v8 aarch64`, `Python 3.13.5`.
  - Virtual environment: `/home/yann/auto_car_lidar/venv` with `pyserial` and `rplidar-roboticia`.
  - RPLIDAR A2M8 hardware/firmware reported via serial protocol: `{'model': 40, 'firmware': (1, 28), 'hardware': 7, 'serialnumber': '83B3ED93C0EA98C6C2E29EF571694061'}`, health: `('Good', 0)`.
  - Acquisition script: `onboard/lidar_acquire.py` (`115200` bit/s, `8N1`, PWM=660).
  - Replay script: `onboard/lidar_replay.py`.
- Instruments and measurement points:
  - Raspberry Pi internal PMIC undervoltage monitor via `vcgencmd get_throttled` (read `throttled=0x0` before, during, and after both scan runs).
  - RPLIDAR A2M8 range measurements across full 360° scan plane with moved obstacle in front sector (`~25°–48°`).
- Procedure:
  1. Boot Raspberry Pi 4 on external USB-C power, inspect existing environment (`/home/yann`), and verify `throttled=0x0`.
  2. Connect RPLIDAR A2M8 USB adapter and verify `/dev/ttyUSB0` enumeration and `dialout` group membership.
  3. Query device info and health; verify motor spin-up using `SET_MOTOR_PWM` (`0xA5 0xF0`, PWM=660) and clean motor stop (`0xA5 0x25` followed by 100 ms delay and PWM=0).
  4. Execute Run 1 (`15.0 s`) via `lidar_acquire.py --duration 15 --out ~/scan_run1_moved_object.csv` while moving a test obstacle closer and further in the scan plane.
  5. Verify automatic motor stop, pause 3 seconds, and execute Run 2 (`10.0 s`) via `lidar_acquire.py --duration 10 --out ~/scan_run2_reacquire.csv`.
  6. Compute SHA-256 checksums, copy raw datasets to local `data/raw/`, and run `lidar_replay.py` on both the Raspberry Pi and development host.
- Expected behavior and its basis:
  - RPLIDAR A2M8 rotates smoothly at ~10 Hz (typical specification range 5–15 Hz), streams valid 360° range points (`0.15–12 m`), reflects moved obstacle distance changes across consecutive scans, stops spinning when commanded, and restarts cleanly on the subsequent run without USB replugging.
- Original readings / logs / photographs / video index:
  - Raw dataset 1: `data/raw/scan_run1_moved_object.csv` (size: `331,158` bytes / `323 KB`, `9,160` lines, SHA-256: `a6fae7287430f6a7e009c89db5023db3d16ab2bfd9fea6040488c94b854de468`)
  - Raw dataset 2: `data/raw/scan_run2_reacquire.csv` (size: `203,407` bytes / `199 KB`, `5,714` lines, SHA-256: `842fbe43dbdddd750d46f04def533733c94b1e9afe513ee5d0ae1b8a6c3c2012`)
  - Replay SVG plots: `data/raw/scan_run1_moved_object.svg` and `data/raw/scan_run2_reacquire.svg`
- Actual results and anomalies:
  - **Run 1 (`scan_run1_moved_object.csv`)**: Recorded `154` complete 360° scans (`9,159` valid points, mean `59.47` points/scan) over `13.938 s` active scan window (`10.98 Hz` effective scan rate). Global distance range: `109.8 mm` to `6315.8 mm`. Closest obstacle distance varied by `528.7 mm` (`638.5 mm` down to `109.8 mm`, then moved back to `155.8 mm` and `125.0 mm` at `~29°–48°`), confirming real-time response to the moved object.
  - **Stop and Re-acquire (`scan_run2_reacquire.csv`)**: Motor stopped completely between runs and restarted cleanly after the 3-second pause. Recorded `98` complete 360° scans (`5,713` valid points, mean `58.30` points/scan) over `8.841 s` active scan window (`10.97 Hz` effective scan rate).
  - **Initial anomaly resolved**: `rplidar-roboticia` default `start_motor()`/`stop_motor()` methods only toggle DTR without sending the A2M8 `SET_MOTOR_PWM` (`0xA5 0xF0`) command or waiting after `STOP` (`0xA5 0x25`), which initially prevented motor stop/start. Resolved in `onboard/lidar_acquire.py` by sending `0xA5 0xF0` PWM packets with a 100 ms post-STOP settle delay.
  - **Camera check (Task B1 observation)**: Running `rpicam-hello --list-cameras` on the Raspberry Pi returned `No cameras available!`, confirming no CSI camera is currently attached to the Pi.
- Conclusion and applicable conditions:
  - **Pass** (under bench USB-C supply with vehicle stationary). Raspberry Pi 4 and RPLIDAR A2M8 acquisition, moved-object detection, clean motor stop, re-acquisition, and recorded-scan replay are verified and reproducible.
- Unresolved items, next step and owner:
  - Onboard vehicle buck-converter (`LM2596S`) load test with Pi + RPLIDAR remains pending joint power verification (Steps 2 & 4).
  - Next steps for Member B: complete Task B1/B2/B4 documentation (monocular camera requirements, region-recognition dataset rules, and AI training manifest preparation) and joint AB/BC interface notes.
- Reviewer: Pending
