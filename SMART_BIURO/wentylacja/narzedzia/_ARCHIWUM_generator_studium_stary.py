# -*- coding: utf-8 -*-
"""Generator PDF: STUDIUM_PRZYPADKU.pdf (na bazie STUDIUM_PRZYPADKU.md)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\STUDIUM_PRZYPADKU.pdf"

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Ar", F + r"\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", F + r"\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI", F + r"\ariali.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + r"\cour.ttf"))

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
S["title"] = ParagraphStyle("title", fontName="ArB", fontSize=19, leading=24, textColor=C_DARK, spaceAfter=4)
S["subtitle"] = ParagraphStyle("subtitle", fontName="Ar", fontSize=11, leading=15, textColor=C_GRAY, spaceAfter=2)
S["h1"] = ParagraphStyle("h1", fontName="ArB", fontSize=14, leading=17.5, textColor=C_ACCENT, spaceBefore=15, spaceAfter=7)
S["body"] = ParagraphStyle("body", fontName="Ar", fontSize=10, leading=13.8, textColor=C_DARK, alignment=TA_JUSTIFY, spaceAfter=5)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=14, bulletIndent=4, spaceAfter=3)
S["tcell"] = ParagraphStyle("tcell", fontName="Ar", fontSize=8.8, leading=11.4, textColor=C_DARK)
S["thead"] = ParagraphStyle("thead", fontName="ArB", fontSize=8.8, leading=11.4, textColor=colors.white)
S["boxtitle"] = ParagraphStyle("boxtitle", fontName="ArB", fontSize=9.6, leading=12.5, textColor=C_DARK)
S["boxbody"] = ParagraphStyle("boxbody", fontName="Ar", fontSize=9.3, leading=12.4, textColor=C_DARK, alignment=TA_JUSTIFY)
S["code"] = ParagraphStyle("code", fontName="Mono", fontSize=8.2, leading=10.6, textColor=C_DARK)
S["small"] = ParagraphStyle("small", fontName="Ar", fontSize=8.4, leading=11, textColor=C_GRAY)


def P(t, s="body"):
    return Paragraph(t, S[s])


def B(t):
    return Paragraph(t, S["bullet"], bulletText="\u2013")


def box(title, text, bg, border):
    t = Table([[Paragraph(title, S["boxtitle"])], [Paragraph(text, S["boxbody"])]], colWidths=[17.0 * cm])
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


def tbl(header, rows, widths):
    data = [[Paragraph(h, S["thead"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, S["tcell"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, C_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_ROWALT]),
    ]))
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
    canvas.drawString(2 * cm, 1.1 * cm, "Studium przypadku: sonda COM-MANUAL dla Gree GKH \u2014 2026-08-22")
    canvas.drawRightString(19 * cm, 1.1 * cm, f"strona {doc.page}")
    canvas.setStrokeColor(C_LINE)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, 1.35 * cm, 19 * cm, 1.35 * cm)
    canvas.restoreState()


story = []
story.append(P("Studium przypadku: od \u201Enic nie pasuje\u201D do rozmowy z klimatyzatorem", "title"))
story.append(P("Pe\u0142ny zapis diagnozy sondy COM-MANUAL z ci\u0105giem przyczynowo-skutkowym \u2022 Gree GKH(12)BB-K6DNA3A/I, p\u0142yta GRZ4M-A3 \u2022 sierpie\u0144 2026", "subtitle"))
story.append(P("Dokument towarzyszy g\u0142\u00F3wnemu raportowi (Integracja_klimatyzacji_Gree_z_Home_Assistant.pdf); sprz\u0119t opisany w folderze plytki\\, schemat ko\u0144cowy w schematy\\schemat_FINALNY_dzialajacy.png.", "subtitle"))
story.append(Spacer(1, 8))

story.append(P("Etap 0 \u2014 punkt wyj\u015Bcia i decyzja o sondzie", "h1"))
story.append(P("<b>Problem:</b> kasetony Gree maj\u0105 by\u0107 sterowane z Home Assistant, ale \u017Cadne z posiadanych akcesori\u00F3w nie pasuje: modu\u0142 WiFi GRJWB04-J wymaga gniazda, kt\u00F3rego p\u0142yta GRZ4M-A3 nie ma, a bramka Modbus ZTS47/SMG-01 wymaga gniazda COM-BMS \u2014 kt\u00F3rego ta p\u0142yta r\u00F3wnie\u017C nie ma."))
story.append(P("<b>Ustalenie kluczowe:</b> na p\u0142ycie jest wolny port COM-MANUAL (4 piny: masa, +12 V i dwu\u017Cy\u0142owa magistrala danych RS485) przeznaczony dla przewodowego pilota. Protok\u00F3\u0142 tej magistrali jest cz\u0119\u015Bciowo rozpracowany publicznie (1200 bod\u00F3w, ramki zaczynaj\u0105ce si\u0119 od 7E 7E, suma kontrolna XOR). Decyzja: zanim cokolwiek kupimy, sprawdzamy sond\u0105 w\u0142asnej roboty, czy jednostka odpowie na ten protok\u00F3\u0142."))
story.append(P("<b>Rozwi\u0105zanie sprz\u0119towe bez zakup\u00F3w:</b> analiza wn\u0119trza \u201Ebezu\u017Cytecznej\u201D bramki pokaza\u0142a, \u017Ce nie ma w niej procesora \u2014 to czysty konwerter UART\u2194RS485. Bramka zosta\u0142a przerobiona na interfejs sondy, a rol\u0119 m\u00F3zgu przej\u0119\u0142a p\u0142ytka WeMos D1 R1 (ESP8266) z firmware wysy\u0142aj\u0105cym co 3 sekundy ramk\u0119-zapytanie i nas\u0142uchuj\u0105cym odpowiedzi, z logiem dost\u0119pnym zdalnie przez WiFi (rozg\u0142oszenia UDP + serwer telnet)."))

story.append(P("Etap 1 \u2014 pierwsze podej\u015Bcie polowe: totalna cisza", "h1"))
story.append(P("Sonda zamontowana przy jednostce nadawa\u0142a poprawnie (w\u0142asny log), ale przez wiele sesji nie odebra\u0142a ani jednego bajta. Pomiary przy jednostce dawa\u0142y niefizyczne wyniki (\u22127 V na liniach danych wzgl\u0119dem masy \u2014 niemo\u017Cliwe dla nadajnika pracuj\u0105cego od 0 do 5 V), co wskazywa\u0142o, \u017Ce mierzymy \u201Ep\u0142ywaj\u0105ce\u201D, niepod\u0142\u0105czone przewody."))
story.append(box("Wniosek metodyczny, kt\u00F3ry odblokowa\u0142 ca\u0142o\u015B\u0107",
    "Przenie\u015B\u0107 diagnostyk\u0119 z drabiny na biurko i roz\u0142o\u017Cy\u0107 tor sygna\u0142u na odcinki, weryfikuj\u0105c ka\u017Cdy z osobna. Do tego powsta\u0142 drugi firmware \u2014 <b>tester biurkowy</b> \u2014 kt\u00F3ry zamiast ramek generuje powolne, mierzalne zwyk\u0142ym multimetrem stany (zmiana co 1 s) i raportuje stan wej\u015Bcia odbiorczego co sekund\u0119.", C_INFOBG, C_INFOBRD))

story.append(P("Etap 2 \u2014 przyczyna nr 1: myl\u0105ce opisy pin\u00F3w WeMos D1 R1", "h1"))
story.append(P("Test ci\u0105g\u0142o\u015Bci (z u\u017Cyciem programatora ALIENTEK jako biernego rozga\u0142\u0119\u017Anika do wtyczki JST) wykaza\u0142, \u017Ce pigtail i dzielnik napi\u0119cia s\u0105 sprawne. Analiza zdj\u0119cia p\u0142ytki ujawni\u0142a natomiast, \u017Ce przewody sygna\u0142owe siedzia\u0142y na pinach RX\u2190D0/TX\u2192D1 (sprz\u0119towy port szeregowy, wsp\u00F3\u0142dzielony z USB), a firmware nadaje i s\u0142ucha na pinach opisanych D12/MISO/D6 i D13/SCK/D5 \u2014 kt\u00F3re by\u0142y puste."))
story.append(B("<b>Przyczyna \u017Ar\u00F3d\u0142owa:</b> p\u0142ytka D1 R1 ma na ka\u017Cdym pinie 2\u20133 nazwy naraz i cz\u0119\u015B\u0107 nazw powt\u00F3rzon\u0105 w dw\u00F3ch miejscach listwy."))
story.append(B("<b>Skutek:</b> sonda fizycznie nigdy nie wys\u0142a\u0142a ramki do bramki."))
story.append(B("<b>Rozwi\u0105zanie:</b> prze\u0142o\u017Cenie przewod\u00F3w na piny w\u0142a\u015Bciwe wed\u0142ug pe\u0142nego nadruku."))

story.append(P("Etap 3 \u2014 przyczyna nr 2: bramka bez automatu kierunku", "h1"))
story.append(P("Po poprawieniu pin\u00F3w tester wykaza\u0142, \u017Ce bramka nadal nie wystawia \u017Cadnego sygna\u0142u na blaszki wyj\u015Bciowe (sta\u0142a r\u00F3\u017Cnica ~0 V zamiast prze\u0142\u0105czania). Trop: transceiver na p\u0142ytce bramki to uk\u0142ad 14-n\u00F3\u017Ckowy (rodzina MAX13089), kt\u00F3ry nie ma automatycznego prze\u0142\u0105czania kierunku nadawanie/odbi\u00F3r \u2014 w oryginale sterowa\u0142a tym p\u0142yta g\u0142\u00F3wna klimatyzatora przez dwie dodatkowe \u017Cy\u0142y z\u0142\u0105cza CN2: RXP (w\u0142\u0105cznik odbiornika, aktywny przy masie) i TXP (w\u0142\u0105cznik nadajnika). U nas obie wisia\u0142y w powietrzu, wi\u0119c bramka by\u0142a r\u00F3wnocze\u015Bnie niema i g\u0142ucha \u2014 to wyja\u015Bni\u0142o ka\u017Cdy dotychczasowy objaw, \u0142\u0105cznie z fantomowymi \u22127 V (niepod\u0142\u0105czony, p\u0142ywaj\u0105cy tor)."))
story.append(B("<b>Rozwi\u0105zanie:</b> RXP (\u017Cy\u0142a bia\u0142a) na sta\u0142e do masy; TXP (\u017Cy\u0142a \u017C\u00F3\u0142ta) pod kontrol\u0119 sondy \u2014 pin D11/MOSI/D7, stan wysoki tylko na czas wysy\u0142ania ramki. Firmware sondy by\u0142 na to gotowy od pocz\u0105tku (identyczny mechanizm jak w popularnych modu\u0142ach MAX485)."))

story.append(P("Etap 4 \u2014 przyczyna nr 3: opisy TXD/RXD \u201Eod strony klimatyzatora\u201D", "h1"))
story.append(P("Z w\u0142\u0105cznikami kierunku pod kontrol\u0105 bramka wci\u0105\u017C milcza\u0142a. Ostatnia zmienna: \u017Cy\u0142y danych. Okaza\u0142o si\u0119, \u017Ce opisy TXD/RXD na laminacie bramki s\u0105 z perspektywy p\u0142yty klimatyzatora: \u201ETXD\u201D to wej\u015Bcie bramki (dane, kt\u00F3re p\u0142yta nadaje), \u201ERXD\u201D \u2014 jej wyj\u015Bcie. Pod\u0142\u0105czenie intuicyjne (\u201Enasz TX do ich RX\u201D) by\u0142o wi\u0119c odwrotne do w\u0142a\u015Bciwego. Rozwi\u0105zanie: zamiana dw\u00F3ch ko\u0144c\u00F3wek w z\u0142\u0105czu krosowym. Natychmiast po niej pin kierunku zacz\u0105\u0142 realnie prze\u0142\u0105cza\u0107 odbiornik \u2014 pierwszy obserwowalny \u201Eznak \u017Cycia\u201D bramki."))

story.append(P("Etap 5 \u2014 pe\u0142na weryfikacja biurkowa", "h1"))
story.append(tbl(
    ["Test", "Wynik"],
    [
        ["Nadawanie: multimetr na blaszkach A\u2013B przy prze\u0142\u0105czaj\u0105cym si\u0119 sygnale", "<b>\u00B14,8 V, przeskok co 1 s</b> \u2014 nadajnik sprawny"],
        ["Ci\u0105g\u0142o\u015B\u0107 blaszek", "X1\u2194X3 zwarte (linia A), X2\u2194X4 zwarte (linia B) \u2014 pary przelotowe do \u0142\u0105czenia magistrali"],
        ["Odbi\u00F3r: wstrzykni\u0119cie 5 V / masy wprost na blaszki", "Wej\u015Bcie odbiorcze pod\u0105\u017Ca za polaryzacj\u0105 \u2014 odbiornik sprawny"],
    ],
    [8.5 * cm, 8.5 * cm],
))
story.append(Spacer(1, 4))
story.append(P("Sonda wr\u00F3ci\u0142a na jednostk\u0119 bez \u017Cadnej zmiany w kodzie \u2014 wy\u0142\u0105cznie z poprawionym okablowaniem."))

story.append(P("Etap 6 \u2014 sukces i pierwsze dane", "h1"))
story.append(P("Pierwsza sesja po naprawie: ka\u017Cda ramka sondy dostaje odpowied\u017A jednostki. Z 286 odebranych ramek 261 (91%) przesz\u0142o kontrol\u0119 sumy XOR; reszta to uci\u0119te odbiory (znany koszt programowego UART przy pracuj\u0105cym WiFi). Kanoniczna odpowied\u017A jednostki:"))
story.append(code("""7E 7E FF 40 11 17 09 30 83 7C 7C 0E 04 00 00 01 00 10 00 00 00 00 00 00 00 00 23 02 39

