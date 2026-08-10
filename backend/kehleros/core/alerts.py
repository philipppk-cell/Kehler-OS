"""Ableitung von Warnungen aus dem Systemzustand.

Bewusst im Backend, nicht in der Oberfläche: Die Bewertung, ob etwas eine
Warnung ist, ist Geschäftslogik und gehört nicht ins Frontend
(Kapitel 4, Kapitel 18 §6).

**Was hier bewertet wird**, ist ausschließlich, was das System sicher weiß:
Sensordefekte, unerreichbare Geräte, verstummte Sensoren, fehlende
Konfiguration — und überschrittene Schwellen, **soweit sie konfiguriert
sind**.

Der letzte Halbsatz ist die eigentliche Regel: Es gibt keine eingebauten
Schwellen. Steht in der Konfiguration keine, wird für diesen Wert nicht
gewarnt. Eine erfundene Schwelle wäre eine Aussage über das Fahrzeug, die
niemand getroffen hat (Kapitel 18 §98).
"""

from __future__ import annotations

from ..domain.enums import AlertState, LinkState, Quality, Severity
from ..domain.models import Alert, Entity
from .registry import Registry
from .state_store import StateStore

_UNREACHABLE = frozenset({LinkState.OFFLINE, LinkState.ERROR})
_USABLE = frozenset({Quality.VALID, Quality.STALE})


def _threshold_alerts(entity: Entity, value: object) -> list[Alert]:
    """Warnungen aus den konfigurierten Schwellen.

    **Es gibt nur Schwellen, die jemand festgelegt hat.** Fehlt eine, wird
    nicht gewarnt — und keine erfunden (Kapitel 18 §98). Deshalb prüft diese
    Funktion ausschließlich Felder, die in der Konfiguration stehen.

    Die Richtung steckt in der Benennung und ist keine Auslegungssache:
    ``warn_below`` für Vorräte, die zur Neige gehen (Frischwasser),
    ``warn_above`` für Behälter, die volllaufen (Grau- und Schwarzwasser).
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return []

    # Gerundet wird vor dem Vergleich, damit die Meldung zu der Zahl passt,
    # die die Oberfläche anzeigt. Andernfalls kann bei 19,6 % eine Warnung
    # „nur noch 20 % — Warnschwelle 20 %" entstehen, die sich selbst
    # widerspricht. Dieselbe Regel gilt in ``core/water.py``.
    value = round(value)

    checks = (
        (
            entity.critical_below,
            value < (entity.critical_below or 0),
            Severity.CRITICAL,
            "alert.levelCriticalLow",
        ),
        (
            entity.critical_above,
            value > (entity.critical_above or 0),
            Severity.CRITICAL,
            "alert.levelCriticalHigh",
        ),
        (
            entity.warn_below,
            value < (entity.warn_below or 0),
            Severity.WARNING,
            "alert.levelLow",
        ),
        (
            entity.warn_above,
            value > (entity.warn_above or 0),
            Severity.WARNING,
            "alert.levelHigh",
        ),
    )

    for threshold, breached, severity, message_key in checks:
        if threshold is None or not breached:
            continue
        # Die kritische Schwelle steht vor der Warnschwelle: Ist beides
        # überschritten, wird nur die schwerere Meldung erzeugt.
        return [
            Alert(
                type="level.threshold",
                entity_id=entity.id,
                severity=severity,
                message_key=message_key,
                params={
                    "name_key": entity.name_key,
                    "threshold": f"{threshold:g}",
                    "value": f"{value:.0f}",
                },
            )
        ]

    return []


BLOCKED = "BLOCKED"
"""Ein bewegliches Teil, das nicht bis zur Endlage gekommen ist.

