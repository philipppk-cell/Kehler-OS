"""Konfiguration laden und in Entities übersetzen.

Die Befehle einer Entity ergeben sich aus ihrem Typ. Dadurch bietet die
Oberfläche automatisch nur an, was das Gerät tatsächlich kann — es gibt
keinen Dimmregler ohne Dimmer (Kapitel 12 §55, Kapitel 13 §60).
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from ..domain.models import CommandSpec, Entity
from .models import EntityConfig, Settings, VehicleConfig

log = logging.getLogger(__name__)


class ConfigError(RuntimeError):
    """Die Konfiguration ist unvollständig oder widersprüchlich.

    Wird beim Start gemeldet, damit ein Tippfehler sofort auffällt und nicht
    erst, wenn ein Befehl ins Leere läuft (Kapitel 12 §68).
    """


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"Konfigurationsdatei fehlt: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} ist kein gültiges YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path} muss eine Zuordnung auf oberster Ebene enthalten")
    return data


def load_vehicle(path: Path) -> VehicleConfig:
    """Lädt die Fahrzeugkonfiguration und prüft sie vollständig."""
    try:
        return VehicleConfig.model_validate(load_yaml(path))
    except ValidationError as exc:
        raise ConfigError(f"Fahrzeugkonfiguration {path} ist ungültig:\n{exc}") from exc


def load_settings(path: Path | None) -> Settings:
    """Lädt die Laufzeiteinstellungen; ohne Datei gelten die Vorgaben."""
    if path is None or not path.exists():
        return Settings()
    try:
        return Settings.model_validate(load_yaml(path))
    except ValidationError as exc:
        raise ConfigError(f"Einstellungen {path} sind ungültig:\n{exc}") from exc


# ── Entities ────────────────────────────────────────────────────────────────


def build_entities(vehicle: VehicleConfig) -> list[Entity]:
    """Übersetzt die Konfiguration in registrierbare Entities."""
    return [_build_entity(item) for item in vehicle.entities]


def _build_entity(config: EntityConfig) -> Entity:
    return Entity(
        id=config.id,
        name_key=config.name_key,
        area=config.area,
        unit=config.unit,
        deadband=config.deadband,
        expected_interval_s=config.expected_interval_s,
        configured=config.configured,
        commands=_commands_for(config),
    )


def _commands_for(config: EntityConfig) -> tuple[CommandSpec, ...]:
    """Leitet die Befehle aus dem Entity-Typ ab.

    Ein Messwert bekommt keine Befehle. Das ist keine Vereinfachung, sondern
    die Durchsetzung des Capability-Prinzips: Die Oberfläche kann nichts
    anbieten, was hier nicht steht.
    """
    if config.type == "measurement":
        return ()

    common = {
        "timeout_ms": config.timeout_ms,
        "risk": config.risk,
        "permission": config.permission,
    }

    if config.type == "switch":
        return (
            CommandSpec(
                verb="set_state",
                expects_param="state",
                params=("state",),
                **common,
            ),
        )

    if config.type == "movable":
        return (
            CommandSpec(verb="open", expects="OPEN", **common),
            CommandSpec(verb="close", expects="CLOSED", **common),
            CommandSpec(verb="stop", expects="STOPPED", **common),
        )

    if config.type == "climate_zone":
        return (
            CommandSpec(
                verb="set_target",
                expects_param="celsius",
                params=("celsius",),
                **common,
            ),
        )

    raise ConfigError(f"Unbekannter Entity-Typ '{config.type}' bei '{config.id}'")
