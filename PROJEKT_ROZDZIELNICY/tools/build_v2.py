# -*- coding: utf-8 -*-
"""Dokument v2 (ekonomiczny): odpowiedzi na uwagi, rewizja najdroższych pozycji, lista zakupowa v2 z linkami, kosztorys v2 vs rew. C.
Źródła: bom/bom_v2.json, bom/linki_v2.json, bom/bom.json + bom/linki.json (rew. C do porównania). Wynik: docs/pdf/05_wersja_v2_tansze_rozwiazania.pdf"""
import json, os, subprocess, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
def J(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
bom, links = J("bom/bom_v2.json"), {int(k): v for k, v in J("bom/linki_v2.json").items()}
bomC, linksC = J("bom/bom.json"), {int(k): v for k, v in J("bom/linki.json").items()}

def esc(s): return html.escape(str(s))
def pln(v): return f"{v:,.0f} zł".replace(",", " ")
def pln2(v): return (f"{v:,.2f}".replace(",", " ").replace(".", ",") + " zł") if abs(v - round(v)) > 0.004 else pln(v)
def unit_price(p, L):
    if p.get("zrodlo") == "magazyn" or p["koszyk"] == "K5": return 0.0, "magazyn"
    if L and L.get("cena_pln"): return float(L["cena_pln"]), "oferta"
    return float(p.get("cena") or 0), p.get("zrodlo", "szac.")
def totals(b, Ls):
    t = {}
    for p in b["pozycje"]:
        u, _ = unit_price(p, Ls.get(p["id"]))
        t[p["koszyk"]] = t.get(p["koszyk"], 0.0) + u * float(p["ilosc"])
    return t
totC, totV = totals(bomC, linksC), totals(bom, links)
sumC, sumV = sum(totC.values()), sum(totV.values())

css = """
@page { size: A4; margin: 14mm 12mm 14mm 12mm; }
html { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9.2pt; line-height: 1.3; color:#111; }
h1 { font-size: 15pt; margin: 0 0 4pt 0; border-bottom: 2px solid #333; padding-bottom: 2pt; }
h2 { font-size: 11.5pt; margin: 10pt 0 3pt 0; border-bottom: 1px solid #999; page-break-after: avoid; }
h3 { font-size: 10pt; margin: 8pt 0 2pt 0; }
p { margin: 3pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 7.6pt; margin: 4pt 0 6pt 0; }
th, td { border: 1px solid #888; padding: 2.2pt 3pt; vertical-align: top; }
th { background: #e8e8e8; text-align: left; }
tr { page-break-inside: avoid; }
td.n { text-align: right; white-space: nowrap; }
a { color: #0a3d91; text-decoration: none; word-break: break-all; }
.small { font-size: 7.2pt; color: #333; }
.tag { font-weight: bold; }
.note { background: #f6f6f6; border: 1px solid #bbb; padding: 4pt 6pt; margin: 4pt 0; font-size: 8.4pt; }
.pb { page-break-before: always; }
ul, ol { margin: 2pt 0 2pt 14pt; padding: 0; }
li { margin: 2pt 0; }
.ok { color:#0a5c2a; font-weight:bold; } .minus { color:#0a5c2a; } .plus { color:#9a1b1b; }
"""
H = [f"<!doctype html><html><head><meta charset='utf-8'><title>Wersja v2 – tańsze rozwiązania</title><style>{css}</style></head><body>"]
H.append("<h1>Rozdzielnica testowa – wersja v2: rewizja kosztów i tańsze rozwiązania</h1>")
H.append(f"<p class='small'>Wersja: {esc(bom['wersja'])}. Odniesienie: rew. C (docs/pdf/03_…, kosztorys {pln(sumC)}). Ceny z ofert Allegro z 15.10.2026 tam, gdzie były widoczne; reszta szacunek ±25 %. Oznaczenia (-K1, -F6 …) jak na schemacie rew. C; pozycje nowe w v2 oznaczone w uwagach.</p>")

# ---------------- 1. odpowiedzi
H.append("<h2>1. Odpowiedzi na uwagi z 15.10</h2>")
H.append("""
<ol>
<li><b>Tolerancje napięcia ładowarek.</b> Masz rację. W <i>AMPERE_POINT_porownanie_ladowarek_v2.html</i> (uwaga D do deklaracji) jest zapisane, że zabezpieczenie podnapięciowe (błąd D) działa dopiero <b>poniżej ok. 150 V</b>, a nadnapięciowe (błąd C) <b>powyżej ok. 270 V</b>; realny zakres pracy to ok. 150–275 V (karta TopAC EVE01-11R podaje tylko nominalne 220/380–240/415 V). Mój toroid ±30 V dawał 200 V / 260 V, czyli w ogóle nie dotykał progów – test byłby bezwartościowy. W v2 usterkę napięciową robi <b>mały toroid 230 V / 2×55 V, 160 VA</b> (ok. 170 zł): oba uzwojenia w szereg i w przeciwfazie dają <b>−110 V → 120 V</b> (błąd D), jedno uzwojenie w fazie daje <b>+55 V → 285 V</b> (błąd C). Taki transformator nie przeniesie prądu ładowania, więc test jest „w stanie gotowości”: ładowarka ma <i>odmówić startu / zgłosić błąd</i> przy złym napięciu. Jeśli mimo to zacznie ładować, bezpiecznik 1,6 A w torze wtórnego otwiera L1 (ładowarka widzi zanik fazy), a wynik testu i tak jest jednoznaczny („zaczęła ładować przy 285 V = źle”). Ładowanie pod obciążeniem przy 120 V nie ma sensu testowego – ładowarka ma wtedy nie ładować.</li>
<li><b>Szybkozłączki.</b> Były tylko wygodą za 0 zł do rozgałęzień (wejście zasilania, N/PE do trzech gniazd). W v2 ich nie ma: przewód zasilający idzie dławnicą wprost na zaciski RCD, PE do jednego bloku rozdzielczego -W2 (płyta, drzwi, radiator, zasilacz, DLB), a N″/PE″ do gniazd łączymy łańcuchowo na podwójnych zaciskach gniazd PCE. Nic nie trzeba kupować.</li>
<li><b>Wtyczka siłowa.</b> Skreślona razem z przewodem 5G4 – użyjesz przewodu z wtykiem CEE 32 A z ładowarki (pozycja „magazyn”).</li>
<li><b>Przewody.</b> Skreślone wszystkie: LgY 1 mm², LiYCY (RS485 już nie ma), H07RN-F. Cewki i sygnały prowadzisz przewodem 2,5 mm² z magazynu; do GPIO dowolny cienki przewód z magazynu.</li>
<li><b>Transformator.</b> 569 zł → ok. 170 zł (punkt 1) i zamiast drugiego stycznika 2NO+2NC na buck (110 zł) dwa małe przekaźniki z podstawkami (ok. 32 zł), bo prąd pierwotnego i odczepu jest znikomy.</li>
<li><b>Kontroler Z-Wave USB.</b> Był potrzebny wyłącznie dlatego, że Shelly <i>Wave</i> rozmawiają tylko po Z-Wave (868 MHz), a w magazynie nie ma żadnego huba Z-Wave: Gateway Gen3 to brama Bluetooth→Wi-Fi do głowic TRV, „pill” to pilot BLE. Bez kontrolera RPi nie wyda Shelly żadnej komendy. W v2 <b>rezygnuję z Shelly w tym projekcie</b>: płytka 16 przekaźników za ok. 60 zł steruje wszystkimi cewkami wprost z GPIO (szybciej, bez radia, prostsze oprogramowanie), a cztery moduły optoizolatorów 230 V (po 16 zł) zastępują wejścia SW. Shelly zostają w magazynie na inne projekty. Gdybyś jednak miał hub Z-Wave – wariant z Shelly nie jest tańszy, tylko oszczędza 5 kanałów płytki.</li>
<li><b>Za drogo.</b> Tabela w p. 2 przechodzi przez pozycje od najdroższej. Kosztorys v2: <b>""" + pln(sumV) + "</b> zamiast " + pln(sumC) + """ (−""" + pln(sumC - sumV) + """, ok. """ + f"{100 * (1 - sumV / sumC):.0f}" + """ %). Lista opcji w p. 4 pozwala zejść niżej (ekran = telefon: −325 zł) albo dołożyć to, co skreśliłem.</li>
</ol>""")

# ---------------- 2. rewizja najdroższych pozycji
H.append("<h2>2. Najdroższe pozycje rew. C i co proponuję zamiast nich</h2>")
rows2 = [
 ("Styczniki Noark 8× 2NO+2NC (110 zł) + 4× 2NC (77 zł) + -K1 4NO (85 zł)", 1273, "Adelid/Gacia: 7× 2NO+2NC po 60 zł, 4× 2NC po 40 zł, 4NO 49 zł; -K7 → 2 przekaźniki 16 zł", 7*60+4*40+49+32, "Tańsza marka, te same funkcje i styki 25 A. Krótkie testy – żywotność styków nie jest problemem."),
 ("RPi 5 4 GB (410) + Touch Display 2 (282) + cooler/microSD/kabel (85)", 777, "RPi 4B 2 GB (290) + ekran 7″ HDMI 1024×600 (130) + microSD/kable (45)", 465, "Niższa rozdzielczość ekranu, ta sama funkcja. Opcja: telefon jako ekran + RPi Zero 2 W → 140 zł."),
 ("Toroid 630 VA 2×30 V (569) + -K6/-K7 2× 110", 789, "Toroid 160 VA 2×55 V (170) + -K6 60 + 2 przekaźniki 32 + bezpiecznik 12", 274, "Test napięciowy tylko w gotowości ładowarki (p. 1), za to trafia w realne progi 150/270 V."),
 ("3× PZEM-016 (144) + izolowany USB-RS485 (113)", 545, "1× PZEM-004T v3 (41) wprost do UART RPi", 41, "Pomiar tylko L1″ (tam są usterki napięciowe); fazy L2/L3 pilnuje CKF-B. 3 fazy: +82 zł."),
 ("Obudowa ABS 700×500×250 (399)", 399, "ABS 600×400×200 z płytą (197)", 197, "Mniej modułów po zmianach (bez -Q1, SPD, -K7, Shelly). Ciaśniej przy montażu."),
 ("Kontroler Z-Wave (189) + płytka 8 przekaźników (95) + Shelly (0)", 284, "Płytka 16 przekaźników (60) + 4 optoizolatory 230 V (63)", 123, "Bez radia, bez Z-Wave JS; całe sterowanie po GPIO. Shelly zostają w magazynie."),
 ("Rozłącznik -Q1 4P 40 A (106)", 106, "brak – odłączanie przez wyjęcie wtyku CEE; RCD -F1 ma dźwignię", 0, "Minimalne zabezpieczenia wg Twojej decyzji."),
 ("RCBO sterowania -F6 Noark (95)", 95, "RCBO dowolnej marki (60)", 60, "Funkcja bez zmian. Opcja: zwykły B6 za 11 zł (−49), patrz p. 4."),
 ("Wtyk CEE 32 A (23) + przewód 5G4 5 m (108) + LgY/LiYCY (125)", 256, "magazyn", 0, "Twoje uwagi 3 i 4."),
 ("-M1 wentylator (38) + -B2 (4) + ZMPT101B/ADS1115 (57)", 99, "skreślone (opcje w p. 4)", 0, "Limit 60 s w oprogramowaniu + -B1 85 °C wystarczą; N″–PE″ nie trzeba mierzyć."),
 ("Bloki rozdzielcze -W1/-W2 2× 32", 63, "1 blok PE (32); N łańcuchowo na zaciskach", 32, "—"),
]
H.append("<table><thead><tr><th style='width:30%'>Pozycja w rew. C</th><th class='n' style='width:7%'>było</th><th style='width:30%'>Propozycja v2</th><th class='n' style='width:7%'>jest</th><th class='n' style='width:8%'>różnica</th><th>Co się zmienia / ryzyko</th></tr></thead><tbody>")
sb = sv = 0
for a, b, c, d, e in rows2:
    sb += b; sv += d
    H.append(f"<tr><td>{esc(a)}</td><td class='n'>{pln(b)}</td><td>{esc(c)}</td><td class='n'>{pln(d)}</td><td class='n minus'>−{pln(b - d)}</td><td class='small'>{esc(e)}</td></tr>")
H.append(f"<tr><td><b>Razem pozycje z tabeli</b></td><td class='n'><b>{pln(sb)}</b></td><td></td><td class='n'><b>{pln(sv)}</b></td><td class='n minus'><b>−{pln(sb - sv)}</b></td><td class='small'>pozostałe pozycje (gniazda, przyciski, rezystory, warystory, zasilacz 5 V, CKF-B, MCB) bez zmian</td></tr>")
H.append("</tbody></table>")
H.append("""<div class='note'><b>Czego NIE ciąłem i dlaczego:</b> stycznik główny -K1 (bez niego E-STOP i kluczyk nie odłączają wyjścia sprzętowo), RCD -F1 (Twój), -K13 CKF-B (jedyne niezależne potwierdzenie kolejności faz, 77 zł), termostat -B1 (chroni rezystor 200 W), zasilacz DIN 5 V (81 zł; tańsze ładowarki USB nie mają 3 A i izolacji), oba gniazda CEE i Schuko.</div>""")

# ---------------- 3. zmiany na schemacie
H.append("<h2>3. Co zmienia się na schemacie rew. C (do rew. D po Twojej akceptacji)</h2>")
H.append("""<ul>
<li><b>Kolumna A:</b> bez -Q1 i -X1 (przewód z wtykiem na zaciski -F1); -F6 RCBO bez zmian; nowa podstawa bezpiecznikowa -F8 1,6 A we wtórnym -T1.</li>
<li><b>Kolumna B, blok -T1:</b> toroid 2×55 V; -K6 (2NO+2NC): NC1 = bocznik L1′→L1″ w spoczynku, NO1 = pierwotne, NO2 = włączenie wtórnego w L1; -RL1 (DPDT) odwraca biegunowość pierwotnego (buck), -RL2 wybiera odczep 55 V (boost) / 110 V (buck). W spoczynku wtórne jest <i>odłączone</i>, nie zwarte – przy małym transformatorze bocznik musi być twardy.</li>
<li><b>Pomiary:</b> jeden -P2 PZEM-004T na L1″ (UART TTL, opto) zamiast -P2a/b/c i -A6; -P3/-A5 skreślone.</li>
<li><b>Sterowanie:</b> -A4 = 16 przekaźników: CH1 -K1 · CH2 -K2 · CH3 -K3 · CH4 -K4 · CH5 -K5 · CH6 -K6 · CH7 -RL1+RL2 (buck) · CH8 -K8 · CH9 -K9 · CH10 -K10 · CH11 -K11 · CH12 -K12a+b · CH13 -R2 (F2) · CH14 -R3 (F3) · CH15 mostek N′–PE′ (F6) · CH16 -R4 (F14); F15 (zestaw DC) i -H1 na dwóch dodatkowych kanałach małej płytki 2-kan. (ok. 8 zł) albo rezygnujemy z -H1 (lampka stanu bezpiecznego) – do decyzji. Wejścia zwrotne: -A7a Lc OK · -A7b -S0 · -A7c -K13 · -A7d -K9 → GPIO.</li>
<li><b>Bez Z-Wave:</b> znikają -A3, -A11…-A15 i tabela Shelly; cewka -K1 z Lc przez przekaźnik CH1 (styk 10 A, cewka ≈ 0,05 A).</li>
<li><b>Zasada bezpieczeństwa bez zmian:</b> cewka bez napięcia = instalacja poprawna; Lc tylko przy kluczyku i zwolnionym E-STOP; watchdog RPi + limity czasu w oprogramowaniu.</li>
</ul>""")

# ---------------- 4. opcje
H.append("<h2>4. Opcje do wyboru (zmiana względem kosztorysu v2)</h2>")
H.append("<table><thead><tr><th>Opcja</th><th class='n' style='width:10%'>zmiana</th><th>Uwagi</th></tr></thead><tbody>")
for o in bom["opcje"]:
    cl = "minus" if o["delta"] < 0 else "plus"
    H.append(f"<tr><td>{esc(o['nazwa'])}</td><td class='n {cl}'>{'−' if o['delta'] < 0 else '+'}{pln(abs(o['delta']))}</td><td class='small'>{esc(o['uwagi'])}</td></tr>")
H.append("</tbody></table>")

# ---------------- 5. lista zakupowa v2
H.append("<h2>5. Lista zakupowa v2 z linkami Allegro</h2>")
H.append("<p class='small'><b>oferta</b> = konkretna oferta z 15.10.2026 (sprawdź przed zakupem); <b>produkt</b> = karta produktu Allegro; <b>szukaj</b> = gotowe wyszukiwanie, gdy nie było potwierdzonej oferty. Pozycje przeniesione z rew. C mają linki z października.</p>")
H.append("<div class='note'><b>Koszyki:</b><ul>" + "".join(f"<li><b>{esc(k)}</b> – {esc(v)}</li>" for k, v in bom["koszyki"].items()) + "</ul></div>")
rows_by = {}
for p in bom["pozycje"]: rows_by.setdefault(p["koszyk"], []).append(p)
grand = {}
for k in ["K1", "K2", "K3", "K5"]:
    rows = rows_by.get(k, [])
    if not rows: continue
    H.append(f"<h3>Koszyk {esc(k)}: {esc(bom['koszyki'][k])}</h3>")
    H.append("<table><thead><tr><th style='width:3%'>Lp.</th><th style='width:9%'>Ozn.</th><th style='width:27%'>Element / parametry</th><th style='width:12%'>Model</th><th style='width:3%'>Szt.</th><th style='width:7%'>Cena jedn.</th><th style='width:7%'>Razem</th><th>Link · uwagi</th></tr></thead><tbody>")
    sub = 0.0
    for p in rows:
        L = links.get(p["id"]); u, src = unit_price(p, L)
        if L and L.get("url"):
            lab = {"oferta": "oferta", "produkt": "produkt"}.get(L.get("url_typ"), "szukaj")
            cell = f"<a href='{esc(L['url'])}'><b>{lab}</b>: {esc(L.get('tytul_oferty', ''))[:90]}</a>" + (f" · ok. {L['cena_pln']:.0f} zł" if L.get("cena_pln") else "") + f"<div class='small'>{esc(L.get('uwagi', ''))}</div>"
        else:
            cell = "<span class='small'>z magazynu</span>"
        lt = u * float(p["ilosc"]); sub += lt
        us = ("—" if u == 0 else pln2(u)) + ("" if src in ("oferta", "magazyn") or u == 0 else "<br><span class='small'>szac.</span>")
        H.append(f"<tr><td class='n'>{p['id']}</td><td class='tag'>{esc(p['ozn'])}</td><td>{esc(p['nazwa'])}</td><td>{esc(p['model'])}</td><td class='n'>{esc(p['ilosc'])}</td><td class='n'>{us}</td><td class='n'>{'—' if lt == 0 else pln(lt)}</td><td>{cell}</td></tr>")
    H.append(f"<tr><td colspan='6' style='text-align:right'><b>Razem koszyk {esc(k)}</b></td><td class='n'><b>{pln(sub)}</b></td><td class='small'>ceny z ofert tam, gdzie widoczne; reszta szacunek ±25 %</td></tr></tbody></table>")
    grand[k] = sub

# ---------------- 6. kosztorys porównawczy
H.append("<h2>6. Kosztorys v2 a rew. C</h2>")
H.append("<table><thead><tr><th>Koszyk</th><th class='n'>rew. C</th><th class='n'>v2</th><th class='n'>różnica</th></tr></thead><tbody>")
for k, lab in (("K1", "K1 aparatura"), ("K2", "K2 elektronika i sterowanie"), ("K3", "K3 transformator"), ("K5", "K5 magazyn")):
    c, v = totC.get(k, 0.0), grand.get(k, 0.0)
    H.append(f"<tr><td>{lab}</td><td class='n'>{pln(c)}</td><td class='n'>{pln(v)}</td><td class='n {'minus' if v <= c else 'plus'}'>{'−' if v <= c else '+'}{pln(abs(c - v))}</td></tr>")
gv = sum(grand.values())
H.append(f"<tr><td><b>Razem (brutto, orientacyjnie)</b></td><td class='n'><b>{pln(sumC)}</b></td><td class='n'><b>{pln(gv)}</b></td><td class='n minus'><b>−{pln(sumC - gv)}</b></td></tr>")
H.append(f"<tr><td>w tym obudowa</td><td class='n'>399 zł</td><td class='n'>{pln([unit_price(p, links.get(p['id']))[0] for p in bom['pozycje'] if p['ozn'] == '-U1'][0])}</td><td></td></tr>")
H.append("</tbody></table>")
H.append("<p class='small'>Nie uwzględniono: elementów montażowych (TH35, kanał, dławnice, kratki, tulejki – poza kosztorysem na Twoje życzenie), kosztów wysyłki (3 paczki), pozycji z magazynu. Wariant „ekran = telefon” obniża sumę o dalsze ok. 325 zł.</p>")
H.append("<p class='small'><b>Następny krok:</b> wskaż, które opcje z p. 4 przyjmujesz (zwłaszcza ekran i RCBO) – wtedy przerysuję schemat jako rew. D i zaktualizuję listę oraz schemat blokowy.</p>")
H.append("</body></html>")

html_path = os.path.join(ROOT, "docs", "_v2.html"); open(html_path, "w", encoding="utf-8").write("\n".join(H))
outp = os.path.join(ROOT, "docs", "pdf", "05_wersja_v2_tansze_rozwiazania.pdf")
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--no-pdf-header-footer", f"--print-to-pdf={outp}", f"file://{html_path}"], check=True, capture_output=True)
from pypdf import PdfReader
print("OK", outp, "stron:", len(PdfReader(outp).pages), "| v2:", round(gv), "| rew. C:", round(sumC))
