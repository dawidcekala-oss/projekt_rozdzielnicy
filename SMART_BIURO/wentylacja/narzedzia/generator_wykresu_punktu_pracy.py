# -*- coding: utf-8 -*-
"""Wizualizacja punktu pracy: prosta rezystora vs hiperbole stalej mocy przetwornicy."""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\schematy\wykres_punkt_pracy.png"

U = 12.0
fig, axes = plt.subplots(1, 2, figsize=(16, 8.2), dpi=200, sharey=True)
fig.suptitle("Punkt pracy filtra: prosta rezystora vs hiperbola sta\u0142ej mocy przetwornicy",
             fontsize=15, fontweight="bold", y=0.98)

C_LINIA = "#15803D"; C_LINIA2 = "#B00020"
C_P055 = "#0369A1"; C_P090 = "#B45309"; C_P165 = "#9467BD"; C_GRAN = "#666666"


def punkt(R, P):
    d = U*U - 4*P*R
    if d < 0:
        return None
    V = (U + np.sqrt(d)) / 2
    return (U - V) / R, V  # (I, V)


def punkt_niestabilny(R, P):
    d = U*U - 4*P*R
    if d < 0:
        return None
    V = (U - np.sqrt(d)) / 2
    return (U - V) / R, V


I = np.linspace(0.005, 0.52, 600)

for ax, R, tytul, kolor in [
    (axes[0], 25.0, "R = 25 \u03a9 (wersja 2 \u2014 dzia\u0142a)", C_LINIA),
    (axes[1], 47.0, "R = 47 \u03a9 (wersja 1 \u2014 awaria)", C_LINIA2),
]:
    # prosta rezystora: V = U - I*R
    Ilin = np.linspace(0, U/R, 200)
    ax.plot(Ilin*1000, U - Ilin*R, color=kolor, lw=3,
            label=f"prosta rezystora: V = 12 \u2212 I\u00b7{R:.0f}")
    # hiperbole stalej mocy
    for P, c, nazwa in [(0.55, C_P055, "P = 0,55 W (praca normalna)"),
                        (0.90, C_P090, "P = 0,90 W (start WiFi)"),
                        (1.65, C_P165, "P = 1,65 W (impuls nadawania)")]:
        ax.plot(I*1000, np.clip(P/I, 0, 13.5), color=c, lw=2, alpha=0.9, label=nazwa)
    # granica U^2/4R
    Pmax = U*U/(4*R)
    ax.plot(I*1000, np.clip(Pmax/I, 0, 13.5), color=C_GRAN, lw=1.6, ls=":",
            label=f"granica U\u00b2/4R = {Pmax:.2f} W (styczna)")
    # punkt stycznosci granicy
    ax.plot([U/(2*R)*1000], [U/2], marker="s", ms=8, color=C_GRAN, zorder=6)

    # punkty pracy
    for P, c in [(0.55, C_P055), (0.90, C_P090)]:
        pt = punkt(R, P)
        if pt:
            ax.plot([pt[0]*1000], [pt[1]], "o", ms=11, color=c, mec="white", mew=1.5, zorder=7)
            ax.annotate(f"{pt[1]:.1f} V / {pt[0]*1000:.0f} mA",
                        (pt[0]*1000, pt[1]), textcoords="offset points", xytext=(12, 10),
                        fontsize=10, fontweight="bold", color=c)
        else:
            # brak przeciecia -> zapasc
            ax.annotate("BRAK PRZECI\u0118CIA\nz prost\u0105 47 \u03a9 \u2192 zapa\u015b\u0107:\nprzetwornica \u015bci\u0105ga w\u0119ze\u0142,\nrezystor grzeje si\u0119 w k\u00f3\u0142ko",
                        xy=(128, 6.0), xytext=(190, 8.6), fontsize=10, fontweight="bold",
                        color=C_P090,
                        arrowprops=dict(arrowstyle="-|>", color=C_P090, lw=2))
    # punkt niestabilny dla 0,55 W (edukacyjnie, tylko raz)
    if R == 25:
        pn = punkt_niestabilny(R, 0.55)
        ax.plot([pn[0]*1000], [pn[1]], "o", ms=10, mfc="white", mec=C_P055, mew=2, zorder=7)
        ax.annotate("drugie przeci\u0119cie \u2014 punkt NIESTABILNY\n(uk\u0142ad z niego ucieka, nieosi\u0105gany)",
                    (pn[0]*1000, pn[1]), textcoords="offset points", xytext=(-8, 26),
                    fontsize=8.6, color=C_P055, ha="right")

    # minimalne napiecie przetwornicy
    ax.axhline(6.5, color="#999999", lw=1.4, ls="--")
    ax.text(505, 6.7, "minimum przetwornicy 6,5 V", fontsize=8.6, color="#666", ha="right")

    ax.set_title(tytul, fontsize=12.5, fontweight="bold",
                 color=(C_LINIA if R == 25 else C_LINIA2))
    ax.set_xlabel("pr\u0105d pobierany z w\u0119z\u0142a I [mA]", fontsize=11)
    ax.set_xlim(0, 520); ax.set_ylim(0, 13.5)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.6, framealpha=0.95)

axes[0].set_ylabel("napi\u0119cie w\u0119z\u0142a V [V]", fontsize=11)

fig.text(0.5, 0.015,
         "Jak czyta\u0107: uk\u0142ad ustala si\u0119 tam, gdzie prosta rezystora przecina hiperbol\u0119 mocy (pe\u0142ne k\u00f3\u0142ka \u2014 punkty stabilne). "
         "Hiperbola impulsu nadawania (fioletowa) le\u017cy ponad granic\u0105 obu rezystor\u00f3w \u2014 impulsy pokrywa kondensator, nie rezystor. "
         "Kwadrat = punkt styczno\u015bci granicy U\u00b2/4R.",
         ha="center", fontsize=9.6, color="#333")

plt.tight_layout(rect=[0, 0.045, 1, 0.94])
plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print("OK:", OUT)
