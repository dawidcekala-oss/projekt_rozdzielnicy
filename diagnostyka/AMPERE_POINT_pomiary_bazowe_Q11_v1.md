# Kampania pomiarów bazowych Q11 — zdrowy egzemplarz + porównanie z uszkodzonymi (v1)

**AMPERE POINT · wątek diagnostyki · 2026-08-28 · bez zakupów: multimetr (UT890C), mini
oscyloskop, przewody z pinami, gama rezystorów, diody z płytek uszkodzonych**

Cel: (1) zdjąć pełny OBRAZ WZORCOWY złącza międzypłytkowego zdrowej Q11 — do niego będą
porównywane wszystkie egzemplarze uszkodzone; (2) wykonać ukierunkowane pomiary
porównawcze pod znane anomalie sprawy „klejdysz". Wyniki wpisywać ręcznie w karty
z tego dokumentu, karty sfotografować — ze skanów powstanie dokumentacja
`pomiary_Q11_zdrowa` (przepisywanie po stronie Claude).

Punkt odniesienia WSZYSTKICH pomiarów napięć: **skrajny pin GND złącza na płytce
kontrolnej** (ten sam, którego użyto przy egzemplarzu „klejdysz" — porównywalność 1:1).
Pinout złącza (potwierdzony, od strony lutowania):
Rząd 1: `PE · NTC1 · ICP · 8V · K1 · K2 · K3 · K4 · 1.65 · CP`
Rząd 2: `GND · GND · CT · NTC2 · ZL3 · ZL2 · ZL1 · V1 · V2 · V3`

## 0. Zasady bezpieczeństwa (obowiązują przy każdej sekcji)

- Manipulacje przy złączu (podpinanie sond na stałe, lutowanie, symulator CP) —
  wyłącznie przy WYJĘTEJ wtyczce, po odczekaniu 1 min i pomiarze braku napięcia.
- Pomiary pod napięciem: tylko sondami trzymanymi w rękach LUB podpiętymi wcześniej
  na wyłączonym urządzeniu; tor mocy (zaciski 40 A) osłonięty; zasilanie stanowiska
  przez RCD 30 mA; jedna ręka przy pomiarach pod napięciem, druga z dala od metalu.
- **Sekcja 2.0 (charakter masy) MUSI być wykonana jako pierwsza** — dopóki nie
  przejdzie, nie wolno podpinać oscyloskopu zasilanego z laptopa ani niczego
  z masą wspólną. Mini oscyloskop na własnej baterii; jeśli zasilany z laptopa —
  laptop przez całą sesję na baterii.
- Krokodylek masy oscyloskopu ZAWSZE na pin GND złącza — nigdy na PE, nigdy na
  zaciski toru mocy.

## 1. Pomiary beznapięciowe zdrowego egzemplarza (wtyczka wyjęta)

Multimetr w trybie rezystancji; przy pinach z elektroniką odczyt może pływać
(kondensatory) — notować wartość po ustabilizowaniu i kierunek dryfu (↑/↓).
Pomiary oznaczone „2×" wykonać w OBU polaryzacjach sond (prostowniki przewodzą
jednokierunkowo — różnica między polaryzacjami też jest informacją).

**KARTA 1A — charakter masy i sieci (rozstrzyga reżim pracy):**

| Pomiar | Polaryzacja 1 [kΩ/MΩ] | Polaryzacja 2 | Uwagi |
|---|---|---|---|
| GND ↔ N (zacisk wejściowy) 2× | ________ | ________ | <1 MΩ = masa związana z siecią → reżim B! |
| GND ↔ L1 2× | ________ | ________ | |
| GND ↔ L2 2× | ________ | ________ | |
| GND ↔ L3 2× | ________ | ________ | |
| GND ↔ PE 2× | ________ | ________ | |
| L1 ↔ N (wtyczka, dla odniesienia) | ________ | — | norma serii: ~120 kΩ (dzielnik pomiaru sieci) |

**KARTA 1B — rezystancje pinów złącza względem GND (zdrowy wzorzec):**

| Pin | R do GND [kΩ] | Pin | R do GND [kΩ] |
|---|---|---|---|
| CT | ________ | K1 | ________ |
| 1.65 | ________ | K2 | ________ |
| CP | ________ | K3 | ________ |
| 8V | ________ | K4 | ________ |
| NTC1 | ________ | ZL1 | ________ |
| NTC2 | ________ | ZL2 | ________ |
| V1 | ________ | ZL3 | ________ |
| V2 | ________ | ICP | ________ |
| V3 | ________ | PE | ________ |

