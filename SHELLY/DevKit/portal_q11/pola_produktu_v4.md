# Produkt „Q11 DevKit test”: pola i punkty danych, wersja 4
_Co wpisać w portalu Shelly X, żeby produkt pokazywał wszystkie punkty danych Q11, i jak to wdrożyć · AMPERE POINT · 29 września 2026 · oprac. Dawid Cekała_
FOOTER: AMPERE POINT — pola produktu v4 · Q11 z modułem Shelly · 2026-09-29

## W skrócie {-}

- **Dziś produkt ma 6 pól. Dochodzi 9 nowych,** razem 15. Nowe pola odpowiadają punktom danych, które sterownik wysyła, a produkt ich nie pokazywał: sygnał z auta, tryb pracy, limit energii, okno godzin (dwa pola), temperatura, energia ostatniej sesji, błędy i wersja sterownika.
- **Nazwy ról muszą być dokładnie takie jak w tabeli.** Skrypt v4 (`script.svc.ts` w tym folderze) szuka pól po roli. Pola, którego nie ma w produkcie, skrypt nie obsługuje, ale działa dalej. Można więc wdrożyć część pól, jeśli portal albo pamięć nie pozwolą na wszystkie.
- **Nazwy w interfejsie są po angielsku,** tak jak obecne pola.
- **Skrypt v4 poprawia też trzy rzeczy z testów 29.09:**
  - czas sesji liczy z tyknięć zegara skryptu, a nie z godziny modułu;
  - moc całkowitą bierze ze sterownika;
  - po każdym zapisie sprawdza, czy sterownik przyjął wartość.
- **Wgranie konfiguracji kasuje Wi-Fi modułu.** Po wgraniu dodajesz DevKit do sieci, a ja przechodzę listę kontrolną z rozdziału 5.

## 1. Pola produktu: ekran Virtual Components

Sześć pól oznaczonych PREDEFINED zostaje bez zmian. Nowe dodajesz przyciskiem **„+ Add custom VC”**. Dla każdego pola:
1. wpisz klucz,
2. wybierz DATA TYPE,
3. ustaw ACCESS,
4. kliknij **Configure** i wypełnij okno.

**Config (write)** nigdzie nie zaznaczaj, tak jak w polach PREDEFINED. **Log to cloud** zostaw bez zmian, bo chmura i tak jest wyłączona. **Persisted** jest domyślnie zaznaczone i przy nowych polach trzeba je **odznaczyć**. Sterownik sam pamięta swoje ustawienia i zgłasza je po starcie, a pamięć w module grozi narzuceniem starej wartości (test C8).

| Klucz | DATA TYPE | ACCESS: zaznaczone | Configure: Display name | Configure: reszta | DEFAULT VALUE | Punkt |
| --- | --- | --- | --- | --- | --- | --- |
| `cp_state` | enum | Config (read), Read | Vehicle signal | Options z rozdziału 2 | pierwsza opcja | 13 |
| `work_mode` | enum | Config (read), Read, Write | Charging mode | Options z rozdziału 2 | pierwsza opcja | 14 |
| `energy_limit` | number | Config (read), Read, Write | Energy limit | zakres 0–200, jednostka kWh | 0 | 17 |
| `window_start` | number | Config (read), Read, Write | Charging window from | zakres 0–23, jednostka h | 0 | 19 |
| `window_end` | number | Config (read), Read, Write | Charging window to | zakres 0–23, jednostka h | 0 | 19 |
| `temperature` | number | Config (read), Read | Temperature | zakres −40–200, jednostka °C | 0 | 24 |
| `last_session_energy` | number | Config (read), Read | Last session energy | zakres 0–9999999, jednostka kWh | 0 | 25 |
| `faults` | text; jeśli nie ma go na liście, number | Config (read), Read | Faults | — | puste albo 0 | 10 |
| `controller_version` | text; jeśli nie ma go na liście, pomiń pole | Config (read), Read | Controller version | — | puste | 23 |

Zakres i jednostka liczb: w oknie Configure, tak jak przy `current_limit` („6–16 A”). **Klucze muszą być dokładnie takie jak w tabeli,** bo skrypt v4 szuka pól po kluczu. Pola, którego nie ma, skrypt nie obsługuje, ale działa dalej.

Energia sesji ma w opisie portalu Wh, a czas sesji sekundy. Skrypt podaje kWh i minuty, tak jak zakresy w polach PREDEFINED („0–9999999999 kWh”, „0–50000 min”). Tego nie zmieniamy.

## 2. Opcje pól enum

W oknie Configure pole „Options (one per line)”. Wkleić dokładnie w tej kolejności, bo sterownik wysyła numer pozycji, a nie nazwę.

