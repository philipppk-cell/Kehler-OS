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


SOC = "energy.battery.soc"


@pytest.fixture
def registry() -> list[Entity]:
    return [
        entity(POWER),
        entity(SHORE, unit=None),
        entity(SOC, unit="percent", capacity_ah=900, nominal_voltage=24),
    ]


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


class TestRestlaufzeit:
    """Die Hochrechnung — und vor allem, wann es sie nicht gibt."""

    def _states(self, soc=None, power=None):
        out = {}
        if soc is not None:
            out[SOC] = state(SOC, soc, unit="percent")
        if power is not None:
            out[POWER] = state(POWER, power)
        return out

    def test_energieinhalt_aus_kapazitaet_und_nennspannung(self, registry):
        s = summarise(self._states(soc=100.0), registry)
        assert s.capacity_wh == pytest.approx(21600.0)
        assert s.remaining_wh == pytest.approx(21600.0)

    def test_hochrechnung_beim_entladen(self, registry):
        # 50 % von 21,6 kWh sind 10,8 kWh; bei 900 W Entnahme also 12 Stunden.
        s = summarise(self._states(soc=50.0, power=-900.0), registry)
        assert s.runtime_h == pytest.approx(12.0)
        assert s.runtime_capped is False

    def test_keine_hochrechnung_beim_laden(self, registry):
        """Beim Laden läuft nichts ab."""
        s = summarise(self._states(soc=50.0, power=900.0), registry)
        assert s.runtime_h is None

    def test_keine_hochrechnung_bei_ruhender_batterie(self, registry):
        """Ohne nennenswerte Entnahme ergäbe die Rechnung eine Scheinzahl."""
        s = summarise(self._states(soc=50.0, power=-5.0), registry)
        assert s.runtime_h is None

    def test_keine_hochrechnung_ohne_ladezustand(self, registry):
        s = summarise(self._states(power=-900.0), registry)
        assert s.remaining_wh is None
        assert s.runtime_h is None

    def test_sehr_lange_laufzeit_wird_gedeckelt(self, registry):
        """„212 Stunden" spiegelt eine Genauigkeit vor, die es nicht gibt."""
        s = summarise(self._states(soc=100.0, power=-100.0), registry)
        assert s.runtime_capped is True
        assert s.runtime_h == pytest.approx(48.0)

    def test_ohne_kapazitaet_kein_energieinhalt(self):
        registry = [entity(SOC, unit="percent"), entity(POWER)]
        s = summarise(
            {SOC: state(SOC, 50.0, unit="percent"), POWER: state(POWER, -900.0)},
            registry,
        )
        assert s.capacity_wh is None
        assert s.runtime_h is None
