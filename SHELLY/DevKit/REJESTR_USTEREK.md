# Q11 z modułem Shelly X: rejestr usterek

*AMPERE POINT · prowadzony od 29 września 2026 · oprac. Dawid Cekała*
FOOTER: AMPERE POINT — rejestr usterek · Q11 z modułem Shelly X

Wszystkie usterki i pułapki napotkane przy DevKicie (Q11 + Shelly X), także te już naprawione, żeby można było do nich wrócić. Każdy wpis mówi, co widać, skąd się bierze, jaki ma stan i gdzie jest opis. Numery się nie zmieniają; nowy wpis dostaje kolejny wolny numer (od S-37) i trafia do tabeli swojej grupy.

Stan: ✘ otwarte · ◐ obejście albo częściowo · ✔ naprawione.

## 1. Nasz skrypt w module {-}

| Nr | Objaw | Przyczyna | Stan | Dalej / opis |
| --- | --- | --- | --- | --- |
| S-01 | Rozjazd pola i sterownika: pole pokazuje wartość, której sterownik nie ma. 12:02:44 tryb „do limitu energii” (sterownik został przy „od razu”), 13:44:27 wyłączenie ładowania z aplikacji (sterownik odpowiedział 2 razy „wł.”) | Gdy odpowiedź sterownika równa się wartości zapamiętanej w module, moduł loguje „same” i nie powiadamia skryptu. Próba sprawdzania po zapisie (v4.1) cofała też dobre wartości | ✘ | Znane odrzucenia (tryb przy limicie 0, okno o równych godzinach) blokuje v4.3. Na resztę potrzebna próba: co widzi skrypt w `getDatapoint().v` po odrzuceniu. Testy B3c, B1 w dokumencie 01 |
| S-02 | Spóźniona odpowiedź sterownika wracała do niego jako polecenie: limit energii 3 → 2 kWh (12:03:07), włącznik „wł.” bez polecenia (12:03:37) | Zmiana z HA i wpisanie starej odpowiedzi przez skrypt docierały do skryptu po sobie; skrypt brał drugą za nowe polecenie | ✔ v4.3 | Zmiany ze źródłem „sys” pomijane. Atrapa, test 11 |
| S-03 | Seria kliknięć w HA dawała serię zapisów: 24 polecenia w 9 s, sterownik przestawał odpowiadać | Każda zmiana pola szła od razu na łącze | ✔ v4.3 | Wysyłana ostatnia wartość po 1 s ciszy. Próba 13:27: 7 → 9 → 7 dało 1 zapis |
| S-04 | Przy każdym starcie modułu jedna zmiana pola „z zewnątrz” z wartością właśnie zgłoszoną przez sterownik | Źródło zdarzenia przy starcie nie jest „sys” (przyczyna nieustalona, startu nie widać w logu) | ✔ v4.3.1 | Zmiana na wartość, którą sterownik ma, nie idzie. Sprawdzić źródło, gdy będzie log startu (S-31) |
| S-05 | Okno godzin „1600” poszło jako 4 znaki ASCII, sterownik zignorował | Moduł wysyła tekst do punktu raw dosłownie, choć odczyt podaje szesnastkowo | ✔ v4.1 | 2 bajty przez `String.fromCharCode` |
| S-06 | Kontrola po zapisie cofnęła tryb „od razu” na „harmonogram” | Po własnym zapisie wartość widoczna dla skryptu nie była odświeżana | ✔ v4.2 | Kontrolę usunięto; wraca w S-01 |
| S-07 | Czas sesji skakał (770 → 815 → 1066 min) | Liczony z zegara modułu, który zmienia się po synchronizacji | ✔ v4 | Liczony z tyknięć co 10 s |
| S-08 | Wartości ułamkowe z HA: okno 0,01 h, limit 6,5 A | HA nie pilnuje kroku pola | ✔ v4.3 | Skrypt zaokrągla i wpisuje z powrotem |

## 2. Moduł Shelly X i portal {-}

