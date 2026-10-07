# USTALENIA cz.2 — switch, anatomia schematu CP, tor mocy, rola Stateflow vs komparator, katalog sym→HIL
> **Charakter pliku:** drugi addendum do `KONTEKST_zadanie_AMPERE_POINT.md`, kontynuacja `USTALENIA_architektura_3petle_2026-06-16.md`. Kondensuje wnioski z dalszej części sesji **2026-06-16** — głównie doprecyzowania pojęciowe wokół schematu CP i roli Stateflow. Wklej do folderu `AMPERE_POINT`.
>
> **Status:** rozstrzygnięcia koncepcyjne; nie ruszono jeszcze `.tex`/modelu. Spina się z cz.1 (architektura 3 pętli, logika stycznika, dwa schematy).

---

## 0. TL;DR
- **Switch w obwodzie CP = styk wewnątrz auta** (dokłada R3 1,3 kΩ → stan C ~6 V), sterowany `StateC` z karty „Emulator auta". **To NIE stycznik mocy.**
- **Jedyny sygnał między autem a ładowarką to napięcie CP** (+ PWM z powrotem). `StateC`, `veh_cmd`, `duty`, `contactor_cmd` są **wewnętrzne** danej strony — nie przekraczają granicy auto↔ładowarka.
- **Węzeł CP = styk R1 ↔ anoda diody** = fizyczna granica: lewa strona ładowarka (źródło + R1), prawa auto (dioda + R2 + switch/R3). Voltage Sensor mierzy w tym punkcie.
- **Tor mocy: TAK, dodać** — bo licznik kWh i DLB nie mają gdzie zaistnieć na schemacie CP. W symulacji darmowy i bezpieczny; w sprzęcie faza v2.
- **Korekta roli Stateflow:** Stateflow **odgrywa zachowanie** ładowarki i auta (aktorzy), **NIE klasyfikuje usterek**. Klasyfikuje **komparator** (sędzia).
- **Symulacja buduje i waliduje test; hardware go wykonuje.** Usterki realne wychodzą **na sprzęcie**, nie w symulacji (wzorzec jest poprawny z definicji).

---

## 1. Switch — czym jest (doprecyzowanie)
Ideal Switch w Simscape = **emulacja styku wewnątrz samochodu**, nie element ładowarki, nie bezpiecznik.
- Działanie czysto rezystancyjne: samo R2 2,74 kΩ → CP ~9 V (stan B). Switch dokłada równolegle **R3 1,3 kΩ** → 2,74‖1,3 ≈ 0,88 kΩ → CP ~6 V (stan C).
- Sterowany `StateC` (0=B, 1=C) z karty Stateflow „Emulator auta" przez mostek Simulink-PS.
- **Nie mylić ze stycznikiem mocy:** switch siedzi w niskonapięciowej gałęzi sygnałowej i przełącza *poziom napięcia rozmowy*; stycznik siedzi na torze 230/400 V i przełącza *przepływ energii*.

## 2. Skąd `StateC` — pułapka pojęciowa (WAŻNE)
W **rzeczywistości nie ma przewodu „StateC"** ani żadnej komendy auto→ładowarka. Auto **zmienia własną elektronikę** (zamyka swój styk, dokłada rezystor); ładowarka **widzi tylko skutek** — napięcie CP samo spada 9→6 V, bo zmienił się dzielnik. Cała rozmowa idzie jedną żyłą CP, wyłącznie poziomem napięcia.
- `StateC` **nie idzie z obwodu sterującego ładowarki** i **nie jest sygnałem przesyłanym z auta do ładowarki**.
- `StateC` to **wewnętrzna decyzja auta**; w symulacji pochodzi z karty „Emulator auta" (mózg auta), bo to ona jest wcieleniem auta.
- **Reguła do zapamiętania:** auto i ładowarka wymieniają się **tylko** poziomem CP (i PWM z powrotem). Wszystkie inne sygnały (`StateC`, `veh_cmd`, `duty`, `contactor_cmd`, `I_offer`) są **wewnętrzne** jednej ze stron.

## 3. Anatomia schematu CP (element po elemencie)
Schemat **warstwy sygnałowej Control Pilot** — fizycznej „linii rozmowy" auto↔ładowarka. Nic więcej (bez toru mocy, bez stycznika).

| Element | Strona | Rola |
|---|---|---|
| Źródło ±12 V / PWM 1 kHz | ładowarka | nadajnik CP; wypełnienie koduje oferowany prąd |
| **R1 1 kΩ** (szereg.) | ładowarka | „rezystor pilota" = górne ramię dzielnika; bez niego brak dzielnika, twarde +12 V |
| **Dioda** (szereg.) | auto | przepuszcza dodatnią połówkę PWM (dzieloną do 9/6 V), blokuje ujemną (−12 V niedzielona). Asymetria = „jestem autem". **Brak diody = klasyczna usterka.** |
| **R2 2,74 kΩ** | auto | ustawia stan B (~9 V) |
| **Switch + R3 1,3 kΩ** | auto | dokłada się → stan C (~6 V); sterowany `StateC` |
| **Voltage Sensor** (CP↔masa) | pomiar | „oczy" obu maszyn stanów; mierzy w węźle granicznym CP |
| **Solver Configuration + Electrical Reference (masa=PE)** | — | obowiązkowa obsługa obwodu Simscape |

