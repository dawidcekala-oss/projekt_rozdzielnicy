"""Podsluch lacza szeregowego miedzy modulem WBR3 a mikrokontrolerem Q11.

Do Q11 z NIERUSZONYM modulem WBR3 podlacz przejsciowke USB-UART:
    RX przejsciowki  -> pole TXD modulu (to, co nadaje modul)   albo pole RXD (to, co nadaje Q11)
    GND przejsciowki -> masa plytki
    TX i zasilanie przejsciowki: NIE podlaczac.

    python podsluch_uart.py COM7            probuje po kolei 9600 i 115200, po 15 s
    python podsluch_uart.py COM7 9600       tylko jedna predkosc, bez konca

Wypisuje kazdy bajt w hex oraz rozpoznane ramki Tuya (55 AA wersja polecenie dlugosc dane suma).
Zapisuje wszystko do ..\\logi\\podsluch_<data>.log.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime

import serial

TUYA_CMDS = {
    0x00: "heartbeat", 0x01: "info o produkcie", 0x02: "tryb pracy", 0x03: "stan Wi-Fi",
    0x04: "reset Wi-Fi", 0x05: "wybor trybu Wi-Fi", 0x06: "polecenie DP (modul->MCU)",
    0x07: "raport DP (MCU->modul)", 0x08: "zapytanie o stan", 0x0A: "aktualizacja MCU start",
    0x0B: "aktualizacja MCU dane", 0x1C: "czas lokalny", 0x2B: "stan sieci", 0x34: "rozszerzone",
    0x37: "czas/sieć rozszerzone",
}

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "logi", f"podsluch_{datetime.now():%Y-%m-%d_%H%M}.log")


def out(text: str) -> None:
    line = f"{datetime.now():%H:%M:%S.%f}"[:-3] + "  " + text
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def frames(buf: bytearray):
    """Wyciaga z bufora kompletne ramki 55 AA; zwraca (lista ramek, bajty-smieci)."""
    found, junk = [], 0
    while True:
        i = buf.find(b"\x55\xaa")
        if i < 0:
            junk += max(0, len(buf) - 1)
            del buf[:max(0, len(buf) - 1)]
            return found, junk
        junk += i
        del buf[:i]
        if len(buf) < 7:
            return found, junk
        ln = (buf[4] << 8) | buf[5]
        if ln > 1024:
            del buf[:2]
            junk += 2
            continue
        total = 6 + ln + 1
        if len(buf) < total:
            return found, junk
        fr = bytes(buf[:total])
        del buf[:total]
        found.append(fr)


def describe(fr: bytes) -> str:
    ver, cmd, ln = fr[2], fr[3], (fr[4] << 8) | fr[5]
    data = fr[6:6 + ln]
    ok = (sum(fr[:-1]) & 0xFF) == fr[-1]
    kto = "modul->MCU" if ver == 0 else "MCU->modul" if ver == 3 else f"wersja {ver}"
    opis = TUYA_CMDS.get(cmd, "nieznane")
    extra = ""
    if cmd == 0x01 and data:
        extra = "  tekst: " + data.decode("utf-8", "replace")
    return (f"RAMKA TUYA {kto}: polecenie 0x{cmd:02X} ({opis}), dane {ln} B"
            f"{'' if ok else ', ZLA SUMA'}: {data.hex(' ')}{extra}")


def listen(port: str, baud: int, seconds: float | None) -> tuple[int, int, int]:
    n_bytes = n_frames = n_junk = 0
    buf = bytearray()
    with serial.Serial(port, baud, timeout=0.2) as s:
        s.reset_input_buffer()
        out(f"--- nasluch {baud} b/s na {port}" + (f", {seconds:.0f} s" if seconds else ", Ctrl+C konczy"))
        end = time.time() + seconds if seconds else None
        while end is None or time.time() < end:
            chunk = s.read(512)
            if not chunk:
                continue
            n_bytes += len(chunk)
            out(f"bajty ({len(chunk)}): {chunk.hex(' ')}")
            buf.extend(chunk)
            fr, junk = frames(buf)
            n_junk += junk
            for f in fr:
                n_frames += 1
                out("    " + describe(f))
    out(f"--- {baud} b/s: bajtow {n_bytes}, ramek Tuya {n_frames}, bajtow poza ramkami {n_junk}")
    return n_bytes, n_frames, n_junk


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    port = sys.argv[1]
    if len(sys.argv) > 2:
        listen(port, int(sys.argv[2]), None)
        return
    wyniki = {b: listen(port, b, 15) for b in (9600, 115200)}
    out("=== PODSUMOWANIE")
    for b, (nb, nf, nj) in wyniki.items():
        out(f"    {b:>6} b/s: bajtow {nb}, ramek Tuya {nf}, smieci {nj}")
    best = max(wyniki, key=lambda b: wyniki[b][1])
    if wyniki[best][1]:
        out(f"    Rozmowa w protokole Tuya przy {best} b/s.")
    elif any(v[0] for v in wyniki.values()):
        out("    Sa bajty, ale bez ramek Tuya: inna predkosc albo inny protokol. Przyslij log.")
    else:
        out("    Cisza przy obu predkosciach: sprawdz podlaczenie RX i masy przejsciowki.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("Zatrzymano.")
