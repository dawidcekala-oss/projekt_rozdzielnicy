# KOMPENDIUM — ustalenia techniczne z sesji czatu

Plik zbiorczy, prowadzony przyrostowo. Zawiera zweryfikowane fakty, wyniki pomiarów
i gotowe procedury ustalone w rozmowach roboczych. Kazda sekcja podaje zrodlo,
zeby dalo sie odroznic dane z dokumentacji od szacunkow i od pomiarow wlasnych.

Konwencja: **[DOK]** = z dokumentacji, **[POMIAR]** = zmierzone wlasnorecznie,
**[SZAC]** = szacunek/obliczenie, **[OTWARTE]** = niepotwierdzone.

---

## 1. ZLACZA

### 1.1 Type 2 / IEC 62196-2 ("Mennekes")

**[DOK]** Zrodlo: `zlacza_dokumentacja/zlacze_type2.pdf` = ITT Cannon
"IEC 62196 Type 2 Coupler", spec. CAS21127E-CU z 05.06.2023, 19 stron.
To najlepszy dokument, jaki jest w folderze. Strona 9 = pelny pinout.

Rozklad stykow, **wtyk do ladowarki (Equipment Plug)**, widok na czolo:

```
      PP            CP
   L1      PE       N
      L2         L3
```

**Wtyk do auta (Vehicle Connector)** — lustrzany:

```
      CP            PP
   N       PE       L1
      L3         L2
```

Kolory zyl: L1 brazowy, L2 czarny, L3 szary, N niebieski, PE zolto-zielony,
CS/CC/PP czerwony, CP bialy.

Kodowanie pradu rezystorem Rc (miedzy PP a PE):
20 A = 680 om / 0,5 W; 32 A = 220 om / 1,0 W; 63 A = 100 om / 1,0 W.

Przekroje kabla: 20 A = 2,5 mm2; 32 A = 6,0 mm2; 63 A = 16,0 mm2; sygnalowe 0,5 mm2.
Srednica kabla: 20 A 1-faz 9,8 mm / 3-faz 12,4 mm; 32 A 12,2 / 15,8 mm; 63 A 22,5 mm.
Certyfikacja kabla EN 50620:2020.

Strona 10 tego samego dokumentu = schemat polaczenia ladowania wg IEC 61851-1 z Rc i Ra.

Limity cieplne zlacza wg IEC 62196-1 (strona 13): maksymalny przyrost 50 K,
zacisk krympowany 90 C, plaszcz kabla 60 C, dotykalne czesci niemetalowe 85 C,
prady proby 22 / 42 / 63 A dla wersji 20 / 32 / 63 A.

Temperatura pracy zlacza: -30...+40 C wg IEC 62196-2:2022, -30...+50 C wg starszej
DIN EN 62196-1:2015, przy czym w zakresie +40...+50 C moze byc wymagana redukcja pradu.
IP: IP44 z zaslepka lub w polaczeniu, IP24 bez zaslepki.

**[DOK]** MENNEKES **nie publikuje** pinoutu Type 2. Sprawdzone: katalog eMobility,
techniczne karty produktow (media.mennekes.org), instrukcja Mode 2 IC-CPD,
strona z dokumentami dla instalatorow, wallbox.mennekes.de. Jedyny ich material
z opisanymi stykami to podrecznik "Elektromobilitaet — Das Ein-mal-Eins", s. 128-129
(etykiety: proximity / earth / control pilot / neutral / L1 L2 L3) oraz s. 151
(wyjasnienie rezystora PP). Ich "Technischer Leitfaden Ladeinfrastruktur" (200+ stron)
jest za formularzem kontaktowym — niesprawdzony, najbardziej obiecujacy kandydat.
Powod: Mennekes sprzedaje dzis gotowe kable i wallboxy, nie komponenty zlaczowe.
Dokumentacje komponentowa publikuja ITT Cannon, HARTING, Phoenix Contact, TE.

Drugie zrodlo w folderze: `zlacza_dokumentacja/Type2.pdf` = karta HARTING,
strona 4 = pinout wtyku do auta.
Zrodlo zewnetrzne z pinoutem: karty kabli Phoenix Contact, np. 1627692.

### 1.2 CEE / IEC 60309 (zlacze silowe)

