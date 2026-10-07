# KOMPENDIUM — projekt AmperePoint / Shelly (folder z_recpec)

Plik roboczy, prowadzony na bieżąco. Nie jest przeznaczony do czytania przez człowieka —
ma służyć jako punkt odniesienia i kontekst dla modelu AI w kolejnych sesjach.
Zasada: przed każdą odpowiedzią sprawdzam, czy coś z wymiany jest warte dopisania tutaj.

Założony: 2026-09-22. Ostatnia aktualizacja: 2026-09-22.

---

## 1. Czym jest ten folder

`C:\Users\Lenovo\Desktop\AMPERE_POINT\z_recpec`

| Plik | Co to |
| --- | --- |
| `Recording_33.m4a` | zapis spotkania, 48 min 50 s, 16 kHz mono AAC |
| `Recording_34.m4a` | zapis spotkania, 18 min 31 s, dalszy ciąg tej samej rozmowy |
| `Recording_33 - transkrypcja.pdf/.md` | transkrypcja, 108 wypowiedzi, 6229 słów |
| `Recording_34 - transkrypcja.pdf/.md` | transkrypcja, 70 wypowiedzi, 2588 słów |
| `AmperePoint-Shelly - analiza.pdf/.md` | analiza biznesowo-technologiczna, 47 stron, 22 rozdziały |
| `KOMPENDIUM.md` | ten plik |

