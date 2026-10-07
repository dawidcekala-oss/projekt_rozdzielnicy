# Wirtualna ładowarka Q11 na Shelly DevKit M1
_Instrukcja obsługi symulatora i powrotu do stanu z dostawy_
_AMPERE POINT · 24 września 2026 · oprac. Dawid Cękała_
FOOTER: AMPERE POINT — wirtualna ładowarka Q11 na DevKit M1 · 2026-09-24

## Co jest teraz na DevKicie

- **Oprogramowanie Shelly bez zmian.** Wersja 2.0.0-xc3-lightexpoGZ2026, ta sama co przy dostawie. Nic nie było wgrywane do pamięci programu.
- **Dodane przez polecenia Shelly:** 16 pól wirtualnych w grupie „Ładowarka Q11 (symulacja)”, skrypt `symulator_q11`, który startuje sam po każdym włączeniu, nazwa urządzenia „Q11 symulator (DevKit)” i strefa czasowa Europe/Warsaw.
- **Kopia stanu z dostawy** leży w folderze `kopia_zapasowa_2026-09-24`. To cała pamięć flash, sprawdzona z płytką bajt w bajt, plus konfiguracja w formie czytelnej.

## Jak otworzyć stronę

- **W sieci biurowej:** DevKit jest połączony z siecią „AmperePoint” i ma adres `http://192.168.0.238`. Strona otwiera się z laptopa i z telefonu w tej sieci. Grupa „Ładowarka Q11 (symulacja)” jest na pulpicie strony. Adres nadaje router, więc warto go zarezerwować w UniFi, żeby się nie zmienił.
- **Bez sieci biurowej:** połącz telefon z otwartą siecią `ShellyXC3-543204516334` i wejdź na `http://192.168.33.1`. Laptopa do tej sieci nie przełączaj, bo straci internet.

> **Uwaga:** W aplikacji Shelly Smart Control pola nie pojawiają się w „Głównych elementach sterujących”. Aplikacja pokazuje tam tylko grupy utworzone jako urządzenie wirtualne z szablonu kategorii produktu. Nasza grupa jest widoczna w zakładce komponentów wirtualnych, ikona sześcianu, podzakładka „Grupy”.

## Jak przetestować

Pole „Symulacja: samochód” udaje stan przewodu sygnałowego, tak jak symulator pojazdu na biurku. Pole „Symulacja: awaria uziemienia” udaje usterkę. Pozostałe pola to ładowarka.

| Co zmieniasz | Co powinno się stać | Wynik testu przez USB |
| --- | --- | --- |
| Samochód: B | stan „Auto podłączone”, sygnał 9 V, moc 0 | ✔ |
| Samochód: C, limit 16 A | stan „Ładuje”, sygnał 6 V, moc około 11 kW, energia sesji rośnie | ✔ 11,09 kW |
| Limit prądu 10 A | moc około 6,9 kW | ✔ 6,9 kW |
| Ładowanie wyłączone | stan „Pauza”, moc 0 | ✔ |
| Tryb „Według harmonogramu”, okno 22–6, w dzień | stan „Czeka na harmonogram” | ✔ |
| Awaria uziemienia | stan „Błąd”, w polu Błędy „earth_fault” | ✔ |
| Samochód: A | stan „Wolna”, energia sesji wraca do zera, licznik całkowity zostaje | ✔ |
| Tryb „Do zadanej energii”, 1 kWh, samochód C | po około 5,5 min przy 11 kW stan „Zakończone” | nie testowane |

Symulator liczy w czasie rzeczywistym, co 2 s. Przy 11 kW energia sesji rośnie o 0,006 kWh na krok, czyli o 11 kWh na godzinę.

## Pola i punkty danych Q11

Każde pole ładowarki odpowiada punktowi danych z profilu lokalnego „Ampere Point Q Series (local)”. W prawdziwej ładowarce te same pola będzie wypełniał tłumacz ramek z łącza szeregowego zamiast symulacji.

