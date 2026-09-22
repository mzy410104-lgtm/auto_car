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

| Responsibility label | Main duties in the first half | Main duties during navigation work | Handover contents |
|---|---|---|---|
| A | Onboard camera, image acquisition, dataset definition, visual-place model, fixed-pickup identifiers, QR codes and user web workflow | Run the visual-place model on the Pi; transmit pickup requests and display task state | Camera and dataset records, model and validation evidence, QR material, pickup identifiers, web software and interface records |
| B | Pi environment, lidar and map production | Lidar localization, fusion of visual-region constraints and C's motion feedback, station-pose management, planning, path following and obstacle handling | Software versions, scans, maps, pickup stopping poses, localization/planning configurations and operating records |
| C | STM32, actuator control, interfaces, sensors and speed feedback | Speed/steering control, encoder and IMU acquisition, close-range protection, stopping/takeover, status and motion feedback | Firmware, interface agreement, calibration and evidence for control, timeout, signal loss and recovery |

C is confirmed as the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), responsible for STM32 and interfaces. A/B members and their GitHub accounts remain to be confirmed. A/B jointly own the visual-localization and pickup-request interfaces. B/C jointly own the navigation-control and motion-feedback interfaces. Component owners handle their own mounting and operating records; all three members share whole-vehicle acceptance testing. Count joint work by the number of people involved.

The owner confirmed that no STM32 project has been created yet. Initial STM32 work therefore starts with development-tool and board checks followed by creation of the first minimal project. The program currently stored on the physical board, if any, remains unverified. Project setup uses the existing C1/C3 allocation and buffer; it does not add working hours.

## 4. Twelve-Week Full-Cycle Schedule

| Week | Main objective | A's main tasks | B's main tasks | C's main tasks | Stage output and prerequisites |
|---|---|---|---|---|---|
| Week 1 | Independent baselines | Define pickup identifiers and QR/web flow; define camera-image acquisition rules | Verify Pi and real A2M8 scans | Preserve the verified UART baseline; restore and test original radio control with wheels raised | QR request prototype, real scan evidence and safe manual-control evidence |
| Week 2 | Interfaces and real data | Establish camera availability/interface/mounting; acquire first labelled image sessions | Save scan recordings; define map and navigation software reproduction | Measure isolated actuator-control signals; prepare STM32 PWM, timeout and sensor interfaces | A/B visual interface and pickup-request interface recorded; B/C command/feedback interface recorded |
| Week 3 | Low-level vehicle control and mapping preparation | Continue image acquisition across actual viewpoints and conditions | Prepare mapping pipeline and recorded-data replay | Verify STM32 neutral, steering, low-speed forward, stop and reverse with the vehicle secured; acquire IMU and SHARP data | Safe low-level control and reproducible sensor acquisition before floor autonomy |
| Week 4 | Motion feedback and first map | Prepare model training/validation split by acquisition session | Build and save the first real-vehicle lidar map | Integrate photointerrupter counting, speed magnitude, inferred direction limits and calibrated steering feedback | Reusable map and motion feedback with explicit limitations |
| Week 5 | Separate localization paths | Train and validate visual-place recognition on held-out runs | Run lidar localization on the saved map using C's time-aligned motion feedback | Provide timestamped speed/IMU/status streams and diagnose mounting/axis issues | Visual region output and continuous lidar-based pose tested separately |
| Week 6 | Fused initialization and recovery | Run camera inference on the Pi and provide place/region plus confidence | Use validated visual output to constrain initialization, check consistency or recover localization; retain lidar map matching as the continuous pose source | Support repeated starts and motion-feedback diagnosis | Repeated `(x, y, yaw)` localization with recorded success and failure cases |
| Week 7 | Fixed pickup targets | Generate final QR material and request handling for defined pickup identifiers | Measure each pickup stopping pose `(x, y, yaw)` on the map and implement identifier-to-pose lookup | Integrate target speed/steering and vehicle-status feedback | One pickup request reaches one mapped stopping pose through recorded interfaces |
| Week 8 | Path following and arrival | Display accepted, travelling, arrived and failed task states | Plan and follow a route respecting TT-02 dimensions, steering and turning radius | Tune low-speed control, feedback, stopping and communication timeout | One obstacle-free pickup task is reproducible and arrival error is recorded |
| Week 9 | Obstacle handling | Display blocked, replanning and resumed states | Build the live obstacle costmap; detour/replan when feasible and report blockage otherwise | Implement calibrated close-range SHARP protection, stop priority, takeover and recovery | Detection, stopping, detouring and blockage are accepted separately |
| Week 10 | Complete taxi workflow | Test different pickup QR codes and visual places | Connect pickup input, visual constraint, lidar pose, route execution, obstacle handling, arrival and status | Record fault states, logs and reconnection behavior | Complete fixed-pickup workflow under the team's documented test scope |
| Week 11 | Repeated tests and fixes | Analyze visual errors, QR/request errors and user-flow failures | Analyze localization, route-following and obstacle failures | Analyze control, communication, speed, IMU and protection failures | Record trial outcomes and regression checks; stop expanding feature scope |
| Week 12 | Freeze, report and demonstrate | Dataset/model/QR/web material and contribution record | System algorithms, maps, configurations and demonstration sequence | Interface, firmware, calibration, control and recovery material | Freeze the demonstration version; complete backups, startup instructions, report and rehearsal |

Each row represents 24 planned person-hours + 6 debugging person-hours. From Week 2 onward, refine individual time slots during the preceding work cycle's review; do not invent unconfirmed laboratory dates. Faults carried into another week consume that week's capacity and defer later work. Do not rely on unplanned overtime to keep every milestone unchanged.

## 5. Handover Prerequisites

1. **Power to equipment:** Actual wiring, no-load/loaded conditions, and results are clear. Document preparation does not count as a passed power check; isolate unverified branches.
2. **Mechanics to control:** Actual counts, distance per count, installation records, and anomaly records are complete. Without measured speed, do not consider closed-loop speed control complete.
3. **Control to navigation:** Evidence exists for speed, steering, stopping, and takeover/signal loss. Vehicle envelope and turning constraints have been measured, and data meanings are clear.
4. **Camera to localization:** Record camera calibration or intrinsic source, rigid mounting, image acquisition sessions, place/region labels, held-out-run validation and the exact visual output consumed by B. A visual class label does not by itself establish metric pose.
5. **Perception to continuous pose:** Record real lidar scans, mounting relationships, coordinate transforms, timing, encoder speed and IMU axes. Lidar map matching remains the continuous planar-pose source; visual output may constrain initialization, consistency checking or recovery only under validated conditions.
6. **Pickup request to navigation:** A pickup identifier becomes usable only after B records the corresponding mapped stopping pose and feasible arrival heading. A successful QR scan does not establish delivery of the request to the vehicle.
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
