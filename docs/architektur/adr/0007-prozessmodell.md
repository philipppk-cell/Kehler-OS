# ADR 0007 – Prozessmodell und Fehlerisolierung

**Status:** angenommen · Phase 1
**Bezug:** Kapitel 17 §13–§17/§35–§37, Kapitel 18 §4/§5

## Entscheidung

**Ein Backend-Prozess als modularer Monolith auf asyncio. Fehlerisolierung über
überwachte Tasks mit Fehlergrenzen, nicht über Prozessgrenzen. systemd
übernimmt Autostart und Neustartbegrenzung.**

## Kontext

Kapitel 18 §5 überlässt die Entscheidung ausdrücklich der Architektur, verlangt
aber eine Begründung. Kapitel 17 §14 warnt vor unnötig vielen Diensten,
Kapitel 17 §15 stellt fest, dass keine Microservice-Architektur vorgeschrieben
ist. Kapitel 18 §4 nennt Microservice-Landschaften ausdrücklich als zu
vermeidende Überkomplexität.

## Abwägung

**Ein Prozess — gewählt.**

Der ausschlaggebende Punkt ist Kapitel 13 §2: Für jeden Zustand darf es genau
eine Wahrheit geben. State Store, Command Bus und Event Bus im selben
Speicherraum zu halten, macht konkurrierende Wahrheiten **strukturell
unmöglich**. Sobald diese drei über Prozessgrenzen verteilt wären, bräuchte es
Synchronisation, Serialisierung und Konfliktauflösung — also genau die
Komplexität, die das Problem erst schafft.

Dazu kommt: Die Last ist I/O-gebunden. Ein zweiter Prozess würde nichts
parallelisieren, was asyncio nicht ohnehin nebenläufig abarbeitet. Er würde
Speicher, Startzeit, IPC-Fehlerwege und Diagnoseaufwand kosten.

**Mehrere Prozesse — verworfen** für den Kern. Der übliche Vorteil,
Fehlerisolierung, wird hier anders erreicht (siehe unten). Der übliche zweite
Vorteil, unabhängige Skalierung, existiert bei einem Fahrzeug mit einer Handvoll
Clients nicht.

## Fehlerisolierung ohne Prozessgrenzen

Kapitel 17 §16/§17 verlangt, dass ein Fehler in einer Komponente nicht das
Gesamtsystem mitreißt — ein abstürzender Kameradienst darf die Lichtsteuerung
nicht berühren.

Umsetzung über einen **Task-Supervisor**: Jeder Adapter und jeder
Hintergrunddienst läuft als eigener asyncio-Task. Der Supervisor

- fängt jede Ausnahme an der Taskgrenze ab, statt sie nach oben durchschlagen
  zu lassen
- protokolliert sie strukturiert mit Correlation-ID
- startet den Task mit exponentiellem Backoff neu
- erkennt Dauerfehler (zu viele Neustarts in einem Zeitfenster) und setzt den
  Dienst dauerhaft auf `ERROR`, statt endlos neu zu starten (Kapitel 17 §36/§37)
- meldet den Dienststatus an die Diagnoseebene

Die betroffenen Datenpunkte gehen dabei auf `UNKNOWN` — nicht auf einen
Standardwert. Alles Übrige läuft weiter. Das ist die Graceful Degradation aus
Kapitel 17 §18.

Ein Absturz des gesamten Prozesses bleibt möglich; dagegen wirkt systemd mit
`Restart=on-failure` und `StartLimitBurst`. Nach einem Neustart wird der
Hardwarezustand vollständig neu eingelesen, nie aus der Datenbank übernommen
(Kapitel 12 §66).

## Ausnahme: nebenläufige Rechenarbeit

Aufgaben, die die Event-Loop blockieren würden — Aggregation der Historie,
Backup, Migrationen — laufen in einem Executor, damit die Bedienung nicht
einfriert (Kapitel 17 §11).

## Betrieb

```
systemd
├── kehleros-backend.service      uvicorn, Restart=on-failure
└── kehleros-kiosk.service        Vollbildanzeige auf dem Hauptdisplay
```

Autostart ohne manuelle Terminalbefehle (Kapitel 17 §34), kein sichtbarer
Desktop im Normalbetrieb (Kapitel 17 §32), eigener Bootscreen bis das Backend
bereit meldet (Kapitel 17 §31).

## Konsequenzen

- Ein Speicherleck in irgendeinem Modul betrifft den gesamten Prozess. Der
  Speicherverbrauch wird deshalb dauerhaft überwacht und ist Teil des
  Dauerlauftests (Kapitel 17 §96, §108).
- Wenn ein Bereich später doch eigene Isolierung braucht — etwa
  Kamerastream-Verarbeitung mit hoher Last — lässt er sich einzeln
  herauslösen, weil die Modulgrenzen bereits sauber gezogen sind. Die
  Entscheidung ist also umkehrbar, ohne den Kern anzufassen.
