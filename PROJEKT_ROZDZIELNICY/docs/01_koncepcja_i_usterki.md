# 01. Koncepcja stanowiska i macierz usterek

Status: SZKIC do zatwierdzenia (etap 0). Wszystko oznaczone **[?]** wymaga Twojego potwierdzenia.

## 1. Co budujemy (założenia robocze)

Rozdzielnica testowo-szkoleniowa Ampere Point: zasila ładowarkę AC (wallbox 3-fazowy
do 32 A/fazę, czyli 22 kW, oraz ładowarkę przenośną 1-fazową 16 A) i pozwala z ekranu
dotykowego włączać typowe błędy instalacyjne, żeby pokazać / sprawdzić, jak reaguje
ładowarka, zabezpieczenia i moduł DLB.

Założenia, które przyjąłem bez zdjęć obecnej rozdzielnicy **[?]**:

| # | Założenie | Dlaczego tak | Co zmienia, jeśli jest inaczej |
|---|-----------|--------------|-------------------------------|
| A1 | Badanym urządzeniem (DUT) jest ładowarka EV, nie dowolny odbiornik | Ampere Point = ładowarki, DLB, tester AmpCheck | Lista usterek i progi napięć |
| A2 | Tor mocy ma przenosić realny prąd ładowania do 3×32 A | Wallbox WB500 22 kW ma 32 A | Przy 16 A: mniejszy transformator, lżejsze styczniki, mniejsza obudowa |
| A3 | Rozdzielnica wisi na ścianie (nie jest mobilna) | Słowo "rozdzielnica", przekładniki DLB na przewodach zasilających | Wersja mobilna = inna obudowa (stelaż, kółka) |
| A4 | Sterowanie: ESP32 z ekranem dotykowym jako HMI, wyjścia przekaźnikowe na posiadanych Shelly | Twoje wytyczne pkt 2, 3 i uwaga o Shelly | Jeśli Shelly to tylko pomiar (3EM), wyjścia robimy na modułach przekaźnikowych |
| A5 | Usterki muszą być odwracalne i nie mogą zniszczyć DUT | Stanowisko ma służyć wielokrotnie | Jeśli dopuszczasz "test niszczący" (np. 400 V na 230 V), dodamy osobny, blokowany tryb |
| A6 | Zasilanie stanowiska: 3×400/230 V TN-S (lub TN-C-S), 5-żyłowo, zabezpieczenie przed rozdzielnicą min. 40 A | Standard w PL | Przy TT inne uwagi o PE |

## 2. Macierz usterek do zasymulowania

Oznaczenia: **K** = stycznik/przekaźnik sterowany, **R** = rezystor, **T1** = transformator
szeregowy. "Reakcja" = czego oczekujemy od ładowarki / zabezpieczeń (wg IEC 61851-1:
ładowarka ma pracować w zakresie ±10 % Un, czyli 207–253 V, i przerwać ładowanie poza nim;
wiele wallboxów dodatkowo wykrywa brak PE / uszkodzenie PEN i złą kolejność faz).

