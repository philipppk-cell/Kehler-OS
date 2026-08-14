# Kehler OS – Roadmap

Abgeleitet aus den Phasen und Meilensteinen des Kapitels 18 (§90, §130).

## Statuskennzeichnung

Kapitel 18 §131/§132 verlangt, dass jederzeit erkennbar ist, wie weit eine
Funktion tatsächlich ist — und dass eine funktionierende Simulation **nicht**
mit fertiger Hardwareintegration verwechselt wird.

| Status | Bedeutung |
| --- | --- |
| `PLANNED` | geplant, nicht begonnen |
| `IN PROGRESS` | in Arbeit |
| `SIMULATED` | funktioniert vollständig gegen die Simulation |
| `HARDWARE TESTED` | gegen reale Hardware geprüft |
| `PRODUCTION READY` | Definition of Done erfüllt, im Fahrzeug freigegeben |

---

## Meilensteine

### M1 – Architektur und Grundgerüst · `SIMULATED`

Analyse, Technologieentscheidungen, Datenmodell, Projektstruktur, Backend- und
Frontend-Skelett, Konfiguration, Logging, Testgerüst, Entwicklungsumgebung.

**Erreicht.** Das Backend startet, liefert einen konsistenten Zustand über
REST und WebSocket, verarbeitet Befehle mit vollständigem Lebenszyklus und
wird von 69 Tests abgedeckt.

### M2 – Simulation · `SIMULATED`

Vollständiger Simulationsadapter mit Zustandsmaschinen, plausiblen Verläufen
und **gezielt auslösbaren Fehlerbildern** (SPS offline, Victron-Timeout,
ungültiger Sensor, blockierte Garage). Ohne Fehlersimulation ist die
Simulation wertlos (Kapitel 18 §65).

**Erreicht.** Der Simulationsadapter erfüllt dieselbe Schnittstelle wie die
realen Adapter und erzeugt Sensordefekt, ungültige Werte, verstummte Sensoren
und blockierte Mechanik. Die Wertebereiche sind je Einheit hinterlegt, damit
keine unplausiblen Zahlen entstehen (48 V auf einem 24-V-System hätte den
Zweck der Simulation verfehlt).

### M3 – Designsystem · `SIMULATED`

Tokens (Farben, Typografie, Abstände, Radien, Schatten, Glows, Statusfarben),
Primitive (Button, Switch, Slider, Card, Dialog, Navigation, Statusanzeige),
Icon-Set, Bewegungsregeln, Bootscreen.

**Fertig, wenn:** jede spätere Seite ausschließlich aus diesen Bausteinen
gebaut werden kann und kein Einzelwert außerhalb der Tokens existiert.

**Erreicht.** Alle Farben, Abstände, Radien, Schriftgrade und Bewegungszeiten
stehen in `frontend/src/design/tokens.css`; Nachtmodus und
`prefers-reduced-motion` tauschen ausschließlich Tokenwerte. Die Primitive
liegen in `primitives.tsx`. `Value` ist dabei der **einzige** Ort, an dem ein
Messwert dargestellt wird — dadurch ist „UNKNOWN wird nie zu 0" (Kapitel 18
§38) einmal umgesetzt statt überall wiederholt.

Noch offen: Slider und Dialog entstehen mit dem ersten Fachmodul, das sie
braucht (M5). Ein Bausteinvorrat auf Verdacht wäre Aufwand ohne Nutzen. Das
Layout bleibt bis zur Klärung des Displayformats (offener Punkt I4) responsiv.

### M4 – Dashboard · `SIMULATED`

Kopfbereich, linke Navigation, Fahrzeugvisualisierung, Warnungen,
Schnellzugriffe, Karten für Energie, Wasser, Klima, Nivellierung und Verbrauch,
Systemstatus. Umsetzung der Designreferenz.

**Fertig, wenn:** die Definition of Done für UI (Kapitel 18 §120) erfüllt ist —
einschließlich der Darstellung von Laden, Unbekannt, Offline und Fehler.

**Erreicht.** Das Dashboard läuft gegen die Simulation. Die vier geforderten
Sonderfälle sind gegen einen laufenden Server geprüft, nicht nur behauptet:

| Fall | Verhalten |
| --- | --- |
| Unbekannt | „—" mit Hinweis, nie eine Zahl |
| Offline | Banner, alle Werte als *veraltet* markiert, Fahrzeugteile gestrichelt, Schnellzugriffe gesperrt, keine Entwarnung im Warnungsbereich |
| Fehler | eigener Zustand, getrennt von Unbekannt |
| Nicht konfiguriert | ruhiger Hinweis, keine Bedienung, das Teil wird am Fahrzeug **nicht** gezeichnet |