**[DOK]** IEC 60309-2 pkt 7.1: tuleje stykowe gniazda ulozone **zgodnie z ruchem
wskazowek zegara patrzac od frontu**, piny wtyczki w kolejnosci odwrotnej.
Kolejnosc od PE zgodnie z zegarem: L1, L2, L3, N.

Punkt odniesienia to zawsze **PE** — styk grubszy, w miejscu wpustu.
Czerwone 400 V 5-pin: PE na godzinie 6 (na dole, w linii wpustu).

**Gniazdo** (patrzac w otwor): PE na dole, L1 z lewej, L2 lewa-gora,
L3 prawa-gora, **N z prawej tuz obok PE**.
**Wtyczka** (patrzac na piny): lustrzanie — **N z lewej**, L1 z prawej.

Godziny sa przyblizone (styki rozlozone mniej wiecej co 72 st.); norma koduje
zegarowo tylko pozycje PE, reszte definiuje jako kolejnosc.

Praktyka: **nie podlaczac "na oko"** — kazda wtyczka i gniazdo ma zaciski wybite
na korpusie (1/2/3 albo L1/L2/L3, N czasem jako "4", symbol uziemienia przy PE),
wymaga tego pkt 7.5 normy. Lustrzane odbicie wtyk/gniazdo to najczestsza przyczyna bledow.

Kolory: 200-250 V niebieski, 380-480 V 3-faz czerwony, 100-130 V zolty.
Wirowanie: L1-L2-L3 zgodnie z zegarem = prawe. Do zmiany sa wtyczki z przemiennikiem faz.
Stare polskie instalacje: 4-pin moze byc 3P+PE (bez N — nie wyciagniesz 230 V) albo 3P+PEN.

### 1.3 Oznaczenia kabli

**[DOK]** W oznaczeniach zharmonizowanych (HD 361 / EN 50525) litera miedzy liczba zyl
a przekrojem to znak mnozenia niosacy informacje:
**G = wersja z zyla ochronna zolto-zielona**, **X = wersja bez niej**.

`5G6` = 5 zyl po 6 mm2, w tym PE. Czyli L1, L2, L3, N, PE — cztery zyly do dyspozycji.
`5X6` = 5 zyl po 6 mm2, zadna nie jest ochronna.

Odpowiedniki: niemieckie NYM-**J** (mit Schutzleiter) vs NYM-**O** (ohne).
Polskie nazewnictwo kablowe: dopisek **zo**, stad "YKY(zo) 5x6" w naszych dokumentach.

`5G6` to standard dla **32 A trojfazowo** = wallbox 22 kW albo gniazdo CEE 32 A 5-stykowe.
Uwaga: samo "5G6" nie mowi nic o typie izolacji. H07RN-F 5G6 to przewod gietki gumowy,
**nie do trwalego ukladania w ziemi** — tam YKY/YKXS. Typ trzeba zawsze podac razem.

**[SZAC]** Spadek napiecia, 32 A / 400 V / 6 mm2 Cu: ok. 0,16 V na metr,
czyli ~4 V na 25 m = ~1,0 %. Zgadza sie z tabela w `Stojak/..._research_rynkowy_v1.html`.

---

## 2. KOMPONENTY

### 2.1 Przekaznik FANHAR FH35L-40-2AT-L2 DC12V

**[DOK]** Karta producenta FH35L-40-EN (fanhar-relay.com).
Kod zamowieniowy: 2A = 2 zestyki zwierne, T = material AgSnO2, L2 = wersja dwucewkowa
zatrzaskowa, DC12V = napiecie cewki.

Zestyki 40 A 250 VAC, max napiecie laczeniowe 380 VAC, max moc laczeniowa 10000 VA,
rezystancja zestyku <=20 mOm (mierzone 6 VDC / 1 A), material AgSnO2,
min. obciazenie 5 VDC 100 mA. Wytrzymuje udar zwarciowy 1020 A / 10 ms.
Cewka DC12V: 125 mA, 96 om, ok. 1,5 W, napiecie set/reset <=9,00 VDC, czas <=15 ms,
impuls musi byc >=5x czasu przelaczenia.
Izolacja: 1000 MOm (500 VDC), wytrzymalosc miedzy zestykami 2000 VAC / 1 min.
Trwalosc: mechaniczna 3x10^5, **elektryczna tylko 6x10^3** przy 40 A 250 VAC (1s/9s).
Otoczenie -40...+85 C, wilgotnosc 5-85 %. Uklad izolacyjny UL klasy F (155 C).
Wymiary 30,0 x 20,0 x 10,0 mm, masa ok. 12 g.

