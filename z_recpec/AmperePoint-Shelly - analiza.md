## Jak czytać ten dokument

Ten dokument porządkuje ustalenia z rozmów AmperePoint z przedstawicielami Shelly
i uzupełnia je o kontekst rynkowy, regulacyjny i techniczny. Jest pisany dla kogoś, kto nie
siedzi w temacie ładowarek, modułów Wi-Fi ani przepisów unijnych — każde pojęcie branżowe
tłumaczę przy pierwszym użyciu, a na końcu jest słowniczek.

Rozdzieliłem trzy rodzaje treści i oznaczam je konsekwentnie, żeby było widać, co jest czyje:

- **To, co padło na spotkaniu** — wypowiedzi podane kursywą, wcięte. Oddają to, co zostało
 powiedziane; gdy zdanie zostało przerwane albo urwane w pół myśli, urywa się także tutaj.
- **Fakty zewnętrzne** — dane z raportów spółek, dokumentacji technicznej i aktów prawnych.
 Każdy ma wskazane źródło w tekście i w spisie na końcu. Sprawdziłem je we wrześniu 2026;
 przepisy i liczby się zmieniają, więc przy decyzjach wartych pieniądze warto je odświeżyć.
- **Moja interpretacja** — wyraźnie zapowiedziana („moim zdaniem”, „z tego wynika”, „warto
 zauważyć”). Nie chcę, żeby wnioski wyglądały na ustalenia ze spotkania.

Dwa zastrzeżenia do samych wypowiedzi. Po pierwsze, **przypisuję je stronom rozmowy —
AmperePoint albo Shelly — a nie konkretnym osobom**, bo po każdej stronie zabierało głos
więcej niż jedna osoba. Po drugie, kilka nazw własnych i liczb padło w sposób, który nie
pozwala ich pewnie ustalić; w takich miejscach zaznaczam niepewność zamiast zgadywać.

### Streszczenie dla niecierpliwych

1. **AmperePoint sprzedaje ładowarki do aut elektrycznych, które „są smart” dzięki cudzemu
 modułowi** — kawałkowi elektroniki wielkości pudełka zapałek, który wkłada się w płytkę
 ładowarki i który odpowiada za Wi-Fi, aplikację w telefonie i chmurę. Ten moduł jest od
 chińskiej firmy Tuya.
2. **Problem nie polega na tym, że moduł jest słaby, tylko że nie jest wasz.** Każda nowa
 funkcja wymaga zgody i czasu Tuya, dane idą przez ich chmurę, a aplikacja jest ich.
 Kategoria „ładowarki” jest dla Tuya marginalna, więc nikt tam jej nie dopieszcza.
3. **Shelly proponuje wymianę tego modułu na swój** — fizycznie ten sam rozmiar i ten sam
 układ nóżek, więc fabryka nie musi przeprojektowywać ładowarki. Zmienia się „mózg
 łączności” i chmura, do której ładowarka się melduje.
4. **Nowy moduł to ESP32-C3** — układ, który ma około dwukrotnie szybszy procesor i dwa razy
 więcej pamięci programu niż obecny moduł Tuya. To jest ten „zapas na przyszłość”, o który
 AmperePoint dopytywał.
5. **Powód pilności to przepisy — ale z ważnym zastrzeżeniem.** Unijne rozporządzenie AFIR
 wymaga obsługi standardu ISO 15118 w nowo instalowanych punktach ładowania (2026 i 2027),
 przy czym **wiąże operatorów punktów publicznie dostępnych**, a nie producentów sprzętu
 sprzedawanego klientom prywatnym. Bezwarunkowo obowiązują natomiast od sierpnia 2025
 wymagania cyberbezpieczeństwa dla urządzeń radiowych — te dotyczą każdej ładowarki z Wi-Fi.
6. **Regulacje kosztują.** AmperePoint szacuje, że pełne przygotowanie sprzętowe podniosłoby
 koszt produkcji o 70 dolarów, co na półce oznacza około 400 złotych więcej i, ich zdaniem,
 trzykrotny spadek sprzedaży. Dlatego wybierają drogę „tania elektronika z dużym zapasem
 możliwości” zamiast „drogi sprzęt na zapas”.
7. **Dla Shelly to mały biznes, dla AmperePoint kluczowy.** Shelly zrobiło w 2025 roku
 149,7 mln euro przychodu i rośnie 40 % rocznie na gniazdkach, przekaźnikach i licznikach.
 Ładowarki to dla nich nowa, mała kategoria. Ta asymetria jest głównym ryzykiem współpracy
 i AmperePoint mówi o niej wprost.
8. **Shelly kupuje sobie kategorię, AmperePoint kupuje niezależność i czas.** Shelly dostaje
 firmę, która zna ładowarki i zrobi za nich rozpoznanie rynku; AmperePoint dostaje platformę,
 na której sam decyduje o funkcjach, oraz europejską chmurę i markę.
9. **Najbliższe kroki są konkretne:** AmperePoint spisuje listę funkcji („dziś jeden do
 jednego”, „za chwilę”, „na jutro”), Shelly dostarcza ładowarkę TopAC, przekładnik prądowy
 i dev kit, a potem odbywa się rozmowa z Borisem, szefem R&D Shelly.
10. **Otwarte pozostaje kilka rzeczy:** brak modułu z kartą SIM w ofercie Shelly, sposób
 obsługi OCPP lokalnie, koszt lokalnego inżyniera w Chinach, warunki handlowe i ryzyko,
 że Shelly zostanie kiedyś przez kogoś kupione.


## Trzy firmy i jedna zależność

Żeby cokolwiek z tego spotkania miało sens, trzeba najpierw zobaczyć, kto jest kim i kto od
kogo zależy. Występują trzy firmy i jedna relacja, która uwiera.

### AmperePoint — ten, kto sprzedaje

AmperePoint to polska marka ładowarek do samochodów elektrycznych i hybryd typu plug-in.
Flagowy produkt to **przenośna ładowarka Q11**: 11 kW mocy, wtyczka Typu 2 do auta, wtyk
przemysłowy (tzw. CEE) do gniazda siłowego, obudowa aluminiowa, stopień ochrony IP66,
regulacja prądu od 6 do 16 amperów, wyświetlacz i łączność Wi-Fi. W polskich sklepach
internetowych kosztuje mniej więcej od 1000 do 1400 złotych, zależnie od wersji i dodanych
przejściówek (źródło: sklep amperepoint.pl i porównywarki cen, wrzesień 2026).

Trzy rzeczy z tego opisu wracają w rozmowie raz za razem:

- **Ładowarka jest przenośna, nie przykręcana do ściany.** To nie jest przypadek ani brak
 ambicji — to świadoma strategia, opisana szerzej w rozdziale o regulacjach.
- **Nie wymaga elektryka.** Klient sam wpina ją do gniazda siłowego, które już ma.
- **„Smart” w tym produkcie to Wi-Fi i aplikacja** — czyli dokładnie ta warstwa, o której
 całe spotkanie jest.

Skala, o której mówi AmperePoint, to około dwudziestu tysięcy klientów końcowych, z czego
mniej więcej połowa korzysta z funkcji smart. Produkcja idzie w trzech różnych
fabrykach w Chinach, każda odpowiada za inną półkę cenową. Tylko jedna z tych
fabryk ma mocny własny zespół elektroników; dwie pozostałe, gdy trzeba cokolwiek zmienić
w elektronice, posiłkują się firmami trzecimi.

> Dwie inne wywodzą się z prostszych sprzętów i są fajne pod kątem montażu (…), ale jak
> trzeba cokolwiek zmienić w elektronice, to sami posiłkują się usługami trzecimi. Bo
> w swoich zespołach na tej roli nie mają dobrych elektroników.

### Tuya — ten, od kogo dziś zależy „smart”

Tuya to chińska firma notowana na amerykańskiej giełdzie, która sprzedaje coś, co w branży
nazywa się **IoT PaaS** — „internet rzeczy jako usługa”. W praktyce działa to tak: producent
dowolnego urządzenia (żarówki, czajnika, rolety, ładowarki) kupuje od Tuya mały moduł Wi-Fi,
wkłada go do swojego produktu, konfiguruje na ich platformie zestaw funkcji — i dostaje
gotową aplikację na telefon, konto w chmurze, parowanie urządzenia, aktualizacje. Nie musi
mieć ani jednego programisty od chmury.

To jest genialne rozwiązanie dla kogoś, kto chce szybko dołożyć „smart” do produktu — i tego
właśnie AmperePoint użył. Cena tej wygody: **wszystko, co dalej, dzieje się na warunkach
Tuya**.

Skala Tuya, dla porównania: w pierwszym kwartale 2025 roku firma miała 74,7 mln dolarów
przychodu przy marży brutto 48,5 %, a na ich platformie zarejestrowanych było ponad
1,4 miliona deweloperów urządzeń i oprogramowania (źródło: raport kwartalny Tuya Inc.).
To jest fabryka „smartowania” wszystkiego, w której pojedyncza kategoria produktowa —
zwłaszcza tak mała jak ładowarki — jest ziarnkiem piasku.

### Shelly (Allterco) — ten, kto proponuje wyjście

Shelly to bułgarska grupa Allterco, notowana na giełdzie we Frankfurcie (od niedawna
w indeksie SDAX). Robi przekaźniki, gniazdka, liczniki energii i sterowniki, które są
w świecie automatyki domowej znane głównie z tego, że **działają lokalnie** — to znaczy nie
przestają działać, gdy zniknie internet — i mają otwarte, udokumentowane interfejsy.

Liczby z ich raportu za 2025 rok: przychód 149,7 mln euro, wzrost o 40,3 % rok do roku; kraje
niemieckojęzyczne (Niemcy, Austria, Szwajcaria — w branży skrótowo „DACH”) to 62,0 mln euro,
reszta Europy 74,0 mln euro przy wzroście 51 %; ponad 2,7 miliona użytkowników chmury Shelly
i obecność w ponad 100 krajach. Na 2026 rok prognozują 195–205 mln euro przychodu (źródło:
komunikaty wynikowe Allterco / Shelly Group SE).

Na spotkaniu pada zdanie, które warto zestawić z tymi liczbami — mówi je strona Shelly
o własnej pozycji w kategorii ładowarek:

> Z tym, że u nas nie mamy doświadczeń z tą kategorią za długich, za fajnych, więc raczej to
> wy będziecie definiować u nas tą kategorię.

To jest kluczowe dla zrozumienia układu sił. Shelly jest duże i rośnie, ale **w ładowarkach
jest nowicjuszem**. Ma jeden własny produkt w tej kategorii — przenośną ładowarkę **TopAC**
(model EVE01-11R, 11 kW, wpinana w gniazdo CEE, z aplikacją i dynamicznym zarządzaniem mocą),
zrobioną z chińską fabryką i sprzedawaną przez własne kanały.

### Relacja, która uwiera

Zależność wygląda tak: **klient końcowy — aplikacja Tuya — chmura Tuya — moduł Tuya w
ładowarce AmperePoint**. AmperePoint jest właścicielem marki, sprzedaży, serwisu
i odpowiedzialności — ale nie jest właścicielem ani jednego elementu tego łańcucha poza samym
urządzeniem. Na spotkaniu ujęto to bez ogródek:

> (…) musicie wyjść z takiego, jakby tu i wchodząc w biznes, tu jesteście trochę
> niewolnikiem, bo macie jedną ścieżkę rozwoju plus ograniczony software.

Propozycja Shelly jest prosta do opisania i trudna do wykonania: **wymienić jeden klocek
w środku urządzenia**, tak żeby cała reszta — obudowa, elektronika mocy, proces produkcji —
została bez zmian, a zmieniło się to, kto decyduje o funkcjach i gdzie płyną dane.


## Co naprawdę siedzi w środku ładowarki

Ta część jest czysto wyjaśniająca. Bez niej rozmowa o „module”, „pinoucie” i „data pointach”
brzmi jak zaklęcia, a z nią cała reszta dokumentu układa się w całość.

### Ładowarka AC nie jest ładowarką

Pierwsza rzecz, która zaskakuje ludzi spoza branży: **domowa „ładowarka” do auta
elektrycznego niczego nie ładuje**. Prostownik — czyli układ, który zamienia prąd
przemienny z gniazdka na prąd stały, jakim karmi się akumulator — siedzi w samochodzie.
Urządzenie wiszące na ścianie albo leżące w bagażniku to w istocie **inteligentny wyłącznik
z zabezpieczeniami i licznikiem**. Jego zadania to:

- podać albo odciąć napięcie z sieci do gniazda auta,
- **powiedzieć samochodowi, ile prądu wolno mu pobrać**,
- pilnować bezpieczeństwa (przegrzanie, prąd upływowy, poprawne uziemienie),
- policzyć zużytą energię,
- i — dopiero na samym końcu — być „smart”, czyli dać się obsłużyć z telefonu.

Branżowo mówi się na to **EVSE** (*Electric Vehicle Supply Equipment*, sprzęt zasilający
pojazd elektryczny), a na sposób ładowania prądem przemiennym z takim sprzętem — **Mode 3**.
Słowo **wallbox** oznacza wersję przykręcaną do ściany; AmperePoint sprzedaje głównie wersję
przenośną, która robi dokładnie to samo, tylko wpina się do gniazda siłowego.

### Jak ładowarka „rozmawia” z autem

To jest zaskakująco prymitywne i warto to wiedzieć, bo cała dyskusja o przyszłych regulacjach
polega na tym, że ten prymityw ma zostać zastąpiony.

W kablu między ładowarką a autem jest cienka żyłka sygnałowa nazywana **Control Pilot**.
Ładowarka wysyła nią prostokątny sygnał i **szerokością impulsu** koduje jedną jedyną
informację: „możesz pobierać maksymalnie tyle a tyle amperów”. Ta technika nazywa się
**PWM** (*Pulse Width Modulation*, modulacja szerokości impulsu). Auto odpowiada,
zmieniając napięcie na tej samej żyłce, co ładowarka odczytuje jako „jestem podłączony”,
„jestem gotowy”, „potrzebuję wentylacji”.

I to wszystko. Żadnych nazw, numerów, tożsamości, żadnych negocjacji. Dlatego ładowarka nie
wie, jakie auto do niej podpięto, a auto nie wie, do czyjej ładowarki się podłączyło.

Nowy standard, o którym mowa na spotkaniu, **ISO 15118**, dokłada do tej samej żyłki
prawdziwą transmisję cyfrową — sygnał danych „nakłada się” na sygnał sterujący techniką
zwaną **PLC** (*Power Line Communication*, komunikacja po przewodzie). Wtedy auto i ładowarka
mogą wymieniać certyfikaty, uzgadniać harmonogram, rozliczać się automatycznie. O tym jest
osobny rozdział — na razie wystarczy, że **PWM to jedna liczba, a PLC to rozmowa**.

### Co jest na płytce

Uproszczony spis części „smart” ładowarki AC, od mocy do inteligencji:

| Element | Po co jest |
| --- | --- |
| Stycznik albo przekaźnik mocy | Fizycznie załącza i odcina prąd do auta |
| Zabezpieczenia | Wykrywanie prądu upływowego (w tym składowej stałej), kontrola temperatury, ochrona przeciwprzepięciowa |
| Pomiar energii | Układ mierzący napięcie i prąd — stąd biorą się kilowatogodziny w aplikacji |
| **MCU produktu** | Mikrokontroler, czyli mały procesor, który steruje całością: czyta przyciski, obsługuje wyświetlacz, generuje sygnał PWM, pilnuje bezpieczeństwa |
| **Moduł łączności** | Osobny kawałek elektroniki z własnym procesorem i radiem Wi-Fi/Bluetooth — to on gada z chmurą i telefonem |
| Wyświetlacz, przyciski, dioda | Interfejs dla człowieka stojącego przy urządzeniu |

