# Ustalenia z testów Q11 z modułem Shelly X

*Stan na 30 września 2026, po poziomie B (bez chmury). Podstawa pełnego zestawienia poziomów B, C i D · AMPERE POINT · oprac. Dawid Cekała*
FOOTER: AMPERE POINT — ustalenia z testów · Q11 z modułem Shelly · v1 · 2026-09-30

Każde ustalenie ma źródło: numer testu (dokument 01) albo numer w rejestrze usterek (S-xx, `DevKit\REJESTR_USTEREK.pdf`). ✔ sprawdzone na module, ◐ częściowo, ✘ nie działa.

## 1. Sterowanie bez chmury {-}

| Droga | Stan | Co ustalono | Źródło |
| --- | --- | --- | --- |
| Strona WWW modułu | ✔ | Działa z laptopa i telefonu, bez hasła. Pokazuje tylko 6 pól szablonu, fazy jako „N/A A” | B2, S-10, S-11 |
| Home Assistant | ✔ z łatką | Oficjalna integracja widzi tylko fazy. Z łatką 33 encje, sterowanie limitem, włącznikiem, trybem, oknem i limitem energii działa lokalnie | B3, S-33 |
| HTTP i WebSocket (API) | ✔ | Odczyt 40–150 ms, zapis dociera do sterownika | B2, B7 |
| MQTT przez broker w sieci lokalnej | ✔ | Polecenia i odpowiedzi przez broker na laptopie, także bez internetu | C4 |
| MQTT przez broker w internecie | ✔ | Publiczny broker testowy: moduł połączony stabilnie, polecenie i odpowiedź w około 1,1 s, sterownik potwierdza | B13 (01.10) |
| OCPP przez nasz most | ✔ | Serwer OCPP w sieci lokalnej, także bez internetu: rejestracja, stan, pomiary, limit prądu, pełna transakcja. Serwera OCPP w internecie nie testowaliśmy | C4c (25.09, 01.10) |
| Wychodzący WebSocket do naszego serwera | ✔ | Moduł sam się łączy, wykonuje polecenia serwera, wraca po zaniku serwera najpóźniej po około minucie. Podstawa mostu OCPP bez otwierania portów u klienta | B8 |
| Harmonogram w module | ✔ | Zadania odpalają co do sekundy, przetrwały restart | B4 |
| Webhooki | ✔ | Zmiana stanu ładowarki, limitu i włącznika sama wywołuje nasz program w około 1 s, także z warunkiem (np. tylko start ładowania); przetrwały restart | B5 |
| Kanał UDP | ✔ | Działa, ale bez hasła; wyłączony | B12, S-42 |
| Aplikacja Shelly | ✘ | Steruje wyłącznie przez chmurę; w sieci lokalnej tylko sprawdza moduł. Z chmurą włączoną na 2 min działała od razu | B1, S-30 |

## 2. Moduł Shelly {-}

- **Granic pilnuje moduł:** limit spoza 6–16 A odrzucony, zanim cokolwiek pójdzie do sterownika. Kroku nie pilnuje (10,5 A przechodzi, skrypt zaokrągla) (B7).
- **Połączenia naraz:** 6 ponad HA, monitor, stronę i połączenie wychodzące. Przy komplecie moduł zamknął połączenie Home Assistant (B9, S-40).
- **Pamięć (dokument 04):** po zaniku zasilania wraca wszystko, co moduł zapisuje: ustawienia, pamięć klucz-wartość, harmonogram, webhooki, usługa, definicje pól, wartości pól zapamiętywanych. Zapis wartości pól najwyżej raz na około 3 s, więc przepadają zmiany z ostatnich około 3 s; częsta zmiana limitu zużywa pamięć (S-44). Pozostałe pola i stan skryptu (czas, energia sesji) giną.
- **Zegar po zaniku:** do czasu synchronizacji moduł wykonuje harmonogram według zapamiętanej, nieaktualnej godziny (S-45).
- **Kopia konfiguracji** niezaszyfrowana, z hasłem Wi-Fi i tokenem chmury, bez plików usługi (B10, S-41).
- **Ponowienia zapisu** po 0,3 s potrafią przestawić kolejność poleceń do sterownika: 13, 12, 13, 13, 12 A (S-13).
- **Stan sieci dla sterownika:** moduł zgłasza „połączony z chmurą”, choć chmura wyłączona; ikona na wyświetlaczu miga co kilkadziesiąt sekund (S-39).
- **Fałszywy start ładowania po restarcie modułu:** webhook „start ładowania” przychodzi po każdym restarcie, choć ładowanie trwa (S-50).
- **Czas:** bez baterii zegara. Serwer czasu na laptopie działa, także bez internetu (C4 przygotowanie). Po starcie sterownik dostaje godzinę po około 24 s.
- **Log:** log UDP pokazuje start od 23. sekundy; pierwszych sekund nie widać przez sieć (S-31).
- **Powitanie ze sterownikiem może utknąć** po restarcie modułu (ponad 3 min w stanie „Fetching Config”, bez danych i sterowania); pomógł kolejny restart (S-46).

