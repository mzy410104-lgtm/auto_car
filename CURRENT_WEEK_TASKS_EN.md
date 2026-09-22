# Autonomous Taxi: Current Two-Week Work Cycle

Revision date: 2026-09-22. This is Cycle 1 of the six-cycle plan and covers project Weeks 1–2. It replaces the earlier one-week allocation after adoption of visual map-region constraints, continuous lidar-based pose and fixed-pickup QR requests.

## 1. Objective

Establish three independent baselines that can later be integrated:

1. A phone can submit one fixed-pickup identifier through a QR/web prototype.
2. The Raspberry Pi can acquire and save real RPLIDAR A2M8 scans with reproducible restart instructions.
3. The original radio-control path can safely demonstrate neutral, steering, low-speed forward, stopping and reverse with the vehicle secured and its wheels raised.

The camera model, complete lidar localization, autonomous actuator control and floor-level autonomous driving are later-stage results. Do not record them as completed in this cycle unless separate real evidence exists.

## 2. Capacity and ownership

Each member has approximately 10 hours per week and 20 hours in this two-week cycle. Allocate 16 hours to the tasks below and retain 4 hours for debugging, review and unexpected hardware access limits.

| Member | Revised responsibility | Planned work | Buffer | Two-week total |
|---|---|---:|---:|---:|
| A | Fixed-pickup QR, user web flow, task state and navigation preparation | 16 h | 4 h | 20 h |
| B | Camera data, AI-model training, Raspberry Pi, lidar and localization preparation | 16 h | 4 h | 20 h |
| C | STM32, radio/actuator control, sensors, motion feedback and safety | 16 h | 4 h | 20 h |

C is the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), and owns the STM32 endpoint. A/B names and GitHub accounts remain unconfirmed and must not be inferred.

This work cycle follows the three-month ownership confirmed on 2026-09-22: A owns pickup service and navigation execution, B owns camera AI and localization, and C owns STM32 and low-level vehicle control.

## 3. A: fixed-pickup service and navigation preparation — 16 hours

| ID | Time | Task | Completion evidence |
|---|---:|---|---|
| A1 | 1.0 h | List the intended fixed pickup points and assign project-defined identifiers without map coordinates yet | Reviewed pickup list; unresolved physical locations are explicit |
| A2 | 4.0 h | Build a minimal QR/web prototype that submits one pickup identifier and shows whether the request was accepted or rejected | QR content, source code, startup instructions and a phone-to-service request log |
| A3 | 2.0 h | Define pickup-task states and the boundary between an accepted request, mapped stopping pose, planning, arrival and failure | Written task flow and unresolved decisions; no invented map coordinates |
| A4 | 3.0 h | Prepare the navigation software structure and recorded-data or test-map replay needed later for global planning and obstacle handling | Versioned source/configuration and reproduction note; no claim of real navigation success |
| AB | 2.0 h | Agree pickup-request, pose, obstacle and localization-health boundaries with B | One shared interface note; exact fields remain undecided until both implementations agree |
| AC | 2.0 h | Agree the high-level motion-command, stop and vehicle-status boundary with C | Shared behavior note; measured units and timing remain explicit dependencies |
| A5 | 2.0 h | Record tests, review another member's interface note and update unresolved actions | Review and test records linked to source versions |

The phone QR path and onboard-camera path are independent. Scanning a pickup QR does not provide the vehicle pose. A visual place label does not establish metric `(x, y, yaw)`.

## 4. B: camera AI, Pi and lidar baseline — 16 hours

| ID | Time | Task | Completion evidence |
|---|---:|---|---|
| B1 | 1.5 h | Record the requirements for a usable monocular camera and establish that no unit is currently available; leave exact model, interface and mounting data unresolved until evidence or a purchasing decision exists | Traceable requirement and availability record; no inferred model |
| B2 | 2.0 h | Define image acquisition, labelling and session-separated training/validation rules for reference place or map-region recognition | Written rules covering place/region, session, viewpoint, orientation, lighting and held-out runs |
| B3 | 3.0 h | Record the Pi/A2M8 connection; acquire, save, stop and reacquire real stationary scans, including response to a moved test object | System/connection record, raw scans, timestamps, operating duration and restart instructions |
| B4 | 3.0 h | Prepare the AI training environment and dataset-manifest structure without claiming a trained localization model | Versioned dependencies, loader/manifest checks and reproducible environment instructions |
| B5 | 2.5 h | Prepare lidar mapping/localization software and recorded-scan replay without claiming a real map or localization pass | Versioned configuration and replay evidence |
| AB | 2.0 h | Agree pickup-request, pose, obstacle and localization-health boundaries with A | Same shared interface note counted for B's time |
| BC | 1.5 h | Agree motion-feedback and localization-input requirements with C | Shared note covering required feedback, timestamps, units, heartbeat, timeout and faults; undecided parameters remain explicit |
| B6 | 0.5 h | Record results and next failures in the repository | Test record linking evidence and outstanding actions |