Ta karta to „odcisk palca" płytki: każdy uszkodzony egzemplarz mierzony tak samo
pokaże różnice bez podawania napięcia. Szczególnie ważne: **K4 vs K1–K3** (czy na
zdrowym wszystkie cztery są identyczne?) oraz **1.65** (czy tor odniesienia ma
inną rezystancję na klejdyszu?).

## 2. Pomiary pod napięciem — stan A (bez pojazdu), zdrowy egzemplarz

### 2.0 Charakter masy pod napięciem (bramka decyzyjna)

Miernikiem True-RMS, rejestrator/oscyloskop jeszcze NIE podłączony:

| Pomiar | Tryb DC [V] | Tryb AC [V] | Werdykt |
|---|---|---|---|
| GND → PE | ________ | ________ | >50 V w którymkolwiek = STOP, reżim B |

(Na klejdyszu zmierzono −3,79 V DC — wartość zdrowego rozstrzygnie, czy to anomalia.)

### 2.1 KARTA 2A — napięcia stałe wszystkich pinów (kolejność jak karta klejdysza)

Multimetr DC, czarna sonda na skrajnym GND:

| Pin | Zdrowy [V] | Klejdysz (zmierzone) | Pin | Zdrowy [V] | Klejdysz |
|---|---|---|---|---|---|
| V3 | ________ | 0,56 | 1.65 | ________ | **4,31** |
| V2 | ________ | 0,56 | K4 | ________ | **5,08** |
| V1 | ________ | 0,56 | K3 | ________ | 7,45 |
| ZL1 | ________ | 3,298 | K2 | ________ | 7,45 |
| ZL2 | ________ | 3,298 | K1 | ________ | 7,45 |
| ZL3 | ________ | 3,298 | 8V | ________ | 7,45 |
| NTC2 | ________ | 1,772 | ICP | ________ | 0 |
| CT | ________ | 1,651 | NTC1 | ________ | 1,78 |
| CP | ________ | 11,99 | GND→GND | 0 (kontrola) | 0 |

### 2.2 KARTA 2B — składowa zmienna (ten sam układ, multimetr w trybie AC)

Tryb AC pokazuje to, czego tryb DC nie widzi — tętnienia i zakłócenia (True-RMS
UT890C mierzy je uczciwie). Na klejdyszu NIE wykonano — na zdrowym robimy komplet,
przy kolejnej sesji z klejdyszem uzupełnimy porównanie:

| Pin | Zdrowy AC [mV] | Pin | Zdrowy AC [mV] |
|---|---|---|---|
| CT | ________ | K4 | ________ |
| 1.65 | ________ | K1 | ________ |
| 8V | ________ | V1 | ________ |
| CP | ________ (uwaga: w stanie A powinno być ~0 — brak PWM) | NTC1 | ________ |

### 2.3 Częstotliwość na CP (tryb Hz multimetru)

Stan A: brak PWM (miernik pokaże 0 lub śmieci) — zanotować: ________
(Pomiar właściwy w stanach B/C — sekcja 4.)

## 3. Oscyloskop — kształty przebiegów zdrowego egzemplarza (stan A)

Masa oscyloskopu na GND złącza. Dla każdego punktu spisać: wartość
międzyszczytową (Vpp), częstotliwość dominującą, opis kształtu (albo zdjęcie
ekranu — preferowane). Podstawa czasu startowa: 5 ms/dz, potem 200 µs/dz.

**KARTA 3 — obserwacje oscyloskopowe:**

| Punkt | Vpp [mV] | f [Hz] | Kształt / zdjęcie nr | Na co patrzeć |
|---|---|---|---|---|
| CT | ________ | ________ | ________ | czy czysta linia przy offsetcie ~1,65 V? każde tętnienie 50 Hz i szpilki notować — to WZORZEC dla głównego podejrzanego |
| 1.65 | ________ | ________ | ________ | ma być „sznurek" — każda zmienność to odkrycie |
| 8V | ________ | ________ | ________ | tętnienie zasilacza pomocniczego (norma: dziesiątki mV) |
| K4 | ________ | ________ | ________ | porównać z K1 — mają wyglądać identycznie |
| K1 | ________ | ________ | ________ | |
| V1 | ________ | ________ | ________ | kształt sieci 50 Hz z dzielnika 1 MΩ |
| CP | ________ | ________ | ________ | stan A: gładkie +12 V |
| ICP | ________ | ________ | ________ | rekonesans: płaski czy aktywny? |
| ZL1 | ________ | ________ | ________ | rekonesans |

