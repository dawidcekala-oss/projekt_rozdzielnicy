# -*- coding: utf-8 -*-
"""Wykresy do raportu o opóźnieniu wznowienia (czyta wyniki.json, liczy jedną przykładową noc)."""
import json, os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sym_opoznienie as m, sys
DEC = int(sys.argv[1]) if len(sys.argv) > 1 else 5

here = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(here, 'wyniki.json'), encoding='utf-8'))
TL = r['T_list']; H = r['houses']; W = sum(h['weight'] for h in H.values())
Tm = np.array(TL) / 60

def wavg(key):
    return np.array([sum(h['weight'] * h['T'][str(T)][key] for h in H.values()) / W for T in TL])

plt.rcParams.update({'font.family': 'Arial', 'font.size': 9})
C1, C2, C3 = '#B45309', '#1F2937', '#0369A1'

# --- rys. 1: krzywe ważone ------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(8.6, 3.3))
a = ax[0]
a.plot(Tm, wavg('cycles_mean'), 'o-', color=C2, label='cykle na noc (średnia)')
a.plot(Tm, wavg('maxh_p90'), 's-', color=C1, label='cykle w najgorszej godzinie (90 % nocy poniżej)')
a.plot(Tm, wavg('empty_mean'), '^-', color=C3, label='cykle puste, < 60 s ładowania')
a.axvspan(3, 5, color='#FEF3C7', zorder=0); a.axvline(DEC, color=C1, lw=0.8, ls='--')
a.set_xlabel('opóźnienie T [min]'); a.set_ylabel('liczba cykli start/stop'); a.set_xlim(0, 15.5); a.set_ylim(0)
a.legend(fontsize=7.5, loc='upper right'); a.grid(alpha=0.3)
a.set_title('Domy — średnia ważona 7 typów', fontsize=9.5)
b = ax[1]
b.plot(Tm, wavg('fin_delay_mean'), 'o-', color=C2, label='późniejsze zakończenie ładowania')
b.plot(Tm, wavg('pause_max_mean'), 's-', color=C1, label='najdłuższa pauza w nocy')
b.axvspan(3, 5, color='#FEF3C7', zorder=0); b.axvline(DEC, color=C1, lw=0.8, ls='--')
b.set_xlabel('opóźnienie T [min]'); b.set_ylabel('minuty'); b.set_xlim(0, 15.5); b.set_ylim(0)
b.legend(fontsize=7.5, loc='upper left'); b.grid(alpha=0.3)
b.set_title('Koszt opóźnienia', fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(here, 'rys1_krzywe.png'), dpi=200); plt.close(fig)

# --- rys. 2: przykładowa noc, dom 3x16 A ------------------------------------------------------
S = 14 * 3600
best = None
for seed in range(1, 60):
    rng = np.random.default_rng(seed)
    pr = m.Profile(rng, S, 3)
    m.house_loads(pr, dict(hob=0.0, oven=1.0, boiler=0.2, well_pump=0.2, kettle_evening=3))
    alloc = m.alloc_from_profile(pr, 16)
    tp = int(rng.uniform(m.hm(17, 30), m.hm(18, 30)))
    c0, E0, f0 = m.simulate_single(alloc, 0, tp, 40.0, 3, S)
    if 12 <= len(c0) <= 30:
        best = (pr, alloc, tp); break
pr, alloc, tp = best
t0, t1 = m.hm(17, 30), m.hm(22, 30)
tt = (np.arange(t0, t1) / 3600 + 17)
fig, ax = plt.subplots(4, 1, figsize=(8.6, 5.2), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1, 1, 1]))
a = ax[0]
a.plot(tt, pr.maxphase()[t0:t1], color=C2, lw=0.8, label='reszta domu, faza najbardziej obciążona [A]')
a.plot(tt, np.clip(alloc[t0:t1], 0, 16), color=C3, lw=0.8, label='przydział dla wallboxa [A]')
a.axhline(6, color=C1, lw=0.8, ls='--'); a.text(t1 / 3600 + 17 - 0.02, 6.3, 'próg 6 A', color=C1, ha='right', fontsize=7.5)
a.set_ylabel('A'); a.legend(fontsize=7.5, loc='upper right', ncol=2); a.grid(alpha=0.3)
a.set_title('Przykładowa noc: dom 3×16 A, piekarnik (termostat) + czajniki, wallbox 11 kW', fontsize=9.5)
for k, T in enumerate([60, DEC * 60, 600]):
    cyc, E, fin = m.simulate_single(alloc, T, tp, 40.0, 3, S)
    a = ax[k + 1]
    n = 0
    for s, e in cyc:
        if e < t0 or s > t1:
            continue
        a.axvspan(max(s, t0) / 3600 + 17, min(e, t1) / 3600 + 17, color='#15803D', alpha=0.55)
        n += 1
    a.set_yticks([]); a.set_ylabel(f'T = {T // 60} min', rotation=0, ha='right', va='center', fontsize=8.5)
    a.text(17.55, 0.5, f'{n} startów w tym oknie', fontsize=7.5, va='center')
    a.grid(alpha=0.3, axis='x')
ax[-1].set_xlabel('godzina'); ax[-1].set_xlim(17.5, 22.5)
fig.tight_layout(); fig.savefig(os.path.join(here, 'rys2_noc.png'), dpi=200); plt.close(fig)
print('wykresy zapisane')
