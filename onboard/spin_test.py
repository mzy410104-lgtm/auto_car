#!/usr/bin/env python3
"""Test which exact command stops the RPLIDAR A2M8 motor."""
import struct
import time
import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200


def pwm_pkt(pwm: int) -> bytes:
    payload = struct.pack("<H", pwm)
    pkt = bytearray([0xA5, 0xF0, 0x02]) + payload
    cs = 0
    for b in pkt:
        cs ^= b
    pkt.append(cs)
    return bytes(pkt)


ser = serial.Serial(PORT, BAUD, timeout=1)

print("1) Sending STOP (A5 25) + DTR=True + PWM=0 for 4 seconds...")
ser.write(b"\xA5\x25")
time.sleep(0.1)
ser.dtr = True
ser.write(pwm_pkt(0))
time.sleep(4.0)

print("2) Sending STOP (A5 25) + DTR=False + PWM=0 for 4 seconds...")
ser.write(b"\xA5\x25")
time.sleep(0.1)
ser.dtr = False
ser.write(pwm_pkt(0))
time.sleep(4.0)

print("3) Closing serial port now...")
ser.close()
print("Done.")
