# Faza 2 — ustalenia (2026-08-25)

## Odkrycie, które zmienia obraz projektu

**Jednostka nie odpowiada na zapytania — ona sama nadaje.** Po wyłączeniu naszych zapytań
ruch na magistrali trwa dalej: równo **co 800 ms** jednostka wysyła ramkę do adresu `40`.
Dotychczasowa „komunikacja dwukierunkowa" była w rzeczywistości **biernym podsłuchem**
tego rozgłoszenia.

Rytm 800 ms jest zegarowo równy (min 799, max 811 ms w pomiarze), ramka zajmuje 241 ms,
więc między ramkami zostaje ~560 ms ciszy.

## Co niesie rozgłoszenie (analiza 228 673 ramek)

```
7E 7E FF 40 11 17 | 09 30 83 [9] [10] 0E [12] 00 [14] 01 00 10 00×8 23 02 | XOR
```

| Bajt | Znaczenie | Zakres |
|---|---|---|
| `[9]` | temperatura pomieszczenia | 0x77–0x7C |
| `[10]` | temperatura wymiennika | 0x65–0x7C |
| `[12]` | bieg rzeczywisty wentylatora | 00 stoi / 04 niski / 02 średni / 01 wysoki |
| `[14]` | klapy nawiewu | 0x80 otwarte / 00 zamknięte |

Wszystkie pozostałe bajty są **stałe** w całej historii pomiarów. Nastaw (temperatura
zadana, tryb, wł./wył., bieg zadany) w tym rozgłoszeniu **nie ma i nigdy nie było**.

## Co przetestowano bez skutku (jednostka nie odpowiedziała ANI RAZU)

| Próba | Zakres |
|---|---|
| ramka zapytania wg dokumentacji XK19 | wielokrotnie, także potrojona |
| pełny przemiat bajtu rozkazu | wszystkie 256 wartości |
| przemiat pól nagłówka: nadawca / adresat / klasa | 768 kombinacji |
| podszycie się pod sterownik centralny (`40→FF`) | kilka wariantów treści |
| lustrzane odbicie własnej ramki jednostki | — |
| ramki krótkie (len 01, 02) i długie (len 15, 17) | — |
| precyzyjne taktowanie bitów (bez zakłóceń WiFi) | firmware v4 |
| wydłużone trzymanie klucza nadawania | 3–5 ms po ostatnim bajcie |
| synchronizacja do okna po ramce jednostki | 30 / 60 / 150 / 300 ms |
| stan czuwania jednostki (wyłączona pilotem) | — |

## Diagnoza elektryczna: tor nadawania jest sprawny

- polaryzacja A/B poprawna (dowód: bezbłędnie odbieramy ramki jednostki — przy odwrotnej
  polaryzacji odbiór byłby śmieciem),
- nadajnik daje ±4,8 V różnicowo (pomiar multimetrem),
- suma kontrolna ramki wzorcowej przeliczona ręcznie bajt po bajcie — zgodna,
- brak echa własnych ramek to normalne: płytka bramki wycisza odbiornik na czas nadawania
  (zaobserwowane już w testach biurkowych).

**KOREKTA (2026-08-25, po testach A/B): tego wniosku NIE DA SIĘ obronić.**
Pomiar ±4,8 V wykonano **przy biurku, na luźnych blaszkach** — nie na magistrali obciążonej
przez klimatyzator. Dwa testy zdalne miały to rozstrzygnąć i **oba wyszły nierozstrzygnięte**:

- test A/B (te same ramki z kluczem nadawania podniesionym vs opuszczonym): **brak różnicy**
  w zakłóceniu odbioru (11,9% vs 11,0%) — ale test jest obarczony wadą, bo firmware blokuje
  przerwania na czas nadawania i odbiornik głuchnie tak czy inaczej;
- test echa (przerwania włączone, szukamy własnej ramki w odbiorze): **0/25 przy kluczu
  podniesionym i 0/25 przy opuszczonym** — nie słyszymy siebie w żadnym przypadku.

Zostają więc dwie równie prawdopodobne możliwości i **nie wiemy, która zachodzi**:
1. nadajemy poprawnie, a jednostka ignoruje niezarejestrowany sterownik, albo
2. **nasze bajty w ogóle nie wychodzą na magistralę** po podłączeniu do klimatyzatora —
   wtedy cała hipoteza o „warstwie rejestracji" jest bezprzedmiotowa, a problem jest sprzętowy.

**Test rozstrzygający wymaga miernika przy jednostce** (2 minuty, opis niżej).

## Co ustaliło rozpoznanie cudzych implementacji (5 równoległych agentów)

Przeszukano GitHub, ESPHome, fora HVAC, dokumentacje bramek Modbus i zrzuty magistrali.
Najważniejsze:

- **Nasza interpretacja ramki została potwierdzona niezależnie.** Zrzut z innego egzemplarza
  (repozytorium `maxim-smirnov/gree-wired-proto`) ma tę samą ramkę `FF→40` i pokrywa się
  z nami pozycyjnie: temperatura pomieszczenia, temperatura wymiennika, bieg wentylatora
  i klapy leżą dokładnie tam, gdzie je znaleźliśmy. Algorytm sumy kontrolnej też się zgadza.
