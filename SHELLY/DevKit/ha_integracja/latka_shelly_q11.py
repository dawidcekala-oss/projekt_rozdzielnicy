# Latka integracji Shelly w Home Assistant: encje dla ladowarki Q11 na Shelly X.
# AMPERE POINT, 2026-09-29. Dziala na KOPII integracji (custom_components/shelly),
# skopiowanej z tej samej wersji HA (tu 2026.6.4). Uzycie:
#   python latka_shelly_q11.py C:\HomeAssistant\config\custom_components\shelly
# Zmiany:
#   - const.py: kody produktu Ampere Point (AMPERE_POINT_EV_MODELS),
#   - entity.py: pole wyboru bez napisow opcji (meta.ui.titles) nie wywraca encji,
#   - number.py: limit pradu takze dla naszych kodow; limit energii, okno od/do,
#   - switch.py: wlacznik ladowania (klucz "state"),
#   - select.py: tryb pracy (klucz "work_mode"),
#   - sensor.py: stan ladowarki, sygnal pojazdu, energia i czas sesji,
#     energia ostatniej sesji, temperatura, usterki, wersja sterownika,
#   - translations/en.json, pl.json: nazwy nowych encji i stanow,
#   - manifest.json: "version" (wymagane dla integracji z custom_components).
import json
import os
import sys

D = sys.argv[1]
MODELS = '{"apq11dev"}'


def patch(name, pairs):
    p = os.path.join(D, name)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if b in s:
            continue  # juz zalatane
        assert s.count(a) == 1, (name, a[:60])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


def number(name, tkey, role):
    return f'''    "{name}": RpcNumberDescription(
        key="number",
        sub_key="value",
        translation_key="{tkey}",
        max_fn=lambda config: config["max"],
        min_fn=lambda config: config["min"],
        mode_fn=lambda _: NumberMode.BOX,
        step_fn=lambda config: config["meta"]["ui"].get("step"),
        unit=get_virtual_component_unit,
        method="number_set",
        role="{role}",
        models=AMPERE_POINT_EV_MODELS,
    ),
'''


patch("const.py", [(
    'MODEL_TOP_EV_CHARGER_EVE01 = "EVE01"\n',
    'MODEL_TOP_EV_CHARGER_EVE01 = "EVE01"\n'
    '# Ampere Point: ladowarki Q11 na Shelly X (kod produktu z portalu x.shelly.cloud)\n'
    'AMPERE_POINT_EV_MODELS = ' + MODELS + '\n',
)])

patch("entity.py", [(
    'titles = self.coordinator.device.config[key]["meta"]["ui"]["titles"]',
    'titles = self.coordinator.device.config[key]["meta"]["ui"].get("titles") or {}',
)])

patch("number.py", [
    ("    MODEL_TOP_EV_CHARGER_EVE01,\n", "    AMPERE_POINT_EV_MODELS,\n    MODEL_TOP_EV_CHARGER_EVE01,\n"),
    ('''        role="current_limit",
        models={MODEL_TOP_EV_CHARGER_EVE01},
    ),
''', '''        role="current_limit",
        models={MODEL_TOP_EV_CHARGER_EVE01, *AMPERE_POINT_EV_MODELS},
    ),
''' + number("number_ap_energy_limit", "energy_limit", "energy_limit")
    + number("number_ap_window_start", "charging_window_start", "window_start")
    + number("number_ap_window_end", "charging_window_end", "window_end")),
])

patch("switch.py", [
    ("    MODEL_TOP_EV_CHARGER_EVE01,\n", "    AMPERE_POINT_EV_MODELS,\n    MODEL_TOP_EV_CHARGER_EVE01,\n"),
    ('''        role="start_charging",
        models={MODEL_TOP_EV_CHARGER_EVE01},
    ),
''', '''        role="start_charging",
        models={MODEL_TOP_EV_CHARGER_EVE01},
    ),
    "boolean_ap_state": RpcSwitchDescription(
        key="boolean",
        sub_key="value",
        translation_key="charging",
        is_on=lambda status: bool(status["value"]),
        method_on="boolean_set",
        method_off="boolean_set",
        method_params_fn=lambda id, value: (id, value),
        role="state",
        models=AMPERE_POINT_EV_MODELS,
    ),
'''),
])

patch("select.py", [
    ("from .const import ROLE_GENERIC\n", "from .const import AMPERE_POINT_EV_MODELS, ROLE_GENERIC\n"),
    ('''    "enum_generic": RpcSelectDescription(''', '''    "enum_ap_work_mode": RpcSelectDescription(
        key="enum",
        sub_key="value",
        translation_key="work_mode",
        method="enum_set",
        role="work_mode",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "enum_generic": RpcSelectDescription('''),
])

