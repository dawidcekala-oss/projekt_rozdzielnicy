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

import base64
import json
import os
import re
import socket
import sys
import time
import urllib.request
from datetime import datetime

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM5"
HERE = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(HERE, "..", "logi")
os.makedirs(LOGDIR, exist_ok=True)
STAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
EVENTS = open(os.path.join(LOGDIR, f"zdarzenia_{STAMP}.log"), "a", encoding="utf-8", buffering=1)
RAW = open(os.path.join(LOGDIR, f"surowy_{STAMP}.log"), "a", encoding="utf-8", buffering=1)

# Pola produktu "Q11 DevKit test" z portalu Shelly X (log: "service:0: vc ... -> ...").
# Stara mapa pol symulatora jest w monitor_devkit_symulator.py.
NAMES = {
    "boolean:200": "Ładowanie włączone (DP 18)",
    "number:200": "Limit prądu (DP 4)",
    "enum:200": "Stan ładowarki (DP 3)",
    "number:201": "Czas sesji",
    "number:202": "Energia sesji",
    "object:200": "Fazy",
}
UNITS = {"number:200": "A", "number:201": "min", "number:202": "kWh"}
SETTINGS = {"boolean:200", "number:200"}
STATES = {"enum:200"}
READOUTS = {"number:201", "number:202", "object:200"}
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
RE_STATUS = re.compile(r"Status change of ((?:enum|number|boolean|text|object):\d+): (\{.*\})\s*$")
RE_STATION = re.compile(r"station: ([0-9a-f:]{17}) (join|leave)", re.I)
RE_DHCP = re.compile(r"(192\.168\.33\.\d+)")

values: dict[str, object] = {}
last_rpc = {"channel": None, "method": None, "t": 0.0}
last_readout_print = 0.0
tmcu_state = {"silent": False}


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
    for k in ("number:202", "number:201"):
        if k in values:
            parts.append(f"{NAMES[k].lower()} {fmt(k, values[k])}")
    ph = values.get("object:200")
    if isinstance(ph, dict):
        v = [ph.get(x, {}).get("voltage", 0) for x in ("phase_a", "phase_b", "phase_c")]
        parts.append(f"moc {ph.get('total_power', 0)} W, prąd {ph.get('total_current', 0)} A, "
                     f"napięcia {'/'.join(str(x) for x in v)} V, licznik {ph.get('total_act_energy', 0)} kWh")
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
    if "Q11TEST" in line:
        emit("TEST: " + line[line.index("Q11TEST") + 8:])
        return
    if "tmcu" in line.lower():
        if "Heartbeat timed out" in line:
            if not tmcu_state["silent"]:
                tmcu_state["silent"] = True
                emit("Q11: mikrokontroler nie odpowiada (Heartbeat timed out); kolejne takie same pomijam")
            return
        # Ostrzezenia i bledy modulu (W/E), np. "Setting unknown datapoint 18" albo
        # "Initialization failed ... Expecting heartbeat", nie znacza, ze Q11 odpowiada.
        # Przy poziomie logu 3 modul co sekunde pisze, ze wysyla zapytanie (TX: 0x00 ...);
        # to nie jest odpowiedz Q11, wiec pomijamy. Za odpowiedz uznajemy tylko wiersze z RX.
        if "Process " in line or "TX: 0x00" in line:
            return
        # Rutyna, gdy Q11 odpowiada: znak zycia, pytania o godzine (0x1c) i o sile Wi-Fi (0x24),
        # stan Wi-Fi (0x03) i zdarzenia wewnetrzne. W dzienniku zdarzen zostaja zmiany punktow danych.
        if (not tmcu_state["silent"] and any(k in line for k in (
                "RX: 0x00", "Tmcu Event 1", "0x1c", "0x24", "0x03 v=3", "wifi report state",
                "Sending WiFi status", "same "))):
            return
        is_warning = line.startswith(("W ", "E "))
        if (tmcu_state["silent"] and not is_warning and "RX" in line.upper()
                and "Creating tmcu" not in line and "tmcu uart=" not in line):
            tmcu_state["silent"] = False
            emit("Q11: mikrokontroler się odezwał")
        emit(f"    TMCU: {line}")
        return
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
    if "shelly_service.cpp" in line and ("Running" in line or "terminated" in line or "Error" in line):
        emit(f"    usługa: {line}")
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


