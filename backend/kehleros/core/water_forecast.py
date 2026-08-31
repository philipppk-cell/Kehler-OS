"""Verbrauchs- und Reichweitenprognose für die Wassertanks.

Die Prognose betrachtet ausschließlich gerichtete Änderungen:

* Frischwasser: nur sinkende Füllstände sind Verbrauch.
  Befüllungen werden ignoriert.
* Abwasser: nur steigende Füllstände sind Nutzung.
  Eine Entleerung wird ignoriert.

Die Berechnung beginnt an einem vom Benutzer gesetzten Checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .history import HOUR_MS, MINUTE_MS, Point

DAY_MS = 24 * HOUR_MS

MIN_OBSERVED_MS = 2 * HOUR_MS
"""Mindestens zwei Stunden Beobachtungszeit für eine Prognose."""

MIN_CHANGE_L = 5.0
"""Mindestens fünf Liter erkannte Änderung gegen Sensorrauschen."""

MAX_GAP_MS = 90 * MINUTE_MS
"""Größere Datenlücken werden nicht als beobachtete Zeit gerechnet."""

MIN_STEP_PERCENT = 0.5
"""Entspricht dem Deadband der realen Tanksensoren."""


Direction = Literal["down", "up"]


@dataclass(frozen=True)
class Change:
    litres: float = 0.0
    observed_ms: int = 0


@dataclass(frozen=True)
class ForecastMetric:
    ready: bool
    rate_l_day: float | None
    remaining_days: float | None
    observed_hours: float
    change_l: float


def directional_change(
    *,
    started_at: int,
    now_ms: int,
    start_percent: float | None,
    current_percent: float | None,
    capacity_l: float | None,
    points: list[Point],
    direction: Direction,
) -> Change:
    """Erkannte Änderung eines Tanks seit dem Checkpoint."""

    if capacity_l is None or capacity_l <= 0:
        return Change()

    previous_value = _percent(start_percent)
    previous_at: int | None = (
        started_at
        if previous_value is not None
        else None
    )

    change_l = 0.0
    observed_ms = 0

    samples: list[tuple[int, float | None]] = [
        (point.at, point.value)
        for point in points
        if started_at < point.at <= now_ms
    ]

    # Der Live-Wert schließt die Historie bis "jetzt" ab.
    samples.append((now_ms, current_percent))

    for at, raw_value in samples:
        value = _percent(raw_value)

        # Eine Datenlücke bleibt auch für die Prognose eine Lücke.
        if value is None:
            previous_value = None
            previous_at = None
            continue

        if previous_value is not None and previous_at is not None:
            gap = at - previous_at

            if 0 < gap <= MAX_GAP_MS:
                observed_ms += gap

                delta = value - previous_value
                directional = (
                    -delta
                    if direction == "down"
                    else delta
                )

                if directional > MIN_STEP_PERCENT:
                    change_l += (
                        directional
                        * capacity_l
                        / 100.0
                    )

        previous_value = value
        previous_at = at

    return Change(
        litres=max(0.0, change_l),
        observed_ms=max(0, observed_ms),
    )


def forecast_metric(
    changes: list[Change],
    *,
    remaining_l: float | None,
) -> ForecastMetric:
    """Erzeugt Rate und Restdauer aus einer oder mehreren Tankänderungen."""

    change_l = sum(change.litres for change in changes)

    # Bei zwei Frischwassertanks läuft dieselbe Zeit parallel.
    # Die Zeiten dürfen deshalb nicht addiert werden.
    observed_ms = max(
        (change.observed_ms for change in changes),
        default=0,
    )

    rate_l_day: float | None = None

    if observed_ms > 0 and change_l > 0:
        rate_l_day = (
            change_l
            * DAY_MS
            / observed_ms
        )

    ready = (
        remaining_l is not None
        and observed_ms >= MIN_OBSERVED_MS
        and change_l >= MIN_CHANGE_L
        and rate_l_day is not None
        and rate_l_day > 0
    )

    remaining_days: float | None = None

    if ready and rate_l_day is not None:
        remaining_days = max(
            0.0,
            remaining_l / rate_l_day,
        )

    return ForecastMetric(
        ready=ready,
        rate_l_day=rate_l_day,
        remaining_days=remaining_days,
        observed_hours=observed_ms / HOUR_MS,
        change_l=change_l,
    )


def _percent(value: float | None) -> float | None:
    if value is None:
        return None

    number = float(value)

    if number < 0.0 or number > 100.0:
        return None

    return number
