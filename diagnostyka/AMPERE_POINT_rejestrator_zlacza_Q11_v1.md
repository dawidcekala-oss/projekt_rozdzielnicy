# Rejestrator złącza międzypłytkowego Q11 — projekt układu podsłuchowego (v1)

**AMPERE POINT · wątek diagnostyki · 2026-08-28 · dokument po 2 rundach recenzji adwersarialnej (dziennik iteracji na końcu)**

Schematy (w tym folderze):
- `AMPERE_POINT_rejestrator_Q11_schemat_A_architektura.png` — architektura: złącze, odczepy, multipleksery, UNO, zasady bezpieczeństwa, klasyfikacja sygnałów,
- `AMPERE_POINT_rejestrator_Q11_schemat_B_tor_CT.png` — tory szybkie: CT, detektor szczytu, pin 1.65,
- `AMPERE_POINT_rejestrator_Q11_schemat_C_tor_CP.png` — tor Control Pilot z komparatorem.
Generator schematów: `generator_schematow_rejestratora.py`.

Odbiorca: technicy serwisu. Wszystkie skróty wyjaśnione przy pierwszym użyciu.
Ograniczenie zakupowe: wszystkie części z asortymentu sklepu elektronika-sklep.pl
(punkt Warszawa) — lista zakupów w §10.

## 1. Cel i zasada działania

Błąd „Overload Reminder" w serii Q pojawia się losowo, przy ROZWARTYCH przekaźnikach —
czyli nie pochodzi z rzeczywistego prądu, lecz powstaje w torze pomiarowym. Główny
podejrzany: tor CT (od ang. current transformer — przekładnik prądowy, pin CT złącza).
Hipoteza konkurencyjna: **pływające odniesienie** — pin 1.65 (nominalnie 1,65 V,
zmierzono 4,31 V!) jest prawdopodobnie punktem odniesienia toru pomiarowego; jego
drgnięcie przesuwa odczyt prądu w sterowniku BEZ żadnego zakłócenia na samej linii CT.
Multimetr pokazuje tylko średnią; oscyloskop widzi kształt, ale nie da się nim patrzeć
na 20 linii przez wiele godzin, czekając na losowy błąd.

Rozwiązanie: **rejestrator wielokanałowy na Arduino UNO**, wpięty odczepami w linie
złącza międzypłytkowego (płytka mocy ↔ płytka kontrolna), logujący WSZYSTKIE sygnały
jednocześnie do laptopa przez wiele godzin. Gdy błąd wystąpi, w logu widać, KTÓRY
sygnał zmienił się PIERWSZY i jak wyglądały pozostałe — korelacja czasowa, której nie
da żaden pojedynczy przyrząd.

Zasada architektury oprogramowania: **UNO niczego nie interpretuje — wysyła ciągły,
surowy strumień binarny, a wszystkie decyzje (progi, obwiednie, wykrywanie anomalii)
zapadają offline na laptopie.** Na UNO nie ma wyzwalaczy, buforów przedwyzwoleniowych
ani progów do strojenia — nie ma więc też ryzyka, że źle dobrany próg przegapi błąd
albo że zrzut bufora zablokuje akwizycję w najważniejszym momencie. W strumieniu są
tylko proste znaczniki zdarzeń (zmiany linii K, klawisz operatora, aktywność
wyświetlacza) na wspólnej osi czasu.

Nadrzędna zasada projektowa: rejestrator ma być „niewidzialny" dla ładowarki. Każdy
odczep obciąża badaną linię co najwyżej rezystancją 200 kΩ (a tory pomiarowe — tylko
prądami upływu rzędu mikroamperów), więc nawet awaria rejestratora nie może sama
wywołać badanego błędu. Liczby — w §4.

## 2. Sygnały złącza — pinout potwierdzony

Pinout POTWIERDZONY zdjęciem strony lutowania (zdjęcie piny_tyl_obudowy): jedno
złącze 2 rzędy × 10 pinów, raster 2,54 mm, obudowane z zatrzaskiem (typ BHL20),
taśma wielożyłowa.

Rząd 1: `PE · NTC1 · ICP · 8V · K1 · K2 · K3 · K4 · 1.65 · CP`
Rząd 2: `GND · GND · CT · NTC2 · ZL3 · ZL2 · ZL1 · V1 · V2 · V3`

Uwagi do pinoutu:
- Wcześniejszy odczyt w DANE_DIAGNOSTYCZNE.md (7 opisów w rzędzie drugim,
  w tym N_PE) był niepełny. **Pin N_PE na tym złączu nie występuje** — tor detekcji
  uziemienia biegnie inaczej albo kryje się pod pinem o innej nazwie; nie zgadywać.
- Na sitodruku płytki kontrolnej fazowe piny pomiarowe opisane są **V1–V3**
  (nie U1–U3 jak w starszych notatkach) — w tym dokumencie używamy V1–V3.
- **ZL1–ZL3: znaczenie niepotwierdzone.** Chińskie opisy na płytce kontrolnej mogą
  oznaczać 电流 = prąd (per faza), a nie 电压 = napięcie. Do weryfikacji pomiarem
  w trybie rekonesansu według tabeli decyzyjnej §6.5 — do tego czasu traktować
  jako sygnał nieznany.
- Mimo potwierdzenia zdjęciem: **przed budową zdzwonić omomierzem KAŻDY pin** do
  znanych węzłów (GND płytki kontrolnej, PE zacisku, N i L zacisków wejściowych)
  przy urządzeniu odłączonym od sieci i wpisać wyniki do tabeli. To wykrywa
  niespodzianki typu „pin opisany jako masa, a związany z siecią" zanim cokolwiek
  zostanie połączone.

Klasyfikacja sygnałów (wartości zmierzone — z egzemplarza uszkodzonego, przy
wyświetlanym błędzie, multimetrem w trybie napięcia stałego):

| Sygnał | Typ | Zmierzono / zakres | Charakter | Tor w rejestratorze |
|---|---|---|---|---|
| CT | analogowy | 1,651 V (średnia) | przebieg zmienny 50 Hz + podejrzane zakłócenia — GŁÓWNY PODEJRZANY | szybki slot A0, 2 kHz + detektor szczytu → multiplekser (§4.3) |
| 1.65 | analogowy DC | **4,31 V** (nazwa sugeruje 1,65 V!) | odniesienie — hipoteza konkurencyjna | **szybki slot A4, 2 kHz** (§4.6) |
| CP | analogowy dwubiegunowy | ±12 V, PWM 1 kHz (Control Pilot — linia pilota wg normy IEC 61851; PWM = modulacja szerokości impulsu) | poziomy stanów A/B/C | sieć rezystorowa → A1 + komparator → D8 (pomiar wypełnienia) |
| V1, V2, V3 | analogowy | 0,56 V każdy (średnia) | kształt napięcia sieci, z dzielników 1 MΩ na płytce mocy | multiplekser → A2 |
| NTC1, NTC2 | analogowy | 1,78 / 1,77 V | wolnozmienne (termistory — czujniki temperatury) | multiplekser |
| 8V | analogowy DC | 7,45 V | szyna zasilania płytki kontrolnej | dzielnik → multiplekser |
| K1–K4 | quasi-cyfrowy ~7,45 V | K1–K3: 7,45 V; **K4: 5,08 V (anomalia!)** | sterowanie przekaźnikami | dzielnik → multiplekser, odczyt ANALOGOWY (patrz §4.5) |
| ICP | NIEZNANY | 0 V | do sklasyfikowania | multiplekser (tryb rekonesansu) |
| ZL1–ZL3 | NIEZNANY | 3,298 V każdy | do sklasyfikowania (电流/电压 — patrz wyżej) | multiplekser (tryb rekonesansu) |
| GND | masa | 0 (odniesienie) | — | JEDEN pin GND → masa UNO (§5.2) |
| PE | przewód ochronny | GND→PE: −3,79 V | — | **NIE podłączać do rejestratora** (§5.2) |

Poza złączem 2×10 rejestrator ma jeszcze jeden odczep: linię nadawczą UART
(uniwersalny interfejs szeregowy) między płytką kontrolną a wyświetlaczem DWIN
T5L0 — jako znacznik chwili wystąpienia błędu (§4.8).

## 3. Wpięcie w złącze — dwa warianty

Pola lutownicze złącza są dostępne od tyłu obudowy (zdjęcie piny_tyl_obudowy),
co otwiera wariant prostszy niż przelotka.

### 3.1 Wariant A — odczepy lutowane od spodu (REKOMENDOWANY)

Cienkie przewody dolutowane wprost do pól lutowniczych złącza od strony lutowania,
bez rozcinania żadnego toru i bez dodatkowych złączy.

