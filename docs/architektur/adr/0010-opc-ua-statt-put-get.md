# ADR 0010 – OPC UA als Transportweg zur SPS

**Status:** angenommen · 2026-08-12
**Ersetzt:** [ADR 0002](0002-plc-transport.md) (S7-Kommunikation über PUT/GET)
**Bezug:** Kapitel 5 §6/§18, Kapitel 12 §4/§57/§74, Kapitel 15 §47/§114,
Kapitel 17 §11, Kapitel 18 §10
**Bezug intern:** Punkte A1–A3 und I3 in
[`OPEN_HARDWARE_REQUIREMENTS.md`](../../OPEN_HARDWARE_REQUIREMENTS.md)

## Entscheidung

**Kehler OS spricht OPC UA mit der S7-1511-1 PN.** Der Fahrzeughalter hat am
2026-08-12 mitgeteilt, dass auf der SPS ein **OPC-UA-Server eingerichtet ist**.

Damit entfällt die Grundlage von ADR 0002. Jene Entscheidung war keine fachliche
Vorliebe für PUT/GET, sondern die Folge einer wirtschaftlichen Vorgabe: Die
Lizenz für den OPC-UA-Server sollte nicht beschafft werden. Diese Vorgabe
besteht nicht mehr, und damit fällt die Entscheidung auf den Weg zurück, den
die ursprüngliche Fassung von ADR 0002 empfohlen hatte.

**Bibliothek: `asyncua`.**

## Warum das erheblich mehr ist als ein Protokollwechsel

PUT/GET liefert Bytes an einer Adresse. OPC UA liefert einen Wert **mit
Kontext**. Der Unterschied trifft dieses Projekt an einer empfindlichen
Stelle, weil das Datenmodell diesen Kontext seit dem ersten Tag vorsieht.

`StateValue` trägt Qualität, Quelle, Messzeit und Empfangszeit. Über PUT/GET
wären davon zwei Felder ehrlich befüllbar gewesen — die Empfangszeit und die
Quelle. Die Messzeit hätte der Adapter setzen müssen, also die Zeit des
Lesens statt der Erfassung, und die Qualität wäre eine Erfindung des Adapters
geblieben: „Bytes gelesen, also gültig."

OPC UA liefert beides direkt:

| Kehler OS | OPC UA | über PUT/GET |
| --- | --- | --- |
| `StateValue.quality` | **StatusCode** (Good / Uncertain / Bad) | vom Adapter angenommen |
| `StateValue.measured_at` | **SourceTimestamp** | Lesezeit statt Messzeit |
| `StateValue.received_at` | ServerTimestamp bzw. Eingang | vorhanden |
| `Entity.deadband` | **DataChangeFilter** (serverseitig) | clientseitig, nach der Übertragung |
| `expected_interval_s` | Sampling- und Publishing-Intervall | nur Abfragetakt |

Die Zeile zur Qualität ist die wichtigste. Ein defekter Analogeingang meldet
in der SPS einen schlechten StatusCode; über PUT/GET wäre davon nur ein
Zahlenwert angekommen, und Kehler OS hätte ihn als gültig angezeigt. Genau
diese Art stiller Falschaussage soll das Qualitätsmodell verhindern
(Kapitel 18 §38) — mit OPC UA kommt die Antwort aus der Anlage statt aus einer
Annahme.

**Ereignisse statt Abfragen.** OPC UA kennt Subscriptions: Der Server meldet
Änderungen von sich aus. ADR 0002 musste zyklisches Lesen vorschreiben, weil
snap7 nichts anderes anbietet. Damit entfällt der Kompromiss zwischen
Reaktionszeit und Buslast (Kapitel 5 §18, Kapitel 12 §74) — die Deadband-Werte
aus der Fahrzeugkonfiguration wandern in den Filter des Servers und
unterdrücken Meldungen, bevor sie das Netz belasten.

**Benannte Knoten statt Adressen.** Ein NodeId wie
`ns=3;s="DB_Kehler"."Tank"."Frisch_Gross"` überlebt eine Umstrukturierung des
Datenbausteins; `DB10.DBX4.2` tut das nicht. Und der Adressraum lässt sich
**durchsuchen** — die Zuordnung muss nicht vollständig von Hand geliefert
werden, sie kann gelesen und dann bestätigt werden.

**Kein Eingriff in die SPS-Projektierung.** PUT/GET verlangte, den
optimierten Bausteinzugriff zu deaktivieren und die PUT/GET-Freigabe zu
setzen — beides Lockerungen an der Steuerung, allein damit ein fremder
Rechner mitlesen kann. Beides entfällt.

**Blockierend gegen asyncio.** `python-snap7` ist blockierend; ADR 0002 sah
deshalb einen Executor vor, damit die Event-Loop nicht einfriert
(Kapitel 17 §11). `asyncua` ist von Grund auf asyncio. Der Thread-Pool
entfällt, und mit ihm eine Fehlerquelle, die dieses Projekt an anderer Stelle
bereits einen reproduzierbaren Absturz gekostet hat (siehe
`platform/database.py`).

