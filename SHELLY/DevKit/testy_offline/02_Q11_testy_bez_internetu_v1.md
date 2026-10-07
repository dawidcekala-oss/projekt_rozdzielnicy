# Testy bez internetu: Q11 z modułem Shelly
*Poziom C: Wi-Fi i sieć lokalna są, internetu nie ma. Testy C1–C12 · AMPERE POINT · 28 września 2026 · oprac. Dawid Cekała*
FOOTER: AMPERE POINT — testy bez internetu · Q11 z modułem Shelly · v1 · 2026-09-28

## W skrócie {-}

- **Poziomu C dotąd naprawdę nie sprawdziliśmy.** 25.09 internet był w tle, a jego brak symulowaliśmy tylko dla serwera czasu. Teraz moduł dostaje adres bez bramy do internetu: widzi laptopa, broker i serwer czasu, ale nie internet.
- **Co już wiemy o czasie:** bez serwera czasu moduł wysyła sterownikowi zerową datę. Z lokalnym serwerem czasu poprawna godzina przychodzi około 18 s po starcie (25.09).
- **Najważniejsze testy:**
  - **C8, zanik zasilania:** czy moduł po starcie nie narzuci sterownikowi zapamiętanego limitu prądu;
  - **C9, restart samego modułu w trakcie ładowania:** tak będzie przy każdej aktualizacji modułu.
- **Opcjonalnie:** C10 (serwer czasu podany przez router), C11 i C12 (porównanie z Tuya). Wszystkie trzy wymagają zmian w routerze, które ustawia administrator sieci.
- Poziomy łączności, pojęcia i porównanie z Tuya są w dokumencie 00, w tabeli 3.2.

## 1. Przygotowanie: moduł bez internetu

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| P1 | Sprawdzamy, że sieć modułu (punkt dostępowy) jest włączona | droga ratunkowa, gdyby moduł zniknął z sieci biura |
| P2 | Moduł dostaje stały adres 192.168.0.238, maskę sieci biura i **brak bramy**; serwer czasu 192.168.0.57 | moduł wraca pod tym samym adresem, monitor działa |
| P3 | Z modułu próba pobrania strony z internetu (polecenie pobrania adresu WWW przez moduł) | błąd: moduł nie ma internetu. Pobranie z laptopa na 192.168.0.57 działa |
| P4 | Na koniec wszystkich testów C: powrót na adres automatyczny i na publiczny serwer czasu | moduł znów ma internet, poziom B |

**Narzędzie do napisania: serwer czasu z przesunięciem** (`narzedzia\zegar_przesuniety.py`, test C6).
- **Co robi:** podaje czas przesunięty tak, żeby za 2 minuty wybiła pełna godzina. Okno godzin ma tylko pełne godziny, więc bez tego test trwałby do dwóch godzin.
- **Dlaczego zegar laptopa zostaje bez zmian:** moduł przekazuje sterownikowi tylko to, co dostał od serwera czasu, więc przesuwamy wyłącznie zegar ładowarki.
- **Jak go uruchomić:** na czas testu zatrzymujemy kontener z serwerem czasu, bo zajmuje port 123. Po każdej zmianie czasu restartujemy sam moduł, żeby od razu pobrał nową godzinę.

