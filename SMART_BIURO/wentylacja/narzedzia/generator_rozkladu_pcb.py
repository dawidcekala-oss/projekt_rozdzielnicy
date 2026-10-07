# -*- coding: utf-8 -*-
# Rozklad plytki glownej modulu v2 - siatka A-X / 01-18 (plytka 5x7 cm).
# Zalozenie: plytka pusta. ESP32 obrocony o 90 st. - obie listwy pionowo
# (kolumna A i kolumna K), dzieki czemu wszystkie uzywane piny leza w kolumnie K,
# a caly obszar L-X zostaje wolny i zaden przewod nie musi przechodzic przez
# rzad zlutowanych pinow.
# Tor podczerwieni siedzi na osobnej plytce 4x6 cm - tutaj wychodzi 5 przewodami.

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

KAT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\SMART_BIURO\wentylacja\modul_v2"
OUT_PNG = KAT + r"\rozklad_pcb.png"
OUT_MD = KAT + r"\rozklad_polaczenia.md"

KOL = "ABCDEFGHIJKLMNOPQRSTUVWX"
C_OTWOR = "#CAD1DA"
C_ESP = "#2E6FB7"
C_RS = "#1F8A4C"
C_MP = "#C2410C"
C_5V = "#E8811A"
C_33 = "#7B3FBF"
C_GND = "#111111"
C_SIG = "#1F77B4"
C_BUS = "#2CA02C"
C_12V = "#D62728"
C_MUT = "#78828F"
NL = chr(10)

W, H = 19.4, 11.4
fig, ax = plt.subplots(figsize=(W, H), dpi=170)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor("white")

X0, Y0, K = 1.30, 1.20, 0.452


def xy(o):
    return X0 + KOL.index(o[0].upper()) * K, Y0 + (18 - int(o[1:])) * K


def most(a, b, kolor):
    x1, y1 = xy(a)
    x2, y2 = xy(b)
    ax.plot([x1, x2], [y1, y2], color=kolor, lw=6.8, solid_capstyle="round",
            zorder=4, alpha=.92)


def lancuch(lista, kolor):
    for a, b in zip(lista, lista[1:]):
        most(a, b, kolor)


def drut(punkty, kolor, lw=2.1):
    pts = [xy(p) for p in punkty]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=kolor, lw=lw,
            solid_capstyle="round", solid_joinstyle="round", zorder=6)


def oczko(o, kolor, r=0.125):
    x, y = xy(o)
    ax.add_patch(Circle((x, y), r, fc=kolor, ec="white", lw=1.1, zorder=9))


def opis(o, tekst, dx=0.0, dy=0.20, fs=6.5, kolor="#1A1A1A", ha="center",
         va="bottom"):
    x, y = xy(o)
    ax.text(x + dx, y + dy, tekst, ha=ha, va=va, fontsize=fs, color=kolor,
            zorder=11, fontweight="bold")


# --- siatka ----------------------------------------------------------------
for r in range(1, 19):
    for k in KOL:
        x, y = xy(k + "%02d" % r)
        ax.add_patch(Circle((x, y), 0.070, fc=C_OTWOR, ec="none", zorder=2))
for i, k in enumerate(KOL):
    ax.text(X0 + i * K, Y0 + 17 * K + 0.34, k, ha="center", va="bottom",
            fontsize=8.2, color=C_MUT, fontweight="bold")
for r in range(1, 19):
    ax.text(X0 - 0.44, Y0 + (18 - r) * K, "%02d" % r, ha="right", va="center",
            fontsize=7.8, color=C_MUT, fontweight="bold")
ax.add_patch(Rectangle((X0 - 0.30, Y0 - 0.30), 23 * K + 0.60, 17 * K + 0.60,
                       fc="none", ec="#B4BDC8", lw=1.5, zorder=1))

ax.text(0.45, H - 0.38, "MODUŁ v2 — płytka główna 5×7 cm", fontsize=18.5,
        fontweight="bold", color="#1A1A1A", va="center")
