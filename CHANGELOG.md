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

### Offen

- Bilddatei der Designreferenz fehlt im Repository (nur Beschreibung vorhanden)
- SPS-Transportweg nicht entschieden (OPC-UA-Lizenz erforderlich?)
- keine realen Hardwareparameter vorhanden — Entwicklung läuft simuliert