# ---------------------------------------------------------------------------
# Log przez Wi-Fi: DevKit zasilany z ladowarki, bez USB.
# Wymaga na DevKicie debug.websocket.enable = true (Sys.SetConfig), wlaczone 2026-09-24.
#     python -u monitor_devkit.py 192.168.0.238
# ---------------------------------------------------------------------------

LEVELS = {0: "E", 1: "W", 2: "I", 3: "D", 4: "V"}


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("polaczenie zamkniete")
        data += chunk
    return data


def ws_log_lines(host: str):
    """Minimalny klient WebSocket do ws://host/debug/log. Oddaje wiersze logu w formacie jak z USB."""
    while True:
        try:
            sock = socket.create_connection((host, 80), timeout=10)
            key = base64.b64encode(os.urandom(16)).decode()
            sock.sendall((f"GET /debug/log HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n"
                          f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                          f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
            head = b""
            while b"\r\n\r\n" not in head:
                chunk = sock.recv(1024)
                if not chunk:
                    raise ConnectionError("brak odpowiedzi")
                head += chunk
            status = head.split(b"\r\n", 1)[0]
            if b" 101" not in status:
                raise ConnectionError(status.decode(errors="replace"))
            rest = head.split(b"\r\n\r\n", 1)[1]
            emit(f"Log przez Wi-Fi: połączono z {host}")
            # DevKit odlaczony od zasilania nie zamyka polaczenia; po 45 s ciszy laczymy od nowa.
            sock.settimeout(45)
            pending = rest
            text = b""
            while True:
                def take(n: int) -> bytes:
                    nonlocal pending
                    if len(pending) >= n:
                        out, pending = pending[:n], pending[n:]
                        return out
                    out = pending + _recv_exact(sock, n - len(pending))
                    pending = b""
                    return out
                try:
                    b0, b1 = take(2)
                except socket.timeout:
                    raise ConnectionError("45 s bez żadnego wiersza logu")
                op, fin, ln = b0 & 0x0F, b0 & 0x80, b1 & 0x7F
                if ln == 126:
                    ln = int.from_bytes(take(2), "big")
                elif ln == 127:
                    ln = int.from_bytes(take(8), "big")
                mask = take(4) if b1 & 0x80 else None
                payload = take(ln) if ln else b""
                if mask:
                    payload = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
                if op == 8:
                    raise ConnectionError("DevKit zamknął log")
                if op == 9:  # ping -> pong (ramki klienta musza byc maskowane)
                    m = os.urandom(4)
                    sock.sendall(bytes([0x8A, 0x80 | len(payload)]) + m +
                                 bytes(c ^ m[i % 4] for i, c in enumerate(payload)))
                    continue
                if op in (0, 1):
                    text += payload
                    if not fin:
                        continue
                    for raw in text.decode("utf-8", "replace").splitlines():
                        try:
                            msg = json.loads(raw)
                            yield f"{LEVELS.get(msg.get('level'), 'I')} {msg.get('data', '').rstrip()}"
                        except ValueError:
                            yield raw
                    text = b""
        except (OSError, ConnectionError) as e:
            emit(f"Log przez Wi-Fi: brak połączenia ({e}); ponawiam za 5 s")
            time.sleep(5)


def read_start_values_http(host: str) -> None:
    for key in NAMES:
        ctype, cid = key.split(":")
        url = f"http://{host}/rpc/{ctype.capitalize()}.GetStatus?id={cid}"
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                values[key] = json.loads(r.read().decode()).get("value")
        except (OSError, ValueError):
            pass


def main_wifi(host: str) -> None:
    read_start_values_http(host)
    emit(f"Monitor DevKitu przez Wi-Fi, {host}. Ustawienia na starcie:")
    for key in NAMES:
        if key in SETTINGS or key in STATES:
            emit(f"    {NAMES[key]}: {fmt(key, values.get(key))}")
    emit(f"    odczyty: {readout_summary()}")
    try:
        for line in ws_log_lines(host):
            if line.strip():
                handle_line(line)
    except KeyboardInterrupt:
        emit("Monitor zatrzymany.")


def main() -> None:
    if not PORT.upper().startswith("COM"):
        main_wifi(PORT.replace("ws://", "").replace("http://", "").strip("/"))
        return
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
