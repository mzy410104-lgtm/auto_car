#!/usr/bin/env python3
"""
RPLIDAR A2M8 scan acquisition script for Raspberry Pi 4.
Records 360-degree scans to CSV with timestamps and prints live closest-obstacle distance.
"""
import argparse
import csv
import struct
import time
from rplidar import RPLidar


def pwm_pkt(pwm: int) -> bytes:
    """Build SLAMTEC A2M8 SET_MOTOR_PWM (0xA5 0xF0) packet."""
    payload = struct.pack("<H", pwm)
    pkt = bytearray([0xA5, 0xF0, 0x02]) + payload
    checksum = 0
    for b in pkt:
        checksum ^= b
    pkt.append(checksum)
    return bytes(pkt)


def start_a2_motor(lidar: RPLidar, pwm: int = 660) -> None:
    """Start the RPLIDAR A2M8 motor."""
    lidar._serial.dtr = False
    time.sleep(0.05)
    lidar._serial.write(pwm_pkt(pwm))
    lidar.motor_running = True


def stop_a2_motor(lidar: RPLidar) -> None:
    """Stop the RPLIDAR A2M8 scan and motor cleanly."""
    lidar._serial.write(b"\xA5\x25")
    time.sleep(0.1)
    lidar._serial.dtr = True
    lidar._serial.write(pwm_pkt(0))
    time.sleep(0.1)
    lidar._serial.dtr = False
    lidar._serial.write(pwm_pkt(0))
    time.sleep(0.1)
    lidar.motor_running = False


def main():
    parser = argparse.ArgumentParser(description="Acquire and save RPLIDAR A2M8 scans.")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port path")
    parser.add_argument("--baud", type=int, default=115200, help="UART baudrate (115200 for A2M8)")
    parser.add_argument("--duration", type=float, default=15.0, help="Duration to record in seconds")
    parser.add_argument("--pwm", type=int, default=660, help="Motor PWM (0-1023, default 660)")
    parser.add_argument("--out", default="scan_run1.csv", help="Output CSV filename")
    parser.add_argument("--stop-only", action="store_true", help="Immediately stop the motor and exit")
    args = parser.parse_args()

    print(f"Connecting to RPLIDAR on {args.port} @ {args.baud} baud...")
    lidar = RPLidar(args.port, baudrate=args.baud)

    # Override rplidar library's default A1 motor methods with A2M8 PWM + DTR methods
    lidar.start_motor = lambda: start_a2_motor(lidar, args.pwm)
    lidar.stop_motor = lambda: stop_a2_motor(lidar)

    if args.stop_only:
        print("Stopping motor...")
        stop_a2_motor(lidar)
        lidar._serial.close()
        print("Motor stopped.")
        return

    try:
        info = lidar.get_info()
        health = lidar.get_health()
        print(f"Device Info:   {info}")
        print(f"Device Health: {health}")

        start_a2_motor(lidar, args.pwm)
        time.sleep(2.0)
        lidar.clean_input()

        start_time = time.time()
        scan_id = 0
        total_points = 0

        with open(args.out, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp_s", "scan_id", "quality", "angle_deg", "distance_mm"])

            print(f"Recording scans for {args.duration:.1f}s -> {args.out} ...")
            for scan in lidar.iter_scans(max_buf_meas=3000):
                now = time.time()
                elapsed = now - start_time

                min_dist = None
                min_angle = None
                for quality, angle, distance in scan:
                    if distance > 0:
                        writer.writerow([f"{now:.4f}", scan_id, quality, f"{angle:.2f}", f"{distance:.1f}"])
                        total_points += 1
                        if min_dist is None or distance < min_dist:
                            min_dist = distance
                            min_angle = angle

                scan_id += 1
                if min_dist is not None:
                    print(
                        f"[{elapsed:5.1f}s] Scan #{scan_id:03d}: {len(scan):3d} pts | "
                        f"Closest obstacle: {min_dist:6.1f} mm ({min_dist/10.0:5.1f} cm) @ {min_angle:5.1f} deg"
                    )
                else:
                    print(f"[{elapsed:5.1f}s] Scan #{scan_id:03d}: 0 valid distance points")

                if elapsed >= args.duration:
                    break

        total_elapsed = time.time() - start_time
        rate_hz = scan_id / total_elapsed if total_elapsed > 0 else 0.0
        print(
            f"\nDone! Saved {scan_id} complete scans ({total_points} valid points) "
            f"in {total_elapsed:.2f}s ({rate_hz:.2f} Hz) to {args.out}"
        )

    finally:
        print("Stopping scan and motor cleanly...")
        try:
            stop_a2_motor(lidar)
        except Exception:
            pass
        try:
            lidar._serial.close()
        except Exception:
            pass
        print("Disconnected.")


if __name__ == "__main__":
    main()
