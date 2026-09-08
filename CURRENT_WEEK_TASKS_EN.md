# Autonomous Taxi: Current Work Cycle Plan (Revised)

Revision date: 2026-09-08. Basis: [Architecture notes](TAXI_TT02_ARCHITECTURE_NOTES_EN.md), existing hardware, and the [step-by-step verification procedure](TAXI_TT02_VERIFICATION_STEPS_EN.md).

**Objective for this work cycle: obtain actual records of power supply checks, stopping with the original radio control, real lidar data, STM32 operation, and bidirectional communication, and arrange acquisition of the speed-sensing components.**

This version covers one full working week: 8 hours of planned tasks and 2 hours of debugging buffer per person, for 24 + 6 = 30 person-hours in total. This is an effort budget, not a promise that every test will pass within its allocated time. The team has been asked about time already spent this week, existing test results, and the deadline; no response has been received yet. The 30 person-hours therefore cannot be treated as the time remaining this week.

See the [overall project plan](TAXI_TT02_PROJECT_WORK_PLAN_EN.md) for the full cycle. `sources/planning/CURRENT_WEEK_TASKS_ZH_before_replan_2026-09-08.md` is retained as a local historical archive; use this file for current execution.

## 1. Changes in This Revision and Work Already Completed

- The architecture diagram and hardware inventory are complete. This work cycle records only differences in the actual vehicle wiring; it does not redraw the architecture, repeat full hardware selection, or reconfirm the SD card, data cables, and handheld transmitter already available.
- Retain the TT-02, Pi4, NUCLEO-F103RB, A2M8, SEN0253, two SHARP sensors, TBLE-04S, and the existing drive and power components.
- The repository owner confirmed responsibility for STM32 (role C) and that no STM32 project has been created yet. C starts with development-tool and board checks, then creates the first minimal project. This does not establish whether the board already contains firmware.
- Speed sensing still uses one perforated transmission gear, one dedicated gear cover, and one OPB815WZ photointerrupter. No update on delivery or installation has been received. Do not return to the shaft-hole or dual-photointerrupter designs, and do not purchase a stereo camera.
- Do not ask again for the motor or servo model, battery capacity, or charger model that the user has already said cannot be confirmed.
- The joint kickoff and review each last 30 minutes, totaling 3 person-hours across all three members; the previous version allocated 6 person-hours to these sessions.
- This work cycle focuses on the basic system connections. For the IMU and SHARP sensors, check the interfaces first and move actual data acquisition to the next stage. Driving on the floor, closed-loop speed control, and complete navigation are not unconditional deliverables for this work cycle.
- Mark items whose measured results have not been received as "pending evidence"; this does not establish that the team has never tested them. Record instrument, room, and equipment availability as it actually stands.

## 2. Effort Summary

