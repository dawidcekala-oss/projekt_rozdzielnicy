# -*- coding: utf-8 -*-
"""Schemat zasilania sondy z linii +12 V COM-MANUAL (filtr R+C -> VIN)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\schematy\schemat_zasilania_12V.png"

fig, ax = plt.subplots(figsize=(17.5, 10.5), dpi=200)
ax.set_xlim(0, 17.5); ax.set_ylim(0, 10.5); ax.axis("off")

C_12="#B00020"; C_GND="#111111"; C_N="#B45309"; C_BOX="#F4F4F2"; C_EDGE="#333333"
C_OK="#15803D"; C_INFO="#0369A1"; C_MUT="#777777"

def box(x0,y0,x1,y1,title,sub=None):
    ax.add_patch(FancyBboxPatch((x0,y0),x1-x0,y1-y0,boxstyle="round,pad=0.04,rounding_size=0.12",fc=C_BOX,ec=C_EDGE,lw=1.6))
    ax.text((x0+x1)/2,y1-0.32,title,ha="center",va="center",fontsize=12,fontweight="bold",color="#222")
    if sub: ax.text((x0+x1)/2,y1-0.66,sub,ha="center",va="center",fontsize=8.6,color="#555")

def pin(x,y,label,side="right",color="#222",fs=9.4):
    ax.add_patch(Circle((x,y),0.07,fc="white",ec=color,lw=1.6,zorder=5))
    dx=0.16 if side=="right" else -0.16; ha="left" if side=="right" else "right"
    ax.text(x+dx,y,label,ha=ha,va="center",fontsize=fs,fontweight="bold",color=color,zorder=6)

def wire(pts,color,lw=2.8):
    ax.plot([p[0] for p in pts],[p[1] for p in pts],color=color,lw=lw,solid_capstyle="round",zorder=3)

def dot(x,y,color):
    ax.add_patch(Circle((x,y),0.09,fc=color,ec=color,zorder=6))

def wlabel(x,y,t,color,fs=9.2):
    ax.text(x,y+0.13,t,ha="center",va="bottom",fontsize=fs,color=color,fontweight="bold",zorder=6,
            bbox=dict(fc="white",ec="none",pad=0.5))

def res_h(xc,yc,label,sub=None):
    ax.add_patch(Rectangle((xc-0.55,yc-0.17),1.1,0.34,fc="white",ec="#222",lw=1.8,zorder=5))
    ax.text(xc,yc+0.34,label,ha="center",fontsize=9.4,color="#222",fontweight="bold",zorder=6)
    if sub: ax.text(xc,yc-0.42,sub,ha="center",fontsize=8.2,color="#555",zorder=6)

def kondensator(xc,yc,label):
    # symbol elektrolita: dwie kreski, jedna gruba (minus)
    ax.plot([xc-0.22,xc+0.22],[yc+0.10,yc+0.10],color="#222",lw=2.6,zorder=5)
    ax.plot([xc-0.22,xc+0.22],[yc-0.10,yc-0.10],color="#222",lw=5.0,zorder=5)
    ax.text(xc+0.32,yc+0.18,"+",fontsize=11,color="#222",fontweight="bold",zorder=6)
    ax.text(xc+0.45,yc-0.02,label,ha="left",fontsize=9.2,color="#222",fontweight="bold",zorder=6)

ax.text(8.75,10.18,"Zasilanie sondy z linii +12 V portu COM-MANUAL \u2014 filtr R+C przed przetwornic\u0105 (wersja 2: R = 25 \u03a9)",
        ha="center",fontsize=14,fontweight="bold")

# ── Klimatyzator ──
box(0.4,4.6,3.6,9.3,"KLIMATYZATOR","gniazdo COM-MANUAL")
pin(3.6,8.3,"+12 V","left",C_12)
pin(3.6,5.6,"GND","left",C_GND)
ax.text(2.0,7.2,"wyj\u015bcie zasilacza\npomocniczego jednostki\n(bud\u017cet: klasa pilota\nprzewodowego)",fontsize=8.4,color="#555",ha="center")

# ── Filtr ──
box(5.0,4.0,9.6,9.3,"FILTR (wlutowany w wi\u0105zk\u0119)")
# tor +12: od pinu do rezystora do wezla
wire([(3.6,8.3),(5.6,8.3)],C_12); wlabel(4.6,8.3,"bia\u0142a \u017cy\u0142a",C_12)
res_h(6.35,8.3,"R = 4\u00d7 100 \u03a9 r\u00f3wnolegle = 25 \u03a9","ka\u017cdy niesie 1/4 mocy")
wire([(6.9,8.3),(8.6,8.3)],C_12)
dot(8.6,8.3,C_N)
ax.text(8.82,8.02,"w\u0119ze\u0142",ha="left",fontsize=9.2,color=C_N,fontweight="bold")
# kondensatory z wezla do masy
wire([(8.6,8.3),(8.6,6.9)],C_N)
kondensator(8.6,6.6,"C = 3\u00d7 100 \u00b5F/50 V\nr\u00f3wnolegle = 300 \u00b5F")
wire([(8.6,6.3),(8.6,5.6)],C_GND)
dot(8.6,5.6,C_GND)
# masa
wire([(3.6,5.6),(13.9,5.6)],C_GND); wlabel(5.6,5.6,"\u017c\u00f3\u0142ta \u017cy\u0142a \u2014 masa wsp\u00f3lna",C_GND)

# ── WeMos ──
box(11.4,3.4,17.1,9.3,"WeMos D1 R1 \u2014 tor zasilania","USB i jack zostaj\u0105 PUSTE")
wire([(8.6,8.3),(11.9,8.3)],C_N)
wlabel(10.25,8.3,"10,7 V praca • 9,7 V start WiFi",C_N,8.6)
pin(11.9,8.3,"pin VIN","right",C_N)
# wewnetrzny lancuch
ax.annotate("",xy=(13.35,8.3),xytext=(12.75,8.3),arrowprops=dict(arrowstyle="-|>",lw=1.6,color=C_MUT))
ax.add_patch(Rectangle((13.4,8.05),0.9,0.5,fc="white",ec="#555",lw=1.3,zorder=5))
ax.text(13.85,8.3,"dioda",ha="center",va="center",fontsize=8.4,color="#333",zorder=6)
ax.text(13.85,7.78,"\u22120,4 V",ha="center",fontsize=8,color="#777")
ax.annotate("",xy=(14.9,8.3),xytext=(14.3,8.3),arrowprops=dict(arrowstyle="-|>",lw=1.6,color=C_MUT))
ax.add_patch(Rectangle((14.95,7.95),1.7,0.7,fc="#FDF3E7",ec=C_N,lw=1.5,zorder=5))
ax.text(15.8,8.42,"PRZETWORNICA",ha="center",fontsize=8.2,color=C_N,fontweight="bold",zorder=6)
ax.text(15.8,8.14,"obni\u017caj\u0105ca \u2192 5 V",ha="center",fontsize=8.2,color="#333",zorder=6)
ax.text(15.8,7.6,"odbiornik STA\u0141EJ MOCY:\nmniej wolt\u00f3w = wi\u0119cej amper\u00f3w",ha="center",fontsize=7.8,color=C_INFO)
# 5V -> LDO -> ESP
ax.annotate("",xy=(15.8,6.7),xytext=(15.8,7.3),arrowprops=dict(arrowstyle="-|>",lw=1.6,color=C_MUT))
ax.add_patch(Rectangle((14.95,6.1),1.7,0.6,fc="white",ec="#555",lw=1.3,zorder=5))
ax.text(15.8,6.4,"stabilizator 3,3 V",ha="center",fontsize=8.2,color="#333",zorder=6)
ax.annotate("",xy=(15.8,5.5),xytext=(15.8,6.05),arrowprops=dict(arrowstyle="-|>",lw=1.6,color=C_MUT))
ax.add_patch(Rectangle((14.75,4.7),2.1,0.75,fc="#E8F4FD",ec=C_INFO,lw=1.5,zorder=5))
ax.text(15.8,5.2,"ESP8266 (WiFi)",ha="center",fontsize=8.6,color=C_INFO,fontweight="bold",zorder=6)
ax.text(15.8,4.92,"+ bramka RS485 z pinu 5V",ha="center",fontsize=7.6,color="#333",zorder=6)
ax.text(13.0,6.2,"wymaga > 6,5 V\nna wej\u015bciu \u2014 mamy\n9,3\u201310,3 V \u2713",fontsize=8.4,color=C_OK,ha="center",fontweight="bold")

# ── Panele dolne ──
ax.add_patch(FancyBboxPatch((0.4,1.9),8.3,1.9,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#DCFCE7",ec=C_OK,lw=1.3))
ax.text(0.65,3.5,"DLACZEGO JEDNOSTKA ZAWSZE WSTANIE (rola rezystora):",fontsize=9,fontweight="bold",color=C_OK,ha="left")
ax.text(0.65,3.12,"\u2022 sufit pr\u0105du: 12 V / 25 \u03a9 = 480 mA \u2014 nieprzekraczalny fizycznie, cokolwiek robi elektronika za rezystorem",fontsize=8.4,color="#14532D",ha="left")
ax.text(0.65,2.76,"\u2022 sufit trwa tylko 7,5 ms (\u0142adowanie kondensator\u00f3w), potem pr\u0105d spada do 63\u201395 mA \u2014 klasa fabrycznego pilota",fontsize=8.4,color="#14532D",ha="left")
ax.text(0.65,2.40,"\u2022 przy trwa\u0142ym zwarciu rezystory przepalaj\u0105 si\u0119 jak bezpiecznik i od\u0142\u0105czaj\u0105 uk\u0142ad od linii",fontsize=8.4,color="#14532D",ha="left")
ax.text(0.65,2.04,"\u2022 b\u0142\u0105d wersji 1: R=47 \u03a9 przepuszcza\u0142 max 0,77 W < 0,9 W fazy \u0142\u0105czenia WiFi \u2192 zapa\u015b\u0107 i grzanie rezystora",fontsize=8.4,color="#7A1E1E",ha="left")

ax.add_patch(FancyBboxPatch((9.1,1.9),8.0,1.9,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#E8F4FD",ec=C_INFO,lw=1.3))
ax.text(9.35,3.5,"WSP\u00d3\u0141PRACA Z PRZETWORNIC\u0104 (rola kondensator\u00f3w):",fontsize=9,fontweight="bold",color=C_INFO,ha="left")
ax.text(9.35,3.12,"\u2022 punkt pracy = przeci\u0119cie prostej rezystora z hiperbol\u0105 sta\u0142ej mocy: V = [12+\u221a(144\u22124PR)]/2",fontsize=8.4,color="#0C4A6E",ha="left")
ax.text(9.35,2.76,"\u2022 sufit mocy U\u00b2/4R = 1,44 W > 0,9 W startu WiFi (zapas 60%); stabilno\u015b\u0107: |\u2212V\u00b2/P| \u2248 100\u2013230 \u03a9 \u226b 25 \u03a9",fontsize=8.4,color="#0C4A6E",ha="left")
ax.text(9.35,2.40,"\u2022 impuls nadawania (~1,65 W, pojedyncze ms) pokrywa kondensator: do\u0142ek 1\u20132 V, w\u0119ze\u0142 wci\u0105\u017c > 7 V",fontsize=8.4,color="#0C4A6E",ha="left")
ax.text(9.35,2.04,"\u2022 mi\u0119dzy impulsami rezystor do\u0142adowuje magazyn w ~25 ms (3\u00d7 sta\u0142a czasowa RC)",fontsize=8.4,color="#0C4A6E",ha="left")

ax.add_patch(FancyBboxPatch((0.4,0.15),16.7,1.4,boxstyle="round,pad=0.04,rounding_size=0.1",fc="#FEF3C7",ec="#D97706",lw=1.3))
ax.text(0.65,1.28,"MONTA\u017b I TEST (szczeg\u00f3\u0142y: ZASILANIE_OBLICZENIA.pdf, rozdz. 7\u20139):",fontsize=9,fontweight="bold",color="#7A5800",ha="left")
ax.text(0.65,0.92,"\u2022 elektrolity PASKIEM (minusem) do masy \u2022 rezystory jednakowe, 4 sztuki \u2014 ka\u017cdy przenosi u\u0142amek mocy \u2022 USB/jack odpi\u0119te przy zasilaniu z VIN",fontsize=8.4,color="#7A5800",ha="left")
ax.text(0.65,0.56,"test przed zamkni\u0119ciem puszki: omomierz (25\u201328 \u03a9 bia\u0142a\u2194VIN, rosn\u0105cy odczyt bia\u0142a\u2194masa) \u2192 linia \u226511 V pod obci\u0105\u017ceniem \u2192 w\u0119ze\u0142 8\u201311 V \u2192 3\u00d7 bezpiecznik \u2192 pilot IR \u2192 10 min logu",fontsize=8.4,color="#7A5800",ha="left")

plt.tight_layout(pad=0.4)
plt.savefig(OUT,dpi=200,bbox_inches="tight",facecolor="white")
print("OK:",OUT)
