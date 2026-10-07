# -*- coding: utf-8 -*-
"""Raport PDF: dobór stałego opóźnienia wznowienia ładowania po pauzie DLB."""
import json, os, sys, numpy as np
V2 = (len(sys.argv) > 1 and sys.argv[1] == 'v2')
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

here = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(here, '..', '..', 'AMPERE_POINT_DLB_opoznienie_wznowienia_v2.pdf' if V2 else 'AMPERE_POINT_DLB_opoznienie_wznowienia_v1.pdf')
F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Ar", F + r"\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", F + r"\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI", F + r"\ariali.ttf"))

C_ACC = colors.HexColor("#B45309"); C_DARK = colors.HexColor("#1F2937"); C_GRAY = colors.HexColor("#6B7280")
C_HEAD = colors.HexColor("#374151"); C_ALT = colors.HexColor("#F3F4F6"); C_OKBG = colors.HexColor("#DCFCE7")
C_OKBRD = colors.HexColor("#15803D"); C_WBG = colors.HexColor("#FEF3C7"); C_WBRD = colors.HexColor("#D97706")
C_HI = colors.HexColor("#FDE68A")

S = dict(
    title=ParagraphStyle("t", fontName="ArB", fontSize=18, leading=23, textColor=C_DARK, spaceAfter=3),
    sub=ParagraphStyle("s", fontName="Ar", fontSize=10, leading=14, textColor=C_GRAY, spaceAfter=10),
    h1=ParagraphStyle("h1", fontName="ArB", fontSize=13, leading=17, textColor=C_ACC, spaceBefore=12, spaceAfter=5),
    h2=ParagraphStyle("h2", fontName="ArB", fontSize=10.5, leading=14, textColor=C_DARK, spaceBefore=8, spaceAfter=3),
    body=ParagraphStyle("b", fontName="Ar", fontSize=9.6, leading=13.2, textColor=C_DARK, alignment=TA_JUSTIFY, spaceAfter=4),
    bul=ParagraphStyle("bl", fontName="Ar", fontSize=9.6, leading=13.2, textColor=C_DARK, leftIndent=12, bulletIndent=2, spaceAfter=2),
    small=ParagraphStyle("sm", fontName="Ar", fontSize=8, leading=10.5, textColor=C_GRAY, spaceAfter=4),
    tc=ParagraphStyle("tc", fontName="Ar", fontSize=8.3, leading=10.6, textColor=C_DARK),
    tcb=ParagraphStyle("tcb", fontName="ArB", fontSize=8.3, leading=10.6, textColor=C_DARK),
    th=ParagraphStyle("th", fontName="ArB", fontSize=8.3, leading=10.6, textColor=colors.white),
    bt=ParagraphStyle("bt", fontName="ArB", fontSize=9.6, leading=12.5, textColor=C_DARK),
    bb=ParagraphStyle("bb", fontName="Ar", fontSize=9.3, leading=12.4, textColor=C_DARK, alignment=TA_JUSTIFY),
)
P = lambda t, s="body": Paragraph(t, S[s])
B = lambda t: Paragraph(t, S["bul"], bulletText="\u2013")


def box(title, text, bg, brd):
    t = Table([[Paragraph(title, S["bt"])], [Paragraph(text, S["bb"])]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 2.2, brd),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
                           ("TOPPADDING", (0, 1), (-1, 1), 1)]))
    return KeepTogether(t)


def table(rows, widths, hi_col=None, bold_first=False):
    data = [[Paragraph(str(c), S["th"]) for c in rows[0]]]
    for i, r_ in enumerate(rows[1:]):
        data.append([Paragraph(str(c), S["tcb"] if (bold_first and j == 0) else S["tc"]) for j, c in enumerate(r_)])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), C_HEAD), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    for i in range(2, len(data), 2):
        st.append(("BACKGROUND", (0, i), (-1, i), C_ALT))
    if hi_col is not None:
        st.append(("BACKGROUND", (hi_col, 1), (hi_col, -1), C_HI))
    t.setStyle(TableStyle(st))
    return t


