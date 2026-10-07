# Przygotowanie do pierwszego dnia — AMPERE POINT (serwis)

Briefing pod listę od kierownika: seria P, rozłożenie prototypu, pierwsze kroki w Tuya, dostępy (Gmail / BaseLinker / Responso / WeChat) oraz instrukcja do serii P. Plus wyjaśnienie tego, co zaobserwowałeś na miejscu.

---

## 0. Twoje obserwacje — co one naprawdę znaczą

### 0.1. Pomiar Control Pilot multimetrem (stany >9 V, różnice rzędu miliwoltów)

To nie jest usterka ładowarki ani testera — to ograniczenie multimetru.

Sygnał CP powstaje tak: mikrokontroler ładowarki generuje przebieg prostokątny 1 kHz, wzmacniacz operacyjny zamienia go na ±12 V i podaje na linię przez rezystor szeregowy 1 kΩ. W stanie A nie ma jeszcze PWM — pilot to stałe +12 V. W stanach B/C/D pilot to fala: górą +12 V, dołem −12 V, a tester (strona auta) ściąga **dodatni szczyt** do 9 / 6 / 3 V swoimi rezystorami i diodą. To ten dodatni szczyt definiuje stan; dół zostaje na −12 V (kontrola obecności diody). Szerokość górnej części (wypełnienie) koduje oferowany prąd.

**Jak czyta to ładowarka:** przetwornik analogowo-cyfrowy próbkuje CP w rytm własnego PWM — raz w fazie wysokiej (łapie dodatni szczyt, czyli stan), raz w fazie niskiej (sprawdza −12 V, czyli diodę). To celowane próbkowanie, więc odczyt jest prawdziwy: 9/6/3 V.

**Jak czyta to multimetr:** multimetr nie próbkuje „w szczycie”. W trybie DC pokazuje wartość średnią całej fali, w trybie AC wartość skuteczną (RMS) — w obu liczy się też dół −12 V, obecny przez większość okresu. Dla fali o dodatnim szczycie Vp, dole −12 V i wypełnieniu D:

- średnia = Vp·D − 12·(1−D),
- RMS = √(Vp²·D + 12²·(1−D)).

Przy małym wypełnieniu (mały oferowany prąd) dominuje dół −12 V, więc wszystkie stany dają wartości skupione blisko 11–12 V, malejące tylko nieznacznie — dokładnie to, co zmierzyłeś (wszystko powyżej 9 V, różnice rzędu miliwoltów). Stan A wyszedł prawidłowo, bo tam CP to czyste +12 V stałe. Wniosek: multimetr pokazuje uśrednioną mieszankę, a nie poziom stanu — to artefakt pomiaru, nie usterka.

**Jak czyta to oscyloskop:** rysuje napięcie w czasie, więc widzisz wprost +12/−12 V, ściągnięty dodatni szczyt (9/6/3 V = stan), okres 1 ms i wypełnienie (= oferowany prąd). To jedyny prosty sposób, by odczytać stan poprawnie.

Praktyka: do CP bierz oscyloskop, nie multimetr. „B[B]” to prawdopodobnie B bez PWM (ładowarka widzi auto, jeszcze nie oferuje prądu) i B z PWM (gotowa, nadaje wypełnienie) — potwierdź w instrukcji testera.

### 0.2. Architektura z ~6 przekaźnikami i kilkoma PCB

To, że wyglądało inaczej niż w naszym modelu, jest spodziewane: w projekcie celowo uprościliśmy sterowanie do jednego stycznika i logiki. Prawdziwa ładowarka realizuje te same trzy pętle (bezpieczeństwo, sterowanie, aplikacja) w sprzęcie, stąd więcej elementów.

Sześć przekaźników w ładowarce 3-fazowej to najczęściej:

- **Główne łączenie mocy** — po jednym biegunie na fazę (L1, L2, L3), często też neutralny → 3 lub 4 przekaźniki.
- **Redundancja bezpieczeństwa** — wiele konstrukcji ma drugi łącznik w szeregu, żeby przy sklejeniu jednego styku drugi i tak przerwał obwód (wymóg „podwójnego przerwania”). To dokłada 1–2 przekaźniki.

Do tego zwykle 2–3 płytki: **sterująca** (mikrokontroler z logiką, front-end CP/PP), **mocy** (sterowniki przekaźników, pomiar prądu/energii, zabezpieczenia) i czasem **komunikacyjna/wyświetlacza**.

