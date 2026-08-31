"""Messhistorie.

Kehler OS zeigt nicht nur, wie es *jetzt* aussieht, sondern auch, wie es
*wurde* (Kapitel 16 §1). Diese Datei ist dafür zuständig.

── Die eine Regel, die alles andere bestimmt ─────────────────────────────────

**Eine Lücke bleibt eine Lücke.** Kapitel 16 §97 verbietet ausdrücklich,
fehlende Messwerte als reale Historie auszugeben. Ein Fühler, der zwei Stunden
verstummt war, darf in der Kurve keine gerade Linie zwischen den beiden
Punkten erzeugen, zwischen denen niemand etwas wusste — er muss ein Loch
hinterlassen.

Umgesetzt wird das an drei Stellen, nicht an einer:

1. **Beim Schreiben** wird die Qualität mitgespeichert, und ein nicht
   belastbarer Wert kommt als ``NULL`` in die Datenbank — nicht als letzter
   bekannter Wert und schon gar nicht als 0.
2. **Beim Verdichten** zählt ``n`` nur die belastbaren Werte. Eine Minute ohne
   einen einzigen gültigen Messwert wird gespeichert, aber mit ``n = 0`` und
   ohne Kennzahlen.
3. **Beim Lesen** wird nichts aufgefüllt. Wer die Punkte zeichnet, bekommt
   Löcher und muss sie als Löcher darstellen.

── Wann geschrieben wird ─────────────────────────────────────────────────────

Kapitel 16 §8 verlangt „eine sinnvolle Kombination aus Zeitintervall,
Wertänderung und Deadband". Genau die drei Bedingungen gelten hier — ein Punkt
wird geschrieben, wenn **eine** davon zutrifft:

* die Qualität hat sich geändert (aus gültig wird unbekannt oder umgekehrt),
* der Wert hat sich um mehr als das Deadband der Entity bewegt,
* seit dem letzten Punkt ist die Herzschlagzeit vergangen.

Der dritte Fall ist der wichtige: Ohne ihn ließe sich später nicht
unterscheiden, ob ein Wert konstant war oder ob das System aus war. Mit ihm
heißt „länger als eine Herzschlagzeit kein Punkt" eindeutig: hier lief nichts.

Das Deadband stammt aus der Entity-Konfiguration und wird **nicht neu
erfunden** — es ist dieselbe Zahl, mit der schon der State Store arbeitet.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass

from ..domain.enums import Quality
from ..platform.database import Database
from .registry import Registry
from .state_store import StateStore

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sample (
    entity_id TEXT    NOT NULL,
    at        INTEGER NOT NULL,
    value     REAL,
    quality   TEXT    NOT NULL,
    PRIMARY KEY (entity_id, at)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS rollup_minute (
    entity_id TEXT    NOT NULL,
    bucket    INTEGER NOT NULL,
    n         INTEGER NOT NULL,
    min_value REAL,
    max_value REAL,
    avg_value REAL,
    PRIMARY KEY (entity_id, bucket)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS rollup_hour (
    entity_id TEXT    NOT NULL,
    bucket    INTEGER NOT NULL,
    n         INTEGER NOT NULL,
    min_value REAL,
    max_value REAL,
    avg_value REAL,
    PRIMARY KEY (entity_id, bucket)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS checkpoint (
    key      TEXT    NOT NULL PRIMARY KEY,
    at       INTEGER NOT NULL,
    snapshot TEXT    NOT NULL
) WITHOUT ROWID;
"""
"""Zeitstempel sind Unix-Millisekunden in UTC.

Kapitel 16 §85 verlangt, dass Reisen zwischen Zeitzonen die Historie nicht
zerstören. Eine lokale Zeit in der Datenbank täte genau das: Dieselbe Stunde
käme zweimal vor oder fehlte, sobald das Fahrzeug eine Zeitzone wechselt.
Umgerechnet wird erst bei der Anzeige.

``WITHOUT ROWID`` ist kein Feinschliff: Der Primärschlüssel ist genau die
Zugriffsart — eine Entity über einen Zeitraum. Damit liegen die Zeilen einer
Entity physisch beieinander, und ein Kurvenausschnitt ist ein
zusammenhängender Bereichsscan statt vieler Einzelzugriffe.
"""

MINUTE_MS = 60_000
HOUR_MS = 3_600_000


