# Adam Gumkowski — Q11 nie rozpoczyna ładowania BYD Atto 2 (auto nie blokuje wtyku)

**Kanał:** e‑mail (hello@, ticket) · **Od:** 2026‑10‑05 · **Stan:** otwarta — u nas ładuje normalnie; **ładowarkę odsyłamy** (decyzja Dawida 07.10, zmiana wcześniejszego „nie odsyłamy na razie”), wsparcie klienta trwa
**Materiały:** `korespondencja\` — reklamacja (05.10), pytanie o auto i odpowiedź (06.10).

`[F]` fakt · `[Z]` założenie

---

## Stan i następny krok (2026‑10‑07)

Ładowarka klienta u nas ładuje samochód normalnie `[F — Dawid]`. Nie odsyłamy, dopóki nie znajdziemy przyczyny. Szkic maila z prośbą o informacje niżej.

~~Trop: rezystancja PP–PE we wtyku~~ — **odpada** (Dawid 07.10): zmierzona u nas, w porządku; poza tym przy złej wartości nasze auto też by nie ładowało. `[F]`

Zadanie od Dawida (07.10): zgłębić, dlaczego u klienta ładowarka fabryczna ładuje auto, a nasza nie.

## Przebieg

| Data | Kto | Co |
|---|---|---|
| 05.10.2026 11:14 | klient | Reklamacja: AmperePoint Q11, 11 kW, Type 2. Uruchamia się po podłączeniu do zasilania; po podłączeniu do auta ładowanie się nie zaczyna; **samochód nie blokuje gniazda ładowania**; ponowne podłączenie nie pomaga. Ten sam samochód ładuje się z fabryczną ładowarką. Prosi o naprawę lub wymianę, proces zwrotu i adres serwisu. `[F — zrzut 01]` |
| 06.10 16:14 | Dawid | Pytanie o markę samochodu. `[F — zrzut 02]` |
| 06.10 16:46 | klient | **BYD Atto 2 Boost, 2025**; wcześniej z tą ładowarką nie było problemu — „coś ewidentnie się zepsuło”. `[F — zrzut 02]` |
| do 07.10 | serwis | Ładowarka u nas ładuje auto normalnie. Nie odsyłamy na razie, próbujemy rozwiązać problem. `[F — Dawid]` |
| 07.10 | Dawid | Zmiana decyzji: ładowarkę odsyłamy, skoro działa; próba wsparcia klienta zostaje. |

## Analiza: co mówi to, że ładowarka fabryczna ładuje (2026‑10‑07)

**Co ten test sprawdza** `[Z — rodzaj ładowarki fabrycznej niepotwierdzony]`: ładowarka dawana z autem to zwykle przenośna, jednofazowa, z gniazda domowego, o małym prądzie. Jej działanie dowodzi, że sprawne są gniazdo ładowania w aucie, rozpoznawanie wtyku i sygnału sterującego po stronie auta oraz że auto ładuje się **jednofazowo**.

**Czego nie sprawdza:**
1. **Gniazda, z którego zasilana jest Q11** — trójfazowe, najpewniej inny obwód niż gniazdo dla ładowarki fabrycznej. Jeśli Q11 wykryje tam problem z zasilaniem (brak fazy, zła wartość napięcia, błąd uziemienia — por. U‑028 i sprawa R. Glocha), nie rozpocznie ładowania i pokaże komunikat na ekranie.
2. **Ładowania trójfazowego w aucie** — BYD Atto 2 ma ładowarkę pokładową 11 kW trójfazową; ładowarka fabryczna używa jednej fazy. Usterka trójfazowej części ładowarki pokładowej nie przeszkadza w ładowaniu jednofazowym.
3. **Reakcji auta na sygnał Q11 po ewentualnej aktualizacji oprogramowania auta** — „wcześniej działało” wskazuje, że coś się zmieniło: gniazdo, auto albo ładowarka.

**„Auto nie blokuje wtyku”** — nie wiemy, kiedy BYD Atto 2 blokuje wtyk (od razu po włożeniu czy dopiero przy starcie ładowania), więc to nie wskazuje etapu, na którym coś zawodzi. Rozstrzyga **to, co pokazywał ekran Q11** po podłączeniu auta: komunikat o zasilaniu → gniazdo/instalacja; „auto podłączone / oczekiwanie” bez startu → po stronie auta.

*Korekta (07.10, Dawid): „auto nie blokuje wtyku” = ładowarka nie przechodzi w żaden inny stan, bo **rezystory w aucie się nie załączają** — ładowarka cały czas widzi brak auta i stoi w gotowości („ready to charge”); ekran niewiele powie. Awaria jest więc **przed pierwszą zmianą stanu**, zanim popłynie prąd — gniazdo zasilające i trójfazowa część ładowarki pokładowej nie mają tu znaczenia (przy problemie z zasilaniem Q11 pokazałaby komunikat, nie gotowość). Kandydaci 1 i 2 poniżej odpadają.* **Zostają:** auto nie uznaje wtyku za podłączony (wykrycie wtyku / wybudzenie — pasuje aktualizacja oprogramowania auta) albo **mechaniczny styk wtyku Q11 w gnieździe tego auta** (styk PP lub CP cofnięty, zgięty, zabrudzony — rezystancja dobra, a w naszym aucie łapie). Przed wysyłką warto obejrzeć i sfotografować czoło wtyku.

~~**Kandydaci (od najbardziej prawdopodobnego):** (1) gniazdo trójfazowe / instalacja u klienta — pasuje do „działało, coś się zmieniło” i do tego, że fabryczna działa z innego gniazda; (2) trójfazowa część ładowarki pokładowej albo oprogramowanie auta — rozstrzygnie ładowanie na publicznej stacji AC (zwykle trójfazowej); (3) przerywana usterka naszej ładowarki — najmniej prawdopodobne po teście u nas.~~

**Log Tuya** — jeśli ładowarka była w aplikacji klienta, log z dnia awarii pokazałby stan sygnału sterującego (12/9/6 V — czy auto w ogóle zostało wykryte), stan pracy i kod usterki. Okno 7 dni → do ok. 12.10. Potrzebny Virtual ID z aplikacji klienta albo znalezienie urządzenia na liście produktu.

**Możliwe przyczyny przy awarii przed pierwszą zmianą stanu (po uwadze Dawida „tylko jedna przyczyna?”, 07.10)** `[Z]`:
- **zmiana po stronie auta:** aktualizacja oprogramowania, ustawienia ładowania (np. tryb oddawania energii, harmonogram — czy blokują już na tym etapie, niepewne) → pytanie do klienta;
- **przebieg w czasie:** nagle (zdarzenie: aktualizacja, upadek wtyczki) vs sporadycznie, potem stale (zużycie lub zabrudzenie styków — wtyku albo gniazda w aucie) → pytanie do klienta;
- **mechaniczny styk wtyku Q11** w gnieździe tego auta (styki cofnięte, zgięte, zabrudzone, zawilgocone) → oględziny u nas przed wysyłką;
- **gniazdo w aucie** (zabrudzony lub uszkodzony styk, który z wtykiem fabrycznym jeszcze łapie, a z naszym nie — inna geometria) → widać na nagraniu/zdjęciach, nie pytamy wprost;
- odpadają: gniazdo zasilające, ładowanie trójfazowe, rezystancja wtyku (zmierzona).

## Szkic odpowiedzi (2026‑10‑07, wersja 6)

*Uwaga Dawida: „sama aktualizacja oprogramowania? tylko jedna przyczyna?” → pytanie ogólniej: czy problem pojawił się nagle czy narastał, co zmieniło się w aucie (aktualizacja, ustawienia ładowania).*

> Dzień dobry Panie Adamie,
>
> Dziękuję za informację. Ładowarkę sprawdziliśmy u nas i ładuje samochód poprawnie, dlatego odsyłamy ją do Pana. Skoro wcześniej ładowanie działało, prosimy o informację, czy problem pojawił się nagle, czy wcześniej zdarzał się sporadycznie, oraz czy przed jego wystąpieniem coś się zmieniło w samochodzie, na przykład aktualizacja oprogramowania albo ustawienia ładowania. Jeśli po otrzymaniu ładowarki problem się powtórzy, prosimy o udokumentowanie, co dzieje się na ładowarce i w samochodzie po podłączeniu, najlepiej krótkim nagraniem albo zdjęciami ekranu ładowarki i ekranu samochodu.
>
> Pozdrawiam,
> Dawid Cekała
> Ampere Point

## Otwarte

- Odpowiedź klienta (nagle czy narastająco; zmiany w aucie: aktualizacja, ustawienia ładowania; nagranie/zdjęcia przy powtórce).
- Oględziny czoła wtyku Q11 przed wysyłką (styki PP i CP).
- ~~Pomiary PP–PE~~ (w porządku); różnica ładowarka fabryczna ↔ Q11 u klienta — analiza.
- Którym samochodem testowaliśmy u nas (do zapisu).
