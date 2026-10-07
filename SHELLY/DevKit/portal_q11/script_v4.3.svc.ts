// Q11 DevKit test: skrypt uslugi Shelly X (low-code). AMPERE POINT, 2026-09-29, v4.3.
// Wkleic w portalu: Develop -> Open editor -> script.svc.ts, zastepujac cala zawartosc.
// Lista pol i punktow danych do portalu: pola_produktu_v4.pdf w tym folderze.
//
// Zmiany wzgledem v3 (kopia: script_v3.svc.ts):
//   - nowe pola: cp_state (DP 13), work_mode (DP 14, zapis), energy_limit (DP 17, zapis),
//     window_start i window_end (DP 19, zapis), temperature (DP 24),
//     last_session_energy (DP 25), faults (DP 10), controller_version (DP 23),
//   - moc calkowita z DP 9, gdy sterownik ja podaje; inaczej suma mocy faz,
//   - czas sesji liczony z tykniec zegara skryptu, nie z godziny modulu
//     (v3 liczyl z Date.now(), wiec skakal przy kazdej zmianie godziny),
//   - punkt, ktorego modul jeszcze nie zna (sterownik go nie zglosil), jest
//     podpinany pozniej: skrypt probuje co 5 s,
//   - po kazdym zapisie skrypt po 3 s sprawdza, czy sterownik przyjal wartosc;
//     jesli nie, pokazuje w polu wartosc sterownika,
//   - pole, ktorego nie ma w produkcie, jest pomijane, wiec skrypt dziala tez
//     na starej konfiguracji z szescioma polami.
// v4.1 (po probie na module 29.09):
//   - zapis punktu raw jako 2 bajty (String.fromCharCode). TMCU wysyla tekst doslownie:
//     "1600" poszlo jako 4 bajty 31 36 30 30 i sterownik je zignorowal,
//   - po zapisie okna skrypt prosi sterownik o wszystkie punkty (queryDatapoints),
//     bo inaczej nie wie, czy sterownik przyjal,
//   - komunikaty o problemach trafiaja do Service.GetStatus (errors); console.log
//     skryptu nie trafia do logu modulu.
// v4.2 (po probie na module 29.09, 10:41):
//   - bez kontroli po zapisie. Po wlasnym zapisie modul nie odswieza wartosci widocznej
//     dla skryptu: sterownik potwierdzil tryb "natychmiast", modul uznal to za "bez zmian",
//     a skrypt przeczytal stara wartosc i cofnal pole na "harmonogram". Pole pokazuje
//     to, co ustawiono; kazda zmiana zgloszona przez sterownik i tak trafia do pola.
// v4.3 (po sterowaniu z Home Assistant 29.09, 12:01-12:04):
//   - do sterownika ida tylko zmiany pola z zewnatrz (HA, strona, aplikacja). Zmiana,
//     ktora robi sam skrypt, ma zrodlo "sys" i jest pomijana. W v4.2 spozniony meldunek
//     sterownika ze stara wartoscia wracal do niego jako polecenie: limit energii 3 -> 2,
//   - zmiany pola czekaja 1 s na koniec serii i idzie tylko ostatnia: pole liczbowe w HA
//     wysylalo polecenie na kazde klikniecie strzalki (24 w 9 s), a sterownik zasypany
//     zapisami limitu energii przestawal odpowiadac modulowi,
//   - znane odrzucenia sterownika nie ida na lacze, pole wraca do poprzedniej wartosci:
//     tryb "do limitu energii" przy limicie 0, okno z rowna godzina startu i konca,
//   - wartosc wyslana do sterownika wraca do pola w postaci, w jakiej poszla
//     (okno 0,01 h -> 0, limit 6,5 A -> 7 A).
//
// Sprzezenia w sterowniku (29.09): limit energii > 0 przelacza tryb na "do limitu energii",
// okno godzin na "harmonogram", tryb "natychmiast" zeruje limit energii.
//
// Postac wartosci z modulu (z logu TMCU): int i enum jako liczba, bool jako true/false,
// bitmap jako liczba, raw jako tekst szesnastkowy, np. "0000". Dokumentacja Shelly nie
// opisuje raw, bitmap ani tekstu, wiec dekodery przyjmuja kazda rozsadna postac.
//
// Faza Q11, 7 bajtow, od najstarszego:
//   [0..1] napiecie x0,1 V   [2..4] prad x0,001 A   [5..6] moc w W
//   przyklad 08 FC 00 3E 80 0E 60 -> 230,0 V, 16,000 A, 3680 W
// DP 1: licznik calkowity w setnych kWh; sterownik wysyla go co 90 s, tylko w stanie "laduje".

