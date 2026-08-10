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
    async def test_zweiter_fahrbefehl_wird_abgewiesen(
        self, bus: CommandBus, simulation
    ):
        """Solange eine Bewegung läuft, wird nicht überlagert (Kapitel 13 §21)."""
        laufend = asyncio.create_task(submit(bus, "vehicle.garage.door", "open"))
        await asyncio.sleep(0.1)

        zweiter = await submit(bus, "vehicle.garage.door", "close")
        assert zweiter.phase is CommandPhase.REJECTED
        assert zweiter.rejection is RejectionReason.BUSY

        laufend.cancel()
        with pytest.raises(asyncio.CancelledError):
            await laufend


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
            Command(
                entity_id="energy.shore.limit", verb="set_value", params={"value": 1}
            )
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
