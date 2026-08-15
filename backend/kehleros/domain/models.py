"""Die Kernobjekte von Kehler OS: Zustandswert, Entity, Befehl, Ereignis, Warnung.

Bewusst als schlanke, unveränderliche Dataclasses gehalten. Sie werden auf
jedem Sensorzyklus erzeugt und liegen damit im heißen Pfad; die Validierung
von außen kommender Daten geschieht an der Systemgrenze (Konfiguration und
API), nicht hier.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Any

from .enums import (
    AlertState,
    CommandPhase,
    LinkState,
    Quality,
    RejectionReason,
    Risk,
    Severity,
    Source,
    Trigger,
)


def utcnow() -> datetime:
    """Alle internen Zeitstempel sind UTC.

    Die Oberfläche stellt lokal dar. So beschädigt ein Zeitzonenwechsel
    während der Fahrt die Historie nicht (Kapitel 16 §83/§84).
    """
    return datetime.now(UTC)


def new_id() -> str:
    return uuid.uuid4().hex


_WITHOUT_VALUE = frozenset({Quality.UNKNOWN, Quality.INVALID, Quality.ERROR})
"""Qualitäten, die keinen Zahlenwert tragen dürfen.

Sie alle bedeuten „hier liegt nichts Belastbares vor". ``STALE`` fehlt
bewusst — dazu ``StateValue.__post_init__``.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Zustandswert
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class StateValue:
    """Ein Wert mit dem Kontext, der ihn beurteilbar macht.

    Ein nackter Messwert ist wertlos, wenn unklar ist, ob er aktuell und
    gültig ist. Deshalb trägt jeder Wert Qualität, Quelle und Zeitbezug
    (Kapitel 13 §7).
    """

    value: Any = None
    unit: str | None = None
    quality: Quality = Quality.UNKNOWN
    source: Source | None = None
    measured_at: datetime | None = None
    """Wann die Hardware den Wert erfasst hat (Messzeit)."""

    received_at: datetime = field(default_factory=utcnow)
    """Wann Kehler OS ihn erhalten hat (Systemzeit)."""

    def __post_init__(self) -> None:
        # Ein nicht belastbarer Wert darf keinen Zahlenwert vortäuschen.
        # Das ist die technische Durchsetzung von Kapitel 18 §38.
        #
        # ``STALE`` ist ausdrücklich ausgenommen: Es bedeutet „alt, aber
        # echt“. Genau dafür existiert der Zustand neben ``UNKNOWN``. Würde
        # auch er den Wert verwerfen, wären beide inhaltlich gleich und die
        # dreistufige Alterung aus Kapitel 13 §9 (gültig → veraltet →
        # unbekannt) hätte keine mittlere Stufe mehr.
        #
        # Die Kennzeichnung übernimmt die Oberfläche: Ein veralteter Wert
        # wird angezeigt und sichtbar als veraltet markiert.
        if self.quality in _WITHOUT_VALUE and self.value is not None:
            object.__setattr__(self, "value", None)

    # ── Fabriken ────────────────────────────────────────────────────────────

    @classmethod
    def valid(
        cls,
        value: Any,
        *,
        unit: str | None = None,
        source: Source | None = None,
        measured_at: datetime | None = None,
    ) -> StateValue:
        return cls(
            value=value,
            unit=unit,
            quality=Quality.VALID,
            source=source,
            measured_at=measured_at or utcnow(),
        )

    @classmethod
    def unknown(
        cls, *, unit: str | None = None, source: Source | None = None
    ) -> StateValue:
        """Der Zustand ist nicht bekannt — nicht ``0``, nicht ``OFF``."""
        return cls(unit=unit, quality=Quality.UNKNOWN, source=source)

    @classmethod
    def invalid(
        cls, *, unit: str | None = None, source: Source | None = None
    ) -> StateValue:
        """Ein Wert lag vor, war aber außerhalb des zulässigen Bereichs."""
        return cls(unit=unit, quality=Quality.INVALID, source=source)

    @classmethod
    def error(
        cls, *, unit: str | None = None, source: Source | None = None
    ) -> StateValue:
        return cls(unit=unit, quality=Quality.ERROR, source=source)

    # ── Alterung ────────────────────────────────────────────────────────────

    def aged(self, quality: Quality) -> StateValue:
        """Stuft die Qualität herab, ohne den Zeitbezug zu verfälschen.

        Der ursprüngliche ``measured_at`` bleibt erhalten — man muss sehen
        können, wie alt die letzte echte Messung war.

        Der Wert bleibt ebenfalls erhalten; ob er das darf, entscheidet
        ``__post_init__`` anhand der neuen Qualität. Bei ``STALE`` bleibt er,
        bei ``UNKNOWN`` fällt er weg.
        """
        return replace(self, quality=quality)

    def age_seconds(self, now: datetime | None = None) -> float:
        reference = self.measured_at or self.received_at
        return ((now or utcnow()) - reference).total_seconds()

    # ── Vergleich ───────────────────────────────────────────────────────────

    def differs_from(self, other: StateValue | None, *, deadband: float = 0.0) -> bool:
        """Ob eine Änderung übertragen und protokolliert werden sollte.

        Ein Türkontakt, der 60 Sekunden geschlossen bleibt, soll nicht
        sechzig Ereignisse erzeugen (Kapitel 13 §65). Bei analogen Werten
        verhindert das Deadband, dass ein zappelnder Sensor Netz und
        Oberfläche flutet (Kapitel 13 §67).
        """
        if other is None:
            return True
        if self.quality is not other.quality:
            return True
        if self.quality is not Quality.VALID:
            # Zwei unbekannte Werte unterscheiden sich nicht.
            return False
        if deadband > 0 and _both_numeric(self.value, other.value):
            return abs(float(self.value) - float(other.value)) > deadband
        return self.value != other.value


