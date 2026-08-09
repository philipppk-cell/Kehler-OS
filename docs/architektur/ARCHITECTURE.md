# Kehler OS – Systemarchitektur

Stand: Phase 1 (Analyse und Architektur)
Grundlage: Anforderungskapitel 1–18 (`docs/anforderungen/`)

---

## 1. Leitgedanke

Kehler OS ist die einzige Oberfläche des Fahrzeugs. Dahinter liegt eine
Schichtung, die drei Dinge strikt auseinanderhält:

**Was der Benutzer will** (Command) · **was tatsächlich ist** (State) ·
**wie die Hardware es technisch realisiert** (Adapter).

Diese Trennung ist nicht Stilfrage, sondern die Voraussetzung für die
wichtigste Zusicherung des Projekts: Die Oberfläche behauptet nie einen
Zustand, den die Hardware nicht bestätigt hat.

## 2. Schichten

```
┌───────────────────────────────────────────────────────────┐
│  FRONTEND                                                  │
│  Darstellung · Eingaben · keine Geschäftslogik            │
└───────────────────┬───────────────────────────────────────┘
                    │ HTTP (REST, /api/v1) + WebSocket
┌───────────────────▼───────────────────────────────────────┐
│  API-SCHICHT                                               │
│  Auth · Autorisierung · Validierung · Snapshot + Deltas    │
└───────────────────┬───────────────────────────────────────┘
┌───────────────────▼───────────────────────────────────────┐
│  KERN                                                      │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐  │
│  │ State Store │ │ Command Bus  │ │ Event Bus          │  │
│  └─────────────┘ └──────────────┘ └────────────────────┘  │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐  │
│  │ Entity      │ │ Automation   │ │ Alerts             │  │
│  │ Registry    │ │ Engine       │ │                    │  │
│  └─────────────┘ └──────────────┘ └────────────────────┘  │
└───────────────────┬───────────────────────────────────────┘
┌───────────────────▼───────────────────────────────────────┐
│  DIENSTE                                                   │
│  History · Audit · Diagnose · Konfiguration · Backup       │
└───────────────────┬───────────────────────────────────────┘
┌───────────────────▼───────────────────────────────────────┐
│  ADAPTERSCHICHT   (einziger Ort mit Hardwarewissen)        │
│  PlcAdapter · VictronAdapter · CameraAdapter · Simulator   │
└───────────────────┬───────────────────────────────────────┘
                    │
        ┌───────────┴───────────┬──────────────┐
        ▼                       ▼              ▼
   Siemens S7-1511-1 PN    Cerbo GX        Kameras
```

**Verbindliche Regeln der Schichtung**

1. Das Frontend kennt ausschließlich semantische IDs (`vehicle.garage.door`),
   niemals Hardwareadressen. → Kapitel 5 §7, Kapitel 10 §7, Kapitel 18 §8
2. Kein Client schreibt jemals direkt zur SPS. → Kapitel 18 §52
3. Hardwarewissen existiert ausschließlich in der Adapterschicht und in der
   Mapping-Konfiguration. Kein Fachmodul, keine Automatisierung, keine
   UI-Komponente kennt eine Adresse. → Kapitel 12 §57/§58, Kapitel 14 §97
4. Jede schreibende API prüft serverseitig Authentifizierung, Autorisierung
   und Gültigkeit — unabhängig davon, was die UI anzeigt. → Kapitel 15 §42/§43

## 3. Prozessmodell

**Ein Backend-Prozess (modularer Monolith auf asyncio), ein Frontend-Bundle.**

Begründung siehe [ADR 0007](adr/0007-prozessmodell.md). Kurz: Kapitel 17 §14/§15
erlauben die Entscheidung ausdrücklich und warnen zugleich vor unnötiger
Fragmentierung. Auf einem Raspberry Pi kostet jeder zusätzliche Prozess
Speicher, Startzeit und Fehlerfläche, ohne dass es hier einen Gewinn gäbe: Die
Last ist vollständig I/O-gebunden.

Fehlerisolierung entsteht stattdessen durch **überwachte Tasks mit
Fehlergrenzen**: Jeder Adapter und jeder Hintergrunddienst läuft als eigener
asyncio-Task unter einem Supervisor, der Abstürze auffängt, protokolliert, mit
Backoff neu startet und den Dienststatus in die Diagnose meldet. Ein
abstürzender Kameraadapter kann die Lichtsteuerung nicht mitreißen.
→ Kapitel 17 §16/§17

Was bewusst **nicht** getrennt läuft: State Store, Command Bus und Event Bus.
Sie im selben Prozess und Speicher zu halten, ist die einfachste wirksame
Garantie gegen konkurrierende Wahrheiten. → Kapitel 13 §2

