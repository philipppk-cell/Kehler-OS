"""Explizit freigegebene OPC-UA-Schreibbefehle für die Siemens-SPS.

Es können ausschließlich die im lokalen Hardware-Mapping freigegebenen
Entity/Verb-Kombinationen ausgeführt werden.

Unterstützt:
- pulse: kurzer TRUE/FALSE-Impuls
- hold: TRUE solange regelmäßig erneuert; Watchdog setzt automatisch FALSE
"""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable
from typing import Any

from asyncua import Client, ua

from ..config.hardware import OpcUaPlcDeviceConfig, OpcUaWritePointConfig
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..domain.enums import Source
from ..domain.models import Command, CommandSpec
from .base import Adapter

log = logging.getLogger(__name__)


def _bool_value(value: bool) -> ua.DataValue:
    return ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))


class OpcUaPlcWriteAdapter(Adapter):
    """Schreibt ausschließlich explizit freigegebene SPS-HMI-Eingänge."""

    name = "plc-opcua-write"
    source = Source.PLC

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        registry: Registry,
        device: OpcUaPlcDeviceConfig,
        points: list[OpcUaWritePointConfig],
        *,
        client_factory: Callable[..., Any] = Client,
    ) -> None:
        entity_ids = list(dict.fromkeys(point.id for point in points))

        super().__init__(
            state,
            events,
            entity_ids=entity_ids,
            poll_interval_s=device.poll_interval_ms / 1000.0,
        )

        self._device = device
        self._client_factory = client_factory
        self._client: Any | None = None

        self._points = {
            (point.id, point.verb): point
            for point in points
        }
        self._nodes: dict[tuple[str, str], Any] = {}

        # Welche Hold-Richtung Kehler OS selbst gerade aktiviert hat.
        self._hold_active: dict[str, str] = {}

        # Pro Entity genau ein Watchdog.
        self._hold_watchdogs: dict[str, asyncio.Task[None]] = {}

        if len(self._points) != len(points):
            raise ValueError("Doppeltes OPC-UA-Schreibmapping")

        for point in points:
            entity = registry.get(point.id)
            if entity is None:
                raise ValueError(
                    f"Unbekannte Entity im Schreibmapping: {point.id}"
                )

            if entity.spec_for(point.verb) is None:
                raise ValueError(
                    "Schreibmapping verweist auf nicht erlaubten Befehl: "
                    f"{point.id}.{point.verb}"
                )

    async def connect(self) -> None:
        connection = self._device.connection
        client = self._client_factory(url=connection.endpoint)

        if connection.username_env:
            username = os.environ.get(connection.username_env)
            if not username:
                raise RuntimeError(
                    f"OPC-UA-Benutzer fehlt in ${connection.username_env}"
                )
            client.set_user(username)

        if connection.password_env:
            password = os.environ.get(connection.password_env)
            if not password:
                raise RuntimeError(
                    f"OPC-UA-Passwort fehlt in ${connection.password_env}"
                )
            client.set_password(password)

        if connection.security:
            await client.set_security_string(connection.security)
        elif not connection.allow_insecure:
            raise RuntimeError(
                "Ungesicherte OPC-UA-Verbindung nicht freigegeben"
            )

        await client.connect()

        self._client = client
        self._nodes = {
            key: client.get_node(point.ref)
            for key, point in self._points.items()
        }

        log.info(
            "OPC-UA-Schreibadapter verbunden: %s (%d Schreibpunkte)",
            connection.endpoint,
            len(self._nodes),
        )

    async def disconnect(self) -> None:
        # Alles, was Kehler OS selbst gehalten hat, vor dem Trennen freigeben.
        for entity_id in list(self._hold_active):
            try:
                await self._release_hold(entity_id)
            except Exception:
                log.critical(
                    "Hold-Eingang konnte beim Trennen nicht sicher "
                    "zurückgesetzt werden: %s",
                    entity_id,
                    exc_info=True,
                )

        for task in self._hold_watchdogs.values():
            task.cancel()
        self._hold_watchdogs.clear()
        self._hold_active.clear()

        client = self._client
        self._client = None
        self._nodes.clear()

        if client is not None:
            await client.disconnect()

    async def poll(self) -> None:
        """Prüft Verbindung und Typ der freigegebenen HMI-Eingänge."""

        if self._client is None:
            raise RuntimeError("OPC-UA-Schreibclient ist nicht verbunden")

        for key, node in self._nodes.items():
            value = await node.read_value()

            if not isinstance(value, bool):
                entity_id, verb = key
                raise RuntimeError(
                    "HMI-Eingang liefert keinen Boolean: "
                    f"{entity_id}.{verb}={value!r}"
                )

            entity_id, verb = key
            point = self._points[key]

            expected_hold = (
                point.mode == "hold"
                and self._hold_active.get(entity_id) == verb
            )

            if value and not expected_hold:
                log.warning(
                    "HMI-Eingang steht außerhalb eines Kehler-OS-Befehls "
                    "auf TRUE: %s.%s",
                    entity_id,
                    verb,
                )

    async def execute(
        self,
        command: Command,
        spec: CommandSpec,
    ) -> None:
        del spec

        # Hold-Entities besitzen keinen eigenen SPS-Node für STOP.
        # Stop bedeutet: alle von Kehler OS gehaltenen Richtungen FALSE.
        if command.verb == "stop":
            hold_points = self._hold_points(command.entity_id)
            if hold_points:
                await self._release_hold(command.entity_id)
                log.info(
                    "OPC-UA-Haltebefehl gestoppt: %s",
                    command.entity_id,
                )
                return

        key = (command.entity_id, command.verb)
        point = self._points.get(key)

        if point is None:
            raise RuntimeError(
                "Kein OPC-UA-Schreibmapping für "
                f"{command.entity_id}.{command.verb}"
            )

        node = self._nodes.get(key)
        if node is None:
            raise RuntimeError("OPC-UA-Schreibadapter ist nicht verbunden")

        if point.mode == "hold":
            await self._execute_hold(command, point, node)
            return

        await self._execute_pulse(command, point, node)

    async def _execute_pulse(
        self,
        command: Command,
        point: OpcUaWritePointConfig,
        node: Any,
    ) -> None:
        current = await node.read_value()

        # Einen vorhandenen Tastendruck des normalen HMIs nicht überschreiben.
        if current is not False:
            raise RuntimeError(
                "HMI-Eingang ist vor dem Befehl nicht FALSE: "
                f"{command.entity_id}.{command.verb}"
            )

        try:
            await node.write_value(_bool_value(True))
            await asyncio.sleep(point.pulse_ms / 1000.0)
        finally:
            try:
                await node.write_value(_bool_value(False))
            except Exception as exc:
                log.critical(
                    "HMI-Eingang konnte nicht auf FALSE zurückgesetzt werden: "
                    "%s.%s",
                    command.entity_id,
                    command.verb,
                )
                raise RuntimeError(
                    "OPC-UA-Impuls konnte nicht sicher zurückgesetzt werden"
                ) from exc

        after = await node.read_value()
        if after is not False:
            raise RuntimeError(
                "HMI-Eingang ist nach dem Impuls nicht FALSE: "
                f"{command.entity_id}.{command.verb}"
            )

        log.info(
            "OPC-UA-Impuls ausgeführt: %s.%s (%d ms)",
            command.entity_id,
            command.verb,
            point.pulse_ms,
        )

    async def _execute_hold(
        self,
        command: Command,
        point: OpcUaWritePointConfig,
        node: Any,
    ) -> None:
        entity_id = command.entity_id
        verb = command.verb
        active_verb = self._hold_active.get(entity_id)

        siblings = self._hold_points(entity_id)

        if active_verb is None:
            # Vor dem ersten TRUE müssen BEIDE Richtungen FALSE sein.
            # So überschreiben wir keinen Tastendruck des normalen HMIs.
            for sibling_verb, _, sibling_node in siblings:
                value = await sibling_node.read_value()
                if value is not False:
                    raise RuntimeError(
                        "HMI-Eingang ist vor Hold nicht FALSE: "
                        f"{entity_id}.{sibling_verb}"
                    )

            await node.write_value(_bool_value(True))
            self._hold_active[entity_id] = verb

            log.info(
                "OPC-UA-Haltebefehl gestartet: %s.%s",
                entity_id,
                verb,
            )

        elif active_verb == verb:
            # Heartbeat für dieselbe Richtung.
            if await node.read_value() is not True:
                raise RuntimeError(
                    "Aktiver Hold-Eingang ist unerwartet nicht TRUE: "
                    f"{entity_id}.{verb}"
                )

            # Gegenrichtung muss währenddessen sicher FALSE bleiben.
            for sibling_verb, _, sibling_node in siblings:
                if sibling_verb == verb:
                    continue
                if await sibling_node.read_value() is not False:
                    raise RuntimeError(
                        "Gegenrichtung ist während Hold aktiv: "
                        f"{entity_id}.{sibling_verb}"
                    )

        else:
            raise RuntimeError(
                "Gegenrichtung bereits aktiv: "
                f"{entity_id}.{active_verb}"
            )

        self._arm_watchdog(entity_id, point.hold_timeout_ms)

    async def renew_hold(self, entity_id: str, verb: str) -> None:
        """Verlängert ausschließlich einen bereits aktiven Hold.

        Diese Methode kann keinen neuen HMI-Eingang einschalten. Der Start
        muss vorher als normaler, validierter CommandBus-Befehl erfolgt sein.
        """
        point = self._points.get((entity_id, verb))

        if point is None or point.mode != "hold":
            raise RuntimeError(
                f"Kein Hold-Schreibpunkt für {entity_id}.{verb}"
            )

        if self._hold_active.get(entity_id) != verb:
            raise RuntimeError(
                f"Hold ist nicht aktiv: {entity_id}.{verb}"
            )

        node = self._nodes.get((entity_id, verb))
        if node is None:
            raise RuntimeError(
                "OPC-UA-Schreibadapter ist nicht verbunden"
            )

        if await node.read_value() is not True:
            raise RuntimeError(
                f"Aktiver Hold-Eingang ist nicht TRUE: {entity_id}.{verb}"
            )

        for sibling_verb, _, sibling_node in self._hold_points(entity_id):
            if sibling_verb == verb:
                continue

            if await sibling_node.read_value() is not False:
                raise RuntimeError(
                    "Gegenrichtung ist während Hold aktiv: "
                    f"{entity_id}.{sibling_verb}"
                )

        self._arm_watchdog(entity_id, point.hold_timeout_ms)

    async def _release_hold(self, entity_id: str) -> None:
        points = self._hold_points(entity_id)
        active_verb = self._hold_active.get(entity_id)

        if not points:
            raise RuntimeError(
                f"Keine Hold-Schreibpunkte für {entity_id}"
            )

        if active_verb is None:
            # STOP darf fremde/physische HMI-Tastendrücke nicht überschreiben.
            for verb, _, node in points:
                if await node.read_value() is not False:
                    raise RuntimeError(
                        "Hold-Eingang ist TRUE, wurde aber nicht von "
                        f"Kehler OS aktiviert: {entity_id}.{verb}"
                    )
            return

        # Beide Richtungen sicher FALSE setzen.
        for _, _, node in points:
            await node.write_value(_bool_value(False))

        for verb, _, node in points:
            if await node.read_value() is not False:
                raise RuntimeError(
                    "Hold-Eingang konnte nicht sicher zurückgesetzt werden: "
                    f"{entity_id}.{verb}"
                )

        self._hold_active.pop(entity_id, None)
        self._cancel_watchdog(entity_id)

    def _hold_points(
        self,
        entity_id: str,
    ) -> list[tuple[str, OpcUaWritePointConfig, Any]]:
        result: list[tuple[str, OpcUaWritePointConfig, Any]] = []

        for (point_entity, verb), point in self._points.items():
            if point_entity != entity_id or point.mode != "hold":
                continue

            node = self._nodes.get((point_entity, verb))
            if node is not None:
                result.append((verb, point, node))

        return result

    def _arm_watchdog(self, entity_id: str, timeout_ms: int) -> None:
        self._cancel_watchdog(entity_id)

        self._hold_watchdogs[entity_id] = asyncio.create_task(
            self._hold_watchdog(entity_id, timeout_ms)
        )

    def _cancel_watchdog(self, entity_id: str) -> None:
        task = self._hold_watchdogs.pop(entity_id, None)

        if (
            task is not None
            and task is not asyncio.current_task()
            and not task.done()
        ):
            task.cancel()

    async def _hold_watchdog(
        self,
        entity_id: str,
        timeout_ms: int,
    ) -> None:
        try:
            await asyncio.sleep(timeout_ms / 1000.0)
            await self._release_hold(entity_id)

            log.warning(
                "OPC-UA-Haltebefehl automatisch beendet "
                "(Heartbeat ausgeblieben): %s",
                entity_id,
            )

        except asyncio.CancelledError:
            return

        except Exception:
            log.critical(
                "OPC-UA-Haltebefehl konnte vom Watchdog nicht sicher "
                "beendet werden: %s",
                entity_id,
                exc_info=True,
            )
