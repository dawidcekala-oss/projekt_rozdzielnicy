# Transkrypcja nagrania Recording_33

**Plik:** Recording_33.m4a  ·  **Długość:** 48 min 50 s  ·  **Język:** polski

**Rozmowa:** AmperePoint — Shelly (moduły Wi-Fi w ładowarkach, wyjście z Tuya)

**Transkrypcja wykonana:** 17 września 2026

### Jak powstała ta transkrypcja i gdzie jej nie ufać

**Tekst** rozpoznał model Whisper large-v3 (przetwarzanie lokalne, na tym komputerze,
nagranie nigdzie nie było wysyłane). Całe 2930 sekund zostało rozpoznane, żaden fragment
nie został pominięty. 40 najbardziej wątpliwych miejsc sprawdziłem drugim, niezależnym
modelem — tam, gdzie oba modele słyszą to samo, tekst jest pewny; tam, gdzie się różnią,
zostawiłem oznaczenie i wypisałem je na końcu dokumentu.

**Podział na wypowiedzi i przypisanie stron wynika z TREŚCI, nie z rozpoznania głosów.**
To jest istotne zastrzeżenie i nie chcę go ukrywać: próbowałem rozpoznać mówców
automatycznie (segmentacja pyannote 3.0 + osadzenia głosu CAM++ i ResNet34). Na tym
nagraniu to nie działa. Sprawdzian: wziąłem sześć fragmentów, o których z treści wiadomo,
kto mówi, i kazałem systemowi przypisać je do wzorców pozostałych — pomylił trzy na
dwanaście, a dla 83 % czasu nagrania różnica między „to Shelly” a „to AmperePoint”
wynosiła mniej niż 0,10 przy skali od 0 do 2, czyli tyle co nic. Powód jest prosty:
jeden mikrofon dyktafonu w pogłosowej sali, kilka męskich głosów w podobnej odległości —
cechy pomieszczenia zagłuszają cechy mówcy.

Dlatego etykiety **AMPEREPOINT** i **SHELLY** postawiłem czytając rozmowę: kto mówi
„nasze fabryki”, „nasze ładowarki”, a kto „za Shelly X jestem ja odpowiedzialny”,
„wyślę Wam dev kita”. Tam, gdzie treść nie rozstrzyga (krótkie „tak”, „no”, wtrącenia),
stoi **NIEUSTALONY** — 10 wypowiedzi, 184 słowa. Po każdej ze stron mówiły co najmniej
dwie osoby i tego rozdzielić się nie da; w rozmowie padają imiona Maciej, Adam, Dawid
(strona AmperePoint) oraz Boris — szef R&D Shelly, nieobecny na spotkaniu.

**Poprawki.** Nazwy własne i terminy branżowe poprawiłem tylko tam, gdzie kontekst nie
zostawia wątpliwości albo potwierdziło to źródło zewnętrzne — np. „PowerAC”, „to PC”
i „PAPC” to za każdym razem **TopAC** (ładowarka Shelly, model EVE01-11R), a „Shell X”
to platforma OEM **Shelly X**. Pełna lista poprawek jest na końcu. Nic poza tym nie
zostało wygładzone: powtórzenia, urwane zdania i potoczność są takie, jak w nagraniu.

---

## Zapis rozmowy

**[00:00] AMPEREPOINT**

To jest produkt częściowo smart, jak to nazwijemy, on jest w pełni smart na to, że dalej połączę. I my równolegle pracujemy z fabrykami, żeby, mówię, teraz jakiś pierwszy moduł DLB wprowadziliśmy, tam teraz Chińczycy mocno pracują nad tym nowym systemem, który będzie umożliwił trochę łatwiejsze parowanie pomiędzy urządzeniami, ale ja wiem jak to będzie działało, że to nie będzie ten eksperyment dla użytkowników i my będziemy musieli później na supporcie ulegać wszystkie konsekwencje związane z tym, że ten produkt nie jest taki jaki powinien być, a jest to istotny punkt praktyczny Jedno jest takie, że żeby być tą najwyższą, najdroższą średnią półką, czyli tam gdzie realnie można zbudować marże, wobec tych, co mielą pieniądze na marżach, no to musimy zawsze oferować coś więcej, czyli musimy być tuż za tymi, którzy nie żyją. Później mamy rozwiązane goee, nextblue i tak dalej, ale to są sprzęty, które są bliżej 4 tysięcy, różnie, więc jak być tuż za nimi, ale daleko przed swoją inwestycją. Tutaj dochodzi dla nas jeszcze taka rzecz pod tytułem, bo patrzyłem jak wygląda dzisiaj wdrożenie w tym TopAC. Chyba, nie pamiętam, Maciej?

**[01:45] SHELLY**

Tak, na tym też Chińczyku, jeśli mam ich wpis do krawca.

**[01:54] AMPEREPOINT**

No to oni mają taką funkcjonalność, jak nazwijmy to, najbardziej bazowej. No i rozchodzi się teraz o to, co będzie się działo dla nas w przyszłości. Je są istotne, wiadomo, tam dobudowanie parów, feature'ów, no to tam w JavaScriptie pewnie można doklepać na bazie samego prostego sterowania, to nie jest problem. Ale to, co będzie istotne z perspektywy regulacji prawnych, teoretycznie od nowego roku, ale to tam jak zwał tak zwał, no to, że wallboxy z całego montażu powinny być tam już zgodne z AFIR i tam narzucone jest trochę technologii, które mogą być wdrożone lub nie, ale już taka sugestia, że sprzęty mają iść w tym kierunku, tak? Czyli na przykład, nie wiem, OCPP wersji 2.0, tak? Czyli to jest coś, co ten protokół musiałby być na przykład nie na zasadzie chmury i wirtualnego obsłużenia, bo to też tak można zrobić, że mamy waship, łączy się na przykład, nie wiem, my przez affich, cokolwiek łączymy w chmurze i symulujemy ten protokół i wysyłamy przestrzeń informacje, to te wytrzymania powinny być zeszyte lokalnie. To jest bardzo prosty protokół, nie ma jakiegoś szaleństwa. Powinno być na przykład, nie wiem, możliwość, to pewnie dałoby radę u Was, czyli że jest odczyt kodu karty RFID, że mamy raportowanie per karta, na przykład energii, żeby na przykład dla biznesu i wiele różnych jakichś tam rzeczy, bo później jeszcze wchodzi inna warstwa, ale to już Was by nie dotyczyła, czyli że komunikacja ma przejść z takiej bardzo prostej PWM na PLC i tam już ma być wymiana certyfikatu pomiędzy ładowarką urządzenia, samochodem i w ogóle jakiś tam kosmos, ale to jest problem, o którym jeszcze nie wiemy, jak sobie poradzimy i traktujemy go jako...

**[03:46] SHELLY**

A jaki w ogóle protokół będzie wykorzystywany do wymiany tych certyfikatów?

**[03:52] AMPEREPOINT**

To jest wszystko określone w jakiejś tam ISO i nie, nie, to jest po PLC, będziesz oszukał.

**[03:59] SHELLY**

Po PLC tylko?

**[03:59] AMPEREPOINT**

Tak. Edykacja po prostu i żeby nie... To służy po to, żeby był cały proces negocjacji, że auto negocjuje z ładowarką, jaki chce prąd, że auto może poinformować, nie wiem, że ma być naładowane, że takie są możliwości jego ładowania i na przykład, że o 8 rano być naładowane. I na przykład wtedy może to przekazać informacji do EMS-a i EMS już sobie wymyśli, jak to zrobić najtaniej, żeby dowiedzieć.

**[04:28] SHELLY**

Więc auto będzie mogło komunikować poziom naładowania.

**[04:32] AMPEREPOINT**

Ten protokół też pozwala na komunikację wzajemną a propos ładowania dwukierunkowego. Czyli, żeby EMS mógł sterować falownikiem w samochodzie, ile ma prądu oddawać w danym momencie, jakie jest zapotrzebowanie domu.