| ID | Błąd instalatora | Jak symulujemy w rozdzielnicy | Oczekiwana reakcja | Ryzyko / blokady |
|----|------------------|-------------------------------|--------------------|------------------|
| F1 | Brak PE (nieprzykręcony/urwany przewód ochronny) | K_PE (stycznik 2P 40 A, oba bieguny równolegle) w torze PE wyjścia, normalnie zamknięty w trybie testu; otwarcie = brak PE. Równolegle **ręczny wyłącznik kluczykowy "PE STAŁE"**, który na stałe mostkuje K_PE poza trybem testu | Ładowarka powinna odmówić ładowania / zgłosić błąd PE (pomiar N-PE lub referencja CP) | Przełączanie PE jest normalnie zabronione; dopuszczalne tylko w trybie testu, z kluczykiem, oznakowaniem i E-STOP |
| F2 | Złe uziemienie (duża impedancja pętli) | Przy otwartym K_PE zamykamy K_PEr (przekaźnik 16 A) z **R 100 Ω / 50 W** w torze PE | Ładowarka z kontrolą PE może nie wykryć; pokazuje różnicę "brak" vs "słabe" PE | R grzeje tylko przy przepływie prądu upływu, bezpieczne |
| F3 | Napięcie na PE (PE "pod napięciem" przez uszkodzoną izolację) **[?]** | Przy otwartym K_PE: K_PEu + **R 220 kΩ** z L1 na PE wyjścia (~1 mA) | Ładowarki z pomiarem napięcia PE-N zgłaszają błąd | Prąd ograniczony do ~1 mA, bez zagrożenia; do decyzji, czy w ogóle potrzebne |
| F4 | Przerwa w N | K_N (2P 40 A, bieguny równolegle) w torze N, normalnie zamknięty | 1-fazowo: zanik zasilania ładowarki. 3-fazowo: asymetria napięć (przesunięcie punktu zerowego) | Przy niesymetrycznym obciążeniu napięcie na jednej fazie może przekroczyć 253 V – dopuszczamy tylko bez dodatkowych odbiorników 1-faz. |
| F5 | Zamiana N z PE na zaciskach urządzenia | Para K_NPEa / K_NPEb (2× stycznik 2P 40 A) krzyżująca N i PE wyjścia; blokada wzajemna | Prąd wraca przez PE: RCD "instalacyjny" 30 mA wyzwala natychmiast pod obciążeniem | Nigdy oba styczniki jednocześnie (blokada sprzętowa stykami NC + firmware) |
| F6 | Mostek N-PE przy urządzeniu (instalator "dorobił" TN-C) | K_B (przekaźnik 16 A) łączy N i PE wyjścia | Część prądu wraca przez PE → RCD wyzwala | Prąd przez przekaźnik do chwili zadziałania RCD (ms) |
| F7 | Zamiana L z N (gniazdo 1-fazowe) | Para K_LNa / K_LNb (2× stycznik 2P 25 A) na odpływie 1-fazowym | Ładowarka przenośna z kontrolą polaryzacji zgłasza błąd | Blokada wzajemna |
| F8 | Zanik jednej fazy | K_L3 (2P 40 A) w torze L3, normalnie zamknięty | Wallbox 3-faz. przechodzi na 1-fazę lub zgłasza błąd | – |
| F9 | Zła kolejność faz (L1-L3-L2) | **Para styczników nawrotnych 3P 32 A (AC-3) z blokadą mechaniczną** (jak do zmiany kierunku silnika): K_SEQa = kolejność zgodna, K_SEQb = L2↔L3. Pełni też rolę głównego stycznika załączającego wyjście | Wallbox zgłasza błąd kolejności faz (jeśli ją kontroluje) | Blokada mechaniczna + elektryczna; przełączanie tylko przy wyłączonym wyjściu |
| F10a | Zbyt niskie napięcie | **T1: transformator toroidalny 230 V / 2×24 V** o prądzie wtórnym ≥ prąd obciążenia, uzwojenie wtórne **w szereg z L1** wyjścia. K_Tbyp (bocznik, normalnie zamknięty), K_Tbuck (polaryzacja "odejmij") → 206 V (−24 V) lub 182 V (−48 V przy obu uzwojeniach) | Poniżej 207 V ładowarka ma przerwać ładowanie | Kolejność łączeń: najpierw zamknąć gałąź T1, potem otworzyć bocznik (never-both). Zwarcie wtórnego przy obu zamkniętych → wyłącznik B6 pierwotnego |
| F10b | Zbyt wysokie napięcie | Jak wyżej, K_Tboost → 254 V (+24 V) lub 278 V (+48 V) **[?]** | Powyżej 253 V ładowarka ma przerwać ładowanie | +48 V = 278 V może uszkodzić tanią elektronikę DUT; proponuję limit 254–265 V (uzwojenie 2×20 V zamiast 2×24 V daje 250/270 V) – do decyzji |
| F11 | Luźny styk (iskrzenie, przerywanie) | K_INT (2P 40 A) w torze L1; firmware przerywa losowo 50–500 ms przez ograniczony czas (np. 20 cykli) | Ładowarka restartuje / zgłasza błąd; DLB widzi skoki | Zużycie styków – limit cykli; alternatywnie SSR 40 A z radiatorem (bez łuku) |
| F12 | Przepalony / wysokorezystancyjny styk, zbyt cienki przewód | **R 0,5 Ω / 300 W** (rezystor w obudowie Al na radiatorze) w torze L1, bocznikowany K_R (normalnie zamknięty). Przy 16 A: spadek 8 V, 128 W; przy 32 A: 16 V, 512 W (!) | Spadek napięcia pod obciążeniem, nagrzewanie – do pokazania kamerą termowizyjną | Limit czasu 60 s w firmware + termostat 90 °C na radiatorze przerywający usterkę sprzętowo; przy 32 A tylko krótkie impulsy **[?]** |
| F13 | Brak RCD w obwodzie ładowarki **[?]** | RCD "instalacyjny" 30 mA typ A 4P 40 A w torze; para K_RCDin / K_RCDbyp (2× 4P 40 A) wybiera "przez RCD" / "z pominięciem". Przed nim zawsze RCD "strażnik" 300 mA typ S (selektywny) chroniący stanowisko | Przy F5/F6/F14 bez RCD: nic nie wyzwala, prąd płynie przez PE – pokaz, dlaczego RCD jest obowiązkowy | Strażnik 300 mA zostaje zawsze w torze |
| F14 | Prąd upływu AC ~30 mA (uszkodzona izolacja) | K_LK + **R 6,8 kΩ / 10 W** z L1 na PE wyjścia (34 mA) | RCD 30 mA wyzwala (test działania), strażnik 300 mA nie | – |
| F15 | Upływ DC 6 mA (test RDC-DD ładowarki) | **Nie da się z rozdzielnicy** – trzeba wstrzyknąć za czujnikiem ładowarki (po stronie pojazdu). To robi tester AmpCheck | – | Informacyjnie |
| F16 | Przerwa PEN w sieci TN-C (najgroźniejsze: PE i N "pływają", PE przyjmuje potencjał fazy przez odbiornik) | Kombinacja F1 + F4 + F6 (PE i N odłączone, zmostkowane przy urządzeniu) | Wallboxy z detekcją PEN (UK, część EU) odmawiają ładowania; pozostałe pracują, a obudowa auta ma potencjał | **Najbardziej niebezpieczna kombinacja** – tylko po 2-krotnym potwierdzeniu na HMI, z sygnalizacją świetlną, bez dotykania DUT |
| F17 | Przeciążenie / zły dobór zabezpieczenia | Informacyjnie: pokaz na liczniku prądu, że ładowarka 32 A jest za wyłącznikiem B16 – wymaga wymiennego MCB w gnieździe **[?]** | Wyłączenie po charakterystyce B/C | Opcja: mały "slot" na MCB wymienny ręcznie |

