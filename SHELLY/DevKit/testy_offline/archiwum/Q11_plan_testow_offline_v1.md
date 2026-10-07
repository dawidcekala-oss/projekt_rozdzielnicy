# Plan testów offline: Q11 z modułem Shelly
_Co jeszcze trzeba sprawdzić, żeby potwierdzić, że bez internetu Q11 na Shelly umie wszystko to, co Q11 na Tuya, i że po zaniku zasilania pamięta to, co powinna · AMPERE POINT · 28 września 2026 · oprac. Dawid Cekała_
FOOTER: AMPERE POINT — plan testów offline · Q11 z modułem Shelly · v1 · 2026-09-28

## W skrócie {-}

- **Co Tuya daje offline?** Prawie nic po stronie modułu: aplikacja Tuya bez chmury nie działa. Wszystko, co działa bez internetu, siedzi w sterowniku Q11: menu, przyciski, start po podłączeniu auta, limit prądu, okno godzin, limit energii, wyświetlacz. Moduł Tuya dokłada tylko ikonę sieci i godzinę.
- **Co więc sprawdzamy?** Dwie rzeczy. Po pierwsze, że funkcje sterownika nadal działają, gdy w miejscu modułu Tuya siedzi Shelly, a internetu nie ma. Po drugie, że to, co moduł Shelly daje od siebie bez chmury, naprawdę działa: Bluetooth, harmonogramy w module, webhooki, pamięć ustawień.
- **Trzecia sprawa: zanik zasilania.** Moduł jest zasilany z płytki, więc gaśnie razem z ładowarką. Po powrocie zasilania dwa układy startują naraz i każdy ma własną pamięć. Trzeba sprawdzić, kto komu narzuca wartości i czy nic nie ginie.
- **Kolejność od bezpiecznych do ryzykownych.** Reset sieci z menu ładowarki zostawiamy na koniec, bo może skasować parowanie Wi-Fi modułu.

## 1. Co ma Q11 na Tuya bez internetu, a co Q11 na Shelly

| Funkcja bez internetu | Gdzie siedzi | Q11 na Tuya | Q11 na Shelly | Test |
| --- | --- | --- | --- | --- |
| Start ładowania po podłączeniu auta | sterownik | ✔ | ✔ sprawdzone 25.09 | T2 |
| Limit prądu z menu | sterownik | ✔ | ? nie sprawdzano z menu, tylko z modułu | T2 |
| Okno godzin (punkt 19) | sterownik | ✔ z menu; z aplikacji przez chmurę | ? | T3 |
| Limit energii sesji (punkt 17) | sterownik | ✔ | ? sterownik nigdy nie zgłosił punktu 17 | T3 |
| Tryb pracy: natychmiast, energia, harmonogram (punkt 14) | sterownik | ✔ | ? | T3 |
| Godzina dla sterownika | moduł | z chmury Tuya; bez internetu brak | ✔ z lokalnego serwera czasu, sprawdzone | T2 |
| Ikona sieci na wyświetlaczu | moduł | odbija stan chmury | ✔ moduł zawsze wysyła „4”; ikona świeci nawet bez internetu | T2 |
| Sterowanie z telefonu bez internetu | moduł | ✘ aplikacja Tuya tylko przez chmurę | ? Bluetooth w aplikacji Shelly; strona WWW modułu | T1 |
| Sterowanie z komputera w sieci lokalnej | moduł | ◐ tylko nieoficjalnie, kluczem lokalnym | ✔ HTTP, WebSocket, MQTT, sprawdzone | — |
| Harmonogram w urządzeniu | — | ✘ tylko w chmurze | ? do 20 zadań w module | T4 |
| Powiadomienie o zdarzeniu do własnego systemu | — | ✘ | ? webhooki w module | T4 |
| Pamięć ustawień po zaniku zasilania | sterownik i moduł | sterownik pamięta swoje | ? dwa układy z pamięcią, do rozstrzygnięcia | T5 |
| Reset sieci z menu ładowarki | sterownik → moduł | ✔ moduł Tuya wchodzi w parowanie | ? co robi moduł Shelly na to polecenie | T6 |

