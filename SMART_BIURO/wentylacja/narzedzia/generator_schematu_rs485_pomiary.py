# -*- coding: utf-8 -*-
"""Modul RS485 V2.05 (MAX3485): widok z gory jak na zdjeciu + schemat + co z tego wynika.

Wersja 3 (14 IX 2026), po pomiarach uzytkownika: RE i DE sa polaczone i wychodza na pin EN,
rezystor 103 podciaga ten wezel do VCC; naprawa = wezel do masy w dowolnym jego punkcie.
Wyjscie: modul_v2/schemat_modul_rs485.png i .pdf
"""
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\SMART_BIURO\wentylacja\modul_v2\schemat_modul_rs485"
plt.rcParams["font.family"] = "DejaVu Sans"

fig = plt.figure(figsize=(18, 12))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 180); ax.set_ylim(0, 120); ax.axis("off")

CZ = "#222222"; SYG = "#1f5fbf"; ZAS = "#c0392b"; BUS = "#0a7d3b"; NAPR = "#8e44ad"; UWAGA = "#e67e22"; NIEB = "#2c4a7c"


def linia(pts, kolor=CZ, lw=2.4, ls="-"):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=kolor, lw=lw, ls=ls, solid_capstyle="round", solid_joinstyle="round", zorder=3)


def t(x, y, s, size=11, **kw):
    kw.setdefault("ha", "center"); kw.setdefault("va", "center")
    ax.text(x, y, s, fontsize=size, zorder=6, **kw)


def rez_pion(x, y1, y2, etyk, side="right", kolor=CZ):
    ym = (y1 + y2) / 2
    linia([(x, y1), (x, ym - 3)], kolor); linia([(x, ym + 3), (x, y2)], kolor)
    ax.add_patch(Rectangle((x - 1.4, ym - 3), 2.8, 6, fc="white", ec=kolor, lw=2, zorder=4))
    t(x + (2.3 if side == "right" else -2.3), ym, etyk, 9, ha="left" if side == "right" else "right")


def pin(x, y, r=1.5, kolor=CZ):
    ax.add_patch(Circle((x, y), r, fc="white", ec=kolor, lw=2, zorder=5))


def smd(x, y, w, h, etyk, kolor="#333", tekst="white"):
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=kolor, ec="#111", zorder=4))
    t(x, y, etyk, 8.5, color=tekst, weight="bold")


# ═══════════════ TYTUL ═══════════════
t(90, 116.5, "Moduł RS485 V2.05 (MAX3485): jak wygląda, jak jest połączony i dlaczego drut do masy włącza odbiór", 15, weight="bold")

# ═══════════════ 1. WIDOK Z GORY ═══════════════
t(8, 111, "1. Widok z góry, jak na zdjęciu", 12, weight="bold", color=NIEB, ha="left")
ax.add_patch(FancyBboxPatch((8, 31), 56, 77, boxstyle="round,pad=0.6,rounding_size=2", fc="#dfe9f7", ec="#5b7db1", lw=2.5, zorder=1))

# listwa magistrali
for x in (26, 36, 46):
    pin(x, 103.5, 1.9)
t(36, 99.3, "listwa magistrali: 3 pola (GND / A / B wg napisów na płytce)", 9.2, color=NIEB)

# rzad rezystorow
smd(24, 93.5, 8, 3.4, "472"); smd(36, 93.5, 8, 3.4, "121"); smd(48, 93.5, 8, 3.4, "472")
t(36, 90, "4,7 kΩ polaryzacja  ·  120 Ω terminator  ·  4,7 kΩ polaryzacja", 8.4)

