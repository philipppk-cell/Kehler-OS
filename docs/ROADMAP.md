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

### M1 – Architektur und Grundgerüst · `IN PROGRESS`

Analyse, Technologieentscheidungen, Datenmodell, Projektstruktur, Backend- und
Frontend-Skelett, Konfiguration, Logging, Testgerüst, Entwicklungsumgebung.

**Fertig, wenn:** das System startet, sich verbindet, einen leeren aber
konsistenten Zustand ausliefert und die Testkette läuft.

### M2 – Simulation · `PLANNED`

Vollständiger Simulationsadapter mit Zustandsmaschinen, plausiblen Verläufen
und **gezielt auslösbaren Fehlerbildern** (SPS offline, Victron-Timeout,
ungültiger Sensor, blockierte Garage). Ohne Fehlersimulation ist die
Simulation wertlos (Kapitel 18 §65).

**Fertig, wenn:** Dashboard, Befehlskette, Warnungen, Realtime und alle
Fehlerzustände ohne reale Hardware durchspielbar sind.

### M3 – Designsystem · `PLANNED`

Tokens (Farben, Typografie, Abstände, Radien, Schatten, Glows, Statusfarben),
Primitive (Button, Switch, Slider, Card, Dialog, Navigation, Statusanzeige),
Icon-Set, Bewegungsregeln, Bootscreen.

**Fertig, wenn:** jede spätere Seite ausschließlich aus diesen Bausteinen
gebaut werden kann und kein Einzelwert außerhalb der Tokens existiert.

### M4 – Dashboard · `PLANNED`

Kopfbereich, linke Navigation, Fahrzeugvisualisierung, Warnungen,
Schnellzugriffe, Karten für Energie, Wasser, Klima, Nivellierung und Verbrauch,
Systemstatus. Umsetzung der Designreferenz.

**Fertig, wenn:** die Definition of Done für UI (Kapitel 18 §120) erfüllt ist —
einschließlich der Darstellung von Laden, Unbekannt, Offline und Fehler.

### M5 – Fachmodule · `PLANNED`

In dieser Reihenfolge, begründet abweichend von Kapitel 18 §90:

1. **Wasser** — drei Tanks, Schwellen, Kalibrierung, Historie
2. **Energie** — Batterie, Solar, Landstrom, Energiefluss, Historie
3. **Licht** — Kreise, Gruppen
4. **Klima** — Zonen, IST/SOLL, Heizung, Lüftung
5. **Fahrzeug** — Türen, Fenster, Stufen, Markise, Verriegelungen
6. **Garage**
7. **Einstellungen**
8. **Diagnose**
9. **Nivellierung** — bewusst spät, siehe unten
10. **Kameras** — abhängig von realer Hardware

> **Begründung der Abweichung** (Kapitel 18 §138): Kapitel 18 §90 beginnt mit
> Licht. Wasser steht hier zuerst, weil es rein lesend ist und damit die
> gesamte Kette von Sensorskalierung über Qualitätszustände und
> Schwellenwarnungen bis zur Historie durchspielt, **ohne** einen einzigen
> Aktor zu bewegen. Licht ist die erste schreibende Funktion und folgt
> unmittelbar. Nivellierung steht zuletzt, weil Kapitel 18 §91 Hydraulik
> ausdrücklich nicht am Anfang sehen will — was für die reale Integration gilt
> und sinnvollerweise auch für die Modulreihenfolge.

### M6 – Automatisierungen · `PLANNED`

Deterministische Engine (Trigger, Bedingungen, Aktionen), Hysterese,
Entprellung, Verzögerungen, Cooldown, Schleifenerkennung, Historie, Dry Run.

> **Ohne Szenen.** Entscheidung vom 2026-08-09, dokumentiert als W10 in
> [`analyse/widersprueche-und-offene-punkte.md`](analyse/widersprueche-und-offene-punkte.md).
> Der Abfahrtscheck ist als reine Prüfung vorgesehen — Bestätigung offen (W11).

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

**Enthalten:** Dashboard, Wasser, Energie, Licht, Klima, Fahrzeug, Garage,
Einstellungen, Diagnose, Automatisierungen, Benutzer und Berechtigungen,
reale SPS- und Victron-Anbindung, Backup/Restore, Kiosk-Betrieb.

**Nach 1.0:** Nivellierung mit realer Hydraulik, Kameras, KI-Assistent,
Fernzugriff, Predictive Maintenance, Wetterstation.

**Gestrichen:** Szenen (W10) und Navigation (W1) — beides Entscheidungen des
Projektverantwortlichen, nicht technische Einschränkungen.

---

## Funktionsstatus

Wird ab M2 fortlaufend gepflegt.

| Bereich | Status |
| --- | --- |
| Architektur und Datenmodell | `IN PROGRESS` |
| Simulation | `PLANNED` |
| Designsystem | `PLANNED` |
| Dashboard | `PLANNED` |
| alle Fachmodule | `PLANNED` |
| SPS-Anbindung | `PLANNED` — blockiert |
| Victron-Anbindung | `PLANNED` — blockiert |
| Kameras | `PLANNED` — keine Hardware bestätigt |
| KI-Assistent | `PLANNED` — letzte Ebene |