| Nr | Objaw | Przyczyna | Stan | Dalej / opis |
| --- | --- | --- | --- | --- |
| S-10 | Strona WWW modułu: kafelki faz „N/A A”, moc podpisana kW, choć jest w W | Szablon ekranu Shelly używa `displayValue` zamiast `value` | ✘ | Własny `web.svc.svelte` (panel) |
| S-11 | Strona WWW nie pokazuje 9 nowych pól | Szablon ekranu zna tylko 6 pól ładowarki | ✘ | Jak S-10 |
| S-12 | Akcje i warunki w manifeście: 2 i 3 zamiast 6 i 12 (kompilacje 3812–3815; 3811 miała 6/12) | Nieustalona; portal przy kompilacji bierze te z szablonu | ✘ | Sprawdzić przy B5 (webhooki) |
| S-13 | Moduł ponawia zapis po 0,3 s bez odpowiedzi („response to 07 timed out”). Ponowienia potrafią przestawić kolejność: 14:13:43–49 poszło 13, 12, 13, 13, 12 A; przez chwilę sterownik miał starsze 13 zamiast 12 | Stały czas oczekiwania w module, sterownik odpowiada wolniej (S-23); moduł ponawia stare polecenie po wysłaniu nowszego | ✘ | Dla Shelly: ponowienie nie powinno wyprzedzać nowszego zapisu tego samego punktu. U nas: odstępy między zapisami ≥ 3 s nie wystarczyły |
| S-14 | Zapis punktu, którego sterownik jeszcze nie zgłosił: „Setting unknown datapoint” | Moduł dodaje punkt dopiero po pierwszym meldunku | ◐ | Skrypt podpina punkt później i zapisuje komunikat |
| S-15 | Otwarcie kreatora w portalu zakłada blokadę edycji; druga karta przechodzi w tryb tylko do odczytu | Blokada z sygnałem co 20 s | ◐ | Nie otwierać kreatora, gdy Dawid edytuje; status `/products/3109/edit-lock/status` |
| S-16 | Portal przestawia wcięcia kilku linii skryptu | Edytor portalu | ◐ | Porównywać treść bez białych znaków |
| S-17 | „Development Wi-Fi” zapisuje hasło Wi-Fi jawnie w tokenie produktu | Tak działa portal | ◐ | Wgrywać samą usługę (Wi-Fi zostaje) |
| S-18 | Strona WWW i API bez hasła: każdy w sieci może sterować ładowarką | Hasło modułu wyłączone | ✘ | Test B11 |
| S-19 | Po restarcie bez internetu moduł nie ma czasu, a sterownik pyta o godzinę | Czas tylko z serwera w internecie | ✘ | Testy C; serwer czasu w sieci lokalnej |
| S-37 | Zmiana pola z harmonogramu modułu (i innych wywołań wewnątrz modułu) dociera do skryptu bez pola źródła; w logu `notifying for status: {"value":6}` (B4, 13:53:52) | Tak moduł zgłasza zmiany z wywołań lokalnych | ◐ | Skrypt uznaje brak źródła za zmianę z zewnątrz, więc harmonogram działa. Prawdopodobnie to samo przy starcie (S-04) |
| S-50 | Po każdym restarcie modułu, około 40 s po nim, przychodzą webhooki „ładuje” i „start ładowania”, choć ładowanie trwa bez przerwy (30.09 15:01, 15:04, 15:07) | Pole stanu po starcie ma wartość domyślną „wolna”; meldunek sterownika zmienia je na „ładuje”, co wygląda jak nowy start | ✘ | Skrypt: po starcie nie wpisywać wartości domyślnej, tylko zostawić puste pole do pierwszego meldunku, albo webhooki z warunkiem na poprzedni stan; integracje liczące sesje muszą to odfiltrować |
| S-39 | Moduł zgłasza sterownikowi stan sieci 4 („połączony z chmurą”), choć chmura jest wyłączona, także bez internetu (co 30 s, bez zmian). Ikona Wi-Fi na wyświetlaczu co kilkadziesiąt sekund znika i wraca (30.09, poziom C) | Moduł wysyła stan Wi-Fi według połączenia z routerem, nie z chmurą | ✘ | `tmcu.overwriteWifiState` w skrypcie; test C5 |
| S-40 | Przy komplecie połączeń (HA, monitor, strona, wychodzące + 6) siódme nie wchodzi, a moduł zamyka połączenie Home Assistant | Limit połączeń w module (B9) | ✘ | Liczyć połączenia w projekcie mostu OCPP; HA łączy się ponownie sam |
| S-41 | Kopia konfiguracji niezaszyfrowana: hasło Wi-Fi i token chmury jawnie; nie zawiera plików usługi | Tak działa `Sys.CreateBackup` (B10) | ◐ | Plik tylko w `DevKit\kopie_konfiguracji`; kopia nie odtworzy produktu na nowym module |
| S-42 | Kanał UDP (B12) steruje ładowarką bez hasła | Kanał bez uwierzytelnienia | ◐ | Wyłączony po teście; sprawdzić przy B11, czy hasło go obejmuje |
| S-44 | Wartości pól zapamiętywanych (włącznik, limit prądu) moduł zapisuje do `storage.json` wprost, bez pliku tymczasowego: około 1,9 s po zmianie, najwyżej raz na około 3 s. Po zaniku przepadają zmiany z ostatnich około 3 s (30.09: 423 i 424 przepadły, wróciło 422). Częsta zmiana limitu zużywa pamięć: co 10 s granica około 2,7 roku, ciągłe zmiany poniżej roku | Tak moduł zapisuje pola z flagą „persisted” | ✘ | Dokument 04 (P4–P6). Zanik w samym zapisie nie trafiony, plik nieuszkodzony. Dla produktu: limit sterowany automatycznie bez flagi zapamiętywania; sterownik i tak pamięta swój limit |
| S-45 | Po zaniku zasilania, dopóki moduł nie dostanie godziny, wykonuje harmonogram według zapamiętanego, nieaktualnego zegara (30.09: start z zegarem 29.09 13:26:55, zadania co 5 s odpalały „o 13:27:00, 13:27:35…”), choć raportuje godzinę jako nieznaną | Moduł bez baterii zegara startuje od zapamiętanej chwili i nie wstrzymuje harmonogramu | ✘ | Groźne na poziomie C: zadanie „22:00 zacznij ładować” odpali o złej porze. Serwer czasu w sieci lokalnej skraca okno do około 25 s; zgłosić do Shelly |

