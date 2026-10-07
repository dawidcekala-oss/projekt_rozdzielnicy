"""Testowy serwer OCPP 1.6J (CSMS) dla mostu Q11. AMPERE POINT, 2026-09-25.

Uruchomienie:  python -u csms_test.py            (nasluch ws://0.0.0.0:9000/<id ladowarki>)
Zapisuje kazda wymiane komunikatow do ..\\logi\\ocpp_csms_<data>.log.

Polecenia do ladowarki wpisuje sie do pliku polecenia.txt obok skryptu, po jednym w wierszu:
    start [idTag]   RemoteStartTransaction
    stop            RemoteStopTransaction ostatniej transakcji
    limit <A>       SetChargingProfile (TxDefaultProfile, limit w amperach)
    status          TriggerMessage StatusNotification
    meter           TriggerMessage MeterValues
    config          GetConfiguration
Serwer czyta plik co sekunde, wykonuje polecenia i czysci plik.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

from websockets.asyncio.server import serve

from ocpp.routing import on
from ocpp.v16 import ChargePoint, call, call_result
from ocpp.v16.enums import (Action, AuthorizationStatus, ChargingProfileKindType,
                            ChargingProfilePurposeType, ChargingRateUnitType,
                            MessageTrigger, RegistrationStatus)

HERE = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(HERE, "..", "logi")
os.makedirs(LOGDIR, exist_ok=True)
CMD_FILE = os.path.join(HERE, "polecenia.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(os.path.join(LOGDIR, f"ocpp_csms_{datetime.now():%Y-%m-%d_%H%M}.log"),
                                  encoding="utf-8")])
log = logging.getLogger("csms")
logging.getLogger("ocpp").setLevel(logging.INFO)

CONNECTED: dict[str, "CentralSide"] = {}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CentralSide(ChargePoint):
    next_tx = 1
    last_tx: int | None = None

    @on(Action.boot_notification)
    def on_boot(self, charge_point_vendor, charge_point_model, **kw):
        log.info("BOOT %s: %s %s %s", self.id, charge_point_vendor, charge_point_model, kw)
        return call_result.BootNotification(current_time=now(), interval=60,
                                            status=RegistrationStatus.accepted)

    @on(Action.heartbeat)
    def on_heartbeat(self):
        return call_result.Heartbeat(current_time=now())

    @on(Action.status_notification)
    def on_status(self, connector_id, error_code, status, **kw):
        log.info("STATUS %s zlacze %s: %s (%s) %s", self.id, connector_id, status, error_code, kw.get("info", ""))
        return call_result.StatusNotification()

    @on(Action.authorize)
    def on_authorize(self, id_tag):
        return call_result.Authorize(id_tag_info={"status": AuthorizationStatus.accepted})

    @on(Action.start_transaction)
    def on_start(self, connector_id, id_tag, meter_start, timestamp, **kw):
        tx = CentralSide.next_tx
        CentralSide.next_tx += 1
        CentralSide.last_tx = tx
        log.info("START TRANSAKCJI %s nr %s: idTag %s, licznik %s Wh", self.id, tx, id_tag, meter_start)
        return call_result.StartTransaction(transaction_id=tx,
                                            id_tag_info={"status": AuthorizationStatus.accepted})

    @on(Action.stop_transaction)
    def on_stop(self, meter_stop, timestamp, transaction_id, **kw):
        log.info("KONIEC TRANSAKCJI %s nr %s: licznik %s Wh, powod %s", self.id, transaction_id,
                 meter_stop, kw.get("reason"))
        return call_result.StopTransaction()

    @on(Action.meter_values)
    def on_meter(self, connector_id, meter_value, **kw):
        for mv in meter_value:
            parts = []
            for sv in mv.get("sampled_value", []):
                parts.append(f"{sv.get('measurand', 'Energy.Active.Import.Register')}"
                             f"{'/' + sv['phase'] if sv.get('phase') else ''}={sv['value']}{sv.get('unit', '')}")
            log.info("POMIAR %s tx %s: %s", self.id, kw.get("transaction_id"), ", ".join(parts))
        return call_result.MeterValues()


async def run_command(cp: CentralSide, line: str) -> None:
    parts = line.split()
    cmd = parts[0].lower()
    if cmd == "start":
        tag = parts[1] if len(parts) > 1 else "AMPERE-TEST"
        r = await cp.call(call.RemoteStartTransaction(id_tag=tag, connector_id=1))
    elif cmd == "stop":
        if CentralSide.last_tx is None:
            log.info("stop: brak transakcji do zatrzymania")
            return
        r = await cp.call(call.RemoteStopTransaction(transaction_id=CentralSide.last_tx))
    elif cmd == "limit":
        amps = float(parts[1])
        profile = {
            "charging_profile_id": 1,
            "stack_level": 0,
            "charging_profile_purpose": ChargingProfilePurposeType.tx_default_profile,
            "charging_profile_kind": ChargingProfileKindType.absolute,
            "charging_schedule": {
                "charging_rate_unit": ChargingRateUnitType.amps,
                "charging_schedule_period": [{"start_period": 0, "limit": amps}],
            },
        }
        r = await cp.call(call.SetChargingProfile(connector_id=1, cs_charging_profiles=profile))
    elif cmd == "status":
        r = await cp.call(call.TriggerMessage(requested_message=MessageTrigger.status_notification, connector_id=1))
    elif cmd == "meter":
        r = await cp.call(call.TriggerMessage(requested_message=MessageTrigger.meter_values, connector_id=1))
    elif cmd == "config":
        r = await cp.call(call.GetConfiguration())
    else:
        log.info("nieznane polecenie: %s", line)
        return
    log.info("POLECENIE '%s' -> odpowiedz ladowarki: %s", line, r)


async def command_loop() -> None:
    while True:
        await asyncio.sleep(1)
        if not os.path.exists(CMD_FILE):
            continue
        with open(CMD_FILE, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        if not lines:
            continue
        open(CMD_FILE, "w", encoding="utf-8").close()
        for line in lines:
            if not CONNECTED:
                log.info("polecenie '%s' pominiete: zadna ladowarka nie jest polaczona", line)
                continue
            cp = list(CONNECTED.values())[-1]
            try:
                await run_command(cp, line)
            except Exception as e:  # noqa: BLE001
                log.info("polecenie '%s' nieudane: %r", line, e)


async def on_connect(connection):
    cp_id = connection.request.path.strip("/") or "bez-nazwy"
    log.info("POLACZENIE ladowarki %s, podprotokol %s", cp_id, connection.subprotocol)
    cp = CentralSide(cp_id, connection)
    CONNECTED[cp_id] = cp
    try:
        await cp.start()
    except Exception as e:  # noqa: BLE001
        log.info("ROZLACZENIE %s: %r", cp_id, e)
    finally:
        CONNECTED.pop(cp_id, None)


async def main() -> None:
    open(CMD_FILE, "a", encoding="utf-8").close()
    async with serve(on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"]):
        log.info("Serwer OCPP 1.6J nasluchuje na ws://0.0.0.0:9000/<id>; polecenia w %s", CMD_FILE)
        await command_loop()


if __name__ == "__main__":
    asyncio.run(main())
