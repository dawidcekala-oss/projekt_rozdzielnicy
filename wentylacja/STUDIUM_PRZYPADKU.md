# Studium przypadku: od „nic nie pasuje" do odczytu danych z klimatyzatora

Zapis przebiegu diagnozy z pełnym ciągiem przyczynowo-skutkowym. Wersja skrócona znajduje
się w głównym raporcie PDF (rozdz. „Studium przypadku"); tu jest komplet szczegółów.
Daty: sierpień 2026. Sprzęt opisany w folderze [`plytki\`](plytki/).

---

## Etap 0 — punkt wyjścia i decyzja o sondzie

**Problem:** kasetony Gree GKH(12)BB-K6DNA3A/I mają być sterowane z Home Assistant,
ale żadne z posiadanych akcesoriów nie pasuje: moduł WiFi GRJWB04-J wymaga gniazda,
którego płyta GRZ4M-A3 nie ma, a bramka Modbus ZTS47/SMG-01 wymaga gniazda COM-BMS —
którego ta płyta również nie ma.

**Ustalenie kluczowe:** na płycie jest wolny port **COM-MANUAL** (4 piny: masa, +12 V
i dwużyłowa magistrala danych RS485) przeznaczony dla przewodowego pilota. Protokół tej
magistrali jest częściowo rozpracowany publicznie (1200 bodów, ramki zaczynające się od
`7E 7E`, suma kontrolna XOR). Decyzja: **zanim cokolwiek kupimy, sprawdzamy sondą własnej
roboty, czy jednostka odpowie na ten protokół.**

**Rozwiązanie sprzętowe bez zakupów:** analiza wnętrza „bezużytecznej" bramki pokazała,
że nie ma w niej procesora — to czysty konwerter UART↔RS485. Bramka została przerobiona
na interfejs sondy, a jej rolę mózgu przejęła płytka WeMos D1 R1 (ESP8266) z firmware
wysyłającym co 3 sekundy ramkę-zapytanie i nasłuchującym magistrali (to, co wówczas
braliśmy za odpowiedzi, okazało się cyklicznym rozgłoszeniem jednostki — patrz Etap 6), z logiem dostępnym
zdalnie przez WiFi (rozgłoszenia UDP + serwer telnet).

---

## Etap 1 — pierwsze podejście polowe: totalna cisza

Sonda zamontowana przy jednostce nadawała poprawnie (własny log), ale przez wiele sesji
nie odebrała **ani jednego bajta**. Pomiary przy jednostce dawały niefizyczne wyniki
(−7 V na liniach danych względem masy — niemożliwe dla nadajnika pracującego od 0 do 5 V),
co wskazywało, że mierzymy „pływające", niepodłączone przewody.

**Wniosek metodyczny, który odblokował całość:** przenieść diagnostykę z drabiny na
biurko i rozłożyć tor sygnału na odcinki, weryfikując każdy z osobna. Do tego powstał
drugi firmware — **tester biurkowy** — który zamiast ramek generuje powolne, mierzalne
zwykłym multimetrem stany (zmiana co 1 s) i raportuje stan wejścia odbiorczego co sekundę.

---

## Etap 2 — przyczyna nr 1: mylące opisy pinów WeMos D1 R1

Test ciągłości (z użyciem programatora ALIENTEK jako biernego rozgałęźnika do wtyczki JST —
patrz [`plytki\flasher_alientek_minipro.md`](plytki/flasher_alientek_minipro.md)) wykazał,
że pigtail i dzielnik napięcia są sprawne. Analiza zdjęcia płytki ujawniła natomiast, że
**przewody sygnałowe siedziały na pinach `RX←D0`/`TX→D1`** (sprzętowy port szeregowy,
współdzielony z USB), a firmware nadaje i słucha na GPIO12/GPIO14 — czyli na pinach
opisanych `D12/MISO/D6` i `D13/SCK/D5`, które były **puste**.

**Przyczyna źródłowa:** płytka D1 R1 ma na każdym pinie 2–3 nazwy naraz i część nazw
powtórzona w dwóch miejscach listwy. **Skutek:** sonda fizycznie nigdy nie wysłała ramki
do bramki. **Rozwiązanie:** przełożenie przewodów na piny właściwe wg pełnego nadruku.

---

## Etap 3 — przyczyna nr 2: bramka bez automatu kierunku

Po poprawieniu pinów tester wykazał, że bramka **nadal nie wystawia żadnego sygnału**
na blaszki wyjściowe (stała różnica ~0 V zamiast przełączania). Trop: transceiver na
płytce bramki to układ 14-nóżkowy (rodzina MAX13089), który **nie ma automatycznego
przełączania kierunku nadawanie/odbiór** — w oryginale sterowała tym płyta główna
klimatyzatora przez dwie dodatkowe żyły złącza CN2: **RXP** (włącznik odbiornika,
aktywny przy masie) i **TXP** (włącznik nadajnika). U nas obie wisiały w powietrzu,
więc bramka była równocześnie **niema i głucha** — to wyjaśniło każdy dotychczasowy objaw,
łącznie z fantomowymi −7 V (niepodłączony, pływający tor).

**Rozwiązanie:** RXP (żyła biała) na stałe do masy; TXP (żyła żółta) pod kontrolę
sondy — pin `D11/MOSI/D7`, stan wysoki tylko na czas wysyłania ramki. Firmware sondy
był na to gotowy od początku (identyczny mechanizm jak w popularnych modułach MAX485).

---

## Etap 4 — przyczyna nr 3: opisy TXD/RXD „od strony klimatyzatora"

Z włącznikami kierunku pod kontrolą bramka wciąż milczała. Ostatnia zmienna: żyły danych.
Okazało się, że opisy `TXD`/`RXD` na laminacie bramki są **z perspektywy płyty
klimatyzatora**: „TXD" to wejście bramki (dane, które płyta nadaje), „RXD" — jej wyjście.
Podłączenie intuicyjne („nasz TX do ich RX") było więc odwrotne do właściwego.

**Rozwiązanie:** zamiana dwóch końcówek w złączu krosowym. Natychmiast po niej pin
kierunku zaczął realnie przełączać odbiornik — pierwszy obserwowalny „znak życia" bramki.

---

## Etap 5 — pełna weryfikacja biurkowa

Po złożeniu wszystkich trzech poprawek tester potwierdził każdy tor niezależnie:

| Test | Wynik |
|---|---|
| nadawanie: multimetr na blaszkach A–B przy przełączającym się sygnale | **±4,8 V, przeskok co 1 s** — nadajnik sprawny |
| ciągłość blaszek | X1↔X3 zwarte (linia A), X2↔X4 zwarte (linia B) — pary przelotowe |
| odbiór: wstrzyknięcie 5 V / masy wprost na blaszki | wejście odbiorcze podąża za polaryzacją — odbiornik sprawny |

Sonda wróciła na jednostkę **bez żadnej zmiany w kodzie** — wyłącznie z poprawionym
okablowaniem.

---

## Etap 6 — przełom: pierwsze odebrane dane

Pierwsza sesja po naprawie: **na magistrali pojawiły się ramki jednostki.**
Wyglądało to wtedy jak odpowiedź na każde nasze zapytanie i tak zostało zapisane —
dopiero faza 2 (25.08) pokazała, że to złudzenie: jednostka **nadaje sama z siebie**,
równo co 800 ms, a sonda była wyłącznie **biernym podsłuchem**. Dowód rozstrzygający:
po całkowitym wyłączeniu naszych zapytań ruch na magistrali płynie dalej bez zmian.
Szczegóły i pełna lista prób nawiązania dialogu (ponad 1100 wariantów ramek, zero
odpowiedzi) — `FAZA2_USTALENIA.pdf`.
Z 286 odebranych ramek 261 (91%) przeszło kontrolę sumy XOR; reszta to ucięte odbiory
(znany koszt programowego UART przy pracującym WiFi). Kanoniczna ramka rozgłoszeniowa jednostki (nadawana cyklicznie co 800 ms, niezależnie
od naszych zapytań):

```
7E 7E FF 40 11 17 09 30 83 7C 7C 0E 04 00 00 01 00 10 00 00 00 00 00 00 00 00 23 02 39
```

- `FF` = nadawca: jednostka wewnętrzna; `40` = adresat z puli „sterownik centralny",
- `17` = długość części danych (23 bajty), ostatni bajt `39` = suma XOR (poprawna),
- bajt `23` przed końcówką **nie jest nastawą** — hipoteza „23 °C jak na wyświetlaczu"
  została obalona w fazie 2: ten bajt jest **stały** we wszystkich 228 673 przeanalizowanych
  ramkach, niezależnie od nastawy, trybu i tego, czy jednostka pracuje.

W całym rozgłoszeniu `FF→40` zmieniają się tylko **cztery pola**:

| Bajt | Znaczenie |
|---|---|
| `[9]` | temperatura powietrza powrotnego (czujnik ROOM, przy suficie) |
| `[10]` | temperatura wymiennika (czujnik TUBE) |
| `[12]` | rzeczywisty bieg wentylatora: 00 stoi / 04 niski / 02 średni / 01 wysoki |
| `[14]` | klapy nawiewu: 0x80 otwarte / 00 zamknięte |

**Nastaw (temperatura zadana, tryb, wł./wył.) w tym rozgłoszeniu nie ma.** Siedzą w ramce
`FF→00`, której jednostka nie wysyła, dopóki sterownik pod adresem 00 nie jest zarejestrowany.
Przelicznik temperatury: **surowy bajt minus 100 = stopnie Celsjusza**.

Pilot podczerwieni **działa równolegle** z sondą — co dziś już nie dziwi: sonda tylko
słucha magistrali, jednostka nie rejestruje jej jako sterownika i nie ma czego blokować.

---

## Incydent: próba zasilenia sondy z pinu +12 V portu (opis w raporcie)

Osobny, cenny wynik uboczny: podanie żyły +12 V z portu COM-MANUAL na wejście `VIN`
WeMosa **uniemożliwiało start całego klimatyzatora** (dwukrotnie zweryfikowane; 230 V na
zasilaniu obecne). Wyjaśnienie mechanizmu — raport PDF, rozdz. „Incydent zasilania".
Wniosek praktyczny na tamtym etapie: **sondę zasilamy z własnego zasilacza 5 V,
nie wprost z pinu +12 V portu.**

**Stan aktualny:** to obejście, nie rozwiązanie docelowe. Powstał układ obniżający
(`+12 V → R → węzeł z kondensatorami → VIN`), w którym wersja z **R = 47 Ω zawiodła**
w teście polowym (przegrzanie rezystora, brak startu sondy). Wartość obowiązująca to
**R = 25–28 Ω** (np. 4×100 Ω równolegle) i **3×100 µF** — obliczenia i errata
w `ZASILANIE_OBLICZENIA.pdf`. Montaż użytkownik odłożył, sprawa niezamknięta.
Stawka jest wyższa niż wygoda: jedna z hipotez fazy 2 mówi, że jednostka wykrywa
obecność sterownika **po poborze prądu z linii +12 V** — jeśli się potwierdzi, zasilanie
z portu okaże się **warunkiem komunikacji**.

---

## Lekcje na przyszłość (skrót)

1. Przy ciszy na magistrali najpierw podziel tor na odcinki i zweryfikuj każdy przy biurku —
   jedna sesja z multimetrem i testerem dała więcej niż tydzień prób przy jednostce.
2. Nazwy na laminacie bywają z perspektywy **drugiej strony** kabla (TXD/RXD!), a piny
   płytek klonów — opisane wieloznacznie. Ufaj pomiarom, nie napisom.
3. Transceiver RS485 bez automatu kierunku = trzy sygnały do ogarnięcia (dane TX, dane RX,
   klucz kierunku) plus włącznik odbiornika. Wszystkie cztery muszą być obsłużone.
4. Pomiar dający wynik „niefizyczny" (−7 V) to niemal zawsze pomiar pływającego przewodu —
   szukaj przerwy, nie egzotycznych wyjaśnień.
