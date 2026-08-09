# ADR 0003 – Anbindung des Victron-Systems

**Status:** angenommen · Schreibumfang entschieden am 2026-08-09
**Bezug:** Kapitel 3, Kapitel 12 §28–§33, Kapitel 18 §12
**Ersetzt:** die Fassung, die dauerhaft read-only vorsah

## Entscheidung

**Lokales MQTT des Cerbo GX als Primärweg, Modbus TCP als Rückfallebene.
Lesend vollständig — schreibend ausschließlich für genau zwei Funktionen:**

1. **Eingangsstrombegrenzung** (Landstrom-Strombegrenzung des MultiPlus)
2. **Wechselrichter ein- und ausschalten**

Alles andere bleibt read-only. Es gibt keinen allgemeinen Schreibpfad.

## Kontext

Kapitel 12 §32 verlangt die klare Trennung von READ und WRITE, §33 hält fest,
dass Batterie- und Wechselrichterschutz bei Victron und dem BMS bleiben.

Die ursprüngliche Fassung dieses ADR sah dauerhaft read-only vor, weil kein
Schreibbedarf bestätigt war. Der Projektverantwortliche hat nun genau zwei
Anwendungsfälle benannt. Beide sind **Betriebsparameter, keine
Schutzfunktionen** — das Grundprinzip aus §33 bleibt damit unangetastet.

Die Eingangsstrombegrenzung ist der praktisch wichtigste: An einem schwach
abgesicherten Campingplatzanschluss muss man den Ladestrom drosseln können,
ohne das Victron-Panel zu suchen.

## Transport

**MQTT — primär.** Der Cerbo betreibt einen lokalen Broker, der
Zustandsänderungen aktiv publiziert. Das passt zur ereignisgetriebenen
Architektur und erzeugt weit weniger Netzlast als zyklisches Abfragen
(Kapitel 11 §18). Schreiben erfolgt über die dafür vorgesehenen Write-Topics.

Eigenheit, die der Adapter behandeln muss: Der Broker stellt die Publikation
ein, wenn der Client keinen regelmäßigen Keepalive sendet. Das Ausbleiben von
Nachrichten muss deshalb als Verbindungsproblem gewertet werden — **nicht** als
„keine Änderungen“.

**Modbus TCP — Rückfallebene.** Dokumentierte Registerliste, polling-basiert.
Deckt einzelne Werte ab, die über MQTT nicht sauber verfügbar sind.

**VRM-Cloud-API — verworfen.** Widerspricht Local First (Kapitel 6 §31) und
Kapitel 11 §42.

> Die genauen Pfade bzw. Register für die beiden Schreibfunktionen werden in
> Phase 10 **gegen das reale Gerät verifiziert**, bevor irgendetwas geschrieben
> wird. Sie werden nicht aus der Dokumentation abgeschrieben und angenommen.

## Absicherung der beiden Schreibfunktionen

Weil dies die einzigen Stellen sind, an denen Kehler OS in das Energiesystem
eingreift, werden sie eng geführt:

**Whitelist statt Schalter.** Der Adapter kennt genau zwei schreibbare
Datenpunkte. Es gibt keine generische Schreibfunktion, über die versehentlich
oder absichtlich etwas anderes gesetzt werden könnte. Ein Schreibversuch auf
einen nicht gelisteten Pfad wird im Adapter abgewiesen.

**Wertebereich wird geprüft.** Die Eingangsstrombegrenzung wird gegen einen
konfigurierten Minimal- und Maximalwert validiert, bevor sie gesendet wird
(Kapitel 15 §44). Der Maximalwert stammt aus der realen Absicherung des
Landstromanschlusses — offener Punkt B2.

**Wechselrichter aus ist bestätigungspflichtig.** Das Abschalten kappt die
230-V-Versorgung im Fahrzeug. Diese Aktion wird als sicherheitsrelevant
eingestuft (Kapitel 15 §21), erfordert eine bewusste Bestätigung
(Kapitel 15 §22/§23) und ist administratorpflichtig.

**Victron behält das letzte Wort.** Lehnt das System einen Wert ab oder
korrigiert ihn, gilt der von Victron zurückgemeldete Zustand — nicht der
gesendete Wunsch. Auch hier ist die Hardware die Quelle der Wahrheit.

**Vollständige Protokollierung.** Beide Funktionen erzeugen einen Audit-Eintrag
mit Benutzer, Gerät, altem und neuem Wert (Kapitel 15 §52).

## Qualität und Ausfall

Jeder Victron-Datenpunkt trägt dieselbe Qualitätskennzeichnung wie alle anderen.
Bleibt der Broker still, werden die Werte `STALE` und dann `UNKNOWN` — es wird
**kein** letzter bekannter Ladezustand als aktuell dargestellt. Ein Ausfall des
Victron-Adapters berührt Licht, Wasser, Klima und Fahrzeugfunktionen nicht
(Kapitel 10 §22).

Alarme des Victron-Systems werden übernommen und in das Kehler-OS-Warnmodell
überführt, nicht neu erfunden.

## Konsequenzen

- Benötigt B1: IP des Cerbo, MQTT aktiviert?, Portal-ID, ggf. TLS/Zugangsdaten.
- Benötigt B2 zusätzlich für den Maximalwert der Eingangsstrombegrenzung.
- Reihenfolge in Phase 10: **erst alles lesend in Betrieb nehmen und
  beobachten**, danach die Strombegrenzung, zuletzt der Wechselrichterschalter.
- Bis dahin liefert der Simulator Energiedaten inklusive Fehlerfällen
  (Timeout, ungültige Werte) und bildet beide Schreibfunktionen nach.
