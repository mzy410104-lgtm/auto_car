#!/usr/bin/env python3
"""Sweep D10 (ESC channel, 1300..1700 us) to test a servo or ESC connected on D10 (PB6 / TIM4_CH1)."""
import glob
import os
import re
import select
import termios
import time


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
        m_esc = re.search(r"ESC_US=(\d+)", out)
        armed = int(m_armed.group(1)) if m_armed else 0
        esc = int(m_esc.group(1)) if m_esc else 1500
        return armed, esc, out

    def move_d10_to(target_us, step_us=50):
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
            reply = send(f"ESC {next_us}", wait=0.06)
            if "ARMED=0" in reply or "NOT ARMED" in reply or "SAFE" in reply:
                send("CENTER", 0.06)
                send("ARM", 0.06)
                _, cur_us, _ = get_state()
                continue
            m_esc = re.search(r"ESC_US=(\d+)", reply)
            if m_esc:
                cur_us = int(m_esc.group(1))
            else:
                _, cur_us, _ = get_state()
        return cur_us

    print("=== Starting 3-Cycle D10 Sweep (1300..1700 us) ===")
    send("STREAM OFF", 0.1)
    send("CENTER", 0.1)
    _, _, status_str = get_state()
    print(f"Initial state: {status_str}")

    for i in range(1, 4):
        cur = move_d10_to(1700, 50)
        print(f"  Cycle {i}/3: Reached {cur} us")
        time.sleep(0.4)

        cur = move_d10_to(1300, 50)
        print(f"  Cycle {i}/3: Reached {cur} us")
        time.sleep(0.4)

    print("Returning D10 to center (1500 us)...")
    move_d10_to(1500, 50)
    reply = send("CENTER", 0.1)
    print(f"Final state: {reply}")
    os.close(fd)
    print("=== D10 Sweep Complete ===")


if __name__ == "__main__":
    main()
