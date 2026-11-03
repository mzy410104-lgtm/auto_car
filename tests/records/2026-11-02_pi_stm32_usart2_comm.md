# Raspberry Pi 4 <-> STM32 NUCLEO-F103RB Serial Communication & Protocol Test

- Related task / Issue: Cycle 1 Tasks BC & C5 / Issues #8 & #9 (Pi–STM32 bidirectional communication, PING/PONG, STATUS, and invalid-command rejection)
- Operator and date/time: Member B (Mahdi), 2026-11-02 15:10–15:17 CET
- Actual time spent: 1.0 h
- Test goal and prerequisites:
  1. Verify physical USB enumeration of the NUCLEO-F103RB onboard ST-LINK/V2-1 virtual COM port on the Raspberry Pi 4.
  2. Query the onboard STM32 firmware command set (`HELP\n`), state (`STATUS\n`), and IMU stream control (`STREAM OFF\n`).
  3. Execute a 10-message `PING\n` -> `PONG\n` diagnostic test, measure round-trip time (RTT) and packet loss, test unrecognized command handling (`INVALID_CMD\n`), and test CRLF (`PING\r\n`) handling.
- Equipment, physical wiring and supply source:
  - Raspberry Pi 4 Model B (`yann`, powered via external 5V USB-C supply).
  - STM32 NUCLEO-F103RB (`MB1136 rev C`) connected via USB cable from its onboard ST-LINK/V2-1 USB Mini-B port to a Raspberry Pi 4 USB 2.0 port (`Bus 001 Device 005: ID 0483:374b STMicroelectronics ST-LINK/V2.1`).
  - Enumerated on Raspberry Pi as `/dev/ttyACM0` and persistent by-id symlink `/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066DFF485753667187154458-if02`.
  - Vehicle ESC (`TBLE-04S`) and propulsion battery remained isolated (`ARMED=0 ESC_US=1500 SERVO_US=1500`).
- Software/firmware commits and actual configuration:
  - Raspberry Pi script: `onboard/stm32_comm_test.py` (`115200` bit/s, `8` data bits, no parity, `1` stop bit).
  - STM32 onboard firmware (`USART2` on `PA2` TX / `PA3` RX @ `115200 8N1`): supports `PING`, `HELP`, `STATUS`, `STREAM ON|OFF`, `STOP`, `CENTER`, `ARM`, `ESC <1300..1700>`, `SERVO <1000..2000>`, with `3000 ms` command timeout returning outputs to `1500 us`.
- Instruments and measurement points:
  - Host-side Python `time.time()` round-trip timing across `/dev/ttyACM0` (`115200 8N1`).
- Procedure:
  1. Verify `/dev/ttyACM0` enumeration and `plugdev`/`dialout` permissions on the Raspberry Pi.
  2. Open `/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066DFF485753667187154458-if02` at `115200 8N1` and observe periodic telemetry for `1.5 s`.
  3. Send `HELP\n` and record the supported command list returned by the STM32.
  4. Send `STREAM OFF\n` (to mute unconnected `BNO055` I2C read error messages) followed by `STATUS\n`.
  5. Send 10 sequential `PING\n` commands at `200 ms` intervals and record `PONG\n` responses and RTTs.
  6. Send `INVALID_CMD\n` to verify unrecognized command rejection, followed by `PING\r\n` to verify CRLF compatibility and immediate recovery.
- Expected behavior and its basis:
  - `PING\n` and `PING\r\n` return `PONG\n`; `INVALID_CMD\n` does not return `PONG\n` and returns `ERR UNKNOWN; SEND HELP`; `STATUS\n` reports disarmed neutral outputs (`1500 us`).
