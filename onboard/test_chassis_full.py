#!/usr/bin/env python3
"""
Full STM32 Chassis Bench Test (SEN0253 BNO055 IMU, Steering Servo on D9, TBLE-04S ESC on D10).
Steps ESC and SERVO channels in <=50 us increments to comply with STM32 bench safety firmware.
"""
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
    if ports:
        return ports[0]
    return "/dev/ttyACM0"


def main():
    port = find_port()
    print(f"Opening STM32 port: {port}")
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    attrs = termios.tcgetattr(fd)
    attrs[4] = attrs[5] = termios.B115200
    attrs[2] |= (termios.CLOCAL | termios.CREAD | termios.CS8)
    attrs[0] = attrs[1] = attrs[3] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    time.sleep(0.1)

    def send(cmd, wait=0.055):
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
        m_servo = re.search(r"SERVO_US=(\d+)", out)
        armed = int(m_armed.group(1)) if m_armed else 0
        esc = int(m_esc.group(1)) if m_esc else 1500
        servo = int(m_servo.group(1)) if m_servo else 1500
        return armed, esc, servo, out

    def ensure_armed():
        armed, esc_us, servo_us, _ = get_state()
        if not armed:
            if esc_us != 1500 or servo_us != 1500:
                send("CENTER", 0.06)
            reply = send("ARM", 0.06)
            print(f"    [ARM] -> {reply}")

    def ramp_channel(channel, target_us, step_us=50):
        ensure_armed()
        _, esc_us, servo_us, _ = get_state()
        cur_us = servo_us if channel == "SERVO" else esc_us
        while cur_us != target_us:
            if target_us > cur_us:
                next_us = min(target_us, cur_us + step_us)
            else:
                next_us = max(target_us, cur_us - step_us)
            reply = send(f"{channel} {next_us}", wait=0.055)
            m_val = re.search(rf"{channel}_US=(\d+)", reply)
            if m_val:
                cur_us = int(m_val.group(1))
            else:
                print(f"    [WARN on {channel} {next_us}] {reply}")
                ensure_armed()
                _, esc_us, servo_us, _ = get_state()
                cur_us = servo_us if channel == "SERVO" else esc_us
        return cur_us

    def hold_channel(channel, us, duration_s=1.0):
        t0 = time.time()
        while time.time() - t0 < duration_s:
            # Re-sending the current value refreshes the 3000 ms timer without triggering ERR CENTER FIRST!
            send(f"{channel} {us}", 0.25)

    print("\n=== TEST 1: PING & SEN0253 (BNO055) IMU Telemetry ===")
    send("STREAM OFF", 0.1)
    ping_out = send("PING", 0.1)
    print(f"  PING -> {ping_out}")
    imu_out = send("STREAM ON", 1.0)
    send("STREAM OFF", 0.15)
    for line in imu_out.splitlines():
        if line.strip():
            print(f"  IMU: {line.strip()}")

    print("\n=== TEST 2: Steering Servo Sweep (Left <-> Right <-> Center) ===")
    send("CENTER", 0.1)
    send("ARM", 0.1)
    cur_s = ramp_channel("SERVO", 1850, 50)
    print(f"  Steering Side A: SERVO_US={cur_s} (holding 1.0s)")
    hold_channel("SERVO", 1850, 1.0)

    cur_s = ramp_channel("SERVO", 1150, 50)
    print(f"  Steering Side B: SERVO_US={cur_s} (holding 1.0s)")
    hold_channel("SERVO", 1150, 1.0)

    cur_s = ramp_channel("SERVO", 1500, 50)
    print(f"  Steering Center: SERVO_US={cur_s}")
    time.sleep(0.3)

    print("\n=== TEST 3: Drive Motor (TBLE-04S ESC) Forward / Stop / Reverse ===")
    print("  3a. Neutral hold (1500 us for 0.8s)...")
    hold_channel("ESC", 1500, 0.8)

    print("  3b. Ramping ESC to 1620 us (Direction 1 - holding 1.5s)...")
    cur_e = ramp_channel("ESC", 1620, 30)
    print(f"      Reached ESC_US={cur_e}")
    hold_channel("ESC", 1620, 1.5)

    print("  3c. Returning ESC to 1500 us (Neutral Stop - holding 1.0s)...")
    cur_e = ramp_channel("ESC", 1500, 50)
    hold_channel("ESC", 1500, 1.0)

    print("  3d. TBLE-04S Brake/Reverse transition (1400 us brake -> 1500 us neutral -> 1380 us Direction 2)...")
    cur_e = ramp_channel("ESC", 1400, 50)
    hold_channel("ESC", 1400, 0.4)
    cur_e = ramp_channel("ESC", 1500, 50)
    hold_channel("ESC", 1500, 0.5)
    cur_e = ramp_channel("ESC", 1380, 30)
    print(f"      Reached ESC_US={cur_e} (holding 1.5s)")
    hold_channel("ESC", 1380, 1.5)

    print("  3e. Stopping & Disarming (ESC=1500, SERVO=1500)...")
    ramp_channel("ESC", 1500, 50)
    stop_reply = send("STOP", 0.15)
    _, _, _, final_state = get_state()
    print(f"  Final state: {final_state} ({stop_reply})")

    os.close(fd)
    print("\n=== All Chassis Tests Complete ===")


if __name__ == "__main__":
    main()
