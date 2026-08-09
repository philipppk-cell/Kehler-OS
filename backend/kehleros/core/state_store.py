"""Der State Store — die eine Wahrheit über den Fahrzeugzustand.

Der Zustand lebt ausschließlich im Arbeitsspeicher. Er wird **nicht** aus der
Datenbank wiederhergestellt: Nach einem Neustart ist alles ``UNKNOWN``, bis
ein Adapter einen bestätigten Wert liefert (Kapitel 6 §44, Kapitel 12 §66,
Kapitel 13 §25).

Nur Adapter schreiben hier hinein. Ein Befehl verändert den Zustand niemals
selbst — er löst allenfalls eine Hardwareänderung aus, die dann zurückgemeldet
wird (Kapitel 12 §67, Kapitel 18 §37).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterator
from dataclasses import dataclass, replace
from datetime import datetime

from ..domain.enums import LinkState, Quality
from ..domain.models import EntityState, RequestedState, StateValue, utcnow
from .registry import Registry

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class StateDelta:
    """Eine Zustandsänderung, wie sie an die Clients geht.

    Übertragen wird der vollständige Zustand *einer* Entity, nicht der des
    Gesamtsystems. Kapitel 13 §29 verbietet Vollupdates bei Einzeländerungen —
    gemeint ist der Gesamtzustand. Eine einzelne Entity komplett zu senden ist
    klein, macht den Client einfacher und schließt Teilaktualisierungsfehler
    aus.
    """

    entity_state: EntityState

    @property
    def entity_id(self) -> str:
        return self.entity_state.entity_id

    @property
    def seq(self) -> int:
        return self.entity_state.seq


class Subscription:
    """Ein Abnehmer von Zustandsänderungen, typischerweise ein WebSocket.

    Die Warteschlange ist begrenzt. Kommt ein Client nicht mehr hinterher,
    werden seine Deltas verworfen und er wird zur Neusynchronisation
    aufgefordert — statt den Speicher wachsen zu lassen (Kapitel 17 §97).
    """

    def __init__(self, maxsize: int = 256) -> None:
        self._queue: asyncio.Queue[StateDelta] = asyncio.Queue(maxsize=maxsize)
        self.needs_resync = False

    def offer(self, delta: StateDelta) -> None:
        try:
            self._queue.put_nowait(delta)
        except asyncio.QueueFull:
            self.needs_resync = True
            self._drain()

    def _drain(self) -> None:
        while not self._queue.empty():
            self._queue.get_nowait()

    async def get(self) -> StateDelta:
        return await self._queue.get()

    def __aiter__(self) -> Subscription:
        return self

    async def __anext__(self) -> StateDelta:
        return await self.get()


class StateStore:
    """Hält den aktuellen Zustand aller Entities und verteilt Änderungen."""

    def __init__(self, registry: Registry) -> None:
        self._registry = registry
        self._states: dict[str, EntityState] = {}
        self._subscribers: set[Subscription] = set()
        self._version = 0
        self._initialise()

    def _initialise(self) -> None:
        """Alles startet unbekannt.

        Kein gespeicherter Zustand wird als aktuell übernommen — auch dann
        nicht, wenn er beim letzten Herunterfahren korrekt war.
        """
        for entity in self._registry:
            link = (
                LinkState.INITIALIZING
                if entity.configured
                else LinkState.NOT_CONFIGURED
            )
            self._states[entity.id] = EntityState(
                entity_id=entity.id,
                state=StateValue.unknown(unit=entity.unit),
                link=link,
            )

    # ── Lesen ───────────────────────────────────────────────────────────────

    @property
    def version(self) -> int:
        """Version des Gesamtzustands, steigt bei jeder Änderung."""
        return self._version

    def get(self, entity_id: str) -> EntityState | None:
        return self._states.get(entity_id)

    def require(self, entity_id: str) -> EntityState:
        state = self._states.get(entity_id)
        if state is None:
            raise KeyError(f"Kein Zustand für Entity '{entity_id}'")
        return state

    def snapshot(self) -> dict[str, EntityState]:
        """Ein in sich konsistenter Gesamtzustand für einen neuen Client.

        Wird aus einer einzigen Momentaufnahme erzeugt und nicht feldweise
        zusammengesammelt (Kapitel 13 §30).
        """
        return dict(self._states)

    def __iter__(self) -> Iterator[EntityState]:
        return iter(self._states.values())

    # ── Schreiben ───────────────────────────────────────────────────────────

    def apply(
        self,
        entity_id: str,
        value: StateValue,
        *,
        attribute: str | None = None,
        force: bool = False,
    ) -> StateDelta | None:
        """Übernimmt einen von der Hardware gemeldeten Wert.

        Gibt ``None`` zurück, wenn sich nichts Nennenswertes geändert hat —
        dann entsteht auch kein Ereignis und keine Netzlast (Kapitel 13 §65).
        """
        current = self._states.get(entity_id)
        if current is None:
            log.warning("Zustand für unbekannte Entity '%s' verworfen", entity_id)
            return None

        entity = self._registry.get(entity_id)
        deadband = entity.deadband if entity else 0.0

        previous = current.attributes.get(attribute) if attribute else current.state
        if not force and not value.differs_from(previous, deadband=deadband):
            return None

        if attribute:
            attributes = dict(current.attributes)
            attributes[attribute] = value
            updated = replace(current, attributes=attributes)
        else:
            updated = replace(current, state=value)

        return self._commit(updated)

    def set_link(self, entity_id: str, link: LinkState) -> StateDelta | None:
        """Setzt den Verbindungszustand einer Entity.

        Wird die Verbindung verloren, altern die Werte separat über
        :meth:`sweep_stale` — der letzte Wert bleibt nicht stillschweigend
        als aktuell stehen.
        """
        current = self._states.get(entity_id)
        if current is None or current.link is link:
            return None
        return self._commit(replace(current, link=link))

    def set_requested(
        self,
        entity_id: str,
        requested: RequestedState | None,
    ) -> StateDelta | None:
        """Hinterlegt oder löscht den Wunschzustand.

        Strikt getrennt vom tatsächlichen Zustand: Die Oberfläche zeigt damit
        „wird ausgeführt“, ohne etwas über die Hardware zu behaupten.
        """
        current = self._states.get(entity_id)
        if current is None:
            return None
        if current.requested is None and requested is None:
            return None
        return self._commit(replace(current, requested=requested))

    def _commit(self, updated: EntityState) -> StateDelta:
        updated = replace(updated, seq=updated.seq + 1)
        self._states[updated.entity_id] = updated
        self._version += 1
        delta = StateDelta(entity_state=updated)
        self._publish(delta)
        return delta

    # ── Alterung ────────────────────────────────────────────────────────────

    def sweep_stale(self, now: datetime | None = None) -> list[StateDelta]:
        """Stuft Werte herab, die länger ausbleiben als erwartet.

        Zuerst ``STALE`` (war gültig, ist aber alt), nach dem doppelten
        Intervall ``UNKNOWN``. So altert ein Wert sichtbar, statt still
        falsch zu werden (Kapitel 13 §9).
        """
        now = now or utcnow()
        deltas: list[StateDelta] = []

        for entity in self._registry:
            interval = entity.expected_interval_s
            if not interval:
                continue
            current = self._states.get(entity.id)
            if current is None:
                continue

            value = current.state
            if value.quality not in (Quality.VALID, Quality.STALE):
                continue

            age = value.age_seconds(now)
            if value.quality is Quality.VALID and age > interval:
                delta = self.apply(entity.id, value.aged(Quality.STALE), force=True)
            elif value.quality is Quality.STALE and age > interval * 2:
                delta = self.apply(entity.id, value.aged(Quality.UNKNOWN), force=True)
            else:
                delta = None

            if delta is not None:
                log.info(
                    "Wert von %s auf %s herabgestuft (%.1fs ohne Aktualisierung)",
                    entity.id,
                    delta.entity_state.state.quality.value,
                    age,
                )
                deltas.append(delta)

        return deltas

    def mark_source_offline(self, entity_ids: list[str]) -> list[StateDelta]:
        """Setzt Entities auf unbekannt, wenn ihre Quelle ausfällt.

        Ausdrücklich nicht auf ``0`` oder ``OFF``: Ein ausgefallener Adapter
        weiß nichts über die Hardware (Kapitel 18 §38).
        """
        deltas: list[StateDelta] = []
        for entity_id in entity_ids:
            current = self._states.get(entity_id)
            if current is None:
                continue
            link = self.set_link(entity_id, LinkState.OFFLINE)
            if link is not None:
                deltas.append(link)
            if current.state.quality is not Quality.UNKNOWN:
                aged = self.apply(
                    entity_id, current.state.aged(Quality.UNKNOWN), force=True
                )
                if aged is not None:
                    deltas.append(aged)
        return deltas

    # ── Verteilung ──────────────────────────────────────────────────────────

    def subscribe(self) -> Subscription:
        subscription = Subscription()
        self._subscribers.add(subscription)
        return subscription

    def unsubscribe(self, subscription: Subscription) -> None:
        self._subscribers.discard(subscription)

    def _publish(self, delta: StateDelta) -> None:
        for subscription in self._subscribers:
            subscription.offer(delta)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)
