"""Victron-Cerbo-GX-Anbindung über lokales MQTT.

Der Adapter liest ausschließlich explizit gemappte N/...-Topics und schreibt
ausschließlich explizit freigegebene W/...-Topics. Es gibt keinen generischen
MQTT-Schreibweg.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import math
import os
import ssl
from collections.abc import Callable
from typing import Any

import aiomqtt

from ..config.hardware import (
    VictronMqttDeviceConfig,
    VictronReadPointConfig,
    VictronWritePointConfig,
)
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..domain.enums import Source
from ..domain.models import Command, CommandSpec, StateValue
from .base import Adapter

log = logging.getLogger(__name__)


class _UnmappedValue(ValueError):
    pass


class VictronMqttAdapter(Adapter):
    """Cerbo GX über den lokalen MQTT-Broker."""

    name = "victron-mqtt"
    source = Source.VICTRON

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        registry: Registry,
        device: VictronMqttDeviceConfig,
        read_points: list[VictronReadPointConfig],
        write_points: list[VictronWritePointConfig],
        *,
        client_factory: Callable[..., Any] = aiomqtt.Client,
    ) -> None:
        entity_ids = sorted(
            {
                point.id
                for point in [*read_points, *write_points]
            }
        )

        super().__init__(
            state,
            events,
            entity_ids=entity_ids,
            poll_interval_s=device.poll_interval_ms / 1000.0,
        )

        self._registry = registry
        self._device = device
        self._client_factory = client_factory

        self._client: Any | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._last_keepalive = 0.0
        self._last_refresh = 0.0
        self._refresh_interval_s = 1.0

        self._read_by_topic: dict[str, VictronReadPointConfig] = {}
        self._write_by_key: dict[
            tuple[str, str],
            VictronWritePointConfig,
        ] = {}

        for point in read_points:
            entity = registry.get(point.id)
            if entity is None:
                raise ValueError(
                    "Unbekannte Entity im Victron-Mapping: "
                    f"{point.id}"
                )

            topic = self._notification_topic(point.path)
            if topic in self._read_by_topic:
                raise ValueError(
                    f"Doppeltes Victron-Topic: {topic}"
                )

            self._read_by_topic[topic] = point

        for point in write_points:
            entity = registry.get(point.id)
            if entity is None:
                raise ValueError(
                    "Unbekannte Entity im Victron-Write-Mapping: "
                    f"{point.id}"
                )

            if entity.spec_for(point.verb) is None:
                raise ValueError(
                    "Victron-Write verweist auf fehlende Capability: "
                    f"{point.id}.{point.verb}"
                )

            key = (point.id, point.verb)
            if key in self._write_by_key:
                raise ValueError(
                    "Doppeltes Victron-Write-Mapping: "
                    f"{point.id}.{point.verb}"
                )

            self._write_by_key[key] = point

    # ── Verbindung ──────────────────────────────────────────────────────

    async def connect(self) -> None:
        connection = self._device.connection

        username = None
        password = None

        if connection.username_env:
            username = os.environ.get(connection.username_env)
            if not username:
                raise RuntimeError(
                    "Victron-MQTT-Benutzer fehlt in "
                    f"${connection.username_env}"
                )

        if connection.password_env:
            password = os.environ.get(connection.password_env)
            if not password:
                raise RuntimeError(
                    "Victron-MQTT-Passwort fehlt in "
                    f"${connection.password_env}"
                )

        kwargs: dict[str, Any] = {
            "hostname": connection.host,
            "port": connection.mqtt_port,
            "username": username,
            "password": password,
            "keepalive": 60,
            "timeout": 5,
        }

        if connection.tls:
            kwargs["tls_context"] = ssl.create_default_context()

        client = self._client_factory(**kwargs)

        await client.__aenter__()

        try:
            for topic in self._read_by_topic:
                await client.subscribe(topic)

            self._client = client

            # Beim ersten Connect brauchen wir einmal einen vollständigen
            # aktuellen Bestand, da aktuelle Venus-Versionen MQTT-Werte
            # nicht mehr als Retained Messages vorhalten.
            await self._send_keepalive(full=True)

            now = asyncio.get_running_loop().time()
            self._last_keepalive = now
            self._last_refresh = now

            self._reader_task = asyncio.create_task(
                self._reader(),
                name="victron-mqtt-reader",
            )
        except Exception:
            self._client = None
            await client.__aexit__(None, None, None)
            raise

        log.info(
            "Victron MQTT verbunden: %s:%d (%d read, %d write)",
            connection.host,
            connection.mqtt_port,
            len(self._read_by_topic),
            len(self._write_by_key),
        )

    async def disconnect(self) -> None:
        task = self._reader_task
        self._reader_task = None

        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        client = self._client
        self._client = None

        if client is not None:
            await client.__aexit__(None, None, None)

    async def poll(self) -> None:
        client = self._client
        if client is None:
            raise RuntimeError("Victron-MQTT-Client ist nicht verbunden")

        task = self._reader_task
        if task is None:
            raise RuntimeError("Victron-MQTT-Reader läuft nicht")

        if task.done():
            task.result()
            raise RuntimeError("Victron-MQTT-Reader wurde beendet")

        loop = asyncio.get_running_loop()
        now = loop.time()

        if now - self._last_refresh >= self._refresh_interval_s:
            await self._refresh_mapped_values()
            self._last_refresh = now

        if (
            now - self._last_keepalive
            >= self._device.keepalive_interval_s
        ):
            await self._send_keepalive(full=False)
            self._last_keepalive = now

    async def _refresh_mapped_values(self) -> None:
        """Fordert alle explizit gemappten Victron-Werte neu an.

        Venus OS hält die N/...-Werte nicht zuverlässig als Retained
        Messages vor. Deshalb werden ausschließlich die bereits
        freigegebenen Read-Mappings regelmäßig über R/... angefordert.
        """
        client = self._client
        if client is None:
            raise RuntimeError(
                "Victron-MQTT-Client ist nicht verbunden"
            )

        for point in self._read_by_topic.values():
            await client.publish(
                self._read_topic(point.path),
                payload="",
                retain=False,
            )

    async def _reader(self) -> None:
        client = self._client
        if client is None:
            raise RuntimeError("Victron-MQTT-Client fehlt")

        async for message in client.messages:
            self._handle_message(message)

        raise RuntimeError("Victron-MQTT-Nachrichtenstrom beendet")

    # ── MQTT-Nachrichten ────────────────────────────────────────────────

    def _handle_message(self, message: Any) -> None:
        topic_object = message.topic
        topic = getattr(topic_object, "value", str(topic_object))

        point = self._read_by_topic.get(topic)
        if point is None:
            return

        entity = self._registry.require(point.id)
        payload = message.payload

        # Venus meldet einen verschwundenen D-Bus-Service mit leerem
        # Payload. Das ist UNKNOWN, nicht 0.
        if not payload:
            self._state.apply(
                point.id,
                StateValue.unknown(
                    unit=entity.unit,
                    source=self.source,
                ),
                force=True,
            )
            return

        try:
            document = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
            log.warning(
                "Victron MQTT: ungültiges JSON bei %s: %r",
                point.id,
                payload,
            )
            self._set_invalid(point.id)
            return

        if not isinstance(document, dict) or "value" not in document:
            log.warning(
                "Victron MQTT: Payload ohne value bei %s",
                point.id,
            )
            self._set_invalid(point.id)
            return

        raw = document["value"]

        if raw is None:
            self._state.apply(
                point.id,
                StateValue.unknown(
                    unit=entity.unit,
                    source=self.source,
                ),
                force=True,
            )
            return

        try:
            value = self._coerce_read(point, raw)
        except _UnmappedValue:
            log.info(
                "Victron MQTT: %s liefert nicht gemappten Wert %r",
                point.id,
                raw,
            )
            self._state.apply(
                point.id,
                StateValue.unknown(
                    unit=entity.unit,
                    source=self.source,
                ),
                force=True,
            )
            return
        except (TypeError, ValueError):
            log.warning(
                "Victron MQTT: %s liefert unerwarteten Wert %r",
                point.id,
                raw,
            )
            self._set_invalid(point.id)
            return

        if not self._plausible(point, value):
            log.warning(
                "Victron MQTT: %s außerhalb Plausibilität: %r",
                point.id,
                value,
            )
            self._set_invalid(point.id)
            return

        self._state.apply(
            point.id,
            StateValue.valid(
                value,
                unit=entity.unit,
                source=self.source,
            ),
        )

    def _set_invalid(self, entity_id: str) -> None:
        entity = self._registry.require(entity_id)
        self._state.apply(
            entity_id,
            StateValue.invalid(
                unit=entity.unit,
                source=self.source,
            ),
            force=True,
        )

    @classmethod
    def _coerce_read(
        cls,
        point: VictronReadPointConfig,
        raw: Any,
    ) -> Any:
        if point.type == "mapped":
            assert point.values is not None
            key = cls._raw_key(raw)
            if key not in point.values:
                raise _UnmappedValue(key)
            return point.values[key]

        if point.type == "float":
            if isinstance(raw, bool):
                raise TypeError("Boolean ist kein Float")
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError("Nicht-endlicher Float")
            return value

        if point.type == "int":
            if isinstance(raw, bool):
                raise TypeError("Boolean ist kein Integer")
            value = float(raw)
            if not value.is_integer():
                raise ValueError("Integer erwartet")
            return int(value)

        if point.type == "bool":
            if not isinstance(raw, bool):
                raise TypeError("Boolean erwartet")
            return raw

        if point.type == "string":
            if not isinstance(raw, str):
                raise TypeError("String erwartet")
            return raw

        raise ValueError(f"Unbekannter Victron-Typ: {point.type}")

    @staticmethod
    def _raw_key(raw: Any) -> str:
        if isinstance(raw, bool):
            return "true" if raw else "false"
        if isinstance(raw, float) and raw.is_integer():
            return str(int(raw))
        return str(raw)

    @staticmethod
    def _plausible(
        point: VictronReadPointConfig,
        value: Any,
    ) -> bool:
        limits = point.plausibility
        if limits is None:
            return True

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        ):
            return True

        if limits.min is not None and value < limits.min:
            return False
        return not (
            limits.max is not None and value > limits.max
        )

    # ── Schreiben ───────────────────────────────────────────────────────

    async def execute(
        self,
        command: Command,
        spec: CommandSpec,
    ) -> None:
        del spec

        client = self._client
        if client is None:
            raise RuntimeError("Victron-MQTT-Client ist nicht verbunden")

        point = self._write_by_key.get(
            (command.entity_id, command.verb)
        )
        if point is None:
            raise RuntimeError(
                "Kein Victron-MQTT-Schreibmapping für "
                f"{command.entity_id}.{command.verb}"
            )

        if point.param not in command.params:
            raise RuntimeError(
                f"Parameter '{point.param}' fehlt"
            )

        requested = command.params[point.param]

        if point.type == "float":
            if (
                not isinstance(requested, (int, float))
                or isinstance(requested, bool)
            ):
                raise RuntimeError("Victron-Schreibwert muss numerisch sein")

            raw: Any = float(requested)

        elif point.type == "mapped":
            assert point.values is not None
            key = str(requested)

            if key not in point.values:
                raise RuntimeError(
                    f"Victron-Wert '{key}' ist nicht freigegeben"
                )

            raw = point.values[key]

        else:
            raise RuntimeError(
                f"Unbekannter Victron-Schreibtyp: {point.type}"
            )

        payload = json.dumps(
            {"value": raw},
            separators=(",", ":"),
        )

        await client.publish(
            self._write_topic(point.path),
            payload=payload,
            retain=False,
        )

        # Explizit neu lesen. Ein Write auf denselben bereits vorhandenen
        # Wert erzeugt nicht zwingend eine Änderungsmeldung; die Rücklesung
        # gibt dem Command Bus trotzdem eine bestätigte Wahrheit.
        await client.publish(
            self._read_topic(point.path),
            payload="",
            retain=False,
        )

    # ── Topics / Keepalive ──────────────────────────────────────────────

    async def _send_keepalive(self, *, full: bool) -> None:
        client = self._client
        if client is None:
            raise RuntimeError("Victron-MQTT-Client ist nicht verbunden")

        if full:
            payload = ""
        else:
            payload = json.dumps(
                {
                    "keepalive-options": [
                        "suppress-republish"
                    ]
                },
                separators=(",", ":"),
            )

        await client.publish(
            f"R/{self._device.connection.portal_id}/keepalive",
            payload=payload,
            retain=False,
        )

    def _notification_topic(self, path: str) -> str:
        return (
            f"N/{self._device.connection.portal_id}/{path}"
        )

    def _read_topic(self, path: str) -> str:
        return (
            f"R/{self._device.connection.portal_id}/{path}"
        )

    def _write_topic(self, path: str) -> str:
        return (
            f"W/{self._device.connection.portal_id}/{path}"
        )
