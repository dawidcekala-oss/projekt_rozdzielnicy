# Notatki sesji — kamera Imou + Home Assistant (pod raport_v2)

Data rozpoczęcia: 2026-07-05
Cel: integracja kamery Imou z Home Assistant (Docker, localhost:8123).
Plik roboczy — dopisywać wszystko chronologicznie; na końcu posłuży do napisania `AMPERE_POINT_home_assistant_..._raport_v2`.

---

## 1. Identyfikacja sprzętu (ze zdjęć, 2026-07-05)

- Kamera: **Imou Turret SE 4MP — model IPC-T42EP** (potwierdzone z naklejki, zdjęcie 2026-07-05).
  - Obiektyw 2,8 mm, sensor 1/2.8" CMOS, 4MP (2560×1440), H.265/H.264, IR do 30 m.
  - Sieć: **Wi-Fi 2,4 GHz (b/g/n) + port Ethernet 100 Mb/s** — jest LAN, można pominąć Wi-Fi.
  - **ONVIF oficjalnie wspierany**; slot microSD (do 256 GB), mikrofon, przycisk reset.
  - S/N: AA01005PDPBF652. Safety code — na naklejce na spodzie (nie zapisujemy w notatkach; to domyślne hasło urządzenia).
  - Kamera wewnętrzna (indoor), -20…+50°C.
- Zasilacz: Jiuzhou DYS12050WC-E, **12 V DC / 0,5 A (6 W)**, pobór <3 W.

## 2. Rozpoznanie metod integracji (research 2026-07-05)

Kamery Imou można wpiąć do HA na dwa równoległe sposoby (analogicznie jak ładowarki: kanał chmurowy + docelowo lokalny):

### A. Lokalnie — RTSP / ONVIF (preferowane: podgląd na żywo bez chmury)
- Imou = marka konsumencka Dahua; kamery wystawiają **RTSP na porcie 554** (URL w stylu Dahua):
  `rtsp://admin:HASLO@IP_KAMERY:554/cam/realmonitor?channel=1&subtype=0` (subtype=1 = strumień pomocniczy).
- **ONVIF** — wbudowana integracja HA (Ustawienia → Dodaj integrację → ONVIF).
- PUŁAPKA: nowszy firmware Imou ma **szyfrowanie/TLS** — trzeba wyłączyć w aplikacji Imou Life (ustawienia kamery → Encryption/TLS off), inaczej zwykły RTSP nie działa.
- Login: `admin`, hasło: zwykle **safety code z naklejki** lub hasło ustawione w aplikacji.
- Wymaga: kamera w tej samej sieci LAN, najlepiej stałe IP w routerze.

### B. Chmurowo — Imou Open Platform (funkcje dodatkowe: przełączniki, detekcja, syrena)
Dwie opcje:
1. **imou_life** (HACS, autor user2684) — wymaga darmowego konta na `open.imoulife.com` → My App → **AppId + AppSecret** (analogia 1:1 do Tuya Client ID/Secret!).
2. **Oficjalna integracja Imou** (GitHub: Imou-OpenPlatform/Imou-Home-Assistant) — od producenta platformy.
- Portal dla Europy: `open.imoulife.com`; region API musi zgadzać się z kontem aplikacji Imou Life.

### C. Rozbudowa (opcjonalnie później)
- **go2rtc / Frigate** — nagrywanie, detekcja obiektów AI lokalnie; konsumuje strumień RTSP.

## 3. Plan działania

1. [ ] Odczytać model + S/N + hasło (safety code) z naklejki kamery.
2. [ ] Skonfigurować kamerę w aplikacji **Imou Life** (Wi-Fi 2,4 GHz — jak Tuya).
3. [ ] Nadać kamerze stałe IP w routerze; zanotować IP.
4. [ ] Wyłączyć szyfrowanie/TLS w Imou Life (jeśli obecne).
5. [ ] HA: dodać integrację **ONVIF** (IP, port 80, admin + hasło); jeśli ONVIF zawiedzie — **Generic Camera** z URL RTSP.
6. [ ] Test podglądu w HA (karta Picture Glance / Picture Entity na pulpicie).
7. [ ] Opcjonalnie: konto `open.imoulife.com` → AppId/AppSecret → HACS **imou_life** (przełączniki, detekcja ruchu jako encje).
8. [ ] Zanotować wynik każdego kroku tutaj.

