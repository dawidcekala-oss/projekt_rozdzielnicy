# DANE DIAGNOSTYCZNE — AMPERE POINT
**Zbiór danych referencyjnych używanych przy diagnozowaniu ładowarek · budowany małymi krokami przy okazji kolejnych spraw**

> **Do czego służy:** jedno miejsce z danymi, do których wraca się przy każdej diagnozie — oznaczenia i budowa płytek, zmierzone wartości odniesienia, znaczenie punktów danych w aplikacji, stany sygnałów, progi. Każdy wpis ma źródło: sprawę serwisową, zdjęcie albo pomiar.
>
> **Zasada nadrzędna:** wpisywać wyłącznie to, co **odczytane lub zmierzone**, nigdy tego, co wynika z „ogólnej wiedzy o elektronice" — to są komponenty chińskie i klasyczne założenia bywają nietrafione. Rzeczy niepewne oznaczać wprost jako hipotezy i pisać, co je potwierdzi.

## Spis zawartości

1. Q11 — płytka mocy, złącze międzypłytkowe, pomiary
2. Q74, Q22, Q37, seria P, seria B
3. Sygnały interfejsu ładowania (CP, PP), czujnik temperatury we wtyczce
4. Komunikat „Low Voltage Reminder" — przelicznik √3
5. Tuya — punkty danych, harmonogram, logi, dostęp, integracja HA
6. Wallbox (PID `gbmxngploofmhbjc`) i moduł DLB‑A1
7. Instalacja zasilająca — wymagania (norma, instrukcja) i przypadki z korespondencji
8. Stanowisko serwisowe — cechy, o których trzeba pamiętać przy testach
9. Pozostałe dokumenty z danymi (odsyłacze)

---

## Q11 (11 kW, 3×16 A, 400 V)

### Płytka mocy — oznaczenie i topologia

Laminat opisany **X20322_2_V4**, data 260419. Płytka wąska, podłużna, mocowana wzdłuż krawędzi obudowy.

Tor mocy tworzą **cztery przekaźniki** oznaczone na sitodruku **K1–K4**, przełączające kolejno **N, L1, L2, L3** — urządzenie rozłącza więc również przewód neutralny. Typ: **Baocheng NB90‑12S‑S‑A**, parametry z obudowy: 40 A / 240 VAC / 30 VDC, dodatkowo 40 A 277 VAC, 1‑5HP 240 VAC, TV‑15, **cewka DC12V**.

Zaciski śrubowe, po obu stronach każdego przekaźnika: wejściowe **N_IN, L1_IN, L2_IN, L3_IN**, wyjściowe **N_O, L1_O, L2_O, L3_O**, osobno **PE**.

### Sekcja wejściowa

Filtr EMC z dławikiem wspólnym, kondensatory oznaczone **RV1** i **RV2** (na sitodruku RV, ale są to kondensatory — ustalone oględzinami 2026‑08) oraz **CY2** przy PE. Element **G1** z nadrukiem „RL600" to **warystor** — zmierzony jako OL na zakresie 60 MΩ. Bezpiecznik **F1: T2A / 250 V**.

Obok filtra mała kostka dwupinowa opisana **L N** — zasilanie modułu pomocniczego, odczepione **przed przekaźnikami**, czyli obecne od chwili włożenia wtyczki.

Złącze **J9** opisane **NTC CT ICP**. Złącze **J12** opisane **8V CP**.

### Złącze międzypłytkowe (płytka mocy ↔ płytka kontrolna)

Taśma wielożyłowa. Na płytce mocy sitodruk w dwóch rzędach, na płytce kontrolnej złącze **J2** z opisem wzdłuż krawędzi. Odczytane oznaczenia pinów:

`PE · NTCI · ICP · 8V · K1 · K2 · K3 · K4 · 1.65 · CP` oraz `GND · CT · NTC · U1 · U2 · U3 · N_PE`

Przy płytce kontrolnej dodatkowo chiński sitodruk **L1电压 / L2电压 / L3电压** — dosłownie „napięcie L1 / L2 / L3", co wiąże piny **U1, U2, U3** z pomiarem napięć trzech faz.

### Wnioski architektoniczne wynikające z opisu pinów

**Nie ma pinu 12 V.** Zasilanie cewek przekaźników nie przychodzi z płytki kontrolnej — powstaje lokalnie na płytce mocy. *(ustalone 2026‑08‑26; wcześniejsze założenie o pinie 12 V na złączu było błędne)*

**8V** — zasilanie płytki kontrolnej, dostarczane z płytki mocy. Skoro ekran i logika działają, ta gałąź zasilania jest sprawna.

**K1–K4** — sygnały sterujące, po jednym na przekaźnik, biegnące z płytki kontrolnej do mocy. Sterują elementami wykonawczymi znajdującymi się na płytce mocy; same są sygnałami logicznymi, nie zasilaniem cewek.

**U1, U2, U3** — pomiar napięć faz, realizowany dzielnikami rezystorowymi na płytce mocy (widoczne łańcuchy rezystorów 1 MΩ, oznaczenia 1004).

**N_PE** — pomiar napięcia między przewodem neutralnym a ochronnym, czyli tor detekcji uziemienia. *Hipoteza do potwierdzenia: to z tego toru pochodzą wartości wyświetlane pod komunikatem „Wiring Abnormality" — producent określił je jako próbki układu detekcji uziemienia (por. U‑020).*

**1.65** — napięcie odniesienia, najpewniej połowa szyny 3,3 V, potrzebne do pomiaru przebiegów zmiennych przetwornikiem jednobiegunowym. *Hipoteza, niepotwierdzona pomiarem.*

**CT** — przekładnik prądowy. **NTC / NTCI** — czujniki temperatury. **ICP** — nieustalone.

### Spód płytki

Zestyki mocy wyprowadzone są **na pięć pinów równolegle**, zalanych wspólnym polem cyny — rozłożenie prądu 40 A na kilka wyprowadzeń. Piny w obrębie jednego pola są zwarte celowo; pola sąsiednie to dwa bieguny tego samego zestyku.

**Wartość odniesienia:** na sprawnej płytce, przy niezasilonej cewce, rezystancja między polami dwóch biegunów zestyku wynosi **15,05 MΩ** i jest identyczna niezależnie od tego, których pinów dotknąć. To nie jest zwarcie ani wada — rozwarty zestyk mierzy się wtedy przez elementy wiszące równolegle do toru na płytce. Wniosek praktyczny: **pomiar rezystancji zestyku ma sens wyłącznie przy zasilonej cewce**, inaczej płytka sprawna i uszkodzona dają ten sam wynik. *(ustalone 2026‑08‑26 na płytce fabrycznej)*

### Wyświetlacz

Moduł **DWIN T5L0**, oznaczenie na taśmie BP0L474HG08 (odczytane 2026‑08‑26 przy zdjętym panelu).

### Pomiary złącza międzypłytkowego — egzemplarz uszkodzony (sprawa „klejdysz")

Warunki pomiaru: urządzenie zasilone, stan A (bez pojazdu), **w chwili wyświetlania błędu Overload Reminder**, a więc przy rozwartych przekaźnikach. Zero pomiarowe: skrajny prawy pin GND złącza na płytce kontrolnej. Multimetr w trybie napięcia stałego.

| Pin | Wartość [V] | Uwagi |
|---|---|---|
| U1 | 0,56 | trzy tory napięć faz identyczne |
| U2 | 0,56 | |
| U3 | 0,56 | |
| ZL1 | 3,298 | trzy identyczne, poziom szyny 3,3 V |
| ZL2 | 3,298 | |
| ZL3 | 3,298 | |
| NTC2 | 1,772 | |
| CT | 1,651 | zgodne z odniesieniem 1,65 V |
| CP | 11,99 | poprawne dla stanu A wg IEC 61851‑1 |
| 1.65 | **4,31** | rozbieżne z nazwą pinu i z offsetem CT |
| K4 | **5,077** | odbiega od pozostałych sygnałów K |
| K3 | 7,45 | |
| K2 | 7,45 | |
| K1 | 7,45 | |
| 8V | 7,45 | zasilanie płytki kontrolnej obecne; czy 7,45 V to wartość prawidłowa — do porównania z egzemplarzem sprawnym |
| ICP | 0 | |
| NTC1 | 1,78 | |
| GND → PE | −3,79 | |
| GND → GND | 0 | kontrola zera pomiarowego |

**Co z tych liczb wynika bez posiadania referencji:**

Zasilanie oznaczone 8 V ma 7,45 V, a CP przyjmuje 11,99 V, czyli wartość prawidłową dla stanu A — tor pilota działa, a logika jest zasilana. Czy 7,45 V na szynie opisanej jako 8 V jest wartością prawidłową, rozstrzygnie dopiero porównanie z egzemplarzem sprawnym; gdyby tam było bliżej 8,0 V, zaniżona szyna zasilania stałaby się tropem wyjaśniającym również zaniżone poziomy na torach pomiarowych.

Dwie wewnętrzne niespójności widoczne bez płytki wzorcowej. Po pierwsze **K4 = 5,077 V przy K1, K2 i K3 równych 7,45 V** — wszystkie cztery sygnały powinny być w tym samym stanie, skoro przekaźniki są rozwarte. Obniżony poziom na jednym wyprowadzeniu wskazuje, że coś to wyprowadzenie obciąża. Po drugie **pin 1.65 pokazuje 4,31 V**, podczas gdy tor CT ma offset 1,651 V — odniesienie 1,65 V w układzie zatem istnieje i działa, ale na tym pinie złącza go nie ma.

**U1, U2 i U3 równe dokładnie 0,56 V** to trzy tory zachowujące się identycznie, więc przyczyna jest dla nich wspólna, a nie leży w pojedynczym dzielniku. Wartość odbiega od offsetu 1,65 V widocznego na CT.

**Charakter usterki i objaw wiodący.** Usterka jest **przerywana**, nie postępująca — urządzenie miewa okresy częściowej sprawności, w których przekaźniki klikają, choć napięcie na zaciskach wyjściowych i tak się nie pojawia. **Objaw wiodący to Overload Reminder i występował już u klienta**, a nie powstał na stanowisku serwisowym. Sekwencja obserwowana w serwisie: kilka sekund po włączeniu krótki, trwający poniżej sekundy komunikat nadnapięciowy, następnie trwały komunikat przeciążeniowy; w tych kilku sekundach przed pojawieniem się błędów przejście do stanu C nie powoduje zadziałania przekaźników.

**Co z tego wynika:** przy rozwartych przekaźnikach prąd przez tor mocy nie płynie, więc komunikat o przeciążeniu **nie może pochodzić z rzeczywistego prądu**. Informacja o przeciążeniu powstaje w torze pomiaru prądu, czyli przy przekładniku i pinie CT. Wartość 1,651 V zmierzona multimetrem odpowiada offsetowi spoczynkowemu, ale tryb stały pokazuje wyłącznie średnią — zakłócenie zmienne nałożone na ten offset dałoby średnią bez zmian, a jednocześnie mogłoby być przez sterownik scałkowane jako prąd. To czyni tor CT pierwszym kandydatem do oglądnięcia oscyloskopem.

**Zastrzeżenie metodyczne:** tory U1–U3, CT i CP przenoszą przebiegi zmienne, a multimetr w trybie stałym pokazuje ich wartość średnią, gubiąc kształt i amplitudę. Do tych punktów właściwym narzędziem jest oscyloskop. Powyższe liczby traktować jako wskazanie kierunku, nie jako pomiar rozstrzygający.

### Otwarte pytania do ustalenia przy kolejnych naprawach

Gdzie dokładnie na płytce mocy powstaje 12 V dla cewek i w którym punkcie da się je zmierzyć od góry. Jakim elementem realizowane jest sterowanie cewką po odebraniu sygnału K — tranzystor czy optoizolator, i gdzie leży. Czy 8 V i 12 V pochodzą z tej samej gałęzi zasilacza pomocniczego, bo od tego zależy, czy działająca płytka kontrolna cokolwiek mówi o stanie zasilania cewek. Znaczenie pinu ICP oraz pinów ZL1–ZL3. Skala i próg wartości w torze N_PE. Jaki jest prawidłowy poziom sygnałów K przy przekaźnikach rozwartych i zwartych. Jaka wartość powinna być na pinie 1.65 i czy podaje on odniesienie z płytki mocy do kontrolnej, czy odwrotnie.

---

## Q74, Q22, Q37, seria P, seria B

Brak zebranych ustaleń. Zanotowano jedynie, że płytka Q74 używa przekaźnika tej samej firmy w wersji **50 A** zamiast 40 A i ma inny laminat — nie jest zamienna z Q11.

**B35 — rzadka niezgodność z konkretnym samochodem** *(2026‑10‑07, sprawa A. Augusta, `casey/Artur_August/`)*: u klienta dwa egzemplarze B35 nie radzą sobie, gdy **samochód sam zmienia stan** — start z harmonogramu w aucie, otwarcie/zamknięcie drzwi (wybudzenie): jeden nie wznawia ładowania, drugi świeci **czerwoną diodą** i nie ładuje. Start od razu po podłączeniu działa. Aktualizacja oprogramowania nie pomogła; w serwisie ten sam egzemplarz działa w obu trybach. Rozwiązanie handlowe: wymiana na **Q37**, z którą takich problemów nie ma (decyzja Dawida: dopłata 400 zł brutto przy różnicy cen 500 zł) albo zwrot. Model samochodu — nieustalony. `[F — relacja klienta i Dawida]` *Uzupełnienie (2026‑10‑07): samochód to **BMW** (model nieznany); ASO BMW uznało auto za sprawne, ładowarka Greencell działa. Drugi egzemplarz B35 tego klienta (…465) **startuje z harmonogramu** — problem z opóźnionym startem ma tylko …504 (aktualizowany przez nas). Wniosek: różnica między egzemplarzami (np. wersja oprogramowania), a nie sama niezgodność modelu z autem `[Z]`; do porównania wersje oprogramowania obu egzemplarzy.* *Drugi podobny przypadek (2026‑10‑07, `casey/Gizinek/`, model najpewniej B35): u nas bez błędu, po naszej aktualizacji oprogramowania u klienta nadal: podłączenie do auta → zielona, po chwili czerwona dioda. W obu sprawach aktualizacja nie pomogła; jedyny egzemplarz, o którym wiadomo, że startuje z harmonogramu (…465 Augusta), aktualizowany nie był `[Z — do sprawdzenia]`.*