**WAŻNA DECYZJA UŻYTKOWNIKA (2026-09-21):** z pliku `analiza` usunięto wszystkie odwołania
do nagrań (142 sygnatury czasowe + 35 sformułowań typu „w nagraniu"). Dokument ma nie
zdradzać, że powstał z nagrań — mówi o „rozmowach ze spotkania". **Przy każdej przyszłej
edycji analizy trzymać się tej konwencji.** Cytaty pozostały dosłowne. Użytkownik został
poinformowany, że (a) dosłowne cytaty nadal brzmią jak stenogram i można je przerobić na mowę
zależną, (b) w tym samym folderze leżą transkrypcje i pliki .m4a, które mówią wszystko wprost
— czeka decyzja, czy je przenieść. **Nie ruszać ich bez polecenia.**

## 2. Tor techniczny (jak powstały pliki)

Szczegóły w pamięci: `transkrypcja-nagran-lokalnie.md` i `srodowisko-modul-windows.md`.
Skrót najważniejszego:

- Transkrypcja: `faster-whisper` large-v3, CPU int8, 8 wątków, `language="pl"`, `vad_filter`,
  `condition_on_previous_text=False`, `initial_prompt` ze słownikiem branżowym. ~1× realtime.
- `HF_HUB_DISABLE_SYMLINKS=1` obowiązkowe (inaczej WinError 1314 przy pobieraniu modelu).
- Dekodowanie M4A przez PyAV (`av`) — na tym komputerze nie ma ffmpeg.
- Kontrola krzyżowa wątpliwych fragmentów drugim modelem (`large-v3-turbo`) — bardzo skuteczna.
- **Diaryzacja (rozpoznawanie mówców) na tych nagraniach NIE DZIAŁA.** Sprawdzone:
  sherpa-onnx + pyannote-segmentation-3.0 + osadzenia WeSpeaker ResNet34_LM (zlewa wszystkich,
  0,83 między różnymi osobami) i CAM++ (lepszy, ale na pełnym materiale 83 % czasu ma margines
  decyzji < 0,10; test na 6 fragmentach o znanym autorze: 9/12). Przyczyna: jeden mikrofon
  w pogłosowej sali. **Przypisanie stron w transkrypcjach zrobione z TREŚCI, nie z głosu.**
- Skład PDF: xelatex z MiKTeX, `\setmainfont{Calibri}` (Carlito NIE jest zainstalowane).
- Skrypty robocze: `<scratchpad>/analiza/` (build_analiza.py, sek_*.md, odetnij.py).

## 3. Kto jest kim

- **AmperePoint** — polska marka ładowarek EV (amperepoint.pl). Flagowiec: przenośna Q11,
  11 kW, Typ 2, CEE, IP66, 6–16 A, Wi-Fi Tuya, ~1000–1400 zł. Ok. 20 tys. klientów końcowych,
  ~50 % korzysta ze smart. Produkcja w 3 fabrykach w Chinach (3 półki cenowe), tylko jedna ma
  mocny zespół elektroników. Sprzedaż: kanał konsumencki i e-commerce.
- **Tuya** — chińska platforma IoT PaaS (moduł + chmura + aplikacja). Q1 2025: 74,7 mln USD
  przychodu, marża brutto 48,5 %, >1,4 mln deweloperów. Dziś dostawca modułu w ładowarkach AP.
- **Shelly / Allterco** — bułgarska grupa, giełda we Frankfurcie (SDAX). FY2025: 149,7 mln EUR
  (+40,3 %), DACH 62,0 mln EUR, reszta Europy 74,0 mln EUR (+51 %), 2,7 mln użytkowników
  chmury, >100 krajów, ~5300 instalatorów. Prognoza 2026: 195–205 mln EUR, EBIT 47–52 mln EUR.
  W ładowarkach nowicjusz: jeden produkt — **TopAC / Shelly Power EV-Charger EVE01-11R**,
  11 kW, przenośny, CEE, DLB, aplikacja. Stan magazynu podany na spotkaniu: 3,5 tys. szt.
- **Plejd** (odniesienie z rozmowy) — szwedzka marka smart home, ~116 mln USD przychodu TTM,
  >5 mln urządzeń, >50 tys. instalatorów, głównie kraje nordyckie.

Osoby wymienione: **Boris** — szef R&D Shelly (nieobecny, do niego call); **Czarek** — Shelly,
organizuje dostawę sprzętu; **Maciej**, **Adam** — pojawiają się w rozmowie; **Dawid** — strona
AmperePoint, część techniczna. Imię przedstawiciela Tuya nieustalone.

## 4. Sedno sprawy (stan na 2026-09)

AmperePoint chce wyjść z zależności od Tuya. Shelly proponuje wymianę modułu Wi-Fi na swój,
pin-to-pin, bez przeprojektowania płytki ładowarki.

- Dziś: moduł **Tuya WBR3** (BK7231N, ~120 MHz, 2 MB flash, 256 kB RAM, 2×8 pinów raster 2 mm).
- Docelowo: moduł **Shelly X0–X4** (ESP32-C3, RISC-V do 160 MHz, typowo 4 MB flash, ~400 kB RAM,
  4–8 I/O, −40…+105 °C). Platforma OEM: **x.shelly.com** (Create Product, no-code/low-code,
  ścieżka „kopiuj Tuya", dev kit na USB-C).
- Co zmienia fabryka: pozycja w BOM + oprogramowanie stanowiska testowego (pingowanie do innej
  chmury) + procedura testu. Płytka, obudowa, narzędzia — bez zmian.
- Warianty współpracy: A) własna chmura/apka, B) moduł jako enabler, C) pełny ekosystem Shelly
  (rekomendowany przez nich, uruchamia kanały sprzedaży), D) własna chmura kompatybilna z Shelly.
- Czego to NIE rozwiązuje: ISO 15118/PLC (wymaga osobnego modemu, ~70 USD w BOM), brak modułu
  z SIM/GSM w ofercie Shelly, jakość montażu w fabryce, zależność jako taka (zmiana pana).

Kluczowe liczby z rozmowy: +70 USD w BOM ≈ +400 zł na półce ≈ sprzedaż /3 (szacunek AP);
zablokowane kontrakty B2B ok. 500 szt./rok; minimum ~30 % marży na obcych produktach;
„poniżej 55 % rabatu nie sprzedajemy niczego".

## 5. Baza wiedzy regulacyjnej

Sprawdzone 2026-09; przy decyzjach potwierdzić u źródła.

### 5.1. Trzy różne porządki prawne (nie mylić!)

