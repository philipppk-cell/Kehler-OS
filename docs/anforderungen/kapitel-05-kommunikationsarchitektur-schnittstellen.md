# KEHLER OS

# Kapitel 5 – Kommunikationsarchitektur und Schnittstellen

> Vorbemerkung aus der Übermittlung:
> Kapitel 5 ist besonders wichtig, weil hier festgelegt wird, wie die einzelnen
> Systeme miteinander sprechen. Dabei halten wir die Ebenen sauber getrennt:
> Die SPS bleibt für Echtzeitsteuerung zuständig, Kehler OS für übergeordnete
> Logik und Visualisierung.

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Treffe keine eigenständigen Architekturentscheidungen.

Dieses Kapitel beschreibt verbindliche Anforderungen und Grundsätze für die spätere Kommunikationsarchitektur.

Verwende dieses Kapitel zusammen mit allen vorherigen Kapiteln als Grundlage für die folgenden Kapitel.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel der Kommunikationsarchitektur

Kehler OS besteht aus verschiedenen Hardware- und Softwarekomponenten.

Diese Komponenten müssen zuverlässig miteinander kommunizieren.

Die Kommunikation muss:

* zuverlässig
* nachvollziehbar
* fehlertolerant
* schnell
* sicher
* modular
* erweiterbar

sein.

Die Kommunikationsarchitektur darf nicht davon abhängig sein, dass einzelne Komponenten dauerhaft verfügbar sind.

⸻

## 2. Grundprinzip

Kehler OS besitzt eine klare Trennung zwischen:

1. Hardware
2. Hardwarekommunikation
3. Systemdiensten
4. Geschäftslogik
5. Benutzeroberfläche

Die Benutzeroberfläche darf niemals direkt mit der SPS oder Victron kommunizieren.

Beispiel:

Benutzer drückt „Licht Wohnzimmer EIN“.

Nicht:

GUI → SPS

Sondern logisch:

```
GUI
 ↓
Kehler-OS-Backend
 ↓
Lichtmodul
 ↓
Hardware-Abstraktion
 ↓
Kommunikationsschnittstelle
 ↓
SPS
 ↓
Ausgang
 ↓
Licht
```

Dadurch bleibt die Benutzeroberfläche vollständig von der Hardware entkoppelt.

⸻

## 3. Raspberry Pi

Der Raspberry Pi 5 ist die zentrale Kommunikationsplattform von Kehler OS.

Er verbindet die verschiedenen Systeme miteinander.

Der Raspberry Pi übernimmt unter anderem:

* Kommunikation mit der SPS
* Kommunikation mit Victron
* Datenverarbeitung
* Speicherung
* Ereignisverarbeitung
* API-Bereitstellung
* Benutzeroberfläche
* Automatisierungen
* Diagnose
* Logging
* Systemüberwachung

Der Raspberry Pi darf jedoch keine Aufgaben übernehmen, die zwingende SPS-Echtzeit benötigen.

⸻

## 4. Siemens SPS

Die Siemens S7-1500 ist für die direkte Maschinen- und Fahrzeugsteuerung zuständig.

Die SPS verarbeitet:

* digitale Eingänge
* digitale Ausgänge
* analoge Eingänge
* Sensorwerte
* Aktoren
* Relais
* Pumpen
* Ventile
* Beleuchtung
* Verriegelungen
* weitere direkte Steuerungsaufgaben

Die SPS muss grundsätzlich unabhängig vom Raspberry Pi funktionieren.

⸻

## 5. SPS-Ausfall des Raspberry Pi

Der Ausfall des Raspberry Pi darf nicht dazu führen, dass die SPS ihre grundlegenden Steuerungsaufgaben verliert.

Beispielsweise müssen vorhandene SPS-Funktionen weiterhin funktionieren, wenn:

* der Raspberry Pi ausgeschaltet ist
* das Betriebssystem neu startet
* das Netzwerk kurzzeitig ausfällt
* eine Software aktualisiert wird

Die SPS darf deshalb nicht von einer permanenten Verbindung zum Backend abhängig sein.

⸻

## 6. Kommunikation Raspberry Pi ↔ SPS

Die Kommunikation zwischen Raspberry Pi und SPS wird über eine geeignete industrielle Netzwerkschnittstelle realisiert.

Die konkrete technische Implementierung wird in späteren Kapiteln festgelegt.

Grundsätzlich gilt:

Der Raspberry Pi liest Zustände aus der SPS.