## 3. Sterownik Q11 {-}

- **Tryb wynika z ostatnio ustawionego parametru:** limit energii > 0 przełącza na „do limitu energii”, okno godzin na „harmonogram”, „od razu” zeruje limit energii; „do limitu energii” przy limicie 0 odrzucony (S-21).
- **Okno o równych godzinach odrzucane** (0–0, 1–1) (S-22).
- **Odpowiedź na zapis:** po 0,3–3 s, najpierw zwykle poprzednia wartość; potwierdzenie nowej przychodzi osobno albo wcale. Brak potwierdzenia nie znaczy odmowy: tryb „od razu” przyjęty bez odpowiedzi (S-23, S-38).
- **Po zapisie limitu energii** kilkusekundowy zalew meldunków (około 10 na sekundę) i chwilowy brak odpowiedzi na sygnał życia (S-20).
- **Po starcie** odpowiada na odpytanie wszystkich punktów po 21–30 s. **Po zaniku zasilania pamięta limit prądu, a traci ustawienie jednej sesji na czas: okno godzin z trybem „harmonogram” oraz opóźnienie i czas trwania z menu** (wraca „od razu”) (S-47). To nie jest harmonogram Tuya — ten ustawia się w aplikacji. Opóźnienie ustawiane w stanie C pokazuje się z innymi wartościami, także z modułem Tuya: usterka sterownika (S-49). Zgłasza wtedy wersję „V1” (S-27). W menu ładowarki jest opóźnienie i czas trwania ładowania; moduł ich nie widzi — sterownik ich nie zgłasza ani sam, ani przy odpytaniu. Widać tylko skutek: stan „czeka” (S-48).
- **Restart modułu nie przerywa ładowania** (5 restartów przy ładowaniu, C9). Stanu „podłączone” nie zgłasza: z „wolna” od razu „ładuje”.
- **Wyłączenia ładowania nie przyjmuje** od 29.09 13:44 (3 próby, z aplikacji i przez API); o 12:03 przyjmował; przyczyna nieustalona. Włącznik sam przechodzi na „wł.” po włączeniu zasilania i na „wył.” po zakończeniu sesji (S-24).

## 4. Nasz skrypt w module {-}

- Wersja **v4.3.1** (usługa 13109-3815): 15 pól, 16 punktów danych; do sterownika tylko zmiany z zewnątrz, po 1 s ciszy; znane odrzucenia nie idą na łącze. Atrapa 51/51, próby na żywo ✔ (S-02, S-03, S-04, S-08).
- **Otwarte:** pole może pokazywać co innego niż sterownik, bo moduł nie przekazuje skryptowi odpowiedzi równej zapamiętanej wartości (S-01). Propozycja: polecenie diagnostyczne w skrypcie, które pokaże, co moduł wie o punktach sterownika.

## 5. Bezpieczeństwo {-}

- Bez hasła każdy w sieci steruje ładowarką przez stronę, HTTP, WebSocket i MQTT (S-18). Test hasła (B11) czeka na Dawida.
- Kopia konfiguracji zawiera hasło Wi-Fi jawnie (S-41).
- **Punkt dostępowy modułu nie włączy się bez hasła**, gdy moduł ma skonfigurowaną sieć (30.09: `WiFi.SetConfig` z `ap.enable` i `is_open` → błąd „pass: should not be empty”). Otwarty był tylko przed konfiguracją Wi-Fi. Hasło wpisuje Dawid; test przez telefon.
- „Development Wi-Fi” w portalu zapisuje hasło w tokenie produktu (S-17); wgrywamy samą usługę.

## 6. Co zostało {-}

| Co | Kto | Dokument |
| --- | --- | --- |
| B5b webhook przy przejściach stanu | ✔ zrobiony 30.09 | 01 |
| B11 hasło | Dawid (wpisanie hasła) | 01 |
| Test pamięci modułu | ✔ zrobiony 30.09 | 04 |
| Poziom C: bez internetu | Dawid (reguła w routerze albo kabel) | 02 |
| Poziom D: bez Wi-Fi | Dawid | 03 |
| Rozjazd pola i sterownika | laptop, po decyzji o poleceniu diagnostycznym | S-01 |
| Pełne zestawienie B, C, D | po testach C i D | ten dokument jako podstawa |
