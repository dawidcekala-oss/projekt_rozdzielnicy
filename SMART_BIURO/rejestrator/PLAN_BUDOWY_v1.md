# Plan budowy rejestratora złącza — krok po kroku (v1)

**SMART_BIURO / rejestrator · 2026-09-04 · plan wykonawczy dla jednej osoby z lutownicą**

Ten dokument mówi wyłącznie CO robić, W JAKIEJ KOLEJNOŚCI i JAK sprawdzić, że
zrobione jest dobrze. Uzasadnienia projektowe i wszystkie liczby są w dokumencie
`AMPERE_POINT_rejestrator_zlacza_Q11_v2.pdf` (w tym folderze), a mapa wszystkich
połączeń — na schemacie `AMPERE_POINT_rejestrator_Q11_schemat_PELNY.png`.
Przy lutowaniu pracuje się ze schematem otwartym obok.

Zasada planu: **po każdym etapie jest SPRAWDZENIE. Nie przechodzi się do
następnego etapu, dopóki sprawdzenie nie wyjdzie.** Dzięki temu błąd zawsze
szuka się w jednym, ostatnio zlutowanym kawałku, a nie w całej płytce.

Każde słowo techniczne jest wyjaśnione przy pierwszym użyciu.

---

## Etap 0 — inwentaryzacja: co masz, czego brak, co czym zastępujemy

| Element | Stan | Uwagi |
|---|---|---|
| CD4051BE (multiplekser) | jest, 3 szt. | do układu idą 2, trzeci to zapas |
| Podstawki DIP-16 | są, 3 szt. | pod CD4051BE |
| Podstawka DIP-8 | jest | zostanie pusta — czeka na komparator |
| LM393 (komparator) | **BRAK** (niekupiony koszyk Conteo) | budujemy bez niego — patrz etap 9 |
| Diody 1N4148 | są, 100 szt. | zużyjemy ok. 40 |
| Zestaw kondensatorów ceramicznych | jest | potrzebne wartości: patrz niżej |
| Rezystory | z Twojej gamy | 100 kΩ ×~40, 120 kΩ ×3, 220 kΩ ×5, 10 kΩ ×~15, 1 MΩ ×1, 2×10 kΩ na dzielnik testowy |
| Płytki uniwersalne 5×7 cm | są | jedna będzie płytką rejestratora |
| Kupione złącze IDC20 | jest, ale NIE PASUJE | idzie do szuflady; wpięcie robimy ogonami z taśmy dawcy |
| Taśma z ładowarki-dawcy | jest (w dawcy) | kluczowy element — etap 1 |
| Arduino UNO | jest (z zapasów) | plus kabel USB i laptop |

**Jak znaleźć właściwe kondensatory w zestawie.** Na małych kondensatorach nie
ma napisu „1 nF" — jest trzycyfrowy kod: dwie pierwsze cyfry to wartość,
trzecia to liczba zer, wynik w pikofaradach (pF). Szukasz czterech kodów:

| Kod na kondensatorze | Wartość | Ile sztuk potrzeba | Gdzie idzie |
|---|---|---|---|
| **471** | 470 pF | 4 | wejścia A0, A1, A2, A3 |
| **102** | 1 nF | 2 | filtr toru CT i toru 1.65 |
| **473** | 47 nF | 1 | detektor szczytu |
| **104** | 100 nF | 2 | przy każdym CD4051BE |

Jeśli w zestawie nie ma kodu 471: weź dwa kondensatory 221 (220 pF) i przy
lutowaniu daj je obok siebie w ten sam punkt (pojemności łączone równolegle
się sumują: 440 pF — dokument dopuszcza tu wszystko od 330 do 680 pF).

Narzędzia: lutownica z cyną i topnikiem, obcinaczki, multimetr, marker
wodoodporny, lupa, suwmiarka (albo linijka), taśma izolacyjna.

---

## Etap 0a — BRAMKA DECYZYJNA: czy ładowarka toleruje nasz odczep

