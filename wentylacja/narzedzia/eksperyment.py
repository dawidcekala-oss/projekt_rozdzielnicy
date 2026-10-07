# -*- coding: utf-8 -*-
"""Szybki wykonawca eksperymentow Fazy 2.
Uzycie: python eksperyment.py <plik_komend> <plik_z_lista_prob> [czekaj_s]

Plik z lista prob: kazda linia to komenda dla sondy (TX/TXX/SET/PORX/POWT/INTTX/DEHOLD...).
Linie zaczynajace sie od '#' to komentarz/etykieta nastepnej proby.
Po kazdej komendzie TX/TXX skrypt sprawdza, czy pojawila sie ramka INNA
niz standardowe rozgloszenie FF->40 len=17.
"""
import io, os, re, time, sys

CMD = sys.argv[1]
LISTA = sys.argv[2]
CZEKAJ = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"


def ramki_od(offset):
    f = io.open(LOG, encoding="utf-8", errors="replace"); f.seek(offset)
    t = f.read(); nowy = f.tell(); f.close()
    raw = []
    for m in re.finditer(r'\[RX[^\]]*\]\s*((?:[0-9A-F]{2}\s+)+)', t):
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
    return fr, nowy, t


def wyslij(linia):
    io.open(CMD, "w", encoding="utf-8").write(linia + "\n")
    time.sleep(0.45)


linie = [l.rstrip("\n") for l in io.open(LISTA, encoding="utf-8")]
etykieta = ""
trafienia = []
print(f"=== EKSPERYMENT: {len(linie)} linii, czekaj={CZEKAJ}s ===", flush=True)
for l in linie:
    s = l.strip()
    if not s:
        continue
    if s.startswith("#"):
        etykieta = s.lstrip("# ").strip()
        continue
    duza = s.upper()
    if not (duza.startswith("TX ") or duza.startswith("TXX ")):
        # komenda konfiguracyjna - wykonaj i idz dalej
        wyslij(s)
        print(f"  [konfig] {s}", flush=True)
        continue
    off = os.path.getsize(LOG)
    wyslij(s)
    time.sleep(CZEKAJ)
    fr, off, tekst = ramki_od(off)
    inne = [f for f in fr if not (f[2] == 0xFF and f[3] == 0x40 and f[5] == 0x17)]
    opis = etykieta or s[:48]
    if inne:
        print(f"*** [{opis}] {len(inne)} NIETYPOWYCH:", flush=True)
        for f in inne[:4]:
            hx = ' '.join(f'{v:02X}' for v in f)
            print(f"      >>> {hx}", flush=True)
            trafienia.append((opis, hx))
    else:
        # sprawdz tez, czy w ogole cos sie zmienilo w rozgloszeniu
        print(f"    [{opis}] cisza ({len(fr)} rozgloszen)", flush=True)

print("\n=== PODSUMOWANIE ===", flush=True)
if trafienia:
    for opis, hx in trafienia:
        print(f"  TRAFIENIE [{opis}]: {hx}", flush=True)
else:
    print("  brak reakcji jednostki na wszystkie proby", flush=True)