# scalak
ax.add_patch(Rectangle((25, 60), 22, 20, fc="#2b2b2b", ec="#000", lw=1.5, zorder=4))
t(36, 72, "MAX3485", 11, color="white", weight="bold"); t(36, 66.5, "widok z góry", 8.5, color="#bbb")
xs = (28, 33.3, 38.7, 44)
for x, n, nazwa in zip(xs, ("8", "7", "6", "5"), ("VCC", "B", "A", "GND")):
    ax.add_patch(Rectangle((x - 0.9, 80), 1.8, 3.2, fc="#c8c8c8", ec="#777", zorder=5))
    t(x, 85.2, n, 9.5, weight="bold"); t(x, 87.7, nazwa, 9)
for x, n, nazwa in zip(xs, ("1", "2", "3", "4"), ("RO", "RE", "DE", "DI")):
    ax.add_patch(Rectangle((x - 0.9, 56.8), 1.8, 3.2, fc="#c8c8c8", ec="#777", zorder=5))
    t(x, 54.3, n, 9.5, weight="bold"); t(x, 51.8, nazwa, 9)
ax.add_patch(Circle((26.4, 57.2), 0.7, fc="white", ec="white", zorder=6))
t(23.6, 55.2, "kropka\n= nóżka 1", 7.8, ha="right")
t(36, 48.6, "dolny rząd od kropki: 1 RO · 2 RE · 3 DE · 4 DI     górny rząd od lewej: 8 VCC · 7 B · 6 A · 5 GND", 8.2)

# 103 po lewej, LED + 102 po prawej
smd(15.5, 70, 3.4, 8, "103"); t(15.5, 76.2, "10 kΩ", 8.5); t(15.5, 63.8, "przy literze T", 7.8)
smd(56, 74, 5, 3.2, "LED", kolor="#5ad07a", tekst="#111"); smd(56, 66, 5, 3.2, "102"); t(56, 62.3, "1 kΩ (dioda)", 7.8)

# listwa do procesora
for x, nazwa in ((16, "EN"), (26, "VCC"), (36, "RXD"), (46, "TXD"), (56, "GND")):
    pin(x, 41, 1.9); t(x, 37.4, nazwa, 9.5, weight="bold")
t(36, 33.8, "listwa do procesora: 5 pól (kolejność wg napisów na płytce)", 9.2, color=NIEB)

# cztery punkty przy T - ramka pod modulem
ax.add_patch(FancyBboxPatch((8, 21.5), 56, 9.2, boxstyle="round,pad=0.4", fc="#fff8f0", ec=UWAGA, lw=1.5, zorder=2))
t(36, 29.0, "Cztery punkty przy 103 i literze T: 2 puste pola + 2 końcówki rezystora", 8.4, weight="bold")
t(36, 26.9, "węzeł RE/DE (wolno do masy): pole DALEJ od T, końcówka 103 BLIŻEJ T", 8.1)
t(36, 24.9, "zasilanie 3,3 V (NIE do masy): pole BLIŻEJ T, końcówka 103 DALEJ od T", 8.1)
t(36, 22.8, "sprawdź: punkt ↔ pin EN listwy = 0 Ω → węzeł;  ≈ 10 kΩ → zasilanie", 8.2, color=ZAS, weight="bold")

# ═══════════════ 2. SCHEMAT ═══════════════
t(70, 111, "2. Schemat połączeń (to, co zmierzyliśmy omomierzem)", 12, weight="bold", color=NIEB, ha="left")
# szyny
linia([(72, 104), (176, 104)], ZAS, 3); t(73, 106.3, "VCC 3,3 V (z pinu 3V3 procesora)", 9.5, color=ZAS, ha="left")
linia([(72, 44), (176, 44)], CZ, 3); t(73, 41.5, "masa (wspólna: listwa do procesora, listwa magistrali, procesor, biała żyła wtyczki)", 9.5, ha="left")