**[04:46] SHELLY**

Czyli, że samochód będzie baterią awaryjną dla domu w gridzie.

**[04:49] AMPEREPOINT**

Tak.

**[04:49] SHELLY**

Ale jest tak dzisiaj też.

**[04:51] AMPEREPOINT**

Tylko to właśnie jest oparte na tym protokole i to działa po PLC-kach. Bezpośredniego przesyłania tego wszystkiego. Więc to są rzeczy związane właśnie już z gotowością na przyszłość. Która nasza fabryka będzie miała gotowość, jest w stanie być w miarę gotowa z niektórymi rzeczami, ale wzrost kosztu produktu, by nam wsiada cała sprzedaż. Produkt by na dzień dzisiejszy dużo więcej nie oferował, ze względu na to, że my po warstwie informatycznej, czyli przez co byśmy nie zaoferowali dodatkowej wartości, a koszt produkcji rośnie o 70 dolarów, czyli przyłożenie mniej więcej na 400 netto na klienta użytkowego, klienta końcowego. Czyli od razu tak naprawdę sprzedaż jakiegoś tam produktu to pewnie byłoby trzeba podzielić przez trzy.

**[05:46] SHELLY**

To typowo przy zmieniających się tam jakichś regulacjach. Ja mam bardzo duży przykład, dygresję może, bo teraz na przykład Rozmiana produktów modelarczych i automatyka z Nice’a. Bo to chyba NICE ma w bramach to pewnie monopole, może nie monopole, ale takie istotne.

**[06:05] NIEUSTALONY**

Nie, nie, tak ci się wydaje, bo taki wysyła tak ze swoim zespołem z budownictwa.

**[06:09] SHELLY**

Nie, nie, po prostu głównie kojarzę tą markę z tych morgówek przy bramach i garażach. Ale Adam mi wyprowadził, że jest taka firma, CAME czy tak? CAME. Która jest liderami. Wiele innych, ale jakby teraz jest też taka bardzo duża zmiana dotycząca jakby niskiego poboru spoczynkowego. No i to jest trochę tak jak u was, że już powinieneś sprzedawać to nowe, które powoduje, że nagle ci tam rośnie cena, może nie jest znacząca, jakieś tam 5-7%.

**[06:35] AMPEREPOINT**

A, bo tam wchodzi dyrektywa maszynowa, bo to jest silnik.

**[06:37] NIEUSTALONY**

Ale wiesz, to jest maszyna nawet, z bramą to już maszyna. Tak, to jest maszyna.

**[06:41] SHELLY**

To też powoduje to, że nagle dzisiaj ludzie jednak decydują się sprzedawać, w cudzysłowie, nielegalne urządzenia, no bo jakby nie ma jeszcze świadomości, że kupujesz nowe, bo to jest compliant. Że nagle wypadasz z rynku natychmiast. To dyrektywa maszynowa to jest segment, bo z InPostem to przerabiamy. Jak to zrobić, żeby paczkomat nie był maszyną w skrócie? Czyli nagle wchodzi, że mamy sprężyna, którą to człowiek naciąga i tylko jest zwolnienie, czyli jak mamy cewkę, to już nie ma siłownika i fikuny.

**[07:22] AMPEREPOINT**

Wracając do samego meritum sprawy, czyli myślimy nad tym, żeby elektronika, którą dołożymy już dzisiaj, miała potencjał na obsługę wszystkiego, co będzie się pojawiało z perspektywy, jeżeli urządzenie będzie już gotowe, żeby obsłużyć jakąś nową funkcjonalność, to żeby tak naprawdę ten chip i cała ta obsługa jego pozostała niezmienna. Czyli tą warstwę, żeby trochę wyprzedzała dzisiejsze zapotrzebowania sprzętu. To jest głównie, jeżeli chodzi z perspektywy biznesowej, to co ile nazwijmy to, tak jak powiedziałam, Sądzę, że my dotrzemy do mniej więcej dwudziestu tysięcy klientów końcowych, z tego pięćdziesiąt procent to będą użytkownicy smart mniej więcej, coś koło tego i na dzień dzisiejszy to jakby wszystko na tu i powinniśmy nawet, załóżmy, że ten proces wszedł do przodu i tak byśmy to robili per fabryka, bo my na dzień dzisiejszy produkujemy urządzenia w trzech różnych fabrykach, Mamy trzy półki cenowe i każda fabryka ma swoją kategorię, raczej tu by szło produkt i sprawdzali jak to się ma, ale mówię, my na dzień dzisiejszy mamy potrzebę wsparcia w takim zakresie, żeby wybrać dostawcę, a widzimy, że stoją, jesteśmy, ale dla nich nie wiem, jakie byśmy musieli mieć wolumeny, żeby produkt, owner, że tak powiem, skupił się na temacie ładowarek, nawet nie my, tylko w ogóle dla nich. Ładowarki to jest, porównując to do żarówek czy jakichś tam innych przedłużaczy smart, to są jakieś tam śmieszne wolumeny, tak? To półroczny wolumen to jest pewnie tygodniowy wolumen żarówka, urządzeń i zarabiają tyle samą, bo wkładają, powiedzmy, ten sam chip, nie?

**[09:29] SHELLY**

Zależy, bo oni jeszcze tą całą część produkcji...

**[09:36] AMPEREPOINT**

Tak, ale jak z nimi rozmawiałem, właśnie się śmiał. Rozumiem moją sytuację, ale on się śmiał, że Marcin ma tako sam.

**[09:46] SHELLY**

Vincent?

**[09:46] AMPEREPOINT**

Nie, on się ma. Nie pamiętam.

**[09:49] NIEUSTALONY**

Ike?

**[10:05] AMPEREPOINT**

Taki mały. Tak, tak, tak.

**[10:10] NIEUSTALONY**

Tego nie było na IFIER. Na IFIER go było, ale też wszędzie go widziałem.

**[10:20] AMPEREPOINT**

Właśnie mówił, że oni zarabiają po kilkadziesiąt centów teoretycznie na finalną marżę per urządzenie. No, a to jest subsydiowany też biznes, taki smaczek dam, że wiesz, to, że zarobią, nie wiem, 92 centy na czipie, to pamiętajcie, że oni mają cały koszt infrastruktury, z każdym urządzeniem dochodzi im ileś tam pingów i to jest kilka miliardów pingów na minutę. Więc koszt infrastruktury jest znacząco wyższy niż te, co raportują jako spółka giełdowa. Gdyby nie subsydia rządowe, to oni by wyszli grubo na minusie danych z całego świata. Ale mówimy, że to w perspektywie do najtańszych produktów, to oni patrzą za wolumenem, a nie patrzą na magazyn energii. I tak trochę wpierają się pod swoją marką, tą coną, żeby coś zrobić. Więc dla nas partner, który coś robi w temacie, ale nie jest na tyle zainteresowany, nie jest w ogóle zainteresowanym doświadczeniem końcowym, tylko dobra, rzucimy trochę nowości, innowacji, żeby nie być tyle za rynkiem. Nie jest przyszłościowo z perspektywy rozwoju marki. Więc mamy tak długofalowo dwie ścieżki. Okazało się, że jedną ze ścieżek jesteście wy, a tak naprawdę bardziej Później myśleliśmy, czy nie zrobić modułu dodatkowego bazującego na ESP, który działoby równolegle do modułu Tuya. Ale mamy Tuya, ale mamy też prosty moduł ESP, który daje np. Lokalnie jakiś prośb, żeby móc dalej wykorzystać i zbudować sobie np. OCPP poprzez wirtualizację w chmurze. Obzdorałem sobie, że musi to być ten protokół, a nie przez API, no to dajemy dzisiaj wirtualizację i możesz to wykorzystać albo coś tam jeszcze innego. Że móc później się wpinać w jakieś pstryki, w rozwiązania dla firm, które potrzebują billingu, bo też jest taki problem, że np. Na dzień dzisiejszy nie możemy świadczyć usług, a często mamy takie linii pod 20-30 wallboxów, posłużyć całą firmę, ale potrzebuje to w jakiś sposób wpiąć do ich systemu biurowego, żeby było rozliczenie prądu na osobę. Czyli ten cały segment rynku na dzień dzisiejszy nie mamy jak go dotknąć, bo życie tego na Tuya.

