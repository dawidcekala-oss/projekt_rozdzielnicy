# Komputer pod biurowy Home Assistant — rozpoznanie rynku (2026-08-31)

Ceny i dostępność sprawdzone tego dnia bezpośrednio na stronach ofert.

**Uwaga o trwałości linków.** Inaczej niż przy liście elementów, gdzie sprzedawcy mieli
po kilkadziesiąt sztuk na stanie, **sprzęt używany to najczęściej pojedyncze egzemplarze**.
Konkretne oferty poniżej traktuj jako dowód, że taki sprzęt jest w tej cenie osiągalny —
a nie jako gwarancję, że będą dostępne za tydzień. Podaję też, czego szukać, gdy znikną.

---

## 1. Najpierw rozstrzygnięcie: po co ten wyświetlacz

To pytanie decyduje o całym zakupie, więc rozdzielam je na dwie różne role, bo w Twoim
pytaniu są zlepione w jedno:

| Rola | Gdzie stoi | Czego naprawdę wymaga |
|---|---|---|
| **konsola serwisowa** | przy komputerze, w kącie | prawie nic — wystarczy złącze HDMI i dowolny monitor podpięty raz na pół roku |
| **panel biura** | na ścianie, tam gdzie ludzie | ekran dotykowy, ale **nie musi być podłączony do serwera** |

Serwer HA obsługuje się przez przeglądarkę. Wyświetlacz przy nim nie jest do niczego
potrzebny w codziennej pracy — przydaje się raz, przy instalacji, i potem gdy coś nie
wstaje. Panel na ścianie to zupełnie inne urządzenie: ma wisieć tam, gdzie stoisz, a nie
tam, gdzie leży serwer.

**Dlatego rekomendacja jest taka:** kup komputer z wyjściem HDMI (każdy z poniższych je ma)
i podłącz do niego jakikolwiek monitor przy instalacji. Ekran dotykowy kupuj osobno
i dopiero wtedy, gdy będziemy wieszać panel — wtedy będzie wiadomo, jaka przekątna i gdzie.
Poniżej i tak podaję opcje, gdybyś chciał wziąć od razu.

---

## 2. Dlaczego nie Raspberry Pi

Miałeś rację, że standardowe RPi to za mało — ale powód jest inny, niż zwykle się podaje.

Nie chodzi tylko o wydajność. **Chodzi o kartę pamięci.** Home Assistant zapisuje stan
encji do bazy danych non stop — w naszym przypadku pięć encji odświeżanych co 15 sekund,
a docelowo znacznie więcej. Karta microSD tego nie znosi i po roku–dwóch pada. To najczęstsza
przyczyna śmierci domowych instalacji HA.

Do tego dochodzi rachunek, który wypada nieoczekiwanie:

| | Raspberry Pi 5 8 GB | Używany mini-PC i5 |
|---|---|---|
| koszt startu | ~450 zł + zasilacz + obudowa + dysk ≈ **700 zł** | **~600 zł**, komplet |
| wydajność | odniesienie | **ok. 3× więcej** rdzeni i mocy |
| dysk | microSD lub USB | **NVMe SSD w środku** |
| RAM później | wlutowana, nie zwiększysz | 2 gniazda, do 32–64 GB |
| pobór | ~4 W | ~8–12 W |
| różnica w prądzie | — | **ok. 60 zł/rok** |

Za sześćdziesiąt złotych rocznie dostajesz trzykrotnie mocniejszą maszynę, dysk, który nie
umiera, i możliwość dołożenia pamięci. Raspberry przestaje mieć sens.

---

## 3. Rekomendacja: poleasingowy mini-PC biznesowy „1 litr"

Klasa sprzętu: **Dell OptiPlex Micro**, **Lenovo ThinkCentre Tiny**, **HP EliteDesk Mini** —
metalowe pudełka wielkości książki, projektowane do pracy ciągłej w biurach, z procesorami
o obniżonym poborze mocy (końcówka **T** w nazwie, np. i5-8500**T**). Firmy wymieniają je
masowo, więc rynek wtórny jest głęboki i tani.

Docelowa specyfikacja: **i5 ósmej generacji, 8 GB RAM, 256 GB SSD, ok. 600 zł.**

Dlaczego akurat to:

- **sześć rdzeni** — zapas na wszystko, co dołożysz później (nagrywanie z kamer, baza
  danych, druga instancja do testów);
