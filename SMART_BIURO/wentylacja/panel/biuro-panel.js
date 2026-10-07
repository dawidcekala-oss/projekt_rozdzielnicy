/*
 * biuro-panel — karta Lovelace z rzutem biura AmperePoint
 *
 * Rzut odwzorowuje szkic użytkownika: 4 kasetony (nasz typ, Gree GKH) i 5 jednostek
 * innego typu tej samej firmy. Geometria jest wpisana na stałe, bo pomieszczenie się
 * nie zmienia; konfiguracja mapuje tylko encje na sloty planu.
 *
 * Karta buduje DOM raz, a przy zmianie stanu tylko go łata — inaczej animacja
 * wentylatorów restartowałaby się przy każdym odświeżeniu encji.
 */

const PLAN = {
  w: 1205,
  h: 396,
  pokoje: [
    { x: 150, y: 117, w: 275, h: 185, r: 14, etykieta: 'Akwarium' },
    { x: 570, y: 252, w: 170, h: 135, r: 12, etykieta: 'Sala 1' },
    { x: 745, y: 252, w: 255, h: 138, r: 12, etykieta: 'Sala 2' },
    { x: 1005, y: 252, w: 190, h: 135, r: 12, etykieta: 'Sala 3' },
  ],
  linie: [
    { x1: 610, y1: 157, x2: 1155, y2: 157 },
    { x1: 883, y1: 60, x2: 883, y2: 157 },
  ],
  // Obszary bez wlasnych scian — sam podpis, bez prostokata.
  etykiety: [
    { x: 620, y: 234, tekst: 'Open space' },
    { x: 470, y: 378, tekst: 'Hala' },
  ],
};

// Sloty: pozycja środka znacznika w układzie planu.
const SLOTY = {
  k1: { x: 75, y: 311, typ: 'kaseton', dom: 'Biuro' },
  k2: { x: 74, y: 69, typ: 'kaseton', dom: 'Hala zachód' },
  k3: { x: 509, y: 69, typ: 'kaseton', dom: 'Hala północ' },
  k4: { x: 290, y: 210, typ: 'kaseton', dom: 'Akwarium' },
  j1: { x: 743, y: 143, typ: 'scienna', dom: 'Open space lewa' },
  j2: { x: 1065, y: 143, typ: 'scienna', dom: 'Open space prawa' },
  j3: { x: 653, y: 270, typ: 'scienna', dom: 'Sala 1' },
  j4: { x: 865, y: 268, typ: 'scienna', dom: 'Sala 2' },
  j5: { x: 1115, y: 268, typ: 'scienna', dom: 'Sala 3' },
};

// Prędkość obrotu wirnika = rzeczywisty bieg wentylatora z magistrali.
const OBROT = { niski: '3.2s', sredni: '1.7s', wysoki: '0.95s' };

const IKONA_DETAL = `
<svg viewBox="0 0 24 24" aria-hidden="true">
  <path d="M4 7h10M18 7h2M4 12h4M12 12h8M4 17h12M20 17h0"/>
  <circle cx="16" cy="7" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="17" r="2"/>
</svg>`;

const IKONA_WIATRAK = `
<svg viewBox="0 0 24 24" class="wirnik" aria-hidden="true">
  <path d="M12 12c0-4 1.2-6.2 3.4-6.2 1.7 0 2.8 1.3 2.8 2.9 0 2.3-2.4 3.3-6.2 3.3z"/>
  <path d="M12 12c3.4 2 4.6 4.2 3.5 6.1-.85 1.5-2.5 1.85-3.9 1.05-2-1.15-1.6-3.7.4-7.15z"/>
  <path d="M12 12c-3.4 2-5.8 1.9-6.9 0-.85-1.5-.25-3.1 1.15-3.9 2-1.15 3.75.75 5.75 3.9z"/>
  <circle cx="12" cy="12" r="1.9" class="piasta"/>
</svg>`;

