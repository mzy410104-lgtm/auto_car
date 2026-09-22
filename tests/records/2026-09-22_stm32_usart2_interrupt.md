# STM32 USART2 Interrupt Reception Test

- Related task / Issue: LOCAL-005 / Issue #5, C3 standalone STM32 communication
- Operator and date/time: mzy410104-lgtm, 2026-09-22 10:13 CEST
- Actual time spent: Not recorded
- Test goal and prerequisites: Verify that the NUCLEO-F103RB continues periodic work while receiving one byte through USART2 interrupt mode and echoing it to the host.
- Equipment, physical wiring and supply source: NUCLEO-F103RB connected to a Windows host through the onboard ST-LINK USB interface. The ST-LINK virtual COM port enumerated as COM8. The exact onboard jumper configuration was not recorded in this test.
- Software/firmware commits and actual configuration: Firmware commit `3f10c88`; USART2 on PA2 TX and PA3 RX; 115200 bit/s, 8 data bits, no parity, one stop bit; USART2 interrupt preemption priority 1 and subpriority 0.
- Instruments and measurement points: Windows serial-port API reading COM8. No electrical measurement was performed.
- Procedure:
  1. Build the Keil project and flash the target.
  2. Reset the board and observe LD2 periodic toggling.
  3. Open COM8 with the configured serial parameters and read the periodic message.
  4. Send the single character `#` and read the returned byte stream.
- Expected behavior and its basis: LD2 continues toggling; `STM32 UART OK\r\n` is transmitted periodically; the received byte triggers `HAL_UART_RxCpltCallback`; the main loop echoes the byte and rearms `HAL_UART_Receive_IT`.
- Original readings / logs / photographs / video index: Keil build log reported `Code=4992`, `RO-data=328`, `RW-data=24`, `ZI-data=1704`, `0 Error(s), 0 Warning(s)`. The host received `#STM32 UART OK\r\n...`; the first returned byte was hexadecimal `23`, matching `#`.
- Actual results and anomalies: The first host read performed before the board reset returned no bytes. After reset, LD2 toggled and periodic USART2 output resumed. The `#` byte was then echoed successfully.
- Conclusion and applicable conditions: Standalone PC-to-STM32 and STM32-to-PC communication passed for one byte using USART2 interrupt reception. Periodic main-loop work continued during the test.
- Unresolved items, next step and owner: This test did not use the Raspberry Pi endpoint and did not test multi-byte framing, disconnection, timeout, recovery, actuator isolation, or onboard vehicle power. C will implement command framing; B and C must later perform the Pi-to-STM32 integration test.
- Reviewer: Pending