ax.text(0.45, H - 0.76,
        "ESP32 obrócony o 90° — wszystkie używane piny w kolumnie K, cała prawa strona wolna",
        fontsize=9.4, color="#555", va="center")

# --- ESP32 ------------------------------------------------------------------
ex1, ey1 = xy("A01")
ex2, ey2 = xy("K18")
ax.add_patch(FancyBboxPatch((ex1 - 0.24, ey2 - 0.24), (ex2 - ex1) + 0.48,
                            (ey1 - ey2) + 0.48,
                            boxstyle="round,pad=0.02,rounding_size=0.10",
                            fc="#E9F0F8", ec=C_ESP, lw=1.8, zorder=3, alpha=.65))
cx, cy = (ex1 + ex2) / 2, (ey1 + ey2) / 2
cx = cx - 0.9
ax.text(cx, cy + 0.30, "ESP32 DevKit", ha="center", va="center", fontsize=13,
        fontweight="bold", color=C_ESP, zorder=5)
ax.text(cx, cy - 0.12, "listwy pionowo, rzędy 02–16",
        ha="center", va="center", fontsize=8.4, color=C_ESP, zorder=5)
ax.text(cx, cy - 0.50, "USB wystaje poza krawędź płytki",
        ha="center", va="center", fontsize=7.6, color=C_MUT, zorder=5)

LEWA = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32",
        "D35", "D34", "VN", "VP", "EN"]
PRAWA = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19",
         "D21", "RX0", "TXO", "D22", "D23"]
UZ_P = {"3V3", "GND", "D4", "RX2", "TX2", "D23"}
for i, nz in enumerate(LEWA):
    o = "A%02d" % (i + 2)
    u = (nz == "VIN")
    oczko(o, C_ESP if u else "#A9BBD0", 0.125 if u else 0.082)
    opis(o, nz, 0.19, 0, 6.2, C_ESP if u else C_MUT, "left", "center")
for i, nz in enumerate(PRAWA):
    o = "K%02d" % (i + 2)
    u = nz in UZ_P
    oczko(o, C_ESP if u else "#A9BBD0", 0.125 if u else 0.082)
    opis(o, nz, -0.19, 0, 6.2, C_ESP if u else C_MUT, "right", "center")

# --- modul RS485 ------------------------------------------------------------
for r, nz in zip(range(5, 10), ["EN", "VCC", "RXD", "TXD", "GND"]):
    o = "M%02d" % r
    oczko(o, C_RS)
    opis(o, nz, 0.19, 0, 6.4, C_RS, "left", "center")
r1x, r1y = xy("M05")
r2x, r2y = xy("S09")
ax.add_patch(Rectangle((r1x - 0.22, r2y - 0.22), (r2x - r1x) + 0.44,
                       (r1y - r2y) + 0.44, fc="#EAF7EF", ec=C_RS, lw=1.5,
                       ls="--", hatch="///", alpha=.4, zorder=3))
ax.text((r1x + r2x) / 2 + 0.35, r1y + 0.02, "RS485 V2.05", ha="center",
        va="center", fontsize=9.2, fontweight="bold", color=C_RS, zorder=5)
ax.text((r1x + r2x) / 2 + 0.35, r1y - 0.40,
        "obrys szacunkowy" + NL + "listwa A/B tam, gdzie sięgnie",
        ha="center", va="center", fontsize=6.8, color=C_RS, zorder=5)
for o, nz in [("S06", "GND"), ("S07", "A"), ("S08", "B")]:
    oczko(o, C_BUS)
    opis(o, nz, 0.19, 0, 6.4, C_BUS, "left", "center")

# --- przetwornica -----------------------------------------------------------
for o, nz in [("N12", "OUT+"), ("V12", "IN+")]:
    oczko(o, C_MP)
    opis(o, nz, 0, -0.20, 6.5, C_MP, "center", "top")
for o, nz in [("N17", "OUT−"), ("V17", "IN−")]:
    oczko(o, C_MP)
    opis(o, nz, 0, 0.20, 6.5, C_MP, "center", "bottom")