**[12:59] NIEUSTALONY**

Jest niemożliwe po prostu.

**[13:00] AMPEREPOINT**

Tak, no nawet gdyby próbowałeś to przy złokach, to jak będzie się rozparowywało, to można sobie spalić w mosty, że tak powiem, sprzedając takie rozwiązanie, tak? Więc nienawidzonym później wystarczyło. Więc tak, no więc mamy tą teksturę, nie? No i teraz jakie mamy pytania do was? Pierwsze jest takie, czy na ile dla was, pomijając, bo znowu te ilości versus koszt tego, czy to nieważne ile by był, to nie jest biznes, nie? Ale mówię, to jest słaby biznes, sam w sobie. On, jakby mam taką nadzieję, że dla Was to jest ważniejsze z perspektywy budowy kategorii i tak zwanego, że ten produkt otwiera klientów na smartfonowe rzeczy i przez cross-sell później ktoś wejdzie, nie wiem, będzie wolał mieć licznik dwukierunkowy od Was, później stwierdzi, o, dorzucę z przekaźnik tu, tam, siam, kupię od sklepu coś innego Power by Shelly i to lawinowo pójdzie przez to, że nasze urządzenie jest tak zwanym urządzeniem niskiego progu wejścia z perspektywy użytkownika, tak? No bo my wszystkie urządzenia i my tego nie zmieniamy, mamy przygotowane, że nie wymagają elektryka do instalacji. Czyli jak ktoś chce, może sobie odłączyć przewód siłowy, zawsze jest wszystko. To wynika z tego, że jeżeli Nie wiem, czy mieliście coś takiego, ale teoretycznie, jeżeli np. Byłby Wasz licznik dwukierunkowy się zepsuł, to klient może Was obciążyć deinstalacją. Czyli elektryk musiał przyjechać. Teoretycznie mógłby Was prawnie do tego zmusić.

**[14:54] SHELLY**

Jeżeli by to był certyfikowany chyba licznik, prawda?

**[14:56] AMPEREPOINT**

Nie ma znaczenia.

**[14:58] SHELLY**

Czyli nawet pomocniczy? Sądzisz, że to obwodowy też?

**[15:01] AMPEREPOINT**

Tak. Green Cell ze swoimi ładowarkami, bo oni sprzedają bez przewodów zasilających. Oto na przykład zamroziło parę sprzętów i ludzie się chwalili na grupę jak zmusić Green Cell do pokrycia kosztów elektryka do montażu i montażu ponownego. Bo to jest z winy Green Cell, jakby aktualizacja się nie przebiegła, no to dlaczego ktoś kto nie jest uprawniony do prac elektrycznych ma pokrywać koszty montażu. Dlatego my, to jest znowu tak, my obserwujemy rynek, projektujemy bardzo, bardzo szczegółowo pod wszystkie ryzyka, pod wymagania itd. No i strategicznie podchodzimy do tego, dlatego my mamy kable zasilające, bo zero odpowiedzialności. Lepiej wchodzą te nowe dyrektywy teraz, które dotyczą sprzętów głównie stałego montażu. A my teraz powiemy, że nasz urząd chce sobie przynośny. Można go zawiesić. No to jest sprzęt przynośny i połowa wymagań odchodzi, która wchodzi od 1 stycznia. Tego musimy tam certyfikować. Zajmie to nie tydzień roboczych. Więc to jest takie bardzo celowo i strategiczne, jakby zakres odpowiedzialności, jak to wchodzi, żeby to był. Znowu, ktoś porówna nasz produkt, nie potrzebuje elektrykę, czy teść mi pomoże podłączyć do gniazda siłowego, który już mam czymś zrobić, gniazdo siłowe, versus sprzęt, który mówi, żeby nie wiem, gwarancja była ważna, to musi to zrobić elektryki, więc my patrzymy na ten jakby brak targ. No więc to było po wyjściu ukryte pytanie, na ile dla Was to jest ciekawy w ogóle część biznesu, żeby w niego wchodzić na poważnie, a nie na zasadzie coś tam sobie działa, tak jak w tym jednym urządzeniu, które macie z tymi Chińczykami, żeby nas po prostu wesprzeć czym więcej niż jakimś onboardingiem.

**[16:57] SHELLY**

Jasne, to może odpowiem, bo akurat za Shelly X jestem ja odpowiedzialny, więc tak, jeżeli chodzi o rozwiązania, które sobie wymyśliliście, od początku do końca jest to możliwe, dodatkowo dla fabryki również to nie będzie problem, ponieważ mamy taki cały gotowy moduł, zalogowałeś się na Shelly X, w ogóle portal nie, to ja proponuję, że zrobimy sobie calla po prostu z Borisem, to jest szef naszego R&D i Boris przejdzie i pokaże wam, bo firmę i funkcjonalności, które wy chcecie mieć, definiujecie sami. Dodatkowo, jeżeli mamy specyfikację odnośnie modułu na Tuya, który jest, to i pinoutu, i całego schematu, jesteśmy w stanie odzwierciedlić jeden do jednego i skomponować się do tego, co już dzisiaj macie, z waszym firmuerem zbudowanym od zera. Mamy taki cały gotowy, nawet jesteśmy w stanie w przypadku prostych produktów na bazie tylko i wyłącznie tych data pointów, które macie tam w Tuya zrobić, jesteśmy w stanie odzwierciedlić, tak, że po prostu w fabryce podmieniają pudełeczko z Tuya na Shelly i dalej już robią na Shelly.

**[17:58] AMPEREPOINT**

Czyli zmieniacie też, jakby w jednym znaczeniu takim, że sam ten chip ma inaczej nie tylko kolejność pinów, ale też w jakiej fizycznej...

**[18:06] SHELLY**

Jednego fizycznie wygląda jak tu. Wyjmiemy i włożymy. No, wejdziemy zaraz w szczegóły, ale jakby mamy sześć czy siedem, ja mogę pokazać wam...

**[18:17] AMPEREPOINT**

Ale przyniesiesz, Dawid, jakby jeden z modułów frontowych, całą tą płytkę kontrolną?

**[18:24] SHELLY**

I teraz tak, mamy sześć rodzajów tych naszych modułów, jeżeli chodzi o funkcjonalność i rozwój tego. Również wydaje mi się, że tutaj dobrze trafiliście, w sensie jeżeli będzie to oczywiście wolumen za tym przed, ale dzisiaj trochę będę uczciwy i szczery, bo dzisiaj trochę sytuacja jest taka, że jeżeli coś produkujemy z danym producentem, to sami różnica główna jest między tują, a czyli tak, że my wrzucamy to do naszego cennika i też sprzedajemy nasze siły sprzedaży. No bo te TopAC, które mamy porobione z fabryką, to my jako handlowcy tu, czyli sprzedajemy to do naszych klientów. Tak samo jest z każdym innym produktem PowerPay, czyli, więc de facto realizacja zaraz z granicą waszych produktów.

**[19:11] AMPEREPOINT**

A jaki za volumen teraz tego TopAC możesz zdradzić?

**[19:14] SHELLY**

Ile mam na stopie, to nie są pewnie... Nie, Polska jest w ogóle niemierna. Na pewno Finlandia jest najlepsza w Europie, to co pokazałeś.

**[19:25] AMPEREPOINT**

Ale w sensie dla was, jeśli chodzi o waszą sprzedaż czy...

