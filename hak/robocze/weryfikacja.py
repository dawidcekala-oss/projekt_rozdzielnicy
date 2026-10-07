import ezdxf, math, subprocess, os, sys
from ezdxf import path as ezpath
from ezdxf.math import Vec2
sys.path.insert(0, ".")
import hak_generator as g

def pts_of(pl, c=Vec2(), rot=0.0):
    return [(Vec2(v.x, v.y) - c).rotate_deg(rot) for v in ezpath.make_path(pl).flattening(0.01)]

def odl(A, B):
    # maks. odległość punktów A od łamanej B (Hausdorff jednostronny, przybliżony gęstym próbkowaniem)
    def d(p, Q):
        best = 1e9
        for i in range(len(Q)):
            a, b = Q[i], Q[(i+1) % len(Q)]
            ab = b - a; t = max(0, min(1, (p - a).dot(ab) / (ab.dot(ab) or 1)))
            best = min(best, (a + ab * t - p).magnitude)
        return best
    return max(max(d(p, B) for p in A), max(d(q, A) for q in B))

# 1) zgodność z dostawcą
src = ezdxf.readfile("hook_oryginal.dxf").modelspace()
polys = [e for e in src if e.dxftype() == "LWPOLYLINE"]
sq = sorted([p for p in polys if len(p) == 4], key=lambda p: p[0][0])
hk = sorted([p for p in polys if len(p) > 4], key=lambda p: p[0][0])
for (kod, a, b), s, h in zip([("K0", 0, 0), ("A1.5", 1.5, 0), ("B3", 0, 3)], sq, hk):
    sp = [Vec2(p[0], p[1]) for p in s.get_points()]
    c = sum(sp, Vec2()) / 4
    ang = math.degrees(math.atan2((sp[1]-sp[0]).y, (sp[1]-sp[0]).x)); rot = -(ang - round(ang/90)*90)
    A = pts_of(h, c, rot)
    doc = ezdxf.new(); B = pts_of(doc.modelspace().add_lwpolyline(g.kontur(a, b), format="xyb", close=True))
    print(f"{kod} vs dostawca: max odchylka konturu {odl(A, B):.3f} mm")

# 2) DWG -> DXF -> porównanie
d2d = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "libredwg", "dwg2dxf.exe")
for kod, a, b, _ in g.WARIANTY:
    out = f"_rt_{kod}.dxf"
    subprocess.run([d2d, "-y", "-o", out, f"../cad/hak_{kod}.dwg"], capture_output=True)
    rt = ezdxf.readfile(out)
    pl = [e for e in rt.modelspace().query("LWPOLYLINE") if e.dxf.layer == "KONTUR"]
    dims = len(rt.modelspace().query("DIMENSION"))
    doc = ezdxf.new(); B = pts_of(doc.modelspace().add_lwpolyline(g.kontur(a, b), format="xyb", close=True))
    print(f"DWG {kod}: kontur {len(pl)} szt., odchylka {odl(pts_of(pl[0]), B):.4f} mm, wymiarow {dims}, warstwy {sorted(l.dxf.name for l in rt.layers)}")
    os.remove(out)
