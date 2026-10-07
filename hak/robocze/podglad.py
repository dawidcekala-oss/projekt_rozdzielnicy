# -*- coding: utf-8 -*-
"""Podgląd pliku hook.dwg (po konwersji do DXF) bez programu CAD.

Strona 1: arkusz porównawczy trzech wariantów haka z pliku, w układzie
          osi obrotu (środek kwadratowego otworu = 0,0), z polskimi opisami.
Strona 2: wierny render zawartości pliku (tak, jak go narysował dostawca).
"""
import math
import ezdxf
from ezdxf import path as ezpath
from ezdxf.math import Vec2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager as fm

for f in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyh.ttf"):
    try:
        fm.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Arial", "Microsoft YaHei"]
ZH = {"family": "Microsoft YaHei"}

SRC = "hook_oryginal.dxf"
doc = ezdxf.readfile(SRC)
msp = doc.modelspace()

# --- wydobycie wariantów w układzie osi obrotu --------------------------------
polys = [e for e in msp if e.dxftype() == "LWPOLYLINE"]
squares = sorted([p for p in polys if len(p) == 4], key=lambda p: p[0][0])
hooks = sorted([p for p in polys if len(p) > 4], key=lambda p: p[0][0])


def to_axis(entity, center, rot):
    pth = ezpath.make_path(entity)
    pts = [(Vec2(v.x, v.y) - center).rotate_deg(rot) for v in pth.flattening(0.005)]
    return [p.x for p in pts], [p.y for p in pts]


variants = []
for sq, hk in zip(squares, hooks):
    sp = [Vec2(p[0], p[1]) for p in sq.get_points()]
    c = sum(sp, Vec2()) / 4
    ang = math.degrees(math.atan2((sp[1] - sp[0]).y, (sp[1] - sp[0]).x))
    rot = -(ang - round(ang / 90) * 90)
    variants.append(dict(hook=to_axis(hk, c, rot), sq=to_axis(sq, c, rot), rot=rot))

INFO = [
    dict(zh="标准锁钩", pl="1. Hak standardowy", sub="(wariant bazowy z pliku)",
         H=38.5, W=20.0, xl=-10.0, yb=-28.5, yt=-23.7, color="#222222", ls="-"),
    dict(zh="整体加长40", pl="2. Całość wydłużona do 40 mm", sub="(+1,5 mm między osią a językiem)",
         H=40.0, W=20.0, xl=-10.0, yb=-30.0, yt=-25.2, color="#1f5fbf", ls="-"),
    dict(zh="锁舌加长3mm", pl="3. Język wydłużony o 3 mm", sub="(+3 mm w bok, długość bez zmian)",
         H=38.515, W=23.0, xl=-13.0, yb=-28.515, yt=-23.715, color="#c0392b", ls="-"),
]


def fmt(v):
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def dim(ax, p1, p2, off, text=None, side="h", color="#555555", fs=9):
    """Wymiar liniowy: side='h' poziomy (odsunięty w y o off), 'v' pionowy (odsunięty w x)."""
    (x1, y1), (x2, y2) = p1, p2
    kw = dict(color=color, lw=0.6)
    if side == "h":
        yd = off
        ax.plot([x1, x1], [y1, yd + (0.8 if yd > y1 else -0.8)], **kw)
        ax.plot([x2, x2], [y2, yd + (0.8 if yd > y2 else -0.8)], **kw)
        ax.annotate("", (x1, yd), (x2, yd), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.6,
                                                             shrinkA=0, shrinkB=0, mutation_scale=7))
        val = abs(x2 - x1)
        ax.text((x1 + x2) / 2, yd + 0.5, text or fmt(val), ha="center", va="bottom", fontsize=fs, color=color)
    else:
        xd = off
        ax.plot([x1, xd + (0.8 if xd > x1 else -0.8)], [y1, y1], **kw)
        ax.plot([x2, xd + (0.8 if xd > x2 else -0.8)], [y2, y2], **kw)
        ax.annotate("", (xd, y1), (xd, y2), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.6,
                                                             shrinkA=0, shrinkB=0, mutation_scale=7))
        val = abs(y2 - y1)
        ax.text(xd + (0.6 if xd > 0 else -0.6), (y1 + y2) / 2, text or fmt(val), ha="left" if xd > 0 else "right",
                va="center", fontsize=fs, color=color, rotation=0)


