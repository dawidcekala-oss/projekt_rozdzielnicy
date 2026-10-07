# -*- coding: utf-8 -*-
"""Składa jeden PDF: [1] schemat A4 + [2..] lista zakupowa z linkami Allegro + założenia/pytania.
Źródła: bom/bom.json, bom/linki.json (scalone wyniki wyszukiwania), schemat/schemat_A4.pdf"""
import json, os, subprocess, html, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
bom = json.load(open(os.path.join(ROOT, "bom", "bom.json"), encoding="utf-8"))
links = {}
lp = os.path.join(ROOT, "bom", "linki.json")
if os.path.exists(lp):
    links = {int(k): v for k, v in json.load(open(lp, encoding="utf-8")).items()}

def listing_url(fraza):
    from urllib.parse import quote_plus
    return "https://allegro.pl/listing?string=" + quote_plus(fraza)

def esc(s): return html.escape(str(s))

rows_by_basket = {}
total_min = 0.0; n_priced = 0
for p in bom["pozycje"]:
    rows_by_basket.setdefault(p["koszyk"], []).append(p)

css = """
@page { size: A4; margin: 14mm 12mm 14mm 12mm; }
html { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9.2pt; line-height: 1.3; color:#111; }
h1 { font-size: 15pt; margin: 0 0 4pt 0; border-bottom: 2px solid #333; padding-bottom: 2pt; }
h2 { font-size: 11.5pt; margin: 10pt 0 3pt 0; border-bottom: 1px solid #999; page-break-after: avoid; }
p { margin: 3pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 7.6pt; margin: 4pt 0 6pt 0; }
th, td { border: 1px solid #888; padding: 2.2pt 3pt; vertical-align: top; }
th { background: #e8e8e8; text-align: left; }
tr { page-break-inside: avoid; }
td.n { text-align: right; white-space: nowrap; }
a { color: #0a3d91; text-decoration: none; word-break: break-all; }
.small { font-size: 7.2pt; color: #333; }
.tag { font-weight: bold; white-space: nowrap; }
.note { background: #f6f6f6; border: 1px solid #bbb; padding: 4pt 6pt; margin: 4pt 0; font-size: 8.2pt; }
.pb { page-break-before: always; }
ul { margin: 2pt 0 2pt 14pt; padding: 0; }
li { margin: 1pt 0; }
"""
H = [f"<!doctype html><html><head><meta charset='utf-8'><title>Lista zakupowa</title><style>{css}</style></head><body>"]
H.append("<h1>Lista zakupowa z linkami Allegro – rozdzielnica testowa Ampere Point</h1>")
H.append(f"<p class='small'>Wersja: {esc(bom['wersja'])}. Oznaczenia (-Q1, -K3 …) odpowiadają schematowi na stronie 1. "
         "Linki: <b>oferta</b> = konkretna oferta znaleziona w październiku 2026 (sprawdź przed zakupem, oferty się zmieniają); "
         "<b>szukaj</b> = gotowe wyszukiwanie Allegro z numerem katalogowym, gdy nie udało się potwierdzić aktywnej oferty. "
         "Ceny orientacyjne, jeśli były widoczne w wynikach. Przewodów 6 mm² i 2,5 mm² nie ma na liście (są w magazynie).</p>")
H.append("<div class='note'><b>Koszyki (minimalna liczba zamówień):</b><ul>")
for k, v in bom["koszyki"].items():
    H.append(f"<li><b>{esc(k)}</b> – {esc(v)}</li>")
