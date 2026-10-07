# LOGI TUYA — `timer_test`: czym jest `switch` (rozstrzygnięcie)

**Urządzenie:** `bfa1efdb234e79915f6sfs` · timer_test · Europe/Warsaw · MAC bc:35:1e:51:19:0e · sygnał −65 dBm
**Źródło:** Tuya Developer Platform, Central Europe, `eu.platform.tuya.com/device/log`
**Pobrano:** 2026‑09‑09, konto Dawida (projekt AmperePoint HA)
**Zakres analizy:** 2026‑09‑09, 08:20–09:10 UTC (10:20–11:10 czasu lokalnego) — okno testów automatyzacji

> **Czas w logu jest w UTC.** Lokalny = log + 2 h (lato). To samo przesunięcie co w sprawach Marcina i Nováka.

---

## 1. Rozstrzygnięcie: `Switch : ON` URUCHAMIA ładowanie

Wcześniejsza teza — powtórzona w obu poradnikach i w `DANE_DIAGNOSTYCZNE.md` — mówiła, że `switch` potrafi tylko zatrzymać sesję, a nie ją rozpocząć. **Teza jest fałszywa.** Log pokazuje trzy niezależne przypadki, w których komenda `Switch = ON` wysłana **z chmury** uruchomiła ładowanie:

```
08:54:00.699  Publish  Switch = ON            cloud
08:54:00.958  Report   Switch = ON            device itself
08:54:01.587  Report   Work State = Charger Charging     ← 0,9 s od komendy

08:55:00.673  Publish  Switch = ON            cloud
08:55:00.884  Report   Switch = ON            device itself
08:55:01.861  Report   Work State = Charger Charging     ← 1,2 s od komendy

09:00:14.703  Publish  Switch = ON            cloud
09:00:14.994  Report   Switch = ON            device itself
09:00:15.516  Report   Work State = Charger Charging     ← 0,8 s od komendy
```

Za każdym razem urządzenie było przed komendą w stanie **Charger Wait** z przełącznikiem w OFF. Komenda chmurowa przechodzi, urządzenie ją potwierdza i w ciągu sekundy wchodzi w ładowanie.

**`switch` to pełny start/stop sesji, nie „zezwolenie na ładowanie".**

## 2. Dlaczego wyglądało to na „nie działa"

Sesja jest natychmiast ubijana przez własną automatyzację `do_not_charge` (*If Work State : Charger Charging → Then Switch : OFF*):

```
08:54:01.587  Work State = Charger Charging
08:54:01.981  Publish  Switch = ON     cloud   ← if_charging_switch_on
08:54:02.025  Publish  Switch = OFF    cloud   ← do_not_charge  (44 ms później)
08:54:02.370  Switch = OFF
08:54:03.770  Work State = Charger Wait
```

**Ładowanie trwa około 1,4 sekundy** — za krótko, żeby zobaczyć je w aplikacji albo na ekranie urządzenia. Dlatego obserwacja „prąd się zmienia, tryb się zgadza, ale ładowanie nie rusza" była myląca: ono ruszało i było zabijane, zanim cokolwiek zdążyło się wyświetlić.

**Obie sceny reagują na to samo zdarzenie.** `if_charging_switch_on` i `do_not_charge` mają identyczny warunek (`Work State : Charger Charging`), więc odpalają się równocześnie — 44 ms od siebie. Wygrywa ta, która wysyła OFF, bo jest ostatnia.

## 3. Harmonogram też działa — i też jest ubijany

O 08:57 urządzenie wystartowało ładowanie **samo**, bez udziału chmury:

```
08:57:16.630  Report   Work Mode = Charging now   device itself  ┐ ta sama
08:57:16.630  Report   Switch = ON                device itself  ┘ milisekunda
08:57:16.635  Report   Work State = Charger Charging             ← 5 ms
08:57:16.927  Publish  Switch = OFF               cloud          ← do_not_charge
08:57:18.131  Report   Switch = OFF
08:57:18.994  Report   Work State = Charger Wait

08:57:21.253  Report   Work Mode = Charging now   device itself  ┐ druga próba
08:57:21.253  Report   Switch = ON                device itself  ┘
08:57:21.257  Report   Work State = Charger Charging
08:57:21.526  Publish  Switch = OFF               cloud
08:57:23.460  Report   Work State = Charger Wait
```

To jest wykonanie wpisu harmonogramu: `Work Mode` i `Switch` przychodzą w tej samej milisekundzie, jako jedna komenda o kształcie `"charge_now",<prąd>,true`. Urządzenie wchodzi w ładowanie po 5 ms. Automatyzacja gasi je po 300 ms i próbuje ponownie 5 sekund później — z tym samym skutkiem.

**Wniosek: harmonogram na `timer_test` działa poprawnie.** Objaw „harmonogram nie startuje ładowania" powstaje wyłącznie z powodu aktywnej sceny wyłączającej.

## 4. `enable_charging` nie zablokowało `do_not_charge`

Scena `enable_charging` (*If Switch : OFF lub Work State : Charger Inserted → Then do_not_charge : Automation Disable*) miała wyłączyć scenę gaszącą. W logu widać, że **nie zdążyła albo nie zadziałała** — `do_not_charge` wysyła `Switch = OFF` również po 09:00.

Przyczyna do sprawdzenia: warunek `Switch : OFF` jest spełniony dopiero **po** zgaszeniu sesji, czyli za późno; a `Charger Inserted` w tym oknie w ogóle nie wystąpił — urządzenie przechodziło Charger Wait ↔ Charger Charging, nigdy przez Charger Inserted.

