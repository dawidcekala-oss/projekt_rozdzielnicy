# -*- coding: utf-8 -*-
"""Generator haka zamka szafy AmperePoint.

Geometria bazowa = 标准锁钩 (hak standardowy) z pliku dostawcy hook.dwg,
odczytana w układzie osi obrotu (0,0 = środek otworu kwadratowego 7,2 mm).

Dwa parametry wydłużenia:
  a — o ile przesunąć język DALEJ OD OSI (cała część poniżej tarczy w dół);
      a = 1,5 odtwarza wariant dostawcy 整体加长40 (długość 40)
  b — o ile wysunąć CZUBEK JĘZYKA w bok (od ramienia na zewnątrz);
      b = 3 odtwarza wariant dostawcy 锁舌加长3mm
Wklęsła krawędź języka zachowuje strzałkę 1,027 mm (tak zrobił dostawca w wariancie 3).

Wyjście:
  ../cad/hak_<wariant>.dxf  (+ .dwg AutoCAD 2000 przez ODA File Converter)  — do edycji w LibreCAD / wysyłki do fabryki
  ../cad/hak_wszystkie_warianty.dxf
  ../rysunki/hak_warianty.pdf                          — arkusz z wymiarami i porównaniem
  ../druk/hak_szablon_1do1_A4.pdf                      — szablon do wycięcia, skala 1:1
"""
import math
import os
import subprocess
import datetime
import textwrap

import ezdxf
from ezdxf import path as ezpath
from ezdxf.math import Vec2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

plt.rcParams["font.family"] = ["Arial", "Segoe UI Symbol", "Microsoft YaHei"]
plt.rcParams["pdf.fonttype"] = 42

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAD = os.path.join(ROOT, "cad")
RYS = os.path.join(ROOT, "rysunki")
DRUK = os.path.join(ROOT, "druk")
for d in (CAD, RYS, DRUK):
    os.makedirs(d, exist_ok=True)
ODA = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ODA_extract", "ODAFileConverter.exe")

GRUBOSC = 1.5          # mm, zmierzona na haku w szafie (plik dostawcy podaje 2,0)
KWADRAT = 7.2          # mm, otwór na trzpień
STRZALKA = 1.027       # mm, wklęsłość krawędzi języka
B90 = math.tan(math.radians(90) / 4)      # 0,4142 — łuk 90°
B270 = math.tan(math.radians(270) / 4)    # 2,4142 — łuk 270° (tarcza R10)
DZIS = datetime.date.today().isoformat()

# (kod pliku, a, b, opis do CAD — bez polskich znaków)
WARIANTY = [
    ("obecny", 0.0, 0.0, "obecny ksztalt (kontrolny)"),
    ("os+1.5", 1.5, 0.0, "jezyk 1,5 mm dalej od osi (= dostawca 40)"),
    ("os+3", 3.0, 0.0, "jezyk 3 mm dalej od osi"),
    ("bok+3", 0.0, 3.0, "czubek jezyka 3 mm dalej w bok (= dostawca 3mm)"),
    ("bok+5", 0.0, 5.0, "czubek jezyka 5 mm dalej w bok"),
    ("os+1.5_bok+3", 1.5, 3.0, "jezyk 1,5 mm dalej od osi i 3 mm dalej w bok"),
]
# wydruk „+4 mm” (2026-10-07): oba kierunki + obecny do porównania
WARIANTY_4 = [
    WARIANTY[0],
    ("os+4", 4.0, 0.0, "jezyk 4 mm dalej od osi"),
    ("bok+4", 0.0, 4.0, "czubek jezyka 4 mm dalej w bok"),
]
ETYKIETA = {"obecny": "OBECNY", "os+1.5": "+1,5 OD OSI", "os+3": "+3 OD OSI", "bok+3": "+3 W BOK",
            "bok+5": "+5 W BOK", "os+1.5_bok+3": "+1,5 OD OSI\n+3 W BOK",
            "os+4": "+4 OD OSI", "bok+4": "+4 W BOK"}
