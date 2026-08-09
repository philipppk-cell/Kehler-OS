"""Einstiegspunkt.

Wird im Fahrzeug als systemd-Dienst gestartet — ohne Terminalbefehle und ohne
sichtbaren Desktop (Kapitel 17 §32/§34).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from .application import Application
from .config.loader import ConfigError
from .platform.logging import setup_logging

log = logging.getLogger(__name__)

DEFAULT_VEHICLE = Path("config/vehicle/vehicle.yaml")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="kehleros", description="Kehler OS Backend")
    parser.add_argument(
        "--vehicle",
        type=Path,
        default=Path(os.environ.get("KEHLEROS_VEHICLE", DEFAULT_VEHICLE)),
        help="Fahrzeugkonfiguration (YAML)",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        default=Path(p) if (p := os.environ.get("KEHLEROS_SETTINGS")) else None,
        help="Laufzeiteinstellungen (YAML)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(os.environ.get("KEHLEROS_LOG_LEVEL", "INFO"))

    try:
        application = Application.from_config(args.vehicle, args.settings)
    except ConfigError as exc:
        # Eine unbrauchbare Konfiguration wird beim Start gemeldet und nicht
        # halb übernommen (Kapitel 15 §76/§77).
        log.error("Start abgebrochen: %s", exc)
        return 2

    import uvicorn

    from .api.http import create_app

    uvicorn.run(
        create_app(application),
        host=application.settings.server.host,
        port=application.settings.server.port,
        log_config=None,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
