# 02. Dobór obudowy i decyzje do podjęcia (checkpoint 1)

Status: PROPOZYCJA do zatwierdzenia, 2026-10-07. Ceny z Allegro pochodzą z wyników
wyszukiwarki (strony sklepów są z tej sesji zablokowane). Oferty oznaczone **[A]** mają
numer oferty Allegro i cenę z października 2026; pozycje **[szac.]** to przedziały
orientacyjne do potwierdzenia przy zakupach.

## 0. W skrócie

| Decyzja | Propozycja | Dlaczego |
|---|---|---|
| Obudowa | **Stalowa naścienna 1000 × 800 × 300 mm z pełną płytą montażową**: Rittal AX 1180.000 (1582 zł na Allegro) lub Adelid OM1008030 (1649 zł) | Pełny zakres funkcji to ok. 120–135 modułów DIN + transformator + rezystor + styczniki nawrotne + listwa CT; w 800 × 600 to się nie mieści z zapasem. 52 kg pusta, ok. 80 kg wyposażona |
| Rozmiar alternatywny | 800 × 600 × 300 (Eaton CS-86/300 ~935–1000 zł, Adelid OM806030 899 zł) | Tylko przy **zakresie podstawowym**: bez pominięcia RCD (F13), bez SPD, bez slotu MCB, bez rezerwy na RCD typu B (ok. 100 modułów, zapas 5–10 %) |
| Prąd projektowy | **3 × 16 A** (zasilanie ze słupka AMPERE: B16/3 → CEE 16 A) | Twoja instalacja nie da więcej; aparatura 25 A zamiast 40 A, transformator 5 kg zamiast 10 kg |
| RCD strażnik | **30 mA typu B, niepomijalny** (albo świadomie 300 mA S + pokazy „bez dotykania” za barierą) | Przy pominiętym RCD instalacyjnym (F13) i braku PE tylko 30 mA chroni człowieka; 300 mA S to ochrona ppoż. |
| Sterowanie | **ESP32-S3 z ekranem 7" + moduły przekaźnikowe Modbus RTU po RS485** | Posiadane Shelly to urządzenia **Z-Wave**, których ESP32 nie obsłuży bez osobnej bramki (szczegóły w rozdz. 6) |
| Wyjścia | Jak teraz: CEE 32 A 5P, CEE 16 A 5P, 3 × Schuko (jedno „AWARIA”) | Zgodność z obecnym stanowiskiem i wtykami ładowarek Q11 / TopAC / P-serii |

## 1. Co ustaliłem z Twoich materiałów (folder AMPERE_POINT)

**Obecna rozdzielnica** (`PROJEKT_ROZDZIELNICY/zdjecia_obecnej`, `rozdzielnica/`): przenośna
skrzynka budowlana **TED Beryl 11M**, ok. 29 × 22 × 11 cm, ok. 12 miejsc na szynie. Stary
komplet: RCD GACIA PR8NM 40 A/30 mA **typ AC**, MCB 3P B32, 3P B16, 1P B16. Nowy komplet
(sierpień 2026): Eaton FAZ-Z16/1, IDEAL KRD6-2/16/10-A (2P, 16 A, 10 mA, typ A), lampka KLI-G,
Noark Ex9BN B32/1. Gniazda: TED IEN 3253 (CEE 32 A), IEN 1653 (CEE 16 A), 3 × Schuko IP54,
środkowe oklejone „AWARIA”. Odręczna kartka „UWAGA L1 → L1 L2 L3” przy gniazdach: koncepcja
„symulator 1F” z 10.08.2026 podaje tę samą fazę na trzy styki CEE.

**Zasilanie stanowiska** (`instalacja/`): słupek „SZAFA AMPERE”: podlicznik ADELID L3F-RS
(3-faz., RS485) → RCD DV-5576 40 A/30 mA → **Siemens B16/3** → **gniazdo CEE 16 A Mennekes**.
Czyli realnie dostępne jest **3 × 16 A**; gniazdo CEE 32 A na rozdzielnicy ma sens tylko jako
złącze (ładowarka 22 kW podłączona do niego i tak zostanie ograniczona przez B16 na słupku).

