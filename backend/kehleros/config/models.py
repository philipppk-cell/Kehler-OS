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


EntityType = Literal["measurement", "contact", "status", "switch", "movable", "setpoint"]
"""Ein ``contact`` ist ein binärer Sensor — Tür, Fenster, Endschalter.

Er ist bewusst von ``measurement`` getrennt: Ein Türkontakt liefert OPEN oder
CLOSED, keinen Zahlenwert. Diese Unterscheidung ist real und nicht nur eine
Eigenheit der Simulation.

Ein ``status`` ist ein mehrwertiger Zustand ohne Bedienung — der Brenner der
SCHEER-Heizung meldet nicht „an/aus", sondern eine Betriebsphase. Ihn als
``contact`` zu führen hieße, fünf Zustände in zwei zu pressen; ihn als
``switch`` zu führen hieße zu behaupten, Kehler OS könne ihn setzen. Beides
wäre falsch: Die Phase entsteht in der HeatMate-Regelung, hier wird sie nur
gelesen.

Ein ``setpoint`` ist ein einstellbarer Zahlenwert mit Grenzen — die
Eingangsstrombegrenzung des Landstroms ebenso wie eine Solltemperatur. Es gab
dafür zeitweise einen eigenen Typ ``climate_zone``; er ist entfallen, weil
zwei Mechanismen für dieselbe Sache unweigerlich auseinanderlaufen — und
weil nur einer von beiden die Grenzen geprüft hat. **Ohne konfigurierte Grenzen bietet
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

    unverified: bool = False
    """``True`` heißt: Die Funktion ist am Gerät zu erwarten, aber es ist
    **nicht bestätigt**, dass sie über die Schnittstelle verfügbar ist.

    Der Unterschied zu ``configured: false`` ist nicht kosmetisch. „Nicht
    konfiguriert" heißt: Die Funktion existiert, ihr fehlt nur die Zuordnung.
    „Noch zu verifizieren" heißt: Ob sie sich überhaupt lesen oder schalten
    lässt, weiß niemand — bei der SCHEER-Heizung liegt die Modbus-Registerliste
    noch nicht vor (Punkt G1). Die Oberfläche muss beides auseinanderhalten
    können, sonst verspricht sie Funktionen, die es vielleicht nie gibt.

    Beides kann gleichzeitig gelten und tut es anfangs auch: Was noch zu
    verifizieren ist, ist erst recht nicht zugeordnet. Sobald ein Register
    bestätigt und gemappt ist, fallen beide Kennzeichen weg.
    """

    states: list[str] = Field(default_factory=list)
    """Die möglichen Zustände eines ``status``.

    Das ist das **interne Vokabular von Kehler OS**, nicht das des Geräts.
    Welcher Registerwert der HeatMate auf welchen Namen abgebildet wird,
    entscheidet später der Adapter — hier stehen nur die Namen, die die
    Software kennt und übersetzt.

    Ohne diese Angabe simuliert der Simulator die Entity **nicht**: Er würde
    sonst raten. Ein Brenner, der „CLOSED" meldet, wäre kein Testfall,
    sondern ein Fehler, der wie ein Zustand aussieht.
    """

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


class HistoryConfig(_Strict):
    """Messhistorie (Kapitel 16, ADR 0004)."""

    enabled: bool = True
    path: str = "data/history.db"
    """Eigene Datei, getrennt von den Betriebsdaten. Wächst sie zu groß oder
    wird sie beschädigt, bleibt die Steuerung davon unberührt
    (Kapitel 16 §88)."""

    sample_interval_s: float = Field(default=5.0, gt=0)
    """Wie oft geprüft wird, ob ein Punkt fällig ist — **nicht**, wie oft
    geschrieben wird. Ob tatsächlich ein Punkt entsteht, entscheiden Deadband,
    Qualitätswechsel und Herzschlagzeit (Kapitel 16 §8)."""

    heartbeat_s: float = Field(default=300.0, gt=0)
    """Spätestens nach dieser Zeit wird ein Punkt geschrieben, auch wenn sich
    nichts geändert hat.

    Ohne ihn ließe sich später nicht unterscheiden, ob ein Wert konstant war
    oder ob das System aus war. Mit ihm heißt eine längere Lücke eindeutig:
    hier lief nichts.
    """

    compact_interval_s: float = Field(default=300.0, gt=0)
    """Abstand zwischen zwei Verdichtungsläufen."""

    raw_days: int = Field(default=7, gt=0)
    minute_days: int = Field(default=60, gt=0)
    hour_days: int = Field(default=1095, gt=0)
    """Aufbewahrung je Auflösung (Kapitel 16 §9). Die endgültigen Fristen sind
    ausdrücklich vertagt (Kapitel 6 §23); dies sind begründete Vorgaben."""


class Settings(_Strict):
    """Laufzeiteinstellungen.

    Die Betriebsart wird beim Start festgelegt und ist zur Laufzeit nicht
    umschaltbar (Kapitel 15 §96).
    """

    environment: Environment = Environment.SIMULATION
    log_level: str = "INFO"
    server: ServerConfig = Field(default_factory=ServerConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    history: HistoryConfig = Field(default_factory=HistoryConfig)
    stale_sweep_interval_s: float = Field(default=2.0, gt=0)

    @property
    def is_simulated(self) -> bool:
        """Ob reale Hardware angesteuert wird.

        Läuft das System simuliert, kennzeichnet die Oberfläche das dauerhaft
        sichtbar (Kapitel 18 §66).
        """
        return self.environment is not Environment.PRODUCTION