- **Nastawy są w ramce `FF→00`** (do sterownika przewodowego), której jednostka **nie wysyła,
  dopóki sterownik pod adresem 00 nie jest zarejestrowany**. To wyjaśnia, dlaczego zmiany
  pilotem nie ruszają ani bajtu w tym, co słyszymy.
- **Bajt na pozycji [4] to znacznik kierunku**: `0x11` = nadrzędny→podrzędny, `0x01` =
  podrzędny→nadrzędny. Nasza jednostka nadaje `0x11`, czyli występuje w roli **nadrzędnej**.
- Na tej samej magistrali złapano kiedyś **krótką ramkę adresowaną do jednostki**
  (`7E 7E 88 FF 11 04 30 19 82 C9`), której treścią jest identyfikator płyty — wygląda na
  puls obecności sterownika. Przetestowaliśmy 48 wariantów tego wzorca z naszym
  identyfikatorem (`09 30 83`) — bez reakcji.
- Znaleziono **precedens negatywny**: na innym porcie tej samej rodziny płyt poprawnie
  zbudowane polecenie „wyłącz" zostało zignorowane mimo prawidłowej struktury i sekwencji
  inicjalizacyjnej. Autor doszedł do wniosku, że port jest wyłącznie rozgłoszeniowy.
  Wniosek dla nas: **poprawna ramka to za mało — brakuje warstwy rejestracji**.
- Istnieją **działające implementacje sterowania** Gree, ale przez inne porty: port modułu
  WiFi (4800 8E1, pełna mapa pól: tryb, nastawa, wentylator, swing) oraz przez płytkę
  Modbus w gnieździe COM-BMS. Naszego kasetonu żadna z tych dróg nie dotyczy (brak gniazd).

## Hipotezy do sprawdzenia (kolejność wg szans)

1. **Wykrywanie sterownika przy rozruchu.** Jednostka może akceptować sterownik przewodowy
   tylko wtedy, gdy wykryje go podczas startu. Test: sonda woła co 500 ms, przełączamy
   bezpiecznik, nagrywamy wszystko od pierwszej milisekundy (`narzedzia\przechwyt_rozruchu.py`).
   Uwaga: wyłączenie pilotem NIE wystarczy — to tylko czuwanie, płyta nie startuje od nowa.
2. **Obecność sterownika wykrywana poborem prądu z linii +12 V.** Prawdziwy pilot przewodowy
   zasila się z portu; nasza sonda nie (biała żyła nieużywana). Jeśli tak, układ zasilający
   z rozdz. „zasilanie" jest **warunkiem komunikacji**, nie tylko wygodą.
3. **Format ramki właściwy dla innej rodziny sterowników** niż udokumentowany XK19 —
   rozpoznanie z cudzych implementacji w toku.

## Wartość dostępna JUŻ TERAZ (bez sterowania)

Bierny podsłuch daje cztery wiarygodne pola aktualizowane co 800 ms. To wystarcza na
**integrację odczytową w Home Assistant**: temperatura pomieszczenia, temperatura
wymiennika, rzeczywisty bieg wentylatora i stan klap — jako encje `sensor`.
Sterowanie dojdzie, gdy pękną hipotezy powyżej.

## Postęp narzędziowy

- **Aktualizacja firmware przez WiFi (OTA) działa** — koniec wgrywania po kablu.
  Wgrywanie: `espota.py -i 192.168.0.172 -f <plik.bin>`.
- Firmware **v4** (`test_com_manual\sonda_gree_v4\`): komendy przez telnet
  (`TX`/`TXX`/`SET`/`START`/`STOP`/`T`/`INTTX`/`DEHOLD`/`PORX`/`POWT`/`INFO`),
  precyzyjne taktowanie bitów, synchronizacja do ciszy na magistrali, znaczniki czasu odbioru.
- Narzędzia w `narzedzia\`: `eksperyment.py` (seria prób z pliku), `skan_pelny.py`,
  `skan_naglowka.py`, `przechwyt_rozruchu.py`, `sonda_listen3.py` (nasłuch + kanał komend).


## Test rozstrzygający: czy nadajnik dochodzi do magistrali (do wykonania przy jednostce)

Firmware **v7** ma tryb fali probierczej. Sonda podnosi klucz nadawania i przełącza poziom
linii danych co sekundę — dokładnie tak, jak w teście biurkowym, ale **na podłączonej
magistrali**.

1. Uruchom tryb komendą przez telnet (port 23): `FALA 120` — fala na 2 minuty.
2. Miernik na napięcie stałe, sondy na **blaszki A i B bramki**.
3. Obserwuj przez ~15 sekund.

| Odczyt | Wniosek |
|---|---|
| przeskakuje co sekundę o kilka woltów | nadajnik **realnie zajmuje magistralę** → jednostka faktycznie nas ignoruje, hipoteza rejestracji zostaje |
| stoi w miejscu / drobne drgania | nadajnik **nie dochodzi do magistrali** → problem jest sprzętowy, a nie protokolarny; cała diagnoza sterowania do przemyślenia od nowa |

Uwaga: jednostka nadaje własne ramki co 800 ms, więc miernik i tak lekko drga. Szukamy
**regularnego, sekundowego** przeskoku o dużej amplitudzie.
