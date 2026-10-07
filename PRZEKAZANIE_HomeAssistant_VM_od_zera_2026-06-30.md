# PRZEKAZANIE / RUNBOOK — Home Assistant na VirtualBox od zera
**(stan na 2026-06-30; kontekst: integracja z falownikiem Huawei SUN2000 i ładowarką AMPERE POINT serii Q)**

> **Jak użyć:** otwórz ten plik na początku nowej rozmowy w Cowork z podpiętym folderem `AMPERE_POINT` (albo wklej jego treść). To instrukcja dla asystenta, żeby od razu zabrać się za postawienie HA od zera.

---

## Instrukcja dla asystenta (przeczytaj najpierw)
Masz postawić **Home Assistant od zera** na maszynie wirtualnej **VirtualBox** (host: Windows, laptop Lenovo) i docelowo zintegrować go z falownikiem Huawei SUN2000 oraz ładowarką serii Q. 

Punkt wyjścia (ustalony z użytkownikiem):
- VirtualBox jest **zainstalowany**.
- Na **Pulpicie** leży świeży plik dysku HAOS (np. `haos_ova-XX.0.vdi`, ewentualnie `.ova`).
- Reszta po poprzedniej, nieudanej próbie została **usunięta**.

Działaj krok po kroku. Sterowanie pulpitem na Windows ma ograniczenia (sekcja „Uwagi do computer-use”) — w razie potrzeby proś użytkownika o kliknięcia UAC i komendy w terminalu.

## Cel końcowy
Działający HA z **HACS** i integracjami: **huawei_solar** (Modbus TCP przez SDongle) oraz **xtend_tuya / tuya_local** (ładowarka Q), plus automatyzacja **ładowania nadwyżką PV**. Pełny opis i źródła są w tym folderze:
- `AMPERE_POINT_integracja_SUN2000_HomeAssistant_Q_v1.pdf`
- `AMPERE_POINT_zrodla_integracja_v1.pdf`

---

## Krok 1 — utwórz maszynę w VirtualBox
**Jeśli na Pulpicie jest `.ova`:** VirtualBox → Plik → *Importuj urządzenie wirtualne* → wskaż `.ova` → Importuj. Potem zweryfikuj EFI i sieć (niżej).

**Jeśli plik to `.vdi` (sam dysk):** VirtualBox → *Nowa*:
- Nazwa: `HomeAssistant`; Typ: Linux; Wersja: `Oracle Linux (64-bit)` (lub „Other Linux 64-bit”).
- Pamięć: min. **2048 MB** (zalecane 4096); Procesory: min. **2**.
- Dysk: **„Użyj istniejącego pliku dysku”** → wskaż `.vdi` z Pulpitu (NIE twórz nowego).
- Po utworzeniu: Ustawienia → System → Płyta główna → **zaznacz „Włącz EFI”** (HAOS wymaga EFI).
- Ustawienia → Sieć → Karta 1 → **„Mostkowana karta sieciowa” (Bridged)**, a w polu „Nazwa” wybierz **kartę przewodową (ethernet), nie Wi‑Fi** — Wi‑Fi było wąskim gardłem.
- Uruchom („Pokaż”/Start).

## Krok 2 — pierwszy boot i instalacja Core
Po starcie HAOS sam pobiera Home Assistant Core. Na konsoli zobaczysz `Home Assistant Core: landingpage` — to znaczy, że Core jeszcze się instaluje (obraz ~1,5–2 GB).
- **Nie wyłączaj VM** w trakcie (twarde wyłączenie psuje sklep — patrz „Co poszło źle”).
- **Host nie może zasnąć**: Windows → „Zasilanie i uśpienie” → *Uśpienie (przy zasilaniu)* = **Nigdy**.
- Daj czas. Po pobraniu nagłówek zmieni się z `landingpage` na numer wersji, a `http://homeassistant.local:8123` wpuści do onboardingu.

## Krok 3 — jeśli utknie na `landingpage` (to się zdarzyło ostatnio)
Objawy w `supervisor logs`: `connection timed out` do `ghcr.io` + `Retrying`, albo (po twardym wyłączeniu) błędy git `object corrupt/empty` i `Can't load data from repository core`.