## 2. Założenia i przygotowanie

- Chmura Shelly wyłączona przez cały czas, jak dotąd.
- W sieci działają kontenery: broker MQTT i lokalny serwer czasu (192.168.0.57). Serwer czasu musi działać **przed** każdym włączeniem ładowarki, bo moduł pyta o czas zaraz po starcie.
- Monitor logu przez Wi-Fi uruchomiony przed każdym testem; do testów z zanikiem zasilania monitor sam się wznawia po powrocie modułu.
- Symulator auta podłączony: stany „podłączone” (9 V) i „ładuje” (6 V). Bez obciążenia prądowego; prąd i moc faz zostają poza tym planem.
- Laptop ma kartę Bluetooth (Intel); do testów z komputera biblioteka `bleak` w Pythonie. Telefon z aplikacją Shelly do testu z użytkownikiem.
- Wi-Fi laptopa nie ruszamy. Zanik Wi-Fi symulujemy po stronie modułu, nie laptopa.
- Po każdym teście zapis w tabeli wyników: ✔ działa, ◐ działa z zastrzeżeniem, ✘ nie działa, z opisem tego, co zaobserwowano.

## 3. Testy

### T1. Bluetooth

**Cel.** Potwierdzić, że ładowarką da się sterować bez Wi-Fi i bez internetu, z telefonu i z komputera.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| 1a | Skan Bluetooth z laptopa | moduł widoczny pod swoją nazwą, z reklamą Shelly |
| 1b | Polecenie przez Bluetooth z laptopa: odczyt stanu, potem zmiana limitu prądu na 10 A | sterownik potwierdza w logu w ciągu 1 s, tak jak przy Wi-Fi |
| 1c | Telefon: Wi-Fi i dane komórkowe wyłączone, aplikacja Shelly przez Bluetooth: włącz/wyłącz ładowanie, zmiana limitu | to samo co 1b; sprawdzamy też, ile trwa połączenie |
| 1d | Moduł bez Wi-Fi: przez Bluetooth wyłączamy stację Wi-Fi modułu (wcześniej upewniamy się, że własna sieć modułu, punkt dostępowy, jest włączona jako droga awaryjna); powtarzamy 1b i 1c | działa bez Wi-Fi; log niedostępny, więc dowodem jest wyświetlacz ładowarki i odpowiedź przez Bluetooth |
| 1e | Przez Bluetooth włączamy stację Wi-Fi z powrotem | moduł wraca do sieci biura w ciągu minuty, log wraca |

**Ryzyko.** Jeśli w 1d Bluetooth zawiedzie, moduł zostaje bez Wi-Fi. Droga powrotu: własna sieć modułu (punkt dostępowy) z telefonu. Dlatego 1d dopiero po udanych 1b i 1c.

**Narzędzie do napisania.** `narzedzia\ble_rpc.py`: klient poleceń Shelly przez Bluetooth (ta sama treść JSON co przez Wi-Fi, opakowana w ramkę Bluetooth Shelly).

### T2. Funkcje sterownika bez internetu

**Cel.** Potwierdzić, że sterownik robi swoje, gdy moduł ma tylko sieć lokalną.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| 2a | Symulator: wolne → podłączone → ładuje | sterownik przechodzi stany 0 → 1 → 4 (punkt 3), zamyka stycznik; moduł pokazuje to w polach |
| 2b | Limit prądu z **menu ładowarki**: 8 A | sterownik zgłasza punkt 4 = 8 samoistnie; pole w module aktualizuje się bez naszego zapisu |
| 2c | Limit prądu z modułu przy ładowaniu: 12 A | sterownik potwierdza w 1 s; wyświetlacz pokazuje 12 A |
| 2d | Godzina po starcie: włączamy ładowarkę, patrzymy na pierwsze ramki czasu | do ~20 s moduł odpowiada zerową datą, potem poprawną; sprawdzamy, co w tym czasie pokazuje wyświetlacz |
| 2e | Ikona sieci: obserwacja | świeci przy samej sieci lokalnej; zapisujemy jako cechę do decyzji: czy „4” bez internetu to dobrze |

