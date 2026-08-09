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
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..application import Application
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
    return api


def _status_for(phase: CommandPhase) -> int:
    """Ordnet der Befehlsphase einen passenden HTTP-Status zu."""
    return {
        CommandPhase.COMPLETED: 200,
        CommandPhase.REJECTED: 409,
        CommandPhase.FAILED: 502,
        CommandPhase.TIMEOUT: 504,
    }.get(phase, 202)
