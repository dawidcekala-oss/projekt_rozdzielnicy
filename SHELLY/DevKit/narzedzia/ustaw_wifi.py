"""Connect the DevKit to a Wi-Fi network over USB, without the app.

Lists the 2.4 GHz networks the DevKit can see, lets you pick one by number
(so the name is copied exactly, without typos or trailing spaces), asks for
the password with hidden input and waits until the DevKit gets an address.
The password is sent only to the DevKit; it is not printed or saved.

    python ustaw_wifi.py COM5

Stop the monitor first: it holds the COM port.
"""
from __future__ import annotations

import getpass
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shelly_uart_rpc import RpcError, ShellyUart  # noqa: E402


def main() -> None:
    port = sys.argv[1] if len(sys.argv) > 1 else "COM5"
    with ShellyUart(port) as dev:
        print("Szukam sieci 2,4 GHz widocznych dla DevKitu...")
        res = dev.call("Wifi.Scan", timeout=25).get("results", [])
        best: dict[str, dict] = {}
        for r in res:
            s = r.get("ssid")
            if s and (s not in best or r.get("rssi", -100) > best[s].get("rssi", -100)):
                best[s] = r
        nets = sorted(best.values(), key=lambda r: -r.get("rssi", -100))
        if not nets:
            print("DevKit nie widzi żadnej sieci 2,4 GHz.")
            return
        for i, r in enumerate(nets, 1):
            print(f"{i:2}. {r['ssid']}   kanał {r.get('channel')}, sygnał {r.get('rssi')} dBm")
        choice = input("Numer sieci: ").strip()
        ssid = nets[int(choice) - 1]["ssid"]
        password = getpass.getpass(f"Hasło do sieci {ssid} (znaki nie będą widoczne): ")
        try:
            dev.call("Wifi.SetConfig", {"config": {"sta": {"ssid": ssid, "pass": password, "enable": True}}})
        except RpcError as e:
            print(f"DevKit odrzucił ustawienia: {e}")
            return
        finally:
            password = None
        print(f"Zapisano sieć {ssid!r}. Czekam na połączenie...")
        t0 = time.time()
        last = None
        while time.time() - t0 < 60:
            st = dev.call("Wifi.GetStatus")
            if st.get("status") != last:
                last = st.get("status")
                print(f"  {time.time() - t0:4.0f} s  {last}")
            if st.get("status") == "got ip":
                print(f"\nPołączono. Adres DevKitu w sieci: http://{st.get('sta_ip')}")
                print(f"Sygnał {st.get('rssi')} dBm, kanał {st.get('channel')}.")
                return
            time.sleep(2)
        print("\nBrak połączenia po 60 s. Najczęstsza przyczyna to błędne hasło.")
        print("Uruchom narzędzie jeszcze raz albo sprawdź log monitora.")


if __name__ == "__main__":
    main()
