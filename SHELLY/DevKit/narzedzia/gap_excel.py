# Q11 comparison table: Tuya WBR3 module vs Shelly X module (confirmed facts only).
# python gap_excel.py <output.xlsx>
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OUT = sys.argv[1]

FILL = {"✔": "C6EFCE", "◐": "FFEB9C", "✘": "FFC7CE", "?": "E7E6E6"}
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")

ROWS = [
    "Control and apps",
    ("Mobile app, with internet", "✔ Tuya Smart / Smart Life via Tuya cloud", "✔ Shelly Smart Control via Shelly cloud", "use; B1 control test"),
    ("Mobile app on the LAN without cloud", "✘ app needs Tuya cloud", "✘ app shows offline; it only probes the device locally", "B1"),
    ("Local web page on the charger", "✘ none", "◐ yes, no login; default screen shows 6 of 15 fields, phases as \"N/A A\"", "B2"),
    ("Local API", "◐ no official API; unofficial local protocol with device key (tuya_local in Home Assistant)", "✔ HTTP and WebSocket JSON-RPC, documented; read 40–150 ms, write confirmed by controller in 1–2 s", "B7, C4"),
    ("MQTT", "✘", "✔ commands and events through a local broker (also without internet) and through an internet broker (public test broker: command and reply in ~1.1 s)", "C4, 01.10"),
    ("Push to own server", "✘ only via Tuya cloud API", "✔ outbound WebSocket (reconnect ≤ ~60 s) and webhooks on state / limit / switch changes (~1 s)", "B5, B8"),
    ("OCPP 1.6J", "✘", "◐ no OCPP client in the module; our bridge (on a PC/server, uses the local API) works: registration, status, meter values every 30 s, current limit from the OCPP server, full transaction start/stop; also without internet (OCPP server on the LAN). OCPP server on the internet not tested", "25.09, 01.10"),
    ("Home Assistant", "◐ official Tuya integration and our custom integration, both via Tuya cloud", "◐ official Shelly integration is local, but for our product shows only 12 phase sensors (EV controls are enabled only for TopAC EVE01); with our patch 33 entities, full local control", "B3"),
    ("Works without internet", "✘ app and remote control lost; charger menu only", "✔ web page, API, MQTT, Home Assistant, schedules and webhooks work; time from a LAN time server", "C2–C9"),
    "Charging control (same charger controller)",
    ("Start / stop charging (switch)", "✔ from the app", "◐ start ✔; stop refused by the controller in 3 of 6 tests, cause open", "B3c, 30.09"),
    ("Current limit 6–16 A", "✔", "✔ confirmed in 1–2 s, value shown on the charger display", "C2"),
    ("Mode: now / energy / time window", "✔", "✔", "B3c"),
    ("Energy limit per session (1–200 kWh)", "✔", "✔", "B3c"),
    ("Time window for one session (full hours)", "✔", "✔ controller starts and stops on module time (22:00:03 start, 23:00:03 stop)", "C6"),
    ("Delay and duration from the charger menu", "◐ works; wrong values shown when set in state C", "◐ same; the module does not see the setting", "30.09"),
    ("Phase voltage / current / power", "◐ sent by controller, not shown in Tuya app", "✔ web page, Home Assistant, Shelly app", "B2, B3"),
    ("Charging state, CP signal, temperature, faults, controller version", "◐ sent by controller; app shows state", "✔ all as fields; version \"V1\" reported after power-on", "B3, 30.09"),
    ("Session energy and time", "◐ last-session energy only; live value calculated in Home Assistant", "✔ calculated in the module (lost at power loss)", "B3, 04"),
    "Automation",
    ("Schedules", "◐ in Tuya cloud (ran with the phone offline)", "✔ in the module, to the second, also without internet; ✘ after power loss without a time source they run on a stale clock", "B4, C7, 04"),
    ("Scenes / automations", "✔ Tuya cloud scenes (time, weather, devices)", "◐ webhooks and scripts in the module; scenes in Shelly cloud", "B5"),
    ("Own logic in the device", "✘", "✔ JavaScript service in the module (our translator runs there)", "B, C"),
    "Reliability",
    ("Module restart while charging", "?", "✔ charging not interrupted (5 restarts, ~30 s each)", "C9"),
    ("After power loss", "? (controller loses time window and menu delay with both modules)", "✔ module restores all its settings, writes nothing to the controller at boot; charging resumes by itself; current limit kept", "04, C8"),
    ("Link to the charger controller (Tuya MCU protocol, UART 9600)", "✔ native", "◐ works; once stuck > 3 min after reboot, retries can reorder commands, unchanged replies not reported", "B3c, B12, 30.09"),
    ("Network icon on the charger display", "✔ real state", "✘ always \"cloud connected\"; icon blinks", "C5"),
    ("Wi-Fi reset from charger menu, controller update via module", "✔", "? not tested", ""),
    "Memory",
    ("Flash / RAM", "2 MB / 256 kB", "8 MB (two 3 MB program copies, 896 kB file system) / 400 kB (117 kB free after boot)", "datasheet, backup"),
    ("Stored in the module", "◐ Wi-Fi and device keys; product definition, schedules and scenes in Tuya cloud", "✔ product definition, service script, schedules, webhooks, key-value store, web page; all survive power loss", "04"),
    ("Saving changed settings", "n/a", "◐ at most every ~3 s; changes from the last ~3 s are lost at power loss", "04"),
    "Security and updates",
    ("Local access protection", "◐ local protocol needs the device key", "✘ no password by default (password option exists)", "B2, B12"),
    ("Configuration backup", "✘", "◐ available; unencrypted, includes Wi-Fi password", "B10"),
    ("Updates", "✔ module and controller via Tuya / factory", "✔ service uploaded by us, Wi-Fi kept; controller update via module not tested", "29.09"),
]

