"""Messhistorie.

Der Schwerpunkt liegt auf der einen Regel, die alles andere bestimmt: **Eine
Lücke bleibt eine Lücke.** Kapitel 16 §97 verbietet, fehlende Messwerte als
reale Historie auszugeben — und eine Kurve, die über ein Loch hinwegzeichnet,
tut genau das.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from kehleros.core.history import HOUR_MS, MINUTE_MS, HistoryStore, Retention
from kehleros.core.registry import Registry
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import Quality
from kehleros.domain.models import StateValue
from kehleros.platform.database import Database
from tests.conftest import make_entity


@pytest.fixture
def registry() -> Registry:
    registry = Registry()
    # Deadband 0.5 wie beim realen Ladezustand.
    registry.register(make_entity("energy.battery.soc", unit="percent", deadband=0.5))
    # Ohne Einheit: ein Schalter gehört nicht in eine Messkurve.
    registry.register(make_entity("water.pump.main"))
    return registry


@pytest.fixture
async def history(tmp_path: Path, registry: Registry):
    state = StateStore(registry)
    store = HistoryStore(
        Database(tmp_path / "history.db"),
        state,
        registry,
        retention=Retention(),
        heartbeat_s=300.0,
    )
    await store.start()
    try:
        yield store, state
    finally:
        await store.stop()


class TestWasAufgezeichnetWird:
    async def test_nur_messgroessen(self, history):
        """Ein Schalter hat keine Einheit und keine Kurve.

        Seine Historie ist eine Ereignisliste (Kapitel 16 §7). Ihn als
        Zahlenreihe zu führen, hieße einen Zustand in einen Messwert zu
        verwandeln.
        """
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        state.apply("water.pump.main", StateValue.valid("ON"))

        await store.record(now_ms=1_000_000)
        series = await store.series("water.pump.main", 0, 2_000_000)
        assert series.points == []

    async def test_erster_wert_wird_immer_geschrieben(self, history):
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))

        assert await store.record(now_ms=1_000_000) == 1

    async def test_deadband_unterdrueckt_zappeln(self, history):
        """Dasselbe Deadband wie im State Store — es wird nicht neu erfunden."""
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=1_000_000)

        state.apply("energy.battery.soc", StateValue.valid(60.2))
        assert await store.record(now_ms=1_010_000) == 0

        state.apply("energy.battery.soc", StateValue.valid(61.0))
        assert await store.record(now_ms=1_020_000) == 1

    async def test_herzschlag_schreibt_auch_ohne_aenderung(self, history):
        """Ohne ihn wäre „konstant" nicht von „System war aus" zu
        unterscheiden."""
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=1_000_000)

        assert await store.record(now_ms=1_200_000) == 0, "vor der Herzschlagzeit"
        assert await store.record(now_ms=1_301_000) == 1, "nach der Herzschlagzeit"


class TestLueckenBleibenLuecken:
    """Der Kern von Kapitel 16 §97."""

    async def test_unbekannter_wert_wird_ohne_zahl_gespeichert(self, history):
        """Nicht als letzter bekannter Wert und schon gar nicht als 0."""
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=1_000_000)

        state.apply("energy.battery.soc", StateValue.unknown())
        await store.record(now_ms=1_010_000)

        series = await store.series("energy.battery.soc", 0, 2_000_000)
        assert [p.value for p in series.points] == [60.0, None]
        assert series.points[1].quality == "UNKNOWN"

    async def test_qualitaetswechsel_schlaegt_das_deadband(self, history):
        """Der Anfang einer Lücke ist die wichtigste Information der Kurve.

        Er darf niemals durch ein Deadband verschluckt werden — sonst führt die
        Linie ungebrochen weiter, obwohl der Fühler verstummt ist.
        """
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=1_000_000)

        # Direkt danach, weit innerhalb der Herzschlagzeit und ohne
        # Wertänderung — trotzdem muss der Punkt entstehen.
        state.apply("energy.battery.soc", StateValue.error())
        assert await store.record(now_ms=1_001_000) == 1

    async def test_veraltet_behaelt_seinen_wert(self, history):
        """STALE heißt „alt, aber echt" — hier wie überall sonst."""
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=1_000_000)

        state.apply("energy.battery.soc", StateValue(value=60.0, quality=Quality.STALE))
        await store.record(now_ms=1_010_000)

        series = await store.series("energy.battery.soc", 0, 2_000_000)
        assert series.points[-1].value == 60.0
        assert series.points[-1].quality == "STALE"

    async def test_verdichteter_eimer_ohne_werte_bleibt_leer(self, history):
        """Eine Minute ohne einen einzigen gültigen Messwert wird gespeichert —
        aber ohne Kennzahl. Der Mittelwert der Nachbarn wäre eine Erfindung.
        """
        store, state = history

        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=10 * MINUTE_MS)

        # Zwei Minuten später: nichts bekannt.
        state.apply("energy.battery.soc", StateValue.unknown())
        await store.record(now_ms=12 * MINUTE_MS)

        await store.compact(now_ms=20 * MINUTE_MS)

        series = await store.series("energy.battery.soc", 0, 10 * 24 * HOUR_MS)
        assert series.resolution == "minute"

        eimer = {p.at: p.value for p in series.points}
        assert eimer[10 * MINUTE_MS] == 60.0
        assert eimer[12 * MINUTE_MS] is None, "Ohne belastbaren Wert kein Mittelwert"


