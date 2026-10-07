# Kalibracja temperatur — jak czytać odczyty jednostki

## Wynik: przelicznik to „surowy bajt minus 100 = stopnie Celsjusza"

Ramka rozgłoszeniowa jednostki niesie dwie temperatury jako pojedyncze bajty:

| Bajt ramki | Czujnik | Przykład |
|---|---|---|
| `[9]` | **powietrze powrotne** (czujnik ROOM) — to, według czego jednostka reguluje | 119 → **19 °C** |
| `[10]` | **wymiennik** (czujnik TUBE) — parownik/skraplacz | 106 → **6 °C** |

## Dowód rozstrzygający (nie wymagał żadnego termometru)

Kandydatów było dwóch: odjęcie 100 albo odjęcie 104. Rozstrzygnął je 40-minutowy pomiar
ciągły przy nastawie **16 °C**:

| | 15:30 | 16:10 |
|---|---|---|
| bajt „powietrze powrotne" | 120 | 119 |
| bajt „wymiennik" | 106 | 106 |
| sprężarka | pracuje | **pracuje nieprzerwanie** |

Sprężarka nie wyłączyła się ani razu. Jednostka przerywa chłodzenie dopiero wtedy, gdy
powietrze powrotne osiągnie nastawę — skoro chłodziła bez przerwy, mierzone powietrze
musiało być **cieplejsze niż 16 °C**.

- **odjęcie 100** → 19–20 °C, powyżej nastawy → chłodzenie słusznie trwa. **Zgodne.**
- odjęcie 104 → 15–16 °C, na poziomie nastawy lub poniżej → sprężarka musiałaby stanąć.
  **Sprzeczne z obserwacją.**

Potwierdzenie dodatkowe: przy zatrzymanej jednostce, gdy oba czujniki się wyrównają,
najczęstszy odczyt historyczny to **124/124** → 24 °C. Tyle ma sierpniowe biuro przed
włączeniem klimatyzacji. Przy odjęciu 104 wyszłoby 20 °C, co dla sierpnia bez chłodzenia
jest mało prawdopodobne.

## Dlaczego odczyt „kłóci się" z odczuciem w pomieszczeniu

To pozorna sprzeczność — oba wrażenia są prawdziwe naraz:

- **Czujnik siedzi w strumieniu powietrza powrotnego, przy suficie.** Ciepłe powietrze się
  unosi, więc pod sufitem jest najcieplej w całym pomieszczeniu. Stąd 19–20 °C.
- **Człowiek przy biurku siedzi w strumieniu nawiewu**, który przy pracującym chłodzeniu ma
  około 6–10 °C (temperatura wymiennika plus podmieszanie). Stąd wrażenie „jest 16".

Różnica między sufitem a strefą przebywania (stratyfikacja) potrafi w biurze sięgać kilku
stopni — i to właśnie widać w danych.

**Praktyczny wniosek:** encja w Home Assistant pokazuje temperaturę, **według której
jednostka podejmuje decyzje**, a nie tę odczuwaną przy biurku. To cenne — wiadomo, dlaczego
klimatyzator chłodzi dalej mimo osiągniętego komfortu. Jeśli potrzebna jest temperatura
strefy przebywania, dokłada się osobny czujnik przy biurku i porównuje obie wartości.

## Czego NIE da się użyć jako punktu odniesienia

- **Wyświetlacz kasetonu** pokazuje **nastawę**, nie temperaturę zmierzoną — to ta sama
  liczba, którą ustawiono pilotem.
- **Przycisk TEMP** na tym pilocie **włącza i wyłącza regulację temperatury**; nie przełącza
  trybu wyświetlania (w odróżnieniu od niektórych innych pilotów Gree).

## Gdyby trzeba było poprawić przelicznik

Stała `OFFSET_TEMP` w pliku `test_com_manual\sonda_gree_v5\sonda_gree_v5.ino`. Po zmianie:
kompilacja i wgranie **przez WiFi**, bez zdejmowania sondy:

```
arduino-cli compile --fqbn esp8266:esp8266:d1 --output-dir build_v5 sonda_gree_v5
python espota.py -i 192.168.0.172 -p 8266 -f build_v5\sonda_gree_v5.ino.bin -r
```