Die Fahrzeugvisualisierung ist auf Wunsch des Fahrzeughalters **dreidimensional
und drehbar** ([ADR 0008](architektur/adr/0008-fahrzeugdarstellung-3d.md)).
Gerendert wird nur bei Änderung; ohne WebGL übernimmt die SVG-Seitenansicht.
Offen bleibt die Messung der Bildrate auf dem realen Display (Punkt I4).

Bewusst **nicht** enthalten: Karten für Nivellierung und Verbrauch. Die
Nivellierung ist ausdrücklich nach 1.0 verschoben (Kapitel 18 §91), und für
eine Verbrauchsanzeige fehlt der Verlauf über die Zeit — sie käme mit der
Zeitreihen-Datenhaltung, nicht mit einer weiteren Momentaufnahme.

### M5 – Fachmodule · `PLANNED`

In dieser Reihenfolge, begründet abweichend von Kapitel 18 §90:

1. **Wasser** · `SIMULATED` — **vier** Tanks (zwei Frischwasser à 550 l und
   450 l, Grauwasser 280 l, Schwarzwasser 370 l), Gesamtmenge Frischwasser,
   Literanzeige, Pumpe.

   **Erreicht.** Die Gesamtmenge entsteht im Backend über Liter statt über
   Prozent und entfällt vollständig, sobald ein Tank keinen belastbaren Wert
   liefert — geprüft gegen einen laufenden Server mit gezielt verstummtem
   Sensor.

   Zwei Warnstufen je Tank sind gesetzt — Frischwasser unter 20 % bzw. 10 %,
   Abwasser über 80 % bzw. 90 % — und beide im Balken als Markierung
   sichtbar. Die Tanks sind gleichmäßig geformt, die Literangabe damit exakt.
   Die Punkte C2 und C3 sind geschlossen.

   Die Historie ist mit M5b dazugekommen; damit ist Wasser vollständig.