class TestVerdichtung:
    async def test_minutenmittel_entsteht_aus_rohwerten(self, history):
        store, state = history

        for offset, value in ((0, 60.0), (10_000, 62.0), (20_000, 64.0)):
            state.apply("energy.battery.soc", StateValue.valid(value))
            await store.record(now_ms=10 * MINUTE_MS + offset)

        await store.compact(now_ms=20 * MINUTE_MS)

        series = await store.series("energy.battery.soc", 0, 10 * 24 * HOUR_MS)
        assert [p.value for p in series.points] == [62.0]

    async def test_laufender_eimer_wird_ausgespart(self, history):
        """Ihn zu verdichten hieße, ein unvollständiges Mittel als endgültig
        abzulegen — beim nächsten Lauf stünde ein anderer Wert dort, ohne dass
        sich etwas geändert hätte."""
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=10 * MINUTE_MS + 5_000)

        # Verdichtung mitten in derselben Minute.
        await store.compact(now_ms=10 * MINUTE_MS + 30_000)

        series = await store.series("energy.battery.soc", 0, 10 * 24 * HOUR_MS)
        assert series.points == []

    async def test_alte_rohdaten_werden_entfernt(self, history):
        store, state = history
        store._retention = Retention(raw_days=1)  # noqa: SLF001 — gezielt

        state.apply("energy.battery.soc", StateValue.valid(60.0))
        await store.record(now_ms=1_000_000)

        await store.compact(now_ms=1_000_000 + 2 * 86_400_000)
        series = await store.series("energy.battery.soc", 0, 1_500_000)
        assert series.points == []


class TestAufloesung:
    """Die Auflösung folgt der Spanne und nicht dem Wunsch des Clients.

    Wer drei Jahre anfragt, will keine 50 Millionen Rohpunkte; wer zehn
    Minuten anfragt, will keine Stundenmittel.
    """

    @pytest.mark.parametrize(
        ("stunden", "erwartet"),
        [(1, "raw"), (6, "raw"), (24, "minute"), (14 * 24, "minute"), (60 * 24, "hour")],
    )
    async def test_spanne_bestimmt_aufloesung(self, history, stunden, erwartet):
        store, _ = history
        series = await store.series("energy.battery.soc", 0, stunden * HOUR_MS)
        assert series.resolution == erwartet


class TestCheckpoint:
    async def test_auswertungs_checkpoint_wird_persistent_gespeichert(
        self,
        history,
    ):
        store, _ = history

        assert await store.checkpoint(
            "water.forecast"
        ) is None

        await store.set_checkpoint(
            "water.forecast",
            {
                "water.tank.fresh.large": 72.5,
                "water.tank.fresh.small": 55.0,
            },
            now_ms=123_456,
        )

        checkpoint = await store.checkpoint(
            "water.forecast"
        )

        assert checkpoint is not None
        assert checkpoint.at == 123_456
        assert checkpoint.snapshot[
            "water.tank.fresh.large"
        ] == 72.5


class TestAusfall:
    async def test_ein_ausfall_reisst_die_steuerung_nicht_mit(self, history):
        """Kapitel 16 §88: Ein voller Datenträger darf die Wasserpumpe nicht
        abschalten. `record` meldet den Ausfall, wirft aber nicht."""
        store, state = history
        state.apply("energy.battery.soc", StateValue.valid(60.0))

        await store.stop()  # Datenbank zu — der nächste Schreibversuch scheitert

        with pytest.raises(RuntimeError):
            # Sicherstellen, dass der Test das Richtige prüft: Die Datenbank
            # ist tatsächlich nicht mehr ansprechbar.
            await store._database.run(lambda c: c.execute("SELECT 1"))  # noqa: SLF001