Co rozpoznać przy rozkładaniu prototypu (mapowanie na nasz model):

- stycznik/przekaźniki mocy — policz bieguny, sprawdź które są w szeregu (redundancja), a które na fazę,
- moduł różnicówki **RCD typ A + RDC-DD 6 mA DC**,
- układ pomiaru prądu i **niezerowalny licznik energii**,
- front-end **CP/PP** (generacja ±12 V, odczyt, rezystory PP),
- mikrokontroler / płytka sterująca (to „mózg” — pętla 2),
- zasilacz pomocniczy, czujniki temperatury (wtyk i obudowa).

Porównaj to z listą zabezpieczeń z karty produktu — wszystko powinno mieć fizyczny odpowiednik.

Dwa pojęcia z tego punktu:

- **Biegun** (przekaźnika lub stycznika) to jeden niezależny styk łączący jeden przewód. Stycznik to kilka takich styków sprzężonych mechanicznie i włączanych razem; „po jednym biegunie na fazę” znaczy jeden styk na L1, jeden na L2, jeden na L3 (i ewentualnie na N). Instalacja 3-fazowa wymaga przełączenia 3–4 przewodów, stąd 3–4 bieguny.
- **Front-end** to analogowy układ pośredniczący między cyfrowym sterownikiem a światem fizycznym. Front-end CP/PP z jednej strony zamienia logiczny przebieg z mikrokontrolera na ±12 V na linii CP (wzmacniacz + rezystor 1 kΩ), a z drugiej sprowadza napięcia CP/PP do poziomu, który bezpiecznie zmierzy przetwornik mikrokontrolera (dzielnik, układ ograniczający). To „pierwszy stopień” stykający procesor z rzeczywistym sygnałem.

---

## 1. Seria P — co musisz wiedzieć

Seria P to **prosta, przenośna** linia z wyświetlaczem, bez WiFi i aplikacji (to domena serii Q). Idealna na start: cała „inteligencja” jest w jednym układzie, a diagnostyka opiera się na CP, zabezpieczeniach i liczniku.

| Model | Moc | Wtyczka wejściowa | Cena det. |
|---|---|---|---|
| P35 | 3,7 kW (230 V × 16 A) | gniazdo sieciowe 230 V | ~689 zł |
| P72 | 7,2 kW (230 V × 32 A) | CEE 32 A | ~799 zł |
| P11 | 11 kW (3 × 230 V × 16 A) | CEE 16 A | ~999 zł |

Prąd a moc (P35 vs P72 — obie jednofazowe). Moc jednofazowa to P = U·I przy U = 230 V, więc 16 A daje 230 × 16 ≈ 3,68 kW, a 32 A daje 230 × 32 ≈ 7,36 kW. Czyli dwa razy większy prąd to dwa razy większa moc — skaluje się wprost. Rozbieżność, którą widać w katalogu (3,7 kW oraz raz „7,2 kW”, raz „7,4 kW”), bierze się tylko z zaokrąglenia tej samej wartości 7,36 kW, a nie z fizyki.

Moc przestaje być wprost proporcjonalna do prądu dopiero, gdy zmienia się coś poza prądem: napięcie, liczba faz albo współczynnik mocy. Dla kontrastu P11 ma ten sam prąd 16 A co P35, ale 11 kW zamiast 3,7 kW — bo jest trójfazowa (P = 3·U·I), więc dodatkowa moc bierze się z trzech faz, nie z większego prądu.

Wspólne cechy: ekran 2,4", regulacja prądu (P72: 8/16/20/24/32 A), opóźnienie startu (zegar do 12 h), monitoring temperatury wtyku i obudowy z autostopem, „automatyczna korekta błędów”. Zabezpieczenia: **RCD typ A 30 mA AC + RDC-DD 6 mA DC**, nadprąd, przepięcie/zanik, zwarcie, upływ, brak/zły PE, przegrzanie. Normy: IEC 61851, IEC 62196-2; IP65/IP67 (rozbieżność karta vs instrukcja — warto wyjaśnić). Przewód 6 m, żyły 3 × 6 mm² + 1 × 0,5 mm² (ta cienka to właśnie CP/sygnał).

