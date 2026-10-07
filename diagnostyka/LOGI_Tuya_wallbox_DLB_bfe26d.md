# LOGI TUYA — wallbox z modułem DLB (`bfe26d78713489f8a6ulsj`)

**Zgłoszenie:** zaraz po włączeniu zasilania wallboxa komunikat „ochrona przed przeciążeniem”; problem od zamontowania modułu DLB. Wallbox pracuje, ale na 12 A — na module ustawione 20 A, na wallboxie 16 A, według klienta brak innych odbiorników, a samochód nie ma ograniczenia.

**Urządzenie:** `bfe26d78713489f8a6ulsj` · PID `gbmxngploofmhbjc` · Europe/Warsaw · „Type B, AC 30mA + DC 6mA” · firmware `(V8.0.7)F1.3.6` · wariant produktu 3
**Dostęp:** Tuya Developer Platform → w prawym górnym rogu przełączyć przestrzeń na konto partnera **深圳市龙眼创新科技有限公司** → Log urządzenia → **Central Europe**. Z przestrzeni własnych kont (także z tego samego loginu, ale w „Moja przestrzeń”) odpowiedź to `没有操作权限!` (brak uprawnień).
**Pobrano:** 2026‑09‑26, okno 7 dni. **Czasy poniżej lokalne.**
**Stan sprawy (2026‑09‑28):** klient czeka na wymianę — ma niefunkcjonalne DLB (relacja Dawida). Producent robi przegląd firmware; rozwój DLB prowadzony w `AMPERE_POINT\DLB_R&D\`.

---

## 1. Fakty z logu

**Log zaczyna się dziś o 10:43:39 od aktywacji urządzenia.** W oknie 7 dni nie ma nic wcześniej, więc okresu, w którym klient obserwował problem, log nie obejmuje.

**Brak jakiegokolwiek zdarzenia błędu.** Stany pracy przyjmują wyłącznie wartości 101 (bezczynny), 200 (wtyk włożony) i 300 (ładowanie). W zestawie punktów danych tego produktu nie ma osobnego punktu błędu. Komunikatu o przeciążeniu log nie rejestruje — albo nie wystąpił w tym oknie, albo jest wyłącznie lokalny, na wyświetlaczu.

*Korekta (2026‑09‑26, 14:47): punkt błędu istnieje — 报警信息 `{"v":400}` razem ze stanem pracy 400. W oknie do 11:47 alarm po prostu nie wystąpił; od 11:50 jest ich 12. Zob. sekcja 8.*

**DLB w danych nie występuje.** Żaden punkt danych nie dotyczy modułu DLB ani przydziału prądu. To zgodne z tym, co wiemy z manuala DLB: prądu przydzielonego wallboxowi nie widać nigdzie.

**Nastawa prądu przy aktywacji wynosiła 12 A**, choć lista dostępnych nastaw to `[6, 8, 10, 13, 16]` — 12 A nie da się wybrać z aplikacji. O 10:44:56 aplikacja zmieniła nastawę na 16 A i od tej pory urządzenie raportuje 16 A.

**Liczne restarty:** zanik zasilania i ponowne włączenie o 10:44:45, 10:51:24, 10:53:30 i 11:09:12, dwa resety programowe, restart z aplikacji o 10:44:27, reset fabryczny o 10:46:31 i ponowna aktywacja o 10:48:53.

**Sesje ładowania przy nastawie 16 A:**

| Start | Koniec | Prąd L1 / L2 / L3 | Moc | Uwagi |
|---|---|---|---|---|
| 10:51:30 | 10:52:12 | **16,0 / 16,0 / 0,0 A** | 7,2 kW | ładowanie dwufazowe, pełne 16 A |
| 10:59:53 | 11:03:30 | 5,8 / 6,5 / 6,5 → 4,9 / 5,4 / 5,6 A | 4,3 → 3,6 kW | trójfazowe, niski prąd |
| 11:03:37 | 11:05:41 | **11,0 / 12,4 / 12,6 A** | 8,1 kW | trójfazowe; na końcu L3 spada do 0, sekunda później koniec sesji |
| 11:10:14 | trwa | **11,3 / 12,4 / 12,4 A** | 8,1 kW | trójfazowe |

Sesje 2–4 zaczynają się tym samym wzorem (L1 1,3 → 1,1 → ok. 4 A, potem zero), więc najpewniej to ten sam samochód. Sesja 1 przebiega inaczej i jest dwufazowa — możliwe, że to inny pojazd.

**Napięcie:** we wszystkich pomiarach jednakowe na trzech fazach (np. 243,0 / 243,0 / 243,0 V). Spoczynkowe spadło z 242–245 V do 227–228 V przy restarcie o 10:51 i od tej pory tak zostało. Pod obciążeniem 224 V.

**Wi-Fi:** −33 do −41 dBm, bardzo silny sygnał.

## 2. Interpretacja — podejrzenia, niepotwierdzone

**12 A jest w logu odtworzone.** Przy nastawie 16 A sesje trójfazowe stoją na 11–12,6 A, a ten sam wallbox w sesji dwufazowej dał pełne 16 A — więc sam wallbox 16 A dostarczyć potrafi.

Jeśli w tych sesjach DLB był podłączony, obraz pasuje do przydziału 13 A: na naszym stanowisku samochód przy pozwoleniu 13 A pobierał 12,2 A (ok. 94%). Przy ustawieniu 20 A na DLB sufit wynosi 18 A, a zapas nad 16 A tylko 2 A, więc każde ponad 2 A obciążenia domu albo błędu przekładnika na dowolnej fazie zrzuca przydział o krok 3 A, do 13 A.

Jeśli DLB w tych sesjach **nie** był podłączony, to wyjaśnienie odpada i ograniczenie trzeba przypisać samochodowi albo wallboxowi — dlatego to jest pierwsze pytanie.

**Jednakowe napięcie na trzech fazach** oznacza albo, że wallbox raportuje jedną wartość dla wszystkich faz, albo że trzy fazy pochodzą z jednego przewodu — tak jak na naszym gnieździe G8, gdzie jedna faza jest zmostkowana na trzy. Ładowarki Q przy prawdziwym zasilaniu trójfazowym pokazują różne wartości na fazach.

**Nastawa 12 A spoza listy dostępnych wartości** mogła zostać wpisana przez moduł DLB albo z menu wallboxa. Nie wiemy, czym.

## 3. Do ustalenia

1. Czy podczas tych sesji moduł DLB był podłączony i sparowany.
2. Gdzie jest wallbox — u klienta czy na naszym stanowisku (silny sygnał, reset fabryczny i seria restartów sugerują test).
3. Czy przy restartach o 10:44, 10:51, 10:53 i 11:09 pojawił się na wyświetlaczu komunikat o przeciążeniu.
4. Czy sesja dwufazowa o 10:51 to inny samochód.
5. Odczyty z wyświetlacza DLB: `SEt` oraz L1/L2/L3 bez auta i w trakcie ładowania.

## 4. Pełny log (bez odświeżeń panelu i pomiaru sygnału; pomiary tylko przy zmianie wartości)

| Czas | Zdarzenie | Wartość | Źródło |
|---|---|---|---|
| 10:43:39 | Aktywacja | — | urządzenie |
| 10:43:41 | Online | — | urządzenie |
| 10:43:41 | Nastawa prądu | 12 | urządzenie |
| 10:43:41 | Prąd maks. | 16 | urządzenie |
| 10:43:41 | Stan pracy | 101 | urządzenie |
| 10:43:41 | Dostępne nastawy | [6,8,10,13,16] | urządzenie |
| 10:43:41 | Język | it | urządzenie |
| 10:43:41 | Info urządzenia | {"r":"Type B, AC 30mA + DC 6mA","fv":"(V8.0.7)F1.3.6"} | urządzenie |
| 10:43:41 | Tryb ładowania | {"m":0,"dt":0,"ss":"00:00","se":"08:00"} | urządzenie |
| 10:43:41 | Wariant produktu | 3 | urządzenie |
| 10:43:51 | Restart | reset programowy | urządzenie |
| 10:44:08 | Pomiary | U 243.0/243.0/243.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 27.0 °C | urządzenie |
| 10:44:27 | Restart | on | aplikacja |
| 10:44:29 | Online | — | urządzenie |
| 10:44:34 | Nastawa prądu | 12 | urządzenie |
| 10:44:34 | Opcja uziemienia | 0 | urządzenie |
| 10:44:34 | NFC | off | urządzenie |
| 10:44:34 | Autotest | {"t":"2000-00-00 00:00:00", "r":[1,1]} | urządzenie |
| 10:44:35 | Stan (debug) | bezczynny | urządzenie |
| 10:44:45 | Restart | zanik zasilania / włączenie | urządzenie |
| 10:44:56 | Nastawa prądu | 16 | aplikacja |
| 10:44:57 | Nastawa prądu | 16 | urządzenie |
| 10:45:02 | Stan (debug) | wtyk włożony | urządzenie |
| 10:45:02 | Stan pracy | 200 | urządzenie |
| 10:45:16 | Pomiary | U 242.0/242.0/242.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 28.0 °C | urządzenie |
| 10:46:31 | Reset fabryczny | on | aplikacja |
| 10:46:32 | Reset urządzenia | — | urządzenie |
| 10:46:32 | Offline | GATEWAY_DELETE | urządzenie |
| 10:48:53 | Aktywacja | — | urządzenie |
| 10:48:54 | Online | — | urządzenie |
| 10:48:54 | Nastawa prądu | 16 | urządzenie |
| 10:48:55 | Język | en | urządzenie |
| 10:48:55 | Stan (debug) | bezczynny | urządzenie |
| 10:49:04 | Restart | reset programowy | urządzenie |
| 10:49:08 | Pomiary | U 243.0/243.0/243.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 28.0 °C | urządzenie |
| 10:49:23 | NFC | off | aplikacja |
| 10:50:24 | Język | it | urządzenie |
| 10:50:45 | Stan (debug) | wtyk włożony | urządzenie |
| 10:50:45 | Stan pracy | 200 | urządzenie |
| 10:50:49 | Pomiary | U 245.0/245.0/245.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 28.0 °C | urządzenie |
| 10:51:07 | Online | — | urządzenie |
| 10:51:12 | Nastawa prądu | 16 | urządzenie |
| 10:51:13 | Autotest | {"t":"2000-00-00 00:00:00", "r":[1,1]} | urządzenie |
| 10:51:13 | Stan (debug) | bezczynny | urządzenie |
| 10:51:15 | Pomiary | U 228.0/228.0/228.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 28.0 °C | urządzenie |
| 10:51:24 | Restart | zanik zasilania / włączenie | urządzenie |
| 10:51:28 | Stan (debug) | wtyk włożony | urządzenie |
| 10:51:30 | Stan (debug) | ładowanie | urządzenie |
| 10:51:30 | Autotest | {"t":"2026-09-26 10:51:14", "r":[1,1]} | urządzenie |
| 10:51:35 | Pomiary | U 226.0/226.0/226.0 V · I 9.4/7.4/0.0 A · P 3.8 kW · T 28.0 °C | urządzenie |
| 10:51:38 | Pomiary | U 224.0/224.0/224.0 V · I 16.0/16.0/0.0 A · P 7.2 kW · T 28.0 °C | urządzenie |
| 10:51:41 | Pomiary | U 224.0/224.0/224.0 V · I 15.8/16.0/0.0 A · P 7.1 kW · T 28.0 °C | urządzenie |
| 10:52:06 | Pomiary | U 224.0/224.0/224.0 V · I 16.0/16.0/0.0 A · P 7.2 kW · T 28.0 °C | urządzenie |
| 10:52:12 | Stan (debug) | wtyk włożony | urządzenie |
| 10:52:12 | Pomiary | U 226.0/226.0/226.0 V · I 1.1/0.0/0.0 A · P 0.2 kW · T 28.0 °C | urządzenie |
| 10:52:13 | Stan (debug) | bezczynny | urządzenie |
| 10:53:17 | Offline | client_closed | urządzenie |
| 10:53:20 | Online | — | urządzenie |
| 10:53:30 | Restart | zanik zasilania / włączenie | urządzenie |
| 10:53:54 | Online | — | urządzenie |
| 10:56:14 | Pomiary | U 228.0/228.0/228.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 27.0 °C | urządzenie |
| 10:59:49 | Stan (debug) | wtyk włożony | urządzenie |
| 10:59:53 | Stan (debug) | ładowanie | urządzenie |
| 10:59:53 | Autotest | {"t":"2026-09-26 10:59:40", "r":[1,1]} | urządzenie |
| 10:59:55 | Pomiary | U 227.0/227.0/227.0 V · I 1.3/0.0/0.0 A · P 0.3 kW · T 27.0 °C | urządzenie |
| 10:59:56 | Pomiary | U 227.0/227.0/227.0 V · I 1.1/0.0/0.0 A · P 0.2 kW · T 27.0 °C | urządzenie |
| 10:59:57 | Pomiary | U 227.0/227.0/227.0 V · I 3.8/0.0/0.0 A · P 0.9 kW · T 27.0 °C | urządzenie |
| 10:59:58 | Pomiary | U 227.0/227.0/227.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 27.0 °C | urządzenie |
| 11:00:08 | Pomiary | U 226.0/226.0/226.0 V · I 2.2/2.0/2.4 A · P 1.5 kW · T 28.0 °C | urządzenie |
| 11:00:18 | Pomiary | U 226.0/226.0/226.0 V · I 5.8/6.5/6.5 A · P 4.3 kW · T 27.0 °C | urządzenie |
| 11:01:18 | Pomiary | U 226.0/226.0/226.0 V · I 4.9/5.4/5.6 A · P 3.6 kW · T 28.0 °C | urządzenie |
| 11:02:12 | Stan pracy | 200 | urządzenie |
| 11:03:30 | Stan (debug) | bezczynny | urządzenie |
| 11:03:30 | Rekord sesji | {"t":"2026-09-26 10:59:30", "s":"10:59","e":"11:03","d":237,"c":1} | urządzenie |
| 11:03:31 | Stan (debug) | wtyk włożony | urządzenie |
| 11:03:37 | Stan (debug) | ładowanie | urządzenie |
| 11:03:37 | Autotest | {"t":"2026-09-26 11:03:27", "r":[1,1]} | urządzenie |
| 11:03:39 | Pomiary | U 226.0/226.0/226.0 V · I 1.3/0.0/0.0 A · P 0.3 kW · T 28.0 °C | urządzenie |
| 11:03:40 | Pomiary | U 226.0/226.0/226.0 V · I 1.1/0.0/0.0 A · P 0.2 kW · T 28.0 °C | urządzenie |
| 11:03:41 | Pomiary | U 226.0/226.0/226.0 V · I 4.0/0.0/0.0 A · P 0.9 kW · T 28.0 °C | urządzenie |
| 11:03:42 | Pomiary | U 226.0/226.0/226.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 28.0 °C | urządzenie |
| 11:04:43 | Pomiary | U 224.0/224.0/224.0 V · I 11.0/12.4/12.6 A · P 8.1 kW · T 28.0 °C | urządzenie |
| 11:05:41 | Stan (debug) | wtyk włożony | urządzenie |
| 11:05:41 | Pomiary | U 224.0/224.0/224.0 V · I 11.3/12.4/0.0 A · P 5.3 kW · T 29.0 °C | urządzenie |
| 11:05:42 | Pomiary | U 226.0/226.0/226.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 29.0 °C | urządzenie |
| 11:05:44 | Stan (debug) | bezczynny | urządzenie |
| 11:05:44 | Rekord sesji | {"t":"2026-09-26 11:03:27", "s":"11:03","e":"11:05","d":131,"c":2} | urządzenie |
| 11:08:24 | Offline | keepalive_timeout | urządzenie |
| 11:08:57 | Online | — | urządzenie |
| 11:09:01 | Nastawa prądu | 16 | urządzenie |
| 11:09:01 | Autotest | {"t":"2000-00-00 00:00:00", "r":[1,1]} | urządzenie |
| 11:09:02 | Stan (debug) | bezczynny | urządzenie |
| 11:09:03 | Pomiary | U 227.0/227.0/227.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 25.0 °C | urządzenie |
| 11:09:12 | Restart | zanik zasilania / włączenie | urządzenie |
| 11:10:10 | Stan (debug) | wtyk włożony | urządzenie |
| 11:10:14 | Stan (debug) | ładowanie | urządzenie |
| 11:10:14 | Autotest | {"t":"2026-09-26 11:09:54", "r":[1,1]} | urządzenie |
| 11:10:16 | Pomiary | U 226.0/226.0/226.0 V · I 1.1/0.0/0.0 A · P 0.2 kW · T 26.0 °C | urządzenie |
| 11:10:18 | Pomiary | U 226.0/226.0/226.0 V · I 0.0/0.0/0.0 A · P 0.0 kW · T 26.0 °C | urządzenie |
| 11:10:19 | Pomiary | U 226.0/226.0/226.0 V · I 0.0/0.0/4.9 A · P 1.1 kW · T 26.0 °C | urządzenie |
| 11:11:19 | Pomiary | U 224.0/224.0/224.0 V · I 11.3/12.4/12.4 A · P 8.1 kW · T 27.0 °C | urządzenie |

*Pominięto powtórzenia raportów stanu i trybu (101, `{"m":0,...}`) po każdym restarcie, powtarzające się pomiary bez zmian prądu oraz sygnały podtrzymania z otwartego panelu aplikacji (co 5 s).*

---

## 5. Nagranie wyświetlacza DLB u klienta (2026‑09‑26, ok. 11:10–11:19)

**Ustalenie:** wallbox jest u klienta, diagnostyka wyłącznie zdalna. Seria restartów i reset fabryczny w logu to działania po stronie klienta.

**Moduł DLB jest zamontowany odwrotnie.** Napisy na płytce („DLB CONTROLLER V1.1 2025‑7‑13”, „PE L N”) są do góry nogami, więc wyświetlacz trzeba czytać po obróceniu o 180°.

*Korekta (26.09, wieczór, po wyciągnięciu klatek z nagrania ffmpegiem): napis na płytce w nagraniu to **„DLB CONTROLLER V1.4 2026‑1‑21”** — ten sam moduł co na zdjęciu klienta, nie V1.1 (V1.1 to nasz egzemplarz ze stanowiska). Po obróceniu klatek o 180° układ modułu (antena u góry po lewej, PE L N u góry po prawej, DIP na dole) zgadza się ze zdjęciem, na którym moduł stoi normalnie — czyli **to nagranie było zrobione telefonem do góry nogami, a nie moduł jest zamontowany odwrotnie**. Odczyt cyklu po obróceniu: L3 013 · SEt 020 · L1 012 · L2 012 · L3 013 · SEt 020 · L1 016 · L2 012. Tabela odwróconych znaków poniżej pozostaje przydatna do czytania takich nagrań.* W cyfrach siedmiosegmentowych po obróceniu „L” wygląda jak „7”, „3” jak „E”, „E” jak „3”, a kolejność znaków się odwraca.

| Widać na nagraniu | Po obróceniu | Znaczenie |
|---|---|---|
| `E7` | `L3` | etykieta fazy L3 |
| `E10` | `013` | **L3 = 13 A** |
| `335` | `SEt` | etykieta nastawy |
| `020` | `020` | **SEt = 20 A** |
| `17` | `L1` | etykieta fazy L1 |
| `210` | `012` | **L1 = 12 A** |
| `27` | `L2` | etykieta fazy L2 |
| `210` | `012` | **L2 = 12 A** |

Kolejność pozycji i czas (ok. 1 s na pozycję, cykl ok. 8 s) zgadzają się z cyklem obserwowanym na naszym stanowisku: L1 → wartość → L2 → wartość → L3 → wartość → SEt → wartość.

**Uwaga praktyczna:** `E7` i `E10` to nie kody błędów, tylko odwrócone „L3” i „13”. Łatwo je tak odczytać.

**Porównanie z logiem wallboxa** (zakładając, że nagranie pochodzi z sesji trwającej od 11:10): wallbox 11,3 / 12,4 / 12,4 A, DLB 12 / 12 / 13 A (wyświetlacz obcina do pełnych amperów). DLB widzi najwyżej ok. 1–1,5 A więcej, niż płynie do auta — albo dom pobiera bardzo mało, albo to błąd przekładnika rzędu 1 A, jak na naszym stanowisku.

**Podejrzenie — mocne, ale niepotwierdzone:** przy SEt = 20 sufit wynosi 18 A. DLB widzi 12–13 A, więc według własnej reguły przydział 16 A mieści się (16 + ok. 1 = ok. 17 ≤ 18). Mimo to wallbox pracuje na przydziale ok. 13 A. To ten sam objaw, który zanotowaliśmy na stanowisku: po zejściu w dół regulator nie wraca w górę, choć już może (tam trzymał 10 A ponad 26 s mimo dopuszczalnych 13 A). Coś raz zbiło przydział — chwilowe obciążenie domu albo stan po włączeniu zasilania — i DLB go nie podniósł.

**Napięcie jednakowe na trzech fazach** w logu wallboxa: skoro to instalacja trójfazowa u klienta, najpewniej wallbox raportuje jedną wartość napięcia dla wszystkich faz. Hipoteza o zmostkowanych fazach (jak G8) nie dotyczy tego przypadku.

**Test rozstrzygający (zdalny):** w trakcie ładowania wyłączyć na ok. 30 s zabezpieczenie zasilające sam moduł DLB, włączyć ponownie i po minucie sprawdzić prąd. Wzrost do ok. 15 A = DLB trzymał zaniżony przydział i nie wracał w górę. Bez zmiany = przyczyna gdzie indziej.

---

## 6. Aktualizacja — log do 11:46:25 (pobrany o 11:47)

### Najważniejsze: od 11:39 prąd PRZEKRACZA limit wallboxa

Po restartach zasilania wallboxa o 11:39:03 i 11:43:42 samochód pobiera **18,2–19,1 A na fazę, 12,2–12,7 kW**, przy nastawie i maksimum wallboxa **16 A** (raportowane bez zmian o 11:30:29 i 11:38:51). To więcej niż własny limit wallboxa i więcej niż sufit DLB przy SEt 20 (18 A). Samochód bierze zwykle 94–99% pozwolenia, więc pozwolenie na przewodzie CP wynosi najpewniej około 19–20 A.

Fakt pewny: pomiar prądu wallboxa był wcześniej wiarygodny — w sesji o 10:51 przy 16 A pozwolenia pokazał 16,0 A, a moc zgadza się z 3 × U × I.

Podejrzenie: wallbox po restarcie przyjmuje od DLB wartość powyżej własnego maksimum i jej nie przycina — albo przekazuje dalej samą nastawę DLB (20). Niepotwierdzone.

**Ryzyko:** praca wallboxa 16 A powyżej znamionowego prądu oraz ok. 19 A na fazę przy zabezpieczeniu głównym 20 A — każdy dodatkowy odbiornik w domu przekroczy przydział przyłącza.

### Korekta wcześniejszej hipotezy

W sekcji 5 zakładałem, że DLB „utknął” na zaniżonym przydziale i nie wraca w górę. **Log temu przeczy:** o 11:26:57 i 11:32:24 prąd wzrósł do 15,3–15,8 A (pozwolenie ok. 16 A), o 11:25:58 spadł chwilowo do ok. 7 A, a o 11:36 wrócił do ok. 12,4 A. Przydział zmienia się w obie strony — obraz jest niestabilny, a nie zablokowany.

### Przebieg 11:11–11:46

| Czas | Co się dzieje | Prąd L1 / L2 / L3 | Moc |
|---|---|---|---|
| 11:10–11:16 | ładowanie | 11,3 / 12,4 / 12,4 A | 8,1 kW |
| 11:16:30 | **L2 spada do zera**, sekundę później koniec sesji | 11,3 / 0 / 12,4 A | 5,3 kW |
| 11:16:39–11:21 | nowa sesja | 11,3 / 12,4 / 12,4 A | 8,1 kW |
| 11:21:08 | **znów L2 spada do zera** i koniec sesji | 11,3 / 0 / 12,4 A | 5,3 kW |
| 11:22:43 | nowa sesja | 11,5 / 12,6 / 12,6 A | 8,2 kW |
| 11:25:58 | spadek | 6,7 / 7,4 / 7,2 A | 4,8 kW |
| 11:26:57 | **wzrost do ok. 16 A** | 14,4 / 15,8 / 15,8 A | 10,2 kW |
| 11:28:33 | koniec sesji | — | — |
| 11:30:39 | restart zasilania wallboxa | — | — |
| 11:32:24 | ładowanie ok. 16 A | 14,4 / 15,8 / 15,3 A | 10,1 kW |
| 11:32:40–11:35:03 | koniec sesji | — | — |
| 11:35:14 | nowa sesja, wraca do ok. 12,4 A | 11,3 / 12,4 / 12,6 A | 8,1 kW |
| 11:38:48–11:39:03 | ponowne połączenie i **restart zasilania wallboxa w trakcie ładowania** | — | — |
| 11:39:30 | 16 A | 16,1 / 16,1 / 16,1 A | 10,8 kW |
| 11:39:33 | **ponad 16 A** | 18,2 / 18,3 / 18,0 A | 12,2 kW |
| 11:41–11:42 | **ponad 16 A** | 18,7 / 18,8 / 18,2 A | 12,5 kW |
| 11:43:30–11:43:42 | rozłączenie i **restart zasilania wallboxa** | — | — |
| 11:44:07 | ładowanie wznowione od razu | 13,5 / 13,4 / 13,5 A | 9,2 kW |
| 11:44:13–11:44:22 | **ponad 16 A** | 18,4–18,7 / 18,5–19,1 / 18,0–18,5 A | 12,4–12,7 kW |
| 11:44:25 | chwilowo | 15,8 / 15,8 / 16,1 A | 10,8 kW |
| 11:45:25–11:46:25 | **ponad 16 A, trwa** | 18,7 / 19,1 / 18,2–18,5 A | 12,6–12,7 kW |

Dodatkowo o 11:28:42 pojawił się punkt danych 倒计时剩余时间 („pozostały czas odliczania”) = 0.

### Do ustalenia pilnie

1. Co dokładnie klient wyłączał o 11:30, 11:39 i 11:43 — wallbox, DLB czy oba. Log pokazuje restarty zasilania **wallboxa**.
2. Czy zmieniał przełączniki DIP na DLB albo nastawę w samochodzie.
3. Co pokazuje teraz wyświetlacz DLB (L1/L2/L3 i SEt, czytane po obróceniu).

---

## 7. Powiązanie z opisem sprawy (`istotne_casey/Karol`) i zdjęciami klienta

To ta sama sprawa — nagranie w folderze Karol jest identyczne z analizowanym wyżej (ta sama suma kontrolna).

### Fakty

- **Klient zgłaszał ładowanie 13 kW przy 11‑kilowatowym samochodzie.** Log z 26.09 pokazuje to samo niezależnym pomiarem: 18–19 A na fazę, **12,2–12,7 kW** (11:39–11:46). Dwa pomiary — samochodu i wallboxa — się zgadzają.
- **Zdjęcie komunikatu** „Ochrona przed przeciążeniem prądu — Automatyczne przełączenie na ładowanie niskim prądem": w tym samym momencie wallbox pokazuje w polu **„DLB 0.0 A"**, nastawę **15 A** i napięcie **224 V**. *Korekta 2026‑09‑26:* 224 V nie dowodzi przepływu prądu — napięcie spoczynkowe u klienta wynosiło tego dnia 226–228 V. Zdjęcie może równie dobrze pochodzić z chwili po włączeniu, bez auta.
- **Zdjęcie normalnego ładowania:** „DLB 12.1 A", 9,0 kW, nastawa 16 A.
- **Zdjęcie w spoczynku:** „DLB 0.0 A", 243 V, bez komunikatu.
- Moduł DLB na zdjęciu: **DLB CONTROLLER V1.4, 2026‑1‑21** (nasz egzemplarz ze stanowiska to V1.1). Na zdjęciu wyświetlacz czyta się normalnie; na nagraniu moduł był obrócony o 180° — albo telefon, albo drugi z użytych kontrolerów.
- Po wymianie przekładnika z przylutowanymi przewodami próg ograniczania się ustabilizował. Dziś DLB pokazuje 12 / 12 / 13 A przy 11,3 / 12,4 / 12,4 A z wallboxa — zgodność w granicach ok. 1 A.

### Mechanizm — podejrzenie, mocno poparte, niepotwierdzone

Hipoteza serwisu: gdy wartość z DLB chwilowo wynosi 0, wallbox koduje na CP pełne 20 A z nastawy DLB. Dane się z nią zgadzają:

1. Wartość z DLB spada do 0 — zdjęcie komunikatu pokazuje „DLB 0.0 A" w trakcie ładowania.
2. Pozwolenie na CP rośnie do ok. 20 A, niezależnie od nastawy wallboxa — samochód bierze zwykle 94–99% pozwolenia, a w logu pobiera 18–19 A.
3. Samochód pobiera więcej, niż wynosi nastawa wallboxa — wallbox włącza własną ochronę nadprądową i wyświetla komunikat.
4. Im niższa nastawa, tym większa różnica między ok. 19 A a nastawą, więc ochrona zadziała szybciej — dokładnie to zgłosił klient.

W logu z 26.09 przekroczenie wystąpiło **po restarcie zasilania wallboxa w trakcie ładowania** (11:39:03, 11:43:42), a nie po zmianie nastawy — w logu nie ma żadnej zmiany nastawy po 10:44:56. Wyzwalacze są więc co najmniej dwa: zmiana prądu (według klienta) i restart wallboxa (według logu). W obu przypadkach wallbox przez chwilę nie ma świeżej wartości z DLB.

Wada leżałaby wtedy po stronie wallboxa: nie przycina pozwolenia do własnej nastawy, gdy brakuje danych z DLB. To tłumaczy, dlaczego wymiana kontrolera DLB na drugi egzemplarz nic nie zmieniła.

### Czego ten mechanizm nie tłumaczy

- Komunikatu przy samym włączeniu zasilania, bez samochodu — bez prądu nie ma przeciążenia. Log nie ma punktu danych błędu, więc tego nie sprawdzimy zdalnie.
- W logu przekroczenie trwało ponad 7 minut (11:39–11:46) bez zatrzymania ładowania; jedyny ślad reakcji to chwilowy spadek do ok. 16 A o 11:44:25. Nie wiemy, czy komunikat się wtedy pojawił.
- Samochód opisany jako 11 kW pobiera 19 A na fazę — jego ładowarka pokładowa musi przyjmować więcej niż 16 A.

### Test rozstrzygający na stanowisku (bez samochodu 22 kW)

Pomiar wypełnienia sygnału CP oscyloskopem w trakcie ładowania z DLB, przy nastawie wallboxa 16 A: odciąć wallboxowi dane z DLB (zdjąć zasilanie modułu DLB albo zrestartować wallbox) i obserwować wypełnienie. 26,7% = 16 A — wallbox przycina poprawnie. **33,3% = 20 A — hipoteza potwierdzona.** Samochód do tego testu nie musi umieć pobrać ponad 16 A, bo mierzymy samo pozwolenie. Pamiętać o izolowanym wejściu oscyloskopu — patrz incydent z różnicówką w `DANE_DIAGNOSTYCZNE.md`.

### Zalecenie dla klienta do czasu wyjaśnienia

Ustawić limit prądu ładowania w samochodzie na 16 A albo niżej. Samochód bierze mniejszą z dwóch wartości — własnego limitu i pozwolenia z CP — więc to zabezpiecza przyłącze niezależnie od błędu wallboxa.

**Korekta do testu (2026‑09‑26):** test na stanowisku ma sens tylko ze **sparowanym** modułem DLB. Bez parowania wallbox nie przyjmuje danych z DLB i pracuje w zwykłym trybie — a w nim działał u klienta poprawnie przed montażem DLB. Próba „włączenia trybu DLB bez modułu” niczego więc nie wykaże. Serwis nie ma obecnie ani modułu DLB, ani samochodu.

**Test możliwy od ręki u klienta:** stan „sparowany, ale bez świeżych danych z DLB” został już odtworzony w logu — restarty zasilania wallboxa w trakcie ładowania o 11:39 i 11:43 dały 18–19 A. Wystarczy powtórzyć to raz, krótko (1–2 min, bez innych odbiorników w domu), i sfotografować ekran wallboxa, podczas gdy my śledzimy prąd w logu na żywo. „DLB 0.0 A” na ekranie przy prądzie powyżej 16 A potwierdza cały łańcuch.

### Łańcuch zdarzeń — od zmiany limitu do komunikatu (wersja robocza, 2026‑09‑26)

`[F]` = fakt z logu, zdjęć albo relacji klienta · `[Z]` = założenie

0. Stan normalny: DLB mierzy prądy L1–L3, wylicza, ile zostaje dla auta (sufit 18 A przy SEt 20), i wysyła to radiem do wallboxa. Wallbox pokazuje wartość w polu „DLB x.x A" `[F]` i ustawia na CP mniejszą z dwóch wartości: własnej nastawy i wartości z DLB `[Z]`.
1. Wyzwalacz: zmiana nastawy na wallboxie w trakcie ładowania (relacja klienta) albo restart zasilania wallboxa (log, 11:39 i 11:43) `[F]`.
2. Wallbox przez chwilę nie ma ważnej wartości z DLB — pole pokazuje „DLB 0.0 A" `[F — zdjęcie]`; że przyczyną jest zmiana lub restart `[Z]`.
3. Zero traktuje nie jako „brak danych", tylko jako „dom nic nie pobiera" albo „brak ograniczenia" i wylicza pozwolenie z samej nastawy DLB — 20 A, bez przycięcia do własnej nastawy i bez 10‑procentowego bufora `[Z — rdzeń hipotezy]`.
4. Wystawia na CP wypełnienie ok. 33% (20 A) `[Z — do zmierzenia]`.
5. Samochód bierze 94–99% pozwolenia: 18–19 A na fazę, 12–13 kW `[F — log i ekran auta]`.
6. Wallbox porównuje zmierzony prąd z **własną** nastawą (15–16 A), a nie z tym, co sam wystawił na CP `[Z]`.
7. Prąd przekracza nastawę — komunikat „Ochrona przed przeciążeniem prądu — Automatyczne przełączenie na ładowanie niskim prądem" `[F — treść]` i obniżenie prądu `[Z — jak bardzo]`. Im niższa nastawa, tym większe przekroczenie i szybsze zadziałanie `[F — obserwacja klienta; mechanizm Z]`.
8. Po powrocie danych z DLB regulacja wraca do normy, a przy następnej zmianie cykl się powtarza. Niestabilne ograniczanie i schodzenie poniżej 6 A mogą być tym samym cyklem, nałożonym na błąd uszkodzonego przekładnika `[Z]`.

Nie pasuje: przekroczenie o 11:39–11:46 trwało 7 min bez zatrzymania (przy nastawie 16 A przekroczenie było tylko ok. 19%); komunikat przy włączeniu bez auta (bez prądu nie ma przeciążenia); samochód „11 kW" pobierający 19 A.

### Hipoteza uzupełniająca: komunikat liczony z wyliczonego pozwolenia, a nie ze zmierzonego prądu (2026‑09‑26)

Pomysł serwisu: ochrona przed przeciążeniem porównuje z nastawą wallboxa **wartość, którą wallbox wyliczył do wystawienia na CP**, a nie prąd zmierzony. W stanie A (bez auta) na CP nie ma PWM, więc chodzi o wartość wyliczoną, nie o sygnał.

Co tłumaczy `[Z]`:
- **Komunikat przy włączeniu bez auta** — po starcie wartość z DLB = 0, wyliczone pozwolenie 20 A > nastawa, choć prąd nie płynie.
- **Szybsze wyzwalanie przy niższych nastawach** — przy 6 A wyliczone pozwolenie przekracza nastawę także w normalnej pracy (np. przydział 13 A), nie tylko przy zerze z DLB.
- **Przekroczenie 11:39–11:46 bez zatrzymania** — częściowo: jeśli reakcja na komunikat obniża nastawę wallboxa, a w trybie DLB CP i tak jest liczone z wartości DLB, komunikat pojawia się, a prąd zostaje wysoki.

Test u klienta, bez przepływu prądu: DLB sparowany, auto odłączone, nastawa 6 A, restart zasilania wallboxa, nagranie ekranu przez 2 min (komunikat i pole „DLB x.x A"); potem to samo z autem wpiętym, ale nieładującym. Komunikat bez prądu — zwłaszcza przy „DLB 0.0 A" — potwierdza tę hipotezę. Przepływ prądu weryfikujemy na żywo w logu Tuya.

### Aktualizacja 2026‑09‑26 (wieczór): brak dalszych testów u klienta — wersja końcowa z posiadanych danych

**Nowe fakty od serwisu:**
- Nastawę prądu **na samym wallboxie** da się zmienić tylko przy wyłączonym ładowaniu; w trakcie ładowania — wyłącznie z aplikacji.
- Komunikat o przeciążeniu pojawiał się **zanim klient cokolwiek robił w aplikacji**.
- Dalszych testów u klienta nie będzie.

**Wniosek:** zmiana nastawy **nie jest wyzwalaczem** — przesuwa jedynie próg, przy którym komunikat się pojawia. Wyzwalaczem jest brak danych z DLB; pewny moment, w którym występuje, to włączenie zasilania wallboxa (do nadejścia pierwszej ramki z DLB). Restart w trakcie ładowania (11:39, 11:43) to ten sam stan, tylko z autem pobierającym prąd.

**Mechanizm — wersja końcowa (`[F]` fakt, `[Z]` założenie):**
1. Włączenie zasilania wallboxa → brak danych z DLB → pole „DLB 0.0 A" `[F — zdjęcie; Z — że to stan po włączeniu]`.
2. Wallbox liczy pozwolenie z samej nastawy DLB: 20 − 0 = 20 A `[Z]`.
3. Porównuje wyliczone pozwolenie z własną nastawą: 20 > 16 → komunikat, mimo że bez auta prąd nie płynie `[Z]`; zgodne z relacją klienta (komunikat przy włączeniu, bez auta, przed użyciem aplikacji) `[F]`.
4. Po pierwszej ramce z DLB pozwolenie wraca do normalnej wartości, komunikat znika, wallbox ładuje normalnie `[Z]`.
5. Jeśli brak danych trafi na trwające ładowanie (restart w trakcie), CP dostaje 20 A → auto 18–19 A, 12–13 kW `[F — log i ekran auta]`.
6. Niższa nastawa = niższy próg w kroku 3; przy 6–10 A wyliczone pozwolenie przekracza nastawę także w normalnej pracy (np. przydział 13 A) → komunikat częściej i szybciej `[F — obserwacja klienta; Z — mechanizm]`.

**Niestabilne ograniczanie i spadki poniżej 6 A (pierwsza skarga)** — najpewniej osobny wątek: przy SEt 20 sufit wynosi 18 A, czajnik (ok. 9 A na jednej fazie) zostawia autu ok. 9 A, a przy kroku 3 A daje to przydział 7 A; zawyżony odczyt uszkodzonego przekładnika (po wymianie się ustabilizowało) mógł zepchnąć przydział do 4 A, czyli poniżej 6 A → pauza `[Z — drabinka 3 A zmierzona na V1.1, klient ma V1.4]`.

**Mocne:** 18–19 A przy maksimum 16 A z dwóch niezależnych pomiarów; 20 to jedyna taka liczba w układzie (SEt na DLB); „DLB 0.0 A" na ekranie z komunikatem.
**Słabe:** dlaczego przekroczenie po 11:39 trwało 7 min (dane z DLB nie wracały przez tyle czasu? — nie wiadomo); co dokładnie robi wallbox po komunikacie.

*Korekta (14:47): oba „słabe” punkty wyjaśnia log pobrany do 14:26 — sekcja 8. „7 min” wynikało z końca pobranego wtedy logu (11:46:25); „DLB 0.0 A” przestaje być mocnym punktem; „komunikat bez auta” nie ma pokrycia w logu. Mechanizm z tej sekcji zastępuje wersja z 8.6.*

**Dalej:** zgłoszenie do producenta z dowodami i konkretnym pytaniem o logikę trybu DLB; klientowi do czasu poprawki — praca bez DLB (działała poprawnie) albo limit 16 A w samochodzie.

---

## 8. Log 11:30–14:26 (pobrany 2026‑09‑26 o 14:47) — alarm przeciążenia widoczny w logu

Wcześniejsze sekcje opierały się na logu pobranym o 11:47. Po 11:47 u klienta było jeszcze 14 włączeń zasilania, zmiany nastawy i 12 alarmów. Urządzenie zniknęło z sieci o 14:26 (keepalive_timeout).

**Korekty wcześniejszych sekcji:**
- „Brak punktu danych błędu” (sekcja 1) — błędne. Punkt istnieje: 报警信息 („informacja o alarmie”) `{"t":"<czas urządzenia>","v":400}`, razem ze stanem pracy **400** i stanem debug 发生故障 („wystąpił błąd”).
- „Przekroczenie trwało 7 min (11:39–11:46)” (sekcje 6, 7, wersja końcowa) — błędne. 11:46:25 to był koniec pobranego wtedy logu. Były dwa odcinki, ok. 4 i ok. 5 min (8.1).
- „Komunikat przy włączeniu bez auta” — nie ma pokrycia w logu; było to moje założenie, nie relacja klienta. Wszystkie 12 alarmów wystąpiło w trakcie ładowania.
- „DLB 0.0 A na zdjęciu z komunikatem” jako mocny dowód braku danych z DLB — wycofane (8.5).

### 8.1 Przekroczenie 11:39–11:49

| Czas | Zdarzenie | L1 / L2 / L3 [A] | Moc |
|---|---|---|---|
| 11:38:48 | online po włączeniu zasilania, nastawa 16 | — | — |
| 11:38:58 | ładowanie (300) | — | — |
| 11:39:30 | | 16,1 / 16,1 / 16,1 | 10,8 kW |
| 11:39:33 | | 18,2 / 18,3 / 18,0 | 12,2 kW |
| 11:39:36–11:39:45 | | 18,4 / 18,8 / 18,2 | 12,4 kW |
| 11:39:51 | 上位机心跳 = off — od teraz pomiar co 60 s | — | — |
| 11:40:45, 11:41:45, 11:42:45 | | 18,4–18,7 / 18,8 / 18,2 | 12,4–12,5 kW |
| 11:43:30 | offline (client_closed) — wyłączenie zasilania, **koniec odcinka 1** | — | — |
| 11:43:33–11:44:06 | online, restart „zanik zasilania”, auto od razu ładuje | — | — |
| 11:44:07 | | 13,5 / 13,4 / 13,5 | 9,2 kW |
| 11:44:13–11:44:22 | | 18,4–18,7 / 18,5–19,1 / 18,0–18,5 | 12,4–12,7 kW |
| 11:44:25 | | 15,8 / 15,8 / 16,1 | 10,8 kW |
| 11:44:32 | 上位机心跳 = off — pomiar co 60 s | — | — |
| 11:45:25–11:48:25 | | 18,7 / 18,8–19,1 / 18,2–18,5 | 12,6–12,7 kW |
| 11:49:24 | **spadek** — bez restartu, bez zmiany nastawy, bez żadnego zdarzenia po stronie wallboxa | 8,8 / 9,1 / 8,4 | 6,0 kW |
| 11:50:16 | koniec sesji (rekord: start 11:43:39, 395 s) | 0 | — |

Odcinek 1: ok. 4 min, zakończony wyłączeniem zasilania. Odcinek 2: ok. 5 min, zakończony spadkiem do ok. 9 A między 11:48:25 a 11:49:24. W żadnym alarmu — maksimum 19,1 A = 119% nastawy.

Czy przez ten czas brakowało danych z DLB — log tego nie pokaże, bo wartości z DLB w nim nie ma `[F]`. Spadek o 11:49 nie ma przyczyny po stronie wallboxa, więc najpewniej prąd obniżył DLB (np. włączony odbiornik w domu) `[Z]`.

To samo przekroczenie nastawy 16 występuje też niezależnie od chwili włączenia: 12:01:14–12:01:33 (17,9–18,7 A), 12:05:17–12:05:45 (18,2–18,7 A, sesja zaczęta 4 min po włączeniu), 12:57:08 (18,7 / 18,8 / 18,2 A, 2 min po włączeniu, po okresie ok. 14–15 A) `[F]`.

### 8.2 Co robi wallbox po alarmie — przykład 11:50–11:52

| Czas | Zdarzenie |
|---|---|
| 11:50:30 | ładowanie, nastawa 16 |
| 11:50:35 | 9,1 / 6,4 / 0 A — narastanie (2 s sesji) |
| 11:50:40 | 发生故障, stan **400**, 报警信息 `v:400` (czas urządzenia 11:50:38), **nastawa 16 → 15** (zgłasza sam wallbox) |
| 11:50:41 | 0 / 0 / 0 A — ładowanie przerwane |
| 11:51:16–11:51:17 | bezczynny → wtyk włożony (200) |
| 11:51:21 | auto samo wznawia ładowanie (300), nastawa 15 |
| 11:51:36–11:51:40 | L1: 16,4 → 17,0 → 19,3 → 19,6 → 20,2 A (L3 = 0) |
| 11:51:43 | kolejny alarm 400 |

### 8.3 Wszystkie alarmy (czasy z logu, lokalne)

| # | Alarm | Nastawa | Prąd w chwili alarmu (maks. faza / nastawa) | Kontekst |
|---|---|---|---|---|
| 1 | 11:50:40 | 16 | brak pomiaru (5 s wcześniej 9,1 / 6,4 / 0 — szybkie narastanie) | nowa sesja od 11:50:30 |
| 2 | 11:51:43 | 15 | 20,2 / 19,1 / 0 — **135%** | wznowienie po alarmie 1 |
| 3 | 11:53:41 | 16 | 20,8 / 19,1 / 0 — **130%** | 36 s po powrocie online (włączenie zasilania) |
| 4 | 11:56:18 | 13 | brak (5 s wcześniej 9,3 / 9,9 / 0) | nastawa 13 z menu o 11:55:45 (bez ładowania), sesja od 11:56:07 |
| 5 | 11:59:31 | 13 | 16,4 / 16,4 / 15,8 — **126%** | 52 s po powrocie online |
| 6 | 12:05:56 | 7 | 18,2 / 18,3 / 17,7 — **261%** | nastawa 16 → 7 z menu w trakcie ładowania, 10 s wcześniej |
| 7 | 12:22:29 | 10 | 12,9 / 11,8 / 0 — **129%** | nastawa 16 → 10 z menu w trakcie ładowania, 10 s wcześniej |
| 8 | 12:24:33 | 10 | 16,7 / 15,6 / 0 — **167%** | 16 s po powrocie online; zapisana nastawa 10 |
| 9 | 12:26:33 | 16 | brak (5 s wcześniej 8,8 / 9,1 / 0 — szybkie narastanie) | 61 s po powrocie online |
| 10 | 12:32:09 | 9 | brak (12:31:10: 17 / 15,3 / 0) | nastawa 16 → 9 z menu w trakcie ładowania, 10 s wcześniej |
| 11 | 12:34:27 | 8 | brak (24 s wcześniej 1,1 / 1,3 / 0) | nastawa 8 po alarmie 10, nowa sesja od 12:33:58 |
| 12 | 13:00:13 | 16 | brak (35 s wcześniej 10,2 / 9,6 / 0) | 91 s po powrocie online |

Luki w pomiarach: po zdarzeniu 上位机心跳 = off wallbox wysyła pomiar tylko co 60 s (np. 11:39:51 → 11:40:45, 11:41:45…; 12:59:43 → nic do alarmu o 13:00:13). Dlatego przy 6 alarmach prądu w chwili zadziałania nie znamy.

### 8.4 Fakty z logu

- **Alarm tylko w trakcie ładowania** — 12 z 12 przy stanie 300. W stanie bezczynnym i przy wpiętym, nieładującym aucie (np. 12:06:52–12:12:19, 13:12:50–14:26) ani razu.
- **Reakcja:** ładowanie stoi po ok. 1 s (prąd 0); stan 400; **nastawa −1 A** w 10 z 12 przypadków (16→15, 13→12, 10→9, 9→8, 8→7, 7→6) — to jest „automatyczne przełączenie na ładowanie niskim prądem”. Obniżka nie jest zapisywana: po włączeniu zasilania wraca nastawa sprzed alarmu (12:00:24 → 13, 12:24:20 → 10, 12:27:16 → 16, 13:00:40 → 16).
- **Po alarmie:** w 7 przypadkach po 10–55 s powrót do „wtyk włożony”; dwa razy stan błędu trwał 77 s i 137 s, aż klient wyłączył zasilanie. Auto samo wznowiło ładowanie 2 razy (11:51:21, 12:34:42); po pierwszym wznowieniu kolejny alarm po 22 s, przy 20,2 A i nastawie już 15.
- **Próg:** przy prądzie znanym w chwili alarmu zawsze ≥126% nastawy (126, 129, 130, 135, 167, 261%); przy 119% (19,1 A / 16 A) — 5 min bez alarmu. Po przekroczeniu w trakcie narastania alarm w 1–3 s.
- **Zmiana nastawy w menu wallboxa w trakcie ładowania** — w logu 4 razy (12:05:45, 12:22:17, 12:31:57, 12:34:49; stan 300, zgłoszenia od urządzenia, nie z aplikacji). Trzy obniżki → alarm ok. 10 s po ostatnim naciśnięciu, prąd do chwili alarmu bez zmian. Log przeczy więc informacji, że na wallboxie nastawę zmienia się tylko przy wyłączonym ładowaniu — menu przyjmuje zmianę także w trakcie.
- **Prąd powyżej nastawy ustawionej przed sesją:** 16,7 A przy 10 (12:24:30), 16,4 A przy 13 (11:59:29), 20,2 A przy 15 (11:51:40), 18–19,1 A przy 16 (11:39–11:49, 12:05, 12:57). Po włączeniu o 12:21:45 przy nastawie 16 prąd od razu tylko 12,9–13,2 A — czyli ograniczał go nie wallbox, tylko coś innego.
- **Przy nastawie 15–16 alarmy wypadły w sesjach z L3 = 0**, z szybkim narastaniem (ok. 9 A po 2 s; L1 do 20,2–20,8 A). W sesjach trójfazowych (narastanie ok. 30 s) auto stawało na 18–19,1 A i alarmu nie było.
- **Pomiary:** `d` = czas sesji w dziesiątych sekundy (potwierdzone), `e` = energia sesji (rośnie o ok. 0,1 kWh; jednostka nieustalona). Nowe stany: 400 / 发生故障 (błąd), 休眠 (uśpienie, 13:17:48).
- Ograniczanie i pauzy jak przy DLB: 12:12:55 → 12:13:04 (12,6 → 5,5 A → pauza), 12:54:16 → 12:54:34, 12:36 → 12:37:53.

### 8.5 Zdjęcie z komunikatem — nowa interpretacja

Zdjęcie: komunikat, nastawa **15**, **224 V**, „DLB 0.0 A”. W logu nastawa 15 pojawia się właśnie po alarmach przy nastawie 16 (11:50:40, 11:53:41, 12:26:33, 13:00:13), a pierwszy odczyt po zatrzymaniu to 0 A przy 224–225 V. Zdjęcie pasuje więc do chwili tuż po alarmie, gdy ładowanie już stoi. Jeśli pole „DLB x.x A” to prąd zmierzony przez DLB (w spoczynku 0.0, przy ładowaniu 12.1 A ≈ prąd auta), to 0.0 A znaczy po prostu „auto nie ładuje” `[Z]`. Nie jest to dowód braku danych z DLB.

### 8.6 Mechanizm — wersja po pełnym logu

1. W trybie DLB prąd ładowania nie jest ograniczany nastawą wallboxa `[F — prąd powyżej nastawy ustawionej przed sesją, 4 nastawy; Z — że to pozwolenie na CP, bo auto nie bierze więcej, niż pozwala CP]`.
2. Przy małym obciążeniu domu auto bierze 18–19 A na trzech fazach, a przy L3 = 0 L1 dochodzi do 20–21 A `[F]`. Pozwolenie ok. 19–20 A — jedyna taka liczba w układzie to SEt 20 na DLB `[Z]`.
3. Ochrona przeciążeniowa porównuje **zmierzony** prąd z nastawą wallboxa i wyzwala przy ok. 120–125% `[F — dane z 8.4; Z — dokładny próg]`.
4. Po alarmie: stop, nastawa −1 A, powrót do gotowości. Auto może wznowić, a niższa nastawa nie obniża prądu (pkt 1), więc alarm się powtarza `[F — 11:50:40 → 11:51:43]`.
5. Im niższa nastawa, tym niższy próg — przy nastawie 10 wystarcza 12,9 A `[F]`. To tłumaczy „im niżej ustawimy, tym szybciej wyskakuje”.
6. Zmiana nastawy z menu w trakcie ładowania → alarm po ok. 10 s `[F]`; najpewniej nowa nastawa zaczyna obowiązywać po zamknięciu menu, a ochrona reaguje, zanim auto zdąży zejść z prądem `[Z]`.
7. „Zaraz po włączeniu zasilania” w logu = wpięte auto zaczyna ładować po kilku sekundach, alarm przychodzi po 15–90 s `[F]`.

Hipoteza „brak danych z DLB po włączeniu → 20 A” nie jest potrzebna do wyjaśnienia logu: przekroczenie występuje też kilka minut po włączeniu, a po włączeniu o 12:21:45 prąd był od razu ograniczony do ok. 13 A. Wykluczyć jej nie można, ale przestaje być rdzeniem mechanizmu.

**Pytanie do producenta (aktualne):** w trybie DLB prąd przekracza nastawę wallboxa (log: 16,7 A przy nastawie 10, 20,2 A przy 15, 19,1 A przy 16), a ochrona przeciążeniowa (alarm 400) porównuje prąd z tą nastawą i po zadziałaniu obniża ją o 1 A. Czy w trybie DLB pozwolenie na CP nie powinno wynosić min(nastawa, wartość z DLB)? Jaki jest próg alarmu 400 i czy po zmianie nastawy w trakcie ładowania auto dostaje czas na zmniejszenie prądu?

**Dla klienta do czasu poprawki:** praca bez DLB albo limit prądu w samochodzie nie wyższy niż nastawa wallboxa. `[Z]` Do rozważenia: SEt na DLB nie wyższe niż nastawa wallboxa — DLB sam nie da wtedy więcej niż nastawa (kosztem mocy, jeśli V1.4 ma sufit 90% i kroki 3 A jak V1.1).

---

## 9. Raport do producenta (2026‑09‑26, wieczór) — na podstawie materiałów instalatorów

Folder: `istotne_casey/Karol/raport_do_producenta/` — `AMPERE_POINT_case_report_wallbox_DLB_EN.pdf` (bazowy), `…_ZH.pdf` (chiński, pełna treść), `…_PL.pdf`; gotowe do wysłania (bez oznaczeń wersji w treści). Źródła LaTeX w `src/` (xelatex; chiński przez Noto Sans CJK SC bez xeCJK, bo w sandboxie brak `ctexhook.sty`), wycinki zdjęć w `img/`. Instalatorzy problemów nie „odtwarzali” — stwierdzili je na miejscu i udokumentowali nagraniem; raport używa tego sformułowania. **Nagranie nie jest oferowane producentowi** (wizerunek instalatorów, brak zgody) — w raporcie są tylko wycinki ekranów; „na życzenie” dostępny jest wyłącznie eksport logu Tuya.

**Materiały instalatorów** (`dostarczone_materiały/przedstawiajace_problem/`, nagranie wideo, informacje zweryfikowane):
- **Problem 1 (priorytet):** DLB SEt 18 (wyświetlacz „018”), nastawa wallboxa 16 → auto dwufazowe pobiera 16,9 A (7,3 kW). Obniżenie nastawy w menu do 9 A w trakcie ładowania → przez kilka sekund nadal 16,6 A / 7,1 kW → komunikat przeciążenia, nastawa 8 A, ładowanie stoi. **Uszkodzona ładowarka pokładowa auta trójfazowego** (auto nie reagowało, potrzebny mechanik).
- **Problem 2:** DLB celowo nisko, auto trójfazowe 10,8 A / 7,4 kW; czajnik → przydział < 6 A → pauza (poprawnie); po wyłączeniu czajnika **brak wznowienia** (5 min); rusza dopiero po przepięciu auta.
- Dwa niezależne zestawy DLB, dwa auta (2‑ i 3‑fazowe), wallbox bez DLB działał poprawnie na tej samej instalacji i gnieździe.

**Dopasowanie wideo ↔ log:** Problem 1 = sesja 12:27:20–12:32:09 (17,0/15,3/0 A, 7,3 kW; SET 6→7→8→9 o 12:31:57–59; alarm 400 o 12:32:09, SET 8). Problem 2 = sesja od 12:35:51 (10,5–10,8 / 10,7–11,0 / 11,1–11,6 A, 7,4 kW), pauza 12:37:53 (stan 200), brak wznowienia do 12:44:21 (offline).

**Zakres raportu (decyzja Dawida, wieczór):** wyłącznie to, co jest w `przedstawiajace_problem/` (ogolne.txt, problem_1_opis.txt, problem_2_opis.txt, zrzuty, zdjęcia gniazd) plus fragmenty logu odpowiadające dokładnie tym dwóm zdarzeniom (12:27–12:32 i 12:35–12:44). Usunięte: wcześniejsze obserwacje klienta (13 kW, komunikat przy niższych nastawach), sesje 11:39–11:48 i 19,1 A, tabela 12 alarmów, zdjęcia z `przed_diadnozą` (komunikat 15 A, moduł V1.4, RF433, rozdzielnica C20), wzmianka o przekładniku z przylutowanymi przewodami. „Co wykluczono”: instalacja (wallbox działał wcześniej), wadliwy wallbox (bez DLB działa poprawnie), samochód (dwa auta), wadliwy DLB albo przekładnik (dwa pełne niezależne zestawy z akcesoriami). Nagranie nie jest oferowane; log producent ma u siebie. Wersje EN 6 str., ZH 5 str., PL 6 str.

**Co świadomie pominąłem w raporcie:** komunikat „przy samym włączeniu zasilania, bez auta” z pierwotnej relacji klienta — nie ma go w materiałach instalatorów ani w logu (12/12 alarmów w trakcie ładowania); Dawid sam wcześniej uznał tę informację za niepewną. Model wallboxa nie jest nazwany (tylko „11 kW, 16 A” + PID/ID/firmware), bo nie został potwierdzony.

**Przegląd pod kątem nieścisłości (wieczór) — poprawione w trzech wersjach:** „zabezpieczenie główne 20 A” → obwód wallboxa ma wyłącznik 3‑bieg. C20 + RCD 40 A/30 mA (odczytane ze zdjęcia rozdzielnicy; „zabezpieczenie 20 A” z relacji dotyczy tego obwodu, nie głównego); „brak limitu w obu autach” → tylko auto B ma to potwierdzone; „oba problemy z oboma autami” → Problem 1 z oboma, Problem 2 udokumentowany z autem B; CSL 20 A przy sesji 11:39–11:48 → wskazane jako odczyt SEt 020 z nagrania ok. 11:15, nie jako pewnik dla tej sesji; „pole DLB = prąd zmierzony przez DLB” → usunięte (nie wiadomo, czy to pomiar, czy przydział); „moduł zamontowany do góry nogami” → klatka obrócona (patrz korekta w sekcji 5); „samochód sam wznowił” → „ładowanie wznowiło się”; „−1 A przy każdym alarmie” → w 10 z 12; „1 761 zdarzeń 10:43–14:26” → liczba dotyczyła okna od 11:30, usunięta; „eksport na życzenie” → producent ma log u siebie; „przekładniki na zasilaniu głównym” → tylko L1/L2/L3 (miejsce nieudokumentowane); „język wyświetlacza polski” usunięte (DP 语言配置 = „it”, zdjęcia po polsku — niepotrzebna niejasność); w tabeli „instrukcja vs obserwacja” komunikat „Automatic switch…” oznaczony jako komunikat wallboxa, nie cytat z instrukcji; opis ustawień Problemu 2 zgodnie z tekstem instalatorów („celowo niżej, aby wywołać usterkę”), bez mojej interpretacji celu.

**Drobne korekty względem sekcji 8 (przeliczone jeszcze raz z surowego logu):** alarm 4 — ostatni pomiar 5 s wcześniej, alarm 10 s po starcie sesji; 12:24:30 — 14 s po online; alarm 2 nastąpił 21 s po wznowieniu ładowania (nie 22).

### 9.1 Stan po wysłaniu (2026‑09‑27)

Raport wysłany do producenta. Odpowiedź: zrobią przegląd firmware. Terminu i wskazania, którego urządzenia dotyczy poprawka (wallbox, kontroler DLB, moduł radiowy), jeszcze nie ma.

DLB nie ma aktualizacji OTA, a zamówiona partia ma to samo, wadliwe oprogramowanie. Pomysł Dawida: wziąć jeden zestaw do pełnego zbadania i wgrywać poprawione oprogramowanie samodzielnie, przez złącze programatora na kontrolerze. Architektura łącza (gdzie co się liczy) i warunki takiej operacji: `DANE_DIAGNOSTYCZNE.md`, sekcja „Łącze DLB ↔ wallbox i firmware”.

---

## 10. Przerwy w ładowaniu i wznowienia — przegląd całego logu (2026‑09‑28)

Źródło: `istotne_casey/Karol/log_tuya_2026-09-26_odtworzony.txt`. Plik odtworzony z zapisu sesji z 26.09, bo surowego eksportu nie zapisano; pomiary są w nim tylko częściowe. Auto A = dwufazowe (L3 = 0), auto B = trójfazowe.

Tabela obejmuje przerwy, po których wallbox wrócił do stanu 200 (wtyk włożony, gotowość), a nikt od razu nie ingerował:

| Przerwa | Auto | Przyczyna | Co było dalej |
|---|---|---|---|
| 11:50:40 | A | alarm 400 | 200 o 11:51:17, **ładowanie samo o 11:51:21** (4 s) |
| 11:53:41 | A | alarm 400 | 200 o 11:54:36, brak wznowienia przez 56 s, odpięcie |
| 12:01:32 | B | nieustalona (L2 → 0, rekord sesji) | brak wznowienia ok. 2 min, przepinanie 12:03–12:04 |
| 12:05:56 | B | alarm 400 | 200 o 12:06:52, brak wznowienia 5,5 min, włączenie zasilania |
| 12:13:04 | B | **pauza DLB** (12,6 → 10,2 → 5,5 A) | brak wznowienia 2,6 min, odpięcie (dalej auto A) |
| 12:16:24 | A | nieustalona | brak wznowienia 4,5 min, odpięcie |
| 12:22:29 | A | alarm 400 | 200 o 12:22:40, brak wznowienia 97 s, włączenie zasilania |
| 12:24:33 | A | alarm 400 | 200 o 12:25:01, brak wznowienia 28 s, wyłączenie zasilania |
| 12:34:27 | A | alarm 400 | 200 o 12:34:37, **ładowanie samo o 12:34:42** (5 s) |
| 12:37:53 | B | **pauza DLB** (czajnik, problem 2) | brak wznowienia 6,5 min, offline |
| 12:54:34 | B | **pauza DLB** (14,6 → 11 A → pauza) | brak wznowienia 39 s, włączenie zasilania |
| 12:57:52 | B | nieustalona (rekord sesji) | brak wznowienia 50 s, włączenie zasilania |

Pozostałe alarmy (11:51:43, 11:56:18, 11:59:31, 12:26:33, 13:00:13) kończyły się, zanim wallbox wyszedł ze stanu błędu — zasilanie wyłączano po 24–137 s.

**Fakty:**
- Samo wznowiło się 2 z 12 przerw. Oba razy było to auto A po alarmie, 4–5 s po powrocie wallboxa do stanu 200.
- **Auto B nie wznowiło ani razu** — ani po pauzie DLB (3 razy), ani po alarmie, ani po przerwie z nieustalonej przyczyny.
- Auto A po czterech innych przerwach też stało, od 28 s do 4,5 min.

**Wniosek `[Z]`:** mechanizm samoczynnego wznowienia w wallboxie istnieje i auto A potrafi na niego zareagować. Nie działa jednak regularnie. Problem 2 udokumentowano wyłącznie autem B, które po żadnej przerwie nie wznowiło. Z samego logu nie da się więc oddzielić, czy winny jest układ DLB–wallbox, czy auto B — tym bardziej że auto B miało później uszkodzoną ładowarkę pokładową. Rozstrzygnie test pauzy DLB z innym samochodem. Log nie pokazuje sygnału CP ani przydziału z DLB.

**Narastanie prądu po starcie:** auto B ok. 30 s do 13–16 A (pięć sesji: 12:00:41, 12:04:44, 12:12:27, 12:53:48, 12:55:22); auto A ok. 5 s do ok. 9 A.

### 10.1 Opóźnienie wznowienia po pauzie DLB — propozycja do poprawki producenta (2026‑09‑28, niezatwierdzona)

Założenie: stałe opóźnienie T, liczone od chwili, gdy zapas dla wallboxa wynosi co najmniej 6 A, i zerowane, gdy spadnie poniżej. Propozycja:
- T = 3 min;
- pauza dopiero, gdy zapas jest poniżej 6 A przez 2–3 s;
- jeśli po wznowieniu auto nie pobiera prądu przez ok. 60 s — jednorazowa sekwencja budzenia.

Uzasadnienie w odpowiedzi z 28.09; skrót w `DANE_DIAGNOSTYCZNE.md`, sekcja wallbox/DLB. **Do skorygowania po decyzji:** nasza ulotka DLB obiecuje, że ładowanie „wznawia się samo, gdy tylko zrobi się miejsce” (`../wallbox_DLB/AMPERE_POINT_modul_DLB_ulotka_v1`).

*Korekta (2026‑09‑28, po odpowiedzi producenta):* producent liczy opóźnienie **od zatrzymania ładowania**. Po jego upływie wallbox wznawia, gdy tylko prąd wystarczy — bez zerowania zegara i bez sprawdzania stabilności. Propozycja 3 min pozostaje, ale z innym uzasadnieniem (limit najwyżej 20 cykli na godzinę; obciążenia dłuższe niż T nie dokładają opóźnienia). Warunek zerowania zegara odpada, dochodzi zapas przy wznowieniu (np. ≥ 7–8 A). Aktualna wersja analizy: `../DLB_R&D/zasoby_informacji/DLB_RD_baza_wiedzy.md`, sekcja 5. *Korekta (28.09, po południu): po symulacji 7 typów domów i 4 obiektów rekomendacja to **4 min** (raport `../DLB_R&D/AMPERE_POINT_DLB_opoznienie_wznowienia_v1.pdf`).* *Decyzja Dawida (28.09): **5 min** — raport v2.*


---

## 11. Sprawdzenie aktualizacji (2026‑09‑29, 06:41)

Log urządzenia z przestrzeni partnera, Central Europe, okno 23.09 06:41 – 29.09 06:41 (czas lokalny):
- **filtr zdarzeń „OTA” (固件升级): brak danych** — nie było żadnej aktualizacji oprogramowania `[F]`;
- **najnowsze zdarzenie w ogóle: 26.09, 14:26:04 — offline (keepalive_timeout)** `[F]`. Od tego czasu wallbox nie łączył się z chmurą, więc aktualizacja przez Tuya nie mogła do niego dotrzeć. Przyczyna offline (zasilanie, Wi‑Fi, demontaż) — nieznana.

Wersja oprogramowania bez zmian od 26.09: `(V8.0.7)F1.3.6`.

**Potwierdzenie bieżącego stanu (29.09, ok. 09:10):** lista urządzeń produktu (AI Product → Device → Device Details, przestrzeń partnera) pokazuje dla `bfe26d78713489f8a6ulsj` status **Activated | Offline**. Pierwsza aktywacja: 26.09 10:43:39, ostatnia: 26.09 10:48:53. Log pobrany ponownie o 09:09 — nadal żadnego zdarzenia po 26.09 14:26:04 `[F]`.
**Ponowne sprawdzenie (29.09, 10:42):** nadal Activated | Offline, w logu nic po 26.09 14:26:04.
