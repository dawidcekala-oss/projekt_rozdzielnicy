# Q11 na Shelly DevKit: wyniki testów lokalnych, MQTT i OCPP
_Raport z testów · AMPERE POINT · 25 września 2026_
FOOTER: AMPERE POINT — Q11 na DevKit: wyniki testów lokalnych, MQTT, OCPP · v1 · 2026-09-25

## Podsumowanie

| Test | Wynik | Najważniejsze |
| --- | --- | --- |
| Praca bez chmury Shelly | ✔ | rozmowa z Q11, polecenia HTTP, WebSocket, MQTT i most OCPP działają przy wyłączonej chmurze |
| Zegar bez internetu | ✔ | bez serwera czasu Q11 dostaje datę z samymi zerami; naprawione lokalnym serwerem czasu w Dockerze |
| MQTT z lokalnym brokerem | ✔ | stan wszystkich pól na osobnych tematach; limit prądu zmieniony przez MQTT i potwierdzony przez Q11 |
| OCPP 1.6J przez most | ✔ | rejestracja, stan, pomiary, zdalny start i limit prądu z serwera OCPP potwierdzony przez Q11 |
| Transakcja OCPP z ładowaniem | ◐ | logika gotowa; test wymaga auta albo symulatora pobierającego prąd |

Chmura Shelly w DevKicie jest wyłączona od 11:48. Aplikacja Shelly pokazuje go jako niedostępny, dopóki chmura nie wróci. Włączenie to jedno polecenie.

## 1. Praca bez chmury

Chmurę wyłączyłem poleceniem w sieci lokalnej, bez restartu. Po wyłączeniu DevKit dalej rozmawia z Q11 co kilka sekund, a wszystkie kanały lokalne działają: polecenia HTTP, WebSocket, MQTT i most OCPP opisane niżej.

## 2. Zegar bez internetu

**Wynik: bez serwera czasu Q11 dostaje błędną datę.** Test: DevKit dostał nieosiągalny serwer czasu i restart.

| Chwila | Co wysłał moduł do Q11 na pytanie o czas | Znaczenie |
| --- | --- | --- |
| po restarcie bez serwera czasu | `01 00 00 00 00 00 00 00` | „czas ważny”, ale rok 0, miesiąc 0, godzina 0 |
| po ręcznym ustawieniu godziny z laptopa | `01 00 00 00 00 00 00 00` | bez zmian: ręczny czas nie trafia do Q11 |
| po restarcie z serwerem czasu | `01 1A 09 19 0B 33 12 05` | 2026-09-25 11:51:18, piątek; poprawnie |

**Mechanizm.** Obsługa Tuya w module podaje Q11 czas tylko wtedy, gdy DevKit zsynchronizował się z serwerem czasu. Ręczne ustawienie godziny zmienia zegar DevKitu, ale nie odblokowuje czasu dla Q11. Q11 może więc przyjąć datę zerową jako ważną, co grozi błędnym działaniem harmonogramu ładowania.

**Wniosek.** Instalacja bez internetu potrzebuje serwera czasu w sieci lokalnej. Router biura na porcie 123 nie odpowiada. Do wyboru:
- włączyć serwer czasu w routerze, jeśli ma taką opcję,
- uruchomić serwer czasu na komputerze z HA; na docelowym OptiPlexie z Linuksem to jeden kontener.

Serwer czasu wpisuje się w DevKit jednym poleceniem. Most OCPP i tak ustawia godzinę DevKitu po restarcie, ale to pomaga tylko harmonogramom Shelly, a nie Q11.

> **Ważne:** wdrożone 25.09 o 12:50. Serwer czasu chrony działa w Dockerze na laptopie: kontener `ntp`, obraz `ampere-ntp:1` zbudowany z oficjalnego Alpine, port 123/udp, pliki w `DevKit\ntp`. Ustawienie „local stratum 10” sprawia, że podaje czas także bez internetu, wtedy z zegara komputera. DevKit ma w ustawieniach serwer `192.168.0.57`. Wynik: synchronizacja 18 s po restarcie, a Q11 dostała na pytanie o czas `01 1A 09 19 0C 32 0C 05`, czyli 2026-09-25 12:50:12, piątek.

<!-- PAGEBREAK -->

## 3. MQTT

**Broker:** Mosquitto 2.1.2 w Dockerze na laptopie, port 1883, kontener `mosquitto` z automatycznym startem. Konfiguracja leży w `DevKit\mqtt\config\mosquitto.conf`. Na razie broker wpuszcza wszystkich bez hasła, więc nadaje się tylko do testów w sieci biura.