patch("sensor.py", [
    ("from .const import CONF_SLEEP_PERIOD, DRIVER_MISSING_ERROR, ROLE_GENERIC\n",
     "from .const import (\n    AMPERE_POINT_EV_MODELS,\n    CONF_SLEEP_PERIOD,\n    DRIVER_MISSING_ERROR,\n    ROLE_GENERIC,\n)\n"),
    ('''        role="time_charge",
    ),
''', '''        role="time_charge",
    ),
    "enum_ap_mode": RpcSensorDescription(
        key="enum",
        sub_key="value",
        translation_key="charger_state",
        device_class=SensorDeviceClass.ENUM,
        role="mode",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "enum_ap_cp_state": RpcSensorDescription(
        key="enum",
        sub_key="value",
        translation_key="cp_state",
        device_class=SensorDeviceClass.ENUM,
        role="cp_state",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "number_ap_session_energy": RpcSensorDescription(
        key="number",
        sub_key="value",
        translation_key="session_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        role="session_energy",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "number_ap_session_duration": RpcSensorDescription(
        key="number",
        sub_key="value",
        translation_key="session_duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_display_precision=0,
        device_class=SensorDeviceClass.DURATION,
        role="session_duration",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "number_ap_last_session_energy": RpcSensorDescription(
        key="number",
        sub_key="value",
        translation_key="last_session_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        device_class=SensorDeviceClass.ENERGY,
        role="last_session_energy",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "number_ap_temperature": RpcSensorDescription(
        key="number",
        sub_key="value",
        translation_key="controller_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        role="temperature",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "text_ap_faults": RpcSensorDescription(
        key="text",
        sub_key="value",
        translation_key="faults",
        role="faults",
        models=AMPERE_POINT_EV_MODELS,
    ),
    "text_ap_controller_version": RpcSensorDescription(
        key="text",
        sub_key="value",
        translation_key="controller_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        role="controller_version",
        models=AMPERE_POINT_EV_MODELS,
    ),
'''),
])

TR = {
    "en": {
        "number": {
            "energy_limit": {"name": "Energy limit"},
            "charging_window_start": {"name": "Charging window from"},
            "charging_window_end": {"name": "Charging window to"},
        },
        "select": {
            "work_mode": {"name": "Charging mode", "state": {
                "charge_now": "Charge now",
                "charge_energy": "Until energy limit",
                "charge_schedule": "Charging window"}},
        },
        "sensor": {
            "cp_state": {"name": "Vehicle signal", "state": {
                "controlpi_12v": "12 V, no vehicle",
                "controlpi_12v_pwm": "12 V with PWM, no vehicle",
                "controlpi_9v": "9 V, vehicle connected",
                "controlpi_9v_pwm": "9 V with PWM, charger ready",
                "controlpi_6v": "6 V, vehicle requests charging",
                "controlpi_6v_pwm": "6 V with PWM, charging",
                "controlpi_error": "Signal error"}},
            "last_session_energy": {"name": "Last session energy"},
            "controller_temperature": {"name": "Controller temperature"},
            "faults": {"name": "Faults"},
            "controller_version": {"name": "Controller version"},
        },
    },
    "pl": {
        "number": {
            "energy_limit": {"name": "Limit energii"},
            "charging_window_start": {"name": "Okno ładowania od"},
            "charging_window_end": {"name": "Okno ładowania do"},
        },
        "select": {
            "work_mode": {"name": "Tryb ładowania", "state": {
                "charge_now": "ładuj od razu",
                "charge_energy": "do limitu energii",
                "charge_schedule": "w oknie godzin"}},
        },
        "sensor": {
            "cp_state": {"name": "Sygnał pojazdu", "state": {
                "controlpi_12v": "12 V, brak pojazdu",
                "controlpi_12v_pwm": "12 V z PWM, brak pojazdu",
                "controlpi_9v": "9 V, pojazd podłączony",
                "controlpi_9v_pwm": "9 V z PWM, ładowarka gotowa",
                "controlpi_6v": "6 V, pojazd chce ładować",
                "controlpi_6v_pwm": "6 V z PWM, ładowanie",
                "controlpi_error": "błąd sygnału"}},
            "last_session_energy": {"name": "Energia ostatniej sesji"},
            "controller_temperature": {"name": "Temperatura sterownika"},
            "faults": {"name": "Usterki"},
            "controller_version": {"name": "Wersja sterownika"},
        },
    },
}
for lang, plats in TR.items():
    p = os.path.join(D, "translations", lang + ".json")
    d = json.load(open(p, encoding="utf-8"))
    for plat, keys in plats.items():
        d.setdefault("entity", {}).setdefault(plat, {}).update(keys)
    json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)

p = os.path.join(D, "manifest.json")
m = json.load(open(p, encoding="utf-8"))
m["version"] = "2026.6.4-ampere1"
json.dump(m, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
print("zalatane:", D)
