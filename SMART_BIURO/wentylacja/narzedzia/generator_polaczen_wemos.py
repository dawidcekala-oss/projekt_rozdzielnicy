# -*- coding: utf-8 -*-
"""Rysunek polaczen: plytka modulu v2 (podstawka po ESP32) <-> WeMos D1 R1.

Nazwy gniazd sa takie, jak nadrukowane na plytkach: na WeMosie jedno gniazdo
nosi po kilka nazw naraz (np. "D11/MOSI/D7") i tylko pelny nadruk jest
jednoznaczny. Wyjscie: modul_v2/polaczenia_wemos.png i .pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\SMART_BIURO\wentylacja\modul_v2\polaczenia_wemos"
plt.rcParams["font.family"] = "DejaVu Sans"

fig = plt.figure(figsize=(18, 12.5))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 180); ax.set_ylim(0, 125); ax.axis("off")

CZ = "#222222"; NIEB = "#2c4a7c"; SZARY = "#9aa0a6"
K5V = "#c0392b"; KGND = "#222222"; K33 = "#e67e22"; KBUS = "#1f5fbf"; KIR = "#0a7d3b"
UWAGA = "#e67e22"


def t(x, y, s, size=10, **kw):
    kw.setdefault("ha", "center"); kw.setdefault("va", "center")
    ax.text(x, y, s, fontsize=size, zorder=9, **kw)


def otwor(x, y, r=1.15, kolor=SZARY, lw=1.6):
    ax.add_patch(Circle((x, y), r, fc="white", ec=kolor, lw=lw, zorder=6))


# ═══════════════ TYTUL ═══════════════
t(90, 121, "Moduł v2 na WeMos D1 R1 — pięć przewodów", 16, weight="bold")
t(90, 116.5, "Przewody męsko-męskie: jeden koniec w otwór podstawki po procesorze ESP32, drugi w gniazdo listwy WeMosa.", 10.5, color="#444")

# ═══════════════ LEWO: PODSTAWKA PO ESP32 ═══════════════
ax.add_patch(FancyBboxPatch((10, 34), 66, 68, boxstyle="round,pad=0.6,rounding_size=2",
                            fc="#f2f4f7", ec="#9aa0a6", lw=2, zorder=1))
t(43, 105.5, "Płytka modułu: podstawka po ESP32", 11.5, weight="bold", color=NIEB)

GORA = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
DOL  = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19", "D21", "RX0", "TXO", "D22", "D23"]
UZYTE_G = {"VIN": K5V, "GND": KGND}
UZYTE_D = {"3V3": K33, "TX2": KBUS, "D23": KIR}
POZ = {}

y0, dy = 96, 4.2
for i, n in enumerate(GORA):
    y = y0 - i * dy
    kol = UZYTE_G.get(n) if i < 2 else None
    otwor(26, y, 1.35 if kol else 1.0, kol or SZARY, lw=2.4 if kol else 1.3)
    t(29, y, n, 8.5 if kol else 6.5, ha="left", color=kol or SZARY, weight="bold" if kol else "normal")
    if kol: POZ[n] = (26, y)
for i, n in enumerate(DOL):
    y = y0 - i * dy
    kol = UZYTE_D.get(n)
    otwor(60, y, 1.35 if kol else 1.0, kol or SZARY, lw=2.4 if kol else 1.3)
    t(57, y, n, 8.5 if kol else 6.5, ha="right", color=kol or SZARY, weight="bold" if kol else "normal")
    if kol: POZ[n] = (60, y)

t(26, 100.5, "rząd górny", 8, color=SZARY)
t(60, 100.5, "rząd dolny", 8, color=SZARY)
t(43, 36.5, "pozostałe otwory zostają puste", 8.5, color=SZARY)

# ═══════════════ PRAWO: WEMOS ═══════════════
ax.add_patch(FancyBboxPatch((100, 52), 72, 44, boxstyle="round,pad=0.6,rounding_size=2",
                            fc="#dfe9f7", ec="#5b7db1", lw=2, zorder=1))
ax.text(136, 41.5, "WeMos D1 R1 (widok z góry, gniazdo USB po lewej)", fontsize=11.5, weight="bold",
        color=NIEB, ha="center", va="center", zorder=9,
        bbox=dict(fc="white", ec="none", alpha=0.95, pad=2.0))
ax.add_patch(Rectangle((96.5, 68), 5, 8, fc="#c8c8c8", ec=CZ, lw=1.4, zorder=5))
t(95.5, 72, "USB", 7, color="#555", ha="right")
ax.add_patch(Rectangle((96.5, 56), 5, 7, fc="#333", ec=CZ, lw=1.4, zorder=5))
t(95.5, 59.5, "gniazdo\nzasilania", 7, color="#555", ha="right")
ax.add_patch(Rectangle((124, 72), 22, 16, fc="#d8d8d8", ec="#888", lw=1.4, zorder=4))
t(135, 80, "ESP8266MOD", 8.5, color="#444")
ax.add_patch(Circle((127, 74.5), 0.8, fc="#4aa3ff", ec="#4aa3ff", zorder=6))
t(129.5, 74.5, "dioda", 6.5, ha="left", color="#4aa3ff")

gora_prawa = [("D11/MOSI/D7", KBUS), ("D12/MISO/D6", KIR), ("D13/SCK/D5", None), ("D14/SDA/D4", None),
              ("D15/SCL/D3", None), ("D2", None), ("TX->D1", None), ("RX<-D0", None)]
x = 133.5
for n, kol in gora_prawa:
    otwor(x, 96, 1.35 if kol else 1.0, kol or SZARY, lw=2.4 if kol else 1.3)
    if kol:
        POZ[n] = (x, 96)
        ax.text(x + 1.2, 98.4, n, fontsize=8.5, color=kol, weight="bold", rotation=45,
                ha="left", va="bottom", rotation_mode="anchor", zorder=9,
                bbox=dict(fc="white", ec="none", alpha=0.9, pad=0.4))
    x += 4.6
x = 104
for n in ["D8", "TX1/D9", "D10/SS", "D11/MOSI", "D12/MISO", "D13/SCK", "GND", "D14/SDA", "D15/SCL"]:
    otwor(x, 96, 1.0, SZARY, lw=1.3)
    x += 2.9

dol_lewa = [("IOREF", None), ("RESET", None), ("3.3V", K33), ("5V", K5V), ("GND", KGND), ("GND", None), ("VIN", None)]
x = 104.5
for n, kol in dol_lewa:
    uz = kol is not None and ("W" + n) not in POZ
    otwor(x, 52, 1.35 if uz else 1.0, kol or SZARY, lw=2.4 if uz else 1.3)
    if uz:
        POZ["W" + n] = (x, 52)
        t(x - 1.2, 49.4, n, 9, color=kol, weight="bold", rotation=30, ha="right")
    else:
        t(x - 1.0, 49.8, n, 6, color=SZARY, rotation=30, ha="right")
    x += 4.6
x = 148
for n in ["A0", "A1", "A2", "A3", "A4", "A5"]:
    otwor(x, 52, 1.0, SZARY, lw=1.3)
    t(x - 1.0, 49.8, n, 6, color=SZARY, rotation=30, ha="right")
    x += 4.2

# ═══════════════ PRZEWODY ═══════════════
def przewod(pts, kolor, opis, opis_xy):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=kolor, lw=3.0, solid_capstyle="round", solid_joinstyle="round", zorder=3)
    t(opis_xy[0], opis_xy[1], opis, 9.5, color=kolor, weight="bold")

# zasilanie: w dół, pod płytkami
przewod([POZ["3V3"], (82, POZ["3V3"][1]), (82, 30), (POZ["W3.3V"][0], 30), POZ["W3.3V"]],
        K33, "3,3 V dla modułu RS485", (60, 31.7))
przewod([POZ["VIN"], (16, POZ["VIN"][1]), (16, 25), (POZ["W5V"][0], 25), POZ["W5V"]],
        K5V, "5 V — zasilanie procesora", (60, 26.7))
przewod([POZ["GND"], (20, POZ["GND"][1]), (20, 20), (POZ["WGND"][0], 20), POZ["WGND"]],
        KGND, "masa wspólna", (60, 21.7))
# sygnały: w górę, nad płytkami
przewod([POZ["TX2"], (84, POZ["TX2"][1]), (84, 107), (POZ["D11/MOSI/D7"][0], 107), POZ["D11/MOSI/D7"]],
        KBUS, "magistrala — z pola TXD modułu RS485", (108, 108.7))
przewod([POZ["D23"], (90, POZ["D23"][1]), (90, 112), (POZ["D12/MISO/D6"][0], 112), POZ["D12/MISO/D6"]],
        KIR, "podczerwień — przez 470 Ω na tranzystor", (112, 113.7))

# ═══════════════ UWAGI ═══════════════
ax.add_patch(FancyBboxPatch((6, 2), 168, 13.5, boxstyle="round,pad=0.5", fc="#fff8f0", ec=UWAGA, lw=2, zorder=1))
t(90, 13.8, "Czego nie podłączamy i o czym pamiętać", 11.5, weight="bold", color=UWAGA)
uwagi = [
    "Otwór RX2 (wejście nadajnika modułu RS485) i otwór D4 (kierunek) zostają puste: moduł nigdy nie nadaje na magistralę, a pole EN jest na module zwarte drutem do masy.",
    "Zasilanie: przetwornica 5,00 V → gniazdo 5V. Wariant awaryjny: 12 V z żółtej żyły prosto na gniazdo VIN WeMosa (tak pracowała dawna sonda) — ale nigdy z obu źródeł naraz.",
    "Nigdy USB i zasilanie z płytki jednocześnie. Wtyk do gniazda COM-MANUAL wpinać przy wyłączonej jednostce.",
    "WeMos jest wielkości Arduino Uno i ma odsłonięte luty na spodzie: podkładka z tworzywa, dystanse, klej na spód przetwornicy i na lut żółtej żyły.",
]
for i, s in enumerate(uwagi):
    t(9, 10.8 - i * 2.6, "•  " + s, 8.8, ha="left")

fig.savefig(OUT + ".png", dpi=160, facecolor="white")
fig.savefig(OUT + ".pdf", facecolor="white")
print("OK:", OUT + ".png / .pdf")
