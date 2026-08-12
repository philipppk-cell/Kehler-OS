"""Die Befehlskette.

Geprüft wird vor allem, dass ein Befehl **niemals** als erfolgreich gilt,
solange die Hardware nichts bestätigt hat (Kapitel 18 §37).
"""

from __future__ import annotations

import asyncio

import pytest

from kehleros.adapters.simulation import Fault, SimulationAdapter
from kehleros.core.command_bus import CommandBus
from kehleros.core.state_store import StateStore
from kehleros.domain.enums import CommandPhase, Quality, RejectionReason
from kehleros.domain.models import Command


async def submit(bus: CommandBus, entity_id: str, verb: str, **params) -> Command:
    return await bus.submit(Command(entity_id=entity_id, verb=verb, params=params))


class TestPruefungVorHardwarekontakt:
    """Alles, was ohne einen einzigen Hardwarezugriff abgewiesen wird."""

    async def test_unbekannte_entity(self, bus: CommandBus, simulation):
        result = await submit(bus, "water.gibt.esnicht", "set_state", state="ON")
        assert result.phase is CommandPhase.REJECTED
        assert result.rejection is RejectionReason.UNKNOWN_ENTITY

    async def test_fehlende_capability(self, bus: CommandBus, simulation):
        # Ein Tank kann nicht geöffnet werden — die Oberfläche bietet es gar
        # nicht erst an, die API weist es trotzdem ab (Kapitel 15 §42).
        result = await submit(bus, "water.tank.fresh", "open")
        assert result.phase is CommandPhase.REJECTED
        assert result.rejection is RejectionReason.MISSING_CAPABILITY

    async def test_unbekannter_parameter(self, bus: CommandBus, simulation):
        result = await submit(bus, "water.pump.main", "set_state", helligkeit=50)
        assert result.phase is CommandPhase.REJECTED
        assert result.rejection is RejectionReason.INVALID_PARAMS

    async def test_nicht_konfigurierte_hardware(self, bus: CommandBus, simulation):
        result = await submit(bus, "vehicle.awning.main", "open")
        assert result.phase is CommandPhase.REJECTED
        assert result.rejection is RejectionReason.NOT_CONFIGURED

    async def test_ohne_adapter_kein_befehl(self, registry, state, events):
        # Ein Command Bus ohne Adapter darf nichts stillschweigend schlucken.
        bus = CommandBus(registry, state, events)
        result = await submit(bus, "water.pump.main", "set_state", state="ON")
        assert result.phase is CommandPhase.REJECTED
        assert result.rejection is RejectionReason.DEVICE_UNAVAILABLE


class TestAusfuehrung:
    async def test_erfolgreicher_schaltbefehl(
        self, bus: CommandBus, state: StateStore, simulation
    ):
        result = await submit(bus, "water.pump.main", "set_state", state="ON")
        assert result.phase is CommandPhase.COMPLETED
        assert state.require("water.pump.main").state.value == "ON"

    async def test_idempotenz(self, bus: CommandBus, simulation):
        """Zweimal EIN ist kein Timeout.

        Ohne bekannten Zielwert würde der zweite Befehl auf eine Änderung
        warten, die nicht kommt — obwohl der gewünschte Zustand längst
        erreicht ist (Kapitel 13 §33).
        """
        await submit(bus, "water.pump.main", "set_state", state="ON")
        zweiter = await submit(bus, "water.pump.main", "set_state", state="ON")
        assert zweiter.phase is CommandPhase.COMPLETED

    async def test_bewegung_laeuft_ueber_zwischenzustand(
        self, bus: CommandBus, state: StateStore, simulation: SimulationAdapter
    ):
        """Das Tor meldet OPENING, bevor es OPEN meldet.

        Genau dieser Verlauf steuert später die Animation (Kapitel 18 §105).
        """
        task = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.15)

        zwischenzustand = state.require("vehicle.garage.door").state.value
        assert zwischenzustand == "OPENING"

        # Der Befehl ist noch nicht fertig — die Oberfläche darf jetzt nicht
        # bereits "offen" behaupten.
        assert not task.done()

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_wunschzustand_getrennt_vom_ist(
        self, bus: CommandBus, state: StateStore, simulation
    ):
        task = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.15)

        current = state.require("vehicle.garage.door")
        assert current.requested is not None
        assert current.requested.value == "OPEN"
        assert current.state.value == "OPENING"

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


