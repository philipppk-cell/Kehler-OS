# KEHLER OS

# Kapitel 12 – Hardwareintegration: Siemens SPS, Raspberry Pi, Victron und Sensorik

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel beschreibt die bekannte Hardwarebasis von Kehler OS, die Aufgabenverteilung zwischen den Komponenten und die Anforderungen an deren spätere Integration.

Wo konkrete Hardware noch nicht festgelegt wurde, darf nichts erfunden werden. Die Architektur muss stattdessen so vorbereitet werden, dass die tatsächliche Hardware später konfiguriert werden kann.

Verwende Kapitel 1–12 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel

Kehler OS verbindet industrielle Steuerungstechnik, Energiekomponenten, Sensorik und moderne Software zu einem gemeinsamen System.

Dabei gilt ein fundamentales Prinzip:

Die Hardware muss auch dann sicher und kontrolliert arbeiten, wenn die grafische Benutzeroberfläche oder der Raspberry Pi nicht verfügbar ist.

Kehler OS erweitert die Fahrzeugtechnik.

Es darf keine unnötige Abhängigkeit erzeugen.

⸻

## 2. Bekannte zentrale Komponenten

Für das Fahrzeug sind derzeit insbesondere folgende Komponenten relevant:

```
Siemens S7-1511-1 PN
Raspberry Pi 5
Victron-System
Cerbo GX
Victron MultiPlus
24-V-Lithium-Batteriesystem
Digitale SPS-Eingänge
Digitale SPS-Ausgänge
Analoge SPS-Eingänge
Sensorik
Aktoren
Netzwerk
Hauptbediengerät
```

Weitere Komponenten können später ergänzt werden.

⸻

## 3. Aufgabenverteilung

Die Aufgaben werden grundsätzlich auf drei Ebenen verteilt:

```
        KEHLER OS
   Benutzer & Intelligenz
            │
            ▼
      Raspberry Pi
   Software & Integration
            │
            ▼
       Siemens SPS
    Echtzeit & Hardware
            │
            ▼
    Sensoren / Aktoren
```

Victron bildet parallel dazu ein eigenständiges Energiesystem, das mit Kehler OS integriert wird.

⸻

## 4. Siemens S7-1511-1 PN

Die Siemens S7-1511-1 PN ist die zentrale SPS des Aufbaus.

Sie ist für robuste und deterministische Steuerungsaufgaben vorgesehen.

Die SPS ist kein Ersatz für Kehler OS.

Kehler OS ist wiederum kein Ersatz für die SPS.

Beide Systeme besitzen unterschiedliche Verantwortlichkeiten.

⸻

## 5. Aufgaben der SPS

Die SPS soll insbesondere dort eingesetzt werden, wo direkte Hardwaresteuerung erforderlich ist.

Beispiele:

* digitale Eingänge erfassen
* digitale Ausgänge steuern
* analoge Sensorwerte erfassen
* Relais ansteuern
* Pumpen steuern
* Verriegelungen steuern
* Garagentor überwachen und steuern
* Lichtkreise steuern
* Endschalter auswerten
* Zustände überwachen
* sicherheitsrelevante Verriegelungsbedingungen umsetzen
* Nivellierungsfunktionen unterstützen

Die endgültige SPS-Programmlogik wird separat definiert.

⸻

## 6. SPS muss autonom bleiben

Grundlegende SPS-Funktionen dürfen nicht davon abhängig sein, dass Kehler OS erreichbar ist.

Beispiel:

```
Raspberry Pi OFFLINE
        │
        ▼
SPS läuft weiter
        │
        ├── Sensoren
        ├── Ausgänge
        ├── Schutzfunktionen
        └── lokale Steuerlogik
```

Ein Softwareproblem im Raspberry Pi darf die SPS nicht unkontrolliert stoppen.

⸻

## 7. Keine sicherheitskritische Logik ausschließlich im Frontend

Die Benutzeroberfläche darf niemals die einzige Instanz sein, die eine gefährliche Aktion verhindert.

Beispiel:

