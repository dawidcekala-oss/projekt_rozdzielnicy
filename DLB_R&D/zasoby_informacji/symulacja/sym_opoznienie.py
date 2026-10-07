# -*- coding: utf-8 -*-
"""
Symulacja doboru stałego opóźnienia wznowienia ładowania po pauzie DLB.

Zasada (potwierdzona przez producenta 2026-09-28):
  - przydział dla wallboxa = floor(0,9 * limit DIP) - ceil(najbardziej obciążona faza reszty budynku)
  - przydział < 6 A  -> wallbox zatrzymuje ładowanie, od tej chwili biegnie opóźnienie T
  - po upływie T: jeśli przydział >= 6 A -> wznowienie natychmiast; jeśli nie -> wznowienie, gdy tylko
    przydział >= 6 A (bez dodatkowego czekania, bez histerezy, bez filtrowania)

Rozdzielczość 1 s. Wieczór + noc 17:00-07:00 (dom) albo dzień 07:00-17:00 (budynek, zakład).
Wszystkie moce, czasy i prawdopodobieństwa odbiorników to ZAŁOŻENIA (typowe wartości katalogowe),
nie pomiary — zapisane w tabeli ODBIORNIKI poniżej, żeby dało się je podważyć i zmienić.
"""
import numpy as np, json, sys, os

V = 230.0
WB_MAX = 16          # A na fazę, wallbox 11 kW
PAUSE_A = 6          # próg pauzy / wznowienia [A]
START_DELAY = 8      # s od wznowienia do pojawienia się prądu (handshake CP)
RAMP = 30            # s narastania prądu auta do pełnej wartości (log: auto trójfazowe ok. 30 s)
T_LIST = [30, 60, 90, 120, 180, 240, 300, 420, 600, 900]   # badane opóźnienia [s]


def hm(hh, mm=0, t0=17):
    """sekundy od początku okna (t0 = godzina początku okna)."""
    return int(((hh - t0) % 24) * 3600 + mm * 60)


class Profile:
    """Prądy na trzech fazach [A] w kolejnych sekundach okna."""
    def __init__(self, rng, S, nph):
        self.rng, self.S, self.nph = rng, S, nph
        self.P = np.zeros((3, S))

    def add(self, ph, start, dur, amps):
        start, dur = int(start), int(dur)
        if dur <= 0 or start >= self.S:
            return
        a = max(0, start); b = min(self.S, start + dur)
        if b > a:
            self.P[ph, a:b] += amps

    def add3(self, start, dur, amps):
        for ph in range(self.nph):
            self.add(ph, start, dur, amps)

    def cyc(self, ph, start, total, on, off, amps, jitter=0.25, three=False):
        """praca termostatyczna: on/off z losowym rozrzutem."""
        t = start; end = start + total; r = self.rng
        while t < end:
            d_on = on * (1 + jitter * (2 * r.random() - 1))
            d_off = off * (1 + jitter * (2 * r.random() - 1))
            if three:
                self.add3(t, d_on, amps)
            else:
                self.add(ph, t, d_on, amps)
            t += d_on + d_off

    def maxphase(self):
        return self.P[:self.nph].max(axis=0)


