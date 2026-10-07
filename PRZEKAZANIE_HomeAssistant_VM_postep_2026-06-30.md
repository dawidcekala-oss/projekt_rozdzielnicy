# PRZEKAZANIE / POSTĘP — Home Assistant na VirtualBox (sesja 2026-06-30, ~15:40)

> Plik do **wznowienia** instalacji w nowej rozmowie Cowork z podpiętym folderem `AMPERE_POINT`.
> Uzupełnia `PRZEKAZANIE_HomeAssistant_VM_od_zera_2026-06-30.md`. Czytaj oba.

---

## STAN NA TERAZ (co już zrobione)
- **VM utworzona** w VirtualBox: nazwa `HomeAssistant`, OS = Oracle Linux (64-bit),
  **RAM 4096 MB**, **2 CPU**, **EFI włączone**, dysk **istniejący** `haos_ova-18.0.vdi`
  (z Pulpitu, SATA Port 0, Normalny 32 GB). NIE tworzono nowego dysku.
- **Sieć — uwaga, zmienione względem runbooka:** karta przewodowa (Intel Ethernet I219-LM)
  **NIE dostała adresu DHCP** (kabel najpewniej nie był wpięty — `enp0s3` miał puste `address: []`,
  `supervisor_internet: false`). Za zgodą użytkownika przełączono **mostek (bridged) na Wi-Fi
  (Intel Wi-Fi 6 AX201)**. Po `host reboot` interfejs dostał adres:
  **`enp0s3 = 192.168.0.132/24`** — internet działa.
- **HA Core SIĘ POBIERA.** `core info` pokazuje `version: landingpage`,
  `version_latest: 2026.6.4`, obraz `ghcr.io/home-assistant/qemux86-64-homeassistant`.
  `supervisor logs` = powtarzające się `Home Assistant Core installation in progress`,
  **bez** timeoutów do ghcr.io i **bez** błędów git (czyli zdrowo, w przeciwieństwie do poprzedniej próby).
- **PROBLEM: pobieranie przez mostek Wi-Fi jest bardzo wolne** — po ~1 h nadal `landingpage`.
  HA OS nie pokazuje % postępu, więc nie ma dokładnego ETA.
- VM **zostawiona WŁĄCZONA**, żeby pobieranie się dokończyło. **Nie wyłączać twardo.**

## CO ZOSTAŁO DO ZROBIENIA
1. Doczekać aż `core info` → `version` zmieni się z `landingpage` na **`2026.6.4`** (numer).
2. Wejść na **`http://homeassistant.local:8123`** lub **`http://192.168.0.132:8123`** → onboarding.
3. **Onboarding (konto/hasło) robi użytkownik** — asystent nie zakłada kont ani nie wpisuje haseł.
4. Dalej wg `AMPERE_POINT_integracja_SUN2000_HomeAssistant_Q_v1.pdf`:
   HACS → **huawei_solar** (Modbus TCP / SDongle) + **xtend_tuya / tuya_local** (ładowarka Q)
   → automatyzacja ładowania nadwyżką PV.

## ZALECENIE (jak skończyć szybko)
Najszybciej: **wpiąć kabel Ethernet** i przełączyć mostek z powrotem na kartę przewodową.
Na kablu reszta pobierania powinna zejść w kilka minut zamiast nieprzewidywalnego czekania.
- Okno VM → menu **Urządzenia → Sieć → Ustawienia sieciowe…**
- Pole **Name**: wybierz **Intel(R) Ethernet Connection (13) I219-LM** (zamiast Wi-Fi), OK.
- W konsoli HA: `host reboot` (czysty restart) → po starcie `network info` → sprawdź `enp0s3` ma adres.

## JAK WZNOWIĆ / SPRAWDZIĆ STATUS
1. VirtualBox Manager → zaznacz `HomeAssistant` → **Pokaż** (NIE `open_application virtualboxvm`).
2. Kliknij w czarną konsolę (przechwyci klawiaturę; zwolnienie = **Right Control**).
3. Wpisz `core info` → patrz na `version`.
   - `landingpage` = nadal trwa; `2026.6.4` = gotowe.
4. `supervisor logs` → ma być „installation in progress” bez timeoutów.
5. Jeśli utknie z błędami (ghcr.io timeout / git corrupt): patrz Krok 3 runbooka
   (`dns options --servers dns://1.1.1.1 --servers dns://8.8.8.8` → `dns restart`
   → `supervisor repair` → `supervisor reload`). **W tej sesji NIE było to potrzebne.**

## UWAGI DO COMPUTER-USE (potwierdzone w tej sesji)
- `type` (schowek) **NIE wchodzi** do konsoli VM — pisać **znak-po-znaku przez `key`**,
  weryfikować zoomem przed Enter; literówka = ctrl+u i powtórz.
- Po `host reboot` Wi-Fi mostek **zadziałał** (DHCP 192.168.0.132). Wcześniej runtime-zmiana
  adaptera zostawiła interfejs w stanie `enabled: false / method: disabled` — naprawił to dopiero restart.
- **Uśpienie hosta:** nie udało się ustawić — okno Ustawień Windows (systemsettings.exe)
  jest maskowane/zasłaniane przez okno VirtualBox. **Zlecić użytkownikowi:**
  Ustawienia → System → Zasilanie → uśpienie przy zasilaniu = **Nigdy** (żeby nie przerwać pobierania).
- Maksymalizacja okna VM ułatwia odczyt konsoli (prompt `ha >` jest na dole).
