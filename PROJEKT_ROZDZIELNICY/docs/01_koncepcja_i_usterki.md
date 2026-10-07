# 01. Koncepcja stanowiska i macierz usterek

Status: wersja 2 (2026-10-07) po lekturze folderu AMPERE_POINT i researchu. Elementy
oznaczone **[?]** wymagają Twojej decyzji (lista pytań w `02_dobor_obudowy`).

## 1. Co budujemy

Naścienna rozdzielnica testowo-szkoleniowa Ampere Point. Zasila ładowarki AC (przenośne
Q11 / TopAC / seria P oraz wallboxy przez CEE) i z ekranu dotykowego wstawia w tor zasilania
typowe błędy instalatora, żeby pokazać, jak reagują ładowarka, jej zabezpieczenia, RCD
instalacji oraz moduł DLB. Następca przenośnej skrzynki TED Beryl 11M (CEE 32 A, CEE 16 A,
3 × Schuko z gniazdem „AWARIA”).

Formalnie jest to **stanowisko probiercze wg EN 50191** (urządzenie badawcze, które celowo
wytwarza stany niebezpieczne), a nie rozdzielnica instalacyjna wg HD 60364. Z tego wynikają:
kluczyk „TRYB TESTOWY”, E-STOP, lampki czerwona/zielona, oznakowanie, obsługa przez osobę
poinstruowaną. Przełączanie PE jest w instalacjach zabronione (HD 60364-5-54 p. 543.3.3,
IEC 61851-1 p. 8.4) i dopuszczalne wyłącznie w takim urządzeniu probierczym; tak samo robią
to komercyjne adaptery testowe EVSE (Metrel A 1532 XA, Kewtech).

## 2. Założenia

| # | Założenie | Źródło |
|---|---|---|
| A1 | DUT: ładowarki AC do 11 kW (CEE 16 A), 1-faz. do 16 A (Schuko), wallboxy przez CEE 32 A tylko jako złącze | produkty AP, obecna skrzynka |
| A2 | **Prąd projektowy 3 × 16 A** – zasilanie ze słupka AMPERE (B16/3 → CEE 16 A). Aparatura 25 A; wymiana na 40 A możliwa, jeśli pojawi się zasilanie 32 A **[?]** | `instalacja/` |
| A3 | Montaż naścienny, przewód zasilający 5G2,5 mm² z wtykiem CEE 16 A **[?]** | – |
| A4 | HMI: ESP32-S3 7"; wyjścia: moduły Modbus RTU po RS485; posiadane Shelly Wave (Z-Wave) nieużyte, chyba że wariant B **[?]** | `SHELLY/inne_sprzety` |
| A5 | Usterki odwracalne. Przepięcie max +24 V (254 V) pod obciążeniem, +48 V (278 V) tylko gdy prąd < 10 A. Przerwa N z przesunięciem zera tylko po osobnym potwierdzeniu **[?]** | IEC 61851-1 (±10 %), karty ładowarek |
| A6 | Sieć TN-S za rozdziałem PEN w budynku | `instalacja/` |
| A7 | Stan bezpieczny = cewki bez napięcia = instalacja **poprawna** (usterka = cewka pod napięciem) | zasada projektowa |

## 3. Macierz usterek

Oznaczenia: K = stycznik/przekaźnik, R = rezystor, T1 = transformator szeregowy.
Progi: ładowarki pracują w 207–253 V (±10 % Un, IEC 61851-1); urządzenia z detekcją
uszkodzenia PEN (UK, część EU) wyłączają się poza 207/253 V w ≤ 5 s; RCD typ A: 30 mA AC
w ≤ 300 ms, odporny na 6 mA DC; RDC-DD ładowarki: 6 mA DC w ≤ 10 s.