- **Węzeł CP = styk R1 ↔ anoda diody** = granica stron (elektryczny odpowiednik styku w gnieździe Type 2). Lewa = ładowarka+kabel (źródło+R1), prawa = auto (dioda+R2+switch/R3).
- W realu na CP jest jeszcze pojemność kabla itp. — **pomijamy** w modelu, bo do poziomów 9/6 V niepotrzebne. Podział „lewa/ładowarka, prawa/auto, na styku CP" jest poprawny.
- Poziom mierzymy **na CP** (między R1 a diodą) — spadek na diodzie nie psuje wartości (stąd 8,98 / 5,99 V).

## 4. „Rezystor pilota" — co to znaczy
Nazwa **roli, nie typu elementu**. Zwykły rezystor; „pilota", bo pracuje na linii Control **Pilot** po stronie ładowarki, a jego zadaniem jest **stworzyć dzielnik napięcia** z rezystorami auta. R1 = górne ramię (od źródła), rezystory auta = dolne ramię (do masy); poziom CP = ich stosunek. (Rozumienie użytkownika było poprawne.)

## 5. Solver Configuration — czym jest
Blok **obowiązkowy w każdej „wyspie" Simscape** — bez niego model nie ruszy (błąd).
- **Dlaczego potrzebny:** w Simulinku sygnał płynie jednokierunkowo (wejście→wyjście). W Simscape modelujesz fizyczny obwód, gdzie prądy i napięcia są **wzajemnie powiązane** prawami Kirchhoffa — trzeba rozwiązać **układ równań naraz dla całego obwodu** w każdym kroku czasu (napięcie CP zależy od prądów, prądy od napięcia).
- **Co robi:** mówi „tu jest fizyczny obwód, rozwiąż jego równania" i ustawia **algorytm numeryczny** solvera (+ tolerancje/krok). Dla nieliniowej diody rozwiązuje iteracyjnie.
- **Praktyka:** wrzuć jeden blok, podepnij do masy (punkt podłączenia obojętny — liczy się obecność), zapomnij. Analogicznie **Electrical Reference (masa)** — bez punktu odniesienia napięcia są niezdefiniowane.

## 6. Tor mocy — czy dodawać (TAK, z uzasadnieniem)
**Powód konkretny, nie „dla kompletu":** dwa z trzech kluczowych scenariuszy nie mają gdzie zaistnieć na schemacie CP — **weryfikacja licznika kWh** (całka mocy po czasie) i **DLB** (suma prądów vs bezpiecznik) żyją w torze mocy.
- Osobny, niełączący się elektrycznie obwód: **L/N/PE + stycznik + licznik kWh + obciążenie (auto pobierające prąd)**. Spina go z resztą **tylko** `contactor_cmd`.
- Pozwala czysto pokazać logikę stycznika (zamknięcie z pętli 2 + weto bezpieczeństwa pętli 1) i jest miejscem, gdzie modelujemy *zachowanie* zabezpieczeń.
- Dotyka 230/400 V → w sprzęcie faza v2 (izolacja, bezpieczniki). **W symulacji darmowy i bezpieczny** → dodać od razu do schematu i modelu.

