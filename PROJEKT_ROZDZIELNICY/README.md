# Projekt rozdzielnicy testowej Ampere Point (symulator usterek instalacji)

Rozdzielnica zasilająca ładowarkę EV (do 3×32 A) z możliwością symulowania
typowych błędów instalacyjnych z wnętrza rozdzielnicy. Sterowanie z
mikrokontrolera (ESP32) i ekranu dotykowego, z wykorzystaniem posiadanych
urządzeń Shelly. Miejsce na smart licznik oraz przekładniki modułu DLB
(moduł na zewnątrz, przekładniki i wyprowadzenia kabli w środku).

## Etapy i status

| Etap | Zakres | Status |
|------|--------|--------|
| 0 | Koncepcja, lista usterek, założenia, pytania | gotowe (v2, 2026-10-07) |
| 1 | Dobór obudowy (checkpoint z zamawiającym) | **czeka na decyzje** – `docs/pdf/02_dobor_obudowy.pdf` |
| 2 | Architektura elektryczna i sterowania (checkpoint) | - |
| 3 | Lista zakupowa (BOM) z podziałem na koszyki Allegro | - |
| 4 | Pełny schemat połączeń na jednej stronie A4 | - |
| 5 | Rozmieszczenie w obudowie, zarys firmware HMI | - |

## Struktura

```
docs/            dokumenty projektowe (źródła .md) – czytaj wersje PDF w docs/pdf/
docs/pdf/        PDF-y do czytania
docs/zrodla/     surowe wyniki researchu i przeglądu krytycznego (JSON)
tools/           generator PDF (pandoc + Chromium): ./tools/build_pdf.sh docs/*.md
zdjecia_obecnej/ zdjęcia obecnej skrzynki TED Beryl 11M (od zamawiającego)
```

## Materiały wejściowe

Cały folder AMPERE_POINT jest w tym repozytorium (gałąź `main`). Projekt rozdzielnicy korzysta
z: `rozdzielnica/`, `PROJEKT_ROZDZIELNICY/zdjecia_obecnej/`, `instalacja/` (zasilanie słupka),
`SHELLY/inne_sprzety/` (posiadane Shelly), `DLB_R&D/` i `wallbox_DLB/` (moduł DLB-A1),
`custom_device_FINAL/` (konwencja oznaczeń EPLAN).
