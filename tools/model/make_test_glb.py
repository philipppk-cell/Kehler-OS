"""Erzeugt ein Test-Fahrzeugmodell als `.glb`.

Nicht zum Ausliefern, sondern zum **Beweisen**: Der Ladeweg für ein geliefertes
Modell lässt sich sonst nicht prüfen, solange kein Modell da ist — und ein
ungeprüfter Ladeweg ist ein Versprechen, kein Merkmal.

Das Modell ist absichtlich hässlich. Vier Kästen genügen, um genau das zu
zeigen, worauf es ankommt:

* Es hat Animationen mit den Namen ``garage``, ``step`` und ``awning``.
* Es hat **keine** für ``door``. Damit lässt sich prüfen, ob ein fehlendes
  Teil auch als fehlend gemeldet wird, statt still unterzugehen.

Ohne Fremdbibliotheken: glTF ist JSON plus ein Binärblock, und ein `.glb` ist
beides mit einem Kopf davor. Für vier Kästen lohnt keine Abhängigkeit.

    python tools/model/make_test_glb.py <zielpfad.glb>
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

# Ein Kasten: acht Ecken, zwölf Dreiecke.
ECKEN = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]
DREIECKE = [
    0,
    1,
    2,
    0,
    2,
    3,  # hinten
    4,
    6,
    5,
    4,
    7,
    6,  # vorn
    0,
    4,
    5,
    0,
    5,
    1,  # unten
    3,
    2,
    6,
    3,
    6,
    7,  # oben
    0,
    3,
    7,
    0,
    7,
    4,  # links
    1,
    5,
    6,
    1,
    6,
    2,  # rechts
]

# name, Größe, Position, Bewegungsziel (None = unbeweglich)
TEILE = [
    ("aufbau", (11.5, 2.6, 2.55), (0.0, 0.6, 0.0), None),
    ("garage", (1.6, 1.4, 0.1), (9.0, 0.7, 1.2), (9.0, 2.1, 1.2)),
    ("step", (0.9, 0.1, 0.6), (3.0, 0.2, 2.5), (3.0, 0.2, 3.2)),
    ("awning", (5.0, 0.1, 0.2), (4.0, 3.0, 2.6), (4.0, 3.0, 5.0)),
    # „door" fehlt bewusst — siehe Kopf dieser Datei.
]


def box(groesse: tuple[float, float, float]) -> bytes:
    sx, sy, sz = groesse
    return b"".join(struct.pack("<fff", x * sx, y * sy, z * sz) for x, y, z in ECKEN)


def ausrichten(daten: bytearray, vielfaches: int = 4, fueller: int = 0) -> None:
    while len(daten) % vielfaches:
        daten.append(fueller)


def main(ziel: Path) -> int:
    puffer = bytearray()
    accessors: list[dict] = []
    meshes: list[dict] = []
    nodes: list[dict] = []
    views: list[dict] = []
    animationen: list[dict] = []

    def ablegen(rohdaten: bytes, ziel_typ: int | None = None) -> int:
        ausrichten(puffer)
        start = len(puffer)
        puffer.extend(rohdaten)
        views.append(
            {"buffer": 0, "byteOffset": start, "byteLength": len(rohdaten)}
            | ({"target": ziel_typ} if ziel_typ else {})
        )
        return len(views) - 1

    indexdaten = struct.pack(f"<{len(DREIECKE)}H", *DREIECKE)
    index_view = ablegen(indexdaten, 34963)
    accessors.append(
        {
            "bufferView": index_view,
            "componentType": 5123,
            "count": len(DREIECKE),
            "type": "SCALAR",
            "max": [max(DREIECKE)],
            "min": [min(DREIECKE)],
        }
    )
    INDEX = 0

    for name, groesse, position, ziel_pos in TEILE:
        view = ablegen(box(groesse), 34962)
        accessors.append(
            {
                "bufferView": view,
                "componentType": 5126,
                "count": len(ECKEN),
                "type": "VEC3",
                "min": [0.0, 0.0, 0.0],
                "max": list(groesse),
            }
        )
        pos_accessor = len(accessors) - 1

        meshes.append(
            {
                "name": name,
                "primitives": [
                    {"attributes": {"POSITION": pos_accessor}, "indices": INDEX}
                ],
            }
        )
        nodes.append(
            {"name": name, "mesh": len(meshes) - 1, "translation": list(position)}
        )

        if ziel_pos is None:
            continue

        # Eine Animation je bewegliches Teil, benannt wie der Zustand. Sie
        # läuft von geschlossen (t = 0) bis offen (t = 1). Kehler OS setzt nur
        # die Stelle darin — den Weg bestimmt das Modell.
        zeit_view = ablegen(struct.pack("<ff", 0.0, 1.0))
        accessors.append(
            {
                "bufferView": zeit_view,
                "componentType": 5126,
                "count": 2,
                "type": "SCALAR",
                "min": [0.0],
                "max": [1.0],
            }
        )
        zeit_accessor = len(accessors) - 1

        wert_view = ablegen(struct.pack("<ffffff", *position, *ziel_pos))
        accessors.append(
            {
                "bufferView": wert_view,
                "componentType": 5126,
                "count": 2,
                "type": "VEC3",
            }
        )
        wert_accessor = len(accessors) - 1

        animationen.append(
            {
                "name": name,
                "samplers": [
                    {
                        "input": zeit_accessor,
                        "output": wert_accessor,
                        "interpolation": "LINEAR",
                    }
                ],
                "channels": [
                    {
                        "sampler": 0,
                        "target": {"node": len(nodes) - 1, "path": "translation"},
                    }
                ],
            }
        )

    ausrichten(puffer)

    gltf = {
        "asset": {"version": "2.0", "generator": "Kehler OS Testmodell"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(puffer)}],
        "animations": animationen,
    }

    json_teil = bytearray(json.dumps(gltf, separators=(",", ":")).encode())
    ausrichten(json_teil, fueller=0x20)  # JSON wird mit Leerzeichen aufgefüllt

    gesamt = 12 + 8 + len(json_teil) + 8 + len(puffer)
    glb = bytearray()
    glb += struct.pack("<III", 0x46546C67, 2, gesamt)
    glb += struct.pack("<II", len(json_teil), 0x4E4F534A) + json_teil
    glb += struct.pack("<II", len(puffer), 0x004E4942) + puffer

    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes(glb)
    print(
        f"{ziel} — {len(glb)} Bytes, {len(animationen)} Animationen: "
        f"{', '.join(a['name'] for a in animationen)}"
    )
    return 0


if __name__ == "__main__":
    pfad = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("testmodell.glb")
    raise SystemExit(main(pfad))
