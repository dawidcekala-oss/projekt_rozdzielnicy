"""Generuje schemat procesora Q11 (plytka X2Q322_K_V4) w numeracji uzytkownika u/d/l/p
z polami miejsca na modul przy kazdej nozce. AMPERE POINT, 2026-09-25.
Wynik: schemat_procesora_Q11_V4_v1.tex (kompilacja xelatex)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "schemat_procesora_Q11_V4_v1.tex")

# Standardowy uklad nozek LQFP64, rodzina STM32F103 / GD32F103 / GD32F303
NAMES = {1: "VBAT", 2: "PC13", 3: "PC14", 4: "PC15", 5: "PD0 OSC\\_IN", 6: "PD1 OSC\\_OUT", 7: "NRST",
         8: "PC0", 9: "PC1", 10: "PC2", 11: "PC3", 12: "VSSA", 13: "VDDA", 14: "PA0", 15: "PA1",
         16: "PA2 USART TX", 17: "PA3 USART RX", 18: "VSS", 19: "VDD", 20: "PA4", 21: "PA5", 22: "PA6",
         23: "PA7", 24: "PC4", 25: "PC5", 26: "PB0", 27: "PB1", 28: "PB2 BOOT1", 29: "PB10", 30: "PB11",
         31: "VSS", 32: "VDD", 33: "PB12", 34: "PB13", 35: "PB14", 36: "PB15", 37: "PC6", 38: "PC7",
         39: "PC8", 40: "PC9", 41: "PA8", 42: "PA9", 43: "PA10", 44: "PA11", 45: "PA12",
         46: "PA13 SWDIO", 47: "VSS", 48: "VDD", 49: "PA14 SWCLK", 50: "PA15", 51: "PC10", 52: "PC11",
         53: "PC12", 54: "PD2", 55: "PB3", 56: "PB4", 57: "PB5", 58: "PB6", 59: "PB7", 60: "BOOT0",
         61: "PB8", 62: "PB9", 63: "VSS", 64: "VDD"}

# Pomiar uzytkownika: nozka -> pole modulu
MEASURED = {"d13": "8 VCC", "p16": "8 VCC", "u1": "8 VCC", "d1": "8 VCC", "l1": "8 VCC", "p3": "8 VCC",
            "p1": "16 TXD", "d16": "15 RXD",
            "d12": "9 GND", "p2": "9 GND", "p15": "9 GND", "u2": "9 GND", "l2": "9 GND"}
PREDICTED = {}
COLOR = {"8 VCC": "pwrred", "16 TXD": "txblue", "15 RXD": "rxgreen", "9 GND": "black"}


def std(side, n):
    return {"d": n, "p": 16 + n, "u": 49 - n, "l": 65 - n}[side]


X0, Y0, X1, Y1 = 9.0, 4.2, 18.0, 13.2       # obrys ukladu
PITCH = 0.5
FIRST = 0.75                                  # odstep pierwszej nozki od rogu


def pin_nodes():
    out = []
    for side in "dupl":
        for n in range(1, 17):
            s = std(side, n)
            name = NAMES[s]
            key = f"{side}{n}"
            pad = MEASURED.get(key) or PREDICTED.get(key)
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
    TABLE_ROWS.append((pad, key, s, NAMES[s].replace("\\_", "\\_"), "zmierzone"))
for key, pad in PREDICTED.items():
    side, n = key[0], int(key[1:])
    s = std(side, n)
    TABLE_ROWS.append((pad.replace("?", ""), key, s, NAMES[s], "przewidywane, do sprawdzenia"))
order = {"16 TXD": 0, "15 RXD": 1, "8 VCC": 2, "9 GND": 3}
TABLE_ROWS.sort(key=lambda r: (order.get(r[0], 9), r[2]))
rows_tex = "\n".join(rf"{p} & {k} & {s} & {nm} & {st} \\" for p, k, s, nm, st in TABLE_ROWS)

TEX = r"""% !TEX program = xelatex
\documentclass[10pt]{article}
\usepackage{fontspec}
\setmainfont{Calibri}
\newfontfamily\sym{Segoe UI Symbol}
\usepackage{polyglossia}\setdefaultlanguage{polish}
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
{\Large\bfseries Procesor Q11: nóżki w numeracji u/d/l/p i pola miejsca na moduł}\\[2pt]
{\small Płytka X2Q322\_K\_V4 (260703), procesor z naklejką „X2Q311OW OTA V22”, LQFP64. Widok jak na zdjęciu: naklejka czytelna, miejsce na moduł po prawej.
Numeracja użytkownika: u i d od lewej, l i p od dołu. Szarym: numer standardowy i funkcja w rodzinie STM32F103 / GD32F103 / GD32F303.
\mbox{AMPERE POINT}, 25.09.2026, v2: masa z pomiaru.}};
% obrys ukladu
\draw[fill=black!85, rounded corners=2pt] (""" + f"{X0},{Y0}) rectangle ({X1},{Y1}" + r""");
\fill[white] (""" + f"{X0+0.45},{Y0+0.45}" + r""") circle (0.13);
\node[white, font=\scriptsize, anchor=west] at (""" + f"{X0+0.65},{Y0+0.45}" + r""") {nóżka 1 = d1};
\node[fill=white, text width=3.4cm, align=center, font=\small] at (""" + f"{(X0+X1)/2},{(Y0+Y1)/2+0.6}" + r""") {X2Q311OW\\OTA\\V22};
\node[white, align=center, font=\scriptsize] at (""" + f"{(X0+X1)/2},{(Y0+Y1)/2-1.4}" + r""") {U2 · LQFP64\\rodzina STM32F103 / GD32F303\\rozpoznana po nóżkach zasilania};
""" + pin_nodes() + r"""
% miejsce na modul (schematycznie, po prawej)
\node[anchor=north west, draw=black!50, rounded corners=3pt, fill=white, text width=4.6cm, font=\scriptsize, inner sep=5pt] at (23.0,13.4) {%
\textbf{Miejsce na moduł, pola}\\[3pt]
{\color{txblue}\textbf{16 TXD}} \ra\ p1 = PA3, odbiór procesora\\
{\color{rxgreen}\textbf{15 RXD}} \la\ d16 = PA2, nadawanie procesora\\
{\color{pwrred}\textbf{8 VCC}} \ra\ d1, d13, p3, p16, u1, l1\\
\textbf{9 GND} \ra\ d12, p2, p15, u2, l2\\[3pt]
Bez połączenia z procesorem:\\ 1 NC, 2 A\_7, 3 EN, 4 A\_11, 5 A\_2, 6 A\_3, 7 A\_4,\\ 10 A\_12, 11 A\_16, 12 A\_17, 13 A\_18, 14 A\_19};
\node[anchor=north west, draw=black!40, rounded corners=3pt, fill=white, text width=4.6cm, font=\scriptsize, inner sep=5pt] at (23.0,7.6) {%
\textbf{Przeliczenie na numer standardowy}\\[2pt]
dN \ra\ N\qquad pN \ra\ 16+N\\
uN \ra\ 49$-$N\qquad lN \ra\ 65$-$N\\[4pt]
\textbf{Legenda}\\[2pt]
{\color{pwrred}\rule{1.4ex}{1.4ex}} zasilanie 3,3 V z pola VCC\\
{\color{txblue}\rule{1.4ex}{1.4ex}} odbiór procesora z pola TXD\\
{\color{rxgreen}\rule{1.4ex}{1.4ex}} nadawanie procesora do pola RXD\\
{\color{black}\rule{1.4ex}{1.4ex}} masa z pola GND\\
{\color{black!55}\rule{1.4ex}{1.4ex}} nóżka bez połączenia z miejscem na moduł};
\end{tikzpicture}

