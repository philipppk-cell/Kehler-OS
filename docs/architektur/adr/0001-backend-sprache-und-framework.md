# ADR 0001 – Backendsprache und Webframework

**Status:** angenommen · Phase 1
**Bezug:** Kapitel 12 §18, Kapitel 17 §12/§74, Kapitel 18 §86/§87

## Entscheidung

**Python 3.12+ mit asyncio, FastAPI (Starlette/uvicorn) und Pydantic v2.**

## Kontext

Das Backend muss auf einem Raspberry Pi 5 dauerhaft laufen und gleichzeitig
mit einer Siemens-SPS, einem Victron-Cerbo, mehreren Clients, einer Datenbank
und einer Automatisierungsengine umgehen. Die Last ist praktisch vollständig
**I/O-gebunden**: warten auf Netzwerkantworten, nicht rechnen.

## Abwägung

**Python** — gewählt.
Der entscheidende Punkt ist die Bibliothekslage für genau diesen
Hardwarestack: `asyncua` für OPC UA, `python-snap7` für S7-Kommunikation,
`aiomqtt` für den Victron-Broker, `pymodbus` für Modbus TCP. Alle vier sind
gepflegt, dokumentiert und auf ARM64 verfügbar. In keiner anderen Sprache
liegen alle vier gleichzeitig in dieser Reife vor.

Der oft angeführte Nachteil — der GIL — trifft hier nicht: Bei I/O-gebundener
Last gibt asyncio den Interpreter während jeder Wartezeit frei. Ein
Durchsatzproblem ist bei den erwarteten Datenraten (einige hundert Datenpunkte,
Aktualisierung im Sekundenbereich) nicht zu erwarten.

Typisierung erfüllt Kapitel 18 §83 über moderne Type Hints plus **Pydantic v2**,
das zusätzlich zur statischen Prüfung eine *Laufzeitvalidierung* liefert. Das
ist für dieses Projekt mehr wert als reine Compile-Zeit-Typen, weil die
gefährlichen Daten von außen kommen: aus der SPS, aus MQTT, aus API-Aufrufen.
Kapitel 15 §44 verlangt genau diese Validierung.

**Go** — verworfen.
Technisch attraktiv (geringer Speicherbedarf, echte Nebenläufigkeit, ein
statisches Binary vereinfacht das Deployment). Verworfen wegen der
Bibliothekslage: `gos7` ist deutlich weniger gepflegt als snap7, und der
OPC-UA-Client ist weniger ausgereift als `asyncua`. Kapitel 12 §82 verlangt
für Industrieschnittstellen ausdrücklich stabile, gut dokumentierte Lösungen.

**Rust** — verworfen.
Beste Laufzeiteigenschaften, aber die schwächste Bibliotheksabdeckung für
S7/Victron und die höchste Hürde für Kapitel 17 §119: Ein anderer qualifizierter
Entwickler soll das Projekt später übernehmen können.

**Node.js/TypeScript** — verworfen.
Durchgehend eine Sprache für Front- und Backend wäre ein echter Vorteil.
Die S7-Anbindung hängt jedoch an `node-snap7`/`nodes7`, die native Builds
erfordern und weniger aktiv gepflegt sind. Für eine Komponente, die später
Fahrzeugaktoren schaltet, ist das das falsche Fundament.

## Framework

**FastAPI** liefert asynchrone Endpunkte, native WebSocket-Unterstützung,
Pydantic-Integration und automatische OpenAPI-Dokumentation. Versionierung
(Kapitel 5 §16) erfolgt über einen Präfix `/api/v1`. Ausgeführt wird es unter
**uvicorn** als systemd-Dienst.

## Konsequenzen

- Der Speicherbedarf liegt höher als bei Go oder Rust. Auf einem Pi 5 mit
  mindestens 4 GB ist das unkritisch, muss aber überwacht werden
  (Kapitel 17 §96).
- Abhängigkeiten werden mit gepinnten Versionen und Lockfile verwaltet.
- CPU-intensive Aufgaben (Aggregation der Historie, Backups) laufen in einem
  Thread- oder Prozess-Executor, damit sie die Event-Loop nicht blockieren
  (Kapitel 17 §11).