declare const Timer: any;   // zegar Shelly: Timer.set(ms, powtarzaj, funkcja)

const tmcu = TMCU.get();

// =====================================================================
// Narzedzia
// =====================================================================

function vc(role: string): any {
  try {
    const h = Service.getVCHandle(role);
    return h ? h : null;
  } catch (e) {
    return null;
  }
}

function setIfChanged(h: any, v: any): void {
  if (!h || v === null || v === undefined) return;
  if (v !== h.getValue()) h.setValue(v);
}

function every(ms: number, fn: () => void): void {
  if (typeof Timer !== 'undefined') Timer.set(ms, true, fn);
  else setInterval(fn, ms);
}

function after(ms: number, fn: () => void): void {
  if (typeof Timer !== 'undefined') {
    Timer.set(ms, false, fn);
  } else {
    const id = setInterval(() => {
      clearInterval(id);
      fn();
    }, ms);
  }
}

function round(x: number, d: number): number {
  const p = Math.pow(10, d);
  return Math.round(x * p) / p;
}

// Ostatnie komunikaty o problemach: widac je w Service.GetStatus (pole errors).
const lastLogs: string[] = [];

function log(msg: string): void {
  lastLogs.push(msg);
  if (lastLogs.length > 5) lastLogs.shift();
  try {
    Service.setErrors(lastLogs.slice());
  } catch (e) {
    // brak setErrors: pomijamy
  }
  try {
    console.log('Q11: ' + msg);
  } catch (e) {
    // brak konsoli: pomijamy
  }
}

const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const HEX = '0123456789abcdef';

function fromBase64(s: string): number[] | null {
  const out: number[] = [];
  let acc = 0;
  let bits = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s.charAt(i);
    if (c === '=') break;
    const idx = B64.indexOf(c);
    if (idx < 0) return null;
    acc = ((acc << 6) | idx) & 0xffffff;
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      out.push((acc >> bits) & 255);
    }
  }
  return out;
}

function fromHex(s: string): number[] | null {
  if (s.length % 2 !== 0) return null;
  const t = s.toLowerCase();
  const out: number[] = [];
  for (let i = 0; i + 1 < t.length; i += 2) {
    const hi = HEX.indexOf(t.charAt(i));
    const lo = HEX.indexOf(t.charAt(i + 1));
    if (hi < 0 || lo < 0) return null;
    out.push(hi * 16 + lo);
  }
  return out;
}

// Bajty z wartosci raw: tablica, tekst szesnastkowy, surowe znaki albo base64.
// n = oczekiwana liczba bajtow.
function toBytes(v: any, n: number): number[] | null {
  if (v === null || v === undefined) return null;
  if (typeof v === 'object' && typeof v.length === 'number') {
    const a: number[] = [];
    for (let i = 0; i < v.length; i++) a.push(v[i] & 255);
    return a;
  }
  if (typeof v !== 'string') return null;
  if (v.length === 2 * n) {
    const h = fromHex(v);
    if (h) return h;
  }
  if (v.length === n) {
    const a: number[] = [];
    for (let i = 0; i < n; i++) a.push(v.charCodeAt(i) & 255);
    return a;
  }
  return fromBase64(v);
}

// Liczba z wartosci bitmap: liczba, tekst szesnastkowy albo tablica bajtow (starszy pierwszy).
function toBits(v: any): number | null {
  if (typeof v === 'number') return v;
  if (typeof v === 'boolean') return v ? 1 : 0;
  let b: number[] | null = null;
  if (typeof v === 'string') b = fromHex(v);
  else if (v && typeof v === 'object' && typeof v.length === 'number') b = toBytes(v, v.length);
  if (!b) return null;
  let n = 0;
  for (let i = 0; i < b.length; i++) n = n * 256 + b[i];
  return n;
}

