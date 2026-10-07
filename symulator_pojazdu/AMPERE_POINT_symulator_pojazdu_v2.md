# Symulator pojazdu elektrycznego — koncepcja v2: aktywna maszyna decyzyjna

**AMPERE POINT · 2026-09-11 · wydanie 2 — zastępuje v1 w całości (v1 pozostaje w folderze jako historia)**

Schemat: **`AMPERE_POINT_symulator_pojazdu_schemat_PELNY.png`** — jeden arkusz,
stan zgodny z tym wydaniem (wklejony na następnej stronie; PNG ma pełną
rozdzielczość). Generator: `generator_schematu_symulatora.py`.

![Pełny schemat symulatora pojazdu — koncepcja v2](AMPERE_POINT_symulator_pojazdu_schemat_PELNY.png)

Odbiorca: technicy serwisu. Wszystkie skróty wyjaśnione przy pierwszym użyciu.
Lista zakupów: celowo ODŁOŻONA do akceptacji koncepcji (osobne wydanie).

## 1. Dlaczego v2 — czego nauczył przypadek modułu Tesli

Wydanie v1 powtarzało błąd ręcznego testera (PM701E): stany wymuszał
człowiek gałką. Taki tester sprawdza ładowarkę wyłącznie na ścieżce
„szczęśliwej" — a prawdziwy pojazd jest przede wszystkim **maszyną
decyzyjną, która potrafi ODMÓWIĆ**. Przypadek z serwisu: ładowarki
z wadliwym modułem zgodności Tesla (zdalne otwieranie klapki) miały
przekłamaną rezystancję PP–PE; samochód odmawiał współpracy i nie zaczynał
ładowania, a na ręcznym testerze wszystko „działało", bo stan C wymuszał
użytkownik. Bez wiedzy o usterce wada przeszłaby niezauważona.

Wniosek konstrukcyjny: **symulator musi odtwarzać proces decyzyjny auta,
nie tylko jego rezystancje.** W v2:

- urządzenie **samo** przechodzi A→B→C — po przejściu wszystkich walidacji,
  które wykonuje pojazd; gdy cokolwiek się nie zgadza, **zostaje w B
  i wyświetla powód odmowy** (przypadek Tesli: „AUTO ODMAWIA: PP = … Ω
  poza tabelą" — w pierwszej sekundzie testu);
- w torze CP **nie ma żadnego ręcznego przełącznika** — w aucie nic nie
  przełącza się manualnie; wszystkie styki załączają przekaźniki sterowane
  przez mikrokontroler;
- dodatkowo symulator **mierzy stoperami wymagania normy wobec STACJI**
  (czasy podania i odcięcia napięcia) — patrz §6;
- tor mocy na pełne **22 kW (3×32 A)** — pod wallboxy PRIME/HM 22 kW —
  z wyjściem do przyszłego magazynu energii (§7, §8).

## 2. Jak stacja i auto rozmawiają — liczby z normy IEC 61851-1

Cała „rozmowa" w ładowaniu AC to linia CP (Control Pilot): stacja podaje
przez rezystor 1 kΩ prostokąt ±12 V / 1 kHz, a pojazd tylko obciąża linię
rezystorami przez diodę (przewodzi wyłącznie dodatnią połówkę — ujemna
zostaje −12 V i po tym stacja poznaje, że po drugiej stronie jest pojazd,
a nie przypadkowa rezystancja).

**Rezystancje pojazdu (Tab. A.2, tolerancje ±3%):** R2 = 2,74 kΩ na stałe;
S2 dokłada R3 = 1,3 kΩ (stan C) albo 270 Ω (stan D — wentylacja); wypadkowo
882 Ω / 246 Ω. Dioda: spadek 0,7 ± 0,15 V.

**Stany (Tab. A.3, poziomy ±1 V):** A: +12 V (brak pojazdu) · B: ~9 V
(podłączony) · C: ~6 V (ładowanie) · D: ~3 V (ładowanie + wentylacja) ·
E: 0 V (zwarcie CP) · F: −12 V (stacja niesprawna).

**Interpretacja wypełnienia PWM przez POJAZD (Tab. A.6)** — to jest tabela
decyzyjna naszej maszyny:

| Wypełnienie | Decyzja pojazdu |
|---|---|
| < 3% | ładowanie ZABRONIONE |
| 3–7% | tylko komunikacja cyfrowa (ISO 15118) → nasz symulator: ODMOWA |
| 7–8% | ZABRONIONE |
| 8–10% | 6 A |
| 10–85% | I = wypełnienie% × 0,6 A |
| 85–96% | I = (wypełnienie% − 64) × 2,5 A |
| 96–97% | 80 A |
| > 97% lub brak PWM | ZABRONIONE |

**Kodowanie kabla na PP (Tab. B.3, ±3%):** 1,5 kΩ → 13 A · 680 Ω → 20 A ·
220 Ω → 32 A · 100 Ω → 63 A. Rezystor siedzi we wtyku kabla, między PP a PE.

**Czasy (Tab. A.7):** POJAZD: otwarcie S2 ≤ 3 s, gdy pilot poza tolerancją
(t_ACoff2); dostosowanie prądu ≤ 5 s po zmianie wypełnienia. STACJA:
napięcie ≤ 3 s po stanie C (t_ACon); odcięcie ≤ 100 ms po otwarciu S2
(t_ACoff1). Dwa ostatnie symulator MIERZY i ocenia (§6).

## 3. Architektura — trzy role w jednej obudowie

1. **Maszyna decyzyjna pojazdu** (§4, §5): rdzeń CP z przekaźnikami +
   mikrokontroler, który zamyka S2 wyłącznie po pełnej walidacji i otwiera
   je zgodnie z czasami normy. To „aktor" grający auto — łącznie z odmowami.
2. **Tester stacji** (§6): pomiary poziomów, wypełnienia, czasów t_ACon
   i t_ACoff1, prądów trzech faz; werdykty PASS/FAIL; automatyczna
   sekwencja scenariuszy usterek.
3. **Tor mocy 22 kW** (§7): przelot 3×32 A do gniazda CEE (magazyn/
   obciążenie) i gniazda 230 V, ze stycznikiem, zabezpieczeniami i E-STOP.

Zasada bezpieczeństwa kierunkowego: **martwy mikrokontroler = wszystkie
przekaźniki opadnięte = symulator w niewinnym stanie B, stycznik otwarty.**

## 4. Rdzeń CP — zero ręcznych styków

- **Gałąź B (R2 = 2,7 kΩ + dioda 1N4148): wlutowana NA STAŁE, bez żadnego
  styku.** Tak jest w aucie — stan B pojawia się sam z chwilą wpięcia
  wtyku, bo przed wpięciem obwód CP fizycznie nie istnieje (to jest
  stan A). Handlowe 2,7 kΩ 1% mieści się w oknie normy: 2,74 kΩ ±3% =
  2,66–2,82 kΩ, a 2,7 kΩ ±1% = 2,673–2,727 kΩ.
- **S2 pojazdu = przekaźnik K2** (dokłada 1,3 kΩ 1%): zamykany przez
  mikrokontroler po przejściu walidacji §5; otwierany przy STOP,
  naruszeniu warunków (≤3 s) i E-STOP.
- **Stan D = przekaźnik K3** (dokłada 270 Ω 1%) — opcja; większość stacji
  nie obsługuje wentylacji, więc to funkcja testowa.
- **Usterki wstrzykiwane — też przekaźniki (menu serwisowe):**
  - **KF1** — bocznik diody (zwarta dioda: ujemna połówka przestaje
    trzymać −12 V; poprawna stacja musi wykryć i odmówić),
  - **KF2** — styk **NC (spoczynkowo zamknięty)** w linii CP: podanie
    cewki = „zanik pojazdu" mimo wpiętego wtyku; jako NC nie przerywa
    CP przy braku zasilania elektroniki,
  - **KF3** — zwarcie CP–PE (stan E; prąd zwarcia ogranicza 1 kΩ stacji
    do 12 mA — test bezpieczny).
- **Cewki wszystkich pięciu przekaźników przez ULN2003** (posiadany —
  7 kanałów z wbudowanymi diodami gaszącymi) z pinów D7, D9–D12.
- Skutek elektryfikacji usterek: scenariusze można odtwarzać
  **automatyczną sekwencją** — urządzenie samo przechodzi listę
  (normalna sesja, zła dioda, zanik pojazdu, stan E) i drukuje PASS/FAIL
  reakcji stacji. Wymuszenie dowolnego stanu do diagnozy doraźnej —
  z menu serwisowego (program zamyka te same przekaźniki); ręcznym
  testerem pozostaje PM701E.
- Moc rezystorów: najgorszy przypadek (stałe +12 V przy zamkniętych K2+K3)
  to 12²/246 Ω = 0,59 W rozłożone na trzy rezystory — metalizowane 0,6 W
  z zapasem; normalna praca to pojedyncze miliwaty.

## 5. Maszyna decyzyjna — warunki i przebieg (tryb AUTO)

Warunki zamknięcia S2 — **wszystkie naraz**, sprawdzane ciągle:

1. **PP w tabeli B.3** (okna ±3% + margines pomiarowy ±10%); poza oknami →
   pozostajemy w B, komunikat „AUTO ODMAWIA: PP = … Ω poza tabelą".
2. **PWM obecny i wypełnienie w dozwolonym oknie Tab. A.6** (w tym strefy
   zakazane 7–8% i >97%; 3–7% = żądanie komunikacji cyfrowej → odmowa
   z komunikatem „stacja żąda ISO 15118").
3. **Poziomy CP w oknach ±1 V** (mierzone własnym torem §6.1); poziom poza
   oknem → odmowa z wartością („poziom 7,4 V poza oknem stanu B").
4. **Opóźnienie startu upłynęło** (konfigurowalne 0–10 s, domyślnie 2 s —
   odpowiednik automatyzacji startu w autach).
5. **Brak STOP** (przycisk).

Przebieg sesji: wpięcie → B (samoczynnie) → walidacje → K2 zamknięte →
stan C → **równolegle zamyka się stycznik Q1** toru mocy → pomiar t_ACon →
nadzór ciągły (PWM, poziomy, PP, pobór z przekładników vs oferta; zmiana
wypełnienia → aktualizacja limitu i komunikat) → STOP lub naruszenie →
otwarcie S2 (≤3 s od naruszenia, jak każe norma) → pomiar t_ACoff1 →
otwarcie Q1. Przy przekroczeniu poboru: najpierw otwiera się S2 (stacja ma
odciąć w ≤100 ms — to mierzymy), po 200 ms tnie własny stycznik.

Komunikaty na LCD 20×4: stan, wypełnienie %, oferowany prąd [A], kodowanie
kabla, POWÓD ODMOWY, wyniki czasów. Dokładne treści ekranów — do
dopracowania przy uruchomieniu (otwarta kwestia §11).

## 6. Tester stacji — pomiary

### 6.1 Tor CP (sieć przejęta 1:1 z rejestratora Q11)

CP → 2×120 kΩ → węzeł A (100 kΩ→+5 V, 120 kΩ→masa, klamra 2×1N4148) →
10 kΩ → węzeł A′ (470 pF) → A1. Przelicznik U(A) = 1,82 V + 0,152·U(CP).
Wypełnienie: komparator LM393 (próg 0,455 V ≈ CP = −6 V, histereza 470 kΩ,
podciąganie 10 kΩ) → D8, przechwytywanie sprzętowe Timer1 (rozdzielczość
mikrosekundowa). Obciążenie linii CP ≤ 50 µA — stany nieprzekłamane.
Ta sama sieć co w rejestratorze = wspólne wzory, części i wzajemna
weryfikacja obu przyrządów.

### 6.2 Tor PP

+5 V → 1 kΩ → pin PP → A2. Napięcia: 1,5 kΩ → 3,0 V; 680 Ω → 2,0 V;
220 Ω → 0,9 V; 100 Ω → 0,45 V; brak kabla → 5,0 V — rozróżnienie pewne
(odstępy setek miliwoltów).

### 6.3 Detektory faz i stopery stacji

Trzy izolowane detektory obecności napięcia (transoptor za mostkiem
z rezystorami, L1/L2/L3 względem N) → D2/D3/D4 — **przed stycznikiem Q1**,
więc widzą napięcie stacji niezależnie od stanu naszego toru mocy. Z nich:

- **t_ACon**: od zamknięcia S2 do pojawienia się napięcia — PASS ≤ 3 s;
- **t_ACoff1**: od otwarcia S2 do zaniku napięcia — PASS ≤ 100 ms
  (wykrywa m.in. sklejony stycznik stacji);
- które fazy obecne (testy stacji przy „wycinaniu" faz — pojazdy z OBC
  modułowym ładują z 1–3 faz, więc symulator raportuje konfigurację).

### 6.4 Prądy — 3× przekładnik prądowy

Przekładniki dzielone (typu SCT-013, galwanicznie izolowane) na L1/L2/L3 →
A3/A6/A7, **każdy przez tor kondycjonowania**: obciążnik dopasowany do typu
przekładnika + polaryzacja węzła do 2,5 V (dzielnik 2×10 kΩ z +5 V,
kondensator odsprzęgający), bo przetwornik Nano mierzy 0–5 V, a sygnał
przekładnika jest przemienny wokół zera. Wartość skuteczną liczy program.
Zastosowanie: zgodność poboru z ofertą PWM (egzekwowana §5), asymetria faz,
dane do wyświetlacza.

## 7. Tor mocy 22 kW

Gniazdo wlotowe Type 2 **32 A** (panelowe, jak wlot auta — kabel stacji
wpina się wprost) → przewody **6 mm²** → rozłącznik-wyłącznik **B32 3P+N** →
**RCD 30 mA typ A 40 A** → **stycznik Q1 3F 40 A** → licznik energii DIN
z wyświetlaczem (opcja zalecana: U/I/P/kWh podczas ładowania) → **gniazdo
CEE 32 A 5P** (wyjście mocy) oraz — mostkami przez **własny B16 1P** —
gniazdo 230 V do szybkich prób jednofazowych. Obecność faz: 3 kontrolki
neonowe. PE prosto z pinu do obu gniazd, **nigdzie nie przełączane**.

Obwód cewki Q1: L1 → **E-STOP (grzybek, styk NC)** → styk modułu
przekaźnikowego (D6) → cewka → N. E-STOP rozcina cewkę sprzętowo —
weto niezależne od programu; dodatkowo procedura E-STOP otwiera S2,
więc stacja sama odcina w ≤100 ms (druga, niezależna droga).

## 8. Magazyn energii — „samochód bez baterii"

Symulator kończy się tam, gdzie w aucie zaczyna się OBC (ładowarka
pokładowa — przetwornica AC→DC, osobny moduł za stykami): **konwersję
AC→DC wykonuje ładowarka magazynu wpięta w gniazdo CEE**, a symulator
dostarcza całą resztę auta — stany, walidacje, limit prądu z PWM
(wyświetlany i EGZEKWOWANY stycznikiem + przekładnikami). Argument
przeciw wbudowanej przetwornicy 22 kW: koszt wielokrotnie przewyższający
resztę urządzenia, masa i chłodzenie klasy szafy, brak certyfikacji —
przy zerowym zysku wierności symulacji (stacja widzi wyłącznie pobór
prądu, nie to, co się z nim dzieje dalej). Architektura modułowa daje
też elastyczność: dziś grzałka 1-fazowa w gnieździe 230 V, jutro
prostowniki + bateria w CEE — bez zmiany symulatora.
**Decyzja do potwierdzenia w §11** (jeśli jednak przetwornica ma być
wbudowana — to osobny, duży projekt mocy).

Rozbudowa przewidziana: wyjście „limit prądu" do ładowarki magazynu
(styk beznapięciowy lub RS485) i log sesji po USB w formacie wspólnym
z rejestratorem Q11.

## 9. Bezpieczeństwo

- W stanie C gniazda wyjściowe pod napięciem 230/400 V do 32 A/fazę;
  praca tylko z zamkniętą obudową (rozdzielnica hermetyczna z płytą
  montażową, przegroda między torem mocy a elektroniką).
- E-STOP w zasięgu ręki; przed otwarciem obudowy: STOP, wypięcie wtyku
  Type 2, kontrola braku napięcia.
- Po montażu: ciągłość PE od pinu gniazda Type 2 do bolców obu gniazd,
  brak ciągłości L↔PE i N↔PE; test progów walidacji na znanych
  rezystorach przed pierwszym wpięciem w stację.
- Obciążenie dołączane do gniazd ≤ oferta z wyświetlacza i ≤ 32 A.
- Elektronika zasilana wyłącznie z USB (powerbank) — komunikaty działają
  w stanach A/B, zanim stacja poda napięcie; jedyne sprzężenia z torem
  mocy są izolowane (transoptory, przekładniki, cewka stycznika przez
  moduł przekaźnikowy).

## 10. Ograniczenia przyjęte świadomie

- Bez komunikacji cyfrowej (ISO 15118) — wypełnienie 5% jest wykrywane
  i komunikowane, nie obsługiwane; serwisowane serie pracują analogowo.
- Bez siłownika blokady wtyku (stacje nie weryfikują blokady po stronie
  pojazdu; zatrzask mechaniczny gniazda wystarcza).
- Pomiar prądu klasy diagnostycznej (przekładniki dzielone + 10-bitowy
  przetwornik), nie rozliczeniowej — od rozliczeń jest licznik DIN.
- Detektory faz mierzą obecność napięcia, nie jego jakość (zapady/kształt
  — poza zakresem tego urządzenia).
- Poziom CP w stanie F (−12 V) rozpoznawany po zaniku dodatniej połówki
  przy zachowanej ujemnej — bez osobnego toru pomiaru ujemnego szczytu
  (komparator widzi obie połówki, poziomy dodatnie mierzy A1).

## 11. Otwarte kwestie (do decyzji przed dokumentacją wykonawczą)

- **Konwersja AC→DC: potwierdzenie architektury modułowej z §8** — czy
  magazyn z własną ładowarką w CEE, czy przetwornica wbudowana (zmiana
  skali projektu o rząd wielkości);
- wybór konkretnego gniazda wlotowego Type 2 32 A (dostępność/cena);
- RCD: typ A wystarcza dla obciążeń rezystancyjnych; przy ładowarce
  magazynu z przetwornicą rozważyć typ B lub RCD w torze magazynu;
- mikrokontroler: Nano (5 V, Timer1, spójność z rejestratorem) vs ESP32
  (WiFi/logi) — rekomendacja: Nano w wersji 1;
- dokładne treści komunikatów LCD i lista scenariuszy sekwencji
  automatycznej;
- format logu sesji (wspólny z rejestratorem Q11).

## Dziennik iteracji

**Iteracja 1 (2026-09-03, v1).** Projekt początkowy: rdzeń stanów czysto
sprzętowy z ręcznym przełącznikiem obrotowym, elektronika tylko
obserwująca, tor 16 A. ODRZUCONY w całości po weryfikacji użytkownika.

**Iteracja 2 (2026-09-11, v2 — to wydanie).** Po researchu folderu
projektu (norma IEC 61851-1, przypadek modułu Tesla/PP, tester PM701E)
i uwagach użytkownika: (1) symulator przebudowany na AKTYWNĄ maszynę
decyzyjną — sam przechodzi A→B→C i ODMAWIA jak auto (walidacje PP/PWM/
poziomów wg Tab. A.6/B.3/A.3, czasy wg Tab. A.7); (2) z toru CP usunięto
wszystkie ręczne przełączniki — R2 wlutowany na stałe (stan B samoczynny
po wpięciu), S2 = przekaźnik K2, stan D = K3, usterki KF1–KF3 też
przekaźnikami (KF2 jako NC), cewki przez posiadany ULN2003 — dzięki czemu
scenariusze usterek odtwarza automatyczna sekwencja z werdyktami PASS/FAIL;
(3) dodano rolę testera stacji: izolowane detektory faz mierzą t_ACon
(≤3 s) i t_ACoff1 (≤100 ms), przekładniki pilnują zgodności poboru
z ofertą; (4) tor mocy podniesiony do 22 kW (3×32 A: B32, RCD 40 A,
stycznik 40 A z E-STOP w obwodzie cewki, CEE 32 A, 6 mm²); (5) magazyn
energii w architekturze modułowej („samochód bez baterii", konwersja
w ładowarce magazynu jak OBC) — decyzja do potwierdzenia w §11. Poprawki
schematu w tym wydaniu: styk KF2 rysowany jako NC, detektory faz
z podłączonym N, narysowany obwód cewki Q1 z E-STOP, przycisk START/STOP,
B16 1P w gałęzi gniazda 230 V, kondycjonowanie przekładników zaznaczone.