Dwa ostatnie wiersze są sednem całego spotkania. **MCU produktu to mózg ładowarki. Moduł
łączności to jej usta i uszy do świata zewnętrznego.** I to właśnie te usta i uszy są dziś
wynajęte od Tuya.

### Jak te dwa układy się dogadują

MCU produktu i moduł łączności są połączone kilkoma przewodami na płytce i rozmawiają
prostym łączem szeregowym zwanym **UART** — to ten sam rodzaj połączenia, co stary port
COM w komputerze. Wymieniają krótkie komunikaty w formacie narzuconym przez dostawcę modułu.

W świecie Tuya każda informacja, którą urządzenie chce wystawić na zewnątrz, nazywa się
**data point** (punkt danych) — na przykład „stan: ładuje / nie ładuje”, „prąd zadany:
10 A”, „energia w tej sesji: 7,4 kWh”, „temperatura: 41 °C”. Producent definiuje listę takich
punktów na platformie Tuya i od tego momentu aplikacja, chmura i automatyzacje operują
właśnie na nich.

To ma dwie konsekwencje, które wracają w rozmowie:

- **Lista data pointów jest praktycznie specyfikacją produktu od strony software'u.** Kto ją
 ma, ten wie, co urządzenie potrafi. Dlatego Shelly mówi, że mając tę listę i pinout,
 odtworzy funkcjonalność „jeden do jednego”.
- **Wszystko, czego na tej liście nie ma, nie istnieje dla aplikacji.** Dołożenie nowego
 punktu to zmiana po stronie platformy, a nie tylko w waszym kodzie.

### Chmura, aplikacja i aktualizacje

Ostatnie ogniwo: moduł łączy się przez domowe Wi-Fi z chmurą dostawcy, tam melduje swój stan
(„ping”), stamtąd dostaje polecenia z aplikacji i aktualizacje oprogramowania
(**OTA**, *over-the-air* — aktualizacja „po powietrzu”, bez kabla i bez serwisanta).

Trzy rzeczy, które z tego wynikają i o których mówi się na spotkaniu:

- **Konto klienta jest w chmurze dostawcy**, nie u producenta ładowarki.
- **Tempo rozwoju funkcji jest tempem dostawcy**, bo aplikacja jest jego.
- **Koszt utrzymania tej chmury jest realny** — każde urządzenie na świecie melduje się co
 kilka–kilkanaście sekund. Właśnie ten koszt jest sednem rachunku, który AmperePoint robi
 Tuya w rozdziale o ich modelu biznesowym.


## Dlaczego wymiana modułu to decyzja strategiczna, a nie zakupowa

Gdyby chodziło tylko o kawałek elektroniki za kilka dolarów, nikt nie zwoływałby spotkania na
godzinę z hakiem. Zależność od dostawcy modułu ma trzy warstwy i każda boli inaczej.

### Warstwa pierwsza: funkcje

Na platformie takiej jak Tuya dostajesz to, co platforma przewidziała dla twojej kategorii
produktu. Jeśli kategoria jest duża — oświetlenie, gniazdka — przewidziano dużo. Jeśli mała,
dostajesz zestaw podstawowy i czekasz. AmperePoint opisuje to tak:

> No to oni mają taką funkcjonalność, jak nazwijmy to, najbardziej bazowej. No i rozchodzi
> się teraz o to, co będzie się działo dla nas w przyszłości.

Problem nie jest dzisiejszy, tylko jutrzejszy: **nie da się obiecać klientowi biznesowemu
funkcji, której dostarczenie zależy od priorytetów firmy, dla której jesteś ziarnkiem piasku.**

### Warstwa druga: doświadczenie klienta i wsparcie

Tu pada najmocniejsze zdanie całego wątku. Mowa o partnerze technologicznym, który dorzuca
nowinki, ale nie interesuje go, co się dzieje na końcu, u użytkownika:

> Więc dla nas partner, który coś robi w temacie, ale nie jest na tyle zainteresowany, nie
> jest w ogóle zainteresowanym doświadczeniem końcowym, tylko dobra, rzucimy trochę nowości,
> innowacji, żeby nie być tyle za rynkiem. Nie jest przyszłościowo z perspektywy rozwoju
> marki.

I konsekwencja praktyczna, wcześniej w tej samej rozmowie: gdy produkt nie działa tak, jak
powinien, **rachunek za to płaci wsparcie techniczne AmperePoint**, a nie dostawca platformy:

> (…) ale ja wiem jak to będzie działało, że to nie będzie ten eksperyment dla użytkowników
> i my będziemy musieli później na supporcie ulegać wszystkie konsekwencje związane z tym, że
> ten produkt nie jest taki jaki powinien być (…)

To jest asymetria, która definiuje całą sprawę: **zyski ze skali zostają u dostawcy platformy,
koszty niedoróbek spadają na producenta urządzenia.**

### Warstwa trzecia: dostęp do segmentów rynku

Najbardziej wymierna strata. AmperePoint nie może dziś obsłużyć klienta firmowego, bo nie ma
jak rozliczyć energii na osobę:

> (…) często mamy takie lead pod tytułem, że ktoś potrzebuje 20–30 wallboxów, posłużyć całą
> firmę, ale potrzebuje to w jakiś sposób wpiąć do ich systemu biurowego, żeby było
> rozliczenie prądu na osobę. Czyli ten cały segment rynku na dzień dzisiejszy nie mamy jak
> go dotknąć, bo życie tego na Tuya (…) jest niemożliwe po prostu.

W tłumaczeniu na polski: przychodzi zapytanie na dwadzieścia–trzydzieści ładowarek dla firmy,
z wymaganiem, żeby zużycie prądu rozliczało się per pracownik i wpinało w ich system.
To jest **billing** — rozliczanie zużycia na konkretnego użytkownika. Na obecnej platformie
nie da się tego zrobić sensownie, więc te zapytania przepadają.

Co więcej, próba obejścia problemu na siłę może się zemścić na relacji z klientem:

> Tak, no nawet gdyby próbowałeś to (…) jak będzie się rozparowywało, to można sobie spalić
> mosty, że tak powiem, sprzedając takie rozwiązanie (…)

„Rozparowywanie” to sytuacja, w której urządzenie traci powiązanie z kontem i przestaje się
meldować — dla klienta wygląda to jak awaria, a dla sprzedawcy kończy się reklamacją.

### Co AmperePoint chce kupić naprawdę

Nie moduł. **Kontrolę nad tym, co urządzenie będzie potrafiło za rok, i pewność, że nikt tego
nie zablokuje.** Najlepiej widać to w tym, jak formułują wymaganie wobec elektroniki:

> (…) myślimy nad tym, żeby elektronika, którą dołożymy już dzisiaj, miała potencjał na
> obsługę wszystkiego, co będzie się pojawiało (…), to żeby tak naprawdę ten chip i cała ta
> obsługa jego pozostała niezmienna. Czyli tą warstwę, żeby trochę wyprzedzała dzisiejsze
> zapotrzebowania sprzętu.

To zdanie jest w gruncie rzeczy całą specyfikacją projektu: **włóż dziś układ z zapasem, żeby
przez kilka lat nie trzeba było ruszać sprzętu ani procesu w fabryce, a nowe funkcje dawały
się dokładać zdalnie.** Rozdział o technologii pokazuje, czy proponowany moduł ten warunek
spełnia.


## Gdzie stoi AmperePoint — pozycja rynkowa rozłożona na czynniki

### Półka cenowa: „tuż za najlepszymi, daleko przed tanizną”

Strategia cenowa została opisana wprost i jest to klasyczne pozycjonowanie w górnej
części średniej półki:

> Jedno jest takie, że żeby być tą najwyższą, najdroższą średnią półką, czyli tam gdzie
> realnie można zbudować marże (…), no to musimy zawsze oferować coś więcej, czyli musimy być
> tuż za tymi, którzy [są najdrożsi]. Później mamy rozwiązane go-e, NextBlue i tak dalej, ale
> to są sprzęty, które są bliżej 4 tysięcy (…)

Mechanizm, który za tym stoi, jest prosty: na najniższej półce marża jest symboliczna, bo
konkuruje się wyłącznie ceną. Na najwyższej trzeba mieć albo markę premium, albo funkcje,
których nikt inny nie ma — jedno i drugie kosztuje lata. Miejsce **tuż pod** liderem jest
najlepsze pod względem stosunku marży do nakładów: klient porównuje cię z drogim sprzętem,
a ty masz od niego niższą cenę i podobną listę funkcji.

Przykład liczbowy na podstawie tego, co padło na spotkaniu, i cen z rynku: jeśli austriacki go-e
kosztuje około 3500–4000 zł, a ładowarka Q11 AmperePoint 1000–1400 zł, to przestrzeń między
nimi jest ogromna. **Każda funkcja dołożona bez wzrostu kosztu produkcji przesuwa produkt
w stronę tej wyższej półki, nie ruszając ceny.** Stąd cała logika spotkania: nowe możliwości
mają przyjść z oprogramowania, nie z droższego sprzętu.

### Przenośność jako strategia, nie kompromis

To jest najciekawszy element pozycjonowania i łatwo go przeoczyć. Ładowarka przenośna zamiast
przykręcanej daje AmperePoint trzy przewagi naraz:

**Pierwsza: nie potrzeba elektryka.** Klient wpina urządzenie w gniazdo siłowe, które już ma
w garażu. Nie ma umawiania instalatora, nie ma kosztu 500–1000 zł za montaż, nie ma tygodnia
czekania. To jest „niski próg wejścia”, o którym mówi AmperePoint.

**Druga: nie ma odpowiedzialności za montaż i demontaż.** Tu pada konkretny przykład z rynku:

> Green Cell ze swoimi ładowarkami, bo oni sprzedają bez przewodów zasilających. Oto na
> przykład zamroziło parę sprzętów i ludzie się chwalili na grupę jak zmusić Green Cell do
> pokrycia kosztów elektryka do montażu i montażu ponownego. Bo to jest z winy Green Cell,
> jakby aktualizacja się nie przebiegła (…)

Mechanizm: jeśli urządzenie jest zainstalowane na stałe przez uprawnionego elektryka, to przy
awarii — zwłaszcza zawinionej przez producenta, np. nieudanej aktualizacji oprogramowania —
klient może żądać zwrotu kosztów demontażu i ponownego montażu. Przy sprzęcie wpinanym do
gniazdka ten problem znika, bo klient sam go wypina. **Przenośność to polisa ubezpieczeniowa
na wady oprogramowania.**

**Trzecia: mniejszy rygor regulacyjny.** AmperePoint twierdzi, że część nowych wymagań
dotyczy sprzętu montowanego na stałe, a urządzenie przenośne wypada z połowy z nich. To jest ich ocena prawna, nie moja — ale kierunek myślenia jest
udokumentowany: klasyfikacja produktu jest świadomym narzędziem, tak samo jak w przytoczonej
w rozmowie historii z paczkomatami, gdzie chodziło o to, żeby urządzenie formalnie nie było
„maszyną”.

### Trzy fabryki, trzy półki, jedna słabość

Produkcja w trzech fabrykach daje elastyczność cenową, ale ma cenę: **kompetencje elektroniczne
są tylko w jednej z nich**. To dlatego w całym spotkaniu tak dużo miejsca zajmuje pytanie nie
o technologię, lecz o **ludzi po stronie Shelly w Chinach**:

> (…) wiem, że macie biuro w Shenzhen, czy do takiego projektu można u Was nająć PM-a
> lokalnego (…) Dalej najwygodniej byłoby pewnie gdyby Chińczyk gadał z Chińczykiem u siebie
> i zapłacić za to fee (…)

PM to *project manager*, kierownik projektu. Sens tego fragmentu: AmperePoint nie chce
kupować samej technologii, chce kupić **kogoś, kto dopilnuje fabryki na miejscu, w tej samej
strefie czasowej i w tym samym języku**. Argument za tym jest bardzo praktyczny:

> (…) jednak jak ktoś tam, kto jest w tej samej strefie czasowej i fizycznie jest 30 minut
> taksówką od fabryki (…) to jest całkowicie inny proces (…)

### Klient biznesowy — segment, do którego nie ma dziś drzwi

AmperePoint przyznaje, że historycznie sprzedawał konsumentom, ale klient firmowy pojawia się
coraz częściej, w tym duże projekty:

> Teraz zaczęliśmy kilka projektów. Mamy na tapecie dużą sieć handlową, która ma ponad 700
> hal sprzedażowych.

Bariera jest programowa, nie sprzętowa: brakuje rozliczania energii na użytkownika, obsługi
kart, integracji z systemami klienta. Dokładnie to ma odblokować zmiana platformy.


## Model Tuya: dlaczego partner, który zarabia centy, nie dopieści twojej kategorii

### Jak zarabia się na „smartowaniu” cudzych produktów

Firma taka jak Tuya ma dwa strumienie przychodu i oba są cienkie w przeliczeniu na sztukę:

- **Sprzedaż modułu** — fizyczny kawałek elektroniki wkładany do produktu klienta. Marża
 liczona w centach.
- **Usługa chmurowa** — obsługa urządzenia przez cały jego cykl życia: konto, aplikacja,
 aktualizacje, serwery.

Model działa wyłącznie przy gigantycznych wolumenach. I tu jest sedno problemu AmperePoint,
wyłożone na spotkaniu bardzo obrazowo:

> Ładowarki to jest, porównując to do żarówek czy jakichś tam innych przedłużaczy smart, to
> są jakieś tam śmieszne wolumeny (…) To półroczny wolumen to jest pewnie tygodniowy wolumen
> żarówek (…) i zarabiają tyle samo, bo wkładają, powiedzmy, ten sam chip.

Zwróć uwagę na ostatni człon, bo on jest kluczowy: **dostawca platformy zarabia tyle samo na
module w żarówce co na module w ładowarce**, bo to ten sam moduł. Ale żarówek sprzedaje się
tysiąckrotnie więcej. Z punktu widzenia menedżera produktu w Tuya każda godzina włożona
w rozwój kategorii „ładowarki” jest godziną odebraną kategorii, która robi tysiąc razy
większy obrót. To nie jest złośliwość ani lekceważenie — **to jest zwykła matematyka
alokacji zasobów** i dlatego nie da się tego przeczekać ani wynegocjować.

### Rachunek, który AmperePoint robi Tuya

Na spotkaniu pada dokładniejsze wyliczenie, warte przytoczenia w całości, bo pokazuje sposób
myślenia AmperePoint o partnerach:

> Właśnie mówię, że oni zarabiają po kilkadziesiąt centów teoretycznie na finalną marżę per
> urządzenie. No, a to jest subsydiowany też biznes (…) to, że zarobią, nie wiem, 92 centy na
> czipie, to pamiętajcie, że oni mają cały koszt infrastruktury, z każdym urządzeniem dochodzi
> im ileś tam pingów i to jest kilka miliardów pingów na minutę. Więc koszt infrastruktury
> jest znacząco wyższy niż te, co raportują jako spółka giełdowa.

Rozłóżmy to na czynniki, bo dla laika „pingi” brzmią niegroźnie.

**Ping** to krótki komunikat „żyję”, który urządzenie wysyła do chmury, żeby aplikacja
wiedziała, że jest online. Przy jednym urządzeniu to nic. Ale urządzenie wysyła go bez
przerwy, przez lata, niezależnie od tego, czy ktokolwiek korzysta z aplikacji. Policzmy
prosto: sto milionów urządzeń meldujących się raz na minutę to sto milionów zapytań na
minutę, czyli ponad 1,6 miliona na sekundę — i to są serwery, łącza i prąd, za które ktoś
płaci co miesiąc, podczas gdy przychód z modułu wpłynął raz, przy produkcji.