## 4. State Store — die eine Wahrheit

Der State Store hält den aktuellen logischen Fahrzeugzustand **im
Arbeitsspeicher**. Er ist nicht die Datenbank und wird nicht aus ihr
wiederhergestellt. → Kapitel 13 §24/§25

Jeder Zustandswert trägt:

| Feld | Zweck |
| --- | --- |
| `value` | der Wert selbst |
| `unit` | physikalische Einheit, intern immer SI-nah und anzeigeunabhängig |
| `quality` | `VALID` · `STALE` · `UNKNOWN` · `INVALID` · `ERROR` |
| `source` | `PLC` · `VICTRON` · `KEHLER_OS` · `USER` · `AUTOMATION` · `SIMULATION` |
| `measured_at` | Messzeit (wann die Hardware den Wert erfasst hat) |
| `received_at` | Systemzeit (wann Kehler OS ihn erhalten hat) |
| `seq` | monoton steigende Sequenznummer für die Reihenfolgesicherung |

Die drei Zeitbegriffe aus Kapitel 5 §26 sind damit getrennt; `occurred_at`
kommt bei Ereignissen hinzu.

**Startverhalten:** Beim Hochfahren steht jeder Zustand auf `INITIALIZING`,
danach auf `UNKNOWN`, bis ein Adapter einen bestätigten Wert liefert. Es wird
niemals ein gespeicherter Zustand als aktuell übernommen.
→ Kapitel 6 §44, Kapitel 12 §66, Kapitel 13 §25, Kapitel 15 §71

**Veralterung:** Jeder Datenpunkt hat ein erwartetes Aktualisierungsintervall.
Bleibt eine Aktualisierung aus, wechselt die Qualität automatisch auf `STALE`
und danach auf `UNKNOWN` — der letzte Wert wird nicht als aktuell weitergereicht.
→ Kapitel 13 §9

## 5. Command-Verarbeitung

```
UI/Automation/KI
  ↓  Command anlegen (eigene ID, Correlation-ID, Auslöser)
Authentifizierung  →  abgelehnt: REJECTED
  ↓
Autorisierung      →  abgelehnt: REJECTED
  ↓
Validierung        →  ungültiger Parameter / fehlende Capability: REJECTED
  ↓
Vorbedingungen     →  Gerät offline, Bewegung läuft, Sicherheitsbedingung: REJECTED
  ↓
Serialisierung je Entity (eine Bewegung zur Zeit)
  ↓
Adapter → Hardware                                   SENT
  ↓
Quittung des Adapters                                ACKNOWLEDGED
  ↓
bestätigte Zustandsänderung                          COMPLETED
     ohne Rückmeldung innerhalb des Timeouts     →   TIMEOUT
     Fehler des Adapters                          →  FAILED
```

**Der Command verändert niemals selbst den State.** Nur der Adapter, der einen
Wert von der Hardware liest, schreibt in den State Store. Das ist die
technische Umsetzung von „Hardware ist Quelle der Wahrheit“.
→ Kapitel 12 §67, Kapitel 13 §3, Kapitel 18 §35/§37

Der gewünschte Zustand wird separat als `requested_state` geführt und der UI
zusätzlich zum `actual_state` übermittelt. Damit kann die Oberfläche „Befehl
wird ausgeführt“ zeigen, ohne den Hardwarezustand zu behaupten.
→ Kapitel 13 §4

**Timeouts sind pro Entity konfiguriert.** Eine Lampe und ein hydraulischer
Zylinder haben verschiedene physikalische Reaktionszeiten; ein universeller
Timeout wäre entweder zu kurz oder wertlos. → Kapitel 13 §70

**Befehle sind idempotent formuliert.** `set_state(ON)` statt `toggle()`, weil
Toggle einen zuverlässig bekannten Ausgangszustand voraussetzt, den es bei
`UNKNOWN` gerade nicht gibt. → Kapitel 13 §33/§34, Kapitel 17 §27

**Retries bei Aktoren erfolgen nicht automatisch.** Ein Bewegungsbefehl, dessen
Ausgang unklar ist, wird nicht blind wiederholt; stattdessen meldet das System
den unklaren Zustand. → Kapitel 14 §17, Kapitel 17 §26

## 6. Capability-Modell

Ein Gerät beschreibt, was es kann. Die Oberfläche richtet sich danach und bietet
nichts an, was die Hardware nicht hergibt.

```
Entity
├── id            vehicle.garage.door
├── domain        vehicle
├── capabilities  [open, close, stop]        ← keine "position": kein Regler
├── state         actual / requested / quality
└── device        Verweis auf das physische Gerät
```

