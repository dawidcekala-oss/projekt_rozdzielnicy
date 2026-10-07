# Pomiar stalowego haka na zdjęciu porównawczym (stal położona na kartonie +4 W BOK).
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

im = np.asarray(Image.open("../zdjęcia/porownanie/stal_na_kartonie_bok+4.jpg").convert("RGB")).astype(float)
sat = im.max(axis=2) - im.min(axis=2)
br = im.mean(axis=2)
stal = (sat < 30) & (br > 80) & (br < 180)
stal = ndi.binary_opening(stal, iterations=2)
lab, n = ndi.label(stal)
sizes = ndi.sum(stal, lab, range(1, n + 1))
glowny = lab == (1 + int(np.argmax(sizes)))
glowny = ndi.binary_closing(glowny, iterations=4)        # zamyka ciemne krawędzie z nalotem
glowny = ndi.binary_fill_holes(glowny | ~ndi.binary_dilation(glowny, iterations=0)) if False else glowny
Image.fromarray((glowny * 255).astype(np.uint8)).save("zoom/maska_stal.png")
ys, xs = np.nonzero(glowny)
print("stal bbox x", xs.min(), xs.max(), "y", ys.min(), ys.max())
# otwór kwadratowy = dziura w masce w środkowej części
dziury = ndi.binary_fill_holes(glowny) & ~glowny
lab2, n2 = ndi.label(dziury)
s2 = ndi.sum(dziury, lab2, range(1, n2 + 1))
otw = lab2 == (1 + int(np.argmax(s2)))
oy, ox = np.nonzero(otw)
print("otwor bbox x", ox.min(), ox.max(), "y", oy.min(), oy.max(), "srodek", ox.mean(), oy.mean())

# --- brzeg maski
brzeg = glowny & ~ndi.binary_erosion(glowny)
by, bx = np.nonzero(brzeg)
cx0, cy0 = ox.mean(), oy.mean()

def fit_circle(x, y):
    A = np.c_[2 * x, 2 * y, np.ones_like(x)]
    b = x ** 2 + y ** 2
    (a, c, d), *_ = np.linalg.lstsq(A, b, rcond=None)
    return a, c, np.sqrt(d + a ** 2 + c ** 2)

# tarcza: zewnętrzny brzeg w dolnej-lewej ćwiartce zdjęcia (poza otworem)
sel = (by > cy0 + 20) & (bx < cx0 + 120) & (np.hypot(bx - cx0, by - cy0) > 110)
ccx, ccy, R = fit_circle(bx[sel].astype(float), by[sel].astype(float))
res = np.hypot(bx[sel] - ccx, by[sel] - ccy) - R
print(f"tarcza: srodek ({ccx:.1f},{ccy:.1f}) R={R:.1f}px  rozrzut {res.std():.2f}px  punktow {sel.sum()}")
print(f"srodek otworu ({cx0:.1f},{cy0:.1f}) -> przesuniecie {ccx-cx0:.1f},{ccy-cy0:.1f}px")

ppm = R / 10.0  # px na mm (tarcza R10)
print(f"skala z tarczy R10: {ppm:.2f} px/mm")
X0, Y0 = ccx, ccy
def mm(v): return v / ppm

# szerokość całkowita (czubek języka .. prawa krawędź ramienia)
print(f"szerokosc: {mm(xs.max()-xs.min()):.2f} mm  (suwmiarka 19,7)")
print(f"os -> prawa krawedz ramienia: {mm(xs.max()-X0):.2f}  os -> czubek jezyka: {mm(X0-xs.min()):.2f}")
print(f"os -> zewn. krawedz jezyka (dol w ukladzie haka): {mm(Y0-ys.min()):.2f}")
print(f"os -> skraj tarczy: {mm(ys.max()-Y0):.2f}")
print(f"dlugosc calkowita: {mm(ys.max()-ys.min()):.2f}")
# wewnętrzna (wklęsła) krawędź języka: dla kolumn w obszarze języka pierwszy piksel "nie-stal" pod językiem
for x in range(480, 741, 20):
    col = glowny[:, x]
    top = np.argmax(col)                      # zewn. krawędź języka
    y = top
    while y < col.size and col[y]:
        y += 1
    print(f"  x={mm(x-X0):6.2f} mm: zewn {mm(Y0-top):6.2f}  wewn {mm(Y0-y):6.2f}  grubosc {mm(y-top):5.2f}")
# krawędź wewnętrzna ramienia (od strony gardła) na kilku wysokościach
for yy in range(500, 641, 20):
    row = glowny[yy, :]
    xr = np.nonzero(row)[0]
    print(f"  y={mm(Y0-yy):6.2f} mm: ramie od x={mm(xr.min()-X0):6.2f} do {mm(xr.max()-X0):6.2f}")
