# -*- coding: utf-8 -*-
"""Schemat polaczen ULN2003AN z Nano i czterema przekaznikami symulatora pojazdu.
Kazdy przekaznik narysowany jako calosc: cewka + styk + sprzezenie mechaniczne."""
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
C_MUT = "#999999"
C_BOX = "#F7F7F5"

W, H = 19.2, 12.8
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def wire(pts, color=C_GND, lw=1.9):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
            solid_capstyle="round", zorder=3)


def dot(x, y, color=C_GND):
    ax.add_patch(Circle((x, y), 0.06, fc=color, ec=color, zorder=6))


def cewka(xc, yc, h=0.80, w=0.34):
    """Cewka przekaznika: prostokat z ukosnikiem, zeby nie mylil sie z rezystorem."""
    ax.add_patch(Rectangle((xc-w/2, yc-h/2), w, h, fc="white", ec="#222", lw=1.8, zorder=5))
    ax.plot([xc-w/2, xc+w/2], [yc-h/2, yc+h/2], color="#222", lw=1.1, zorder=6)


def styk(xc, yc, uzyty, lab_g=None, lab_d=None):
    """Styk przelaczny. uzyty = 'gora' / 'dol' / 'obie' - uzyte pozycje na pomaranczowo."""
    xw, xf = xc, xc + 1.30
    yg, yd = yc + 0.30, yc - 0.30
    ax.add_patch(Circle((xw, yc), 0.055, fc="white", ec="#222", lw=1.5, zorder=6))
    ax.add_patch(Circle((xf, yg), 0.055, fc="white", ec="#222", lw=1.5, zorder=6))
    ax.add_patch(Circle((xf, yd), 0.055, fc="white", ec="#222", lw=1.5, zorder=6))
    wire([(xw+0.05, yc), (xf-0.06, yg)], "#222", 1.8)
    ug = uzyty in ("gora", "obie")
    ud = uzyty in ("dol", "obie")
    kol_g = C_SIG if ug else C_MUT
    kol_d = C_SIG if ud else C_MUT
    wire([(xf, yg), (xf+0.50, yg)], kol_g, 2.4 if ug else 1.2)
    wire([(xf, yd), (xf+0.50, yd)], kol_d, 2.4 if ud else 1.2)
    wire([(xw, yc), (xw-0.50, yc)], C_SIG, 2.4)
    ax.text(xf+0.58, yg, lab_g or "zwarty w spoczynku", ha="left", va="center", fontsize=6.8,
            color=kol_g, fontweight="bold" if ug else "normal", zorder=6)
    ax.text(xf+0.58, yd, lab_d or "rozwarty w spoczynku", ha="left", va="center", fontsize=6.8,
            color=kol_d, fontweight="bold" if ud else "normal", zorder=6)
    ax.text(xw-0.56, yc, "wspólny", ha="right", va="center", fontsize=6.8,
            color=C_SIG, fontweight="bold", zorder=6)


# ═══════════════ TYTUL ═══════════════
ax.text(W/2, 12.35, "ULN2003AN — schemat połączeń w symulatorze pojazdu",
        ha="center", fontsize=15.5, fontweight="bold")
ax.text(W/2, 12.02, "każdy przekaźnik: jeden koniec cewki na +5 V, drugi na wyjście swojego kanału • pomarańczowy styk = ten, który idzie w tor pilota",
        ha="center", fontsize=8.8, color="#555")

# ═══════════════ SZYNY ═══════════════
wire([(3.60, 11.00), (18.20, 11.00)], C_5V, 2.4)
wire([(18.20, 11.00), (18.20, 2.60)], C_5V, 2.4)
ax.text(3.55, 11.00, "+5 V", ha="right", va="center", fontsize=9.6,
        fontweight="bold", color=C_5V, zorder=6)
wire([(3.60, 2.10), (18.20, 2.10)], C_GND, 2.4)
ax.text(3.55, 2.10, "masa", ha="right", va="center", fontsize=9.6,
        fontweight="bold", color=C_GND, zorder=6)

# ═══════════════ NANO ═══════════════
ax.add_patch(FancyBboxPatch((0.90, 6.90), 2.30, 3.30, boxstyle="round,pad=0.02,rounding_size=0.08",
             fc=C_BOX, ec="#222", lw=1.8, zorder=1))
ax.text(2.05, 9.90, "Arduino Nano", ha="center", fontsize=10.0, fontweight="bold", zorder=2)

# ═══════════════ ULN ═══════════════
ux0, ux1 = 5.10, 8.10
ax.add_patch(FancyBboxPatch((ux0, 3.10), ux1-ux0, 7.00, boxstyle="round,pad=0.02,rounding_size=0.08",
             fc=C_BOX, ec="#222", lw=2.2, zorder=1))