Fehlt eine Capability, existiert das Bedienelement nicht — kein ausgegrauter
Regler, kein toter Knopf. Ist ein Gerät gar nicht konfiguriert, zeigt die UI
„Nicht konfiguriert“ statt eines Platzhalters.
→ Kapitel 10 §40/§41, Kapitel 12 §55, Kapitel 13 §60, Kapitel 18 §101

## 7. Adapterschicht

Jeder Adapter erfüllt dieselbe schmale Schnittstelle: verbinden, lesen,
schreiben, Verbindungszustand melden, sauber beenden. Er übersetzt zwischen
Hardwaredetail und semantischem Datenpunkt — und **nur** das.

| Adapter | Zielsystem | Zustand |
| --- | --- | --- |
| `SimulationAdapter` | keiner (interne Zustandsmaschine) | zuerst umgesetzt |
| `PlcAdapter` | Siemens S7-1511-1 PN | Interface definiert, Transport offen (A1) |
| `VictronAdapter` | Cerbo GX | Interface definiert, read-only vorgesehen |
| `CameraAdapter` | künftige Kameras | Interface vorgesehen |

Der Simulator ist **kein Sonderweg**, sondern eine gleichrangige Implementierung
derselben Schnittstelle. Dadurch testet die Simulation exakt die Pfade, die
später real laufen. → Kapitel 12 §59, Kapitel 18 §63

**Trennung Simulation ↔ Realität:** Der aktive Adaptersatz wird beim Start
anhand der Umgebung festgelegt und ist zur Laufzeit nicht umschaltbar. Läuft
irgendein Adapter simuliert, kennzeichnet die Oberfläche das dauerhaft
sichtbar. Ein simuliertes Gerät kann keinen realen Aktor erreichen, weil kein
Codepfad zwischen beiden existiert.
→ Kapitel 12 §60, Kapitel 15 §95/§96, Kapitel 18 §66/§67

## 8. Datenhaltung

Drei getrennte Verantwortlichkeiten, bewusst unterschiedlich gelöst
([ADR 0004](adr/0004-datenhaltung.md)):

| Was | Wo | Warum |
| --- | --- | --- |
| Live-Zustand | Arbeitsspeicher | ist nie persistente Wahrheit |
| Konfiguration und Hardware-Mapping | YAML unter `config/`, versioniert | menschenlesbar, diffbar, auch ohne laufendes System editierbar |
| Betriebsdaten (Benutzer, Automatisierungen, Ereignisse, Audit) | SQLite `kehleros.db` | transaktional, einfach zu sichern |
| Historie und Zeitreihen | separate SQLite `history.db` | Ausfall darf die Steuerung nicht berühren |

Die Trennung der beiden Datenbankdateien ist Absicht: Fällt die Historie aus,
läuft die Fahrzeugsteuerung weiter, und die Oberfläche sagt genau das.
→ Kapitel 16 §88/§89/§90

Zeitreihen werden gestaffelt verdichtet (roh → Minute → Stunde) und nach
konfigurierbaren Regeln gelöscht. Der Speicherverbrauch wird überwacht, bevor
er kritisch wird — nicht erst, wenn nichts mehr geschrieben werden kann.
→ Kapitel 16 §9/§77/§79/§80

## 9. Realtime

WebSocket unter `/api/v1/realtime`:

1. Client verbindet und authentifiziert sich
2. Server sendet einen vollständigen, in sich konsistenten **Snapshot** mit
   Versionsnummer
3. danach ausschließlich **Deltas**, jeweils mit Sequenznummer
4. Der Client verwirft Deltas mit veralteter Sequenz — damit kann ein
   verzögertes `OPENING` kein bereits bestätigtes `OPEN` überschreiben
5. Nach einem Verbindungsabbruch fordert der Client einen neuen Snapshot an und
   arbeitet **nicht** mit seinem alten Stand weiter

→ Kapitel 13 §29/§30/§32, Kapitel 17 §104/§105

## 10. Sicherheitsgrenzen

Die Sicherheitsarchitektur liegt auf mehreren Ebenen, keine trägt sie allein
(Kapitel 15 §2):

- **Netzwerkzugehörigkeit ist keine Berechtigung.** Ein Gerät im WLAN ist kein
  Administrator. → Kapitel 15 §39
- **Serverseitige Prüfung jeder schreibenden Operation.** Ein ausgeblendeter
  Knopf ist keine Zugriffskontrolle. → Kapitel 15 §42