def _both_numeric(a: Any, b: Any) -> bool:
    return isinstance(a, (int, float)) and isinstance(b, (int, float))


# ─────────────────────────────────────────────────────────────────────────────
# Entity
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class CommandSpec:
    """Was ein Befehl tut und unter welchen Bedingungen er zulässig ist."""

    verb: str
    expects: Any = None
    """Fester Zustand, der nach erfolgreicher Ausführung erwartet wird."""

    expects_param: str | None = None
    """Alternativ: Der Zielzustand steht in diesem Befehlsparameter.

    Nötig für idempotente Befehle. ``set_state(ON)`` auf eine bereits
    eingeschaltete Lampe ändert nichts — ohne bekannten Zielwert liefe der
    Befehl in einen Timeout, obwohl der gewünschte Zustand längst erreicht
    ist (Kapitel 13 §33).
    """

    timeout_ms: int = 5000
    """Pro Entity konfiguriert — eine Lampe und ein Hydraulikzylinder haben
    verschiedene physikalische Reaktionszeiten (Kapitel 13 §70)."""

    risk: Risk = Risk.LOW
    params: tuple[str, ...] = ()
    """Erlaubte Parameternamen. Alles andere wird abgewiesen."""

    hold_to_run: bool = False
    """Ob dieser Befehl nur solange aktiv bleiben darf, wie der Benutzer hält."""

    preempts: bool = False
    """Ob dieser Befehl einen laufenden unterbrechen darf.

    Genau ein Fall: der **Stopp**. Ihn mit „es läuft bereits ein Befehl"
    abzuweisen, hieße die Handbremse zu sperren, weil das Fahrzeug fährt
    (Kapitel 13 §21 meint überlagerte *Fahr*befehle, nicht deren Abbruch).
    """

    superseded_states: tuple[str, ...] = ()
    """Zustände, die bedeuten: Ein anderer Befehl hat übernommen.

    Meldet ein Tor `STOPPED`, während `open` noch auf `OPEN` wartet, ist die
    Bewegung beendet — nur eben anders. Ohne diese Angabe liefe der Befehl
    bis zum Timeout und meldete „keine Rückmeldung", obwohl die Hardware sehr
    wohl geantwortet hat.
    """

    failure_states: tuple[str, ...] = ()
    """Zustände, die bedeuten: Die Bewegung ist gescheitert.

    Bei `BLOCKED` sofort zu melden ist der eigentliche Gewinn — sonst steht
    der Benutzer zwanzig Sekunden vor einem klemmenden Garagentor und
    erfährt dann das Falsche.
    """

    def expected_value(self, command: Command) -> Any:
        """Der konkrete Zielzustand dieses Befehls.

        ``None`` heißt: kein vorhersagbarer Zielzustand — dann genügt eine
        bestätigte Änderung.
        """
        if self.expects_param is not None:
            return command.params.get(self.expects_param)
        return self.expects