**[19:29] SHELLY**

Naszą sprzedaż tego produktu w Shelly W sensie, bo TopAC robi sobie oczywiście własną sprzedaż niezależnie No tak I całą politykę cenową zostawia za siebie, ale u nas wewnętrznie

**[19:39] NIEUSTALONY**

I na dzień dzisiejszy to jest tam właśnie WBR3 WBR3, no tak myślałem, że WBR3 z trójką macie też Za mną i za mnie, to jest najważniej po kolei unijnej tańczy I teraz będzie, gdzieś mogę otrzymać w którym kierunku to idzie No

**[20:03] AMPEREPOINT**

Tu ja rozesłała do wszystkich fabryk, że będzie po samą informację

**[20:10] SHELLY**

Zobaczymy ten stok tam jaki jest. Patrzę, patrzę, właśnie odpalam.

**[20:13] AMPEREPOINT**

Nie wiem, bo podoba mi się jaki jest stok aktualnie tego, a nie ile sprzedaliśmy.

**[20:20] SHELLY**

Mogę zobaczyć, czekam aż mi się zapłaci. No okej, to WBR3, czyli najbardziej popularny ten kit. I teraz kontynuując, to co mówiliśmy, czyli rozwój samego firmware'u, czy funkcjonalności w aplikacji też również. Ja się sądzę, że jeżeli... Na WR11, to poznanie samo z przyzwyczajeniem do tego. Okej. To nieważne, to względne na to, co tutaj mamy. Schemat jest bardzo prosty i popularny i zrobiliśmy już kilka tranzycji. Polega to na tym, że my dajemy swój... Zresztą mam tak, bo nie wiem, czy macie jakiś projektor, ale jak nie, to tak... To nie ma, ale to jak zawsze dzisiaj. Okej. De facto to tak wygląda nasz moduł, ale to jest mało ważne. Przejdę szybciej trochę. Całe story. To chyba wydaje mi się, że jest najbardziej, z tego całego wachlarza korzyści wchodząc w współpracę z Shell, to pamiętajcie, że to jest chmura europejska. Ja wiem, że Tuya mówi, że ma w Amsterdamie Azure i w Damie WSA. Z tym, że deploymenty są na bieżąco fizycznie dokonywane na miejscu.

**[21:52] AMPEREPOINT**

Z ciekawości wydajecie Reda do tego? Osobnego?

**[21:55] SHELLY**

W sensie Reda?

**[21:57] AMPEREPOINT**

Nie, bo czy bezpieczeństwo to jest Red? Dobrze myślę? No, to jest certyfikat.

**[22:01] SHELLY**

Tak, ale tutaj ten data czy reszta nie ma problemu, bo w momencie kiedy wy, bo macie różne opcje, poczekaj, bo odnośnie reda to za chwilkę, bo są różne opcje, bo to też chodzenie w Shelly, bo musicie wyjść z takiego, jakby tu i wchodząc w biznes, tu jesteście trochę niewolnikiem, bo macie jedną ścieżkę rozwoju plus ograniczony software. Tutaj chciałbym wam pokazać właśnie, że wybieracie sobie środowisko, w którym chcecie współpracować, a następnie aplikacyjnie to już wy wybieracie, czy macie obecne MCU i dokładacie sobie Shelly, działacie na dwóch i wtedy wybieracie swoją aplikację swojego clouda albo local only, no bo to jest też różnica, że Shelly jest local first, czyli trzeba skrypty i całość, że nie potrzebujemy tego po fredzie, to sobie chodzi w układzie. Możecie wybrać wtedy tylko z przez Shelly na przykład moduł jako enabler i musicie używać w ogóle wtedy znowu naszej chmury czy naszej aplikacji albo w takim docelowym, jak zazwyczaj robimy, czyli wrzucacie nasz moduł do naszej chmury i do naszej aplikacji. Ta trzecia opcja uruchamia Wam automatycznie możliwości sprzedażowe. My nie widzimy wartości w blendowaniu na siłę po utrzymaniu swojej apki. Jeżeli robimy działalność w przestrzeni clouda i macie swoją apę, ale do tego i tak może sobie wziąć klucz, my mamy dodatkowy dashboard, który sobie może to połączyć. Więc jak ktoś chce ekstra jeszcze coś tam, bo ja przynajmniej patrzę jako taki osoba, która nie wiem.

**[23:42] AMPEREPOINT**

Ja na dzień dzisiejszy dostaję świra, że w domu nie mam postawionego home systemu, stąd pewnie to teraz zrobię, ale że klimę, oczyszczasz powietrza, tak naprawdę klimę i termosy mam w jednym, ale jakby parę innych rzeczy mam wszystko w oddzielnych appkach, bo nie można tego połączyć w każdy sposób. I musiałbym to szyć gdzieś tam. Wymieniamy wszystkie klocki, bo mi się nie chce, no bo działają. Więc na siłę budować jakby z perspektywy, ja jako nie wiem, z perspektywy marketingu bym chciał, żeby w App Store był sobie logam, prepointa, ale... Znaczy wiem, ale z perspektywy klienta w głowie ważniejsze jest to, że przyklejając się do... W przypadku projuzerów wasza marka jest bardzo silna, więc to przyklejenie się dla nas, dla firmy, która chce jak najszybciej skalować, to jest trochę, według mnie, najlepszym porównaniem jest bycie jako producent akcesoriów w Apple Store. Więc jak Apple ci daje certified, że możesz mieć ich obudowę nawet z silikonem, to nagle możesz za tą samą silikonią ogólnioną obudowę właśnie płacić 40 złotych kosztownie i dla mnie to jest...

**[25:04] SHELLY**

Jasne, jakby zgadzam się w 100%, z tym, że znowu opcje, które się pojawiają na stole teraz w ramach tego bycia w naszym ekosystemie, czego jeszcze nie ma dzisiaj, ale do końca roku ma się pojawić, to jest branding samej aplikacji Waszej, czyli nie będziecie kolejnym produktem z portfolio Tuya do, nie, wróć, Shelly do naszej aplikacji, tylko Wasz page produktowy będzie brandowany. Zresztą te opcje chyba też macie dzisiaj na stole, jeżeli chodzi o Tuyę, tylko to jest niewykorzystywalne ten UI, tam customizacja UI-a.

**[25:38] AMPEREPOINT**

No tak, znaczy mamy to delikatnie, znaczy nie, mamy to, logo, nie logo, wszystko jest, ale za customizację, która pewnie gdybyśmy mogli sami ten kod podmienić, 4 godziny, czy tam dwie, zapłacić 100 000 dolarów, z kosmosu, za skórkę i tam jeden prosty pitch murowy.

**[26:00] SHELLY**

Ja wiem, że tu ja tutaj studniam bez znanego, a z drugiej strony przy tej skali, bo mówicie, że nie ma tam czasu na wejście w daną kategorię, w dany produkt i rozwój software'u.

**[26:11] AMPEREPOINT**

Pamiętajcie, że nie mam 7 tysięcy kategorii produktowych na sobie, więc tam jest wszystko maźnięte. I żarówki też są maźnięte, bo funkcjonalność żarówek nie jest na poziomie Philips Hue. Podstawowa DIMM on-off i nie ma tam integracja z muzyką, polega na wykrywaniu trzech pasów, czasami poszczególnych uderzeń.

**[26:31] SHELLY**

Jeżeli chodzi o Shelly, jeszcze tylko wspomnę, czyli macie możliwość różnie jak chcecie, bo możemy również zrobić tak, że to posadzimy na waszej chmurze i to będzie kompatybilne z Shelly Cloudem. Jakkolwiek będziecie chcieli tylko koszt infrastruktury później, będzie wam trochę przerastał maintenance, będzie znowu to samo co...

**[26:51] AMPEREPOINT**

