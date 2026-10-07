import numpy as np
from PIL import Image
from scipy import ndimage as ndi
exec(open("pomiar_zdjecia.py", encoding="utf-8").read().split("# --- brzeg maski")[0])
pelny = ndi.binary_fill_holes(glowny)
r, g, b_ = im[..., 0], im[..., 1], im[..., 2]
karton = (sat > 22) & (br < 185) & (r > b_ + 15)
karton = ndi.binary_opening(karton, iterations=2)
suma = ndi.binary_fill_holes(ndi.binary_closing(karton | pelny, iterations=3))
lab, n = ndi.label(suma); s = ndi.sum(suma, lab, range(1, n+1)); suma = lab == 1 + int(np.argmax(s))
Image.fromarray((suma*255).astype(np.uint8)).save("zoom/maska_suma.png")
brzeg = suma & ~ndi.binary_erosion(suma)
blisko_stali = ndi.binary_dilation(pelny, iterations=4)
kb = brzeg & ~blisko_stali
ky, kx = np.nonzero(kb)
print("widoczny brzeg kartonu: punktow", kx.size, "x", kx.min(), kx.max(), "y", ky.min(), ky.max())
# osobno: łuk tarczy kartonu (dolna połowa zdjęcia) i krawędzie języka (góra)
CX, CY, RS = 636.5, 823.3, 169.7
luk = (ky > 600)
x, y = kx[luk].astype(float), ky[luk].astype(float)
if luk.sum() > 30:
    A = np.c_[2*x, 2*y, np.ones_like(x)]; bb = x**2 + y**2
    (a, c, d), *_ = np.linalg.lstsq(A, bb, rcond=None); R = np.sqrt(d + a*a + c*c)
    print(f"luk tarczy kartonu: srodek ({a:.1f},{c:.1f}) R={R:.1f}px rozrzut {np.std(np.hypot(x-a,y-c)-R):.2f}px, pkt {luk.sum()}, y {y.min():.0f}-{y.max():.0f}, x {x.min():.0f}-{x.max():.0f}")
gora = ky < 420
print("jezyk kartonu: najwyzszy y", ky[gora].min(), " najbardziej lewy x", kx[gora].min())
# zewn. krawędź języka kartonu: mediana y górnego brzegu dla x w 420..760
top = [ky[(kx == xx) & gora].min() for xx in range(420, 761, 20) if ((kx == xx) & gora).any()]
print("gorna krawedz kartonu (y) na kolejnych x:", top)
# lewa krawędź (czubek) kartonu: mediana x dla y 320..400
lewa = [kx[(ky == yy)].min() for yy in range(320, 401, 10) if (ky == yy).any()]
print("lewa krawedz kartonu (x):", lewa)