## 3. Sterownik Q11 {-}

| Nr | Objaw | Przyczyna | Stan | Dalej / opis |
| --- | --- | --- | --- | --- |
| S-20 | Po zapisie limitu energii sterownik przez kilka sekund powtarza meldunek limitu i trybu, około 10 par na sekundę (12:02:00–03 ≈ 45 par), i nie odpowiada modułowi (6 razy „Heartbeat timed out”, każde ustąpiło po 1–5 s) | Oprogramowanie sterownika | ◐ | Skrypt ogranicza zapisy (S-03). Pytanie do fabryki |
| S-21 | Tryb pracy zmienia się sam: limit energii > 0 → „do limitu energii”, okno → „harmonogram”, „od razu” zeruje limit; „do limitu energii” przy limicie 0 odrzucony | Tak działa sterownik (29.09) | ◐ | Skrypt nie wysyła trybu, który zostanie odrzucony. `DANE_DIAGNOSTYCZNE.md` |
| S-22 | Okno o równej godzinie startu i końca (0–0, 1–1) odrzucane | Sterownik | ◐ | Skrypt go nie wysyła; stan fabryczny 0–0 nie do przywrócenia z modułu |
| S-23 | Odpowiedź po 0,3–3 s i często najpierw ze starą wartością (limit 14 → zapis 9 → meldunki 14, 9) | Sterownik | ◐ | Obsłużone w v4.3 |
| S-24 | Sterownik nie przyjmuje wyłączenia ładowania: 29.09 13:44:27 (z aplikacji), 30.09 10:59:56 i 11:06:50 (przez API). Restart samego modułu pokazał, że sterownik dalej ma „wł.”. 29.09 o 12:03 takie samo wyłączenie przyjął. Sam ustawia włącznik: „wł.” po włączeniu zasilania, „wył.” po zakończeniu sesji | Nieustalona; może zależeć od trybu albo stanu sterownika | ✘ | Porównać warunki z 12:03 (tryb „do limitu energii”) z późniejszymi; pytanie do fabryki |
| S-25 | Mapa usterek (punkt 10) ma 2 bajty, definicja 17 kodów; bit 16 „przegrzanie” się nie mieści | Sterownik albo definicja | ✘ | Pytanie do fabryki |
| S-26 | Limit prądu w definicji Tuya 6–32 A, Q11 to 16 A | Definicja produktu | ◐ | Skrypt przyjmuje 6–16 A |
| S-46 | Po restarcie modułu łącze ze sterownikiem utknęło w stanie „Fetching Config” na ponad 3 min (30.09 12:24–12:27): sterownik odpowiadał na sygnał życia i pytał o godzinę, ale moduł nie dokończył powitania i nie ponawiał pytania; brak danych i sterowania. Pomógł kolejny restart. Zdarzyło się przy pierwszym restarcie modułu po zaniku zasilania | Warstwa łącza w module (Shelly) nie ponawia pytania o konfigurację | ✘ | Zgłosić do Shelly. U nas: w skrypcie strażnik — gdy przez 2 min po starcie brak meldunków sterownika, komunikat w stanie usługi i ewentualnie restart modułu |
| S-47 | Przy zaniku zasilania sterownik traci ustawienie jednej sesji na czas: okno godzin z trybem „harmonogram” (wraca „od razu”) oraz opóźnienie i czas trwania z menu (sprawdzone 2 razy 30.09); limit prądu pamięta. Klient, który ustawił opóźnienie na tańszą taryfę, po mrugnięciu prądu ładuje od razu | Sterownik nie zapisuje ustawień sesji | ✘ | Pytanie do fabryki. Propozycja (niesprawdzona): moduł zapamiętuje ustawienie sesji i odtwarza je po starcie. To nie jest harmonogram — harmonogram Tuya ustawia się w aplikacji |
| S-49 | Opóźnienie i czas trwania ustawiane w menu, gdy ładowarka jest w stanie C, pokazują się na ekranie z innymi wartościami niż wybrane (Dawid, 30.09). Występuje też na ładowarce z modułem Tuya | Sterownik (nie moduł) | ✘ | Powtarzalne niezależnie od ustawionych godzin; tak samo z Shelly i z WBR3, więc nie różnicuje modułów. Odłożone jako osobny, większy temat do fabryki (Dawid, 30.09) |
| S-48 | Opóźnienie i czas trwania ładowania ustawione w menu ładowarki (30.09 ok. 12:35) są dla modułu niewidoczne: sterownik nic nie wysłał, a przy odpytaniu podał okno 0–0 i tryb „od razu”. Widać tylko skutek: z testerem stan „czeka” mimo sygnału auta „chce ładować” (12:41) | Funkcja menu nie ma odpowiednika w zgłaszanych punktach; kandydat: punkt 33 `mode_set` (surowy, do 128 B), nigdy nie zgłoszony | ✘ | Z testerem: czy opóźnienie z menu działa i czy moduł widzi „czeka”. Pytanie do fabryki o punkt 33 |
| S-27 | Punkt 33 nigdy nie przyszedł; licznik (1) tylko w stanie „ładuje”, co 90 s. Wersję (23) „V1” sterownik zgłasza po włączeniu zasilania (30.09: 3 razy). Po włączeniu zasilania nie zgłasza okna godzin (19), także przy późniejszym restarcie samego modułu, więc pola okna zostają 0–0 | Sterownik | ◐ | Zestawienie DP; okno: sprawdzić, czy sterownik je kasuje przy zaniku (ustawić okno, zanik, odczyt z menu) |
| S-38 | Zapis trybu „od razu” (14:01:43) bez żadnej odpowiedzi, a sterownik go przyjął (odpytanie przy starcie o 14:04: tryb 0). O 12:02:38 ten sam zapis potwierdził | Sterownik nie zawsze potwierdza zapis | ✘ | Razem z S-01: brak potwierdzenia nie znaczy odmowy |

