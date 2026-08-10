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

        for entity_id in ("climate.cooling.target", "climate.cooling.state"):
            assert entity_id in entities, entity_id

        # Die Heizung hat eigene Sollwerte an der Anlage — keinen gemeinsamen
        # mit dem Klima.
        assert "heating.temperature.target" in entities
        assert "climate.cooling.target" != "heating.temperature.target"

    def test_heizung_ist_die_scheer_anlage(self):
        """Die Anlage ist mehr als Ein/Aus und ein Sollwert (Punkt G1).

        Verbaut ist eine SCHEER selection mit HeatMate-Steuerung: zwei
        Wärmequellen, zwei Heizkreise, Warmwasser, Elektroheizung. Ein
        einzelner Raumsollwert würde die Anlage falsch darstellen — der Test
        hält fest, dass die Struktur vorhanden ist.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        ids = {e.id for e in vehicle.entities}

        for entity_id in (
            "heating.system.state",
            "heating.system.fault",
            "heating.burner.state",
            "heating.temperature.actual",
            "heating.temperature.target",
            "heating.radiators.state",
            "heating.floor.state",
            "heating.night.state",
            "heating.water.state",
            "heating.water.plus",
            "heating.electric.state",
            "heating.electric.mode",
            "heating.supply.mains",
            "heating.supply.wakeup",
        ):
            assert entity_id in ids, entity_id

    def test_zwei_heizkreise_mit_namen(self):
        """BESTÄTIGT (2026-08-10): zwei Kreise, keine drei.

        Kreis 1 sind die Heizkörper, Kreis 2 ist die Fußbodenheizung. Ein
        früherer Entwurf führte die Fußbodenheizung als dritten Kreis daneben
        — das war erfunden und hätte in der Oberfläche einen Kreis gezeigt,
        den es nicht gibt.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        kreise = sorted(
            e.id
            for e in vehicle.entities
            if e.id.startswith("heating.") and e.id.endswith(".state")
            if e.id.split(".")[1] in ("radiators", "floor", "circuit1", "circuit2")
        )
        assert kreise == ["heating.floor.state", "heating.radiators.state"]

    def test_die_anlage_fuehrt_genau_eine_temperatur(self):
        """BESTÄTIGT (2026-08-10): ein Ist- und ein Sollwert.

        Kessel und Warmwasser werden nicht getrennt geführt. Zwei
        Temperaturen anzuzeigen hätte eine Genauigkeit vorgetäuscht, die die
        Anlage nicht hat.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        temperaturen = sorted(
            e.id
            for e in vehicle.entities
            if e.id.startswith("heating.") and e.unit == "celsius"
        )
        assert temperaturen == [
            "heating.temperature.actual",
            "heating.temperature.target",
        ]

    def test_elektroheizung_hat_drei_stufen_in_kilowatt(self):
        """BESTÄTIGT (2026-08-10): 1 kW, 2 kW, 3 kW.

        Stufe und Leistung sind dasselbe — Stufe 2 *ist* 2 kW. Deshalb ein
        Eintrag mit der Einheit kW und nicht zwei.

        Der Bereich ist bestätigt, der Schreibzugriff nicht: `unverified`
        bleibt, und damit entsteht vorerst kein Bedienelement. Bestätigte
        Grenzen und bestätigter Schreibzugriff sind zwei verschiedene Fragen.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        leistung = next(e for e in vehicle.entities if e.id == "heating.electric.power")
        assert (leistung.min_value, leistung.max_value, leistung.step) == (1, 3, 1)
        assert leistung.unit == "kW"
        assert leistung.unverified

        entity = next(
            e for e in build_entities(vehicle) if e.id == "heating.electric.power"
        )
        assert entity.capabilities == ()

    def test_unbestaetigte_funktion_erzeugt_keinen_befehl(self):
        """Die wichtigste Zusicherung der Heizungsanbindung.

        Die Modbus-Registerliste der HeatMate liegt nicht vor. Ob sich eine
        Funktion überhaupt schalten lässt, weiß niemand — also entsteht kein
        Befehl und damit kein Bedienelement (Kapitel 18 §98/§136).

        Ohne diese Regel wäre die Konfiguration eine Wunschliste, aus der die
        Oberfläche Schalter baut, hinter denen nichts liegt.
        """
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(
                        id="heating.water.plus",
                        name_key="w",
                        type="switch",
                        unverified=True,
                    )
                ]
            )
        )[0]
        assert entity.capabilities == ()

        # Gegenprobe: Ohne das Kennzeichen entsteht der Befehl wie gewohnt.
        bestaetigt = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(id="heating.water.plus", name_key="w", type="switch")
                ]
            )
        )[0]
        assert bestaetigt.capabilities == ("set_state",)

    def test_heizungsanlage_ist_vollstaendig_unbestaetigt(self):
        """Solange die Registerliste fehlt, ist keine Funktion bedienbar.

        Der Test prüft die gelieferte Konfiguration und nicht nur den
        Mechanismus: Ein versehentlich vergessenes `unverified` würde in der
        Oberfläche einen Schalter erzeugen, der eine Heizungsanlage schaltet.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        heizung = [e for e in vehicle.entities if e.id.startswith("heating.")]
        assert heizung

        for config in heizung:
            assert config.unverified, config.id
            assert not config.configured, config.id

        for entity in build_entities(vehicle):
            if entity.id.startswith("heating."):
                assert entity.capabilities == (), entity.id

    def test_zustandsnamen_sind_zeichenketten(self):
        """YAML liest `ON` und `OFF` als Wahrheitswerte.

        Ohne Anführungszeichen wird aus der Pumpenstellung `true`/`false` —
        und aus einer Brennerphase ein Wahrheitswert, den niemand übersetzen
        kann. Der Fehler ist beim Lesen der Datei nicht zu sehen; hier ist er
        es.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        for config in vehicle.entities:
            for zustand in config.states:
                assert isinstance(zustand, str), config.id
                assert zustand == zustand.upper(), config.id

    def test_status_ist_lesbar_und_nicht_schaltbar(self):
        """Eine Betriebsphase wird gemeldet, nicht gesetzt.

        Der Brenner meldet `OFF`, `DEMAND`, `HEATING`, `POSTRUN`, `FAULT` —
        fünf Zustände, die weder in einen Kontakt passen noch von Kehler OS
        gesetzt werden dürfen. Die Phase entsteht in der HeatMate-Regelung.
        """
        entity = build_entities(
            VehicleConfig(
                entities=[
                    EntityConfig(id="heating.burner.state", name_key="b", type="status")
                ]
            )
        )[0]
        assert entity.capabilities == ()

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
