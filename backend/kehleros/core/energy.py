"""Den Energiefluss zusammenfassen.

Die Messwerte allein beantworten die Alltagsfrage nicht. „−340 W" ist eine
Zahl; „die Batterie entlädt sich" ist eine Aussage. Diese Übersetzung steht
hier und nicht in der Oberfläche, weil sie zwei Entscheidungen enthält, die
Geschäftslogik sind:

1. **Ab wann gilt die Batterie als „ruhend"?** Ein Strom schwankt immer ein
   wenig. Ohne eine Totzone wechselt die Anzeige im Sekundentakt zwischen
   „lädt" und „entlädt" — und wird damit unbrauchbar. Die Grenze ist eine
   Festlegung, keine Messung, und sie gehört an eine Stelle.

2. **Wann gibt es gar keine Aussage?** Ohne belastbaren Messwert wird nicht
   geraten. Die Richtung bleibt dann `None` — und die Oberfläche zeigt
   „unbekannt" statt „ruhend" (Kapitel 18 §38). Das ist der wichtigere der
   beiden Punkte: „ruhend" sieht harmlos aus und wäre hier eine Lüge.

**Kehler OS regelt nichts.** Victron bleibt Energiemanagement und
Schutzinstanz (Kapitel 12 §33). Dieses Modul liest und deutet, mehr nicht.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Literal

from ..domain.enums import Quality
from ..domain.models import Entity, EntityState

BATTERY_SOC = "energy.battery.soc"
BATTERY_VOLTAGE = "energy.battery.voltage"
BATTERY_CURRENT = "energy.battery.current"
BATTERY_POWER = "energy.battery.power"
SOLAR_POWER = "energy.solar.power"
CONSUMPTION = "energy.consumption.power"
SHORE_CONNECTED = "energy.shore.connected"
SHORE_POWER = "energy.shore.power"

_USABLE = (Quality.VALID, Quality.STALE)

IDLE_WATT = 25.0
"""Unterhalb dieser Leistung gilt die Batterie als ruhend.

Eine Festlegung, keine Messung: Ohne sie flackert die Anzeige zwischen
„lädt" und „entlädt", sobald der Strom um null pendelt. 25 W entsprechen bei
24 V etwa einem Ampere — deutlich unter jedem echten Lade- oder Entladefall,
aber über dem Rauschen.
"""

Direction = Literal["charging", "discharging", "idle"]


@dataclass(frozen=True, slots=True)
class Reading:
    """Ein Messwert mit seiner Belastbarkeit."""

    value: float | None
    quality: Quality

    @property
    def usable(self) -> bool:
        return self.quality in _USABLE and self.value is not None


@dataclass(frozen=True, slots=True)
class EnergySummary:
    soc: Reading
    voltage: Reading
    current: Reading
    battery_power: Reading
    solar_power: Reading
    consumption: Reading
    shore_power: Reading

    shore_connected: bool | None
    """``None`` heißt unbekannt — ausdrücklich nicht „nicht verbunden"."""

    direction: Direction | None
    """Richtung des Batterieflusses. ``None``, wenn sie nicht belegbar ist."""


def summarise(
    states: Mapping[str, EntityState],
    entities: Iterable[Entity],
) -> EnergySummary:
    by_id = {entity.id: entity for entity in entities}

    def read(entity_id: str) -> Reading:
        if entity_id not in by_id or not by_id[entity_id].configured:
            return Reading(None, Quality.UNKNOWN)
        state = states.get(entity_id)
        if state is None:
            return Reading(None, Quality.UNKNOWN)
        value = state.state.value
        number = float(value) if isinstance(value, (int, float)) else None
        return Reading(number, state.state.quality)

    battery_power = read(BATTERY_POWER)

    return EnergySummary(
        soc=read(BATTERY_SOC),
        voltage=read(BATTERY_VOLTAGE),
        current=read(BATTERY_CURRENT),
        battery_power=battery_power,
        solar_power=read(SOLAR_POWER),
        consumption=read(CONSUMPTION),
        shore_power=read(SHORE_POWER),
        shore_connected=_contact(states.get(SHORE_CONNECTED)),
        direction=_direction(battery_power),
    )


def _direction(power: Reading) -> Direction | None:
    """Übersetzt die Batterieleistung in eine Aussage.

    Vorzeichenkonvention: **positiv = laden**. Sie steht in der
    Fahrzeugkonfiguration und ist damit eine Eigenschaft der Anlage, keine
    Annahme dieses Moduls.
    """
    if not power.usable:
        return None
    if power.value > IDLE_WATT:
        return "charging"
    if power.value < -IDLE_WATT:
        return "discharging"
    return "idle"


def _contact(state: EntityState | None) -> bool | None:
    """Ein Kontakt kennt drei Antworten: ja, nein und „weiß nicht"."""
    if state is None or state.state.quality not in _USABLE:
        return None
    value = state.state.value
    if value == "CLOSED":
        return True
    if value == "OPEN":
        return False
    return None
