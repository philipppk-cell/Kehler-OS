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

### Entfernt — Keine Benutzer und keine Berechtigungen (Beschluss W14)

- Der Fahrzeughalter möchte **keine Benutzer und keine Berechtigungen**. Für
  ein Fahrzeug mit einem Besitzer verwaltet eine Anmeldung nichts und steht im
  Weg. M7 entfällt.
- **Das Feld `permission` in der Entity-Konfiguration ist entfernt.** Es wurde
  von niemandem ausgewertet — eine Konfiguration, die stillschweigend
  wirkungslos bleibt, ist schlimmer als keine: Wer sie setzte, glaubte etwas
  abgesichert zu haben. Da unbekannte Felder verboten sind, scheitert ein
  solcher Eintrag jetzt laut statt zu schweigen.
- **Das Benutzersymbol im Kopfbereich ist entfernt.** Ein Symbol, das ein Konto
  andeutet, hinter dem keines liegt, ist ein Versprechen.
- **Das Netzsymbol daneben zeigt jetzt den Verbindungszustand**, statt
  unverändert dazustehen. Ein Symbol, das wie eine Statusanzeige aussieht und
  keine ist, wäre Dekoration an genau der Stelle, an der Kapitel 7 §5 sie
  verbietet.
- Die Rückfrage bei riskanten Aktionen (`Risk.HIGH`) bleibt. Sie schützt vor
  dem versehentlichen Antippen, nicht vor einem Unbefugten — beides zu
  verwechseln wäre der Fehler, und das steht jetzt so in der Konfiguration.
- Der `Authorizer`-Haken im Command Bus bleibt bestehen und lässt alles durch.
  Das steht ausdrücklich im Code, samt der Folge: **Die Absicherung liegt
  damit vollständig auf der Netztrennung** (Punkt I3). Wer das Backend über
  das Netz erreicht, darf alles, was Kehler OS kann. Neu ist das nicht — für
  die S7-Kommunikation galt es schon immer (ADR 0002) —, aber I3 ist jetzt die
  einzige tragende Maßnahme.

### Hinzugefügt — M5b: Messhistorie

- **Verlaufskarte auf Wasser und Energie** mit Auswahl von Messgröße und
  Zeitraum (6 Stunden bis 30 Tage). Damit ist bei beiden Fachmodulen der
  jeweils letzte offene Punkt geschlossen.
- **Aufzeichnung** in einer eigenen SQLite-Datei nach ADR 0004: Rohtabelle
  plus vorberechnete Rollups für Minute und Stunde. Zeitstempel in UTC —
  eine lokale Zeit würde beim Zeitzonenwechsel Stunden doppeln oder
  verschlucken (Kapitel 16 §85).
- Geschrieben wird nach den drei Bedingungen aus Kapitel 16 §8:
  Qualitätswechsel, Wertänderung über das Deadband, oder Herzschlagzeit
  abgelaufen. Der Herzschlag ist der wichtige Teil — ohne ihn ließe sich
  „der Wert war konstant" nicht von „das System war aus" unterscheiden.
- **Lücken bleiben Lücken** (Kapitel 16 §97), durchgesetzt an vier Stellen:
  Ein unbelastbarer Wert kommt als `NULL` in die Datenbank, ein verdichteter
  Eimer ohne gültige Werte bekommt keine Kennzahl, gelesen wird nichts
  aufgefüllt, und die Kurve zerfällt in eigenständige Abschnitte statt über
  das Loch hinwegzuzeichnen.
- Eine Lücke wird zusätzlich **gezeichnet** und nicht nur ausgelassen: Eine
  kurze Lücke ist wenige Pixel breit und sähe sonst aus wie ein
  Darstellungsfehler statt wie eine Aussage.
- Die Kurve ist von Hand als SVG gebaut. Gebraucht werden eine Linie, eine
  Achse und die Fähigkeit, Lücken als Lücken zu zeichnen — Letzteres ist
  genau das, was fertige Diagrammbibliotheken standardmäßig falsch machen.
  Eine Abhängigkeit mitzunehmen, um ihr Standardverhalten abzuschalten, wäre
  der schlechtere Handel (Kapitel 18 §4).
