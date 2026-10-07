# -*- coding: utf-8 -*-
"""Pelny przemiat bajtu rozkazu w zapytaniu 00->FF (Faza 2).
Uzycie: python skan_pelny.py <plik_komend> <pozycja_bajtu> [czekaj_s]
Pozycja liczona w calej ramce (nasze zapytanie: [8] to bajt '02')."""
import io, os, re, time, sys

CMD = sys.argv[1]
POZ = int(sys.argv[2]) if len(sys.argv) > 2 else 8
CZEKAJ = float(sys.argv[3]) if len(sys.argv) > 3 else 1.3
LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"

BAZA = [0x7E,0x7E,0x00,0xFF,0x11,0x0E,0x00,0x00,0x02,0x01,0x89,0x8A,0xBE,0x47,0x00,0x80,0x00,0x00,0x00]


def ramki_od(offset):
    f = io.open(LOG, encoding="utf-8", errors="replace"); f.seek(offset)
    t = f.read(); nowy = f.tell(); f.close()
    raw = []
    for m in re.finditer(r'\[RX\]\s*((?:[0-9A-F]{2}\s+)+)', t):
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


def wyslij(linia):
    io.open(CMD, "w", encoding="utf-8").write(linia + "\n")


print(f"=== PRZEMIAT bajtu [{POZ}] : 256 wartosci, {CZEKAJ}s kazda ===", flush=True)
wyslij("STOP"); time.sleep(2)
trafienia = []
for v in range(256):
    ramka = list(BAZA); ramka[POZ] = v
    hexy = ' '.join(f'{x:02X}' for x in ramka)
    off = os.path.getsize(LOG)
    wyslij(f"TXX {hexy}")
    time.sleep(CZEKAJ)
    fr, off = ramki_od(off)
    inne = [f for f in fr if not (f[2]==0xFF and f[3]==0x40 and f[5]==0x17)]
    if inne:
        for f in inne:
            hx = ' '.join(f'{x:02X}' for x in f)
            trafienia.append((v, hx))
            print(f"*** TRAFIENIE przy [{POZ}]={v:02X}: {hx}", flush=True)
    if v % 32 == 31:
        print(f"  ... przebadano do {v:02X}, trafien: {len(trafienia)}", flush=True)
print("\n=== KONIEC PRZEMIATU ===", flush=True)
if trafienia:
    for v, hx in trafienia:
        print(f"  [{POZ}]={v:02X} -> {hx}", flush=True)
else:
    print("  ZERO odpowiedzi na wszystkie 256 wartosci", flush=True)
wyslij("STOP")
