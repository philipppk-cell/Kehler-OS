# ADR 0005 – Realtime zwischen Backend und Clients

**Status:** angenommen · Phase 1
**Bezug:** Kapitel 5 §17, Kapitel 13 §28–§32, Kapitel 17 §104/§105, Kapitel 18 §40/§41

## Entscheidung

**WebSocket unter `/api/v1/realtime`, mit initialem Snapshot, danach
sequenznummerierten Deltas und clientseitigem Reconnect mit erneutem Snapshot.**

## Abwägung

**WebSocket — gewählt.** Eine dauerhafte Verbindung pro Client, geringer
Overhead je Nachricht, integrierte Ping/Pong-Lebendprüfung. Letztere ist der
entscheidende Punkt: Kehler OS muss den Unterschied zwischen „gerade keine
Änderung“ und „Verbindung tot“ zuverlässig erkennen (Kapitel 11 §65). Bei
Server-Sent Events wäre dafür ein zusätzlicher Mechanismus nötig.

**Server-Sent Events — verworfen.** Einfacher, aber nur unidirektional und ohne
eingebaute Lebendprüfung. Der Vorteil wäre gering, der Verlust real.

**Polling — verworfen** als Grundmechanismus. Kapitel 5 §18 verbietet es nicht,
verlangt aber, dass es keine unnötige Last erzeugt. Für Zustandsänderungen wäre
es genau das.

**MQTT bis in den Browser — verworfen.** MQTT wird eingangsseitig für Victron
genutzt; es bis in die Clients durchzureichen, würde einen Broker in den
kritischen Bedienpfad legen und die Berechtigungsprüfung (Kapitel 15 §43)
umgehbar machen. Der Client spricht ausschließlich mit dem Kehler-OS-Backend.

## Protokoll

```
Client verbindet + authentifiziert
  → Server: SNAPSHOT { version, entities[], alerts[], system }
  → Server: DELTA { seq, entity_id, changes }   (fortlaufend)
  ← Client: PONG                                (Lebendprüfung)
```

**Reihenfolgesicherung.** Jede Zustandsänderung trägt eine je Entity monoton
steigende Sequenznummer. Der Client verwirft Deltas mit kleinerer Sequenz als
der bereits verarbeiteten. Damit kann ein verzögertes `OPENING` kein bereits
bestätigtes `OPEN` überschreiben — der Fall, den Kapitel 13 §32 ausdrücklich
benennt.

**Reconnect.** Nach einem Abbruch verbindet sich der Client mit exponentiellem
Backoff neu und fordert einen **vollständigen neuen Snapshot** an. Er arbeitet
nie mit seinem alten Stand weiter (Kapitel 17 §105). Bis der Snapshot da ist,
zeigt die Oberfläche den Verbindungszustand — nicht die letzten bekannten Werte
als aktuelle.

**Keine Vollupdates bei Einzeländerungen.** Ein geänderter Tankwert erzeugt ein
Delta, keinen neuen Gesamtzustand (Kapitel 13 §29).

**Drosselung.** Analoge Werte werden mit Deadband und Mindestintervall
übertragen, damit ein zappelnder Sensor nicht das Netz und die Oberfläche
flutet (Kapitel 13 §67/§68).

## Befehle laufen nicht über den WebSocket

Befehle gehen als `POST /api/v1/commands` über HTTP. Gründe: eindeutige
Fehlercodes, saubere Authentifizierungs- und Autorisierungsprüfung pro Aufruf,
einfachere Nachvollziehbarkeit im Audit-Log. Die Rückmeldung zum
Befehlsfortschritt kommt dann über den WebSocket, verknüpft über die
Command-ID (Kapitel 13 §18).

## Konsequenzen

- Der WebSocket-Endpunkt benötigt dieselbe Authentifizierung wie die REST-API;
  eine offene Realtime-Verbindung ist ein Zugriffsweg wie jeder andere.
- Der Snapshot muss in sich konsistent sein — er wird aus einer einzigen
  Momentaufnahme des State Stores erzeugt, nicht feldweise zusammengesammelt.
