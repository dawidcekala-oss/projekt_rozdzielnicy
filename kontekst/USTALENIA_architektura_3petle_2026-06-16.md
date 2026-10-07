# USTALENIA — architektura sterowania, stycznik, schematy, mapowanie sim↔HIL
> **Charakter pliku:** addendum do `KONTEKST_zadanie_AMPERE_POINT.md`. Kondensuje wnioski z sesji **2026-06-16** dot. architektury złotego wzorca i jego odwzorowania na realny test. Wklej do folderu `AMPERE_POINT`, żeby nowa rozmowa płynnie kontynuowała.
>
> **Status:** rozstrzygnięcia koncepcyjne (nie ruszono jeszcze plików `.tex`/modelu). **Do zrobienia:** wprowadzić te ustalenia do `AMPERE_POINT_projekt_v3.tex` → wersja v4 i do modelu Stateflow.

---

## 0. TL;DR (jedno spojrzenie)
- Wnętrze ładowarki (DUT **i** złotego wzorca) ma **3 zagnieżdżone pętle**: odruchowa (bezpieczeństwo) ⊂ sterująca (IEC 61851 + DLB) ⊂ aplikacja (Tuya/RFID/licznik/harmonogram). To standard firmware EVSE, nie żargon firmy — i pokrywa się z tym, co Dawid usłyszał na rozmowie.
- **Stycznik jest jeden**, ale dwie pętle mają nad nim władzę o różnym charakterze: **pętla 2 załącza/wyłącza w normalnej pracy**, **pętla 1 ma nadrzędne weto (awaryjne odcięcie)**.
- **Dwa osobne schematy elektryczne:** sygnałowy CP (mamy, Faza 1) i tor mocy (stycznik + licznik + obciążenie, odłożony). Nie łączą się elektrycznie — łączy je tylko sygnał `contactor_cmd`.
- **Stateflow = logika decyzyjna kontrolerów** (model behawioralny normy), **nie** firmware i **nie** elektronika. Fizyka żyje w Simscape; granicę przekraczają bloki-mostki PS.
- **Symulacja = specyfikacja adaptera HIL.** Każdy blok-mostek w modelu ma fizyczny odpowiednik (peryferium MCU + układ pośredniczący) w realnym teście.

---

## 1. Architektura 3 pętli (wnętrze ładowarki = wnętrze złotego wzorca)

**Pętla 1 — odruchowa / bezpieczeństwo (ms, często sprzęt/dedykowany MCU).**
Front-end CP (generacja ±12 V/PWM, odczyt poziomu), sterowanie stycznikiem na poziomie wykonawczym, **zabezpieczenia: RCD typ A 30 mA + detekcja 6 mA DC, monitoring PE, wykrycie sklejonego stycznika, nadprąd/przegrzanie.** Działa odruchowo — usterka (CP w E/F, upływ RCD) → stycznik otwarty natychmiast, niezależnie od warstw wyższych.

**Pętla 2 — sterująca (dziesiątki ms…s).**
FSM handshake A→B→C→D, decyzja o wypełnieniu PWM (= oferowany prąd), zarządzanie sesją, **DLB do 4 stacji**. Wydaje polecenia w dół („zamknij stycznik", „ustaw duty"), raportuje stan w górę. To „mózg sterowania".

**Pętla 3 — aplikacja (miękki/zerowy real-time).**
WiFi + Tuya, RFID, OTA, **niezerowalny licznik kWh** (filar rozliczeń flotowych), harmonogramy, konfiguracja DLB, UI. Ustawia **polityki/nastawy** dla pętli 2 (autoryzacja, limity, okna czasowe); sama nie dotyka stycznika.

Kaskada: odruch ⟶ sterowanie ⟶ aplikacja. Wyższa warstwa zadaje cele niższej; niższa (1) może zawsze przebić wyższe w imię bezpieczeństwa.

---

## 2. Logika stycznika — permisywne zamknięcie + nadrzędne odcięcie (WAŻNE)

Stycznik fizycznie jeden; **asymetria uprawnień**, nie sprzeczność:
- **Pętla 2** załącza i wyłącza w **normalnej** pracy (B→C OK → `contactor_cmd=1`; koniec sesji / auto odpięte → otwiera).
- **Pętla 1** ma **prawo weta** — rozwiera stycznik niezależnie od pętli 2 (RCD, stan E/F, sklejony styk, nadprąd). Otwarcie z pętli 1 jest nadrzędne i zwykle sprzętowe (przerywa obwód cewki niezależnie od MCU).

