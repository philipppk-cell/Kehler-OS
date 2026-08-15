"""Explizit freigegebene OPC-UA-Schreibbefehle für die Siemens-SPS.

Dieser Adapter kennt keine beliebigen SPS-Adressen. Er kann ausschließlich
die im lokalen Hardware-Mapping freigegebenen Entity/Verb-Kombinationen
ausführen.

Aktuell unterstützt er nur getestete Boolean-Impulse auf HMI-Eingänge.
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
            "OPC-UA-Schreibadapter verbunden: %s (%d Befehle)",
            connection.endpoint,
            len(self._nodes),
        )

    async def disconnect(self) -> None:
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

            if value:
                entity_id, verb = key
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

        current = await node.read_value()

        # Kein vorhandenes TRUE überschreiben. Das könnte beispielsweise ein
        # gleichzeitig gedrückter Taster des normalen HMIs sein.
        if current is not False:
            raise RuntimeError(
                "HMI-Eingang ist vor dem Befehl nicht FALSE: "
                f"{command.entity_id}.{command.verb}"
            )

        active = ua.DataValue(
            ua.Variant(True, ua.VariantType.Boolean)
        )
        inactive = ua.DataValue(
            ua.Variant(False, ua.VariantType.Boolean)
        )

        # Das Zurücksetzen liegt absichtlich im finally: Auch wenn der Task
        # während des Impulses abgebrochen wird, darf der HMI-Eingang nicht
        # absichtlich auf TRUE stehen bleiben.
        try:
            await node.write_value(active)
            await asyncio.sleep(point.pulse_ms / 1000.0)
        finally:
            try:
                await node.write_value(inactive)
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
