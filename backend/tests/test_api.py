"""HTTP- und WebSocket-Schnittstelle.

Geprüft wird vor allem, dass die API nach außen ehrlich bleibt: kein
erfolgreicher Statuscode für einen Befehl, den die Hardware nicht bestätigt
hat (Kapitel 18 §20).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kehleros.adapters.simulation import Fault
from kehleros.api.http import API_PREFIX, create_app
from kehleros.application import Application
from kehleros.config.loader import load_vehicle
from kehleros.config.models import HistoryConfig, Settings
from kehleros.domain.enums import Environment

REPO = Path(__file__).resolve().parents[2]


def settings(tmp_path: Path, **felder: object) -> Settings:
    """Einstellungen für einen Test — mit Historie im Wegwerfverzeichnis.

    Ohne das schriebe jeder Testlauf in `backend/data/`: gemeinsame Datei über
    alle Tests hinweg, Rückstände im Arbeitsverzeichnis und zwei parallele
    Läufe, die sich gegenseitig die Daten überschreiben.
    """
    history = HistoryConfig(path=str(tmp_path / "history.db"))
    return Settings(history=history, **felder)  # type: ignore[arg-type]


@pytest.fixture
def app(tmp_path: Path) -> Application:
    vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
    return Application(settings(tmp_path), vehicle)


@pytest.fixture
def client(app: Application) -> TestClient:
    with TestClient(create_app(app)) as test_client:
        yield test_client


class TestSystem:
    def test_simulation_ist_nach_aussen_erkennbar(self, client: TestClient):
        """Ein simuliertes System darf sich niemals als real ausgeben
        (Kapitel 18 §66)."""
        payload = client.get(f"{API_PREFIX}/system").json()
        assert payload["simulated"] is True
        assert payload["environment"] == "simulation"

    def test_nicht_konfigurierte_entities_werden_gezaehlt(self, client: TestClient):
        payload = client.get(f"{API_PREFIX}/system").json()
        assert payload["unconfigured"] >= 1

    def test_dienststatus_abrufbar(self, client: TestClient):
        payload = client.get(f"{API_PREFIX}/diagnostics/services").json()
        assert "simulation" in payload
        assert "stale-sweep" in payload


class TestFahrzeugbeschreibung:
    """Was das System über das Fahrzeug weiß — und nur das.

    Kapitel 6 §14 trennt die Fahrzeugkonfiguration von den
    Benutzereinstellungen. Sie ist nur lesbar: Es gibt keinen Endpunkt, der
    sie ändert, weil es keine Einstellungspersistenz gibt.
    """

    def test_liefert_bezeichnung_und_bereiche(self, client: TestClient):
        payload = client.get(f"{API_PREFIX}/vehicle").json()

        assert payload["name"] == "Kehler"
        bereiche = {area["id"] for area in payload["areas"]}
        assert {"living", "garage", "tech"} <= bereiche
        assert all(area["name_key"] for area in payload["areas"])

    def test_ohne_angabe_wird_kein_name_erfunden(self, tmp_path: Path):
        """Fehlt die Bezeichnung, bleibt sie leer statt „Wohnmobil"
        (Kapitel 18 §98)."""
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        namenlos = Application(
            settings(tmp_path), vehicle.model_copy(update={"name": None})
        )

        with TestClient(create_app(namenlos)) as client:
            assert client.get(f"{API_PREFIX}/vehicle").json()["name"] is None

    def test_ist_nur_lesbar(self, client: TestClient):
        assert client.post(f"{API_PREFIX}/vehicle", json={}).status_code == 405


class TestSimulationswerkzeuge:
    """Die Diagnoseoberfläche fragt ab, was sich auslösen lässt.

    Sie darf es nicht selbst wissen: Sonst gäbe es zwei Listen derselben
    Sache, und die Oberfläche böte irgendwann Schaltflächen an, die der
    Server abweist.
    """

    def test_blockiert_gibt_es_nur_an_beweglichen_teilen(self, client: TestClient):
        """``BLOCKED`` wird ausschließlich im Bewegungsablauf ausgewertet.

        An einem Ladezustand ließe es sich setzen, ohne dass etwas geschieht —
        eine Schaltfläche ohne Wirkung schickt den Suchenden an die falsche
        Stelle.
        """
        entities = client.get(f"{API_PREFIX}/diagnostics/simulation").json()["entities"]

        # Die Einstiegsstufe ist das bewegliche Teil der Konfiguration. Die
        # Heckklappe war es einmal — seit dem 2026-08-12 ist sie ein `release`
        # mit nur einem Befehl (Gasdruckdämpfer, kein Schließantrieb).
        assert "BLOCKED" in entities["vehicle.step.entry"]["faults"]
        assert "BLOCKED" not in entities["energy.battery.soc"]["faults"]
        assert "BLOCKED" not in entities["vehicle.garage.door"]["faults"]

        # Alles außer BLOCKED wirkt überall: Ein Fühler kann unplausibel
        # werden, einen Defekt melden oder verstummen — ein Garagentor auch.
        ueberall = {f.value for f in Fault} - {"BLOCKED"}
        for entity_id, tools in entities.items():
            assert ueberall <= set(tools["faults"]), entity_id

    def test_setzbar_ist_eine_echte_teilmenge_der_simulierten(self, client: TestClient):
        """Ein Messwert lässt sich setzen, ein Garagentor nicht.

        Wäre das nicht unterschieden, böte die Oberfläche am Garagentor ein
        Eingabefeld an, das nur eine Fehlermeldung erzeugt.
        """
        entities = client.get(f"{API_PREFIX}/diagnostics/simulation").json()["entities"]

        assert entities["water.tank.fresh.large"]["settable"] is True
        assert entities["vehicle.garage.door"]["settable"] is False
        assert any(not tools["settable"] for tools in entities.values())

    def test_gemeldete_werte_lassen_sich_auch_wirklich_setzen(self, client: TestClient):
        """Die Zusage wird eingelöst — für jede genannte Entity.

        Das ist der eigentliche Punkt dieses Endpunkts: Nicht dass er eine
        Auskunft liefert, sondern dass die Auskunft stimmt.
        """
        entities = client.get(f"{API_PREFIX}/diagnostics/simulation").json()["entities"]

        for entity_id, tools in entities.items():
            if not tools["settable"]:
                continue
            antwort = client.post(
                f"{API_PREFIX}/diagnostics/simulation/level",
                json={"entity_id": entity_id, "value": 42},
            )
            assert antwort.status_code == 200, f"{entity_id} ließ sich nicht setzen"

    def test_nicht_gemeldete_entity_wird_abgewiesen(self, client: TestClient):
        """Und umgekehrt: Was nicht genannt ist, geht auch nicht."""
        antwort = client.post(
            f"{API_PREFIX}/diagnostics/simulation/level",
            json={"entity_id": "vehicle.garage.door", "value": 42},
        )
        assert antwort.status_code == 422

    def test_im_produktivbetrieb_gibt_es_keine_werkzeuge(self, tmp_path: Path):
        """Kein Fehlerbild darf je an realer Hardware vorgetäuscht werden
        (Kapitel 15 §96).

        Die Oberfläche blendet die Werkzeuge daraufhin aus. Die Absicherung
        ist aber nicht das Ausblenden, sondern dass es hier nichts zu holen
        gibt.
        """
        vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
        produktiv = Application(
            settings(tmp_path, environment=Environment.PRODUCTION), vehicle
        )

        with TestClient(create_app(produktiv)) as client:
            payload = client.get(f"{API_PREFIX}/diagnostics/simulation").json()
            assert payload == {"available": False, "entities": {}}

            for pfad in ("fault", "level"):
                antwort = client.post(
                    f"{API_PREFIX}/diagnostics/simulation/{pfad}",
                    json={
                        "entity_id": "water.tank.fresh.large",
                        "fault": "SENSOR_ERROR",
                        "value": 42,
                    },
                )
                assert antwort.status_code == 404


class TestEntities:
    def test_liste_enthaelt_qualitaet_und_capabilities(self, client: TestClient):
        entities = client.get(f"{API_PREFIX}/entities").json()
        assert entities

        eintrag = next(e for e in entities if e["entity_id"] == "vehicle.step.entry")
        assert eintrag["state"]["quality"] in {
            "UNKNOWN",
            "VALID",
            "STALE",
            "INVALID",
            "ERROR",
        }
        verben = {c["verb"] for c in eintrag["definition"]["capabilities"]}
        assert verben == {"open", "close", "stop"}

    def test_heckklappe_bietet_nur_oeffnen_an(self, client: TestClient):
        """BESTÄTIGT (2026-08-12): Sie hat keinen Schließantrieb.

        Gasdruckdämpfer drücken sie auf, zugedrückt wird sie von Hand. Bekäme
        die Oberfläche hier `close` oder `stop` geliefert, entstünden zwei
        Schaltflächen für Funktionen, die es am Fahrzeug nicht gibt.
        """
        eintrag = client.get(f"{API_PREFIX}/entities/vehicle.garage.door").json()
        verben = {c["verb"] for c in eintrag["definition"]["capabilities"]}
        assert verben == {"open"}

    def test_schraenke_haben_drei_gruppen_mit_auf_und_zu(self, client: TestClient):
        """BESTÄTIGT (2026-08-12): drei Gruppen, nur öffnen und schließen."""
        entities = client.get(f"{API_PREFIX}/entities").json()
        gruppen = {
            e["entity_id"]: {c["verb"] for c in e["definition"]["capabilities"]}
            for e in entities
            if e["entity_id"].startswith("vehicle.cabinet.")
        }
        assert set(gruppen) == {
            "vehicle.cabinet.group1",
            "vehicle.cabinet.group2",
            "vehicle.cabinet.group3",
        }
        assert all(v == {"open", "close"} for v in gruppen.values())

    def test_messwert_hat_keine_bedienelemente(self, client: TestClient):
        eintrag = client.get(f"{API_PREFIX}/entities/water.tank.fresh.large").json()
        assert eintrag["definition"]["capabilities"] == []

    def test_unbekannte_entity_ergibt_404(self, client: TestClient):
        assert client.get(f"{API_PREFIX}/entities/gibt.es.nicht").status_code == 404


class TestBefehle:
    def test_erfolgreicher_befehl(self, client: TestClient):
        antwort = client.post(
            f"{API_PREFIX}/commands",
            json={
                "entity_id": "water.pump.main",
                "verb": "set_state",
                "params": {"state": "ON"},
            },
        )
        assert antwort.status_code == 200
        assert antwort.json()["success"] is True

    def test_fehlende_capability_ergibt_konflikt(self, client: TestClient):
        antwort = client.post(
            f"{API_PREFIX}/commands",
            json={"entity_id": "water.tank.fresh.large", "verb": "open"},
        )
        assert antwort.status_code == 409
        assert antwort.json()["rejection"] == "MISSING_CAPABILITY"

    def test_nicht_konfiguriert_ergibt_konflikt(self, client: TestClient):
        antwort = client.post(
            f"{API_PREFIX}/commands",
            json={
                "entity_id": "climate.cooling.state",
                "verb": "set_state",
                "params": {"state": "ON"},
            },
        )
        assert antwort.status_code == 409
        assert antwort.json()["rejection"] == "NOT_CONFIGURED"

    def test_ohne_rueckmeldung_wird_nicht_gewartet(
        self, client: TestClient, app: Application
    ):
        """Der Fall des realen Fahrzeugs seit dem 2026-08-12.

        Hier stand ein Test, der eine blockierte Stufe prüfte: Der Befehl
        musste sofort mit 502 scheitern statt zwölf Sekunden in den Timeout zu
        laufen. Dieser Test ist entfallen, weil **das Fahrzeug keine
        Rückmeldung liefert** — eine Blockade kann gar nicht mehr erkannt
        werden. Der Mechanismus selbst bleibt geprüft, dort wo er greift:
        `test_command_bus.py::TestStopp::test_blockierte_bewegung_meldet_sofort`.

        Geprüft wird hier stattdessen, was am realen Fahrzeug geschieht: Der
        Befehl gilt als erledigt, sobald er abgesetzt ist — und zwar sofort.
        Würde auf eine Bestätigung gewartet, käme nach zwölf Sekunden „keine
        Rückmeldung", obwohl nichts fehlgeschlagen ist.
        """
        simulation = app.adapters[0]
        simulation.inject("vehicle.step.entry", Fault.BLOCKED)

        begonnen = time.monotonic()
        antwort = client.post(
            f"{API_PREFIX}/commands",
            json={"entity_id": "vehicle.step.entry", "verb": "open"},
        )
        gedauert = time.monotonic() - begonnen

        assert antwort.status_code == 200
        assert antwort.json()["phase"] == "COMPLETED"
        assert gedauert < 3.0, f"Antwort erst nach {gedauert:.1f} s — wird gewartet?"

    def test_ohne_rueckmeldung_bleibt_der_zustand_unbekannt(self, client: TestClient):
        """Ein erfolgreicher Befehl macht aus nichts kein Wissen.

        Das ist die Regel, an der die ganze Anzeige hängt: Kehler OS hat die
        Stufe angesteuert und weiß trotzdem nicht, wo sie steht
        (Kapitel 18 §38).
        """
        client.post(
            f"{API_PREFIX}/commands",
            json={"entity_id": "vehicle.step.entry", "verb": "open"},
        )
        eintrag = client.get(f"{API_PREFIX}/entities/vehicle.step.entry").json()

        assert eintrag["state"]["quality"] == "UNKNOWN"
        assert eintrag["state"]["value"] is None
        # Sichtbar bleibt allein der letzte Befehl — als Wunsch, nicht als
        # Zustand.
        assert eintrag["requested"]["value"] == "OPEN"


class TestRealtime:
    def test_snapshot_vor_deltas(self, client: TestClient):
        """Ein neuer Client bekommt erst den Gesamtzustand, dann Änderungen
        (Kapitel 13 §30)."""
        with client.websocket_connect(f"{API_PREFIX}/realtime") as ws:
            nachricht = ws.receive_json()

        assert nachricht["type"] == "snapshot"
        assert nachricht["entities"]
        assert "version" in nachricht

    def test_zustandsaenderung_erreicht_den_client(
        self, client: TestClient, app: Application
    ):
        with client.websocket_connect(f"{API_PREFIX}/realtime") as ws:
            ws.receive_json()  # Snapshot

            app.adapters[0].set_value("water.pump.main", "ON")

            nachricht = ws.receive_json()
            assert nachricht["type"] == "delta"
            assert nachricht["entity"]["entity_id"] == "water.pump.main"
            assert nachricht["entity"]["state"]["value"] == "ON"

    def test_unbekannter_wert_kommt_ohne_zahl_an(
        self, client: TestClient, app: Application
    ):
        """Auch über die Leitung gilt: UNKNOWN trägt keinen Wert."""
        with client.websocket_connect(f"{API_PREFIX}/realtime") as ws:
            ws.receive_json()

            app.adapters[0].inject("water.tank.grey", Fault.SENSOR_ERROR)

            nachricht = ws.receive_json()
            zustand = nachricht["entity"]["state"]
            assert zustand["quality"] == "ERROR"
            assert zustand["value"] is None