Wenn eine mechanische Bewegung unter bestimmten Bedingungen verboten ist, darf nicht nur der Button ausgeblendet werden.

Die zuständige Steuerung muss die Aktion selbst ebenfalls verhindern.

Die UI ist keine Sicherheitseinrichtung.

⸻

## 8. SPS-Eingänge

Digitale Eingänge können beispielsweise verwendet werden für:

* Türkontakte
* Fensterkontakte
* Endschalter
* Taster
* Verriegelungsrückmeldungen
* Garagenstatus
* Pumpenrückmeldungen
* weitere binäre Sensoren

Die konkrete Belegung wird später anhand des tatsächlichen Fahrzeugs dokumentiert.

⸻

## 9. SPS-Ausgänge

Digitale Ausgänge können beispielsweise verwendet werden für:

* Relais
* Beleuchtung
* Verriegelungen
* Pumpen
* Ventile
* Signale
* Freigaben
* weitere Aktoren

Die Software darf keine feste Zuordnung erfinden.

Die tatsächliche I/O-Belegung muss konfiguriert beziehungsweise dokumentiert werden.

⸻

## 10. Analoge Eingänge

Die SPS besitzt beziehungsweise erhält analoge Eingänge.

Diese können beispielsweise Sensorwerte erfassen für:

* Druck
* Füllstand
* Temperatur
* weitere analoge Messgrößen

Für jeden analogen Sensor muss später definiert werden:

```
Sensortyp
Messbereich
elektrischer Bereich
Skalierung
physikalische Einheit
Fehlerbereich
Plausibilitätsbereich
```

⸻

## 11. Skalierung analoger Sensoren

Ein Rohwert darf nicht direkt in der Benutzeroberfläche erscheinen.

Beispielsweise:

```
Analogeingang
      ↓
Rohwert
      ↓
Skalierung
      ↓
physikalischer Wert
      ↓
Plausibilisierung
      ↓
Kehler OS
```

Die UI erhält beispielsweise:

```
Frischwasser
64 %
```

und keinen SPS-Rohwert.

⸻

## 12. Sensorfehler

Ein Sensor muss als fehlerhaft erkannt werden können.

Beispiele:

* Kabelbruch
* Kurzschluss
* Wert außerhalb des Messbereichs
* Kommunikationsausfall
* physikalisch unplausibler Wert

Kehler OS darf einen solchen Zustand nicht als gültigen Messwert darstellen.

⸻

## 13. Sensorqualität

Ein Sensorwert soll logisch mindestens folgende Qualitätszustände unterstützen können:

```
VALID
STALE
UNKNOWN
INVALID
ERROR
```

Dadurch kann die UI beispielsweise unterscheiden:

Frischwasser: 0 %

von:

Frischwasser: Sensor nicht verfügbar

⸻

## 14. Aktoren

Aktoren verändern den physischen Zustand des Fahrzeugs.

Dazu gehören beispielsweise:

* Relais
* Motoren
* Pumpen
* Ventile
* Schlösser
* Garagentor
* Markise
* Stufen

Bei Aktoren ist die Rückmeldung besonders wichtig.

⸻

## 15. Befehl und Zustand

Ein Befehl ist nicht dasselbe wie ein Zustand.

Beispiel:

```
COMMAND:
garage.open
```

bedeutet nicht automatisch:

```
STATE:
garage = OPEN
```

Die Hardware muss die Zustandsänderung bestätigen.

⸻

## 16. Bewegliche Systeme

Bei beweglichen Komponenten sollen Zwischenzustände berücksichtigt werden.

Beispiel:

```
CLOSED
↓
OPENING
↓
OPEN
```

oder:

```
OPEN
↓
CLOSING
↓
CLOSED
```

Zusätzlich können auftreten:

```
STOPPED
BLOCKED
ERROR
UNKNOWN
```

⸻

## 17. Endschalter

Wo mechanisch sinnvoll, sollen Endzustände durch geeignete Sensorik beziehungsweise Endschalter bestätigt werden.

