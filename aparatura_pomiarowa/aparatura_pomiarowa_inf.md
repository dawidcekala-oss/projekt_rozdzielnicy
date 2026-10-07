# APARATURA POMIAROWA — informacje i przekazanie kontekstu
**AMPERE POINT · pomiary elektryczne stacji/ładowarek AC EV · stan: 2026-07-02**

> **Jak użyć:** wklej treść tego pliku na początku nowej rozmowy w Cowork (z podpiętym folderem `AMPERE_POINT`), aby odtworzyć pełny kontekst tematu „przyrządy i pomiary" i kontynuować dyskusję.

---

## 1. Cel i kontekst
Zakład AMPERE POINT (Warszawa) sprowadza, testuje, sprzedaje i serwisuje inteligentne ładowarki AC do EV. Kompletujemy **aparaturę pomiarową**, żeby samodzielnie:
- wykonywać **obowiązkowe pomiary elektryczne stacji/ładowarek** (kontrola jakości importu, testy, serwis),
- prowadzić **diagnostykę serwisową** (spadek napięcia pod obciążeniem, hot-spoty, prąd/asymetria, dokręcanie zacisków).

Zasada doboru: **możliwie najtaniej, ale w pełni adekwatnie**. Rynek PL, dopuszczalny AliExpress. Podstawa merytoryczna: „Przewodnik w zakresie wykonywania pomiarów elektrycznych stacji ładowania" (Warszawa 2024) — plik `Przewodnik_pomiary_stacji_ladowania.pdf`.

