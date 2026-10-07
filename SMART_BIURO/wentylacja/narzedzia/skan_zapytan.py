# -*- coding: utf-8 -*-
"""Skaner zapytan Fazy 2: wysyla kandydatow przez kanal komend sondy v3
i wykrywa KAZDA ramke inna niz standardowe rozgloszenie FF->40 len=17."""
import io, os, re, time, sys

CMD = r"C:\Users\Lenovo\AppData\Local\Temp\claude\C--Users-Lenovo-Desktop-Modul\c57d3366-4e7-48b3-ab20-8b5b0e566fad\scratchpad\sonda_cmd.txt"
CMD = sys.argv[1]
LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
CZEKAJ = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5


def ramki_od(offset):
    f = io.open(LOG, encoding="utf-8", errors="replace")
    f.seek(offset)
    t = f.read()
    nowy = f.tell()
    f.close()
    raw = []
    for m in re.finditer(r'\[RX\]\s*((?:[0-9A-F]{2}\s+)+)', t):
        raw += m.group(1).split()
    b = [int(x, 16) for x in raw]
    fr, i = [], 0
    while i < len(b) - 6:
        if b[i] == 0x7E and b[i+1] == 0x7E:
            dl = b[i+5]; tot = 6 + dl
            if tot <= 64 and i + tot <= len(b):
                r = b[i:i+tot]; x = 0
                for v in r[:-1]:
                    x ^= v
                if x == r[-1]:
                    fr.append(r); i += tot; continue
        i += 1
    return fr, nowy


def wyslij(linia):
    io.open(CMD, "w", encoding="utf-8").write(linia + "\n")


# kandydaci: (opis, komenda)
KAND = [
    ("oryginal XK19 (00->FF)",        "TX 7E 7E 00 FF 11 0E 00 00 02 01 89 8A BE 47 00 80 00 00 00 99"),
    ("jako centrala (40->FF)",        "TXX 7E 7E 40 FF 11 0E 00 00 02 01 89 8A BE 47 00 80 00 00 00"),
    ("do centrali (00->40)",          "TXX 7E 7E 00 40 11 0E 00 00 02 01 89 8A BE 47 00 80 00 00 00"),
    ("puste cialo (00->FF)",          "TXX 7E 7E 00 FF 11 0E 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("kod 00 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 00 01 89 8A BE 47 00 80 00 00 00"),
    ("kod 01 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 01 01 89 8A BE 47 00 80 00 00 00"),
    ("kod 03 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 03 01 89 8A BE 47 00 80 00 00 00"),
    ("kod 04 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 04 01 89 8A BE 47 00 80 00 00 00"),
    ("kod 05 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 05 01 89 8A BE 47 00 80 00 00 00"),
    ("kod 06 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 06 01 89 8A BE 47 00 80 00 00 00"),
    ("kod 08 zamiast 02",             "TXX 7E 7E 00 FF 11 0E 00 00 08 01 89 8A BE 47 00 80 00 00 00"),
    ("krotka ramka len=01",           "TXX 7E 7E 00 FF 11 01"),
    ("krotka ramka len=02",           "TXX 7E 7E 00 FF 11 02 00"),
    ("naglowek jak rozgloszenie",     "TXX 7E 7E 00 FF 11 17 09 30 83 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("dlugosc 15 wg dokumentacji",    "TXX 7E 7E 00 FF 11 15 00 00 02 01 89 8A BE 47 00 80 00 00 00 00 00 00 00 00 00 00"),
]

print("=== SKAN ZAPYTAN (Faza 2) ===", flush=True)
wyslij("STOP")
time.sleep(3)
off = os.path.getsize(LOG)
# tlo: ile roznych ramek leci samo z siebie
time.sleep(3)
fr, off = ramki_od(off)
tlo = set(tuple(f[:6]) for f in fr)
print(f"tlo (bez wysylki): {len(fr)} ramek, typy: {[f'{t[2]:02X}->{t[3]:02X} len={t[5]:02X}' for t in tlo]}", flush=True)

znaleziska = []
for opis, cmd in KAND:
    off = os.path.getsize(LOG)
    wyslij(cmd)
    time.sleep(CZEKAJ)
    fr, off = ramki_od(off)
    inne = [f for f in fr if not (f[2] == 0xFF and f[3] == 0x40 and f[5] == 0x17)]
    stat = f"{len(fr)} ramek"
    if inne:
        stat += f"  *** {len(inne)} NIETYPOWYCH ***"
        for f in inne[:3]:
            hx = ' '.join(f'{v:02X}' for v in f)
            stat += f"\n      >>> {hx}"
            znaleziska.append((opis, hx))
    print(f"[{opis}] {stat}", flush=True)

print("\n=== PODSUMOWANIE ===", flush=True)
if znaleziska:
    for opis, hx in znaleziska:
        print(f"  ODPOWIEDZ na '{opis}': {hx}", flush=True)
else:
    print("  brak jakiejkolwiek nietypowej ramki - jednostka nie reaguje na zadnego kandydata", flush=True)
wyslij("STOP")
