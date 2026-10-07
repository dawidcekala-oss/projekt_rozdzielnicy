// Wirtualna ladowarka AmperePoint Q11 na Shelly DevKit M1.
//
// Pola odpowiadaja punktom danych Tuya z profilu lokalnego
// "Ampere Point Q Series (local)" (amperepoint_q11_pro_evcharger.yaml):
//   text:202    stan ladowarki        DP3  work_state (slowami)
//   text:203    sygnal Control Pilot  DP13 connection_state (slowami)
//   enum:202    tryb ladowania        DP14 work_mode
//   number:200  limit pradu           DP4  charge_cur_set
//   number:201  energia docelowa      DP17 energy_charge
//   number:202  poczatek harmonogramu DP19 bajt 0
//   number:203  koniec harmonogramu   DP19 bajt 1
//   number:204  moc                   DP9  power_total
//   number:205  energia sesji         liczona tak jak w integracji HA
//   number:206  licznik calkowity     DP1  (w Q11 licznik narastajacy)
//   number:207  temperatura           DP24 temp_current
//   boolean:200 ladowanie wlaczone    DP18 switch
//   text:200    fazy L1 L2 L3         DP6 DP7 DP8
//   text:201    bledy                 DP10 fault
// Kody Tuya stanu i sygnalu (charger_free, controlpi_12v...) ida w zdarzeniu
// q11_state. Stan jest polem tekstowym, bo lista w widoku etykiety rysuje
// w tej wersji strony pusty obrazek.
// Pola symulacji, ktorych w prawdziwej ladowarce nie ma:
//   enum:203    samochod: A odlaczony, B podlaczony, C gotowy do ladowania
//   boolean:201 awaria: udaje brak uziemienia
//
// W prawdziwej ladowarce w miejscu funkcji tick() bedzie tlumacz ramek
// Tuya z lacza szeregowego. Pola i ich znaczenie zostaja te same.

let TICK_MS = 2000;
let KVS_KEY = "q11_sim_total_kwh";

let V = {
  mode: Virtual.getHandle("enum:202"),
  car: Virtual.getHandle("enum:203"),
  limit: Virtual.getHandle("number:200"),
  target: Virtual.getHandle("number:201"),
  hStart: Virtual.getHandle("number:202"),
  hEnd: Virtual.getHandle("number:203"),
  power: Virtual.getHandle("number:204"),
  session: Virtual.getHandle("number:205"),
  total: Virtual.getHandle("number:206"),
  temp: Virtual.getHandle("number:207"),
  enable: Virtual.getHandle("boolean:200"),
  fault: Virtual.getHandle("boolean:201"),
  phases: Virtual.getHandle("text:200"),
  errors: Virtual.getHandle("text:201"),
  stateTxt: Virtual.getHandle("text:202"),
  cpTxt: Virtual.getHandle("text:203")
};

let STATE_PL = {
  charger_free: "Wolna",
  charger_insert: "Auto podłączone",
  charger_free_fault: "Wolna, błąd",
  charger_wait: "Czeka na harmonogram",
  charger_charging: "Ładuje",
  charger_pause: "Pauza",
  charger_end: "Zakończone",
  charger_fault: "Błąd"
};
let CP_PL = {
  controlpi_12v: "12 V: brak auta",
  controlpi_9v: "9 V: auto podłączone",
  controlpi_6v: "6 V: auto gotowe",
  controlpi_error: "Błąd sygnału"
};

let sim = { session: 0, total: 0, temp: 23, ended: false, lastState: "", lastSave: 0 };

function rnd(x, d) {
  let p = Math.pow(10, d);
  return Math.round(x * p) / p;
}

function put(h, v) {
  if (h.getValue() !== v) h.setValue(v);
}

function localHour() {
  let s = Shelly.getComponentStatus("sys");
  if (!s || typeof s.unixtime !== "number") return -1;
  let off = typeof s.utc_offset === "number" ? s.utc_offset : 0;
  return Math.floor(((s.unixtime + off) % 86400) / 3600);
}

function inWindow(h, a, b) {
  if (h < 0) return false;          // zegar nieustawiony: ladowarka czeka
  if (a === b) return true;         // ten sam poczatek i koniec: cala doba
  if (a < b) return h >= a && h < b;
  return h >= a || h < b;           // okno przez polnoc
}

function saveTotal() {
  Shelly.call("KVS.Set", { key: KVS_KEY, value: JSON.stringify(rnd(sim.total, 3)) });
}

function tick() {
  let car = V.car.getValue();
  let fault = V.fault.getValue();
  let mode = V.mode.getValue();
  let cp = car === "A" ? "controlpi_12v" : (car === "B" ? "controlpi_9v" : "controlpi_6v");
  let state;

  if (car === "A") {                 // odpiecie auta zamyka sesje
    sim.session = 0;
    sim.ended = false;
  }

  if (fault) {
    state = car === "A" ? "charger_free_fault" : "charger_fault";
  } else if (car === "A") {
    state = "charger_free";
  } else if (car === "B") {
    state = "charger_insert";
  } else if (sim.ended) {
    state = "charger_end";
  } else if (!V.enable.getValue()) {
    state = "charger_pause";
  } else if (mode === "charge_schedule" && !inWindow(localHour(), V.hStart.getValue(), V.hEnd.getValue())) {
    state = "charger_wait";
  } else if (mode === "charge_energy" && sim.session >= V.target.getValue()) {
    state = "charger_end";
    sim.ended = true;
  } else {
    state = "charger_charging";
  }

  let charging = state === "charger_charging";
  let amps = charging ? V.limit.getValue() : 0;
  let kw = 0;
  let txt = "";
  for (let i = 0; i < 3; i++) {
    let v = 229.5 + i * 0.5 + Math.random();
    let a = charging ? amps - 0.1 + Math.random() * 0.2 : 0;
    let p = v * a / 1000;
    kw += p;
    txt += (i ? " | " : "") + "L" + (i + 1) + " " + v.toFixed(1) + " V " + a.toFixed(1) + " A " + p.toFixed(2) + " kW";
  }

  let hours = TICK_MS / 3600000;
  sim.session += kw * hours;
  sim.total += kw * hours;
  sim.temp += ((23 + amps * 1.1) - sim.temp) * 0.03;

  put(V.stateTxt, STATE_PL[state]);
  put(V.cpTxt, CP_PL[cp]);
  put(V.power, rnd(kw, 2));
  put(V.session, rnd(sim.session, 3));
  put(V.total, rnd(sim.total, 2));
  put(V.temp, rnd(sim.temp, 1));
  put(V.phases, txt);
  put(V.errors, fault ? "earth_fault: brak uziemienia (symulacja)" : "brak");

  if (state !== sim.lastState) {
    print("Q11 stan: " + sim.lastState + " -> " + state);
    Shelly.emitEvent("q11_state", { state: state, cp: cp });
    if (sim.lastState === "charger_charging") saveTotal();
    sim.lastState = state;
  }
  let now = Date.now();
  if (charging && now - sim.lastSave > 300000) {
    saveTotal();
    sim.lastSave = now;
  }
}

Shelly.call("KVS.Get", { key: KVS_KEY }, function (res) {
  if (res && res.value) {
    let t = parseFloat(JSON.parse(res.value));
    if (t > 0) sim.total = t;
  }
  Timer.set(TICK_MS, true, tick);
  print("Symulator Q11 wystartowal, licznik calkowity " + sim.total + " kWh");
});
