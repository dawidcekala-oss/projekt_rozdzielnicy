# Zasilanie modułu — obliczenia (wersja 5)

> **SPROSTOWANIE WERSJI 4 (2026-09-01).** Wersja 4 głosiła, że „zasilanie z portu
> COM-MANUAL zostaje porzucone". **To był błędny wniosek.** Użytkownik odrzucił
> **metodę** — rezystor gaszący z kondensatorami — a nie **źródło**. Zasilanie
> z portu przez przetwornicę pozostaje **rozwiązaniem docelowym**.
>
> | Wariant | Status |
> |---|---|
> | port + rezystor gaszący (rozdz. 1–11) | **odrzucony** — trzy nieudane próby, mechanizm wyjaśniony |
> | **port + przetwornica MP1584 (rozdz. 12, 14)** | **DOCELOWY** — pobór spada ze 150 mA do ok. 60 mA |
> | osobny zasilacz 230 V → 12 V (rozdz. 13) | **tymczasowy / awaryjny** — sprawdzony wariant zapasowy |
>
> Różnica między pierwszym a drugim wierszem jest zasadnicza: rezystor nie zmniejsza
> poboru prądu, przetwornica zmniejsza go dwuipółkrotnie. To właśnie pobór blokował
> start jednostki.

> **UWAGA — rozdziały 1–9 opierają się na BŁĘDNYM założeniu i zachowano je wyłącznie
> jako zapis toku rozumowania.** Przyjąłem tam, że płytka WeMos zachowuje się jak
> odbiornik stałej mocy (przetwornica impulsowa, sprawność 85%). Pomiar wykonany później
> dowiódł czegoś innego: to **stabilizator liniowy**, czyli odbiornik **stałego prądu**.
> Zmienia to wszystkie liczby i mechanizm awarii. **Obowiązują rozdziały 10–12.**

**Errata po pierwszym teście polowym (2026-08-22):** wersja 1 z R = 47 Ω zawiodła —
patrz rozdz. 9. Wartość obowiązująca w wersji 2 była **R = 25–28 Ω**; w wersji 3 rezystor
gaszący znika całkowicie — patrz rozdz. 12.

Układ: `+12 V → R ≈ 25 Ω → węzeł z C = 3×100 µF (300 µF) → pin VIN WeMosa`.
Cel obliczeń: wykazać, że układ (1) nigdy nie zablokuje startu klimatyzatora,
(2) zapewnia sondzie stabilne zasilanie w każdym stanie pracy, (3) nie przeciąża
żadnego elementu.

## 1. Dane wejściowe

| Wielkość | Wartość | Skąd |
|---|---|---|
| napięcie linii U | 12 V | pomiar na białej żyle (do potwierdzenia pod obciążeniem) |
| rezystor R | 47 Ω | wybrany; wymagana moc obudowy ≥0,5 W (patrz p. 5) |
| kondensator C | 300 µF (3×100 µF/50 V równolegle) | luźne kondensatory użytkownika |
| pobór sondy (WeMos + bramka) na szynie 5 V | 0,43–0,55 W | ESP8266 z WiFi ~70–85 mA przy 3,3 V przez stabilizator z 5 V + CH340 + bramka |
| sprawność przetwornicy VIN→5 V | ~85% | typowa dla tej płytki |
| **moc pobierana z węzła (P)** | **0,51–0,65 W** | powyższe / 0,85 |
| minimalne napięcie pracy przetwornicy | ~6,5 V (po diodzie na VIN ~0,4 V spadku) | dokumentacja płytki D1 R1 |

Przetwornica jest odbiornikiem „stałej mocy": gdy napięcie na wejściu spada, pobiera
większy prąd, żeby utrzymać moc. To źródło całej trudności i powód, dla którego liczymy.

## 2. Punkt pracy ustalonej

Bilans: prąd przez rezystor I = (12 − V)/R musi pokrywać moc P = V·I.
Stąd równanie kwadratowe: **V² − 12·V + P·R = 0**, rozwiązanie stabilne:
V = [12 + pierwiastek(144 − 4·P·R)] / 2.

| Scenariusz | P | V węzła | I | spadek na R | moc na R |
|---|---|---|---|---|---|
| pobór typowy | 0,51 W | **9,5 V** | 54 mA | 2,5 V | 0,14 W |
| pobór maksymalny ciągły | 0,65 W | **8,3 V** | 78 mA | 3,7 V | 0,29 W |

Wnioski: napięcie węzła 8,3–9,5 V, po diodzie płytki 7,9–9,1 V — **powyżej wymaganych
6,5 V z zapasem**. Prąd z linii 54–78 mA — klasa poboru fabrycznego pilota przewodowego.

