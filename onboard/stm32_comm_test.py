#!/usr/bin/env python3
"""
Pi <-> STM32 (NUCLEO-F103RB) Bidirectional Serial Communication & Telemetry Test.
Tests ASCII PING/PONG protocol, measures round-trip time (RTT), tests invalid-line
rejection, and logs any incoming SEN0253 (BNO055) IMU telemetry lines.
"""
import argparse
import json
import time
import serial

DEFAULT_BY_ID = "/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066DFF485753667187154458-if02"
DEFAULT_PORT = "/dev/ttyACM0"


def resolve_port(requested_port: str) -> str:
    import os
    if os.path.exists(requested_port):
        return requested_port
    if os.path.exists(DEFAULT_BY_ID):
        return DEFAULT_BY_ID
    return DEFAULT_PORT


def run_reconnect_test(port_hint: str, baud: int, log_out: str | None = None):
    import os
    print("=== Pi <-> STM32 Physical Disconnect & Reconnect Test ===")
    port = resolve_port(port_hint)

    # Phase 1: Pre-disconnect PINGs
    print(f"[Phase 1] Opening {port} and verifying 3 pre-disconnect PINGs...")
    pre_pongs = 0
    ser = serial.Serial(port=port, baudrate=baud, timeout=0.2, write_timeout=0.5)
    ser.write(b"\nSTREAM OFF\n")
    ser.flush()
    time.sleep(0.15)
    ser.reset_input_buffer()

    for i in range(1, 4):
        t0 = time.time()
        ser.write(b"PING\n")
        ser.flush()
        while time.time() - t0 < 0.4:
            line = ser.readline().decode("ascii", errors="replace").strip()
            if line == "PONG":
                rtt = (time.time() - t0) * 1000.0
                pre_pongs += 1
                print(f"  [Pre-disconnect {i}/3] PING -> PONG (RTT = {rtt:.2f} ms)")
                break
        time.sleep(0.3)

    # Phase 2: Wait for user to unplug USB cable
    print("\n>>> ACTION REQUIRED: Unplug the STM32 USB cable from the Raspberry Pi NOW! <<<")
    t_wait_unplug = time.time()
    disconnect_detected_at = None
    while time.time() - t_wait_unplug < 30.0:
        try:
            if not os.path.exists(port) and not os.path.exists(DEFAULT_PORT):
                disconnect_detected_at = time.time()
                print("  [DISCONNECT DETECTED] Serial device path removed from /dev!")
                break
            ser.write(b"PING\n")
            ser.flush()
            raw = ser.readline()
        except Exception as e:
            disconnect_detected_at = time.time()
            print(f"  [DISCONNECT DETECTED] Serial exception on unplug: {type(e).__name__}: {e}")
            break
        time.sleep(0.25)

    try:
        ser.close()
    except Exception:
        pass

    if disconnect_detected_at is None:
        print("ERROR: No USB disconnect detected within 30 seconds.")
        return

    # Ensure device path disappears completely before waiting for reconnect
    while os.path.exists(DEFAULT_BY_ID) or os.path.exists(DEFAULT_PORT):
        time.sleep(0.1)

    print("\n>>> ACTION REQUIRED: Now plug the STM32 USB cable BACK IN! <<<")
    reconnect_detected_at = None
    new_port = None
    t_wait_replug = time.time()
    while time.time() - t_wait_replug < 30.0:
        if os.path.exists(DEFAULT_BY_ID):
            new_port = DEFAULT_BY_ID
            reconnect_detected_at = time.time()
            break
        if os.path.exists(DEFAULT_PORT):
            new_port = DEFAULT_PORT
            reconnect_detected_at = time.time()
            break
        time.sleep(0.2)

    if reconnect_detected_at is None or new_port is None:
        print("ERROR: No USB reconnect detected within 30 seconds.")
        return

    unplug_duration_s = reconnect_detected_at - disconnect_detected_at
    print(f"  [RECONNECT DETECTED] {new_port} re-enumerated after {unplug_duration_s:.2f} s!")
    print("  Waiting 3.6s for STM32 boot (700ms delay + I2C_Scan) & ST-LINK VCP initialization...")
    time.sleep(3.6)

    # Phase 3: Post-reconnect verification
    post_pongs = 0
    post_status = None
    post_rtts = []
    with serial.Serial(port=new_port, baudrate=baud, timeout=0.2, write_timeout=0.5) as ser2:
        ser2.write(b"\nSTREAM OFF\n")
        ser2.flush()
        time.sleep(0.15)
        ser2.reset_input_buffer()

        ser2.write(b"STATUS\n")
        ser2.flush()
        t_st = time.time()
        while time.time() - t_st < 0.5:
            line = ser2.readline().decode("ascii", errors="replace").strip()
            if line.startswith("STATUS "):
                post_status = line
                print(f"  [Post-reconnect STATUS] {line}")
                break

        for i in range(1, 6):
            t0 = time.time()
            ser2.write(b"PING\n")
            ser2.flush()
            while time.time() - t0 < 0.4:
                line = ser2.readline().decode("ascii", errors="replace").strip()
                if line == "PONG":
                    rtt = (time.time() - t0) * 1000.0
                    post_pongs += 1
                    post_rtts.append(rtt)
                    print(f"  [Post-reconnect {i}/5] PING -> PONG (RTT = {rtt:.2f} ms)")
                    break
            time.sleep(0.2)

    result = {
        "test": "disconnect_reconnect",
        "pre_disconnect_pongs": f"{pre_pongs}/3",
        "disconnect_detected": True,
        "unplug_duration_s": round(unplug_duration_s, 2),
        "re_enumerated_port": new_port,
        "post_reconnect_status": post_status,
        "post_reconnect_pongs": f"{post_pongs}/5",
        "post_reconnect_mean_rtt_ms": round(sum(post_rtts) / len(post_rtts), 2) if post_rtts else None,
    }
    print("\n=== Disconnect & Reconnect Summary ===")
    for k, v in result.items():
        print(f"  {k:30s}: {v}")
    if log_out:
        with open(log_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Saved reconnect log to {log_out}")


def main():
    parser = argparse.ArgumentParser(description="Test Pi <-> STM32 USART2 communication.")
    parser.add_argument("--port", default=DEFAULT_BY_ID, help="Serial device path")
    parser.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    parser.add_argument("--count", type=int, default=10, help="Number of PING requests to send")
    parser.add_argument("--interval", type=float, default=0.5, help="Interval between PINGs in seconds")
    parser.add_argument("--log-out", default=None, help="Optional JSON log output path")
    parser.add_argument("--reconnect-test", action="store_true", help="Run interactive USB unplug/replug test")
    args = parser.parse_args()

    if args.reconnect_test:
        run_reconnect_test(args.port, args.baud, args.log_out)
        return

    port = resolve_port(args.port)
    print(f"Opening STM32 serial link on {port} @ {args.baud} 8N1...")

    events = []
    ping_sent = 0
    pong_received = 0
    rtts_ms = []
    imu_lines = []

    with serial.Serial(
        port=port,
        baudrate=args.baud,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        write_timeout=1.0,
    ) as ser:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Listen briefly for any periodic startup/IMU messages
        print("=== Listening 1.5s for periodic STM32 telemetry ===")
        t0 = time.time()
        while time.time() - t0 < 1.5:
            raw = ser.readline()
            if raw:
                line = raw.decode("ascii", errors="replace").strip()
                if line:
                    print(f"  [RX telemetry] {line}")
                    imu_lines.append({"t": round(time.time(), 4), "line": line})

        # Send an initial newline to flush any partial bytes in STM32's uart_line_buffer,
        # then query HELP to discover onboard firmware commands.
        ser.write(b"\n")
        ser.flush()
        time.sleep(0.1)
        ser.reset_input_buffer()

        print("=== Querying STM32 Onboard Firmware Commands (TX: HELP\\n) ===")
        ser.write(b"HELP\n")
        ser.flush()
        help_lines = []
        t_help = time.time()
        while time.time() - t_help < 0.6:
            raw = ser.readline()
            if raw:
                line = raw.decode("ascii", errors="replace").strip()
                if line and "BNO055" not in line:
                    print(f"  [RX HELP] {line}")
                    help_lines.append(line)

        print("\n=== Querying STM32 STATUS & Muting Unconnected IMU Stream (TX: STREAM OFF\\n, STATUS\\n) ===")
        ser.write(b"STREAM OFF\n")
        ser.flush()
        time.sleep(0.1)
        ser.write(b"STATUS\n")
        ser.flush()
        status_lines = []
        t_stat = time.time()
        while time.time() - t_stat < 0.5:
            raw = ser.readline()
            if raw:
                line = raw.decode("ascii", errors="replace").strip()
                if line:
                    print(f"  [RX STATUS] {line}")
                    status_lines.append(line)

        print(f"\n=== Sending {args.count} PING\\n requests ===")
        for i in range(1, args.count + 1):
            t_send = time.time()
            ser.write(b"PING\n")
            ser.flush()
            ping_sent += 1

            got_pong = False
            deadline = t_send + 0.4
            while time.time() < deadline:
                raw = ser.readline()
                if not raw:
                    continue
                t_rx = time.time()
                line = raw.decode("ascii", errors="replace").strip()
                if line == "PONG":
                    rtt = (t_rx - t_send) * 1000.0
                    rtts_ms.append(rtt)
                    pong_received += 1
                    got_pong = True
                    print(f"  [{i:02d}/{args.count:02d}] TX: PING\\n -> RX: PONG\\n (RTT = {rtt:.2f} ms)")
                    events.append({"seq": i, "tx": "PING", "rx": "PONG", "rtt_ms": round(rtt, 2)})
                    break
                elif line:
                    print(f"  [RX async] {line}")
                    imu_lines.append({"t": round(t_rx, 4), "line": line})

            if not got_pong:
                print(f"  [{i:02d}/{args.count:02d}] TX: PING\\n -> TIMEOUT (no PONG within 400 ms)")
                events.append({"seq": i, "tx": "PING", "rx": None, "rtt_ms": None})

            time.sleep(args.interval)

        # Test unrecognized line rejection (per CONTROL_INTERFACE.md: sends no response)
        print("\n=== Testing unrecognized command rejection (TX: INVALID_CMD\\n) ===")
        ser.write(b"INVALID_CMD\n")
        ser.flush()
        unexpected_pong = False
        t_inv = time.time()
        while time.time() - t_inv < 0.4:
            raw = ser.readline()
            if raw:
                line = raw.decode("ascii", errors="replace").strip()
                if line == "PONG":
                    unexpected_pong = True
                elif line:
                    print(f"  [RX async during invalid test] {line}")
                    imu_lines.append({"t": round(time.time(), 4), "line": line})
        print(f"  Unrecognized command ignored (no PONG): {not unexpected_pong}")

        # Verify immediate recovery with one final PING\r\n (CRLF test)
        print("\n=== Testing CRLF compatibility & recovery (TX: PING\\r\\n) ===")
        t_send = time.time()
        ser.write(b"PING\r\n")
        ser.flush()
        crlf_ok = False
        while time.time() - t_send < 0.4:
            raw = ser.readline()
            if raw:
                line = raw.decode("ascii", errors="replace").strip()
                if line == "PONG":
                    rtt = (time.time() - t_send) * 1000.0
                    crlf_ok = True
                    print(f"  TX: PING\\r\\n -> RX: PONG\\n (RTT = {rtt:.2f} ms)")
                    break
                elif line:
                    imu_lines.append({"t": round(time.time(), 4), "line": line})

    summary = {
        "port": port,
        "baudrate": args.baud,
        "ping_sent": ping_sent,
        "pong_received": pong_received,
        "packet_loss_pct": round((1.0 - pong_received / max(ping_sent, 1)) * 100.0, 2),
        "mean_rtt_ms": round(sum(rtts_ms) / len(rtts_ms), 2) if rtts_ms else None,
        "min_rtt_ms": round(min(rtts_ms), 2) if rtts_ms else None,
        "max_rtt_ms": round(max(rtts_ms), 2) if rtts_ms else None,
        "invalid_cmd_ignored": not unexpected_pong,
        "crlf_ping_accepted": crlf_ok,
        "async_telemetry_lines_received": len(imu_lines),
        "events": events,
        "telemetry_sample": imu_lines[:10],
    }

    print("\n=== Pi <-> STM32 Communication Summary ===")
    for k in [
        "port",
        "baudrate",
        "ping_sent",
        "pong_received",
        "packet_loss_pct",
        "mean_rtt_ms",
        "min_rtt_ms",
        "max_rtt_ms",
        "invalid_cmd_ignored",
        "crlf_ping_accepted",
        "async_telemetry_lines_received",
    ]:
        print(f"  {k:32s}: {summary[k]}")

    if args.log_out:
        with open(args.log_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Saved JSON test log to {args.log_out}")


if __name__ == "__main__":
    main()
