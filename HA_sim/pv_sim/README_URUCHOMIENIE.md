# Symulator falownika Huawei SUN2000 dla Home Assistant

Serwer Modbus TCP udający falownik **SUN2000-10KTL-M1** (10 kWp, 2 stringi PV,
licznik energii). Pozwala przećwiczyć całą integrację `huawei_solar` w HA
**bez fizycznego sprzętu** — encje, panel Energia, automatyzacje ładowania nadwyżką.

Czysty Python (stdlib) — **niczego nie trzeba instalować pipem**.

## 1. Uruchomienie (Windows, ten sam komputer co HA w Dockerze)

```
cd C:\Users\Lenovo\Desktop\AMPERE_POINT\pv_sim
python sun2000_sim.py
```

- Gdy Windows zapyta o zaporę → **Zezwól** (sieci prywatne).
- Parametry opcjonalne:
  - `--port 502` (domyślny; zmień np. na 5020, jeśli 502 zajęty)
  - `--kwp 10` — moc instalacji
  - `--time-scale 60` — doba mija w 24 minuty (do szybkich testów)
  - `--no-meter` — bez licznika energii
  - `--sunrise 4.8 --sunset 21.0` — godziny „słońca"
- Licznik energii całkowitej zapisuje się do `sun2000_sim_state.json` (przeżywa restart).

Szybki test bez HA (drugie okno terminala):

```
python test_client.py 127.0.0.1 502
```

## 2. Podpięcie w Home Assistant

1. **HACS → wyszukaj „Huawei Solar"** (autor wlcrs) → Pobierz → restart kontenera
   `homeassistant` w Docker Desktop.
2. Ustawienia → Urządzenia i usługi → **Dodaj integrację → Huawei Solar**.
3. Typ połączenia: **Modbus TCP**:
   - Host: `host.docker.internal`  (tak kontener HA widzi Twój Windows)
   - Port: `502` (lub własny)
   - Slave/Device ID: `0` lub `1` (symulator przyjmuje każdy)
   - Tryb: bez podwyższonych uprawnień (read-only).
4. Po chwili pojawi się urządzenie **SUN2000-10KTL-M1** z encjami: moc czynna,
   moc DC, energia dzienna/całkowita, napięcia/prądy faz i stringów PV,
   temperatura, status, licznik (eksport/import) itd.

## 3. Panel Energia (propozycja)

Ustawienia → Pulpity → Energia:
- Produkcja słoneczna: `Daily yield` / energia całkowita falownika,
- Zużycie z sieci / oddanie do sieci: energie licznika (import/eksport).

Po godzinie–dwóch wykresy zaczną się rysować. Z `--time-scale 60` dane
przyrastają szybciej (HA i tak zapisuje w czasie rzeczywistym).

## 4. Automatyzacja „ładowanie nadwyżką PV" (szkic do testów)

Wyzwalacz: wartość liczbowa `sensor.power_meter_active_power` > 3000 W
(eksport ≥ 3 kW) przez 5 min → akcja: `switch.turn_on` ładowarki (encja
z xtend_tuya). Analogicznie wyłączenie przy spadku eksportu < 500 W.

## 5. Ograniczenia symulatora

- Mapa rejestrów odwzorowuje najważniejsze odczyty SUN2000; egzotyczne
  encje mogą być puste/niedostępne — to normalne.
- Brak baterii LUNA2000 i optymalizatorów (celowo; integracja wykrywa to
  poprawnie przez wyjątki Modbus).
- Zapisy (tryb podwyższonych uprawnień) są przyjmowane, ale nie zmieniają
  logiki produkcji.
- Wartości są losowo „chmurzone" — krzywa dobowa sin^1.5 + spacer losowy.

## 6. Pliki

| Plik | Rola |
|---|---|
| `sun2000_sim.py` | symulator (serwer Modbus TCP) |
| `test_client.py` | test odczytów bez HA |
| `sun2000_sim_state.json` | stan liczników (tworzy się sam) |
