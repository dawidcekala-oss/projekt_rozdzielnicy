# Testy offline: Q11 z modułem Shelly — przegląd
*Poziomy łączności, porównanie z Tuya, wspólne założenia i kolejność testów z trzech dokumentów · AMPERE POINT · 28 września 2026 · oprac. Dawid Cekała*
FOOTER: AMPERE POINT — testy offline, przegląd · Q11 z modułem Shelly · v1 · 2026-09-28

## W skrócie {-}

- **Cel dla użytkownika.** Zwykły użytkownik, bez Home Assistant, ma prosto sterować ładowarką bez chmury, z aplikacji przez Bluetooth albo ze strony modułu. Po zaniku zasilania ładowarka ma pamiętać to, co powinna.
- **Trzy dokumenty testów, po jednym na poziom łączności:**

| Dokument | Poziom | Testy |
| --- | --- | --- |
| 01 Testy bez chmury | B: Wi-Fi i internet są, chmura Shelly wyłączona | B1–B12 |
| 02 Testy bez internetu | C: Wi-Fi i sieć lokalna są, internetu nie ma | C1–C12 |
| 03 Testy bez Wi-Fi | D: bez routera; Bluetooth albo sieć modułu | D1–D9 |

- **Ten dokument** zawiera poziomy łączności, pojęcia, porównanie z Tuya w trzech tabelach, wspólne założenia i kolejność wszystkich testów.
- **Najważniejsze testy:** C8, zanik zasilania: czy moduł po starcie nie narzuci sterownikowi zapamiętanego limitu prądu. D5 i D6: godzina bez Wi-Fi.
- **Poprzednie wersje planu** (v1–v3) leżą w podfolderze `archiwum`. Stare numery testów T0–T7 mają odpowiedniki w rozdziale 7.

## 1. Poziomy łączności

„Offline” może znaczyć kilka różnych rzeczy. Rozróżniamy pięć poziomów:

| Poziom | Co działa | Czego nie ma | Przykład z życia | Dokument |
| --- | --- | --- | --- | --- |
| A. Z chmurą | Wi-Fi, internet, chmura producenta | — | zwykła praca; aplikacja z dowolnego miejsca | — |
| B. Bez chmury | Wi-Fi i internet | chmura producenta wyłączona w module | nasze próby od 25.09 | 01 |
| C. Bez internetu | Wi-Fi i sieć lokalna | internet | awaria łącza; firma, która nie wpuszcza ładowarek do internetu | 02 |
| D. Bez Wi-Fi | Bluetooth albo własna sieć modułu, telefon obok ładowarki | router | garaż bez zasięgu Wi-Fi | 03 |
| E. Bez niczego | sama ładowarka | żadnej łączności | tylko menu i przyciski | 03, funkcje sterownika |

Na poziomie B większość już sprawdziliśmy. Poziomu C dotąd naprawdę nie sprawdzaliśmy: internet był zawsze w tle, a jego brak symulowaliśmy tylko dla serwera czasu.

## 2. Pojęcia

