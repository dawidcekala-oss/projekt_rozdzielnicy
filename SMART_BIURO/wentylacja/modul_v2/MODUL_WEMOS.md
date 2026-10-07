# Moduł v2 na WeMos D1 R1 — połączenia i firmware

Wersja zapasowa modułu, na procesorze z dawnej sondy v10. Powstała 16 września 2026,
gdy w module „hala północ" padły kolejno dwa procesory ESP32, a zapasowych nie było.
Płytka modułu, moduł RS485, przetwornica i nadajnik podczerwieni zostają bez zmian —
wymieniamy tylko procesor i sposób, w jaki jest podpięty.

Home Assistant nie wymaga żadnych przeróbek: adresy `/stan` i `/ustaw` odpowiadają tak
samo jak w wersji na ESP32. Zmienia się tylko adres IP modułu, bo procesor ma inny MAC.

---

## 1. Nazwy gniazd na WeMosie

Na listwach D1 R1 jedno gniazdo nosi po kilka nazw naraz, np. `D11/MOSI/D7`. W tabeli
poniżej podaję **pełny nadruk**, bo tylko on jest jednoznaczny: samo „D11" albo samo „D7"
występuje na płytce w dwóch różnych miejscach, a oba prowadzą do tej samej nóżki procesora.

| Nadruk na listwie WeMosa | Do czego służy u nas |
|---|---|
| `D11/MOSI/D7` | wejście magistrali (sprzętowy port szeregowy) |
| `D12/MISO/D6` | wyjście na nadajnik podczerwieni |
| `5V` | zasilanie płytki |
| `3.3V` | zasilanie modułu RS485 |
| `GND` | masa |

Niebieska dioda sygnalizacyjna jest na srebrnym module ESP8266 i nie zajmuje żadnego
gniazda listwy.

---

## 2. Tabela połączeń — pięć przewodów

Przewody męsko-męskie: jeden koniec w otwór podstawki po procesorze ESP32 na płytce
modułu, drugi w gniazdo listwy WeMosa. Otwory podstawki rozpoznajemy po nazwach pinów
ESP32, które w nie wchodziły (rysunek rozkładu: `rozklad_pcb.png`).

| # | Płytka modułu — otwór podstawki po ESP32 | WeMos D1 R1 — nadruk | Co tym płynie |
|---|---|---|---|
| 1 | `VIN` | `5V` | 5 V z przetwornicy — zasilanie procesora |
| 2 | `GND` | `GND` | masa wspólna |
| 3 | `3V3` | `3.3V` | 3,3 V dla modułu RS485 (procesor je wytwarza) |
| 4 | `TX2` | `D11/MOSI/D7` | odebrana magistrala: pole `TXD` modułu RS485 |
| 5 | `D23` | `D12/MISO/D6` | sterowanie nadajnikiem podczerwieni przez 470 Ω |

**Czego nie podłączamy i dlaczego:**

- otwór `RX2` — to wejście nadajnika modułu RS485. Moduł nigdy nie nadaje na magistralę,
  więc ten przewód jest zbędny. Przy okazji znika ryzyko, że procesor zagłuszy jednostkę.
- otwór `D4` — sterowanie kierunkiem modułu RS485. Na tym module pole `EN` jest na stałe
  zwarte drutem do masy, więc podanie tam napięcia z procesora tylko zwierałoby wyjście.
  Odbiornik jest włączony bez udziału procesora.
- otwór `D2` — dioda na płytce ESP32. WeMos ma własną.

---

## 3. Zasilanie

**Wariant podstawowy (zalecany):** przetwornica zostaje ustawiona na 5,00 V i zasila
WeMosa przez gniazdo `5V`, czyli dokładnie tak, jak zasilała ESP32 przez `VIN`.
Nadajnik podczerwieni bierze swoje 5 V z tej samej szyny, jak dotąd.

**Wariant awaryjny:** gdyby płytka nie ruszyła z gniazda `5V`, WeMos ma własną przetwornicę
i wejście `VIN` znoszące 9–24 V — dawna sonda pracowała tak tygodniami prosto z 12 V
klimatyzatora. Wtedy: żółta żyła z wtyku na `VIN`, biała na `GND`, a przetwornica MP1584
zostaje tylko po to, żeby dawać 5 V nadajnikowi podczerwieni.
**Nie wolno zasilać z obu źródeł naraz** — przetwornica walczyłaby z przetwornicą WeMosa.

**Nigdy USB i zasilanie z płytki jednocześnie.** Zasada bez zmian względem ESP32:
przed wpięciem USB odłącz wtyk od klimatyzatora albo przewód zasilania od podstawki.

---

## 4. Pierwsze uruchomienie — kolejność

