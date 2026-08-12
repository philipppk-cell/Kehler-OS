"""Gemeinsame Testbausteine."""

from __future__ import annotations

import pytest

from kehleros.adapters.simulation import SimulationAdapter
from kehleros.config.loader import build_entities
from kehleros.config.models import EntityConfig, VehicleConfig
from kehleros.core.command_bus import CommandBus
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import Risk
from kehleros.domain.models import CommandSpec, Entity


def make_entity(
    entity_id: str,
    *,
    commands: tuple[CommandSpec, ...] = (),
    unit: str | None = None,
    configured: bool = True,
    expected_interval_s: float | None = None,
    deadband: float = 0.0,
    min_value: float | None = None,
    max_value: float | None = None,
    step: float | None = None,
    kind: str = "measurement",
) -> Entity:
    """``kind`` ist nicht kosmetisch.

    Der Simulator leitet sein Verhalten überwiegend aus den Capabilities ab,
    an zwei Stellen aber aus der Art: ``status`` und ``valve`` lassen sich
    daran nicht erkennen. Ein Ventil ohne ``kind`` würde hier als bewegliches
    Teil simuliert — mit Zwischenzuständen, die es nicht hat. Der Test liefe
    durch und prüfte etwas anderes als das ausgelieferte Verhalten.
    """
    return Entity(
        id=entity_id,
        name_key=entity_id,
        commands=commands,
        unit=unit,
        configured=configured,
        expected_interval_s=expected_interval_s,
        deadband=deadband,
        min_value=min_value,
        max_value=max_value,
        step=step,
        kind=kind,
    )


SWITCH = (
    CommandSpec(
        verb="set_state", expects_param="state", params=("state",), timeout_ms=500
    ),
)

SETPOINT = (
    CommandSpec(
        verb="set_value", expects_param="value", params=("value",), timeout_ms=500
    ),
)


def _specs_for(entity_type: str, **felder) -> tuple[CommandSpec, ...]:
    """Die echten Befehle eines Typs — aus dem Loader, nicht nachgebaut.

    Nachgebaute Specs waren hier eine stille Fehlerquelle: Sie sahen richtig
    aus und wichen doch von dem ab, was die Fahrzeugkonfiguration erzeugt.
    Ein Test, der eine andere Spec prüft als die ausgelieferte, prüft nichts.
    """
    config = VehicleConfig(
        entities=[
            EntityConfig(
                id="vehicle.garage.door",
                name_key="t",
                type=entity_type,
                timeout_ms=500,
                **felder,
            )
        ]
    )
    return build_entities(config)[0].commands


MOVABLE = _specs_for("movable")
VALVE = _specs_for("valve", risk=Risk.HIGH)


@pytest.fixture
def registry() -> Registry:
    reg = Registry()
    reg.register_all(
        [
            make_entity("water.pump.main", commands=SWITCH),
            make_entity("vehicle.garage.door", commands=MOVABLE),
            make_entity(
                "water.tank.fresh", unit="percent", expected_interval_s=1.0, deadband=0.5
            ),
            make_entity("vehicle.awning.main", commands=MOVABLE, configured=False),
            make_entity("water.valve.grey", commands=VALVE, kind="valve"),
            make_entity(
                "energy.shore.limit",
                commands=SETPOINT,
                unit="A",
                min_value=3,
                max_value=16,
                step=1,
            ),
        ]
    )
    return reg


@pytest.fixture
def state(registry: Registry) -> StateStore:
    return StateStore(registry)


@pytest.fixture
def events() -> EventBus:
    return EventBus()


@pytest.fixture
def bus(registry: Registry, state: StateStore, events: EventBus) -> CommandBus:
    return CommandBus(registry, state, events)


@pytest.fixture
async def simulation(
    registry: Registry, state: StateStore, events: EventBus, bus: CommandBus
) -> SimulationAdapter:
    adapter = SimulationAdapter(state, events, registry, seed=1)
    await adapter.start()
    bus.register_target(adapter)
    return adapter