class TestAblassventil:
    """Ein Absperrorgan ist keine Mechanik mit kurzer Laufzeit.

    Die Unterscheidung ist keine Wortklauberei: Ein ``movable`` brächte einen
    Stopp mit und meldete Zwischenzustände. Beides hat ein Ablassventil nicht,
    und beides würde die Oberfläche anzeigen, wenn der Typ falsch wäre.
    """

    async def test_ventil_schaltet_ohne_zwischenzustand(
        self, bus: CommandBus, state: StateStore, simulation: SimulationAdapter
    ):
        # Ein Zyklus, damit der Anfangszustand im State Store steht. Vor der
        # ersten Meldung ist er UNKNOWN — und das ist richtig so: Kehler OS
        # weiß beim Start nicht, wie ein Ventil steht (Kapitel 18 §38).
        await simulation.poll()
        assert state.require("water.valve.grey").state.value == "CLOSED"

        result = await submit(bus, "water.valve.grey", "open")
        assert result.phase is CommandPhase.COMPLETED
        assert state.require("water.valve.grey").state.value == "OPEN"

        result = await submit(bus, "water.valve.grey", "close")
        assert result.phase is CommandPhase.COMPLETED
        assert state.require("water.valve.grey").state.value == "CLOSED"

    async def test_ventil_meldet_niemals_eine_fahrt(
        self, bus: CommandBus, state: StateStore, simulation: SimulationAdapter
    ):
        """Kein OPENING, kein CLOSING — auch nicht kurz.

        Beim Garagentor ist der Zwischenzustand ein Merkmal; hier wäre er eine
        Behauptung über eine Bewegung, die nicht stattfindet. Der Test greift
        deshalb **während** des Befehls zu.
        """
        await simulation.poll()

        gesehen: list[object] = []
        task = asyncio.create_task(submit(bus, "water.valve.grey", "open"))
        for _ in range(6):
            await asyncio.sleep(0.01)
            gesehen.append(state.require("water.valve.grey").state.value)
        await task

        assert "OPENING" not in gesehen
        assert set(gesehen) <= {"CLOSED", "OPEN"}

    async def test_ventil_kennt_keinen_stopp(self, bus: CommandBus, simulation):
        """Und weist ihn ab, bevor irgendetwas die Hardware erreicht."""
        result = await submit(bus, "water.valve.grey", "stop")
        assert result.phase is CommandPhase.REJECTED
        assert result.rejection is RejectionReason.MISSING_CAPABILITY

    async def test_blockiert_wird_am_ventil_nicht_angeboten(
        self, simulation: SimulationAdapter
    ):
        """Die Diagnose meldet nur, was tatsächlich etwas bewirkt.

        ``BLOCKED`` wird ausschließlich im Bewegungsablauf ausgewertet. Es am
        Ventil anzubieten hieße, eine Schaltfläche ohne Wirkung anzubieten —
        und wer sie drückt und nichts sieht, sucht den Fehler anschließend an
        der falschen Stelle.
        """
        entities = simulation.diagnostics()["entities"]
        assert Fault.BLOCKED.value not in entities["water.valve.grey"]["faults"]
        assert Fault.BLOCKED.value in entities["vehicle.garage.door"]["faults"]


class TestFehlerfaelle:
    async def test_timeout_wenn_hardware_nicht_bestaetigt(
        self, bus: CommandBus, simulation: SimulationAdapter
    ):
        """Blockierte Mechanik ergibt niemals einen Erfolg."""
        simulation.inject("vehicle.garage.door", Fault.BLOCKED)
        result = await submit(bus, "vehicle.garage.door", "open")

        assert result.phase is CommandPhase.TIMEOUT
        assert not result.phase.is_success

    async def test_adapterfehler_wird_gemeldet(
        self, bus: CommandBus, simulation: SimulationAdapter
    ):
        simulation.inject("water.pump.main", Fault.SENSOR_ERROR)
        result = await submit(bus, "water.pump.main", "set_state", state="ON")

        # Der Sensor meldet einen Defekt: Das Gerät gilt als nicht erreichbar
        # oder der Adapter lehnt ab — beides ist ein Misserfolg, niemals ein
        # stiller Erfolg.
        assert result.phase in (CommandPhase.FAILED, CommandPhase.REJECTED)
        assert not result.phase.is_success

    async def test_ungueltiger_sensorwert_bestaetigt_nichts(
        self, bus: CommandBus, state: StateStore, simulation: SimulationAdapter
    ):
        simulation.inject("water.pump.main", Fault.SENSOR_INVALID)
        assert state.require("water.pump.main").state.quality is Quality.INVALID

    async def test_wunschzustand_wird_nach_fehler_aufgeraeumt(
        self, bus: CommandBus, state: StateStore, simulation: SimulationAdapter
    ):
        simulation.inject("vehicle.garage.door", Fault.BLOCKED)
        await submit(bus, "vehicle.garage.door", "open")
        assert state.require("vehicle.garage.door").requested is None


