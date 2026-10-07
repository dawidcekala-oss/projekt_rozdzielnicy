# Projekt rozdzielnicy testowej Ampere Point (symulator usterek instalacji)

Rozdzielnica zasilająca ładowarkę EV (do 3×32 A) z możliwością symulowania
typowych błędów instalacyjnych z wnętrza rozdzielnicy. Sterowanie z
mikrokontrolera (ESP32) i ekranu dotykowego, z wykorzystaniem posiadanych
urządzeń Shelly. Miejsce na smart licznik oraz przekładniki modułu DLB
(moduł na zewnątrz, przekładniki i wyprowadzenia kabli w środku).

## Etapy i status

| Etap | Zakres | Status |
|------|--------|--------|
| 0 | Koncepcja, lista usterek, założenia, pytania | w toku |
| 1 | Dobór obudowy (checkpoint z zamawiającym) | w toku |
| 2 | Architektura elektryczna i sterowania (checkpoint) | - |
| 3 | Lista zakupowa (BOM) z podziałem na koszyki Allegro | - |
| 4 | Pełny schemat połączeń na jednej stronie A4 | - |
| 5 | Rozmieszczenie w obudowie, zarys firmware HMI | - |

## Struktura

```
docs/        dokumenty projektowe (koncepcja, dobór obudowy, architektura, BOM)
schemat/     źródła i wygenerowane pliki schematu (SVG/PDF A4)
materialy/   materiały wejściowe od zamawiającego (zdjęcia obecnej rozdzielnicy, karty katalogowe)
```

## Jak dostarczyć materiały z folderu AMPERE_POINT

Sesja projektowa działa w chmurze i nie widzi dysku lokalnego. Zdjęcia
obecnej rozdzielnicy, listę posiadanych Shelly i wszelkie karty katalogowe
należy wrzucić do repozytorium, np. z folderu `C:\Users\Lenovo\Desktop\AMPERE_POINT`:

```
cd C:\Users\Lenovo\Desktop\PROJEKT_ROZDZIELNICY
git clone https://github.com/dawidcekala-oss/projekt_rozdzielnicy .   # jeśli jeszcze nie sklonowane
git checkout claude/beautiful-euler-kh81w2
copy C:\Users\Lenovo\Desktop\AMPERE_POINT\*.jpg materialy\zdjecia_obecnej_rozdzielnicy\
git add materialy
git commit -m "Materiały: zdjęcia obecnej rozdzielnicy"
git push
```

Zdjęcia najlepiej zmniejszyć do ok. 2000 px szerokości (po kilkaset KB).
