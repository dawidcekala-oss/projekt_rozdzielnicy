# KONTEKST — zadanie rekrutacyjne AMPERE POINT
> **Jak użyć:** wklej ten plik na start nowej rozmowy z Claude. Dla kompletu dołącz: `AMPERE_POINT_projekt_v3.pdf`(+`.tex`), `cp_circuit.slx`, `iec-61851-1_compress.pdf` (norma), `README_obwod_CP.md`, `cp_circuit_sim.py`, `cp_waveform.png`, `AMPERE_POINT_zadanie_zarys_v1.pdf`.
>
> **FOLDER PROJEKTOWY:** `C:\Users\dawid\Desktop\AMPERE_POINT` (podpięty — Claude pisze tutaj, nie do „outputs").
> **CEL NADRZĘDNY:** **pełna dokumentacja projektowa** części 2. **Aktualizacja:** 2026-06-16.

---

## 1. Sytuacja
- **Ja:** Dawid Cekała — inżynieria (robotyka/automatyka/elektronika), cel: automatyka/energetyka. **Pierwsza styczność z ładowarkami EV** — tłumaczyć technicznie, ale od podstaw.
- **Rekrutacja:** Serwisant/Pracownik serwisu w **AMPERE POINT** (Warszawa). Serwis (elektryka+elektronika), integracja smart home, rozwój produktów, rozmowy z fabrykami o jakości, AI/automatyzacja zgłoszeń.
- **Zadanie (deadline pn, ~40 h):**
  1. **Prezentacja ~10 min** o własnym produkcie. **WYBÓR: „Projekt stanowiska zrobotyzowanego"** — stanowisko do punktowego znakowania/dozowania pasty (Torque Seal) na 4 śrubach pokrywy obudowy elektronicznej. Robot TT (gantry X/Y/Z) + SCARA FANUC SR-3iA (załadunek, Profinet) + autorski dozownik z suck-back (komora ciśnieniowa + Venturi −0,86 bar) + wizja OK/NOK + sortowanie. Specy: Tc ≤ 8 s, ±0,05 mm, pole 50×50 mm. **Projekt ZESPOŁOWY, Dawid = kierownik zespołu** (Krupa-procesy, Gliszczyński-hardware, Łyszkowski-PLC) → **trzeba wyraźnie wyróżnić własny wkład**. Prezentacja oceniona pozytywnie (lepsza na tę rolę niż ROSbot — integracja+diagnostyka). Plik: `uploads/Prezentacja_TT (1).pptx`.
  2. **Własny projekt dot. ładowania AC** — patrz sekcja 3.

## 2. Firma AMPERE POINT — fakty
- **Inteligentne ładowarki AC do EV**: wallboxy PRIME/HM 11/22 kW, przenośne (Q/Q PRO/P/B). Type 2; WiFi+**Tuya**; **niezerowalny licznik energii**; OTA; RFID; **DLB do 4 stacji**; **RCD typ A 30 mA + 6 mA DC**; TÜV; IP65/66; 6–32 A co 1 A.
- **„OEM na sterydach"**: gotowy sprzęt z Azji, magazyn Tuchom k. Gdańska, testują/wdrażają/sprzedają bezpośrednio. „Każda jednostka przechodzi wiele testów".
- **Firmware ZAMKNIĘTY** (chiński) → ładowarka = **czarna skrzynka**; zgłaszają uwagi, producent przysyła nowy firmware/elementy.
- **Świadomie BEZ OCPP**; prosty sprzęt + licznik do rozliczeń małych flot (1–30 aut). Rozdają podstawowy **„tester wallboxów"**.
- Strategia: mało prototypów, szybka adaptacja, nie topić kapitału. **Cenią INTEGRACJĘ i DIAGNOSTYKĘ**, nie projektowanie elektroniki od zera.

## 3. Koncepcja (część 2): cyfrowy bliźniak + testbench diagnostyczny EVSE
Firmware zamknięty → opisuję poprawne zachowanie jako **złoty wzorzec** (IEC 61851) i sprawdzam odchyłki realnej ładowarki. Komponenty: (1) wzorzec Simulink/Stateflow+Simscape; (2) emulator auta + scenariusze + **wstrzykiwanie usterek**; (3) komparator → pass/fail + **raport do producenta**; (4) opcjonalny tani adapter. Scenariusze: (A) **weryfikacja licznika energii**; (B) **DLB**; + regresja firmware. Pasuje: integracja+diagnostyka, czarna skrzynka, bez OCPP, ~0 kapitału, ~40 h, rozwija ich „tester wallboxów". Pełny opis: `AMPERE_POINT_projekt_v3`.

## 4. Primer techniczny
- Ładowarka AC = „inteligentny włącznik", prostownik AC→DC jest w aucie. **Control Pilot (CP)** — żyła sygnałowa, rozmowa napięciem (IEC 61851). Stany: A `+12 V`, B `+9 V`, C `+6 V`, D `+3 V`, E/F `0`/`−12 V`. **PWM 1 kHz**: I[A]=wypełnienie[%]×0,6 (32 A≈53%). **PP** kabel. **RCD typ A+6 mA DC**. **DLB**, **licznik**, **Tuya**.

## 5. Obwód CP — Faza 1 (ZROBIONE, zweryfikowane)
- Topologia: `Vpilot(±12 V PWM)–[R1 1k]–(CP)–[dioda]–(X)–[R2 2,74k]–masa`; stan C dokłada `[SW]–[R3 1,3k]`. Poziom mierzony na węźle CP.
- **Python:** A `+12,00`, B `+8,98` (~9 V), C `+5,99` (~6 V), dół `−12 V`. Wykres `cp_waveform.png`.
- **Model wzorcowy `cp_circuit.slx`** (jest w folderze, kompletny i poprawnie połączony) — kanoniczne źródło prawdy.
- W folderze jest też **`iec-61851-1_compress.pdf` — pełna norma IEC 61851-1** (źródło do dokumentacji i precyzji).

## 6. Status i pliki (folder `AMPERE_POINT`)
- `AMPERE_POINT_zadanie_zarys_v1` (część 1 + szkic 2); `AMPERE_POINT_projekt_v2`; `AMPERE_POINT_projekt_v3` (v2 + „10. Ścieżka realizacji").
- `cp_circuit_sim.py`, `cp_circuit.cir`, `cp_waveform.png`, `README_obwod_CP.md`.
- `cp_circuit.slx` — model wzorcowy. `iec-61851-1_compress.pdf` — norma.
- `build_cp_circuit_simscape.m` — auto-builder; **nie generuje w pełni poprawnych połączeń** (porty Vsrc/SW/Vsense). Teraz **model `.slx` jest dostępny → można zsynchronizować skrypt 1:1** albo usunąć go z dokumentacji (rekomendacja: `.slx` = wzorzec).
- Wersjonowanie: stare zostają, kolejne `_v2/_v3`… Ten plik aktualizowany na bieżąco.

## 7. Następne kroki
- **Cel: pełna dokumentacja projektowa.**
- (opcjonalnie) Zsynchronizować `build_cp_circuit_simscape.m` z `cp_circuit.slx`.
- Przeramować prezentację TT na 10 min rekrutacyjne + wyróżnić wkład Dawida.
- **Faza 2 — Stateflow:** wzorzec EVSE + emulator auta; dalej prąd/PP, usterki+komparator, licznik, DLB, raport.

## 8. Jak ze mną pracować
- **Po polsku**, zwięźle, technicznie, **jak dla kogoś z podstawami elektrotechniki**.
- Dokumenty **.tex+.pdf** (xelatex, DejaVu, granatowe nagłówki). Wersjonować, nie kasować starych. Pisać do folderu `AMPERE_POINT`.
- Uwaga: file-tool bywa nie syncuje z mountem powłoki → `.tex`/skrypty twórz przez **shell heredoc**, weryfikuj `tail`/balans `\begin`/`\end`.
- Cel: **sposób myślenia** + realizowalność; finalnie **pełna dokumentacja projektowa**.

---
## Aktualizacja 2026-06-16: wkład Dawida w projekt TT (część 1)
Rdzeń projektu jest **autorski**: koncepcja projektowa, schemat stanowiska, **koncepcja dozownika + obliczenia wytrzymałościowe + dobór elementów dozownika**, dobór pozostałych komponentów, **algorytmy sterowania**. Koledzy: Krupa (procesy/technologia), Gliszczyński (konstrukcja/hardware — wykonanie), Łyszkowski (programowanie/PLC — implementacja). **Wniosek:** część 1 prezentować jako własny projekt (lider + autor rdzenia inżynierskiego); haczyk „projekt zespołowy" rozwiązany.

---
## Dodatek 2026-06-16: `USTALENIA_architektura_3petle_2026-06-16.md` (PRZECZYTAJ)
Addendum z ustaleniami architektonicznymi (sesja zewnętrzna). Kluczowe:
- **Złoty wzorzec = 3 zagnieżdżone pętle:** odruchowa/bezpieczeństwo ⊂ sterująca (IEC 61851 + DLB) ⊂ aplikacja (Tuya/RFID/licznik/harmonogram).
- **Stycznik jeden, asymetria władzy:** pętla 2 zamyka/otwiera w normalnej pracy; pętla 1 ma **nadrzędne weto** (awaryjne odcięcie). `zamknięty = (pętla2 każe) AND not(usterka pętla1)`. Diagnostyka mapuje wadę na pętlę (bezpieczeństwo/sterowanie/licznik).
- **Dwa rozdzielne schematy:** CP sygnałowy (mamy) + tor mocy (stycznik+licznik+obciążenie, odłożony); łączy je tylko `contactor_cmd`.
- **Stateflow = logika decyzyjna** (model behawioralny normy), nie firmware/elektronika; fizyka w Simscape, granica = bloki-mostki PS.
- **Symulacja = specyfikacja adaptera HIL** (każdy mostek → peryferium MCU + układ pośredniczący).
- **Do zrobienia:** v3→**v4** (rozbić wzorzec na 3 pętle + diagram kaskady), dorysować schemat toru mocy, rozpisać logikę stycznika, tabela „blok sim → peryferium MCU → element elektryczny", potem pełne karty Stateflow.

---
## Dodatek 2 (2026-06-16): `USTALENIA_cz2_schemat-stateflow-katalog_2026-06-16.md` (PRZECZYTAJ z cz.1)
Doprecyzowania i KOREKTY:
- **Switch w CP = styk WEWNĄTRZ auta** (dokłada R3 → stan C ~6 V), sterowany `StateC` z „Emulatora auta". To NIE stycznik mocy.
- **Jedyny sygnał auto↔ładowarka = napięcie CP** (+ PWM z powrotem). `StateC`/`veh_cmd`/`duty`/`contactor_cmd`/`I_offer` są **wewnętrzne** danej strony. W realu **nie ma przewodu „StateC"** — auto zmienia własną elektronikę, ładowarka widzi tylko skutek (dzielnik → spadek 9→6 V).
- **KOREKTA ról:** Stateflow = **AKTORZY** (odgrywają zachowanie wzorca/auta wg normy), Sekwencer = **reżyser** (scenariusz+usterki), **Komparator = SĘDZIA** (klasyfikuje, liczy odchyłki, pass/fail). Diagnozuje komparator, nie Stateflow.
- **KLUCZ (korekta intuicji):** w symulacji **nie diagnozujesz ładowarki** — **budujesz i kalibrujesz narzędzie** + definicję poprawnej reakcji. Produkt fazy sym = **katalog** par „bodziec → oczekiwana poprawna odpowiedź" + tolerancja + pass/fail. Wzorzec jest **poprawny z definicji** → prawdziwe usterki wychodzą **NA SPRZĘCIE (HIL)**, nie w symulacji. Realny DUT może oblać — te oblania to **odkrycia**. Szybsze, bo testy gotowe/automatyczne; nowy firmware → ten sam katalog → regresje jednym kliknięciem.
- **Tor mocy: dodać** — licznik kWh i DLB nie mają gdzie zaistnieć na schemacie CP.
- **Next-steps (zaktualizowane, zastępują cz.1):** v4 = 3 pętle + diagram kaskady; schemat toru mocy (L/N/PE+stycznik+licznik+obciążenie); logika stycznika (`AND not(fault)`); **sekcja „symulacja buduje test, hardware go wykonuje" + logika katalogu**; opc. TikZ warstw (fizyka/aktorzy/sędzia); tabela „blok sim → peryferium MCU → element elektryczny"; potem pełne karty Stateflow + Faza 2.