---

## Sygnały interfejsu ładowania (CP, PP)

Wartości potwierdzone odczytem w logach Tuya oraz pomiarem na płytce.

| Stan CP | Napięcie | Znaczenie | Opis w Tuya |
|---|---|---|---|
| A | 12 V | brak pojazdu | `Connection State = Control pilot 12V` |
| B | 9 V | pojazd podłączony, ładowanie nierozpoczęte | `Control pilot 9V` |
| C | 6 V | ładowanie w toku | `Control pilot 6V` |

Powiązane stany pracy raportowane przez urządzenie: `Charger Free` (brak pojazdu), `Charger Wait` (pojazd podłączony, oczekiwanie), `Charger Charging` (ładowanie).

**Czasy z normy** (IEC 61851‑1:2010, tab. A.7; w folderze `../KONTEKST/iec-61851-1_compress.pdf` jest tylko to wydanie):
- ładowarka zmienia wypełnienie PWM najpóźniej **10 s** po zewnętrznym poleceniu (np. z systemu zarządzania mocą);
- auto dostosowuje prąd najpóźniej **5 s** po zmianie wypełnienia;
- ładowarka załącza zasilanie najpóźniej **3 s** po wykryciu stanu C;
- auto zgłasza chęć ładowania (stan C) **bez limitu czasu** — norma nie wymaga, żeby auto w ogóle wznowiło pobór po powrocie PWM.

*(odczytane 2026‑09‑28)*

**PP — kodowanie obciążalności kabla** (rezystor PP–PE w złączu Type 2, wyłącznie po stronie pojazdu): przewidziane wartości to **13, 20, 32 i 63 A**. Nie ma wartości 10 A. Niezgodna albo brakująca rezystancja **uniemożliwia komunikację z pojazdem, a nie ogranicza prąd**. Po stronie zasilania żadnego kodowania nie ma — zwykłe gniazdo domowe nie przekazuje urządzeniu informacji o dopuszczalnym prądzie. *(ustalone 2026‑08‑18 po błędnym wyjaśnieniu w sprawie U‑023)*

**Objaw „samochód nie blokuje wtyku, ładowanie się nie zaczyna”** — auto nie rozpoznało ładowarki jeszcze przed ładowaniem (etap wtyku PP i sygnału CP), w przeciwieństwie do przerw w trakcie ładowania. Pierwszy przypadek: Q11 + BYD Atto 2 Boost 2025, u nas ta sama ładowarka ładuje normalnie (sprawa A. Gumkowskiego, 2026‑10‑07, `istotne_casey/Adam_Gumkowski/`). Rezystancja PP–PE we wtyku tej ładowarki zmierzona — w porządku (a zła wartość zatrzymałaby też nasze auto). Przyczyna w toku. `[F — objaw, pomiar PP; przyczyna nieustalona]`

**Jak czytać „z ładowarką fabryczną auto się ładuje”** *(2026‑10‑07)*: ładowarka dawana z autem jest zwykle przenośna, jednofazowa, z gniazda domowego `[Z]`. Jej działanie dowodzi sprawności gniazda w aucie, rozpoznawania wtyku i sygnału sterującego oraz ładowania **jednofazowego**. **Nie** dowodzi: (1) sprawności gniazda/obwodu, z którego zasilana jest nasza ładowarka (zwykle inne, trójfazowe — nasze zabezpieczenia mogą tam odmówić startu i pokazać komunikat); (2) ładowania trójfazowego w aucie (usterka trójfazowej części ładowarki pokładowej nie przeszkadza jednofazowej); (3) zgodności auta z naszym sygnałem po aktualizacji oprogramowania auta. Rozróżnia: komunikat na ekranie naszej ładowarki w chwili problemu (zasilanie vs auto), ładowanie auta na publicznej stacji AC (zwykle trójfazowej), log Tuya ze stanem sygnału sterującego 12/9/6 V. Moment blokowania wtyku przez auto zależy od marki — bez jego znajomości „auto nie blokuje wtyku” nie wskazuje etapu. *Korekta (2026‑10‑07, Dawid): „auto nie blokuje wtyku” oznacza, że ładowarka nie przechodzi w żaden inny stan — **auto nie załącza rezystorów w obwodzie sygnału sterującego**, ładowarka widzi cały czas brak auta i stoi w gotowości (ekran „ready to charge” niewiele powie). Awaria jest więc przed pierwszą zmianą stanu, zanim popłynie prąd: gniazdo zasilające i ładowanie trójfazowe nie mają znaczenia (problem z zasilaniem Q11 pokazałaby komunikatem). Szukać: czy auto uznaje wtyk za podłączony (wykrycie wtyku, wybudzenie, oprogramowanie auta) i mechanicznego styku PP/CP wtyku w gnieździe konkretnego auta. Punkty (1)–(2) powyżej dotyczą tylko awarii po rozpoznaniu auta.*

### Przycisk otwierania klapki Tesli (wersje z przyciskiem, np. Q11 PRO) *(2026‑10‑07, sprawa D. Romanka)*

- Przycisk na rękojeści wysyła **sygnał radiowy** do portu ładowania Tesli; aktywacji nie wymaga. Sygnał nie jest uwierzytelniany — to stały komunikat. `[F — opisy projektów odtwarzających sygnał, źródła niżej]`
- **Częstotliwość zależy od rynku samochodu: Europa 433,92 MHz, USA 315 MHz** — według projektów hobbystycznych odtwarzających sygnał, nie według dokumentacji Tesli. *Korekta (2026‑10‑07, pytanie Dawida): wniosek „Tesla sprowadzona z USA nie zareaguje” jest niepotwierdzony. Tesle z USA mają inne gniazdo ładowania (NACS lub starsze złącze Tesli); żeby ładować z wtyku Type 2, gniazdo musi być przerobione na europejskie, a co wtedy odbiera sygnał przycisku — nie wiadomo. Klientom tego nie podawać.* `[F — github.com/fredilarsen/TeslaChargeDoorOpener, github.com/Algafix/pico-tesla-charging-port-opener, hackaday.com 2022‑04‑08; Z — że nasz przycisk nadaje 433,92 MHz: wniosek z tego, że otwiera klapkę naszej Tesli]`
- Instrukcja Tesli (Model 3): przy samochodzie **w trybie P** nacisnąć i puścić przycisk na przewodzie, żeby otworzyć klapkę. `[F — tesla.com/ownersmanual, „Charging Instructions”]`
- U nas ładowarka D. Romanka otwiera klapkę naszej Tesli prawidłowo (07.10), a u klienta nie — przy aucie otwartym, z telefonem w środku. Wyjaśnienie nieustalone; możliwe warunki użycia (tryb P, odległość). `[F — relacja Dawida]`
- Czy przycisk ma własną baterię — nieustalone; nie zakładać.
- **Instrukcja Tesli Model Y, wersja polska** (tesla.com/ownersmanual/modely/pl_pl, „Instrukcje ładowania”, odczytane 2026‑10‑07) `[F]`:
  - „Po włączeniu w pojeździe Model Y położenia postojowego zwolnij przycisk na kablu ładowania Tesla, aby otworzyć klapkę gniazda ładowania.”
  - Inne sposoby: ekran → **Sterowanie → ikona gniazda ładowania (błyskawica)** albo **Sterowanie > Ładowanie > Otwórz gniazdo ładowania**; naciśnięcie klapki przy odblokowanym aucie lub z uwierzytelnionym telefonem — „jeśli klapka się nie otwiera, może być konieczne wybudzenie pojazdu poprzez pociągnięcie za klamkę, a następnie ponowienie próby”; przycisk tylnego bagażnika na kluczyku 1–2 s; polecenia głosowe.
  - Przy bardzo niskiej temperaturze i oblodzeniu zatrzask klapki może przymarznąć (podgrzewacz gniazda z ogrzewaniem tylnej szyby, przygotowanie pojazdu w aplikacji); nie otwierać klapki na siłę.
  - Klapka sama się zamyka, jeśli w ciągu kilku minut nie zostanie włożony kabel.
  - „W przypadku niektórych starszych urządzeń do ładowania firmy Tesla naciśnięcie przycisku na kablu może nie otworzyć klapki” — dotyczy sprzętu Tesli.
  - ~~Praktyczny test dla klienta: jeśli klapka nie otwiera się także z ekranu samochodu, przyczyna jest po stronie auta.~~ *Korekta (2026‑10‑07, Dawid): test bez wartości — klient ładuje auto, więc klapka u niego otwiera się innym sposobem (ekran, aplikacja, naciśnięcie). Mechanizm klapki jest sprawny; problem dotyczy tylko reakcji auta na przycisk.*
  - Strona instrukcji odrzuca pobieranie automatyczne (403) — czytać przez przeglądarkę.

### Czujnik temperatury we wtyczce / adapterze — ograniczenie prądu do 10 A

Q11 kontroluje temperaturę **po stronie wtyku zasilającego**, a układ czujnika biegnie przez **wymienny adapter**. Przerwanie tego obwodu daje komunikat:

> „Temperature sensing wire in the plug is disconnected"

i **ograniczenie prądu do 10 A**. Ograniczenie jest zachowaniem zabezpieczającym, nie usterką nastaw.

**Konsekwencja dla diagnostyki:** objaw „nastawa prądu wraca do 10 A" należy w pierwszej kolejności wiązać z obwodem czujnika temperatury w adapterze, a nie z pamięcią nastaw ani z interfejsem. *(ustalone 2026‑09‑06 na zgłoszeniu M. Ratusznika; retrospektywnie tłumaczy sprawę U‑023, gdzie 16 A wracało do 10 A)*

**Dwa różne obrazy awarii tego obwodu:**

| Moment pojawienia się komunikatu | Interpretacja |
|---|---|
| natychmiast po wpięciu adaptera, przed ładowaniem | obwód czujnika **rozwarty na stałe** — przerwa w żyle, wypięty styk, uszkodzony termistor |
| dopiero po rozpoczęciu ładowania | obwód **ciągły, ale niepewny** — styk na granicy, rozwierający się przy nagrzaniu lub obciążeniu mechanicznym przewodu |

Adaptery sprawdzać zawsze **porównawczo między sobą**, bo ładowarka jest w takim zestawie jedna, a adapterów kilka.

### Uszkodzony termistor — fałszywy komunikat o przegrzaniu

Drugą awarią tego samego obwodu jest **uszkodzenie samego termistora**, dające objaw zupełnie inny niż przerwa w przewodzie:

> „Overheating Reminder"

**Reguła rozpoznawania:** komunikat o przegrzaniu przy urządzeniu i przewodzie **zimnych w dotyku**, a zwłaszcza pojawiający się **przed podłączeniem pojazdu i przed przepływem prądu**, nie opisuje rzeczywistej temperatury — opisuje stan toru pomiarowego. Rzeczywiste nagrzanie wymaga czasu i obciążenia, więc komunikat natychmiast po wpięciu wtyczki fizycznie nie może z niego wynikać.

Typowy przebieg: najpierw sporadyczne komunikaty w trakcie ładowania, potem coraz częstsze, wreszcie stały komunikat już przy samym podłączeniu do gniazdka.

**Naprawa:** wymiana wtyczki. *(potwierdzone 2026‑09 na sprawie U‑026 — po wymianie urządzenie pracuje prawidłowo)*

| Awaria obwodu czujnika | Komunikat | Skutek |
|---|---|---|
| przerwany przewód czujnika | „Temperature sensing wire in the plug is disconnected" | ograniczenie prądu do **10 A** |
| uszkodzony termistor | „Overheating Reminder" | zablokowanie ładowania, komunikat mimo zimnego urządzenia |

**Nie mylić tych dwóch przypadków** — mają inne komunikaty, inne skutki i inny obraz narastania.

**Trop uboczny:** przy uszkodzeniu termistora warto zapytać, czy urządzenie pracowało wcześniej ze zwykłego gniazda i czy przewód się nagrzewał. W sprawie U‑026 klient miał wcześniej rzeczywiste nagrzewanie przewodu, które ustało po zamontowaniu dedykowanego gniazda 230 V dla pojazdów — uszkodzenie termistora mogło być następstwem tamtej pracy w podwyższonej temperaturze.

---

---

## Komunikat „Low Voltage Reminder" — znaczenie wyświetlanych liczb

**Wartości pod komunikatem to surowe dane z procesora, przeskalowane — normalnie niewidoczne dla użytkownika.** Nie są to odczyty w woltach, mimo że mają przy sobie jednostkę V.

### Przelicznik

**Wartość na ekranie podzielić przez √3 (1,732), żeby otrzymać napięcie fazowe w woltach.**

Przykład ze sprawy U‑028 — odczyt **414 / 115 / 418**:

| Ekran | ÷ √3 | Ocena |
|---|---|---|
| 414 | **239 V** | prawidłowe |
| 418 | **241 V** | prawidłowe |
| 115 | **66 V** | napięcie szczątkowe — **brak fazy** |

Podany przez producenta zakres pracy **280–480** odpowiada po przeliczeniu **162–277 V** na fazę, co jest sensownymi granicami.

### Dlaczego producent mówi o napięciu międzyfazowym

Zapytany wprost odpowiedział: **三个数值为线电压** („trzy wartości to napięcia międzyfazowe"), **是输入电压** („to napięcie wejściowe"), **正确范围是280V—480V**.

