# ADR 0003 – Anbindung des Victron-Systems

**Status:** angenommen (vorbehaltlich B1) · Phase 1
**Bezug:** Kapitel 3, Kapitel 12 §28–§33, Kapitel 18 §12

## Entscheidung

**Lokales MQTT des Cerbo GX als Primärweg, Modbus TCP als Rückfallebene.
Ausschließlich lesender Zugriff, solange kein Schreibbedarf bestätigt ist.**

## Kontext

Kapitel 12 §28 legt fest: Victron bleibt das Energiemanagementsystem und die
Schutzinstanz. Kehler OS liest, visualisiert, analysiert und automatisiert
darüber — es ersetzt nichts.

Der Cerbo GX bietet lokal zwei dokumentierte Schnittstellen.

## Abwägung

**MQTT — primär.**
Der Cerbo betreibt einen lokalen Broker, der Zustandsänderungen aktiv
publiziert. Das passt zur ereignisgetriebenen Architektur (Kapitel 2, Kapitel 5
§14) und erzeugt deutlich weniger Netzlast als zyklisches Abfragen — was
Kapitel 11 §18 ausdrücklich verlangt.

Eigenheit, die im Adapter behandelt werden muss: Der Broker stellt die
Publikation ein, wenn der Client keine regelmäßigen Keepalive-Nachrichten
sendet. Der Adapter muss den Keepalive also aktiv aufrechterhalten und dessen
Ausbleiben als Verbindungsproblem werten — nicht als „keine Änderungen“.

**Modbus TCP — Rückfallebene.**
Die Registerliste ist dokumentiert und stabil. Als Polling-Verfahren erzeugt
sie mehr Last, ist aber unabhängig von der MQTT-Konfiguration und deckt
einzelne Register ab, die über MQTT nicht sauber verfügbar sind.

**VRM-Cloud-API — verworfen.**
Widerspricht Kapitel 6 §31 (Local First) und Kapitel 11 §42: Das Fahrzeug darf
für seine Grundfunktionen nicht auf externe Server angewiesen sein.

## Read-only als Voreinstellung

Kapitel 12 §32 verlangt die klare Trennung von READ und WRITE, §33 hält fest,
dass Batterie- und Wechselrichterschutz bei Victron und dem BMS bleiben.

Der Adapter wird deshalb **ohne Schreibpfad** ausgeliefert. Ein solcher wird
erst ergänzt, wenn B3 einen konkreten, sicher unterstützten Anwendungsfall
bestätigt. Das ist die konservativere Voreinstellung und kostet nichts:
Visualisierung, Warnungen, Historie und übergeordnete Automatisierungen
funktionieren vollständig lesend.

## Qualität und Ausfall

Jeder Victron-Datenpunkt trägt dieselbe Qualitätskennzeichnung wie alle anderen
(`VALID`/`STALE`/`UNKNOWN`/…). Bleibt der Broker still, werden die Werte
`STALE` und dann `UNKNOWN` — es wird **kein** letzter bekannter Ladezustand als
aktuell dargestellt. Der Ausfall des Victron-Adapters berührt Licht, Wasser,
Klima und Fahrzeugfunktionen nicht (Kapitel 10 §22).

## Konsequenzen

- Benötigt B1: IP des Cerbo, MQTT aktiviert?, Portal-ID, ggf. TLS/Zugangsdaten.
- Bis dahin liefert der Simulator plausible Energiedaten inklusive Fehlerfällen
  (Timeout, ungültige Werte).
- Alarme des Victron-Systems werden übernommen und in das Kehler-OS-Warnmodell
  überführt, nicht neu erfunden.
