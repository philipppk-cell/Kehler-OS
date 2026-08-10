"""Die Aufzählungen, mit denen das gesamte System arbeitet.

Diese Werte sind technische Identitäten, keine Anzeigetexte. Die Oberfläche
übersetzt sie über i18n-Schlüssel — Programmlogik hängt niemals an einem
sichtbaren Text (Kapitel 13 §76).
"""

from __future__ import annotations

from enum import StrEnum


class Quality(StrEnum):
    """Wie belastbar ein Wert ist.

    ``UNKNOWN`` ist ein echter Zustand und bedeutet niemals ``0``, ``OFF``
    oder ``CLOSED`` (Kapitel 5 §19, Kapitel 18 §38).
    """

    VALID = "VALID"
    """Aktueller, plausibler Messwert."""

    STALE = "STALE"
    """War gültig, wurde aber länger nicht aktualisiert als erwartet."""

    UNKNOWN = "UNKNOWN"
    """Der tatsächliche Zustand ist derzeit nicht bekannt."""

    INVALID = "INVALID"
    """Wert vorhanden, aber außerhalb des zulässigen Bereichs."""

    ERROR = "ERROR"
    """Sensor oder Kanal meldet einen Fehler."""

    @property
    def is_usable(self) -> bool:
        """Ob der Wert als Grundlage für Anzeige und Automatisierung taugt."""
        return self is Quality.VALID


class Source(StrEnum):
    """Woher ein Wert stammt.

    ``KEHLER_OS`` kennzeichnet berechnete Werte. Sie dürfen nie als direkte
    Messwerte erscheinen (Kapitel 13 §38/§39).
    """

    PLC = "PLC"
    VICTRON = "VICTRON"
    SENSOR = "SENSOR"
    KEHLER_OS = "KEHLER_OS"
    USER = "USER"
    AUTOMATION = "AUTOMATION"
    SIMULATION = "SIMULATION"

    @property
    def is_simulated(self) -> bool:
        return self is Source.SIMULATION


class LinkState(StrEnum):
    """Verbindungszustand eines Geräts oder Adapters (Kapitel 11 §16)."""

    INITIALIZING = "INITIALIZING"
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    RECONNECTING = "RECONNECTING"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    """Gerät ist vorgesehen, aber nicht vollständig konfiguriert.

    Die Oberfläche zeigt dann „Nicht konfiguriert“ statt eines erfundenen
    Zustands (Kapitel 12 §68, Kapitel 18 §101).
    """


class CommandPhase(StrEnum):
    """Lebenszyklus eines Befehls (Kapitel 13 §16, Kapitel 18 §36)."""

    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    REJECTED = "REJECTED"

    SUPERSEDED = "SUPERSEDED"
    """Ein anderer Befehl hat übernommen — typisch: Stopp während der Fahrt.

    Bewusst **kein** Fehler. Wer ein fahrendes Tor anhält, hat genau das
    erreicht, was er wollte; eine Fehlermeldung dafür wäre eine Belehrung.
    Erfolgreich ist der abgelöste Befehl trotzdem nicht — er hat sein Ziel
    nicht erreicht, und das bleibt sichtbar (Kapitel 18 §20).
    """

    @property
    def is_final(self) -> bool:
        return self in _FINAL_PHASES

    @property
    def is_success(self) -> bool:
        return self is CommandPhase.COMPLETED


_FINAL_PHASES = frozenset(
    {
        CommandPhase.COMPLETED,
        CommandPhase.FAILED,
        CommandPhase.TIMEOUT,
        CommandPhase.REJECTED,
        # Abgelöst ist endgültig: Der Befehl wurde von einem Stopp beendet
        # und läuft nicht weiter. Ihn hier auszulassen hieße, dass
        # `is_final` bei genau der Phase falsch antwortet, die zuletzt
        # dazugekommen ist.
        CommandPhase.SUPERSEDED,
    }
)


class RejectionReason(StrEnum):
    """Warum ein Befehl abgewiesen wurde — vor jedem Hardwarekontakt.

    Die Oberfläche macht daraus eine verständliche Meldung; der technische
    Grund bleibt für Diagnose und Audit erhalten (Kapitel 17 §22).
    """

    UNKNOWN_ENTITY = "UNKNOWN_ENTITY"
    UNSUPPORTED_VERB = "UNSUPPORTED_VERB"
    MISSING_CAPABILITY = "MISSING_CAPABILITY"
    INVALID_PARAMS = "INVALID_PARAMS"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    DEVICE_UNAVAILABLE = "DEVICE_UNAVAILABLE"
    BUSY = "BUSY"
    """Für diese Entity läuft bereits ein Befehl (Kapitel 13 §21)."""

    SAFETY_CONDITION = "SAFETY_CONDITION"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    SERVICE_MODE = "SERVICE_MODE"


class Trigger(StrEnum):
    """Wodurch eine Aktion ausgelöst wurde (Kapitel 9 §46, Kapitel 13 §72)."""

    USER = "USER"
    AUTOMATION = "AUTOMATION"
    SYSTEM = "SYSTEM"
    AI = "AI"


class Severity(StrEnum):
    """Dringlichkeit von Ereignissen und Warnungen (Kapitel 8 §9)."""

    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertState(StrEnum):
    """Lebenszyklus einer Warnung.

    Quittieren ist nicht Beheben: Eine quittierte Warnung bleibt technisch
    aktiv, solange die Ursache besteht (Kapitel 13 §44).
    """

    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class SystemHealth(StrEnum):
    """Aggregierter Gesamtzustand (Kapitel 13 §53).

    ``CRITICAL`` ist bewusst sparsam zu verwenden — zu viele kritische
    Meldungen entwerten die Priorität (Kapitel 13 §55).
    """

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    INITIALIZING = "INITIALIZING"


class Environment(StrEnum):
    """Betriebsart. Wird beim Start festgelegt und ist zur Laufzeit nicht
    umschaltbar (Kapitel 15 §96, Kapitel 18 §68)."""

    DEVELOPMENT = "development"
    SIMULATION = "simulation"
    PRODUCTION = "production"

    @property
    def allows_real_hardware(self) -> bool:
        return self is Environment.PRODUCTION


class VehicleMode(StrEnum):
    """Übergeordneter Betriebszustand (Kapitel 14 §31).

    ``DRIVING`` wird nur dann automatisch gesetzt, wenn eine reale Datenquelle
    konfiguriert ist. Ohne sie bleibt der Modus manuell — geraten wird nicht
    (Kapitel 14 §35).
    """

    PARKED = "PARKED"
    CAMPING = "CAMPING"
    NIGHT = "NIGHT"
    DRIVING = "DRIVING"
    SERVICE = "SERVICE"


class Risk(StrEnum):
    """Sicherheitsrelevanz einer Aktion (Kapitel 15 §21).

    Ab ``HIGH`` ist eine bewusste Bestätigung erforderlich. Das ersetzt keine
    technische Schutzfunktion — die Oberfläche ist keine Sicherheitseinrichtung
    (Kapitel 15 §24).
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def needs_confirmation(self) -> bool:
        return self in (Risk.HIGH, Risk.CRITICAL)