**Posiadane Shelly** (`SHELLY/inne_sprzety`): Shelly **Wave** Pro 3 (3 × 16 A styki
bezpotencjałowe, Z-Wave), Wave Pro Shutter, Wave Pro Dimmer 1PM, Wave Pro 2 (Qubino, 2 wyjścia),
„the Pill by Shelly” (Gen3, Wi-Fi/BT, 5 V USB-C, hub czujników), Shelly BLU Gateway Gen3 (zestaw
z BLU TRV). **Wszystkie przekaźniki są Z-Wave, nie Wi-Fi.** Do tego TopAC EVE01-11R (ładowarka
„Powered by Shelly”, CEE 16 A, 6–16 A) i DevKit modułu Shelly X do Q11.

**Moduł DLB** (`DLB_R&D`, `wallbox_DLB`): **DLB-A1**: 3 przekładniki prądowe (CT) 0–100 A
(2000:1, klasa 0,5) na L1/L2/L3 **przed wszystkimi odpływami**, zasilanie 100–240 V AC, łączność
z wallboxem **wyłącznie radiowa 433 MHz** (antena SMA na podstawie magnetycznej), RS485 nie ma.
Producent zaleca montaż w rozdzielnicy z wyprowadzeniem anteny na zewnątrz. W stalowej obudowie
radio nie przejdzie, więc Twój plan „moduł na zewnątrz, przekładniki w środku” jest słuszny;
potrzebny jest dławik na trzy cienkie kable CT (M25 z wkładką wielootworową). Długości kabli CT
nie ma w instrukcji — do zmierzenia na egzemplarzu.

**Produkty do testowania**: ładowarki przenośne Q11 (11 kW, CEE 16 A), TopAC (CEE 16 A),
seria P (1-faz., Schuko), wallboxy PRIME/HM 11/22 kW. Firma ma tester EVSE PeakMeter PM701E
(symulacja CP/PE, test 6 mA DC), kamerę termowizyjną, UT890C. Projekt `custom_device_FINAL`
(stacja testowa z obciążeniem) używa oznaczeń EPLAN (-K, -F, -X, -S0 E-STOP, łańcuch 24 V); przyjmę
tę samą konwencję w schemacie.

## 2. Założenia po korekcie

| # | Założenie | Zmiana względem szkicu |
|---|---|---|
| A1 | DUT = ładowarki AC Ampere Point i konkurencji (przenośne na CEE/Schuko, wallboxy przez CEE 32 A lub puszkę) | bez zmian |
| A2 | **Prąd projektowy 3 × 16 A** (B16/3 na słupku). Tory 3-fazowe na aparaturze 25 A, gniazdo CEE 32 A tylko jako złącze. Przy przyszłym zasilaniu 32 A wymiana: 4 styczniki + transformator | było 32 A |
| A3 | Rozdzielnica **naścienna**, przy słupku lub w warsztacie, zasilana przewodem z wtykiem CEE 16 A (5G2,5 mm², który masz) | bez zmian |
| A4 | HMI: ESP32-S3 7"; wyjścia: moduły Modbus RTU na RS485; **bez Shelly Z-Wave** (chyba że wybierzesz wariant B z rozdz. 6) | było „Shelly jako wyjścia” |
| A5 | Usterki odwracalne, nieniszczące; przepięcie ograniczone do +24 V (254 V) pod obciążeniem, +48 V (278 V) tylko bez prądu ładowania | doprecyzowane |
| A6 | Sieć TN-S (słupek ma osobne bloki N i PE z mostkiem w szafie X = rozdział PEN w budynku) | potwierdzone z `instalacja/` |

## 3. Co musi się zmieścić (po korekcie)

