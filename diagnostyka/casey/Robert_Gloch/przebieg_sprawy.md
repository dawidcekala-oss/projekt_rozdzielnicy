# Robert Gloch — „High Voltage Reminder”, ładowarka nie ładuje

**Kanał:** e‑mail (hello@) · **Od:** 2026‑10‑02 · **Stan:** **ZAMKNIĘTA 2026‑10‑06** — urządzenie sprawdzone także na samochodzie, bez usterki; wraca do klienta bez naprawy
**Materiały:** `konwersacja\` (wiadomość klienta), `zdjecia_klienta\` (dwa zdjęcia ekranu), `nasze_zdjecia\` (test w serwisie).

`[F]` fakt · `[Z]` założenie albo wniosek

---

## Zamknięcie (2026-10-06)

Dawid: „sprawa zamknięta już. testowane na aucie i wraca do klienta”. Poza testami na gnieździe zwykłym i siłowym ładowarka przeszła test ładowania samochodu; usterki nie stwierdzono, urządzenie wraca do klienta bez naprawy. `[F — relacja Dawida]` Która wersja maila poszła do klienta — nieustalone.

## Wynik diagnostyki i zalecenie (2026-10-06)

**Wynik serwisu:** w przeprowadzonych testach nie stwierdzono usterki ładowarki. Dawid potwierdził sprawdzenie na gnieździe zwykłym 230 V i siłowym; na żadnym komunikat nie wystąpił. `[F — relacja Dawida]`

**Zalecenie na podstawie dostępnych wyników:** odesłanie urządzenia bez naprawy, z informacją o wyniku testów i zaleceniem sprawdzenia instalacji zasilającej przez elektryka. Wysyłka i odpowiedź do klienta nie są jeszcze potwierdzone. To wynik diagnostyki, nie automatyczne rozstrzygnięcie prawne reklamacji.

**Podejrzenie przyczyny:** warunki zasilania lub sposób podłączenia u klienta. Błędne podłączenie N pozostaje hipotezą; nie stwierdzono konkretnego błędu instalacji pomiarem. Nie przypisywać winy elektrykowi na podstawie samych zdjęć.

**Zdjęcia a gniazdo 230 V:** według Dawida przy zasilaniu jednego kanału oczekiwane są dwa zera na ekranie. Żadne zdjęcie klienta nie przedstawia takiego układu. Brak potwierdzenia zdjęciowego błędu przy takim podłączeniu; nie ustalono, z jakiego połączenia wykonano każde zdjęcie. Relacja klienta o błędzie na 230 V pozostaje relacją, której serwis nie odtworzył.

**Korekta wcześniejszej analizy:** 000 na ekranie samo w sobie nie dowodzi obecności tej samej fazy na L i N. Zakres prawidłowy 280–480 podany przez producenta nie ustala granicy liniowości toru pomiarowego. Nasycenie pomiaru, rzeczywiste 400 V u klienta i przewidywany wynik 000/580/500 nie zostały potwierdzone. Wycofuję propozycję celowego podania 400 V na wejście L–N urządzenia klienta. Żadna z tych hipotez nie jest podstawą wyniku serwisu.

Poniżej zachowana historia wcześniejszych interpretacji. W razie sprzeczności obowiązuje powyższy wynik z 06.10.

## Historia analizy (2026-10-05, zastąpiona wynikiem z 06.10)

**Ładowarka sprawna w pomiarze napięć** `[F]`: na naszym stanowisku (G8) każdy kanał dostaje to samo napięcie fazowe co w prawdziwej sieci; ekran 388 (= 224 V), bez komunikatu, na wyjściu 227 V na L1–L3. Test jest miarodajny dla toru pomiaru (korekta mojej wcześniejszej tezy — Dawid).

**Najbardziej prawdopodobne: faza na zacisku N gniazda trójfazowego** (hipoteza Dawida) `[Z]`. Zdjęcie A (000 / 582 / 495): dokładne zero na jednym kanale = zacisk tej fazy i zacisk N na tym samym przewodzie; dwa pozostałe kanały dostają napięcie międzyfazowe 400 V — ponad zakres (do 277 V), stąd „High Voltage”, a odczyty poniżej teoretycznych ~690 i różne najpewniej przez nasycenie toru pomiaru `[Z]`. Pomiar elektryka „230 V fazowe, 400 V międzyfazowe” nie wyklucza tego, jeśli fazy mierzył względem PE, a nie N.

**Zdjęcie B (602 / 231 / 228)** — nie pasuje do gniazda 230 V z poprawnym N (348 V na jednym kanale jest tam niemożliwe); skąd pochodzi — nieustalone. Ładowarka nie ma adapterów, więc do gniazda 230 V klient musiał użyć własnej przejściówki (połączenia nieznane).

*05.10: propozycja maila z prośbą o te pomiary odrzucona przez Dawida („o czym ty w ogóle mówisz?”) — urządzenie jest u nas i działa; dalszy krok to decyzja serwisu, nie prośba o dane.* **Rozstrzygające u klienta (wiedza do ewentualnego zalecenia, nie prośba):** elektryk mierzy w gnieździe trójfazowym napięcie N–PE (prawidłowo ok. 0 V; przy fazie na N ok. 230 V) oraz każdą fazę względem N (przy fazie na N: jedna ok. 0 V, dwie ok. 400 V). Zapytać, czy ostatnio coś zmieniano w instalacji (ładowarka działała od 10.2025).

Opcjonalnie u nas: odtworzenie (faza na zacisku N przy prawdziwym zasilaniu trójfazowym) — powinno dać ok. 000 / ~580 / ~500. Ryzyko: 400 V na zasilaczu urządzenia klienta (przetrwał to już u klienta, ale to poza specyfikacją).

### Pierwsza wersja analizy — korekty (Dawid, 05.10)
1. Zdjęcie B przypisane do gniazda 230 V bez podstawy — wartości temu przeczą.
2. Hipoteza „styk N w adapterze” — ładowarka nie ma adapterów.
3. „G8 nie sprawdza pracy na prawdziwej sieci” — dla toru pomiaru napięć sprawdza tak samo.
4. „Zdjęcie A niespójne → kanał pokazuje coś innego niż napięcie” — pominięte nasycenie pomiaru powyżej zakresu.

## Przebieg

| Data | Kto | Co |
|---|---|---|
| 15.10.2025 | klient | Zakup ładowarki (według wiadomości). Model — do ustalenia (okrągły wyświetlacz, przyciski Current/Timer, jak w U‑028). |
| 01.10.2026 | klient | Ładowarka przestała ładować; błąd „brak napięcia na jednej fazie i wysokie napięcia na pozostałych”; to samo po podłączeniu do gniazda 230 V. `[F — wiadomość]` |
| 02.10.2026 09:04 | klient | Wiadomość: elektryk sprawdził oba gniazda — fazowe 230 V, międzyfazowe 400 V; auto ładuje zwykłą ładowarką fabryczną; prośba o szybkie rozpatrzenie reklamacji. Zdjęcia ekranu: **High Voltage Reminder 000 / 582 / 495 V** oraz **High Voltage Reminder 602 / 231 / 228 V** (nie podał, które z którego gniazda). `[F]` |
| do 05.10 | serwis | Urządzenie u nas (oznaczone „GLOCH”): ekran spoczynkowy 16 A, 388 V, bez błędu; tester PM701E — 227,0 / 227,1 / 227,4 V na L1 / L2 / L3 względem PE. `[F — nasze zdjęcia]` |
| 05.10 | Dawid | Hipoteza: słaby elektryk podpiął fazy i N w odwrotnej kolejności — na dwóch fazach napięcie międzyfazowe, na trzeciej 0. |
| 05.10 | Dawid | Korekty mojej analizy: zdjęcie B nie pasuje do 230 V; ładowarka bez adapterów; mostek na G8 odzwierciedla prawdziwą sieć. |
| 06.10 | serwis | **Test na gnieździe zwykłym 230 V i na siłowym — na żadnym błąd się nie wyświetla.** `[F — relacja Dawida]` Na zwykłym gnieździe niezasilone kanały pokazują 000, więc ekran miałby dwa zera — zdjęcia z gniazda 230 V klient najpewniej nie przysłał (oba zdjęcia z połączenia trójfazowego) `[Z — Dawid]`. |
| 06.10 | serwis | Test ładowania samochodu — bez błędu. **Sprawa zamknięta, urządzenie wraca do klienta.** `[F — relacja Dawida]` |

## Ustalenia (2026‑10‑05)

**Skala liczb na ekranie** (rozmowa z producentem z 08.09.2026, sprawa U‑028: „三个数值为线电压 / 是输入电压 / 正确范围是280V—480V”): liczba ÷ √3 = napięcie fazowe danej fazy; zakres pracy 280–480 = 162–277 V. Potwierdzone także tutaj: ekran spoczynkowy 388 ↔ 224 V na stanowisku. `[F]`

| Zdjęcie | Ekran | ÷ √3 (V) |
|---|---|---|
| A | 000 / 582 / 495 | 0 / 336 / 286 |
| B | 602 / 231 / 228 | 348 / 133 / 132 |

**Hipoteza „zamiana faz i N”** `[F — obliczenie]` *(Korekta 05.10: wariant „faza na zacisku N” pasuje do zdjęcia A, jeśli tor pomiaru nasyca się powyżej zakresu — patrz „Stan i następny krok”; poniższe dotyczy pomiaru liniowego i ścisłej zamiany N z fazą)*:
- Zamiana N z jedną fazą w gnieździe dałaby **ok. 398 / 690 / 690** (230 V na jednym kanale, 400 V międzyfazowe na dwóch), stabilnie. Na zdjęciach nie ma żadnej wartości bliskiej 690 i nie ma 398.
- Nawet w wersji „dwie międzyfazowe + zero” dwie niezerowe wartości byłyby **równe** (obie 400 V). Tu 582 i 495 to 336 i 286 V — różne i żadna nie jest napięciem międzyfazowym.
- ~~Ten sam błąd na gnieździe 230 V (602 → 348 V między L a N) nie może wynikać z połączeń w gnieździe trójfazowym.~~ *Korekta: brak podstaw, że zdjęcie B jest z gniazda 230 V.*

*Wersja pierwsza, częściowo nieaktualna — patrz „Stan i następny krok” i korekty.* **Co pasowało w pierwszej wersji: przesunięty („pływający”) przewód neutralny** `[Z]`. W bazie wiedzy (sekcja Low Voltage Reminder) zapisany obraz przerwy N: „dwie wartości podwyższone powyżej 480, jedna zaniżona” — zdjęcie A dokładnie takie (582 i 495 > 480, trzecia 0). 348 V między L a N na gnieździe jednofazowym jest możliwe tylko przy przesuniętym N. Miejsce przerwy — dwie możliwości:
1. **Instalacja klienta** (wspólny N dla obu gniazd; luźny zacisk N/PEN widoczny dopiero pod obciążeniem — pomiar elektryka bez obciążenia mógł wyjść poprawnie). Przeciw: auto ładuje się ładowarką fabryczną; klient nie wspomina o innych objawach w domu.
2. **Droga N w ładowarce lub adapterze** (styk N we wtyku / złączu adaptera, przewód) — wspólna dla obu gniazd, przerywana; na stanowisku styk mógł akurat przewodzić. Za: oba gniazda, elektryk i ładowarka fabryczna mówią „instalacja OK”.

Zastrzeżenie: zdjęcie A nie daje się złożyć w jeden spójny trójkąt napięć (przy 336 i 286 V trzecia faza musiałaby mieć ok. 115 V, a nie 0) — co najmniej jeden kanał nie pokazuje rzeczywistego napięcia albo wartości nie są z tej samej chwili. `[F — obliczenie; Z — interpretacja]`

## Dalszy krok

- Przekazać klientowi wynik testów i zalecenie sprawdzenia instalacji; odesłać urządzenie bez naprawy. Wykonanie tych działań niepotwierdzone.

## Szkic maila do klienta — wersja 1 (2026-10-06, zastąpiony wersją 2 poniżej)

Dzień dobry Panie Robercie,

Dziękuję za przesłanie ładowarki. W przeprowadzonych testach nie stwierdziliśmy usterki urządzenia, dlatego odsyłamy je bez naprawy.

Ładowarkę sprawdziliśmy zarówno na zwykłym gnieździe 230 V, jak i na gnieździe siłowym. W obu przypadkach działała prawidłowo, a komunikat „High Voltage Reminder” nie wystąpił.

Przed ponownym podłączeniem ładowarki proszę o sprawdzenie instalacji zasilającej przez elektryka z uprawnieniami, ze szczególnym uwzględnieniem poprawności podłączenia przewodu neutralnego oraz napięć w gnieździe.

Pozdrawiam,
Dawid Cekała
Ampere Point

## Szkic maila do klienta — wersja 2 (2026-10-06, niewysłany)

Dzień dobry Panie Robercie,

Dziękuję za przesłanie ładowarki i zdjęć. Zakończyliśmy sprawdzenie urządzenia — zarówno na zwykłym gnieździe 230 V, jak i na gnieździe siłowym pracowało prawidłowo. W przeprowadzonych testach nie stwierdziliśmy usterki, a komunikat „High Voltage Reminder” nie wystąpił.

Chciałbym też wyjaśnić, dlaczego zalecamy ponowne sprawdzenie zasilania. Ładowarka kontroluje napięcie każdej fazy względem przewodu neutralnego N. Nieprawidłowe podłączenie tego przewodu lub jego luźny styk mogą powodować, że napięcie na części wejść będzie zaniżone, a na innych zawyżone. W takiej sytuacji zabezpieczenie napięciowe może uniemożliwić rozpoczęcie ładowania.

To jedna z możliwych przyczyn wskazań widocznych na przesłanych zdjęciach, choć na ich podstawie nie możemy potwierdzić konkretnego błędu w instalacji. Prawidłowe napięcia między fazami nie wykluczają problemu z przewodem neutralnym. Dlatego mimo wcześniejszego sprawdzenia gniazd proszę, aby elektryk zweryfikował właśnie podłączenie i pewność styku przewodu N oraz napięcia poszczególnych faz względem niego. Pozwoli to sprawdzić warunki zasilania, które są istotne dla pracy tej ładowarki.

Ładowarkę odsyłamy do Pana bez naprawy, ponieważ podczas kontroli działała prawidłowo. Domyślnie przesyłka zostanie skierowana na adres dostawy z pierwotnego zamówienia.

Pozdrawiam,
Dawid Cekała
Ampere Point

### Uwagi redakcyjne do wersji 2

Na polecenie Dawida: łagodniejszy ton i wyjaśnienie podejrzewanej przyczyny. Opis N jest hipotezą, nie ustaloną wadą instalacji; bez oskarżania elektryka, bez prośby o przesłanie pomiarów i bez interpretowania cyfr jako dowodu zamiany przewodów.

Źródło mechanizmu ogólnego: badanie „Neutral Conductor Loss in Residential Photovoltaic Installations: Overvoltage Analysis and Design of a Contactor-Based Automatic Transfer Switch”, https://www.mdpi.com/1996-1073/19/10/2346 — opis spadków i wzrostów napięć przy utracie N w niesymetrycznie obciążonym układzie trójfazowym. Nie jest to potwierdzenie przyczyny w urządzeniu Glocha.

**Ustalenie Dawida (2026-10-06):** domyślny adres odesłania to adres dostawy z pierwotnego zamówienia; dopisano do aktualnego szkicu. Wysyłka nadal niepotwierdzona.

## Odwrócenie kolejności N i faz — rozpisanie zacisków (2026-10-06)

Obliczenie warunkowe, a nie potwierdzenie połączeń w gnieździe klienta. Zakładamy sprawną sieć 230/400 V, PE bez zmian, wszystkie cztery różne przewody podłączone dokładnie raz. Umowna kolejność zacisków od lewej: L1, L2, L3, N. Po odwróceniu kolejności przewodów do tych zacisków trafia N, L3, L2, L1. To przykład logicznego przypisania, nie uniwersalny rozkład styków gniazda CEE.

| Zacisk ładowarki | Przewód z instalacji po odwróceniu | Względem rzeczywistego N / w przybliżeniu PE | Względem zacisku N ładowarki |
|---|---|---|---|
| L1 | N | ok. 0 V | ok. 230 V |
| L2 | L3 | ok. 230 V | ok. 400 V |
| L3 | L2 | ok. 230 V | ok. 400 V |
| N | L1 | ok. 230 V | 0 V (ten sam zacisk) |

Ładowarka między własnymi L1–N, L2–N, L3–N otrzyma zatem około **230 / 400 / 400 V**, nie 0 / 400 / 400 V. N instalacji na wejściu L1 ma 0 V względem rzeczywistego N, ale względem zacisku N ładowarki, na który trafiła faza, jest 230 V. Jeżeli umowna kolejność była N,L1,L2,L3, jej odwrócenie daje na kanałach L1–N / L2–N / L3–N odpowiednio 400/400/230 V. Zestaw wartości jest ten sam, zmienia się kanał z 230 V.

Przy liniowym przeliczniku ekranu ×√3 odpowiadałoby to około 400 / 690 / 690. To obliczenie teoretyczne; nie potwierdza wskazań firmware przy nadmiernym napięciu. Samo odwrócenie przewodów nie wyjaśnia więc zdjęcia 000/582/495. Wcześniejsze powiązanie tej hipotezy z zerem na kanale było zbyt daleko idące. Nasycenia pomiaru nie wykazano. Stanowisko serwisu pozostaje: w wykonanych testach usterki ładowarki nie stwierdzono; konkretne połączenia u klienta nieznane.

Źródło wartości znamionowych 230/400 V: Schneider Electric, Electrical Installation Guide — Definition of voltage ranges, https://www.electrical-installation.org/enwiki/Definition_of_voltage_ranges . Przypisanie przewodów i wynikowe różnice potencjałów: obliczenie dla powyższego założenia.
