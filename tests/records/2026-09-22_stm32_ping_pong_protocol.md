# STM32 PING/PONG Protocol Test

- Related task / Issue: LOCAL-005 / Issue #5, C2/C3 diagnostic protocol
- Operator and date: mzy410104-lgtm, 2026-09-22 CEST
- Test goal: Verify newline-delimited diagnostic command parsing over USART2 interrupt reception.
- Equipment and connection: NUCLEO-F103RB connected to a Windows host through the onboard ST-LINK virtual COM port, enumerated as COM8.
- Actual configuration: USART2 on PA2 TX and PA3 RX; 115200 bit/s, 8 data bits, no parity and one stop bit.
- Build result: Keil reported `Code=5056`, `RO-data=316`, `RW-data=24`, `ZI-data=1720`, `0 Error(s), 0 Warning(s)`.
- Procedure and results:
  1. Sent hexadecimal `50 49 4E 47 0A`, representing `PING\n`; received `50 4F 4E 47 0A`, representing `PONG\n`.
  2. Sent `NOPE\n`; received zero bytes during the observation interval.
  3. Sent `PING\r\n`; received `50 4F 4E 47 0A`, representing `PONG\n`.
  4. LD2 continued its 500 ms heartbeat during the test.
- Conclusion: The standalone STM32 diagnostic parser passed for LF and CRLF request endings. An unrecognized line produced no response under the tested implementation.
- Limits and next step: The endpoint was a Windows host, not the Raspberry Pi. Control commands, feedback messages, timeout, disconnection and recovery remain undefined or untested. B and C must perform the Pi integration test later.
- Reviewer: Pending