**[OTWARTE] Karta NIE podaje przyrostu temperatury ani krzywej derating ani
obciazalnosci ciaglej.** Sprawdzone — nie ma takiego wiersza w dokumencie.

**[SZAC]** Grzanie zalezy od **pradu, nie od napiecia** — 230 V nie ma z tym nic wspolnego
poza lukiem przy przelaczaniu. Cewka odpada z bilansu (zatrzask, tylko impuls),
w przeciwienstwie do 2x HF165F-50 z ~1,2 W kazdy w sposob ciagly.
Katalogowe <=20 mOm to granica odbiorcza, nie wartosc robocza — przy 32 A dalaby 20 W
na biegun, czyli fizyczna niemozliwosc. Realna rezystancja nowego zestyku z zaciskami
to 1-3 mOm, czyli 1-3 W na biegun. Typowy przyrost dla tej klasy: 40-70 K nad otoczeniem.
W obudowie ladowarki przy 40-50 C powietrza daje to korpus **80-110 C**.

Co peknie pierwsze: **laminat i luty**, nie przekaznik. FR4 ma Tg ok. 130-140 C,
pola lutownicze powinny siedziec ponizej ~105-110 C. Klasa F 155 C jest dopiero za tym.

Ryzyko wlasciwe: **ucieczka termiczna** — rosnaca rezystancja zestyku -> wiecej watow ->
wyzsza temperatura -> szybsze utlenianie. Tak umieraja przekazniki w wallboxach.
Trwalosc 6x10^3 cykli jest akceptowalna tylko dlatego, ze w poprawnym EVSE przekaznik
rozlacza praktycznie bezpradowo (auto zjezdza z pradem po CP przed otwarciem stycznika).

**Uwaga projektowa nieujeta w dokumencie porownawczym:** konsolidacja dwoch osobnych
przekaznikow w jeden 2-biegunowy wsadza straty obu biegunow (L i N, ten sam prad)
do jednej brylki 30x20x10 mm. Przy tej samej rezystancji styku temperatura *korpusu*
bedzie wyzsza niz wczesniej, mimo ze sumaryczne cieplo w obudowie spadlo o ~2,4 W z cewek.

**Diagnostyka:** najlepszy pojedynczy pomiar to spadek napiecia na zwartym zestyku przy
pradzie roboczym. Przy 32 A 100 mV = 3,1 mOm = 3,2 W. **Trendowanie tej wartosci w czasie
jest wczesnym ostrzezeniem przed ucieczka termiczna** — dobra funkcja dla custom device.
Do temperatury: termopara typu K na zacisku i na polu lutowniczym, 32 A przez 1,5-2 h
do stanu ustalonego, obudowa zamknieta. Termowizja tylko do znalezienia hot spotu —
emisyjnosc cynowanych zaciskow rozjezdza odczyt bezwzgledny.

**Do pytan do producenta:** raport z proby nagrzewania przy 32 A i 40 A ciagle wraz
z temperatura otoczenia proby; krzywa derating / obciazalnosc ciagla w funkcji temperatury;
wymagana powierzchnia miedzi i szerokosc sciezek pod zaciski.

### 2.2 Przekladnik ZMCT356E

**[DOK]** Producent: Qingxian Zeming Langxi Electronic Devices. Typ bazowy ZMCT356.
Przekladnia **2000:1**. 2,5 mA przy 5 A. Zakres liniowy 0-50 A przy rezystorze 10 om.
Blad przekladni +/-0,5 %, blad katowy <=20', liniowosc 0,2 % — wszystko przy 10 om.
Napiecie izolacji 3000 V (napiecie **proby**, nie kwalifikacja do izolacji podstawowej
w instalacji 400 V kat. III — to tani element do pracy WEWNATRZ obudowy).
Praca -40...+85 C. 2000 zwojow drutem 2UEW Ø0,08. Rdzen Ø14*19*5. Zalewany epoksydem.
Wersja z wyprowadzeniami na przewodach (flying leads) + wtyk JST.

