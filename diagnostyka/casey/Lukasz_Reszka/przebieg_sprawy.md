# Łukasz Reszka — przejściówka z gniazda 4‑pinowego (PEN) na 5‑pinowe z mostkiem N–PE

**Kanał:** ticket (adres klienta `lukaszreszka…`; nazwisko odczytane z adresu e‑mail, niepotwierdzone) · **Od:** przed 2026‑09‑25 · **Stan:** zamknięta 2026‑10‑01 („tamto załatwione” — relacja Dawida; czy wysłano dokładnie szkic poniżej — nieustalone)
**Materiały:** `korespondencja\01_…png` — odpowiedź Miłosza i pytanie klienta.

`[F]` fakt · `[Z]` założenie albo wniosek

---

## Stan i następny krok (2026‑09‑29)

Szkic odpowiedzi (niżej) przygotowany pod kątem **uniknięcia odpowiedzialności firmy** — polecenie Dawida z 29.09. *Aktualizacja 2026‑10‑01: sprawa załatwiona (relacja Dawida) — zamknięta. 2026‑10‑05: przeniesiona z `istotne_casey` do `casey` (pytanie o instalację, nieistotne diagnostycznie — decyzja Dawida).*

## Przebieg

| Data | Kto | Co |
|---|---|---|
| przed 25.09 | klient → Miłosz Księżak | Pytanie o podłączenie ładowarki (Q PRO) do starego gniazda siłowego 4‑pinowego. `[Z — treść pierwszej wiadomości nieznana, wynika z odpowiedzi]` |
| przed 25.09 | Miłosz Księżak | Gniazdo powinno być 5‑pinowe; ładowarki i producenci aut wymagają prawidłowego uziemienia; „nie rekomendujemy” przejściówek; zalecenie: modernizacja instalacji i gniazdo 5‑pinowe CEE przez elektryka; po wykonaniu oferta na Q PRO z przewodem. `[F — zrzut 01]` |
| 25.09 14:52 | klient | „Wiem o tym”, ale znalazł informację, że można zrobić przejściówkę ze zmostkowanym N i PE i „ponoć powinno działać” — link do filmu na YouTube. „Czy się mylę?” `[F — zrzut 01]` |
| 29.09 | analiza | Szkic odpowiedzi; sprawdzona norma i instrukcja. |

## Ustalenia

- Stare gniazdo 4‑pinowe = 3 fazy + PEN (instalacja TN‑C). Przejściówka z mostkiem N–PE przenosi rozdział PEN do wtyczki. `[Z — z opisu Dawida i klienta]`
- **Norma:** IEC 60364‑7‑722:2018, pkt 722.312.2.1 (PN‑HD 60364‑7‑722) — w układzie TN obwód zasilający punkt ładowania nie może zawierać przewodu PEN. `[F]`
- **Zagrożenie:** przerwa w PEN → napięcie sieci na obudowie ładowarki i karoserii; wyłącznik różnicowoprądowy w ładowarce tego nie wykryje. Wywód: `..\..\DANE_DIAGNOSTYCZNE.md`, sekcja Instalacja zasilająca.
- **Instrukcja serii Q** (wersja robocza `QSeries_Ampere_Point_manual_EN_CONTENT_REVIEW.docx`): gniazdo prawidłowo uziemione, instalacja z poprawnie podłączonymi PE, N i fazą, obwód z RCD typu A, zakaz przedłużaczy. `[F — wersja robocza; zgodność z wysyłaną niesprawdzona]`
- Filmu z linku nie oglądaliśmy — w odpowiedzi nie komentujemy go.
- Odpowiedź Miłosza użyła sformułowania „nie rekomendujemy” — za słabego z punktu widzenia odpowiedzialności. Nowy szkic: „nie możemy zalecić ani zaakceptować”, podstawa w normie i instrukcji, ostrzeżenie o konkretnym zagrożeniu, „na wyłączną odpowiedzialność użytkownika”. Zasady: `..\..\ZASADY_maile_do_klientow.md`, pkt 10.

## Szkic odpowiedzi (2026‑09‑29)

> Dzień dobry Panie Łukaszu,
>
> Dziękuję za wiadomość. Takie rozwiązanie jest niezgodne z przepisami i z instrukcją ładowarki, dlatego nie możemy go zalecić ani zaakceptować.
>
> Norma dotycząca instalacji zasilających pojazdy elektryczne, PN-HD 60364-7-722, nie dopuszcza przewodu PEN w obwodzie zasilającym punkt ładowania. Instrukcja ładowarki wymaga podłączenia wyłącznie do prawidłowo uziemionego gniazda, w instalacji z osobnym przewodem ochronnym i neutralnym oraz z wyłącznikiem różnicowoprądowym. Mostek między N a PE w przejściówce nie zastępuje przewodu ochronnego, a jedynie sprawia, że zabezpieczenie ładowarki nie rozpozna jego braku. W razie przerwy w przewodzie PEN na obudowie ładowarki i na karoserii samochodu może pojawić się niebezpieczne napięcie, którego zabezpieczenia ładowarki nie wykryją.
>
> Podłączenie ładowarki przez taką przejściówkę byłoby użytkowaniem niezgodnym z instrukcją i odbywałoby się na wyłączną odpowiedzialność użytkownika. Po wykonaniu przez elektryka obwodu z osobnym przewodem ochronnym i gniazda 5-pinowego chętnie przygotujemy ofertę na ładowarkę.
>
> Pozdrawiam,
> Dawid Cekała
> Ampere Point

## Otwarte

- Wysłanie odpowiedzi; podpis — dotąd odpowiadał Miłosz Księżak.
- Weryfikacja wymagań w wysyłanej instrukcji serii Q.
- Zdanie o gwarancji celowo pominięte — w wersji roboczej instrukcji nie ma wyłączenia gwarancji za niewłaściwą instalację.
