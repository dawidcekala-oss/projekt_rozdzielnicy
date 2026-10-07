// Q11 DevKit test: skrypt uslugi Shelly X (low-code). AMPERE POINT, 2026-09-24, v3.
// Wkleic w portalu: Develop -> Open editor -> script.svc.ts, zastepujac cala zawartosc.
//
// Czesc 1 to kod wygenerowany przez portal z zakladki Data, z dwiema poprawkami:
//   - DP 3 przychodzi jako numer pozycji (TMCU.DT_ENUM = indeks), a pole "mode"
//     przyjmuje nazwy, wiec numer tlumaczy tablica MODES (kolejnosc jak w portalu i w Q11),
//   - wartosc od mikrokontrolera nie wraca do niego z powrotem jako polecenie (bez echa).
// Czesc 2 wypelnia pozostale pola ekranu ladowarki:
//   phase_info       z DP 6, 7, 8 (po 7 bajtow na faze) i DP 1 (licznik)
//   session_energy   przyrost licznika DP 1 od wpiecia auta, kWh
//                    (tak samo liczy integracja HA tuyaextend_amperepoint)
//   session_duration minuty w stanie "charger_charging"
//
// Faza Q11, 7 bajtow, od najstarszego:
//   [0..1] napiecie x0,1 V   [2..4] prad x0,001 A   [5..6] moc w W
//   przyklad 08 FC 00 3E 80 0E 60 -> 230,0 V, 16,000 A, 3680 W
// DP 1: licznik calkowity w setnych kWh, 123456 -> 1234,56 kWh.

declare const Timer: any;   // zegar Shelly: Timer.set(ms, powtarzaj, funkcja)

const tmcu = TMCU.get();

const stateHandle = Service.getVCHandle('state');
const currentLimitHandle = Service.getVCHandle('current_limit');
const modeHandle = Service.getVCHandle('mode');
const phaseInfoHandle = Service.getVCHandle('phase_info');
const sessionEnergyHandle = Service.getVCHandle('session_energy');
const sessionDurationHandle = Service.getVCHandle('session_duration');

const MODES = [
  'charger_free',        // 0 wolna
  'charger_insert',      // 1 auto podlaczone
  'charger_free_fault',  // 2 wolna, blad
  'charger_wait',        // 3 czeka na harmonogram
  'charger_charging',    // 4 laduje
  'charger_pause',       // 5 pauza
  'charger_end',         // 6 zakonczone
  'charger_fault',       // 7 blad
];

function setIfChanged(h: any, v: any): void {
  if (v === null || v === undefined) return;
  if (v !== h.getValue()) h.setValue(v);
}

// =====================================================================
// Czesc 1: stan, limit pradu, ladowanie wlaczone
// =====================================================================

// mode <- DP 3 (tylko odczyt)
function toMode(raw: any): string | null {
  if (typeof raw === 'number') return raw >= 0 && raw < MODES.length ? MODES[raw] : null;
  if (typeof raw === 'string' && MODES.indexOf(raw) >= 0) return raw;
  return null;
}

function syncMode(raw: any): void {
  const m = toMode(raw);
  if (m === null) return;
  setIfChanged(modeHandle, m);
  onState(m);
}

// current_limit <-> DP 4
let lastLimitFromDevice: any = null;
const dpCurrentLimit = tmcu.getDatapoint(4);
if (dpCurrentLimit) {
  const syncCurrentLimit = (raw: any) => {
    if (typeof raw !== 'number') return;
    lastLimitFromDevice = raw;
    setIfChanged(currentLimitHandle, raw);
  };
  syncCurrentLimit(dpCurrentLimit.v);
  dpCurrentLimit.on('change', (res: any) => syncCurrentLimit(res.v));
}
currentLimitHandle.on('change', ({ value }: any) => {
  const amps = Math.round(value);
  if (amps === lastLimitFromDevice) return;   // to przyszlo z Q11, nie odsylamy
  lastLimitFromDevice = amps;
  tmcu.writeDatapoint(4, TMCU.DT_INT, amps);
});

// state <-> DP 18
let lastStateFromDevice: any = null;
const dpState = tmcu.getDatapoint(18);
if (dpState) {
  const syncState = (raw: any) => {
    if (typeof raw !== 'boolean') return;
    lastStateFromDevice = raw;
    setIfChanged(stateHandle, raw);
  };
  syncState(dpState.v);
  dpState.on('change', (res: any) => syncState(res.v));
}
stateHandle.on('change', ({ value }: any) => {
  if (value === lastStateFromDevice) return;  // to przyszlo z Q11, nie odsylamy
  lastStateFromDevice = value;
  tmcu.writeDatapoint(18, TMCU.DT_BOOL, value);
});

