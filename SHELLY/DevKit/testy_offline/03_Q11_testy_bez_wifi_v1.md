# Testy bez Wi-Fi: Q11 z modułem Shelly
*Poziom D: nie ma routera; zostaje Bluetooth albo sieć modułu i telefon obok ładowarki. Do tego funkcje samego sterownika. Testy D1–D9 · AMPERE POINT · 28 września 2026 · oprac. Dawid Cekała*
FOOTER: AMPERE POINT — testy bez Wi-Fi · Q11 z modułem Shelly · v1 · 2026-09-28

## W skrócie {-}

- **Sytuacja z życia:** garaż bez zasięgu Wi-Fi. Q11 na Tuya ma wtedy tylko menu ładowarki.
- **Q11 na Shelly ma dwie drogi:**
  - Bluetooth: aplikacja albo laptop;
  - własna sieć modułu, do której telefon łączy się bezpośrednio i otwiera stronę WWW modułu.
- **Kłopot to godzina.** Bez Wi-Fi nie ma serwera czasu, a czasu ustawionego ręcznie moduł sterownikowi nie przekazuje (sprawdzone 25.09). D5 sprawdza, czy strona albo aplikacja w ogóle ustawiają zegar modułu. D6 sprawdza, co sterownik robi z oknem godzin bez godziny.
- **Funkcje samego sterownika z menu** (D7, D9) też są w tym dokumencie, bo bez Wi-Fi to jedyne, co zostaje po stronie Tuya.
- **Większość kroków robimy z modułem nadal w sieci biura,** żeby widzieć log. Prawdziwe wyłączenie Wi-Fi modułu (D8) robimy dopiero, gdy Bluetooth i strona WWW działają.
- Poziomy łączności, pojęcia i porównanie z Tuya są w dokumencie 00, w tabeli 3.3.

## 1. Przygotowanie

- Laptop: karta Bluetooth (Intel), Python z biblioteką `bleak`.
- **Narzędzie do napisania:** `narzedzia\ble_rpc.py`, klient poleceń Shelly przez Bluetooth. Ta sama treść JSON co przez Wi-Fi, opakowana w ramkę Bluetooth Shelly.
- Telefon z aplikacją Shelly.
- Monitor logu przez Wi-Fi uruchomiony (poza D8).
- Symulator auta podłączony (D6–D8).

## 2. Testy

### D1. Skan Bluetooth

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D1a | Skan Bluetooth z laptopa | moduł widoczny pod swoją nazwą, z reklamą Shelly |

### D2. Polecenia z laptopa przez Bluetooth

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D2a | Odczyt stanu przez Bluetooth | te same pola co przez Wi-Fi |
| D2b | Zmiana limitu prądu na 10 A przez Bluetooth | sterownik potwierdza w logu w ciągu 1 s, tak jak przy Wi-Fi |

### D3. Aplikacja Shelly przez Bluetooth

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D3a | Telefon z wyłączonym Wi-Fi i danymi komórkowymi; aplikacja Shelly: włącz/wyłącz ładowanie, zmiana limitu | **do ustalenia.** Aplikacja wymaga konta w chmurze, a chmura modułu jest wyłączona; może nie pokazać urządzenia. Zapisujemy, co widać i ile trwa połączenie |

### D4. Strona WWW przez sieć modułu

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D4a | Sprawdzamy ustawienia sieci modułu: czy jest włączona i **czy ma hasło** | zapisujemy |
| D4b | Telefon łączy się z siecią modułu; przeglądarka otwiera stronę modułu | strona działa bez routera i bez aplikacji |
| D4c | Zmiana limitu i włącznika ze strony | sterownik potwierdza |

**Wniosek do analizy GAP, niezależnie od wyniku.** Jeśli sieć modułu nie ma hasła, każdy w pobliżu może sterować ładowarką przez stronę WWW.

### D5. Czas z telefonu

**Cel.** Bez Wi-Fi jedynym źródłem godziny jest telefon. Sprawdzić, czy strona WWW albo aplikacja ustawiają zegar modułu przy połączeniu i czy sterownik dostaje tę godzinę. Wiemy już, że czasu ustawionego poleceniem moduł sterownikowi nie przekazuje (25.09).

| Krok | Co robimy | Wynik oczekiwany / co zapisujemy |
| --- | --- | --- |
| D5a | Zatrzymujemy kontener z serwerem czasu, restartujemy moduł | moduł nie ma godziny; sterownik dostaje zerową datę |
| D5b | Telefon: strona WWW modułu przez sieć modułu | czy zegar modułu dostał godzinę z telefonu; co moduł wysyła sterownikowi |
| D5c | Telefon: aplikacja przez Bluetooth | to samo |
| D5d | Serwer czasu z powrotem, restart modułu | poprawna godzina wraca |

**Jeśli zegar modułu dostaje godzinę, a sterownik nie,** to potwierdza prośbę do Shelly: czas ustawiony z telefonu ma się liczyć jako ważny dla sterownika.

### D6. Okno godzin bez godziny