Software darf einen mechanischen Endzustand nicht allein aufgrund einer abgelaufenen Zeit annehmen, wenn eine tatsächliche Rückmeldung verfügbar ist.

⸻

## 18. Raspberry Pi 5

Der Raspberry Pi 5 bildet die zentrale Softwareplattform von Kehler OS.

Er übernimmt keine harte Echtzeitsteuerung.

Seine Aufgaben liegen insbesondere bei:

* Backend
* API
* Hardwareintegration
* Datenhaltung
* Ereignisverarbeitung
* Automatisierung
* Benutzerverwaltung
* Diagnose
* Weboberfläche
* Kommunikation
* Systemmanagement

⸻

## 19. Raspberry Pi als Gateway

Der Raspberry Pi bildet die Brücke zwischen der industriellen Fahrzeugtechnik und der Benutzeroberfläche.

Konzeptionell:

```
SPS ──────┐
          │
Victron ──┼──► Raspberry Pi ──► Kehler OS
          │
weitere ──┘
Geräte
```

⸻

## 20. Raspberry Pi darf kein Single Point of Unsafe Failure sein

Der Raspberry Pi ist für Kehler OS sehr wichtig.

Sein Ausfall darf aber keinen gefährlichen Hardwarezustand erzeugen.

Bei einem Ausfall müssen Aktoren in einem definierten beziehungsweise durch die jeweilige Steuerung kontrollierten Zustand bleiben.

⸻

## 21. Raspberry-Pi-Überwachung

Kehler OS soll den eigenen Rechner überwachen können.

Relevante Informationen können sein:

* CPU-Auslastung
* RAM-Auslastung
* Datenträgerbelegung
* CPU-Temperatur
* Netzwerkstatus
* Laufzeit
* Dienststatus
* Fehler
* Neustarts

⸻

## 22. Temperatur des Raspberry Pi

Da der Rechner in einem Fahrzeug betrieben wird, ist die thermische Situation relevant.

Eine zu hohe Systemtemperatur soll erkannt werden können.

Der Administrator soll diesen Zustand in der Diagnose sehen können.

⸻

## 23. Datenträger

Die Systemarchitektur muss berücksichtigen, dass dauerhafte Schreibvorgänge Datenträger belasten können.

Logging und historische Daten dürfen deshalb nicht unkontrolliert ständig auf einen ungeeigneten Datenträger geschrieben werden.

Die endgültige Speicherlösung wird später technisch festgelegt.

⸻

## 24. Kontrolliertes Herunterfahren

Wenn technisch möglich, soll ein kontrolliertes Herunterfahren des Raspberry Pi vorgesehen werden.

Ein plötzliches Abschalten der Stromversorgung soll möglichst vermieden werden.

Eine geeignete Stromversorgung beziehungsweise Pufferung kann hierfür eingesetzt werden.

⸻

## 25. Automatischer Start

Nach Wiederkehr der Versorgung soll Kehler OS automatisch starten können.

Der Benutzer soll nicht jedes Mal:

* einen Desktop öffnen
* Programme manuell starten
* Terminalbefehle ausführen

müssen.

⸻

## 26. Boot-Verhalten

Der gewünschte Ablauf ist:

```
Stromversorgung vorhanden
↓
Raspberry Pi startet
↓
Betriebssystem startet
↓
Kehler-OS-Dienste starten
↓
Hardwareverbindungen werden aufgebaut
↓
Systemzustände werden synchronisiert
↓
Kehler OS betriebsbereit
```

⸻

## 27. Unvollständiger Systemstart

Nicht alle Komponenten müssen beim Start sofort verfügbar sein.

Beispiel:

```
Raspberry Pi: ONLINE
SPS: INITIALIZING
Victron: ONLINE
Kamera 1: OFFLINE
```

Kehler OS muss auch mit einem teilweise verfügbaren System starten können.

⸻

## 28. Victron

Das Victron-System bleibt ein eigenständiges Energiemanagementsystem.

Kehler OS integriert seine Daten und gegebenenfalls freigegebene Steuerungsmöglichkeiten.