- **Menu ładowarki.** Ustawienia na samej Q11: wyświetlacz i dwa przyciski na obudowie, 5 języków. Działa bez żadnego modułu. „Z menu” znaczy: ktoś stoi przy ładowarce i ustawia przyciskami.
- **Okno godzin ładowania.** Ustawienie sterownika Q11: godzina od i godzina do, w których wolno ładować, np. 22–6 dla nocnej taryfy. Działa w trybie „harmonogram”. Sterownik pilnuje okna sam, potrzebuje tylko aktualnej godziny od modułu. Zapisane w dwóch bajtach: godzina startu i godzina końca, **bez minut**.
- **Harmonogram w aplikacji Tuya.** Wpisy tworzy aplikacja, a przechowuje chmura. Telefon do wykonania nie jest potrzebny. Kto wykonuje wpis, nie jest rozstrzygnięte, bo źródła są sprzeczne. Za chmurą przemawia definicja produktu Q21 w Tuya: *CloudTiming: „cloud timing without local timing”*. Za modułem Tuya przemawiają logi ładowarki testowej (Q11 PRO): wykonanie wpisu widać tylko jako raport samej ładowarki, bez polecenia z chmury, które pojawia się przy scenach. Rozstrzyga test C12.
- **Harmonogram w module Shelly.** Do 20 zadań zapisanych w samym module, np. „o 22:00 ustaw 16 A”. Moduł wykonuje je sam, bez chmury i internetu. Potrzebuje godziny.
- **API.** Zestaw poleceń, którymi inne programy rozmawiają z modułem, np. „podaj stan” albo „ustaw limit 10 A”. Te same polecenia idą różnymi drogami: HTTP, WebSocket, MQTT, Bluetooth.
- **Webhook.** Adres WWW, który moduł **sam** wywołuje, gdy coś się stanie, np. „zaczęło się ładowanie”. To odwrotność API: przy API program pyta moduł, przy webhooku moduł sam zawiadamia program.
- **Zapamiętywanie pola.** Ustawienie pola w portalu Shelly („persisted”): moduł trzyma wartość w swojej pamięci i po restarcie ją odtwarza. U nas zapamiętywane są limit prądu i włącznik ładowania.
- **Sieć modułu.** Moduł może sam wystawić sieć Wi-Fi (punkt dostępowy), do której łączy się telefon, bez routera. **Stacja Wi-Fi** to druga strona: moduł jako klient sieci biura.
- **Serwer czasu.** Urządzenie w sieci, od którego moduł pobiera godzinę. Z internetem to serwer publiczny; bez internetu trzeba mieć własny w sieci lokalnej.

## 3. Tuya a Shelly na każdym poziomie łączności

Trzy tabele, po jednej na poziom. W każdej: co może Q11 na Tuya, co może Q11 na Shelly i czy to sprawdziliśmy.

**Czy działa:** ✔ działa · ◐ częściowo · ✘ nie działa · ? nie wiadomo.

**Sprawdzone?:**
- **tak** — sprawdzone u nas na sprzęcie, z datą;
- **z użytkowania** — znane z pracy ładowarek u klientów i w serwisie, bez osobnego testu;
- **z dokumentacji** — wiemy od producenta, nie sprawdzaliśmy;
- **wniosek** — wynika z budowy systemu, nikt nie sprawdzał;
- **nie → B…, C…, D…** — sprawdzi test z dokumentu 01, 02 albo 03.

Funkcje samego sterownika, czyli menu, przyciski, start po podłączeniu auta i limit z menu, nie zależą od łączności. Są w tabeli 3.3, ale obowiązują na każdym poziomie.

### 3.1 Bez chmury: Wi-Fi i internet są, chmury producenta nie ma

Tuya nie ma wyłącznika chmury. Dla Tuya ten poziom znaczy: internet jest, ale z chmury Tuya nie korzystamy, bo jest niedostępna albo zablokowana.

