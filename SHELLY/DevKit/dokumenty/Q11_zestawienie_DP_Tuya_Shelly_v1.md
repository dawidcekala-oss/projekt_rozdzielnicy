# Zestawienie punktów danych: Q11 na Tuya a Q11 na Shelly
_Wszystkie punkty danych Q11 z definicji Tuya, to, co sterownik naprawdę wysyła, i gdzie każdy punkt trafia po stronie Shelly · AMPERE POINT · 28 września 2026 · oprac. Dawid Cekała_
FOOTER: AMPERE POINT — zestawienie punktów danych · Q11 z modułem Shelly · v1 · 2026-09-28

## W skrócie {-}

- **Tuya rozmawia punktami danych.** Sterownik Q11 i moduł wymieniają numerowane punkty: numer, typ, wartość. Definicja produktu Q11 w chmurze Tuya ma ich 17.
- **Shelly nie ma punktów danych, ma pola.** Pole to element modułu z nazwą i numerem, np. `number:200` „limit prądu”. Warstwa Tuya wbudowana w moduł Shelly (TMCU) rozmawia ze sterownikiem punktami danych, a nasz skrypt usługi przepisuje je na pola i z powrotem.
- **Stan dziś:** sterownik wysyła 14 z 17 punktów. Nasz produkt obsługuje 6 z nich: włącznik, limit prądu, stan i trzy fazy. 8 kolejnych trzeba dodać jako pola.
- **Licznik całkowity przychodzi tylko podczas ładowania.** Sterownik wysyła go co 90 s w stanie „ładuje”. 24–25.09 ładowarka nie ładowała, dlatego wcześniej uznaliśmy, że go nie wysyła (*korekta 29.09*). Na naszym egzemplarzu licznik stoi na 0, bo przy symulatorze bez obciążenia energia nie płynie.

**Źródła:**
- definicja produktu z chmury Tuya (produkt „Ampere Point EV Charger”, ta sama co Q11 PRO),
- zrzut stanu z chmury,
- kodowanie z naszej integracji Home Assistant,
- logi modułu z 24–25.09 (około 10 godzin rozmowy ze sterownikiem),
- skrypt usługi v3,
- dokumentacja Shelly dla TopAC.

**Oznaczenia:** ✔ działa albo widziane w logu · ◐ częściowo · ✘ nie ma albo nie widziane · ? nie wiadomo.

## 1. Punkty danych Q11 w definicji Tuya

| Nr | Kod Tuya | Co to jest | Typ | Zakres i jednostka | Zapis z zewnątrz | Na łączu |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `forward_energy_total` | licznik całkowity energii | liczba | 0–99 999 999, setne kWh | ✘ tylko odczyt | 4 B |
| 3 | `work_state` | stan ładowarki | wyliczenie | 8 stanów, tabela w rozdz. 4 | ✘ | 1 B, numer pozycji |
| 4 | `charge_cur_set` | limit prądu | liczba | 6–32 A w definicji; Q11 ma 16 A | ✔ | 4 B |
| 6 | `phase_a` | faza L1: napięcie, prąd, moc | surowe | napięcie ×0,1 V (2 B), prąd ×0,001 A (3 B), moc w W (2 B) | ✘ | 7 B |
| 7 | `phase_b` | faza L2 | surowe | jak L1 | ✘ | 7 B |
| 8 | `phase_c` | faza L3 | surowe | jak L1 | ✘ | 7 B |
| 9 | `power_total` | moc całkowita | liczba | tysięczne kW, czyli W | ✘ | 4 B |
| 10 | `fault` | błędy | mapa bitowa | 17 błędów, tabela w rozdz. 4 | ✘ | w logu 2 B |
| 13 | `connection_state` | sygnał z auta (Control Pilot) | wyliczenie | 7 wartości, tabela w rozdz. 4 | ✘ | 1 B, numer pozycji |
| 14 | `work_mode` | tryb pracy | wyliczenie | natychmiast, do limitu energii, w oknie godzin | ✔ | 1 B, numer pozycji |
| 17 | `energy_charge` | limit energii sesji | liczba | 1–200 kWh | ✔ | 4 B |
| 18 | `switch` | ładowanie włączone | logiczne | tak, nie | ✔ | 1 B |
| 19 | `local_timer` | okno godzin ładowania | surowe | 2 B: godzina startu, godzina końca, 0–23, bez minut | ✔ | 2 B |
| 23 | `system_version` | wersja programu sterownika | tekst | do 255 znaków; w chmurze „V1” | ✘ | tekst |
| 24 | `temp_current` | temperatura | liczba | −40–200 °C | ✘ | 4 B |
| 25 | `charge_energy_once` | energia ostatniej sesji | liczba | setne kWh | ✘ | 4 B |
| 33 | `mode_set` | nieznane | surowe | znaczenie nieznane; w chmurze puste | ✔ | ? |