## 4. Log wykonanych czynności

- **2026-07-05**: Zdjęcia kamery i zasilacza; identyfikacja wstępna (Imou turret, 12V/0,5A). Research metod integracji (RTSP/ONVIF lokalnie, imou_life/oficjalna chmurowo). Utworzono ten plik notatek.
- **2026-07-05**: Zdjęcie naklejki → model potwierdzony: **IPC-T42EP (Turret SE 4MP)**, 2,8 mm. Ma port Ethernet i oficjalne wsparcie ONVIF → ścieżka A (lokalna) w pełni wykonalna; zalecane podłączenie po kablu LAN zamiast Wi-Fi.
- **2026-07-05**: BLOKADA kamery — urządzenie powiązane z INNYM kontem Imou (trzeba będzie odpiąć od starego konta w Imou Life lub reset + ponowne parowanie). Temat odłożony na później.
- **2026-07-05**: Nowy wątek — **symulacja falownika PV dla HA bez fizycznego sprzętu**. Research: brak gotowego symulatora SUN2000; wykonalne własnym serwerem Modbus TCP (pymodbus) emulującym mapę rejestrów. Opcje opisane w sekcji 7.

## 4a. Log — ciąg dalszy (2026-07-06)

- **2026-07-06 (po północy)**: Na polecenie Dawida powstał **kompletny przewodnik instalacyjno-integracyjny w stylu AmperePoint**: `home_assistant/AMPERE_POINT_przewodnik_HA_instalacja_integracja_v1.tex` + skompilowany PDF (19 stron, XeLaTeX, zero błędów). Zakres: Windows/WSL2/Docker → HA (kontener) → HACS → Tuya → xtend_tuya (etapy A/B/C z krytycznym oknem OpenAPI) → TuyaExtend AmperePoint → porządki/Energia/pulpit → automatyzacje (3 przykłady YAML) → rozszerzenia opcjonalne (kamera Imou IPC-T42EP z blokadą cudzego konta; symulator SUN2000 z pv_sim) → backup/aktualizacje → tabela problemów (instalacyjne + chmurowe + rozszerzenia) → checklista końcowa → słowniczek. Wykorzystuje doświadczenia z sesji 2026-06-30 (VM/VirtualBox — porażka przez most Wi-Fi i uśpienie hosta → decyzja o Dockerze), 2026-07-01 (skrypty ha-docker-*.bat), 2026-07-05 (raport v1 + kamera + symulator). Docelowy czytelnik: osoba bez doświadczenia.
- Drobiazg techniczny: pierwotny zapis .tex został ucięty na ostatnich bajtach (`\end{cen`) — naprawiono dopisaniem końcówki; kompilacja 2× XeLaTeX czysta (0 błędów, 0 overfull).
- **Temat „falownik" (uruchomienie symulatora + integracja w HA) wstrzymany — Dawid wznowi hasłem „falownik".**
- **2026-07-06**: Feedback Dawida do przewodnika: to ma być **instrukcja dla KLIENTA (publikacja w internecie)** — bez wewnętrznych szczegółów projektu (nasze urządzenia, konta, ścieżki), problemy opisane ogólnie (nie jako studium przypadku), styl jak wpis blogowy amperepoint.pl (`/blogs/poradniki/integration-of-ampere-point-q-series-charger-with-home-assistant`), działające linki (stare z bloga 404: hacs.xyz/docs/setup/download → nowa ścieżka hacs.xyz/docs/use/download/download), bez nadmiaru pogrubień, z obrazkami pomocniczymi.
- **2026-07-06**: Powstał `home_assistant/AMPERE_POINT_poradnik_klienta_HA_Q_v1.html` — samodzielna strona (HTML+CSS+inline SVG): intro/korzyści, wymagania, instalacja HA (HAOS lub Docker/Windows z komendami), HACS (obie ścieżki wg oficjalnych docs), Tuya (User Code+QR; „tylko przełącznik = normalne"), xtend_tuya (pobranie≠dodanie; okno OpenAPI z ilustracją SVG „nie zamykaj krzyżykiem", checkbox+Poland+Europe), klucze platformy Tuya + DP Instruction (linki do oficjalnych docs xtend_tuya), efekty+panel Energia, 3 automatyzacje YAML (w tym nadwyżka PV generycznie), tabela 12 ogólnych problemów (ostatni: „1 encja mimo wszystko → kontakt hello@amperepoint.com" — uogólniony przypadek Light Source), tuya-local jako alternatywa, boks „wszystkie linki". Linki zweryfikowane 2026-07-06 (HACS docs, repo xtend_tuya v4.4.8, docs cloud_credentials/enable_all_dpcodes). Walidacja: HTML dobrze sformowany, SVG wyrenderowane poprawnie. Pogrubienia ograniczone do minimum (1 strong w krytycznym ostrzeżeniu + nagłówki tabel).
- Wersja wewnętrzna (LaTeX/PDF 19 str.) zostaje jako dokument projektowy; wersja kliencka jest osobnym plikiem.
- **2026-07-06**: Przewodnik wewnętrzny → **v2** (v1 zostaje wg konwencji): dodany rozdział **„Wariant R — Home Assistant na Raspberry Pi, w całości przez Wi-Fi (bez Ethernetu)"** — wstawiony po Etapie 1. Zawartość: kiedy ten wariant; lista zakupów z uzasadnieniami (Pi 4/5, karta A2 — dlaczego, zasilacz 15/27 W — undervoltage, micro-HDMI); „jak to działa pod maską" (bootloader/karta=dysk, HAOS = NetworkManager + Supervisor + kontenery); Raspberry Pi Imager + PUŁAPKA: personalizacja Imagera (Wi-Fi) NIE działa dla HAOS — pominąć; Wi-Fi metoda A: pendrive FAT32 etykieta CONFIG, folder network, plik `my-network` bez rozszerzenia (pełny listing profilu NetworkManager; pułapka ukrytych rozszerzeń .txt) — zweryfikowano aktualność metody (2026); metoda B: konsola `ha >`, `network update wlan0 --wifi-mode infrastructure --ssid ... --psk ...`; pierwszy start (10–20 min, Preparing HA), mDNS/homeassistant.local + fallback IP z routera, rezerwacja DHCP; różnice HAOS vs Docker (HACS przez dodatek Get HACS z repo hacs/addons, restart z GUI, wbudowane kopie, aktualizacje z GUI); wskazówka SSD/USB boot. Zaktualizowane: podtytuł, mapa etapów (wiersz R), wymagania, tabela problemów (blok 5 wierszy RPi/Wi-Fi), słowniczek (mDNS, NetworkManager), stopka v2. Kompilacja: 26 stron, 0 błędów, 0 overfull.
- **2026-07-06**: Pytania Dawida do rozdziału R → doprecyzowania w v2: (1) jak sprawdzić zawartość karty przed zapisem (Ten komputer; pułapka „Musisz sformatować dysk" po Linuksie ≠ pusta karta; weryfikacja rozmiarem w Imagerze; odłączyć inne USB); (2) pendrive CONFIG nie musi być pusty — HAOS czyta tylko folder network po etykiecie; jeśli już FAT32 → sama zmiana etykiety bez formatowania, inaczej formatowanie (z ostrzeżeniem o utracie danych); etykietę można potem przywrócić. Rekompilacja czysta (26 str.).

- **2026-07-06**: Dawid dostarczył zrzut listy DP z platformy Tuya (ekran DP↔Standard Instruction): **Q11 = 17 punktów danych** (forward_energy_total, work_state, charge_cur_set, phase_a/b/c, power_total, fault, connection_state, work_mode, energy_charge, switch, local_timer, system_version, temp_current, charge_energy_once, mode_set); **Q37 = to samo + dp_num**. Kategoria Tuya: qccdz. Zweryfikowano znaczenia (web): work_state enum charger_free/insert/wait/charging/pause/end/fault; energy_charge = energia bieżącej sesji; charge_energy_once = porcja kWh (nastawa).
- **2026-07-06**: Poradnik kliencki → **v2** (`AMPERE_POINT_poradnik_klienta_HA_Q_v2.html`, v1 zostaje): w sekcji 7 rozwijana ściąga encji (details/summary, bez JS — działa też po wklejeniu do Shopify): tabela 17 DP Q11 z objaśnieniami po polsku + typ encji w HA; blok Q37 (dp_num + uwaga o zerowych fazach B/C w modelu 1-fazowym); powiązanie z sekcją 6.2 (skąd bierze się lista DP); nawiązanie do Q&A o „faktycznej mocy" przy power_total; poprawka przykładu YAML (from charger_charging → to charger_end zamiast charging/charger_free); dopisek „wersja 2" w meta; CSS akordeonu. Walidacja HTML czysta.

- **2026-07-06 KOREKTA**: Moje założenie „Q37 = Q11 + dp_num" było BŁĘDNE. Drugi zrzut Dawida: **Q37 ma własny szablon producenta, 26 DP**: switch_led (główny włącznik!), work_mode, x_work_state, x_metrics (pakiet pomiarów), x_selftest, x_alarm, x_charge_history, x_charger_info, x_adjust_current, x_downcounter, x_work_st_debug, x_wifi_signal, current_for_cjsz, x_do_charge, x_do_reset, x_do_reboot, x_charge_current, x_charge_mode, x_max_current_cfg, x_lang_cfg, x_socket_cfg, x_nfc_cfg, x_earch_free_cfg (literówka producenta od earth-free), x_product_varient (literówka), x_heartbeat + dp_num (poza kadrem zrzutu). Blok Q37 w poradniku v2 wymieniony w całości: tabela 26 DP w 4 grupach (sterowanie/status/konfiguracja/serwis) z odpowiednikami Q11 w opisach; usunięta błędna uwaga o phase_b/c; intro ściągi wyjaśnia różnicę szablonów (Q11 standardowy vs Q37 własny x_*). Obecność switch_led w Q37 spójna z wcześniejszym odkryciem „Light Source" — szablony producenta ewoluują z tej samej bazy.

- **2026-07-06**: Nowy dokument: **`AMPERE_POINT_poradnik_automatyzacje_integracje_HA_v1`** (tex+PDF, 28 stron, XeLaTeX czysto) — wyczerpujący poradnik automatyzacji i integracji urządzeń. Zakres: architektura HA (magistrala zdarzeń/maszyna stanów/recorder/rejestry, ramki „Dla ciekawych" o asyncio itd.), odkrywanie urządzeń (mDNS/SSDP/DHCP/BT) i klasy IoT (kwadrant local/cloud×push/poll), protokoły w głębi (HTTP/REST/WebSocket, MQTT z QoS/retain/LWT/discovery, Zigbee ZHA vs Z2M + mesh + pułapka USB/2,4 GHz, Z-Wave 868 MHz, Thread vs Matter — rozdział warstw, BLE+proxy/BTHome, RTSP/ONVIF/go2rtc/Frigate, Modbus), ekosystemy (Tuya-esencja, ESPHome z pełnym przykładem YAML czujnika, Shelly, Companion), anatomia automatyzacji (nowa składnia 2024.10 triggers/actions — zweryfikowana web + tabela tłumaczenia starej platform:/service:, wszystkie wyzwalacze/warunki/akcje/tryby), Jinja2 (stany-jako-tekst, float(0), has_value, tabela niezbędnika), helpery/skrypty/sceny/blueprinty, **7 przepisów z komentarzem** (taryfa schedule, koniec ładowania z kosztem, FLAGOWY: nadwyżka PV z płynną regulacją prądu 6–16 A z poprawką na własny pobór + IEC 61851 min 6 A, eskalacja repeat/until, actionable notifications pełny obieg, watchdog unavailable, raport dzienny), diagnostyka (traces + 6 pułapek), Energia (state_class total_increasing, Riemann left, utility_meter+taryfy), niezawodność (backupy, aktualizacje, Nabu Casa/VPN/proxy), tabela problemów, duży słowniczek. **Pomoce wizualne (na prośbę Dawida): 6 autorskich diagramów TikZ** — architektura (magistrala), kwadrant IoT, MQTT pub/sub, gwiazda vs mesh, oś pasm 868 MHz/2,4/5 GHz, przepływ wyzwalacze→warunki→akcje. Poprawka rzetelności: usunięty wymyślony klucz `actions_traced` z listingu przed publikacją.

- **2026-07-07**: Poradnik automatyzacji → **v2** (35 stron, XeLaTeX czysto; v1 zostaje). Na życzenie Dawida (wybrał w ankiecie: rozdział 5 — Ekosystemy):
  - **Nowy rozdział „Klik po kliku"** (wstawiony przed Anatomią): edytor automatyzacji HA krok po kroku (Utwórz → wyzwalacz/warunek/akcja → zapis → menu „…": Uruchom [tylko akcje!], Ślady, YAML, Duplikuj; per-klocek Edytuj w YAML); automatyzacje Smart Life (Scena → + → Gdy/Wtedy → zapis; działają w chmurze bez HA); platforma deweloperska: linkage rules przez **API Explorer** (UID → home_id → Add Automation z przykładowym JSON; usługa Scene Linkage z naszego projektu; szczera ocena: droga dla programistów); tabela „gdzie trzymać którą regułę" + UWAGA o dublowaniu reguł (duchy).
  - **Rozdział 5: każdy ekosystem rozszerzony o „Wdrożenie krok po kroku — najpierw symulacja, potem sprzęt"**: 5.1 Tuya — Symulacja A: pakiet `ha_sim_tools/symulator_ladowarki.yaml` (pełna udawana ładowarka: status charger_*, moc=prąd×3×230, energia Riemann+utility_meter, number 6–16 A, switch z blokadą „bez wtyczki", + helpery cena/progi PV) z instrukcją packages i **tabelą mapowania encji sym→xtend_tuya (Q11/Q37)**; Symulacja B: wirtualne urządzenia na platformie (Add Virtual Devices for Debugging + API Explorer; uczciwa uwaga: nie wchodzą do HA); sprzęt = etapy 3–7 przewodnika + podmiana ID. 5.2 ESPHome — symulacja platformą **host** w WSL (`ha_sim_tools/esphome_host_sim.yaml`, API 6053, HA: host.docker.internal; zweryfikowane web: host = Linux/macOS/WSL) + sprzęt ESP32 (COM→OTA). 5.3 Shelly — symulacja przez **MQTT Discovery** (`ha_sim_tools/mqtt_fake_device.md`: Mosquitto kontener, 2×config retain, stany, mosquitto_sub na /set) + sprzęt (AP 192.168.33.1, mDNS). 5.4 Companion — symulacja bez telefonu (persistent_notification + ręczne zdarzenie mobile_app_notification_action z Narzędzi dev) + sprzęt (instalacja, zezwolenia, strefy). 5.5 kompas — Zigbee sprzętowo z **UWAGĄ: Docker Desktop/Windows nie przekazuje USB** (usbipd-win albo wariant R/RPi), Matter przez QR/Companion, falownik: pv_sim → sprzęt = zmiana tylko hosta na IP SDongle.
  - Weryfikacje web przed pisaniem: Tuya Scene Linkage API (istnieje, deprecated-but-working), wirtualne urządzenia Tuya (Devices → Add Virtual Devices for Debugging), ESPHome host (Windows przez WSL).
  - Nowa paczka narzędzi: **`ha_sim_tools/`** (3 pliki, gotowe do użycia).

## 4b. Q&A techniczne (2026-07-06)

**P: Czy moc w Tuya/HA może być „wprost z urządzenia", czy zawsze przeliczana? (klient, „coś z ułamkami")**
O: Encje DP z xtend_tuya NIE są przeliczane: ładowarka raportuje integer + skala z szablonu produktu (÷10^n = zmiana jednostki, nie obliczenie); to samo widzi Smart Life. Trzy typowe przyczyny rozjazdu: (1) zaokrąglenie wyświetlania w HA → ustawienia encji → Wyświetlana precyzja (+ jednostka W/kW); (2) encja pochodna (helper TuyaExtend / suma faz) zamiast surowej `cur_power` → zmapować źródłową; (3) zła skala w szablonie produktu (×10) → poprawka po stronie producenta. Weryfikacja u źródła: platforma Tuya → Debug Device / API Explorer (Query Properties) — surowe DP na żywo. Zastrzeżenie: raporty DP są progowe/okresowe (próbki), ale każda próbka = dokładny pomiar urządzenia.

