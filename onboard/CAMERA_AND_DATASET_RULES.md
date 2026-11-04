# Onboard Monocular Camera Requirements & Region Dataset Protocol (Tasks B1 & B2)

Revision date: 2026-11-04  
Related tasks: Cycle 1 Tasks `B1` & `B2` ([CURRENT_WEEK_TASKS_EN.md](../CURRENT_WEEK_TASKS_EN.md), GitHub Issue `#8`)  
Owner: Member B

---

## 1. Monocular Camera Requirements and Availability Record (`Task B1`)

### 1.1 Architectural Role of the Onboard Camera
Under the project architecture revised on 2026-09-22 ([TAXI_TT02_ARCHITECTURE_NOTES_EN.md](../TAXI_TT02_ARCHITECTURE_NOTES_EN.md)):
1. **Visual Map-Region / Reference-Place Recognition Only**: The onboard monocular camera observes the indoor environment and outputs a discrete region or reference-place identifier (`region_id`) with an associated confidence score (`visual_confidence`).
2. **Not a Standalone Metric Pose Sensor**: A single image classification does **not** provide metric planar coordinates `(x, y, yaw)`. Continuous planar pose is maintained by 2D RPLIDAR A2M8 scan-to-map matching combined with wheel-speed magnitude (`OPB815WZ`) and IMU (`SEN0253` / `BNO055`) motion feedback.
3. **Validated Localization Usage**: Visual region predictions may only be used for global pose initialization, consistency checking, or kid-napped robot recovery after passing held-out session validation (`Task B2` / Cycle 3).
4. **Separation from Passenger QR Scanning**: Fixed-pickup QR codes are scanned by the passenger's smartphone (`Member A` workflow). The vehicle's onboard camera is not required to read passenger pickup QR codes during driving.

### 1.2 Technical Requirements for the Onboard Monocular Camera
| Requirement category | Target specification | Engineering rationale |
|---|---|---|
| **Physical & electrical interface** | Raspberry Pi 4 Model B MIPI CSI-2 (`CAMERA` 15-pin, 1.0 mm pitch ribbon) or USB 2.0 UVC | Must integrate natively with Debian 13 (`trixie`) `libcamera` / `rpicam-apps` / `picamera2` without kernel recompilation and without exhausting USB bus bandwidth shared with RPLIDAR A2M8 (`/dev/ttyUSB0`) and STM32 (`/dev/ttyACM0`). |
| **Power budget** | Combined Pi 4 + RPLIDAR A2M8 + camera operation must maintain `vcgencmd get_throttled` at `0x0` | Prevents Pi 4 PMIC undervoltage throttling (`0x50000` / `0x50005`) during continuous acquisition. |
| **Optical focus & shutter** | Fixed-focus lens focused for indoor distances (`~0.5 m` to `5.0 m`); automatic exposure/gain (`AEC/AGC`) and auto white balance (`AWB`) supported by Pi ISP | Avoids autofocus hunting caused by chassis vibration; handles indoor artificial and window lighting transitions. |
| **Resolution & frame rate** | Minimum `640×480` at `15–20 FPS` for live streaming/inference and up to `1296×972` (2×2 binned full FOV) for reference stills | `640×480` or `1296×972` preserves the full sensor field of view without cropping while keeping CPU/ISP load low on Raspberry Pi 4. |
| **Mechanical mounting** | Rigid forward-facing mount on the TT-02 upper platform | Must have a repeatable camera-to-`base_link` orientation and must **not** occlude the 360° horizontal scan plane of the RPLIDAR A2M8 or the two front SHARP `GP2Y0A21YK0F` close-range sensors. |

### 1.3 Verified Availability & Bench Test Timeline
1. **2026-11-02 (Initial Baseline Check — No Camera Attached)**:
   - During the RPLIDAR A2M8 baseline test ([`2026-11-02_pi_rplidar_a2m8_baseline.md`](../tests/records/2026-11-02_pi_rplidar_a2m8_baseline.md)), running `rpicam-hello --list-cameras` on the Raspberry Pi 4 (`yann`) returned `No cameras available!`. No CSI or USB camera was attached at that time.