Der Raspberry Pi schreibt freigegebene Befehle an die SPS.

Die SPS entscheidet weiterhin selbst über sicherheitskritische und echtzeitabhängige Vorgänge.

⸻

## 7. Lesen von SPS-Daten

Kehler OS soll unter anderem folgende Informationen aus der SPS erhalten können:

* digitale Eingänge
* digitale Ausgänge
* analoge Werte
* Tankwerte
* Temperaturwerte
* Türkontakte
* Fensterkontakte
* Garagenstatus
* Pumpenzustände
* Lichtzustände
* Verriegelungszustände
* weitere Sensorwerte

Die Daten müssen im Backend in einer verständlichen Form zur Verfügung stehen.

Die Benutzeroberfläche soll niemals SPS-Adressen kennen müssen.

Beispiel:

Die GUI darf nicht wissen:

```
DB10.DBX4.2
```

Sie soll stattdessen einen semantischen Wert erhalten, beispielsweise:

```
garage.door.state
```

Die Hardwareadresse bleibt ausschließlich innerhalb der Hardwarekommunikationsschicht.

⸻

## 8. Schreiben von SPS-Daten

Auch beim Schreiben gilt die Abstraktion.

Die GUI sendet beispielsweise:

```
light.living_room.set_state = true
```

Das Backend verarbeitet die Anfrage.

Erst die Hardware-Abstraktionsschicht übersetzt sie in die entsprechende SPS-Kommunikation.

Dadurch bleibt die Hardware austauschbar.

⸻

## 9. Hardware-Abstraktion

Jede Hardware erhält eine logische Schnittstelle.

Beispiel:

```
LightController
TankSensor
DoorController
GarageController
PumpController
TemperatureSensor
```

Die restliche Software arbeitet ausschließlich mit diesen logischen Komponenten.

Die konkrete Hardware wird darunter gekapselt.

⸻

## 10. Victron-System

Das Victron-System ist für die Energieverwaltung zuständig.

Kehler OS soll die relevanten Informationen aus dem Victron-System erfassen.

Beispiele:

* Batteriespannung
* Batteriestrom
* Ladezustand
* Ladeleistung
* Entladeleistung
* Solarleistung
* Solarspannung
* Solarstrom
* Wechselrichterstatus
* Ladegerätstatus
* Landstromstatus
* Alarme
* Systemzustände

Kehler OS darf die Energieinformationen visualisieren und für Automatisierungen verwenden.

⸻

## 11. Trennung der Verantwortlichkeiten bei Victron

Victron bleibt für seine eigene Energiehardware verantwortlich.

Kehler OS ersetzt nicht die Victron-Steuerung.

Kehler OS bildet darüber eine intelligente übergeordnete Ebene.

Beispiel:

Victron entscheidet technisch über Ladeprozesse.

Kehler OS kann beispielsweise erkennen:

„Batterie ist fast voll.“

Darauf kann Kehler OS eine übergeordnete Automatisierung ausführen.

⸻

## 12. Interne Kommunikation

Innerhalb von Kehler OS wird eine einheitliche Kommunikationsstruktur benötigt.

Module sollen nicht unnötig direkt miteinander verbunden werden.

Bevorzugt wird eine ereignisorientierte Kommunikation.

Beispiel:

```
Batterie
 ↓
battery.state.changed
 ↓
Event-System
 ↓
Dashboard
Automatisierung
Benachrichtigung
Logging
KI
```

Dadurch kann ein Ereignis von mehreren Modulen verwendet werden.

⸻

## 13. Ereignisse

Ereignisse müssen eindeutig benannt werden.

Beispiele:

```
battery.state.changed
tank.level.changed
door.opened
door.closed
garage.opened
garage.closed
shore_power.connected
shore_power.disconnected
internet.online
internet.offline
camera.online
camera.offline
system.warning
system.error
```

Die tatsächlichen Ereignisnamen dürfen später weiter standardisiert werden.

Wichtig ist die Konsistenz.

⸻

## 14. Ereignisdaten

Ein Ereignis muss mindestens eindeutig identifizierbar sein.

Es sollte logisch folgende Informationen enthalten können:

* Ereignistyp
* Zeitpunkt
* Quelle
* Wert
* vorheriger Wert
* neuer Wert
* Schweregrad
* optionale Zusatzinformationen

Beispiel:

```
event:
    type: tank.level.changed
    source: fresh_water_tank
    previous: 62
    current: 61
    timestamp: ...
```