H.append("</ul></div>")
order = ["K1", "K4", "K2", "K3", "K5"]
for k in order:
    rows = rows_by_basket.get(k, [])
    if not rows: continue
    H.append(f"<h2>Koszyk {esc(k)}: {esc(bom['koszyki'][k])}</h2>")
    H.append("<table><thead><tr><th style='width:4%'>Lp.</th><th style='width:9%'>Oznaczenie</th><th style='width:33%'>Element / parametry</th><th style='width:17%'>Model (alternatywy)</th><th style='width:4%'>Szt.</th><th style='width:33%'>Link Allegro · cena · uwagi</th></tr></thead><tbody>")
    for p in rows:
        L = links.get(p["id"])
        if L and L.get("url"):
            typ = L.get("url_typ", "oferta")
            lab = "oferta" if typ in ("oferta", "produkt") else "szukaj"
            cena = f" · ok. {L['cena_pln']:.0f} zł" if L.get("cena_pln") else ""
            sprz = f" · {esc(L['sprzedawca'])}" if L.get("sprzedawca") else ""
            tyt = esc(L.get("tytul_oferty", ""))[:90]
            uw_raw = (L.get("uwagi", "") or "").strip()
            if len(uw_raw) > 230:
                cut = uw_raw[:230]
                k = max(cut.rfind(". "), cut.rfind("; "))
                uw_raw = (cut[:k + 1] if k > 80 else cut) + " …"
            uw = esc(uw_raw)
            alt = f" <a href='{esc(L['alternatywa_url'])}'>[alternatywa]</a>" if L.get("alternatywa_url") else ""
            cell = f"<a href='{esc(L['url'])}'><b>{lab}</b>: {tyt}</a>{cena}{sprz}{alt}<div class='small'>{uw}</div>"
        else:
            if p.get("fraza"):
                cell = f"<a href='{esc(listing_url(p['fraza']))}'><b>szukaj</b>: {esc(p['fraza'])}</a>"
            else:
                cell = "<span class='small'>z magazynu / w komplecie</span>"
        H.append(f"<tr><td class='n'>{p['id']}</td><td class='tag'>{esc(p['ozn'])}</td><td>{esc(p['nazwa'])}</td><td>{esc(p['model'])}</td><td class='n'>{esc(p['ilosc'])}</td><td>{cell}</td></tr>")
    H.append("</tbody></table>")

