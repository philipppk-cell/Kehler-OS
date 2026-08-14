# Kehler OS — Übergabe an eine andere KI

Diese Datei ist zum Hochladen gedacht. Sie enthält alles, was nötig ist, um an
diesem Projekt weiterzuarbeiten, ohne die bisherige Unterhaltung zu kennen.

**Stand:** 2026-08-14 · Branch `claude/wohnmobil-betriebssystem-mqg8x3`
**Repository:** `philipppk-cell/Kehler-OS`

---

## 1. Was das ist

Ein Betriebssystem für ein Expeditions-/Luxus-LKW-Wohnmobil auf **MAN TGX 6×2**
mit Kofferaufbau. Es läuft auf einem **Raspberry Pi 5**, liest und steuert über
eine **Siemens S7-1511-1 PN**, liest die **Victron**-Energieanlage, und wird
über ein **iPad Pro 13"** im Browser bedient.

Der Fahrzeughalter heißt Philipp Kehler. Er ist Auftraggeber und einzige Quelle
für alle Angaben über das Fahrzeug.

## 2. Der Qualitätsmaßstab — das Wichtigste

> **Bauen, als ginge es in Serie. Wenn es zwei Lösungen gibt, immer die
> technisch bessere — nie die schnellere oder billigere.**

Daraus folgen Regeln, die im ganzen Projekt durchgehalten werden und die man
nicht aufweichen sollte:

**Nichts erfinden.** Keine IP-Adressen, SPS-Datenbausteine, Sensormodelle,
Passwörter, Tankgrößen, Registeradressen. Was nicht bekannt ist, bleibt leer und
wird als offener Punkt festgehalten. Lieber eine Lücke als eine plausible
Falschangabe.

**Kein Bedienelement ohne Befehl.** Die Oberfläche leitet sich aus den
Capabilities der Entity ab. Gibt es keinen `close`-Befehl, gibt es keine
Schaltfläche „Schließen" — auch keine ausgegraute. Eine ausgegraute Schaltfläche
behauptet, das ginge grundsätzlich schon und sei nur gerade gesperrt.

**Nie einen Zustand behaupten, den man nicht kennt.** `UNKNOWN` heißt niemals
`0`, `OFF` oder `CLOSED`. Wo keine Rückmeldung kommt, wird der letzte **Befehl**
angezeigt und auch so benannt („Öffnen befohlen"), nie eine Stellung.

**Drei verschiedene Arten von Abwesenheit** werden auseinandergehalten:
- `configured: false` → „Nicht konfiguriert" (Funktion da, Zuordnung fehlt)
- `unverified: true` → „Noch zu verifizieren" (unklar, ob über die
  Schnittstelle überhaupt erreichbar)
- Entity fehlt ganz → erscheint nirgends

**Die Oberfläche ist keine Sicherheitseinrichtung.** Kein „Trotzdem"-Befehl
darf eine Hardware-Schutzbedingung übergehen. Keine Schaltfläche wird als
zertifizierter Not-Halt dargestellt.

**Keine Schutzfunktion der SCHEER-Heizung wird ersetzt, nachgebaut oder
umgangen.**

**Secrets niemals in Quelltext oder Logs.** Adressen und Zugangsdaten gehören
nach `config/hardware/` — das ist per `.gitignore` ungetrackt.

## 3. Technik

**Backend:** Python 3.11, asyncio, FastAPI, Pydantic v2, modularer Monolith.
**Frontend:** React 18 + TypeScript + Vite, CSS über Design-Tokens, three.js für
die 3D-Fahrzeugansicht (lazy geladen, Render nur auf Anforderung).
**Datenhaltung:** SQLite mit WAL, Rohtabelle plus Minuten-/Stunden-Verdichtung.

**Kernidee des Datenmodells:** Jeder Wert trägt Qualität, Quelle, Messzeit und
Empfangszeit.

```
VALID    aktueller, plausibler Wert
STALE    war gültig, ist alt — Wert bleibt erhalten und wird gekennzeichnet
UNKNOWN  Zustand nicht bekannt — KEIN Wert
INVALID  außerhalb des zulässigen Bereichs — KEIN Wert
ERROR    Sensor meldet Defekt — KEIN Wert
```