**Co z tego jest zweryfikowane, a co nie.** Sprawdziłem dane publiczne: w pierwszym kwartale
2025 roku Tuya wykazała 74,7 mln dolarów przychodu przy marży brutto 48,5 % i ponad
1,4 mln zarejestrowanych deweloperów (raporty spółki). To potwierdza skalę i to, że biznes
jest rentowny na poziomie marży brutto. **Tezy o subsydiach rządowych i o tym, że realny
koszt infrastruktury jest wyższy, niż wynika z raportów, nie weryfikowałem** — traktuj ją
jako opinię AmperePoint, nie jako fakt. Dla decyzji, o którą chodzi, to zresztą drugorzędne:
nawet przy najbardziej życzliwej interpretacji finansów Tuya wniosek operacyjny się nie
zmienia — **kategoria ładowarek jest tam za mała, żeby ktokolwiek się nią zajął**.

### „Marka, z którą pracujecie, to nie jest marka”

W dalszej części rozmowy strona Shelly stawia diagnozę, która jest może najcelniejszym zdaniem
całego spotkania:

> Ale dla was też myślę, że ta marka z którą teraz pracujecie to nie jest marka, to jest
> produkt, ale to nie jest marka.

Sens: Tuya jest **dostawcą komponentu**, a nie marką, pod którą można się schować. Klient
końcowy nie kupuje ładowarki dlatego, że jest „na Tuya” — w najlepszym razie tego nie
zauważa, w najgorszym kojarzy z tanią chińską elektroniką. Odpowiedź AmperePoint pokazuje,
o co im w tym wszystkim naprawdę chodzi:

> My głównie budujemy markę i zastanawiamy się jakie produkty przytulić pod markę, ale to
> jest tak naprawdę budowanie marki (…)

To jest ta sama myśl, co w porównaniu, którego AmperePoint używa wcześniej w rozmowie — do
producentów akcesoriów certyfikowanych przez Apple:

> W przypadku pro-userów wasza marka jest bardzo silna, więc to przyklejenie się (…)
> najlepszym porównaniem jest bycie jako producent akcesoriów w Apple Store. Więc jak Apple
> ci daje certified (…) to nagle możesz za tą samą silikonową obudowę płacić 40 złotych
> (…)

Mechanizm jest realny i dobrze opisany w marketingu: **cudza marka, do której wolno ci się
oficjalnie odwołać, przenosi część swojego zaufania na twój produkt i pozwala podnieść cenę
bez zmiany samego produktu.** Tuya takiej wartości nie daje, bo jest niewidzialna dla klienta
końcowego. Shelly — w środowisku instalatorów i entuzjastów automatyki domowej — daje.


## Kim jest Shelly i co właściwie sprzedaje AmperePointowi

### Firma w liczbach

| Wskaźnik (2025 r.) | Wartość |
| --- | --- |
| Przychód grupy | 149,7 mln euro (+40,3 % rok do roku) |
| Kraje niemieckojęzyczne (DACH) | 62,0 mln euro (+27,0 %) |
| Pozostała Europa | 74,0 mln euro (+51,0 %) |
| Użytkownicy chmury Shelly | ponad 2,7 mln |
| Obecność | ponad 100 krajów |
| Sieć instalatorów | ok. 5 300 (wzrost blisko sześciokrotny) |
| Prognoza na 2026 r. | 195–205 mln euro przychodu, 47–52 mln euro EBIT |

Źródło: komunikaty wynikowe Allterco / Shelly Group SE. Spółka jest notowana na giełdzie
we Frankfurcie i wchodzi do indeksu SDAX.

Te liczby warto zestawić z tym, co padło na spotkaniu. AmperePoint mówi o „50 % przychodów
z Niemiec” — w rzeczywistości DACH to około 41 % przychodu grupy, a Shelly
potwierdza kierunek („zdecydowanie”). Pada też liczba „3 miliony użytkowników”,
przy raportowanych 2,7 mln. **Rząd wielkości się zgadza i to wystarczy do wniosków** — ale
przy negocjacjach warto operować liczbami z raportu, nie z pamięci.

### Czym Shelly różni się od Tuya

To jest różnica, która decyduje o całej wartości tej oferty dla AmperePoint.

**Tuya jest platformą dla producentów.** Klient końcowy jej nie zna. Produkt jest „smart”
przez aplikację Tuya (albo jej białą etykietę), a producent jest jednym z setek tysięcy.

**Shelly jest marką konsumencką i instalatorską, która przy okazji otworzyła swoją platformę
dla producentów.** Ta platforma nazywa się **Shelly X** i jest tym, co Shelly sprzedaje
AmperePointowi. Na spotkaniu przedstawia się ją tak:

> Jasne, to może odpowiem, bo akurat za Shelly X jestem ja odpowiedzialny (…) jeżeli chodzi
> o rozwiązania, które sobie wymyśliliście, od początku do końca jest to możliwe, dodatkowo
> dla fabryki również to nie będzie problem, ponieważ mamy taki cały gotowy moduł (…)

Publicznie dostępny opis platformy (x.shelly.com) potwierdza to, co mówiono przy stole:
konto OEM, kreator produktu, wybór modułu, tworzenie oprogramowania bez pisania kodu
(*no-code*) albo z niewielką ilością kodu przez wtyczkę do edytora Visual Studio Code
(*low-code*), oraz możliwość „oprowizjonowania” gotowych urządzeń Shelly własną konfiguracją
i marką.

### Trzy argumenty, którymi Shelly gra

**Chmura europejska.** W rozmowie pada to jako pierwsza z korzyści:

> (…) z tego całego wachlarza korzyści wchodząc w współpracę z Shelly, to pamiętajcie, że to
> jest chmura europejska. Ja wiem, że Tuya mówi, że ma w Amsterdamie Azure (…)

Dla klienta biznesowego — zwłaszcza sieci handlowej, firmy farmaceutycznej czy instytucji —
to bywa warunek wstępny przetargu, a nie miły dodatek.

**Działanie lokalne w pierwszej kolejności.** Shelly opisuje swoją filozofię jako
*local first*:

> (…) Shelly jest local first, czyli [macie] skrypty i całość (…)

Po ludzku: urządzenie ma działać i dawać się sterować **bez internetu**, z lokalnej sieci,
a chmura jest dodatkiem. Dla ładowarki to ma konkretne znaczenie — sterowanie mocą,
współpraca z domowym systemem energetycznym i rozliczenia nie mogą padać, gdy padnie łącze.

**Możliwość pisania własnych skryptów.** Urządzenia Shelly pozwalają uruchamiać na sobie
niewielkie programy w języku JavaScript. To znaczy, że część logiki — harmonogramy, reakcje
na cenę prądu, reguły bezpieczeństwa — można dołożyć **bez zmiany firmware'u i bez pytania
kogokolwiek o zgodę**. AmperePoint wie o tej możliwości i wspomina o niej już na początku.

### Czego Shelly nie ma i sam to przyznaje

Uczciwość tej rozmowy polega na tym, że Shelly nie udaje eksperta od ładowarek:

> Z tym, że u nas nie mamy doświadczeń z tą kategorią za długich, za fajnych, więc raczej to
> wy będziecie definiować u nas tą kategorię. Ona nie jest łatwa z perspektywy wsparcia.
> Ilość kontaktu z klientem jaką trzeba mieć.

Mają jeden produkt w kategorii — przenośną ładowarkę **TopAC** (EVE01-11R), 11 kW, wpinaną
w gniazdo CEE, z dynamicznym zarządzaniem obciążeniem i aplikacją — zrobioną z chińską
fabryką, sprzedawaną przez własnych handlowców. Skala jest na razie skromna
i świeża:

> Wiesz, to jest kilka miesięcy doświadczeń, trudno by wam było pokazać jakąś tam skalę, bo
> ta skala największa jest dzisiaj (…) głównie ta Skandynawia czy tam Finlandia (…) wiem, że
> jest jakiś duży deal w Danii.

> Tak, na magazynie mamy aktualnie 3,5 tysiąca Portable (…)

**Co z tego wynika dla AmperePoint.** Po pierwsze: nie kupujecie gotowej ekspertyzy od
ładowarek — kupujecie platformę, a ekspertyzę wnosicie sami. Po drugie: to jest pozycja
negocjacyjna. Firma, która chce zbudować kategorię i nie ma w niej doświadczenia, potrzebuje
partnera referencyjnego bardziej, niż ten partner potrzebuje kolejnego dostawcy modułów.
Strona Shelly mówi to niemal wprost: *„to wy będziecie definiować u nas tą kategorię”*.


## Krajobraz rynku: kto z kim i o co gra

### Trzy piętra rynku ładowania

Dla porządku, bo te słowa mieszają się w potocznym użyciu:

- **Ładowanie prądem przemiennym (AC)** — domowe i firmowe, moce 3,7–22 kW, prostownik
 w aucie. Tu gra AmperePoint. Sprzęt jest relatywnie tani, a różnicują go funkcje, jakość
 wykonania i oprogramowanie.
- **Ładowanie prądem stałym (DC)** — stacje przy trasach, od 50 kW w górę, prostownik
 w stacji. Zupełnie inna liga kosztowa (dziesiątki–setki tysięcy złotych za stanowisko)
 i inna branża. W rozmowie przewija się polski producent takich stacji, Ekoenergetyka.
- **Infrastruktura publiczna i operatorzy** — firmy, które stawiają i rozliczają stacje.
 To one od lat żyją protokołem OCPP i wymaganiami regulacyjnymi, o których mowa dalej.

### Konkurencja w segmencie AmperePoint

Z rozmowy i z rynku wyłania się taki obraz:

| Kto | Pozycja | Znaczenie dla AmperePoint |
| --- | --- | --- |
| go-e (Austria) | Wallbox premium, ok. 3,5–4 tys. zł | Wyznacza górną granicę półki; punkt odniesienia dla funkcji |
| „NextBlue” *(nazwa do potwierdzenia)* | Ta sama półka co go-e | j.w. |
| Green Cell (Polska) | Popularna marka konsumencka | Przykład, jak nie robić: awaria oprogramowania przy sprzęcie montowanym na stałe = koszty elektryka |
| Shelly TopAC | Przenośna, 11 kW, kilka miesięcy na rynku | Jednocześnie partner i najbliższy „sąsiad” produktowy |
| Marki chińskie bez marki | Najniższa półka | Konkurują wyłącznie ceną, AmperePoint świadomie nie schodzi na ten poziom |

Warto zauważyć rzecz, która przewija się między wierszami: **TopAC to produkt
bardzo podobny do Q11** — przenośny, 11 kW, z aplikacją. Shelly proponuje wręcz, żeby zrobić
z niego punkt odniesienia:

> (…) na podstawie tej naszej ładowarki TopAC jakbyście mogli zrobić taką analizę gap (…)
> kopiujemy sobie listę funkcjonalności z TopAC, pomyślimy, co jeszcze brakuje (…)

**Analiza gap** (dosłownie „analiza luki”) to porównanie dwóch produktów funkcja po funkcji
i wypisanie różnic. Rzecz sensowna technicznie, ale trzeba mieć świadomość, że **partner
i konkurent to tutaj ta sama firma**. To nie jest zarzut — to po prostu fakt, który warto
mieć z tyłu głowy przy ustalaniu, co się komu pokazuje.

### Kanały sprzedaży — dwa różne światy

W dalszej części rozmowy wychodzi rzecz istotna dla wspólnego biznesu: obie firmy sprzedają przez
inne kanały.

> Ale to też wynika z tego, że mamy zupełnie innego dystrybutora, w innym kanale funkcjonuje.

Shelly sprzedaje przez hurtownie elektryczne i sieć instalatorów (ok. 5 300 partnerów wg
raportu za 2025 r.), AmperePoint — przez kanał konsumencki i e-commerce. Dla współpracy to
jest **zaleta, nie problem**: te same produkty mogą trafić do dwóch rozłącznych grup klientów
bez kanibalizacji. Dlatego pojawia się pomysł osobnych numerów EAN:

> Może nasz produkt będzie u was zupełnie innym EAN-em, czyli będziecie go inaczej
> pozycjonować. Albo stworzyć EAN osobny dla dystrybucji (…)

**EAN** to ten kreskowy numer towaru ze sklepowej etykiety. Osobny numer dla każdego kanału
pozwala prowadzić różne ceny i różne opisy tego samego fizycznie produktu, nie wywołując
wojny cenowej między kanałami — bo porównywarki i klienci widzą po prostu dwa różne towary.

### Dokąd idzie ten rynek

Trzy siły, które w ciągu najbliższych lat zdecydują o tym, czyj produkt będzie się sprzedawał:

**Po pierwsze — energia, nie motoryzacja.** Ładowarka przestaje być gadżetem do auta, a staje
się elementem domowego systemu energetycznego: fotowoltaika, magazyn energii, taryfy
dynamiczne (cena prądu zmienna co godzinę), sterowanie mocą. Widać to w tym, że
Shelly z marszu proponuje dorzucenie przekładnika prądowego i bilansu energetycznego:

> Tą naszą ładowarkę TopAC od nas z magazynu, CT-ki jedną naszą 120-amperową, bo od razu
> wydaje mi się, że dobrze by było, gdybyśmy porozmawiali o bundlowaniu tego (…) to, że
> bilans energetyczny (…) samozwracalna się ładowarka będzie super też marketingowo działała

**CT** (*current transformer*, przekładnik prądowy) to obejma zakładana na przewód
w rozdzielnicy, która mierzy przepływający prąd. Dzięki niej system wie, ile dom aktualnie
zużywa i ile zostało zapasu — i może dostosować moc ładowania, żeby nie wybiło bezpiecznika.
„Samozwracalna się ładowarka” to argument sprzedażowy: urządzenie, które ładuje auto
w najtańszych godzinach albo z nadwyżki z paneli, zwraca koszt zakupu.

**Po drugie — regulacje.** Cały następny rozdział.

**Po trzecie — klient firmowy.** Rozliczenia, karty, raporty, integracje. Segment, w którym
marże są wyższe i w którym AmperePoint dziś nie może startować.


## Regulacje: co się zmienia, kiedy i dlaczego to napędza całą sprawę

To jest rozdział, bez którego spotkanie wygląda jak dyskusja o wygodzie. Z nim widać, że
istnieje zegar.

### AFIR — unijne rozporządzenie o infrastrukturze paliw alternatywnych

**Co to jest.** Rozporządzenie (UE) 2023/1804, w skrócie **AFIR** (*Alternative Fuels
Infrastructure Regulation*), obowiązuje od kwietnia 2024 r. bezpośrednio we wszystkich krajach
Unii — nie wymaga wdrożenia ustawą krajową. Ujednolica infrastrukturę ładowania: dostępność
stacji, sposób płatności, przejrzystość cen i **standardy komunikacji**.

**Kogo wiąże.** To jest najważniejsze rozróżnienie w całym rozdziale i łatwo je przeoczyć:
**AFIR nakłada obowiązki na operatorów punktów ładowania publicznie dostępnych** — takich,
z których może skorzystać nieokreślony krąg osób. Punkt prywatny, używany przez jedno
gospodarstwo domowe albo zamknięty krąg użytkowników, jest poza zakresem tego rozporządzenia.

**Co z niego wynika dla sprzętu.** Kluczowe dwie daty:

- **8 stycznia 2026** — nowo instalowane, publicznie dostępne punkty ładowania mają
 obsługiwać **EN ISO 15118-2**.
- **1 stycznia 2027** — nowo instalowane punkty ładowania prądem przemiennym (Mode 3)
 mają obsługiwać **EN ISO 15118-20**.

Do tego doszły przepisy szczegółowe: akt delegowany (UE) 2025/656 domknął standardy
techniczne, a rozporządzenie wykonawcze (UE) 2025/655 — obowiązki przekazywania danych
(ceny, dostępność, status) przez otwarte interfejsy.

