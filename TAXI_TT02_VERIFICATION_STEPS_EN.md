# TT-02 Architecture Verification: Step-by-Step Procedure and Records

Date: 2026-09-08. Companion to the [completed architecture diagram](TAXI_TT02_ARCHITECTURE_EN.png).

This is a procedure awaiting execution; no measured results have been entered. The purpose of the main switch and the confirmed hardware models and quantities follow the user's confirmations. The team is not asked again to dismantle the vehicle to identify the motor or servo, or to identify the battery capacity or charger model. The user has been asked which instruments are available; no reply has been received. Follow the applicable instrument-dependent route below.

Sequence: **Record with power disconnected → No-load power checks → Individual board tests → Basic radio control → Bidirectional communication → Sensors → Speed measurement → Control and whole-vehicle integration**. Individual boards may use an already verified bench supply without waiting for every vehicle regulator issue to be resolved. Distinguish these two supply conditions in the records.

## 0. Prepare tools and a recording method

| Tool | Purpose in this work cycle | If unavailable |
|---|---|---|
| Digital multimeter and its manual | Battery/regulator output voltage and continuity checks with power disconnected | Complete photographs and document checks first; connecting equipment to an unknown supply is not a substitute for measurement |
| Insulated work surface, secure support, insulated clips and labels | Secure the vehicle and probes; label connections | Establish reliable supports first so a handheld probe cannot slip while someone operates the vehicle |
| Computer and existing data cables | Board identification, data and logs | Use the existing system and projects first; do not assume reflashing is required |
| Ruler or tape measure, cardboard and tape markers | Distance tests, installed coverage and speed calibration | Borrow these in advance if needed; no electrical wiring is involved |
| Oscilloscope or logic analyzer | Control pulses, communication and encoder waveforms | A logic analyzer cannot replace analog-voltage or supply-transient measurements; record the evidence gap for checks without waveform instruments |
| Current-limited bench supply, electronic load or suitable current-measurement equipment | Branch power, controlled load and current checks | An already verified commercial supply can support individual-module functional tests; do not declare the module's maximum-current capability verified |

