# Źródło „Tuya MCU” do odtworzenia po teście łącza

Usunięte z portalu 2026-09-24 na czas testu `test_uart_q11.ts`. ESP32-C3 ma dwa sprzętowe porty szeregowe: port 0 obsługuje USB i log, a port 1 zajmował „Tuya MCU”. Źródło „UART” też chce portu 1, więc firmware odrzucił konfigurację z oboma naraz: `invalid token : xc.uart@2 : uart 1 (code -114)`.

## Hardware → Tuya MCU

| Pole | Wartość |
| --- | --- |
| Name | Q11 MCU |
| Baud Rate | 115200 (ostatnio testowane; wcześniej 9600) |
| TX IO | IO 4 |
| RX IO | IO 5 |

## Data → Datapoints

| DP ID | Name | Type | Mode | Bind to VC | Transform |
| --- | --- | --- | --- | --- | --- |
| 18 | state | Boolean | readwrite | state | None |
| 4 | current_limit | Integer | readwrite | current_limit | None |
| 3 | mode | Enum | readonly | mode | None |
| 1 | total_energy | Integer | readonly | not bound | — |
| 6 | phase_a | Raw | readonly | not bound | — |
| 7 | phase_b | Raw | readonly | not bound | — |
| 8 | phase_c | Raw | readonly | not bound | — |

Po odtworzeniu: usunąć źródło „UART test”, wkleić `script.svc.ts` (v3), zbudować, wgrać.