**Cel.** Co sterownik robi z oknem godzin, gdy dostaje od modułu zerową datę. Tak będzie po każdym zaniku zasilania bez Wi-Fi.

| Krok | Co robimy | Wynik oczekiwany / co zapisujemy |
| --- | --- | --- |
| D6a | Serwer czasu zatrzymany, restart modułu; z menu tryb „harmonogram”, okno obejmujące bieżącą godzinę; symulator „ładuje” | czy sterownik ładuje, nie ładuje, czy robi coś innego |
| D6b | Okno poza bieżącą godziną | to samo |
| D6c | Serwer czasu z powrotem, restart modułu | sterownik wraca do normalnej pracy z oknem |

### D7. Funkcje sterownika z menu

**Cel.** Te funkcje działają bez żadnej łączności. Sprawdzamy, czy sterownik zgłasza zmiany z menu modułowi, żeby moduł je pokazał.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D7a | Limit prądu z menu ładowarki: 8 A | sterownik sam zgłasza 8 A; pole w module aktualizuje się bez naszego zapisu |
| D7b | Z menu: czy okno godzin da się ustawić z minutami | jeśli tak, założenie „tylko pełne godziny” jest błędne; poprawić w zestawieniu punktów danych |
| D7c | Start ładowania po podłączeniu auta, bez żadnego polecenia | jak 25.09: sterownik startuje sam; potwierdzenie na obecnej konfiguracji |

### D8. Moduł naprawdę bez Wi-Fi

**Cel.** Wszystko z D2–D4 przy wyłączonej stacji Wi-Fi modułu, czyli naprawdę bez routera.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D8a | Sieć modułu włączona (D4a); harmonogram w module: za 3 min limit 6 A | droga awaryjna gotowa |
| D8b | Przez Bluetooth wyłączamy stację Wi-Fi modułu | moduł znika z sieci biura; log niedostępny |
| D8c | Powtórka D2, D3 i D4 | działa bez Wi-Fi; dowodem są wyświetlacz ładowarki i odpowiedzi przez Bluetooth |
| D8d | Harmonogram z D8a | czy odpalił; wyświetlacz pokazuje 6 A |
| D8e | Ikona sieci na wyświetlaczu | czy moduł wysyła inny stan niż „4”, np. „2” = brak routera |
| D8f | Przez Bluetooth włączamy stację Wi-Fi z powrotem | moduł wraca do sieci biura w ciągu minuty, log wraca. Jeśli moduł zażąda hasła sieci, wpisuje je użytkownik |

**Ryzyko: średnie.** Jeśli Bluetooth zawiedzie, moduł zostaje bez Wi-Fi. Droga powrotu: sieć modułu z telefonu. Dlatego D8 dopiero po udanych D2 i D4.

### D9. Reset sieci z menu ładowarki

**Cel.** W Q11 na Tuya pozycja menu „reset sieci” wprowadza moduł w parowanie. Sprawdzić, co to polecenie sterownika robi z modułem Shelly.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| D9a | Monitor na najwyższym poziomie logu; z menu ładowarki: reset sieci | w logu ramka od sterownika z poleceniem resetu Wi-Fi i reakcja modułu: ignoruje, kasuje Wi-Fi albo wchodzi w parowanie |
| D9b | Jeśli moduł skasował Wi-Fi: ponowne dodanie do sieci | moduł wraca do sieci |

**Drogi powrotu w D9b, w tej kolejności:**
1. **Aplikacja Shelly przez Bluetooth.** Uwaga: 24.09 ta droga zawiodła, bo aplikacja zapisała nazwę sieci ze spacją na końcu.
2. **Sieć modułu i jego strona WWW.** Nazwę sieci i hasło wpisuje użytkownik.

USB odpada, bo moduł jest zasilany z płytki.

**Ryzyko: duże.** Utrata Wi-Fi modułu, dlatego to ostatni test całego programu. Wynik zapisujemy jako fakt do dokumentacji dla fabryki.

## 3. Kolejność i czas

| Kolejność | Testy | Czas |
| --- | --- | --- |
| 1 | narzędzie Bluetooth, D1–D4 | 1 h 35 min |
| 2 | D5 | 15 min |
| 3 | D6, D7 | 50 min |
| 4 | D8 | 30 min |
| 5 | D9, na końcu całego programu | 20 min plus ewentualne dodanie do sieci |

Razem około 3 h 30 min. Miejsce tych testów w kolejności całego programu: dokument 00, rozdział 5.

## 4. Wyniki

| Test | Wynik | Co zaobserwowano | Data |
| --- | --- | --- | --- |
| D1 skan Bluetooth | | | |
| D2 polecenia z laptopa | | | |
| D3 aplikacja przez Bluetooth | | | |
| D4 strona WWW przez sieć modułu | | | |
| D5 czas z telefonu | | | |
| D6 okno godzin bez godziny | | | |
| D7 funkcje z menu | | | |
| D8 moduł bez Wi-Fi | | | |
| D9 reset sieci z menu | | | |
