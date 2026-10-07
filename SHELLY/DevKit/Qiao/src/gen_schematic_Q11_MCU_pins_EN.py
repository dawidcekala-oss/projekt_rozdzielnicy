"""English version of generuj_schemat_procesora.py for the Q11 factory.
Generates schematic_Q11_MCU_pins_EN.tex (compile with xelatex). AMPERE POINT, 2026-09-28."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "schematic_Q11_MCU_pins_EN.tex")

NAMES = {1: "VBAT", 2: "PC13", 3: "PC14", 4: "PC15", 5: "PD0 OSC\\_IN", 6: "PD1 OSC\\_OUT", 7: "NRST",
         8: "PC0", 9: "PC1", 10: "PC2", 11: "PC3", 12: "VSSA", 13: "VDDA", 14: "PA0", 15: "PA1",
         16: "PA2 USART TX", 17: "PA3 USART RX", 18: "VSS", 19: "VDD", 20: "PA4", 21: "PA5", 22: "PA6",
         23: "PA7", 24: "PC4", 25: "PC5", 26: "PB0", 27: "PB1", 28: "PB2 BOOT1", 29: "PB10", 30: "PB11",
         31: "VSS", 32: "VDD", 33: "PB12", 34: "PB13", 35: "PB14", 36: "PB15", 37: "PC6", 38: "PC7",
         39: "PC8", 40: "PC9", 41: "PA8", 42: "PA9", 43: "PA10", 44: "PA11", 45: "PA12",
         46: "PA13 SWDIO", 47: "VSS", 48: "VDD", 49: "PA14 SWCLK", 50: "PA15", 51: "PC10", 52: "PC11",
         53: "PC12", 54: "PD2", 55: "PB3", 56: "PB4", 57: "PB5", 58: "PB6", 59: "PB7", 60: "BOOT0",
         61: "PB8", 62: "PB9", 63: "VSS", 64: "VDD"}

MEASURED = {"d13": "8 VCC", "p16": "8 VCC", "u1": "8 VCC", "d1": "8 VCC", "l1": "8 VCC", "p3": "8 VCC",
            "p1": "16 TXD", "d16": "15 RXD",
            "d12": "9 GND", "p2": "9 GND", "p15": "9 GND", "u2": "9 GND", "l2": "9 GND"}
COLOR = {"8 VCC": "pwrred", "16 TXD": "txblue", "15 RXD": "rxgreen", "9 GND": "black"}


def std(side, n):
    return {"d": n, "p": 16 + n, "u": 49 - n, "l": 65 - n}[side]


X0, Y0, X1, Y1 = 9.0, 4.2, 18.0, 13.2
PITCH = 0.5
FIRST = 0.75


def pin_nodes():
    out = []
    for side in "dupl":
        for n in range(1, 17):
            s = std(side, n)
            name = NAMES[s]
            key = f"{side}{n}"
            pad = MEASURED.get(key)
            col = COLOR.get(pad, "black")
            if side in "du":
                x = X0 + FIRST + PITCH * (n - 1)
                if side == "d":
                    y, y2 = Y0, Y0 - 0.28
                    out.append(rf"\draw[fill={'black!55' if not pad else col}, draw=black] ({x-0.12:.2f},{y2:.2f}) rectangle ({x+0.12:.2f},{y:.2f});")
                    lab = rf"\textbf{{{key}}}\ \ {{\color{{black!55}}{s} {name}}}"
                    if pad:
                        lab += rf"\ \ {{\color{{{col}}}\textbf{{\la\ {pad}}}}}"
                    out.append(rf"\node[rotate=90, anchor=east, font=\scriptsize] at ({x:.2f},{y2-0.05:.2f}) {{{lab}}};")
                else:
                    y, y2 = Y1, Y1 + 0.28
                    out.append(rf"\draw[fill={'black!55' if not pad else col}, draw=black] ({x-0.12:.2f},{y:.2f}) rectangle ({x+0.12:.2f},{y2:.2f});")
                    lab = rf"\textbf{{{key}}}\ \ {{\color{{black!55}}{s} {name}}}"
                    if pad:
                        lab += rf"\ \ {{\color{{{col}}}\textbf{{\la\ {pad}}}}}"
                    out.append(rf"\node[rotate=90, anchor=west, font=\scriptsize] at ({x:.2f},{y2+0.05:.2f}) {{{lab}}};")
            else:
                y = Y0 + FIRST + PITCH * (n - 1)
                if side == "l":
                    x, x2 = X0, X0 - 0.28
                    out.append(rf"\draw[fill={'black!55' if not pad else col}, draw=black] ({x2:.2f},{y-0.12:.2f}) rectangle ({x:.2f},{y+0.12:.2f});")
                    lab = rf"{{\color{{black!55}}{s} {name}}}\ \ \textbf{{{key}}}"
                    if pad:
                        lab = rf"{{\color{{{col}}}\textbf{{{pad} \ra}}}}\ \ " + lab
                    out.append(rf"\node[anchor=east, font=\scriptsize] at ({x2-0.05:.2f},{y:.2f}) {{{lab}}};")
                else:
                    x, x2 = X1, X1 + 0.28
                    out.append(rf"\draw[fill={'black!55' if not pad else col}, draw=black] ({x:.2f},{y-0.12:.2f}) rectangle ({x2:.2f},{y+0.12:.2f});")
                    lab = rf"\textbf{{{key}}}\ \ {{\color{{black!55}}{s} {name}}}"
                    if pad:
                        lab += rf"\ \ {{\color{{{col}}}\textbf{{\la\ {pad}}}}}"
                    out.append(rf"\node[anchor=west, font=\scriptsize] at ({x2+0.05:.2f},{y:.2f}) {{{lab}}};")
    return "\n".join(out)


TABLE_ROWS = []
for key, pad in list(MEASURED.items()):
    side, n = key[0], int(key[1:])
    s = std(side, n)
    TABLE_ROWS.append((pad, key, s, NAMES[s], "measured"))
order = {"16 TXD": 0, "15 RXD": 1, "8 VCC": 2, "9 GND": 3}
TABLE_ROWS.sort(key=lambda r: (order.get(r[0], 9), r[2]))
rows_tex = "\n".join(rf"{p} & {k} & {s} & {nm} & {st} \\" for p, k, s, nm, st in TABLE_ROWS)

TEX = r"""% !TEX program = xelatex
\documentclass[10pt]{article}
\usepackage{fontspec}
\setmainfont{Calibri}
\newfontfamily\sym{Segoe UI Symbol}
\usepackage[table]{xcolor}
\usepackage{geometry}
\geometry{a4paper,landscape,margin=0.8cm}
\usepackage{tikz}
\usepackage{booktabs,array}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\definecolor{txblue}{HTML}{1D4ED8}
\definecolor{rxgreen}{HTML}{15803D}
\definecolor{pwrred}{HTML}{B91C1C}
\definecolor{ncgrey}{HTML}{6B7280}
\definecolor{padfill}{HTML}{F59E0B}
\definecolor{copper}{HTML}{C2410C}
\definecolor{modblue}{HTML}{DBEAFE}
\newcommand{\ra}{{\sym →}}
\newcommand{\la}{{\sym ←}}
\begin{document}
\begin{tikzpicture}[x=1cm,y=1cm]
\node[anchor=north west, text width=27.5cm] at (0,19.4) {%
{\Large\bfseries Q11 controller: package pins and the U10 pads that reach them}\\[2pt]
{\small Control board X2Q322\_K\_V4 (260703), controller with sticker ``X2Q311OW OTA V22'', LQFP64. View as in the photo: sticker readable, module site U10 on the right.
Pin keys: u = top edge, d = bottom edge (numbered from the left), l = left edge, p = right edge (numbered from the bottom). Grey: standard pin number and function in the STM32F103 / GD32F103 / GD32F303 family.
\mbox{AMPERE POINT}, 28 September 2026, EN v1 (from PL v2 of 25 September 2026): ground measured.}};
\draw[fill=black!85, rounded corners=2pt] (""" + f"{X0},{Y0}) rectangle ({X1},{Y1}" + r""");
\fill[white] (""" + f"{X0+0.45},{Y0+0.45}" + r""") circle (0.13);
\node[white, font=\scriptsize, anchor=west] at (""" + f"{X0+0.65},{Y0+0.45}" + r""") {pin 1 = d1};
\node[fill=white, text width=3.4cm, align=center, font=\small] at (""" + f"{(X0+X1)/2},{(Y0+Y1)/2+0.6}" + r""") {X2Q311OW\\OTA\\V22};
\node[white, align=center, font=\scriptsize] at (""" + f"{(X0+X1)/2},{(Y0+Y1)/2-1.4}" + r""") {U2 · LQFP64\\STM32F103 / GD32F303 family\\identified by the power-pin pattern};
""" + pin_nodes() + r"""
\node[anchor=north west, draw=black!50, rounded corners=3pt, fill=white, text width=4.6cm, font=\scriptsize, inner sep=5pt] at (23.0,13.4) {%
\textbf{Module site U10, pads}\\[3pt]
{\color{txblue}\textbf{16 TXD}} \ra\ p1 = PA3, controller receives\\
{\color{rxgreen}\textbf{15 RXD}} \la\ d16 = PA2, controller transmits\\
{\color{pwrred}\textbf{8 VCC}} \ra\ d1, d13, p3, p16, u1, l1\\
\textbf{9 GND} \ra\ d12, p2, p15, u2, l2\\[3pt]
No continuity to the controller:\\ 1 NC, 2 A\_7, 3 EN, 4 A\_11, 5 A\_2, 6 A\_3, 7 A\_4,\\ 10 A\_12, 11 A\_16, 12 A\_17, 13 A\_18, 14 A\_19};
\node[anchor=north west, draw=black!40, rounded corners=3pt, fill=white, text width=4.6cm, font=\scriptsize, inner sep=5pt] at (23.0,7.6) {%
\textbf{Conversion to the standard pin number}\\[2pt]
dN \ra\ N\qquad pN \ra\ 16+N\\
uN \ra\ 49$-$N\qquad lN \ra\ 65$-$N\\[4pt]
\textbf{Legend}\\[2pt]
{\color{pwrred}\rule{1.4ex}{1.4ex}} 3.3 V supply from pad VCC\\
{\color{txblue}\rule{1.4ex}{1.4ex}} controller receive, from pad TXD\\
{\color{rxgreen}\rule{1.4ex}{1.4ex}} controller transmit, to pad RXD\\
{\color{black}\rule{1.4ex}{1.4ex}} ground from pad GND\\
{\color{black!55}\rule{1.4ex}{1.4ex}} pin with no connection to the module site};
\end{tikzpicture}

