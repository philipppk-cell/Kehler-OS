"""Zusammenbau des Systems.

Hier wird entschieden, welche Adapter laufen — und das geschieht **einmalig
beim Start** anhand der Umgebung. Zur Laufzeit ist kein Wechsel zwischen
Simulation und realer Hardware möglich; die beiden teilen sich keinen
Codepfad, über den ein simuliertes Gerät je einen realen Aktor erreichen
könnte (Kapitel 15 §95/§96, Kapitel 18 §67).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from .adapters.base import Adapter
from .adapters.simulation import SimulationAdapter
from .config.loader import build_entities, load_settings, load_vehicle
from .config.models import Settings, VehicleConfig
from .core.command_bus import CommandBus
from .core.event_bus import EventBus
from .core.registry import Registry
from .core.state_store import StateStore
from .domain.enums import Environment, LinkState, Severity, SystemHealth
from .domain.models import Event
from .platform.supervisor import ServiceState, Supervisor

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SystemInfo:
    """Was die Oberfläche über den Systemzustand wissen muss."""

    version: str
    environment: Environment
    simulated: bool
    health: SystemHealth
    entities: int
    unconfigured: int
    services: dict[str, str]
    state_version: int


class Application:
    """Das laufende Kehler OS."""

    def __init__(self, settings: Settings, vehicle: VehicleConfig) -> None:
        from . import __version__

        self.version = __version__
        self.settings = settings
        self.vehicle = vehicle

        self.registry = Registry()
        self.registry.register_all(build_entities(vehicle))

        self.state = StateStore(self.registry)
        self.events = EventBus()
        self.commands = CommandBus(self.registry, self.state, self.events)
        self.supervisor = Supervisor()

        self.adapters: list[Adapter] = []
        self._started = False

    # ── Aufbau ──────────────────────────────────────────────────────────────

    @classmethod
    def from_config(
        cls, vehicle_path: Path, settings_path: Path | None = None
    ) -> Application:
        settings = load_settings(settings_path)
        vehicle = load_vehicle(vehicle_path)
        return cls(settings, vehicle)

    def _build_adapters(self) -> list[Adapter]:
        """Wählt die Adapter anhand der Betriebsart.

        In ``production`` werden ausschließlich reale Adapter gebaut. Da die
        SPS-Parameter noch fehlen (offene Punkte A2/A3), gibt es dort derzeit
        keinen realen Adapter — und es wird auch keiner erfunden
        (Kapitel 18 §97).
        """
        if self.settings.environment is Environment.PRODUCTION:
            log.warning(
                "Produktionsbetrieb: Es sind noch keine realen Adapter "
                "konfiguriert. Siehe docs/OPEN_HARDWARE_REQUIREMENTS.md (A2, A3)."
            )
            return []

        return [
            SimulationAdapter(
                self.state,
                self.events,
                self.registry,
                seed=self.settings.simulation.seed,
                poll_interval_s=self.settings.simulation.poll_interval_s,
            )
        ]

    # ── Lebenszyklus ────────────────────────────────────────────────────────

    async def start(self) -> None:
        if self._started:
            return
        self._started = True

        log.info(
            "Kehler OS %s startet in Betriebsart '%s' mit %d Entities",
            self.version,
            self.settings.environment.value,
            len(self.registry),
        )
        if self.settings.is_simulated:
            log.warning("SIMULATION — es wird keine reale Fahrzeughardware gesteuert")

        unconfigured = self.registry.unconfigured()
        if unconfigured:
            log.info(
                "%d Entities ohne Hardwarezuordnung: %s",
                len(unconfigured),
                ", ".join(e.id for e in unconfigured),
            )

        self.adapters = self._build_adapters()
        for adapter in self.adapters:
            self.commands.register_target(adapter)
            self.supervisor.start(adapter.name, self._adapter_loop(adapter))

        self.supervisor.start("stale-sweep", self._stale_loop)

        await self.events.publish(
            Event(
                type="system.started",
                data={
                    "version": self.version,
                    "environment": self.settings.environment.value,
                    "simulated": self.settings.is_simulated,
                },
            )
        )

    async def stop(self) -> None:
        await self.supervisor.stop_all()
        for adapter in self.adapters:
            try:
                await adapter.stop()
            except Exception:
                log.exception("Adapter %s ließ sich nicht sauber beenden", adapter.name)
        await self.events.publish(Event(type="system.stopped"))
        self._started = False

    # ── Hintergrunddienste ──────────────────────────────────────────────────

    def _adapter_loop(self, adapter: Adapter):
        """Verbindet und liest zyklisch.

        Ein Verbindungsverlust setzt die Werte auf ``UNKNOWN`` und wird nach
        oben gemeldet — der Supervisor sorgt für den Wiederaufbau mit
        Backoff (Kapitel 11 §17).
        """

        async def loop() -> None:
            await adapter.start()
            try:
                while True:
                    await adapter.poll()
                    await asyncio.sleep(adapter.poll_interval_s)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await adapter.on_connection_lost(str(exc))
                raise

        return loop

    async def _stale_loop(self) -> None:
        """Lässt Werte altern, die nicht mehr aktualisiert werden."""
        interval = self.settings.stale_sweep_interval_s
        while True:
            await asyncio.sleep(interval)
            for delta in self.state.sweep_stale():
                await self.events.publish(
                    Event(
                        type="state.quality_degraded",
                        entity_id=delta.entity_id,
                        severity=Severity.NOTICE,
                        data={"quality": delta.entity_state.state.quality.value},
                    )
                )

    # ── Zustand nach außen ──────────────────────────────────────────────────

    def info(self) -> SystemInfo:
        return SystemInfo(
            version=self.version,
            environment=self.settings.environment,
            simulated=self.settings.is_simulated,
            health=self.health(),
            entities=len(self.registry),
            unconfigured=len(self.registry.unconfigured()),
            services={
                name: status.state.value
                for name, status in self.supervisor.status().items()
            },
            state_version=self.state.version,
        )

    def health(self) -> SystemHealth:
        """Leitet den Gesamtzustand aus den Einzelzuständen ab.

        ``CRITICAL`` bleibt bewusst selten — zu viele kritische Meldungen
        entwerten die Priorität (Kapitel 13 §55).
        """
        statuses = self.supervisor.status()
        if not statuses:
            return SystemHealth.INITIALIZING

        if self.supervisor.failed:
            return SystemHealth.CRITICAL

        if any(s.state is ServiceState.STARTING for s in statuses.values()):
            return SystemHealth.INITIALIZING

        if any(s.state is ServiceState.RESTARTING for s in statuses.values()):
            return SystemHealth.WARNING

        offline = [
            entity_state
            for entity_state in self.state
            if entity_state.link in (LinkState.OFFLINE, LinkState.ERROR)
        ]
        if offline:
            return SystemHealth.DEGRADED

        return SystemHealth.HEALTHY