OPIS_PL = {"os+4": "język 4 mm dalej od osi\n(cały hak dłuższy o 4 mm)",
           "bok+4": "czubek języka 4 mm dalej w bok\n(hak szerszy o 4 mm)",
           "obecny": "nic — kształt obecnego haka (do porównania)",
           "os+1.5": "język 1,5 mm dalej od osi (= wariant dostawcy „40”)",
           "os+3": "język 3 mm dalej od osi",
           "bok+3": "czubek języka 3 mm dalej w bok (= wariant dostawcy „3 mm”)",
           "bok+5": "czubek języka 5 mm dalej w bok",
           "os+1.5_bok+3": "język 1,5 mm dalej od osi i czubek 3 mm dalej w bok"}


def kontur(a, b):
    """Wierzchołki (x, y, bulge) zamkniętej polilinii, obieg zgodny z ruchem wskazówek zegara."""
    yb = -28.5 - a          # spód języka
    yt = -23.7 - a          # wewnętrzna (wklęsła) krawędź języka, na końcach
    xl = -10.0 - b          # czubek języka
    cieciwa = (5.0) - (xl + 1.0)
    return [
        (10.0, 0.0, 0.0),
        (10.0, -24.5 - a, -B90),            # R4
        (6.0, yb, 0.0),
        (xl + 1.0, yb, -B90),               # R1
        (xl, yb + 1.0, 0.0),
        (xl, yt - 1.0, -B90),               # R1
        (xl + 1.0, yt, 2 * STRZALKA / cieciwa),   # wklęsła krawędź języka
        (5.0, yt, 0.0),
        (5.0, -22.0 - a, 0.0),              # stopień 1,7
        (1.0, -22.0 - a, -B90),             # R1
        (0.0, -21.0 - a, 0.0),
        (0.0, -10.0, -B270),                # tarcza R10 wokół osi
    ]


def kwadrat():
    h = KWADRAT / 2
    return [(-h, -h), (h, -h), (h, h), (-h, h)]


def splaszcz(pts):
    """Kontur jako lista punktów (do rysowania w matplotlib i liczenia promienia)."""
    doc = ezdxf.new()
    pl = doc.modelspace().add_lwpolyline(pts, format="xyb", close=True)
    return [Vec2(v.x, v.y) for v in ezpath.make_path(pl).flattening(0.002)]


def parametry(a, b):
    p = splaszcz(kontur(a, b))
    return dict(
        dlugosc=10.0 + 28.5 + a,
        szerokosc=20.0 + b,
        os_jezyk=23.7 + a,
        promien=max(v.magnitude for v in p),
    )


# ------------------------------------------------------------------ DXF / DWG
def nowy_dxf():
    doc = ezdxf.new("R2000", setup=["linetypes"], units=4)
    doc.header["$MEASUREMENT"] = 1
    doc.styles.get("Standard").dxf.font = "simplex.shx"   # zna ją AutoCAD i LibreCAD
    warstwy = [("KONTUR", 7, 50), ("OTWOR", 7, 50), ("OSIE", 1, 18), ("WYMIARY", 3, 18),
               ("OPISY", 2, 18), ("ZAKRES_OBROTU", 8, 13)]
    for n, kol, lw in warstwy:
        doc.layers.add(n, color=kol, lineweight=lw)
    doc.layers.get("OSIE").dxf.linetype = "CENTER"
    doc.layers.get("ZAKRES_OBROTU").dxf.linetype = "DASHED"
    doc.dimstyles.new("HAK", dxfattribs=dict(
        dimtxsty="Standard", dimtxt=2.5, dimasz=2.0, dimexe=1.0, dimexo=0.8, dimgap=0.8,
        dimdec=1, dimdsep=ord(","), dimzin=8, dimtad=1, dimlunit=2, dimscale=1.0,
        dimtih=0, dimtoh=0, dimclrd=3, dimclre=3, dimclrt=3))
    return doc