**[POMIAR] 2026-08 — przekladnia potwierdzona doswiadczalnie: 2000:1.**
Metoda: czajnik ~8,5 A przez symulator EV podpiety do ladowarki B35, faza przewleczona
przez rdzen, amperomierz **AC** na wyjsciu przekladnika. Przy ~8 A odczyt 4 mA.
8 / 0,004 = 2000. Wersja 1000:1 dalaby 8 mA — wykluczona.
**Sufiks "E" nie zmienia przekladni.**

Pulapka, ktora nas kosztowala jedno podejscie: pierwszy pomiar dal 56-77 **mikroamper**,
bladzacych. Przyczyna — **miernik na zakresie pradu STALEGO**. Przebieg przemienny na
zakresie DC usrednia sie do zera i dryfuje. Stabilny prad pierwotny daje **stabilny** odczyt;
bladzaca liczba = brak sygnalu, a nie maly sygnal.

Tabela odniesienia przy 2000:1:

| Prad pierwotny | Wtorny | Na 10 om |
|---|---|---|
| 6 A | 3 mA | 30 mV |
| 8 A | 4 mA | 40 mV |
| 16 A | 8 mA | 80 mV |
| 32 A | 16 mA | 160 mV |
| 50 A | 25 mA | 250 mV |

**Zasady pomiaru przekladnika (wypracowane):**
- Amperomierz na zaciskach CT jest **poprawny** (obciazenie ~0 = idealny warunek pracy CT).
  Przekladnik ma pracowac w zwarciu, NIGDY w rozwarciu.
- Ale lepiej: **wpiac na stale 10 om i mierzyc napiecie w mV AC**. Zalety: wtorny nigdy nie
  jest rozwarty, warunki zgodne z karta katalogowa, zakres mV AC ma kazdy miernik
  (mikroamperow AC — nie kazdy), i mozna przepinac miernik przy pracujacym ukladzie.
  Przepalony bezpiecznik w torze mA = rozwarty wtorny = wysokie napiecie szpilkowe.
- **Przewlekanie N razy mnozy prad efektywny** — 5 zwojow x 8,5 A = 42,5 A. Podnosi
  rozdzielczosc i daje darmowy test liniowosci (wskazania musza byc proporcjonalne
  1:2:3:5), bez ruszania obciazenia. Najczystszy eksperyment.
- Przez otwor idzie **wylacznie faza**. L razem z N = suma zero = odczyt zero.
- To przekladnik **przelotowy**, nie ceegi — trzeba rozlaczyc obwod i przewlec przewod.
- **Nastawa pradu w EVSE nie ogranicza glupiego obciazenia.** Limit CP to informacja do
  samochodu, a nie regulator. Czajnik pobiera swoje. Brac **wskazanie** licznika, nie nastawe.
- Licznik ladowarki ma klase ~1-2 % — wystarczy do ustalenia przekladni (roznica 2x),
  nie wystarczy do kalibracji elementu o bledzie +/-0,5 %.

**[SZAC] Dobor rezystora obciazenia** dla ukladu pomiarowego, zasilanie 3,3 V,
punkt pracy 1,65 V, swing +/-1,5 V szczytowo:
- zakres do 32 A: 16 mA sk. -> 22,6 mA szcz. -> **ok. 68 om**, wyjscie 1,09 V sk. przy 32 A
- pelny zakres 50 A: 25 mA sk. -> 35,4 mA szcz. -> **ok. 43 om**
Moc do pominiecia (rzedu mW). Rezystor 1 % dla stabilnosci przekladni.

---

## 3. FORMALNOSCI

### 3.1 Uprawnienia SEP

**[DOK]** Rozporzadzenie Ministra Klimatu i Srodowiska z 1 lipca 2022,
**Dz.U. 2022 poz. 1392**, Zalacznik nr 1, **Grupa 1** (urzadzenia, instalacje i sieci
elektroenergetyczne), 13 punktow zakresu.
**Pkt 12** = "urzadzenia umozliwiajace magazynowanie energii elektrycznej i jej
wprowadzanie do sieci elektroenergetycznej o mocy wyzszej niz 10 kW" — czyli magazyny
energii (BESS) powyzej 10 kW.
Rodzaje: **E** (eksploatacja) i **D** (dozor). Swiadectwa wazne 5 lat.

