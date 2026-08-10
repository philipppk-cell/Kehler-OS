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


class TestSchwellen:
    """Schwellenwarnungen.

    Die Richtung ist hier das Entscheidende: Frischwasser warnt nach unten,
    Abwasser nach oben. Eine vertauschte Schwelle schweigt genau dann, wenn
    sie gebraucht wird.
    """

    def tank(self, **kwargs):
        from kehleros.core.registry import Registry
        from tests.conftest import make_entity

        entity = make_entity(TANK, unit="percent")
        reg = Registry()
        reg.register(
            type(entity)(
                id=entity.id,
                name_key=entity.name_key,
                unit="percent",
                **kwargs,
            )
        )
        return reg

    def store(self, registry, percent: float | None, quality=Quality.VALID):
        store = StateStore(registry)
        store.apply(
            TANK,
            StateValue(
                value=percent,
                unit="percent",
                quality=quality,
                source=Source.SIMULATION,
                measured_at=utcnow(),
            ),
            force=True,
        )
        return store

    def test_frischwasser_warnt_unter_der_schwelle(self):
        reg = self.tank(warn_below=20)
        alerts = derive_alerts(self.store(reg, 19.0), reg)

        level = [a for a in alerts if a.type == "level.threshold"]
        assert len(level) == 1
        assert level[0].message_key == "alert.levelLow"
        assert level[0].severity is Severity.WARNING
        assert level[0].params["threshold"] == "20"

    def test_frischwasser_schweigt_auf_der_schwelle(self):
        """Genau 20 % ist noch nicht darunter."""
        reg = self.tank(warn_below=20)
        alerts = derive_alerts(self.store(reg, 20.0), reg)
        assert not [a for a in alerts if a.type == "level.threshold"]

    def test_abwasser_warnt_ueber_der_schwelle(self):
        reg = self.tank(warn_above=80)
        alerts = derive_alerts(self.store(reg, 81.0), reg)

        level = [a for a in alerts if a.type == "level.threshold"]
        assert len(level) == 1
        assert level[0].message_key == "alert.levelHigh"

    def test_abwasser_warnt_nicht_wenn_es_leer_ist(self):
        """Ein leerer Abwassertank ist der Normalfall, keine Meldung."""
        reg = self.tank(warn_above=80)
        alerts = derive_alerts(self.store(reg, 4.0), reg)
        assert not [a for a in alerts if a.type == "level.threshold"]

    def test_ohne_schwelle_keine_warnung(self):
        """Es gibt keine eingebauten Schwellen (Kapitel 18 §98)."""
        reg = self.tank()
        alerts = derive_alerts(self.store(reg, 1.0), reg)
        assert not [a for a in alerts if a.type == "level.threshold"]

    def test_unbekannter_wert_erzeugt_keine_schwellenwarnung(self):
        """Ohne belastbaren Wert lässt sich keine Schwelle prüfen."""
        reg = self.tank(warn_below=20)
        store = StateStore(reg)
        alerts = derive_alerts(store, reg)
        assert not [a for a in alerts if a.type == "level.threshold"]

    def test_veralteter_wert_wird_trotzdem_geprueft(self):
        """Ein Tank, der vor Minuten bei 8 % stand, ist noch immer fast leer.

        Die Unsicherheit meldet die Warnung über den veralteten Wert.
        """
        reg = self.tank(warn_below=20)
        alerts = derive_alerts(self.store(reg, 8.0, Quality.STALE), reg)

        typen = types_of(alerts)
        assert "level.threshold" in typen
        assert "sensor.stale" in typen

    def test_kritische_stufe_ersetzt_die_warnung(self):
        """Unter beiden Schwellen gibt es **eine** Meldung, nicht zwei.

        Zwei Meldungen für denselben Sachverhalt wären Rauschen — und die
        schwerere würde in der Liste neben der leichteren stehen.
        """
        reg = self.tank(warn_below=20, critical_below=10)
        alerts = derive_alerts(self.store(reg, 7.0), reg)

        level = [a for a in alerts if a.type == "level.threshold"]
        assert len(level) == 1
        assert level[0].severity is Severity.CRITICAL
        assert level[0].message_key == "alert.levelCriticalLow"

    def test_zwischen_den_stufen_bleibt_es_bei_der_warnung(self):
        reg = self.tank(warn_below=20, critical_below=10)
        alerts = derive_alerts(self.store(reg, 15.0), reg)

        level = [a for a in alerts if a.type == "level.threshold"]
        assert len(level) == 1
        assert level[0].severity is Severity.WARNING

    def test_abwasser_kritisch(self):
        reg = self.tank(warn_above=80, critical_above=90)
        alerts = derive_alerts(self.store(reg, 94.0), reg)

        level = [a for a in alerts if a.type == "level.threshold"]
        assert len(level) == 1
        assert level[0].severity is Severity.CRITICAL
        assert level[0].message_key == "alert.levelCriticalHigh"

    def test_gerundeter_wert_entscheidet(self):
        """Anzeige und Bewertung dürfen sich nicht widersprechen.

        19,6 % erscheint als „20 %". Würde der Rohwert entscheiden, stünde
        dort eine Warnung mit dem Text „nur noch 20 % — Warnschwelle 20 %".
        """
        reg = self.tank(warn_below=20)
        alerts = derive_alerts(self.store(reg, 19.6), reg)
        assert not [a for a in alerts if a.type == "level.threshold"]

        alerts = derive_alerts(self.store(reg, 19.4), reg)
        level = [a for a in alerts if a.type == "level.threshold"]
        assert len(level) == 1
        assert level[0].params["value"] == "19"