Kehler OS soll Victron nicht unnötig ersetzen oder grundlegende Schutzmechanismen umgehen.

⸻

## 29. Bekannte Victron-Komponenten

Im Fahrzeug sind beziehungsweise waren im Projekt insbesondere relevant:

* Victron-Batteriesystem
* 24-V-System
* MultiPlus
* Cerbo GX
* Solar-/Ladeinfrastruktur

Die exakte Konfiguration muss vor der finalen Implementierung überprüft werden.

Es dürfen keine nicht bestätigten Geräte erfunden werden.

⸻

## 30. Cerbo GX

Der Cerbo GX kann eine wichtige Integrationsschnittstelle zwischen Victron und Kehler OS bilden.

Die tatsächlich verfügbare und technisch sinnvollste Schnittstelle muss vor der Implementierung geprüft werden.

Kehler OS soll möglichst über dokumentierte und stabile Schnittstellen auf Victron-Daten zugreifen.

⸻

## 31. Victron-Daten

Relevante Daten können beispielsweise umfassen:

```
Batterie-SOC
Batteriespannung
Batteriestrom
Leistung
Lade-/Entladezustand
Solarleistung
Landstrom
Wechselrichterstatus
Ladegerätstatus
Alarme
```

Nur tatsächlich verfügbare Daten dürfen später als reale Messwerte dargestellt werden.

⸻

## 32. Victron-Steuerung

Nicht jeder Victron-Datenpunkt muss durch Kehler OS veränderbar sein.

Es muss klar zwischen:

READ

und:

WRITE / CONTROL

unterschieden werden.

Steuerungsmöglichkeiten dürfen nur implementiert werden, wenn sie technisch vorgesehen und sicher sind.

⸻

## 33. Victron bleibt Schutzinstanz

Batterie- und Wechselrichterschutzfunktionen sollen weiterhin durch die dafür vorgesehenen Victron-/BMS-Komponenten ausgeführt werden.

Kehler OS kann:

* überwachen
* visualisieren
* warnen
* analysieren
* übergeordnete Automatisierungen auslösen

Es darf grundlegende Schutzmechanismen nicht ersetzen.

⸻

## 34. Tanks

Das Fahrzeug besitzt drei relevante Tanks:

```
Frischwasser
Grauwasser
Schwarzwasser
```

Kehler OS muss alle drei separat behandeln.

⸻

## 35. Tankkonfiguration

Für jeden Tank sollen später konfigurierbar sein:

* Name
* Typ
* Kapazität
* Sensor
* Messbereich
* Warnschwellen
* kritische Schwellen
* Einheit

Dadurch darf die Software nicht auf fest einprogrammierte Tankgrößen angewiesen sein.

⸻

## 36. Tankmessung

Die Rohmessung muss in einen verständlichen Füllstand umgerechnet werden.

Beispiel:

```
Sensor
↓
Rohwert
↓
Kalibrierung
↓
Liter
↓
Prozent
↓
Kehler OS
```

⸻

## 37. Tankkalibrierung

Ein Tank ist nicht zwangsläufig geometrisch linear.

Wenn notwendig, muss eine Kalibrierung mehrere Messpunkte unterstützen können.

Beispiel:

```
Sensorwert A → 0 L
Sensorwert B → 100 L
Sensorwert C → 200 L
...
```

Damit kann auch ein unregelmäßig geformter Tank genauer dargestellt werden.

⸻

## 38. Nivellierung

Das Fahrzeug besitzt vier hydraulische Zylinder für die Nivellierung.

Kehler OS soll dieses System später überwachen und bedienen können.

Die sicherheitskritische Bewegungslogik gehört jedoch nicht ausschließlich in die Benutzeroberfläche.

⸻

## 39. Neigungssensorik

Für die Nivellierung ist eine Sensorik zur Erfassung der Fahrzeuglage vorgesehen.

Das System muss mindestens:

* Längsneigung
* Querneigung

zuverlässig bestimmen können.