- Die Achse beginnt **nicht** bei null, wenn die Werte es nicht tun: Ein
  Ladezustand zwischen 58 % und 62 % gegen eine Achse ab 0 % ist eine flache
  Linie, die nichts zeigt.
- „Historie nicht verfügbar" ist von „keine Werte in diesem Zeitraum"
  unterschieden. Das erste ist eine Aussage über die Datenhaltung, das zweite
  eine über das Fahrzeug.

### Behoben — Speicherzugriffsfehler beim Beenden

- Eine abgebrochene Koroutine bricht keinen Thread ab. Wurde der
  Historiendienst beim Herunterfahren abgebrochen, während er gerade schrieb,
  lief der Schreibvorgang weiter — und die unmittelbar danach geschlossene
  Verbindung ließ SQLite auf freigegebenen Speicher zugreifen. In der
  Testsuite reproduzierbar als Segfault.
- Die Datenbank hat jetzt einen eigenen Executor mit genau einem Arbeiter,
  und beim Schließen wird gewartet, bis nichts mehr läuft. Erst die Arbeit zu
  Ende, dann die Verbindung zu.

### Geändert — Segmentierte Auswahl im Designsystem

- Diagnose und Historie brauchen dieselbe Bedienung: wenige gleichrangige
  Möglichkeiten, von denen genau eine gilt. Sie liegt jetzt als `Segmented`
  im Designsystem statt zweimal in je einer Seite (Kapitel 7 §39/§40).

### Hinzugefügt — M5: Einstellungen

- **Seite „Einstellungen"** — bewusst kurz. Kapitel 6 §13 nennt neun mögliche
  Einstellungen; genau eine davon hat heute eine echte Wirkung.
- **Nachtmodus.** Die Farbdämpfung war im Designsystem seit Beginn gebaut
  (`:root[data-night]`) und hatte nie einen Schalter — ein fertiges Merkmal
  ohne Zugang. Sie wird vor dem ersten Rendern angewandt, sonst blitzt die
  helle Darstellung auf, bevor sie greift: nachts im Fahrzeug genau der
  Moment, den die Einstellung verhindern soll.
- **Bildschirm wach halten.** Ein fest verbautes Bedienpanel, das nach zwei
  Minuten schwarz wird, ist kein Bedienpanel. Der Schalter zeigt den Wunsch,
  die Anzeige daneben den tatsächlichen Zustand — das Betriebssystem kann die
  Sperre ablehnen oder beim Wegblenden einziehen, und „ein" zu zeigen, während
  das Display ausgeht, wäre eine Behauptung (Kapitel 18 §37). „Vom Gerät
  abgelehnt" ist dabei von „nicht aktiv" unterschieden: Wer nach dem Umlegen
  nur „nicht aktiv" liest, sucht den Fehler bei sich.
- Die Anzeigeeinstellungen gehören **diesem Gerät** und sagen das auch. Ein
  Benutzersystem gibt es nicht (M7), eine Einstellungspersistenz im Backend
  ebenso wenig — „global gespeichert" wäre eine Erfindung, „folgt dir" eine
  Halbwahrheit. Ein fremder oder älterer Eintrag im lokalen Speicher wird
  feldweise geprüft, nicht blind übernommen.
- **Fahrzeugkonfiguration**, nur lesend: Bezeichnung, Bereiche und die
  hinterlegten Zahlen — Tankkapazitäten, Batteriekapazität und Nennspannung,
  Sollwertgrenzen, Warn- und Kritischschwellen. Kapitel 6 §14 trennt sie von
  den Benutzereinstellungen; eine Tankgröße ist keine Vorliebe. Neuer Endpunkt
  `GET /api/v1/vehicle`, ausschließlich lesend.
- Zeilen zu noch nicht bestätigten Funktionen tragen ihre Kennzeichnung mit:
  Bei der Heizung stehen 1 bis 3 kW in der Beschreibung, ohne dass bestätigt
  wäre, dass sich die Stufen schalten lassen. Ohne den Hinweis läse sich die
  Zeile wie eine Zusage.
- **Die sieben fehlenden Einstellungen werden benannt, nicht verschwiegen** —
  Sprache, Einheiten, Displayhelligkeit, helles Thema, Zeitformat,
  Benachrichtigungen, Netzwerk, Automatisierungen, Benutzer: jede mit ihrem
  Grund. Eine erklärte Lücke ist etwas anderes als eine vergessene.