def rysuj_wariant(msp, kod, a, b, opis, dx=0.0, dy=0.0, z_wymiarami=True):
    o = Vec2(dx, dy)
    pts = [(x + dx, y + dy, bl) for x, y, bl in kontur(a, b)]
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "KONTUR"})
    msp.add_lwpolyline([(x + dx, y + dy) for x, y in kwadrat()], close=True, dxfattribs={"layer": "OTWOR"})
    msp.add_line((dx - 14 - b, dy), (dx + 14, dy), dxfattribs={"layer": "OSIE"})
    msp.add_line((dx, dy + 14), (dx, dy - 33 - a), dxfattribs={"layer": "OSIE"})
    par = parametry(a, b)
    msp.add_circle((dx, dy), par["promien"], dxfattribs={"layer": "ZAKRES_OBROTU"})
    if z_wymiarami:
        d = dict(dimstyle="HAK", dxfattribs={"layer": "WYMIARY"})
        yb, yt, xl = -28.5 - a, -23.7 - a, -10.0 - b
        msp.add_linear_dim(base=(dx + 17, dy), p1=(dx + 10, dy + 10), p2=(dx + 10, dy + yb), angle=90, **d).render()
        msp.add_linear_dim(base=(dx, dy + yb - 6), p1=(dx + xl, dy + yb), p2=(dx + 10, dy + yb), **d).render()
        msp.add_linear_dim(base=(dx + xl - 6, dy), p1=(dx, dy), p2=(dx + xl, dy + yt), angle=90, **d).render()
        msp.add_linear_dim(base=(dx + xl - 6, dy), p1=(dx + xl, dy + yt), p2=(dx + xl, dy + yb), angle=90, **d).render()
        msp.add_linear_dim(base=(dx, dy + 13), p1=(dx - 3.6, dy + 3.6), p2=(dx + 3.6, dy + 3.6), **d).render()
        msp.add_linear_dim(base=(dx + 5, dy - 17), p1=(dx, dy - 15), p2=(dx + 10, dy - 15), **d).render()
        msp.add_radius_dim(center=(dx, dy), radius=10, angle=135, **d).render()
        msp.add_radius_dim(center=(dx + 6, dy - 24.5 - a), radius=4, angle=-45, **d).render()
    t = dict(layer="OPISY", height=2.5)
    msp.add_text(f"HAK {kod}: {opis}", dxfattribs=t).set_placement((dx - 22, dy - 48 - a))
    msp.add_text(f"stal nierdzewna / stainless steel {str(GRUBOSC).replace('.', ',')} mm",
                 dxfattribs=t).set_placement((dx - 22, dy - 52 - a))
    msp.add_text(f"zakres obrotu R{par['promien']:.1f}".replace(".", ","),
                 dxfattribs=dict(layer="ZAKRES_OBROTU", height=2.0)).set_placement((dx - 22, dy - 56 - a))


def do_dwg(dxf_paths):
    """DXF -> DWG (AutoCAD 2000, jak plik dostawcy) przez ODA File Converter; jedno wywołanie na całą paczkę."""
    import shutil, tempfile
    tmp_in, tmp_out = tempfile.mkdtemp(), tempfile.mkdtemp()
    for p in dxf_paths:
        shutil.copy(p, tmp_in)
    subprocess.run([ODA, tmp_in, tmp_out, "ACAD2000", "DWG", "0", "1", "*.DXF"], capture_output=True)
    wynik = []
    for p in dxf_paths:
        nazwa = os.path.splitext(os.path.basename(p))[0] + ".dwg"
        src = os.path.join(tmp_out, nazwa)
        ok = os.path.exists(src) and os.path.getsize(src) > 0
        if ok:
            os.replace(src, os.path.join(os.path.dirname(p), nazwa))
        wynik.append((nazwa, ok))
    shutil.rmtree(tmp_in, ignore_errors=True)
    shutil.rmtree(tmp_out, ignore_errors=True)
    return wynik


def zapisz_cad():
    pliki = []
    for kod, a, b, opis in WARIANTY + [w for w in WARIANTY_4 if w not in WARIANTY]:
        doc = nowy_dxf()
        rysuj_wariant(doc.modelspace(), kod, a, b, opis)
        p = os.path.join(CAD, f"hak_{kod}.dxf")
        doc.saveas(p)
        pliki.append(p)
    doc = nowy_dxf()
    for i, (kod, a, b, opis) in enumerate(WARIANTY):
        rysuj_wariant(doc.modelspace(), kod, a, b, opis, dx=i * 70.0)
    p = os.path.join(CAD, "hak_wszystkie_warianty.dxf")
    doc.saveas(p)
    pliki.append(p)
    return do_dwg(pliki)


