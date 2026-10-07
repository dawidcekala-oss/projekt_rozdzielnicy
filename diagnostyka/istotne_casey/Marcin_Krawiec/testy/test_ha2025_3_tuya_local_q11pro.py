"""Customer's setup on HA 2025.3.3: AmperePoint 0.5.40 (empty entry, as at the customer)
+ tuya-local 2026.2.0 with the Q11 PRO profile. The charger is faked with a real Q11 PRO
LOCAL DPS capture (no network). Question: what does the customer have to do to get data?
Mount: /work = tree with custom_components/{tuyaextend_amperepoint,tuya_local}.
"""
import asyncio
import json
import logging
import shutil
import sys
import tempfile
import time
from pathlib import Path

from homeassistant import bootstrap, loader
from homeassistant.const import __version__
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

DOMAIN = "tuyaextend_amperepoint"
DPS = {"3": "charger_free", "4": 8, "9": 0, "10": 0, "13": "controlpi_12v",
       "14": "charge_now", "18": True, "24": 25}
SETTINGS = {"name": "AmperePoint", "session_energy_mode": "auto", "tariff_value": 1.2,
            "currency": "PLN", "complete_power_threshold_kw": 0.25, "complete_idle_minutes": 3}


def entries():
    tl = {"entry_id": "01TUYALOCALFAKE0000000000", "version": 13, "minor_version": 16,
          "domain": "tuya_local", "title": "Ladowarka", "unique_id": "bf00000000000000fake00",
          "data": {"device_id": "bf00000000000000fake00", "host": "192.0.2.10",
                   "local_key": "0123456789abcdef", "protocol_version": 3.5,
                   "poll_only": False, "type": "amperepoint_q11_pro_evcharger"},
          "options": {}, "source": "user", "pref_disable_new_entities": False,
          "pref_disable_polling": False, "disabled_by": None}
    ap = {"entry_id": "01M39PXEKFR6QEZGFY52QTFKEA", "version": 1, "minor_version": 1,
          "domain": DOMAIN, "title": "AmperePoint", "unique_id": None,
          "data": {**SETTINGS, "model": "q11"}, "options": {**SETTINGS, "model": "q_series"},
          "source": "user", "pref_disable_new_entities": False, "pref_disable_polling": False,
          "disabled_by": None}
    return [tl, ap] if "--with-empty" in sys.argv else [tl]


def fake_charger(config: Path):
    sys.path.insert(0, str(config))
    from custom_components.tuya_local import device as d

    async def refresh(self):
        self._cached_state = {**DPS, "updated_at": time.time()}

    d.TuyaLocalDevice.async_refresh = refresh
    d.TuyaLocalDevice.actually_start = lambda self, event=None: None
    d.TuyaLocalDevice.start = lambda self: None


def summary(hass):
    out = []
    for e in hass.config_entries.async_entries(DOMAIN):
        coord = hass.data.get(DOMAIN, {}).get(e.entry_id)
        data = getattr(coord, "data", None) or {}
        keys = sorted(k for k in e.data if k.startswith("source_"))
        out.append(f"  - '{e.title}' state={e.state.name} source={e.data.get('source_integration')} "
                   f"mapped={len(keys)} status={data.get('status')!r} current={data.get('current_limit_a')} "
                   f"temp={data.get('temperature_c')} connected={data.get('vehicle_connected')}")
    return "\n".join(out) or "  (none)"


async def main():
    logging.basicConfig(level=logging.CRITICAL)
    with tempfile.TemporaryDirectory() as directory:
        config = Path(directory)
        for name in (DOMAIN, "tuya_local"):
            shutil.copytree(Path("/work/custom_components") / name, config / "custom_components" / name)
        (config / ".storage").mkdir()
        (config / ".storage" / "core.config_entries").write_text(json.dumps(
            {"version": 1, "minor_version": 1, "key": "core.config_entries",
             "data": {"entries": entries()}}))
        fake_charger(config)
        hass = HomeAssistant(directory)
        loader.async_setup(hass)
        hass.config.skip_pip = True
        assert await bootstrap.async_from_config_dict(
            {"homeassistant": {"name": "t", "time_zone": "Europe/Warsaw"}, "frontend": {}, "lovelace": {}}, hass)
        await hass.async_start()
        await hass.async_block_till_done()
        await asyncio.sleep(3)
        await hass.async_block_till_done()
        print(f"HA {__version__}, scenario: {'empty AP entry present' if '--with-empty' in sys.argv else 'no AP entry'}")
        tl_entities = [e.entity_id for e in er.async_get(hass).entities.values() if e.platform == "tuya_local"]
        print(f"tuya_local entities: {len(tl_entities)}", sorted(tl_entities)[:30])

        from custom_components.tuyaextend_amperepoint.discovery import discover_sources
        for c in discover_sources(hass):
            print(f"candidate: title={c.title!r} model={c.model_key} platform={c.source_integration} "
                  f"mapping={sorted(c.mapping)}")
        print("AmperePoint entries after start (auto-adoption):\n" + summary(hass))

        if "--flow" in sys.argv:
            flow = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
            print("flow:", flow["type"], flow.get("step_id"), flow.get("menu_options"))
            flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"next_step_id": "automatic"})
            print("flow:", flow["type"], flow.get("step_id"), flow.get("errors"), flow.get("reason"))
            if flow["type"] == "form" and flow["step_id"] == "automatic":
                schema = flow["data_schema"].schema
                device_key = next(k for k in schema if str(k) == "source_device_id")
                options = getattr(schema[device_key], "container", None) or getattr(schema[device_key], "options", None)
                print("  options:", options)
                choice = next(iter(options)) if options else None
                flow = await hass.config_entries.flow.async_configure(
                    flow["flow_id"], {"source_device_id": choice, "name": "Ładowarka Q11"})
                print("flow:", flow["type"], flow.get("step_id"), flow.get("errors"), flow.get("reason"))
            if flow["type"] == "form" and flow["step_id"] == "settings":
                flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {})
                print("flow:", flow["type"], flow.get("step_id"), flow.get("errors"), flow.get("reason"))
            await hass.async_block_till_done()
            await asyncio.sleep(2)
            print("AmperePoint entries after config flow:\n" + summary(hass))
        await hass.async_stop()


asyncio.run(main())