Die endgültige Sensorhardware und Messarchitektur müssen vor Implementierung bestätigt werden.

⸻

## 40. Mehrere Neigungsmesspunkte

Das System soll so vorbereitet sein, dass mehrere Messpunkte beziehungsweise Sensoren verwendet werden können.

Die Sensordaten können zur:

* Plausibilisierung
* Diagnose
* Nivellierung

genutzt werden.

Die genaue mathematische Auswertung wird später anhand der realen Sensorinstallation festgelegt.

⸻

## 41. Hydraulikbewegungen

Hydraulische Bewegungen müssen kontrolliert erfolgen.

Zu berücksichtigen sind unter anderem:

* Endzustände
* maximale Bewegungsbereiche
* Sensorfehler
* Not-Stopp
* unzulässige Kombinationen
* Zeitüberschreitungen
* Druck beziehungsweise weitere relevante Rückmeldungen, sofern vorhanden

⸻

## 42. Nivellierungs-UI

Die UI darf beispielsweise anzeigen:

```
Längs: +0,8°
Quer: -1,2°
```

und den Fahrzeugzustand visualisieren.

Die tatsächliche Regelung muss jedoch auf einer dafür geeigneten Steuerungsebene stattfinden.

⸻

## 43. Drucksensorik

Druckwerte können für technische Systeme relevant sein.

Wenn Drucksensoren integriert werden, muss für jeden Sensor definiert werden:

* Medium
* Messbereich
* elektrisches Signal
* Anschluss
* Skalierung
* Einheit
* Warnbereich
* Fehlerbereich

⸻

## 44. Temperatur

Temperatursensoren können in mehreren Bereichen vorhanden sein.

Beispiele:

* Wohnbereich
* Schlafzimmer
* Bad
* Technikraum
* Außenbereich
* Batteriesystem

Die Anzahl der Sensoren darf nicht fest in der Software begrenzt sein.

⸻

## 45. Tür- und Fensterkontakte

Kehler OS soll Zustände von Türen und Fenstern erfassen können.

Die Sensoren liefern beispielsweise:

```
OPEN
CLOSED
```

Zusätzlich muss Kehler OS mit:

```
UNKNOWN
ERROR
```

umgehen können.

⸻

## 46. Zentralverriegelung

Die Zentralverriegelung soll über Kehler OS integrierbar sein.

Die tatsächliche Verriegelungslogik soll jedoch Rückmeldungen berücksichtigen.

Ein gesendeter Verriegelungsbefehl bedeutet nicht automatisch, dass tatsächlich alle Schlösser verriegelt sind.

⸻

## 47. Schrankverriegelungen

Kehler OS soll auch Verriegelungen von Schränken beziehungsweise dafür vorgesehenen Aufbauelementen integrieren können.

Diese sollen logisch gruppiert werden können.

Beispielsweise:

```
Alle Schränke
VERRIEGELT
```

oder:

```
Schrank 4
NICHT VERRIEGELT
```

sofern entsprechende Rückmeldungen vorhanden sind.

⸻

## 48. Garagentor

Das Garagentor ist ein wichtiger Aktor.

Kehler OS soll mindestens folgende logische Zustände unterstützen:

```
CLOSED
OPENING
OPEN
CLOSING
STOPPED
ERROR
UNKNOWN
```

Die tatsächlichen verfügbaren Zustände hängen von der Sensorik ab.

⸻

## 49. Licht

Die Lichtsteuerung wird über die dafür vorgesehenen Steuerungskomponenten integriert.

Kehler OS soll Lichtkreise logisch benennen und gruppieren.

Die UI arbeitet mit:

```
Wohnzimmer
Küche
Bad
Außen
Garage
```

und nicht mit SPS-Ausgangsnummern.

⸻

## 50. Keine RGB-Annahme

Für das aktuelle Fahrzeug darf nicht automatisch von RGB-Beleuchtung ausgegangen werden.

Die Softwarearchitektur kann zukünftige Lichttypen unterstützen.