# ----------------------------------------------------------------------------------------------
# ODBIORNIKI DOMOWE  (prąd [A] przy 230 V; czasy w sekundach)
# ----------------------------------------------------------------------------------------------
def house_loads(pr, cfg):
    r = pr.rng; nph = pr.nph
    S = pr.S
    ph_k = 0 if nph == 1 else int(r.integers(0, 3))          # faza gniazd kuchennych
    rp = (lambda: 0) if nph == 1 else (lambda: int(r.integers(0, 3)))

    # tło: oświetlenie, elektronika (wieczór), lodówka
    pr.add(ph_k, hm(17), hm(23) - hm(17), 2.5)
    for ph in range(nph):
        pr.add(ph, 0, S, 0.6)
    pr.add(ph_k, hm(6), hm(7) - hm(6), 1.5)
    pr.cyc(ph_k, 0, S, 12 * 60, 28 * 60, 1.0)                 # lodówka

    # czajnik 2,2 kW = 9,6 A
    n_ev = r.poisson(cfg.get('kettle_evening', 2.2))
    for _ in range(n_ev):
        t = hm(17) + r.beta(2, 2.5) * (hm(22, 30) - hm(17))
        pr.add(ph_k, t, r.uniform(90, 240), 9.6)
    for _ in range(r.poisson(cfg.get('kettle_morning', 1.0))):
        pr.add(ph_k, r.uniform(hm(6), hm(7) - 200), r.uniform(90, 240), 9.6)

    # mikrofalówka 1,5 kW = 6,5 A
    for _ in range(r.poisson(cfg.get('microwave', 0.8))):
        pr.add(ph_k, r.uniform(hm(17), hm(22)), r.uniform(60, 300), 6.5)

    # ekspres 1,4 kW = 6 A, impulsy 45 s
    if r.random() < cfg.get('coffee', 0.6):
        t = r.uniform(hm(6), hm(6, 50))
        pr.add(ph_k, t, 45, 6.0); pr.add(ph_k, t + 120, 45, 6.0)
    if r.random() < 0.4:
        pr.add(ph_k, r.uniform(hm(17), hm(21)), 45, 6.0)

    # piekarnik 2,5 kW = 11 A: rozgrzewanie 9 min ciągiem, potem termostat 80 s / 160 s
    if r.random() < cfg.get('oven', 0.5):
        ph = rp(); t = r.uniform(hm(17), hm(19, 30)); tot = r.uniform(40, 70) * 60
        pr.add(ph, t, 9 * 60, 11.0)
        pr.cyc(ph, t + 9 * 60, tot - 9 * 60, 80, 160, 11.0)

    # płyta indukcyjna: pole 1 (2 kW = 8,7 A) i pole 2 (1,5 kW = 6,5 A); po zagotowaniu
    # podtrzymywanie impulsami (8 s / 12 s) — typowe dla indukcji na małej mocy
    if r.random() < cfg.get('hob', 0.7):
        pa = rp(); pb = rp() if nph == 3 else 0
        t = r.uniform(hm(17), hm(19, 30))
        pr.add(pa, t, r.uniform(5, 8) * 60, 8.7)
        pr.cyc(pa, t + 7 * 60, r.uniform(10, 25) * 60, 8, 12, 8.7, jitter=0.1)
        t2 = t + r.uniform(2, 5) * 60
        pr.add(pb, t2, r.uniform(3, 5) * 60, 6.5)
        pr.cyc(pb, t2 + 4 * 60, r.uniform(8, 15) * 60, 6, 14, 6.5, jitter=0.1)

    # zmywarka 2 kW = 8,7 A: grzanie 12 min i 18 min w cyklu
    if r.random() < cfg.get('dishwasher', 0.6):
        ph = rp(); t = r.uniform(hm(19, 30), hm(22, 30))
        pr.add(ph, t + 8 * 60, 12 * 60, 8.7); pr.add(ph, t + 65 * 60, 18 * 60, 8.7)

    # pralka 2 kW = 8,7 A: grzanie 15 min na początku
    if r.random() < cfg.get('washer', 0.35):
        ph = rp(); t = r.uniform(hm(18), hm(22))
        pr.add(ph, t + 5 * 60, 15 * 60, 8.7)
    if r.random() < cfg.get('washer_night', 0.15):
        ph = rp(); t = r.uniform(hm(1), hm(4))
        pr.add(ph, t + 5 * 60, 15 * 60, 8.7)

    # suszarka 2,5 kW = 11 A: 15 min ciągiem, potem termostat 150 s / 90 s przez ~70 min
    if r.random() < cfg.get('dryer', 0.25):
        ph = rp(); t = r.uniform(hm(19), hm(22))
        pr.add(ph, t, 15 * 60, 11.0)
        pr.cyc(ph, t + 15 * 60, 70 * 60, 150, 90, 11.0)

    # suszarka do włosów 2 kW = 8,7 A
    if r.random() < cfg.get('hairdryer', 0.5):
        pr.add(rp(), r.uniform(hm(20, 30), hm(23)), r.uniform(4, 8) * 60, 8.7)
    if r.random() < 0.3:
        pr.add(rp(), r.uniform(hm(6, 20), hm(6, 55)), r.uniform(3, 6) * 60, 8.7)

    # odkurzacz 1,6 kW = 7 A
    if r.random() < cfg.get('vacuum', 0.15):
        pr.add(rp(), r.uniform(hm(17, 30), hm(20)), 15 * 60, 7.0)

    # żelazko 2,2 kW = 9,6 A: 20 s / 60 s
    if r.random() < cfg.get('iron', 0.15):
        pr.cyc(rp(), r.uniform(hm(19), hm(22)), 30 * 60, 20, 60, 9.6)

    # bojler 2 kW = 8,7 A: taryfa nocna, 2,5 h ciągiem od 22:00
    if r.random() < cfg.get('boiler', 0.0):
        pr.add(rp(), hm(22) + r.uniform(0, 30 * 60), 2.5 * 3600, 8.7)

    # przepływowy podgrzewacz 21 kW 3-f = 30 A/fazę: prysznice + mycie rąk
    if cfg.get('flow_heater', False):
        for _ in range(2):
            pr.add3(r.uniform(hm(20), hm(23)), r.uniform(6, 10) * 60, 30.0)
        for _ in range(r.integers(1, 3)):
            pr.add3(r.uniform(hm(6), hm(7) - 600), r.uniform(6, 10) * 60, 30.0)
        for _ in range(r.poisson(10)):
            pr.add3(r.uniform(hm(17), hm(23)), r.uniform(15, 60), 30.0)
        for _ in range(r.poisson(4)):
            pr.add3(r.uniform(hm(6), hm(7)), r.uniform(15, 60), 30.0)

    # pompa ciepła 3-f: sprężarka 6 A/fazę 20 min / 20 min; grzałka 9 A/fazę 6 min co ~75 min
    if cfg.get('heat_pump', False):
        pr.cyc(0, r.uniform(0, 20 * 60), S, 20 * 60, 20 * 60, 6.0, jitter=0.3, three=True)
        if r.random() < 0.5:
            t = r.uniform(0, 75 * 60)
            while t < S:
                pr.add3(t, 6 * 60, 9.0); t += r.uniform(60, 90) * 60

    # hydrofor 1,1 kW = 5 A, 40 s co 3-12 min przy poborze wody
    if r.random() < cfg.get('well_pump', 0.0):
        ph = rp()
        for (a, b) in [(hm(17), hm(23)), (hm(6), hm(7))]:
            t = a
            while t < b:
                pr.add(ph, t, 40, 5.0); t += r.uniform(3, 12) * 60


