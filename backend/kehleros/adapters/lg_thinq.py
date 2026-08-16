"""LG-Klimaanlage über die offizielle ThinQ-Connect-API.

Es existiert absichtlich kein generischer ThinQ-Schreibweg. Der Adapter
besitzt nur die ausdrücklich freigegebenen Klima-Entities und Befehle.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aiohttp import ClientSession
from thinqconnect.thinq_api import ThinQApi

from ..config.hardware import LgThinQDeviceConfig
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..domain.enums import Source
from ..domain.models import Command, CommandSpec, StateValue
from .base import Adapter

log = logging.getLogger(__name__)

STATE_ID = "climate.cooling.state"
TARGET_ID = "climate.cooling.target"


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
    ) -> None:
        super().__init__(
            state,
            events,
            entity_ids=[STATE_ID, TARGET_ID],
            poll_interval_s=device.poll_interval_ms / 1000.0,
        )

        self._registry = registry
        self._device = device
        self._session_factory = session_factory
        self._api_factory = api_factory

        self._session: Any | None = None
        self._api: Any | None = None

        # Die Application ruft poll() alle 0,5 s auf. ThinQ selbst wird
        # normalerweise aber nur im konfigurierten Intervall abgefragt.
        #
        # Nach einem Schreibbefehl wird kurzzeitig schneller gelesen, damit
        # der CommandBus nicht mehrere Sekunden auf die echte Rückmeldung
        # warten muss.
        self._normal_poll_interval_s = (
            device.poll_interval_ms / 1000.0
        )
        self._fast_poll_interval_s = 0.75
        self._fast_poll_window_s = 8.0

        self._last_status_poll = 0.0
        self._fast_poll_until = 0.0
        self._fast_expectations: dict[str, Any] = {}

        state_entity = registry.get(STATE_ID)
        target_entity = registry.get(TARGET_ID)

        if state_entity is None:
            raise ValueError(f"ThinQ-Entity fehlt: {STATE_ID}")
        if target_entity is None:
            raise ValueError(f"ThinQ-Entity fehlt: {TARGET_ID}")

        if state_entity.spec_for("set_state") is None:
            raise ValueError(
                f"ThinQ-Entity besitzt kein set_state: {STATE_ID}"
            )

        if target_entity.spec_for("set_value") is None:
            raise ValueError(
                f"ThinQ-Entity besitzt kein set_value: {TARGET_ID}"
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

        for line in path.read_text(encoding="utf-8").splitlines():
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

        missing = [key for key in required if not result.get(key)]

        if missing:
            raise RuntimeError(
                "ThinQ-Zugangsdaten unvollständig: "
                + ", ".join(missing)
            )

        return result

    async def connect(self) -> None:
        credentials = self._load_credentials(
            self._device.connection.credentials_file
        )

        session = self._session_factory()

        api = self._api_factory(
            session=session,
            access_token=credentials["THINQ_PAT"],
            country_code=credentials["THINQ_COUNTRY"],
            client_id=credentials["THINQ_CLIENT_ID"],
        )

        try:
            status = await api.async_get_device_status(
                self._device.connection.device_id
            )
        except Exception:
            await session.close()
            raise

        if not isinstance(status, dict):
            await session.close()
            raise RuntimeError(
                "LG ThinQ lieferte keinen gültigen Gerätestatus"
            )

        self._session = session
        self._api = api

        log.info(
            "LG ThinQ verbunden: %s",
            self._device.model or self._device.name,
        )

    async def disconnect(self) -> None:
        self._api = None

        session = self._session
        self._session = None

        if session is not None:
            await session.close()

    # ── Lesen ───────────────────────────────────────────────────────────

    async def poll(self) -> None:
        api = self._require_api()

        status = await api.async_get_device_status(
            self._device.connection.device_id
        )

        if not isinstance(status, dict):
            raise RuntimeError(
                "LG ThinQ lieferte keinen gültigen Gerätestatus"
            )

        power = self._read_power(status)
        target = self._read_target_temperature(status)

        if power is None:
            self._state.apply(
                STATE_ID,
                StateValue.unknown(source=self.source),
                force=True,
            )
        else:
            self._state.apply(
                STATE_ID,
                StateValue.valid(
                    power,
                    source=self.source,
                ),
            )

        target_entity = self._registry.require(TARGET_ID)

        if target is None:
            self._state.apply(
                TARGET_ID,
                StateValue.unknown(
                    unit=target_entity.unit,
                    source=self.source,
                ),
                force=True,
            )
        else:
            self._state.apply(
                TARGET_ID,
                StateValue.valid(
                    target,
                    unit=target_entity.unit,
                    source=self.source,
                ),
            )

    @staticmethod
    def _find_key(value: Any, wanted: str) -> Any:
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
    def _read_power(cls, status: dict[str, Any]) -> str | None:
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
    def _read_target_temperature(
        cls,
        status: dict[str, Any],
    ) -> float | None:
        # Die ThinQ-API hat je nach Gerät/Firmware zwei beobachtete
        # Darstellungen. Beide werden gelesen; geschrieben wird ausschließlich
        # die am realen Gerät bestätigte temperatureInUnits-Ressource.

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

                raw = item.get("targetTemperature")

                if raw is None:
                    raw = item.get("targetTemperatureC")

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
            return float(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    # ── Schreiben ───────────────────────────────────────────────────────

    async def execute(
        self,
        command: Command,
        spec: CommandSpec,
    ) -> None:
        api = self._require_api()

        if (
            command.entity_id == STATE_ID
            and command.verb == "set_state"
        ):
            requested = str(
                command.params.get("state", "")
            ).upper()

            if requested not in {"ON", "OFF"}:
                raise ValueError(
                    "ThinQ-Klimazustand muss ON oder OFF sein"
                )

            payload = {
                "operation": {
                    "airConOperationMode": (
                        "POWER_ON"
                        if requested == "ON"
                        else "POWER_OFF"
                    )
                }
            }

            await api.async_post_device_control(
                self._device.connection.device_id,
                payload,
            )
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
                    "ThinQ-Solltemperatur muss eine Zahl sein"
                )

            value = float(raw)

            # Reales Gerät: nur ganze °C.
            if not value.is_integer():
                raise ValueError(
                    "LG-Klimaanlage akzeptiert in Kehler OS "
                    "nur ganze °C"
                )

            payload = {
                "temperatureInUnits": {
                    "targetTemperature": int(value),
                    "unit": "C",
                }
            }

            await api.async_post_device_control(
                self._device.connection.device_id,
                payload,
            )
            return

        raise ValueError(
            "Nicht freigegebener ThinQ-Befehl: "
            f"{command.entity_id}.{command.verb}"
        )

    def _require_api(self):
        if self._api is None:
            raise RuntimeError(
                "LG-ThinQ-Adapter ist nicht verbunden"
            )
        return self._api