### 3.1 Szyna TH35 (moduły 18 mm)

| Grupa | Elementy | Mod. |
|---|---|---:|
| Zasilanie i ochrona | rozłącznik 4P 40 A z kłódką (4) + wyzwalacz wzrostowy od E-STOP (1) · RCD „strażnik” 4P 40 A **30 mA typ B** niepomijalny (4) · RCD „instalacyjny” 4P 25 A 30 mA typ A (4) · MCB 3P B16 ×2, osobno dla CEE 32 i CEE 16 (6) · MCB 1P+N B16 gałąź Schuko z własnym N (2) · MCB 1P B6/B2 ×4: sterowanie, transformator, zasilacze, pomiar (4) | **25** |
| Opcje | SPD T2 4P po stronie zasilania (4) · „slot” na wymienny MCB do pokazu złego doboru (3) · selektor RCD typu AC/A (zamiast samego pominięcia) (4) | (11) |
| Styczniki usterek (25 A) | przerwa N, przerwa PE (2 bieguny NC równolegle), zanik L3, bocznik rezystora: **4 × stycznik 2NC 1 mod.** (cewka pod napięciem = usterka wstawiona) (4) · transformator: K_buck + K_boost, zamiana N–PE, zamiana L–N: **4 × stycznik 2NO+2NC 2 mod.** (blokada „nigdy oba” w aparacie) (8) · pominięcie RCD: 1 × 4P 25 A NO (3) | **15** |
| Przekaźniki 16 A, 1 mod. | słabe PE (100 Ω), PE pod napięciem (220 kΩ), mostek N–PE, upływ AC 30 mA, upływ DC 6 mA | **5** |
| Sterowanie i łańcuch bezpieczeństwa | 2 × Waveshare Modbus RTU Relay (D): 8 przekaźników + 8 wejść każdy, obudowa DIN 175 × 90 mm (≈ 10 mod. każdy) (20) · zasilacz 5 V HDR-15-5 (1) + 24 V HDR-30-24 (2) · przekaźnik watchdog (1) · przekaźnik czasowy limitu (2) · przekaźnik „master” cewek (1) · bezpieczniki obwodów cewek i pomiaru (2) | **29** |
| Pomiar i potwierdzenie | licznik 3-faz. RS485 Eastron SDM630-Modbus V2 po stronie zasilania (4) + złączki RS485 (2) · moduł pomiaru 3-faz. po stronie wyjścia, Modbus, zakres ≥ 300 V (4) · przekaźnik kolejności faz F&F CKF-B (1) · przekaźnik napięciowy 3-faz. F&F CP-730 (3) | **14** |
| Złączki | wejście 5 × 10 mm² (WAGO 2010), wyjścia 3-faz. ×2 i 1-faz., bloki N/PE „sieciowe” i „wyjściowe” (osobne, bo N i PE wyjścia są przełączane), sterowanie 24 V, RS485 | **≈ 20** |
| **Razem** | | **≈ 108 (+11 opcji) → 120 przy pełnym zakresie** |

### 3.2 Poza szyną

