# Autonomous Taxi: Overall Project Plan (Visual Region Constraint, Lidar Pose and Fixed Pickup QR)

Revision date: 2026-09-22. See the [verification procedure](TAXI_TT02_VERIFICATION_STEPS_EN.md) for specific electrical and vehicle measurements. The current-work-cycle file predates the localization and fixed-pickup revision and must not be used to assign the new camera or QR work.

## 1. Time and Objective

The user has confirmed a team of three, approximately 10 hours per person per week, and a three-month project. The vehicle must operate in a small room without floor markings. A monocular camera provides a visual constraint identifying the map region or reference place. Lidar map matching, wheel-speed feedback and IMU motion information provide the continuous planar pose `(x, y, yaw)`. Users scan a location-specific QR code at a fixed pickup point; the service converts that pickup identifier into a mapped stopping pose, and the vehicle plans and follows a route while handling obstacles in real time.

This table organizes the three months as a **full-cycle reference covering 12 working weeks**, with a capacity of 3 × 10 × 12 = 360 person-hours. Actual start/end dates, time already spent, and completed stages still need to be provided. Do not restart the table as a fresh 12 weeks from today or claim that 360 person-hours remain.

Each full working week includes 24 person-hours of planned tasks and 6 person-hours of debugging buffer, giving 288 + 72 = 360 person-hours over the full cycle. Testing, fixes, and reporting in the final two weeks are already included in this total, not added on top. Week numbers are scheduling targets; actual prerequisite results determine entry into the next stage.

## 2. Decisions to Retain

- Reuse the existing TT-02, Pi4, NUCLEO-F103RB, A2M8, SEN0253, two SHARP sensors, TBLE-04S, motor/servo, and radio-control equipment.
- A bootable SD card, sufficient data cables, and a handheld transmitter are already available. Use the existing inventory as the baseline and do not repeat identification of confirmed equipment. The newly required monocular camera still needs its own availability and selection record.
- Speed sensing uses one perforated transmission gear, one dedicated gear cover, and one OPB815WZ photointerrupter. Do not return to the shaft-hole or dual-photointerrupter designs; update delivery/installation progress from actual information.
- Record speed magnitude and inferred direction separately. Retain limitations during reversal, coasting, and external pushing in motion estimation and control tests.
- Do not purchase a stereo camera. The revised method requires one Pi-compatible monocular camera; its existing availability, exact model, field of view, interface and mounting arrangement have not been confirmed and must be established before acquisition or installation.
- Train or configure the visual subsystem to identify a reference place or map region and report its confidence. Do not treat one natural-scene image classification as a verified continuous metric pose.
- Use lidar map matching as the primary correction for continuous planar pose. Fuse verified wheel-speed and IMU motion information for short-term motion estimation. Use the visual result for initialization, consistency checking or recovery only after validating it on separately recorded runs.
- Use location-specific QR codes at fixed pickup points. The QR workflow supplies a pickup identifier; the mapped stopping pose, including arrival heading, is maintained in the vehicle-service configuration after the map is established.
- Keep user QR scanning and vehicle-camera localization as separate functions: the phone scans pickup QR codes, while the onboard camera observes the environment.
- Use the SHARP sensors for close-range obstacle protection after calibration; do not use them as map-position measurements.
- The architecture diagram is a design input; verify wiring, software, and operating results separately.

## 3. Long-Term Responsibilities

The user confirmed on 2026-09-22 that the following A/B/C ownership applies across the three-month project. Weekly tasks may move when prerequisites or vehicle access change, but responsibility for the three main workstreams remains fixed unless the team explicitly revises it.

| Responsibility label | Main duties in the first half | Main duties during navigation work | Handover contents |
|---|---|---|---|
| A | Fixed-pickup identifiers, QR codes, user web workflow and navigation-task state | Convert accepted pickup requests into navigation goals; implement global planning, path following, local replanning, arrival state and user-visible status | QR material, pickup identifiers, web software, task-state records, planning configurations and route/obstacle test evidence |
| B | Onboard camera, image acquisition, dataset definition, AI model, Pi environment, lidar and map production | Run visual-place inference, lidar localization and fusion of visual-region constraints with C's motion feedback; maintain mapped pickup stopping poses | Camera and dataset records, model and validation evidence, software versions, scans, maps, pickup stopping poses and localization records |
| C | STM32, actuator control, interfaces, sensors and speed feedback | Speed/steering control, encoder and IMU acquisition, close-range protection, stopping/takeover, status and motion feedback | Firmware, interface agreement, calibration and evidence for control, timeout, signal loss and recovery |

