#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symulator falownika Huawei SUN2000 (Modbus TCP) dla Home Assistant.
Projekt AMPERE_POINT - 2026-07-05

Emuluje mape rejestrow SUN2000-10KTL-M1 na tyle wiernie, by integracja
HA "Huawei Solar" (wlcrs/huawei_solar) traktowala go jak fizyczny falownik.

ZERO zaleznosci - czysta biblioteka standardowa Pythona (3.8+).

Uruchomienie:  python sun2000_sim.py [--port 502] [--kwp 10] [--time-scale 1] [--no-meter]
"""

import argparse
import json
import math
import os
import random
import socketserver
import struct
import threading
import time
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# Parametry symulowanego falownika
# ----------------------------------------------------------------------------
MODEL_NAME = "SUN2000-10KTL-M1"
SERIAL_NUMBER = "SIMHV2600000001"
PRODUCT_NUMBER = "02312SIM"
RATED_POWER_W = 10000
NB_PV_STRINGS = 2
NB_MPPT = 2

BLOCK_SIZE = 50001  # rejestry 0..50000

REGS = [0] * BLOCK_SIZE
REGS_LOCK = threading.Lock()


# ----------------------------------------------------------------------------
# Kodowanie wartosci do rejestrow 16-bitowych (big-endian, high word first)
# ----------------------------------------------------------------------------
def enc_u16(v):
    return [int(v) & 0xFFFF]


def enc_i16(v):
    return [int(v) & 0xFFFF]


def enc_u32(v):
    v = int(v) & 0xFFFFFFFF
    return [(v >> 16) & 0xFFFF, v & 0xFFFF]


def enc_i32(v):
    v = int(v)
    if v < 0:
        v += 1 << 32
    return enc_u32(v)


def enc_str(s, nregs):
    raw = s.encode("ascii", "ignore")[: nregs * 2]
    raw = raw + b"\x00" * (nregs * 2 - len(raw))
    return [(raw[i] << 8) | raw[i + 1] for i in range(0, len(raw), 2)]


def set_regs(addr, values):
    with REGS_LOCK:
        REGS[addr : addr + len(values)] = values


# ----------------------------------------------------------------------------
# Serwer Modbus TCP (FC 03/04 odczyt, FC 06/16 zapis)
# ----------------------------------------------------------------------------
class ModbusHandler(socketserver.BaseRequestHandler):
    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.request.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def handle(self):
        while True:
            mbap = self._recv_exact(7)
            if mbap is None:
                return
            tid, pid, length, uid = struct.unpack(">HHHB", mbap)
            pdu = self._recv_exact(length - 1)
            if pdu is None or len(pdu) < 1:
                return
            fc = pdu[0]
            resp = self._process(fc, pdu[1:])
            out = struct.pack(">HHHB", tid, pid, len(resp) + 1, uid) + resp
            try:
                self.request.sendall(out)
            except OSError:
                return

    @staticmethod
    def _exc(fc, code):
        return struct.pack(">BB", fc | 0x80, code)

    def _process(self, fc, data):
        try:
            if fc in (3, 4):  # read holding / input registers
                addr, count = struct.unpack(">HH", data[:4])
                if not 1 <= count <= 125:
                    return self._exc(fc, 3)
                if addr + count > BLOCK_SIZE:
                    return self._exc(fc, 2)
                with REGS_LOCK:
                    vals = REGS[addr : addr + count]
                return (
                    struct.pack(">BB", fc, count * 2)
                    + struct.pack(f">{count}H", *vals)
                )
            if fc == 6:  # write single register
                addr, val = struct.unpack(">HH", data[:4])
                if addr >= BLOCK_SIZE:
                    return self._exc(fc, 2)
                set_regs(addr, [val])
                return struct.pack(">BHH", fc, addr, val)
            if fc == 16:  # write multiple registers
                addr, count, bc = struct.unpack(">HHB", data[:5])
                if addr + count > BLOCK_SIZE or bc != count * 2:
                    return self._exc(fc, 2)
                vals = list(struct.unpack(f">{count}H", data[5 : 5 + bc]))
                set_regs(addr, vals)
                return struct.pack(">BHH", fc, addr, count)
            return self._exc(fc, 1)  # illegal function
        except (struct.error, IndexError):
            return self._exc(fc, 3)


class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


# ----------------------------------------------------------------------------
# Logika symulacji
# ----------------------------------------------------------------------------
class Sim:
    def __init__(self, args):
        self.args = args
        self.start_wall = time.time()
        self.state_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sun2000_sim_state.json"
        )
        self.total_kwh = 12345.67  # licznik zycia falownika (odtwarzany z pliku)
        self.exported_kwh = 8000.0
        self.imported_kwh = 1500.0
        self._load_state()

        self.daily_kwh = 0.0
        self.day_peak_w = 0
        self.cloud = 0.85
        self.load_walk = 0.5
        self.sim_day = self._now().date()

    # ------------------------------------------------------------------ czas
    def _now(self):
        """Czas symulacji (opcjonalnie przyspieszony --time-scale)."""
        if self.args.time_scale == 1:
            return datetime.now()
        elapsed = (time.time() - self.start_wall) * self.args.time_scale
        return datetime.fromtimestamp(self.start_wall) + timedelta(seconds=elapsed)

    # ------------------------------------------------------------- stan/dysk
    def _load_state(self):
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                st = json.load(f)
            self.total_kwh = st.get("total_kwh", self.total_kwh)
            self.exported_kwh = st.get("exported_kwh", self.exported_kwh)
            self.imported_kwh = st.get("imported_kwh", self.imported_kwh)
        except (OSError, ValueError):
            pass

    def _save_state(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "total_kwh": round(self.total_kwh, 2),
                        "exported_kwh": round(self.exported_kwh, 2),
                        "imported_kwh": round(self.imported_kwh, 2),
                    },
                    f,
                )
        except OSError:
            pass

    # --------------------------------------------------- rejestry stale (ID)
    def write_identity(self):
        set_regs(30000, enc_str(MODEL_NAME, 15))
        set_regs(30015, enc_str(SERIAL_NUMBER, 10))
        set_regs(30025, enc_str(PRODUCT_NUMBER, 10))
        set_regs(30070, enc_u16(410))               # model ID (umowny)
        set_regs(30071, enc_u16(NB_PV_STRINGS))
        set_regs(30072, enc_u16(NB_MPPT))
        set_regs(30073, enc_u32(RATED_POWER_W))     # Pn
        set_regs(30075, enc_u32(RATED_POWER_W))     # Pmax
        set_regs(30077, enc_u32(RATED_POWER_W))     # Smax
        set_regs(30079, enc_i32(6000))              # Qmax out
        set_regs(30081, enc_i32(-6000))             # Qmax in
        set_regs(32091, enc_u32(int(time.time())))  # startup time
        set_regs(32093, enc_u32(0xFFFFFFFF))        # shutdown time: N/A
        set_regs(37200, enc_u16(0))                 # brak optymalizatorow
        set_regs(42000, enc_u16(0))                 # grid code (umowny, poprawny enum)
        set_regs(43006, enc_i16(120))               # strefa czasowa: UTC+2 (min)
        if not self.args.no_meter:
            set_regs(37125, enc_u16(1))             # licznik: 3-fazowy

    # ------------------------------------------------------- krzywa produkcji
    def _irradiance(self, t):
        """0..1 wg pory dnia (dzwon miedzy wschodem a zachodem)."""
        h = t.hour + t.minute / 60 + t.second / 3600
        if h <= self.args.sunrise or h >= self.args.sunset:
            return 0.0
        x = (h - self.args.sunrise) / (self.args.sunset - self.args.sunrise)
        return math.sin(math.pi * x) ** 1.5

    # ------------------------------------------------------------ krok symul.
    def tick(self, dt_sim_s):
        t = self._now()

        # reset dobowy
        if t.date() != self.sim_day:
            self.sim_day = t.date()
            self.daily_kwh = 0.0
            self.day_peak_w = 0

        # chmury: powolny spacer losowy
        self.cloud = min(1.0, max(0.55, self.cloud + random.gauss(0, 0.015)))

        irr = self._irradiance(t)
        p_dc = self.args.kwp * 1000.0 * irr * self.cloud
        p_dc *= 1 + random.gauss(0, 0.01)
        p_dc = max(0.0, min(p_dc, RATED_POWER_W * 1.05))
        eff = 0.98 if p_dc > 100 else 0.90
        p_ac = p_dc * eff

        self.daily_kwh += p_ac * dt_sim_s / 3.6e6
        self.total_kwh += p_ac * dt_sim_s / 3.6e6
        self.day_peak_w = max(self.day_peak_w, int(p_ac))

        # dom: 0.3-2.5 kW, wieczorny szczyt
        self.load_walk = min(1.0, max(0.0, self.load_walk + random.gauss(0, 0.03)))
        evening = 800 if 18 <= t.hour <= 22 else 0
        p_load = 300 + 1400 * self.load_walk + evening
        p_meter = p_ac - p_load  # >0 eksport do sieci
        if p_meter > 0:
            self.exported_kwh += p_meter * dt_sim_s / 3.6e6
        else:
            self.imported_kwh += -p_meter * dt_sim_s / 3.6e6

        v_ph = 230.0 + random.gauss(0, 1.2)
        freq = 50.0 + random.gauss(0, 0.01)
        i_ph = p_ac / (3 * v_ph) if v_ph else 0.0
        temp = 32.0 + 10.0 * (p_ac / RATED_POWER_W) + random.gauss(0, 0.3)

        day = irr > 0
        # --- stany / alarmy
        set_regs(32000, enc_u16(6 if day else 1))         # state_1
        set_regs(32002, enc_u16(3))                       # state_2
        set_regs(32003, enc_u32(0))                       # state_3
        set_regs(32008, enc_u16(0))                       # alarm_1
        set_regs(32009, enc_u16(0))                       # alarm_2
        set_regs(32010, enc_u16(0))                       # alarm_3
        set_regs(32089, enc_u16(512 if day else 2))       # 512=On-grid, 2=Standby
        set_regs(32090, enc_u16(0))                       # fault code

        # --- lancuchy PV
        for s in range(NB_PV_STRINGS):
            if day:
                v_pv = 590 + random.gauss(0, 4)
                i_pv = (p_dc / NB_PV_STRINGS) / v_pv
            else:
                v_pv, i_pv = 0.0, 0.0
            set_regs(32016 + 2 * s, enc_i16(round(v_pv * 10)))
            set_regs(32017 + 2 * s, enc_i16(round(i_pv * 100)))

        # --- moce / parametry AC
        set_regs(32064, enc_i32(round(p_dc)))             # input power (DC)
        set_regs(32066, enc_u16(4000))                    # U AB 400.0 V
        set_regs(32067, enc_u16(4000))
        set_regs(32068, enc_u16(4000))
        for i, a in enumerate((32069, 32070, 32071)):     # fazy L1-L3
            set_regs(a, enc_u16(round((v_ph + i * 0.3) * 10)))
        for a in (32072, 32074, 32076):
            set_regs(a, enc_i32(round(i_ph * 1000)))
        set_regs(32078, enc_i32(self.day_peak_w))         # szczyt dnia
        set_regs(32080, enc_i32(round(p_ac)))             # active power
        set_regs(32082, enc_i32(0))                       # reactive
        set_regs(32084, enc_i16(1000))                    # PF 1.000
        set_regs(32085, enc_u16(round(freq * 100)))
        set_regs(32086, enc_u16(round(eff * 10000)))      # 98.00 %
        set_regs(32087, enc_i16(round(temp * 10)))
        set_regs(32088, enc_u16(3000))                    # izolacja 3.000 MOhm

        # --- energie
        set_regs(32106, enc_u32(round(self.total_kwh * 100)))
        set_regs(32114, enc_u32(round(self.daily_kwh * 100)))

        # --- licznik energii (power meter)
        if not self.args.no_meter:
            set_regs(37100, enc_u16(1))                   # online
            for i, a in enumerate((37101, 37103, 37105)):
                set_regs(a, enc_i32(round((v_ph + i * 0.3) * 10)))
            i_m = abs(p_meter) / (3 * v_ph) if v_ph else 0
            for a in (37107, 37109, 37111):
                set_regs(a, enc_i32(round(i_m * 100)))
            set_regs(37113, enc_i32(round(p_meter)))      # + = eksport
            set_regs(37115, enc_i32(0))
            set_regs(37117, enc_i16(1000))
            set_regs(37118, enc_i16(round(freq * 100)))
            set_regs(37119, enc_i32(round(self.exported_kwh * 100)))
            set_regs(37121, enc_u32(round(self.imported_kwh * 100)))

        # --- czas systemowy
        set_regs(40000, enc_u32(int(t.timestamp())))

    # ----------------------------------------------------------------- watek
    def run_updater(self):
        last_save = time.time()
        interval = 5.0
        while True:
            try:
                self.tick(interval * self.args.time_scale)
            except Exception as e:  # noqa: BLE001 - symulacja ma zyc dalej
                print(f"[sim] blad ticku: {e}")
            if time.time() - last_save > 60:
                self._save_state()
                last_save = time.time()
            time.sleep(interval)


def main():
    ap = argparse.ArgumentParser(description="Symulator Huawei SUN2000 (Modbus TCP)")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=502)
    ap.add_argument("--kwp", type=float, default=10.0, help="moc instalacji PV [kWp]")
    ap.add_argument("--sunrise", type=float, default=4.8, help="wschod [h]")
    ap.add_argument("--sunset", type=float, default=21.0, help="zachod [h]")
    ap.add_argument("--time-scale", type=float, default=1.0,
                    help="przyspieszenie czasu symulacji (np. 60 = doba w 24 min)")
    ap.add_argument("--no-meter", action="store_true",
                    help="nie symuluj licznika energii (power meter)")
    args = ap.parse_args()

    sim = Sim(args)
    sim.write_identity()
    sim.tick(0.0)

    threading.Thread(target=sim.run_updater, daemon=True).start()

    print(f"[sim] {MODEL_NAME}  S/N {SERIAL_NUMBER}")
    print(f"[sim] Modbus TCP na {args.host}:{args.port} (unit id: dowolny)")
    print(f"[sim] PV {args.kwp} kWp, dzien {args.sunrise}-{args.sunset} h, "
          f"time-scale x{args.time_scale}, meter: {'NIE' if args.no_meter else 'TAK'}")
    print("[sim] Ctrl+C aby zakonczyc")
    srv = ThreadedTCPServer((args.host, args.port), ModbusHandler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        sim._save_state()
        srv.shutdown()


if __name__ == "__main__":
    main()
