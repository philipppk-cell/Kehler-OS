"""Tests für den explizit freigegebenen OPC-UA-Schreibadapter."""

from __future__ import annotations

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
from kehleros.domain.models import Command, CommandSpec
from tests.conftest import VALVE, make_entity

ENTITY = "vehicle.cabinet.group1"
REF = 'ns=3;s="HMI Eingänge"."Schrankgruppe 1 Öffnen"'


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
        self.connected = False

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

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
            "poll_interval_ms": 1000,
        }
    )


def point() -> OpcUaWritePointConfig:
    return OpcUaWritePointConfig.model_validate(
        {
            "id": ENTITY,
            "device": "plc",
            "direction": "write",
            "verb": "open",
            "type": "bool",
            "ref": REF,
            "mode": "pulse",
            "pulse_ms": 50,
        }
    )


async def build_adapter():
    registry = Registry()
    registry.register_all(
        [
            make_entity(
                ENTITY,
                commands=VALVE,
                kind="lock",
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
        [point()],
        client_factory=lambda **_: client,
    )

    await adapter.connect()
    return adapter, registry, client


async def test_sendet_true_false_impuls() -> None:
    adapter, registry, client = await build_adapter()

    spec = registry.require(ENTITY).spec_for("open")
    assert spec is not None

    await adapter.execute(
        Command(entity_id=ENTITY, verb="open"),
        spec,
    )

    assert client.nodes[REF].writes == [True, False]
    assert client.nodes[REF].value is False


async def test_nicht_freigegebenes_verb_wird_abgewiesen() -> None:
    adapter, registry, _ = await build_adapter()

    spec = registry.require(ENTITY).spec_for("close")
    assert spec is not None

    with pytest.raises(RuntimeError, match="Kein OPC-UA-Schreibmapping"):
        await adapter.execute(
            Command(entity_id=ENTITY, verb="close"),
            spec,
        )


async def test_bereits_aktiver_hmi_eingang_wird_nicht_ueberschrieben() -> None:
    adapter, registry, client = await build_adapter()
    client.nodes[REF].value = True

    spec = registry.require(ENTITY).spec_for("open")
    assert spec is not None

    with pytest.raises(RuntimeError, match="nicht FALSE"):
        await adapter.execute(
            Command(entity_id=ENTITY, verb="open"),
            spec,
        )

    assert client.nodes[REF].writes == []


async def test_pulse_wird_waehrend_hold_derselben_entity_abgewiesen() -> None:
    entity_id = "water.valve.grey"
    open_ref = 'ns=3;s="HMI Eingänge"."Ventil Grauwasser Öffnen"'
    close_ref = 'ns=3;s="HMI Eingänge"."Ventil Grauwasser Schließen"'

    registry = Registry()
    registry.register_all(
        [
            make_entity(
                entity_id,
                commands=(
                    CommandSpec(verb="open", hold_to_run=True),
                    CommandSpec(verb="close"),
                    CommandSpec(verb="stop", preempts=True),
                ),
                kind="valve",
                feedback=False,
            )
        ]
    )

    state = StateStore(registry)
    events = EventBus()
    client = FakeClient()

    points = [
        OpcUaWritePointConfig.model_validate(
            {
                "id": entity_id,
                "device": "plc",
                "direction": "write",
                "verb": "open",
                "type": "bool",
                "ref": open_ref,
                "mode": "hold",
                "hold_timeout_ms": 5000,
            }
        ),
        OpcUaWritePointConfig.model_validate(
            {
                "id": entity_id,
                "device": "plc",
                "direction": "write",
                "verb": "close",
                "type": "bool",
                "ref": close_ref,
                "mode": "pulse",
                "pulse_ms": 50,
            }
        ),
    ]

    adapter = OpcUaPlcWriteAdapter(
        state,
        events,
        registry,
        device(),
        points,
        client_factory=lambda **_: client,
    )
    await adapter.connect()

    open_spec = registry.require(entity_id).spec_for("open")
    assert open_spec is not None
    await adapter.execute(
        Command(entity_id=entity_id, verb="open"),
        open_spec,
    )

    assert client.nodes[open_ref].value is True

    close_spec = registry.require(entity_id).spec_for("close")
    assert close_spec is not None

    with pytest.raises(RuntimeError, match="Hold-Richtung bereits aktiv"):
        await adapter.execute(
            Command(entity_id=entity_id, verb="close"),
            close_spec,
        )

    assert client.nodes[close_ref].writes == []

    stop_spec = registry.require(entity_id).spec_for("stop")
    assert stop_spec is not None

    await adapter.execute(
        Command(entity_id=entity_id, verb="stop"),
        stop_spec,
    )

    assert client.nodes[open_ref].value is False
    await adapter.disconnect()