Wykonanie:
- wyłącznie przy urządzeniu odłączonym i potwierdzonym jako beznapięciowe (§5.5);
- **pierwszy rezystor 100 kΩ wlutowany w przewód jak najbliżej punktu odczepu**,
  zabezpieczony koszulką termokurczliwą — dzięki temu przetarcie lub zwarcie
  przewodu odczepowego do czegokolwiek obciąża badaną linię co najwyżej przez
  100 kΩ, nigdy wprost;
- lutowanie z topnikiem, oględziny pod lupą; po lutowaniu dla każdego odczepu
  omomierzem: ciągłość odczep↔pin oraz BRAK zwarcia z oboma pinami sąsiednimi
  (raster 2,54 mm — mostek cynowy to najbardziej prawdopodobny błąd montażu);
- wiązka odczepów odciążona mechanicznie (opaska, kropla kleju na krawędzi
  obudowy) i poprowadzona z dala od zacisków toru mocy, tak by żaden przewód
  nie mógł opaść na tor 40 A;
- PE oraz drugi (nadmiarowy) pin GND: **bez odczepu, nietykane**.

Zalety: oryginalne złącze pozostaje zamknięte i nienaruszone — zachowanie
urządzenia bez zmian (znika też wątpliwość o wpływ pojemności i długości taśmy
przelotki); brak ryzyka odwrotnego lub przesuniętego wpięcia wtyku; zero
egzotycznych złączy. Wady: demontaż odczepów wymaga lutownicy.

Odczep linii UART wyświetlacza (§4.8) wykonać tą samą techniką na polach
lutowniczych złącza wyświetlacza na płytce kontrolnej — te same zasady
(rezystor przy punkcie odczepu, koszulka, test zwarć z sąsiadami).

### 3.2 Wariant B — przelotka w linii taśmy (zapasowy)

Płytka uniwersalna MS-TSOP1 z wlutowanym złączem BHL20 S lub RA (2×10, obudowane,
z zatrzaskiem — identyczne jak fabryczne): w BHL20 wpina się ORYGINALNA taśma
(zatrzask i obudowa wymuszają poprawną orientację — nie da się wpiąć odwrotnie
ani z przesunięciem o pin). Z przelotki każda linia biegnie 1:1 do gniazda na
płytce kontrolnej, a odczep odchodzi przez rezystory jak w §4.

Słabe miejsce: w asortymencie sklepu nie ma gotowej taśmy 2×10 z zaciśniętym
żeńskim złączem — połączenie przelotki z gniazdem płytki kontrolnej trzeba
wykonać kabelkami połączeniowymi żyła po żyle, a 20 luźnych końcówek to wysokie
ryzyko pomyłki. Dlatego obowiązkowo: trwałe oznaczenie rzędów 1/2 i pinu nr 1
na przelotce, 100% test ciągłości pin–pin oraz braku zwarć między wszystkimi
parami sąsiednich pinów PRZED pierwszym wpięciem, oględziny strony lutowania.
Linia PE wyłącznie jako przelot 1:1 — nigdy do masy rejestratora.

Kiedy wariant B: gdy pola lutownicze okażą się niedostępne albo odczep ma być
wielokrotnie zakładany i zdejmowany bez lutowania. W pozostałych przypadkach —
wariant A.

## 4. Tory wejściowe — wartości przeliczone

### 4.1 Zasada wspólna każdego odczepu

Każdy odczep zaczyna się od **dwóch rezystorów 100 kΩ w szereg (razem 200 kΩ)**.
Dlaczego dwa: pojedynczy rezystor przewlekany ma dopuszczalne napięcie pracy
ok. 250 V — dwa w szeregu wytrzymują 500 V, czyli więcej niż 400 V międzyfazowe.
Scenariusz awaryjny „230 V na odczepie" (przebicie na płytce mocy): prąd
230 V / 200 kΩ = **1,15 mA** (poziom bezpieczny dotykowo i o rząd wielkości
poniżej dawnych 23 mA przy 10 kΩ), moc 0,264 W łącznie = **0,13 W na rezystor**
— w granicach elementów 0,25 W.

Za rezystorami: **para diod 1N4148** — jedna do szyny +5 V UNO, druga do masy
(klamra: napięcie w węźle nie wyjdzie poza ok. −0,7…+5,7 V). Przy awarii 230 V
(szczyt 325 V) do szyny 5 V wpływa (325 − 5,7) / 200 kΩ ≈ **1,6 mA** — dioda
wytrzymuje (limit 200 mA), a UNO pobiera z tej szyny dziesiątki mA, więc szyna
prąd przyjmie. Za klamrą dodatkowy rezystor **10 kΩ** do wejścia multipleksera —
dzięki niemu samo wejście układu CD4051BE nigdy nie zobaczy nawet tych 5,7 V
w pełni (ochrona przed zatrzaśnięciem struktury, tzw. latch-up, po którym
multiplekser mógłby zewrzeć kanały między sobą).

Skutek dla badanej ładowarki: tory pomiarowe (typ P niżej) NIE mają ścieżki
stałoprądowej do masy — obciążenie to wyłącznie prądy upływu (pojedyncze µA
w najgorszym przypadku). Dla porównania: dawny odczep 10 kΩ przy niezasilonym
rejestratorze ściągnąłby pin 1.65 z 1,65 V do ok. 1,1 V i przesunął zero
wszystkich pomiarów ładowarki — obecny odczep 200 kΩ z klamrą pobiera z tego
pinu najwyżej (1,65 − 0,6) / 200 kΩ ≈ **5 µA** nawet przy martwym rejestratorze.
Mimo to obowiązuje **sekwencja: najpierw zasilić rejestrator, potem ładowarkę;
przy demontażu odwrotnie** (najpierw ładowarka spod napięcia, potem rejestrator).

Typy odczepów:
- **typ P (pomiarowy):** pin → 100 kΩ + 100 kΩ → klamra 2×1N4148 → 10 kΩ →
  multiplekser. Dotyczy: V1–V3, ZL1–ZL3, ICP, NTC1, NTC2.
- **typ D (z dzielnikiem):** jak typ P, ale w węźle klamry dodatkowo **220 kΩ
  do masy**. Podział: 220 / (200 + 220) = 0,524. Dotyczy: K1–K4, 8V.
- **CT, 1.65, CP, detektor szczytu, UART wyświetlacza:** tory dedykowane,
  opisane niżej.

### 4.2 Tor CT (główny podejrzany) → A0, filtr dwustopniowy

Pin CT → **100 kΩ + 100 kΩ** → węzeł 1: klamra 2×1N4148 + kondensator **1 nF
do masy** → **100 kΩ** → węzeł 2: kondensator **470 pF do masy** → wprost na
wejście A0 przetwornika ADC (przetwornik analogowo-cyfrowy) UNO.

To filtr antyaliasingowy DRUGIEGO rzędu (dwustopniowy RC — rezystor-kondensator):
- stopień 1: 200 kΩ × 1 nF → częstotliwość graniczna f₁ ≈ **0,8 kHz**;
- stopień 2: 100 kΩ × 470 pF → f₂ ≈ **3,4 kHz**;
- łączne tłumienie: przy 1 kHz ok. −5 dB, przy 2 kHz ok. −10 dB, przy 4 kHz
  ok. −16 dB, przy 20 kHz ok. **−36 dB** (dla porównania: dawny filtr
  jednostopniowy dawał przy 20 kHz ledwie −21 dB).

Uczciwa deklaracja pasma (ważne dla interpretacji logu): przy próbkowaniu CT
2 kHz (szybki slot, §6.1) granica Nyquista to 1 kHz. **Wiarygodne pasmo logu CT
to ok. 0–0,8 kHz** (składowa 50 Hz i harmoniczne do ~16.); składowe 0,8–1 kHz są
stłumione, ale prawdziwe; **częstotliwości powyżej 1 kHz mogą pojawiać się
w logu jako alias — rejestrator wykrywa, ŻE coś było, ale ich częstotliwości
NIE klasyfikuje.** Klasyfikację widmową szybkich zakłóceń robi oscyloskop,
a ich samą obecność między próbkami łapie detektor szczytu (§4.3).

Pozostałe własności toru:
- kondensator 470 pF przy A0 jest ~34× większy od kondensatora próbkującego
  przetwornika (14 pF) — szpilki doładowania przy każdej próbce zostają
  stłumione i nie wstrzykują istotnego ładunku w badany, wysokoimpedancyjny
  węzeł CT;
- obciążenie stałoprądowe toru CT: tylko upływ wejścia (typowo pojedyncze mV
  błędu na 300 kΩ; katalogowy najgorszy przypadek do ~0,3 V — bez znaczenia,
  bo szukamy ODCHYLEŃ zmiennych od poziomu spoczynkowego, a składową stałą
  odejmuje analiza offline);