**[OTWARTE]** Rozporzadzenie **nie definiuje**, czy prog 10 kW dotyczy mocy zainstalowanej,
mocy falownika, czy mocy przylaczeniowej. To realna luka interpretacyjna.

### 3.2 Fakturowanie i KSeF

**[DOK]** Termin wystawienia faktury: do 15. dnia miesiaca nastepujacego po dostawie/usludze.
Paragon z NIP do 450 zl = faktura uproszczona.
**KSeF**: 1 lutego 2026 — podatnicy o sprzedazy >200 mln zl za 2024 oraz obowiazek
*odbierania* dla wszystkich; 1 kwietnia 2026 — pozostali; 1 stycznia 2027 — najmniejsi.
Odroczenie dla sprzedazy <=10 000 zl miesiecznie do konca 2026. **B2C poza KSeF.**

**Stawki VAT dla montazu ladowarek:** domyslnie **23 %**. Stawka **8 %** tylko dla czesci
mieszkalnej w ramach spolecznego programu mieszkaniowego (dom <=300 m2, lokal <=150 m2).
**Garaz — przylegly, wolnostojacy czy podziemny — jest niemieszkalny, czyli 23 %.**

**Split payment (MPP):** obowiazkowy dopisek na fakturach >=15 000 zl brutto obejmujacych
roboty elektryczne/instalacyjne (zalacznik 15 do ustawy o VAT).

---

## 4. INFRASTRUKTURA BIUROWA

### 4.1 Drukarka etykiet Qoltec 50243 (LTP-0243) @ 192.168.0.87

**[DOK]** Etykieciarka kurierska, 203 dpi, szerokosc druku 104 mm (max nosnik 108 mm),
szerokosc papieru/etykiety 26,7-120 mm, dlugosc etykiety 20-300 mm, grubosc 0,06-0,2 mm,
max srednica rolki 120 mm, rdzen 26,7 mm, predkosc do 127 mm/s, USB / RS-232 / Ethernet.
Producent nie publikuje ani jezyka polecen (TSPL/ESC-POS/ZPL), ani procedury kalibracji.

**Konfiguracja dzialajaca (przeniesiona z komputera zrodlowego):**
sterownik **Rongta RP4xx Series** (provider NiceLabel, v3 z 2016, `rongta.inf_amd64_9f646a54d8efbcb1`),
port **IP_192.168.0.87**, protokol **RAW 9100**, **SNMP wylaczone**, nazwa kolejki `Qoltec 50243 LAN`.

Instalacja od zera, PowerShell jako administrator:

```powershell
$inf = "<sciezka>\drivers\rongta.inf_amd64_9f646a54d8efbcb1\RONGTA.inf"
pnputil /add-driver "$inf" /install
Add-PrinterDriver -Name "Rongta RP4xx Series"
Add-PrinterPort  -Name "IP_192.168.0.87" -PrinterHostAddress "192.168.0.87" -PortNumber 9100
Add-Printer      -Name "Qoltec 50243 LAN" -DriverName "Rongta RP4xx Series" -PortName "IP_192.168.0.87"
```

**Pulapki (wszystkie napotkane realnie):**
- `Add-PrinterPort` **nie ma** parametru `-SNMPEnabled`. Sa `-SNMP` (UInt32, WLACZA SNMP
  i ustawia indeks) oraz `-SNMPCommunity`. Zeby SNMP bylo wylaczone — **nie podawac zadnego**.
- Sterownik ma w INF `NoTestPage=1`, wiec **przycisk "Drukuj strone testowa" jest wylaczony**.
  Test surowym strumieniem: TcpClient na 192.168.0.87:9100 + bajty ASCII.
  Test przez sterownik: `"tekst" | Out-Printer -Name "Qoltec 50243 LAN"`.
- **Rozmiar strony jest glownym zrodlem problemow.** `Add-Printer` zaklada kolejke
  z fabrycznym stockiem sterownika = **12,00 x 33,20 cm** (uwaga: CENTYMETRY), czyli
  120 x 332 mm — maksymalny nosnik, a nie etykieta. Edge wysrodkowuje wtedy etykiete A6
  na stronie 332 mm, przez co na naklejce ladunek trafia od ~92 mm, czyli widac tylko
  gorny fragment obrazu w dolnej czesci naklejki.
  Poprawka: `Preferencje drukowania` -> sekcja Rozmiar -> **Wysokosc 33,20 -> 15,00 cm**.
  Szerokosc zostawic 12,00 (marginesy 0,80 z kazdej strony daja dokladnie 104 mm druku).
  Otwarcie okna: `rundll32 printui.dll,PrintUIEntry /e /n "Qoltec 50243 LAN"`.
  Po zmianie **zamknac i otworzyc Edge** — trzyma ustawienia drukarki w pamieci.