r = json.load(open(os.path.join(here, 'wyniki.json'), encoding='utf-8'))
TL = r['T_list']; H = r['houses']; W = sum(h['weight'] for h in H.values()); SI = r['sites']
SHOW = [60, 120, 180, 240, 300, 600, 900]
wavg = lambda key, T: sum(h['weight'] * h['T'][str(T)][key] for h in H.values()) / W
f1 = lambda v: f"{v:.1f}"

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Opóźnienie wznowienia ładowania po pauzie DLB", author="AMPERE POINT")
E = []
E.append(P("Opóźnienie wznowienia ładowania po pauzie DLB — dobór wartości", "title"))
E.append(P(("AMPERE POINT · rozwój modułu DLB-A1 · wersja 2 · 2026-09-28 (v1: rekomendacja 4 min; v2: decyzja 5 min) · " if V2 else "AMPERE POINT · rozwój modułu DLB-A1 · wersja 1 · 2026-09-28 · ") + "źródła i symulacja: <i>DLB_R&amp;D\\zasoby_informacji\\symulacja</i>", "sub"))

if V2:
    E.append(box("Decyzja: 5 minut (300 s), liczone od zatrzymania ładowania",
        "Symulacja wskazuje przedział 3–5 minut; z niego wybrano górną wartość, bo daje najmniej cykli start/stop, a jest okrągła "
        "i łatwa do zakomunikowania klientowi i instalatorowi. Wobec 4 minut dodatkowa minuta zmniejsza liczbę cykli pustych "
        "(start i natychmiastowy stop) o połowę, a cykli w najgorszej godzinie o jedną piątą; kosztuje średnio 1,2 min późniejsze "
        "zakończenie ładowania i o 0,6 min dłuższą najdłuższą pauzę — dla klienta bez znaczenia. Wartość przekracza okres pracy termostatu "
        "piekarnika i suszarki (2–5 min), więc wallbox pomija ich cykle zamiast za nimi nadążać. Warunek: w instrukcji, ulotce i skrypcie "
        "serwisu podać wprost „wznowienie po 5 minutach od zatrzymania”, żeby test instalatora miał jasne kryterium — bez tego pauza "
        "równa 5 minutom wygląda jak brak wznowienia (tyle czekali instalatorzy 26.09).", C_OKBG, C_OKBRD))
else:
  E.append(box("Wniosek: 4 minuty (240 s), liczone od zatrzymania ładowania",
    "Dopuszczalny przedział to 3–5 minut; 4 minuty leżą w miejscu, gdzie krzywa liczby cykli start/stop przestaje "
    "wyraźnie spadać, a pauza wciąż mieści się poniżej 5 minut — tyle instalatorzy czekali podczas testu i uznali brak "
    "wznowienia za usterkę. Wartość jest dłuższa niż okres pracy termostatu piekarnika i suszarki (2–5 min), więc przy takich "
    "odbiornikach wallbox pomija ich cykle zamiast za nimi nadążać, a zarazem bliska czasowi gotowania wody w czajniku "
    "(2–4 min), więc po najczęstszej przyczynie pauzy ładowanie wraca niemal od razu po jej ustaniu.", C_OKBG, C_OKBRD))
E.append(Spacer(1, 6))

E.append(P("1. Zasada działania, którą potwierdził producent", "h1"))
E.append(P("Gdy przydział dla wallboxa spada poniżej 6 A, wallbox zatrzymuje ładowanie i od tej chwili odlicza opóźnienie T. "
           "Po upływie T wznawia od razu, jeśli prąd już wystarcza; jeśli nie — czeka i wznawia w chwili, gdy prąd wystarczy. "
           "Nie ma dodatkowego sprawdzania stabilności ani zapasu przy wznowieniu. Z tej zasady wynikają trzy rzeczy:"))
E.append(B("obciążenie trwające <b>dłużej niż T</b> nie dokłada żadnego opóźnienia — ładowanie wraca zaraz po jego końcu;"))
E.append(B("obciążenie <b>krótsze niż T</b> wydłuża pauzę do T; przy 11 kW każda minuta pauzy to 0,18 kWh przesunięte w czasie;"))
E.append(B("T jest twardym limitem liczby cykli: najwyżej <b>60/T na godzinę</b> (T w minutach), ale nie zapobiega skakaniu, gdy przydział "
           "krąży wokół 6 A — wtedy wallbox wznawia i zatrzymuje ładowanie co T."))
