"""Entity-IDs und ihre Prüfung.

Aufbau: ``<domain>.<gruppe>.<name>`` — Kleinbuchstaben, ``snake_case``
innerhalb eines Segments, Punkt als Trenner.

Die IDs sind das gemeinsame Vokabular von Backend, API, Automatisierung und
Oberfläche. Eine Hardwarereferenz taucht darin niemals auf; sie existiert
ausschließlich in der Mapping-Konfiguration (Kapitel 12 §57/§58).
"""

from __future__ import annotations

import re
from enum import StrEnum


class Domain(StrEnum):
    """Oberste Ebene einer Entity-ID."""

    ENERGY = "energy"
    WATER = "water"
    CLIMATE = "climate"
    LIGHT = "light"
    VEHICLE = "vehicle"
    LEVELING = "leveling"
    CAMERA = "camera"
    NETWORK = "network"
    SYSTEM = "system"


_SEGMENT = r"[a-z][a-z0-9_]*"
_ENTITY_ID = re.compile(rf"^{_SEGMENT}(\.{_SEGMENT})+$")
_VERB = re.compile(rf"^{_SEGMENT}$")

_DOMAINS = frozenset(d.value for d in Domain)


class InvalidEntityId(ValueError):
    """Eine Entity-ID entspricht nicht der Namenskonvention."""


def validate_entity_id(entity_id: str) -> str:
    """Prüft eine Entity-ID und gibt sie unverändert zurück.

    Wird beim Laden der Konfiguration angewendet, damit ein Tippfehler beim
    Start auffällt und nicht erst, wenn ein Befehl ins Leere läuft
    (Kapitel 12 §68).
    """
    if not entity_id:
        raise InvalidEntityId("Entity-ID ist leer")
    if not _ENTITY_ID.match(entity_id):
        raise InvalidEntityId(
            f"Entity-ID '{entity_id}' entspricht nicht dem Schema "
            "<domain>.<gruppe>.<name> in Kleinbuchstaben"
        )
    domain = entity_id.split(".", 1)[0]
    if domain not in _DOMAINS:
        known = ", ".join(sorted(_DOMAINS))
        raise InvalidEntityId(
            f"Unbekannte Domäne '{domain}' in '{entity_id}'. Bekannt: {known}"
        )
    return entity_id


def domain_of(entity_id: str) -> Domain:
    """Liefert die Domäne einer bereits geprüften Entity-ID."""
    return Domain(entity_id.split(".", 1)[0])


def validate_verb(verb: str) -> str:
    """Prüft ein Command-Verb (``open``, ``set_state``, …)."""
    if not _VERB.match(verb or ""):
        raise InvalidEntityId(
            f"Verb '{verb}' muss aus Kleinbuchstaben und Unterstrichen bestehen"
        )
    return verb


def command_name(entity_id: str, verb: str) -> str:
    """Vollständiger Befehlsname, wie er in Logs und Audit erscheint."""
    return f"{entity_id}.{verb}"


def event_name(entity_id: str, event: str) -> str:
    """Vollständiger Ereignisname, z. B. ``vehicle.garage.door.opened``."""
    return f"{entity_id}.{event}"


def datapoint_name(entity_id: str, attribute: str | None = None) -> str:
    """Referenz auf einen einzelnen Datenpunkt.

    Ohne Attribut ist der Hauptzustand gemeint, sonst z. B.
    ``water.tank.fresh.level``.
    """
    return entity_id if attribute is None else f"{entity_id}.{attribute}"