Formalnie zgadza się co do jednostki, bo urządzenie najprawdopodobniej mierzy napięcie fazowe i mnoży je przez √3. Ale **robi to dla każdej fazy osobno**, więc trzy liczby pochodzą z trzech niezależnych pomiarów. Dlatego jedna z nich może odbiegać — prawdziwe napięcia międzyfazowe są ze sobą geometrycznie związane i tak zachować by się nie mogły.

*Potwierdzenie z praktyki:* na stanowisku serwisowym gniazdo G8 ma **zmostkowaną jedną fazę na wszystkie trzy**. Prawdziwe napięcia międzyfazowe wynoszą tam zero, a mimo to ładowarka nie zgłasza błędu — bo każdy z trzech torów mierzy poprawne 230 V wobec N i wylicza około 400.

### Jak czytać odczyt

**Wszystkie trzy w zakresie 280–480** — zasilanie prawidłowe, przyczyny szukać gdzie indziej.

**Jedna wartość drastycznie zaniżona, dwie prawidłowe** — **brak jednej fazy**. Faza odłączona zachowuje napięcie szczątkowe rzędu kilkudziesięciu woltów, indukowane z sąsiednich przewodów. Sprawdzać: zabezpieczenia w rozdzielnicy, styki w gnieździe, wtyczkę, adapter.

**Wszystkie trzy zaniżone** — obniżone napięcie sieci albo duży spadek na długim przewodzie lub przedłużaczu.

**Dwie wartości podwyższone powyżej 480, jedna zaniżona** — dopiero to byłby obraz przerwy w przewodzie neutralnym, bo przy przesunięciu punktu gwiazdowego napięcia fazowe rosną **powyżej** wartości znamionowej. W U‑028 tak nie było: 239 i 241 V to dokładnie wartości prawidłowe.

### Pułapki pomiarowe przy weryfikacji u klienta

Odczyt „napięcie jest na każdej fazie" **niczego nie dowodzi**. Przy przerwanej fazie miernik cyfrowy o wysokiej impedancji pokaże napięcie indukowane z sąsiednich przewodów, często kilkadziesiąt woltów. Rozstrzyga pomiar **pod obciążeniem** — napięcie szczątkowe wtedy zapada, prawdziwe się utrzymuje.

### Ta sama skala w „High Voltage Reminder” i na ekranie spoczynkowym *(2026‑10‑05, sprawa R. Glocha)*

Ekran spoczynkowy ładowarki z okrągłym wyświetlaczem (przyciski Current/Timer) pokazuje napięcie w tej samej skali: na stanowisku **388 ↔ 224 V** (388 ÷ √3). Pod komunikatem **„High Voltage Reminder”** — te same trzy liczby, próg górny 480 (= 277 V). `[F — zdjęcie ekranu spoczynkowego; Z — że próg „High” to górna granica zakresu 280–480]`

**Niezasilony kanał pokazuje 000** (oczekiwany przez Dawida obraz przy zasilaniu tylko jednego kanału, 2026‑10‑06: dwa kanały 000). Na długiej instalacji odłączona faza może za to pokazać napięcie szczątkowe (U‑028: 115 = 66 V). `[F — relacja Dawida]`

**Korekta i wynik sprawy R. Glocha (2026-10-06):** serwis sprawdził urządzenie na gnieździe zwykłym 230 V i siłowym — na żadnym błąd nie wystąpił `[F — Dawid]`. Wynik: **usterki w przeprowadzonych testach nie stwierdzono**, zalecenie odesłania bez naprawy. Warunki zasilania u klienta są podejrzewaną przyczyną; konkretne połączenie N nie jest ustalone. Zdjęcia nie mają dwóch zer oczekiwanych przez serwis przy zasilaniu jednego kanału, więc nie potwierdzają zdjęciowo zgłoszenia dla takiego podłączenia.

**Sprostowanie pewności wcześniejszych wpisów:** zakres prawidłowy 280–480 podany przez producenta nie określa granicy pomiarowej ani nasycenia ADC. Teza, że 582/495 oznacza w rzeczywistości 400 V z nasyconym pomiarem, jest niezweryfikowaną hipotezą. Sam odczyt 000 nie identyfikuje połączeń przewodów. Poniższa tabela i wcześniejsze interpretacje nie stanowią dowodu na konkretną wadę instalacji ani podstawy do odtwarzania przepięcia na urządzeniu klienta. Zalecenie takiego odtwarzania wycofane.
**Czego się spodziewać przy typowych błędach połączeń** (ekran = napięcie kanału × √3):

| Sytuacja | Ekran | Uwagi |
|---|---|---|
| prawidłowo, 230 V | ok. 398 / 398 / 398 | |
| brak jednej fazy | ok. 400 / (kilkadziesiąt–kilkaset) / 400 | U‑028: 414 / 115 / 418 |
| zamiana N z jedną fazą albo odwrócenie kolejności wszystkich czterech przewodów | teoretycznie ok. **400 / 690 / 690**, kolejność zależy od zamiany | rzeczywiste napięcia wejść względem zacisku N urządzenia: ok. 230/400/400 V; nie 0/400/400; wskazania ekranu tylko przy zachowaniu liniowego przelicznika |
| ta sama faza jednocześnie na zacisku N i jednym zacisku L, dwie inne fazy na pozostałych L | teoretycznie ok. 000 / 690 / 690 | osobny wariant błędnego połączenia, nie zwykła zamiana czterech różnych przewodów. Nie stwierdzono go u klienta. Sam odczyt 000 nie dowodzi takiego połączenia |
| przesunięty (pływający) N | wartości zależne od obciążeń i miejsca przerwy | brak jednego uniwersalnego wzoru wskazań; zdjęcie nie ustala przyczyny |

