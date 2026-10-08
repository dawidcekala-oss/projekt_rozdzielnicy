# -*- coding: utf-8 -*-
"""Schemat blokowy (poglądowy) rozdzielnicy testowej – 2 strony A4 poziome:
   1) co z czym się łączy i jakim medium (bloki + nazwane połączenia),
   2) jak to współpracuje – cztery scenariusze krok po kroku.
Wyjście: schemat_blokowy.svg (str. 1), schemat_blokowy_2.svg (str. 2), schemat_blokowy.pdf (obie), .png."""
import math, os, html

W, H = 297.0, 210.0
out = []
def emit(s): out.append(s)
def esc(s): return html.escape(str(s))

C = {"moc": "#111111", "lc": "#c0152a", "l230": "#c0152a", "selv": "#1f4fd1", "radio": "#7a2fb0", "rs485": "#0f7a3a",
     "ct": "#7a2fb0", "fb": "#d97706", "term": "#666666", "pe": "#149114"}
FILL = {"moc": "#f4f4f4", "ust": "#fff4e5", "wyj": "#eef7ee", "pom": "#eaf1fb", "ster": "#f3eefb", "selv": "#eef3ff", "dut": "#ffffff"}

def line(x1, y1, x2, y2, col="#111", lw=0.3, dash=None, arrow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#ar_{col[1:]})"' if arrow else ""
    emit(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{lw}" stroke-linecap="round"{d}{m}/>')
def path(pts, col="#111", lw=0.3, dash=None, arrow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#ar_{col[1:]})"' if arrow else ""
    emit('<polyline points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + f'" fill="none" stroke="{col}" stroke-width="{lw}" stroke-linejoin="round" stroke-linecap="round"{d}{m}/>')
def rect(x, y, w, h, fill="white", col="#111", lw=0.3, rx=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    emit(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{col}" stroke-width="{lw}"{d}/>')
def text(x, y, s, size=1.4, anchor="start", col="#111", bold=False, italic=False):
    fw = ' font-weight="bold"' if bold else ""; fi = ' font-style="italic"' if italic else ""
    emit(f'<text x="{x:.2f}" y="{y:.2f}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{col}"{fw}{fi}>{esc(s)}</text>')
def wave(x1, y1, x2, y2, col, lw=0.32, amp=0.55, per=1.8, arrow=False):
    """linia falista (radio) między dwoma punktami"""
    L = math.hypot(x2 - x1, y2 - y1); n = max(int(L / 0.25), 4)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L; px, py = -uy, ux
    pts = []
    for i in range(n + 1):
        t = i / n; d = t * L; a = amp * math.sin(2 * math.pi * d / per)
        pts.append((x1 + ux * d + px * a, y1 + uy * d + py * a))
    path(pts, col, lw, arrow=arrow)
def vjump(x, y0, y1, ycross, col, lw=0.45, dash=None, arrow=False):
    """pion y0->y1 z półkolem (przeskok) na wysokości ycross"""
    r = 0.9; s_ = 1 if y1 > y0 else -1
    line(x, y0, x, ycross - s_ * r, col, lw, dash)
    emit(f'<path d="M{x:.2f},{ycross - s_ * r:.2f} A{r},{r} 0 0 {1 if s_ > 0 else 0} {x:.2f},{ycross + s_ * r:.2f}" fill="none" stroke="{col}" stroke-width="{lw}"/>')
    line(x, ycross + s_ * r, x, y1, col, lw, dash, arrow=arrow)
def dot(x, y, col="#111", r=0.55): emit(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{col}"/>')

def box(x, y, w, h, title, lines=(), fill="white", tsize=1.75, lsize=1.3, lh=1.85, tag=None, tagcol=None, col="#111", lw=0.35, title2=None):
    rect(x, y, w, h, fill=fill, col=col, lw=lw)
    text(x + 1.3, y + 2.6, title, tsize, bold=True)
    yy = y + 2.6
    if title2:
        yy += 1.9; text(x + 1.3, yy, title2, 1.35, bold=True, col="#333")
    yy += 0.6
    for ln in lines:
        yy += lh; text(x + 1.3, yy, ln, lsize)
    if tag:
        text(x + 1.3, y + h - 1.0, tag, 1.25, col=tagcol or C["lc"], bold=True)

def defs():
    emit("<defs>")
    for c in set(C.values()) | {"#111111", "#111"}:
        emit(f'<marker id="ar_{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    emit("</defs>")

def page_frame(title, sub):
    emit(f'<rect width="{W}" height="{H}" fill="white"/>')
    rect(3, 3, W - 6, H - 6, fill="none", lw=0.5, rx=0)
    text(5, 8.2, title, 3.0, bold=True)
    text(5, 11.6, sub, 1.45, italic=True)

GX = [6.0 + i * 36.0 for i in range(8)]   # siatka 8 kolumn, szerokość 30.5, przerwa 5.5
BW = 30.5

def legend(x, y):
    items = [("moc", "tor mocy 3×400/230 V (L1 L2 L3 N PE)", 0.9, None, False),
             ("l230", "230 V sterowanie: L230/N230 (za RCBO -F6), LT1", 0.45, "1.2,0.8", False),
             ("lc", "Lc = 230 V cewek: tylko kluczyk + E-STOP OK", 0.6, None, False),
             ("selv", "SELV 5 V: USB, GPIO, I²C, DSI", 0.4, None, False),
             ("rs485", "RS485 Modbus RTU (LiYCY 2×0,5)", 0.4, "0.9,0.6", False),
             ("radio", "radio: Z-Wave 868 MHz / DLB 433 MHz", 0.35, None, True),
             ("ct", "przekładniki prądowe (sygnał)", 0.3, "0.4,0.4", False)]
    xx = x
    for key, lab, lw, dash, isw in items:
        if isw: wave(xx, y, xx + 7, y, C[key])
        else: line(xx, y, xx + 7, y, C[key], lw, dash)
        text(xx + 8.2, y + 0.5, lab, 1.2)
        xx += 8.2 + len(lab) * 0.64 + 3.0

# ------------------------------------------------------------------ STRONA 1
def page1():
    page_frame("ROZDZIELNICA TESTOWA – SCHEMAT BLOKOWY: CO Z CZYM SIĘ ŁĄCZY I JAK WSPÓŁPRACUJE",
               "Widok poglądowy do schematu zasadniczego (rew. C). Strzałki = kierunek przepływu energii lub informacji; „← -A12:O1” przy bloku = który styk Shelly/GPIO zasila cewkę tego bloku.")
    legend(5.0, 15.0)
    defs()
    # --- wiersz 1: ZASILANIE I ZABEZPIECZENIA (y 20..44)
    y1, h1 = 20.0, 24.0
    text(GX[0], y1 - 0.8, "1 · ZASILANIE I ZABEZPIECZENIA  (3×400/230 V, 32 A, 6 mm²)", 1.6, bold=True, col="#444")
    r1 = [
        ("-W0  wtyk CEE 32 A 5P", ["przewód H07RN-F 5G4, 5 m", "do gniazda 32 A w instalacji", "(sieć TN-S, własny SPD w instalacji)"], FILL["moc"], None),
        ("-X1  szybkozłączki + CT DLB", ["wejście L1 L2 L3 N PE (6 mm²)", "-T2/-T3/-T4: przekładniki 100 A", "modułu DLB-A1 na L1/L2/L3"], FILL["moc"], None),
        ("-Q1  rozłącznik 4P 40 A", ["ręczne odłączenie całości,", "blokowany kłódką", "-W1/-W2: bloki N i PE (7 zac.)"], FILL["moc"], None),
        ("-F6 RCBO · -F7 B10  odczep", ["-F6 1P+N B6 30 mA → L230/N230:", "  sterowanie, -G1, Shelly, -A20", "-F7 B10 → LT1: pierwotne -T1"], FILL["moc"], None),
        ("-F1 RCD 30 mA + -K12a/b", ["RCD 4P 40 A (z magazynu, typ A)", "-K12: styki NO omijają RCD", "= usterka F13 „brak RCD”"], FILL["ust"], "cewki -K12a/b ← -A4:CH4 (GPIO)"),
        ("-F3  wyłącznik 3P B16", ["ogranicza prąd testów do 16 A", "(styki 25 A, przewody 2,5 mm²)", "chroni sekcję usterek i gniazda"], FILL["moc"], None),
        ("-K1  stycznik główny 4NO", ["jedyny element, który włącza", "napięcie na gniazda; opada, gdy", "Lc znika (E-STOP / kluczyk)"], FILL["moc"], "cewka ← Lc przez -A11:O1 (Shelly)"),
        ("-K2  zamiana L2↔L3 (F9)", ["zła kolejność faz; przełączany", "tylko przy wyłączonym -K1", "-K13 CKF-B potwierdza na wyjściu"], FILL["ust"], "cewka ← -A4:CH7 (GPIO)"),
    ]
    for i, (t, ls, f, tag) in enumerate(r1):
        box(GX[i], y1, BW, h1, t, ls, f, tag=tag)
    for i in range(7):
        line(GX[i] + BW, y1 + h1 / 2, GX[i + 1], y1 + h1 / 2, C["moc"], 0.9, arrow=True)
    text(GX[5] + BW + 0.6, y1 + h1 / 2 - 1.0, "16 A", 1.1, col="#444")
    # --- wiersz 2: SEKCJA USTEREK (y 58..86), kierunek prawo -> lewo
    y2, h2 = 58.0, 28.0
    text(GX[2], y2 - 0.8, "2 · SEKCJA USTEREK  (prawo → lewo; usterka = cewka pod napięciem)", 1.6, bold=True, col="#444")
    text(GX[5], y2 - 0.8, "bez napięcia na cewkach = instalacja poprawna", 1.3, italic=True, col="#444")
    r2 = [
        ("-K10  zamiana N↔PE (F5)", ["styki NC: N′→N″, PE′→PE″", "styki NO: krzyżują N i PE", "(wyjście -K10 = szyny N″/PE″)"], "cewka ← -A13:O2 (Shelly)"),
        ("drabinka upływów", ["F2  -R2 100 Ω: słabe PE ← -A14:O1", "F3  -R3 220 kΩ: PE pod U ← -A14:O2", "F6  mostek N′–PE′ ← -A14:O3", "F14 -R4 6,8 kΩ: 34 mA ← -A15:O1", "F15 dioda+C: 6 mA= ← -A15:O2"], None),
        ("-K9  przerwa PE (F1)", ["2 styki NC równolegle w PE;", "styk NO → -A13:SW1 potwierdza,", "że PE jest przerwane"], "cewka ← -A13:O1 (Shelly)"),
        ("-K8  przerwa N (F4)", ["styki NC w przewodzie N;", "N″ „pływa” – ładowarka 1-faz.", "widzi dziwne napięcia"], "cewka ← -A12:O3 (Shelly)"),
        ("-T1 + -K6/-K7  U za niskie/wysokie", ["toroid 2×30 V w szereg z L1:", "F10a buck 200 V · F10b boost 260 V", "-K6/-K7 przełączają pierwotne LT1", "w spoczynku NC·NC zwierają P1–P2"], "cewki ← -A4:CH2 / CH3 (blokada NC)"),
        ("-R1 + -K5  przepalony styk (F12)", ["0,5 Ω / 200 W w szereg z L1", "(128 W przy 16 A) na radiatorze", "-B1 85 °C przerywa cewkę -K5", "-M1 wentylator ← -A4:CH6 / -B2"], "cewka -K5 ← -A12:O2 (Shelly)"),
        ("-K3  zanik fazy L3 (F8)", ["styki NC w L3 otwierają się;", "ładowarka 3-faz. traci jedną fazę"], "cewka ← -A12:O1 (Shelly)"),
        ("-K4  luźny styk L1 (F11)", ["impulsy 0,1–0,5 s przerw w L1", "(szybkie – dlatego z GPIO, nie", "z Z-Wave)"], "cewka ← -A4:CH1 (GPIO)"),
    ]
    for i, (t, ls, tag) in enumerate(r2):
        box(GX[i], y2, BW, h2, t, ls, FILL["ust"], lsize=1.22, lh=1.75, tag=tag)
    for i in range(7, 0, -1):
        line(GX[i], y2 + h2 / 2, GX[i - 1] + BW, y2 + h2 / 2, C["moc"], 0.9, arrow=True)
    # łącznik wiersz 1 -> 2 (prawy skraj)
    xk = GX[7] + BW / 2
    path([(xk, y1 + h1), (xk, y2)], C["moc"], 0.9, arrow=True)
    text(xk + 1.0, y1 + h1 + 8.5, "L1′ L2′ L3′ N′ PE′", 1.15, col="#444")
    # --- wiersz 3: WYJŚCIA, POMIARY, BADANA ŁADOWARKA (y 100..130)
    y3, h3 = 100.0, 30.0
    text(GX[0], y3 - 0.8, "3 · WYJŚCIA, POMIARY, DUT", 1.6, bold=True, col="#444")
    box(GX[0], y3, BW, h3, "-A20  moduł DLB-A1", ["NA ZEWNĄTRZ obudowy", "zasilanie L/N/PE z -X6 (L230)", "wejścia CT ← -T2/-T3/-T4", "radio 433 MHz → wallbox:", "dynamiczne równoważenie mocy"], FILL["pom"], lsize=1.22, lh=1.75)
    box(GX[1], y3, 2 * BW + 5.5, h3, "szyny wyjściowe L1″ L2″ L3″ N″ PE″  +  pomiary", [
        "-K13 CKF-B: kolejność / zanik faz → styk → -A12:SW3",
        "-P2a/-P2b/-P2c PZEM-016: U, I, P, kWh każdej fazy (CT na L″, U wzgl. N",
        "   sprzed -K8/-K10) → RS485 Modbus adr. 1/2/3 → -A6 → RPi",
        "-P3 ZMPT101B: napięcie N″–PE″ → -A5 ADS1115 (I²C) → RPi",
        "zaciski N″/PE″: szybkozłączki -X1 (magazyn); DUT na płycie izolacyjnej"], FILL["pom"], lsize=1.22, lh=1.75)
    box(GX[4], y3, BW, h3, "-X2  gniazdo CEE 32 A", ["5P, IP44; elektrycznie 16 A", "(za -F3); ładowarka 3-faz.", "22 kW będzie ograniczona"], FILL["wyj"])
    box(GX[5], y3, BW, h3, "-X3  gniazdo CEE 16 A", ["5P, IP44; ładowarka 11 kW", "lub przenośna 3-faz."], FILL["wyj"])
    box(GX[6], y3, BW, h3, "-F5 + -K11 → -X4a/-X4b Schuko", ["-F5 2P B16 (L1″ + N″)", "-K11 zamiana L↔N (F7):", "styki NC prosto, NO na krzyż", "2 gniazda 16 A równolegle"], FILL["wyj"], lsize=1.22, lh=1.75, tag="cewka -K11 ← -A13:O3 (Shelly)")
    box(GX[7], y3, BW, h3, "DUT: ładowarka EV + pojazd", ["badana ładowarka (wallbox lub", "przenośna) + samochód / tester", "EVSE jako obciążenie 6–16 A", "reakcję ładowarki obserwuje", "operator i PZEM/CKF-B"], FILL["dut"], lsize=1.22, lh=1.75, col="#7a4a1e", lw=0.5)
    # łącznik wiersz 2 -> 3 (lewy skraj: -K10 -> szyny)
    path([(GX[0] + BW / 2, y2 + h2), (GX[0] + BW / 2, y2 + h2 + 7.0), (GX[1] + 4.0, y2 + h2 + 7.0), (GX[1] + 4.0, y3)], C["moc"], 0.9, arrow=True)
    text(GX[1] + 6.5, y2 + h2 + 5.8, "→ szyny: N″ PE″ po -K10; L1″ L2″ L3″ po -K4…-K3", 1.15, col="#444")
    # szyny -> gniazda
    xs_end = GX[1] + 2 * BW + 5.5
    line(xs_end, y3 + h3 / 2, GX[4], y3 + h3 / 2, C["moc"], 0.9, arrow=True)
    line(GX[4] + BW, y3 + h3 / 2, GX[5], y3 + h3 / 2, C["moc"], 0.9, arrow=True)
    line(GX[5] + BW, y3 + h3 / 2, GX[6], y3 + h3 / 2, C["moc"], 0.9, arrow=True)
    line(GX[6] + BW, y3 + h3 / 2, GX[7], y3 + h3 / 2, C["moc"], 0.9, arrow=True)
    text(GX[5] + BW / 2, y3 - 0.8, "wtyk badanej ładowarki do jednego z gniazd →", 1.15, col="#444", anchor="middle")
    # CT DLB: z -X1 (wiersz 1) do -A20 (wiersz 3) – pion w przerwie między blokami
    xct = GX[1] - 2.0
    path([(GX[1] + 4.0, y1 + h1), (GX[1] + 4.0, y1 + h1 + 4.0), (xct, y1 + h1 + 4.0), (xct, y3 + 6.0), (GX[0] + BW, y3 + 6.0)], C["ct"], 0.35, dash="0.5,0.5", arrow=True)
    text(xct - 0.8, y1 + h1 + 8.0, "CT ×3", 1.1, col=C["ct"], anchor="end")
    # radio DLB -> wallbox
    wave(GX[0] + BW / 2, y3 + h3, GX[0] + BW / 2, y3 + h3 + 3.5, C["radio"])
    wave(GX[0] + BW / 2, y3 + h3 + 3.5, GX[7] + BW / 2, y3 + h3 + 3.5, C["radio"])
    wave(GX[7] + BW / 2, y3 + h3 + 3.5, GX[7] + BW / 2, y3 + h3, C["radio"], arrow=True)
    text(GX[5] + BW / 2 + 6.0, y3 + h3 + 2.6, "433 MHz: -A20 → wallbox (limit prądu ładowania wg -T2…-T4)", 1.1, col=C["radio"], anchor="middle")
    # --- L230/N230: odczep z -F6 (wiersz 1) w dół do magistrali sterowania (y 139)
    yb = 139.0
    xl = GX[3] + BW + 2.5   # pion w przerwie 144.5..150 -> x=147
    path([(GX[3] + BW, y1 + h1 - 4.0), (xl, y1 + h1 - 4.0), (xl, yb)], C["l230"], 0.5, dash="1.2,0.8")
    line(6.0, yb, W - 6.0, yb, C["l230"], 0.5, dash="1.2,0.8")
    text(72.5, yb - 0.8, "L230/N230 – 230 V sterowania za RCBO -F6 (niezależne od kluczyka i od -F1) → -G1, -S1, -A11…-A15, -A20", 1.1, col=C["l230"])
    # LT1: z odczepu do -T1 (wiersz 2)
    path([(GX[3] + BW - 4.0, y1 + h1), (GX[3] + BW - 4.0, y1 + h1 + 7.0), (GX[4] + BW / 2, y1 + h1 + 7.0), (GX[4] + BW / 2, y2)], C["l230"], 0.45, dash="1.2,0.8", arrow=True)
    text(GX[4] + 1.0, y1 + h1 + 4.9, "LT1 (z -F7 B10) → pierwotne -T1", 1.1, col=C["l230"])
    # drop L230 do -A20
    path([(GX[0] + 24.0, yb), (GX[0] + 24.0, y3 + h3)], C["l230"], 0.45, dash="1.2,0.8", arrow=True)
    # --- wiersz 4: STEROWANIE (y 145..205)
    y4 = 145.0
    text(GX[2], y4 - 0.8, "4 · STEROWANIE: kluczyk i E-STOP (sprzętowo) · Raspberry Pi 5 z ekranem (programowo) · Shelly po Z-Wave i przekaźniki GPIO (wykonawczo)", 1.6, bold=True, col="#444")
    box(GX[0], y4 + 1.0, BW, 14.0, "-S1  kluczyk TRYB TESTOWY", ["w drzwiach; styk NO; kluczyk", "wyjmowany w położeniu 0"], FILL["ster"], lsize=1.22, lh=1.75)
    box(GX[1], y4 + 1.0, BW, 14.0, "-S0  E-STOP (grzybek)", ["w drzwiach; styk NC w szeregu", "+ styk NO → -A12:SW2 (info)"], FILL["ster"], lsize=1.22, lh=1.75)
    box(GX[7], y4 + 1.0, BW, 18.0, "-A11  Shelly Wave Pro 3", ["„wyłącznik główny”: zasilany z Lc", "O1 zamyka obwód cewki -K1", "O2, O3 rezerwa; komenda po Z-Wave", "bez Lc = -K1 nie może się załączyć"], FILL["ster"], lsize=1.22, lh=1.75)
    # Lc: S1 -> S0 -> A11 -> (prawy margines) -> K1
    ylc = y4 + 8.0
    line(GX[0] + BW, ylc, GX[1], ylc, C["lc"], 0.6, arrow=True)
    line(GX[1] + BW, ylc, GX[7], ylc, C["lc"], 0.6, arrow=True)
    text(GX[2] + 2.0, ylc - 1.0, "Lc = 230 V cewek: jest tylko gdy kluczyk w TEST i E-STOP zwolniony → zasila wszystkie cewki usterek (przez styki Shelly/GPIO) i -A11", 1.15, col=C["lc"])
    path([(GX[0] + BW - 4.0, yb), (GX[0] + BW - 4.0, y4 + 1.0)], C["l230"], 0.45, dash="1.2,0.8", arrow=True)
    xm = W - 4.2
    path([(GX[7] + BW, y4 + 6.0), (xm, y4 + 6.0), (xm, 17.2), (GX[6] + BW / 2, 17.2), (GX[6] + BW / 2, y1)], C["lc"], 0.6, arrow=True)
    text(GX[6] + BW / 2 + 2.0, y1 - 1.2, "Lc → cewka -K1 (A1/A2) przez -A11:O1 (prawy margines)", 1.1, col=C["lc"])
    # G1
    box(GX[0], y4 + 19.0, BW, 18.0, "-G1  zasilacz 5 V 6,5 A", ["Mean Well HDR-60-5 na TH35", "wej. L230/N230/PE", "wyj. +5 V → RPi (USB-C), -A4, -A5"], FILL["selv"], lsize=1.22, lh=1.75)
    path([(GX[0] + 3.0, yb), (GX[0] + 3.0, y4 + 19.0)], C["l230"], 0.45, dash="1.2,0.8", arrow=True)
    # A6 / A5
    box(GX[1], y4 + 19.0, BW, 18.0, "-A6  USB ⇄ RS485 (izol.)", ["master Modbus RTU → -P2a/b/c", "LiYCY 2×0,5, 120 Ω na końcach"], FILL["selv"], lsize=1.22, lh=1.75)
    box(GX[1], y4 + 41.0, BW, 18.0, "-A5  ADS1115 (ADC I²C)", ["czyta -P3 ZMPT101B (0–5 V)", "= napięcie N″–PE″ dla RPi"], FILL["selv"], lsize=1.22, lh=1.75)
    # RPi
    box(GX[2], y4 + 19.0, 2 * BW + 5.5, 40.0, "-A1  Raspberry Pi 5 (4 GB)  +  -A2 ekran dotykowy 7″ (DSI, w drzwiach)", [
        "oprogramowanie: automat stanów usterek, blokady (jedna usterka na grupę, F16 zablokowana),",
        "limity czasu (F10/F12 ≤ 60 s), dziennik, ekran: wybór usterki, START/STOP, odczyty U/I/P/kWh",
        "USB: -A3 Z-Wave · -A6 RS485      GPIO (40 pin): -A4 przekaźniki      I²C: -A5      DSI: -A2",
        "watchdog sprzętowy: po zawieszeniu restart → GPIO = wejścia → przekaźniki -A4 opadają",
        "+ Shelly: auto-off 60 s na każdym wyjściu (usterka nie trwa bez nadzoru)"], FILL["selv"], lsize=1.22, lh=1.75)
    # A3, A4
    box(GX[4], y4 + 19.0, BW, 14.0, "-A3  kontroler Z-Wave USB", ["seria 800, EU 868 MHz, LR", "sieć Z-Wave z -A11…-A15"], FILL["selv"], lsize=1.22, lh=1.75)
    box(GX[4], y4 + 37.0, BW, 22.0, "-A4  8 przekaźników GPIO (5 A)", ["szybkie / krytyczne czasowo:", "CH1 -K4 · CH2 -K6 · CH3 -K7", "CH4 -K12a+b · CH6 -M1 · CH7 -K2", "CH8 -H1 · CH5 rezerwa"], FILL["ster"], lsize=1.22, lh=1.75, tag="styki: Lc → cewka (230 V)")
    # Shelly group
    box(GX[5], y4 + 19.0, 2 * BW + 5.5, 40.0, "-A12 … -A15  Shelly Wave Pro 3 (Z-Wave, DIN) – usterki „wolne”", [
        "każdy: 3 styki bezpotencjałowe 16 A (O1–O3) + 3 wejścia 230 V (SW1–SW3); zasilanie z L230/N230",
        "-A12: O1 -K3 · O2 -K5 · O3 -K8        SW1 ← Lc OK · SW2 ← -S0 NO · SW3 ← -K13 CKF-B",
        "-A13: O1 -K9 · O2 -K10 · O3 -K11      SW1 ← -K9 NO (PE przerwane)",
        "-A14: O1 -R2 (F2) · O2 -R3 (F3) · O3 mostek N′–PE′ (F6)",
        "-A15: O1 -R4 (F14) · O2 zestaw DC (F15) · O3 rezerwa      (+1 szt. zapas w magazynie)"], FILL["ster"], lsize=1.22, lh=1.75, tag="styki O: Lc → cewka / rezystor (230 V) · wejścia SW: informacja zwrotna do RPi")
    # lampki / wentylator
    box(GX[7], y4 + 23.0, BW, 36.0, "-H1 -H2 lampki · -M1 wentylator", ["-H1 zielona ← -A4:CH8: „stan", "  bezpieczny” (-K1 wył., -K13 bez U)", "-H2 czerwona ∥ cewka -K1:", "  „napięcie na gniazdach”", "-M1 wentylator radiatora -R1", "  ← -A4:CH6 lub -B2 60 °C", "-B1 85 °C w cewce -K5 (sprzęt.)"], FILL["ster"], lsize=1.22, lh=1.75)
    # SELV links
    line(GX[0] + BW, y4 + 31.0, GX[2], y4 + 31.0, C["selv"], 0.55, arrow=True); text(GX[1] + 2.0, y4 + 30.0, "+5 V", 1.1, col=C["selv"])
    line(GX[1] + BW, y4 + 26.0, GX[2], y4 + 26.0, C["selv"], 0.4, arrow=True); text(GX[1] + BW + 0.5, y4 + 25.0, "USB", 1.0, col=C["selv"])
    line(GX[1] + BW, y4 + 50.0, GX[2], y4 + 50.0, C["selv"], 0.4, arrow=True); text(GX[1] + BW + 0.5, y4 + 49.0, "I²C", 1.0, col=C["selv"])
    line(GX[3] + BW, y4 + 26.0, GX[4], y4 + 26.0, C["selv"], 0.4, arrow=True); text(GX[3] + BW + 0.5, y4 + 25.0, "USB", 1.0, col=C["selv"])
    line(GX[3] + BW, y4 + 48.0, GX[4], y4 + 48.0, C["selv"], 0.4, arrow=True); text(GX[3] + BW + 0.5, y4 + 47.0, "GPIO", 1.0, col=C["selv"])
    # radio Z-Wave
    wave(GX[4] + BW, y4 + 26.0, GX[5], y4 + 26.0, C["radio"], arrow=True)
    wave(GX[4] + BW / 2, y4 + 19.0, GX[4] + BW / 2, y4 + 14.5, C["radio"])
    wave(GX[4] + BW / 2, y4 + 14.5, GX[7], y4 + 14.5, C["radio"], arrow=True)
    text(GX[4] + BW / 2 + 1.5, y4 + 13.6, "Z-Wave 868 MHz: komendy do -A11 i -A12…-A15, stany z powrotem do RPi", 1.1, col=C["radio"])
    # RS485 z A6 do pomiarów (wiersz 3)
    xr = GX[1] + BW - 3.0
    vjump(xr, y4 + 19.0, y3 + h3, yb, C["rs485"], 0.45, dash="0.9,0.6", arrow=True)
    text(xr + 0.8, y4 + 16.5, "RS485", 1.05, col=C["rs485"])
    # sygnał ZMPT -> A5 (tag) i K13 -> A12:SW3 (tag) – opisane w blokach
    # Shelly L230 zasilanie
    vjump(GX[5] + 6.0, yb, y4 + 19.0, ylc, C["l230"], 0.45, dash="1.2,0.8", arrow=True)
    path([(GX[7] + 4.0, yb), (GX[7] + 4.0, y4 + 1.0)], C["l230"], 0.45, dash="1.2,0.8", arrow=True)
    # stopka
    text(5.0, H - 4.2, "Strona 1/2 · schemat blokowy do rew. C · Ampere Point / D. Cękała · pełne połączenia zacisk-po-zacisku: schemat zasadniczy (docs/pdf/03_…, str. 1)", 1.15, italic=True, col="#444")

# ------------------------------------------------------------------ STRONA 2
def page2():
    page_frame("JAK TO WSPÓŁPRACUJE – CZTERY SCENARIUSZE KROK PO KROKU",
               "Każdy krok nazywa element (oznaczenie jak na schemacie) i medium, którym idzie energia lub informacja. Kolory jak na stronie 1.")
    defs()
    cols = [
        ("A · NORMALNA SESJA ŁADOWANIA (bez usterki)", FILL["wyj"], [
            ("Operator", "przekręca -S1 kluczyk w TEST; -S0 E-STOP zwolniony → na szynie Lc pojawia się 230 V", "lc"),
            ("-A12:SW1", "wejście Shelly widzi Lc → po Z-Wave do RPi: „stanowisko uzbrojone”", "radio"),
            ("Ekran -A2 / RPi -A1", "operator wybiera „START”; RPi sprawdza: brak aktywnej usterki, -K13 bez napięcia", "selv"),
            ("RPi → -A3 ⇢ -A11", "komenda Z-Wave: zamknij O1", "radio"),
            ("-A11:O1 → cewka -K1", "Lc płynie przez O1 do A1/A2 stycznika głównego; -K1 zamyka 4 styki", "lc"),
            ("-K1 → -K2 → sekcja usterek → szyny L″ N″ PE″", "wszystkie cewki usterek bez napięcia = tor czysty; napięcie na -X2/-X3/-X4", "moc"),
            ("Ładowarka (DUT)", "wykrywa pojazd, zaczyna ładować 6–16 A; -H2 czerwona świeci (∥ cewka -K1)", "moc"),
            ("-P2a/b/c PZEM → RS485 → -A6 → RPi", "U, I, P, kWh każdej fazy na ekranie; -K13 CKF-B potwierdza kolejność faz (SW3)", "rs485"),
            ("-T2…-T4 → -A20 ⇢ wallbox", "niezależnie: CT na wejściu mierzą pobór, DLB-A1 radiem ogranicza moc ładowarki", "ct"),
        ]),
        ("B · TEST USTERKI F8 „ZANIK FAZY L3”", FILL["ust"], [
            ("Ekran -A2 / RPi -A1", "operator wybiera F8; RPi sprawdza macierz wykluczeń (jedna usterka z grupy L) i limit czasu", "selv"),
            ("RPi → -A3 ⇢ -A12", "komenda Z-Wave: zamknij O1 (styk przypisany do -K3)", "radio"),
            ("-A12:O1 → cewka -K3", "Lc przez styk O1 zasila cewkę; -K3 otwiera 2 styki NC w L3", "lc"),
            ("Szyna L3″ bez napięcia", "ładowarka 3-faz. traci jedną fazę w trakcie ładowania", "moc"),
            ("-K13 CKF-B → -A12:SW3", "przekaźnik zaniku faz zwalnia styk; Shelly raportuje do RPi po Z-Wave", "fb"),
            ("-P2c PZEM (L3) → RS485", "U(L3″) ≈ 0 V, I(L3″) = 0 A → ekran: „usterka F8 aktywna, L3 = 0 V”", "rs485"),
            ("Operator obserwuje DUT", "czy ładowarka wyłącza, zgłasza błąd, przechodzi na 1 fazę, wznawia po powrocie", "moc"),
            ("STOP lub timer / auto-off 60 s", "RPi (lub Shelly samo) otwiera O1 → cewka -K3 bez napięcia → styki NC wracają → L3 wraca", "radio"),
            ("Powrót do normy", "RPi czeka na -K13 (SW3 = OK) i PZEM (3 fazy) zanim pokaże „OK”; wpis do dziennika", "selv"),
        ]),
        ("C · TEST UPŁYWU F14 (RCD MA WYŁĄCZYĆ)", FILL["pom"], [
            ("Ekran / RPi", "operator wybiera F14 (upływ 34 mA L1′→PE′); RPi: tylko jedna usterka z grupy RCD", "selv"),
            ("RPi ⇢ -A15:O1 → -R4", "styk Shelly łączy -R4 6,8 kΩ między L1′ a PE′: płynie ~34 mA do PE", "lc"),
            ("-F1 RCD 30 mA", "prąd różnicowy > 30 mA → RCD wyłącza L1 L2 L3 N za sobą (cała sekcja usterek i gniazda)", "moc"),
            ("Sterowanie żyje dalej", "-G1, RPi, Shelly i -A20 są zasilane sprzed -F1 (przez RCBO -F6) – komputer nie restartuje", "l230"),
            ("-K13 → -A12:SW3 · PZEM milczą", "RPi widzi: brak napięcia na wyjściu, PZEM bez zasilania → „RCD wyłączył: test F14 zaliczony”", "fb"),
            ("RPi ⇢ -A15:O1 otwiera", "upływ zdjęty, zanim elektryk ręcznie załączy RCD (przycisk T sprawdza RCD osobno)", "radio"),
            ("Elektryk E/D załącza -F1", "napięcie wraca na sekcję usterek; -K1 pozostaje wyłączony do kolejnego START", "moc"),
            ("Wariant F13 „brak RCD”", "-A4:CH4 → -K12a/b: styki NO omijają RCD, NC otwierają tor przez RCD – wtedy F14 nic nie wyłączy", "lc"),
        ]),
        ("D · E-STOP / ZAWIESZENIE STEROWNIKA", FILL["ster"], [
            ("Operator naciska -S0", "styk NC przerywa Lc – sprzętowo, bez udziału RPi, Shelly ani oprogramowania", "lc"),
            ("Cewka -K1 bez napięcia", "stycznik główny opada: 4 styki NO otwierają L1 L2 L3 N do gniazd (styki Shelly są bistabilne, dlatego -K1)", "moc"),
            ("Wszystkie cewki usterek bez Lc", "-K3…-K12 wracają do położeń NC (instalacja „poprawna”), -R4/-R2 odłączone – energize-to-fault", "lc"),
            ("-A12:SW1 / SW2 → RPi", "Shelly melduje: Lc zniknęło, -S0 naciśnięty → ekran: „E-STOP”, dziennik", "fb"),
            ("-H2 gaśnie, -H1 (CH8) świeci", "RPi potwierdza stan bezpieczny, gdy -K13 nie widzi napięcia na wyjściu", "selv"),
            ("Zawieszenie RPi (bez E-STOP)", "watchdog restartuje RPi → GPIO = wejścia → -A4 opada (-K4, -K6/-K7, -K12, -K2 bez cewki)", "selv"),
            ("Shelly bez komend", "auto-off 60 s zdejmuje każdą usterkę Shelly; -A11:O1 też → -K1 opada po 60 s bez nadzoru", "radio"),
            ("Zanik zasilania sieci", "Lc = 0 → -K1 opada; po powrocie napięcia nic nie włącza się samo (START tylko z ekranu)", "moc"),
        ]),
    ]
    x0, cw, ytop = 6.0, 68.0, 20.0
    for ci, (title, fill, steps) in enumerate(cols):
        x = x0 + ci * (cw + 5.0)
        rect(x, ytop, cw, 183.0, fill="#fbfbfb", lw=0.3, rx=1.5)
        text(x + 2.0, ytop + 4.2, title, 1.7, bold=True)
        yy = ytop + 7.5
        sh = (183.0 - 9.0) / len(steps)
        for si, (who, what, kind) in enumerate(steps):
            col = C.get(kind, "#111")
            bh = sh - 2.6
            rect(x + 2.0, yy, cw - 4.0, bh, fill=fill, lw=0.3, rx=1.0)
            line(x + 2.0, yy, x + 2.0, yy + bh, col, 1.2)
            text(x + 4.0, yy + 2.6, f"{si + 1}. {who}", 1.45, bold=True)
            # zawijanie opisu
            words = what.split(" "); lines = []; cur = ""
            for w_ in words:
                if len(cur) + len(w_) + 1 > 60: lines.append(cur); cur = w_
                else: cur = (cur + " " + w_).strip()
            if cur: lines.append(cur)
            for li, ln in enumerate(lines[:3]):
                text(x + 4.0, yy + 4.6 + li * 1.75, ln, 1.2)
            if si < len(steps) - 1:
                line(x + cw / 2, yy + bh, x + cw / 2, yy + sh - 0.2, "#111", 0.4, arrow=True)
            yy += sh
    text(5.0, H - 4.2, "Strona 2/2 · kolor paska przy kroku = medium (patrz legenda str. 1): czarny tor mocy · czerwony 230 V sterowania/Lc · niebieski SELV · fioletowy radio · zielony RS485 · pomarańczowy sygnał zwrotny do Shelly", 1.15, italic=True, col="#444")

def render(fn_svg, pagefn):
    global out
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">']
    pagefn(); emit("</svg>")
    svg = "\n".join(out)
    open(fn_svg, "w", encoding="utf-8").write(svg)
    return svg

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    import cairosvg
    from pypdf import PdfReader, PdfWriter
    s1 = render(os.path.join(here, "schemat_blokowy.svg"), page1)
    s2 = render(os.path.join(here, "schemat_blokowy_2.svg"), page2)
    p1 = os.path.join(here, "_blok1.pdf"); p2 = os.path.join(here, "_blok2.pdf")
    cairosvg.svg2pdf(bytestring=s1.encode(), write_to=p1)
    cairosvg.svg2pdf(bytestring=s2.encode(), write_to=p2)
    cairosvg.svg2png(bytestring=s1.encode(), write_to=os.path.join(here, "schemat_blokowy.png"), dpi=200)
    w = PdfWriter()
    for f in (p1, p2):
        for pg in PdfReader(f).pages: w.add_page(pg)
    w.add_metadata({"/Title": "Ampere Point – rozdzielnica testowa: schemat blokowy (poglądowy)", "/Author": "Claude / D. Cękała"})
    outp = os.path.join(here, "schemat_blokowy.pdf"); w.write(outp)
    os.remove(p1); os.remove(p2)
    print("OK", outp)

if __name__ == "__main__":
    main()