E.append(P("Skutek dla odbiorników okresowych (termostat piekarnika, suszarki, żelazka): jeśli T jest krótsze niż okres termostatu, "
           "wallbox wznawia w każdej przerwie grzania i zatrzymuje przy każdym włączeniu — liczba cykli nie zależy od T. "
           "Dopiero T dłuższe niż okres pomija całe cykle grzania. Przykład: piekarnik grzeje 80 s co 4 min. Przy T = 3 min "
           "wallbox startuje 15 razy na godzinę, przy T = 5 min około 9, przy T = 10 min około 5."))

E.append(Image(os.path.join(here, 'rys2_noc.png'), width=14.2 * cm, height=14.2 * cm * 5.2 / 8.6))
E.append(P("Rys. 2. Jedna wylosowana noc w domu 3×16 A: rozgrzewanie piekarnika (19:15–19:35) zabiera cały przydział, potem termostat "
           "włącza grzałkę co ok. 4 min. Zielone pola to ładowanie. Przy T = 1 min wallbox startuje w każdej przerwie grzania, często "
           "na kilkanaście sekund; przy T = " + ("5 min pomija większość cykli termostatu" if V2 else "4 min część cykli pomija") + "; przy T = 10 min startuje rzadko, ale każda pauza trwa 10 min.", "small"))
E.append(P("2. Metoda", "h1"))
E.append(P("Symulacja z rozdzielczością 1 s: 120 losowych wieczorów i nocy (17:00–07:00) dla każdego z siedmiu typów domów, "
           "30 dni dla każdego z czterech obiektów z kilkoma wallboxami. Auto podłączane między 17:30 a 19:30, potrzebuje 15–45 kWh "
           "(3,7 kW: 10–25 kWh). Odbiorniki mają typowe moce katalogowe i losowe pory włączeń; termostaty i płyta indukcyjna "
           "pracują impulsowo. Narastanie prądu auta po starcie: 8 s zwłoki + 30 s narastania (z logu auta trójfazowego). "
           "Przydział DLB = 90 % limitu minus najbardziej obciążona faza reszty domu, w pełnych amperach."))
rows = [["Typ domu", "Waga", "Odbiorniki, które wywołują pauzy", "Pauz na noc przy T = 0", "Nocy z pauzą"]]
for name, h in H.items():
    rows.append([name, f"{h['weight']:.2f}", h['desc'], f"{h['pauses_T0_mean']:.1f} (90 % nocy poniżej {h['pauses_T0_p90']:.0f})", f"{h['nights_with_pause_pct']:.0f} %"])
E.append(table(rows, [4.3 * cm, 1.1 * cm, 6.8 * cm, 3.2 * cm, 1.6 * cm], bold_first=True))
E.append(P("Wagi to szacunek udziału danego typu wśród klientów z DLB (przyłącze 3×25 A najczęstsze). Pełna lista założeń o odbiornikach "
           "jest w pliku symulacji i można ją zmienić bez ruszania reszty.", "small"))

E.append(P("3. Wyniki dla domów", "h1"))
rows = [["Miara (średnia ważona 7 typów)"] + [f"T = {T // 60} min" for T in SHOW]]
for key, lab in [("cycles_mean", "cykle start/stop na noc"), ("maxh_p90", "cykle w najgorszej godzinie (90 % nocy poniżej)"),
                 ("empty_mean", "cykle puste (< 60 s ładowania) na noc"), ("short_mean", "cykle krótkie (< 5 min) na noc"),
                 ("fin_delay_mean", "późniejsze zakończenie ładowania [min]"), ("pause_max_mean", "najdłuższa pauza w nocy [min]")]:
    rows.append([lab] + [f1(wavg(key, T)) for T in SHOW])
E.append(table(rows, [6.4 * cm] + [1.51 * cm] * len(SHOW), hi_col=5 if V2 else 4))
E.append(Spacer(1, 4))
E.append(Image(os.path.join(here, 'rys1_krzywe.png'), width=17 * cm, height=17 * cm * 3.3 / 8.6))
E.append(P("Rys. 1. Lewy panel: liczba cykli maleje z T, ale od 4–5 min coraz wolniej. Prawy: koszt rośnie liniowo — każda minuta T "
           "to później zakończone ładowanie i dłuższa najdłuższa pauza. Żółte pole: przedział 3–5 min; linia przerywana: " + ("5" if V2 else "4") + " min. Nierówności między 2 a 3 min (np. cykle puste) to rezonans T z okresem termostatu piekarnika w modelu (4 min).", "small"))