Inne błędy spotykane w instalacjach ładowarek (do dyskusji, które warto pokazać): brak
oddzielnego obwodu dla ładowarki, wspólny N z innymi obwodami, aluminium pod zaciskiem
Cu, niedokręcone zaciski (= F11/F12), brak ogranicznika przepięć (SPD), RCD typu AC zamiast
A/B (nie da się zasymulować inaczej niż fizyczną wymianą aparatu), przekładniki DLB na złych
przewodach lub odwrócone (łatwe do pokazania: przekładnik na przewodzie wyjściowym zamiast
zasilającym, albo odwrócony kierunek – to też "usterka" dla DLB!) **[?]**.

## 3. Wnioski z macierzy wpływające na obudowę

* Aparatura DIN (zabezpieczenia + styczniki modułowe + przekaźniki + Shelly + zasilacz) to
  rząd wielkości **80–110 modułów** (szczegóły w `02_dobor_obudowy.md`).
* Elementy **poza szyną DIN**: para styczników nawrotnych 3P 32 A (ok. 100×100×90 mm),
  transformator toroidalny 400–800 VA (Ø 120–150 mm, 3–6 kg), rezystor mocy z radiatorem
  i wentylatorem (ok. 150×100×80 mm), ewentualny router/switch, listwy zaciskowe.
* **Ciepło**: przy aktywnej F12 do kilkuset W przez krótki czas; przy normalnej pracy
  kilkanaście W (cewki styczników, Shelly, ESP32). Potrzebna kratka wentylacyjna z filtrem,
  opcjonalnie wentylator 120 mm sterowany termostatem.
* **Drzwi**: ekran 7" (płytka 181×108×15 mm) + E-STOP + kluczyk PE + lampki → albo pełne
  drzwi stalowe z wycięciem, albo drzwi transparentne (widać przełączające się styczniki,
  wartość pokazowa) i HMI w osobnej puszce na drzwiach/obok **[?]**.
* **Przekładniki DLB**: na przewodach zasilających tuż za zaciskami wejściowymi, potrzebny
  prosty odcinek ~80 mm na fazę; wyprowadzenie kabla przekładników przez dławik do modułu
  DLB na zewnątrz. Rezerwa na smart licznik: ok. 7 modułów + zaciski.

## 4. Architektura sterowania (propozycja, do zatwierdzenia w etapie 2)

```
 [ESP32-S3 + ekran 7"]  --WiFi (AP na ESP32 lub mały router)-->  [Shelly Pro 4PM / Pro 3 ...]  --> cewki styczników 230 V
          |                                                        [Shelly Pro 3EM]  <-- przekładniki na wyjściu: U, I, P na HMI
          |
   sprzętowe: E-STOP w obwodzie cewek, blokady NC między stycznikami par, kluczyk PE, termostat R
```

* ESP32 = HMI + logika scenariuszy + nadzór; Shelly = wyjścia przekaźnikowe (z pomiarem mocy
  cewek jako potwierdzeniem zadziałania) i pomiar 3-fazowy; sterowanie lokalnym API Shelly
  (HTTP RPC), bez chmury.
* Wszystko, co dotyczy bezpieczeństwa, jest **sprzętowe** (E-STOP, blokady, kluczyk,
  termostat), firmware tylko dodaje ograniczenia (jedna usterka "ciężka" naraz, limity czasu).
* Stan bezpieczny = brak zasilania cewek = wyjście odłączone (K_SEQa/b otwarte).

## 5. Pytania, od których zależy dalszy projekt

Patrz koniec pliku `02_dobor_obudowy.md` (jedna wspólna lista, uszeregowana wg wagi).
