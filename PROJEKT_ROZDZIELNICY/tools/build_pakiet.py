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
def pln(v): return f"{v:,.0f} zł".replace(",", "\u202f")

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
         "Linki: <b>oferta</b> = konkretna oferta znaleziona w październiku 2026 (sprawdź przed zakupem); "
         "<b>szukaj</b> = gotowe wyszukiwanie Allegro z numerem katalogowym, gdy nie udało się potwierdzić aktywnej oferty. "
         "Ceny orientacyjne, jeśli były widoczne w wynikach. Przewodów 6 mm² i 2,5 mm² nie ma na liście (są w magazynie).</p>")
H.append("<div class='note'><b>Koszyki (minimalna liczba zamówień):</b><ul>")
for k, v in bom["koszyki"].items():
    H.append(f"<li><b>{esc(k)}</b> – {esc(v)}</li>")
H.append("</ul></div>")
order = ["K1", "K2", "K3", "K4", "K5"]
grand = {}
for k in order:
    rows = rows_by_basket.get(k, [])
    if not rows: continue
    H.append(f"<h2>Koszyk {esc(k)}: {esc(bom['koszyki'][k])}</h2>")
    H.append("<table><thead><tr><th style='width:3%'>Lp.</th><th style='width:8%'>Ozn.</th><th style='width:25%'>Element / parametry</th><th style='width:13%'>Model</th><th style='width:3%'>Szt.</th><th style='width:7%'>Cena jedn.</th><th style='width:7%'>Razem</th><th style='width:34%'>Link Allegro · uwagi</th></tr></thead><tbody>")
    subtotal = 0.0
    for p in rows:
        L = links.get(p["id"])
        if L and L.get("url"):
            typ = L.get("url_typ", "oferta")
            lab = "oferta" if typ in ("oferta", "produkt") else "szukaj"
            cena = (f" · cena rynkowa ok. {L['cena_pln']:.0f} zł" if (p.get("zrodlo") == "magazyn" or k == "K5") else f" · ok. {L['cena_pln']:.0f} zł") if L.get("cena_pln") else ""
            sprz = f" · {esc(L['sprzedawca'])}" if L.get("sprzedawca") else ""
            tyt = esc(L.get("tytul_oferty", ""))[:90]
            uw_raw = (L.get("uwagi", "") or "").strip()
            if len(uw_raw) > 170:
                cut = uw_raw[:170]
                cutpos = max(cut.rfind(". "), cut.rfind("; "))
                uw_raw = (cut[:cutpos + 1] if cutpos > 60 else cut) + " …"
            uw = esc(uw_raw)
            alt = f" <a href='{esc(L['alternatywa_url'])}'>[alternatywa]</a>" if L.get("alternatywa_url") else ""
            cell = f"<a href='{esc(L['url'])}'><b>{lab}</b>: {tyt}</a>{cena}{sprz}{alt}<div class='small'>{uw}</div>"
        else:
            if p.get("fraza"):
                cell = f"<a href='{esc(listing_url(p['fraza']))}'><b>szukaj</b>: {esc(p['fraza'])}</a>"
            else:
                cell = "<span class='small'>z magazynu / w komplecie</span>"
        # cena: z oferty jeśli znaleziona, inaczej szacunek z BOM
        if p.get("zrodlo") == "magazyn" or k == "K5":
            unit = 0.0; src = "magazyn"
        elif L and L.get("cena_pln"):
            unit = float(L["cena_pln"]); src = "oferta"
        else:
            unit = float(p.get("cena") or 0); src = p.get("zrodlo", "szac.")
        line_total = unit * float(p["ilosc"]); subtotal += line_total
        unit_s = ("—" if unit == 0 else pln(unit)) + ("" if src in ("oferta", "magazyn") or unit == 0 else "<br><span class='small'>szac.</span>")
        tot_s = "—" if line_total == 0 else pln(line_total)
        H.append(f"<tr><td class='n'>{p['id']}</td><td class='tag'>{esc(p['ozn'])}</td><td>{esc(p['nazwa'])}</td><td>{esc(p['model'])}</td><td class='n'>{esc(p['ilosc'])}</td><td class='n'>{unit_s}</td><td class='n'>{tot_s}</td><td>{cell}</td></tr>")
    H.append(f"<tr><td colspan='6' style='text-align:right'><b>Razem koszyk {esc(k)}</b></td><td class='n'><b>{pln(subtotal)}</b></td><td class='small'>ceny z ofert tam, gdzie były widoczne; pozostałe szacunek ±25 %</td></tr>")
    grand[k] = subtotal
    H.append("</tbody></table>")

