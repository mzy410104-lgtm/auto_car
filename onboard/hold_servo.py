#!/usr/bin/env python3
"""Hold SERVO at 1700 us for ~6 s so we can read TIM3 registers live."""
import glob
import os
import select
import termios
import time


def find_port():
    by_id = sorted(glob.glob("/dev/serial/by-id/usb-STMicroelectronics*"))
    if by_id:
        return os.path.realpath(by_id[0])
    ports = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/cu.usbmodem*"))
    return ports[0] if ports else "/dev/ttyACM0"


def main():
    port = find_port()
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    a = termios.tcgetattr(fd)
    a[4] = a[5] = termios.B115200
    a[2] |= termios.CLOCAL | termios.CREAD | termios.CS8
    a[0] = a[1] = a[3] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)

    def send(c, w=0.08):
        os.write(fd, (c + "\n").encode())
        time.sleep(w)
        chunks = []
        while select.select([fd], [], [], 0.0)[0]:
            data = os.read(fd, 4096)
            if not data:
                break
            chunks.append(data.decode(errors="replace"))
        return "".join(chunks).strip()

    send("STREAM OFF")
    send("CENTER")
    print(send("ARM"))
    for v in (1550, 1600, 1650, 1700):
        print(send(f"SERVO {v}"))
    t0 = time.time()
    while time.time() - t0 < 6:
        send("SERVO 1700", 0.5)
    for v in (1650, 1600, 1550, 1500):
        send(f"SERVO {v}")
    print(send("CENTER"))
    os.close(fd)


if __name__ == "__main__":
    main()
