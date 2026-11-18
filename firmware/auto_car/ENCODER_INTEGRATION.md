# Dual contact-wheel encoders

This branch integrates two quadrature encoders into the STM32 firmware on top of the current `main` branch. The servo and ESC remain on their existing PWM timers.

| Function | Timer / pins |
| --- | --- |
| Left encoder A/B | TIM2 CH1/CH2, PA0/PA1 |
| Right encoder A/B | TIM1 CH1/CH2, PA8/PA9 (D7/D8) |
| Servo PWM | TIM3 CH2, PC7 |
| ESC PWM | TIM4 CH1, PB6 |

Both encoders must share signal ground with the STM32. The inputs are configured without internal pull-ups. If the encoder outputs are open collector, use pull-ups to **3.3 V** after checking the output type and voltage; do not drive STM32 inputs with an unverified 5 V signal.

The serial command `ODOM` returns left/right wheel speed in mm/s, distance in mm, estimated X/Y position in mm, wrapped heading and cumulative heading in centidegrees. It does not arm the motor. `PING`, `STATUS`, `ARM`, `ESC`, `SERVO`, `CENTER`, `STOP`, `STREAM` and IMU output remain in the current firmware.

The speed conversion currently assumes 600 pulses per revolution, 4 counts per pulse and a 61 mm contact-wheel diameter. The heading estimate assumes 202 mm between the contact-wheel paths. These values came from the supplied encoder prototype and require measurement and calibration on the car. The physical car wheel track of 180 mm is not automatically the same as the contact-wheel spacing.

Keil MDK build on 2026-11-18: 0 errors, 0 warnings; see [`tests/records/2026-11-18_encoder_integration_build.log`](../../tests/records/2026-11-18_encoder_integration_build.log). This build does not establish physical actuator operation. In the most recent test reported by the team, serial `STATUS` reflected ESC and servo commands, but neither actuator moved, and the ESC LED flashed slowly. Diagnose that condition before driving the car.