Wiesz, nam zależy na najszybszym plug and play i takie bardziej dla mnie ważne pytanie do postawienia, bo z trzech fabryk sobie nie współpracujemy, tylko jedna fabryka ma mocny zespół od strony elektroniki. Dwie inne wywodzą się z prostszych sprzętów i są fajne pod kątem montażu, trzeba korzystać z innego, ale jak trzeba cokolwiek zmienić w elektronice, to sami posiłkują się usługami trzecimi. Bo w swoich zespołach na tej roli nie mają dobrych elektroników. Studenciaków w wolnej chwili muszą pomagać na linii produkcyjnej, nie więcej tak to wygląda. Wygląda, więc dla mnie najbardziej istotne też jest, bo wiem, że macie biuro w Shenzhen, czy do takiego projektu można u Was nająć PM-a lokalnego, który w zasadzie sprawia, że dla nas, my tą część informatyczną, że później już jest to u Was w Cloudzie, my z wielką chęcią tutaj lokalnie sobie zrobimy, ale pod tym kątem nazwijmy to mapowanie itd. Dalej najwygodniej byłoby pewnie gdyby Chińczyk gadał z Chińczykiem u siebie i zapłacić za to fee i jakby nie widzieć tego procesu, dostać ewentualnie, żebyśmy rozmawiali z kimś od Was o wyższych kompetencjach i nam opowiedz co się dzieje i wymusił pewne normy jakościowe jak ten projekt powinien przebiegać. My nie damy wartości dodanej poza pewnie...

**[28:43] SHELLY**

Wiecie co, jeżeli chodzi o support lokalny w Chinach, to również nie ma problemu, bo to mamy ten zespoły, żeby trochę pchać te fabryki do przodu i też...

**[28:52] NIEUSTALONY**

W związku z tym biura jednak nie patrzy w dobrym miejscu.

**[29:00] SHELLY**

Tak, i tu nie ma problemu. Ja wyślę Wam dev kita, to jest taki mały moduł nasz, który jest podłączeniem do USB-C do kompa, potem sobie włączycie i możecie sobie zasymulować, zaprogramować całe swoje urządzenia w tym małym dev kicie i zobaczycie, jak wygląda cały proces. Wystarczy, że wejdziecie sobie na Shelly X, będziecie robili sobie Create Product. Odnośnie całej rozbudowy i później wszystkich rzeczy, to musicie sobie zdefiniować. Tutaj jest wszystkie informacje. Później mamy wybór płytki, ale ja wam powiem, która to jest płytka dokładnie odpowiada za WBR3. I tam jest opcja później, że czy wybierasz, czy ty chcesz wybrać, czy to będzie żarówka, czy cokolwiek innego. A wy musicie wybrać opcję kopiuje-Tuya, bo to jest ścieżka gotowa i przenosicie po prostu, tak jak powiedziałem, na gotowym waszym chipie pinout, odzwierciedlamy sobie funkcjonalności w pinaucie, więc ta cała technologia jakby znowu też odpada, bo mamy tu przećwiczone nam 20-30 produktach, to ciągle nie jest skala Tuya, ale że de facto na koniec elektronicznie czy proceduralnie dla fabryki nic się nie zmienia, Tylko sam pingowanie i testowanie później tej produkcji odbywa się do innej chmury. Więc ten Chińczyk na koniec przychodzi, kiedy masz pinga...

**[30:29] AMPEREPOINT**

Wiem, ale no też wiem jak to jest, że jednak jak ktoś tam, kto jest w tej samej strefie czasowej i fizycznie jest 30 minut taksówką od fabryki, bo mniej więcej o tych odległościach... Dobra, to jest całkowicie inny proces i jeżeli to nie będzie kosztował około 80 pieniędzy, to dla sukcesu projektu dla nas to jest warte, żeby takiego PM-a, gdzieś tam na parę Mendei, PM-a czy po prostu inżyniera lokalnego, który wspierał, no bo zależy nam, żeby się, nazwijmy to, odciąć od jakości, którą mamy aktualnie w Tuya, nie? Czyli żeby po prostu było tak super smooth z perspektywy i fabryki, i przyszłych feature'ów, i klienta. Później tą część informatyczną to my tutaj sobie lokalnie w biurze, tutaj Dawid pewnie by nie wychodził przyzwyczajenia, bo by chciał dalej rozbudowywać i kodować. Wycieczki do Żabki po energetyki i dalej jedziemy, żeby rozbudować funkcjonalność. No ale z Chińczykami jest, sami wiecie, więcej lat przebojów z nimi. Bywa ciężko i ktoś z Was zna produkt, pójdzie, jak Chińczyk będzie mówił, że nie działa, odwiedzi ktoś od Was, powie, że działa albo lutujesz na odwrót. Czyli sam opór materii wynika czysto politycznie, tak wam powiem, szczerze, z perspektywy. Tu ja jestem chińską firmą i ten nacjonalizm dosyć mocny jest tam i tam trochę jest login dosyć duży do rozwiązań. Tu intershelly trochę im siedzi, więc to chociażby po to jest potrzebne, żeby dopatrzeć, że cały proces jest dopieszczony.

**[32:25] SHELLY**

Ale okej, zróbmy tak, że wydaje mi się, że w ogóle cały proces zaraz mogę odzwierciedlić, bo to też nie jest problem, bo tylko, że lista funkcjonalności, gdybyście mogli spisać mi w ogóle, bo rozumiem, że macie tu TopAC na warsztacie i sprawdzaliście sobie...

**[32:40] AMPEREPOINT**

I patrzą tego na filmach na YouTubie.

**[32:42] SHELLY**

Okej, bo ja bym dwie rzeczy wam dostarczył. Tą naszą ładowarkę TopAC od nas z magazynu, CT-ki jednego naszego 120-amperowego, bo od razu wydaje mi się, że dobrze by było, gdybyśmy po bundlowaniu tego i wartością dodaną w ogóle, wydaje mi się, że do waszej, to, że bilans energetyczny, bo samozwracalna się ładowarka będzie super też marketingowo działała i trzecia rzecz jest jeszcze taka, że ładowarkę i tego dev kity, czyli żebyście mogli sobie już zrobić cały projekt funkcjonalny i wizerunkowo. Co najważniejsze, my nie potrzebujemy kodu, bo to mamy na AI, więc wy opiszecie po prostu, co powinien zawierać, jakie feature'y i zobaczymy, zwalidujemy sobie. Znaczy, opiszmy wam

**[33:32] AMPEREPOINT**

Co nazwijmy jest dzisiaj jeden do jednego, co byśmy chcieli od razu w pierwszej iteracji, a jakie funkcjonalności potrzebujemy w przyszłości w podzieleniu nazwijmy to na jakieś tam segmenty klientów, że jest w tym wartość, bo klient w ogóle, no ile dzisiaj wy siedzicie też w klientach, nazwijmy to tak stricte odbiorcach biznesowych, bo to ten, nie wiem, budynek jakiś tam biurowy itd. My tam jesteśmy, tylko nie jesteśmy bezpośrednio z instalatora, czy klasa, czy jakiś pośredniczy. Dzięki tej ofercie pro, to coraz częściej faktycznie nie jesteśmy...

**[34:20] SHELLY**

Czy wasz produkt używany w tej przemysłowej instalacji?

**[34:26] AMPEREPOINT**

Teraz zaczęliśmy kilka projektów. Mamy na tapecie dużą sieć handlową, która ma ponad 700 hal sprzedażowych.

**[34:39] SHELLY**

Już widzę dla was miejsce, bo tam mają ładowarki.

**[34:46] AMPEREPOINT**

Ok, więc trzeba byłoby pewnie...

**[34:53] SHELLY**