1. **Prawo produktowe** — co musi spełnić urządzenie, żeby je wolno było sprzedać.
   LVD (bezpieczeństwo elektryczne), EMC, **RED** (radio, od 1 VIII 2025 także
   cyberbezpieczeństwo — rozporządzenie delegowane (UE) 2022/30, normy **EN 18031-1/2/3**),
   RoHS, GPSR. Dotyczy tak samo przenośnych i stacjonarnych.
2. **Prawo infrastrukturalne / operatorskie** — **AFIR**, rozporządzenie (UE) 2023/1804.
   **Wiąże operatorów punktów PUBLICZNIE DOSTĘPNYCH.** Prywatny sprzęt domowy jest poza
   zakresem. Terminy: EN ISO 15118-2 dla nowo instalowanych publicznych od 8 I 2026;
   ISO 15118-20 od 1 I 2027; akt delegowany (UE) 2025/656 + rozp. wykonawcze (UE) 2025/655.
3. **Prawo budowlane / instalacyjne** — **EPBD** (dyrektywa (UE) 2024/1275): wymogi dla
   BUDYNKÓW (nowe i po głębokiej renowacji, >3 miejsca postojowe): prekablowanie ≥50 % miejsc,
   min. jeden punkt ładowania, punkty mają być interoperacyjne i zdolne do smart charging,
   „gdzie właściwe" dwukierunkowe. Obowiązek po stronie inwestora/właściciela budynku.
   + krajowe: prawo budowlane, zgłoszenia do OSD, przepisy instalacyjne.

### 5.2. Przenośne vs stacjonarne — gdzie naprawdę leży różnica

- **IEC 61851-1 Mode 3** = EVSE **na stałe przyłączone** do sieci (wallbox, słupek).
- **Mode 2** = urządzenie **nieprzyłączone na stałe**, z modułem sterująco-zabezpieczającym
  w kablu (**IC-CPD**), norma **IEC/EN 62752** (wyd. 2024). Wymaga m.in.: RCD ≤30 mA,
  wykrywanie składowej stałej **6 mA DC** (obowiązkowe od 1 I 2018 — bez tego nie wolno
  sprzedawać), **kontrola temperatury części prądowych we wtyczce** (nowość w wyd. 2024).
- **Polska, UDT:** badaniom UDT podlegają **stacje ładowania** i punkty będące elementem
  infrastruktury ładowania drogowego transportu publicznego — badanie przed oddaniem do
  eksploatacji oraz po naprawie/modernizacji. **Wyłączone: stacje prywatne do użytku własnego
  i gniazda będące elementem instalacji budynku.** Podstawa: nowelizacja ustawy
  o elektromobilności, obowiązuje od 24 XII 2021.
- **Rozporządzenie maszynowe (UE) 2023/1230** — od 20 I 2027 zastępuje dyrektywę 2006/42/WE,
  bez okresu przejściowego. Ładowarek nie dotyczy; w rozmowie pojawiło się jako analogia
  (bramy Nice/CAME, paczkomaty InPost).

### 5.3. KOREKTA wcześniejszego zapisu

W pliku `AmperePoint-Shelly - analiza` (wersja z 20 IX 2026) napisano, powołując się na
opracowania branżowe, że od 1 I 2027 obowiązek ISO 15118-20 obejmie „nowo instalowane punkty
publiczne **i prywatne**". Weryfikacja 22 IX 2026 pokazuje, że **AFIR wiąże operatorów punktów
publicznie dostępnych**, a wątek „prywatny" pochodzi z EPBD i dotyczy budynków, nie sprzętu
wprowadzanego do obrotu. Tabela kalendarza w analizie wymaga poprawki przy najbliższej edycji.

### 5.4. Granica: instalacja stała a urządzenie z wtyczką (sprawdzone 2026-09-22)

- Granica instalacji stałej budynku biegnie **na gnieździe**. Wszystko za gniazdem to
  odbiornik (urządzenie) i podlega prawu wyrobowemu, nie instalacyjnemu.
- O klasyfikacji decyduje **sposób przyłączenia (wtyk vs przewód na stałe)**, a nie to, czy
  urządzenie wisi na ścianie. Powieszenie przenośnej ładowarki na uchwycie niczego nie zmienia.