| ID | Błąd instalatora | Jak symulujemy | Oczekiwana reakcja | Blokady / uwagi |
|---|---|---|---|---|
| F1 | Brak PE | K_PE: stycznik **2NC 25 A** w pojedynczym przewodzie PE wyjścia; cewka pod napięciem = PE otwarte. Cewka zasilana tylko przez kluczyk „TRYB TESTOWY” i E-STOP; styk pomocniczy do sterownika | Ładowarki z kontrolą PE / N–PE (go-e, Easee, Zaptec, UK O-PEN) odmawiają; proste EVSE ładują normalnie – to też wynik pokazu | nigdy nie przełączamy PE obudowy ani szyny PE, tylko żyłę do DUT; auto-powrót ≤ 60 s; lampka czerwona |
| F2 | Słabe uziemienie (duża impedancja) | przy otwartym K_PE: K_PEr (16 A) + **R 100 Ω / 50 W** równolegle do styku K_PE | tester pokazuje wysokie Zs; ładowarka zwykle bez reakcji; RCD nadal zadziała (30 mA × 100 Ω = 3 V) | nie łączyć z F6/F14 (moc w rezystorze) |
| F3 | PE pod napięciem | przy otwartym K_PE: K_PEu + **R 220 kΩ** z L1 na PE wyjścia (≈ 1 mA) | monitor N–PE ładowarki (wejście MΩ) widzi ~230 V i zgłasza błąd; tester pokazuje napięcie na PE | prąd ograniczony do 1 mA; mimo to DUT traktować jak pod napięciem **[?]** |
| F4 | Przerwa w N | K_N: stycznik 2NC 25 A w N wyjścia | 1-faz.: zanik zasilania. 3-faz.: ładowarka widzi asymetrię (jej elektronika L1–N) | przesunięcie zera (np. 267/133 V) tylko z dodatkowymi niesymetrycznymi odbiornikami – opcja, ≤ 5 s, DUT „do poświęcenia” **[?]** |
| F5 | Zamiana N z PE | K_NPE: stycznik **2NO+2NC 25 A** krzyżujący N/PE wyjścia (blokada mechaniczna w aparacie) | z RCD w torze: wyzwolenie przy pierwszym poborze prądu; bez RCD „działa”, a obudowa auta ma potencjał N | dozwolone tylko z RCD w torze (blokada w firmware) |
| F6 | Mostek N–PE przy urządzeniu („dorobione” TN-C) | K_B (16 A) łączy N i PE wyjścia | RCD wyzwala przy ~60–100 mA poboru; bez RCD przez PE płynie do połowy prądu | – |
| F7 | Zamiana L z N (gniazdo 1-faz.) | K_LN: stycznik 2NO+2NC 25 A na odpływie Schuko | ładowarka 1-faz. z kontrolą N–PE / IC-CPD (IEC 62752) odmawia startu | – |
| F8 | Zanik fazy | K_L3: stycznik 2NC 25 A w L3 | kody typu „phase loss / imbalance” (go-e E03, Wallbox 09, BMW E13) lub przejście na 1 fazę | – |
| F9 | Zła kolejność faz | **para styczników nawrotnych 3P** (Chint NC1-2510 ×2 + blokada mechaniczna): K_SEQa zgodna, K_SEQb L2↔L3; pełni rolę stycznika głównego | większość ładowarek nie reaguje (IEC 61851-1 tego nie wymaga); Mennekes Amtron – błąd 10; **DLB i liczniki** mapują fazy błędnie | przełączanie tylko przy otwartym wyjściu, martwy czas ≥ 50 ms |
| F10a | Za niskie napięcie | **T1** toroid 230 / 2 × 30 V (lub 2 × 24 V), 500–630 VA, uzwojenia wtórne równolegle (30 V przy ≥ 16 A) **na stałe w szereg z L1**. Przełączanie **po stronie pierwotnej** (~2–3 A): K_buck i K_boost = 2 × stycznik 2NO+2NC 25 A; gdy oba bez napięcia, ich styki NC **zwierają uzwojenie pierwotne** → wtórne ma tylko impedancję rozproszenia (spadek ~1 V, 10–20 W). Usterka: rozewrzyj zwarcie → zamknij K_buck (pierwotne w przeciwfazie) → 200 V | poniżej 207 V przerwanie ładowania w ≤ 5 s (Easee); Wallbox dopiero < 150 V | nigdy nie bocznikujemy wtórnego przy zasilonym pierwotnym (zwarcie transformatora); blokada K_buck/K_boost stykami NC; softstart NTC + MCB B6 na pierwotnym; warystor S14K275 |
| F10b | Za wysokie napięcie | jak wyżej, K_boost (pierwotne w fazie) → +30 V. Firmware dobiera krok od **zmierzonego** napięcia sieci tak, by wyjście ≤ 260 V (przy sieci > 236 V używa odczepu +12/+24 V lub odmawia) | powyżej 253 V przerwanie ładowania | max 260 V, ≤ 30 s, potem ≥ 60 s przerwy; 278 V (+48 V) **wykreślone** (zasilacze DUT znoszą zwykle 264 V) |
| F11 | Luźny styk (przerywanie) | K_INT: **stycznik przemysłowy AC-3** (Chint NC1-2510 klasa, trwałość 1–2 mln cykli) w L1 jako element zużywalny z licznikiem cykli; impulsy OFF ≥ 100 ms, ON ≥ 500 ms, ≤ 30 cykli w serii, ≥ 2 min przerwy. Opcja bez łuku: **SSR 40 A** zero-cross tylko na gałęzi 1-faz. 16 A, z własnym B16 i bocznikiem | restart / błąd „zanik zasilania”; DLB widzi skoki | widoczny łuk (stycznik) vs czysty pokaz (SSR) – do wyboru **[?]**; nie jest to pokaz AFDD |
| F12 | Przepalony styk / za cienki przewód | **R 0,5 Ω / ≥ 600 W** (2 × 1 Ω / 300 W równolegle lub 4 × 1 Ω / 100 W) na radiatorze ≤ 0,5 K/W z wentylatorem, bocznik K_R (2NC = pod napięciem wstawia rezystor); 16 A → 8 V spadku, 128 W; krok 1 Ω → 16 V (7 %), 256 W | spadek napięcia pod obciążeniem (limit 5 % wg HD 60364-5-52 zał. G), nagrzewanie do kamery termowizyjnej (kamera nie widzi przez szkło – pokaz przy otwartych drzwiach wg procedury) | termostat KSD301 85 °C NC w obwodzie cewki K_R (gorący radiator **usuwa** usterkę); czujnik DS18B20 do sterownika (blokada > 75 °C); limit 60 s / 1 Ω: 20 s; obudowy rezystorów na PE; przewody silikonowe; alternatywa bez ciepła: T1 w trybie „−30 V” **[?]** |
| F13 | Brak RCD | tor „przez RCD 30 mA typ A” / „z pominięciem” (stycznik 4P 25 A **NO** = pominięcie tylko pod napięciem cewki). Przed nim zawsze **RCD strażnik niepomijalny** | bez RCD usterki F5/F6/F14 „działają”, prąd płynie przez PE | **decyzja**: strażnik 30 mA typ B (chroni człowieka, może zadziałać razem z instalacyjnym) albo 300 mA S (tylko ochrona ppoż. – wtedy F13 zabronione z F1–F3/F16 i pokazy „bez dotykania”) **[?]**; ≤ 120 s |
| F14 | Upływ AC ~30 mA | K_LK + **R 6,8 kΩ / 25 W** z L1 na PE wyjścia (34 mA) | RCD 30 mA wyzwala, strażnik 300 mA nie | – |
| F15 | Upływ DC 6 mA | K_LKdc + mostek prostowniczy + C 22 µF/400 V + **R 54 kΩ / 5 W** (6 mA gładkie) wstrzyknięte **przed** ładowarką | RCD typu A/AC nie reaguje na gładkie 6 mA DC (to nie jest „oślepianie” – typ A ma zachować czułość przy 6 mA DC; typ B by zadziałał); RDC-DD w ładowarce nie widzi, bo upływ jest przed jej czujnikiem | test RDC-DD ładowarki robi PM701E po stronie auta |
| F16 | Przerwa PEN (TN-C) | F1 + F4 + F6 jednocześnie (PE i N odłączone, zmostkowane przy DUT) | ładowarki z detekcją PEN odmawiają; pozostałe pracują, a PE/obudowa auta przyjmuje potencjał przez odbiornik | jedyna dozwolona kombinacja: **przycisk podtrzymania (hold-to-run) na drzwiach**, usterka trwa tylko gdy instruktor go trzyma, max 10 s przekaźnikiem czasowym; bez prawdziwego auta; DUT za barierą; lampka + brzęczyk |
| F17 | Zły dobór zabezpieczenia | „slot” 3 mod. na wymienny MCB (B16 ↔ C32) z mostkowanymi zaciskami | pokaz charakterystyk na liczniku prądu | opcja **[?]** |
| F18 | Błędy montażu przekładników DLB | listwa CT: przekładnik na złej fazie, odwrócony, na przewodzie odpływowym zamiast zasilającego, na całym kablu 5-żyłowym (= 0 A) | DLB-A1 źle bilansuje / nic nie widzi | bez przełączania, pokaz ręczny; koszt zero |