def axis_cross(ax):
    ax.plot([-13, 13], [0, 0], color="#888", lw=0.5, ls=(0, (8, 2, 1, 2)))
    ax.plot([0, 0], [-34, 13], color="#888", lw=0.5, ls=(0, (8, 2, 1, 2)))


def setup(ax):
    ax.set_aspect("equal")
    ax.set_xlim(-24, 24)
    ax.set_ylim(-44, 17)
    ax.axis("off")


# ============================== STRONA 1 ======================================
A3 = (16.54, 11.69)
fig1 = plt.figure(figsize=A3)
fig1.text(0.03, 0.955, "Hak zamka szafy AmperePoint — co jest w pliku hook.dwg", fontsize=20, weight="bold")
fig1.text(0.03, 0.905, "Plik od dostawcy (opisy po chińsku) zawiera trzy warianty haka. Wszystkie: stal nierdzewna, blacha 2,0 mm "
                       "(不锈钢2.0厚度).\nRysunki ustawione na wspólnej osi obrotu (środek otworu kwadratowego 7,2 mm), "
                       "wymiary w mm odczytane z geometrii pliku, nie z napisów.", fontsize=12)

panel_w, gap, left0 = 0.225, 0.012, 0.03
for i, (v, inf) in enumerate(zip(variants, INFO)):
    ax = fig1.add_axes([left0 + i * (panel_w + gap), 0.36, panel_w, 0.54])
    setup(ax)
    axis_cross(ax)
    hx, hy = v["hook"]
    ax.fill(hx, hy, color=inf["color"], alpha=0.10)
    ax.plot(hx, hy, color=inf["color"], lw=1.6)
    sx, sy = v["sq"]
    ax.fill(sx, sy, color="white")
    ax.plot(sx, sy, color=inf["color"], lw=1.2)
    ax.text(0, 16, inf["pl"], ha="center", va="top", fontsize=14, weight="bold", color=inf["color"])
    ax.text(0, 13.3, inf["zh"], ha="center", va="top", fontsize=11, color=inf["color"], fontdict=ZH)
    # wymiary
    dim(ax, (10, 10), (10, inf["yb"]), 16, side="v")                       # długość całkowita
    dim(ax, (inf["xl"], inf["yb"]), (10, inf["yb"]), inf["yb"] - 4.5, side="h")  # szerokość
    dim(ax, (inf["xl"], 0), (inf["xl"], inf["yt"]), inf["xl"] - 5, side="v", color="#7a5c00")  # oś -> język
    dim(ax, (inf["xl"], inf["yt"]), (inf["xl"], inf["yb"]), inf["xl"] - 5, side="v", color="#7a5c00")
    ax.text(-3.6, 4.6, "□ 7,2", fontsize=9, color="#555")
    ax.text(7.5, 8.5, "R10", fontsize=9, color="#555")
    ax.text(0, -40.5, inf["sub"], ha="center", va="top", fontsize=11, color="#333")

# panel 4: nałożenie
ax = fig1.add_axes([left0 + 3 * (panel_w + gap), 0.36, panel_w, 0.54])
setup(ax)
axis_cross(ax)
for v, inf in zip(variants, INFO):
    hx, hy = v["hook"]
    ax.plot(hx, hy, color=inf["color"], lw=1.4, ls="-" if inf is INFO[0] else (0, (5, 2)))
sx, sy = variants[0]["sq"]
ax.plot(sx, sy, color="#222", lw=1.0)
ax.text(0, 16, "4. Nałożone na siebie", ha="center", va="top", fontsize=14, weight="bold")
ax.text(0, 13.3, "wspólna oś obrotu", ha="center", va="top", fontsize=11)
ax.annotate("+1,5 mm\nw dół", (-4, -29.6), (-21, -37), fontsize=10, color=INFO[1]["color"],
            arrowprops=dict(arrowstyle="->", color=INFO[1]["color"], lw=0.8))