**Po co ten etap:** pomiar sondą oscyloskopu (wejście ~1 MΩ) w stanie
ładowania wywołał błąd „wiring abnormality" — ładowarka aktywnie pilnuje
swoich węzłów pomiarowych i wykrywa obce obciążenia. Nasz odczep obciąża
węzeł ~100× słabiej niż sonda (mikroampery zamiast setek mikroamperów),
co wynika z rachunku — ale zanim polutujesz 19 odczepów, sprawdzamy ten
rachunek JEDNYM odczepem, za cenę godziny. Wszystkie odczepy to kopie tej
samej impedancji, a każdy węzeł ładowarki widzi tylko swój własny odczep —
więc jeden odczep na najczulszym węźle testuje najgorszy przypadek całości.

**Przygotowanie (na stole):** zlutuj jeden „latający" odczep typu P na
kawałku przewodu: końcówka pomiarowa → 100 kΩ → 100 kΩ → węzeł z klamrą
(dioda paskiem do +5 V, dioda paskiem do węzła — jak w etapie 8) → 10 kΩ →
przewód sygnałowy; plus przewód masy i przewód +5 V. Zasilenie klamry
i odczyt: UNO z wgranym programem testowym (sygnał na A0), najlepiej
zasilane z POWERBANKU — wtedy w pierwszej próbie laptop w ogóle nie
uczestniczy.

**Warunek ważności testu — zamknięta pętla.** Sam drut na węźle niczego
nie dowodzi, bo bez drogi powrotnej prąd nie płynie. Test wykonuje się
ZAWSZE z podłączonym przewodem masy (masa UNO → pin GND złącza) i z UNO
wykonującym pomiary — dopiero wtedy płynie dokładnie ten prąd, który
będzie płynął w gotowym rejestratorze: węzeł → 200 kΩ → wejście i klamra →
masa UNO → przewód masy → masa płytki kontrolnej. Pełny rejestrator na
danym węźle nie przyłoży nigdy nic więcej niż ten jeden odczep.

**Przebieg (na SPRAWNEJ ładowarce):**
1. Najpierw wykonaj na sprawnym egzemplarzu pomiar charakteru masy —
   dokładnie procedura z etapu 4. Wynik „masa związana z siecią" = STOP
   także dla tego testu.
2. Ładowarka odłączona od sieci (procedura beznapięciowa): przyczep
   przewód pomiarowy odczepu do pola lutowniczego wybranego pinu złącza,
   przewód masy do pina GND. Nic nie dotykamy po załączeniu.
3. Załącz ładowarkę, doprowadź do stanu ładowania, odczekaj **30 minut**.
4. Powtórz dla kolejnych węzłów. Kolejność:
   - **V1** — węzeł napięciowy (ten typ węzła przewrócił oscyloskop),
   - **CT** — główny podejrzany śledztwa,
   - **8V, z odczepem uzupełnionym o 220 kΩ z węzła klamry do masy**
     (czyli typ D) — to test drugiej klasy obciążenia: odczepy K1–K4 i 8V
     pobierają celowo ~18 µA, nie tylko upływ. Po tych trzech przebiegach
     bramka pokrywa każdy rodzaj obciążenia, jaki pełny układ przyłoży
     do któregokolwiek węzła.

**Decyzja:**

| Wynik | Znaczenie | Co dalej |
|---|---|---|
| 30 min ładowania bez błędu na wszystkich trzech węzłach | ładowarka nie widzi odczepów | budujemy — etapy 1 i dalej |
| błąd tylko przy V1 | węzły napięciowe za czułe | linie V1–V3 wypadają z obserwacji (wartość drugorzędna), pozostałe przebiegi kontynuować |
| błąd przy CT lub przy 8V (typ D) | koncepcja odczepów do rewizji | budowy NIE zaczynać — wracamy do analizy, koszt: godzina zamiast całej konstrukcji |

Uwaga do skali: pełny rejestrator pobiera przez wspólny przewód masy sumę
prądów wszystkich odczepów (~0,2 mA). Ta suma wraca do własnej masy płytki
kontrolnej — obwodu niskonapięciowego, poza czujnikiem prądu różnicowego
toru mocy — i jest niemierzalna na tle dziesiątek miliamperów, które ta
masa i tak prowadzi. Dlatego o „widzialności" rejestratora decydują węzły
pojedynczo, a nie suma — i dlatego test pojedynczych odczepów jest
reprezentatywny dla całości.

---

## Etap 1 — ogony przyłączeniowe z taśmy dawcy

**Cel:** dwa odcinki taśmy, każdy z fabryczną wtyczką na jednym końcu
i przygotowanymi do lutowania żyłami na drugim.