**Jak to czytać:**
- „Zapis z zewnątrz” mówi, czy Tuya pozwala zmienić punkt z aplikacji. Pozostałe punkty sterownik tylko zgłasza.
- Wyliczenia idą po łączu jako numer pozycji. Nazwy i ich kolejność są tylko w definicji w chmurze, dlatego nasz skrypt ma własną tablicę nazw.
- Okno godzin jest zapisane w dwóch bajtach, bez minut. Tak koduje je nasza integracja Home Assistant; w zrzucie z chmury ma wartość `AAA=`, czyli 00 i 00.

**Inny produkt, dla porządku.** Eksport Q21 z repozytorium (inna definicja w Tuya) ma tylko 11 punktów, a punkt 8 znaczy tam „zdarzenia ładowarki”. Ma też punkty 41–49, których Q11 nie ma. Tłumacz po stronie Shelly trzeba więc pisać osobno dla każdej definicji produktu. Q11 na biurku mówi zestawem z tabeli powyżej.

## 2. Q11 a Shelly, punkt po punkcie

„Q11 wysyła” to wynik z logów modułu z 24–25.09. „Nasz produkt” to produkt „Q11 DevKit test” na DevKicie. „TopAC” to ładowarka na Shelly X, wzorzec pól po stronie Shelly.

| Nr | Co | Q11 wysyła | Nasz produkt Shelly | TopAC | Stan |
| --- | --- | --- | --- | --- | --- |
| 1 | licznik całkowity | ✔ co 90 s, tylko w stanie „ładuje”; wartość 0 (*korekta 29.09*; 24–25.09 ładowarka nie ładowała) | `phase_info.total_act_energy` i podstawa energii sesji | `total_act_energy` | ◐ dochodzi; wartość i przyrost do sprawdzenia pod obciążeniem |
| 3 | stan ładowarki | ✔ | `enum:200` „mode”, skrypt tłumaczy numer na nazwę | `work_state` | ✔ |
| 4 | limit prądu | ✔ | `number:200` „current_limit”, 6–16 A, zapamiętywane | `current_limit` 6–16 A | ✔ w obie strony |
| 6–8 | fazy L1–L3 | ✔ | `object:200` „phase_info”: `phase_a/b/c` | `phase_info` | ◐ napięcia sprawdzone; prąd i moc pod obciążeniem nie |
| 9 | moc całkowita | ✔ wartość 0 | nieużywany; skrypt sumuje moc faz w `total_power` | `total_power` | ◐ |
| 10 | błędy | ✔ wartość 0 | brak | brak w API | do dodania |
| 13 | sygnał z auta | ✔ 12 V, 9 V, 6 V | brak | brak | do dodania |
| 14 | tryb pracy | ✔ „natychmiast” | brak | brak jawnego pola | do dodania, z zapisem |
| 17 | limit energii sesji | ✘ nie widziany | brak | `global_charge_limit` 0–1000 kWh | do dodania; sprawdzić w teście T3 |
| 18 | ładowanie włączone | ✔ | `boolean:200` „state”, zapamiętywane | `start_charging` | ✔ w obie strony |
| 19 | okno godzin | ✔ `0000` | brak | brak; zamiast tego harmonogram modułu | do dodania, z zapisem |
| 23 | wersja sterownika | ✘ nie widziana | brak | ? | do dodania; ustalić, kiedy sterownik ją wysyła |
| 24 | temperatura | ✔ 18–19 °C | brak | brak | do dodania |
| 25 | energia ostatniej sesji | ✔ raz, wartość 0 (24.09, 11:23) | brak | `energy_charge` | do dodania; możliwe źródło energii sesji |
| 33 | nieznane | ✘ | brak | — | do ustalenia z fabryką |