const STYL = `
:host {
  display:block;
  /* Kolory biorą się z motywu Home Assistanta; wartości po przecinku to zapas,
     dzięki któremu karta wygląda poprawnie także poza HA (podgląd offline). */
  --akcent:       var(--state-climate-cool-color, #38bdf8);
  --zly:          var(--error-color, #f05252);
  --spi:          color-mix(in srgb, var(--primary-text-color, #e8eaed) 34%, transparent);
  --kreska:       var(--divider-color, rgba(255,255,255,.10));
  --kreska-mocna: color-mix(in srgb, var(--primary-text-color, #e8eaed) 38%, transparent);
  --tlo-plytki:   var(--ha-card-background, var(--card-background-color, #16181d));
}
*, *::before, *::after { box-sizing:border-box; }

.karta {
  position:relative;
  background:var(--ha-card-background, var(--card-background-color, #16181d));
  color:var(--primary-text-color, #e8eaed);
  border-radius:var(--ha-card-border-radius, 16px);
  box-shadow:var(--ha-card-box-shadow, 0 2px 14px rgba(0,0,0,.28));
  overflow:hidden;
  min-height:430px;
  font-family:var(--paper-font-body1_-_font-family, Inter, Roboto, system-ui, sans-serif);
}

/* ---- pasek górny ---- */
.gora { display:flex; align-items:center; gap:16px; padding:18px 22px 14px; flex-wrap:wrap; }
.tytul { font-size:1.05rem; font-weight:600; letter-spacing:.2px; margin:0; }
.podtytul { font-size:.74rem; opacity:.55; margin:2px 0 0; letter-spacing:.3px; }
.rozpychacz { flex:1 1 auto; }

.chipy { display:flex; gap:8px; flex-wrap:wrap; }
.chip {
  display:inline-flex; align-items:center; gap:7px;
  padding:6px 12px; border-radius:999px; font-size:.76rem; font-weight:500;
  background:color-mix(in srgb, var(--primary-text-color, #e8eaed) 7%, transparent);
  border:1px solid color-mix(in srgb, var(--primary-text-color, #e8eaed) 9%, transparent);
  white-space:nowrap;
}
.chip b { font-weight:650; font-variant-numeric:tabular-nums; }
.kropka { width:7px; height:7px; border-radius:50%; background:var(--akcent); }
.kropka.spi { background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 28%, transparent); }
.kropka.alarm { background:var(--zly); }

.przycisk {
  display:inline-flex; align-items:center; gap:8px;
  padding:7px 14px; border-radius:999px; cursor:pointer; font-size:.78rem; font-weight:550;
  background:color-mix(in srgb, var(--akcent) 14%, transparent);
  border:1px solid color-mix(in srgb, var(--akcent) 30%, transparent);
  color:var(--akcent);
  transition:background .18s ease, transform .12s ease;
  user-select:none;
}
.przycisk:hover { background:color-mix(in srgb, var(--akcent) 22%, transparent); }
.przycisk:active { transform:scale(.97); }
.strzalka { transition:transform .22s ease; font-size:.7em; }
.otwarte .strzalka { transform:rotate(180deg); }

/* ---- lista automatyzacji ---- */
.automatyzacje {
  display:grid; grid-template-rows:0fr;
  transition:grid-template-rows .3s cubic-bezier(.4,0,.2,1);
  border-top:1px solid transparent;
}
.automatyzacje.otwarte { grid-template-rows:1fr; border-top-color:var(--kreska); }
.automatyzacje > div { overflow:hidden; }
.auto-lista { padding:6px 14px 12px; display:flex; flex-direction:column; gap:2px; }
.auto-wiersz {
  display:flex; align-items:center; gap:12px; padding:9px 12px; border-radius:10px;
  transition:background .15s ease;
}
.auto-wiersz:hover { background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 5%, transparent); }
.auto-nazwa { flex:1 1 auto; font-size:.83rem; }
.auto-opis { font-size:.7rem; opacity:.5; margin-top:2px; }
.auto-pusto { padding:14px 16px; font-size:.8rem; opacity:.5; }

.pstryczek {
  position:relative; width:36px; height:20px; border-radius:999px; cursor:pointer; flex:0 0 auto;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 18%, transparent);
  transition:background .2s ease;
}
.pstryczek::after {
  content:''; position:absolute; top:3px; left:3px; width:14px; height:14px; border-radius:50%;
  background:#fff; transition:transform .2s cubic-bezier(.4,0,.2,1);
}
.pstryczek.wl { background:var(--akcent); }
.pstryczek.wl::after { transform:translateX(16px); }

/* ---- rzut ---- */
.scena { position:relative; padding:6px 22px 22px; }
.plan { position:relative; width:100%; aspect-ratio:1205/396; }
.plan svg { position:absolute; inset:0; width:100%; height:100%; }
.obrys { fill:none; stroke:var(--kreska-mocna); stroke-width:2.2; }
.pokoj { fill:color-mix(in srgb, var(--primary-text-color,#e8eaed) 3%, transparent); stroke:var(--kreska-mocna); stroke-width:1.8; }
.mebel { stroke:var(--kreska-mocna); stroke-width:1.8; stroke-linecap:round; }
.nazwa-pokoju { fill:var(--primary-text-color,#e8eaed); opacity:.26; font-size:11px; letter-spacing:1.4px; text-transform:uppercase; }

/* ---- znacznik jednostki ---- */
.jedn {
  position:absolute; transform:translate(-50%,-50%);
  display:flex; flex-direction:column; align-items:center; gap:5px;
  cursor:pointer; --barwa:var(--spi);
}
.jedn.pracuje { --barwa:var(--akcent); }
.jedn.brak { --barwa:var(--spi); cursor:default; }
.jedn.alarm { --barwa:var(--zly); }

.plytka {
  position:relative; display:grid; place-items:center;
  border-radius:12px;
  background:color-mix(in srgb, var(--barwa) 13%, var(--tlo-plytki));
  border:1.5px solid color-mix(in srgb, var(--barwa) 45%, transparent);
  transition:border-color .3s ease, background .3s ease, box-shadow .3s ease;
}
.jedn.pracuje .plytka { box-shadow:0 0 0 4px color-mix(in srgb, var(--akcent) 9%, transparent); }
.jedn:not(.brak):hover .plytka { border-color:color-mix(in srgb, var(--barwa) 80%, transparent); }
.typ-kaseton .plytka { width:clamp(40px,4vw,64px); aspect-ratio:1; }
.typ-scienna .plytka { width:clamp(58px,5.6vw,96px); aspect-ratio:3.4/1; border-radius:8px; }

.wirnik { width:58%; height:58%; fill:var(--barwa); opacity:.9; transform-origin:50% 50%; }
.typ-scienna .wirnik { width:auto; height:64%; }
.jedn.pracuje .wirnik { animation:kreci var(--tempo,1.7s) linear infinite; }
.jedn.brak .wirnik { opacity:.22; }
.jedn.brak .plytka { border-style:dashed; background:transparent; }
.piasta { fill:var(--tlo-plytki); }
@keyframes kreci { to { transform:rotate(360deg); } }
@media (prefers-reduced-motion:reduce) { .jedn.pracuje .wirnik { animation:none; } }

.odznaka {
  position:absolute; top:-5px; left:-5px; width:15px; height:15px; border-radius:50%;
  display:grid; place-items:center; font-size:9px; font-weight:700;
  background:var(--zly); color:#fff; box-shadow:0 0 0 2px var(--tlo-plytki);
}
.odznaka[hidden] { display:none; }

/* Widoczna furtka do szczegółów — użytkownik ma wiedzieć, że jest w co kliknąć. */
.ikona-detal {
  position:absolute; top:-6px; right:-6px; width:18px; height:18px; border-radius:50%;
  display:grid; place-items:center; color:var(--barwa);
  background:var(--tlo-plytki);
  border:1px solid color-mix(in srgb, var(--barwa) 50%, transparent);
  opacity:.72; transition:opacity .2s ease, transform .15s ease, background .2s ease;
}
.ikona-detal svg { width:10px; height:10px; fill:none; stroke:currentColor; stroke-width:2.2; stroke-linecap:round; }
.ikona-detal circle { fill:var(--tlo-plytki); }
.jedn:not(.brak):hover .ikona-detal { opacity:1; transform:scale(1.15); background:color-mix(in srgb, var(--barwa) 20%, var(--tlo-plytki)); }
.jedn.brak .ikona-detal { display:none; }

.opis {
  display:flex; flex-direction:column; align-items:center; line-height:1.3; pointer-events:none;
  padding:2px 6px; border-radius:7px;
  background:color-mix(in srgb, var(--tlo-plytki) 82%, transparent);
  backdrop-filter:blur(2px);
}
.opis .nazwa { font-size:clamp(9px,.72vw,12px); font-weight:600; opacity:.8; letter-spacing:.2px; white-space:nowrap; }
.opis .dane { font-size:clamp(8.5px,.68vw,11px); opacity:.6; font-variant-numeric:tabular-nums; white-space:nowrap; }
.opis .dane b { font-weight:650; opacity:.95; color:var(--barwa); }

/* ---- sekcja automatyzacji pod rzutem ---- */
.auto-sekcja { padding:2px 22px 24px; }
.auto-sekcja-gora { display:flex; align-items:center; gap:14px; padding:12px 2px 12px; border-top:1px solid var(--kreska); }
.auto-sekcja-tytul { font-size:.78rem; text-transform:uppercase; letter-spacing:1.1px; opacity:.6; font-weight:600; }
.auto-sekcja-pod { font-size:.74rem; opacity:.45; flex:1 1 auto; }
.auto-siatka { display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:10px; }
.grupa {
  display:flex; flex-direction:column; gap:6px; padding:12px 14px; border-radius:12px; cursor:pointer;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 5%, transparent);
  border:1px solid var(--kreska); transition:background .15s ease, border-color .15s ease;
}
.grupa:hover { background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 8%, transparent); border-color:var(--kreska-mocna); }
.grupa.wykonano { border-color:var(--akcent); background:color-mix(in srgb, var(--akcent) 12%, transparent); }
.g-gora { display:flex; align-items:center; gap:8px; }
.g-nazwa { flex:1 1 auto; font-size:.9rem; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.g-opis { font-size:.76rem; opacity:.6; line-height:1.4; }
.g-akcja {
  flex:0 0 auto; width:28px; height:28px; border-radius:9px; display:grid; place-items:center; font-size:13px;
  background:color-mix(in srgb, var(--akcent) 16%, transparent); color:var(--akcent); transition:background .15s ease;
}
.g-akcja:hover { background:color-mix(in srgb, var(--akcent) 32%, transparent); }
.g-usun { background:transparent; color:inherit; opacity:.4; }
.g-usun:hover { opacity:1; background:color-mix(in srgb, var(--zly) 18%, transparent); color:var(--zly); }
.auto-pusto-kafel {
  grid-column:1 / -1; padding:16px 18px; border-radius:12px; font-size:.82rem; line-height:1.5; opacity:.6;
  border:1px dashed var(--kreska-mocna);
}

/* ---- formularz automatyzacji w szufladzie ---- */
.pole { display:flex; flex-direction:column; gap:6px; }
.pole input[type=text], .pole input[type=number], .pole select {
  font:inherit; font-size:.85rem; padding:8px 10px; border-radius:9px; color:inherit;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 7%, transparent);
  border:1px solid var(--kreska-mocna); outline:none; width:100%;
}
.pole input:focus, .pole select:focus { border-color:var(--akcent); }
.pole select option { color:#111; }
.wybor-jedn { display:flex; flex-direction:column; gap:4px; }
.wybor-jedn label {
  display:flex; align-items:center; gap:10px; padding:7px 10px; border-radius:9px; font-size:.83rem; cursor:pointer;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 5%, transparent);
}
.wybor-jedn input { accent-color:var(--akcent); width:16px; height:16px; }
.wybor-jedn .brak-mod { opacity:.4; }
.segmenty.wiele { flex-wrap:wrap; }
.segmenty.wiele .segment { flex:1 1 30%; }
.komendy { display:flex; flex-direction:column; gap:14px; }
.komenda-wiersz { display:flex; flex-direction:column; gap:8px; padding:10px 12px; border-radius:11px; border:1px solid var(--kreska); }
.komenda-gora { display:flex; align-items:center; justify-content:space-between; }
.fParam:empty { display:none; }
#fDodajKomende { align-self:flex-start; }
.przyciski-form { display:flex; gap:8px; justify-content:flex-end; }
.przycisk.glowny { background:var(--akcent); color:#fff; border-color:transparent; }
.przycisk.glowny:hover { filter:brightness(1.1); }
.blad-form { color:var(--zly); font-size:.78rem; }

/* ---- panel szczegółów ---- */
.zaslona {
  position:absolute; inset:0; border-radius:inherit; background:rgba(0,0,0,.42); backdrop-filter:blur(2px);
  opacity:0; pointer-events:none; transition:opacity .25s ease; z-index:5;
}
.zaslona.widoczna { opacity:1; pointer-events:auto; }
.szuflada {
  position:absolute; top:0; right:0; bottom:0; width:min(340px,86%);
  background:var(--ha-card-background, var(--card-background-color, #16181d));
  border-left:1px solid var(--kreska); z-index:6;
  transform:translateX(100%); transition:transform .3s cubic-bezier(.4,0,.2,1);
  display:flex; flex-direction:column; box-shadow:-12px 0 40px rgba(0,0,0,.35);
}
.szuflada.widoczna { transform:none; }
.sz-gora { padding:18px 20px 14px; border-bottom:1px solid var(--kreska); }
.sz-tytul { font-size:1rem; font-weight:650; margin:0; }
.sz-pod { font-size:.72rem; opacity:.5; margin:3px 0 0; }
.zamknij {
  position:absolute; top:14px; right:14px; width:28px; height:28px; border-radius:8px;
  display:grid; place-items:center; cursor:pointer; opacity:.55; font-size:15px; line-height:1;
}
.zamknij:hover { opacity:1; background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 8%, transparent); }
.sz-tresc { padding:16px 20px 22px; overflow-y:auto; overflow-x:hidden; display:flex; flex-direction:column; gap:20px; }

.siatka { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.kafel {
  padding:11px 13px; border-radius:11px;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 5%, transparent);
}
.kafel .etyk { font-size:.66rem; opacity:.5; text-transform:uppercase; letter-spacing:.7px; }
.kafel .wart { font-size:1.05rem; font-weight:600; margin-top:3px; font-variant-numeric:tabular-nums; }
.kafel .wart small { font-size:.62em; opacity:.55; font-weight:500; margin-left:2px; }

.sekcja-tytul { font-size:.68rem; text-transform:uppercase; letter-spacing:1px; opacity:.45; margin-bottom:9px; }
.wiersz { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:7px 0; }
.wiersz .etyk { font-size:.83rem; }

.termostat { display:flex; align-items:center; justify-content:space-between; gap:14px; }
.krok {
  width:36px; height:36px; border-radius:11px; display:grid; place-items:center; cursor:pointer;
  font-size:19px; font-weight:400; line-height:1; user-select:none;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 8%, transparent);
  transition:background .15s ease, transform .1s ease;
}
.krok:hover { background:color-mix(in srgb, var(--akcent) 22%, transparent); }
.krok:active { transform:scale(.92); }
.krok.nieczynny { opacity:.28; pointer-events:none; }
.nastawa-duza { font-size:2.1rem; font-weight:300; font-variant-numeric:tabular-nums; letter-spacing:-1px; }
.nastawa-duza small { font-size:.42em; opacity:.5; margin-left:1px; }

.segmenty { display:flex; gap:5px; }
.segment {
  flex:1 1 0; text-align:center; padding:8px 4px; border-radius:9px; cursor:pointer;
  font-size:.74rem; font-weight:500;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 6%, transparent);
  border:1px solid transparent; transition:all .15s ease; white-space:nowrap;
}
.segment:hover { background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 11%, transparent); }
.segment.wybrany {
  background:color-mix(in srgb, var(--akcent) 17%, transparent);
  border-color:color-mix(in srgb, var(--akcent) 42%, transparent);
  color:var(--akcent);
}

.ostrzezenie {
  display:flex; gap:10px; padding:11px 13px; border-radius:11px; font-size:.78rem; line-height:1.45;
  background:color-mix(in srgb, var(--zly) 12%, transparent);
  border:1px solid color-mix(in srgb, var(--zly) 30%, transparent);
}
.info-brak {
  padding:13px; border-radius:11px; font-size:.79rem; line-height:1.5; opacity:.62;
  background:color-mix(in srgb, var(--primary-text-color,#e8eaed) 5%, transparent);
}
`;

class BiuroPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._zbudowane = false;
    this._wybrany = null;
    this._autoOtwarte = false;
    this._grupy = null;          // lista skryptow HA utworzonych z tej karty (null = nie wczytano)
    this._wczytujeGrupy = false;
    this._formularz = null;      // otwarty formularz: { id, alias, jednostki, komenda } lub null
  }

  setConfig(config) {
    this._config = config || {};
    this._jednostki = {};
    (this._config.jednostki || []).forEach((j) => {
      if (j && j.slot && SLOTY[j.slot]) this._jednostki[j.slot] = j;
    });
    this._zbudowane = false;
    if (this.shadowRoot) this.shadowRoot.innerHTML = '';
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._zbudowane) this._zbuduj();
    this._odswiez();
    if (this._grupy === null && !this._wczytujeGrupy) this._ladujGrupy();
    else this._sprawdzNoweSkrypty();
  }

  getCardSize() { return 9; }

  // ---------- odczyt encji ----------
  _st(id) {
    if (!id || !this._hass) return null;
    const e = this._hass.states[id];
    return e ? e.state : null;
  }
  _jest(id) { return this._st(id) === 'on'; }
  _liczba(id) {
    const v = parseFloat(this._st(id));
    return Number.isFinite(v) ? v : null;
  }

  _dane(slot) {
    const cfg = this._jednostki[slot];
    const meta = SLOTY[slot];
    if (!cfg || !cfg.encje) {
      return { podlaczona: false, nazwa: (cfg && cfg.nazwa) || meta.dom, meta };
    }
    const e = cfg.encje;
    const bieg = this._st(e.bieg);
    return {
      podlaczona: true,
      nazwa: cfg.nazwa || meta.dom,
      meta,
      encje: e,
      online: e.online ? this._jest(e.online) : true,
      pracuje: this._jest(e.pracuje),
      bieg: bieg,
      temperatura: this._liczba(e.temperatura),
      wymiennik: this._liczba(e.wymiennik),
      nastawa: this._liczba(e.nastawa),
      tryb: this._st(e.tryb),
      biegZadany: this._st(e.bieg_zadany),
      klapy: e.klapy ? this._jest(e.klapy) : null,
      wlaczona: e.wlacznik ? this._jest(e.wlacznik) : null,
      alarm: e.alarm ? this._jest(e.alarm) : false,
      potwierdzenie: this._st(e.potwierdzenie),
    };
  }

  _automatyzacje() {
    if (!this._hass) return [];
    const jawne = this._config.automatyzacje;
    const idki = jawne && jawne.length
      ? jawne
      : Object.keys(this._hass.states).filter((k) => k.startsWith('automation.'));
    return idki
      .map((id) => this._hass.states[id])
      .filter(Boolean)
      .map((e) => ({
        id: e.entity_id,
        nazwa: (e.attributes && e.attributes.friendly_name) || e.entity_id,
        wl: e.state === 'on',
        ostatnie: e.attributes && e.attributes.last_triggered,
      }))
      .sort((a, b) => a.nazwa.localeCompare(b.nazwa, 'pl'));
  }

  // ---------- budowa DOM ----------
  _zbuduj() {
    const r = this.shadowRoot;
    r.innerHTML = `<style>${STYL}</style>${this._szkielet()}`;

    this._el = {
      chipy: r.querySelector('#chipy'),
      przyciskAuto: r.querySelector('#przyciskAuto'),
      listaAuto: r.querySelector('#listaAuto'),
      wrapAuto: r.querySelector('#wrapAuto'),
      zaslona: r.querySelector('#zaslona'),
      szuflada: r.querySelector('#szuflada'),
    };

    this._el.przyciskAuto.addEventListener('click', () => {
      this._autoOtwarte = !this._autoOtwarte;
      this._el.wrapAuto.classList.toggle('otwarte', this._autoOtwarte);
      this._el.przyciskAuto.classList.toggle('otwarte', this._autoOtwarte);
    });
    this._el.zaslona.addEventListener('click', () => this._zamknij());
    r.querySelector('#zamknij').addEventListener('click', () => this._zamknij());
    this._el.listaGrup = r.querySelector('#listaGrup');
    r.querySelector('#dodajGrupe').addEventListener('click', () => this._otworzFormularz(null));

    r.querySelectorAll('.jedn').forEach((el) => {
      el.addEventListener('click', () => {
        const slot = el.dataset.slot;
        if (this._jednostki[slot] && this._jednostki[slot].encje) this._otworz(slot);
      });
    });

    this._zbudowane = true;
  }

  _szkielet() {
    const znaczniki = Object.entries(SLOTY).map(([slot, s]) => {
      const lewo = ((s.x / PLAN.w) * 100).toFixed(3);
      const gora = ((s.y / PLAN.h) * 100).toFixed(3);
      return `
      <div class="jedn typ-${s.typ}" data-slot="${slot}" style="left:${lewo}%;top:${gora}%">
        <div class="plytka">${IKONA_WIATRAK}<span class="odznaka" hidden>!</span><span class="ikona-detal">${IKONA_DETAL}</span></div>
        <div class="opis"><span class="nazwa"></span><span class="dane"></span></div>
      </div>`;
    }).join('');

    const pokoje = PLAN.pokoje.map((p) => `
      <rect class="pokoj" x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="${p.r}"/>
      <text class="nazwa-pokoju" x="${p.x + 12}" y="${p.y + p.h - 11}">${p.etykieta}</text>`).join('');

    const linie = PLAN.linie.map((l) =>
      `<line class="mebel" x1="${l.x1}" y1="${l.y1}" x2="${l.x2}" y2="${l.y2}"/>`).join('');

    const etykiety = (PLAN.etykiety || []).map((e) =>
      `<text class="nazwa-pokoju" x="${e.x}" y="${e.y}">${e.tekst}</text>`).join('');

    return `
    <div class="karta">
      <div class="gora">
        <div>
          <p class="tytul">Klimatyzacja biura</p>
          <p class="podtytul">AmperePoint · rzut kondygnacji</p>
        </div>
        <div class="rozpychacz"></div>
        <div class="chipy" id="chipy"></div>
        <div class="przycisk" id="przyciskAuto">Reguły HA <span class="strzalka">▼</span></div>
      </div>

      <div class="automatyzacje" id="wrapAuto"><div><div class="auto-lista" id="listaAuto"></div></div></div>

      <div class="scena">
        <div class="plan">
          <svg viewBox="0 0 ${PLAN.w} ${PLAN.h}" preserveAspectRatio="xMidYMid meet">
            <rect class="obrys" x="1.5" y="1.5" width="${PLAN.w - 3}" height="${PLAN.h - 3}" rx="18"/>
            ${pokoje}${linie}${etykiety}
          </svg>
          ${znaczniki}
        </div>
      </div>

      <div class="auto-sekcja">
        <div class="auto-sekcja-gora">
          <span class="auto-sekcja-tytul">Automatyzacje</span>
          <span class="auto-sekcja-pod">jedna komenda dla wielu jednostek · zapisane jako skrypty w Home Assistancie</span>
          <div class="przycisk" id="dodajGrupe">+ Dodaj</div>
        </div>
        <div class="auto-siatka" id="listaGrup"><div class="auto-pusto-kafel">Wczytuję…</div></div>
      </div>

      <div class="zaslona" id="zaslona"></div>
      <div class="szuflada" id="szuflada">
        <div class="sz-gora">
          <p class="sz-tytul" id="szTytul">—</p>
          <p class="sz-pod" id="szPod">—</p>
          <div class="zamknij" id="zamknij">✕</div>
        </div>
        <div class="sz-tresc" id="szTresc"></div>
      </div>
    </div>`;
  }

  // ---------- odświeżanie ----------
  _odswiez() {
    if (!this._zbudowane) return;
    const r = this.shadowRoot;
    let pracujace = 0, zModulem = 0, offline = 0, alarmy = 0, sumaT = 0, ileT = 0;

    Object.keys(SLOTY).forEach((slot) => {
      const d = this._dane(slot);
      const el = r.querySelector(`.jedn[data-slot="${slot}"]`);
      if (!el) return;

      el.classList.toggle('brak', !d.podlaczona);
      el.classList.toggle('pracuje', !!d.pracuje);
      el.classList.toggle('alarm', !!d.alarm);
      if (d.pracuje && d.bieg && OBROT[d.bieg]) el.style.setProperty('--tempo', OBROT[d.bieg]);

      const odznaka = el.querySelector('.odznaka');
      odznaka.hidden = !(d.alarm || (d.podlaczona && d.online === false));

      el.querySelector('.nazwa').textContent = d.nazwa;
      const dane = el.querySelector('.dane');
      if (!d.podlaczona) {
        dane.innerHTML = '<span style="opacity:.7">bez modułu</span>';
      } else if (d.online === false) {
        zModulem++; offline++;
        dane.innerHTML = '<span style="opacity:.8">brak łączności</span>';
      } else {
        zModulem++;
        if (d.pracuje) pracujace++;
        if (d.alarm) alarmy++;
        if (d.temperatura !== null) { sumaT += d.temperatura; ileT++; }
        const t = d.temperatura !== null ? `<b>${d.temperatura}°</b>` : '—';
        const n = d.nastawa !== null ? ` → ${d.nastawa}°` : '';
        dane.innerHTML = `${t}${n}`;
      }
      el.title = d.podlaczona ? `${d.nazwa} — kliknij, aby otworzyć sterowanie` : `${d.nazwa} — moduł jeszcze niezamontowany`;
    });

    const srednia = ileT ? (sumaT / ileT).toFixed(1) : null;
    const bezModulu = Object.keys(SLOTY).length - zModulem;
    this._el.chipy.innerHTML = [
      `<span class="chip"><span class="kropka ${pracujace ? '' : 'spi'}"></span>${pracujace} z ${zModulem} pracuje</span>`,
      srednia !== null ? `<span class="chip">średnio <b>${srednia}°C</b></span>` : '',
      bezModulu ? `<span class="chip"><span class="kropka spi"></span>${bezModulu} bez modułu</span>` : '',
      offline ? `<span class="chip"><span class="kropka alarm"></span>${offline} bez łączności</span>` : '',
      alarmy ? `<span class="chip"><span class="kropka alarm"></span>${alarmy} bez potwierdzenia</span>` : '',
    ].filter(Boolean).join('');

    this._rysujAutomatyzacje();
    if (this._wybrany) this._rysujSzuflade(this._wybrany);
  }

  _rysujAutomatyzacje() {
    const lista = this._automatyzacje();
    const cel = this._el.listaAuto;
    if (!lista.length) {
      cel.innerHTML = '<div class="auto-pusto">Brak zdefiniowanych automatyzacji.</div>';
      return;
    }
    cel.innerHTML = lista.map((a) => {
      const kiedy = a.ostatnie
        ? new Date(a.ostatnie).toLocaleString('pl-PL', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
        : 'jeszcze nie uruchamiana';
      return `<div class="auto-wiersz">
        <div style="flex:1 1 auto">
          <div class="auto-nazwa">${a.nazwa}</div>
          <div class="auto-opis">ostatnio: ${kiedy}</div>
        </div>
        <div class="pstryczek ${a.wl ? 'wl' : ''}" data-auto="${a.id}"></div>
      </div>`;
    }).join('');
    cel.querySelectorAll('.pstryczek').forEach((p) => {
      p.addEventListener('click', () => {
        const id = p.dataset.auto;
        const wl = p.classList.contains('wl');
        this._hass.callService('automation', wl ? 'turn_off' : 'turn_on', { entity_id: id });
      });
    });
  }

  // ---------- szuflada ----------
  _otworz(slot) {
    this._wybrany = slot;
    this._rysujSzuflade(slot);
    this._el.zaslona.classList.add('widoczna');
    this._el.szuflada.classList.add('widoczna');
  }
  _zamknij() {
    this._wybrany = null;
    this._formularz = null;
    this._el.zaslona.classList.remove('widoczna');
    this._el.szuflada.classList.remove('widoczna');
  }

  // ---------- automatyzacje (grupowe komendy zapisane jako skrypty HA) ----------
  // Kazda automatyzacja to skrypt Home Assistanta o identyfikatorze klima_panel_*.
  // Skrypt jest trwaly (scripts.yaml), widoczny w HA i uruchamialny z dowolnego miejsca;
  // karta trzyma w polu `description` skryptu opis w JSON, zeby odtworzyc formularz.
  static get KOMENDY() {
    return {
      wl:    { nazwa: 'Włącz',           opis: () => 'włącz' },
      wyl:   { nazwa: 'Wyłącz',          opis: () => 'wyłącz' },
      plus:  { nazwa: '+1 °C',           opis: () => 'nastawa +1 °C' },
      minus: { nazwa: '−1 °C',           opis: () => 'nastawa −1 °C' },
      temp:  { nazwa: 'Ustaw temperaturę', opis: (k) => `nastawa ${k.wartosc} °C` },
      tryb:  { nazwa: 'Tryb',            opis: (k) => `tryb: ${k.wartosc}` },
      bieg:  { nazwa: 'Bieg',            opis: (k) => `bieg: ${k.wartosc}` },
    };
  }

  _jednostkiZModulem() {
    return Object.keys(SLOTY).filter((slot) => this._jednostki[slot] && this._jednostki[slot].encje);
  }

  _nazwaSlotu(slot) {
    const cfg = this._jednostki[slot];
    return (cfg && cfg.nazwa) || (SLOTY[slot] && SLOTY[slot].dom) || slot;
  }

  _skryptyPanelu() {
    if (!this._hass) return [];
    return Object.keys(this._hass.states).filter((id) => id.startsWith('script.klima_panel_')).sort();
  }

  async _ladujGrupy() {
    if (!this._hass || !this._hass.callApi) { this._grupy = []; this._rysujGrupy(); return; }
    this._wczytujeGrupy = true;
    const grupy = [];
    for (const id of this._skryptyPanelu()) {
      const objectId = id.slice('script.'.length);
      let meta = null;
      try {
        const cfg = await this._hass.callApi('GET', `config/script/config/${objectId}`);
        try { meta = JSON.parse(cfg.description || ''); } catch (e) { meta = null; }
        grupy.push({ id: objectId, entity: id, alias: cfg.alias || objectId, jednostki: (meta && meta.jednostki) || [], komendy: BiuroPanel._komendyZMeta(meta) });
      } catch (e) {
        grupy.push({ id: objectId, entity: id, alias: (this._hass.states[id].attributes || {}).friendly_name || objectId, jednostki: [], komendy: [] });
      }
    }
    this._grupy = grupy;
    this._wczytujeGrupy = false;
    this._rysujGrupy();
  }

  // Skrypty pojawiaja sie w hass.states chwile po zapisie - wtedy doczytujemy ich opis.
  _sprawdzNoweSkrypty() {
    if (!this._grupy || this._wczytujeGrupy) return;
    const teraz = this._skryptyPanelu();
    const znane = this._grupy.map((g) => g.entity).sort();
    if (teraz.length !== znane.length || teraz.some((id, i) => id !== znane[i])) this._ladujGrupy();
  }

  static _komendyZMeta(meta) {
    if (!meta) return [];
    if (Array.isArray(meta.komendy)) return meta.komendy;
    if (meta.komenda) return [meta.komenda];
    return [];
  }

  _opisKomend(komendy) {
    const K = BiuroPanel.KOMENDY;
    const o = (komendy || []).filter((k) => k && K[k.typ]).map((k) => K[k.typ].opis(k));
    return o.length ? o.join(', ') : 'skrypt HA';
  }

  _opisGrupy(g) {
    const kom = this._opisKomend(g.komendy);
    const jedn = g.jednostki.length ? g.jednostki.map((s) => this._nazwaSlotu(s)).join(', ') : '';
    return jedn ? `${kom} · ${jedn}` : kom;
  }

  _rysujGrupy() {
    const cel = this._el && this._el.listaGrup;
    if (!cel) return;
    if (this._grupy === null) { cel.innerHTML = '<div class="auto-pusto-kafel">Wczytuję…</div>'; return; }
    if (!this._grupy.length) {
      cel.innerHTML = '<div class="auto-pusto-kafel">Brak automatyzacji. „+ Dodaj" tworzy jedną komendę dla wybranych jednostek, np. „wszystkie +1 °C" albo „wyłącz wszystkie". Każda zapisana automatyzacja dostaje tu kafelek z przyciskiem wykonania.</div>';
      return;
    }
    cel.innerHTML = this._grupy.map((g) => `
      <div class="grupa" data-id="${g.id}" title="kliknij, aby edytować">
        <div class="g-gora">
          <span class="g-nazwa">${g.alias}</span>
          <span class="g-akcja g-wykonaj" data-id="${g.id}" title="wykonaj teraz">▶</span>
          <span class="g-akcja g-usun" data-id="${g.id}" title="usuń">✕</span>
        </div>
        <div class="g-opis">${this._opisGrupy(g)}</div>
      </div>`).join('');
    cel.querySelectorAll('.g-wykonaj').forEach((b) => b.addEventListener('click', (ev) => { ev.stopPropagation(); this._wykonajGrupe(b.dataset.id); }));
    cel.querySelectorAll('.g-usun').forEach((b) => b.addEventListener('click', (ev) => { ev.stopPropagation(); this._usunGrupe(b.dataset.id); }));
    cel.querySelectorAll('.grupa').forEach((w) => w.addEventListener('click', () => {
      const g = this._grupy.find((x) => x.id === w.dataset.id);
      if (g) this._otworzFormularz(g);
    }));
  }

  async _wykonajGrupe(id) {
    if (!this._hass) return;
    const g = this._grupy.find((x) => x.id === id);
    try {
      await this._hass.callService('script', 'turn_on', { entity_id: `script.${id}` });
      const w = this._el.listaGrup.querySelector(`.grupa[data-id="${id}"]`);
      if (w) { w.classList.add('wykonano'); setTimeout(() => w.classList.remove('wykonano'), 1500); }
    } catch (e) {
      alert(`Nie udało się uruchomić „${g ? g.alias : id}": ${e.message || e}`);
    }
  }

  async _usunGrupe(id) {
    const g = this._grupy.find((x) => x.id === id);
    if (!confirm(`Usunąć automatyzację „${g ? g.alias : id}"?`)) return;
    try {
      await this._hass.callApi('DELETE', `config/script/config/${id}`);
      this._grupy = this._grupy.filter((x) => x.id !== id);
      this._rysujGrupy();
    } catch (e) {
      alert(`Nie udało się usunąć: ${e.message || e}`);
    }
  }

  // Sekwencja skryptu: dla kazdej jednostki kolejno wszystkie komendy. continue_on_error,
  // zeby jednostka bez lacznosci nie zatrzymala reszty. Przelacznik szablonowy sam czeka
  // 2 s po komendzie, wiec kolejne rozkazy do tego samego modulu nie nakladaja sie.
  _krokKomendy(e, komenda) {
    if (komenda.typ === 'wl' && e.wlacznik) return { action: 'switch.turn_on', target: { entity_id: e.wlacznik } };
    if (komenda.typ === 'wyl' && e.wlacznik) return { action: 'switch.turn_off', target: { entity_id: e.wlacznik } };
    if ((komenda.typ === 'plus' || komenda.typ === 'minus') && e.nastawa) {
      const d = komenda.typ === 'plus' ? 1 : -1;
      return { action: 'number.set_value', target: { entity_id: e.nastawa },
               data: { value: `{{ [16, [30, (states('${e.nastawa}') | float(22)) + (${d})] | min] | max | int }}` } };
    }
    if (komenda.typ === 'temp' && e.nastawa) return { action: 'number.set_value', target: { entity_id: e.nastawa }, data: { value: Number(komenda.wartosc) } };
    if (komenda.typ === 'tryb' && e.tryb) return { action: 'select.select_option', target: { entity_id: e.tryb }, data: { option: komenda.wartosc } };
    if (komenda.typ === 'bieg' && e.bieg_zadany) return { action: 'select.select_option', target: { entity_id: e.bieg_zadany }, data: { option: komenda.wartosc } };
    return null;
  }

  _budujSekwencje(jednostki, komendy) {
    const kroki = [];
    for (const slot of jednostki) {
      const e = (this._jednostki[slot] || {}).encje;
      if (!e) continue;
      for (const k of komendy) {
        const krok = this._krokKomendy(e, k);
        if (krok) { krok.continue_on_error = true; kroki.push(krok); }
      }
    }
    return kroki;
  }

  _otworzFormularz(g) {
    this._wybrany = null;
    this._formularz = g
      ? { id: g.id, alias: g.alias, jednostki: g.jednostki.slice(), komendy: (g.komendy && g.komendy.length ? g.komendy : [{ typ: 'wyl' }]).map((k) => ({ ...k })) }
      : { id: null, alias: '', jednostki: this._jednostkiZModulem(), komendy: [{ typ: 'wyl' }] };
    this._rysujFormularz();
    this._el.zaslona.classList.add('widoczna');
    this._el.szuflada.classList.add('widoczna');
  }

  _domyslnaWartosc(typ) {
    return typ === 'temp' ? 22 : typ === 'tryb' ? 'chlodzenie' : typ === 'bieg' ? 'auto' : undefined;
  }

  _rysujFormularz() {
    const f = this._formularz;
    const r = this.shadowRoot;
    const K = BiuroPanel.KOMENDY;
    r.querySelector('#szTytul').textContent = f.id ? 'Edycja automatyzacji' : 'Nowa automatyzacja';
    r.querySelector('#szPod').textContent = 'Komendy wykonują się po kolei dla każdej zaznaczonej jednostki. Zapis jako skrypt w Home Assistancie.';
    const tresc = r.querySelector('#szTresc');
    const jedn = Object.keys(SLOTY).map((slot) => {
      const ma = !!(this._jednostki[slot] && this._jednostki[slot].encje);
      const zazn = f.jednostki.includes(slot) && ma;
      return `<label class="${ma ? '' : 'brak-mod'}"><input type="checkbox" data-slot="${slot}" ${zazn ? 'checked' : ''} ${ma ? '' : 'disabled'}> ${this._nazwaSlotu(slot)}${ma ? '' : ' <small>(bez modułu)</small>'}</label>`;
    }).join('');
    const param = (k, n) => {
      if (k.typ === 'temp') return `<input type="number" class="fWartosc" data-n="${n}" min="16" max="30" step="1" value="${Number(k.wartosc) || 22}">`;
      if (k.typ === 'tryb') return `<select class="fWartosc" data-n="${n}">${['chlodzenie', 'grzanie', 'osuszanie', 'wentylacja', 'auto'].map((o) => `<option value="${o}" ${k.wartosc === o ? 'selected' : ''}>${o}</option>`).join('')}</select>`;
      if (k.typ === 'bieg') return `<select class="fWartosc" data-n="${n}">${['auto', 'niski', 'sredni', 'wysoki'].map((o) => `<option value="${o}" ${k.wartosc === o ? 'selected' : ''}>${o}</option>`).join('')}</select>`;
      return '';
    };
    const komendy = f.komendy.map((k, n) => `
      <div class="komenda-wiersz" data-n="${n}">
        <div class="komenda-gora"><span class="sekcja-tytul" style="margin:0">Komenda ${n + 1}</span>${f.komendy.length > 1 ? `<span class="g-akcja g-usun fUsunKomende" data-n="${n}" title="usuń komendę">✕</span>` : ''}</div>
        <div class="segmenty wiele fTypy" data-n="${n}">${Object.entries(K).map(([typ, kk]) => `<div class="segment ${k.typ === typ ? 'wybrany' : ''}" data-typ="${typ}">${kk.nazwa}</div>`).join('')}</div>
        <div class="pole fParam" data-n="${n}">${param(k, n)}</div>
      </div>`).join('');
    tresc.innerHTML = `
      <div class="pole"><div class="sekcja-tytul">Nazwa</div><input type="text" id="fNazwa" placeholder="np. Włącz wszystkie i ustaw 24 °C" value="${(f.alias || '').replace(/"/g, '&quot;')}"></div>
      <div><div class="sekcja-tytul">Jednostki</div><div class="wybor-jedn" id="fJedn">${jedn}</div></div>
      <div class="komendy" id="fKomendy">${komendy}</div>
      <div class="przycisk" id="fDodajKomende">+ kolejna komenda</div>
      <div class="blad-form" id="fBlad"></div>
      <div class="przyciski-form">
        <div class="przycisk" id="fAnuluj">Anuluj</div>
        <div class="przycisk glowny" id="fZapisz">${f.id ? 'Zapisz zmiany' : 'Zapisz'}</div>
      </div>`;
    tresc.querySelector('#fNazwa').addEventListener('input', (ev) => { f.alias = ev.target.value; });
    tresc.querySelectorAll('#fJedn input').forEach((c) => c.addEventListener('change', () => {
      f.jednostki = Array.from(tresc.querySelectorAll('#fJedn input:checked')).map((x) => x.dataset.slot);
    }));
    tresc.querySelectorAll('.fTypy .segment').forEach((sg) => sg.addEventListener('click', () => {
      const n = Number(sg.parentElement.dataset.n);
      f.komendy[n] = { typ: sg.dataset.typ, wartosc: this._domyslnaWartosc(sg.dataset.typ) };
      this._rysujFormularz();
    }));
    tresc.querySelectorAll('.fWartosc').forEach((w) => w.addEventListener('input', (ev) => { f.komendy[Number(w.dataset.n)].wartosc = ev.target.value; }));
    tresc.querySelectorAll('.fUsunKomende').forEach((b) => b.addEventListener('click', () => { f.komendy.splice(Number(b.dataset.n), 1); this._rysujFormularz(); }));
    tresc.querySelector('#fDodajKomende').addEventListener('click', () => { f.komendy.push({ typ: 'temp', wartosc: 24 }); this._rysujFormularz(); });
    tresc.querySelector('#fAnuluj').addEventListener('click', () => this._zamknij());
    tresc.querySelector('#fZapisz').addEventListener('click', () => this._zapiszFormularz());
  }

  async _zapiszFormularz() {
    const f = this._formularz;
    const blad = this.shadowRoot.querySelector('#fBlad');
    const alias = (f.alias || '').trim();
    if (!alias) { blad.textContent = 'Podaj nazwę.'; return; }
    if (!f.jednostki.length) { blad.textContent = 'Zaznacz co najmniej jedną jednostkę.'; return; }
    if (!f.komendy.length) { blad.textContent = 'Dodaj co najmniej jedną komendę.'; return; }
    for (const k of f.komendy) {
      if (k.typ === 'temp') { const v = Number(k.wartosc); if (!(v >= 16 && v <= 30)) { blad.textContent = 'Temperatura 16–30 °C.'; return; } k.wartosc = v; }
    }
    const sekwencja = this._budujSekwencje(f.jednostki, f.komendy);
    if (!sekwencja.length) { blad.textContent = 'Wybrane jednostki nie mają encji dla tych komend.'; return; }
    const id = f.id || ('klima_panel_' + alias.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ł/g, 'l').replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 30) + '_' + Date.now().toString(36).slice(-4));
    const cfg = {
      alias,
      description: JSON.stringify({ biuro_panel: 1, jednostki: f.jednostki, komendy: f.komendy }),
      icon: 'mdi:air-conditioner',
      mode: 'single',
      sequence: sekwencja,
    };
    try {
      blad.textContent = 'Zapisuję…';
      await this._hass.callApi('POST', `config/script/config/${id}`, cfg);
      this._zamknij();
      const istn = this._grupy ? this._grupy.filter((x) => x.id !== id) : [];
      this._grupy = istn.concat([{ id, entity: `script.${id}`, alias, jednostki: f.jednostki, komendy: f.komendy }]).sort((a, b) => a.id.localeCompare(b.id));
      this._rysujGrupy();
    } catch (e) {
      blad.textContent = `Nie udało się zapisać: ${e.message || e}`;
    }
  }

  _rysujSzuflade(slot) {
    const d = this._dane(slot);
    const r = this.shadowRoot;
    r.querySelector('#szTytul').textContent = d.nazwa;
    r.querySelector('#szPod').textContent = d.meta.typ === 'kaseton'
      ? 'Kaseton sufitowy · Gree GKH' : 'Jednostka ścienna';

    const tresc = r.querySelector('#szTresc');
    if (!d.podlaczona) {
      tresc.innerHTML = `<div class="info-brak">Ta jednostka nie ma jeszcze modułu sterującego.
        Po zamontowaniu pojawią się tu odczyty z magistrali i pełne sterowanie.</div>`;
      return;
    }

    const e = d.encje;
    const trybNaz = { chlodzenie: 'Chłodzenie', grzanie: 'Grzanie', osuszanie: 'Osuszanie', wentylacja: 'Wentylacja', auto: 'Auto' };
    const biegNaz = { auto: 'Auto', niski: 'Niski', sredni: 'Średni', wysoki: 'Wysoki' };

    tresc.innerHTML = `
      ${d.alarm ? `<div class="ostrzezenie"><span>⚠</span><span>Ostatnia komenda <b>nie została potwierdzona</b> przez magistralę. Sprawdź diodę nadawczą przy odbiorniku jednostki.</span></div>` : ''}

      <div>
        <div class="sekcja-tytul">Pomiar z magistrali</div>
        <div class="siatka">
          <div class="kafel"><div class="etyk">Pomieszczenie</div><div class="wart">${d.temperatura ?? '—'}<small>°C</small></div></div>
          <div class="kafel"><div class="etyk">Wymiennik</div><div class="wart">${d.wymiennik ?? '—'}<small>°C</small></div></div>
          <div class="kafel"><div class="etyk">Wentylator</div><div class="wart" style="font-size:.92rem">${biegNaz[d.bieg] || 'Stoi'}</div></div>
          <div class="kafel"><div class="etyk">Klapy</div><div class="wart" style="font-size:.92rem">${d.klapy === null ? '—' : (d.klapy ? 'Otwarte' : 'Zamknięte')}</div></div>
        </div>
      </div>

      <div>
        <div class="sekcja-tytul">Sterowanie</div>
        <div class="wiersz">
          <span class="etyk">Zasilanie</span>
          <div class="pstryczek ${d.wlaczona ? 'wl' : ''}" id="pstrykZasilanie"></div>
        </div>
        <div class="termostat" style="margin:10px 0 16px">
          <div class="krok ${d.nastawa !== null && d.nastawa <= 16 ? 'nieczynny' : ''}" id="minus">−</div>
          <div class="nastawa-duza">${d.nastawa ?? '—'}<small>°C</small></div>
          <div class="krok ${d.nastawa !== null && d.nastawa >= 30 ? 'nieczynny' : ''}" id="plus">+</div>
        </div>
        <div class="sekcja-tytul">Tryb</div>
        <div class="segmenty" style="margin-bottom:14px">
          ${['chlodzenie', 'grzanie', 'osuszanie', 'wentylacja', 'auto'].map((t) =>
            `<div class="segment ${d.tryb === t ? 'wybrany' : ''}" data-tryb="${t}">${trybNaz[t]}</div>`).join('')}
        </div>
        <div class="sekcja-tytul">Bieg wentylatora</div>
        <div class="segmenty">
          ${['auto', 'niski', 'sredni', 'wysoki'].map((b) =>
            `<div class="segment ${d.biegZadany === b ? 'wybrany' : ''}" data-bieg="${b}">${biegNaz[b]}</div>`).join('')}
        </div>
      </div>

      <div>
        <div class="sekcja-tytul">Stan modułu</div>
        <div class="wiersz"><span class="etyk">Łączność z sondą</span><span style="font-size:.83rem;opacity:.7">${d.online ? 'w porządku' : 'brak'}</span></div>
        <div class="wiersz"><span class="etyk">Potwierdzenie komendy</span><span style="font-size:.83rem;opacity:.7">${
          { tak: 'potwierdzona', nie: 'BRAK POTWIERDZENIA', w_toku: 'sprawdzanie…', brak: 'brak komendy' }[d.potwierdzenie] || '—'}</span></div>
      </div>`;

    const wolaj = (dom, usl, dane) => this._hass.callService(dom, usl, dane);
    const pstryk = tresc.querySelector('#pstrykZasilanie');
    if (pstryk && e.wlacznik) {
      pstryk.addEventListener('click', () =>
        wolaj('switch', d.wlaczona ? 'turn_off' : 'turn_on', { entity_id: e.wlacznik }));
    }
    const zmienNastawe = (delta) => {
      if (d.nastawa === null || !e.nastawa) return;
      const v = Math.min(30, Math.max(16, d.nastawa + delta));
      wolaj('number', 'set_value', { entity_id: e.nastawa, value: v });
    };
    tresc.querySelector('#minus').addEventListener('click', () => zmienNastawe(-1));
    tresc.querySelector('#plus').addEventListener('click', () => zmienNastawe(1));
    tresc.querySelectorAll('[data-tryb]').forEach((s) => s.addEventListener('click', () =>
      e.tryb && wolaj('select', 'select_option', { entity_id: e.tryb, option: s.dataset.tryb })));
    tresc.querySelectorAll('[data-bieg]').forEach((s) => s.addEventListener('click', () =>
      e.bieg_zadany && wolaj('select', 'select_option', { entity_id: e.bieg_zadany, option: s.dataset.bieg })));
  }
}

// Podwojne zaladowanie modulu (np. resources + extra_module_url) rzucaloby wyjatkiem.
if (!customElements.get('biuro-panel')) customElements.define('biuro-panel', BiuroPanel);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'biuro-panel',
  name: 'Panel biura — klimatyzacja',
  description: 'Rzut biura z jednostkami klimatyzacji, sterowaniem i listą automatyzacji.',
});

export { BiuroPanel, SLOTY, PLAN };
