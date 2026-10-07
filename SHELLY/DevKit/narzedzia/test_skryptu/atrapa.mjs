// Atrapa modułu Shelly X do sprawdzenia skryptu v4 bez sprzętu.
// Zegar, warstwa TMCU (punkty danych) i pola usługi są podstawione.
import { readFileSync, writeFileSync } from 'node:fs';

let now = 0;                       // ms, zegar atrapy
const timers = [];
globalThis.Timer = {
  set(ms, repeat, fn) { timers.push({ due: now + ms, ms, repeat, fn }); return timers.length; },
};
function advance(ms) {             // przesuwa zegar i odpala timery po kolei
  const end = now + ms;
  for (;;) {
    let next = null;
    for (const t of timers) if (!t.done && t.due <= end && (!next || t.due < next.due)) next = t;
    if (!next) break;
    now = next.due;
    if (next.repeat) next.due += next.ms; else next.done = true;
    next.fn();
  }
  now = end;
}

const logs = [];
const realInfo = console.log.bind(console);
globalThis.console = { log: (m) => logs.push(m), info: realInfo };

// --- TMCU: punkt znany od startu (zadeklarowany) albo dodawany przy pierwszym meldunku
const DECLARED = [18, 4, 3, 1, 6, 7, 8];
const dps = {};
const writes = [];
let queries = 0;
function mkDp(id) { return { id, v: undefined, ls: [], on(ev, cb) { this.ls.push(cb); } }; }
for (const id of DECLARED) dps[id] = mkDp(id);
globalThis.TMCU = {
  DT_BOOL: 'bool', DT_INT: 'int', DT_ENUM: 'enum', DT_RAW: 'raw',
  get() {
    return {
      getDatapoint: (id) => dps[id] || null,
      writeDatapoint: (id, type, value) => {
        writes.push([id, type, value]);
        if (!dps[id] || dps[id].v === undefined) throw new Error('Setting unknown datapoint ' + id);
      },
      queryDatapoints: () => { queries++; },
    };
  },
};
function report(id, v) {           // meldunek sterownika; brak zdarzenia, gdy wartość ta sama
  if (!dps[id]) dps[id] = mkDp(id);
  const dp = dps[id];
  if (dp.v === v) return;
  dp.v = v;
  for (const cb of dp.ls) cb({ v });
}

// --- pola usługi
const ROLES = ['state', 'current_limit', 'mode', 'phase_info', 'session_energy', 'session_duration',
  'cp_state', 'work_mode', 'energy_limit', 'window_start', 'window_end', 'temperature',
  'faults', 'controller_version'];                       // bez 'last_session_energy': brakujące pole
const vcs = {};
for (const r of ROLES) {
  vcs[r] = {
    val: r === 'faults' ? 0 : undefined, ls: [],   // faults jako pole number
    getValue() { return this.val; },
    // setValue woła skrypt: zdarzenie ze źródłem "sys"; ext() = zmiana z HA/strony ("rpc")
    setValue(v, source = 'sys') { const ch = JSON.stringify(v) !== JSON.stringify(this.val); this.val = v; if (ch) emit(this, { value: v, source }); },
    on(ev, cb) { this.ls.push(cb); },
  };
}
// Zdarzenia pól: od razu albo (asyncEvents) w kolejce do flush(), jak w module,
// gdzie docierają do skryptu dopiero po obu zmianach (29.09 12:03:07).
let asyncEvents = false;
const evq = [];
function emit(h, ev) { if (asyncEvents) evq.push([h, ev]); else for (const cb of h.ls) cb(ev); }
function flush() { while (evq.length) { const [h, ev] = evq.shift(); for (const cb of h.ls) cb(ev); } }
function ext(r, v) { vcs[r].setValue(v, 'rpc'); }
let serviceErrors = null;
globalThis.Service = { getVCHandle: (r) => { if (!vcs[r]) throw new Error('no vc ' + r); return vcs[r]; }, setErrors: (e) => { serviceErrors = e; return true; } };
globalThis.setInterval = () => { throw new Error('setInterval nie powinien być użyty'); };
globalThis.clearInterval = () => {};
Date.now = () => 1790650000000 + now;