2. **Energie** · `SIMULATED` — Batterie (Ladezustand, Spannung, Strom,
   Leistung), Energiefluss über Solar, Landstrom, Batterie und Verbrauch,
   Landstromanschluss, Wechselrichter.

   **Erreicht.** Die Laderichtung („lädt", „entlädt", „ruht") entsteht im
   Backend samt der Totzone, ab der eine Richtung überhaupt behauptet wird —
   ohne belastbaren Messwert bleibt sie leer statt „ruht".

   Schreibend gibt es genau die zwei erlaubten Funktionen (Punkt B3):
   Wechselrichter ein/aus mit Bestätigungspflicht und die
   Eingangsstrombegrenzung, einstellbar zwischen 3 und 16 A. Die Obergrenze
   ist die reale Absicherung des Anschlusses; höhere Werte weist der Command
   Bus ab, auch wenn ein Client die Oberfläche umgeht.

   Restlaufzeit und Energieinhalt gibt es seit der Angabe der Batterie-
   kapazität (900 Ah). Die Restlaufzeit ist als Hochrechnung des
   augenblicklichen Verbrauchs gekennzeichnet und entfällt beim Laden.

   Die Historie ist mit M5b dazugekommen; damit ist Energie vollständig.
3. **Klima** und **Heizung** · `SIMULATED` / `VORBEREITET` — zwei Bereiche,
   weil es zwei Systeme sind.

   **Klima erreicht.** Klima und Heizung laufen beide über die Steuerung,
   sind aber getrennte Systeme (bestätigt 2026-08-10) — und die Trennung
   liegt im Datenmodell, nicht nur in der Navigation: eigene Domäne
   `heating.`, eigener Schalter, eigener Sollwert. Ein gemeinsamer Sollwert
   wäre die aufgeräumtere Oberfläche und die falsche Anlage.

   **Heizung vorbereitet.** Verbaut ist eine **SCHEER selection 10/17 kW** mit
   **HeatMate V4.02** — eine zentrale Heizungs- und Warmwasseranlage mit zwei
   Wärmequellen, zwei Heizkreisen (Heizkörper und Fußbodenheizung),
   Warmwasserbereitung und Elektroheizung. Die Seite ist deshalb ein
   Anlagen-Dashboard und kein Raumthermostat.

   Die HeatMate bleibt Regler und Schutzeinrichtung; Kehler OS ist
   übergeordnete Bedien- und Anzeigeebene (ADR 0009). Die Anlage ist mit 22
   Entities vollständig beschrieben — aber die Modbus-Registerliste liegt
   nicht vor (Punkt G1), also trägt jede Funktion `unverified`. Das ist
   wirksam und nicht dekorativ: Eine unverifizierte Entity bekommt keine
   Capabilities, und ohne Capability entsteht kein Bedienelement.

   Bestätigt und festgehalten: zwei Heizkreise, **eine** Temperatur (Ist und
   Soll, Kessel und Warmwasser nicht getrennt), drei Elektrostufen à 1/2/3 kW.

   Offen bleibt die Registerliste. Ihr Eintreffen ist eine
   Konfigurationsänderung, kein Umbau.
4. **Fahrzeug** · `SIMULATED` — Garagentor, Einstiegsstufe, Markise,
   Eingangstür.

   **Erreicht.** Die Seite behandelt das letzte fehlende Bedienmuster:
   **bewegliche Teile**. Ein Schalter kennt zwei Zustände, ein bewegliches
   Teil sechs — vier davon sind keine Endlagen.

   Daraus folgten zwei Korrekturen im Kern, die erst diese Seite sichtbar
   gemacht hat:

   * **Der Stopp wurde abgewiesen**, solange eine Bewegung lief — mit „es
     läuft bereits ein Befehl". Genau der Befehl, dessen Zweck der Abbruch
     ist. Er unterbricht jetzt, statt zu warten.
   * **Eine blockierte Mechanik lief in den Timeout** und meldete danach
     „keine Rückmeldung". Die Hardware hatte geantwortet, nur eben `BLOCKED`.
     Die Meldung kommt jetzt sofort und benennt den Grund.

   Blockierte Bewegung erscheint außerdem in den Warnungen — sonst stünde
   „Alles in Ordnung" über einer feststeckenden Stufe.

   Bewusst **nicht** enthalten: Fenster und Verriegelungen (keine Entities,
   also keine Bedienelemente) und eine Gesamtbewertung „abfahrbereit" (W11).
5. **Garage** — **entfallen.** Das Garagentor ist ein bewegliches Aufbauteil
   und steht mit allen Fahrbefehlen auf der Fahrzeugseite; der Bereich
   enthielt genau diese eine Entity. Ein eigener Reiter hätte einen Bereich
   behauptet, wo eine Zeile ist. Navigationseintrag und Platzhalterseite sind
   entfernt.
6. **Diagnose** · `ERREICHT` — vorgezogen vor Einstellungen, weil die
   Hardware-Inbetriebnahme näher liegt als die Einstellungen: Sobald der
   Modbus-Draht liegt und die SPS angebunden wird, ist dies das Werkzeug, mit
   dem sich beantworten lässt, ob ein Wert ankommt.

   Kern der Seite ist die **Entity-Tabelle**: jede Entity mit Kennung,
   Verbindung, Qualität, Rohwert, Quelle und Rückstand, durchsuchbar über
   Name *und* Kennung. Sie unterscheidet die drei Arten von Abwesenheit, die
   das ganze System unterscheidet — „nicht konfiguriert" (offene Zuordnung),
   „noch zu verifizieren" (offene Frage) und „auffällig" (tatsächliche
   Störung). Der Filter „Auffällig" schließt die ersten beiden aus; sonst
   bestünde er dauerhaft aus bekannten offenen Punkten.

   Der **Rückstand** rechnet bewusst nicht gegen die Uhr des Tablets, sondern
   gegen den jüngsten Zeitstempel des Systems: Ein Fahrzeug ohne dauerhafte
   Internetverbindung hat regelmäßig abweichende Uhren, und „vor drei
   Stunden" an einem eben eingetroffenen Wert wäre ausgerechnet hier die
   schädlichste Falschauskunft. Gelesen wird er gegen `expected_interval_s`:
   Wo keine regelmäßige Meldung erwartet wird — ein Garagentor —, ist ein
   stehender Zeitstempel der Normalzustand und wird gedämpft dargestellt.

   Die **Simulationswerkzeuge** (Kapitel 18 §65) sind damit erstmals bedienbar
   statt nur als Endpunkt vorhanden. Welche Fehlerbilder eine Entity annimmt
   und ob sich ihr Wert setzen lässt, meldet der Adapter je Entity; die
   Oberfläche führt darüber keine eigene Liste. Im Produktivbetrieb sind die
   Werkzeuge nicht vorhanden — die Absicherung liegt im Backend, das
   Ausblenden ist nur die Folge.

   Zwei Fehler kamen dabei heraus, siehe CHANGELOG: ein gesunder, ruhiger
   Fühler alterte fälschlich zu `STALE` und `UNKNOWN`, und zwei getrennt
   gerechnete Zähler ergaben mehr offene Punkte als es Entities gibt.
7. **Einstellungen** · `ERREICHT` — bewusst kurz.

   Kapitel 6 §13 nennt neun mögliche Einstellungen. Von diesen hat heute genau
   eine eine echte Wirkung: der **Nachtmodus**, der als Farbdämpfung im
   Designsystem längst gebaut war und nur nie einen Schalter hatte. Dazu kommt
   **Bildschirm wach halten**, das der Browser tatsächlich kann.

   Die übrigen sieben sind nicht gebaut und werden **benannt statt
   verschwiegen** — jede mit ihrem Grund, in einer eigenen Karte. Eine
   Sprachauswahl mit einem Eintrag, ein Helligkeitsregler, den der Browser
   nicht erreicht, ein Netzwerkbereich ohne Netzwerkverwaltung: Jedes davon
   wäre ein Bedienelement ohne Wirkung.

   Die Anzeigeeinstellungen gehören ausdrücklich **diesem Gerät**. Ein
   Benutzersystem gibt es nicht (M7) und eine Einstellungspersistenz im
   Backend ebenso wenig — „global gespeichert" wäre eine Erfindung, „folgt
   dir" eine Halbwahrheit. Sie liegen im Speicher des Tablets, und die
   Oberfläche sagt das.

   Die **Fahrzeugkonfiguration** steht darunter, nur lesend: Bereiche,
   Kapazitäten, Schwellen, Sollwertgrenzen. Kapitel 6 §14 trennt sie von den
   Benutzereinstellungen, und die Trennung ist keine Förmlichkeit — eine
   Tankgröße ist keine Vorliebe.

   Nebenbefund, dokumentiert unter I4: „Bildschirm wach halten" gibt es nur
   über HTTPS. Über einfaches HTTP fehlt die Browser-Schnittstelle
   vollständig — ein Argument mehr für die ohnehin anstehende Netzarbeit.
8. **Nivellierung** — bewusst spät, siehe unten

> **Licht entfällt vollständig** (2026-08-10). Die Beleuchtung läuft über
> gewöhnliche Lichtschalter und nicht über die SPS. Es gibt weder Entities
> noch einen Reiter — was nicht angebunden ist, erscheint nicht. Punkt F1 ist
> damit erledigt statt offen.
>
> **Kameras entfallen ebenso** (2026-08-12). Das Fahrzeug hat keine. Reiter,
> Symbol und die Domäne `camera` im Vokabular der Entity-IDs sind entfernt.
> Punkt H1 ist damit erledigt statt offen.

> **Begründung der Abweichung** (Kapitel 18 §138): Kapitel 18 §90 beginnt mit
> Licht — das entfällt hier ersatzlos, weil die Beleuchtung nicht auf der SPS
> liegt. Wasser steht stattdessen zuerst, weil es rein lesend ist und damit
> die gesamte Kette von Sensorskalierung über Qualitätszustände und
> Schwellenwarnungen bis zur Historie durchspielt, **ohne** einen einzigen
> Aktor zu bewegen. Die ersten schreibenden Funktionen sind stattdessen die
> Wasserpumpe und der Wechselrichter. Nivellierung steht zuletzt, weil
> Kapitel 18 §91 Hydraulik ausdrücklich nicht am Anfang sehen will — was für
> die reale Integration gilt und sinnvollerweise auch für die
> Modulreihenfolge.

### M5b – Historie und Zeitreihen · `SIMULATED` (2026-08-10)

Sie zählt zu M5 und nicht zu einem neuen Thema: Bei **Wasser** und **Energie**
steht sie jeweils als *einziger* offener Punkt. Erst mit ihr sind die beiden
Fachmodule fertig.

Umsetzung nach ADR 0004: eigene SQLite-Datei `history.db` mit WAL, Rohtabelle
plus vorberechnete Rollups (Minute, Stunde) aus einem Hintergrunddienst.

**Zwei Festlegungen, die den Ausschlag geben:**

1. **Die Qualität wird mitgeschrieben.** Kapitel 16 §97 verbietet, fehlende
   Messwerte als reale Historie auszugeben. Ein verstummter Fühler muss in der
   Kurve eine **Lücke** erzeugen und keine gerade Linie zwischen den beiden
   Punkten, zwischen denen niemand etwas wusste.
2. **Ein Ausfall der Historie reißt die Steuerung nicht mit** (Kapitel 16 §88).
   Deshalb die getrennte Datei und ein überwachter Dienst mit eigener
   Fehlergrenze.

**Gemessene Datenrate** (Simulation, 20 Messgrößen, 5-Sekunden-Takt): rund
1,4 Zeilen je Sekunde, im ungünstigsten Fall 4. Hochgerechnet sind das bei
sieben Tagen Rohdaten grob 100 MB — für eine SD-Karte tragbar, aber die
Größenordnung, an der man drehen würde. Die Stellschrauben stehen alle in der
Konfiguration: `sample_interval_s`, `raw_days` und die Deadbands je Entity.

Die Deadbands selbst sind für **reale** Sensorik gewählt (0,5 A, 5 W, 0,2 °C).
Dass der Simulator sie im Sekundentakt überschreitet, ist eine Eigenschaft des
Simulators und kein Grund, sie zu ändern.

**Erreicht.** Verlaufskarte auf Wasser und Energie mit Auswahl von Messgröße
und Zeitraum (6 Stunden bis 30 Tage). Die Kurve ist von Hand als SVG gebaut
und nicht mit einer Diagrammbibliothek: Gebraucht werden eine Linie, eine
Achse und die Fähigkeit, Lücken als Lücken zu zeichnen — und Letzteres ist
genau das, was fertige Bibliotheken standardmäßig falsch machen.

Eine Lücke wird dabei nicht nur ausgelassen, sondern **gezeichnet**: Eine kurze
Lücke ist wenige Pixel breit und sähe sonst aus wie ein Darstellungsfehler
statt wie eine Aussage. Gegen einen laufenden Server geprüft mit einem gezielt
ausgelösten Sensorfehler — die Kurve zerfällt an dieser Stelle sichtbar in
zwei Abschnitte mit einer gekennzeichneten Lücke dazwischen.

### M6 – Automatisierungen · `ZURÜCKGESTELLT` (2026-08-10)

Deterministische Engine (Trigger, Bedingungen, Aktionen), Hysterese,
Entprellung, Verzögerungen, Cooldown, Schleifenerkennung, Historie, Dry Run.

> **Zurückgestellt, nicht gestrichen.** Auf die Frage, was automatisiert werden
> soll, lautet die Antwort des Fahrzeughalters: nichts — ihm fällt keine Regel
> ein, die er haben möchte. Das deckt sich mit dem technischen Befund: Die
> naheliegenden Regeln scheitern heute an fehlenden Voraussetzungen (Fahrmodus
> J1, Modbus G1, Klimaanbindung) oder gehören als Schutzfunktion in die
> Hardware. Begründung und Einzelfälle in W13.
>
> Gebaut wird die Engine, sobald es eine erste reale Regel gibt — und dann
> anhand dieser Regel. Die Voraussetzungen stehen bereits: serverseitige
> Prüfung im Command Bus, `Trigger.AUTOMATION` im Datenmodell, Event Bus.

> **Ohne Szenen und ohne Abfahrtscheck.** Entscheidungen vom 2026-08-09,
> dokumentiert als W10 und W11 in
> [`analyse/widersprueche-und-offene-punkte.md`](analyse/widersprueche-und-offene-punkte.md).
>
> Bei manuellem Eingriff gewinnt der Benutzerbefehl: Er setzt eine sichtbare,
> zeitlich begrenzte Übersteuerung, die Komfortregeln respektieren und
> Sicherheitsregeln übersteuern (W5).

### M7 – Benutzer und Sicherheit · `ENTFALLEN` (2026-08-10)

Vorgesehen waren Authentifizierung, Geräteregistrierung, Rollen und granulare
Berechtigungen, Sessions mit Widerruf, Audit-Log, Service-Modus, abgesicherte
APIs.

> **Auf Wunsch des Fahrzeughalters entfallen** (Beschluss W14): keine Benutzer,
> keine Berechtigungen. Für ein Fahrzeug mit einem Besitzer verwaltet eine
> Anmeldung nichts und steht im Weg.
>
> **Was daraus folgt:** Wer das Backend über das Netz erreicht, darf alles, was
> Kehler OS kann.
>
> *Nachtrag 2026-08-12:* Dieser Absatz endete früher mit dem Satz, die
> Absicherung liege damit **vollständig** auf der Netztrennung — weil auch die
> S7-Kommunikation über PUT/GET weder Verschlüsselung noch Authentifizierung
> kannte. Seit auf der SPS ein **OPC-UA-Server** läuft, stimmt das nicht mehr
> ([ADR 0010](architektur/adr/0010-opc-ua-statt-put-get.md)): Der Weg zur
> Steuerung ist jetzt signiert, verschlüsselt und authentifiziert.
>
> Offen bleibt die Kehler-OS-API selbst. Der Unterschied ist aber erheblich —
> der Weg über Kehler OS geht durch Befehlsprüfung, Grenzwerte,
> Risikoeinstufung und Protokollierung, der direkte Weg zur SPS ging an
> alledem vorbei. **I3 ist deshalb nicht mehr blockierend, sondern eine
> Abwägung darüber, wer ins Fahrzeug-WLAN kommt.**
>
> Der `Authorizer`-Haken im Command Bus bleibt bestehen. Er kostet nichts, und
> Kapitel 18 §120 verbietet, erst zu bauen und später abzusichern: Käme je eine
> Prüfung dazu, liegt die Stelle dafür fest.
>
> Der **Service-Modus** aus dieser Liste ist damit nicht erledigt, sondern
> heimatlos. Er ist keine Berechtigungsfrage, sondern eine Betriebsart, in der
> Automatik und Warnungen bewusst schweigen. Er wird bei Bedarf einzeln
> aufgegriffen.

### M8 – Reale SPS-Integration · `PLANNED` · **blockiert durch A1–A3, A5**

Beginn mit **digitalen Lesewerten**, danach ein ungefährlicher Ausgang, erst
danach weitere Aktoren. Jede Funktion durchläuft die Testcheckliste aus
Kapitel 17 §127.

### M9 – Victron · `PLANNED` · **blockiert durch B1**

Zunächst ausschließlich lesend. Schreibzugriffe nur nach ausdrücklicher
Bestätigung eines Bedarfs (B3).

### M10 – Weitere Hardware · `PLANNED`

Tanksensoren, Verriegelungen, Garage, zuletzt Hydraulik. Einzeln und
kontrolliert.

### M11 – Stabilisierung · `PLANNED`

Dauerlauftest über mehrere Tage mit Beobachtung von Speicherverbrauch,
Reconnects, Datenbankwachstum und Latenzen. Sicherheitsreview nach Kapitel 17
§110. Backup- und Restore-Probe auf einem zweiten Raspberry Pi.

### M12 – Produktivfreigabe · `PLANNED`

Kiosk-Betrieb, Autostart, Update- und Rollback-Weg, vollständige Dokumentation.

---

## Abgrenzung Version 1.0

**Bestätigt am 2026-08-09.**

**Enthalten:** Dashboard, Wasser, Energie, Klima, Heizung, Fahrzeug,
Einstellungen, Diagnose, Automatisierungen, Benutzer und Berechtigungen,
reale SPS- und Victron-Anbindung, Backup/Restore, Kiosk-Betrieb.

*Garage ist seit dem 2026-08-10 kein eigener Bereich mehr — das Garagentor
steht vollständig auf der Fahrzeugseite. Der Funktionsumfang ändert sich
dadurch nicht, nur die Navigation.*

*Licht ist seit dem 2026-08-10 nicht mehr enthalten — die Beleuchtung liegt
nicht auf der SPS. Klima und Heizung stehen dafür einzeln, weil es zwei
getrennte Systeme sind.*

**Nach 1.0:** Nivellierung mit realer Hydraulik, KI-Assistent, Fernzugriff,
Predictive Maintenance, Wetterstation.

**Gestrichen:** Szenen (W10), Navigation (W1) und Kameras (H1) — die ersten
beiden Entscheidungen des Projektverantwortlichen, die dritte eine Tatsache
über das Fahrzeug: Es hat keine.

---

## Funktionsstatus

Wird ab M2 fortlaufend gepflegt.

| Bereich | Status |
| --- | --- |
| Architektur und Datenmodell | `SIMULATED` |
| Backend-Kern (State, Commands, Events) | `SIMULATED` |
| Simulation mit Fehlerbildern | `SIMULATED` |
| REST- und Realtime-Schnittstelle | `SIMULATED` |
| Designsystem | `PLANNED` |
| Dashboard | `PLANNED` |
| alle Fachmodule | `PLANNED` |
| SPS-Anbindung | `PLANNED` — blockiert |
| Victron-Anbindung | `PLANNED` — blockiert |
| KI-Assistent | `PLANNED` — letzte Ebene |