**Skąd bierze się wątek „prywatny”.** Nie z AFIR, tylko z **EPBD** — dyrektywy
o charakterystyce energetycznej budynków (UE) 2024/1275. To ona wymaga, żeby w nowych
budynkach i budynkach po głębokiej renowacji, mających więcej niż trzy miejsca postojowe,
powstały punkty ładowania zdolne do sterowanego ładowania. Adresatem tego obowiązku jest
**inwestor albo właściciel budynku**, a nie producent urządzenia wprowadzanego do obrotu.
Te dwa porządki bywają mylone, bo mówią o tym samym sprzęcie — ale nakładają obowiązki na
zupełnie różne podmioty.

**Uwaga o zakresie, ważna dla AmperePoint.** Data 2027 jest tą, o której mówi
AmperePoint:

> (…) to, co będzie istotne z perspektywy regulacji prawnych, teoretycznie od nowego roku
> (…), że wallboxy z całego montażu powinny być tam już zgodne z AFIR i tam narzucone jest
> trochę technologii, które mogą być wdrożone lub nie, ale już taka sugestia, że sprzęty mają
> iść w tym kierunku (…) Czyli na przykład OCPP wersji 2.0 (…)

Trzeba to jednak czytać ostrożniej, niż zabrzmiało przy stole. AFIR **nie jest przepisem
o wprowadzaniu wyrobów do obrotu** — nie mówi producentowi, czego nie wolno mu sprzedać.
Mówi operatorowi punktu publicznie dostępnego, co ten punkt musi umieć. Dla firmy, która
sprzedaje przenośne ładowarki klientom prywatnym, oznacza to, że **data 2027 nie jest
automatycznym wyrokiem na produkt bez modemu PLC**.

Wraca ona natomiast dwoma innymi drogami i o nich warto pamiętać: przy sprzedaży do punktów
publicznie dostępnych (a tam właśnie leżą kontrakty B2B, o które chodzi) oraz przy dostawach
do budynków objętych EPBD. Otwarte pozostaje pytanie o klasyfikację samego urządzenia —
czy przenośna ładowarka z wtykiem jest sprzętem Mode 3, czy Mode 2 — bo cytowane wyżej
terminy odnoszą się do punktów Mode 3. **To jest pytanie do jednostki certyfikującej i warto
je zadać na piśmie.**

### ISO 15118 — „rozmowa” zamiast jednej liczby

Standard, który zastępuje prymitywne sygnalizowanie prądu (opisane wcześniej PWM) prawdziwą
transmisją danych między autem a ładowarką, prowadzoną po tym samym przewodzie techniką PLC.
Co to daje:

- **Plug & Charge** — wtykasz kabel i to wszystko; auto przedstawia się certyfikatem,
 ładowarka je rozpoznaje, rozliczenie dzieje się samo. Żadnych kart ani aplikacji.
- **Negocjację harmonogramu** — auto może powiedzieć „mam być naładowany na 8 rano”,
 a system wybiera najtańsze godziny.
- **Ładowanie dwukierunkowe** — auto oddaje prąd do domu albo do sieci.

Dokładnie tak opisuje to AmperePoint na spotkaniu, i to jest najlepszy fragment techniczny
całej rozmowy:

> To służy po to, żeby był cały proces negocjacji, że auto negocjuje z ładowarką, jaki chce
> prąd, że auto może poinformować (…) że o 8 rano być naładowane. I na przykład wtedy może to
> przekazać informacji do EMS-a i EMS już sobie wymyśli, jak to zrobić najtaniej (…)

> Ten protokół też pozwala na komunikację wzajemną a propos ładowania dwukierunkowego. Czyli,
> żeby EMS mógł sterować falownikiem w samochodzie, ile ma prądu oddawać w danym momencie,
> jakie jest zapotrzebowanie domu.

**EMS** (*Energy Management System*) to system zarządzania energią w budynku — układ, który
patrzy na produkcję z paneli, stan magazynu energii, cenę prądu i zapotrzebowanie, i decyduje,
co w danej chwili włączyć.

**Rzecz kluczowa i często mylona:** ISO 15118 to **nie jest** funkcja oprogramowania, którą
da się dograć zdalnie. Wymaga **modemu PLC** — dodatkowego układu scalonego w ładowarce — plus
obsługi certyfikatów. Dlatego pada zdanie:

> (…) to jest problem, o którym jeszcze nie wiemy, jak sobie poradzimy i traktujemy go
> jako…

**To jest zupełnie inna decyzja niż wymiana modułu Wi-Fi** i żadna platforma chmurowa jej nie
załatwi. Wrócę do tego w rozdziale o ograniczeniach.

### OCPP — język między ładowarką a systemem operatora

**Co to jest.** *Open Charge Point Protocol*, otwarty standard komunikacji między stacją
ładowania a systemem zarządzania stacjami (**CSMS**). Ładowarka melduje status, rozpoczyna
i kończy sesje, wysyła odczyty licznika, przyjmuje konfigurację i limity mocy.

**Wersje.** W użyciu są 1.6 i 2.0.1. Ta druga jest przeprojektowana od podstaw: lepsze
bezpieczeństwo, rozbudowane zarządzanie urządzeniem, obsługa ISO 15118 i sterowania mocą
z udziałem systemów energetycznych. Realia rynku: **około 90 % zainstalowanych ładowarek
z OCPP nadal działa na wersji 1.6** (źródło: opracowania branżowe ChargeLab, Codibly).

**Dlaczego to ważne dla AmperePoint.** Bo otwiera segment firmowy — jeśli ładowarka mówi
OCPP, to wpina się w dowolny system rozliczeniowy klienta i można ją sprzedać do biurowca,
sieci handlowej czy floty.

**Haczyk, który AmperePoint zauważa i który jest najbardziej technicznie dojrzałym momentem
rozmowy:**

> Czyli to jest coś, co ten protokół musiałby być na przykład nie na zasadzie chmury
> i wirtualnego obsłużenia, bo to też tak można zrobić, że mamy [ładowarkę], łączy się (…)
> w chmurze i symulujemy ten protokół (…), to te [wymagania] powinny być zaszyte lokalnie.
> To jest bardzo prosty protokół, nie ma jakiegoś szaleństwa.

Po ludzku: OCPP można obsłużyć na dwa sposoby. **Uczciwy** — ładowarka sama mówi OCPP,
bezpośrednio do systemu klienta. **Na skróty** — ładowarka gada po swojemu z chmurą
producenta, a chmura udaje OCPP wobec systemu klienta. To drugie działa do pierwszej awarii
internetu i do pierwszego audytu. Dla klienta korporacyjnego, który wymaga protokołu
z powodów zgodności, to bywa dyskwalifikujące.

Ciekawostka: sam AmperePoint wcześniej rozważał wariant pośredni — dołożyć obok modułu Tuya
drugi, prosty moduł na układzie ESP z lokalnym API, i zbudować OCPP przez „wirtualizację
w chmurze”. Wybór Shelly jest wyjściem z tego kompromisu.

### Cyberbezpieczeństwo urządzeń radiowych (RED)

Każde urządzenie z Wi-Fi jest w Unii **sprzętem radiowym** i podlega dyrektywie RED. Od
**1 sierpnia 2025** obowiązują dodatkowe wymagania dotyczące cyberbezpieczeństwa,
wprowadzone rozporządzeniem delegowanym (UE) 2022/30, ze zharmonizowanymi normami serii
**EN 18031**: ochrona sieci (18031-1), ochrona danych osobowych i prywatności (18031-2),
ochrona przed oszustwami finansowymi (18031-3).

W praktyce oznacza to: bezpieczne uruchamianie urządzenia, kontrola aktualizacji, brak
domyślnych haseł, szyfrowana komunikacja, udokumentowana obsługa podatności. To jest
dokładnie ta warstwa, którą dostarcza dostawca modułu — i dlatego na spotkaniu pada pytanie:

> Z ciekawości wydajecie RED-a do tego? Osobnego? (…) Nie, bo czy bezpieczeństwo to jest RED?
> Dobrze myślę? No, to jest certyfikat.

**To pytanie jest warte tysięcy złotych** i zasługuje na pisemną odpowiedź od Shelly: co
dokładnie pokrywa ich dokumentacja modułu, a co musi zbadać AmperePoint dla całego
urządzenia. Odpowiedź na spotkaniu była wymijająca — rozmowa zeszła na inne opcje
współpracy.

### Rozporządzenie maszynowe — dygresja, która pokazuje mechanizm

W rozmowie pada anegdota o automatyce bram (Nice, CAME) i o paczkomatach InPostu. Chodzi w niej o to, że zmiana przepisów potrafi z dnia na dzień
uczynić sprzedawany od lat produkt niezgodnym z prawem, a producenci szukają wtedy
przeklasyfikowania produktu, żeby uciec spod rygoru.

Fakty w tle: **rozporządzenie (UE) 2023/1230** zastępuje dyrektywę maszynową 2006/42/WE
i jest obowiązkowe **od 20 stycznia 2027**; nie ma okresu, w którym obowiązują oba akty
naraz. Nowe przepisy obejmują też cyfryzację i cyberbezpieczeństwo maszyn.

Dlaczego to jest w tym dokumencie: bo **ta sama logika dotyczy ładowarek**. Klasyfikacja
produktu (przenośny czy stały, maszyna czy nie) jest narzędziem strategicznym i AmperePoint
używa go świadomie. Ryzyko jest jednak symetryczne — regulator może tę furtkę zamknąć
i wtedy cała przewaga znika w jednym akcie prawnym.


## Ekonomia zgodności: dlaczego 70 dolarów zabija produkt

Najważniejsza liczba całego spotkania nie dotyczy technologii, tylko tego, co się z nią
dzieje po drodze na półkę.

> (…) wzrost kosztu produktu, [przez który] by nam wsiadła cała sprzedaż. Produkt by na
> dzień dzisiejszy dużo więcej nie oferował (…), a koszt produkcji rośnie o 70 dolarów, czyli
> przyłożenie mniej więcej na 400 [zł] netto na klienta końcowego. Czyli od razu tak naprawdę
> sprzedaż jakiegoś tam produktu to pewnie byłoby trzeba podzielić przez trzy.

### Jak 70 dolarów zamienia się w 400 złotych

Laik zapyta: skoro część kosztuje 70 dolarów (ok. 280 zł), to dlaczego na półce ma być
o 400 zł drożej? Bo **każdy złoty dołożony w fabryce jest po drodze mnożony**. Uproszczony,
poglądowy rachunek — liczby są przykładowe, nie padły na spotkaniu, ale rzędy wielkości są
typowe dla elektroniki konsumenckiej sprowadzanej z Chin:

| Etap | Co się dzieje | Kwota |
| --- | --- | --- |
| Koszt materiałowy w fabryce | Dodatkowy modem PLC, pamięć, układy zabezpieczeń | +70 USD ≈ +280 zł |
| Transport, cło, ubezpieczenie | Kilka–kilkanaście procent | +15–30 zł |
| Marża producenta (AmperePoint) | Musi zostać procentowo podobna, żeby biznes się spinał | +60–90 zł |
| Marża kanału sprzedaży | Sklep, marketplace, dystrybutor | +50–80 zł |
| Podatek VAT | 23 % od wszystkiego powyżej | +90–110 zł |
| **Efekt na półce** | | **około +400 zł** |

To jest ta „dźwignia”, o której mówi AmperePoint. **Koszt w fabryce mnoży się mniej więcej
przez 1,4–1,5 razy, zanim dotrze do ceny detalicznej brutto.**

### Dlaczego +400 zł oznacza sprzedaż podzieloną przez trzy

Tu działa **elastyczność cenowa popytu** — im droższy produkt, tym mniej sztuk się sprzedaje,
ale nie liniowo. W segmencie, w którym ładowarka kosztuje 1000–1400 zł, dołożenie 400 zł to
wzrost ceny o **30–40 %**. Produkt przeskakuje z półki „impulsowy zakup do auta” na półkę
„poważna inwestycja, przemyślę to”, i trafia w okolice cen konkurentów premium — tyle że bez
ich marki.

Najgorsze jest to, co AmperePoint mówi w tym samym zdaniu: **klient za te 400 zł nie
dostałby nic, co by dziś zauważył**. Modem do standardu, który zacznie mieć znaczenie za rok
czy dwa, jest niewidzialny w momencie zakupu. Trzykrotny spadek sprzedaży jest oczywiście
szacunkiem, a nie pomiarem — ale kierunek jest niewątpliwy i każdy, kto sprzedawał sprzęt
w tej półce, go rozpozna.

### Wniosek, który z tego wyciągają — i on jest słuszny

Skoro nie można dziś zapłacić za sprzęt na zapas, a jutro trzeba będzie mieć funkcje,
to jedyne sensowne wyjście to: **włożyć dziś możliwie pojemną, ale tanią elektronikę
i dokładać funkcje oprogramowaniem**.

To jest dokładnie ta myśl z rozdziału o zależności: *„żeby elektronika, którą dołożymy już
dzisiaj, miała potencjał na obsługę wszystkiego, co będzie się pojawiało”*.
Różnica kosztu między modułem Wi-Fi słabszym a mocniejszym to **dolary, nie dziesiątki
dolarów** — i to jest inwestycja, która się broni, bo nie zmienia ceny na półce.

I stąd, w prostej linii, bierze się pytanie zadane Shelly pod koniec pierwszego spotkania:

> Jest takie pytanie, czy ten chip, który wybierzemy, nie dzisiaj, tylko czy w przyszłości na
> nim jest tyle miejsca i tyle (…) I czy ten procesor to pociągnie. Jak nie, to czy później
> na tym samym pinoucie macie coś mocniejszego, które to pozwoli (…)

To jest, moim zdaniem, najlepiej postawione pytanie całej rozmowy — i wrócę do niego przy
porównaniu modułów, bo odpowiedź jest pomyślna.

### Drugi sposób na ten sam problem: przeklasyfikowanie produktu

AmperePoint ma jeszcze jedno narzędzie, opisane wcześniej: skoro część wymagań dotyczy
sprzętu montowanego na stałe, to produkt przenośny wypada z ich części.

> Lepiej wchodzą te nowe dyrektywy teraz, które dotyczą sprzętów głównie stałego montażu.
> A my teraz powiemy, że nasz [sprzęt] jest przenośny. Można go zawiesić. No to jest sprzęt
> przenośny i połowa wymagań odchodzi, która wchodzi od 1 stycznia.

**Ostrzeżenie, które trzeba tu postawić wprost:** to jest skuteczna taktyka, ale krucha.
Opiera się na interpretacji przepisu, którą może zmienić jedna nowelizacja, jedno stanowisko
Komisji albo jedna kontrola. Dobrze mieć ją w zestawie narzędzi; źle budować na niej jedyny
plan. Warto mieć tę interpretację potwierdzoną pisemnie przez jednostkę notyfikowaną, zanim
zostanie wpisana w strategię produktową na 2027 rok.


## „Nowy chip”: co dokładnie ma powstać

### Najpierw sprostowanie, bo to częste nieporozumienie

Kiedy na spotkaniu pada „ten chip”, łatwo pomyśleć, że ktoś zamierza **zaprojektować nowy
układ scalony**. Nic takiego się nie dzieje. Projektowanie prawdziwego chipa to koszt
liczony w milionach dolarów i lata pracy — nikt tego nie robi dla ładowarki.

To, co ma powstać, to trzy rzeczy, w tej kolejności:

1. **Wymiana gotowego modułu** — zamiast kupowanego dziś modułu Tuya do ładowarki trafia
 gotowy, produkowany seryjnie moduł Shelly.
2. **Nowe oprogramowanie na tym module** — czyli definicja produktu: jakie funkcje, jakie
 dane, jak sterowane, jak wyglądają w aplikacji.
3. **Nowy tor chmurowy** — urządzenie melduje się do chmury Shelly, a nie Tuya; klient
 dostaje inną aplikację.

Fizycznie zmienia się **jeden element w spisie części** i to wszystko. Cała trudność jest
w punktach 2 i 3 oraz w procesie w fabryce.

### Co siedzi w takim module

Moduł to mała płytka (wielkości mniej więcej dwóch znaczków pocztowych) z:

- **układem SoC** (*System on Chip*) — procesorem, radiem Wi-Fi/Bluetooth i pamięcią RAM
 w jednej kostce,
- **pamięcią flash** — gdzie mieszka program (firmware) i ustawienia,
- **anteną** wytrawioną na płytce,
- **metalowym ekranem** tłumiącym zakłócenia,
- **rządkiem metalizowanych wcięć na krawędzi** — to są „nóżki”, którymi moduł przylutowuje
 się do płytki ładowarki.

Rozkład i znaczenie tych nóżek nazywa się **pinoutem**. Jeśli dwa moduły mają ten sam pinout
i te same wymiary, to jeden można wlutować w miejsce drugiego **bez przeprojektowania płytki
ładowarki** — a to oznacza brak zmian w narzędziach, obudowie i procesie montażu w fabryce.
Cała oferta Shelly opiera się właśnie na tym:

> Dodatkowo, jeżeli mamy specyfikację odnośnie modułu na Tuya, który jest, to i pinoutu,
> i całego schematu, jesteśmy w stanie odzwierciedlić jeden do jednego i skomponować się do
> tego, co już dzisiaj macie (…) po prostu w fabryce podmieniają pudełeczko z Tuya na Shelly
> i dalej już robią na Shelly.

Pytanie AmperePoint dotyczy właśnie tej fizycznej zgodności — i odpowiedź jest twierdząca:

> Czyli zmieniacie też (…) sam ten chip ma inaczej nie tylko kolejność pinów, ale też
> w jakiej fizycznej… — Jednego fizycznie wygląda jak tu. Wyjmiemy i włożymy.

### Porównanie: co jest dziś, co byłoby jutro

| Cecha | Moduł Tuya WBR3 (dziś) | Moduł Shelly X (propozycja) |
| --- | --- | --- |
| Układ | BK7231N (Beken) | ESP32-C3 (Espressif) |
| Rdzeń | 32-bitowy, do ok. 120 MHz | 32-bitowy RISC-V, do 160 MHz |
| Pamięć programu (flash) | 2 MB | typowo 4 MB |
| Pamięć robocza (RAM) | 256 kB | ok. 400 kB |
| Radio | Wi-Fi 2,4 GHz + Bluetooth LE | Wi-Fi 2,4 GHz + Bluetooth LE |
| Wyprowadzenia | 2 rzędy po 8 pinów, raster 2 mm | 4–8 użytecznych wejść/wyjść, zależnie od wersji (X0–X4) |
| Zakres temperatur | katalogowy modułu | od −40 °C do +105 °C |
| Kto kontroluje oprogramowanie | Tuya | wy, na platformie Shelly |
| Chmura | Tuya | Shelly (Europa) |
| Praca bez internetu | ograniczona | zakładana od początku (*local first*) |

Źródła parametrów: karta katalogowa modułu WBR3 z portalu deweloperskiego Tuya oraz strony
modułów Shelly X0–X4 na x.shelly.com. **Dokładne wartości pamięci w konkretnym wariancie
modułu Shelly trzeba potwierdzić w karcie katalogowej przy zamówieniu** — podaję typowe dla
tego układu.

### Odpowiedź na najlepsze pytanie spotkania

AmperePoint pytał, czy na wybranym układzie będzie „tyle miejsca i tyle [mocy]” na przyszłe
funkcje, a jeśli nie — czy na tym samym pinoucie jest coś mocniejszego.
Z zestawienia wynika, że:

- **Mocy jest około jedną trzecią więcej** (160 MHz wobec 120 MHz), a przy nowoczesnym
 rdzeniu realna różnica bywa większa niż sama liczba megaherców.
- **Miejsca na program jest dwa razy więcej** (4 MB wobec 2 MB). To jest ta najważniejsza
 rezerwa: obsługa dodatkowych protokołów, szyfrowanie, skrypty i bezpieczna aktualizacja
 (która wymaga miejsca na dwie kopie oprogramowania naraz) jedzą flash, nie megaherce.
- **Rodzina modułów daje ścieżkę w górę** — Shelly deklaruje sześć wariantów,
 a publicznie opisane są X0 do X4, różniące się liczbą wyprowadzeń i zasilaniem.

Innymi słowy: **zapas jest realny, choć nie kosmiczny.** Wystarczy na OCPP, rozliczenia,
obsługę kart, skrypty i solidne bezpieczeństwo. Nie wystarczy — i nie o to chodzi — na
ISO 15118 z modemem PLC, bo to wymaga dodatkowego sprzętu, nie mocniejszego procesora.


## Jak to się robi krok po kroku

Poniżej cała droga od dzisiejszej ładowarki na Tuya do ładowarki na Shelly, w kolejności,
w jakiej ustalono ją na spotkaniu. Przy każdym kroku piszę, co to znaczy po ludzku, kto to
robi i gdzie jest ryzyko.

### Krok 1. Spisanie listy funkcji w trzech horyzontach

**Co to jest.** Dokument, w którym AmperePoint wypisuje wszystko, co ładowarka ma robić,
podzielone na trzy grupy: co ma działać od pierwszego dnia dokładnie tak jak dziś, co ma
dojść „za chwilę”, i co ma być możliwe „na jutro”. Tak to ujęto:

> Znaczy, opiszmy wam co (…) jest dzisiaj jeden do jednego, co byśmy chcieli od razu
> w pierwszej iteracji, a jakie funkcjonalności potrzebujemy w przyszłości (…) w podzieleniu
> na jakieś tam segmenty klientów

> To wiesz co, musimy wrócić do tego, co powiedziałeś, musicie nam dać na teraz, na za
> chwilę i na jutro (…) Jak nam dacie te (…) funkcjonalności, które chcesz, no to zaraz to
> nam wyjdzie.

**Kto robi.** AmperePoint. Zadeklarowano termin: do końca następnego dnia.

**Dlaczego to jest najważniejszy krok całego projektu.** Bo ta lista jest jednocześnie:
specyfikacją techniczną dla Shelly, kryterium odbioru („czy to działa?”), podstawą wyceny
i — co najistotniejsze — **testem, czy wybrany moduł wystarczy na kilka lat**. Shelly wprost
mówi, że dopiero z tą listą będzie umiało powiedzieć, którą ścieżką iść.

**Gdzie ryzyko.** W pokusie napisania tylko tego, co jest dziś. Rzeczy z kolumny „na jutro”
(rozliczenia per użytkownik, karty, OCPP, praca w sieci firmowej) decydują o wyborze wariantu
modułu — a wybór modułu jest decyzją na lata produkcji.

### Krok 2. Analiza gap wobec TopAC

**Co to jest.** Porównanie funkcja po funkcji z ładowarką Shelly TopAC i wypisanie, czego
w niej nie ma, a co AmperePoint ma albo chce mieć. Dzięki temu Shelly widzi
listę życzeń nie w próżni, tylko wobec własnego, istniejącego produktu.

**Uwaga strategiczna.** Analiza działa w obie strony — pokazuje też Shelly, czym
AmperePoint przewyższa ich produkt. Warto świadomie zdecydować, co się w tym dokumencie
znajdzie.

### Krok 3. Dev kit na biurko

**Co to jest.** *Dev kit* (zestaw deweloperski) to mała płytka z tym samym modułem, wpinana
do komputera przez USB-C, na której można wyklikać i przetestować produkt, zanim ktokolwiek
ruszy prawdziwą ładowarkę.

> Ja wyślę Wam dev kita, to jest taki mały moduł nasz, który jest podłączeniem do USB-C do
> kompa, potem sobie włączycie i możecie sobie zasymulować, zaprogramować całe swoje
> urządzenia w tym małym dev kicie i zobaczycie, jak wygląda cały proces.

Shelly deklaruje dostarczenie dev kitu razem z ładowarką TopAC i przekładnikiem prądowym.

**Po co to naprawdę.** Żeby zespół AmperePoint zobaczył cały proces na własnych oczach,
zanim podejmie zobowiązania wobec fabryki. To jest najtańszy możliwy test partnera.

### Krok 4. Konto OEM i „utworzenie produktu” na platformie Shelly X

**Co to jest.** Na portalu producenta zakłada się konto, klika „Create Product” i przechodzi
kreator: jaki to typ urządzenia, jaki moduł, jakie wejścia i wyjścia, jakie funkcje.

> Wystarczy, że wejdziecie sobie na Shelly X, będziecie robili sobie Create Product. (…)
> Później mamy wybór płytki, ale ja wam powiem, która to jest płytka dokładnie [odpowiada
> za] WBR3.

**OEM** (*Original Equipment Manufacturer*) to w tym kontekście tryb pracy dla producenta,
który buduje własny produkt na cudzej platformie.

### Krok 5. Ścieżka „kopiuj Tuya” — mapowanie pinoutu i data pointów

To jest technicznie najciekawszy moment i dokładnie tu dzieje się „przesiadka”.

> (…) a wy musicie wybrać opcję „kopiuj Tuya”, bo to jest ścieżka gotowa i przenosicie po
> prostu (…) na gotowym waszym chipie pinout, odzwierciedlamy sobie funkcjonalności
> w pinoucie

> (…) nawet jesteśmy w stanie w przypadku prostych produktów na bazie tylko i wyłącznie tych
> data pointów, które macie tam w Tuya zrobić, jesteśmy w stanie odzwierciedlić

**Co się faktycznie dzieje.** Bierze się dwie rzeczy z obecnego rozwiązania:

- **pinout** — która nóżka modułu jest podłączona do czego na płytce ładowarki (linie
 transmisji do mikrokontrolera, diody, wejścia),
- **listę data pointów** — spis wszystkich informacji i poleceń, jakie ładowarka wymienia
 z aplikacją.

I odwzorowuje się je jeden do jednego w nowym module, tak żeby **mikrokontroler ładowarki
niczego nie zauważył**. Z jego punktu widzenia nadal rozmawia przez to samo złącze, tymi
samymi komunikatami, tylko po drugiej stronie siedzi inny partner.

**Ważne zastrzeżenie.** „Kopiuj” nie oznacza, że coś kopiuje się samo. Protokół, którym
moduł Tuya rozmawia z mikrokontrolerem produktu, jest inny niż u Shelly — ktoś musi
przetłumaczyć jeden na drugi. W przypadku prostych urządzeń robi to gotowa ścieżka
w narzędziu; przy ładowarce, gdzie w grę wchodzi bezpieczeństwo i logika sesji, **spodziewaj
się pracy inżynierskiej, a nie wyklikania w kreatorze**. Shelly zresztą mówi, że robili to
„na 20–30 produktach” — czyli to jest wydeptana ścieżka, ale nie automat.

### Krok 6. Zbudowanie oprogramowania

Shelly oferuje trzy poziomy, od najprostszego:

- **bez kodu** (*no-code*) — funkcje definiuje się klikając w portalu,
- **z niewielką ilością kodu** (*low-code*) — wtyczka do edytora Visual Studio Code,
- **skrypty w JavaScript** uruchamiane na samym urządzeniu — do logiki, której nie przewiduje
 kreator.

Na spotkaniu pada zdanie, które dobrze pokazuje dzisiejsze realia pracy:

> Co najważniejsze, my nie potrzebujemy kodu, bo to mamy na AI, więc wy opiszecie po prostu,
> co powinien zawierać, jakie feature'y i zobaczymy, zwalidujemy sobie.

Sens: Shelly nie chce od AmperePoint gotowego programu, tylko **dobrego opisu**. Pisanie
kodu na podstawie opisu jest dziś tanie; wiedza o tym, **co ma powstać i dlaczego**, jest
droga. Dlatego krok 1 jest wąskim gardłem całego projektu, a nie programowanie.

### Krok 7. Zmiana w fabryce

Tu kryje się rzecz, której łatwo nie docenić, a która decyduje o powodzeniu.

> (…) de facto na koniec elektronicznie czy proceduralnie dla fabryki nic się nie zmienia.
> Tylko samo pingowanie i testowanie później tej produkcji odbywa się do innej chmury.

Na taśmie produkcyjnej każde gotowe urządzenie jest **uruchamiane, programowane
i testowane**: wgrywa się firmware, nadaje unikalny identyfikator i klucze, sprawdza, czy
łączy się z chmurą, czy radio działa, czy wyświetlacz świeci. Ten proces nazywa się
**provisioningiem** i jest zaszyty w stanowiskach testowych fabryki.

Co realnie trzeba zmienić:

- pozycję w spisie części (moduł Shelly zamiast Tuya),
- oprogramowanie stanowiska testowego, żeby „pingowało” do chmury Shelly,
- procedurę testu końcowego i kryteria odbioru,
- dokumentację i etykiety (jeśli zmienia się identyfikator radiowy modułu).

Czego **nie** trzeba zmieniać, jeśli pinout się zgadza: płytki, obudowy, narzędzi, procesu
montażu.

### Krok 8. Człowiek na miejscu w Chinach

To jest najsilniej akcentowane oczekiwanie AmperePoint i moim zdaniem słusznie.

> Dalej najwygodniej byłoby pewnie gdyby Chińczyk gadał z Chińczykiem u siebie i zapłacić za
> to fee i jakby nie widzieć tego procesu (…) żebyśmy rozmawiali z kimś od Was o wyższych
> kompetencjach i nam opowiedział co się dzieje i wymusił pewne normy jakościowe, jak ten
> projekt powinien przebiegać.

> (…) zależy nam, żeby się, nazwijmy to, odciąć od jakości, którą mamy aktualnie w Tuya (…)
> żeby po prostu było tak super smooth z perspektywy i fabryki, i przyszłych feature'ów,
> i klienta.

Shelly deklaruje, że wsparcie lokalne w Chinach nie jest problemem, bo mają tam zespoły. **To jest punkt do zapisania w umowie, nie do zapamiętania z rozmowy** —
z nazwiskiem, zakresem i stawką.

Jest też szczery komentarz o tym, dlaczego to takie ważne — chodzi o opór fabryki przed
odejściem od chińskiej platformy:

> Czyli sam opór materii wynika czysto politycznie (…) Tuya jest chińską firmą i ten
> nacjonalizm dosyć mocny jest tam (…) więc to chociażby po to jest potrzebne, żeby dopatrzeć,
> że cały proces jest dopieszczony.

### Krok 9. Rozmowa z Borisem i harmonogram

Boris to szef działu badawczo-rozwojowego Shelly. Ustalono rozmowę, na której przejdzie cały
proces i powie, jak będzie wyglądała ścieżka. AmperePoint poprosił
o przesunięcie jej za targi.

### Krok 10. Certyfikacja i zgodność

Nie ustalono tego na spotkaniu, a trzeba: zakres dokumentacji RED (w tym część
cyberbezpieczeństwa wg EN 18031), ewentualne ponowne badania radiowe całego urządzenia,
deklaracja zgodności, oznakowanie. Część pokryje dokumentacja modułu, część trzeba zrobić
dla wyrobu. **To jest pozycja kosztowa i czasowa, która potrafi zaskoczyć na końcu projektu.**

### Ile to realnie potrwa

Na spotkaniu nikt nie podał terminu całości. Z opisu procesu wynika porządek wielkości:
tygodnie na specyfikację i prototyp na dev kicie, następnie kilka–kilkanaście tygodni na
firmware, testy, uruchomienie w fabryce i certyfikację. Jedno zdanie z rozmowy warto
zapamiętać jako realistyczną kotwicę:

> To i tak nie są zmiany overnight.


## Cztery warianty współpracy i pytanie o markę

Shelly przedstawia to nie jako jedną ofertę, lecz jako menu. Warto je rozpisać, bo każdy
wariant inaczej rozkłada koszty, kontrolę i korzyści marketingowe.

> Tutaj chciałbym wam pokazać właśnie, że wybieracie sobie środowisko, w którym chcecie
> współpracować, a następnie aplikacyjnie to już wy wybieracie (…)

### Wariant A: wasz mikrokontroler + moduł Shelly, wasza chmura albo tylko lokalnie

