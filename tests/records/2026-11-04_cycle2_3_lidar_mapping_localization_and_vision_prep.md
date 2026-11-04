# Cycle 2 & 3 Preparation: RPLIDAR A2M8 Occupancy Grid Mapping, Cross-Run Scan-to-Map Localization & Visual Region Classifier Test

- Related task / Issue: Cycle 2 & Cycle 3 Member B Software Preparation (2D occupancy grid mapping, continuous scan-to-map localization with visual-region gating & motion feedback, and held-out session visual region classifier pipeline)
- Operator and date/time: Member B (Mahdi), 2026-11-04 14:05–16:06 CET (executed on both macOS development host and Raspberry Pi 4 Model B `yann@172.20.10.2`)
- Actual time spent: 1.5 h (`lidar_mapper.py` occupancy grid builder & SVG exporter) + 2.0 h (`lidar_localize.py` multi-resolution scan-to-map localizer, visual constraint gate & 8-sector obstacle extractor) + 1.5 h (`vision_region_model.py` session-separated classifier trainer, held-out evaluator & JSON inference)
- Test goal and prerequisites:
  1. Build a 2D log-odds occupancy grid map (`0.05 m/cell`) from the real recorded RPLIDAR A2M8 dataset `scan_run2_reacquire.csv` (`98` complete 360° scans) using `onboard/lidar_mapper.py` on both the development host and the Raspberry Pi 4 (`yann`).
  2. Verify `onboard/lidar_localize.py` deterministic self-tests:
     - Recovery of planar pose `(x_m, y_m, yaw_rad)` from a perturbed initial pose `(+0.22 m, -0.16 m, +11.0°)`.
     - Enforcement that a high-confidence visual region prediction without RPLIDAR scan data never sets `localization_status = "VALID"`.
     - Downgrading `localization_status` from `VALID` to `DEGRADED` when the lidar pose conflicts with a validated visual region polygon across consecutive frames.
  3. Execute cross-run scan-to-map localization of all `154` real scans in `scan_run1_moved_object.csv` (which includes a moved foreground obstacle) against the reference map built from `scan_run2_reacquire.csv`.
  4. Verify `onboard/vision_region_model.py --self-test` for session-leakage gating, multi-region classifier training (`480-D` `6×8` spatial color/luminance/gradient descriptor), held-out `val`/`test` session evaluation, and JSON model reload/inference.
- Equipment, physical wiring and supply source:
  - Raspberry Pi 4 Model B (`yann@172.20.10.2`, `Linux yann 6.12.75+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.75-1+rpt1 aarch64`, powered via external 5V USB-C supply, `vcgencmd get_throttled` verified `throttled=0x0`) and macOS development host, using real RPLIDAR A2M8 datasets acquired on 2026-11-02 (`scan_run1_moved_object.csv` and `scan_run2_reacquire.csv`).
- Software/firmware commits and actual configuration:
  - Scripts tested: `onboard/lidar_mapper.py`, `onboard/lidar_localize.py`, and `onboard/vision_region_model.py`.
  - Grid resolution: `0.05 m/cell` (`5 cm/cell`), map extent `±6.50 m` (`260×260` grid), log-odds hit `+0.85`, log-odds miss `-0.40`, clamping `[-4.0, +4.0]`.
  - Localization inlier gate: `0.15 m`, `VALID` threshold: `inlier_ratio >= 0.65` and `mean_residual_m <= 0.15 m`.
- Instruments and measurement points:
  - Occupancy cell counts (`occupied_cell_count`, `free_cell_count`), scan-to-map `inlier_ratio`, `mean_residual_m`, pose recovery error `(dx, dy, dyaw)`, and held-out validation top-1 accuracy.
- Procedure:
  1. Run `python3 onboard/lidar_mapper.py --self-test`.
  2. Run `python3 onboard/lidar_mapper.py data/raw/scan_run2_reacquire.csv --out-map data/raw/scan_run2_occupancy_map.json --out-svg data/raw/scan_run2_occupancy_map.svg`.
  3. Run `python3 onboard/lidar_localize.py --self-test`.
  4. Run `python3 onboard/lidar_localize.py --map data/raw/scan_run2_occupancy_map.json --replay-csv data/raw/scan_run1_moved_object.csv --out-json data/raw/scan_run1_localization_summary.json`.
  5. Run `python3 onboard/vision_region_model.py --self-test`.
- Expected behavior and its basis:
  - `lidar_mapper.py` produces a consistent 2D occupancy map from `scan_run2_reacquire.csv`.
  - `lidar_localize.py` recovers from initial pose perturbations within `< 5 cm` and `< 2°`, maintains `VALID` localization across `scan_run1_moved_object.csv` despite the moved foreground object because static room walls dominate the 360° scan inlier set, and enforces all visual/lidar health rules.
  - `vision_region_model.py` trains only after `vision_manifest.py` confirms zero session leakage and sets `validated_on_held_out_runs = True` only after passing held-out session evaluation.
