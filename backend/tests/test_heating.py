"""Die Heizungsanlage.

Verbaut ist eine SCHEER selection 10/17 kW mit HeatMate V4.02. Kehler OS
regelt sie nicht — es liest sie und deutet **eine** Sache: welche Wärmequelle
gerade arbeitet.

Der Schwerpunkt der Tests liegt deshalb auf der Grenze zwischen „keine
Wärmequelle aktiv" und „unbekannt". Die beiden zu verwechseln ist der Fehler,
der hier möglich ist — und der gefährlichere von beiden ist, Ruhe zu
behaupten, wo nichts bekannt ist (Kapitel 18 §38).
"""

from __future__ import annotations

from kehleros.core.heating import HeatingSummary, summarise
from kehleros.domain.enums import Quality
from kehleros.domain.models import Entity, EntityState, StateValue


def _entity(
    entity_id: str, *, configured: bool = True, unverified: bool = False
) -> Entity:
    return Entity(
        id=entity_id,
        name_key=entity_id,
        configured=configured,
        unverified=unverified,
    )


def _state(
    entity_id: str, value: str | None, quality: Quality = Quality.VALID
) -> EntityState:
    state = (
        StateValue.valid(value)
        if quality is Quality.VALID
        else StateValue(value=value, quality=quality)
    )
    return EntityState(entity_id=entity_id, state=state)


def _summary(**werte: str | None) -> HeatingSummary:
    """Baut eine Anlage, bei der genau die genannten Werte bekannt sind."""
    ids = {
        "burner": "heating.burner.state",
        "electric": "heating.electric.state",
        "fault": "heating.system.fault",
    }
    entities = [_entity(entity_id) for entity_id in ids.values()]
    states = {
        ids[name]: _state(ids[name], value)
        for name, value in werte.items()
        if value is not None
    }
    return summarise(states, entities)


class TestWaermequelle:
    def test_brenner_allein(self):
        assert _summary(burner="HEATING", electric="OFF").heat_source == "burner"

    def test_elektro_allein(self):
        assert _summary(burner="OFF", electric="ON").heat_source == "electric"

    def test_beide(self):
        assert _summary(burner="HEATING", electric="ON").heat_source == "both"

    def test_keine(self):
        assert _summary(burner="OFF", electric="OFF").heat_source == "none"

    def test_anforderung_zaehlt_als_aktiv(self):
        # Zwischen Anforderung und Flamme liegen Sekunden. „Nichts aktiv" wäre
        # in dieser Zeit falsch.
        assert _summary(burner="DEMAND", electric="OFF").heat_source == "burner"

    def test_nachlauf_zaehlt_nicht_als_aktiv(self):
        # Im Nachlauf wird Restwärme abgeführt, der Brenner heizt nicht mehr.
        assert _summary(burner="POSTRUN", electric="OFF").heat_source == "none"


class TestUnbekannt:
    """„Unbekannt" ist nicht „nichts läuft"."""

    def test_ohne_werte_keine_aussage(self):
        assert _summary().heat_source is None

    def test_halbe_kenntnis_ergibt_keine_aussage(self):
        # Der Brenner heizt — aber ob die Elektroheizung mitläuft, ist offen.
        # „Brenner" wäre dann keine unvollständige, sondern eine falsche
        # Aussage.
        assert _summary(burner="HEATING").heat_source is None
        assert _summary(electric="ON").heat_source is None

    def test_nicht_konfiguriert_ergibt_keine_aussage(self):
        entities = [
            _entity("heating.burner.state", configured=False, unverified=True),
            _entity("heating.electric.state", configured=False, unverified=True),
        ]
        summary = summarise({}, entities)
        assert summary.heat_source is None
        assert summary.linked is False
        assert summary.unverified == 2

    def test_veralteter_wert_gilt_weiter(self):
        # STALE heißt „alt, aber echt" — die Aussage bleibt, wie überall sonst.
        entities = [_entity("heating.burner.state"), _entity("heating.electric.state")]
        states = {
            "heating.burner.state": _state(
                "heating.burner.state", "HEATING", Quality.STALE
            ),
            "heating.electric.state": _state("heating.electric.state", "OFF"),
        }
        assert summarise(states, entities).heat_source == "burner"


class TestStoerung:
    def test_ohne_meldung_keine_entwarnung(self):
        """Schweigen ist kein „alles in Ordnung"."""
        assert _summary().fault is None

    def test_gemeldete_stoerung(self):
        assert _summary(fault="FAULT").fault is True

    def test_gemeldeter_normalzustand(self):
        assert _summary(fault="OK").fault is False


class TestAnbindung:
    def test_ohne_angebundene_funktion_gilt_die_anlage_als_unverbunden(self):
        """Solange die Registerliste fehlt, ist nichts angebunden (Punkt G1).

        Die Oberfläche braucht diese Auskunft, um die Anlage als Struktur zu
        zeigen und die ausstehende Anbindung zu erklären — statt zwanzig
        Zeilen „unbekannt" ohne Grund.
        """
        entities = [
            _entity("heating.system.state", configured=False, unverified=True),
            _entity("heating.burner.state", configured=False, unverified=True),
        ]
        summary = summarise({}, entities)
        assert summary.linked is False
        assert summary.unverified == 2

    def test_eine_angebundene_funktion_genuegt(self):
        entities = [
            _entity("heating.system.state"),
            _entity("heating.burner.state", configured=False, unverified=True),
        ]
        assert summarise({}, entities).linked is True

    def test_fremde_entities_bleiben_unberuecksichtigt(self):
        # Die Klimaanlage ist ein eigenes System und darf die Heizung nicht
        # als angebunden erscheinen lassen.
        entities = [
            _entity("climate.cooling.state"),
            _entity("heating.system.state", configured=False, unverified=True),
        ]
        summary = summarise({}, entities)
        assert summary.linked is False
        assert summary.unverified == 1