C is confirmed as the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), responsible for STM32 and interfaces. A/B members and their GitHub accounts remain to be confirmed. B owns camera AI and continuous localization; A consumes B's validated pose and owns pickup-task execution, planning and obstacle-handling behavior. A/B jointly own the pose, obstacle and pickup-task interfaces. A/C exchange vehicle commands and status through the high-level/low-level interface, with B contributing the pose and motion-feedback requirements. Component owners handle their own mounting and operating records; all three members share whole-vehicle acceptance testing. Count joint work by the number of people involved.

The NUCLEO-F103RB project now exists in the repository. Compilation, flashing, LD2 operation, USART2 interrupt reception and the standalone `PING`/`PONG` diagnostic exchange have corresponding records. These results establish the STM32 development and diagnostic-communication baseline only; they do not establish Pi integration, actuator control, vehicle sensors or autonomous driving.

## 4. Six Two-Week Work Cycles

Each cycle covers two working weeks. Each member has 20 hours per cycle: 16 hours of assigned work and 4 hours for debugging, review and integration. One cycle therefore contains 48 planned team hours and 12 buffer hours. Across six cycles this retains the full 360-person-hour project capacity.

| Cycle | Main objective | A: pickup service and navigation | B: camera AI and localization | C: STM32 and vehicle control | Required cycle output |
|---|---|---|---|---|---|
| Cycle 1, Weeks 1–2 | Establish independent baselines without camera or photointerrupter dependency | Define pickup identifiers; build one QR/web request; define task states; prepare navigation software structure and interfaces | Record camera requirements and image rules; verify Pi/A2M8; save and replay real scans; prepare AI environment and data-manifest structure | Resolve the 3.5V battery condition; restore raised-wheel radio control; measure isolated PWM; verify Pi–STM32 diagnostic communication; prepare sensor interfaces | Reproducible QR request, lidar acquisition/restart, safe radio-control evidence, isolated PWM record and agreed boundaries |
| Cycle 2, Weeks 3–4 | Obtain real perception data, first map and reliable low-level actuation | Implement request queue/state handling; prepare planning on recorded or test maps; define vehicle-command behavior with C | After the actual camera is available, mount it and collect labelled sessions; build the first real lidar map; preserve a session-separated dataset split | Verify STM32 control of neutral, steering, low-speed forward, stop and reverse; acquire IMU/SHARP data; integrate the photointerrupter only after delivery and electrical checks | First reusable map, labelled visual data, safe automatic actuator baseline and recorded sensor streams |
| Cycle 3, Weeks 5–6 | Produce continuous localization and planning inputs | Implement route planning against the saved map and TT-02 turning constraints; import mapped pickup stopping poses | Train and validate visual-place recognition on held-out runs; run lidar map localization; combine validated visual region constraints with time-aligned motion feedback | Provide timestamped speed, IMU and status feedback; calibrate steering and speed after the optical assembly is available; diagnose axes and timing | Repeated `(x, y, yaw)` output with quality state, visual validation evidence, feasible planned routes and calibrated motion feedback or an explicit dependency block |
| Cycle 4, Weeks 7–8 | Complete one obstacle-free pickup journey | Connect QR requests to mapped goals; implement path following, arrival state and user-visible progress | Run camera inference and lidar localization during motion; maintain pickup stopping poses and localization diagnostics | Execute target speed/steering; tune low-speed control, stopping, timeout and status feedback | One reproducible request-to-arrival run without temporary obstacles, including measured arrival error and failure logs |
| Cycle 5, Weeks 9–10 | Add obstacle handling and fault recovery | Build local obstacle handling; stop, replan or report blockage; display blocked and resumed states | Supply validated lidar obstacle data; verify localization stability near obstacles and during recovery | Implement calibrated SHARP close-range protection, stop priority, manual takeover, link-loss handling and reconnection | Separate evidence for detection, protective stop, feasible detour, no-route blockage, takeover and communication recovery |
| Cycle 6, Weeks 11–12 | Repeat tests, freeze and demonstrate | Fix QR, task, planning, following and detour failures; freeze web/navigation material | Fix dataset, model, map and fused-localization failures; freeze perception/localization material | Fix control, communication, speed, IMU and protection failures; freeze firmware and calibration material | Regression results, trial counts, known limitations, complete startup/recovery instructions, final report, backups and demonstration rehearsal |