- **8–12 W na biegu jałowym** — ok. 100 zł prądu rocznie przy pracy ciągłej;
- **cicho** — te obudowy projektowano do pracy przy biurku;
- **SSD NVMe w środku**, gniazdo na drugi dysk 2,5", dwa sloty RAM;
- **HDMI + DisplayPort** — konsola serwisowa bez kombinowania;
- w cenie zwykle licencja Windows, którą i tak skasujesz.

### Znalezione oferty

| Model | Specyfikacja | Cena | Na stanie |
|---|---|---|---|
| [HP EliteDesk 800 G4 DM](https://allegro.pl/produkt/komputer-hp-elitedesk-800-g4-dm-i5-8500-8gb-256gb-nvme-wifi-win11-a1259-dfe16c12-c84e-4383-86a5-f71247435953) | i5-8500, 8 GB, 256 GB NVMe, WiFi | **595 zł** | 1 szt. |
| [Dell OptiPlex 3060 Micro](https://allegro.pl/produkt/miniaturowy-komputer-dell-optiplex-3060-micro-i5-8500t-8-256gb-wifi-w11p-cd94d22d-594a-4402-916f-a4319890d040) | i5-8500T, 8 GB, 256 GB, WiFi | **599 zł** | 1 szt. |
| [HP EliteDesk 800 G4 mini](https://allegro.pl/produkt/hp-elitedesk-800-g4-mini-intel-core-i5-8-gb-128-gb-w11p-a30ce255-7233-4911-86cb-ab9427e345a1) | i5, 8 GB, 128 GB, powystawowy | **559 zł** | 2 szt. |
| [Dell OptiPlex 3050 Micro](https://allegro.pl/produkt/mini-pc-dell-optiplex-3050-i5-7500t-4gb-128ssd-win11-office-hdmi-dp-99e8b670-667f-4309-a377-530cf7cb9e32) | i5-7500T, **4 GB**, 128 GB | **349 zł** | **47 szt.** |

```
HP EliteDesk 800 G4 DM  https://allegro.pl/produkt/komputer-hp-elitedesk-800-g4-dm-i5-8500-8gb-256gb-nvme-wifi-win11-a1259-dfe16c12-c84e-4383-86a5-f71247435953
Dell OptiPlex 3060      https://allegro.pl/produkt/miniaturowy-komputer-dell-optiplex-3060-micro-i5-8500t-8-256gb-wifi-w11p-cd94d22d-594a-4402-916f-a4319890d040
HP EliteDesk 800 G4     https://allegro.pl/produkt/hp-elitedesk-800-g4-mini-intel-core-i5-8-gb-128-gb-w11p-a30ce255-7233-4911-86cb-ab9427e345a1
Dell OptiPlex 3050      https://allegro.pl/produkt/mini-pc-dell-optiplex-3050-i5-7500t-4gb-128ssd-win11-office-hdmi-dp-99e8b670-667f-4309-a377-530cf7cb9e32
```

Ostatnia pozycja jest tu **jako ostrzeżenie, nie jako oszczędność** — patrz niżej.

### Pułapka, w którą łatwo wpaść

Kusi wersja za 349 zł i dołożenie pamięci. Sprawdziłem, ile kosztuje pamięć:
**8 GB SO-DIMM DDR4 to 175–195 zł.**

| Wariant | Rachunek | Razem |
|---|---|---|
| tańszy komputer + pamięć | 349 zł + 180 zł | **529 zł**, 7. generacja, 128 GB dysku |
| od razu 8 GB | 599 zł | **599 zł**, 8. generacja, 256 GB dysku |

Siedemdziesiąt złotych różnicy za nowszą generację, dwa razy większy dysk i brak grzebania
w środku. **Nie kupuj wersji 4 GB z zamiarem rozbudowy** — to się nie opłaca. Jeśli
natrafisz na egzemplarz z 16 GB w cenie do ok. 750 zł, bierz go bez wahania: przy takich
cenach pamięci to okazja.


---

## 3a. Wersja tańsza — i to ona jest teraz rekomendowana

Sześćset złotych to faktycznie za dużo jak na to zadanie. Zejście o dwie generacje
procesora obniża cenę do **ok. 400 zł**, a Home Assistant tej różnicy nie zauważy.

Co się traci: **cztery rdzenie zamiast sześciu** i mniejszy dysk. Co zostaje bez zmian:
pobór prądu (ta sama klasa 35 W, na biegu jałowym 8–10 W), ta sama metalowa obudowa
projektowana do pracy ciągłej, ten sam SSD w środku, te same dwa gniazda pamięci.
Cztery rdzenie to wciąż **kilka razy więcej niż Raspberry Pi**.

### Rekomendacja

**[Lenovo ThinkCentre M710q Tiny — i5-7500T, 8 GB, 128 GB NVMe, Win 11 Pro — 399 zł](https://allegro.pl/produkt/tani-pc-lenovo-m710q-tiny-i5-7500t-8gb-128gb-nvme-w11pro-dp-poleasingowy-398973cc-3ac7-4676-b17b-6a4eeccbda71)**

`https://allegro.pl/produkt/tani-pc-lenovo-m710q-tiny-i5-7500t-8gb-128gb-nvme-w11pro-dp-poleasingowy-398973cc-3ac7-4676-b17b-6a4eeccbda71`

Dlaczego akurat ta oferta, a nie inna w tej samej cenie:

- **12 sztuk na stanie** — to nie jest pojedynczy egzemplarz, który zniknie do jutra;
  sprzedawca prowadzi regularny obrót poleasingowy, więc oferta jest stabilna;
- **12 miesięcy gwarancji** wprost w treści oferty — sprawdziłem, jest napisane;
- **dysk NVMe**, nie SATA — szybszy i bez kabli w środku;
- **i5-7500T**, czyli generacja nowsza niż w konkurencyjnych ofertach po 395 zł;
- zasilacz i WiFi w komplecie.

### Zapasowy wybór, gdyby tamta zniknęła

| Model | Specyfikacja | Cena | Na stanie |
|---|---|---|---|
| [HP EliteDesk 800 G3 Tiny](https://allegro.pl/produkt/hp-elitedesk-800-g3-tiny-i5-6500t-8gb-128gb-ssd-win11-e9645591-1b13-4f2a-8ade-699520360f7a) | i5-6500T, 8 GB, 128 GB SSD | 395 zł | **16 szt.** |
| [HP EliteDesk 800 G3 Mini](https://allegro.pl/produkt/komputer-hp-elitedesk-800-g3-mini-i5-7500-8gb-128gb-ssd-wifi-win11-a1403-d339f313-62bc-4b83-b1a5-c5d1b9b12633) | i5-7500, 8 GB, 128 GB SSD, WiFi | 399 zł | 3 szt. |
| [HP EliteDesk 800 G3 DM](https://allegro.pl/produkt/hp-elitedesk-800-g3-dm-intel-core-i5-6500t-256gb-ssd-8gb-ram-87805ca8-a1af-41aa-9b4d-ded3789d0fa5) | i5-6500T, 8 GB, **256 GB SSD** | 399 zł | 1 szt. |

```
HP 800 G3 Tiny  https://allegro.pl/produkt/hp-elitedesk-800-g3-tiny-i5-6500t-8gb-128gb-ssd-win11-e9645591-1b13-4f2a-8ade-699520360f7a
HP 800 G3 Mini  https://allegro.pl/produkt/komputer-hp-elitedesk-800-g3-mini-i5-7500-8gb-128gb-ssd-wifi-win11-a1403-d339f313-62bc-4b83-b1a5-c5d1b9b12633
HP 800 G3 DM    https://allegro.pl/produkt/hp-elitedesk-800-g3-dm-intel-core-i5-6500t-256gb-ssd-8gb-ram-87805ca8-a1af-41aa-9b4d-ded3789d0fa5
```

### Czy 128 GB dysku wystarczy

Tak. Home Assistant OS zajmuje ok. 32 GB, reszta to baza historii, która przy naszej
skali rośnie o rząd wielkości wolniej, niż pozwala ten dysk. Gdybyśmy kiedyś doszli do
nagrywania z kamer, w obudowie Tiny jest **miejsce na drugi dysk 2,5"** — dołożysz go
wtedy za stówkę, zamiast płacić dziś za pojemność, której nie używasz.

### Czego unikać w tym przedziale cenowym

Przy 350 zł zaczynają się oferty, które wyglądają podobnie, a nie są:

- **Celeron zamiast i5** (M720q za 339–459 zł) — dwa rdzenie, bez zapasu;
- **dysk 1 TB SATA** za dopłatą — w tych obudowach to zwykle talerzowy dysk 2,5":
  hałasuje i pada w pracy ciągłej, czyli dokładnie odwrotnie, niż chcemy;
- **oferty „tylko na części"** — trafiłem na taką za 249 zł;
- **martwe oferty z absurdalną ceną** — jedna pozycja za „53 zł" okazała się wyprzedana,
  sprawdziłem.
---

## 4. Alternatywa warta rozważenia: używany laptop biznesowy

Ta opcja ma zaletę, która akurat u Ciebie znaczy więcej niż gdzie indziej.

**Bezpieczniki Twojego biura są poza biurem.** Zanik napięcia oznacza twarde odcięcie
zasilania serwera w trakcie zapisu do bazy — najprostsza droga do uszkodzonej instalacji.
Laptop ma **wbudowany zasilacz awaryjny**: bateria przetrzyma zanik i pozwoli systemowi
zamknąć się porządnie. Dodatkowo ma ekran i klawiaturę, więc konsola serwisowa odpada
z listy zakupów.

| Za | Przeciw |
|---|---|
| bateria = UPS w cenie | bateria po latach puchnie i trzeba ją wymienić lub wyjąć |
| ekran i klawiatura w zestawie | trudniej zamontować na ścianie czy w szafce |
| pobór podobny, przy zgaszonym ekranie nawet niższy | trzeba wyłączyć usypianie po zamknięciu klapy |

Znalezione:

| Model | Specyfikacja | Cena |
|---|---|---|
| [Dell Latitude 7480](https://allegro.pl/produkt/laptop-dell-latitude-7480-i5-6300u-8-gb-256-gb-ssd-14-1920x1080-8ea61743-704b-47b5-9eb7-e6741d933983) | i5, 8 GB, 256 GB, 14" FHD | **379 zł** |
| [Dell Latitude 7480](https://allegro.pl/produkt/laptop-dell-latitude-7480-14-intel-core-i5-16-gb-256-gb-czarny-5dfb9519-097a-468f-8ea6-15c5cdb388f4) | i5, **16 GB**, 256 GB, 14" | **549 zł** |

```
Latitude 7480  8 GB  https://allegro.pl/produkt/laptop-dell-latitude-7480-i5-6300u-8-gb-256-gb-ssd-14-1920x1080-8ea61743-704b-47b5-9eb7-e6741d933983
Latitude 7480 16 GB  https://allegro.pl/produkt/laptop-dell-latitude-7480-14-intel-core-i5-16-gb-256-gb-czarny-5dfb9519-097a-468f-8ea6-15c5cdb388f4
```

Uwaga: to procesory serii **U** (dwurdzeniowe, mobilne) — wyraźnie słabsze od sześciordzeniowego
i5-8500T z mini-PC. Do samego HA w zupełności wystarczą; do nagrywania z kamer już nie.

---

## 5. Czego **nie** polecam

**Nowy mini-PC z procesorem N100.** Technicznie ładny — 6–10 W, cichy, gwarancja. Ale ceny
na Allegro zaczynają się od **1119 zł** i sięgają 2000 zł, czyli dwa do trzech razy więcej
niż używany i5, przy porównywalnej wydajności. Sens ma tylko wtedy, gdy zależy Ci na
gwarancji i nowym sprzęcie.

**Lenovo ThinkCentre M720q w tanich wariantach.** Wyglądają atrakcyjnie (339–459 zł), ale
to egzemplarze z **Celeronem** G4900T/G4930T — dwa rdzenie, bez zapasu na cokolwiek.
Sama obudowa Tiny jest świetna; szukaj wariantów z i5, nie z Celeronem.

---

## 6. Wyświetlacze — jeśli chcesz od razu

**Ważne odkrycie przy sprawdzaniu.** Najtańszy dotykowy ekran, na jaki trafiłem — Mimo
UM-1080CP-B, 10,1", 1280×800, **188 zł, 79 sztuk na stanie** — przesyła obraz i dotyk
**przez USB, nie HDMI**. Na Windowsie działa dobrze; pod Linuksem wymaga sterownika
DisplayLink i bywa kapryśny. Skoro serwer będzie linuksowy, **to nie jest bezpieczny wybór
na panel**, choć cena kusi.

| Ekran | Parametry | Cena | Uwaga |
|---|---|---|---|
| [HMTECH 10", dotykowy](https://allegro.pl/produkt/hmtech-ekran-dotykowy-10-do-raspberry-1024x600-monitor-hdmi-c1f35378-4dfa-4270-a8b9-e66476873aab) | 1024×600, **HDMI** | 299 zł | bezpieczny wybór pod Linuksa |
| [10,1" IPS dotykowy](https://allegro.pl/produkt/10-1-monitor-dotykowy-ips-lcd-dla-raspberry-pi-i-systemu-windows-1024600-11499d7b-3c44-4c07-8c7d-2d568eb6bdec) | 1024×600, HDMI | 300 zł | to samo, inny sprzedawca |
| [Mimo UM-1080CP-B](https://allegro.pl/produkt/monitor-lcd-mimo-um-1080cp-b-10-1-1280-x-800-px-ips-pls-e4e4385b-30ef-41d5-ba0f-92e49677e000) | 1280×800 IPS, **USB** | 188 zł | lepsza matryca, ale USB — pod Linuksa ryzykowne |

```
HMTECH 10 HDMI    https://allegro.pl/produkt/hmtech-ekran-dotykowy-10-do-raspberry-1024x600-monitor-hdmi-c1f35378-4dfa-4270-a8b9-e66476873aab
10,1 IPS HDMI     https://allegro.pl/produkt/10-1-monitor-dotykowy-ips-lcd-dla-raspberry-pi-i-systemu-windows-1024600-11499d7b-3c44-4c07-8c7d-2d568eb6bdec
Mimo UM-1080CP-B  https://allegro.pl/produkt/monitor-lcd-mimo-um-1080cp-b-10-1-1280-x-800-px-ips-pls-e4e4385b-30ef-41d5-ba0f-92e49677e000
```

Szczerze: **na panel ścienny tańszy i wygodniejszy będzie używany tablet z Androidem**
przyklejony do ściany — ma ekran, dotyk, WiFi i zasilanie jednym kablem, a HA otwiera się
w przeglądarce. Wróćmy do tego przy panelu; nie ma sensu kupować dziś w ciemno.

---

## 7. Co ten komputer zmieni oprócz mocy

Jedna rzecz z dzisiaj wymaga sprostowania. Kazałem Ci otworzyć „dodatek File editor",
a Ty słusznie zapytałeś, co ja w ogóle opowiadam — bo **Twoja instalacja go nie ma**.
Home Assistant w Dockerze, tak jak stoi teraz na laptopie, **nie obsługuje dodatków**.

Na dedykowanym komputerze zainstalujemy **Home Assistant OS**, czyli pełną wersję
z nadzorcą. Wtedy dodatki są dostępne i moja tamta instrukcja przestaje być bez sensu:
edytor plików, terminal, kopie zapasowe, udział sieciowy — wszystko klikalne z panelu.

Przenosiny są proste: kopia zapasowa z obecnej instalacji, odtworzenie na nowej. Encje,
historia i integracje przechodzą razem z nią.

---

## 8. Na co patrzeć przy zakupie używanego

1. **Procesor z „T" na końcu** (i5-8500T, i5-7500T) — wersja o obniżonym poborze, ważna
   przy pracy ciągłej. Wersja bez „T" też zadziała, tylko grzeje się bardziej.
2. **8 GB minimum**, 16 GB jeśli premia poniżej ~150 zł.
3. **SSD, nie dysk talerzowy** — talerzowy w pracy ciągłej hałasuje i pada.
4. **WiFi w opisie** — przydatne, ale i tak podłączymy kablem; sieć przewodowa nie zrywa.
5. **Zasilacz w zestawie** — te maszyny mają zasilacze zewnętrzne z nietypowymi wtykami,
   dokupienie osobno bywa kłopotliwe.
6. Sprzedawcy poleasingowi zwykle dają gwarancję 12 miesięcy — sprawdź, czy jest.

## 9. Podsumowanie kosztów

| Pozycja | Kwota |
|---|---|
| **mini-PC i5, 8 GB, 128 GB (rekomendacja)** | **ok. 400 zł** |
| mini-PC i5 6-rdzeniowy, 8 GB, 256 GB | ok. 600 zł |
| prąd przy pracy ciągłej | ok. 100 zł/rok |
| ekran dotykowy (opcjonalnie, później) | ok. 300 zł |

**Bierz Lenovo ThinkCentre M710q Tiny z i5-7500T i 8 GB za 399 zł**, bez ekranu na teraz.
Dwanaście sztuk na stanie, rok gwarancji, dysk NVMe. Do Home Assistanta to z zapasem
wystarczy, a zaoszczędzone dwieście złotych pokrywa dwa lata prądu.

Wersję sześciordzeniową za 600 zł rozważ tylko wtedy, gdy z góry wiesz, że dojdzie
nagrywanie z kamer. Jeśli ważniejsza jest odporność na zaniki napięcia — laptop Latitude
7480 z 16 GB za 549 zł ma baterię i ekran w cenie.
