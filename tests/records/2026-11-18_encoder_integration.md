# Dual encoder integration — 2026-11-18

- Based on GitHub `main` at `35b0132`; this branch preserves the updated STM32 bench command parser and Raspberry Pi test scripts.
- Right encoder moved from the prototype's TIM3 pins to TIM1 PA8/PA9 so TIM3 PC7 remains available for servo PWM. Left encoder uses TIM2 PA0/PA1. ESC remains on TIM4 PB6.
- Added quadrature counts, wheel speed/distance, midpoint odometry and read-only serial `ODOM` output. Updated the CubeMX configuration and Keil project source list.
- Keil MDK V5.05 build: **0 errors, 0 warnings**. The complete output is in the adjacent build log. The generated hex and axf are local build products; this branch has not been flashed or physically tested.
- The team reported successful manual encoder rotation testing of an earlier integration. That result has not been repeated for this branch.
- The team subsequently reported that `STATUS` updated on ESC and servo commands but neither actuator moved, while the ESC LED flashed slowly. Therefore actuator operation is **not validated** and must be diagnosed before a driving test.
- Calibrate the assumed 600 PPR, x4 count factor, 61 mm contact-wheel diameter and 202 mm contact-wheel spacing on the assembled vehicle. Check each encoder's forward sign by rolling it forward.
