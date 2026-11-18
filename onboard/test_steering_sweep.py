#!/usr/bin/env python3
"""
Multi-Cycle Steering Servo Sweep Test on STM32 SERVO Channel (TIM3_CH2 / PC7 / D9).
Ramps in 50 us increments between 1900 us and 1100 us.
"""
import glob
import os
import re
import select
import termios
import time

CYCLES = 5


def find_port():
    by_id = sorted(glob.glob("/dev/serial/by-id/usb-STMicroelectronics*"))
    if by_id:
        return os.path.realpath(by_id[0])
    ports = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/cu.usbmodem*"))
    return ports[-1] if ports else "/dev/ttyACM0"


def main():
    port = find_port()
    print(f"Using port: {port}")
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    attrs = termios.tcgetattr(fd)
    attrs[4] = attrs[5] = termios.B115200
    attrs[2] |= (termios.CLOCAL | termios.CREAD | termios.CS8)
    attrs[0] = attrs[1] = attrs[3] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    time.sleep(0.1)

    def send(cmd, wait=0.06):
        os.write(fd, (cmd + "\n").encode("ascii"))
        time.sleep(wait)
        chunks = []
        while select.select([fd], [], [], 0.0)[0]:
            data = os.read(fd, 4096)
            if not data:
                break
            chunks.append(data.decode("utf-8", "replace"))
        return "".join(chunks).strip()

    def get_state():
        out = send("STATUS", wait=0.06)
        m_armed = re.search(r"ARMED=(\d+)", out)
        m_servo = re.search(r"SERVO_US=(\d+)", out)
        armed = int(m_armed.group(1)) if m_armed else 0
        servo = int(m_servo.group(1)) if m_servo else 1500
        return armed, servo, out

    def move_servo_to(target_us, step_us=50):
        armed, cur_us, _ = get_state()
        if not armed:
            send("CENTER", 0.06)
            send("ARM", 0.06)
            _, cur_us, _ = get_state()
        while cur_us != target_us:
            if target_us > cur_us:
                next_us = min(target_us, cur_us + step_us)
            else:
                next_us = max(target_us, cur_us - step_us)
            reply = send(f"SERVO {next_us}", wait=0.055)
            if "ARMED=0" in reply or "NOT ARMED" in reply or "SAFE" in reply:
                send("CENTER", 0.055)
                send("ARM", 0.055)
                _, cur_us, _ = get_state()
                continue
            m_servo = re.search(r"SERVO_US=(\d+)", reply)
            if m_servo:
                cur_us = int(m_servo.group(1))
            else:
                _, cur_us, _ = get_state()
        return cur_us

    print(f"=== Starting {CYCLES}-Cycle Verified Left <-> Right Steering Sweep ===")
    send("STREAM OFF", 0.15)
    send("CENTER", 0.15)
    _, start_us, status_str = get_state()
    print(f"Initial state: {status_str}")

    for i in range(1, CYCLES + 1):
        cur = move_servo_to(1900, 50)
        print(f"  Cycle {i}/{CYCLES}: Reached {cur} us (Right/Side A)")
        time.sleep(0.25)

        cur = move_servo_to(1100, 50)
        print(f"  Cycle {i}/{CYCLES}: Reached {cur} us (Left/Side B)")
        time.sleep(0.25)

    print("Returning to center (1500 us)...")
    cur = move_servo_to(1500, 50)
    reply = send("CENTER", 0.1)
    _, final_us, final_status = get_state()
    print(f"Final state: {final_status} ({reply})")
    os.close(fd)
    print("=== Multi-Sweep Complete ===")


if __name__ == "__main__":
    main()