- Original readings / logs / photographs / video index:
  - JSON logs saved on Raspberry Pi at `/home/yann/stm32_comm_log.json` and `/home/yann/stm32_reconnect_log.json`.
  - `HELP\n` response:
    - `BENCH COMMANDS: ARM, ESC <1300..1700>, SERVO <1000..2000>, CENTER, STOP, STATUS, STREAM ON|OFF, HELP; Timeout: outputs return to 1500 us after 3000 ms.`
  - `STREAM OFF\n` and `STATUS\n` responses:
    - `OK STREAM=0`
    - `STATUS ARMED=0 ESC_US=1500 SERVO_US=1500 STREAM=0 TIMEOUT_MS=3000`
- Actual results and anomalies:
  - **With `STREAM ON` (default boot state while `SEN0253` I2C sensor is unplugged)**: STM32 periodically prints `BNO055 EULER READ ERROR` / `BNO055 CALIB READ ERROR`. During blocking I2C timeouts (`100 ms`), UART `PING` RTT varied between `1.83 ms` and `39.11 ms` (mean `6.08 ms`, `10/10` received after flushing initial partial line buffer).
  - **With `STREAM OFF` (`OK STREAM=0`)**: `10/10` `PING\n` requests received `PONG\n` (`0.0%` packet loss) with RTT mean `1.84 ms` (`min = 1.24 ms`, `max = 1.97 ms`).
  - **Invalid command test (`INVALID_CMD\n`)**: Returned `ERR UNKNOWN; SEND HELP` and no `PONG\n` (`invalid_cmd_ignored = True`).
  - **CRLF recovery test (`PING\r\n`)**: Returned `PONG\n` in `1.96 ms` (`crlf_ping_accepted = True`).
  - **USB Disconnect & Reconnect test (`stm32_comm_test.py --reconnect-test`)**:
    - Pre-disconnect: `3/3` `PING -> PONG` (`1.86–1.89 ms` RTT) with `STREAM=0`.
    - USB unbind/disconnect on bus device `1-1.3` (`0483:374b`): Raspberry Pi immediately removed `/dev/ttyACM0` and `/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066DFF485753667187154458-if02`.
    - USB rebind/reconnect after `2.61 s`: Device re-enumerated at the same persistent `by-id` path. Because the NUCLEO-F103RB derives power from the ST-LINK USB connection in standalone bench mode, USB disconnection/reconnection resets the STM32 target MCU (`STATUS` returned `STATUS ARMED=0 ESC_US=1500 SERVO_US=1500 STREAM=1 TIMEOUT_MS=3000`, confirming reset to safe disarmed neutral `1500 us` and default `STREAM=1`).
    - Startup settle time: On boot/reset, the STM32 executes `HAL_Delay(700)` + `I2C_Scan()` across 127 addresses (`~2.5 s` when I2C devices are absent), requiring `~3.5 s` after USB re-enumeration before `USART2` command processing resumes. After a `3.6 s` post-enumeration wait, `5/5` post-reconnect `PING -> PONG` checks passed (`1.88 ms` min RTT, `4.32 ms` mean RTT).
- Conclusion and applicable conditions:
  - **Pass**. Bidirectional Raspberry Pi 4 <-> STM32 NUCLEO-F103RB serial communication, command diagnostics, invalid-command rejection, and USB disconnect/reconnect recovery over `/dev/ttyACM0` (`115200 8N1`) are verified and reproducible.
- Unresolved items, next step and owner:
  - Notice that the firmware currently flashed on the physical NUCLEO-F103RB board includes the interactive bench command parser (`HELP`, `STATUS`, `STREAM ON|OFF`, `ARM`, `ESC`, `SERVO`, `STOP`, `3000 ms` timeout), whereas `firmware/auto_car/Core/Src/main.c` in the repository currently reflects an earlier version (`BENCH_TIMEOUT_MS = 2000U`, `PING` only). Member C should commit the latest STM32 `main.c` source so the repository matches the flashed board firmware.
  - Physical reconnect/disconnect test and high-level autonomous motion-control framing remain to be finalized jointly by Members A, B, and C.
- Reviewer: Pending