Reguła:
```
stycznik_zamknięty = (pętla 2 każe zamknąć) AND (pętla 1 NIE zgłasza usterki)
```
Tylko pętla 2 *załącza* moc i tylko gdy pętla 1 *pozwala*. *Otworzyć* może każda; otwarcie z pętli 1 wygrywa.

**Model (Simscape/Stateflow):** Ideal Switch na torze mocy sterowany bramką
`switch_close = contactor_cmd_pętla2 AND not(fault_pętla1)`.
W Stateflow: warstwa odruchowa **wymusza** (nadpisuje) otwarcie; warstwa sterująca tylko *prosi* o zamknięcie.

**Diagnostyka (klucz dla raportu):**
- stycznik **nie** otwiera się na usterkę, gdy powinien → defekt **pętli 1** (bezpieczeństwo);
- zły prąd / złe duty przy zamkniętym styczniku → defekt **pętli 2** (sterowanie);
- przekłamanie kWh → defekt **pętli 3** (aplikacja).

> **Korekta wobec wcześniejszych notatek:** „sterowanie stycznikiem" było skrótowo wrzucone do pętli 1 — poprawnie **normalne sterowanie = pętla 2**, a pętla 1 trzyma awaryjne odcięcie.

---

## 3. Dwa schematy elektryczne (rozdzielić w dokumentacji)

**Schemat sygnałowy CP (mamy — Faza 1, zweryfikowany w Pythonie).**
R1 1 kΩ (ładowarka) ↔ węzeł CP ↔ dioda ↔ R2 2,74 kΩ ↔ masa; gałąź R3 1,3 kΩ + switch (stan C); Voltage Sensor na CP↔PE. Niskie napięcie, bezpieczne. Poziomy: A +12 V, B ~9 V (8,98), C ~6 V (5,99), dół PWM −12 V.

**Schemat toru mocy (odłożony — dotyka 230/400 V).**
L/N/PE, **stycznik**, **licznik kWh**, obciążenie (auto). Tu mieszka stycznik — **nie** na schemacie CP. Oba obwody **nie łączą się elektrycznie**; spina je tylko sygnał `contactor_cmd` (pętla 2 → stycznik) z wetem pętli 1.

**Co to za schemat:** CP = front-end CP ładowarki ↔ sieć rezystorowa po stronie auta ↔ pomiar (Voltage Sensor w sym / ADC-timer w HIL). Interfejs **sygnałowy**, nie mocowy.

**Elementy bezpieczeństwa a schemat:** RCD/PE/detekcja sklejenia są **wewnątrz DUT (czarna skrzynka)** — nie rysujemy ich jako własnych. Na schemacie CP jedyne „okołobezpieczeństwowe" byty to **dioda** (jej brak = usterka, ładowarka ma odmówić) i punkt **zwarcia CP→PE** (wstrzyknięcie stanu E) — to *nasze bodźce testowe*, nie zabezpieczenia ładowarki. W złotym wzorcu modelujemy *zachowanie* zabezpieczeń (stycznik + uproszczony model odcięcia na torze mocy). W teście realnym sprawdzamy je *od zewnątrz* (czy stycznik się otworzył; opcjonalnie izolowany detektor zamknięcia).

---

## 4. Czym jest Stateflow (i czym nie jest)