Warunek istnienia punktu pracy: 4·P·R < 144, czyli **P < 0,77 W**. Nasz pobór ciągły ma
18–50% zapasu do tej granicy. (Dlatego R nie może być większy: już 2×47 Ω w szereg = 94 Ω
daje granicę 0,38 W — poniżej poboru sondy — układ by nie wystartował.)

## 3. Stabilność punktu pracy

Odbiornik stałej mocy ma ujemną rezystancję przyrostową r = −V²/P. Punkt pracy jest
stabilny, gdy wartość bezwzględna r przekracza R = 47 Ω:

| Scenariusz | r | warunek stabilności |
|---|---|---|
| pobór typowy | −176 Ω | spełniony z zapasem 3,7× |
| pobór maksymalny | −107 Ω | spełniony z zapasem 2,3× |

## 4. Start klimatyzatora (kluczowy dowód bezpieczeństwa)

Najgorsza chwila: powrót zasilania po przerwie, kondensatory rozładowane, zasilacz
jednostki dopiero wstaje.

- **Prąd maksymalny, fizycznie nieprzekraczalny:** I_max = 12 V / 47 Ω = **255 mA** —
  tyle płynie tylko w pierwszej chwili ładowania pustego kondensatora. Linia nie widzi
  nigdy więcej, niezależnie od zachowania przetwornicy. To usuwa mechanizm, który
  wcześniej blokował start (bezpośrednio wpięta przetwornica żądała prądu bez ograniczeń).
- **Czas ładowania:** stała czasowa R·C = 47 Ω × 300 µF = **14 ms**; po ~3 stałych
  (~45 ms) kondensator naładowany, prąd spada do wartości roboczej.
- **Energia wydzielona w R przy starcie:** ½·C·U² = ½ · 300 µF · 144 V² = **21,6 mJ** —
  pomijalna (chwilowe ~0,5 W przez 45 ms).
- Ewentualne kilkukrotne „czknięcie" przetwornicy przy narastaniu napięcia jest
  nieszkodliwe — kondensator ładuje się dalej i układ wchodzi w stabilny punkt pracy.

## 5. Moc rezystora — wymaganie

Praca ciągła: do 0,29 W (scenariusz maksymalny). Zwykły rezystor 0,25 W pracowałby na
granicy lub ponad nią, dlatego:

- **pojedynczy 47 Ω tylko w obudowie ≥0,5 W** (większy fizycznie, gruby),
- **jeśli dostępne tylko 0,25 W → 2× 100 Ω równolegle** (wypadkowa 50 Ω, na każdym po
  ~0,13 W — komfortowo; wszystkie liczby z p. 2–4 zmieniają się kosmetycznie).

## 6. Impulsy nadawania WiFi (rola kondensatora)

Podczas nadawania ESP8266 pobiera chwilowo do ~1,4 W na szynie 5 V (~1,65 W z węzła) —
ponad granicę 0,77 W z p. 2. Deficyt pokrywa kondensator:

- impuls typowy ≤5 ms, deficyt ~1 W → energia z kondensatora ~5 mJ,
- spadek napięcia węzła: z 9,5 V do ~7,5 V (z bilansu energii ½·C·(V1²−V2²) = 5 mJ) —
  wciąż powyżej 6,5 V, praca niezakłócona,
- między impulsami (nadawanie co ~100 ms i rzadziej) kondensator odbudowuje się w ~3×14 ms.

**Przypadek graniczny (uczciwie):** zbieg poboru maksymalnego i długiego impulsu daje
dołek do ~6,0 V — na granicy. Jeśli w testach sonda będzie się resetować, rozwiązanie
jest gotowe: dolutować czwarty kondensator 100 µF/50 V (takie same siedzą na płycie
GK1116 — nadruk `ZKT 100 50V`) → 400 µF spłyca dołek do ~6,6 V.

## 7. Kryteria zaliczenia testu (przed zamknięciem puszki)

| # | Test | Kryterium |
|---|---|---|
| 1 | pomiar linii 12 V pod obciążeniem (sonda pracuje) | ≥11 V (linia nie siada) |
| 2 | pomiar węzła (na kondensatorach) | 8–10 V stabilnie |
| 3 | 3× wyłącz/włącz bezpiecznikiem | jednostka wstaje za każdym razem, sonda też |
| 4 | pilot IR po podłączeniu zasilania | działa |
| 5 | log sondy przez ≥10 minut | komunikacja ciągła, bez restartów (licznik czasu w logu nie zeruje się) |

Niespełnienie kryterium 1 = linia za słaba → plan B (zasilacz fabryczny na 230 V
z listwy). Niespełnienie 5 = powiększyć C (p. 6).

