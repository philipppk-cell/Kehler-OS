"""Zeichnet eine laufende Kehler-OS-Sitzung für die Demo auf.

Die Demo spielt **echte Ausgaben des Backends** ab. Sie rechnet nichts nach:
Ob ein Tank 62 % hat und ob daraus 341 Liter werden, entscheidet weiterhin
``core/water.py`` — nur eben zum Zeitpunkt der Aufzeichnung statt live.

Das ist die einzige Bauart, die zum Rest des Projekts passt. Die Alternative
wäre gewesen, die Deutungen in JavaScript nachzubilden — also genau die
Geschäftslogik zu verdoppeln, die Kapitel 18 §6 im Backend halten will. Zwei
Umsetzungen derselben Regel laufen auseinander, und dann zeigt die Demo etwas
anderes als das Fahrzeug.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8000/api/v1"

# Einmalig: ändert sich zur Laufzeit nicht.
STATIC = ["/vehicle", "/diagnostics/adapters", "/diagnostics/simulation"]

# Je Einzelbild: der bewegliche Teil.
PER_FRAME = ["/system", "/water", "/energy", "/heating", "/alerts", "/diagnostics/services"]

# Verläufe für die Messgrößen, die die Oberfläche anbietet.
HISTORY = [
    "water.tank.fresh.large",
    "water.tank.fresh.small",
    "water.tank.grey",
    "water.tank.black",
    "energy.battery.soc",
    "energy.battery.voltage",
    "energy.solar.power",
    "energy.consumption.power",
]
HISTORY_SPANS = [6, 24, 168, 720]


def get(path: str) -> object:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as response:
        return json.load(response)


def post(path: str, body: dict[str, object]) -> None:
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10):
        pass


def stage(index: int, total: int) -> None:
    """Erzeugt während der Aufnahme gezielt die interessanten Zustände.

    Eine Aufzeichnung, in der nichts passiert, zeigt nur die halbe Oberfläche:
    Wie ein Fehler aussieht, wie eine Warnung aussieht und wie das System sich
    wieder fängt, ist der Teil, auf den es ankommt (Kapitel 18 §65/§71).

    Vorher gesetzte Zustände genügen dafür nicht — ein hoch gesetzter Tank
    driftet binnen Minuten wieder unter die Schwelle, und die Warnung war beim
    ersten Versuch prompt verschwunden, bevor die Aufnahme begann.
    """
    if index == 0:
        post("/diagnostics/simulation/level", {"entity_id": "water.tank.grey", "value": 87})
    elif index == total // 3:
        post(
            "/diagnostics/simulation/fault",
            {"entity_id": "water.tank.fresh.small", "fault": "SENSOR_ERROR"},
        )
    elif index == (2 * total) // 3:
        post(
            "/diagnostics/simulation/fault",
            {"entity_id": "water.tank.fresh.small", "fault": "NONE"},
        )


def main(frames: int, interval: float, out: Path) -> int:
    print(f"Zeichne {frames} Bilder im Abstand von {interval} s auf …")

    static = {path: get(path) for path in STATIC}

    entities = get("/entities")
    assert isinstance(entities, list)

    # Die Definitionen stehen einmal da. Sie machen den Großteil der Datenmenge
    # aus und ändern sich nicht — sie je Einzelbild zu wiederholen, hätte die
    # Datei vervierfacht.
    definitions = {
        entry["entity_id"]: entry["definition"]
        for entry in entities
        if entry.get("definition")
    }

    recorded: list[dict[str, object]] = []
    for index in range(frames):
        stage(index, frames)
        states = get("/entities")
        assert isinstance(states, list)

        recorded.append(
            {
                "entities": [
                    {
                        "entity_id": entry["entity_id"],
                        "seq": entry["seq"],
                        "link": entry["link"],
                        "state": entry["state"],
                    }
                    for entry in states
                ],
                **{path: get(path) for path in PER_FRAME},
            }
        )
        print(f"  {index + 1}/{frames}", end="\r", flush=True)
        if index + 1 < frames:
            time.sleep(interval)

    history = {
        f"{entity_id}:{hours}": get(f"/history/{entity_id}?hours={hours}")
        for entity_id in HISTORY
        for hours in HISTORY_SPANS
    }

    payload = {
        "recordedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "intervalMs": int(interval * 1000),
        "static": static,
        "definitions": definitions,
        "frames": recorded,
        "history": history,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"\n{out} — {out.stat().st_size / 1024:.0f} kB, {len(recorded)} Bilder")
    return 0


if __name__ == "__main__":
    frames = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
    raise SystemExit(main(frames, interval, Path("tools/demo/recording.json")))
