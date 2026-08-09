# Changelog

Format angelehnt an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [Semantic Versioning](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Hinzugefügt

- **Phase 1 – Analyse und Architektur** abgeschlossen:
  - Systemarchitektur mit Schichtung Frontend → API → Kern → Adapter → Hardware
  - Daten-, Command- und Eventmodell einschließlich Namenskonvention
  - sieben Architekturentscheidungen (ADR 0001–0007) mit Abwägung und
    Konsequenzen: Backend-Stack, SPS-Transport, Victron-Anbindung,
    Datenhaltung, Realtime, Frontend-Stack, Prozessmodell
  - Analyse der Spezifikation mit neun identifizierten Widersprüchen bzw.
    offenen Entscheidungen
  - strukturierte Sammlung der offenen Hardwareanforderungen
  - Roadmap mit zwölf Meilensteinen und Funktionsstatus
- Anforderungskapitel 1–18 im Wortlaut archiviert
- Beschreibung der verbindlichen Dashboard-Designreferenz

### Hinzugefügt — M1/M2: Backend-Kern und Simulation

- **Domänenmodell:** Zustandswerte mit Qualität, Quelle und getrennten
  Zeitstempeln; Entities mit Capabilities; Befehle mit vollständigem
  Lebenszyklus; Ereignisse und Warnungen.
- **State Store** als einzige Wahrheit. Startet vollständig `UNKNOWN` und wird
  nie aus einer Datenbank wiederhergestellt. Werte altern selbsttätig zu
  `STALE` und `UNKNOWN`, wenn Aktualisierungen ausbleiben.
- **Command Bus** mit serverseitiger Prüfung vor jedem Hardwarekontakt,
  Serialisierung je Entity, entitätsspezifischen Timeouts und Bestätigung
  durch die Hardware. Ein Befehl gilt nie als erfolgreich, solange die
  Hardware nichts gemeldet hat.
- **Adapterschicht** mit einheitlicher Schnittstelle; Simulationsadapter als
  gleichrangige Implementierung, inklusive gezielt auslösbarer Fehlerbilder
  (Sensordefekt, ungültiger Wert, verstummter Sensor, blockierte Mechanik).
- **Supervisor** mit Fehlergrenzen je Dienst, Backoff und
  Crash-Loop-Erkennung.
- **REST- und WebSocket-Schnittstelle** unter `/api/v1`: Snapshot beim
  Verbinden, danach Deltas mit Sequenznummern. Statuscodes bilden das
  tatsächliche Befehlsergebnis ab.
- **Konfiguration** als validiertes YAML; Capabilities werden aus dem
  Entity-Typ abgeleitet. Demokonfiguration für die Simulation, ausdrücklich
  ohne erfundene Tankkapazitäten oder Hardwareadressen.
- 69 Tests mit Schwerpunkt auf Fehlerzuständen; Lint sauber.

### Hinzugefügt — M3/M4: Designsystem und Dashboard

- **Design-Tokens** als einzige Quelle für Farbe, Abstand, Radius, Typografie
  und Bewegung. Nachtmodus und reduzierte Bewegung tauschen ausschließlich
  Tokenwerte; keine Komponente kennt ein Thema.
- **Primitive** (Karte, Statuspunkt, Wert, Balken, Schalter, Schnellzugriff,
  Zeile, Button, „Nicht konfiguriert"). Die Komponente `Value` ist der einzige
  Ort, an dem ein Messwert dargestellt wird — dadurch kann keine Seite einen
  unbekannten Zustand versehentlich als Zahl ausgeben.
- **Fahrzeugvisualisierung** als Inline-SVG mit dokumentiertem Koordinatenplan.
  Sie ist reine Ausgabe. Bewegungen entstehen aus echten Zuständen; ein
  unbekannter Zustand wird gestrichelt gezeigt statt in einer erfundenen
  Position, und nicht konfigurierte Hardware wird gar nicht gezeichnet.
- **Realtime-Client** mit Snapshot beim Verbinden, Deltas mit Sequenzprüfung,
  exponentiellem Backoff und vollständigem Neuabgleich nach Verbindungsverlust.
- **Dashboard** mit Kopfbereich, Navigation, Fahrzeugstatus, Warnungen,
  Schnellzugriffen und Karten für Energie, Wasser und Klima.
- **Warnungsableitung im Backend** (`core/alerts.py`) — die Bewertung, ob etwas
  eine Warnung ist, ist Geschäftslogik und gehört nicht in die Oberfläche.
  Bewusst **ohne Schwellenwertwarnungen**, solange die Schwellen nicht
  konfiguriert sind (offener Punkt C3).
- **Verhalten ohne Verbindung** durchgängig geprüft: Banner, alle Werte als
  veraltet gekennzeichnet, Zustände als unbekannt geführt, Bedienelemente
  gesperrt und keine Entwarnung im Warnungsbereich.

### Geändert

- **ADR 0006 korrigiert:** Zustand und TanStack Query entfallen. Der
  Fahrzeugzustand kommt über einen einzigen WebSocket; es gibt keine Abfragen
  zu cachen. Stattdessen Reacts eingebautes `useSyncExternalStore`.
- **Simulation** kennt jetzt Wertebereiche je Einheit und einen eigenen Typ für
  binäre Kontakte, damit keine unplausiblen Werte entstehen.

### Entschieden (2026-08-09)

- **SPS-Transport:** S7-Kommunikation über snap7 statt OPC UA — keine Lizenz.
  Folge: Netztrennung wird sicherheitstragend (ADR 0002, Punkt I3 aufgewertet).
- **Speichermedium:** SSD bestätigt (Punkt I1).
- **Victron:** schreibend nur für Eingangsstrombegrenzung und Wechselrichter
  ein/aus, als Whitelist mit Bestätigungspflicht (ADR 0003, Punkt B3).
- **Szenen entfallen vollständig** (W10). Automatisierungsregeln,
  Schnellzugriffe und Fahrzeugmodi bleiben.
- **Navigation entfällt vollständig** (W1).
- **Umfang Version 1.0 bestätigt.** Nivellierung, Kameras und KI danach (W9).
- **Manueller Eingriff gewinnt** gegenüber Komfortautomatisierungen: sichtbare,
  zeitlich begrenzte Übersteuerung; Sicherheitsregeln übersteuern sie (W5).
- **Abfahrtscheck entfällt** (W11). Die Einzelzustände bleiben sichtbar.

### Offen

- Bilddatei der Designreferenz fehlt im Repository (nur Beschreibung vorhanden)
- keine realen Hardwareparameter vorhanden — Entwicklung läuft simuliert
- Übersteuerungsdauer und Bindung an den Moduswechsel im Detail (vor M6)
