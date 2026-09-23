"""Lokale Anbindung des Smart-Life-Fußbodenheizungs-Thermostats.

Das Thermostat bleibt selbst Regler. Kehler OS liest seinen Zustand und
setzt ausschließlich die am realen Gerät bestätigten Tuya-Datenpunkte.

Es gibt bewusst keinen generischen DPID-Schreibweg.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any

import tinytuya

from ..config.hardware import TuyaThermostatDeviceConfig
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..domain.enums import Source
from ..domain.models import Command, CommandSpec, StateValue
from .base import Adapter


STATE_ID = "heating.floor.state"
ACTUAL_ID = "heating.floor.temperature.actual"
TARGET_ID = "heating.floor.temperature.target"
MODE_ID = "heating.floor.mode"
ECO_ID = "heating.floor.eco"
DEMAND_ID = "heating.floor.demand"
CHILD_LOCK_ID = "heating.floor.child_lock"

ENTITY_IDS = [
    STATE_ID,
    ACTUAL_ID,
    TARGET_ID,
    MODE_ID,
    ECO_ID,
    DEMAND_ID,
    CHILD_LOCK_ID,
]

DP_SWITCH = 1
DP_MODE = 2
DP_ECO = 4
DP_TARGET = 16
DP_CURRENT = 24
DP_VALVE = 36
DP_CHILD_LOCK = 40


class TuyaThermostatAdapter(Adapter):
    """Fußbodenheizungs-Thermostat über lokales Tuya-Protokoll."""

    name = "tuya-floor"
    source = Source.SENSOR

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        registry: Registry,
        device: TuyaThermostatDeviceConfig,
        *,
        device_factory: Callable[..., Any] = tinytuya.Device,
    ) -> None:
        super().__init__(
            state,
            events,
            entity_ids=ENTITY_IDS,
            poll_interval_s=device.poll_interval_ms / 1000.0,
        )

        self._registry = registry
        self._config = device
        self._device_factory = device_factory
        self._device: Any | None = None

        for entity_id in ENTITY_IDS:
            if registry.get(entity_id) is None:
                raise ValueError(
                    f"Tuya-Thermostat-Entity fehlt: {entity_id}"
                )

    @staticmethod
    def _load_credentials(filename: str) -> dict[str, str]:
        path = Path(filename).expanduser()

        if not path.is_file():
            raise RuntimeError(
                f"Tuya-Zugangsdaten fehlen: {path}"
            )

        result: dict[str, str] = {}

        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()

        required = (
            "TUYA_FLOOR_DEVICE_ID",
            "TUYA_FLOOR_LOCAL_KEY",
        )

        missing = [
            key
            for key in required
            if not result.get(key)
        ]

        if missing:
            raise RuntimeError(
                "Tuya-Zugangsdaten unvollständig: "
                + ", ".join(missing)
            )

        return result

    async def connect(self) -> None:
        credentials = self._load_credentials(
            self._config.connection.credentials_file
        )

        device = self._device_factory(
            credentials["TUYA_FLOOR_DEVICE_ID"],
            self._config.connection.address,
            credentials["TUYA_FLOOR_LOCAL_KEY"],
            version=self._config.connection.version,
        )

        device.set_socketTimeout(5)
        self._device = device

        # Beim Verbindungsaufbau muss einmal ein echter Status erfolgreich
        # gelesen werden. Erst danach meldet der Adapter ONLINE.
        result = await asyncio.to_thread(device.status)
        self._apply_status(result)

    async def disconnect(self) -> None:
        self._device = None

    async def poll(self) -> None:
        device = self._require_device()
        result = await asyncio.to_thread(device.status)
        self._apply_status(result)

    async def execute(
        self,
        command: Command,
        spec: CommandSpec,
    ) -> None:
        del spec

        device = self._require_device()

        if command.entity_id == STATE_ID:
            raw = self._switch_value(command)
            dp = DP_SWITCH

        elif command.entity_id == TARGET_ID:
            requested = command.params.get("value")

            if (
                not isinstance(requested, (int, float))
                or isinstance(requested, bool)
            ):
                raise RuntimeError(
                    "Solltemperatur muss numerisch sein"
                )

            raw = int(round(float(requested) * 10))
            dp = DP_TARGET

        elif command.entity_id == MODE_ID:
            state = command.params.get("state")

            if state not in ("AUTO", "MANUAL"):
                raise RuntimeError(
                    "Unbekannter Thermostat-Modus"
                )

            raw = str(state).lower()
            dp = DP_MODE

        elif command.entity_id == ECO_ID:
            raw = self._switch_value(command)
            dp = DP_ECO

        elif command.entity_id == CHILD_LOCK_ID:
            raw = self._switch_value(command)
            dp = DP_CHILD_LOCK

        else:
            raise RuntimeError(
                f"Schreiben auf {command.entity_id} nicht freigegeben"
            )

        result = await asyncio.to_thread(
            device.set_value,
            dp,
            raw,
        )

        if isinstance(result, dict) and result.get("Error"):
            raise RuntimeError(
                f"Tuya-Schreibfehler: {result['Error']}"
            )

        # Direkt vom Gerät zurücklesen. Der Command Bus bestätigt dadurch
        # ausschließlich den echten Hardwarezustand und nicht den gesendeten
        # Wunschwert.
        await asyncio.sleep(0.15)
        await self.poll()

    @staticmethod
    def _switch_value(command: Command) -> bool:
        state = command.params.get("state")

        if state == "ON":
            return True
        if state == "OFF":
            return False

        raise RuntimeError(
            "Schaltzustand muss ON oder OFF sein"
        )

    def _apply_status(self, result: Any) -> None:
        if not isinstance(result, dict):
            raise RuntimeError(
                "Tuya lieferte keinen gültigen Status"
            )

        dps = result.get("dps")

        if not isinstance(dps, dict):
            raise RuntimeError(
                "Tuya-Status enthält keine DPS"
            )

        self._apply_switch(
            STATE_ID,
            self._dp(dps, DP_SWITCH),
        )

        self._apply_temperature(
            ACTUAL_ID,
            self._dp(dps, DP_CURRENT),
        )

        self._apply_temperature(
            TARGET_ID,
            self._dp(dps, DP_TARGET),
        )

        mode = self._dp(dps, DP_MODE)

        if isinstance(mode, str) and mode.lower() in {
            "auto",
            "manual",
        }:
            self._valid(
                MODE_ID,
                mode.upper(),
            )
        else:
            self._invalid(MODE_ID)

        self._apply_switch(
            ECO_ID,
            self._dp(dps, DP_ECO),
        )

        valve = self._dp(dps, DP_VALVE)

        if valve == "open":
            self._valid(DEMAND_ID, "HEATING")
        elif valve == "close":
            self._valid(DEMAND_ID, "IDLE")
        else:
            self._invalid(DEMAND_ID)

        self._apply_switch(
            CHILD_LOCK_ID,
            self._dp(dps, DP_CHILD_LOCK),
        )

    @staticmethod
    def _dp(dps: dict[Any, Any], number: int) -> Any:
        return dps.get(str(number), dps.get(number))

    def _apply_switch(
        self,
        entity_id: str,
        raw: Any,
    ) -> None:
        if isinstance(raw, bool):
            self._valid(
                entity_id,
                "ON" if raw else "OFF",
            )
        else:
            self._invalid(entity_id)

    def _apply_temperature(
        self,
        entity_id: str,
        raw: Any,
    ) -> None:
        if (
            isinstance(raw, (int, float))
            and not isinstance(raw, bool)
        ):
            self._valid(
                entity_id,
                float(raw) / 10.0,
            )
        else:
            self._invalid(entity_id)

    def _valid(
        self,
        entity_id: str,
        value: Any,
    ) -> None:
        entity = self._registry.require(entity_id)

        self._state.apply(
            entity_id,
            StateValue.valid(
                value,
                unit=entity.unit,
                source=self.source,
            ),
        )

    def _invalid(self, entity_id: str) -> None:
        entity = self._registry.require(entity_id)

        self._state.apply(
            entity_id,
            StateValue.invalid(
                unit=entity.unit,
                source=self.source,
            ),
            force=True,
        )

    def _require_device(self) -> Any:
        if self._device is None:
            raise RuntimeError(
                "Tuya-Thermostat ist nicht verbunden"
            )

        return self._device
