# Procedura: sonda COM-MANUAL (Gree GKH, płyta GRZ4M-A3) — ODCZYT, wersja zweryfikowana

Stan: **odczyt magistrali DZIAŁA (zweryfikowany 2026-08-25)** — ale uwaga: to jest
BIERNY PODSŁUCH, a nie dialog. Jednostka **nie odpowiada** na ramki sondy; sama rozgłasza
swój stan co dokładnie 800 ms do adresu 40, a sonda ten rozgłos tylko czyta. Ten dokument
opisuje działającą konfigurację odczytu i sposób jej uruchamiania.
Historia dochodzenia do niej: [`..\STUDIUM_PRZYPADKU.md`](../STUDIUM_PRZYPADKU.md).
Schemat: [`..\schematy\schemat_FINALNY_dzialajacy.png`](../schematy/schemat_FINALNY_dzialajacy.png).

## 1. Elementy układu (wszystko z domowych zapasów)

| Element | Rola | Dokumentacja |
|---|---|---|
| WeMos D1 R1 (ESP8266) | mózg sondy: ramki + log przez WiFi | [`..\plytki\wemos_d1_r1.md`](../plytki/wemos_d1_r1.md) |
| bramka ZTS47/SMG-01 (płytka GRZ47-G) | konwerter UART↔RS485 | [`..\plytki\bramka_grz47_smg01.md`](../plytki/bramka_grz47_smg01.md) |
| pigtail JST (z RCD) | wtyczka do gniazda COM-MANUAL | żyły: czarna=A, czerwona=B, żółta=GND, biała=+12V (zaizolowana!) |
| 2 rezystory: 3,3 kΩ + 6,5 kΩ | dzielnik 5 V → 3,3 V na linii odbioru | wlutowane w wiązkę |
| programator ALIENTEK Mini-Pro | tylko pomocniczo: rozgałęźnik do testu ciągłości | [`..\plytki\flasher_alientek_minipro.md`](../plytki/flasher_alientek_minipro.md) |

## 2. Połączenia (komplet — patrz schemat)

```
WeMos 5V            → CN2 +5V (żyła czerwona)
WeMos GND           → CN2 GND  oraz  CN2 RXP (biała)  ← odbiornik włączony na stałe
WeMos D12/MISO/D6   → CN2 „TXD"   (nadawanie; opisy CN2 są z perspektywy klimatyzatora!)
CN2 „RXD" → [3,3 kΩ] → WeMos D13/SCK/D5, z węzła [6,5 kΩ] → GND   (odbiór przez dzielnik)
WeMos D11/MOSI/D7   → CN2 TXP (żółta)   ← klucz nadawania (HIGH tylko na czas ramki)
blaszka X1 (lub X3) → konektor CZARNY  → pigtail → pin A gniazda COM-MANUAL
blaszka X2 (lub X4) → konektor CZERWONY→ pigtail → pin B gniazda
żyła żółta pigtaila → GND WeMosa (masa wspólna — obowiązkowa)
żyła biała pigtaila (+12 V) → na razie NIGDZIE (zaizolowana). Podanie wprost na VIN blokuje
                              start jednostki; docelowo przez filtr 25–28 Ω + 300 µF — patrz ZASILANIE_OBLICZENIA
```

## 3. Uruchomienie w terenie

1. Bezpiecznik klimatyzatora **wyłącz** → wtyczka pigtaila w gniazdo COM-MANUAL (dociśnij) → bezpiecznik **włącz**.
2. Zasil WeMosa **z własnej ładowarki 5 V** (micro-USB lub jack) — nigdy wprost z pinu +12 V portu
   (dopuszczalny wyłącznie przez filtr ograniczający prąd, patrz `ZASILANIE_OBLICZENIA.md`).
