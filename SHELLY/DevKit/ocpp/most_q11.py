"""Most OCPP 1.6J dla Q11 na Shelly DevKit (wariant A, lokalny). AMPERE POINT, 2026-09-25.

Z jednej strony laczy sie z DevKitem przez WebSocket RPC w sieci lokalnej (ws://<DevKit>/rpc),
z drugiej wystepuje wobec serwera OCPP (CSMS) jako ladowarka OCPP 1.6J.

    python -u most_q11.py [adres DevKitu] [adres serwera OCPP]
    domyslnie: 192.168.0.238 ws://localhost:9000

Pola DevKitu (produkt „Q11 DevKit test”):
    boolean:200 state            wlaczenie ladowania (DP 18)
    number:200  current_limit    limit pradu (DP 4), 6-16 A
    enum:200    mode             stan ladowarki (DP 3)
    object:200  phase_info       fazy i licznik (DP 6/7/8, DP 1)
    number:201  session_duration minuty
    number:202  session_energy   kWh
"""
from __future__ import annotations

import asyncio
import itertools
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from websockets.asyncio.client import connect

from ocpp.routing import on
from ocpp.v16 import ChargePoint, call, call_result
from ocpp.v16.enums import (Action, ChargePointErrorCode, ChargePointStatus,
                            ChargingProfileStatus, ConfigurationStatus, MessageTrigger,
                            Reason, RegistrationStatus, RemoteStartStopStatus, ResetStatus,
                            TriggerMessageStatus, UnlockStatus)

DEVKIT = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.238"
CSMS = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:9000"
CP_ID = "Q11-543204516334"
METER_INTERVAL = 30          # s, MeterValues w trakcie transakcji
LIMIT_MIN, LIMIT_MAX = 6, 16

HERE = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(HERE, "..", "logi")
os.makedirs(LOGDIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(os.path.join(LOGDIR, f"ocpp_most_{datetime.now():%Y-%m-%d_%H%M}.log"),
                                  encoding="utf-8")])
log = logging.getLogger("most")
logging.getLogger("ocpp").setLevel(logging.INFO)

