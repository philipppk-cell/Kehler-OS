"""Die Wasserzusammenfassung.

Geprüft wird vor allem, wann es **keinen** Gesamtstand gibt. Genau das ist
die Regel, die leicht verlorengeht: Ein halber Gesamtstand sieht aus wie ein
ganzer.
"""

from __future__ import annotations

import pytest

from kehleros.core.water import summarise
from kehleros.domain.enums import Quality, Source
from kehleros.domain.models import Entity, EntityState, StateValue


def tank(entity_id: str, name_key: str, capacity: float | None) -> Entity:
    return Entity(
        id=entity_id,
        name_key=name_key,
        unit="percent",
        capacity_l=capacity,
    )


def state(entity_id: str, value: float | None, quality: Quality) -> EntityState:
    return EntityState(
        entity_id=entity_id,
        state=StateValue(
            value=value,
            unit="percent",
            quality=quality,
            source=Source.SIMULATION,
        ),
    )


@pytest.fixture
def registry() -> list[Entity]:
    return [
        tank("water.tank.fresh.large", "tank.fresh_large", 550),
        tank("water.tank.fresh.small", "tank.fresh_small", 450),
        tank("water.tank.grey", "tank.grey", 280),
        tank("water.tank.black", "tank.black", 370),
    ]


def test_summe_ueber_liter_nicht_ueber_prozent(registry):
    """Der eigentliche Rechenfehler, den diese Datei verhindert.

    Voll (450 l) und leer (550 l) sind zusammen 45 % — nicht 50 %.
    """
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 0.0, Quality.VALID),
        "water.tank.fresh.small": state("water.tank.fresh.small", 100.0, Quality.VALID),
    }

    fresh = summarise(states, registry).fresh

    assert fresh.litres == pytest.approx(450.0)
    assert fresh.capacity_l == pytest.approx(1000.0)
    assert fresh.percent == pytest.approx(45.0)


def test_kein_gesamtstand_wenn_ein_tank_unbekannt(registry):
    """Ein unbekannter Summand macht die ganze Summe unbekannt."""
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 80.0, Quality.VALID),
        "water.tank.fresh.small": state("water.tank.fresh.small", None, Quality.UNKNOWN),
    }

    fresh = summarise(states, registry).fresh

    assert fresh.litres is None
    assert fresh.percent is None
    assert fresh.quality is Quality.UNKNOWN
    # Das Fassungsvermögen bleibt bekannt — es hängt nicht am Sensor.
    assert fresh.capacity_l == pytest.approx(1000.0)


def test_kein_gesamtstand_bei_sensorfehler(registry):
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 80.0, Quality.VALID),
        "water.tank.fresh.small": state("water.tank.fresh.small", None, Quality.ERROR),
    }

    fresh = summarise(states, registry).fresh

    assert fresh.litres is None
    assert fresh.quality is Quality.ERROR


def test_veraltet_bleibt_verwertbar_faerbt_aber_die_summe(registry):
    """STALE ist ein alter, aber echter Wert — die Summe wird deshalb
    gebildet und trägt die schlechtere Qualität weiter."""
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 50.0, Quality.VALID),
        "water.tank.fresh.small": state("water.tank.fresh.small", 50.0, Quality.STALE),
    }

    fresh = summarise(states, registry).fresh

    assert fresh.litres == pytest.approx(500.0)
    assert fresh.quality is Quality.STALE


def test_ohne_kapazitaet_keine_liter():
    """Ohne Kapazität gibt es Prozent, aber keine erfundenen Liter."""
    registry = [tank("water.tank.fresh.large", "x", None)]
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 60.0, Quality.VALID)
    }

    fresh = summarise(states, registry).fresh

    assert fresh.tanks[0].percent == pytest.approx(60.0)
    assert fresh.tanks[0].litres is None
    assert fresh.litres is None


@pytest.mark.parametrize(
    "entity_id",
    [
        "water.tank.fresh.large",
        "water.tank.fresh.small",
        "water.tank.grey",
        "water.tank.black",
    ],
)
@pytest.mark.parametrize(
    "reported_percent",
    [100.1, 101.0, 102.0],
)
def test_tankgeber_bis_102_prozent_werden_als_voll_verarbeitet(
    registry,
    entity_id,
    reported_percent,
):
    """Die obere Sensortoleranz gilt für jeden Wassertank."""

    states = {
        entity_id: state(
            entity_id,
            reported_percent,
            Quality.VALID,
        ),
    }

    summary = summarise(states, registry)

    tanks = [
        *summary.fresh.tanks,
        *summary.waste,
    ]

    actual = next(
        tank
        for tank in tanks
        if tank.entity_id == entity_id
    )

    expected_capacity = next(
        entity.capacity_l
        for entity in registry
        if entity.id == entity_id
    )

    assert actual.quality is Quality.VALID
    assert actual.percent == pytest.approx(100.0)
    assert actual.litres == pytest.approx(expected_capacity)


def test_freier_platz_wird_nicht_negativ(registry):
    """Ein Sensor, der über 100 % meldet, darf keinen negativen Restplatz
    erzeugen."""
    states = {
        "water.tank.grey": state("water.tank.grey", 104.0, Quality.VALID),
    }

    waste = summarise(states, registry).waste
    grey = next(t for t in waste if t.entity_id == "water.tank.grey")

    assert grey.free_l == pytest.approx(0.0)


def test_groesster_tank_zuerst(registry):
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 50.0, Quality.VALID),
        "water.tank.fresh.small": state("water.tank.fresh.small", 50.0, Quality.VALID),
    }

    fresh = summarise(states, registry).fresh

    assert [t.entity_id for t in fresh.tanks] == [
        "water.tank.fresh.large",
        "water.tank.fresh.small",
    ]


def test_nicht_konfigurierter_tank_zaehlt_nicht_mit():
    """Ein Tank ohne Hardwarezuordnung darf die Gesamtmenge weder
    vergrößern noch unbekannt machen."""
    registry = [
        tank("water.tank.fresh.large", "a", 550),
        Entity(
            id="water.tank.fresh.small",
            name_key="b",
            unit="percent",
            capacity_l=450,
            configured=False,
        ),
    ]
    states = {
        "water.tank.fresh.large": state("water.tank.fresh.large", 100.0, Quality.VALID),
    }

    fresh = summarise(states, registry).fresh

    assert len(fresh.tanks) == 1
    assert fresh.capacity_l == pytest.approx(550.0)
    assert fresh.litres == pytest.approx(550.0)