p1x, p1y = xy("N12")
p2x, p2y = xy("V17")
ax.add_patch(Rectangle((p1x - 0.22, p2y - 0.22), (p2x - p1x) + 0.44,
                       (p1y - p2y) + 0.44, fc="#FDF1E8", ec=C_MP, lw=1.5,
                       ls="--", hatch="\\\\\\", alpha=.35, zorder=3))
ax.text((p1x + p2x) / 2, (p1y + p2y) / 2 + 0.12, "MP1584  ·  5,36 V",
        ha="center", va="center", fontsize=9.2, fontweight="bold",
        color=C_MP, zorder=5)
ax.text((p1x + p2x) / 2, (p1y + p2y) / 2 - 0.30, "obrys szacunkowy",
        ha="center", va="center", fontsize=6.8, color=C_MP, zorder=5)

# --- szyny ------------------------------------------------------------------
SZ_5V = ["%s01" % k for k in "LMNOPQRSTUV"]
SZ_GND = ["X%02d" % r for r in range(2, 19)]
SZ_DOL = ["%s18" % k for k in "LMNOPQRSTUVWX"]
SZ_G04 = ["%s04" % k for k in "LMNOPQRSTUVWX"]
for lst, kol in [(SZ_5V, C_5V), (SZ_GND, C_GND), (SZ_DOL, C_GND),
                 (SZ_G04, C_GND)]:
    lancuch(lst, kol)
    for o in lst:
        oczko(o, kol, 0.092)
opis("L01", "szyna +5 V — rząd 01", -0.30, 0, 7.6, C_5V, "right", "center")
opis("X09", "szyna GND" + NL + "kolumna X", 0.26, 0, 7.8, C_GND, "left", "center")
opis("Q18", "odnoga masy — rząd 18", 0, -0.24, 7.8, C_GND, "center", "top")
opis("L04", "odnoga masy — rząd 04", -0.30, 0, 7.6, C_GND, "right", "center")

# --- wtyk, elementy przewlekane, pola IR ------------------------------------
for o, nz, kol in [("U02", "B", C_BUS), ("V02", "A", C_BUS),
                   ("W02", "+12V", C_12V), ("X02", "GND", C_GND)]:
    oczko(o, kol)
    opis(o, nz, 0, 0.20, 6.4, kol)
ax.text(xy("V02")[0], Y0 + 17 * K + 0.72, "wtyk JST-XH z gniazda COM-MANUAL",
        ha="center", va="bottom", fontsize=7.8, color="#666", fontweight="bold")


oczko("V01", C_5V)
oczko("X01", C_GND)
drut(["V01", "X01"], "#7C8794", lw=4.5)
opis("X01", "C1  470 µF", 0.26, 0, 7.2, "#555", "left", "center")

# --- wezly 3,3 V i masy tuz przy procesorze ---------------------------------
oczko("L02", C_33)
oczko("L03", C_GND)

# --- tor nadawczy IR na plytce glownej --------------------------------------
oczko("Q01", C_5V)
oczko("Q02", C_5V)
drut(["Q01", "Q02"], "#7C8794", lw=4.5)
ax.text(xy("Q01")[0] + 0.24, (xy("Q01")[1] + xy("Q02")[1]) / 2,
        "R1  33 Ω", ha="left", va="center", fontsize=7.2, color=C_5V,
        fontweight="bold", zorder=11)

oczko("P02", C_SIG)
oczko("P03", C_SIG)
drut(["P02", "P03"], "#7C8794", lw=4.5)
ax.text(xy("P02")[0] - 0.24, (xy("P02")[1] + xy("P03")[1]) / 2,
        "R2  470 Ω", ha="right", va="center", fontsize=7.2, color=C_SIG,
        fontweight="bold", zorder=11)

tx1, ty = xy("O03")
tx2, _ = xy("Q03")
ax.add_patch(FancyBboxPatch((tx1 - 0.22, ty - 0.24), (tx2 - tx1) + 0.44, 0.48,
                            boxstyle="round,pad=0.02,rounding_size=0.22",
                            fc="#F2F4F7", ec="#444", lw=1.5, zorder=3))
