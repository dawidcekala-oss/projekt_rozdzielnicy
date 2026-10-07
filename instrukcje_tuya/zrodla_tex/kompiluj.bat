@echo off
REM Kompilacja obu instrukcji Tuya - AMPERE POINT
REM Wymaga XeLaTeX (MiKTeX lub TeX Live). Uruchamiac z tego katalogu.

cd /d "%~dp0"

where xelatex >nul 2>nul
if errorlevel 1 (
  echo.
  echo BLAD: nie znaleziono xelatex. Zainstaluj MiKTeX ze strony miktex.org
  echo i upewnij sie, ze katalog z xelatex.exe jest w zmiennej PATH.
  echo.
  pause
  exit /b 1
)

for %%F in (AMPERE_POINT_instrukcja_blokada_godzin_v1 AMPERE_POINT_poradnik_automatyzacje_tuya_v1) do (
  echo.
  echo === Kompiluje %%F ===
  xelatex -interaction=nonstopmode "%%F.tex" >nul
  xelatex -interaction=nonstopmode "%%F.tex" >nul
  if exist "%%F.pdf" (echo     gotowe: %%F.pdf) else (echo     BLAD - sprawdz %%F.log)
)

echo.
echo Sprzatanie plikow posrednich...
del /q *.aux *.log *.out 2>nul

echo.
echo Zakonczono.
pause
