"""Die gemeinsame Schnittstelle aller Hardwareadapter.

Ein Adapter ist die **einzige** Stelle, die Hardwaredetails kennt. Er
übersetzt zwischen Transport und semantischem Datenpunkt — und nur das.
Oberhalb sieht kein Code eine Adresse (Kapitel 12 §57/§58, Kapitel 18 §8/§9).

Der Simulator erfüllt dieselbe Schnittstelle wie die realen Adapter. Dadurch
testet die Simulation exakt die Pfade, die später real laufen — sie ist kein
Sonderweg (Kapitel 12 §59).
"""

from __future__ import annotations

import abc
import logging

from ..core.event_bus import EventBus
from ..core.state_store import StateStore
from ..domain.enums import LinkState, Severity, Source
from ..domain.models import Command, CommandSpec, Event

log = logging.getLogger(__name__)


class Adapter(abc.ABC):
    """Basis für alle Adapter.

    Unterklassen implementieren :meth:`connect`, :meth:`poll` und
    :meth:`execute`. Verbindungsaufbau, Wiederverbindung und
    Zustandsmeldung übernimmt diese Basis, damit sich jeder Adapter
    einheitlich verhält.
    """

    #: Kurzname für Logs und Diagnose.
    name: str = "adapter"

    #: Quelle, die den von diesem Adapter gelieferten Werten zugeschrieben wird.
    source: Source = Source.SENSOR

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        *,
        entity_ids: list[str],
        poll_interval_s: float = 1.0,
    ) -> None:
        self._state = state
        self._events = events
        self._entity_ids = list(entity_ids)
        self._owned = frozenset(entity_ids)
        self.poll_interval_s = poll_interval_s
        self._link = LinkState.INITIALIZING

    # ── Zuständigkeit ───────────────────────────────────────────────────────

    def owns(self, entity_id: str) -> bool:
        return entity_id in self._owned

    @property
    def entity_ids(self) -> list[str]:
        return list(self._entity_ids)

    @property
    def link(self) -> LinkState:
        return self._link

    # ── Von Unterklassen zu implementieren ──────────────────────────────────

    @abc.abstractmethod
    async def connect(self) -> None:
        """Baut die Verbindung auf. Wirft bei Misserfolg eine Ausnahme."""

    @abc.abstractmethod
    async def poll(self) -> None:
        """Liest den aktuellen Hardwarezustand und schreibt ihn in den Store."""

    @abc.abstractmethod
    async def execute(self, command: Command, spec: CommandSpec) -> None:
        """Setzt einen Befehl auf der Hardware ab.

        Darf **nicht** selbst den Zustand im Store setzen. Der neue Zustand
        entsteht erst durch die Rückmeldung der Hardware beim nächsten
        :meth:`poll` (Kapitel 12 §67).
        """

    async def disconnect(self) -> None:  # noqa: B027
        """Beendet die Verbindung.

        Bewusst kein ``abstractmethod``: Nicht jeder Adapter hat etwas
        abzubauen. Die leere Vorgabe ist die richtige Antwort, kein
        vergessener Haken.
        """

    # ── Lebenszyklus ────────────────────────────────────────────────────────

    async def start(self) -> None:
        await self._set_link(LinkState.INITIALIZING)
        await self.connect()
        await self._set_link(LinkState.ONLINE)

    async def stop(self) -> None:
        try:
            await self.disconnect()
        finally:
            await self._set_link(LinkState.OFFLINE)

    async def on_connection_lost(self, reason: str) -> None:
        """Meldet einen Verbindungsverlust.

        Die betroffenen Werte werden auf ``UNKNOWN`` gesetzt — ausdrücklich
        nicht auf ``0`` oder ``OFF`` (Kapitel 18 §38).
        """
        log.warning("%s: Verbindung verloren (%s)", self.name, reason)
        await self._set_link(LinkState.RECONNECTING, severity=Severity.WARNING)
        self._state.mark_source_offline(self._entity_ids)

    async def _set_link(
        self, link: LinkState, *, severity: Severity = Severity.INFO
    ) -> None:
        if self._link is link:
            return
        previous, self._link = self._link, link
        for entity_id in self._entity_ids:
            self._state.set_link(entity_id, link)
        await self._events.publish(
            Event(
                type=f"adapter.{self.name}.link_changed",
                severity=severity,
                source=self.source,
                data={"from": previous.value, "to": link.value},
            )
        )