### Behoben — Der Einheitenschlüssel stand im Text

- „16 bis 30 celsius" statt „16 bis 30 °C". Die Zuordnung von
  Einheitenschlüssel zu lesbarem Zeichen lag privat in `primitives.tsx`; die
  neue Seite baute sich daraufhin ihre eigene. Sie ist jetzt exportiert, und
  die Kennzeichnung offener Punkte (`.tag`) ist aus der Diagnoseseite ins
  Designsystem gewandert — zwei Kopien derselben Regel sehen genau so lange
  gleich aus, bis eine geändert wird (Kapitel 7 §39/§40).

### Hinzugefügt — M5: Diagnose

- **Seite „Diagnose"** — die einzige Seite, auf der Kehler OS technische
  Rohdaten zeigt (Kapitel 7 §43): Systemkennzahlen, Dienste mit
  Neustartzähler, Adapter, Meldungen einschließlich der Stufe `INFO`, und als
  Arbeitsfläche eine **Entity-Tabelle** mit Kennung, Verbindung, Qualität,
  Rohwert, Quelle und Rückstand.
- Die Tabelle hält die **drei Arten von Abwesenheit** auseinander, die das
  System überall unterscheidet: „nicht konfiguriert" ist eine offene
  Zuordnung, „noch zu verifizieren" eine offene Frage, „auffällig" eine
  tatsächliche Störung. Der Filter „Auffällig" schließt die ersten beiden
  ausdrücklich aus — sonst bestünde er dauerhaft aus den 25 bekannten offenen
  Punkten und wäre für den einen Fall unbrauchbar, für den es ihn gibt.
- Gesucht wird über **Kennung und übersetzten Namen**. Wer „Garage" tippt,
  denkt nicht an `vehicle.garage.door`; wer die Kennung kennt, tippt sie.
- Der **Rückstand** vergleicht Backend-Zeit mit Backend-Zeit: den Zeitstempel
  eines Wertes gegen den jüngsten Zeitstempel des Systems, nicht gegen die Uhr
  des Tablets. Ein Fahrzeug ohne dauerhafte Internetverbindung hat regelmäßig
  abweichende Uhren, und „vor drei Stunden" an einem eben eingetroffenen Wert
  wäre ausgerechnet auf dieser Seite die schädlichste Falschauskunft.
  Gelesen wird er gegen `expected_interval_s`, das die API dafür neu
  mitliefert: Wo keine regelmäßige Meldung erwartet wird — ein Garagentor —,
  ist ein stehender Zeitstempel der Normalzustand und wird gedämpft
  dargestellt statt als Befund.
- Die **Simulationswerkzeuge** aus Kapitel 18 §65 sind damit erstmals
  bedienbar und nicht nur als Endpunkt vorhanden: Fehlerbilder auslösen und
  Messwerte auf einen Stand setzen, beides an der in der Tabelle ausgewählten
  Entity.
- Was dabei möglich ist, meldet der Adapter **je Entity** über
  `GET /api/v1/diagnostics/simulation`; die Oberfläche führt darüber keine
  eigene Liste. Das ist nicht dieselbe Auskunft für alle: Nur Mess- und
  Sollwerte lassen sich setzen, `BLOCKED` bewirkt ausschließlich an
  beweglichen Teilen etwas, und eine Entity ohne simuliertes Gerät — ein
  `status` ohne bekannte Zustandsnamen — bietet gar nichts an. Zwei Listen
  derselben Sache wären auseinandergelaufen, und dann stünde am Ladezustand
  eine Schaltfläche „Blockiert", die nichts tut.
- **Im Produktivbetrieb gibt es die Werkzeuge nicht.** Die Absicherung liegt
  im Backend (`available: false`, leere Auskunft, 404 auf die Endpunkte); das
  Ausblenden in der Oberfläche ist nur die Folge.

### Behoben — Ein ruhiger Fühler alterte fälschlich zu „veraltet" und „unbekannt"

- Das Deadband unterdrückt die **Meldung** einer Änderung. Es unterdrückte
  bisher auch den **Empfang**: Ein Wert innerhalb des Deadbands wurde
  verworfen, und damit blieb sein Zeitstempel stehen.
