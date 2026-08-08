# KEHLER OS

# Kapitel 18 – Finaler Entwicklungsauftrag an Claude

AB JETZT ÄNDERT SICH DER MODUS

Du hast die Kapitel 1 bis 17 erhalten.

Diese Kapitel bilden gemeinsam die vollständige Projektspezifikation von Kehler OS.

Bis hierhin solltest du ausschließlich Wissen aufnehmen.

Ab diesem Kapitel bist du mit der Entwicklung beauftragt.

Du darfst jetzt:

* Architekturentscheidungen treffen
* Technologien auswählen
* Projektstruktur erstellen
* Code schreiben
* Dateien anlegen
* Entwicklungsphasen planen
* Tests erstellen
* Simulationen aufbauen
* Dokumentation erzeugen

Dabei gelten sämtliche Anforderungen aus Kapitel 1 bis 17 weiterhin verbindlich.

⸻

## 1. Oberstes Ziel

Entwickle Kehler OS als professionelle, lokale und modulare Fahrzeugplattform für ein LKW-Wohnmobil.

Das System soll:

* stabil
* schnell
* hochwertig
* offlinefähig
* hardwareabstrahiert
* sicher
* erweiterbar
* wartbar

sein.

Es soll nicht wie ein Hobbyprojekt wirken.

⸻

## 2. Alle bisherigen Kapitel sind verbindlich

Kapitel 1 bis 17 müssen vollständig berücksichtigt werden.

Keine Anforderung darf stillschweigend ignoriert werden.

Wenn zwei Anforderungen scheinbar widersprüchlich sind, sollst du sie zuerst gegeneinander abwägen.

Priorität haben dabei grundsätzlich:

1. Sicherheit
2. Zuverlässigkeit
3. korrekter Hardwarezustand
4. Wartbarkeit
5. Benutzerfreundlichkeit
6. Performance
7. Erweiterbarkeit
8. visuelle Effekte

⸻

## 3. Keine blinde Umsetzung

Du sollst die Spezifikation nicht mechanisch in Code übersetzen.

Vor der Implementierung musst du:

* die Gesamtarchitektur analysieren
* Abhängigkeiten erkennen
* Risiken identifizieren
* geeignete Technologien auswählen
* Datenflüsse definieren
* Verantwortlichkeiten sauber trennen

⸻

## 4. Keine unnötige Komplexität

Kehler OS läuft auf einem Raspberry Pi 5.

Die Architektur muss professionell sein, aber zum realen System passen.

Vermeide unnötig:

* Kubernetes
* große Cloud-Plattformen
* komplexe Microservice-Landschaften
* externe Infrastruktur ohne echten Mehrwert
* überdimensionierte Enterprise-Komponenten

⸻

## 5. Bevorzugte Architektur

Die Software soll grundsätzlich modular aufgebaut sein.

Eine geeignete Architektur kann beispielsweise ein modularer Backend-Kern mit klar getrennten Komponenten sein.

Du darfst selbst entscheiden, ob bestimmte Teile in:

* einem Prozess
* mehreren Prozessen
* separaten Diensten

laufen.

Die Entscheidung muss begründet sein.

⸻

## 6. Frontend und Backend müssen getrennt sein

Die Benutzeroberfläche darf keine direkte Hardwarekommunikation enthalten.

Das Prinzip lautet:

```
Frontend
↓
API / Realtime
↓
Backend
↓
Command / State Layer
↓
Hardware Adapter
↓
SPS / Victron / andere Geräte
```

⸻

## 7. Zentraler State

Kehler OS benötigt eine zentrale Zustandsverwaltung.

Alle Clients müssen denselben tatsächlichen Fahrzeugzustand verwenden.

Verhindere mehrere konkurrierende Wahrheiten.

⸻

## 8. Hardwareabstraktion

Hardwaredetails dürfen nicht durch die gesamte Software verteilt sein.

Beispiel:

Nicht:

```
DB10.DBX4.2
```

im Frontend.

Sondern:

```
garage.door.state
```

oder ein vergleichbares semantisches Datenmodell.

⸻

## 9. Hardware Adapter

Baue klare Adapter für externe Systeme.

Mindestens muss die Architektur vorbereitet sein für:

```
Siemens SPS
Victron
Kameras
weitere zukünftige Geräte
```

Ein Adapter soll nur für die Kommunikation mit seinem jeweiligen System verantwortlich sein.

⸻

## 10. Siemens SPS

Die bekannte SPS ist:

Siemens S7-1511-1 PN

Die tatsächliche Kommunikationsmethode muss anhand der realen SPS-Konfiguration und der verfügbaren Schnittstellen gewählt werden.

Erfinde keine SPS-Adressen.

⸻

## 11. SPS-Mapping

Wenn konkrete Datenpunkte noch nicht bekannt sind, erstelle:

* abstrahierte Konfiguration
* Beispiel-Mapping
* klare Platzhalter
* Dokumentation

aber keine erfundenen produktiven Adressen.

⸻

## 12. Victron

Das bekannte Energiesystem enthält insbesondere:

* Victron-System
* Cerbo GX
* MultiPlus
* 24-V-Batteriesystem

Wähle für die Integration eine stabile, lokal verfügbare und dokumentierte Schnittstelle.

Victron bleibt Schutz- und Energiemanagementinstanz.

⸻

