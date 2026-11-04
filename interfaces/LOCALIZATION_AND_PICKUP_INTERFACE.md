# Pickup Request, Localization, and Obstacle Interface Agreement (Task AB)

Revision date: 2026-11-04  
Participants: Member A (pickup service, task state, global/local navigation) and Member B (camera region AI, RPLIDAR A2M8 mapping/localization, sensor fusion)  
Related tasks: Cycle 1 Task `AB` ([CURRENT_WEEK_TASKS_EN.md](../CURRENT_WEEK_TASKS_EN.md), GitHub Issues `#7` & `#8`)

This interface note defines the logical data boundary between Member A's pickup/navigation subsystem and Member B's perception/localization subsystem on the Raspberry Pi 4. Exact inter-process transport identifiers, room map coordinates, and update frequencies remain explicitly undecided until both implementations and the Cycle 2 room map are established.

---

## 1. Boundary Overview

| Boundary direction | Logical channel | Producer → Consumer | Purpose |
|---|---|---|---|
| `A <-> B` | Station Stopping-Pose Table | B defines mapped poses → A resolves incoming `pickup_id` | Maps a logical fixed-pickup identifier (`pickup_id`) submitted via QR/web to a validated stopping pose `(x_m, y_m, yaw_rad)` on the room map. |
| `B -> A` | Continuous Planar Pose & Health | B (Localization) → A (Task Manager & Path Follower) | Provides real-time planar pose `(x_m, y_m, yaw_rad)`, visual map-region constraint (`visual_region_id`, `visual_confidence`), and localization health status (`localization_status`). |
| `B -> A` | Lidar Obstacle Summary | B (RPLIDAR A2M8 processing) → A (Local Obstacle Handler) | Provides timestamped obstacle distances/sectors in the vehicle frame (`base_link`) for protective stopping and local detour replanning. |

---

## 2. Fixed-Pickup Identifier and Mapped Stopping Pose (`A <-> B`)

1. **Independence of QR Scanning and Onboard Camera**:
   - The passenger scans a stationary location QR code using a smartphone browser to submit a `pickup_id` to Member A's web service.
   - Scanning a pickup QR code does **not** supply the vehicle's current pose, and the vehicle's onboard OV5647 camera does **not** scan passenger QR codes.
2. **Station Table Responsibility**:
   - Member A defines the logical station identifiers (e.g., `PICKUP_01`, `PICKUP_02`, ...) and manages user request acceptance/rejection and task state transitions.
   - Once the real test room map is built with the RPLIDAR A2M8 in Cycle 2, Member B records the corresponding stopping pose and arrival heading in the `map` frame for each valid `pickup_id`.
   - **Cycle 1 Constraint**: No numeric `(x_m, y_m, yaw_rad)` coordinates are invented in Cycle 1 before the physical room is mapped.
3. **Request Acceptance & Rejection Conditions at the `A/B` Boundary**:
   - Member A's service must **reject** (or hold from entering active driving) a pickup request if:
     - `pickup_id` is unknown or its mapped stopping pose is still `UNMAPPED` (`null`).
     - Member B's `localization_status` is `UNINITIALIZED` or `LOST` when autonomous dispatch is requested.
     - Another pickup task is already active (`VEHICLE_BUSY`) or the low-level controller reports a fault (`VEHICLE_FAULT`).

| Logical field | Meaning | Units / allowed values | Cycle 1 status |
|---|---|---|---|
| `pickup_id` | Fixed pickup station identifier | Project string (e.g., `PICKUP_01`) | Structure agreed; final station list owned by Member A (`Task A1`) |
| `target_x_m`, `target_y_m` | Stopping position in `map` frame | Meters (`m`) | **Unresolved** until Cycle 2 RPLIDAR room map |
| `target_yaw_rad` | Required vehicle arrival heading in `map` frame | Radians (`rad`, `[-pi, pi]`, CCW from `+X_map`) | **Unresolved** until Cycle 2 RPLIDAR room map |
| `arrival_xy_tol_m`, `arrival_yaw_tol_rad` | Position and heading tolerance to declare arrival | Meters (`m`), Radians (`rad`) | **Unresolved** pending TT-02 turning/stopping measurements |