# ------------------------------------------------------------------ rysunek PDF
KOLORY = {"obecny": "#222222", "os+1.5": "#1f5fbf", "os+3": "#0d3b80", "bok+3": "#c0392b",
          "bok+5": "#7b1d12", "os+1.5_bok+3": "#7d3c98"}


def fmt(v):
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def wymiar(ax, p1, p2, off, side, color="#555", fs=8):
    (x1, y1), (x2, y2) = p1, p2
    kw = dict(color=color, lw=0.5)
    if side == "h":
        ax.plot([x1, x1], [y1, off - 0.8 if off < y1 else off + 0.8], **kw)
        ax.plot([x2, x2], [y2, off - 0.8 if off < y2 else off + 0.8], **kw)
        ax.annotate("", (x1, off), (x2, off), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.5,
                                                               shrinkA=0, shrinkB=0, mutation_scale=6))
        ax.text((x1 + x2) / 2, off + 0.4, fmt(abs(x2 - x1)), ha="center", va="bottom", fontsize=fs, color=color)
    else:
        ax.plot([x1, off + 0.8 if off > x1 else off - 0.8], [y1, y1], **kw)
        ax.plot([x2, off + 0.8 if off > x2 else off - 0.8], [y2, y2], **kw)
        ax.annotate("", (off, y1), (off, y2), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.5,
                                                               shrinkA=0, shrinkB=0, mutation_scale=6))
        ax.text(off + (0.5 if off > 0 else -0.5), (y1 + y2) / 2, fmt(abs(y2 - y1)),
                ha="left" if off > 0 else "right", va="center", fontsize=fs, color=color)


def rysuj_mpl(ax, a, b, color, lw=1.4, fill=True, ls="-"):
    p = splaszcz(kontur(a, b))
    xs, ys = [v.x for v in p] + [p[0].x], [v.y for v in p] + [p[0].y]
    if fill:
        ax.fill(xs, ys, color=color, alpha=0.10, lw=0)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls)
    k = kwadrat() + [kwadrat()[0]]
    if fill:
        ax.fill([q[0] for q in k], [q[1] for q in k], color="white")
    ax.plot([q[0] for q in k], [q[1] for q in k], color=color, lw=lw * 0.7)


