"""LG ThinQ: bestätigte Funktionen lesen und explizit schreiben."""

from __future__ import annotations

from typing import Any

import pytest

from kehleros.adapters.lg_thinq import (
    FAN_ID,
    INSIDE_ID,
    MODE_ID,
    POWER_SAVE_ID,
    STATE_ID,
    SWING_HORIZONTAL_ID,
    SWING_VERTICAL_ID,
    TARGET_ID,
    LgThinQAdapter,
)
from kehleros.config.hardware import LgThinQDeviceConfig
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import Quality, Source
from kehleros.domain.models import Command
from tests.conftest import SETPOINT, SWITCH, make_entity


class FakeSession:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeApi:
    def __init__(self) -> None:
        self.status: dict[str, Any] = {
            "operation": {
                "airConOperationMode": "POWER_OFF",
            },
            "airConJobMode": {
                "currentJobMode": "COOL",
            },
            "temperatureInUnits": [
                {
                    "unit": "C",
                    "currentTemperature": 24.5,
                    "targetTemperature": 18,
                }
            ],
            "airFlow": {
                "windStrength": "HIGH",
            },
            "windDirection": {
                "rotateUpDown": True,
                "rotateLeftRight": False,
            },
            "powerSave": {
                "powerSaveEnabled": False,
            },
        }
        self.controls: list[dict[str, Any]] = []
        self.status_calls = 0

    async def async_get_device_status(
        self,
        device_id: str,
    ):
        self.status_calls += 1
        return self.status

    async def async_post_device_control(
        self,
        device_id: str,
        payload: dict[str, Any],
    ):
        self.controls.append(payload)

        for resource, properties in payload.items():
            if resource == "temperatureInUnits":
                current = self.status[resource][0]
                current.update(properties)
                continue

            current = self.status.setdefault(
                resource,
                {},
            )

            if isinstance(current, dict):
                current.update(properties)

        return {}


def build_adapter(tmp_path):
    credentials = tmp_path / "thinq.env"
    credentials.write_text(
        "THINQ_PAT=test-token\n"
        "THINQ_COUNTRY=DE\n"
        "THINQ_CLIENT_ID=test-client\n",
        encoding="utf-8",
    )

    device = LgThinQDeviceConfig.model_validate(
        {
            "id": "lg_climate",
            "kind": "CLIMATE",
            "vendor": "LG",
            "model": "S3-M09JA3FA",
            "transport": "thinq",
            "connection": {
                "credentials_file": str(credentials),
                "device_id": "test-device",
            },
            "poll_interval_ms": 3000,
        }
    )

    registry = Registry()
    registry.register_all(
        [
            make_entity(
                INSIDE_ID,
                unit="celsius",
            ),
            make_entity(
                STATE_ID,
                commands=SWITCH,
                kind="switch",
            ),
            make_entity(
                TARGET_ID,
                commands=SETPOINT,
                kind="setpoint",
                unit="celsius",
                min_value=18,
                max_value=30,
                step=1,
            ),
            make_entity(
                MODE_ID,
                commands=SWITCH,
                kind="select",
            ),
            make_entity(
                FAN_ID,
                commands=SWITCH,
                kind="select",
            ),
            make_entity(
                SWING_VERTICAL_ID,
                commands=SWITCH,
                kind="switch",
            ),
            make_entity(
                SWING_HORIZONTAL_ID,
                commands=SWITCH,
                kind="switch",
            ),
            make_entity(
                POWER_SAVE_ID,
                commands=SWITCH,
                kind="switch",
            ),
        ]
    )

    state = StateStore(registry)
    events = EventBus()
    fake_api = FakeApi()

    adapter = LgThinQAdapter(
        state,
        events,
        registry,
        device,
        session_factory=FakeSession,
        api_factory=lambda **kwargs: fake_api,
        readback_delay_s=0.0,
    )

    return adapter, registry, state, fake_api


@pytest.mark.asyncio
async def test_status_wird_vollstaendig_gelesen(
    tmp_path,
):
    adapter, _, state, _ = build_adapter(tmp_path)

    await adapter.start()
    await adapter.poll()

    expected = {
        INSIDE_ID: 24.5,
        STATE_ID: "OFF",
        TARGET_ID: 18,
        MODE_ID: "COOL",
        FAN_ID: "HIGH",
        SWING_VERTICAL_ID: "ON",
        SWING_HORIZONTAL_ID: "OFF",
        POWER_SAVE_ID: "OFF",
    }

    for entity_id, value in expected.items():
        current = state.require(entity_id).state
        assert current.quality is Quality.VALID
        assert current.value == value
        assert current.source is Source.THINQ

    await adapter.stop()


