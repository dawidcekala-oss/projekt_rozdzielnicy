# Home Assistant w Dockerze (Windows) — instrukcja + gotowe skrypty
**2026-07-01. Powód: instalacja HAOS w VirtualBox pobierała Core skrajnie wolno — dławi wirtualna karta sieciowa VM (most na Wi‑Fi), nie internet. Docker Desktop (WSL2) ma wydajną sieć, więc pobieranie będzie szybkie.**

## Podział pracy
- **Claude przygotował** (w tym folderze): `ha-docker-setup.bat` (tworzy kontener HA) i `ha-docker-hacs.bat` (instaluje HACS) oraz tę instrukcję.
- **Ty wykonujesz** kroki wymagające administratora/terminala/restartów (WSL, Docker Desktop) — poniżej dokładnie.

## Krok 1 — WSL2 (silnik Linuksa dla Dockera)
1. Kliknij prawym na **Start** → **Terminal (administrator)** (albo „Windows PowerShell (administrator)"), potwierdź UAC.
2. Wpisz i zatwierdź:
   ```
   wsl --install
   ```
3. Gdy skończy — **zrestartuj komputer**. (Jeśli napisze, że WSL już jest — pomiń restart.)

## Krok 2 — Docker Desktop
1. Pobierz: https://www.docker.com/products/docker-desktop/  (Docker Desktop for Windows).
2. Zainstaluj (zostaw zaznaczony **WSL 2 backend**), potwierdź UAC, w razie potrzeby zrestartuj/zaloguj się.
3. Uruchom **Docker Desktop** i poczekaj, aż w zasobniku ikonka wieloryba przestanie się animować i będzie „**Docker Desktop is running**".

## Krok 3 — uruchom Home Assistant
- Dwuklik na **`ha-docker-setup.bat`** (z tego folderu). Skrypt utworzy `C:\HomeAssistant\config` i wystartuje kontener HA.
- Obraz pobiera się przy pierwszym starcie (przez WSL2 — szybko). Po ~1–2 min otwórz w przeglądarce:
  **http://localhost:8123**  → ekran powitalny (onboarding).
- Z innych urządzeń w LAN: `http://<IP-tego-Windowsa>:8123`.

## Krok 4 — HACS + integracje
- Dwuklik na **`ha-docker-hacs.bat`** → zainstaluje HACS i zrestartuje kontener.
- W HA: **Ustawienia → Urządzenia i usługi → Dodaj integrację → HACS** (autoryzacja przez `github.com/login/device`).
- W HACS pobierz: **Huawei Solar** oraz (dla ładowarki Q) **xtend_tuya** lub **tuya_local**. Dalsza konfiguracja: `AMPERE_POINT_integracja_SUN2000_HomeAssistant_Q_v1.pdf` w tym folderze.

## Uwagi
- Ręczny odpowiednik `ha-docker-setup.bat` (gdybyś wolał wpisać w terminalu):
  ```
  mkdir C:\HomeAssistant\config
  docker run -d --name homeassistant --restart=unless-stopped -e TZ=Europe/Warsaw -v "C:\HomeAssistant\config:/config" -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable
  ```
- Sieć Docker Desktop na Windows: brak host-mode i ograniczone auto‑wykrywanie mDNS. Połączenia wychodzące (Modbus TCP do falownika, Tuya) działają normalnie — dla Twoich integracji to wystarcza.
- Kopia zapasowa = skopiuj folder `C:\HomeAssistant\config`.
- Starą maszynę HAOS w VirtualBox możesz wyłączyć (prawy klik na VM → Zamknij → Wyłącz). Dysk i runbook `PRZEKAZANIE_HomeAssistant_VM_od_zera_2026-06-30.md` zostają, gdybyś kiedyś chciał wrócić do VM (wtedy ustaw sieć na **NAT**, nie most — to usuwa ten dławik).