## 8. Montaż — uwagi

- Elektrolity mają biegunowość: **pasek na obudowie = minus = do masy**. Odwrotny montaż
  kończy się rozerwaniem kondensatora.
- Rezystor(y) wlutować w białą żyłę blisko wtyczki, całość w koszulkach termokurczliwych,
  jak reszta wiązki.
- Masa układu już jest wspólna (żółta żyła pigtaila) — kondensatory minusem do niej.
- Pin `VIN` na WeMos — na listwie zasilania obok `GND`/`5V` (uwaga: to wejście przez
  diodę do przetwornicy; przy zasilaniu z VIN port USB zostawić niepodłączony).

## 9. Errata: dlaczego wersja z R = 47 Ω zawiodła w teście polowym

Objawy pierwszego testu (2026-08-22): po załączeniu bezpiecznika jednostka wstała, ale
sonda nie wystartowała, a rezystor zaczął się przegrzewać (swąd). Kondensatory (50 V,
biegunowość poprawna) nie ucierpiały.

**Przyczyna — pominięta faza startowa.** Obliczenia wersji 1 obejmowały pracę ustaloną
(0,51–0,65 W) i milisekundowe impulsy nadawania, ale nie **fazę łączenia z WiFi**:
przez pierwsze 10–20 s po starcie ESP8266 pobiera średnio ~0,8–0,95 W — powyżej granicy
przepustowości układu z R = 47 Ω (0,77 W, rozdz. 2). Układ nie miał punktu pracy:
przetwornica cyklicznie ściągała węzeł w dół, przez rezystor płynęło w kółko ~130 mA
(~0,75 W strat), sonda nigdy nie przeszła startu, a rezystor o zbyt małej mocy się
przegrzewał. Kondensatory nie mogły pomóc — pokrywają impulsy milisekundowe, nie
kilkunastosekundową fazę o dużym poborze średnim.

**Poprawka:** R obniżony do **25–28 Ω** (np. 4× 100 Ω równolegle = 25 Ω):

| Parametr | R = 47 Ω (wersja 1) | R = 25 Ω (wersja 2) |
|---|---|---|
| granica przepustowości (P max) | 0,77 W | **1,44 W** |
| zapas nad fazą startową (~0,9 W) | BRAK — awaria | ~60% |
| napięcie węzła przy 0,9 W (start) | brak punktu pracy | 9,7 V |
| napięcie węzła przy 0,55 W (praca) | 9,3 V | 10,7 V |
| prąd maksymalny z linii (chwila ładowania C) | 255 mA | 480 mA przez ~8 ms |
| moc na rezystorach (start / praca) | — | 0,29 W / 0,10 W łącznie, po 1/4 na sztukę |

Prąd chwilowy 480 mA trwa tylko czas ładowania kondensatorów (τ = 25 Ω × 300 µF
= 7,5 ms) i pozostaje w klasie rozruchu akcesoriów; ostatecznym sędzią pozostaje
kryterium testu nr 3 (3× start jednostki bezpiecznikiem).

**Wnioski systemowe:** (1) w obliczeniach zasilaczy dla modułów radiowych uwzględniać
średni pobór fazy łączenia, nie tylko pracę ustaloną i piki; (2) rezystory bez znanej
mocy znamionowej nie wchodzą do układów zasilania.

---

# 10. Sprostowanie modelu: to stabilizator liniowy, nie przetwornica

## 10.1 Dowód

Podczas testów płytkę zasilono **5 V przez gniazdo zasilania**. Na szynie "5 V" pojawiło
się **3,8 V**. Ten jeden pomiar rozstrzyga sprawę:

| Gdyby na płytce był… | …to przy 5 V na wejściu na szynie 5 V byłoby |
|---|---|
| stabilizator liniowy (LDO) | **wejście minus ok. 1,2 V spadku = 3,8 V** — zgadza się |
| przetwornica impulsowa obniżająca | ok. 4,7–5,0 V albo całkowity brak działania |

Spadek 1,2 V to podpis układu typu AMS1117. **Płytka ma stabilizator liniowy.**

## 10.2 Co to zmienia

Różnica jest fundamentalna, bo oba typy zachowują się przeciwnie:

| | stabilizator liniowy | przetwornica impulsowa |
|---|---|---|
| prąd pobierany z wejścia | **równy prądowi wyjścia** — nie zależy od napięcia | rośnie, gdy napięcie spada |
| nadmiar napięcia | **zamieniany w ciepło** | przetwarzany na prąd |
| przy 12 V na wejściu i 5 V na wyjściu | traci 7 V razy prąd jako ciepło | traci ok. 15% mocy |

