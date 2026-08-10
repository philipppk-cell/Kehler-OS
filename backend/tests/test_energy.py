"""Die Energiezusammenfassung.

Schwerpunkt: wann das System **keine** Aussage über die Laderichtung trifft.
„Ruht" sieht harmlos aus und wäre bei unbekanntem Messwert eine Lüge.
"""

from __future__ import annotations

import pytest

from kehleros.core.energy import IDLE_WATT, summarise
from kehleros.domain.enums import Quality, Source
from kehleros.domain.models import Entity, EntityState, StateValue

POWER = "energy.battery.power"
SHORE = "energy.shore.connected"


def entity(entity_id: str, unit: str | None = "W", **kwargs) -> Entity:
    return Entity(id=entity_id, name_key=entity_id, unit=unit, **kwargs)


def state(entity_id: str, value, quality=Quality.VALID, unit="W") -> EntityState:
    return EntityState(
        entity_id=entity_id,
        state=StateValue(
            value=value, unit=unit, quality=quality, source=Source.SIMULATION
        ),
    )


@pytest.fixture
def registry() -> list[Entity]:
    return [entity(POWER), entity(SHORE, unit=None)]


class TestLaderichtung:
    def test_laden_ist_positiv(self, registry):
        s = summarise({POWER: state(POWER, 480.0)}, registry)
        assert s.direction == "charging"

    def test_entladen_ist_negativ(self, registry):
        s = summarise({POWER: state(POWER, -310.0)}, registry)
        assert s.direction == "discharging"

    def test_kleine_leistung_gilt_als_ruhend(self, registry):
        """Ohne Totzone flackert die Anzeige, sobald der Strom um null pendelt."""
        s = summarise({POWER: state(POWER, IDLE_WATT - 1)}, registry)
        assert s.direction == "idle"

        s = summarise({POWER: state(POWER, -(IDLE_WATT - 1))}, registry)
        assert s.direction == "idle"

    def test_unbekannt_ist_keine_richtung(self, registry):
        """Der wichtigste Fall: „ruht" wäre hier eine Lüge."""
        s = summarise({POWER: state(POWER, None, Quality.UNKNOWN)}, registry)
        assert s.direction is None

    def test_ohne_zustand_keine_richtung(self, registry):
        s = summarise({}, registry)
        assert s.direction is None

    def test_sensorfehler_ist_keine_richtung(self, registry):
        s = summarise({POWER: state(POWER, None, Quality.ERROR)}, registry)
        assert s.direction is None

    def test_veralteter_wert_ergibt_weiterhin_eine_richtung(self, registry):
        """Ein alter, echter Wert taugt für eine Richtungsaussage.

        Die Unsicherheit trägt die Qualität, die mitgeliefert wird.
        """
        s = summarise({POWER: state(POWER, -400.0, Quality.STALE)}, registry)
        assert s.direction == "discharging"
        assert s.battery_power.quality is Quality.STALE


class TestLandstrom:
    def test_verbunden(self, registry):
        s = summarise({SHORE: state(SHORE, "CLOSED", unit=None)}, registry)
        assert s.shore_connected is True

    def test_getrennt(self, registry):
        s = summarise({SHORE: state(SHORE, "OPEN", unit=None)}, registry)
        assert s.shore_connected is False

    def test_unbekannt_ist_nicht_getrennt(self, registry):
        """Drei Antworten, nicht zwei: ja, nein und „weiß nicht"."""
        s = summarise({SHORE: state(SHORE, None, Quality.UNKNOWN, unit=None)}, registry)
        assert s.shore_connected is None

        s = summarise({}, registry)
        assert s.shore_connected is None


def test_nicht_konfigurierte_entity_liefert_nichts():
    registry = [entity(POWER, configured=False)]
    s = summarise({POWER: state(POWER, 500.0)}, registry)

    assert s.battery_power.value is None
    assert s.direction is None