## 13. Raspberry Pi 5

Der Raspberry Pi 5 bildet die zentrale Softwareplattform.

Optimiere die Architektur auf:

* begrenzte Ressourcen
* Dauerbetrieb
* geringen Wartungsaufwand
* robuste Speicherung
* kontrollierte Prozesse

⸻

## 14. Designreferenz

Das in den vorherigen Kapiteln beschriebene und bereitgestellte Dashboard-Design ist eine verbindliche visuelle Referenz.

Die Designrichtung umfasst:

* dunkle Oberfläche
* Cyan als Hauptakzent
* hochwertige technische Optik
* dezente Glows
* dunkle Panels
* klare Statusfarben
* feine Rahmen
* moderne Typografie
* hochwertige Animationen
* Premium-Fahrzeug-HMI-Gefühl

⸻

## 15. Kein einfaches Admin-Dashboard

Das Frontend darf nicht wie:

* Bootstrap Admin
* Home Assistant
* Grafana
* klassische SPS-Visualisierung
* einfache Webseite

wirken.

Es muss eine eigenständige Kehler-OS-Identität besitzen.

⸻

## 16. Fahrzeugdarstellung

Das Fahrzeug ist ein zentrales visuelles Element.

Es soll Zustände animiert darstellen können.

Beispiele:

* Garage
* Türen
* Stufen
* Markise
* Nivellierung

Die Fahrzeugdarstellung ist primär Statusvisualisierung und nicht die zentrale Bedienfläche.

⸻

## 17. Designfreiheit

Du erhältst bewusst Designfreiheit für die einzelnen Unterseiten.

Du sollst selbst hochwertige Layouts entwickeln für:

* Licht
* Energie
* Wasser
* Klima
* Nivellierung
* Fahrzeug
* Kameras
* Garage
* Einstellungen
* Diagnose
* Automatisierungen

Diese müssen jedoch eindeutig zum selben Designsystem gehören.

⸻

## 18. Unterseiten nicht kopieren

Nicht jede Seite muss dieselbe Struktur wie das Dashboard besitzen.

Die Informationsarchitektur darf an die jeweilige Funktion angepasst werden.

⸻

## 19. Hauptdisplay

Das Hauptdisplay beziehungsweise primäre Bediengerät hat Priorität.

Weitere Geräte wie:

* Smartphone
* Tablet
* Laptop

sollen unterstützt werden, sind aber sekundär.

⸻

## 20. Responsive Design

Kleinere Geräte dürfen andere Layouts verwenden.

Nicht einfach das Desktop-/HMI-Layout proportional verkleinern.

⸻

## 21. Bottom Navigation

Die endgültige Verwendung einer zusätzlichen Bottom Navigation wurde bewusst noch nicht festgelegt.

Behandle sie nicht als verbindliche Hauptnavigation.

Die endgültige Entscheidung soll später anhand des tatsächlichen UI-Konzepts getroffen werden.

⸻

## 22. Dashboard

Das Dashboard muss mindestens einen schnellen Überblick ermöglichen über:

* Fahrzeug
* Warnungen
* Energie
* Wasser
* Klima
* Nivellierung
* wichtige Schnellzugriffe
* Systemstatus

⸻

## 23. Dynamisches Dashboard

Das Dashboard darf relevante Informationen abhängig vom Zustand stärker hervorheben.

Beispiel:

```
Batterie kritisch
→ Energieinformation erhält höhere Priorität
```

Das Layout soll dennoch stabil bleiben.

⸻

## 24. Licht

Das Lichtsystem muss:

* logische Lichtkreise
* Gruppen
* Ein/Aus
* gegebenenfalls Dimmen
* Szenen

unterstützen können.

Die tatsächliche Hardware bestimmt die Capabilities.

⸻

## 25. Keine RGB-Annahme

Die aktuelle Konfiguration besitzt keine bestätigte RGB-Beleuchtung.

Baue keine sichtbaren RGB-Funktionen ein, solange diese nicht konfiguriert sind.

⸻

## 26. Wasser

Mindestens drei Tanks:

```
Frischwasser
Grauwasser
Schwarzwasser
```

Die Architektur darf jedoch nicht auf exakt drei Tanks fest beschränkt sein.

⸻

## 27. Tankdarstellung

Unterstütze:

* Prozent
* reale Menge
* Warnschwellen
* Historie
* Kalibrierung

⸻

## 28. Energie

Das Energiemodul soll Daten sinnvoll zusammenführen.

Beispiele:

* Batterie
* Solar
* Landstrom
* Wechselrichter
* Ladezustand
* Strom
* Spannung
* Leistung
* Historie

⸻

## 29. Klima

Unterstütze mehrere Zonen und die Trennung von:

```
IST
SOLL
```

Die Regelungslogik soll vorhandene Hardwareintelligenz sinnvoll verwenden und nicht unnötig ersetzen.

⸻

## 30. Nivellierung

Das Fahrzeug besitzt vier hydraulische Zylinder.

Die UI soll die Nivellierung hochwertig visualisieren.

Die eigentliche Echtzeit- und Sicherheitslogik gehört auf die dafür geeignete Steuerungsebene.

⸻

## 31. Verriegelungen

Kehler OS soll unterstützen können:

* Zentralverriegelung
* einzelne Verriegelungen
* Schrankverriegelungen

Der tatsächliche Rückmeldezustand ist entscheidend.

