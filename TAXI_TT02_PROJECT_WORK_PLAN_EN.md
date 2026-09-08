# Autonomous Taxi: Overall Project Plan (Replanned Around Current Hardware)

Revision date: 2026-09-08. See the [current work cycle plan](CURRENT_WEEK_TASKS_EN.md) for near-term execution and the [verification procedure](TAXI_TT02_VERIFICATION_STEPS_EN.md) for specific measurements.

## 1. Time and Objective

The user has confirmed a team of three, approximately 10 hours per person per week, and a three-month project. The vehicle must navigate a small room without floor markings, plan and follow a route from its current position to a selected destination, and handle obstacles in real time.

This table organizes the three months as a **full-cycle reference covering 12 working weeks**, with a capacity of 3 × 10 × 12 = 360 person-hours. Actual start/end dates, time already spent, and completed stages still need to be provided. Do not restart the table as a fresh 12 weeks from today or claim that 360 person-hours remain.

Each full working week includes 24 person-hours of planned tasks and 6 person-hours of debugging buffer, giving 288 + 72 = 360 person-hours over the full cycle. Testing, fixes, and reporting in the final two weeks are already included in this total, not added on top. Week numbers are scheduling targets; actual prerequisite results determine entry into the next stage.

## 2. Decisions to Retain

- Reuse the existing TT-02, Pi4, NUCLEO-F103RB, A2M8, SEN0253, two SHARP sensors, TBLE-04S, motor/servo, and radio-control equipment.
- A bootable SD card, sufficient data cables, and a handheld transmitter are already available. The hardware inventory and architecture diagram are complete; do not schedule hardware selection from scratch again.
- Speed sensing uses one perforated transmission gear, one dedicated gear cover, and one OPB815WZ photointerrupter. Do not return to the shaft-hole or dual-photointerrupter designs; update delivery/installation progress from actual information.
- Record speed magnitude and inferred direction separately. Retain limitations during reversal, coasting, and external pushing in motion estimation and control tests.
- Do not purchase a stereo camera at this stage; decide other additions, such as power components, from measured gaps.
- The architecture diagram is a design input; verify wiring, software, and operating results separately.

## 3. Long-Term Responsibilities

| Responsibility label | Main duties in the first half | Main duties during navigation work | Handover contents |
|---|---|---|---|
| A | Power, mechanics/speed-sensing components, original radio control, room | Measure dimensions/turning/stopping, execute tests, maintain hardware, and record costs | Wiring, power conditions, vehicle parameters, test records, and acquisition status |
| B | Pi environment, lidar, host communication | Mapping/localization, planning/path following, destination interface | Software versions, real scans, maps, configurations, and operating records |
| C | STM32, interfaces, sensors, and speed feedback | Speed/steering control, stopping/takeover, status and motion feedback | Firmware, interface agreement, calibration, and evidence for control/signal loss/recovery |

C is confirmed as the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), responsible for STM32 and interfaces. A/B members and their GitHub accounts remain to be confirmed. B/C jointly own the navigation-control interface. After mechanical work is complete, A continues to handle whole-vehicle testing. Count joint work by the number of people involved.

The owner confirmed that no STM32 project has been created yet. Initial STM32 work therefore starts with development-tool and board checks followed by creation of the first minimal project. The program currently stored on the physical board, if any, remains unverified. Project setup uses the existing C1/C3 allocation and buffer; it does not add working hours.

## 4. Twelve-Week Full-Cycle Schedule