**Laptop nie może usypiać podczas testów C.** 29.09 rano, po uśpieniu laptopa, serwer czasu w kontenerze przez około 48 min nie miał źródeł (log kontenera: „Can't synchronise: no selectable sources”). W tym czasie podawał czas z zegara maszyny wirtualnej, który po uśpieniu stoi w miejscu. DevKit przyjął godzinę spóźnioną o 44 minuty i przekazywał ją sterownikowi. Serwer czasu na laptopie jest dobry do testów, nie jako rozwiązanie u klienta.

<!-- PAGEBREAK -->

## 2. Testy

### C1. Aplikacja Shelly w sieci lokalnej

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C1a | Telefon w sieci biura, aplikacja Shelly; moduł bez internetu i bez chmury | czy aplikacja znajduje moduł w sieci lokalnej i steruje nim. Telefon ma w tym czasie internet przez sieć biura, więc sprawdzamy tylko drogę telefon → moduł |

### C2. Sterownik sterowany z modułu

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C2a | Symulator: wolne → podłączone → ładuje | sterownik przechodzi stany „wolna” → „auto podłączone” → „ładuje”, zamyka stycznik; moduł pokazuje to w polach |
| C2b | Limit prądu z modułu przy ładowaniu: 12 A | sterownik potwierdza w 1 s; wyświetlacz pokazuje 12 A |

### C3. Godzina po starcie

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C3a | Wyłączamy i włączamy ładowarkę; obserwujemy pierwsze ramki czasu | przez około 20 s zerowa data, potem poprawna; zapisujemy, co w tym czasie pokazuje wyświetlacz |

### C4. Drogi lokalne bez internetu

**Cel.** Potwierdzić, że wszystko, co sprawdziliśmy na poziomie B, działa też bez internetu. Ruch zostaje w sieci lokalnej, więc oczekujemy tego samego wyniku.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C4a | Zmiana limitu przez HTTP i WebSocket | sterownik potwierdza |
| C4b | Zmiana limitu przez MQTT | sterownik potwierdza; broker działa w sieci lokalnej |
| C4c | Zmiana limitu przez most OCPP | sterownik potwierdza; most i serwer testowy OCPP w sieci lokalnej |
| C4d | Strona WWW z laptopa | działa jak w B2 |
| C4e | Home Assistant, jeśli B3 się udało | działa jak w B3 |

### C5. Ikona sieci

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C5a | Obserwacja stanu sieci wysyłanego do sterownika i ikony na wyświetlaczu | według opisu protokołu Tuya: 2 = brak routera, 3 = router bez chmury, 4 = połączony z chmurą. Zapisujemy, czy moduł bez internetu nadal wysyła „4”. Ciąg dalszy przy wyłączonym Wi-Fi w D8 |

### C6. Okno godzin, tryb pracy i limit energii, z lokalnym czasem

**Cel.** Te funkcje ma sam sterownik. Ustalić, czy je zgłasza i wykonuje, kiedy ma godzinę z lokalnego serwera. Przy okazji powstanie lista pól do dodania w produkcie Shelly.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C6a | Serwer z przesunięciem: za 2 min wybije godzina G. Z menu: tryb „harmonogram”, okno od G do G+1. Symulator w stanie „ładuje” | sterownik zgłasza tryb „harmonogram” i okno (G, G+1); przed G stan „czeka”, o G ładowanie rusza |
| C6b | Przesunięcie na 2 min przed G+1 | o G+1 ładowanie staje |
| C6c | Z menu: tryb „energia”, limit 1 kWh | sterownik zgłasza tryb „energia” i, oby, limit energii; bez obciążenia licznik nie ruszy, więc sprawdzamy tylko zgłaszanie |

**Ustalone 29.09 przy wgrywaniu v4.2 (poziom B):** zapis okna z modułu działa (2 bajty). Sterownik po przyjęciu okna **sam przechodzi w tryb „harmonogram”** i poza oknem przestaje ładować. Okna 0–0 nie przyjmuje. W C6 trzeba to uwzględnić: po teście ustawić tryb „natychmiast”.

**Zapis tych ustawień z modułu to osobny etap.** Moduł nie ma polecenia do zapisu dowolnego punktu danych; zapisuje tylko skrypt usługi, do pól zdefiniowanych w produkcie. Trzeba więc dodać pola w portalu i wgrać nową konfigurację, a to kasuje Wi-Fi modułu.

### C7. Harmonogram i webhook bez internetu

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C7a | Harmonogram z B4 na poziomie C | zadania odpalają o czasie; godzina z lokalnego serwera |
| C7b | Webhook z B5 na poziomie C | wywołania dochodzą do laptopa jak w B5 |

### C8. Zanik zasilania

**Cel.** Rozstrzygnąć, co pamięta sterownik, co moduł i kto komu narzuca wartość po starcie.

**Co przewiduje kod naszego skryptu.** Po starcie skrypt czyta limit i włącznik ze sterownika i nadpisuje nimi pola w module. Do sterownika pisze tylko wtedy, gdy pole się zmieni na wartość inną niż ostatnio otrzymana ze sterownika. Normalnie wygrywa więc sterownik.

Słabe miejsce: zanim sterownik pierwszy raz zgłosi limit, skrypt nie zna jego wartości. Każda zmiana pola w tych kilku sekundach pójdzie do sterownika. Taką zmianą może być odtworzenie zapamiętanej wartości, harmonogram albo polecenie z aplikacji. Dlatego w C8d patrzymy na pierwsze sekundy logu.

| Krok | Co robimy | Wynik oczekiwany / co zapisujemy |
| --- | --- | --- |
| C8a | Stan wyjściowy z logu: limit 10 A ustawiony **z modułu**, ładowanie wyłączone, symulator „podłączone”. W drugiej rundzie dodatkowo tryb „harmonogram” z oknem, limit energii 1 kWh, wpis klucz-wartość i harmonogram z B4 | pełny zrzut wszystkich punktów danych i pól modułu |
| C8b | Wyłącznik ładowarki: wyłączyć na 30 s, włączyć | moduł i sterownik startują; monitor wraca |
| C8c | Zrzut po starcie porównany z C8a | które wartości sterownik zachował; oczekujemy limitu prądu, trybu, okna i limitu energii |
| C8d | Pierwsze sekundy logu po starcie | **czy moduł wysłał zapis limitu albo włącznika, zanim sterownik zgłosił swoje wartości** |
| C8e | Włącznik: przed wyłączeniem „włączone”, symulator „ładuje” | czy po powrocie zasilania ładowanie rusza samo, czy czeka na polecenie |
| C8f | Czas: po ilu sekundach od startu sterownik dostał poprawną godzinę | z logu |
| C8g | Moduł: Wi-Fi, stały adres, MQTT, serwer czasu, harmonogram, webhook, wpis klucz-wartość | wszystko na miejscu |
| C8h | Energia i czas sesji w polach modułu | energia sesji 0, bo bez obciążenia licznik nie rośnie. Czas sesji niewiarygodny: skrypt liczy go z zegara modułu, więc skacze przy każdej zmianie zegara. 29.09 przy korekcie zegara skoczył o 45 min (770 → 815), a po restarcie modułu na 1066 min, czyli mniej więcej tyle, ile moduł pracował przed restartem. Do poprawy w skrypcie: liczyć z czasu pracy modułu, nie z zegara |
| C8i | Powtórka C8a–C8d z limitem ustawionym **z menu ładowarki** | czy moduł po starcie nie nadpisze ustawienia z menu swoją zapamiętaną wartością |

**Dlaczego to ważne.** Klient ustawia z menu 8 A, bo ma słabe zabezpieczenie. Moduł pamięta z aplikacji 16 A. Po zaniku zasilania moduł wstaje, wysyła 16 A i ładowarka rusza z 16 A. Taki błąd byłby groźny, dlatego C8d i C8i to najważniejsze punkty całego programu.

**Rekomendacja, jeśli C8c pokaże, że sterownik sam pamięta limit i włącznik.** Wyłączyć w portalu zapamiętywanie tych dwóch pól. Wtedy nic nie dają, bo sterownik i tak zgłasza swoje wartości po starcie, a są jedynym źródłem opisanego ryzyka.

### C9. Restart samego modułu w trakcie ładowania

**Cel.** Sterownik pracuje dalej, moduł znika na kilkanaście sekund. Tak będzie przy każdej aktualizacji oprogramowania modułu.

| Krok | Co robimy | Wynik oczekiwany / co zapisujemy |
| --- | --- | --- |
| C9a | Symulator „ładuje”; restart modułu poleceniem | czy sterownik przerywa ładowanie, gdy moduł przestaje dawać znak życia |
| C9b | Po powrocie modułu | co moduł wysyła do sterownika; czy pola w module zgadzają się ze sterownikiem |

### C10. Serwer czasu podany przez router, opcjonalnie

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C10a | Administrator ustawia w routerze rozgłaszanie adresu serwera czasu (opcja 42 przy przydzielaniu adresów); w module pole serwera czasu puste; moduł na adresie automatycznym | czy moduł sam bierze ten serwer. Jeśli tak, w firmach godzina działałaby bez konfiguracji |

### C11. Aplikacja Tuya bez internetu, opcjonalnie, porównanie

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C11a | Q11 z modułem Tuya odcięta od internetu regułą w routerze; telefon w tej samej sieci; aplikacja Tuya | czy aplikacja steruje ładowarką lokalnie |

### C12. Harmonogram Tuya bez internetu, opcjonalnie, porównanie

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| C12a | Wpis harmonogramu w aplikacji Tuya za 10 min; potem ładowarka odcięta od internetu regułą w routerze | jeśli wpis się wykona, wykonuje go moduł Tuya, a nie chmura |

## 3. Kolejność i czas

| Kolejność | Testy | Czas |
| --- | --- | --- |
| 1 | P1–P3, C1–C5 | 1 h 25 min |
| 2 | C8 pierwsza runda, C9 | 1 h 5 min |
| 3 | C6 z narzędziem, C7 | 1 h 20 min |
| 4 | C8 druga runda | 45 min |
| 5 | P4 powrót na poziom B | 10 min |
| — | C10–C12, opcjonalnie | gdy administrator ustawi router |

Razem około 4 h 45 min. Miejsce tych testów w kolejności całego programu: dokument 00, rozdział 5.

## 4. Wyniki

| Test | Wynik | Co zaobserwowano | Data |
| --- | --- | --- | --- |
| P3 moduł bez internetu | | | |
| Przygotowanie P1–P3 | ✔ | 30.09 13:56: moduł na stałym adresie 192.168.0.238 bez bramy i bez serwera nazw. Z modułu: nazwa strony w internecie „Host not found”, adres IP w internecie „Timed out”; laptop (192.168.0.57:8099) odpowiada. Punktu dostępowego nie włączaliśmy (jest otwarty, bez hasła); droga ratunkowa: ten sam adres i podsieć | 30.09 13:57 |
| C1 aplikacja w sieci lokalnej | ✘ z B1 | Wynika z B1: aplikacja steruje tylko przez chmurę | 30.09 |
| C2 sterownik z modułu | ✔ z uwagą | 30.09 14:57, bez internetu. C2a: tester B → C; moduł pokazał „ładuje” i sygnał 6 V, webhooki włącznik „wł.”, „ładuje”, start ładowania. Stanu „podłączone” (B) sterownik nie zgłosił, tak jak w B5b. C2b: limit 12 A z modułu przy ładowaniu — sterownik potwierdził w 1 s (najpierw stare 8, potem 12), wyświetlacz pokazał 12 A | 30.09 14:58 |
| C3 godzina po starcie | ◐ | 30.09 14:06, zanik zasilania całej ładowarki, moduł bez internetu: sterownik dostał poprawną godzinę 23 s po włączeniu (z serwera czasu na laptopie). Co pokazuje wyświetlacz przez te sekundy: do sprawdzenia. Uwaga S-45: bez serwera czasu moduł ma do tego czasu starą, zapamiętaną godzinę | 30.09 14:07 |
| C4 drogi lokalne | ✔ | 30.09 14:08, bez internetu: zapis limitu przez HTTP (210 ms), WebSocket (150 ms) i MQTT przez broker na laptopie; sterownik potwierdził 9, 10 i 8 A w 1–2 s. Strona WWW odpowiada, HA bez błędów. C4c (most OCPP): *korekta 01.10* — most jest (`DevKit\ocpp\most_q11.py`, z 25.09), patrz C4c niżej | 30.09 14:09 |
| C4c most OCPP bez internetu | ✔ | 01.10 11:34–11:36, moduł bez internetu (zapytania do internetu kończą się po czasie). Most i testowy serwer OCPP 1.6J na laptopie (`ws://localhost:9000`). BootNotification: Accepted, StatusNotification: Available, heartbeat co 60 s. Z serwera: limit 10 A (SetChargingProfile: Accepted, sterownik potwierdził 10 A), TriggerMessage status i pomiary (Accepted, pomiary 0, bo tester odłączony), GetConfiguration, limit 12 A (potwierdzony). 25.09 ten sam most działał z modułem mającym internet (tylko chmura wyłączona). Serwera OCPP w internecie nie testowaliśmy. Pełna transakcja ✔ (11:36–11:39, tester A → C → A): StatusNotification „SuspendedEVSE”, potem „Charging” i StartTransaction nr 1 (licznik 0 Wh), MeterValues co 30 s (6 razy, L1 225 V, 0 A), po odłączeniu „Available” i StopTransaction z powodem „EVDisconnected” | 01.10 11:40 |
| C5 ikona sieci | ◐ obserwacja | 30.09 14:5x, bez internetu: moduł co 30 s wysyła sterownikowi stan sieci 4 („połączony z chmurą”), bez zmian. Ikona Wi-Fi na wyświetlaczu co kilkadziesiąt sekund znika i wraca (zdjęcia Dawida). [Z] Sterownik gasi ikonę między meldunkami. Do sprawdzenia: to samo z internetem i po zmianie zgłaszanego stanu na 3 (rejestr S-39) | 30.09 14:57 |
| C6 okno godzin z lokalnym czasem | ✔ | 30.09 15:24–15:31, bez internetu, tester w C. Serwer czasu z przesunięciem (`narzedzia\zegar_przesuniety.py`, w kontenerze zamiast `ntp`; zmiana czasu = restart modułu). Okno 22–23 ustawione z modułu (w menu nie ma okna, tylko opóźnienie): sterownik przeszedł w „harmonogram” i przerwał ładowanie („czeka”). C6a: o 22:00:03 zegara modułu „ładuje”. C6b: po przestawieniu na 22:58 ładowanie trwa, o 23:00:03 „czeka”. **Sterownik wykonuje okno sam, według godziny, którą dostaje od modułu** (odpowiada mu na pytanie o czas co około 18 s). C6c pominięty: sprzężenie limitu energii z trybem znane z B (S-21). Po teście: zwykły serwer czasu, tryb „od razu”, ładuje | 30.09 15:31 |
| C7 harmonogram i webhook | ✔ | 30.09 14:11, bez internetu: zadanie harmonogramu odpaliło co do sekundy (godzina z serwera na laptopie), sterownik potwierdził 11 A; webhooki na zmianę limitu doszły do laptopa (14:08). Zadanie usunięte, limit z powrotem 8 A. Uwaga S-45: po zaniku zasilania bez serwera czasu harmonogram działa według starej godziny | 30.09 14:11 |
| C8 zanik zasilania | ◐ runda 1 | 30.09 14:06, bez internetu. Limit ustawiony z menu (8 A): sterownik go zachował, moduł też; przy starcie moduł nie wysłał sterownikowi żadnego zapisu (log UDP od 21 s). Łącze gotowe po 30 s, skrypt bez komunikatów, godzina 23 s po starcie. Test pamięci (dokument 04): moduł odtwarza wszystko, co zapisuje; sterownik traci okno, tryb harmonogramu i opóźnienie z menu (S-47). C8e ✔ (15:19, tester w C): po zaniku zasilania ładowanie ruszyło samo — sterownik około 30 s po włączeniu zgłosił „ładuje”, limit 12 A, tryb „od razu”; moduł nic nie zapisał, godzinę przekazał po 24 s. Razem z S-47: po mrugnięciu prądu ładowarka ładuje od razu, nawet gdy było ustawione opóźnienie. Zostaje druga runda | 30.09 15:20 |
| C9 restart modułu w trakcie ładowania | ✔ z uwagą | 30.09 15:00–15:07, bez internetu, tester w C: 5 restartów modułu (każdy około 30 s bez modułu, trzy jeden po drugim). Sterownik ładował bez przerwy, na ekranie nic się nie działo (Dawid). Po powrocie moduł nie wysłał zapisu, pola zgodne ze sterownikiem (ładuje, 6 V, 12 A). Uwaga: około 40 s po restarcie przychodzi fałszywy webhook „ładuje” i „start ładowania” (rejestr S-50) | 30.09 15:07 |
| C10 serwer czasu z routera | | | |
| C11 aplikacja Tuya | | | |
| C12 harmonogram Tuya | | | |