A/B/C are responsibility labels. C is the repository owner, [mzy410104-lgtm](https://github.com/mzy410104-lgtm), who confirmed responsibility for STM32. A/B members and their GitHub accounts remain to be confirmed. The task IDs below are newly defined for this version and do not retain the meanings of IDs in the previous version.

| Member | Individual and two-person tasks | Joint kickoff | Joint review | Planned total | Debugging buffer | Full-week limit |
|---|---:|---:|---:|---:|---:|---:|
| A: Power and mechanics | 7 h | 0.5 h | 0.5 h | 8 h | 2 h | 10 h |
| B: Pi and lidar | 7 h | 0.5 h | 0.5 h | 8 h | 2 h | 10 h |
| C: STM32 and interfaces | 7 h | 0.5 h | 0.5 h | 8 h | 2 h | 10 h |
| Total | 21 person-hours | 1.5 person-hours | 1.5 person-hours | 24 person-hours | 6 person-hours | 30 person-hours |

AB, AC, and BC each involve 1 hour of joint work, or 2 person-hours per session, already included in each participant's 7 hours. The 0.5 hour in C2 and B3 is the same interface discussion and is also included for both participants. Additional assistance, preparation, and handover must be charged to a task or the buffer.

## 3. Joint Kickoff: 30 Minutes per Member

| Duration | Action | Record |
|---|---|---|
| 10 minutes | Credit existing tests and record each person's time already spent and remaining this week | Passed with records; performed but pending evidence; tasks awaiting execution |
| 10 minutes | Confirm instrument and room status and equipment handovers; allocate time for the single vehicle, Pi, and NUCLEO | Actual resources and owners of unresolved arrangements |
| 10 minutes | Record key requirements and assign verification: destination input, initial position, arrival, stopping/detouring, course requirements, and deadline | Retain the original objective; leave undecided criteria pending confirmation |

These 30 minutes do not include room measurements that have not yet taken place. Once the room is available, A schedules the measurements and charges the time to their tasks or debugging buffer.

## 4. A: Power and Mechanical Component Acquisition, 7 Hours

| ID | Task | Time | Work and deliverable | Prerequisites / handling deferral |
|---|---|---:|---|---|
| A1 | Trace wiring with power disconnected | 0.75 h | Shut down normally, disconnect all power sources, take labeled photos, and trace the battery-main switch-ESC/LM2596S paths and their output loads to produce an actual vehicle wiring record | Exclusive use of the vehicle; no one else powers it on during this task; follow verification procedure Step 1 |
| A2 | Power requirements and instruments | 0.75 h | Check polarity, permitted supply conditions, BEC/receiver paths, and measurement points; record instruments and borrowing arrangements | Measurements remain pending if suitable instruments are unavailable; do not substitute trial connection of a load for measurement |
| A3 | No-load voltages and main switch | 1 h | Isolate the step-down converter output and the ESC battery input; measure the battery, LM input/output, and readings with the switch off | A1/A2 prerequisites met; follow procedure Step 2; record readings before adjusting voltage and do not claim a loaded test has passed |
| AB | Add loads progressively with B | 1 h | Connect loads one at a time through verified paths, measure voltage, and record software and power behavior | No-load targets and B's standalone prerequisites established; disconnect power before every wiring change and isolate unverified branches |
| AC | Check original radio control and stopping with C | 1 h | Check paired equipment/wiring, neutral, and basic actions; for signal loss, first isolate actuator movement and read the output, then perform controlled checks with the wheels raised once the behavior is clear | Follow procedure Step 5 with power, operating, and instrument prerequisites established; if incomplete, record the actual scope and do not proceed to floor movement |
| A4 | Acquire speed-sensing components | 1.5 h | 0.5 hour to organize official documents and installation records; 0.5 hour for a team member to submit requirements to the supplier/workshop; 0.5 hour to review actual replies, quotations, lead times, and follow-up | Submit early; do not spend the whole allocation waiting for replies; record inquiry, order, and delivery separately |
| A5 | Records and handover | 1 h | Consolidate the wiring version, measurements, radio-control results, and procurement status; hand over verified power paths and identify branches not yet connected | Includes equipment handover; save failed results and the next action as well |
| Total | | 7 h | Add 1 hour for the joint kickoff/review and 2 hours of buffer, totaling 10 hours | |

The 1 hour for AC is this work cycle's effort allocation; it does not require all movement and signal-loss tests to be completed within that hour. If stopping has not passed, prioritize the buffer and defer driving on the floor. This assistant does not send external messages or place orders on the team's behalf.

## 5. B: Pi, Lidar, and Communication, 7 Hours

| ID | Task | Time | Work and deliverable | Prerequisites / handling deferral |
|---|---|---:|---|---|
| B1 | Record the system and existing projects | 0.5 h | Use the existing SD card; record the actual system, software, projects, and boot behavior; preserve existing material | Pi handed over and power verified; while A traces wiring, perform only preparation that requires no power; do not reimage by default |
| B2 | Acquire and reproduce real lidar data | 2.5 h | Check the adapter and acquire real scans; move a cardboard sheet and observe the corresponding changes; stop and restart acquisition; save logs/video and durations | Standalone power verified; vehicle secured, with no movement or rewiring by others; simulation does not replace measurement |
| B3 | Prepare host communication | 1.5 h | 0.5 hour to agree the interface with C and 1 hour to prepare transmission, reception, numbering, and logging | Determine parameters from the actual project/connections; do not assume serial-port names, pins, baud rate, or message fields |
| AB | Add loads progressively with A | 1 h | Observe Pi/lidar operation and contribute to the power records | Same AB session as in A's table; record results after a power-source change separately |
| BC | Bidirectional communication with C | 1 h | Verify matching send/receive records for the same data batch separately in each direction, check disconnection, timeout, and recovery, and save logs from both ends | B3/C3 ready; connection voltage levels and power verified; exclusive use of Pi/NUCLEO with actuators isolated |
| B4 | Reproduction instructions and handover | 0.5 h | Save actual configurations/commands, data locations, power conditions, and failure points | System detection does not mean communication or scanning has passed |
| Total | | 7 h | Add 1 hour for the joint kickoff/review and 2 hours of buffer, totaling 10 hours | |

## 6. C: STM32 and Interfaces, 7 Hours

| ID | Task | Time | Work and deliverable | Prerequisites / handling deferral |
|---|---|---:|---|---|
| C1 | Development tools, board, and existing firmware state | 1 h | Record the actual development tools and versions; check MB1136 power configuration/jumpers, target STM32 power and interface detection; record any known firmware already on the board and its recovery information. No existing STM32 project is available to import | Power on only after A has completed and handed over the relevant records made with power disconnected; do not treat the absence of a source project as proof that the board is blank |
| C2 | Agree the communication interface with B | 0.5 h | Specify the physical interface, actual connections, voltage levels, parameters, information/units, and failure/recovery behavior | Same discussion as the 0.5 hour within B3; do not guess exact values when information is insufficient |
| C3 | Create the first minimal project and run it standalone | 1.5 h | Create a NUCLEO-F103RB project with the verified tools; implement and compile minimal transmission/reception using the agreed interface; once board-state and flashing prerequisites are met, flash it, observe operation, and reproduce it after a restart | Complete C1 and the C2 agreement first. Flash verification does not prove operation; use the buffer or defer if setup exceeds the allocation; do not erase or unlock an unknown original program |
| BC | Bidirectional communication with B | 1 h | Same BC session as B's; record actual transmission/reception and disconnection/recovery; record separately when USB disconnection causes a reset | Programs at both ends, wiring, voltage levels, and power established; a self-test at one end does not count as a passed integration test |
| AC | Check original radio control and stopping with A | 1 h | Same AC session as A's; handle signal documentation and stopping/recovery records, keeping receiver and STM32 outputs separate | Do not connect unknown signals to an unverified interface; do not claim automatic takeover is complete in this work cycle |
| C4 | Prepare IMU and SHARP interfaces | 1 h | Check the actual hardware versions and record SEN0253 power/I²C pull-up conditions, SHARP power/ADC conditions, and missing information | Follow procedure Steps 7/8; review only before connection and move acquisition to the next stage |
| C5 | Project and interface handover | 1 h | Save build/flashing/operation evidence, the actual interface agreement, and logs; list next-cycle actions | Record actual parameter values and their sources, and retain reasons for items that have not passed |
| Total | | 7 h | Add 1 hour for the joint kickoff/review and 2 hours of buffer, totaling 10 hours | |

## 7. Execution Order for the Single Vehicle, Pi, and NUCLEO

The following is a dependency order, not a list of booked dates. Fill in shared times at the kickoff meeting.

1. **A first traces the wiring with power disconnected.** B/C prepare documentation without disturbing that disconnected state; boards whose isolation has not been confirmed must not be powered independently.
2. **Perform standalone tests after handover.** If verified, mutually disconnected independent power supplies are available, B tests Pi/lidar while C tests NUCLEO; otherwise work sequentially. A can prepare procurement/workshop material in parallel.
3. **Secure the vehicle during B2 scans.** Do not schedule radio-controlled movement, gear removal/installation, or rewiring of the same vehicle.
4. **Use a dedicated AB session to check electronics power.** A measures the supply and B observes loads; C does not alter related wiring at the same time.
5. **Use a dedicated AC session to check original radio control.** B stops scanning and wiring work on the vehicle; independent software preparation away from the vehicle may continue. First check signal-loss outputs with actuator movement isolated, then arrange controlled movement with the wheels raised.
6. **Use a dedicated BC session for communication.** Reserve Pi and NUCLEO exclusively and isolate actuators; A does not change related power or data wiring. C2 can take place earlier but must precede completion of the B3/C3 implementations.
7. **Archive individual work, then hold the joint review.** At handover, state the wiring, power, equipment status, and responsible person.

AB and AC may be reordered according to resources when they have no direct dependency, but scanning and movement windows always remain separate. If prerequisites are missing, switch to fault diagnosis; do not skip prerequisite checks to save time.

## 8. Six Deliverables and Completion Criteria

| Deliverable | Responsibility | Evidence to retain | If prerequisites are missing |
|---|---|---|---|
| Requirements and resource record | All three members | Credit for existing results, remaining time, instrument/room/equipment availability, and owners of undecided requirements | Record unresolved items and the next action; do not invent dates or criteria |
| Power record | A/B | Actual wiring, no-load/switch-off readings, and progressive-load conditions and results | Record document checks, no-load tests, and loaded tests separately |
| Original radio control and stopping | A/C | Neutral, actual movement, stopping, and signal-loss/recovery records | Record only the actual scope; do not begin floor tests before stopping has passed |
| Pi and lidar reproduction material | B | Environment, adapter, real scans, cardboard response, repeated acquisition, and durations | State exactly whether work stopped at power, detection, or acquisition; distinguish bench and onboard power |
| STM32 and communication material | C/B | Recovery information, project, compilation, operation, and bidirectional/disconnection-recovery logs | Separate compilation, flashing, operation, and one-way/two-way communication; preparation does not count as a pass |
| Speed-sensing component acquisition arrangements | A | Submission records for the three components, actual replies/quotations/lead times, and the person following up | Record awaiting reply, not ordered, not delivered, and not installed separately; delivery is not a prerequisite for this work cycle |

## 9. Joint Review: 30 Minutes per Member

Use the first 15 minutes to check evidence against the six deliverables and the last 15 minutes to record actual time spent, reasons for failed items, the next action, and its owner. Do not repeat tests that are already sufficiently verified just for the review; continue to identify missing reproduction evidence explicitly.

Record template:

    Task ID, person performing the task, actual time spent:
    Current wiring, power, and equipment status:
    Actual locations of raw data, photos, logs, and projects:
    Conclusion: passed / partially passed / failed / prerequisites not met / performed but pending evidence
    Unresolved issues:
    Next action, owner, and prerequisites:

## 10. Buffer and Deferral

- Prioritize each person's 2-hour buffer for identified faults in power, stopping, real scanning, and communication; do not add new features by default.
- If the week has already started, first subtract actual time spent and credit tasks already passed. If the full table cannot fit, select task segments in prerequisite order. Deferred tasks use the next week's existing capacity, with each person's total effort still limited to 10 hours.
- If required instruments are unavailable, complete wiring tracing, document preparation, and borrowing arrangements; unperformed measurements remain pending. Software/standalone work may continue with verified independent power.
- If speed-sensing components have not arrived, advance the other basic connections. Do not substitute throttle commands for measured speed or mark speed PID or odometry as passed.
- Having only a multimeter does not establish that power transients have been ruled out; retain missing evidence for timing checks that lack waveforms.
- Decide other additional parts from actual missing items and test results; do not repurchase equipment already confirmed to be available.
- Credit completion against actual records. Writing documents, preparing purchases, or detecting a device once does not establish completion of a whole-vehicle function.

This revision updates plan files only; no suppliers have been contacted, workshops booked, orders placed, wiring changed, firmware flashed, or real-vehicle tests performed.
