# Tabela porównawcza Q11: moduł Tuya WBR3 a moduł Shelly X (tylko potwierdzone fakty), wersja polska.
# Wersja angielska: gap_excel.py. Uruchomienie: python gap_excel_pl.py <plik.xlsx>
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OUT = sys.argv[1]

FILL = {"✔": "C6EFCE", "◐": "FFEB9C", "✘": "FFC7CE", "?": "E7E6E6"}
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")

ROWS = [
    "Sterowanie i aplikacje",
    ("Aplikacja w telefonie, z internetem", "✔ Tuya Smart / Smart Life przez chmurę Tuya", "✔ Shelly Smart Control przez chmurę Shelly", "użytkowanie; B1 próba kontrolna"),
    ("Aplikacja w sieci lokalnej bez chmury", "✘ aplikacja potrzebuje chmury Tuya", "✘ aplikacja pokazuje „offline”; w sieci lokalnej tylko sprawdza moduł", "B1"),
    ("Strona WWW na ładowarce", "✘ brak", "◐ jest, bez logowania; domyślny ekran pokazuje 6 z 15 pól, fazy jako „N/A A”", "B2"),
    ("Lokalne API", "◐ brak oficjalnego; nieoficjalny protokół lokalny z kluczem urządzenia (tuya_local w Home Assistant)", "✔ HTTP i WebSocket JSON-RPC, udokumentowane; odczyt 40–150 ms, zapis potwierdzony przez sterownik w 1–2 s", "B7, C4"),
    ("MQTT", "✘", "✔ polecenia i zdarzenia przez lokalny broker (także bez internetu) i przez broker w internecie (publiczny broker testowy: polecenie i odpowiedź w ok. 1,1 s)", "C4, 01.10"),
    ("Wysyłanie danych do własnego serwera", "✘ tylko przez API chmury Tuya", "✔ wychodzący WebSocket (ponowne połączenie ≤ ok. 60 s) i webhooki na zmianę stanu, limitu i włącznika (ok. 1 s)", "B5, B8"),
    ("OCPP 1.6J", "✘", "◐ moduł nie ma klienta OCPP; działa przez nasz most (na komputerze lub serwerze, korzysta z lokalnego API): rejestracja, stan, pomiary co 30 s, limit prądu z serwera OCPP, pełna transakcja start/stop; także bez internetu (serwer OCPP w sieci lokalnej). Serwera OCPP w internecie nie testowaliśmy", "25.09, 01.10"),
    ("Home Assistant", "◐ oficjalna integracja Tuya i nasza integracja, obie przez chmurę Tuya", "◐ oficjalna integracja Shelly działa lokalnie, ale dla naszego produktu pokazuje tylko 12 czujników faz (sterowanie ładowarką tylko dla TopAC EVE01); z naszą łatką 33 encje, pełne sterowanie lokalne", "B3"),
    ("Praca bez internetu", "✘ aplikacja i zdalne sterowanie niedostępne; zostaje menu ładowarki", "✔ działają strona WWW, API, MQTT, Home Assistant, harmonogramy i webhooki; czas z serwera czasu w sieci lokalnej", "C2–C9"),
    "Sterowanie ładowaniem (ten sam sterownik ładowarki)",
    ("Start / stop ładowania (włącznik)", "✔ z aplikacji", "◐ start ✔; stop odrzucony przez sterownik w 3 z 6 prób, przyczyna nieustalona", "B3c, 30.09"),
    ("Limit prądu 6–16 A", "✔", "✔ potwierdzony w 1–2 s, wartość widoczna na wyświetlaczu ładowarki", "C2"),
    ("Tryb: od razu / do limitu energii / okno godzin", "✔", "✔", "B3c"),
    ("Limit energii sesji (1–200 kWh)", "✔", "✔", "B3c"),
    ("Okno godzin dla jednej sesji (pełne godziny)", "✔", "✔ sterownik startuje i kończy według czasu z modułu (start 22:00:03, koniec 23:00:03)", "C6"),
    ("Opóźnienie i czas trwania z menu ładowarki", "◐ działa; ustawione w stanie C pokazuje złe wartości", "◐ tak samo; moduł nie widzi tego ustawienia", "30.09"),
    ("Napięcie, prąd i moc faz", "◐ sterownik wysyła, aplikacja Tuya nie pokazuje", "✔ strona WWW, Home Assistant, aplikacja Shelly", "B2, B3"),
    ("Stan ładowarki, sygnał z auta, temperatura, błędy, wersja sterownika", "◐ sterownik wysyła; aplikacja pokazuje stan", "✔ wszystko jako pola; wersja „V1” zgłaszana po włączeniu zasilania", "B3, 30.09"),
    ("Energia i czas sesji", "◐ tylko energia ostatniej sesji; bieżąca liczona w Home Assistant", "✔ liczone w module (giną przy zaniku zasilania)", "B3, 04"),
    "Automatyka",
    ("Harmonogramy", "◐ w chmurze Tuya (wykonał się przy telefonie bez sieci)", "✔ w module, co do sekundy, także bez internetu; ✘ po zaniku zasilania bez serwera czasu działają według nieaktualnego zegara", "B4, C7, 04"),
    ("Sceny i automatyzacje", "✔ sceny w chmurze Tuya (czas, pogoda, urządzenia)", "◐ webhooki i skrypty w module; sceny w chmurze Shelly", "B5"),
    ("Własna logika w urządzeniu", "✘", "✔ usługa w JavaScripcie w module (działa w niej nasz tłumacz)", "B, C"),
    "Niezawodność",
    ("Restart modułu w trakcie ładowania", "?", "✔ ładowanie bez przerwy (5 restartów, po ok. 30 s)", "C9"),
    ("Po zaniku zasilania", "? (sterownik traci okno godzin i opóźnienie z menu przy obu modułach)", "✔ moduł odtwarza wszystkie swoje ustawienia, przy starcie nic nie zapisuje sterownikowi; ładowanie rusza samo; limit prądu zostaje", "04, C8"),
    ("Łącze ze sterownikiem ładowarki (protokół Tuya, UART 9600)", "✔ natywne", "◐ działa; raz utknęło > 3 min po restarcie, ponowienia potrafią przestawić kolejność poleceń, niezmienione odpowiedzi nie są przekazywane", "B3c, B12, 30.09"),
    ("Ikona sieci na wyświetlaczu ładowarki", "✔ pokazuje rzeczywisty stan", "✘ zawsze „połączony z chmurą”; ikona miga", "C5"),
    ("Reset Wi-Fi z menu ładowarki, aktualizacja sterownika przez moduł", "✔", "? nie sprawdzane", ""),
    "Pamięć",
    ("Pamięć programu / pamięć robocza", "2 MB / 256 kB", "8 MB (dwie kopie programu po 3 MB, system plików 896 kB) / 400 kB (117 kB wolne po starcie)", "karta katalogowa, kopia pamięci"),
    ("Co przechowuje moduł", "◐ Wi-Fi i klucze urządzenia; definicja produktu, harmonogramy i sceny w chmurze Tuya", "✔ definicja produktu, skrypt usługi, harmonogramy, webhooki, pamięć klucz-wartość, strona WWW; wszystko przetrwa zanik zasilania", "04"),
    ("Zapis zmienionych ustawień", "nie dotyczy", "◐ najwyżej co ok. 3 s; zmiany z ostatnich ok. 3 s giną przy zaniku zasilania", "04"),
    "Bezpieczeństwo i aktualizacje",
    ("Ochrona dostępu lokalnego", "◐ protokół lokalny wymaga klucza urządzenia", "✘ domyślnie bez hasła (hasło można ustawić)", "B2, B12"),
    ("Kopia konfiguracji", "✘", "◐ jest; niezaszyfrowana, zawiera hasło Wi-Fi", "B10"),
    ("Aktualizacje", "✔ moduł i sterownik przez Tuya / fabrykę", "✔ usługę wgrywamy sami, Wi-Fi zostaje; aktualizacja sterownika przez moduł nie sprawdzana", "29.09"),
]