- `Set-PrintConfiguration -PaperSize A6` dziala (A6 = 105x148 mm), ale **bije sie**
  z wlasnym stockiem sterownika. Jedno zrodlo prawdy — ustawiac w oknie sterownika.
- Reset kolejki bez reinstalacji sterownika i portu:
  `Remove-Printer` + `Add-Printer` z tymi samymi parametrami.

**Bledy w paczce instalacyjnej od Michala** (do zgloszenia, zeby nastepna osoba nie utknela):
domyslny `-DriverName` w `install-printer.ps1` to `Rongta RP5xx Series`, podczas gdy
dzialajaca konfiguracja to **RP4xx** (przyznaje to sam README w ostatnim akapicie);
lista fallback nie pomoze, bo odpala sie tylko gdy preferowany sterownik **nie da sie
zainstalowac**, a RP5xx instaluje sie bez problemu. Drugi blad: `-SNMPEnabled $false`
w linii 69, przy `$ErrorActionPreference = "Stop"` na gorze — skrypt wywala sie w tym miejscu.
Paczka nigdy nie zostala przepuszczona od poczatku do konca.

**Diagnoza pierwotnego problemu:** kolejka na laptopie admina byla **Shared: True**
(`CURRENT_SYSTEM_INFO.txt`), czyli cale biuro drukowalo przez jego maszyne i wydruki
czekaly, az wroci do biura. Lokalna instalacja z portem TCP/IP to usuwa.

**Do poproszenia admina:** rezerwacja DHCP dla 192.168.0.87 — adres jest wpisany na sztywno
w port, wiec zmiana adresu po cichu polozy kolejki wszystkim.

### 4.2 BaseLinker + etykiety InPost

Etykiety InPost pobierane z BaseLinker sa **A6: 297 x 421 pt = 104,8 x 148,5 mm**,
tresc wypelnia cala strone. **Nie wymagaja przycinania** — sa gotowe do druku 1:1.

**Automatyczny wydruk:** aplikacja **BaseLinker Printer** (darmowa, Windows/macOS/Linux).
Panel -> Ustawienia -> Drukowanie -> BaseLinker Printer -> pobrac, zainstalowac
**na wlasnym komputerze**, uruchomic (zasobnik), "Set in App", wybrac `Qoltec 50243 LAN`, zapisac.
Aplikacja **musi byc uruchomiona na komputerze, do ktorego podlaczona jest drukarka** —
to wlasnie powod, dla ktorego zlecenia ladowaly w kolejce na serwerze admina.
Autoprint: BaseLinker -> Automatyzacja -> akcja **Drukuj etykiete**, np. po zmianie statusu.

Kolejnosc wdrozenia ma znaczenie: **najpierw rozmiar strony w sterowniku, potem agent** —
BaseLinker Printer wysyla PDF do tej samej kolejki Windows.

---

## 5. WATKI OTWARTE

- Sufiks "E" w ZMCT356E — przekladnia potwierdzona jako 2000:1, ale znaczenie litery nieustalone.
- FANHAR FH35L-40 — brak przyrostu temperatury i obciazalnosci ciaglej w karcie; do fabryki.
- SEP pkt 12 — brak definicji, czy 10 kW to moc zainstalowana, falownika czy przylaczeniowa.
- MENNEKES "Technischer Leitfaden Ladeinfrastruktur" — 200+ stron za formularzem, niesprawdzony.
- Drukarka: skad wczesniej szly zlecenia, skoro na stacji nie bylo zadnej kolejki Rongty
  ani polaczenia do udzialu admina — do sprawdzenia po wdrozeniu BaseLinker Printer.

---

## 2.3 Modul RCMU RICHSENS RCPDA20S03-L300

