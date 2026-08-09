# Kehler OS

Betriebssystem für ein Expeditions- und Luxus-LKW-Wohnmobil.

Kehler OS führt sämtliche technischen Systeme des Fahrzeugs unter einer
einzigen Oberfläche zusammen — Energie, Wasser, Klima, Licht, Aufbaufunktionen,
Nivellierung, Diagnose und Automatisierung. Für den Benutzer entsteht ein
zusammenhängendes System, keine Sammlung einzelner Apps.

**Status:** Backend-Kern und Simulation laufen. Das System ist ohne Fahrzeug
startbar und vollständig bedienbar — die reale Hardwareanbindung folgt, sobald
die offenen Punkte geklärt sind.

---

## Grundsätze

Drei Regeln prägen jede Entscheidung in diesem Projekt:

**Die Oberfläche behauptet nie einen Zustand, den die Hardware nicht bestätigt
hat.** Ein gesendeter Befehl ist kein erreichter Zustand. Ein unerreichbarer
Sensor bedeutet nicht „null“, sondern „unbekannt“.

**Die Oberfläche ist keine Sicherheitseinrichtung.** Wo eine Bewegung unzulässig
ist, muss die Steuerung sie selbst verhindern. Kehler OS blendet den Befehl
zusätzlich aus, verlässt sich aber nie darauf.

**Das Fahrzeug funktioniert ohne Internet.** Cloud, Fernzugriff und KI sind
Erweiterungen, keine Voraussetzungen.

---

## Plattform

| Rolle | Komponente |
| --- | --- |
| Softwareplattform | Raspberry Pi 5 |
| Echtzeitsteuerung | Siemens S7-1511-1 PN |
| Energiesystem | Victron mit Cerbo GX, MultiPlus, 24-V-Batteriesystem |
| Bedienung | zentrales Touchdisplay, ergänzend iPad, Smartphone, Laptop |

Die Aufgabenteilung ist verbindlich: Die SPS steuert in Echtzeit und arbeitet
unabhängig vom Raspberry Pi weiter. Victron bleibt für Energie und deren
Schutzfunktionen zuständig. Kehler OS ist die übergeordnete Plattform —
Visualisierung, Logik, Historie, Automatisierung.

---

## Technologie

| Ebene | Wahl | Begründung |
| --- | --- | --- |
| Backend | Python 3.12 · asyncio · FastAPI · Pydantic v2 | [ADR 0001](docs/architektur/adr/0001-backend-sprache-und-framework.md) |
| SPS-Transport | OPC UA empfohlen, S7/snap7 als Alternative | [ADR 0002](docs/architektur/adr/0002-plc-transport.md) |
| Victron | lokales MQTT, Modbus TCP als Rückfall, read-only | [ADR 0003](docs/architektur/adr/0003-victron-transport.md) |
| Datenhaltung | SQLite (getrennt für Betrieb und Historie), Konfiguration als YAML | [ADR 0004](docs/architektur/adr/0004-datenhaltung.md) |
| Realtime | WebSocket mit Snapshot und Deltas | [ADR 0005](docs/architektur/adr/0005-realtime-transport.md) |
| Frontend | React · TypeScript · Vite · Motion · CSS-Tokens | [ADR 0006](docs/architektur/adr/0006-frontend-stack.md) |
| Prozessmodell | ein Prozess, modularer Monolith | [ADR 0007](docs/architektur/adr/0007-prozessmodell.md) |

---

## Dokumentation

| Dokument | Inhalt |
| --- | --- |
| [Architektur](docs/architektur/ARCHITECTURE.md) | Schichten, State, Commands, Adapter, Sicherheit |
| [Datenmodell](docs/architektur/datenmodell.md) | Namenskonvention, Zustände, Commands, Events, Alerts |
| [Architekturentscheidungen](docs/architektur/adr/) | ADRs mit Abwägung und Konsequenzen |
| [Offene Hardwareanforderungen](docs/OPEN_HARDWARE_REQUIREMENTS.md) | was für die reale Integration noch fehlt |
| [Widersprüche und offene Punkte](docs/analyse/widersprueche-und-offene-punkte.md) | Analyse der Spezifikation |
| [Entwicklung](docs/DEVELOPMENT.md) | Einrichten, starten, testen, Fehler simulieren |
| [Roadmap](docs/ROADMAP.md) | Meilensteine und Funktionsstatus |
| [Anforderungen](docs/anforderungen/) | Kapitel 1–18 im Wortlaut |
| [Changelog](CHANGELOG.md) | Versionshistorie |

Die Kapitel 1–18 sind die verbindliche Spezifikation. Jede
Implementierungsentscheidung lässt sich auf sie zurückführen; Abweichungen sind
in den ADRs mit Begründung dokumentiert.

---

## Simulation

Kehler OS läuft vollständig ohne das reale Fahrzeug. Der Simulationsadapter
erfüllt dieselbe Schnittstelle wie die realen Adapter und erzeugt auch
Fehlerbilder — offline, Timeout, ungültige Werte, blockierte Mechanik.

Läuft das System simuliert, ist das in der Oberfläche dauerhaft sichtbar. Die
Betriebsart wird beim Start festgelegt und ist zur Laufzeit nicht umschaltbar;
ein simuliertes Gerät kann keinen realen Aktor erreichen.

---

## Mitwirkende

Entwickelt für ein konkretes Fahrzeug, mit dem Anspruch, dass ein anderer
qualifizierter Entwickler das Projekt jederzeit übernehmen kann.