@dataclass
class Retention:
    """Wie lange welche Auflösung aufbewahrt wird (Kapitel 16 §9).

    Die Voreinstellungen sind eine begründete Vorgabe und keine Festlegung:
    Kapitel 6 §23 vertagt die endgültigen Fristen ausdrücklich, verlangt aber
    Vorgaben. Sie stehen in der Konfiguration und lassen sich ändern, ohne
    Code anzufassen.
    """

    raw_days: int = 7
    """Rohdaten. Beantwortet „was war letzte Nacht" in voller Auflösung."""

    minute_days: int = 60
    """Minutenwerte. Beantwortet „wie war die letzte Reise"."""

    hour_days: int = 1095
    """Stundenwerte, drei Jahre. Beantwortet „wie war der letzte Sommer" —
    und ist mit rund 26 000 Zeilen je Entity und Jahr klein genug, dass die
    Frage nach dem Speicherplatz sich nicht stellt."""


@dataclass
class Point:
    """Ein Punkt einer Kurve.

    ``value is None`` heißt: Zu diesem Zeitpunkt war kein belastbarer Wert
    bekannt. Das ist eine Aussage und kein fehlendes Feld — deshalb wird der
    Punkt überhaupt übertragen.
    """

    at: int
    value: float | None
    quality: str


@dataclass
class Series:
    entity_id: str
    resolution: str
    points: list[Point]
    """Aufsteigend nach Zeit. Nicht aufgefüllt — siehe Kopf dieser Datei."""


@dataclass(frozen=True)
class Checkpoint:
    """Persistenter Startpunkt einer abgeleiteten Auswertung."""

    at: int
    snapshot: dict[str, float | None]


@dataclass
class _Last:
    """Was zuletzt für eine Entity geschrieben wurde."""

    at: int
    value: float | None
    quality: Quality


