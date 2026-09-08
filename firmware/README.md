# STM32 Project Entry Point

This directory defines the firmware location in the repository. On 2026-09-08, the owner confirmed that no STM32 project has been created yet. The directory currently contains this README only; it does not provide a buildable or flashable program. The firmware already stored on the physical board, if any, remains unverified.

Owner: C, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), responsible for STM32 and interfaces. The main current task is [LOCAL-005 / Issue #5](https://github.com/mzy410104-lgtm/auto_car/issues/5). Record the actual toolchain and versions, target NUCLEO-F103RB board, build/flashing methods and existing board firmware state before the first flash. Obtain pins, clocks, peripherals and communication parameters from verified board documentation and the agreed design.

Add generated-file ignore rules once the real build directories are confirmed. Update the [interface agreement](../interfaces/CONTROL_INTERFACE.md) when interfaces change, and save measured results in [test records](../tests/records/README.md).

## Current work sequence

Follow the [current work cycle plan](../CURRENT_WEEK_TASKS_EN.md) for task hours. This checklist adds no extra allocation.

1. **C1 — Establish the starting conditions.** Record installed development tools and versions, actual MB1136 power/jumpers, target-chip power and interface recognition. Coordinate board handover with A. An absent source project does not establish that erasing the board is appropriate.
2. **C2 — Agree the Pi–STM32 interface with B.** Record the physical connection, voltage levels, actual pins, communication settings, units, command expiry and recovery behavior. Keep unspecified values blank until their source or design decision is established.
3. **C3 — Create the first minimal project.** Use NUCLEO-F103RB and the verified development tools. Implement the agreed minimal communication, compile it, then flash and check execution/restart once power, board-state and programming prerequisites are met. Record build, flash verification and observed execution separately.
4. **AC — Check existing radio control and stopping with A.** Keep receiver and STM32 outputs separate. Inspect signal-loss outputs with actuation isolated before controlled suspended-wheel tests. Schedule this separately from scans and BC work.
5. **BC — Test both communication directions with B.** Reserve the Pi and NUCLEO together; isolate actuators. Match transmitted and received data from both endpoints and test disconnection, timeout and recovery.
6. **C4 — Prepare sensor interfaces.** Check SEN0253 power/I²C pull-ups and the two SHARP sensors' power/ADC conditions. This cycle covers preparation before connection; actual acquisition follows at the next stage. This document work may run in parallel when it does not occupy shared equipment.
7. **C5 — Commit the project and evidence.** Save actual source/configuration, build and operating records, the shared interface agreement and both-end logs. Record missing evidence and the next action.

Later STM32 responsibilities include sensor acquisition, OPB815WZ pulse counting, calibrated speed feedback, ESC/servo control, speed PID, and stop/takeover handling. A handles mechanical speed-sensor parts with C providing interface requirements; B handles map localization and route planning. Single-photointerrupter speed magnitude and direction inferred from control state remain distinct.