| Funkcja | Q11 na Tuya | Sprawdzone? | Q11 na Shelly | Sprawdzone? |
| --- | --- | --- | --- | --- |
| Sterowanie z telefonu spoza domu | ✘ zdalny dostęp idzie przez chmurę | wniosek | ✘ tak samo | nie → B1 |
| Aplikacja producenta w tej samej sieci | ? polecenia idą lokalnie, ale do logowania aplikacja potrzebuje chmury | polecenia lokalne: tak, 07.09; bez chmury: nie | ? | nie → B1 |
| Strona WWW modułu w przeglądarce | ✘ moduł Tuya jej nie ma | z dokumentacji | ◐ działa; na produkcie Q11 jeszcze nie sprawdzona | tak, 24.09 na symulatorze; Q11 → B2 |
| Sterowanie z komputera w sieci lokalnej | ◐ tylko kluczem lokalnym, który trzeba raz pobrać z konta Tuya | tak, nasza integracja Home Assistant | ✔ HTTP i WebSocket, bez klucza | tak, 25.09 |
| Home Assistant | ◐ tuya local z naszym profilem | tak, 24.09 | ? oficjalna integracja Shelly | nie → B3 |
| MQTT do własnego systemu | ✘ moduł łączy się tylko z brokerem w chmurze Tuya | wniosek | ✔ własny broker | tak, 25.09 |
| OCPP | ✘ | wniosek | ◐ przez most; bez pełnej transakcji | tak, 25.09 |
| Moduł sam łączy się z naszym serwerem | ✘ tylko z chmurą Tuya | wniosek | ? wychodzący WebSocket | nie → B8 |
| Godzina dla sterownika | ? przychodzi z chmury Tuya | wniosek | ✔ z publicznego serwera czasu | tak, 25.09, 11:51 |
| Harmonogram | ? zależy, kto wykonuje wpis: chmura czy moduł | nie → C12 | ? do 20 zadań w module | nie → B4 |
| Powiadomienie do własnego systemu | ✘ | wniosek | ? webhook | nie → B5 |
| Granice API: wartości spoza zakresu, hasło, połączenia naraz | — | — | ? | nie → B7, B9, B11 |
| Ikona sieci na wyświetlaczu | ? | nie | ◐ pokazuje „chmura”, choć chmury nie ma | tak, 25.09 |
| Aktualizacja oprogramowania modułu | ✘ tylko z chmury Tuya | wniosek | ◐ z portalu przez Bluetooth; komputer potrzebuje internetu, moduł nie | tak, 24.09 |

**Wniosek.** Shelly bez chmury traci zdalny dostęp z telefonu, a zyskuje wszystko lokalnie: API, MQTT, OCPP przez most i godzinę z internetu. Większość z tego sprawdziliśmy 24–25.09. Tuya bez chmury działa lokalnie tylko u kogoś, kto pobierze klucz lokalny i postawi Home Assistant.

### 3.2 Bez internetu: Wi-Fi i sieć lokalna są, internetu nie ma

Zdalny dostęp i wszystko, co idzie przez chmurę, odpada w obu systemach, więc tych wierszy tu nie powtarzamy.

| Funkcja | Q11 na Tuya | Sprawdzone? | Q11 na Shelly | Sprawdzone? |
| --- | --- | --- | --- | --- |
| Aplikacja producenta w tej samej sieci | ? polecenia idą lokalnie, ale logowanie wymaga chmury | nie → C11 | ? | nie → C1 |
| Strona WWW modułu | ✘ | z dokumentacji | ◐ działa; Q11 jeszcze nie | tak, 24.09 na symulatorze; bez internetu → C4 |
| Sterowanie z komputera w sieci lokalnej | ◐ kluczem lokalnym; ruch zostaje w sieci | nie | ✔ ruch zostaje w sieci | tak, 25.09, ale z internetem w tle; bez → C4 |
| Home Assistant | ◐ tuya local | nie | ? | nie → B3, C4 |
| MQTT, własny broker | ✘ | wniosek | ✔ | tak, 25.09, z internetem w tle; bez → C4 |
| OCPP przez most | ✘ | wniosek | ◐ most w sieci lokalnej | tak, 25.09, z internetem w tle; bez → C4 |
| Godzina dla sterownika | ✘ czas tylko z chmury Tuya | wniosek | ◐ tylko z lokalnym serwerem czasu; bez niego zerowa data | tak, 25.09, oba przypadki; po starcie → C3 |
| Serwer czasu podany przez router | — | — | ? | nie → C10 |
| Okno godzin ładowania | ? sterownik ma okno, ale nie ma godziny | nie | ? z lokalnym serwerem czasu | nie → C6 |
| Harmonogram | ? | nie → C12 | ? z lokalnym serwerem czasu | nie → C7 |
| Powiadomienie do własnego systemu | ✘ | wniosek | ? webhook | nie → C7 |
| Ikona sieci na wyświetlaczu | ? | nie | ◐ pokazuje „chmura” | nie → C5 |
| Pamięć ustawień po zaniku zasilania | ◐ sterownik pamięta swoje | wniosek | ? dwa układy z pamięcią | nie → C8 |
| Restart samego modułu w trakcie ładowania | ? | nie | ? | nie → C9 |

