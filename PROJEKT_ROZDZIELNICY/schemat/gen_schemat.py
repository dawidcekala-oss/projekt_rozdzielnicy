# -*- coding: utf-8 -*-
"""Schemat jednoarkuszowy A4 (pion) – rozdzielnica testowa Ampere Point. Jednostki: mm."""
import math, os

W, H = 210.0, 297.0
out = []
def emit(s): out.append(s)
COL = {"L1": "#7a4a1e", "L2": "#111111", "L3": "#707070", "N": "#1f4fd1", "PE": "#149114",
       "C": "#b3001b", "S": "#6a1fb3", "ZW": "#008c7a"}
LWP, LWC, LWS = 0.42, 0.28, 0.28

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def line(x1, y1, x2, y2, col="#111", lw=LWS, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    emit(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{lw}" stroke-linecap="round"{d}/>')
def poly(pts, col="#111", lw=LWS, fill="none", dash=None, close=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    emit(f'<{"polygon" if close else "polyline"} points="{p}" fill="{fill}" stroke="{col}" stroke-width="{lw}" stroke-linejoin="round" stroke-linecap="round"{d}/>')
def rect(x, y, w, h, col="#111", lw=LWS, fill="white", rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    emit(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{col}" stroke-width="{lw}"{d}/>')
def circle(x, y, r, col="#111", lw=LWS, fill="white"):
    emit(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="{col}" stroke-width="{lw}"/>')
def dot(x, y, col="#111", r=0.5):
    emit(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{col}" stroke="none"/>')
def text(x, y, s, size=1.6, anchor="start", rot=0, col="#111", bold=False, italic=False):
    fw = ' font-weight="bold"' if bold else ""; fi = ' font-style="italic"' if italic else ""
    tr = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ""
    emit(f'<text x="{x:.2f}" y="{y:.2f}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{col}"{fw}{fi}{tr}>{esc(s)}</text>')
def arc(x, y, r, a0, a1, col="#111", lw=LWS):
    x0, y0 = x + r * math.cos(math.radians(a0)), y + r * math.sin(math.radians(a0))
    x1, y1 = x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    emit(f'<path d="M{x0:.2f},{y0:.2f} A{r:.2f},{r:.2f} 0 {large} 1 {x1:.2f},{y1:.2f}" fill="none" stroke="{col}" stroke-width="{lw}" stroke-linecap="round"/>')

def wire(pts, net):
    col = COL.get(net, "#111"); lw = LWP if net in ("L1", "L2", "L3", "N", "PE") else LWC
    poly(pts, col, lw)
    if net == "PE": poly(pts, "#e3cf00", lw * 0.5, dash="1.1,1.1")

def hwire(y, x1, x2, net, cross=()):
    """pozioma linia z mostkami nad pionowymi przewodami w `cross` (x) leżącymi między x1 i x2"""
    xs = sorted([x for x in cross if min(x1, x2) + 0.6 < x < max(x1, x2) - 0.6])
    col = COL.get(net, "#111"); lw = LWP if net in ("L1", "L2", "L3", "N", "PE") else LWC
    cur = x1; r = 0.8
    sgn = 1 if x2 > x1 else -1
    for x in (xs if sgn > 0 else xs[::-1]):
        wire([(cur, y), (x - sgn * r, y)], net)
        arc(x, y, r, 180, 360, col, lw) if sgn > 0 else arc(x, y, r, 180, 360, col, lw)
        cur = x + sgn * r
    wire([(cur, y), (x2, y)], net)

def vwire(x, y1, y2, net, cross=()):
    ys = sorted([y for y in cross if min(y1, y2) + 0.6 < y < max(y1, y2) - 0.6])
    col = COL.get(net, "#111"); lw = LWP if net in ("L1", "L2", "L3", "N", "PE") else LWC
    cur = y1; r = 0.8; sgn = 1 if y2 > y1 else -1
    for y in (ys if sgn > 0 else ys[::-1]):
        wire([(x, cur), (x, y - sgn * r)], net)
        arc(x, y, r, 90, 270, col, lw)
        cur = y + sgn * r
    wire([(x, cur), (x, y2)], net)

# ---------- symbole IEC 60617 ----------
def contact(x, y, kind="NO", h=6.0, contactor=False, side=1, col="#111"):
    """zestyk na przewodzie pionowym (y..y+h). side: strona odchylenia zwory (+1 prawo, -1 lewo)"""
    line(x, y, x, y + 1.2, col); line(x, y + h - 1.2, x, y + h, col)
    if kind == "NO":
        line(x, y + 1.2, x + 2.0 * side, y + h - 1.6, col)
    else:
        line(x, y + 1.2, x, y + h - 1.2, col)                      # zwora zamknięta
        line(x, y + h - 1.2, x + 1.5 * side, y + h - 1.2, col)       # ogranicznik
        line(x - 0.9 * side, y + h - 1.2, x - 0.9 * side, y + h - 2.6, col)
    if contactor:
        arc(x, y + h - 1.9, 0.8, 0, 180, col)
def hcontact(x, y, kind="NO", w=6.0, col="#111", mark=None):
    """zestyk na przewodzie poziomym (x..x+w)"""
    line(x, y, x + 1.2, y, col); line(x + w - 1.2, y, x + w, y, col)
    if kind == "NO":
        line(x + 1.2, y, x + w - 1.6, y - 2.0, col)
    else:
        line(x + 1.2, y, x + w - 1.2, y, col); line(x + w - 1.2, y, x + w - 1.2, y - 1.5, col)
        line(x + w - 1.2, y + 0.9, x + w - 2.6, y + 0.9, col)
    if mark == "relay":
        arc(x + w - 1.6, y, 0.8, 90, 270, col)
def breaker(x, y, h=7.0, isolator=False, col="#111"):
    line(x, y, x, y + 1.4, col); line(x, y + h - 1.4, x, y + h, col)
    line(x, y + 1.4, x + 2.1, y + h - 1.9, col)
    if isolator:
        line(x - 1.1, y + 1.4, x + 1.1, y + 1.4, col)
    else:
        cx, cy = x, y + h - 1.4
        line(cx - 0.9, cy - 0.9, cx + 0.9, cy + 0.9, col); line(cx - 0.9, cy + 0.9, cx + 0.9, cy - 0.9, col)
def mech_link(xs, y): line(min(xs) + 0.7, y, max(xs) + 0.7, y, "#111", 0.22, dash="0.9,0.7")
def resistor_v(x, y, h=7.0, w=2.4): rect(x - w / 2, y, w, h)
def resistor_h(x, y, w=6.0, h=2.2): rect(x, y - h / 2, w, h)
def varistor_v(x, y, h=4.5, w=2.4):
    rect(x - w / 2, y, w, h); line(x - 0.8, y + h - 0.7, x + 0.8, y + 0.7); line(x + 0.8, y + 0.7, x + 1.5, y + 0.7)
def lamp(x, y, r=1.9, fill="white"):
    circle(x, y, r, fill=fill); d = r * 0.7
    line(x - d, y - d, x + d, y + d); line(x - d, y + d, x + d, y - d)
def fan(x, y, r=2.3):
    circle(x, y, r); text(x, y + 0.6, "M", 1.7, "middle"); text(x + 1.5, y - 0.9, "~", 1.5, "middle")
def ct(x, y, r=2.1): circle(x, y, r, fill="none")
def terminal(x, y, r=0.85): circle(x, y, r)
def coil(x, y, w=6.4, h=3.4, lab=""):
    rect(x - w / 2, y - h / 2, w, h); text(x, y + 0.65, lab, 1.5, "middle", bold=True)
    text(x - w / 2 + 0.2, y - h / 2 - 0.5, "A1", 0.95); text(x + w / 2 - 0.2, y - h / 2 - 0.5, "A2", 0.95, "end")
def bridge(x, y, s=2.6):
    poly([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], close=True); text(x, y + 0.5, "≈/=", 1.1, "middle")
def box(x, y, w, h, title, lines=(), tsize=1.8, lsize=1.35, lh=1.95, fill="#fcfcfc"):
    rect(x, y, w, h, fill=fill, lw=0.32, rx=0.6)
    text(x + 1.2, y + 2.6, title, tsize, bold=True)
    yy = y + 2.6 + lh + 0.3
    for ln in lines:
        text(x + 1.2, yy, ln, lsize); yy += lh

# ---------- geometria ----------
XA = {"L1": 18.0, "L2": 25.0, "L3": 32.0, "N": 39.0, "PE": 46.0}      # kolumna A
XB = {"L1": 118.0, "L2": 125.0, "L3": 132.0, "N": 139.0, "PE": 146.0}  # kolumna B
NETS = ("L1", "L2", "L3", "N", "PE")
XCH = {"L1": 100.0, "L2": 102.0, "L3": 104.0, "N": 106.0, "PE": 108.0}  # kanał między kolumnami

def header():
    emit(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">')
    emit('<rect width="210" height="297" fill="white"/>')
    rect(3, 3, 204, 291, lw=0.5, fill="none")
    text(5, 7.4, "AMPERE POINT – ROZDZIELNICA TESTOWA (SYMULATOR USTEREK INSTALACJI)", 2.6, bold=True)
    text(5, 10.4, "Schemat zasadniczy, arkusz 1/1, rew. B · przyłącze 3×400/230 V TN-S 32 A, prąd testów ≤16 A · wyjścia CEE 32 A, CEE 16 A, 2× Schuko · sterowanie Raspberry Pi 5 + Z-Wave (Shelly Wave Pro 3) + przekaźniki GPIO", 1.5)
    text(5, 12.6, "Urządzenie probiercze wg EN 50191 – obsługa wyłącznie przez osoby z uprawnieniami SEP E/D. Zasada: cewka bez napięcia = instalacja poprawna; usterka = cewka pod napięciem; wyjście załączone = styki -A11 zamknięte.", 1.35, italic=True)

def column_A():
    X = XA
    for n in NETS: text(X[n], 16.3, n, 1.7, "middle", bold=True, col=COL[n])
    rect(X["L1"] - 5, 17.2, X["PE"] - X["L1"] + 10, 4.0, rx=0.8)
    text((X["L1"] + X["PE"]) / 2, 19.9, "-W0  wtyk CEE 32 A 5P + H07RN-F 5G4 ≈5 m", 1.45, "middle")
    for n in NETS: wire([(X[n], 21.2), (X[n], 24.1)], n); terminal(X[n], 25.0)
    text(X["PE"] + 3.0, 25.6, "-X1 szybkozłączki 6 mm² (magazyn)", 1.5, bold=True)
    # CT
    for n in NETS: wire([(X[n], 25.9), (X[n], 36.0)], n)
    for n, nm in (("L1", "-T2"), ("L2", "-T3"), ("L3", "-T4")):
        ct(X[n], 30.5); wire([(X[n] + 2.1, 30.5), (X[n] + 3.4, 30.5), (X[n] + 3.4, 33.2)], "S")
        text(X[n] - 1.0, 28.1, nm, 1.2, "end", col=COL["S"])
    text(X["PE"] + 3.0, 29.6, "-T2, -T3, -T4  CT 100 A modułu DLB-A1", 1.45)
    text(X["PE"] + 3.0, 31.7, "listwa CT: proste odcinki ≥100 mm; przewody → -A20", 1.3)
    # Q1
    y = 36.0
    for n in ("L1", "L2", "L3", "N"): breaker(X[n], y, 7.0, isolator=True)
    wire([(X["PE"], 36.0), (X["PE"], 61.0)], "PE")
    mech_link((X["L1"], X["N"]), y + 3.6)
    text(X["PE"] + 3.0, y + 3.2, "-Q1  rozłącznik izolacyjny 4P 40 A", 1.5, bold=True); text(X["PE"] + 3.0, y + 5.4, "(blokowany kłódką)", 1.3)
    for n in ("L1", "L2", "L3", "N"): wire([(X[n], y + 7.0), (X[n], 62.0)], n)
    # SPD -F2: odgałęzienia na y 46..50 do kolumny ograniczników x 62..
    xs0 = 64.0
    for i, n in enumerate(("L1", "L2", "L3", "N")):
        yy = 46.0 + i * 1.4; xb = xs0 + i * 5.0
        dot(X[n], yy, COL[n]); hwire(yy, X[n], xb, n, cross=[X[m] for m in NETS])
        wire([(xb, yy), (xb, 52.0)], n)
        varistor_v(xb, 52.0, 4.6, 2.4)
        wire([(xb, 56.6), (xb, 58.5)], "PE")
    wire([(xs0, 58.5), (xs0 + 15.0, 58.5)], "PE")
    wire([(xs0 + 15.0, 58.5), (xs0 + 19.0, 58.5), (xs0 + 19.0, 61.0), (X["PE"], 61.0)], "PE"); dot(X["PE"], 61.0, COL["PE"])
    text(xs0 + 21.0, 52.0, "-F2  SPD typ 2, 4P", 1.5, bold=True); text(xs0 + 21.0, 54.1, "Uc 275 V, In 20 kA", 1.3)
    # P1 SDM630
    y = 62.0
    rect(X["L1"] - 3.2, y, X["N"] - X["L1"] + 6.4, 7.6, fill="#fcfcfc")
    for n in ("L1", "L2", "L3", "N"):
        terminal(X[n], y + 1.4, 0.6); terminal(X[n], y + 6.2, 0.6); wire([(X[n], y + 7.6), (X[n], 73.0)], n)
    text((X["L1"] + X["N"]) / 2, y + 4.4, "-P1  SDM630 V2", 1.5, "middle", bold=True)
    text(X["PE"] + 3.0, y + 3.0, "licznik 3-faz. 100 A (bezpośredni)", 1.45); text(X["PE"] + 3.0, y + 5.1, "RS485 A/B → magistrala (adres 1)", 1.3)
    wire([(X["PE"], 61.0), (X["PE"], 140.0)], "PE")
    # odgałęzienie sterowania: F6, F7 (L1) i N230
    yF = 74.0
    dot(X["L1"], yF, COL["L1"]); hwire(yF, X["L1"], 78.0, "L1", cross=[X[m] for m in NETS])
    dot(66.0, yF, COL["L1"])
    breaker(66.0, yF, 7.0); breaker(78.0, yF, 7.0)
    text(68.4, yF + 4.0, "-F6 B6", 1.4, bold=True); text(80.4, yF + 4.0, "-F7 B10", 1.4, bold=True)
    wire([(66.0, yF + 7.0), (66.0, 84.0)], "C"); text(66.0, 86.0, "L230", 1.4, "middle", bold=True, col=COL["C"])
    wire([(78.0, yF + 7.0), (78.0, 84.0)], "C"); text(78.0, 86.0, "LT1", 1.4, "middle", bold=True, col=COL["C"])
    yN = 77.0
    dot(X["N"], yN, COL["N"]); hwire(yN, X["N"], 90.0, "N", cross=[X["PE"]]); text(90.0, 86.0, "N230", 1.4, "middle", bold=True, col=COL["N"])
    wire([(90.0, yN), (90.0, 84.0)], "N")
    text(58.0, 89.2, "L230/N230: zasilanie sterowania (pas dolny); LT1: pierwotne -T1 (kolumna B)", 1.2)
    # K12 (tor przez RCD) + pominięcie
    yK = 92.0
    for n in ("L1", "L2", "L3", "N"):
        x = X[n]
        dot(x, yK - 1.0, COL[n])
        wire([(x, yK - 1.0), (x - 3.0, yK - 1.0), (x - 3.0, 104.0)], n)      # tor pominięcia
        contact(x, yK, "NC", 6.0, contactor=True)
        wire([(x, yK + 6.0), (x, 108.0)], n)
        contact(x - 3.0, 104.0, "NO", 6.0, contactor=True, side=-1)
        wire([(x - 3.0, 110.0), (x - 3.0, 115.0), (x, 115.0)], n); dot(x, 115.0, COL[n])
    mech_link((X["L1"], X["L2"]), yK + 3.0); mech_link((X["L3"], X["N"]), yK + 3.0)
    mech_link((X["L1"] - 3, X["L2"] - 3), 107.0); mech_link((X["L3"] - 3, X["N"] - 3), 107.0)
    text(X["PE"] + 3.0, yK + 2.6, "-K12a, -K12b  2NO+2NC 25 A", 1.5, bold=True)
    text(X["PE"] + 3.0, yK + 4.7, "zestyki NC: tor przez RCD;", 1.3); text(X["PE"] + 3.0, yK + 6.7, "zestyki NO (lewe tory): pominięcie RCD (F13)", 1.3)
    # RCD -F1
    yR = 108.0
    emit(f'<ellipse cx="{(X["L1"] + X["N"]) / 2:.2f}" cy="{yR + 0.8:.2f}" rx="{(X["N"] - X["L1"]) / 2 + 2.4:.2f}" ry="1.5" fill="none" stroke="#111" stroke-width="0.3"/>')
    for n in ("L1", "L2", "L3", "N"):
        breaker(X[n], yR + 1.5, 6.5); wire([(X[n], yR + 8.0), (X[n], 118.0)], n)
    mech_link((X["L1"], X["N"]), yR + 4.9)
    text(X["PE"] + 3.0, yR + 3.6, "-F1  RCD 4P 40 A, IΔn 30 mA, typ A", 1.5, bold=True); text(X["PE"] + 3.0, yR + 5.7, "(jedyny RCD stanowiska)", 1.3)
    # -F3 3P B16 (sekcja usterek, testy ≤16 A)
    yF3 = 120.0
    for n in ("L1", "L2", "L3"): breaker(X[n], yF3, 6.5)
    mech_link((X["L1"], X["L3"]), yF3 + 3.3)
    text(X["PE"] + 3.0, yF3 + 2.6, "-F3  wyłącznik 3P B16 – zabezpieczenie sekcji usterek", 1.5, bold=True)
    text(X["PE"] + 3.0, yF3 + 4.7, "i obu gniazd CEE (prąd testów ≤16 A, styki Shelly 16 A)", 1.3)
    for n in ("L1", "L2", "L3"): wire([(X[n], yF3 + 6.5), (X[n], 130.0)], n)
    # -A11 Shelly Wave Pro 3 = stycznik główny (3 styki NO 16 A)
    yS = 130.0
    for i, n in enumerate(("L1", "L2", "L3")):
        contact(X[n], yS, "NO", 6.0, side=-1); arc(X[n], yS + 4.1, 0.8, 90, 270)
        text(X[n] - 1.2, yS - 0.6, f"O{i + 1}", 1.0, "end")
    mech_link((X["L1"], X["L3"]), yS + 3.0)
    text(X["PE"] + 3.0, yS + 2.6, "-A11  Shelly Wave Pro 3 (Z-Wave): O1 L1, O2 L2, O3 L3", 1.5, bold=True)
    text(X["PE"] + 3.0, yS + 4.7, "= stycznik główny wyjścia (16 A/styk); zasilanie -A11 z Lc,", 1.3)
    text(X["PE"] + 3.0, yS + 6.7, "więc E-STOP / kluczyk odłączają wyjście sprzętowo", 1.3)
    for n in ("L1", "L2", "L3"): wire([(X[n], yS + 6.0), (X[n], 140.0)], n)
    # -K2 zamiana L2<->L3 (2NO+2NC): NC prosto, NO na krzyż
    yK2 = 140.0
    contact(X["L2"], yK2, "NC", 6.0, contactor=True, side=-1); contact(X["L3"], yK2, "NC", 6.0, contactor=True)
    dot(X["L2"], yK2, COL["L2"]); wire([(X["L2"], yK2), (X["L2"] + 2.6, yK2 + 0.6), (X["L2"] + 2.6, yK2 + 1.2)], "L2")
    contact(X["L2"] + 2.6, yK2 + 1.2, "NO", 4.4, contactor=True, side=1)
    wire([(X["L2"] + 2.6, yK2 + 5.6), (X["L2"] + 2.6, yK2 + 7.6), (X["L3"], yK2 + 10.4)], "L2")
    dot(X["L3"], yK2, COL["L3"]); wire([(X["L3"], yK2), (X["L3"] - 2.6, yK2 + 0.6), (X["L3"] - 2.6, yK2 + 1.2)], "L3")
    contact(X["L3"] - 2.6, yK2 + 1.2, "NO", 4.4, contactor=True, side=-1)
    wire([(X["L3"] - 2.6, yK2 + 5.6), (X["L3"] - 2.6, yK2 + 7.6), (X["L2"], yK2 + 10.4)], "L3")
    arc((X["L2"] + X["L3"]) / 2, yK2 + 9.0, 0.7, 180, 360, COL["L3"], LWP)
    wire([(X["L2"], yK2 + 6.0), (X["L2"], 156.0)], "L2"); wire([(X["L3"], yK2 + 6.0), (X["L3"], 156.0)], "L3")
    dot(X["L2"], yK2 + 10.4, COL["L2"]); dot(X["L3"], yK2 + 10.4, COL["L3"])
    wire([(X["L1"], yK2), (X["L1"], 156.0)], "L1"); wire([(X["N"], 118.0), (X["N"], 156.0)], "N")
    text(X["PE"] + 3.0, yK2 + 2.6, "-K2  2NO+2NC 25 A: NC L2→L2′, L3→L3′ · NO: zamiana", 1.5, bold=True)
    text(X["PE"] + 3.0, yK2 + 4.7, "L2↔L3 = zła kolejność faz (F9); przełączanie tylko", 1.3)
    text(X["PE"] + 3.0, yK2 + 6.7, "przy otwartym -A11; -K13 CKF-B potwierdza na wyjściu", 1.3)
    # przejście do kolumny B: y 140..148 w prawo, kanał w górę
    for i, n in enumerate(NETS):
        yy = 157.0 + i * 1.8
        wire([(X[n], 156.0 if n != "PE" else 140.0), (X[n], yy)], n)
        hwire(yy, X[n], XCH[n], n, cross=[X[m] for m in NETS if X[m] > X[n]])
        wire([(XCH[n], yy), (XCH[n], 20.0 + i * 1.0)], n)
        hwire(20.0 + i * 1.0, XCH[n], XB[n], n, cross=[])
    text(104.0, 168.5, "do kolumny B ↑", 1.3, "middle", italic=True)
    text(104.0, 17.8, "z kolumny A", 1.3, "middle", italic=True)

def column_B():
    X = XB
    xlab = X["PE"] + 4.0
    for n in NETS: text(X[n], 16.3, n + "′", 1.7, "middle", bold=True, col=COL[n])
    y0 = {n: 20.0 + i * 1.0 for i, n in enumerate(NETS)}
    # K4 (L1) i K3 (L3)
    yK3 = 28.0
    for n in NETS: wire([(X[n], y0[n]), (X[n], yK3)], n)
    contact(X["L1"], yK3, "NC", 6.0, contactor=True, side=-1); contact(X["L3"], yK3, "NC", 6.0, contactor=True)
    wire([(X["L2"], yK3), (X["L2"], 158.0)], "L2"); wire([(X["L3"], yK3 + 6.0), (X["L3"], 158.0)], "L3")
    text(xlab, yK3 + 2.4, "-K4  2NC 25 A (L1): luźny styk – impulsy (F11)", 1.4, bold=True)
    text(xlab, yK3 + 4.6, "-K3  2NC 25 A (L3): zanik fazy (F8)", 1.4, bold=True)
    # R1 + K5 (L1)
    yR = 38.0
    wire([(X["L1"], yK3 + 6.0), (X["L1"], yR)], "L1"); dot(X["L1"], yR, COL["L1"])
    resistor_v(X["L1"], yR + 1.5, 7.0); wire([(X["L1"], yR + 8.5), (X["L1"], yR + 11.0)], "L1"); dot(X["L1"], yR + 11.0, COL["L1"])
    wire([(X["L1"], yR), (X["L1"] - 4.0, yR), (X["L1"] - 4.0, yR + 1.5)], "L1")
    contact(X["L1"] - 4.0, yR + 1.5, "NC", 6.5, contactor=True, side=-1)
    wire([(X["L1"] - 4.0, yR + 8.0), (X["L1"] - 4.0, yR + 11.0), (X["L1"], yR + 11.0)], "L1")
    text(xlab, yR + 2.0, "-R1  0,5 Ω / 200 W (2×1 Ω 100 W ∥) na radiatorze; 128 W przy 16 A", 1.4, bold=True)
    text(xlab, yR + 4.1, "-K5  2NC 25 A: bocznik -R1 (F12 – przepalony styk)", 1.4, bold=True)
    text(xlab, yR + 6.2, "-B1 θ 85 °C NC w obwodzie cewki -K5; -M1 wentylator radiatora", 1.3)
    text(X["L1"] - 6.5, yR + 5.4, "-K5", 1.2, "end"); text(X["L1"] + 1.6, yR + 5.4, "-R1", 1.2)
    # T1 wtórne (L1)
    yT = 53.0
    wire([(X["L1"], yR + 11.0), (X["L1"], yT)], "L1")
    for k in range(4): arc(X["L1"], yT + 1.0 + k * 1.8, 0.9, 90, 270)
    line(X["L1"] - 1.7, yT + 0.3, X["L1"] - 1.7, yT + 8.0, lw=0.35); line(X["L1"] - 2.3, yT + 0.3, X["L1"] - 2.3, yT + 8.0, lw=0.35)
    xp = X["L1"] - 4.0
    for k in range(4): arc(xp, yT + 1.0 + k * 1.8, 0.9, -90, 90)
    wire([(X["L1"], yT + 8.2), (X["L1"], 158.0)], "L1")
    text(xlab, yT + 2.0, "-T1  transformator toroidalny 630 VA, 230 V / 2×30 V", 1.4, bold=True)
    text(xlab, yT + 4.1, "wtórne (2 uzwojenia ∥, 30 V / 21 A) w szereg z L1: ±30 V (F10a/b)", 1.3)
    text(xlab, yT + 6.2, "pierwotne P1–P2 zasilane przez -K6/-K7 (ramka poniżej)", 1.3)
    # pierwotne: wyprowadzenia P1, P2 w lewo-dół do ramki
    wire([(xp, yT + 1.0), (xp - 2.5, yT + 1.0), (xp - 2.5, 74.0)], "C")
    wire([(xp, yT + 7.0), (xp - 4.5, yT + 7.0), (xp - 4.5, 76.0)], "C")
    text(xp - 2.5 + 0.8, 72.5, "P1", 1.1); text(xp - 4.5 - 0.6, 72.5, "P2", 1.1, "end")
    # ramka K6/K7 (pierwotne) x 150..204, y 62..86  — przewody P1/P2 prowadzone poziomo w prawo pod kolumną? użyj y 66 w prawo do ramki
    fx, fy, fw, fh = 152.0, 66.0, 52.0, 27.0
    hwire(74.0, xp - 2.5, fx + 12.0, "C", cross=[X[n] for n in NETS] + [xp - 4.5, fx + 4.0])
    hwire(76.0, xp - 4.5, fx + 12.0, "C", cross=[X[n] for n in NETS] + [fx + 4.0])
    rect(fx, fy, fw, fh, fill="#fcfcfc", rx=0.6)
    text(fx + 1.2, fy + 2.4, "-K6 boost / -K7 buck – pierwotne -T1 (2× 2NO+2NC 25 A)", 1.4, bold=True)
    text(fx + 1.2, fy + 4.3, "oba bez napięcia: NC(K6)·NC(K7) zwierają P1–P2 → bocznik magnetyczny", 1.15)
    xl, xn = fx + 4.0, fx + fw - 4.0
    wire([(xl, fy + 6.0), (xl, fy + fh - 1.5)], "C"); text(xl, fy + fh - 2.0 + 0.0, "", 1)
    wire([(xn, fy + 6.0), (xn, fy + fh - 1.5)], "N")
    text(xl, fy + 5.6, "LT1 (z -F7)", 1.1, "middle", col=COL["C"]); text(xn, fy + 5.6, "N230", 1.1, "middle", col=COL["N"])
    rect(xl - 1.0, fy + 7.0, 2.0, 3.0, lw=0.22); text(xl - 1.6, fy + 9.4, "-RT1 NTC", 1.0, "end")
    # P1 i P2 szyny w ramce
    p1y, p2y = 74.0, 76.0
    xP1, xP2 = fx + 22.0, fx + 30.0
    wire([(fx + 12.0, p1y), (xP1, p1y)], "C"); wire([(fx + 12.0, p2y), (xP2, p2y)], "C")
    wire([(xP1, p1y), (xP1, fy + fh - 1.5)], "C"); wire([(xP2, p2y), (xP2, fy + fh - 1.5)], "C")
    text(xP1, fy + fh - 0.0 + 1.2, "P1", 1.05, "middle"); text(xP2, fy + fh + 1.2, "P2", 1.05, "middle")
    # K6: LT1->P1 (y 76), N->P2 (y 76) ; K7: N->P1 (y 81), LT1->P2 (y 81) ; zwarcie P1-P2 (y 85)
    yk6, yk7, yz = fy + 12.5, fy + 18.0, fy + 23.5
    hcontact(xl, yk6, "NO", 6.0, mark=None); wire([(xl + 6.0, yk6), (xP1, yk6)], "C"); dot(xP1, yk6, COL["C"]); dot(xl, yk6, COL["C"]); text(xl + 3.0, yk6 - 2.3, "K6", 1.05, "middle")
    hcontact(xn - 6.0 - 6.0, yk6, "NO", 6.0); wire([(xn, yk6), (xn - 6.0, yk6)], "N"); wire([(xn - 12.0, yk6), (xP2, yk6)], "N"); dot(xP2, yk6, COL["N"]); dot(xn, yk6, COL["N"]); text(xn - 9.0, yk6 - 2.3, "K6", 1.05, "middle")
    hcontact(xl, yk7, "NO", 6.0); hwire(yk7, xl + 6.0, xP2, "C", cross=[xP1]); dot(xP2, yk7, COL["C"]); dot(xl, yk7, COL["C"]); text(xl + 3.0, yk7 - 2.3, "K7", 1.05, "middle")
    # krzyżowanie: LT1->P2 przecina szynę P1
    hcontact(xn - 12.0, yk7, "NO", 6.0); wire([(xn, yk7), (xn - 6.0, yk7)], "N"); hwire(yk7, xn - 12.0, xP1, "N", cross=[xP2]); dot(xP1, yk7, COL["N"]); dot(xn, yk7, COL["N"]); text(xn - 9.0, yk7 - 2.3, "K7", 1.05, "middle")
    # zwarcie: P1 -> NC K6 -> NC K7 -> P2
    hcontact(xP1, yz, "NC", 3.8); hcontact(xP1 + 4.2, yz, "NC", 3.8); wire([(xP1 + 8.0, yz), (xP2, yz)], "C")
    dot(xP1, yz, COL["C"]); dot(xP2, yz, COL["C"]); text(xP1 + 1.9, yz - 2.3, "K6", 1.0, "middle"); text(xP1 + 6.1, yz - 2.3, "K7", 1.0, "middle")
    varistor_v(xn - 3.0, yk7 + 1.5, 3.4, 2.0); text(xn - 6.5, yk7 + 4.2, "-RV1", 1.0, "end")
    # K8 (N), K9 (PE 2 bieguny ∥)
    yK8 = 106.0
    for n in ("N", "PE"): wire([(X[n], y0[n]), (X[n], yK8)], n)
    contact(X["N"], yK8, "NC", 6.0, contactor=True)
    dot(X["PE"], yK8, COL["PE"]); wire([(X["PE"], yK8), (X["PE"] + 3.0, yK8), (X["PE"] + 3.0, yK8 + 0.4)], "PE")
    contact(X["PE"], yK8 + 0.4, "NC", 6.0, contactor=True, side=-1); contact(X["PE"] + 3.0, yK8 + 0.4, "NC", 6.0, contactor=True, side=1)
    wire([(X["PE"] + 3.0, yK8 + 6.4), (X["PE"] + 3.0, yK8 + 7.0), (X["PE"], yK8 + 7.0)], "PE"); dot(X["PE"], yK8 + 7.0, COL["PE"])
    wire([(X["N"], yK8 + 6.0), (X["N"], 134.0)], "N"); wire([(X["PE"], yK8 + 7.0), (X["PE"], 134.0)], "PE")
    text(X["N"] - 1.4, yK8 - 1.2, "-K8", 1.2, "end"); text(X["PE"] + 5.2, yK8 - 1.2, "-K9", 1.2)
    text(xlab + 6.0, yK8 - 5.2, "-K8 2NC 25 A: przerwa N (F4)", 1.3, bold=True)
    text(xlab + 6.0, yK8 - 3.1, "-K9 2NC 25 A: przerwa PE (F1), 2 bieguny ∥", 1.3, bold=True)
    # szyny do drabinki upływów
    xr = 203.0
    rails = {"PEs": 115.0, "L1o": 119.0, "No": 124.0, "PEo": 129.0}
    dot(X["PE"], 97.0, COL["PE"]); hwire(97.0, X["PE"], 151.0, "PE"); wire([(151.0, 97.0), (151.0, rails["PEs"])], "PE")
    hwire(rails["PEs"], 151.0, xr, "PE")
    dot(X["L1"], rails["L1o"], COL["L1"]); hwire(rails["L1o"], X["L1"], xr, "L1", cross=[X[n] for n in NETS if n != "L1"] + [151.0])
    dot(X["N"], rails["No"], COL["N"]); hwire(rails["No"], X["N"], xr, "N", cross=[X["PE"], 151.0])
    dot(X["PE"], rails["PEo"], COL["PE"]); hwire(rails["PEo"], X["PE"], xr, "PE", cross=[151.0])
    for k, lab, c in (("PEs", "PE (sieć)", "PE"), ("L1o", "L1′", "L1"), ("No", "N′", "N"), ("PEo", "PE′", "PE")):
        text(xr + 0.6, rails[k] + 0.55, lab, 1.15, col=COL[c])
    # F2: PEs -> styk -> R2 -> PEo
    x = 156.0
    dot(x, rails["PEs"], COL["PE"]); contact(x, rails["PEs"] + 0.2, "NO", 4.2, side=1); text(x + 2.3, rails["PEs"] + 3.0, "-A14:O1", 1.05)
    resistor_v(x, rails["PEs"] + 4.6, 4.0, 2.0); text(x + 1.6, rails["PEs"] + 7.4, "-R2 100 Ω 50 W", 1.0)
    vwire(x, rails["PEs"] + 8.6, rails["PEo"], "PE", cross=[rails["L1o"], rails["No"]]); dot(x, rails["PEo"], COL["PE"])
    text(x, rails["PEs"] - 1.3, "F2 słabe PE", 1.1, "middle", bold=True)
    # F3: L1o -> styk -> R3 220k -> PEo
    x = 168.0
    dot(x, rails["L1o"], COL["L1"]); contact(x, rails["L1o"] + 0.2, "NO", 3.8, side=1); text(x + 2.3, rails["L1o"] + 2.8, "-A14:O2", 1.05)
    resistor_v(x, rails["L1o"] + 4.2, 3.6, 2.0); text(x + 1.6, rails["L1o"] + 6.9, "-R3 220 kΩ 2 W", 1.0)
    vwire(x, rails["L1o"] + 7.8, rails["PEo"], "PE", cross=[rails["No"]]); dot(x, rails["PEo"], COL["PE"])
    text(x, rails["PEs"] - 1.3, "F3 PE pod U", 1.1, "middle", bold=True)
    # F6: No -> styk -> PEo
    x = 179.0
    dot(x, rails["No"], COL["N"]); contact(x, rails["No"] + 0.1, "NO", 4.8, side=1); text(x + 2.3, rails["No"] + 3.2, "-A14:O3", 1.05)
    dot(x, rails["PEo"], COL["PE"])
    text(x, rails["PEs"] - 1.3, "F6 mostek N′–PE′", 1.1, "middle", bold=True)
    # F14: L1o -> styk -> R4 -> PEo
    x = 193.0
    dot(x, rails["L1o"], COL["L1"]); contact(x, rails["L1o"] + 0.2, "NO", 3.8, side=1); text(x + 2.3, rails["L1o"] + 2.8, "-A15:O1", 1.05)
    resistor_v(x, rails["L1o"] + 4.2, 3.6, 2.0); text(x + 1.6, rails["L1o"] + 6.9, "-R4 6,8 kΩ 25 W", 1.0)
    vwire(x, rails["L1o"] + 7.8, rails["PEo"], "PE", cross=[rails["No"]]); dot(x, rails["PEo"], COL["PE"])
    text(x + 1.0, rails["PEs"] - 1.3, "F14 upływ 34 mA~", 1.1, "middle", bold=True)
    # F15: zestaw DC pod szynami: L1' -> styk -> dioda -V1 -> węzeł A; -C1 ∥ -R6 między A a N'; -R5 z A do PE'
    yd = rails["PEo"] + 3.0
    text(154.0, yd + 1.4, "F15 upływ 6 mA= (oślepianie RCD typu A):", 1.1, bold=True)
    text(154.0, yd + 3.7, "L1′ → styk → dioda -V1 (1 kV) → węzeł A; -C1 22 µF/400 V ∥ -R6 100 kΩ", 1.0)
    text(154.0, yd + 5.9, "między A a N′ (≈ 325 V=); -R5 56 kΩ 5 W z A do PE′ → ≈ 6 mA prądu stałego", 1.0)
    xv = 200.5
    dot(xv, rails["L1o"], COL["L1"]); vwire(xv, rails["L1o"], yd + 2.0, "L1", cross=[rails["No"], rails["PEo"]])
    contact(xv, yd + 2.0, "NO", 3.6, side=-1); text(xv - 2.2, yd + 4.6, "-A15:O2", 1.0, "end")
    # dioda pionowo (strzałka w dół)
    wire([(xv, yd + 5.6), (xv, yd + 7.0)], "L1")
    poly([(xv - 1.3, yd + 7.0), (xv + 1.3, yd + 7.0), (xv, yd + 9.2)], close=True); line(xv - 1.3, yd + 9.2, xv + 1.3, yd + 9.2)
    text(xv + 1.8, yd + 8.8, "-V1", 1.0)
    yA = yd + 11.0
    wire([(xv, yd + 9.2), (xv, yA)], "S"); dot(xv, yA, COL["S"])            # węzeł A
    # R5 w lewo do PE'
    wire([(xv, yA), (xv - 4.0, yA)], "S"); resistor_h(xv - 9.0, yA, 5.0, 2.0); text(xv - 6.5, yA - 1.6, "-R5", 1.0, "middle")
    wire([(xv - 9.0, yA), (xv - 12.0, yA), (xv - 12.0, rails["PEo"])], "PE"); dot(xv - 12.0, rails["PEo"], COL["PE"])
    # C1 ∥ R6 w dół do N' (N' poprowadzony z szyny No w dół po prawej stronie)
    xn2 = 203.0
    dot(xn2, rails["No"], COL["N"]); vwire(xn2, rails["No"], yA + 6.5, "N", cross=[rails["PEo"]])
    wire([(xv, yA), (xv, yA + 1.2)], "S")
    line(xv - 1.5, yA + 1.2, xv + 1.5, yA + 1.2, lw=0.4); line(xv - 1.5, yA + 2.2, xv + 1.5, yA + 2.2, lw=0.4)   # kondensator
    wire([(xv, yA + 2.2), (xv, yA + 6.5), (xn2, yA + 6.5)], "N")
    text(xv - 2.0, yA + 2.2, "-C1", 1.0, "end")
    wire([(xv, yA), (xv - 3.0, yA + 0.0)], "S")  # już jest; R6 równolegle
    wire([(xv - 2.0, yA), (xv - 2.0, yA + 3.0)], "S"); rect(xv - 3.0, yA + 3.0, 2.0, 2.0, lw=0.22); wire([(xv - 2.0, yA + 5.0), (xv - 2.0, yA + 6.5), (xv, yA + 6.5)], "N")
    text(xv - 3.6, yA + 4.6, "-R6", 1.0, "end")
    # K10 zamiana N–PE
    yK10 = 134.0
    contact(X["N"], yK10, "NC", 6.0, contactor=True); contact(X["PE"], yK10, "NC", 6.0, contactor=True)
    dot(X["N"], yK10, COL["N"]); wire([(X["N"], yK10), (X["N"] + 2.6, yK10 + 0.6), (X["N"] + 2.6, yK10 + 1.2)], "N")
    contact(X["N"] + 2.6, yK10 + 1.2, "NO", 4.4, contactor=True, side=1)
    wire([(X["N"] + 2.6, yK10 + 5.6), (X["N"] + 2.6, yK10 + 7.6), (X["PE"], yK10 + 10.4)], "N")
    dot(X["PE"], yK10, COL["PE"]); wire([(X["PE"], yK10), (X["PE"] - 2.6, yK10 + 0.6), (X["PE"] - 2.6, yK10 + 1.2)], "PE")
    contact(X["PE"] - 2.6, yK10 + 1.2, "NO", 4.4, contactor=True, side=-1)
    wire([(X["PE"] - 2.6, yK10 + 5.6), (X["PE"] - 2.6, yK10 + 7.6), (X["N"], yK10 + 10.4)], "PE")
    arc((X["N"] + X["PE"]) / 2, yK10 + 9.0, 0.7, 180, 360, COL["PE"], LWP)
    wire([(X["N"], yK10 + 6.0), (X["N"], 160.0)], "N"); wire([(X["PE"], yK10 + 6.0), (X["PE"], 160.0)], "PE")
    dot(X["N"], yK10 + 10.4, COL["N"]); dot(X["PE"], yK10 + 10.4, COL["PE"])
    text(152.0, 150.5, "-K10  2NO+2NC 25 A: NC: N′→N″, PE′→PE″ · NO: zamiana N↔PE (F5)", 1.3, bold=True)
    text(152.0, 152.7, "N″ / PE″ = przewody neutralny i ochronny do gniazd wyjściowych", 1.15)
    for n in ("L1", "L2", "L3"): wire([(X[n], 158.0), (X[n], 160.0)], n)
    # szyny wyjściowe
    yb = {n: 160.0 + i * 2.0 for i, n in enumerate(NETS)}
    xe = 203.0
    for n in NETS:
        dot(X[n], yb[n], COL[n]); hwire(yb[n], X[n], xe, n, cross=[X[m] for m in NETS if X[m] > X[n]])
        text(xe + 0.6, yb[n] + 0.5, n + "″", 1.15, col=COL[n])
    def group3(x0, name, tag, ysock):
        for i, n in enumerate(("L1", "L2", "L3")):
            x = x0 + i * 3.2
            dot(x, yb[n], COL[n]); vwire(x, yb[n], ysock, n, cross=[yb[m] for m in NETS if yb[m] > yb[n]])
        dot(x0 + 9.6, yb["N"], COL["N"]); vwire(x0 + 9.6, yb["N"], ysock, "N", cross=[yb["PE"]])
        dot(x0 + 12.8, yb["PE"], COL["PE"]); wire([(x0 + 12.8, yb["PE"]), (x0 + 12.8, ysock)], "PE")
        text(x0 - 1.5, 178.0, tag, 1.15)
        rect(x0 - 2.0, ysock, 17.0, 5.0, rx=0.8); text(x0 + 6.5, ysock + 3.3, name, 1.4, "middle", bold=True)
    group3(141.0, "-X2  CEE 32 A 5P", "zab. -F3 B16 (kol. A)", 187.0)
    group3(163.0, "-X3  CEE 16 A 5P", "zab. -F3 B16 (kol. A)", 187.0)
    x5 = 187.0
    dot(x5, yb["L1"], COL["L1"]); vwire(x5, yb["L1"], 173.0, "L1", cross=[yb[m] for m in NETS if m != "L1"])
    dot(x5 + 3.2, yb["N"], COL["N"]); vwire(x5 + 3.2, yb["N"], 173.0, "N", cross=[yb["PE"]])
    breaker(x5, 173.0, 5.0); breaker(x5 + 3.2, 173.0, 5.0); mech_link((x5, x5 + 3.2), 175.5)
    text(x5 + 5.6, 175.2, "-F5 B16", 1.2, bold=True); text(x5 + 5.6, 177.0, "2P (L+N)", 1.2, bold=True)
    yk = 179.0
    dot(x5, yk, COL["L1"]); dot(x5 + 3.2, yk, COL["N"])
    contact(x5, yk, "NC", 4.0, contactor=True, side=-1); contact(x5 + 3.2, yk, "NC", 4.0, contactor=True, side=1)
    wire([(x5, yk), (x5 - 2.6, yk), (x5 - 2.6, yk + 0.6)], "L1"); contact(x5 - 2.6, yk + 0.6, "NO", 3.4, contactor=True, side=-1)
    wire([(x5 - 2.6, yk + 4.0), (x5 - 2.6, yk + 5.6), (x5 + 3.2, yk + 5.6)], "L1")
    wire([(x5 + 3.2, yk), (x5 + 5.8, yk), (x5 + 5.8, yk + 0.6)], "N"); contact(x5 + 5.8, yk + 0.6, "NO", 3.4, contactor=True, side=1)
    wire([(x5 + 5.8, yk + 4.0), (x5 + 5.8, yk + 5.6), (x5, yk + 5.6)], "N")
    arc(x5 + 1.6, yk + 5.6, 0.6, 180, 360, COL["N"], LWP)
    wire([(x5, yk + 4.0), (x5, yk + 5.6)], "L1"); wire([(x5 + 3.2, yk + 4.0), (x5 + 3.2, yk + 5.6)], "N")
    dot(x5, yk + 5.6, COL["L1"]); dot(x5 + 3.2, yk + 5.6, COL["N"])
    text(x5 + 8.0, yk + 1.6, "-K11 2NO+2NC", 1.15, bold=True); text(x5 + 8.0, yk + 3.3, "25 A: L↔N (F7)", 1.1)
    wire([(x5, yk + 5.6), (x5, 189.5)], "L1"); wire([(x5 + 3.2, yk + 5.6), (x5 + 3.2, 189.5)], "N")
    dot(x5 + 9.6, yb["PE"], COL["PE"]); wire([(x5 + 9.6, yb["PE"]), (x5 + 9.6, 171.0), (x5 + 14.5, 171.0), (x5 + 14.5, 189.5)], "PE")
    rect(x5 - 4.5, 189.5, 21.5, 5.6, rx=0.8); text(x5 + 6.2, 191.9, "-X4a, -X4b  2× Schuko", 1.3, "middle", bold=True); text(x5 + 6.2, 194.0, "16 A (L, N, PE″) równolegle", 1.0, "middle")
    # -K13 CKF-B, -P2 PZEM-016, -P3 ZMPT101B – skrzynki z odczepami od szyn wyjściowych
    bx, bw = 110.0, 26.0
    # K13
    rect(bx, 172.0, bw, 5.2, fill="#fcfcfc", rx=0.5); text(bx + 1.0, 174.2, "-K13 CKF-B", 1.3, bold=True); text(bx + 1.0, 176.3, "kolejność/zanik faz → styk → -A12:SW3", 0.95)
    for i, n in enumerate(("L1", "L2", "L3", "N")):
        x = bx + 2.5 + i * 2.6
        dot(x, yb[n], COL[n]); vwire(x, yb[n], 172.0, n, cross=[yb[m] for m in NETS if yb[m] > yb[n]])
    # P2
    rect(bx, 179.0, bw, 6.0, fill="#fcfcfc", rx=0.5); text(bx + 1.0, 181.2, "-P2 PZEM-016", 1.3, bold=True); text(bx + 1.0, 183.2, "U(L1″–N″), I przez CT na L1″", 0.95); text(bx + 1.0, 184.6, "RS485 adres 2", 0.95)
    xa_, xb_ = 128.0, 135.0
    dot(xa_, yb["L1"], COL["L1"]); vwire(xa_, yb["L1"], 179.0, "L1", cross=[yb[m] for m in NETS if m != "L1"])
    dot(xb_, yb["N"], COL["N"]); vwire(xb_, yb["N"], 179.0, "N", cross=[yb["PE"]])
    ct(135.5, yb["L1"], 1.6); text(135.5, yb["L1"] - 2.2, "CT -P2", 0.95, "middle", col=COL["S"])
    # P3
    rect(bx, 187.0, bw, 5.2, fill="#fcfcfc", rx=0.5); text(bx + 1.0, 189.2, "-P3 ZMPT101B", 1.3, bold=True); text(bx + 1.0, 191.2, "U(N″–PE″) → -A5 ADS1115 → RPi", 0.95)
    xc_, xd_ = 137.6, 139.4
    dot(xc_, yb["N"], COL["N"]); vwire(xc_, yb["N"], 190.5, "N", cross=[yb["PE"]]); wire([(xc_, 190.5), (bx + bw, 190.5)], "N")
    dot(xd_, yb["PE"], COL["PE"]); wire([(xd_, yb["PE"]), (xd_, 191.7), (bx + bw, 191.7)], "PE")
    text(bx, 195.2, "DUT na osobnej płycie izolacyjnej; gniazda opisane „TYLKO DUT – PE PRZEŁĄCZANE”", 0.95, italic=True)

def ladder():
    """pas dolny: sterowanie 230 V – dwie kolumny szczebli"""
    y_top = 198.0
    rect(5.0, y_top, 101.0, 92.0, fill="white", lw=0.3)
    text(6.2, y_top + 2.6, "STEROWANIE 230 V (cewki) – zasilanie z -F6: L230 / N230", 1.6, bold=True)
    yc = y_top + 8.5
    xa = 7.0
    text(xa, yc + 0.5, "L230", 1.3, "start", bold=True, col=COL["C"]); wire([(xa + 7.0, yc), (xa + 10.0, yc)], "C")
    hcontact(xa + 10.0, yc, "NO", 6.0); rect(xa + 11.0, yc - 4.8, 2.4, 1.6, lw=0.22); line(xa + 12.2, yc - 3.2, xa + 12.2, yc - 1.2, lw=0.22, dash="0.5,0.4")
    text(xa + 14.6, yc - 3.0, "-S1 kluczyk „TRYB TESTOWY” (NO)", 1.15)
    wire([(xa + 16.0, yc), (xa + 46.0, yc)], "C")
    hcontact(xa + 46.0, yc, "NC", 6.0); arc(xa + 49.0, yc - 4.2, 1.3, 180, 360); line(xa + 49.0, yc - 4.2, xa + 49.0, yc - 1.4, lw=0.22, dash="0.5,0.4")
    text(xa + 53.0, yc - 3.0, "-S0 E-STOP (NC)", 1.15)
    wire([(xa + 52.0, yc), (xa + 62.0, yc)], "C"); text(xa + 63.0, yc + 0.5, "Lc = zasilanie cewek", 1.3, bold=True, col=COL["C"])
    cols = [(8.0, 54.0), (58.0, 104.0)]
    rungs = [
        ("—", "-H1", "lamp", "#bfe8bf", []),
        ("-A4:CH7", "-K2", "coil", None, []),
        ("-A12:O1", "-K3", "coil", None, []),
        ("-A4:CH1", "-K4", "coil", None, []),
        ("-A12:O2", "-K5", "coil", None, [("NC", "-B1 θ85°C")]),
        ("-A4:CH2", "-K6", "coil", None, [("NC", "-K7 NC2")]),
        ("-A4:CH3", "-K7", "coil", None, [("NC", "-K6 NC2")]),
        ("-A12:O3", "-K8", "coil", None, []),
        ("-A13:O1", "-K9", "coil", None, []),
        ("-A13:O2", "-K10", "coil", None, []),
        ("-A13:O3", "-K11", "coil", None, []),
        ("-A4:CH4", "-K12a/b", "coil", None, []),
        ("-A4:CH5", "-H2", "lamp", "#f3b7b7", []),
        ("-A4:CH6", "-M1", "fan", None, []),
    ]
    per = 7; dy = 5.6
    for ci, (x0, x1) in enumerate(cols):
        sub = rungs[ci * per:(ci + 1) * per]
        yl0 = y_top + 14.0
        yl1 = yl0 + dy * len(sub) + 0.5
        wire([(x0, yl0), (x0, yl1)], "C"); wire([(x1, yl0), (x1, yl1)], "N")
        text(x0, yl0 - 1.0, "Lc", 1.2, "middle", bold=True, col=COL["C"]); text(x1, yl0 - 1.0, "N230", 1.2, "middle", bold=True, col=COL["N"])
        for ri, (src, name, kind, fill, extra) in enumerate(sub):
            y = yl0 + 3.0 + ri * dy
            dot(x0, y, COL["C"]); dot(x1, y, COL["N"])
            xc = x0 + 2.0
            wire([(x0, y), (xc, y)], "C")
            if src != "—":
                hcontact(xc, y, "NO", 6.0, mark="relay" if src.startswith("-A4") else None)
                text(xc + 3.0, y - 2.4, src, 1.05, "middle")
                if name == "-M1":
                    # równoległy termostat -B2 (NO)
                    wire([(xc, y), (xc, y + 2.6)], "C"); wire([(xc + 6.0, y), (xc + 6.0, y + 2.6)], "C")
                    hcontact(xc, y + 2.6, "NO", 6.0); text(xc + 3.0, y + 4.6, "-B2 θ60°C", 1.0, "middle")
                xc += 6.0
            else:
                wire([(xc, y), (xc + 6.0, y)], "C"); xc += 6.0
            for kind2, lab in extra:
                wire([(xc, y), (xc + 1.0, y)], "C"); hcontact(xc + 1.0, y, kind2, 6.0); text(xc + 4.0, y - 2.4, lab, 1.0, "middle"); xc += 7.0
            xcoil = x1 - 7.0
            wire([(xc, y), (xcoil - 3.2, y)], "C")
            if kind == "lamp":
                lamp(xcoil, y, 1.7, fill); wire([(xcoil + 1.7, y), (x1, y)], "N"); text(xcoil - 4.2, y + 0.5, name, 1.2, "end", bold=True)
            elif kind == "fan":
                fan(xcoil, y, 1.9); wire([(xcoil + 1.9, y), (x1, y)], "N"); text(xcoil - 4.2, y + 0.5, name, 1.2, "end", bold=True)
            else:
                coil(xcoil, y, 6.4, 3.0, name); wire([(xcoil + 3.2, y), (x1, y)], "N")
                rect(xcoil - 1.2, y + 1.9, 2.4, 1.1, lw=0.2); wire([(xcoil - 3.2, y), (xcoil - 3.2, y + 2.45), (xcoil - 1.2, y + 2.45)], "C"); wire([(xcoil + 1.2, y + 2.45), (xcoil + 3.2, y + 2.45), (xcoil + 3.2, y)], "N")
    ylist = y_top + 14.0 + dy * 7 + 6.0
    text(6.2, ylist, "Funkcje: -H1 lampa zielona (Lc OK) · -A11 (kolumna A) stycznik główny wyjścia · -K2 zła kolejność faz (F9) · -K3 zanik L3 (F8) · -K4 luźny styk L1, impulsy 0,1–0,5 s (F11)", 1.05)
    text(6.2, ylist + 2.2, "-K5 rezystor -R1 w tor (F12) · -K6 boost +30 V (F10b) · -K7 buck −30 V (F10a) · -K8 przerwa N (F4) · -K9 przerwa PE (F1) · -K10 zamiana N↔PE (F5) · -K11 zamiana L↔N (F7)", 1.05)
    text(6.2, ylist + 4.4, "-K12a/b pominięcie RCD (F13) · -H2 lampa czerwona „usterka aktywna” · -M1 wentylator radiatora (z -A4:CH6 lub termostatu -B2) · -A4:CH8 rezerwa", 1.05)
    text(6.2, ylist + 7.0, "z L230/N230 (niezależnie od kluczyka): -G1 zasilacz 5 V (RPi) · -A12…-A15 Shelly Wave Pro 3 (L, N) · -A20 DLB-A1 przez -X6 (L, N, PE).  Z Lc/N230: -A11 (stycznik główny).", 1.05)
    text(6.2, ylist + 9.2, "wejścia zwrotne 230 V do SW Shelly Wave: Lc→-A12:SW1 (klucz+E-STOP OK) · -S0 NO→-A12:SW2 · -K13 CKF-B→-A12:SW3 · -A11: stan własnych styków przez Z-Wave", 1.0)
    text(6.2, ylist + 11.4, "RV = warystor S10K275 równolegle do każdej cewki. -K6/-K7: blokada wzajemna stykami NC2. -K2, -K10, -K11, -K12: styczniki przełączne (nigdy oba tory). Przewody cewek 1,0 mm².", 1.0)

def selv_panel():
    x0, y0, w = 110.0, 198.0, 95.0
    rect(x0, y0, w, 68.0, fill="white", lw=0.3)
    text(x0 + 1.2, y0 + 2.6, "STEROWNIK I ŁĄCZNOŚĆ (SELV 5 V)", 1.6, bold=True)
    box(x0 + 1.0, y0 + 4.0, 46.0, 9.0, "-G1  Mean Well HDR-60-5", ["wej. L230/N230/PE · wyj. +5 V 6,5 A →", "-A1 (USB-C), -A4, -A5"], 1.45, 1.15, 1.75)
    box(x0 + 48.0, y0 + 4.0, 46.0, 9.0, "Magistrala RS485 Modbus RTU", ["-A6 master → -P1 SDM630 (adr 1) → -P2 PZEM-016", "(adr 2); LiYCY 2×0,5; 120 Ω na końcach"], 1.45, 1.1, 1.75)
    box(x0 + 1.0, y0 + 14.0, 93.0, 17.0, "-A1  Raspberry Pi 5 (4 GB)  +  -A2 Raspberry Pi Touch Display 2 (7″, DSI, w drzwiach)", [
        "USB: -A3 kontroler Z-Wave 800 EU (LR) ⇄ radio 868 MHz ⇄ -A11…-A15     USB: -A6 konwerter USB–RS485 (izolowany)",
        "GPIO: -A4 płytka 8 przekaźników 10 A (opto) → styki CH1…CH8 drabinki (CH1 -K4, CH2 -K6, CH3 -K7, CH4 -K12, CH5 -H2, CH6 -M1, CH7 -K2, CH8 rezerwa)",
        "I²C: -A5 ADS1115 ← -P3 ZMPT101B (U N″–PE″)     karta microSD, aktywne chłodzenie, zasilanie USB-C z -G1",
        "oprogramowanie: Z-Wave JS UI + aplikacja nadzorcza (automat stanów usterek, blokady wzajemne, limity czasu, dziennik), opcjonalnie Home Assistant",
    ], 1.45, 1.1, 1.8)
    # Wave Pro 3 tabela
    ty = y0 + 32.0
    rect(x0 + 1.0, ty, 93.0, 24.0, fill="#fcfcfc", lw=0.32, rx=0.6)
    text(x0 + 2.2, ty + 2.6, "-A11 … -A15  Shelly Wave Pro 3 (Z-Wave, DIN): styki bezpotencjałowe 16 A O1–O3, wejścia SW1–SW3 230 V (+1 szt. zapas)", 1.35, bold=True)
    rows = [("-A11", "O1 L1  O2 L2  O3 L3 = stycznik główny (zasilany z Lc)", "SW1–SW3 rezerwa"),
            ("-A12", "O1→-K3   O2→-K5   O3→-K8", "SW1 Lc OK · SW2 -S0 NO · SW3 -K13 CKF-B"),
            ("-A13", "O1→-K9   O2→-K10   O3→-K11", "SW1–SW3 rezerwa"),
            ("-A14", "O1→-R2 (F2)   O2→-R3 (F3)   O3→mostek N′–PE′ (F6)", "SW1–SW3 rezerwa"),
            ("-A15", "O1→-R4 (F14)   O2→-V1 zestaw DC (F15)   O3→rezerwa", "SW1–SW3 rezerwa")]
    yy = ty + 5.6
    for a, o, s in rows:
        text(x0 + 2.2, yy, a, 1.25, bold=True); text(x0 + 10.0, yy, o, 1.15); text(x0 + 56.0, yy, s, 1.1); yy += 3.4
    # DLB
    box(x0 + 1.0, y0 + 57.5, 93.0, 9.5, "-A20  moduł DLB-A1 – NA ZEWNĄTRZ obudowy", [
        "zasilanie L, N, PE z zacisków -X6 (L230/N230/PE) · wejścia CT ← -T2, -T3, -T4 przez dławik M25 wielootworowy",
        "antena 433 MHz na zewnątrz · łączność radiowa z wallboxem",
    ], 1.45, 1.1, 1.75)

def legend_title():
    x0, y0 = 110.0, 268.0
    rect(x0, y0, 44.0, 22.0, lw=0.3)
    text(x0 + 1.2, y0 + 2.5, "Legenda", 1.6, bold=True)
    items = [("L1", "L1"), ("L2", "L2"), ("L3", "L3"), ("N", "N"), ("PE", "PE"), ("C", "230 V cewki/sterowanie"), ("S", "sygnały / CT")]
    yy = y0 + 5.0
    for n, lab in items:
        wire([(x0 + 1.5, yy), (x0 + 6.5, yy)], n); text(x0 + 7.5, yy + 0.5, lab, 1.15); yy += 2.25
    dot(x0 + 24.0, y0 + 5.0, "#111"); text(x0 + 26.0, y0 + 5.5, "połączenie", 1.1); line(x0 + 22.5, y0 + 7.4, x0 + 23.3, y0 + 7.4); arc(x0 + 24.0, y0 + 7.4, 0.7, 180, 360); line(x0 + 24.7, y0 + 7.4, x0 + 25.5, y0 + 7.4); text(x0 + 26.0, y0 + 7.8, "skrzyżowanie bez połączenia", 1.1)
    text(x0 + 23.0, y0 + 10.1, "-A4:CHx styk GPIO RPi", 1.05); text(x0 + 23.0, y0 + 12.4, "-A1x:Ox styk Shelly Wave", 1.05)
    text(x0 + 23.0, y0 + 14.7, "symbole IEC 60617", 1.05); text(x0 + 23.0, y0 + 17.0, "oznaczenia IEC 81346", 1.05)
    text(x0 + 23.0, y0 + 19.6, "części + linki: str. 2–4", 1.05, bold=True)
    x1 = 156.0
    rect(x1, y0, 49.0, 22.0, lw=0.4)
    line(x1, y0 + 6.0, x1 + 49, y0 + 6.0, lw=0.3); line(x1, y0 + 12.0, x1 + 49, y0 + 12.0, lw=0.3); line(x1, y0 + 17.0, x1 + 49, y0 + 17.0, lw=0.3)
    text(x1 + 1.2, y0 + 2.6, "AMPERE POINT", 2.3, bold=True); text(x1 + 1.2, y0 + 4.9, "Rozdzielnica testowa – symulator usterek", 1.3)
    text(x1 + 1.2, y0 + 8.4, "Schemat zasadniczy: tor mocy, sterowanie, pomiary", 1.35, bold=True); text(x1 + 1.2, y0 + 10.6, "Arkusz 1/1 · A4 · wszystkie elementy i połączenia", 1.15)
    text(x1 + 1.2, y0 + 14.0, "przyłącze 32 A, testy ≤16 A · CEE 32/16 A · 2× Schuko · cewki 230 V", 1.1); text(x1 + 1.2, y0 + 16.0, "RPi 5 + Z-Wave (Shelly Wave Pro 3) + GPIO · DLB-A1 zewn.", 1.1)
    text(x1 + 1.2, y0 + 19.2, "Rew. B · 2026-10-07 · do weryfikacji przez elektryka SEP E/D", 1.1); text(x1 + 1.2, y0 + 21.0, "Opracowanie: Claude dla D. Cękała / Ampere Point", 1.0)

def main():
    header(); column_A(); column_B(); ladder(); selv_panel(); legend_title()
    emit('</svg>')
    svg = "\n".join(out)
    here = os.path.dirname(os.path.abspath(__file__))
    open(os.path.join(here, "schemat_A4.svg"), "w", encoding="utf-8").write(svg)
    import cairosvg
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=os.path.join(here, "schemat_A4.pdf"))
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(here, "schemat_A4.png"), dpi=200)
    print("OK")

if __name__ == "__main__":
    main()