Do not power or move the vehicle during stationary scan work unless the corresponding power and movement prerequisites have been completed and the session is explicitly coordinated.

## 5. C: STM32 and vehicle baseline — 16 hours

The existing NUCLEO-F103RB project, compilation/flashing workflow, USART2 interrupt reception and standalone `PING`/`PONG` diagnostic test are retained. Do not repeat project creation as a new task.

| ID | Time | Task | Completion evidence |
|---|---:|---|---|
| C1 | 3.0 h | Resolve the confirmed 3.5V battery condition through the matching NiMH charging/replacement process and recorded voltage checks; only then restore the original receiver-to-servo and receiver-to-TBLE-04S connections and perform a raised-wheel radio test | Battery and wiring evidence plus neutral, steering, low-speed forward, stopping and reverse observations; invalid voltage or unresolved polarity stops movement work |
| C2 | 3.0 h | Configure and measure STM32 control pulses with the servo and ESC isolated | `.ioc` and source changes, build/flash record, instrument traces or measured periods/pulse widths, and safe startup output |
| AC/BC | 2.0 h | Agree high-level motion commands, localization input requirements, STM32 feedback, heartbeat, timeout and fault behavior with A and B | Shared interface note; verified diagnostic settings remain distinguished from future vehicle-control messages |
| C3 | 3.5 h | Prepare verified electrical/interface records and initial acquisition work for SEN0253 and the two SHARP sensors; prepare the OPB815WZ timer/input design without claiming a speed result before delivery | Supply/level checks, intended peripherals, actual sensor records and explicit photointerrupter dependency; no unsupported pin assignment |
| C4 | 2.0 h | Define and implement the first stop-priority and command-timeout behavior with actuators isolated | Source, build/flash record and a timed test showing the safe output after command loss |
| C5 | 1.5 h | Perform the first Pi–STM32 `PING`/`PONG`, disconnect and reconnect test using the actual enumerated interface | Matching logs from both endpoints and restart evidence |
| C6 | 1.0 h | Record results, review another member's interface note and update unresolved actions | Test record linking firmware version, evidence and outstanding actions |

Do not connect the receiver and STM32 outputs directly to the same servo or ESC control input. Floor movement begins only after stopping has passed with the driven wheels raised.

## 6. Shared handovers

| Handover | Owner pair | Required content |
|---|---|---|
| Pickup and navigation task | A/B | Pickup identifier, mapped stopping pose, request acceptance/rejection, task state, duplicate-request behavior and network failure behavior |
| Localization output | B/A | Planar pose, visual place/region and confidence, timestamp, pose quality, validation conditions and rejection behavior |
| Vehicle control | A/C with B's localization requirements | Target motion, stop priority, heartbeat, timeout, feedback units, timestamps, faults and reconnection behavior |
| Power and vehicle access | A/B/C | Actual supply branches, isolation, who has the vehicle, permitted movement state and handover time |

Exact message identifiers, field names, units, update rates, timeout values and wiring must be agreed from the implementations and measurements. This plan does not predefine them.

## 7. Exit criteria

This cycle is complete only when all three baseline paths have reproducible evidence:

- A: one location-specific QR reaches the request service from a phone and returns an explicit result; task-state and navigation preparation are reproducible.
- B: camera absence and requirements are recorded, image/training rules and the AI environment are reproducible, and real A2M8 data is acquired, saved, stopped, reacquired and replayed from written instructions.
- C: battery voltage is resolved before movement, the original radio path demonstrates controlled raised-wheel movement and reliable stopping, isolated STM32 output work has a recorded state, and Pi–STM32 diagnostics have endpoint logs.
- A/B and high-level/low-level vehicle interface notes identify the information crossing each boundary and explicitly retain undecided parameters.

If a prerequisite is missing, record the stopping point and next action. Preparation, compilation, a web page opening, device detection or one successful message does not establish the complete function.
