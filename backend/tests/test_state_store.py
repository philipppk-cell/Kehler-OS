"""Zustandsverwaltung.

Der Schwerpunkt liegt bewusst auf den Fehlerzuständen. Kapitel 18 §71 verlangt
ausdrücklich, ``UNKNOWN``, ``OFFLINE``, ``INVALID`` und ``ERROR`` gezielt zu
prüfen — nicht nur den Normalfall.
"""

from __future__ import annotations

from datetime import timedelta

from kehleros.core.state_store import StateStore
from kehleros.domain.enums import LinkState, Quality, Source
from kehleros.domain.models import StateValue, utcnow


class TestUnbekannteWerte:
    """Die wichtigste Zusicherung des Projekts."""

    def test_unbekannt_traegt_niemals_einen_wert(self):
        assert StateValue.unknown().value is None

    def test_qualitaet_ungleich_valid_verwirft_den_wert(self):
        # Selbst wenn jemand versucht, einen Wert mitzugeben: Ein nicht
        # belastbarer Zustand darf keine Zahl vortäuschen (Kapitel 18 §38).
        for quality in (Quality.UNKNOWN, Quality.STALE, Quality.INVALID, Quality.ERROR):
            value = StateValue(value=42, quality=quality)
            assert value.value is None, f"{quality} hat einen Wert behalten"

    def test_startzustand_ist_unbekannt(self, state: StateStore):
        # Nach einem Neustart wird nichts aus der Datenbank übernommen
        # (Kapitel 6 §44, Kapitel 12 §66).
        for entity_state in state:
            assert entity_state.state.quality is Quality.UNKNOWN
            assert entity_state.state.value is None

    def test_nicht_konfiguriert_ist_erkennbar(self, state: StateStore):
        awning = state.require("vehicle.awning.main")
        assert awning.link is LinkState.NOT_CONFIGURED


class TestAenderungserkennung:
    def test_gleicher_wert_erzeugt_kein_delta(self, state: StateStore):
        first = state.apply("water.tank.fresh", StateValue.valid(64.0, unit="percent"))
        second = state.apply("water.tank.fresh", StateValue.valid(64.0, unit="percent"))
        assert first is not None
        assert second is None, "Unveränderter Wert darf kein Delta erzeugen"

    def test_deadband_unterdrueckt_zappeln(self, state: StateStore):
        # water.tank.fresh hat ein Deadband von 0.5
        state.apply("water.tank.fresh", StateValue.valid(64.0))
        winzig = state.apply("water.tank.fresh", StateValue.valid(64.2))
        deutlich = state.apply("water.tank.fresh", StateValue.valid(65.0))
        assert winzig is None
        assert deutlich is not None

    def test_qualitaetswechsel_zaehlt_immer_als_aenderung(self, state: StateStore):
        state.apply("water.tank.fresh", StateValue.valid(64.0))
        delta = state.apply("water.tank.fresh", StateValue.error())
        assert delta is not None
        assert delta.entity_state.state.quality is Quality.ERROR

    def test_sequenznummer_steigt_je_entity(self, state: StateStore):
        a = state.apply("water.tank.fresh", StateValue.valid(60.0))
        b = state.apply("water.tank.fresh", StateValue.valid(61.0))
        assert b.seq > a.seq


class TestAlterung:
    """Ein Wert altert sichtbar, statt still falsch zu werden."""

    def test_valid_wird_nach_intervall_stale(self, state: StateStore):
        alt = utcnow() - timedelta(seconds=5)
        state.apply(
            "water.tank.fresh",
            StateValue.valid(64.0, measured_at=alt),
        )
        deltas = state.sweep_stale()
        assert len(deltas) == 1
        assert deltas[0].entity_state.state.quality is Quality.STALE

    def test_stale_wird_zu_unknown(self, state: StateStore):
        alt = utcnow() - timedelta(seconds=10)
        state.apply("water.tank.fresh", StateValue.valid(64.0, measured_at=alt))
        state.sweep_stale()
        deltas = state.sweep_stale()
        assert deltas[0].entity_state.state.quality is Quality.UNKNOWN

    def test_frischer_wert_altert_nicht(self, state: StateStore):
        state.apply("water.tank.fresh", StateValue.valid(64.0))
        assert state.sweep_stale() == []

    def test_ohne_erwartetes_intervall_keine_alterung(self, state: StateStore):
        # light.interior.living hat kein expected_interval_s
        alt = utcnow() - timedelta(hours=1)
        state.apply("light.interior.living", StateValue.valid("ON", measured_at=alt))
        assert state.sweep_stale() == []


class TestQuellenausfall:
    def test_ausfall_setzt_auf_unbekannt_nicht_auf_null(self, state: StateStore):
        state.apply("water.tank.fresh", StateValue.valid(64.0, source=Source.PLC))
        state.mark_source_offline(["water.tank.fresh"])

        current = state.require("water.tank.fresh")
        assert current.state.quality is Quality.UNKNOWN
        assert current.state.value is None, "Ausfall darf nicht als 0 erscheinen"
        assert current.link is LinkState.OFFLINE


class TestVerteilung:
    async def test_abonnent_erhaelt_aenderungen(self, state: StateStore):
        subscription = state.subscribe()
        state.apply("water.tank.fresh", StateValue.valid(64.0))
        delta = await subscription.get()
        assert delta.entity_id == "water.tank.fresh"

    def test_langsamer_abonnent_wird_zur_neusynchronisation_markiert(
        self, state: StateStore
    ):
        # Statt den Speicher wachsen zu lassen, wird der Client zur
        # Neusynchronisation aufgefordert (Kapitel 17 §97).
        subscription = state.subscribe()
        for i in range(400):
            state.apply("water.tank.fresh", StateValue.valid(float(i)))
        assert subscription.needs_resync

    def test_abmeldung_beendet_zustellung(self, state: StateStore):
        subscription = state.subscribe()
        state.unsubscribe(subscription)
        state.apply("water.tank.fresh", StateValue.valid(64.0))
        assert state.subscriber_count == 0
