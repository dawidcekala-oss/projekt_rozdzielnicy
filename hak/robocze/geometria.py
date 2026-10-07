import ezdxf, math
from ezdxf.math import Vec2, bulge_to_arc
doc = ezdxf.readfile("hook_oryginal.dxf")
msp = doc.modelspace()
for s in doc.styles: print("style", s.dxf.name, s.dxf.font, s.dxf.get("bigfont"))
polys = [e for e in msp if e.dxftype()=="LWPOLYLINE"]
squares = [p for p in polys if len(p)==4]
hooks = [p for p in polys if len(p)>4]
for sq, hk in zip(sorted(squares,key=lambda p:p[0][0]), sorted(hooks,key=lambda p:p[0][0])):
    sp=[Vec2(p[0],p[1]) for p in sq.get_points()]
    c = sum(sp,Vec2())/4
    ang = math.degrees(math.atan2((sp[1]-sp[0]).y,(sp[1]-sp[0]).x))
    print("\n=== wariant przy x=%.0f  srodek kwadratu %s, kat boku %.3f deg" % (c.x, c.round(3), ang))
    # rotate so square sides axis-aligned
    rot = -(ang - round(ang/90)*90)
    print("obrot korekcyjny %.3f deg" % rot)
    pts = hk.get_points()
    for i,p in enumerate(pts):
        v = (Vec2(p[0],p[1])-c).rotate_deg(rot)
        q = Vec2(pts[(i+1)%len(pts)][0],pts[(i+1)%len(pts)][1])
        w = (q-c).rotate_deg(rot)
        L = (w-v).magnitude
        b = p[4]
        extra = ""
        if b:
            ce, sa, ea, r = bulge_to_arc(v, w, b)
            extra = " ARC r=%.3f kat=%.1f srodek=%s" % (r, 4*math.degrees(math.atan(b)), ce.round(3))
        print("  %2d (%8.3f,%8.3f) -> cieciwa %.3f%s" % (i, v.x, v.y, L, extra))
    side = [ (Vec2(p[0],p[1])-c).rotate_deg(rot) for p in sq.get_points()]
    print("  kwadrat bok %.3f" % (side[1]-side[0]).magnitude)