# scalak
ax.add_patch(Rectangle((112, 56), 26, 40, fc="white", ec=CZ, lw=2.5, zorder=4))
t(125, 92.5, "MAX3485", 11.5, weight="bold")
t(125, 84.5, "odbiornik\nA−B > +0,2 V → RO = 1\nA−B < −0,2 V → RO = 0", 8.2, color="#444")
t(125, 66.5, "nadajnik\nDI → A/B\ntylko gdy DE = 1", 8.2, color="#444")
YL = {"RO": 92, "RE": 82, "DE": 72, "DI": 62}
for nazwa, n in (("RO", "1"), ("RE", "2"), ("DE", "3"), ("DI", "4")):
    y = YL[nazwa]; linia([(108, y), (112, y)], CZ, 2); t(113.5, y, f"{n} {nazwa}", 9.5, ha="left", weight="bold")
YR = {"VCC": 92, "B": 82, "A": 72, "GND": 62}
for nazwa, n in (("VCC", "8"), ("B", "7"), ("A", "6"), ("GND", "5")):
    y = YR[nazwa]; linia([(138, y), (142, y)], CZ, 2); t(136.5, y, f"{nazwa} {n}", 9.5, ha="right", weight="bold")
linia([(142, 92), (146, 92), (146, 104)], ZAS)
linia([(142, 62), (146, 62), (146, 44)], CZ)

# listwa do procesora
t(78, 100.8, "listwa do\nprocesora", 9, color=NIEB)
for y, nazwa in ((96, "VCC"), (92 - 0, "TXD"), (77, "EN"), (62, "RXD"), (50, "GND")):
    pass
pin(80, 97, 1.6); t(77.4, 97, "VCC", 10, ha="right", weight="bold"); linia([(80, 97), (86, 97), (86, 104)], ZAS)
pin(80, 92, 1.6); t(77.4, 92, "TXD", 10, ha="right", weight="bold"); linia([(80, 92), (108, 92)], SYG)
t(94, 94.2, "RO → TXD → pin TX2 (GPIO17) procesora", 8.4, color=SYG)
pin(80, 77, 1.6); t(77.4, 77, "EN", 10, ha="right", weight="bold"); linia([(80, 77), (98, 77)], SYG)
pin(80, 62, 1.6); t(77.4, 62, "RXD", 10, ha="right", weight="bold"); linia([(80, 62), (108, 62)], SYG)
t(94, 59.8, "RXD → DI ← pin RX2 (GPIO16) procesora", 8.4, color=SYG)
pin(80, 50, 1.6); t(77.4, 50, "GND", 10, ha="right", weight="bold"); linia([(80, 50), (86, 50), (86, 44)], CZ)

# wezel RE/DE: EN -> (98,77) -> pion x=104 -> RE (82) i DE (72)
linia([(98, 77), (104, 77)], SYG); linia([(104, 82), (104, 72)], SYG)
linia([(104, 82), (108, 82)], SYG); linia([(104, 72), (108, 72)], SYG)
ax.add_patch(Circle((98, 77), 1.0, fc=SYG, ec=SYG, zorder=5))
t(96.5, 74.4, "węzeł RE/DE", 9.5, color=SYG, weight="bold", ha="right")
# 103 z wezla do VCC (krotka odnoga, zeby nie ciac linii RO)
rez_pion(98, 77, 88, "103\n10 kΩ", side="left")
t(98, 89.6, "▲ 3,3 V", 8.5, color=ZAS)
t(100.6, 85.5, "podciąga węzeł\ndo góry", 7.8, ha="left", color="#555")
# drut naprawczy
linia([(98, 77), (98, 44)], NAPR, 2.8, ls="--")
ax.add_patch(FancyBboxPatch((84, 65.5), 22.5, 6.2, boxstyle="round,pad=0.3", fc="#f5eefa", ec=NAPR, lw=1.5, zorder=5))
t(95.2, 68.6, "DRUT NAPRAWCZY: węzeł → masa\n(pole dalej od T / końcówka 103 / pin EN)", 8, color=NAPR, weight="bold")

