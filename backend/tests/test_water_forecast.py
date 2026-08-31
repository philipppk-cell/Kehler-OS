"""Verbrauchs- und Reichweitenberechnung der Wassertanks."""

from kehleros.core.history import HOUR_MS, Point
from kehleros.core.water_forecast import (
    directional_change,
    forecast_metric,
)


def point(hour: float, value: float | None) -> Point:
    return Point(
        at=int(hour * HOUR_MS),
        value=value,
        quality=(
            "VALID"
            if value is not None
            else "UNKNOWN"
        ),
    )


def test_frischwasser_befuellung_wird_nicht_als_verbrauch_gerechnet():
    change = directional_change(
        started_at=0,
        now_ms=3 * HOUR_MS,
        start_percent=80.0,
        current_percent=60.0,
        capacity_l=550.0,
        points=[
            point(0.5, 70.0),
            point(1.0, 40.0),
            # Befüllung: darf den Verbrauch nicht rückwärts rechnen.
            point(1.5, 80.0),
            point(2.0, 70.0),
        ],
        direction="down",
    )

    # 80→70 + 70→40 + 80→70 + 70→60 = 60 Prozentpunkte.
    assert change.litres == 330.0


def test_abwasser_entleerung_wird_ignoriert():
    change = directional_change(
        started_at=0,
        now_ms=3 * HOUR_MS,
        start_percent=20.0,
        current_percent=30.0,
        capacity_l=280.0,
        points=[
            point(0.5, 40.0),
            # Entleerung.
            point(1.0, 10.0),
            point(2.0, 20.0),
        ],
        direction="up",
    )

    # 20→40 + 10→20 + 20→30 = 40 Prozentpunkte.
    assert change.litres == 112.0


def test_prognose_wartet_auf_genug_daten():
    metric = forecast_metric(
        [
            type(
                "Change",
                (),
                {
                    "litres": 20.0,
                    "observed_ms": HOUR_MS,
                },
            )()
        ],
        remaining_l=400.0,
    )

    assert metric.ready is False
    assert metric.remaining_days is None