| Element | Gabaryt | Uwaga |
|---|---|---|
| Para styczników nawrotnych 3P (kolejność faz = zarazem stycznik główny), np. 2 × Chint NC1-2510 + blokada mechaniczna | ~100 × 85 × 95 mm | trwałość AC-1 ok. 1 mln cykli, 10× więcej niż modułowe |
| Transformator toroidalny 230 / 2 × 30 V (lub 2 × 24 V), **500–630 VA** (2 × 8–10 A równolegle = 30 V przy 16–20 A), uzwojenie wtórne na stałe w L1, przełączanie po stronie pierwotnej | Ø 136–142 mm, h 60–65 mm, 4–5 kg | śruba M8 z zestawem izolacyjnym (bez zwartego zwoju przez płytę); softstart NTC; ≥ 50 mm od strefy gorącej |
| Rezystor „przepalony styk”: 2 × 1 Ω / 300 W równolegle na radiatorze + wentylator 120 mm + termostat KSD301 85 °C | ~200 × 100 × 80 mm | 128 W przy 16 A, limit czasu w firmware |
| SSR 40 A z radiatorem (opcja do „luźnego styku” bez łuku) | 60 × 45 × 80 mm | alternatywa dla stycznika zużywalnego |
| „Listwa CT”: 4 proste odcinki L1 L2 L3 N po ≥ 100 mm, rozstaw ≥ 40 mm | 150 × 60 mm | przekładniki DLB-A1 (+ pokaz błędu: CT na złej fazie / odwrócony / na całym kablu = 0 A) |
| Moduł pomiaru napięcia N–PE (ZMPT101B) + ewentualny mały switch sieciowy | małe | na płycie przy sterowniku |

### 3.3 Drzwi

Ekran 7" (płytka Waveshare ESP32-S3-Touch-LCD-7: 193 × 111 × 15 mm, wycięcie ok. 193 × 111 mm,
ramka drukowana 3D z uszczelką) · grzybek E-STOP Ø22 · kluczyk „TRYB TESTOWY” Ø22 · przycisk
podtrzymania do F16 Ø22 · lampki Ø22: zielona „instalacja poprawna”, czerwona „usterka aktywna /
PE rozłączone” · brzęczyk. **Wszystko na drzwiach w 24 V DC / 5 V**, drzwi zamknięte podczas
testu (wyłącznik drzwiowy w łańcuchu cewek), plecionka PE przez zawias. Gniazda CEE i Schuko na
**dolnej ściance** nad płytą dławikową (nie na drzwiach: ciężar kabli, 400 V na drzwiach).

### 3.4 Wynik: minimalna płyta

Pełny zakres (≈ 120 modułów + 20 modułów złączek = 140): 4 rzędy szyn po ≥ 35 modułów
(630 mm) w rozstawie 150 mm = 600 mm + strefa złączek i listwy CT 120 mm + strefa
transformator / rezystor / styczniki nawrotne 250 mm → **płyta ≥ 970 × 740 mm** → obudowa
**1000 × 800 × 300** (Rittal AX: płyta 975 × 745). Zakres podstawowy (≈ 100 modułów): 4 rzędy
po 27 modułów (500 mm) w rozstawie 125 mm = 500 mm + 270 mm na resztę → płyta 770 × 550 →
**800 × 600 × 300**, bez zapasu na rozbudowę. Głębokość: 70 mm aparat + 20 mm szyna/dystanse +
40 mm przewody + 25 mm ekran w drzwiach + kanał 60 mm → 300 mm; 250 mm jest na styk.

## 4. Warianty obudowy