**`cp_state`**, sygnał z auta:

```
controlpi_12v
controlpi_12v_pwm
controlpi_9v
controlpi_9v_pwm
controlpi_6v
controlpi_6v_pwm
controlpi_error
```

| Nr | Opcja | Znaczenie |
| --- | --- | --- |
| 0 | `controlpi_12v` | 12 V, brak auta |
| 1 | `controlpi_12v_pwm` | 12 V z sygnałem prądu |
| 2 | `controlpi_9v` | 9 V, auto podłączone |
| 3 | `controlpi_9v_pwm` | 9 V z sygnałem prądu, gotowe |
| 4 | `controlpi_6v` | 6 V, auto chce ładować |
| 5 | `controlpi_6v_pwm` | 6 V z sygnałem prądu, ładowanie |
| 6 | `controlpi_error` | błąd sygnału |

**`work_mode`**, tryb pracy:

```
charge_now
charge_energy
charge_schedule
```

| Nr | Opcja | Znaczenie |
| --- | --- | --- |
| 0 | `charge_now` | natychmiast |
| 1 | `charge_energy` | do limitu energii |
| 2 | `charge_schedule` | w oknie godzin |

**Opcje nie mają osobnych napisów.** Na stronie WWW modułu i w API widać surowe nazwy, np. `controlpi_6v`. Czytelne napisy po polsku da dopiero nasz własny ekran.

**`faults`**, błędy. Przy polu text skrypt wpisuje `none` albo listę kodów z definicji Tuya i wartość szesnastkową, np. `ov_Temp_fault, earth_fault (0x10040)`. Przy polu number wpisuje samą wartość, np. 65600. Znaczenie kodów jest w zestawieniu punktów danych, rozdział 4.

## 3. Punkty danych w źródle Tuya MCU

Zakładka Data → Datapoints. Pierwsze siedem wierszy już jest. Nowe punkty zostawiamy **niepowiązane z polami**, bo obsługuje je nasz skrypt. Powiązanie w portalu wygenerowałoby dla nich kod, który i tak zastępujemy.

| DP | Nazwa | Typ | Tryb | Powiązanie z polem |
| --- | --- | --- | --- | --- |
| 18 | state | Boolean | readwrite | state |
| 4 | current_limit | Integer | readwrite | current_limit |
| 3 | mode | Enum | readonly | mode |
| 1 | total_energy | Integer | readonly | brak |
| 6 | phase_a | Raw | readonly | brak |
| 7 | phase_b | Raw | readonly | brak |
| 8 | phase_c | Raw | readonly | brak |
| **9** | power_total | Integer | readonly | brak |
| **10** | faults | Bitmap | readonly | brak |
| **13** | cp_state | Enum | readonly | brak |
| **14** | work_mode | Enum | readwrite | brak |
| **17** | energy_limit | Integer | readwrite | brak |
| **19** | charge_window | Raw | readwrite | brak |
| **23** | controller_version | String | readonly | brak |
| **24** | temperature | Integer | readonly | brak |
| **25** | last_session_energy | Integer | readonly | brak |

**Jeśli portal nie ma typu Bitmap albo String,** pomiń ten punkt. Moduł sam dodaje punkt, gdy sterownik go przyśle; tak było z temperaturą, której nie było w tabeli (w logu: „add int 24 = 19”). Skrypt v4 podpina takie punkty z opóźnieniem, próbując co 5 s.

## 4. Skrypt v4

Zakładka Develop → Open editor → `script.svc.ts`: zastąpić całą zawartość plikiem `script.svc.ts` z tego folderu i zbudować. Portal oznaczy skrypt jako przepisany („REWRITTEN — NOT MERGING”). **Nie klikać „REVERT & REGENERATE”.** Wersja v3 zostaje w tym folderze jako `script_v3.svc.ts`.

| Zmiana w v4 | Dlaczego |
| --- | --- |
| Dziewięć nowych pól z tłumaczeniem numerów pozycji na nazwy | generator portalu przepisuje numer bez tłumaczenia (znane z v2) |
| Okno godzin: dwa pola, jeden punkt; zmiana któregokolwiek wysyła oba | punkt 19 ma dwa bajty: godzinę startu i godzinę końca |
| Czas sesji z tyknięć zegara skryptu co 10 s | v3 liczył z godziny modułu; 29.09 czas skoczył o 45 min przy korekcie zegara i na 1066 min po restarcie |
| Moc całkowita z punktu 9 | sterownik podaje ją sam; suma faz zostaje na wypadek jej braku |
| Po zapisie kontrola po 3 s | gdy sterownik odrzuci wartość, odsyła starą, a moduł nie zgłasza zmiany; pole zostałoby z wartością, której sterownik nie ma |
| Punkty podpinane z opóźnieniem | moduł dodaje punkt dopiero po pierwszym meldunku sterownika |
| Brakujące pole jest pomijane | wdrożenie częściowe nie psuje reszty |
| Komunikaty w logu z przedrostkiem `Q11:` | odrzucony zapis albo wartość poza zakresem widać w monitorze |