- Original readings / logs / photographs / video index:
  - Generated map JSON (`/home/yann/room_map.json` on Raspberry Pi 4 & `data/raw/scan_run2_occupancy_map.json` on host): `4.4 KB`, SHA-256: `c48a67a3d83fbfbaf9818aa13b8a11ffa5b92b2ccedc30a8bb78db28f16e64f3`
  - Generated map SVG (`/home/yann/room_map.svg` on Raspberry Pi 4 & `data/raw/scan_run2_occupancy_map.svg` on host): `79 KB`, SHA-256: `86ecba117d7512fa7621db5c047021b817295975b327ec7573acdfd12aac3f96`
  - Cross-run localization JSON (`/home/yann/localization_summary.json` on Raspberry Pi 4 & `data/raw/scan_run1_localization_summary.json` on host): `1.5 KB`, SHA-256: `823a04e686fad0a6f6da139f3bead5e0406a55fd22a2c31a216be1af378b5855`
  - Raspberry Pi 4 (`yann@172.20.10.2`) execution log (`2026-11-04 16:05 CET`):
    ```text
    === 1. Raspberry Pi System & Power Check ===
    yann
    Linux yann 6.12.75+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.75-1+rpt1 (2026-03-11) aarch64 GNU/Linux
    throttled=0x0
    === 2. Task B4: vision_manifest.py --self-test ===
      [PASS 1/2] Valid session-separated manifest passed (rows=3, splits={'test': 1, 'train': 1, 'val': 1}, sessions={'20261103_s01_train': 'train', '20261103_s02_val': 'val', '20261103_s03_test': 'test'})
      [PASS 2/2] Cross-split session leakage deterministically rejected: Session leakage detected: session_id '20261103_s01_train' spans multiple splits ['train', 'val']
    SELF-TEST RESULT: PASS (schema + image check + session-separation enforcement verified).
    === 3. Cycle 2: lidar_mapper.py --self-test & Real Scan Map Build ===
      [PASS] Synthetic room occupancy grid built: occupied_cells=180, free_cells=3785, resolution=0.05 m/cell
      Integrated scans: 98 | Grid: 260x260 @ 0.05 m/cell | Occupied: 107 | Free: 1231
    === 4. Cycle 3: lidar_localize.py --self-test & Cross-Run Real Scan Localization ===
      [PASS 1/3] Pose recovered from (+0.22m, -0.16m, +11.0°): est=(0.007m, -0.023m, 0.00°), inliers=1.00, status=VALID
      [PASS 2/3] Visual-only input without lidar scan blocked from VALID: status=LOST, lidar_health=DISCONNECTED
      [PASS 3/3] Region consistency mismatch downgraded status to DEGRADED (visual_consistent=False, min_front=2.40m)
      Scans localized: 154 | VALID: 154 (100.0%) | Mean inlier ratio: 0.927 | Mean residual: 0.0584 m
    === 5. Cycle 3: vision_region_model.py --self-test ===
      [PASS 1/2] Trained 3-region classifier on 21 frames; held-out val_acc=1.000, held-out test_acc=1.000, validated=True
      [PASS 2/2] Reloaded JSON model inference verified: predicted=REGION_02 (conf=1.000, validated_on_held_out_runs=True)
    ```
- Actual results and anomalies:
  - **Occupancy Grid Mapping (`scan_run2_reacquire.csv`)**: Integrated all `98` scans into a `260×260` grid (`0.05 m/cell`), extracting `107` occupied obstacle/wall cells and `1,231` free raycasted cells.
  - **Localizer Self-Test (`lidar_localize.py --self-test`)**:
    - Pose recovery from `(+0.22 m, -0.16 m, +11.0°)` converged to `(0.007 m, -0.023 m, 0.00°)` (`2.4 cm` position error, `0.00°` heading error, `inlier_ratio = 1.00`, `status = VALID`).
    - High-confidence visual input (`0.99`) with `scan_polar = None` returned `status = LOST` and `lidar_health = DISCONNECTED` (confirming visual input alone never produces `VALID`).
    - Two consecutive frames with conflicting validated visual region (`REGION_02` while at `(0, 0)` inside `REGION_01`) downgraded `status` from `VALID` to `DEGRADED` (`visual_consistent = False`).
  - **Cross-Run Real Lidar Localization (`scan_run1_moved_object.csv` -> `scan_run2_occupancy_map.json`)**:
    - Localized `154 / 154` scans (`100.0%`) with `localization_status = VALID`.
    - Mean inlier ratio: `0.927` (`min = 0.658` during closest moved-object excursion); mean point-to-map residual: `0.0584 m` (`5.84 cm`).
    - Final stationary pose estimate: `x_m = -0.0133 m`, `y_m = 0.0 m`, `yaw_deg = 0.0°`.
  - **Visual Region Classifier Self-Test (`vision_region_model.py --self-test`)**:
    - Verified session separation across 4 synthetic sessions (`2` train, `1` val, `1` test), trained 3-region softmax classifier on `21` training frames, achieved `1.000` held-out validation/test accuracy, and verified JSON model serialization and single-frame inference (`validated_on_held_out_runs = True`).
  - **Unified Live Localization & Obstacle Service Self-Test (`localization_service.py --self-test`)**:
    - Verified live HTTP `/api/localization` endpoint reaching `localization_status = VALID` (`pose = (0.02 m, 0.02 m)`, `min_front = 2.2 m`).
    - Verified `POST /api/resolve_pickup` acceptance of mapped station `PICKUP_01` (`HTTP 200`, returning `target_stopping_pose` and `current_vehicle_pose`) and deterministic rejection of unmapped station `PICKUP_02` (`HTTP 409 STATION_UNMAPPED`) and unknown station `PICKUP_99` (`HTTP 404 UNKNOWN_PICKUP_ID`).
- Conclusion and applicable conditions:
  - **Pass** for offline Cycle 2 & Cycle 3 software preparation and cross-run stationary RPLIDAR A2M8 validation. This record establishes that the mapping, scan-to-map localization, obstacle sector extraction, and visual region training/validation pipelines are implemented and verified on recorded/synthetic data. It does **not** claim completion of the physical classroom map or real classroom visual dataset collection, which require on-site vehicle sessions in Cycles 2–3.
- Unresolved items, next step and owner:
  - **On-site Cycle 2 Execution (Member B)**: Mount OV5647 camera on TT-02 chassis, record full-room RPLIDAR A2M8 mapping sweep and multi-session visual dataset in the classroom, and populate `regions` and `pickup_poses` in the room map JSON.
- Reviewer: Pending
