# KOMPENDIUM — prowadzenie firmy

Plik zbiorczy dla wiedzy **nietechnicznej**: podatki, cło, logistyka, formalności,
obowiązki przedsiębiorcy. Prowadzony przyrostowo, tak samo jak techniczny.

Bliźniaczy plik techniczny: `KONTEKST_kompendium_czatow.md` (złącza, komponenty,
pomiary, infrastruktura). Tam też, w sekcji 3, siedzą na razie SEP i fakturowanie/KSeF —
docelowo część podatkowa może się przenieść tutaj.

Znaczniki: **[DOK]** z dokumentacji/przepisu, **[PRZYKŁAD]** wyliczenie ilustracyjne,
**[POMIAR]** dane z naszej praktyki, **[OTWARTE]** niepotwierdzone.

---

## 1. VAT — należny i naliczony

**[DOK]** Dwa kierunki tego samego podatku. Mylenie ich to najczęstszy błąd w rozmowie o VAT.

**VAT należny** — podatek doliczony do **Twojej sprzedaży**, na fakturach, które
**wystawiasz**. Należny **urzędowi** — to Twój dług wobec fiskusa.

**VAT naliczony** — podatek zawarty w **Twoich zakupach**, na fakturach, które
**dostajesz**. Naliczony **Tobie** przez dostawcę — to Twoja wierzytelność do odliczenia.

Do urzędu płacisz **różnicę**: należny minus naliczony. Gdy naliczony przewyższa należny,
powstaje nadwyżka — do przeniesienia na kolejny okres albo do zwrotu na rachunek.

**[PRZYKŁAD]** Sprzedaż 10 000 zł netto → VAT należny 2 300 zł.
Zakupy 6 000 zł netto → VAT naliczony 1 380 zł. Do urzędu: 2 300 − 1 380 = **920 zł**.
VAT jest więc podatkiem od **wartości dodanej** — płacisz od marży, nie od obrotu.

### Odwrotne obciążenie — dlaczego to ważne przy imporcie

Przy **WNT** (wewnątrzwspólnotowe nabycie towarów) i przy imporcie usług podatek rozlicza
**nabywca**. Wykazujesz **tę samą kwotę jednocześnie jako należny i jako naliczony**
w tej samej deklaracji. Wynik netto: **zero**.

**[PRZYKŁAD]** Kontener za 200 000 zł wprowadzony przez procedurę 42: VAT należny
46 000 zł **i** naliczony 46 000 zł w tym samym JPK_V7 → do zapłaty 0 zł.
Przy zwykłej odprawie w PL te 46 000 zł trzeba **fizycznie wyłożyć** w ciągu 10 dni
od zwolnienia towaru i odzyskać dopiero w rozliczeniu okresowym.

**To jest cała oszczędność procedury 42 — nie na kwocie podatku, tylko na płynności.**

---

## 2. Odprawa celna — co to dokładnie jest

**[DOK]** **Postępowanie administracyjne**, w którym towar przekraczający granicę celną UE
zostaje objęty określoną **procedurą celną** i dopuszczony do obrotu. Nie jest to „opłata"
ani „przepustka".

1. **Zgłoszenie celne** — Ty albo agencja celna w Twoim imieniu, elektronicznie
   (w PL: AIS/IMPORT na PUESC). Papierowy **SAD** to już historia.
2. **Deklarujesz**: kod taryfy **CN/TARIC**, **wartość celną** (zwykle CIF — cena
   + ubezpieczenie + fracht do granicy UE), **kraj pochodzenia**, ilość, masę.
3. **Organ wylicza**: **cło** wg Wspólnej Taryfy Celnej, ewentualne cło antydumpingowe,
   oraz **VAT importowy** — od wartości celnej **powiększonej o cło** i transport
   do pierwszego miejsca przeznaczenia w UE.
4. **Kontrola** wg analizy ryzyka: bez kontroli, kontrola dokumentów albo **rewizja**.
5. **Zwolnienie towaru** po zapłacie lub zabezpieczeniu należności. Dopiero wtedy
   towar jest Twój do dysponowania.