`STALE` behält seinen Wert, die anderen drei nicht. Das ist technisch
durchgesetzt (`StateValue.__post_init__`).

**Entity-Typen** (in `backend/kehleros/config/models.py`):

| Typ | Befehle |
| --- | --- |
| `measurement` | keine |
| `contact` | keine (binärer Sensor) |
| `status` | keine (mehrwertiger Zustand, z. B. Brennerphase) |
| `switch` | `set_state` |
| `movable` | `open`, `close`, `stop` |
| `valve` | `open`, `close` — kein Stopp |
| `lock` | `open`, `close` — wie valve, eigener Name |
| `release` | nur `open` |
| `setpoint` | `set_value` — nur mit bekanntem `max_value` |

**`feedback: false`** ist ein eigener Fall: Der Aktor lässt sich ansteuern, aber
nicht auslesen. Dann wartet der Command Bus **nicht** auf eine Bestätigung (die
nie käme), der Zustand bleibt dauerhaft `UNKNOWN`, und der Wunschzustand bleibt
stehen statt gelöscht zu werden.

## 4. Getroffene Architekturentscheidungen (ADRs in `docs/architektur/adr/`)

| Nr. | Entscheidung |
| --- | --- |
| 0001 | Python/FastAPI im Backend |
| 0002 | **ersetzt durch 0010** |
| 0003 | Victron nur lesen, zwei Ausnahmen |
| 0004 | SQLite mit Verdichtung |
| 0005 | WebSocket für Realtime |
| 0006 | React + TypeScript + Vite |
| 0007 | Prozessmodell |
| 0008 | Fahrzeug im Dashboard aus Code gebaut |
| 0009 | SCHEER-Heizung über die SPS, HeatMate bleibt Regler |
| 0010 | **OPC UA statt PUT/GET** zur SPS (`asyncua`) |

## 5. Bestätigte Fahrzeugangaben

**Tanks:** Frischwasser 550 l und 450 l, Grauwasser 280 l, Schwarzwasser 370 l.
Gleichmäßig geformt, lineare Umrechnung. Schwellen: Frischwasser Warnung unter
20 %, kritisch unter 10 %; Abwasser Warnung über 80 %, kritisch über 90 %.

**Energie:** Victron mit Cerbo GX, 24-V-Lithium, 900 Ah, Solar auf dem Dach,
Landstrom mit 16 A abgesichert. **Nur lesen**, mit genau zwei Ausnahmen:
Eingangsstrombegrenzung und Wechselrichter ein/aus.

**Heizung:** SCHEER selection 10/17 kW mit HeatMate V4.02. Zwei Heizkreise
(Heizkörper, Fußboden), **eine** Temperatur, Elektroheizung mit drei Stufen
(1/2/3 kW). Modbus-Anschluss vorhanden, **noch nicht verdrahtet**.
Registerliste liegt nicht vor → alle Heizungs-Entities `unverified: true`.

**Klima:** LG S3-M09JA3FA, eigenes WLAN-Modul. Anbindungsweg noch nicht
entschieden → `unverified: true`.

**Beleuchtung:** läuft über gewöhnliche Lichtschalter, **nicht** über die SPS.
Es gibt keine Licht-Entities und keinen Reiter.

**Kameras:** gibt es **nicht**. Reiter, Symbol und die Domäne `camera` wurden
entfernt.

**Ablassventile:** je eins für Grau- und Schwarzwasser, nur öffnen/schließen,
**keine Stellungsrückmeldung**.

**Heckklappe:** lässt sich **nur öffnen** (Gasdruckdämpfer, zudrücken von Hand).

**Schränke:** Zentralverriegelung, drei Gruppen (Schrankgruppe 1/2/3), nur
öffnen/schließen.

**Keine Rückmeldung von irgendeinem beweglichen Teil.** Messwerte kommen.

**Display:** iPad Pro 13", über Netzwerk, Touch, beide Ausrichtungen.

**Netzwerk:** LTE-Router mit Gigabit-Switch, ein flaches Segment.
SPS unter `192.168.1.10`, OPC-UA-Server läuft (Port 4840).

## 6. Ausdrücklich abbestellt