for o, nz in [("O03", "E"), ("P03", "B"), ("Q03", "C")]:
    oczko(o, "#333")
    opis(o, nz, 0, -0.22, 6.4, "#333", "center", "top")
opis("O03", "T1", -0.26, 0, 7.4, "#333", "right", "center")

oczko("Q02", C_5V)
oczko("Q03", "#333")
ax.add_patch(Rectangle((xy("Q02")[0] - 0.22, xy("Q03")[1] - 0.22), 0.44, 0.88,
                       fc="none", ec=C_12V, lw=1.3, ls=":", zorder=3))
ax.text(xy("Q02")[0] + 0.26, (xy("Q02")[1] + xy("Q03")[1]) / 2,
        "D1 → TSAL6100", ha="left", va="center", fontsize=7.2, color=C_12V,
        fontweight="bold", zorder=11)

# ===========================================================================
MOSTKI = [
    (["K07", "L07", "M07"], C_SIG, "pole RXD modułu (wejście nadajnika, nieużywane) → RX2"),
    (["K08", "L08", "M08"], C_SIG, "pole TXD modułu = WYJŚCIE odbiornika → TX2 (firmware czyta GPIO17)"),
    (["K02", "L02"], C_33, "3V3 procesora → węzeł +3,3 V"),
    (["K03", "L03"], C_GND, "GND procesora → węzeł masy"),
    (["K16", "L16"], C_SIG, "D23 → tor nadawczy"),
    (["L03", "L04"], C_GND, "masa procesora → odnoga masy w rzędzie 04"),
    (["O03", "O04"], C_GND, "emiter tranzystora → odnoga masy"),
    (["A01", "A02"], C_5V, "szyna +5 V → VIN procesora"),
    (["X01", "X02"], C_GND, "minus C1 → szyna GND"),
    (["N17", "N18"], C_GND, "OUT− przetwornicy → odnoga masy"),
    (["V17", "V18"], C_GND, "IN− przetwornicy → odnoga masy"),
]
for pkt, kol, _ in MOSTKI:
    lancuch(pkt, kol)

DRUTY = [
    (["M01", "A01"], C_5V, "szyna +5 V → VIN (przewód pod modułem)"),
    (["L16", "L10", "N10", "N02", "P02"], C_SIG, "D23 → R2 → baza tranzystora"),
    (["M09", "M18"], C_GND, "GND modułu RS485 → odnoga masy"),
    (["M05", "L05", "L06", "K06"], C_SIG, "EN modułu RS485 → D4"),
    (["M06", "M02", "L02"], C_33, "VCC modułu RS485 → 3V3"),
    (["S06", "X06"], C_GND, "masa magistrali → szyna GND (odniesienie dla A/B)"),
    (["V02", "V07", "T07", "S07"], C_BUS, "A z wtyku → pin A modułu"),
    (["U02", "U08", "T08", "S08"], C_BUS, "B z wtyku → pin B modułu"),
    (["W02", "W12", "V12"], C_12V, "+12 V z wtyku → IN+ przetwornicy"),
    (["N12", "N11", "T11", "T01"], C_5V, "OUT+ przetwornicy → szyna +5 V"),
]
for pkt, kol, _ in DRUTY:
    drut(pkt, kol)

# --- panel boczny -----------------------------------------------------------
PX = 12.9
ax.text(PX, 9.90, "Jak czytać", fontsize=10.5, fontweight="bold", color="#1A1A1A")
for i, t in enumerate([
        "gruba kreska  =  mostek z cyny w rzędzie lub kolumnie",
        "cienka kreska  =  przewód w izolacji, od spodu płytki",
        "Przewód w izolacji może przechodzić nad zlutowanym",
        "pinem i nad mostkiem — to normalna praktyka na płytce",
        "uniwersalnej. Zwarcie robi tylko goła cyna.",
]):
    ax.text(PX, 9.58 - i * 0.27, t, fontsize=8.1, color="#444", va="top")

