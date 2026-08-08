# ADR 0002 – Transportweg zur Siemens S7-1511-1 PN

**Status:** vorläufig · Entscheidung offen (siehe `OPEN_HARDWARE_REQUIREMENTS.md` A1)
**Bezug:** Kapitel 5 §6, Kapitel 12 §4, Kapitel 15 §47, Kapitel 18 §10

## Entscheidung

**Der Adapter wird transportunabhängig gebaut. Empfohlen wird OPC UA;
S7-Kommunikation über snap7 bleibt als vollwertige Alternative implementierbar.
Die endgültige Wahl trifft der Projektverantwortliche, weil sie reale Kosten
verursacht.**

## Kontext

Die S7-1511-1 PN bietet für einen externen Rechner zwei etablierte Wege.
Kapitel 18 §10 verlangt, die Methode anhand der realen Konfiguration zu wählen
— die noch nicht vorliegt. Kapitel 18 §96 verlangt zugleich, deswegen nicht
stehenzubleiben.

## Abwägung

### OPC UA — empfohlen

Die CPU hat einen integrierten OPC-UA-Server. Für dieses Projekt spricht:

- **Benannte Nodes statt roher Adressen.** Das Mapping wird lesbar und
  überlebt Umstrukturierungen im SPS-Programm besser als absolute Adressen.
- **Verschlüsselung und Authentifizierung** sind Teil des Protokolls. Kapitel 15
  §46 verlangt gesicherte Kommunikation, wo technisch möglich — hier ist sie es.
- **Der optimierte Bausteinzugriff kann aktiv bleiben.** Das SPS-Programm muss
  nicht verschlechtert werden, um von außen lesbar zu sein.
- Der Client `asyncua` ist ausgereift, asynchron und reines Python.

Dagegen: Der Server benötigt eine kostenpflichtige SIMATIC-Runtime-Lizenz.
Das ist keine technische, sondern eine wirtschaftliche Hürde — und deshalb
keine Entscheidung, die die Software allein treffen darf.

### S7-Kommunikation über snap7 — Alternative

Kostenfrei und weit verbreitet. Erfordert in TIA Portal jedoch:

- „Zugriff über PUT/GET-Kommunikation erlauben“
- **Deaktivierung des optimierten Bausteinzugriffs** für alle betroffenen DBs
- keine Transportsicherheit → die Absicherung muss vollständig über
  Netzsegmentierung erfolgen (Kapitel 15 §47 sieht diesen Fall ausdrücklich vor)

Fachlich funktioniert das einwandfrei. Es verlagert aber Sicherheit vom
Protokoll in die Netzarchitektur und macht das Mapping empfindlicher gegenüber
Änderungen am SPS-Programm.

### Modbus TCP — verworfen

Wäre nur über zusätzliche Projektierung in der SPS verfügbar und böte keinen
Vorteil gegenüber den beiden nativen Wegen.

## Umsetzung

```
PlcAdapter (Interface)
├── OpcUaPlcTransport      asyncua
├── S7PlcTransport         python-snap7
└── SimulatedPlcTransport  interne Zustandsmaschine
```

Über dem Transport liegt eine gemeinsame Mapping-Schicht, die semantische IDs
auf Transportreferenzen abbildet. Die Referenz ist im Mapping ein
undurchsichtiger String — beim einen Transport eine NodeId, beim anderen eine
Adresse. Kein Code oberhalb der Adapterschicht sieht ihn.

Damit kostet ein späterer Wechsel des Transports genau eine
Konfigurationsänderung plus ein neues Mapping — und keine Änderung an Modulen,
Automatisierung oder UI.

## Konsequenzen

- Bis A1 beantwortet ist, läuft ausschließlich `SimulatedPlcTransport`.
- Für die produktive Nutzung müssen zusätzlich A2 (Netzwerkparameter) und A3
  (Mapping) vorliegen. Ohne sie wird kein realer Ausgang geschaltet.
- Fällt die Wahl auf snap7, ist die Netzsegmentierung (Kapitel 15 §40) keine
  Kür mehr, sondern die tragende Sicherheitsmaßnahme. Das wird dann in der
  Installationsdokumentation entsprechend hervorgehoben.