ax.text((ux0+ux1)/2, 9.78, "ULN2003AN", ha="center", fontsize=11.5, fontweight="bold", zorder=2)
ax.add_patch(Circle(((ux0+ux1)/2, 10.10), 0.19, fc="white", ec="#222", lw=2.0, zorder=4))
ax.text((ux0+ux1)/2, 10.36, "wcięcie", ha="center", fontsize=7.0, color="#666", zorder=6)

YP = [9.72 - i*0.76 for i in range(8)]
for i, y in enumerate(YP):
    wire([(ux0-0.28, y), (ux0, y)], "#222", 1.6)
    ax.text(ux0+0.14, y, str(i+1), ha="left", va="center", fontsize=8.6,
            fontweight="bold", color="#222", zorder=6)
    wire([(ux1, y), (ux1+0.28, y)], "#222", 1.6)
    ax.text(ux1-0.14, y, str(16-i), ha="right", va="center", fontsize=8.6,
            fontweight="bold", color="#222", zorder=6)

# ═══════════════ NANO -> WEJSCIA ═══════════════
kanaly = [("D11", 0, "zwarcie pilota do ziemi",  "dol",  None, None),
          ("D10", 1, "gałąź ładowania (1302 Ω)", "dol",  None, None),
          ("D9",  2, "zwarcie diody pojazdu",    "obie",
           "przez diodę  (spoczynek)", "z pominięciem diody  (zasilona)"),
          ("D7",  3, "zanik pojazdu",            "gora", None, None)]

for nazwa, i, opis, uz, lg, ld in kanaly:
    y = YP[i]
    wire([(3.20, y), (ux0, y)], C_DIG, 1.9)
    ax.text(3.13, y, nazwa, ha="right", va="center", fontsize=9.0,
            fontweight="bold", color=C_DIG, zorder=6)
    ax.add_patch(Circle((3.20, y), 0.07, fc="white", ec=C_DIG, lw=1.5, zorder=6))

# ═══════════════ PRZEKAZNIKI ═══════════════
YR = [9.70, 7.70, 5.70, 3.70]
XV = [10.30, 10.00, 9.70, 9.40]

for (nazwa, i, opis, uz, lg, ld), yr, xv in zip(kanaly, YR, XV):
    y = YP[i]
    ax.add_patch(FancyBboxPatch((10.60, yr-0.85), 6.80, 1.75,
                 boxstyle="round,pad=0.02,rounding_size=0.06",
                 fc="#FCFCFB", ec=C_DIG, lw=1.3, linestyle=(0, (4, 3)), zorder=1))
    ax.text(10.75, yr+0.70, opis, fontsize=8.6, fontweight="bold", color=C_DIG, zorder=6)

    wire([(ux1+0.28, y), (xv, y), (xv, yr-0.25), (11.40, yr-0.25)], C_SIG, 1.9)
    cewka(11.40, yr+0.15)
    ax.text(11.62, yr+0.15, "cewka\n125 Ω", ha="left", va="center", fontsize=7.4,
            fontweight="bold", color="#222", zorder=6, linespacing=1.25)
    wire([(11.40, yr+0.55), (18.20, yr+0.55)], C_5V, 1.9)
    dot(18.20, yr+0.55, C_5V)

    ax.plot([11.58, 12.55], [yr+0.15, yr+0.15], color=C_MUT, lw=1.2,
            linestyle=(0, (2, 2)), zorder=4)
    ax.plot([12.55, 12.55], [yr+0.15, yr-0.40], color=C_MUT, lw=1.2,
            linestyle=(0, (2, 2)), zorder=4)

    styk(13.10, yr-0.45, uz, lg, ld)

# ═══════════════ NOZKA 8 I 9 ═══════════════
y8 = YP[7]
wire([(ux0, y8), (4.70, y8), (4.70, 2.10)], C_GND, 2.1)
dot(4.70, 2.10)
ax.text(4.82, 2.34, "nóżka 8 — wspólny emiter", ha="left", va="center",
        fontsize=7.8, fontweight="bold", color=C_GND, zorder=6)

wire([(ux1, y8), (9.00, y8), (9.00, 2.60), (18.20, 2.60)], C_5V, 2.1)
ax.text(9.15, 2.66, "nóżka 9 → +5 V  (wspólna katoda diod gaszących)",
        ha="left", va="bottom", fontsize=8.0, fontweight="bold", color=C_5V, zorder=6)

# ═══════════════ WOLNE KANALY ═══════════════
for i in (4, 5, 6):
    y = YP[i]
    ax.text(ux0-0.36, y, "wolne", ha="right", va="center", fontsize=7.6, color=C_MUT, zorder=6)
    ax.text(ux1+0.36, y, "wolne", ha="left", va="center", fontsize=7.6, color=C_MUT, zorder=6)

# ═══════════════ WSTAWKA: RZECZYWISTA ORIENTACJA KOSCI ═══════════════
ax.add_patch(FancyBboxPatch((0.45, 2.55), 3.95, 3.30, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc="#FFFDF5", ec="#D97706", lw=1.3, zorder=1))
ax.text(2.42, 5.68, "Tak leży kość naprawdę", ha="center", fontsize=9.2,
        fontweight="bold", color="#7A5800", zorder=6)