Inne błędy z polskich źródeł (ładowarka na istniejącym obwodzie, RCD typu AC, brak pomiarów
odbiorczych, zły punkt rozdziału PEN, brak SPD) pokazujemy opisowo na HMI lub przez F13/F17.

## 4. Architektura (wariant A, do zatwierdzenia w etapie 2)

```
[ESP32-S3 + ekran 7"]
   |-- RS485 Modbus RTU --> [Modbus Relay (D) #1: 8 R + 8 DI]  cewki grupy PE / N / L
   |                        [Modbus Relay (D) #2: 8 R + 8 DI]  K_SEQ, K_INT, K_R, K_buck/K_boost,
   |                                                            przekaźniki upływu, wentylator
   |                        [Eastron SDM630 V2 – strona zasilania]  U, I, P, PF „licznika instalacji”
   |                        [moduł pomiaru 3-faz. – strona wyjścia, ≥ 300 V] + [ZMPT101B: U N–PE]
   +-- GPIO: bicie serca 1 Hz --> przekaźnik watchdog

Łańcuch sprzętowy zasilania cewek (24 V DC):
   kluczyk „TRYB TESTOWY” -> E-STOP (NC) -> wyłącznik drzwiowy (NC) -> termostat radiatora 85 °C (NC)
   -> przekaźnik watchdog (brak bicia serca 2 s = otwarty) -> przekaźnik czasowy limitu
      (60 s grupa PE/N, 10 s F16 z przyciskiem podtrzymania) -> styk przekaźnika Modbus -> cewka
Zasada: cewka bez napięcia = instalacja poprawna; tylko para K_SEQ (stycznik główny)
jest „pod napięciem = praca”. E-STOP dodatkowo wyzwala wyzwalacz wzrostowy rozłącznika
głównego (redundancja na wypadek sklejonego stycznika).
```

