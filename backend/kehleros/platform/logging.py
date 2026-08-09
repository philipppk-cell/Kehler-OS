"""Strukturierte Protokollierung.

Logs sind für die Fehlersuche da und werden deshalb maschinenlesbar erzeugt
(Kapitel 16 §27). Die Correlation-ID verbindet alle Stationen eines Vorgangs
und macht aus verstreuten Zeilen eine nachvollziehbare Kette (Kapitel 16 §28).

Geheimnisse gehören nie in Logs (Kapitel 15 §51). Deshalb filtert ein
Formatierer bekannte Schlüsselwörter heraus, bevor etwas geschrieben wird.
"""

from __future__ import annotations

import logging
import re
import sys

_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|passwort|token|secret|api[_-]?key|authorization)\b"
    r"\s*[=:]\s*\S+"
)


class SecretFilter(logging.Filter):
    """Ersetzt offensichtliche Geheimnisse in Logtexten.

    Das ist eine letzte Sicherung, kein Freibrief: Geheimnisse gehören gar
    nicht erst in eine Logmeldung.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _SECRET_PATTERN.sub(r"\1=***", record.msg)
        return True


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)-28s  %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    handler.addFilter(SecretFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Der Webserver protokolliert seine Zugriffe selbst; das würde die
    # eigentlichen Systemmeldungen zudecken.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
