# Projekt rozdzielnicy testowej Ampere Point (symulator usterek instalacji)

Rozdzielnica zasilająca ładowarkę EV (do 3×32 A) z możliwością symulowania
typowych błędów instalacyjnych z wnętrza rozdzielnicy. Sterowanie:
Raspberry Pi 5 z ekranem dotykowym 7″ + Z-Wave (posiadane Shelly Wave Pro 3)
+ przekaźniki GPIO. Bez licznika energii (pomiar: 3× PZEM-016 na wyjściu);
przekładniki modułu DLB w środku (moduł na zewnątrz).

## Etapy i status

| Etap | Zakres | Status |
|------|--------|--------|
| 0 | Koncepcja, lista usterek, założenia, pytania | gotowe (v2, 2026-10-07) |
| 1 | Dobór obudowy (checkpoint z zamawiającym) | decyzja: obudowa ABS 700×500×250 z płytą montażową, wolnostojąca |
| 2 | Architektura elektryczna i sterowania | RPi 5 + Z-Wave (Shelly Wave Pro 3) + GPIO, testy ≤16 A |
| 3 | Lista zakupowa (BOM) z podziałem na koszyki Allegro | `bom/bom.json` v5 (bez SPD i licznika, RCD z magazynu, montażowe poza kosztorysem) + kosztorys w `docs/pdf/03_…` |
| 4 | Pełny schemat połączeń na jednej stronie A4 | rew. C – `schemat/gen_schemat.py` → `docs/pdf/03_schemat_i_lista_zakupow.pdf` |
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
