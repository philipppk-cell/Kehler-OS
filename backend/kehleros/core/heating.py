"""Die Heizungsanlage zusammenfassen.

Verbaut ist eine **SCHEER selection 10/17 kW** mit der Steuerung **SCHEER
HeatMate V4.02**. Sie ist Heizung und Warmwasserbereitung zugleich und hat
zwei Wärmequellen: den Brenner und eine Elektroheizung.

**Kehler OS regelt hier nichts.** Die HeatMate bleibt Regler und
Schutzeinrichtung — Temperaturbegrenzer, Brennersteuerung und Abschaltungen
gehören ihr (Kapitel 12 §33/§67, Kapitel 18 §29). Dieses Modul liest und
deutet, mehr nicht. Es gibt keinen Zustand, den Kehler OS erzeugt; es gibt
nur Zustände, die es weitergibt.

Gedeutet wird genau eine Sache, und die ist die Alltagsfrage der Seite:
**Welche Wärmequelle arbeitet gerade?** Aus „Brenner: HEATING" und
„Elektro: ON" folgt „beide". Diese Verknüpfung ist Geschäftslogik und gehört
deshalb hierher und nicht in die Oberfläche (Kapitel 18 §6) — sonst rechnet
sie jede Ansicht neu und irgendwann eine davon anders.

Alles andere wird durchgereicht. Insbesondere wird **nicht** aus der
Temperatur geschlossen, ob der Brenner läuft: Das weiß die HeatMate, und wenn
sie es nicht meldet, weiß es niemand.

Die Anlage führt genau **eine** Temperatur — Kessel und Warmwasser werden
nicht getrennt geführt (BESTÄTIGT 2026-08-10).

── Stand der Anbindung ──────────────────────────────────────────────────────

Die Modbus-Registerliste der HeatMate liegt nicht vor (Punkt G1). Sämtliche
Entities sind deshalb `unverified` und ohne Hardwarezuordnung; dieses Modul
liefert derzeit durchgehend „unbekannt". Das ist der richtige Zustand und
kein Mangel — die Struktur steht, die Werte kommen mit der Registerliste.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Literal

from ..domain.enums import Quality
from ..domain.models import Entity, EntityState

SYSTEM_STATE = "heating.system.state"
SYSTEM_FAULT = "heating.system.fault"
BURNER_STATE = "heating.burner.state"
ELECTRIC_STATE = "heating.electric.state"

_USABLE = (Quality.VALID, Quality.STALE)

BURNER_ACTIVE = frozenset({"HEATING", "DEMAND"})
"""Brennerphasen, in denen Wärme angefordert wird oder entsteht.

`POSTRUN` gehört nicht dazu: Im Nachlauf wird die Restwärme abgeführt, der
Brenner heizt nicht mehr. Ihn mitzuzählen hieße, „die Anlage heizt" zu
sagen, während sie gerade ausgeht.

Die Namen sind das interne Vokabular von Kehler OS. Welcher Registerwert der
HeatMate auf welchen Namen abgebildet wird, entscheidet der Adapter, sobald
die Registerliste vorliegt — nicht dieses Modul.
"""

HeatSource = Literal["burner", "electric", "both", "none"]


@dataclass(frozen=True, slots=True)
class Reading:
    """Ein Wert mit seiner Belastbarkeit."""

    value: float | str | None
    quality: Quality

    @property
    def usable(self) -> bool:
        return self.quality in _USABLE and self.value is not None


@dataclass(frozen=True, slots=True)
class HeatingSummary:
    heat_source: HeatSource | None
    """Welche Wärmequelle arbeitet.

    ``None`` heißt unbekannt und ausdrücklich **nicht** ``"none"``. Der
    Unterschied ist der ganze Punkt: „keine Wärmequelle aktiv" ist eine
    Aussage über die Anlage, „unbekannt" eine über unser Wissen. Solange die
    Registerliste fehlt, ist es immer ``None``.
    """

    fault: bool | None
    """Ob die Anlage eine Störung meldet. ``None``, solange sie nichts meldet."""

    linked: bool
    """Ob überhaupt eine Funktion der Anlage angebunden ist.

    Ist das ``False``, zeigt die Oberfläche die Anlage als Struktur und sagt
    dazu, dass die Anbindung noch aussteht — statt zwanzig Zeilen „unbekannt"
    ohne Erklärung.
    """

    unverified: int
    """Wie viele Funktionen noch auf ihre Bestätigung warten."""


def summarise(
    states: Mapping[str, EntityState],
    entities: Iterable[Entity],
) -> HeatingSummary:
    by_id = {entity.id: entity for entity in entities if entity.id.startswith("heating.")}

    def read(entity_id: str) -> Reading:
        entity = by_id.get(entity_id)
        if entity is None or not entity.configured:
            return Reading(None, Quality.UNKNOWN)
        state = states.get(entity_id)
        if state is None:
            return Reading(None, Quality.UNKNOWN)
        return Reading(state.state.value, state.state.quality)

    return HeatingSummary(
        heat_source=_heat_source(read(BURNER_STATE), read(ELECTRIC_STATE)),
        fault=_fault(read(SYSTEM_FAULT)),
        linked=any(entity.configured for entity in by_id.values()),
        unverified=sum(1 for entity in by_id.values() if entity.unverified),
    )


def _heat_source(burner: Reading, electric: Reading) -> HeatSource | None:
    """Welche Wärmequelle gerade arbeitet.

    Die Aussage entsteht nur, wenn **beide** Quellen bekannt sind. Bei nur
    einer bekannten Quelle ließe sich zwar sagen „der Brenner heizt", aber
    nicht, ob die Elektroheizung mitläuft — und „Brenner" statt „beide" wäre
    eine falsche Aussage, keine unvollständige.
    """
    if not burner.usable or not electric.usable:
        return None

    burning = str(burner.value) in BURNER_ACTIVE
    electrical = str(electric.value) == "ON"

    if burning and electrical:
        return "both"
    if burning:
        return "burner"
    if electrical:
        return "electric"
    return "none"


def _fault(state: Reading) -> bool | None:
    """Ob eine Störung anliegt — mit „weiß nicht" als dritter Antwort.

    Eine fehlende Meldung ist keine Entwarnung. Solange die Anlage nichts
    sagt, bleibt es ``None``; „keine Störung" wäre an dieser Stelle die
    gefährlichere der beiden Behauptungen (Kapitel 18 §38).
    """
    if not state.usable:
        return None
    return str(state.value) not in ("OK", "NONE", "OFF")