**Stateflow = logika decyzyjna kontrolerów** („jaką decyzję podejmuje sterownik, gdy widzi taki sygnał"). Model **behawioralny** poprawnego zachowania wg IEC 61851 — **nie** kopia zamkniętego firmware (kodu nie mamy), **nie** elektronika.

Mapowanie pętli na narzędzia (nie wszystko jest w Stateflow):
- **Pętla 2** — w całości Stateflow (FSM, duty, DLB).
- **Pętla 1** — *rozkrok*: decyzja „otwórz na usterkę" w Stateflow, ale front-end CP i sam stycznik w Simscape.
- **Pętla 3** — Stateflow/Simulink/skrypt; wchodzi jako nastawy/flagi do pętli 2.

Dwie karty Stateflow dogadują się **przez fizyczny węzeł CP** (Simscape w środku jako „kabel"), nie sygnałowo na sztywno — to czyni model wiernym cyfrowym bliźniakiem:
- **Emulator auta:** stany `A_Unplugged`→`B_Connected`→`C_Ready`(+`Fault`); wyjścia `veh_cmd` (co wpiąć), `i_demand`. Pasywny elektrycznie — wybiera rezystory/diodę.
- **Złoty wzorzec EVSE:** wejście `cp_voltage` → stan; wyjścia `duty`, `I_offer`, `contactor_cmd`. Wewnątrz: 3 zagnieżdżone pętle (§1).

---

## 5. Jak kontrolery łączą się z elektryką (3 światy)

**Realna ładowarka (DUT):** między logiką a mocą zawsze stoi **driver/front-end** — MCU nie steruje cewką ani nie czyta ±12 V wprost.
- CP: timer→PWM→op-amp/komparator do ±12 V (nadajnik); dzielnik+clamp→ADC (odbiór).
- Stycznik: GPIO→driver→cewka; styk pomocniczy→GPIO (sklejenie).
- Zabezpieczenia: RCD ma sprzętową linię wyzwalającą wprost w cewkę + IRQ do MCU.
- Licznik: SPI/UART lub wyjście impulsowe.

**Symulacja:** „połączeniem" są **bloki-mostki** (= cyfrowe drivery/front-endy):
- `duty` → Pulse Generator → **Simulink-PS** → Controlled Voltage Source (CP).
- Voltage Sensor → **PS-Simulink** → `cp_voltage`.
- `contactor_cmd` → mostek → Ideal Switch (tor mocy).

**Adapter HIL (nasz sprzęt):** MCU (ESP32/STM32) ↔ linie CP/PP gniazda Type 2:
- CP: dzielnik+clamp+offset→input-capture (odczyt PWM ładowarki); przełączane R (przekaźnik/MOSFET)+dioda→ściąganie do 9/6 V lub wstrzyk usterki.
- PP: bank rezystorów (1,5 k/680/220 Ω).
- opcjonalnie: izolowany detektor zamknięcia stycznika, obciążenie+czujnik prądu.
- do PC: USB/WiFi.

**Wniosek do pitchu:** to, co w symulacji jest blokiem-mostkiem, w sprzęcie staje się peryferium MCU + układem pośredniczącym. **Symulacja jest wprost specyfikacją adaptera.**

---

## 6. Dwa tryby pracy (mapowanie 1:1)
- **Tryb 1 — czysta symulacja (deliverable teraz):** obie role w Stateflow, „kabel" w Simscape; scenariusze + usterki; komparator vs wartości oczekiwane z normy. Zero kapitału.
- **Tryb 2 — HIL z realną ładowarką:** podmiana — Stateflow „Emulator auta" → **adapter sprzętowy**; Simscape „warstwa CP" → realny kabel Type 2 + elektronika CP ładowarki; „Złoty wzorzec" **zostaje w software** jako odniesienie; komparator+raport bez zmian, karmione pomiarami z adaptera. W sprzęt przechodzi tylko połowa „auto".

---

## 7. Następne kroki (priorytet)
1. **Rozbić złoty wzorzec na 3 zagnieżdżone pętle** w `AMPERE_POINT_projekt_v3.tex` (monolit → warstwy) — sekcja architektury + diagram kaskady. → v4.
2. **Dorysować schemat toru mocy** (stycznik + licznik + obciążenie) jako uzupełnienie istniejącego schematu CP.
3. **Rozpisać logikę stycznika** (permisywne zamknięcie + weto, bramka `AND not(fault)`) jako fragment Stateflow gotowy do modelu.
4. **Tabela „blok symulacji → peryferium MCU → element elektryczny"** (most sim↔HIL na jednej stronie).
5. Dopiero potem: karty Stateflow w pełni (stany/przejścia/sygnały), Faza 2 modelu.

## 8. Zasady pracy (bez zmian)
PL, zwięźle, technicznie, dla kogoś z podstawami elektrotechniki. Dokumenty `.tex`+`.pdf` (xelatex, DejaVu, granatowe nagłówki), wersjonować nie kasować, pisać do folderu `AMPERE_POINT`. `.tex`/skrypty przez shell heredoc, weryfikować `tail`/balans `\begin`/`\end`. Cel: sposób myślenia + realizowalność → pełna dokumentacja projektowa.