## 3. Pola Shelly bez własnego punktu danych

| Pole | Nasz produkt | TopAC | Skąd wartość |
| --- | --- | --- | --- |
| Czas sesji | `number:201` „session_duration”, minuty | `time_charge` | liczy skrypt z czasu w stanie „ładuje”; ginie przy restarcie modułu |
| Energia sesji | `number:202` „session_energy”, kWh | `energy_charge` | przyrost licznika całkowitego; dziś 0, bo bez obciążenia licznik nie rośnie |
| Prąd całkowity | `phase_info.total_current` | `total_current` | suma prądów faz w skrypcie |
| Limit czasu sesji | brak | `global_time_limit` 0–1440 min | Q11 ma go w menu, bez punktu danych |
| Autoryzacja startu | brak | ustawienie „auto charge” | ustawienie usługi Shelly, nie punkt danych |

## 4. Wartości wyliczeń i mapa błędów

**Stan ładowarki, sygnał z auta, tryb pracy.** Numer pozycji to wartość na łączu.

| Nr pozycji | Stan ładowarki (3) | Sygnał z auta (13) | Tryb pracy (14) |
| --- | --- | --- | --- |
| 0 | `charger_free` wolna | `controlpi_12v`: 12 V, brak auta | `charge_now` natychmiast |
| 1 | `charger_insert` auto podłączone | `controlpi_12v_pwm`: 12 V z sygnałem prądu | `charge_energy` do limitu energii |
| 2 | `charger_free_fault` wolna, błąd | `controlpi_9v`: 9 V, auto podłączone, nie chce ładować | `charge_schedule` w oknie godzin |
| 3 | `charger_wait` czeka | `controlpi_9v_pwm`: 9 V z sygnałem prądu | — |
| 4 | `charger_charging` ładuje | `controlpi_6v`: 6 V, auto chce ładować | — |
| 5 | `charger_pause` pauza | `controlpi_6v_pwm`: 6 V z sygnałem prądu, ładowanie | — |
| 6 | `charger_end` zakończone | `controlpi_error`: błąd sygnału | — |
| 7 | `charger_fault` błąd | — | — |

Sygnał z auta to napięcie na przewodzie Control Pilot: 12 V bez auta, 9 V po podłączeniu, 6 V gdy auto chce ładować. „Z sygnałem prądu” znaczy, że ładowarka nadaje auto dozwolony prąd przebiegiem prostokątnym.

**Mapa błędów (10).** Nazwy po polsku to tłumaczenie kodów z definicji Tuya.

| Bit | Kod | Znaczenie |
| --- | --- | --- |
| 0 | `ov_cr` | nadprąd |
| 1 | `ov2_cr_fault` | nadprąd, drugi próg |
| 2 | `ov_vol` | przepięcie |
| 3 | `undervoltage_alarm` | podnapięcie |
| 4 | `contactor_adhesion` | sklejony stycznik |
| 5 | `contactor_fault` | awaria stycznika |
| 6 | `earth_fault` | błąd uziemienia |
| 7 | `meter_hardware_alarm` | awaria układu pomiaru energii |
| 8 | `scram_fault` | wyłącznik awaryjny |
| 9 | `cp_fault` | błąd sygnału z auta |
| 10 | `meter_commu_fault` | brak łączności z układem pomiaru |
| 11 | `card_reader_fault` | awaria czytnika kart |
| 12 | `cir_short_fault` | zwarcie |
| 13 | `adhesion_fault` | sklejenie styków |
| 14 | `self_test_alarm` | błąd autotestu |
| 15 | `leakagecurr_alarm` | prąd upływu |
| 16 | `ov_Temp_fault` | przegrzanie |