Die endgültige Datenstruktur wird in einem späteren Kapitel definiert.

⸻

## 15. MQTT

MQTT kann als Kommunikationsmechanismus innerhalb der Systemarchitektur eingesetzt werden.

Es eignet sich insbesondere für:

* Ereignisse
* Zustände
* Sensorwerte
* lose Kopplung
* zukünftige Erweiterungen

MQTT darf jedoch nicht automatisch für jede Kommunikation verwendet werden.

Für jede Schnittstelle muss geprüft werden, welches Kommunikationsverfahren technisch sinnvoll ist.

⸻

## 16. APIs

Kehler OS benötigt klar definierte APIs.

Die API stellt Funktionen des Backends für Benutzeroberflächen und zukünftige Clients bereit.

Beispiele:

```
GET /api/system/status
GET /api/tanks
GET /api/energy
GET /api/lights
POST /api/lights/living-room
GET /api/cameras
GET /api/alerts
```

Die endgültige API-Struktur wird später definiert.

Die API muss versionierbar sein.

⸻

## 17. Echtzeitdaten

Bestimmte Informationen müssen nahezu unmittelbar auf der Benutzeroberfläche erscheinen.

Beispiele:

* Lichtstatus
* Türstatus
* Garagentor
* Tankwerte
* Batterie
* Solarleistung
* Alarme

Für solche Daten ist eine kontinuierliche Aktualisierung erforderlich.

Eine geeignete Echtzeitkommunikation zwischen Backend und Frontend muss vorgesehen werden.

WebSockets oder eine vergleichbare Technologie können hierfür verwendet werden.

Die endgültige Entscheidung erfolgt in einem späteren Architekturkapitel.

⸻

## 18. Polling

Polling darf nicht grundsätzlich verboten werden.

Es soll dort verwendet werden, wo es technisch sinnvoll ist.

Es darf jedoch nicht dazu führen, dass:

* unnötig Netzwerkverkehr entsteht
* die SPS überlastet wird
* der Raspberry Pi unnötig belastet wird
* die Benutzeroberfläche verzögert reagiert

Die Kommunikationsfrequenz muss für jede Datenart sinnvoll gewählt werden.

⸻

## 19. Zustandsmodell

Kehler OS muss zwischen verschiedenen Zuständen unterscheiden können.

Beispielsweise:

```
ONLINE
OFFLINE
UNKNOWN
ERROR
WARNING
INITIALIZING
```

Ein fehlender Datenwert darf nicht automatisch als „0“ interpretiert werden.

Beispiel:

Wenn ein Tanksensor nicht erreichbar ist, bedeutet das nicht:

Tank = 0 %

Sondern:

Tank = UNKNOWN

Diese Unterscheidung ist für die Sicherheit und Benutzerführung entscheidend.

⸻

## 20. Kommunikationsfehler

Kommunikationsfehler müssen erkannt werden.

Beispiele:

* SPS nicht erreichbar
* Victron nicht erreichbar
* Kamera nicht erreichbar
* MQTT nicht erreichbar
* Netzwerkverbindung verloren
* API nicht erreichbar

Das System muss erkennen:

1. dass ein Fehler besteht
2. welches System betroffen ist
3. seit wann der Fehler besteht
4. ob der Fehler automatisch behoben wurde
5. ob der Benutzer informiert werden muss

⸻

## 21. Wiederverbindung

Wenn eine Verbindung verloren geht, muss das System automatisch versuchen, sie wiederherzustellen.

Die Wiederverbindung darf jedoch nicht zu einer Endlosschleife führen.

Es müssen geeignete:

* Timeouts
* Wiederholungsintervalle
* Backoff-Mechanismen
* Fehlerzustände

vorgesehen werden.

⸻

## 22. Netzwerkunterbrechungen

Das Fahrzeug muss auch bei Netzwerkproblemen möglichst weiter funktionieren.

Ein kurzfristiger Netzwerkausfall darf nicht dazu führen, dass sämtliche Funktionen ausfallen.

Lokale Steuerungsfunktionen müssen weiterhin verfügbar bleiben.

⸻

## 23. Internet

Internet ist keine Voraussetzung für den Betrieb.

Kehler OS muss vollständig lokal funktionieren.

Internet wird nur für zusätzliche Funktionen benötigt.

Beispiele:

* Wetter
* Fernzugriff
* Kartenaktualisierung
* Updates
* Cloud-Dienste
* externe KI-Dienste

Der Verlust des Internets darf die Grundfunktionen des Fahrzeugs nicht beeinträchtigen.

⸻

## 24. Sicherheit

Kommunikation muss grundsätzlich gegen unberechtigten Zugriff geschützt werden.

Besonders geschützt werden müssen:

* Steuerbefehle
* Benutzerkonten
* Administrationsfunktionen
* Netzwerkzugänge
* externe Schnittstellen

Nicht jede Schnittstelle darf aus dem Internet erreichbar sein.

⸻

## 25. Keine direkte Internetsteuerung der Hardware

SPS und andere kritische Hardware dürfen niemals ungeschützt direkt aus dem Internet erreichbar sein.

Externer Zugriff muss ausschließlich über die dafür vorgesehene sichere Kehler-OS-Infrastruktur erfolgen.

⸻

## 26. Zeitstempel

Zeitkritische Ereignisse benötigen korrekte Zeitstempel.

Das System muss zwischen:

* Systemzeit
* Ereigniszeit
* Messzeit

unterscheiden können.

Bei fehlender Internetverbindung muss weiterhin eine zuverlässige lokale Zeitbasis vorhanden sein.

⸻

## 27. Diagnose

Die Kommunikationsarchitektur muss Diagnosemöglichkeiten bieten.

Der Administrator soll später erkennen können:

* welche Geräte verbunden sind
* welche Geräte offline sind
* wann die Verbindung zuletzt aktiv war
* wie viele Kommunikationsfehler aufgetreten sind
* welche Schnittstelle Probleme verursacht

⸻

## 28. Erweiterungen

Die Kommunikationsarchitektur muss später weitere Systeme aufnehmen können.

Beispiele:

* weitere SPS
* zusätzliche Victron-Geräte
* Modbus-Geräte
* CAN-Bus-Geräte
* Bluetooth-Geräte
* USB-Geräte
* weitere Sensoren
* neue Kameras
* externe Steuerungen

Neue Schnittstellen sollen über Adapter beziehungsweise Treiber integriert werden können.

⸻

## 29. Grundsatz für zukünftige Entwickler

Ein Entwickler darf niemals einfach eine direkte Verbindung zwischen zwei Modulen herstellen, nur weil dies kurzfristig einfacher ist.

Vor jeder neuen Verbindung muss geprüft werden:

* Welche Ebene ist zuständig?
* Gibt es bereits einen passenden Dienst?
* Gibt es bereits eine Schnittstelle?
* Muss ein neues Event definiert werden?
* Kann die Verbindung abstrahiert werden?

Die Architektur soll langfristig sauber bleiben.

⸻

## 30. Zielbild

Das ideale Kommunikationsmodell sieht logisch ungefähr so aus:

```
                    KEHLER OS
                        │
              ┌─────────┴─────────┐
              │                   │
          Frontend             Backend
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
          Event-System       Systemdienste       Fachmodule
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                       Hardware-Abstraktion
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
             SPS               Victron            Kameras
              │                   │                   │
          Sensoren             Energie            Video
          Aktoren              System
```

Diese Darstellung beschreibt das gewünschte Prinzip, nicht bereits die endgültige technische Implementierung.

⸻

## 31. Prioritäten

Bei der Auswahl einer Kommunikationsmethode gilt folgende Priorität:

1. Sicherheit
2. Zuverlässigkeit
3. Datenkonsistenz
4. Wartbarkeit
5. Performance
6. Erweiterbarkeit
7. Einfachheit

Eine vermeintlich einfachere Lösung darf nicht gewählt werden, wenn sie langfristig Nachteile verursacht.

⸻

## 32. Dokumentationspflicht

Jede externe Schnittstelle muss dokumentiert werden.

Für jede Schnittstelle müssen später mindestens definiert werden:

* Zweck
* Protokoll
* Datenformat
* Endpunkte beziehungsweise Adressen
* Eingaben
* Ausgaben
* Fehlerzustände
* Timeout-Verhalten
* Wiederverbindung
* Sicherheitsanforderungen
* Version

⸻

## Ende Kapitel 5

Dieses Kapitel definiert die Grundprinzipien der Kommunikationsarchitektur von Kehler OS.

Die konkrete technische Implementierung wird in späteren Kapiteln weiter spezifiziert.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf das nächste Kapitel.

Verwende Kapitel 1 bis 5 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