- Die Alterung rechnet gegen genau diesen Zeitstempel. Ein völlig gesunder
  Fühler, der schlicht nichts Neues zu melden hatte, wurde deshalb nach dem
  erwarteten Intervall als `STALE` und nach dem doppelten als `UNKNOWN`
  geführt. Beim Ladezustand — Deadband 0,5 %, erwartetes Intervall 10 s, Drift
  0,04 %/s — trat das im laufenden Betrieb regelmäßig auf und war auf der
  neuen Diagnoseseite sofort zu sehen. Ein stehendes Fahrzeug mit vollem
  Frischwassertank hätte nach 20 Sekunden „Unbekannt" angezeigt, obwohl der
  Tank meldet.
- Das ist der gefährlichere der beiden möglichen Fehler. Einen alten Wert als
  aktuell auszugeben wäre falsch — aber einen aktuellen Wert für unbekannt zu
  erklären, entwertet die Kennzeichnung selbst: Wer „Veraltet" oft genug an
  gesunden Werten sieht, glaubt ihr nicht mehr, wenn sie zählt.
- Der Zeitbezug wird jetzt auch bei unterdrückten Werten nachgeführt. Es
  entsteht dabei bewusst kein Delta, keine neue Sequenznummer und keine
  Netzlast — die Oberfläche hat schon den richtigen Wert, nur die Uhr geht
  weiter. Ein wirklich verstummter Fühler altert unverändert.

### Behoben — Zwei getrennt gerechnete Zähler ergaben mehr offene Punkte als Entities

- Die Diagnoseseite wies „Offen (49)" bei 45 Entities aus. „Nicht
  konfiguriert" und „noch zu verifizieren" wurden addiert — bei der Heizung
  gilt aber **beides gleichzeitig**, weil das, was noch zu verifizieren ist,
  erst recht nicht zugeordnet ist.
- Zähler und Filter benutzen jetzt dasselbe Prädikat. Getrennt gerechnet
  laufen zwei Antworten auf dieselbe Frage unweigerlich auseinander — dieselbe
  Lehre wie beim Systemzustand gegenüber den Warnungen.

### Geändert — Der Bereich „Garage" ist entfallen

- Hinter dem Navigationseintrag lag genau eine Entity: das Garagentor. Es
  steht mit allen Fahrbefehlen auf der Fahrzeugseite. Ein eigener Reiter hätte
  einen Bereich behauptet, wo eine Zeile ist.
- `CommandPhase.SUPERSEDED` zählt außerdem jetzt als abgeschlossene Phase.
  Sie fehlte in der Liste der Endzustände — eine Eigenschaft, die bei der
  zuletzt hinzugekommenen Phase falsch antwortet, ist eine Falle für den
  nächsten Leser.

### Hinzugefügt — M5: Fahrzeug

- **Seite „Fahrzeug"** mit der drehbaren Ansicht, den beweglichen Teilen
  (Garagentor, Einstiegsstufe, Markise) und der Eingangstür als Sensor.
- Damit ist das letzte Bedienmuster gebaut. Bisher: Messwert, Schalter,
  Sollwert, mehrwertiger Zustand. **Bewegliche Teile** sind das fünfte — und
  das einzige mit Zwischenzuständen: geschlossen, öffnend, offen, schließend,
  gestoppt, blockiert.
- Während einer Fahrt sind Öffnen und Schließen gesperrt (der Command Bus
  weist sie ohnehin ab), der **Stopp** dagegen nie — und er hebt sich ab,
  solange etwas fährt.
- Die Bestätigungspflicht steht in der Capability, nicht in der Oberfläche.
- Der gemeinsame Baustein `useVehicleState` liegt jetzt neben der Darstellung
  statt im Dashboard. Mit der Fahrzeugseite gibt es zwei Nutzer — und damit
  wäre eine zweite Auslegung desselben Zustands möglich geworden.

### Behoben — Der Stopp wurde abgewiesen, während etwas fuhr

- Ein laufender Fahrbefehl sperrte die Entity, und der **Stopp** lief in
  dieselbe Sperre: „Für vehicle.garage.door läuft bereits ein Befehl". Damit
  verhinderte die Bewegung genau ihren eigenen Abbruch.
