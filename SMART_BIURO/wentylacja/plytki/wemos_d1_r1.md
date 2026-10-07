# WeMos D1 R1 (ESP8266) — dokumentacja płytki

Płytka z układem WiFi ESP8266 w obudowie wielkości Arduino UNO. W projekcie pełni rolę
**mózgu sondy**: wysyła ramki do klimatyzatora, odbiera odpowiedzi i przekazuje wszystko
przez WiFi (sieć `AmperePoint`, 2,4 GHz) do komputera.

## Najważniejsza pułapka: potrójne opisy pinów

Każdy pin na listwie ma nadrukowane **2–3 nazwy naraz** (spadek po zgodności z UNO),
a część nazw **powtarza się w dwóch miejscach listwy**. W tym projekcie przez tę
niejednoznaczność przewody sygnałowe trafiły początkowo na piny `RX←D0`/`TX→D1`
(sprzętowy port szeregowy, zajęty przez USB) zamiast na właściwe — i sonda tygodniami
„nadawała w pustkę". Obowiązuje zasada: **pin identyfikujemy po pełnym nadruku**, nie po
pojedynczej literce z kodu.

## Piny używane w projekcie

| Nadruk na płytce | GPIO (w kodzie) | Rola w sondzie |
|---|---|---|
| `D12/MISO/D6` | GPIO12 | **nadawanie** → żyła „TXD" złącza CN2 bramki |
| `D13/SCK/D5` | GPIO14 | **odbiór** ← żyła „RXD" CN2, przez dzielnik napięcia |
| `D11/MOSI/D7` | GPIO13 | **klucz nadawania** → żyła TXP (żółta) CN2 |
| `GND` (kilka pinów) | — | masa wspólna całego układu + żyła RXP (biała) CN2 |
| `5V` (dwa piny) | — | zasilanie bramki (+5V na CN2) |

Uwaga: piny `D11/MISI`, `D12/MISO`, `D13/SCK` w dalszej części listwy to **fizycznie te
same sygnały** co `D11/MOSI/D7`, `D12/MISO/D6`, `D13/SCK/D5` — płytka dubluje wyprowadzenia.
Można używać dowolnego z pary.

## Zasilanie — trzy drogi, jedna zakazana

| Droga | Status | Uwagi |
|---|---|---|
| micro-USB | ✅ podstawowa | 5 V z ładowarki/komputera; zasila też bramkę przez pin `5V` |
| gniazdo jack (okrągłe) | ✅ działa | wewnętrzna przetwornica obniża napięcie |
| pin `VIN` | ⚠️ tylko z jackiem | **`VIN` jest MARTWY przy zasilaniu z USB** — działa wyłącznie jako wejście współdzielone z jackiem |
| pin `VIN` z +12 V portu klimatyzatora | ❌ **ZAKAZANE** | blokuje start klimatyzatora — opis w raporcie, rozdz. „Incydent zasilania" |

## Ograniczenia elektryczne

- Logika **3,3 V** — sygnał 5 V z bramki musi przejść przez dzielnik napięcia
  (u nas: 3,3 kΩ szeregowo + 6,5 kΩ do masy → ~3,3 V na pinie `D13/SCK/D5`).
- Programowy port szeregowy (SoftwareSerial) przy włączonym WiFi gubi ok. 9% ramek —
  akceptowalne w sondzie, w wersji docelowej lepszy ESP32 ze sprzętowym UART.

## Wgrywanie firmware

- Narzędzie: `arduino-cli`, płytka `esp8266:esp8266:d1`, port COM6 (konwerter CH340).
- Kabel USB musi być **4-żyłowy (dane)** — kable „tylko ładowanie" zasilają płytkę,
  ale komputer jej nie widzi.
- Firmware sondy: `test_com_manual\sonda_gree_wemos_wifi\sonda_gree_wemos_wifi.ino`
- Firmware testera biurkowego: `test_com_manual\tester_biurkowy\tester_biurkowy.ino`
