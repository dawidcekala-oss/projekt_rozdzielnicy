"""Remove the virtual Q11 charger from the DevKit and undo its settings.

Deletes the simulator script, its virtual components and group, the saved
energy counter and the device name and time zone set by the installer.
For a byte-exact return to the delivered state restore the flash backup
instead (see README).

    python usun_symulator.py COM5
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "narzedzia"))
sys.path.insert(0, HERE)
from shelly_uart_rpc import RpcError, ShellyUart  # noqa: E402
from zainstaluj_symulator import remove_previous  # noqa: E402


def main() -> None:
    port = sys.argv[1] if len(sys.argv) > 1 else "COM5"
    with ShellyUart(port) as dev:
        remove_previous(dev)
        try:
            dev.call("KVS.Delete", {"key": "q11_sim_total_kwh"})
            print("  usunięto zapisany licznik")
        except RpcError:
            pass
        dev.call("Sys.SetConfig", {"config": {"location": {"tz": None}, "device": {"name": None}}})
        print("Symulator usunięty. Nazwa urządzenia i strefa czasowa jak przed instalacją.")


if __name__ == "__main__":
    main()