Naprawa w konsoli `ha >` — **w tym CLI nie trzeba pisać „ha” przed komendą**:
1. `dns options --servers dns://1.1.1.1 --servers dns://8.8.8.8`
2. `dns restart`
3. `supervisor repair`  ← odbudowuje uszkodzony sklep, czyści stare kontenery/sieci
4. `supervisor reload`
5. Kontrola: `core info` → pole `version` (`landingpage` = jeszcze trwa; numer = gotowe). `version_latest` = cel.
6. Podgląd: `supervisor logs` → ma być „installation in progress” **bez** timeoutów.

Jeśli mimo to po ~20 min **na kablu** dalej `landingpage` → czysta reinstalacja (nowy obraz) albo wariant Docker (niżej).

## Co poszło źle ostatnio (żeby nie powtórzyć)
Poprzednia VM utknęła na `landingpage`, bo: (a) pobieranie Core z `ghcr.io` **timeoutowało przez niestabilne Wi‑Fi**, oraz (b) VM została **twardo wyłączona** (host zasnął), co uszkodziło sklep Supervisora (puste/uszkodzone obiekty git). Po `supervisor repair` + DNS `1.1.1.1` instalacja ruszyła bez błędów, ale pełzła przez Wi‑Fi. **Wniosek: kabel + brak usypiania + cierpliwość, i nigdy nie wyłączać VM twardo.**

## Uwagi do computer-use (oszczędź sobie czasu)
- Wpisywanie do konsoli VM bywa zawodne: fokus wraca do okna Claude i gubi znaki. Pisz **znak‑po‑znaku przez `key`**, **weryfikuj zoomem PRZED Enterem**; jak się rozjedzie — `ctrl+u` i powtórz.
- `type` (przez schowek) **NIE wchodzi** do konsoli Linuksa (brak współdzielenia schowka z TTY) — używaj `key`.
- Konsolę VM przywołujesz: VirtualBox Manager → zaznacz `HomeAssistant` → **„Pokaż”**. NIE rób `open_application "Virtualboxvm"` (odpala pusty proces i błąd „Musisz określić maszynę…”).
- Nazwy do `request_access`: VirtualBox = **„Oracle VirtualBox”**; okno działającej VM = **„virtualboxvm.exe”**; Ustawienia Windows = **„systemsettings.exe”**. Windows potrafi trzymać okno VirtualBox na wierzchu i blokować Ustawienia — wyłączenie usypiania bywa szybciej zlecić użytkownikowi.
- Terminale (PowerShell/Terminal) są w tierze „tylko klik” — **nie wpiszesz w nie komend**; przeglądarka jest „tylko do oglądania”. UAC/instalatory z prawami administratora są dla computer-use niedostępne.

## Wariant alternatywny — Docker (Home Assistant Container)
Jeśli HAOS dalej sprawia problemy: HA w kontenerze przez **Docker Desktop (WSL2)**. Wystarcza do huawei_solar i xtend_tuya/tuya_local (HACS instalowany ręcznie). **UWAGA:** instalacja wymaga praw administratora (UAC), komend w terminalu i restartów — Claude NIE wykona tego w pełni sam; trzeba prowadzić użytkownika (np. tryb nauki).

Skrót kroków: `wsl --install` (admin, restart) → instalacja Docker Desktop (WSL2 backend, restart) → folder `C:\HomeAssistant\config` → `docker-compose.yml` (niżej) → `docker compose up -d` → `http://localhost:8123` → HACS ręcznie (`docker exec -it homeassistant bash` → `wget -O - https://get.hacs.xyz | bash -` → `docker restart homeassistant`).

`docker-compose.yml`:
```yaml
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    environment:
      - TZ=Europe/Warsaw
    volumes:
      - "C:/HomeAssistant/config:/config"
    ports:
      - "8123:8123"
    restart: unless-stopped
```
Ograniczenia na Windows: brak `network_mode: host`, ograniczone auto‑wykrywanie mDNS, brak łatwego przekazania pendrive'a Zigbee/Z‑Wave. Połączenia wychodzące (Modbus do falownika, Tuya) działają normalnie.

## Weryfikacja końcowa
- `core info` → `version` = numer (nie `landingpage`).
- `http://homeassistant.local:8123` lub `http://<IP-VM>:8123` → onboarding / panel.
- Dalej: HACS → **huawei_solar** + **xtend_tuya/tuya_local** → konfiguracja wg `AMPERE_POINT_integracja_SUN2000_HomeAssistant_Q_v1.pdf`.
