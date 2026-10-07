# -*- coding: utf-8 -*-
"""Schemat kompletny modulu v2 (ESP32 + MAX3485 + IR) — jeden duzy rysunek.

Konwencje rysunku:
  * gora        — wytwarzanie zasilania: zrodlo -> ogranicznik udaru -> przetwornica
  * srodek      — trzy szyny poziome: +5 V, +3,3 V, GND
  * dol         — odbiorniki; KAZDY pobiera zasilanie pionowym odczepem z gornej krawedzi
  * opisy pinow zawsze WEWNATRZ bloku, zeby nie kolidowaly z przewodami
  * sygnaly biegna poziomo na tych samych wysokosciach po obu stronach
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\modul_v2\schemat_modul_v2.png"

W, H = 24.6, 15.2
C_12V = "#D62728"
C_5V  = "#E8811A"
C_33  = "#7B3FBF"
C_GND = "#111111"
C_SIG = "#1F77B4"
C_BUS = "#2CA02C"
C_BOX = "#F6F6F4"
C_EDG = "#333333"
C_MUT = "#8A8A8A"
C_WRN = "#B00020"

fig, ax = plt.subplots(figsize=(W, H), dpi=165)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
fig.patch.set_facecolor("white")


def box(x0, y0, x1, y1, tytul, sub=None, styl="-", ec=C_EDG, lw=1.8):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle="round,pad=0.03,rounding_size=0.14",
                                fc=C_BOX, ec=ec, lw=lw, zorder=2, linestyle=styl))
    ax.text((x0 + x1) / 2, y1 - 0.32, tytul, ha="center", va="center",
            fontsize=13, fontweight="bold", color="#1a1a1a", zorder=6)
    if sub:
        ax.text((x0 + x1) / 2, y1 - 0.66, sub, ha="center", va="center",
                fontsize=9.0, color="#555", zorder=6)


def pin(x, y, etyk, gdzie="in_right", kolor="#222", fs=9.6):
    """gdzie: in_right / in_left / in_down  — opis zawsze wewnatrz bloku."""
    ax.add_patch(Circle((x, y), 0.078, fc="white", ec=kolor, lw=1.8, zorder=7))
    if gdzie == "in_right":
        ax.text(x + 0.19, y, etyk, ha="left", va="center", fontsize=fs,
                fontweight="bold", color=kolor, zorder=8)
    elif gdzie == "in_left":
        ax.text(x - 0.19, y, etyk, ha="right", va="center", fontsize=fs,
                fontweight="bold", color=kolor, zorder=8)
    else:  # in_down -> etykieta NAD pinem, obok pionowego przewodu
        ax.text(x + 0.22, y + 0.22, etyk, ha="left", va="bottom", fontsize=fs,
                fontweight="bold", color=kolor, zorder=8)


def wire(pkt, kolor, lw=2.5, styl="-"):
    ax.plot([p[0] for p in pkt], [p[1] for p in pkt], color=kolor, lw=lw,
            solid_capstyle="round", zorder=3, linestyle=styl)


def wezel(x, y, kolor):
    ax.add_patch(Circle((x, y), 0.105, fc=kolor, ec=kolor, zorder=8))


def rez_h(x, y, opis, dlug=1.0, kolor="#222"):
    ax.add_patch(Rectangle((x, y - 0.17), dlug, 0.34, fc="white", ec=kolor, lw=1.8, zorder=6))
    ax.text(x + dlug / 2, y + 0.38, opis, ha="center", va="bottom", fontsize=10,
            fontweight="bold", color=kolor, zorder=8)


def rez_v(x, y, opis, dlug=1.0, kolor="#222"):
    ax.add_patch(Rectangle((x - 0.17, y), 0.34, dlug, fc="white", ec=kolor, lw=1.8, zorder=6))
    ax.text(x + 0.30, y + dlug / 2, opis, ha="left", va="center", fontsize=10,
            fontweight="bold", color=kolor, zorder=8)


def kond_v(x, y, opis, kolor="#222"):
    ax.plot([x - 0.32, x + 0.32], [y, y], color=kolor, lw=2.8, zorder=6)
    ax.plot([x - 0.32, x + 0.32], [y - 0.24, y - 0.24], color=kolor, lw=2.8, zorder=6)
    ax.text(x + 0.46, y - 0.12, opis, ha="left", va="center", fontsize=10,
            fontweight="bold", color=kolor, zorder=8)
    ax.text(x - 0.46, y, "+", ha="right", va="center", fontsize=12,
            fontweight="bold", color=kolor, zorder=8)


def dioda_ir(x, y, kolor="#222"):
    ax.add_patch(Polygon([[x - 0.28, y], [x + 0.28, y], [x, y - 0.46]],
                         closed=True, fc="white", ec=kolor, lw=1.8, zorder=6))
    ax.plot([x - 0.28, x + 0.28], [y - 0.46, y - 0.46], color=kolor, lw=2.6, zorder=6)
    for i in (0, 1):
        ax.annotate("", xy=(x - 0.66 - i * 0.17, y - 0.04 + i * 0.17),
                    xytext=(x - 0.38 - i * 0.17, y - 0.28 + i * 0.17),
                    arrowprops=dict(arrowstyle="-|>", color=kolor, lw=1.4), zorder=7)


def tranzystor(x, y, kolor="#222"):
    """NPN: baza z lewej, kolektor u gory (x+0.28), emiter na dole (x+0.28)."""
    ax.add_patch(Circle((x, y), 0.56, fc="white", ec=kolor, lw=1.8, zorder=6))
    ax.plot([x - 0.20, x - 0.20], [y - 0.32, y + 0.32], color=kolor, lw=2.8, zorder=7)
    ax.plot([x - 0.56, x - 0.20], [y, y], color=kolor, lw=2.3, zorder=7)
    ax.plot([x - 0.20, x + 0.28], [y + 0.19, y + 0.50], color=kolor, lw=2.3, zorder=7)
    ax.plot([x - 0.20, x + 0.28], [y - 0.19, y - 0.50], color=kolor, lw=2.3, zorder=7)
    ax.annotate("", xy=(x + 0.22, y - 0.44), xytext=(x + 0.02, y - 0.31),
                arrowprops=dict(arrowstyle="-|>", color=kolor, lw=1.3), zorder=8)


# =========================================================================
ax.text(0.5, H - 0.45, "MODUŁ v2 — schemat kompletny", fontsize=22,
        fontweight="bold", color="#111", va="center")
ax.text(0.5, H - 0.98, "Odczyt i sterowanie klimatyzatora Gree GKH · jeden moduł na jednostkę · AmperePoint",
        fontsize=11.5, color="#555", va="center")

# ---------------- SZYNY ----------------
SZ_5V, SZ_33, SZ_GND = 7.75, 7.10, 6.45
for y, kol, opis in ((SZ_5V, C_5V, "+5 V"), (SZ_33, C_33, "+3,3 V"), (SZ_GND, C_GND, "GND")):
    wire([(0.95, y), (23.9, y)], kol, lw=3.4)
    ax.text(0.80, y, opis, ha="right", va="center", fontsize=11.5, fontweight="bold", color=kol)

# ---------------- GORA: zrodla i przetwornica ----------------
box(0.8, 10.6, 4.2, 13.7, "GNIAZDO COM-MANUAL", "w skrzynce klimatyzatora")
pin(4.2, 13.15, "+12 V  biały", "in_left", C_12V, 9.4)
pin(4.2, 12.45, "GND  żółty", "in_left", C_GND, 9.4)
pin(4.2, 11.65, "A  czarny", "in_left", C_BUS, 9.4)
pin(4.2, 11.00, "B  czerwony", "in_left", C_BUS, 9.4)
ax.text(2.5, 10.85, "wtyk JST-XH 2,54 mm / 4 pin", ha="center", fontsize=8.6, color="#666")

box(0.8, 8.75, 4.2, 10.05, "ZASILACZ 12 V", "wariant zapasowy — nota 3", styl="--", ec=C_MUT)
pin(4.2, 9.55, "+12 V", "in_left", C_12V, 9.0)
pin(4.2, 9.05, "GND", "in_left", C_GND, 9.0)

wire([(4.2, 13.15), (5.25, 13.15)], C_12V)
rez_h(5.25, 13.15, "10 Ω", 1.05, C_12V)
wire([(6.30, 13.15), (7.30, 13.15)], C_12V)
ax.text(5.78, 12.72, "ogranicznik udaru", ha="center", fontsize=8.6, color="#666")
wire([(4.2, 12.45), (7.30, 12.45)], C_GND)

wire([(4.2, 9.55), (4.72, 9.55), (4.72, 13.15)], C_12V, lw=1.8, styl=(0, (5, 4)))
wire([(4.2, 9.05), (5.02, 9.05), (5.02, 12.45)], C_GND, lw=1.8, styl=(0, (5, 4)))

box(7.30, 11.55, 11.30, 14.0, "PRZETWORNICA MP1584EN", "obniżająca, regulowana")
pin(7.30, 13.15, "IN+", "in_right", C_12V, 9.4)
pin(7.30, 12.45, "IN−", "in_right", C_GND, 9.4)
pin(11.30, 13.15, "OUT+", "in_left", C_5V, 9.4)
pin(11.30, 12.45, "OUT−", "in_left", C_GND, 9.4)
ax.text(9.30, 11.85, "USTAWIĆ 5,00 V PRZED PODŁĄCZENIEM", ha="center",
        fontsize=10.4, fontweight="bold", color=C_WRN)

wire([(11.30, 13.15), (12.55, 13.15)], C_5V)
wezel(12.55, 13.15, C_5V)
kond_v(12.55, 12.95, "470 µF / 25 V", C_5V)
wire([(12.55, 13.15), (12.55, 12.95)], C_5V)
wire([(12.55, 12.71), (12.55, 12.45)], C_GND)
wire([(11.30, 12.45), (13.15, 12.45)], C_GND)
wezel(12.55, 12.45, C_GND)

wire([(12.55, 13.15), (14.10, 13.15), (14.10, SZ_5V)], C_5V)
wezel(14.10, SZ_5V, C_5V)
wire([(13.15, 12.45), (13.15, SZ_GND)], C_GND)
wezel(13.15, SZ_GND, C_GND)

# ---------------- DOL: ESP32 ----------------
box(3.0, 0.85, 8.0, 5.75, "ESP32 DevKit", "ESP-WROOM-32, 30 pin")
pin(3.85, 5.75, "5V", "in_down", C_5V, 9.2)
pin(4.95, 5.75, "GND", "in_down", C_GND, 9.2)
pin(6.05, 5.75, "3V3", "in_down", C_33, 9.2)
wire([(3.85, 5.75), (3.85, SZ_5V)], C_5V);  wezel(3.85, SZ_5V, C_5V)
wire([(4.95, 5.75), (4.95, SZ_GND)], C_GND); wezel(4.95, SZ_GND, C_GND)
wire([(6.05, 5.75), (6.05, SZ_33)], C_33);  wezel(6.05, SZ_33, C_33)
ax.text(8.30, 6.22, "stabilizator 3,3 V ESP32 zasila szynę", ha="left",
        fontsize=8.6, color=C_33)

pin(8.0, 4.85, "GPIO16", "in_left", C_SIG, 9.2)
pin(8.0, 4.25, "GPIO17", "in_left", C_SIG, 9.2)
pin(8.0, 3.65, "GPIO4", "in_left", C_SIG, 9.2)
pin(8.0, 2.55, "GPIO23", "in_left", C_SIG, 9.2)
pin(8.0, 1.75, "GPIO19", "in_left", C_SIG, 9.2)
ax.text(5.5, 1.15, "UART2 sprzętowy · podczerwień układem RMT", ha="center",
        fontsize=8.8, color="#666")

# ---------------- MAX3485 ----------------
box(10.7, 3.05, 14.7, 5.75, "MODUŁ MAX3485", "konwerter RS-485, 3,3 V")
pin(10.7, 4.85, "RO", "in_right", C_SIG, 9.2)
pin(10.7, 4.25, "DI", "in_right", C_SIG, 9.2)
pin(10.7, 3.65, "DE+RE", "in_right", C_SIG, 9.2)
pin(11.60, 5.75, "VCC", "in_down", C_33, 9.2)
pin(12.90, 5.75, "GND", "in_down", C_GND, 9.2)
wire([(11.60, 5.75), (11.60, SZ_33)], C_33);  wezel(11.60, SZ_33, C_33)
wire([(12.90, 5.75), (12.90, SZ_GND)], C_GND); wezel(12.90, SZ_GND, C_GND)
pin(14.7, 4.60, "A", "in_left", C_BUS, 9.2)
pin(14.7, 3.80, "B", "in_left", C_BUS, 9.2)

for y, opis in ((4.85, "odbiór"), (4.25, "nadawanie"), (3.65, "kierunek")):
    wire([(8.0, y), (10.7, y)], C_SIG)
    ax.text(9.35, y + 0.20, opis, ha="center", fontsize=8.6, color=C_SIG)

wire([(14.7, 4.60), (15.35, 4.60), (15.35, 11.65), (4.2, 11.65)], C_BUS)
wire([(14.7, 3.80), (15.85, 3.80), (15.85, 11.00), (4.2, 11.00)], C_BUS)
ax.text(16.05, 10.55, "magistrala RS-485 do gniazda", ha="left", fontsize=9.2,
        color=C_BUS, fontweight="bold")

# ---------------- nadajnik IR ----------------
box(17.0, 0.85, 20.9, 5.75, "NADAJNIK PODCZERWIENI", "dioda przez wzmacniacz prądowy")
pin(19.05, 5.75, "+5V", "in_down", C_5V, 9.2)
pin(20.45, 5.75, "GND", "in_down", C_GND, 9.2)
wire([(19.05, 5.75), (19.05, SZ_5V)], C_5V);  wezel(19.05, SZ_5V, C_5V)
wire([(20.45, 5.75), (20.45, SZ_GND)], C_GND); wezel(20.45, SZ_GND, C_GND)
pin(17.0, 2.55, "we.", "in_right", C_SIG, 9.2)
wire([(8.0, 2.55), (17.0, 2.55)], C_SIG)

wire([(19.05, 5.75), (19.05, 4.85)], C_5V)
rez_v(19.05, 3.95, "33 Ω", 0.90, C_5V)
wire([(19.05, 3.95), (19.05, 3.62)], C_5V)
dioda_ir(19.05, 3.62, C_5V)
ax.text(19.42, 3.42, "TSAL6100", ha="left", va="center", fontsize=9.6,
        fontweight="bold", color=C_5V)
wire([(19.05, 3.16), (19.05, 2.75)], C_5V)
tranzystor(18.77, 2.25, "#222")
rez_h(17.60, 2.25, "470 Ω", 0.85, C_SIG)
wire([(17.0, 2.55), (17.42, 2.55), (17.42, 2.25), (17.60, 2.25)], C_SIG)
wire([(18.45, 2.25), (18.21, 2.25)], C_SIG)
ax.text(19.52, 1.98, "BC337", ha="left", va="center", fontsize=9.6,
        fontweight="bold", color="#222")
wire([(19.05, 1.75), (19.05, 1.30), (20.45, 1.30), (20.45, 5.75)], C_GND)
ax.text(18.30, 1.05, "≈100 mA w impulsie", ha="center", fontsize=8.6, color="#666")

# ---------------- odbiornik IR ----------------
box(21.6, 0.85, 24.1, 5.75, "ODBIORNIK IR", "VS1838B, 38 kHz")
pin(22.35, 5.75, "3V3", "in_down", C_33, 9.2)
pin(23.55, 5.75, "GND", "in_down", C_GND, 9.2)
wire([(22.35, 5.75), (22.35, SZ_33)], C_33);  wezel(22.35, SZ_33, C_33)
wire([(23.55, 5.75), (23.55, SZ_GND)], C_GND); wezel(23.55, SZ_GND, C_GND)
pin(21.6, 1.75, "wyjście", "in_right", C_SIG, 9.2)
wire([(8.0, 1.75), (16.35, 1.75), (16.35, 0.42), (21.15, 0.42), (21.15, 1.75), (21.6, 1.75)], C_SIG)
wire([(22.35, 5.75), (22.35, 3.90)], C_33)
rez_v(22.35, 3.00, "10 kΩ", 0.90, C_33)
wire([(22.35, 3.00), (22.35, 2.30), (22.90, 2.30)], C_33)
ax.text(22.85, 2.70, "podciągnięcie", ha="left", fontsize=8.4, color=C_33)
wire([(21.6, 1.75), (22.90, 1.75), (22.90, 2.30)], C_SIG)
wezel(22.90, 2.30, C_SIG)

# ---------------- noty ----------------
noty = [
    ("1.", "Przetwornica MP1584EN przychodzi ustawiona na przypadkowe napięcie. Ustawić 5,00 V", C_WRN),
    ("",   "miernikiem PRZED podłączeniem czegokolwiek — 12 V na pinie 5V niszczy ESP32.", C_WRN),
    ("2.", "Masa jest wspólna dla zasilania i magistrali: żyła żółta gniazda idzie do GND modułu.", "#333"),
    ("3.", "Zasilacz 12 V to wariant zapasowy — wchodzi do gry, jeśli port nie udźwignie ok. 60 mA.", "#333"),
    ("4.", "Żyła biała (+12 V) zasila moduł w wariancie docelowym; w zapasowym zostaje wolna.", "#333"),
    ("5.", "Jeśli moduł MAX3485 ma wlutowany terminator 120 Ω — zostawić go niepodłączony.", "#333"),
    ("6.", "Krzyżujące się przewody bez wypełnionej kropki NIE są ze sobą połączone.", "#333"),
]
for i, (nr, tekst, kol) in enumerate(noty):
    yy = 14.55 - i * 0.33
    ax.text(16.4, yy, nr, fontsize=9.0, fontweight="bold", color=kol, va="center")
    ax.text(16.85, yy, tekst, fontsize=9.0, color=kol, va="center")

# ---------------- legenda ----------------
lx, ly = 0.55, 4.85
ax.text(lx, ly + 0.55, "LEGENDA", fontsize=9.8, fontweight="bold", color=C_MUT)
for i, (kol, opis) in enumerate([(C_12V, "+12 V"), (C_5V, "+5 V"), (C_33, "+3,3 V"),
                                 (C_GND, "GND"), (C_SIG, "sygnał cyfrowy"), (C_BUS, "magistrala A/B")]):
    yy = ly - i * 0.40
    ax.plot([lx, lx + 0.62], [yy, yy], color=kol, lw=3.2)
    ax.text(lx + 0.78, yy, opis, fontsize=9.0, va="center", color="#444")

ax.text(W - 0.4, 0.16, "AmperePoint · wentylacja · modul_v2 · 2026-09-01",
        ha="right", fontsize=8.4, color="#999")

fig.savefig(OUT, facecolor="white", bbox_inches="tight", pad_inches=0.25)
print("zapisano:", OUT)