@dataclass(frozen=True, slots=True)
class Entity:
    """Ein logisches Gerät, wie die Software es kennt.

    Die Capabilities steuern die Oberfläche: Fehlt ``set_brightness``,
    existiert kein Dimmregler — nicht ausgegraut, sondern gar nicht
    (Kapitel 12 §55, Kapitel 13 §60).
    """

    id: str
    name_key: str
    device_id: str | None = None
    area: str | None = None
    commands: tuple[CommandSpec, ...] = ()
    unit: str | None = None
    deadband: float = 0.0
    expected_interval_s: float | None = None
    """Erwartetes Aktualisierungsintervall. Bleibt es aus, altert der Wert
    sichtbar zu ``STALE`` und dann ``UNKNOWN`` (Kapitel 13 §9)."""

    configured: bool = True
    """``False`` heißt: vorgesehen, aber ohne Hardwarezuordnung. Die
    Oberfläche zeigt „Nicht konfiguriert“ (Kapitel 18 §101)."""

    feedback: bool = True
    """Ob die Hardware ihren Zustand zurückmeldet.

    ``False`` heißt: ansteuerbar, aber nicht auslesbar. Der Zustand bleibt
    dann dauerhaft ``UNKNOWN``, und sichtbar ist ausschließlich der zuletzt
    gesendete Befehl — als Befehl gekennzeichnet und nie als Messwert.

    Nicht mit ``configured: False`` zu verwechseln. Dort fehlt die Zuordnung;
    hier ist alles zugeordnet und angeschlossen, es gibt nur nichts zu lesen.
    """

    unverified: bool = False
    """``True`` heißt: Ob die Funktion über die Schnittstelle überhaupt
    verfügbar ist, ist nicht bestätigt.

    Nicht dasselbe wie ``configured: False``. Dort fehlt die Zuordnung, hier
    fehlt die Gewissheit, dass es etwas zuzuordnen gibt.
    """

    capacity_l: float | None = None
    """Nutzbare Kapazität eines Tanks in Litern.

    Ohne Angabe zeigt die Oberfläche ausschließlich Prozent. Eine Kapazität
    wird nicht geschätzt — eine Literzahl ist eine Aussage über das Fahrzeug
    (Kapitel 18 §98).
    """

    capacity_ah: float | None = None
    nominal_voltage: float | None = None
    """Nur für die Batterie. Fehlt eines von beiden, gibt es keine Angabe in
    Kilowattstunden und keine Restlaufzeit — beide wären sonst geraten."""

    kind: str = "measurement"
    """Die Art der Entity, wie sie konfiguriert ist.

    Die Oberfläche braucht sie nicht — sie richtet sich nach den Capabilities
    und bekommt diese Angabe deshalb gar nicht erst. Der Simulator braucht
    sie: ``contact`` und ``status`` sind beide einheitenlos und befehlslos,
    verhalten sich aber verschieden, und ein Brenner, der „CLOSED" meldet,
    wäre kein Prüfbild, sondern ein Fehler in Gestalt eines Zustands.
    """

    states: tuple[str, ...] = ()
    """Die möglichen Zustände eines mehrwertigen Zustands.

    Internes Vokabular von Kehler OS. Die Übersetzung von Rohwerten der
    Hardware auf diese Namen macht der Adapter.
    """

    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None
    """Grenzen eines einstellbaren Wertes.

    Ohne ``max_value`` gibt es keine Bedienung: Eine Strombegrenzung ohne
    Kenntnis der realen Absicherung wäre eine gefährliche Erfindung
    (Kapitel 18 §98/§136).
    """

    warn_below: float | None = None
    """Unterhalb dieses Wertes wird gewarnt — für Vorräte wie Frischwasser."""

    warn_above: float | None = None
    """Oberhalb dieses Wertes wird gewarnt — für Abwasser und Ähnliches."""

    critical_below: float | None = None
    critical_above: float | None = None
    """Kritische Schwellen. Bleiben leer, solange sie nicht festgelegt sind —
    eine kritische Meldung ohne Grundlage entwertet die Priorität
    (Kapitel 13 §55)."""

    @property
    def capabilities(self) -> tuple[str, ...]:
        return tuple(spec.verb for spec in self.commands)

    def spec_for(self, verb: str) -> CommandSpec | None:
        for spec in self.commands:
            if spec.verb == verb:
                return spec
        return None


@dataclass(frozen=True, slots=True)
class EntityState:
    """Der vollständige Zustand einer Entity zu einem Zeitpunkt."""

    entity_id: str
    state: StateValue
    attributes: dict[str, StateValue] = field(default_factory=dict)
    requested: RequestedState | None = None
    link: LinkState = LinkState.UNKNOWN
    seq: int = 0
    """Monoton je Entity. Ein verzögertes Delta kann damit kein bereits
    bestätigtes neueres überschreiben (Kapitel 13 §32)."""