# kosztorys zbiorczy
H.append("<h2>Kosztorys zbiorczy</h2><table><thead><tr><th>Koszyk</th><th>Zakres</th><th class='n'>Suma</th></tr></thead><tbody>")
for k in order:
    if k in grand:
        H.append(f"<tr><td class='tag'>{esc(k)}</td><td>{esc(bom['koszyki'][k])}</td><td class='n'>{pln(grand[k])}</td></tr>")
tot = sum(grand.values())
obud = [p for p in bom['pozycje'] if p['id']==23][0]['cena']
H.append(f"<tr><td colspan='2' style='text-align:right'><b>Razem (brutto, orientacyjnie)</b></td><td class='n'><b>{pln(tot)}</b></td></tr>")
H.append(f"<tr><td colspan='2' style='text-align:right'>w tym obudowa</td><td class='n'>{pln(obud)}</td></tr>")
H.append(f"<tr><td colspan='2' style='text-align:right'>bez obudowy</td><td class='n'>{pln(tot - obud)}</td></tr>")
H.append("</tbody></table><p class='small'>Nie uwzględniono: RCD, przewodów 6 i 2,5 mm², szybkozłączek, Shelly Wave Pro 3 i przekładników DLB (magazyn) oraz kosztów wysyłki (3 paczki). Rozrzut cen na Allegro ±25 %.</p>")
pk = bom.get("poza_kosztorysem")
if pk:
    H.append(f"<p class='small'><b>Poza kosztorysem (na życzenie):</b> {esc(pk['opis'])}: " + "; ".join(f"{esc(q['nazwa'].split(' – ')[0].split(' (')[0])} ×{esc(q['ilosc'])}" for q in pk["pozycje"]) + ".</p>")