Płytka D1 R1 pobiera **około 150 mA** (ESP8266 z WiFi, układ USB-szeregowy, diody
sygnalizacyjne, dwa stabilizatory liniowe kaskadowo). I ten prąd jest **stały** —
niezależnie od tego, jaki rezystor wstawimy w szereg.

To jest sedno całej sprawy: **rezystor nie zmniejsza poboru prądu. Zmienia tylko to,
gdzie wydziela się ciepło.**

---

# 11. Dlaczego rezystory się spaliły — rachunek

Przy stałym prądzie 150 mA moc tracona w rezystorze to **P = I do kwadratu razy R**,
a napięcie docierające do płytki to **12 V − 0,15 A razy R**. Stabilizator potrzebuje
na wejściu co najmniej ok. **6,5 V**, żeby w ogóle wydać 5 V.

| Rezystor | Spadek | Zostaje dla płytki | Moc w rezystorze | Obudowa 0,25 W | Skutek |
|---|---|---|---|---|---|
| **47 Ω** (próba 1) | 7,05 V | **4,95 V — za mało** | **1,06 W** | przeciążona **4,2 razy** | spalony, sonda nie wstała |
| **22 Ω** (próba 2) | 3,30 V | 8,70 V — wystarczy | **0,50 W** | przeciążona **2,0 razy** | spalony |
| 2 x 100 Ω = 50 Ω | 7,50 V | **4,50 V — za mało** | 1,13 W | po 0,56 W = **2,2 razy** | spaliłby się |
| 2 x 47 Ω = 23,5 Ω | 3,53 V | 8,47 V — wystarczy | 0,53 W | po 0,26 W = **1,06 razy** | spaliłby się wolniej |
| **4 x 100 Ω = 25 Ω** | 3,75 V | 8,25 V — wystarczy | 0,56 W | po **0,14 W = 56%** | wytrzymuje |

## 11.1 Dwie różne przyczyny, nie jedna

Rezystor 47 Ω zawiódł **z dwóch powodów naraz**, i warto je rozdzielić:

1. **Za duża rezystancja** — zabrała 7 z 12 V, więc na płytkę zostało 4,95 V zamiast
   wymaganych 6,5 V. Sonda nie miała szans wystartować niezależnie od mocy rezystora.
2. **Za mała obudowa** — 1,06 W w elemencie przewidzianym na 0,25 W. Stąd swąd.

Rezystor 22 Ω naprawił punkt pierwszy (8,7 V wystarcza), ale **nie punkt drugi**:
0,5 W to wciąż dwa razy więcej, niż taki element odprowadzi.

## 11.2 Dlaczego równoległe — i dlaczego DWA to za mało

Tu jest nieporozumienie warte wyprostowania: **rekomendowałem cztery rezystory, nie dwa.**
Dwa nie załatwiają sprawy i tabela wyżej pokazuje dlaczego — w obu sensownych wariantach
dwójka przegrywa:

- **2 x 100 Ω** dają 50 Ω, więc napięcie spada do 4,5 V i sonda nie wstaje (ta sama
  awaria co przy 47 Ω);
- **2 x 47 Ω** dają 23,5 Ω, więc napięcie jest w porządku, ale na każdy rezystor wypada
  0,26 W, czyli **ponad jego wytrzymałość**.

Zasada, która to porządkuje: **łączenie równoległe nie zmniejsza wydzielanego ciepła —
ono dzieli je między więcej elementów.** Łączna moc traci się ta sama (0,5–0,6 W), bo
wyznacza ją prąd obciążenia, a nie liczba rezystorów. Zmienia się wyłącznie liczba watów
przypadająca na jedną obudowę.

Do tego dochodzi reguła praktyczna: element pracujący w zamkniętej puszce pod sufitem,
gdzie latem jest ciepło, powinien być obciążony **najwyżej w połowie** swojej
wytrzymałości. Cztery rezystory dają 56% — mieści się. Trzy dałyby 75% — na styk.

---

# 12. Rozwiązanie docelowe: przetwornica zamiast rezystora

## 12.1 Dlaczego cała droga z rezystorem była ślepa

Nawet gdy dobierzemy rezystory poprawnie, zostaje problem, którego żaden rezystor nie
rozwiąże: **z portu i tak płynie 150 mA**, a 1,05 W zamienia się w ciepło wewnątrz
zamkniętej puszki. Rezystor tylko decyduje, ile z tego ciepła wydzieli się na nim, a ile
na stabilizatorze płytki.