// =====================================================================
// Podpinanie punktow danych
// =====================================================================
// Punkt, ktorego modul jeszcze nie zna, podpinamy pozniej: modul dodaje go dopiero
// wtedy, gdy sterownik go zglosi (w logu TMCU: "add int 24 = 19").

type Binding = { id: number; fn: (v: any) => void; onDp: ((dp: any) => void) | null };
const pending: Binding[] = [];

function tryBind(b: Binding): boolean {
  const dp = tmcu.getDatapoint(b.id);
  if (!dp) return false;
  if (b.onDp) b.onDp(dp);
  if (dp.v !== null && dp.v !== undefined) b.fn(dp.v);
  dp.on('change', (res: any) => b.fn(res.v));
  return true;
}

function bindDp(id: number, fn: (v: any) => void, onDp?: (dp: any) => void): void {
  const b: Binding = { id: id, fn: fn, onDp: onDp ? onDp : null };
  if (!tryBind(b)) pending.push(b);
}

every(5000, () => {
  for (let i = pending.length - 1; i >= 0; i--) {
    if (tryBind(pending[i])) pending.splice(i, 1);
  }
});

// Pole tylko do odczytu.
function linkReadOnly(role: string, id: number, toField: (raw: any) => any): void {
  const h = vc(role);
  if (!h) return;
  bindDp(id, (raw: any) => setIfChanged(h, toField(raw)));
}

// Zmiany pola czekaja tyle na koniec serii; do sterownika idzie tylko ostatnia.
const SETTLE_MS = 1000;

// Zmiana pola zrobiona przez sam skrypt (wpisanie meldunku sterownika) ma zrodlo "sys".
function fromOutside(ev: any): boolean {
  return !(ev && ev.source === 'sys');
}

// Pole zapisywalne. toField: punkt -> pole, toDp: pole -> punkt (null = nie zapisywac),
// check: powod, dla ktorego sterownik odrzuci wartosc (null = wysylac).
function linkWritable(role: string, id: number, dpType: any,
                      toField: (raw: any) => any, toDp: (v: any) => any,
                      check?: (v: any) => string | null): void {
  const h = vc(role);
  if (!h) return;
  let last: any = undefined;     // ostatnia wartosc zgloszona przez sterownik albo wyslana
  let wanted: any = undefined;   // ostatnia wartosc ustawiona z zewnatrz
  let gen = 0;                   // numer zmiany; po odczekaniu wysylamy tylko najnowsza

  bindDp(id, (raw: any) => {
    const v = toField(raw);
    if (v === null || v === undefined) return;
    last = v;
    setIfChanged(h, v);
  });

  function refuse(why: string): void {
    log(role + ': ' + why + ', nie wysylam');
    if (last !== undefined) setIfChanged(h, last);
  }

  function send(): void {
    const v = wanted;
    wanted = undefined;
    const out = toDp(v);
    if (out === null || out === undefined) {
      refuse('wartosc ' + v + ' poza zakresem sterownika');
      return;
    }
    const shown = toField(out);
    const why = check ? check(shown) : null;
    if (why) {
      refuse(why);
      return;
    }
    last = shown;
    setIfChanged(h, shown);
    try {
      tmcu.writeDatapoint(id, dpType, out);
    } catch (e) {
      log(role + ': zapis DP ' + id + ' odrzucony: ' + e);
    }
  }

  h.on('change', (ev: any) => {
    if (!fromOutside(ev)) return;
    wanted = ev.value;
    const my = ++gen;
    after(SETTLE_MS, () => {
      if (my === gen) send();
    });
  });
}

// =====================================================================
// Czesc 1: pola sterowania i stanu
// =====================================================================

const MODES = [
  'charger_free',        // 0 wolna
  'charger_insert',      // 1 auto podlaczone
  'charger_free_fault',  // 2 wolna, blad
  'charger_wait',        // 3 czeka
  'charger_charging',    // 4 laduje
  'charger_pause',       // 5 pauza
  'charger_end',         // 6 zakonczone
  'charger_fault',       // 7 blad
];

