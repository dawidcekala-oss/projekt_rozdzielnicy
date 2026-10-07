# DLB R&D — baza wiedzy
**AMPERE POINT · rozwój modułu DLB‑A1 i współpracy z wallboxem · założona 2026‑09‑28 · aktualizowana na bieżąco**

> **Do czego służy:** jedno miejsce z wiedzą potrzebną przy rozwoju DLB: budowa systemu, znane wady, ustalenia z producentem, specyfikacje zmian, plany badań.
> **Zasady:** każdy wpis ma datę i źródło. `[F]` oznacza fakt (log, zdjęcie, pomiar, instrukcja, odpowiedź producenta), `[Z]` — założenie albo wniosek do potwierdzenia. Błędne wpisy poprawiać w miejscu, z adnotacją „*Korekta (data): …*”.
> **Folder:** `info_producenta\` — to, co przysłał albo napisał producent (zrzuty rozmów, pliki); `zasoby_informacji\` — ta baza, instrukcje (PDF + tekst do przeszukiwania), zdjęcia, logi.
> **Powiązane poza folderem:** sprawa u klienta, która wszystko zaczęła — `..\diagnostyka\istotne_casey\Karol\` i `..\diagnostyka\LOGI_Tuya_wallbox_DLB_bfe26d.md`; ogólne dane diagnostyczne — `..\diagnostyka\DANE_DIAGNOSTYCZNE.md` (sekcja wallbox/DLB); budowa wallboxa M3A1 — `..\WALLBOX_architektura\AI_PAMIEC_wallbox_M3A1.md`.

---

## 1. Stan (2026‑09‑28)

- Raport o dwóch wadach (EN/ZH/PL) wysłany producentowi 26–27.09 (`..\diagnostyka\istotne_casey\Karol\raport_do_producenta\`). Producent zapowiedział **przegląd firmware** (27.09).
- Producent pracuje nad **opóźnieniem wznowienia po pauzie** i potwierdził, jak ma ono działać (sekcja 5). Czeka na naszą wartość — **decyzja Dawida (28.09): 5 min** (sekcja 5.4, raport PDF v2 w folderze); do przekazania producentowi.
- Mamy zamówioną partię zestawów DLB z tym samym, wadliwym oprogramowaniem. **DLB nie ma OTA.** Pomysł: jeden zestaw do pełnego zbadania + ewentualne wgrywanie poprawki przez złącze programatora na kontrolerze (sekcja 4).
- Stanowisko Dawida (28.09): wada leży w DLB albo w parze DLB–wallbox. Sam wallbox jest na rynku od dawna i nigdy nie podawał absurdalnych prądów.

## 2. Budowa systemu — gdzie co się liczy

| Element | Co robi | Źródło |
|---|---|---|
| Kontroler DLB‑A1 (V1.4 z 2026‑01‑21; nasz stary egzemplarz ze stanowiska V1.1 z 2025‑07‑13) | mierzy prąd budynku trzema przekładnikami; przydział = 90% ustawionego limitu (DIP 1–255 A, na wyświetlaczu „SEt”) minus najbardziej obciążona faza reszty budynku; wysyła wallboxowi docelowy prąd w pełnych amperach | instrukcje `[F]` |
| Radio w kontrolerze | 433 MHz, złącze antenowe SMA, antena na podstawie magnetycznej | instrukcje, zdjęcie zestawu `[F]` |
| Moduł radiowy po stronie wallboxa (mała niebieska płytka z anteną spiralną) | wpina się w 8‑pinowe złącze „RF433 Module” na płycie głównej wallboxa; to samo łącze szeregowe procesora obsługuje RS485, wybór suwakiem „RF433 ⟷ RS485”; skonfigurowany fabrycznie, używać tylko z „własnym” DLB | zdjęcia M3A1, instrukcja `[F]`; że to przezroczysty mostek bez logiki — `[Z]` |
| Procesor wallboxa | wystawia sygnał CP dla auta, mierzy prąd, ochrona przeciążeniowa (alarm 400), po alarmie nastawa −1 A | log Tuya `[F]` |
| Moduł Wi‑Fi Tuya w wallboxie | chmura, aplikacja, log | `[F]` |

- **Łącze najpewniej dwukierunkowe** `[Z]`. Instrukcja mówi „each wall box is capped by its own requested current”, a DLB ma diody stanu połączenia z każdym wallboxem.
- **Wyświetlacz DLB** pokazuje w cyklu L1 → wartość → L2 → wartość → L3 → wartość → SEt → wartość (ok. 1 s na pozycję, cykl ok. 8 s), obcinając do pełnych amperów. Nagranie zrobione telefonem do góry nogami czyta się po obróceniu: „17/27/E7” = L1/L2/L3, „335” = SEt. Tabela w `DANE_DIAGNOSTYCZNE.md`.
- **Pole „DLB x.x A” na ekranie wallboxa:** w spoczynku 0.0, przy ładowaniu ≈ prąd auta (12.1 A przy 12,4 A). Czy to pomiar, czy przydział — nieustalone.
- **Rozbieżność instrukcji:** Quick Manual (EN) — „433 MHz albo RS485”; polska — RS485 „nie jest obecnie oferowane”.
- **Parowanie:**
  - DLB: przytrzymać przycisk 5 s (kasuje wszystkie powiązania, tryb wygasa po 2 min).
  - Wallbox, gdy nie ładuje: A + C przez 5 s → Settings → DLB Pairing → On.
  - Parować wszystkie wallboxy naraz.

## 3. Znane wady (materiały instalatorów i log z 26.09)

**Problem 1 — prąd powyżej nastawy wallboxa w trybie DLB (priorytet)** `[F]`
- Przy SEt 18 i nastawie 16 auto dwufazowe pobiera 16,9 A.
- Po obniżeniu nastawy do 9 A w trakcie ładowania wallbox przez kilka sekund ładuje dalej 16,6 A / 7,1 kW. Potem komunikat przeciążenia, nastawa 8 A i stop.
- W logu: 16,7 A przy nastawie 10, 20,2 A przy nastawie 15 i maksimum 16, 18–19,1 A przy 16.
- Alarm 400 porównuje zmierzony prąd z nastawą. Próg ≈ nastawa + większa z wartości (20%, 2 A) — zgodne z całym logiem i z instrukcją wallboxa `[Z]`.
- **Skutek:** uszkodzona ładowarka pokładowa auta trójfazowego (potrzebny był mechanik).

**Problem 2 — brak wznowienia po pauzie DLB** `[F]`
- Czajnik → przydział < 6 A → pauza (to działa poprawnie).
- Po wyłączeniu czajnika ładowanie nie wraca przez 5 min. Rusza dopiero po przepięciu auta.
- To sprzeczne z instrukcją: „Recovery is automatic when headroom returns”.

**Zastrzeżenie do problemu 2** `[F → Z]`
- W całym logu z 26.09 samo wznowiło się tylko 2 z 12 przerw. Oba razy auto dwufazowe, po alarmie, 4–5 s po powrocie wallboxa do gotowości.
- **Auto trójfazowe (to z nagrania problemu 2, później z uszkodzoną ładowarką pokładową) nie wznowiło ani razu, po żadnym rodzaju przerwy.**
- Część problemu 2 może więc wynikać z auta. Do sprawdzenia pauzą DLB z innym samochodem.
- Szczegóły: `..\diagnostyka\LOGI_Tuya_wallbox_DLB_bfe26d.md`, sekcja 10.

**Narastanie prądu po starcie** `[F — log]`: auto trójfazowe ok. 30 s do 13–16 A, dwufazowe ok. 5 s do ok. 9 A.

## 4. Aktualizacja oprogramowania — co wiemy (2026‑09‑27)

- DLB nie ma OTA `[F]`.
- Na płytce kontrolera V1.4 jest złącze do programatora `[F — zdjęcie]`. Opisu pinów i typu procesora jeszcze nie odczytano. Potrzebne ostre zdjęcia złącza, nadruku procesora (może być pod wyświetlaczem albo od spodu) i modułu radiowego z obu stron.
- Wallbox M3A1 ma złącze programowania „3V DIO CLK GND” (SWD, procesor ARM w obudowie LQFP‑48, nadruk nieczytelny) i moduł Wi‑Fi Tuya `[F — zdjęcia]`. Czy producent przewidział aktualizację procesora wallboxa przez Tuya — nieustalone.
- **Od producenta, jeśli poprawka ma trafić do DLB:**
  - plik `.hex` (albo `.bin` z adresem), model procesora, interfejs i ustawienia programowania;
  - informacja, czy w pamięci są dane egzemplarza (kalibracja przekładników, adres radiowy, parowanie) i czy wgranie je kasuje;
  - sposób sprawdzenia wersji po wgraniu;
  - plik obecnej wersji, żeby dało się wrócić;
  - pisemna zgoda na wgrywanie przez nas.
- **Pułapki:**
  - Blokada odczytu. Na poziomie podstawowym wgrać się da, ale najpierw trzeba skasować całą pamięć — tracimy dane egzemplarza i kopię oryginału. Poziom najwyższy trwale wyłącza złącze. Sprawdzić samym podłączeniem, niczego nie zmieniając.
  - Zasilanie. Programować przy odłączonej sieci, zasilając procesor z programatora albo z 3,3 V, nigdy z dwóch źródeł naraz. Nie łączyć programatora podłączonego do komputera z płytką zasilaną z sieci.
- Narzędzie: gotowy programator do rodziny procesora. Ewentualnie przejściówka albo klips z igłami sprężynowymi i skrypt do serii.

## 5. Opóźnienie wznowienia po pauzie

### 5.1 Jak działa według producenta *(potwierdzone 2026‑09‑28, rozmowa z 海客, zrzut w `..\info_producenta\`)* `[F]`

1. Przydział dla wallboxa spada poniżej 6 A → wallbox wyłącza ładowanie.
2. Od tej chwili biegnie opóźnienie T (to, które mamy ustalić).
3. Po upływie T:
   - jeśli prąd już wystarcza → wznowienie od razu;
   - jeśli nie → wallbox czeka, aż będzie wystarczający, i wtedy wznawia.

Czyli **T to minimalny czas pauzy, liczony od zatrzymania**. Po jego upływie nie ma dodatkowego sprawdzania stabilności.

*Korekta (2026‑09‑28): moja pierwsza analiza z tego samego dnia zakładała inną zasadę — T liczone od chwili, gdy zapas wróci, i zerowane przy każdym spadku. Wnioski poniżej przeliczone pod zasadę producenta.*

### 5.2 Skutki tej zasady

- **Obciążenie dłuższe niż T nic nie kosztuje:** wznowienie następuje zaraz po jego końcu. Przykład: czajnik 4 min przy T = 3 min → ładowanie wraca w chwili wyłączenia czajnika.
- **Obciążenie krótsze niż T przedłuża pauzę do T.** Przykład: kran z przepływowym podgrzewaczem na 30 s → pauza 3 min. Przy 11 kW to 0,46 kWh przesunięte w czasie.
- **T jest twardym limitem liczby cykli: najwyżej 60/T na godzinę** (T w minutach). Stałe opóźnienie ogranicza częstotliwość, ale nie zapobiega samemu skakaniu. Jeśli przydział krąży wokół 6 A (np. pompa ciepła z płynną regulacją, duże stałe obciążenie), wallbox wznowi i zatrzyma ładowanie co T, a samo ładowanie będzie trwało sekundy.
- **Pauza trwa co najmniej T**, więc dłuższe T to dłuższe przerwy dla auta. Auto dwufazowe wznawiało po przerwach 15–41 s; zachowanie przy przerwach wielominutowych nieznane.

### 5.3 Symulacja (2026‑09‑28) — pliki `symulacja\`, raport `..\AMPERE_POINT_DLB_opoznienie_wznowienia_v1.pdf`

Model: 1 s, 17:00–07:00, 120 nocy × 7 typów domów (wagi = szacunek udziału wśród klientów), 30 dni × 4 obiekty (wspólnota 3×40 A z 3 wallboxami, biuro 3×63 A, zakład 3×100 A, warsztat 3×63 A z 2 wallboxami). Odbiorniki z mocami katalogowymi i losowymi porami; termostaty i indukcja impulsowo. Auto: 8 s zwłoki + 30 s narastania (z logu). Wszystkie moce, czasy i wagi to **założenia** `[Z]` — zapisane w `sym_opoznienie.py`, do podważenia i zmiany.

Średnia ważona domów:

| Miara | T = 1 min | 2 | 3 | **4** | 5 | 10 |
|---|---|---|---|---|---|---|
| cykle start/stop na noc | 7,5 | 6,7 | 6,3 | **5,6** | 5,1 | 4,4 |
| cykle w najgorszej godzinie (90 % nocy poniżej) | 10,7 | 8,7 | 7,7 | **6,5** | 5,3 | 3,9 |
| cykle puste (< 60 s) na noc | 1,9 | 1,1 | 1,5 | **1,1** | 0,6 | 0,4 |
| późniejsze zakończenie ładowania [min] | 1,2 | 2,9 | 5,6 | **7,5** | 8,7 | 17,9 |
| najdłuższa pauza w nocy [min] | 10,0 | 10,4 | 10,9 | **11,6** | 12,2 | 15,9 |

Co z tego wynika `[F — z modelu]`:
- Przy T krótszym niż okres termostatu (piekarnik, suszarka: 2–5 min) liczba cykli nie zależy od T — wallbox startuje w każdej przerwie grzania. Dopiero T dłuższe niż okres pomija cykle. Test wrażliwości (okres 1,5 / 3 / 4 / 5 min): największy spadek cykli zawsze między 3 a 5 min.
- Koszt T rośnie liniowo (każda minuta = później zakończone ładowanie), zysk w cyklach powyżej 5 min maleje.
- Domy wrażliwe: 3×16–20 A (czajnik sam wywołuje pauzę, piekarnik = cykl co 4 min), pompa ciepła, mieszkanie 1‑fazowe (indukcja impulsowa = skakanie wokół progu). Dom z przepływowym podgrzewaczem woli krótkie T (każde mycie rąk = pełne T). Dom 3×32 A: pauzy rzadkie, T bez znaczenia.
- Biuro / zakład: pauzy z krótkich szczytów (winda, sprężarka, spawarka 10–90 s); wystarczy T > szczyt (~2 min), dłuższe T nic nie daje i nic nie kosztuje. Wspólnota 3×40 A z 3 wallboxami jest niedowymiarowana — T tylko rozrzedza pauzy (40 → 28 cykli/noc przy 4 min).

### 5.4 Decyzja (2026‑09‑28): **T = 5 min (300 s)**, liczone od zatrzymania ładowania

*Symulacja wskazała przedział 3–5 min z rekomendacją 4 min (raport v1). Dawid wybrał 5 min: okrągła wartość, łatwa do zakomunikowania, najmniej cykli w przedziale; minuta różnicy dla klienta bez znaczenia. Raport v2 z tą decyzją. Wcześniejsza propozycja 3 min (rano 28.09) liczona przy błędnym założeniu o zasadzie odliczania.*

Co daje 5 min wobec 4 min (średnia ważona domów): cykle na noc 5,6 → 5,1 (−8 %), cykle w najgorszej godzinie 6,5 → 5,3 (−19 %), **cykle puste (start i natychmiastowy stop) 1,1 → 0,6 (−50 %)**; koszt: ładowanie kończy się 1,2 min później, najdłuższa pauza dłuższa o 0,6 min. W domach wrażliwych: 3×16 A najgorsza godzina 11 → 8, pompa ciepła 8 → 6.

**Warunek wdrożenia:** w instrukcji DLB, ulotce i skrypcie serwisu podać wprost „wznowienie po 5 minutach od zatrzymania”. Bez tego pauza równa 5 min wygląda jak brak wznowienia — tyle czekali instalatorzy 26.09 i uznali to za usterkę. Producentowi: timer ma liczyć dokładnie 5:00 od zatrzymania (nie od końca alarmu ani od komunikatu).

Argumenty z symulacji za wartościami w przedziale (zachowane dla porządku):

- 4 min to koniec stromego odcinka krzywej cykli i wciąż poniżej 5 min — tyle czekali instalatorzy w teście i uznali brak wznowienia za usterkę.
- Dłuższe niż okres termostatu piekarnika/suszarki → pomija ich cykle; bliskie czasowi czajnika (2–4 min) → po najczęstszej przyczynie pauzy ładowanie wraca niemal od razu.
- 3 min: w domach 3×16–20 A wciąż ~15 cykli w najgorszej godzinie. 5 min: każda pauza ≥ 5 min, klient po 2‑minutowym czajniku patrzy na stojące ładowanie jeszcze 3 min. ≥ 10 min: mały zysk, 18 min później koniec, ryzyko uśpienia auta.

Czego stałe T nie załatwia (do osobnego zgłoszenia, nie dotyczy doboru T): skakanie co T przy przydziale krążącym wokół 6 A (brak zapasu przy wznowieniu); pełna pauza od szczytu poniżej sekundy (brak filtrowania); auto, które nie wznawia po powrocie sygnału (w logu z 26.09 auto trójfazowe nie wznowiło ani razu, dwufazowe po 4–5 s). Ulotka DLB obiecuje wznowienie „gdy tylko zrobi się miejsce” — do poprawy po wdrożeniu.

## 6. Pytania otwarte do producenta

1. Którego urządzenia dotyczy poprawka problemu 1 i 2 (wallbox, DLB, oba)? Czy wallbox ma aktualizację procesora przez Tuya?
2. Co dokładnie znaczy „enough current” przy wznowieniu — przydział ≥ 6 A czy z zapasem?
3. Czy DLB uśrednia prąd przed decyzją o pauzie (odporność na chwilowe skoki)?
4. Co robi wallbox, jeśli auto po wznowieniu nie pobiera prądu (budzenie)?
5. Jeśli poprawka trafi do DLB — pakiet z sekcji 4.
6. Jak wallbox sygnalizuje pauzę na CP (brak PWM, PWM poniżej 8%, stan E/F)?

## 7. Plan badań jednego zestawu na stanowisku (propozycja z 2026‑09‑27)

- **Problem 1 bez samochodu:**
  - tester PM701E symuluje ładowanie (stan C), oscyloskop podpięty na CP;
  - zmieniamy nastawę wallboxa i odczytujemy wypełnienie: 26,7% = 16 A, 33,3% = 20 A, prąd = wypełnienie × 0,6.
  - Oscyloskop z izolowanym wejściem — patrz incydent z różnicówką w `DANE_DIAGNOSTYCZNE.md`.
- **Problem 2 i test opóźnienia:**
  - obciążenie domu symulujemy przewodem czajnika przeprowadzonym przez przekładnik kilka razy (3 zwoje × 9 A ≈ 27 A dla DLB);
  - mierzymy czas od zdjęcia obciążenia do powrotu PWM;
  - potem to samo z prawdziwym autem, przy pauzach 1, 3, 5, 10 i 15 min.
- **Podsłuch łącza** między modułem radiowym a procesorem wallboxa analizatorem stanów logicznych — co wysyła DLB, co odpowiada wallbox.
- **Nadruki procesorów** i sprawdzenie blokady odczytu.

## 8. Źródła

| Plik | Zawartość |
|---|---|
| `instrukcje\DLB-A1_instrukcja_PL_Rev20251109.pdf` (+ `_tekst.txt`) | polska instrukcja DLB‑A1 |
| `instrukcje\DLB_Quick_Manual_EN_Rev20251109.pdf` (+ `_tekst.txt`) | Quick User Manual producenta |
| `zdjecia\DLB_A1_V1.4_zestaw_2026-09-27.webp` | zestaw V1.4: kontroler, 3 przekładniki, moduł radiowy do wallboxa, antena |
| `logi\log_tuya_2026-09-26_odtworzony.txt` | log wallboxa u klienta 11:38–14:26 (odtworzony, pomiary częściowe) |
| `symulacja\sym_opoznienie.py`, `wyniki.json`, `wykresy.py`, `raport_pdf.py` | symulacja doboru opóźnienia (założenia o odbiornikach w kodzie), wyniki, wykresy, generator raportu |
| `..\AMPERE_POINT_DLB_opoznienie_wznowienia_v1.pdf` / `_v2.pdf` | raport: dobór opóźnienia wznowienia — v1 rekomendacja 4 min, v2 decyzja 5 min |
| `..\info_producenta\` | korespondencja z producentem (`KORESPONDENCJA.md` + zrzuty) |
| `..\..\KONTEKST\iec-61851-1_compress.pdf` | IEC 61851‑1:2010 (tab. A.5–A.7: wypełnienie, czasy) |

## 6. Przekaźnik wallboxa a częste wznawianie *(2026-09-30)*

Pytanie Dawida: wersja firmware „dla niecierpliwych” z natychmiastowym wznowieniem po pauzie DLB. Frank: nie, ze względu na żywotność przekaźników. Sprawdzenie na przekaźniku z płyty wallboxa (zdjęcia `zdjecia\wallbox_plyta_przekaznik_NB90_2026-09-30_a/b.jpg`).

**Przekaźnik** `[F]`: Ningbo Baocheng (NBC) **NB90-12S-S-A**, jeden zestyk zwierny, cewka 12 V DC, nadruk „40A 240VAC 30VDC · 50A 277VAC · 2HP 240VAC · TV-15”, styki AgSnO₂; po jednym na fazę (3 szt. na płycie, obok bezpiecznik T2A250V i 3 kondensatory 470 µF 16 V). Strona producenta (nbc-relays.com, NB90 50 A „charging pile in Europe”): **trwałość elektryczna 1×10⁴ przełączeń** (przy zdolności łączeniowej 50 A), **mechaniczna 1×10⁷**; LCSC (wariant 40 A): 40 A/240 VAC, 40 A/30 VDC, 277 VAC, bez podanej trwałości; karty PDF (LCSC C396901) nie udało się pobrać. Przekaźniki tej samej klasy T90 (Hongfa HF105F-1, TE T90) podają w kartach typowo 1×10⁵ przy 30 A rezystancyjnie i 1×10⁷ mechanicznie `[Z — z pamięci, nie z pobranej karty]`. Przy 16 A trwałość elektryczna jest kilka razy większa niż przy prądzie znamionowym (zużycie styków rośnie mniej więcej z kwadratem prądu), ale liczy się tylko wtedy, gdy przekaźnik otwiera się pod prądem — a w sprawie Karola wallbox otwierał obwód przy 16,6 A (zadziałanie zabezpieczenia), więc liczyć trwałość elektryczną, nie mechaniczną.

**Pauzy na noc z symulacji** (`symulacja\wyniki.json`, `pauses_T0_*` = wznowienie natychmiastowe, `T[300]` = 5 min; jedna pauza = otwarcie + zamknięcie = 2 przełączenia):

| Dom | natychmiast, średnio | natychmiast, złe noce (p90) | 5 min, średnio | 5 min, p90 |
|---|---|---|---|---|
| A1 3×25 A, kuchnia elektryczna (waga 0,3) | 3,7 | 11,5 | 2,1 | 5,0 |
| A2 3×25 A + pompa ciepła | 12,7 | 28,1 | 7,0 | 12,0 |
| A3 3×16 A, starsza instalacja | 16,0 | 32,0 | 10,9 | 19,1 |
| A4 3×20 A | 11,9 | 30,2 | 5,4 | 10,1 |
| A5 3×25 A + podgrzewacz przepływowy 21 kW | 9,0 | 17,0 | 7,8 | 12,0 |
| A6 mieszkanie 1×25 A, wallbox 3,7 kW | 12,6 | 39,2 | 3,6 | 7,0 |
| A7 3×32 A | 0,7 | 2,0 | 1,2 | 2,0 |
| **średnia ważona** | **8,9** | — | **5,1** | — |

**Przeliczenie na rok** (250 nocy ładowania, 2 przełączenia na pauzę): średni dom 4 400 przełączeń natychmiast wobec 2 600 przy 5 min; dom 3×16 A 8 000 wobec 5 500; złe noce w mieszkaniu 1‑fazowym do 20 000 rocznie. **Czas do wyczerpania 10 000 przełączeń z karty producenta:** natychmiast 1–2 lata w słabszych domach (średni 2,3), 5 min 2–4 lata. **Przy 100 000 (klasa T90 przy 30 A):** natychmiast 12–23 lata, 5 min 18–40 lat.

**Wniosek** `[Z]`: 5 min zmniejsza liczbę cykli tylko ~1,7 raza, nie 10 razy; argument „żywotność przekaźnika” rozstrzyga o wyniku dopiero przy pesymistycznej karcie (10⁴) i otwieraniu pod prądem. Ważniejszy skutek natychmiastowego wznowienia to seria start–stop co kilkadziesiąt sekund przy indukcji i pompie ciepła (cykle puste) oraz auta, które po kilku przerwach przestają wznawiać. Jeśli wersja „dla niecierpliwych” ma powstać, rozsądniejsze minimum to 1–2 min niż 0. Wiadomość do Franka z tymi liczbami: rozmowa 30.09.