- **Die Oberfläche ist keine Sicherheitseinrichtung.** Wo eine Bewegung unter
  Bedingungen unzulässig ist, muss die Steuerung sie selbst verhindern; Kehler OS
  blendet den Befehl zusätzlich aus, verlässt sich aber nie darauf.
  → Kapitel 12 §7, Kapitel 15 §24
- **Kein Force-Befehl**, der eine Hardwarebedingung umgeht. → Kapitel 15 §26
- **Kein Softwareknopf wird als Not-Halt dargestellt.** → Kapitel 14 §73
- **KI erhält keinen direkten Hardwarezugriff**, sondern nutzt dieselbe
  geprüfte Command-Kette wie jeder Benutzer. Externe Inhalte sind Daten, nie
  Befehle. → Kapitel 15 §90/§92
- **Secrets liegen außerhalb des Quellcodes** und erscheinen weder in Logs noch
  in Diagnoseexporten. → Kapitel 15 §49/§51/§59

## 11. Beobachtbarkeit

Strukturierte Logs, Metriken und Ereignisse ergänzen sich (Kapitel 16 §103).
Eine **Correlation-ID** verbindet alle Stationen eines Vorgangs — API-Request,
Validierung, Adapterbefehl, Hardwarequittung, Zustandsänderung, UI-Update.
Damit ist die Frage „warum ging die Garage nicht auf?“ in einer Abfrage
beantwortbar statt in fünf Logdateien. → Kapitel 16 §28/§107

Die normale Oberfläche bleibt davon unberührt: Der Benutzer sieht einen
verständlichen Satz, der Administrator die technische Kette.

## 12. Umgebungen

| Umgebung | Adapter | Kennzeichnung in der UI |
| --- | --- | --- |
| `development` | Simulation | „SIMULATION“ dauerhaft sichtbar |
| `simulation` | Simulation | „SIMULATION“ dauerhaft sichtbar |
| `production` | reale Adapter | keine Kennzeichnung; Debugfunktionen deaktiviert |

Der Wechsel erfolgt ausschließlich über die Umgebungskonfiguration beim Start,
nie zur Laufzeit und nie unbemerkt. → Kapitel 15 §94/§96, Kapitel 18 §68

## 13. Projektstruktur

```
kehler-os/
├── backend/
│   └── kehleros/
│       ├── core/          State Store · Command Bus · Event Bus · Registry
│       ├── domain/        Datenmodelle, Zustandsmaschinen, Einheiten
│       ├── adapters/      base · simulation · plc · victron · camera
│       ├── modules/       Licht · Energie · Wasser · Klima · Fahrzeug · …
│       ├── services/      History · Audit · Diagnose · Konfiguration · Backup
│       ├── automation/    Engine · Trigger · Bedingungen · Aktionen
│       ├── api/           REST-Routen · WebSocket · Auth · Schemas
│       └── platform/      Logging · Supervisor · Zeit · Health
├── frontend/
│   └── src/
│       ├── design/        Tokens · Primitive · Icons · Motion
│       ├── shell/         Layout · Navigation · Boot · Statusleiste
│       ├── pages/         eine Seite je Fachmodul
│       ├── vehicle/       austauschbare Fahrzeugvisualisierung
│       ├── realtime/      WebSocket-Client · Snapshot · Reconnect
│       └── api/           typisierter API-Client
├── config/
│   ├── environments/      development · simulation · production
│   ├── hardware/          Geräte, Mapping, Kalibrierung (leer bis geklärt)
│   └── vehicle/           Räume, Tanks, Lichtkreise, Zonen
├── tests/
├── deployment/            systemd · Kiosk · Installation · Backup
├── tools/
└── docs/
    ├── anforderungen/     Kapitel 1–18 im Wortlaut
    ├── architektur/       dieses Dokument · ADRs · Datenmodell
    └── analyse/           Widersprüche und offene Punkte
```

Die Fahrzeugvisualisierung liegt bewusst in einem eigenen Verzeichnis mit
schmaler Schnittstelle (Zustände hinein, Darstellung heraus), damit die
Grafik später ersetzt werden kann, ohne das Dashboard anzufassen.
→ Kapitel 18 §104

## 14. Was diese Architektur bewusst nicht tut

- keine Microservices, kein Container-Orchestrator, keine Cloud-Abhängigkeit
  → Kapitel 18 §4
- kein Mandantensystem, keine Flottenverwaltung → Kapitel 18 §125
- keine eigene Kryptografie, kein eigenes Protokoll → Kapitel 18 §88
- keine KI im kritischen Pfad; das System funktioniert vollständig ohne sie
  → Kapitel 14 §101, Kapitel 18 §113
