"""Wasserstände zusammenfassen.

Das Fahrzeug hat **zwei** Frischwassertanks. Für den Alltag zählt aber die
Frage „wie viel Wasser habe ich noch" — und deren Antwort ist eine Summe über
beide.

Diese Summe steht hier und nicht in der Oberfläche, weil sie zwei
Entscheidungen enthält, die Geschäftslogik sind:

1. **Prozente dürfen nicht addiert werden.** 100 % in einem 450-l-Tank und
   0 % in einem 550-l-Tank sind nicht „50 % Frischwasser", sondern 45 %.
   Gerechnet wird über Liter.

2. **Eine Summe ist nur so gut wie ihr schlechtester Summand.** Meldet einer
   der Tanks keinen belastbaren Wert, gibt es *keinen* Gesamtstand — auch
   nicht den halben. Alles andere wäre eine Zahl, die belastbarer aussieht,
   als sie ist (Kapitel 18 §38).

Die Umrechnung Prozent → Liter setzt einen linearen Tank voraus. Solange
keine Stützpunkte für eine Kalibrierkurve vorliegen (offener Punkt C2), ist
die Literangabe eine Umrechnung des Füllstands und keine Messung. Die
Oberfläche weist darauf hin.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from ..domain.enums import Quality
from ..domain.models import Entity, EntityState

FRESH_PREFIX = "water.tank.fresh"
WASTE_IDS = ("water.tank.grey", "water.tank.black")

# Von gut nach schlecht. Die Reihenfolge ist die Rangfolge, mit der die
# Qualität einer Summe bestimmt wird.
_RANK = {
    Quality.VALID: 0,
    Quality.STALE: 1,
    Quality.INVALID: 2,
    Quality.ERROR: 3,
    Quality.UNKNOWN: 4,
}

_USABLE = (Quality.VALID, Quality.STALE)


@dataclass(frozen=True, slots=True)
class TankView:
    """Ein einzelner Tank, wie die Oberfläche ihn braucht."""

    entity_id: str
    name_key: str
    quality: Quality
    percent: float | None
    capacity_l: float | None
    litres: float | None
    """Belegter Inhalt. ``None``, wenn Füllstand oder Kapazität fehlen."""

    warn_below: float | None = None
    warn_above: float | None = None

    @property
    def free_l(self) -> float | None:
        if self.capacity_l is None or self.litres is None:
            return None
        return max(0.0, self.capacity_l - self.litres)

    @property
    def breached(self) -> bool:
        """Ob eine konfigurierte Schwelle überschritten ist.

        Die Oberfläche färbt danach den Balken. Ohne Schwelle bleibt er
        neutral — eine Farbe ohne Bedeutung wäre Dekoration.
        """
        if self.percent is None:
            return False
        if self.warn_below is not None and self.percent < self.warn_below:
            return True
        return self.warn_above is not None and self.percent > self.warn_above


@dataclass(frozen=True, slots=True)
class TankGroup:
    """Mehrere Tanks und ihre Summe."""

    tanks: tuple[TankView, ...]
    quality: Quality
    capacity_l: float | None
    litres: float | None
    percent: float | None

    warn_below: float | None = None
    """Schwelle für die Gesamtmenge.

    Sie wird **nur** übernommen, wenn alle Tanks der Gruppe dieselbe Schwelle
    tragen. Bei unterschiedlichen Schwellen gibt es für die Summe keine —
    welche davon für das Ganze gälte, ist eine Frage, die die Konfiguration
    nicht beantwortet, und die Software beantwortet sie nicht an ihrer Stelle.
    """

    @property
    def free_l(self) -> float | None:
        if self.capacity_l is None or self.litres is None:
            return None
        return max(0.0, self.capacity_l - self.litres)

    @property
    def breached(self) -> bool:
        if self.percent is None or self.warn_below is None:
            return False
        return self.percent < self.warn_below


@dataclass(frozen=True, slots=True)
class WaterSummary:
    fresh: TankGroup
    waste: tuple[TankView, ...]


def summarise(
    states: Mapping[str, EntityState],
    entities: Iterable[Entity],
) -> WaterSummary:
    """Fasst die Wassertanks zusammen.

    ``entities`` ist alles, was sich über Entities iterieren lässt — die
    ``Registry`` genauso wie eine einfache Liste im Test.
    """
    by_id = {entity.id: entity for entity in entities}

    fresh = [
        _tank(entity, states.get(entity.id))
        for entity in by_id.values()
        if entity.id.startswith(FRESH_PREFIX) and entity.configured
    ]
    # Größter Tank zuerst — sonst hängt die Reihenfolge an der Konfiguration.
    fresh.sort(key=lambda tank: -(tank.capacity_l or 0))

    waste = [
        _tank(by_id[entity_id], states.get(entity_id))
        for entity_id in WASTE_IDS
        if entity_id in by_id and by_id[entity_id].configured
    ]

    return WaterSummary(fresh=_group(fresh), waste=tuple(waste))


def _tank(entity: Entity, state: EntityState | None) -> TankView:
    quality = state.state.quality if state else Quality.UNKNOWN
    value = state.state.value if state else None
    percent = float(value) if isinstance(value, (int, float)) else None

    litres: float | None = None
    if percent is not None and entity.capacity_l is not None:
        litres = entity.capacity_l * percent / 100.0

    return TankView(
        entity_id=entity.id,
        name_key=entity.name_key,
        quality=quality,
        percent=percent,
        capacity_l=entity.capacity_l,
        litres=litres,
        warn_below=entity.warn_below,
        warn_above=entity.warn_above,
    )


def _shared_warn_below(tanks: tuple[TankView, ...]) -> float | None:
    """Die gemeinsame Schwelle — oder keine."""
    thresholds = {tank.warn_below for tank in tanks}
    if len(thresholds) == 1:
        return next(iter(thresholds))
    return None


def _group(tanks: list[TankView]) -> TankGroup:
    ordered = tuple(tanks)
    if not ordered:
        return TankGroup((), Quality.UNKNOWN, None, None, None)

    warn_below = _shared_warn_below(ordered)

    # Schlechteste Qualität aller Summanden bestimmt die der Summe.
    quality = max((tank.quality for tank in ordered), key=lambda q: _RANK[q])

    usable = all(
        tank.quality in _USABLE and tank.litres is not None and tank.capacity_l
        for tank in ordered
    )
    if not usable:
        # Kein Teilergebnis. Eine Summe über die „guten" Tanks wäre keine
        # Gesamtmenge, sondern eine Zahl ohne Bezug.
        capacity = sum(t.capacity_l for t in ordered if t.capacity_l) or None
        return TankGroup(ordered, quality, capacity, None, None, warn_below)

    capacity = sum(tank.capacity_l or 0.0 for tank in ordered)
    litres = sum(tank.litres or 0.0 for tank in ordered)
    percent = litres / capacity * 100.0 if capacity else None

    return TankGroup(ordered, quality, capacity, litres, percent, warn_below)
