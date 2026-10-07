# Klimatyzacja Gree → Home Assistant — dokumentacja projektu

**Stan na 2026-08-26. Sterowanie z Home Assistant DZIAŁA — w obie strony.**

Sonda zbudowana wyłącznie z posiadanych części **odczytuje stan kasetonu Gree** z portu
COM-MANUAL i **wydaje mu polecenia podczerwienią**. Dwa tory pracują razem i pilnują się
nawzajem:

- **odczyt** — bierny podsłuch rozgłoszenia RS-485, które jednostka nadaje sama co 800 ms;
  daje temperatury, bieg wentylatora i klapy;
- **sterowanie** — dioda podczerwieni przy odbiorniku jednostki, protokół Gree (YAW1F);
  po każdej komendzie **magistrala sprawdza, czy jednostka faktycznie zareagowała**,
  a niepotwierdzona komenda jest powtarzana i na koniec zgłaszana jako błąd.

Magistrala pozostaje jednokierunkowa: jednostka **nie odpowiada** na nasze ramki RS-485
i nie przyjmuje przez nie poleceń od niezarejestrowanego sterownika (ponad 1100 prób —
szczegóły: FAZA2_USTALENIA). Sterowanie ominęło ten problem inną drogą — podczerwienią.

Konfiguracja Home Assistant: `HA_INTEGRACJA.pdf` (odczyt + sterowanie, wersja podstawowa).
Pełny panel biura dojdzie po montażu docelowym.

**Każdy dokument `.md` ma obok wersję `.pdf` o tej samej nazwie** — do czytania służą
PDF-y; pliki `.md` to źródła (konwersja: `narzedzia\md_do_pdf.py`).

## Mapa folderu

