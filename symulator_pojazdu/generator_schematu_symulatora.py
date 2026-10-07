# -*- coding: utf-8 -*-
"""Pelny schemat symulatora pojazdu EV — KONCEPCJA v2 (aktywna maszyna decyzyjna).
Tryb AUTO: MCU zamyka/otwiera S2 (przekaznik) wg walidacji PP/PWM/poziomow jak pojazd.
Tor mocy 3x32 A (22 kW) ze stycznikiem, CT, detektorami faz i pomiarem czasow stacji."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\symulator_pojazdu"

C_SIG = "#B45309"   # sygnaly CP/PP
C_DIG = "#15803D"   # cyfrowe / I2C / sterowanie
C_GND = "#111111"   # PE / masa
C_5V  = "#B00020"
C_MOC = "#7C2D12"   # tor mocy 230/400 V
C_BOX = "#F4F4F2"
C_EDGE = "#333333"
C_INFO = "#0369A1"
C_MUT = "#888888"
C_WARN = "#B00020"

W, H = 27.0, 37.5
fig, ax = plt.subplots(figsize=(W, H), dpi=110)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def box(x0, y0, x1, y1, title, sub=None, fc=C_BOX, tfs=9.5, tdy=0.32, dashed=False):
    ls = (0, (4, 3)) if dashed else "solid"
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0,
                 boxstyle="round,pad=0.03,rounding_size=0.1", fc=fc, ec=C_EDGE, lw=1.5,
                 linestyle=ls, zorder=1))
    ax.text((x0+x1)/2, y1-tdy, title, ha="center", va="center", fontsize=tfs, fontweight="bold", color="#222", zorder=2)
    if sub:
        ax.text((x0+x1)/2, y1-tdy-0.32, sub, ha="center", va="center", fontsize=6.6, color="#555", zorder=2)


def wire(pts, color=C_SIG, lw=1.9):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw, solid_capstyle="round", zorder=3)


def dot(x, y, color=C_SIG):
    ax.add_patch(Circle((x, y), 0.06, fc=color, ec=color, zorder=6))


def pinc(x, y, color="#222"):
    ax.add_patch(Circle((x, y), 0.055, fc="white", ec=color, lw=1.4, zorder=6))


def res_h(xc, yc, label, fs=6.8, lab_dy=0.26):
    ax.add_patch(Rectangle((xc-0.42, yc-0.12), 0.84, 0.24, fc="white", ec="#222", lw=1.4, zorder=5))
    ax.text(xc, yc+lab_dy, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def res_v(xc, yc, label, h=0.6, fs=6.6, side="right"):
    ax.add_patch(Rectangle((xc-0.12, yc-h/2), 0.24, h, fc="white", ec="#222", lw=1.4, zorder=5))
    dx = 0.2 if side == "right" else -0.2
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, yc, label, ha=ha, va="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def cap_v(xc, y_top, label, side="right", fs=6.6):
    wire([(xc, y_top), (xc, y_top-0.26)], C_GND, 1.4)
    ax.plot([xc-0.16, xc+0.16], [y_top-0.26, y_top-0.26], color="#222", lw=2.4, zorder=5)
    ax.plot([xc-0.16, xc+0.16], [y_top-0.38, y_top-0.38], color="#222", lw=2.4, zorder=5)
    wire([(xc, y_top-0.38), (xc, y_top-0.52)], C_GND, 1.4)
    gnd(xc, y_top-0.52)
    dx = 0.24 if side == "right" else -0.24
    ha = "left" if side == "right" else "right"
    ax.text(xc+dx, y_top-0.32, label, ha=ha, va="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


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
        ax.text(xc, yc-0.32, label, ha="center", fontsize=fs, color="#222", fontweight="bold", zorder=6)


def gnd(x, y):
    wire([(x, y), (x, y-0.08)], C_GND, 1.6)
    for i, w in enumerate([0.15, 0.10, 0.05]):
        ax.plot([x-w, x+w], [y-0.10-i*0.055, y-0.10-i*0.055], color=C_GND, lw=1.8, zorder=4)


def klamra(x, y):
    dot(x, y)
    wire([(x, y), (x, y+0.18)], C_5V, 1.3)
    dioda_v(x, y+0.30, "gora")
    wire([(x, y+0.42), (x, y+0.56)], C_5V, 1.3)
    ax.text(x, y+0.66, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold", zorder=6)
    wire([(x, y), (x, y-0.18)], C_GND, 1.3)
    dioda_v(x, y-0.30, "gora")
    wire([(x, y-0.42), (x, y-0.50)], C_GND, 1.3)
    gnd(x, y-0.50)


def sw_h(xc, yc):
    dot_l, dot_r = xc-0.28, xc+0.28
    ax.add_patch(Circle((dot_l, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.add_patch(Circle((dot_r, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.plot([dot_l+0.04, dot_r-0.02], [yc+0.02, yc+0.30], color="#222", lw=1.6, zorder=5)


def sw_v(xc, yc):
    dot_g, dot_d = yc+0.28, yc-0.28
    ax.add_patch(Circle((xc, dot_g), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.add_patch(Circle((xc, dot_d), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.plot([xc+0.02, xc+0.30], [dot_g-0.04, dot_d+0.02], color="#222", lw=1.6, zorder=5)


def sw_h_nc(xc, yc):
    """Styk NORMALNIE ZAMKNIETY (NC) w linii poziomej: ramie spoczywa na styku."""
    dot_l, dot_r = xc-0.28, xc+0.28
    ax.add_patch(Circle((dot_l, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.add_patch(Circle((dot_r, yc), 0.05, fc="white", ec="#222", lw=1.3, zorder=6))
    ax.plot([dot_l+0.04, dot_r+0.06], [yc+0.02, yc+0.06], color="#222", lw=1.6, zorder=5)
    ax.plot([dot_r+0.06, dot_r+0.06], [yc+0.06, yc+0.20], color="#222", lw=1.6, zorder=5)


def styk_przek_v(xc, yc, label=""):
    """Styk przekaznika (pionowy) z ramka."""
    sw_v(xc, yc)
    ax.add_patch(Rectangle((xc-0.34, yc-0.42), 0.9, 0.84, fill=False, ec=C_DIG, lw=0.9,
                 linestyle=(0, (2, 2)), zorder=4))
    if label:
        ax.text(xc+0.62, yc, label, ha="left", fontsize=6.0, color=C_DIG, fontweight="bold", zorder=6)


def neon(xc, yc, kol="#D97706"):
    ax.add_patch(Circle((xc, yc), 0.16, fc="white", ec=kol, lw=1.8, zorder=6))
    ax.add_patch(Circle((xc, yc), 0.06, fc=kol, ec=kol, zorder=6))


def ct_sensor(xc, yc):
    """Przekladnik pradowy (kolo na przewodzie)."""
    ax.add_patch(Circle((xc, yc), 0.24, fill=False, ec=C_INFO, lw=2.0, zorder=6))


Y_BUS = 24.0   # szyna PE (masa elektroniki)

# ================= TYTUL + LEGENDA =================
ax.text(W/2, 36.85, "Symulator pojazdu EV — PEŁNY SCHEMAT, koncepcja v2 (AKTYWNA maszyna decyzyjna pojazdu)",
        ha="center", fontsize=15, fontweight="bold")
ax.text(W/2, 36.35, "urządzenie SAMO przechodzi A→B→C po walidacji PP/PWM/poziomów — i ODMAWIA jak auto • ZERO ręcznych przełączników w torze CP: wszystkie styki załączają przekaźniki sterowane przez MCU • mierzy czasy reakcji stacji wg IEC 61851-1",
        ha="center", fontsize=8.2, color="#444")
ax.add_patch(FancyBboxPatch((0.4, 34.95), W-0.8, 1.05, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#EEF6FB", ec=C_INFO, lw=1.1, zorder=1))
ax.text(0.7, 35.7, "LEGENDA: pomarańczowy = sygnały CP/PP • zielony = cyfrowe/sterowanie • ciemnobrązowy gruby = tor mocy 230/400 V (32 A/fazę) • czarny = PE (= masa elektroniki) • czerwony = +5 V (z USB)",
        fontsize=7.2, color="#0C4A6E")
ax.text(0.7, 35.32, "kropka = połączenie, skrzyżowanie bez kropki = brak • styk w przerywanej ramce = styk przekaźnika (sterowany elektrycznie) • wartości rezystorów pojazdu wg IEC 61851-1 Tab. A.2 (±3%)",
        fontsize=7.2, color="#0C4A6E")

# ================= GNIAZDO TYPE 2 =================
box(0.4, 9.6, 2.9, 34.3, "Gniazdo wlotowe\nType 2, 32 A", "(jak w pojeździe —\nwpina się kabel stacji)", tfs=8.0, tdy=0.55)
Y_CP, Y_PP, Y_PE = 32.2, 29.2, 25.6
Y_L1, Y_L2, Y_L3, Y_N = 15.0, 13.8, 12.6, 11.4
for nazwa, yy, kol in [("CP", Y_CP, C_SIG), ("PP", Y_PP, C_SIG), ("PE", Y_PE, C_GND),
                       ("L1", Y_L1, C_MOC), ("L2", Y_L2, C_MOC), ("L3", Y_L3, C_MOC), ("N", Y_N, C_MOC)]:
    ax.text(2.62, yy, nazwa, ha="right", va="center", fontsize=7.6, fontweight="bold", color=kol, zorder=6)
    pinc(2.9, yy, kol)

# ================= RDZEN STANOW CP =================
wire([(2.9, Y_CP), (4.32, Y_CP)])
dot(3.6, Y_CP)
dot(4.15, Y_CP)
sw_h_nc(4.6, Y_CP)
ax.add_patch(Rectangle((4.18, Y_CP-0.34), 0.84, 0.78, fill=False, ec=C_DIG, lw=0.9,
             linestyle=(0, (2, 2)), zorder=4))
ax.text(4.6, 31.62, "KF2 — styk NC (spoczynkowo ZAMKNIĘTY):\nPRZERWA CP (przekaźnik, menu usterek)", ha="center", fontsize=5.6, color="#444", zorder=6, va="top")
wire([(4.88, Y_CP), (5.5, Y_CP)])
dot(5.5, Y_CP)
dioda_h(6.05, Y_CP, "1N4148")
wire([(6.16, Y_CP), (7.4, Y_CP)])
dot(6.6, Y_CP)
# bocznik diody KF1 (przekaznik)
wire([(5.5, Y_CP), (5.5, 33.3)], C_SIG, 1.4)
wire([(6.6, Y_CP), (6.6, 33.3)], C_SIG, 1.4)
wire([(5.5, 33.3), (5.77, 33.3)], C_SIG, 1.4)
sw_h(6.05, 33.3)
ax.add_patch(Rectangle((5.63, 32.96), 0.84, 0.78, fill=False, ec=C_DIG, lw=0.9,
             linestyle=(0, (2, 2)), zorder=4))
wire([(6.33, 33.3), (6.6, 33.3)], C_SIG, 1.4)
ax.text(6.05, 33.98, "KF1: ZWARCIE DIODY (przekaźnik, menu usterek — stacja musi wykryć i odmówić)", ha="center", fontsize=5.8, color="#444", zorder=6)
dot(7.4, Y_CP)
wire([(7.4, Y_CP), (11.8, Y_CP)])
# KF3: zwarcie CP-PE (stan E) — przekaznik
wire([(4.15, Y_BUS), (4.15, 28.25)], C_SIG, 1.4)
wire([(4.15, 28.81), (4.15, Y_CP)], C_SIG, 1.4)
styk_przek_v(4.15, 28.53)
ax.text(4.5, 27.55, "KF3: zwarcie CP–PE, stan E (przekaźnik, menu usterek)", ha="left", fontsize=5.8, color="#444", zorder=6)
dot(4.15, Y_BUS, C_GND)

# --- galaz B: R2 = 2,7 k NA STALE (bez styku — jak w aucie)
xg = 8.2
dot(xg, Y_CP)
wire([(xg, Y_CP), (xg, 30.1)], C_SIG, 1.6)
res_v(xg, 29.7, "2,7 kΩ 1%", h=0.8)
ax.text(xg+0.22, 28.98, "(norma: 2,74 k ±3%)", ha="left", fontsize=5.2, color=C_MUT, zorder=6)
wire([(xg, 29.3), (xg, Y_BUS)], C_SIG, 1.6)
dot(xg, Y_BUS, C_GND)
ax.text(4.5, 30.95, "R2 NA STAŁE — bez styku:\nstan B pojawia się SAM z chwilą\nwpięcia wtyku (przed wpięciem\nobwód nie istnieje = stan A)", ha="left",
        fontsize=5.6, color=C_INFO, fontweight="bold", zorder=6, va="top")

# --- galaz C: R3 = 1,3 k; zamykana PRZEKAZNIKIEM K2 (= S2 pojazdu)
xg = 10.4
dot(xg, Y_CP)
wire([(xg, Y_CP), (xg, 31.98)], C_SIG, 1.6)
styk_przek_v(xg, 31.65)
ax.text(10.12, 30.95, "K2 = S2 pojazdu (MCU)", ha="right", fontsize=5.6, color=C_DIG, fontweight="bold", zorder=6)
wire([(xg, 31.32), (xg, 30.1)], C_SIG, 1.6)
res_v(xg, 29.7, "1,3 kΩ 1%", h=0.8)
wire([(xg, 29.3), (xg, Y_BUS)], C_SIG, 1.6)
dot(xg, Y_BUS, C_GND)

# --- galaz D: R3 = 270; zamykana PRZEKAZNIKIEM K3 (wentylacja, opcja)
xg = 11.8
dot(xg, Y_CP)
wire([(xg, Y_CP), (xg, 31.98)], C_SIG, 1.6)
styk_przek_v(xg, 31.65)
wire([(xg, 31.32), (xg, 30.1)], C_SIG, 1.6)
res_v(xg, 29.7, "270 Ω 1%", h=0.8)
wire([(xg, 29.3), (xg, Y_BUS)], C_SIG, 1.6)
dot(xg, Y_BUS, C_GND)
ax.text(12.05, 29.0, "K3 = stan D (opcja)", ha="left", fontsize=5.4, color=C_DIG, fontweight="bold", zorder=6)
# cewki przekaznikow + driver
box(13.1, 29.9, 16.1, 31.5, "K2, K3, KF1–KF3\nprzekaźniki sygnałowe 5 V", "cewki przez ULN2003 (posiadany)\n← D7, D9–D12", tfs=6.6, tdy=0.38)
wire([(16.1, 30.7), (21.8, 30.7)], C_DIG, 1.5)
ax.text(16.8, 30.88, "D7, D9–D12 — sterowanie przekaźnikami stanów i usterek", fontsize=5.6, color=C_DIG, zorder=6)


# ================= POMIAR CP -> A1 + KOMPARATOR -> D8 =================
wire([(3.6, Y_CP), (3.6, 28.0), (12.38, 28.0)])
res_h(12.8, 28.0, "120 kΩ")
wire([(13.22, 28.0), (13.58, 28.0)])
res_h(14.0, 28.0, "120 kΩ")
wire([(14.42, 28.0), (17.28, 28.0)])
dot(14.8, 28.0)
ax.text(14.55, 28.22, "A", ha="right", fontsize=6.2, color=C_MUT, fontweight="bold", zorder=6)
wire([(14.8, 28.0), (14.8, 28.14)], C_5V, 1.3)
res_v(14.8, 28.46, "100 kΩ", h=0.55)
wire([(14.8, 28.74), (14.8, 28.9)], C_5V, 1.3)
ax.text(14.8, 29.02, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold", zorder=6)
wire([(14.8, 28.0), (14.8, 27.85)], C_GND, 1.3)
res_v(14.8, 27.52, "120 kΩ", h=0.55)
wire([(14.8, 27.24), (14.8, 27.1)], C_GND, 1.3)
gnd(14.8, 27.1)
klamra(16.2, 28.0)
dot(17.1, 28.0)
res_h(17.8, 28.0, "10 kΩ")
wire([(18.22, 28.0), (21.8, 28.0)])
dot(18.8, 28.0); cap_v(18.8, 28.0, "470 pF")
ax.text(18.8, 28.22, "A′", ha="center", fontsize=6.2, color=C_MUT, fontweight="bold", zorder=6)
ax.text(9.2, 27.0, "U(A) = 1,82 V + 0,152·U(CP)\n(sieć pomiarowa jak w rejestratorze Q11)",
        fontsize=6.2, color=C_INFO, zorder=6, va="top")
# galaz komparatora
wire([(17.1, 28.0), (17.1, 27.57)])
res_v(17.1, 27.3, "100 kΩ", h=0.55)
wire([(17.1, 27.02), (17.1, 26.2), (18.0, 26.2)])
dot(17.1, 26.2)
ax.text(16.85, 26.38, "B", ha="right", fontsize=6.2, color=C_MUT, fontweight="bold", zorder=6)
wire([(17.1, 26.2), (17.1, 25.87)], C_GND, 1.3)
res_v(17.1, 25.6, "100 kΩ", h=0.55)
wire([(17.1, 25.32), (17.1, Y_BUS)], C_GND, 1.3)
dot(17.1, Y_BUS, C_GND)
ax.add_patch(FancyBboxPatch((18.0, 24.7), 3.0, 2.0, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc=C_BOX, ec=C_EDGE, lw=1.5, zorder=1))
ax.text(19.5, 26.45, "LM393 (½)", ha="center", fontsize=7.8, fontweight="bold", color="#222", zorder=2)
ax.text(18.15, 26.2, "IN−", fontsize=6.4, va="center", color="#222", zorder=2)
ax.text(18.15, 25.4, "IN+", fontsize=6.4, va="center", color="#222", zorder=2)
ax.text(20.85, 25.8, "OUT", fontsize=6.4, va="center", ha="right", color="#222", zorder=2)
wire([(16.6, 25.4), (18.0, 25.4)], C_INFO, 1.5)
dot(16.6, 25.4, C_INFO)
wire([(16.6, 25.4), (16.6, 25.7)], C_5V, 1.3)
res_v(16.6, 25.95, "100 kΩ", h=0.5, side="left")
wire([(16.6, 26.2), (16.6, 26.32)], C_5V, 1.3)
ax.text(16.6, 26.44, "+5V", ha="center", fontsize=5.6, color=C_5V, fontweight="bold", zorder=6)
wire([(16.6, 25.4), (16.6, 25.1)], C_GND, 1.3)
res_v(16.6, 24.85, "10 kΩ", h=0.5, side="left")
wire([(16.6, 24.6), (16.6, Y_BUS)], C_GND, 1.3)
dot(16.6, Y_BUS, C_GND)
ax.text(16.25, 24.28, "próg 0,455 V ≈ U(CP) = −6 V", fontsize=5.8, color=C_INFO, ha="right", zorder=6)
wire([(21.0, 25.8), (21.8, 25.8)], C_DIG, 1.8)
dot(21.25, 25.8, C_DIG)
wire([(21.25, 25.8), (21.25, 26.02)], C_5V, 1.3)
res_v(21.25, 26.28, "10 kΩ", h=0.5)
wire([(21.25, 26.54), (21.25, 26.68)], C_5V, 1.3)
ax.text(21.25, 26.8, "+5V", ha="center", fontsize=5.6, color=C_5V, fontweight="bold", zorder=6)
dot(21.55, 25.8, C_DIG)
wire([(21.55, 25.8), (21.55, 24.3), (16.9, 24.3)], C_MUT, 1.3)
wire([(16.9, 24.3), (16.9, 25.4)], C_MUT, 1.3)
dot(16.9, 25.4, C_INFO)
res_h(19.4, 24.3, "470 kΩ (histereza)", fs=5.8, lab_dy=0.24)

# ================= PE / SZYNA MASY =================
wire([(2.9, Y_PE), (3.15, Y_PE)], C_GND, 2.0)
dot(3.15, Y_PE, C_GND)
wire([(3.15, Y_PE), (3.15, Y_BUS), (21.8, Y_BUS)], C_GND, 2.0)
ax.text(5.0, 23.7, "szyna PE = masa elektroniki (sygnały CP/PP odniesione do PE — jak w pojeździe)",
        fontsize=6.4, color=C_GND, fontweight="bold", zorder=6)
wire([(3.15, Y_PE), (3.15, 9.4)], C_GND, 2.0)
wire([(3.15, 9.4), (25.8, 9.4)], C_GND, 2.0)
ax.text(14.6, 9.08, "PE do gniazd wyjściowych — nigdzie nie przełączane", fontsize=6.2, color=C_GND, zorder=6)

# ================= PP =================
wire([(2.9, Y_PP), (5.0, Y_PP)])
wire([(5.0, Y_PP), (5.0, 22.2), (21.8, 22.2)])
dot(13.0, 22.2)
wire([(13.0, 22.2), (13.0, 22.38)], C_5V, 1.3)
res_v(13.0, 22.68, "1 kΩ", h=0.55, side="left")
wire([(13.0, 22.96), (13.0, 23.1)], C_5V, 1.3)
ax.text(13.0, 23.22, "+5V", ha="center", fontsize=5.8, color=C_5V, fontweight="bold", zorder=6)
ax.text(8.6, 22.42, "PP: pomiar i WALIDACJA kodowania kabla", fontsize=6.4, color=C_INFO, zorder=6)
ax.text(8.6, 21.92, "rezystor kodujący siedzi we WTYKU kabla, między PP a PE (Tab. B.3, ±3%)", fontsize=5.8, color=C_MUT, zorder=6)
# przycisk START/STOP: D5 -> przycisk -> masa (wejscie z podciaganiem)
wire([(21.8, 21.3), (20.9, 21.3)], C_DIG, 1.5)
sw_h(20.6, 21.3)
wire([(20.3, 21.3), (20.05, 21.3), (20.05, Y_BUS)], C_GND, 1.4)
dot(20.05, Y_BUS, C_GND)
ax.text(20.25, 21.52, "przycisk START/STOP — zwiera D5 do masy", ha="right", fontsize=5.4, color="#444", zorder=6)

# ================= NANO + LCD + PRZYCISK + ZASILANIE =================
box(21.8, 15.9, 26.4, 34.3, "Arduino Nano", "maszyna decyzyjna pojazdu + tester czasów stacji", tfs=10)
nano_piny = [("A4", 33.4, "SDA → LCD 20×4", C_DIG),
             ("A5", 32.9, "SCL → LCD 20×4", C_DIG),
             ("D7", 30.7, "K2 (S2); D9–D12: K3, KF1–KF3 (przez ULN2003)", C_DIG),
             ("A1", 28.0, "poziomy CP (węzeł A′)", C_SIG),
             ("D8", 25.8, "komparator → Timer1 (wypełnienie PWM)", C_DIG),
             ("GND", Y_BUS, "masa = PE", C_GND),
             ("A2", 22.2, "PP (kodowanie kabla)", C_SIG),
             ("D5", 21.3, "przycisk START/STOP", C_DIG),
             ("D6", 20.6, "cewka stycznika Q1 (przez moduł przek.)", C_DIG),
             ("D2", 19.9, "detektor fazy L1 (izolowany)", C_DIG),
             ("D3", 19.4, "detektor fazy L2", C_DIG),
             ("D4", 18.9, "detektor fazy L3", C_DIG),
             ("A3", 18.2, "CT L1 (przekładnik prądowy)", C_SIG),
             ("A6", 17.7, "CT L2", C_SIG),
             ("A7", 17.2, "CT L3", C_SIG)]
for nazwa, yy, opis, kol in nano_piny:
    pinc(21.8, yy, kol)
    ax.text(22.0, yy, nazwa + " — " + opis, fontsize=6.4, va="center", color="#222", fontweight="bold", zorder=6)
ax.text(22.0, 16.6, "pomiar czasów stacji: t_ACon (C→napięcie ≤3 s),", fontsize=6.0, color="#333", zorder=6)
ax.text(22.0, 16.2, "t_ACoff1 (S2 otwarte→zanik ≤100 ms) — werdykt PASS/FAIL", fontsize=6.0, color="#333", zorder=6)
box(12.6, 32.4, 16.8, 34.3, "LCD 20×4 + I2C", "stan, wypełnienie, prąd, kabel,\nPOWÓD ODMOWY, wyniki czasów", tfs=8.2, tdy=0.38)
wire([(16.8, 33.4), (21.8, 33.4)], C_DIG, 1.6)
wire([(16.8, 32.9), (21.8, 32.9)], C_DIG, 1.6)
box(23.2, 13.8, 26.4, 15.3, "Zasilanie 5 V", "powerbank / zasilacz USB —\nbez związku z torem mocy", tfs=8, tdy=0.35)
wire([(24.8, 15.9), (24.8, 15.3)], C_INFO, 2.0)
ax.text(24.95, 15.58, "USB", fontsize=6.0, color=C_INFO, zorder=6)

# ================= TABELE NORMOWE =================
ax.add_patch(FancyBboxPatch((3.6, 16.4), 5.9, 4.6, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#E8F4FD", ec=C_INFO, lw=1.0, zorder=1))
ax.text(3.85, 20.68, "Interpretacja PWM przez POJAZD (Tab. A.6):", fontsize=6.6, fontweight="bold", color=C_INFO, zorder=2)
for i, t in enumerate(["< 3%:  ładowanie ZABRONIONE", "3–7%:  tylko komunikacja cyfrowa → ODMOWA",
                       "7–8%:  ZABRONIONE", "8–10%:  6 A", "10–85%:  I = wypełnienie% × 0,6 A",
                       "85–96%:  I = (wypełnienie% − 64) × 2,5 A", "96–97%:  80 A", "> 97% / brak PWM:  ZABRONIONE"]):
    ax.text(3.85, 20.3-i*0.48, t, fontsize=6.0, color="#0C4A6E", zorder=2)
ax.add_patch(FancyBboxPatch((9.9, 16.4), 5.6, 4.6, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#E8F4FD", ec=C_INFO, lw=1.0, zorder=1))
ax.text(10.15, 20.68, "Stany CP (±1 V, Tab. A.3) i czasy (Tab. A.7):", fontsize=6.6, fontweight="bold", color=C_INFO, zorder=2)
for i, t in enumerate(["A: 12 V • B: 9 V • C: 6 V • D: 3 V • E: 0 V", "ujemna połówka: −12 V (dioda pojazdu)",
                       "POJAZD: S2 otwarte ≤3 s gdy pilot zły (t_ACoff2)", "POJAZD: nowy prąd ≤5 s po zmianie PWM",
                       "STACJA: napięcie ≤3 s po C (t_ACon)", "STACJA: odcięcie ≤100 ms po otwarciu S2",
                       "→ dwa ostatnie MIERZYMY i oceniamy stację"]):
    ax.text(10.15, 20.3-i*0.55, t, fontsize=6.0, color="#0C4A6E", zorder=2)
ax.add_patch(FancyBboxPatch((15.9, 16.4), 4.6, 4.6, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#E8F4FD", ec=C_INFO, lw=1.0, zorder=1))
ax.text(16.15, 20.68, "PP → kabel (Tab. B.3, ±3%):", fontsize=6.6, fontweight="bold", color=C_INFO, zorder=2)
for i, t in enumerate(["1,5 kΩ → 13 A", "680 Ω → 20 A", "220 Ω → 32 A", "100 Ω → 63 A", "poza oknami → ODMOWA",
                       "(przypadek wadliwego", "modułu Tesli — wykryty)"]):
    ax.text(16.15, 20.3-i*0.55, t, fontsize=6.0, color="#0C4A6E", zorder=2)

# ================= TOR MOCY 3x32 A =================
box(5.4, 10.6, 7.6, 16.0, "Rozłącznik +\nwyłącznik\nB32, 3P+N", tfs=7.2, tdy=0.5)
box(8.2, 10.6, 10.4, 16.0, "RCD 30 mA\ntyp A, 4P,\n40 A", tfs=7.2, tdy=0.5)
box(11.0, 10.6, 13.6, 16.0, "Stycznik Q1\n3F, 40 A", "zamykany z wejściem w C;\ncewka przez E-STOP (weto\nsprzętowe) i moduł przek. z D6", tfs=7.2, tdy=0.5)
box(14.2, 10.6, 16.6, 16.0, "Licznik energii\n3-faz., DIN", "U, I, P, kWh podczas\nładowania (opcja zalecana)", tfs=7.0, tdy=0.5, dashed=True)
box(19.4, 10.3, 22.4, 16.2, "Gniazdo CEE 32 A, 5P", tfs=7.4, tdy=0.35)
ax.text(20.9, 15.55, "wyjście mocy 22 kW —\nmagazyn energii / obciążenie\n(konwersję AC→DC robi ładowarka\nmagazynu — jak OBC w aucie)", ha="center", fontsize=6.0, color="#555", zorder=2, va="top")
box(23.2, 10.3, 26.4, 13.0, "Gniazdo 230 V", "za własnym B16 1P;\nszybkie próby 1-fazowe", tfs=7.2, tdy=0.4)
for yy in [Y_L1, Y_L2, Y_L3, Y_N]:
    wire([(2.9, yy), (5.4, yy)], C_MOC, 2.6)
    wire([(7.6, yy), (8.2, yy)], C_MOC, 2.6)
    wire([(10.4, yy), (11.0, yy)], C_MOC, 2.6)
    wire([(13.6, yy), (14.2, yy)], C_MOC, 2.6)
    wire([(16.6, yy), (19.4, yy)], C_MOC, 2.6)
ax.text(3.7, 15.26, "6 mm²", fontsize=6.0, color=C_MOC, zorder=6)
# detektory faz (izolowane) - przed stycznikiem, za RCD? -> za B32, przed stycznikiem: x 10.7 obszar waski;
# rysujemy odczepy z segmentu miedzy RCD a stycznikiem w dol do boxu detektorow
box(9.0, 8.2, 13.2, 9.9, "3× izolowany detektor obecności fazy (transoptor)", "pomiar L1/L2/L3 względem N → D2/D3/D4 (t_ACon, t_ACoff1 niezależnie od Q1)", tfs=6.6, tdy=0.35)
for i, yl in enumerate([Y_L1, Y_L2, Y_L3, Y_N]):
    xq = 10.5 + i*0.13
    dot(xq, yl, C_MOC)
    wire([(xq, yl), (xq, 9.9)], C_MOC, 1.2)
# CT na fazach (za licznikiem)
for i, yl in enumerate([Y_L1, Y_L2, Y_L3]):
    ct_sensor(16.95, yl)
ax.text(16.95, 15.62, "3× CT → A3/A6/A7", ha="center", fontsize=5.8, color=C_INFO, fontweight="bold", zorder=6)
ax.text(17.55, 16.12, "(obciążnik + polaryzacja 2,5 V)", ha="center", fontsize=5.0, color=C_INFO, zorder=6)
# neonowki
for xg, yl in [(17.8, Y_L1), (18.25, Y_L2), (18.7, Y_L3)]:
    dot(xg, yl, C_MOC)
    wire([(xg, yl), (xg, Y_N+0.62)], C_MOC, 1.3)
    neon(xg, Y_N+0.45)
    wire([(xg, Y_N+0.28), (xg, Y_N)], C_MOC, 1.3)
    dot(xg, Y_N, C_MOC)
ax.text(18.25, 10.42, "3× kontrolka faz", ha="center", fontsize=5.8, color=C_MOC, zorder=6)
# most CEE -> 230V przez B16 1P
wire([(22.4, 12.0), (22.5, 12.0)], C_MOC, 2.2)
ax.add_patch(Rectangle((22.5, 11.62), 0.9, 0.76, fc="white", ec=C_EDGE, lw=1.3, zorder=5))
ax.text(22.95, 12.0, "B16\n1P", ha="center", va="center", fontsize=5.4, fontweight="bold", color="#222", zorder=6)
wire([(23.4, 12.0), (23.6, 12.0)], C_MOC, 2.2)
# PE do gniazd
wire([(21.0, 9.4), (21.0, 10.3)], C_GND, 1.8)
dot(21.0, 9.4, C_GND)
wire([(24.6, 9.4), (24.6, 10.3)], C_GND, 1.8)
dot(24.6, 9.4, C_GND)
# obwod cewki stycznika: L1 -> E-STOP (NC) -> styk modulu przek. (D6) -> cewka Q1 -> N
box(4.6, 8.2, 8.4, 9.9, "Obwód cewki Q1", tfs=7.0, tdy=0.3)
ax.text(6.5, 9.42, "L1 → E-STOP (grzybek, NC) → styk\nmodułu przekaźnikowego (D6) →\ncewka Q1 → N; E-STOP = odcięcie\nniezależne od MCU", ha="center", fontsize=5.4, color="#555", zorder=2, va="top")
wire([(8.4, 8.55), (8.7, 8.55), (8.7, 8.0), (13.45, 8.0), (13.45, 10.6)], C_MOC, 1.4)
ax.text(13.58, 9.6, "do cewki Q1", fontsize=5.2, color=C_MOC, zorder=6)

# ================= SEKWENCJA / NOTATKI =================
ax.add_patch(FancyBboxPatch((0.4, 4.3), 26.1, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#ECFDF5", ec="#059669", lw=1.2, zorder=1))
ax.text(0.65, 7.35, "SEKWENCJA TRYBU AUTO (dokładnie jak pojazd wg IEC 61851-1 Tab. A.4):", fontsize=7.0, fontweight="bold", color="#065F46", zorder=2)
seq = ["1. Wpięcie wtyku → stan B pojawia się SAM (R2 wlutowany na stałe — przed wpięciem obwód CP nie istnieje) • MCU czyta PP → walidacja Tab. B.3; ZŁE PP = zostajemy w B + „AUTO ODMAWIA: PP = … Ω poza tabelą”",
       "2. Stacja podaje PWM → walidacja wypełnienia (Tab. A.6) i poziomów (±1 V); poprawne → po opóźnieniu startu MCU zamyka K2 (S2) → stan C i RÓWNOLEGLE zamyka stycznik Q1",
       "3. Pomiar t_ACon: czy stacja podała napięcie ≤3 s po C (detektory faz)? • w C ciągły nadzór: PWM/poziomy/PP/pobór (CT) vs oferta — naruszenie → S2 otwarte ≤3 s + komunikat",
       "4. STOP (przycisk / koniec sesji): MCU otwiera S2 → pomiar t_ACoff1: czy stacja odcięła ≤100 ms (detektory faz)? potem otwarcie Q1 • przekroczenie poboru: najpierw S2, po 200 ms Q1",
       "5. W torze CP NIE MA żadnego ręcznego przełącznika — wymuszanie stanów i usterek wyłącznie elektronicznie, z menu serwisowego (K2/K3, KF1–KF3); scenariusze usterek odtwarzane też AUTOMATYCZNĄ sekwencją z werdyktami PASS/FAIL"]
for i, t in enumerate(seq):
    ax.text(0.65, 6.95-i*0.52, t, fontsize=6.1, color="#065F46", zorder=2)

ax.add_patch(FancyBboxPatch((0.4, 0.9), 26.1, 3.0, boxstyle="round,pad=0.03,rounding_size=0.1",
             fc="#FEF3C7", ec="#D97706", lw=1.2, zorder=1))
naty = ["• BEZPIECZEŃSTWO: w stanie C gniazda wyjściowe pod napięciem 230/400 V, do 32 A/fazę. Praca tylko z zamkniętą obudową; E-STOP rozcina cewkę Q1 sprzętowo (weto niezależne od programu);",
        "  otwarcie S2 przy E-STOP → stacja sama odcina ≤100 ms (druga, niezależna droga odcięcia). Kierunek bezpieczny: martwy MCU = S2 otwarte = najwyżej stan B, stycznik otwarty.",
        "• MAGAZYN ENERGII: symulator = „samochód bez baterii” — konwersję AC→DC wykonuje ładowarka magazynu wpięta w CEE (dokładnie jak OBC w aucie); symulator egzekwuje limit prądu",
        "  z PWM (stycznik + CT) i wyświetla go operatorowi/ładowarce magazynu. • Rezystory rdzenia: metalizowane 1% (okna normy ±3%); dioda: Vd 0,7 ± 0,15 V — 1N4148 spełnia.",
        "• Zasilanie elektroniki WYŁĄCZNIE z USB (powerbank) — komunikaty działają w stanach A/B, zanim stacja poda napięcie; brak związku galwanicznego elektroniki z L/N (CT i transoptory = izolacja)."]
for i, t in enumerate(naty):
    ax.text(0.65, 3.55-i*0.52, t, fontsize=6.1, color="#7A5800", zorder=2)

plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_schemat_PELNY.png", dpi=110,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: schemat symulatora v2 zapisany")