def arkusz_rysunkowy():
    A3 = (16.54, 11.69)
    fig = plt.figure(figsize=A3)
    fig.text(0.03, 0.955, "Hak zamka szafy AmperePoint — warianty wydłużenia do próby", fontsize=19, weight="bold")
    fig.text(0.03, 0.915, "Baza: hak standardowy z pliku dostawcy (标准锁钩). Rysunki na wspólnej osi obrotu (środek otworu "
                          "kwadratowego 7,2 mm). Stal nierdzewna 1,5 mm (zmierzona; plik dostawcy podaje 2,0).\n"
                          "a = język dalej od osi, b = czubek języka dalej w bok. Szara przerywana linia: okrąg, "
                          "który zatacza najdalszy punkt haka przy obrocie (ważne przy sprawdzaniu, czy hak o coś nie zawadzi).",
                 fontsize=11, va="top")
    n = len(WARIANTY)
    pw = 0.94 / n
    for i, (kod, a, b, opis) in enumerate(WARIANTY):
        ax = fig.add_axes([0.03 + i * pw, 0.33, pw * 0.98, 0.52])
        ax.set_aspect("equal")
        ax.set_xlim(-25, 22)
        ax.set_ylim(-46, 20)
        ax.axis("off")
        c = KOLORY[kod]
        par = parametry(a, b)
        ax.add_patch(plt.Circle((0, 0), par["promien"], fill=False, ls=(0, (3, 2)), color="#aaa", lw=0.6))
        ax.plot([-14 - b, 14], [0, 0], color="#999", lw=0.4, ls=(0, (6, 2, 1, 2)))
        ax.plot([0, 0], [-33 - a, 13], color="#999", lw=0.4, ls=(0, (6, 2, 1, 2)))
        if kod != "obecny":
            rysuj_mpl(ax, 0, 0, "#999", lw=0.6, fill=False, ls=(0, (2, 1.5)))
        rysuj_mpl(ax, a, b, c)
        yb, yt, xl = -28.5 - a, -23.7 - a, -10.0 - b
        wymiar(ax, (10, 10), (10, yb), 15.5, "v")
        wymiar(ax, (xl, yb), (10, yb), yb - 4, "h")
        wymiar(ax, (xl, 0), (xl, yt), xl - 4, "v", color="#7a5c00")
        wymiar(ax, (xl, yt), (xl, yb), xl - 4, "v", color="#7a5c00")
        ax.text(0, 13, ETYKIETA[kod], ha="center", va="bottom", fontsize=13, weight="bold", color=c,
                linespacing=1.0)
        ax.text(0, -40, f"a = {fmt(a)}   b = {fmt(b)}", ha="center", va="top", fontsize=10, color="#333")
        ax.text(0, -43.5, f"zakres obrotu R{fmt(par['promien'])}", ha="center", va="top", fontsize=9, color="#777")

    # tabela
    ax = fig.add_axes([0.03, 0.05, 0.94, 0.24])
    ax.axis("off")
    kol = ["Wariant", "Co zmienione", "Długość całkowita", "Szerokość", "Oś → wklęsła krawędź języka",
           "Promień zakresu obrotu", "Zmiana promienia"]
    r0 = parametry(0, 0)["promien"]
    wiersze = []
    for kod, a, b, opis in WARIANTY:
        p = parametry(a, b)
        co = OPIS_PL[kod]
        wiersze.append([ETYKIETA[kod].replace("\n", ", "), co, fmt(p["dlugosc"]), fmt(p["szerokosc"]), fmt(p["os_jezyk"]),
                        fmt(p["promien"]), "—" if kod == "obecny" else "+" + fmt(p["promien"] - r0)])
    tb = ax.table(cellText=wiersze, colLabels=kol, loc="upper left", cellLoc="center",
                  colWidths=[0.14, 0.33, 0.10, 0.07, 0.14, 0.12, 0.10])
    tb.auto_set_font_size(False)
    tb.set_fontsize(10)
    tb.scale(1, 1.55)
    for (r, c_), cell in tb.get_celld().items():
        cell.set_edgecolor("#bbb")
        if r == 0:
            cell.set_facecolor("#eeeeee")
            cell.set_text_props(weight="bold")
        if c_ == 1 and r > 0:
            cell.set_text_props(ha="left")
            cell._loc = "left"
    fig.text(0.97, 0.015, f"hak_generator.py — {DZIS} — wymiary w mm", ha="right", fontsize=8, color="#999")
    return fig


