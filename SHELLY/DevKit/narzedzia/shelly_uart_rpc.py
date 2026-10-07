"""Minimal RPC client for Shelly OS over the DevKit USB serial port.

The firmware exposes an RPC channel on UART0 (the port behind the DevKit's
USB-UART bridge). A request is a JSON-RPC object wrapped in triple quotes:
    \"\"\"{"id":1,"src":"laptop","method":"Shelly.GetDeviceInfo"}\"\"\"
The device answers with a JSON line carrying the same id. Log lines from the
firmware share the same port and are skipped.

Usage as a library:
    with ShellyUart("COM5") as dev:
        info = dev.call("Shelly.GetDeviceInfo")
Usage from the command line, parameters as JSON or as key=value pairs:
    python shelly_uart_rpc.py COM5 Shelly.GetStatus
    python shelly_uart_rpc.py COM5 Number.Set '{"id":200,"value":10}'
    python shelly_uart_rpc.py COM5 Enum.Set id=203 value=C
"""
from __future__ import annotations

import json
import sys
import time

import serial


class RpcError(Exception):
    pass


class ShellyUart:
    def __init__(self, port: str = "COM5", baud: int = 115200):
        self.s = serial.Serial()
        self.s.port = port
        self.s.baudrate = baud
        self.s.timeout = 0.1
        # keep EN and GPIO9 released: opening the port must not reset the chip
        self.s.dtr = False
        self.s.rts = False
        self._id = 100
        self._buf = ""

    def __enter__(self) -> "ShellyUart":
        self.s.open()
        time.sleep(0.2)
        self.s.reset_input_buffer()
        self.sync()
        return self

    def sync(self) -> None:
        """Make sure the device's frame parser is in step with us.

        If an earlier frame arrived cut, the device keeps a frame open and
        every later frame is read shifted by one delimiter, so nothing gets
        an answer. A lone delimiter closes the dangling frame.
        """
        for attempt in range(3):
            try:
                self.call("Shelly.GetDeviceInfo", timeout=3.0 + 2.0 * attempt)
                return
            except (TimeoutError, RpcError):
                if attempt == 1:
                    # Two silent tries: assume a dangling frame and close it.
                    self.s.write(b'"""\n')
                    self.s.flush()
                time.sleep(0.5)
                self.s.reset_input_buffer()
                self._buf = ""
        raise TimeoutError("device does not answer on the serial RPC channel; "
                           "reset it (unplug USB or press RST) and try again")

    def __exit__(self, *exc) -> None:
        self.s.close()

    def call(self, method: str, params: dict | None = None, timeout: float = 5.0):
        self._id += 1
        req = {"id": self._id, "src": "laptop", "method": method}
        if params is not None:
            req["params"] = params
        body = ('"""' + json.dumps(req, ensure_ascii=False, separators=(",", ":"))).encode("utf-8")
        # The body goes in small pieces so a busy device does not overflow its
        # UART input. The closing delimiter goes last, whole and after a short
        # gap: the device does not recognise a delimiter split across two reads,
        # and a missed delimiter shifts every later frame by one.
        for i in range(0, len(body), 48):
            self.s.write(body[i:i + 48])
            self.s.flush()
            time.sleep(0.008)
        time.sleep(0.02)
        self.s.write(b'"""\n')
        self.s.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            chunk = self.s.read(4096)
            if chunk:
                self._buf += chunk.decode("utf-8", errors="replace")
            while "\n" in self._buf:
                line, self._buf = self._buf.split("\n", 1)
                line = line.strip().strip('"')
                if not line.startswith("{"):
                    continue
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                if msg.get("id") != self._id:
                    continue
                if "error" in msg:
                    raise RpcError(f"{method}: {msg['error']}")
                return msg.get("result")
        raise TimeoutError(f"no answer to {method} within {timeout} s")


def parse_params(args: list[str]) -> dict | None:
    if not args:
        return None
    if args[0].lstrip().startswith("{"):
        return json.loads(args[0])
    params = {}
    for pair in args:
        key, _, raw = pair.partition("=")
        try:
            params[key] = json.loads(raw)   # numbers, true/false, null
        except ValueError:
            params[key] = raw               # anything else stays a string
    return params


if __name__ == "__main__":
    port, method = sys.argv[1], sys.argv[2]
    params = parse_params(sys.argv[3:])
    with ShellyUart(port) as dev:
        print(json.dumps(dev.call(method, params), indent=2, ensure_ascii=False))
