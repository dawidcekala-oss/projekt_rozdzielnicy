# -*- coding: utf-8 -*-
"""Przechwycenie rozruchu jednostki (Faza 2, eksperyment kluczowy).
Sonda hamerowo wysyla zapytanie co 500 ms, a skrypt zapisuje WSZYSTKO,
co pojawi sie na magistrali od chwili zalaczenia bezpiecznika.
Uzycie: python przechwyt_rozruchu.py <plik_komend> [sekundy_nagrywania]"""
import io, os, re, time, sys
from collections import Counter

CMD = sys.argv[1]
CZAS = int(sys.argv[2]) if len(sys.argv) > 2 else 180
LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
WYNIK = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\rozruch_jednostki.txt"


def wyslij(l):
    io.open(CMD, "w", encoding="utf-8").write(l + "\n"); time.sleep(0.4)


print("=== PRZECHWYT ROZRUCHU ===", flush=True)
print("konfiguracja sondy: zapytanie co 500 ms, precyzyjne bity", flush=True)
wyslij("INTTX 0"); wyslij("DEHOLD 5"); wyslij("PORX 0"); wyslij("POWT 1")
wyslij("SET 7E 7E 00 FF 11 0E 00 00 02 01 89 8A BE 47 00 80 00 00 00 99")
wyslij("T 500")
off = os.path.getsize(LOG)
wyslij("START")
print(f">>> TERAZ: wylacz i wlacz bezpiecznik klimatyzatora. Nagrywam {CZAS} s...", flush=True)
t0 = time.time()
while time.time() - t0 < CZAS:
    time.sleep(5)
    print(f"    ...{int(time.time()-t0)} s", flush=True)
wyslij("STOP"); wyslij("T 3000")

f = io.open(LOG, encoding="utf-8", errors="replace"); f.seek(off); tekst = f.read(); f.close()
io.open(WYNIK, "w", encoding="utf-8").write(tekst)

raw = []
for m in re.finditer(r'\[RX[^\]]*\]\s*((?:[0-9A-F]{2}\s+)+)', tekst):
    raw += m.group(1).split()
b = [int(x,16) for x in raw]
typy = Counter(); przyk = {}
i = 0
while i < len(b)-6:
    if b[i]==0x7E and b[i+1]==0x7E:
        dl=b[i+5]; tot=6+dl
        if tot<=64 and i+tot<=len(b):
            r=b[i:i+tot]; x=0
            for v in r[:-1]: x^=v
            if x==r[-1]:
                k=(r[2],r[3],r[4],dl); typy[k]+=1
                przyk.setdefault(k,' '.join(f'{y:02X}' for y in r))
                i+=tot; continue
    i+=1
print(f"\n=== WYNIK: {len(b)} bajtow, {sum(typy.values())} poprawnych ramek ===", flush=True)
for (s,d,t,l),n in typy.most_common():
    gwiazdka = "   <<< NOWY TYP!" if not (s==0xFF and d==0x40 and l==0x17) else ""
    print(f"  {s:02X}->{d:02X} klasa={t:02X} len={l:02X}  x{n}{gwiazdka}", flush=True)
    print(f"      {przyk[(s,d,t,l)]}", flush=True)
print(f"\npelny zapis: {WYNIK}", flush=True)
