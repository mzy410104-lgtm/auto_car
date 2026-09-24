# STM32 SEN0253 Initial Acquisition Record

- Related task / Issue: Cycle 1 C3 / Issue #9
- Operator and date: Member C, 2026-09-24 CEST
- Test goal: Verify initial I2C communication with the DFRobot SEN0253 board and acquire changing BNO055 orientation values before integration with vehicle control.
- Equipment: NUCLEO-F103RB, DFRobot SEN0253 and a host serial terminal.
- Firmware configuration: I2C1 uses PB8 for SCL and PB9 for SDA at 100 kHz in 7-bit addressing mode. USART2 reports diagnostics at 115200 bit/s. These are firmware settings; the physical wire colours, measured supply voltage and supply source were not recorded during this test.
- Firmware source: The firmware included in the same commit as this record.
- Build and flash status: The operator reported that compilation and flashing completed successfully. Exact compiler output and binary size were not retained for that run.

## Procedure and observed data

1. Scanned the I2C bus. The terminal returned:

   ```text
   I2C 0x28
   I2C 0x76
   I2C SCAN DONE
   ```

2. Read the device identification registers. The terminal returned:

   ```text
   BNO055 ID: 0xA0
   BMP280 ID: 0x58
   ```

3. Wrote the BNO055 operating mode and read it back. The terminal returned:

   ```text
   BNO055 MODE: 0x0C
   ```

4. Read heading, roll and pitch values. The values changed continuously when the board was moved.

5. Performed the BNO055 calibration movement sequence. The terminal returned:

   ```text
   CAL SYS=3 GYR=3 ACC=3 MAG=3
   MODE=0x0C SYS_STATUS=5 SYS_ERR=0x00
   ```

## Result

The initial SEN0253 acquisition passed for I2C discovery, device identification, BNO055 NDOF-mode readback, changing Euler output and a fully calibrated status during the observed test.

## Limits and next actions

- The measured sensor supply voltage and exact physical wiring must be recorded in a later electrical-interface check.
- The exact models and electrical limits of the two SHARP sensors have not been recorded. They must be identified before connecting their outputs to STM32 ADC inputs.
- No speed measurement was performed. The timer/input design remains dependent on the final speed-sensor and mechanical installation decision.
- A separately tested device responded at `0x77` with identification value `0x60`; the operator confirmed that this was the wrong sensor and it is excluded from this SEN0253 result.
- Reviewer: Pending
