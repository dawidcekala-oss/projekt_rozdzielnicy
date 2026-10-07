# -*- coding: utf-8 -*-
"""Schemat FINALNY zweryfikowanego polaczenia sondy (2026-08-22) - v2 bez kolizji."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\schematy\schemat_FINALNY_dzialajacy.png"

fig, ax = plt.subplots(figsize=(17.5, 11.5), dpi=200)
ax.set_xlim(0, 17.5); ax.set_ylim(0, 11.5); ax.axis("off")

C_5V="#D62728"; C_GND="#111111"; C_TX="#1F77B4"; C_RX="#9467BD"; C_DIR="#8C564B"
C_A="#2CA02C"; C_B="#FF7F0E"; C_BOX="#F4F4F2"; C_EDGE="#333333"; C_WARN="#B00020"; C_MUT="#999999"
C_OK="#15803D"

def box(x0,y0,x1,y1,title,sub=None):
    ax.add_patch(FancyBboxPatch((x0,y0),x1-x0,y1-y0,boxstyle="round,pad=0.04,rounding_size=0.12",fc=C_BOX,ec=C_EDGE,lw=1.6))
    ax.text((x0+x1)/2,y1-0.32,title,ha="center",va="center",fontsize=12,fontweight="bold",color="#222")
    if sub: ax.text((x0+x1)/2,y1-0.68,sub,ha="center",va="center",fontsize=8.6,color="#555")

def pin(x,y,label,side="right",color="#222",fs=9.6,muted=False):
    ax.add_patch(Circle((x,y),0.07,fc="white",ec=color,lw=1.6,zorder=5))
    dx=0.16 if side=="right" else -0.16; ha="left" if side=="right" else "right"
    ax.text(x+dx,y,label,ha=ha,va="center",fontsize=fs,
            fontweight="normal" if muted else "bold",color=color,zorder=6)

def wire(pts,color,lw=2.6):
    ax.plot([p[0] for p in pts],[p[1] for p in pts],color=color,lw=lw,solid_capstyle="round",zorder=3)

def dot(x,y,color):
    ax.add_patch(Circle((x,y),0.09,fc=color,ec=color,zorder=6))

def wlabel(x,y,t,color,fs=9.4):
    ax.text(x,y+0.13,t,ha="center",va="bottom",fontsize=fs,color=color,fontweight="bold",zorder=6,
            bbox=dict(fc="white",ec="none",pad=0.5))

def res_h(xc,yc,label):
    ax.add_patch(Rectangle((xc-0.42,yc-0.15),0.84,0.30,fc="white",ec="#222",lw=1.7,zorder=5))
    ax.text(xc,yc+0.30,label,ha="center",fontsize=8.8,color="#222",fontweight="bold",zorder=6)

def res_v(xc,yc,label):
    ax.add_patch(Rectangle((xc-0.15,yc-0.42),0.30,0.84,fc="white",ec="#222",lw=1.7,zorder=5))
    ax.text(xc+0.26,yc,label,ha="left",va="center",fontsize=8.8,color="#222",fontweight="bold",zorder=6)

ax.text(8.75,11.15,"SCHEMAT FINALNY \u2014 zweryfikowane po\u0142\u0105czenie sondy COM-MANUAL (dzia\u0142a od 2026-08-22)",
        ha="center",fontsize=14.5,fontweight="bold",color=C_OK)
ax.text(8.75,10.75,"WeMos D1 R1 \u2194 bramka GRZ47-G (jako konwerter UART\u2194RS485) \u2194 gniazdo COM-MANUAL p\u0142yty GRZ4M-A3 \u2022 1200 bod\u00F3w, 8N1",
        ha="center",fontsize=10,color="#444")

# WeMos: kolejnosc pinow od gory: 5V, D7, D6, D5, GND
box(0.5,2.7,4.6,10.1,"WeMos D1 R1 (ESP8266)","zasilanie: micro-USB 5 V (w\u0142asny zasilacz!)")
pin(4.6,9.5,"5V","left",C_5V)
pin(4.6,8.7,"D11/MOSI/D7","left",C_DIR)
pin(4.6,7.9,"D12/MISO/D6","left",C_TX)
pin(4.6,6.8,"D13/SCK/D5","left",C_RX)
pin(4.6,5.4,"GND","left",C_GND)
ax.text(2.5,3.35,"UWAGA: piny wg PE\u0141NEGO nadruku!\nVIN nie u\u017Cywany (patrz raport)",fontsize=8.2,color=C_WARN,ha="center")

# CN2
box(7.7,2.7,11.4,10.1,"BRAMKA \u2014 z\u0142\u0105cze CN2","przez czerwone z\u0142\u0105cze krosowe i kabel fabryczny")
pin(7.7,9.5,"+5V (czerwona)","right",C_5V,8.8)
pin(7.7,8.7,"TXP (\u017C\u00F3\u0142ta) \u2014 w\u0142. nadajnika","right",C_DIR,8.8)
pin(7.7,7.9,"\u201ETXD\u201D = wej\u015Bcie danych","right",C_TX,8.8)
pin(7.7,6.8,"\u201ERXD\u201D = wyj\u015Bcie danych","right",C_RX,8.8)
pin(7.7,5.6,"GND","right",C_GND,8.8)
pin(7.7,4.9,"RXP (bia\u0142a) \u2014 w\u0142. odbiornika","right",C_GND,8.8)
pin(7.7,3.6,"PE / PE","right",C_MUT,8.8,muted=True)
ax.text(8.6,3.32,"wolne",fontsize=8,color=C_MUT,ha="center")
pin(11.4,8.1,"blaszki X1+X3 = A","left",C_A,9.2)
pin(11.4,6.9,"blaszki X2+X4 = B","left",C_B,9.2)
ax.text(9.6,10.28,"opisy \u201ETXD/RXD\u201D na laminacie s\u0105 z perspektywy KLIMATYZATORA \u2014 st\u0105d po\u0142\u0105czenie \u201Ena wprost\u201D",
        fontsize=8.2,color=C_WARN,ha="center")

# Klimatyzator
box(13.9,2.7,17.1,10.1,"KLIMATYZATOR","GRZ4M-A3 \u2014 gniazdo COM-MANUAL")
pin(13.9,8.1,"A","right",C_A)
pin(13.9,6.9,"B","right",C_B)
pin(13.9,5.2,"GND","right",C_GND)
pin(13.9,8.9,"+12V","right",C_WARN)
ax.plot([13.75,14.05],[8.75,9.05],color=C_WARN,lw=2.4,zorder=7)
ax.plot([13.75,14.05],[9.05,8.75],color=C_WARN,lw=2.4,zorder=7)
ax.text(14.85,8.9,"\u2190 NIE POD\u0141\u0104CZA\u0106 (blokuje start!)",fontsize=8.2,color=C_WARN,fontweight="bold",ha="left")

# Przewody proste
wire([(4.6,9.5),(7.7,9.5)],C_5V); wlabel(6.15,9.5,"+5 V",C_5V)
wire([(4.6,8.7),(7.7,8.7)],C_DIR); wlabel(6.15,8.7,"D7 \u2192 TXP (klucz nadawania)",C_DIR)
wire([(4.6,7.9),(7.7,7.9)],C_TX); wlabel(6.15,7.9,"D6 \u2192 \u201ETXD\u201D (nadawanie)",C_TX)

# Dzielnik na linii odbioru
wire([(7.7,6.8),(6.85,6.8)],C_RX)
res_h(6.4,6.8,"3,3 k\u03A9")
wire([(5.98,6.8),(4.6,6.8)],C_RX)
dot(5.3,6.8,C_RX)
wire([(5.3,6.8),(5.3,6.5)],C_RX)
res_v(5.3,6.08,"6,5 k\u03A9")
wire([(5.3,5.66),(5.3,5.4)],C_GND)
dot(5.3,5.4,C_GND)
wlabel(7.25,6.8,"\u201ERXD\u201D \u2192 D5",C_RX)
ax.text(4.95,7.08,"\u22483,3 V",fontsize=8.6,color=C_RX,ha="center",fontweight="bold")
ax.text(6.62,5.85,"dzielnik: 5 V \u2192 3,3 V (chroni ESP8266)",fontsize=8.2,color=C_RX,ha="center")

# Masa: szyna od GND WeMosa
wire([(4.6,5.4),(7.05,5.4),(7.05,5.6),(7.7,5.6)],C_GND); wlabel(6.0,5.42,"GND",C_GND)
dot(6.6,5.4,C_GND)
wire([(6.6,5.4),(6.6,4.9),(7.7,4.9)],C_GND)
wlabel(7.08,4.92,"\u2192 RXP",C_GND)
ax.text(6.62,4.5,"odbi\u00F3r w\u0142\u0105czony na sta\u0142e",fontsize=8.2,color="#444",ha="center")
dot(4.85,5.4,C_GND)
wire([(4.85,5.4),(4.85,1.6),(13.1,1.6),(13.1,5.2),(13.9,5.2)],C_GND)
wlabel(9.0,1.6,"masa wsp\u00F3lna \u2014 \u017C\u00F3\u0142ta \u017Cy\u0142a pigtaila do GND gniazda (obowi\u0105zkowa)",C_GND)

# A/B
wire([(11.4,8.1),(13.9,8.1)],C_A,lw=3.2); wlabel(12.65,8.1,"konektor CZARNY \u2192 A",C_A)
wire([(11.4,6.9),(13.9,6.9)],C_B,lw=3.2); wlabel(12.65,6.9,"konektor CZERWONY \u2192 B",C_B)
ax.text(12.65,6.32,"pigtail JST \u2192 wtyczka\nw gniazdo COM-MANUAL",fontsize=8.2,color="#555",ha="center")

# Panele dolne
ax.add_patch(FancyBboxPatch((0.5,0.12),10.6,1.15,boxstyle="round,pad=0.04,rounding_size=0.1",
                            fc="#DCFCE7",ec=C_OK,lw=1.3))
ax.text(0.75,1.03,"ZWERYFIKOWANE POMIARAMI (2026-08-22):",fontsize=9,fontweight="bold",color=C_OK,ha="left")
ax.text(0.75,0.68,"nadajnik: \u00B14,8 V na A\u2013B \u2022 odbiornik: czyta polaryzacj\u0119 szyn \u2022 X1\u2194X3 i X2\u2194X4 zwarte wewn\u0119trznie (pary przelotowe)",
        fontsize=8.6,color="#14532D",ha="left")
ax.text(0.75,0.35,"jednostka odpowiada ramk\u0105 7E 7E FF 40 11 17 ... (29 bajt\u00F3w, suma XOR poprawna) na ka\u017Cd\u0105 sond\u0119 \u2022 pilot IR dzia\u0142a r\u00F3wnolegle",
        fontsize=8.6,color="#14532D",ha="left")

ax.add_patch(FancyBboxPatch((11.5,0.12),5.6,1.15,boxstyle="round,pad=0.04,rounding_size=0.1",
                            fc="#FEF3C7",ec="#D97706",lw=1.3))
ax.text(11.75,1.03,"Firmware:",fontsize=9,fontweight="bold",color="#7A5800",ha="left")
ax.text(11.75,0.68,"sonda_gree_wemos_wifi.ino \u2022 log przez WiFi",fontsize=8.6,color="#7A5800",ha="left")
ax.text(11.75,0.35,"bia\u0142y przew\u00F3d +12 V pigtaila: zaizolowany, wolny",fontsize=8.6,color="#7A5800",ha="left")

plt.tight_layout(pad=0.4)
plt.savefig(OUT,dpi=200,bbox_inches="tight",facecolor="white")
print("OK:",OUT)