E.append(P("Które domy są wrażliwe", "h2"))
rows = [["Typ domu", "Cykle/noc<br/>T=3 · 4 · 5 min", "Najgorsza godzina<br/>T=3 · 4 · 5 min", "Późniejszy koniec [min]<br/>T=3 · 4 · 5 min", "Uwaga"]]
notes = {'A1': "pauzy tylko przy zbiegu dwóch dużych odbiorników na jednej fazie",
         'A2': "sprężarka + grzałka + bojler; długie okresy, T mało zmienia",
         'A3': "czajnik sam wywołuje pauzę; piekarnik = cykl co 4 min, dopiero T ≥ 4 min je pomija",
         'A4': "jak A3, mniej ostro", 'A5': "wiele krótkich zdarzeń (mycie rąk 20–60 s): każde kosztuje pełne T — tu krótsze T jest lepsze",
         'A6': "wszystko na jednej fazie; indukcja impulsowa daje skakanie wokół progu",
         'A7': "pauzy rzadkie, T bez znaczenia"}
for name, h in H.items():
    k = name[:2]; g = lambda key: " · ".join(f1(h['T'][str(T)][key]) for T in (180, 240, 300))
    rows.append([name, g('cycles_mean'), g('maxh_p90'), g('fin_delay_mean'), notes[k]])
E.append(table(rows, [4.1 * cm, 2.4 * cm, 2.7 * cm, 2.8 * cm, 5.0 * cm], bold_first=True))

E.append(P("Test wrażliwości: okres termostatu piekarnika", "h2"))
E.append(P("Dom 3×16 A, piekarnik u wszystkich, 60 nocy. Cykle w najgorszej godzinie (90 % nocy poniżej):"))
rows = [["Okres termostatu", "T = 1 min", "2 min", "3 min", "4 min", "5 min", "10 min"],
        ["1,5 min (45 s / 45 s)", "32", "17", "15", "12", "9", "6"],
        ["3 min (60 s / 120 s)", "20", "17", "15", "10", "9", "6"],
        ["4 min (80 s / 160 s) — bazowy", "16", "15", "15", "11", "8", "6"],
        ["5 min (100 s / 200 s)", "15", "14", "13", "10", "8", "5"]]
E.append(table(rows, [4.6 * cm] + [2.06 * cm] * 6, hi_col=5 if V2 else 4))
E.append(P("Niezależnie od okresu termostatu największy spadek liczby cykli przypada między 3 a 5 minutami. Poniżej 3 min T prawie nic nie "
           "zmienia, powyżej 5 min zyski są małe, a pauzy długie.", "small"))

E.append(P("4. Budynki z kilkoma wallboxami i zakład", "h1"))
rows = [["Obiekt", "Pauz/dzień przy T = 0", "Cykle/dzień (wszystkie auta)<br/>T = 1 · 2 · 3 · 4 · 5 · 10 min", "Najgorsza godzina<br/>T = 1 · 3 · 4 · 5 · 10 min"]]
for name, s in SI.items():
    rows.append([name, f1(s['pauses_T0_mean']),
                 " · ".join(f1(s['T'][str(T)]['cycles_mean']) for T in (60, 120, 180, 240, 300, 600)),
                 " · ".join(f1(s['T'][str(T)]['maxh_mean']) for T in (60, 180, 240, 300, 600))])
E.append(table(rows, [5.2 * cm, 2.3 * cm, 5.3 * cm, 4.2 * cm], bold_first=True))
E.append(P("Wspólnota z przyłączem 3×40 A i trzema wallboxami jest po prostu niedowymiarowana: pauzy wynikają z windy, hydroforu i suszarek "
           "w pralni, a T tylko je rozrzedza (40 → 28 cykli przy 4 min). W biurze i zakładzie pauzy wywołują krótkie szczyty (winda, sprężarka, "
           "spawarka, 10–90 s): tam wystarczy T dłuższe niż szczyt, czyli około 2 min, i dłuższe T nic już nie daje ani nie kosztuje — "
           "wszystkie auta kończą ładowanie w ciągu dnia. Dla tych zastosowań 4 min jest neutralne."))