⸻

## 32. Garage

Unterstütze mindestens logisch:

```
CLOSED
OPENING
OPEN
CLOSING
STOPPED
ERROR
UNKNOWN
```

nur soweit diese Zustände tatsächlich aus der Hardware ableitbar sind.

⸻

## 33. Kameras

Die Kameraarchitektur soll erweiterbar sein.

Aktuell dürfen keine bereits installierten Kameras erfunden werden.

Kamera-Funktionen sollen capability-basiert erscheinen.

⸻

## 34. Nicht bestätigte Hardware

Nimm insbesondere nicht automatisch an, dass vorhanden sind:

* RGB-Beleuchtung
* Dachlukensteuerung
* physische Alarmanlage
* Satellitenanlage
* vollständige Kameraausstattung

⸻

## 35. Commands

Trenne strikt:

COMMAND

von:

STATE

Beispiel:

```
Command:
garage.open
```

ist nicht dasselbe wie:

```
State:
garage = OPEN
```

⸻

## 36. Command Lifecycle

Entwickle eine saubere Befehlsverarbeitung.

Geeignete Phasen können sein:

```
REQUESTED
VALIDATING
SENT
ACKNOWLEDGED
COMPLETED
FAILED
TIMEOUT
REJECTED
```

Passe dies sinnvoll an die tatsächliche Architektur an.

⸻

## 37. Hardwarefeedback

Die UI darf einen Befehl nicht als ausgeführt darstellen, bevor der tatsächliche Zustand bestätigt wurde.

⸻

## 38. UNKNOWN

UNKNOWN ist ein echter Zustand.

Er darf niemals pauschal zu:

```
0
OFF
CLOSED
```

umgewandelt werden.

⸻

## 39. Datenqualität

Messwerte müssen Qualität besitzen können.

Mindestens konzeptionell:

```
VALID
STALE
UNKNOWN
INVALID
ERROR
```

⸻

## 40. Realtime

Statusänderungen sollen zeitnah an alle verbundenen Clients verteilt werden.

Wähle dafür eine geeignete Technologie.

⸻

## 41. Initial Snapshot

Ein neu verbundener Client benötigt zunächst einen konsistenten Snapshot.

Danach erhält er Änderungen.

⸻

## 42. Mehrere Clients

Alle Clients müssen synchron bleiben.

Eine Aktion auf dem Haupt-iPad soll auf anderen Clients korrekt sichtbar werden.

⸻

## 43. Konflikte

Konflikte zwischen gleichzeitigen Befehlen müssen serverseitig gelöst werden.

⸻

## 44. Event-System

Entwickle eine saubere interne Event-Struktur.

Beispiele:

```
garage.opened
battery.state.changed
shore_power.connected
system.warning
```

Die tatsächliche Namenskonvention soll konsistent sein.

⸻

## 45. Automatisierungsengine

Kehler OS benötigt eine deterministische Automatisierungsengine.

Grundmodell:

```
TRIGGER
CONDITIONS
ACTIONS
```

⸻

## 46. Szenen

Unterstütze Szenen wie:

```
ABFAHRT
ANKUNFT
NACHT
```

als konfigurierbares Konzept.

Die tatsächlichen Aktionen dürfen nicht hart angenommen werden, wenn Hardware fehlt.

⸻

## 47. Abfahrtscheck

Ein hochwertiger Abfahrtscheck ist ein wichtiges zukünftiges Feature.

Er soll reale Rückmeldungen prüfen.

Beispiel:

```
Markise              ✓
Stufen               ✓
Garage               ✓
Fenster              ✓
Schrankverriegelung  ✓
```

Fehlende Daten müssen als UNKNOWN erscheinen.

⸻

## 48. Sicherheitslogik

Sicherheitskritische Regeln dürfen nicht ausschließlich in der UI oder in einer generativen KI liegen.

Deterministische und hardwareabhängige Regeln gehören in die geeignete Steuerungsebene.

⸻

## 49. Benutzer und Rollen

Implementiere eine angemessene Benutzer- und Berechtigungsarchitektur.

Mindestens:

```
ADMIN
USER
```

Die Architektur soll granulare Berechtigungen unterstützen können.

⸻

## 50. Lokaler Komfort

Das feste Hauptbediengerät soll im Alltag komfortabel funktionieren.

Vermeide unnötige Login-Reibung.

Sicherheit muss trotzdem erhalten bleiben.

⸻

## 51. API-Sicherheit

Jede schreibende beziehungsweise kritische API muss serverseitig:

* authentifizieren
* autorisieren
* validieren

⸻

## 52. Keine direkte SPS-Nutzung aus Clients

Clients dürfen niemals direkt zur SPS schreiben.

⸻

## 53. Remote-Zugriff

Baue die Architektur so, dass später sicherer Remote-Zugriff ergänzt werden kann.

Aktiviere jedoch keine unsichere direkte Internetfreigabe.

⸻

## 54. Secrets

Keine Secrets im Quellcode.

Verwende geeignete Konfigurations- und Secret-Mechanismen.

⸻

## 55. Datenbank

Wähle erst jetzt eine geeignete Datenhaltung.

Begründe die Wahl.

Berücksichtige:

* Raspberry Pi
* lokale Nutzung
* Zeitreihendaten
* Konfiguration
* Ereignisse
* Backups
* Migrationen
* geringe Wartung

