# Marcin Krawiec — integracja ładowarki z Home Assistant 2025.3

**Kanał:** ticket przez support@amperepoint.pl · **Od:** 2026‑09‑24 · **Stan:** otwarta — v0.5.40 wydana i zainstalowana u klienta (panel działa); brak źródła danych — instrukcja tuya local do wysłania (patrz „Stan i następny krok”)
**Materiały:** `korespondencja\` — zrzuty wiadomości 01–05; `materialy_od_klienta\` — dwa pliki logu HA i diagnostyka wpisu (29.09).

`[F]` fakt (korespondencja, kod, log) · `[Z]` założenie albo wniosek do potwierdzenia

---

## Stan i następny krok (2026‑10‑05)

**Poprawka wydana:** PR #42 scalony 01.10 ok. 13:00, autor repo dodał jedną poprawkę (`1986818`) i wydał **v0.5.40**. Klient 05.10 zaktualizował — panel działa, danych brak, pyta, jak skonfigurować.

**Dlaczego brak danych** `[F]`: dodatek nie ma źródła odczytu. Oficjalna integracja Tuya tworzy encje dla ładowarek EV (kategoria `qccdz`, tylko przełącznik) dopiero od **HA 2025.8.0** — na 2025.3 nie ma żadnej encji, więc droga „Tuya Cloud”, którą repo zaleca dla serii Q od 0.5.38, u klienta nie zadziała. Zostaje tuya local 2026.2.0 z profilem `amperepoint_q11_pro_evcharger` (zgodnie z mailem z 01.10).

**Test na wersjach klienta** (HA 2025.3.3, dodatek 0.5.40, tuya local 2026.2.0, profil q11_pro; ładowarka podstawiona zapisem `LOCAL DPS` Q11 PRO; skrypt `testy\test_ha2025_3_tuya_local_q11pro.py`) `[F]`:
- tuya local tworzy 22 encje; dodatek rozpoznaje ładowarkę (model q_series, źródło tuya_local, 25 przypisanych encji);
- z pustym wpisem klienta: po starcie HA dodatek **sam tworzy drugi wpis** z danymi (status „Gotowy”, 8 A, 25 °C), pusty zostaje bez danych;
- bez pustego wpisu: „Dodaj integrację → AmperePoint → Skonfiguruj wykrytą ładowarkę” → wybór ładowarki → wpis z danymi.
Niesprawdzone: prawdziwa ładowarka (sieć, klucz lokalny).

**Dalej:** mail do klienta z krokami (szkic niżej) — do wysłania przez Dawida.

## Przebieg

| Data | Kto | Co |
|---|---|---|
| przed 24.09 | klient | Komentarz: chce zintegrować Tuya z HA; po dodaniu repo do HACS „nie pobiera się po restarcie”; ma HA 2025.3, którego świeże wersje tuya extend nie wspierają; pyta o starszą wersję. `[F — zrzut 01]` |
| 24.09 14:34 | (HA klienta) | Start HA (czasy z logu klienta, strefa Europe/Warsaw). `[F — log]` |
| 24.09 14:40:44 | (HA klienta) | **Pierwszy błąd:** `Error setting up entry AmperePoint for tuyaextend_amperepoint` → `dashboard.py`, linia 266, `frontend.async_register_built_in_panel(...)` → `TypeError: ... unexpected keyword argument 'show_in_sidebar'`. `[F — log 11‑09‑06]` |
| 24.09 14:41:07 | (HA klienta) | Błędy wtórne `has already been setup!` dla 6 platform. `[F — log]` Dodatek był więc zainstalowany przed wiadomością Dawida z 15:29 (albo czasy w tickecie są przesunięte) — nieustalone. |
| 24.09 15:29 | Dawid | Czy próbował naszego dodatku — link do `github.com/amperepoint/tuyaextend-amperepoint`. Ticket → „Oczekujący”. `[F — zrzut 02]` |
| 24.09 15:40 | klient | Dodatek pobrany, ale brak danych w encjach; dodanie lokalne po IP → „połączenie odpowiada, ale tego układu DP jeszcze nie obsługujemy”. `[F — zrzut 02]` |
| 25.09 12:00 | Dawid | Mail: zalecenie aktualizacji HA (tuya local wymaga 2026.8); profil `amperepoint_q_series_local.yaml`; alternatywnie linia `LOCAL DPS`. `[F — zrzut 03]` **Błędy — patrz niżej.** |
| 28.09 08:36 | klient | „W logach niewiele jest” + zrzut błędu z 24.09 14:41. `[F — zrzut 04]` |
| 28.09 14:42 | support (Dawid) | Wysłany mail: prośba o pełny log (Ustawienia → System → Logi, „Pobierz logi”) + sprostowanie nazwy profilu (`amperepoint_q_series_evcharger.yaml`) i źródła komunikatu (tryb lokalny dodatku, tylko PRIME). `[F — cytat w zrzucie 05]` |
| 29.09 13:09–13:17 | klient | Pobrał log (zawiera okres 24.09 14:34 – 29.09 12:59), potem zrestartował HA i pobrał drugi log (od 13:17) — ten sam `TypeError` o 13:17:22, czyli błąd powtarzalny. Dołączył diagnostykę wpisu. `[F]` |
| 29.09 13:18 | klient | Mail z trzema załącznikami, bez treści. `[F — zrzut 05]` |
| 01.10 | analiza | Przyczyna ustalona; warianty do decyzji. |
| 01.10 | Dawid | „Zrób to, co pomoże klientowi” → poprawka w forku, testy (wyżej). |
| 01.10 | Dawid → GitHub | PR #42 do repo bazowego (otwarty przez wbudowaną przeglądarkę na koncie Dawida). |
| 01.10 | GitHub CI | PR #42: wszystkie 5 zadań zielone — testy jednostkowe, energia na 2024.6.0 i 2026.7.2, **nowy test pełnego uruchomienia na 2025.2.0 i 2026.7.2**. `[F]` |
| 01.10 ok. 13:00 | autor repo | PR #42 scalony; dodatkowa poprawka `1986818` „Fix dashboard recovery after panel registration fails”; wydanie **v0.5.40**. `[F — GitHub]` |
| 01.10 13:04 | support (Dawid) | Wysłany mail z 01.10 (przyczyna po naszej stronie, aktualizacja HA niepotrzebna, tuya local 2026.2.0 + profil q11_pro). `[F — cytat w zrzucie 06]` |
| 05.10 12:46 | klient | „Pobrałem najnowszą aktualizację, ale dalej nie widzę danych, poza nowym dashboardem. Jak powinienem to skonfigurować?” `[F — zrzut 06]` |
| 05.10 | analiza | Brak źródła danych; test ścieżki tuya local na wersjach klienta; szkic instrukcji. |
| 05.10 13:12 | Dawid | Ticket → „Zamknięty” (instrukcja z 05.10 wysłana). `[F — zrzut 07]` |
| 05.10 15:37 | klient | Zrzut okna pobierania HACS: **„Local Tuya”**, wersja v5.2.5, katalog `/config/custom_components/localtuya`; „Nie ma takiej wersji localTuya”. Pomylił dodatki: LocalTuya (rospogrigio) zamiast Tuya Local (make-all). `[F — zrzut 07]` |
| 05.10 | analiza | Tuya Local (make-all) nie jest w domyślnym katalogu HACS — wyszukiwarka podsuwa LocalTuya. Szkic sprostowania. |
| 05.10 22:09 | klient | Zainstalował Tuya Local i przeszedł logowanie, ale **aplikacją Tuya** (ładowarki nie ma w Smart Life). Po kodzie i QR wybrał ładowarkę (tę samą co w aplikacji Tuya); po chwili ekran konfiguracji z **pustym polem adresu IP**. Wpisanie IP nie pomaga — błąd tuya local `connection`: „Nie można podłączyć się do urządzenia z tymi danymi. To może być tymczasowy problem lub dane mogą być niewłaściwe.” `[F — zrzut 08]` |
| 06.10 | analiza | Przyczyna z kodu tuya local 2026.2.0: wyszukiwanie w sieci (`tinytuya.find_device`, rozgłoszenia UDP) nie znalazło ładowarki → puste pole IP **i domyślna „Wersja protokołu” = 3.3** (chmura nie podaje wersji — `cloud.py`: `"version": None`; wersję ustawia tylko udane wyszukiwanie). Ładowarka mówi 3.5 → test połączenia z 3.3 nie przechodzi → błąd `connection`, także po wpisaniu poprawnego IP. Nasz działający wpis tuya_local (Q37 OTA) ma 3.5. Szkic odpowiedzi niżej. (Workflow wieloagentowy przerwany na polecenie Dawida — analiza zrobiona bezpośrednio.) `[F — kod]` |

## Ustalenia

- **Przyczyna:** `dashboard.py` (0.5.39) wywołuje `frontend.async_register_built_in_panel(..., show_in_sidebar=True, ...)`. Parametr `show_in_sidebar` istnieje w HA od **2026.3.0** (sprawdzone w źródłach `home-assistant/core`: brak w 2024.6–2026.2.0, obecny od 2026.3.0). Na starszym HA uruchomienie wpisu przerywa się po utworzeniu encji, więc dalej występuje błąd wtórny `has already been setup!`. Mechanizm opisany 28.09 — **potwierdzony**. `[F]`
- **System klienta** (diagnostyka wpisu): HA **2025.3.3**, instalacja **Container**, arch **armv7l** (32 bity), Python 3.13.2, jądro `5.10.103-v7l+`, strefa Europe/Warsaw. `[F]`
- **32 bity:** HA zakończył wsparcie 32‑bitowych architektur (armv7, armhf, i386) z wydaniem 2025.12. W rejestrze obrazów `ghcr.io/home-assistant/armv7-homeassistant` istnieje 2025.11.3, a 2025.12.0 już nie. Najwyższe możliwe u klienta: **2025.11.x** — za mało i dla dodatku 0.5.39 (2026.3), i dla bieżącego tuya local (2026.8). `[F]`
- **Tuya local 2026.2.0** deklaruje minimum HA 2025.1 → instalowalne u klienta. *Korekta 01.10: sprawdzone na HA 2025.3.3 — ładuje się, profil `q11_pro` pasuje w 100% (szczegóły wyżej); bez prawdziwej ładowarki.* `[F]`
- **Wpis dodatku:** `data.model = q11`, `options.model = q_series`; `source_type = entity_mapping`, brak jakiegokolwiek przypisania encji źródłowych (`raw_dp_count = 0`, „Brak danych”). Ładowarka: **seria Q (Q11)** `[F — wybór klienta w konfiguracji]`. Nawet po poprawce dodatek potrzebuje źródła danych — tuya local z profilem `amperepoint_q11_pro_evcharger`.
- Tryb lokalny dodatku (dodawanie po IP) obsługuje tylko PRIME — dla Q11 zawsze `local_unsupported`. `[F — kod]`

Ogólne wnioski: `..\..\DANE_DIAGNOSTYCZNE.md`, sekcja Tuya → Integracja z Home Assistant.

## Błędy w korespondencji

Z maila z 25.09 (dwa pierwsze sprostowane 28.09):
1. Nazwa profilu z forka (`amperepoint_q_series_local.yaml`) zamiast `amperepoint_q_series_evcharger.yaml`.
2. Komunikat o nieobsługiwanym układzie DP przypisany tuya local — pochodzi z naszego trybu lokalnego.
3. Prośba o linię `LOCAL DPS` — zapisuje ją tuya local, którego klient nie ma.
4. **Zalecenie aktualizacji HA do 2026.8 bez sprawdzenia, czy jest możliwa** — u klienta (32 bity) nie jest. **Niesprostowane** (sprostowanie w szkicu z 01.10).
5. Mail z 28.09: profil `amperepoint_q_series_evcharger.yaml` (75% dopasowania) zamiast `amperepoint_q11_pro_evcharger.yaml` (100%) — wskazany bez sprawdzenia dopasowania. Sprostowanie w szkicu z 01.10.

Wpisane do `..\..\ZASADY_maile_do_klientow.md`, pkt 9.

## Szkic odpowiedzi (2026‑10‑01)

> Dzień dobry Panie Marcinie,
>
> Dziękuję za logi, pozwoliły ustalić przyczynę. Błąd leży po naszej stronie: obecna wersja dodatku nie jest zgodna z Pana wersją Home Assistanta i przerywa uruchamianie przy tworzeniu panelu. Przygotowaliśmy poprawkę i sprawdziliśmy ją na tej samej wersji Home Assistanta, której Pan używa. Dam znać, gdy będzie dostępna do aktualizacji w HACS.
>
> Aktualizacja Home Assistanta, którą wcześniej zalecałem, nie będzie potrzebna. Pana instalacja działa w wersji 32-bitowej, dla której ostatnim wydaniem Home Assistanta jest 2025.11, więc wersja, o której pisałem, i tak nie byłaby dostępna.
>
> Już teraz można przygotować odczyt danych z ładowarki przez tuya local. Na Pana wersji Home Assistanta działa tuya local 2026.2.0, dlatego w HACS przy pobieraniu trzeba wybrać właśnie tę wersję, bo nowsze wymagają nowszego Home Assistanta. Dla Q11 właściwy jest profil amperepoint_q11_pro_evcharger.yaml z katalogu amperepoint/profiles/tuya_local/ naszego repozytorium, a nie podany poprzednio. Plik należy skopiować do config/custom_components/tuya_local/devices/ i zrestartować Home Assistanta. Przy dodawaniu ładowarki w tuya local, w kroku wyboru typu urządzenia, trzeba wskazać amperepoint_q11_pro_evcharger, bo domyślnie może zostać zaznaczony inny profil. Gdy poprawiona wersja dodatku będzie dostępna, napiszę, jak połączyć go z ładowarką dodaną w tuya local.
>
> Pozdrawiam,
> Dawid Cekała
> Ampere Point

## Szkic odpowiedzi (2026‑10‑05)

> Dzień dobry Panie Marcinie,
>
> Dziękuję za informację. Panel działa, więc dodatek uruchamia się już poprawnie. Danych brakuje, ponieważ dodatek nie ma jeszcze z czego ich odczytywać. Na Pana wersji Home Assistanta źródłem musi być tuya local, bo oficjalna integracja Tuya w tej wersji nie udostępnia ładowarek EV. Konfiguracja wygląda następująco:
>
> 1. W HACS należy pobrać Tuya Local w wersji 2026.2.0, ponieważ nowsze wymagają nowszego Home Assistanta.
> 2. Plik amperepoint_q11_pro_evcharger.yaml z katalogu amperepoint/profiles/tuya_local/ naszego repozytorium trzeba skopiować do config/custom_components/tuya_local/devices/ i uruchomić Home Assistanta ponownie.
> 3. W Ustawienia → Urządzenia oraz usługi → Dodaj integrację należy wybrać Tuya Local. Najprościej skorzystać z logowania przez aplikację Smart Life: Tuya Local poprosi o kod użytkownika z aplikacji i zeskanowanie kodu QR, a potem pozwoli wybrać ładowarkę z listy. Na czas wyszukiwania adresu IP ładowarki aplikację Smart Life w telefonie warto zamknąć. W kroku „Wybierz typ urządzenia” trzeba wskazać amperepoint_q11_pro_evcharger.
> 4. W Ustawienia → Urządzenia oraz usługi → AmperePoint należy usunąć obecny wpis „AmperePoint”, który nie jest połączony z żadną ładowarką, a następnie przez Dodaj integrację → AmperePoint wybrać „Skonfiguruj wykrytą ładowarkę” i wskazać ładowarkę dodaną w tuya local. Jeśli po ponownym uruchomieniu Home Assistanta ładowarka pojawi się w AmperePoint sama, wystarczy usunąć pusty wpis.
>
> Po tych krokach panel pokaże dane z ładowarki.
>
> Pozdrawiam,
> Dawid Cekała
> Ampere Point

## Szkic odpowiedzi — pomylony dodatek (2026‑10‑05, 15:37)

> Dzień dobry Panie Marcinie,
>
> Dziękuję za zrzut. Widoczny na nim LocalTuya to inny dodatek o podobnej nazwie i nie jest potrzebny. Chodzi o Tuya Local autorstwa make-all, którego nie ma w domyślnym katalogu HACS. Trzeba go dodać tak samo jak nasz dodatek: w HACS, w repozytoriach niestandardowych, adres https://github.com/make-all/tuya-local z typem Integracja. W oknie pobierania należy skorzystać z opcji wyboru innej wersji i wskazać 2026.2.0. Po pobraniu dodatek znajdzie się w /config/custom_components/tuya_local, czyli w katalogu, do którego trafia nasz plik profilu. Dalsze kroki pozostają bez zmian.
>
> Pozdrawiam,
> Dawid Cekała
> Ampere Point

## Szkic odpowiedzi — błąd połączenia w Tuya Local (2026‑10‑06, wersja 4)

*Wersja 3 + na prośbę Dawida przywrócona droga przez panel routera jako pierwszy z dwóch sposobów (obok `tinytuya scan`).*

*Pytanie Dawida (06.10): czy klient w ogóle używa Dockera? Z diagnostyki (29.09): `installation_type` „Home Assistant Container”, `docker: true`, `hassio: false` → oficjalny obraz HA w kontenerze, na Raspberry Pi (`armv7l`, jądro `5.10.103-v7l+`). Runtime najpewniej Docker, ale pole `docker` jest prawdziwe także dla Podmana — wtedy `podman exec` zamiast `docker exec`. Nazwy kontenera i trybu sieci nie znamy.* `[F — diagnostyka + kod HA; Z — Docker]`

*Wersja 2 odsyłała tylko do listy urządzeń w routerze. Uwaga Dawida: klient może tego nie ogarnąć → polecenie `tinytuya scan` (biblioteka jest już w kontenerze HA, bo wymaga jej nasz dodatek i tuya local), zapasowo na zwykłym komputerze. Usunięte zalecenie stałego adresu w routerze — sprzeczne z założeniem, że klient nie obsługuje routera.*

> Dzień dobry Panie Marcinie,
>
> Dziękuję za opis. Logowanie przez aplikację Tuya jest w porządku. Puste pole adresu IP oznacza, że Tuya Local nie znalazł ładowarki w sieci samodzielnie, a wtedy w polu „Wersja protokołu” zostawia wartość 3.3. Ładowarka używa wersji 3.5 i z 3.3 połączenie się nie uda.
>
> Adresu IP nie wybiera się samodzielnie — ładowarka ma już adres nadany przez router i trzeba go odnaleźć. Można to zrobić na dwa sposoby.
>
> Pierwszy to panel routera: na liście urządzeń podłączonych do sieci ładowarkę najłatwiej rozpoznać, porównując tę listę przy włączonej i wyłączonej ładowarce.
>
> Drugi to polecenie w terminalu na komputerze, na którym działa Home Assistant:
>
> docker exec -it -w /tmp homeassistant python3 -m tinytuya scan
>
> Po około 20 sekundach pojawi się lista urządzeń Tuya w sieci. Ładowarka to pozycja, której Device ID jest takie samo jak w polu Device ID w oknie Tuya Local; w tym samym wierszu jest jej adres (Address) i wersja protokołu (Version). Jeśli kontener Home Assistanta ma inną nazwę niż homeassistant, pokaże ją polecenie docker ps. Gdyby skaner nie znalazł żadnego urządzenia, to samo można uruchomić na dowolnym komputerze w tej samej sieci z zainstalowanym Pythonem: najpierw python -m pip install tinytuya, potem python -m tinytuya scan, a jeśli system zapyta o dostęp przez zaporę — zezwolić.
>
> Adres widoczny w aplikacji Tuya to adres internetowy i tutaj się nie nada.
>
> Następnie w oknie Tuya Local proszę wpisać znaleziony adres, zmienić „Wersja protokołu” na 3.5, a pozostałe pola zostawić bez zmian. Na czas łączenia warto całkowicie zamknąć aplikację Tuya w telefonie, bo potrafi blokować połączenie lokalne. Dalsze kroki, w tym wybór typu amperepoint_q11_pro_evcharger, pozostają takie jak w poprzedniej wiadomości.
>
> Pozdrawiam,
> Dawid Cekała
> Ampere Point

## Otwarte

- ~~Scalenie PR #42 i wydanie nowej wersji~~ — wydane 01.10 jako v0.5.40.
- ~~Wysłanie instrukcji tuya local~~ — wysłana 05.10; klient zainstalował LocalTuya zamiast Tuya Local → sprostowanie (szkic 15:37) do wysłania; potem potwierdzenie, że dane są widoczne.
- Wysłanie maila do klienta (szkic z 01.10) — sprostowuje punkt 4 i profil.
- Czy klient ma skonfigurowaną oficjalną integrację Tuya — z diagnostyki nie wynika.