3. Sonda sama łączy się z WiFi `AmperePoint` (2,4 GHz) i od tej chwili:
   - co 2 s rozgłasza po sieci komunikat `SONDA-GREE <adres IP>` (port UDP 4210),
   - udostępnia log na porcie telnet 23 (historia + na żywo),
   - serwuje stan po HTTP: `http://192.168.0.172/` (podgląd w przeglądarce) oraz
     `http://192.168.0.172/stan` (JSON — źródło dla 5 encji REST w Home Assistant),
   - przyjmuje aktualizację firmware przez WiFi (OTA, host `sonda-gree`) — wgrywanie
     po kablu nie jest już potrzebne,
   - **nic nie wysyła do jednostki** — wysyłka okresowa jest domyślnie bezcelowa
     (przetestowano ponad 1100 wariantów ramek, zero odpowiedzi) i można ją wyłączyć
     komendą `STOP` przez telnet; do odczytu stanu nie jest potrzebna.
4. Na komputerze: nasłuch `sonda_listen.py` dopisuje wszystko do `log_sondy.txt`.

## 4. Interpretacja

| Obserwacja | Znaczenie |
|---|---|
| ramka `7E 7E FF 40 ...` (29 B) powtarzana co ~800 ms | stan normalny — sonda czyta rozgłoszenie jednostki. Ramka pojawia się także wtedy, gdy sonda nic nie nadaje |
| brak odpowiedzi na ramki wysłane przez sondę | **stan normalny, nie usterka** — jednostka ignoruje niezarejestrowany sterownik |
| ramki z dopiskiem „suma bledna" (~9%) | ucięte odbiory (programowy UART + WiFi) — ignorować pojedyncze |
| brak **jakichkolwiek** ramek w logu (całkowita cisza na magistrali) | sprawdź kolejno: zasilanie bramki (5 V na CN2), styk wtyczki w gnieździe, polaryzację A/B (zamiana konektorów czarny↔czerwony na blaszkach — bezpieczna przy pracującej jednostce) |

## 5. Testy diagnostyczne przy biurku (bez klimatyzatora)

Uwaga: poniższe testy sprawdzają **wyłącznie elektrykę** toru nadawania i odbioru. Sprawny
nadajnik nie oznacza, że jednostka odpowie — tor nadawania jest zweryfikowany jako sprawny,
a jednostka i tak ignoruje nasze ramki programowo (nie jesteśmy zarejestrowanym sterownikiem).

Firmware `tester_biurkowy\tester_biurkowy.ino` (komendy po USB: `n`/`o` = tryb
nadawanie/odbiór, `1`/`0` = klucz nadawania):

1. **Nadawanie:** tryb `n` + multimetr na blaszkach A–B → odczyt ma przeskakiwać co 1 s
   (osiągane ±4,8 V).
2. **Odbiór:** tryb `o` + wstrzyknięcie: 5 V na jedną blaszkę, masa na drugą (przez chwilę,
   wprost z pinów WeMosa) → raportowany stan D5 ma podążać za polaryzacją.
3. **Ciągłość pigtaila:** wtyczka w gniazdo nakładki programatora ALIENTEK (odłączonego
   od USB!), piszczyk: szpilka ↔ drugi koniec żyły. Uwaga: tor odbioru zawiera rezystor
   3,3 kΩ — piszczyk tam **nie zapiszczy nigdy**; mierzyć omomierzem (~3,3 kΩ = OK).

## 6. Po teście / bezpieczeństwo

- Pilot IR działa równolegle z sondą (zweryfikowane). Gdyby jednostka przestała reagować
  na pilota — odłączyć sondę i przełączyć bezpiecznik.
- Wpinanie/wypinanie wtyczki z gniazda COM-MANUAL tylko przy wyłączonym bezpieczniku.
  Zmiany po stronie bramki (blaszki, złącze krosowe) są bezpieczne przy pracującej jednostce.
- W skrzynce jednostki jest 230 V; czynnik R32 jest palny — bez iskrzenia przy jednostce.