## 5. Dane do uzupełnienia

| Pole | Wartość |
|---|---|
| Model kamery | IPC-T42EP (Imou Turret SE 4MP, 2,8 mm) |
| S/N | AA01005PDPBF652 |
| IP w LAN | _do uzupełnienia_ |
| Hasło urządzenia | NIE zapisywać tu — trzymać w menedżerze haseł |
| AppId (open.imoulife.com) | _jeśli etap B_ |

## 7. Symulacja falownika PV (bez sprzętu) — opcje

Falowniki (w tym Huawei SUN2000, docelowy wg dokumentu AMPERE_POINT_integracja_SUN2000) rozmawiają z HA po **Modbus TCP** — protokół da się zasymulować programowo. Gotowego symulatora SUN2000 brak; trzy poziomy wierności:

1. **Symulator SUN2000 (pełna wierność)** — własny serwer Modbus TCP w Pythonie (pymodbus) z mapą rejestrów SUN2000; HA łączy się przez prawdziwą integrację **huawei_solar (wlcrs)** jak z fizycznym falownikiem. Ćwiczy dokładnie docelową instalację. Nakład: średni (integracja waliduje sporo rejestrów: model, S/N, parametry).
2. **Generyczny falownik Modbus (średnia wierność)** — prosty serwer pymodbus (kilkanaście rejestrów: moc PV, energia dzienna/całkowita, napięcia) + wbudowana integracja HA `modbus` (YAML). Szybkie, niezawodne, uczy Modbusa.
3. **Same dane (bez protokołu)** — sensory template/MQTT generujące realistyczną krzywą produkcji PV (dzwon dzienny + chmury). Wystarcza do testów panelu Energia i automatyzacji „ładowanie nadwyżką PV" z ładowarkami; zero konfiguracji sieciowej.