**Uwaga do mapy błędów.**
- **Kolejność bitów to założenie:** bit 0 = pierwszy kod w definicji, według zwyczaju Tuya. Potwierdzi ją dopiero prawdziwy błąd w logu.
- **17. kod nie mieści się w tym, co sterownik wysyła.** W logu mapa ma 2 bajty, czyli 16 bitów, więc bit 16 („przegrzanie”) nie ma gdzie trafić. Albo sterownik wysyła dłuższą mapę tylko przy tym błędzie, albo przegrzanie idzie inaczej. To pytanie do fabryki.

## 5. Polecenia protokołu Tuya poza punktami danych

Oprócz punktów danych sterownik i moduł wymieniają polecenia usługowe. Liczby z logów z 24–25.09.

| Kod | Kierunek | Co to jest | Jak często | Q11 na Shelly |
| --- | --- | --- | --- | --- |
| 0x00 | moduł → sterownik | znak życia | co 15 s | ✔ |
| 0x01 | moduł → sterownik | zapytanie o informacje o produkcie | przy starcie | ◐ nie złapane, leci przed połączeniem logu |
| 0x03 | moduł → sterownik | stan sieci: 2 brak routera, 3 router, 4 chmura | co 30 s | ◐ moduł zawsze wysyła 4, także przy wyłączonej chmurze |
| 0x04 | sterownik → moduł | reset Wi-Fi, z menu ładowarki | na żądanie | ? test T6 |
| 0x06 | moduł → sterownik | ustaw punkt danych | na polecenie | ✔ 75 razy w logach |
| 0x07 | sterownik → moduł | meldunek punktu danych | przy zmianie i na zapytanie | ✔ |
| 0x08 | moduł → sterownik | zapytanie o wszystkie punkty | po starcie | ✔ |
| 0x0A, 0x0B | moduł → sterownik | aktualizacja programu sterownika | na żądanie | ? oprogramowanie modułu ma tę funkcję; niesprawdzone, wymaga pliku od fabryki |
| 0x1C | sterownik → moduł | prośba o czas lokalny | co 30 s | ✔ po synchronizacji z serwerem czasu; wcześniej zerowa data |
| 0x24 | sterownik → moduł | prośba o siłę sygnału Wi-Fi | co około 18 s | ✔ |
| 0x34 | moduł → sterownik | usługi rozszerzone; w logu niesie datę i godzinę | 41 razy w logach | ◐ dokładne znaczenie do ustalenia |

## 6. Co z tego wynika

**Sterownik wysyła 14 z 17 punktów.** Nie widzieliśmy dotąd limitu energii (17), wersji (23) ani punktu nieznanego (33). Mogą się pojawić dopiero po zmianie w menu, przy starcie albo w innym stanie ładowarki, tak jak licznik całkowity, który przychodzi tylko w stanie „ładuje”. Sprawdzą to testy C6, C8 i D7.

**Licznik całkowity dochodzi, ale tylko w stanie „ładuje”** (*korekta 29.09*; wcześniej uznany za brak). Energię sesji liczymy z jego przyrostu, jak w integracji Home Assistant. Czy rośnie poprawnie, pokaże dopiero test pod obciążeniem. Źródła zastępcze na wypadek, gdyby nie rósł:
- **energia ostatniej sesji (25):** wartość ze sterownika, dokładna, ale dostępna dopiero po sesji;
- **suma mocy z punktu 9 w skrypcie:** na żywo, ale przybliżona. Przy 6,9 kW każdy 30-sekundowy krok dodaje 0,0575 kWh, a zmiana mocy między odczytami wprowadza błąd.

Rekomendacja: zostać przy przyroście licznika i sprawdzić go pod obciążeniem; punkt 25 dodać jako kontrolę po każdej sesji.

**Do dodania jest 8 pól:** błędy, sygnał z auta, tryb pracy, limit energii, okno godzin, wersja, temperatura, energia ostatniej sesji. Moc całkowitą wystarczy dopisać do istniejącego pola faz. Razem z obecnymi 6 polami daje to 14. Pamięć na pola w module ma 5376 B i przy 17 polach użytkownika była prawie pełna, więc po dodaniu trzeba zmierzyć, ile zostało.

**Pytania do fabryki:** 17. bit mapy błędów, znaczenie punktu 33, kiedy sterownik wysyła wersję i limit energii.