- Jeśli instalator obetnie wtyk i podłączy urządzenie na stałe → użycie niezgodne
  z przeznaczeniem; deklaracja producenta tej konfiguracji nie obejmuje. Analogia potwierdzona
  w branży bram: **instalator, który łączy napęd z bramą, staje się „producentem" zestawu
  i odpowiada za CE całości.**
- Ale gniazdo też nie jest wolne od wymagań: **PN-HD 60364-7-722** (obwody do zasilania
  pojazdów elektrycznych) wymaga m.in. osobnego obwodu na punkt, RCD ≤30 mA na każdy punkt
  przyłączeniowy, wykrywania składowej stałej >6 mA, jedno gniazdo = jeden pojazd,
  współczynnik jednoczesności 1. Różnica: to spełnia elektryk raz, przy gnieździe.
- Polska, UDT: wyłączone stacje prywatne do użytku własnego i gniazda będące elementem
  instalacji budynku (patrz 5.2).

### 5.5. Kto wystawia deklarację zgodności (sprawdzone 2026-09-22)

- **NIE fabryka.** Producentem w rozumieniu prawa jest ten, kto wprowadza wyrób do obrotu
  **pod własną nazwą lub znakiem towarowym**. AmperePoint na obudowie = AmperePoint jest
  producentem ze wszystkimi obowiązkami, mimo że fizycznie produkuje fabryka w Chinach
  (tzw. own-brander). Importer/dystrybutor, który nakłada własną markę, przejmuje obowiązki
  producenta.
- Obowiązki producenta: dokumentacja techniczna, procedura oceny zgodności, deklaracja
  zgodności UE, oznakowanie CE, identyfikowalność (typ/partia/adres), archiwizacja (zwykle
  10 lat), nadzór nad wyrobem na rynku, działania naprawcze. Rozporządzenie (UE) 2019/1020
  wymaga też podmiotu odpowiedzialnego z siedzibą w UE.
- Akty dotyczące ładowarki z Wi-Fi: **LVD** 2014/35/UE, **EMC** 2014/30/UE, **RED**
  2014/53/UE (+ cyber od 1 VIII 2025, EN 18031), **RoHS** 2011/65/UE, **GPSR** 2023/988,
  WEEE, 2019/1020.
