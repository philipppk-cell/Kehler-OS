"""Überwachung der Hintergrunddienste.

Kehler OS läuft in einem Prozess (ADR 0007). Fehlerisolierung entsteht deshalb
nicht über Prozessgrenzen, sondern hier: Jeder Adapter und jeder
Hintergrunddienst läuft als eigener Task mit einer Fehlergrenze. Ein
abstürzender Kameradienst kann die Lichtsteuerung nicht mitreißen
(Kapitel 17 §16/§17).

Ein dauerhaft fehlschlagender Dienst wird **nicht** endlos neu gestartet.
Nach zu vielen Versuchen in kurzer Zeit gilt er als dauerhaft gestört und wird
als solcher gemeldet (Kapitel 17 §36/§37).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum

log = logging.getLogger(__name__)


class ServiceState(StrEnum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"
    FAILED = "FAILED"
    """Dauerhaft gestört — kein weiterer Neustartversuch."""


@dataclass
class ServiceStatus:
    """Was die Diagnose über einen Dienst wissen muss."""

    name: str
    state: ServiceState = ServiceState.STOPPED
    restarts: int = 0
    last_error: str | None = None
    started_at: float | None = None
    recent_failures: list[float] = field(default_factory=list)

    @property
    def uptime_s(self) -> float | None:
        if self.started_at is None or self.state is not ServiceState.RUNNING:
            return None
        return time.monotonic() - self.started_at


class Supervisor:
    """Startet, überwacht und beendet die Hintergrunddienste."""

    def __init__(
        self,
        *,
        max_failures: int = 5,
        failure_window_s: float = 120.0,
        initial_backoff_s: float = 1.0,
        max_backoff_s: float = 60.0,
    ) -> None:
        self._max_failures = max_failures
        self._failure_window_s = failure_window_s
        self._initial_backoff_s = initial_backoff_s
        self._max_backoff_s = max_backoff_s
        self._tasks: dict[str, asyncio.Task] = {}
        self._status: dict[str, ServiceStatus] = {}

    # ── Steuerung ───────────────────────────────────────────────────────────

    def start(self, name: str, factory: Callable[[], Awaitable[None]]) -> None:
        """Startet einen überwachten Dienst.

        ``factory`` wird bei jedem Versuch neu aufgerufen und muss eine
        langlaufende Koroutine liefern.
        """
        if name in self._tasks:
            raise RuntimeError(f"Dienst '{name}' läuft bereits")
        self._status[name] = ServiceStatus(name=name, state=ServiceState.STARTING)
        self._tasks[name] = asyncio.create_task(
            self._run(name, factory), name=f"kehleros.{name}"
        )

    async def stop(self, name: str) -> None:
        task = self._tasks.pop(name, None)
        if task is None:
            return
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        self._status[name].state = ServiceState.STOPPED

    async def stop_all(self) -> None:
        for name in list(self._tasks):
            await self.stop(name)

    # ── Überwachung ─────────────────────────────────────────────────────────

    async def _run(self, name: str, factory: Callable[[], Awaitable[None]]) -> None:
        status = self._status[name]
        backoff = self._initial_backoff_s

        while True:
            try:
                status.state = ServiceState.RUNNING
                status.started_at = time.monotonic()
                log.info("Dienst '%s' gestartet", name)
                await factory()
                # Normal beendet — kein Fehler, kein Neustart.
                status.state = ServiceState.STOPPED
                return
            except asyncio.CancelledError:
                status.state = ServiceState.STOPPED
                raise
            except Exception as exc:
                status.last_error = f"{type(exc).__name__}: {exc}"
                status.restarts += 1
                log.exception("Dienst '%s' abgebrochen", name)

                if self._is_crash_looping(status):
                    status.state = ServiceState.FAILED
                    log.error(
                        "Dienst '%s' gilt als dauerhaft gestört "
                        "(%d Fehler in %.0f s) — kein weiterer Neustart",
                        name,
                        len(status.recent_failures),
                        self._failure_window_s,
                    )
                    return

                status.state = ServiceState.RESTARTING
                log.info("Dienst '%s' startet in %.1f s neu", name, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self._max_backoff_s)

    def _is_crash_looping(self, status: ServiceStatus) -> bool:
        now = time.monotonic()
        status.recent_failures = [
            t for t in status.recent_failures if now - t < self._failure_window_s
        ]
        status.recent_failures.append(now)
        return len(status.recent_failures) >= self._max_failures

    # ── Diagnose ────────────────────────────────────────────────────────────

    def status(self) -> dict[str, ServiceStatus]:
        return dict(self._status)

    @property
    def all_running(self) -> bool:
        return all(s.state is ServiceState.RUNNING for s in self._status.values())

    @property
    def failed(self) -> list[str]:
        return [
            name for name, s in self._status.items() if s.state is ServiceState.FAILED
        ]