// --- skrypt
const src = readFileSync(process.argv[2], 'utf8');
writeFileSync(new URL('./skrypt.ts', import.meta.url), src);
await import('./skrypt.ts');

let ok = 0, bad = 0;
function check(name, cond, info) {
  if (cond) { ok++; console.info('  ✔ ' + name); }
  else { bad++; console.info('  ✘ ' + name + (info !== undefined ? '  -> ' + JSON.stringify(info) : '')); }
}
const V = (r) => vcs[r].val;

console.info('1. Start i meldunki sterownika');
report(18, true); report(4, 12); report(1, 0); report(6, '08de0000000000');
report(3, 4); report(13, 4); report(14, 0); report(19, '0000'); report(24, 29); report(10, 0); report(9, 0);
report(23, '5631');
check('state = true', V('state') === true, V('state'));
check('current_limit = 12', V('current_limit') === 12, V('current_limit'));
check('mode = charger_charging', V('mode') === 'charger_charging', V('mode'));
check('faza A 227 V', V('phase_info') && V('phase_info').phase_a.voltage === 227, V('phase_info'));
check('cp_state jeszcze pusty przed tyknięciem (punkt dodany później)', V('cp_state') === undefined, V('cp_state'));
advance(5000);
check('cp_state = controlpi_6v po podpięciu', V('cp_state') === 'controlpi_6v', V('cp_state'));
check('work_mode = charge_now', V('work_mode') === 'charge_now', V('work_mode'));
check('okno 0-0', V('window_start') === 0 && V('window_end') === 0, [V('window_start'), V('window_end')]);
check('temperature = 29', V('temperature') === 29, V('temperature'));
check('controller_version = V1', V('controller_version') === 'V1', V('controller_version'));
check('brak zapisów do sterownika przy samych meldunkach', writes.length === 0, writes);

console.info('2. Limit z pola, sterownik przyjmuje (najpierw odsyła starą wartość)');
ext('current_limit', 10);
check('przed upływem 1 s nic nie poszło', writes.length === 0, writes);
advance(1100);
check('zapis DP4 = 10', JSON.stringify(writes.at(-1)) === JSON.stringify([4, 'int', 10]), writes.at(-1));
report(4, 12);                    // ta sama wartość: brak zdarzenia
advance(1000); report(4, 10);
advance(3000);
check('pole zostaje 10', V('current_limit') === 10, V('current_limit'));
check('jeden zapis', writes.length === 1, writes);

console.info('3. Limit z pola, sterownik nie odpowiada (v4.2: bez kontroli po zapisie)');
ext('current_limit', 15);
advance(3500);
check('pole zostaje 15, jeden nowy zapis', V('current_limit') === 15 && writes.filter((w) => w[0] === 4).length === 2, [V('current_limit'), writes]);
report(4, 12);                    // sterownik zglasza inna wartosc: pole za nia idzie
check('meldunek sterownika poprawia pole na 12', V('current_limit') === 12, V('current_limit'));
check('meldunek nie wraca jako zapis', writes.filter((w) => w[0] === 4).length === 2, writes);

console.info('4. Okno godzin z pola');
ext('window_start', 22);
advance(1100);
check('zapis DP19 = 2 bajty 16 00', JSON.stringify(writes.at(-1)) === JSON.stringify([19, 'raw', String.fromCharCode(22, 0)]), writes.at(-1));
report(19, '1600');
advance(3500);
check('okno 22-0', V('window_start') === 22 && V('window_end') === 0);
ext('window_end', 6);
advance(1100);
check('zapis DP19 = 2 bajty 16 06', JSON.stringify(writes.at(-1)) === JSON.stringify([19, 'raw', String.fromCharCode(22, 6)]), writes.at(-1));
report(19, '1606'); advance(3500);
const n19 = writes.filter((w) => w[0] === 19).length;
report(19, '1707');               // sterownik sam zmienia okno (z menu): 23-7
advance(3500);
check('okno z menu 23-7 w polach', V('window_start') === 23 && V('window_end') === 7, [V('window_start'), V('window_end')]);
check('okno z menu nie wraca do sterownika jako zapis', writes.filter((w) => w[0] === 19).length === n19, writes.filter((w) => w[0] === 19));

