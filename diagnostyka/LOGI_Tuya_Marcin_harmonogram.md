# LOGI TUYA — sprawa Marcin (harmonogram nie włącza ładowania)

**Urządzenie:** `bf23e52865ef2863f0hnze` · strefa urządzenia wg platformy: **Europe/Warsaw** · Product ID: `fdfjiphjxtc9q…`
**Źródło:** Tuya Developer Platform, Central Europe Data Center, `eu.platform.tuya.com/device/log`, wersja darmowa (7 dni)
**Pobrano:** 2026‑09‑07, konto trzecie (pierwsze dwa nie miały tego urządzenia w projekcie)
**Zakres:** 1–7.09.2026 · 136 zdarzeń po odfiltrowaniu szumu pomiarowego (fazy, temperatura, moc, energia — ok. 24 tys. rekordów)

---

## 1. Ustalenie kluczowe: czasy w logu są przesunięte o 2 h względem harmonogramu

Kolumna w panelu nosi etykietę **Time(GMT+2)**, ale zdarzenia wykonania harmonogramu wypadają **dwie godziny wcześniej**, niż wynika z nastaw widocznych w aplikacji. Po dodaniu 2 h wszystko się układa:

| Wpis harmonogramu (aplikacja) | Zdarzenie w logu | Po dodaniu 2 h | Zgodność |
|---|---|---|---|
| 07:00 — **Off** | 03.09 **05:00:08** Switch = **OFF** | 07:00 | zgadza się co do minuty i co do typu akcji |
| — (start ręczny klienta) | 03.09 11:09:27 Switch = ON, CP 6 V, Charger Charging | 13:09 | klient kliknął o 13:09 lokalnie — dowód rozstrzygający na przesunięcie |
| 13:02 — On | 04.09 11:02:05 oraz 07.09 11:02:06 | 13:02 | co do minuty |
| 19:00 — **Off** | 04.09 **17:00:08** raport Switch | 19:00 | co do minuty |

*Skreślone 2026‑09‑08:* wiersz „22:00 — On · 01.09 20:00:15 · 05.09 20:00:09 + Switch ON" był **błędny**. Zdarzenie 05.09 20:00:09 należy do cyklu szumu tego dnia (13:40:10 + 6 h 20 min = 20:00), a towarzyszący mu `Switch = ON` o 20:00:28 to typowe dla szumu opóźnienie 19 s. Wpis 22:02 nie zostawił w logu żadnego śladu.

**Wniosek roboczy:** przesunięcie dotyczy prezentacji czasu w panelu logów, nie działania urządzenia. Zdarzenia zapisywane są w UTC, a nagłówek kolumny mimo to deklaruje GMT+2. **Przy każdej analizie tych logów dodawać 2 h** (czas letni; zimą +1 h).

*Zastrzeżenie:* ustalenie opiera się na dopasowaniu wzorca, nie na dokumentacji. Jeden przypadek nie pasuje — 04.09 o 17:00:08 (czyli 19:00 lokalnie, gdzie harmonogram ma **Off**) zapisano Switch = **ON**. Do wyjaśnienia; możliwe, że wpisy Off zachowują się inaczej, na co wskazuje też „undefinedA" w ich opisie.

## 2. Harmonogram wykonuje się, ale NIE URUCHAMIA ładowania

**Korekta z 2026‑09‑07:** pierwsza wersja tej sekcji twierdziła, że 3 września harmonogram zadziałał o 13:09. Błąd — serwis ustalił, że **start o 13:09 wykonał klient ręcznie**. To jednocześnie potwierdza przesunięcie czasu z sekcji 1: Marcin kliknął o 13:09 czasu lokalnego, log zapisał 11:09.

Porównanie dwóch sekwencji pokazuje mechanizm usterki.

**Start ręczny** — 3.09, 11:09 w logu (13:09 lokalnie):

```
11:09:27  Switch = ON          (dwa razy)
11:09:30  Work State = Charger Charging
11:09:30  Connection State = Control pilot 6V
```

**Wykonanie wpisu harmonogramu „13:02 On"** — 4.09 o 11:02:05 i 7.09 o 11:02:06, czyli 13:02 lokalnie, co do minuty:

```
11:02:05  Work Mode = Charging now
          (i nic więcej)
```

Brak `Switch = ON`. Brak przejścia w Charger Charging. Brak CP 6 V. **Ładowanie nie rusza.**

Trzeciego września wpis 13:02 nie zostawił nawet tego śladu — został utworzony o 11:18 lokalnie, więc możliwe, że zaczął obowiązywać dopiero następnego dnia. Do potwierdzenia.

### Dowód, że 11:02 to wykonanie wpisu, a nie szum cykliczny

*(uzupełnione 2026‑09‑08 na podstawie surowego logu — wcześniejsza wersja podawała ten ślad bez uzasadnienia, słusznie zakwestionowanego)*

Sekcja 6 opisuje cykliczny raport stanu co ok. 6 h 20 min, którego pierwszym elementem jest właśnie `Work Mode`. Żeby oddzielić jedno od drugiego, wystarczy odtworzyć cykl z danego dnia z raportów `Switch`:

| Dzień | Raporty cyklu (log/UTC) | Odstęp | Zdarzenie o 11:02 |
|---|---|---|---|
| 4.09 | 05:59:22 → 12:19:41 → 18:40:10 | 6 h 20 min | **11:02:05 nie należy do cyklu** |
| 7.09 | 03:41:00 → 10:00:54 | 6 h 20 min | **11:02:06 nie należy do cyklu** |

Cykl tych dni przechodzi obok godziny 11:02. Zdarzenie `Work Mode = Charging now` o 11:02:05 i 11:02:06 jest więc **osobne**, wypada co do sekundy na godzinie wpisu 13:02 lokalnego i występuje wyłącznie w dni robocze. To wykonanie wpisu harmonogramu.

Tą samą metodą widać reakcję na wpisy Off — raporty `Switch` o **05:00:0x** (07:00 lokalnie) 1, 2, 3, 4 i 7 września oraz o **17:00:08** (19:00 lokalnie) 4 września leżą poza cyklem szumu każdego z tych dni.

**Asymetria jest zatem udokumentowana po obu stronach:**

| Wpis | Reakcja urządzenia | Punkt danych |
|---|---|---|
| 07:00 Off, 19:00 Off | raport `Switch` co do sekundy | **rusza `switch`** |
| 13:02 On, 22:02 On | raport `Work Mode = Charging now`, nic poza tym | **rusza tylko tryb** |

W całym tygodniu **nie ma ani jednego `Switch = ON` o 11:02 lub 20:02**. Jedyne włączenia to ręczny start klienta 3.09 o 11:09 oraz raporty cykliczne.

*Osobna obserwacja do wyjaśnienia:* raport o 05:00:0x niesie wartość **ON** we wszystkie dni poza 3 września, kiedy niesie OFF — a tego dnia 20 minut wcześniej urządzenie się zrestartowało. Możliwe, że wpisy Off także skutkują tylko po restarcie. Nie ma to wpływu na diagnozę startu, ale warto o tym pamiętać przy testach.

### Przyczyna: harmonogram i automatyzacja operują na różnych punktach danych

Zawartość wpisu harmonogramu, odczytana ze zdarzeń Timing:

```
"dps":"\"charge_now\",20,true"
```

Wpis ustawia **`charge_now`** (tryb) oraz prąd 20 A. **Nie dotyka `switch`.**

Automatyzacja chmurowa wyłącza natomiast właśnie `switch` — patrz sekcja 4, komenda `Publish Switch = OFF` z 2 września.

Wpisy Off harmonogramu też działają na `switch`: 3 września o 07:00 lokalnie mamy czyste `Switch = OFF` z przejściem w Charger Wait.

**Stąd asymetria, która jest sednem usterki:** wpis wyłączający harmonogramu i automatyzacja przestawiają przełącznik, natomiast wpis włączający harmonogramu ustawia wyłącznie tryb. Po każdym wyłączeniu przełącznik zostaje w pozycji OFF i nic go już nie włącza. Kolejny wpis harmonogramu ustawia poprawny tryb i poprawny prąd, ale przy wyłączonym przełączniku nie ma to żadnego skutku — urządzenie ma podłączony pojazd, właściwe nastawy i po prostu stoi.