| Wariant | Przykładowe oferty | Cena | Masa | Plusy | Minusy |
|---|---|---|---|---|---|
| **W1 stal 800 × 600 × 300, pełna płyta (zakres podstawowy)** | Eaton CS-86/300 (111708) [A] oferta 17739059022 ~935–1000 zł; Adelid OM806030 [A] oferta 4877631140, 899 zł; ETI GT 80-60-30 ~1084 zł | 900–1100 zł | 27–33 kg | płyta 3 mm (Eaton 770 × 550), drzwi 1,5 mm odwracalne, IP66 IK10, płyta dławikowa w dnie, naturalne chłodzenie (ΔT ≈ 13 K przy 100 W) | mieści tylko zakres podstawowy (ok. 100 modułów), bez rezerwy; stalowe drzwi tłumią Wi-Fi (ESP32 za wycięciem – do sprawdzenia) |
| W1' stal 800 × 600 × 250 | Adelid OM806025 [A] 4877631306, 799 zł; Eaton CS-86/250 ~800–890 zł | 800–900 zł | 27–33 kg | 100–200 zł taniej | 50 mm mniej głębokości – ciasno za drzwiami z ekranem i przy toroidzie |
| **W2 stal 1000 × 800 × 300 (rekomendacja przy pełnym zakresie)** | Rittal AX 1180.000 [A] 16422788244, 1582 zł (płyta 745 × 975 × 2,5); Adelid OM1008030 [A] 7684269351, 1649 zł; Eaton CS-108/300 [A] 17130395404, 2269 zł | 1600–2300 zł | 48–52 kg | 4 rzędy po 35–41 modułów (140–164), strefa mocy 250 mm, miejsce na selektor RCD, SPD, slot MCB, drugi toroid; ΔT ≈ 9 K przy 100 W | ciężar: ok. 80 kg wyposażona → 4 kotwy M10/M12 w nośnej ścianie, montaż we dwóch; cena |
| W3 tworzywo ABS 700 × 500 × 250 z drzwiami transparentnymi | [A] 9787503614 (transparentne) 449 zł; [A] 11299484986 (pełne) 329–419 zł | 330–450 zł | ~8 kg | lekka, tania, radio-przezroczysta (Wi-Fi, 433 MHz), **widać przełączające się styczniki** – wartość pokazowa | płyta ~650 × 450: 4 × 22 mod. = 88 – za mało nawet na zakres podstawowy; 1,6× gorsze chłodzenie; drzwi z tworzywa nie uniosą ekranu – HMI w osobnej puszce; IK niski |
| W4 rozdzielnica modułowa 5 × 24 / 6 × 24 | Hager univers FW524WT 981–1359 zł; PrismaSeT XS 6 × 24 ~2800 zł | 1000–2800 zł | 15–25 kg | wygląd „jak w domu” | głębokość 150–170 mm: nie zmieści toroidu, rezystora, styczników nawrotnych ani ekranu bez poświęcenia rzędu; IP30/40 |
| W5 większa skrzynka budowlana (jak obecna, 3 × 12) | TED/Pawbol/Elektro-Plast | 300–600 zł | 5–8 kg | przenośna, gniazda na froncie | max ~36 modułów – trzykrotnie za mało |

Drzwi przeszklone w stali istnieją tylko u Legranda (Atlantic 036949 1000 × 800, promocja
~2113 zł) i jako akcesorium Eaton (CS-108/300); na Allegro ich nie znalazłem. Uwaga: kamera
termowizyjna i tak nie widzi przez szkło ani pleksi, więc okno pomaga tylko oglądać styczniki.
Drzwi i tak mają być zamknięte podczas testu, więc okno jest luksusem, nie potrzebą.

## 5. Termika i wentylacja

Straty ciągłe: cewki 6–10 styczników (2–4 W każda), moduły Modbus, ESP32, zasilacze, uzwojenie
transformatora ze zwartym pierwotnym (10–20 W) → ok. 60 W. W2 stal: przyrost ≈ 6 K, W1 ≈ 8 K. Rezystor 128 W przez ≤ 60 s nie nagrzeje obudowy, ale radiator musi
mieć własny wentylator. Zalecam od razu kratkę z filtrem 120 × 120 (20–35 zł) na dole i drugą na
górze, bez wentylatora obudowy; miejsce na wentylator filtrujący 150 × 150 (ATV2200, ~203 zł)
zostawione na wypadek, gdyby rezystor miał pracować dłużej.

## 6. Dylemat: posiadane Shelly (Z-Wave) a sterowanie z mikrokontrolera

Shelly Wave Pro 3 to świetny element wykonawczy (3 niezależne styki bezpotencjałowe 16 A, DIN),
ale rozmawia tylko po **Z-Wave**. ESP32 nie ma Z-Wave; wejścia SW1–SW3 tych urządzeń są
230-woltowe, więc żeby je wysterować, ESP32 i tak potrzebuje przekaźnika – wtedy Wave Pro 3
niczego nie dodaje. Dwie spójne drogi:

