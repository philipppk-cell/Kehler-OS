"""Konfigurationsmodelle.

Konfiguration kommt von außen und wird deshalb validiert, bevor sie das
laufende System erreicht. Ein ungültiger Wert verhindert die Übernahme,
statt Schaden anzurichten (Kapitel 15 §76).

Fahrzeugspezifische Werte stehen ausschließlich hier und niemals im Code
(Kapitel 17 §48). Fehlt eine Angabe, bleibt sie leer — sie wird nicht
erfunden (Kapitel 18 §97/§98).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..domain.enums import Environment, Risk
from ..domain.ids import validate_entity_id


class _Strict(BaseModel):
    """Unbekannte Felder sind ein Fehler, kein stiller Zufall."""

    model_config = ConfigDict(extra="forbid")


EntityType = Literal[
    "measurement", "contact", "switch", "movable", "climate_zone", "setpoint"
]
"""Ein ``contact`` ist ein binärer Sensor — Tür, Fenster, Endschalter.

Er ist bewusst von ``measurement`` getrennt: Ein Türkontakt liefert OPEN oder
CLOSED, keinen Zahlenwert. Diese Unterscheidung ist real und nicht nur eine
Eigenheit der Simulation.

Ein ``setpoint`` ist ein einstellbarer Zahlenwert mit Grenzen — etwa die
Eingangsstrombegrenzung des Landstroms. **Ohne konfigurierte Grenzen bietet
die Oberfläche keine Bedienung an.** Das ist kein Sonderfall, sondern
dieselbe Regel wie überall: Was nicht bekannt ist, wird nicht erfunden
(Kapitel 18 §98). Eine Strombegrenzung ohne die reale Absicherung des
Anschlusses zu kennen, wäre eine gefährliche Erfindung.
"""


class EntityConfig(_Strict):
    """Eine logische Entity, wie das Fahrzeug sie besitzt."""

    id: str
    name_key: str
    type: EntityType = "measurement"
    area: str | None = None
    unit: str | None = None

    deadband: float = Field(default=0.0, ge=0)
    """Ab welcher Änderung ein analoger Wert überhaupt gemeldet wird.

    Verhindert, dass ein zappelnder Sensor Netz und Oberfläche flutet
    (Kapitel 13 §67).
    """

    expected_interval_s: float | None = Field(default=None, gt=0)
    """Erwartetes Aktualisierungsintervall. Bleibt es aus, altert der Wert
    sichtbar zu STALE und dann UNKNOWN (Kapitel 13 §9)."""

    timeout_ms: int = Field(default=5000, gt=0)
    """Wie lange auf die Hardwarebestätigung gewartet wird.

    Bewusst je Entity: Eine Lampe und ein Hydraulikzylinder haben verschiedene
    physikalische Reaktionszeiten (Kapitel 13 §70).
    """

    risk: Risk = Risk.LOW
    permission: str | None = None

    configured: bool = True
    """``False`` heißt: vorgesehen, aber ohne Hardwarezuordnung. Die
    Oberfläche zeigt dann „Nicht konfiguriert“ (Kapitel 18 §101)."""

    min_value: float | None = None
    max_value: float | None = None
    step: float | None = Field(default=None, gt=0)
    """Grenzen und Schrittweite eines ``setpoint``.

    Fehlt ``max_value``, wird der Wert nur angezeigt und nicht einstellbar —
    siehe ``EntityType``.
    """

    capacity_ah: float | None = Field(default=None, gt=0)
    nominal_voltage: float | None = Field(default=None, gt=0)
    """Nur für die Batterie. Aus beidem folgt der Energieinhalt.

    Die Nennspannung steht bewusst in der Konfiguration und nicht im Code:
    Ob ein „24-V-System" nominal mit 24,0 oder 25,6 V rechnet, ist eine
    Eigenschaft der Anlage.
    """

    capacity_l: float | None = Field(default=None, gt=0)
    """Nur für Tanks. Ohne Angabe zeigt die Oberfläche keine Literwerte —
    eine Kapazität wird nicht geraten (Kapitel 18 §98)."""

    warn_below: float | None = None
    warn_above: float | None = None
    critical_below: float | None = None
    critical_above: float | None = None

    @field_validator("id")
    @classmethod
    def _check_id(cls, value: str) -> str:
        return validate_entity_id(value)


class AreaConfig(_Strict):
    id: str
    name_key: str


class VehicleConfig(_Strict):
    """Das konkrete Fahrzeug."""

    version: int = 1
    name: str | None = None
    areas: list[AreaConfig] = Field(default_factory=list)
    entities: list[EntityConfig] = Field(default_factory=list)

    @field_validator("entities")
    @classmethod
    def _unique_ids(cls, entities: list[EntityConfig]) -> list[EntityConfig]:
        seen: set[str] = set()
        for entity in entities:
            if entity.id in seen:
                raise ValueError(f"Entity '{entity.id}' ist mehrfach konfiguriert")
            seen.add(entity.id)
        return entities


class SimulationConfig(_Strict):
    seed: int | None = None
    poll_interval_s: float = Field(default=1.0, gt=0)


class ServerConfig(_Strict):
    host: str = "127.0.0.1"
    port: int = Field(default=8000, gt=0, lt=65536)


class Settings(_Strict):
    """Laufzeiteinstellungen.

    Die Betriebsart wird beim Start festgelegt und ist zur Laufzeit nicht
    umschaltbar (Kapitel 15 §96).
    """

    environment: Environment = Environment.SIMULATION
    log_level: str = "INFO"
    server: ServerConfig = Field(default_factory=ServerConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    stale_sweep_interval_s: float = Field(default=2.0, gt=0)

    @property
    def is_simulated(self) -> bool:
        """Ob reale Hardware angesteuert wird.

        Läuft das System simuliert, kennzeichnet die Oberfläche das dauerhaft
        sichtbar (Kapitel 18 §66).
        """
        return self.environment is not Environment.PRODUCTION
