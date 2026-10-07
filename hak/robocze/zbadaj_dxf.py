import ezdxf, collections
doc = ezdxf.readfile("hook_oryginal.dxf")
print("version", doc.dxfversion, "units", doc.header.get("$INSUNITS"), "measurement", doc.header.get("$MEASUREMENT"))
msp = doc.modelspace()
c = collections.Counter(e.dxftype() for e in msp)
print("modelspace:", dict(c))
for name in doc.layouts.names():
    lay = doc.layouts.get(name)
    print("layout", name, collections.Counter(e.dxftype() for e in lay))
print("layers:", [l.dxf.name for l in doc.layers])
print("blocks:", [b.name for b in doc.blocks if not b.name.startswith('*')])
for e in msp:
    t = e.dxftype()
    d = e.dxf
    if t == "LINE":
        print(t, d.layer, tuple(round(v,3) for v in d.start)[:2], tuple(round(v,3) for v in d.end)[:2])
    elif t == "ARC":
        print(t, d.layer, "c", tuple(round(v,3) for v in d.center)[:2], "r", round(d.radius,3), "a", round(d.start_angle,2), round(d.end_angle,2))
    elif t == "CIRCLE":
        print(t, d.layer, "c", tuple(round(v,3) for v in d.center)[:2], "r", round(d.radius,3))
    elif t in ("LWPOLYLINE",):
        print(t, d.layer, "closed", e.closed, [tuple(round(x,3) for x in p) for p in e.get_points()])
    elif t == "DIMENSION":
        try:
            m = e.get_measurement()
        except Exception as ex:
            m = ex
        print(t, d.layer, "dimtype", d.dimtype, "text", repr(d.get("text")), "meas", m, "p1", d.get("defpoint2"), "p2", d.get("defpoint3"))
    elif t in ("TEXT","MTEXT"):
        print(t, d.layer, repr(e.plain_text() if t=="MTEXT" else d.text), d.insert)
    elif t == "INSERT":
        print(t, d.name, d.insert, d.get("xscale"), d.get("rotation"))
    else:
        print(t, d.layer)