**Zasady bezpieczeństwa przyjęte do projektu** (wyciąg z przeglądu krytycznego, pełna lista 50 reguł w `docs/zrodla/`):

1. Przełączany jest wyłącznie pojedynczy przewód PE do DUT; obudowa, płyta, drzwi (plecionka przez zawias), radiator, osłony są na stałe na PE sieci. Dwa osobne bloki: „PE/N sieciowe” i „PE/N wyjściowe”.
2. PE przez dwa równoległe bieguny NC stycznika 25 A (redundancja powrotu); potwierdzenie stanu PE z dwóch niezależnych źródeł: styk pomocniczy + pomiar U(PE_DUT – PE_sieci) < 5 V. Niezgodność > 500 ms = zrzut wszystkich cewek, otwarcie wyjścia, reset kluczykiem.
3. Zasilanie sterownika, zasilaczy, licznika, SPD i wentylatora **po stronie zasilania** (za rozłącznikiem i strażnikiem, przed sekcją usterek); nic, czego potrzebuje sterownik, nie odnosi się do N ani PE wyjścia.
4. Pomiar napięć po stronie wyjścia tylko przez przetworniki izolowane o zakresie ≥ 400 V (ZMPT101B z dzielnikiem) i przekaźniki F&F CP-730 / CKF-B (400 V); licznik SDM630 po stronie zasilania.
5. Na drzwiach wyłącznie obwody 24 V DC i 5 V (E-STOP, kluczyk, przycisk podtrzymania, lampki, brzęczyk, HMI); wiązka HMI oddzielona ≥ 10 mm od 230/400 V; żadnych przewodów Dupont.
6. Drzwi zamknięte podczas testu (wyłącznik drzwiowy w łańcuchu cewek); wnętrze palcobezpieczne IPXXB (osłony zacisków, osłonięta listwa CT, osłonięte końcówki rezystorów i transformatora).
7. Ładowarka badana montowana na **osobnej płycie izolacyjnej ≥ 0,5 m od obudowy**, nigdy na obudowie; podczas F1/F2/F3/F5/F6/F13/F16 bez prawdziwego auta (symulator / AmpCheck); gniazdo CEE opisane „TYLKO URZĄDZENIE BADANE – PE PRZEŁĄCZANE”, zasilane tylko w trybie testowym.
8. Macierz wykluczeń w firmware i – gdzie się da – w okablowaniu (cewki drabinek upływu przez styki NC K_PE i K_B): grupy PE{F1–F3}, N{F4–F6}, L{F7–F9}, U{F10}, Z{F11–F12}, RCD{F13–F15}, jedna usterka na grupę; zakazane m.in. F10b+F4, F13+PE, F4+F5/F6/F7; F9 tylko przy otwartym wyjściu.
9. Warunki uzbrojenia: prąd wyjścia < 1 A dla każdego przełączenia PE/N/L, napięcie sieci 207–253 V i poprawna kolejność, radiator < 60 °C, kluczyk w TEST, drzwi zamknięte, E-STOP zwolniony. Powrót do normy weryfikowany stykami pomocniczymi i pomiarem, zanim HMI pokaże „OK”.
10. Autotest przed sesją (30 s): PE zamknięte, usterki wyłączone, napięcia i kolejność w normie, E-STOP i wyłącznik drzwiowy sprawdzone, przycisk TEST RCD instalacyjnego potwierdzony; wynik do dziennika na SD.
11. Tabliczka „URZĄDZENIE PROBIERCZE EN 50191 – SYMULATOR USTEREK – PE MOŻE BYĆ ODŁĄCZONY”, znak W012, instrukcja stanowiskowa, protokół pomiarów po montażu (ciągłość PE < 0,1 Ω do każdej części, Zs, test RCD).

## 5. Pytania

Jedna wspólna lista, uszeregowana, jest w `02_dobor_obudowy.md`, rozdział 8.