**[DOK]** Hubei RICHSENS (richsensor.com), seria RCPDA20S03-4P6.
**To NIE jest RCD** — to modul pomiarowy RCMU / czujnik RDC-DD. Nic nie rozlacza,
wystawia sygnal trip do sterownika; rozlaczeniem zajmuje sie stycznik.
Zasada **fluxgate**, pomiar izolowany, zasilanie pojedyncze **5 V**.
Progi **6 mA DC** i **30 mA AC**, rozdzielczosc 0,2 mA, wyjscie przelaczajace (trip),
autotest z autokalibracja, norma **IEC 62752**. Sufiks `-L300` = przewody 300 mm.

**[POMIAR] Wyprowadzenia — odczytane z sita plytki, nie z karty.** Plytka X2Q322_K_V4,
zlacze 4-pin opisane **`漏保`**. Kolejnosc fizyczna na wtyku:

| Pin | Kolor | Opis |
|---|---|---|
| 1 | zolty | **S_OUT** — wyjscie sygnalu zadzialania |
| 2 | czarny | **GND** |
| 3 | czerwony | **5V** |
| 4 | bialy | **T_IN** — wejscie autotestu |

**[OTWARTE]** Polaryzacja T_IN nieustalona — nie sterowac przed otrzymaniem karty.
Producent nie publikuje czasow zadzialania. Kontakt: sales@richsensor.com.

### Stanowisko pomiarowe (schemat `RCPDA20S03_stanowisko_pomiarowe.svg`)

Zasada: czujnik mierzy sume wektorowa pradow w otworze, wiec pojedynczy przewod niosacy
6 mA wyglada dla niego jak 6 mA uplywu. **Caly test w SELV, bez 230 V i bez zwarcia do PE.**

Galaz DC: bateria 9 V + R1 680 om + P1 5 kom 10-obrotowy → 1,6–13 mA.
Galaz AC: trafo 12 V AC + R2 270 om/1 W + P2 470 om/2 W drutowy → 9–44 mA.
SW1 wybor zrodla, SW3 zmiana polaryzacji DC, miernik 1 szeregowo w petli.
Przewod przechodzi **raz przez otwor**, powrot petli **poza otworem**.
Odczyt: R3 10 kom podciagajace S_OUT do +5 V (dziala i dla push-pull, i dla otwartego drenu),
LED z R4 2k2, miernik 2 jako woltomierz DC. Zasilanie 5 V z powerbanku, C1 100u + C2 100n.

**Warunek poprawnosci:** petla wstrzykujaca **galwanicznie oddzielona** od zasilania 5 V.
Wspolna masa = czesc pradu wraca sciezka zasilania, poza otworem, i wynik jest fikcja.

**Kolejnosc:** potencjometr na maks. rezystancji → zalaczyc 5 V → **odczekac 10 s na
autokalibracje, ktora musi sie odbyc bez pradu w otworze** → zanotowac stan spoczynkowy →
powoli narastac → notowac prog → zdjac 5 V (kasowanie zatrzasku) → powtorzyc dla
**odwrotnej polaryzacji DC** → przelaczyc na AC.
Slaba powtarzalnosc: przewlec N razy, prad zastepczy = N·I.

**Ograniczenie:** sprawdzenie **funkcjonalne, nie badanie zgodnosci**.
**Nie robic:** testu rezystorem miedzy faza a PE w dzialajacej instalacji.

## 4.3 Plytka sterownika X2Q322_K_V4

**[POMIAR]** Ze zdjec: MCU **X2Q322** LQFP64 (znakowanie wlasne), modul radiowy **Tuya WBR3**
(P/N 3500000301-10), zasilacz **ATAZ AD10-B12** (100–277 VAC 0,23 A → 12 V / 830 mA, ta 55 C).
Zlacza: 20-pin glowne (CP, K1–K4, 6 V, ICP, NTC, IN_PE), trzy 2-pinowe
**`L1/L2/L3 电流`** (tu ida przekladniki ZMCT356E), 4-pinowe **`漏保`** (modul RCMU),
FPC **`LCD`**, oraz naglowki **`J3 烧录`** (GND/DIO/CLK/3.3V) i UART (GND/TX1/RX1/5V).

**Wniosek praktyczny: sito tej plytki jest kompletnym opisem wyprowadzen dla podzespolow,
ktorych producenci nie dokumentuja. Przy nieznanym module — najpierw czytac plytke.**

---

## 6. SYGNAL CP — WARTOSCI ODNIESIENIA I POMIARY

