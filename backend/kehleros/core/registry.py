"""Verzeichnis der bekannten Entities.

Hier steht, *was es gibt und was es kann* — nicht, wie es gerade aussieht.
Konfiguration, Capabilities und Live-Zustand bleiben strikt getrennt
(Kapitel 13 §58/§59).
"""

from __future__ import annotations

from collections.abc import Iterator

from ..domain.ids import Domain, domain_of, validate_entity_id
from ..domain.models import Entity


class DuplicateEntity(ValueError):
    """Eine Entity-ID wurde zweimal registriert."""


class Registry:
    """Die registrierten Entities, gefüllt beim Start aus der Konfiguration."""

    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}

    def register(self, entity: Entity) -> Entity:
        validate_entity_id(entity.id)
        if entity.id in self._entities:
            raise DuplicateEntity(f"Entity '{entity.id}' ist bereits registriert")
        self._entities[entity.id] = entity
        return entity

    def register_all(self, entities: list[Entity]) -> None:
        for entity in entities:
            self.register(entity)

    def get(self, entity_id: str) -> Entity | None:
        return self._entities.get(entity_id)

    def require(self, entity_id: str) -> Entity:
        entity = self._entities.get(entity_id)
        if entity is None:
            raise KeyError(f"Unbekannte Entity '{entity_id}'")
        return entity

    def __contains__(self, entity_id: object) -> bool:
        return entity_id in self._entities

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self) -> Iterator[Entity]:
        return iter(self._entities.values())

    def in_domain(self, domain: Domain) -> list[Entity]:
        return [e for e in self._entities.values() if domain_of(e.id) is domain]

    def unconfigured(self) -> list[Entity]:
        """Entities ohne Hardwarezuordnung.

        Sie erscheinen in der Oberfläche als „Nicht konfiguriert“ und in der
        Diagnose als offener Punkt — es wird kein Zustand erfunden
        (Kapitel 12 §68, Kapitel 18 §101).
        """
        return [e for e in self._entities.values() if not e.configured]
