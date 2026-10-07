# Hak zamka szafy AmperePoint — notatki projektu

Folder roboczy: `C:\Users\Lenovo\Desktop\AMPERE_POINT\hak` (od 2026-10-07, polecenie Dawida — wszystko tu).

## Problem (od Dawida, 2026-10-07)
- Zamek szyfrowy DAMUZHI na drzwiach szafy (kod 3×3 bębenki + kluczyk serwisowy, wskaźnik
  zielony/czerwony), hak obraca się z gałką i zachodzi za górną część podłużnego otworu w szafie.
- Hak ma luz także w stanie zablokowanym (luzu NIE likwidujemy).
- Gałka w skrajnym położeniu zgodnie z ruchem wskazówek zegara (kierunek otwierania), kod
  nieustawiony, lekkie dociśnięcie drzwi w dół → drzwi się otwierają.
- Ustalenie: hak za krótki, trzeba go wydłużyć.
- Uwagi Dawida: (1) sprawdzić, czy dłuższy hak się zmieści i o nic nie zawadzi;
  (2) przed wyjazdem do fabryki haków próba: wydruk 1:1, wycięcie z kartonu/plastiku,
  założenie i sprawdzenie działania.

## Hak w szafie (zdjęcia `zdjęcia/`, pomiary Dawida)
- **Grubość 1,5 mm** (Dawid, 2026-10-07) — plik dostawcy podaje 2,0.
- Szerokość zmierzona 19,7 mm (zdjęcie b343…) → wariant standardowy (20), nie „język +3” (23).
  Długości (38,5 standard czy 40 wariant „40”) jeszcze nie potwierdzono.
- Hak przykręcony śrubą z podkładką na trzpieniu zamka, kształt „9” (tarcza z otworem
  u góry, ramię, język u dołu skierowany ku wolnej krawędzi drzwi — przy drzwiach otwartych).
- Pomiary na zdjęciach, znaczenie NIEPOTWIERDZONE (pytanie do Dawida):
  27,8 mm (537f…, poziomo przy górze zamka), 12,7 mm (609a…, pod zamkiem),
  19,7 mm (b343…, szerokość haka), ok. 36 mm (9aae…, przy haku, wyświetlacz nieostry),
  38,5 mm (fb1c…, szczęki wewnętrzne na ramie szafy — prawdopodobnie długość otworu),
  długa linijka 70–150 mm przy okrągłym termohigrometrze (cb2d…, cce1…).
- Pod zamkiem wygięty wspornik ze stali nierdzewnej (kształt U/L) — potencjalna przeszkoda
  przy obrocie dłuższego haka.

## Plik od dostawcy: `dostawca/hook.dwg`
- AutoCAD 2000 (AC1015), mm, opisy po chińsku. Trzy warianty, każdy „不锈钢2.0厚度”:
  1. 标准锁钩 = hak standardowy: długość 38,5, szerokość 20,0.
  2. 整体加长40 = całość wydłużona do 40: język 1,5 mm dalej od osi.
  3. 锁舌加长3mm = język wydłużony o 3 mm: czubek z x = −10 na −13, szerokość 23,0.
- Geometria w układzie osi obrotu (0,0 = środek otworu kwadratowego 7,2 mm): tarcza R10
  (łuk 270°), ramię x 0…10, prawa krawędź do R4, spód języka y = −28,5, czubek x = −10 (R1),
  grubość języka 4,8 (w dołku ~3,8), wklęsła krawędź = łuk R24,377 (strzałka 1,027 mm),
  stopień 1,7 mm przy ramieniu (x 1…5, y −22,0…−23,7). Dostawca w wariancie 3 zachował
  strzałkę 1,027 (R35,7 na cięciwie 17).
- Błędy w pliku: wariant 1 obrócony o 0,4°; „19,56” zdjęte z zaokrąglenia (jest 20,0);
  „22,7” w wariancie 3 (jest 23,0).

## Warianty do próby (`robocze/hak_generator.py`)
a = język dalej od osi, b = czubek języka dalej w bok. Zgodność z dostawcą sprawdzona
(`robocze/weryfikacja.py`): obecny 0,010 mm, +1,5 od osi 0,001 mm, +3 w bok 0,015 mm.