Dwie ważne rzeczy z dokumentacji:
- Istnieje gotowa instrukcja „Instrukcja_AMP_P_and_B_Series_EU_2025” (EN/DE/PL/CZ) — punkt wyjścia do zadania „instrukcja do P”.
- W opiniach klientów pojawia się skarga na **rozbieżność licznika energii** względem rzeczywistości — to realny, znany słaby punkt (i dokładnie to, co weryfikował nasz projekt).

### Kody błędów serii P (z instrukcji) — ściąga serwisowa

| Kod | Znaczenie | Pierwszy krok diagnozy |
|---|---|---|
| A | Przegrzanie | sprawdź prąd obciążenia; ostudź; jeśli wraca — serwis |
| B | Zwarcie (wykrycie) | odłącz i wepnij ponownie; jeśli błąd znika bez auta → zwarcie CP po stronie auta |
| C | Przepięcie | napięcie zasilania > 270 V; poczekaj na normalizację |
| D | Podnapięcie | napięcie zasilania < 150 V |
| E | Uziemienie/PE (brak lub zamiana L–N) | sprawdź instalację; PE i kolejność L/N |
| F | Zabezpieczenie przeciwzwarciowe | jeśli po odłączeniu auta działa → zwarcie po stronie auta |
| G | Upływ (różnicówka) | jak F; jeśli wraca bez auta → serwis |
| H | Inne | wsparcie techniczne |

---

## 2. Testowanie z autem i diagnostyka

„Testowanie z autem” to sprawdzenie pełnego cyklu na rzeczywistym pojeździe: podłączasz, obserwujesz przejście stanów (A→B→C), start ładowania, ustawiany prąd, narastanie energii, poprawne zakończenie i rozłączenie. Auto jest „grzecznym” partnerem — pokazuje, że podstawowy tor działa, ale nie wymusi przypadków brzegowych (od tego jest tester stanów).

Co realnie sprawdzać:
- **Handshake CP** — czy stany przełączają się czysto, czy ładowarka oferuje właściwy prąd (wypełnienie PWM na oscyloskopie).
- **Prąd i moc** — czy zgadza się z nastawą i z autem.
- **Bezpieczeństwo** — reakcja na brak/zły PE (błąd E), zachowanie różnicówki.
- **Licznik energii** — porównanie z miernikiem odniesienia (znany słaby punkt).
- **Temperatura** — czy autostop działa.

Narzędzia, które warto znać (i zapytać, czym dysponuje firma):
- **Tester stanów CP** (ten, który już widziałeś) — wymusza stany A/B/C/D, do szybkiej diagnozy bez auta.
- **Oscyloskop** (np. zestawy Pico do EV) — jedyny sposób, by wiernie zobaczyć falę CP i wypełnienie.
- **Adapter/analizator EVSE** do mierników bezpieczeństwa — np. Sonel EVSE-01, Metrel A1632 — do pomiarów bezpieczeństwa stacji/przewodów (izolacja, pętla zwarcia, RCD, ciągłość PE).

Bezpieczeństwo: tor mocy to 230/400 V. Pomiary pod napięciem tylko z właściwymi środkami i wiedzą; CP/PP są niskonapięciowe i bezpieczniejsze do nauki.

---

## 3. Rozłożenie prototypu — na co patrzeć

Cel: ocenić „co jest w środku” i jak to się ma do specyfikacji. Praktyczna lista (oprócz pkt 0.2):

1. Policz bieguny łączników mocy i ustal, które są w szeregu (redundancja bezpieczeństwa), a które na fazę.
2. Znajdź moduł różnicówki i osobny układ detekcji 6 mA DC (RDC-DD) — to wyróżnik „dedykowane dla EV”.
3. Zlokalizuj pomiar prądu (boczniki/przekładniki/Hall) i układ licznika energii.
4. Zidentyfikuj front-end CP/PP i mikrokontroler sterujący.
5. Sprawdź zasilacz pomocniczy i czujniki temperatury.
6. Wypisz różnice względem aktualnej serii produkcyjnej — to jest sedno „oceny prototypu”.

Pytanie do zanotowania: czym ten prototyp różni się od obecnej serii i dlaczego (nowy firmware? inny układ mocy? inny licznik?).

---

## 4. Tuya — pierwsze kroki

Dotyczy modeli z WiFi (seria Q / PRIME), nie serii P. Podstawy:

1. Zainstaluj aplikację **Tuya Smart** (lub Smart Life) i załóż konto (e-mail/telefon).
2. Wprowadź ładowarkę w tryb parowania — zwykle przytrzymanie przycisku ~5 s, aż ikona WiFi zacznie migać.
3. W aplikacji dodaj urządzenie, wybierz sieć WiFi (2,4 GHz) i podaj hasło; aplikacja sama skonfiguruje połączenie.
4. Po sparowaniu masz zdalny podgląd i sterowanie: status, prąd, harmonogram, licznik.

Ekosystem Tuya współpracuje z Google Home, Alexa i Home Assistant. Zapytaj, czy firma ma konto producenta/administratora w Tuya (do zarządzania wieloma urządzeniami), czy korzysta tylko z konta użytkownika.

---

## 5. Dostępy — co to jest i jak zacząć

- **Gmail** — firmowa skrzynka; podstawowy kanał z klientem i wewnątrz. Skonfiguruj na telefonie i w przeglądarce, ustaw podpis.
- **BaseLinker** — platforma do zarządzania sprzedażą wielokanałową: zamówienia z różnych kanałów (Allegro, Amazon, sklep), magazyn, kurierzy, faktury — wszystko w jednym panelu. W serwisie używana do zamówień, stanów magazynowych i obsługi zwrotów/reklamacji (RMA).
- **Responso** — centralny hub obsługi klienta (to jest „reponso” z listy). Zbiera wiadomości z wielu źródeł w jeden system zgłoszeń (ticketów) i jest **zintegrowane z BaseLinkerem**: do ticketu podciągane są dane zamówienia, można zmieniać statusy i pobierać etykiety. Tu będziesz prowadzić komunikację serwisową z klientami.
- **WeChat** — komunikator do kontaktu z **fabryką w Chinach**. Zainstaluj, załóż konto (potrzebny numer telefonu; czasem aktywacja wymaga potwierdzenia przez innego użytkownika). Przydatne: wbudowane tłumaczenie wiadomości, przesyłanie zdjęć/plików. Pamiętaj o różnicy czasu (Chiny UTC+8) i pisz zwięźle, konkretnie, z numerami modeli i zdjęciami.

---

## 6. Instrukcja do serii P — co już jest, co można poprawić

Istniejąca instrukcja (P i B) ma układ: bezpieczeństwo → opis funkcji → ekran/LED → parametry → bezpieczne użycie → start/koniec ładowania → kody błędów A–H → gwarancja → deklaracja zgodności. To instrukcja **użytkownika**.

Możliwe kierunki pracy nad „instrukcją do P” (warto zaproponować):
- Wersja **serwisowa** obok użytkowej: rozszerzone kody błędów z drzewem decyzyjnym diagnozy, punkty pomiarowe (CP na oscyloskopie, RCD, PE), procedura RMA.
- Ujednolicenie rozbieżności (IP65 vs IP67 na karcie/instrukcji; adres serwisu biuro@emaxima.pl vs hello@amperepoint.com).
- Krótka tabela „objaw → prawdopodobna przyczyna → działanie” dla najczęstszych zgłoszeń (w tym rozbieżność licznika energii).
- Spójne nazewnictwo i jednostki (na karcie zdarzają się literówki, np. „moc w Voltach”).

---

## 7. Co wziąć i o co zapytać (pokazuje inicjatywę)

Pytania na pierwszy dzień:
- Jakiego testera EVSE i oscyloskopu używamy do CP i diagnostyki?
- Jak wygląda standardowy proces serwisu/RMA dla serii P?
- Jakie są najczęstsze usterki i reklamacje serii P?
- Tuya: mamy konto producenta/administratora czy użytkownika?
- WeChat: z kim po stronie fabryki się kontaktuję i w jakich sprawach?
- BaseLinker/Responso: jaka jest moja rola w obiegu zgłoszeń?

Dobrze mieć przy sobie: oscyloskop (jeśli jest), multimetr (ale ze świadomością ograniczeń przy CP), notatnik na różnice prototypu.

---

## 8. Matematyka prądu, napięcia, mocy i energii (przypomnienie)

Podstawowe wielkości i jednostki:

- Prąd to przepływ ładunku: i = dq/dt; jednostka amper (A = C/s).
- Napięcie to energia na jednostkę ładunku: u = dW/dq; jednostka wolt (V = J/C).
- Moc chwilowa: p(t) = u(t)·i(t); jednostka wat (W = V·A).
- Energia to całka mocy po czasie: E = ∫ p(t) dt; jednostka dżul (J = W·s). W rozliczeniach 1 kWh = 3,6 MJ, więc E[kWh] = (1/3 600 000)·∫ p dt.

Wartość średnia i skuteczna (przydają się przy AC i PWM):

- Średnia: ⟨x⟩ = (1/T)·∫ x dt.
- Skuteczna (RMS): X = √((1/T)·∫ x² dt). Moc na rezystancji zależy od kwadratu, więc od RMS: P = U²/R = U·I (wartości skuteczne).
- W sieci AC: P = U·I·cosφ, gdzie cosφ to współczynnik mocy. Trzy fazy: P = 3·U_f·I·cosφ.

PWM i kodowanie wartości:

- Fala prostokątna o poziomach 0 i V oraz wypełnieniu D ma wartość średnią V·D. To jest istota kodowania: wypełnienie niesie wartość (na linii CP — oferowany prąd), a uśrednienie (filtr RC albo całkowanie) tę wartość odzyskuje. Sterowanie mocą przez PWM działa tak samo: zmieniasz wypełnienie, zmienia się dostarczana wartość średnia.

Układy, które to realizują:

- Pomiar prądu: bocznik (z prawa Ohma u = R·i mierzysz spadek napięcia) albo czujnik Halla (bezstykowo, z pola magnetycznego). Pomiar napięcia: dzielnik rezystorowy.
- Mnożenie u·i: układ mnożący analogowy albo (częściej) mikrokontroler próbkuje u oraz i przetwornikiem i mnoży je cyfrowo.
- Całkowanie (energia): analogowo — integrator, czyli wzmacniacz operacyjny z kondensatorem (napięcie na kondensatorze jest proporcjonalne do całki wejścia); cyfrowo — sumowanie próbek mocy w czasie. Niezerowalny licznik energii to zwykle dedykowany układ liczący ∫ u·i dt i wystawiający impulsy (stała liczba impulsów na kWh).
- Różniczka i całka spotykają się tu wprost: prąd jest pochodną ładunku, a energia całką mocy; licznik energii to po prostu integrator iloczynu u·i.

---

## 9. Zabezpieczenia — na nadmiar czego działają, jak i jak wpięte

Każde zabezpieczenie reaguje na nadmiar lub niedomiar konkretnej wielkości i jest inaczej włączone w obwód.

- Nadprądowe i przeciwzwarciowe (błąd B i F): reagują na nadmiar prądu w torze mocy. Detekcja przez pomiar prądu (bocznik/Hall) lub klasyczny wyłącznik nadprądowy. Wpięte szeregowo w tor mocy; po przekroczeniu rozłączają stycznik lub przerywają obwód.
- Różnicowoprądowe (RCD typ A + RDC-DD 6 mA DC, błąd G): reaguje na nadmiar prądu upływu, czyli różnicy między prądem fazy a prądem przewodu neutralnego (to, co ucieka do ziemi lub przez człowieka). Przekładnik sumujący obejmuje fazę i neutralny; gdy ich suma odbiega od zera powyżej progu (30 mA dla składowej przemiennej, 6 mA dla gładkiej składowej stałej) — rozłączenie. Wpięte obejmująco (przewody przechodzą przez wspólny rdzeń).
- Przepięciowe i podnapięciowe (błąd C i D): reagują na nadmiar lub niedomiar napięcia zasilania. Pomiar napięcia dzielnikiem; poza zakresem (tu >270 V lub <150 V) ładowarka blokuje pracę. Dodatkowo warystory odprowadzają przepięcia atmosferyczne do PE (wpięte równolegle).
- Przegrzania (błąd A): reaguje na nadmiar temperatury. Czujniki we wtyku i obudowie; powyżej progu autostop, wznowienie po ostygnięciu.
- Uziemienia/PE (błąd E): reaguje na brak lub błąd przewodu ochronnego, w tym zamianę L–N. Monitoruje obecność i potencjał PE; bez poprawnego PE praca jest blokowana.

Trzy typowe sposoby wpięcia: szeregowo (nadprądowe, stycznik — przerywają tor), obejmująco (różnicówka — mierzy różnicę prądów) oraz pomiarowo/równolegle (napięcie, temperatura, ochronniki przepięć).

