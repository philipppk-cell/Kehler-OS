from __future__ import annotations

from kehleros.adapters.tuya_thermostat import (
    ACTUAL_ID,
    CHILD_LOCK_ID,
    DEMAND_ID,
    ECO_ID,
    MODE_ID,
    STATE_ID,
    TARGET_ID,
    TuyaThermostatAdapter,
)
from kehleros.config.hardware import (
    TuyaThermostatDeviceConfig,
)
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.models import Command, CommandSpec, Entity


class FakeTuyaDevice:
    def __init__(self, *args, **kwargs):
        del args, kwargs

        self.dps = {
            "1": True,
            "2": "auto",
            "4": False,
            "16": 350,
            "24": 290,
            "36": "close",
            "40": False,
        }

        self.writes = []

    def set_socketTimeout(self, timeout):
        self.timeout = timeout

    def status(self):
        return {"dps": dict(self.dps)}

    def set_value(self, dp, value):
        self.writes.append((dp, value))
        self.dps[str(dp)] = value
        return {"dps": {str(dp): value}}


def registry() -> Registry:
    reg = Registry()

    reg.register_all(
        [
            Entity(
                STATE_ID,
                "floor",
                kind="switch",
            ),
            Entity(
                ACTUAL_ID,
                "actual",
                unit="celsius",
            ),
            Entity(
                TARGET_ID,
                "target",
                unit="celsius",
                kind="setpoint",
                min_value=5,
                max_value=45,
                step=0.5,
            ),
            Entity(
                MODE_ID,
                "mode",
                kind="select",
                states=("AUTO", "MANUAL"),
            ),
            Entity(
                ECO_ID,
                "eco",
                kind="switch",
            ),
            Entity(
                DEMAND_ID,
                "demand",
                kind="status",
                states=("IDLE", "HEATING"),
            ),
            Entity(
                CHILD_LOCK_ID,
                "lock",
                kind="switch",
            ),
        ]
    )

    return reg


def config(tmp_path):
    credentials = tmp_path / "tuya.env"

    credentials.write_text(
        "TUYA_FLOOR_DEVICE_ID=test-device\n"
        "TUYA_FLOOR_LOCAL_KEY=test-key\n",
        encoding="utf-8",
    )

    return TuyaThermostatDeviceConfig.model_validate(
        {
            "id": "tuya_floor",
            "name": "Fußbodenheizung",
            "kind": "THERMOSTAT",
            "vendor": "Tuya",
            "model": "Thermostat",
            "transport": "tuya_local",
            "connection": {
                "credentials_file": str(credentials),
                "address": "192.168.1.100",
                "version": 3.5,
            },
            "poll_interval_ms": 1000,
        }
    )


async def test_status_wird_semantisch_uebersetzt(tmp_path):
    reg = registry()
    state = StateStore(reg)
    fake = FakeTuyaDevice()

    adapter = TuyaThermostatAdapter(
        state,
        EventBus(),
        reg,
        config(tmp_path),
        device_factory=lambda *args, **kwargs: fake,
    )

    await adapter.connect()

    assert state.require(STATE_ID).state.value == "ON"
    assert state.require(ACTUAL_ID).state.value == 29.0
    assert state.require(TARGET_ID).state.value == 35.0
    assert state.require(MODE_ID).state.value == "AUTO"
    assert state.require(ECO_ID).state.value == "OFF"
    assert state.require(DEMAND_ID).state.value == "IDLE"
    assert state.require(CHILD_LOCK_ID).state.value == "OFF"


async def test_solltemperatur_wird_mit_faktor_zehn_geschrieben(
    tmp_path,
):
    reg = registry()
    state = StateStore(reg)
    fake = FakeTuyaDevice()

    adapter = TuyaThermostatAdapter(
        state,
        EventBus(),
        reg,
        config(tmp_path),
        device_factory=lambda *args, **kwargs: fake,
    )

    await adapter.connect()

    await adapter.execute(
        Command(
            entity_id=TARGET_ID,
            verb="set_value",
            params={"value": 31.5},
        ),
        CommandSpec(
            verb="set_value",
            expects_param="value",
            params=("value",),
        ),
    )

    assert fake.writes[-1] == (16, 315)
    assert state.require(TARGET_ID).state.value == 31.5


async def test_modus_wird_explizit_gemappt(tmp_path):
    reg = registry()
    state = StateStore(reg)
    fake = FakeTuyaDevice()

    adapter = TuyaThermostatAdapter(
        state,
        EventBus(),
        reg,
        config(tmp_path),
        device_factory=lambda *args, **kwargs: fake,
    )

    await adapter.connect()

    await adapter.execute(
        Command(
            entity_id=MODE_ID,
            verb="set_state",
            params={"state": "MANUAL"},
        ),
        CommandSpec(
            verb="set_state",
            expects_param="state",
            params=("state",),
        ),
    )

    assert fake.writes[-1] == (2, "manual")
    assert state.require(MODE_ID).state.value == "MANUAL"


async def test_unbekannte_entity_wird_nicht_geschrieben(tmp_path):
    reg = registry()
    state = StateStore(reg)
    fake = FakeTuyaDevice()

    adapter = TuyaThermostatAdapter(
        state,
        EventBus(),
        reg,
        config(tmp_path),
        device_factory=lambda *args, **kwargs: fake,
    )

    await adapter.connect()

    try:
        await adapter.execute(
            Command(
                entity_id="heating.floor.unknown",
                verb="set_state",
                params={"state": "ON"},
            ),
            CommandSpec(
                verb="set_state",
                expects_param="state",
                params=("state",),
            ),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "Unbekannte Entity wurde nicht abgewiesen"
        )

    assert fake.writes == []