ax.text(2.42, 5.44, "wcięcie po LEWEJ, napis czytany normalnie", ha="center",
        fontsize=7.4, color="#7A5800", zorder=6)

ix0, ix1, iy0, iy1 = 0.85, 3.95, 3.75, 4.55
ax.add_patch(Rectangle((ix0, iy0), ix1-ix0, iy1-iy0, fc="#3A3A3A", ec="#222", lw=1.4, zorder=3))
ax.add_patch(Circle((ix0, (iy0+iy1)/2), 0.13, fc="#FFFDF5", ec="#222", lw=1.2, zorder=4))
ax.add_patch(Circle((ix1-0.26, (iy0+iy1)/2), 0.10, fc="#2A2A2A", ec="#555", lw=1.0, zorder=5))
ax.text((ix0+ix1)/2 + 0.05, (iy0+iy1)/2, "ULN2003AN", ha="center", va="center",
        fontsize=6.6, color="#DDD", zorder=5)
ax.annotate("wcięcie\n= tu jest nóżka 1", xy=(ix0+0.02, (iy0+iy1)/2), xytext=(0.58, 5.14),
            fontsize=6.8, color="#7A5800", fontweight="bold", ha="left", linespacing=1.3,
            arrowprops=dict(arrowstyle="->", color="#7A5800", lw=1.0), zorder=6)
ax.annotate("kółko = ślad z formy,\nnie oznacza niczego", xy=(ix1-0.26, (iy0+iy1)/2+0.10),
            xytext=(2.55, 5.14), fontsize=6.8, color="#888", ha="left", linespacing=1.3,
            arrowprops=dict(arrowstyle="->", color="#888", lw=1.0), zorder=6)

IX = [ix0 + 0.25 + k*0.38 for k in range(8)]
for k, x in enumerate(IX):
    ax.plot([x, x], [iy0, iy0-0.16], color="#888", lw=2.6, zorder=3)
    ax.text(x, iy0-0.36, str(k+1), ha="center", va="center", fontsize=7.6,
            fontweight="bold", color="#222", zorder=6)
    ax.plot([x, x], [iy1, iy1+0.16], color="#888", lw=2.6, zorder=3)
    ax.text(x, iy1+0.36, str(16-k), ha="center", va="center", fontsize=7.6,
            fontweight="bold", color="#222", zorder=6)

ax.text(2.42, 3.05, "dolny rząd od lewej:  1 2 3 4 5 6 7 8", ha="center",
        fontsize=7.6, fontweight="bold", color="#222", zorder=6)
ax.text(2.42, 2.80, "górny rząd od lewej:  16 15 14 13 12 11 10 9", ha="center",
        fontsize=7.6, fontweight="bold", color="#222", zorder=6)

# ═══════════════ TABELA ═══════════════
ax.add_patch(FancyBboxPatch((0.45, 0.22), 18.3, 1.42, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc="white", ec="#BBB", lw=1.2, zorder=0))
kol = [0.70, 4.40, 5.70, 7.10, 8.60]
for x, t in zip(kol, ["Przekaźnik", "Nano", "ULN wejście", "ULN wyjście", "Styk użyty w torze pilota"]):
    ax.text(x, 1.42, t, fontsize=8.4, fontweight="bold", color=C_INFO, zorder=6)
ax.plot([0.65, 18.55], [1.32, 1.32], color=C_INFO, lw=0.9, zorder=4)

wiersze = [
    ("zwarcie pilota do ziemi", "D11", "1", "16", "wspólny + rozwarty w spoczynku"),
    ("gałąź ładowania 1302 Ω",  "D10", "2", "15", "wspólny + rozwarty w spoczynku"),
    ("zwarcie diody pojazdu",   "D9",  "3", "14", "OBA styki stałe: górny = droga przez diodę, dolny = droga z pominięciem diody"),
    ("zanik pojazdu",           "D7",  "4", "13", "wspólny + ZWARTY w spoczynku — linia pilota ciągła bez zasilania"),
]
for j, w in enumerate(wiersze):
    yy = 1.12 - j*0.200
    for x, t in zip(kol, w):
        ax.text(x, yy, t, fontsize=8.0, color="#222", zorder=6)

ax.text(0.70, 0.33, "Wejścia 5, 6, 7 i wyjścia 10, 11, 12 zostają wolne — wejście bez sygnału jest ściągane do masy przez wewnętrzne 7,2 kΩ i 3 kΩ, więc kanał jest pewnie wyłączony.",
        fontsize=7.6, color="#7A5800", zorder=6)

plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_polaczenia_uln.pdf",
            bbox_inches="tight", facecolor="white")
plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_polaczenia_uln.png", dpi=150,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: polaczenia ULN zapisane (PDF + PNG)")
