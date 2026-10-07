# Dodatkowe dostępne elementy — identyfikacja

| Folder | Co to jest | Przydatność w projekcie |
|---|---|---|
| `UNO\` | Arduino UNO (klon z CH340) | Zapas — może służyć za drugi tester/konwerter USB-serial; tor USB sprawny |
| `nie_wiem\` | **Sterownik silnika krokowego ULN2003** (płytka z wejściami IN1–IN7, 4 diody D1–D4, białe 5-pinowe gniazdo P3 do silnika 28BYJ-48) | W tym projekcie zbędny. Bonus: białe gniazdo P3 to ten sam typ co wtyczki JST — może służyć jako zapasowy rozgałęźnik do testów ciągłości (jak nakładka programatora ALIENTEK) |
| `nie_wiem2\` | **Czujnik ruchu PIR HC-SR501** (biała kopułka Fresnela; na spodzie układ BISS0001, dwa potencjometry: czułość i czas podtrzymania, zworka trybu) | **Potencjalnie przydatny**: po zintegrowaniu klimatyzacji z Home Assistant może sterować automatyką obecności (np. podnoszenie/obniżanie nastawy, gdy w pomieszczeniu nikogo nie ma). Zasilanie 5 V, wyjście 3,3 V — bezpośrednio kompatybilne z ESP |


---

# Elementy modułu v2 — identyfikacja z natury (2026-09-04)

Sprawdzone na dostarczonych sztukach. **Opisy na płytkach różnią się od katalogowych**
i to właśnie te opisy obowiązują przy lutowaniu.

| Folder | Element | Opisy wyprowadzeń — jak jest naprawdę |
|---|---|---|
| `esp32\` | ESP32 DevKit 30-pin, ESP-WROOM-32, CP2102 | góra: VIN GND D13 D12 D14 D27 D26 D25 D33 D32 D35 D34 VN VP EN · dół: 3V3 GND D15 D2 D4 **RX2 TX2** D5 D18 **D19** D21 RX0 TXO D22 **D23** |
| `max3485\` | Moduł **RS485 V2.05** na MAX3485 | jedna listwa: **EN VCC RXD TXD GND** · druga: **GND A B** |
| `mp1584\` | Przetwornica MP1584EN z potencjometrem | pola lutownicze opisane od spodu; potencjometr wieloobrotowy z lewej |
| `tranzystor_odbiornik\` | **BC337-40** (NPN) i **VS1838B** (odbiornik IR w ekranie metalowym) | VS1838B patrząc od soczewki: **OUT GND VCC** |

## Trzy rozbieżności wobec pierwotnego schematu

**Nie ma pinu „5V".** Wejście zasilania ESP32 nazywa się **VIN**. To groźne, bo w dawnej
sondzie na ESP8266 pin o tej samej nazwie przyjmował 9–24 V — tutaj wolno podać wyłącznie
**5,00 V**. Szczegóły: `..\modul_v2\MODUL_v2.pdf`, rozdz. 3.7.

**Moduł RS-485 ma inne nazwy pinów, niż zakładałem.** Zamiast katalogowych RO / DI / DE+RE
są **RXD / TXD / EN**. Odwzorowanie: RXD↔RX2, TXD↔TX2, EN↔D4.

**Tranzystor to BC337-40, nie -25.** Wyższe wzmocnienie prądowe (250–630 zamiast 160–400),
więc rezystor bazy 470 Ω działa z jeszcze większym zapasem. Bez zmian w układzie.

Zdjęcia elementów znajdują się w podfolderach. Elementy użyte w działającej sondzie są
opisane w [`..\plytki\`](../plytki/) i na schemacie
[`..\schematy\schemat_FINALNY_dzialajacy.png`](../schematy/schemat_FINALNY_dzialajacy.png).
