# Pi–STM32 Interface Agreement

This is an interface document awaiting completion, not an implemented protocol. C is [mzy410104-lgtm](https://github.com/mzy410104-lgtm), responsible for the STM32 endpoint. The B member is still to be confirmed. B/C will complete this agreement together after inspecting the actual wiring and any available software. C confirmed that the STM32 project has not yet been created; define the interface before implementing communication at both ends.

| Item | Current value / status | Source or responsibility |
|---|---|---|
| Physical connection and interface routing | To be recorded | Physical hardware, board manual and existing project |
| Pins, power, signal levels and common ground | To be recorded | Actual wiring verification |
| Communication parameters and message format | To be agreed by both sides | Read an existing implementation first; if none exists, explicitly define the design before coding |
| Units and direction conventions for target speed and steering | To be agreed by both sides | Joint control/navigation agreement |
| Stop, timeout, error and recovery behavior | To be agreed by both sides | Project control requirements and measured tests |
| Speed, orientation, distance and status feedback | To be agreed by both sides | Actual sensor outputs and their meaning |
| Corresponding firmware/host versions and test records | To be recorded | Actual commits and integration records from both sides |

Express speed magnitude measured by the single photointerrupter separately from direction inferred from control state. No JSON keys, frame fields or serial-port identifiers are prescribed here.