- Die Regel aus Kapitel 13 §21 meint überlagerte *Fahr*befehle. Ein Stopp ist
  kein zweiter Fahrbefehl, sondern das Ende des ersten. Er trägt jetzt
  `preempts` und geht sofort durch.
- Der abgelöste Fahrbefehl endet als **`SUPERSEDED`** — ein neuer Zustand, der
  ausdrücklich **kein Fehler** ist. Wer ein fahrendes Tor anhält, hat erreicht,
  was er wollte; eine Fehlermeldung dafür wäre eine Belehrung. Erfolgreich ist
  der Befehl trotzdem nicht: Das Teil steht auf „Gestoppt", nicht auf „Offen".

### Behoben — Blockierte Mechanik meldete zu spät und das Falsche

- Ein blockiertes Teil lief bis zum vollen Timeout (Garagentor: 20 s, Stufe:
  12 s) und meldete dann „keine Rückmeldung". Beides war falsch: Die Hardware
  **hatte** geantwortet, nämlich `BLOCKED`.
- Eine Bewegung endet auf drei Arten — am Ziel, angehalten oder blockiert. Alle
  drei sind eine Antwort, und keine davon ist ein Zeitablauf. Der Command Bus
  unterscheidet sie jetzt über `superseded_states` und `failure_states`.
- Gemessen: Die Meldung kommt nach rund zwei Sekunden statt nach zwölf, und sie
  lautet „Die Bewegung wurde blockiert und angehalten" statt „Befehl konnte
  nicht ausgeführt werden". Der Grund reist als maschinenlesbares
  `ended_state` mit; `detail` bleibt Rohtext für die Diagnose.
- **Blockierte Bewegung erzeugt jetzt eine Warnung.** Vorher stand
  „Alles in Ordnung" im Systemstatus, während eine Stufe feststeckte — derselbe
  Widerspruch, der zwischen Systemzustand und Warnungen schon einmal behoben
  wurde.
- Nebeneffekt: Die Testsuite läuft in 5 statt 15 Sekunden, weil zwei Tests
  nicht mehr auf echte Timeouts warten.

### Geändert — Testbausteine leiten die Befehle aus dem Loader ab

- Die Befehlsspezifikationen für bewegliche Teile waren im Testaufbau von Hand
  nachgebaut. Sie sahen richtig aus und wichen doch von dem ab, was die
  Fahrzeugkonfiguration erzeugt — ein Test, der eine andere Spezifikation
  prüft als die ausgelieferte, prüft nichts. Sie kommen jetzt aus dem Loader.

### Hinzugefügt — Reale Geräteangaben eingearbeitet

- **Hauptdisplay ist ein iPad Pro 13 Zoll** (Punkt I4 geklärt). Damit ist die
  Anzeige kein angeschlossener Bildschirm, sondern ein eigenes Gerät im Netz:
  Die Oberfläche läuft in Safari, nicht als Kiosk auf dem Pi. Das entkoppelt
  System und Anzeige — der Pi läuft weiter, auch wenn niemand hinsieht.
  Beide Ausrichtungen sind gegen einen laufenden Server geprüft.
- **Klimagerät ist eine wandmontierte LG-Anlage** (`S3-M09JA3FA`). Sie ist
  **nicht** an die Steuerung angebunden, und auf welchem Weg das geschehen
  soll, ist offen. Vier Wege sind mit ihren Folgen dokumentiert (Punkt G1b).
- **Heizung: der Modbus-Anschluss existiert, ist aber nicht verdrahtet.** Die
  Anlage ist derzeit gar nicht mit der SPS verbunden. Damit ist die Reihenfolge
  klar — erst der Draht, dann die Registerliste, dann der Adapter. Zwischen CAN
  und Modbus ist entschieden; offen bleibt RTU gegen TCP, und das entscheidet,
  ob der SPS eine Kommunikationsbaugruppe fehlt.
- **Victron Cerbo GX**: Adresse bekannt, hinterlegt in
  `config/hardware/devices.yaml` — ungetrackt, wie alle Adressen. Der Adapter
  bleibt `simulated`: Eine eingetragene Adresse ist keine geprüfte Verbindung.
