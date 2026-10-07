# Mapowanie: pola miejsca na moduł → nóżki procesora, płytka X2Q322_K_V4 (260703)

Procesor: naklejka „X2Q311OW OTA V22”, LQFP64, rodzina STM32F103 / GD32F103 / GD32F303 (rozpoznana po nóżkach zasilania).
Konwencja użytkownika: u = góra, d = dół (numeracja od lewej), l = lewo, p = prawo (numeracja od dołu); widok z naklejką czytelną, miejsce na moduł po prawej.
Przeliczenie na numer standardowy (nóżka 1 = d1): dN → N, pN → 16+N, uN → 49−N, lN → 65−N.

| Pole modułu | Nóżki procesora (pomiar użytkownika) | Numer standardowy |
| --- | --- | --- |
| 8 VCC | d13, p16, u1, d1, l1, p3 | 13, 32, 48, 1, 64, 19 |
| 7 A_4 | brak | — |
| 6 A_3 | brak | — |
| 5 A_2 | brak | — |
| 4 A_11 | brak | — |
| 3 EN | brak | — |
| 2 A_7 | brak | — |
| 1 NC | brak | — |
| 9 GND | p15, p2, d12, l2, u2 | 31, 18, 12, 63, 47 = wszystkie nóżki masy według karty |
| 10 A_12 | brak | — |
| 11 A_16 | brak | — |
| 12 A_17 | brak | — |
| 13 A_18 | brak | — |
| 14 A_19 | brak | — |
| 15 RXD | d16 | 16 = PA2, USART2_TX (w nazewnictwie GD32: USART1_TX), nadawanie procesora |
| 16 TXD | p1 | 17 = PA3, USART2_RX (w nazewnictwie GD32: USART1_RX), odbiór procesora |

Przewidywanie PB10/PB11 (p13/p14) się nie sprawdziło; port to PA2/PA3.