**Dokumenty:** faktura handlowa, packing list, dokument transportowy (**B/L** morze,
**CMR** droga, **AWB** lotnictwo), świadectwo pochodzenia przy preferencjach celnych,
dokumenty wyrobowe (deklaracja zgodności, certyfikaty).

**Kody procedury:** **4000** — zwykłe dopuszczenie do obrotu z wprowadzeniem
do konsumpcji. **4200** — dopuszczenie do obrotu z jednoczesną dostawą
wewnątrzwspólnotową, zwolnione z VAT importowego → **to właśnie „procedura 42"**.

**Cło jest identyczne w całej UE** (Wspólna Taryfa Celna). W Hamburgu i w Gdańsku
zapłacisz co do grosza tyle samo. Różnice między portami dotyczą **wyłącznie** momentu
zapłaty VAT-u i kosztów logistyki.

---

## 3. Import z Chin przez Niemcy — procedura 42

**[DOK]** Podstawy: art. 143 ust. 1 lit. d dyrektywy 2006/112/WE, art. 33a i art. 83
ust. 1 pkt 23 ustawy o VAT.

Towar odprawiany w Niemczech, ale nie do konsumpcji tam, tylko z natychmiastowym
przemieszczeniem do Polski. Import zwolniony z VAT w DE, podatek rozliczany w PL jako WNT
— odwrotnym obciążeniem, na zero.

**Warunki:** aktywny **VAT-UE** importera (lub przedstawiciel fiskalny), numer VAT nabywcy
w zgłoszeniu celnym, **zamiar WDT już w momencie zgłoszenia**, **faktyczne
i udokumentowane przemieszczenie** towaru.

**Obowiązki w PL:** WNT w **JPK_V7**, **informacja podsumowująca VAT-UE**,
**Intrastat** po przekroczeniu progów, komplet dokumentów przewozowych (art. 42 ustawy o VAT).

**Ryzyko:** zwolnienie jest **warunkowe**. Brak jednego elementu łańcucha zawala całą
konstrukcję — niemiecki organ dolicza VAT importowy z odsetkami, polski może nałożyć
sankcję z art. 112b ustawy o VAT. **Odpowiada importer, niezależnie od liczby pośredników.**

---

## 4. Fracht, FCL i LCL

**[DOK]** **Fracht** — opłata za sam przewóz. **Nie obejmuje** THC, opłat portowych,
odprawy ani dowozu. Koszt „do drzwi" to inna wielkość — warto pilnować, o której
mówi oferta spedytora.