class TestSerialisierung:
    async def test_zweiter_fahrbefehl_wird_abgewiesen(self, bus: CommandBus, simulation):
        """Solange eine Bewegung läuft, wird nicht überlagert (Kapitel 13 §21)."""
        laufend = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.1)

        zweiter = await submit(bus, "vehicle.garage.door", "close")
        assert zweiter.phase is CommandPhase.REJECTED
        assert zweiter.rejection is RejectionReason.BUSY

        laufend.cancel()
        with pytest.raises(asyncio.CancelledError):
            await laufend


class TestStopp:
    """Der Stopp ist der eine Befehl, der immer durchkommen muss."""

    async def test_stopp_wird_nicht_wegen_laufender_bewegung_abgewiesen(
        self, bus: CommandBus, simulation
    ):
        """Sonst sperrt die laufende Bewegung genau ihren eigenen Abbruch.

        Das war der Zustand vor dieser Änderung: Ein fahrendes Garagentor
        beantwortete den Stopp mit „es läuft bereits ein Befehl".
        """
        laufend = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.1)

        stopp = await submit(bus, "vehicle.garage.door", "stop")
        assert stopp.rejection is not RejectionReason.BUSY
        assert stopp.phase is CommandPhase.COMPLETED

        # Und die abgelöste Bewegung endet sofort mit — nicht im Timeout.
        abgeloest = await asyncio.wait_for(laufend, timeout=1.0)
        assert abgeloest.phase is CommandPhase.SUPERSEDED
        assert abgeloest.phase.is_success is False

    async def test_abgeloest_ist_kein_fehler_aber_auch_kein_erfolg(
        self, bus: CommandBus, simulation
    ):
        """Wer ein Tor anhält, hat erreicht, was er wollte.

        Der abgelöste Fahrbefehl hat sein Ziel trotzdem nicht erreicht — beides
        muss unterscheidbar bleiben (Kapitel 18 §20).
        """
        laufend = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.1)
        await submit(bus, "vehicle.garage.door", "stop")

        abgeloest = await asyncio.wait_for(laufend, timeout=1.0)
        assert abgeloest.phase is not CommandPhase.FAILED
        assert abgeloest.phase is not CommandPhase.TIMEOUT
        assert abgeloest.phase.is_success is False

    async def test_blockierte_bewegung_meldet_sofort(self, bus: CommandBus, simulation):
        """Blockiert ist eine Antwort — und zwar eine schnelle.

        Vorher lief der Befehl in den vollen Timeout und meldete „keine
        Rückmeldung". Die Hardware hatte aber geantwortet.
        """
        simulation.inject("vehicle.garage.door", Fault.BLOCKED)

        laufend = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        # Warten, bis die Bewegung tatsächlich angelaufen ist — der Adapter
        # meldet den Zwischenzustand mit einer kleinen Verzögerung.
        await asyncio.sleep(0.15)

        # Ein Zyklus des Adapters — dabei stellt er die Blockade fest. In der
        # laufenden Anwendung macht das die Schleife des Adapters selbst.
        await simulation.poll()

        begonnen = asyncio.get_running_loop().time()
        ergebnis = await asyncio.wait_for(laufend, timeout=1.0)
        gedauert = asyncio.get_running_loop().time() - begonnen

        assert ergebnis.phase is CommandPhase.FAILED
        assert ergebnis.phase is not CommandPhase.TIMEOUT
        # Der Befehl endet mit der Meldung, nicht mit dem Timeout (500 ms).
        assert gedauert < 0.2, f"erst nach {gedauert:.2f} s gemeldet"

    async def test_ein_zuvor_gestopptes_teil_laesst_sich_wieder_fahren(
        self, bus: CommandBus, state: StateStore, simulation
    ):
        """Der alte Endzustand darf den neuen Befehl nicht sofort beenden.

        `STOPPED` bedeutet „abgelöst" — steht das Teil aber schon vorher auf
        `STOPPED`, ist das kein Ergebnis des neuen Befehls. Ohne diese
        Unterscheidung ließe sich ein gestopptes Tor nie wieder bewegen: Der
        zweite Fahrbefehl endete sofort, weil er den eigenen Ausgangszustand
        für sein Ergebnis hielte.
        """
        laufend = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.1)
        await submit(bus, "vehicle.garage.door", "stop")
        await laufend
        assert state.require("vehicle.garage.door").state.value == "STOPPED"

        erneut = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.15)

        # Die Bewegung läuft — der alte `STOPPED`-Stand hat sie nicht beendet.
        assert not erneut.done()
        assert state.require("vehicle.garage.door").state.value == "OPENING"

        erneut.cancel()
        with pytest.raises(asyncio.CancelledError):
            await erneut