### T3. Okno godzin, tryb pracy, limit energii

**Cel.** Trzy funkcje, których Tuya obsługuje z aplikacji, a my na razie tylko z menu. Ustalić, czy sterownik je zgłasza i wykonuje, oraz co trzeba dodać w produkcie Shelly.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| 3a | Z menu ładowarki: tryb „harmonogram”, okno np. od bieżącej godziny + 2 min do + 5 min; symulator w stanie „ładuje” | sterownik zgłasza punkt 14 = 2 i punkt 19 z godzinami; ładowanie rusza w oknie i staje po nim; poza oknem stan „czeka” |
| 3b | To samo bez ważnego czasu: serwer czasu zatrzymany, ładowarka włączona na nowo | sterownik dostaje zerową datę; zapisujemy, co robi z oknem: nie startuje, startuje od razu, czy coś innego. Potem serwer czasu z powrotem |
| 3c | Z menu: tryb „energia”, limit np. 1 kWh | sterownik zgłasza punkt 14 = 1 i, mamy nadzieję, punkt 17; bez obciążenia licznik nie ruszy, więc sprawdzamy tylko zgłaszanie |
| 3d | Zapis punktów 14, 17 i 19 z modułu (surowym poleceniem do punktu danych, bez zmiany produktu) | sterownik przyjmuje i pokazuje w menu |

**Wynik uboczny.** Lista pól do dodania w portalu: tryb pracy, okno godzin, limit energii, plus błędy, sygnał z auta i temperatura z poprzedniej listy.

### T4. Harmonogram, webhook i pamięć w module

**Cel.** To, co moduł Shelly daje ponad Tuya, ma działać bez chmury i przetrwać restart.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| 4a | Harmonogram w module: o +2 min ustaw limit 6 A, o +4 min 16 A | oba zadania odpalają o czasie, sterownik potwierdza |
| 4b | Webhook: przy zmianie stanu ładowania moduł wywołuje adres na laptopie (mały nasłuch HTTP w Pythonie) | wywołanie przychodzi przy każdej zmianie, z treścią zdarzenia |
| 4c | Pamięć klucz-wartość: zapis wartości testowej | odczyt daje to samo; sprawdzenie po T5, czy przetrwała zanik zasilania |
| 4d | Harmonogram i webhook po restarcie modułu (samo polecenie restartu, bez zaniku zasilania) | nadal są i działają |

### T5. Zanik zasilania

**Cel.** Rozstrzygnąć, co pamięta sterownik, co moduł, i kto komu narzuca wartość po starcie.