HOUSES = {
    # nazwa: (waga, limit DIP [A], liczba faz, opis, konfiguracja odbiorników)
    'A1 dom 3x25 A, kuchnia elektryczna':
        (0.30, 25, 3, 'indukcja + piekarnik, zmywarka, pralka; bojler nocny u 40 %',
         dict(boiler=0.4, well_pump=0.2)),
    'A2 dom 3x25 A + pompa ciepła':
        (0.15, 25, 3, 'jak A1 + pompa ciepła 3-f (sprężarka 6 A/fazę, grzałka 9 A/fazę) + bojler',
         dict(heat_pump=True, boiler=0.5, well_pump=0.3)),
    'A3 dom 3x16 A, starsza instalacja':
        (0.15, 16, 3, 'płyta gazowa, piekarnik elektryczny u 50 %, czajnik, zmywarka',
         dict(hob=0.0, oven=0.5, boiler=0.2, well_pump=0.2)),
    'A4 dom 3x20 A':
        (0.10, 20, 3, 'jak A1, mniejsze przyłącze', dict(boiler=0.3, well_pump=0.2)),
    'A5 dom 3x25 A + przepływowy podgrzewacz 21 kW':
        (0.10, 25, 3, 'jak A1, ciepła woda z podgrzewacza przepływowego (30 A/fazę)',
         dict(flow_heater=True, boiler=0.0, well_pump=0.2)),
    'A6 mieszkanie 1x25 A, wallbox 3,7 kW':
        (0.10, 25, 1, 'jedna faza: czajnik, indukcja 1-f, piekarnik u 40 %, zmywarka, pralka',
         dict(oven=0.4, hob=0.6, boiler=0.0)),
    'A7 dom 3x32 A':
        (0.10, 32, 3, 'jak A1, duże przyłącze', dict(boiler=0.4, well_pump=0.2)),
}