**Wniosek.** W sieci lokalnej Shelly robi to samo co bez chmury. Jedyna różnica to godzina: trzeba lokalnego serwera czasu, a w przyszłości, jeśli Shelly to zmieni, wystarczy czas z telefonu. Tuya bez internetu to Home Assistant z kluczem lokalnym, w dodatku bez godziny dla sterownika.

### 3.3 Bez Wi-Fi: tylko telefon albo laptop obok ładowarki

| Funkcja | Q11 na Tuya | Sprawdzone? | Q11 na Shelly | Sprawdzone? |
| --- | --- | --- | --- | --- |
| Aplikacja producenta przez Bluetooth | ? moduł Tuya ma Bluetooth, sterowanie nim niesprawdzone | nie | ? aplikacja wymaga konta w chmurze | nie → D3 |
| Strona WWW przez sieć modułu | ✘ | z dokumentacji | ◐ działa bez routera i bez aplikacji | tak, 24.09 na symulatorze; Q11 → D4, D8 |
| Polecenia z komputera przez Bluetooth | ✘ brak otwartego sposobu | wniosek | ? włączone w konfiguracji modułu | konfiguracja: tak, 25.09; działanie → D2 |
| Godzina dla sterownika | ✘ | wniosek | ✘ czas ustawiony ręcznie nie trafia do sterownika | tak, 25.09; czas z telefonu → D5 |
| Okno godzin ładowania | ? bez godziny | nie | ? bez godziny | nie → D6 |
| Harmonogram | ✘ bez sieci | wniosek | ◐ działa, dopóki moduł pamięta godzinę sprzed utraty sieci; po zaniku zasilania nie | nie → D8 |
| MQTT, OCPP, Home Assistant | ✘ brak sieci | wniosek | ✘ brak sieci | wniosek |
| Start ładowania po podłączeniu auta | ✔ | z użytkowania | ✔ | tak, 25.09 |
| Limit prądu z menu ładowarki | ✔ | z użytkowania | ? | nie → D7 |
| Tryb, okno godzin i limit energii z menu | ✔ ustawienie działa; okno wymaga godziny | z użytkowania | ? | nie → C6, D7 |
| Reset sieci z menu ładowarki | ✔ moduł wchodzi w parowanie | z dokumentacji Tuya | ? | nie → D9 |

**Wniosek.** Bez Wi-Fi Tuya ma tylko menu ładowarki. Shelly ma dodatkowo stronę WWW przez własną sieć modułu, bez aplikacji i bez konta; na symulatorze to działało. Przeszkodą jest godzina: bez Wi-Fi nie ma serwera czasu, a czasu ustawionego ręcznie moduł sterownikowi nie przekazuje. Dopóki Shelly tego nie zmieni, okno godzin i harmonogramy bez Wi-Fi nie mają godziny po zaniku zasilania.

## 4. Wspólne założenia

- Chmura Shelly wyłączona przez cały czas, jak dotąd.
- **Serwer czasu.** Na poziomie B moduł bierze godzinę z publicznego serwera w internecie, jak u klienta. Lokalny serwer czasu (kontener na 192.168.0.57) jest potrzebny na poziomie C i w testach D5–D6. Wtedy musi działać **przed** każdym włączeniem ładowarki, bo moduł pyta o czas zaraz po starcie.
- **Broker MQTT** (kontener na 192.168.0.57) to pośrednik: przez niego laptop, a u klienta jego system, odbiera stan modułu i wysyła polecenia. Potrzebny w teście C4.
- Monitor logu przez Wi-Fi uruchomiony przed każdym testem. Przy zaniku zasilania monitor sam się wznawia po powrocie modułu.
- Symulator auta podłączony: stany „podłączone” (9 V) i „ładuje” (6 V). Bez obciążenia prądowego, więc prąd i moc faz zostają poza programem.
- Wi-Fi laptopa i router zostają bez zmian. Brak internetu dla modułu uzyskujemy po stronie modułu (dokument 02).
- DevKit zasilany z płytki Q11: nigdy nie podłączamy jednocześnie USB.
- Po każdym teście wpis w tabeli wyników na końcu dokumentu: ✔ działa, ◐ działa z zastrzeżeniem, ✘ nie działa, z opisem tego, co zaobserwowano.

