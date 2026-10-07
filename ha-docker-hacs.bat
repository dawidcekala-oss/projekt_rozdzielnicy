@echo off
echo === Instalacja HACS w kontenerze Home Assistant ===
docker exec homeassistant bash -c "wget -O - https://get.hacs.xyz | bash -"
if errorlevel 1 (
  echo [BLAD] Nie udalo sie. Upewnij sie, ze kontener 'homeassistant' dziala (ha-docker-setup.bat).
  pause
  exit /b 1
)
docker restart homeassistant
echo.
echo HACS zainstalowany. W Home Assistant:
echo   Ustawienia - Urzadzenia i uslugi - Dodaj integracje - HACS
echo   (autoryzacja przez github.com/login/device)
echo Potem w HACS pobierz: Huawei Solar oraz xtend_tuya lub tuya_local.
pause