| | **A. ESP32 + Modbus (rekomendacja)** | **B. Raspberry Pi + Home Assistant + Z-Wave** |
|---|---|---|
| HMI | Waveshare ESP32-S3-Touch-LCD-7 [A] 18176697600, ~188–229 zł | RPi 4/5 (~300–480 zł) + Touch Display 2 7" [A] 17135472433, ~282 zł |
| Wyjścia | 2 × Waveshare Modbus RTU Relay (D) [A] 15193520373, ~149 zł: 16 przekaźników 10 A + 16 wejść zwrotnych, jeden kabel RS485 | posiadane Wave Pro 3 (3 wyjścia/szt.), Wave Pro 2, + USB stick Z-Wave 800 (~200–280 zł) |
| Pomiar | SDM630 V2 na tym samym RS485 | SDM630 przez adapter USB-RS485 lub integracja HA |
| Czas reakcji | 10–30 ms, deterministyczny; „brzęczenie” 50–500 ms możliwe | 100–500 ms przez Z-Wave; brzęczenie niepraktyczne |
| Bezpieczeństwo | automat stanów w firmware + watchdog; i tak wszystko krytyczne sprzętowo | automatyzacje HA nie są warstwą bezpieczeństwa; wszystko krytyczne sprzętowo |
| Start, odporność | < 2 s, brak karty SD w torze krytycznym | 20–30 s, karta SD, zasilanie 5 V/3 A |
| Co z magazynem Shelly | nieużyte (zostają do biura / ofert) | wykorzystane |
| Koszt sterowania | ~550–650 zł | ~900–1200 zł + stick |

Mój wniosek: to, co powiedziałeś na początku („sterowanie przez mikrokontroler”), jest
technicznie lepsze dla tego stanowiska. Shelly Wave użyj tam, gdzie jest już Z-Wave (biuro),
a tu zostaw ewentualnie **„the Pill”** jako węzeł Wi-Fi do czujników temperatury radiatora
(Gen3, lokalne API, zasilanie 5 V). Jeśli jednak zależy Ci, żeby stanowisko było częścią
ekosystemu Home Assistant / Shelly, powiedz – przeprojektuję na wariant B.

## 7. Rekomendacja

1. **Obudowa W2: Rittal AX 1180.000** (1000 × 800 × 300, Allegro oferta 16422788244, 1582 zł;
   płyta 975 × 745 × 2,5 mm, dwie płyty dławikowe, IK10) albo **Adelid OM1008030** (1649 zł,
   polski producent, blacha 1,2–1,5 mm; przed zakupem potwierdzić u sprzedawcy wymiar płyty
   ≥ 960 × 740). Jeśli świadomie tniesz zakres do podstawowego (bez F13, SPD, slotu MCB,
   selektora RCD, bez miejsca na rozbudowę) – **W1: Eaton CS-86/300 lub Adelid OM806030**.
2. **Drzwi pełne stalowe** z ekranem 7", E-STOP, kluczykiem, przyciskiem podtrzymania, dwiema
   lampkami i brzęczykiem – wszystko 24 V / 5 V; wyłącznik drzwiowy; drzwi zamknięte w czasie
   testu. Gniazda na dolnej ściance.
3. **Zasilanie 3 × 16 A**, aparatura 25 A, jeden transformator 500–630 VA na L1 przełączany po
   stronie pierwotnej.
4. **RCD strażnik 30 mA typu B, niepomijalny** (Noark Ex9L-B / ETI EFI-4 B, 600–1200 zł).
5. **Sterowanie wariant A** (ESP32-S3 + 2 × Modbus RTU Relay (D) + SDM630 V2 na wspólnym RS485)
   z łańcuchem sprzętowym 24 V opisanym w `01_koncepcja`.
6. **Ładowarka badana na osobnej płycie izolacyjnej** ≥ 0,5 m od obudowy, nigdy na obudowie.
7. Rezerwa: SPD, slot MCB, selektor RCD AC/A, drugi toroid, 10–15 modułów.