// =====================================================================
// Czesc 2: fazy, energia i czas sesji
// =====================================================================

const DP_TOTAL = 1;
const DP_PHASES = [6, 7, 8];
const PHASE_KEYS = ['phase_a', 'phase_b', 'phase_c'];
const TICK_MS = 30000;

type Phase = { voltage: number; current: number; power: number };

const phases: (Phase | null)[] = [null, null, null];
let totalKwh: number | null = null;
let baselineKwh: number | null = null;
let connected = false;
let chargingSince: number | null = null;
let chargedMs = 0;

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

// Dokumentacja nie mowi, w jakiej postaci skrypt dostaje DT_RAW,
// wiec przyjmujemy kazda rozsadna: tablice bajtow, tekst hex, base64 albo surowy tekst.
function toBytes(v: any): number[] | null {
  if (v === null || v === undefined) return null;
  if (typeof v === 'object' && typeof v.length === 'number') {
    const a: number[] = [];
    for (let i = 0; i < v.length; i++) a.push(v[i] & 255);
    return a;
  }
  if (typeof v !== 'string') return null;
  if (v.length === 14) {
    const h = fromHex(v);
    if (h) return h;
  }
  if (v.length === 7) {
    const a: number[] = [];
    for (let i = 0; i < 7; i++) a.push(v.charCodeAt(i) & 255);
    return a;
  }
  return fromBase64(v);
}

function round(x: number, d: number): number {
  const p = Math.pow(10, d);
  return Math.round(x * p) / p;
}

function decodePhase(raw: any): Phase | null {
  const b = toBytes(raw);
  if (!b || b.length !== 7) return null;
  return {
    voltage: round((b[0] * 256 + b[1]) / 10, 1),
    current: round((b[2] * 65536 + b[3] * 256 + b[4]) / 1000, 3),
    power: b[5] * 256 + b[6],
  };
}

function publishPhases(): void {
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
  value.total_power = power;
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
  let ms = chargedMs;
  if (chargingSince !== null) ms += Date.now() - chargingSince;
  setIfChanged(sessionDurationHandle, Math.floor(ms / 60000));
}

// Sesja: wpiecie auta zaczyna nowa, odpiecie zostawia wynik ostatniej.
function onState(state: string): void {
  const nowConnected = state !== 'charger_free' && state !== 'charger_free_fault';
  if (nowConnected && !connected) {
    baselineKwh = totalKwh;      // gdy licznik jeszcze nie przyszedl, ustawi go onTotal
    chargedMs = 0;
    chargingSince = null;
    setIfChanged(sessionEnergyHandle, 0);
    setIfChanged(sessionDurationHandle, 0);
  }
  connected = nowConnected;

  const now = Date.now();
  if (state === 'charger_charging') {
    if (chargingSince === null) chargingSince = now;
  } else if (chargingSince !== null) {
    chargedMs += now - chargingSince;
    chargingSince = null;
  }
  publishDuration();
}

function onTotal(raw: any): void {
  if (typeof raw !== 'number') return;
  totalKwh = round(raw / 100, 2);
  if (connected && baselineKwh === null) baselineKwh = totalKwh;
  publishEnergy();
  publishPhases();
}

const dpTotal = tmcu.getDatapoint(DP_TOTAL);
if (dpTotal) {
  onTotal(dpTotal.v);
  dpTotal.on('change', (res: any) => onTotal(res.v));
}

for (let i = 0; i < 3; i++) {
  const idx = i;
  const dp = tmcu.getDatapoint(DP_PHASES[idx]);
  if (dp) {
    phases[idx] = decodePhase(dp.v);
    dp.on('change', (res: any) => {
      phases[idx] = decodePhase(res.v);
      publishPhases();
    });
  }
}

// Stan na koncu, gdy licznik i fazy juz sa podpiete.
const dpMode = tmcu.getDatapoint(3);
if (dpMode) {
  syncMode(dpMode.v);
  dpMode.on('change', (res: any) => syncMode(res.v));
}

publishPhases();

// Zegar: oprogramowanie modulu (Espruino) nie ma setInterval, choc dokumentacja
// uzywa go w przykladach. Wdrozenie v2 zatrzymalo sie na: ReferenceError "setInterval" is not defined.
if (typeof Timer !== 'undefined') {
  Timer.set(TICK_MS, true, publishDuration);
} else {
  setInterval(publishDuration, TICK_MS);
}