# strona: założenia i pytania
H.append("<h2 class='pb'>Założenia przyjęte do schematu (do potwierdzenia) i pytania otwarte</h2>")
H.append("""
<p><b>Zakres i zasilanie.</b> Zasilanie 3×400/230 V, 32 A, TN-S, przewodem H07RN-F 5G6 z wtykiem CEE 32 A. Pełny zakres funkcji (F1–F15). Skrzynka na razie wolnostojąca (Rittal AX 1180.000, 1000×800×300 mm, ok. 52 kg pusta, ok. 80 kg wyposażona); sposób montażu do ustalenia później.</p>
<p><b>Zabezpieczenia minimalne</b> (zgodnie z Twoją decyzją; pomiary i uruchomienie wykonuje elektryk z uprawnieniami E i D): rozłącznik główny 4P 63 A, SPD typu 2, jeden RCD 4P 40 A 30 mA typu A (pomijany stycznikami tylko w teście F13), MCB 3P C32 (CEE 32 A), 3P B16 (CEE 16 A), 1P+N B16 (gniazda 230 V), B6 (sterowanie), B10 (transformator). Bez RCD strażnika typu B, bez wyzwalacza wzrostowego, bez wyłącznika drzwiowego i przekaźników watchdog – te funkcje realizuje oprogramowanie na RPi i procedura obsługi (jedna usterka naraz, limity czasu, zakaz dotykania DUT w testach PE).</p>
<p><b>Sterowanie.</b> Raspberry Pi 5 z ekranem 7″ w drzwiach; wyjścia wolne (stany usterek) na posiadanych Shelly Wave Pro 3 przez Z-Wave (kontroler USB); wyjścia szybkie i krytyczne czasowo (-K1/-K2 stycznik główny i kolejność faz, -K4 „luźny styk”, -K6/-K7 transformator, -K12 pominięcie RCD, lampka, wentylator) na płytce 8 przekaźników GPIO. Pomiary: SDM630 (Modbus) po stronie zasilania, PZEM-016 (Modbus) i ZMPT101B (ADC) po stronie wyjścia, CKF-B jako niezależne potwierdzenie kolejności faz. Wszystkie cewki 230 V AC przez kluczyk „TRYB TESTOWY” i E-STOP (sprzętowo). Zasada: cewka bez napięcia = instalacja poprawna.</p>
<p><b>Shelly Wave Pro 3 z magazynu:</b> potrzeba 5 sztuk (plus 1 zapas). Jeśli masz mniej, brakujące wyjścia przejmie druga płytka przekaźników GPIO (ok. 40 zł) – schemat zmienia się tylko w opisach źródeł styków.</p>
<p><b>Transformator.</b> 230 V / 2×30 V, 1000 VA, uzwojenia wtórne równolegle (30 V / 33 A) na stałe w szeregu z L1; przełączanie po stronie pierwotnej (-K6 boost, -K7 buck), w stanie spoczynku pierwotne zwarte stykami NC. Daje 200 V / 260 V przy 230 V sieci. Alternatywa 2×24 V (206/254 V) jest tańsza i łatwiej dostępna, ale progi 207/253 V łapie na styk.</p>
<p><b>Rezystor „przepalony styk”.</b> 0,5 Ω / 600 W (2×1 Ω 300 W równolegle) na radiatorze z wentylatorem; przy 32 A to 512 W – oprogramowanie ogranicza do 15 s, przy 16 A do 60 s; termostat 85 °C w obwodzie cewki -K5 zdejmuje usterkę sprzętowo.</p>
<p><b>Pytania, które zostały otwarte</b> (odpowiedz przy okazji akceptacji schematu):</p>
<ul>
<li>Ile dokładnie Shelly Wave Pro 3 (i Wave Pro 2) jest w magazynie? Czy jest już jakikolwiek kontroler Z-Wave (stick USB)?</li>
<li>Jak jest dziś podłączone gniazdo „AWARIA” na obecnej skrzynce – chcesz odtworzyć tę konkretną usterkę na stałe, czy wystarczy, że wszystkie usterki są przełączalne?</li>
<li>Ładowarki testowe: egzemplarze „do zużycia” czy mają zostać sprawne? (Decyduje o dopuszczeniu 260 V i przesunięcia punktu zerowego.)</li>
<li>Marka aparatury: lista zakłada Noark/Hager/Chint-zamienniki (dostępne na Allegro). Jeśli wolisz jedną markę premium (Hager/Eaton), podmienię pozycje 1–12.</li>
<li>Czy oprogramowanie ma być Home Assistant (znasz) czy osobna aplikacja Python + Z-Wave JS UI (lepsze blokady)? Sprzęt jest ten sam.</li>
<li>Gniazdo Type 2 (np. pod AmpCheck / wstrzyknięcie 6 mA DC za ładowarką) – dodać?</li>
</ul>
<p class='small'>Następne etapy po akceptacji: (3) rozmieszczenie elementów na płycie montażowej 1000×800 i w drzwiach, (4) lista połączeń zacisk-po-zacisku i okablowanie, (5) oprogramowanie: automat stanów, blokady, ekran dotykowy, dziennik.</p>
""")
H.append("</body></html>")
html_path = os.path.join(ROOT, "docs", "_lista.html")
open(html_path, "w", encoding="utf-8").write("\n".join(H))
pdf_list = os.path.join(ROOT, "docs", "_lista.pdf")
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_list}", f"file://{html_path}"], check=True, capture_output=True)
# scal: schemat + lista
from pypdf import PdfReader, PdfWriter
w = PdfWriter()
for f in (os.path.join(ROOT, "schemat", "schemat_A4.pdf"), pdf_list):
    for pg in PdfReader(f).pages: w.add_page(pg)
w.add_metadata({"/Title": "Ampere Point – rozdzielnica testowa: schemat i lista zakupowa", "/Author": "Claude / D. Cękała"})
outp = os.path.join(ROOT, "docs", "pdf", "03_schemat_i_lista_zakupow.pdf")
w.write(outp)
print("OK", outp, "stron:", len(PdfReader(outp).pages), "| linki:", len(links))