A to właśnie pobór prądu jest tym, co zablokowało start klimatyzatora. Linia +12 V portu
jest wymiarowana pod fabryczny sterownik przewodowy — mały panel z wyświetlaczem, biorący
kilkadziesiąt miliamperów. Nasze 150 mA to trzy do pięciu razy więcej.

## 12.2 Co robi przetwornica

Przetwornica impulsowa nie gasi nadmiaru napięcia — **przetwarza go na prąd**. Pobiera
mniej prądu przy wyższym napięciu i oddaje więcej prądu przy niższym, zachowując moc
(minus straty). Rachunek dla modułu z ESP32:

| Wielkość | Wartość |
|---|---|
| pobór ESP32 z szyny 5 V (średnio, WiFi połączone) | ok. 100 mA, czyli 0,50 W |
| sprawność przetwornicy MP1584 | ok. 85% |
| moc pobierana z linii 12 V | 0,59 W |
| **prąd pobierany z linii 12 V** | **ok. 49 mA** |
| ciepło wydzielane w przetwornicy | ok. 0,09 W |

Zestawienie obu dróg:

| | dziś: liniowo + rezystor | moduł v2: przetwornica |
|---|---|---|
| prąd z portu klimatyzatora | **150 mA** | **49 mA** |
| ciepło w puszce | ok. 1,05 W | ok. 0,09 W |
| napięcie na płytce | zależy od prądu, 4,9–8,7 V | **stabilne 5,00 V** |
| zachowanie przy szczycie WiFi | napięcie zapada | trzyma |

Trzykrotnie mniejszy pobór z portu to jest właśnie ta różnica, która decyduje, czy
jednostka wystartuje.

## 12.3 Układ docelowy

```
  +12 V (biala zyla) --[ 10 om ]--+-- IN+  MP1584  OUT+ --+-- 5V  ESP32
                                  |    (ustawic 5,00 V)   |
                                  |                    470 uF
                                  |                    low ESR
  GND (zolta zyla) ---------------+----- IN- ----- OUT- --+-- GND
```

**Rezystor 10 Ω — po co jeszcze jest, skoro przetwornica załatwia sprawę.** Nie służy już
do gaszenia napięcia, tylko do **ograniczenia udaru przy wpięciu wtyczki**. Przy 49 mA
traci 0,024 W, czyli praktycznie nic — element 0,25 W jest obciążony w 10%. W chwili
wpięcia ogranicza prąd ładowania kondensatorów wejściowych do 1,2 A przez ok. 0,1 ms
(energia 0,7 mJ, pomijalna).

Ciekawostka: **stara bateria 4 x 100 Ω też by tu zadziałała**, tylko niepotrzebnie zabiera
1,2 V zapasu. Skoro rezystory już masz, 10–22 Ω jest wygodniejsze.

**Kondensator 470 µF na WYJŚCIU, nie na wejściu.** To ważne rozróżnienie: na wyjściu
pokrywa szarpnięcia prądu ESP32 przy nadawaniu WiFi, tak że port ich nie widzi. Gdyby
siedział na wejściu, powiększyłby tylko udar przy wpięciu.

## 12.4 Sprawdzenie marginesów

| Warunek | Wymaganie | Nasz układ | Zapas |
|---|---|---|---|
| istnienie punktu pracy | P poniżej 3,6 W | 0,59 W | **6,1 razy** |
| to samo w fazie łączenia z WiFi | P poniżej 3,6 W | 0,88 W | **4,1 razy** |
| stabilność (odbiornik stałej mocy) | R znacznie poniżej 201 Ω | 10 Ω | **20 razy** |
| napięcie na wejściu przetwornicy | co najmniej 4,5 V | 11,5 V | **2,6 razy** |
| obciążenie rezystora | najwyżej 0,125 W | 0,024 W | **5,2 razy** |

Dla porównania: układ z wersji 1 (47 Ω) miał w wierszu "faza łączenia z WiFi" **zapas
ujemny** — i to go zabiło. Wersja 3 ma czterokrotny.

## 12.5 Co zostaje do sprawdzenia w terenie

Rachunek nie rozstrzyga jednej rzeczy: **czy płyta klimatyzatora zaakceptuje 49 mA**.
Wiemy, że 150 mA blokowało start; nie wiemy, gdzie dokładnie leży próg. Dlatego przy
montażu pierwszego modułu obowiązuje kolejność:

1. przetwornicę ustawić na **5,00 V miernikiem, zanim** cokolwiek do niej podłączysz
   (fabrycznie bywa ustawiona wyżej, a podanie 12 V na ESP32 kończy się jego zniszczeniem);
2. podłączyć moduł i zmierzyć napięcie linii +12 V **pod obciążeniem** — ma zostać co
   najmniej 11 V;
