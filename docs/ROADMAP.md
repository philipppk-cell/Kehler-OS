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

   Offen bleibt nur die Historie; sie folgt mit der Zeitreihen-Datenhaltung.
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

   Offen bleibt die Historie; sie folgt mit der Zeitreihen-Datenhaltung.
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
4. **Fahrzeug** — Türen, Fenster, Stufen, Markise, Verriegelungen
5. **Garage**
6. **Einstellungen**
7. **Diagnose**
8. **Nivellierung** — bewusst spät, siehe unten
9. **Kameras** — abhängig von realer Hardware

> **Licht entfällt vollständig** (2026-08-10). Die Beleuchtung läuft über
> gewöhnliche Lichtschalter und nicht über die SPS. Es gibt weder Entities
> noch einen Reiter — was nicht angebunden ist, erscheint nicht. Punkt F1 ist
> damit erledigt statt offen.

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

### M6 – Automatisierungen · `PLANNED`

Deterministische Engine (Trigger, Bedingungen, Aktionen), Hysterese,
Entprellung, Verzögerungen, Cooldown, Schleifenerkennung, Historie, Dry Run.

> **Ohne Szenen und ohne Abfahrtscheck.** Entscheidungen vom 2026-08-09,
> dokumentiert als W10 und W11 in
> [`analyse/widersprueche-und-offene-punkte.md`](analyse/widersprueche-und-offene-punkte.md).
>
> Bei manuellem Eingriff gewinnt der Benutzerbefehl: Er setzt eine sichtbare,
> zeitlich begrenzte Übersteuerung, die Komfortregeln respektieren und
> Sicherheitsregeln übersteuern (W5).

### M7 – Benutzer und Sicherheit · `PLANNED`

Authentifizierung, Geräteregistrierung, Rollen und granulare Berechtigungen,
Sessions mit Widerruf, Audit-Log, Service-Modus, abgesicherte APIs.

> Grundlegende Sicherheitsgrenzen entstehen bereits in M1 — Kapitel 18 §120
> verbietet ausdrücklich, erst zu bauen und später abzusichern. M7
> vervollständigt, es beginnt nicht.

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

**Enthalten:** Dashboard, Wasser, Energie, Klima, Heizung, Fahrzeug, Garage,
Einstellungen, Diagnose, Automatisierungen, Benutzer und Berechtigungen,
reale SPS- und Victron-Anbindung, Backup/Restore, Kiosk-Betrieb.

*Licht ist seit dem 2026-08-10 nicht mehr enthalten — die Beleuchtung liegt
nicht auf der SPS. Klima und Heizung stehen dafür einzeln, weil es zwei
getrennte Systeme sind.*

**Nach 1.0:** Nivellierung mit realer Hydraulik, Kameras, KI-Assistent,
Fernzugriff, Predictive Maintenance, Wetterstation.

**Gestrichen:** Szenen (W10) und Navigation (W1) — beides Entscheidungen des
Projektverantwortlichen, nicht technische Einschränkungen.

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
| Kameras | `PLANNED` — keine Hardware bestätigt |
| KI-Assistent | `PLANNED` — letzte Ebene |