⸻

## 56. Unterschiedliche Speichertechnologien

Wenn sinnvoll, dürfen unterschiedliche Speichermechanismen für:

* Konfiguration
* Live-State
* Historie

eingesetzt werden.

Übertreibe die Architektur jedoch nicht.

⸻

## 57. Historie

Unterstütze historische Daten für unter anderem:

* Energie
* Tanks
* Temperaturen
* Warnungen
* Commands
* Events

⸻

## 58. Retention

Verhindere unbegrenztes Datenwachstum.

Plane:

* Aggregation
* Retention
* Log Rotation
* Speicherüberwachung

⸻

## 59. Diagnose

Erstelle eine technisch hochwertige Diagnoseebene.

Sie soll unter anderem zeigen können:

* Raspberry Pi
* SPS
* Victron
* Netzwerk
* interne Dienste
* Datenbank
* Sensoren
* Aktoren
* Fehler

⸻

## 60. Normaler Benutzer versus Diagnose

Die normale UI bleibt einfach.

Technische Details gehören in Administrator-/Service-Bereiche.

⸻

## 61. Logging

Verwende strukturierte Logs.

Unterstütze sinnvolle Log-Level.

Vermeide Secrets in Logs.

⸻

## 62. Audit

Wichtige Benutzer- und Systemaktionen sollen nachvollziehbar sein.

⸻

## 63. Simulation

Eine Hardware-Simulation ist verpflichtend für die Entwicklung.

Das Projekt soll auch ohne das reale Wohnmobil lauffähig und testbar sein.

⸻

## 64. Simulationsumfang

Die Simulation soll mindestens typische Zustände bereitstellen können:

```
SPS ONLINE
Batterie 75 %
Frischwasser 60 %
Grauwasser 35 %
Schwarzwasser 20 %
Garage CLOSED
Außenlicht OFF
Temperatur 22 °C
```

⸻

## 65. Fehler simulieren

Die Simulation muss auch Fehler erzeugen können.

Beispiele:

```
SPS OFFLINE
Victron TIMEOUT
Sensor INVALID
Garage BLOCKED
```

⸻

## 66. Simulation eindeutig kennzeichnen

Die UI beziehungsweise Entwicklungsumgebung muss klar zeigen:

SIMULATION

wenn keine reale Hardware verwendet wird.

⸻

## 67. Keine Vermischung von Real und Simulation

Verhindere, dass ein simuliertes Gerät versehentlich einen realen Aktor beeinflusst.

⸻

## 68. Entwicklungsumgebungen

Unterstütze klar getrennte Umgebungen:

```
DEVELOPMENT
SIMULATION
PRODUCTION
```

⸻

## 69. Tests

Erstelle von Anfang an Tests.

Mindestens:

* Unit Tests
* Integration Tests
* State Machine Tests
* Command Tests
* Permission Tests
* Fehlerfalltests

⸻

## 70. UI Tests

Wichtige Benutzerabläufe sollen ebenfalls automatisiert testbar sein, sofern die gewählte Technologie dies vernünftig unterstützt.

⸻

## 71. UNKNOWN testen

Testfälle dürfen nicht nur perfekte Daten verwenden.

Teste gezielt:

* UNKNOWN
* OFFLINE
* TIMEOUT
* INVALID
* ERROR

⸻

## 72. Deployment

Kehler OS muss reproduzierbar installierbar sein.

Dokumentiere die Installation auf dem Raspberry Pi.

⸻

## 73. Autostart

Alle benötigten Dienste sollen beim Systemstart automatisch starten.

⸻

## 74. Kein sichtbarer Linux-Desktop

Der normale Fahrzeugbetrieb soll möglichst direkt Kehler OS zeigen.

⸻

## 75. Bootscreen

Entwickle einen passenden Kehler-OS-Bootscreen beziehungsweise Startzustand.

⸻

## 76. Update-System

Plane ein kontrolliertes Update-System.

Updates sollen:

* überprüfbar
* versioniert
* diagnostizierbar

sein.

⸻

## 77. Rollback

Plane mindestens konzeptionell eine Möglichkeit, auf eine funktionierende Version zurückzukehren, wenn ein Update fehlschlägt.

⸻

## 78. Backup

Erstelle eine klare Backupstrategie für wichtige Daten.

Mindestens:

* Konfiguration
* Benutzer
* Hardware Mapping
* Automatisierungen
* Kalibrierungen

⸻

## 79. Restore

Dokumentiere, wie ein neues Raspberry-Pi-System nach einem Defekt wiederhergestellt werden kann.

⸻

## 80. Hardwarezustand nach Restore

Nach einem Restore müssen reale Hardwarezustände neu synchronisiert werden.

Nie alte Live-Zustände als aktuelle Wahrheit verwenden.

⸻

## 81. Dokumentation

Erstelle während der Entwicklung technische Dokumentation.

Mindestens:

```
README
ARCHITECTURE
INSTALLATION
HARDWARE_INTEGRATION
CONFIGURATION
BACKUP_RESTORE
DEVELOPMENT
```

Die genaue Struktur darf sinnvoll erweitert werden.

⸻

## 82. Architekturentscheidungen

Dokumentiere wichtige Technologieentscheidungen und ihre Gründe.

⸻

## 83. Codequalität

Verwende:

* verständliche Namen
* klare Module
* konsistenten Stil
* Typisierung, sofern die Sprache dies sinnvoll unterstützt
* Validierung
* gute Fehlerbehandlung

⸻

## 84. Keine riesigen Dateien

Vermeide unstrukturierte Dateien mit tausenden Zeilen und vielen unabhängigen Verantwortlichkeiten.

⸻

## 85. Keine künstliche Fragmentierung

Erzeuge gleichzeitig nicht für jede triviale Funktion eine eigene Datei.

⸻

## 86. Technologieauswahl

Wähle jetzt den konkreten Technologie-Stack.

Bewerte dabei mindestens:

### Backend

* Performance auf Raspberry Pi
* Async-I/O
* Hardwarebibliotheken
* Typisierung
* Wartbarkeit

### Frontend

* hochwertiges HMI
* Animationen
* Touch
* Responsive Design
* Realtime

### Datenbank

* lokal
* robust
* Backup
* Zeitreihen

### Realtime

* niedrige Latenz
* automatische Reconnects
* mehrere Clients

⸻

## 87. Keine Technologie nur wegen Popularität

Begründe jede wesentliche Wahl anhand dieses Projekts.

⸻

## 88. Bestehende Libraries

Verwende etablierte Bibliotheken, wo sinnvoll.

Erfinde keine eigenen:

* Kryptografie
* Datenbanken
* WebSocket-Protokolle
* Authentifizierungsalgorithmen

⸻

## 89. Lizenzierung

Achte bei Abhängigkeiten auf sinnvolle Lizenzen für dieses Projekt.

⸻

## 90. Entwicklungsreihenfolge

Entwickle Kehler OS nicht alles gleichzeitig.

Verwende folgende grundsätzliche Reihenfolge.

⸻

### PHASE 1 – Analyse und Architektur

Bevor du größere Codemengen erstellst:

1. Analysiere Kapitel 1–17 vollständig.
2. Erstelle eine konsolidierte Anforderungsliste.
3. Identifiziere offene Hardwareinformationen.
4. Identifiziere Widersprüche.
5. Wähle den Technologie-Stack.
6. Definiere die Systemarchitektur.
7. Definiere die Projektstruktur.
8. Definiere Daten- und Command-Modelle.

⸻

### PHASE 2 – Projektgrundgerüst

Erstelle anschließend:

* Repository-Struktur
* Backend-Grundgerüst
* Frontend-Grundgerüst
* Konfiguration
* Logging
* Tests
* Entwicklungsumgebung

Noch ohne reale kritische Hardwaresteuerung.

⸻

### PHASE 3 – Simulation

Implementiere zuerst eine vollständige Simulation.

Das Frontend muss mit simulierten Fahrzeugdaten laufen können.

Damit soll bereits getestet werden können:

* Dashboard
* Navigation
* State Management
* Realtime
* Commands
* Warnungen
* Fehlerzustände

⸻

### PHASE 4 – Designsystem

Erstelle das zentrale Kehler-OS-Designsystem.

Definiere:

* Farben
* Typografie
* Spacing
* Radii
* Schatten
* Glows
* Statusfarben
* Buttons
* Switches
* Slider
* Cards
* Dialoge
* Navigation
* Icons
* Animationen

Danach müssen alle Seiten diese Komponenten verwenden.

⸻

### PHASE 5 – Dashboard

Entwickle das zentrale Dashboard.

Prioritäten:

* Designreferenz einhalten
* Fahrzeugdarstellung
* Systemübersicht
* Warnungen
* Schnellzugriffe
* Energie
* Wasser
* Klima
* Nivellierung

⸻

### PHASE 6 – Fachmodule

Implementiere schrittweise:

1. Licht
2. Energie
3. Wasser
4. Klima
5. Fahrzeug
6. Garage
7. Nivellierung
8. Kameras
9. Einstellungen
10. Diagnose

Die Reihenfolge darf begründet angepasst werden.

⸻

### PHASE 7 – Automatisierungen

Erstelle danach:

* Automation Engine
* Szenen
* Trigger
* Bedingungen
* Aktionen
* Historie
* Simulation

⸻

### PHASE 8 – Benutzer und Sicherheit

Vervollständige:

* Authentifizierung
* Rollen
* Berechtigungen
* Audit
* Service-Modus
* abgesicherte APIs

Grundlegende Sicherheitsgrenzen müssen natürlich bereits vorher in der Architektur vorhanden sein.

⸻

### PHASE 9 – Reale SPS-Integration

Vor diesem Schritt musst du die realen SPS-Datenpunkte erhalten.

Wenn die Daten fehlen:

Nicht raten.

Fordere die benötigten Informationen an beziehungsweise hinterlege dokumentierte offene Mappings.

Beginne reale Tests mit ungefährlichen Funktionen.

⸻

### PHASE 10 – Victron

Integriere anschließend die reale Victron-Kommunikation über eine geeignete dokumentierte Schnittstelle.

Teste zunächst Read-Only-Daten.

Schreibzugriffe nur, wenn sie tatsächlich benötigt und sicher unterstützt werden.

⸻

### PHASE 11 – Weitere Hardware

Danach:

* Tanksensoren
* Verriegelungen
* Garage
* Hydraulik
* weitere Geräte

jeweils kontrolliert und einzeln.

⸻

## 91. Keine erste reale Prüfung mit Hydraulik