class TestNachvollziehbarkeit:
    async def test_jeder_befehl_erzeugt_ein_ereignis(
        self, bus: CommandBus, events, simulation
    ):
        gesammelt = []
        events.subscribe("command.*", lambda event: gesammelt.append(event))

        await submit(bus, "water.pump.main", "set_state", state="ON")

        assert len(gesammelt) == 1
        assert gesammelt[0].type == "command.completed"
        assert gesammelt[0].entity_id == "water.pump.main"

    async def test_abgewiesener_befehl_wird_ebenfalls_gemeldet(
        self, bus: CommandBus, events, simulation
    ):
        gesammelt = []
        events.subscribe("command.*", lambda event: gesammelt.append(event))

        await submit(bus, "water.tank.fresh", "open")

        assert gesammelt[0].type == "command.rejected"
        assert gesammelt[0].data["rejection"] == "MISSING_CAPABILITY"

    async def test_correlation_id_bleibt_erhalten(
        self, bus: CommandBus, events, simulation
    ):
        gesammelt = []
        events.subscribe("command.*", lambda event: gesammelt.append(event))

        command = Command(
            entity_id="water.pump.main",
            verb="set_state",
            params={"state": "ON"},
        )
        await bus.submit(command)

        assert gesammelt[0].correlation_id == command.correlation_id


class TestWertebereich:
    """Grenzen einstellbarer Werte.

    Das ist die eigentliche Schutzfunktion — nicht ein Bestätigungsdialog in
    der Oberfläche. Ein Client, der die Oberfläche umgeht, muss hier
    scheitern (Kapitel 15 §42).
    """

    async def test_wert_ueber_der_grenze_wird_abgewiesen(self, bus, registry):
        command = await bus.submit(
            Command(
                entity_id="energy.shore.limit", verb="set_value", params={"value": 63}
            )
        )

        assert command.phase is CommandPhase.REJECTED
        assert command.rejection is RejectionReason.INVALID_PARAMS

    async def test_wert_unter_der_grenze_wird_abgewiesen(self, bus, registry):
        command = await bus.submit(
            Command(entity_id="energy.shore.limit", verb="set_value", params={"value": 1})
        )

        assert command.phase is CommandPhase.REJECTED
        assert command.rejection is RejectionReason.INVALID_PARAMS

    async def test_wert_an_der_grenze_ist_zulaessig(self, bus, simulation):
        command = await bus.submit(
            Command(
                entity_id="energy.shore.limit", verb="set_value", params={"value": 16}
            )
        )

        assert command.phase is CommandPhase.COMPLETED

    async def test_fehlender_zielwert_wird_abgewiesen(self, bus, registry):
        """Ein Befehl ohne Zielwert liefe sonst in einen Timeout."""
        command = await bus.submit(
            Command(entity_id="energy.shore.limit", verb="set_value", params={})
        )

        assert command.phase is CommandPhase.REJECTED
        assert command.rejection is RejectionReason.INVALID_PARAMS

    async def test_text_statt_zahl_wird_abgewiesen(self, bus, registry):
        command = await bus.submit(
            Command(
                entity_id="energy.shore.limit", verb="set_value", params={"value": "viel"}
            )
        )

        assert command.phase is CommandPhase.REJECTED
        assert command.rejection is RejectionReason.INVALID_PARAMS
