@echo off
title Pobieranie zdjec plytki P11
cd /d "%~dp0"
echo Pobieram zdjecia z linkow .url do tego folderu...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ProgressPreference='SilentlyContinue';" ^
 "Get-ChildItem -Path $PWD -Filter *.url | ForEach-Object {" ^
 "  $u = ((Get-Content $_.FullName | Where-Object { $_ -like 'URL=*' }) -replace '^URL=','');" ^
 "  $out = Join-Path $PWD $_.BaseName;" ^
 "  try { Invoke-WebRequest -Uri $u -OutFile $out -UseBasicParsing; Write-Host ('OK   ' + $_.BaseName) -ForegroundColor Green }" ^
 "  catch { Write-Host ('BLAD ' + $_.BaseName + ' -> ' + $_.Exception.Message) -ForegroundColor Red }" ^
 "}"
echo.
echo Zakonczono. Napisz w czacie: gotowe
pause
