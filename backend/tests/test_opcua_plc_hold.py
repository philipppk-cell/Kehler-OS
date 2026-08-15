"""Tests für OPC-UA Hold-to-run mit Watchdog."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from kehleros.adapters.opcua_plc_write import OpcUaPlcWriteAdapter
from kehleros.config.hardware import (
    OpcUaPlcDeviceConfig,
    OpcUaWritePointConfig,
)
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.models import Command
from tests.conftest import MOVABLE, make_entity

ENTITY = "vehicle.awning.main"
OUT_REF = 'ns=3;s="HMI Eingänge"."Markise Ausfahren"'
IN_REF = 'ns=3;s="HMI Eingänge"."Markise Einfahren"'


class FakeNode:
    def __init__(self) -> None:
        self.value = False
        self.writes: list[bool] = []

    async def read_value(self) -> bool:
        return self.value

    async def write_value(self, data: Any) -> None:
        value = data.Value.Value
        assert isinstance(value, bool)
        self.value = value
        self.writes.append(value)


class FakeClient:
    def __init__(self) -> None:
        self.nodes: dict[str, FakeNode] = {}

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    def get_node(self, ref: str) -> FakeNode:
        return self.nodes.setdefault(ref, FakeNode())


def device() -> OpcUaPlcDeviceConfig:
    return OpcUaPlcDeviceConfig.model_validate(
        {
            "id": "plc",
            "kind": "PLC",
            "transport": "opcua",
            "connection": {
                "endpoint": "opc.tcp://127.0.0.1:4840",
                "allow_insecure": True,
            },
        }
    )


def points(timeout_ms: int = 800) -> list[OpcUaWritePointConfig]:
    return [
        OpcUaWritePointConfig.model_validate(
            {
                "id": ENTITY,
                "verb": "open",
                "ref": OUT_REF,
                "mode": "hold",
                "hold_timeout_ms": timeout_ms,
            }
        ),
        OpcUaWritePointConfig.model_validate(
            {
                "id": ENTITY,
                "verb": "close",
                "ref": IN_REF,
                "mode": "hold",
                "hold_timeout_ms": timeout_ms,
            }
        ),
    ]


async def build_adapter(timeout_ms: int = 800):
    registry = Registry()
    registry.register_all(
        [
            make_entity(
                ENTITY,
                commands=MOVABLE,
                kind="movable",
                feedback=False,
            )
        ]
    )

    state = StateStore(registry)
    events = EventBus()
    client = FakeClient()

    adapter = OpcUaPlcWriteAdapter(
        state,
        events,
        registry,
        device(),
        points(timeout_ms),
        client_factory=lambda **_: client,
    )

    await adapter.connect()

    return adapter, registry, client


async def test_hold_bleibt_true_bis_stop() -> None:
    adapter, registry, client = await build_adapter()

    open_spec = registry.require(ENTITY).spec_for("open")
    stop_spec = registry.require(ENTITY).spec_for("stop")
    assert open_spec is not None
    assert stop_spec is not None

    await adapter.execute(Command(entity_id=ENTITY, verb="open"), open_spec)

    assert client.nodes[OUT_REF].value is True
    assert client.nodes[IN_REF].value is False

    await adapter.execute(Command(entity_id=ENTITY, verb="stop"), stop_spec)

    assert client.nodes[OUT_REF].value is False
    assert client.nodes[IN_REF].value is False

    await adapter.disconnect()


async def test_heartbeat_verlaengert_hold() -> None:
    adapter, registry, client = await build_adapter(timeout_ms=300)

    open_spec = registry.require(ENTITY).spec_for("open")
    assert open_spec is not None

    await adapter.execute(Command(entity_id=ENTITY, verb="open"), open_spec)

    await asyncio.sleep(0.20)

    # Heartbeat verlängert nur den bereits laufenden Hold und erzeugt
    # keinen zweiten Fahrbefehl.
    await adapter.renew_hold(ENTITY, "open")

    await asyncio.sleep(0.20)
    assert client.nodes[OUT_REF].value is True

    # Nach Ausbleiben des nächsten Heartbeats greift der Watchdog.
    await asyncio.sleep(0.20)
    assert client.nodes[OUT_REF].value is False

    await adapter.disconnect()


async def test_gegenrichtung_wird_waehrend_hold_abgewiesen() -> None:
    adapter, registry, client = await build_adapter()

    open_spec = registry.require(ENTITY).spec_for("open")
    close_spec = registry.require(ENTITY).spec_for("close")
    stop_spec = registry.require(ENTITY).spec_for("stop")

    assert open_spec is not None
    assert close_spec is not None
    assert stop_spec is not None

    await adapter.execute(Command(entity_id=ENTITY, verb="open"), open_spec)

    with pytest.raises(RuntimeError, match="Gegenrichtung"):
        await adapter.execute(
            Command(entity_id=ENTITY, verb="close"),
            close_spec,
        )

    assert client.nodes[OUT_REF].value is True
    assert client.nodes[IN_REF].value is False

    await adapter.execute(Command(entity_id=ENTITY, verb="stop"), stop_spec)
    await adapter.disconnect()