Ładowarka zachowuje swój mikrokontroler, dokłada moduł Shelly, a dane idą tam, gdzie chcecie
— do waszej chmury, do własnej aplikacji, albo **wcale** (praca wyłącznie lokalna).

- **Plus:** pełna kontrola i niezależność.
- **Minus:** musicie mieć i utrzymywać chmurę oraz aplikację. Shelly ostrzega przed tym
 uczciwie: *„koszt infrastruktury później będzie wam trochę przerastał maintenance,
 będzie znowu to samo co…”*. „Maintenance” to bieżące utrzymanie —
 serwery, aktualizacje, dyżury, bezpieczeństwo.

### Wariant B: moduł Shelly jako „otwieracz”, ale aplikacja i chmura wasze

Pośredni — bierzecie moduł po to, żeby mieć lepszą platformę i lokalne API, ale warstwę
klienta trzymacie u siebie.

### Wariant C: pełne wejście w ekosystem Shelly (wariant, który oni rekomendują)

Moduł Shelly, chmura Shelly, aplikacja Shelly.

> (…) albo w takim docelowym, jak zazwyczaj robimy, czyli wrzucacie nasz moduł do naszej
> chmury i do naszej aplikacji. Ta trzecia opcja uruchamia Wam automatycznie możliwości
> sprzedażowe.

„Możliwości sprzedażowe” to nie ogólnik — chodzi o to, że produkt staje się widoczny dla
2,7 miliona użytkowników aplikacji Shelly i dla ich sieci instalatorów, a Shelly może go
wziąć do własnego cennika i sprzedawać swoimi kanałami, tak jak robi to z TopAC.

### Wariant D: wasza chmura, ale kompatybilna z Shelly

Wspomniany osobno: produkt stoi na waszej infrastrukturze, ale pozostaje zgodny z chmurą
Shelly. Najwięcej swobody i najwięcej pracy.

### Co na to AmperePoint

Odpowiedź jest jednoznaczna i pragmatyczna — **nie chcą budować własnej aplikacji na siłę**:

> My nie widzimy wartości w [brandowaniu] na siłę [ani w] utrzymaniu swojej apki.

Uzasadnienie jest zarazem osobiste i trafne rynkowo — o tym, że użytkownik ma już w telefonie
osobną aplikację do każdego urządzenia i że to jest męczące:

> Ja na dzień dzisiejszy dostaję świra, że w domu nie mam postawionego home systemu (…) parę
> innych rzeczy mam wszystko w oddzielnych appkach, bo nie można tego połączyć (…)

To jest **argument za wariantem C**: dla klienta wartością jest to, że ładowarka pojawia się
w tej samej aplikacji, w której ma już przekaźniki, licznik i czujniki — a nie kolejna ikonka
na ekranie.

### Branding aplikacji — kompromis, który Shelly dokłada

Shelly zapowiada, że produkt partnera nie będzie anonimowym wierszem w ich katalogu:

> (…) to jest branding samej aplikacji Waszej, czyli nie będziecie kolejnym produktem
> z portfolio (…) Shelly do naszej aplikacji, tylko Wasz page produktowy będzie brandowany.

Zastrzeżenie: na spotkaniu powiedziano, że tej funkcji **jeszcze nie ma**, ma pojawić się do
końca roku. To jest obietnica, nie stan faktyczny — warto ją mieć zapisaną z terminem.

Dla porównania, ta sama rzecz u Tuya wyglądała tak:

> (…) mamy to delikatnie (…) logo, nie logo, wszystko jest, ale za customizację, która pewnie
> gdybyśmy mogli sami ten kod podmienić [zajęłaby] 4 godziny (…) zapłacić 100 000 dolarów,
> z kosmosu, za skórkę

Liczba jest podana w rozmowie z emocją i nie weryfikowałem jej — ale sens jest czytelny:
**personalizacja wyglądu aplikacji była u obecnego dostawcy wyceniana absurdalnie wysoko
w stosunku do nakładu pracy.**

### Moja ocena wariantów

Dla firmy wielkości AmperePoint, bez własnego zespołu chmurowego i z ambicją szybkiego
skalowania, **wariant C jest naturalny na start, z zachowaniem furtki do B**. Argumenty:

- utrzymanie chmury to koszt stały i dyżury 24/7, a nie jednorazowy projekt,
- korzyść marketingowa z bycia „w ekosystemie” działa tylko w wariancie C,
- praca lokalna w urządzeniach Shelly i lokalne API sprawiają, że nawet w wariancie C
 **nie jesteście zakładnikiem ich chmury** w takim stopniu jak dziś u Tuya — i to jest
 różnica jakościowa wobec obecnej sytuacji.

Warunek, który warto postawić w umowie: **prawo do eksportu danych i do lokalnego trybu
pracy niezależnie od wariantu**. To jest tania klauzula dziś i bezcenna za trzy lata.


## Czego ta zmiana nie załatwi

Uczciwa analiza musi powiedzieć też, gdzie leży granica. Wymiana modułu rozwiązuje problem
kontroli nad oprogramowaniem i danymi. Nie rozwiązuje czterech rzeczy.

### 1. ISO 15118 i komunikacja PLC z samochodem

To wymaga **dodatkowego sprzętu** — modemu komunikacji po przewodzie oraz infrastruktury
certyfikatów. Żaden moduł Wi-Fi tego nie zastąpi, bo to inna warstwa fizyczna. Jest to
dokładnie ten koszt, który w rozmowie wyceniono na około 70 dolarów w produkcji, i dokładnie ten problem, o którym AmperePoint mówi, że jeszcze nie wie, jak
go rozwiąże.

**Co to znaczy praktycznie:** jeśli wymagania AFIR obejmą również sprzęt przenośny od
2027 roku, to zmiana modułu Wi-Fi **nie wystarczy** i trzeba będzie osobnego projektu
sprzętowego. Zmiana platformy jest warunkiem koniecznym, ale nie wystarczającym.

### 2. Moduł z kartą SIM

Dla projektów komercyjnych — ładowarki na parkingach firmowych, u operatorów, w miejscach
bez zasięgu Wi-Fi — potrzebna jest łączność komórkowa. Zapytanie AmperePoint i odpowiedź
Shelly są jednoznaczne:

> Macie jakikolwiek chip, który obsługuje SIM-kartę? — To jest dobre pytanie. Bo nie mamy.
> Nie. Nie, na pewno nie mamy.

> W ogóle to nie było, wiesz, to jest jakby trochę cofanie się dla Shelly, to jest trochę
> cofanie się tam o trzy kroki.

Padł pomysł obejścia przez eSIM (kartę wirtualną, wlutowaną w urządzenie),
ale to nadal wymaga modemu komórkowego, którego w ofercie modułów nie ma.

Dlaczego to boli: AmperePoint mówi o konkretnych, leżących na stole kontraktach:

> Mając przykładowo taki protokół OCPP i tak dalej, to my mamy takie deale, nazwijmy to na
> stole, które leżą tam 500 sztuk rocznie, które po prostu sobie leżą. My nie mieliśmy tego
> jak chwycić (…)

Warto to policzyć: przy 500 sztukach rocznie i cenie rzędu 1500–2500 zł dla klienta
biznesowego mówimy o rzędzie miliona złotych rocznie przychodu zablokowanego brakiem dwóch
funkcji — rozliczeń i łączności. To jest twardy argument w negocjacjach z Shelly.

### 3. Jakość dostarczana przez fabrykę

Zmiana modułu nie zmienia tego, kto lutuje i testuje. AmperePoint mówi o tym otwarcie
w kontekście nieudanego projektu dla wymagającego klienta:

> I my nie chcieliśmy wchodzić w coś, co my w przypadku fuck-upu nie będziemy sami w stanie
> zrobić aktualizacji firmware'u z tego protokołu overnight. Będziemy czekać (…) aż Chińczyk
> zareaguje w tygodniu (…)

> Poziom jakości wymagany jest w firmie farmaceutycznej, gdzie ze wszystkiego robią się
> [czerwoni] (…) My wycofaliśmy się z takiego projektu

Tu zmiana platformy **pomaga częściowo**: możliwość samodzielnego wydania aktualizacji
w ciągu godzin zamiast tygodni to dokładnie to, czego brakowało. Ale sama jakość montażu,
komponentów i testów pozostaje po stronie fabryki — i dlatego tak istotny jest człowiek
Shelly na miejscu.

### 4. Zależność jako taka

To jest punkt, który wymaga chłodnej głowy. **Wyjście z Tuya do Shelly nie jest wyjściem
z zależności — jest zmianą tego, od kogo się zależy.** Różnica jest realna i moim zdaniem
korzystna:

| Wymiar | Tuya dziś | Shelly po zmianie |
| --- | --- | --- |
| Kto definiuje funkcje | platforma | wy, w narzędziu platformy |
| Praca bez chmury | ograniczona | przewidziana |
| Lokalizacja danych | Chiny/globalnie | Europa |
| Wasza waga u dostawcy | ziarnko piasku | partner referencyjny w nowej kategorii |
| Dostęp do kodu i eksport danych | brak | do ustalenia w umowie |

…ale to nadal jest cudza platforma, cudza chmura i cudza marka. Dlatego klauzule
o eksporcie danych, o trybie lokalnym i o tym, co się stanie przy zmianie właściciela Shelly,
są ważniejsze niż cena modułu.

To ostatnie nie jest teoretyczne — pojawia się w rozmowie jako obawa AmperePoint:

> Ja się tylko zastanawiam, jakby na przykład was jakaś większa firma kupiła, typu Schneider,
> który ma zamknięty system.

Odpowiedź Shelly sprowadzała się do tego, że nikt nie kupuje firmy za taką kwotę po to, żeby
ją zamknąć, i że kierunek jest odwrotny — ku otwartości. To jest rozsądna
odpowiedź, ale nie jest gwarancją i nie da się jej wpisać do umowy. Można natomiast wpisać
do umowy skutki: prawo do dalszego użycia oprogramowania, eksport danych, okres wypowiedzenia.


## Co każda ze stron chce z tego ugrać

Dobre negocjacje zaczynają się od zrozumienia, czego naprawdę chce druga strona. W tych
obu rozmowach obie strony powiedziały to zaskakująco otwarcie.

### AmperePoint chce czterech rzeczy

**Kontroli nad rozwojem produktu.** Żeby obiecana klientowi funkcja zależała od nich, a nie
od priorytetów firmy z drugiego końca świata.

**Dostępu do klienta biznesowego.** Rozliczenia, karty, integracje — segment, który dziś
odpada na starcie.

**Jakości, za którą nie płaci się supportem.** Możliwość wydania poprawki w ciągu godzin.

**Marki, do której można się przykleić.** Argument z akcesoriami w ekosystemie Apple
 — cudza rozpoznawalność podnosi wartość waszego produktu bez zmiany produktu.

Jest też motyw, który pada w dalszej części rozmowy i mówi wiele o ich sposobie myślenia: nie chcą
wchodzić w kolejne kategorie kosztem tej, w której są, bo to najszybszy sposób na utratę
pozycji:

> Kategoria nasza na tyle dynamicznie idzie do przodu, że też takie oportunistyczne, o
> wejdźmy w kolejną kategorię zamiast dopieszczać, to możemy zaraz stracić swojej pozycji
> (…) bo nie trzymaliśmy ręki na pulsie, że trzeba cały czas dopieszczać produkt i dawać
> kolejną wartość.

To jest zdrowa dyscyplina strategiczna i warto ją zapamiętać przy ocenie pomysłów
dosprzedażowych, które Shelly będzie podsuwać (magazyny energii, liczniki, przekaźniki).

### Shelly chce trzech rzeczy

**Kategorii, której nie ma.** Powiedziane wprost: *„to wy będziecie definiować u nas tą
kategorię”*.

**Wolumenu i zasięgu w nowym kanale.** AmperePoint sprzedaje tam, gdzie Shelly nie sprzedaje
— do konsumenta kupującego ładowarkę, nie do instalatora automatyki.

**Klienta, który wciąga kolejne produkty.** To jest myśl AmperePoint, ale jest to
jednocześnie najlepszy argument sprzedażowy wobec Shelly i dlatego został im podany na tacy:

> (…) ten produkt otwiera klientów na smartfonowe rzeczy i przez cross-sell później ktoś
> wejdzie (…) będzie wolał mieć licznik dwukierunkowy od Was, później stwierdzi, o, dorzucę
> przekaźnik tu, tam, siam (…) i to lawinowo pójdzie przez to, że nasze urządzenie jest tak
> zwanym urządzeniem niskiego progu wejścia

**Cross-sell** to sprzedaż dodatkowych produktów klientowi, który już coś kupił.
Mechanizm jest realny: ktoś, kto kupił ładowarkę i zobaczył, że ma ją w aplikacji razem
z licznikiem prądu, kupi następnie przekaźnik do bramy i czujnik zalania. **Ładowarka jest
drzwiami do domu klienta** — dosłownie i w sensie handlowym.

### Asymetria, o której trzeba pamiętać

AmperePoint sam nazywa ten biznes słabym z punktu widzenia Shelly:

> (…) czy to nieważne ile by był, to nie jest biznes, nie? Ale mówię, to jest słaby biznes,
> sam w sobie.

I ma rację arytmetycznie. Przy 149,7 mln euro przychodu Shelly nawet kilkanaście tysięcy
modułów rocznie to pozycja, której nie widać w raporcie. Dla AmperePoint to jest fundament
produktu.

**Co z tej asymetrii wynika praktycznie:**

- **Nie liczcie na to, że Shelly będzie pilnować harmonogramu za was.** Projekt ma priorytet
 taki, jaki mu nadacie swoją obecnością.
- **Wartość, którą wnosicie, jest niepieniężna** — wiedza o kategorii, referencja, wejście
 do nowego kanału. To jest waluta w tych negocjacjach i warto nią świadomie płacić za
 konkrety: nazwisko PM-a w Chinach, terminy, zakres dokumentacji do certyfikacji.
- **Najlepszy moment na twarde ustalenia jest teraz**, dopóki jesteście „tym, kto zdefiniuje
 kategorię”, a nie jednym z dwudziestu partnerów w niej.

Druga strona zresztą sama podpowiada, jak na to patrzeć:

> Ja bym to już naprawdę wprost tego patrząc traktował Shelly jako lewar sprzedażowy.
> Zmieniając technologię jesteście w stanie wejść po prostu na nowe rynki bezinwestycyjnie.

**Lewar** (dźwignia) w biznesie oznacza narzędzie, które zwielokrotnia efekt własnego
wysiłku. Zdanie jest prawdziwe — z zastrzeżeniem, że dźwignia działa w obie strony: opiera
się na cudzym punkcie podparcia.


## Pieniądze: marże, rabaty i kanały

Druga część rozmowy jest w dużej mierze o ekonomii współpracy. Rozłóżmy to na czynniki, bo dla
kogoś spoza handlu te liczby brzmią jak szyfr.

### Jak się liczy marżę i rabat w dystrybucji

Producent ustala cenę katalogową (tzw. cennik). Partnerzy handlowi kupują z **rabatem** od
tej ceny — im większy partner i większy wolumen, tym większy rabat. Rabat 55 % oznacza, że
partner płaci 45 % ceny katalogowej. Różnica między ceną zakupu a ceną sprzedaży to jego
**marża**.

Pada zdanie, które opisuje twardą granicę po stronie AmperePoint:

> No bo to nie ma sensu wtedy, przy tym, że patrzę sobie tam na wyniki, że my poniżej 55
> w ogóle nie sprzedajemy niczego

oraz, co do produktów obcych marek w ich ofercie:

> No na tych obcych produktach, jeżeli nie będziemy mieli tam marży między 30 a… — Nie ma
> sensu wtedy.