Orientacyjny budżet całości (bez przewodów 6/2,5 mm²): aparatura Noark/F&F/Chint 2300–2900 zł
(z RCD typu B) albo Hager/Eaton 4500–5500 zł · obudowa 1600–1650 zł · HMI + 2 × Modbus +
zasilacze + przekaźniki watchdog/czasowe ~800 zł · transformator 260–390 zł · licznik + moduł
pomiaru wyjścia 350–600 zł · rezystory, radiator, wentylator, termostaty ~250 zł · gniazda,
dławiki, osprzęt 22 mm 24 V 200–400 zł · złączki, bloki, przewody sterownicze 300–450 zł →
**ok. 6,5–8 tys. zł (budżet) lub 9–11 tys. zł (premium)**. Koszyki: hurtownia na Allegro
(aparatura + obudowa + złączki + gniazda), Botland/Kamami (ESP32, Modbus, zasilacze, SSR,
rezystory, ZMPT101B), Indel/Breve/Telto (toroid), Chint (para nawrotna).

## 8. Pytania (od najważniejszego)

1. **Dotykanie podczas pokazów**: czy przy „brak PE”, „PE pod napięciem”, „zamiana N–PE”, „brak
   RCD”, „przerwa PEN” ktokolwiek dotyka ładowarki, kabla, testera lub auta? Czy podłączane bywa
   prawdziwe auto, czy tylko symulator / AmpCheck? → decyduje o strażniku 30 mA B vs 300 mA S.
2. **Zasilanie**: potwierdzasz 3 × 16 A z CEE 16 A na słupku? Czy przewidujesz kiedyś 32 A?
3. **Sterowanie A czy B** (rozdz. 6)? Jeśli B: ile sztuk Wave Pro 3 / Wave Pro 2 / Pro Shutter
   masz i czy jest już kontroler Z-Wave?
4. **Zakres → obudowa**: pełny zakres (z pominięciem RCD, SPD, slotem MCB, rezerwą) → W2
   1000 × 800 × 300; zakres podstawowy → W1 800 × 600 × 300. Który?
5. **Gdzie wisi**: ściana w warsztacie, przy słupku na zewnątrz (IP66 bez kratek, grzałka), czy
   stelaż? Ok. 80 kg wyposażona – jest nośna ściana?
6. **Ładowarki badane**: egzemplarze „do zużycia” czy mają zostać sprawne? Zgoda na max 260 V przez
   30 s? Przesunięcie punktu zerowego (przerwa N z niesymetrycznym obciążeniem) – tak czy nie?
7. **Gniazda wyjściowe**: zestaw jak dziś (CEE 32 + CEE 16 + 3 × Schuko)? Jak dziś jest podłączone
   gniazdo „AWARIA”? Potrzebne gniazdo Type 2 (AmpCheck, wstrzyknięcie 6 mA DC za ładowarką)?
8. **„Przepalony styk”**: realne grzanie 128 W do kamery (otwarte drzwi wg procedury) czy tylko
   spadek napięcia z transformatora? **„Luźny styk”**: widoczny łuk (stycznik zużywalny) czy czysty
   pokaz (SSR)?
9. **Marka aparatury**: budżet (Noark / ETI / F&F / Chint) czy premium (Hager / Eaton)?
10. **Smart licznik**: Eastron SDM630 V2 (Modbus, czyta HMI), ADELID L3F-RS jak na słupku, czy
    licznik MID do rozliczeń?
11. **Obsługa i dokumentacja**: kto obsługuje (SEP E ≤ 1 kV)? Czy chcesz formalnej instrukcji
    stanowiskowej, oceny ryzyka i protokołu pomiarów po montażu (zrobię w etapie 5)?
12. Czy masz dostęp do drukarki 3D (ramka ekranu)? Jeśli nie – wytnę ramkę z blachy/pleksi w projekcie.
