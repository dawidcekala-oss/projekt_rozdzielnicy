# Odpowiedzi fabryki na pytania z dokumentacji
_Corey (fabryka Q11), WeChat, 30 września 2026 · pytania z dokumentacji „Q11 charger with a Shelly X module” v1 · AMPERE POINT · oprac. Dawid Cekała_
FOOTER: AMPERE POINT — odpowiedzi fabryki Q11 · 2026-09-30

## W skrócie {-}

- Fabryka odpowiedziała na wszystkie 11 pytań, jedną listą, po chińsku z automatycznym tłumaczeniem. **7 odpowiedzi jest jasnych i zgodnych z naszymi pomiarami**, 4 wymagają dopytania (pytania 2, 7, 8, 9), jedna kłóci się z logiem (punkt 23 „co 1,5 minuty”), jedna wymaga uwagi (punkt 25 „nieużywany”, choć raz przyszedł).
- **Najważniejsze fakty:** procesor to **STM32F030RCT6 z 256 kB pamięci programu**; płytka używa tylko czterech pól modułu; punkt 8 to zawsze faza C; licznik całkowity przychodzi po zakończeniu ładowania; program rozruchowy sterownika toleruje przerwaną aktualizację; milczenie modułu nie zmienia zachowania sterownika.
- Tłumaczenia poniżej są moje, z oryginału chińskiego; automatyczne tłumaczenie WeChat w dwóch miejscach zaciera sens (pytania 7 i 8).

## 1. Odpowiedzi punkt po punkcie

| Nr, pytanie | Odpowiedź: oryginał i tłumaczenie | Nasze obserwacje | Stan |
| --- | --- | --- | --- |
| **1** jaki procesor i ile pamięci | 单片机STM32F030RCT6，flash-256KB — mikrokontroler STM32F030RCT6, flash 256 kB | zgodne z pomiarem: zasilanie na nóżkach 1, 13, 19, 32, 48, 64, masa na 12, 18, 31, 47, 63, port na PA2/PA3 (nóżki 16/17). To rdzeń Cortex-M0 z rodziny F0, nie F103; ten sam układ wyprowadzeń. Program może mieć do 256 kB, więc aktualizacja po łączu 9600 b/s potrwa do około 5 minut | ✔ |
| **2** co niesie ramka informacji o produkcie | 主要传PID 和软件版本 具体见协议说明 — głównie identyfikator produktu (PID) i wersję oprogramowania; szczegóły w opisie protokołu | wartości nie podali; wersja z punktu 23 przyszła 30.09 po włączeniu zasilania jako „V1” **[dopytać o wartości]** | ◐ |
| **3** które pola miejsca na moduł są używane | 模组的只用 VCC、GND、RXD 和 TXD — moduł używa tylko VCC, GND, RXD i TXD | zgodne z pomiarem 12 wolnych pól | ✔ |
| **4a** kiedy przychodzi punkt 1, licznik całkowity | DP1 在充电完成时会上报 — punkt 1 jest zgłaszany po zakończeniu ładowania | log 29.09: co 90 s w stanie „ładuje”, wartość 0. Zakończenia ładowania jeszcze nie obserwowaliśmy, więc oba mogą być prawdą | ◐ |
| **4b** kiedy przychodzi punkt 17, limit energii | DP17设置功率充电时会有上报下发 — punkt 17 jest zgłaszany i przyjmowany, gdy ustawiony jest tryb ładowania do limitu energii | zgodne z 29.09: wartości 1, 2, 8 po zapisach w tym trybie | ✔ |
| **4c** kiedy przychodzi punkt 23, wersja | DP23 1.5分钟会更新一次 — punkt 23 odświeża się co 1,5 minuty | **sprzeczne z logiem:** w około 15 godzinach ani razu; przyszedł raz, po włączeniu zasilania 30.09. Co 90 s, czyli co 1,5 minuty, przychodzi punkt 1. Najpewniej pomylili numery w odpowiedzi **[dopytać]** | ✘ |
| **4d** punkt 33 | D33 没有使用 — punkt 33 nieużywany | zgodne: nigdy nie przyszedł | ✔ |
| **4e** punkt 25, energia sesji | DP25 没有使用 — punkt 25 nieużywany | przyszedł raz, 25.09 o 11:23, z wartością 0, w jednej ramce z wyłączeniem ładowania. „Nieużywany” znaczy: bez znaczenia użytkowego. Energii sesji z niego nie będzie **[z zastrzeżeniem]** | ✔ |
| **5** znaczenie punktu 33 | D33 没有使用 — jak wyżej |  | ✔ |
| **6** punkt 8: faza C czy zdarzenia | DP8 都是 phase_c — punkt 8 to zawsze faza C | zgodne; definicja Q21 z eksportu, gdzie punkt 8 to „zdarzenia ładowarki”, nie dotyczy Q11 | ✔ |
| **7** przypisanie numerów do nazw w wyliczeniach | 没有顺序要求 — nie ma wymagań co do kolejności | odpowiedź nie na temat: zrozumieli „kolejność wysyłania”, a pytaliśmy, czy 0 = wolna, 1 = podłączone itd. **[dopytać z tabelą]** | ✘ |
| **8** stan Wi-Fi i reset sieci z menu | 暂时没有用 — na razie nieużywane | niejasne. Może znaczyć, że sterownik nie używa wartości stanu sieci. Nie wiemy, czy ikona na wyświetlaczu zależy od tej ramki ani co wysyła reset sieci z menu **[dopytać]** | ✘ |
| **9** aktualizacja sterownika przez moduł | Bootloader 可以中断 中断后需要重新升级 — program rozruchowy można przerwać; po przerwaniu trzeba powtórzyć aktualizację | potwierdza dwie rzeczy: sterownik ma program rozruchowy do aktualizacji po łączu i przerwanie nie psuje płyty. Bez odpowiedzi: format pliku i czy go dostaniemy **[dopytać]** | ◐ |
| **10** do czego sterownik używa czasu | 用于预约充电 — do ładowania planowanego | czyli do okna godzin. Bez odpowiedzi: co się dzieje bez ważnego czasu **[dopytać]** | ◐ |
| **11** czy milczenie modułu coś zmienia | 不会改变控制器行为 — nie zmienia zachowania sterownika | zgodne z obserwacją | ✔ |

