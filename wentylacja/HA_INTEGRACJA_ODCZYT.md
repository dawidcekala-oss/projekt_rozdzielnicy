# Integracja odczytowa z Home Assistant — gotowa do wdrożenia

> **DOKUMENT ZASTĄPIONY (2026-08-26).** Obowiązuje `HA_INTEGRACJA.md` / `.pdf`, który
> opisuje odczyt **i sterowanie**. Ten plik zachowano jako zapis stanu sprzed uruchomienia
> sterowania podczerwienią. Ostatnie zdanie („czego jeszcze nie ma: sterowania") jest
> **nieaktualne** — sterowanie działa, tylko nie przez magistralę, lecz przez podczerwień.

Sonda (firmware **v5**) udostępnia stan jednostki pod adresem `http://192.168.0.172/stan`
w formacie JSON. Nie wymaga brokera MQTT ani dodatków — Home Assistant odpytuje ją
wbudowaną integracją `rest`.

Podgląd dla człowieka: `http://192.168.0.172/` (zwykła strona z odczytami).

## Co daje

| Encja | Źródło | Uwaga |
|---|---|---|
| temperatura pomieszczenia | czujnik ROOM jednostki | ten sam, na którym pracuje termostat |
| temperatura wymiennika | czujnik TUBE | pokazuje, czy chłodzenie/grzanie realnie pracuje |
| bieg wentylatora | stan rzeczywisty | stoi / niski / średni / wysoki |
| klapy nawiewu | stan rzeczywisty | otwarte / zamknięte |
| jednostka pracuje | wyliczone z biegu | wentylator ≠ stoi |

Dane odświeżają się co 800 ms po stronie sondy; HA odpytuje co 30 s (do zmiany).

## Konfiguracja — wklej do `configuration.yaml`

```yaml
rest:
  - resource: http://192.168.0.172/stan
    scan_interval: 30
    sensor:
      - name: "Klimatyzacja biuro temperatura"
        value_template: "{{ value_json.temp_pokoj }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
      - name: "Klimatyzacja biuro wymiennik"
        value_template: "{{ value_json.temp_wymiennik }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
      - name: "Klimatyzacja biuro wentylator"
        value_template: "{{ value_json.wentylator }}"
        icon: mdi:fan
    binary_sensor:
      - name: "Klimatyzacja biuro pracuje"
        value_template: "{{ value_json.pracuje }}"
        device_class: running
      - name: "Klimatyzacja biuro klapy"
        value_template: "{{ value_json.klapy_otwarte }}"
        device_class: opening
      - name: "Klimatyzacja biuro sonda online"
        value_template: "{{ value_json.dostepne }}"
        device_class: connectivity
```

Po wklejeniu: **Narzędzia deweloperskie → YAML → Przeładuj encje REST** (albo restart HA).

## Uwaga o adresie IP

Sonda ma teraz adres `192.168.0.172` przydzielony przez router. Warto na routerze
**zarezerwować ten adres dla jej adresu MAC**, żeby nie zmienił się po restarcie — inaczej
encje przestaną się odświeżać.

## Kalibracja temperatury — do potwierdzenia

Kodowanie przyjęte w firmware: **wartość bajtu minus 100 = stopnie Celsjusza**. Hipoteza
opiera się na wiarygodności zakresów (pomieszczenie 20–24 °C, wymiennik spadający do
kilku stopni przy chłodzeniu). Weryfikacja: przycisk **TEMP** na pilocie przełącza
wyświetlacz kasetonu na temperaturę pomieszczenia — jeśli pokaże inną wartość niż encja
w HA, poprawiam stałą `OFFSET_TEMP` w firmware i wgrywam przez WiFi (bez zdejmowania sondy).

## Czego jeszcze nie ma

Sterowania (włącz/wyłącz, nastawa, tryb) — jednostka nie przyjmuje poleceń od
niezarejestrowanego sterownika. Szczegóły i plan odblokowania: `FAZA2_USTALENIA.pdf`.