\newpage
{\Large\bfseries Połączenia miejsca na moduł z procesorem}\\[4pt]
\small
\renewcommand{\arraystretch}{1.3}
\begin{tabular}{@{}l l r l l@{}}
\toprule
\rowcolor{black!8}\textbf{Pole modułu} & \textbf{Nóżka (u/d/l/p)} & \textbf{Nr standardowy} & \textbf{Funkcja w procesorze} & \textbf{Status} \\
\midrule
""" + rows_tex + r"""
\bottomrule
\end{tabular}

\vspace{10pt}
\textbf{Wnioski}\\[3pt]
1. \textbf{Rozpoznanie procesora.} Sześć nóżek zasilania wypada dokładnie na pozycjach 1, 13, 19, 32, 48 i 64, a to układ zasilania procesorów STM32F103 i ich zamienników GD32F103 i GD32F303 w obudowie LQFP64. Port modułu trafił na PA2 i PA3, czyli na nóżki portu szeregowego tej rodziny. Wszystkie pięć nóżek masy trafiło w miejsca przewidziane przez kartę katalogową: 12, 18, 31, 47 i 63. Te trzy niezależne trafienia potwierdzają i rodzinę, i położenie nóżki 1 w lewym dolnym rogu.\\[2pt]
2. \textbf{Kierunki.} Pole TXD, czyli nadawanie modułu, trafia na odbiór procesora PA3. Pole RXD trafia na nadawanie procesora PA2. DevKit jest podłączony zgodnie z tym: nóżka 4 do pola TXD, nóżka 5 do pola RXD.\\[2pt]
3. \textbf{Nic poza portem.} Pola A\_x, EN i NC nie łączą się z procesorem. Moduł nie ma żadnej linii resetu ani sygnałów pomocniczych od procesora.\\[2pt]
4. \textbf{Masa} z pola GND idzie na d12, p2, p15, u2 i l2, zgodnie z kartą katalogową. Według karty kwarc 8 MHz powinien wisieć na d5 i d6, a reset procesora na d7.\\[2pt]
5. \textbf{Złącze programowania procesora,} jeśli kiedyś będzie potrzebne: SWDIO na u3, SWCLK na l16, BOOT0 na l5, reset na d7.
\end{document}
"""
open(OUT, "w", encoding="utf-8").write(TEX)
print("zapisano", OUT)