- Certyfikat modułu radiowego **nie zwalnia** z oceny całego wyrobu — to jest sedno pytania,
  które padło na spotkaniu („wydajecie RED-a do tego?").

### 5.6. Normy wyrobu: 61851-1 vs 62752 vs 62955 (sprawdzone 2026-09-22)

- **IEC/EN 61851-1** — ogólna norma przewodowych systemów ładowania EV; opisuje m.in. Mode 3
  (EVSE przyłączone na stałe), sygnalizację Control Pilot / PWM, sekwencje, blokadę wtyku.
  Od aktualizacji z 2017 r. dla Mode 3 wymagane wykrywanie gładkiej składowej stałej 6 mA:
  albo **RCD typu B**, albo **RCD typu A + RDC-DD** wg **IEC 62955**. Producenci wallboxów
  najczęściej wybierają A + RDC-DD (taniej, prostsza instalacja).
- **IEC/EN 62752** (wyd. 2024) — IC-CPD dla Mode 2: wbudowany RCD ≤30 mA, obowiązkowe
  wykrywanie 6 mA DC (bez tego nie wolno sprzedawać od 1 I 2018), **kontrola temperatury
  części prądowych we wtyczce domowej** (nowość wyd. 2024), wymagania dla wtyku wg norm
  krajowych lub IEC 60884-1.
- Logika różnicy: Mode 2 może trafić do nieznanej instalacji → musi nosić ochronę ze sobą;
  Mode 3 zakłada zaprojektowany obwód → część ochrony może być w rozdzielnicy.
- Rozwinięcia: RCD = Residual Current Device; RDC-DD = Residual Direct Current Detecting
  Device; IC-CPD = In-Cable Control and Protection Device; CP = Control Pilot.

### 5.7. Dyrektywa/rozporządzenie maszynowe — szczegóły (sprawdzone 2026-09-22)

- Dziś dyrektywa **2006/42/WE**; od **20 I 2027** rozporządzenie **(UE) 2023/1230**, bez
  okresu przejściowego (nie ma momentu, w którym obowiązują oba).
- Definicja maszyny: zespół **wyposażony w układ napędowy inny niż bezpośrednio przyłożona
  siła ludzka lub zwierzęca**, złożony z połączonych części, z których co najmniej jedna się
  porusza. ← To zdanie jest podstawą wszystkich prób przeklasyfikowania produktu.
- Obowiązki: ocena ryzyka (EN ISO 12100), funkcje bezpieczeństwa i ich poziom (EN ISO 13849-1
  — Performance Level a–e; lub EN 62061 — SIL), dokumentacja techniczna, instrukcja w języku
  kraju, deklaracja + CE. Dla kategorii z **załącznika I część A** — obowiązkowa jednostka
  notyfikowana (koniec samodzielnej deklaracji).
- Nowości 2023/1230: cyberbezpieczeństwo, oprogramowanie i uczenie maszynowe w funkcjach
  bezpieczeństwa (automatycznie wysokie ryzyko → jednostka notyfikowana), instrukcje cyfrowe,
  **istotna modyfikacja** (kto istotnie modyfikuje maszynę, staje się jej producentem).
- Bramy: napędzane bramy są maszynami; zestaw norm EN 12445, EN 12453, EN 12635, EN 13241.
  Instalator łączący napęd z bramą = producent zestawu.
- Dlaczego się to omija: koszt i czas oceny ryzyka oraz badań, konieczność dołożenia
  zabezpieczeń (fotokomórki, listwy krawędziowe, ograniczenie siły wg EN 12453), poziom
  nienaruszalności funkcji bezpieczeństwa, odpowiedzialność osobista, a przy załączniku I —
  jednostka notyfikowana. Typowy chwyt: usunąć układ napędowy (np. sprężyna naciągana przez
  człowieka + elektromagnetyczne zwolnienie) → formalnie nie maszyna. Tak omawiano paczkomaty.

## 6. Zadania i pytania otwarte projektu

Po stronie AmperePoint: lista funkcji w 3 horyzontach („dziś 1:1", „za chwilę", „na jutro"),
analiza gap wobec TopAC. Po stronie Shelly: dev kit + ładowarka TopAC + przekładnik 120 A,
call z Borisem (przesunięty za targi — Kongres Nowej Mobilności, Katowice).

Pytania bez odpowiedzi: który moduł X0–X4 pasuje pinoutem do WBR3 i jaka dokładnie pamięć;
kto pisze i utrzymuje warstwę protokołu do MCU ładowarki; OCPP lokalnie czy tylko przez chmurę;
zakres dokumentacji RED/EN 18031 po stronie Shelly; eksport danych i ciągłość przy zmianie
właściciela Shelly; stawka lokalnego PM/inżyniera w Chinach; warunki handlowe i rabaty;
termin brandowanej strony produktowej w aplikacji.

## 7. Dziennik zmian

- **2026-09-17** — transkrypcja Recording_33, dokumenty .md + .pdf.
- **2026-09-20** — transkrypcja Recording_34; analiza 47 stron.
- **2026-09-21** — usunięcie z analizy wszystkich odwołań do nagrań.
- **2026-09-22** — założenie tego pliku; weryfikacja różnic regulacyjnych przenośne vs
  stacjonarne (sekcja 5) i korekta wcześniejszego zapisu o AFIR.
- **2026-09-22 (druga tura)** — **korekta o AFIR WPROWADZONA do pliku analizy**: poprawione
  sekcje „Regulacje" (dodany akapit „Kogo wiąże" + wyjaśnienie, że wątek prywatny pochodzi
  z EPBD), tabela kalendarza (wiersz 2027 + nowy wiersz EPBD) i punkt 5 streszczenia. PDF
  przebudowany. Dopisane sekcje 5.4–5.7 kompendium: granica instalacja/urządzenie, role
  w ocenie zgodności, porównanie norm wyrobu, szczegóły prawa maszynowego.
