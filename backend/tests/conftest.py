"""Gemeinsame Testbausteine."""

from __future__ import annotations

import pytest

from kehleros.adapters.simulation import SimulationAdapter
from kehleros.core.command_bus import CommandBus
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
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
) -> Entity:
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

MOVABLE = (
    CommandSpec(verb="open", expects="OPEN", timeout_ms=500),
    CommandSpec(verb="close", expects="CLOSED", timeout_ms=500),
    CommandSpec(verb="stop", expects="STOPPED", timeout_ms=500),
)


@pytest.fixture
def registry() -> Registry:
    reg = Registry()
    reg.register_all(
        [
            make_entity("light.interior.living", commands=SWITCH),
            make_entity("vehicle.garage.door", commands=MOVABLE),
            make_entity(
                "water.tank.fresh", unit="percent", expected_interval_s=1.0, deadband=0.5
            ),
            make_entity("vehicle.awning.main", commands=MOVABLE, configured=False),
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