@pytest.mark.asyncio
async def test_ganze_solltemperatur_wird_geschrieben(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()

    command = Command(
        entity_id=TARGET_ID,
        verb="set_value",
        params={"value": 19},
    )

    spec = registry.require(TARGET_ID).spec_for(
        "set_value"
    )
    assert spec is not None

    await adapter.execute(command, spec)

    assert api.controls[-1] == {
        "temperatureInUnits": {
            "targetTemperature": 19,
            "unit": "C",
        }
    }
    assert state.require(TARGET_ID).state.value == 19

    await adapter.stop()


@pytest.mark.asyncio
async def test_halbe_grade_werden_abgewiesen(
    tmp_path,
):
    adapter, registry, _, _ = build_adapter(tmp_path)

    await adapter.start()

    command = Command(
        entity_id=TARGET_ID,
        verb="set_value",
        params={"value": 18.5},
    )

    spec = registry.require(TARGET_ID).spec_for(
        "set_value"
    )
    assert spec is not None

    with pytest.raises(ValueError, match="ganze"):
        await adapter.execute(command, spec)

    await adapter.stop()


async def execute_state(
    adapter,
    registry,
    entity_id,
    value,
):
    spec = registry.require(entity_id).spec_for(
        "set_state"
    )
    assert spec is not None

    await adapter.execute(
        Command(
            entity_id=entity_id,
            verb="set_state",
            params={"state": value},
        ),
        spec,
    )


@pytest.mark.asyncio
async def test_power_write_ist_explizit_begrenzt(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()
    await execute_state(
        adapter,
        registry,
        STATE_ID,
        "ON",
    )

    assert api.controls[-1] == {
        "operation": {
            "airConOperationMode": "POWER_ON",
        }
    }
    assert state.require(STATE_ID).state.value == "ON"

    await adapter.stop()


@pytest.mark.asyncio
async def test_betriebsart_wird_geschrieben(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()
    await execute_state(
        adapter,
        registry,
        MODE_ID,
        "FAN",
    )

    assert api.controls[-1] == {
        "airConJobMode": {
            "currentJobMode": "FAN",
        }
    }
    assert state.require(MODE_ID).state.value == "FAN"

    await adapter.stop()


@pytest.mark.asyncio
async def test_luefterstufe_wird_geschrieben(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()
    await execute_state(
        adapter,
        registry,
        FAN_ID,
        "LOW",
    )

    assert api.controls[-1] == {
        "airFlow": {
            "windStrength": "LOW",
        }
    }
    assert state.require(FAN_ID).state.value == "LOW"

    await adapter.stop()


@pytest.mark.asyncio
async def test_vertikaler_swing_wird_geschrieben(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()
    await execute_state(
        adapter,
        registry,
        SWING_VERTICAL_ID,
        "OFF",
    )

    assert api.controls[-1] == {
        "windDirection": {
            "rotateUpDown": False,
        }
    }
    assert (
        state.require(
            SWING_VERTICAL_ID
        ).state.value
        == "OFF"
    )

    await adapter.stop()


@pytest.mark.asyncio
async def test_horizontaler_swing_wird_geschrieben(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()
    await execute_state(
        adapter,
        registry,
        SWING_HORIZONTAL_ID,
        "ON",
    )

    assert api.controls[-1] == {
        "windDirection": {
            "rotateLeftRight": True,
        }
    }
    assert (
        state.require(
            SWING_HORIZONTAL_ID
        ).state.value
        == "ON"
    )

    await adapter.stop()


@pytest.mark.asyncio
async def test_energiesparen_wird_geschrieben(
    tmp_path,
):
    adapter, registry, state, api = build_adapter(
        tmp_path
    )

    await adapter.start()
    await execute_state(
        adapter,
        registry,
        POWER_SAVE_ID,
        "ON",
    )

    assert api.controls[-1] == {
        "powerSave": {
            "powerSaveEnabled": True,
        }
    }
    assert (
        state.require(
            POWER_SAVE_ID
        ).state.value
        == "ON"
    )

    await adapter.stop()