### 3.1 Sekwencja startowa (×3 powtórzenia)

Oscyloskop na **CT**, wyzwalanie pojedyncze (single) albo obserwacja ciągła;
włączyć zasilanie ładowarki i obserwować pierwsze ~10 s. Powtórzyć z sondą na
**1.65** i na **8V**. Notować: jak długo szyny wstają, czy są oscylacje,
przerzuty, zapadki. (Klejdysz: w kilka sekund po starcie krótki komunikat
nadnapięciowy, potem trwały przeciążeniowy — sekwencja startowa zdrowego to
wzorzec, z którym to porównamy.)

| Start # | CT — obserwacje | 1.65 — obserwacje | 8V — obserwacje |
|---|---|---|---|
| 1 | ________ | ________ | ________ |
| 2 | ________ | ________ | ________ |
| 3 | ________ | ________ | ________ |

## 4. Stany B i C — symulator CP z posiadanych części

Symulator obwodu pojazdu wg IEC 61851 (montaż na wtyku Type 2 przy WYŁĄCZONYM
urządzeniu; między CP a PE wtyczki pojazdowej):

```
CP ──[dioda krzemowa]──┬──[2,7 kΩ]──── PE      ← stan B (norma: 2,74 kΩ)
                       └──[wyłącznik/zworka]──[1,3 kΩ]── PE   ← domknięcie = stan C
```

- **Dioda: NIE używać LED** (spadek ~2 V przekłamie poziomy). Diodę krzemową
  (1N400x/1N4148/prostownicza) wylutować z płytki uszkodzonej Q11 — na płytce
  kontrolnej widoczne D12/D20, na płytce mocy sekcja zasilacza. Sprawdzić
  diodę multimetrem (spadek 0,5–0,7 V) przed użyciem.
- Rezystory z gamy: 2,7 kΩ (zamiast 2,74 kΩ — tolerancja okien stanów wg IEC
  wystarcza) i 1,3 kΩ (lub 1,2 kΩ + 100 Ω szeregowo).
- W stanie C ładowarka ZAMKNIE przekaźniki i poda napięcie na wtyk — wtyk
  w czasie prób osłonięty, nic nie podłączać do toru mocy.

**KARTA 4 — pomiary w stanach B i C (zdrowy):**

| Pomiar | Stan B | Stan C | Na co patrzeć |
|---|---|---|---|
| CP: multimetr DC [V] | ________ | ________ | średnia PWM — wartość niższa niż 9/6 V (to norma trybu DC przy PWM) |
| CP: multimetr Hz | ________ | ________ | oczekiwane ~1000 Hz |
| CP: oscyloskop — góra impulsu [V] | ________ | ________ | ~9 V (B) / ~6 V (C) |
| CP: oscyloskop — dół impulsu [V] | ________ | ________ | ~−12 V |
| CP: wypełnienie [%] (z ekranu oscyloskopu) | ________ | ________ | prąd oferowany = wypełnienie × 0,6 A |
| K1–K4: DC po przejściu do C [V] | ________ | ________ | które K zmieniają poziom przy zamykaniu przekaźników i NA JAKI |
| CT: DC + AC po zamknięciu przekaźników (bez obciążenia) | ________ | ________ | czy sam klik przekaźników zaburza tor CT? |
| 1.65: DC w B i C | ________ | ________ | czy odniesienie stoi nieruchomo niezależnie od stanu |
| ZL1–ZL3: DC w C (bez obciążenia) | ________ | ________ | rekonesans: reagują na załączenie przekaźnika? (jeśli tak → mierzą napięcie, nie prąd) |
| ekran ładowarki: komunikaty | ________ | ________ | zdrowy wzorzec zachowania |

## 5. Spis ukierunkowanych pomiarów porównawczych (zdrowy ↔ klejdysz ↔ pozostałe uszkodzone)

Kolejność od najbardziej rozstrzygających. Każdy pomiar wykonywać IDENTYCZNIE
na obu egzemplarzach (ten sam punkt odniesienia, ten sam tryb miernika).