**Rozstrzygnięcie obliczeniowe (2026-10-06):** przy odwróceniu kolejności czterech różnych przewodów L1,L2,L3,N → N,L3,L2,L1 wejścia ładowarki L1–N/L2–N/L3–N dostają około **230/400/400 V**. Zero względem PE na zacisku z rzeczywistym neutralnym nie jest zerem względem błędnie zasilonego zacisku N urządzenia. Dokładna tabela w `casey/Robert_Gloch/przebieg_sprawy.md`. Obliczenie nie potwierdza, że klient ma takie połączenie. Wcześniejszy wniosek, że 000/582/495 potwierdza ten wariant przez nasycenie toru, był nieuzasadniony. Źródło znamionowych napięć: [Schneider Electric](https://www.electrical-installation.org/enwiki/Definition_of_voltage_ranges).

**Historia interpretacji — poniższy akapit zastąpiony korektami z 06.10:**
Wniosek z obliczeń dla zamiany N z fazą: dwie wartości **równe** i bliskie 690. Para różnych wartości (np. 582 i 495) do zamiany nie pasuje. Ten sam komunikat na gnieździe 230 V z wartością > 480 na jednym kanale wymaga przesuniętego N (w instalacji albo w drodze N ładowarki/adaptera). `[F — obliczenie]` *Korekta (2026‑10‑05): „para różnych wartości nie pasuje” zakłada liniowy pomiar także powyżej zakresu. Przy 400 V na kanale (o 45% ponad górną granicę 277 V) tor może się nasycać i dawać zaniżone, różne wartości — wtedy 582 / 495 obok dokładnego 000 pasuje do fazy na zacisku N (hipoteza Dawida). Zdanie o gnieździe 230 V dotyczy tylko gniazda z poprawnym N.*

~~**Przypomnienie:** dobry wynik testu na G8 (jedna faza zmostkowana na trzy — odczyty na L1/L2/L3 prawie identyczne) nie wyklucza usterki widocznej tylko na prawdziwej sieci trójfazowej.~~ *Korekta (2026‑10‑05, Dawid): błędne. Ładowarka mierzy każdy kanał względem N, a mostek na G8 daje każdemu kanałowi to samo napięcie fazowe co prawdziwa sieć — **tor pomiaru napięć sprawdzony na G8 jest miarodajny**; na prawdziwej sieci wynik byłby ten sam.*

### Historia błędnych interpretacji tego odczytu

Zanim ustalono przelicznik, ten sam odczyt prowadził kolejno do trzech błędnych hipotez: przerwy w przewodzie neutralnym (przyjęto, że liczby to napięcia fazowe w woltach), zmostkowania dwóch faz (odrzucone, bo dałoby wartość bliską zeru, a nie 115) oraz uszkodzenia toru pomiarowego w urządzeniu (odrzucone testem na stanowisku). **Zasada: nie interpretować liczb wyświetlanych pod komunikatami bez znajomości skali** — por. U‑020, gdzie wartości okazały się próbkami układu detekcji uziemienia.

**Sprawa R. Glocha (2026‑10‑05) — moje błędy, do niepowtarzania:** (1) uznałem test na G8 za niemiarodajny dla toru pomiaru — a jest miarodajny (wyżej); (2) przypisałem zdjęcie 602 / 231 / 228 do gniazda 230 V, choć klient tego nie napisał, a wartość 602 (348 V) na gnieździe jednofazowym z poprawnym N jest niemożliwa; (3) wskazałem styk w adapterze, a ta ładowarka nie ma adapterów — **sprawdzać wersję i wyposażenie urządzenia, zanim zbuduje się na nich hipotezę**; (4) z niespójności „trójkąta” napięć wyciągnąłem wniosek o błędnym kanale, pomijając możliwość nasycenia pomiaru powyżej zakresu.

---

## Tuya — punkty danych, harmonogram, logi

### Punkty danych istotne diagnostycznie

| Nazwa w logu | Znaczenie | Uwagi |
|---|---|---|
| `Switch` | start/stop sesji ładowania | **`ON` z chmury uruchamia ładowanie w ok. 1 s** — potwierdzone na `timer_test` 2026‑09‑09, trzy niezależne przypadki. To pełna komenda startu, nie „zezwolenie" |
| `charge_now` / `Work Mode` | tryb pracy („Charging now") | ustawiany przez wpisy harmonogramu; sam, bez `switch`, nie uruchamia ładowania |
| `Charge Current Set` | nastawa prądu | w harmonogramie zaszyta we wpisie, nie jest osobnym ustawieniem |
| `Connection State` | stan CP (12/9/6 V) | patrz tabela wyżej |
| `Work State` | Charger Free / Wait / Charging | **`Charger Inserted` nie występuje** — na `timer_test` w 2000 zdarzeń z tygodnia tylko Free (20×), Wait (24×), Charging (23×). Scena z warunkiem „Charger Inserted" nigdy nie odpali; na „wpięte, nie ładuje" używać `Charger Wait`. *(sprawdzone na jednym urządzeniu, 2026‑09‑10)* |
| `Once Charge Energy` | energia bieżącej sesji | raportowana przy zakończeniu |
| `Fault` | kod usterki | `0` = brak |
| `Schedule charging` | zapis harmonogramu w urządzeniu | wartość binarna, np. `AAA=` |

### Start ładowania — jak wygląda w logu

Sprawny start to **`Work Mode = Charging now` i `Switch = ON` w tej samej milisekundzie**, jedna komenda o kształcie `"charge_now",<prąd>,true`. Urządzenie wchodzi w `Charger Charging` po kilku–kilkuset milisekundach. Tak wygląda wykonanie wpisu harmonogramu i tak wygląda start z aplikacji.

Sam `Switch = ON` z chmury również uruchamia sesję, w ok. 1 s. Dowody i pełne sekwencje: `LOGI_Tuya_timer_test_switch.md`.

**Pułapka diagnostyczna:** scena typu *If Work State : Charger Charging → Then Switch : OFF* gasi sesję po ok. 0,3–1,4 s od startu. Ładowanie faktycznie rusza, ale trwa tak krótko, że nie widać go ani w aplikacji, ani na ekranie urządzenia — objaw wygląda wtedy identycznie jak „komenda nie działa". Przy każdej takiej reklamacji **najpierw sprawdzić, czy klient nie ma aktywnej sceny wyłączającej**, zanim zacznie się szukać wady w urządzeniu.

Dwie sceny z tym samym warunkiem (`Charger Charging`) odpalają się równocześnie, kilkadziesiąt milisekund od siebie — wygrywa ta, której komenda dotrze ostatnia.

**`Work Mode` i `Switch` w tej samej milisekundzie to raport stanu po zmianie, nie komenda.** Przy starcie z komendy chmurowej `Switch = ON` raportu `Work Mode` nie ma wcale, bo tryb się nie zmienił. Wpis harmonogramu ustawia tryb, który zwykle już jest ustawiony, więc nic nie zmienia; scena przestawia przełącznik, który realnie stoi w OFF. *(2026‑09‑10, `timer_test`)*

**Odpięcie i ponowne wpięcie wtyczki samo przywraca `switch` na ON** (`timer_test`, 10.09, 10:25:55), niezależnie od tego, że wcześniej wyłączyła go automatyzacja. Klient, który przepnie kabel, zawsze uruchomi ładowanie — dlatego objawy związane ze scenami bywają nieregularne.

**Scena z wyzwalaczem godzinowym uruchamia ładowanie** (`Harmonogram` → `Charge Current Set` + `Work Mode : Charging now` + `Switch : ON`): potwierdzone 10.09 o 10:29, przejście w `Charger Charging` 0,8 s po komendzie. To obejście dla wpisów harmonogramu, które nie startują ładowania. Wymaga internetu — scena wykonuje się w chmurze, harmonogram w urządzeniu.

### Asymetria harmonogramu — przyczyna typowej reklamacji

**Wpis włączający harmonogramu ustawia `charge_now`, ale nie dotyka `switch`. Wpis wyłączający oraz automatyzacje chmurowe operują na `switch`.** Skutek: po każdym wyłączeniu przełącznik zostaje w pozycji OFF i żaden kolejny wpis harmonogramu ładowania nie uruchomi — urządzenie ma podłączony pojazd, prawidłowy tryb i prąd, i stoi.

Objaw zgłaszany przez klienta: „automatyzacje działają, ale po ich zakończeniu harmonogram nie startuje". Przesuwanie godzin nie pomaga. Szczegóły i dowody: `LOGI_Tuya_Marcin_harmonogram.md`.

### Format wpisu harmonogramu (zdarzenie `Timing`, źródło `app client`)

```
"TYPE":"CREATE", "id":861877997, "time":"13:02",
"dps":"\"charge_now\",20,true", "loops":"0111110", "status":"opened"
```

**`loops`** — maska dni tygodnia, siedem pozycji **od niedzieli**. `0111110` = poniedziałek–piątek („Robocze"). **`dps`** — punkt danych, wartość prądu, stan.

### Czytanie logów urządzenia

**Czasy podawać zawsze po przeliczeniu na lokalny.** Log zapisuje UTC (nagłówek kolumny kłamie, deklarując GMT+2). W rozmowie, w mailach i przy porównywaniu z tym, co widać w aplikacji, używać **czasu lokalnego** — surowe UTC tylko w plikach z logami i tylko z wyraźną adnotacją. Podanie godziny z loga bez przeliczenia jest bezużyteczne dla kogoś, kto patrzy na zegarek. *(zasada z 2026‑09‑09)*


- Adres: `iot.tuya.com/device/log` (lub `eu.platform.tuya.com/device/log`), wyszukiwanie po Device ID, **7 dni wstecz** w wersji darmowej.
- **Wybrać właściwe centrum danych** — dla Polski Central Europe. Przy złym centrum wynik jest pusty.
- Logi widać **tylko dla urządzeń powiązanych z projektem chmurowym** zalogowanego konta. Puste pola „strefa czasowa urządzenia" i „Pid" oznaczają, że urządzenia nie ma w projekcie — a nie brak zdarzeń.
- **Czas w tabeli jest przesunięty:** kolumna deklaruje GMT+2, ale zdarzenia zapisywane są w UTC. **Dodawać 2 h latem, 1 h zimą.** *(ustalone 2026‑09‑07 przez porównanie z godziną kliknięcia klienta)*
- Kolumna **Source**: `device itself` = raport stanu z urządzenia, `cloud` = komenda z automatyzacji, `app client` = działanie z aplikacji (edycje timera, zapytania).
- **Szum:** co ok. **6 h 20 min** urządzenie wysyła komplet raportów stanu (`Work Mode`, po 18–19 s `Switch`). To nie są komendy — odróżniać po braku zmiany `Work State` i `Connection State`.
- Komendy wysłane z aplikacji, gdy telefon jest w tej samej sieci Wi‑Fi co urządzenie, idą lokalnie i **mogą nie trafić do logu chmurowego**. Przy testach przełączać telefon na dane komórkowe.
- **Identyfikator do logu = Wirtualny identyfikator z aplikacji** (Panel urządzenia → ołówek → Informacje o urządzeniu → Virtual ID). Sprawdzone na pięciu urządzeniach: wszystkie 22 znaki, zaczynają się od „bf". Numer seryjny z tabliczki to najpewniej inny ciąg — niesprawdzone.
- **Odpowiedzi panelu rozróżniają przypadki:** `没有操作权限!` = urządzenie istnieje, ale konto nie ma uprawnień; `设备不存在` = takiego urządzenia nie ma w tym centrum danych; sukces z pustymi polami „strefa czasowa" i „Pid" = brak powiązania z projektem.
- **Logi wallboxów** są dostępne tylko z przestrzeni partnera: zalogować się kontem `michal+…tek@amperepoint.pl`, w prawym górnym rogu (我的空间 → 切换空间) wybrać **深圳市龙眼创新科技有限公司**, potem Log urządzenia w Central Europe. Z „Mojej przestrzeni" każdego konta odpowiedź to brak uprawnień. *(2026‑09‑26)*
- **Koniec pobranego okna to nie koniec zdarzenia.** Przed wnioskiem o czasie trwania albo o braku jakiegoś zdarzenia pobrać log do bieżącej chwili. *(26.09: „przekroczenie 7 min” i „brak punktu błędu” wynikały z logu uciętego o 11:46.)*
- Podejrzenie: dostęp do logów wynika z tego, do kogo należy **produkt (PID)**, a nie z powiązania urządzenia z projektem — konto widziało logi ładowarek klientów, których nie było w jego projekcie. Platforma ma też mechanizm „międzyfirmowego udostępnienia logów" (跨企业-日志权限授权).
- Panel ma wąski widok — przełącznik przestrzeni w nagłówku widać dopiero po poszerzeniu okna.
- **Bieżący stan urządzenia (online/offline) i data aktywacji:** w przestrzeni partnera AI Product → Device → **Device Details**. To lista wszystkich urządzeń produktu `gbmxngploofmhbjc` ze statusem „Activated | Online/Offline”, pierwszą i ostatnią aktywacją, adresem MAC i przyciskiem Logs. 29.09 było tam 112 urządzeń, 88 online. Log pokazuje tylko zdarzenia, a ta lista pokazuje stan w danej chwili. *(2026‑09‑29)*
- **Sprawdzanie aktualizacji oprogramowania:** w logu wybrać typ zdarzenia **OTA** (固件升级) zamiast „All”. „No Data” = w oknie 7 dni nie było aktualizacji. Zawsze sprawdzić też najnowsze zdarzenie bez filtra: urządzenie offline nie dostanie aktualizacji z chmury. *(2026‑09‑29, wallbox Karola)*
- **Czas w przestrzeni partnera (29.09):** kolumna „Time(GMT+2)” pokazywała czas **lokalny**; potwierdzone z datownikiem epoch zdarzenia. Pole `eventTimeStr` w odpowiedzi API (`/micro-app/device/api/deviceAllEventLog`) jest w **UTC**. Przy innych kontach i widokach obserwowano UTC w kolumnie — patrz wyżej. Przed przeliczaniem porównać z jednym zdarzeniem o znanej godzinie.

### Objaw: sterowanie działa, ale nie da się dodać urządzenia ani sceny

Sterowanie ładowarką odbywa się lokalnie po LAN, natomiast dodawanie urządzeń i scen wymaga chmury. Komunikat „Błąd sieci / Network request failed" przy zachowanym sterowaniu oznacza, że **telefon nie ma dostępu do chmury Tuya** — nie że urządzenie jest niesprawne. Test: wyłączyć Wi‑Fi, spróbować na danych komórkowych. *(zaobserwowane 2026‑09‑07)*

**Wariant: aplikacja „kręci się" i pokazuje pusty ekran na Wi‑Fi, na danych komórkowych działa** (sprawa Bogusz, 2026‑09). W tym samym czasie ładowarka klienta raportowała do chmury bez przerw (−70 dBm, ani jednej luki ponad 15 min w dwóch dobach). Urządzenie i aplikacja łączą się z chmurą różnymi drogami — urządzenie przez MQTT, aplikacja przez API HTTPS — więc sieć może przepuszczać jedno i blokować drugie. Podejrzenie, niepotwierdzone: filtrowanie DNS lub blokada reklam w routerze. Test: prywatny DNS `dns.google` w telefonie albo wyłączenie filtrów w routerze.

*Uwaga do korespondencji z tą sprawą:* w mailu do klienta napisano, że ładowarka „nie obsługuje sterowania lokalnego". To stoi w sprzeczności z ustaleniem wyżej (sterowanie lokalne po LAN działa) i nie było sprawdzone.

### Integracja z Home Assistant — TuyaExtend AmperePoint

- Dodatek pobiera dane przez **oficjalną integrację Tuya w HA**, która musi być skonfigurowana wcześniej. `hacs.json` dopuszcza HA od 2024.6; opis w README dotyczy testów na HA 2026.7.
- Błąd **`local_unsupported`** — „Połączenie odpowiada, ale tego układu DP jeszcze nie obsługujemy": LAN działa (IP, local key i protokół poprawne), ale układu DP danego modelu nie ma na liście obsługiwanych. Pełne sterowanie po LAN jest zweryfikowane tylko dla PRIME.
- **Plik diagnostyczny** (Ustawienia → Urządzenia oraz usługi → AmperePoint → ⋮ → Pobierz diagnostykę) z trybu chmurowego zawiera product ID, kategorię, bieżące DP i ich definicje — wystarcza do dopisania obsługi nowego modelu. Diagnostyka trybu lokalnego celowo tych danych nie eksportuje.

*Uzupełnienia z 2026‑09‑28 (sprawa M. Krawca, HA 2025.3; sprawdzone w kodzie wydania 0.5.39 z repo `amperepoint/tuyaextend-amperepoint`):*

- **`local_unsupported` pochodzi z własnego trybu lokalnego dodatku (dodawanie po adresie IP), a nie z tuya local.** Tryb ten rozpoznaje wyłącznie układy DP wallboxów PRIME: DP 102 jako JSON z polami `p`, `e`, `t` i tablicą `L` albo `L1`, do tego DP 109 jako tekst (`local_source.py`, `validate_snapshot`). Ładowarka serii Q zawsze dostanie ten komunikat i profil tuya local go nie usunie. Dla serii Q właściwa droga: tuya local z naszym profilem, a dodatek w trybie automatycznym, czytający encje tuya local.
- **Linię `LOCAL DPS` zapisuje w logu tuya local** w kroku wyboru typu urządzenia („Device matches <config> with quality of <n>%. LOCAL DPS: {...}”). Nie da się jej wziąć od klienta, który nie ma zainstalowanego tuya local.
- **Profile tuya local w repo bazowym i w forku mają różne nazwy.** Repo bazowe (z niego instaluje klient): `amperepoint_q_series_evcharger.yaml`, `amperepoint_q11_pro_evcharger.yaml`, `amperepoint_q22_ota_evcharger.yaml`, `amperepoint_prime_22kw_evcharger.yaml`, `amperepoint_prime_split_evcharger.yaml`, `amperepoint_ve_evcharger.yaml`. Plik `amperepoint_q_series_local.yaml` istnieje **tylko w forku** `dawidcekala-oss` (zmiana nazwy nie trafiła do repo bazowego). Klientom podawać nazwy z repo bazowego. Profil PRIME dodatek instaluje sam (`profile_installer.py`), profil Q trzeba skopiować ręcznie.
- **Minimalna wersja HA dla tuya local** (odczytane z `hacs.json` w repo `make-all/tuya-local`): wydanie **2026.2.0 → HA 2025.1.0**; od zmiany z 2026‑03‑02 (wydania od 2026.3.0) → HA 2025.11.0; obecny `main` → HA 2026.8.0. Na HA 2025.3 da się więc zainstalować tuya local 2026.2.0, wybierając wersję w HACS. Czy nasz profil i dodatek współpracują z tą wersją — niesprawdzone.
- **Błąd `Config entry AmperePoint (<id>) for tuyaextend_amperepoint.sensor has already been setup!`** zgłoszony jednocześnie dla wszystkich platform (`sensor`, `binary_sensor`, `number`, `select`, `switch`, `time`) **jest błędem wtórnym**. Mechanizm: `async_setup_entry` najpierw tworzy encje wszystkich platform, a dopiero potem uruchamia planer, tworzy panel i uruchamia automatyczne dodawanie ładowarek. Jeśli któryś z tych trzech kroków rzuci wyjątek, wpis przechodzi w stan „błąd konfiguracji”, a encje zostają zarejestrowane. Przy ponownym ładowaniu HA nie wywołuje wtedy naszego `async_unload_entry` (dla wpisu, który się nie załadował, tylko zmienia stan), więc drugie tworzenie encji kończy się tym błędem na każdej platformie — aż do restartu HA. **Właściwa przyczyna to pierwszy błąd konfiguracji wpisu, zapisany osobno i z innym śladem stosu** — prosić o pełny plik logu, pobrany przed restartem HA. Mechanizm odtworzony z kodu dodatku i znanego zachowania HA, niepotwierdzony na HA 2025.3. *Korekta (2026‑10‑01): potwierdzony logiem klienta (HA 2025.3.3) — pierwszy błąd to `TypeError` przy tworzeniu panelu, 23 s później błędy wtórne na 6 platformach.*
- **Pobranie pełnego logu HA od klienta:** Ustawienia → System → Logi, w nagłówku listy ikona strzałki w dół z podpisem **„Pobierz logi”** (obok odświeżania i menu ⋮). Pobiera cały plik `home-assistant.log` (`/api/error_log`), nie tylko widok skrócony. W menu ⋮ jest „Wyświetl cały log”. Adres bezpośredni: `<adres HA>/config/logs`. Sprawdzone w źródłach i polskich tłumaczeniach interfejsu HA 2025.3 (frontend 20250306.0) oraz na HA 2026.6.4. Plik jest nadpisywany przy restarcie HA, więc prosić o pobranie przed restartem. *(2026‑09‑28; wcześniej podałem klientowi nieistniejącą „opcję pobrania pełnego logu”)* Potwierdzone na naszym HA 2026.6.4: pobrany plik zaczyna się od startu HA (10:10:18) i zawiera wszystko do chwili pobrania, ze śladami stosu. Szukany wpis ma postać `ERROR (MainThread) [homeassistant.config_entries] Error setting up entry <nazwa> for <domena>` + `Traceback`.
- **Start HA bez DNS wyłącza oficjalną integrację Tuya:** `Error setting up entry <konto> for tuya` z `NameResolutionError` dla `apigw.tuyaeu.com`. Na naszym HA 28.09 (start 10:10) w logu do 14:17 nie było żadnej ponownej próby — encje z chmury Tuya zostają niedostępne do ręcznego „Załaduj ponownie” albo restartu. Przy zgłoszeniu „po restarcie nie ma encji Tuya” sprawdzić ten wpis. *(obserwacja z jednego logu; brak ponowień wywnioskowany z braku wpisów)*
- **Jak sprawdzić napis w interfejsie HA konkretnej wersji:** wersję frontendu odczytać z `homeassistant/components/frontend/manifest.json` w repo `home-assistant/core` (tag = wersja HA), pobrać koło `home-assistant-frontend==<wersja>` z PyPI i otworzyć `hass_frontend/static/translations/config/pl-*.json`. Umiejscowienie przycisków: repo `home-assistant/frontend`, tag = wersja frontendu, `src/panels/config/…`.
- **Zgodność z HA starszym niż bieżący nie jest sprawdzona dla pełnego uruchomienia dodatku.** CI uruchamia test w kontenerach HA 2024.6.0 i 2026.7.2 (`tests/ha_energy_smoke.py`), ale test celowo omija konfigurację wpisu — sprawdza tylko licznik energii. Deklarowane w `hacs.json` minimum 2024.6 dotyczy więc części kodu. *Korekta (2026‑10‑01):* **dodatek 0.5.39 wymaga w praktyce HA ≥ 2026.3.0.** `dashboard.py` wywołuje `frontend.async_register_built_in_panel(..., show_in_sidebar=True, ...)`; parametru `show_in_sidebar` nie ma w HA 2024.6–2026.2.0, pojawił się w 2026.3.0 (sprawdzone w źródłach `home-assistant/core`; wcześniej o widoczności w pasku bocznym decydowało podanie `sidebar_title` i `sidebar_default_visible`). Na starszym HA: `TypeError: async_register_built_in_panel() got an unexpected keyword argument 'show_in_sidebar'` → wpis przerwany po utworzeniu encji → błędy wtórne `has already been setup!`. Deklarowane w `hacs.json` minimum 2024.6 jest nieprawdziwe. `[F — log klienta 29.09 + źródła HA]`
- **Poprawka zgodności (gałąź `fix/ha-older-compat` w forku, 2026‑10‑01; PR #42 do repo bazowego, niescalony):** panel bez `show_in_sidebar` + wyrejestrowanie encji przy przerwanym uruchomieniu. **Rzeczywiste minimum dodatku z poprawką: HA 2025.2.0** (`LOVELACE_DATA` w `homeassistant.components.lovelace.const` pojawiła się w 2025.2.0; na 2024.6.0 dodatek się nie importuje). Sprawdzone testem pełnego uruchomienia na 2025.2.0, 2025.3.3, 2026.6.4 i 2026.9.4. `[F]`
- **Poprawka a nowszy HA — analiza regresji (2026‑10‑01):** `show_in_sidebar` ma wartość domyślną `True` w każdej wersji, która go zna (2026.3.0 … 2026.9.4 i gałąź `dev` — sprawdzone w źródłach); parametr był w kodzie od pierwszej wersji panelu (#5, 2026‑07‑14), nie jako obejście. Na HA 2026.9.4 panel zarejestrowany przez kod 0.5.39 i przez poprawkę jest **identyczny**, łącznie z opisem wysyłanym do przeglądarki. Zmiana zachowania tylko przy awarii po utworzeniu encji: wcześniej encje zostawały „pół‑żywe” przy wpisie w stanie błędu, a każda próba ponownego ładowania **uruchamiała kolejny planer w tle** (2026.9.4: po jednej awarii i przeładowaniu 2 planery zamiast 1); teraz encje i planer są sprzątane, wpis pokazuje błąd, ponowne ładowanie działa. Planer sam łapie błędy poleceń do ładowarki (`_async_send`), więc taka awaria to w praktyce tylko błąd programu albo zapisu na dysk. `[F — porównanie w kontenerze]`
- **Test pełnego uruchomienia dodatku w prawdziwym HA:** `tests/ha_setup_smoke.py` (na gałęzi wyżej). Uruchomienie dowolnej wersji HA w izolowanym kontenerze: `docker run --rm --network none --mount "type=bind,source=<repo>,target=/work,readonly" --entrypoint python ghcr.io/home-assistant/home-assistant:<wersja> /work/tests/ha_setup_smoke.py` (w Git Bash poprzedzić `MSYS_NO_PATHCONV=1`). Odtwarza błąd klienta na niepoprawionym kodzie — dobry sposób, żeby sprawdzić zgłoszenie „nie działa na mojej wersji HA” bez angażowania klienta.
- **Tuya local 2026.2.0 na HA 2025.3.3** (sprawdzone 2026‑10‑01 w kontenerze): integracja się ładuje; na zapisie `LOCAL DPS` Q11 PRO (`amperepoint/docs/device-q11-pro.md`) profil `amperepoint_q11_pro_evcharger.yaml` pasuje w **100%**, `amperepoint_q_series_evcharger.yaml` w 75%; dopasowanie „pasuje” zgłaszają też liczne obce profile (dopasowanie tuya local jest luźne). **Dla Q11 podawać profil `q11_pro`.** W kroku wyboru typu urządzenia tuya local zaznacza domyślnie profil o najwyższym dopasowaniu — przy remisie (np. obcy `aimiler_11kW_evcharger`, opisany w dokumentacji repo) może to nie być nasz, więc klient musi wskazać `amperepoint_q11_pro_evcharger` ręcznie. Linię „Device matches … LOCAL DPS: …” tuya local zapisuje na poziomie WARNING właśnie w tym kroku. `[F — kod tuya local 2026.2.0 + test]`
- **Oficjalna integracja Tuya a ładowarki EV (kategoria `qccdz`):** encje (tylko przełącznik) tworzy dopiero **od HA 2025.8.0**; w 2025.3–2025.7 — żadnych (sprawdzone w źródłach `tuya/switch.py`). Dodatek wykrywa ładowarki po encjach w rejestrze, więc ścieżka „Tuya Cloud”, którą `INSTALL.pl.md` zaleca dla serii Q od 0.5.38 (dodatek czyta wtedy wszystkie DP z działającej integracji Tuya, także bez encji), **wymaga HA ≥ 2025.8**. Na starszym HA: tuya local 2026.2.0 + profil `amperepoint_q11_pro_evcharger`. Zdanie z maila z 25.09 („oficjalna integracja wystawia tylko przełącznik”) jest prawdziwe dopiero od 2025.8. *(2026‑10‑05)* `[F]`
- **Ścieżka tuya local sprawdzona na HA 2025.3.3** (dodatek 0.5.40, tuya local 2026.2.0, profil q11_pro, ładowarka podstawiona zapisem `LOCAL DPS` Q11 PRO; skrypt `istotne_casey/Marcin_Krawiec/testy/test_ha2025_3_tuya_local_q11pro.py`): tuya local tworzy 22 encje; dodatek rozpoznaje ładowarkę (q_series, tuya_local, 25 przypisanych encji). **Automatyczne przyjęcie** przy starcie HA tworzy **nowy** wpis z danymi; istniejący pusty wpis (bez przypisanych encji) zostaje pusty — trzeba go usunąć. Ręcznie: „Dodaj integrację → AmperePoint → Skonfiguruj wykrytą ładowarkę”. Metoda testu bez ładowarki: podmiana `TuyaLocalDevice.async_refresh` na zwrot zapisanego `LOCAL DPS` (i wyłączenie `start`). *(2026‑10‑05)* `[F]`
- **Tuya Local ≠ LocalTuya — klienci mylą.** **Tuya Local**: repo `make-all/tuya-local`, w HACS nazwa „Tuya Local”, katalog `custom_components/tuya_local`, wersje w formacie daty (np. 2026.2.0); **nie ma go w domyślnym katalogu HACS** (lista `hacs/default`, sprawdzone 2026‑10‑05) — dodawać jako repozytorium niestandardowe `https://github.com/make-all/tuya-local`, typ Integracja. **LocalTuya**: repo `rospogrigio/localtuya`, w HACS „Local Tuya”, katalog `custom_components/localtuya`, wersje 5.x; jest w domyślnym katalogu, więc wyszukanie „tuya local” w HACS podsuwa właśnie jego. Nasze profile są dla Tuya Local. W oknie pobierania HACS wybór wersji: „Need a different version?” (polskiego brzmienia nie sprawdziłem). *(2026‑10‑05, sprawa M. Krawca)* `[F]`
- **Tuya local 2026.2.0 — puste pole IP i błąd „Nie można podłączyć się do urządzenia z tymi danymi…” (klucz `connection`):** po logowaniu przez aplikację (Smart Life albo Tuya) krok „Znajdź adres IP urządzenia” szuka ładowarki rozgłoszeniami UDP (`tinytuya.find_device`). Gdy nie znajdzie — pole IP zostaje puste, **a „Wersja protokołu” ma domyślnie 3.3**, bo chmura wersji nie podaje (`cloud.py`: `"version": None`; `config_flow.py`, `async_step_local`: `proto_opts = {"default": 3.3}`, nadpisywane tylko wynikiem wyszukiwania). Nasze ładowarki mówią **3.5** (zapis z Q11 PRO; nasz działający wpis Q37 OTA też 3.5), więc z 3.3 test połączenia nie przechodzi nawet przy dobrym IP. **Rozwiązanie:** w tym samym oknie wpisać IP ładowarki — **adres nadany przez router, odczytany z listy urządzeń w panelu routera, nie wymyślony** (ładowarkę rozpoznać, porównując listę przy włączonej i wyłączonej ładowarce; adres IP pokazywany w aplikacji Tuya/Smart Life i zwracany przez chmurę to adres internetowy — komentarz w `config_flow.py`, `async_step_search`: „Current IP is the WAN IP which is of no use”; zalecić stały adres w routerze) i ustawić „Wersja protokołu (spróbuj auto jeśli nieznana)” na **3.5**; Device ID i Local key z chmury zostawić; na czas łączenia zamknąć aplikację w telefonie. Wyszukiwanie zawodzi najpewniej, gdy HA działa w Dockerze bez sieci hosta (rozgłoszenia nie docierają do kontenera) `[Z]`. *(2026‑10‑06, sprawa M. Krawca)* `[F — kod]`
- **Jak czytać `installation_type` / `docker` w diagnostyce HA** *(2026‑10‑06, kod HA 2025.3.3: `helpers/system_info.py`, `util/package.py`)*: `"docker": true` znaczy „działa w kontenerze” — warunek to istnienie `/.dockerenv` (Docker) **albo** `/run/.containerenv` (Podman) albo zmienna Kubernetes albo oficjalny obraz; to nie przesądza, że runtime to Docker. `"installation_type": "Home Assistant Container"` = kontener + użytkownik root + **oficjalny obraz HA**; obca budowa daje „Unsupported Third Party Container”. Nazwy kontenera ani trybu sieci diagnostyka nie podaje. `[F — kod]`
- **Znalezienie adresu IP ładowarki bez routera — `tinytuya scan`** *(2026‑10‑06)*: biblioteka `tinytuya` jest w kontenerze HA, gdy zainstalowany jest nasz dodatek (wymaga `tinytuya==1.20.0`) albo tuya local (`==1.17.4`). Polecenie na komputerze z HA: `docker exec -it -w /tmp homeassistant python3 -m tinytuya scan` — nasłuch rozgłoszeń UDP 6666/6667/7000 przez 18 s (urządzenia 3.5 wywoływane rozgłoszeniem na 7000 co 6 s), wypisuje dla każdego urządzenia `Address`, `Device ID`, `Version`; ładowarkę rozpoznać po Device ID z formularza tuya local. `-w /tmp`, bo skaner zapisuje `snapshot.json` w bieżącym katalogu (bez tego trafia do `/config`). **Działa tylko, gdy kontener ma sieć hosta** (`--network=host`, jak w oficjalnej instrukcji HA Container); na naszym HA (Docker Desktop, sieć `bridge`) skan znalazł 0 urządzeń. Tryb `-force <podsieć>` wymaga kluczy w `devices.json` — bez nich sam się wyłącza. Zapasowo na zwykłym komputerze w tej samej sieci: `python -m pip install tinytuya`, `python -m tinytuya scan` (zezwolić w zaporze). `[F — test na naszym HA]`
- **Możliwy konflikt wersji `tinytuya`** między naszym dodatkiem (`==1.20.0`) a tuya local 2026.2.0 (`==1.17.4`) — HA może przy każdym starcie przeinstalowywać pakiet. Na naszym HA zainstalowana jest 1.20.0. Niesprawdzone, czy przeszkadza. `[Z]`
- **Tuya local 2026.2.0 — dodawanie urządzenia:** wybór między ręcznym (Device ID, IP, local key) a logowaniem przez aplikację Smart Life (kod użytkownika + kod QR, potem lista urządzeń i wyszukiwanie IP w sieci — **na czas wyszukiwania zamknąć aplikację w telefonie**, bo blokuje połączenie lokalne). Krok typu urządzenia: „Wybierz typ urządzenia”. *(z tłumaczeń tuya local 2026.2.0)*
- **Wydanie v0.5.40** (2026‑10‑01): poprawka zgodności z HA 2025.2–2026.2 (PR #42) + poprawka autora repo `1986818` dot. odzyskiwania panelu. Panel działa na HA 2025.3.3 u klienta (relacja klienta 05.10).
- **HA 32‑bitowy (armv7, armhf, i386) kończy się na 2025.11.x.** Wsparcie zakończone z wydaniem 2025.12; w rejestrze `ghcr.io/home-assistant/armv7-homeassistant` jest 2025.11.3, nie ma 2025.12.0. Rozpoznanie: w pliku diagnostyki wpisu dodatku pole `"arch": "armv7l"` (sekcja `home_assistant`). Takiemu klientowi **nie zalecać aktualizacji HA** ponad 2025.11 — bez przeinstalowania systemu na 64‑bitowy jest niemożliwa; odpada też bieżący tuya local (wymaga 2026.8) i dodatek 0.5.39 (2026.3). *(2026‑10‑01, sprawa M. Krawca)*
- **Ostrzeżenia loadera „We found a custom integration … not been tested” nie są znacznikiem restartu.** W logu klienta wystąpiły 29.09 00:01 bez ponownego uruchamiania wpisów; restart rozpoznawać po ponownym „Error setting up entry” / ładowaniu integracji albo po początku nowego pliku. Pobrany plik logu u klienta objął 24.09 14:34 – 29.09 12:59, czyli od ostatniego restartu. *(2026‑10‑01)*

### Harmonogram przez Bluetooth — niewiadoma

Wykonanie wpisu harmonogramu nie wymaga internetu (wykonuje go urządzenie). Czy aplikacja pozwala **ustawiać** harmonogram przez Bluetooth bez Wi‑Fi — niesprawdzone. Moduł ma Wi‑Fi i Bluetooth, ale to zależy od konfiguracji produktu. Otwarte też: czy zegar urządzenia przetrwa zanik zasilania bez internetu. Procedura testu na `timer_test` opisana w rozmowie z 2026‑09‑25.

*Korekta (2026‑09‑28): zdanie „wykonuje go urządzenie” to wniosek, nie fakt, a źródła są sprzeczne.*
- [F] Logi `timer_test` (Q11 PRO) pokazują wykonanie wpisu wyłącznie jako raport `device itself`. Nie ma przy nim `Publish` ze źródła `cloud`, który pojawia się przy scenach.
- [F] Definicja produktu Q21 (`kvldga0omutrnify`, arkusz „Product Advanced Functions” w eksporcie z 17.09) ma funkcję *CloudTiming: „Tuya Cloud provides cloud timing without local timing”*.
- [F] 28.09 Dawid zapisał harmonogram w aplikacji na danych komórkowych, potem wyłączył w telefonie wszystkie sieci, a wpis i tak się wykonał. To dowodzi tylko, że telefon nie jest potrzebny. Ładowarka miała internet.
- [Z] Dla Q11 PRO wykonuje moduł Tuya. Rozstrzygnie test: ładowarka z modułem Tuya odcięta od internetu regułą w routerze, a wpis ma się wykonać w tym czasie (test C12 w `SHELLY\DevKit\testy_offline\02_Q11_testy_bez_internetu_v1.pdf`).

### Punkty danych na łączu szeregowym Q11 — z logów modułu Shelly *(2026‑09‑28)*

Źródło: logi DevKitu Shelly wpiętego w miejsce modułu Tuya, 24–25.09, około 10 h rozmowy ze sterownikiem. Pełne zestawienie: `SHELLY\DevKit\dokumenty\Q11_zestawienie_DP_Tuya_Shelly_v1.pdf`.
- [F] Sterownik wysyła 13 z 17 punktów: 3, 4, 6, 7, 8, 9, 10, 13, 14, 18, 19, 24, 25. **Nigdy nie wysłał** 1 (licznik całkowity), 17 (limit energii), 23 (wersja) ani 33.
  *Korekta (2026‑09‑29):* [F] licznik całkowity (1) przychodzi **co 90 s, gdy ładowarka jest w stanie „ładuje”**. Widziany 28–29.09, kiedy symulator od 28.09 13:20 trzymał stan „ładuje”; wartość 0, bo bez obciążenia energia nie płynie. 24–25.09 ładowarka nie ładowała. Czyli 14 z 17; nie widziane zostają 17, 23, 33. [Z] Te też mogą zależeć od stanu albo od menu.
- [F] `fault` (10) idzie jako mapa bitowa **2 B**, a definicja ma 17 kodów. Bit 16 („przegrzanie”) się nie mieści. Pytanie do fabryki.
- [F] `charge_energy_once` (25) przyszedł raz, 24.09 o 11:23, z wartością 0, w jednej ramce razem z `switch`.
- [F] `local_timer` (19) = 2 B: godzina startu, godzina końca (0–23), bez minut. Tak koduje go `tuyaextend_amperepoint` (`_decode_schedule_window`); w logu `0000`.
- [F] `charge_cur_set` (4) ma w definicji Tuya zakres 6–32 A, choć Q11 to 16 A.
- *(2026‑09‑29, próba z modułem Shelly na Q11 z symulatorem auta)*
  - [F] Zapis okna godzin (19) jako 2 bajty `16 06` sterownik przyjmuje i potwierdza w ciągu kilku sekund.
  - [F] **Po przyjęciu okna sterownik sam przełącza tryb pracy (14) na „harmonogram” (2).** Poza oknem przestaje ładować: stan przeszedł z „ładuje” na „czeka”. Po zapisie trybu „natychmiast” (14 = 0) wraca do ładowania.
  - [F] **Okna z równą godziną startu i końca (0–0) sterownik nie przyjmuje.** Odsyła poprzednie okno (0–6). Wartość `0000` widać tylko jako stan fabryczny albo z aplikacji Tuya.
  - [F] Zapis 4 bajtów `31 36 30 30` (tekst „1600”) sterownik ignoruje bez odpowiedzi. Moduł Shelly ponawia wtedy ramkę kilka razy.
- *(2026‑09‑29 12:01–12:04, sterowanie z Home Assistant przez moduł Shelly; symulator odłączony, stan „wolna”)*
  - [F] **Limit energii (17) i tryb pracy (14) są sprzężone.** Zapis limitu większego od 0 sam przełącza tryb na „do limitu energii” (14 = 1). Po zapisie trybu „natychmiast” sterownik zgłasza limit 0. Tryb „do limitu energii” przy limicie 0 jest odrzucany: sterownik odsyła „natychmiast” (12:02:44). Razem z oknem (19 → tryb „harmonogram”) wychodzi reguła: **tryb wynika z ostatnio ustawionego parametru**.
  - [F] Po zapisie limitu energii sterownik przez kilka sekund powtarza meldunek limitu i trybu, około 10 par na sekundę (12:02:00–12:02:03 ≈ 45 par, 12:03:06–12:03:12 ≈ 60 par). W tym czasie nie odpowiada na sygnał życia modułu: 6 razy „Heartbeat timed out”, każde ustąpiło po 1–5 s.
  - [F] Odpowiedź na zapis przychodzi po 0,3–3 s i często najpierw ze starą wartością: limit prądu 14 → zapis 9 → meldunki 14, potem 9. Okno 1–1 odrzucone ponownie (równe godziny).
  - [F] Limit prądu (4) i włącznik (18) z Home Assistant: każda zmiana potwierdzona (9 A, 6 A, 6 przełączeń włącznika w 20 s).
- *(2026‑09‑29 13:43–14:16, dalsze testy z modułem Shelly)*
  - [F] **Brak potwierdzenia nie znaczy odmowy.** Zapis trybu „natychmiast” o 14:01:43 został bez odpowiedzi, a przy odpytaniu wszystkich punktów o 14:04 sterownik podał tryb 0. O 12:02:38 ten sam zapis potwierdził w 1 s.
  - [F] Pierwsza odpowiedź na zapis to zwykle **poprzednia** wartość, potwierdzenie nowej przychodzi osobno albo wcale: limit 12 → zapis 10 → odpowiedź 12, potwierdzenia 10 brak (14:07:39); przy następnym zapisie odesłał 10 jako „starą”.
  - [F] Wyłączenie ładowania o 13:44:27: odpowiedź dwa razy „włączone”; przy starcie modułu o 13:56 sterownik podał „włączone”. Czy odrzucił, nieustalone.
  - [F] Po starcie modułu sterownik po około 23 s odpowiada na odpytanie wszystkich punktów; po synchronizacji czasu moduł wysyła mu godzinę (ramka 0x34).
- *(2026‑09‑30, test pamięci z zanikami zasilania całej ładowarki)*
  - [F] **Sterownik pamięta limit prądu przez zanik zasilania** (11 A, potem 9 A zgłoszone po włączeniu).
  - [F] Po włączeniu zasilania zgłasza wersję (23) „V1” — wcześniej nigdy jej nie wysłał. **Okna godzin (19) po włączeniu zasilania nie zgłasza**, także przy późniejszym restarcie samego modułu; 29.09 przy restarcie samego modułu zgłaszał 2–0. [Z] Okno ginie przy zaniku albo sterownik nie zgłasza pustego okna.
  - [F] **Wyłączenia ładowania (18 = 0) nie przyjmuje** (30.09 10:59:56 i 11:06:50, tryb „natychmiast”, bez auta): odpowiada „włączone”, po restarcie modułu nadal „włączone”. 29.09 o 12:03 (tryb „do limitu energii”) wyłączenie przyjmował.
  - [F] Po włączeniu zasilania odpowiada na odpytanie punktów po 21–30 s; 30.09 o 10:52 przez pierwsze 28 s odpowiedział tylko temperaturą.
  - [F] **Okno godzin i tryb „harmonogram” giną przy zaniku zasilania** (30.09 12:1x): przed zanikiem, przy restarcie samego modułu, sterownik zgłaszał okno 2–4 i tryb 2; po zaniku tryb 0 („natychmiast”) i brak okna, także przy kolejnym odpytaniu. Limit prądu (12 A) został. Okna nie da się ustawić z menu ładowarki — menu ma tylko opóźnienie ładowania.
  - *Korekta (30.09 12:40):* menu ma opóźnienie i czas trwania ładowania (czyli okno, ale nie wprost). Po ustawieniu ich w menu sterownik nic nie wysłał; przy odpytaniu (restart modułu) podał okno `0000` i tryb 0. **Ustawienia opóźnienia z menu nie widać w żadnym zgłaszanym punkcie.** [Z] Kandydat: punkt 33 `mode_set` (raw, do 128 B), nigdy nie zgłoszony. Okno po zaniku zasilania sterownik podaje jako `0000` (wyzerowane).
  - [F] (30.09 12:41) Z opóźnieniem ustawionym w menu: tester podłączony od razu w stanie C → sterownik zgłosił „ładuje”, po około 3 s „czeka”; przełączanie sygnału 9 V ↔ 6 V nie zmieniło „czeka”; po 23 s sam zgłosił włącznik (18) = wyłączony; po odłączeniu „wolna”. Dawid: ładowanie załączyło się od razu i wyłączyło prawie natychmiast. [Z] Opóźnienie z menu działa dopiero po starcie ładowania (krótkie załączenie stycznika) i zeruje włącznik; sprawdzi to powtórka bez opóźnienia.
  - [F] **Opóźnienie i czas trwania ustawiane w stanie C dają na ekranie inne wartości niż wybrane w menu** (Dawid, 30.09). Tylko gdy ładowarka jest w stanie C (auto chce ładować); to samo na ładowarce z modułem Tuya, więc usterka sterownika — do fabryki. Wartości do dopisania.
  - *Uwaga do nazewnictwa (Dawid, 30.09):* okno godzin (19) i opóźnienie z menu to ustawienie **jednej sesji na czas**, nie harmonogram. Harmonogram Tuya ustawia się w aplikacji (zob. wyżej, kto go wykonuje).
  - [F] **Okno godzin (19) wykonuje sam sterownik, według godziny od modułu** (30.09, test C6 z przesuniętym zegarem): okno 22–23, tester w C — przed 22:00 „czeka”, o 22:00:03 „ładuje”, o 23:00:03 „czeka”. Godzinę sterownik bierze z odpowiedzi modułu na swoje pytanie o czas (ramka 0x1C, co około 18 s) i z ramki 0x34 po starcie modułu.
  - [F] **Po zaniku zasilania z podłączonym autem ładowanie rusza samo** (30.09 15:19, tester w C): około 30 s po włączeniu stan „ładuje”, limit zachowany, tryb „natychmiast”.
  - [F] **Restart modułu nie przerywa ładowania** (30.09 15:00–15:07, tester w C, 5 restartów po około 30 s bez modułu, trzy jeden po drugim): sterownik ładował dalej, na ekranie bez zmian (Dawid).
  - [F] Ikona Wi-Fi na wyświetlaczu co kilkadziesiąt sekund znika i wraca, choć moduł co 30 s wysyła ten sam stan sieci 4 (30.09, moduł bez internetu).
  - [F] Przy przejściu testera A → B → C sterownik nie zgłasza stanu „podłączone” (1); z „wolna” przechodzi od razu na „ładuje” (30.09, dwa razy).
  - [F] **Limit prądu zmieniony w menu sterownik zgłasza od razu** (30.09 14:05, 8 A: meldunek 4 = 8 w ciągu sekund), inaczej niż opóźnienie z menu. Zachowuje go przez zanik zasilania.
  - [F] **Opóźnienie i czas trwania z menu giną przy zaniku zasilania** (Dawid, 30.09 13:02–13:08, dwa razy: raz po sesji z testerem, raz bez auta — po włączeniu zasilania ekran bez opóźnienia i czasu). Ustawienie opóźnienia w trakcie ładowania od razu przerywa ładowanie: stan „ładuje” → „czeka” (webhook 13:03:58 czasu laptopa).
  - [F] Włącznik (18): po włączeniu zasilania sterownik zgłasza „włączony” (13:06:00), po zakończeniu sesji, przy przejściu na „wolna”, sam zgłasza „wyłączony” (13:04:21, także 12:41:38).
    *Korekta (Dawid, 30.09):* włącznik (`switch`, 18) to osobna encja, nie stan ładowania; moje przypuszczenie o „znaczniku sesji” wycofane. Zostaje sama obserwacja.

---

## Wallbox (PID `gbmxngploofmhbjc`) i moduł DLB‑A1

*(sprawa z 2026‑09‑26, wallbox u klienta z modułem DLB; szczegóły w `LOGI_Tuya_wallbox_DLB_bfe26d.md`)*

### Dane urządzenia z logu

Firmware `(V8.0.7)F1.3.6`, „Type B, AC 30mA + DC 6mA", wariant produktu 3, maksimum 16 A, nastawy do wyboru w aplikacji: **6, 8, 10, 13, 16 A** (12 A nie da się wybrać). Nazwy zdarzeń po chińsku:

| Zdarzenie | Znaczenie | Format |
|---|---|---|
| 指标信息 | pomiary | `L1:[U×10, I×10, P×10 kW]`, `t` = temperatura ×10 °C, `p` = moc całkowita ×10 kW, `d` = czas sesji w dziesiątych sekundy (potwierdzone), `e` = energia sesji (jednostka nieustalona) |
| 工作状态 | stan pracy | 101 bezczynny · 200 wtyk włożony · 300 ładowanie · **400 błąd** |
| 调试用工作状态 | stan (debug) | 闲置状态 bezczynny · 插入充电枪 wtyk · 充电中 ładowanie · 发生故障 błąd · 休眠 uśpienie |
| 报警信息 | alarm | `{"t":"<czas urządzenia>","v":400}` — 400 = ochrona przed przeciążeniem prądu (komunikat na ekranie) |
| 上位机心跳 | heartbeat | po `off` od urządzenia pomiary przychodzą tylko co 60 s — stąd luki w logu |
| 设置充电电流 / 最大充电电流 | nastawa / maksimum prądu | A |
| 设备重启 | restart | 软件复位 reset programowy · 电源重启 zanik zasilania |
| 充电记录 | rekord sesji | `s`, `e` godziny, `d` czas w s |
| 开机自检结果 | autotest | `r:[1,1]` we wszystkich odczytach |

**Alarm przeciążenia jest w logu** jako 报警信息 `v:400` ze stanem pracy 400 *(korekta 2026‑09‑26: wcześniej wpisane „brak punktu danych błędu” wynikało z okna logu, w którym alarm nie wystąpił)*. **Brak danych z DLB** — przydziału prądu nie widać nigdzie. **Napięcie raportowane jednakowo na trzech fazach**, także przy zasilaniu trójfazowym u klienta — najpewniej jedna wartość dla wszystkich faz.

### Wyświetlacz DLB na nagraniu do góry nogami

Jeśli obraz jest obrócony (napisy „DLB CONTROLLER" i „PE L N" do góry nogami — u Karola okazało się, że to telefon był odwrócony, a moduł stoi normalnie), wyświetlacz czyta się po obróceniu o 180°: „L" wygląda jak „7", „3" jak „E", „E" jak „3", kolejność znaków się odwraca. **`E7` i `E10` to wtedy nie kody błędów.** Zanim uzna się moduł za zamontowany odwrotnie, porównać układ złączy z innym zdjęciem albo obrócić klatki (ffmpeg `transpose=1,transpose=1`).

| Widać | Znaczy |
|---|---|
| `17` / `27` / `E7` | etykiety L1 / L2 / L3 |
| `335` | SEt |
| `210` | 12 A |
| `E10` | 13 A |
| `020` | 20 (symetryczne) |

### Obserwacje z tej sprawy

- Przy SEt 20 (sufit 18 A) i nastawie wallboxa 16 A samochód trójfazowy pobierał przeważnie ok. 12,4 A, czasem ok. 16 A, chwilowo ok. 7 A — **przydział zmienia się w obie strony**, nie jest zablokowany.
- **W trybie DLB samochód pobiera więcej, niż wynosi nastawa wallboxa:** 18–19,1 A na fazę (12,2–12,7 kW) przy nastawie 16 — po restartach (11:39, 11:44), ale też minuty po włączeniu (12:05, 12:57); 16,7 A przy nastawie 10, 16,4 A przy 13, 20,2 A przy 15 (nastawy ustawione przed sesją). Klient niezależnie zgłaszał „13 kW przy 11‑kilowatowym aucie".
- **Alarm 400 (ochrona przed przeciążeniem):** tylko w trakcie ładowania; przy znanym prądzie zawsze ≥126% nastawy, przy 119% 5 min bez alarmu → próg ok. 120–125% nastawy, liczony ze zmierzonego prądu `[próg: Z]`. Reakcja: stop w ok. 1 s, nastawa −1 A (to jest „automatyczne przełączenie na ładowanie niskim prądem”, niezapisywane — po włączeniu zasilania wraca poprzednia), po 10–55 s gotowość; auto może wznowić i — skoro nastawa nie ogranicza prądu — dostać kolejny alarm.
  *Dopisek 2026‑09‑27:* notatka z instrukcji wallboxa M3A1 (`../WALLBOX_architektura/AI_PAMIEC_wallbox_M3A1.md`, §3) podaje próg „Overcurrent" jako przekroczenie nastawy o ponad 20% lub o 2 A. Jeśli liczy się większa z tych dwóch wartości, zgadzają się wszystkie dane z logu: nastawa 16 → próg 19,2 A (19,1 A trzymane 5 min bez alarmu), 13 → 15,6 A (alarm przy 16,4 A), 10 → 12 A (alarm przy 12,9 A) `[Z — dokładne brzmienie sprawdzić w skanie instrukcji; model wallboxa u klienta niepotwierdzony]`.
- Przy nastawie 15–16 alarmy wypadały w sesjach z L3 = 0 (L1 do 20–21 A); na trzech fazach auto stawało na 18–19 A, bez alarmu.
- **Pole „DLB x.x A" na ekranie wallboxa** pokazuje wartość otrzymaną z DLB — przy normalnym ładowaniu np. 12.1 A, przy 12,4 A pobieranych przez auto, więc najpewniej prąd zmierzony przekładnikami. W chwili komunikatu „Ochrona przed przeciążeniem prądu — Automatyczne przełączenie na ładowanie niskim prądem" pole pokazywało **0.0 A** przy nastawie 15 A. Napięcie 224 V na tym zdjęciu nie przesądza, czy płynął prąd — spoczynkowe było tego dnia 226–228 V. *Korekta: nastawa 15 i 224 V odpowiadają w logu chwili tuż po alarmie (nastawa obniżona z 16 na 15, prąd już 0, pierwszy odczyt 224–225 V) — „DLB 0.0 A” może znaczyć po prostu, że auto już nie ładuje; to nie jest dowód braku danych z DLB.*
- **Hipoteza uzupełniająca:** ochrona porównuje z nastawą wallboxa **wyliczone pozwolenie**, a nie zmierzony prąd. Tłumaczy komunikat przy włączeniu bez auta (DLB = 0 → pozwolenie 20 A > nastawa) i szybsze wyzwalanie przy niskich nastawach. Test: komunikat pojawia się bez przepływu prądu (auto odłączone albo nieładujące, restart wallboxa, nastawa 6 A). *Log jej nie potwierdza: wszystkie 12 alarmów w trakcie ładowania, a przy znanym prądzie był on ≥126% nastawy.*
- **Mechanizm — podejrzenie mocno poparte, niepotwierdzone:** gdy wartość z DLB spada do 0 (restart wallboxa, zmiana nastawy), wallbox koduje na CP pozwolenie z nastawy DLB (20 A) zamiast przyciąć je do własnej nastawy. Samochód pobiera więcej niż nastawa, więc wallbox włącza ochronę nadprądową — tym szybciej, im niższa nastawa. Wymiana kontrolera DLB tego nie zmienia, bo wada byłaby po stronie wallboxa. **Test:** pomiar wypełnienia CP oscyloskopem przy odciętych danych z DLB — 26,7% (16 A) poprawnie, 33,3% (20 A) potwierdza. **Wymaga sparowanego modułu DLB** — bez parowania wallbox pracuje w zwykłym trybie, a w nim działa poprawnie (u klienta przed montażem DLB nie było problemów), więc test bez DLB niczego nie wykaże. Szczegóły: `LOGI_Tuya_wallbox_DLB_bfe26d.md`, sekcja 7.
- **Nastawę prądu na samym wallboxie zmienia się tylko przy wyłączonym ładowaniu**; w trakcie ładowania — wyłącznie z aplikacji. U klienta komunikat pojawiał się, zanim cokolwiek robił w aplikacji, więc zmiana nastawy nie jest wyzwalaczem — tylko przesuwa próg. Wyzwalaczem jest brak danych z DLB, przynajmniej po włączeniu zasilania wallboxa.
  *Korekta po pełnym logu z 26.09: w logu są 4 zmiany nastawy z menu wallboxa w trakcie ładowania (stan 300); trzy obniżki dały alarm ok. 10 s po ostatnim naciśnięciu. Alarmy bez żadnej zmiany nastawy też są (po włączeniu zasilania, 16–91 s później, zawsze już w trakcie ładowania). „Brak danych z DLB” nie jest potrzebny do wyjaśnienia logu — mechanizm: nastawa nie ogranicza prądu w trybie DLB, a ochrona porównuje z nią zmierzony prąd. Szczegóły: `LOGI_Tuya_wallbox_DLB_bfe26d.md`, sekcja 8.*
- **Zabezpieczenie do czasu wyjaśnienia:** limit prądu w samochodzie ustawiony na nastawę wallboxa — samochód bierze mniejszą z dwóch wartości.
- Istnieje wersja **DLB CONTROLLER V1.4 (2026‑1‑21)**; nasz egzemplarz ze stanowiska to V1.1 (2025‑7‑13).
- **Materiały instalatorów (wideo, 26.09) — zweryfikowane:** przy DLB SEt 18 i nastawie 16 auto dwufazowe pobiera 16,9 A; po obniżeniu nastawy do 9 A w trakcie ładowania wallbox przez kilka sekund ładuje dalej 16,6 A / 7,1 kW, potem komunikat przeciążenia, nastawa 8 A i stop. **Problem 2:** po pauzie DLB (< 6 A, czajnik) wallbox nie wznawia ładowania (5 min); rusza dopiero po przepięciu auta — sprzeczne z instrukcją DLB‑A1 („Recovery is automatic when headroom returns”). **Uszkodzona ładowarka pokładowa auta trójfazowego** — sprawa priorytetowa. Raport do producenta EN/ZH/PL: `istotne_casey/Karol/raport_do_producenta/` — **wysłany; producent zapowiedział przegląd firmware** (2026‑09‑27).
- **Instrukcja DLB‑A1 (Quick User Manual Rev. 20251109) obiecuje:** „each wall box is capped by its own requested current” i „Recovery is automatic when headroom returns” — oba punkty w praktyce niespełnione; to główna oś argumentacji wobec producenta.
- Kilka sesji kończyło się tak, że najpierw jedna faza spadała do zera, a sekundę później kończyła się sesja. Przyczyna nieznana.

### Łącze DLB ↔ wallbox i firmware — gdzie co się liczy *(2026‑09‑27)*

- **Przydział liczy DLB** `[F — instrukcja DLB‑A1 PL i Quick Manual EN, Rev. 20251109, w ../wallbox_DLB/]`. Mierzy prąd budynku przekładnikami, bierze 90% ustawionego limitu i odejmuje najwyższy prąd fazowy reszty budynku. Wynik wysyła wallboxowi radiem 433 MHz jako „docelową wartość prądu”, w pełnych amperach.
- **Łącze najpewniej działa w obie strony** `[Z]`. Instrukcja mówi: „each wall box is capped by its own requested current”. Żeby to spełnić, DLB musi znać żądany prąd każdego wallboxa. Za tym przemawiają też diody stanu połączenia na DLB.
- **Sygnał CP wystawia wyłącznie wallbox.** 20,2 A przy nastawie 15 i maksimum 16 (log z 26.09) znaczy, że żadna strona nie przycięła pozwolenia nawet do maksimum wallboxa `[F]`. Poprawkę problemu 1 najpewniej trzeba zrobić po stronie wallboxa `[Z]`. Chodzi o regułę: CP = min(nastawa, maksimum, wartość z DLB). To ostatnie urządzenie przed samochodem, więc tam ta reguła chroni niezależnie od tego, co przyśle DLB. Problem 2 (brak wznowienia) może leżeć po każdej stronie `[Z]`.
- **Moduł radiowy po stronie wallboxa** to mała płytka z anteną spiralną z zestawu DLB. Wpina się w 8‑pinowe złącze „RF433 Module” na płycie głównej wallboxa. To samo łącze szeregowe procesora obsługuje RS485, a wybiera się je suwakiem „RF433 ⟷ RS485” `[F — zdjęcia M3A1, ../WALLBOX_architektura/]`. Najpewniej to przezroczysty mostek „łącze szeregowe ↔ radio”, bez logiki przydziału `[Z]`. Instrukcja: moduł jest skonfigurowany fabrycznie, używać tylko tego dostarczonego z danym DLB.
- **Aktualizacja oprogramowania:**
  - DLB nie ma OTA `[F]`.
  - Na płytce kontrolera V1.4 jest złącze do programatora `[F — zdjęcie z 27.09; opisu pinów i typu procesora jeszcze nie odczytano]`.
  - Wallbox M3A1 ma na płycie głównej złącze programowania opisane „3V DIO CLK GND” (interfejs SWD, rdzeń ARM, procesor LQFP‑48 z nieczytelnym nadrukiem) i moduł Wi‑Fi Tuya `[F — zdjęcia]`.
  - Czy producent przewidział aktualizację procesora wallboxa przez Tuya — nieustalone.
  - Czy wallbox u klienta to ten sam model co M3A1 ze zdjęć — niepotwierdzone.
- **Rozbieżność instrukcji:** Quick Manual (EN) podaje „433 MHz albo RS485”, polska instrukcja — że RS485 „nie jest obecnie oferowane”.

### Wznowienie po przerwie — co pokazał log z 26.09 *(2026‑09‑28)*

- **Samo wznowiło się 2 z 12 przerw.** Oba razy auto dwufazowe (A), po alarmie przeciążenia, 4–5 s po powrocie wallboxa do stanu 200. Pozostałe przerwy trwały do przepięcia auta albo wyłączenia zasilania — od 28 s do 6,5 min `[F]`.
- **Auto trójfazowe (B) nie wznowiło ani razu**, po żadnym rodzaju przerwy. To ono jest na nagraniu problemu 2 i to ono miało uszkodzoną ładowarkę pokładową. Problem 2 może więc częściowo wynikać z zachowania auta `[Z]` — do sprawdzenia pauzą DLB z innym samochodem. Szczegóły: `LOGI_Tuya_wallbox_DLB_bfe26d.md`, sekcja 10.
- **Narastanie prądu po starcie:** auto B ok. 30 s do 13–16 A, auto A ok. 5 s do ok. 9 A `[F — log]`. Wznowienie krótsze niż ok. minuta daje autu B głównie rozruch.
- **Opóźnienie wznowienia po pauzie DLB:** według producenta (28.09) wallbox zatrzymuje ładowanie, gdy przydział spada poniżej 6 A. Od tej chwili biegnie stałe opóźnienie T; po jego upływie wznawia, gdy tylko prąd wystarczy. T jest więc minimalnym czasem pauzy i limitem najwyżej 60/T cykli na godzinę. Symulacja (28.09) wskazała przedział 3–5 min; decyzja Dawida: T = 5 min (okrągła wartość, najmniej cykli). W instrukcji i ulotce podać wprost „5 minut”. Analiza i dalszy rozwój DLB: `../DLB_R&D/zasoby_informacji/DLB_RD_baza_wiedzy.md`.

---

## Instalacja zasilająca — wymagania i przypadki z korespondencji

### Przewód PEN w obwodzie ładowania — zakaz normowy *(2026‑09‑29, sprawa Ł. Reszki)*

**IEC 60364‑7‑722:2018, pkt 722.312.2.1** (polskie wydanie: PN‑HD 60364‑7‑722): w układzie TN obwód zasilający punkt ładowania **nie może zawierać przewodu PEN**. `[F — norma; potwierdzone w opisie normy, zob. electrical-installation.org, rozdział EV charging]` Rozdział PEN na N i PE musi nastąpić przed tym obwodem, w instalacji stałej (rozdzielnica) — rzecz dla elektryka.

**Przejściówka z gniazda 4‑pinowego (3 fazy + PEN, instalacja TN‑C) na wtyk 5‑pinowy z mostkiem N–PE** — pytanie klienta, „na YouTube działa”:
- Ładowarka najpewniej ruszy: test obecności uziemienia widzi PE połączony z N i przechodzi. Ochrona jest iluzoryczna. `[Z — zgodne z przewodnikiem ..\AMPERE_POINT_instalacje_a_ladowanie_EV_przewodnik_v1, sekcja TN‑C; na Q nie sprawdzane]`
- **Przerwa w PEN** (instalacja, zacisk, styk gniazda lub wtyku przejściówki): obudowa ładowarki i karoseria samochodu, połączone z PE, dostają napięcie sieci przez włączone odbiorniki. **Wyłącznik różnicowoprądowy w ładowarce tego nie wykryje** — prąd odbiornika płynie przez jego przekładnik tam i z powrotem po L i N, bilansuje się, a dopiero za ładowarką, na mostku w przejściówce, przechodzi na PE i karoserię. Prąd rażenia człowieka dotykającego auta jest dla tego wyłącznika niewidoczny. `[Z — wywód z budowy układu, zgodny z przewodnikiem („najgroźniejsza wada instalacyjna”)]`
- W TN‑C z mostkiem za różnicówką nie da się też poprawnie zastosować RCD w instalacji — wyzwala przy każdym obciążeniu (przewodnik, sekcja TN‑C).

**Instrukcja serii Q** (`..\Q11_architektura\QSeries_Ampere_Point_manual_EN_CONTENT_REVIEW.docx` — **wersja robocza do przeglądu, nie wiadomo, czy tożsama z wysyłaną**): gniazdo „must be properly grounded”; obwód chroniony RCD typu A i zabezpieczeniem nadprądowym dobranym przez elektryka; podłączać tylko do instalacji „with protective earth, phase and neutral conductors correctly wired”; zakaz przedłużaczy (także przedłużaczy Type 2); gwarancja 24 miesiące na sam produkt, tylko z dowodem zakupu. Wyłączeń gwarancji z powodu niewłaściwej instalacji w tej wersji nie znalazłem.

---

## Stanowisko serwisowe — cechy, o których trzeba pamiętać przy testach

### Gniazdo siłowe G8 ma zmostkowaną jedną fazę na wszystkie trzy

Rozwiązanie służy do sprawdzania, czy ładowarka odbiera napięcie na wszystkich wejściach. **Nie nadaje się do testowania urządzeń trójfazowych** — prawdziwe napięcia międzyfazowe wynoszą tam zero, a obciążenie całego zestawu spoczywa na jednej fazie.

**Konsekwencja diagnostyczna:** wynik testu ładowarki trójfazowej na G8 nie rozstrzyga o poprawności zasilania. Urządzenie nie zgłosi błędu, bo każdy tor pomiarowy widzi wobec N poprawne 230 V — patrz sekcja o komunikacie Low Voltage. Do testów, które mają cokolwiek dowodzić w kwestii faz, używać gniazda rzeczywiście trójfazowego. *Uzupełnienie (2026‑10‑05, Dawid): dotyczy zjawisk zależnych od napięć międzyfazowych i obciążenia jednej fazy. **Tor pomiaru napięć ładowarki** (każdy kanał faza–N) G8 sprawdza tak samo jak prawdziwa sieć — poprawny odczyt i brak komunikatu na G8 oznaczają sprawny pomiar.*

### Pomiary oscyloskopem w obwodach sieciowych wyzwalają różnicówkę

*(zdarzenie 2026‑09‑08, gniazdo G8, rozdzielnica biurkowa + szafa 1. piętro, wyłącznik Q2B — Hager CDC240J 40 A / 30 mA)*

Podłączenie oscyloskopu i woltomierza jednocześnie do tego samego punktu pod napięciem spowodowało zadziałanie dwóch wyłączników różnicowoprądowych w kaskadzie.

**Mechanizm:** różnicówka nie reaguje na pobór prądu, tylko na prąd uciekający do ziemi. Masa oscyloskopu zasilanego z sieci albo połączonego z komputerem jest połączona z przewodem ochronnym. Wpięcie takiej masy w punkt pod napięciem tworzy drogę upływu do PE i zadziałanie następuje natychmiast.

**Wniosek praktyczny:** do pomiarów w obwodach sieciowych używać oscyloskopu z izolowanym wejściem albo zasilanego z akumulatora, bez połączenia z komputerem. Nie łączyć równolegle kilku przyrządów mających masę na PE.

**Reset wyłącznika po zadziałaniu:** dźwignia zatrzymuje się w położeniu pośrednim. Trzeba ją najpierw docisnąć całkowicie w dół, aż do zatrzasku, i dopiero wtedy podnieść. Jeśli nie chce się załączyć mimo prawidłowego skasowania i pustego obwodu — sprawdzić, czy nie zahacza o osłonę czołową, spróbować przycisku T, a przy dalszym oporze nie forsować, tylko wymienić aparat. Górne zaciski pozostają pod napięciem mimo wyłączenia.

---

## Pozostałe dokumenty z danymi

| Plik | Zawartość |
|---|---|
| `AMPERE_POINT_pomiary_bazowe_Q11_v1.md` / `.pdf` / `.xlsx` | pomiary bazowe Q11 wykonane dostępnym sprzętem |
| `AMPERE_POINT_rejestrator_zlacza_Q11_v2.md` / `.pdf` | rejestrator złącza międzypłytkowego, schemat zbiorczy |
| `AMPERE_POINT_rejestrator_Q11_schemat_*.png` | schematy: architektura, tor CT, tor CP, schemat pełny |
| `LOGI_Tuya_Marcin_harmonogram.md` | analiza logów Tuya, mechanizm `charge_now` vs `switch` |
| `LOGI_Tuya_timer_test_switch.md` | dowody, że `Switch : ON` z chmury uruchamia ładowanie; `switch` a `Work Mode` |
| `LOGI_Tuya_Novak_prad_6A.md` | harmonogram ustawiający 6 A zamiast nastawy |
| `LOGI_Tuya_wallbox_DLB_bfe26d.md` | wallbox z DLB u klienta: pełny log do 14:26, dekodowanie wyświetlacza DLB, prąd powyżej nastawy, 12 alarmów 400 i reakcja wallboxa (sekcja 8), raport do producenta (sekcja 9) |
| `casey/Daniel_Romanek/przebieg_sprawy.md` | przycisk otwierania klapki Tesli „nie działa” u klienta, u nas działa; częstotliwości EU/USA |
| `casey/Robert_Gloch/przebieg_sprawy.md` | „High Voltage Reminder” 000/582/495 i 602/231/228 — testy na obu gniazdach bez błędu; usterki nie stwierdzono, wada N niepotwierdzona |
| `istotne_casey/Karol/raport_do_producenta/` | raport do producenta EN/ZH/PL (PDF + źródła LaTeX + wycinki zdjęć): dwa problemy wallbox + DLB‑A1, log Tuya jako dowód, pytania do producenta |
| `../DLB_R&D/zasoby_informacji/DLB_RD_baza_wiedzy.md` | rozwój DLB: budowa systemu, wady, ustalenia z producentem, opóźnienie wznowienia, plan badań, korespondencja |
| `../wallbox_DLB/` | instrukcje DLB‑A1 (PL i Quick Manual EN, Rev. 20251109), ulotka, schematy instalacji DLB |
| `../WALLBOX_architektura/AI_PAMIEC_wallbox_M3A1.md` + `WALLBOX_M3A1_schemat.pdf` | budowa wallboxa M3A1: płyta główna, złącze SWD, złącze modułu RF433, przełącznik RF433/RS485, progi komunikatów z instrukcji |
| `ZASADY_maile_do_klientow.md` | zasady redagowania korespondencji serwisowej |
| `SPRAWY_W_TOKU.md` | rejestr otwartych spraw: stan, na co czekamy, gdzie pliki (od 2026‑09‑28) |
| `casey/Dawid_Kaczmarek/generuj_kosztorys.py` + `kosztorys.json` | **generator kosztorysu naprawy na papierze firmowym** (te same funkcje i wygląd co protokoły z `repair-protocols`; PDF przez Word) — do kolejnych kosztorysów: skopiować JSON, zmienić dane, uruchomić pythonem z venv `repair-protocols` |
| `casey/Lukasz_Reszka/przebieg_sprawy.md` | klient chce przejściówkę z gniazda 4‑pinowego (PEN) na 5‑pinowe z mostkiem N–PE; odpowiedź pod kątem odpowiedzialności |
| `istotne_casey/Marcin_Krawiec/przebieg_sprawy.md` | integracja ładowarki z HA 2025.3 przez tuyaextend-amperepoint: przebieg, ustalenia, błędy maila z 25.09, zrzuty korespondencji |
| `AMPERE_POINT_diagnostyka_zdalna_instalacja_v1.pdf` | metodyka diagnozy zdalnej, testy T1–T8, objawy O‑1…O‑16 |
| `AMPERE_POINT_schematy_instalacji_dom_przemysl_v1.pdf` | schematy instalacji domowej i przemysłowej z ładowarką |
| `cennik_czesci_Q_2026-07-14.md` | ceny części serwisowych serii Q |
| `../AMPERE_POINT_porownanie_ladowarek_v2.html` | katalog usterek U‑001…U‑029 |

### Odpowiedzi fabryki Q11 (Corey, WeChat) na pytania z dokumentacji dla Qiao *(2026-09-30)*

Źródło: zrzuty `SHELLY\DevKit\Qiao\konwersacja\odp_pyt_dokumentacja\` (30.09.2026, ok. 10:44); analiza `SHELLY\DevKit\Qiao\odpowiedzi_fabryki_2026-09-30.md/.pdf`. Numeracja = pytania z `AMPERE_POINT_Q11_Shelly_module_test_documentation_EN` v1.

- [F] **Procesor Q11: STM32F030RCT6, 256 kB flash** (Cortex-M0, LQFP64). Zgodne z pomiarem nóżek zasilania (1, 13, 19, 32, 48, 64), masy (12, 18, 31, 47, 63) i portu PA2/PA3 = nóżki 16/17 (USART2). Wcześniejsze „rodzina STM32F103/GD32” do poprawy w dokumentach.
- [F] Ramka informacji o produkcie (0x01): „głównie PID i wersja oprogramowania, szczegóły w opisie protokołu”. Wartości nieznane; punkt 23 po starcie 30.09 = „V1”.
- [F] Moduł używa tylko VCC, GND, RXD, TXD — potwierdzone przez fabrykę.
- [F] Punkt 1 (licznik całkowity): fabryka: „zgłaszany po zakończeniu ładowania”. Nasz log 29.09: co 90 s w stanie „ładuje”, wartość 0. Oba mogą być prawdą; koniec ładowania nieobserwowany.
- [F] Punkt 17 (limit energii): zgłaszany i przyjmowany, gdy ustawiony tryb „do limitu energii” — zgodne z 29.09.
- [Z] Punkt 23 (wersja): fabryka: „odświeżany co 1,5 min”. **Sprzeczne z logiem**: w ~15 h ani razu, raz po włączeniu zasilania (30.09). Co 90 s przychodzi punkt 1 — prawdopodobnie fabryka pomyliła numery. Do dopytania.
- [F] Punkty 33 i 25: „nieużywane”. Punkt 25 przyszedł raz (25.09 11:23, wartość 0, w jednej ramce z wyłączeniem ładowania) — bez znaczenia użytkowego; energii sesji z niego nie będzie.
- [F] Punkt 8 = zawsze phase_c. Definicja Q21 z eksportu („charger_events”) nieaktualna dla Q11.
- [—] Pytanie 7 (przypisanie numer → nazwa wyliczeń): odpowiedź „bez wymagań co do kolejności” — nie na temat. Do dopytania z tabelą.
- [—] Pytanie 8 (stan Wi-Fi 0x03 i reset sieci z menu): „na razie nieużywane”. Niejasne: czy ikona sieci na wyświetlaczu zależy od 0x03 i co wysyła reset z menu. Do dopytania; test C5/D9.
- [F] Aktualizacja sterownika po łączu: „program rozruchowy można przerwać; po przerwaniu trzeba powtórzyć aktualizację” → sterownik ma bootloader do aktualizacji po łączu, przerwanie nie psuje płyty. Format pliku i udostępnienie — bez odpowiedzi.
- [F] Czas (0x1C) używany do ładowania planowanego (okno godzin). Zachowanie bez ważnego czasu — bez odpowiedzi.
- [F] Milczenie modułu nie zmienia zachowania sterownika — zgodne z obserwacją.