Review scope, evidence and unresolved prerequisites at the end of every two-week cycle before assigning the next cycle's detailed task hours. Work that fails a prerequisite consumes the next cycle's capacity and moves dependent work; do not claim completion from calendar progress or use unplanned overtime to preserve every date.

## 5. Handover Prerequisites

1. **Power to equipment:** Actual wiring, no-load/loaded conditions, and results are clear. Document preparation does not count as a passed power check; isolate unverified branches.
2. **Mechanics to control:** Actual counts, distance per count, installation records, and anomaly records are complete. Without measured speed, do not consider closed-loop speed control complete.
3. **Control to navigation:** Evidence exists for speed, steering, stopping, and takeover/signal loss. Vehicle envelope and turning constraints have been measured, and data meanings are clear.
4. **Camera AI to localization:** B records camera calibration or intrinsic source, rigid mounting, image acquisition sessions, place/region labels, held-out-run validation and the exact visual output used by the localization subsystem. A visual class label does not by itself establish metric pose.
5. **Perception to continuous pose:** Record real lidar scans, mounting relationships, coordinate transforms, timing, encoder speed and IMU axes. Lidar map matching remains the continuous planar-pose source; visual output may constrain initialization, consistency checking or recovery only under validated conditions.
6. **Pickup request to navigation:** A pickup identifier becomes usable only after B records the corresponding mapped stopping pose and feasible arrival heading and A imports it into the task workflow. A successful QR scan does not establish delivery of the request to the vehicle.
7. **Localization to execution:** First reproduce the current position and heading, then assess planning and following. The existence of a map does not establish completed localization.
8. **Routes to obstacle handling:** Accept stopping, detouring and blockage handling separately. Stopping at an obstacle does not substitute for detouring.

Project preparation, recorded-data processing, and module development may begin earlier in parallel. Vehicle movement and cross-module acceptance still require the corresponding prerequisite evidence.

## 6. Delays and Resource Management

- Separate power-disconnected rewiring, stationary scanning, and movement tests on the same vehicle. Only boards that are actually isolated may be powered in parallel. Reserve Pi and NUCLEO together for integration tests.
- Submit requirements for speed-sensing components early. Schedule installation from actual delivery and fabrication results; do not infer delivery dates from planned week numbers.
- If parts are delayed, first work on lidar data, sensor/communication software, mapping-software preparation, and report material. Defer affected measured-speed, control, and motion-feedback tasks. If formal delivery is affected, coordinate scope/scheduling with the instructor; do not independently lower required acceptance criteria.
- Record fault symptoms, factors already ruled out, and the next verification before using the buffer. Each week, credit existing evidence and record each person's actual effort.
- The team must establish the deadline, room, permitted software/algorithm reuse, speed/accuracy/obstacle criteria, initialization rules, and arrival rules. Leave them undecided until responses are received.
- Record actual hardware spending item by item, including taxes, shipping, and included items. Do not enter estimates as confirmed costs when no quotation has been received.

## 7. Final Deliverables

1. A real-vehicle version that executes destination tasks under the documented room conditions, with startup, stopping, and recovery procedures.
2. Actual wiring diagram, hardware inventory, actual costs, measured parameters, and known limitations.
3. Recoverable Pi and STM32 projects, configurations, interface agreements, and corresponding versions.
4. Versioned image-acquisition rules, labelled visual-place data, the trained or configured model, held-out-run results, fixed-pickup QR material and user-request software.
5. Separate evidence for visual-region recognition, lidar-based planar pose, initialization/recovery, path following, arrival, obstacle stopping, detouring, blockage handling and fault recovery.
6. Actual trial counts and successes/failures, arrival error, continuous-operation records and endurance records; explicitly identify untested items.
7. Report, demonstration and records of team members' contributions.

This file is an execution plan, not an instructor-approved project brief, and it does not establish that the real-vehicle functions above have passed acceptance.
