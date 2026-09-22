# Pi–STM32 Interface Agreement

This interface agreement is partially completed. C is [mzy410104-lgtm](https://github.com/mzy410104-lgtm), responsible for the STM32 endpoint. The B member is still to be confirmed. Standalone STM32 communication has been implemented and tested with a Windows host through the onboard ST-LINK virtual COM port. This does not establish the Raspberry Pi wiring or the final application protocol.

| Item | Current value / status | Source or responsibility |
|---|---|---|
| Physical connection and interface routing | Standalone test: Windows host to onboard ST-LINK USB virtual COM port, internally routed to STM32 USART2. Raspberry Pi connection remains to be agreed and verified. | NUCLEO-F103RB project configuration and the 2026-09-22 standalone test |
| Pins, power, signal levels and common ground | STM32 USART2 uses PA2 TX and PA3 RX. Raspberry Pi connector pins, power arrangement, electrical-level verification and common-ground wiring remain to be recorded before direct Pi connection. | `firmware/auto_car/auto_car.ioc`; physical Pi wiring remains B/C responsibility |
| Communication parameters and message format | STM32 standalone configuration: 115200 bit/s, 8 data bits, no parity and one stop bit. The test firmware transmits `STM32 UART OK\r\n` and echoes one received byte. Final framing and application messages remain to be agreed by both sides. | Firmware commit `3f10c88`; final protocol requires B/C agreement |
| Units and direction conventions for target speed and steering | To be agreed by both sides | Joint control/navigation agreement |
| Stop, timeout, error and recovery behavior | To be agreed by both sides | Project control requirements and measured tests |
| Speed, orientation, distance and status feedback | To be agreed by both sides | Actual sensor outputs and their meaning |
| Corresponding firmware/host versions and test records | STM32 interrupt-reception firmware: `3f10c88`. Standalone evidence: `tests/records/2026-09-22_stm32_usart2_interrupt.md`. Raspberry Pi version and integration record remain pending. | Repository commits and actual integration records from both sides |

Express speed magnitude measured by the single photointerrupter separately from direction inferred from control state. No JSON keys, frame fields or serial-port identifiers are prescribed here.