**Po co:** kupione złącze nie pasuje do wtyczki fabrycznej, więc rejestrator
nie dostanie gniazd — dostanie dwa kablowe „ogony" zakończone oryginalnymi
wtyczkami z taśmy dawcy. Oryginał pasuje do oryginału z definicji.

**Wykonanie:**
1. Wypnij taśmę komunikacyjną z obu złączy ładowarki-dawcy (urządzenie
   odłączone od sieci).
2. ZANIM cokolwiek przetniesz: znajdź żyłę numer 1. Na taśmach jest zwykle
   oznaczona kolorem (czerwony pasek na skrajnej żyle); jeśli nie ma —
   wybierz jedną skrajną i oznacz ją markerem **przy obu wtyczkach** oraz
   w połowie długości taśmy, po obu stronach przyszłego cięcia.
3. Przetnij taśmę w połowie długości, prosto, ostrymi nożyczkami.
4. Na każdej połówce: rozdziel żyły na końcowych ~2 cm (taśma rwie się
   wzdłuż rowków palcami), zdejmij ~3 mm izolacji z każdej żyły, skręć
   i pocynuj końcówki (dotknij lutownicą z odrobiną cyny, żeby druciki
   się nie strzępiły).

**Sprawdzenie:** multimetr w trybie ciągłości (piszczy przy połączeniu).
Do styku we wtyczce dochodzi się cienkim drucikiem albo szpilką włożoną
w otwór styku. Dla KAŻDEJ z 20 żył obu połówek: styk we wtyczce ↔
pocynowany koniec tej samej żyły — musi piszczeć; sąsiednia żyła — nie może.

**Pułapka:** zgubienie numeracji żył po przecięciu. Jeśli masz wątpliwość,
która żyła jest którą — rozstrzyga test ciągłości od strony wtyczki, bo
kolejność styków we wtyczce jest stała.

---

## Etap 2 — rozplanowanie płytki i przelot

**Cel:** płytka 5×7 cm z wlutowanymi obydwoma ogonami i „przelotem" —
czyli takim połączeniem, że każda żyła ogona A jest zwarta z tą samą żyłą
ogona B. Wpięta między płytki ładowarki niczego jeszcze nie mierzy, ale
ładowarka przez nią działa jak przez zwykłą taśmę.

**Po co przelot najpierw:** to szkielet całego rejestratora. Wszystkie
późniejsze elementy pomiarowe tylko DOTYKAJĄ tych 20 linii — nie przerywają
ich. Jak przelot działa, to najgorsze ryzyko (pomieszanie linii) masz z głowy.

**Wykonanie:**
1. Markerem podziel płytkę na strefy (patrząc na schemat): wzdłuż jednej
   krawędzi pas na przelot (2 rzędy po 20 otworów), dalej szeroki pas na
   odczepy, potem pas na dwa multipleksery, przy przeciwnej krawędzi pas
   na tory CT/1.65/CP i wiązkę do UNO.
2. Wlutuj 20 żył ogona A w jeden rząd otworów, obok — 20 żył ogona B
   w drugi rząd. Kolejność ta sama (żyła 1 obok żyły 1). Ogony wychodzą
   z płytki w tę samą stronę; przy krawędzi przywiąż je opaską przez dwa
   otwory płytki, żeby szarpnięcie za kabel nie zrywało lutów.
3. Połącz pary punktów drutem lub mostkiem z cyny: A1↔B1, A2↔B2 … A20↔B20.
   Przy każdej parze zostaw wolny sąsiedni otwór — tam w etapie 6 wejdą
   odczepy.
4. Podpisz markerem na laminacie co którą linię: nazwy pinów przepisz ze
   schematu (PE, NTC1, ICP, 8V, K1…). UWAGA: która żyła taśmy to który
   sygnał, wynika z tego, w który pin złącza ładowarki trafia dana żyła —
   rozstrzygniesz to ostatecznie w etapie 3 testem ciągłości na dawcy
   i wtedy poprawisz podpisy.

**Sprawdzenie:** dla każdej z 20 linii: styk we wtyczce A ↔ styk we
wtyczce B (ciągłość, musi piszczeć) oraz styk we wtyczce A ↔ obie SĄSIEDNIE
linie (nie może piszczeć). To wykrywa mostki cynowe — najczęstszy błąd na
płytce uniwersalnej.

---

## Etap 3 — pasowanie i mapa sygnałów na ładowarce-dawcy