**FCL** (Full Container Load) — cały kontener na wyłączność (20', 40', 40'HQ).
Płacisz za kontener niezależnie od zapełnienia.

**LCL** (Less than Container Load, drobnica) — palety dzielą kontener z ładunkiem innych
firm. Rozliczenie za **CBM** albo za tonę, wg zasady **„w/m" (weight or measurement)** —
płaci się wg tego, co większe. Dochodzą opłaty **CFS** za konsolidację i dekonsolidację
po obu stronach, naliczane **od przesyłki**, nie od CBM.

**Granica opłacalności FCL vs LCL:** zwykle okolice 13–15 CBM.

### [PRZYKŁAD] Kiedy Hamburg wygrywa z Gdańskiem — sam fracht, bez VAT-u

Stawki ilustracyjne. **25 CBM, 6 000 kg, towar za 200 000 zł.**

**A — LCL Szanghaj → Gdańsk:** fracht 110 USD/CBM × 25 = 2 750 USD ≈ 2 530 EUR;
THC+CFS 25 EUR/CBM × 25 = 625 EUR; odprawa 150 EUR; dowóz do Warszawy 350 EUR.
**Razem ≈ 3 655 EUR**, tranzyt ~45 dni, **46 000 zł VAT-u wyłożone na ~30 dni**.

**B — LCL Szanghaj → Hamburg + ciężarówka:** fracht 75 USD/CBM × 25 = 1 875 USD ≈ 1 725 EUR;
THC+CFS 22 EUR/CBM × 25 = 550 EUR; odprawa fiskalna 42 = 180 EUR;
dowóz Hamburg → Warszawa 900 EUR. **Razem ≈ 3 355 EUR**, tranzyt ~35 dni, **0 zł VAT-u**.

Wynik: **~300 EUR taniej, ~10 dni szybciej, 46 000 zł niezamrożone.**

**Dlaczego:** Hamburg i Rotterdam to porty oceaniczne pierwszej linii — wielokrotnie więcej
zawinięć i opcji konsolidacji drobnicy, więc niższa stawka za CBM. Gdańsk obsługuje mniej
serwisów bezpośrednich, sporo LCL i tak idzie tam przeładunkiem.

**Punkt równowagi:** oszczędność ~32 EUR/CBM, dodatkowy dowóz drogowy ~550 EUR (w przybliżeniu
stały). **550 / 32 ≈ 17 CBM.** Poniżej — taniej prosto do Gdańska. Powyżej — wygrywa Hamburg.

**Przy FCL rachunek się odwraca:** różnica stawek oceanicznych jest procentowo mniejsza,
a dowóz 40'HQ z Hamburga kosztuje 1 200–1 500 EUR. **LCL sprzyja Hamburgowi, FCL Gdańskowi.**

---

## 5. Numery i deklaracje

### EORI

**[DOK]** **Economic Operators Registration and Identification** — numer identyfikujący
przedsiębiorcę wobec organów celnych. Nadawany **raz, przez jedno państwo członkowskie,
ważny w całej UE**. Format PL: `PL` + NIP + dopełnienie zerami.

Bez EORI **nie złożysz zgłoszenia celnego** — ani sam, ani przez agencję.
Bezpłatny, przez **PUESC**. Załatwić **zanim** towar wypłynie, nie gdy stoi w porcie
i nalicza się storage.

### JPK_V7

**[DOK]** **Jednolity Plik Kontrolny z deklaracją VAT.** Od X.2020 zastąpił osobną
deklarację VAT-7 i osobny rejestr — jeden plik XML łączy **część ewidencyjną**
(rejestr faktur) i **deklaracyjną** (rozliczenie).

**JPK_V7M** miesięczny; **JPK_V7K** — ewidencja co miesiąc, deklaracja kwartalnie.
**Termin: do 25. dnia miesiąca po okresie rozliczeniowym.**

**Od 1 lutego 2026:** nowe wzory **JPK_V7M(3)** i **JPK_V7K(3)**, dostosowane do KSeF.
Węzeł KSeF z czterema oznaczeniami: **NrKSeF** (numer faktury nadany w KSeF),
**OFF** (faktury z trybu awarii, bez numeru na dzień złożenia), **BFK** (faktury
wystawione **poza** KSeF — sprzedaż konsumencka, dokumenty sprzed KSeF),
**DI** (dowód inny niż faktura, z offline24 lub okresu niedostępności).
**Termin składania bez zmian.**

Harmonogram KSeF i stawki VAT dla montażu ładowarek: `KONTEKST_kompendium_czatow.md`, sekcja 3.2.

---

## 6. Obowiązki importera wyrobu — nasza branża

**[DOK]** Jeśli to **nasza firma jest importerem**, przejmujemy obowiązki importera
w rozumieniu unijnego prawa wyrobowego: weryfikacja zgodności (CE, LVD, EMC, RoHS),
**własna nazwa i adres na wyrobie**, przechowywanie dokumentacji technicznej i deklaracji
zgodności, odpowiedzialność wobec nadzoru rynku, rejestracja w **BDO**.

**Konsekwencja odprawy w Niemczech:** towar ogląda **niemiecki** urząd celny, wyraźnie
bardziej dociekliwy w kontroli CE i dokumentacji. Braki zatrzymają kontener w Hamburgu.
**Sprawdzać u dostawcy zanim kontener wypłynie** — zatrzymanie generuje demurrage
i storage liczone w setkach euro dziennie.

---

## 7. WĄTKI OTWARTE

- Czy przy naszym wolumenie przekraczamy progi Intrastat.
- Kto formalnie figuruje jako importer w dotychczasowych dostawach z Chin i czy mamy
  komplet deklaracji zgodności dla sprowadzanych ładowarek.
- Czy warto wystąpić o pozwolenie na art. 33a (odroczony VAT importowy w PL) jako
  alternatywę dla procedury 42 przy mniejszych przesyłkach.
- Czy mamy własną pulę EAN z GS1 Polska (patrz sekcja 8).
## 8. EAN i SKU — identyfikatory towaru

**[DOK]** Dwa numery, które łatwo pomylić, bo stoją obok siebie w każdym systemie
sprzedażowym. Różnią się właścicielem i zasięgiem.

### EAN — numer zewnętrzny, globalny

European Article Number, formalnie dziś **GTIN** (Global Trade Item Number) w systemie
**GS1**. To ten numer pod kreskami na opakowaniu. Identyfikuje **produkt**, a nie sprzedawcę
— ta sama ładowarka kupiona u trzech różnych hurtowników ma **ten sam EAN**.

Odmiany: **EAN-13** (standard detaliczny), **EAN-8** (małe opakowania),
**UPC-12** (USA), **GTIN-14** (opakowania zbiorcze, kartony, warstwy na palecie).
Ostatnia cyfra to **cyfra kontrolna** liczona z pozostałych — po niej system od razu
wykrywa literówkę.

**Nie da się go wymyślić.** Pule numerów przydziela **GS1** (w Polsce GS1 Polska),
odpłatnie, na firmę. Prefiks **590** oznacza, że numer wydała **polska organizacja GS1** —
i tu klasyczne nieporozumienie: **590 nie znaczy „wyprodukowano w Polsce"**, tylko
że firma, która zarejestrowała numer, jest zarejestrowana w Polsce. Produkt może
pochodzić skądkolwiek.

### SKU — numer wewnętrzny, twój

**Stock Keeping Unit** — własny numer katalogowy. Wymyślasz go sam, obowiązuje wyłącznie
u Ciebie, nikt go nie reguluje i nic nie kosztuje. Np. `AP-WB-11-T2-5M`.
To on spina fakturę z magazynem, z ERP i z BaseLinkerem.

**Zasada przy projektowaniu SKU:** kodować tylko cechy **trwałe** — typ, moc, wersję
złącza, długość kabla. Nigdy ceny, dostawcy ani lokalizacji magazynowej, bo to się zmienia,
a SKU ma zostać na zawsze.

### W kontekście faktur i zakupów

Ustawa o VAT **nie wymaga** ani EAN, ani SKU na fakturze — obowiązkowa jest nazwa towaru,
ilość, cena jednostkowa, wartość netto, stawka i kwota VAT. Oba numery są dodatkiem,
ale dodatkiem, który robi robotę:

- **SKU na fakturze zakupowej** pozwala zaksięgować przyjęcie (PZ) automatycznie,
  bez ręcznego dopasowywania pozycji do kartotek.
- **EAN** pozwala skanować towar przy przyjęciu i jest **wymagany przy wystawianiu ofert**
  na Allegro i Amazonie (na Amazonie da się uzyskać zwolnienie GTIN dla marki własnej).

**Nasza sytuacja:** jeśli sprowadzamy i sprzedajemy pod własną marką, potrzebujemy
**własnej puli EAN z GS1 Polska**. Numery podawane przez chińskich dostawców trzeba
zweryfikować w wyszukiwarce GS1 — w obiegu krąży sporo numerów nieprzypisanych albo
przypisanych do zupełnie innej firmy, a kolizja EAN-ów wywala oferty na marketplace'ach.

**Nie mylić z kodem celnym.** EAN nie ma nic wspólnego z odprawą — tam obowiązuje
**kod CN/TARIC**, który opisuje kategorię towaru dla taryfy celnej, a nie konkretny
egzemplarz asortymentu. Patrz sekcja 2.