**Konsekwencja praktyczna:** przesuwanie godzin startu o kilka minut nie pomoże. Problem nie polega na kolizji czasowej z oknem automatyzacji, tylko na tym, że wpis włączający nie ma czym włączyć.

**Test potwierdzający dla klienta:** po zadziałaniu automatyzacji, a przed godziną startu harmonogramu, sprawdzić stan głównego przełącznika ładowarki w aplikacji. Przełącznik w pozycji wyłączonej potwierdza diagnozę.

**Kierunki obejścia:** przebudować scenę tak, by zamiast `switch` przestawiała tryb pracy; albo dodać automatyzację włączającą przełącznik kilka minut przed startem harmonogramu; albo zrezygnować ze scen i oprzeć się wyłącznie na harmonogramie, skoro ten ma własne wpisy Off.

## 2a. Hipoteza WYKLUCZONA: prąd spoza zakresu urządzenia

*(2026‑09‑08 — zapisane, żeby do tego nie wracać)*

Robocza teoria: wpis On niesie 20 A, wpisy Off nie niosą prądu wcale (w aplikacji „undefinedA"); jeśli 20 A przekracza zakres modelu, sterownik odrzuca całą komendę, a wpis bez prądu nie ma czego odrzucić. Podział działa/nie działa pokrywałby się wtedy z podziałem z prądem/bez prądu.

*Uwaga porządkowa:* zawartość `dps` wpisów **Off** nie jest znana z logu. Zdarzenia Timing zapisały się tylko dla wpisów On, bo tylko te Marcin edytował 3 września. „undefinedA" pochodzi ze zrzutu aplikacji, nie z danych urządzenia.

**Wykluczone: urządzenie klienta to Q74 — 7,4 kW, 1 faza, zakres 6–32 A.** Nastawa 20 A mieści się w zakresie i jest całkowicie poprawna. Potwierdza to zresztą raport stanu z 3.09 o 06:40, gdzie urządzenie podaje `Charge Current Set = 20A` bez żadnego ograniczenia.

Wartość prądu we wpisie **nie jest** przyczyną.

## 3. Edycje harmonogramu widoczne w logu

Zdarzenia typu **Timing**, źródło **app client** — pokazują, że Marcin przestawiał wpisy (czasy poniżej surowe, +2 h dla lokalnego):

| Czas (log) | Operacja | Godzina wpisu |
|---|---|---|
| 03.09 04:52:59 | DELETED → CREATE | 22:00 → 22:02 |
| 03.09 04:53:57 | DELETED → CREATE | 13:00 → 13:01 |
| 03.09 05:00:03 | DELETED → CREATE | 22:02 → 22:00 |
| 03.09 05:00:14 | DELETED → CREATE | 13:01 → 13:00 |
| 03.09 09:18:45 | DELETED → CREATE | 13:00 → **13:02** |
| 03.09 09:18:53 | DELETED → CREATE | 22:00 → **22:02** |

Każdy wpis niesie `dps: "charge_now",20,true` oraz `loops: "0111110"`.

**`loops` to maska dni tygodnia** — siedem pozycji od niedzieli. `0111110` = poniedziałek–piątek, czyli „Robocze" ze zrzutu ekranu. 3 września 2026 to czwartek, więc wpis obowiązywał.

**`dps` zawiera prąd 20 A** — nastawa prądu jest częścią wpisu harmonogramu, nie osobnym ustawieniem. Istotne dla sprawy U‑023 i zgłoszenia Novaka, gdzie prąd wracał do niższej wartości.

## 4. Automatyzacje chmurowe nie wysłały nic

W całym tygodniu **jedno jedyne** zdarzenie ze źródłem `cloud`: 02.09 o 17:02:18 komenda **Publish Switch = OFF**, wykonana 150 ms po tym, jak urządzenie zaraportowało rozpoczęcie ładowania (CP 6 V, Charger Charging). To jest ślad zadziałania automatyzacji — dokładnie ten mechanizm, o którym mowa w zgłoszeniu: scena ubiła ładowanie natychmiast po jego rozpoczęciu.

Poza tym jednym przypadkiem automatyzacje nie odezwały się ani razu. Reszta zdarzeń pochodzi od `device itself` (raporty stanu) albo `app client` (edycje timera, zapytania o stan).

## 5. Restart z powodu zaniku zasilania

**03.09 o 06:40 lokalnie:** `Device restart = power off reboot`, poprzedzone wejściem online i pełnym raportem stanu (Fault = 0, Switch ON, Schedule charging, System version V1, Charge Current Set 20 A, CP 9 V → 6 V). Urządzenie straciło zasilanie i wstało ponownie. Do wyjaśnienia, czy to skutek prac Marcina, czy zdarzenie w instalacji.

## 6. Szum, który łatwo wziąć za zdarzenia

Co około **6 h 20 min** urządzenie wysyła komplet raportów stanu — najpierw `Work Mode = Charging now`, po 18–19 s `Switch = ON/OFF`. Widać to jako regularne serie (np. 03.09 04:40, 11:09, 17:19, 23:39). **To nie są komendy**, tylko cykliczne odświeżenie punktów danych. Przy czytaniu logów odróżniać je po tym, że nie towarzyszy im zmiana Work State ani Connection State.

Stany CP w logu: **12 V** = brak pojazdu, **9 V** = pojazd podłączony, **6 V** = ładowanie w toku.

---

## Wnioski dla sprawy

Harmonogram **wykonuje się** o właściwych godzinach — potwierdzone analizą cyklu raportów (sekcja 2, „Dowód"). Wpis włączający ustawia jednak wyłącznie **tryb pracy** (`Work Mode = Charging now`) i nie dotyka **przełącznika** (`switch`). Wpisy wyłączające oraz automatyzacja chmurowa działają odwrotnie — ruszają właśnie przełącznik.

Skutek: po każdym wyłączeniu przełącznik zostaje w pozycji OFF, a kolejny wpis włączający nie ma czym włączyć. Urządzenie ma podłączony pojazd, właściwy tryb i właściwy prąd — i stoi.

Jedyne potwierdzone zadziałanie automatyzacji w całym tygodniu: 02.09 o 17:02:18 `Publish Switch = OFF` ze źródła `cloud`, 150 ms po rozpoczęciu ładowania. To ta komenda zostawiła przełącznik w OFF.

**Dlaczego u serwisu ten sam układ działa:** jeżeli przełącznik pozostaje włączony, `Work Mode = Charging now` wystarcza do startu. Różnicą nie jest konfiguracja harmonogramu, tylko to, czy coś wcześniej przestawiło przełącznik.

**Test rozstrzygający dla klienta (jedno spojrzenie w aplikację):** przed godziną 13:02 sprawdzić stan głównego przełącznika ładowarki. Przełącznik wyłączony potwierdza diagnozę. Włączenie go ręcznie powinno sprawić, że wpis o 13:02 wystartuje.

**Obejście:** przebudować automatyzację tak, by zamiast `Switch : OFF` ograniczała prąd do minimum (6 A) — wtedy przełącznik nigdy nie schodzi w OFF. Wariant alternatywny: druga automatyzacja ustawiająca `Switch : ON` kilka minut przed godziną startu; jej zadaniem nie jest uruchomienie ładowania (`Switch : ON` tego nie potrafi — sprawdzone na `timer_test`), tylko przywrócenie przełącznika, żeby wpis harmonogramu miał co uruchomić.

Kandydat do zgłoszenia producentowi razem ze sprawą Nováka — wspólny mianownik to obsługa wpisów harmonogramu.

## Jak powtórzyć pobranie

Endpoint używany przez panel: `POST /micro-app/device/api/deviceAllEventLog`, ciało `{"query":{"devId":"…","startTime":<ms>,"endTime":<ms>,"size":2000,"queryType":1}}`, wymagany nagłówek `csrf-token` z ciasteczka o tej samej nazwie oraz `X-Requested-With: XMLHttpRequest`. Paginacja przez `nextPageStartRowKey` w praktyce zwracała tę samą stronę — pewniejsze jest dzielenie zapytań na kilkugodzinne przedziały.