- **Keine Benutzer, keine Berechtigungen** (Beschluss W14)
- **Keine Szenen**
- **Kein Navigationsmodul**
- **Kein Abfahrtscheck, keine Gesamtbewertung „abfahrbereit"**
- **Keine Erinnerung an ein offenes Ablassventil**
- Nivellierung, KI-Assistent, Fernzugriff: erst nach Version 1.0

## 7. Offene Punkte (`docs/OPEN_HARDWARE_REQUIREMENTS.md`)

**Blockierend für die erste reale Inbetriebnahme:**
- **A2** — Zugang zum OPC-UA-Server: Sicherheitsrichtlinie, Anmeldeverfahren,
  Zertifikatsweg. Das Werkzeug `tools/opcua/erkunden.py` beantwortet das; es
  muss im Fahrzeugnetz laufen.
- **A3** — Bedeutung der Knoten. NodeIds und Datentypen sind auslesbar; was
  `TRUE` bedeutet („ist offen" oder „fahre auf"), muss der Fahrzeughalter sagen.
- **A5** — vorhandene Sicherheitsverriegelungen in der SPS

**Danach:**
- **B1** Cerbo-Schnittstelle (MQTT aktiviert? VRM-Portal-ID?)
- **C1** Tanksensorik
- **G1** Heizung: erst verdrahten, dann Registerliste. Offen ist auch, ob
  Modbus **RTU** (dann fehlt Hardware) oder **TCP**.
- **K1** fünf fehlende Fahrzeugmaße
- **I3** Netztrennung — seit OPC UA nicht mehr blockierend, aber empfohlen

## 8. Wo was liegt

```
backend/kehleros/
  config/       models.py (Entity-Typen), loader.py (Typ → Befehle)
  core/         state_store, command_bus, alerts, history, registry
  domain/       models.py (StateValue, Entity, Command), enums.py, ids.py
  adapters/     base.py, simulation.py
  api/          http.py, serialization.py, realtime
frontend/src/
  pages/        Dashboard, Wasser, Energie, Klima, Heizung, Fahrzeug,
                Schraenke, Diagnose, Einstellungen
  control/      actuator.tsx  ← „ohne Rückmeldung keine Stellung behaupten"
  vehicle3d/    buildVehicle, loadVehicle, VehicleScene, dimensions
  design/       primitives, icons, tokens.css
  i18n/de.ts    alle Texte
config/
  vehicle/vehicle.yaml       WELCHE Funktionen das Fahrzeug hat (versioniert)
  hardware/devices.yaml      Adressen und Zugangsdaten (UNGETRACKT)
tools/
  opcua/        erkunden.py — Adressraum der SPS auslesen
  model/        MODELL-AUFTRAG.md — Spezifikation für ein 3D-Modell
  demo/         weitergebbare Demo-HTML
docs/
  OPEN_HARDWARE_REQUIREMENTS.md   ← die offenen Fragen, gepflegt
  ROADMAP.md · CHANGELOG.md · architektur/adr/
```

## 9. Arbeitsweise, die sich bewährt hat

- Jede Änderung mit Tests, die den Fehler tatsächlich reproduzieren würden.
  Aktuell 205 Tests, `ruff` und `tsc` sauber.
- Oberflächenänderungen gegen einen **laufenden** Server prüfen, bei 390×844
  (Handy) und 1024×1366 (iPad), mit Blick auf waagerechtes Scrollen.
- Entscheidungen im Quelltext begründen, nicht nur beschreiben — vor allem,
  **warum die naheliegende Lösung verworfen wurde**.
- Wenn eine Angabe des Fahrzeughalters eine frühere Annahme widerlegt: die
  Annahme entfernen und den Vorgang festhalten, statt still zu überschreiben.

## 10. Der nächste Schritt

`tools/opcua/erkunden.py` im Fahrzeugnetz laufen lassen:

```bash
pip install asyncua
python erkunden.py opc.tcp://192.168.1.10:4840 --unsicher
```

Der erzeugte Bericht beantwortet A2 und den größten Teil von A3. Danach kann
der OPC-UA-Adapter gebaut werden — er ist das einzige größere Stück, das noch
zwischen der Simulation und dem realen Betrieb steht.
