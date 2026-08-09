"""Übersetzung der internen Objekte in das API-Format.

Die API legt keine internen Strukturen offen (Kapitel 6 §32). Sie liefert
semantisch verständliche Daten — und zu jedem Wert die Information, wie
belastbar er ist. Ein Client, der `quality` ignoriert, kann keinen falschen
Zustand anzeigen, weil bei allem außer ``VALID`` gar kein Wert mitkommt.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..core.registry import Registry
from ..domain.models import Command, Entity, EntityState, StateValue


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def state_value(value: StateValue) -> dict[str, Any]:
    return {
        "value": value.value,
        "unit": value.unit,
        "quality": value.quality.value,
        "source": value.source.value if value.source else None,
        "measured_at": _iso(value.measured_at),
        "received_at": _iso(value.received_at),
    }


def entity_definition(entity: Entity) -> dict[str, Any]:
    """Was die Entity *ist und kann* — unabhängig vom aktuellen Zustand."""
    return {
        "id": entity.id,
        "name_key": entity.name_key,
        "area": entity.area,
        "unit": entity.unit,
        "configured": entity.configured,
        "capacity_l": entity.capacity_l,
        "capabilities": [
            {
                "verb": spec.verb,
                "params": list(spec.params),
                "risk": spec.risk.value,
                "needs_confirmation": spec.risk.needs_confirmation,
                "timeout_ms": spec.timeout_ms,
            }
            for spec in entity.commands
        ],
    }


def entity_state(state: EntityState, entity: Entity | None = None) -> dict[str, Any]:
    """Der aktuelle Zustand einer Entity."""
    payload: dict[str, Any] = {
        "entity_id": state.entity_id,
        "seq": state.seq,
        "link": state.link.value,
        "state": state_value(state.state),
        "attributes": {
            name: state_value(value) for name, value in state.attributes.items()
        },
        "requested": None,
    }

    if state.requested is not None:
        # Wunschzustand und tatsächlicher Zustand bleiben getrennt. Die
        # Oberfläche zeigt damit „wird ausgeführt“, ohne etwas über die
        # Hardware zu behaupten (Kapitel 13 §4).
        payload["requested"] = {
            "value": state.requested.value,
            "command_id": state.requested.command_id,
            "since": _iso(state.requested.since),
        }

    if entity is not None:
        payload["definition"] = entity_definition(entity)

    return payload


def snapshot(
    states: dict[str, EntityState], registry: Registry, version: int
) -> dict[str, Any]:
    """Ein vollständiger, in sich konsistenter Ausgangszustand.

    Ein neu verbundener Client bekommt genau einmal alles und danach nur noch
    Änderungen (Kapitel 13 §30).
    """
    return {
        "type": "snapshot",
        "version": version,
        "entities": [
            entity_state(state, registry.get(entity_id))
            for entity_id, state in states.items()
        ],
    }


def delta(state: EntityState) -> dict[str, Any]:
    """Eine einzelne Zustandsänderung."""
    return {"type": "delta", "entity": entity_state(state)}


def command_result(command: Command) -> dict[str, Any]:
    """Das Ergebnis eines Befehls.

    ``detail`` ist die technische Begründung für Diagnose und Audit. Die
    Oberfläche macht daraus eine verständliche Meldung und zeigt den
    Rohtext nicht (Kapitel 17 §22).
    """
    return {
        "command_id": command.id,
        "correlation_id": command.correlation_id,
        "entity_id": command.entity_id,
        "verb": command.verb,
        "phase": command.phase.value,
        "success": command.phase.is_success,
        "rejection": command.rejection.value if command.rejection else None,
        "detail": command.detail,
        "duration_ms": command.duration_ms,
    }
