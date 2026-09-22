# Autonomous Taxi: Cycle 1 Task Board

Updated: 2026-09-22. This board maps the current two-week allocation to the active GitHub issues. Detailed task definitions and completion criteria remain in [the current work cycle](CURRENT_WEEK_TASKS_EN.md); the complete three-month schedule is in [the overall project plan](TAXI_TT02_PROJECT_WORK_PLAN_EN.md).

## Active issues

| Cycle | Member | GitHub issue | Responsibility | Planned work | Buffer | State at update |
|---|---|---|---|---:|---:|---|
| 1, Weeks 1–2 | A | [#7](https://github.com/mzy410104-lgtm/auto_car/issues/7) | Pickup service and navigation preparation | 16 h | 4 h | Open |
| 1, Weeks 1–2 | B | [#8](https://github.com/mzy410104-lgtm/auto_car/issues/8) | Camera AI, Raspberry Pi and lidar baseline | 16 h | 4 h | Open |
| 1, Weeks 1–2 | C | [#9](https://github.com/mzy410104-lgtm/auto_car/issues/9) | STM32 and vehicle baseline | 16 h | 4 h | Open |

Member C is the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm). Member A and Member B names and GitHub accounts have not been confirmed, so they are not assigned to inferred accounts.

## Cycle 1 objective

Establish three independent, reproducible baselines:

1. A phone submits one fixed-pickup identifier through the QR/web prototype.
2. The Raspberry Pi acquires and saves real RPLIDAR A2M8 scans and can restart acquisition from written instructions.
3. The vehicle safely demonstrates the original raised-wheel radio-control path after the confirmed 3.5 V battery condition has been resolved, while isolated STM32 control and safety work continues.

Each issue contains its task checklist, allocated hours, safety constraints and required evidence. GitHub issue state is the day-to-day progress record; this file only maintains the exact mapping.

## Shared handovers

| Boundary | Participants | Cycle 1 result |
|---|---|---|
| Pickup request and localization | A/B | Agree the pickup identifier, mapped stopping pose, task state, localization health and rejection behavior. |
| Navigation and vehicle control | A/C | Agree target motion, stop priority, vehicle status and failure behavior. |
| Localization and motion feedback | B/C | Agree feedback requirements, timestamps, units, heartbeat, timeout and fault behavior. |
| Vehicle access and power | A/B/C | Record the active supply, isolation, permitted movement state and vehicle handover. |

Exact message identifiers, field names, units, update rates, timeout values, wiring and pin assignments must come from implementation agreement and measurements. They are not inferred by this board.

## Superseded issues

The six earlier foundational issues were closed on 2026-09-22 after the project adopted camera map-region recognition, continuous lidar-based pose and fixed-pickup QR requests:

- [#1 — LOCAL-001 Requirements and Resource Record](https://github.com/mzy410104-lgtm/auto_car/issues/1)
- [#2 — LOCAL-002 Power Record](https://github.com/mzy410104-lgtm/auto_car/issues/2)
- [#3 — LOCAL-003 Original Radio Control and Stopping](https://github.com/mzy410104-lgtm/auto_car/issues/3)
- [#4 — LOCAL-004 Pi and Lidar Reproduction Material](https://github.com/mzy410104-lgtm/auto_car/issues/4)
- [#5 — LOCAL-005 STM32 and Communication Material](https://github.com/mzy410104-lgtm/auto_car/issues/5)
- [#6 — LOCAL-006 Speed-Sensing Component Acquisition Arrangements](https://github.com/mzy410104-lgtm/auto_car/issues/6)

Their history remains available for traceability. Open work from those records is represented in Issues #7–#9 where it remains applicable.

## Evidence rules

- A commit establishes a file change; it does not establish that a hardware test passed.
- Record source versions, actual wiring, supply conditions, instruments, test actions, raw evidence, results, time spent and unresolved items.
- Treat documentation, compilation, flashing, communication, actuator behavior and complete system behavior as separate results.
- Do not report camera localization, lidar localization, autonomous actuator control or floor-level autonomous driving as completed during Cycle 1 without separate real evidence.
- Invalid propulsion-battery voltage or unresolved polarity stops movement work. Keep the receiver and STM32 from driving the same servo or ESC input simultaneously.