- **SPS-Aufbau** aus dem Schaltschrankfoto festgehalten: CPU 1511-1 PN im
  Zustand RUN, digitale Ein- und Ausgangsbaugruppen, keine sichtbare
  Kommunikationsbaugruppe.

### Geändert — Die Klimaanlage bekommt dieselbe Behandlung wie die Heizung

- `climate.cooling.state` und `climate.cooling.target` tragen jetzt
  `unverified: true`. Vorher zeigte die Klimaseite einen Schalter und einen
  Sollwertsteller — beides versprach eine Bedienung, deren **Weg noch nicht
  einmal ausgewählt** ist.
- Die Regel galt schon für die Heizung; sie gilt für jedes Gerät, dessen
  Anbindung offen ist. Ohne diese Gleichbehandlung hinge es vom Zufall ab,
  welche Seite ehrlich ist.
- Die beiden Temperaturfühler bleiben unberührt — sie gehören zum Fahrzeug,
  nicht zum Klimagerät. Die Seite zeigt deshalb weiterhin eine echte
  Innen- und Außentemperatur.
- Sollwert und Ein/Aus sagen jetzt beide „Noch zu verifizieren". Vorher stand
  an der einen Stelle „Unbekannt" und an der anderen „Noch zu verifizieren" —
  zwei Auskünfte über dieselbe Entity. „Unbekannt" wäre nicht falsch gewesen,
  aber es sagt das Falsche: Nicht der Messwert fehlt, sondern die Verbindung.

### Sicherheit — Netztrennung fehlt (Punkt I3)

- **Das Fahrzeugnetz ist flach**: ein LTE-Router mit Gigabit-Switch verbindet
  alle Geräte, ohne Segmentierung.
- Das trifft eine tragende Annahme von ADR 0002: Die S7-Kommunikation über
  PUT/GET kennt weder Verschlüsselung noch Authentifizierung, und ihre
  Absicherung liegt **vollständig** auf der Netztrennung. Ohne sie kann jedes
  Gerät im WLAN die Steuerung direkt ansprechen — nicht Kehler OS umgehen,
  sondern die SPS.
- Folgenlos, solange nichts real angesteuert wird; vor dem Produktivbetrieb
  aber zu lösen. Zwei Wege sind dokumentiert: VLAN auf einem verwalteten
  Switch, oder — meist praktischer — eine zweite Netzwerkschnittstelle am Pi,
  an der die SPS allein hängt.

### Behoben — Statuskarte lag auf dem iPad quer über dem Fahrzeug

- Zwei Schwellen beantworteten dieselbe Frage verschieden: Ob die Karte auf
  dem Fahrzeug liegt, entschied ein Media Query am Viewport (1200 px); ob das
  Fahrzeug ihr ausweicht, entschied die 3D-Szene an ihrer Leinwandbreite
  (820 px). Dazwischen liegt das iPad im Querformat.
- Die Verschiebung steht jetzt als `--vehicle-shift` im CSS, an derselben
  Stelle wie der Media Query; die Szene liest sie, statt selbst zu entscheiden.
- Zusätzlich hat die Karte eine eigene Schwelle bekommen (1500 px): Bei
  1376 px bleibt neben ihr kein Platz für ein 11,5 m langes Fahrzeug, also
  geht sie darunter — auch wenn das Raster zweispaltig bleiben darf.

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

### Korrigiert — Fahrzeugmaße gemessen statt geschätzt (2026-08-11)

Der Fahrzeughalter hat die fehlenden Maße aus Punkt K1 nachgereicht. Die
Längsaufteilung des Modells beruht damit nicht mehr auf Fotoproportionen:

- **Gesamtbreite 2,53 m** statt der angesetzten 2,55 m (des zulässigen
  Höchstmaßes).
- **Radstand 5,88 m, Achsabstand des Tandems 1,20 m, Hecküberhang 3,00 m.**
  Der Vorderüberhang ergibt sich daraus rechnerisch zu 1,42 m — genau der
  Serienwert eines MAN TGX. Die Achsen sind entsprechend gesetzt; Radläufe
  und Schürzenausschnitte folgen ihnen automatisch.
- **Reifen 315/80 R 22.5.** Der Radhalbmesser ist daraus gerechnet (0,538 m
  statt geschätzter 0,53 m), die Reifenbreite auf 0,315 m korrigiert.