FF = nadawca: jednostka wewnetrzna     40 = adresat z puli "sterownik centralny"
17h = dlugosc czesci danych (23 bajty)  39 = suma XOR (poprawna)
23h na koncu danych odpowiada nastawie 23 st. C (hipoteza do potwierdzenia)"""))
story.append(P("Pilot podczerwieni dzia\u0142a r\u00F3wnolegle z sond\u0105 \u2014 jednostka nie zablokowa\u0142a odbiornika IR."))
story.append(box("Incydent: pr\u00F3ba zasilenia sondy z pinu +12 V portu",
    "Osobny, cenny wynik uboczny: podanie \u017Cy\u0142y +12 V z portu COM-MANUAL na wej\u015Bcie VIN WeMosa uniemo\u017Cliwia\u0142o start ca\u0142ego klimatyzatora (dwukrotnie zweryfikowane; 230 V na zasilaniu obecne). Wyja\u015Bnienie mechanizmu \u2014 raport g\u0142\u00F3wny, rozdz. 9. Wniosek: sond\u0119/mostek zasilamy wy\u0142\u0105cznie z w\u0142asnego zasilacza 5 V.", C_WARNBG, C_WARNBRD))

story.append(P("Lekcje na przysz\u0142o\u015B\u0107", "h1"))
story.append(B("Przy ciszy na magistrali najpierw podziel tor na odcinki i zweryfikuj ka\u017Cdy przy biurku \u2014 jedna sesja z multimetrem i testerem da\u0142a wi\u0119cej ni\u017C tydzie\u0144 pr\u00F3b przy jednostce."))
story.append(B("Nazwy na laminacie bywaj\u0105 z perspektywy drugiej strony kabla (TXD/RXD!), a piny p\u0142ytek-klon\u00F3w \u2014 opisane wieloznacznie. Ufaj pomiarom, nie napisom."))
story.append(B("Transceiver RS485 bez automatu kierunku = cztery sygna\u0142y do obs\u0142u\u017Cenia: dane w obie strony, klucz nadawania i w\u0142\u0105cznik odbiornika. Wszystkie musz\u0105 by\u0107 pod kontrol\u0105."))
story.append(B("Pomiar daj\u0105cy wynik \u201Eniefizyczny\u201D (\u22127 V) to niemal zawsze pomiar p\u0142ywaj\u0105cego przewodu \u2014 szukaj przerwy, nie egzotycznych wyja\u015Bnie\u0144."))
story.append(Spacer(1, 8))
story.append(P("Wersja \u017Ar\u00F3d\u0142owa tego dokumentu (Markdown): STUDIUM_PRZYPADKU.md. Generator: narzedzia\\generator_studium.py.", "small"))

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.7 * cm, bottomMargin=1.8 * cm,
    title="Studium przypadku: sonda COM-MANUAL dla Gree GKH",
    author="dokumentacja projektu",
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("OK:", OUT)