- świadome uproszczenie: wtórnik operacyjny (bufor) byłby czystszy, ale sklep
  nie ma wzmacniaczy operacyjnych; wtórnik na tranzystorze BC547C odpada, bo
  przesuwa poziom o ~0,65 V ze współczynnikiem temperaturowym. Odczep 300 kΩ
  z rezerwuarami 1 nF + 470 pF realizuje ten sam cel prostszymi środkami.

### 4.3 Detektor szczytu toru CT → multiplekser (kanał 7)

Osobna, RÓWNOLEGŁA gałąź od pinu CT — łapie zdarzenia szybsze, niż widzi
próbkowanie:

pin CT → **100 kΩ + 100 kΩ** (własna para) → węzeł P: klamra 2×1N4148 →
**dioda 1N4148 szeregowo** (anoda od węzła P) → węzeł D: kondensator **47 nF
do masy** + rezystor upustowy **1 MΩ do masy** → 10 kΩ → multiplekser 1,
kanał 7.

Działanie: węzeł P nie ma kondensatora filtrującego (tylko pojemności
pasożytnicze, τ rzędu mikrosekund), więc szybkie szpilki do niego docierają.
Gdy chwilowe napięcie w P przekroczy napięcie kondensatora + ~0,6 V, dioda
szeregowa doładowuje kondensator — kondensator „zapamiętuje szczyt", a upust
1 MΩ rozładowuje go powoli (stała czasowa ~47 ms), aż do odczytu przez
multiplekser co ~10 ms (utrata między odczytami ~20%).

Uczciwe liczby czułości (ładowanie przez 200 kΩ, τ ≈ 9,4 ms):
- pojedyncze zdarzenie o czasie trwania 100 µs i amplitudzie 2 V ponad próg
  podnosi kondensator o ~20 mV ≈ 4 kroki przetwornika — wykrywalne;
- **powtarzalne szpilki (bursty przetwornic, zakłócenia komutacyjne) pompują
  kondensator kumulacyjnie** — to główny przypadek użycia i tu czułość jest
  wysoka;
- pojedyncza, izolowana szpilka krótsza niż ~10 µs praktycznie nie zostawi
  śladu — to zadeklarowane martwe pole (§8).

Poziom spoczynkowy detektora (szczyt składowej 50 Hz minus 0,6 V) wyznacza
sesja bazowa (§7.2); anomalią jest jego wzrost ponad obwiednię bazową.

### 4.4 Tor CP (pilot ±12 V) → A1 + komparator → D8

Dzielnik dwurezystorowy NIE mieści ±12 V w 0–5 V (warunek na −12 V→0 V wymusza
proporcje, przy których +12 V daje ~7 V). Dlatego sieć trzyrezystorowa z gałęzią
komparatora:

- pin CP → **2×120 kΩ (=240 kΩ)** → węzeł A;
- węzeł A → **100 kΩ → +5 V**; węzeł A → **120 kΩ → masa**;
- węzeł A → klamra 2×1N4148;
- węzeł A → **100 kΩ** → węzeł B; węzeł B → **100 kΩ → masa**; węzeł B →
  wejście odwracające komparatora LM393;
- węzeł A → **10 kΩ** → węzeł A′: kondensator **470 pF do masy** → wejście **A1**.

**Zmiana względem wersji 1 (usunięcie błędu systematycznego wypełnienia):**
kondensator 470 pF NIE siedzi już na węźle A, lecz za rezystorem 10 kΩ na
osobnym węźle A′. Odgałęzienie komparatora odchodzi PRZED kondensatorem —
komparator widzi ostre zbocza (na węźle A zostają tylko pojemności
pasożytnicze, τ poniżej 1 µs), więc dawny błąd systematyczny wypełnienia
~1,6% (≈1 A w skali IEC 61851) spada poniżej **0,1% (≈0,06 A)** — bez
kalibracji programowej. Przeliczenia stałoprądowe (tabela niżej) nie zmieniają
się, bo przesunięcie kondensatora nie zmienia rezystancji sieci.

Cena: węzeł A′ ustala się ze stałą czasową ~22 µs (46 kΩ Thevenina × 484 pF).
Przy fazach PWM dłuższych niż ~150 µs (wypełnienie 15–85%, czyli cały normalny
zakres prądowy IEC) poziom na A1 jest w pełni ustalony; przy fazach krótszych
próbka poziomu jest częściowo nieustalona — ale wypełnienie i tak mierzy
komparator z rozdzielczością mikrosekundową, a poziomy A1 służą tylko do
klasyfikacji stanu A/B/C.

Przeliczenie (z uwzględnieniem gałęzi komparatora):
**U(A) = 1,82 V + 0,152 × U(CP)**

| U(CP) | U(A′) na A1 | U(B) na komparatorze |
|---|---|---|
| +12 V (stan A) | 3,64 V | 1,82 V |
| +9 V (stan B) | 3,18 V | 1,59 V |
| +6 V (stan C) | 2,73 V | 1,36 V |
| 0 V | 1,82 V | 0,91 V |
| −12 V (dół PWM) | 0,00 V | 0,00 V |

Obciążenie linii CP: maks. 50 µA, czyli spadek 50 mV na rezystancji źródła
pilota (1 kΩ) — pomijalny, stany wg IEC 61851 nieprzekłamane.

Komparator LM393 (pomiar wypełnienia PWM sprzętowo, wejście przechwytujące
Timer1 = pin D8):
- wejście odwracające: węzeł B (zakres 0–1,82 V — mieści się w dopuszczalnym
  zakresie wejściowym LM393 przy zasilaniu 5 V, tj. 0–3,5 V; dawny pomysł
  podawania surowego CP ±12 V uszkodziłby układ);
- wejście nieodwracające: próg z dzielnika **100 kΩ / 10 kΩ** z szyny 5 V =
  **0,455 V**, co odpowiada U(CP) = **−6 V** — dokładnie między dołem PWM
  (−12 V) a najniższym stanem górnym (+3 V);
- histereza: rezystor **470 kΩ** z wyjścia do wejścia nieodwracającego —
  ok. 90 mV w węźle B (≈ ±0,6 V w skali CP), koniec drgań na zboczach;
- wyjście (otwarty kolektor): podciąganie **10 kΩ do +5 V** → D8.

Przetwornik na A1 rejestruje poziomy (próbki wyzwalane stanem komparatora —
§6.1: jedna w środku fazy górnej, jedna w dolnej, raz na ~10 ms), komparator
na D8 mierzy wypełnienie każdego okresu z rozdzielczością mikrosekundową.
LM393 jest układem PODWÓJNYM — drugi komparator zostaje wolny jako rezerwa
(np. formowanie poziomu 3,3 V linii UART wyświetlacza, §4.8).

### 4.5 Tory K1–K4 i 8V (typ D, odczyt analogowy)

Poziomy K to ~7,45 V — za dużo na wejście UNO wprost, a dzielnik pod wejście
CYFROWE wpada w strefę zabronioną progów logicznych (przy anomalii K4 = 5,08 V
odczyt byłby losowy — akurat podejrzany sygnał byłby nieczytelny). Dlatego
K1–K4 i 8V idą przez dzielnik typu D na kanały multipleksera i są odczytywane
ANALOGOWO — bez progów logicznych, z pełną wartością napięcia w logu:

| Napięcie na pinie | Po dzielniku ×0,524 (odczyt ADC) |
|---|---|
| 7,45 V (K1–K3, 8V — stan zastany) | 3,90 V |
| 5,08 V (anomalia K4!) | 2,66 V |
| 0 V (stan niski) | 0,00 V |

Rozróżnialność 3,90 V od 2,66 V to ~250 kroków przetwornika — anomalia K4
będzie w logu widoczna wprost, łącznie z jej ewentualnymi wahaniami w czasie.
Obciążenie linii K: 420 kΩ, czyli 18 µA przy 7,45 V — pomijalne.
Rozdzielczość czasowa zdarzeń K wynika z obiegu multipleksera: **~10 ms**
(§6.2) — wystarczająca, bo sam przekaźnik przełącza się 5–15 ms, a korelację
robimy w oknach 20 ms. Każda zmiana skwantowanego stanu K generuje dodatkowo
znacznik zdarzenia w strumieniu (§6.3).

Uwaga interpretacyjna (alias na kanałach wolnych): kanał czytany co ~10 ms
przy paśmie toru ~1,6 kHz zamienia ewentualne tętnienie 50/100 Hz (np. na K4
lub 8V) w powolne „falowanie" o ułamkach herca. **Powolne, okresowe falowanie
kanału wolnego to w pierwszej kolejności podejrzenie aliasu tętnienia, nie
dryfu** — rozstrzyga tryb rekonesansu (kanał zaparkowany, 2 kHz, §6.5).

