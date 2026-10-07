# Obwód Control Pilot (IEC 61851) — paczka realizacyjna (Faza 1)

Pierwszy kamień milowy projektu: warstwa fizyczna Control Pilot, w której widać poziomy **9 V (stan B)** i **6 V (stan C)** oraz przebieg **PWM ±12 V / 1 kHz**.

## Wynik (zweryfikowany u mnie w Pythonie)

| Stan | Rezystancja auta (Rev) | Napięcie na CP | Cel normy |
|---|---|---|---|
| A — brak auta | — | **+12,00 V** (stałe, bez PWM) | +12 V |
| B — podłączone | 2 740 Ω | **+8,98 V** | ~9 V |
| C — ładowanie | 2 740 ‖ 1 300 = 882 Ω | **+5,99 V** | ~6 V |
| dół PWM | dioda blokuje | **−12,00 V** | −12 V |

Kodowanie prądu: **I [A] = wypełnienie [%] × 0,6** (10–85%). Zob. `cp_waveform.png`.

## Co jest w paczce

- **`cp_waveform.png`** — gotowy wykres: handshake A→B→C z poziomami 9/6 V.
- **`cp_circuit_sim.py`** — darmowy model w Pythonie (numpy/matplotlib). Liczy poziomy i rysuje przebieg. Uruchom: `python3 cp_circuit_sim.py`.
- **`cp_circuit.cir`** — netlista dla **ngspice / LTspice** (ten sam obwód jako prawdziwy SPICE). W ngspice: `ngspice cp_circuit.cir`. W LTspice: otwórz jako plik tekstowy/„netlist” i uruchom `.tran`; oglądaj `V(cp)`. Stan C: odkomentuj linię `R3`.
- **`build_cp_circuit_simscape.m`** — skrypt budujący ten sam obwód w **Simulink/Simscape**. Uruchom w MATLAB: `build_cp_circuit_simscape`.

## Obwód (schemat tekstowy = źródło prawdy do okablowania)

```
 Vpilot(PWM ±12V) --[R1 1k]--+--(węzeł CP)
                             |
                          [Dioda]
                             |
                         (węzeł X)--[R2 2,74k]--+--(masa/PE)
                             |                  |
                          [Switch]--[R3 1,3k]---+
                             ^
                       StateC (0=B, 1=C)

 Voltage Sensor:  (+)->CP, (-)->masa  ->  Scope
 Solver Configuration: dopięty do dowolnego węzła (np. masa)
```

Lista połączeń (gdyby auto-okablowanie w skrypcie .m gdzieś nie wstało — komunikat `[!]`):

1. `PWM → Bias(−12) → Simulink-PS → Vsrc(sygnał sterujący)`
2. `Vsrc(+) → R1`
3. `R1 → CP → Dioda(anoda)`
4. `Dioda(katoda) → X`
5. `X → R2 → masa`
6. `X → Switch → R3 → masa`
7. `Vsrc(−) → masa`
8. `StateC → Simulink-PS → Switch(sterowanie)`
9. `Voltage Sensor: (+)→CP, (−)→masa ; wyjście → PS-Simulink → Scope`
10. `Solver Configuration → masa`

## Ważne uwagi

- Skrypt `.m` **nie był uruchomiony** u mnie (brak MATLAB-a w środowisku). Dodawanie bloków i parametry są pewne; ścieżki bloków to standardowy **Foundation Library (`fl_lib`)** — wymaga **bazowego Simscape**, nie dodatku Simscape Electrical. Jeśli któraś linia połączenia nie powstanie, dorysuj ją wg listy wyżej (kilka minut), potem `Ctrl+Shift+A` (auto-układ) i Run.
- Poziomy 9 V/6 V mierzymy **na węźle CP** (między R1 a diodą) — tak jak robi to ładowarka. Dlatego spadek na diodzie nie psuje wartości (sprawdź: wynik 8,98 V / 5,99 V).
- To warstwa **niskonapięciowa, sygnałowa** — bezpieczna. Tor mocy (230/400 V) to osobna, późniejsza faza.