@dataclass(frozen=True, slots=True)
class RequestedState:
    """Der Wunschzustand aus dem letzten Befehl.

    Streng getrennt vom tatsächlichen Zustand. Damit kann die Oberfläche
    „Befehl wird ausgeführt“ zeigen, ohne den Hardwarezustand zu behaupten
    (Kapitel 13 §4, Kapitel 18 §37).
    """

    value: Any
    command_id: str
    since: datetime = field(default_factory=utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Befehl
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class Command:
    """Eine gewünschte Aktion — ausdrücklich kein Zustand (Kapitel 18 §35)."""

    entity_id: str
    verb: str
    params: dict[str, Any] = field(default_factory=dict)
    trigger: Trigger = Trigger.USER
    actor: str | None = None
    """Benutzer- oder Automatisierungskennung."""

    client: str | None = None
    """Gerät, von dem der Befehl kam."""

    id: str = field(default_factory=new_id)
    correlation_id: str = field(default_factory=new_id)
    """Verbindet API-Aufruf, Adapterbefehl, Zustandsänderung und Log zu einer
    nachvollziehbaren Kette (Kapitel 16 §28)."""

    requested_at: datetime = field(default_factory=utcnow)
    phase: CommandPhase = CommandPhase.REQUESTED
    rejection: RejectionReason | None = None
    detail: str | None = None

    ended_state: str | None = None
    """Der Zustand, in dem eine Bewegung tatsächlich geendet ist.

    Nur gesetzt, wenn das Ziel **nicht** erreicht wurde — `STOPPED` bei einer
    Ablösung, `BLOCKED` bei einer Blockade. Damit kann die Oberfläche den
    Grund nennen, statt auf „Befehl konnte nicht ausgeführt werden"
    auszuweichen. `detail` bleibt Rohtext für die Diagnose; dieses Feld ist
    maschinenlesbar (Kapitel 17 §22).
    """
    """Technische Begründung für Diagnose und Audit — nicht für die
    normale Oberfläche (Kapitel 17 §22)."""

    finished_at: datetime | None = None

    @property
    def name(self) -> str:
        return f"{self.entity_id}.{self.verb}"

    @property
    def duration_ms(self) -> float | None:
        if self.finished_at is None:
            return None
        return (self.finished_at - self.requested_at).total_seconds() * 1000

    def reject(self, reason: RejectionReason, detail: str | None = None) -> Command:
        self.phase = CommandPhase.REJECTED
        self.rejection = reason
        self.detail = detail
        self.finished_at = utcnow()
        return self

    def fail(self, phase: CommandPhase, detail: str | None = None) -> Command:
        self.phase = phase
        self.detail = detail
        self.finished_at = utcnow()
        return self

    def complete(self) -> Command:
        self.phase = CommandPhase.COMPLETED
        self.finished_at = utcnow()
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Ereignis und Warnung
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Event:
    """Etwas ist zu einem Zeitpunkt geschehen.

    Ein Ereignis beschreibt einen Zeitpunkt, ein Zustand die Gegenwart. Die
    beiden werden nie vermischt (Kapitel 13 §45).
    """

    type: str
    entity_id: str | None = None
    source: Source | None = None
    severity: Severity = Severity.INFO
    data: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=new_id)
    correlation_id: str | None = None
    occurred_at: datetime = field(default_factory=utcnow)
    recorded_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class Alert:
    """Eine Warnung mit eigenem Lebenszyklus."""

    type: str
    message_key: str
    entity_id: str | None = None
    severity: Severity = Severity.WARNING
    state: AlertState = AlertState.ACTIVE
    params: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=new_id)
    raised_at: datetime = field(default_factory=utcnow)
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    resolved_at: datetime | None = None

    def acknowledge(self, by: str | None) -> Alert:
        """Quittieren ändert die Sichtbarkeit, nicht die Ursache.

        Solange die Ursache besteht, bleibt die Warnung technisch aktiv
        (Kapitel 13 §44).
        """
        if self.state is AlertState.ACTIVE:
            self.state = AlertState.ACKNOWLEDGED
            self.acknowledged_at = utcnow()
            self.acknowledged_by = by
        return self

    def resolve(self) -> Alert:
        self.state = AlertState.RESOLVED
        self.resolved_at = utcnow()
        return self

    @property
    def is_open(self) -> bool:
        return self.state is not AlertState.RESOLVED