console.info('4b. Tryb z pola: modul po wlasnym zapisie nie odswieza wartosci (jak 29.09 10:41)');
report(14, 2);
ext('work_mode', 'charge_now');
advance(1100);
dps[14].v = 2;                    // wartosc widoczna dla skryptu zostaje stara, bez zdarzenia
advance(6000);
check('pole zostaje charge_now (bez cofania do starej wartosci)', V('work_mode') === 'charge_now', V('work_mode'));
report(14, 1);                    // sterownik sam zmienia tryb: pole za nim idzie
check('zmiana zgloszona przez sterownik trafia do pola', V('work_mode') === 'charge_energy', V('work_mode'));

console.info('5. Tryb pracy z pola');
ext('work_mode', 'charge_schedule');
advance(1100);
check('zapis DP14 = 2', JSON.stringify(writes.at(-1)) === JSON.stringify([14, 'enum', 2]), writes.at(-1));
report(14, 2); advance(3500);
check('pole charge_schedule', V('work_mode') === 'charge_schedule');

console.info('6. Limit energii, punkt nigdy niezgłoszony');
ext('energy_limit', 5);
advance(3500);
check('próba zapisu DP17 = 5', writes.some((w) => w[0] === 17 && w[2] === 5), writes);
check('komunikat o odrzuconym zapisie w stanie uslugi', Array.isArray(serviceErrors) && serviceErrors.some((e) => e.includes('zapis DP 17 odrzucony')), serviceErrors);

console.info('7. Czas sesji z tyknięć, niezależny od zegara');
const before = V('session_duration');
Date.now = () => 1790650000000 + now + 45 * 60000;   // skok zegara o 45 min
advance(130000);
check('czas sesji rośnie o około 2 min, nie o 45', V('session_duration') - before >= 2 && V('session_duration') - before <= 3, [before, V('session_duration')]);
report(3, 6);                     // zakończone
const stop = V('session_duration');
advance(120000);
check('po zakończeniu czas stoi', V('session_duration') === stop, [stop, V('session_duration')]);

console.info('8. Moc z punktu 9, licznik i energia sesji');
report(1, 123456);                // licznik z poprzedniej sesji
report(3, 0); report(3, 1);       // nowa sesja: odpięcie i wpięcie
report(9, 6900); report(3, 4); report(1, 123525); report(1, 123594);
check('total_power = 6900 z punktu 9', V('phase_info').total_power === 6900, V('phase_info').total_power);
check('energia sesji 1,38 kWh', V('session_energy') === 1.38, V('session_energy'));

console.info('9. Błędy w polu number i brak pola energii ostatniej sesji');
report(10, 0x41); advance(5000);
check('faults = 65 (surowa wartość w polu number)', V('faults') === 0x41, V('faults'));
report(25, 164);
check('skrypt działa dalej bez pola last_session_energy', true);

console.info('10. Seria kliknięć w HA: idzie tylko ostatnia wartość (29.09: 24 polecenia w 9 s)');
report(17, 2);
advance(5000);                    // punkt 17 podpina się przy najbliższej próbie (co 5 s)
let w17 = writes.filter((w) => w[0] === 17).length;
ext('energy_limit', 1); advance(300); ext('energy_limit', 2); advance(300);
ext('energy_limit', 5); advance(300); ext('energy_limit', 3);
advance(1100);
const s17 = writes.filter((w) => w[0] === 17).slice(w17);
check('jeden zapis DP17 = 3', s17.length === 1 && s17[0][2] === 3, s17);

console.info('11. Wyścig z 12:03:07: HA ustawia 4, spóźniony meldunek sterownika 3');
w17 = writes.filter((w) => w[0] === 17).length;
asyncEvents = true;
ext('energy_limit', 4);           // zdarzenie "rpc" 4 czeka w kolejce
report(17, 3);                    // skrypt wpisuje 3 do pola: zdarzenie "sys" 3 w kolejce
flush();
asyncEvents = false;
advance(1100);
const r17 = writes.filter((w) => w[0] === 17).slice(w17);
check('poszło tylko 4, bez powrotu starej 3', r17.length === 1 && r17[0][2] === 4, r17);
check('pole pokazuje 4', V('energy_limit') === 4, V('energy_limit'));

