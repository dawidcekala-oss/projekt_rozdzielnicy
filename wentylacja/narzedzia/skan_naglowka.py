# -*- coding: utf-8 -*-
"""Przemiat pol naglowka ramki zapytania: src [2], dst [3], klasa [4].
Uzycie: python skan_naglowka.py <plik_komend> [czekaj_s]"""
import io, os, re, time, sys

CMD = sys.argv[1]
CZEKAJ = float(sys.argv[2]) if len(sys.argv) > 2 else 1.25
LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
BAZA = [0x7E,0x7E,0x00,0xFF,0x11,0x0E,0x00,0x00,0x02,0x01,0x89,0x8A,0xBE,0x47,0x00,0x80,0x00,0x00,0x00]


def ramki_od(offset):
    f = io.open(LOG, encoding="utf-8", errors="replace"); f.seek(offset)
    t = f.read(); nowy = f.tell(); f.close()
    raw = []
    for m in re.finditer(r'\[RX[^\]]*\]\s*((?:[0-9A-F]{2}\s+)+)', t):
        raw += m.group(1).split()
    b = [int(x,16) for x in raw]
    fr, i = [], 0
    while i < len(b)-6:
        if b[i]==0x7E and b[i+1]==0x7E:
            dl=b[i+5]; tot=6+dl
            if tot<=64 and i+tot<=len(b):
                r=b[i:i+tot]; x=0
                for v in r[:-1]: x^=v
                if x==r[-1]:
                    fr.append(r); i+=tot; continue
        i+=1
    return fr, nowy


def wyslij(l):
    io.open(CMD, "w", encoding="utf-8").write(l + "\n"); time.sleep(0.4)


wyslij("STOP"); wyslij("INTTX 0"); wyslij("DEHOLD 5"); wyslij("PORX 40")
trafienia = []
for poz, nazwa in [(4, "klasa"), (3, "adresat"), (2, "nadawca")]:
    print(f"\n=== PRZEMIAT [{poz}] ({nazwa}) : 256 wartosci ===", flush=True)
    for v in range(256):
        r = list(BAZA); r[poz] = v
        hx = ' '.join(f'{x:02X}' for x in r)
        off = os.path.getsize(LOG)
        wyslij(f"TXX {hx}")
        time.sleep(CZEKAJ)
        fr, off = ramki_od(off)
        inne = [f for f in fr if not (f[2]==0xFF and f[3]==0x40 and f[5]==0x17)]
        for f in inne:
            h = ' '.join(f'{x:02X}' for x in f)
            trafienia.append((nazwa, v, h))
            print(f"*** TRAFIENIE [{poz}]={v:02X} ({nazwa}): {h}", flush=True)
        if v % 64 == 63:
            print(f"  ...{nazwa}: do {v:02X}, trafien lacznie {len(trafienia)}", flush=True)

print("\n=== KONIEC ===", flush=True)
if trafienia:
    for n, v, h in trafienia:
        print(f"  {n}={v:02X} -> {h}", flush=True)
else:
    print("  ZERO reakcji na 768 kombinacji naglowka", flush=True)
wyslij("PORX 0")
