# -*- coding: utf-8 -*-
"""Konwerter Markdown -> PDF w stylu raportu projektu.
Uzycie: python md_do_pdf.py plik.md [plik.pdf]
Obsluguje: # naglowki, tabele |..|, listy -, listy 1., pogrubienie **..**,
kod `..` i ```..```, linki [t](u) -> klikalne, linie poziome ---."""
import sys, re, io, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Ar", F + r"\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", F + r"\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + r"\cour.ttf"))

C_ACCENT = colors.HexColor("#B45309")
C_DARK = colors.HexColor("#1F2937")
C_GRAY = colors.HexColor("#6B7280")
C_LINE = colors.HexColor("#D1D5DB")
C_HEADBG = colors.HexColor("#374151")
C_ROWALT = colors.HexColor("#F3F4F6")
C_CODEBG = colors.HexColor("#F5F5F4")

S = {
    "title": ParagraphStyle("title", fontName="ArB", fontSize=17, leading=22, textColor=C_DARK, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName="ArB", fontSize=13.5, leading=17, textColor=C_ACCENT, spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="ArB", fontSize=11.5, leading=15, textColor=C_DARK, spaceBefore=10, spaceAfter=5),
    "body": ParagraphStyle("body", fontName="Ar", fontSize=10, leading=13.8, textColor=C_DARK, alignment=TA_JUSTIFY, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="Ar", fontSize=10, leading=13.8, textColor=C_DARK, alignment=TA_JUSTIFY, leftIndent=14, bulletIndent=4, spaceAfter=3),
    "tcell": ParagraphStyle("tcell", fontName="Ar", fontSize=8.8, leading=11.4, textColor=C_DARK),
    "thead": ParagraphStyle("thead", fontName="ArB", fontSize=8.8, leading=11.4, textColor=colors.white),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=8.2, leading=10.6, textColor=C_DARK),
    "small": ParagraphStyle("small", fontName="Ar", fontSize=8.4, leading=11, textColor=C_GRAY),
}

EMOJI = {"\u2705": "TAK", "\u274C": "NIE", "\u26A0\uFE0F": "UWAGA", "\u26A0": "UWAGA"}


def inline(t):
    for k, v in EMOJI.items():
        t = t.replace(k, v)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # linki -> klikalne w PDF (wczesniej adres byl wyrzucany - psulo listy zakupow)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<link href="\2" color="#1F6FB2">\1</link>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)          # pogrubienie
    t = re.sub(r"`([^`]+)`", r'<font face="Mono">\1</font>', t)  # kod w linii
    return t


def tabela(wiersze):
    naglowek = [inline(c) for c in wiersze[0]]
    dane = [[Paragraph(h, S["thead"]) for h in naglowek]]
    for r in wiersze[2:]:
        r = list(r) + [""] * (len(naglowek) - len(r))
        dane.append([Paragraph(inline(c), S["tcell"]) for c in r[:len(naglowek)]])
    # szerokosci proporcjonalne do najdluzszej komorki, min 1.6 cm
    surowe = [[c for c in w] for w in wiersze if w is not wiersze[1]]
    maxy = [max(len(w[i]) if i < len(w) else 0 for w in surowe) for i in range(len(naglowek))]
    maxy = [max(m, 6) for m in maxy]
    suma = sum(maxy)
    szer = [max(1.6, 17.0 * m / suma) * cm for m in maxy]
    k = sum(szer) / (17.0 * cm)
    szer = [s / k for s in szer]
    t = Table(dane, colWidths=szer, repeatRows=1)
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


# Blok kodu nie miesci sie na stronie, jesli jest dlugi, a tabela reportlaba
# nie umie sie podzielic - dlatego tniemy go na kawalki wysokosci strony.
MAX_LINII_KODU = 58


def obrazek(sciezka, opis, katalog):
    """Skaluje obraz do szerokosci ramki, zachowujac proporcje."""
    import os
    from reportlab.lib.utils import ImageReader
    p = sciezka if os.path.isabs(sciezka) else os.path.join(katalog, sciezka)
    if not os.path.exists(p):
        return [Paragraph("[brak pliku obrazu: " + sciezka + "]", S["small"])]
    iw, ih = ImageReader(p).getSize()
    szer = 17.0 * cm
    wys = szer * ih / float(iw)
    maks = 23.6 * cm
    if wys > maks:
        wys = maks
        szer = wys * iw / float(ih)
    wy = []
    if wys > 15.0 * cm:
        # duzy obraz (np. pelny schemat) - na wlasnej stronie
        from reportlab.platypus import PageBreak
        wy.append(PageBreak())
    wy.append(Image(p, width=szer, height=wys))
    if opis:
        wy.append(Spacer(1, 4))
        wy.append(Paragraph(opis, S["small"]))
    return wy


