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

### Hinzugefügt — M5: Energie

- **Batterie** mit Ladezustand, Spannung, Strom und Leistung. Das Vorzeichen
  trägt die Aussage: `+` lädt, `−` entlädt.
- **Energiefluss** über Solar, Landstrom, Batterie und Verbrauch. Bewusst als
  Liste gemessener Wege und **nicht** als Schaubild mit Leitungen — ein
  Schaubild müsste behaupten, wie die Anlage verschaltet ist, und das ist
  nicht bekannt (Punkt B2).
- **Laderichtung im Backend gedeutet** (`core/energy.py`), samt der Totzone,
  ab der eine Richtung überhaupt behauptet wird. Ohne sie flackerte die
  Anzeige zwischen „lädt" und „entlädt", sobald der Strom um null pendelt.
  Ohne belastbaren Messwert bleibt die Richtung leer — „ruht" sieht harmlos
  aus und wäre dort eine Lüge.
- **Landstrom** mit Anschlusszustand („verbunden", „nicht verbunden",
  „unbekannt" — drei Antworten, nicht zwei) und Strombegrenzung.
- **Wechselrichter ein/aus** mit Bestätigungspflicht beim Abschalten. Ob eine
  Bestätigung nötig ist, steht in der Capability und nicht in der Oberfläche.
- **Neuer Entity-Typ `setpoint`** mit Grenzen. Ohne konfigurierte Obergrenze
  entsteht kein Befehl und damit kein Bedienelement. Genau das trifft die
  Eingangsstrombegrenzung: Ohne die reale Absicherung des Anschlusses zu
  kennen, wäre eine Obergrenze eine gefährliche Erfindung (Kapitel 18 §136).
- Die Simulation koppelt die Energiewerte physikalisch
  (Batterie = Solar + Landstrom − Verbrauch) und gibt jeder Watt-Größe einen
  eigenen Wertebereich. Vorher trafen 640 W Solar auf 640 W Verbrauch, und
  ein Darstellungsfehler wäre in dieser Unordnung nicht aufgefallen.

### Hinzugefügt — Batteriekapazität und Landstromabsicherung

- **900 Ah bei 24 V nominal** ergeben 21,6 kWh Energieinhalt. Die Energieseite
  zeigt jetzt den verbleibenden Inhalt in Kilowattstunden und eine
  **Restlaufzeit**.
- Die Restlaufzeit ist ausdrücklich als Hochrechnung des augenblicklichen
  Verbrauchs gekennzeichnet und gibt es nur beim **Entladen** — beim Laden
  liefe nichts ab, und eine sehr große Zahl sähe dort aus wie eine
  Zusicherung. Über 48 Stunden wird nur noch „mehr als" angezeigt: Eine
  Hochrechnung auf 212 Stunden spiegelt eine Genauigkeit vor, die sie nicht
  hat.
- **16 A Absicherung** macht die Eingangsstrombegrenzung bedienbar, über
  einen Stepper mit fingergerechten Flächen statt eines Schiebereglers.
- **Der Command Bus prüft jetzt Wertebereiche.** Das ist die eigentliche
  Schutzfunktion — nicht ein Dialog in der Oberfläche: Ein Client, der die
  Oberfläche umgeht, wird ebenso abgewiesen. Ebenfalls neu geprüft: ein
  Befehl, der seinen Zielwert gar nicht mitbringt (er wäre sonst in einen
  Timeout gelaufen).
- Das Risiko der Strombegrenzung ist von `HIGH` auf `MEDIUM` gesetzt. Innerhalb
  von 3–16 A kann kein Wert die Zuleitung überlasten, weil die Obergrenze die
  Absicherung *ist*. Eine Bestätigung bei jedem Schritt wäre Reibung ohne
  Schutzwirkung.

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

### Hinzugefügt — Die Heizung ist eine SCHEER-Anlage, kein Thermostat

- **Verbaut ist eine SCHEER selection 10/17 kW mit HeatMate V4.02** (Angabe
  vom 2026-08-10): zentrale Heizung und Warmwasserbereitung, zwei
  Wärmequellen, zwei Heizkreise, Elektroheizung. Die Seite „Heizung" ist
  deshalb ein Anlagen-Dashboard und beantwortet die Frage „was macht die
  Anlage gerade" — nicht „wie warm hätten Sie es gern".
- **Die HeatMate bleibt Regler und Schutzeinrichtung.** Temperaturbegrenzer,
  Brennersteuerung und Abschaltungen gehören ihr und werden weder nachgebaut
  noch umgangen. Begründung und Datenkette in
  [ADR 0009](docs/architektur/adr/0009-heizungsanbindung-scheer.md):
  SCHEER/HeatMate → Modbus → Siemens S7-1500 → Kehler OS.
- **Neues Kennzeichen `unverified`.** Die Modbus-Registerliste liegt nicht vor
  (Punkt G1), also ist die Anlage vollständig beschrieben, aber keine Funktion
  bestätigt. Das Kennzeichen ist **wirksam und nicht dekorativ**: Der Loader
  vergibt an eine unverifizierte Entity keine Capabilities, und ohne
  Capability entsteht in der Oberfläche kein Bedienelement. Ohne diese Regel
  wäre die Konfiguration eine Wunschliste, aus der die Oberfläche Schalter
  baut, hinter denen nichts liegt.
- Damit hält das System drei Abwesenheiten auseinander, die verschiedene Dinge
  bedeuten: „nicht verfügbar" (gibt es nicht), „noch zu verifizieren" (offene
  Frage) und „nicht konfiguriert" (offene Zuordnung).
- **Neuer Entity-Typ `status`** — ein mehrwertiger, lesender Zustand. Der
  Brenner meldet keine zwei Zustände, sondern eine Betriebsphase; ein Kontakt
  könnte „Nachlauf" nicht von „aus" unterscheiden, ein Schalter würde
  behaupten, Kehler OS könne die Phase setzen.
- Die Zustandsnamen stehen als `states` in der Konfiguration. Sie sind das
  interne Vokabular von Kehler OS, nicht das der HeatMate — die Zuordnung von
  Rohwerten macht später der Adapter. Ein Zustand **ohne** diese Liste wird
  nicht simuliert: Der Fehlercode der Anlage ist Klartext, und ihn zu erfinden
  hieße, eine Diagnose zu erfinden.
- Gedeutet wird genau eine Sache, und zwar im Backend (`core/heating.py`):
  **welche Wärmequelle gerade arbeitet.** Ist eine der beiden Quellen
  unbekannt, bleibt die Aussage aus — „keine aktiv" wäre dann eine Behauptung.

### Korrigiert — Anlage nach Rückmeldung des Fahrzeughalters

Drei Annahmen eines ersten Entwurfs waren falsch und sind ersetzt:

- **Zwei Heizkreise statt drei.** Kreis 1 sind die Heizkörper, Kreis 2 ist die
  Fußbodenheizung. Der Entwurf führte die Fußbodenheizung als dritten Kreis
  neben zwei namenlosen „Heizkreis 1/2" — und hätte damit einen Kreis gezeigt,
  den es nicht gibt. Die Kreise heißen jetzt nach dem, was sie beheizen:
  „Heizkörper" und „Fußbodenheizung" sind im Fahrzeug zu finden, „Kreis 2"
  steht nur im Schaltplan.
- **Eine Temperatur statt zwei.** Die Anlage führt einen Ist- und einen
  Sollwert; Kessel und Warmwasser werden nicht getrennt geführt. Zwei
  Temperaturen anzuzeigen hätte eine Genauigkeit vorgetäuscht, die die Anlage
  nicht hat. Der Wert heißt schlicht „Temperatur" — wo der Fühler sitzt, ist
  nicht genannt und wird nicht behauptet.
- **Drei Elektrostufen: 1 kW, 2 kW, 3 kW.** Stufe und Leistung sind dasselbe —
  Stufe 2 *ist* 2 kW. Der Entwurf führte beides getrennt, eine Stufe ohne
  bekannten Bereich und daneben eine gemessene Leistung; letztere war obendrein
  ein angenommener Sensor. Geblieben ist ein Eintrag mit der Einheit, die die
  Angabe hat.
- Der bestätigte Bereich 1–3 macht die Funktion **nicht** bedienbar: Ob sich
  die Stufe über die Schnittstelle setzen lässt, ist weiterhin offen.
  Bestätigte Grenzen und bestätigter Schreibzugriff sind zwei verschiedene
  Fragen — und nur die zweite entscheidet über das Bedienelement.
- Alle drei Angaben sind in Tests festgehalten, damit sie nicht wieder
  verrutschen.

### Hinzugefügt — M5: Klima und Heizung als zwei Bereiche

- **Klima und Heizung sind getrennte Systeme** (Angabe vom 2026-08-10) und
  bekommen deshalb je einen eigenen Reiter. Die Trennung liegt nicht nur in
  der Navigation, sondern im Datenmodell: eigene Domäne `heating.`, eigener
  Schalter, eigener Sollwert. Ein gemeinsamer Sollwert wäre die aufgeräumtere
  Oberfläche und die falsche Anlage — das Verstellen der Heizung würde
  stillschweigend die Klimaanlage mitverstellen.
- **Gemeinsam bleibt allein der gemessene Wert.** Es gibt einen Wohnraum und
  einen Fühler; beide Seiten zeigen dieselbe Innentemperatur, weil es dieselbe
  ist. Die Beschriftung eines Werts kommt dabei aus der Entity und nicht aus
  der Seite — derselbe Fühler heißt damit überall gleich.
- **Ein gemeinsamer Baustein für beide Seiten** (`pages/Zone.tsx`). Zwei
  Kopien derselben Darstellung würden über kurz oder lang auseinanderlaufen,
  und dann sähe ein Sollwert auf der einen Seite anders aus als auf der
  anderen. Getrennt bleiben die Daten, nicht die Bausteine.
- **Bewusst nicht gebaut:** Betriebsarten, ein „heizt gerade"-Zustand,
  Warmwasser und Lüftung. Alles davon setzt voraus, dass ein Gerät es meldet;
  welche Geräte verbaut sind, ist offen (Punkt G1). Eine vorhandene Regelung
  wird nicht nachgebaut (Kapitel 12 §67, Kapitel 18 §29).
- Die Stellbereiche (Klima 16–30 °C, Heizung 5–30 °C, Schritt 0,5 K) sind in
  der Konfiguration als `VORLÄUFIG` markiert. Anders als bei der
  Strombegrenzung ist ein falscher Bereich hier ungefährlich — eine
  Solltemperatur kann keine Zuleitung überlasten.
- **Entity-Typ `climate_zone` entfernt.** Er erzeugte einen Sollwertbefehl
  *ohne* Bereichsprüfung — anders als `setpoint`, der ohne Obergrenze gar
  keinen Befehl erzeugt. Zwei Wege zum selben Ziel, von denen einer die
  Prüfung übersprang; geblieben ist der prüfende.
- Geprüft gegen einen laufenden Server: Der Stepper hält die Schrittweite ein,
  sperrt an der konfigurierten Untergrenze, und der Command Bus weist 95 °C
  und 4,5 °C auch dann ab, wenn ein Client die Oberfläche umgeht.

### Geändert — Sollwertverstellung ist jetzt ein Baustein des Designsystems

- Der Stepper lag auf der Energieseite und wird nun von Klima und Heizung
  mitbenutzt (`design/stepper.tsx`). Strombegrenzung und Solltemperatur sind
  fachlich weit auseinander, aber es ist derselbe Handgriff — und der muss
  überall gleich aussehen (Kapitel 7 §39).
- Dabei zwei Dinge ergänzt, die vorher fehlten:
  - **Nachkommastellen.** Ein 0,5-K-Schritt braucht eine; die
    Strombegrenzung in ganzen Ampere keine.
  - **Rundung auf das Schrittraster.** 20,5 + 0,5 ergibt in Gleitkomma nicht
    immer genau 21. Ohne Rundung wanderten winzige Reste in den Befehl und
    von dort in die Steuerung.
- Die Tasten heißen für die Sprachausgabe nach der Größe, die sie verstellen
  („Heizung Solltemperatur erhöhen"). Vorher hieß jeder Stepper im Fahrzeug
  „Strombegrenzung erhöhen".

### Behoben — ohne Verbindung verschwanden die Werte, statt zu altern

- Aufgefallen auf der neuen Klimaseite: Bei getrennter Verbindung zeigte die
  gemessene Temperatur „Unbekannt", während der Sollwert daneben seine Zahl
  behielt — dieselbe Karte, zwei Antworten auf dieselbe Frage.
- Ursache war eine Regel, die an drei Stellen anders umgesetzt war als im
  Designsystem. Die Komponente `Value` zeigt einen Wert ohne Verbindung
  weiter und kennzeichnet ihn; die Fachseiten leerten ihn. Auch der Hook
  `useWater` beschrieb bereits das Gegenteil dessen, was die Seite tat.
- Jetzt gilt überall dieselbe Regel: **Der zuletzt bekannte Wert bleibt
  stehen und wird gedämpft dargestellt.** Ihn zu leeren war kein Gewinn an
  Ehrlichkeit, sondern ein Verlust — „Verbindung weg" sah damit genauso aus
  wie „Fühler hat nie etwas gemeldet". Das ist derselbe Denkfehler, der im
  Backend schon einmal behoben wurde, als `STALE` seinen Wert verwarf.
- **Bedient wird weiterhin nichts.** Schalter, Stepper und Kacheln bleiben
  ohne Verbindung gesperrt; ein gesperrter Regler neben einer alten Zahl ist
  etwas anderes als ein bedienbarer.

### Geändert — „Veraltet" markiert den einzelnen Fühler, nicht die Funkstille

- Neuer Baustein `StaleMark` im Designsystem. Er kennzeichnet einen
  veralteten Wert als **Text** und nicht nur über eine blassere Farbe — der
  Zustand muss ohne Farbe erkennbar bleiben (Kapitel 7 §23).
- Er erscheint nur bei der Qualität `STALE`, also am einen Fühler, der
  verstummt ist, während der Rest weiterläuft. Bei getrennter Verbindung
  entfällt er: Dort ist ohnehin alles veraltet, das Banner sagt es einmal für
  die ganze Seite, und ein Schriftzug hinter jeder Zahl wäre Lärm statt
  Information. Auf der Energieseite waren es in einem Zwischenstand neun
  Stück — einer davon schob eine Stepper-Taste aus der Karte.
- Geprüft gegen einen laufenden Server: online null Markierungen, ein gezielt
  verstummter Tank genau eine, getrennte Verbindung wieder null — bei
  gedämpften, aber vorhandenen Werten.

### Geändert — Dashboard: aus „Klima" wird „Temperatur"

- Die Karte zeigte einen Sollwert, den es so nicht mehr gibt. Sie heißt jetzt
  nach der Größe statt nach einem der beiden Systeme und führt beide
  Sollwerte einzeln auf. Ein gemeinsames „Soll" würde einen der beiden
  verschweigen.
- Sie verwies außerdem auf `climate.living.target` — eine Entity, die es nach
  der Trennung nicht mehr gibt. Sichtbar war das als dauerhaftes „Nicht
  verfügbar".

### Entfernt — Lichtsteuerung

- **Die Beleuchtung wird nicht über die SPS gesteuert**, sondern über
  gewöhnliche Lichtschalter (Angabe vom 2026-08-10). Entfernt wurden deshalb
  der Reiter „Licht", die Lichtentities aus der Fahrzeugkonfiguration, die
  Lichtkacheln im Schnellzugriff und die zugehörigen Texte und Symbole.
- Das ist keine Lücke, die später gefüllt wird: Was nicht angebunden ist,
  erscheint nicht (Kapitel 12 §55). Offener Punkt F1 ist damit erledigt statt
  offen.
- Der Schnellzugriff hat dadurch vier statt sechs Kacheln und steht jetzt in
  zwei Spalten. In drei Spalten stünde eine Kachel allein in der zweiten
  Reihe; in zwei entsteht ein geschlossenes Feld mit größeren Flächen.

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