ax.annotate("+3 mm\nw bok", (-12.6, -26), (-23, -18), fontsize=10, color=INFO[2]["color"],
            arrowprops=dict(arrowstyle="->", color=INFO[2]["color"], lw=0.8))
ax.text(0, -40.5, "czarny = standard, przerywane = warianty", ha="center", va="top", fontsize=11, color="#333")

notes = [
    "Brązowe wymiary po lewej: odległość od osi obrotu do wewnętrznej krawędzi języka (tu siedzi krawędź blachy szafy) oraz grubość języka (4,8 mm; w środku ~3,8 mm, bo krawędź jest lekko wklęsła).",
    "Wklęsła krawędź języka nie jest współśrodkowa z osią obrotu: odległość od osi do niej to 25,4 mm przy czubku i 24,2 mm przy ramieniu (wariant 1; w wariancie 2 o 1,5 mm więcej; w wariancie 3: 26,6 → 24,2 mm).",
    "Błędy w pliku dostawcy: wariant 1 jest narysowany obrócony o 0,4°, a jego wymiar „19,56” jest zdjęty z zaokrąglenia — rzeczywista szerokość to 20,0. W wariancie 3 wymiar „22,7” powinien brzmieć 23,0.",
    "Który wariant siedzi dziś w szafach — do sprawdzenia suwmiarką na wyjętym haku: długość całkowita 38,5 czy 40, szerokość 20 czy 23.",
]
for k, n in enumerate(notes):
    fig1.text(0.03, 0.36 - k * 0.04, "• " + n, fontsize=11.5, color="#333", wrap=True)
fig1.text(0.97, 0.015, "Podgląd wygenerowany z hook.dwg (AutoCAD 2000) — 2026-10-07", ha="right", fontsize=8, color="#999")

# ============================== STRONA 2 ======================================
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy

fig2 = plt.figure(figsize=A3)
fig2.text(0.03, 0.955, "Wierny render pliku hook.dwg (jak narysował dostawca)", fontsize=20, weight="bold")
fig2.text(0.03, 0.925, "Trzy warianty leżą w pliku daleko od siebie (x ≈ 170, 1925, 3450 mm), a opisy mają wysokość 80 mm — "
                       "dlatego każdy wycinek pokazany osobno. Tłumaczenie opisów pod spodem.", fontsize=11)
ctx = RenderContext(doc)
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
windows = [((140, 135), (215, 215)), ((1900, 180), (1975, 260)), ((3420, 270), (3495, 345))]
trans = ["标准锁钩 = hak standardowy\n不锈钢2.0厚度 = stal nierdzewna, grubość 2,0",
         "整体加长40 = całość wydłużona, 40\n不锈钢2.0厚度 = stal nierdzewna, grubość 2,0",
         "锁舌加长3mm = język zamka wydłużony o 3 mm\n不锈钢2.0厚度 = stal nierdzewna, grubość 2,0"]
def bez_wielkich_opisow(e):
    # opisy wariantów mają 80 mm wysokości i leżą daleko od rysunków — tłumaczymy je pod spodem
    return not (e.dxftype() == "MTEXT" and e.dxf.char_height > 50)


for i, ((x0, y0), (x1, y1)) in enumerate(windows):
    ax = fig2.add_axes([0.03 + i * 0.32, 0.22, 0.30, 0.66])
    Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(msp, finalize=False, filter_func=bez_wielkich_opisow)
    fig2.set_size_inches(*A3)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig2.text(0.03 + i * 0.32 + 0.15, 0.17, trans[i], ha="center", va="top", fontsize=12)

with PdfPages("../podglad/hook_podglad.pdf") as pdf:
    pdf.savefig(fig1)
    pdf.savefig(fig2)
fig1.savefig("../podglad/hook_podglad.png", dpi=110)
fig2.savefig("hook_render_oryginalu.png", dpi=110)
print("OK")