| Plik / folder | Opis |
|---|---|
| `Integracja_klimatyzacji_Gree_z_Home_Assistant.pdf` | **Główny raport** — analiza, studium przypadku, zweryfikowana konfiguracja, plan prac. **Uwaga: wydanie z 22.08, sprzed ustaleń Fazy 2** — fragmenty o „komunikacji dwukierunkowej" są nieaktualne; obowiązuje `FAZA2_USTALENIA` |
| `FAZA2_USTALENIA.pdf` / `.md` | **ustalenia Fazy 2**: jednostka tylko rozgłasza, 1100+ prób ramek bez odpowiedzi, rozpoznanie cudzych implementacji |
| `KALIBRACJA_TEMPERATUR.pdf` / `.md` | dowód przelicznika temperatur (bajt − 100 = °C) i wyjaśnienie różnicy wobec odczucia w pomieszczeniu |
| `HA_INTEGRACJA.pdf` / `.md` | **gotowa konfiguracja Home Assistant — odczyt i sterowanie**, do wklejenia |
| `HA_INTEGRACJA_ODCZYT.pdf` / `.md` | poprzednia wersja, tylko odczyt — **zastąpiona** przez `HA_INTEGRACJA` |
| `DEKODOWANIE_POSTEP.pdf` / `.md` | mapa pól ramki rozgłoszeniowej |
| `STUDIUM_PRZYPADKU.pdf` / `.md` | pełny zapis diagnozy: problemy → przyczyny → rozwiązania (PDF + źródło Markdown) |
| `PLAN_DEKODOWANIA.pdf` / `.md` | plan etapu dekodowania (3 fazy, podział ról) — **wykonany**, wyniki w dokumentach poniżej |
| `DEKODOWANIE_POSTEP.pdf` / `.md` | mapa pól rozgłoszenia: cztery zmienne bajty `[9]` `[10]` `[12]` `[14]`, cała reszta stała |
| `FAZA2_USTALENIA.pdf` / `.md` | **dokument obowiązujący**: jednostka nadaje sama i nie odpowiada; wynik ponad 1100 prób nadawania; kalibracja temperatury (surowy bajt − 100 = °C); gdzie leżą nastawy |
| `HA_INTEGRACJA.pdf` / `.md` | konfiguracja HA: encje odczytowe + przełącznik, nastawa, tryb i bieg |
| `ZASILANIE_OBLICZENIA.pdf` / `.md` | zasilanie docelowe z +12 V portu: obliczenia (punkt pracy, start, impulsy WiFi), kryteria testu oraz **errata po nieudanym teście z 47 Ω — obowiązuje R = 25–28 Ω** |
| `schematy\schemat_FINALNY_dzialajacy.png` | **schemat działającego połączenia** (jedyny aktualny) |
| `schematy\archiwum\` | wcześniejsze warianty schematów (historyczne) |
| `plytki\wemos_d1_r1.md` | dokumentacja płytki WeMos D1 R1 (pułapka z opisami pinów!) |
| `plytki\bramka_grz47_smg01.md` | dokumentacja bramki ZTS47/SMG-01 jako konwertera (CN2, RXP/TXP, blaszki) |
| `plytki\flasher_alientek_minipro.md` | programator ALIENTEK jako rozgałęźnik serwisowy |
| `test_com_manual\PROCEDURA_TESTU.md` | procedura uruchomienia sondy + testy biurkowe |
| `test_com_manual\sonda_gree_v5\` | **aktualny firmware** (v5): odczyt dla HA po HTTP, komendy przez telnet, aktualizacja przez WiFi |
| `test_com_manual\sonda_gree_v3\`, `_v4\` | wcześniejsze wersje firmware (v3 zdalne zapytania, v4 precyzyjne nadawanie) |
| `test_com_manual\tester_biurkowy\` | firmware diagnostyczny (testy bramki multimetrem) |
| `test_com_manual\sonda_gree.ino`, `sonda_gree_wemos.ino` | starsze warianty firmware (USB, bez WiFi) |
| `test_com_manual\log_sondy.txt` | log wszystkich sesji sondy: odebrane rozgłoszenia jednostki oraz — w sesjach nadawczych — nasze ramki wysłane, zawsze bez odpowiedzi |
| `test_com_manual\kalibracja_log.txt` | 40-minutowy pomiar ciągły, na którym rozstrzygnięto przelicznik temperatury |
| `test_com_manual\ramka_odniesienia.json` | wzorcowa ramka rozgłoszenia do porównań różnicowych |
| `test_com_manual\log_tester_biurkowy.txt` | log sesji testera biurkowego |
| `instrukcje\` | oficjalne instrukcje bramki (Sinclair SMG-01, TD metal U-Match) |
| `dodatkowe_dostepne_elementy\SPIS_ELEMENTOW.md` | identyfikacja zapasowych części (UNO, sterownik ULN2003, czujnik ruchu PIR) |
| `narzedzia\` | skrypty: generatory raportu i schematów, nasłuch sondy, analiza ramek, dekoder różnicowy (`dekoder_roznicowy.py`), skanery prób nadawania (`skan_pelny.py`, `skan_naglowka.py`, `skan_zapytan.py`) |
| `zdjecia\uklad\` | zdjęcia układu testowego (WeMos, bramka, wiązka, pigtail) |
| `zdjecia\flasher\` | zdjęcia programatora ALIENTEK |
| `dzialajace_polaczenie\` | zdjęcie kompletnego działającego układu przy jednostce |

## Kluczowe fakty (skrót)

- Port: **COM-MANUAL** płyty GRZ4M-A3 (GND / +12 V / A / B), magistrala RS485, **1200 bodów 8N1**,
  ramki `7E 7E`, suma XOR. Jednostka **rozgłasza** ramkę `7E 7E FF 40 11 17 ...` (29 bajtów) co 800 ms.
- Bramka ZTS47/SMG-01 pracuje jako **konwerter UART↔RS485**: opisy TXD/RXD na jej laminacie
  są z perspektywy klimatyzatora (połączenie „na wprost"), RXP (biała)→masa włącza odbiornik,
  TXP (żółta)→D7 jest kluczem nadawania. Szczegóły: `plytki\bramka_grz47_smg01.md`.
- **+12 V portu wolno użyć tylko przez filtr ograniczający prąd** (25–28 Ω + 300 µF). Podłączenie wprost blokuje start jednostki, a wersja z 47 Ω przegrzała rezystor — patrz ZASILANIE_OBLICZENIA.
- Pilot podczerwieni działa równolegle z sondą.
- **Jednostka nadaje sama co 800 ms i nie odpowiada na zapytania** — odczyt to bierny podsłuch.
- Temperatury: **surowy bajt − 100 = °C**; czujnik ROOM mierzy powietrze powrotne przy suficie.