# ------------------------------------------------------------------ szablon 1:1
def szablon_1do1(warianty=WARIANTY):
    W, H = 210.0, 297.0
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(15, 284, "Hak zamka — szablon do wycięcia, SKALA 1:1", fontsize=14, weight="bold", va="top")
    ax.text(15, 277, "Drukować w ROZMIARZE RZECZYWISTYM (100 %), bez „dopasuj do strony”. Przed cięciem zmierzyć "
                     "suwmiarką\nkreskę kontrolną na dole: ma mieć 100,0 mm (dopuszczalne ±0,5). "
                     "Ciąć po zewnętrznej stronie linii.\nKwadratowy otwór 7,2 mm wyciąć ciasno — ma siedzieć na "
                     "trzpieniu zamka bez luzu, tak jak stalowy hak.", fontsize=8.5, va="top", linespacing=1.4)
    # siatka 3 × 2 (albo jeden rząd, gdy wariantów jest najwyżej 3)
    kol_x = [45, 107, 169]
    rzad_y = [212, 112] if len(warianty) > 3 else [175]
    for i, (kod, a, b, opis) in enumerate(warianty):
        cx, cy = kol_x[i % 3] + 3, rzad_y[i // 3]
        if len(warianty) <= 3:
            par = parametry(a, b)
            ax.text(cx - 1, cy - 50 - a, f"długość {fmt(par['dlugosc'])} mm\nszerokość {fmt(par['szerokosc'])} mm",
                    ha="center", fontsize=7, va="top", color="#444")
        p = splaszcz(kontur(a, b))
        xs, ys = [cx + v.x for v in p] + [cx + p[0].x], [cy + v.y for v in p] + [cy + p[0].y]
        ax.plot(xs, ys, color="black", lw=0.35)
        k = kwadrat() + [kwadrat()[0]]
        ax.plot([cx + q[0] for q in k], [cy + q[1] for q in k], color="black", lw=0.35)
        ax.plot([cx - 2, cx + 2], [cy, cy], color="black", lw=0.2)
        ax.plot([cx, cx], [cy - 2, cy + 2], color="black", lw=0.2)
        ax.text(cx - 1, cy + 14, ETYKIETA[kod], ha="center", va="bottom", fontsize=12, weight="bold",
                linespacing=1.0)
        ax.text(cx - 1, cy - 36 - a, OPIS_PL[kod].replace(" (", "\n("), ha="center", fontsize=7, va="top")
        # opis na samym haku (pod otworem), żeby po wycięciu się nie pomylić
        ax.text(cx + 1.2, cy - 6.6, ETYKIETA[kod].replace(" ", ""), ha="center", va="center",
                fontsize=3.6, color="#555", linespacing=1.0)
    # kreska kontrolna 100 mm + kwadrat 40 mm
    x0, y0 = 15, 30
    ax.plot([x0, x0 + 100], [y0, y0], color="black", lw=0.5)
    for k in range(0, 101, 10):
        h = 4 if k % 50 == 0 else 2.5
        ax.plot([x0 + k, x0 + k], [y0, y0 + h], color="black", lw=0.4)
        ax.text(x0 + k, y0 + 5, str(k), ha="center", fontsize=6)
    ax.text(x0, y0 - 4, "kreska kontrolna 100 mm", fontsize=8, va="top")
    ax.add_patch(plt.Rectangle((150, 15), 40, 40, fill=False, lw=0.5))
    ax.text(170, 35, "40 × 40 mm", ha="center", va="center", fontsize=8)
    ax.text(15, 10, f"hak_generator.py — {DZIS}", fontsize=6, color="#888")
    return fig


def strona_proby(warianty=WARIANTY):
    """Druga strona szablonu: przebieg próby i tabela do wpisania wyników."""
    fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 210)
    ax.set_ylim(0, 297)
    ax.axis("off")
    ax.text(15, 284, "Próba wyciętych haków — przebieg i wyniki", fontsize=14, weight="bold", va="top")
    kroki = [
        ("Materiał.", "Twardy plastik ok. 1,5 mm (płytka PCV, okładka segregatora PP sklejona w 2–3 warstwy) "
                      "albo gruba tektura. Miękki karton ugnie się przy dociskaniu drzwi i zafałszuje wynik."),
        ("Kontrola wydruku.", "Kreska na stronie 1 ma 100,0 mm. Wycięty OBECNY przyłożyć do stalowego haka — "
                              "obrysy mają się pokryć (różnica poniżej 0,5 mm). Jeśli się nie pokrywają: stop, "
                              "dać znać (zły druk albo w szafie jest inny hak niż w pliku dostawcy)."),
        ("Najpierw OBECNY.", "Wycięty obecny hak MUSI odtworzyć usterkę (punkt C poniżej: drzwi się otwierają). "
                             "Jeśli nie odtwarza — próba z pozostałymi jest niemiarodajna (za miękki materiał "
                             "albo inne ułożenie niż stalowego haka)."),
        ("Montaż.", "Zdjąć stalowy hak (śruba na trzpieniu), założyć wycięty w tym samym ułożeniu, "
                    "dokręcić lekko, żeby się nie pogiął."),
    ]
    y = 270
    for i, (tyt, txt) in enumerate(kroki, 1):
        ax.text(15, y, f"{i}. {tyt}", fontsize=9, weight="bold", va="top")
        y -= 5
        zawiniety = textwrap.fill(txt, 105)
        ax.text(19, y, zawiniety, fontsize=8.5, va="top")
        y -= 4.6 * (zawiniety.count("\n") + 1) + 3
    ax.text(15, y, "Dla każdego wyciętego haka sprawdzić:", fontsize=9, weight="bold", va="top")
    y -= 6
    testy = [
        ("A", "Drzwi otwarte: gałka w obie skrajne pozycje — hak o nic nie ociera?"),
        ("B", "Zamek odblokowany: drzwi zamykają się bez oporu (hak wchodzi w otwór szafy)?"),
        ("C", "Zablokowany, zły kod, gałka w skrajnej pozycji zgodnie z ruchem wskazówek zegara, "
              "lekki docisk drzwi w dół i pociągnięcie — drzwi mają się NIE otworzyć."),
        ("D", "Dobry kod: drzwi otwierają się normalnie (dłuższy hak nie może zaczepiać przy otwieraniu)."),
    ]
    for lit, txt in testy:
        ax.text(18, y, lit, fontsize=9, weight="bold", va="top")
        ax.text(25, y, textwrap.fill(txt, 100), fontsize=8.5, va="top")
        y -= 4.6 * (textwrap.fill(txt, 100).count("\n") + 1) + 2
    # tabela wyników
    y -= 4
    kol = [("Hak", 38), ("A  nie ociera", 22), ("B  zamyka się", 22), ("C  NIE otwiera się", 26),
           ("D  otwiera kodem", 24), ("Uwagi", 48)]
    x0 = 15
    h = 13
    xs = [x0]
    for _, w in kol:
        xs.append(xs[-1] + w)
    wiersze = [ETYKIETA[k].replace("\n", ", ") for k, *_ in warianty]
    ax.plot([xs[0], xs[-1]], [y, y], color="black", lw=0.6)
    for (n, w), xl in zip(kol, xs):
        ax.text(xl + 1.5, y - 2, n, fontsize=7.5, weight="bold", va="top")
    y_naglowek = y - 9
    ax.plot([xs[0], xs[-1]], [y_naglowek, y_naglowek], color="black", lw=0.6)
    yy = y_naglowek
    for w in wiersze:
        ax.text(xs[0] + 1.5, yy - h / 2, w, fontsize=8, va="center")
        yy -= h
        ax.plot([xs[0], xs[-1]], [yy, yy], color="black", lw=0.4)
    for xl in xs:
        ax.plot([xl, xl], [y, yy], color="black", lw=0.4)
    ax.text(15, yy - 6, "W kolumnach A–D wpisać ✔ / ✘. Zdjęcie wypełnionej tabeli wystarczy — na tej podstawie "
                        "przygotuję rysunek wybranego haka dla fabryki.", fontsize=8, va="top")
    ax.text(15, 10, f"hak_generator.py — {DZIS}", fontsize=6, color="#888")
    return fig