## 4a. `switch` a `Work Mode` — na czym polega różnica

*(ustalone 2026‑09‑10 na sekwencji z przepięciem testera; czasy lokalne)*

`Work Mode` to **nastawa trwała** — w jakim trybie urządzenie ma pracować, gdy zaistnieją warunki do ładowania. `switch` to **wyzwalacz sesji** — ładuj teraz. Oba mogą pojawić się w logu razem, ale znaczą co innego i pochodzą z różnych źródeł.

Sekwencja przepięcia testera:

```
10:25:53.893  Work State = Charger Free
10:25:53.994  CP 12 V                         ← odpięcie
10:25:55.881  Work State = Charger Wait
10:25:55.888  Switch = ON                     ← urządzenie SAMO przywraca przełącznik
10:25:56.009  CP 9 V                          ← wpięcie
10:25:57.828  Work Mode = Charging now  ┐ raport stanu po starcie,
10:25:57.828  Switch = ON               ┘ nie komenda
10:25:57.855  Work State = Charger Charging
10:25:58.162  CP 6 V
```

Sesja ruszyła **od wpięcia**, nie od żadnej komendy. Urządzenie miało tryb `Charging now`, samo ustawiło `switch` na ON po wykryciu pojazdu i rozpoczęło ładowanie. Para `Work Mode` + `Switch` w tej samej milisekundzie to **raport o stanie po zmianie**, a nie polecenie — to samo widać przy wykonaniu wpisu harmonogramu.

**Ustalenie uboczne, istotne dla reklamacji:** odpięcie i ponowne wpięcie pojazdu **samo przywraca `switch` na ON**, niezależnie od tego, że wcześniej wyłączyła go automatyzacja (10:25:55.888). Dlatego klient, który wypnie i wepnie wtyczkę, zawsze uruchomi ładowanie — i dlatego objaw bywa nieregularny.

Dla porównania start z komendy chmurowej, trzy minuty później:

```
10:29:00.347  Publish  Charge Current Set = 16A   cloud
10:29:00.355  Publish  Switch = ON                cloud
10:29:00.742  Report   Switch = ON
10:29:01.155  Work State = Charger Charging       ← 0,8 s
```

**Nie ma tu żadnego raportu `Work Mode`** — bo tryb był już `Charging now` i się nie zmienił. Tuya nie generuje zdarzenia dla wartości, która pozostaje bez zmian. To jest sedno różnicy: wpis harmonogramu ustawia tryb, który zwykle **już jest ustawiony**, więc nie robi nic; scena rusza przełącznik, który realnie stoi w OFF, więc robi wszystko.

## 5. Co z tego wynika dla sprawy Marcina

U Marcina wpis harmonogramu o 13:02 zostawia w logu **wyłącznie `Work Mode = Charging now`**, bez towarzyszącego `Switch = ON` w tej samej milisekundzie. Tutaj, na sprawnym układzie, oba punkty przychodzą razem. **To jest realna różnica między jego urządzeniem a naszym** — i teraz wiadomo, czego szukać: nie tego, czy `switch` potrafi włączyć, tylko dlaczego jego wpis nie niesie `switch`.

Możliwy trop: jego wpisy On były wielokrotnie kasowane i tworzone od nowa 3 września (sześć operacji DELETED→CREATE w ciągu 26 minut). Wpis mógł zapisać się niekompletnie.

## 6. Poprawki do wprowadzenia w materiałach

| Miejsce | Co jest napisane | Stan faktyczny |
|---|---|---|
| `AMPERE_POINT_charging_current_automation_v1.tex`, krok 9 | „Do not select Switch — on this charger the switch cannot start charging, only stop it" | **nieprawda** — `Switch : ON` startuje sesję |
| tamże, ramka „One thing to avoid" | „Do not add Switch : ON as a second action. On this charger that command has no effect on starting a session" | **nieprawda** |
| `DANE_DIAGNOSTYCZNE.md`, tabela DP | „`charge_now` / `Work Mode` — sam nie uruchamia ładowania" | zostaje w mocy, ale start następuje, gdy `Work Mode` i `switch` przyjdą **razem** |
| `LOGI_Tuya_Marcin_harmonogram.md`, sekcja 2 | asymetria „wpis On rusza tylko tryb" | zostaje — dotyczy urządzenia Marcina, nie mechanizmu jako takiego |

## 7. Jak powtórzyć pobranie

Zapytanie wykonane z konsoli przeglądarki na zalogowanym panelu:

```js
const csrf = document.cookie.split('; ').find(c=>c.startsWith('csrf-token=')).split('=')[1];
const r = await fetch('/micro-app/device/api/deviceAllEventLog', {
  method:'POST',
  headers:{'Content-Type':'application/json','csrf-token':csrf,'X-Requested-With':'XMLHttpRequest'},
  body: JSON.stringify({query:{devId:'<DEVICE_ID>',startTime:<ms>,endTime:<ms>,size:2000,queryType:1}})
});
(await r.json()).result.datas;
```

Pola rekordu: `eventTimeStr` (UTC), `eventType` (`Report` / `Publish` / `Timing` / `Online` / `Offline` / `Device restart`), `eventName` (nazwa punktu danych), `eventDetail` (wartość), `requestFrom` (`device itself` / `cloud` / `app client`).

Szum do odfiltrowania: `Current temp`, `Phase A/B/C`, `Total power`, `Total Forward Energy`, `Device semaphore`, `Device Signal Detection`.