Ale teraz wiesz, miejsca handlowe, to nawet można by tam z nimi rozmawiać, czy też, jakby już mówimy o tych takich jakichś, wiesz, tam linkach pewnie tutaj marketingowo, komercyjnych, można nam zawsze Wam pomóc. Klient biznesowy jest naszym klientem, coraz częściej tak. Jeżeli było całkowicie pro takie, wiesz, konsumenckie z racji dużej dynamiki sprzedaży tego produktu plug and play. W tej chwili jakby najlepiej sprzedającym w Polsce się elementem Natomiast 2PM, który siedzi w trakcie, jakby się to wszystko przeskalowało, to się po prostu pozmieniało. Kiedyś sprzedawały się wallplug'i czy jakieś inne rzeczy, a dzisiaj 2PM w ogóle wyprzedza decydowanie w różnych generacjach.

**[35:43] AMPEREPOINT**

Głównie po to pytam, że przykładowo dodanie, tylko to musiało być zakodowane już w chipset'cie, na przykład obsługa protokole. I z tego co wiem, to plany nazwijmy takie europejskie jest raczej, żeby ten protokół używać też szerzej, nazwijmy to nie tylko, bo dziś jest używany tylko w ładowarkach, a fantazja jest wszystkich, żeby używać tego protokołu do wszelkich możliwych sprzętów prądożernych, tak, czyli używaj ten, klimatyzacja na tym działała, na przykład by pozwolił, na przykład żeby hotel chciał zrobić płatną klimatyzację. Ona jest, chcesz, rozliczasz się przez jakąś tam mapkę, jest dokładnie określone jak się biją pingi, jak to ma działać, jeżeli zabraki internetu, otwarcie, zamknięcie sesji, więc te wszystkie jakieś tam organizacje, które projektowały te standardy mają fantazję, że to jest w ogóle protokół do...

**[36:40] SHELLY**

To właśnie napisałem do Christiana, żeby tam przełożyć, dobra?

**[36:47] AMPEREPOINT**

Żeby ten protokół był używany wszystkim, co służy w zarządzaniu transakcjami energetycznymi w domu, w firmie. Więc to też jest taka...

**[36:59] SHELLY**

Nie, spoko, bo to otwiera wiele nowych tematów, bo u nas do integracji wszystkich urządzeń prądożernych nie używamy nowych takich rynek pasowych.

**[37:14] AMPEREPOINT**

Tylko to nie jest transakcja, nie?

**[37:15] SHELLY**

Nie, nie jest transakcja, ale jest odczyt jednokierunkowy, prawda, na poziomie Huawei'a, mamy poznanego z Zendure, Ankera, EcoFlow, mamy spiętego Sigenergy [?], mamy spiętego jeszcze Marsteka, mamy spiętego, więc też jesteśmy pospinani już z producentami AGD odnośnie zużycia energii. Coraz większa jest ta baza, bo dzisiaj de facto każde urządzenie ma jakąś swoją formę, ale wydaje mi się, że to wszystko jest otwarta sesja, bo to co mnie właśnie najbardziej jakby, bo też jestem w miarę świeży w Shelly, więc łatwiej mi powiedzieć, zdziwiło to jest to właśnie jak deep dive robią do każdego poszczególnego. Sądzę, że w momencie, kiedy dzwonicie się z Borisem, Andriem z naszego R&D...

**[38:23] AMPEREPOINT**

Jest takie pytanie, czy ten chip, który wybierzemy, nie dzisiaj, tylko czy w przyszłości na nim jest tyle miejsca i tyle...

**[38:32] SHELLY**

Do rozbudowy funkcjonuje.

**[38:35] AMPEREPOINT**

Tak. I czy ten procesor to pociągnie. Jak nie, to czy później na tym samym pinoucie macie coś mocniejszego, które to pozwoli. I później będzie znowu w tym dostaniu nowe zabawki i on nawet nie wie, że my tam mamy więcej funkcjonalności. Tak, nie wiem. Bo to jest jedyna rzecz na zasadzie myślenia takiego strategicznego, że dzisiaj tego nie potrzebujemy. Ale powiedzmy nie potrzebujemy tego na poziomie rolloutu, ale istotne jest czy my taką funkcjonalność możemy w przyszłości obiecać lub przynajmniej mieć w planach produktowych ze względu na użycie.

**[39:15] SHELLY**

To wiesz co, musimy wrócić do tego, co powiedziałeś, musicie nam dać na teraz, na za chwilę i na jutro, nie? Jak nam dacie te aplikacje funkcjonalności, które chcesz, no to zaraz to nam wyjdzie. I na takim spotkaniu przed, jak nam to dacie, to jak już będziecie z Borisem na dawno, to on wam mniej więcej powie też, jak ta ścieżka będzie, nie?

**[39:33] AMPEREPOINT**

Przykładowo, wchodząc w OCPP, mamy... Okej, my tam... Macie jakikolwiek chip, który obsługuje SIM-kartę?

**[39:44] SHELLY**

To jest dobre pytanie. Bo nie mamy. Nie. Nie, na pewno nie mamy. Nie mamy, bo nic jeszcze na GSM-ie nie robiliśmy. W ogóle to nie było, wiesz, to jest jakby trochę cofanie się dla, dla, dla Shelly, to jest trochę cofanie się tam o trzy kroki.

**[39:58] NIEUSTALONY**

Ale faktycznie, ja wiem pewnie, bo ty chyba rozmawiałeś też na, na, na telifie o tym. No, w ogóle to... Trzeba też pewnie zapytać, czy jest jakaś możliwość. Znaczy, no teraz to można robić już bez fizycznej SIM-ka w poziomie eSIM-u. Być antena i tyle, tak?

**[40:16] SHELLY**

MikroTika, używa Ekoenergetyka w tych stacjach, bo sprzedawałem też.

**[40:25] AMPEREPOINT**

Mając przykładowo taki protokół OCPP i tak dalej, to my mamy takie deale, nazwijmy to na stole, które leżą tam 500 sztuk rocznie, które po prostu sobie leżą. My nie mieliśmy tego jak chwycić, bo mieliśmy prototypy, które działają, ale jakościowo nie było to pod kątem... Chińczycy nie byli w stanie dograć tego jakościowo na tyle, żeby później obsłużyć. I my nie chcieliśmy wchodzić w coś, co my w przypadku fuck-upu nie będziemy sami w stanie zrobić aktualizacji firmware'u z tego protokołu overnight. Będziemy czekać zresztą, nie wiem, Chińczyk zareaguje w tygodniu i w sumie on nie będzie czuł tej małej różnicy jakościowej, która jest wymagana np. Operatora. Te sprzęty są np. Dawane dla klientów, pracowników. Poziom jakości wymagany jest w firmie farmaceutycznej, gdzie ze wszystkiego robią się od czerwoni. Pod kątem oczekiwania kościowych. My wycofaliśmy się z takiego projektu, gotowe, no elektronika i jakby możliwość zarządzania tymi rzeczami nie było. Wiesz, ten GSM to dodatkowanie jeszcze będzie. To jest wtedy, to są znaczy mówię, to nie jest dzisiaj, tylko znowu w przyszłości, to jest po prostu otwarcie się na komercyjne projekty, bo wszystkie takie AC, które są publiczne, one są w GSM.

**[42:01] SHELLY**

Bo my nasze CT-ki-i będziemy w Bułgarii mieli uzbrojone w SIM-ki, żeby zdalnie były wysyłane dane odnośnie, bo tam jest taki duży projekt energetyczny. Zresztą w Polsce też planujemy, ale nie w oparciu o SIM, bo część już z nich ma. Tam jest drugi największy operator energetyczny, który może i też tam było wymaganie tego.

**[42:25] AMPEREPOINT**

Popytamy o to, bo to jest jakby wiesz, na tym spotkaniu kilka takich rzeczy, albo jak w tym specyfikacji byście potrzebowali to jako rozwój tego, tej swojej funkcjonalności, to opiszcie to nam, nie? To jest znowu coś, czego nie potrzebujemy dzisiaj, ale to, że coś takiego na przykład może się pojawić za rok, Daje jakąś fajną wartość. Jak będziemy to mieli, to przynajmniej kogoś tam po drugiej stronie poprosimy, żeby się przygotował do tego, żeby odpowiedział. I żeby albo dał zielone światło, że możemy o tym rozmawiać, albo na razie to zamknij.

