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
import time
from dataclasses import dataclass
from pathlib import Path

from .adapters.base import Adapter
from .adapters.opcua_plc import OpcUaPlcAdapter
from .adapters.opcua_plc_write import OpcUaPlcWriteAdapter
from .adapters.simulation import SimulationAdapter
from .config.hardware import (
    load_plc_device,
    load_plc_read_points,
    load_plc_write_points,
)
from .config.loader import build_entities, load_settings, load_vehicle
from .config.models import Settings, VehicleConfig
from .core.alerts import derive_alerts
from .core.command_bus import CommandBus
from .core.event_bus import EventBus
from .core.history import HistoryStore, Retention
from .core.registry import Registry
from .core.state_store import StateStore
from .domain.enums import Environment, Severity, SystemHealth
from .domain.models import Event
from .platform.database import Database
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

    def __init__(
        self,
        settings: Settings,
        vehicle: VehicleConfig,
        *,
        vehicle_dir: Path | None = None,
        hardware_dir: Path | None = None,
    ) -> None:
        from . import __version__

        self.version = __version__
        self.settings = settings
        self.vehicle = vehicle

        self.vehicle_dir = vehicle_dir
        self.hardware_dir = hardware_dir
        """Verzeichnis der Fahrzeugkonfiguration.

        Nur dafür da, das 3D-Modell daneben zu finden. Ein eigener
        Konfigurationseintrag dafür wäre eine Einstellung, die niemand je
        anders setzt — die Datei liegt bei der Beschreibung des Fahrzeugs,
        weil sie zum Fahrzeug gehört.
        """

        self.registry = Registry()
        self.registry.register_all(build_entities(vehicle))

        self.state = StateStore(self.registry)
        self.events = EventBus()
        self.commands = CommandBus(self.registry, self.state, self.events)
        self.supervisor = Supervisor()

        self.history: HistoryStore | None = None
        if settings.history.enabled:
            self.history = HistoryStore(
                Database(Path(settings.history.path)),
                self.state,
                self.registry,
                retention=Retention(
                    raw_days=settings.history.raw_days,
                    minute_days=settings.history.minute_days,
                    hour_days=settings.history.hour_days,
                ),
                heartbeat_s=settings.history.heartbeat_s,
            )

        self.adapters: list[Adapter] = []
        self._started = False

    # ── Aufbau ──────────────────────────────────────────────────────────────

    @classmethod
    def from_config(
        cls, vehicle_path: Path, settings_path: Path | None = None
    ) -> Application:
        settings = load_settings(settings_path)
        vehicle = load_vehicle(vehicle_path)
        return cls(
            settings,
            vehicle,
            vehicle_dir=vehicle_path.parent,
            hardware_dir=vehicle_path.parent.parent / "hardware",
        )

    def _build_adapters(self) -> list[Adapter]:
        """Wählt die Adapter anhand der Betriebsart.

        In ``production`` werden ausschließlich reale Adapter gebaut. Da die
        SPS-Parameter noch fehlen (offene Punkte A2/A3), gibt es dort derzeit
        keinen realen Adapter — und es wird auch keiner erfunden
        (Kapitel 18 §97).
        """
        if self.settings.environment is Environment.PRODUCTION:
            if self.hardware_dir is None:
                log.warning(
                    "Produktionsbetrieb ohne Hardwarekonfiguration: "
                    "Es werden keine realen Adapter gestartet."
                )
                return []

            device = load_plc_device(self.hardware_dir / "devices.yaml")
            read_points = load_plc_read_points(
                self.hardware_dir / "mapping.yaml"
            )
            write_points = load_plc_write_points(
                self.hardware_dir / "mapping.yaml"
            )

            adapters: list[Adapter] = [
                OpcUaPlcAdapter(
                    self.state,
                    self.events,
                    self.registry,
                    device,
                    read_points,
                )
            ]

            if write_points:
                adapters.append(
                    OpcUaPlcWriteAdapter(
                        self.state,
                        self.events,
                        self.registry,
                        device,
                        write_points,
                    )
                )

            return adapters

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

        if self.history is not None:
            # Als überwachter Dienst mit eigener Fehlergrenze: Ein voller
            # Datenträger oder eine beschädigte Datei darf die Steuerung nicht
            # mitreißen (Kapitel 16 §88, Kapitel 17 §16/§17).
            await self.history.start()
            self.supervisor.start("history", self._history_loop)

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
        if self.history is not None:
            await self.history.stop()
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

    async def _history_loop(self) -> None:
        """Zeichnet auf und verdichtet in einem Takt.

        Beides in einer Schleife und nicht in zweien: Sie greifen auf dieselbe
        Datei zu, und zwei Dienste, die sich gegenseitig sperren, wären zwei
        Fehlerquellen statt einer.
        """
        history = self.history
        assert history is not None  # nur gestartet, wenn vorhanden

        settings = self.settings.history
        next_compaction = 0.0

        while True:
            await history.record()

            now = time.monotonic()
            if now >= next_compaction:
                await history.compact()
                next_compaction = now + settings.compact_interval_s

            await asyncio.sleep(settings.sample_interval_s)

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

    @property
    def model_file(self) -> Path | None:
        """Das 3D-Modell des Fahrzeugs, falls eines hinterlegt ist.

        Ist keines da, bleibt es bei der aus Code gebauten Darstellung
        (ADR 0008). Das ist kein Mangelzustand, sondern der Auslieferungsstand:
        Die Oberfläche zeigt in beiden Fällen dasselbe Fahrzeug mit denselben
        Zuständen — nur eben verschieden fein.
        """
        if self.vehicle_dir is None:
            return None
        pfad = self.vehicle_dir / "model.glb"
        return pfad if pfad.is_file() else None

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

        **Der Gesamtzustand ergibt sich aus denselben Warnungen, die die
        Oberfläche anzeigt.** Das ist bewusst so und nicht nur bequem: Wären
        es zwei getrennte Ableitungen, könnten sie sich widersprechen — und
        genau das ist passiert. Ein verstummter Tanksensor stand als Warnung
        in der Liste, während der Systemstatus „Alles in Ordnung“ meldete.
        Eine Zusammenfassung, die beruhigt, während darunter eine Warnung
        steht, ist schlimmer als gar keine.

        ``CRITICAL`` bleibt trotzdem selten — zu viele kritische Meldungen
        entwerten die Priorität (Kapitel 13 §55). Deshalb hebt eine einzelne
        Sensorwarnung den Gesamtzustand nur auf ``DEGRADED``.
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

        alerts = derive_alerts(self.state, self.registry)
        severities = {alert.severity for alert in alerts}

        if Severity.CRITICAL in severities:
            return SystemHealth.CRITICAL
        if Severity.WARNING in severities:
            return SystemHealth.DEGRADED
        if Severity.NOTICE in severities:
            return SystemHealth.WARNING

        # INFO bleibt ohne Wirkung: „Nicht konfiguriert“ ist ein offener
        # Punkt in der Einrichtung, keine Störung im Betrieb.
        return SystemHealth.HEALTHY