def blok_kodu(linie):
    if len(linie) > MAX_LINII_KODU:
        wy = []
        for p in range(0, len(linie), MAX_LINII_KODU):
            wy.extend(blok_kodu(linie[p:p + MAX_LINII_KODU]))
        return wy
    t = Table([[Preformatted("\n".join(linie), S["code"])]], colWidths=[17.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.4, C_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [t]


def konwertuj(md_path, pdf_path):
    linie = io.open(md_path, encoding="utf-8").read().splitlines()
    katalog = os.path.dirname(os.path.abspath(md_path))
    story, tytul = [], os.path.basename(md_path)
    i, akapit = 0, []
    punkt = None  # (tekst, bulletText) ostatniego punktu listy - zbiera kontynuacje

    def zrzuc_punkt():
        nonlocal punkt
        if punkt:
            story.append(Paragraph(inline(punkt[0]), S["bullet"], bulletText=punkt[1]))
            punkt = None

    def zrzuc_akapit():
        nonlocal akapit
        zrzuc_punkt()
        if akapit:
            story.append(Paragraph(inline(" ".join(akapit)), S["body"]))
            akapit = []

    while i < len(linie):
        l = linie[i]
        if l.startswith("```"):
            zrzuc_akapit()
            blok = []
            i += 1
            while i < len(linie) and not linie[i].startswith("```"):
                blok.append(linie[i]); i += 1
            story.extend(blok_kodu(blok)); story.append(Spacer(1, 4))
        elif l.startswith("|"):
            zrzuc_akapit()
            wiersze = []
            while i < len(linie) and linie[i].startswith("|"):
                wiersze.append([c.strip() for c in linie[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            if len(wiersze) >= 2:
                story.append(tabela(wiersze)); story.append(Spacer(1, 5))
        elif l.strip().startswith("!["):
            zrzuc_akapit()
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", l.strip())
            if m:
                story.extend(obrazek(m.group(2), m.group(1), katalog))
                story.append(Spacer(1, 8))
        elif l.startswith("# "):
            zrzuc_akapit(); tytul = l[2:].strip()
            story.append(Paragraph(inline(tytul), S["title"]))
        elif l.startswith("## "):
            zrzuc_akapit(); story.append(Paragraph(inline(l[3:].strip()), S["h1"]))
        elif l.startswith("### "):
            zrzuc_akapit(); story.append(Paragraph(inline(l[4:].strip()), S["h2"]))
        elif re.match(r"^\s*[-*] ", l):
            zrzuc_akapit()
            punkt = (re.sub(r"^\s*[-*] ", "", l), "\u2013")
        elif re.match(r"^\s*\d+\. ", l):
            zrzuc_akapit()
            nr = re.match(r"^\s*(\d+)\. ", l).group(1)
            punkt = (re.sub(r"^\s*\d+\. ", "", l), nr + ".")
        elif l.strip() == "---":
            zrzuc_akapit(); story.append(Spacer(1, 6))
        elif l.strip() == "":
            zrzuc_akapit()
        elif punkt and re.match(r"^\s{2,}\S", l):
            punkt = (punkt[0] + " " + l.strip(), punkt[1])
        else:
            zrzuc_punkt()
            akapit.append(l.strip())
        i += 1
    zrzuc_akapit()
    story.append(Spacer(1, 8))
    story.append(Paragraph("Wersja \u017Ar\u00F3d\u0142owa: " + os.path.basename(md_path) + " \u2022 wygenerowano narzedzia\\md_do_pdf.py", S["small"]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Ar", 7.6)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(2 * cm, 1.1 * cm, tytul[:90])
        canvas.drawRightString(19 * cm, 1.1 * cm, f"strona {doc.page}")
        canvas.setStrokeColor(C_LINE)
        canvas.setLineWidth(0.4)
        canvas.line(2 * cm, 1.35 * cm, 19 * cm, 1.35 * cm)
        canvas.restoreState()

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.7 * cm, bottomMargin=1.8 * cm, title=tytul)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("OK:", pdf_path)


if __name__ == "__main__":
    md = sys.argv[1]
    pdf = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.md$", ".pdf", md)
    konwertuj(md, pdf)