2. **2026-11-03 (Hardware Provided & Verified on Raspberry Pi 4 Bench)**:
   - Member B connected a **Raspberry Pi Camera Module v1 (Rev 1.3)** equipped with the **OmniVision OV5647** 5 MP CMOS sensor to the Raspberry Pi 4 `CAMERA` MIPI CSI-2 connector using a standard 15-pin-to-15-pin (`16 mm` wide, `1.0 mm` pitch) flat ribbon cable.
   - `rpicam-hello --list-cameras` confirmed hardware enumeration on Unicam `/dev/media0` and ISP `/dev/media2`:
     ```text
     0 : ov5647 [2592x1944 10-bit GBRG] (/base/soc/i2c0mux/i2c@1/ov5647@36)
         Modes: 'SGBRG10_CSI2P' : 640x480 [58.92 fps - (16, 0)/2560x1920 crop]
                                  1296x972 [46.34 fps - (0, 0)/2592x1944 crop]
                                  1920x1080 [32.81 fps - (348, 434)/1928x1080 crop]
                                  2592x1944 [15.63 fps - (0, 0)/2592x1944 crop]
     ```
   - Verified still capture (`1296×972` JPEG, `186 KB`) and continuous MJPEG web streaming (`640×480 @ 20.0 FPS`) via [`onboard/camera_live_web.py`](camera_live_web.py) while the RPLIDAR A2M8 was connected on `/dev/ttyUSB0` and `vcgencmd get_throttled` reported `throttled=0x0` ([`2026-11-03_pi_camera_ov5647_and_vision_manifest.md`](../tests/records/2026-11-03_pi_camera_ov5647_and_vision_manifest.md)).

### 1.4 Explicitly Unresolved Camera Items (Deferred to Cycle 2)
- **Rigid Chassis Mounting**: The OV5647 board is currently connected via its flexible 15-pin ribbon on the bench and has not yet been mechanically fixed to the TT-02 upper platform.
- **Ribbon Strain Relief**: Moving an unmounted CSI ribbon during live capture triggered a temporary `V4L2 dequeue timer expired` / `Camera frontend has timed out` event on `/dev/video0`. While [`camera_live_web.py`](camera_live_web.py) now includes a 2.2 s frame watchdog that automatically restarts the `rpicam-vid` subprocess, physical strain relief and a rigid camera bracket are required before vehicle movement tests.
- **Camera Intrinsics & Extrinsics**: Horizontal/vertical field of view on the selected `640×480` / `1296×972` modes and the exact mounting pose relative to `base_link` remain to be measured after mounting on the chassis.

---

## 2. Image Acquisition, Labelling, and Session-Separated Dataset Rules (`Task B2`)

### 2.1 Region Partitioning Without Invented Coordinates
- The indoor test room will be partitioned into discrete topological **map regions** (`REGION_01`, `REGION_02`, ..., `REGION_NN`).
- **No Invented Metric Coordinates in Cycle 1**: In accordance with Cycle 1 rules, no numeric `(x, y)` bounding polygons are assigned to `REGION_01..NN` until the real RPLIDAR A2M8 room map is produced in Cycle 2.
- Once the Cycle 2 lidar map is built, each `region_id` will be associated with a bounded polygon `(x_min, x_max, y_min, y_max)` and allowed heading range in the `map` frame.

### 2.2 Dataset Directory Layout & Manifest Schema
All captured images and metadata are stored under a dataset root directory (default `~/camera_dataset` on the Raspberry Pi):
```text
camera_dataset/
├── manifest.csv
└── images/
    ├── <session_id_1>/
    │   ├── img_<epoch_ms>_0001.jpg
    │   └── ...
    └── <session_id_2>/
        └── ...
```

Every row in `manifest.csv` must conform to the 14-column schema enforced by [`camera_live_web.py`](camera_live_web.py) and validated by [`vision_manifest.py`](vision_manifest.py):