**Cel:** pewność, że wtyczki wchodzą, zatrzaskują się, taśmy sięgają,
i że wiesz, która linia na Twojej płytce to który sygnał.

**Wykonanie (dawca CAŁY CZAS odłączony od sieci):**
1. Wepnij ogon A w złącze płytki mocy dawcy, ogon B w złącze płytki
   kontrolnej. Sprawdź zatrzaski i czy obudowa ładowarki da się w tym
   stanie sensownie ułożyć (płytka rejestratora musi się gdzieś zmieścić).
2. Mapa sygnałów: pinout złącza jest na schemacie (wkładka „Fizyczny układ
   złącza 2×10"). Multimetrem w trybie ciągłości: pin złącza na płytce
   dawcy (np. ten opisany na laminacie jako CT) ↔ kolejne punkty przelotu
   na Twojej płytce, aż znajdziesz piszczący. Podpisz. Powtórz dla
   wszystkich 20.
3. Popraw podpisy na płytce, jeśli w etapie 2 były „na wiarę".

**Sprawdzenie:** komplet 20 podpisanych linii, w tym: GND, drugi GND, PE.
Na liniach PE i drugim GND narysuj markerem krzyżyk — **te dwie zostają
gołym przelotem na zawsze, żadnych elementów** (powód: §5.2 dokumentu).

---

## Etap 4 — pomiary bramkowe na ładowarce BADANEJ

**Cel:** decyzja, czy w ogóle wolno prowadzić sesje z laptopem.

**Po co:** rejestrator łączy masę ładowarki z masą UNO, a przez kabel USB —
z laptopem. Jeżeli masa ładowarki jest połączona z siecią energetyczną,
to na obudowie laptopa może pojawić się napięcie sieci. Ten etap to
wyklucza ALBO zatrzymuje projekt — dlatego jest przed dalszą budową.

**Wykonanie — część 1 (ładowarka ODŁĄCZONA, wtyczka wyjęta, odczekaj minutę):**
multimetr w trybie omomierza (pomiar rezystancji). Mierzysz między pinem
GND złącza a kolejno: zaciskiem N, zaciskami L1/L2/L3, zaciskiem PE.
Każdy pomiar wykonaj DWA RAZY z zamienionymi końcówkami miernika —
w zasilaczach są elementy przewodzące tylko w jedną stronę, więc wynik
może zależeć od strony przyłożenia; liczy się gorszy (niższy) wynik.

**Wykonanie — część 2 (ładowarka zasilona, rejestrator NIEPODŁĄCZONY):**
multimetr w trybie napięcia: GND → PE, raz na zakresie napięcia stałego,
raz zmiennego.

**Sprawdzenie / decyzja:**

| Wynik | Znaczenie | Co dalej |
|---|---|---|
| każda rezystancja do N i L powyżej 1 MΩ ORAZ napięcie GND→PE poniżej 50 V | masa pływająca | sesje dozwolone (laptop na baterii) |
| cokolwiek poniżej 1 MΩ do N lub L, LUB powyżej 50 V | masa związana z siecią | **sesji nie prowadzić** — wróć do dokumentu §5.2, temat eskalujemy |

Wynik zapisz (wartości, data) — to dokument bezpieczeństwa całego projektu.

---

## Etap 5 — szyny zasilania i wiązka do UNO

**Cel:** na płytce są dwie szyny (dłuższe ścieżki zbiorcze): masa i +5 V,
oraz wiązka przewodów do UNO.

**Wykonanie:**
1. Wyznacz na płytce dwie równoległe linie otworów: szynę masy i szynę
   +5 V (drut wzdłuż rzędu otworów). Podpisz.
2. Szynę masy połącz drutem z punktem przelotu linii **GND** (ten właściwy,
   nie „drugi GND" z krzyżykiem). To jest JEDYNE połączenie masy
   rejestratora z ładowarką.
3. Wiązka do UNO — przewody z pinami, które masz. Docelowo zajęte będą:
   A0, A1, A2, A3, A4, D4, D5, D6, D8 (na przyszłość), GND, 5V.
   GND wiązki → szyna masy; 5V wiązki → szyna +5 V. Resztę przewodów
   podłączaj w miarę etapów.

**Sprawdzenie:** omomierzem szyna masy ↔ szyna +5 V: NIE może piszczeć
(zwarcie zasilania to najgorszy błąd). Potem UNO na USB: multimetrem
napięcie między szynami ≈ 5 V.

**ŻELAZNA ZASADA ZASILANIA (wniosek z awarii ESP32):** jedynym źródłem
zasilania UNO jest USB. **Nigdy, w żadnym momencie, nie wolno podłączyć
do UNO drugiego zasilania** — przetwornicy, wejścia VIN, ani tym bardziej
linii 8V/12V z ładowarki — równolegle z wpiętym USB. Dokładnie taka
konfiguracja (przetwornica + USB naraz, bez diody zaporowej) uszkodziła
port komputera i pamięć ESP32. Linia 8V ładowarki jest w rejestratorze
wyłącznie PODSŁUCHIWANA przez rezystory 420 kΩ (18 µA) — nie jest i nigdy
nie będzie zasilaniem.

---

## Etap 6 — multipleksery

**Co to jest, po ludzku:** CD4051BE to elektroniczny przełącznik obrotowy.
Ma 8 wejść i jedno wyjście; trzema sygnałami sterującymi (adres) wybiera
się, które wejście jest w danej chwili połączone z wyjściem. Dzięki dwóm
takim układom 16 wolnozmiennych sygnałów ładowarki czyta się dwoma
wejściami UNO.

**Obudowa i numeracja nóżek:** układ jest w obudowie DIP-16 — 16 nóżek
w dwóch rzędach. Na jednym końcu obudowy jest wcięcie (albo kropka):
patrząc z góry, nóżka 1 jest na lewo od wcięcia, numeracja biegnie w dół
lewym rzędem (1–8) i wraca górą prawym (9–16). Podstawka ma to samo
wcięcie — wlutuj podstawki tak, żeby wcięcia obu były po tej samej stronie,
a układy wkładaj dopiero po zlutowaniu wszystkiego wokół.

**Nóżki CD4051BE i co gdzie podłączyć (oba układy identycznie, poza wyjściem):**

| Nóżka | Nazwa | Podłączenie | Po co |
|---|---|---|---|
| 16 | VDD | szyna +5 V | zasilanie |
| 8 | VSS | szyna masy | masa |
| 7 | VEE | szyna masy | „zasilanie ujemne" — potrzebne tylko przy sygnałach poniżej masy, u nas ich nie ma |
| 6 | INH | szyna masy | wyłącznik układu; przy masie układ jest zawsze włączony |
| 11 / 10 / 9 | A / B / C | D4 / D5 / D6 na UNO — **oba układy równolegle** | adres, czyli wybór kanału |
| 3 | wyjście wspólne | MUX1 → A2, MUX2 → A3 | tu pojawia się napięcie wybranego kanału |
| 13, 14, 15, 12, 1, 5, 2, 4 | kanały 0–7 | wejścia — na razie WOLNE (podłączą się w etapie 8) | |

Do tego przy każdym układzie: kondensator **104** (100 nF) między nóżką 16
a 8, jak najbliżej obudowy (tłumi zakłócenia zasilania), oraz kondensator
**471** (470 pF) z wyjścia (nóżka 3) do masy. Kanał 7 DRUGIEGO multipleksera
połącz od razu drutem do szyny masy — to samokontrola: ten kanał ma zawsze
czytać zero, a jeśli przestanie, znaczy że rejestrator kłamie.

**Sprawdzenie:** przed włożeniem układów w podstawki — omomierz +5 V↔masa
(brak zwarcia). Po włożeniu i zasileniu UNO: na nóżce 16 ma być ~5 V,
na 8/7/6 — 0 V. Pełny test funkcji zrobi program w etapie 7.

---

## Etap 7 — program testowy nr 1

**Co to jest:** w folderze `test_multiplekserow\` leży plik
`test_multiplekserow.ino` — program dla UNO (otwiera się w Arduino IDE,
wgrywa przyciskiem ze strzałką). Program co sekundę przełącza adresy 0–7
i wypisuje w oknie „Monitor portu szeregowego" (lupka w prawym górnym rogu
IDE, prędkość 115200) tabelkę odczytów.

**Jednostki:** UNO mierzy napięcia w krokach 0–1023, gdzie 0 = 0 V,
a 1023 = 5 V; jeden krok ≈ 5 mV. Program wypisuje i kroki, i wolty.

**Wykonanie testu:**
1. Zbuduj dzielnik testowy: dwa rezystory 10 kΩ w szereg między szyną
   +5 V a masą; w punkcie środkowym jest dokładnie połowa napięcia, ~2,5 V.
2. Podłącz punkt środkowy drutem do wybranego kanału, np. kanału 2
   pierwszego multipleksera (nóżka 15).
3. Wgraj program, otwórz monitor.

**Sprawdzenie zaliczone, gdy:**
- przy adresie 2 kolumna MUX1 pokazuje ~512 (±15), a przy innych adresach
  co innego;
- przy adresie 7 kolumna MUX2 pokazuje 0–3 (to ten kanał masy);
- kanały, do których nic nie podłączono, pokazują wartości przypadkowe
  i „pływające" — to NORMALNE (wejście wisi w powietrzu i łapie wszystko);
  niepokoić ma się dopiero ten, kto widzi pływanie na kanale PODŁĄCZONYM.

Przełóż dzielnik na 2–3 inne kanały (w tym drugi multiplekser) i potwierdź,
że wartość „chodzi" za właściwym adresem i właściwą kolumną.

---

## Etap 8 — odczepy

**Co to jest, po ludzku:** odczep to trzy elementy między linią ładowarki
a wejściem multipleksera: dwa rezystory 100 kΩ (ograniczają prąd tak, że
podsłuch jest dla ładowarki niewyczuwalny i bezpieczny), para diod
(klamra — pilnuje, żeby na wejście multipleksera nigdy nie weszło napięcie
spoza zakresu 0–5 V) i rezystor 10 kΩ (dodatkowa ochrona samego wejścia).

**Kierunki diod — jedyne miejsce, gdzie łatwo o błąd.** Na szklanej diodzie
1N4148 czarny pasek oznacza katodę. W punkcie za rezystorami (nazwijmy go
węzłem):
- dioda „górna": **pasek do szyny +5 V**, koniec bez paska do węzła;
- dioda „dolna": **pasek do węzła**, koniec bez paska do szyny masy.
Łatwo zapamiętać: oba paski „patrzą w górę" — w stronę +5 V.

**Dwa typy odczepów:**
- **typ P** (9 linii: V1, V2, V3, ZL1, ZL2, ZL3, ICP, NTC1, NTC2):
  linia → 100 kΩ → 100 kΩ → węzeł (klamra) → 10 kΩ → kanał multipleksera;
- **typ D** (5 linii: K1, K2, K3, K4, 8V): jak typ P **plus** rezystor
  220 kΩ z węzła do masy. Ten rezystor obniża napięcie o połowę (dokładnie
  ×0,524), bo te linie mają ~7,45 V — za dużo na wejście UNO wprost.

**Który odczep w który kanał** (jak na schemacie):

| Kanał | MUX1 | MUX2 |
|---|---|---|
| 0 | V1 | K1 |
| 1 | V2 | K2 |
| 2 | V3 | K3 |
| 3 | ZL1 | K4 |
| 4 | ZL2 | 8V |
| 5 | ZL3 | NTC1 |
| 6 | ICP | NTC2 |
| 7 | detektor szczytu (etap 9) | masa (już podłączona) |

**Wykonanie:** lutuj linia po linii, zawsze w tej samej kolejności
elementów. Pierwszy rezystor 100 kΩ wchodzi w wolny otwór przy punkcie
przelotu danej linii.

**Sprawdzenie — po KAŻDEJ linii, zanim zaczniesz następną:**
1. omomierz: punkt przelotu linii ↔ węzeł klamry ≈ 200 kΩ;
2. test napięciem: punkt środkowy dzielnika testowego (2,5 V) przyłóż
   do punktu przelotu tej linii; program testowy ma pokazać na właściwym
   kanale: **typ P ~512**, **typ D ~268** (bo dzielnik ×0,524). Wartość
   inna niż oczekiwana = błąd w tej jednej linii — szukaj od razu.

---

## Etap 9 — tory szybkie: CT, 1.65 i detektor szczytu

Trzy tory omijają multipleksery i idą wprost do UNO — dokładny przebieg
i wartości są na schemacie (górna część). Skrót wykonawczy:

- **CT → A0:** linia CT → 100 kΩ → 100 kΩ → punkt z kondensatorem 102
  (1 nF) do masy i klamrą → 100 kΩ → punkt z kondensatorem 471 (470 pF)
  do masy → przewód do A0. Kondensatory robią z tego filtr, który
  przepuszcza wolne przebiegi, a tłumi szybkie śmieci.
- **1.65 → A4:** linia 1.65 → 100 kΩ → 100 kΩ → punkt z klamrą
  i kondensatorem 102 do masy → przewód do A4.
- **detektor szczytu → MUX1 kanał 7:** OSOBNA para 100 kΩ + 100 kΩ od tej
  samej linii CT → węzeł z klamrą → dioda 1N4148 szeregowo (pasek W STRONĘ
  kondensatora!) → punkt z kondensatorem 473 (47 nF) do masy i rezystorem
  1 MΩ do masy → 10 kΩ → nóżka 4 pierwszego multipleksera.
  Ten obwód „zapamiętuje" najwyższe napięcie, jakie się pojawiło —
  kondensator ładuje się przez diodę szybko, a rozładowuje przez 1 MΩ
  powoli.

**Sprawdzenie:** dzielnik 2,5 V na linię CT → A0 ma pokazać ~512;
na kanale 7 MUX1 po kilku sekundach ~385 (2,5 V minus ~0,6 V spadku na
diodzie), a po ODŁĄCZENIU dzielnika wartość ma opadać powoli (sekundy) —
to widać gołym okiem w monitorze i to jest właśnie „pamięć szczytu".
Dzielnik na linię 1.65 → A4 ~512.

---

## Etap 10 — tor CP w wersji bez komparatora

**Czego nie będzie i dlaczego:** komparator (LM393 — układ porównujący
napięcie z progiem) nie przyszedł. On w projekcie mierzy WYPEŁNIENIE
przebiegu pilota (stosunek czasu „góry" do całego okresu), z którego wynika
oferowany prąd ładowania. Bez niego rejestrator widzi POZIOMY napięcia
pilota (stany A/B/C — wolny / podłączony / ładowanie), a wypełnienia nie
mierzy. Na diagnostykę „Overload" to na razie wystarczy — wypełnienie
dołożymy później.

**Wykonanie:** linia CP → 120 kΩ → 120 kΩ → węzeł A, do którego dochodzą:
100 kΩ do szyny +5 V, 120 kΩ do masy i klamra. Dalej: 10 kΩ → punkt
z kondensatorem 471 do masy → przewód do A1. Obok wlutuj pustą podstawkę
DIP-8 i zostaw wolne pole — to miejsce przyszłego komparatora, żeby jego
dołożenie nie wymagało przeróbek.

**Sprawdzenie:** przy NIEPODŁĄCZONEJ ładowarce sama sieć rezystorów ustawia
w węźle A napięcie ~2,73 V (dzielnik 100 kΩ na 120 kΩ z 5 V) — program
testowy na A1 ma pokazać **~558 (±20)**. To rzadki luksus: obwód sam sobie
robi test spoczynkowy.

---

## Etap 11 — sucha sesja (pierwszy prawdziwy test całości)

Wszystkie odczepy odłączone od ładowarki (ogony wypięte), punkt środkowy
dzielnika testowego podłączony drutem do KILKU punktów przelotu naraz
(np. CT, 1.65, K1, V1). Program testowy uruchomiony na godzinę; co jakiś
czas spójrz na monitor:
- wartości mają stać w miejscu (drgania o 1–3 kroki to norma);
- kanał masy ma stać na zerze;
- nic nie ma „skakać" przy dotykaniu obudowy laptopa czy włączaniu światła.

To domowa wersja „suchej sesji" z dokumentu (§7.1). Pełną, formalną suchą
sesję robi się już docelowym programem rejestrującym — **gdy dojdziesz do
tego punktu, zgłoś się: dostarczę firmware rejestrujący i skrypt zapisu na
laptopa jako następny krok.** Dalsza droga (sesja na dawcy, sesja bazowa,
sesja właściwa) jest opisana w dokumencie v2, §5.4 i §7.

---

## Kolejność ponownego montażu przy każdej sesji (przypomnienie z §5.4)

1. Ładowarka odłączona od sieci → wepnij ogony.
2. Laptop NA BATERII → USB do UNO (rejestrator zasilony).
3. Dopiero teraz zasilenie ładowarki.
4. Demontaż: ładowarka spod napięcia → dopiero potem reszta.
