"""Einmalige Aktionen besitzen keinen dauerhaften Zielzustand."""

from __future__ import annotations

from kehleros.core.command_bus import CommandBus
from kehleros.core.event_bus import EventBus
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import CommandPhase, Quality
from kehleros.domain.models import Command, CommandSpec, Entity


class FakeActionTarget:
    name = "fake-action"

    def owns(self, entity_id: str) -> bool:
        return entity_id == "vehicle.sensors.restart"

    async def execute(self, command: Command, spec: CommandSpec) -> None:
        assert command.verb == "trigger"
        assert spec.expected_value(command) is None


async def test_einmalige_aktion_hinterlaesst_keinen_wunschzustand() -> None:
    registry = Registry()
    registry.register(
        Entity(
            id="vehicle.sensors.restart",
            name_key="vehicle.sensors_restart",
            kind="action",
            feedback=False,
            commands=(CommandSpec(verb="trigger"),),
        )
    )

    state = StateStore(registry)
    events = EventBus()
    bus = CommandBus(registry, state, events)
    bus.register_target(FakeActionTarget())

    result = await bus.submit(
        Command(
            entity_id="vehicle.sensors.restart",
            verb="trigger",
        )
    )

    assert result.phase is CommandPhase.COMPLETED

    current = state.require("vehicle.sensors.restart")
    assert current.requested is None
    assert current.state.quality is Quality.UNKNOWN
    assert current.state.value is None