STATUS_MAP = {
    "charger_free": ChargePointStatus.available,
    "charger_insert": ChargePointStatus.preparing,
    "charger_wait": ChargePointStatus.suspended_evse,
    "charger_charging": ChargePointStatus.charging,
    "charger_pause": ChargePointStatus.suspended_evse,
    "charger_end": ChargePointStatus.finishing,
    "charger_fault": ChargePointStatus.faulted,
    "charger_free_fault": ChargePointStatus.faulted,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Strona DevKitu: WebSocket RPC Shelly
# ---------------------------------------------------------------------------

class DevKit:
    def __init__(self, host: str):
        self.url = f"ws://{host}/rpc"
        self.ws = None
        self.ids = itertools.count(1)
        self.pending: dict[int, asyncio.Future] = {}
        self.state: dict[str, dict] = {}
        self.listeners = []           # funkcje (klucz, stary, nowy)
        self.connected = asyncio.Event()

    def value(self, key: str, default=None):
        return self.state.get(key, {}).get("value", default)

    async def rpc(self, method: str, params: dict | None = None, timeout: float = 10):
        if self.ws is None:
            raise ConnectionError("DevKit niepolaczony")
        rid = next(self.ids)
        fut = asyncio.get_running_loop().create_future()
        self.pending[rid] = fut
        await self.ws.send(json.dumps({"id": rid, "src": "most-ocpp", "method": method, "params": params or {}}))
        try:
            msg = await asyncio.wait_for(fut, timeout)
        finally:
            self.pending.pop(rid, None)
        if "error" in msg:
            raise RuntimeError(f"{method}: {msg['error']}")
        return msg.get("result")

    def _merge(self, status: dict) -> None:
        for key, val in status.items():
            if not isinstance(val, dict):
                continue
            old = self.state.get(key, {}).get("value")
            self.state.setdefault(key, {}).update(val)
            new = self.state[key].get("value")
            if "value" in val and old != new:
                for f in self.listeners:
                    f(key, old, new)

    async def run(self) -> None:
        while True:
            try:
                async with connect(self.url, open_timeout=10, ping_interval=20) as ws:
                    self.ws = ws
                    reader = asyncio.create_task(self._reader(ws))
                    full = await self.rpc("Shelly.GetStatus")
                    self._merge(full)
                    # Pola uslugi (owner service:0) nie wchodza do Shelly.GetStatus: odczyt osobno.
                    for key in ("boolean:200", "number:200", "enum:200", "object:200",
                                "number:201", "number:202"):
                        ctype, cid = key.split(":")
                        st = await self.rpc(f"{ctype.capitalize()}.GetStatus", {"id": int(cid)})
                        self._merge({key: st})
                    log.info("DevKit polaczony: stan %s, ladowanie %s, limit %s A, czas DevKitu %s",
                             self.value("enum:200"), self.value("boolean:200"), self.value("number:200"),
                             full.get("sys", {}).get("time"))
                    await self._sync_time(full)
                    self.connected.set()
                    await reader
            except Exception as e:  # noqa: BLE001
                log.info("DevKit: brak polaczenia (%r), ponawiam za 5 s", e)
            self.ws = None
            self.connected.clear()
            await asyncio.sleep(5)

    async def _sync_time(self, full: dict) -> None:
        # Bez internetu DevKit po restarcie nie zna godziny. Ustawienie z mostu pomaga
        # harmonogramom Shelly; UWAGA: obsluga Tuya i tak podaje Q11 czas tylko z serwera czasu.
        if full.get("sys", {}).get("unixtime") is None:
            await self.rpc("Sys.SetTime", {"unixtime": int(time.time())})
            log.info("DevKit nie znal godziny: ustawiona z mostu")

    async def _reader(self, ws) -> None:
        async for raw in ws:
            msg = json.loads(raw)
            if "id" in msg and msg["id"] in self.pending:
                self.pending[msg["id"]].set_result(msg)
            elif msg.get("method") in ("NotifyStatus", "NotifyFullStatus"):
                self._merge(msg.get("params", {}))


# ---------------------------------------------------------------------------
# Strona OCPP: ladowarka 1.6J
# ---------------------------------------------------------------------------

class Q11ChargePoint(ChargePoint):
    def __init__(self, cp_id, connection, dev: DevKit):
        super().__init__(cp_id, connection)
        self.dev = dev
        self.tx_id: int | None = None
        self.pending_tag: str | None = None
        self.heartbeat = 60
        self.last_status = None

    # ---- pomiary ----
    def energy_wh(self) -> int:
        ph = self.dev.value("object:200") or {}
        return int(round(float(ph.get("total_act_energy", 0) or 0) * 1000))

    def sampled(self, context: str) -> list:
        ph = self.dev.value("object:200") or {}
        sv = [{"value": str(self.energy_wh()), "measurand": "Energy.Active.Import.Register",
               "unit": "Wh", "context": context}]
        sv.append({"value": str(ph.get("total_power", 0)), "measurand": "Power.Active.Import",
                   "unit": "W", "context": context})
        for key, phase in (("phase_a", "L1"), ("phase_b", "L2"), ("phase_c", "L3")):
            p = ph.get(key) or {}
            sv.append({"value": str(p.get("current", 0)), "measurand": "Current.Import",
                       "phase": phase, "unit": "A", "context": context})
            sv.append({"value": str(p.get("voltage", 0)), "measurand": "Voltage",
                       "phase": phase, "unit": "V", "context": context})
        sv.append({"value": str(self.dev.value("number:200", 0)), "measurand": "Current.Offered",
                   "unit": "A", "context": context})
        return sv

    async def send_meter(self, context: str = "Sample.Periodic") -> None:
        await self.call(call.MeterValues(connector_id=1, transaction_id=self.tx_id,
                                         meter_value=[{"timestamp": now_iso(),
                                                       "sampled_value": self.sampled(context)}]))

    # ---- stan i transakcje ----
    async def send_status(self, force: bool = False) -> None:
        mode = self.dev.value("enum:200", "charger_free")
        status = STATUS_MAP.get(mode, ChargePointStatus.unavailable)
        if status == self.last_status and not force:
            return
        self.last_status = status
        err = ChargePointErrorCode.other_error if status == ChargePointStatus.faulted else ChargePointErrorCode.no_error
        await self.call(call.StatusNotification(connector_id=1, error_code=err, status=status,
                                                timestamp=now_iso(), info=f"Q11: {mode}"))

    async def on_mode_change(self, old, new) -> None:
        await self.send_status()
        if new == "charger_charging" and self.tx_id is None:
            tag = self.pending_tag or "Q11-LOKALNIE"
            self.pending_tag = None
            r = await self.call(call.StartTransaction(connector_id=1, id_tag=tag,
                                                      meter_start=self.energy_wh(), timestamp=now_iso()))
            self.tx_id = r.transaction_id
            log.info("transakcja %s rozpoczeta (idTag %s)", self.tx_id, tag)
        elif new in ("charger_end", "charger_free", "charger_free_fault", "charger_fault") and self.tx_id is not None:
            reason = Reason.ev_disconnected if new == "charger_free" else Reason.local
            if new in ("charger_fault", "charger_free_fault"):
                reason = Reason.other
            await self.stop_tx(reason)

    async def stop_tx(self, reason) -> None:
        if self.tx_id is None:
            return
        tx, self.tx_id = self.tx_id, None
        await self.call(call.StopTransaction(meter_stop=self.energy_wh(), timestamp=now_iso(),
                                             transaction_id=tx, reason=reason))
        log.info("transakcja %s zakonczona (%s)", tx, reason)

    # ---- polecenia z serwera ----
    @on(Action.remote_start_transaction)
    async def remote_start(self, id_tag, connector_id=None, **kw):
        self.pending_tag = id_tag
        try:
            await self.dev.rpc("Boolean.Set", {"id": 200, "value": True})
            return call_result.RemoteStartTransaction(status=RemoteStartStopStatus.accepted)
        except Exception as e:  # noqa: BLE001
            log.info("RemoteStart nieudany: %r", e)
            return call_result.RemoteStartTransaction(status=RemoteStartStopStatus.rejected)

    @on(Action.remote_stop_transaction)
    async def remote_stop(self, transaction_id, **kw):
        if self.tx_id is not None and transaction_id != self.tx_id:
            return call_result.RemoteStopTransaction(status=RemoteStartStopStatus.rejected)
        try:
            await self.dev.rpc("Boolean.Set", {"id": 200, "value": False})
        except Exception as e:  # noqa: BLE001
            log.info("RemoteStop nieudany: %r", e)
            return call_result.RemoteStopTransaction(status=RemoteStartStopStatus.rejected)
        asyncio.create_task(self.stop_tx(Reason.remote))
        return call_result.RemoteStopTransaction(status=RemoteStartStopStatus.accepted)

    @on(Action.set_charging_profile)
    async def set_profile(self, connector_id, cs_charging_profiles, **kw):
        try:
            sched = cs_charging_profiles["charging_schedule"]
            limit = float(sched["charging_schedule_period"][0]["limit"])
            if str(sched.get("charging_rate_unit", "A")).upper() == "W":
                limit = limit / (3 * 230)          # moc na 3 fazy -> prad na faze
            amps = int(max(LIMIT_MIN, min(LIMIT_MAX, round(limit))))
            await self.dev.rpc("Number.Set", {"id": 200, "value": amps})
            log.info("SetChargingProfile: limit %s -> %s A na Q11", limit, amps)
            return call_result.SetChargingProfile(status=ChargingProfileStatus.accepted)
        except Exception as e:  # noqa: BLE001
            log.info("SetChargingProfile odrzucony: %r", e)
            return call_result.SetChargingProfile(status=ChargingProfileStatus.rejected)

    @on(Action.trigger_message)
    async def trigger(self, requested_message, connector_id=None, **kw):
        async def later():
            await asyncio.sleep(0.5)
            if requested_message == MessageTrigger.status_notification:
                await self.send_status(force=True)
            elif requested_message == MessageTrigger.meter_values:
                await self.send_meter("Trigger")
            elif requested_message == MessageTrigger.heartbeat:
                await self.call(call.Heartbeat())
        if requested_message in (MessageTrigger.status_notification, MessageTrigger.meter_values,
                                 MessageTrigger.heartbeat):
            asyncio.create_task(later())
            return call_result.TriggerMessage(status=TriggerMessageStatus.accepted)
        return call_result.TriggerMessage(status=TriggerMessageStatus.not_implemented)

    @on(Action.get_configuration)
    async def get_config(self, key=None, **kw):
        keys = [
            {"key": "HeartbeatInterval", "readonly": False, "value": str(self.heartbeat)},
            {"key": "MeterValueSampleInterval", "readonly": True, "value": str(METER_INTERVAL)},
            {"key": "NumberOfConnectors", "readonly": True, "value": "1"},
            {"key": "ChargeProfileMaxStackLevel", "readonly": True, "value": "0"},
            {"key": "Q11CurrentLimitA", "readonly": True, "value": str(self.dev.value("number:200"))},
        ]
        return call_result.GetConfiguration(configuration_key=keys)

    @on(Action.change_configuration)
    async def change_config(self, key, value, **kw):
        if key == "HeartbeatInterval":
            self.heartbeat = int(value)
            return call_result.ChangeConfiguration(status=ConfigurationStatus.accepted)
        return call_result.ChangeConfiguration(status=ConfigurationStatus.not_supported)

    @on(Action.unlock_connector)
    async def unlock(self, connector_id, **kw):
        return call_result.UnlockConnector(status=UnlockStatus.not_supported)

    @on(Action.reset)
    async def reset(self, type, **kw):  # noqa: A002
        return call_result.Reset(status=ResetStatus.rejected)

    # ---- petle ----
    async def loops(self) -> None:
        r = await self.call(call.BootNotification(
            charge_point_vendor="AmperePoint", charge_point_model="Q11",
            charge_point_serial_number=CP_ID, firmware_version="Shelly X DevKit + skrypt v3"))
        log.info("BootNotification: %s, heartbeat %s s", r.status, r.interval)
        if r.status != RegistrationStatus.accepted:
            return
        self.heartbeat = r.interval or 60
        await self.dev.connected.wait()
        await self.send_status(force=True)
        if self.dev.value("enum:200") == "charger_charging" and self.tx_id is None:
            await self.on_mode_change(None, "charger_charging")
        loop = asyncio.get_running_loop()

        def listener(key, old, new):
            if key == "enum:200":
                loop.create_task(self.on_mode_change(old, new))
        self.dev.listeners.append(listener)
        try:
            last_hb = last_mv = time.monotonic()
            while True:
                await asyncio.sleep(1)
                t = time.monotonic()
                if t - last_hb >= self.heartbeat:
                    await self.call(call.Heartbeat())
                    last_hb = t
                if self.tx_id is not None and t - last_mv >= METER_INTERVAL:
                    await self.send_meter()
                    last_mv = t
        finally:
            self.dev.listeners.remove(listener)


async def ocpp_side(dev: DevKit) -> None:
    url = f"{CSMS.rstrip('/')}/{CP_ID}"
    while True:
        try:
            async with connect(url, subprotocols=["ocpp1.6"], open_timeout=10) as ws:
                log.info("Polaczono z serwerem OCPP %s", url)
                cp = Q11ChargePoint(CP_ID, ws, dev)
                await asyncio.gather(cp.start(), cp.loops())
        except Exception as e:  # noqa: BLE001
            log.info("Serwer OCPP: brak polaczenia (%r), ponawiam za 10 s", e)
        await asyncio.sleep(10)


async def main() -> None:
    dev = DevKit(DEVKIT)
    await asyncio.gather(dev.run(), ocpp_side(dev))


if __name__ == "__main__":
    asyncio.run(main())