ax.text(PX, 7.85, "Zanim polutujesz", fontsize=10.5, fontweight="bold",
        color="#B00020")
for i, t in enumerate([
        "Zmierz oba moduły — obrysy kreskowane są szacunkowe.",
        "Listwa A/B modułu RS485 może wypaść w innej kolumnie",
        "niż S; przewody A i B dociągnij do rzeczywistych pinów.",
        "Ustaw MP1584 na 5,00 V zanim osadzisz ESP32 (pin VIN!).",
        "Na module RS485: drut od pola dalej od litery T do GND —",
        "bez tego odbiornik jest fabrycznie wyłączony (MODUL_v2 3.3a).",
]):
    ax.text(PX, 7.53 - i * 0.27, t, fontsize=8.1, color="#B00020", va="top")

ax.text(PX, 6.15, "Kolejność montażu", fontsize=10.5, fontweight="bold",
        color="#1A1A1A")
for i, t in enumerate([
        "1.  szyny: rząd 01, kolumna X, rząd 18",
        "2.  pozostałe mostki (tabela 2)",
        "3.  przewody w izolacji (tabela 3)",
        "4.  R1, R2, C1 i tranzystor",
        "5.  podstawki pod moduły",
        "6.  wiązki: wtyk JST i dioda IR",
        "7.  pomiar: +5 V na A02, brak zwarcia do masy",
        "8.  dopiero teraz ESP32 i moduły",
]):
    ax.text(PX, 5.83 - i * 0.27, t, fontsize=8.1, color="#444", va="top")

ax.text(PX, 3.55, "Nadajnik podczerwieni", fontsize=10.5, fontweight="bold",
        color="#1A1A1A")
for i, t in enumerate([
        "R1  33 Ω          Q01 – Q02   (pionowo)",
        "R2  470 Ω        P02 – P03   (pionowo)",
        "T1  BC337-40   O03 = E · P03 = B · Q03 = C",
        "       płaska ścianka w stronę rzędu 18",
        "D1  TSAL6100  anoda Q02, katoda Q03 — 2 przewody",
        "Odbiornika IR nie ma. Rzeczywisty stan jednostki",
        "podaje magistrala co 800 ms — echo IR było zbędne.",
]):
    ax.text(PX, 3.23 - i * 0.27, t, fontsize=8.1, color="#444", va="top")

ax.text(W - 0.3, 0.28, "AmperePoint  ·  SMART_BIURO  ·  modul_v2", ha="right",
        fontsize=8.0, color="#9AA3AE")

fig.savefig(OUT_PNG, facecolor="white", bbox_inches="tight", pad_inches=0.20)
print("zapisano:", OUT_PNG)

# ===========================================================================
w = ["# Lista połączeń — płytka główna modułu v2", "",
     "Siatka **A–X / 01–18**, płytka uniwersalna 5×7 cm.",
     "ESP32 stoi **pionowo**: listwa `VIN…EN` w kolumnie **A**, listwa `3V3…D23`",
     "w kolumnie **K**, oba rzędy pinów 02–16. Gniazdo USB wystaje poza krawędź",
     "płytki od strony rzędu 18.", "",
     "Gruba linia na rysunku = **mostek z cyny**. Cienka = **przewód w izolacji**",
     "prowadzony od spodu; może przechodzić nad zlutowanym pinem i nad mostkiem.", "",
     "## 1. Szyny — ciągły mostek cyny", "",
     "| # | Przebieg | Rola |", "|---|---|---|",
     "| 1 | **L01 → V01** (rząd 01) | szyna +5 V |",
     "| 2 | **X02 → X18** (kolumna X) | szyna GND |",
     "| 3 | **L18 → X18** (rząd 18) | odnoga masy przy przetwornicy |", "",
     "## 2. Pozostałe mostki", "",
     "| # | Przebieg | Co łączy |", "|---|---|---|"]
