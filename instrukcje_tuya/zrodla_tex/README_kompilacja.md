# Źródła LaTeX — instrukcje Tuya AMPERE POINT

Komplet plików potrzebnych do samodzielnej kompilacji obu dokumentów.

## Zawartość

| Plik | Rola |
|---|---|
| `AMPERE_POINT_instrukcja_blokada_godzin_v1.tex` | instrukcja uproszczona — blokada ładowania w wybranych godzinach |
| `AMPERE_POINT_poradnik_automatyzacje_tuya_v1.tex` | poradnik — automatyzacje w aplikacji Tuya |
| `preambula.tex` | wspólna preambuła: kolory, czcionki, stopka, makra (`\apheader`, `\krok`, `\apinfo`, `\osczasu` i inne) |
| `logo_ap.png` | logo używane w pasku tytułowym |
| `screeny/norm/*.jpg` | 20 zrzutów ekranu, znormalizowanych do 1080×1440 |

Oba dokumenty wciągają `preambula.tex` przez `\input`, więc **zmiana kolorystyki, stopki albo autora w jednym miejscu zmienia oba PDF-y naraz**.

## Czym kompilować

Wymagany jest **XeLaTeX**, nie pdfLaTeX — dokumenty używają `fontspec` i systemowej czcionki **DejaVu Sans**.

Potrzebne pakiety: `fontspec`, `geometry`, `graphicx`, `xcolor`, `tikz`, `enumitem`, `fancyhdr`, `titlesec`, `array`, `tabularx`, `booktabs`, `hyperref`, `needspace`. W dystrybucjach MiKTeX i TeX Live Full wszystkie są w komplecie.

Na Windows najprościej: zainstalować **MiKTeX** (miktex.org), otworzyć plik `.tex` w TeXworks i wybrać silnik XeLaTeX z listy rozwijanej, albo uruchomić `kompiluj.bat`.

## Kompilacja z wiersza poleceń

Uruchamiać **z tego katalogu**, bo `\graphicspath` wskazuje `screeny/norm/` względnie:

```
xelatex AMPERE_POINT_instrukcja_blokada_godzin_v1.tex
xelatex AMPERE_POINT_instrukcja_blokada_godzin_v1.tex
```

Dwa przebiegi są konieczne — pierwszy zbiera położenia elementów, drugi ustawia poprawnie numerację i odsyłacze.

## Co gdzie zmienić

**Tytuł i podtytuł** — pierwsze linie każdego `.tex`, makro `\apheader{tytuł}{podtytuł}`. W podtytule `\\` łamie linię.

**Nazwa dokumentu w stopce** — linia 2 każdego `.tex`, `\newcommand{\DOCFOOT}{...}`.

**Autor** — `preambula.tex`: w stopce (`\fancyfoot[L]`) oraz w metadanych PDF (`\hypersetup{pdfauthor=...}`).

**Kolory** — `preambula.tex`, sekcja `\definecolor`. `apaccent` to pomarańcz z logo (#EC6434), `apnavy` to grafit nagłówków (#1A1A1A).

**Krok z obrazkiem** — `\krok{numer}{tytuł}{opis}{plik.jpg}`. Dla kroku bez zrzutu jest `\krokbezobrazka{numer}{tytuł}{opis}` — rysuje szarą ramkę z adnotacją o braku zrzutu.

**Oś doby** — `\osczasu{etykieta}{a/b,c/d}`, gdzie pary to godziny początku i końca stref blokady, np. `6/10,17/21`.

## Brakujące zrzuty

W poradniku trzy kroki nie mają jeszcze zrzutu i korzystają z `\krokbezobrazka`: lista harmonogramów, ekran dodawania wpisu harmonogramu oraz ekran „Powtórz" z wyborem dni tygodnia. Po zrobieniu zrzutów wystarczy je znormalizować do 1080×1440, wrzucić do `screeny/norm/` i zamienić `\krokbezobrazka{n}{t}{o}` na `\krok{n}{t}{o}{plik.jpg}`.

Normalizacja rozmiaru (ImageMagick):

```
magick plik.jpg -resize 1080x1440^ -gravity center -extent 1080x1440 screeny/norm/plik.jpg
```