if __name__ == "__main__":
    rap = zapisz_cad()
    for nazwa, ok in rap:
        print("DWG", nazwa, "OK" if ok else "BLAD")
    with PdfPages(os.path.join(RYS, "hak_warianty.pdf")) as pdf:
        f = arkusz_rysunkowy()
        pdf.savefig(f)
        f.savefig(os.path.join(RYS, "hak_warianty.png"), dpi=100)
    with PdfPages(os.path.join(DRUK, "hak_szablon_1do1_A4.pdf")) as pdf:
        f = szablon_1do1()
        pdf.savefig(f)
        f.savefig(os.path.join(DRUK, "hak_szablon_1do1_A4.png"), dpi=150)
        f2 = strona_proby()
        pdf.savefig(f2)
        f2.savefig(os.path.join(DRUK, "hak_proba_strona2.png"), dpi=110)
    with PdfPages(os.path.join(DRUK, "hak_+4mm_szablon_1do1_A4.pdf")) as pdf:
        f = szablon_1do1(WARIANTY_4)
        pdf.savefig(f)
        f.savefig(os.path.join(DRUK, "hak_+4mm_szablon_1do1_A4.png"), dpi=150)
        pdf.savefig(strona_proby(WARIANTY_4))
    for kod, a, b, _ in WARIANTY + WARIANTY_4[1:]:
        p = parametry(a, b)
        print(kod, {k: round(v, 3) for k, v in p.items()})