**[DOK]** Zrodlo: `KONTEKST/iec-61851-1_compress.pdf` — uwaga, to **wydanie IEC 61851-1:2010**,
nie 2017. Wartosci CP w Zalaczniku A sa w obu wydaniach zasadniczo te same.

**Tabela A.1 — parametry generatora CP w EVSE:**
napiecie dodatnie Voch **12,00 V ±0,6**; ujemne Vocl **−12,00 V ±0,6**;
czestotliwosc Fo **1000 Hz ±0,5 %** (995–1005 Hz);
szerokosc impulsu **±25 us** (przy okresie 1000 us = **±2,5 pkt proc. wypelnienia**);
**maks. czas narastania i opadania (10–90 %) = 2 us**; min. czas ustalania do 95 % = 3 us;
rezystancja zastepcza zrodla R1 **1000 om ±3 %**; Cs zalecane 300 pF; Cs+Cc maks. 3100 pF.

**Tabela A.3 — stany i napiecia, tolerancja ±1 V** (mierzone po ustabilizowaniu):
A = **12 V** staly, brak pojazdu · B = **9 V**, pojazd podlaczony, nie gotowy ·
C = **6 V**, gotowy, ladowanie, bez wentylacji (R3 = 1,3 kom) ·
D = **3 V**, wymagana wentylacja (R3 = 270 om) · E = 0 V · F = −12 V, EVSE niedostepne.
Rezystory po stronie pojazdu: R2 = 2,74 kom ±3 %, spadek na diodzie 0,7 V ±0,15.
**Polowka ujemna −12 V jest dowodem obecnosci diody** w pojezdzie — jej brak to usterka.

**Tabele A.5 / A.6 — wypelnienie a prad:** dla 6–51 A: **% wypelnienia = prad[A] / 0,6**,
zakres 10–85 %. Interpretacja przez pojazd: prad = % wypelnienia × 0,6 A.
Dla 51–80 A: % = prad/2,5 + 64. Ponizej 3 % — brak ladowania; 3–7 % — komunikacja cyfrowa;
8–10 % — 6 A; powyzej 97 % — brak ladowania.

### [POMIAR] Ladowarka Q11 — zmierzone oscyloskopem

Trzy przebiegi, sonda X1, 10 V/dz, 200 us/dz, sprzezenie DC:

| Stan | Vmax | Vmin | f | Wypelnienie | Ocena |
|---|---|---|---|---|---|
| A (bez pojazdu) | 12,60 | 11,70 (Vave 12,20) | — | — | OK, mieści sie nawet w wezszym ±0,6 |
| B (podlaczony) | 9,50 | −12,30 | 0,999 kHz | 26,4 % | OK |
| C (ladowanie) | 6,40 | −12,40 | 0,999 kHz | 27,2 % | OK |

Wypelnienie 26,4 % → 15,84 A; 27,2 % → 16,32 A. Nominal dla 16 A = **26,67 %**.
Odchylki 0,3–0,5 pkt proc. przy dopuszczalnych **±2,5 pkt proc.** (czyli ±1,5 A). Bardzo dobrze.
**Zgadza sie z Q11 = 11 kW = 16 A trojfazowo.**

**Czego ten pomiar NIE zweryfikowal:**
1. **Czasy narastania i opadania** (limit 2 us) — przy 200 us/dz zbocze to jeden piksel.
   Trzeba zejsc na ~1 us/dz z wyzwalaniem zboczem. To jest realna luka, bo wolne zbocza
   to klasyczna przyczyna, ze auto zle odczytuje wypelnienie albo odmawia startu.
2. **Vmax to zly parametr na plateau** — tani DSO lapie przestrzelenie na zboczu.
   Norma mowi „po ustabilizowaniu", wiec czytac plateau **kursorami**, nie auto-Vmax.
3. **Rozdzielczosc pionowa** — przy 10 V/dz przebieg 24 V zajmuje ~2,4 dzialki z osmiu.
   Lepiej 5 V/dz z przesunieciem pionowym.

Vave i Vrms nie sa parametrami normy. Sluza za kontrole spojnosci:
Vave = D·V+ + (1−D)·V−. Dla stanu C: 0,272·6,40 + 0,728·(−12,40) = **−7,28 V**
wobec zmierzonych −7,60 V — zgadza sie w granicach odczytu.
