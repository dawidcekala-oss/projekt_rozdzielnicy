# SPRAWY W TOKU — AMPERE POINT (diagnostyka)

> **Do czego służy:** jedno miejsce ze stanem otwartych spraw — na czym stanęło, na co czekamy, gdzie są pliki. Aktualizować przy każdej zmianie stanu (wysłana wiadomość, odpowiedź klienta lub producenta, decyzja Dawida). Szczegóły zostają w pliku sprawy; tu tylko stan. Sprawa zamknięta → do sekcji „Zamknięte” z datą i wynikiem.
>
> Rejestr prowadzony od 2026‑09‑28. Starsze sprawy (np. Bogusz, U‑003, protokół 40940192) mają stan nieustalony — dopisywać, gdy wrócą.

---

## Karol — wallbox z modułem DLB‑A1 (od 2026‑09‑26)

**Stan (2026‑09‑28):** klient czeka na wymianę — ma niefunkcjonalne DLB. Raport o dwóch wadach wysłany producentowi 26–27.09; producent robi przegląd firmware. Opóźnienie wznowienia po pauzie: decyzja Dawida 5 min (28.09) — do przekazania producentowi (w `KORESPONDENCJA.md` jeszcze bez wpisu o wysłaniu).
**Sprawdzenie 2026‑09‑29, 06:41:** w logu Tuya nie ma żadnej aktualizacji oprogramowania wallboxa (filtr OTA, okno 23–29.09). Urządzenie jest offline od 26.09, 14:26 — do tego czasu nie było żadnego zdarzenia; aktualizacja z chmury nie dotrze, dopóki wallbox nie wróci do sieci. Stan „Offline” potwierdzony w liście urządzeń produktu o ok. 09:10 i ponownie o 10:42.
**Czekamy na:** poprawione oprogramowanie od producenta. **Ruch po naszej stronie:** przekazać producentowi 5 min.
**Otwarte:** wpis do katalogu usterek (`..\AMPERE_POINT_porownanie_ladowarek_v2.html`, ostatni U‑029) — do decyzji Dawida.
**Pliki:** `istotne_casey\Karol\`, `LOGI_Tuya_wallbox_DLB_bfe26d.md`; rozwój DLB: `..\DLB_R&D\zasoby_informacji\DLB_RD_baza_wiedzy.md`, korespondencja z producentem: `..\DLB_R&D\info_producenta\KORESPONDENCJA.md`.

## Marcin Krawiec — integracja z Home Assistant 2025.3 (od 2026‑09‑24)

**Stan (2026‑10‑05):** poprawka wydana 01.10 jako **v0.5.40** (PR #42 scalony); klient zaktualizował — panel działa, danych brak (dodatek bez źródła). Oficjalna Tuya daje encje ładowarek EV dopiero od HA 2025.8, więc u klienta źródłem musi być tuya local 2026.2.0 + profil q11_pro — ścieżka sprawdzona testem na jego wersjach (bez prawdziwej ładowarki).
**Czekamy na:** instrukcja wysłana 05.10 (ticket zamknięty 13:12); klient o 15:37 pobierał **LocalTuya** zamiast **Tuya Local** (make-all, poza domyślnym katalogiem HACS) — sprostowanie do wysłania (szkic w pliku sprawy), potem potwierdzenie od klienta. **05.10 22:09:** klient zainstalował właściwy Tuya Local, ale dodanie ładowarki kończy się błędem połączenia (puste pole IP po wyszukiwaniu, po wpisaniu IP — „Nie można podłączyć się do urządzenia…”); **06.10:** przyczyna z kodu tuya local — po nieudanym wyszukiwaniu w sieci formularz ma pusty IP i domyślną wersję protokołu 3.3, a ładowarka mówi 3.5; szkic odpowiedzi (wersja 4: adres z panelu routera albo z `tinytuya scan`, wersja protokołu 3.5, zamknąć aplikację Tuya) w pliku sprawy, do wysłania.
**Pliki:** `istotne_casey\Marcin_Krawiec\przebieg_sprawy.md` (+ `korespondencja\`, `materialy_od_klienta\`, `testy\`).

## Dawid Kaczmarek — kosztorys naprawy dla ubezpieczyciela, Q22 Pro (od 2026‑10‑05)

**Stan (2026‑10‑05):** klient (zakup 06.09.2026) prosi o oficjalny kosztorys na papierze firmowym: przewód z wtyczką Typ 2 najechany kołem samochodu, chce odpłatnej wymiany z zachowaniem gwarancji na resztę. Dawid: część 400 zł, robocizna i testy 150 zł, razem 550 zł; naprawa nie wpływa na gwarancję reszty ładowarki. Kosztorys (PDF) i szkic maila gotowe.
**Czekamy na:** wysłanie przez Dawida; do potwierdzenia: brutto, koszt wysyłki zwrotnej, czy na kosztorysie ma być NIP i numer dokumentu.
**Pliki:** `casey\Dawid_Kaczmarek\` (`kosztorys.pdf`, `kosztorys.json`, `generuj_kosztorys.py`, `przebieg_sprawy.md`).

## Adam Gumkowski — Q11 nie rozpoczyna ładowania BYD Atto 2 (od 2026‑10‑05)

**Stan (2026‑10‑07):** auto (BYD Atto 2 Boost 2025) nie blokuje wtyku i nie zaczyna ładować; z ładowarką fabryczną ładuje; wcześniej z tą Q11 działało. U nas ładuje normalnie (PP–PE w porządku). **Decyzja Dawida: ładowarkę odsyłamy**, wsparcie trwa — mail (wersja 6): czy problem pojawił się nagle czy narastał, co zmieniło się w aucie (aktualizacja, ustawienia ładowania); przy powtórce — nagranie/zdjęcia ładowarki i auta. Wniosek Dawida: auto nie załącza rezystorów CP → awaria przed pierwszą zmianą stanu; przed wysyłką obejrzeć styki wtyku.
**Czekamy na:** wysłanie maila i ładowarki; odpowiedź klienta; oględziny wtyku przed wysyłką.
**Pliki:** `istotne_casey\Adam_Gumkowski\przebieg_sprawy.md`.

## Daniel Romanek — przycisk klapki Tesli „nie działa”, Q11 PRO (od 2026‑09‑30)

**Stan (2026‑10‑07):** u nas ładowarka klienta otwiera klapkę naszej Tesli prawidłowo. Odsyłamy bez naprawy; szkic maila v3 gotowy: przycisk bez aktywacji + możliwe przyczyny po stronie auta z instrukcji Tesli (tryb P, naciśnij i puść, wybudzenie auta) + w razie braku reakcji serwis Tesli.
**Czekamy na:** wysłanie maila i urządzenia przez Dawida.
**Pliki:** `casey\Daniel_Romanek\przebieg_sprawy.md`.

## Gizinek — czerwona dioda po podłączeniu do auta, także po aktualizacji (od przed 06.10; Allegro)

**Stan (2026‑10‑07):** u nas bez błędu, zaktualizowane i odesłane 06.10; klient 07.10: dalej czerwona dioda po podłączeniu do auta. Propozycja jak u A. Augusta (Q37 z dopłatą 400 zł / zwrot); szkic gotowy. **Uwaga:** w Allegro reklamacja oznaczona jako uznana z rozwiązaniem „wymiana na nowy towar”.
**Czekamy na:** decyzję Dawida (zgodność z Allegro), wysłanie maila, decyzję klienta.
**Pliki:** `casey\Gizinek\przebieg_sprawy.md`.

---

## Zamknięte

### Artur August — B35 i BMW klienta, dwa egzemplarze
**Zamknięta 2026‑10‑07** („jego temat zamknięty” — Dawid). Klient nie zgodził się na wymianę na Q37 z dopłatą; najpewniej zwrot pieniędzy za …504. Wniosek do bazy: drugi egzemplarz (…465) w tym samym BMW startuje z harmonogramu — różnica między egzemplarzami (podejrzenie: wersja oprogramowania). Pliki: `casey\Artur_August\przebieg_sprawy.md`.

### Robert Gloch — „High Voltage Reminder”, nie ładuje
**Zamknięta 2026‑10‑06.** Ładowarka sprawdzona na gnieździe zwykłym 230 V, siłowym i na samochodzie — błąd nie wystąpił, usterki nie stwierdzono; wraca do klienta bez naprawy. Która wersja maila poszła do klienta — nieustalone. Pliki: `casey\Robert_Gloch\przebieg_sprawy.md`.

### Łukasz Reszka — przejściówka z gniazda 4‑pinowego (PEN) z mostkiem N–PE
**Zamknięta 2026‑10‑01** („tamto załatwione” — relacja Dawida). Odpowiedź nastawiona na uniknięcie odpowiedzialności: norma PN‑HD 60364‑7‑722 zakazuje PEN w obwodzie punktu ładowania, „na wyłączną odpowiedzialność użytkownika”. Czy wysłano dokładnie szkic — nieustalone. Pliki: `casey\Lukasz_Reszka\przebieg_sprawy.md`.
