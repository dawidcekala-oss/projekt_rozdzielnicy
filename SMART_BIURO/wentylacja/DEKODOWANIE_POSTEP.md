# Dekodowanie protokołu — postęp (stan: 2026-08-25, strona „stan rzeczywisty" ROZSZYFROWANA I SKALIBROWANA)

## Rozgłoszenie jednostki FF→40 — mapa kompletna

Ramka (29 bajtów): `7E 7E FF 40 11 17` + 22 bajty danych + suma XOR.
Jednostka nadaje ją SAMA, cyklicznie co ~800 ms, do adresu `40` — to rozgłoszenie, nie
odpowiedź na nasze zapytanie. Dowód rozstrzygający: po całkowitym wyłączeniu naszych
zapytań ruch na magistrali płynie dalej bez zmian; nasza rola to bierny podsłuch.
Bajt `[4]`=`0x11` to znacznik kierunku nadrzędny→podrzędny (`0x01` = podrzędny→nadrzędny).
Indeksy bajtów liczone od zera od początku ramki. Ta strona niesie wyłącznie
**stan rzeczywisty** jednostki (to, co jednostka robi, nie to, co ma zadane):

| Bajt | Znaczenie | Wartości / dowody |
|---|---|---|
| `[9]` | **temperatura powietrza powrotnego** (czujnik ROOM, przy suficie) | przelicznik POTWIERDZONY: bajt − 100 = °C (dowód w KALIBRACJA_TEMPERATUR) |
| `[10]` | **temperatura wymiennika** (czujnik TUBE) | ten sam przelicznik; przy pracującym chłodzeniu 6–7 °C |
| `[12]` | **bieg RZECZYWISTY wentylatora** | `00`=stoi, `04`=niski, `02`=średni, `01`=wysoki; potwierdzone fizycznie (ręka przy kratce) i sekwencjami start/stop; przy zmianie trybu chwilowo `00`; po wyłączeniu najpierw `04` (dosuszanie/wybieg), po ~2 min `00` |
| `[14]` | **klapy nawiewu** | bit `80` = otwarte/pozycjonowane, `00` = zamknięte (gaśnie po wyłączeniu jednostki, wraca po włączeniu); NIE oznacza samego wachlowania (zostaje `80` po zatrzymaniu wachlowania przy pracującej jednostce) |
| `[17]` | stała `10` — funkcja nieznana (NIE nastawa) | — |
| reszta | stałe w całym badaniu | `09 30 83 ... 0E`, zera, `23 02` |

## Ustalenia negatywne (równie cenne)

- **Nastawy temperatury, trybu pracy i biegu ZADANEGO nie ma w tej ramce** — zmiany
  16→17°C oraz AUTO→chłodzenie→kolejne tryby nie ruszyły żadnego bajtu.
    Nastawy jadą w osobnej ramce **FF→00**, której jednostka NIE wysyła, dopóki sterownik
  pod adresem `00` nie jest ZAREJESTROWANY. To nie jest kwestia doboru zapytania —
  patrz Faza 2 (zamknięta wynikiem negatywnym).
- Bajt `[26]`=0x23 jest STAŁY — wcześniejsza hipoteza „nastawa 23°C" obalona.

## Faza 2 — wykonana, wynik NEGATYWNY

Faza 2 została przeprowadzona i zamknięta. Sonda nadała do jednostki **ponad 1100
wariantów ramek**: pełny przemiat bajtu rozkazu (256 wartości), 768 kombinacji nagłówka
src/dst/klasa, 48 wariantów „pulsu obecności", różne długości, precyzyjne taktowanie
bitów, synchronizację do okna 30/60/150/300 ms po ramce jednostki, podszywanie się pod
sterownik centralny. **ZERO odpowiedzi.**

Diagnoza: tor nadawania jest sprawny elektrycznie — jednostka ignoruje nas **programowo**,
bo nie jesteśmy zarejestrowanym sterownikiem. Rozpoznanie cudzych implementacji potwierdziło
naszą mapę pól niezależnie (inny egzemplarz Gree ma te same 4 pola w tych samych miejscach)
i ustaliło, że nastawy jadą w ramce FF→00, wysyłanej dopiero po zarejestrowaniu sterownika
pod adresem `00`.

Wniosek: droga do nastaw prowadzi wyłącznie przez rejestrację jako sterownik, nie przez
kolejne warianty ramek zapytania. Kolejne przemiaty ramek to strata czasu.

Infrastruktura jest gotowa i nie wymaga już dotykania sprzętu: firmware **v5** serwuje stan
po HTTP (`http://192.168.0.172/stan`), aktualizacja idzie przez WiFi (**OTA**) — koniec
wgrywania po kablu.

## Sekwencje zaobserwowane (dziennik dowodów)

- Chłodzenie przy nastawie 16°C: wymiennik surowo 124→116→104→102 (24→2°C);
  po wyłączeniu: 112→115 (12→15°C, ogrzewa się do otoczenia).
- Wyłączenie pilotem: `[14]` 80→00 (klapy zamknięte), `[12]` 04 (wybieg) → po 2 min 00.
- Włączenie: natychmiast `[14]`=80, `[12]`=04, wymiennik znów spada (surowo 111 = 11°C → ...).

## Lekcja metodyczna: wojna nasłuchów

Osierocony proces nasłuchu z poprzedniej sesji walczył z nowym o jedyne miejsce na
telnecie sondy — sonda przy każdym przełączeniu klienta wysyłała historię od nowa,
zaśmiecając log powtórkami (4352 „ramki" w 70 s przy rzeczywistym strumieniu ~87 (jednostka rozgłasza co ~800 ms)). Wszystkie
odczyty z tego okresu unieważniono i powtórzono.

**Rytuał wznowienia dekodowania** (przy "start"):
1. zabić WSZYSTKIE procesy `sonda_listen`/`beacon_watch` (PowerShell po CommandLine),
2. uruchomić JEDEN nasłuch, sprawdzić: 0 zerwań i ~50 ODEBRANYCH ramek / 40 s
   (jednostka rozgłasza co ~800 ms; sonda sama nic nie nadaje),
3. `dekoder_roznicowy.py baza` → nowa ramka odniesienia,
4. dopiero potem eksperymenty: tryby pracy (ikonka po każdej zmianie), swing, wł./wył.

## Narzędzia

- `narzedzia\dekoder_roznicowy.py` — `baza` zapisuje odniesienie; bez argumentu
  porównuje najnowszą stabilną ramkę i wypisuje zmienione bajty.
- `narzedzia\sonda_listen.py` — nasłuch (dopisuje do `test_com_manual\log_sondy.txt`).
