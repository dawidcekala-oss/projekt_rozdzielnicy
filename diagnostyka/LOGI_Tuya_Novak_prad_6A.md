# LOGI TUYA — sprawa Jiří Novák (harmonogram ustawia 6 A zamiast nastawy)

**Urządzenie:** `bfaeb91d8a8d7c699aevbz` · Q11 przenośna, 16 A, Type 2 · strefa: **Europe/Prague** (GMT+2 latem)
**Product ID:** `3axf0fkgiop0ukhb` · IP 109.71.213.* · MAC 00:33:7a:c8:3c:54 · sygnał −47 dBm
**Źródło:** Tuya Developer Platform, Central Europe, `eu.platform.tuya.com/device/log`
**Pobrano:** 2026‑09‑07 · zakres 1–7.09.2026

> **Uwaga o czasie:** czasy w tym dokumencie podane są **tak, jak zapisuje je log, czyli w UTC**. Czas lokalny klienta = log + 2 h. To samo przesunięcie co w sprawie Marcina.

---

## 1. Zgłoszenie

Klient ustawia w aplikacji 13–14 A, tę samą wartość wpisuje w harmonogramie, a rano ładowanie startuje z prądem 6 A. Na początku działało poprawnie, problem pojawił się po pewnym czasie. Klient pyta, czy przyczyną jest aktualizacja oprogramowania.

Zrzuty potwierdzają rozbieżność: wieczorem faza A pokazuje **12,1 A / 2,746 kW**, rano **5,2 A / 1,232 kW**, przy nastawie w ustawieniach niezmiennie **13 A**.

Harmonogram klienta: **08:00 On, 13 A** oraz **19:00 Off, „undefinedA"**, oba z powtarzaniem **„Jednou" (raz)**.

## 2. Ustalenie rozstrzygające

Zmiany nastawy prądu dzielą się w logu na dwie klasy, które łatwo odróżnić po źródle:

| Czas (log/UTC) | Wartość | Źródło | Temp. | Interpretacja |
|---|---|---|---|---|
| 09‑01 15:59:55 | 13 A | **app client** | 33 ℃ | zmiana klienta |
| 09‑01 15:59:56 | 13 A | device itself | 33 ℃ | potwierdzenie urządzenia |
| **09‑02 06:00:04** | **6 A** | **device itself** | 26 ℃ | **bez udziału aplikacji** |
| 09‑04 10:37:32 | 15 A | **app client** | 26 ℃ | zmiana klienta |
| 09‑04 10:37:34 | 15 A | device itself | 26 ℃ | potwierdzenie |
| 09‑04 14:51:46 | 12 A | **app client** | 32 ℃ | zmiana klienta |
| 09‑07 07:27:51 | 10 A | **device itself** | 25 ℃ | bez aplikacji |
| 09‑07 12:08:43 | 14 A | device itself | 25 ℃ | prawdopodobnie klient po LAN |
| 09‑07 12:15:05 | 12 A | device itself | 25 ℃ | prawdopodobnie klient po LAN |
| **09‑07 12:19:20** | **6 A** | **device itself** | 26 ℃ | **bez udziału aplikacji** |

**Każda zmiana wykonana przez klienta ma parę wpisów: `app client` + `device itself`. Zmiany bez pary pochodzą od samego urządzenia.**

### Kluczowy dowód — 2 września

Wpis **09‑02 06:00:04 UTC** to **08:00:04 czasu lokalnego w Pradze**, czyli **dokładnie godzina wpisu harmonogramu klienta**. W tej sekundzie urządzenie ustawiło nastawę na **6 A**, bez żadnej komendy z aplikacji.

Nastawa nie „wraca" więc do 6 A po restarcie ani nie gubi się w pamięci — **to wpis harmonogramu ustawia 6 A**, mimo że w aplikacji ten sam wpis wyświetla „Změna proudu (A): 13A".

## 3. Prawdopodobna przyczyna: prąd zapisany jako tekst, nie liczba

Porównanie zawartości wpisów harmonogramu z dwóch urządzeń:

| Klient | Zawartość `dps` | Skutek |
|---|---|---|
| Marcin (PL) | `"charge_now",20,true` | prąd **20** jako liczba |
| **Novák (CZ)** | `"charge_now","13",true` | prąd **„13"** jako **łańcuch znaków** |

Wartość prądu u Nováka jest ujęta w cudzysłowy, czyli przekazywana jako tekst. Jeśli sterownik oczekuje liczby, nie zinterpretuje takiego zapisu i **przyjmuje wartość minimalną dopuszczoną przez IEC 61851‑1, czyli 6 A**.

To spójnie tłumaczy wszystkie obserwacje: nastawa główna pozostaje na 13 A, wpis harmonogramu wygląda w aplikacji poprawnie, a mimo to po jego wykonaniu urządzenie ładuje minimalnym prądem.

*Status: hipoteza mocno wsparta, ale niepotwierdzona przez producenta.* Potwierdzeniem byłoby zestawienie kilku urządzeń — jeśli okaże się, że zapis tekstowy występuje w konkretnej wersji aplikacji albo w konkretnej lokalizacji językowej, mamy wadę do zgłoszenia.

## 4. Co zostało wykluczone

**Przegrzanie i ograniczenie termiczne.** W chwili obniżenia prądu 7 września temperatura urządzenia wynosiła **26 ℃**, a 2 września również 26 ℃. Po obniżeniu temperatura **rosła** (26 → 29 → 30 ℃) mimo mniejszego prądu, czyli była skutkiem pracy, nie przyczyną ograniczenia.

Przebieg 7 września w szczegółach:

```
12:15:05  Charge Current Set = 12A
12:15:18  Switch ON · Charger Charging · CP 6V
12:15:43  Total power = 2.61 kW      ← praca przy 12 A
12:17:46  Current temp = 26℃
12:19:20  Charge Current Set = 6A    ← obniżenie, 4 min po starcie
12:19:29  Total power = 1.37 kW      ← moc spada natychmiast
12:24:07  Current temp = 29℃
12:30:28  Current temp = 30℃
```

**Ograniczenie ze strony pojazdu.** Wykluczone — zmienia się sama nastawa urządzenia (`Charge Current Set`), a nie tylko prąd pobierany. Pojazd nie ma jak zmienić nastawy ładowarki.

**Utrata nastawy przy restarcie.** Wykluczone — w badanym tygodniu nie ma zdarzeń restartu, a obniżenia następują w trakcie pracy albo dokładnie o godzinie wpisu harmonogramu.

## 5. Powiązania z innymi sprawami

**U‑023 (Marcin Maj)** — nastawa 16 A wracała do 10 A. Ten sam mechanizm: urządzenie samo zmienia nastawę. Wartość 10 A wskazuje jednak raczej na ograniczenie od czujnika temperatury we wtyku (patrz U‑026), a nie na błąd zapisu wartości.

**U‑026 (Michał Ratusznik)** — rozwarty obwód czujnika temperatury w adapterze daje komunikat i ograniczenie do **10 A**. U Nováka pojawia się **10 A** 7 września o 07:27:51 bez udziału aplikacji — warto zapytać, czy widział wtedy komunikat o przewodzie czujnika.

**Wniosek porządkujący:** urządzenie ma co najmniej dwa mechanizmy samoczynnego obniżania nastawy — ograniczenie zabezpieczające do **10 A** oraz zejście do minimum **6 A** przy wpisie harmonogramu. Nie mylić ich ze sobą.

## 6. Do wyjaśnienia z klientem

Czy 7 września około 14:08–14:19 czasu lokalnego zmieniał nastawy w aplikacji, będąc w tej samej sieci Wi‑Fi co ładowarka. Komendy lokalne nie trafiają do logu chmurowego jako `app client`, więc seria 14 A → 12 A → 6 A może być częściowo jego działaniem.

Czy przy ograniczeniu do 10 A widział komunikat o przewodzie czujnika temperatury.

Czy problem występuje również przy uruchomieniu ręcznym, bez harmonogramu — to rozstrzygnie ostatecznie, czy przyczyna leży wyłącznie we wpisie harmonogramu.
