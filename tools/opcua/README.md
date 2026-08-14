# OPC UA — Erkundung der SPS

Seit dem 2026-08-12 läuft auf der S7-1511-1 PN ein **OPC-UA-Server**
([ADR 0010](../../docs/architektur/adr/0010-opc-ua-statt-put-get.md)).

**Der Endpunkt steht in `config/hardware/devices.yaml`** und nicht hier —
Adressen gehören zum Fahrzeug und werden nicht versioniert (Kapitel 17 §48).
In den Beispielen unten steht deshalb `<endpunkt>`.

`erkunden.py` beantwortet die beiden Punkte, die eine reale Anbindung noch
aufhalten — **und zwar so, dass niemand eine Adressliste abtippen muss.**

| Punkt | Frage | wer beantwortet sie |
| --- | --- | --- |
| **A2** | Welche Sicherheit, welche Anmeldung? | das Werkzeug, ohne Anmeldung |
| **A3** | Welche Knoten, welche Datentypen, schreibbar? | das Werkzeug, nach Anmeldung |
| — | Was die Werte **bedeuten** | nur der, der das SPS-Programm geschrieben hat |

## Ausführen

Das Werkzeug läuft **im Fahrzeugnetz** — auf dem Raspberry Pi oder einem
Notebook, das die SPS erreicht. Nicht auf dem Entwicklungsrechner: Von dort
gibt es keine Route dorthin.

```bash
pip install asyncua
python tools/opcua/erkunden.py <endpunkt>
```

Der Bericht landet in `tools/opcua/opcua-bericht.txt` und kann weitergegeben
werden.

**Es wird ausschließlich gelesen.** Ein Erkundungslauf darf ein Fahrzeug nicht
bewegen, und dieses Werkzeug kennt keinen einzigen Schreibaufruf.

### Stufe 1 läuft immer

Die Abfrage der Endpunkte braucht **keine Anmeldung** — OPC UA erlaubt genau
diese eine Abfrage ungesichert, damit ein Client überhaupt herausfinden kann,
wie er sich sicher verbinden soll. Schon dieser Teil beantwortet A2
vollständig.

### Stufe 2 braucht eine Entscheidung

Für den Adressraum wird eine Sitzung aufgebaut, und das Werkzeug fällt dabei
**nicht** stillschweigend auf eine ungesicherte Verbindung zurück. Ohne Angabe
bricht es ab und sagt, was fehlt. Entweder:

```bash
# ausdrücklich ohne Verschlüsselung — nur lesend, im eigenen Netz vertretbar
python tools/opcua/erkunden.py <endpunkt> --unsicher

# oder verschlüsselt, mit Client-Zertifikat
python tools/opcua/erkunden.py <endpunkt> \
  --sicherheit "Basic256Sha256,SignAndEncrypt,client.der,client.pem"
```

Verlangt der Server eine Anmeldung, zusätzlich `--benutzer` und `--passwort`.
**Das Passwort erscheint nicht im Bericht.**

## Was im Bericht steht

```
▸ DB_Kehler
  ▸ Tank
    · Frisch_Gross      ns=2;i=3    Float    r   = 62.5  (12:26:38)
    · Schwarz           ns=2;i=10   Float    r   [BadSensorFailure] — kein Wert
  ▸ Garage
    · Tor_Auf           ns=2;i=6    Boolean  rw  = False (12:26:38)
```

Die Zeile mit `BadSensorFailure` ist die wichtigste des ganzen Berichts und
zugleich der Grund, warum OPC UA die bessere Wahl war: **Die Anlage sagt
selbst, dass dieser Wert nichts taugt**, und liefert dazu weder Zahl noch
Zeitstempel. Über PUT/GET wäre nur eine `0.0` angekommen, und die Oberfläche
hätte einen leeren Tank angezeigt.

Genau so arbeitet auch Kehler OS: Was nicht belastbar ist, trägt keine Zahl
(Kapitel 18 §38). Die Zuordnung ist damit unmittelbar:

| OPC UA | Kehler OS |
| --- | --- |
| StatusCode `Good` | `Quality.VALID` |
| StatusCode `Uncertain…` | `Quality.STALE` |
| StatusCode `Bad…` | `Quality.ERROR` bzw. `UNKNOWN` |
| SourceTimestamp | `StateValue.measured_at` |
| `rw` im AccessLevel | die Entity darf Befehle haben |

## Was das Werkzeug nicht leisten kann

Die **Bedeutung** der Werte. Dass ein Bit `Tor_Auf` heißt, sagt nicht, ob
`TRUE` „ist offen" oder „fahre auf" bedeutet — im ersten Fall ist es eine
Rückmeldung, im zweiten ein Befehl. Beides zu verwechseln hieße, ein Tor zu
öffnen, wo eine Anzeige gemeint war.

Diese Zuordnung steht im SPS-Programm und wird nicht geraten (Kapitel 18 §97).
Sie ist der einzige Teil von A3, der Handarbeit bleibt — und mit dem
Bericht als Vorlage ist es eine Liste zum Durchgehen statt eine zum
Schreiben.

## Der Bericht wird nicht versioniert

`opcua-bericht.txt` steht in `.gitignore`. Er enthält Bausteinnamen, Struktur
und aktuelle Messwerte der Anlage — das gehört zum Fahrzeug wie die
Hardwareadressen und damit nicht ins Repository (Kapitel 17 §48).
