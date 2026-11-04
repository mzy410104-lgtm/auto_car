# Raspberry Pi 4 + Camera Module Rev 1.3 (OV5647) Verification & Vision Manifest Validation Test

- Related task / Issue: Cycle 1 Tasks B1, B2, B4 & B6 / Issue #8 (Monocular camera verification, dataset labelling rules, AI environment & session-separated manifest validation)
- Operator and date/time: Member B (Mahdi), 2026-11-03 18:50–20:59 CET (hardware test on Raspberry Pi 4) & 2026-11-04 13:36 CET (manifest validator self-test)
- Actual time spent: 1.5 h (B1 camera connection, CSI ribbon orientation & `rpicam`/`libcamera` verification) + 2.0 h (B2 dataset protocol & session-separation rules) + 3.0 h (B4 live MJPEG web capture tool `camera_live_web.py` & manifest validator `vision_manifest.py`) + 0.5 h (B6 test record & index updates)
- Test goal and prerequisites:
  1. Connect the Raspberry Pi Camera Module v1 (Rev 1.3, OmniVision OV5647) to the Raspberry Pi 4 Model B `CAMERA` MIPI CSI-2 interface and verify sensor detection via `rpicam-hello --list-cameras`.
  2. Verify still JPEG capture (`1296×972`) and continuous live MJPEG streaming (`640×480 @ 20 FPS`) while the RPLIDAR A2M8 is connected on `/dev/ttyUSB0` and check power integrity via `vcgencmd get_throttled`.
  3. Verify automatic recovery from CSI ribbon flex / `V4L2` frame timeout using a self-healing `rpicam-vid` subprocess watchdog in `onboard/camera_live_web.py`.
  4. Verify dataset manifest schema validation and strict session-leakage blocking using `onboard/vision_manifest.py --self-test`.
- Equipment, physical wiring and supply source:
  - Raspberry Pi 4 Model B (`yann`, powered via external 5V USB-C supply; vehicle propulsion battery and LM2596S buck converter isolated).
  - Raspberry Pi Camera Module v1 (Rev 1.3, 5 MP OmniVision `OV5647` sensor) connected to the Raspberry Pi 4 `CAMERA` MIPI CSI-2 slot (between the 3.5 mm audio jack and micro-HDMI ports) using a standard 15-pin-to-15-pin (`16 mm` wide, `1.0 mm` pitch) flat ribbon cable (silver contacts facing the PCB on the camera end and facing the micro-HDMI ports on the Pi 4 end).
  - RPLIDAR A2M8 connected simultaneously on USB 2.0 (`/dev/ttyUSB0`, `ID 10c4:ea60`).
- Software/firmware commits and actual configuration:
  - Raspberry Pi OS: `Debian GNU/Linux 13.4 (trixie)`, Kernel `6.12.75+rpt-rpi-v8 aarch64`, `Python 3.13.5`.
  - Camera stack: `libcamera v0.6.0+rpt20251202`, `rpicam-apps` (`rpicam-hello`, `rpicam-still`, `rpicam-vid`), `python3-picamera2`, `python3-pil`, tuning file `/usr/share/libcamera/ipa/rpi/vc4/ov5647.json`.
  - Onboard scripts: `onboard/camera_live_web.py`, `onboard/vision_manifest.py`, `onboard/requirements-vision.txt`, and `onboard/CAMERA_AND_DATASET_RULES.md`.
- Instruments and measurement points:
  - Raspberry Pi PMIC undervoltage monitor via `vcgencmd get_throttled`.
  - Kernel CSI/Unicam device registration (`dmesg`, `/dev/media0`, `/dev/media2`, `/dev/video0`).
  - Live HTTP `/api/status` frame rate measurement (`measured_fps`) on port `8081`.
- Procedure:
  1. With Raspberry Pi 4 powered off, attach the 15-pin flat ribbon cable between the Camera Module Rev 1.3 and the Pi 4 `CAMERA` CSI-2 port, then boot the Pi on external USB-C power.
  2. Run `vcgencmd get_throttled`, `lsusb`, and `rpicam-hello --list-cameras` to verify camera enumeration and power health alongside the connected RPLIDAR A2M8.
  3. Capture a reference still image using `rpicam-still -n --width 1296 --height 972 -t 500 -o ~/camera_test_ov5647.jpg` and inspect the output file metadata.
  4. Launch `onboard/camera_live_web.py --http-port 8081 --width 640 --height 480 --fps 20` and query `http://172.20.10.2:8081/api/status`.
  5. Observe behavior when the unmounted ribbon cable is moved, then update `camera_live_web.py` to use an isolated `rpicam-vid` MJPEG subprocess with a `2.2 s` watchdog and 180° hardware rotation toggle (`--rotation 180`).
  6. Run `python3 onboard/vision_manifest.py --self-test` to verify the 14-column manifest schema, image dimension check, and deterministic rejection of cross-split session leakage.
