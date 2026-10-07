# -*- coding: utf-8 -*-
"""Symulator pojazdu EV — schemat v8: WSZYSTKO W JEDNEJ PUSZCE, bez stanu D, wartosci z zapasu.
Zabezpieczenia pracuja szeregowo poza puszka (rozdzielnica biurkowa + ladowarka),
w puszce: elektronika pojazdu, pomiary, wyswietlacze, przelot mocy 3x32 A.
Zapis: PDF (wektor, do czytania i powiekszania) + PNG (do wklejenia w dokument)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\symulator_pojazdu"

C_SIG = "#B45309"
C_DIG = "#15803D"
C_GND = "#111111"
C_5V = "#B00020"
C_MOC = "#7C2D12"
C_BOX = "#F4F4F2"
C_EDGE = "#333333"
C_INFO = "#0369A1"
C_MUT = "#888888"
C_ISTN = "#1D4ED8"

W, H = 28.0, 38.0
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def box(x0, y0, x1, y1, title, sub=None, fc=C_BOX, tfs=9.0, tdy=0.34, dashed=False,
        ec=C_EDGE, lw=1.5, tcol="#222", sfs=6.3):
    ls = (0, (4, 3)) if dashed else "solid"
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0,
                 boxstyle="round,pad=0.03,rounding_size=0.1", fc=fc, ec=ec, lw=lw,
                 linestyle=ls, zorder=1))
    ax.text((x0+x1)/2, y1-tdy, title, ha="center", va="center", fontsize=tfs,
            fontweight="bold", color=tcol, zorder=2)
    if sub:
        ax.text((x0+x1)/2, y1-tdy-0.30, sub, ha="center", va="top", fontsize=sfs,
                color="#555", zorder=2, linespacing=1.35)


def wire(pts, color=C_SIG, lw=1.9):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
            solid_capstyle="round", zorder=3)


def dot(x, y, color=C_SIG):
    ax.add_patch(Circle((x, y), 0.06, fc=color, ec=color, zorder=6))


def pinc(x, y, color="#222"):
    ax.add_patch(Circle((x, y), 0.055, fc="white", ec=color, lw=1.4, zorder=6))


def res_h(xc, yc, label, fs=6.4, lab_dy=0.26):
    ax.add_patch(Rectangle((xc-0.40, yc-0.12), 0.80, 0.24, fc="white", ec="#222", lw=1.4, zorder=5))
    ax.text(xc, yc+lab_dy, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def res_v(xc, yc, label, h=0.6, fs=6.2, side="right"):
    ax.add_patch(Rectangle((xc-0.12, yc-h/2), 0.24, h, fc="white", ec="#222", lw=1.4, zorder=5))
    if label:
        dx = 0.19 if side == "right" else -0.19
        ha = "left" if side == "right" else "right"
        ax.text(xc+dx, yc, label, ha=ha, va="center", fontsize=fs, color="#222",
                fontweight="bold", zorder=6)


def gnd(x, y):
    wire([(x, y), (x, y-0.08)], C_GND, 1.6)
    for i, w in enumerate([0.15, 0.10, 0.05]):
        ax.plot([x-w, x+w], [y-0.10-i*0.055, y-0.10-i*0.055], color=C_GND, lw=1.8, zorder=4)


def cap_v(xc, y_top, label, side="right", fs=6.2):
    wire([(xc, y_top), (xc, y_top-0.26)], C_GND, 1.4)
    ax.plot([xc-0.16, xc+0.16], [y_top-0.26, y_top-0.26], color="#222", lw=2.4, zorder=5)
    ax.plot([xc-0.16, xc+0.16], [y_top-0.38, y_top-0.38], color="#222", lw=2.4, zorder=5)
    wire([(xc, y_top-0.38), (xc, y_top-0.52)], C_GND, 1.4)
    gnd(xc, y_top-0.52)
    dx = 0.23 if side == "right" else -0.23
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, y_top-0.32, label, ha=ha, va="center", fontsize=fs, color="#222",
            fontweight="bold", zorder=6)


def dioda_v(xc, yc, kierunek="gora"):
    if kierunek == "gora":
        ax.add_patch(Polygon([(xc-0.12, yc-0.11), (xc+0.12, yc-0.11), (xc, yc+0.09)],
                     fc="white", ec="#222", lw=1.3, zorder=5))
        ax.plot([xc-0.12, xc+0.12], [yc+0.11, yc+0.11], color="#222", lw=1.8, zorder=5)
    else:
        ax.add_patch(Polygon([(xc-0.12, yc+0.11), (xc+0.12, yc+0.11), (xc, yc-0.09)],
                     fc="white", ec="#222", lw=1.3, zorder=5))
        ax.plot([xc-0.12, xc+0.12], [yc-0.11, yc-0.11], color="#222", lw=1.8, zorder=5)


def dioda_h(xc, yc, label="", fs=6.0, lab_dy=-0.34):
    ax.add_patch(Polygon([(xc-0.11, yc-0.13), (xc-0.11, yc+0.13), (xc+0.09, yc)],
                 fc="white", ec="#222", lw=1.3, zorder=5))
    ax.plot([xc+0.11, xc+0.11], [yc-0.13, yc+0.13], color="#222", lw=1.8, zorder=5)
    if label:
        ax.text(xc, yc+lab_dy, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def klamra(x, y):
    dot(x, y)
    wire([(x, y), (x, y+0.18)], C_5V, 1.3)
    dioda_v(x, y+0.30, "gora")
    wire([(x, y+0.42), (x, y+0.56)], C_5V, 1.3)
    ax.text(x, y+0.66, "+5V", ha="center", fontsize=5.4, color=C_5V, fontweight="bold", zorder=6)
    wire([(x, y), (x, y-0.18)], C_GND, 1.3)
    dioda_v(x, y-0.30, "gora")
    wire([(x, y-0.42), (x, y-0.50)], C_GND, 1.3)
    gnd(x, y-0.50)


def sw_h(xc, yc):
    dl, dr = xc-0.26, xc+0.26
    ax.add_patch(Circle((dl, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.add_patch(Circle((dr, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.plot([dl+0.04, dr-0.02], [yc+0.02, yc+0.28], color="#222", lw=1.6, zorder=5)


def sw_h_nc(xc, yc):
    dl, dr = xc-0.26, xc+0.26
    ax.add_patch(Circle((dl, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.add_patch(Circle((dr, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.plot([dl+0.04, dr+0.06], [yc+0.02, yc+0.06], color="#222", lw=1.6, zorder=5)
    ax.plot([dr+0.06, dr+0.06], [yc+0.06, yc+0.20], color="#222", lw=1.6, zorder=5)


def sw_v(xc, yc):
    dg, dd = yc+0.26, yc-0.26
    ax.add_patch(Circle((xc, dg), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.add_patch(Circle((xc, dd), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.plot([xc+0.02, xc+0.28], [dg-0.04, dd+0.02], color="#222", lw=1.6, zorder=5)


def przek_v(xc, yc):
    sw_v(xc, yc)
    ax.add_patch(Rectangle((xc-0.32, yc-0.40), 0.86, 0.80, fill=False, ec=C_DIG, lw=0.9,
                 linestyle=(0, (2, 2)), zorder=4))


def przek_h(xc, yc, nc=False):
    (sw_h_nc if nc else sw_h)(xc, yc)
    ax.add_patch(Rectangle((xc-0.40, yc-0.30), 0.86, 0.72, fill=False, ec=C_DIG, lw=0.9,
                 linestyle=(0, (2, 2)), zorder=4))


def ct_ring(xc, yc):
    ax.add_patch(Circle((xc, yc), 0.22, fill=False, ec=C_INFO, lw=2.0, zorder=6))


# ═══════════ TYTUL I LEGENDA ═══════════
ax.text(W/2, 37.2, "Symulator pojazdu EV — SCHEMAT v8: WSZYSTKO W JEDNEJ PUSZCE",
        ha="center", fontsize=15.5, fontweight="bold")
ax.text(W/2, 36.68, "wersja 8: bez stanu D (wentylacja) — badane ładowarki go nie obsługują  •  wszystkie rezystory z posiadanego zapasu  •  rozdzielnica biurkowa NIE jest przerabiana",
        ha="center", fontsize=8.4, color="#444")
ax.add_patch(FancyBboxPatch((0.4, 35.2), W-0.8, 1.05, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#EEF6FB", ec=C_INFO, lw=1.1, zorder=1))
ax.text(0.7, 35.95, "LEGENDA: pomarańczowy = sygnały CP/PP • zielony = cyfrowe/sterowanie • ciemnobrązowy gruby = tor mocy • czarny = PE (= masa elektroniki) • czerwony = +5 V • NIEBIESKI OPIS = element już w puszce",
        fontsize=7.0, color="#0C4A6E")
ax.text(0.7, 35.55, "kropka = połączenie, skrzyżowanie bez kropki = brak połączenia • styk w zielonej przerywanej ramce = styk przekaźnika sterowanego przez mikrokontroler • rezystory pojazdu wg IEC 61851-1 Tab. A.2",
        fontsize=7.0, color="#0C4A6E")

# ═══════════ POZA PUSZKA ═══════════
box(0.5, 27.4, 4.8, 34.3, "ROZDZIELNICA BIURKOWA", "(istniejąca, z własnymi\nzabezpieczeniami — POZA puszką)",
    tfs=7.4, tdy=0.34, dashed=True, fc="#FAFAF9", sfs=6.0)
for i, t in enumerate(["• wyłącznik główny — odcięcie",
                       "   w zasięgu ręki operatora",
                       "• zabezpieczenia 32 A — ISTNIEJĄCE,",
                       "   rozdzielnica NIE jest przerabiana",
                       "• przekrój żył w puszce musi im",
                       "   odpowiadać → 6 mm²",
                       "• do sprawdzenia: jeśli różnicówka",
                       "   tutaj ma 30 mA, przy badaniu",
                       "   różnicówki ładowarki może",
                       "   zadziałać pierwsza"]):
    ax.text(0.72, 32.75-i*0.44, t, fontsize=5.9, color="#333", zorder=2)

box(0.5, 22.4, 4.8, 26.6, "ŁADOWARKA BADANA", "(urządzenie badane)", tfs=7.4, tdy=0.34,
    dashed=True, fc="#FAFAF9", sfs=6.0)
for i, t in enumerate(["• własna różnicówka 30 mA",
                       "   + detekcja 6 mA DC",
                       "• własny wyłącznik mocy (stycznik)",
                       "• generator CP ±12 V / 1 kHz",
                       "   przez rezystor 1 kΩ"]):
    ax.text(0.72, 25.25-i*0.44, t, fontsize=5.9, color="#333", zorder=2)
wire([(2.65, 27.4), (2.65, 26.6)], C_MOC, 2.4)
ax.text(2.82, 26.95, "zasilanie", fontsize=5.8, color=C_MOC, zorder=6)
wire([(4.8, 24.0), (6.15, 24.0)], C_MOC, 2.4)
ax.text(5.45, 24.2, "kabel\nType 2", ha="center", fontsize=5.8, color=C_MOC, zorder=6, va="bottom")

# ═══════════ RAMA PUSZKI ═══════════
ax.add_patch(FancyBboxPatch((5.3, 2.4), 22.4, 32.4, boxstyle="round,pad=0.03,rounding_size=0.15",
             fc="#FDFDFC", ec="#111111", lw=2.6, zorder=0))
ax.text(16.5, 34.4, "PUSZKA SYMULATORA — istniejąca obudowa IP65 (≈200×300×120 mm)",
        ha="center", fontsize=10.5, fontweight="bold", color="#111", zorder=2)

# ═══════════ WLOT TYPE 2 ═══════════
ax.add_patch(FancyBboxPatch((6.15, 4.6), 2.2, 28.0, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc=C_BOX, ec=C_ISTN, lw=1.8, zorder=1))
ax.text(7.25, 32.1, "Wlot Type 2", ha="center", fontsize=8.0, fontweight="bold", color=C_ISTN, zorder=2)
ax.text(7.25, 31.4, "ISTNIEJĄCY\n(zamontowany\ni okablowany)", ha="center", va="top",
        fontsize=6.2, color=C_ISTN, zorder=2, linespacing=1.35)
Y_CP, Y_PP, Y_PE = 28.6, 26.0, 23.6
Y_L1, Y_L2, Y_L3, Y_N = 11.2, 10.2, 9.2, 8.2
Y_BUS = 17.4
for nazwa, yy, kol in [("CP", Y_CP, C_SIG), ("PP", Y_PP, C_SIG), ("PE", Y_PE, C_GND),
                       ("L1", Y_L1, C_MOC), ("L2", Y_L2, C_MOC), ("L3", Y_L3, C_MOC), ("N", Y_N, C_MOC)]:
    ax.text(8.12, yy, nazwa, ha="right", va="center", fontsize=7.2, fontweight="bold", color=kol, zorder=6)
    pinc(8.35, yy, kol)

# ═══════════ RDZEN STANOW CP ═══════════
wire([(8.35, Y_CP), (10.0, Y_CP)])
dot(8.8, Y_CP)
dot(9.3, Y_CP)
przek_h(10.4, Y_CP, nc=True)
ax.text(9.9, 29.35, "KF2 — styk NC:\nprzerwa CP („zanik pojazdu”)", ha="center",
        fontsize=5.6, color="#444", zorder=6, va="bottom", linespacing=1.3)
wire([(10.8, Y_CP), (11.5, Y_CP)])
dot(11.5, Y_CP)
wire([(11.5, Y_CP), (11.99, Y_CP)])
dioda_h(12.1, Y_CP, "1N4148")
wire([(12.21, Y_CP), (13.2, Y_CP)])
dot(12.7, Y_CP)
wire([(11.5, Y_CP), (11.5, 30.3)], C_SIG, 1.4)
wire([(12.7, Y_CP), (12.7, 30.3)], C_SIG, 1.4)
wire([(11.5, 30.3), (11.84, 30.3)], C_SIG, 1.4)
przek_h(12.1, 30.3)
wire([(12.36, 30.3), (12.7, 30.3)], C_SIG, 1.4)
ax.text(12.1, 31.2, "KF1: ZWARCIE DIODY (usterka testowa — ładowarka musi wykryć i odmówić)",
        ha="center", fontsize=5.6, color="#444", zorder=6)
wire([(13.2, Y_CP), (15.5, Y_CP)])
# KF3
wire([(9.3, Y_CP), (9.3, 27.4)], C_SIG, 1.4)
przek_v(9.3, 27.0)
wire([(9.3, 26.6), (9.3, Y_BUS)], C_SIG, 1.4)
dot(9.3, Y_BUS, C_GND)
ax.text(9.62, 25.6, "KF3: zwarcie CP–PE (stan E)", ha="left", fontsize=5.6, color="#444", zorder=6)
# galezie stanow
for xg, przek, rez in [(14.0, False, "2742 Ω\n(2,2k+510+22+10)"), (15.5, True, "1302 Ω\n(1k+270+22+10)")]:
    dot(xg, Y_CP)
    if przek:
        wire([(xg, Y_CP), (xg, 28.4)], C_SIG, 1.6)
        przek_v(xg, 28.0)
        wire([(xg, 27.6), (xg, 27.0)], C_SIG, 1.6)
    else:
        wire([(xg, Y_CP), (xg, 27.0)], C_SIG, 1.6)
    res_v(xg, 26.6, rez, h=0.8, fs=5.4, side="left")
    wire([(xg, 26.2), (xg, Y_BUS)], C_SIG, 1.6)
    dot(xg, Y_BUS, C_GND)
# legenda galezi
ax.add_patch(FancyBboxPatch((13.3, 28.78), 5.4, 2.30, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#E8F4FD", ec=C_INFO, lw=1.0, zorder=1))
ax.text(13.5, 30.80, "GAŁĘZIE STANÓW (wg IEC 61851-1):", fontsize=6.2, fontweight="bold", color=C_INFO, zorder=2)
for i, t in enumerate(["2,7 kΩ — BEZ STYKU, na stałe: stan B powstaje",
                       "   sam z chwilą wpięcia wtyku, jak w aucie",
                       "1,3 kΩ przez K2 = S2 pojazdu → stan C",
                       "BRAK STANU D (ładowanie z wentylacją) — nasze",
                       "   ładowarki go nie obsługują, gałąź 270 Ω usunięta",
                       "sumy: 2742 Ω i 1302 Ω — błąd 2 Ω wobec normy"]):
    ax.text(13.5, 30.44-i*0.30, t, fontsize=5.5, color="#0C4A6E", zorder=2)

box(19.4, 30.4, 22.6, 32.8, "Przekaźniki K2, KF1–KF3",
    "4 przekaźniki sygnałowe 5 V;\ncewki przez ULN2003 (posiadany)\n← piny D7, D9–D11", tfs=7.0, tdy=0.34, sfs=6.0)
wire([(22.6, 31.6), (23.0, 31.6)], C_DIG, 1.5)
box(19.4, 27.4, 22.6, 29.6, "E-STOP (grzybek)",
    "styk NC w zasilaniu cewek: wciśnięcie\n= S2 otwarte sprzętowo → ładowarka\nodcina napięcie w ≤100 ms", tfs=7.0, tdy=0.34, sfs=6.0)
wire([(21.0, 30.4), (21.0, 29.6)], C_5V, 1.5)
ax.text(21.15, 29.95, "+5 V cewek", fontsize=5.6, color=C_5V, zorder=6)

# ═══════════ POMIAR CP ═══════════
wire([(8.8, Y_CP), (8.8, 22.6), (9.4, 22.6)])
dot(8.8, 22.6)
res_h(9.85, 22.6, "220 kΩ")
wire([(10.25, 22.6), (10.65, 22.6)])
res_h(11.05, 22.6, "20 kΩ (2×10k)")
wire([(11.45, 22.6), (14.3, 22.6)])
dot(11.9, 22.6)
ax.text(11.9, 22.84, "A", ha="center", fontsize=6.0, color=C_MUT, fontweight="bold", zorder=6)
wire([(11.9, 22.6), (11.9, 22.75)], C_5V, 1.3)
res_v(11.9, 23.08, "100 kΩ", h=0.55)
wire([(11.9, 23.36), (11.9, 23.5)], C_5V, 1.3)
ax.text(11.9, 23.62, "+5V", ha="center", fontsize=5.4, color=C_5V, fontweight="bold", zorder=6)
wire([(11.9, 22.6), (11.9, 22.45)], C_GND, 1.3)
res_v(11.9, 22.12, "120 kΩ\n(100k+2×10k)", h=0.55)
wire([(11.9, 21.84), (11.9, 21.7)], C_GND, 1.3)
gnd(11.9, 21.7)
klamra(13.1, 22.6)
dot(13.9, 22.6)
res_h(14.75, 22.6, "10 kΩ")
wire([(15.15, 22.6), (23.0, 22.6)])
dot(15.9, 22.6); cap_v(15.9, 22.6, "470 pF")
ax.text(15.9, 22.84, "A′", ha="center", fontsize=6.0, color=C_MUT, fontweight="bold", zorder=6)
ax.text(9.05, 21.35, "U(A) = 1,82 V + 0,152·U(CP) — sieć pomiarowa jak w rejestratorze Q11",
        fontsize=6.0, color=C_INFO, zorder=6)
# komparator
wire([(13.9, 22.6), (13.9, 22.0)])
res_v(13.9, 21.7, "100 kΩ", h=0.55)
wire([(13.9, 21.42), (13.9, 20.8), (17.1, 20.8)])
dot(13.9, 20.8)
ax.text(13.66, 20.98, "B", ha="right", fontsize=6.0, color=C_MUT, fontweight="bold", zorder=6)
wire([(13.9, 20.8), (13.9, 20.6)], C_GND, 1.3)
res_v(13.9, 20.35, "", h=0.45)
wire([(13.9, 20.12), (13.9, Y_BUS)], C_GND, 1.3)
dot(13.9, Y_BUS, C_GND)
ax.text(14.1, 20.35, "100 kΩ", fontsize=6.0, color="#222", fontweight="bold", zorder=6, va="center")
ax.add_patch(FancyBboxPatch((17.1, 19.2), 2.9, 2.4, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc=C_BOX, ec=C_EDGE, lw=1.5, zorder=1))
ax.text(18.55, 21.32, "LM393", ha="center", fontsize=7.4, fontweight="bold", color="#222", zorder=2)
ax.text(18.55, 21.02, "8 → +5 V  ·  4 → masa  ·  100 nF między 8 i 4", ha="center", fontsize=5.0, color="#555", zorder=2)
ax.text(18.55, 20.80, "5 urwana  ·  6 → masa  ·  7 wolna", ha="center", fontsize=5.0, color="#555", zorder=2)
ax.text(17.25, 20.45, "2  IN−", fontsize=6.2, va="center", color="#222", zorder=2)
ax.text(17.25, 19.8, "3  IN+", fontsize=6.2, va="center", color="#222", zorder=2)
ax.text(19.85, 20.2, "OUT  1", fontsize=6.2, va="center", ha="right", color="#222", zorder=2)
wire([(16.4, 19.8), (17.1, 19.8)], C_INFO, 1.4)
dot(16.4, 19.8, C_INFO)
wire([(16.4, 19.8), (16.4, 20.05)], C_5V, 1.3)
res_v(16.4, 20.3, "100 kΩ", h=0.45, side="left")
wire([(16.4, 20.53), (16.4, 20.65)], C_5V, 1.3)
ax.text(16.4, 20.77, "+5V", ha="center", fontsize=5.2, color=C_5V, fontweight="bold", zorder=6)
dot(16.4, 19.8, C_INFO)
wire([(16.4, 19.8), (15.9, 19.8)], C_INFO, 1.4)
wire([(15.9, 19.8), (15.9, 19.6)], C_GND, 1.3)
res_v(15.9, 19.35, "10 kΩ", h=0.45, side="left")
wire([(15.9, 19.12), (15.9, 19.0)], C_GND, 1.3)
gnd(15.9, 19.0)
# sprzezenie zwrotne -> histereza
wire([(21.3, 20.2), (21.3, 18.95), (19.62, 18.95)], C_MUT, 1.3)
res_h(19.2, 18.95, "470 kΩ — histereza", fs=5.6, lab_dy=-0.3)
wire([(18.8, 18.95), (16.4, 18.95), (16.4, 19.8)], C_MUT, 1.3)
dot(21.3, 20.2, C_DIG)
ax.text(18.55, 19.55, "próg 0,455 V ≈ CP = −6 V", fontsize=5.6, color=C_INFO, ha="center", zorder=6)
wire([(20.0, 20.2), (23.0, 20.2)], C_DIG, 1.8)
dot(20.9, 20.2, C_DIG)
wire([(20.9, 20.2), (20.9, 20.45)], C_5V, 1.3)
res_v(20.9, 20.7, "10 kΩ", h=0.45)
wire([(20.9, 20.93), (20.9, 21.05)], C_5V, 1.3)
ax.text(20.9, 21.17, "+5V", ha="center", fontsize=5.2, color=C_5V, fontweight="bold", zorder=6)

# ═══════════ PE ═══════════
wire([(8.35, Y_PE), (8.6, Y_PE)], C_GND, 2.0)
dot(8.6, Y_PE, C_GND)
wire([(8.6, Y_PE), (8.6, Y_BUS), (23.0, Y_BUS)], C_GND, 2.0)
ax.text(10.2, 17.68, "szyna PE = masa elektroniki (sygnały CP/PP odniesione do PE — jak w pojeździe)",
        fontsize=6.0, color=C_GND, fontweight="bold", zorder=6)
wire([(8.6, Y_BUS), (8.6, 2.9), (26.6, 2.9)], C_GND, 2.0)
ax.text(14.0, 2.62, "PE do obu gniazd wyjściowych — nigdzie nie przełączane, 6 mm²",
        fontsize=6.0, color=C_GND, zorder=6)

# ═══════════ PP ═══════════
wire([(8.35, Y_PP), (9.0, Y_PP), (9.0, 18.6), (23.0, 18.6)])
dot(12.0, 18.6)
wire([(12.0, 18.6), (12.0, 18.8)], C_5V, 1.3)
res_v(12.0, 19.05, "1 kΩ", h=0.45, side="left")
wire([(12.0, 19.28), (12.0, 19.4)], C_5V, 1.3)
ax.text(12.0, 19.52, "+5V", ha="center", fontsize=5.2, color=C_5V, fontweight="bold", zorder=6)
ax.text(17.4, 18.25, "PP: pomiar i WALIDACJA kodowania kabla\n(rezystor kodujący jest we wtyku kabla — Tab. B.3)",
        fontsize=5.8, color=C_INFO, zorder=6, va="top", linespacing=1.35)

# ═══════════ DETEKTOR SZCZYTU + MIERNIK CP ═══════════
wire([(8.8, 22.6), (8.8, 15.6), (9.45, 15.6)])
res_h(9.85, 15.6, "2,2 kΩ")
wire([(10.25, 15.6), (10.39, 15.6)])
dioda_h(10.5, 15.6, "BAT85", lab_dy=0.52)
wire([(10.61, 15.6), (11.3, 15.6)])
dot(11.3, 15.6); cap_v(11.3, 15.6, "100 nF", side="left")
wire([(11.3, 15.6), (11.9, 15.6)])
box(11.9, 14.6, 16.1, 16.6, "Miernik „CP: V DC”",
    "ISTNIEJĄCY — dostaje detektor szczytu:\npokaże 12 / 9 / 6 / 3 V zamiast\nwartości średniej z przebiegu PWM",
    tfs=7.2, tdy=0.34, ec=C_ISTN, lw=1.8, tcol=C_ISTN, sfs=6.0)
box(16.7, 14.6, 21.6, 16.6, "Wyświetlacz tekstowy 16×2",
    "NOWY — w oknie po mierniku „PP: OHM”\n(okno ≈71×39 mm, potrzebne 71×24 mm:\nwchodzi bez przerabiania panelu)",
    tfs=7.2, tdy=0.34, sfs=6.0)
wire([(21.6, 15.9), (23.0, 15.9)], C_DIG, 1.5)
wire([(21.6, 15.3), (23.0, 15.3)], C_DIG, 1.5)

# ═══════════ POMIAR TORU MOCY ═══════════
box(15.4, 12.4, 21.6, 14.2, "Pomiar toru mocy (płytka sterownika)",
    "3× przekładnik prądowy: obciążnik + polaryzacja 2,5 V (2×10 kΩ) → A3/A6/A7\n3× izolowany detektor obecności fazy: transoptor + (220 kΩ + 100 kΩ) szeregowo → D2/D3/D4",
    tfs=7.0, tdy=0.34, sfs=6.0)
wire([(21.6, 13.4), (23.0, 13.4)], C_SIG, 1.5)
wire([(21.6, 12.8), (23.0, 12.8)], C_DIG, 1.5)

# ═══════════ TOR MOCY ═══════════
box(9.6, 7.6, 11.4, 11.8, "Listwa\nzaciskowa\n6 mm²", tfs=6.8, tdy=0.42)
for yy in [Y_L1, Y_L2, Y_L3, Y_N]:
    wire([(8.35, yy), (9.6, yy)], C_MOC, 2.6)
    wire([(11.4, yy), (24.3, yy)], C_MOC, 2.6)
ax.text(8.95, 11.45, "5×6 mm²", fontsize=5.6, color=C_MOC, zorder=6)
for yy in [Y_L1, Y_L2, Y_L3]:
    ct_ring(12.6, yy)
wire([(12.6, Y_L1), (12.6, 12.9), (15.4, 12.9)], C_INFO, 1.4)
ax.text(12.95, 12.52, "3× przekładnik prądowy", ha="left", fontsize=5.8, color=C_INFO,
        fontweight="bold", zorder=6)
for i, yl in enumerate([Y_L1, Y_L2, Y_L3, Y_N]):
    xq = 16.2 + i*0.3
    dot(xq, yl, C_MOC)
    wire([(xq, yl), (xq, 12.4)], C_MOC, 1.1)
for xg, yl, lab in [(14.6, Y_L1, "L1"), (17.9, Y_L2, "L2"), (21.2, Y_L3, "L3")]:
    box(xg-1.45, 5.4, xg+1.45, 7.7, "Miernik V/A — " + lab,
        "ISTNIEJĄCY\npodgląd niezależny\nod elektroniki", tfs=6.8, tdy=0.34,
        ec=C_ISTN, lw=1.6, tcol=C_ISTN, sfs=5.8)
    dot(xg-0.5, yl, C_MOC)
    wire([(xg-0.5, yl), (xg-0.5, 7.7)], C_MOC, 1.1)
    dot(xg+0.5, Y_N, C_MOC)
    wire([(xg+0.5, Y_N), (xg+0.5, 7.7)], C_MOC, 1.1)
box(24.3, 7.2, 27.4, 11.6, "Gniazdo CEE 32 A, 5P",
    "NOWE — wyjście mocy 22 kW:\nmagazyn energii ze swoją ładowarką\n(jak ładowarka pokładowa w aucie)\nalbo obciążenie próbne", tfs=7.4, tdy=0.34, sfs=6.0)
box(24.3, 3.9, 27.4, 6.8, "Gniazdo 230 V",
    "ISTNIEJĄCE — szybkie\npróby 1-fazowe (L1 + N)", tfs=7.2, tdy=0.34,
    ec=C_ISTN, lw=1.6, tcol=C_ISTN, sfs=6.0)
dot(23.6, Y_L1, C_MOC)
wire([(23.6, Y_L1), (23.6, 5.9), (24.3, 5.9)], C_MOC, 1.6)
dot(23.9, Y_N, C_MOC)
wire([(23.9, Y_N), (23.9, 5.0), (24.3, 5.0)], C_MOC, 1.6)
dot(24.9, 2.9, C_GND); wire([(24.9, 2.9), (24.9, 3.9)], C_GND, 1.8)
dot(26.6, 2.9, C_GND); wire([(26.6, 2.9), (26.6, 7.2)], C_GND, 1.8)

# ═══════════ MIKROKONTROLER ═══════════
box(23.0, 11.9, 27.5, 34.0, "Mikrokontroler (Arduino Nano)",
    "maszyna decyzyjna pojazdu + tester czasów ładowarki", tfs=9.0, tdy=0.36, sfs=6.4)
piny = [("D7", 31.6, "K2 (S2 pojazdu); D9–D11: KF1–KF3", C_DIG),
        ("A1", 22.6, "poziomy CP (węzeł A′)", C_SIG),
        ("D8", 20.2, "komparator → Timer1 (wypełnienie PWM)", C_DIG),
        ("A2", 18.6, "PP — kodowanie kabla", C_SIG),
        ("GND", Y_BUS, "masa = PE", C_GND),
        ("A4", 15.9, "SDA → wyświetlacz", C_DIG),
        ("A5", 15.3, "SCL → wyświetlacz", C_DIG),
        ("A3/A6/A7", 13.4, "prądy L1/L2/L3", C_SIG),
        ("D2/D3/D4", 12.8, "obecność faz L1/L2/L3", C_DIG)]
for nazwa, yy, opis, kol in piny:
    pinc(23.0, yy, kol)
    ax.text(23.18, yy, nazwa + " — " + opis, fontsize=6.1, va="center", color="#222",
            fontweight="bold", zorder=6)
ax.text(23.18, 32.9, "D5 — przycisk START/STOP (na panelu)", fontsize=6.0, color=C_MUT, zorder=6)
ax.text(23.18, 32.5, "D6 — brzęczyk alarmowy (głośny sygnał,", fontsize=6.0, color=C_MUT, zorder=6)
ax.text(23.18, 32.1, "      gdy ładowarka nie odcięła napięcia)", fontsize=6.0, color=C_MUT, zorder=6)
ax.text(23.18, 30.8, "CO ROBI:", fontsize=6.8, color="#222", fontweight="bold", zorder=6)
for i, t in enumerate(["• waliduje PP (Tab. B.3), wypełnienie PWM",
                       "   (Tab. A.6) i poziomy CP (okna ±1 V)",
                       "• zamyka S2 tylko gdy WSZYSTKO się zgadza;",
                       "   inaczej zostaje w stanie B i wyświetla",
                       "   POWÓD ODMOWY — jak prawdziwe auto",
                       "• w stanie C nadzoruje ciągle: naruszenie",
                       "   → otwarcie S2 w ≤3 s (norma t_ACoff2)",
                       "• mierzy ładowarce t_ACon (≤3 s) i t_ACoff1",
                       "   (≤100 ms) → werdykt PASS / FAIL",
                       "• pilnuje, czy pobór ≤ oferta z PWM"]):
    ax.text(23.18, 30.35-i*0.42, t, fontsize=6.0, color="#333", zorder=6)

# ═══════════ ZASILANIE ELEKTRONIKI ═══════════
box(8.8, 3.3, 14.4, 5.1, "Zasilanie elektroniki 5 V",
    "zasilacz USB z rozdzielnicy biurkowej — elektronika żyje\nniezależnie od ładowarki (odpowiednik instalacji 12 V\nw aucie); wyłącznik: ISTNIEJĄCY łącznik 16 A z panelu",
    tfs=7.2, tdy=0.34, sfs=6.0)
wire([(5.3, 4.2), (8.8, 4.2)], C_INFO, 1.6)
ax.text(5.45, 3.35, "cienki przewód zasilający\n(poza torem mocy)", fontsize=5.6, color=C_INFO,
        zorder=6, va="bottom", linespacing=1.3)

# ═══════════ NOTATKI ═══════════
ax.add_patch(FancyBboxPatch((0.4, 0.10), 27.2, 2.12, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#FEF3C7", ec="#D97706", lw=1.2, zorder=1))
naty = ["• OGRANICZENIE PRZYJĘTE ŚWIADOMIE: symulator nie ma własnego rozłącznika mocy. Jeśli badana ładowarka nie odetnie napięcia mimo zgłoszenia końca ładowania (czyli właśnie wtedy, gdy jest wadliwa),",
        "   urządzenie pokazuje błąd i włącza brzęczyk, a odcięcia dokonuje operator wyłącznikiem głównym w rozdzielnicy. Sesje prowadzi technik obecny przy stanowisku.",
        "• DLACZEGO BEZ ZABEZPIECZEŃ W PUSZCE: zabezpieczenie nadprądowe i różnicowoprądowe pracują szeregowo — w rozdzielnicy biurkowej i w samej badanej ładowarce. WARUNEK: przekrój żył w puszce",
        "   musi odpowiadać zabezpieczeniu w rozdzielnicy (32 A → 6 mm²). DO SPRAWDZENIA: jeśli różnicówka w rozdzielnicy ma 30 mA, przy badaniu różnicówki ładowarki może zadziałać pierwsza (brak selektywności).",
        "• BILANS CIEPLNY: 3×32 A na 6 mm², ok. 0,6 m drogi na fazę → 6,5 W w przewodach + ok. 1,8 W na zaciskach = ok. 8 W; powierzchnia obudowy 0,24 m² → przyrost 6–9 K ponad otoczenie. Krytyczne są STYKI: jeden luźny zacisk o rezystancji 5 mΩ to 5 W w jednym punkcie.",
        "• KIERUNEK BEZPIECZNY: brak zasilania elektroniki = wszystkie przekaźniki opadnięte = stan B = ładowarka nie podaje napięcia. Grzybek awaryjny działa sprzętowo, bez udziału programu."]
for i, t in enumerate(naty):
    ax.text(0.65, 1.90-i*0.31, t, fontsize=5.8, color="#7A5800", zorder=2)

plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_schemat_v8.pdf",
            bbox_inches="tight", facecolor="white")
plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_schemat_v8.png", dpi=110,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: schemat v8 zapisany (PDF + PNG)")