Die Nivellierung beziehungsweise andere leistungsstarke mechanische Aktoren dürfen nicht die erste reale Hardwareintegration sein.

⸻

## 92. Kleine sichere Schritte

Beginne beispielsweise mit:

digitalen Lesewerten

dann:

ungefährlichen Ausgängen

und erst später mit komplexen Aktoren.

⸻

## 93. Offene Hardwareinformationen

Wenn Informationen fehlen, erstelle eine Datei beziehungsweise Dokumentation wie:

```
OPEN_HARDWARE_REQUIREMENTS.md
```

oder eine vergleichbare strukturierte Lösung.

Dort werden konkrete offene Punkte gesammelt.

⸻

## 94. Beispiele für offene Punkte

Beispielsweise:

```
PLC IP address
PLC data block mapping
tank sensor electrical ranges
garage end switches
lock feedback signals
leveling sensor model
hydraulic valve mapping
```

⸻

## 95. Nicht jedes Detail muss vor Phase 1 bekannt sein

Die Simulation soll Entwicklung ermöglichen, bevor sämtliche reale Hardwaredetails verfügbar sind.

⸻

## 96. Arbeit nicht stoppen, wenn Hardwaredetails fehlen

Wenn eine reale Hardwareinformation fehlt:

* abstrahiere die Schnittstelle
* simuliere das Gerät
* dokumentiere den offenen Punkt
* entwickle unabhängig weiter

sofern dies technisch sinnvoll ist.

⸻

## 97. Keine erfundenen Produktdaten

Erfinde keine realen:

* IP-Adressen
* SPS-Datenbausteine
* Sensormodelle
* Passwörter
* Tankgrößen
* Hardwarefunktionen

wenn sie nicht vorgegeben wurden.

⸻

## 98. Tankgrößen

Die Software soll Tankkapazitäten als Konfiguration behandeln.

Keine frei erfundenen realen Fahrzeugkapazitäten fest einbauen.

⸻

## 99. Fahrzeugdaten

Dasselbe gilt für alle anderen fahrzeugspezifischen Parameter.

Konfigurierbar statt erfunden.

⸻

## 100. Fehler nicht verstecken

Wenn eine Funktion noch nicht real angebunden ist, muss dies im Entwicklungsstand klar erkennbar sein.

Beispiel:

```
SIMULATED
```

oder:

```
NOT CONFIGURED
```

⸻

## 101. Platzhalter im UI

Vermeide hässliche Entwicklerplatzhalter in der finalen Benutzeroberfläche.

Fehlende Hardware soll hochwertig dargestellt werden.

Beispielsweise:

```
Nicht konfiguriert
```

statt:

```
TODO
```

⸻

## 102. Designqualität

Du darfst viel Zeit in das UI investieren.

Kehler OS soll optisch außergewöhnlich hochwertig werden.

Achte besonders auf:

* Abstände
* Größenverhältnisse
* Animation Timing
* Interaktionsfeedback
* Layout
* Typografie
* Statusanzeigen

⸻

## 103. Trotzdem Funktion vor Dekoration

Eine perfekte Karte mit falschem Hardwarezustand ist schlechter als eine etwas einfachere Karte mit korrektem Zustand.

⸻

## 104. Fahrzeugmodell

Die Fahrzeugvisualisierung soll modular aufgebaut sein.

Wenn eine echte grafische Fahrzeugdarstellung nicht sofort verfügbar ist, muss die Architektur erlauben, diese später auszutauschen, ohne das Dashboard neu zu entwickeln.

⸻

## 105. Animation State

Animationen sollen aus echten State-Daten erzeugt werden.

Beispiel:

```
garage.state = OPENING
```

steuert die entsprechende Animation.

⸻

## 106. Keine erfundenen Animationen

Wenn ein Zwischenzustand nicht bekannt ist, darf die UI keine scheinbar präzise reale Bewegung vortäuschen.

⸻

## 107. Performance

Definiere realistische Performance-Ziele und messe sie.

Besonders:

* Frontend
* API
* Realtime
* Startup
* State Updates

⸻

## 108. Dauerlauf

Plane einen längeren Stabilitätstest.

Das System soll nicht nur fünf Minuten lang funktionieren.

⸻

## 109. Testdauer

Vor einer finalen Produktionsfreigabe sollen unter anderem längere Tests mit:

* Reconnects
* Datenbank
* Realtime
* Simulation
* Speicherverbrauch

durchgeführt werden.

⸻

## 110. Sicherheitsreview

Vor produktiver Hardwaresteuerung soll eine eigene Sicherheitsprüfung erfolgen.

Prüfe insbesondere:

* Berechtigungen
* Command Validation
* Timeouts
* Aktor-Retries
* UNKNOWN Handling
* Service-Modus
* Remote Access
* Secrets

⸻

## 111. Code Review

Prüfe den eigenen Code kritisch auf:

* Duplikation
* unnötige Komplexität
* Sicherheitsprobleme
* fehlende Fehlerfälle
* schlechte Abstraktion

⸻

## 112. Keine automatische komplette Neuschreibung

Wenn später ein Problem entdeckt wird, soll nicht reflexartig das gesamte Projekt neu aufgebaut werden.

Die modulare Architektur soll gezielte Verbesserungen ermöglichen.

⸻

## 113. KI-Assistent