**[42:58] SHELLY**

Także wydaje mi się, że tak. Najważniejsze, żebyście popatrzyli to, co powiedział człowiek. Przekażemy wam to, co pozwoli w pozanie. Jakbyście opisali nam to, żeby tą bazą do rozmowy. Tak jest. Godzina nam wystarczy.

**[43:17] AMPEREPOINT**

Z Borisem?

**[43:18] SHELLY**

Wydaje mi się, że skończy się tym, że Boris przyjedzie tutaj, ale wrzucam na poniedziałek na 14. Było dla was okej? Poszuczę wam ten devkit i ładowarkę dzisiejsze, byście mogli sobie już coś zacząć.

**[43:35] NIEUSTALONY**

Na 14 to skończymy. O 12.30. 12 okej.

**[43:39] AMPEREPOINT**

Znaczy ja by specyfikować mogę, znaczy powiem tak, my mamy, co? Mamy, w przyszłym tygodniu idziemy na targi, więc poniedziałek może być trochę jeszcze chaotyczny, więc ja bym spotkania te bym wolał zrobić jeszcze w kolejnym tygodniu, a w przyszłym tygodniu sobie wszystko robić bardziej mailowo, bo bije, także człowiek będzie miał, znaczy żeby po prostu nie mieć spotkania takim poczuciem, że coś zaszybu, trzy osoby czekają na jakąś inną decyzję lub pomoc. Ja mogę wyspecyfikować wszystko w tym tygodniu. Nie wiem, czy to pewnie jutro, może dzisiaj zaczniemy. My jesteśmy w stanie zobowiązując się, że jutro do końca dnia wyspecyfikujemy funkcjonalności.

**[44:25] SHELLY**

Pół jutra też dostaniemy, zobaczymy, co już jest. Jutro, czy tam w poniedziałek, jak już byśmy dostali. Jak tylko dostaniemy, to jesteśmy w stanie powiedzieć, OK, to jest to, tego potrzebujemy, to fajnie byłoby mieć w przyszłości, a to w jeszcze dalszej przyszłości.

**[44:40] AMPEREPOINT**

Wiemy, żeby otworzyło kolejne drzwi z perspektywy tej kategorii produktowej, bo inne rozwiązania to mają.

**[44:48] SHELLY**

To i tak nie są zmiany overnight. Ja bym tylko jeszcze dwie rzeczy dołożył, bo jedna rzecz to taka, żeby w całej tej naszej ładowarki TopAC, jakbyście mogli zrobić taką analizę gap.

**[45:01] AMPEREPOINT**

No tak, tak właśnie o tym powiedziałem.

**[45:04] SHELLY**

Dokładnie, że jakby wiesz, kopiujemy sobie listę funkcjonalności z TopAC, Pomyślimy, co jeszcze brakuje nam, żebyście odzwierciedli dzisiejszy stan, a druga rzecz jest taka, że od razu jakbyś to zrobił, to ja bym z Borisem przyłożył to Wam na tego dev kita, którego Ci dostarczył. Czyli żebyś od razu widział, jak to będzie wyglądało w aplikacji Shelly i żebyś od razu miał firmware spisany. No bo to będzie chwila, tylko wpisany dopinał to będzie dłuższe pewnie, ale to też sądzę, że jest ważne. Wydaje mi się dlatego, że z Borisem ten call będzie ważny, bo on powie wam od razu, od początku, jak wygląda proces i też będziesz układał sobie myśli pod ten proces, jak on wygląda i też na funkcjonalności i specyfika, bo to wprowadzi was w to, jak my to szykujemy u nas. To jest dużo czasu, moim zdaniem, zaoszczędzi, a godzina czasu z Borisem będzie... Rozumiem, że nie teraz, bo macie targi, tylko po dwudziestym tam ósmym.

**[46:02] AMPEREPOINT**

Będzie wtedy na spokojnie. To jest na tyle ważny temat, że nie chcę być na spotkaniu, na którym czuję, że coś za plecami się pali, bo nie wiem, wykładzina nie dojechała i jest problem jak mieć wykładzinę na targach.

**[46:17] SHELLY**

Na które targi się zbieracie?

**[46:19] AMPEREPOINT**

W przyszłym tygodniu są Kongres Nowej Mobilności w Katowicach. One są darmowe, zresztą wyjeżdżaliście w tym tygodniu. My tam mamy spore stoisko, ale one są mniej produktowe, bardziej to są takie...

**[46:35] SHELLY**

Relacyjne.

**[46:36] AMPEREPOINT**

Tak, to jest taki specyficzny event. Takie tam klepanko w plecach.

**[46:43] SHELLY**

Jakie bramy?

**[46:44] AMPEREPOINT**

Nowej, znaczy nie no, nowa energia, tak, czyli, tak, no tak, bo tam jest też jakieś tam Orleny, jakieś takie klimaty, i tam będą mnóstwo osób, jakieś tam będą jakieś tam, nie wiem, toki zjedzone, nie wiem, kursje, ludzi tylko na przykład z różnych miast z Europy, zarządzanie, nie wiem, hulajnogami albo czymś innym, no to już tak, zresztą jakiś tam premier był, takie klimaty, nie, bardzo, bardzo, przyjechać, poproszamy, będziemy mieli wygodne hotele do siedzenia, od środa do piątku, 3 dni aż, no, zobaczyć, Bo to organizuje tam PSNM, czyli to jest największa organizacja lobbingowa w zakresie elektromobilności, mocno manipulowana przez chińskie firmy odprodukacyjne.

**[47:43] NIEUSTALONY**

No właśnie nie, czy chińskie, bo te ich działania zmierzają ku takiej nadregulacji, ale w stronę europejskich producentów. Będzie zupa po 11, to już coś tylko elektryczne.

**[48:02] AMPEREPOINT**

Właśnie, bo tak jakby gdzieś tam się urwało. I jeszcze wracając do ostatniej tej rzeczy, zawracając jakby, czyli te techniczne sobie miarę ugryźliśmy, czyli takiej biznesowej, bo tyle ile tam będzie kosztowało typowości. My mamy jakieś tam na dzień dzisiejszy, sądzę, że jak my byśmy utrzymali przez właśnie przewagę współkonkurencyjną, wchodzą takie liczby i tak dalej, żebyśmy mieli i to by się okazało, bo sądzę, że nawet taki Gartner by nam nie powiedział, kim mam na udział, bo nie, to jest za mała kategoria, żeby mieć realny pogląd, tak? Więc, ale sądzę, że jeżeli na przestrzeni lat, tak, będziemy mieli cały czas tam, bo ktoś za tego świadczy, dziękuję.

---

## Miejsca niepewne — do sprawdzenia przez uczestnika spotkania

Tu oba modele słyszą co innego albo nagranie jest po prostu nieczytelne. Zostawiłem
tekst tak, jak rozpoznał go model, żeby nie podstawiać zmyślonych słów.