### 4.6 Tor 1.65 (hipoteza pływającego odniesienia) → A4, szybki slot

Pin 1.65 awansuje z multipleksera do DEDYKOWANEGO wejścia A4, czytanego
w szybkim slocie na przemian z CT (obie linie po 2 kHz — §6.1). Powód:
jeśli odniesienie toru pomiarowego drga, sterownik widzi „prąd" bez żadnego
zakłócenia na linii CT — rejestrator patrzący na 1.65 raz na ~10 ms mógłby
to przegapić, a patrzący 2000 razy na sekundę nie przegapi.

Tor: pin 1.65 → 100 kΩ + 100 kΩ → klamra 2×1N4148 + kondensator **1 nF do
masy** → wprost na **A4**. Pasmo ~0,8 kHz — takie samo jak stopień 1 toru CT,
więc oba szybkie kanały są porównywalne.

Przesłuch szybkiego slotu (uczciwie): przetwornik UNO ma jeden kondensator
próbkujący, który przy przełączeniu A0↔A4 wnosi ładunek poprzedniego kanału.
Mimo odrzucania pierwszej konwersji (§6.2) zostaje stały ofset rzędu
kilkunastu kroków przetwornika (przy różnicy poziomów CT↔1.65 ok. 2,7 V),
a szybkie zmiany jednej linii odciskają się w drugiej z wagą ~2%. Ofset jest
stały (mierzy go sesja sucha §7.1 i bazowa §7.2 — analiza offline go
odejmuje); sprzężenie 2% oznacza, że anomalii mniejszej niż ~3 kroki ponad
obwiednię bazową nie rozstrzygamy między liniami — większe rozstrzygamy.

### 4.7 Multipleksery — 2× CD4051BE

Werdykt w sprawie „ekspanderów": klasyczne ekspandery wejść/wyjść (MCP23017
itp.) są CYFROWE — tu prawie nic by nie dały. Właściwe narzędzie to multiplekser
ANALOGOWY. Pierwotnie planowany 16-kanałowy 74HC4067 jest niedostępny w sklepie —
zastępują go **dwa 8-kanałowe CD4051BE** (DIP16, 3,30 zł/szt.). Precyzyjny
przetwornik ADS1115 również niedostępny — i niepotrzebny: 10-bitowy przetwornik
UNO w zupełności wystarcza do logowania korelacyjnego.

Połączenie (prostsze niż jeden 16-kanałowy):
- linie adresowe A/B/C obu układów RÓWNOLEGLE → D4, D5, D6;
- wejścia blokujące (INH) obu układów na stałe do masy (zawsze aktywne);
- wyjście multipleksera 1 → **A2**, wyjście multipleksera 2 → **A3** — jeden
  adres wybiera naraz parę kanałów, czytaną dwoma wejściami przetwornika;
- na A2 i A3 kondensator **470 pF do masy** (rezerwuar ładunku dla przetwornika
  przy źródle ~210 kΩ); stała czasowa ładowania rezerwuaru ~0,1 ms — dlatego
  po każdej zmianie adresu obowiązuje **czas ustalania 0,7 ms (7 stałych
  czasowych)**, po którym błąd ustalania spada poniżej 0,1% (§6.2);
- zasilanie: VDD = 5 V z UNO, VEE i VSS do masy (sygnały tylko 0–5 V, ujemne
  poziomy CP na multiplekser nie trafiają), po **100 nF** odsprzęgania przy
  każdym układzie;
- rezystancja włączonego klucza CD4051BE przy 5 V to do ~1 kΩ — przy źródle
  200 kΩ i odczycie na wejście wysokoimpedancyjne bez znaczenia.

Mapa kanałów:

| Adres | Multiplekser 1 → A2 | Multiplekser 2 → A3 |
|---|---|---|
| 0 | V1 | K1 |
| 1 | V2 | K2 |
| 2 | V3 | K3 |
| 3 | ZL1 | K4 |
| 4 | ZL2 | 8V (przez dzielnik) |
| 5 | ZL3 | NTC1 |
| 6 | ICP | NTC2 |
| 7 | **detektor szczytu CT** (§4.3) | masa (samokontrola zera) |

Kanał „masa" to autotest: jeśli w logu przestaje być zerem, rejestrator sam
zgłasza własną usterkę. Kolejność ODCZYTU adresów w oprogramowaniu nie musi
być rosnąca — zostanie ustalona tak, by sąsiednie konwersje różniły się jak
najmniej napięciem (minimalizacja przesłuchu, §6.2), na podstawie poziomów
stałych zmierzonych w rekonesansie.

### 4.8 Podsłuch UART wyświetlacza DWIN T5L0 (znacznik chwili błędu)

