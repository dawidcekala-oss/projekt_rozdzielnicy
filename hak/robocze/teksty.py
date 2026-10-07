import ezdxf
doc = ezdxf.readfile("hook_oryginal.dxf")
msp = doc.modelspace()
for e in msp.query("MTEXT"):
    print("MTEXT", repr(e.text), "h=", e.dxf.get("char_height"), "w=", e.dxf.get("width"), "style", e.dxf.style, "ins", e.dxf.insert)
for e in msp.query("TEXT"):
    print("TEXT", repr(e.dxf.text), "h=", e.dxf.get("height"), "rot", e.dxf.get("rotation"), "ins", e.dxf.insert)
for e in msp.query("DIMENSION"):
    print("DIM blk", e.dxf.get("geometry"), "style", e.dxf.dimstyle, "txtpt", e.dxf.get("text_midpoint"), "defpoint", e.dxf.get("defpoint"))
    blk = e.dxf.get("geometry")
    if blk and blk in doc.blocks:
        for sub in doc.blocks.get(blk):
            if sub.dxftype() in ("MTEXT","TEXT"):
                print("    ", sub.dxftype(), repr(sub.text if sub.dxftype()=="MTEXT" else sub.dxf.text), sub.dxf.insert)
for d in doc.dimstyles: print("dimstyle", d.dxf.name, d.dxf.get("dimtxt"), d.dxf.get("dimscale"), d.dxf.get("dimasz"), d.dxf.get("dimlfac"))
