# Entwicklung

Kehler OS läuft vollständig ohne das Fahrzeug. Alles, was hier beschrieben ist,
funktioniert auf einem normalen Rechner.

## Voraussetzungen

Python 3.11 oder neuer. Diese Version bringt Raspberry Pi OS (Bookworm) mit —
auf dem Zielgerät wird also nichts zusätzlich installiert.

## Einrichten

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Starten

```bash
python -m kehleros.main --vehicle ../config/vehicle/vehicle.yaml
```

Danach:

| Adresse | Inhalt |
| --- | --- |
| `http://127.0.0.1:8000/api/v1/system` | Gesamtzustand, Betriebsart, Dienste |
| `http://127.0.0.1:8000/api/v1/entities` | alle Entities mit Zustand und Fähigkeiten |
| `http://127.0.0.1:8000/api/v1/docs` | API-Dokumentation |
| `ws://127.0.0.1:8000/api/v1/realtime` | Snapshot und Zustandsänderungen |

Beim Start meldet das Log unübersehbar:

```
WARNING  SIMULATION — es wird keine reale Fahrzeughardware gesteuert
```

Und `GET /api/v1/system` liefert `"simulated": true`. Eine Verwechslung mit dem
Produktivbetrieb ist damit ausgeschlossen (Kapitel 18 §66).

## Ein Befehl von Hand

```bash
curl -X POST http://127.0.0.1:8000/api/v1/commands \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"light.exterior.entry","verb":"set_state","params":{"state":"ON"}}'
```

Der Statuscode sagt die Wahrheit über das Ergebnis:

| Code | Bedeutung |
| --- | --- |
| `200` | Hardware hat den Zustand bestätigt |
| `409` | abgewiesen — fehlende Berechtigung, Fähigkeit, Konfiguration oder laufende Bewegung |
| `502` | Adapter konnte den Befehl nicht absetzen |
| `504` | keine Rückmeldung innerhalb des Timeouts |

**Ein Befehl liefert niemals `200`, solange die Hardware nichts bestätigt hat.**
Das ist die zentrale Zusicherung des Projekts, und sie ist im Statuscode
sichtbar.

## Fehler ausprobieren

Der Simulator kann gezielt Fehlerbilder erzeugen. Eine Simulation, die nur den
Normalfall kennt, wäre wertlos (Kapitel 18 §65).

```python
from kehleros.adapters.simulation import Fault

simulation = application.adapters[0]

simulation.inject("water.tank.fresh", Fault.SENSOR_ERROR)     # Kabelbruch
simulation.inject("water.tank.grey", Fault.SENSOR_INVALID)    # unmöglicher Wert
simulation.inject("climate.living.temperature", Fault.SILENT) # Sensor verstummt
simulation.inject("vehicle.garage.door", Fault.BLOCKED)       # Mechanik klemmt
simulation.clear_faults()
```

Beobachtenswert:

- `SILENT` sendet einfach nichts mehr. Der Wert altert von selbst zu `STALE`
  und danach zu `UNKNOWN` — genau wie bei einem echten verstummten Sensor.
- `BLOCKED` lässt einen Öffnungsbefehl in einen Timeout laufen. Der Zustand
  bleibt `BLOCKED`, und die Oberfläche behauptet **nicht**, das Tor sei offen.

## Tests

```bash
cd backend
pytest              # alle Tests
pytest -k command   # nur die Befehlskette
ruff check .        # Stil und einfache Fehler
```

Die Tests prüfen bewusst schwerpunktmäßig die Fehlerfälle: `UNKNOWN`,
`OFFLINE`, `TIMEOUT`, `INVALID`, fehlende Berechtigung, fehlende Konfiguration
(Kapitel 18 §71). Der Normalfall ist der kleinere Teil.

## Aufbau des Backends

```
kehleros/
├── domain/       Vokabular: Zustände, Qualität, Befehle, Ereignisse
├── core/         State Store · Command Bus · Event Bus · Registry
├── adapters/     einzige Stelle mit Hardwarewissen
├── config/       Laden und Validieren der Konfiguration
├── platform/     Logging, Dienstüberwachung
├── api/          HTTP und WebSocket
└── application.py  Zusammenbau
```

Drei Regeln, die beim Weiterentwickeln nicht verhandelbar sind:

**Nur Adapter schreiben in den State Store.** Ein Befehl verändert den Zustand
nie selbst — er löst eine Hardwareänderung aus, die zurückgemeldet wird.

**Oberhalb der Adapterschicht existiert keine Hardwareadresse.** Wer eine
braucht, gehört in einen Adapter oder in die Mapping-Konfiguration.

**`UNKNOWN` wird nie zu `0`, `OFF` oder `CLOSED`.** `StateValue` setzt das
technisch durch: Bei jeder Qualität außer `VALID` wird der Wert verworfen.

## Eine Entity hinzufügen

Es genügt ein Eintrag in der Fahrzeugkonfiguration:

```yaml
entities:
  - id: light.interior.bedroom
    name_key: light.bedroom
    type: switch
    area: bedroom
```

Der Typ bestimmt die Fähigkeiten — `measurement` bekommt keine Befehle,
`switch` bekommt `set_state`, `movable` bekommt `open`/`close`/`stop`. Der
Simulator leitet sein Verhalten daraus ab, und die Oberfläche bietet
automatisch genau das an, was möglich ist.

Fehlt die Hardwarezuordnung, wird `configured: false` gesetzt. Dann erscheint
die Entity als „Nicht konfiguriert“ und nimmt keine Befehle an — statt einen
Zustand zu erfinden (Kapitel 18 §101).

## Was noch fehlt

Reale Adapter für SPS und Victron. Sie kommen mit M8 und M9, sobald die
offenen Punkte in [`OPEN_HARDWARE_REQUIREMENTS.md`](OPEN_HARDWARE_REQUIREMENTS.md)
geklärt sind. Bis dahin wird in `production` **kein** Adapter geladen und
entsprechend gewarnt — es wird kein Ersatz erfunden.