const CP_STATES = [
  'controlpi_12v',       // 0 12 V, brak auta
  'controlpi_12v_pwm',   // 1 12 V z sygnalem pradu
  'controlpi_9v',        // 2 9 V, auto podlaczone
  'controlpi_9v_pwm',    // 3 9 V z sygnalem pradu
  'controlpi_6v',        // 4 6 V, auto chce ladowac
  'controlpi_6v_pwm',    // 5 6 V z sygnalem pradu, ladowanie
  'controlpi_error',     // 6 blad sygnalu
];

const WORK_MODES = [
  'charge_now',          // 0 natychmiast
  'charge_energy',       // 1 do limitu energii
  'charge_schedule',     // 2 w oknie godzin
];

const FAULTS = [
  'ov_cr', 'ov2_cr_fault', 'ov_vol', 'undervoltage_alarm', 'contactor_adhesion',
  'contactor_fault', 'earth_fault', 'meter_hardware_alarm', 'scram_fault', 'cp_fault',
  'meter_commu_fault', 'card_reader_fault', 'cir_short_fault', 'adhesion_fault',
  'self_test_alarm', 'leakagecurr_alarm', 'ov_Temp_fault',
];

// Wyliczenie: po lacze idzie numer pozycji, pole przyjmuje nazwe.
function enumName(names: string[], raw: any): string | null {
  if (typeof raw === 'number') return raw >= 0 && raw < names.length ? names[raw] : null;
  if (typeof raw === 'string' && names.indexOf(raw) >= 0) return raw;
  return null;
}

function toBool(raw: any): boolean | null {
  if (typeof raw === 'boolean') return raw;
  if (raw === 1) return true;
  if (raw === 0) return false;
  return null;
}

function toInt(raw: any): number | null {
  return typeof raw === 'number' ? raw : null;
}

// Wlaczenie ladowania <-> DP 18
linkWritable('state', 18, TMCU.DT_BOOL, toBool, (v: any) => (v ? true : false));

// Limit pradu <-> DP 4 (sterownik przyjmuje 6-16 A)
linkWritable('current_limit', 4, TMCU.DT_INT, toInt, (v: any) => {
  const a = Math.round(v);
  return a >= 6 && a <= 16 ? a : null;
});

// Tryb pracy <-> DP 14. "Do limitu energii" przy limicie 0 sterownik odrzuca (29.09 12:02:44).
linkWritable('work_mode', 14, TMCU.DT_ENUM,
  (raw: any) => enumName(WORK_MODES, raw),
  (v: any) => {
    const i = WORK_MODES.indexOf(v);
    return i >= 0 ? i : null;
  },
  (v: any) => {
    if (v !== 'charge_energy') return null;
    const e = vc('energy_limit');
    const k = e ? e.getValue() : null;
    if (typeof k === 'number' && k > 0) return null;
    return 'tryb "do limitu energii" wymaga limitu wiekszego od 0; ustaw limit, sterownik sam przejdzie w ten tryb';
  });

// Limit energii sesji <-> DP 17 (1-200 kWh; 0 w polu = sterownik jeszcze nie zglosil)
linkWritable('energy_limit', 17, TMCU.DT_INT,
  (raw: any) => (typeof raw === 'number' && raw >= 0 && raw <= 200 ? raw : null),
  (v: any) => {
    const k = Math.round(v);
    return k >= 1 && k <= 200 ? k : null;
  });