## 5. Kolejność i czas

Kolejność idzie od bezpiecznych do ryzykownych, niezależnie od dokumentu.

| Kolejność | Testy | Dokument | Ryzyko | Czas | Potrzebny użytkownik |
| --- | --- | --- | --- | --- | --- |
| 1 | B1–B3 aplikacja, strona WWW, Home Assistant | 01 | małe | 50 min | tak, telefon |
| 2 | D1–D4 Bluetooth, aplikacja przez Bluetooth, sieć modułu | 03 | małe | 1 h 35 min z narzędziem | tak, telefon |
| 3 | D5 czas z telefonu | 03 | małe | 15 min | tak, telefon |
| 4 | B4–B6 harmonogram, webhook, pamięć | 01 | małe | 1 h | nie |
| 5 | B7–B10, B12 API | 01 | małe | 1 h 30 min | nie |
| 6 | Przejście na poziom C, C1–C5 | 02 | małe | 1 h 25 min | tak, telefon i symulator |
| 7 | C8 zanik zasilania, pierwsza runda; C9 restart modułu | 02 | małe | 1 h 5 min | tak, wyłącznik |
| 8 | C6 okno godzin, C7 harmonogram i webhook | 02 | małe | 1 h 20 min | tak, menu |
| 9 | C8 druga runda | 02 | małe | 45 min | tak, wyłącznik |
| 10 | Powrót modułu na poziom B | 02 | małe | 10 min | nie |
| 11 | D6 okno bez godziny, D7 menu | 03 | małe | 50 min | tak, menu |
| 12 | B11 hasło do API | 01 | średnie | 20 min | nie |
| 13 | D8 moduł naprawdę bez Wi-Fi | 03 | średnie | 30 min | tak, telefon jako droga awaryjna |
| 14 | D9 reset sieci z menu | 03 | duże | 20 min plus ewentualne dodanie do sieci | tak |

Razem około 12 godzin, czyli trzy dni pracy. Testy opcjonalne C10–C12 poza tym czasem. Po wszystkim: wyniki do analizy GAP v4 i uzupełnienie dokumentacji dla fabryki o wyniki C8 i D9.

## 6. Czego program nie obejmuje

- Prąd i moc faz pod obciążeniem, pełna sesja z energią: wymaga obciążenia, osobny test.
- Zapis trybu, okna godzin i limitu energii z modułu: wymaga nowych pól w produkcie, osobny etap po C6.
- Aktualizacja sterownika przez moduł: wymaga pliku od fabryki.
- Ekran ładowarki w aplikacji Shelly: sprawa portalu, nie łączności.

## 7. Stare numery testów

Plan v1–v3 numerował testy T0–T7. Odpowiedniki:

| Stary numer | Nowy | Stary numer | Nowy |
| --- | --- | --- | --- |
| T0a | C11 | T4a, T4e | B4 |
| T0b | C12 | T4b, T4c | B5 |
| T1a | D1 | T4d | B6 |
| T1b | D2 | T5a–T5i | C8 |
| T1c | D3 | T5j | C9 |
| T1d, T1e | D8 | T6 | D9 |
| T1f | D4 | T7a | B7 |
| T1g | C1 | T7b | B8 |
| T2a, T2c | C2 | T7c | B9 |
| T2b | D7 | T7d | B10 |
| T2d | C3 | T7e | B11 |
| T2e | C5 | T7f | B12 |
| T2f | C4 | T7g | B3 |
| T3a, T3c | C6 | nowe | B1, B2, C7, C10, D5 |
| T3b | D6 | | |
| T3d | D7 | | |
