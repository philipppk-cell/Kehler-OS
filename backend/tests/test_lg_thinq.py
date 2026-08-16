"""LG ThinQ: Status lesen und nur freigegebene Befehle schreiben."""

from __future__ import annotations

from typing import Any

import pytest

from kehleros.adapters.lg_thinq import (
    STATE_ID,
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
            "temperatureInUnits": [
                {
                    "unit": "C",
                    "currentTemperature": 24.5,
                    "targetTemperature": 18,
                }
            ],
        }
        self.controls: list[dict[str, Any]] = []

    async def async_get_device_status(
        self,
        device_id: str,
    ):
        return self.status

    async def async_post_device_control(
        self,
        device_id: str,
        payload: dict[str, Any],
    ):
        self.controls.append(payload)
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
    )

    return adapter, registry, state, fake_api


@pytest.mark.asyncio
async def test_status_wird_gelesen(tmp_path):
    adapter, _, state, _ = build_adapter(tmp_path)

    await adapter.start()
    await adapter.poll()

    power = state.require(STATE_ID).state
    target = state.require(TARGET_ID).state

    assert power.quality is Quality.VALID
    assert power.value == "OFF"
    assert power.source is Source.THINQ

    assert target.quality is Quality.VALID
    assert target.value == 18
    assert target.source is Source.THINQ

    await adapter.stop()


@pytest.mark.asyncio
async def test_ganze_solltemperatur_wird_geschrieben(tmp_path):
    adapter, registry, _, api = build_adapter(tmp_path)

    await adapter.start()

    command = Command(
        entity_id=TARGET_ID,
        verb="set_value",
        params={"value": 19},
    )

    spec = registry.require(TARGET_ID).spec_for("set_value")
    assert spec is not None

    await adapter.execute(command, spec)

    assert api.controls[-1] == {
        "temperatureInUnits": {
            "targetTemperature": 19,
            "unit": "C",
        }
    }

    await adapter.stop()


@pytest.mark.asyncio
async def test_halbe_grade_werden_abgewiesen(tmp_path):
    adapter, registry, _, _ = build_adapter(tmp_path)

    await adapter.start()

    command = Command(
        entity_id=TARGET_ID,
        verb="set_value",
        params={"value": 18.5},
    )

    spec = registry.require(TARGET_ID).spec_for("set_value")
    assert spec is not None

    with pytest.raises(ValueError, match="ganze"):
        await adapter.execute(command, spec)

    await adapter.stop()


@pytest.mark.asyncio
async def test_power_write_ist_explizit_begrenzt(tmp_path):
    adapter, registry, _, api = build_adapter(tmp_path)

    await adapter.start()

    command = Command(
        entity_id=STATE_ID,
        verb="set_state",
        params={"state": "ON"},
    )

    spec = registry.require(STATE_ID).spec_for("set_state")
    assert spec is not None

    await adapter.execute(command, spec)

    assert api.controls[-1] == {
        "operation": {
            "airConOperationMode": "POWER_ON",
        }
    }

    await adapter.stop()
