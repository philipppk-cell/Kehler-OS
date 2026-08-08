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

### Offen

- Bilddatei der Designreferenz fehlt im Repository (nur Beschreibung vorhanden)
- SPS-Transportweg nicht entschieden (OPC-UA-Lizenz erforderlich?)
- keine realen Hardwareparameter vorhanden — Entwicklung läuft simuliert