Der Zustand geht von selbst nicht weg — er bleibt, bis jemand nachsieht.
Genau deshalb gehört er in die Warnungen und nicht nur auf die Fahrzeugseite:
Ein Fahrzeug, dessen Stufe klemmt, ist nicht „in Ordnung".
"""


def _motion_alerts(entity: Entity, value: object) -> list[Alert]:
    """Eine blockierte Mechanik ist eine Warnung, kein bloßer Zustand.

    Sie unterscheidet sich von einem Sensorfehler: Der Wert ist einwandfrei,
    nur die Sache dahinter klemmt. Ohne diese Warnung stünde im Systemstatus
    „Alles in Ordnung", während die Stufe halb ausgefahren feststeckt — genau
    der Widerspruch, den die Zustandsanzeige vermeiden soll (Kapitel 13 §55).
    """
    if value != BLOCKED:
        return []
    return [
        Alert(
            type="motion.blocked",
            entity_id=entity.id,
            severity=Severity.WARNING,
            message_key="alert.motionBlocked",
            params={"name_key": entity.name_key},
        )
    ]


def derive_alerts(state: StateStore, registry: Registry) -> list[Alert]:
    """Erzeugt die aktuell zutreffenden Warnungen.

    Zustandslos: Die Warnungen ergeben sich jedes Mal neu aus dem Zustand.
    Ein Lebenszyklus mit Quittierung folgt mit dem Warnungsdienst in einer
    späteren Phase — bis dahin wäre eine gespeicherte Warnung nur eine
    Scheingenauigkeit.
    """
    alerts: list[Alert] = []

    for entity_state in state:
        entity = registry.get(entity_state.entity_id)
        if entity is None:
            continue

        # Fehlende Hardwarezuordnung ist ein Hinweis, keine Störung. Sie
        # gehört sichtbar gemacht, damit sie nicht vergessen wird.
        if not entity.configured:
            alerts.append(
                Alert(
                    type="system.not_configured",
                    entity_id=entity.id,
                    severity=Severity.INFO,
                    message_key="alert.notConfigured",
                    params={"name_key": entity.name_key},
                    state=AlertState.ACTIVE,
                )
            )
            continue

        if entity_state.link in _UNREACHABLE:
            alerts.append(
                Alert(
                    type="device.unreachable",
                    entity_id=entity.id,
                    severity=Severity.WARNING,
                    message_key="alert.deviceOffline",
                    params={"name_key": entity.name_key},
                )
            )
            continue

        quality = entity_state.state.quality

        if quality in (Quality.ERROR, Quality.INVALID):
            alerts.append(
                Alert(
                    type="sensor.faulty",
                    entity_id=entity.id,
                    severity=Severity.WARNING,
                    message_key="alert.sensorFaulty",
                    params={"name_key": entity.name_key},
                )
            )
        elif quality is Quality.STALE:
            alerts.append(
                Alert(
                    type="sensor.stale",
                    entity_id=entity.id,
                    severity=Severity.NOTICE,
                    message_key="alert.sensorStale",
                    params={"name_key": entity.name_key},
                )
            )

        elif quality is Quality.UNKNOWN and entity_state.state.measured_at:
            # Ein Wert, der einmal da war und weggefallen ist.
            #
            # Die Bedingung `measured_at` ist der ganze Punkt: Beim Start ist
            # alles unbekannt, weil noch nichts gemeldet wurde — daraus eine
            # Warnung je Entity zu machen, wäre eine Wand aus Meldungen ohne
            # Aussage. Ein Sensor dagegen, der geliefert hat und dann
            # verstummt ist, trägt einen Messzeitpunkt. Das ist der Fall, der
            # gemeldet gehört (Kapitel 13 §9).
            alerts.append(
                Alert(
                    type="sensor.lost",
                    entity_id=entity.id,
                    severity=Severity.WARNING,
                    message_key="alert.sensorLost",
                    params={"name_key": entity.name_key},
                )
            )

        # Schwellen werden nur an einem Wert geprüft, den es gibt. Ein
        # veralteter Wert zählt dabei mit: Ein Tank, der vor fünf Minuten bei
        # 8 % stand, ist auch jetzt noch fast leer. Die Unsicherheit meldet
        # bereits die Warnung darüber.
        if quality in _USABLE:
            alerts.extend(_threshold_alerts(entity, entity_state.state.value))
            alerts.extend(_motion_alerts(entity, entity_state.state.value))

    # Wichtigstes zuerst — das Dashboard zeigt oben, was zählt
    # (Kapitel 8 §9).
    order = {
        Severity.CRITICAL: 0,
        Severity.WARNING: 1,
        Severity.NOTICE: 2,
        Severity.INFO: 3,
    }
    alerts.sort(key=lambda alert: order[alert.severity])
    return alerts
