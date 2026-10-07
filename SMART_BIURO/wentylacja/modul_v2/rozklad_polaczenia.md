# Lista połączeń — płytka główna modułu v2

Siatka **A–X / 01–18**, płytka uniwersalna 5×7 cm.
ESP32 stoi **pionowo**: listwa `VIN…EN` w kolumnie **A**, listwa `3V3…D23`
w kolumnie **K**, oba rzędy pinów 02–16. Gniazdo USB wystaje poza krawędź
płytki od strony rzędu 18.

Gruba linia na rysunku = **mostek z cyny**. Cienka = **przewód w izolacji**
prowadzony od spodu; może przechodzić nad zlutowanym pinem i nad mostkiem.

## 1. Szyny — ciągły mostek cyny

| # | Przebieg | Rola |
|---|---|---|
| 1 | **L01 → V01** (rząd 01) | szyna +5 V |
| 2 | **X02 → X18** (kolumna X) | szyna GND |
| 3 | **L18 → X18** (rząd 18) | odnoga masy przy przetwornicy |

## 2. Pozostałe mostki

| # | Przebieg | Co łączy |
|---|---|---|
| 4 | **K07** → **L07** → **M07** | pole RXD modułu (wejście nadajnika, nieużywane) → RX2 |
| 5 | **K08** → **L08** → **M08** | pole TXD modułu = WYJŚCIE odbiornika → TX2 (firmware czyta GPIO17) |
| 6 | **K02** → **L02** | 3V3 procesora → węzeł +3,3 V |
| 7 | **K03** → **L03** | GND procesora → węzeł masy |
| 8 | **K16** → **L16** | D23 → tor nadawczy |
| 9 | **L03** → **L04** | masa procesora → odnoga masy w rzędzie 04 |
| 10 | **O03** → **O04** | emiter tranzystora → odnoga masy |
| 11 | **A01** → **A02** | szyna +5 V → VIN procesora |
| 12 | **X01** → **X02** | minus C1 → szyna GND |
| 13 | **N17** → **N18** | OUT− przetwornicy → odnoga masy |
| 14 | **V17** → **V18** | IN− przetwornicy → odnoga masy |

## 3. Przewody w izolacji, od spodu

| # | Trasa | Co łączy |
|---|---|---|
| 15 | **M01** → **A01** | szyna +5 V → VIN (przewód pod modułem) |
| 16 | **L16** → **L10** → **N10** → **N02** → **P02** | D23 → R2 → baza tranzystora |
| 17 | **M09** → **M18** | GND modułu RS485 → odnoga masy |
| 18 | **M05** → **L05** → **L06** → **K06** | EN modułu RS485 → D4 |
| 19 | **M06** → **M02** → **L02** | VCC modułu RS485 → 3V3 |
| 20 | **S06** → **X06** | masa magistrali → szyna GND (odniesienie dla A/B) |
| 21 | **V02** → **V07** → **T07** → **S07** | A z wtyku → pin A modułu |
| 22 | **U02** → **U08** → **T08** → **S08** | B z wtyku → pin B modułu |
| 23 | **W02** → **W12** → **V12** | +12 V z wtyku → IN+ przetwornicy |
| 24 | **N12** → **N11** → **T11** → **T01** | OUT+ przetwornicy → szyna +5 V |

## 4. Elementy przewlekane

| Element | Otwory | Uwaga |
|---|---|---|
| R1 33 Ω | **Q01 → Q02** | pionowo, jedna nóżka zagięta; Q01 leży na szynie +5 V |
| R2 470 Ω | **P02 → P03** | pionowo; P03 to baza tranzystora |
| T1 BC337-40 | **O03** = E, **P03** = B, **Q03** = C | baza to środkowa nóżka; BC337 ma płaską ścianką do siebie kolejność **E-B-C** (odwrotnie niż BC547). Na płytce: **płaska ścianka zwrócona w stronę rzędu 18**, grzbiet do rzędu 01 |
| C1 470 µF | **+ w V01**, **− w X01** | rozstaw 2 otwory = 5,08 mm; W01 zostaje pusty |

## 5. Wtyk JST-XH z gniazda COM-MANUAL

| Żyła | Otwór |
|---|---|
| B | **U02** |
| A | **V02** |
| +12 V | **W02** |
| GND | **X02** |

## 6. Dioda TSAL6100 — dwa przewody

Dioda musi być przyklejona naprzeciw okienka odbiornika jednostki, więc
zostaje na przewodach; cała elektronika sterująca jest na płytce.

| Żyła | Otwór |
|---|---|
| anoda | **Q02** — za rezystorem R1 |
| katoda | **Q03** — kolektor tranzystora |

**Odbiornika podczerwieni nie ma.** Rzeczywisty stan jednostki podaje
magistrala co 800 ms i to ona potwierdza wykonanie komendy, więc echo IR
niczego nie wnosiło. **D19 zostaje wolny** — gdyby kiedyś miał wrócić,
wystarczy mostek `K11 → L11` i trzy przewody z VS1838B.

## 6a. Na samym module RS485 V2.05 — obowiązkowe

Odbiornik tego modułu jest fabrycznie wyłączony: noga `RE` układu MAX3485 jest
podciągnięta do plusa przez rezystor `103` i nie wychodzi na listwę (`EN` steruje
tylko nadajnikiem). **Drut od pola dalej od litery `T` do pola `GND` listwy** — na
module, przed osadzeniem w podstawce. Pole bliżej `T` to `VCC`, nie zwierać do masy.

Pole `TXD` modułu jest wyjściem odbiornika (opisy z perspektywy modułu); płytka
zostaje zlutowana jak na rysunku, firmware czyta GPIO17. Szczegóły: MODUL_v2 3.3a.

## 7. Czego jeszcze nie zmierzyłem

| Element | Co sprawdzić | Co zrobić, jeśli wyjdzie inaczej |
|---|---|---|
| RS485 V2.05 | odstęp listwy `EN…GND` od listwy `GND/A/B` | przesunąć obrys; przewody A i B dociągnąć do rzeczywistych pinów |
| MP1584 | rozstaw IN↔OUT i rozstaw pinów w parze | przesunąć obrys w wolnym polu N–V, rzędy 11–17 |
| C1 470 µF | rzeczywisty rozstaw nóżek | jeśli 3,5 mm — wstawić w **V01/W01**, mostek **W01→X01** |