# ----------------------------------------------------------------------------------------------
# SILNIK — jeden wallbox (dom)
# ----------------------------------------------------------------------------------------------
def alloc_from_profile(pr, csl):
    usable = int(np.floor(0.9 * csl))
    return usable - np.ceil(pr.maxphase() - 1e-9).astype(int)


def simulate_single(alloc, T, t_plug, e_need, nph, S):
    """Zwraca: cykle (lista (t_start, t_stop)), energia [kWh], czas zakończenia albo None,
    energia przy 'idealnym' braku pauz nie tu."""
    ok = alloc >= PAUSE_A
    bad_idx = np.flatnonzero(~ok); good_idx = np.flatnonzero(ok)
    def next_bad(t):
        i = np.searchsorted(bad_idx, t); return bad_idx[i] if i < len(bad_idx) else S
    def next_good(t):
        i = np.searchsorted(good_idx, t); return good_idx[i] if i < len(good_idx) else S
    kwh_per_As = V * nph / 3.6e6          # kWh na (A * s)
    t = t_plug; E = 0.0; cycles = []; charging = False; pause_until = t_plug; t_fin = None
    while t < S:
        if not charging:
            tc = max(t, pause_until)
            tg = next_good(tc)
            if tg >= S:
                break
            t = tg; charging = True; t_start = t
            cycles.append([t, None])
        else:
            tb = next_bad(t)
            seg = np.minimum(alloc[t:tb], WB_MAX).astype(float)
            n = tb - t
            # narastanie prądu po starcie
            rel = np.arange(t - t_start, tb - t_start)
            f = np.clip((rel - START_DELAY) / RAMP, 0, 1)
            e_seg = np.cumsum(seg * f) * kwh_per_As
            if E + e_seg[-1] >= e_need:
                k = int(np.searchsorted(e_seg, e_need - E)); t_fin = t + k + 1
                E = e_need; cycles[-1][1] = t_fin
                return cycles, E, t_fin
            E += e_seg[-1]
            t = tb; charging = False; cycles[-1][1] = t; pause_until = t + T
    if cycles and cycles[-1][1] is None:
        cycles[-1][1] = S
    return cycles, E, t_fin


def run_houses(n_runs=120, seed=1):
    S = 14 * 3600
    results = {}
    for name, (w, csl, nph, desc, cfg) in HOUSES.items():
        rng = np.random.default_rng(seed)
        acc = {T: dict(cycles=[], maxh=[], empty=[], short=[], e_lost=[], unfinished=0, fin=[],
                       pause_max=[], pause_mean=[]) for T in T_LIST}
        n_pause_events = []
        for k in range(n_runs):
            pr = Profile(rng, S, nph)
            house_loads(pr, cfg)
            alloc = alloc_from_profile(pr, csl)
            t_plug = int(rng.uniform(hm(17, 30), hm(19, 30)))
            e_need = float(rng.uniform(15, 45)) if nph == 3 else float(rng.uniform(10, 25))
            # odniesienie: T = 0 (wznowienie natychmiast)
            c0, E0, f0 = simulate_single(alloc, 0, t_plug, e_need, nph, S)
            n_pause_events.append(len(c0) - 1)
            for T in T_LIST:
                cyc, E, fin = simulate_single(alloc, T, t_plug, e_need, nph, S)
                a = acc[T]
                a['cycles'].append(len(cyc))
                starts = np.array([c[0] for c in cyc])
                mh = 0
                for s0 in starts:
                    mh = max(mh, int(((starts >= s0) & (starts < s0 + 3600)).sum()))
                a['maxh'].append(mh)
                durs = np.array([c[1] - c[0] for c in cyc])
                a['empty'].append(int((durs < 60).sum()))
                a['short'].append(int((durs < 300).sum()))
                a['e_lost'].append(E0 - E)
                a['unfinished'] += int(fin is None and f0 is not None)
                if fin is not None and f0 is not None:
                    a['fin'].append((fin - f0) / 60)
                pauses = [cyc[i + 1][0] - cyc[i][1] for i in range(len(cyc) - 1)]
                if pauses:
                    a['pause_max'].append(max(pauses) / 60); a['pause_mean'].append(np.mean(pauses) / 60)
        summ = {}
        for T in T_LIST:
            a = acc[T]
            summ[T] = dict(
                cycles_mean=float(np.mean(a['cycles'])), cycles_p90=float(np.percentile(a['cycles'], 90)),
                maxh_mean=float(np.mean(a['maxh'])), maxh_p90=float(np.percentile(a['maxh'], 90)),
                empty_mean=float(np.mean(a['empty'])), short_mean=float(np.mean(a['short'])),
                e_lost_mean=float(np.mean(a['e_lost'])), e_lost_p90=float(np.percentile(a['e_lost'], 90)),
                unfinished_pct=100.0 * a['unfinished'] / n_runs,
                fin_delay_mean=float(np.mean(a['fin'])) if a['fin'] else 0.0,
                pause_max_mean=float(np.mean(a['pause_max'])) if a['pause_max'] else 0.0,
            )
        results[name] = dict(weight=w, csl=csl, nph=nph, desc=desc,
                             pauses_T0_mean=float(np.mean(n_pause_events)),
                             pauses_T0_p90=float(np.percentile(n_pause_events, 90)),
                             nights_with_pause_pct=100.0 * float(np.mean(np.array(n_pause_events) > 0)),
                             T=summ)
        print(name, 'pauzy T0 =', round(results[name]['pauses_T0_mean'], 1), flush=True)
    return results