3. **trzykrotnie** wyłączyć i włączyć bezpiecznik — jednostka ma wstawać za każdym razem;
4. dopiero po zaliczeniu kroku 3 montować pozostałe trzy moduły.

Gdyby krok 2 lub 3 nie przeszedł, zostaje plan awaryjny bez zmiany elektroniki: zasilanie
modułu z osobnego zasilacza 5 V, tak jak działa teraz — z tą różnicą, że przetwornica i
tak zostaje w układzie i przyjmuje wtedy napięcie z zasilacza.


---

# 13. Wariant zapasowy: osobny zasilacz 230 V → 12 V

**Status: rozwiązanie tymczasowe i awaryjne, nie docelowe.** Wchodzi do gry, jeżeli
test z rozdz. 12.5 wykaże, że port nie udźwignie nawet 60 mA. Wartość tego wariantu
polega na tym, że jest **sprawdzony i gotowy** — jeśli port zawiedzie, projekt nie stoi.

## 13.1 Co ten wariant zmienia

Po trzech nieudanych podejściach z rezystorem gaszącym (47 Ω, 22 Ω, 4×100 Ω)
użytkownik sięgnął po osobny zasilacz. Zestawienie obu źródeł:

| | zasilanie z portu | osobny zasilacz |
|---|---|---|
| obciążenie linii +12 V klimatyzatora | 150 mA | **zero** |
| ryzyko zablokowania startu jednostki | realne, potwierdzone doświadczalnie | **żadne** |
| ciepło w puszce | 0,5–1,1 W | 0,14 W (przy wariancie B) |
| liczba niewiadomych | próg tolerancji płyty nieznany | brak |

Port COM-MANUAL zostaje wyłącznie **magistralą danych**: żyły A, B i masa.
Biała żyła +12 V pozostaje **niepodłączona i zaizolowana**.

## 13.2 Zastosowany zasilacz

Zasilacz LED EKO-LIGHT, dane z tabliczki:

| Parametr | Wartość | Komentarz |
|---|---|---|
| wejście | 220–240 V AC, 0,070–0,075 A | z zacisków zasilania klimatyzatora |
| wyjście | 12 V DC, 1,25 A, 15 W | **ośmiokrotny zapas** — pobór modułu to ok. 2 W |
| klasa ochronności | II (podwójna izolacja) | wyjście odizolowane, pływające |
| stopień ochrony | IP44 | |
| temperatura otoczenia | −10…+40 °C | do sprawdzenia w skrzynce latem |
| tc | 80 °C | |

Klasa II ma znaczenie praktyczne: wyjście jest odseparowane od sieci, więc **połączenie
jego masy z masą magistrali klimatyzatora jest bezpieczne** i nie tworzy pętli masy.
Ta wspólna masa jest dla RS-485 obowiązkowa.

## 13.3 Dwa warianty podłączenia — i dlaczego to nie jest obojętne

### Wariant A: 12 V wprost na VIN (dopuszczalny WYŁĄCZNIE na test)

Płytka WeMos ma na wejściu VIN **stabilizator liniowy** (dowód: rozdz. 10). Podanie
12 V oznacza, że musi on zutylizować całą różnicę do 5 V:

| Wielkość | Wartość |
|---|---|
| pobór płytki | ok. 150 mA |
| różnica napięć | 7 V |
| **moc tracona w stabilizatorze** | **1,05 W** |
| rezystancja termiczna SOT-223 (typowa) | 60–90 K/W |
| przyrost temperatury złącza | +65…95 K ponad otoczenie |
| w skrzynce o temperaturze 35–40 °C | **100–135 °C** |

Katalogowy limit złącza AMS1117 wynosi **125 °C**. Wariant A ląduje na granicy lub
powyżej niej. Płytka zadziała, ale będzie gorąca, a w upał należy się liczyć
z zadziałaniem zabezpieczenia termicznego. **Do montażu na stałe nie nadaje się.**

### Wariant B: 12 V → przetwornica → pin 5V (OBOWIĄZUJĄCY)

```
  230 V ---- zasilacz LED ---- 12 V ---[ MP1584 ]--- 5,00 V ---> pin 5V modulu
  (zaciski klimatyzatora)        |     ustawiona        |
                                 |     miernikiem    470 uF
  magistrala: A, B, GND ---------+-------- GND --------+------> GND modulu
```

Ta sama przetwornica, która jest na liście zakupów — tylko zasilana z zasilacza
zamiast z portu. Stabilizator na płytce obniża wtedy jedynie 5 → 3,3 V:

