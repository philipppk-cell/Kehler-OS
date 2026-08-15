"""Validierte Hardwarekonfiguration für reale Adapter.

Die Fahrzeugbeschreibung sagt, was das Fahrzeug besitzt. Dieses Modul liest
die lokalen, nicht versionierten Dateien unter ``config/hardware`` und kennt
damit reale Verbindungsdaten und NodeIds.

Stufe 1 lädt ausschließlich lesende SPS-Datenpunkte.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from ..domain.ids import validate_entity_id
from .loader import ConfigError, load_yaml


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OpcUaConnectionConfig(_Strict):
    endpoint: str
    security: str | None = None
    username_env: str | None = None
    password_env: str | None = None
    allow_insecure: bool = False

    @field_validator("endpoint")
    @classmethod
    def _endpoint_is_opc_tcp(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("opc.tcp://"):
            raise ValueError(
                "OPC-UA-Endpunkt muss mit 'opc.tcp://' beginnen"
            )
        return value


class OpcUaPlcDeviceConfig(_Strict):
    id: Literal["plc"] = "plc"
    name: str = "Siemens SPS"
    kind: Literal["PLC"] = "PLC"
    vendor: str | None = None
    model: str | None = None
    transport: Literal["opcua"]
    connection: OpcUaConnectionConfig
    poll_interval_ms: int = Field(default=1000, ge=100, le=60_000)


class PlausibilityConfig(_Strict):
    min: float | None = None
    max: float | None = None


class OpcUaReadPointConfig(_Strict):
    id: str
    device: Literal["plc"] = "plc"
    direction: Literal["read"] = "read"
    type: Literal["bool", "int", "float", "string"]
    ref: str
    plausibility: PlausibilityConfig | None = None

    @field_validator("id")
    @classmethod
    def _valid_entity_id(cls, value: str) -> str:
        return validate_entity_id(value)

    @field_validator("ref")
    @classmethod
    def _real_reference(cls, value: str) -> str:
        value = value.strip()
        if not value or "<TODO" in value.upper():
            raise ValueError("OPC-UA-NodeId fehlt")
        if not value.startswith("ns="):
            raise ValueError("OPC-UA-NodeId muss mit 'ns=' beginnen")
        return value


class OpcUaWritePointConfig(_Strict):
    """Explizit freigegebener OPC-UA-Schreibbefehl.

    Kehler OS kann damit nicht beliebige NodeIds beschreiben. Jede erlaubte
    Kombination aus Entity und Verb muss einzeln im lokalen Hardware-Mapping
    hinterlegt sein.
    """

    id: str
    device: Literal["plc"] = "plc"
    direction: Literal["write"] = "write"
    verb: str
    type: Literal["bool"] = "bool"
    ref: str
    mode: Literal["pulse", "hold"] = "pulse"
    pulse_ms: int = Field(default=100, ge=50, le=500)
    # Bei hold muss Kehler OS den Befehl regelmäßig erneuern.
    # Bleibt die Erneuerung aus, wird der Eingang automatisch zurückgesetzt.
    hold_timeout_ms: int = Field(default=800, ge=300, le=5000)

    @field_validator("id")
    @classmethod
    def _valid_entity_id(cls, value: str) -> str:
        return validate_entity_id(value)

    @field_validator("verb")
    @classmethod
    def _valid_verb(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Schreibverb fehlt")
        return value

    @field_validator("ref")
    @classmethod
    def _real_reference(cls, value: str) -> str:
        value = value.strip()
        if not value or "<TODO" in value.upper():
            raise ValueError("OPC-UA-NodeId fehlt")
        if not value.startswith("ns="):
            raise ValueError("OPC-UA-NodeId muss mit 'ns=' beginnen")
        return value


def load_plc_device(path: Path) -> OpcUaPlcDeviceConfig:
    data = load_yaml(path)
    devices = data.get("devices")
    if not isinstance(devices, list):
        raise ConfigError(f"{path}: 'devices' muss eine Liste sein")

    raw = next(
        (
            item
            for item in devices
            if isinstance(item, dict) and item.get("id") == "plc"
        ),
        None,
    )
    if raw is None:
        raise ConfigError(f"{path}: Gerät 'plc' fehlt")

    try:
        device = OpcUaPlcDeviceConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(
            f"SPS-Konfiguration {path} ist ungültig:\n{exc}"
        ) from exc

    if (
        device.connection.security is None
        and not device.connection.allow_insecure
    ):
        raise ConfigError(
            f"{path}: ungesicherte OPC-UA-Verbindung nicht freigegeben"
        )

    return device


def load_plc_read_points(path: Path) -> list[OpcUaReadPointConfig]:
    data = load_yaml(path)
    datapoints = data.get("datapoints")
    if not isinstance(datapoints, list):
        raise ConfigError(f"{path}: 'datapoints' muss eine Liste sein")

    result: list[OpcUaReadPointConfig] = []
    seen: set[str] = set()

    for raw in datapoints:
        if not isinstance(raw, dict):
            raise ConfigError(
                f"{path}: jeder Datenpunkt muss eine Zuordnung sein"
            )
        if raw.get("device") != "plc" or raw.get("direction") != "read":
            continue

        try:
            point = OpcUaReadPointConfig.model_validate(raw)
        except ValidationError as exc:
            raise ConfigError(
                f"Ungültiger SPS-Datenpunkt in {path}:\n{exc}"
            ) from exc

        if point.id in seen:
            raise ConfigError(
                f"{path}: Datenpunkt '{point.id}' ist doppelt"
            )

        seen.add(point.id)
        result.append(point)

    if not result:
        raise ConfigError(
            f"{path}: kein lesender SPS-Datenpunkt konfiguriert"
        )

    return result



def load_plc_write_points(path: Path) -> list[OpcUaWritePointConfig]:
    """Lädt ausschließlich explizit freigegebene SPS-Schreibbefehle."""

    data = load_yaml(path)
    datapoints = data.get("datapoints")
    if not isinstance(datapoints, list):
        raise ConfigError(f"{path}: 'datapoints' muss eine Liste sein")

    result: list[OpcUaWritePointConfig] = []
    seen: set[tuple[str, str]] = set()

    for raw in datapoints:
        if not isinstance(raw, dict):
            raise ConfigError(
                f"{path}: jeder Datenpunkt muss eine Zuordnung sein"
            )

        if raw.get("device") != "plc" or raw.get("direction") != "write":
            continue

        try:
            point = OpcUaWritePointConfig.model_validate(raw)
        except ValidationError as exc:
            raise ConfigError(
                f"Ungültiger SPS-Schreibpunkt in {path}:\n{exc}"
            ) from exc

        key = (point.id, point.verb)
        if key in seen:
            raise ConfigError(
                f"{path}: Schreibpunkt '{point.id}.{point.verb}' ist doppelt"
            )

        seen.add(key)
        result.append(point)

    return result