# ----------------------------------------------------------------------------------------------
# SILNIK — kilka wallboxów (budynek, zakład); zdarzeniowy
# ----------------------------------------------------------------------------------------------
def simulate_multi(H, T, cars, S, nph=3):
    """H: zapas [A] dla wszystkich wallboxów w kolejnych sekundach (już po odjęciu reszty budynku).
    cars: lista dict(t_plug, e_need). Przydział: najpierw auta już ładujące, potem wracające z pauzy,
    po 6 A na auto ile się zmieści; reszta zapasu dzielona równo (do 16 A)."""
    kwh_per_As = V * nph / 3.6e6
    n = len(cars)
    chg = [False] * n; pu = [c['t_plug'] for c in cars]; E = [0.0] * n; done = [False] * n
    cyc = [[] for _ in range(n)]; tstart = [0] * n; fin = [None] * n
    # granice zmian H
    change = np.flatnonzero(np.diff(H) != 0) + 1
    bounds = np.concatenate([[0], change, [S]])
    bi = 0; t = 0
    while t < S:
        # następna granica H
        while bi + 1 < len(bounds) and bounds[bi + 1] <= t:
            bi += 1
        tb = bounds[bi + 1] if bi + 1 < len(bounds) else S
        h = int(H[t])
        # kto może ładować
        active = [i for i in range(n) if not done[i] and cars[i]['t_plug'] <= t]
        keep = [i for i in active if chg[i]]
        want = [i for i in active if not chg[i] and pu[i] <= t]
        kmax = max(0, h // PAUSE_A)
        new_chg = keep[:kmax] + want[:max(0, kmax - len(keep))]
        for i in active:
            if chg[i] and i not in new_chg:          # pauza
                chg[i] = False; cyc[i][-1][1] = t; pu[i] = t + T
            elif (not chg[i]) and i in new_chg:      # start / wznowienie
                chg[i] = True; tstart[i] = t; cyc[i].append([t, None])
        k = len(new_chg)
        per = min(WB_MAX, h // k) if k else 0
        # następne zdarzenie: granica H, koniec pauzy auta, koniec ładowania
        t_next = tb
        for i in active:
            if not chg[i] and pu[i] > t:
                t_next = min(t_next, pu[i])
        # energia do t_next (z narastaniem)
        for i in new_chg:
            rel0 = t - tstart[i]; L = t_next - t
            rel = np.arange(rel0, rel0 + L)
            f = np.clip((rel - START_DELAY) / RAMP, 0, 1)
            e = np.cumsum(f) * per * kwh_per_As
            if E[i] + e[-1] >= cars[i]['e_need']:
                kk = int(np.searchsorted(e, cars[i]['e_need'] - E[i]))
                t_next = min(t_next, t + kk + 1)
        for i in new_chg:
            rel0 = t - tstart[i]; L = t_next - t
            rel = np.arange(rel0, rel0 + L)
            f = np.clip((rel - START_DELAY) / RAMP, 0, 1)
            E[i] += float(f.sum()) * per * kwh_per_As
            if E[i] >= cars[i]['e_need'] - 1e-9:
                done[i] = True; chg[i] = False; cyc[i][-1][1] = t_next; fin[i] = t_next
        t = t_next
    for i in range(n):
        if cyc[i] and cyc[i][-1][1] is None:
            cyc[i][-1][1] = S
    return cyc, E, fin


def site_loads(pr, kind):
    """Odbiorniki budynku / zakładu w oknie 07:00-17:00 (t0 = 7) albo 17:00-07:00 dla wspólnoty."""
    r = pr.rng; S = pr.S
    if kind == 'B1':   # wspólnota mieszkaniowa, 3x40 A, wieczór/noc 17:00-07:00
        pr.add3(0, S, 4.0)                                   # oświetlenie, wentylacja, pompy
        # winda 3-f 8 A/fazę, jazda 25 s; częstość zależna od pory
        for (a, b, per_h) in [(hm(17), hm(22), 30), (hm(22), hm(24), 12), (hm(0), hm(6), 3), (hm(6), hm(7), 25)]:
            t = a
            while t < b:
                pr.add3(t, 25, 8.0); t += r.exponential(3600 / per_h)
        # hydrofor 3-f 6 A/fazę, 60 s co 5-10 min wieczorem i rano
        for (a, b) in [(hm(17), hm(23)), (hm(6), hm(7))]:
            t = a
            while t < b:
                pr.add3(t, 60, 6.0); t += r.uniform(5, 10) * 60
        # pralnia: 2 suszarki 11 A na różnych fazach, wieczorem (termostat)
        for ph in (0, 1):
            if r.random() < 0.5:
                t = r.uniform(hm(18), hm(21)); pr.add(ph, t, 15 * 60, 11.0)
                pr.cyc(ph, t + 15 * 60, 70 * 60, 150, 90, 11.0)
        # kotłownia gazowa: pompy 2 A; grzałka zasobnika 3-f 9 A/fazę 22:00-01:00 u 50 %
        if r.random() < 0.5:
            pr.add3(hm(22), 3 * 3600, 9.0)
    elif kind == 'B2':  # biuro / mały hotel, 3x63 A, dzień 07:00-17:00
        pr.add3(0, S, 8.0)                                   # serwery, oświetlenie, wentylacja
        pr.cyc(0, r.uniform(0, 600), S, 10 * 60, 10 * 60, 20.0, jitter=0.3, three=True)   # klimatyzacja/HVAC
        for _ in range(r.poisson(12)):                       # kuchnia: czajniki, mikrofale
            pr.add(int(r.integers(0, 3)), r.uniform(hm(7, 30, 7), hm(15, 0, 7)), r.uniform(90, 240), 9.6)
        t = 0
        while t < S:                                         # winda 8 A/fazę
            pr.add3(t, 25, 8.0); t += r.exponential(3600 / 20)
    elif kind == 'I1':  # warsztat / mała produkcja, 3x100 A, dzień
        pr.add3(0, S, 5.0)                                   # oświetlenie, biuro
        pr.add3(hm(7, 30, 7), 8 * 3600, 15.0)                # maszyny CNC ciągle
        t = r.uniform(0, 300)
        while t < S:                                         # sprężarka 15 kW = 22 A/fazę, 90 s co 3-10 min
            pr.add3(t, 90, 22.0); t += r.uniform(3, 10) * 60
        t = 0
        while t < S:                                         # spawarka 1-f 40 A, serie 10-30 s
            if r.random() < 0.6:
                for _ in range(r.integers(3, 10)):
                    pr.add(int(r.integers(0, 3)), t, r.uniform(10, 30), 40.0); t += r.uniform(30, 90)
            t += r.exponential(20 * 60)
    elif kind == 'I2':  # warsztat 3x63 A, 2 wallboxy
        pr.add3(0, S, 4.0)
        pr.add3(hm(7, 30, 7), 8 * 3600, 8.0)
        t = r.uniform(0, 300)
        while t < S:
            pr.add3(t, 120, 15.0); t += r.uniform(3, 8) * 60
        t = 0
        while t < S:
            if r.random() < 0.6:
                for _ in range(r.integers(3, 10)):
                    pr.add(int(r.integers(0, 3)), t, r.uniform(10, 30), 30.0); t += r.uniform(30, 90)
            t += r.exponential(20 * 60)


SITES = {
    'B1 wspólnota, 3x40 A, 3 wallboxy, wieczór/noc': dict(kind='B1', csl=40, n=3, S=14 * 3600,
        plug=(hm(17, 30), hm(19, 30)), need=(15, 35), t0=17),
    'B2 biuro/hotel, 3x63 A, 3 wallboxy, dzień': dict(kind='B2', csl=63, n=3, S=10 * 3600,
        plug=(hm(7, 0, 7), hm(9, 0, 7)), need=(10, 30), t0=7),
    'I1 zakład, 3x100 A, 3 wallboxy, dzień': dict(kind='I1', csl=100, n=3, S=10 * 3600,
        plug=(hm(7, 0, 7), hm(9, 0, 7)), need=(10, 30), t0=7),
    'I2 warsztat, 3x63 A, 2 wallboxy, dzień': dict(kind='I2', csl=63, n=2, S=10 * 3600,
        plug=(hm(7, 0, 7), hm(9, 0, 7)), need=(10, 30), t0=7),
}


def run_sites(n_runs=30, seed=2):
    out = {}
    for name, c in SITES.items():
        rng = np.random.default_rng(seed)
        S = c['S']
        acc = {T: dict(cycles=[], maxh=[], empty=[], e_lost=[], unfinished=0) for T in T_LIST}
        p0 = []
        for k in range(n_runs):
            pr = Profile(rng, S, 3)
            site_loads(pr, c['kind'])
            usable = int(np.floor(0.9 * c['csl']))
            H = usable - np.ceil(pr.maxphase() - 1e-9).astype(int)
            cars = [dict(t_plug=int(rng.uniform(*c['plug'])), e_need=float(rng.uniform(*c['need'])))
                    for _ in range(c['n'])]
            cyc0, E0, f0 = simulate_multi(H, 0, cars, S)
            p0.append(sum(len(x) - 1 for x in cyc0))
            for T in T_LIST:
                cyc, E, fin = simulate_multi(H, T, cars, S)
                a = acc[T]
                allc = [x for cc in cyc for x in cc]
                a['cycles'].append(len(allc))
                starts = np.array([x[0] for x in allc]); mh = 0
                for s0 in starts:
                    mh = max(mh, int(((starts >= s0) & (starts < s0 + 3600)).sum()))
                a['maxh'].append(mh)
                a['empty'].append(int(sum(1 for x in allc if x[1] - x[0] < 60)))
                a['e_lost'].append(sum(E0) - sum(E))
                a['unfinished'] += int(sum(1 for i in range(c['n']) if fin[i] is None and f0[i] is not None))
        summ = {T: dict(cycles_mean=float(np.mean(a['cycles'])), maxh_mean=float(np.mean(a['maxh'])),
                        empty_mean=float(np.mean(a['empty'])), e_lost_mean=float(np.mean(a['e_lost'])),
                        unfinished_pct=100.0 * a['unfinished'] / (n_runs * c['n']))
                for T, a in acc.items()}
        out[name] = dict(n=c['n'], csl=c['csl'], pauses_T0_mean=float(np.mean(p0)), T=summ)
        print(name, 'pauzy T0 =', round(out[name]['pauses_T0_mean'], 1), flush=True)
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    nh = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    ns = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    res = dict(houses=run_houses(nh), sites=run_sites(ns), T_list=T_LIST,
               params=dict(PAUSE_A=PAUSE_A, START_DELAY=START_DELAY, RAMP=RAMP, WB_MAX=WB_MAX))
    with open(os.path.join(here, 'wyniki.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print('zapisano wyniki.json')