For DC voltage measurements, follow the instrument manual, using voltage mode and the voltage-measurement sockets, with the probes connected in parallel across the measurement points. **Never connect a meter in current mode across a battery or supply output. Resistance/continuity checks require all power to be disconnected and stored energy to be discharged.** This procedure does not call for stalling a motor or servo to measure current. [Fluke DC voltage measurement instructions](https://www.fluke.com/en-ie/learn/blog/digital-multimeters/how-to-measure-dc-voltage-with-a-digital-multimeter)

For each record, enter the date, operator, task, equipment and wiring photographs, supply source, measurement points, load condition, actual results, log/video locations, conclusion and next step. Use the conclusions "Pass", "Partial pass", "Fail" or "Prerequisites not met". A result that has not been received does not mean the test has never been performed.

## 1. Photograph and trace wiring with all power disconnected

Prerequisites: shut down the Raspberry Pi normally and disconnect the battery, computer USB and every other external supply. Preserve the current project and wiring information.

1. Photograph the whole vehicle from above, the lower power/ESC area, and the connectors and jumpers on every board. The photographs must allow both ends of each wire to be identified.
2. Attach removable connector labels and record the actual source and destination of each connection. Record before unplugging or reconnecting; do not infer function from wire color.
3. Trace the battery connector to the main switch, then trace the ESC input and LM2596S input separately.
4. Record each wire against the actual buck-board markings `IN+`, `IN-`, `OUT+` and `OUT-`. These four markings are visible in earlier user photographs; identify them again on the current physical board when measuring.
5. Trace the devices actually connected to the LM2596S output. Separately trace the power branch in the ESC receiver lead and the servo supply. Do not treat two positive supply outputs as suitable for parallel connection.
6. Check exposed copper, loose connectors and wires pinched by steering or transmission parts. Leave a power branch disconnected when its destination or polarity is unsupported by evidence.
7. If continuity mode is needed to identify a wire, disconnect every supply and isolate that wire from electronic circuits first. Capacitor charging and parallel paths affect readings across a whole board; a single beep does not establish a board short circuit.

Deliverable:

| Actual source marking | Actual destination marking | Power / signal / ground | Photograph location | Unresolved item |
|---|---|---|---|---|
| To be recorded | To be recorded | To be recorded | To be recorded | To be recorded |

Proceed when both ends of the branch under test, the basis for its polarity and the method of isolating its loads are clear.

## 2. Measure the battery, main switch and unloaded buck-converter output

Prerequisites: the branch under test has been checked in Step 1. Disconnect all loads from the buck-converter output and disconnect the ESC battery-input branch. Retain only the battery–main-switch–buck-converter branch under test. Use a digital multimeter and verify DC voltage mode, sockets and range against its manual.

1. Measure the voltage at the battery connector. Record the value, sign and corresponding probe positions. For a digital voltage measurement, a positive reading means the red-probe point is at a higher potential than the black-probe point; wire colors cannot replace this record. 7.2V is the nominal rating, not a requirement to read exactly 7.20V now.
2. Check how the main switch is connected in the supply circuit and the source of its DC load rating. A continuity check cannot establish an unknown switch's rated capability.
3. Keep the electronic loads disconnected and connect the verified battery–switch–buck-converter branch. Secure the measurement clips before powering it, then complete the table below.
4. Record the present buck-converter output before turning the adjustment potentiometer. If adjustment is needed, first establish the allowed conditions for every load on that branch. Adjust according to the actual module circuit with loads disconnected, then measure again.
5. Turn off the main switch and observe the buck-converter input and output voltages. Output capacitors retain charge; record the decay over time. If computer USB or another supply is connected, this does not test whether the battery main switch has disconnected every power source.
6. If power remains continuously present after switching off, disconnect power and trace any bypass or other supply source. Do not connect loads if polarity or voltage conflicts with the design.

| Condition | Red-probe point | Black-probe point | Actual reading |
|---|---|---|---|
| Battery measured separately | Verified battery positive terminal | Verified battery negative terminal | To be measured |
| Main switch on, buck converter unloaded | `IN+` | `IN-` | To be measured |
| Main switch on, buck converter unloaded | `OUT+` | `OUT-` | To be measured |
| Main switch off, no other supply | `IN+` | `IN-` | To be measured |
| Main switch off, no other supply | `OUT+` | `OUT-` | To be measured, including elapsed time |

Proceed when unloaded voltage and polarity match the established target and the shutdown path can be explained. **This does not establish stability under load or continuous 3A capability for the complete module.** The LM2596 chip specification does not replace the actual module's thermal and supporting-component limits. [TI LM2596 documentation](https://www.ti.com/product/LM2596)

## 3. Perform separate minimal power-up tests on the Raspberry Pi and NUCLEO

### 3A. Raspberry Pi

1. Select an already verified supply and USB-C power cable. Use the existing bootable SD card; leave the lidar, STM32, sensors and ESC disconnected.
2. Power up and record whether the existing system starts. Save the system version, existing project location and any power-related warnings. Determine how to retrieve this information from the actual system; no source code or system configuration establishing the Pi startup commands has been found in the current working directory.
3. Shut down normally and start again to check reproducibility. Preserve the SD card and existing software; do not reflash them as a prerequisite for this test.
4. Record a result obtained with bench power as "Pi standalone startup passed with bench power". Repeat the check when vehicle power is used later.

Reference: the official Pi 4 recommendation is a 5.1V/3A supply. The current rating is a supply-capability reference; actual loads must still be assessed. A 5.1V reading alone does not establish an adequate supply. [Official Raspberry Pi power-supply guidance](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply)

### 3B. NUCLEO-F103RB

1. Preserve photographs of the current board wiring and the existing project/firmware information. Disconnect external loads and other supplies.
2. Check USB power selection and relevant jumpers against the physical MB1136 board and its manual. Record their actual state; the manual's default configuration does not establish this board's present configuration. Verify position and function before changing a jumper.
3. Once these conditions are established, connect only the onboard ST-LINK USB port to the computer. Record the power state and what the computer actually recognizes.
4. Check whether the target STM32 section receives power. ST-LINK recognition does not establish that the target chip is powered correctly or running.
5. If a virtual serial port appears, record its actual name. This stage establishes interface recognition only, not successful bidirectional communication.
6. Arrange compilation, flashing, execution and a repeat after restart only once the existing program's recovery basis, target project, actual connection and programming tool are established. Do not erase or unlock the chip to bypass an unknown original-program state.

Reference: UM1724 Rev17, §7.4, §7.5.1 and §7.10. USB board power has its own enumeration and current limits; the Raspberry Pi USB port's capability is not automatically the NUCLEO sensor power budget. [ST MB1136 manual](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf)

## 4. Connect the lidar and verify the electronics load in stages

1. Photograph both sides of the A2M8 adapter, its connectors and current cable harness. Find interface documentation matching the actual hardware. Having enough data cables does not replace this adapter check.
2. Verify lidar and adapter power sources, polarity and data connections. Make connections with power disconnected. Do not directly parallel an additional 5V supply with the USB power output.
3. Connect the lidar under the already verified Pi power conditions. Record system recognition first, then start acquisition using existing compatible software. Determine the actual program and parameters by reading the current system/project.
4. Secure the lidar and vehicle. Move cardboard within the scan plane and save a video linking the physical movement to the scan changes.
5. Stop acquisition and start it again. Retain the second dataset and record actual duration and errors.
6. To verify the vehicle buck supply, first establish its target voltage and supply path. Add loads in stages: "Pi alone → Pi plus lidar → Other electronic modules with verified supply requirements". Disconnect power before each wiring change and add only one load at a time.
7. At each stage, measure the buck output and the load-terminal voltage where safely accessible. Use a suitable USB measurement adapter; do not insert bare probes into USB-C contacts. Record anomalies during startup, lidar rotation and program execution.
8. If an oscilloscope is available, someone familiar with it should verify probe ground reference and range before observing logic-supply transients. Do not arbitrarily attach an ordinary earth-referenced probe ground clip to a motor output. With only a multimeter, record what it observes without claiming that transient voltage drops have been ruled out.

| Load in this test | Battery terminal voltage | LM2596S input | LM2596S output | Load-terminal voltage | Continuous duration / anomalies |
|---|---|---|---|---|---|
| No load | To be measured | To be measured | To be measured | Not applicable | To be recorded |
| Pi | To be measured | To be measured | To be measured | To be measured | To be recorded |
| Pi + lidar | To be measured | To be measured | To be measured | To be measured | To be recorded |
| Actual additional electronic load | To be measured | To be measured | To be measured | To be measured | To be recorded |

Proceed when voltages meet each device's requirements under the recorded supply, load and duration conditions, acquisition is reproducible, and no supply anomaly has been observed. Leave any missing current or waveform evidence unverified; do not write "full-load capability passed". [SLAMTEC A2 specifications](https://www.slamtec.com/en/lidar/a2spec)

## 5. Check the BEC, receiver, servo and basic radio control

1. Establish the allowed receiver/servo supply conditions and the ESC's current pairing from the actual wiring, original vehicle records and matching documentation. The user cannot identify the motor or servo model; retain that status. The ESC model alone does not establish motor type or supply compatibility.
2. Identify power, ground and signal on the actual ESC receiver connector and record the wiring. Establish the measurement points before measuring the BEC; do not assign probes from wire position or color alone.
3. Check the output and load documentation. The TBLE-04S manual specifies a 6V/1.5A BEC and imposes servo compatibility restrictions. That value does not establish compatibility with the vehicle's current servo/receiver. If evidence is insufficient, leave this connection unverified and continue independent electronics work whose conditions have been checked.
4. Using the verified original radio-control chain, secure the vehicle with all driven wheels off the ground. Power it according to the applicable transmitter and ESC instructions. Observe neutral first, then briefly test steering, forward motion, stopping and reverse one at a time.
5. Save each action and response. Record steering neutral, left/right mechanical limits, and braking/reverse sequence. Do not fill in PWM timing from common practice or arbitrarily hold the ESC setup button.
6. If BEC load behavior must be observed, use suitable instruments to record voltage, current and anomalies during normal steering. Do not deliberately force the servo against a stop to measure stall current.
7. Test loss of radio signal first by reading receiver outputs with motor and servo actuation isolated. Once the stop command and recovery behavior are clear, perform controlled tests with the wheels suspended. Record deliberate signal-loss tests separately from normal power-on/off procedures.

Deliverables: wiring evidence, present settings and response records, action video, and signal-loss/recovery records. Arrange a short ground-level manual test only after reliable stopping with suspended wheels has been demonstrated and the test area is established. [Original TBLE-04S manual](https://cdn.simba-dickie-group.de/downloads/300045069/300045069_TBLE-04S.pdf)

## 6. Define and verify bidirectional Pi–STM32 communication

Complete this table first. The communication protocol is a team design decision; hardware documentation cannot decide it for the team.

| Item | What to record |
|---|---|
| Actual physical connection | Direct UART, or USB through the onboard interface; record the final choice |
| Board routing | Actual connector, pins, jumpers/solder bridges and their functions, from board documentation and the physical board |
| Levels and power | Signal levels, common ground, and selection between USB and external power |
| Communication settings | Parameters read from the existing project or explicitly agreed by both sides |
| Information content | Target speed, steering, stop, status and sensor data; define units and direction semantics |
| Invalid/timeout handling | Project-defined invalidity conditions, expiry time, and actions on invalidity and recovery |

1. Isolate the actuators. Record the current project and recovery source; do not overwrite unknown original firmware.
2. Prepare minimal programs on the host and STM32 that log transmitted and received data. Complete compilation and separate endpoint execution first. No actual project parameters are available, so this procedure does not prescribe serial-device names, baud rates, pins or installation commands.
3. Send an agreed set of numbered test data from the Pi and check what the STM32 actually receives. Repeat in the opposite direction.
4. At both ends, record actual transmit/receive counts, content differences and timing. A "send successful" message alone does not establish reception by the other endpoint.
5. Disconnect the data link and check timeout status. Reconnect, verify new bidirectional data and record recovery. For USB connections, also record whether the target board loses power or resets.
6. Add checks for invalid data and expired commands. Inspect status and control outputs first while actuators remain isolated.

Proceed when the two logs correspond and disconnect/recovery behavior meets the written interface agreement. If only one direction works, record that result without declaring the entire integration successful.

## 7. Connect SEN0253 separately

1. Disconnect power and confirm the physical board revision, supply, ground, SCL, SDA and connector orientation. Record its installed coordinate orientation.
2. Check I²C pull-up power and the level requirements of the selected STM32 interface. In the original SEN0253 V1.0 schematic, external SCL/SDA pull up to module VCC. Match this to the actual board revision; internal 3.3V sensor operation does not establish a 3.3V external bus.
3. Once supply and bus conditions are established, use a minimal acquisition program matching the actual wiring. Read device identification first, then record stationary and rotating data.
4. Secure the board and slowly rotate it about each vehicle axis. Record data directions and the coordinate convention. Record successful identification, plausible data changes and completed calibration separately.
5. Only after the standalone module is stable should its data be included in Pi communication logs and motion estimation. IMU data is not equivalent to the current position in a map.

References: [DFRobot SEN0253 interface documentation](https://wiki.dfrobot.com/sen0253), [V1.0 schematic](https://dfimg.dfrobot.com/wiki/23066/SEN0253_gravity-10-dof-imu-ahrs-bno055-bmp280_schematics_V1.0.pdf).

## 8. Verify each SHARP sensor before connecting it to an ADC

1. Number the two sensors separately. Verify each supply, ground, analog output and connector orientation.
2. Use a supply meeting the manual and initially leave the analog output disconnected from the STM32. The manufacturer specifies 4.5–5.5V; do not change the sensor supply to 3.3V merely to match the ADC.
3. Aim the sensor at fixed cardboard and measure the distance with a ruler. The suggested checkpoints for this work cycle are 20, 40 and 60cm; record output voltage for each sensor separately at each point. These are planned checkpoints, not course acceptance accuracy requirements or guarantees. Also record behavior outside the specified measurement range, without applying the valid-range conversion there.
4. Establish input conditioning and protection from the documented output conditions, actual ADC reference voltage and sampling conditions. A digital pin's 5V tolerance does not mean its ADC can measure 5V; one voltage reading cannot establish that conditioning is unnecessary.
5. Verify the conditioned levels before connecting the ADC. At the same distances, retain "ruler distance—raw voltage—raw ADC value—converted result".
6. Vary target material and angle, then repeat at the actual mounting position. Cover the areas in which the sensor will be relied on during forward motion, reverse and turns.
7. Set stopping-distance thresholds only after measuring actual speed, processing delay and stopping distance. Do not treat distances below 10cm as a reliable fallback zone.

The manufacturer's effective range is 10–80cm. [SHARP datasheet](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y0a21yk_e.pdf). For ADC input range and sampling conditions, see [STM32F103x8/xB datasheet §5.3.18](https://www.st.com/resource/en/datasheet/stm32f103rb.pdf).

## 9. Verify the speed-sensing parts after arrival

No update on parts arrival has been received. Execute this section only once the gear, cover, OPB815WZ and interface circuit are ready.

1. Compare the physical parts and mounting relationships with the [official mechanical documentation](sources/CoVAPSy_encoder_official/SOURCE_INDEX.md). With drive power disconnected, rotate the transmission slowly. Verify clearance through a complete revolution and that apertures and opaque areas pass through the optical beam.
2. Verify LED current limiting and the detector-output load/pull-up circuit independently. If an existing board already includes these functions, inspect its circuit before adding duplicates. Determine resistor values, supply and input pin from the actual design calculations.
3. Before connecting the STM32, record output levels with the beam clear and blocked. If waveform instruments are available, observe edges and chatter to decide whether signal shaping is required.
4. Once input conditions are acceptable, connect the timer and explicitly select rising-edge, falling-edge or both-edge counting. Place a removable mark on the sensed gear, turn it manually through a complete revolution and repeat over several revolutions to verify actual counts per revolution. Do not equate aperture count directly with software count.
5. With all four wheels on the ground and the vehicle moving straight, record actual travel distance L and valid count N. Calculate distance per count k=L/N and repeat several times. Do not calibrate central-transmission vehicle speed by rotating only one suspended wheel; the differential changes the relationship.
6. Calculate speed magnitude = k × valid counts during an interval / interval duration, then compare it with an independent distance/time measurement. Check low speed and stopping separately for missed counts and incorrect retention of the previous speed.
7. Continue to label forward/reverse direction as inferred from control state. Test the limitations during direction changes, coasting and externally pushing the vehicle. Passing a test cannot turn a single photointerrupter into hardware that independently measures direction.

References: [OPB815 datasheet](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Datasheet/OPB815.pdf), [TT Electronics Application Note 248](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Application-Note/App-Note-248-Connecting-and-Using-Infrared-Optoelectronics.pdf).

## 10. Enable STM32 control outputs and verify takeover logic

1. Obtain actual control timing and neutral values from verified receiver/ESC documentation, original system records or waveform measurements. Do not assume commonly used pulse widths or frequencies.
2. Measure STM32 outputs with actuators isolated first. Check that neutral, steering range, run/stop commands and program state agree.
3. Once levels, timing and stopping behavior are clear, connect the ESC and servo with the vehicle secured and all driven wheels off the ground. Verify neutral first, then small actions one at a time. Receiver outputs and STM32 outputs must not be directly connected together to the same control input.
4. Verify speed PID only after speed feedback passes Step 9. Without measured speed, record only open-loop actuator tests; do not claim closed-loop speed control has passed.
5. Test manual selection, automatic selection, takeover, active-command timeout, radio-signal loss, nearby-obstacle triggers and communication recovery separately. Check logic with actuation isolated first, then perform controlled suspended-wheel tests.
6. Explicitly record whether restart is permitted after recovery and which valid command is required. The project must define this behavior; restored communication must not automatically mean resumed driving.

Proceed to ground tests once stopping, direction changes and takeover behavior are documented, and mechanical mounting, test area and team roles are established. Software takeover through the STM32 still depends on a working STM32; it is not independent hardware takeover.

## 11. Whole-vehicle integration and navigation acceptance

1. Run the Pi, lidar, STM32 and sensors together on the actual vehicle supply. Repeat power and data checks.
2. In a controlled area, begin with low-speed manual operation, then verify automatic speed/steering responses. Record whether motor/servo activity affects power, communication or speed measurement.
3. Measure actual stopping distance, space occupied during turns and vehicle dimensions. Then define compatible driving areas and obstacle-trigger conditions.
4. Test map creation, localization in the map, destination planning, path following, obstacles with an available detour and stopping at a completely blocked route separately. Accuracy, speed and obstacle criteria not established in a formal brief remain open for discussion; do not invent instructor acceptance requirements.
5. Change only one justified condition at a time and preserve successful and failed records. A single short successful test establishes only its recorded conditions; arrange sustained operation and reproduction separately.

## Results to submit first

Start with Steps 1 and 2; the later steps need not all be completed in one session. Step 3 can proceed independently in parallel where verified standalone board power is available.

| Item | Current result |
|---|---|
| Available instruments and models | Awaiting user information |
| Actual wiring records for both branches after the main switch | To be recorded |
| Battery terminal voltage and polarity | To be measured |
| LM2596S unloaded input voltage | To be measured |
| LM2596S unloaded output voltage | To be measured |
| Devices originally connected to the LM2596S output | To be traced |
| Input/output readings and elapsed time after switching off | To be measured |

Use these actual results to determine the next loads that may be connected, the interface documentation still needed and the corresponding measurement points. A drawing cannot replace inspection of the physical vehicle.
