"""LG-Klimaanlage über die offizielle ThinQ-Connect-API.

Es existiert absichtlich kein generischer ThinQ-Schreibweg. Der Adapter
besitzt nur die ausdrücklich am realen Fahrzeug bestätigten Klima-Entities
und Befehle.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aiohttp import ClientSession
from thinqconnect.mqtt_client import ThinQMQTTClient
from thinqconnect.thinq_api import ThinQApi, ThinQAPIException

from ..config.hardware import LgThinQDeviceConfig
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..domain.enums import Source
from ..domain.models import Command, CommandSpec, StateValue
from .base import Adapter

log = logging.getLogger(__name__)

INSIDE_ID = "climate.living.temperature"
STATE_ID = "climate.cooling.state"
TARGET_ID = "climate.cooling.target"
MODE_ID = "climate.cooling.mode"
FAN_ID = "climate.cooling.fan"
SWING_VERTICAL_ID = "climate.cooling.swing_vertical"
SWING_HORIZONTAL_ID = "climate.cooling.swing_horizontal"
POWER_SAVE_ID = "climate.cooling.power_save"

MODE_VALUES = frozenset(
    {
        "AUTO",
        "HEAT",
        "AIR_DRY",
        "COOL",
        "FAN",
    }
)

FAN_VALUES = frozenset(
    {
        "AUTO",
        "LOW",
        "MID",
        "HIGH",
    }
)

_SWITCH_IDS = frozenset(
    {
        STATE_ID,
        SWING_VERTICAL_ID,
        SWING_HORIZONTAL_ID,
        POWER_SAVE_ID,
    }
)


class LgThinQAdapter(Adapter):
    """LG DUALCOOL über ThinQ Connect."""

    name = "lg-thinq"
    source = Source.THINQ

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        registry: Registry,
        device: LgThinQDeviceConfig,
        *,
        session_factory: Callable[[], Any] = ClientSession,
        api_factory: Callable[..., Any] = ThinQApi,
        mqtt_factory: Callable[..., Any] = ThinQMQTTClient,
        readback_delay_s: float = 0.8,
    ) -> None:
        entity_ids = [
            INSIDE_ID,
            STATE_ID,
            TARGET_ID,
            MODE_ID,
            FAN_ID,
            SWING_VERTICAL_ID,
            SWING_HORIZONTAL_ID,
            POWER_SAVE_ID,
        ]

        super().__init__(
            state,
            events,
            entity_ids=entity_ids,
            poll_interval_s=device.poll_interval_ms / 1000.0,
        )

        self._registry = registry
        self._device = device
        self._session_factory = session_factory
        self._api_factory = api_factory
        self._mqtt_factory = mqtt_factory
        self._readback_delay_s = readback_delay_s

        self._session: Any | None = None
        self._api: Any | None = None
        self._mqtt: Any | None = None

        # MQTT-Callbacks kommen aus einem AWS-CRT-Thread. Änderungen am
        # StateStore werden deshalb immer zurück in den asyncio-Thread
        # von Kehler OS gereicht.
        self._loop: asyncio.AbstractEventLoop | None = None
        self._mqtt_connected = False
        self._mqtt_disconnected_since: float | None = None

        # ThinQ sendet DEVICE_STATUS-Ereignisse als Patches. Der letzte
        # vollständige bekannte Zustand wird deshalb hier gehalten und
        # jedes MQTT-report darauf zusammengeführt.
        self._status_cache: dict[str, Any] = {}

        for entity_id in entity_ids:
            entity = registry.get(entity_id)

            if entity is None:
                raise ValueError(
                    f"ThinQ-Entity fehlt: {entity_id}"
                )

            # Die Innentemperatur ist ein reiner Messwert des
            # LG-Innengeräts und besitzt absichtlich keinen Befehl.
            if entity_id == INSIDE_ID:
                continue

            expected_verb = (
                "set_value"
                if entity_id == TARGET_ID
                else "set_state"
            )

            if entity.spec_for(expected_verb) is None:
                raise ValueError(
                    f"ThinQ-Entity besitzt kein "
                    f"{expected_verb}: {entity_id}"
                )

    # ── Verbindung ──────────────────────────────────────────────────────

    @staticmethod
    def _load_credentials(filename: str) -> dict[str, str]:
        path = Path(filename).expanduser()

        if not path.is_file():
            raise RuntimeError(
                f"ThinQ-Zugangsdaten fehlen: {path}"
            )

        result: dict[str, str] = {}

        for line in path.read_text(
            encoding="utf-8"
        ).splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()

        required = (
            "THINQ_PAT",
            "THINQ_COUNTRY",
            "THINQ_CLIENT_ID",
        )

        missing = [
            key
            for key in required
            if not result.get(key)
        ]

        if missing:
            raise RuntimeError(
                "ThinQ-Zugangsdaten unvollständig: "
                + ", ".join(missing)
            )

        return result

    async def connect(self) -> None:
        # Nach einem Supervisor-Neustart können noch Ressourcen des
        # vorherigen Versuchs existieren.
        if self._session is not None or self._mqtt is not None:
            await self.disconnect()

        credentials = self._load_credentials(
            self._device.connection.credentials_file
        )

        self._loop = asyncio.get_running_loop()

        session = self._session_factory()

        api = self._api_factory(
            session=session,
            access_token=credentials["THINQ_PAT"],
            country_code=credentials["THINQ_COUNTRY"],
            client_id=credentials["THINQ_CLIENT_ID"],
        )

        self._session = session
        self._api = api
        self._mqtt = None
        self._mqtt_connected = False
        self._mqtt_disconnected_since = None
        self._status_cache = {}

        try:
            # Genau EIN Status-GET beim Start. Danach übernimmt MQTT.
            status = await api.async_get_device_status(
                self._device.connection.device_id
            )

            if not isinstance(status, dict):
                raise RuntimeError(
                    "LG ThinQ lieferte keinen gültigen "
                    "Gerätestatus"
                )

            self._status_cache = dict(status)
            self._apply_status(self._status_cache)

            # Test-Doubles aus den Unit-Tests besitzen teilweise nur
            # Status/Control. In diesem Fall bleibt der alte REST-Testpfad
            # erhalten; das echte ThinQApi besitzt alle folgenden Methoden.
            required_mqtt_api = (
                "async_get_route",
                "async_post_client_register",
                "async_post_client_certificate",
                "async_post_event_subscribe",
            )

            if not all(
                callable(getattr(api, name, None))
                for name in required_mqtt_api
            ):
                log.debug(
                    "LG ThinQ: API-Testdouble ohne MQTT-Unterstützung"
                )
                return

            mqtt = self._mqtt_factory(
                thinq_api=api,
                client_id=credentials["THINQ_CLIENT_ID"],
                on_message_received=self._on_mqtt_message,
                on_connection_interrupted=(
                    self._on_mqtt_connection_interrupted
                ),
                on_connection_success=(
                    self._on_mqtt_connection_success
                ),
                on_connection_failure=(
                    self._on_mqtt_connection_failure
                ),
                on_connection_closed=(
                    self._on_mqtt_connection_closed
                ),
            )

            self._mqtt = mqtt

            await mqtt.async_init()

            prepared = await mqtt.async_prepare_mqtt()

            if not prepared:
                raise RuntimeError(
                    "LG ThinQ MQTT konnte nicht vorbereitet werden"
                )

            # DEVICE_STATUS-Events aktivieren. Die Subscription besitzt
            # bei LG eine lange Laufzeit und wird beim Start erneuert.
            try:
                await api.async_post_event_subscribe(
                    self._device.connection.device_id
                )
            except ThinQAPIException as exc:
                # 1312 bedeutet, dass das Event-Subscription-Limit
                # erreicht ist. Eine bereits vorhandene Subscription
                # kann trotzdem weiter funktionieren.
                if str(exc.code) != "1312":
                    raise

                log.warning(
                    "LG ThinQ Event-Subscription bereits am Limit; "
                    "vorhandene Subscription wird weiterverwendet"
                )

            await mqtt.async_connect_mqtt()

            if not mqtt.is_connected:
                raise RuntimeError(
                    "LG ThinQ MQTT-Verbindung konnte nicht "
                    "aufgebaut werden"
                )

            self._mqtt_connected = True
            self._mqtt_disconnected_since = None

        except Exception:
            mqtt = self._mqtt
            self._mqtt = None
            self._mqtt_connected = False

            if (
                mqtt is not None
                and getattr(mqtt, "is_connected", False)
            ):
                try:
                    await mqtt.async_disconnect()
                except Exception:
                    log.exception(
                        "LG ThinQ MQTT ließ sich nach "
                        "Startfehler nicht sauber abbauen"
                    )

            self._api = None
            self._session = None

            await session.close()
            raise

        log.info(
            "LG ThinQ verbunden: %s (MQTT Push aktiv)",
            self._device.model or self._device.name,
        )

    async def disconnect(self) -> None:
        mqtt = self._mqtt
        self._mqtt = None

        self._mqtt_connected = False
        self._mqtt_disconnected_since = None

        if mqtt is not None:
            try:
                await mqtt.async_disconnect()
            except Exception as exc:
                # Beim Herunterfahren darf ein verlorenes Internet den
                # gesamten Kehler-OS-Shutdown nicht blockieren.
                log.warning(
                    "LG ThinQ MQTT konnte nicht sauber "
                    "getrennt werden: %s",
                    exc,
                )

        self._api = None

        session = self._session
        self._session = None

        if session is not None:
            await session.close()

        self._loop = None

    # ── MQTT Push ───────────────────────────────────────────────────────

    def _on_mqtt_message(
        self,
        topic: str,
        payload: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        del topic, args, kwargs

        try:
            if isinstance(payload, (bytes, bytearray)):
                raw = bytes(payload).decode("utf-8")
            else:
                raw = str(payload)

            message = json.loads(raw)

        except Exception as exc:
            log.warning(
                "LG ThinQ: ungültiges MQTT-Event: %s",
                exc,
            )
            return

        if not isinstance(message, dict):
            return

        loop = self._loop

        if loop is None or loop.is_closed():
            return

        loop.call_soon_threadsafe(
            self._handle_mqtt_message,
            message,
        )

    def _handle_mqtt_message(
        self,
        message: dict[str, Any],
    ) -> None:
        if message.get("pushType") != "DEVICE_STATUS":
            return

        if (
            message.get("deviceId")
            != self._device.connection.device_id
        ):
            return

        report = message.get("report")

        if not isinstance(report, dict):
            return

        # Wichtig: LG sendet häufig nur das geänderte Feld.
        # Beispiel:
        # {"temperature": {"targetTemperature": 19}}
        #
        # Deshalb niemals report direkt als kompletten Status behandeln.
        self._deep_merge(
            self._status_cache,
            report,
        )

        self._apply_status(self._status_cache)

        log.debug(
            "LG ThinQ MQTT DEVICE_STATUS übernommen"
        )

    @classmethod
    def _deep_merge(
        cls,
        target: dict[str, Any],
        patch: dict[str, Any],
    ) -> None:
        """Führt ein partielles ThinQ-report in den Status-Cache ein."""

        for key, value in patch.items():
            current = target.get(key)

            if (
                isinstance(current, dict)
                and isinstance(value, dict)
            ):
                cls._deep_merge(current, value)
                continue

            if isinstance(value, dict):
                target[key] = dict(value)
            else:
                # Listen wie temperatureInUnits werden vollständig
                # ersetzt. Die semantischen Werte lesen wir zusätzlich
                # aus den normalen Ressourcen-Dictionaries.
                target[key] = value

    def _queue_mqtt_connection_state(
        self,
        connected: bool,
    ) -> None:
        loop = self._loop

        if loop is None or loop.is_closed():
            return

        loop.call_soon_threadsafe(
            self._set_mqtt_connection_state,
            connected,
        )

    def _on_mqtt_connection_interrupted(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        del args, kwargs
        self._queue_mqtt_connection_state(False)

    def _on_mqtt_connection_failure(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        del args, kwargs
        self._queue_mqtt_connection_state(False)

    def _on_mqtt_connection_closed(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        del args, kwargs
        self._queue_mqtt_connection_state(False)

    def _on_mqtt_connection_success(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        del args, kwargs
        self._queue_mqtt_connection_state(True)

    def _set_mqtt_connection_state(
        self,
        connected: bool,
    ) -> None:
        if connected:
            reconnected = (
                self._mqtt_disconnected_since is not None
            )

            self._mqtt_connected = True
            self._mqtt_disconnected_since = None

            if reconnected and self._api is not None:
                # Nach einem echten Verbindungsabbruch genau EINEN
                # Status-Read durchführen. Das ist kein Dauerpolling.
                asyncio.create_task(
                    self._refresh_after_mqtt_reconnect()
                )

            return

        if self._mqtt_disconnected_since is None:
            try:
                self._mqtt_disconnected_since = (
                    asyncio.get_running_loop().time()
                )
            except RuntimeError:
                self._mqtt_disconnected_since = 0.0

        self._mqtt_connected = False

        log.warning(
            "LG ThinQ MQTT-Verbindung unterbrochen"
        )

    async def _refresh_after_mqtt_reconnect(
        self,
    ) -> None:
        api = self._api

        if api is None:
            return

        try:
            status = await api.async_get_device_status(
                self._device.connection.device_id
            )
        except Exception as exc:
            # MQTT funktioniert bereits wieder. Ein fehlgeschlagener
            # einmaliger REST-Refresh darf deshalb keinen Crash-Loop
            # verursachen.
            log.warning(
                "LG ThinQ: Status-Refresh nach MQTT-Reconnect "
                "fehlgeschlagen: %s",
                exc,
            )
            return

        if isinstance(status, dict):
            self._status_cache = dict(status)
            self._apply_status(self._status_cache)

    # ── Lesen ───────────────────────────────────────────────────────────

    async def poll(self) -> None:
        """Überwacht MQTT, ohne ThinQ permanent per REST abzufragen."""

        # Kompatibilitätsweg für Unit-Test-Doubles ohne MQTT.
        if self._mqtt is None:
            api = self._require_api()

            status = await api.async_get_device_status(
                self._device.connection.device_id
            )

            if not isinstance(status, dict):
                raise RuntimeError(
                    "LG ThinQ lieferte keinen gültigen "
                    "Gerätestatus"
                )

            self._status_cache = dict(status)
            self._apply_status(self._status_cache)
            return

        if self._mqtt_connected:
            # Kein Netzwerkrequest. Eine aktive MQTT-Subscription
            # garantiert, dass Änderungen als Push eintreffen.
            #
            # Das erneute Anwenden hält die vorhandenen Werte frisch,
            # ohne Hardwarezustände zu erfinden oder LG zu pollen.
            if self._status_cache:
                self._apply_status(self._status_cache)

            return

        now = asyncio.get_running_loop().time()

        if self._mqtt_disconnected_since is None:
            self._mqtt_disconnected_since = now
            return

        # AWS IoT bekommt Zeit für seinen eigenen automatischen
        # Reconnect. Erst nach zwei Minuten übergeben wir den Fehler
        # an den Kehler-OS-Supervisor.
        if now - self._mqtt_disconnected_since < 120.0:
            return

        raise RuntimeError(
            "LG ThinQ MQTT seit mehr als 120 s getrennt"
        )

    def _apply_status(
        self,
        status: dict[str, Any],
    ) -> None:
        values: dict[str, Any] = {
            INSIDE_ID: self._read_current_temperature(status),
            STATE_ID: self._read_power(status),
            TARGET_ID: self._read_target_temperature(
                status
            ),
            MODE_ID: self._read_mode(status),
            FAN_ID: self._read_fan(status),
            SWING_VERTICAL_ID: self._read_boolean(
                status,
                "windDirection",
                "rotateUpDown",
            ),
            SWING_HORIZONTAL_ID: self._read_boolean(
                status,
                "windDirection",
                "rotateLeftRight",
            ),
            POWER_SAVE_ID: self._read_boolean(
                status,
                "powerSave",
                "powerSaveEnabled",
            ),
        }

        for entity_id, value in values.items():
            entity = self._registry.require(entity_id)

            if value is None:
                self._state.apply(
                    entity_id,
                    StateValue.unknown(
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
                ),
            )

    @staticmethod
    def _find_key(
        value: Any,
        wanted: str,
    ) -> Any:
        if isinstance(value, dict):
            if wanted in value:
                return value[wanted]

            for child in value.values():
                result = LgThinQAdapter._find_key(
                    child,
                    wanted,
                )

                if result is not None:
                    return result

        elif isinstance(value, list):
            for child in value:
                result = LgThinQAdapter._find_key(
                    child,
                    wanted,
                )

                if result is not None:
                    return result

        return None

    @classmethod
    def _read_current_temperature(
        cls,
        status: dict[str, Any],
    ) -> float | None:
        """Liest die vom LG-Innengerät gemessene Raumtemperatur in °C."""

        def as_number(raw: Any) -> float | None:
            if isinstance(raw, bool):
                return None

            try:
                value = float(raw)
            except (TypeError, ValueError):
                return None

            if not math.isfinite(value):
                return None

            return value

        # MQTT DEVICE_STATUS des realen Geräts:
        #
        # "temperature": {
        #     "currentTemperature": 31,
        #     "targetTemperature": 18,
        #     "unit": "C"
        # }
        temperature = status.get("temperature")

        if isinstance(temperature, dict):
            unit = str(
                temperature.get("unit", "C")
            ).upper()

            if unit in {"C", "CELSIUS"}:
                value = as_number(
                    temperature.get(
                        "currentTemperature"
                    )
                )

                if value is not None:
                    return value

        # REST-Status / alternatives ThinQ-Format:
        #
        # "temperatureInUnits": [
        #     {
        #         "currentTemperature": 24.5,
        #         "targetTemperature": 18,
        #         "unit": "C"
        #     }
        # ]
        temperatures = status.get(
            "temperatureInUnits"
        )

        if isinstance(temperatures, list):
            for item in temperatures:
                if not isinstance(item, dict):
                    continue

                if (
                    str(
                        item.get("unit", "")
                    ).upper()
                    != "C"
                ):
                    continue

                value = as_number(
                    item.get(
                        "currentTemperature"
                    )
                )

                if value is not None:
                    return value

        return None

    @classmethod
    def _read_power(
        cls,
        status: dict[str, Any],
    ) -> str | None:
        raw = cls._find_key(
            status,
            "airConOperationMode",
        )

        if raw is None:
            return None

        value = str(raw).upper()

        if value in {"POWER_ON", "ON"}:
            return "ON"

        if value in {"POWER_OFF", "OFF"}:
            return "OFF"

        log.warning(
            "LG ThinQ: unbekannter Power-Zustand %r",
            raw,
        )
        return None

    @classmethod
    def _read_mode(
        cls,
        status: dict[str, Any],
    ) -> str | None:
        raw = cls._find_key(
            status,
            "currentJobMode",
        )

        if raw is None:
            return None

        value = str(raw).upper()

        if value in MODE_VALUES:
            return value

        log.warning(
            "LG ThinQ: unbekannte Betriebsart %r",
            raw,
        )
        return None

    @classmethod
    def _read_fan(
        cls,
        status: dict[str, Any],
    ) -> str | None:
        raw = None

        air_flow = status.get("airFlow")

        if isinstance(air_flow, dict):
            raw = air_flow.get("windStrength")

            if raw is None:
                raw = air_flow.get(
                    "windStrengthDetail"
                )

        if raw is None:
            raw = cls._find_key(
                status,
                "windStrength",
            )

        if raw is None:
            return None

        value = str(raw).upper()

        if value in FAN_VALUES:
            return value

        log.warning(
            "LG ThinQ: unbekannte Lüfterstufe %r",
            raw,
        )
        return None

    @classmethod
    def _read_boolean(
        cls,
        status: dict[str, Any],
        resource_name: str,
        key: str,
    ) -> str | None:
        raw = None

        resource = status.get(resource_name)

        if isinstance(resource, dict):
            raw = resource.get(key)

        if raw is None:
            raw = cls._find_key(status, key)

        if isinstance(raw, bool):
            return "ON" if raw else "OFF"

        if raw is not None:
            log.warning(
                "LG ThinQ: %s ist kein Boolean: %r",
                key,
                raw,
            )

        return None

    @classmethod
    def _read_target_temperature(
        cls,
        status: dict[str, Any],
    ) -> float | None:
        for resource_name in (
            "temperatureInUnits",
            "temperature",
        ):
            resource = status.get(resource_name)

            candidates: list[dict[str, Any]] = []

            if isinstance(resource, dict):
                candidates.append(resource)

            elif isinstance(resource, list):
                candidates.extend(
                    item
                    for item in resource
                    if isinstance(item, dict)
                )

            for item in candidates:
                unit = item.get("unit")

                if unit not in (None, "C"):
                    continue

                raw = item.get(
                    "targetTemperature"
                )

                if raw is None:
                    raw = item.get(
                        "targetTemperatureC"
                    )

                if raw is None:
                    continue

                try:
                    return float(raw)
                except (TypeError, ValueError):
                    return None

        raw = cls._find_key(
            status,
            "targetTemperature",
        )

        try:
            return (
                float(raw)
                if raw is not None
                else None
            )
        except (TypeError, ValueError):
            return None

    # ── Schreiben ───────────────────────────────────────────────────────

    async def execute(
        self,
        command: Command,
        spec: CommandSpec,
    ) -> None:
        del spec

        if (
            command.entity_id == STATE_ID
            and command.verb == "set_state"
        ):
            requested = self._switch_value(command)

            payload = {
                "operation": {
                    "airConOperationMode": (
                        "POWER_ON"
                        if requested == "ON"
                        else "POWER_OFF"
                    )
                }
            }

            await self._post_and_readback(payload)
            return

        if (
            command.entity_id == TARGET_ID
            and command.verb == "set_value"
        ):
            raw = command.params.get("value")

            if (
                not isinstance(raw, (int, float))
                or isinstance(raw, bool)
            ):
                raise ValueError(
                    "ThinQ-Solltemperatur muss "
                    "eine Zahl sein"
                )

            value = float(raw)

            # Das reale Gerät wurde mit ganzen °C bestätigt.
            if not value.is_integer():
                raise ValueError(
                    "LG-Klimaanlage akzeptiert in "
                    "Kehler OS nur ganze °C"
                )

            payload = {
                "temperatureInUnits": {
                    "targetTemperature": int(value),
                    "unit": "C",
                }
            }

            await self._post_and_readback(payload)
            return

        if (
            command.entity_id == MODE_ID
            and command.verb == "set_state"
        ):
            requested = str(
                command.params.get("state", "")
            ).upper()

            if requested not in MODE_VALUES:
                raise ValueError(
                    "Nicht freigegebene "
                    f"ThinQ-Betriebsart: {requested}"
                )

            await self._post_and_readback(
                {
                    "airConJobMode": {
                        "currentJobMode": requested
                    }
                }
            )
            return

        if (
            command.entity_id == FAN_ID
            and command.verb == "set_state"
        ):
            requested = str(
                command.params.get("state", "")
            ).upper()

            if requested not in FAN_VALUES:
                raise ValueError(
                    "Nicht freigegebene "
                    f"ThinQ-Lüfterstufe: {requested}"
                )

            await self._post_and_readback(
                {
                    "airFlow": {
                        "windStrength": requested
                    }
                }
            )
            return

        if (
            command.entity_id
            == SWING_VERTICAL_ID
            and command.verb == "set_state"
        ):
            requested = self._switch_value(command)

            await self._post_and_readback(
                {
                    "windDirection": {
                        "rotateUpDown": (
                            requested == "ON"
                        )
                    }
                }
            )
            return

        if (
            command.entity_id
            == SWING_HORIZONTAL_ID
            and command.verb == "set_state"
        ):
            requested = self._switch_value(command)

            await self._post_and_readback(
                {
                    "windDirection": {
                        "rotateLeftRight": (
                            requested == "ON"
                        )
                    }
                }
            )
            return

        if (
            command.entity_id == POWER_SAVE_ID
            and command.verb == "set_state"
        ):
            requested = self._switch_value(command)

            await self._post_and_readback(
                {
                    "powerSave": {
                        "powerSaveEnabled": (
                            requested == "ON"
                        )
                    }
                }
            )
            return

        raise ValueError(
            "Nicht freigegebener ThinQ-Befehl: "
            f"{command.entity_id}.{command.verb}"
        )

    @staticmethod
    def _switch_value(
        command: Command,
    ) -> str:
        requested = str(
            command.params.get("state", "")
        ).upper()

        if requested not in {"ON", "OFF"}:
            raise ValueError(
                "ThinQ-Schaltzustand muss "
                "ON oder OFF sein"
            )

        return requested

    async def _post_and_readback(
        self,
        payload: dict[str, Any],
    ) -> None:
        """Sendet einen freigegebenen ThinQ-Befehl.

        Im echten Betrieb kommt die Hardwarebestätigung ausschließlich
        über MQTT DEVICE_STATUS. Dadurch entsteht nach einem Befehl kein
        zusätzlicher REST-Statusaufruf.

        Der kleine REST-Readback unten existiert nur für injizierte
        Test-Doubles, die keine MQTT-Schnittstelle besitzen.
        """

        api = self._require_api()

        await api.async_post_device_control(
            self._device.connection.device_id,
            payload,
        )

        # Echter Betrieb: auf das MQTT-Event der Klimaanlage warten.
        if self._mqtt is not None:
            return

        # Unit-Test-/Fallback-Pfad ohne MQTT.
        if self._readback_delay_s > 0:
            await asyncio.sleep(
                self._readback_delay_s
            )

        try:
            status = await api.async_get_device_status(
                self._device.connection.device_id
            )
        except Exception as exc:
            log.info(
                "LG ThinQ: Test/Fallback-Readback "
                "nicht verfügbar: %s",
                exc,
            )
            return

        if isinstance(status, dict):
            self._status_cache = dict(status)
            self._apply_status(self._status_cache)

    def _require_api(self):
        if self._api is None:
            raise RuntimeError(
                "LG-ThinQ-Adapter ist nicht verbunden"
            )

        return self._api