Die UI darf aber nur Funktionen anzeigen, die tatsächlich vorhanden sind.

⸻

## 51. Kameras

Kameras sind als zukünftige beziehungsweise erweiterbare Funktion vorgesehen.

Die Architektur muss vorbereitet sein.

Es darf jedoch nicht davon ausgegangen werden, dass bereits alle Kameras installiert und verfügbar sind.

⸻

## 52. Keine Dachluken-Annahme

Die aktuelle Fahrzeugkonfiguration besitzt keine als Kehler-OS-Funktion bestätigten Dachluken.

Daher dürfen Dachluken nicht ohne spätere Bestätigung als vorhandene steuerbare Funktion behandelt werden.

⸻

## 53. Keine Alarmanlagen-Annahme

Eine dedizierte Alarmanlage ist aktuell nicht als vorhandene Hardware bestätigt.

Sicherheitsfunktionen von Kehler OS dürfen deshalb nicht automatisch eine physische Alarmanlage voraussetzen.

⸻

## 54. Keine Satellitenanlagen-Annahme

Eine Satellitenanlage ist aktuell nicht Bestandteil der bestätigten Hardware.

Kehler OS darf sie nicht als vorhandene Funktion darstellen.

⸻

## 55. Capability-basiertes System

Die Benutzeroberfläche soll sich langfristig nach den tatsächlich vorhandenen Fähigkeiten richten.

Beispiel:

Gerät A:

```
ON/OFF
```

Gerät B:

```
ON/OFF
DIMMING
```

Dann darf nur Gerät B eine Dimmersteuerung anzeigen.

⸻

## 56. Hardware Registry

Kehler OS soll konzeptionell eine zentrale Kenntnis über die vorhandene Hardware besitzen.

Für jedes Gerät können Informationen existieren wie:

```
ID
Name
Kategorie
Hersteller
Modell
Verbindung
Status
Capabilities
Firmware
Konfiguration
```

Die konkrete Implementierung wird später festgelegt.

⸻

## 57. Hardware-Mapping

Die Verbindung zwischen logischem Gerät und physischer Hardware muss eindeutig dokumentiert werden.

Beispiel:

```
Logisch:
garage.door.open
Hardware:
SPS
→ definierter Datenpunkt
```

Dieses Mapping darf nicht über die gesamte Codebasis verteilt sein.

⸻

## 58. Zentrale Konfiguration

Hardwarezuordnungen sollen möglichst zentral verwaltet werden.

Wenn beispielsweise ein Sensor auf einen anderen SPS-Eingang umgeklemmt wird, soll nicht an zehn verschiedenen Stellen Programmcode geändert werden müssen.

⸻

## 59. Simulation

Für die Entwicklung soll später geprüft werden, ob Hardware simuliert werden kann.

Das wäre besonders hilfreich, wenn Claude beziehungsweise Entwickler Kehler OS programmieren, ohne permanent Zugriff auf das reale Wohnmobil zu besitzen.

Eine Simulation könnte beispielsweise Zustände erzeugen wie:

```
Batterie 73 %
Frischwasser 61 %
Garage CLOSED
SPS ONLINE
Außentemperatur 22 °C
```

⸻

## 60. Simulation darf nicht mit realer Hardware verwechselt werden

Das System muss eindeutig erkennen, ob es mit:

REAL HARDWARE

oder:

SIMULATION

arbeitet.

Eine Simulation darf niemals versehentlich als echte Fahrzeugsteuerung dargestellt werden.

⸻

## 61. Entwicklungsmodus

Ein separater Entwicklungsmodus kann vorgesehen werden.

Dieser darf zusätzliche Informationen anzeigen wie:

* Rohwerte
* Datenpunktnamen
* Kommunikationsstatus
* Timing
* Fehler
* Hardware-Mapping

Diese Informationen gehören nicht in die normale Benutzeroberfläche.

⸻

## 62. Service-Modus

Zusätzlich kann später ein Servicebereich sinnvoll sein.

Dieser könnte beispielsweise ermöglichen:

* einzelne Sensoren prüfen
* Ausgänge testen
* Kommunikationsstatus prüfen
* Kalibrierungen durchführen
* Diagnoseinformationen anzeigen

Servicefunktionen müssen vor unbeabsichtigter Bedienung geschützt werden.

⸻

## 63. Sicherheitsprinzip

Kehler OS darf niemals eine physische Aktion allein deshalb durchführen, weil die Benutzeroberfläche sie angefordert hat.

Der vollständige Ablauf lautet konzeptionell:

```
Benutzer
↓
UI
↓
Berechtigungsprüfung
↓
Systemlogik
↓
Sicherheitsbedingungen
↓
Hardwarebefehl
↓
Steuerung
↓
Aktuator
↓
Rückmeldung
↓
Systemzustand
↓
UI
```

⸻

## 64. Hardware-Watchdog

Für wichtige Komponenten soll geprüft werden, ob Watchdog-Mechanismen sinnvoll sind.

Beispielsweise kann erkannt werden, wenn:

* ein Dienst hängt
* eine Kommunikation ausfällt
* ein Gerät keine Daten mehr liefert

Die konkrete Watchdog-Architektur wird später festgelegt.

⸻

## 65. Heartbeats

Bei Netzwerkgeräten können Heartbeats beziehungsweise regelmäßige Lebenszeichen sinnvoll sein.

Dadurch kann Kehler OS unterscheiden:

Gerät liefert gerade keinen neuen Messwert

von:

Gerät ist vollständig offline

⸻

## 66. Boot-Synchronisation

Nach einem Neustart muss Kehler OS die tatsächlichen Hardwarezustände neu einlesen.

Es darf nicht einfach alte Zustände aus der Datenbank übernehmen.

Beispiel:

```
Vor Neustart:
Garage CLOSED
Nach Neustart:
nicht automatisch CLOSED annehmen
↓
Hardware abfragen
↓
tatsächlicher Zustand
```

⸻

## 67. Hardware ist Quelle der Wahrheit

Bei physischen Zuständen ist grundsätzlich die tatsächliche Hardware beziehungsweise deren zuverlässige Rückmeldung die maßgebliche Quelle.

Die Datenbank ist kein Ersatz für den aktuellen Hardwarezustand.

⸻

## 68. Konfigurationsfehler

Kehler OS muss erkennen können, wenn eine Hardwarekonfiguration unvollständig oder widersprüchlich ist.

Beispiel:

```
Garagentor konfiguriert
aber
kein Kommunikationsdatenpunkt vorhanden
```

Dies muss als Konfigurationsproblem behandelt werden.

⸻

## 69. Unbekannte Hardware

Wenn Kehler OS ein nicht vollständig unterstütztes Gerät erkennt, darf es keine Funktionen erfinden.

Das Gerät kann beispielsweise als:

UNSUPPORTED

oder:

NOT CONFIGURED

behandelt werden.

⸻

## 70. Dokumentation

Für jede integrierte Hardwarekomponente soll später dokumentiert werden:

* Hersteller
* Modell
* Aufgabe
* Stromversorgung
* Schnittstelle
* Kommunikationsprotokoll
* Datenpunkte
* Schreibrechte
* Fehlerverhalten
* Sicherheitsrelevanz
* Abhängigkeiten

⸻

## 71. Austauschbarkeit

Hardware soll soweit technisch sinnvoll austauschbar bleiben.

Beispiel:

Wenn ein Temperatursensor ersetzt wird, soll das Klima-Modul nicht komplett neu programmiert werden müssen.

Die Abstraktionsschicht übernimmt diese Entkopplung.

⸻

## 72. Erweiterbarkeit

Die Hardwarearchitektur muss spätere Erweiterungen erlauben.

Beispiele:

* zusätzliche Sensoren
* neue Kameras
* weitere SPS-I/O-Module
* Wetterstation
* weitere Energiekomponenten
* neue Aktoren
* zusätzliche Displays
* weitere Netzwerkgeräte

⸻

## 73. Keine künstlichen Begrenzungen