| Column | Type | Allowed values / format | Description |
|---|---|---|---|
| `image_id` | string | `img_<epoch_ms>_<seq>` | Unique frame identifier |
| `relative_path` | string | `images/<session_id>/<image_id>.jpg` | Path relative to dataset root directory |
| `timestamp_s` | float | Unix epoch seconds (`0.001 s` resolution) | Acquisition timestamp for time-alignment with lidar/STM32 logs |
| `iso_utc` | string | `YYYY-MM-DDTHH:MM:SSZ` | Human-readable UTC timestamp |
| `session_id` | string | Non-empty slug (e.g. `20261110_s01_train`) | Identifier of the contiguous physical recording run |
| `region_id` | string | `REGION_01` .. `REGION_99` | Target map region or reference place label |
| `heading_sector` | enum | `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW` | Approximate vehicle heading sector in the room (45° bins) |
| `viewpoint_offset` | enum | `center`, `left_offset`, `right_offset`, `angled_left`, `angled_right` | Lateral/angular variation relative to the nominal path inside the region |
| `lighting_condition` | enum | `artificial_indoor`, `daylight_window`, `mixed`, `dim` | Illumination condition during the session |
| `motion_state` | enum | `stationary`, `low_speed` | Whether the vehicle was stationary or moving at low speed during capture |
| `split` | enum | `train`, `val`, `test` | Dataset partition assigned to the entire `session_id` |
| `width` | int | `> 0` (default `640` or `1296`) | Image width in pixels |
| `height` | int | `> 0` (default `480` or `972`) | Image height in pixels |
| `camera_model` | string | `ov5647` | Camera sensor identifier |

### 2.3 Mandatory Coverage Rules Across Viewpoint, Heading, and Lighting
To prevent the visual classifier from memorizing a single static camera pose:
1. **Multi-Viewpoint Coverage per Region**: For each `region_id`, frames must be collected at `center`, `left_offset`, and `right_offset` lateral positions, as well as `angled_left` and `angled_right` yaw perturbations (`±15°–30°`) along the traversable corridor.
2. **Heading Sector Explicitness**: Because a monocular forward camera observes completely different walls when facing North vs. South at the same `(x, y)` location, every sample records `heading_sector`. Visual region classes either include the heading sector (`(region_id, heading_sector)`) or are conditioned on the heading estimate before constraining pose.
3. **Lighting & Motion Diversity**: Training and validation sessions must record whether room lights, window daylight, or mixed lighting were active, and must include both `stationary` and `low_speed` frames once vehicle motion is enabled.

### 2.4 Strict Session-Separation Rule (Zero Session Leakage)
1. **Session-Level Partitioning Only**: A `session_id` represents one continuous recording run. Every frame with the same `session_id` **must** map to the exact same `split` (`train`, `val`, or `test`).
2. **Prohibition of Random Frame-Level Splits**: Randomly splitting consecutive frames from the same video run into `train` and `val` is prohibited. Consecutive frames captured seconds apart have near-identical lighting, background clutter, and camera pose, leading to severe data leakage and unrealistic validation metrics.
3. **Software Enforcement**:
   - **During Capture ([`camera_live_web.py`](camera_live_web.py))**: `CameraStreamer.save_labelled_frame()` tracks `self.session_splits[session_id]`. If an operator attempts to switch `split` from `train` to `val` or `test` without changing `session_id`, the capture API returns HTTP `400` (`Session leakage blocked`) and refuses to write the frame.
   - **Before Training ([`vision_manifest.py`](vision_manifest.py))**: The manifest validator scans all rows and raises a validation failure if any `session_id` appears in more than one `split`, or if `val`/`test` lacks independent sessions.
4. **Held-Out Run Acceptance Criterion (Cycle 3 Gate)**: A trained region-recognition model is only eligible to assist localization if it is evaluated on held-out `val` and `test` sessions recorded on separate runs from all `train` sessions.
