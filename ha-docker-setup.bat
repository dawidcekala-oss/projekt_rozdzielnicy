@echo off
echo === Home Assistant (Docker) - konfiguracja ===
echo.
echo Sprawdzam, czy Docker dziala...
docker version >nul 2>&1
if errorlevel 1 (
  echo [BLAD] Docker nie odpowiada. Uruchom Docker Desktop, poczekaj az bedzie "running", potem odpal ten plik ponownie.
  pause
  exit /b 1
)
if not exist "C:\HomeAssistant\config" mkdir "C:\HomeAssistant\config"
echo Usuwam stary kontener (jesli istnial)...
docker rm -f homeassistant >nul 2>&1
echo Uruchamiam Home Assistant (pierwszy start pobiera obraz)...
docker run -d --name homeassistant --restart=unless-stopped -e TZ=Europe/Warsaw -v "C:\HomeAssistant\config:/config" -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable
if errorlevel 1 (
  echo [BLAD] Nie udalo sie uruchomic kontenera. Sprawdz, czy Docker Desktop dziala.
  pause
  exit /b 1
)
echo.
echo GOTOWE. Za ~1-2 min otworz:  http://localhost:8123
echo Nastepnie uruchom:  ha-docker-hacs.bat  (instalacja HACS)
pause