- Expected behavior and its basis:
  - `rpicam-hello --list-cameras` enumerates `ov5647` at `/base/soc/i2c0mux/i2c@1/ov5647@36` with four CSI2P modes (`640x480`, `1296x972`, `1920x1080`, `2592x1944`).
  - Still capture produces a valid `1296×972` JPEG, live streaming sustains `~20 FPS` at `640×480` with `throttled=0x0`, and `vision_manifest.py --self-test` passes clean manifests while blocking session leakage.
- Original readings / logs / photographs / video index:
  - `rpicam-hello --list-cameras` output on `yann`:
    ```text
    Available cameras
    -----------------
    0 : ov5647 [2592x1944 10-bit GBRG] (/base/soc/i2c0mux/i2c@1/ov5647@36)
        Modes: 'SGBRG10_CSI2P' : 640x480 [58.92 fps - (16, 0)/2560x1920 crop]
                                 1296x972 [46.34 fps - (0, 0)/2592x1944 crop]
                                 1920x1080 [32.81 fps - (348, 434)/1928x1080 crop]
                                 2592x1944 [15.63 fps - (0, 0)/2592x1944 crop]
    ```
  - Still capture log (`rpicam-still`):
    - Saved `/home/yann/camera_test_ov5647.jpg` (`186 KB`, `JPEG image data, Exif standard, baseline, precision 8, 1296x972, components 3`).
  - Live stream `/api/status` response (`http://172.20.10.2:8081/api/status`):
    - `{"sensor": "ov5647", "width": 640, "height": 480, "fps": 19.974087875461173, "saved_count": 0, "flip_180": false, "out_dir": "/home/yann/camera_dataset"}`
  - Manifest validator self-test output (`python3 onboard/vision_manifest.py --self-test`):
    ```text
    Running onboard/vision_manifest.py self-test (Task B4)...
      [PASS 1/2] Valid session-separated manifest passed (rows=3, splits={'test': 1, 'train': 1, 'val': 1}, sessions={'20261103_s01_train': 'train', '20261103_s02_val': 'val', '20261103_s03_test': 'test'})
      [PASS 2/2] Cross-split session leakage deterministically rejected: Session leakage detected: session_id '20261103_s01_train' spans multiple splits ['train', 'val']
    SELF-TEST RESULT: PASS (schema + image check + session-separation enforcement verified).
    ```
- Actual results and anomalies:
  - **Sensor Enumeration & Power**: `ov5647` was detected immediately on `/base/soc/i2c0mux/i2c@1/ov5647@36` and registered to Unicam `/dev/media0` and ISP `/dev/media2`. `vcgencmd get_throttled` reported `throttled=0x0` before, during, and after still capture and 20 FPS streaming with the RPLIDAR A2M8 connected on `/dev/ttyUSB0`.
  - **CSI Ribbon Flex Timeout & Watchdog Mitigation**: After ~2.5 minutes of initial streaming while the camera board was unmounted on a loose ribbon cable, moving the cable caused a transient CSI clock/data interruption logged as:
    `WARN V4L2 v4l2_videodevice.cpp:2100 /dev/video0[12:cap]: Dequeue timer of 1000000.00us has expired!` / `ERROR RPI pipeline_base.cpp:1350 Camera frontend has timed out!`.
    Because an in-process `Picamera2` instance cannot cleanly re-initialize `/dev/video0` after a Unicam timeout without resetting the process, `onboard/camera_live_web.py` was refactored to read MJPEG frames from an isolated `rpicam-vid` subprocess monitored by a `2.2 s` watchdog thread (`_watchdog_loop`) that automatically kills and respawns `rpicam-vid` on timeout or 180° flip toggle.
  - **Dataset Manifest & Session-Leakage Verification**: Both `camera_live_web.py` (at capture time) and `vision_manifest.py` (offline validation) deterministically block any `session_id` from spanning multiple dataset splits (`train`, `val`, `test`).
- Conclusion and applicable conditions:
  - **Pass** for Cycle 1 Tasks B1, B2, B4, and B6 (camera availability/requirements recorded, OV5647 CSI capture and live streaming verified on Raspberry Pi 4 bench supply, dataset labelling protocol defined, and session-separated manifest loader/validator verified). This does **not** claim a trained visual localization model or completed room dataset collection (which belong to Cycles 2–3).
- Unresolved items, next step and owner:
  - **Cycle 2 Mechanical Mounting & Strain Relief (Member B)**: Rigidly mount the OV5647 camera module on the TT-02 upper platform with ribbon cable strain relief (clear of the RPLIDAR A2M8 360° scan plane and front SHARP sensors).
  - **Cycle 2 Room Dataset & Lidar Map Collection (Member B)**: Collect multi-session labelled images (`train`, `val`, `test` in separate sessions) in the real test room alongside the first complete RPLIDAR A2M8 room map.
  - **Onboard Buck Converter (`LM2596S`) Load Test (Members A/B/C)**: Verify 5V voltage stability under combined Pi 4 + RPLIDAR A2M8 + OV5647 camera load once the 7.2V NiMH battery condition (`Task C1`) is resolved.
- Reviewer: Pending
