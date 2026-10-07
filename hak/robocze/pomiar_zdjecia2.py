import numpy as np
from PIL import Image
from scipy import ndimage as ndi
exec(open("pomiar_zdjecia.py", encoding="utf-8").read().split("# --- brzeg maski")[0])
pelny = ndi.binary_fill_holes(glowny)
brzeg = pelny & ~ndi.binary_erosion(pelny)
by, bx = np.nonzero(brzeg)
cx0, cy0 = ox.mean(), oy.mean()
sel = (by > cy0 + 10) & (bx < cx0 + 140)
x, y = bx[sel].astype(float), by[sel].astype(float)
# okrąg
A = np.c_[2*x, 2*y, np.ones_like(x)]; b = x**2 + y**2
(a, c, d), *_ = np.linalg.lstsq(A, b, rcond=None); R = np.sqrt(d + a*a + c*c)
print(f"okrag: srodek ({a:.1f},{c:.1f}) R={R:.1f}px rozrzut {np.std(np.hypot(x-a, y-c)-R):.2f}px")
# elipsa osiowa: (x-x0)^2/A^2 + (y-y0)^2/B^2 = 1  -> liniowo: x^2 + p*y^2 + q*x + r*y + s = 0
M = np.c_[y**2, x, y, np.ones_like(x)]
(p, q, r, s), *_ = np.linalg.lstsq(M, -x**2, rcond=None)
x0, y0 = -q/2, -r/(2*p)
A2 = x0**2 + p*y0**2 - s; Ax, By = np.sqrt(A2), np.sqrt(A2/p)
print(f"elipsa: srodek ({x0:.1f},{y0:.1f}) poziomo {Ax:.1f}px pionowo {By:.1f}px  stosunek pion/poziom {By/Ax:.4f}")
ys_, xs_ = np.nonzero(pelny)
print("bbox", xs_.min(), xs_.max(), ys_.min(), ys_.max())