| Pole na stronie | Punkt danych Q11 | Rodzaj pola |
| --- | --- | --- |
| Stan ładowarki | 3, work_state | tekst, tylko odczyt |
| Sygnał Control Pilot | 13, connection_state | tekst, tylko odczyt |
| Limit prądu | 4, charge_cur_set | suwak 6–16 A |
| Ładowanie włączone | 18, switch | przełącznik |
| Tryb ładowania | 14, work_mode | lista wyboru |
| Energia docelowa | 17, energy_charge | liczba 1–200 kWh |
| Początek i koniec harmonogramu | 19, local_timer, dwa bajty | liczby 0–23 |
| Moc | 9, power_total | tylko odczyt |
| Licznik całkowity | 1, forward_energy_total | tylko odczyt |
| Temperatura | 24, temp_current | tylko odczyt |
| Fazy L1 / L2 / L3 | 6, 7 i 8, siedem bajtów na fazę | tekst |
| Błędy | 10, fault | tekst |
| Energia sesji | brak, liczona tak jak w integracji HA | tylko odczyt |

Stan ładowarki i sygnał są polami tekstowymi, a nie listami. Ta wersja strony rysuje listę w widoku etykiety jako pusty obrazek. Pamięć na pola wirtualne ma też tylko 5376 bajtów i 17 elementów symulatora zajmuje ją prawie całą. Kody Tuya, na przykład „charger_charging”, skrypt wysyła w zdarzeniu `q11_state`.

## Zegar

DevKit nie ma zegara z baterią. Bez internetu zapomina godzinę przy każdym restarcie, a tryb harmonogramu czeka wtedy bez końca. Po restarcie uruchom w tym folderze `python ustaw_zegar.py COM5`. Gdy DevKit dostanie Wi-Fi z internetem, zegar ustawi się sam.

## Aplikacja Shelly

Żeby zobaczyć ładowarkę w aplikacji Shelly Smart Control, dodaj DevKit przez Bluetooth: przycisk „+”, potem „Add via Bluetooth”, urządzenie `ShellyXC3-543204516334` i dane Twojej sieci Wi-Fi. Tego kroku nie zrobiłem, bo wymaga wpisania hasła do sieci. Po dodaniu strona będzie dostępna pod adresem, który router nada DevKitowi, a zegar zsynchronizuje się z internetem. Nie wiem jeszcze, czy aplikacja pokaże pola wirtualne tej wersji oprogramowania. To pierwsza rzecz do sprawdzenia.

## Sterowanie z laptopa przez USB

Narzędzie `..\narzedzia\shelly_uart_rpc.py` wysyła polecenia Shelly przez port COM5, bez Wi-Fi. Przykłady:

- podłączenie wirtualnego samochodu: `python shelly_uart_rpc.py COM5 Enum.Set id=203 value=C`
- odczyt stanu ładowarki: `python shelly_uart_rpc.py COM5 Enum.GetStatus id=200`
- limit prądu 10 A: `python shelly_uart_rpc.py COM5 Number.Set id=200 value=10`
- ponowna instalacja symulatora po zmianach w kodzie: `python zainstaluj_symulator.py COM5`

## Usunięcie symulatora i powrót do stanu z dostawy

- **Samo usunięcie symulatora:** `python usun_symulator.py COM5`. Kasuje skrypt, pola, zapisany licznik, nazwę urządzenia i strefę czasową.
- **Pełny powrót bajt w bajt:** polecenia w pliku `kopia_zapasowa_2026-09-24\PRZYWRACANIE.txt`. Zapis trwa około 2 minut.

> **Uwaga:** Plik kopii zawiera dane fabryczne urządzenia, w tym jego klucz. Nie wrzucać go do repozytorium ani nigdzie nie wysyłać.

## Co to jest, a czego jeszcze nie ma

- **To wariant bez konta producenta.** Pola wirtualne i skrypt użytkownika działają na każdym urządzeniu Shelly tej generacji.
- **Docelowy low-code to usługa z portalu Shelly X.** Tworzą ją lista pól i skrypt, wgrywane tokenem z portalu. Oprogramowanie DevKitu ma do tego polecenie, ale token wymaga konta producenta.
- **Język Tuya jest już w oprogramowaniu.** W pamięci DevKitu są komunikaty warstwy TMCU, w tym aktualizacji oprogramowania mózgu ładowarki. To potwierdza, że moduł Shelly umie rozmawiać z mózgiem Q11 i aktualizować jego oprogramowanie.
- **Następny krok do prawdziwej ładowarki:** zamienić funkcję symulacji w skrypcie na tłumacza ramek Tuya z łącza szeregowego. Pola zostają te same.
