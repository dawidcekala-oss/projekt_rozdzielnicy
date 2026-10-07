| Co | Oczekiwane | Wynik | Szczegol |
| --- | --- | --- | --- |
| konfiguracja: ble | zostaje | OK |  |
| konfiguracja: bthome | zostaje | OK |  |
| konfiguracja: cloud | zostaje | OK |  |
| konfiguracja: modbus | zostaje | OK |  |
| konfiguracja: mqtt | zostaje | OK |  |
| konfiguracja: service:0 | zostaje | OK |  |
| konfiguracja: sys | zostaje | OK |  |
| konfiguracja: wifi | zostaje | OK |  |
| konfiguracja: ws | zostaje | OK |  |
| pamiec klucz-wartosc | zostaje | OK | 2 -> 2 kluczy |
| harmonogram | zostaje | OK | 1 -> 1 zadan |
| webhooki | zostaja | OK | 5 -> 5 |
| usluga: wersja i kompilacja | zostaje | OK | 13109-3815 -> 13109-3815 |
| usluga: pliki (sha256) | zostaja | OK |  |
| usluga: dziala | dziala | OK | stan running, komunikaty None |
| urzadzenie: id, firmware, token produktu | zostaje | OK | jti 001094000005 -> 001094000005 |
| definicje pol | zostaja | OK | 15 -> 15 pol |
| wartosc boolean:200 (state), zapamietywana | zostaje | ZMIANA | False -> True |
| wartosc enum:200 (mode) | od sterownika albo domyslna | - | charger_free -> charger_free |
| wartosc enum:201 (cp_state) | od sterownika albo domyslna | - | controlpi_12v -> controlpi_12v |
| wartosc enum:202 (work_mode) | od sterownika albo domyslna | - | charge_now -> charge_now |
| wartosc number:200 (current_limit), zapamietywana | zostaje | OK | 11 -> 11 |
| wartosc number:201 (session_duration) | od sterownika albo domyslna | - | 0 -> 0 |
| wartosc number:202 (session_energy) | od sterownika albo domyslna | - | 0 -> 0 |
| wartosc number:203 (energy_limit) | od sterownika albo domyslna | - | 0 -> 0 |
| wartosc number:204 (last_session_energy) | od sterownika albo domyslna | - | 0 -> 0 |
| wartosc number:205 (temperature) | od sterownika albo domyslna | - | 21 -> 21 |
| wartosc number:206 (window_end) | od sterownika albo domyslna | - | 0 -> 0 |
| wartosc number:207 (window_start) | od sterownika albo domyslna | - | 0 -> 0 |
| wartosc text:200 (controller_version) | od sterownika albo domyslna | - | V1 -> V1 |
| wartosc text:201 (faults) | od sterownika albo domyslna | - | none -> none |
| czas pracy | od zera | OK | 467 -> 91 s |
| godzina | z serwera czasu | OK | synchronizacja 1790759101 |
| polaczenie Cloud | jak przed | OK | {'connected': False} -> {'connected': False} |
| polaczenie MQTT | jak przed | OK | {'connected': True} -> {'connected': True} |
| polaczenie WS | jak przed | OK | {'connected': False} -> {'connected': False} |

zmian wbrew oczekiwaniu: 1
