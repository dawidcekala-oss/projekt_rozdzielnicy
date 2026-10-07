# Lista zakupów — Hurtownia Stępień (Wolumen 2, paw. 71)

Niedziela: otwarte **9:00–14:00** • tel. 601 296 402 (warto zadzwonić i poprosić
o odłożenie) • MAX485 mają pod nr kat. **5133**.

## PRIORYTET 1 — naprawa zasilania sondy (potrzebne od razu)

| Element | Ile | Po co |
|---|---|---|
| rezystor **100 Ω / 0,25 W** | 8–10 szt. | 4 szt. równolegle = 25 Ω — nowy rezystor ograniczający filtra (stary 47 Ω spłonął, bo miał za małą moc i za wysoką wartość); reszta = zapas na filtr drugiego mostka |
| kondensator elektrolityczny **470–1000 µF / 25 V** | 2–4 szt. | powiększenie magazynku energii filtra (obliczenia wskazały przypadek graniczny przy 300 µF — większy kondensator go likwiduje) |
| kondensator elektrolityczny **100 µF / 50 V** | 4 szt. | zapas na wypadek, gdyby obecne 3 szt. ucierpiały od gorącego rezystora + jeden do rozbudowy |

## PRIORYTET 2 — szablon mostka dla kolejnych klimatyzatorów

| Element | Ile | Po co |
|---|---|---|
| **MAX485CPA+ (DIP8)** — kat. 5133 | 3 szt. | serce mostka: konwerter UART↔RS485 zastępujący dużą bramkę (5 zł/szt., nie ma co żałować zapasu) |
| podstawka **DIP8** | 3 szt. | gniazdo pod MAX485 — lutujesz podstawkę, nie scalak; wymiana układu bez lutownicy |
| płytka uniwersalna **~50×70 mm** wiercona | 3 szt. | baza mostka: ESP + MAX485 + dzielnik + złączki na jednej płytce |
| listwa **goldpin żeńska 1×40, raster 2,54** | 3 szt. | tniesz na odcinki = gniazda, w które wciskasz płytkę ESP (wyjmowalna jak MAX485 z podstawki) |
| złączka śrubowa **ARK 3-pin, raster 5 mm** | 3 szt. | zaciski A / B / GND — kable polowe do gniazda klimatyzatora pod śrubkę, serwis bez lutownicy |
| złączka śrubowa **ARK 2-pin** | 3 szt. | wejście zasilania +12 V z żyły JST |
| przewód montażowy cienki (linka, 2–3 kolory) | po kilka m | mostki i połączenia na płytce uniwersalnej + okablowanie w puszce |
| rezystory **3,3 kΩ i 6,8 kΩ / 0,25 W** | po 5 szt. | dzielniki napięcia 5 V → 3,3 V dla każdego mostka (jak w sondzie) |

## PRIORYTET 3 — drobiazgi „przy okazji"

| Element | Ile | Po co |
|---|---|---|
| listwa goldpin **męska** 1×40 | 2 szt. | gdyby zamówione D1 mini przyszły bez wlutowanych szpilek + szpilki serwisowe |
| koszulki termokurczliwe (mix średnic) | 1 kpl. | izolacja połączeń w wiązkach — standard w Twoich montażach |
| rezystor **120 Ω / 0,25 W** | 4 szt. | terminacja magistrali RS485 — na razie zbędna (krótkie kable), ale grosze i przyda się przy próbie wspólnej magistrali wielu jednostek |
| cyna z topnikiem 0,7–1 mm | 1 szpulka | jeśli zapas się kończy |

## Tego u Stępnia NIE kupisz (zamówienie internetowe — Allegro, jedna wysyłka)

- 2× **Sone Sterownik Rolet V3 WiFi** (zestaw 130,99 zł) — rolety,
- 2–3× płytka **ESP32 DevKit** (~25–35 zł) — mózgi kolejnych mostków,
- 2–3× **mini przetwornica 12→5 V** (MP1584/LM2596, ~5–8 zł) — stopień zasilania mostków z żyły +12 V,
- mini-przekaźniki **Tuya WiFi** do świateł — po weryfikacji N w puszkach włączników,
- gotowe przewody dupont (jak do Arduino) — jeśli Stępień nie będzie miał nic wygodnego.
