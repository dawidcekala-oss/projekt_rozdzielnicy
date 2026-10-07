# Panel biura — karta Lovelace `biuro-panel`

Rzut kondygnacji biura z dziewięcioma jednostkami klimatyzacji: cztery kasetony
Gree GKH (nasz typ) i pięć jednostek ściennych tej samej firmy. Karta pokazuje stan
na żywo, pozwala sterować i wypisuje aktywne automatyzacje.

## Pliki

| Plik | Rola |
|---|---|
| `biuro-panel.js` | **źródło karty** — jedyny plik, który się edytuje |
| `podglad.html` | podgląd przez serwer lokalny (importuje `biuro-panel.js`) |
| `podglad_offline.html` | podgląd **z dysku, bez serwera** — kod karty wklejony w środku |

`podglad_offline.html` jest **generowany**; po zmianie `biuro-panel.js` trzeba go
odtworzyć, inaczej pokaże starą wersję.

## Zainstalowane w Home Assistancie

| Co | Gdzie |
|---|---|
| plik karty | `C:\HomeAssistant\config\www\biuro-panel.js` |
| definicja pulpitu | `C:\HomeAssistant\config\panel_biuro.yaml` |
| wpis rejestrujący pulpit | `configuration.yaml`, sekcja `lovelace:` |
| pulpit w interfejsie | **Biuro** w menu bocznym |

Kopie zapasowe plików sprzed zmiany mają sufiks `.przed_panelu_<data>`.

Po każdej zmianie `biuro-panel.js` trzeba **skopiować go do `config/www/`** i podbić
numer w `panel_biuro.yaml` (`/local/biuro-panel.js?v=2`), inaczej przeglądarka poda
starą wersję z pamięci podręcznej.

## Co karta robi

- **Rzut biura** odwzorowany ze szkicu: hala, open space, lada z przegrodą, trzy sale.
- **Wirnik kręci się tylko wtedy, gdy jednostka realnie pracuje**, a prędkość obrotu
  odpowiada biegowi z magistrali: niski 3,2 s na obrót, średni 1,7 s, wysoki 0,95 s.
  To nie jest ozdoba — patrząc na rzut od razu widać, która jednostka dmucha i jak mocno.
- **Przy każdej jednostce** dyskretnie: nazwa, temperatura pomieszczenia i nastawa.
- **Ikonka suwaków** w rogu znacznika otwiera panel boczny z kompletem parametrów
  (pomiar z magistrali) i sterowaniem (zasilanie, nastawa, tryb, bieg).
- **Rozwijana lista automatyzacji** w pasku górnym, z przełącznikiem przy każdej
  i datą ostatniego uruchomienia.
- **Chipy podsumowania**: ile pracuje, średnia temperatura, ile bez modułu,
  ile bez łączności, ile bez potwierdzenia komendy.

## Stany jednostki na rzucie

| Wygląd | Znaczenie |
|---|---|
| pełna ramka, wirnik się kręci, poświata | pracuje |
| pełna ramka, wirnik stoi | ma moduł, nie pracuje |
| **ramka przerywana**, napis „bez modułu" | jednostka bez sprzętu — 8 z 9 na dziś |
| napis „brak łączności" + plakietka | moduł jest, ale sonda milczy |
| **czerwona ramka** + plakietka | ostatnia komenda niepotwierdzona przez magistralę |

## Dodanie jednostki po zamontowaniu modułu

W `panel_biuro.yaml` dopisać do odpowiedniego slotu sekcję `encje` — wzorem `k1`.
Sloty: `k1`–`k4` (kasetony), `j1`–`j5` (ścienne); pozycje na rzucie są w karcie
na stałe i nie wymagają zmian.

## Ograniczenia (stan na 2026-09-01)

- **Tylko jedna jednostka ma moduł.** Pozostałe osiem to miejsca oczekujące; karta
  rysuje je przerywaną kreską i nie udaje, że ma z nich dane.
- **Nastawa i tryb pochodzą z pamięci sondy, nie z jednostki.** Zmiana pilotem nie
  zaktualizuje ich w panelu — magistrala nie przenosi nastaw. Praca, bieg, klapy
  i temperatury są mierzone i pokazują prawdę niezależnie od tego, kto wydał polecenie.
- Nazwy pomieszczeń są robocze — do zmiany w `panel_biuro.yaml`.