---

## 10. Przewód neutralny (N) a ochronno-neutralny (PEN) — fizyka i działanie

W instalacji występują przewody o różnych rolach: fazowy (L), neutralny (N), ochronny (PE). PEN łączy funkcje N i PE w jednym przewodzie.

- Neutralny (N): przewód roboczy. Prowadzi prąd powrotny odbiornika (w układzie 3-fazowym — prąd nierównowagi faz). Ponieważ płynie nim prąd, ma spadek napięcia (u = i·Z), więc jego potencjał wzdłuż trasy nie jest dokładnie zerem ziemi i nieco rośnie pod obciążeniem.
- Ochronny (PE): przewód bezpieczeństwa. Normalnie nie płynie nim prąd roboczy, więc jego potencjał jest praktycznie równy ziemi na całej długości. Łączy metalowe obudowy z ziemią i daje drogę prądowi zwarcia, co wyzwala zabezpieczenie, zanim obudowa stanie się niebezpieczna.
- Ochronno-neutralny (PEN): jeden przewód pełniący obie funkcje naraz (układ TN-C). Fizyka problemu: skoro tym samym przewodem płynie prąd roboczy, to ma on spadek napięcia, a zarazem jest odniesieniem ochronnym — więc obudowy podpięte do PEN nie są dokładnie na potencjale ziemi. Co gorsza, jeśli PEN się przerwie, prąd roboczy traci powrót, a obudowy podłączone do tego przewodu mogą znaleźć się pod napięciem fazowym. To realne zagrożenie.

Dlatego nowoczesne instalacje rozdzielają PEN na osobne PE i N (układ TN-S, albo TN-C-S z rozdziałem w rozdzielnicy), a do odbiorników — w tym ładowarek EV — prowadzi się osobny, pewny PE. Ładowarka wymaga poprawnego PE i go monitoruje (błąd E), bo użytkownik dotyka nadwozia auta: przerwany lub zamieniony PE musi zablokować ładowanie. W instalacjach TN-C-S stosuje się też wykrywanie zaniku PEN, właśnie z powodu powyższego ryzyka.

Różnica w skrócie: N prowadzi prąd i bywa pod napięciem, PE jest czystym odniesieniem bezpieczeństwa bez prądu, a PEN łączy obie role — wygodnie, lecz ryzykownie, dlatego przy ładowaniu EV preferuje się osobny PE.

---

## Źródła
- AMPERE POINT — seria P (P72): https://www.amperepoint.pl/products/portable-charger-32a-7-2kw-type-2-display-bag-included-red-cee
- Instrukcja AMP P & B Series EU 2025 (PDF): https://cdn.shopify.com/s/files/1/0780/2218/1190/files/Instrukcja_AMP_P_and_B_Series_EU_2025.pdf
- Tuya Smart — konfiguracja urządzeń: https://www.kristronik.com/instrukcje/konfiguracja-urzadzen-z-aplikacja-tuya-smart-life/
- BaseLinker — czym jest: https://sellify.pl/baselinker-co-to-jest-jak-dziala-i-czy-warto-korzystac-z-tego-systemu-w-sprzedazy-marketplace/
- Responso x BaseLinker (integracja): https://baselinker.com/pl-PL/blog/responso-i-baselinker-co-nowego-w-integracji/
- Diagnostyka CP oscyloskopem / adaptery EVSE: https://www.merserwis.pl/blog/artykul/badanie-stacji-evse-elektromobilnosc
- Instrukcja serii P (publiczna, do pobrania ze strony produktu) — link wyżej.
- CP/PWM reference design (schemat, wzmacniacz LM7332, ±12 V, R 1 kΩ): https://www.beyondlogic.org/prototype-iec61851-j1772-evse-interface/
- NXP EasyEVSE — dokumentacja stacji ładowania (budowa, CP): https://www.nxp.com/docs/en/user-manual/UM12110-v1.pdf
- Pico — pomiar komunikacji CP oscyloskopem (Type 2): https://www.picoauto.com/library/automotive-guided-tests/electric-vehicles/charger-vehicle-tests/AGT-896-charger-vehicle-communications-type-2/
- EV Charger Engineering — AC Chargers (budowa i działanie): https://www.porticos.net/ev-chargers-ac-chargers/
