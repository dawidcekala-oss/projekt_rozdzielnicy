# -*- coding: utf-8 -*-
"""Dekoder roznicowy: porownuje najnowsza poprawna ramke jednostki z ramka odniesienia.
Uzycie:
  python dekoder_roznicowy.py baza   -> zapisuje aktualna ramke jako odniesienie
  python dekoder_roznicowy.py        -> porownuje najnowsza ramke z odniesieniem
"""
import re, sys, io, os, json, time

LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
REF = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\ramka_odniesienia.json"
MAPA = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\mapa_pol.json"


def ramki_ok(tekst):
    """Wyciaga wszystkie ramki jednostki z poprawna suma XOR."""
    raw = []
    for m in re.finditer(r'\[RX\]\s*((?:[0-9A-F]{2}\s+)+)', tekst):
        raw += m.group(1).split()
    b = [int(x, 16) for x in raw]
    wynik, i = [], 0
    while i < len(b) - 6:
        if b[i] == 0x7E and b[i+1] == 0x7E:
            dl = b[i+5]; total = 6 + dl
            if total <= 64 and i + total <= len(b):
                fr = b[i:i+total]
                x = 0
                for v in fr[:-1]:
                    x ^= v
                if x == fr[-1] and fr[2] == 0xFF:
                    wynik.append(fr)
                i += total
                continue
        i += 1
    return wynik


def ostatnia_stabilna(n_ogona=6):
    """Najczestsza ramka z ostatnich n odebranych (odrzuca pojedyncze przeklamania)."""
    h = io.open(LOG, encoding="utf-8", errors="replace").read()
    i = h.rfind('=== SONDA COM-MANUAL v2')
    fr = ramki_ok(h[i:] if i >= 0 else h)
    if not fr:
        return None
    ogon = fr[-n_ogona:]
    klucze = [' '.join(f'{v:02X}' for v in f) for f in ogon]
    naj = max(set(klucze), key=klucze.count)
    return [int(x, 16) for x in naj.split()]


def main():
    fr = ostatnia_stabilna()
    if fr is None:
        print("BRAK poprawnych ramek w logu")
        return
    hexfr = ' '.join(f'{v:02X}' for v in fr)
    if len(sys.argv) > 1 and sys.argv[1] == 'baza':
        json.dump({"czas": time.strftime('%H:%M:%S'), "ramka": fr}, open(REF, 'w'))
        print("ODNIESIENIE zapisane:", hexfr)
        return
    if not os.path.exists(REF):
        print("Brak odniesienia - uruchom najpierw z argumentem 'baza'. Aktualna:", hexfr)
        return
    ref = json.load(open(REF))["ramka"]
    print("odniesienie:", ' '.join(f'{v:02X}' for v in ref))
    print("aktualna:  ", hexfr)
    if len(ref) != len(fr):
        print(f"UWAGA: rozna dlugosc ({len(ref)} vs {len(fr)})")
    zmiany = [(i, a, b) for i, (a, b) in enumerate(zip(ref, fr)) if a != b]
    zmiany = [z for z in zmiany if z[0] != len(fr) - 1]  # pomijamy sume kontrolna
    if not zmiany:
        print("BRAK ZMIAN (poza suma kontrolna)")
    for i, a, b in zmiany:
        print(f"  bajt[{i:2d}]: {a:02X} -> {b:02X}   (dec: {a} -> {b})")


if __name__ == "__main__":
    main()