## Sicherheit — was sich ändert und was nicht

**Was sich ändert:** Der Weg zur SPS ist nicht mehr ungeschützt. OPC UA bietet
Signierung, Verschlüsselung und Authentifizierung über Zertifikate. Damit
verliert die Aussage aus ADR 0002 ihre Gültigkeit, wonach jeder im selben Netz
mit der Steuerung sprechen kann, sofern er die Adressen kennt.

**Bedingung:** Das gilt **nur bei aktivierter Sicherheit.** Ein OPC-UA-Server
lässt sich mit `SecurityPolicy: None` betreiben, und dann ist er so offen wie
PUT/GET — mit dem Unterschied, dass er sicher aussieht. Verbindlich für dieses
Projekt:

> **`Basic256Sha256` oder stärker, Modus `SignAndEncrypt`, Anmeldung nicht
> anonym.** Eine Verbindung ohne Sicherheit wird nicht aufgebaut, auch nicht
> ersatzweise. Ein stiller Rückfall auf eine ungesicherte Verbindung wäre
> genau die Art Bequemlichkeit, die eine Schutzmaßnahme wertlos macht.

**Was sich nicht ändert:** Die Kehler-OS-API selbst bleibt ohne Anmeldung
erreichbar. Der Fahrzeughalter hat Benutzer und Berechtigungen ausdrücklich
abbestellt (Beschluss W14). Wer im Netz ist, kann weiterhin über Kehler OS das
Garagentor öffnen — nur eben nicht mehr an Kehler OS vorbei direkt die SPS.

Punkt I3 (Netztrennung) verliert damit seine Rolle als **einzige** tragende
Maßnahme, bleibt aber sinnvoll. Er wird von `BLOCKIEREND` auf `EMPFOHLEN`
zurückgestuft — nicht, weil das Problem gelöst wäre, sondern weil es nicht
mehr dasselbe Problem ist.

## Umsetzung

```
Adapter (Interface, unverändert)
├── OpcUaAdapter        asyncua        ← neu
└── SimulationAdapter   unverändert
```

Die Adapterschnittstelle bleibt, wie sie ist. Das war der Zweck der
Abstraktion, und dieser Wechsel ist ihr erster echter Beleg: Oberhalb der
Adapterschicht ändert sich **keine Zeile** — nicht im State Store, nicht im
Command Bus, nicht in der Oberfläche.

Was der Adapter zu leisten hat:

- **Verbindungsaufbau mit Zertifikat**, kein Rückfall auf eine ungesicherte
  Verbindung.
- **Subscriptions** je Datenpunkt, mit Deadband und Intervall aus der
  Fahrzeugkonfiguration. Die Werte stehen dort bereits.
- **StatusCode übersetzen**, nicht überschreiben: `Good` → `VALID`,
  `Uncertain` → `STALE`, `Bad` → je nach Unterkategorie `ERROR` oder
  `UNKNOWN`. Die Zuordnung gehört in den Adapter und nirgendwo sonst hin.
- **SourceTimestamp übernehmen**, statt die Empfangszeit als Messzeit
  auszugeben.
- **Verbindungsabbruch** erkennen und mit Backoff neu aufbauen; die
  betroffenen Datenpunkte gehen dabei auf `UNKNOWN` und nicht auf einen
  Standardwert (Kapitel 11 §17).
- **Schreiben** ausschließlich über die Command-Kette, mit demselben
  Bestätigungsverhalten wie bisher.

## Konsequenzen

- **ADR 0002 ist ersetzt.** Die dort beschriebenen TIA-Einstellungen —
  PUT/GET-Freigabe, optimierter Bausteinzugriff deaktiviert — werden **nicht**
  mehr benötigt. Sind sie bereits gesetzt, sollten sie zurückgenommen werden:
  Eine offene PUT/GET-Freigabe neben einem gesicherten OPC-UA-Server ist eine
  unverschlossene Hintertür neben einer verschlossenen Vordertür.
- **A2 ändert sich inhaltlich:** Statt Rack und Slot werden Endpunkt-URL,
  Sicherheitsrichtlinie und Anmeldeverfahren gebraucht.
- **A3 wird kleiner:** Der Adressraum ist durchsuchbar. Statt einer
  handgeschriebenen Adressliste genügt der Zugang; die gefundene Zuordnung
  wird anschließend bestätigt.
- **I3 wird zurückgestuft** — siehe oben.
- **Abhängigkeit:** `asyncua` statt `python-snap7`.
- Bis Zugang und Zuordnung vorliegen, läuft weiterhin ausschließlich der
  Simulator.

## Was offen bleibt

Ob die Lizenzlage dauerhaft trägt, ist eine Frage an die Anlage und nicht an
die Software. Sollte der Server nach Ablauf einer Testlizenz den Dienst
einstellen, meldet Kehler OS das als Verbindungsverlust — die Werte gehen auf
`UNKNOWN`, es wird nichts weitergezeigt, was nicht mehr aktuell ist. Das ist
das richtige Verhalten, aber es ersetzt keine gültige Lizenz.
