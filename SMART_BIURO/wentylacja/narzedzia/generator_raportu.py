# -*- coding: utf-8 -*-
"""Raport: integracja klimatyzatorów Gree z Home Assistant."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\Integracja_klimatyzacji_Gree_z_Home_Assistant.pdf"

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Ar", F + r"\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", F + r"\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI", F + r"\ariali.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + r"\cour.ttf"))
pdfmetrics.registerFont(TTFont("MonoB", F + r"\courbd.ttf"))

C_ACCENT = colors.HexColor("#B45309")
C_DARK = colors.HexColor("#1F2937")
C_GRAY = colors.HexColor("#6B7280")
C_LINE = colors.HexColor("#D1D5DB")
C_WARNBG = colors.HexColor("#FEF3C7")
C_WARNBRD = colors.HexColor("#D97706")
C_INFOBG = colors.HexColor("#E0F2FE")
C_INFOBRD = colors.HexColor("#0369A1")
C_OKBG = colors.HexColor("#DCFCE7")
C_OKBRD = colors.HexColor("#15803D")
C_HEADBG = colors.HexColor("#374151")
C_ROWALT = colors.HexColor("#F3F4F6")
C_CODEBG = colors.HexColor("#F5F5F4")

S = {}
S["title"] = ParagraphStyle("title", fontName="ArB", fontSize=20, leading=25, textColor=C_DARK, spaceAfter=4)
S["subtitle"] = ParagraphStyle("subtitle", fontName="Ar", fontSize=11, leading=15, textColor=C_GRAY, spaceAfter=2)
S["h1"] = ParagraphStyle("h1", fontName="ArB", fontSize=14.5, leading=18, textColor=C_ACCENT, spaceBefore=16, spaceAfter=7)
S["h2"] = ParagraphStyle("h2", fontName="ArB", fontSize=11.5, leading=15, textColor=C_DARK, spaceBefore=11, spaceAfter=5)
S["body"] = ParagraphStyle("body", fontName="Ar", fontSize=10, leading=13.8, textColor=C_DARK, alignment=TA_JUSTIFY, spaceAfter=5)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=14, bulletIndent=4, spaceAfter=3)
S["small"] = ParagraphStyle("small", fontName="Ar", fontSize=8.4, leading=11, textColor=C_GRAY)
S["tcell"] = ParagraphStyle("tcell", fontName="Ar", fontSize=8.8, leading=11.4, textColor=C_DARK)
S["tcellb"] = ParagraphStyle("tcellb", fontName="ArB", fontSize=8.8, leading=11.4, textColor=C_DARK)
S["thead"] = ParagraphStyle("thead", fontName="ArB", fontSize=8.8, leading=11.4, textColor=colors.white)
S["boxtitle"] = ParagraphStyle("boxtitle", fontName="ArB", fontSize=9.6, leading=12.5, textColor=C_DARK)
S["boxbody"] = ParagraphStyle("boxbody", fontName="Ar", fontSize=9.3, leading=12.4, textColor=C_DARK, alignment=TA_JUSTIFY)
S["code"] = ParagraphStyle("code", fontName="Mono", fontSize=8.2, leading=10.6, textColor=C_DARK)
S["iterlead"] = ParagraphStyle("iterlead", fontName="ArI", fontSize=10, leading=13.8, textColor=C_DARK, alignment=TA_JUSTIFY, spaceAfter=5)


def P(text, style="body"):
    return Paragraph(text, S[style])


def B(text):
    return Paragraph(text, S["bullet"], bulletText="\u2013")


def box(title, text, bg, border):
    t = Table(
        [[Paragraph(title, S["boxtitle"])], [Paragraph(text, S["boxbody"])]],
        colWidths=[17.0 * cm],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, 1), 1),
    ]))
    return KeepTogether(t)


def warn(title, text):
    return box(title, text, C_WARNBG, C_WARNBRD)


def info(title, text):
    return box(title, text, C_INFOBG, C_INFOBRD)


def ok(title, text):
    return box(title, text, C_OKBG, C_OKBRD)


def tbl(header, rows, widths, aligns=None):
    data = [[Paragraph(h, S["thead"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, S["tcell"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), C_HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, C_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_ROWALT]),
    ]
    t.setStyle(TableStyle(style))
    return t


def code(txt):
    t = Table([[Preformatted(txt, S["code"])]], colWidths=[17.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.4, C_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Ar", 7.6)
    canvas.setFillColor(C_GRAY)
    canvas.drawString(2 * cm, 1.1 * cm, "Integracja klimatyzacji Gree z Home Assistant \u2014 v2, po udanym te\u015Bcie sondy (2026-08-22)")
    canvas.drawRightString(19 * cm, 1.1 * cm, f"strona {doc.page}")
    canvas.setStrokeColor(C_LINE)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, 1.35 * cm, 19 * cm, 1.35 * cm)
    canvas.restoreState()


story = []

# ── Nagłówek ──────────────────────────────────────────────────────────────
story.append(P("Integracja klimatyzatorów Gree z Home Assistant", "title"))
story.append(P("Analiza sprzętu, pinouty przewodów, iteracje projektowe i plan wdrożenia dla instalacji wielojednostkowej", "subtitle"))
story.append(P("Obiekt: kasetony Gree GKH(12)BB-K6DNA3A/I \u2022 wersja 2 \u2014 uzupe\u0142niona o studium przypadku i zweryfikowan\u0105 konfiguracj\u0119 (2026-08-22)", "subtitle"))
story.append(Spacer(1, 4))
story.append(ok("ODCZYT DZIAŁA, STEROWANIE OTWARTE (stan 2026-08-25)",
    "Sonda zbudowana wyłącznie z posiadanych części <b>odczytuje stan kasetonu</b> z portu COM-MANUAL i podaje go do Home Assistant. Uwaga: to <b>bierny podsłuch</b> — jednostka nadaje swój stan sama co 800 ms i <b>nie odpowiada</b> na nasze ramki (ponad 1100 przetestowanych wariantów, zero reakcji). Historia diagnozy: rozdz. 7. Konfiguracja: rozdz. 8. Dalsze kroki: rozdz. 10.")) 
story.append(Spacer(1, 8))

# ── 1. Streszczenie ───────────────────────────────────────────────────────
story.append(P("1. Streszczenie zarz\u0105dcze", "h1"))
story.append(B("<b>Cel osiągnięty na poziomie odczytu:</b> kaseton Gree <b>rozgłasza</b> swój stan na porcie COM-MANUAL (1200 bodów, ramki 7E 7E, suma XOR) równo co 800 ms, a sonda ten rozgłos czyta — bez żadnych zakupów sprzętowych. <b>Jednostka nie odpowiada na zapytania</b> i nie przyjmuje poleceń od niezarejestrowanego sterownika."))
story.append(B("<b>\u015acie\u017cka Modbus (bramka w gniazdo COM-BMS) upad\u0142a definitywnie</b> \u2014 na p\u0142ycie GRZ4M-A3 tego gniazda nie ma. Bramka ZTS47/SMG-01 zosta\u0142a za to <b>przerobiona na konwerter sygna\u0142\u00f3w</b> (UART 5 V \u2194 RS485) i jest sercem dzia\u0142aj\u0105cej sondy \u2014 opis w dokumencie plytki\\bramka_grz47_smg01.md."))
story.append(B("<b>Droga do sukcesu wymaga\u0142a trzech odkry\u0107</b> (rozdz. 7): myl\u0105ce opisy pin\u00f3w p\u0142ytki WeMos D1 R1, brak automatu kierunku w bramce (piny RXP/TXP musz\u0105 by\u0107 sterowane) oraz opisy TXD/RXD na laminacie bramki pisane z perspektywy klimatyzatora."))
story.append(B("<b>Wa\u017cny incydent:</b> pr\u00f3ba zasilenia sondy z pinu +12 V portu COM-MANUAL <b>blokowa\u0142a start ca\u0142ego klimatyzatora</b>. Mechanizm wyja\u015bniony w rozdz. 9; wniosek \u2014 sonda/mostek zawsze na w\u0142asnym zasilaczu 5 V."))
story.append(B("<b>Nast\u0119pny etap:</b> dekodowanie p\u00f3l protoko\u0142u metod\u0105 r\u00f3\u017cnicow\u0105 (zmiana nastawy pilotem \u2192 por\u00f3wnanie ramek), potem docelowy mostek WiFi z encj\u0105 climate w Home Assistant \u2014 plan i ulepszenia w rozdz. 10."))
story.append(B("Modu\u0142 WiFi GRJWB04-J pozostaje nieprzydatny dla kaseton\u00f3w (brak gniazda) \u2014 do wykorzystania przy ewentualnych jednostkach \u015bciennych Gree."))
story.append(B("Dokumentacja towarzysz\u0105ca w folderze projektu: STUDIUM_PRZYPADKU.md (pe\u0142na historia diagnozy), plytki\\ (dokumentacja ka\u017cdej u\u017cytej p\u0142ytki), schematy\\schemat_FINALNY_dzialajacy.png, test_com_manual\\PROCEDURA_TESTU.md."))

# ── 2. Sprzęt ─────────────────────────────────────────────────────────────
story.append(P("2. Zinwentaryzowany sprzęt", "h1"))
story.append(tbl(
    ["Element", "Identyfikacja", "Kluczowe fakty"],
    [
        ["Jednostka wewnętrzna",
         "Gree <b>GKH(12)BB-K6DNA3A/I</b>, kaseton sufitowy, seria Free Match / Multi, czynnik R32, prod. 2019-01",
         "Chłodzenie 3500 W, grzanie 4000 W, przepływ 650 m\u00B3/h, 41 dB(A), 20 kg, 220\u2013240 V. Sterowanie: pilot IR + opcjonalne akcesoria przewodowe."],
        ["Płyta główna (AP1)",
         "<b>GRZ4M-A3</b> V1 2017/09/25 (nr części 300002060012)",
         "Ta sama rodzina płyt (GRZ4M) co jednostki U-Match, dla których dokumentacja bramki wskazuje gniazdo COM-BMS. Porty opisane w rozdz. 4."],
        ["Panel z wyświetlaczem (AP2)",
         "Listwa z 7-segm. wyświetlaczem, odbiornikiem IR i przyciskami AUTO/TEST",
         "Połączona z płytą główną dwiema taśmami (DISP1, DISP2). Wyświetlany kod \u201EFU\u201D = ograniczanie częstotliwości sprężarki (ochrona przed oszronieniem), nie usterka i nie filtr (filtr = \u201ECL\u201D)."],
        ["Moduł WiFi (posiadany)",
         "Gree <b>GRJWB04-J</b>, nr 300018060398, fabrycznie nowy",
         "4-żyłowy kabel z niebieskim wtykiem. Przeznaczenie: gniazdo WIFI w splitach ściennych Gree. <b>W tym kasetonie brak pasującego gniazda \u2014 niekompatybilny.</b>"],
        ["Bramka (posiadana)",
         "Gree Gateway Kit <b>ZTS47</b>, nr 300014000011, etykieta \u201E137305 SMG-01\u201D, prod. 2025-04 \u2261 <b>Sinclair SMG-01 Modbus Gateway</b>",
         "Kabel L2: 6-\u017cy\u0142owy, czerwony wtyk przeznaczony do gniazda COM-BMS (kt\u00f3rego na p\u0142ycie A3 nie ma). <b>Od 2026-08-22 bramka pracuje jako konwerter UART\u2194RS485 sondy</b> \u2014 rozdz. 7\u20138 i plytki\\bramka_grz47_smg01.md."],
        ["\u201EJednostka centralna\u201D",
         "<b>Rozstrzygni\u0119te: brak wsp\u00f3lnego systemu zarz\u0105dzania</b>",
         "Na dachu jest jednostka zewn\u0119trzna; kasetony s\u0105 sterowane wy\u0142\u0105cznie pilotami IR. Home Assistant b\u0119dzie pierwszym wsp\u00f3lnym sterowaniem \u2014 bez ryzyka konfliktu z istniej\u0105cym sterownikiem centralnym."],
    ],
    [3.1 * cm, 5.6 * cm, 8.3 * cm],
))

# ── 3. Zdjęcia ────────────────────────────────────────────────────────────
story.append(P("3. Co ustaliła analiza zdjęć", "h1"))
story.append(P("Zdj\u0119cia projektu: <b>zdjecia\\uklad\\</b> (uk\u0142ad testowy), <b>zdjecia\\flasher\\</b> (programator u\u017cyty serwisowo), <b>dzialajace_polaczenie\\</b> (kompletny uk\u0142ad przy jednostce). Poni\u017cej ustalenia z pierwotnej analizy zdj\u0119\u0107 instalacji:"))
story.append(tbl(
    ["Grupa zdjęć", "Ustalenia"],
    [
        ["Tabliczka znamionowa i naklejka R32",
         "Model GKH(12)BB-K6DNA3A/I, parametry jw. Czynnik R32 (palny): pomieszczenie \u2265 4 m\u00B2, zakaz źródeł zapłonu \u2014 istotne przy pracach w suficie."],
        ["Naklejka ze schematem elektrycznym (INDOOR UNIT)",
         "Pełna lista złączy płyty AP1: ROOM, TUBE, PUMP, WATER-DTCT, COM-MANUAL (\u2192 sterownik przewodowy AP3), DOOR-C/X10 (styk beznapięciowy AP4, opcja), DISP1/DISP2 (\u2192 panel AP2), SWING-UD1/UD2, DC-MOTOR, N1/COM-OUT/AC-L (zasilanie i komunikacja z jednostką zewnętrzną przez listwę XT). <b>Schemat nie wymienia żadnego portu WiFi</b> \u2014 stąd pewność, że moduł WiFi nie ma tu miejsca. Uwaga: schemat nie musi pokazywać gniazd niewykorzystywanych w danym modelu (na płycie fizycznie są np. SWING-LR1/LR2, których schemat nie pokazuje) \u2014 dlatego obecności COM-BMS nie da się rozstrzygnąć samym schematem."],
        ["Zbliżenia płyty głównej",
         "COM-MANUAL: białe 4-pin, <b>wolne</b>. Obok układ scalony z rodziny MAX130xx (transceiver RS-485; odczyt z fotografii) \u2014 spójne z różnicową magistralą A/B na tym porcie. DOOR-C (DRY-C): niebieskie gniazdo <b>zajęte</b> czarnym kablem \u2014 najpewniej mostka/styk okienny lub czujnik; <b>nie odłączać</b> (jednostka może odmówić pracy). Niebieski kapturek \u201E1\u201D na pinach JUMP = zworka kodująca model \u2014 <b>nie ruszać</b>. DISP1/DISP2 zajęte (panel). SWING-LR1/LR2 wolne (niewykorzystywane w tym modelu). Czerwone gniazdo DC-MOTOR = zasilanie silnika wentylatora \u2014 <b>wysokie napięcie, niczego tam nie wpinać</b>."],
        ["Panel przedni / listwa wyświetlacza",
         "Odbiornik IR i wyświetlacz na cienkiej listwie; kod \u201EFU\u201D w trakcie pracy. Za listwą płytka AP2 \u2014 na sfotografowanej stronie brak wolnego gniazda pasującego do wtyku modułu WiFi."],
        ["Moduł WiFi + wtyk",
         "GRJWB04-J, 4 żyły, niebieski wtyk kluczowany. Brak pasującego gniazda w jednostce (test fizyczny użytkownika + schemat)."],
        ["Bramka + jej instrukcja",
         "Gateway Kit: topologia \u201Esterownik centralny / monitor \u2014 magistrala L1 \u2014 do 255 bramek \u2014 każda bramka kablem L2 do swojej jednostki\u201D. Zaciski A, A, B, B pod pokrywą (podwójne \u2014 do łączenia przelotowego). Dobór przewodu L1: skrętka 2-żyłowa AWG24; powyżej 800 m wymagany repeater optoizolowany."],
        ["Luźne okablowanie przy kracie wentylatora",
         "Przewód w żółtej koszulce niezakończony wtykiem \u2014 nie jest to złącze akcesoriów; bez znaczenia dla integracji."],
    ],
    [4.6 * cm, 12.4 * cm],
))

# ── 4. Architektura sterowania ───────────────────────────────────────────
story.append(P("4. Jak zbudowane jest sterowanie tej jednostki", "h1"))
story.append(P("Kaseton nie ma żadnego interfejsu sieciowego. Całe sterowanie przechodzi przez płytę główną AP1, do której prowadzą trzy drogi: (1) pilot IR przez odbiornik na panelu AP2, (2) port sterownika przewodowego COM-MANUAL, (3) \u2014 jeżeli występuje \u2014 gniazdo COM-BMS dla bramki Modbus. Komunikacja z jednostką zewnętrzną biegnie osobno, przez listwę zaciskową (żyła COM-OUT) i nie jest dostępna dla integracji."))
story.append(tbl(
    ["Port na płycie", "Stan u Ciebie", "Rola"],
    [
        ["COM-MANUAL (4-pin, białe)", "wolny",
         "Port sterownika przewodowego (XK...). 4 żyły: GND, +12 V, A, B (RS485). Tu wpina się XK117 wymagany do aktywacji Modbus; tu też można zbudować mostek DIY (iteracja 3)."],
        ["COM-BMS (6-pin, ciemnoczerwone)", "<b>BRAK na tej p\u0142ycie</b>",
         "Ogl\u0119dziny p\u0142yty A3 nie wykaza\u0142y gniazda \u2014 \u015bcie\u017cka fabrycznego Modbusa (iteracja 4) upad\u0142a. Bramka znalaz\u0142a nowe \u017cycie jako konwerter sondy na COM-MANUAL (rozdz. 7\u20138)."],
        ["DISP1 / DISP2 (15-żył.)", "zajęte", "Połączenie z panelem AP2 (wyświetlacz, odbiornik IR, przyciski)."],
        ["DOOR-C / DRY-C (niebieskie)", "zajęte", "Styk beznapięciowy (karta hotelowa / czujnik okna). Nie odłączać bez zrozumienia, co jest wpięte."],
        ["DC-MOTOR (czerwone)", "zajęte", "<b>Zasilanie silnika wentylatora \u2014 nie mylić z COM-BMS</b> (oba mogą być czerwonawe!). Pomyłka grozi zniszczeniem bramki."],
        ["ROOM / TUBE / PUMP / WATER-DTCT", "zajęte", "Czujniki temperatury, pompka skroplin, czujnik poziomu \u2014 bez znaczenia dla integracji."],
    ],
    [4.2 * cm, 2.6 * cm, 10.2 * cm],
))
story.append(Spacer(1, 4))
story.append(warn("Ostrzeżenie \u2014 zanim cokolwiek wepniesz",
    "Wszystkie próby wpinania wykonuj przy <b>wyłączonym bezpieczniku</b>. Złącza są kluczowane: właściwe gniazdo przyjmuje wtyk bez użycia siły. Jeżeli wtyk nie wchodzi lekko \u2014 to nie jest to gniazdo. Nigdy nie wpinaj bramki w czerwone gniazdo DC-MOTOR (zasilanie silnika). Nie zdejmuj zworki JUMP i nie odłączaj kabla z DOOR-C."))

# ── 5. Pinouty ────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(P("5. Za co odpowiadają poszczególne żyły \u2014 pinouty", "h1"))
story.append(P("Poniżej komplet wiedzy o trzech kablach/portach, z wyraźnym podziałem na fakty potwierdzone dokumentacją i na ustalenia społecznościowe (inżynieria wsteczna). Tam, gdzie producent niczego nie publikuje, napisane jest to wprost \u2014 zgadywanie pinów przy podłączonym zasilaniu kończy się spaleniem modułu."))

story.append(P("5.1. Bramka SMG-01 \u2014 zaciski L1 (A, A, B, B)", "h2"))
story.append(tbl(
    ["Zacisk", "Funkcja", "Status wiedzy"],
    [
        ["A, A", "Linia A (D+) magistrali RS485; dwa zaciski zwarte wewnętrznie \u2014 jeden przyjmuje magistralę, drugi prowadzi ją dalej, do następnej bramki", "potwierdzone (instrukcja)"],
        ["B, B", "Linia B (D\u2212) magistrali RS485; analogicznie zdublowana", "potwierdzone (instrukcja)"],
        ["ekran kabla", "Podłączyć do masy obudowy w <b>jednym</b> punkcie magistrali (najlepiej przy skrajnej jednostce)", "potwierdzone (instrukcja TD metal)"],
    ],
    [2.6 * cm, 11.2 * cm, 3.2 * cm],
))
story.append(Spacer(1, 3))
story.append(B("Kabel: ekranowana skrętka 2-żyłowa, 0,2\u20130,32 mm\u00B2 (AWG 24\u201322), np. BELDEN 3016A."))
story.append(B("Topologia: wyłącznie szeregowa (bus). Gwiazda i pierścień są zabronione."))
story.append(B("Długość: do 500 m (wg TD metal); instrukcja Gree dopuszcza więcej z repeaterem optoizolowanym powyżej 800 m."))
story.append(B("Terminacja: rezystor 120 \u03A9 między A i B na obu skrajnych urządzeniach magistrali."))

story.append(P("5.2. Bramka SMG-01 \u2014 kabel L2 (6-żyłowy, czerwony wtyk)", "h2"))
story.append(P("Kabel fabrycznie zakończony z obu stron: czerwony wtyk 6-pin do gniazda <b>COM-BMS</b> na płycie głównej jednostki, drugi koniec do gniazda <b>UNIT</b> w bramce. Prowadzi <b>zasilanie bramki</b> (bramka nie ma własnego zasilacza \u2014 czerwona dioda świeci po podaniu zasilania z jednostki) oraz <b>łącze danych</b> między procesorem jednostki a bramką. W Twoim egzemplarzu widoczne żyły: czerwona, czarna, pomarańczowa, brązowa, żółta, biała."))
story.append(warn("Znaczenie poszczególnych żył L2 nie jest publikowane",
    "Ani Gree, ani Sinclair, ani TD metal nie publikują rozpisu pin-po-pinie kabla L2. Nie jest on do niczego potrzebny przy prawidłowym montażu \u2014 wtyk jest kluczowany i pasuje wyłącznie do COM-BMS. <b>Nie rozszywać kabla i nie podawać napięć z zasilacza laboratoryjnego</b> \u2014 to najprostszy sposób na spalenie bramki, za którą nie ma publicznej dokumentacji serwisowej."))

story.append(P("5.3. Moduł WiFi GRJWB04-J \u2014 kabel 4-żyłowy (niebieski wtyk)", "h2"))
story.append(tbl(
    ["Linia", "Funkcja", "Status wiedzy"],
    [
        ["+5 V", "Zasilanie modułu z jednostki", "inż. wsteczna społeczności (zamiennik open-source)"],
        ["GND", "Masa", "jw."],
        ["TX", "Dane: moduł \u2192 jednostka, UART", "jw."],
        ["RX", "Dane: jednostka \u2192 moduł, UART", "jw."],
    ],
    [2.6 * cm, 11.2 * cm, 3.2 * cm],
))
story.append(Spacer(1, 3))
story.append(B("Parametry UART: <b>4800 bps, 8 bitów danych, 1 bit stopu, parzystość EVEN</b>; ramki zaczynają się od 7E 7E (ustalenia projektu zamiennika open-source: esphome_gree_ac)."))
story.append(B("Mapowanie kolorów żył na piny nie jest publikowane \u2014 w razie potrzeby ustalać wyłącznie przy odłączonym zasilaniu, śledząc ścieżki od wtyku."))
story.append(B("Przeznaczenie: gniazdo \u201EWIFI\u201D splitów ściennych Gree (Bora, Pular, Amber itp.). W kasetonie GKH brak takiego gniazda \u2014 moduł odkładamy do ewentualnych jednostek ściennych."))

story.append(P("5.4. Port COM-MANUAL (sterownik przewodowy) \u2014 4 piny", "h2"))
story.append(tbl(
    ["Pin", "Funkcja", "Status wiedzy"],
    [
        ["GND", "Masa", "dokumentacja społecznościowa protokołu (gree-wired-proto)"],
        ["+12 V", "Zasilanie sterownika przewodowego", "jw."],
        ["A", "RS485 linia A", "jw.; obok gniazda na płycie siedzi transceiver RS-485 (MAX130xx \u2014 odczyt z fotografii), co potwierdza magistralę różnicową"],
        ["B", "RS485 linia B", "jw."],
    ],
    [2.6 * cm, 11.2 * cm, 3.2 * cm],
))
story.append(Spacer(1, 3))
story.append(B("Parametry: <b>1200 bps, 8N1</b>, ramki 7E 7E + adresy (00 = sterownik, FF = jednostka, 40 = prawdopodobnie sterownik centralny) + suma XOR \u2014 wg dokumentacji społecznościowej dla sterownika XK19."))
story.append(B("<b>ZWERYFIKOWANE SONDĄ:</b> jednostka <b>rozgłasza</b> ramkę stanu co 800 ms niezależnie od nas (kanoniczna ramka i parametry w rozdz. 8). Na ramki wysyłane przez nas <b>nie reaguje</b> — patrz FAZA2_USTALENIA."))

# ── 6. Iteracje ───────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(P("6. Iteracje projektowe \u2014 pomysł, krytyka, wniosek", "h1"))
story.append(P("Zgodnie z zamówieniem: każdy pomysł przechodzi rundę krytycznej analizy, a wnioski z niej budują kolejną iterację.", "iterlead"))

story.append(P("Iteracja 1 \u2014 moduł WiFi w każdej jednostce + integracja \u201Egree\u201D w HA", "h2"))
story.append(P("<b>Pomysł:</b> do każdego kasetonu wpiąć moduł GRJWB04-J, sparować aplikacją GREE+, a Home Assistant wykryje jednostki wbudowaną integracją gree (lub komponentem \u201EGree A/C\u201D z HACS, który pozwala podać adres IP ręcznie \u2014 istotne przy HA w kontenerze Docker, gdzie wykrywanie rozgłoszeniowe nie działa)."))
story.append(P("<b>Krytyka:</b> (1) na płycie GRZ4M-A3 nie ma gniazda dla tego modułu \u2014 potwierdzone fizycznie (wtyk nigdzie nie pasuje) i schematem (żaden port WiFi nie występuje); (2) moduł jest projektowany dla splitów ściennych \u2014 nawet identyczna nazwa modelu nie gwarantuje zgodności między rodzinami; (3) przy wielu jednostkach koszt rośnie liniowo, a każda jednostka wisi osobno na WiFi \u2014 najmniej niezawodnym medium w tym zestawieniu."))
story.append(P("<b>Wniosek:</b> odrzucone dla kasetonów. Moduł zachować \u2014 znajdzie zastosowanie, jeżeli w budynku są ścienne jednostki Gree (tam wpina się w gniazdo WIFI i działa z integracją gree)."))

story.append(P("Iteracja 2 \u2014 nadajniki podczerwieni (ESPHome climate_ir)", "h2"))
story.append(P("<b>Pomysł:</b> przy każdym kasetonie nadajnik IR (ESP32 + dioda), ESPHome ma gotowy profil klimatyzatorów Gree; HA dostaje encję climate od ręki."))
story.append(P("<b>Krytyka:</b> (1) komunikacja jednokierunkowa \u2014 HA nie zna rzeczywistego stanu; każdy pilot ręczny lub zanik zasilania rozjeżdża stan; (2) wymóg linii widzenia do panelu; (3) pilot Gree wysyła zawsze komplet nastaw, więc nie ma zmiany pojedynczego parametru; (4) użytkownik jednoznacznie wymaga toru dwukierunkowego (\u201Echcę mieć wyjście i wejście\u201D)."))
story.append(P("<b>Wniosek:</b> odrzucone jako samodzielne rozwiązanie docelowe, ale <b>wraca do gry po ustaleniach z 2026-08-25</b>. Skoro jednostka ignoruje nasze ramki na COM-MANUAL, podczerwień jest dziś jedyną dostępną drogą zapisu. Zarzut (1) — brak wiedzy o rzeczywistym stanie — znika, gdy IR odpowiada za sterowanie, a sonda na COM-MANUAL za bierny odczyt stanu faktycznego. Taki układ hybrydowy daje pełny tor dwukierunkowy bez rejestracji sterownika."))

story.append(P("Iteracja 3 \u2014 własny mostek ESP32 na porcie COM-MANUAL", "h2"))
story.append(P("<b>Pomysł:</b> port COM-MANUAL istnieje w każdej jednostce na pewno i jest wolny. 4 żyły dają zasilanie 12 V i magistralę RS485 (1200 bps). ESP32 + transceiver RS485 (~40\u201360 zł/szt.) udaje sterownik przewodowy i mostkuje do HA (ESPHome/MQTT), zasilając się wprost z portu."))
story.append(P("<b>Krytyka:</b> (1) publiczna dokumentacja protokołu dotyczy sterownika XK19 \u2014 zgodność ramek z tą jednostką trzeba najpierw potwierdzić nasłuchem; (2) brak gotowej implementacji \u2014 to projekt inżynierski (tygodnie), nie weekendowy; (3) <b>kolizja zasobów: ten sam port będzie potrzebny dla XK117 przy ścieżce Modbus</b>, a jeśli okaże się, że istniejący sterownik centralny działa po tej właśnie magistrali (adres 40 w protokole!), dołożenie własnego urządzenia grozi konfliktem; (4) N jednostek = N urządzeń DIY do zbudowania, wgrania i serwisowania \u2014 skala działa przeciw temu pomysłowi."))
story.append(P("<b>Wniosek:</b> technicznie realne i najtańsze per sztuka, ale słabo skalowalne i obarczone pracą badawczą. Sensowne jako plan B, gdy zawiedzie weryfikacja COM-BMS z iteracji 4, albo dla 1\u20132 jednostek."))

story.append(P("Iteracja 4 \u2014 bramki SMG-01 + wspólna magistrala Modbus + HA", "h2"))
story.append(P("<b>Pomysł:</b> w każdej jednostce bramka SMG-01 wpięta kablem L2 w COM-BMS; wszystkie bramki spięte przelotowo jedną skrętką (zaciski A/B); na końcu magistrali mostek RS485\u2192LAN (np. Elfin EW11); HA rozmawia po Modbus RTU-over-TCP wbudowaną integracją modbus \u2014 encje climate/sensor per jednostka według mapy rejestrów. Jedna magistrala obsłuży wszystkie kasetony w budynku (limit 255)."))
story.append(P("<b>Krytyka:</b> (1) <b>fakt bramkujący: obecność gniazda COM-BMS na płycie A3 nie została potwierdzona</b> \u2014 instrukcja pokazuje je na siostrzanej płycie A6 (U-Match: kanałowe, kasetonowe, przypodłogowe), a Sinclair pozycjonuje SMG-01 do serii UNI SPLIT; Twoje kasetony to Free Match \u2014 rodziny są blisko spokrewnione (wspólna płyta GRZ4M), ale to wymaga oględzin lub pytania do dystrybutora; (2) wymagany XK117 do aktywacji (parametr 10 \u2192 01) i adresowania \u2014 dodatkowy zakup; do potwierdzenia, czy jeden XK117 można przenosić między jednostkami na czas komisjonowania; (3) mapa rejestrów tylko u dystrybutora \u2014 bez niej konfiguracja HA stoi; parametry transmisji (zapewne 9600 8N1, jak w innych bramkach Gree) też do potwierdzenia w tym dokumencie; (4) <b>jeden master:</b> jeżeli \u201Ejednostka centralna\u201D to sterownik centralny Modbus, nie może odpytywać magistrali równolegle z HA \u2014 trzeba wybrać architekturę (HA przejmuje wszystko, sterownik zostaje odłączony lub na osobnej magistrali z osobnymi bramkami); (5) okablowanie: skrętka musi przejść szeregowo przez wszystkie jednostki \u2014 praca w sufitach, choć jednorazowa; (6) koszt bramek \u00D7 N \u2014 do wyceny u dystrybutora (cen publicznych brak)."))
story.append(P("<b>Wniosek:</b> najlepsza ścieżka docelowa \u2014 fabryczne komponenty, standardowy protokół, natywna integracja w HA, jedna magistrala zamiast N osobnych łączy. Całość warunkowana punktem (1), dlatego plan wdrożenia zaczyna się od weryfikacji, a nie od zakupów."))

story.append(P("Iteracja 5 \u2014 synteza: drzewo decyzyjne", "h2"))
story.append(tbl(
    ["Pytanie weryfikacyjne", "Odpowiedź \u2192 decyzja"],
    [
        ["P1. Czym jest \u201Ejednostka centralna\u201D? (zdjęcie tabliczki znamionowej)",
         "Sterownik centralny na Modbus (np. SCC-16/36) \u2192 magistrala i bramki mogą już istnieć w budynku; HA albo przejmuje rolę mastera (sterownik odłączany), albo pytamy dystrybutora o wariant sterownika z własnym interfejsem IP, z którym HA rozmawia zamiast z magistralą. Tylko jednostka zewnętrzna / sterownik na innym medium \u2192 budujemy magistralę od zera wg iteracji 4."],
        ["P2. Czy na płycie GRZ4M-A3 jest gniazdo COM-BMS? (oględziny rozstrzygni\u0119te ni\u017cej)",
         "Jest \u2192 iteracja 4 (pilot na 1 jednostce, potem skala). Nie ma \u2192 pytanie do dystrybutora o bramkę dla Free Match / adapter; jeśli brak rozwiązania fabrycznego \u2192 iteracja 3 (DIY na COM-MANUAL) lub \u2014 punktowo \u2014 iteracja 2."],
        ["P3. Ile jednostek i jakich typów jest w budynku?",
         "Wszystkie kasetonowe/kanałowe z rodziny GRZ4M \u2192 jedna wspólna magistrala. Są też ścienne Gree \u2192 dla nich GRJWB04-J + integracja gree (moduł już jest); nie mieszać tych ścieżek na siłę \u2014 obie kończą się encjami climate w tym samym HA."],
    ],
    [6.2 * cm, 10.8 * cm],
))
story.append(Spacer(1, 5))
story.append(ok("Rozstrzygni\u0119cie (2026-08-22)",
    "P1: wsp\u00f3lnego sterownika nie ma \u2014 HA b\u0119dzie pierwszym masterem. P2: gniazda COM-BMS na p\u0142ycie A3 <b>nie ma</b> \u2014 iteracja 4 upada. Wygra\u0142a <b>iteracja 3</b> (w\u0142asny mostek na COM-MANUAL), zrealizowana bez zakup\u00f3w: rol\u0119 uk\u0142adu RS485 pe\u0142ni przerobiona bramka, rol\u0119 mostka \u2014 WeMos D1 R1. Szczeg\u00f3\u0142y w dw\u00f3ch kolejnych rozdzia\u0142ach."))

# -- 7. Studium przypadku --
story.append(PageBreak())
story.append(P("7. Studium przypadku — droga do działającej sondy", "h1"))
story.append(P("Skrót przebiegu diagnozy z ciągiem przyczynowo-skutkowym. Pełna wersja z detalami: <b>STUDIUM_PRZYPADKU.md</b> w folderze projektu. Każdy etap ma trzy elementy: co obserwowaliśmy, jaka była rzeczywista przyczyna i co ją usunęło."))
story.append(tbl(
    ["Etap", "Objaw", "Ustalona przyczyna", "Rozwiązanie"],
    [
        ["1", "Sonda przy jednostce nadaje, ale przez wiele sesji nie odbiera ani bajta; pomiary przy gnieździe dają niefizyczne −7 V",
         "Pomiar dotyczył „pływających” (niepodłączonych) przewodów — sygnał w ogóle nie krążył w torze",
         "Zmiana metody: diagnostyka przeniesiona na biurko, tor rozłożony na odcinki, każdy weryfikowany osobno multimetrem i firmwarem testowym"],
        ["2", "Firmware raportuje wysyłkę, ale bramka nie dostaje ani bita",
         "Przewody sygnałowe siedziały na pinach RX←D0/TX→D1 (port zajęty przez USB), a firmware nadaje na innych — winne <b>potrójne, powtarzające się opisy pinów</b> płytki D1 R1",
         "Przewody przepięte na piny wg pełnego nadruku: D12/MISO/D6 (nadawanie) i D13/SCK/D5 (odbiór przez dzielnik)"],
        ["3", "Tester biurkowy: bramka wciąż nie wystawia żadnego napięcia na blaszki (różnica ~0 V)",
         "Układ RS485 bramki (14-pin, rodzina MAX13089) <b>nie ma automatu kierunku</b> — nadajnik i odbiornik włącza płyta główna żyłami RXP/TXP, które u nas wisiały w powietrzu (bramka głucha i niema jednocześnie)",
         "RXP (biała) na stałe do masy = odbiór włączony; TXP (żółta) pod pin D11/MOSI/D7 = klucz nadawania podnoszony tylko na czas ramki"],
        ["4", "Kierunek działa, a echo testów dalej martwe",
         "Opisy „TXD/RXD” na laminacie bramki są <b>z perspektywy klimatyzatora</b>: „TXD” to wejście bramki, „RXD” — wyjście; podłączenie intuicyjne było odwrotne",
         "Zamiana dwóch końcówek w złączu krosowym — połączenie „na wprost” (D6 → „TXD”, „RXD” → D5)"],
        ["5", "—", "—",
         "Weryfikacja każdego toru przy biurku: nadajnik ±4,8 V na szynach; odbiornik czyta wymuszoną polaryzację; blaszki X1+X3 = linia A, X2+X4 = linia B (pary przelotowe)"],
        ["6", "—", "—",
         "Powrót na jednostkę: sonda odbiera ciągły strumień rozgłoszeń nadawanych przez jednostkę co 800 ms (91% z poprawną sumą kontrolną; reszta to ucięte odbiory programowego portu szeregowego), pilot podczerwieni działa równolegle"],
    ],
    [1.1 * cm, 4.5 * cm, 6.3 * cm, 5.1 * cm],
))
story.append(Spacer(1, 4))
story.append(info("Metodologia, która przełamała impas",
    "Dwa proste narzędzia: <b>tester biurkowy</b> (firmware zamieniający ramki na powolne stany mierzalne zwykłym multimetrem — zmiana co 1 s, raport wejścia co 1 s) oraz <b>programator ALIENTEK użyty jako bierny rozgałęźnik</b> do testów ciągłości wtyczki. Ta kombinacja pozwoliła zweryfikować każdy odcinek toru bez wchodzenia na drabinę i bez udziału klimatyzatora. Dokumentacja użytych płytek: folder plytki\\."))

# -- 8. Zweryfikowana konfiguracja --
story.append(PageBreak())
story.append(P("8. Zweryfikowana konfiguracja połączenia", "h1"))
story.append(P("Kompletna, działająca konfiguracja — rysunek: <b>schematy\\schemat_FINALNY_dzialajacy.png</b>. Każde połączenie ma swój powód:"))
story.append(tbl(
    ["Połączenie", "Po co"],
    [
        ["WeMos 5V → złącze CN2 +5V (żyła czerwona); wspólna masa", "Zasilanie układów bramki (nie ma własnego zasilacza)"],
        ["WeMos D12/MISO/D6 → żyła „TXD”", "Nadawanie: dane z sondy do wejścia bramki (nazwa „TXD” jest z perspektywy klimatyzatora — stąd połączenie „na wprost”)"],
        ["Żyła „RXD” → rezystor 3,3 kΩ → WeMos D13/SCK/D5; z węzła rezystor 6,5 kΩ do masy", "Odbiór: wyjście bramki pracuje na 5 V, a ESP8266 znosi 3,3 V — dzielnik obniża napięcie w bezpiecznej proporcji"],
        ["WeMos GND → żyła RXP (biała)", "Włącznik odbiornika bramki (aktywny przy masie) — odbiór na stałe"],
        ["WeMos D11/MOSI/D7 → żyła TXP (żółta)", "Włącznik nadajnika — firmware podnosi go wyłącznie na czas wysyłania ramki (magistrala jest wspólna dla obu kierunków)"],
        ["Blaszka X1 (linia A) → konektor czarny → pigtail → pin A gniazda; blaszka X2 (linia B) → konektor czerwony → pin B", "Magistrala RS485 do jednostki; pary blaszek X1+X3 i X2+X4 są zwarte wewnętrznie (do łączenia przelotowego)"],
        ["Żółta żyła pigtaila → GND WeMosa", "Masa wspólna z klimatyzatorem — bez niej magistrala nie ma punktu odniesienia"],
        ["Biała żyła pigtaila (+12 V z gniazda)", "<b>ZAIZOLOWANA, niepodłączona</b> — patrz rozdz. 9"],
    ],
    [8.2 * cm, 8.8 * cm],
))
story.append(Spacer(1, 4))
story.append(P("Parametry potwierdzone pomiarami i logiem", "h2"))
story.append(B("Magistrala: 1200 bodów, 8 bitów danych, bez parzystości, 1 bit stopu; ramki zaczynają się od 7E 7E; ostatni bajt = suma XOR wszystkich poprzednich."))
story.append(B("Nadajnik bramki: ±4,8 V różnicy między liniami A–B (pomiar multimetrem przy przechodzącym sygnale testowym)."))
story.append(B("Ramka testowa sondy, wysyłana co 3 s: 7E 7E 00 FF 11 0E 00 00 02 01 89 8A BE 47 00 80 00 00 00 99 — <b>jednostka jej nie potwierdza</b>. Po całkowitym wyłączeniu naszego nadawania ruch na magistrali płynie bez żadnej zmiany, co rozstrzyga, że odczyt jest biernym podsłuchem rozgłoszeń, a nie dialogiem."))
story.append(code("""Rozgloszenie jednostki (nadawane samoczynnie co 800 ms, niezaleznie od nas, suma XOR poprawna):
7E 7E FF 40 11 17 | 09 30 83 7C 7C 0E 04 00 00 01 00 10 00 00 00 00 00 00 00 00 23 02 | 39
naglowek: FF = nadawca (jednostka)   40 = adresat   11 = kierunek (nadrzedny->podrzedny;
          0x01 znaczyloby podrzedny->nadrzedny)   17h = 23 bajty danych
