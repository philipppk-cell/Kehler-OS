"""Ableitung von Warnungen aus dem Systemzustand.

Bewusst im Backend, nicht in der Oberfläche: Die Bewertung, ob etwas eine
Warnung ist, ist Geschäftslogik und gehört nicht ins Frontend
(Kapitel 4, Kapitel 18 §6).

**Was hier bewertet wird**, ist ausschließlich, was das System sicher weiß:
Sensordefekte, unerreichbare Geräte, unbekannte Zustände, fehlende
Konfiguration.

**Was hier bewusst nicht bewertet wird**, sind Schwellenwarnungen wie
„Grauwasser zu voll“. Die Schwellen sind eine offene Frage (Punkt C3), und
Kapitel 18 §98 verbietet, sie zu erfinden. Sobald sie konfiguriert sind,
kommen sie hier dazu — nicht vorher.
"""

from __future__ import annotations

from ..domain.enums import AlertState, LinkState, Quality, Severity
from ..domain.models import Alert
from .registry import Registry
from .state_store import StateStore

_UNREACHABLE = frozenset({LinkState.OFFLINE, LinkState.ERROR})


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
