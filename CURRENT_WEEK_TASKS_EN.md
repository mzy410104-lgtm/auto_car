# Autonomous Taxi: Current Work Cycle

Revision date: 2026-09-22. This cycle replaces the earlier allocation after adoption of visual map-region constraints, continuous lidar-based pose and fixed-pickup QR requests.

## 1. Objective

Establish three independent baselines that can later be integrated:

1. A phone can submit one fixed-pickup identifier through a QR/web prototype.
2. The Raspberry Pi can acquire and save real RPLIDAR A2M8 scans with reproducible restart instructions.
3. The original radio-control path can safely demonstrate neutral, steering, low-speed forward, stopping and reverse with the vehicle secured and its wheels raised.

The camera model, complete lidar localization, autonomous actuator control and floor-level autonomous driving are later-stage results. Do not record them as completed in this cycle unless separate real evidence exists.

## 2. Capacity and ownership

Each member has approximately 10 hours for a full workweek. Allocate 8 hours to the tasks below and retain 2 hours for debugging, review and unexpected hardware access limits.

| Member | Revised responsibility | Planned work | Buffer | Total |
|---|---|---:|---:|---:|
| A | Camera, visual-place data, fixed-pickup QR and user web flow | 8 h | 2 h | 10 h |
| B | Raspberry Pi, lidar, mapping/localization preparation and high-level interfaces | 8 h | 2 h | 10 h |
| C | STM32, radio/actuator control, sensors, motion feedback and safety | 8 h | 2 h | 10 h |

C is the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), and owns the STM32 endpoint. A/B names and GitHub accounts remain unconfirmed and must not be inferred.

## 3. A: camera and fixed-pickup service — 8 hours

| ID | Time | Task | Completion evidence |
|---|---:|---|---|
| A1 | 1.0 h | List the intended fixed pickup points and assign project-defined identifiers without map coordinates yet | Reviewed pickup list; unresolved physical locations are explicit |
| A2 | 1.0 h | Establish whether a usable monocular camera is already available; record its exact markings, interface, lens/field-of-view information from its source, and mounting constraints | Photographs or purchasing evidence and a traceable camera record; no inferred model |
| A3 | 1.5 h | Define image acquisition and labelling rules for reference place or map-region recognition | Written rules covering place/region label, recording session, viewpoint, orientation and lighting; validation runs are separated from training sessions |
| A4 | 3.0 h | Build a minimal QR/web prototype that submits one pickup identifier and shows whether the request was accepted or rejected | QR content, source code, startup instructions and a phone-to-service request log |
| AB | 1.0 h | Agree the pickup-request and visual-output boundaries with B | One shared interface note: pickup identifier and task state; visual place/region and confidence. Exact fields remain undecided until both implementations agree |
| A5 | 0.5 h | Record results and next failures in the repository | Test record linking evidence and outstanding actions |

The phone QR path and onboard-camera path are independent. Scanning a pickup QR does not provide the vehicle pose. A visual place label does not establish metric `(x, y, yaw)`.

## 4. B: Pi and lidar baseline — 8 hours

| ID | Time | Task | Completion evidence |
|---|---:|---|---|
| B1 | 1.5 h | Record the actual Pi system, available storage, A2M8 adapter and physical connection used for the test | Commands, outputs, connection photograph and power condition |
| B2 | 2.0 h | Acquire and save real A2M8 scans while the vehicle is stationary and secured | Raw scan or recording, timestamps, operating duration and a visible response to a moved test object |
| B3 | 1.0 h | Stop and restart acquisition using written instructions | Reproduction steps and logs from both runs |
| B4 | 1.5 h | Prepare mapping/localization software and recorded-data replay without claiming real mapping success | Versioned configuration, dependency record and replay result |
| AB | 1.0 h | Agree pickup-request and visual-output boundaries with A | Same shared interface note counted for B's time |
| BC | 1.0 h | Agree the navigation-control and motion-feedback boundary with C | One shared interface note covering intended command, feedback, heartbeat, timeout and fault semantics; undecided parameters remain explicit |

Do not power or move the vehicle during stationary scan work unless the corresponding power and movement prerequisites have been completed and the session is explicitly coordinated.

## 5. C: STM32 and vehicle baseline — 8 hours

The existing NUCLEO-F103RB project, compilation/flashing workflow, USART2 interrupt reception and standalone `PING`/`PONG` diagnostic test are retained. Do not repeat project creation as a new task.

| ID | Time | Task | Completion evidence |
|---|---:|---|---|
| C1 | 2.0 h | Restore the original receiver-to-servo and receiver-to-TBLE-04S connections from actual connector markings and official manuals; perform a raised-wheel radio test | Wiring evidence plus neutral, steering, low-speed forward, stopping and reverse observations; unresolved polarity or pin labels stop connection work |
| C2 | 2.0 h | Configure and measure STM32 control pulses with the servo and ESC isolated | `.ioc` and source changes, build/flash record, instrument traces or measured periods/pulse widths, and safe startup output |
| BC | 1.0 h | Agree the Pi–STM32 command and feedback boundary with B | Same shared interface note counted for C's time; the verified diagnostic serial settings remain distinguished from the future vehicle-control protocol |
| C3 | 1.5 h | Prepare verified interface records for the OPB815WZ, SEN0253 and two SHARP sensors using actual hardware and source documents | Connection requirements, supply and level checks, intended STM32 peripherals and unresolved measurements; no unsupported pin assignment |
| C4 | 1.0 h | Define and implement the first stop-priority and command-timeout behavior with actuators isolated | Source, build/flash record and a timed test showing the safe output after command loss |
| C5 | 0.5 h | Record results and next failures in the repository | Test record linking firmware version, evidence and outstanding actions |

Do not connect the receiver and STM32 outputs directly to the same servo or ESC control input. Floor movement begins only after stopping has passed with the driven wheels raised.

## 6. Shared handovers

| Handover | Owner pair | Required content |
|---|---|---|
| Pickup request | A/B | Pickup identifier, request acceptance/rejection, task state, duplicate-request behavior and network failure behavior |
| Visual localization | A/B | Place or map-region result, confidence meaning, timestamp, validation conditions and rejection behavior |
| Navigation control | B/C | Target motion, stop priority, heartbeat, timeout, feedback units, timestamps, faults and reconnection behavior |
| Power and vehicle access | A/B/C | Actual supply branches, isolation, who has the vehicle, permitted movement state and handover time |

Exact message identifiers, field names, units, update rates, timeout values and wiring must be agreed from the implementations and measurements. This plan does not predefine them.

## 7. Exit criteria

This cycle is complete only when all three baseline paths have reproducible evidence:

- A: one location-specific QR reaches the request service from a phone and returns an explicit result.
- B: real A2M8 data is acquired, saved, stopped and reacquired from written instructions.
- C: the original radio path demonstrates controlled raised-wheel movement and reliable stopping, and isolated STM32 output work has a recorded state.
- A/B and B/C interface notes identify the information crossing each boundary and explicitly retain undecided parameters.

If a prerequisite is missing, record the stopping point and next action. Preparation, compilation, a web page opening, device detection or one successful message does not establish the complete function.
