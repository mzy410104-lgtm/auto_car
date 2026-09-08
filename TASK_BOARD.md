# Autonomous Taxi: Local Task Board

Created: 2026-09-08. Basis: the six deliverables in Section 8 of the [current work cycle plan](CURRENT_WEEK_TASKS_EN.md).

`LOCAL-001` through `LOCAL-006` are local task IDs defined in this file, **not remote issue numbers**. Corresponding issues have been created in [mzy410104-lgtm/auto_car](https://github.com/mzy410104-lgtm/auto_car); the mapping is shown below. C is the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), who confirmed responsibility for STM32. A/B members and their GitHub accounts remain to be confirmed. A GitHub Projects board has not yet been configured.

All six initial statuses are **pending evidence**: the corresponding results have not yet been received. This does not establish that the team has never performed the tasks. Credit existing results first, then schedule actual work.

## Usage Rules

- Suggested workflow columns: **Pending evidence, Prerequisites pending, In progress, Awaiting review, Completed**. This is a proposed team workflow, not platform configuration that has already been created. Select a status based on actual progress; do not automatically change every "Pending evidence" item to "Not started."
- **A Git commit does not mean a hardware test has passed.** Retain separate evidence for documentation, source code, compilation, flashing, actual operation, and hardware functionality. Commit records can establish file changes, but cannot replace voltage readings, real-vehicle video, or communication logs from both ends.
- Retain the completion criteria in the existing plan: record actual wiring, power, software/project locations, actions, results, raw evidence, actual time spent, and unresolved matters. Record failures and unmet prerequisites truthfully as well. Finishing a document does not automatically satisfy hardware completion criteria.
- This board adds no working hours. AB, AC, BC, and the joint B3/C2 discussion remain included in participants' time under the original plan. Do not count time again when multiple deliverables reference the same handover task.
- Separate rewiring, stationary scanning, and vehicle movement windows for the single vehicle. Reserve Pi and NUCLEO together for communication integration tests. Only boards that are actually isolated and have verified independent power may be powered in parallel.
- Advance tasks according to the specific prerequisites below; independent preparation does not require every related task to be closed first. Record standalone results using verified bench power separately from onboard-power results.

## Initial Task Overview

| Local ID | GitHub Issue | Deliverable | Owner | Current status |
|---|---|---|---|---|
| LOCAL-001 | [#1](https://github.com/mzy410104-lgtm/auto_car/issues/1) | Requirements and resource record | A/B/C | Pending evidence |
| LOCAL-002 | [#2](https://github.com/mzy410104-lgtm/auto_car/issues/2) | Power record | A/B | Pending evidence |
| LOCAL-003 | [#3](https://github.com/mzy410104-lgtm/auto_car/issues/3) | Original radio control and stopping | A/C | Pending evidence |
| LOCAL-004 | [#4](https://github.com/mzy410104-lgtm/auto_car/issues/4) | Pi and lidar reproduction material | B | Pending evidence |
| LOCAL-005 | [#5](https://github.com/mzy410104-lgtm/auto_car/issues/5) | STM32 and communication material | C/B | Pending evidence |
| LOCAL-006 | [#6](https://github.com/mzy410104-lgtm/auto_car/issues/6) | Speed-sensing component acquisition arrangements | A | Pending evidence |

## LOCAL-001: Requirements and Resource Record

- **Owner:** A/B/C; C is [mzy410104-lgtm](https://github.com/mzy410104-lgtm). A/B members remain to be confirmed.
- **Status:** Pending evidence.
- **Related plan sections:** Section 3, "Joint Kickoff," and Section 9, "Joint Review." Neither has a separate task ID in the existing plan; this board does not invent retrospective IDs for them.
- **Completion evidence:** Review and credit for existing test results and evidence; each person's actual time spent and remaining; availability and handover arrangements for instruments, the room, and the single vehicle/Pi/NUCLEO; confirmed destination, initialization, arrival, stopping/detouring, course requirements, and deadline information, or owners of unresolved items; the next action identified during review.
- **Dependencies:** Team members provide actual status and records. Unresolved items may remain open with a next action assigned. Joint discussion does not replace room measurements that have not yet been performed; do not invent dates or criteria.

## LOCAL-002: Power Record

- **Owner:** A/B.
- **Status:** Pending evidence.
- **Related plan IDs:** A1, A2, A3, AB, A5.
- **Completion evidence:** Actual wiring photos and version, branches under test and isolation methods, basis for power conditions, instruments, and measurement points; battery readings and LM2596S no-load input/output and switch-off readings; load state, power source, actual voltage, and software behavior during progressive loading; unverified branches and handover records. Record no-load, switch-off, and loaded results separately.
- **Dependencies:** First establish the equipment-use arrangements in LOCAL-001. A1 requires exclusive use of the vehicle to trace wiring with power disconnected. Perform A3 only after A2's power requirements and instrument prerequisites are established. AB requires no-load targets and B's verified standalone conditions; coordinate load and operating-status handover with LOCAL-004. Disconnect power before every wiring change.
- **If prerequisites are missing:** Preserve wiring-trace records, documentation, and instrument-borrowing arrangements; measurements remain pending. No-load readings do not prove loaded stability or the module's continuous output capability.

## LOCAL-003: Original Radio Control and Stopping

- **Owner:** A/C; C is [mzy410104-lgtm](https://github.com/mzy410104-lgtm). The A member remains to be confirmed.
- **Status:** Pending evidence.
- **Related plan IDs:** AC, A5, C5.
- **Completion evidence:** Basis for the actual paired equipment and wiring; neutral, basic movement, and stopping records; signal-loss outputs with actuator movement isolated, and the basis for stopping/recovery; controlled movement with the wheels raised and signal-loss/recovery records once prerequisites are established; actual scope passed and unresolved items.
- **Dependencies:** Relevant power, operating, and instrument prerequisites established, and handover of the corresponding LOCAL-002 branches complete. Unrelated branches do not all need to be completed first. While AC uses the vehicle, B stops onboard scanning and wiring. First check signal-loss outputs with actuator movement isolated; once behavior is clear, proceed to checks with the wheels raised. Keep receiver and STM32 outputs separate.
- **If prerequisites are missing:** Record only the actual verified scope. Do not begin floor tests before stopping has passed. This item does not establish completion of automatic takeover.

## LOCAL-004: Pi and Lidar Reproduction Material

- **Owner:** B.
- **Status:** Pending evidence.
- **Related plan IDs:** B1, B2, B4. Joint power records from AB also belong to LOCAL-002, without adding working hours.
- **Completion evidence:** Actual locations of the existing system, software, and projects; A2M8 adapter and actual connections; real scan data, video showing the response to cardboard movement, actual duration, and anomalies; results and reproduction instructions for acquisition restarted after stopping; explicit bench or onboard power conditions.
- **Dependencies:** A has completed the relevant wiring tracing with power disconnected and handed over Pi; standalone power is verified. Secure the vehicle during B2, with no vehicle movement, mechanical disassembly/assembly, or rewiring of the same vehicle. If onboard power has not yet passed, standalone tests may first use verified, physically isolated bench power.
- **If prerequisites are missing:** Record the actual point at which work stopped: power, adapter, detection, or acquisition. Preserve the existing SD card and do not reimage by default. System detection, simulated data, or a single acquisition does not replace the required reproduction evidence.

## LOCAL-005: STM32 and Communication Material

- **Owner:** C, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), for STM32; B for the Pi endpoint and joint communication work. The B member remains to be confirmed.
- **Status:** Pending evidence.
- **Related plan IDs:** C1, C2, C3, B3, BC, C5, B4.
- **Starting point:** C confirmed that no STM32 project has been created yet. Record actual development tools and the physical board's existing firmware state, then create the first minimal NUCLEO-F103RB project. No source project does not mean the board is blank.
- **Completion evidence:** Development-tool versions and board firmware/recovery information; actual hardware power and interface records; one shared interface agreement and sources for actual parameters; the newly created minimal project, compilation, flashing, operation, and restart records; matching sent/received data from both ends and disconnection, timeout, and recovery logs; actual storage locations for the project and reproduction material.
- **Dependencies:** A has completed the relevant records with power disconnected and handed over NUCLEO; standalone power and interface prerequisites are established. C2 and the 0.5 hour within B3 are the same discussion; agreement must precede completion of both implementations. Establish recovery and flashing prerequisites before flashing in C3. Enter BC once B3/C3 are ready and connections, voltage levels, and power have been verified; reserve the only Pi and NUCLEO for the session and isolate actuators.
- **If prerequisites are missing:** If the original firmware's recovery information is insufficient, preserve the original program and advance only permitted checks and preparation; do not erase or unlock it. Assess compilation, flashing, operation, one-way communication, and bidirectional communication separately. A host self-test cannot be recorded as passed communication between the two devices.

## LOCAL-006: Speed-Sensing Component Acquisition Arrangements

- **Owner:** A.
- **Status:** Pending evidence.
- **Related plan IDs:** A4, A5.
- **Completion evidence:** Requirements and official documents/installation records for one perforated transmission gear, one dedicated gear cover, and one OPB815WZ photointerrupter; actual records of a team member submitting requirements to the supplier or workshop; replies, quotations, lead times, and included items actually received; waiting status and the person following up when no reply has arrived; handover of actual acquisition status.
- **Dependencies:** Use existing official documents and actual installation records. Document preparation and submission may run in parallel with tasks that do not occupy the vehicle. Coordinate a vehicle-use window before inspecting or photographing the real vehicle; do not disassemble it during stationary scanning or movement.
- **If prerequisites are missing:** Record awaiting reply, not ordered, not delivered, and not installed separately. This work cycle does not require delivery or completed real speed measurement as a prerequisite. Do not return to the shaft-hole or dual-photointerrupter designs, and do not add stereo-camera procurement.

This file and the six GitHub issues have been created. This does not verify the six hardware or implementation outcomes. Use the issues as the source of day-to-day progress from now on; this file retains task scope, completion criteria, and links to avoid maintaining status in two places.
