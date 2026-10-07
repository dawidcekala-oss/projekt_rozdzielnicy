# Plan dekodowania protokołu COM-MANUAL

Cel: zbudować tabelę „bajt → znaczenie" dla ramek jednostki (odczyt) i ramek rozkazów
(zapis), wystarczającą do postawienia encji odczytowych w Home Assistant. Encja `climate` (sterowanie)
pozostaje celem odległym — wymaga przebicia warstwy rejestracji sterownika, patrz faza 2.
Stan wyjściowy: sonda działa, ale jednostka NIE odpowiada na zapytania — ona sama nadaje
rozgłoszenie 29-bajtowe do adresu `40` równo co 800 ms. Nasza rola to bierny podsłuch
(dowód: po wyłączeniu zapytań ruch na magistrali trwa dalej bez zmian — patrz
`FAZA2_USTALENIA.md`). Narzędzia gotowe: log `test_com_manual\log_sondy.txt` +
`narzedzia\analiza_ramek.py`.

## Faza 1 — dekodowanie ODCZYTU (bez żadnego ryzyka) — ZAKOŃCZONA

Wynik: rozgłoszenie niesie tylko cztery zmienne pola — `[9]` temperatura powietrza
powrotnego, `[10]` temperatura wymiennika, `[12]` bieg rzeczywisty wentylatora,
`[14]` klapy nawiewu. Wszystkie pozostałe bajty są stałe. Poniższy plan zachowano jako
zapis metody; kroki dotyczące nastaw okazały się bezprzedmiotowe.

Metoda różnicowa: jednostka sama nadaje co 800 ms, sonda tylko słucha; użytkownik zmienia
pilotem IR **jedną rzecz naraz**,
porównujemy ramki przed/po. Bajt, który się zmienił, dostaje nazwę.

| Krok | Zmiana pilotem | Czego szukamy |
|---|---|---|
| 1.1 | ~~nastawa 23→24→25→…→30, potem →16~~ | BEZPRZEDMIOTOWE — nastawy nie ma w rozgłoszeniu; jedzie ona w ramce `FF→00`, której jednostka nie wysyła bez zarejestrowanego sterownika pod adresem 00 |
| 1.2 | ~~tryb: chłodzenie → grzanie → wentylator → osuszanie → auto~~ | BEZPRZEDMIOTOWE — bajtu trybu w rozgłoszeniu nie ma; zmiana trybu pilotem nie rusza żadnego bajtu |
| 1.3 | wentylator: niski → średni → wysoki → auto | bajt biegu |
| 1.4 | wyłączenie → włączenie | brak osobnego bajtu stanu pracy — wyłączenie rozpoznajemy pośrednio: `[12]`=00 (wentylator stoi) i `[14]`=00 (klapy zamknięte) |
| 1.5 | żaluzje (swing) wł./wył. | bajt żaluzji |
| 1.6 | ZAKOŃCZONE | dwa bajty temperatur: `[9]` powietrze powrotne (czujnik ROOM, przy suficie — według niego jednostka reguluje) i `[10]` wymiennik (czujnik TUBE); przelicznik: **surowy bajt minus 100 = °C** — patrz `KALIBRACJA_TEMPERATUR.md` |

Zasady: po każdej zmianie odczekać ~10 s (2–3 zapytania sondy); zapisywać godzinę i co
zmieniono; na koniec wrócić do nastaw wyjściowych. Wynik fazy: tabela pól ramki odczytu.

## Faza 2 — dekodowanie ZAPISU (ostrożnie, krok po kroku)

Hipoteza startowa: format rozkazu wg publicznej dokumentacji XK19 (ta sama, z której
pochodzi ramka, którą wysyłaliśmy — nigdy nie doczekała się odpowiedzi). Weryfikacja:

1. WYKONANE I WYCZERPANE. Przetestowano ponad 1100 wariantów ramek wysyłanych do jednostki:
   pełny przemiat bajtu rozkazu (256 wartości), 768 kombinacji nadawca/adresat/klasa,
   48 wariantów „pulsu obecności", różne długości ramki, precyzyjne taktowanie bitów,
   synchronizację do okna po ramce jednostki (30/60/150/300 ms), podszycie się pod
   sterownik centralny. **Ani jednej odpowiedzi.**
2. Sprawdzić podwójnie: (a) słychać/widać reakcję jednostki, (b) kolejna ramka odczytu
   pokazuje nową wartość w polu z fazy 1.
3. Działa → kolejne pola: nastawa, tryb, wł./wył., żaluzje — zawsze jedno pole na próbę.
4. Nie działa → porównać strukturę naszej ramki zapytania z formatem rozkazu XK19 i
   WYKONANE: warianty adresów przemieciono (768 kombinacji nadawca/adresat/klasa)
   bez skutku — problemem nie jest adres, tylko brak rejestracji sterownika.

Zasady bezpieczeństwa zapisu: nigdy nie wysyłać ramek z polami o nieznanym znaczeniu
ustawionymi „na ślepo"; po każdej sesji przywrócić nastawy pilotem; pilot IR pozostaje
nadrzędny (działa równolegle — zweryfikowane); w razie dziwnego zachowania jednostki:
odłączyć sondę i przełączyć bezpiecznik.

## Faza 3 — utrwalenie

1. Tabela pól (odczyt + zapis) trafia do dokumentacji projektu i do raportu.
2. Firmware docelowy — DOSTARCZONY. Wersja v5 nasłuchuje rozgłoszenia, dekoduje cztery pola
   i serwuje stan po HTTP (`http://192.168.0.172/stan`); w Home Assistant pięć encji REST
   (patrz `HA_INTEGRACJA_ODCZYT.md`). Aktualizacja firmware przez WiFi (OTA) działa — koniec
   wgrywania po kablu. Encja `climate` dojdzie dopiero, gdy uda się zarejestrować sondę jako
   sterownik przewodowy. Uwaga o zasilaniu sondy z linii
   jednostki: wariant z rezystorem 47 om **zawiódł** (przegrzanie, brak startu sondy) —
   obowiązująca wersja to **25–28 om** (np. 4×100 om równolegle) + 3×100 µF. Sprawa
   niezamknięta, montaż odłożony przez użytkownika.
3. Test stabilności kilka dni na jednostce pilotażowej.

## Podział ról

- **Użytkownik:** naciska przyciski pilota i mówi, co zmienił; w fazie 2
  przełącza bezpiecznik na komendę (test wykrywania sterownika przy rozruchu płyty —
  wyłączenie pilotem NIE wystarczy, to tylko czuwanie).
- **Claude:** całą resztę — zbieranie ramek, porównania, tabela pól, ramki testowe fazy 2,
  firmware fazy 3.