| Krok | Co robimy | Wynik oczekiwany / co zapisujemy |
| --- | --- | --- |
| 5a | Stan wyjściowy, zapisany z logu: limit 10 A ustawiony **z modułu**, ładowanie wyłączone, tryb „harmonogram” z oknem, limit energii 1 kWh, wpis w pamięci klucz-wartość, harmonogram z T4, symulator w stanie „podłączone” | pełny zrzut wszystkich punktów danych i pól modułu |
| 5b | Wyłącznik ładowarki: wyłączyć na 30 s, włączyć | moduł i sterownik startują; monitor wraca |
| 5c | Zrzut po starcie (odpowiedź sterownika na zapytanie o wszystkie punkty) porównany ze stanem 5a | które wartości sterownik zachował: oczekujemy limit prądu, tryb, okno, limit energii; zapisujemy każdą różnicę |
| 5d | Pola modułu po starcie a wartości sterownika | pole „limit prądu” w module jest zapamiętywane w jego pamięci. Jeśli sterownik wstał z inną wartością niż moduł: kto wygrał? Czy moduł wysłał swoją wartość do sterownika (zapis w logu), czy przyjął jego? Zapis w logu rozstrzyga |
| 5e | To samo dla włącznika ładowania: przed wyłączeniem „włączone”, symulator w stanie „ładuje” | czy po powrocie zasilania ładowanie rusza samo, czy czeka na polecenie; to jest zachowanie sterownika, ważne dla klienta |
| 5f | Czas: ile sekund po starcie sterownik dostał poprawną godzinę | z logu; wcześniej zerowa data |
| 5g | Moduł: konfiguracja Wi-Fi, MQTT, serwer czasu, harmonogram, webhook, wpis klucz-wartość | wszystko na miejscu |
| 5h | Energia i czas sesji w polach modułu | oczekujemy zera: znany brak, do przeniesienia do pamięci klucz-wartość |
| 5i | Powtórka 5a–5c z limitem ustawionym **z menu ładowarki** zamiast z modułu | sprawdzamy drugi kierunek: czy moduł po starcie nie nadpisze ustawienia z menu swoją zapamiętaną wartością |

**Dlaczego to ważne.** Przykład: klient ustawia z menu 8 A, bo ma słabe zabezpieczenie. Moduł pamięta z aplikacji 16 A. Po zaniku zasilania moduł wstaje, wysyła „16 A” i ładowarka rusza z 16 A. Taki błąd byłby groźny, więc 5d i 5i to najważniejsze punkty planu.

### T6. Reset sieci z menu ładowarki

**Cel.** W Q11 na Tuya pozycja menu „reset sieci” wprowadza moduł w parowanie. Sprawdzić, co polecenie sterownika robi z modułem Shelly.

| Krok | Co robimy | Wynik oczekiwany |
| --- | --- | --- |
| 6a | Monitor na najwyższym poziomie logu; z menu ładowarki: reset sieci | w logu ramka od sterownika (kod resetu Wi-Fi) i reakcja modułu: ignoruje, kasuje Wi-Fi, wchodzi w parowanie |
| 6b | Jeśli moduł skasował Wi-Fi: ponowne parowanie z telefonu przez Bluetooth, jak 24.09 | moduł wraca do sieci |

**Ryzyko.** Utrata Wi-Fi modułu; dlatego na końcu. Co się stanie, zapisujemy jako fakt do dokumentacji dla fabryki (pytanie 8).

## 4. Kolejność i czas

| Kolejność | Test | Ryzyko | Szacowany czas | Potrzebny użytkownik |
| --- | --- | --- | --- | --- |
| 1 | T1a–T1c Bluetooth przy działającym Wi-Fi | małe | 1 h z napisaniem narzędzia | tak, do 1c z telefonem |
| 2 | T2 funkcje sterownika | małe | 30 min | tak, menu i symulator |
| 3 | T5 zanik zasilania, pierwsza runda | małe | 45 min | tak, wyłącznik |
| 4 | T3 okno, tryb, limit energii | małe | 45 min | tak, menu |
| 5 | T4 harmonogram, webhook, pamięć | małe | 45 min | nie |
| 6 | T5 druga runda, po T3 i T4 | małe | 30 min | tak |
| 7 | T1d–T1e Bluetooth bez Wi-Fi | średnie | 30 min | tak, telefon jako droga awaryjna |
| 8 | T6 reset sieci z menu | duże | 20 min plus ewentualne parowanie | tak |

Razem około 5 godzin z przerwami. Po wszystkim: tabela wyników do analizy GAP (v4) i uzupełnienie dokumentacji dla fabryki o wyniki T5 i T6.

## 5. Czego ten plan nie obejmuje

- Prąd i moc faz pod obciążeniem, pełna sesja z energią: wymaga obciążenia, osobny test.
- Aktualizacja sterownika przez moduł: wymaga pliku od fabryki.
- Ekran ładowarki w aplikacji Shelly: sprawa portalu, nie offline.
