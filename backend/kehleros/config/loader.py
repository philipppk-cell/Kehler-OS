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

from ..domain.enums import Risk
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
        unverified=config.unverified,
        kind=config.type,
        states=tuple(config.states),
        capacity_l=config.capacity_l,
        capacity_ah=config.capacity_ah,
        nominal_voltage=config.nominal_voltage,
        min_value=config.min_value,
        max_value=config.max_value,
        step=config.step,
        warn_below=config.warn_below,
        warn_above=config.warn_above,
        critical_below=config.critical_below,
        critical_above=config.critical_above,
        commands=_commands_for(config),
    )


def _commands_for(config: EntityConfig) -> tuple[CommandSpec, ...]:
    """Leitet die Befehle aus dem Entity-Typ ab.

    Ein Messwert bekommt keine Befehle. Das ist keine Vereinfachung, sondern
    die Durchsetzung des Capability-Prinzips: Die Oberfläche kann nichts
    anbieten, was hier nicht steht.
    """
    if config.type in ("measurement", "contact", "status"):
        return ()

    # Solange nicht bestätigt ist, dass sich eine Funktion über die
    # Schnittstelle überhaupt schalten lässt, entsteht kein Befehl — und damit
    # kein Bedienelement. Die Konfiguration darf die Anlage bereits vollständig
    # beschreiben; ein Schalter in der Oberfläche wäre trotzdem ein
    # Versprechen, das niemand geprüft hat (Kapitel 18 §98/§136).
    #
    # Bei der SCHEER-Heizung ist das der Regelfall: Die Modbus-Registerliste
    # liegt nicht vor, also ist keine einzige schreibende Funktion bestätigt.
    if config.unverified:
        return ()

    common = {
        "timeout_ms": config.timeout_ms,
        "risk": config.risk,
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
        # Eine Fahrt endet auf drei Arten: am Ziel, angehalten oder blockiert.
        # Nur die erste ist ein Erfolg — aber alle drei sind eine Antwort, und
        # keine davon ist ein Timeout.
        ends = {
            "superseded_states": ("STOPPED",),
            "failure_states": ("BLOCKED",),
        }
        return (
            CommandSpec(verb="open", expects="OPEN", **common, **ends),
            CommandSpec(verb="close", expects="CLOSED", **common, **ends),
            # Der Stopp unterbricht und wird selbst nicht unterbrochen.
            CommandSpec(verb="stop", expects="STOPPED", preempts=True, **common),
        )

    if config.type == "valve":
        # Zwei Befehle, zwei Stellungen, kein Stopp — ein Absperrorgan hat
        # nichts dazwischen.
        #
        # ── Warum die beiden verschieden eingestuft sind ──────────────────
        #
        # Das Risiko liegt **im Öffnen**. Ein offenes Ablassventil entleert
        # den Tank, und wo das geschieht, bestimmt nicht die Software.
        # Deshalb trägt `open` die konfigurierte Einstufung und verlangt ab
        # HIGH eine Bestätigung.
        #
        # `close` bleibt ausdrücklich LOW, und das ist kein Versehen:
        # Schließen ist die Handlung, mit der man einen unerwünschten
        # Zustand **beendet**. Sie hinter eine Rückfrage zu stellen hieße,
        # den Rückweg schwerer zu machen als den Hinweg — dieselbe
        # Überlegung, aus der die Strombegrenzung trotz Schreibzugriff nur
        # MEDIUM trägt: Eine Bestätigung ohne Schutzwirkung ist reine
        # Reibung (Kapitel 15 §21).
        #
        # Möglich ist das, weil `risk` seit jeher am einzelnen Befehl hängt
        # und nicht an der Entity. Bisher hat nur niemand davon Gebrauch
        # gemacht; die Oberfläche liest die Einstufung ohnehin je Verb
        # (`needs_confirmation` in serialization.py).
        return (
            CommandSpec(
                verb="open",
                expects="OPEN",
                timeout_ms=config.timeout_ms,
                risk=config.risk,
            ),
            CommandSpec(
                verb="close",
                expects="CLOSED",
                timeout_ms=config.timeout_ms,
                risk=Risk.LOW,
            ),
        )

    if config.type == "setpoint":
        # Ohne bekannte Obergrenze gibt es keinen Befehl — und damit in der
        # Oberfläche kein Bedienelement. Der Wert bleibt sichtbar.
        if config.max_value is None:
            return ()
        return (
            CommandSpec(
                verb="set_value",
                expects_param="value",
                params=("value",),
                **common,
            ),
        )

    raise ConfigError(f"Unbekannter Entity-Typ '{config.type}' bei '{config.id}'")