| # | Pomiar | Zdrowy | Klejdysz | Interpretacja różnicy |
|---|---|---|---|---|
| P1 | **pin 1.65: DC** | ________ | 4,31 V | jeśli zdrowy ≈1,65 V → klejdysz ma uszkodzony tor odniesienia = najkrótsza droga do przyczyny „Overload"; jeśli zdrowy też ≈4,3 V → nazwa pinu myli i hipoteza odniesienia upada |
| P2 | **8V: DC** | ________ | 7,45 V | zdrowy ≈8,0 V → zaniżona szyna klejdysza (zasilacz pomocniczy); zdrowy ≈7,45 V → norma konstrukcji |
| P3 | **K4 vs K1–K3: DC** | ________ | K4=5,08, reszta 7,45 | zdrowy z czterema równymi → coś obciąża K4 klejdysza (tor sterowania przekaźnika N lub L3 — wg architektury K1..K4 = N,L1,L2,L3) |
| P4 | **CT: oscyloskop, Vpp i kształt** | ________ | do zmierzenia | zakłócenia obecne tylko na klejdyszu → tor CT potwierdzony jako źródło; obecne na obu → norma konstrukcji, szukać dalej |
| P5 | **1.65: oscyloskop** | ________ | do zmierzenia | drgania odniesienia tylko na klejdyszu → hipoteza pływającego odniesienia rośnie |
| P6 | **V1–V3: DC** | ________ | 0,56 V | trzy identyczne 0,56 V na obu → konstrukcja; różnica → wspólny tor pomiaru napięć |
| P7 | **GND→PE: DC i AC** | ________ | −3,79 V DC | różnica → tor detekcji uziemienia / sprzężenie z siecią |
| P8 | **sekwencja startowa na CT i 1.65 (oscyloskop)** | karta 3.1 | do zmierzenia | klejdysz: czy anomalia pojawia się PRZED komunikatem nadnapięciowym/przeciążeniowym — kolejność zdarzeń wskazuje przyczynę |
| P9 | **karta 1B (rezystancje beznapięciowe)** | karta 1B | do zmierzenia | różnice rezystancji lokalizują uszkodzenie bez zasilania — najbezpieczniejszy pomiar różnicowy |
| P10 | **ZL1–ZL3, ICP: DC + oscyloskop** | ________ | 3,298 / 0 | rekonesans znaczenia pinów; różnice między egzemplarzami = dodatkowy trop |
| P11 | **ekran: sekwencja komunikatów przy starcie** | ________ | nadnapięciowy→przeciążeniowy | czy zdrowy też mryga czymkolwiek przy starcie |
| P12 | **stan B/C: czy klejdysz przechodzi do C i klika przekaźnikami** | karta 4 | do zmierzenia | notatki serwisowe: w okresach „częściowej sprawności" klika, ale napięcia na wyjściu brak — potwierdzić i zmierzyć wtedy K1–K4 oraz zestyki |
| P13 | **pozostałe uszkodzone Q11: karty 1B + 2A** | — | — | czy anomalie klejdysza (1.65, K4) powtarzają się w innych egzemplarzach z „Overload" — wspólny mechanizm usterki serii czy przypadek jednostkowy |

## 6. Opcja bez zakupów: „rejestrator zerowy" na Arduino UNO

Posiadane UNO + rezystory z gamy wystarczą na uproszczony, 4-kanałowy rejestrator
(bez multiplekserów i komparatora): CT→A0, 1.65→A1, 8V→A2 (przez dzielnik z gamy),
K4→A3 (przez dzielnik), każdy tor przez 2×100 kΩ szeregowo (ochronę zapewnia
rezystor + wewnętrzne diody zabezpieczające UNO — przy 200 kΩ prąd awaryjny
1,15 mA mieści się w ich limicie). Strumień CSV do laptopa (na baterii), sesje
wielogodzinne na klejdyszu w oczekiwaniu na błąd. To nie zastępuje pełnego
rejestratora (brak detektora szczytu, wolniejsze próbkowanie, 4 kanały zamiast 18),
ale pozwala zacząć łapać błąd od razu. Firmware i skrypt — po decyzji (praca po
stronie Claude, zero części).

## 7. Organizacja wyników

- Karty wypełniać długopisem, jedna karta = jedno zdjęcie (czytelne, prostopadle).
- Zdjęcia do: `Q11_architektura\pomiary_Q11_zdrowa\` (karty 1A–4) oraz
  `Q11_architektura\pomiary_Q11_klejdysz\` (pomiary porównawcze P1–P12);
  zdjęcia ekranu oscyloskopu numerować i wpisywać numer w kartę.
- Po sesji: przekazać skany — dokumentacja wzorcowa zdrowej ładowarki
  (`pomiary_Q11_zdrowa_v1`) powstanie z przepisania kart, z tabelami
  porównawczymi i wnioskami.