1. Procesora ESP32 nie ma w podstawce, zasilanie z przetwornicy odłączone.
2. WeMos na USB, wgranie firmware'u (rozdział 6).
3. Sprawdzenie w konsoli USB: baner, wczytane nastawy, adres IP po połączeniu z siecią.
   Konsola milknie w chwili, gdy port szeregowy przejmuje magistralę — tak ma być.
4. USB odłączone. Pięć przewodów wg tabeli z rozdziału 2.
5. Wtyk do gniazda `COM-MANUAL` **przy wyłączonej jednostce**, dopiero potem zasilanie.
6. Kontrola: licznik `ramek_ok` w `/stan` rośnie o mniej więcej 1,25 na sekundę,
   `ramek_zla_suma` stoi, `cisza_na_magistrali_s` = 0.

---

## 5. Czym ta wersja różni się w środku

| Zagadnienie | ESP32 | WeMos D1 R1 |
|---|---|---|
| odbiór magistrali | miękki odbiornik: przerwanie co 52 µs, 16 próbek na bit | **sprzętowy port szeregowy** UART0 przeniesiony na `D11/MOSI/D7`, odwracanie sygnału w układzie |
| nastawy | pamięć NVS | EEPROM emulowany we flashu |
| temperatura rdzenia | `temp_procesora_c` w `/stan` | brak czujnika, pole puste |
| test pinu | podciąganie w górę i w dół | tylko w górę (ESP8266 nie ma podciągania w dół) |
| strażnik zawieszenia | zakładany ręcznie, 90 s | wbudowany w SDK, ok. 3,2 s |
| port OTA | 3232 | **8266** |

**Dlaczego sprzętowy port, a nie miękki odbiornik.** Programowe próbkowanie linii co 52 µs
to dokładnie to, co wywracało sondę v10 przy obciążeniu WiFi i było powodem przejścia na
ESP32 (rozdz. 7.1 dokumentu głównego). ESP8266 ma jednak w układzie UART funkcję
odwracania sygnału, a magistralę Gree trzeba właśnie odwrócić, bo w spoczynku trzyma
linię nisko. Dzięki temu całą robotę wykonuje sprzęt, a program tylko odbiera gotowe bajty.

Port szeregowy jest przenoszony programowo z gniazda `RX<-D0` na `D11/MOSI/D7`. Ubocznym
skutkiem jest to, że po starcie **konsola na USB milknie** — ten sam układ obsługuje obie
role. Podgląd pracy pozostaje przez telnet (port 23), stronę modułu i `/stan`.

**Punkty diagnostyczne**, które w tej wersji nie istnieją: `/echo`, `/nadawaj`, `/kierunek`
oraz test pętli zwrotnej w `/diag`. Wszystkie wymagały sterowania kierunkiem modułu RS485,
a tego przewodu nie ma. `/diag` sprawdza teraz to, co sprawdzić się da: czy na linii coś
się dzieje, czy wyjście odbiornika nią steruje i co pokazują liczniki portu.

---

## 6. Wgrywanie

Pierwszy raz kablem USB (płytka odłączona od zasilania modułu):

```
arduino-cli compile --fqbn esp8266:esp8266:d1 --output-dir build_wemos firmware\modul_v2_wemos
arduino-cli upload  --fqbn esp8266:esp8266:d1 -p COMx --input-dir build_wemos
```

Kolejne wersje przez WiFi, **portem 8266** (w modułach na ESP32 był 3232):

```
espota.exe -i <IP modułu> -I <IP laptopa> -p 8266 -f build_wemos\modul_v2_wemos.ino.bin -r
```

Numer egzemplarza podaje się przy kompilacji; bez flagi powstaje `modul-gree-2`:

```
--build-property "compiler.cpp.extra_flags=-DMODUL_NR=4"
```

---

## 7. Uwagi praktyczne

- **WeMos D1 R1 jest wielkości Arduino Uno** (około 68 × 53 mm), czyli wyraźnie większy
  od ESP32 DevKita. Do dotychczasowej puszki się nie zmieści — trzeba większej obudowy
  albo innego mocowania.
- **Izolacja od metalu obowiązuje tym bardziej.** Dwa procesory ESP32 padły w tym module
  przy zamykaniu metalowej obudowy; płytka WeMosa ma odsłonięte luty na całym spodzie.
  Podkładka z tworzywa pod płytką, dystanse i klej na gorąco na spód przetwornicy oraz
  na lut żółtej żyły.
- **Po wymianie procesora zmienia się adres IP**, bo MAC jest inny. Trzeba poprawić sześć
  adresów w `configuration.yaml` Home Assistanta (zamieniać całe `http://<ip>/`) i zrobić
  rezerwację w routerze.
- Nadajnik podczerwieni ma dostawać 100 mA w impulsie z szyny 5 V. Przy zasilaniu wariantem
  awaryjnym (12 V na `VIN`) szyna 5 V nadal musi pochodzić z przetwornicy MP1584.
