"""Install the virtual Q11 charger on the Shelly DevKit over USB serial.

Creates the virtual components, groups them, sets the clock and time zone,
uploads symulator_q11.js as an auto-starting script and starts it.
Running it again removes the previous installation first.

    python zainstaluj_symulator.py COM5
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "narzedzia"))
from shelly_uart_rpc import RpcError, ShellyUart  # noqa: E402

SCRIPT_NAME = "symulator_q11"
GROUP_NAME = "Ładowarka Q11 (symulacja)"

STATE_TITLES = {
    "charger_free": "Wolna",
    "charger_insert": "Auto podłączone",
    "charger_free_fault": "Wolna, błąd",
    "charger_wait": "Czeka na harmonogram",
    "charger_charging": "Ładuje",
    "charger_pause": "Pauza",
    "charger_end": "Zakończone",
    "charger_fault": "Błąd",
}
CP_TITLES = {
    "controlpi_12v": "12 V: brak auta",
    "controlpi_9v": "9 V: auto podłączone",
    "controlpi_6v": "6 V: auto gotowe",
    "controlpi_error": "Błąd sygnału",
}
MODE_TITLES = {
    "charge_now": "Natychmiast",
    "charge_energy": "Do zadanej energii",
    "charge_schedule": "Według harmonogramu",
}
CAR_TITLES = {
    "A": "A: odłączony",
    "B": "B: podłączony, czeka",
    "C": "C: gotowy do ładowania",
}


def enum(cid, name, titles, view, default, persisted=False):
    return ("enum", cid, {
        "name": name,
        "options": list(titles),
        "default_value": default,
        "persisted": persisted,
        "meta": {"ui": {"view": view, "titles": titles}},
    })


def number(cid, name, lo, hi, unit, view, default=0, step=None, persisted=False):
    ui = {"view": view, "unit": unit}
    if step is not None:
        ui["step"] = step
    return ("number", cid, {
        "name": name, "min": lo, "max": hi, "default_value": default,
        "persisted": persisted, "meta": {"ui": ui},
    })


def boolean(cid, name, titles, default, persisted=False):
    return ("boolean", cid, {
        "name": name, "default_value": default, "persisted": persisted,
        "meta": {"ui": {"view": "toggle", "titles": titles}},
    })


def text(cid, name, default):
    return ("text", cid, {
        "name": name, "max_len": 255, "default_value": default,
        "persisted": False, "meta": {"ui": {"view": "label"}},
    })


# Charger state and Control Pilot state are text fields, not enums: in web UI
# 2.0.0-xc3 an enum in "label" view always renders an <img> (the value is
# always a key of the images map), so it showed an empty picture. The Tuya
# codes (charger_free, controlpi_12v...) travel in the script's q11_state
# event instead. The storage for virtual components holds 5376 bytes, which
# the 17 elements below fill almost completely: there is no room for extra
# enums with long title lists.
HIDDEN_FROM_GROUP: set[str] = set()

# Order here is the order of the group shown on the web page:
# vehicle simulation first, then charger controls, then read-outs.
COMPONENTS = [
    enum(203, "Symulacja: samochód", CAR_TITLES, "dropdown", "A"),
    boolean(201, "Symulacja: awaria uziemienia", ["Brak", "Awaria"], False),
    boolean(200, "Ładowanie włączone", ["Wyłączone", "Włączone"], True, persisted=True),
    number(200, "Limit prądu", 6, 16, "A", "slider", 16, step=1, persisted=True),
    enum(202, "Tryb ładowania", MODE_TITLES, "dropdown", "charge_now", persisted=True),
    number(201, "Energia docelowa", 1, 200, "kWh", "field", 10, step=1, persisted=True),
    number(202, "Początek harmonogramu", 0, 23, "h", "field", 22, step=1, persisted=True),
    number(203, "Koniec harmonogramu", 0, 23, "h", "field", 6, step=1, persisted=True),
    text(202, "Stan ładowarki", STATE_TITLES["charger_free"]),
    text(203, "Sygnał Control Pilot", CP_TITLES["controlpi_12v"]),
    number(204, "Moc", 0, 30, "kW", "label"),
    number(205, "Energia sesji", 0, 1000, "kWh", "label"),
    number(206, "Licznik całkowity", 0, 1000000, "kWh", "label"),
    number(207, "Temperatura", -40, 200, "°C", "label", 23),
    text(200, "Fazy L1 / L2 / L3", "-"),
    text(201, "Błędy", "brak"),
]


def remove_previous(dev: ShellyUart) -> None:
    for s in dev.call("Script.List").get("scripts", []):
        if s.get("name") == SCRIPT_NAME:
            if s.get("running"):
                dev.call("Script.Stop", {"id": s["id"]})
            dev.call("Script.Delete", {"id": s["id"]})
            print(f"  usunięto poprzedni skrypt id={s['id']}")
    # The device returns components in pages; walk all of them.
    comps, offset = [], 0
    while True:
        page = dev.call("Shelly.GetComponents", {"dynamic_only": True, "offset": offset})
        batch = page.get("components", [])
        comps += batch
        offset += len(batch)
        if not batch or offset >= page.get("total", offset):
            break
    # enum:200 and enum:201 belonged to the first version of the simulator
    ours = {f"{t}:{i}" for t, i, _ in COMPONENTS} | {"enum:200", "enum:201"}
    for c in comps:
        key = c.get("key", "")
        is_our_group = key.startswith("group:") and c.get("config", {}).get("name") == GROUP_NAME
        if key in ours or is_our_group:
            dev.call("Virtual.Delete", {"key": key})
            print(f"  usunięto {key}")


def upload_script(dev: ShellyUart, code: str) -> int:
    sid = dev.call("Script.Create", {"name": SCRIPT_NAME})["id"]
    chunk = 700
    for i in range(0, len(code), chunk):
        dev.call("Script.PutCode", {"id": sid, "code": code[i:i + chunk], "append": i > 0})
    dev.call("Script.SetConfig", {"id": sid, "config": {"enable": True}})
    dev.call("Script.Start", {"id": sid})
    return sid


def main() -> None:
    port = sys.argv[1] if len(sys.argv) > 1 else "COM5"
    code = open(os.path.join(HERE, "symulator_q11.js"), encoding="utf-8").read()
    with ShellyUart(port) as dev:
        info = dev.call("Shelly.GetDeviceInfo")
        print(f"Urządzenie {info['id']}, oprogramowanie {info['ver']}")

        print("1. Porządki po poprzedniej instalacji")
        remove_previous(dev)

        print("2. Zegar i strefa czasowa")
        dev.call("Sys.SetConfig", {"config": {"location": {"tz": "Europe/Warsaw"},
                                              "device": {"name": "Q11 symulator (DevKit)"}}})
        try:
            dev.call("Sys.SetTime", {"unixtime": int(time.time())})
            print("  zegar ustawiony z laptopa")
        except RpcError as e:
            print(f"  zegara nie ustawiono: {e}")

        print("3. Pola ładowarki")
        keys = []
        for ctype, cid, cfg in COMPONENTS:
            dev.call("Virtual.Add", {"type": ctype, "id": cid, "config": cfg})
            if f"{ctype}:{cid}" not in HIDDEN_FROM_GROUP:
                keys.append(f"{ctype}:{cid}")
            print(f"  {ctype}:{cid:<4} {cfg['name']}")
        gid = dev.call("Virtual.Add", {"type": "group", "config": {"name": GROUP_NAME}})["id"]
        dev.call("Group.Set", {"id": gid, "value": keys})
        print(f"  group:{gid} {GROUP_NAME} ({len(keys)} pól)")

        print("4. Skrypt symulatora")
        sid = upload_script(dev, code)
        time.sleep(3)
        st = dev.call("Script.GetStatus", {"id": sid})
        print(f"  skrypt id={sid}, działa={st.get('running')}, błędy={st.get('errors', [])}")

        print("5. Kontrola")
        state = dev.call("Text.GetStatus", {"id": 202})["value"]
        cp = dev.call("Text.GetStatus", {"id": 203})["value"]
        print(f"  stan ładowarki: {state}, sygnał CP: {cp}")
        sysst = dev.call("Sys.GetStatus")
        print(f"  czas urządzenia: {sysst.get('time')}, strefa: UTC{sysst.get('utc_offset', 0) // 3600:+d}")


if __name__ == "__main__":
    main()