class HistoryStore:
    """Schreibt die Messhistorie und liest sie wieder.

    Ein Ausfall darf die Fahrzeugsteuerung nicht mitreißen (Kapitel 16 §88).
    Deshalb liegt die Historie in einer eigenen Datei, läuft als überwachter
    Dienst mit eigener Fehlergrenze — und deshalb fängt diese Klasse
    Datenbankfehler ab, statt sie nach oben durchzureichen: Ein voller
    Datenträger soll die Wasserpumpe nicht abschalten.
    """

    def __init__(
        self,
        database: Database,
        state: StateStore,
        registry: Registry,
        *,
        retention: Retention | None = None,
        heartbeat_s: float = 300.0,
    ) -> None:
        self._database = database
        self._state = state
        self._registry = registry
        self._retention = retention or Retention()
        self._heartbeat_ms = int(heartbeat_s * 1000)
        self._last: dict[str, _Last] = {}
        self._degraded = False

    # ── Aufbau ──────────────────────────────────────────────────────────────

    async def start(self) -> None:
        await self._database.open()
        await self._database.run(lambda c: c.executescript(SCHEMA))

    async def stop(self) -> None:
        await self._database.close()

    @property
    def degraded(self) -> bool:
        """Ob das Aufzeichnen gerade nicht funktioniert.

        Die Oberfläche kann damit sagen „Historie nicht verfügbar" statt eine
        leere Kurve zu zeigen, die wie „nichts passiert" aussieht
        (Kapitel 16 §79).
        """
        return self._degraded

    # ── Schreiben ───────────────────────────────────────────────────────────

    async def record(self, now_ms: int | None = None) -> int:
        """Schreibt einen Durchlauf über alle aufzeichnungswürdigen Entities.

        Gibt die Zahl der geschriebenen Punkte zurück — null ist der Normalfall
        bei ruhiger Anlage und kein Fehler.
        """
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        rows = self._due(now)
        if not rows:
            return 0

        def write(connection: sqlite3.Connection) -> None:
            connection.execute("BEGIN")
            connection.executemany(
                "INSERT OR REPLACE INTO sample (entity_id, at, value, quality) "
                "VALUES (?, ?, ?, ?)",
                rows,
            )
            connection.execute("COMMIT")

        try:
            await self._database.run(write)
        except sqlite3.Error:
            # Bewusst nicht weitergereicht: Die Historie ist eine
            # Aufzeichnung, kein Steuerpfad.
            if not self._degraded:
                log.exception("Historie kann nicht schreiben — Aufzeichnung ausgesetzt")
            self._degraded = True
            return 0

        self._degraded = False
        for entity_id, at, value, quality in rows:
            self._last[entity_id] = _Last(at=at, value=value, quality=Quality(quality))
        return len(rows)

    def _due(self, now: int) -> list[tuple[str, int, float | None, str]]:
        """Welche Entities gerade einen Punkt verdienen."""
        rows: list[tuple[str, int, float | None, str]] = []

        for entity in self._registry:
            if not _records(entity.unit):
                continue

            current = self._state.get(entity.id)
            if current is None:
                continue

            quality = current.state.quality
            value = _numeric(current.state.value, quality)

            if self._is_due(entity.id, now, value, quality, entity.deadband):
                rows.append((entity.id, now, value, quality.value))

        return rows

    def _is_due(
        self,
        entity_id: str,
        now: int,
        value: float | None,
        quality: Quality,
        deadband: float,
    ) -> bool:
        """Die drei Bedingungen aus Kapitel 16 §8, einzeln benannt.

        Bewusst als Kette früher Rückgaben und nicht als eine
        zusammengezogene Bedingung: Jede der drei hat einen eigenen Grund, und
        wer später eine davon ändert, soll sehen, welche.
        """
        last = self._last.get(entity_id)

        # Der erste Punkt überhaupt.
        if last is None:
            return True

        # Qualitätswechsel. Der Übergang von „gültig" zu „unbekannt" ist die
        # wichtigste Information der ganzen Kurve — er markiert den Anfang
        # einer Lücke und darf nie durch ein Deadband verschluckt werden.
        if quality is not last.quality:
            return True

        # Herzschlag. Ohne ihn wäre „konstant" von „System war aus" nicht zu
        # unterscheiden.
        if now - last.at >= self._heartbeat_ms:
            return True

        # Ab hier: gleiche Qualität, kein Herzschlag fällig. Sind beide Werte
        # unbelastbar, gibt es nichts Neues zu sagen.
        if value is None or last.value is None:
            return False

        # Wertänderung, gemessen am Deadband der Entity — derselben Zahl, mit
        # der schon der State Store arbeitet.
        return abs(value - last.value) > deadband

    # ── Verdichten und Aufräumen ────────────────────────────────────────────

    async def compact(self, now_ms: int | None = None) -> None:
        """Bildet Minuten- und Stundenwerte und wirft Abgelaufenes weg.

        Die Verdichtung ist ausdrücklich vorberechnet und nicht bei jeder
        Abfrage gerechnet (ADR 0004): Auf einem Fahrzeugrechner ist eine Kurve
        über drei Jahre sonst eine Sekundenangelegenheit statt einer
        Millisekundenangelegenheit.
        """
        now = now_ms if now_ms is not None else int(time.time() * 1000)

        def work(connection: sqlite3.Connection) -> None:
            connection.execute("BEGIN")
            _rollup(connection, "rollup_minute", MINUTE_MS, now)
            _rollup(connection, "rollup_hour", HOUR_MS, now)

            connection.execute(
                "DELETE FROM sample WHERE at < ?",
                (now - self._retention.raw_days * 86_400_000,),
            )
            connection.execute(
                "DELETE FROM rollup_minute WHERE bucket < ?",
                (now - self._retention.minute_days * 86_400_000,),
            )
            connection.execute(
                "DELETE FROM rollup_hour WHERE bucket < ?",
                (now - self._retention.hour_days * 86_400_000,),
            )
            connection.execute("COMMIT")

        try:
            await self._database.run(work)
        except sqlite3.Error:
            log.exception("Historie konnte nicht verdichtet werden")

    # ── Lesen ───────────────────────────────────────────────────────────────

    async def series(self, entity_id: str, since_ms: int, until_ms: int) -> Series:
        """Eine Kurve im gewünschten Zeitraum.

        Die Auflösung wird aus der Spanne abgeleitet und nicht vom Client
        gewählt: Wer drei Jahre anfragt, will keine 50 Millionen Rohpunkte, und
        wer zehn Minuten anfragt, will keine Stundenmittel. Die getroffene Wahl
        steht im Ergebnis, damit die Oberfläche sie benennen kann.
        """
        span = max(0, until_ms - since_ms)
        if span <= 6 * HOUR_MS:
            table, resolution = None, "raw"
        elif span <= 14 * 24 * HOUR_MS:
            table, resolution = "rollup_minute", "minute"
        else:
            table, resolution = "rollup_hour", "hour"

        def read(connection: sqlite3.Connection) -> list[Point]:
            if table is None:
                rows = connection.execute(
                    "SELECT at, value, quality FROM sample "
                    "WHERE entity_id = ? AND at >= ? AND at <= ? ORDER BY at",
                    (entity_id, since_ms, until_ms),
                ).fetchall()
                return [Point(r["at"], r["value"], r["quality"]) for r in rows]

            rows = connection.execute(
                f"SELECT bucket, n, avg_value FROM {table} "  # noqa: S608 — feste Namen
                "WHERE entity_id = ? AND bucket >= ? AND bucket <= ? ORDER BY bucket",
                (entity_id, since_ms, until_ms),
            ).fetchall()
            # Ein Eimer ohne belastbaren Wert bleibt ein Loch und wird nicht
            # mit dem Mittel der Nachbarn gefüllt.
            return [
                Point(
                    r["bucket"],
                    r["avg_value"] if r["n"] > 0 else None,
                    Quality.VALID.value if r["n"] > 0 else Quality.UNKNOWN.value,
                )
                for r in rows
            ]

        try:
            points = await self._database.run(read)
        except sqlite3.Error:
            log.exception("Historie konnte nicht gelesen werden")
            self._degraded = True
            points = []

        return Series(entity_id=entity_id, resolution=resolution, points=points)



    # ── Persistente Auswertungs-Checkpoints ──────────────────────────────

    async def checkpoint(
        self,
        key: str,
    ) -> Checkpoint | None:
        """Liest den gespeicherten Startpunkt einer Auswertung."""

        def read(
            connection: sqlite3.Connection,
        ) -> sqlite3.Row | None:
            return connection.execute(
                "SELECT at, snapshot FROM checkpoint WHERE key = ?",
                (key,),
            ).fetchone()

        try:
            row = await self._database.run(read)
        except sqlite3.Error as error:
            self._degraded = True
            log.exception("Checkpoint konnte nicht gelesen werden")
            raise RuntimeError(
                "Historie nicht verfügbar"
            ) from error

        if row is None:
            return None

        try:
            raw = json.loads(row["snapshot"])

            if not isinstance(raw, dict):
                raise ValueError("Snapshot ist kein Objekt")

            snapshot = {
                str(entity_id): (
                    None
                    if value is None
                    else float(value)
                )
                for entity_id, value in raw.items()
            }
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            log.exception("Checkpoint ist beschädigt")
            raise RuntimeError(
                "Checkpoint ist beschädigt"
            ) from error

        return Checkpoint(
            at=int(row["at"]),
            snapshot=snapshot,
        )

    async def set_checkpoint(
        self,
        key: str,
        snapshot: dict[str, float | None],
        *,
        now_ms: int | None = None,
    ) -> Checkpoint:
        """Setzt einen Checkpoint atomar neu."""

        at = (
            int(time.time() * 1000)
            if now_ms is None
            else now_ms
        )

        payload = json.dumps(
            snapshot,
            separators=(",", ":"),
            sort_keys=True,
        )

        def write(connection: sqlite3.Connection) -> None:
            connection.execute(
                """
                INSERT INTO checkpoint (key, at, snapshot)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    at = excluded.at,
                    snapshot = excluded.snapshot
                """,
                (key, at, payload),
            )

        try:
            await self._database.run(write)
        except sqlite3.Error as error:
            self._degraded = True
            log.exception("Checkpoint konnte nicht gespeichert werden")
            raise RuntimeError(
                "Historie nicht verfügbar"
            ) from error

        self._degraded = False

        return Checkpoint(
            at=at,
            snapshot=dict(snapshot),
        )