E.append(P("5. Dlaczego nie krócej i dlaczego nie dłużej", "h1"))
E.append(B("<b>1–2 min:</b> w domach z termostatami liczba cykli jest taka sama jak bez opóźnienia (T krótsze niż okres grzania); "
           "co czwarty start jest pusty — auto nie zdąży rozpędzić prądu, zanim znów zostanie zatrzymane."))
E.append(B("<b>3 min:</b> pokrywa czajnik, ale w domach 3×16–20 A wciąż 15 cykli w najgorszej godzinie."))
E.append(B("<b>4 min:</b> koniec stromego odcinka krzywej; w typowym domu 3×25 A ładowanie kończy się średnio 3 min później, "
           "w domu z przepływowym podgrzewaczem 20 min później — i tak przed ranem." + (" Wartość dobra, ale nieokrągła." if V2 else "")))
if V2:
    E.append(B("<b>5 min (wybrane):</b> najmniej cykli w przedziale — wobec 4 min o połowę mniej cykli pustych i o jedną piątą mniej "
               "w najgorszej godzinie, za cenę 1,2 min późniejszego końca ładowania. Każda pauza trwa co najmniej 5 min, więc "
               "po 2-minutowym czajniku ładowanie stoi jeszcze 3 min — do zaakceptowania, jeśli klient wie, że tak ma być. "
               "Dlatego liczba „5 minut” musi znaleźć się w instrukcji i ulotce."))
else:
  E.append(B("<b>5 min:</b> nieco mniej cykli, ale każda pauza trwa co najmniej 5 min; tyle właśnie czekali instalatorzy i uznali, że "
           "urządzenie nie wznawia. Klient po 2-minutowym czajniku patrzy na stojące ładowanie jeszcze 3 min."))
E.append(B("<b>10 min i więcej:</b> zysk w cyklach mały, koszt duży (18 min później koniec, pauzy 16 min), rośnie ryzyko, że auto "
           "po dłuższej przerwie zaśnie i nie wznowi — norma IEC 61851-1 nie wymaga od auta wznowienia po powrocie sygnału."))

E.append(P("6. Czego stałe opóźnienie nie załatwia", "h1"))
E.append(P("Przydział krążący wokół 6 A (indukcja na małej mocy, pompa ciepła o zmiennej mocy, dom na granicy limitu) daje cykl co T "
           "niezależnie od wartości T — przy 4 min to 15 startów na godzinę, a ładowanie w każdym trwa sekundy. Chwilowe szczyty poniżej "
           "sekundy (rozruch sprężarki) wywołują pełną pauzę T. Auto, które nie wznawia po powrocie sygnału, nie ruszy przy żadnym T — "
           "w logu z 26.09 auto trójfazowe nie wznowiło po żadnej z przerw, a dwufazowe wznawiało po 4–5 s. To są sprawy do osobnego "
           "zgłoszenia producentowi; dobór T ich nie dotyczy."))

E.append(P("7. Założenia i ograniczenia", "h1"))
E.append(B("Moce i czasy odbiorników to wartości katalogowe i typowe, nie pomiary u klientów; wagi typów domów to szacunek."))
E.append(B("Przyjęto, że DLB nie filtruje pomiaru i reaguje w 1 s; że próg wznowienia równa się progowi pauzy (6 A); że wallbox po wznowieniu "
           "dostaje prąd po 8 s i osiąga pełną wartość po 30 s (z logu). Wersja V1.4 modułu może zaokrąglać przydział inaczej niż V1.1 (skoki co 3 A)."))
E.append(B("Symulacja liczy jeden sezon (jesień/zima, bez klimatyzacji). Latem klimatyzator (8–9 A, cykle 8/8 min) zachowuje się jak pompa ciepła "
           "— wynik nie zmienia się."))
E.append(B("Nie uwzględniono zachowania auta po długiej pauzie (sen). Brak danych; argument działa na korzyść krótszego T."))

doc.build(E)
print('PDF:', os.path.abspath(OUT))