Kehler OS soll nicht unnötig fest programmieren:

```
genau 3 Temperatursensoren
genau 4 Kameras
genau 10 Lampen
```

Wo sinnvoll, sollen Geräte konfigurations- beziehungsweise capability-basiert verwaltet werden.

⸻

## 74. Performance

Hardwarekommunikation muss effizient sein.

Nicht jeder Sensor benötigt dieselbe Abfragerate.

Beispiel:

```
Nivellierung
→ hohe Aktualisierungsrate
Tankfüllstand
→ deutlich niedrigere Aktualisierungsrate ausreichend
```

Die Aktualisierungsraten müssen dem jeweiligen Anwendungsfall entsprechen.

⸻

## 75. Prioritäten

Bei Hardwareintegration gilt folgende Priorität:

1. Sicherheit
2. Zuverlässigkeit
3. korrekter tatsächlicher Zustand
4. Fehlertoleranz
5. Wartbarkeit
6. Performance
7. Benutzerkomfort

Eine schöne Animation darf niemals wichtiger sein als eine korrekte Hardware-Rückmeldung.

⸻

## 76. Zielbild

Kehler OS soll sämtliche Hardware abstrahieren.

Für den Benutzer sieht es beispielsweise so aus:

```
Frischwasser
64 %
Batterie
87 %
Garage
GESCHLOSSEN
Außenlicht
EIN
```

Im Hintergrund kann dagegen eine komplexe Infrastruktur arbeiten:

```
Sensor
↓
SPS
↓
Ethernet
↓
Hardware Adapter
↓
Backend
↓
State Management
↓
Realtime API
↓
UI
```

Diese Komplexität soll für den normalen Benutzer unsichtbar bleiben.

⸻

## 77. Grundsatz für Claude

Wenn die spätere Entwicklung beginnt und eine konkrete Hardwareinformation fehlt, darf Claude keine Hardwaredetails erfinden.

Stattdessen muss die entsprechende Stelle:

* konfigurierbar
* abstrahiert
* dokumentiert

werden.

Falls für eine reale Integration zwingend eine Information benötigt wird, muss Claude diese als offene Hardwareanforderung kennzeichnen.

⸻

## 78. Ziel dieses Kapitels

Kehler OS soll nicht nur auf einem Bildschirm gut aussehen.

Es soll tatsächlich mit einem realen LKW-Wohnmobil zuverlässig funktionieren.

Deshalb müssen Software und Hardware von Anfang an als zusammenhängendes technisches System betrachtet werden.

Die industrielle SPS bleibt für ihre geeigneten Steuerungsaufgaben verantwortlich.

Victron bleibt für das Energiesystem und dessen Schutzmechanismen verantwortlich.

Der Raspberry Pi verbindet diese Systeme mit der intelligenten Kehler-OS-Softwareplattform.

⸻

## Ende Kapitel 12

Dieses Kapitel definiert die Hardwareintegration von Kehler OS.

Besonders festgelegt wurden:

* Siemens S7-1511-1 PN als SPS
* Raspberry Pi 5 als zentrale Softwareplattform
* Integration des Victron-Systems
* klare Trennung zwischen SPS und Kehler OS
* Hardwareabstraktion
* Sensor- und Aktorzustände
* Rückmeldungen statt angenommener Zustände
* drei Tanks
* hydraulische Nivellierung mit vier Zylindern
* Zentral- und Schrankverriegelungen
* Garagentor
* Lichtsteuerung
* capability-basierte Hardware
* Simulation und Entwicklungsmodus
* Boot-Synchronisation
* Fehlertoleranz
* Erweiterbarkeit

Nicht bestätigte Hardware darf nicht erfunden werden.

Insbesondere dürfen derzeit nicht automatisch vorausgesetzt werden:

* RGB-Beleuchtung
* Dachlukensteuerung
* physische Alarmanlage
* Satellitenanlage
* bereits installierte vollständige Kameraausstattung

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf Kapitel 13.

Verwende Kapitel 1 bis 12 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