Problem metodologiczny: przy rozwartych przekaźnikach linie K mogą się w chwili
błędu w ogóle nie zmienić — bez niezależnego znacznika „TERAZ wystąpił błąd"
korelacja „co zmieniło się pierwsze" jest nierozstrzygalna, a znacznik od
operatora ma opóźnienie sekund. Najlepszy dostępny znacznik: płytka kontrolna
komunikuje się z wyświetlaczem DWIN T5L0 po UART — w chwili błędu wysyła
polecenia przerysowania ekranu (komunikat „Overload Reminder").

Realizacja podstawowa — **licznik aktywności linii** (nie dekodowanie):
- odczep na linii nadawczej płytki kontrolnej do wyświetlacza (pole lutownicze
  złącza wyświetlacza; PRZED montażem zdzwonić i zmierzyć poziom logiczny —
  T5L0 bywa 3,3 V lub 5 V);
- tor: linia TX → 100 kΩ + 100 kΩ → klamra 2×1N4148 → pin **D2** UNO
  (pojemność wejścia ~10 pF, stała czasowa ~2 µs — wystarcza do 115 200 bodów);
- przerwanie zboczowe na D2 tylko INKREMENTUJE licznik (kilka µs na zbocze);
  licznik zboczy w każdym oknie 20 ms trafia do ramki strumienia — wybuch
  aktywności w chwili błędu daje znacznik czasu z dokładnością jednego okna;
- przy poziomie 3,3 V margines progu wejścia UNO (3,0 V przy zasilaniu 5 V)
  jest mały — w razie niepewnych odczytów linia idzie przez WOLNY drugi
  komparator LM393 (próg 1,65 V z dzielnika) zamiast wprost na D2.

Zastrzeżenie wydajnościowe: jeśli rekonesans wykaże, że ruch na linii jest
CIĄGŁY (stałe odpytywanie ekranu, dziesiątki tysięcy zboczy na sekundę),
licznik w przerwaniu zboczowym obciąży procesor ponad budżet — wtedy licznik
zastępujemy obserwacją SUMY aktywności (ta sama zasada co detektor szczytu:
dioda + kondensator + upust na wolne wejście A5) albo schodzimy do minimum
zastępczego. Pełne DEKODOWANIE ramek (SoftwareSerial — programowy port
szeregowy) jest ŚWIADOMIE wykluczone w czasie sesji: SoftwareSerial blokuje
przerwania na czas całego bajtu, co łamie limit blokady <20 µs (§6.1)
i rozsypuje akwizycję. Dekodowanie ramek DWIN (w tym prawdopodobny kod błędu)
wolno wykonać w OSOBNEJ sesji rekonesansowej, z wyłączoną akwizycją szybką.

**Minimum zastępcze (zawsze dostępne):** kamera / telefon filmujący ekran
ładowarki, z zegarem zsynchronizowanym z laptopem (kadr obejmuje ekran
i zegar na ekranie laptopa). Daje znacznik ±1 s — gorszy niż licznik
aktywności, ale wystarczający do zgrubnej korelacji i obowiązkowy jako
zapas, gdyby odczep UART okazał się niewykonalny.

### 4.9 Przydział pinów UNO (podsumowanie)

A0 = CT (szybki slot) · A1 = CP (węzeł A′) · A2 = wyjście MUX1 · A3 = wyjście
MUX2 · A4 = 1.65 (szybki slot) · A5 = rezerwa (opcja: suma aktywności UART) ·
D2 = licznik aktywności UART wyświetlacza · D4–D6 = adres multiplekserów ·
D8 = wyjście komparatora (przechwytywanie Timer1) · D13 = dioda LED „żyję".
Fizycznego przycisku „BŁĄD TERAZ" NIE MA — znacznik operatora wpisuje się
z klawiatury laptopa; skrypt wysyła bajt do UNO, a UNO wstawia znacznik do
najbliższej ramki strumienia (wspólna oś czasu, §6.3). Operator nie dotyka
niczego galwanicznie związanego z ładowarką w czasie sesji (§5.3).

## 5. Bezpieczeństwo — pomiar decyduje, nie założenie

### 5.1 Pomiar rozstrzygający charakter masy (OBOWIĄZKOWY, przed pierwszą sesją)

Jedyny dotychczasowy dowód to −3,79 V średniej (GND→PE) — to NIE rozstrzyga,
czy masa ładowarki jest związana z siecią (zasilacz pomocniczy jest odczepiony
z L-N przed przekaźnikami; jeśli to konstrukcja beztransformatorowa, masa może
siedzieć wprost na przewodzie neutralnym, a przy zamianie L/N w instalacji —
na fazie 230 V).

Krok 1 — urządzenie ODŁĄCZONE (wtyczka wyjęta, procedura §5.5): omomierzem
rezystancja GND↔N, GND↔L1/L2/L3, GND↔PE, w obu polaryzacjach sond (prostowniki
przewodzą jednokierunkowo). Wynik **poniżej 1 MΩ** do N lub L = masa związana
z siecią → reżim B.

Krok 2 — urządzenie zasilone, rejestrator jeszcze NIE podłączony: miernikiem
True-RMS (miernik pokazujący rzeczywistą wartość skuteczną, nie średnią)
napięcie GND→PE w trybie zmiennym I stałym. Wynik **powyżej 50 V** w którymkolwiek
trybie → reżim B. Inaczej → reżim A.

### 5.2 Reżimy pracy

**Reżim A — masa pływająca (potwierdzona pomiarem):** sesje dozwolone na
poniższych zasadach:
- laptop przez CAŁĄ sesję wyłącznie NA BATERII; zasilacz laptopa fizycznie
  poza stanowiskiem (nie „obok, na wszelki wypadek" — usunięty z pokoju stanowiska);
- **koniec baterii = koniec sesji**: najpierw ładowarka spod napięcia, dopiero
  potem wolno podpiąć zasilacz laptopa; sesję planować pod pojemność baterii;
- masa odniesienia: JEDEN pin GND złącza → masa UNO, jedno połączenie i nic
  więcej; **PE nigdy do masy rejestratora** (zwarcie PE–GND przez rejestrator
  puściłoby prąd wyrównawczy przez cienkie ścieżki płytki uniwersalnej
  i sfałszowało tor detekcji uziemienia ładowarki);
- UNO z płytką odczepową w zamkniętej obudowie z tworzywa (izolacyjnej),
  nietykane w czasie sesji; znaczniki błędu — wyłącznie z klawiatury.

**Reżim B — masa związana z siecią:** **sesji NIE prowadzić.** Dostępny
asortyment nie zawiera izolatora USB, a laptop na baterii NIE chroni operatora —
przy masie na potencjale sieci cały laptop (obudowa, porty) wchodzi na ten
potencjał i dotknięcie go plus czegokolwiek uziemionego zamyka obwód przez
ciało. Eskalacja do głównego inżyniera; wyjścia: izolator USB z pełną separacją
(łącznie z przetwornicą zasilania) z innego źródła zaopatrzenia albo rejestrator
w pełni bateryjny bez laptopa. To ograniczenie zapisane świadomie — żaden wariant
„na skróty" nie jest dopuszczony.

### 5.3 Organizacja stanowiska (sesje wielogodzinne, otwarta obudowa, 230/400 V)

- zasilanie badanej ładowarki przez wyłącznik różnicowoprądowy (RCD) 30 mA
  typu A na stanowisku + rozłącznik/wtyczka w zasięgu ręki operatora;
- tor mocy (zaciski 40 A) osłonięty (płyta pleksi) na czas sesji — obok wisi
  wiązka odczepów i nic nie może na te zaciski opaść; wiązka mocowana mechanicznie;
- sesje wielogodzinne wyłącznie z osłoniętym torem mocy; stanowisko oznaczone,
  osoby postronne poinformowane, że urządzenia nie wolno dotykać ani wyłączać;
- operator w czasie sesji nie dotyka: ładowarki, rejestratora, przewodów.
  Jedyny punkt styku to klawiatura laptopa — dozwolona tylko w reżimie A;
- eksperymenty czynne (§7.3) z manipulacją przy urządzeniu — wyłącznie po
  odłączeniu zasilania wg §5.5; symulator CP montuje się na wtyku pojazdowym
  przy urządzeniu wyłączonym, a próby prowadzi bez dotykania wtyku.

### 5.4 Sekwencja łączenia

1. Zdzwonienie pinów i pomiar rozstrzygający (§2, §5.1) — jednorazowo.
2. Montaż odczepów (wariant A) lub wpięcie przelotki (wariant B) — §5.5.
3. Podłączenie USB do laptopa (na baterii), start skryptu — rejestrator zasilony.
4. Dopiero teraz: zasilenie ładowarki.
5. Demontaż w odwrotnej kolejności: ładowarka spod napięcia (§5.5), potem reszta.

### 5.5 Procedura stanu beznapięciowego (przed każdą manipulacją przy złączu)

- fizyczne WYJĘCIE wtyczki (nie wyłącznik) i trzymanie jej w polu widzenia
  technika przez cały czas pracy — nikt nie załączy zasilania „bo nie wiedział";
- odczekać min. 1 minutę (kondensatory filtru przeciwzakłóceniowego RV1/RV2,
  CY2 mogą trzymać ładunek);
- pomiar braku napięcia na zaciskach wejściowych miernikiem PRZED dotknięciem
  czegokolwiek przy złączu.

## 6. Oprogramowanie

### 6.1 Architektura przerwaniowa i bilans przetwornika

Przetwornik UNO z preskalerem 64 (zegar przetwornika 250 kHz, konwersja ~52 µs,
przepustowość ~19,2 tys. konwersji/s; przy 10 bitach lekka utrata dokładności
wobec preskalera 128 — akceptowalna).

**Akwizycja działa WYŁĄCZNIE jako maszyna stanów w przerwaniu przetwornika
(ISR ADC — procedura obsługi przerwania wywoływana po każdej konwersji):**
po zakończeniu konwersji ISR zapisuje wynik do bufora pierścieniowego, wybiera
następny kanał wg harmonogramu i startuje kolejną konwersję. Pętla główna
NIE wykonuje żadnego `analogRead()` — tylko składa ramki i sączy je do portu
szeregowego. Zwykła pętla z `analogRead()` (funkcja blokująca ~112 µs) nie
utrzymałaby kadencji 250 µs — to nie jest opcja, to wymóg.

Harmonogram i JAWNY bilans zajętości przetwornika:

| Zadanie | Kadencja | Konwersje/s | Zajętość |
|---|---|---|---|
| Szybki slot: CT i 1.65 na przemian, slot co 250 µs (każda linia 2 kHz), 2 konwersje na slot (pierwsza odrzucana) | 4 000 slotów/s | 8 000 | 42% |
| Kanały multiplekserowe: ~100 obiegów/s × 8 adresów × 4 konwersje (A2, A3, po jednej odrzucanej) | co ~10 ms obieg | 3 200 | 17% |
| Poziomy CP na A1: para góra/dół wyzwalana stanem komparatora, raz na ~10 ms | 100 par/s | 400 | 2% |
| Wzorzec wewnętrzny 1,1 V (bandgap — wbudowane odniesienie napięciowe): 2 konwersje na obieg (pierwsza odrzucana) | co ~10 ms | 200 | 1% |
| **RAZEM (średnio)** | | **~11 800** | **~62%** |

Szczytowo (zbieg wtrąconej pary CP ze slotem szybkim i obiegiem) zajętość
sięga ~70–75%. **Strop projektowy: 75%** — powyżej harmonogram przestaje się
domykać; każda przyszła zmiana harmonogramu musi zmieścić się pod stropem.
Deklarowany w wersji 1 „dwukrotny zapas" był nieprawdziwy i zostaje wycofany.

Pomiar wzorca 1,1 V służy korekcji odniesienia: przetwornik odnosi wyniki do
szyny AVcc (zasilanie analogowe = 5 V z USB laptopa), która na baterii dryfuje
do ±5%. Z odczytu wzorca oprogramowanie wylicza rzeczywiste AVcc
(AVcc = 1023 × 1,1 V / odczyt) i wpisuje je do każdej ramki — analiza offline
koryguje wszystkie wartości bezwzględne. Zero dodatkowych części.

Twarde reguły implementacyjne:
- **zakaz klasy `String`** (fragmentacja pamięci) i zakaz rekurencji;
- **każda sekcja z zablokowanymi przerwaniami krótsza niż 20 µs** — dłuższa
  blokada gubi zbocze w jednobuforowym rejestrze przechwytującym ICR1
  (przy wypełnieniu 5% zbocza CP dzieli tylko 50 µs); kopiowanie buforów
  wyłącznie porcjami po kilkanaście bajtów albo przez atomowe przełączenie
  wskaźników;
- ISR przechwytywania Timer1 (zbocza CP): odczyt ICR1, zmiana aktywnego
  zbocza, zlecenie próbki A1 — kilka µs; ISR zboczy D2 (UART wyświetlacza):
  sama inkrementacja licznika;
- ilość wolnej pamięci RAM mierzona w każdym obiegu i raportowana w ramce
  (1 bajt, w krokach 8 B) — spadek poniżej 256 B to sygnał do przerwania sesji.

Bilans pamięci SRAM (2048 B): podwójny bufor ramki 2×256 B = 512 B, bufory
sprzętowego portu szeregowego 64+64 = 128 B, kolejka zdarzeń 32 B, zmienne
stanu i statystyki ~150 B, stos ~300 B — razem ~1,1 kB, zapas ~0,9 kB.
Zapas jest realny tylko przy przestrzeganiu zakazu `String`.

### 6.2 Przełączanie kanałów, ustalanie i przesłuch

- **Reguła żelazna: pierwsza konwersja po KAŻDEJ zmianie kanału (adres
  multipleksera lub przełączenie wejścia A0/A1/A2/A3/A4/bandgap) jest
  odrzucana** — kondensator próbkujący przetwornika (14 pF) wnosi ładunek
  poprzedniego kanału;
- po każdej zmianie ADRESU multipleksera: **czas ustalania 0,7 ms**
  (7 stałych czasowych węzła 470 pF przy źródle ~210 kΩ) zanim padnie
  pierwsza konwersja; w czasie ustalania przetwornik obsługuje sloty szybkie —
  czas nie jest tracony;
- kolejność odczytu kanałów ustawiona tak, by sąsiednie konwersje różniły się
  jak najmniej napięciem (ładunek wstrzykiwany przez kondensator próbkujący
  jest proporcjonalny do różnicy poziomów); dokładna kolejność — w firmware,
  na podstawie poziomów stałych z rekonesansu;
- **deklaracja dokładności: mimo powyższych zabiegów ostatnie 2–3 kroki
  przetwornika (LSB — najmłodszy bit, tu ~5 mV na krok) na kanałach
  multiplekserowych to przesłuch międzykanałowy, nie sygnał.** Analiza offline
  nie może traktować pojedynczych kroków jako anomalii; obwiednię szumu
  i przesłuchu własnego wyznacza sucha sesja (§7.1).

### 6.3 Łącze szeregowe: ciągły strumień binarny

- prędkość **250 000 bodów** (przy zegarze 16 MHz błąd prędkości 0% —
  w odróżnieniu od 115 200, gdzie wynosi ~3,5%); przepustowość ~25 kB/s;
- **strumień jest ciągły i binarny — żadnych wyzwalaczy, żadnego bufora
  przedwyzwoleniowego, żadnej kompresji stratnej.** Surowe próbki szybkie
  (4 000 × 2 B = 8 kB/s) plus dane wolne mieszczą się w łączu z zapasem;
- ramka co 20 ms (~242 B, ~12,1 kB/s = 48% łącza):
  - nagłówek synchronizacji (2 B) + licznik ramek (2 B — wykrywanie ubytków);
  - 80 próbek szybkich × 2 B (40 CT + 40 „1.65", w każdej próbce 10 bitów
    wartości + znacznik kanału + licznik modulo do kontroli ciągłości);
  - 2 komplety kanałów wolnych × 16 kanałów × 2 B (dwa obiegi multipleksera
    na ramkę — rozdzielczość zdarzeń K ~10 ms zachowana w logu);
  - CP: wypełnienie z Timer1 (2 B) + poziom góry i dołu z A1 (2×2 B);
  - wyliczone AVcc (2 B), licznik zboczy UART wyświetlacza w oknie (2 B),
    wolny RAM (1 B), suma kontrolna CRC-8 (1 B);
- **znaczniki zdarzeń w strumieniu** (krótkie ramki doklejane między ramkami
  danych, z numerem ramki i pozycją próbki — wspólna oś czasu):
  zmiana skwantowanego stanu K1–K4 (poziom przed/po), znacznik operatora
  (bajt odebrany z laptopa), restart rejestratora, przepełnienie kolejki;
- wysyłka wyłącznie z pętli głównej, sączona przez `Serial.availableForWrite()`
  — nadawanie nigdy nie blokuje i nie zatrzymuje akwizycji (bufor nadawczy
  sprzętowego portu ma tylko 64 B, więc „wyślij i czekaj" jest zakazane).

### 6.4 Skrypt na laptopie i decyzje offline

Skrypt Python: odbiera strumień, weryfikuje CRC i ciągłość liczników,
zapisuje SUROWY plik binarny (dowód pierwotny) oraz dekodowany plik CSV
(czytelny dla technika), pokazuje dyżurny podgląd (bieżące poziomy, licznik
ubytków ramek). Klawisz operatora = wysłanie bajtu znacznika do UNO (wraca
w strumieniu na wspólnej osi czasu) + wpis lokalny z czasem systemowym.

Wszystkie decyzje diagnostyczne zapadają OFFLINE, po sesji: progi i obwiednie
liczone są z sesji bazowej (§7.2), a nie zgadywane przed sesją. Dzięki temu
„kryteria wyzwalania" przestają istnieć jako problem na UNO — niczego nie
można źle ustawić i przez to przegapić.

### 6.5 Tryb rekonesansu — z kryteriami decyzyjnymi

Komenda z laptopa parkuje multiplekser na jednym wybranym kanale, próbkowanym
wtedy ~2 kHz (na przemian z CT). Zastosowanie: klasyfikacja ICP i ZL1–ZL3,
obejrzenie kształtu V1–V3, rozstrzyganie aliasów kanałów wolnych (§4.5).
Kanały o statusie NIEZNANYM dodatkowo przed pierwszym wpięciem obejrzeć
oscyloskopem wprost na pinie (przy zachowaniu §5) — rejestrator ma je
obserwować, nie odkrywać na ślepo.

Klasyfikacja wymaga BODŹCÓW — sygnał prądowy przy rozwartych przekaźnikach
nie istnieje, więc „patrzenie na płaską linię" niczego nie rozstrzyga:

| Obserwacja na ZL przy bodźcu | Wniosek |
|---|---|
| Składowa 50 Hz pojawia się już po ZAŁĄCZENIU przekaźnika K (stan C wymuszony symulatorem CP), BEZ obciążenia | 电压 = napięcie (tor mierzy napięcie za przekaźnikiem) |
| Składowa 50 Hz pojawia się dopiero przy PRZEPŁYWIE PRĄDU (stan C + obciążenie), amplituda rośnie z prądem | 电流 = prąd (tor mierzy prąd fazy) |
| Płasko przy załączonym K i przy obciążeniu | wynik NIEROZSTRZYGNIĘTY — tor nieaktywny w tym stanie albo pinout błędnie przypisany; nie zgadywać |

Bodziec obciążenia w stanie C: obciążnica albo pojazd, prąd dowolny, ale
stabilny; bez dostępu do obciążenia klasyfikacja 电流/电压 pozostaje otwarta —
wpisać „nierozstrzygnięte", NIE klasyfikować z samego poziomu stałego.
ICP: bodźce = cykl zasilania, zmiana stanu CP (A→B→C symulatorem), załączenie
przekaźników; jeśli ICP nie reaguje na żaden — status pozostaje NIEZNANY.

## 7. Metodologia sesji: sucha, bazowa, eksperymenty czynne

### 7.1 Sucha sesja na stole (OBOWIĄZKOWA przed pierwszą sesją przy ładowarce)

Wszystkie odczepy spięte do stabilnego dzielnika rezystorowego na płytce
stykowej (np. 2×10 kΩ z szyny 5 V UNO → 2,5 V na wejściach) zamiast ładowarki;
minimum 1 godzina rejestracji. Sucha sesja wyznacza i dokumentuje:
- obwiednię szumu własnego każdego kanału (bez niej „zakłócenie" z pierwszej
  sesji może być szumem rejestratora);
- rzeczywisty przesłuch międzykanałowy (skoki między kanałami o różnych
  poziomach) i stały ofset szybkiego slotu CT↔1.65 (§4.6);
- stabilność łącza: zero ubytków ramek przez godzinę, poprawne CRC;
- zużycie RAM w czasie (wyciek pamięci widać jako trend), poprawność AVcc
  z wzorca 1,1 V (porównać z multimetrem na szynie 5 V);
- działanie znaczników operatora i licznika D2 (podać na D2 przebieg testowy,
  np. z drugiego pinu UNO).
Sesja przy ładowarce bez zaliczonej suchej sesji jest niedopuszczalna —
odróżnianie zakłócenia od artefaktu własnego bez tej obwiedni nie istnieje.

### 7.2 Sesja bazowa — sprawny egzemplarz PRZED chorym

Serwis dysponuje sprawnym egzemplarzem/płytkami Q11. **Protokół wymaga sesji
referencyjnej sprawnego urządzenia PRZED sesją na egzemplarzu chorym:** ten
sam rejestrator, te same kanały, ta sama konfiguracja, minimum kilka godzin
(w tym kilka cykli zasilania). Z sesji bazowej analiza offline wyznacza
obwiednie normy: poziomy spoczynkowe CT i detektora szczytu, rzeczywisty
poziom pinu 1.65 i szyny 8V, poziomy K1–K4, zachowanie sekwencji startowej.

Bez sesji bazowej NIE WIADOMO, czy zmierzone anomalie DC (1.65 = 4,31 V;
8V = 7,45 V; K4 = 5,08 V) to usterki, czy norma tej rewizji sprzętu — a na
tym rozróżnieniu stoi cała interpretacja. Dopiero różnica chory−sprawny jest
dowodem.

### 7.3 Eksperymenty czynne — bodziec zamiast czekania

Notatki serwisowe mówią, że błąd potrafi pojawić się kilka sekund po
włączeniu. Wielogodzinne bierne czekanie jest wtedy złym protokołem — sekwencja
startowa to dane pierwszej klasy, a bodźce są tanie:

- **seryjne cykle zasilania:** np. 20 cykli (załącz → odczekaj do ustalenia
  lub błędu → wyłącz wg §5.5 → pauza), log ciągły przez całą serię; każda
  sekwencja startowa chorego porównywana z bazową; jeśli błąd wymaga
  „wygrzania", serie powtórzyć po godzinie pracy;
- **wymuszenie stanu C symulatorem CP:** wtyk pojazdowy z rezystorem 882 Ω
  i diodą (układ pojazdu wg IEC 61851; stan B = 2,74 kΩ) — pozwala badać
  zachowanie przy zamkniętych przekaźnikach bez pojazdu. UWAGA: w stanie C
  ładowarka zamyka przekaźniki i na wtyku pojawia się pełne napięcie —
  symulator montować przy urządzeniu wyłączonym (§5.5), prób nie prowadzić
  z odsłoniętym wtykiem, obciążenie podłączać tylko za zgodą głównego
  inżyniera;
- **sesja z torem CT odłączonym po stronie przekładnika:** jeśli błąd
  występuje nadal przy odłączonym (lub zwartym) wejściu CT płytki, źródło
  leży ZA torem wejściowym (odniesienie 1.65, przetwornik sterownika,
  oprogramowanie) — jedna sesja potrafi skreślić główną hipotezę. UWAGA:
  wtórnego uzwojenia przekładnika prądowego nie wolno pozostawić otwartym
  przy przepływie prądu pierwotnego (niebezpieczne napięcia) — eksperyment
  wyłącznie w stanach bez ładowania (A/B), nigdy w stanie C z obciążeniem;
- **zamiana płytek kontrolna↔moc ze sprawnym egzemplarzem — dobry KROK ZEROWY,
  prowadzony RÓWNOLEGLE z budową rejestratora:** nie wymaga żadnych zakupów,
  daje wynik binarny (błąd wędruje z płytką kontrolną albo zostaje przy
  płytce mocy) i w minuty zawęża pole poszukiwań o połowę. Dlaczego równolegle,
  a nie zamiast: zamiana nie mówi, CO na płytce jest wadliwe; błąd losowy
  może wymagać godzin reprodukcji po każdej zamianie; a ponowny montaż złącza
  zmienia styki — jeśli usterka jest stykowa, zamiana ją chwilowo „naprawi"
  i zmyli diagnozę. Wynik zamiany wybiera egzemplarz do sesji rejestratorem,
  ale rejestrator pozostaje właściwym narzędziem wskazania przyczyny.

Zasada nadrzędna: dopiero powtarzalna para „bodziec → reakcja" odróżnia
„X drgnie, WIĘC błąd" od „X drga, BO błąd". Obserwacja bierna tego nie
rozstrzyga.

## 8. Czego ten rejestrator NIE zobaczy (martwe pola)

Deklaracja wprost, żeby wynik negatywny nie został przeinterpretowany:

- **domena PE:** przewód ochronny świadomie nie jest podłączony (§5.2) —
  anomalia GND→PE = −3,79 V i cały tor detekcji uziemienia pozostają POZA
  obserwacją;
- **skoki wspólnej masy:** rejestrator pływa razem z masą ładowarki — przesuw
  całej masy względem sieci/PE jest dla niego niewidzialny;
- **częstotliwości powyżej ~0,8–1 kHz w torze CT:** stłumione i/lub
  aliasowane (§4.2); detektor szczytu wykrywa ich OBECNOŚĆ, ale nie
  częstotliwość ani kształt — klasyfikacja widmowa należy do oscyloskopu;
- **pojedyncze szpilki krótsze niż ~10 µs:** poniżej czułości detektora
  szczytu (§4.3);
- **kolejność zdarzeń poniżej ~10 ms między kanałami wolnymi:** kanały
  z obiegu multipleksera są czytane w różnych chwilach obiegu (skew rotacji)
  — rozstrzyganie „co było pierwsze" między dwoma kanałami wolnymi ma
  rozdzielczość dopiero ~10–20 ms; szybciej rozstrzygają tylko pary
  CT↔1.65 (250 µs) i cokolwiek↔wypełnienie CP;
- **alias tętnień na kanałach wolnych:** falowanie ułamków Hz na K/8V może
  być zwinięte tętnienie 50/100 Hz (§4.5) — wymaga weryfikacji rekonesansem.

**Zasada interpretacji wyniku negatywnego: cichy log ≠ czysta linia.**
Jeśli błąd wystąpił, a tor CT w logu milczy, NIE wolno ogłosić „tor CT
oczyszczony" — wolno powiedzieć: „w paśmie 0–0,8 kHz i w zakresie czułości
detektora szczytu nie zarejestrowano anomalii CT". Ciężar przesuwa się wtedy
na hipotezy konkurencyjne (1.65, domena cyfrowa sterownika, martwe pola
powyżej) i na pomiar oscyloskopem w trybie wyzwalania na szpilki.

## 9. Ograniczenia przyjęte świadomie

- Brak bufora operacyjnego na CT (niedostępny w sklepie) — skompensowany
  odczepem wysokoimpedancyjnym z rezerwuarami 1 nF + 470 pF; błąd składowej
  stałej bez znaczenia dla obserwacji odchyleń zmiennych.
- Diody 1N4148 zamiast Schottky (klamrują przy ~0,7 V zamiast ~0,3 V) —
  dodatkowy rezystor 10 kΩ za klamrą utrzymuje wejścia CD4051BE w granicach.
- Antyaliasing tylko drugiego rzędu (filtr aktywny wymagałby wzmacniacza
  operacyjnego) — pasmo wiarygodne 0–0,8 kHz zadeklarowane w §4.2 i §8,
  szybsze zjawiska pokrywa jakościowo detektor szczytu.
- Zdarzenia K z rozdzielczością ~10 ms zamiast mikrosekundowej — cena za
  odczyt analogowy, który jako jedyny czyta anomalię K4 = 5,08 V jednoznacznie.
- V1–V3 przez multiplekser to próbki chwilowe, nie pełny przebieg — pełny
  kształt pojedynczej fazy dostępny w trybie rekonesansu.
- Poziomy CP na A1 przy wypełnieniach <15% częściowo nieustalone (§4.4) —
  wypełnienie mierzy komparator, poziomy służą tylko klasyfikacji stanów.
- Podsłuch UART wyświetlacza to licznik aktywności, nie dekoder — pełne
  dekodowanie tylko w osobnej sesji rekonesansowej; minimum zastępcze: kamera.
- Reżim B (masa związana z siecią) blokuje sesje do czasu zdobycia izolatora —
  świadomie, bo dostępny asortyment nie daje bezpiecznej alternatywy.

## 10. Lista zakupów (elektronika-sklep.pl, punkt Warszawa)

| Pozycja | Ilość | Uwagi |
|---|---|---|
| CD4051BE DIP16 | 2 | 3,30 zł/szt., multipleksery |
| LM393 | 1 | 2 zł, komparator toru CP (drugi kanał = rezerwa dla UART wyświetlacza) |
| BHL20 S lub RA | 1 | 4 zł, TYLKO wariant B |
| 1N4148 | 50 | klamry + detektor szczytu + odczep UART (39 + zapas) |
| Rezystor 100 kΩ 0,25 W | 50 | łańcuchy odczepowe + stopień 2 filtru CT + detektor szczytu + odczep UART + sieć CP |
| Rezystor 120 kΩ 0,25 W | 4 | sieć CP (2×120 k = 240 k oraz 120 k do masy) + zapas |
| Rezystor 220 kΩ 0,25 W | 6 | dzielniki K1–K4, 8V + zapas |
| Rezystor 10 kΩ 0,25 W | 25 | za klamrami, izolacja A′ toru CP, próg i podciąganie komparatora, dzielnik suchej sesji |
| Rezystor 470 kΩ 0,25 W | 2 | histereza komparatora + zapas |
| Rezystor 1 MΩ 0,25 W | 2 | upust detektora szczytu + zapas |
| Kondensator ceramiczny 1 nF | 4 | stopień 1 filtru CT + węzeł 1.65 (A4) + zapas — sprawdzić na miejscu |
| Kondensator ceramiczny 47 nF | 2 | detektor szczytu + zapas; 10–100 nF też zadziała (mniejszy = czulszy na krótkie zdarzenia, krótsza pamięć) |
| Kondensator ceramiczny 470 pF | 5 | A0 (węzeł 2), A′ (CP), A2, A3 + zapas; 330–680 pF też zadziała |
| Kondensator ceramiczny 100 nF | 4 | odsprzęganie CD4051BE i LM393 — sprawdzić na miejscu |
| Płytka uniwersalna MS-TSOP1 | 1 | płytka odczepowa / przelotka |
| Płytka stykowa 170 pól | 1 | prototyp toru komparatora i sucha sesja |
| Kabelki połączeniowe M/M, F/F, M/F | po 1 kpl. | odczepy i połączenia |
| Koszulka termokurczliwa, opaski | wg potrzeb | wariant A |

Usunięte względem wersji 0: 74HC4067, ADS1115, izolator USB ADUM3160
(niedostępne w sklepie — zastąpione jak w §4.7 i §5.2), przycisk (tact switch)
i tranzystory 2N2222A/BC547C (niepotrzebne po zmianach §4.9 i §4.2).
Wartości kondensatorów są niekrytyczne — przy braku dokładnej wartości brać
najbliższą z półki (wyjątek: 470 pF przy A0/A2/A3 nie zwiększać powyżej
~1 nF, bo wydłuża ustalanie).

## 11. Otwarte kwestie do kolejnej iteracji

- wynik pomiaru rozstrzygającego §5.1 (decyduje o reżimie A/B);
- poziom logiczny (3,3/5 V), prędkość i charakter ruchu (ciągły/zdarzeniowy)
  linii UART wyświetlacza — decyduje o formie podsłuchu (§4.8);
- klasyfikacja ICP i ZL1–ZL3 wg tabeli §6.5 (wymaga symulatora CP,
  a dla 电流/电压 — obciążenia w stanie C);
- sesja bazowa sprawnego egzemplarza (§7.2) — rozstrzygnie, czy 1.65 = 4,31 V,
  8V = 7,45 V i K4 = 5,08 V to usterki, czy norma rewizji;
- ostateczna kolejność odczytu kanałów multipleksera (minimalizacja przesłuchu)
  po zmierzeniu poziomów w rekonesansie;
- pojemność baterii laptopa vs planowana długość sesji — rozstrzygana przy
  okazji suchej sesji (§7.1);
- wynik zamiany płytek kontrolna↔moc (krok zerowy §7.3) — wybór egzemplarza
  i płytki do pierwszej sesji rejestratorem.

## Dziennik iteracji

**Iteracja 1 (2026-08-28).** Wprowadzono niemal wszystkie uwagi obu recenzji:
odczepy przeprojektowano z 10 kΩ na 2×100 kΩ z klamrami 1N4148 i rezystorem
10 kΩ za klamrą (obciążenie torów wysokoimpedancyjnych spadło z ~110 µA do
pojedynczych µA, scenariusz 230 V daje 1,15 mA i 0,13 W na rezystor), tor CP
dostał przeliczoną sieć trzyrezystorową (±12 V → 0–3,64 V) z komparatorem
w dopuszczalnym zakresie wejściowym i progiem −6 V, K1–K4 przeniesiono na
odczyt analogowy przez multiplekser (anomalia K4 = 5,08 V → 2,66 V czytelna
wprost), a budżety przetwornika i łącza policzono jawnie (250 000 bodów, bufor
przedwyzwoleniowy 0,2 s jako limit SRAM). Pinout zastąpiono potwierdzonym
zdjęciem strony lutowania (bez N_PE — znika sprzeczność obu recenzji), PE
odcięto od masy rejestratora, dodano pomiar rozstrzygający charakter masy,
dwa reżimy pracy, organizację stanowiska z RCD 30 mA i procedurę stanu
beznapięciowego, a fizyczny przycisk zastąpiono znacznikiem z klawiatury.
Wpięcie opisano w dwóch wariantach zgodnie z ustaleniami głównego inżyniera:
rekomendowane odczepy lutowane od tyłu obudowy (A) i zapasowa przelotka BHL20 (B);
części niedostępne w elektronika-sklep.pl usunięto (74HC4067 → 2×CD4051BE,
ADS1115 → wystarcza przetwornik UNO). Odrzucono żądanie obowiązkowego izolatora
USB ADUM3160 (recenzje A2/A7/B8) jako niewykonalne zakupowo — w zamian pomiar
masy stał się bramką decyzyjną, a przy masie związanej z siecią sesje są wprost
zakazane, co zachowuje intencję recenzentów bez fikcji „izolacji". Odrzucono
też bufor operacyjny na CT i diody Schottky (B6, A5/B1) jako niedostępne —
zastąpione odpowiednio odczepem 200 kΩ z kondensatorem 470 pF i parą
1N4148 + 10 kΩ, o skutkach opisanych w §7.

**Iteracja 2 (2026-08-28, finalna).** Najgłębsza zmiana jest programowa:
wyzwalacze, progi i bufor przedwyzwoleniowy usunięto w całości na rzecz
ciągłego binarnego strumienia surowych próbek (8 kB/s szybkich w łączu
25 kB/s) z decyzjami offline — jedna decyzja zamyka naraz zarzuty o brak
kryteriów wyzwalania, stratną kompresję bufora 8-bitowego, dziurę w akwizycji
podczas zrzutu i ciasnotę SRAM (A1/A2/A6/A7/B7). Akwizycję przepisano na
maszynę stanów w przerwaniu ADC z jawnym bilansem (~62% średnio, strop 75% —
wycofano fałszywy „dwukrotny zapas"), limitem blokady przerwań <20 µs,
zakazem `String` i cykliczną korekcją odniesienia wzorcem 1,1 V (A1/A7/A8/A10/B8).
Metodologię uzupełniono o to, czego pasywny plan nie miał: detektor szczytu na
CT (B1), szybki slot 2 kHz dla pinu 1.65 jako równorzędnej hipotezy (B4),
znacznik chwili błędu z aktywności UART wyświetlacza DWIN z kamerą jako minimum
(B3), obowiązkową suchą sesję i sesję bazową sprawnego egzemplarza przed chorym
(B5/B8), eksperymenty czynne z uzasadnieniem zamiany płytek jako kroku zerowego
(B6), tabelę decyzyjną rekonesansu (B9) oraz sekcję martwych pól z zasadą
„cichy log ≠ czysta linia" (B10/A9). W sprzęcie: filtr CT dwustopniowy
1 nF + 470 pF z uczciwą deklaracją pasma 0–0,8 kHz (B2/A9), kondensator toru CP
przeniesiony za rezystor 10 kΩ z odgałęzieniem komparatora przed nim — błąd
wypełnienia spada z ~1,6% poniżej 0,1% (A5), próbki A1 wyzwalane stanem
komparatora zamiast ślepego max/min (A4), ustalanie multipleksera wydłużone do
0,7 ms z deklaracją przesłuchu 2–3 LSB i kolejnością kanałów minimalizującą
skoki (A3). Odrzucono: pełne dekodowanie UART wyświetlacza w czasie sesji
(SoftwareSerial blokuje przerwania na całe bajty — łamie limit 20 µs;
zastąpione licznikiem zboczy i osobną sesją dekodującą), kompresję bufora do
int8 ze wzmocnieniem ×4 (A2 — bezprzedmiotowa po przejściu na strumień ciągły
10-bitowy) oraz podnoszenie rzędu filtru powyżej drugiego (wymagałoby
wzmacniacza operacyjnego, niedostępnego zakupowo — lukę pokrywa detektor
szczytu plus deklaracja martwych pól).
