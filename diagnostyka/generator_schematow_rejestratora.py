# -*- coding: utf-8 -*-
"""Trzy arkusze schematow rejestratora zlacza Q11 (wg sniffer_projekt.md v2)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\diagnostyka"

C_SIG="#B45309"; C_GND="#111111"; C_5V="#B00020"; C_BOX="#F4F4F2"; C_EDGE="#333333"
C_OK="#15803D"; C_INFO="#0369A1"; C_MUT="#888888"; C_WARN="#B00020"


def nowy(w=17.5, h=11.0):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax


def box(ax,x0,y0,x1,y1,title,sub=None,fc=C_BOX):
    ax.add_patch(FancyBboxPatch((x0,y0),x1-x0,y1-y0,boxstyle="round,pad=0.04,rounding_size=0.12",fc=fc,ec=C_EDGE,lw=1.5))
    ax.text((x0+x1)/2,y1-0.3,title,ha="center",va="center",fontsize=11.5,fontweight="bold",color="#222")
    if sub: ax.text((x0+x1)/2,y1-0.62,sub,ha="center",va="center",fontsize=8.2,color="#555")


def pin(ax,x,y,label,side="right",color="#222",fs=9):
    ax.add_patch(Circle((x,y),0.065,fc="white",ec=color,lw=1.5,zorder=5))
    dx=0.15 if side=="right" else -0.15; ha="left" if side=="right" else "right"
    ax.text(x+dx,y,label,ha=ha,va="center",fontsize=fs,fontweight="bold",color=color,zorder=6,bbox=dict(fc="white",ec="none",pad=0.4))


def wire(ax,pts,color=C_SIG,lw=2.2):
    ax.plot([p[0] for p in pts],[p[1] for p in pts],color=color,lw=lw,solid_capstyle="round",zorder=3)


def dot(ax,x,y,color=C_SIG):
    ax.add_patch(Circle((x,y),0.08,fc=color,ec=color,zorder=6))


def res_h(ax,xc,yc,label,fs=8.6):
    ax.add_patch(Rectangle((xc-0.42,yc-0.14),0.84,0.28,fc="white",ec="#222",lw=1.6,zorder=5))
    ax.text(xc,yc+0.3,label,ha="center",fontsize=fs,color="#222",fontweight="bold",zorder=6)


def res_v(ax,xc,yc,label,fs=8.6,side="right"):
    ax.add_patch(Rectangle((xc-0.14,yc-0.4),0.28,0.8,fc="white",ec="#222",lw=1.6,zorder=5))
    dx = 0.24 if side=="right" else -0.24
    ha = "left" if side=="right" else "right"
    ax.text(xc+dx,yc,label,ha=ha,va="center",fontsize=fs,color="#222",fontweight="bold",zorder=6)


def cap_v(ax,xc,yc,label,fs=8.6):
    ax.plot([xc-0.18,xc+0.18],[yc+0.07,yc+0.07],color="#222",lw=2.6,zorder=5)
    ax.plot([xc-0.18,xc+0.18],[yc-0.07,yc-0.07],color="#222",lw=2.6,zorder=5)
    ax.text(xc+0.26,yc,label,ha="left",va="center",fontsize=fs,color="#222",fontweight="bold",zorder=6)


def dioda_v(ax,xc,yc,label="",kierunek="dol",fs=8.2):
    # trojkat + kreska; kierunek przewodzenia
    if kierunek=="dol":
        ax.add_patch(Polygon([(xc-0.14,yc+0.12),(xc+0.14,yc+0.12),(xc,yc-0.1)],fc="white",ec="#222",lw=1.4,zorder=5))
        ax.plot([xc-0.14,xc+0.14],[yc-0.12,yc-0.12],color="#222",lw=2,zorder=5)
    else:
        ax.add_patch(Polygon([(xc-0.14,yc-0.12),(xc+0.14,yc-0.12),(xc,yc+0.1)],fc="white",ec="#222",lw=1.4,zorder=5))
        ax.plot([xc-0.14,xc+0.14],[yc+0.12,yc+0.12],color="#222",lw=2,zorder=5)
    if label: ax.text(xc+0.24,yc,label,ha="left",va="center",fontsize=fs,color="#222",zorder=6)


def dioda_h(ax,xc,yc,label="",fs=8.2):
    ax.add_patch(Polygon([(xc-0.12,yc-0.14),(xc-0.12,yc+0.14),(xc+0.1,yc)],fc="white",ec="#222",lw=1.4,zorder=5))
    ax.plot([xc+0.12,xc+0.12],[yc-0.14,yc+0.14],color="#222",lw=2,zorder=5)
    if label: ax.text(xc,yc+0.28,label,ha="center",fontsize=fs,color="#222",fontweight="bold",zorder=6)


def gnd(ax,x,y):
    ax.plot([x,x],[y,y-0.12],color=C_GND,lw=2,zorder=4)
    for i,w in enumerate([0.16,0.11,0.06]):
        ax.plot([x-w,x+w],[y-0.14-i*0.06,y-0.14-i*0.06],color=C_GND,lw=2,zorder=4)


def klamra(ax,x,y,fs=7.8):
    """Klamra 2x1N4148: do +5V i do GND, rysowana kompaktowo obok wezla."""
    wire(ax,[(x,y),(x,y+0.35)],C_5V,1.6)
    dioda_v(ax,x,y+0.55,kierunek="gora")
    wire(ax,[(x,y+0.75),(x,y+0.95)],C_5V,1.6)
    ax.text(x,y+1.08,"+5 V",ha="center",fontsize=fs,color=C_5V,fontweight="bold")
    wire(ax,[(x,y),(x,y-0.35)],C_GND,1.6)
    dioda_v(ax,x,y-0.55,kierunek="gora")
    wire(ax,[(x,y-0.75),(x,y-0.9)],C_GND,1.6)
    gnd(ax,x,y-0.9)
    ax.text(x+0.2,y+0.55,"1N4148",ha="left",fontsize=7.4,color="#555")
    ax.text(x+0.2,y-0.55,"1N4148",ha="left",fontsize=7.4,color="#555")


# ═══════════════ ARKUSZ B: TOR CT + DETEKTOR + 1.65 ═══════════════
fig, ax = nowy()
ax.text(8.75,10.6,"Arkusz B — tory szybkie: CT (główny podejrzany), detektor szczytu, pin 1.65",
        ha="center",fontsize=14,fontweight="bold")
ax.text(8.75,10.2,"próbkowanie: CT i 1.65 na przemian po 2 kHz (A0/A4) • detektor szczytu czytany kanałem 7 multipleksera 1",
        ha="center",fontsize=9.5,color="#444")

# --- TOR CT (gorny pas, y=8.6) ---
ax.text(0.5,9.4,"TOR CT → A0  (filtr antyaliasingowy 2. rzędu, pasmo wiarygodne 0–0,8 kHz)",fontsize=10,fontweight="bold",color=C_INFO)
y=8.6
pin(ax,0.7,y,"pin CT","right",C_SIG)
wire(ax,[(0.7,y),(1.7,y)])
res_h(ax,2.12,y,"100 kΩ"); wire(ax,[(2.54,y),(2.9,y)])
res_h(ax,3.32,y,"100 kΩ"); wire(ax,[(3.74,y),(5.0,y)])
dot(ax,5.0,y); ax.text(5.0,y+0.35,"węzeł 1",ha="center",fontsize=8.2,color=C_SIG)
klamra(ax,5.85,y)
wire(ax,[(5.0,y),(5.85,y)])
wire(ax,[(5.0,y),(5.0,y-0.5)],C_GND,1.6)
cap_v(ax,5.0,y-0.72,"1 nF")
wire(ax,[(5.0,y-0.94),(5.0,y-1.15)],C_GND,1.6); gnd(ax,5.0,y-1.15)
wire(ax,[(5.85,y),(7.3,y)])
res_h(ax,7.72,y,"100 kΩ"); wire(ax,[(8.14,y),(9.3,y)])
dot(ax,9.3,y); ax.text(9.3,y+0.35,"węzeł 2",ha="center",fontsize=8.2,color=C_SIG)
wire(ax,[(9.3,y),(9.3,y-0.5)],C_GND,1.6)
cap_v(ax,9.3,y-0.72,"470 pF")
wire(ax,[(9.3,y-0.94),(9.3,y-1.15)],C_GND,1.6); gnd(ax,9.3,y-1.15)
wire(ax,[(9.3,y),(10.6,y)])
pin(ax,10.6,y,"A0 (UNO)","right",C_OK,10)
ax.text(12.9,y+0.05,"f₁ ≈ 0,8 kHz (200 kΩ×1 nF)\nf₂ ≈ 3,4 kHz (100 kΩ×470 pF)\ntłumienie: −16 dB @4 kHz, −36 dB @20 kHz",
        fontsize=8.4,color="#333",ha="left",va="center")

# --- DETEKTOR SZCZYTU (srodkowy pas, y=5.6) ---
ax.text(0.5,6.95,"DETEKTOR SZCZYTU CT → MUX1 kanał 7  (łapie szpilki szybsze niż próbkowanie; osobna gałąź od pinu CT)",
        fontsize=10,fontweight="bold",color=C_INFO)
y=5.6
pin(ax,0.7,y,"pin CT","right",C_SIG)
wire(ax,[(0.7,y),(1.7,y)])
res_h(ax,2.12,y,"100 kΩ"); wire(ax,[(2.54,y),(2.9,y)])
res_h(ax,3.32,y,"100 kΩ"); wire(ax,[(3.74,y),(5.0,y)])
dot(ax,5.0,y); ax.text(5.0,y+0.35,"węzeł P (bez kondensatora!)",ha="center",fontsize=8.2,color=C_SIG)
klamra(ax,5.85,y)
wire(ax,[(5.0,y),(5.85,y)])
wire(ax,[(5.85,y),(6.9,y)])
dioda_h(ax,7.2,y,"1N4148")
wire(ax,[(7.32,y),(8.6,y)])
dot(ax,8.6,y); ax.text(8.6,y+0.35,"węzeł D „pamięć szczytu”",ha="center",fontsize=8.2,color=C_SIG)
wire(ax,[(8.6,y),(8.6,y-0.5)],C_GND,1.6)
cap_v(ax,8.6,y-0.72,"47 nF")
wire(ax,[(8.6,y-0.94),(8.6,y-1.15)],C_GND,1.6); gnd(ax,8.6,y-1.15)
wire(ax,[(8.6,y),(9.6,y)])
dot(ax,9.6,y)
wire(ax,[(9.6,y),(9.6,y-0.45)],C_GND,1.6)
res_v(ax,9.6,y-0.85,"1 MΩ")
wire(ax,[(9.6,y-1.25),(9.6,y-1.45)],C_GND,1.6); gnd(ax,9.6,y-1.45)
wire(ax,[(9.6,y),(10.4,y)])
res_h(ax,10.82,y,"10 kΩ"); wire(ax,[(11.24,y),(12.2,y)])
pin(ax,12.2,y,"MUX1 kan. 7","right",C_OK,9.6)
ax.text(13.9,y+0.02,"ładowanie τ≈9,4 ms, upust τ≈47 ms\nszpilka 100 µs / 2 V → +20 mV (≈4 kroki ADC)\nbursty pompują kumulacyjnie",
        fontsize=8.2,color="#333",ha="left",va="center")

# --- TOR 1.65 (dolny pas, y=2.6) ---
ax.text(0.5,3.95,"TOR 1.65 → A4  (hipoteza konkurencyjna: pływające odniesienie toru pomiarowego)",
        fontsize=10,fontweight="bold",color=C_INFO)
y=2.6
pin(ax,0.7,y,"pin 1.65","right",C_SIG)
wire(ax,[(0.7,y),(1.7,y)])
res_h(ax,2.12,y,"100 kΩ"); wire(ax,[(2.54,y),(2.9,y)])
res_h(ax,3.32,y,"100 kΩ"); wire(ax,[(3.74,y),(5.0,y)])
dot(ax,5.0,y)
klamra(ax,5.85,y)
wire(ax,[(5.0,y),(5.85,y)])
wire(ax,[(5.0,y),(5.0,y-0.5)],C_GND,1.6)
cap_v(ax,5.0,y-0.72,"1 nF")
wire(ax,[(5.0,y-0.94),(5.0,y-1.15)],C_GND,1.6); gnd(ax,5.0,y-1.15)
wire(ax,[(5.85,y),(7.2,y)])
pin(ax,7.2,y,"A4 (UNO)","right",C_OK,10)
ax.text(9.2,y+0.02,"pasmo ~0,8 kHz — identyczne jak stopień 1 toru CT (porównywalność) •\nzmierzono 4,31 V zamiast 1,65 V — sesja bazowa rozstrzygnie, czy to usterka",
        fontsize=8.4,color="#333",ha="left",va="center")

ax.add_patch(FancyBboxPatch((0.5,0.15),16.5,0.85,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#DCFCE7",ec=C_OK,lw=1.2))
ax.text(0.75,0.72,"Wspólne dla wszystkich odczepów: 2×100 kΩ szeregowo (500 V wytrzymałości, awaria 230 V → maks. 1,15 mA), klamra 2×1N4148 do +5 V i masy.",
        fontsize=8.6,color="#14532D",ha="left")
ax.text(0.75,0.38,"Pierwszy 100 kΩ wlutowany PRZY punkcie odczepu (koszulka termokurczliwa) — przetarty przewód odczepowy nigdy nie zwiera badanej linii wprost.",
        fontsize=8.6,color="#14532D",ha="left")
plt.tight_layout(pad=0.4)
plt.savefig(OUT + r"\AMPERE_POINT_rejestrator_Q11_schemat_B_tor_CT.png",dpi=200,bbox_inches="tight",facecolor="white")
plt.close(fig)

# ═══════════════ ARKUSZ C: TOR CP + KOMPARATOR ═══════════════
fig, ax = nowy()
ax.text(8.75,10.6,"Arkusz C — tor CP (Control Pilot ±12 V): poziomy na A1 + wypełnienie PWM przez komparator na D8",
        ha="center",fontsize=14,fontweight="bold")
ax.text(8.75,10.2,"U(A) = 1,82 V + 0,152 × U(CP) • odgałęzienie komparatora PRZED kondensatorem (błąd wypełnienia < 0,1%)",
        ha="center",fontsize=9.5,color="#444")

y=8.0
pin(ax,0.7,y,"pin CP","right",C_SIG)
wire(ax,[(0.7,y),(1.6,y)])
res_h(ax,2.02,y,"120 kΩ"); wire(ax,[(2.44,y),(2.8,y)])
res_h(ax,3.22,y,"120 kΩ"); wire(ax,[(3.64,y),(4.9,y)])
dot(ax,4.9,y); ax.text(4.9,y+0.33,"węzeł A",ha="center",fontsize=8.6,color=C_SIG,fontweight="bold")
# 100k do +5V
wire(ax,[(4.9,y),(4.9,y+0.5)],C_5V,1.6)
res_v(ax,4.9,y+0.9,"100 kΩ")
wire(ax,[(4.9,y+1.3),(4.9,y+1.55)],C_5V,1.6)
ax.text(4.9,y+1.7,"+5 V",ha="center",fontsize=8.4,color=C_5V,fontweight="bold")
# 120k do GND
wire(ax,[(4.9,y),(4.9,y-0.5)],C_GND,1.6)
res_v(ax,4.9,y-0.9,"120 kΩ",side="left")
wire(ax,[(4.9,y-1.3),(4.9,y-1.5)],C_GND,1.6); gnd(ax,4.9,y-1.5)
# klamra
klamra(ax,6.0,y)
wire(ax,[(4.9,y),(6.0,y)])
# galaz A' do A1
wire(ax,[(6.0,y),(7.1,y)])
res_h(ax,7.52,y,"10 kΩ"); wire(ax,[(7.94,y),(9.1,y)])
dot(ax,9.1,y); ax.text(9.1,y+0.33,"węzeł A′",ha="center",fontsize=8.4,color=C_SIG)
wire(ax,[(9.1,y),(9.1,y-0.5)],C_GND,1.6)
cap_v(ax,9.1,y-0.72,"470 pF")
wire(ax,[(9.1,y-0.94),(9.1,y-1.15)],C_GND,1.6); gnd(ax,9.1,y-1.15)
wire(ax,[(9.1,y),(10.3,y)])
pin(ax,10.3,y,"A1 (UNO) — poziomy","right",C_OK,9.6)
# galaz komparatora z wezla A
wire(ax,[(6.0,y),(6.0,6.3)],C_SIG,1.8)
res_v(ax,6.0,5.9,"100 kΩ")
wire(ax,[(6.0,5.5),(6.0,5.1)],C_SIG,1.8)
dot(ax,6.0,5.1); ax.text(6.35,5.15,"węzeł B (0–1,82 V)",fontsize=8.4,color=C_SIG,ha="left")
wire(ax,[(6.0,5.1),(6.0,4.7)],C_GND,1.6)
res_v(ax,6.0,4.3,"100 kΩ",side="left")
wire(ax,[(6.0,3.9),(6.0,3.7)],C_GND,1.6); gnd(ax,6.0,3.7)
# komparator LM393
box(ax,7.6,3.6,10.6,5.6,"LM393 (½)","komparator, zasilanie +5 V / masa")
wire(ax,[(6.0,5.1),(7.6,5.1)],C_SIG,1.8)
ax.text(7.75,5.1,"IN−",fontsize=8.6,color="#222",va="center")
# prog
wire(ax,[(7.0,4.1),(7.6,4.1)],C_INFO,1.8)
ax.text(7.75,4.1,"IN+",fontsize=8.6,color="#222",va="center")
ax.text(6.9,4.1,"próg 0,455 V",fontsize=8.2,color=C_INFO,ha="right",va="center")
ax.text(6.9,3.75,"(dzielnik 100 kΩ z +5 V / 10 kΩ do masy)\n≈ U(CP) = −6 V",fontsize=7.6,color=C_INFO,ha="right",va="top")
# wyjscie
wire(ax,[(10.6,4.6),(12.2,4.6)],C_OK,2.0)
dot(ax,11.4,4.6,C_OK)
wire(ax,[(11.4,4.6),(11.4,5.3)],C_5V,1.6)
res_v(ax,11.4,5.7,"10 kΩ")
wire(ax,[(11.4,6.1),(11.4,6.3)],C_5V,1.6)
ax.text(11.4,6.45,"+5 V (podciąganie)",ha="center",fontsize=8,color=C_5V)
pin(ax,12.2,4.6,"D8 (Timer1 — wypełnienie)","right",C_OK,9.4)
# histereza
wire(ax,[(11.4,4.6),(11.4,3.4),(8.6,3.4),(8.6,3.6)],C_MUT,1.4)
ax.text(10.0,3.15,"histereza: 470 kΩ z wyjścia do IN+ (≈ ±0,6 V w skali CP)",fontsize=8,color=C_MUT,ha="center")

# tabela poziomow
ax.add_patch(FancyBboxPatch((13.2,5.6),3.9,3.6,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#E8F4FD",ec=C_INFO,lw=1.2))
ax.text(13.45,8.85,"Poziomy (przeliczone):",fontsize=9,fontweight="bold",color=C_INFO)
for i,(cp,a1,b) in enumerate([("+12 V (stan A)","3,64 V","1,82 V"),("+9 V (stan B)","3,18 V","1,59 V"),
                               ("+6 V (stan C)","2,73 V","1,36 V"),("0 V","1,82 V","0,91 V"),("−12 V (dół PWM)","0,00 V","0,00 V")]):
    ax.text(13.45,8.45-i*0.5,f"CP {cp}",fontsize=8,color="#0C4A6E")
    ax.text(15.6,8.45-i*0.5,f"A′ {a1} · B {b}",fontsize=8,color="#0C4A6E")
ax.text(13.45,5.85,"obciążenie linii CP ≤ 50 µA →\nspadek ≤ 50 mV (pomijalny wg IEC 61851)",fontsize=7.8,color="#0C4A6E")

ax.add_patch(FancyBboxPatch((0.5,0.6),16.5,2.0,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#FEF3C7",ec="#D97706",lw=1.2))
ax.text(0.75,2.3,"Dlaczego taka topologia:",fontsize=9,fontweight="bold",color="#7A5800")
ax.text(0.75,1.95,"• zwykły dzielnik nie mieści ±12 V w 0–5 V — rezystor 100 kΩ do +5 V przesuwa zakres (−12 V→0,00 V; +12 V→3,64 V), klamra pilnuje reszty;",fontsize=8.4,color="#7A5800")
ax.text(0.75,1.6,"• komparator odgałęziony PRZED kondensatorem — widzi ostre zbocza (węzeł A: tylko pojemności pasożytnicze), więc błąd wypełnienia < 0,1% (~0,06 A w skali IEC);",fontsize=8.4,color="#7A5800")
ax.text(0.75,1.25,"• kondensator 470 pF przeniesiony za 10 kΩ (węzeł A′) — wygładza poziomy dla ADC, nie zniekształcając pomiaru wypełnienia;",fontsize=8.4,color="#7A5800")
ax.text(0.75,0.9,"• próbki A1 wyzwalane stanem komparatora: jedna w fazie górnej, jedna w dolnej, raz na ~10 ms — bez ślepego łapania minimów i maksimów.",fontsize=8.4,color="#7A5800")
plt.tight_layout(pad=0.4)
plt.savefig(OUT + r"\AMPERE_POINT_rejestrator_Q11_schemat_C_tor_CP.png",dpi=200,bbox_inches="tight",facecolor="white")
plt.close(fig)

# ═══════════════ ARKUSZ A: SYSTEM (zlacze, odczepy, MUXy, UNO) ═══════════════
fig, ax = nowy(17.5, 11.8)
ax.text(8.75,11.45,"Arkusz A — architektura rejestratora: złącze 2×10, odczepy, multipleksery, Arduino UNO",
        ha="center",fontsize=14,fontweight="bold")
ax.text(8.75,11.05,"wariant A (rekomendowany): odczepy lutowane do pól złącza od tyłu obudowy • wszystkie decyzje offline — UNO tylko streamuje",
        ha="center",fontsize=9.5,color="#444")

# zlacze 2x10
box(ax,0.4,4.6,3.4,10.6,"Złącze 2×10","pola lutownicze od tyłu obudowy")
rz1 = ["PE","NTC1","ICP","8V","K1","K2","K3","K4","1.65","CP"]
rz2 = ["GND","GND","CT","NTC2","ZL3","ZL2","ZL1","V1","V2","V3"]
for i,(a,b) in enumerate(zip(rz1,rz2)):
    yy = 9.8 - i*0.52
    kol_a = C_WARN if a=="PE" else ("#222")
    ax.text(1.15,yy,a,fontsize=8.6,ha="right",color=kol_a,fontweight="bold")
    ax.add_patch(Circle((1.45,yy),0.05,fc="#999",ec="#666",zorder=5))
    ax.add_patch(Circle((2.05,yy),0.05,fc="#999",ec="#666",zorder=5))
    ax.text(2.35,yy,b,fontsize=8.6,ha="left",color=("#222" if b!="GND" else C_GND),fontweight="bold")
ax.text(1.9,4.85,"PE i drugi GND: BEZ odczepu",fontsize=7.6,ha="center",color=C_WARN)

# blok odczepow
box(ax,4.4,7.2,8.4,10.6,"Odczepy typ P / typ D","na płytce uniwersalnej MS-TSOP1")
ax.text(4.65,9.7,"typ P (pomiarowy):",fontsize=8.8,fontweight="bold",color="#222")
ax.text(4.65,9.42,"pin → 100k → 100k → [klamra 2×1N4148] → 10k → MUX",fontsize=8,color="#333")
ax.text(4.65,9.14,"dotyczy: V1–V3, ZL1–ZL3, ICP, NTC1, NTC2",fontsize=7.8,color="#555")
ax.text(4.65,8.62,"typ D (z dzielnikiem ×0,524):",fontsize=8.8,fontweight="bold",color="#222")
ax.text(4.65,8.34,"jak typ P + 220 kΩ z węzła klamry do masy",fontsize=8,color="#333")
ax.text(4.65,8.06,"dotyczy: K1–K4 (7,45 V→3,90 V; anomalia K4: 5,08→2,66 V), 8V",fontsize=7.8,color="#555")
ax.text(4.65,7.55,"tory dedykowane: CT (ark. B), 1.65 (ark. B), CP (ark. C)",fontsize=8,color=C_INFO)

# muxy
box(ax,9.4,6.4,13.0,10.6,"2× CD4051BE (DIP16)","adres wspólny D4–D6; INH→masa; 100 nF przy każdym")
ax.text(9.6,9.7,"MUX1 → A2:",fontsize=8.6,fontweight="bold",color="#222")
m1 = "0:V1  1:V2  2:V3  3:ZL1\n4:ZL2  5:ZL3  6:ICP  7:DET.SZCZYTU"
ax.text(9.6,9.16,m1,fontsize=8,color="#333")
ax.text(9.6,8.44,"MUX2 → A3:",fontsize=8.6,fontweight="bold",color="#222")
m2 = "0:K1  1:K2  2:K3  3:K4\n4:8V  5:NTC1  6:NTC2  7:MASA (autotest)"
ax.text(9.6,7.9,m2,fontsize=8,color="#333")
ax.text(9.6,7.12,"na A2/A3: 470 pF do masy; po zmianie adresu\nczas ustalania 0,7 ms; pierwsza konwersja odrzucana",fontsize=7.8,color="#555")
ax.text(9.6,6.65,"werdykt „ekspandery”: nie cyfrowe (MCP23017),\nlecz multipleksery ANALOGOWE — to one mnożą wejścia",fontsize=7.8,color=C_INFO)

# UNO
box(ax,13.9,4.6,17.1,10.6,"Arduino UNO","akwizycja w przerwaniu ADC; strumień binarny")
piny_uno = [("A0","CT (2 kHz)"),("A1","poziomy CP"),("A2","wyjście MUX1"),("A3","wyjście MUX2"),
            ("A4","1.65 (2 kHz)"),("A5","rezerwa"),("D2","licznik UART DWIN"),("D4–D6","adres MUX"),
            ("D8","komparator (Timer1)"),("D13","LED „żyję”"),("USB","250 000 bodów, laptop (bateria!)")]
for i,(p,o) in enumerate(piny_uno):
    ax.text(14.15,9.72-i*0.47,p,fontsize=8.4,fontweight="bold",color=C_OK)
    ax.text(15.15,9.72-i*0.47,o,fontsize=8.2,color="#333")

# strzalki przeplywu
for y0 in [9.3, 8.4]:
    wire(ax,[(3.4,y0),(4.4,y0)],C_SIG,1.8)
wire(ax,[(8.4,9.0),(9.4,9.0)],C_SIG,1.8)
wire(ax,[(13.0,8.5),(13.9,8.5)],C_SIG,1.8)
ax.text(3.9,9.55,"20 żył",fontsize=7.6,color=C_SIG,ha="center")

# UART DWIN
box(ax,4.4,4.9,8.4,6.6,"Odczep UART wyświetlacza DWIN","znacznik chwili błędu")
ax.text(4.65,5.86,"linia TX płytki kontrolnej → 100k → 100k →",fontsize=8,color="#333")
ax.text(4.65,5.54,"[klamra 2×1N4148] → D2 (licznik zboczy w oknach 20 ms)",fontsize=8,color="#333")
ax.text(4.65,5.16,"przed montażem zmierzyć poziom (3,3/5 V);\nminimum zastępcze: kamera na ekran + zegar",fontsize=7.6,color="#555")
wire(ax,[(8.4,5.8),(13.6,5.8),(13.9,5.8)],C_SIG,1.6)

# zasady bezpieczenstwa
ax.add_patch(FancyBboxPatch((0.4,2.5),16.7,1.7,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#FEE2E2",ec=C_WARN,lw=1.4))
ax.text(0.65,3.9,"BEZPIECZEŃSTWO (szczegóły: §5 dokumentu):",fontsize=9.2,fontweight="bold",color=C_WARN)
ax.text(0.65,3.55,"• PRZED pierwszą sesją pomiar rozstrzygający charakter masy (GND↔N/L omomierzem przy odłączonym; GND→PE True-RMS przy zasilonym) — decyduje o reżimie A/B;",fontsize=8.2,color="#7A1E1E")
ax.text(0.65,3.2,"• reżim B (masa związana z siecią) = sesji NIE prowadzić • laptop przez całą sesję NA BATERII, zasilacz poza pokojem • PE NIGDY do masy rejestratora;",fontsize=8.2,color="#7A1E1E")
ax.text(0.65,2.85,"• jeden pin GND złącza → masa UNO (jedyne połączenie mas) • sekwencja: rejestrator zasilony PRZED ładowarką • tor mocy 40 A osłonięty na czas sesji (RCD 30 mA).",fontsize=8.2,color="#7A1E1E")

ax.add_patch(FancyBboxPatch((0.4,0.3),16.7,1.9,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#DCFCE7",ec=C_OK,lw=1.2))
ax.text(0.65,1.9,"KLASYFIKACJA (odpowiedź na pytanie o analog/cyfra/ekspandery):",fontsize=9.2,fontweight="bold",color=C_OK)
ax.text(0.65,1.55,"analogowe szybkie: CT, 1.65 (po 2 kHz) i CP (±12 V; poziomy + wypełnienie) • analogowe wolne (multiplekser, ~100 obiegów/s): V1–V3, NTC1–2, 8V, detektor szczytu;",fontsize=8.2,color="#14532D")
ax.text(0.65,1.2,"quasi-cyfrowe o poziomie 7,45 V czytane ANALOGOWO (przez dzielnik ×0,524): K1–K4 — bo tylko odczyt analogowy pokazuje anomalię K4 = 5,08 V wprost;",fontsize=8.2,color="#14532D")
ax.text(0.65,0.85,"cyfrowe: wyjście komparatora CP (D8), licznik aktywności UART (D2) • nieznane (rekonesans wg tabeli decyzyjnej): ICP, ZL1–ZL3 (chiński opis: prąd czy napięcie?);",fontsize=8.2,color="#14532D")
ax.text(0.65,0.5,"ekspandery cyfrowe NIEPOTRZEBNE — wejścia mnożą 2× CD4051BE (multipleksery analogowe), wejść cyfrowych UNO wystarcza.",fontsize=8.2,color="#14532D")
plt.tight_layout(pad=0.4)
plt.savefig(OUT + r"\AMPERE_POINT_rejestrator_Q11_schemat_A_architektura.png",dpi=200,bbox_inches="tight",facecolor="white")
plt.close(fig)
print("OK: 3 arkusze zapisane w", OUT)