| Week | Main objective | A's main tasks | B's main tasks | C's main tasks | Stage output and prerequisites |
|---|---|---|---|---|---|
| Week 1 | Basic checks and real data | Power, original radio control, speed-sensing component acquisition | Pi/lidar and host communication | STM32 operation and bidirectional communication | Produce the six deliverables in the current work cycle plan; retain the actual status of failed items |
| Week 2 | Fix basic issues and connect existing sensors | Power/wiring issues, room, and mechanical progress | Jointly record lidar, sensor, and vehicle status | Acquire SEN0253 and two SHARP sensor streams; prepare control outputs and command-failure handling | Acquire data after electrical checks; log jointly after communication passes; prioritize basic faults |
| Week 3 | Speed measurement and actuator control | Installation checks after delivery, full-rotation interference checks, and straight-line calibration | Record speed/movement data and prepare the motion-data interface | Photointerrupter interface, pulse counting/speed measurement, neutral and stopping under STM32 control | Perform real speed measurement only when mechanical parts are ready; connect automatic control outputs after interface/original-radio prerequisites are established |
| Week 4 | Low-speed control and motion data | Vehicle envelope, turning space, stopping distance | Check motion quantities, coordinates, timing, and correspondence with actual travel with C | Speed control, steering calibration, reversal, stopping, and takeover | Low-speed and feedback evidence available; applicability of inferred direction explicit; do not treat the chassis as capable of turning in place |
| Week 5 | Reusable map | Set up and document the environment; check occlusion | Map with the real vehicle, save the map and reproduction steps | Provide motion feedback, manual control, and stopping support | Basic driving/acquisition established; compare the map with the room; software preparation may start earlier |
| Week 6 | Localization on the map and repeatability | Record physical reference positions/headings and place the vehicle repeatedly | Localize on the saved map; test restarts and repositioning | Diagnose sensor coordinates, motion feedback, and timing | Position initialization explicit; save localization and failure evidence |
| Week 7 | Destination and feasible route | Check routes and turning space | Destination input and planning that respects chassis constraints | Integrate target speed/steering and status | Localization reproducible; first complete one simple end-to-end task |
| Week 8 | Path following and arrival | Measure straight-line/turning/arrival errors | Tune path following and arrival states | Tune low-speed control, feedback, and stopping | Destination selection through arrival and stopping reproducible; record measured errors |
| Week 9 | Obstacle handling | Controlled obstacles, coverage checks, and stopping tests | Detour/replan when a route exists; stop and report when no route exists | Close-range stopping, timeouts, takeover, and recovery | Record detection, stopping, detouring, and blockage separately; start with static obstacles, then controlled moving obstacles |
| Week 10 | Complete taxi workflow | Test different start/destination/route/obstacle combinations | Connect task input, localization, driving, arrival, and status display | Fault states, logs, and reconnection behavior | Demonstrate against the formal scope; if requirements remain undecided, state the team's own test scope |
| Week 11 | Repeated tests and fixes | Repeat trials; check endurance and hardware condition | Analyze and fix localization/route/detour issues | Analyze and fix control/communication/speed-measurement issues | Record trial counts and outcomes; perform regression checks; stop expanding the feature scope |
| Week 12 | Freeze the version, report, and demonstrate | Hardware, parameters, costs, demonstration preparation | System/algorithms, maps, demonstration sequence | Interface/firmware/control and recovery material | Freeze the demonstration version; complete backups, startup instructions, report, and rehearsal |

Each row represents 24 planned person-hours + 6 debugging person-hours. From Week 2 onward, refine individual time slots during the preceding work cycle's review; do not invent unconfirmed laboratory dates. Faults carried into another week consume that week's capacity and defer later work. Do not rely on unplanned overtime to keep every milestone unchanged.

## 5. Handover Prerequisites

1. **Power to equipment:** Actual wiring, no-load/loaded conditions, and results are clear. Document preparation does not count as a passed power check; isolate unverified branches.
2. **Mechanics to control:** Actual counts, distance per count, installation records, and anomaly records are complete. Without measured speed, do not consider closed-loop speed control complete.
3. **Control to navigation:** Evidence exists for speed, steering, stopping, and takeover/signal loss. Vehicle envelope and turning constraints have been measured, and data meanings are clear.
4. **Perception to localization:** Record real scans, mounting relationships, direction/timing, and motion data. Software self-tests do not replace real-vehicle localization.
5. **Localization to execution:** First reproduce the current position and heading, then assess planning and following. The existence of a map does not establish completed localization.
6. **Routes to obstacle handling:** Accept stopping, detouring, and blockage handling separately. Stopping at an obstacle does not substitute for detouring.

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
4. Separate evidence for map localization, path following, arrival, obstacle stopping, detouring, blockage handling, and fault recovery.
5. Actual trial counts and successes/failures, arrival error, continuous-operation records, and endurance records; explicitly identify untested items.
6. Report, demonstration, and records of team members' contributions.

This file is an execution plan, not an instructor-approved project brief, and it does not establish that the real-vehicle functions above have passed acceptance.