## 4. Aplikacja Shelly, Home Assistant, narzędzia {-}

| Nr | Objaw | Przyczyna | Stan | Dalej / opis |
| --- | --- | --- | --- | --- |
| S-30 | Aplikacja Shelly bez chmury „offline”; w sieci lokalnej tylko sprawdza moduł | Aplikacja steruje wyłącznie przez chmurę (próba 13:43–13:45: z chmurą działa od razu) | ✘ | Ograniczenie Shelly; bez chmury strona WWW i HA. Test B1 |
| S-31 | Startu modułu nie widać w logu | Monitor łączy się 20–45 s po starcie; log przez MQTT też za późno i zapełnia się własnymi wpisami | ◐ | Log UDP (odbiornik w kontenerze, port 8514) pokazuje start od 23. sekundy, czyli od połączenia z Wi-Fi; wcześniejszych sekund nie widać żadną drogą sieciową |
| S-43 | Zegar laptopa spóźnia się o 8,3 s (serwer czasu w kontenerze), więc czasy w logach po stronie laptopa (webhooki, WebSocket, zdarzenia) są o 8 s wcześniejsze niż w logu modułu | Zegar Windows | ◐ | Przy porównywaniu logów przesuwać o 8 s albo zsynchronizować zegar laptopa (decyzja Dawida) |
| S-32 | Aplikacja rysuje ogólny ekran ładowarki, nie ekran TopAC | Ekran zależy od typu produktu w aplikacji | ✘ | Do ustalenia z Shelly |
| S-33 | Oficjalna integracja HA pokazuje tylko fazy (19 encji) | Encje tylko dla kluczy z listy w kodzie; limit i włącznik tylko dla TopAC (EVE01) | ◐ | Łatka `DevKit\ha_integracja` (33 encje); docelowo zmiana w integracji |
| S-34 | Integracja HA wywraca się na polu wyboru bez napisów opcji | Błąd w kodzie integracji (`titles`) | ◐ | Naprawione w łatce; zgłosić do HA |
| S-35 | Łatana kopia integracji HA po aktualizacji HA może nie wstać | Kopia z wersji 2026.6.4 | ◐ | `ha_integracja\CZYTAJ.pdf` |
| S-36 | Polskie tłumaczenie aplikacji z błędami („Oskarżony”) | Aplikacja Shelly | ✘ | Analiza GAP |