Czyli: **na produkcie obcej marki AmperePoint potrzebuje co najmniej ok. 30 % marży, żeby
w ogóle się nim zajmować.** To jest konkretna liczba do negocjacji z Shelly, jeśli miałoby
dojść do odsprzedaży produktów Shelly (przekaźniki, liczniki, magazyny) przez AmperePoint.

Po stronie Shelly sytuacja jest bardziej skomplikowana i sami to przyznają:

> Znaczy, inny poziom marży mamy (…) bo tam mamy różne kategorie tych produktów, inaczej
> rabatowane, bałagan, tak? No i też na przykład te Powered są zupełnie inaczej rabatowane.

„Powered” to linia **Powered by Shelly** — produkty innych firm zbudowane na module Shelly.
Skoro mają osobną politykę rabatową, to jest to punkt, który trzeba wyjaśnić konkretnymi
liczbami, zanim powstanie wspólny produkt.

### Rynek polski kontra zagraniczny

> Na rynku zagranicznym pewnie dla nas to nie dałby sens. Na rynku polskim to maksymalne
> rabaty, dlatego że po prostu ta kategoria jest trochę wyżyłowana, ale znowu wchodząc (…)
> w nowe funkcjonalności, mamy przestrzeń na podbicie marż, nie pomijając poziomu kosztowego.

„Wyżyłowana kategoria” to taka, w której wszyscy już zeszli z cenami tak nisko, jak się da.
Jedyne wyjście z takiej pułapki to **zmiana tego, co się sprzedaje** — czyli dołożenie
funkcji, za które można wziąć więcej. To jest dokładnie ekonomiczne uzasadnienie całego
projektu wymiany platformy i warto to zdanie zapamiętać, bo spina technologię z pieniędzmi.

### Dwa kanały, dwa numery EAN

Opisane wcześniej rozwiązanie: ten sam fizycznie produkt sprzedawany pod różnymi numerami
towarowymi w różnych kanałach, żeby nie zderzać cen.

### Amazon: przykład, ile zostaje ze sprzedaży

Shelly opowiada o własnym doświadczeniu i to jest bardzo pouczający fragment dla każdego,
kto myśli o marketplace'ach:

> Jest jeden produkt, który tak naprawdę ciągnie nam całe Amazon, to jest to gniazdko (…)
> nie ma tak wysoko jakościowego gniazdka zewnętrznego (…) my sprzedajemy je po 50 euro,
> kosztuje poniżej 10, z tego można na Amazonie żyć (…) bo Amazon (…) koszty obsługi to
> zabija.

Mechanizm: Amazon pobiera prowizję, koszty magazynowania i obsługi zwrotów. Przy produkcie
z marżą kilkunastu procent te koszty zjadają cały zysk. **Na marketplace'ach da się żyć
tylko z produktów o bardzo wysokiej marży jednostkowej** — tu pięciokrotność kosztu
wytworzenia.

Pada też pytanie o model współpracy z Amazonem:

> Ale to w fulfilmencie z nimi działacie? Że wysyłacie do nich te 30% na dzień dobry
> zostawiać u nich?

**Fulfilment** (Amazon FBA) to model, w którym towar leży w magazynie Amazona, a oni pakują
i wysyłają. Wygodne, ale kosztowne — stąd wspomniane „30 % na dzień dobry”. Alternatywa to
wysyłka własna, przy której jednak — jak zauważa rozmówca — niemiecki klient chce widzieć
towar „na miejscu”:

> Jeżeli coś nie jest na magazynie niemieckim to (…) Niemiec to widzi (…)

### Ile to wszystko może być warte — rachunek poglądowy

Nikt na spotkaniu nie policzył wartości projektu, więc zrobię to szacunkowo, **wyraźnie
zaznaczając, że to moja arytmetyka, nie ich deklaracja**:

| Pozycja | Założenie | Efekt roczny |
| --- | --- | --- |
| Odblokowane kontrakty B2B | 500 szt./rok, ok. 2000 zł netto | ok. 1,0 mln zł przychodu |
| Podniesienie marży w kanale konsumenckim | +5 p.p. na ok. 10 tys. szt. × 1200 zł | ok. 0,6 mln zł marży |
| Oszczędność na wsparciu technicznym | mniej reklamacji „rozparowało się” | trudne do wyceny, ale realne |
| Koszt: moduł | różnica ceny modułu × wolumen | rzędu dolarów na sztukę |
| Koszt: wdrożenie | firmware, testy, certyfikacja, PM w Chinach | jednorazowo, dziesiątki tysięcy zł |

Wniosek z tego zestawienia: **projekt broni się już samym odblokowaniem segmentu firmowego**,
nawet gdyby nie przyniósł ani złotówki więcej w kanale konsumenckim. To jest dobra rama do
rozmowy wewnętrznej o budżecie.


## Rynki, skala i ograniczenia wzrostu

Druga część rozmowy dotyczy w dużej mierze geografii: gdzie kto sprzedaje, gdzie jest
przestrzeń i co blokuje wzrost. Dla zrozumienia całości jest to istotne, bo pokazuje, czym
dla każdej ze stron jest ta współpraca.

### Gdzie sprzedaje Shelly

Z rozmowy i z raportów układa się spójny obraz:

- **Europa to około 90 % biznesu**; reszta świata to dziesięć procent.
- **DACH jest najmocniejszy**, i to nie dlatego, że ktoś tam bardziej lubi Shelly, tylko
 z powodu **penetracji rynku** — czyli odsetka gospodarstw domowych, które już mają
 jakąkolwiek automatykę: *„tam po prostu największa jest penetracja rynku”*.
- **Skandynawia** — silna, z lokalnym liderem Plejd.
- **Stany Zjednoczone** — mały biznes i konkretny problem: *„mamy problem głównie
 z dystrybucją. To jest specyficzny typ dystrybucji”*. Mowa o około
 4 mln dolarów.
- **Australia, Nowa Zelandia, Ameryka Południowa** — obecność, ale nie skala.

### Plejd jako lustro

W rozmowie pada ciekawe porównanie:

> (…) jak popatrzysz sobie na Skandynawię, na Plejda, który tam jest. Nie wszyscy nawet
> kojarzymy tą markę (…) to on jest dzisiaj na tyle duży, że jest porównywalny do [nas].
> Ale działa głównie w Szwecji, troszeczkę gdzieś tam w Norwegii, troszeczkę w Danii. I oni
> sprzedają sześć urządzeń (…) Światło i power metering na poziomie zerowym.

Dane zewnętrzne to potwierdzają: szwedzki Plejd ma około 116 mln dolarów przychodu
w ostatnich dwunastu miesiącach (stan na połowę 2026 r.), ponad 5 mln zainstalowanych
urządzeń i ponad 50 tys. instalatorów, działając głównie w krajach nordyckich (źródło:
dane giełdowe i materiały spółki).

**Wniosek, który z tego płynie i który dotyczy też AmperePoint:** można zbudować firmę
wielkości Shelly, sprzedając **kilka produktów na jednym rynku**, zamiast setek produktów
wszędzie. Głębokość bije szerokość. To jest dokładnie ta sama myśl, co ostrzeżenie
AmperePoint przed rozpraszaniem się na nowe kategorie.

### Co ogranicza wzrost AmperePoint

Tu pada najbardziej praktyczny fragment o zarządzaniu firmą:

> Mamy też taki problem, że portfolio (…) tych produktów jest niby nazwijmy to 4, nazwijmy
> to 5 bazowych, ale każdy produkt potrzebuje od 2 do 5 wariantów. [Gdy] wchodzimy w kolejne
> wtyczki, to nagle ten magazyn utrzymać (…) trzeba właśnie być wybranym, dlatego właśnie
> boimy się trochę nowej kategorii (…) bo nie będziemy mieli takiego runway'a i stracimy
> pozycję

Rozłóżmy to, bo to jest istota problemu małych producentów sprzętu:

- **Pięć produktów bazowych razy 2–5 wariantów to 10–25 pozycji magazynowych.** Warianty
 biorą się z wtyczek (różne gniazda w różnych krajach), mocy, długości kabla, kolorów.
- **Każda pozycja to zamrożone pieniądze.** Towar trzeba kupić, zapłacić, przywieźć
 i trzymać, zanim się sprzeda.
- **Runway** to w żargonie finansowym „pas startowy” — ile czasu firma może działać
 z posiadaną gotówką. Im więcej zamrożonego towaru, tym krótszy.

Stąd ostrożność wobec nowych kategorii i stąd logika: **lepiej dołożyć wartość do
istniejących pozycji magazynowych niż mnożyć nowe**. Zmiana platformy na taką, która pozwala
dokładać funkcje zdalnie, jest w tej optyce idealna — nie tworzy ani jednej nowej pozycji
magazynowej.

Rozważane jest natomiast rozszerzenie geograficzne, nie produktowe:

> My teraz też się zastanawialiśmy (…), czy nie próbować jakiegoś tam na razie delikatnego
> liźnięcia UK-a, no bo technicznie to jest zmiana tylko w certyfikacji i (…) prawie to samo.

To jest rozsądny kierunek: ta sama elektronika, inna wtyczka i inne papiery. Warto pamiętać,
że po brexicie dochodzi osobne oznakowanie brytyjskie, więc „tylko certyfikacja” może
oznaczać więcej pracy, niż brzmi.

### Bundlowanie: sprzedawać klocki, nie klocek

Ostatni wątek rynkowy to obserwacja, że klienci i tak sami składają zestawy:

> Ono już się dzieje (…) Już my widzimy, że nasi klienci korzystają z tych bundli w ramach
> Home Assistanta, mają te klocki, więc dla nas jest naturalne posiadać wszystkie te klocki
> w sprzedaży.

**Home Assistant** to darmowe, otwarte oprogramowanie do automatyki domowej, które ludzie
stawiają sobie sami i które potrafi połączyć urządzenia wielu producentów w jeden system.
Jego użytkownicy to najbardziej wymagająca i najbardziej wpływowa grupa w tym segmencie —
to oni piszą recenzje i doradzają znajomym.

Wniosek: skoro klienci i tak łączą ładowarkę z licznikiem i przekaźnikiem, to sprzedawanie
im gotowego zestawu jest naturalnym krokiem — i to jest właśnie **bundlowanie**, czyli
sprzedaż pakietu produktów, o którym mówi Shelly przy okazji przekładnika prądowego.


## Ryzyka i pytania, na które nikt jeszcze nie odpowiedział

### Tabela ryzyk

| Ryzyko | Na czym polega | Co z tym zrobić |
| --- | --- | --- |
| Zakres AFIR dla sprzętu przenośnego | Cała strategia „przenośny, więc lżejszy rygor” opiera się na interpretacji przepisu | Pisemna opinia jednostki notyfikowanej lub kancelarii, przed budżetem na 2027 |
| Brak modułu z łącznością komórkową | Blokuje projekty komercyjne warte rzędu miliona zł rocznie | Zapytać Shelly o plan i termin; równolegle rozważyć zewnętrzny modem |
| ISO 15118 / PLC | Wymaga osobnego sprzętu, nie załatwia tego moduł Wi-Fi | Osobny projekt i osobny budżet; decyzja „kiedy”, nie „czy” |
| Priorytet projektu u Shelly | Dla nich to mała kategoria | Zapisane terminy, nazwisko PM-a, regularny rytm spotkań |
| Opór fabryki | Zmiana z chińskiej platformy na europejską bywa niechętnie przyjmowana | Człowiek Shelly na miejscu; zapis w zamówieniu, nie ustalenie ustne |
| Zależność 2.0 | Zmieniacie pana, nie stan | Klauzule: eksport danych, tryb lokalny, ciągłość przy zmianie właściciela |
| Przejęcie Shelly | Obawa podniesiona wprost | j.w. — zabezpieczenie skutków, nie zdarzenia |
| Certyfikacja RED i EN 18031 | Niedoszacowany koszt i czas na końcu projektu | Ustalić na piśmie, co pokrywa dokumentacja modułu |
| Koszty magazynowe wariantów | Każdy nowy wariant to zamrożona gotówka | Priorytet dla funkcji dodawanych zdalnie, nie nowych indeksów |
| Konkurencja z partnerem | TopAC to produkt bardzo podobny do waszego | Świadoma decyzja, ile pokazujecie w analizie gap |

### Pytania otwarte po obu spotkaniach

Zebrane w kolejności, w jakiej powinny paść na rozmowie z Borisem:

**Techniczne**

- Który konkretnie moduł (X0–X4) odpowiada pinoutem obecnemu WBR3 i jaka jest jego
 dokładna pamięć flash i RAM?
- Czy na tym samym pinoucie jest wariant mocniejszy, na później?
- Jak dokładnie wygląda odwzorowanie protokołu do mikrokontrolera ładowarki? Kto pisze tę
 warstwę i kto ją utrzymuje?
- Czy OCPP da się obsłużyć **lokalnie na module**, czy tylko przez chmurę?
- Jaki jest realny czas wydania aktualizacji przez was — od zgłoszenia do wgranej poprawki?
- Czy jest droga do łączności komórkowej w perspektywie roku–dwóch?

**Formalne**

- Co dokładnie pokrywa wasza dokumentacja RED i EN 18031, a co musimy zbadać dla wyrobu?
- Jak wygląda odpowiedzialność, gdy aktualizacja waszego firmware'u popsuje urządzenia
 w terenie? (to jest scenariusz Green Cell, tylko z waszej strony)
- Czy możemy wyeksportować dane użytkowników i telemetryczne, gdybyśmy chcieli odejść?
- Co się dzieje z licencją i wsparciem, jeśli Shelly zmieni właściciela?

**Handlowe**

- Cena modułu przy naszych wolumenach i przy jakich progach się zmienia?
- Stawka i zakres lokalnego PM-a / inżyniera w Chinach?
- Warunki rabatowe, gdybyśmy sprzedawali wasze produkty (padło: minimum ok. 30 % marży)?
- Kiedy dokładnie będzie brandowana strona produktowa w aplikacji? *(obietnica „do końca roku”)*
- Czy i na jakich zasadach nasz produkt trafia do waszego cennika i waszych kanałów?


## Co ustalono i co robić dalej

### Ustalenia ze spotkań

| Kto | Co | Kiedy |
| --- | --- | --- |
| AmperePoint | Spisuje listę funkcjonalności w trzech horyzontach: „dziś jeden do jednego”, „za chwilę”, „na jutro” | „jutro do końca dnia” |
| AmperePoint | Analiza gap wobec ładowarki TopAC | po otrzymaniu sprzętu |
| Shelly | Dostarcza dev kit, ładowarkę TopAC i przekładnik prądowy 120 A | przy najbliższej okazji; dopytanie o adres |
| Shelly | Organizuje rozmowę z Borisem, szefem R&D — ok. godziny | pierwotnie poniedziałek 14:00, przesunięte za targi |
| AmperePoint | Udział w targach (Kongres Nowej Mobilności, Katowice) | „w przyszłym tygodniu”, stąd przesunięcie rozmowy |
| Shelly | Przygotowanie dostawy sprzętu przez Czarka | |

### Czego w ustaleniach brakuje — moja rekomendacja

Ustalenia ze spotkań są dobre operacyjnie, ale nie zabezpieczają projektu. Proponuję dopisać
do nich sześć rzeczy, w tej kolejności:

**1. Zanim powstanie lista funkcji — ustalić jej strukturę.** Nie „lista życzeń”, tylko
tabela: funkcja, po co jest, kto z niej korzysta (konsument / firma / instalator), czy jest
dziś, w którym horyzoncie ma być, co jest potrzebne po stronie sprzętu. Taka tabela od razu
pokaże, które pozycje wymagają modemu PLC albo modemu komórkowego — a więc wypadają poza
zakres tego projektu.

**2. Do listy funkcji dołożyć wymagania niefunkcjonalne.** Czas reakcji na awarię, czas
wydania poprawki, dostępność chmury, sposób logowania zdarzeń, wymagania dla klienta
firmowego (raporty, eksport, konta). To jest to, co później decyduje o przetargach.