| Wielkość | Wariant A | Wariant B |
|---|---|---|
| moc tracona na płytce | **1,05 W** | **0,14 W** |
| przyrost temperatury | +65…95 K | +9…13 K |
| margines do limitu 125 °C | brak | ponad 70 K |

## 13.4 Kolejność uruchomienia

1. **Bezpiecznik klimatyzatora wyłączony.** Zasilacz wpiąć w zaciski zasilania jednostki
   (L: brązowy, N: niebieski — opis na tabliczce).
2. **Zmierzyć wyjście zasilacza przed podłączeniem czegokolwiek.** Ma być ok. 12 V.
   Tanie zasilacze LED bez obciążenia potrafią podbić napięcie; **odczyt powyżej 14 V
   dyskwalifikuje wariant A** i wymusza przetwornicę.
3. Ustawić przetwornicę na **5,00 V miernikiem, przed** podłączeniem modułu.
4. Podłączyć moduł: 5 V i masa z przetwornicy, A/B/GND z magistrali.
5. Trzykrotnie przełączyć bezpiecznik — jednostka i moduł mają wstawać za każdym razem.
6. Po godzinie pracy sprawdzić palcem temperaturę stabilizatora na płytce; ma być
   letni, nie parzący.

## 13.5 Konsekwencje dla reszty projektu

- **Cztery zasilacze** — po jednym na jednostkę; każdy zasilany z zacisków swojego
  klimatyzatora, więc moduł żyje dokładnie wtedy, gdy jednostka ma napięcie.
- **Rezystory i kondensatory filtrujące z rozdz. 1–12 przestają być potrzebne.**
  Zostaje kondensator 470 µF na wyjściu przetwornicy — nadal ma sens, bo pokrywa
  szarpnięcia prądu przy nadawaniu WiFi i przy impulsach diody podczerwieni.
- **Największe otwarte ryzyko projektu znika.** Nie trzeba już zgadywać, gdzie leży
  próg tolerancji płyty klimatyzatora na pobór z portu — nic z niego nie pobieramy.


---

# 14. Tor zasilania modułu docelowego (ESP32) — komplet

## 14.1 Schemat toru

```
  230 V z zaciskow klimatyzatora
        |
        v
   zasilacz 12 V (klasa II, wyjscie odizolowane)
        |  12 V DC
        v
   [ 10 om ]  ogranicznik udaru przy wpinaniu (opcjonalny)
        |
        v
   MP1584EN  --- ustawiona miernikiem na 5,00 V ---
        |  5 V -----+----- 470 uF low ESR
        |           |
        v           v
   ESP32 pin 5V   dioda IR przez BC337 (~100 mA w impulsie)
        |
        +-- wbudowany stabilizator 3,3 V --+-- uklad ESP32
                                           +-- MAX3485 (magistrala RS-485)
                                           +-- VS1838B (odbiornik IR)
```

## 14.2 Bilans prądu

| Odbiornik | Pobór z szyny 5 V |
|---|---|
| ESP32 z WiFi, średnio | 80–120 mA |
| MAX3485 | ok. 1 mA |
| VS1838B | ok. 1 mA |
| dioda IR | ok. 100 mA, wyłącznie w impulsach po ~70 ms |
| **razem, średnio** | **100–130 mA, czyli 0,5–0,65 W** |
| **pobór z linii 12 V przez przetwornicę** | **ok. 60 mA** |

Zasilacz 15 W / 1,25 A daje **dwudziestokrotny zapas**.

## 14.3 Dlaczego przy ESP32 przetwornica jest OBOWIĄZKOWA

To jest różnica wobec dzisiejszej sondy i najłatwiejszy sposób na zniszczenie modułu:

| Płytka | Wejście zasilania | 12 V wprost? |
|---|---|---|
| WeMos D1 R1 (obecna sonda) | VIN **9–24 V** | **tak** — mieści się w specyfikacji, tylko grzeje stabilizator |
| ESP32 DevKit (moduł docelowy) | pin 5V/VIN oczekuje **5 V** | **NIE** |

ESP32 DevKit ma za tym pinem stabilizator 3,3 V. Przy 12 V na wejściu musiałby
zutylizować 8,7 V, a ESP32 w szczycie nadawania WiFi pobiera do 250 mA — to
**ponad 2 W** w obudowie SOT-223. Kończy się zadziałaniem zabezpieczenia termicznego
albo uszkodzeniem układu.

**Zasada: na modułach docelowych 12 V nigdy nie trafia na płytkę bezpośrednio.**
Zawsze przez MP1584 ustawioną na 5,00 V, podane na pin `5V`.

## 14.4 Skąd biorą się elementy toru

