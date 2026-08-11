"""HTTP- und WebSocket-Schnittstelle.

Die Oberfläche spricht ausschließlich mit dieser Schicht — niemals direkt mit
einem Adapter, einer SPS oder einem Victron-Gerät (Kapitel 18 §6/§52).

Befehle laufen bewusst über HTTP und nicht über den WebSocket: eindeutige
Fehlercodes, saubere Berechtigungsprüfung je Aufruf, einfachere
Nachvollziehbarkeit im Audit (ADR 0005). Der WebSocket liefert nur den
Zustand.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..adapters.simulation import Fault as SimulationFault
from ..application import Application
from ..core.alerts import derive_alerts
from ..core.energy import Reading as EnergyReading
from ..core.energy import summarise as energy_summary
from ..core.heating import summarise as heating_summary
from ..core.water import TankView
from ..core.water import summarise as water_summary
from ..domain.enums import CommandPhase, Trigger
from ..domain.models import Command
from . import serialization as ser

log = logging.getLogger(__name__)

API_PREFIX = "/api/v1"
"""Die API ist versioniert, damit ältere Clients nicht unangekündigt brechen
(Kapitel 5 §16)."""


class CommandRequest(BaseModel):
    """Ein Befehl, wie ihn ein Client absetzt."""

    entity_id: str
    verb: str
    params: dict[str, Any] = Field(default_factory=dict)
    client: str | None = None


class FaultRequest(BaseModel):
    """Ein gezielt ausgelöstes Fehlerbild — nur in der Simulation."""

    entity_id: str
    fault: str


class LevelRequest(BaseModel):
    """Ein gezielt gesetzter Messwert — nur in der Simulation."""

    entity_id: str
    value: float


def create_app(application: Application) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Startet die Hintergrunddienste mit dem Webserver und beendet sie
        wieder — ohne manuelle Terminalbefehle (Kapitel 17 §34)."""
        await application.start()
        try:
            yield
        finally:
            await application.stop()

    api = FastAPI(
        title="Kehler OS",
        version=application.version,
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )
    router = APIRouter(prefix=API_PREFIX)

    # ── System ──────────────────────────────────────────────────────────────

    @router.get("/system")
    async def system() -> dict[str, Any]:
        """Gesamtzustand — und ob real oder simuliert gearbeitet wird."""
        info = application.info()
        return {
            "version": info.version,
            "environment": info.environment.value,
            "simulated": info.simulated,
            "health": info.health.value,
            "entities": info.entities,
            "unconfigured": info.unconfigured,
            "services": info.services,
            "state_version": info.state_version,
        }

    @router.get("/vehicle")
    async def vehicle() -> dict[str, Any]:
        """Das Fahrzeug, wie es konfiguriert ist — nicht, wie es gerade steht.

        Kapitel 6 §14 trennt die **Fahrzeugkonfiguration** ausdrücklich von den
        Benutzereinstellungen: Sie beschreibt das konkrete Fahrzeug — welche
        Tanks es hat, wie groß sie sind, welche Bereiche es gibt. Diese Angaben
        stehen in ``config/vehicle/`` und werden beim Start gelesen
        (Kapitel 17 §48).

        **Nur lesend.** Die Oberfläche zeigt sie an; ändern lassen sie sich
        über die Konfigurationsdatei. Ein Eingabefeld für die Tankgröße wäre
        eine Zusage, die dieses System nicht einlöst: Es gibt keine
        Einstellungspersistenz, und der Zustand wird nach einem Neustart
        bewusst nicht wiederhergestellt (Kapitel 6 §44).
        """
        return {
            "name": application.vehicle.name,
            "areas": [
                {"id": area.id, "name_key": area.name_key}
                for area in application.vehicle.areas
            ],
            # Ob ein 3D-Modell hinterlegt ist. Ohne eines bleibt es bei der aus
            # Code gebauten Darstellung — das ist der Auslieferungsstand und
            # kein Fehlzustand (ADR 0008).
            "has_model": application.model_file is not None,
        }

    @router.get("/vehicle/model")
    async def vehicle_model() -> FileResponse:
        """Das 3D-Modell des Fahrzeugs, falls hinterlegt.

        Liegt in `config/vehicle/model.glb`, also bei der Beschreibung des
        Fahrzeugs — es gehört zum Fahrzeug und nicht zum Programm.

        Ohne Datei ein sauberes 404. Die Oberfläche nimmt dann die aus Code
        gebaute Darstellung; ein leeres Bild oder ein Platzhalterwürfel wäre
        die schlechtere Antwort.
        """
        pfad = application.model_file
        if pfad is None:
            raise HTTPException(status_code=404, detail="Kein Fahrzeugmodell hinterlegt")
        return FileResponse(pfad, media_type="model/gltf-binary")

    @router.get("/diagnostics/services")
    async def services() -> dict[str, Any]:
        """Dienststatus für die Diagnoseansicht (Kapitel 16 §55)."""
        return {
            name: {
                "state": status.state.value,
                "restarts": status.restarts,
                "uptime_s": status.uptime_s,
                "last_error": status.last_error,
            }
            for name, status in application.supervisor.status().items()
        }

    @router.get("/diagnostics/adapters")
    async def adapters() -> list[dict[str, Any]]:
        return [
            {
                "name": adapter.name,
                "link": adapter.link.value,
                "source": adapter.source.value,
                "entities": len(adapter.entity_ids),
                "poll_interval_s": adapter.poll_interval_s,
            }
            for adapter in application.adapters
        ]

    @router.get("/diagnostics/simulation")
    async def simulation() -> dict[str, Any]:
        """Was sich in dieser Betriebsart auslösen lässt — je Entity.

        Die Oberfläche baut ihr Werkzeug daraus, statt die Möglichkeiten
        selbst zu kennen. Im Produktivbetrieb ist ``available`` ``false`` und
        ``entities`` leer — die Werkzeuge verschwinden dann, statt
        Schaltflächen anzubieten, die der Server ohnehin abweist
        (Kapitel 15 §96).
        """
        empty: dict[str, Any] = {"available": False, "entities": {}}
        if not application.settings.is_simulated:
            return empty

        for adapter in application.adapters:
            report = getattr(adapter, "diagnostics", None)
            if report is None:
                continue
            return {"available": True, **report()}

        return empty

    @router.post("/diagnostics/simulation/fault")
    async def inject_fault(request: FaultRequest) -> dict[str, Any]:
        """Löst ein Fehlerbild in der Simulation aus.

        Kapitel 18 §65: Eine Simulation ohne auslösbare Fehlerbilder ist
        wertlos — die Zustände, die im Alltag am seltensten auftreten, sind im
        Ernstfall die wichtigsten. Ohne diesen Zugang lassen sie sich nur
        prüfen, indem man auf sie wartet.

        **Im Produktivbetrieb nicht vorhanden.** Der Weg existiert nur,
        solange kein reales Fahrzeug angesteuert wird — er darf niemals einen
        Fehler an echter Hardware vortäuschen (Kapitel 15 §96).
        """
        if not application.settings.is_simulated:
            raise HTTPException(
                status_code=404,
                detail="Fehlerinjektion gibt es nur in der Simulation",
            )

        for adapter in application.adapters:
            inject = getattr(adapter, "inject", None)
            if inject is None or request.entity_id not in adapter.entity_ids:
                continue
            try:
                inject(request.entity_id, SimulationFault(request.fault))
            except ValueError as error:
                raise HTTPException(status_code=422, detail=str(error)) from error
            return {"entity_id": request.entity_id, "fault": request.fault}

        raise HTTPException(status_code=404, detail="Unbekannte Entity")

    @router.post("/diagnostics/simulation/level")
    async def set_level(request: LevelRequest) -> dict[str, Any]:
        """Setzt einen simulierten Messwert auf einen bestimmten Stand.

        Ohne das ließen sich Schwellenwarnungen nur prüfen, indem man wartet,
        bis der Simulator zufällig dorthin driftet. Wie die Fehlerinjektion
        existiert dieser Weg ausschließlich in der Simulation.
        """
        if not application.settings.is_simulated:
            raise HTTPException(
                status_code=404,
                detail="Messwerte setzen gibt es nur in der Simulation",
            )

        for adapter in application.adapters:
            set_level_fn = getattr(adapter, "set_level", None)
            if set_level_fn is None or request.entity_id not in adapter.entity_ids:
                continue
            try:
                set_level_fn(request.entity_id, request.value)
            except (KeyError, ValueError) as error:
                raise HTTPException(status_code=422, detail=str(error)) from error
            return {"entity_id": request.entity_id, "value": request.value}

        raise HTTPException(status_code=404, detail="Unbekannte Entity")

    @router.get("/alerts")
    async def alerts() -> list[dict[str, Any]]:
        """Aktuelle Warnungen.

        Die Bewertung geschieht im Backend, nicht in der Oberfläche
        (Kapitel 18 §6). Schwellenwarnungen fehlen bewusst, solange die
        Schwellen nicht konfiguriert sind (Punkt C3).
        """
        return [
            {
                "id": alert.id,
                "type": alert.type,
                "entity_id": alert.entity_id,
                "severity": alert.severity.value,
                "state": alert.state.value,
                "message_key": alert.message_key,
                "params": alert.params,
                "raised_at": alert.raised_at.isoformat(),
            }
            for alert in derive_alerts(application.state, application.registry)
        ]

    @router.get("/water")
    async def water() -> dict[str, Any]:
        """Wasserstände einschließlich Gesamtmenge Frischwasser.

        Die Summe über beide Frischwassertanks entsteht hier und nicht in der
        Oberfläche: Sie wird über Liter gebildet, nicht über Prozent, und sie
        entfällt vollständig, sobald ein Tank keinen belastbaren Wert liefert
        (siehe ``core/water.py``).
        """
        summary = water_summary(
            {state.entity_id: state for state in application.state},
            application.registry,
        )
        return {
            "fresh": {
                "quality": summary.fresh.quality.value,
                "capacity_l": summary.fresh.capacity_l,
                "litres": summary.fresh.litres,
                "free_l": summary.fresh.free_l,
                "percent": summary.fresh.percent,
                "warn_below": summary.fresh.warn_below,
                "critical_below": summary.fresh.critical_below,
                "level": summary.fresh.level,
                "tanks": [_tank_json(tank) for tank in summary.fresh.tanks],
            },
            "waste": [_tank_json(tank) for tank in summary.waste],
        }

    @router.get("/energy")
    async def energy() -> dict[str, Any]:
        """Energiefluss mit gedeuteter Laderichtung.

        Die Deutung („lädt", „entlädt", „ruht") entsteht im Backend, samt der
        Totzone, ab der eine Richtung überhaupt behauptet wird — siehe
        ``core/energy.py``. Ohne belastbaren Messwert bleibt sie leer.
        """
        summary = energy_summary(
            {state.entity_id: state for state in application.state},
            application.registry,
        )
        return {
            "soc": _reading_json(summary.soc),
            "voltage": _reading_json(summary.voltage),
            "current": _reading_json(summary.current),
            "battery_power": _reading_json(summary.battery_power),
            "solar_power": _reading_json(summary.solar_power),
            "consumption": _reading_json(summary.consumption),
            "shore_power": _reading_json(summary.shore_power),
            "shore_connected": summary.shore_connected,
            "direction": summary.direction,
            "capacity_wh": summary.capacity_wh,
            "remaining_wh": summary.remaining_wh,
            "runtime_h": summary.runtime_h,
            "runtime_capped": summary.runtime_capped,
        }

    @router.get("/heating")
    async def heating() -> dict[str, Any]:
        """Zustand der SCHEER-Heizungsanlage.

        Gedeutet wird eine einzige Sache: **welche Wärmequelle gerade
        arbeitet** — aus Brennerphase und Elektroheizung zusammen (siehe
        ``core/heating.py``). Alles andere reicht die API durch.

        Solange die Modbus-Registerliste fehlt (Punkt G1), ist `linked`
        ``false`` und die Wärmequelle ``null``. Die Oberfläche zeigt dann die
        Anlage als Struktur und sagt dazu, dass die Anbindung aussteht.
        """
        summary = heating_summary(
            {state.entity_id: state for state in application.state},
            application.registry,
        )
        return {
            "heat_source": summary.heat_source,
            "fault": summary.fault,
            "linked": summary.linked,
            "unverified": summary.unverified,
        }

    @router.get("/history/{entity_id}")
    async def history(entity_id: str, hours: float = 24.0) -> dict[str, Any]:
        """Der Verlauf einer Messgröße.

        ``available`` ist ``false``, wenn die Historie abgeschaltet ist oder
        gerade nicht schreiben kann. Die Oberfläche sagt dann „Historie nicht
        verfügbar" (Kapitel 16 §79) — eine leere Kurve sähe aus wie „nichts
        passiert", und das wäre eine Aussage über das Fahrzeug statt über die
        Datenhaltung.

        Punkte ohne Wert werden **mitgeliefert** und nicht weggelassen: Sie
        sind die Aussage „hier war nichts bekannt". Wer sie wegließe, bekäme
        eine durchgehende Linie über eine Lücke — genau das, was Kapitel 16 §97
        verbietet.
        """
        if application.registry.get(entity_id) is None:
            raise HTTPException(status_code=404, detail="Unbekannte Entity")

        store = application.history
        if store is None or store.degraded:
            return {
                "entity_id": entity_id,
                "available": False,
                "resolution": None,
                "points": [],
            }

        until = int(time.time() * 1000)
        since = until - int(max(0.0, hours) * 3_600_000)
        series = await store.series(entity_id, since, until)

        return {
            "entity_id": series.entity_id,
            "available": True,
            "resolution": series.resolution,
            "points": [
                {"at": point.at, "value": point.value, "quality": point.quality}
                for point in series.points
            ],
        }

    # ── Entities ────────────────────────────────────────────────────────────

    @router.get("/entities")
    async def entities() -> list[dict[str, Any]]:
        return [
            ser.entity_state(state, application.registry.get(state.entity_id))
            for state in application.state
        ]

    @router.get("/entities/{entity_id}")
    async def entity(entity_id: str) -> dict[str, Any]:
        state = application.state.get(entity_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Unbekannte Entity")
        return ser.entity_state(state, application.registry.get(entity_id))

    # ── Befehle ─────────────────────────────────────────────────────────────

    @router.post("/commands")
    async def submit(request: CommandRequest) -> JSONResponse:
        """Setzt einen Befehl ab und wartet auf sein Ergebnis.

        Der Statuscode bildet ab, was tatsächlich passiert ist — ein
        abgewiesener oder in einen Timeout gelaufener Befehl liefert niemals
        200 (Kapitel 18 §20).
        """
        command = await application.commands.submit(
            Command(
                entity_id=request.entity_id,
                verb=request.verb,
                params=request.params,
                trigger=Trigger.USER,
                client=request.client,
            )
        )
        return JSONResponse(
            status_code=_status_for(command.phase),
            content=ser.command_result(command),
        )

    # ── Realtime ────────────────────────────────────────────────────────────

    @router.websocket("/realtime")
    async def realtime(websocket: WebSocket) -> None:
        """Snapshot beim Verbinden, danach nur noch Änderungen.

        Kommt ein Client nicht mehr hinterher, wird er zur
        Neusynchronisation aufgefordert, statt ihm veraltete Deltas
        unterzuschieben (Kapitel 17 §105).
        """
        await websocket.accept()
        subscription = application.state.subscribe()
        try:
            await websocket.send_json(
                ser.snapshot(
                    application.state.snapshot(),
                    application.registry,
                    application.state.version,
                )
            )
            while True:
                delta = await subscription.get()
                if subscription.needs_resync:
                    subscription.needs_resync = False
                    await websocket.send_json(
                        ser.snapshot(
                            application.state.snapshot(),
                            application.registry,
                            application.state.version,
                        )
                    )
                    continue
                await websocket.send_json(ser.delta(delta.entity_state))
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Realtime-Verbindung unerwartet beendet")
        finally:
            application.state.unsubscribe(subscription)

    api.include_router(router)
    _mount_frontend(api)
    return api


def _mount_frontend(api: FastAPI) -> None:
    """Liefert die gebaute Oberfläche aus.

    Das Fahrzeug braucht dadurch keinen zweiten Webserver (ADR 0006). Alle
    Ressourcen — Schriften, Symbole, Grafiken — liegen lokal; ohne Internet
    fällt die Oberfläche nicht auseinander (Kapitel 17 §107/§108).
    """
    static = Path(__file__).parent / "static"
    if not static.is_dir():
        log.info(
            "Kein gebautes Frontend gefunden (%s). "
            "Das Backend läuft; die Oberfläche wird mit 'npm run build' erzeugt.",
            static,
        )
        return

    api.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

    @api.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(static / "index.html")


def _status_for(phase: CommandPhase) -> int:
    """Ordnet der Befehlsphase einen passenden HTTP-Status zu."""
    return {
        CommandPhase.COMPLETED: 200,
        CommandPhase.REJECTED: 409,
        CommandPhase.FAILED: 502,
        CommandPhase.TIMEOUT: 504,
        # Abgelöst ist kein Serverfehler: Der Befehl wurde ordnungsgemäß
        # verarbeitet und dann von einem Stopp beendet. 409 sagt „nicht im
        # gewünschten Zustand abgeschlossen", ohne einen Defekt zu behaupten.
        CommandPhase.SUPERSEDED: 409,
    }.get(phase, 202)


def _reading_json(reading: EnergyReading) -> dict[str, Any]:
    """Ein Messwert mit seiner Belastbarkeit — nie ein nackter Zahlenwert."""
    return {"value": reading.value, "quality": reading.quality.value}


def _tank_json(tank: TankView) -> dict[str, Any]:
    """Ein Tank für die Oberfläche.

    ``litres`` ist ``None``, wenn Füllstand oder Kapazität fehlen — nicht 0.
    """
    return {
        "entity_id": tank.entity_id,
        "name_key": tank.name_key,
        "quality": tank.quality.value,
        "percent": tank.percent,
        "capacity_l": tank.capacity_l,
        "litres": tank.litres,
        "free_l": tank.free_l,
        "warn_below": tank.warn_below,
        "warn_above": tank.warn_above,
        "critical_below": tank.critical_below,
        "critical_above": tank.critical_above,
        "level": tank.level,
    }
