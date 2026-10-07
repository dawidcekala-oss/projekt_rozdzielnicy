# Panel biura — karta Lovelace `biuro-panel`

Rzut kondygnacji biura z dziewięcioma jednostkami klimatyzacji: cztery kasetony
Gree GKH (nasz typ) i pięć jednostek ściennych tej samej firmy. Karta pokazuje stan
na żywo, pozwala sterować i wypisuje aktywne automatyzacje.

## Pliki

| Plik | Rola |
|---|---|
| `biuro-panel.js` | **źródło karty** — jedyny plik, który się edytuje |
| `biuro-panel-start.js` | **rozrusznik** — ładuje kartę z ponawianiem (patrz „Dlaczego rozrusznik”) |
| `podglad.html` | podgląd przez serwer lokalny (importuje `biuro-panel.js`) |
| `podglad_offline.html` | podgląd **z dysku, bez serwera** — kod karty wklejony w środku |

`podglad_offline.html` jest **generowany**; po zmianie `biuro-panel.js` trzeba go
odtworzyć, inaczej pokaże starą wersję.

## Zainstalowane w Home Assistancie

| Co | Gdzie |
|---|---|
| plik karty | `C:\HomeAssistant\config\www\biuro-panel.js` |
| rozrusznik karty | `C:\HomeAssistant\config\www\biuro-panel-start.js` |
| wpis ładujący kartę | `configuration.yaml`, `frontend: extra_module_url: /local/biuro-panel-start.js?v=…` |
| definicja pulpitu | `C:\HomeAssistant\config\panel_biuro.yaml` |
| wpis rejestrujący pulpit | `configuration.yaml`, sekcja `lovelace:` |
| pulpit w interfejsie | **Biuro** w menu bocznym |

Kopie zapasowe plików sprzed zmiany mają sufiks `.przed_panelu_<data>`.

Po każdej zmianie `biuro-panel.js` trzeba **skopiować go do `config/www/`**, podbić
**jeden** numer w `configuration.yaml` (`/local/biuro-panel-start.js?v=5`) i zrestartować
Home Assistanta. Rozrusznik czyta ten numer ze swojego adresu i ładuje
`/local/biuro-panel.js?v=<ten sam numer>`, więc nowy numer omija obie pamięci
podręczne naraz. Bez podbicia przeglądarka poda starą wersję: Home Assistant wysyła
pliki z `www/` z nagłówkiem `Cache-Control: max-age=2678400` (31 dni), a jego service
worker trzyma je dodatkowo we własnej pamięci przez 24 h. Starego `biuro-panel.js`
nie usuwać od razu — przez jedno przeładowanie po restarcie przeglądarka może jeszcze
użyć poprzedniej strony startowej, która importuje go bezpośrednio.

## Automatyzacje (grupowe komendy) — od 14 września 2026

Pod rzutem jest sekcja **Automatyzacje** (pełna szerokość karty, kafelki). „+ Dodaj" otwiera
w szufladzie formularz: nazwa, zaznaczenie jednostek (tylko te z modułem) i jedna lub więcej
komend wykonywanych po kolei (Włącz / Wyłącz / +1 °C / −1 °C / Ustaw temperaturę / Tryb /
Bieg; „+ kolejna komenda" dodaje następną, np. „Włącz" + „Ustaw 24 °C"). Po zapisaniu
automatyzacja pojawia się na liście z opisem (komenda · jednostki), przyciskiem ▶
(wykonaj teraz) i ✕ (usuń); kliknięcie w wiersz otwiera edycję.

**Jak to jest zapisane.** Każda automatyzacja to zwykły **skrypt Home Assistanta**
o identyfikatorze `script.klima_panel_…`, tworzony przez API konfiguracji
(`POST /api/config/script/config/<id>`), więc trafia do `scripts.yaml`, przeżywa restart,
jest widoczny w Ustawienia → Automatyzacje i sceny → Skrypty i da się go uruchomić z
dowolnego miejsca (także z reguł HA). W polu `description` skryptu karta trzyma JSON
z zaznaczonymi slotami i listą komend (`komendy`), żeby odtworzyć formularz. Sekwencja to
kolejne akcje każdej komendy dla każdej jednostki (`switch.turn_on/off`, `number.set_value`, `select.select_option`) z
`continue_on_error: true`, więc jednostka bez łączności nie zatrzymuje reszty.
„+1 °C" liczy się z aktualnej nastawy szablonem
`{{ [16, [30, (states('number.…') | float(22)) + 1] | min] | max | int }}`.
Wymaga konta administratora w HA (API konfiguracji).
Skrypt można też dopisać ręcznie do `scripts.yaml` w tym samym formacie (identyfikator
`klima_panel_…`, `description` z JSON); tak powstała pierwsza automatyzacja „Włącz wszystkie
i ustaw 24 °C" (14 IX 2026).

**Nazwy jednostek** (w `panel_biuro.yaml`): Biuro, Hala zachód, Hala północ, Akwarium,
Open space lewa/prawa, Sala 1–3. Identyfikatory encji się nie zmieniły.

Przycisk w pasku górnym nazywa się teraz **Reguły HA** i rozwija listę zwykłych
automatyzacji Home Assistanta (z przełącznikami), jak dotąd.

## Dlaczego rozrusznik

Home Assistant importuje moduły z `extra_module_url` **dokładnie raz**, w chwili
otwarcia strony, i nieudanego importu nie ponawia. Jeśli w tej chwili serwer nie
odpowiada (restart Home Assistanta, uśpiony Docker, chwilowy zanik sieci), plik karty
nie dociera, element `biuro-panel` nigdy nie powstaje i pulpit **Biuro** do końca
sesji pokazuje „Błąd konfiguracji”. Od wersji 2025 Home Assistant nie wypisuje treści
błędu na pulpicie (tylko w edytorze karty), więc z zewnątrz nie widać, że chodzi
o brakujący element. Rozrusznik (`biuro-panel-start.js`, 2 kB) ponawia import
co 1–10 s przez ok. 15 minut; gdy karta się w końcu zdefiniuje, Home Assistant sam
wymienia zaślepkę na prawdziwą kartę, bez odświeżania strony. Stan prób widać
w konsoli przeglądarki (F12) pod `window.biuroPanelStart`.

Jeśli błąd mimo to zostanie: F12 → zakładka **Console** → czerwona linia z tekstem
`custom:biuro-panel` albo `biuro-panel` mówi, co się nie udało.

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
