"""Victron MQTT: Mapping, Lesen, Keepalive und explizite Writes."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from kehleros.adapters.victron_mqtt import VictronMqttAdapter
from kehleros.config.hardware import (
    VictronMqttDeviceConfig,
    VictronReadPointConfig,
    VictronWritePointConfig,
)
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import Quality, Source
from kehleros.domain.models import Command
from tests.conftest import SETPOINT, SWITCH, make_entity

PORTAL = "c0619ab78ede"


class FakeTopic:
    def __init__(self, value: str) -> None:
        self.value = value


class FakeMessage:
    def __init__(self, topic: str, payload: bytes) -> None:
        self.topic = FakeTopic(topic)
        self.payload = payload


class FakeMessages:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[FakeMessage] = asyncio.Queue()

    def __aiter__(self):
        return self

    async def __anext__(self) -> FakeMessage:
        return await self.queue.get()


class FakeClient:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.messages = FakeMessages()
        self.subscriptions: list[str] = []
        self.published: list[tuple[str, str, bool]] = []
        self.connected = False

    async def __aenter__(self):
        self.connected = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.connected = False

    async def subscribe(self, topic: str) -> None:
        self.subscriptions.append(topic)

    async def publish(
        self,
        topic: str,
        payload: str = "",
        retain: bool = False,
    ) -> None:
        self.published.append((topic, payload, retain))

    async def push(self, topic: str, value: Any) -> None:
        payload = json.dumps({"value": value}).encode()
        await self.messages.queue.put(
            FakeMessage(topic, payload)
        )


def device() -> VictronMqttDeviceConfig:
    return VictronMqttDeviceConfig.model_validate(
        {
            "id": "victron",
            "kind": "ENERGY",
            "transport": "mqtt",
            "connection": {
                "host": "127.0.0.1",
                "mqtt_port": 1883,
                "portal_id": PORTAL,
                "tls": False,
            },
            "poll_interval_ms": 100,
            "keepalive_interval_s": 30,
        }
    )


def read_point(
    entity_id: str,
    path: str,
    *,
    kind: str = "float",
    values: dict[str, str] | None = None,
) -> VictronReadPointConfig:
    return VictronReadPointConfig.model_validate(
        {
            "id": entity_id,
            "device": "victron",
            "direction": "read",
            "type": kind,
            "path": path,
            **({"values": values} if values is not None else {}),
        }
    )


def write_point(
    entity_id: str,
    verb: str,
    path: str,
    *,
    kind: str,
    param: str,
    values: dict[str, Any] | None = None,
) -> VictronWritePointConfig:
    return VictronWritePointConfig.model_validate(
        {
            "id": entity_id,
            "device": "victron",
            "direction": "write",
            "verb": verb,
            "type": kind,
            "path": path,
            "param": param,
            **({"values": values} if values is not None else {}),
        }
    )


async def build_adapter():
    registry = Registry()
    registry.register_all(
        [
            make_entity(
                "energy.battery.soc",
                unit="percent",
            ),
            make_entity(
                "energy.shore.connected",
                kind="contact",
            ),
            make_entity(
                "energy.shore.limit",
                commands=SETPOINT,
                unit="A",
                min_value=3,
                max_value=16,
                step=1,
            ),
            make_entity(
                "energy.inverter.state",
                commands=SWITCH,
                kind="switch",
            ),
        ]
    )

    state = StateStore(registry)
    events = EventBus()
    client = FakeClient()

    reads = [
        read_point(
            "energy.battery.soc",
            "system/0/Dc/Battery/Soc",
        ),
        read_point(
            "energy.shore.connected",
            "vebus/276/Ac/ActiveIn/ActiveInput",
            kind="mapped",
            values={"0": "CLOSED", "240": "OPEN"},
        ),
        read_point(
            "energy.shore.limit",
            "vebus/276/Ac/In/1/CurrentLimit",
        ),
        read_point(
            "energy.inverter.state",
            "vebus/276/Mode",
            kind="mapped",
            values={"3": "ON", "4": "OFF"},
        ),
    ]

    writes = [
        write_point(
            "energy.shore.limit",
            "set_value",
            "vebus/276/Ac/In/1/CurrentLimit",
            kind="float",
            param="value",
        ),
        write_point(
            "energy.inverter.state",
            "set_state",
            "vebus/276/Mode",
            kind="mapped",
            param="state",
            values={"ON": 3, "OFF": 4},
        ),
    ]

    adapter = VictronMqttAdapter(
        state,
        events,
        registry,
        device(),
        reads,
        writes,
        client_factory=lambda **_: client,
    )

    await adapter.connect()

    return adapter, registry, state, client


async def settle() -> None:
    for _ in range(10):
        await asyncio.sleep(0)


async def test_connect_abonniert_und_fordert_full_publish_an() -> None:
    adapter, _, _, client = await build_adapter()

    try:
        assert (
            f"N/{PORTAL}/system/0/Dc/Battery/Soc"
            in client.subscriptions
        )
        assert (
            f"R/{PORTAL}/keepalive",
            "",
            False,
        ) in client.published
    finally:
        await adapter.disconnect()


async def test_batteriewert_wird_als_victron_wert_uebernommen() -> None:
    adapter, _, state, client = await build_adapter()

    try:
        await client.push(
            f"N/{PORTAL}/system/0/Dc/Battery/Soc",
            92.06,
        )
        await settle()

        value = state.require("energy.battery.soc").state

        assert value.quality is Quality.VALID
        assert value.value == pytest.approx(92.06)
        assert value.source is Source.VICTRON
    finally:
        await adapter.disconnect()


async def test_active_input_wird_zu_kontaktzustand() -> None:
    adapter, _, state, client = await build_adapter()

    try:
        topic = (
            f"N/{PORTAL}/vebus/276/Ac/ActiveIn/ActiveInput"
        )

        await client.push(topic, 240)
        await settle()
        assert state.require(
            "energy.shore.connected"
        ).state.value == "OPEN"

        await client.push(topic, 0)
        await settle()
        assert state.require(
            "energy.shore.connected"
        ).state.value == "CLOSED"
    finally:
        await adapter.disconnect()


async def test_landstromlimit_schreibt_nur_freigegebenes_topic() -> None:
    adapter, registry, _, client = await build_adapter()

    try:
        spec = registry.require(
            "energy.shore.limit"
        ).spec_for("set_value")
        assert spec is not None

        await adapter.execute(
            Command(
                entity_id="energy.shore.limit",
                verb="set_value",
                params={"value": 9},
            ),
            spec,
        )

        assert (
            f"W/{PORTAL}/vebus/276/Ac/In/1/CurrentLimit",
            '{"value":9.0}',
            False,
        ) in client.published

        assert (
            f"R/{PORTAL}/vebus/276/Ac/In/1/CurrentLimit",
            "",
            False,
        ) in client.published
    finally:
        await adapter.disconnect()


async def test_inverter_mapping_ist_ausschliesslich_on_off() -> None:
    adapter, registry, state, client = await build_adapter()

    try:
        topic = f"N/{PORTAL}/vebus/276/Mode"

        await client.push(topic, 3)
        await settle()
        assert state.require(
            "energy.inverter.state"
        ).state.value == "ON"

        spec = registry.require(
            "energy.inverter.state"
        ).spec_for("set_state")
        assert spec is not None

        await adapter.execute(
            Command(
                entity_id="energy.inverter.state",
                verb="set_state",
                params={"state": "OFF"},
            ),
            spec,
        )

        assert (
            f"W/{PORTAL}/vebus/276/Mode",
            '{"value":4}',
            False,
        ) in client.published
    finally:
        await adapter.disconnect()



async def test_poll_fordert_mapped_values_aktiv_neu_an() -> None:
    """Der periodische Refresh muss den echten poll()-Pfad durchlaufen."""

    adapter, _, _, client = await build_adapter()

    try:
        # Erzwingt beim nächsten poll() sofort einen Refresh.
        adapter._last_refresh = 0.0

        await adapter.poll()

        assert (
            f"R/{PORTAL}/system/0/Dc/Battery/Soc",
            "",
            False,
        ) in client.published

        assert (
            f"R/{PORTAL}/vebus/276/Mode",
            "",
            False,
        ) in client.published
    finally:
        await adapter.disconnect()
