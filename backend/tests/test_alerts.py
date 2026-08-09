"""Die Ableitung von Warnungen.

Schwerpunkt: der Unterschied zwischen „noch nichts gemeldet" und „hat
gemeldet und ist verstummt". Beide sind ``UNKNOWN`` — nur der zweite Fall ist
eine Störung.
"""

from __future__ import annotations

from datetime import timedelta

from kehleros.core.alerts import derive_alerts
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import Quality, Severity, Source
from kehleros.domain.models import StateValue, utcnow

TANK = "water.tank.fresh"


def types_of(alerts) -> set[str]:
    return {alert.type for alert in alerts}


class TestUnbekannt:
    def test_start_erzeugt_keine_warnungsflut(
        self, state: StateStore, registry: Registry
    ):
        """Nach dem Start ist alles unbekannt — das ist kein Fehler.

        Eine Warnung je Entity wäre eine Wand aus Meldungen ohne Aussage
        (Kapitel 13 §55).
        """
        alerts = derive_alerts(state, registry)
        assert "sensor.lost" not in types_of(alerts)

    def test_verstummter_sensor_wird_gemeldet(
        self, state: StateStore, registry: Registry
    ):
        """Ein Wert, der da war und weggefallen ist, ist eine Störung."""
        state.apply(
            TANK,
            StateValue(
                value=None,
                unit="percent",
                quality=Quality.UNKNOWN,
                source=Source.SIMULATION,
                measured_at=utcnow() - timedelta(minutes=5),
            ),
            force=True,
        )

        alerts = derive_alerts(state, registry)
        lost = [a for a in alerts if a.type == "sensor.lost"]

        assert len(lost) == 1
        assert lost[0].entity_id == TANK
        assert lost[0].severity is Severity.WARNING

    def test_wieder_gelieferter_wert_beendet_die_warnung(
        self, state: StateStore, registry: Registry
    ):
        state.apply(
            TANK,
            StateValue(
                value=None,
                unit="percent",
                quality=Quality.UNKNOWN,
                source=Source.SIMULATION,
                measured_at=utcnow() - timedelta(minutes=5),
            ),
            force=True,
        )
        assert "sensor.lost" in types_of(derive_alerts(state, registry))

        state.apply(
            TANK,
            StateValue.valid(61.0, unit="percent", source=Source.SIMULATION),
            force=True,
        )
        assert "sensor.lost" not in types_of(derive_alerts(state, registry))


class TestNichtKonfiguriert:
    def test_ist_hinweis_keine_stoerung(self, state: StateStore, registry: Registry):
        """Fehlende Hardwarezuordnung ist ein offener Punkt in der
        Einrichtung, kein Betriebsfehler."""
        alerts = [
            a
            for a in derive_alerts(state, registry)
            if a.type == "system.not_configured"
        ]

        assert alerts, "Die nicht konfigurierte Markise sollte auftauchen"
        assert all(a.severity is Severity.INFO for a in alerts)