// Okno godzin <-> DP 19: 2 bajty, godzina startu i godzina konca (0-23), bez minut.
// Dwa pola, jeden punkt: zmiana ktoregokolwiek pola wysyla oba.
(function linkWindow(): void {
  const hStart = vc('window_start');
  const hEnd = vc('window_end');
  if (!hStart || !hEnd) return;
  let lastStart: any = undefined;   // ostatnie okno zgloszone przez sterownik albo wyslane
  let lastEnd: any = undefined;
  let wantStart: any = undefined;   // ustawione z zewnatrz, czeka na koniec serii
  let wantEnd: any = undefined;
  let gen = 0;
  let applying = false;   // true, gdy skrypt sam wpisuje okno ze sterownika do pol

  function decode(raw: any): number[] | null {
    const b = toBytes(raw, 2);
    if (!b || b.length !== 2 || b[0] > 23 || b[1] > 23) return null;
    return b;
  }

  // Pola ustawiamy po kolei; bez blokady zmiana pierwszego wyslalaby do sterownika
  // okno zlozone z nowego startu i starego konca.
  function show(w: number[]): void {
    lastStart = w[0];
    lastEnd = w[1];
    applying = true;
    setIfChanged(hStart, w[0]);
    setIfChanged(hEnd, w[1]);
    applying = false;
  }

  bindDp(19, (raw: any) => {
    const w = decode(raw);
    if (w) show(w);
  });

  function pick(want: any, known: any, h: any): number {
    if (want !== undefined) return Math.round(want);
    if (known !== undefined) return known;
    return Math.round(h.getValue());
  }

  function back(): void {
    if (lastStart !== undefined && lastEnd !== undefined) show([lastStart, lastEnd]);
  }

  function send(): void {
    const s = pick(wantStart, lastStart, hStart);
    const e = pick(wantEnd, lastEnd, hEnd);
    wantStart = undefined;
    wantEnd = undefined;
    if (!(s >= 0 && s <= 23 && e >= 0 && e <= 23)) {   // takze NaN
      log('okno godzin: ' + s + '-' + e + ' poza zakresem 0-23, nie wysylam');
      back();
      return;
    }
    if (s === e) {
      log('okno godzin: start i koniec ' + s + ' sa rowne, sterownik takiego okna nie przyjmuje');
      back();
      return;
    }
    // Ponowny zapis tego samego okna przelaczylby sterownik w tryb "harmonogram".
    const same = s === lastStart && e === lastEnd;
    show([s, e]);   // pola w pelnych godzinach (np. 0,01 -> 0)
    if (same) return;
    try {
      // 2 bajty: godzina startu i konca. Tekst szesnastkowy poszedlby jako 4 znaki ASCII.
      // Uwaga: sterownik po otrzymaniu okna sam przechodzi w tryb "harmonogram".
      tmcu.writeDatapoint(19, TMCU.DT_RAW, String.fromCharCode(s) + String.fromCharCode(e));
    } catch (err) {
      log('okno godzin: zapis DP 19 odrzucony: ' + err);
    }
  }

  function later(): void {
    const my = ++gen;
    after(SETTLE_MS, () => {
      if (my === gen) send();
    });
  }

  hStart.on('change', (ev: any) => {
    if (applying || !fromOutside(ev)) return;
    wantStart = ev.value;
    later();
  });
  hEnd.on('change', (ev: any) => {
    if (applying || !fromOutside(ev)) return;
    wantEnd = ev.value;
    later();
  });
})();

// Sygnal z auta <- DP 13 (tylko odczyt)
linkReadOnly('cp_state', 13, (raw: any) => enumName(CP_STATES, raw));

// Temperatura <- DP 24, stopnie C
linkReadOnly('temperature', 24, (raw: any) =>
  (typeof raw === 'number' && raw >= -40 && raw <= 200 ? raw : null));

// Energia ostatniej sesji <- DP 25, setne kWh
linkReadOnly('last_session_energy', 25, (raw: any) =>
  (typeof raw === 'number' && raw >= 0 ? round(raw / 100, 2) : null));

// Bledy <- DP 10: mapa bitowa, bit 0 = pierwszy kod z definicji Tuya.
// Pole text: lista kodow; pole number (gdy portal nie ma typu text): sama wartosc.
const faultsIsNumber = (() => {
  const h = vc('faults');
  return h ? typeof h.getValue() === 'number' : false;
})();
linkReadOnly('faults', 10, (raw: any) => {
  const n = toBits(raw);
  if (n === null) return null;
  if (faultsIsNumber) return n;
  if (n === 0) return 'none';
  const out: string[] = [];
  for (let i = 0; i < 24; i++) {
    if ((n >> i) & 1) out.push(i < FAULTS.length ? FAULTS[i] : 'bit' + i);
  }
  return out.join(', ') + ' (0x' + n.toString(16) + ')';
});

// Wersja sterownika <- DP 23: tekst; jesli przyjdzie szesnastkowo, zamieniamy na znaki
linkReadOnly('controller_version', 23, (raw: any) => {
  if (typeof raw !== 'string') return raw === null || raw === undefined ? null : '' + raw;
  const b = fromHex(raw);
  if (!b || b.length === 0) return raw;
  let s = '';
  for (let i = 0; i < b.length; i++) {
    if (b[i] < 32 || b[i] > 126) return raw;
    s += String.fromCharCode(b[i]);
  }
  return s;
});

