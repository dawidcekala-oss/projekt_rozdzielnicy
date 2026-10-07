"""Set the DevKit clock from the laptop.

The DevKit has no battery-backed clock. Without internet it forgets the time
on every restart, and the schedule mode of the simulator then waits forever.
Once the DevKit is on a Wi-Fi network with internet access it syncs by itself.

    python ustaw_zegar.py COM5
"""
from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "narzedzia"))
from shelly_uart_rpc import ShellyUart  # noqa: E402

port = sys.argv[1] if len(sys.argv) > 1 else "COM5"
with ShellyUart(port) as dev:
    dev.call("Sys.SetTime", {"unixtime": int(time.time())})
    print("Czas urządzenia:", dev.call("Sys.GetStatus").get("time"))