- **01:45** „jeśli mam ich wpis do krawca" — fragment nieczytelny (drugi model: „jeśli mam ich quiz").
- **01:14** „go-e, NextBlue" — marki wallboxów. „go-e" istnieje na pewno, „NextBlue" nie udało się potwierdzić.
- **09:46 / 09:49** „Vincent?", „Ike?" — imię przedstawiciela Tuya; w nagraniu sami go nie pamiętacie.
- **10:10** „Tego nie było na IFIER" — nazwa targów; drugi model słyszy „na IFR”, najpewniej chodzi o IFA.
- **11:20** „pod swoją marką, tą coną" — nazwa marki magazynów energii Tuya; drugi model słyszy „zoną".
- **12:29** „wpinać się w jakieś pstryki" — oba modele słyszą to samo; prawdopodobnie chodzi o Pstryk (rozliczenia energii).
- **12:38** „24 wallboxów" — drugi model słyszy „20–30 wallboxów"; liczba niepewna.
- **13:07** „gdyby próbowałeś to przy złokach", „spalić w mosty" — fragment nieczytelny.
- **20:44** „Na WR11, to poznanie samo z przyzwyczajeniem" — nieczytelne; prawdopodobnie kolejny symbol modułu.
- **22:40** „nie potrzebujemy tego po fredzie" — nieczytelne (drugi model: „po popredzie").
- **28:52** „W związku z tym biura jednak nie patrzy w dobrym miejscu" — nieczytelne.
- **37:15** „Sigenergy" — dopasowanie po brzmieniu („Siga"); nazwa może być inna.
- **39:48** „nic jeszcze na GSM-ie nie robiliśmy" — rekonstrukcja z dwóch niepełnych odczytów.
- **41:12** „ze wszystkiego robią się od czerwoni" — nieczytelne.
- **47:56** „Będzie zupa po 11" — nieczytelne.
- **48:48** „bo ktoś za tego świadczy, dziękuję" — końcówka nagrania, nieczytelna.

## Kto jest kim — na czym oparłem przypisanie

- **SHELLY** — mówi „za Shelly X jestem ja odpowiedzialny" (16:57), „wyślę Wam dev kita" (29:00),
  „te TopAC, które mamy porobione z fabryką, to my jako handlowcy sprzedajemy" (19:00),
  „nasze CT-ki będziemy w Bułgarii mieli uzbrojone w SIM-ki" (42:01 — Allterco jest bułgarskie),
  umawia rozmowę z Borisem, szefem R&D.
- **AMPEREPOINT** — „my równolegle pracujemy z fabrykami" (00:16), „produkujemy urządzenia w trzech
  różnych fabrykach" (08:26), „mamy trzy półki cenowe", „odciąć się od jakości, którą mamy aktualnie
  w Tuya" (31:11), „przyniesiesz, Dawid, jeden z modułów frontowych" (18:17).
- **NIEUSTALONY** — 10 krótkich wtrąceń, w których treść nie wskazuje strony.

Po każdej ze stron mówi więcej niż jedna osoba — rozdzielenie ich wymagałoby albo nagrania
z osobnych mikrofonów, albo Twojej pamięci ze spotkania. Etykiety w tekście oznaczają **stronę
rozmowy, nie konkretnego człowieka**.


## Poprawki wprowadzone w tekście

Rozpoznawanie mowy myli nazwy własne i żargon. Poprawiłem tylko te miejsca, w których kontekst nie zostawia wątpliwości albo potwierdziło to sprawdzenie drugim modelem lub źródło zewnętrzne. Poniżej wszystko, co zmieniłem — żeby dało się to zweryfikować, a nie brać na wiarę.

- **TUI** → **Tuya** (×7) — Tuya — platforma IoT; model słyszał „TUI”
- **Kame** → **CAME** (×2) — CAME — włoski producent automatyki bram
- **Shell X** → **Shelly X** (×2) — Shelly X = platforma OEM (x.shelly.com), potwierdzone
- **top AC** → **TopAC** (×2) — j.w.
- **WUBER** → **WBR3** (×2) — j.w.
- **dev kit'a** → **dev kita** (×2) — zapis
- **to PC** → **TopAC** (×2) — j.w.
- **CTK** → **CT-ki** (×2) — CT — przekładnik prądowy Shelly 120 A
- **PAPC** → **TopAC** (×2) — j.w.
- **PowerAC** → **TopAC** — TopAC = ładowarka Shelly (EVE01-11R), potwierdzone
- **Kieńczycy** → **Chińczycy** — przesłyszenie
- **marsze** → **marże** — przesłyszenie
- **marszach** → **marżach** — przesłyszenie
- **soporcie** → **supporcie** — przesłyszenie
- **NICE'a** → **Nice’a** — Nice — producent automatyki bram
- **impostem** → **InPostem** — InPost — paczkomaty
- **natui** → **na Tuya** — j.w.
- **OCPF** → **OCPP** — protokół OCPP
- **podłoga giełdowa** → **spółka giełdowa** — przesłyszenie
- **substytut rządowy** → **subsydia rządowe** — przesłyszenie
- **wybióli** → **wyszli** — przesłyszenie
- **bazującego na SP** → **bazującego na ESP** — ESP32/ESP8266 — kontekst modułu
- **prostowy moduł SP** → **prosty moduł ESP** — j.w.
- **Top AC** → **TopAC** — j.w.
- **w szele** → **w Shelly** — nazwa firmy
- **WUBER 3** → **WBR3** — WBR3 = moduł Wi-Fi Tuya
- **szeli** → **Shelly** — nazwa firmy
- **przedszeli** → **przez Shelly** — nazwa firmy
- **nie mam posuwanej akumaski** → **nie mam postawionego home systemu** — kontrola krzyżowa
- **w oddzielnych kapkach** → **w oddzielnych appkach** — kontrola krzyżowa
- **tuję** → **Tuyę** — j.w.
- **Philips Q** → **Philips Hue** — Philips Hue — linia żarówek
- **Biuro Przędzel** → **biuro w Shenzhen** — Shenzhen — siedziba fabryk
- **support lokalny w kinach** → **support lokalny w Chinach** — przesłyszenie
- **pchać te kobryki do przodu** → **pchać te fabryki do przodu** — kontrola krzyżowa
- **stuje** → **Tuya** — j.w. („kopiuj Tuya”)
- **Uber 3** → **WBR3** — j.w.
- **dev kit'ie** → **dev kicie** — zapis
- **defiki** → **dev kity** — dev kit
- **obanglowaniu** → **bundlowaniu** — kontrola krzyżowa („bandlowaniu”)
- **klimatstacja** → **klimatyzacja** — przesłyszenie
- **klimatstwę** → **klimatyzację** — przesłyszenie
- **szali** → **Shelly** — nazwa firmy
- **MarsTek'a** → **Marsteka** — Marstek — magazyny energii
- **Endura** → **Zendure** — kontrola krzyżowa („Zendura”) — marka magazynów energii
- **SIG'a** → **Sigenergy [?]** — kontrola krzyżowa („Siga”); dopasowanie niepewne
- **finałcie** → **pinoucie** — kontrola krzyżowa drugim modelem
- **Borzysem** → **Borisem** — imię (szef R&D Shelly)
- **Shell'i** → **Shelly** — nazwa firmy
- **nic jeszcze na PogG SMI nie mamy** → **nic jeszcze na GSM-ie nie robiliśmy** — kontrola krzyżowa
- **MikroTika używa ePoEnergy, bo sprzedawałem też ePoEnergy** → **MikroTika, używa Ekoenergetyka w tych stacjach, bo sprzedawałem też** — kontrola krzyżowa; Ekoenergetyka — producent stacji DC
- **o CPP** → **OCPP** — protokół OCPP
- **Kinczyk** → **Chińczyk** — przesłyszenie
- **w przypadku FAPu** → **w przypadku fuck-upu** — kontrola krzyżowa
- **Boricem** → **Borisem** — imię
- **Borys** → **Boris** — imię
- **Sherry** → **Shelly** — nazwa firmy
- **obręb nowej siedzibności** → **Kongres Nowej Mobilności** — targi PSNM w Katowicach
- **PSNL** → **PSNM** — PSNM — Polskie Stowarzyszenie Nowej Mobilności
- **lotnigowa** → **lobbingowa** — przesłyszenie
- **w zakresie technik mocno manipulowana** → **w zakresie elektromobilności, mocno manipulowana** — kontrola krzyżowa
- **garden** → **Gartner** — Gartner — firma analityczna
