# Dodatkowe dostępne elementy — identyfikacja

| Folder | Co to jest | Przydatność w projekcie |
|---|---|---|
| `UNO\` | Arduino UNO (klon z CH340) | Zapas — może służyć za drugi tester/konwerter USB-serial; tor USB sprawny |
| `nie_wiem\` | **Sterownik silnika krokowego ULN2003** (płytka z wejściami IN1–IN7, 4 diody D1–D4, białe 5-pinowe gniazdo P3 do silnika 28BYJ-48) | W tym projekcie zbędny. Bonus: białe gniazdo P3 to ten sam typ co wtyczki JST — może służyć jako zapasowy rozgałęźnik do testów ciągłości (jak nakładka programatora ALIENTEK) |
| `nie_wiem2\` | **Czujnik ruchu PIR HC-SR501** (biała kopułka Fresnela; na spodzie układ BISS0001, dwa potencjometry: czułość i czas podtrzymania, zworka trybu) | **Potencjalnie przydatny**: po zintegrowaniu klimatyzacji z Home Assistant może sterować automatyką obecności (np. podnoszenie/obniżanie nastawy, gdy w pomieszczeniu nikogo nie ma). Zasilanie 5 V, wyjście 3,3 V — bezpośrednio kompatybilne z ESP |

Zdjęcia elementów znajdują się w podfolderach. Elementy użyte w działającej sondzie są
opisane w [`..\plytki\`](../plytki/) i na schemacie
[`..\schematy\schemat_FINALNY_dzialajacy.png`](../schematy/schemat_FINALNY_dzialajacy.png).