# strona: założenia i pytania
H.append("<h2 class='pb'>Założenia przyjęte do schematu (do potwierdzenia) i pytania otwarte</h2>")
H.append("""
<p><b>Zakres i zasilanie.</b> Przyłącze 3×400/230 V, 32 A (wtyk CEE 32 A, przewód H07RN-F 5G4, 5 m), ale <b>prąd testów ograniczony do 16 A na fazę</b> wyłącznikiem -F3 B16 za RCD – zgodnie z Twoją uwagą o krótkich testach. Dzięki temu styki Shelly Wave Pro 3 (16 A) mogą pełnić rolę stycznika głównego, a cała sekcja usterek jest na aparaturze 25 A i przewodach 2,5 mm². Gniazdo CEE 32 A jest mechanicznie 32 A, elektrycznie 16 A (ładowarka 22 kW będzie ograniczona). Obudowa: wolnostojąca skrzynka z ABS 700×500×250 mm IP65 z ocynkowaną płytą montażową (ok. 400 zł zamiast 1600 zł za Rittal AX); ekran 7″ i przyciski w drzwiach, gniazda na ścianie bocznej lub dolnej; montaż później.</p>
<p><b>Zabezpieczenia minimalne</b> (pomiary i uruchomienie przez elektryka E/D): rozłącznik 4P 40 A, jeden RCD 4P 40 A 30 mA <b>z magazynu</b> (pomijany stycznikami tylko w F13; dla ładowarek EV zalecany typ A – sprawdź oznaczenie na aparacie), MCB 3P B16 sekcji, 2P B16 gniazd 230 V, B6 sterowania, B10 transformatora. <b>Bez SPD</b> – zgodnie z Twoją decyzją; moja uwaga: elektronika (RPi, PZEM, ADS1115) jest wtedy chroniona tylko warystorami przy cewkach i w zasilaczu -G1, więc stanowisko podłączaj do instalacji, która ma własny ogranicznik; na szynie zostaje 4 moduły wolnego miejsca, gdyby SPD miał wrócić.</p>
<p><b>Dlaczego zostały jakieś styczniki, skoro mamy Shelly:</b> styki Shelly są tylko zwierne (NO) i nie mają sprzętowej blokady między sobą. Tam, gdzie usterka musi znikać po zaniku sterowania (przerwa PE, N, L3, bocznik rezystora), potrzebny jest styk rozwierny – stycznik 2NC za ok. 48 zł. Tam, gdzie zamieniamy dwa przewody (fazy, N–PE, L–N, tor RCD), potrzebny jest styk przełączny z mechaniczną gwarancją „nigdy oba” – stycznik 2NO+2NC za ok. 75 zł. Para styczników przemysłowych Schneidera została usunięta: stycznik główny to -A11 Shelly Wave Pro 3, zamiana faz to jeden -K2. Pierwotne transformatora (-K6/-K7) dałoby się zrobić na Shelly Wave Pro 2 + Pro Shutter z blokadą programową – zostawiłem styczniki (2×75 zł), bo zwarcie uzwojenia przy błędzie oprogramowania jest zbyt kosztowne; jeśli wolisz wariant Shelly, powiedz.</p>
<p><b>Sterowanie.</b> Raspberry Pi 5 z ekranem 7″ w drzwiach; -A11…-A15 Shelly Wave Pro 3 po Z-Wave (-A11 zasilany z Lc, więc kluczyk i E-STOP odłączają wyjście sprzętowo; pozostałe sterują cewkami i drabinką upływów); płytka 8 przekaźników GPIO na przełączenia szybkie (-K4 impulsy, -K6/-K7, -K12, -K2, lampka, wentylator). Pomiary <b>bez licznika</b>: trzy PZEM-016 (Modbus RTU, adresy 1–3 nadane programowo) mierzą napięcie, prąd, moc i energię każdej fazy wyjścia – to wystarcza do kontroli sesji ładowania; ich wejścia napięciowe odniesione są do N sprzed styczników -K8/-K10 (stały), bo przy przerwie N (F4) pływający N″ dałby na PZEM nawet 400 V; ZMPT101B mierzy N″–PE″; CKF-B jest niezależnym potwierdzeniem kolejności faz. Uwaga do Shelly: posiadane Wave Pro 3 nie mają pomiaru energii (tylko styki), a Wave Pro Shutter / Dimmer 1PM mierzą, lecz nie przeniosą 16 A w tym układzie – dlatego pomiar robi PZEM, a nie Shelly. Zasada: cewka bez napięcia = instalacja poprawna.</p>
<p><b>Elementy montażowe</b> (szyna TH35, kanał grzebieniowy, dławnice, kratki wentylacyjne, tulejki) są poza tabelą i podsumowaniem – dobierzemy je na etapie montażu; wentylacja radiatora -R1 wymaga wtedy kratki z filtrem.</p>
<p><b>Szybkozłączki z magazynu</b> zastępują złączki szynowe: wejście zasilania, rozgałęzienia N/PE wyjścia, zaciski DLB. Zostały tylko dwa bloki rozdzielcze 125 A na N i PE strony zasilania (po kilkanaście odpływów). Dla toru 32 A (od -X1 do -F3) użyj szybkozłączek 6 mm² (seria 221-61x) i przewodu 6 mm²; za -F3 wystarczą 2,5 mm².</p>
<p><b>Transformator.</b> 230 V / 2×30 V, 630 VA, uzwojenia wtórne równolegle (30 V / 21 A) na stałe w szeregu z L1; przełączanie po stronie pierwotnej (-K6 boost, -K7 buck), w spoczynku pierwotne zwarte stykami NC. Daje 200 V / 260 V przy 230 V sieci.</p>
<p><b>Rezystor „przepalony styk”.</b> 0,5 Ω / 200 W (2×1 Ω 100 W równolegle) na radiatorze z wentylatorem; przy 16 A to 128 W – oprogramowanie ogranicza do 60 s, termostat 85 °C w obwodzie cewki -K5 zdejmuje usterkę sprzętowo.</p>
<p><b>Pytania, które zostały otwarte:</b></p>
<ul>
<li>Ile dokładnie Shelly Wave Pro 3 (i Wave Pro 2) jest w magazynie? Potrzeba 5 + 1 zapas. Czy jest już kontroler Z-Wave USB?</li>
<li>Jak dziś jest podłączone gniazdo „AWARIA” na obecnej skrzynce – odtworzyć na stałe, czy wystarczą usterki przełączalne?</li>
<li>Ładowarki testowe: egzemplarze „do zużycia” czy mają zostać sprawne? (260 V przez 30 s i przesunięcie punktu zerowego.)</li>
<li>Oprogramowanie: Home Assistant (znasz) czy osobna aplikacja Python + Z-Wave JS UI (lepsze blokady)? Sprzęt ten sam.</li>
<li>Czy jest przewód giętki 5G4 lub 5G6 do zasilania (poz. 19 można wtedy skreślić)?</li>
</ul>
<p class='small'>Następne etapy po akceptacji: (3) rozmieszczenie elementów na płycie montażowej obudowy 700×500 i w drzwiach, (4) lista połączeń zacisk-po-zacisku i okablowanie, (5) oprogramowanie: automat stanów, blokady, ekran dotykowy, dziennik.</p>
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