def _rollup(connection: sqlite3.Connection, table: str, width: int, now: int) -> None:
    """Verdichtet abgeschlossene Zeitfenster.

    Der laufende Eimer bleibt ausgespart: Ihn zu verdichten hieße, ein
    unvollständiges Mittel als endgültig abzulegen — und beim nächsten Lauf
    stünde ein anderer Wert dort, ohne dass sich etwas geändert hätte.
    """
    boundary = (now // width) * width

    connection.execute(
        f"INSERT OR REPLACE INTO {table} "  # noqa: S608 — feste Namen
        "(entity_id, bucket, n, min_value, max_value, avg_value) "
        "SELECT entity_id, (at / ?) * ?, "
        "       COUNT(value), MIN(value), MAX(value), AVG(value) "
        "FROM sample WHERE at < ? "
        "GROUP BY entity_id, at / ?",
        (width, width, boundary, width),
    )


def _records(unit: str | None) -> bool:
    """Ob eine Entity in die Messhistorie gehört.

    Kapitel 16 §4 zählt Messgrößen auf — Ladezustand, Spannung, Füllstände,
    Temperaturen. Alle haben eine Einheit. Ein Türkontakt oder eine
    Brennerphase hat keine, und ihre Historie ist eine Ereignisliste und keine
    Kurve (Kapitel 16 §7). Die entsteht getrennt; sie hier als Zahlenreihe zu
    führen, hieße einen Zustand in einen Messwert zu verwandeln.
    """
    return unit is not None


def _numeric(value: object, quality: Quality) -> float | None:
    """Der Zahlenwert — oder ``None``, wenn er nicht belastbar ist.

    ``STALE`` behält seinen Wert, wie überall im System: alt, aber echt. Alles
    andere außer ``VALID`` hat ohnehin keinen.
    """
    if quality not in (Quality.VALID, Quality.STALE):
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)