---

## 3. Continuous Localization Output (`B -> A`)

Member B's localization module supplies the vehicle pose and visual region constraint to Member A's planner/controller:

| Logical field | Meaning | Units / allowed values | Role in navigation (`Member A`) |
|---|---|---|---|
| `timestamp_s` | Monotonic / Unix epoch timestamp of pose estimate | Seconds (`s`, float) | Reject stale pose estimates exceeding age threshold |
| `x_m`, `y_m` | Continuous planar vehicle position (`base_link` origin in `map` frame) | Meters (`m`) | Primary position input for global planning and path following |
| `yaw_rad` | Continuous planar vehicle heading in `map` frame | Radians (`rad`, `[-pi, pi]`) | Primary heading input for steering control |
| `localization_status` | Overall pose health state | `UNINITIALIZED`, `VALID`, `DEGRADED`, `LOST` | Navigation may initiate/continue autonomous motion only in `VALID` (or speed-limited `DEGRADED` if agreed); `UNINITIALIZED` or `LOST` triggers immediate stop |
| `visual_region_id` | Discrete map region recognized by OV5647 model | `REGION_01`..`REGION_NN` or `UNKNOWN` | Used by B for pose initialization, consistency check, or recovery only after held-out run validation; **never used by A as a direct substitute for `(x_m, y_m, yaw_rad)`** |
| `visual_confidence` | Classifier probability / confidence score | Float `[0.0, 1.0]` | Gated against validation threshold before constraining pose |

### Validation & Rejection Rules for Localization Output
- **Visual-Only Constraint Rule**: A high-confidence `visual_region_id` without valid RPLIDAR scan matching does **not** set `localization_status = VALID`.
- **Region Consistency Mismatch**: If RPLIDAR pose `(x_m, y_m)` falls outside the mapped polygon of a high-confidence validated `visual_region_id` for consecutive frames, Member B downgrades `localization_status` to `DEGRADED` (or `LOST`) so Member A can command a safe stop or recovery.

---

## 4. Lidar Obstacle Summary (`B -> A`)

From the live RPLIDAR A2M8 360° scan stream (`~10.98 Hz` verified in [`2026-11-02_pi_rplidar_a2m8_baseline.md`](../tests/records/2026-11-02_pi_rplidar_a2m8_baseline.md)), Member B provides obstacle data in the vehicle frame:

| Logical field | Meaning | Units / convention |
|---|---|---|
| `scan_timestamp_s` | Timestamp of the completed 360° lidar scan | Seconds (`s`, float) |
| `min_front_distance_m` | Closest valid obstacle return within the forward driving corridor | Meters (`m`) |
| `sector_distances_m` | Minimum obstacle distances across angular sectors around the vehicle | Meters (`m`) per angular bin |
| `lidar_health` | RPLIDAR acquisition health | `OK`, `STALE`, `DISCONNECTED` |

- If `lidar_health != OK` or `scan_timestamp_s` exceeds the staleness timeout during motion, Member A must immediately command a protective stop (`STOP`).
- Note: Hardware close-range emergency protection (`SHARP GP2Y0A21YK0F` on STM32, owned by Member C) operates below Member A's planner and always retains stop priority.

---

## 5. Explicitly Undecided Parameters (Pending Joint A/B Implementation & Cycle 2 Tests)

1. **IPC Transport & Serialization**: Whether A and B exchange data on the Raspberry Pi via local UDP/TCP JSON sockets, ZeroMQ, shared memory, or Python module queues remains undecided until Member A's navigation skeleton (`Task A4`) is integrated.
2. **Exact Field Names & Update Rates**: Target localization publication rate (`10 Hz` aligned with RPLIDAR scan rate vs. higher-rate IMU/wheel-speed interpolation) and exact staleness timeout values remain to be finalized.
3. **Physical Room Coordinates & Region Polygons**: All `pickup_id` stopping poses `(target_x_m, target_y_m, target_yaw_rad)` and `REGION_01..NN` boundaries depend on Cycle 2 room mapping.