| Wariant | a | b | długość | szerokość | oś→język | promień obrotu |
|---|---|---|---|---|---|---|
| OBECNY | 0 | 0 | 38,5 | 20 | 23,7 | 29,9 |
| +1,5 OD OSI (= dostawca „40”) | 1,5 | 0 | 40 | 20 | 25,2 | 31,4 |
| +3 OD OSI | 3 | 0 | 41,5 | 20 | 26,7 | 32,8 |
| +3 W BOK (= dostawca „3 mm”) | 0 | 3 | 38,5 | 23 | 23,7 | 31,0 |
| +5 W BOK | 0 | 5 | 38,5 | 25 | 23,7 | 31,9 |
| +1,5 OD OSI, +3 W BOK | 1,5 | 3 | 40 | 23 | 25,2 | 32,4 |

| +4 OD OSI (prośba Dawida „+4 mm”, 2026-10-07) | 4 | 0 | 42,5 | 20 | 27,7 | 33,8 |
| +4 W BOK (j.w., drugi kierunek) | 0 | 4 | 38,5 | 24 | 23,7 | 31,4 |

„Promień obrotu” = najdalszy punkt haka od osi (okrąg, który hak zatacza) — do oceny kolizji.
Dawid poprosił o „+4 mm” bez kierunku → wydruk `druk/hak_+4mm_szablon_1do1_A4.pdf` ma oba
kierunki + obecny (sprawdzone: 2 strony A4, kreska 100,000 mm); CAD `cad/hak_os+4.*`, `cad/hak_bok+4.*`.

## Pliki wynikowe
- `cad/hak_<wariant>.dxf` + `.dwg` (AutoCAD 2000), `cad/hak_wszystkie_warianty.*`.
  Warstwy: KONTUR, OTWOR, OSIE, WYMIARY, OPISY, ZAKRES_OBROTU. Czcionka simplex.shx.
  Opisy w CAD bez polskich znaków (DXF R2000 = cp1252).
- `rysunki/hak_warianty.pdf` — arkusz A3 z wymiarami, nałożeniem na obecny i tabelą.
- `druk/hak_szablon_1do1_A4.pdf` — str. 1 szablon 1:1 (sprawdzone: A4 210×297, kreska
  kontrolna w PDF = 100,000 mm), str. 2 przebieg próby + tabela wyników A–D.
- `podglad/hook_podglad.pdf` — podgląd oryginalnego pliku dostawcy z tłumaczeniem.

## Narzędzia (zainstalowane 2026-10-07, bez uprawnień administratora)
- LibreCAD 2.2.1.5: `%LOCALAPPDATA%\Programs\LibreCAD\LibreCAD.exe` (rozpakowany 7-Zipem z
  oficjalnego instalatora, SHA256 zgodna z winget). Skrót w folderze `hak`. Konsolowy
  `dxf2png` NIE rysuje tekstów i NIE czyta żadnego DWG (nawet oryginału) — nie służy do weryfikacji.
- ODA File Converter 27.9: `%LOCALAPPDATA%\Programs\ODA_extract\ODAFileConverter.exe`
  (MSI podpisany przez Open Design Alliance, rozpakowany `msiexec /a`). Wywołanie:
  `ODAFileConverter <we> <wy> ACAD2000 DWG 0 1 *.DXF`. Tym robimy DWG.
- LibreDWG 0.14: `%LOCALAPPDATA%\Programs\libredwg\` — `dwg2dxf` do odczytu DWG.
  Jego `dxf2dwg` odrzuca MTEXT z obrotem i daje DWG, którego LibreCAD nie otwiera → nie używać.
- Python `ezdxf`. Pułapki: skrypt nie może się nazywać `inspect.py`; matplotlib z Calibri
  gubi litery → Arial + Segoe UI Symbol (✔✘); w heredocu `\n` w kodzie Pythona ginie → Edit.

## Otwarte (pytania do Dawida, 2026-10-07)
- Długość haka w szafie: 38,5 czy 40?
- Co mierzą 27,8 / 12,7 / ~36 / 38,5 / pomiar przy termohigrometrze?
- W którą stronę i o ile obraca się hak przy zamykaniu; która część haka zachodzi za
  krawędź otworu (czubek języka czy wnętrze „gardła” obejmuje blachę)?
- Otwór w blasze równoległej do drzwi czy w ściance prostopadłej?
- Grubość nowego haka: zostać przy 1,5 czy 2,0 jak w pliku dostawcy (czy zmieści się
  w otworze i pod śrubą)?
- Wyniki próby wyciętych haków (tabela A–D) → wybór wariantu → rysunek dla fabryki
  (wtedy opisy także po chińsku i angielsku).
