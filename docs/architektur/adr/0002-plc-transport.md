# ADR 0002 – Transportweg zur Siemens S7-1511-1 PN

**Status:** angenommen · entschieden am 2026-08-09 durch den Projektverantwortlichen
**Bezug:** Kapitel 5 §6, Kapitel 12 §4, Kapitel 15 §47, Kapitel 18 §10
**Ersetzt:** die vorläufige Fassung, die OPC UA empfahl

## Entscheidung

**S7-Kommunikation (PUT/GET) über `python-snap7`.**

OPC UA wurde geprüft und verworfen, weil der integrierte OPC-UA-Server der
S7-1500 eine kostenpflichtige SIMATIC-Runtime-Lizenz benötigt. Der
Projektverantwortliche hat entschieden, diese Lizenz nicht zu beschaffen.

Das ist eine legitime wirtschaftliche Entscheidung. Sie ist fachlich tragfähig —
sie verlagert allerdings die Sicherheit vom Protokoll in die Netzarchitektur,
was unten Konsequenzen hat.

## Was das für die SPS-Projektierung bedeutet

Damit ein externer Rechner über PUT/GET lesen und schreiben kann, muss in
TIA Portal Folgendes eingestellt sein:

1. **CPU → Schutz & Security → Verbindungsmechanismen:**
   „Zugriff über PUT/GET-Kommunikation durch entfernten Partner erlauben“
   aktivieren.
2. **Für jeden Datenbaustein, auf den Kehler OS zugreift:**
   Eigenschaften → **„Optimierter Bausteinzugriff“ deaktivieren.**
   Nur dann sind die Daten absolut adressierbar (`DB10.DBX4.2`), was PUT/GET
   voraussetzt.
3. Die Verbindung läuft über ISO-on-TCP, Port 102. Typischerweise Rack 0,
   Slot 1 — ist bei der Inbetriebnahme zu bestätigen.

> **Hinweis für die spätere Wartung:** Wird ein Datenbaustein nachträglich
> wieder auf optimierten Zugriff gestellt, bricht die Verbindung zu genau
> diesen Datenpunkten ab. Das gehört in die Wartungsdokumentation.

## Sicherheitsfolge — und wie sie aufgefangen wird

S7-Kommunikation über PUT/GET kennt **keine Transportverschlüsselung und keine
Authentifizierung**. Wer im selben Netzsegment ist und die Adressen kennt, kann
mit der SPS sprechen.

Kapitel 15 §47 sieht genau diesen Fall vor und verlangt, die Sicherheit dann
über die Gesamtarchitektur herzustellen. Konkret heißt das für dieses Projekt:

- **Die SPS ist ausschließlich für den Raspberry Pi erreichbar.** Kein Client,
  kein Gäste-WLAN, kein sonstiges Netzgerät bekommt eine Route dorthin.
  → Kapitel 15 §114
- **Netzsegmentierung wird von „wäre schön“ zur tragenden Maßnahme.** Damit
  steigt die Wichtigkeit des offenen Punkts I3 (VLAN-Fähigkeit des Switches)
  erheblich. Kann der Switch keine VLANs, brauchen wir eine andere
  Trennung — etwa eine zweite Netzwerkschnittstelle am Pi, an der die SPS
  allein hängt.
- **Kein Remote-Zugriff erreicht die SPS jemals direkt.** Fernzugriff endet
  immer am Kehler-OS-Backend, das Authentifizierung, Autorisierung und
  Validierung durchsetzt. → Kapitel 15 §36/§37
- Das Backend bleibt der einzige kontrollierte Weg zur Hardware.
  → Kapitel 15 §115

## Umsetzung

```
PlcAdapter (Interface)
├── S7PlcTransport         python-snap7   ← gewählt
└── SimulatedPlcTransport  interne Zustandsmaschine
```

Die Transportabstraktion bleibt trotz der getroffenen Entscheidung bestehen.
Sie kostet praktisch nichts und hält den Weg offen, falls später doch OPC UA
oder ein anderes Verfahren gewünscht wird. Über dem Transport liegt die
Mapping-Schicht; oberhalb der Adapterschicht sieht kein Code eine Adresse.

**Betriebliche Feinheiten von snap7**, die der Adapter behandeln muss:

- Die Bibliothek ist blockierend. Alle Aufrufe laufen deshalb in einem
  Executor, damit die Event-Loop nicht einfriert (Kapitel 17 §11).
- Es gibt keine Ereignisbenachrichtigung — gelesen wird zyklisch. Die
  Abfragerate wird je Datenpunkt konfiguriert, damit die SPS nicht unnötig
  belastet wird (Kapitel 5 §18, Kapitel 12 §74).
- Zusammenhängende Datenpunkte werden möglichst in einem Lesezugriff
  gebündelt, statt jeden einzeln abzufragen.
- Ein Verbindungsabbruch wird erkannt und mit exponentiellem Backoff neu
  aufgebaut; die betroffenen Datenpunkte gehen dabei auf `UNKNOWN`, nicht auf
  einen Standardwert.

## Konsequenzen

- **Offen und blockierend bleiben** A2 (IP, Rack, Slot) und A3 (Mapping).
- **Punkt I3 ist aufgewertet:** Die Netztrennung ist jetzt sicherheitstragend
  und keine Kür mehr.
- Die TIA-Portal-Einstellungen aus dem Abschnitt oben gehören in
  `docs/HARDWARE_INTEGRATION.md` und in die Wartungsdokumentation.
- Bis A2/A3 vorliegen, läuft ausschließlich `SimulatedPlcTransport`.
