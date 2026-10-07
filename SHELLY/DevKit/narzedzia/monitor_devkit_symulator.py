"""Live monitor of the Shelly DevKit over USB serial.

Keeps the DevKit log open while someone uses its web page from a phone.
Prints a readable Polish event feed and writes two files to ..\\logi:
    zdarzenia_<data>.log   readable events: who changed what, charger states
    surowy_<data>.log      full firmware log with laptop timestamps

    python -u monitor_devkit.py COM5

The monitor only listens, apart from reading the starting values once.
It holds the COM port, so stop it (Ctrl+C) before running other USB tools.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM5"
HERE = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(HERE, "..", "logi")
os.makedirs(LOGDIR, exist_ok=True)
STAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
EVENTS = open(os.path.join(LOGDIR, f"zdarzenia_{STAMP}.log"), "a", encoding="utf-8", buffering=1)
RAW = open(os.path.join(LOGDIR, f"surowy_{STAMP}.log"), "a", encoding="utf-8", buffering=1)

NAMES = {
    "enum:203": "Symulacja: samochód",
    "boolean:201": "Symulacja: awaria uziemienia",
    "boolean:200": "Ładowanie włączone",
    "number:200": "Limit prądu",
    "enum:202": "Tryb ładowania",
    "number:201": "Energia docelowa",
    "number:202": "Początek harmonogramu",
    "number:203": "Koniec harmonogramu",
    "text:202": "Stan ładowarki",
    "text:203": "Sygnał Control Pilot",
    "number:204": "Moc",
    "number:205": "Energia sesji",
    "number:206": "Licznik całkowity",
    "number:207": "Temperatura",
    "text:200": "Fazy",
    "text:201": "Błędy",
}
UNITS = {"number:200": "A", "number:201": "kWh", "number:202": "h", "number:203": "h",
         "number:204": "kW", "number:205": "kWh", "number:206": "kWh", "number:207": "°C"}
SETTINGS = {"enum:203", "boolean:201", "boolean:200", "number:200", "enum:202",
            "number:201", "number:202", "number:203"}
STATES = {"text:202", "text:203", "text:201"}
READOUTS = {"number:204", "number:205", "number:206", "number:207"}
TITLES = {
    "charger_free": "Wolna", "charger_insert": "Auto podłączone", "charger_free_fault": "Wolna, błąd",
    "charger_wait": "Czeka na harmonogram", "charger_charging": "Ładuje", "charger_pause": "Pauza",
    "charger_end": "Zakończone", "charger_fault": "Błąd",
    "controlpi_12v": "12 V, brak auta", "controlpi_9v": "9 V, auto podłączone",
    "controlpi_6v": "6 V, auto gotowe", "controlpi_error": "błąd sygnału",
    "charge_now": "Natychmiast", "charge_energy": "Do zadanej energii",
    "charge_schedule": "Według harmonogramu",
    "A": "A, odłączony", "B": "B, podłączony", "C": "C, gotowy do ładowania",
    True: "tak", False: "nie",
}

RE_RPC = re.compile(r"shos_rpc_inst\.c:\d+\s+(\S+) \[([^\]]*)\] via (\S+)")
RE_STATUS = re.compile(r"Status change of ((?:enum|number|boolean|text):\d+): (\{.*\})\s*$")
RE_STATION = re.compile(r"station: ([0-9a-f:]{17}) (join|leave)", re.I)
RE_DHCP = re.compile(r"(192\.168\.33\.\d+)")

values: dict[str, object] = {}
last_rpc = {"channel": None, "method": None, "t": 0.0}
last_readout_print = 0.0


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def emit(text: str) -> None:
    line = f"{now()}  {text}"
    print(line, flush=True)
    EVENTS.write(line + "\n")


def channel_name(ch: str) -> str:
    c = ch.upper()
    if "UART" in c:
        return "USB"
    if "HTTP" in c or "WS" in c:
        return "strona WWW"
    if "BLE" in c or "GATT" in c or "BT" in c:
        return "Bluetooth"
    if "LOOPBACK" in c:
        return "skrypt"
    if "MQTT" in c:
        return "MQTT"
    return ch


def fmt(key: str, v) -> str:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        s = f"{v:g}".replace(".", ",")
        return f"{s} {UNITS.get(key, '')}".strip()
    return str(TITLES.get(v, v))


def readout_summary() -> str:
    parts = []
    for k in ("number:204", "number:205", "number:206", "number:207"):
        if k in values:
            parts.append(f"{NAMES[k].lower()} {fmt(k, values[k])}")
    return " | ".join(parts)


def handle_status(key: str, payload: dict) -> None:
    global last_readout_print
    if "value" not in payload:
        return
    new = payload["value"]
    old = values.get(key)
    values[key] = new
    if old == new:
        return
    if key in SETTINGS:
        who = ""
        if last_rpc["method"] and time.time() - last_rpc["t"] < 2.0:
            who = f"[{channel_name(last_rpc['channel'])}] "
        arrow = f"{fmt(key, old)} na {fmt(key, new)}" if old is not None else fmt(key, new)
        emit(f"{who}{NAMES[key]}: {arrow}")
    elif key in STATES:
        emit(f"    {NAMES[key]}: {fmt(key, new)}")
    elif key in READOUTS and time.time() - last_readout_print >= 10:
        last_readout_print = time.time()
        emit(f"    odczyty: {readout_summary()}")


def handle_line(line: str) -> None:
    RAW.write(f"{now()} {line}\n")
    m = RE_RPC.search(line)
    if m:
        method, _, ch = m.groups()
        last_rpc.update(channel=ch, method=method, t=time.time())
        if not method.endswith(("GetStatus", "GetConfig", "GetComponents", "GetDeviceInfo",
                                "ListMethods", "List", "Get", "GetMany")) and "loopback" not in ch:
            if method.split(".")[0] not in ("Enum", "Number", "Boolean", "Text"):
                emit(f"[{channel_name(ch)}] polecenie {method}")
        elif ch.upper().startswith(("HTTP", "WS")) and method == "Shelly.GetDeviceInfo":
            emit("[strona WWW] strona DevKitu została otwarta")
        return
    m = RE_STATUS.search(line)
    if m:
        try:
            handle_status(m.group(1), json.loads(m.group(2)))
        except ValueError:
            pass
        return
    m = RE_STATION.search(line)
    if m:
        mac, what = m.groups()
        emit(f"Wi-Fi DevKitu: urządzenie {mac} {'połączyło się' if what.lower() == 'join' else 'rozłączyło się'}")
        return
    if "DHCP" in line and RE_DHCP.search(line) and "assign" in line.lower():
        emit(f"Wi-Fi DevKitu: przydzielono adres {RE_DHCP.search(line).group(1)}")
        return
    if line.startswith(("Q11 stan:", "Symulator Q11")):
        emit(f"    skrypt: {line}")
        return
    if line.startswith("E ") or " error" in line.lower() and line.startswith("W "):
        emit(f"!!  {line}")


def read_start_values(s: serial.Serial) -> None:
    """Ask once for the current value of every field so changes show old and new."""
    rid = 5000
    for key in NAMES:
        ctype, cid = key.split(":")
        rid += 1
        req = {"id": rid, "src": "monitor", "method": f"{ctype.capitalize()}.GetStatus", "params": {"id": int(cid)}}
        s.write(('"""' + json.dumps(req) + '"""\n').encode())
        deadline = time.time() + 2
        buf = ""
        while time.time() < deadline:
            buf += s.read(2048).decode("utf-8", "replace")
            mm = re.search(r'\{"id":%d,"result":(\{.*?\})\}' % rid, buf)
            if mm:
                try:
                    values[key] = json.loads(mm.group(1)).get("value")
                except ValueError:
                    pass
                break


def main() -> None:
    s = serial.Serial()
    s.port, s.baudrate, s.timeout = PORT, 115200, 0.2
    s.dtr = False   # do not reset the DevKit when the port opens
    s.rts = False
    s.open()
    time.sleep(0.3)
    s.reset_input_buffer()
    read_start_values(s)
    emit(f"Monitor DevKitu na {PORT}. Ustawienia na starcie:")
    for key in NAMES:
        if key in SETTINGS or key in STATES:
            emit(f"    {NAMES[key]}: {fmt(key, values.get(key))}")
    emit(f"    odczyty: {readout_summary()}")
    buf = ""
    try:
        while True:
            chunk = s.read(4096)
            if not chunk:
                continue
            buf += chunk.decode("utf-8", "replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.rstrip("\r")
                if line.strip():
                    handle_line(line)
    except KeyboardInterrupt:
        emit("Monitor zatrzymany.")
    finally:
        s.close()


if __name__ == "__main__":
    main()