## 7. Jak schematy mają się do Stateflow
Dwie warstwy, różne role:
- **Schematy (Simscape) = fizyka** — płyną prądy, ustala się napięcie, dioda blokuje, licznik całkuje.
- **Stateflow = logika decyzyjna („mózgi")** — żadnego rezystora; tylko stany i decyzje „widzę napięcie → robię to".
- Łączą je **mostki** Simulink-PS / PS-Simulink.

**Pętla obiegu sygnału:**
`Emulator auta (SF)` ustawia `StateC`/`veh_cmd` → mostek → switch/R w Simscape → napięcie CP się ustala (fizyka) → Voltage Sensor → mostek → `cp_voltage` → `Złoty wzorzec (SF)` decyduje `duty`/`contactor_cmd` → mostek → źródło PWM + stycznik w Simscape → koło się zamyka.

**Dwie karty Stateflow nie gadają wprost — rozmawiają przez fizyczny węzeł CP** (jak auto z ładowarką jedną żyłą). To czyni z modelu cyfrowy bliźniak, nie sam diagram logiki.

## 8. Rola Stateflow vs komparator — KOREKTA rozumienia
**Stateflow ≠ klasyfikator usterek.** Podział ról (z analogią):
- **Stateflow = aktorzy** — odgrywa zachowanie wzorca EVSE i emulatora auta zgodnie z normą („mam 6 V i brak usterki → zamykam stycznik, podaję 16 A").
- **Sekwencer = reżyser** — prowadzi scenariusz, wstrzykuje usterki.
- **Komparator = sędzia** — porównuje realną odpowiedź z oczekiwaną, liczy odchyłki, klasyfikuje, wystawia pass/fail. **To on diagnozuje, nie Stateflow.**

Architektura **3 pętli** (odruchowa/sterująca/aplikacja) siedzi **wewnątrz karty wzorca** → dzięki tej warstwowości komparator może wskazać **którą pętlę** trafia odchyłka (bezpieczeństwo / sterowanie / aplikacja). Ale to komparator *wskazuje*, Stateflow tylko *odgrywa*.

## 9. Katalog scenariuszy: symulacja buduje, hardware wykonuje (KLUCZ)
**Korekta intuicji „wykrywam usterki na bliźniaku":** wzorzec jest poprawny z definicji → wstrzyknięcie usterki do *niego* daje poprawną reakcję. Więc w symulacji **nie diagnozujesz ładowarki** — **budujesz i kalibrujesz narzędzie testowe** oraz definicję poprawnej reakcji.

**Produkt fazy symulacyjnej = katalog:** lista par **„bodziec → oczekiwana poprawna odpowiedź"** + tolerancja + kryterium pass/fail. Np.: *„«brak diody» → ładowarka MUSI odmówić w T ms; jeśli zamknie stycznik = FAIL"*; *„profil prądu X → licznik w ±1%"*.

**Przejście na HIL — co się zmienia, co zostaje:**
- Emulator auta (SF) → **fizyczny adapter** (MCU + przełączane R/dioda) — *wstrzykuje* usterki w realny kabel (zdejmuje diodę, zwiera CP↔PE, dokłada R3).
- Warstwa CP (Simscape) → **realny kabel + realna ładowarka (DUT)**.
- **Wzorzec + sekwencer + komparator + katalog → zostają w software, bez zmian.**

**Odwrócenie błędnej intuicji użytkownika** („z realnego sprzętu dłużej, bo mniej usterek"):
- W symulacji wzorzec **zawsze przechodzi** (poprawny z definicji) — to oczekiwane, służy do *zbudowania* testów.
- Realna ładowarka (czarna skrzynka) **może oblać** — i **te oblane testy to odkrycia**. Realny sprzęt ma **potencjalnie więcej** usterek, nie mniej.
- Przykładasz **ten sam katalog** do DUT, komparator porównuje realną odpowiedź z wzorcową; rozjazd = twardy wpis do raportu (*scenariusz, odchyłka, o ile, jak odtworzyć*).
- Jest **szybsze**, nie wolniejsze: testy gotowe, zautomatyzowane, powtarzalne → „start", adapter przelatuje listę, pass/fail z liczbami. Nowy firmware → ten sam katalog → wykrywa regresje jednym kliknięciem.

**Jedno zdanie spinające:** schemat = fizyka (Simscape), Stateflow = mózgi aktorów, komparator = sędzia; katalog zbudowany w symulacji przykładasz do realnego sprzętu — i to **na sprzęcie**, nie w symulacji, wychodzą prawdziwe usterki.

---

## 10. Następne kroki (zaktualizowane)
1. (z cz.1) Rozbić złoty wzorzec na 3 zagnieżdżone pętle w `projekt_v3.tex` → v4.
2. **Dorysować schemat toru mocy** (L/N/PE + stycznik + licznik + obciążenie) obok schematu CP — uzasadnienie w §6.
3. (z cz.1) Logika stycznika: permisywne zamknięcie + weto, bramka `AND not(fault)`.
4. **Sekcja „Symulacja buduje test, hardware go wykonuje"** + logika katalogu (§9) — domyka część HIL, mocny punkt na rozmowę.
5. (opcjonalnie) Diagram „warstwa fizyczna (CP+moc) / aktorzy SF / sędzia-komparator" jako TikZ.
6. Tabela „blok symulacji → peryferium MCU → element elektryczny" (most sim↔HIL).
7. Dopiero potem: pełne karty Stateflow (stany/przejścia/sygnały), Faza 2 modelu.

## 11. Zasady pracy (bez zmian)
PL, zwięźle, technicznie, dla kogoś z podstawami elektrotechniki. `.tex`+`.pdf` (xelatex, DejaVu, granatowe nagłówki), wersjonować nie kasować, do folderu `AMPERE_POINT`. `.tex`/skrypty przez shell heredoc + weryfikacja `tail`/balans `\begin`/`\end`. Cel: sposób myślenia + realizowalność → pełna dokumentacja projektowa.