**Ein genannter Wert war widersprüchlich und wurde nicht übernommen.** Mit
dem zuerst genannten Radstand von 4,80 m summierten sich die Längsmaße auf
10,45 m statt 11,50 m. Der fehlende Meter nach vorn gerechnet hätte die
Vorderachse hinter das Fahrerhaus gestellt — die Fotos zeigen sie eindeutig
darunter. Die Differenz entsprach zwei Reifenhalbmessern (1,08 m): gemessen
war von Reifenkante zu Reifenkante statt von Radmitte zu Radmitte. Nach
Rückfrage bestätigt und auf 5,88 m korrigiert.

- **Wohnboden ca. 1,50 m über Grund** statt geschätzter 1,85 m. Das war die
  größte Einzelabweichung des Modells: Der Aufbau ist damit 2,50 m hoch statt
  2,15 m, bei unveränderter Gesamthöhe von 4,0 m. Die Fotos hatten die
  Trennlinie zwischen Staukastenband und Wohnaufbau zu hoch gelesen — auf den
  Sonnenaufnahmen liegt dort ein harter Schatten, der wie eine Kante wirkt.
  Türunterkante, Garagenboden und Einstiegsstufe sind mit ihren Abständen zum
  Wohnboden mitgewandert, sonst hätte die Tür 35 cm über dem Boden geschwebt.

- **Die Garage ist ein eigener Raum**, nicht der hintere Teil des
  Wohnbereichs. Sie ist der überhängende Heckteil und sitzt ganz unten: Boden
  bündig mit der Unterkante des Aufbaus, Raumhöhe ca. 1,65 m. Die Heckklappe
  reicht damit von 0,72 m bis 2,37 m statt von 1,90 m bis 3,72 m — sie nimmt
  rund die Hälfte der Heckwand ein, nicht deren volle Höhe.

  Hier lagen **zwei** Fehler übereinander: Der Garagenboden war an den
  Wohnboden gekoppelt, obwohl die Garage mit ihm nichts zu tun hat, und die
  Klappenhöhe war aus den Fotos zu groß geschätzt. Auf der maßgeblichen
  Aufnahme steht die Klappe **waagerecht abstehend** — in dieser Stellung
  zeigt sie ihre Unterseite, und ihre Höhe ist aus keinem Blickwinkel
  abzuschätzen. Garagenboden und Aufbauunterkante teilen sich jetzt eine
  Konstante, damit sie nicht wieder auseinanderlaufen.

**Punkt K1 ist damit geschlossen.** Bewusst nicht weiter verfolgt: Der
Vorderüberhang bleibt gerechnet statt gemessen; Spurweiten, Klappenbreite und
Unterkante des Aufbaus bleiben geschätzt und sind durch Gesamtbreite und
Reifenoberkante nach oben begrenzt.

**Notiert, nicht gelöst:** Die Garagenoberkante liegt 0,87 m über der
Unterkante des Wohnbodens. Über dem Heck muss der Wohnboden also höher liegen
als im übrigen Fahrzeug — für die Außendarstellung ohne Belang, aber
festgehalten, damit die Zahlen nicht als Widerspruch gelesen werden.

### Dokumentiert — was Fotos für das Fahrzeugmodell leisten (Punkt K3)

Auf die Frage nach einem 3D-Modell aus vielen Fotos festgehalten: Ein
fotogrammetrischer Scan liefert ein verschmolzenes Netz ohne benannte Knoten,
mit eingebrannter Beleuchtung und in genau einem Zustand — Heckklappe offen
oder zu, nie beides. Damit wäre er als Zustandsanzeige unbrauchbar (Punkt K2).
Fotos verbessern die **Form**, liefern aber keine **Maße**, solange kein
Maßstab in derselben Ebene im Bild liegt.

Der Fall hat das gleich belegt: Die Fotos konnten den falschen Radstand nicht
ersetzen, aber sie konnten ihn widerlegen.

### Offen

- Bilddatei der Designreferenz fehlt im Repository (nur Beschreibung vorhanden)
- keine realen Hardwareparameter vorhanden — Entwicklung läuft simuliert
- Übersteuerungsdauer und Bindung an den Moduswechsel im Detail (vor M6)
