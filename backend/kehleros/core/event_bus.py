"""Ereignisverteilung innerhalb des Backends.

Module sprechen nicht direkt miteinander, sondern senden Ereignisse. Andere
Module reagieren darauf. Dadurch entstehen möglichst wenige direkte
Abhängigkeiten (Kapitel 2, Kapitel 5 §12).

Ein Fehler in einem Abnehmer darf die Verteilung nicht anhalten — deshalb wird
jeder Aufruf einzeln abgesichert (Kapitel 17 §19).
"""

from __future__ import annotations

import asyncio
import contextlib
import fnmatch
import inspect
import logging
from collections.abc import Awaitable, Callable
from typing import TypeAlias

from ..domain.models import Event

log = logging.getLogger(__name__)

Handler: TypeAlias = Callable[[Event], Awaitable[None] | None]


class EventBus:
    """Schlanke Ereignisverteilung mit Mustererkennung.

    Muster folgen der üblichen Platzhalterschreibweise::

        vehicle.garage.door.opened   genau dieses Ereignis
        vehicle.garage.*             alles zum Garagentor
        *                            alles
    """

    def __init__(self) -> None:
        self._handlers: list[tuple[str, Handler]] = []

    def subscribe(self, pattern: str, handler: Handler) -> Callable[[], None]:
        """Meldet einen Abnehmer an und gibt die Abmeldefunktion zurück."""
        entry = (pattern, handler)
        self._handlers.append(entry)

        def unsubscribe() -> None:
            with contextlib.suppress(ValueError):
                self._handlers.remove(entry)

        return unsubscribe

    async def publish(self, event: Event) -> None:
        """Stellt ein Ereignis allen passenden Abnehmern zu."""
        for pattern, handler in list(self._handlers):
            if not fnmatch.fnmatchcase(event.type, pattern):
                continue
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except asyncio.CancelledError:
                raise
            except Exception:
                # Ein defekter Abnehmer darf die übrigen nicht blockieren.
                log.exception(
                    "Fehler im Event-Handler für '%s' (Muster '%s')",
                    event.type,
                    pattern,
                )

    @property
    def handler_count(self) -> int:
        return len(self._handlers)
