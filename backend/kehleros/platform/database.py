"""SQLite-Zugriff.

ADR 0004 wählt SQLite und begründet es: wartungsfrei, absturzsicher, Backup
ist eine Dateikopie. Diese Datei setzt die dort genannten Einstellungen an
genau einer Stelle um, statt sie an jeder Öffnungsstelle zu wiederholen.

**Der Schreibzugriff läuft in einem eigenen Thread.** SQLite ist synchron; ein
Schreibvorgang auf eine SD-Karte kann Millisekunden bis Sekunden dauern. Im
Ereignis-Loop ausgeführt, würde er die Zustandsverteilung und damit die
Bedienung anhalten — die Historie darf die Steuerung nicht ausbremsen
(Kapitel 16 §88, Kapitel 17 §97).
"""

from __future__ import annotations

import asyncio
import logging
import sqlite3
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")


def connect(path: Path, durable: bool) -> sqlite3.Connection:
    """Öffnet eine Datenbank mit den Einstellungen aus ADR 0004.

    ``durable`` unterscheidet die beiden Datenbanken, und der Unterschied ist
    bewusst: Die Konfigurationsdatenbank muss einen Stromausfall überstehen,
    koste es Schreibleistung (``synchronous=FULL``). Die Historie darf im
    schlimmsten Fall die letzten Sekunden verlieren — dafür schont
    ``synchronous=NORMAL`` die SD-Karte spürbar. Ein verlorener Messpunkt ist
    kein Schaden; eine zerstörte Konfiguration wäre einer.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(f"PRAGMA synchronous={'FULL' if durable else 'NORMAL'}")
    connection.execute("PRAGMA foreign_keys=ON")
    # Ohne Zeitlimit blockiert ein paralleler Schreibzugriff sofort mit
    # „database is locked", statt kurz zu warten.
    connection.execute("PRAGMA busy_timeout=5000")
    connection.row_factory = sqlite3.Row
    return connection


class Database:
    """Eine Datenbank mit **einem eigenen Thread** für alle Zugriffe.

    Der Thread ist nicht bloß eine Auslagerung, sondern die Zusicherung: Alle
    Arbeitseinheiten laufen nacheinander auf derselben Verbindung, in der
    Reihenfolge, in der sie abgegeben wurden. Es gibt genau einen Schreiber.

    ── Warum ein eigener Executor und nicht ``asyncio.to_thread`` ────────────

    Das war ein Absturz und keine Geschmacksfrage. ``to_thread`` benutzt den
    Standard-Executor, und eine **abgebrochene Koroutine bricht den Thread
    nicht ab**: Wird der Historiendienst beim Herunterfahren abgebrochen,
    während er gerade schreibt, läuft der Schreibvorgang weiter. Wurde
    unmittelbar danach die Verbindung geschlossen, griff SQLite auf
    freigegebenen Speicher zu — reproduzierbar ein Speicherzugriffsfehler beim
    Beenden.

    Mit einem eigenen Executor lässt sich beim Schließen **warten, bis
    tatsächlich nichts mehr läuft**. Das ist die einzige Reihenfolge, die
    sicher ist: erst die Arbeit zu Ende, dann die Verbindung zu.
    """

    def __init__(self, path: Path, *, durable: bool = False) -> None:
        self.path = path
        self._durable = durable
        self._connection: sqlite3.Connection | None = None
        self._executor: ThreadPoolExecutor | None = None

    async def open(self) -> None:
        if self._connection is not None:
            return
        # Genau ein Arbeiter: Damit ist die Serialisierung eine Eigenschaft
        # des Executors und braucht keine zusätzliche Sperre, die man
        # vergessen könnte.
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="db")
        self._connection = await asyncio.get_running_loop().run_in_executor(
            self._executor, connect, self.path, self._durable
        )
        log.info("Datenbank geöffnet: %s", self.path)

    async def close(self) -> None:
        """Beendet die laufende Arbeit und schließt danach.

        ``shutdown(wait=True)`` ist der entscheidende Teil: Es kehrt erst
        zurück, wenn keine Arbeitseinheit mehr läuft. Erst danach darf die
        Verbindung geschlossen werden.
        """
        connection, self._connection = self._connection, None
        executor, self._executor = self._executor, None

        if executor is not None:
            await asyncio.to_thread(executor.shutdown, True)
        if connection is not None:
            connection.close()

    async def run(self, work: Callable[[sqlite3.Connection], T]) -> T:
        """Führt eine Arbeitseinheit im Datenbank-Thread aus.

        Der Aufrufer bekommt die Verbindung und darf darauf mehrere Anweisungen
        absetzen — eine Arbeitseinheit ist eine Transaktion und nicht eine
        Zeile.
        """
        connection, executor = self._connection, self._executor
        if connection is None or executor is None:
            raise RuntimeError("Datenbank ist nicht geöffnet")

        return await asyncio.get_running_loop().run_in_executor(
            executor, work, connection
        )