**3. Poprosić o pisemną odpowiedź na pytania formalne** z poprzedniego rozdziału —
szczególnie o zakres dokumentacji RED i o eksport danych. Nie na rozmowie, tylko mailem.

**4. Ustalić pilota.** Jeden produkt, jedna fabryka — najlepiej ta z mocnym zespołem
elektroników — i jedna, niewielka partia. Nie przenosić trzech półek cenowych naraz.

**5. Zapisać rolę człowieka w Chinach.** Nazwisko, zakres, stawka, do kogo raportuje. To
jest, moim zdaniem, pojedynczy czynnik, który najbardziej wpłynie na powodzenie wdrożenia —
i jedyny, którego nie da się nadrobić później.

**6. Ustalić, co się stanie z urządzeniami już sprzedanymi.** W terenie są ładowarki na
Tuya. Czy zostają, czy jest ścieżka migracji, czy będą wspierane równolegle? To jest pytanie
o koszt utrzymania dwóch platform przez kilka lat i o komunikację do klientów.

### Kolejność, gdybym miał to ułożyć od zera

- **Tydzień 1–2:** lista funkcji z wymaganiami niefunkcjonalnymi; pytania formalne wysłane
 mailem; odebranie dev kitu i TopAC.
- **Tydzień 2–3:** rozmowa z Borisem; analiza gap; wybór konkretnego modułu; potwierdzenie
 pinoutu na podstawie dokumentacji obecnej płytki.
- **Tydzień 3–6:** prototyp na dev kicie odwzorowujący dzisiejszą funkcjonalność; równolegle
 wycena i warunki handlowe.
- **Tydzień 6–10:** prototyp w prawdziwej ładowarce; testy; uruchomienie procesu w jednej
 fabryce; ustalenia certyfikacyjne.
- **Tydzień 10+:** partia pilotażowa, testy w terenie, decyzja o przeniesieniu pozostałych
 produktów.

To jest harmonogram optymistyczny i zakłada, że nikt po drodze nie znika na trzy tygodnie.
Warto go traktować jako szkielet do wypełnienia realnymi datami po rozmowie z Borisem,
a nie jako obietnicę.


## Słowniczek

- **AFIR** — rozporządzenie (UE) 2023/1804 o infrastrukturze paliw alternatywnych. Ujednolica
 w Unii wymagania wobec punktów ładowania: dostępność, płatności, przejrzystość cen
 i standardy komunikacji.
- **Analiza gap** — porównanie dwóch produktów funkcja po funkcji i wypisanie różnic
 („luki”). Służy do zaplanowania, co trzeba dorobić.
- **API** — zestaw poleceń, którymi jeden program może sterować drugim. „Lokalne API”
 oznacza, że urządzeniem da się sterować bezpośrednio z sieci domowej, bez chmury.
- **Billing** — rozliczanie zużycia na konkretnego użytkownika, kartę albo dział firmy.
- **Bundlowanie** — sprzedaż kilku produktów razem jako zestawu.
- **CEE** — przemysłowe gniazdo i wtyczka (te niebieskie i czerwone), używane do zasilania
 ładowarek przenośnych.
- **Chmura** — serwery dostawcy, z którymi łączy się urządzenie i przez które działa
 aplikacja w telefonie.
- **Cross-sell** — dosprzedaż innych produktów klientowi, który już coś kupił.
- **CSMS** — system zarządzania stacjami ładowania po stronie operatora; to z nim ładowarka
 rozmawia protokołem OCPP.
- **CT / przekładnik prądowy** — obejma zakładana na przewód w rozdzielnicy, mierząca
 przepływający prąd. Pozwala systemowi wiedzieć, ile mocy jeszcze zostało.
- **DACH** — skrót handlowy na Niemcy, Austrię i Szwajcarię.
- **Data point (punkt danych)** — pojedyncza informacja albo polecenie, które urządzenie
 wymienia z aplikacją (np. „prąd zadany”, „energia sesji”). Lista data pointów jest
 faktyczną specyfikacją produktu od strony oprogramowania.
- **Dev kit** — zestaw deweloperski; płytka z modułem wpinana do komputera, na której
 testuje się produkt przed dotknięciem prawdziwego urządzenia.
- **DLB** (*Dynamic Load Balancing*) — dynamiczne zarządzanie obciążeniem: ładowarka sama
 zmniejsza prąd, gdy dom zużywa dużo, żeby nie wybiło bezpiecznika.
- **EAN** — kreskowy numer towaru. Osobne numery pozwalają sprzedawać ten sam produkt
 w różnych kanałach po różnych cenach.
- **EMS** (*Energy Management System*) — system zarządzania energią w budynku: patrzy na
 produkcję z paneli, magazyn, cenę prądu i decyduje, co włączyć.
- **ESP32-C3** — układ scalony firmy Espressif z procesorem RISC-V do 160 MHz, Wi-Fi
 i Bluetooth; serce modułów Shelly X.
- **EVSE** — formalna nazwa „ładowarki” do auta elektrycznego (sprzęt zasilający pojazd).
- **Firmware** — oprogramowanie zaszyte w urządzeniu.
- **Flash** — pamięć nieulotna, w której mieszka firmware. Jej rozmiar ogranicza to, ile
 funkcji da się w urządzeniu zmieścić.
- **Fulfilment (Amazon FBA)** — model, w którym towar leży w magazynie Amazona, a oni pakują
 i wysyłają; wygodne, ale drogie.
- **Home Assistant** — darmowe, otwarte oprogramowanie do automatyki domowej, łączące
 urządzenia wielu producentów w jeden system.
- **IoT** (*Internet of Things*) — internet rzeczy; urządzenia codziennego użytku podłączone
 do sieci.
- **ISO 15118** — standard cyfrowej komunikacji między autem a ładowarką; umożliwia
 Plug & Charge, negocjację harmonogramu i ładowanie dwukierunkowe.
- **Lead** — zapytanie od potencjalnego klienta.
- **Local first** — filozofia projektowa, w której urządzenie działa w pełni bez internetu,
 a chmura jest dodatkiem.
- **Marża** — różnica między ceną sprzedaży a kosztem; **rabat** — upust od ceny katalogowej
 dla partnera handlowego.
- **MCU** — mikrokontroler; mały procesor sterujący urządzeniem.
- **Mode 3** — ładowanie prądem przemiennym przez dedykowany sprzęt (wallbox lub ładowarka
 przenośna), w odróżnieniu od ładowania ze zwykłego gniazdka.
- **Moduł** — gotowa płytka z procesorem, radiem i pamięcią, wlutowywana w produkt, żeby
 dodać mu łączność.
- **No-code / low-code** — tworzenie oprogramowania bez pisania kodu (przez klikanie)
 albo z minimalną jego ilością.
- **OCPP** (*Open Charge Point Protocol*) — otwarty standard komunikacji między ładowarką
 a systemem operatora. W użyciu wersje 1.6 (ok. 90 % instalacji) i 2.0.1.
- **OEM** — producent budujący własny produkt, często na cudzej platformie lub w cudzej
 fabryce.
- **OTA** (*over-the-air*) — aktualizacja oprogramowania przez sieć, bez kabla i serwisanta.
- **Penetracja rynku** — odsetek klientów w danym kraju, którzy mają już produkt danej
 kategorii.
- **Ping** — krótki komunikat „żyję”, który urządzenie wysyła do chmury.
- **Pinout** — rozkład i znaczenie wyprowadzeń („nóżek”) modułu. Zgodny pinout pozwala
 wymienić moduł bez przeprojektowania płytki.
- **PLC** (*Power Line Communication*) — przesyłanie danych po przewodzie zasilającym lub
 sygnałowym; używane przez ISO 15118.
- **Plug & Charge** — wtykasz kabel i wszystko dzieje się samo: auto się przedstawia,
 a rozliczenie jest automatyczne.
- **Provisioning** — proces nadania urządzeniu na taśmie produkcyjnej tożsamości, kluczy
 i oprogramowania oraz sprawdzenia, czy łączy się z chmurą.
- **PWM** — sposób, w jaki ładowarka mówi autu, ile prądu może pobrać: szerokością impulsu
 na żyłce sygnałowej. Prymitywne, ale wystarczające do dziś.
- **RED** — unijna dyrektywa o urządzeniach radiowych. Od 1 sierpnia 2025 obejmuje też
 wymagania cyberbezpieczeństwa (normy EN 18031).
- **RFID** — bezstykowa karta zbliżeniowa; w ładowarkach używana do identyfikacji
 użytkownika i rozliczeń.
- **Runway** — „pas startowy”; ile czasu firma może funkcjonować z posiadaną gotówką.
- **Skrypt** — mały program uruchamiany na samym urządzeniu, pozwalający dodać logikę bez
 zmiany firmware'u.
- **SoC** (*System on Chip*) — układ scalony zawierający procesor, pamięć i radio w jednej
 kostce.
- **Tuya** — chińska platforma IoT dla producentów: moduły, chmura i aplikacja „pod klucz”.
- **Type 2** — europejski standard wtyczki do ładowania aut prądem przemiennym.
- **UART** — proste łącze szeregowe, którym moduł łączności rozmawia z mikrokontrolerem
 produktu.
- **V2G / V2H** — oddawanie prądu z auta do sieci (*vehicle-to-grid*) albo do domu
 (*vehicle-to-home*).
- **Wallbox** — ładowarka montowana na stałe do ściany.
- **WBR3** — moduł Wi-Fi i Bluetooth firmy Tuya na układzie BK7231N; ten, który dziś siedzi
 w ładowarkach AmperePoint.


## Kalendarz regulacyjny

| Data | Co zaczyna obowiązywać | Kogo dotyczy |
| --- | --- | --- |
| kwiecień 2024 | AFIR — rozporządzenie (UE) 2023/1804 wchodzi w życie bezpośrednio we wszystkich krajach Unii | cały rynek ładowania |
| 1 sierpnia 2025 | Wymagania cyberbezpieczeństwa w ramach dyrektywy RED (rozporządzenie delegowane (UE) 2022/30), normy EN 18031-1/2/3 | każde urządzenie z radiem, więc także ładowarka z Wi-Fi |
| 2025 | Akt delegowany (UE) 2025/656 (standardy techniczne) i rozporządzenie wykonawcze (UE) 2025/655 (obowiązki danych) | operatorzy i producenci |
| 8 stycznia 2026 | Nowo instalowane, publicznie dostępne punkty ładowania mają obsługiwać EN ISO 15118-2 | infrastruktura publiczna |
| 1 stycznia 2027 | Nowo instalowane punkty ładowania AC (Mode 3) mają obsługiwać EN ISO 15118-20 | operatorzy punktów **publicznie dostępnych**; klasyfikacja urządzeń przenośnych (Mode 2 czy Mode 3) do potwierdzenia |
| wdrożenia krajowe EPBD | Punkty ładowania w nowych budynkach i po głębokiej renowacji (>3 miejsca postojowe) zdolne do sterowanego ładowania; prekablowanie ≥50 % miejsc | inwestorzy i właściciele budynków, nie producenci sprzętu |
| 20 stycznia 2027 | Rozporządzenie maszynowe (UE) 2023/1230 zastępuje dyrektywę 2006/42/WE; brak okresu przejściowego z oboma aktami naraz | producenci maszyn (w rozmowie: bramy, paczkomaty) |

Do tego dochodzi data wskazana przez AmperePoint — *„połowa wymagań odchodzi, która wchodzi
od 1 stycznia”* — dotycząca, według AmperePoint, sprzętu montowanego na stałe.
**Nie zweryfikowałem, o który konkretnie akt chodzi**, i uważam, że to jest pierwsza rzecz do
sprawdzenia u prawnika, bo na tym opiera się cała przewaga wynikająca z przenośności produktu.

### Jak to czytać jako harmonogram działania

- **Dziś** — wymagania cyberbezpieczeństwa już obowiązują. To znaczy, że dokumentacja modułu
 ma znaczenie **teraz**, a nie za rok.
- **2026** — rok na przygotowanie się do stycznia 2027. Wymiana platformy mieści się w tym
 oknie z zapasem, jeśli ruszy w najbliższych miesiącach.
- **2027** — data istotna dla sprzedaży do punktów publicznie dostępnych i do budynków
 objętych EPBD. **Nie jest to data, po której nie wolno sprzedawać przenośnej ładowarki bez
 modemu PLC klientowi prywatnemu** — AFIR reguluje obowiązki operatorów, a nie warunki
 wprowadzania wyrobów do obrotu. To rozróżnienie decyduje o tym, czy projekt sprzętowy
 z modemem PLC jest koniecznością na 2027 rok, czy decyzją biznesową o wejściu w segment
 publiczny.


## Źródła

### Część pierwszoźródłowa

Wszystkie wypowiedzi podane kursywą pochodzą ze spotkań AmperePoint z przedstawicielami
Shelly. Przypisane są stronom rozmowy, a nie konkretnym osobom. W miejscach, w których nie
dało się pewnie ustalić nazwy własnej albo liczby, zaznaczam to w tekście.

### Regulacje i standardy

- AFIR, rozporządzenie (UE) 2023/1804 oraz terminy ISO 15118 dla punktów AC —
 opracowania Bender (`bender.de`), Smappee, Pionix; akt delegowany (UE) 2025/656
 i rozporządzenie wykonawcze (UE) 2025/655.
- OCPP, różnice 1.6 wobec 2.0.1 i udział wersji na rynku — Open Charge Alliance
 (`openchargealliance.org`), ChargeLab, Codibly.
- ISO 15118, Plug & Charge, komunikacja PLC wobec sygnalizacji PWM — materiały Vector
 (`vector.com`) i Renco.
- Dyrektywa RED, rozporządzenie delegowane (UE) 2022/30, normy EN 18031 i data
 1 sierpnia 2025 — CEN-CENELEC, BSI, SCHUTZWERK.
- Rozporządzenie maszynowe (UE) 2023/1230 i data 20 stycznia 2027 — Pilz, TÜV Rheinland.

### Firmy i produkty

- Wyniki Shelly Group / Allterco za 2025 r. (przychód 149,7 mln euro, DACH 62,0 mln euro,
 2,7 mln użytkowników chmury, prognoza 2026) — komunikaty spółki publikowane przez
 `webdisclosure.com`.
- Platforma Shelly X, moduły X0–X4 na ESP32-C3, tryb no-code i low-code — `x.shelly.com`.
- Ładowarka Shelly TopAC / Shelly Power EV-Charger EVE01-11R — materiały i fora branżowe
 (`shelly-forum.com`, `emobility.energy`).
- Wyniki Tuya Inc. za I kwartał 2025 r. (74,7 mln USD przychodu, marża brutto 48,5 %,
 ponad 1,4 mln deweloperów) — raport spółki, `ir.tuya.com`.
- Moduł Tuya WBR3 i układ BK7231N (120 MHz, 2 MB flash, 256 kB RAM, 2×8 pinów) —
 `developer.tuya.com`, dokumentacja modułu.
- AmperePoint, ładowarka Q11 (11 kW, Typ 2, IP66, 6–16 A, Wi-Fi) i ceny rynkowe —
 `amperepoint.pl`, Allegro, Ceneo.
- Plejd (ok. 116 mln USD przychodu, ponad 5 mln urządzeń, kraje nordyckie) — dane giełdowe
 i materiały spółki, opracowanie Memoori.

### Zastrzeżenie

Dane zewnętrzne sprawdziłem we wrześniu 2026 roku. Liczby spółek i terminy regulacyjne
zmieniają się — przed decyzjami inwestycyjnymi albo negocjacjami warto je potwierdzić
u źródła. Wszystkie wyliczenia oznaczone jako poglądowe (rachunek marż na półce, szacunek
wartości projektu) są moją arytmetyką na podstawie typowych parametrów rynkowych, a nie
danymi przedstawionymi na spotkaniu ani dokumentami AmperePoint.
