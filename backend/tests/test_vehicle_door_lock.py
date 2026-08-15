"""Bestätigte Fähigkeiten der Terrassentür-Zentralverriegelung."""

from pathlib import Path

from kehleros.config.loader import build_entities, load_vehicle

REPO = Path(__file__).resolve().parents[2]


def test_terrassentuer_zv_hat_open_close_ohne_feedback() -> None:
    vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
    entities = {entity.id: entity for entity in build_entities(vehicle)}

    lock = entities["vehicle.door.main.lock"]

    assert lock.kind == "lock"
    assert lock.feedback is False
    assert set(lock.capabilities) == {"open", "close"}