## 2. Pięć obowiązkowych pomiarów (wg przewodnika)
Do pomiarów 1, 2, 4, 5 na stacji **konieczny jest adapter EVSE**, bo wprowadza ją w status C (stan „ładuje auto") i daje dostęp do żył L/N/PE.
1. **Ciągłość przewodów ochronnych** — prąd probierczy **≥200 mA**; mierzone przez wyjście PE adaptera; kryterium: niska rezystancja.
2. **Rezystancja izolacji** — napięcia **250/500/1000 V DC**; min. **1 MΩ**; 250 V dla obwodów z elektroniką/gniazdami; żyły czynne można zewrzeć i mierzyć względem PE (ochrona elektroniki).
3. **Rezystancja uziemienia roboczego** — metoda techniczna **3-elektrodowa (szpilkowa)**, elektrody E/S/H, ~20 m; „o ile stosowane" (dot. własnego uziomu — układ TT lub lokalny pręt).
4. **Sprawdzenie RCD** — przez adapter w statusie C; typ (AC/A/B/F), czas i prąd zadziałania, napięcie dotyku U_B.
5. **Skuteczność ochrony (impedancja pętli Zs)** — warunek **Zs·Ia ≤ Uo**; czasy wyłączenia z tabeli (TN/TT).

## 3. Co zakład JUŻ POSIADA
- **Multimetr Uni-T UT890C** — TRMS, 6000 cyfr; V/A (prąd **szeregowo do 20 A**), R, C, częstotliwość, temperatura, NCV. Rola miernika ręcznego pokryta. **Uwaga:** 20 A szeregowo → nim nie zmierzysz prądu ładowania 32 A (stąd potrzeba cęgów).
- **Adapter EVSE PEAKMETER PM701E** — generyczny; Type 1/2/NACS; symulacja stanów A/B/C/D; pre-test PE; symulacja błędów CP/PE; **wbudowany test wyzwalania upływem ≥6 mA**; IEC 61010, CAT III 600 V; współpracuje z **dowolnym** miernikiem wielofunkcyjnym (nie tylko Sonel). Źródło: peak-meter.com (seria PM701).
- **Kamera termowizyjna** (posiadana) — hot-spoty/przegrzania (istotne przy usterce typu U-001).
- **Wkrętak dynamometryczny** (posiadany) — dokręcanie zacisków momentem.

## 4. Co dokupić (rekomendacje)
Ceny orientacyjne (PL, ~czerwiec/lipiec 2026) — zweryfikuj aktualne.

- **Uni-T UT595 — miernik wielofunkcyjny (POZYCJA KLUCZOWA).** ~1800–2300 zł PL / ~$400–500 AliExpress. Robi **4 z 5** pomiarów: ciągłość (>200 mA), izolacja (250/500/1000 V), pętla Zs, RCD (typ AC/A). Dodatkowo: impedancja linii + prąd zwarcia PSC, kolejność faz, napięcie AC. **NIE robi** pomiaru rezystancji uziomu metodą 3-elektrodową; **brak** RCD typu B i testu gładkiego 6 mA DC. Linki: [Ceneo](https://www.ceneo.pl/35724086), [sklep](https://centrummiernictwa.pl/produkt/ut595-wielofunkcyjny-miernik-instalacji-uni-t/). AliExpress: item 32836823749, 1005008977596296, 1005004411620556.
- **Uni-T UT210E — cęgi AC/DC TRMS.** ~250–300 zł. Prąd obciążenia/asymetria/upływ bezinwazyjnie (bo UT890C tylko 20 A szeregowo). [sklep](https://termoplus.pl/ut210e.html) / [Ceneo](https://www.ceneo.pl/75262019).
- **Uni-T UT522 — miernik rezystancji uziemienia (metoda 3-elektrodowa).** ~730–850 zł PL / ~$170–223 AliExpress. Domyka pomiar 3, którego UT595 nie robi. **Potrzebny tylko gdy stacja ma własny uziom** (TT/pręt); w czystym TN skuteczność uziemienia ochronnego potwierdza pomiar pętli (UT595). [Allegro](https://allegro.pl/oferta/uni-t-ut522-miernik-rezystancji-uziemienia-cyfrowy-8438552070) / [Ceneo](https://www.ceneo.pl/52323575). Alternatywy: **UT521** (taniej), **Kyoritsu 4105A** ~1150–1490 zł ([sklep](https://centrummiernictwa.pl/produkt/kew4105a-miernik-rezystancji-uziemienia-kyoritsu/), pod oficjalne protokoły), Sonel serii MRU.

Razem rdzeń (UT595 + UT210E + UT522) ≈ 2800–3400 zł. Adaptera, kamery, wkrętaka i multimetru już nie kupujemy.

## 5. UT595 — jak fizycznie wykonuje pomiary (z instrukcji UT593/UT595)
- **Interfejs:** LCD (góra), pokrętło funkcji (środek), przycisk **TEST**, przyciski **F1–F4** (podświetlenie/próg, blokada pomiaru, **ZERO**/pamięć, wybór prądu RCD). **Trzy gniazda wejściowe (4 mm)** w górnej części: **RED = L**, **GREEN = E/PE**, **BLACK = N**.
- **Przewody:** 3× pojedyncze (czerwony/zielony/czarny), „special power test lead" (przewód sieciowy z wtykiem: **L→red, PE→green, N→black**), „remote-control test lead" (sonda ze zdalnym TEST).
- **Zasada:** pomiary 2-przewodowe (ciągłość, izolacja) → tylko **RED+BLACK**; pomiary pod napięciem (pętla, RCD, linia) → **3 żyły L/N/PE** przez przewód sieciowy, na stacji przez **PM701E w statusie C**.
- **Ciągłość:** pokrętło „Ω", RED+BLACK na dwa końce PE, ZERO (F3) → prąd stały >200 mA → R. Obwód beznapięciowy.
- **Izolacja:** pokrętło 250/500/1000 V, RED+BLACK między żyły (L–PE, N–PE lub zwarte L+N vs PE) → wysokie napięcie DC → prąd upływu → MΩ. Beznapięciowo.
- **Pętla Zs / linia / RCD:** 3 żyły L/N/PE; miernik pobiera znany prąd (do 20 A) i liczy Zs oraz PSC; tryb „no-trip" (≈15 mA) gdy jest RCD 30 mA; RCD: wstrzykuje prąd różnicowy L→PE, mierzy czas/prąd zadziałania.
- **Instrukcja:** [Uni-Trend](https://meters.uni-trend.com/download/ut593-595-user-manual/) · [PDF (UT593)](https://rapid-tech.com.au/wp-content/uploads/2021/02/UNI-T-UT593-User-Manual.pdf).

## 6. Pokrycie pomiarów przyrządami
| Pomiar / zadanie | Przyrząd |
|---|---|
| 1. Ciągłość PE (≥200 mA) | UT595 + PM701E |
| 2. Rezystancja izolacji | UT595 + PM701E |
| 3. Rezystancja uziomu (3-elektrodowo) | **UT522 / Kyoritsu 4105A** (UT595 tego NIE robi; tylko gdy jest własny uziom) |
| 4. RCD (typ AC/A) | UT595 + PM701E |
| 5. Pętla Zs | UT595 + PM701E |
| Spadek napięcia / ciągłość / temperatura | UT890C |
| Prąd obciążenia / asymetria (32 A) | UT210E (cęgi) |
| Hot-spoty | kamera termowizyjna |
| Dokręcanie zacisków | wkrętak dynamometryczny |
| Status C, pre-test PE, test 6 mA | PM701E |

## 7. Otwarte punkty i uwagi
- **RCD typ B / detekcja 6 mA DC (RDC-DD).** UT595 bada tylko AC/A. Praktyczny test 6 mA masz wbudowany w PM701E; pełna weryfikacja gładkiego 6 mA DC (IEC 62955) to sprzęt specjalistyczny/drogi → opierać się na **deklaracji producenta** (to wiąże się z pytaniem P6 do producenta z osobnego wątku).
- **Wzorcowanie.** Do oficjalnych protokołów potrzebne aktualne świadectwo wzorcowania miernika (i adaptera).
- **Uprawnienia/BHP.** Pomiary wykonują osoby z uprawnieniami (SEP E/D).
- **KOREKTA do wcześniejszego pliku.** `AMPERE_POINT_przyrzady_pomiarowe_v1.pdf` (starszy) błędnie zaliczał pomiar uziomu do możliwości UT595 — **to nieaktualne**. Obowiązuje niniejszy plik: UT595 uziomu 3-elektrodowego NIE mierzy.

## 8. Pliki w folderze (dot. tematu)
- `Przewodnik_pomiary_stacji_ladowania.pdf` — źródło wymagań (5 pomiarów).
- `AMPERE_POINT_przyrzady_pomiarowe_v1.pdf` — lista przyrządów z linkami/cenami (z zastrzeżeniem o uziomie z pkt 7).

## 9. Możliwe kolejne kroki
- Decyzja zakupowa: UT595 + UT210E na pewno; UT522 vs Kyoritsu 4105A (zależnie od tego, czy będziecie robić protokoły z uziomem).
- Ewentualnie cęgi upływowe (mA) do prądu upływu.
- Zaktualizować/wersjonować `AMPERE_POINT_przyrzady_pomiarowe_v1` z korektą o uziomie (v2).