**Sprawdzenie przed wgraniem.** Skrypt uruchomiony na laptopie na atrapie modułu: podstawiona warstwa Tuya, pola i zegar (`narzedzia\test_skryptu\atrapa.mjs`, polecenie `node atrapa.mjs ../../portal_q11/script.svc.ts`). 31 sprawdzeń, wszystkie ✔:
- meldunki sterownika trafiają do pól, także punktów podpiętych z opóźnieniem;
- zapis limitu, trybu i okna trafia do sterownika jeden raz;
- odrzucony zapis wraca do wartości sterownika, bez ponownego zapisu;
- limit energii przy niezgłoszonym punkcie daje komunikat w logu;
- czas sesji nie reaguje na skok zegara o 45 min;
- moc bierze z punktu 9, energię sesji liczy z licznika;
- brak pola nie zatrzymuje skryptu.

Test złapał błąd w pierwszej wersji v4. Gdy sterownik zgłaszał nowe okno godzin, skrypt ustawiał pola po kolei. Zmiana pierwszego pola odsyłała sterownikowi okno z nowym startem i starym końcem, np. zamiast 22–6 szło 22–0. Poprawione blokadą na czas wpisywania okna do pól.

## 5. Wdrożenie i lista kontrolna

| Krok | Kto | Co |
| --- | --- | --- |
| 1 | Dawid | Portal, ekran Virtual Components: 9 pól przyciskiem „+ Add custom VC” (rozdziały 1 i 2); potem „Set up datapoints”: punkty z rozdziału 3 |
| 2 | Dawid | Develop: wkleić skrypt v4, zbudować |
| 3 | Dawid | Wgranie przez Bluetooth; po wgraniu dodać DevKit do Wi-Fi |
| 4 | Claude | Moduł ma 15 pól; brakujące = limit pamięci albo portal, zapisać które |
| 5 | Claude | Usługa działa: skrót kodu w stanie usługi zgadza się z v4 |
| 6 | Claude | Ustawienia po wgraniu: chmura wyłączona, serwer czasu `time.cloudflare.com`, MQTT `192.168.0.57:1883` z przedrostkiem `ampere/q11dev`, log przez WebSocket włączony, poziom 3; co wgranie zmieniło, przywrócić |
| 7 | Claude | Pola wypełnione ze sterownika: sygnał z auta, tryb, okno, temperatura, błędy „none” |
| 8 | Claude | Zapis z modułu: tryb pracy, okno godzin, limit energii; sterownik potwierdza albo w logu jest `Q11:` z powodem |
| 9 | razem | Powrót do testów: B3 (Home Assistant widzi nowe encje), B2 (strona WWW z nowymi polami) |

## 6. Ryzyka

| Ryzyko | Co się stanie | Co wtedy |
| --- | --- | --- |
| Opcje pól enum bez napisów | na stronie WWW i w API surowe nazwy, np. `controlpi_6v` | czytelne napisy w naszym ekranie |
| Pola dodane przez „Add custom VC” nie pojawią się na ekranie ładowarki w aplikacji | widać je na stronie WWW, w API i w Home Assistant | bez aplikacji z chmurą to i tak nieważne (test B1); sprawdzić po wgraniu |
| Brak pamięci na 15 pól | część pól nie powstanie | połączyć: okno godzin jako jeden tekst „22–6”, wersję wpisać do błędów |
| Limit energii i wersja nigdy nie przyszły od sterownika | moduł odrzuci zapis limitu energii, dopóki sterownik go nie zgłosi | w logu `Q11: … nie zglosil DP 17`; sprawdzić w teście C6 po zmianie trybu z menu |
| Zapis okna jako tekst szesnastkowy to założenie (odczyt przychodzi w tej postaci) | sterownik może nie przyjąć | skrypt po 3 s pokaże w polach wartość sterownika i zapisze powód w logu |
| Kolejność bitów błędów to założenie | kody mogą być przesunięte | potwierdzi dopiero prawdziwy błąd; wartość szesnastkowa jest w polu obok kodów |
| Licznik całkowity przychodzi co 90 s i tylko w stanie „ładuje” | początek albo koniec sesji może być policzony z opóźnieniem do 90 s; przy 11 kW to do 0,275 kWh (11 kW × 90 s) | sprawdzić pod obciążeniem, porównać z energią ostatniej sesji ze sterownika (punkt 25) |