// =====================================================================
// Czesc 2: fazy, moc, energia i czas sesji
// =====================================================================

const modeHandle = vc('mode');
const phaseInfoHandle = vc('phase_info');
const sessionEnergyHandle = vc('session_energy');
const sessionDurationHandle = vc('session_duration');

const DP_PHASES = [6, 7, 8];
const PHASE_KEYS = ['phase_a', 'phase_b', 'phase_c'];
const TICK_S = 10;

type Phase = { voltage: number; current: number; power: number };

const phases: (Phase | null)[] = [null, null, null];
let totalKwh: number | null = null;
let totalPowerW: number | null = null;   // z DP 9, gdy sterownik go podaje
let baselineKwh: number | null = null;
let connected = false;
let charging = false;
let chargedS = 0;

function decodePhase(raw: any): Phase | null {
  const b = toBytes(raw, 7);
  if (!b || b.length !== 7) return null;
  return {
    voltage: round((b[0] * 256 + b[1]) / 10, 1),
    current: round((b[2] * 65536 + b[3] * 256 + b[4]) / 1000, 3),
    power: b[5] * 256 + b[6],
  };
}

function publishPhases(): void {
  if (!phaseInfoHandle) return;
  let current = 0;
  let power = 0;
  const value: any = {};
  for (let i = 0; i < 3; i++) {
    const p = phases[i] || { voltage: 0, current: 0, power: 0 };
    value[PHASE_KEYS[i]] = p;
    current += p.current;
    power += p.power;
  }
  value.total_current = round(current, 3);
  value.total_power = totalPowerW !== null ? totalPowerW : power;
  value.total_act_energy = totalKwh === null ? 0 : totalKwh;
  value.counter = {
    total: totalKwh === null ? 0 : round(totalKwh * 1000, 0),
    minute_ts: Math.floor(Date.now() / 60000) * 60,
    by_minute: [0, 0, 0],
  };
  phaseInfoHandle.setValue(value);
}

function publishEnergy(): void {
  if (totalKwh === null || baselineKwh === null) return;
  setIfChanged(sessionEnergyHandle, round(Math.max(0, totalKwh - baselineKwh), 2));
}

function publishDuration(): void {
  setIfChanged(sessionDurationHandle, Math.floor(chargedS / 60));
}

// Sesja: wpiecie auta zaczyna nowa, odpiecie zostawia wynik ostatniej.
function onState(state: string): void {
  const nowConnected = state !== 'charger_free' && state !== 'charger_free_fault';
  if (nowConnected && !connected) {
    baselineKwh = totalKwh;      // gdy licznik jeszcze nie przyszedl, ustawi go onTotal
    chargedS = 0;
    setIfChanged(sessionEnergyHandle, 0);
    setIfChanged(sessionDurationHandle, 0);
  }
  connected = nowConnected;
  charging = state === 'charger_charging';
  publishDuration();
}

function onTotal(raw: any): void {
  if (typeof raw !== 'number') return;
  totalKwh = round(raw / 100, 2);
  if (connected && baselineKwh === null) baselineKwh = totalKwh;
  publishEnergy();
  publishPhases();
}

bindDp(1, onTotal);

bindDp(9, (raw: any) => {
  if (typeof raw !== 'number' || raw < 0) return;
  totalPowerW = raw;             // tysieczne kW, czyli W
  publishPhases();
});

for (let i = 0; i < 3; i++) {
  const idx = i;
  bindDp(DP_PHASES[idx], (raw: any) => {
    phases[idx] = decodePhase(raw);
    publishPhases();
  });
}

// Stan na koncu, gdy licznik i fazy sa juz podpiete.
bindDp(3, (raw: any) => {
  const m = enumName(MODES, raw);
  if (!m) return;
  setIfChanged(modeHandle, m);
  onState(m);
});

publishPhases();

// Czas sesji: zliczamy tykniecia zegara skryptu, niezalezne od godziny modulu.
every(TICK_S * 1000, () => {
  if (charging) chargedS += TICK_S;
  publishDuration();
});
