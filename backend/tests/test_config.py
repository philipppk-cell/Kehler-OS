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
            "climate.cooling.living_room",
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
                    EntityConfig(id="water.tank.fresh", name_key="t", type="measurement")
                ]
            )
        )[0]
        assert entity.capabilities == ()

    def test_schalter_kennt_nur_set_state(self):
        entity = build_entities(
            VehicleConfig(
                entities=[EntityConfig(id="water.pump.main", name_key="l", type="switch")]
            )
        )[0]
        assert entity.capabilities == ("set_state",)

    def test_bewegliches_teil_kennt_open_close_stop(self):
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(id="vehicle.garage.door", name_key="g", type="movable")
                ]
            )
        )[0]
        assert set(entity.capabilities) == {"open", "close", "stop"}

    def test_kein_dimmer_ohne_konfiguration(self):
        """RGB und Dimmen werden nicht angenommen (Kapitel 18 §25/§34)."""
        entity = build_entities(
            VehicleConfig(
                entities=[EntityConfig(id="water.pump.main", name_key="l", type="switch")]
            )
        )[0]
        assert "set_brightness" not in entity.capabilities
        assert "set_color" not in entity.capabilities


class TestMitgelieferteKonfiguration:
    """Die Demokonfiguration muss geladen werden können und ehrlich bleiben."""

    def test_simulationskonfiguration_laedt(self):
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        entities = build_entities(vehicle)
        assert len(entities) > 10

    def test_tankkapazitaeten_entsprechen_der_angabe(self):
        """Die Kapazitäten sind vom Fahrzeughalter genannt (Punkt C2).

        Der Test hält sie fest, damit ein Zahlendreher in der Konfiguration
        auffällt — und nicht erst dann, wenn die Oberfläche eine falsche
        Literzahl anzeigt.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        kapazitaeten = {
            e.id: e.capacity_l for e in vehicle.entities if e.id.startswith("water.tank.")
        }
        assert kapazitaeten == {
            "water.tank.fresh.large": 550,
            "water.tank.fresh.small": 450,
            "water.tank.grey": 280,
            "water.tank.black": 370,
        }

    def test_warnschwellen_entsprechen_der_angabe(self):
        """Die Schwellen sind vom Fahrzeughalter genannt (Punkt C3).

        Frischwasser warnt nach unten, Abwasser nach oben. Die Richtung ist
        das, was hier schiefgehen kann — eine vertauschte Schwelle würde
        genau dann schweigen, wenn sie gebraucht wird.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        schwellen = {
            e.id: (e.warn_below, e.warn_above)
            for e in vehicle.entities
            if e.id.startswith("water.tank.")
        }
        assert schwellen == {
            "water.tank.fresh.large": (20, None),
            "water.tank.fresh.small": (20, None),
            "water.tank.grey": (None, 80),
            "water.tank.black": (None, 80),
        }

    def test_kritische_schwellen_entsprechen_der_angabe(self):
        """Zweite Stufe, ebenfalls vom Fahrzeughalter genannt."""
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        kritisch = {
            e.id: (e.critical_below, e.critical_above)
            for e in vehicle.entities
            if e.id.startswith("water.tank.")
        }
        assert kritisch == {
            "water.tank.fresh.large": (10, None),
            "water.tank.fresh.small": (10, None),
            "water.tank.grey": (None, 90),
            "water.tank.black": (None, 90),
        }

    def test_kritische_stufe_liegt_hinter_der_warnstufe(self):
        """Die schärfere Schwelle muss auch die spätere sein.

        Wären sie vertauscht, würde die kritische Meldung vor der Warnung
        erscheinen — und die Warnstufe damit nie sichtbar.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        for e in vehicle.entities:
            if e.warn_below is not None and e.critical_below is not None:
                assert e.critical_below < e.warn_below, e.id
            if e.warn_above is not None and e.critical_above is not None:
                assert e.critical_above > e.warn_above, e.id

    def test_nur_wasser_hat_schwellen(self):
        """Für alles andere ist keine Schwelle genannt — also gibt es keine."""
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        for e in vehicle.entities:
            if e.id.startswith("water.tank."):
                continue
            assert e.warn_below is None and e.warn_above is None, e.id
            assert e.critical_below is None and e.critical_above is None, e.id

    def test_klima_und_heizung_sind_getrennt(self):
        """Zwei Systeme, zwei Sollwerte (BESTÄTIGT 2026-08-10).

        Der naheliegende Fehler wäre, beiden Bereichen denselben Sollwert zu
        geben — die Oberfläche sähe dann aufgeräumter aus, und das Verstellen
        der Heizung würde stillschweigend die Klimaanlage mitverstellen.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        entities = {e.id: e for e in build_entities(vehicle)}

        for entity_id in ("climate.cooling.target", "heating.target"):
            assert entity_id in entities, entity_id
            assert "set_value" in entities[entity_id].capabilities, entity_id

        for entity_id in ("climate.cooling.state", "heating.state"):
            assert entity_id in entities, entity_id
            assert "set_state" in entities[entity_id].capabilities, entity_id

    def test_sollwert_ohne_grenzen_ist_nicht_verstellbar(self):
        """Ohne Obergrenze kein Befehl — und damit kein Bedienelement.

        Das ist die Stelle, an der Kapitel 18 §136 wirksam wird: Eine
        geratene Obergrenze wäre bei der Strombegrenzung gefährlich, also
        entsteht sie gar nicht erst.
        """
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(id="energy.shore.limit", name_key="s", type="setpoint")
                ]
            )
        )[0]
        assert entity.capabilities == ()

    def test_kein_lichtbereich(self):
        """Die Beleuchtung läuft über Lichtschalter, nicht über die SPS.

        BESTÄTIGT (2026-08-10). Eine übrig gebliebene Lichtentity würde in
        der Oberfläche einen Bereich erzeugen, den es am Fahrzeug nicht gibt.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        assert not [e for e in vehicle.entities if e.id.startswith("light.")]

    def test_beispiel_fuer_nicht_konfigurierte_hardware(self):
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        offen = [e for e in vehicle.entities if not e.configured]
        assert offen, "Die Demokonfiguration soll den Fall 'nicht konfiguriert' zeigen"

    def test_beispielkonfigurationen_sind_gueltiges_yaml(self):
        import yaml

        for pfad in (REPO / "config").rglob("*.example.yaml"):
            yaml.safe_load(pfad.read_text(encoding="utf-8"))
