---
doc_type: ai-memory
audience: AI assistant (nie do czytania przez ludzi; format zoptymalizowany pod odtworzenie kontekstu)
subject: AMPERE POINT wallbox M3A1-11W — architektura elektroniki, referencje diagnostyczne
version: 2
created: 2026-09-04
updated: 2026-09-06 (Rev.2 schematu: symbole IEC, układ fizyczny; nowe ustalenia z zoomów zdjęć)
sources:
  - photos: AMPERE_POINT/WALLBOX_architektura/*.jpg (22 szt., 1280x1280, hash-nazwy)
  - manual: AMPERE_POINT/wallbox_22kw_kabel11kw/WALLBOX MANUAL 3.0.pdf (Rev. 20251121, skan; s.1-24 przejrzane)
  - prior: AMPERE_POINT/diagnostyka/ARCHITEKTURA_plytek_modeli.md (Q11), KONTEKST/KONTEKST_kompendium_czatow.md (§2.1-2.3, §4.3, §6)
  - prior: AMPERE_POINT/diagnostyka/AMPERE_POINT_rejestrator_zlacza_Q11_v2.md (§2 pinout Q11)
  - schematic: AMPERE_POINT/WALLBOX_architektura/WALLBOX_M3A1_schemat.pdf (Rev.2, A1: str.1 = schemat w układzie fizycznym płyty (widok TOP) + legenda + lista niepewności + tabela pinów; str.2 = mapa foto, opis, BOM)
  - schematic_source: /home/claude/wb/tex/wb_phys.tex (circuitikz european; współrzędne X = 1 + fx*56, Y = 54.5 - fy*50, fx/fy = ułamki zdjęcia 33c6c377) — źródło może nie istnieć w nowej sesji, wtedy odtworzyć z PDF
  - sibling: AMPERE_POINT/P11_schemat/P11_schemat.pdf (ładowarka przenośna, inna architektura)
confidence_legend: "[C]=odczytane z nadruku/sitodruku/manuala, [I]=wywnioskowane z funkcji, [Q11]=przeniesione z płyty Q11 tego samego OEM, [?]=niepotwierdzone"
---

# 0. TOŻSAMOŚĆ
- model_family: Mode 3 Wall-mounted AC EV Charger, OEM powered by Tuya. Numery: M3A1-11 (16A, 11kW), M3A1-11W (16A+WiFi), M3A1-22 (32A), M3A1-22W [C manual s.8]
- egzemplarz_na_zdjęciach: wersja z kablem Typ 2 na stałe (tethered), zasilanie kablem z wtykiem CEE 16A 5P czerwony [C foto]; złącze LOCK niewykorzystane [I]
- parametry [C manual]: 400V 3f 50Hz, 16A, RCD typ A 30mA + RDC-DD 6mA DC, IP65 (wtyk IP66), -25..+50°C, wys. do 2000 m, kabel 11kW: 5x2.5 + 1x0.75 mm², wymiary 25/19.5/8 cm
- front [C manual]: LCD, LED stanu (biały=selftest, niebieski=gotowa, zielony pulsujący=ładowanie, czerwony=błąd), klawisz A (Ampere: prąd 6-16A), klawisz C (Clock: opóźnienie +30 min), NFC card auth (opcja), przycisk stopu awaryjnego na dole
- łączność [C]: Wi-Fi 2.4GHz Tuya Smart (moduł WBR3), DLB pairing opcjonalny (RF433), RS485 zaciski, pole 4G niezalutowane
- ARCHITEKTURA_KLUCZ: JEDNA płyta główna (moc+pomiar+zasilacz+MCU) + płytka wyświetlacza Sinotek. Brak osobnej płyty mocy (inaczej niż Q11 i P11).

# 1. PŁYTA GŁÓWNA — INWENTARZ [C jeśli nie zaznaczono]
- przekaźniki: 4x BAOCHENG NB90-12S-S-A, 40A/240VAC/30VDC, 50A/277VAC, 2HP, TV-15, cewka DC12V, data code D305V 0226; monostabilne 1xNO; przełączane L1,L2,L3,N (N też). Ten sam typ co płyta mocy Q11 [Q11].
- zaciski mocy: oczka śrubowe M4 lutowane: L3-out, L3-in, L2-out, L2-in (rząd górny lewy→prawy); N-out, N-in, L1-out, L1-in (rząd dolny). PE: 3 śruby z symbolem uziemienia (osobne, nieprzełączane). UWAGA na sitodruk: "L-in/L-out" = L1.
- przekładniki prądowe: GTA06L2.0 2000/1 (红 博信电子 = Bo Xin), pierścienie na żyłach WYJŚCIOWYCH (kabel ładowania, za przekaźnikami): CT3 na szarej żyle → L3-out (pierścień lewy, przy śrubach PE) [C zoom 33c6c377/0f94a1ff]; CT1 na brązowej → L1-out (pierścień prawy, przy RS485) [C zoom]; CT2 na czarnej → L2-out NIEWIDOCZNY — najpewniej schowany pod dużym rdzeniem RCM [?]. Wtórne (czerwony/czarny) → złącza JST 2-pin A1 (przy UART), A2 (przy L2-out, pod rdzeniem), A3 (przy L3-out/CPL) [C sitodruk 'A2','3']. Przy 16A → 8mA wtórnego. Brak CT na N.
- czujnik różnicowy: moduł RICHSENS RCPD-SA01 (S/N 2012549501841) wlutowany na stronie lutowanej + zewnętrzny duży rdzeń pierścieniowy (ok. 2x większy od CT) pod dławikiem lewym → złącze "RCD" 2-pin. Przez otwór rdzenia widać JEDNĄ grubą czarną wiązkę (koszulka) — interpretacja: 4 żyły L1 N L2 L3 kabla ładowania w koszulce, PE i CP odgałęzione przed rdzeniem [I, DO POTWIERDZENIA zdjęciem]. Alternatywa (mniej prawdopodobna): przez rdzeń idzie tylko 1 żyła (błąd montażu) — wtedy RCM nieskuteczny. Rodzina jak RCPDA20S03-L300 w Q11 (fluxgate, 5V, 6mA DC/30mA AC, S_OUT trip + T_IN autotest, IEC 62752) [Q11/I].
- ZHTPT107: 1 szt. (niebieski, przy LOCK). 1:1, 2mA/2mA, 3.2kV. Funkcja [?]: najpewniej tor N–PE (kontrola uziemienia) albo izolowane odniesienie fazy. NIE zakładać, że to pomiar 3 faz — tych jest za mało.
- dzielniki napięcia (strona lutowana): łańcuchy 4x "1004" (1MΩ) + "2402" (24kΩ) — 3 zestawy → V1 V2 V3 [I]; osobne łańcuchy "1504" (1.5MΩ) — [?] pomiar za przekaźnikami (Sticky Relay / napięcie na wtyku). Analogia Q11: dzielniki 1MΩ na płycie mocy → piny V1-V3 [Q11].
- zasilacz: bezpiecznik F1 "T2A250V" (brązowy SMD-blok) leży TUŻ przy zacisku L2-in → faza zasilacza = L2 [C położenie]; łańcuch (kolejność fizyczna od F1 w dół): R1 rezystor mocy cylindryczny (paski odczytane niepewnie: niebieski-szary-złoty = 6.8Ω?) → CX żółty kondensator foliowy → C_bulk szary elektrolit (400V) → RV niebieski dysk (MOV lub Y) → dławik CM (2 cewki miedziane na zielonym rdzeniu) → pionowa płytka AC/DC (trafo flyback z pomarańczową taśmą, TO-252, SMD, mały niebieski dysk) [C foto 3831432d/4a7fc1ae]. Węzeł N zasilacza = ślad na płycie z N-in [I]. Wyjście 12V; turkusowy elektrolit przy K4 = wyjście modułu [I]; 3x 470µF/16V przy LCD/J3 = filtr 12V [I].
- przetwornice wtórne (strona lutowana): dławik "100" (10µH) + IC → 5V [I]; dławik "2R2" + SOT-223 → 3.3V [I]; jedna z nich lub osobna pompa ładunku → −12V dla CP [?].
- MCU: LQFP-48 (12 pinów/bok), nadruk NIECZYTELNY na zdjęciach. Złącze J3 SWD "3V DIO CLK GND" → rdzeń ARM Cortex-M [I]. W Q11 MCU opisany "X2Q322 LQFP64" [Q11] — tu inna obudowa, inny układ.
- radio: Tuya WBR3 (Model WBR3, P/N 2.01.99.00006, S/N 10022554406AC), strona lutowana, antena PCB. UART z MCU [I].
- SOIC-8 x3 (strona lutowana), nadruki nieczytelne; kandydaci: wzmacniacz CP (±12V), komparator/opamp toru CT, driver [?].
- SOT-23 (kilka) przy dzielnikach i cewkach: tranzystory cewek K1-K4 / diody [?].
- złącza sygnałowe: LCD 14-pin (5V 3V3 GND BTNA LED BTND SCK MOSI CS SCL SDA DC RST BL) [C]; LOCK 8-pin (PP F+ F− M− M+ +3 nieopisane) [C]; RS485 2-pin śrubowe A/B [C]; przełącznik suwakowy "RF433 ⟷ RS485" [C] (jeden UART, dwa cele [I]); "RF433 Module" pin header 8 [C, pusty]; "4G MODULE" pole 2x10 [C, puste]; "RCD" 2-pin pod rdzeniem RCM [C]; "S" JST 4-pin (żółty=NO, biały=C bloku zestyków stopu awaryjnego; foto c84d19c8 pokazuje wpięcie w NO i C) [C]; "CPL" (sitodruk przy śrubach PE) = najpewniej linia CP z kabla ładowania (biała 0.75) [I] — WCZEŚNIEJSZY zapis o "CP 3-pin z szarym kablem" był błędny (szary = żyła L3 przechodząca obok); A1/A2/A3 JST 2-pin = wtórne CT [C]; NTC = czarny czujnik opasany opaską na brązowej żyle L1-in obok CT1, przewody do gniazda przy UART (4-pin w ramce?) [I]; UART 6-pin "3V GND …" [C]; mała niebieska płytka z nadrukiem "101 …" pod przewodami przy rdzeniu RCM/RCD [?, nieznana].
- sitodruk "J3 烧录"-odpowiednik: tu "3V DIO CLK GND" bez nazwy [C].

# 2. PŁYTKA WYŚWIETLACZA — Sinotek XMT-M3-LCD, 2025-12-03 [C]
- LCD TFT 2.4" FPC "HD24019C18-V3", złącze FPC ~24-pin; interfejs SPI (SCK MOSI CS DC RST) + BL [C sitodruk]
- NFC: WS1850S (Wisesoft, QFN-32, MFRC522-compatible, 13.56MHz) + rezonator "ZHW 27.000 MHz", antena = pętla ścieżek wokół [C nadruk "WS185.."+logo]
- 2x 470µF/16V RVT; 2x SOT-23-6 (AM..1B?) = LDO/translator [I]; rezystory 01C(10k),01B(1k),20R0
- sitodruk płytki opisuje SPI jako SCL/SDA (dwie pary SCL/SDA!) — mapowanie na płytę główną: SCK↔SCL#1, MOSI↔SDA#1, drugie SCL/SDA = I2C NFC [I]
- klawisze A/C = BTNA/BTND, LED = 1 linia [C]

# 3. FUNKCJE ↔ BLOKI (do diagnostyki)
- "Leakage Protection" ← RCPD-SA01 S_OUT. Sprawdzić: żyły przez rdzeń (wszystkie 4 raz, w koszulce), złącze RCD, 5V, realny upływ kabel/pojazd. Rdzeń jest na kablu ŁADOWANIA (po stronie -out).
- "Unearthed Socket" ← tor detekcji PE (rezystancyjny; L+N→PE ≈0.4MΩ omomierzem = KONSTRUKCYJNE, nie upływ) [Q11/diagnostyka_inf]. [?] udział ZHTPT107.
- "Control Box Overheat" (>80°C, redukcja prądu) ← NTC 2-pin.
- "Undervoltage/Overvoltage" (<80V? / >270V) ← V1-V3 dzielniki 1004. Przerwa w łańcuchu = fałszywe podnapięcie JEDNEJ fazy.
- "Overcurrent" (>20% lub 2A ponad nastawę) ← boczniki CT1-CT3 z offsetem 1.65V (złącza A1/A2/A3). Multimetr DC pokazuje tylko offset; przebieg = oscyloskop. CT są na żyłach -out, więc bez zamkniętych przekaźników nie ma sygnału.
- "EV Diode Not Detected" ← brak −12V w dolnej połówce CP.
- "System Error 9 Sticky Relay" ← napięcie za przekaźnikiem przy rozwartym (dzielniki 1504 [?]).
- "System Error 10 RCD Failure" ← autotest T_IN→S_OUT nieudany.
- "System Error 11 CP Failure" ← sterownik CP / ±12V / zwarcie CP-PE.
- brak ekranu + brak LED ← F1, filtr, moduł AC/DC, 12V, buck 3.3V; ekran ciemny ale ładuje ← taśma 14-pin, 5V, płytka Sinotek.
- brak jednej fazy na wyjściu ← 1 przekaźnik / 1 tranzystor cewki / zacisk; przekaźniki monostabilne → brak 12V na cewce = nie załączony (inaczej niż P11 latching).

# 4. WARTOŚCI ODNIESIENIA (Q11 = ten sam OEM; M3A1 do potwierdzenia)
- CP stan A: +12V stały (Q11: 12.2V); stan B: +9V PWM; stan C: +6V PWM; dół −12V; f=1kHz (Q11: 0.999kHz); wypełnienie = I[A]/0.6 → 16A = 26.7% (Q11: 26.4–27.2%) [KONTEKST §6]
- offset toru CT = 1.65V DC [Q11]
- szyna główna: 12V (moduł) ±5%; 5V; 3.3V (mierzyć na złączu LCD: piny 5V, 3V3)
- L→N na wtyku CEE omomierzem ≈120kΩ (dzielniki + bleeder) [diagnostyka_inf]; L+N→PE ≈0.4MΩ konstrukcyjne
- spadek na zwartym zestyku przy 16A: <100mV; trend rosnący = ucieczka termiczna [KONTEKST §2.1]
- cewka NB90-12S: 12V przy załączeniu; sygnał K z MCU ~3V (Q11 na złączu międzypłytowym K=7.45V/5.08V, ale tam inny stopień) [Q11]

# 5. RÓŻNICE WZGLĘDEM INNYCH MODELI (żeby nie mylić)
- vs Q11 (przenośna 11kW): Q11 = 2 płyty (mocy X20322_2_V4 + sterująca X2Q322_K_V4) z taśmą 2x10 (PE NTC1 ICP 8V K1-K4 1.65 CP / GND GND CT NTC2 ZL3 ZL2 ZL1 V1 V2 V3), RCM jako moduł z kabelkami RCPDA20S03-L300, wyświetlacz DWIN T5L0 (UART). M3A1 = 1 płyta, RCM wlutowany RCPD-SA01, wyświetlacz Sinotek SPI + NFC WS1850S. Wspólne: NB90-12S-S-A, F1 T2A, WBR3, dzielniki 1MΩ, CT 2000:1, offset 1.65V.
- vs P11 (przenośna 11kW, inny OEM/płyta GPEV320): P11 ma licznik RN8302B, przekaźniki bistabilne Fanhar FH35L-40 (impuls SET/RESET), przekładniki ZHTPT107 x3 + ZHTC01A x3, VIPer22A. M3A1 nie ma licznika scalonego — liczy MCU.

# 6. NIEWIADOME / DO POMIARU (priorytet)
1. Typ MCU (lupa/SWD) — bez tego brak możliwości odczytu firmware/debug.
2. Przypisanie K1-K4 → przekaźnik/faza (przyjęte wg zacisków nad korpusami: K4=L3 skrajny lewy górny, K3=L2, K1=N, K2=L1 skrajny prawy dolny; sitodruk K nieodczytany) — przedzwonić od cewek do SOT-23 do pinów MCU.
2a. RDZEŃ RCM: ile żył przez otwór i dokąd idą jego 2 przewody (RCD czy A2) — zdjęcie z góry/z boku po odchyleniu przewodów. CT2: gdzie jest (pod rdzeniem?) — zdjęcie okolicy pod rdzeniem + złącze A2.
2b. CPL/A3 przy śrubach PE: który przewód wchodzi do CPL (biała CP?) — zdjęcie z góry z przewodami. Śruby PE: która żyła PE na której śrubie + cienki przewód na środkowej.
3. Rola ZHTPT107 (N–PE vs faza).
4. Który łańcuch = pomiar za przekaźnikami; próg "Sticky Relay".
5. Skąd −12V dla CP; typ wzmacniacza CP (SOIC-8).
6. Pinout złącza "CPL" i gniazda NTC (4-pin w ramce przy UART?); "S" 4-pin = NO+C potwierdzone [C].
7. Wartość boczników CT i filtrów RC (nadruki nieczytelne na zdjęciach 1280px).
8. Nazwa/numer laminatu płyty (nie trafił na zdjęcia).
9. Spód płyty prostopadle w 4 ćwiartkach (dzielniki: z których zacisków -in/-out; ZHTPT107 pierwotne; MCU; SOIC-8; przetwornice) — żeby zamienić bloki/linie [?] na pełne połączenia.
10. Pionowa płytka AC/DC z obu stron + R1 z bliska (kod paskowy) + wartości CX/C_bulk/RV.

# 7. INDEKS ZDJĘĆ (WALLBOX_architektura/, prefiks hash → treść)
- 33c6c377: pełny widok płyty głównej od frontu (MAPA, użyte na str.2; baza współrzędnych schematu Rev.2) — przekaźniki, zaciski, CT, rdzeń RCM, RS485, RF433, LOCK, ZHTPT107, moduł AC/DC. Zoomy potwierdzają: szara żyła przez CT3 → L3-out, brązowa przez CT1 → L1-out, czarna CEE → L2-in obok rdzenia, F1 przy L2-in, brzęczyk HNDZ przy RCD
- 455e90dc: strona lutowana (fragment) — WBR3, RCPD-SA01, dzielniki 1004/2402/1504, pola zestyków, dławik 100
- 722ad31f: strona lutowana pod kątem — MCU LQFP-48, SOT-223, dławik 2R2
- e5904880: strona lutowana zbliżenie — RCPD-SA01 nadruk, 2x SOIC-8, rezystory 22R0/1001/1003/3302
- ee6568db, fd5c746b, 256718a4: strona lutowana — łańcuchy 1004/2402/1504, pola przekaźników
- 3b1bc630: prawy dół płyty — ZHTPT107, LOCK (PP F+ F− M− M+), przełącznik RF433/RS485, RS485, UART 6-pin, "L-in L-out N-in"
- 0f94a1ff: lewy górny róg — złącze LCD 14-pin z opisem pinów, J3 SWD, złącze S/CP, zaciski PE
- 3831432d, 4a7fc1ae, b755133e: przekaźniki NB90-12S-S-A, moduł AC/DC, filtr (X2, dławik, warystor, rezystor), F1 T2A250V
- 545b958b: przekładnik CT3 GTA06L2.0 2000/1 nadruk (na szarej żyle), koniec płaszcza kabla EVC, żółto-zielone do śrub PE, perspektywa od strony dławików (góra zdjęcia = strona zacisków)
- c84d19c8: blok zestyków stopu awaryjnego NC/NO/C — żółty w NO, biały w C; obok śruby PE z żyłami żółto-zielonymi
- 06365ad7, 3ac5e84b, a983f302, c403fb02: płytka wyświetlacza Sinotek XMT-M3-LCD — złącze 14-pin (opisy), 470µF, SOT-23-6, FPC LCD HD24019C18-V3
- 3a25b702: czytnik NFC WS1850S QFN-32 + rezonator 27MHz (zbliżenie)
- 6dd7e003: 3x 470µF/16V, J3, złącze LCD od strony płyty głównej
- 68dba0b6: pełny widok strony lutowanej (glare) — RCPD-SA01 w rogu

# 8. JAK UŻYĆ TEJ NOTATKI
- Przy zgłoszeniu serwisowym M3A1: najpierw dopasować komunikat z ekranu do §3, potem sprawdzić wartości z §4 i z tabeli pinów na str.1 schematu, potem lokalizować na schemacie str.1 (układ = płyta widziana od góry) lub mapie str.2 (numery 1-27, A-E, P-S).
- Konwencja schematu Rev.2 (wymaganie użytkownika): symbole IEC, elementy w miejscach jak na płycie, WSZYSTKIE połączenia narysowane (łuk = skrzyżowanie bez połączenia), sterownik = 1 blok z wyprowadzeniami, bloki tylko w ostateczności (AC/DC, wyświetlacz, sterownik); linie fioletowe kreskowane = domniemane. Przy kolejnych rewizjach NIE wracać do konwencji z flagami/etykietami sieci (odrzucona).
- Przy porównaniu z Q11/P11: §5 — nie przenosić założeń między modelami (bistabilne vs monostabilne; licznik scalony vs MCU; RCM moduł vs wlutowany).
- Każde nowe ustalenie pomiarowe wpisywać do §6 z datą i zamieniać [?]→[C]; aktualizować version w nagłówku.