wb = Workbook()
ws = wb.active
ws.title = "Tuya a Shelly"
ws.append(["Przenośna ładowarka Q11: moduł Tuya WBR3 a moduł Shelly X — potwierdzone fakty"])
ws["A1"].font = Font(bold=True, size=13)
ws.append(["AMPERE POINT · Dawid Cekała · 01.10.2026 · Shelly: DevKit M1, oprogramowanie 2.0.0-beta11, nasza usługa v4.3.1 · testy 29.09–01.10 bez chmury i bez internetu, z symulatorem auta"])
ws.append(["✔ tak / działa   ◐ częściowo / z ograniczeniem   ✘ nie   ? nie sprawdzano"])
ws.append([])
header = ["Funkcja", "Q11 z Tuya WBR3", "Q11 z Shelly X", "Potwierdzone w"]
ws.append(header)
hr = ws.max_row
for c in range(1, 5):
    cell = ws.cell(row=hr, column=c)
    cell.fill = PatternFill("solid", fgColor="1F4E78")
    cell.font = Font(bold=True, color="FFFFFF")
    cell.alignment, cell.border = WRAP, BORDER
for r in ROWS:
    if isinstance(r, str):
        ws.append([r])
        row = ws.max_row
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        cell = ws.cell(row=row, column=1)
        cell.fill, cell.font = PatternFill("solid", fgColor="D9E1F2"), Font(bold=True)
        continue
    ws.append(list(r))
    row = ws.max_row
    for c in range(1, 5):
        cell = ws.cell(row=row, column=c)
        cell.alignment, cell.border = WRAP, BORDER
        if c in (2, 3):
            sym = str(cell.value).strip()[:1]
            if sym in FILL:
                cell.fill = PatternFill("solid", fgColor=FILL[sym])
for col, w in zip("ABCD", (40, 48, 64, 18)):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "B%d" % (hr + 1)
wb.save(OUT)
print("zapisano", OUT, "wierszy", len([r for r in ROWS if not isinstance(r, str)]))