**DevKit:** broker `192.168.0.57:1883`, przedrostek tematów `ampere/q11dev`, powiadomienia i polecenia włączone. Zmianę ustawień zrobiłem poleceniem w sieci lokalnej, bez portalu.

| Temat | Zawartość |
| --- | --- |
| `ampere/q11dev/online` | `true` albo `false`, obecność DevKitu |
| `ampere/q11dev/status/boolean:200` | włączenie ładowania |
| `ampere/q11dev/status/number:200` | limit prądu w A |
| `ampere/q11dev/status/enum:200` | stan ładowarki, np. `charger_free` |
| `ampere/q11dev/status/object:200` | fazy: napięcie, prąd, moc, licznik |
| `ampere/q11dev/status/number:201`, `number:202` | czas i energia sesji |
| `ampere/q11dev/events/rpc` | powiadomienia o każdej zmianie |
| `ampere/q11dev/rpc` | polecenia do DevKitu |

**Test sterowania:** wiadomość na `ampere/q11dev/rpc` z poleceniem ustawienia limitu na 10 A. Q11 potwierdziła 10 A, a następna wiadomość przywróciła 12 A. Q11 potwierdziła i to.

## 4. OCPP 1.6J przez most

Most `DevKit\ocpp\most_q11.py` łączy się z DevKitem przez WebSocket w sieci lokalnej, a wobec serwera OCPP występuje jako ładowarka `Q11-543204516334`. Testowy serwer `DevKit\ocpp\csms_test.py` zapisuje każdy komunikat w `DevKit\logi\ocpp_csms_*.log`.

| Krok | Wynik |
| --- | --- |
| BootNotification | Accepted, heartbeat co 60 s |
| StatusNotification | Available, bo Q11 jest wolna, a auto odłączone |
| TriggerMessage, pomiary | energia 0 Wh, moc 0 W, prąd i napięcie na trzech fazach, oferowany prąd 10 A |
| SetChargingProfile 10 A | Accepted; Q11 potwierdziła 10 A po około 2 s |
| SetChargingProfile 12 A | Accepted; Q11 potwierdziła 12 A |
| GetConfiguration | lista ustawień mostu |
| RemoteStartTransaction z identyfikatorem karty KARTA-TEST | Accepted; most włącza ładowanie i zapamiętuje identyfikator |

**Czego jeszcze nie sprawdziłem:** pełnej transakcji. Most wysyła StartTransaction, gdy Q11 przejdzie w stan „ładuje”, pomiary co 30 s w trakcie i StopTransaction przy końcu ładowania, odłączeniu auta albo zdalnym zatrzymaniu. Do testu potrzebne jest auto albo symulator pobierający prąd.

**Jak uruchomić,** w dwóch oknach wiersza poleceń:
- serwer testowy: `python -u DevKit\ocpp\csms_test.py`
- most: `python -u DevKit\ocpp\most_q11.py 192.168.0.238 ws://localhost:9000`

Polecenia do ładowarki wpisuje się do pliku `DevKit\ocpp\polecenia.txt`, po jednym w wierszu: `start`, `stop`, `limit 10`, `status`, `meter`, `config`.

## 5. Otwarte sprawy

1. **Serwer czasu na stałe.** Działa na laptopie, więc DevKit ma czas tylko wtedy, gdy laptop jest włączony. Docelowo ten sam kontener na OptiPlexie razem z HA. Zegar laptopa odbiega od wzorca o około 2 s, bo usługa czasu Windows jest wyłączona; dla harmonogramu ładowania to bez znaczenia.
2. **Pełna transakcja OCPP** z autem albo symulatorem.
3. **Licznik całkowity podaje 0 kWh.** Do porównania z wyświetlaczem ładowarki.
4. **Nowe pola w konfiguracji v2:** błędy, sygnał z auta, temperatura i licznik jako osobne pola. OCPP potrzebuje ich do kodów błędów w StatusNotification.
5. **Most na stałe.** Dziś działa na laptopie, póki trwa sesja. Docelowo jako usługa na OptiPlexie albo wariant serwerowy, w którym DevKit sam łączy się z mostem przez wychodzący WebSocket.
6. **Hasło do brokera MQTT** przed jakimkolwiek użyciem poza testem.
7. **Chmura Shelly** zostaje wyłączona do dalszych testów, zgodnie z decyzją z 25.09.