\newpage
{\Large\bfseries Connections between the module site and the controller}\\[4pt]
\small
\renewcommand{\arraystretch}{1.3}
\begin{tabular}{@{}l l r l l@{}}
\toprule
\rowcolor{black!8}\textbf{Module pad} & \textbf{Pin (u/d/l/p)} & \textbf{Standard no.} & \textbf{Function in the controller} & \textbf{Status} \\
\midrule
""" + rows_tex + r"""
\bottomrule
\end{tabular}

\vspace{10pt}
\textbf{Findings}\\[3pt]
1. \textbf{Controller family.} The six supply pins fall exactly on positions 1, 13, 19, 32, 48 and 64, which is the supply pattern of the STM32F103 and its GD32F103 / GD32F303 equivalents in LQFP64. The module port lands on PA2 and PA3, the USART pins of that family. All five ground pins fall on the positions given by the datasheet: 12, 18, 31, 47 and 63. These three independent matches confirm both the family and the location of pin 1 in the bottom-left corner. The exact part number is under the sticker.\\[2pt]
2. \textbf{Directions.} Pad TXD (module transmit) reaches the controller receive pin PA3. Pad RXD reaches the controller transmit pin PA2. The DevKit is wired accordingly: pin 4 (TX) to pad TXD, pin 5 (RX) to pad RXD.\\[2pt]
3. \textbf{Nothing but the port.} Pads A\_x, EN and NC have no continuity to the controller. The module has no reset line and no auxiliary signals from the controller.\\[2pt]
4. \textbf{Ground} from pad GND reaches d12, p2, p15, u2 and l2, as in the datasheet. By the datasheet the 8 MHz crystal should be on d5 and d6 and the controller reset on d7.\\[2pt]
5. \textbf{Programming connector of the controller,} if ever needed: SWDIO on u3, SWCLK on l16, BOOT0 on l5, reset on d7.
\end{document}
"""
open(OUT, "w", encoding="utf-8").write(TEX)
print("written", OUT)
