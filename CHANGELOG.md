# Changelog

Format angelehnt an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [Semantic Versioning](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Hinzugefügt

- **Phase 1 – Analyse und Architektur** abgeschlossen:
  - Systemarchitektur mit Schichtung Frontend → API → Kern → Adapter → Hardware
  - Daten-, Command- und Eventmodell einschließlich Namenskonvention
  - sieben Architekturentscheidungen (ADR 0001–0007) mit Abwägung und
    Konsequenzen: Backend-Stack, SPS-Transport, Victron-Anbindung,
    Datenhaltung, Realtime, Frontend-Stack, Prozessmodell
  - Analyse der Spezifikation mit neun identifizierten Widersprüchen bzw.
    offenen Entscheidungen
  - strukturierte Sammlung der offenen Hardwareanforderungen
  - Roadmap mit zwölf Meilensteinen und Funktionsstatus
- Anforderungskapitel 1–18 im Wortlaut archiviert
- Beschreibung der verbindlichen Dashboard-Designreferenz

### Hinzugefügt — M1/M2: Backend-Kern und Simulation

- **Domänenmodell:** Zustandswerte mit Qualität, Quelle und getrennten
  Zeitstempeln; Entities mit Capabilities; Befehle mit vollständigem
  Lebenszyklus; Ereignisse und Warnungen.
- **State Store** als einzige Wahrheit. Startet vollständig `UNKNOWN` und wird
  nie aus einer Datenbank wiederhergestellt. Werte altern selbsttätig zu
  `STALE` und `UNKNOWN`, wenn Aktualisierungen ausbleiben.
- **Command Bus** mit serverseitiger Prüfung vor jedem Hardwarekontakt,
  Serialisierung je Entity, entitätsspezifischen Timeouts und Bestätigung
  durch die Hardware. Ein Befehl gilt nie als erfolgreich, solange die
  Hardware nichts gemeldet hat.
- **Adapterschicht** mit einheitlicher Schnittstelle; Simulationsadapter als
  gleichrangige Implementierung, inklusive gezielt auslösbarer Fehlerbilder
  (Sensordefekt, ungültiger Wert, verstummter Sensor, blockierte Mechanik).
- **Supervisor** mit Fehlergrenzen je Dienst, Backoff und
  Crash-Loop-Erkennung.
- **REST- und WebSocket-Schnittstelle** unter `/api/v1`: Snapshot beim
  Verbinden, danach Deltas mit Sequenznummern. Statuscodes bilden das
  tatsächliche Befehlsergebnis ab.
- **Konfiguration** als validiertes YAML; Capabilities werden aus dem
  Entity-Typ abgeleitet. Demokonfiguration für die Simulation, ausdrücklich
  ohne erfundene Tankkapazitäten oder Hardwareadressen.
- 69 Tests mit Schwerpunkt auf Fehlerzuständen; Lint sauber.

### Hinzugefügt — M3/M4: Designsystem und Dashboard

- **Design-Tokens** als einzige Quelle für Farbe, Abstand, Radius, Typografie
  und Bewegung. Nachtmodus und reduzierte Bewegung tauschen ausschließlich
  Tokenwerte; keine Komponente kennt ein Thema.
- **Primitive** (Karte, Statuspunkt, Wert, Balken, Schalter, Schnellzugriff,
  Zeile, Button, „Nicht konfiguriert"). Die Komponente `Value` ist der einzige
  Ort, an dem ein Messwert dargestellt wird — dadurch kann keine Seite einen
  unbekannten Zustand versehentlich als Zahl ausgeben.
- **Fahrzeugvisualisierung** als Inline-SVG mit dokumentiertem Koordinatenplan.
  Sie ist reine Ausgabe. Bewegungen entstehen aus echten Zuständen; ein
  unbekannter Zustand wird gestrichelt gezeigt statt in einer erfundenen
  Position, und nicht konfigurierte Hardware wird gar nicht gezeichnet.
- **Realtime-Client** mit Snapshot beim Verbinden, Deltas mit Sequenzprüfung,
  exponentiellem Backoff und vollständigem Neuabgleich nach Verbindungsverlust.
- **Dashboard** mit Kopfbereich, Navigation, Fahrzeugstatus, Warnungen,
  Schnellzugriffen und Karten für Energie, Wasser und Klima.
- **Warnungsableitung im Backend** (`core/alerts.py`) — die Bewertung, ob etwas
  eine Warnung ist, ist Geschäftslogik und gehört nicht in die Oberfläche.
  Bewusst **ohne Schwellenwertwarnungen**, solange die Schwellen nicht
  konfiguriert sind (offener Punkt C3).
- **Verhalten ohne Verbindung** durchgängig geprüft: Banner, alle Werte als
  veraltet gekennzeichnet, Zustände als unbekannt geführt, Bedienelemente
  gesperrt und keine Entwarnung im Warnungsbereich.

### Hinzugefügt — drehbare 3D-Fahrzeugansicht

- **Das Fahrzeug wird dreidimensional dargestellt und lässt sich mit dem
  Finger frei drehen** (ein Finger dreht, zwei Finger ändern den Abstand,
  eine Schaltfläche stellt die Ausgangsansicht her). Damit sind alle vier
  Seiten erreichbar — Garage im Heck, Eingangstür und Markise rechts,
  Solarfeld auf dem Dach.
- **Gerendert wird nur bei Änderung.** Es gibt keine Renderschleife: Ein Bild
  entsteht beim Drehen, beim Auslaufen der Bewegung oder bei einem
  Zustandswechsel. Ein stillstehendes Dashboard kostet keine Grafiklast.
- Die Geometrie entsteht im Code aus einer Maßtabelle statt aus einer
  Modelldatei — dadurch bleibt sie lesbar und korrigierbar, und im Repository
  liegt kein Binärartefakt.
- **Rückfallebene ohne WebGL:** die bisherige SVG-Seitenansicht mit denselben
  Zuständen. Sie überbrückt außerdem das Nachladen der 3D-Ansicht.
- Die Ehrlichkeitsregeln gelten unverändert: unbekannte Stellung heißt
  durchscheinendes Bauteil in Ruhelage ohne Bewegung, nicht konfigurierte
  Hardware wird gar nicht erzeugt. Die Markisenkassette gehört zum Aufbau —
  nur das ausgefahrene Tuch ist ein Zustand.
- Fahrzeugreferenz aus den Fotos dokumentiert; Gesamtlänge (11,5 m) und
  Gesamthöhe (4,0 m) sind angegeben, alle übrigen Maße sind einzeln als
  Schätzung gekennzeichnet (Punkt K1).
- [ADR 0008](docs/architektur/adr/0008-fahrzeugdarstellung-3d.md) mit der
  Begründung, warum die 3D-Absage aus ADR 0006 revidiert wurde.

### Hinzugefügt — M5: Wasser

- **Vier Tanks mit realen Kapazitäten** (Frischwasser 550 l und 450 l,
  Grauwasser 280 l, Schwarzwasser 370 l). Damit zeigt die Oberfläche Liter
  statt nur Prozent. Punkt C2 ist für die Kapazitäten geklärt.
- **Gesamtmenge Frischwasser** über beide Tanks — im Backend gerechnet, weil
  zwei Regeln darin Geschäftslogik sind: über Liter statt über Prozent
  summieren, und **keine Summe, wenn ein Tank keinen belastbaren Wert
  liefert**. Ein halber Gesamtstand sieht aus wie ein ganzer.
- **Wasserseite** mit Gesamtmenge, Einzeltanks, Abwasser (belegt und frei),
  Pumpenschalter und einem Abschnitt, der benennt, was noch fehlt.
- **Fehlerinjektion über die API** (`/diagnostics/simulation/fault`), damit
  sich die seltenen Zustände prüfen lassen, ohne auf sie zu warten
  (Kapitel 18 §65). Im Produktivbetrieb nicht vorhanden.
- Die Fahrzeugkonfiguration heißt jetzt `vehicle.yaml` statt
  `vehicle.simulation.yaml` und gilt in allen Betriebsarten — sie enthält
  reale Fahrzeugdaten. Jeder Eintrag ist als `BESTÄTIGT` oder `VORLÄUFIG`
  gekennzeichnet. Hardwareadressen liegen weiterhin ungetrackt in
  `config/hardware/`.

### Hinzugefügt — Warnschwellen in zwei Stufen

- **Schwellen sind konfiguriert und wirken** (Punkt C3 geklärt):

  | Tank | Warnung (orange) | Kritisch (rot) |
  | --- | --- | --- |
  | Frischwasser | unter 20 % | unter 10 % |
  | Grau-/Schwarzwasser | über 80 % | über 90 % |

- **Beide Stufen werden im Balken als Markierung eingezeichnet** — man sieht
  damit nicht nur, *dass* es eng wird, sondern auch, wie weit es bis zur
  nächsten Stufe ist.
- **Eine Stufe erzeugt eine Meldung, nicht zwei.** Unterhalb beider Schwellen
  erscheint ausschließlich die kritische. Zwei Meldungen für denselben
  Sachverhalt wären Rauschen.
- Eine überschrittene kritische Schwelle hebt den Systemzustand auf
  „Kritisch". Durch die eng gefassten Grenzen bleibt das selten — und behält
  damit seine Bedeutung (Kapitel 13 §55).
- **Es gibt weiterhin keine eingebauten Schwellen.** Steht in der
  Konfiguration keine, wird für diesen Wert nicht gewarnt und der Balken
  bleibt neutral. Ein Test hält fest, dass außer den Wassertanks keine Entity
  eine Schwelle trägt.
- **Die Tanks sind gleichmäßig geformt** (Punkt C2 vollständig geklärt). Die
  Umrechnung Prozent → Liter ist damit exakt; eine Kalibrierkurve entfällt.
- Warnungstexte nennen jetzt Wert und Schwelle („Nur noch 13 % —
  Warnschwelle 20 %"). Die Übersetzungsschicht kann dafür Platzhalter
  einsetzen.
- **Messwerte lassen sich in der Simulation gezielt setzen**
  (`/diagnostics/simulation/level`). Ohne das ließen sich Schwellenwarnungen
  nur prüfen, indem man wartet, bis der Simulator zufällig dorthin driftet.

### Geändert — dunkleres Rot

- Das Rot ist deutlich tiefer und ernster. Dabei ist es in **zwei
  Abstufungen** getrennt, weil ein einziger Wert nicht beides kann:
  - `--error` (#e5484d) für **Text** — Statuszeilen, Banner, Meldungen. Es
    hält 5,1:1 Kontrast und bleibt damit auch bei Sonneneinstrahlung lesbar
    (Kapitel 7 §26). Ein dunkleres Rot fällt unter 4,5:1.
  - `--error-solid` (#c81e1e) für **Flächen** — Balken und Statuspunkte. Dort
    gilt die Anforderung von 3:1, und das Rot kann deshalb spürbar dunkler
    sein.
- Die Kontrastwerte sind im Token gemessen und dokumentiert, damit ein
  späterer Farbwechsel nicht versehentlich unter die Grenze rutscht.

### Behoben — Anzeige und Bewertung stimmten bei gerundeten Werten nicht überein

- Ein Tank mit 19,6 % erschien als „20 %" — mit orangem Balken, obwohl die
  Warnschwelle „unter 20 %" lautet. Zahl und Farbe widersprachen sich.
- Schwellen werden jetzt am **gerundeten** Wert geprüft, also an genau der
  Zahl, die auf dem Bildschirm steht. Ein Tanksensor löst ohnehin kein halbes
  Prozent auf; Übereinstimmung ist mehr wert als diese Scheingenauigkeit.

### Behoben — Zustände, die sich widersprachen

- **`STALE` verwarf seinen Wert.** Damit war „veraltet" inhaltlich nicht von
  „unbekannt" zu unterscheiden und die dreistufige Alterung aus Kapitel 13 §9
  hatte keine mittlere Stufe mehr. Jetzt behält ein veralteter Wert seine
  Zahl und wird sichtbar gekennzeichnet; `UNKNOWN`, `INVALID` und `ERROR`
  tragen weiterhin keinen Wert.
- **Ein verstummter Sensor erzeugte keine Warnung.** `UNKNOWN` war von der
  Warnungsableitung ausgenommen — ausgerechnet der schwerwiegendste
  Sensorzustand blieb stumm. Jetzt wird unterschieden: „seit dem Start noch
  nichts gemeldet" bleibt ohne Warnung, „hat gemeldet und ist verstummt"
  ergibt eine Warnung.
- **Systemzustand und Warnungen wurden getrennt abgeleitet und konnten sich
  widersprechen.** Der Systemstatus meldete „Alles in Ordnung", während eine
  Warnung in der Liste stand. Der Gesamtzustand ergibt sich jetzt aus
  denselben Warnungen, die die Oberfläche anzeigt.

### Korrigiert — Fahrzeugmodell nach zusätzlichem Foto

Eine Drohnenaufnahme mit Umgebung und geöffnetem Heck hat drei Fehler
aufgedeckt, die aus den Sonnenfotos nicht erkennbar waren:

- **Heckmechanik:** Die Garage öffnet über **eine oben angeschlagene
  Heckklappe**, die nach oben hebt — nicht über zwei Flügeltüren. Die
  waagerechte Fuge in der Heckwand war als Mittelteilung fehlgedeutet worden.
- **Farbe:** Der Lack ist **grau mit leichtem Blaustich**, nicht weiß. In
  praller Sonne wirkt er ausgebrannt hell. Lichtstärken und Umgebungs-
  spiegelung sind entsprechend zurückgenommen — bei den alten Werten wäre aus
  dem Grau wieder ein Weiß geworden.
- **Fenster und Aufbaufront:** Fenster größer, tiefer sitzend, mit gerundeten
  Ecken und kräftigem Rahmen. Die obere Vorderkante des Aufbaus ist
  abgeschrägt, nicht gerundet.

### Behoben

- **Warnungstexte fehlten in der Übersetzungstabelle.** Die Warnungskarte hat
  den rohen Schlüssel angezeigt (`alert.sensorStale` statt „Seit längerem
  keine Rückmeldung").

### Geändert

- **ADR 0006 korrigiert:** Zustand und TanStack Query entfallen. Der
  Fahrzeugzustand kommt über einen einzigen WebSocket; es gibt keine Abfragen
  zu cachen. Stattdessen Reacts eingebautes `useSyncExternalStore`.
- **Simulation** kennt jetzt Wertebereiche je Einheit und einen eigenen Typ für
  binäre Kontakte, damit keine unplausiblen Werte entstehen.

### Entschieden (2026-08-09)

- **SPS-Transport:** S7-Kommunikation über snap7 statt OPC UA — keine Lizenz.
  Folge: Netztrennung wird sicherheitstragend (ADR 0002, Punkt I3 aufgewertet).
- **Speichermedium:** SSD bestätigt (Punkt I1).
- **Victron:** schreibend nur für Eingangsstrombegrenzung und Wechselrichter
  ein/aus, als Whitelist mit Bestätigungspflicht (ADR 0003, Punkt B3).
- **Szenen entfallen vollständig** (W10). Automatisierungsregeln,
  Schnellzugriffe und Fahrzeugmodi bleiben.
- **Navigation entfällt vollständig** (W1).
- **Umfang Version 1.0 bestätigt.** Nivellierung, Kameras und KI danach (W9).
- **Manueller Eingriff gewinnt** gegenüber Komfortautomatisierungen: sichtbare,
  zeitlich begrenzte Übersteuerung; Sicherheitsregeln übersteuern sie (W5).
- **Abfahrtscheck entfällt** (W11). Die Einzelzustände bleiben sichtbar.

### Offen

- Bilddatei der Designreferenz fehlt im Repository (nur Beschreibung vorhanden)
- keine realen Hardwareparameter vorhanden — Entwicklung läuft simuliert
- Übersteuerungsdauer und Bindung an den Moduswechsel im Detail (vor M6)