Die KI-Funktion ist eine spätere Ebene und nicht Voraussetzung für den Core von Kehler OS.

Das Grundsystem muss vollständig ohne KI funktionieren.

⸻

## 114. KI-Funktionen

Später kann KI beispielsweise:

* Systemzustände erklären
* historische Daten analysieren
* Wartungshinweise geben
* Automatisierungen vorschlagen
* Benutzerfragen beantworten

⸻

## 115. KI darf nicht frei auf Hardware zugreifen

Alle KI-Aktionen laufen über dieselbe kontrollierte Command-Infrastruktur.

⸻

## 116. Lokale KI versus Cloud-KI

Treffe die Entscheidung später anhand von:

* Raspberry-Pi-Leistung
* Internet
* Datenschutz
* Funktionsanforderungen

Die gesamte Fahrzeugsteuerung darf nicht von einem Cloud-KI-Modell abhängig sein.

⸻

## 117. Erst Core, dann KI

Implementiere niemals zuerst den KI-Assistenten.

Reihenfolge:

```
Core
↓
Hardware
↓
Stabilität
↓
Automatisierung
↓
KI
```

⸻

## 118. Definition of Done

Ein Modul gilt nicht als fertig, wenn nur der Happy Path funktioniert.

Mindestens müssen berücksichtigt sein:

```
Normalzustand
Loading
Unknown
Offline
Error
Permission denied
Timeout
Reconnect
```

soweit für das Modul relevant.

⸻

## 119. Definition of Done für Hardware

Eine reale Hardwarefunktion gilt erst als integriert, wenn mindestens geprüft wurde:

```
Lesen
Schreiben, falls erforderlich
Rückmeldung
Timeout
Verbindungsverlust
Reconnect
Fehlerzustand
Neustart
```

⸻

## 120. Definition of Done für UI

Eine UI-Seite gilt erst als fertig, wenn:

* Designsystem eingehalten
* Touch-Bedienung funktioniert
* Status korrekt dargestellt
* Fehlerfälle dargestellt
* responsive Verhalten geprüft
* keine Mock-Werte als reale Werte erscheinen

⸻

## 121. Dokumentiere Annahmen

Falls du eine Annahme treffen musst, kennzeichne sie.

Beispiel:

```
ASSUMPTION:
...
```

Vermeide versteckte Annahmen.

⸻

## 122. Frage nur, wenn notwendig

Du sollst nicht bei jedem kleinen Detail die Entwicklung unterbrechen.

Wenn eine sinnvolle konfigurierbare oder simulierbare Lösung möglich ist, nutze sie.

Frage nur dann nach, wenn eine reale Entscheidung ohne die Information nicht sicher getroffen werden kann.

⸻

## 123. Hardwarefragen bündeln

Wenn mehrere reale Hardwaredetails benötigt werden, bündele sie in einer klaren Liste statt ständig einzelne Fragen zu stellen.

⸻

## 124. Priorität des realen Fahrzeugs

Kehler OS ist derzeit für ein konkretes Fahrzeug bestimmt.

Optimiere deshalb die UX auf dieses Fahrzeug.

Die Architektur soll trotzdem sauber genug bleiben, um später erweitert werden zu können.

⸻

## 125. Keine vorschnelle Produktplattform

Baue nicht sofort:

* Kundenverwaltung
* Abrechnung
* Flottenverwaltung
* Multi-Tenant-Cloud

Diese Dinge gehören derzeit nicht zum Projekt.

⸻

## 126. Grundlegende Projektstruktur

Nach deiner Analyse soll eine klare Projektstruktur entstehen.

Konzeptionell beispielsweise:

```
kehler-os/
│
├── backend/
├── frontend/
├── config/
├── simulation/
├── tests/
├── deployment/
├── docs/
└── tools/
```

Dies ist kein verbindlicher Dateibaum.

Du darfst eine bessere Struktur wählen.

⸻

## 127. Dokumentationsstruktur

Die Dokumentation soll sowohl für den Projektbesitzer als auch für zukünftige Entwickler verständlich sein.

⸻

## 128. CHANGELOG

Führe während der Entwicklung einen sinnvollen Changelog beziehungsweise eine Versionshistorie.

⸻

## 129. Roadmap

Erstelle eine Entwicklungsroadmap mit klaren Meilensteinen.

⸻

## 130. Meilensteine

Geeignete Meilensteine können beispielsweise sein:

```
M1 – Architektur und Skeleton
M2 – Simulation
M3 – Dashboard
M4 – Core Fahrzeugmodule
M5 – Automatisierung
M6 – reale SPS
M7 – Victron
M8 – reale Fahrzeugintegration
M9 – Stabilisierung
M10 – Production Release
```

Passe sie sinnvoll an.

⸻

## 131. Fortschritt sichtbar halten

Dokumentiere, welche Funktionen:

```
PLANNED
IN PROGRESS
SIMULATED
HARDWARE TESTED
PRODUCTION READY
```

sind.

⸻

## 132. Keine Verwechslung von simuliert und fertig

Eine perfekt funktionierende Simulation bedeutet nicht automatisch, dass die reale Hardwareintegration abgeschlossen ist.

⸻

## 133. Anforderungen rückverfolgbar machen

Wo sinnvoll, sollen wichtige Implementierungsentscheidungen auf die Anforderungen aus diesen Kapiteln zurückführbar sein.