Architektura (opcje 1–2): symulator jako skrypt/kontener na tym samym PC; HA (kontener Docker) łączy się na `host.docker.internal:502`.

**DECYZJA (Dawid): opcja 1 — symulator SUN2000.** ZREALIZOWANO 2026-07-05:

- Zbudowano `pv_sim/sun2000_sim.py` — serwer Modbus TCP w **czystym Pythonie (stdlib, zero zależności)**; pierwotna wersja na pymodbus porzucona (sandbox bez PyPI, a stdlib upraszcza uruchomienie na Windows).
- Emuluje SUN2000-10KTL-M1: identyfikacja (model/SN/PN @30000+), parametry znamionowe, stany/alarmy, 2 stringi PV, moce DC/AC, napięcia/prądy faz, częstotliwość, sprawność, temperatura, energia dzienna/całkowita (@32106/32114), licznik energii 3-fazowy (@37100+, eksport/import), czas systemowy; FC03/04/06/16; odczyt poza zakresem → wyjątek Modbus (tak huawei_solar wykrywa brak baterii/optymalizatorów).
- Realistyka: krzywa dobowa sin^1.5 (wschód/zachód konfigurowalne), zachmurzenie jako spacer losowy, obciążenie domu 0,3–2,5 kW ze szczytem wieczornym, `--time-scale` przyspiesza dobę, stan liczników w `sun2000_sim_state.json`.
- **Testy w sandboxie (Linux, 2026-07-05): PASS** — odczyty pojedyncze i blokowe (116 rej.), 3 równoległe połączenia, zapis FC06, wyjątek kod 2 poza zakresem.
- Pliki: `pv_sim/sun2000_sim.py`, `pv_sim/test_client.py`, `pv_sim/README_URUCHOMIENIE.md`.
- Podpięcie w HA: HACS → „Huawei Solar" (wlcrs) → Dodaj integrację → Modbus TCP → host `host.docker.internal`, port 502. Szczegóły w README.
- DO ZROBIENIA: uruchomić na Windows, dodać integrację w HA, spiąć z panelem Energia; docelowo automatyzacja „ładowanie nadwyżką PV" (eksport licznika > próg → switch ładowarki z xtend_tuya).

## 6. Źródła

- https://github.com/user2684/imou_life (HACS imou_life)
- https://github.com/Imou-OpenPlatform/Imou-Home-Assistant (oficjalna)
- https://imou-life.readthedocs.io/en/latest/INSTALLATION.html
- https://www.home-assistant.io/integrations/onvif/
- https://www.ispyconnect.com/camera/imou (URL-e RTSP wg modeli)
- https://community.home-assistant.io/t/imou-life-cloud-integration/462439
