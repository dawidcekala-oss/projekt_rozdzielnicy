# -*- coding: utf-8 -*-
"""Architektura ULN2003AN (Texas Instruments) i jego zastosowanie w symulatorze.
Zrodlo danych: TI SLRS027T, grudzien 1976, rewizja marzec 2025."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\symulator_pojazdu"

C_SIG = "#B45309"
C_DIG = "#15803D"
C_GND = "#111111"
C_5V = "#B00020"
C_INFO = "#0369A1"
C_MUT = "#888888"
C_BOX = "#F7F7F5"

W, H = 16.2, 11.6
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def panel(x0, y0, x1, y1, tytul, fs=10.5):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0,
                 boxstyle="round,pad=0.02,rounding_size=0.08",
                 fc="white", ec="#BBB", lw=1.2, zorder=0))
    ax.text(x0+0.18, y1-0.30, tytul, fontsize=fs, fontweight="bold", color="#111", zorder=2)


def wire(pts, color=C_GND, lw=1.8):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
            solid_capstyle="round", zorder=3)


def dot(x, y, color=C_GND):
    ax.add_patch(Circle((x, y), 0.055, fc=color, ec=color, zorder=6))


def pinc(x, y, color="#222"):
    ax.add_patch(Circle((x, y), 0.075, fc="white", ec=color, lw=1.6, zorder=6))


def res_h(xc, yc, label, fs=8.0, dy=0.23, col="#222"):
    ax.add_patch(Rectangle((xc-0.33, yc-0.11), 0.66, 0.22, fc="white", ec="#222", lw=1.4, zorder=5))
    ax.text(xc, yc+dy, label, ha="center", fontsize=fs, color=col, fontweight="bold", zorder=6)


def res_v(xc, yc, label, h=0.6, fs=8.0, side="right", col="#222"):
    ax.add_patch(Rectangle((xc-0.11, yc-h/2), 0.22, h, fc="white", ec="#222", lw=1.4, zorder=5))
    dx = 0.18 if side == "right" else -0.18
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, yc, label, ha=ha, va="center", fontsize=fs, color=col, fontweight="bold", zorder=6)


def npn(xb, yb, nazwa=""):
    """Tranzystor NPN: pionowa kreska bazy w (xb,yb), kolektor w gore-prawo, emiter w dol-prawo."""
    ax.plot([xb, xb], [yb-0.27, yb+0.27], color="#222", lw=3.0, zorder=5, solid_capstyle="butt")
    wire([(xb-0.45, yb), (xb, yb)], "#222", 1.8)
    wire([(xb, yb+0.16), (xb+0.60, yb+0.62)], "#222", 1.8)
    wire([(xb, yb-0.16), (xb+0.60, yb-0.62)], "#222", 1.8)
    ex, ey = xb+0.40, yb-0.46
    ax.add_patch(Polygon([(ex, ey), (ex-0.17, ey+0.05), (ex-0.05, ey+0.18)],
                 fc="#222", ec="#222", zorder=6))
    if nazwa:
        ax.text(xb-0.12, yb+0.40, nazwa, ha="right", fontsize=9.0, fontweight="bold",
                color="#222", zorder=6)


def dioda_v_gora(xc, yc):
    ax.add_patch(Polygon([(xc-0.15, yc-0.14), (xc+0.15, yc-0.14), (xc, yc+0.11)],
                 fc="white", ec="#222", lw=1.5, zorder=5))
    ax.plot([xc-0.15, xc+0.15], [yc+0.13, yc+0.13], color="#222", lw=2.4, zorder=5)


# ═══════════════════════ TYTUL ═══════════════════════
ax.text(W/2, 11.20, "ULN2003AN — architektura układu i jego rola w symulatorze pojazdu",
        ha="center", fontsize=15.0, fontweight="bold")
ax.text(W/2, 10.88, "siedem par Darlingtona ze wspólnym emiterem, wyjścia typu otwarty kolektor, wbudowane diody gaszące o wspólnej katodzie",
        ha="center", fontsize=8.6, color="#555")
ax.text(W/2, 10.62, "dane: Texas Instruments SLRS027T (grudzień 1976, rewizja marzec 2025) • egzemplarz z nadrukiem ULN2003AN, obudowa PDIP-16",
        ha="center", fontsize=7.8, color=C_INFO)

# ═══════════════════════ PANEL A — WYPROWADZENIA ═══════════════════════
panel(0.35, 5.25, 4.95, 10.30, "Wyprowadzenia, widok od góry")

bx0, bx1, by0, by1 = 2.10, 3.25, 6.50, 9.55
ax.add_patch(Rectangle((bx0, by0), bx1-bx0, by1-by0, fc=C_BOX, ec="#222", lw=1.8, zorder=1))
ax.add_patch(Circle(((bx0+bx1)/2, by1), 0.16, fc="white", ec="#222", lw=1.5, zorder=2))

lewe  = ["1B", "2B", "3B", "4B", "5B", "6B", "7B", "E"]
prawe = ["1C", "2C", "3C", "4C", "5C", "6C", "7C", "COM"]
for i in range(8):
    yy = 9.28 - i*0.36
    wire([(bx0-0.30, yy), (bx0, yy)], "#222", 1.6)
    ax.text(bx0-0.38, yy, str(i+1) + "  " + lewe[i], ha="right", va="center",
            fontsize=8.2, fontweight="bold", color="#222", zorder=6)
    wire([(bx1, yy), (bx1+0.30, yy)], "#222", 1.6)
    ax.text(bx1+0.38, yy, str(16-i) + "  " + prawe[i], ha="left", va="center",
            fontsize=8.2, fontweight="bold", color="#222", zorder=6)

for i, t in enumerate(["B  — wejście kanału,   C  — wyjście kanału",
                       "E  — wspólny emiter wszystkich kanałów:",
                       "        w naszym układzie masa",
                       "COM — wspólna katoda diod gaszących:",
                       "        w naszym układzie +5 V"]):
    ax.text(0.50, 6.18-i*0.210, t, fontsize=7.6, color="#333", zorder=6)

# ═══════════════════════ PANEL B — ARCHITEKTURA KANALU ═══════════════════════
panel(5.25, 5.25, 15.85, 10.30, "Architektura jednego z siedmiu kanałów  (TI SLRS027, rys. 7-2)")

pinc(6.15, 7.50)
ax.text(6.15, 7.72, "Wejście  B", ha="center", fontsize=8.6, fontweight="bold", color=C_DIG, zorder=6)
wire([(6.15, 7.50), (6.82, 7.50)])
res_h(7.15, 7.50, "R$_B$ = 2,7 kΩ", fs=8.4)
wire([(7.48, 7.50), (8.33, 7.50)])
dot(8.30, 7.50)
npn(8.78, 7.50, "Q1")

wire([(8.30, 7.50), (8.30, 7.18)])
res_v(8.30, 6.88, "7,2 kΩ", h=0.6, side="left", fs=8.4)
wire([(8.30, 6.58), (8.30, 6.30), (9.38, 6.30)])
wire([(9.38, 6.88), (9.38, 6.30)])
dot(9.38, 6.30)

npn(10.55, 6.30, "Q2")
wire([(9.38, 6.30), (10.10, 6.30)])
dot(9.95, 6.30)
wire([(9.95, 6.30), (9.95, 6.18)])
res_v(9.95, 5.90, "3 kΩ", h=0.55, side="left", fs=8.4)
wire([(9.95, 5.62), (9.95, 5.50), (13.05, 5.50)])
wire([(11.15, 5.68), (11.15, 5.50)])
dot(11.15, 5.50)
pinc(13.05, 5.50)
ax.text(13.20, 5.50, "E  — nóżka 8  (masa)", ha="left", va="center",
        fontsize=8.6, fontweight="bold", color=C_GND, zorder=6)

wire([(9.38, 8.12), (11.15, 8.12)])
wire([(11.15, 6.92), (11.15, 8.12)])
wire([(11.15, 8.12), (13.05, 8.12)])
dot(11.90, 8.12)
pinc(13.05, 8.12)
ax.text(13.20, 8.12, "Wyjście  C", ha="left", va="center", fontsize=8.6,
        fontweight="bold", color=C_SIG, zorder=6)

wire([(11.90, 8.12), (11.90, 8.50)])
dioda_v_gora(11.90, 8.66)
wire([(11.90, 8.79), (11.90, 9.10)])
pinc(11.90, 9.10)
ax.text(11.90, 9.30, "COM — nóżka 9", ha="center", fontsize=8.6,
        fontweight="bold", color=C_5V, zorder=6)
ax.text(12.15, 8.62, "dioda gasząca", ha="left", va="center", fontsize=7.8,
        color="#555", zorder=6)

for i, t in enumerate(["Wartości rezystorów nominalne.",
                       "Dioda kolektor–emiter jest strukturą",
                       "pasożytniczą i NIE służy do przewodzenia",
                       "prądu — gdyby kolektor mógł zejść poniżej",
                       "masy, trzeba zewnętrznej diody Schottky'ego."]):
    ax.text(5.42, 6.50-i*0.225, t, fontsize=7.4, color="#7A5800", zorder=6)

# ═══════════════════════ PANEL C — ZASTOSOWANIE ═══════════════════════
panel(0.35, 0.35, 8.55, 5.00, "Zastosowanie w symulatorze — jeden kanał, jeden przekaźnik")

wire([(1.00, 4.25), (8.10, 4.25)], C_5V, 2.2)
ax.text(1.00, 4.38, "+5 V", fontsize=8.8, fontweight="bold", color=C_5V, zorder=6)
wire([(1.00, 1.45), (8.10, 1.45)], C_GND, 2.2)
ax.text(1.00, 1.56, "masa", fontsize=8.8, fontweight="bold", color=C_GND, zorder=6)

ax.add_patch(FancyBboxPatch((0.70, 2.80), 1.55, 0.80, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc=C_BOX, ec="#222", lw=1.5, zorder=1))
ax.text(1.475, 3.28, "Nano", ha="center", fontsize=9.0, fontweight="bold", zorder=2)
ax.text(1.475, 2.98, "D7", ha="center", fontsize=8.2, color="#555", zorder=2)

ax.add_patch(FancyBboxPatch((3.30, 2.20), 2.05, 1.85, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc=C_BOX, ec="#222", lw=1.8, zorder=1))
ax.text(4.325, 3.78, "ULN2003AN", ha="center", fontsize=9.4, fontweight="bold", zorder=2)
ax.text(4.325, 3.52, "kanał 1", ha="center", fontsize=8.2, color="#555", zorder=2)

wire([(2.25, 3.20), (3.30, 3.20)], C_DIG, 1.8)
ax.text(2.77, 3.32, "1,33 mA", ha="center", fontsize=7.8, color=C_DIG, fontweight="bold", zorder=6)
ax.text(3.38, 3.20, "1B", ha="left", va="center", fontsize=7.8, fontweight="bold", zorder=6)

wire([(5.35, 3.20), (6.35, 3.20)], C_SIG, 1.8)
ax.text(5.28, 3.20, "1C", ha="right", va="center", fontsize=7.8, fontweight="bold", zorder=6)
wire([(6.35, 3.20), (6.35, 3.43)], C_SIG, 1.8)
res_v(6.35, 3.72, "cewka 125 Ω", h=0.58, fs=8.0)
wire([(6.35, 4.01), (6.35, 4.25)], C_5V, 1.8)
dot(6.35, 4.25, C_5V)
ax.text(6.12, 3.30, "33 mA", ha="right", fontsize=7.8, color=C_SIG, fontweight="bold", zorder=6)

wire([(4.05, 2.20), (4.05, 1.45)], C_GND, 1.8)
dot(4.05, 1.45)
ax.text(4.13, 1.80, "nóżka 8", ha="left", fontsize=7.8, fontweight="bold", zorder=6)
wire([(4.85, 4.05), (4.85, 4.25)], C_5V, 1.8)
dot(4.85, 4.25, C_5V)
ax.text(4.93, 4.10, "nóżka 9", ha="left", fontsize=7.8, fontweight="bold", color=C_5V, zorder=6)

ax.add_patch(Rectangle((6.85, 2.05), 1.15, 0.95, fill=False, ec=C_DIG, lw=1.0,
             linestyle=(0, (2, 2)), zorder=4))
ax.add_patch(Circle((7.10, 2.35), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
ax.add_patch(Circle((7.80, 2.35), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
ax.plot([7.14, 7.76], [2.38, 2.70], color="#222", lw=1.6, zorder=5)
ax.text(7.425, 1.86, "styk w torze pilota", ha="center", fontsize=7.4, color="#555", zorder=6)

for i, t in enumerate(["prąd wejściowy przy 5 V:   (5,0 − 1,4) / 2,7 kΩ = 1,33 mA   — tyle oddaje wyprowadzenie procesora",
                       "prąd cewki:   (5,02 − 0,9) / 125 Ω = 33 mA   — tyle przejmuje układ zamiast procesora",
                       "cztery kanały naraz: 132 mA przez nóżkę 8, przy dopuszczalnych 2,5 A"]):
    ax.text(0.50, 1.10-i*0.235, t, fontsize=7.5, color="#333", zorder=6)

# ═══════════════════════ PANEL D — PARAMETRY ═══════════════════════
panel(8.85, 0.35, 15.85, 5.00, "Parametry z karty katalogowej i co z nich wynika dla nas")

wiersze = [
    ("Wartości graniczne", "", True),
    ("napięcie kolektor–emiter", "50 V", False),
    ("napięcie wsteczne diody gaszącej", "50 V", False),
    ("napięcie wejściowe", "30 V", False),
    ("szczytowy prąd kolektora, jeden kanał", "500 mA", False),
    ("prąd wspólnego emitera (nóżka 8)", "2,5 A", False),
    ("temperatura otoczenia", "−40…70 °C", False),
    ("Charakterystyki przy 25 °C", "", True),
    ("spadek na przewodzącym kanale, 100 mA", "0,9 V typ / 1,1 V max", False),
    ("spadek na przewodzącym kanale, 200 mA", "1,0 V typ / 1,3 V max", False),
    ("spadek na przewodzącym kanale, 350 mA", "1,2 V typ / 1,6 V max", False),
    ("prąd wejściowy przy 3,85 V", "0,93 mA typ / 1,35 mA max", False),
    ("napięcie załączające przy 200 mA", "2,4 V max", False),
    ("prąd upływu wyłączonego wyjścia", "50 µA (100 µA przy 70 °C)", False),
    ("spadek na diodzie gaszącej, 350 mA", "1,7 V typ / 2,0 V max", False),
    ("prąd wsteczny diody gaszącej", "50 µA przy 50 V", False),
    ("pojemność wejściowa", "15 pF typ / 25 pF max", False),
    ("opóźnienie przełączania", "0,25 µs typ / 1 µs max", False),
]
y = 4.48
for tekst, wart, naglowek in wiersze:
    if naglowek:
        y -= 0.06
        ax.text(9.02, y, tekst, fontsize=8.4, fontweight="bold", color=C_INFO, zorder=6)
        ax.plot([9.02, 15.65], [y-0.09, y-0.09], color=C_INFO, lw=0.8, zorder=4)
        y -= 0.25
    else:
        ax.text(9.02, y, tekst, fontsize=7.4, color="#333", zorder=6)
        ax.text(15.65, y, wart, fontsize=7.4, color="#111", fontweight="bold", ha="right", zorder=6)
        y -= 0.165

ax.add_patch(FancyBboxPatch((8.98, 0.42), 6.80, 0.56, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc="#FEF3C7", ec="#D97706", lw=1.1, zorder=1))
for i, t in enumerate(["Nasze 33 mA leży PONIŻEJ najniższego punktu tabeli (100 mA) — spadek 0,9 V to oszacowanie w górę,",
                       "nie wartość katalogowa. Cewka dostaje co najmniej 4,02 V przy zmierzonym zadziałaniu 3,1 V."]):
    ax.text(9.10, 0.80-i*0.225, t, fontsize=7.3, color="#7A5800", zorder=2)

plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_detal_uln.pdf",
            bbox_inches="tight", facecolor="white")
plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_detal_uln.png", dpi=150,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: architektura ULN2003AN zapisana (PDF + PNG)")