console.info('12. Tryb "do limitu energii" przy limicie 0: sterownik by odrzucił');
report(17, 0); report(14, 0);
const w14 = writes.filter((w) => w[0] === 14).length;
ext('work_mode', 'charge_energy');
advance(1100);
check('brak zapisu DP14', writes.filter((w) => w[0] === 14).length === w14, writes.filter((w) => w[0] === 14));
check('pole wraca do charge_now', V('work_mode') === 'charge_now', V('work_mode'));
check('komunikat w stanie usługi', serviceErrors.some((e) => e.includes('wymaga limitu')), serviceErrors);
report(17, 5);
ext('work_mode', 'charge_energy');
advance(1100);
check('przy limicie 5 tryb idzie: DP14 = 1', JSON.stringify(writes.at(-1)) === JSON.stringify([14, 'enum', 1]), writes.at(-1));

console.info('13. Okno z równą godziną startu i końca');
report(19, '0206');
let w19 = writes.filter((w) => w[0] === 19).length;
ext('window_end', 2);
advance(1100);
check('brak zapisu okna 2-2', writes.filter((w) => w[0] === 19).length === w19, writes.filter((w) => w[0] === 19));
check('pola wracają do 2-6', V('window_start') === 2 && V('window_end') === 6, [V('window_start'), V('window_end')]);

console.info('14. Okno 0,01 h z HA: pole w pełnych godzinach, bez zbędnego zapisu');
report(19, '0200');
w19 = writes.filter((w) => w[0] === 19).length;
ext('window_end', 0.01);
advance(1100);
check('pole = 0', V('window_end') === 0, V('window_end'));
check('bez zapisu (to samo okno przełączyłoby tryb)', writes.filter((w) => w[0] === 19).length === w19, writes.filter((w) => w[0] === 19));

console.info('15. Limit prądu 6,5 A z HA');
ext('current_limit', 6.5);
advance(1100);
check('zapis 7 A i pole 7', JSON.stringify(writes.at(-1)) === JSON.stringify([4, 'int', 7]) && V('current_limit') === 7, [writes.at(-1), V('current_limit')]);

console.info('16. Włącznik: szybkie przełączanie, idzie stan końcowy');
report(18, true);
const w18 = writes.filter((w) => w[0] === 18).length;
ext('state', false); advance(400); ext('state', true); advance(400); ext('state', false);
advance(1100);
const s18 = writes.filter((w) => w[0] === 18).slice(w18);
check('jeden zapis DP18 = false', s18.length === 1 && s18[0][2] === false, s18);

console.info('17. Start modułu: zmiana pola bez źródła z wartością, którą sterownik właśnie zgłosił');
report(14, 1); report(17, 0);
const w14b = writes.filter((w) => w[0] === 14).length;
const e0 = serviceErrors.length;
for (const cb of vcs.work_mode.ls) cb({ value: 'charge_energy', source: '' });
advance(1100);
check('brak zapisu i brak komunikatu', writes.filter((w) => w[0] === 14).length === w14b && serviceErrors.length === e0, [writes.filter((w) => w[0] === 14).slice(w14b), serviceErrors]);
ext('current_limit', 9); advance(300);
for (const cb of vcs.current_limit.ls) cb({ value: 7, source: '' });   // powrót do wartości sterownika
advance(1100);
check('powrót do wartości sterownika kasuje czekające 9', !writes.some((w) => w[0] === 4 && w[2] === 9), writes.filter((w) => w[0] === 4));
report(19, '0206');
w19 = writes.filter((w) => w[0] === 19).length;
for (const cb of vcs.window_start.ls) cb({ value: 2, source: '' });
advance(1100);
check('okno: ta sama godzina bez zapisu', writes.filter((w) => w[0] === 19).length === w19, writes.filter((w) => w[0] === 19));

console.info('\nwynik: ' + ok + ' ✔, ' + bad + ' ✘');
console.info('log skryptu:\n  ' + logs.join('\n  '));
