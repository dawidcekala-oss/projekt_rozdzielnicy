// Q11 DevKit: TEST LACZA v2 (Tuya + Modbus + parzystosc). AMPERE POINT, 2026-09-24.
// Zrodlo danych "UART" na IO4 (TX) / IO5 (RX), tak jak w tescie v1.
//
// Test v1: zero bajtow od Q11 przy 4800-115200 8N1, na pytanie Tuya v0 i v3.
// Hipoteza: procesor Q11 jest strona, ktora tylko odpowiada, i mowi innym protokolem,
// np. Modbus RTU (czesto 8E1), albo inna parzystoscia.
//
// Dla kazdej kombinacji predkosc x format (8N1, 8E1, 8O1):
//   1,5 s nasluchu, potem po kolei, co 0,5 s:
//     tuya0   55 AA 00 00 00 00 FF              heartbeat Tuya, wersja 0
//     mb1-03  01 03 00 00 00 01 + CRC          Modbus: odczyt rejestru 0, adres 1
//     mb1-04  01 04 00 00 00 01 + CRC          Modbus: rejestr wejsciowy 0, adres 1
//     mb2-03  02 03 00 00 00 01 + CRC          adres 2
//     mb247-03 F7 03 00 00 00 01 + CRC         adres 247
// Kazdy odebrany bajt trafia do logu jako "Q11TEST RX ..." z kombinacja i ostatnim pytaniem.

declare const Timer: any;

const uart = UART.get(0) || UART.get(1);
const BAUDS = [9600, 19200, 115200, 38400, 57600, 4800, 2400];
const MODES = ['8N1', '8E1', '8O1'];
const LISTEN_STEPS = 3;          // 3 x 0,5 s

function bytes(b: number[]): string {
  let s = '';
  for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i] & 255);
  return s;
}

function crc16(b: number[]): number {
  let crc = 0xffff;
  for (let i = 0; i < b.length; i++) {
    crc ^= b[i];
    for (let k = 0; k < 8; k++) crc = (crc & 1) ? ((crc >> 1) ^ 0xa001) : (crc >> 1);
  }
  return crc;
}

function modbus(slave: number, fn: number): string {
  const b = [slave, fn, 0x00, 0x00, 0x00, 0x01];
  const c = crc16(b);
  b.push(c & 255, (c >> 8) & 255);
  return bytes(b);
}

const PROBES = [
  { name: 'tuya0', data: bytes([0x55, 0xaa, 0x00, 0x00, 0x00, 0x00, 0xff]) },
  { name: 'mb1-03', data: modbus(1, 3) },
  { name: 'mb1-04', data: modbus(1, 4) },
  { name: 'mb2-03', data: modbus(2, 3) },
  { name: 'mb247-03', data: modbus(247, 3) },
];

function hex(s: string): string {
  let o = '';
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i) & 255;
    o += (c < 16 ? '0' : '') + c.toString(16) + ' ';
  }
  return o;
}

let combo = 0;
let stepNo = 0;
let lastSent = 'nasluch';
let rxCombo = 0;
const hits: string[] = [];

function comboName(): string {
  return BAUDS[Math.floor(combo / MODES.length) % BAUDS.length] + ' ' + MODES[combo % MODES.length];
}

function startCombo(): void {
  const baud = BAUDS[Math.floor(combo / MODES.length) % BAUDS.length];
  const mode = MODES[combo % MODES.length];
  uart.configure({ baud: baud, mode: mode });
  stepNo = 0;
  rxCombo = 0;
  lastSent = 'nasluch';
}

uart.recv((data: string) => {
  rxCombo += data.length;
  console.log('Q11TEST RX ' + comboName() + ', po: ' + lastSent + ' (' + data.length + ' B): ' + hex(data));
  const tag = comboName() + '/' + lastSent;
  if (hits.indexOf(tag) < 0) hits.push(tag);
});

function step(): void {
  stepNo++;
  if (stepNo <= LISTEN_STEPS) return;
  const p = stepNo - LISTEN_STEPS - 1;
  if (p < PROBES.length) {
    lastSent = PROBES[p].name;
    uart.write(PROBES[p].data);
    return;
  }
  if (p === PROBES.length) return;   // 0,5 s na ostatnia odpowiedz
  if (rxCombo > 0) console.log('Q11TEST ODPOWIEDZ przy ' + comboName() + ': ' + rxCombo + ' B');
  combo++;
  if (combo % (BAUDS.length * MODES.length) === 0) {
    console.log('Q11TEST PODSUMOWANIE cyklu: ' + (hits.length ? 'odpowiedzi: ' + JSON.stringify(hits) : 'cisza we wszystkich ' + (BAUDS.length * MODES.length) + ' kombinacjach'));
  }
  startCombo();
}

console.log('Q11TEST v2 start: ' + BAUDS.length + ' predkosci x ' + MODES.length + ' formaty, pytania Tuya i Modbus');
startCombo();
Timer.set(500, true, step);