n = 4
for pkt, _, o in MOSTKI:
    w.append("| %d | %s | %s |" % (n, " → ".join("**%s**" % p for p in pkt), o))
    n += 1
w += ["", "## 3. Przewody w izolacji, od spodu", "",
      "| # | Trasa | Co łączy |", "|---|---|---|"]
for pkt, _, o in DRUTY:
    w.append("| %d | %s | %s |" % (n, " → ".join("**%s**" % p for p in pkt), o))
    n += 1
w += ["", "## 4. Elementy przewlekane", "",
      "| Element | Otwory | Uwaga |", "|---|---|---|",
      "| R1 33 Ω | **Q01 → Q02** | pionowo, jedna nóżka zagięta; Q01 leży na szynie +5 V |",
      "| R2 470 Ω | **P02 → P03** | pionowo; P03 to baza tranzystora |",
      "| T1 BC337-40 | **O03** = E, **P03** = B, **Q03** = C | baza to środkowa nóżka; BC337 ma płaską ścianką do siebie kolejność **E-B-C** (odwrotnie niż BC547). Na płytce: **płaska ścianka zwrócona w stronę rzędu 18**, grzbiet do rzędu 01 |",
      "| C1 470 µF | **+ w V01**, **− w X01** | rozstaw 2 otwory = 5,08 mm; W01 zostaje pusty |", "",
      "## 5. Wtyk JST-XH z gniazda COM-MANUAL", "",
      "| Żyła | Otwór |", "|---|---|",
      "| B | **U02** |", "| A | **V02** |", "| +12 V | **W02** |", "| GND | **X02** |", "",
      "## 6. Dioda TSAL6100 — dwa przewody", "",
      "Dioda musi być przyklejona naprzeciw okienka odbiornika jednostki, więc",
      "zostaje na przewodach; cała elektronika sterująca jest na płytce.", "",
      "| Żyła | Otwór |", "|---|---|",
      "| anoda | **Q02** — za rezystorem R1 |",
      "| katoda | **Q03** — kolektor tranzystora |", "",
      "**Odbiornika podczerwieni nie ma.** Rzeczywisty stan jednostki podaje",
      "magistrala co 800 ms i to ona potwierdza wykonanie komendy, więc echo IR",
      "niczego nie wnosiło. **D19 zostaje wolny** — gdyby kiedyś miał wrócić,",
      "wystarczy mostek `K11 → L11` i trzy przewody z VS1838B.", "",
      "## 6a. Na samym module RS485 V2.05 — obowiązkowe", "",
      "Odbiornik tego modułu jest fabrycznie wyłączony: noga `RE` układu MAX3485 jest",
      "podciągnięta do plusa przez rezystor `103` i nie wychodzi na listwę (`EN` steruje",
      "tylko nadajnikiem). **Drut od pola dalej od litery `T` do pola `GND` listwy** — na",
      "module, przed osadzeniem w podstawce. Pole bliżej `T` to `VCC`, nie zwierać do masy.", "",
      "Pole `TXD` modułu jest wyjściem odbiornika (opisy z perspektywy modułu); płytka",
      "zostaje zlutowana jak na rysunku, firmware czyta GPIO17. Szczegóły: MODUL_v2 3.3a.", "",
      "## 7. Czego jeszcze nie zmierzyłem", "",
      "| Element | Co sprawdzić | Co zrobić, jeśli wyjdzie inaczej |", "|---|---|---|",
      "| RS485 V2.05 | odstęp listwy `EN…GND` od listwy `GND/A/B` | przesunąć obrys; przewody A i B dociągnąć do rzeczywistych pinów |",
      "| MP1584 | rozstaw IN↔OUT i rozstaw pinów w parze | przesunąć obrys w wolnym polu N–V, rzędy 11–17 |",
      "| C1 470 µF | rzeczywisty rozstaw nóżek | jeśli 3,5 mm — wstawić w **V01/W01**, mostek **W01→X01** |", ""]
io.open(OUT_MD, "w", encoding="utf-8", newline=NL).write(NL.join(w))
print("zapisano:", OUT_MD)
