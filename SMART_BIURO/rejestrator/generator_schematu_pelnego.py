# -*- coding: utf-8 -*-
"""Jeden pelny schemat elektryczny rejestratora zlacza Q11 (do dokumentu v2).
Wszystkie tory na jednym arkuszu: zlacze 2x10, odczepy P/D, CT, detektor szczytu,
1.65, CP z komparatorem, 2x CD4051BE, magistrala adresowa, UNO, UART DWIN, laptop."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\diagnostyka"

C_SIG = "#B45309"   # tor analogowy
C_DIG = "#15803D"   # tor cyfrowy
C_GND = "#111111"
C_5V  = "#B00020"
C_BOX = "#F4F4F2"
C_EDGE = "#333333"
C_INFO = "#0369A1"
C_MUT = "#888888"
C_WARN = "#B00020"

W, H = 27.0, 47.0
fig, ax = plt.subplots(figsize=(W, H), dpi=110)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def box(x0, y0, x1, y1, title, sub=None, fc=C_BOX, tfs=10, tdy=0.32):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0,
                 boxstyle="round,pad=0.03,rounding_size=0.1", fc=fc, ec=C_EDGE, lw=1.5, zorder=1))
    ax.text((x0+x1)/2, y1-tdy, title, ha="center", va="center", fontsize=tfs, fontweight="bold", color="#222", zorder=2)
    if sub:
        ax.text((x0+x1)/2, y1-tdy-0.3, sub, ha="center", va="center", fontsize=6.8, color="#555", zorder=2)


def pin(x, y, label, side="right", color="#222", fs=7.5):
    ax.add_patch(Circle((x, y), 0.055, fc="white", ec=color, lw=1.4, zorder=6))
    dx = 0.13 if side == "right" else -0.13
    ha = "left" if side == "right" else "right"
    ax.text(x+dx, y, label, ha=ha, va="center", fontsize=fs, fontweight="bold", color=color, zorder=7,
            bbox=dict(fc="white", ec="none", pad=0.3))


def wire(pts, color=C_SIG, lw=1.9):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw, solid_capstyle="round", zorder=3)


def dot(x, y, color=C_SIG):
    ax.add_patch(Circle((x, y), 0.06, fc=color, ec=color, zorder=6))


def res_h(xc, yc, label, fs=6.8, lab_dy=0.26):
    ax.add_patch(Rectangle((xc-0.42, yc-0.12), 0.84, 0.24, fc="white", ec="#222", lw=1.4, zorder=5))
    ax.text(xc, yc+lab_dy, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def res_v(xc, yc, label, h=0.6, fs=6.6, side="right"):
    ax.add_patch(Rectangle((xc-0.12, yc-h/2), 0.24, h, fc="white", ec="#222", lw=1.4, zorder=5))
    dx = 0.2 if side == "right" else -0.2
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, yc, label, ha=ha, va="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def cap_v(xc, y_top, label, side="right", fs=6.6, do_gnd=True):
    """Kondensator z przewodem od y_top w dol + masa. Zwraca nic."""
    wire([(xc, y_top), (xc, y_top-0.28)], C_GND, 1.4)
    ax.plot([xc-0.16, xc+0.16], [y_top-0.28, y_top-0.28], color="#222", lw=2.4, zorder=5)
    ax.plot([xc-0.16, xc+0.16], [y_top-0.40, y_top-0.40], color="#222", lw=2.4, zorder=5)
    wire([(xc, y_top-0.40), (xc, y_top-0.55)], C_GND, 1.4)
    if do_gnd:
        gnd(xc, y_top-0.55)
    dx = 0.24 if side == "right" else -0.24
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, y_top-0.34, label, ha=ha, va="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def dioda_v(xc, yc, kierunek="gora"):
    if kierunek == "gora":
        ax.add_patch(Polygon([(xc-0.12, yc-0.11), (xc+0.12, yc-0.11), (xc, yc+0.09)], fc="white", ec="#222", lw=1.3, zorder=5))
        ax.plot([xc-0.12, xc+0.12], [yc+0.11, yc+0.11], color="#222", lw=1.8, zorder=5)
    else:
        ax.add_patch(Polygon([(xc-0.12, yc+0.11), (xc+0.12, yc+0.11), (xc, yc-0.09)], fc="white", ec="#222", lw=1.3, zorder=5))
        ax.plot([xc-0.12, xc+0.12], [yc-0.11, yc-0.11], color="#222", lw=1.8, zorder=5)


def dioda_h(xc, yc, label="", fs=6.6):
    ax.add_patch(Polygon([(xc-0.11, yc-0.13), (xc-0.11, yc+0.13), (xc+0.09, yc)], fc="white", ec="#222", lw=1.3, zorder=5))
    ax.plot([xc+0.11, xc+0.11], [yc-0.13, yc+0.13], color="#222", lw=1.8, zorder=5)
    if label:
        ax.text(xc, yc+0.26, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def gnd(x, y):
    wire([(x, y), (x, y-0.08)], C_GND, 1.6)
    for i, w in enumerate([0.15, 0.10, 0.05]):
        ax.plot([x-w, x+w], [y-0.10-i*0.055, y-0.10-i*0.055], color=C_GND, lw=1.8, zorder=4)


def klamra(x, y):
    """Kompaktowa klamra 2x1N4148 przy wezle (x,y): gorna dioda do +5V, dolna z masy."""
    dot(x, y)
    wire([(x, y), (x, y+0.18)], C_5V, 1.3)
    dioda_v(x, y+0.30, "gora")
    wire([(x, y+0.42), (x, y+0.56)], C_5V, 1.3)
    ax.text(x, y+0.66, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold", zorder=6)
    wire([(x, y), (x, y-0.18)], C_GND, 1.3)
    dioda_v(x, y-0.30, "gora")
    wire([(x, y-0.42), (x, y-0.50)], C_GND, 1.3)
    gnd(x, y-0.50)


# ================= TYTUL, LEGENDA =================
ax.text(W/2, 46.35, "Rejestrator złącza Q11 — PEŁNY SCHEMAT ELEKTRYCZNY (jeden arkusz, wszystkie tory)",
        ha="center", fontsize=16, fontweight="bold")
ax.text(W/2, 45.78, "wg dokumentu v2 • wpięcie: JEDNA płytka rejestratora z WEJŚCIEM i WYJŚCIEM 20-pin w linii taśmy (druga taśma z uszkodzonej Q11 — dawcy) • UNO tylko streamuje — decyzje offline",
        ha="center", fontsize=9, color="#444")

ax.add_patch(FancyBboxPatch((0.4, 44.2), W-0.8, 1.35, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#EEF6FB", ec=C_INFO, lw=1.1, zorder=1))
ax.text(0.7, 45.28, "LEGENDA: para diod przy węźle = klamra 2×1N4148 (górna → +5 V, dolna ← masa) • kropka = połączenie, skrzyżowanie bez kropki = brak połączenia • symbol masy = masa rejestratora (= masa UNO)",
        fontsize=7.2, color="#0C4A6E")
ax.text(0.7, 44.92, "kolory: pomarańczowy = tor analogowy, zielony = tor cyfrowy, czerwony = +5 V, czarny = masa • w każdym odczepie PIERWSZY 100 kΩ przy punkcie odczepu • wszystkie rezystory 0,25 W",
        fontsize=7.2, color="#0C4A6E")
ax.text(0.7, 44.56, "wszystkie elementy między złączem a UNO siedzą na JEDNEJ płytce rejestratora (WEJŚCIE/WYJŚCIE 20-pin = 2× BHL20, przelot 1:1 + odczepy; §3.1) — wpinanej złączami, bez lutowania w ładowarce",
        fontsize=7.2, color="#0C4A6E")

# ================= ZLACZE 2x10 =================
box(0.4, 4.5, 2.7, 43.4, "Złącze 2×10", "w linii taśmy, przez\npłytkę rejestratora\n(§3.1)", tfs=9)
Y_CT_PIN = 41.95
Y_CT = 43.2      # gorna galaz: filtr -> A0
Y_DET = 40.7     # dolna galaz: detektor szczytu
Y_165 = 38.5
Y_CP = 36.4
LANES_P1 = [("V1", 31.2), ("V2", 29.6), ("V3", 28.0), ("ZL1", 26.4), ("ZL2", 24.8), ("ZL3", 23.2), ("ICP", 21.6)]
LANES_2 = [("K1", 18.4, "D"), ("K2", 16.8, "D"), ("K3", 15.2, "D"), ("K4", 13.6, "D"),
           ("8V", 12.0, "D"), ("NTC1", 10.4, "P"), ("NTC2", 8.8, "P")]
Y_GND = 6.1
piny_zlacza = ([("CT", Y_CT_PIN, "#222"), ("1.65", Y_165, "#222"), ("CP", Y_CP, "#222")]
               + [(n, y, "#222") for n, y in LANES_P1]
               + [(n, y, "#222") for n, y, t in LANES_2]
               + [("GND", Y_GND, C_GND), ("GND", 5.5, C_MUT), ("PE", 4.95, C_WARN)])
for n, y, kol in piny_zlacza:
    ax.text(2.48, y, n, ha="right", va="center", fontsize=7.3, fontweight="bold", color=kol, zorder=6)
    ax.add_patch(Circle((2.7, y), 0.055, fc="white", ec=kol, lw=1.4, zorder=6))
ax.text(3.0, 5.5, "nadmiarowy GND — bez odczepu", fontsize=6.2, color=C_MUT, va="center")
ax.text(3.0, 4.95, "PE — NIE podłączać do rejestratora! (§5.2)", fontsize=6.2, color=C_WARN, va="center", fontweight="bold")

# ================= TOR CT: rozgalezienie z pinu =================
wire([(2.7, Y_CT_PIN), (3.05, Y_CT_PIN)])
wire([(3.05, Y_CT), (3.05, Y_DET)])
dot(3.05, Y_CT_PIN)

# --- galaz gorna: filtr 2. rzedu -> A0 ---
y = Y_CT
wire([(3.05, y), (3.33, y)])
res_h(3.75, y, "100 kΩ")
wire([(4.17, y), (4.58, y)])
res_h(5.0, y, "100 kΩ")
wire([(5.42, y), (7.08, y)])
dot(5.75, y); cap_v(5.75, y, "1 nF", side="right")
ax.text(5.62, y+0.24, "w1", ha="center", fontsize=6.0, color=C_MUT)
klamra(6.7, y)
res_h(7.5, y, "100 kΩ")
wire([(7.92, y), (20.9, y)])
dot(8.4, y); cap_v(8.4, y, "470 pF", side="right")
ax.text(8.4, y+0.24, "w2", ha="center", fontsize=6.0, color=C_MUT)
wire([(20.9, y), (20.9, 40.6), (21.8, 40.6)])
ax.text(11.0, y+0.34, "TOR CT (główny podejrzany) — filtr antyaliasingowy 2. rzędu: f₁≈0,8 kHz, f₂≈3,4 kHz • pasmo wiarygodne 0–0,8 kHz • −36 dB @ 20 kHz",
        fontsize=7.0, color=C_INFO, fontweight="bold")

# --- galaz dolna: detektor szczytu -> MUX1 in7 ---
y = Y_DET
wire([(3.05, y), (3.33, y)])
res_h(3.75, y, "100 kΩ")
wire([(4.17, y), (4.58, y)])
res_h(5.0, y, "100 kΩ")
wire([(5.42, y), (6.49, y)])
klamra(5.75, y)
ax.text(5.98, y+0.24, "P", ha="center", fontsize=6.0, color=C_MUT)
dioda_h(6.6, y, "1N4148")
wire([(6.71, y), (9.18, y)])
dot(7.5, y); cap_v(7.5, y, "47 nF", side="right")
ax.text(7.32, y+0.24, "D", ha="center", fontsize=6.0, color=C_MUT)
dot(8.45, y)
wire([(8.45, y), (8.45, y-0.14)], C_GND, 1.4)
res_v(8.45, y-0.47, "1 MΩ", h=0.6)
wire([(8.45, y-0.77), (8.45, y-0.97)], C_GND, 1.4)
gnd(8.45, y-0.97)
res_h(9.6, y, "10 kΩ")
wire([(10.02, y), (14.85, y), (14.85, 20.0), (15.4, 20.0)])
ax.text(10.6, y+0.34, "DETEKTOR SZCZYTU CT — „pamięć” szpilek szybszych niż próbkowanie (τ ład. ≈ 9,4 ms, upust ≈ 47 ms) → MUX1 in7",
        fontsize=7.0, color=C_INFO, fontweight="bold")

# ================= TOR 1.65 -> A4 =================
y = Y_165
wire([(2.7, y), (3.33, y)])
res_h(3.75, y, "100 kΩ")
wire([(4.17, y), (4.58, y)])
res_h(5.0, y, "100 kΩ")
wire([(5.42, y), (21.8, y)])
klamra(5.75, y)
dot(6.45, y); cap_v(6.45, y, "1 nF", side="right")
ax.text(7.6, y+0.34, "TOR 1.65 — hipoteza pływającego odniesienia (zmierzono 4,31 V!)",
        fontsize=7.0, color=C_INFO, fontweight="bold")
ax.text(15.3, y+0.34, "pasmo ~0,8 kHz jak CT • szybki slot 2 kHz",
        fontsize=7.0, color=C_INFO, fontweight="bold")

# ================= TOR CP -> A1 + komparator -> D8 =================
y = Y_CP
wire([(2.7, y), (3.33, y)])
res_h(3.75, y, "120 kΩ")
wire([(4.17, y), (4.58, y)])
res_h(5.0, y, "120 kΩ")
wire([(5.42, y), (8.08, y)])
dot(5.75, y)
ax.text(5.5, y+0.22, "A", ha="center", fontsize=6.4, color=C_MUT, fontweight="bold")
# pull-up 100k do +5V
wire([(5.75, y), (5.75, y+0.14)], C_5V, 1.4)
res_v(5.75, y+0.44, "100 kΩ", h=0.6, side="left")
wire([(5.75, y+0.74), (5.75, y+0.9)], C_5V, 1.4)
ax.text(5.75, y+1.0, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold")
# 120k do masy
wire([(5.75, y), (5.75, y-0.17)], C_GND, 1.4)
res_v(5.75, y-0.47, "120 kΩ", h=0.6, side="left")
wire([(5.75, y-0.77), (5.75, y-0.97)], C_GND, 1.4)
gnd(5.75, y-0.97)
# odgalezienie komparatora (PRZED kondensatorem)
dot(6.4, y)
klamra(7.1, y)
res_h(8.5, y, "10 kΩ")
wire([(8.92, y), (21.8, y)])
dot(9.5, y); cap_v(9.5, y, "470 pF", side="right")
ax.text(9.5, y+0.22, "A′", ha="center", fontsize=6.4, color=C_MUT, fontweight="bold")
ax.text(9.0, y+0.72, "TOR CP (Control Pilot ±12 V) — poziomy → A1",
        fontsize=7.0, color=C_INFO, fontweight="bold")
ax.text(15.3, y+0.72, "komparator PRZED kondensatorem → D8 (błąd wypełnienia < 0,1%)",
        fontsize=7.0, color=C_INFO, fontweight="bold")
ax.text(3.35, y+1.0, "U(A) = 1,82 V + 0,152 · U(CP)", fontsize=6.6, color="#222", fontweight="bold")
# ga1az w dol do komparatora
wire([(6.4, y), (6.4, 36.05)])
res_v(6.4, 35.65, "100 kΩ", h=0.8)
wire([(6.4, 35.25), (6.4, 34.7), (10.5, 34.7)])
dot(6.4, 34.7)
ax.text(6.18, 34.9, "B", ha="center", fontsize=6.4, color=C_MUT, fontweight="bold")
wire([(6.4, 34.7), (6.4, 34.4)], C_GND, 1.4)
res_v(6.4, 34.1, "100 kΩ", h=0.6)
wire([(6.4, 33.8), (6.4, 33.55)], C_GND, 1.4)
gnd(6.4, 33.55)
# komparator LM393
ax.add_patch(FancyBboxPatch((10.5, 32.5), 3.1, 2.8, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc=C_BOX, ec=C_EDGE, lw=1.5, zorder=1))
ax.text(12.05, 35.05, "LM393 (½)", ha="center", fontsize=8.5, fontweight="bold", color="#222", zorder=2)
ax.text(10.65, 34.7, "IN−", fontsize=6.8, va="center", color="#222", zorder=2)
ax.text(10.65, 33.1, "IN+", fontsize=6.8, va="center", color="#222", zorder=2)
ax.text(13.45, 34.2, "OUT", fontsize=6.8, va="center", ha="right", color="#222", zorder=2)
ax.text(12.05, 32.75, "druga połówka wolna (rezerwa)", ha="center", fontsize=5.8, color=C_MUT, zorder=2)
# prog na IN+
wire([(9.2, 33.1), (10.5, 33.1)], C_INFO, 1.6)
dot(9.2, 33.1, C_INFO)
wire([(9.2, 33.1), (9.2, 33.3)], C_5V, 1.3)
res_v(9.2, 33.6, "100 kΩ", h=0.6)
wire([(9.2, 33.9), (9.2, 34.05)], C_5V, 1.3)
ax.text(9.2, 34.17, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold")
wire([(9.2, 33.1), (9.2, 32.9)], C_GND, 1.3)
res_v(9.2, 32.6, "10 kΩ", h=0.6)
wire([(9.2, 32.3), (9.2, 32.1)], C_GND, 1.3)
gnd(9.2, 32.1)
ax.text(8.9, 32.78, "próg 0,455 V ≈ U(CP) = −6 V", fontsize=6.4, color=C_INFO, ha="right")
# wyjscie OC + pull-up + D8
wire([(13.6, 34.2), (21.8, 34.2)], C_DIG, 1.9)
dot(15.6, 34.2, C_DIG)
wire([(15.6, 34.2), (15.6, 34.42)], C_5V, 1.4)
res_v(15.6, 34.75, "10 kΩ", h=0.6)
wire([(15.6, 35.08), (15.6, 35.22)], C_5V, 1.4)
ax.text(15.6, 35.34, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold")
ax.text(16.6, 34.42, "wyjście otwarty kolektor + podciąganie", fontsize=6.0, color=C_MUT)
# histereza 470k: z wyjscia do IN+
dot(13.9, 34.2, C_DIG)
wire([(13.9, 34.2), (13.9, 31.6), (10.05, 31.6)], C_MUT, 1.3)
wire([(10.05, 31.6), (10.05, 33.1)], C_MUT, 1.3)
dot(10.05, 33.1, C_INFO)
res_h(12.0, 31.6, "470 kΩ (histereza)", fs=6.2, lab_dy=0.26)
# tabelka poziomow CP
ax.add_patch(FancyBboxPatch((3.0, 31.9), 2.6, 3.0, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#E8F4FD", ec=C_INFO, lw=1.0, zorder=1))
ax.text(3.15, 34.62, "Poziomy CP → A′ (A1):", fontsize=6.6, fontweight="bold", color=C_INFO, zorder=2)
for i, t in enumerate(["+12 V (stan A) → 3,64 V", "+9 V (stan B) → 3,18 V", "+6 V (stan C) → 2,73 V",
                       "0 V → 1,82 V", "−12 V (dół PWM) → 0,00 V"]):
    ax.text(3.15, 34.25-i*0.42, t, fontsize=6.2, color="#0C4A6E", zorder=2)
ax.text(3.15, 32.08, "obciążenie CP ≤ 50 µA (pomijalne)", fontsize=5.6, color="#0C4A6E", zorder=2)

# ================= LANES: odczepy typ P / typ D =================
def lane(nazwa, y, typ, x_end=15.4):
    wire([(2.7, y), (3.33, y)])
    res_h(3.75, y, "100 kΩ")
    wire([(4.17, y), (4.58, y)])
    res_h(5.0, y, "100 kΩ")
    wire([(5.42, y), (7.68, y)])
    if typ == "D":
        dot(5.65, y)
        wire([(5.65, y), (5.65, y-0.17)], C_GND, 1.4)
        res_v(5.65, y-0.5, "220 kΩ", h=0.6, side="left")
        wire([(5.65, y-0.8), (5.65, y-1.0)], C_GND, 1.4)
        gnd(5.65, y-1.0)
    klamra(6.6, y)
    res_h(8.1, y, "10 kΩ")
    wire([(8.52, y), (x_end, y)])

for n, y in LANES_P1:
    lane(n, y, "P")
    ax.text(11.4, y+0.16, "typ P", fontsize=5.8, color=C_MUT)
for n, y, t in LANES_2:
    lane(n, y, t)
    if n == "K4":
        ax.text(10.6, y+0.16, "typ D · anomalia: 5,08 V → 2,66 V po dzielniku!", fontsize=5.8, color=C_WARN, fontweight="bold")
    elif t == "D":
        ax.text(10.9, y+0.16, "typ D (dzielnik ×0,524)", fontsize=5.8, color=C_MUT)
    else:
        ax.text(11.4, y+0.16, "typ P", fontsize=5.8, color=C_MUT)

# ================= MUX1 / MUX2 =================
box(15.4, 19.3, 18.4, 32.0, "CD4051BE — MUX1 (8→1)", tfs=7.8, tdy=0.28)
mux1_in = [("in0 · V1", 31.2), ("in1 · V2", 29.6), ("in2 · V3", 28.0), ("in3 · ZL1", 26.4),
           ("in4 · ZL2", 24.8), ("in5 · ZL3", 23.2), ("in6 · ICP", 21.6), ("in7 · DETEKTOR", 20.0)]
for t, yy in mux1_in:
    ax.text(15.55, yy, t, fontsize=6.4, va="center", color="#333", zorder=2)
ax.text(18.25, 25.6, "OUT", fontsize=6.6, va="center", ha="right", color="#222", fontweight="bold", zorder=2)
for t, yy in [("A", 20.6), ("B", 20.1), ("C", 19.6)]:
    ax.text(18.25, yy, t, fontsize=6.2, va="center", ha="right", color=C_DIG, fontweight="bold", zorder=2)

box(15.4, 6.5, 18.4, 19.05, "CD4051BE — MUX2 (8→1)", tfs=7.8, tdy=0.28)
mux2_in = [("in0 · K1", 18.4), ("in1 · K2", 16.8), ("in2 · K3", 15.2), ("in3 · K4", 13.6),
           ("in4 · 8V", 12.0), ("in5 · NTC1", 10.4), ("in6 · NTC2", 8.8), ("in7 · masa (autotest)", 7.2)]
for t, yy in mux2_in:
    ax.text(15.55, yy, t, fontsize=6.4, va="center", color="#333", zorder=2)
ax.text(18.25, 12.8, "OUT", fontsize=6.6, va="center", ha="right", color="#222", fontweight="bold", zorder=2)
for t, yy in [("A", 8.0), ("B", 7.5), ("C", 7.0)]:
    ax.text(18.25, yy, t, fontsize=6.2, va="center", ha="right", color=C_DIG, fontweight="bold", zorder=2)

# autotest masy na in7 MUX2
wire([(15.4, 7.2), (14.7, 7.2), (14.7, 7.0)], C_GND, 1.4)
gnd(14.7, 7.0)

# wyjscia MUX -> A2/A3 z 470 pF
wire([(18.4, 25.6), (21.8, 25.6)])
dot(21.0, 25.6); cap_v(21.0, 25.6, "470 pF", side="left")
wire([(18.4, 12.8), (21.8, 12.8)])
dot(21.0, 12.8); cap_v(21.0, 12.8, "470 pF", side="left")

# magistrala adresowa D4-D6 (zielona)
def bus(x, y_uno, y_m1, y_m2):
    wire([(21.8, y_uno), (x, y_uno), (x, y_m2), (18.4, y_m2)], C_DIG, 1.6)
    dot(x, y_m1, C_DIG)
    wire([(x, y_m1), (18.4, y_m1)], C_DIG, 1.6)

bus(19.5, 23.4, 20.6, 8.0)
bus(19.9, 22.8, 20.1, 7.5)
bus(20.3, 22.2, 19.6, 7.0)

# ================= UNO =================
box(21.8, 9.6, 26.2, 42.3, "Arduino UNO", "akwizycja w przerwaniu ADC • strumień binarny", tfs=11)
uno_piny = [("A0", 40.6, "CT — szybki slot 2 kHz", C_SIG),
            ("A4", 38.5, "1.65 — szybki slot 2 kHz", C_SIG),
            ("A1", 36.4, "poziomy CP (węzeł A′)", C_SIG),
            ("D8", 34.2, "komparator → Timer1 (wypełnienie PWM)", C_DIG),
            ("A2", 25.6, "wyjście MUX1", C_SIG),
            ("D4", 23.4, "adres A", C_DIG),
            ("D5", 22.8, "adres B", C_DIG),
            ("D6", 22.2, "adres C", C_DIG),
            ("A3", 12.8, "wyjście MUX2", C_SIG),
            ("D2", 10.6, "licznik zboczy UART DWIN", C_DIG),
            ("GND", 10.0, "masa wspólna (jedyne połączenie mas)", C_GND)]
for nazwa, yy, opis, kol in uno_piny:
    ax.add_patch(Circle((21.8, yy), 0.055, fc="white", ec=kol, lw=1.4, zorder=6))
    ax.text(22.0, yy, nazwa + " — " + opis, fontsize=6.8, va="center", color="#222", zorder=6,
            fontweight="bold")
ax.text(22.0, 32.9, "A5 — rezerwa (opcja: suma aktywności UART)", fontsize=6.4, va="center", color=C_MUT, zorder=6)
ax.text(22.0, 32.4, "D13 — LED „żyję” (wbudowana)", fontsize=6.4, va="center", color=C_MUT, zorder=6)
ax.text(22.0, 20.9, "WEWNĄTRZ (oprogramowanie):", fontsize=6.8, color="#222", fontweight="bold", zorder=6)
uno_info = ["• maszyna stanów w przerwaniu ADC (preskaler 64,", "   zajętość ~62% śr., strop projektowy 75%)",
            "• pierwsza konwersja po zmianie kanału odrzucana",
            "• Timer1: przechwytywanie zboczy D8 (rozdz. µs)",
            "• bandgap 1,1 V → korekcja AVcc w każdej ramce",
            "• zakaz String • blokady przerwań < 20 µs",
            "• ramka co 20 ms (~242 B): 80 próbek szybkich,",
            "   2 obiegi MUX, CP, AVcc, licznik D2, RAM, CRC-8",
            "• +5 V z UNO zasila: klamry, CD4051BE, LM393"]
for i, t in enumerate(uno_info):
    ax.text(22.0, 20.4-i*0.42, t, fontsize=6.2, color="#333", zorder=6)

# ================= MASA: jeden pin GND -> UNO =================
wire([(2.7, Y_GND), (21.3, Y_GND), (21.3, 10.0), (21.8, 10.0)], C_GND, 2.0)
ax.text(7.5, Y_GND-0.28, "JEDEN pin GND złącza → masa UNO — jedyne połączenie mas (PE nigdy!)", fontsize=6.6, color=C_GND, fontweight="bold")

# ================= UART DWIN =================
box(0.4, 2.9, 2.7, 4.4, "Złącze wyśw.\nDWIN T5L0", tfs=7.0, tdy=0.45)
ax.add_patch(Circle((2.7, 3.55), 0.055, fc="white", ec="#222", lw=1.4, zorder=6))
ax.text(2.48, 3.55, "TX", ha="right", va="center", fontsize=7.0, fontweight="bold", color="#222", zorder=6)
wire([(2.7, 3.55), (3.33, 3.55)], C_DIG, 1.7)
res_h(3.75, 3.55, "100 kΩ")
wire([(4.17, 3.55), (4.58, 3.55)], C_DIG, 1.7)
res_h(5.0, 3.55, "100 kΩ")
wire([(5.42, 3.55), (20.7, 3.55), (20.7, 10.6), (21.8, 10.6)], C_DIG, 1.7)
klamra(5.9, 3.55)
ax.text(7.0, 3.75, "znacznik chwili błędu: licznik zboczy w oknach 20 ms • przed montażem zmierzyć poziom (3,3/5 V)", fontsize=6.2, color=C_MUT)

# ================= LAPTOP =================
box(21.8, 3.2, 26.2, 6.4, "Laptop — NA BATERII", "skrypt Python: surowy plik binarny +\ndekodowany CSV + dyżurny podgląd", tfs=9)
wire([(24.0, 9.6), (24.0, 6.4)], C_INFO, 2.2)
ax.text(24.15, 8.0, "USB — strumień binarny 250 000 bodów", fontsize=6.4, color=C_INFO, rotation=90, va="center")
ax.text(22.0, 4.2, "klawisz operatora = bajt do UNO →\nznacznik w strumieniu (wspólna oś czasu)", fontsize=6.0, color="#333", zorder=6)

# ================= INSET: fizyczny uklad zlacza =================
ax.add_patch(FancyBboxPatch((0.4, 0.4), 9.4, 2.1, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#FAFAF9", ec=C_EDGE, lw=1.2, zorder=1))
ax.text(0.7, 2.16, "Fizyczny układ złącza 2×10 (kolejność pinów; na schemacie wyżej piny uporządkowano wg torów):", fontsize=6.6, fontweight="bold", color="#222", zorder=2)
rz1 = ["PE", "NTC1", "ICP", "8V", "K1", "K2", "K3", "K4", "1.65", "CP"]
rz2 = ["GND", "GND", "CT", "NTC2", "ZL3", "ZL2", "ZL1", "V1", "V2", "V3"]
ax.text(0.75, 1.62, "rząd 1:", fontsize=6.4, color="#555", zorder=2)
ax.text(0.75, 1.05, "rząd 2:", fontsize=6.4, color="#555", zorder=2)
for i, (a, b) in enumerate(zip(rz1, rz2)):
    xx = 1.75 + i*0.78
    kol_a = C_WARN if a == "PE" else "#222"
    ax.text(xx, 1.62, a, fontsize=6.4, ha="center", color=kol_a, fontweight="bold", zorder=2)
    ax.text(xx, 1.05, b, fontsize=6.4, ha="center", color="#222", fontweight="bold", zorder=2)
ax.text(0.75, 0.6, "przed budową: zdzwonić omomierzem KAŻDY pin do znanych węzłów (urządzenie odłączone) — §2", fontsize=5.8, color=C_MUT, zorder=2)

# ================= NOTATKI =================
ax.add_patch(FancyBboxPatch((10.2, 0.4), 16.0, 2.1, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#FEF3C7", ec="#D97706", lw=1.2, zorder=1))
naty = ["• BEZPIECZEŃSTWO: przed pierwszą sesją pomiar charakteru masy (§5.1); masa związana z siecią (reżim B) = sesji NIE prowadzić • laptop całą sesję na baterii, zasilacz poza pokojem",
        "• SEKWENCJA: najpierw zasilić rejestrator (USB), potem ładowarkę; demontaż odwrotnie • tor mocy 40 A osłonięty • oba CD4051BE: INH→masa, VDD=+5 V, VEE=VSS=masa, 100 nF przy każdym",
        "• FILOZOFIA: UNO niczego nie interpretuje — ciągły surowy strumień, wszystkie progi i obwiednie liczy analiza offline z sesji bazowej • „cichy log ≠ czysta linia” (martwe pola: §8)"]
for i, t in enumerate(naty):
    ax.text(10.45, 2.05-i*0.55, t, fontsize=6.6, color="#7A5800", zorder=2)

plt.savefig(OUT + r"\AMPERE_POINT_rejestrator_Q11_schemat_PELNY.png", dpi=110,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: schemat pelny zapisany")