wb = Workbook()
ws = wb.active
ws.title = "Tuya vs Shelly"
ws.append(["Q11 portable EV charger: Tuya WBR3 module vs Shelly X module — confirmed facts"])
ws["A1"].font = Font(bold=True, size=13)
ws.append(["AMPERE POINT · Dawid Cekała · 01.10.2026 · Shelly: DevKit M1, firmware 2.0.0-beta11, our service v4.3.1 · tests 29.09–01.10 without cloud and without internet, EV simulator"])
ws.append(["✔ yes / works   ◐ partly / with limitation   ✘ no   ? not tested"])
ws.append([])
header = ["Function", "Q11 with Tuya WBR3", "Q11 with Shelly X", "Confirmed by"]
ws.append(header)
hr = ws.max_row
for c in range(1, 5):
    cell = ws.cell(row=hr, column=c)
    cell.fill = PatternFill("solid", fgColor="1F4E78")
    cell.font = Font(bold=True, color="FFFFFF")
    cell.alignment, cell.border = WRAP, BORDER
for r in ROWS:
    if isinstance(r, str):
        ws.append([r])
        row = ws.max_row
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        cell = ws.cell(row=row, column=1)
        cell.fill, cell.font = PatternFill("solid", fgColor="D9E1F2"), Font(bold=True)
        continue
    ws.append(list(r))
    row = ws.max_row
    for c in range(1, 5):
        cell = ws.cell(row=row, column=c)
        cell.alignment, cell.border = WRAP, BORDER
        if c in (2, 3):
            sym = str(cell.value).strip()[:1]
            if sym in FILL:
                cell.fill = PatternFill("solid", fgColor=FILL[sym])
for col, w in zip("ABCD", (40, 48, 64, 16)):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "B%d" % (hr + 1)
wb.save(OUT)
print("saved", OUT, "rows", len([r for r in ROWS if not isinstance(r, str)]))