# strona magistrali
t(168, 100.8, "listwa\nmagistrali", 9, color=NIEB)
pin(164, 82, 1.6); t(166.4, 82, "B (czerwona)", 9.5, ha="left", weight="bold", color=BUS)
pin(164, 72, 1.6); t(166.4, 72, "A (czarna)", 9.5, ha="left", weight="bold", color=BUS)
pin(164, 50, 1.6); t(166.4, 50, "GND (biała)", 9.5, ha="left", weight="bold")
linia([(142, 82), (164, 82)], BUS); linia([(142, 72), (164, 72)], BUS); linia([(164, 50), (160, 50), (160, 44)], CZ)
rez_pion(159, 72, 82, "121\n120 Ω", side="right")
rez_pion(152, 82, 104, "472\n4,7 kΩ", side="right")
rez_pion(155, 44, 72, "472\n4,7 kΩ", side="right")
t(74, 37.5, "Dioda zasilania: 102 (1 kΩ) + LED między 3,3 V a masą.\nŚwieci już od ~2 V, więc nie dowodzi, że zasilanie jest dobre.", 8.2, color="#555", ha="left")
t(122, 37.5, "Polaryzacja (472): jedna linia do 3,3 V, druga do masy, w partiach bywa odwrotnie.\n4,7 kΩ = dobrze.  470 Ω (napis 471) = za mocno, taki moduł nie odbiera Gree.", 8.2, color="#555", ha="left")

# ═══════════════ 3. CO Z TEGO WYNIKA ═══════════════
ax.add_patch(FancyBboxPatch((8, 1), 168, 19.3, boxstyle="round,pad=0.5", fc="#fff8f0", ec=UWAGA, lw=2, zorder=1))
t(92, 19.0, "3. Co z tego wynika", 12, weight="bold", color=UWAGA)
punkty = [
    "RE (nóżka 2) i DE (nóżka 3) są spięte i wychodzą na pin EN. Ten jeden węzeł decyduje o wszystkim: WYSOKO = nadajnik włączony, odbiornik wyłączony (moduł nie odbiera i zakłóca magistralę); NISKO = odbiornik włączony, nadajnik wyłączony (tego chcemy).",
    "Rezystor 103 (10 kΩ) sam z siebie podciąga węzeł do 3,3 V, więc moduł prosto z paczki NIE odbiera. Pin D4 procesora powinien ściągać węzeł w dół, ale na naszych płytkach nie polegamy na tym: drut z węzła do masy załatwia to na stałe (przez 103 płynie 0,33 mA, bez znaczenia).",
    "Drut można przylutować w dowolnym punkcie węzła: pole dalej od T, końcówka 103 bliżej T, pin EN listwy. Punktów zasilania (pole bliżej T, końcówka 103 dalej od T, pin VCC) NIE wolno łączyć z masą: to zwarcie 3,3 V, port USB laptopa się wyłącza.",
    "Pomiary omomierzem, moduł bez zasilania: punkt ↔ pin EN: 0 Ω = węzeł, ≈10 kΩ = zasilanie | po naprawie pin EN ↔ pin GND: 0 Ω, pin VCC ↔ pin GND: nie zero | A ↔ B: ≈120 Ω | A/B ↔ masa i ↔ VCC: ≈4,7 kΩ (470 Ω = zła partia, 0 Ω = zwarcie) | TXD ↔ masa: nie zero.",
    "Test /diag z firmware sprawdza tylko wnętrze scalaka (DI → A/B → RO): nie widzi listew, przewodów, wtyczki ani wartości rezystorów. O odbiorze rozstrzyga wyłącznie licznik ramek na klimie.",
]
y = 16.8
for p in punkty:
    linie = textwrap.wrap(p, 185)
    for i, l in enumerate(linie):
        t(11, y, ("•  " if i == 0 else "    ") + l, 8.6, ha="left")
        y -= 1.5
    y -= 0.45

fig.savefig(OUT + ".png", dpi=160, facecolor="white")
fig.savefig(OUT + ".pdf", facecolor="white")
print("OK:", OUT + ".png / .pdf")
