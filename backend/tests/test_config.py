"""Konfiguration.

Eine unbrauchbare Konfiguration muss beim Start auffallen — nicht erst, wenn
ein Befehl ins Leere läuft (Kapitel 12 §68, Kapitel 15 §76).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from kehleros.config.loader import ConfigError, build_entities, load_vehicle
from kehleros.config.models import EntityConfig, VehicleConfig
from kehleros.domain.ids import InvalidEntityId, validate_entity_id

REPO = Path(__file__).resolve().parents[2]


class TestNamenskonvention:
    @pytest.mark.parametrize(
        "entity_id",
        [
            "water.tank.fresh",
            "vehicle.garage.door",
            "energy.battery.main",
            "light.interior.living_room",
        ],
    )
    def test_gueltige_ids(self, entity_id: str):
        assert validate_entity_id(entity_id) == entity_id

    @pytest.mark.parametrize(
        "entity_id",
        [
            "",
            "wasser.tank.frisch",  # unbekannte Domäne
            "Water.Tank.Fresh",  # Großbuchstaben
            "water",  # zu wenige Segmente
            "water..fresh",  # leeres Segment
            "water.tank-fresh",  # Bindestrich
            "DB10.DBX4.2",  # Hardwareadresse gehört nie in eine Entity-ID
        ],
    )
    def test_ungueltige_ids(self, entity_id: str):
        with pytest.raises(InvalidEntityId):
            validate_entity_id(entity_id)


class TestFahrzeugkonfiguration:
    def test_doppelte_entity_faellt_auf(self):
        with pytest.raises(ValueError, match="mehrfach"):
            VehicleConfig.model_validate(
                {
                    "entities": [
                        {"id": "water.tank.fresh", "name_key": "a"},
                        {"id": "water.tank.fresh", "name_key": "b"},
                    ]
                }
            )

    def test_unbekanntes_feld_wird_abgewiesen(self):
        # Ein Tippfehler in der Konfiguration darf nicht stillschweigend
        # ignoriert werden.
        with pytest.raises(ValueError):
            EntityConfig.model_validate(
                {"id": "water.tank.fresh", "name_key": "a", "kapazitaet": 500}
            )

    def test_fehlende_datei_meldet_klar(self, tmp_path: Path):
        with pytest.raises(ConfigError, match="fehlt"):
            load_vehicle(tmp_path / "gibtesnicht.yaml")

    def test_kaputtes_yaml_meldet_klar(self, tmp_path: Path):
        datei = tmp_path / "kaputt.yaml"
        datei.write_text("entities: [\n  - id: 'unfertig")
        with pytest.raises(ConfigError, match="YAML"):
            load_vehicle(datei)


class TestCapabilitiesAusTyp:
    """Die Oberfläche kann nur anbieten, was hier entsteht."""

    def test_messwert_hat_keine_befehle(self):
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(
                        id="water.tank.fresh", name_key="t", type="measurement"
                    )
                ]
            )
        )[0]
        assert entity.capabilities == ()

    def test_schalter_kennt_nur_set_state(self):
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(id="light.interior.living", name_key="l", type="switch")
                ]
            )
        )[0]
        assert entity.capabilities == ("set_state",)

    def test_bewegliches_teil_kennt_open_close_stop(self):
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(
                        id="vehicle.garage.door", name_key="g", type="movable"
                    )
                ]
            )
        )[0]
        assert set(entity.capabilities) == {"open", "close", "stop"}

    def test_kein_dimmer_ohne_konfiguration(self):
        """RGB und Dimmen werden nicht angenommen (Kapitel 18 §25/§34)."""
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(id="light.interior.living", name_key="l", type="switch")
                ]
            )
        )[0]
        assert "set_brightness" not in entity.capabilities
        assert "set_color" not in entity.capabilities


class TestMitgelieferteKonfiguration:
    """Die Demokonfiguration muss geladen werden können und ehrlich bleiben."""

    def test_simulationskonfiguration_laedt(self):
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.simulation.yaml")
        entities = build_entities(vehicle)
        assert len(entities) > 10

    def test_keine_erfundenen_tankkapazitaeten(self):
        """Kapitel 18 §98: Kapazitäten werden nicht geraten."""
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.simulation.yaml")
        tanks = [e for e in vehicle.entities if e.id.startswith("water.tank.")]
        assert tanks, "Es sollten Tanks konfiguriert sein"
        assert all(t.capacity_l is None for t in tanks)

    def test_beispiel_fuer_nicht_konfigurierte_hardware(self):
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.simulation.yaml")
        offen = [e for e in vehicle.entities if not e.configured]
        assert offen, "Die Demokonfiguration soll den Fall 'nicht konfiguriert' zeigen"

    def test_beispielkonfigurationen_sind_gueltiges_yaml(self):
        import yaml

        for pfad in (REPO / "config").rglob("*.example.yaml"):
            yaml.safe_load(pfad.read_text(encoding="utf-8"))
