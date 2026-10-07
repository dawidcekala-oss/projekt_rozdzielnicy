# -*- coding: utf-8 -*-
"""Rysunek szczegolowy: jak zasilic plytke Nano z ISTNIEJACEJ przetwornicy 230 V -> 5 V
w puszce. Reszta elektroniki jest juz zlutowana i zasilana z wyprowadzen 5V/GND Nano
(ten sam wezel) - bez zmian."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\symulator_pojazdu"

C_GND = "#111111"
C_5V = "#B00020"
C_MOC = "#7C2D12"
C_N = "#1D4ED8"
C_INFO = "#0369A1"
C_MUT = "#888888"
C_BOX = "#F7F7F5"

W, H = 16.2, 9.6
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def panel(x0, y0, x1, y1, tytul, fs=10.0):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle="round,pad=0.02,rounding_size=0.08",
                 fc="white", ec="#BBB", lw=1.2, zorder=0))
    ax.text(x0+0.18, y1-0.28, tytul, fontsize=fs, fontweight="bold", color="#111", zorder=2)


def box(x0, y0, x1, y1, tytul, fs=7.0, fc=C_BOX, ec="#333"):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle="round,pad=0.02,rounding_size=0.06",
                 fc=fc, ec=ec, lw=1.3, zorder=1))
    ax.text((x0+x1)/2, y1-0.22, tytul, ha="center", va="top", fontsize=fs, fontweight="bold", color="#111", zorder=2)


def wire(pts, color=C_GND, lw=1.8):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw, solid_capstyle="round", zorder=3)


def dot(x, y, color=C_GND):
    ax.add_patch(Circle((x, y), 0.055, fc=color, ec=color, zorder=6))


def pinc(x, y, color="#222"):
    ax.add_patch(Circle((x, y), 0.05, fc="white", ec=color, lw=1.3, zorder=6))


def sw_h(xc, yc):
    l, r = xc-0.25, xc+0.25
    ax.add_patch(Circle((l, yc), 0.045, fc="white", ec="#222", lw=1.2, zorder=6))
    ax.add_patch(Circle((r, yc), 0.045, fc="white", ec="#222", lw=1.2, zorder=6))
    ax.plot([l+0.04, r-0.02], [yc+0.02, yc+0.26], color="#222", lw=1.5, zorder=5)


def cap_v(xc, yc, label, polar=False, side="right"):
    ax.plot([xc-0.16, xc+0.16], [yc+0.05, yc+0.05], color="#222", lw=2.3, zorder=5)
    if polar:
        ax.add_patch(Rectangle((xc-0.16, yc-0.11), 0.32, 0.07, fc="#222", ec="#222", zorder=5))
        ax.text(xc+0.2, yc+0.13, "+", fontsize=7, color="#222", zorder=6)
    else:
        ax.plot([xc-0.16, xc+0.16], [yc-0.06, yc-0.06], color="#222", lw=2.3, zorder=5)
    if side == "right":
        ax.text(xc+0.24, yc, label, fontsize=6.2, va="center", ha="left", color="#222", fontweight="bold", zorder=6)
    else:
        ax.text(xc-0.26, yc, label, fontsize=6.2, va="center", ha="right", color="#222", fontweight="bold", zorder=6)


# ================= TYTUL =================
ax.text(W/2, 9.22, "Symulator pojazdu EV — SZCZEGÓŁ: jak zasilić Nano z istniejącej przetwornicy 5 V",
        ha="center", fontsize=13, fontweight="bold")
ax.text(W/2, 8.86, "dwa przewody i dwa kondensatory — reszta elektroniki jest już zlutowana i bierze 5 V z wyprowadzeń płytki Nano (ten sam węzeł); niczego nie przelutowywać",
        ha="center", fontsize=8.2, color="#444")

# ================= PANEL A: STRONA 230 V =================
panel(0.3, 2.3, 6.85, 8.45, "A. Strona 230 V (istniejące elementy puszki, bez zmian)")
box(0.55, 4.7, 1.85, 7.6, "Wtyczka\n230 V", fs=7.2)
ax.text(1.2, 6.85, "własny przewód\nzasilający\ntestera", ha="center", va="top", fontsize=5.8, color="#555", zorder=2)
Y_L, Y_N, Y_PE = 7.05, 6.05, 5.05
for lab, yy, kol in [("L", Y_L, C_MOC), ("N", Y_N, C_N), ("PE", Y_PE, C_GND)]:
    pinc(1.85, yy, kol)
    ax.text(1.68, yy, lab, ha="right", va="center", fontsize=6.8, fontweight="bold", color=kol, zorder=6)
ax.plot([2.25, 2.25], [4.8, 7.5], color="#999", lw=1.0, ls=(0, (3, 2)), zorder=2)
ax.text(2.25, 7.88, "dławnica", ha="center", va="bottom", fontsize=5.8, color="#777", zorder=6)
wire([(1.85, Y_L), (2.6, Y_L)], C_MOC, 2.0)
sw_h(2.85, Y_L)
ax.text(2.85, 7.6, "łącznik na panelu\n(ISTNIEJĄCY)", ha="center", fontsize=5.8, color="#444", zorder=6)
wire([(3.1, Y_L), (3.5, Y_L)], C_MOC, 2.0)
ax.add_patch(Rectangle((3.5, Y_L-0.13), 0.62, 0.26, fc="white", ec="#333", lw=1.2, ls=(0, (3, 2)), zorder=5))
ax.plot([3.5, 4.12], [Y_L, Y_L], color="#333", lw=1.0, zorder=5)
ax.text(3.81, Y_L-0.45, "T 500 mA\n5×20 (zalecany —\nmoduł nie ma\nwłasnego)", ha="center", va="top", fontsize=5.4, color="#444", zorder=6)
wire([(4.12, Y_L), (4.5, Y_L)], C_MOC, 2.0)
wire([(1.85, Y_N), (4.5, Y_N)], C_N, 2.0)
wire([(1.85, Y_PE), (2.05, Y_PE), (2.05, 1.55)], C_GND, 2.2)
ax.text(2.18, 3.6, "PE wtyczki testera → szyna PE puszki", fontsize=5.8, color=C_GND, rotation=90, va="center", zorder=6)

box(4.5, 3.9, 6.7, 7.75, "Przetwornica 230 V → 5 V", fs=7.4)
for lab, yy, kol, side in [("L IN", Y_L, C_MOC, "l"), ("N", Y_N, C_N, "l"), ("OUT +", Y_L, C_5V, "r"), ("OUT −", Y_N, C_GND, "r")]:
    xx = 4.5 if side == "l" else 6.7
    pinc(xx, yy, kol)
    ax.text(xx + (0.14 if side == "l" else -0.14), yy, lab, ha=("left" if side == "l" else "right"),
            va="center", fontsize=6.4, fontweight="bold", color=kol, zorder=6)
ax.text(5.6, 5.65, "ISTNIEJĄCA (SKU 011012)\nizolowany moduł impulsowy\n0,7 A / 3,5 W\nograniczenie prądu, zabezp.\nzwarciowe i termiczne\n\nstrona 230 V odsłonięta —\nmoduł na dystansach lub\nw koszulce, ≥ 8 mm od\nmasy i sygnałów",
        ha="center", va="top", fontsize=5.5, color="#444", zorder=2)
ax.text(1.15, 4.35, "kolory żył jak w puszce:\nL IN — czerwony\nN — niebieski\nOUT+ — czerwony\nOUT− — czarny",
        ha="center", va="top", fontsize=5.6, color=C_MUT, zorder=2)

# ================= PANEL B: DO NANO =================
panel(7.0, 2.3, 15.95, 8.45, "B. Co dochodzi: dwa przewody 0,5 mm² i dwa kondensatory")
# przewody z przetwornicy do Nano
wire([(6.7, Y_L), (9.6, Y_L)], C_5V, 2.2)
wire([(6.7, Y_N), (9.6, Y_N)], C_GND, 2.2)
ax.text(7.75, Y_L+0.16, "NOWY przewód (czerwony)", ha="center", fontsize=5.8, color=C_5V, zorder=6)
ax.text(7.75, Y_N+0.14, "NOWY przewód (czarny)", ha="center", fontsize=5.8, color=C_GND, zorder=6)
# kondensatory tuz przy plytce (dwa piony, etykiety po lewej, rozne wysokosci)
XC = 8.7
dot(XC, Y_L, C_5V); dot(XC, Y_N)
wire([(XC, Y_L), (XC, 6.85)], C_5V, 1.5)
cap_v(XC, 6.7, "470 µF/16 V", polar=True, side="left")
wire([(XC, 6.55), (XC, Y_N)], C_GND, 1.5)
XC2 = 9.25
dot(XC2, Y_L, C_5V); dot(XC2, Y_N)
wire([(XC2, Y_L), (XC2, 6.5)], C_5V, 1.5)
cap_v(XC2, 6.35, "100 nF", side="left")
wire([(XC2, 6.2), (XC2, Y_N)], C_GND, 1.5)
ax.text(8.25, 5.72, "oba NOWE, tuż przy\nwyprowadzeniach płytki", ha="left", va="top", fontsize=5.4, color=C_MUT, zorder=6)

# Nano
box(9.6, 3.9, 12.1, 7.75, "Płytka Nano", fs=7.6)
for lab, yy, kol in [("5V", Y_L, C_5V), ("GND", Y_N, C_GND)]:
    pinc(9.6, yy, kol)
    ax.text(9.74, yy, lab, ha="left", va="center", fontsize=6.6, fontweight="bold", color=kol, zorder=6)
ax.text(10.85, 5.65, "5V — NIE VIN:\nstabilizator z 5 V na wejściu\nnie zrobi 5 V na wyjściu\n\nUSB na czas programowania:\nłącznik na panelu w OFF\n(dioda na płytce i tak\nblokuje, ale to nawyk)\n\nprzez wyprowadzenie 5V\npłynie pobór reszty + płytki:\n≈ 175 mA (ścieżka ≈ 1 A)",
        ha="center", va="top", fontsize=5.5, color="#444", zorder=2)
# istniejace polaczenia z pinow Nano
for lab, yy, kol in [("5V", Y_L, C_5V), ("GND", Y_N, C_GND)]:
    pinc(12.1, yy, kol)
    ax.text(11.96, yy, lab, ha="right", va="center", fontsize=6.6, fontweight="bold", color=kol, zorder=6)
wire([(12.1, Y_L), (12.9, Y_L)], C_5V, 2.2)
wire([(12.1, Y_N), (12.9, Y_N)], C_GND, 2.2)
ax.text(12.5, Y_L+0.16, "ISTNIEJĄCE", ha="center", fontsize=5.6, color=C_MUT, zorder=6)
box(12.9, 3.9, 15.75, 7.75, "Reszta elektroniki —\nZLUTOWANA, bez zmian", fs=6.8, fc="#F1F5F9", ec="#94A3B8")
ax.text(13.05, 6.85, "zasilana z wyprowadzeń 5V / GND\npłytki Nano — to TEN SAM węzeł,\nco wyjście przetwornicy:",
        ha="left", va="top", fontsize=5.5, color="#333", zorder=2)
for i, t in enumerate(["• sterownik cewek ULN2003 (nóżki 9 i 8)", "  + 4 cewki przekaźników 5 V",
                       "• komparator LM393 (nóżki 8 i 4)", "• wyświetlacz 16×2", "• brzęczyk",
                       "• sieć pomiarowa (klamry, próg,", "  podciąganie PP i wyjścia)",
                       "", "pobór razem ≈ 150 mA"]):
    ax.text(13.05, 6.05-i*0.24, t, fontsize=5.3, color="#333", zorder=2)
# miernik pilota - zostaje na wyjsciu przetwornicy jak dotad
wire([(7.4, Y_L), (7.4, 3.55)], C_5V, 1.4); dot(7.4, Y_L, C_5V)
wire([(7.9, Y_N), (7.9, 3.55)], C_GND, 1.4); dot(7.9, Y_N)
box(7.15, 2.5, 9.4, 3.55, "Miernik pilota (ISTNIEJĄCY)", fs=6.2)
ax.text(8.27, 3.1, "zostaje na wyjściu przetwornicy\ntak, jak jest — bez zmian (do 100 mA)", ha="center", va="top", fontsize=5.3, color="#444", zorder=2)

# masa -> PE (istniejacy jeden punkt)
wire([(12.5, Y_N), (12.5, 1.55)], C_GND, 2.2); dot(12.5, Y_N)
dot(12.5, 1.55)
ax.text(12.62, 2.0, "ISTNIEJĄCE: jedyny punkt masa → PE (bez zmian)", fontsize=5.8, color=C_GND, fontweight="bold", zorder=6)
wire([(2.05, 1.55), (15.7, 1.55)], C_GND, 2.6)
ax.text(8.0, 1.25, "szyna PE puszki = PE wtyczki testera = PE wlotu Type 2 (dwa przewody ochronne na jednej szynie — normalne)", ha="center", fontsize=6.2, color=C_GND, zorder=6)
ax.text(15.55, 1.69, "PE wlotu Type 2", ha="right", fontsize=6.0, color=C_GND, zorder=6)
wire([(15.7, 1.55), (15.7, 2.0)], C_GND, 1.6); dot(15.7, 1.55)

# ================= NOTATKI =================
ax.add_patch(FancyBboxPatch((0.3, 0.12), 7.7, 0.92, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc="#E8F4FD", ec=C_INFO, lw=1.1, zorder=1))
for i, t in enumerate(["BILANS przetwornicy (0,7 A): miernik pilota do 100 mA + Nano 25 mA + reszta ≈ 150 mA",
                       "(wyświetlacz 25, dwa przekaźniki naraz 66, brzęczyk 30 chwilowo, komparator i sieć < 5) → RAZEM ≈ 250–275 mA, zapas ≈ 2,5×",
                       "w przeciążeniu moduł ogranicza prąd → zanik 5 V → przekaźniki opadają → stan „podłączony” (kierunek bezpieczny bez zmian)"]):
    ax.text(0.45, 0.82-i*0.25, t, fontsize=6.2, color="#0C4A6E", zorder=2)
ax.add_patch(FancyBboxPatch((8.2, 0.12), 7.75, 0.92, boxstyle="round,pad=0.02,rounding_size=0.06",
             fc="#FEF3C7", ec="#D97706", lw=1.1, zorder=1))
for i, t in enumerate(["CO ZROBIĆ: (1) czerwony OUT+ → wyprowadzenie 5V Nano, (2) czarny OUT− → GND Nano, (3) 470 µF (plus do 5V) i 100 nF",
                       "między tymi wyprowadzeniami, (4) odpiąć zasilacz USB. Wszystko inne zostaje. Kolejność po włączeniu łącznika:",
                       "5 V → start programu → przekaźniki opadnięte → stan „podłączony” — dokładnie jak dotąd z zasilacza USB."]):
    ax.text(8.35, 0.82-i*0.25, t, fontsize=6.2, color="#7A5800", zorder=2)

plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_detal_zasilania.pdf", bbox_inches="tight", facecolor="white")
plt.savefig(OUT + r"\AMPERE_POINT_symulator_pojazdu_detal_zasilania.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("OK: detal zasilania (wersja 'dwa przewody') zapisany (PDF + PNG)")
