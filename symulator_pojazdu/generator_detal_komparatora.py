# -*- coding: utf-8 -*-
"""Szczegol: dokladne polaczenia komparatora LM393 w symulatorze pojazdu.
Stan faktyczny egzemplarza: nozka 5 urwana, dlatego nozka 6 idzie do masy."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\symulator_pojazdu"

C_SIG = "#B45309"
C_DIG = "#15803D"
C_GND = "#111111"
C_5V = "#B00020"
C_INFO = "#0369A1"
C_MUT = "#888888"

W, H = 13.2, 7.6
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def wire(pts, color=C_SIG, lw=1.9):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
            solid_capstyle="round", zorder=3)


def dot(x, y, color=C_SIG):
    ax.add_patch(Circle((x, y), 0.045, fc=color, ec=color, zorder=6))


def res_v(xc, yc, label, h=0.6, fs=8.0, side="right"):
    ax.add_patch(Rectangle((xc-0.10, yc-h/2), 0.20, h, fc="white", ec="#222", lw=1.4, zorder=5))
    dx = 0.16 if side == "right" else -0.16
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, yc, label, ha=ha, va="center", fontsize=fs, color="#222",
            fontweight="bold", zorder=6)


def res_h(xc, yc, label, fs=8.0, lab_dy=0.22):
    ax.add_patch(Rectangle((xc-0.32, yc-0.10), 0.64, 0.20, fc="white", ec="#222", lw=1.4, zorder=5))
    ax.text(xc, yc+lab_dy, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def gnd(x, y):
    wire([(x, y), (x, y-0.07)], C_GND, 1.6)
    for i, w in enumerate([0.13, 0.085, 0.045]):
        ax.plot([x-w, x+w], [y-0.09-i*0.05, y-0.09-i*0.05], color=C_GND, lw=1.8, zorder=4)


def cap_v(xc, y_top, label, fs=8.0):
    wire([(xc, y_top), (xc, y_top-0.22)], C_GND, 1.5)
    ax.plot([xc-0.14, xc+0.14], [y_top-0.22, y_top-0.22], color="#222", lw=2.4, zorder=5)
    ax.plot([xc-0.14, xc+0.14], [y_top-0.33, y_top-0.33], color="#222", lw=2.4, zorder=5)
    wire([(xc, y_top-0.33), (xc, y_top-0.46)], C_GND, 1.5)
    ax.text(xc+0.20, y_top-0.27, label, ha="left", va="center", fontsize=fs,
            color="#222", fontweight="bold", zorder=6)


def plus5(x, y):
    ax.text(x, y, "+5 V", ha="center", va="bottom", fontsize=8.5, color=C_5V,
            fontweight="bold", zorder=6)


# ═══════════ TYTUL ═══════════
ax.text(W/2, 7.24, "Komparator LM393 — dokładne połączenia wyprowadzeń",
        ha="center", fontsize=13.5, fontweight="bold")
ax.text(W/2, 6.94, "stan faktyczny egzemplarza: nóżka 5 urwana przy montażu, dlatego nóżka 6 idzie do masy, a nie do zasilania",
        ha="center", fontsize=8.2, color="#B45309")
ax.text(W/2, 6.70, "kropka = połączenie • skrzyżowanie bez kropki = brak połączenia",
        ha="center", fontsize=7.6, color=C_INFO)

# ═══════════ OBUDOWA ═══════════
ax.add_patch(FancyBboxPatch((5.0, 3.6), 3.0, 1.8, boxstyle="round,pad=0.02,rounding_size=0.08",
             fc="#F4F4F2", ec="#222", lw=2.0, zorder=1))
ax.add_patch(Circle((5.20, 4.12), 0.09, fc="#222", ec="#222", zorder=4))
ax.text(6.5, 4.74, "LM393", ha="center", fontsize=12.5, fontweight="bold", color="#222", zorder=2)
ax.text(6.5, 4.42, "widok od góry, kropka przy nóżce 1", ha="center", fontsize=7.4,
        color="#666", zorder=2)

PX = [5.45, 6.15, 6.85, 7.55]
for i, x in enumerate(PX):                      # dolny rzad: 1 2 3 4
    wire([(x, 3.6), (x, 3.25)], C_GND, 2.2)
    ax.text(x, 3.80, str(i+1), ha="center", va="center", fontsize=9.5,
            fontweight="bold", color="#222", zorder=4)
for i, x in enumerate(PX):                      # gorny rzad: 8 7 6 5
    wire([(x, 5.4), (x, 5.75)], C_GND, 2.2)
    ax.text(x, 5.20, str(8-i), ha="center", va="center", fontsize=9.5,
            fontweight="bold", color="#222", zorder=4)

# ═══════════ NOZKA 1 — wyjscie ═══════════
wire([(5.45, 3.25), (5.45, 3.05), (3.95, 3.05)], C_DIG)
dot(4.55, 3.05, C_DIG)
ax.text(3.88, 3.05, "→ wejście D8", ha="right", va="center", fontsize=8.6,
        fontweight="bold", color=C_DIG, zorder=6)
wire([(4.55, 3.05), (4.55, 3.50)], C_5V, 1.5)
res_v(4.55, 3.80, "10 kΩ", h=0.6, side="left")
wire([(4.55, 4.10), (4.55, 4.34)], C_5V, 1.5)
plus5(4.55, 4.39)
# histereza 470 k: nozka 1 -> nozka 3
wire([(4.55, 3.05), (4.55, 1.00), (6.18, 1.00)], C_MUT, 1.6)
res_h(6.60, 1.00, "470 kΩ — histereza")
wire([(7.02, 1.00), (9.40, 1.00), (9.40, 2.30)], C_MUT, 1.6)

# ═══════════ NOZKA 2 — wejscie sygnalu ═══════════
wire([(6.15, 3.25), (6.15, 2.75), (2.40, 2.75)], C_SIG)
dot(2.40, 2.75, C_SIG)
wire([(2.40, 2.75), (2.40, 3.10)], C_SIG, 1.6)
res_v(2.40, 3.40, "100 kΩ", h=0.6, side="left")
wire([(2.40, 3.70), (2.40, 4.38)], C_SIG, 1.6)
ax.text(2.40, 4.46, "z węzła pomiarowego A", ha="center", va="bottom", fontsize=8.4,
        fontweight="bold", color=C_SIG, zorder=6)
wire([(2.40, 2.75), (2.40, 2.45)], C_GND, 1.6)
res_v(2.40, 2.15, "100 kΩ", h=0.6, side="right")
wire([(2.40, 1.85), (2.40, 1.72)], C_GND, 1.6)
gnd(2.40, 1.72)

# ═══════════ NOZKA 3 — prog ═══════════
wire([(6.85, 3.25), (6.85, 2.30), (10.75, 2.30)], C_INFO)
dot(9.40, 2.30, C_INFO)
wire([(9.40, 2.30), (9.40, 2.92)], C_5V, 1.5)
res_v(9.40, 3.27, "100 kΩ", h=0.7)
wire([(9.40, 3.62), (9.40, 4.34)], C_5V, 1.5)
plus5(9.40, 4.39)
wire([(10.75, 2.30), (10.75, 2.10)], C_GND, 1.5)
res_v(10.75, 1.80, "10 kΩ", h=0.6)
wire([(10.75, 1.50), (10.75, 1.38)], C_GND, 1.5)
gnd(10.75, 1.38)

# ═══════════ NOZKA 4 — masa ═══════════
wire([(7.55, 3.25), (7.55, 3.00), (8.55, 3.00), (8.55, 2.72)], C_GND, 2.0)
gnd(8.55, 2.72)

# ═══════════ NOZKA 8 — zasilanie ═══════════
wire([(5.45, 5.75), (4.55, 5.75), (4.55, 6.20)], C_5V, 2.0)
plus5(4.55, 6.25)

# ═══════════ NOZKA 7 — wolna ═══════════
wire([(6.15, 5.75), (6.15, 5.95)], C_MUT, 1.6)
ax.add_patch(Circle((6.15, 6.03), 0.07, fc="white", ec=C_MUT, lw=1.6, zorder=6))
ax.text(6.15, 6.18, "wolna", ha="center", va="bottom", fontsize=8.4, color=C_MUT,
        fontweight="bold", zorder=6)

# ═══════════ NOZKA 6 — do masy ═══════════
wire([(6.85, 5.75), (6.85, 6.48), (9.60, 6.48), (9.60, 5.70)], C_GND, 2.0)
gnd(9.60, 5.70)

# ═══════════ NOZKA 5 — urwana ═══════════
wire([(7.55, 5.75), (7.55, 5.92)], C_MUT, 1.6)
ax.plot([7.40, 7.70], [5.98, 6.14], color="#B00020", lw=2.4, zorder=6)
ax.plot([7.40, 7.70], [6.14, 5.98], color="#B00020", lw=2.4, zorder=6)
ax.text(7.86, 6.06, "urwana — bez połączenia", ha="left", va="center", fontsize=8.4,
        color="#B00020", fontweight="bold", zorder=6)

# ═══════════ KONDENSATOR ODSPRZEGAJACY ═══════════
wire([(0.95, 3.56), (0.95, 3.32)], C_5V, 1.6)
plus5(0.95, 3.61)
cap_v(0.95, 3.32, "100 nF")
gnd(0.95, 2.86)
ax.text(1.15, 2.48, "na płytce, przy przewodach\nzasilających komparator —\n20 cm drutu nie robi różnicy",
        ha="center", va="top", fontsize=7.6, color="#666", zorder=6, linespacing=1.45)

# ═══════════ NOTATKA ═══════════
ax.add_patch(FancyBboxPatch((0.35, 0.10), W-0.7, 0.62, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc="#FEF3C7", ec="#D97706", lw=1.1, zorder=1))
ax.text(0.55, 0.55, "NÓŻKA 5 (wejście nieodwracające nieużywanej połówki) urwała się przy montażu. Wejścia tego układu są na tranzystorach PNP — prąd polaryzacji WYPŁYWA z nóżki, więc urwane wejście samo odpływa do góry.",
        fontsize=7.8, color="#7A5800", zorder=2)
ax.text(0.55, 0.28, "Dlatego nóżkę 6 podano na MASĘ (pierwotnie miała iść na +5 V): różnica między wejściami zostaje zachowana, nieużywana połówka siedzi w stanie ustalonym i nie drga. Jej wyjście (7) jest zamknięte, więc zostaje wolne.",
        fontsize=7.8, color="#7A5800", zorder=2)

plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_detal_komparatora.pdf",
            bbox_inches="tight", facecolor="white")
plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_detal_komparatora.png", dpi=150,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: detal komparatora zapisany (PDF + PNG)")