## 2. Co z tego wynika dla nas

| Temat | Wniosek | Co zrobić |
| --- | --- | --- |
| Procesor | STM32F030RCT6, rodzina F0. Nasze dokumenty mówią „rodzina STM32F103 / GD32”, bo tak wynikało z układu zasilania, wspólnego dla obu rodzin | poprawić w dokumentacji dla fabryki v2, w schemacie procesora (nóżka 1 = VDD, nóżki 5 i 6 = PF0/PF1, nóżka 28 bez BOOT1) i w mapowaniu pól. Programator MiniPro obsługuje STM32F0 |
| Licznik całkowity | przychodzi co 90 s w trakcie ładowania i według fabryki po zakończeniu | energia sesji z przyrostu punktu 1 jest dobrą drogą; sprawdzić pod obciążeniem |
| Energia ostatniej sesji, punkt 25 | bez znaczenia | nie budować na nim pola; w produkcie v4 pole `last_session_energy` będzie zawsze 0 |
| Wersja, punkt 23 | przychodzi po włączeniu zasilania, nie cyklicznie | pole `controller_version` zapamiętywać w module albo odczytywać przy starcie |
| Punkt 8 | faza C | tłumacz pisany według definicji Q11 PRO jest właściwy; definicja Q21 z repozytorium do odłożenia |
| Aktualizacja przez moduł | technicznie możliwa, program rozruchowy jest odporny na przerwanie | otwarta zostaje sprawa pliku: format i zgoda fabryki |
| Ikona sieci | fabryka sugeruje, że sterownik nie używa stanu sieci | sprawdzić w teście C5, czy ikona na wyświetlaczu reaguje na ramkę stanu sieci; jeśli nie, usterka S-39 traci znaczenie |

## 3. Pytania uzupełniające, projekt wiadomości po angielsku

Hi Corey, thank you for the answers, they are very helpful. A few short follow-ups:

1. **(Q7)** We meant the meaning of each index value on the serial link, not the order of reports. Please confirm: DP3 work_state 0 = charger_free, 1 = charger_insert, 2 = charger_free_fault, 3 = charger_wait, 4 = charger_charging, 5 = charger_pause, 6 = charger_end, 7 = charger_fault. DP13 connection_state 0 = 12V, 1 = 12V_pwm, 2 = 9V, 3 = 9V_pwm, 4 = 6V, 5 = 6V_pwm, 6 = error. DP14 work_mode 0 = charge_now, 1 = charge_energy, 2 = charge_schedule.
2. **(Q4)** In our logs DP23 (system_version, "V1") arrived only once, right after power-on, while DP1 arrives every 90 s during charging. Could "every 1.5 minutes" refer to DP1? And is DP1 additionally reported at the end of charging?
3. **(Q8)** Does the network icon on the charger display depend on the Wi-Fi status frame (0x03) from the module? What does the "network reset / pairing" item in the charger menu send to the module: 0x04, 0x05 or nothing?
4. **(Q9)** Good to know that the bootloader tolerates an interruption. Which file format do you upload to the Tuya platform for the MCU OTA (plain .bin?), and could you provide that file to us, so that the Shelly module, which implements the same Tuya update commands (0x0A / 0x0B), can update the controller? If you prefer the programmer route only, we understand; we are still waiting for the MiniPro client software to read the two codes.
5. **(Q10)** What does the controller do with schedule charging when the module never delivers a valid time, for example without Internet?
6. **(Q2)** Could you send us the exact product-information reply (PID and version string), so that we can verify our capture?
7. **From our tests:** the fault bitmap DP10 arrives as 2 bytes (16 bits), but the definition has 17 codes; which bit is ov_Temp_fault? And after a write to DP17 the controller repeats DP17 and DP14 reports about 10 times per second for a few seconds and misses heartbeats; is that expected?

Thanks, Dawid

## 4. Źródła {-}

- Zrzuty rozmowy: `Qiao\konwersacja\odp_pyt_dokumentacja\` (2 pliki, 30.09.2026).
- Logi modułu: `logi\surowy_2026-09-25_1355.log`, `logi\surowy_2026-09-29_0705.log`.
- Ustalenia testów B: `testy_offline\USTALENIA_v1.md`, `REJESTR_USTEREK.md` (S-20, S-25, S-27), `dokumenty\Q11_zestawienie_DP_Tuya_Shelly_v1.md`.