⸻

## 134. Erste Antwort nach diesem Kapitel

Nach Erhalt dieses Kapitels sollst du nicht sofort tausende Zeilen Code erzeugen.

Deine erste Aufgabe lautet:

1. Bestätige, dass du Kapitel 1–18 als vollständige Projektspezifikation verstanden hast.
2. Erstelle eine kurze konsolidierte Zusammenfassung des Systems.
3. Nenne erkennbare Widersprüche oder offene technische Fragen.
4. Schlage einen konkreten Technologie-Stack vor.
5. Begründe jede Hauptentscheidung.
6. Zeige die geplante Projektarchitektur.
7. Zeige die Entwicklungsphasen.
8. Liste die Hardwareinformationen auf, die später für die reale Integration benötigt werden.

Danach darfst du mit Phase 1 beginnen.

⸻

## 135. Nicht auf eine erneute Freigabe warten

Nachdem du die obige Analyse geliefert hast, darfst du direkt mit der initialen Projektstruktur und der Entwicklung beginnen, sofern keine sicherheitskritische reale Hardwareinformation fehlt.

Für fehlende reale Hardwareinformationen verwendest du Simulation und Abstraktion.

⸻

## 136. Keine realen Aktoren ohne Daten

Du darfst niemals eine echte mechanische oder sicherheitsrelevante Hardwareintegration anhand erfundener Parameter aktivieren.

⸻

## 137. Architektur darf sich entwickeln

Wenn du während der Implementierung eine bessere technische Lösung erkennst, darf die interne Implementierung verbessert werden.

Die funktionalen und sicherheitsrelevanten Anforderungen aus Kapitel 1–18 bleiben jedoch bestehen.

⸻

## 138. Abweichungen dokumentieren

Wenn eine konkrete Vorgabe technisch nicht sinnvoll oder nicht umsetzbar ist, dokumentiere:

```
Requirement
Problem
Alternative
Reason
Impact
```

und verwende die technisch bessere Lösung.

⸻

## 139. Kein blindes Gehorchen bei technischen Fehlern

Die Spezifikation beschreibt das gewünschte System.

Falls eine einzelne technische Formulierung objektiv zu einer schlechteren oder unsicheren Lösung führen würde, wähle die bessere Lösung und dokumentiere die Abweichung.

⸻

## 140. Ziel

Das Endergebnis soll sich anfühlen wie ein echtes Produkt.

Der Benutzer soll:

* Kehler OS einschalten
* sofort das Fahrzeug sehen
* den Zustand verstehen
* Funktionen intuitiv bedienen
* Warnungen klar erkennen
* keine technische Komplexität sehen

⸻

## 141. Im Hintergrund

Gleichzeitig soll das System technisch besitzen:

```
Hardwareabstraktion
Central State
Command Processing
Realtime
Events
Automation
Authentication
Permissions
Logging
History
Diagnostics
Simulation
Testing
Backup
Updates
```

⸻

## 142. Qualitätsanspruch

Das Ziel ist nicht:

„Eine Webseite, mit der man ein paar SPS-Ausgänge schalten kann.“

Das Ziel ist:

Ein professionelles digitales Betriebssystem für das gesamte Wohnmobil.

⸻

## 143. Langfristige Vision

Kehler OS soll über Jahre erweitert werden können.

Später können beispielsweise hinzukommen:

* zusätzliche Kameras
* neue Sensoren
* weitere Energiekomponenten
* neue Displays
* Wetterstation
* KI-Assistent
* Predictive Maintenance
* Remote-Zugriff
* zusätzliche Automatisierungen

Die heutige Architektur soll diesen Weg ermöglichen.

⸻

## 144. Letzte verbindliche Regel

Wenn eine Entscheidung zwischen:

schnell gebaut

und:

langfristig sauber

besteht, wähle grundsätzlich die langfristig saubere Lösung, sofern dadurch keine unnötige Überkomplexität entsteht.

⸻

## 145. Entwicklungsfreigabe

Mit Abschluss dieses Dokuments ist die bisherige reine Wissensaufnahme beendet.

DU DARFST JETZT MIT DER ENTWICKLUNG VON KEHLER OS BEGINNEN.

Beginne jedoch strukturiert.

Nicht mit zufälligem Code.

Zuerst:

```
Analyse
↓
Technologieentscheidung
↓
Architektur
↓
Projektstruktur
↓
Simulation
↓
Core
↓
Frontend
↓
reale Hardwareintegration
```

⸻

## ENDE DER GESAMTSPEZIFIKATION

Projekt: Kehler OS

Dokumente: Kapitel 1–18

Status: DEVELOPMENT AUTHORIZED

Primärplattform: Raspberry Pi 5

Industriesteuerung: Siemens S7-1511-1 PN

Energiesystem: Victron / Cerbo GX / MultiPlus / 24-V-System

Primäres Ziel: vollständige lokale Steuerungs-, Visualisierungs-, Diagnose- und Automatisierungsplattform für das Wohnmobil.

Designrichtung: Premium Dark Vehicle HMI gemäß bereitgestellter Referenz.

Grundsatz:

Kehler OS muss so gut aussehen wie ein Premium-Fahrzeugsystem, so zuverlässig arbeiten wie industrielle Steuerungstechnik und sich für den Benutzer trotzdem selbstverständlich anfühlen.
