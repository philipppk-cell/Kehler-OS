"""HTTP- und WebSocket-Schnittstelle.

Geprüft wird vor allem, dass die API nach außen ehrlich bleibt: kein
erfolgreicher Statuscode für einen Befehl, den die Hardware nicht bestätigt
hat (Kapitel 18 §20).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kehleros.adapters.simulation import Fault
from kehleros.api.http import API_PREFIX, create_app
from kehleros.application import Application
from kehleros.config.loader import load_vehicle
from kehleros.config.models import Settings

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def app() -> Application:
    vehicle = load_vehicle(REPO / "config/vehicle/vehicle.yaml")
    return Application(Settings(), vehicle)


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


class TestEntities:
    def test_liste_enthaelt_qualitaet_und_capabilities(self, client: TestClient):
        entities = client.get(f"{API_PREFIX}/entities").json()
        assert entities

        eintrag = next(e for e in entities if e["entity_id"] == "vehicle.garage.door")
        assert eintrag["state"]["quality"] in {
            "UNKNOWN",
            "VALID",
            "STALE",
            "INVALID",
            "ERROR",
        }
        verben = {c["verb"] for c in eintrag["definition"]["capabilities"]}
        assert verben == {"open", "close", "stop"}

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
            json={"entity_id": "vehicle.awning.main", "verb": "open"},
        )
        assert antwort.status_code == 409
        assert antwort.json()["rejection"] == "NOT_CONFIGURED"

    def test_timeout_ergibt_keinen_erfolgsstatus(
        self, client: TestClient, app: Application
    ):
        """Blockierte Mechanik darf niemals 200 liefern."""
        simulation = app.adapters[0]
        simulation.inject("vehicle.step.entry", Fault.BLOCKED)

        antwort = client.post(
            f"{API_PREFIX}/commands",
            json={"entity_id": "vehicle.step.entry", "verb": "open"},
        )
        assert antwort.status_code == 504
        assert antwort.json()["success"] is False
        assert antwort.json()["phase"] == "TIMEOUT"


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