w danych zmieniaja sie TYLKO 4 bajty (reszta jest stala):
  [9]  temperatura powietrza powrotnego (czujnik ROOM, przy suficie)
  [10] temperatura wymiennika (czujnik TUBE)
  [12] rzeczywisty bieg wentylatora: 00 stoi / 04 niski / 02 sredni / 01 wysoki
  [14] klapy nawiewu: bit 0x80 otwarte, 00 zamkniete
kalibracja temperatury: surowy bajt minus 100 = stopnie C
NASTAW (temperatura zadana, tryb, wl/wyl) W TEJ RAMCE NIE MA - dawna hipoteza
"bajt 23h = nastawa 23 st. C" ZOSTALA OBALONA, ten bajt jest staly"""))
story.append(B("Zdalny dostęp do sondy: rozgłoszenia UDP „SONDA-GREE (adres IP)” na porcie 4210 co 2 s oraz serwer telnet na porcie 23 (po połączeniu zrzuca historię i streamuje na żywo). Log sesji: test_com_manual\\log_sondy.txt."))

# -- 9. Incydent zasilania --
story.append(P("9. Incydent zasilania: +12 V z portu blokowało start jednostki", "h1"))
story.append(P("<b>Przebieg:</b> przed uruchomieniem sondy podjęto próbę zasilenia płytki WeMos wprost z pinu +12 V gniazda COM-MANUAL (biała żyła pigtaila → wejście VIN). Skutek: <b>klimatyzator w ogóle nie startował</b>, mimo że na zasilaniu było 230 V (pomiar miernikiem). Zweryfikowano dwukrotnie, włączając i wyłączając bezpiecznik — wynik powtarzalny. Po odłączeniu żyły jednostka startowała normalnie."))
story.append(P("<b>Wyjaśnienie mechanizmu:</b> pin +12 V to wyjście małego zasilacza wewnętrznego jednostki — <b>tego samego, który zasila jej własną elektronikę sterującą</b>. Producent przewidział go dla drobnego odbiornika (przewodowy pilot pobiera kilkadziesiąt miliamperów). Wejście VIN WeMosa to natomiast przetwornica impulsowa z kondensatorami na wejściu — obciążenie wyjątkowo wrogie w momencie włączania prądu, z dwóch powodów:"))
story.append(B("<b>Prąd rozruchowy:</b> rozładowane kondensatory w pierwszej chwili zachowują się niemal jak zwarcie — pobierają duży prąd, zanim się naładują."))
story.append(B("<b>Charakter „stałej mocy”:</b> przetwornica utrzymuje moc wyjściową, więc im niższe napięcie na wejściu, tym większy prąd pobiera. Gdy zasilacz jednostki startuje „miękko” (napięcie narasta od zera), przetwornica przy niskim napięciu żąda prądu największego — dokładnie wtedy, gdy zasilacz może dać najmniej."))
story.append(P("Zabezpieczenie nadprądowe zasilacza wykrywa przeciążenie i restartuje próbę startu w nieskończonej pętli (tzw. tryb czkawki). Napięcie nigdy nie osiąga wartości roboczej, elektronika sterująca jednostki nie dostaje zasilania — <b>cały klimatyzator wygląda na martwy, choć z sieci płynie 230 V</b>. To nie usterka, lecz prawidłowe działanie ochrony: po zdjęciu obciążenia wszystko wróciło do normy, a późniejszy sukces sondy potwierdził, że ani jednostka, ani płytka nie ucierpiały."))
story.append(warn("Wniosek obowiązujący na stałe",
    "Sondy/mostka <b>nie zasilamy wprost z pinu +12 V portu COM-MANUAL</b> — ani przy starcie, ani „na gorąco”. Wersja obowiązująca i bezpieczna: własny zasilacz 5 V (ładowarka USB), biała żyła pigtaila zaizolowana. Wariant badany (montaż odłożony przez użytkownika, sprawa niezamknięta): miękki start z +12 V przez rezystor szeregowy <b>25–28 Ω</b> (np. 4 × 100 Ω równolegle) i <b>3 × 100 µF</b> na wejściu. Wariant z rezystorem <b>47 Ω zawiódł</b> — przegrzewanie rezystora i brak startu sondy — i nie wolno go stosować."))

# -- 10. Ulepszenia i wdrozenie --
story.append(PageBreak())
story.append(P("10. Propozycje ulepsze\u0144 i plan wdro\u017cenia na pozosta\u0142e jednostki", "h1"))
story.append(P("Sonda udowodniła wykonalność, ale jest prototypem z odzysku. Docelowe wdrożenie na wiele jednostek powinno być prostsze, tańsze i powtarzalne:"))
story.append(tbl(
    ["Obszar", "Propozycja", "Uzasadnienie"],
    [
        ["Konwerter RS485", "Zamiast dużej bramki — popularny moduł <b>MAX485</b> (ok. 4–5 zł za sztukę)",
         "Identyczna funkcja, ułamek rozmiaru; sygnał kierunku już obsługiwany w firmware (pin D7); bramka wraca do szuflady jako zapas"],
        ["Płytka sterująca", "ESP32 (lub D1 mini) zamiast WeMos D1 R1",
         "ESP32 ma sprzętowe porty szeregowe — zniknie ~9% uciętych ramek programowego odbioru przy działającym WiFi; mniejsza płytka łatwiej mieści się przy jednostce"],
        ["Zasilanie", "Ładowarka USB 5 V przy każdej jednostce",
         "Wniosek z incydentu +12 V (rozdz. 9); ładowarka 5 V / 1 A wystarcza z dużym zapasem. Wariant bez osobnego zasilacza (miękki start z +12 V przez 25–28 Ω i 3 × 100 µF) jest zbadany, ale nie zmontowany — do rozstrzygnięcia przed replikacją na wiele jednostek"],
        ["Okablowanie", "Gotowe fabryczne kable z wtyczką JST zamiast ciętych i lutowanych; żyły opisane; jedna kartka dokumentacji na jednostkę",
         "Prototypowa wiązka była źródłem większości przestojów diagnostycznych"],
        ["Oprogramowanie", "Etap 1 (WYKONANY): dekodowanie pól — ustalone 4 zmienne pola i kalibracja „surowy bajt minus 100”. Etap 2 (WYKONANY): firmware v5 z serwerem HTTP /stan, 5 encji REST w Home Assistant, aktualizacja przez WiFi (OTA). Etap 3 (OTWARTY): sterowanie — albo rejestracja jako sterownik przewodowy (droga nierozpoznana), albo tor podczerwieni ESPHome climate_ir sprzężony z odczytem z sondy",
         "Odczyt jest gotowy, przetestowany i wystawiony po HTTP — nie wymaga żadnych zmian sprzętowych. Brakującym elementem jest wyłącznie zapis: jednostka odrzuca ramki od niezarejestrowanego sterownika, więc sterowanie musi pójść inną drogą"],
        ["Architektura", "Zbadać, czy jedna sonda nasłuchowa obsłuży kilka jednostek na wspólnej magistrali (rozgłoszenie każdej jednostki idzie samoczynnie do adresu 40 — puli „sterownika centralnego”, więc bierny odbiornik nie generuje ruchu i nie może wejść w konflikt)",
         "Gdyby tak — jedna skrętka i jeden mostek na grupę jednostek zamiast mostka przy każdej; wymaga eksperymentu na dwóch jednostkach"],
    ],
    [2.8 * cm, 6.6 * cm, 7.6 * cm],
))
story.append(Spacer(1, 5))
story.append(P("Kolejność wdrożenia", "h2"))
story.append(B("<b>Krok 1 (WYKONANY):</b> dekodowanie pól protokołu na działającej sondzie — ustalone 4 zmienne pola, kalibracja temperatury „surowy bajt minus 100”, potwierdzony brak nastaw w rozgłoszeniu."))
story.append(B("<b>Krok 2 (WYKONANY w zakresie odczytu):</b> firmware v5 serwuje stan po HTTP (/stan), Home Assistant czyta go pięcioma encjami REST; aktualizacja idzie po WiFi (OTA). Pozostaje test stabilności przez kilka dni na jednostce pilotażowej."))
story.append(B("<b>Krok 3:</b> szablon sprzętowy (płytka + MAX485 + kabel z wtyczką + ładowarka) i replikacja na kolejne jednostki; każda dostaje nazwę i wpis w Home Assistant."))
story.append(B("<b>Krok 4:</b> dokumentacja powykonawcza na jednostkę (zdjęcie montażu, adres IP, encje) w folderze projektu."))

# ── 9. Bezpieczeństwo ────────────────────────────────────────────────────
story.append(PageBreak())
story.append(P("10a. Faza 2: co ustaliło dalsze badanie protokołu (2026-08-25)", "h1"))
story.append(P("Rozdział dopisany po tygodniu badań protokołu. <b>Rewiduje jedno z głównych twierdzeń wcześniejszej wersji raportu</b> — zostaje tu świadomie, bo droga do prawdy jest częścią dokumentacji."))
story.append(warn("Sprostowanie",
    "Wcześniejsza wersja raportu głosiła, że <b>jednostka odpowiada na każdą ramkę</b> sondy. To było błędne. Jednostka <b>nadaje swój stan sama</b>, równo co 800 ms, do adresu 40 — niezależnie od tego, czy ktokolwiek o cokolwiek pyta. Dowód: po całkowitym wyłączeniu naszych zapytań ruch na magistrali płynie dalej bez zmian. Nasza „komunikacja dwukierunkowa” była <b>biernym podsłuchem</b>."))
story.append(P("Próby nawiązania dialogu — wyczerpujące i bezskuteczne", "h2"))
story.append(tbl(
    ["Co przetestowano", "Zakres"],
    [
        ["ramka zapytania wg dokumentacji sterownika XK19", "wielokrotnie, także powtórzenia seriami"],
        ["pełny przemiat bajtu rozkazu", "wszystkie 256 wartości"],
        ["pola nagłówka: nadawca / adresat / klasa ramki", "768 kombinacji"],
        ["„puls obecności” z identyfikatorem płyty", "48 wariantów"],
        ["taktowanie: precyzyjne bity, dłuższe trzymanie klucza nadawania", "firmware v4"],
        ["synchronizacja do okna po ramce jednostki", "30 / 60 / 150 / 300 ms"],
        ["podszycie się pod sterownik centralny, lustro własnej ramki jednostki", "kilka wariantów"],
    ],
    [9.5 * cm, 7.5 * cm],
))
story.append(Spacer(1, 4))
story.append(P("<b>Łącznie ponad 1100 wariantów ramek — ani jednej odpowiedzi.</b> Tor nadawania jest sprawny elektrycznie (polaryzacja potwierdzona poprawnym odbiorem, ±4,8 V zmierzone, suma kontrolna ramki wzorcowej przeliczona ręcznie). Jednostka <b>ignoruje nas programowo</b>, bo nie jesteśmy zarejestrowanym sterownikiem. Nastawy jeżdżą w ramce FF→00, której jednostka nie wysyła, dopóki sterownik pod adresem 00 nie zostanie zarejestrowany — to potwierdziło też rozpoznanie cudzych implementacji."))
story.append(P("Co z tego działa i jest dostarczone", "h2"))
story.append(B("<b>Odczyt czterech pól</b> odświeżanych co 800 ms: temperatura powietrza powrotnego, temperatura wymiennika, rzeczywisty bieg wentylatora, stan klap nawiewu."))
story.append(B("<b>Przelicznik temperatur potwierdzony</b>: surowy bajt minus 100 = stopnie Celsjusza (dowód w osobnym dokumencie KALIBRACJA_TEMPERATUR)."))
story.append(B("<b>Integracja z Home Assistant</b>: sonda serwuje stan po HTTP, gotowa konfiguracja pięciu encji REST (HA_INTEGRACJA_ODCZYT)."))
story.append(B("<b>Aktualizacja firmware przez WiFi</b> — koniec wgrywania po kablu."))
story.append(P("Drogi do sterowania — stan otwarty", "h2"))
story.append(B("<b>Rejestracja przy rozruchu płyty</b>: sonda woła co 500 ms, przełączamy bezpiecznik, nagrywamy start od pierwszej milisekundy. Wyłączenie pilotem nie wystarczy — to tylko czuwanie."))
story.append(B("<b>Pobór prądu z linii +12 V</b> jako sygnał obecności sterownika — prawdziwy pilot przewodowy zasila się z portu, nasza sonda nie. Jeśli hipoteza się potwierdzi, układ zasilający okaże się warunkiem komunikacji."))
story.append(B("<b>Hybryda: podczerwień do zapisu + magistrala do odczytu.</b> Odrzucając niegdyś podczerwień, głównym zarzutem był brak wiedzy o rzeczywistym stanie. Ten zarzut właśnie zniknął: stan odczytujemy z magistrali. Podczerwień odpowiadałaby wyłącznie za wydawanie poleceń — i daje pełny tor dwukierunkowy bez rejestracji sterownika."))
story.append(Spacer(1, 6))

story.append(P("11. Zasady bezpieczeństwa", "h1"))
story.append(B("Każda ingerencja w skrzynkę elektryczną wyłącznie przy odłączonym zasilaniu (bezpiecznik, nie pilot). W skrzynce jest 230 V, a gniazdo DC-MOTOR prowadzi napięcie zasilania silnika."))
story.append(B("Czynnik R32 jest palny: przy jednostce nie używać otwartego ognia ani narzędzi iskrzących; naklejka wymaga pomieszczenia \u2265 4 m\u00B2."))
story.append(B("Wtyki kluczowane wpinać bez siły; opór = złe gniazdo. Nie rozszywać fabrycznych kabli L2 i kabla modułu WiFi."))
story.append(B("Nie zdejmować zworki JUMP (kodowanie modelu) i nie odłączać DOOR-C \u2014 jednostka może przestać pracować."))
story.append(B("<b>Nigdy nie zasila\u0107 sondy/mostka z pinu +12 V portu COM-MANUAL</b> \u2014 blokuje start jednostki (rozdz. 9); wy\u0142\u0105cznie w\u0142asny zasilacz 5 V."))
story.append(B("Wtyczk\u0119 z gniazda COM-MANUAL wpina\u0107/wypina\u0107 tylko przy wy\u0142\u0105czonym bezpieczniku; zmiany po stronie bramki (blaszki, z\u0142\u0105cze krosowe) s\u0105 bezpieczne przy pracuj\u0105cej jednostce."))
story.append(B("Na magistrali RS485 zachować topologię szeregową, terminację 120 \u03A9 na końcach i ekran uziemiony w jednym punkcie \u2014 to warunek stabilnej komunikacji, nie kosmetyka."))

# ── 10. Źródła ───────────────────────────────────────────────────────────
story.append(P("12. \u0179r\u00f3d\u0142a i dokumentacja towarzysz\u0105ca", "h1"))
srcs = [
    "Dokumentacja projektu (ten folder): STUDIUM_PRZYPADKU.md \u2022 plytki\\wemos_d1_r1.md \u2022 plytki\\bramka_grz47_smg01.md \u2022 plytki\\flasher_alientek_minipro.md \u2022 schematy\\schemat_FINALNY_dzialajacy.png \u2022 test_com_manual\\PROCEDURA_TESTU.md",
    "Instrukcja bramki (Gree Gateway Kit / Sinclair SMG-01), EN \u2014 kopia w folderze: instrukcje\\Sinclair_SMG-01_Modbus_Gateway_instrukcja_EN.pdf",
    "TD metal: Installation manual \u2014 Modbus Gateway (TD GUD 30/01) for U-Match R32 units \u2014 kopia w folderze: instrukcje\\TDmetal_Modbus_Gateway_U-Match_instalacja_EN.pdf (źródło: gree.at/uploads/navody/modbus_gateway_en.pdf)",
    "Sinclair: karta produktu SMG-01 \u2014 sinclair.pl/oferta/klimatyzatory-split/akcesoria/smg-01.html",
    "Protokół sterownika przewodowego Gree (RS485, 1200 8N1, ramki 7E 7E) \u2014 github.com/maxim-smirnov/gree-wired-proto",
    "Zamiennik open-source modułu WiFi Gree (UART 4800 8E1) \u2014 github.com/gekkehenkie11/esphome_gree_ac oraz wątek community.home-assistant.io \u201EOpen source Gree wifi module replacement\u201D",
    "Komponent HACS \u201EGree A/C\u201D (ręczny adres IP) \u2014 github.com/RobHofmann/HomeAssistant-GreeClimateComponent",
    "Integracja modbus w Home Assistant \u2014 home-assistant.io/integrations/modbus",
    "Integracja gree w Home Assistant \u2014 home-assistant.io/integrations/gree",
    "Karta produktu jednostki \u2014 kirbyhvacr.com.au/product-detail/GKH(12)BB-K6DNA3A/I",
]
for i, s_ in enumerate(srcs, 1):
    story.append(B(f"[{i}] {s_}"))
story.append(Spacer(1, 8))
story.append(P("Dokument przygotowany na podstawie analizy zdjęć instalacji, dwóch instrukcji producenta (kopie w folderze instrukcje\\) oraz źródeł wymienionych wyżej. Pozycje oznaczone jako \u201Edo weryfikacji\u201D lub \u201Einż. wsteczna społeczności\u201D nie są potwierdzone dokumentacją producenta.", "small"))

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.7 * cm, bottomMargin=1.8 * cm,
    title="Integracja klimatyzatorów Gree z Home Assistant",
    author="analiza techniczna",
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("OK:", OUT)
