# -*- coding: utf-8 -*-
"""
Obwod Control Pilot (IEC 61851) - weryfikacja poziomow napiec i przebieg PWM.
Model obwodu:  Vpilot --[R1]-- (wezel CP) --[dioda]--[Rev]-- masa(PE)
  R1   = 1 kOhm  (rezystor szeregowy po stronie ladowarki)
  Rev  = 2,74 kOhm        -> stan B
  Rev  = 2,74k || 1,3k    -> stan C (auto dolacza R3=1,3k rownolegle)
Napiecie na CP mierzymy na wezle miedzy R1 a dioda (tak jak ladowarka).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- parametry ---
V    = 12.0     # napiecie pilota [V]
R1   = 1000.0   # rezystor szeregowy ladowarki [Ohm]
R2   = 2740.0   # rezystor auta, stan B [Ohm]
R3   = 1300.0   # dodatkowy rezystor, stan C (rownolegle) [Ohm]
Vd   = 0.7      # spadek na diodzie [V]
f    = 1000.0   # czestotliwosc PWM [Hz]
duty = 0.50     # wypelnienie (50% dla czytelnosci; w realu koduje prad)

def plateau(Rev):
    # dodatnia polowka: dioda przewodzi, I=(V-Vd)/(R1+Rev), V_cp = V - I*R1
    return (V*Rev + Vd*R1) / (R1 + Rev)

Rb = R2
Rc = R2*R3/(R2+R3)
Vb, Vc = plateau(Rb), plateau(Rc)

print("================ WERYFIKACJA POZIOMOW CP ================")
print(f"Stan A (brak auta)         : +{V:5.2f} V  (stale, bez PWM)")
print(f"Stan B (Rev = {Rb:6.0f} Ohm) : +{Vb:5.2f} V  (cel ~9 V)")
print(f"Stan C (Rev = {Rc:6.0f} Ohm) : +{Vc:5.2f} V  (cel ~6 V)")
print(f"Dolny poziom PWM           : -{V:5.2f} V  (dioda blokuje)")
print("--------------------------------------------------------")
print("Kodowanie pradu:  I [A] = wypelnienie[%] * 0,6")
for d,l in [(10,'10%'),(26.7,'16 A'),(50,'50%'),(53.3,'32 A')]:
    print(f"   wypelnienie {l:>5}  ->  I = {0.6*d:5.1f} A")
print("========================================================")

# --- przebieg czasowy: A -> B -> C ---
fs = 200000.0
t  = np.arange(0, 9e-3, 1/fs)
phase = (t % (1/f)) / (1/f)
high  = phase < duty
cp = np.where(t < 3e-3, V,
      np.where(t < 6e-3, np.where(high, Vb, -V),
                          np.where(high, Vc, -V)))

fig, ax = plt.subplots(figsize=(9.2, 4.3))
ax.plot(t*1000, cp, color="#13284f", lw=1.3)
for lvl, txt, c in [(12, "+12 V (A)", "#777777"),
                    (Vb, f"+{Vb:.1f} V (B)", "#1f77b4"),
                    (Vc, f"+{Vc:.1f} V (C)", "#2ca02c"),
                    (-12, "-12 V", "#777777")]:
    ax.axhline(lvl, ls="--", lw=0.8, color=c, alpha=0.8)
    ax.text(9.1, lvl, txt, va="center", fontsize=8.5, color=c)
ax.axvline(3, ls=":", color="gray"); ax.axvline(6, ls=":", color="gray")
ax.text(1.5, 14.0, "Stan A\n(spoczynek)", ha="center", fontsize=8.5)
ax.text(4.5, 14.0, "Stan B\n(podłączone)", ha="center", fontsize=8.5)
ax.text(7.5, 14.0, "Stan C\n(ładowanie)", ha="center", fontsize=8.5)
ax.set_xlabel("czas [ms]"); ax.set_ylabel("napięcie CP [V]")
ax.set_title("Control Pilot (IEC 61851): handshake A → B → C, PWM 1 kHz")
ax.set_ylim(-15, 16); ax.set_xlim(0, 10.4); ax.grid(alpha=0.25)
plt.tight_layout()
plt.savefig("cp_waveform.png", dpi=130)
print("Zapisano wykres: cp_waveform.png")
