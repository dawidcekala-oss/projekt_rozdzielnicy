# Udawane urzadzenie MQTT (styl Shelly/Tasmota) - narzedzia
Projekt AMPERE_POINT - 2026-07-06. Wszystkie komendy: PowerShell na Windows.

## 1. Broker Mosquitto (kontener)
```
mkdir C:\mosquitto
notepad C:\mosquitto\mosquitto.conf     # wklej 2 linie ponizej i zapisz
```
Zawartosc pliku mosquitto.conf:
```
listener 1883
allow_anonymous true
```
Start brokera:
```
docker run -d --name mosquitto --restart=unless-stopped -p 1883:1883 -v "C:\mosquitto\mosquitto.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto
```

## 2. Integracja MQTT w HA
Ustawienia -> Urzadzenia i uslugi -> Dodaj integracje -> MQTT
Broker: `host.docker.internal`, port `1883`, bez loginu (broker testowy!).

## 3. Urzadzenie pojawia sie samo (MQTT Discovery)
Gniazdko z pomiarem mocy - dwa ogloszenia konfiguracyjne (retain!):
```
docker exec mosquitto mosquitto_pub -t "homeassistant/switch/sym_gniazdko/config" -r -m '{"name":"Symulowane gniazdko","uniq_id":"sym_gniazdko_1","cmd_t":"sym/gniazdko/set","stat_t":"sym/gniazdko/state","dev":{"ids":["sym_gniazdko"],"name":"Symulowane gniazdko MQTT","mf":"AMPERE POINT (sym)"}}'

docker exec mosquitto mosquitto_pub -t "homeassistant/sensor/sym_gniazdko_moc/config" -r -m '{"name":"Symulowane gniazdko moc","uniq_id":"sym_gniazdko_moc_1","stat_t":"sym/gniazdko/moc","unit_of_meas":"W","dev_cla":"power","stat_cla":"measurement","dev":{"ids":["sym_gniazdko"]}}'
```

## 4. Stany i pomiary (powtarzaj dowolnie)
```
docker exec mosquitto mosquitto_pub -t "sym/gniazdko/state" -r -m "ON"
docker exec mosquitto mosquitto_pub -t "sym/gniazdko/moc" -m "1250"
```

## 5. Podgladaj, co HA wysyla przy klikaniu przelacznika
```
docker exec mosquitto mosquitto_sub -t "sym/gniazdko/set" -v
```
(zostaw okno otwarte i klikaj encje w HA - zobaczysz ON/OFF na zywo)

## Sprzatanie
```
docker exec mosquitto mosquitto_pub -t "homeassistant/switch/sym_gniazdko/config" -r -n
docker exec mosquitto mosquitto_pub -t "homeassistant/sensor/sym_gniazdko_moc/config" -r -n
```
(puste ogloszenie retain kasuje encje z HA)
