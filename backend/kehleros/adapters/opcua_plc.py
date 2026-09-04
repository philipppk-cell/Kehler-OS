"""Read-only OPC-UA-Adapter für die Siemens-SPS.

Erste reale Integrationsstufe: ausschließlich Messwerte lesen.
Schreibbefehle werden technisch verweigert.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any

from asyncua import Client

from ..config.hardware import OpcUaPlcDeviceConfig, OpcUaReadPointConfig
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..core.water import normalise_tank_percent
from ..domain.enums import Source
from ..domain.models import Command, CommandSpec, StateValue, utcnow
from .base import Adapter

log = logging.getLogger(__name__)


class OpcUaPlcAdapter(Adapter):
    name = "plc-opcua"
    source = Source.PLC

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        registry: Registry,
        device: OpcUaPlcDeviceConfig,
        points: list[OpcUaReadPointConfig],
        *,
        client_factory: Callable[..., Any] = Client,
    ) -> None:
        super().__init__(
            state,
            events,
            entity_ids=[point.id for point in points],
            poll_interval_s=device.poll_interval_ms / 1000.0,
        )
        self._registry = registry
        self._device = device
        self._points = {point.id: point for point in points}
        self._client_factory = client_factory
        self._client: Any | None = None
        self._nodes: dict[str, Any] = {}

        for point in points:
            entity = registry.get(point.id)
            if entity is None:
                raise ValueError(
                    "Unbekannte Entity im Hardware-Mapping: "
                    f"{point.id}"
                )
            if entity.commands:
                raise ValueError(
                    "Read-only-Stufe darf Aktor nicht besitzen: "
                    f"{point.id}"
                )

    async def connect(self) -> None:
        connection = self._device.connection
        client = self._client_factory(url=connection.endpoint)

        if connection.username_env:
            username = os.environ.get(connection.username_env)
            if not username:
                raise RuntimeError(
                    "OPC-UA-Benutzer fehlt in "
                    f"${connection.username_env}"
                )
            client.set_user(username)

        if connection.password_env:
            password = os.environ.get(connection.password_env)
            if not password:
                raise RuntimeError(
                    "OPC-UA-Passwort fehlt in "
                    f"${connection.password_env}"
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
            entity_id: client.get_node(point.ref)
            for entity_id, point in self._points.items()
        }

        log.info(
            "OPC UA verbunden: %s (%d read-only Datenpunkte)",
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
        if self._client is None:
            raise RuntimeError("OPC-UA-Client ist nicht verbunden")

        for entity_id, point in self._points.items():
            entity = self._registry.require(entity_id)

            try:
                data = await self._nodes[entity_id].read_data_value(False)
            except Exception:
                log.exception(
                    "OPC-UA-Lesefehler bei %s",
                    entity_id,
                )
                self._state.apply(
                    entity_id,
                    StateValue.error(
                        unit=entity.unit,
                        source=self.source,
                    ),
                    force=True,
                )
                continue

            status = data.StatusCode
            if not status.is_good():
                if status.name in {
                    "BadNoData",
                    "BadWaitingForInitialData",
                }:
                    value = StateValue.unknown(
                        unit=entity.unit,
                        source=self.source,
                    )
                else:
                    value = StateValue.error(
                        unit=entity.unit,
                        source=self.source,
                    )

                self._state.apply(
                    entity_id,
                    value,
                    force=True,
                )
                continue

            try:
                value = self._coerce(
                    point.type,
                    data.Value.Value,
                )
            except (TypeError, ValueError):
                log.warning(
                    "OPC UA: %s liefert unerwarteten Wert %r",
                    entity_id,
                    data.Value.Value,
                )
                self._state.apply(
                    entity_id,
                    StateValue.invalid(
                        unit=entity.unit,
                        source=self.source,
                    ),
                    force=True,
                )
                continue

            # Die Tankgeber dürfen am oberen Anschlag geringfügig über
            # 100 % melden. Bis einschließlich 102 % bedeutet der Messwert
            # weiterhin schlicht "voll". Die Korrektur geschieht vor der
            # Plausibilitätsprüfung, damit ein Mapping mit max: 100 den
            # tolerierten Rohwert nicht vorher verwirft.
            if (
                entity.id.startswith("water.tank.")
                and entity.unit == "percent"
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
            ):
                value = normalise_tank_percent(float(value))

            if not self._plausible(point, value):
                log.warning(
                    "OPC UA: %s außerhalb Plausibilität: %r",
                    entity_id,
                    value,
                )
                self._state.apply(
                    entity_id,
                    StateValue.invalid(
                        unit=entity.unit,
                        source=self.source,
                    ),
                    force=True,
                )
                continue

            self._state.apply(
                entity_id,
                StateValue.valid(
                    value,
                    unit=entity.unit,
                    source=self.source,
                    measured_at=utcnow(),
                ),
            )

    async def execute(
        self,
        command: Command,
        spec: CommandSpec,
    ) -> None:
        raise RuntimeError(
            "OPC-UA-Stufe 1 ist read-only; Schreiben ist gesperrt"
        )

    @staticmethod
    def _coerce(kind: str, value: Any) -> Any:
        if kind == "float":
            if isinstance(value, bool):
                raise TypeError("Boolean ist kein Float-Messwert")
            return float(value)

        if kind == "int":
            if isinstance(value, bool):
                raise TypeError("Boolean ist kein Integer-Messwert")
            return int(value)

        if kind == "bool":
            if not isinstance(value, bool):
                raise TypeError("Wert ist kein Boolean")
            return value

        if kind == "string":
            if not isinstance(value, str):
                raise TypeError("Wert ist kein String")
            return value

        raise ValueError(f"Unbekannter Mapping-Typ: {kind}")

    @staticmethod
    def _plausible(
        point: OpcUaReadPointConfig,
        value: Any,
    ) -> bool:
        limits = point.plausibility
        if limits is None:
            return True
        if not isinstance(value, (int, float)):
            return True

        if limits.min is not None and value < limits.min:
            return False
        return not (limits.max is not None and value > limits.max)
