// Q11 DevKit: TEST LACZA Z MIKROKONTROLEREM Q11. AMPERE POINT, 2026-09-24.
// Wymaga zrodla danych "UART" (IO4 = TX, IO5 = RX) zamiast "Tuya MCU".
// Po tescie wracamy do script.svc.ts v3 i zrodla "Tuya MCU".
//
// Co robi, w kolko dla kazdej predkosci:
//   1. 6 s tylko slucha: czy Q11 nadaje sama z siebie (np. wlasny protokol producenta),
//   2. 12 s co sekunde wysyla pytanie Tuya "heartbeat" na zmiane w dwoch wariantach:
//        v0: 55 AA 00 00 00 00 FF  (wersja 0x00, jak klasyczny modul Tuya)
//        v3: 55 AA 03 00 00 00 02  (wersja 0x03, tak loguje wbudowana obsluga Shelly)
//      i zapisuje, po ktorym wariancie przyszla odpowiedz.
// Kazdy odebrany bajt trafia do logu jako "Q11TEST RX ...".

declare const Timer: any;

// Pierwsze zrodlo UART na liscie w zakladce Data; gdyby portal liczyl wszystkie zrodla razem, drugie.
const uart = UART.get(0) || UART.get(1);
const BAUDS = [9600, 115200, 19200, 38400, 57600, 4800];
const LISTEN_MS = 6000;
const PROBE_MS = 12000;

let bi = 0;
let phase = 'listen';
let lastSent = '-';
let phaseStart = 0;
let rxPhase = 0;
const rxTotal: number[] = [0, 0, 0, 0, 0, 0];
let tick = 0;

function frame(ver: number, cmd: number): string {
  const b = [0x55, 0xaa, ver, cmd, 0x00, 0x00];
  let sum = 0;
  for (let i = 0; i < b.length; i++) sum += b[i];
  b.push(sum & 255);
  let s = '';
  for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
  return s;
}

const HB_V0 = frame(0x00, 0x00);
const HB_V3 = frame(0x03, 0x00);

function hex(s: string): string {
  let o = '';
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i) & 255;
    o += (c < 16 ? '0' : '') + c.toString(16) + ' ';
  }
  return o;
}

function setBaud(): void {
  uart.configure({ baud: BAUDS[bi], mode: '8N1' });
  phase = 'listen';
  phaseStart = Date.now();
  rxPhase = 0;
  lastSent = '-';
  console.log('Q11TEST === predkosc ' + BAUDS[bi] + ' b/s: 6 s nasluchu, potem pytania v0/v3');
}

uart.recv((data: string) => {
  rxPhase += data.length;
  rxTotal[bi] += data.length;
  console.log('Q11TEST RX ' + BAUDS[bi] + ' b/s, faza ' + phase + ', po wyslaniu ' + lastSent +
    ' (' + data.length + ' B): ' + hex(data));
});

function step(): void {
  const t = Date.now() - phaseStart;
  if (phase === 'listen' && t >= LISTEN_MS) {
    console.log('Q11TEST nasluch 6 s bez pytania: odebrano ' + rxPhase + ' B');
    phase = 'probe';
    phaseStart = Date.now();
    rxPhase = 0;
  } else if (phase === 'probe') {
    if (t >= PROBE_MS) {
      console.log('Q11TEST koniec ' + BAUDS[bi] + ' b/s: odpowiedz na pytania ' + rxPhase +
        ' B; lacznie przy tej predkosci ' + rxTotal[bi] + ' B');
      bi = (bi + 1) % BAUDS.length;
      if (bi === 0) console.log('Q11TEST PODSUMOWANIE bajtow wg predkosci: ' + JSON.stringify(BAUDS) + ' -> ' + JSON.stringify(rxTotal));
      setBaud();
      return;
    }
    tick++;
    // wariant zapisany PRZED wyslaniem, zeby odpowiedz przypisala sie do wlasciwego pytania
    if (tick % 2 === 0) {
      lastSent = 'v0';
      uart.write(HB_V0);
    } else {
      lastSent = 'v3';
      uart.write(HB_V3);
    }
  }
}

setBaud();
Timer.set(1000, true, step);