| Element | Źródło |
|---|---|
| przetwornica MP1584EN, 6 szt. | lista zakupów, pozycja **A3** |
| kondensator 470 µF / 25 V, 6 szt. | lista zakupów, pozycja **A7** |
| rezystor 10 Ω (ogranicznik udaru) | zapasy użytkownika |
| przewody, koszulki termokurczliwe | zapasy użytkownika |
| zasilacz 12 V (tylko wariant zapasowy) | poza listą — patrz 14.5 |

## 14.5 Zasilacze — tylko na wypadek niepowodzenia testu portu

Lista zakupów **nie zawiera zasilaczy i słusznie**: planem docelowym jest zasilanie
z portu przez przetwornicę, a wtedy zasilacze są zbędne. Kupować je trzeba **dopiero
wtedy**, gdy test z rozdz. 12.5 wypadnie negatywnie — i wtedy cztery sztuki.

Parametry, gdyby doszło do zakupu:

- **12 V DC**, minimum **5 W** (zapas jest wskazany — zasilacze pracujące blisko
  granicy mocy grzeją się i szybciej padają),
- **klasa ochronności II** (symbol kwadratu w kwadracie) — wyjście odizolowane od
  sieci; to warunek bezpiecznego spięcia masy zasilacza z masą magistrali,
- zakres temperatur otoczenia obejmujący warunki w skrzynce klimatyzatora latem.


---

# 15. Napięcia i marginesy — czy tor to wytrzyma

## 15.1 Napięcie z przetwornicy: ustawiane, nie fabryczne

MP1584EN jest przetwornicą **regulowaną**. Moduł przychodzi ustawiony na przypadkową
wartość — bywa 12 V, bywa prawie tyle, co na wejściu.

| Parametr | Wartość |
|---|---|
| napięcie wejściowe | 4,5–28 V |
| napięcie wyjściowe | **0,8–20 V, potencjometr na płytce** |
| prąd wyjściowy | do 3 A |

**Obowiązkowy krok montażu: ustawić 5,00 V miernikiem przy odłączonym module.**
Podanie 12 V na pin `5V` ESP32 niszczy płytkę.

## 15.2 Marginesy elementów przy poborze 130 mA z szyny 5 V

| Element | Wytrzymałość | Obciążenie | Zapas |
|---|---|---|---|
| MP1584, wejście | 4,5–28 V | 12 V | w środku zakresu |
| MP1584, prąd wyjścia | 3 A | 0,13 A | **23×** |
| MP1584, straty własne | — | ok. 0,09 W | nie grzeje się |
| kondensator 470 µF | 25 V | 5 V | **5×** |
| stabilizator 3,3 V na ESP32 | ok. 0,5 W ciągłe | 0,2 W średnio; 0,43 W w szczycie WiFi | wystarcza |
| tranzystor BC337 | 800 mA / 625 mW | 100 mA / ok. 0,02 W | **8×** |
| dioda TSAL6100 | 100 mA ciągłe | 100 mA, wyłącznie impulsowo | praca impulsowa, w normie |
| MAX3485 | 3,0–3,6 V | 3,3 V | nominalnie |

Wniosek: **żaden element toru nie pracuje blisko granicy.**

## 15.3 Dwie wartości do dobrania przy lutowaniu

Nie wynikają z listy zakupów, bo zależą od napięcia szyny:

**Rezystor szeregowy diody IR — 33 Ω.**
R = (5 V − 1,35 V spadku na diodzie − 0,2 V na nasyconym tranzystorze) ÷ 0,1 A ≈ 34 Ω.
W impulsie traci 0,33 W, ale nośna 38 kHz ma ok. 50% wypełnienia, a paczka trwa ~70 ms —
średnia moc jest pomijalna. Element 0,25 W wystarczy.

**Rezystor bazy tranzystora — 470 Ω.**
I_B = (3,3 V − 0,7 V) ÷ 470 Ω ≈ 5,5 mA, przy limicie pinu ESP32 wynoszącym 12 mA.
Przy wzmocnieniu prądowym BC337 rzędu 100 daje to pełne nasycenie przy 100 mA kolektora.

## 15.4 Co pozostaje niewiadomą

Wytrzymałość elementów jest policzona i wszędzie z zapasem. Rachunek **nie rozstrzyga
jednej rzeczy: czy płyta klimatyzatora zaakceptuje pobór ok. 60 mA z portu.**

Wiadomo, że 150 mA blokowało start. Progu nie znamy. Fabryczny sterownik przewodowy
pobiera kilkadziesiąt miliamperów, więc 60 mA mieści się w tej klasie — ale to
przesłanka, nie dowód. Rozstrzyga test z rozdz. 12.5, wykonany na jednym module
przed montażem pozostałych trzech.
