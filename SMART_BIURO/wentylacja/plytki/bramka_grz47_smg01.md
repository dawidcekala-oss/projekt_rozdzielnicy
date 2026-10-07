# Bramka Gree ZTS47 / Sinclair SMG-01 (płytka GRZ47-G) — dokumentacja

Fabrycznie: bramka Modbus do jednostek U-Match, wpinana kablem w gniazdo COM-BMS płyty
głównej. Nasze kasetony (płyta GRZ4M-A3) **nie mają COM-BMS**, więc bramka była bezużyteczna —
do czasu, aż analiza jej wnętrza pokazała, że to w istocie **prosty konwerter sygnału
szeregowego (UART, 5 V) na magistralę różnicową RS485** — dokładnie ten element, którego
brakowało sondzie. Na płytce **nie ma procesora** — cała „inteligencja" Modbus siedzi w płycie
głównej jednostki, a bramka tylko tłumaczy poziomy elektryczne. Dzięki temu można ją napędzać
własnym kontrolerem.

## Złącze CN2 (białe, wielopinowe) — serce sprawy

Opisy na laminacie: `RXP/TXP  PE/PE  GND  TXD  RXD  +5V`. Trzy kluczowe fakty ustalone
w testach biurkowych 2026-08-22:

### 1. Nazwy TXD/RXD są z perspektywy PŁYTY KLIMATYZATORA, nie bramki

| Żyła wg laminatu | Faktyczna rola | Podłączenie u nas |
|---|---|---|
| `TXD` | **wejście danych do bramki** (to, co płyta główna nadaje) | ← WeMos `D12/MISO/D6` (nadawanie) |
| `RXD` | **wyjście danych z bramki** (to, co płyta miała odbierać) | → dzielnik → WeMos `D13/SCK/D5` (odbiór) |

Podłączenie „po nazwach" (TX do RXD, RX do TXD — jak między dwoma zwykłymi urządzeniami)
jest tu **błędne** i daje całkowitą ciszę.

### 2. Transceiver nie ma automatu kierunku — piny RXP/TXP to włączniki

Układ U5 (14 nóżek, rodzina MAX13089) wymaga zewnętrznego sterowania: osobno włącza się
nadajnik, osobno odbiornik. W oryginale robiła to płyta główna; u nas:

| Żyła | Kolor | Rola | Podłączenie |
|---|---|---|---|
| `RXP` | **biała** | włącznik odbiornika, aktywny przy masie | na stałe do `GND` WeMosa |
| `TXP` | **żółta** | włącznik nadajnika | do WeMos `D11/MOSI/D7` — stan wysoki tylko na czas wysyłania ramki |

Z wiszącymi (niepodłączonymi) RXP/TXP bramka jest **jednocześnie głucha i niema** —
to była główna przyczyna tygodnia ciszy w testach polowych.

### 3. Zasilanie

`+5V` (żyła czerwona) + `GND` — z pinów `5V`/`GND` WeMosa. Pobór znikomy. Diody LED na
płytce nie świecą w tej konfiguracji (sterowane były przez płytę główną) — brak światła
nie oznacza braku zasilania.

## Blaszki (konektory noża) X1–X4 — wyjście na magistralę

| Blaszki | Rola | Nasze podłączenie |
|---|---|---|
| **X1 + X3** (zwarte wewnętrznie) | linia **A** magistrali RS485 | konektor **czarny** → pigtail → pin A gniazda COM-MANUAL |
| **X2 + X4** (zwarte wewnętrznie) | linia **B** | konektor **czerwony** → pigtail → pin B |

Podwójne blaszki służą fabrycznie do łączenia przelotowego wielu urządzeń w jedną magistralę
(druga blaszka pary prowadzi przewód dalej). Zmierzone parametry: nadajnik wystawia
**±4,8 V** różnicy między liniami; odbiornik poprawnie czyta polaryzację (test wstrzyknięcia
5 V / masy wprost na blaszki).

## Czego z bramką nie robić

- Nie podawać na CN2 napięć wyższych niż 5 V.
- Nie zwierać blaszki A z B przy włączonym nadajniku.
- Nie sugerować się nazwami TXD/RXD ani diodami LED — patrz wyżej.
