# KEHLER OS

# Kapitel 10 – Systemarchitektur und Kommunikation

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel beschreibt die technische Architektur und die Kommunikation zwischen den einzelnen Komponenten von Kehler OS.

Die konkrete Technologieauswahl darf erst nach vollständiger Analyse aller Anforderungen erfolgen.

Verwende Kapitel 1–10 gemeinsam als verbindliche Grundlage.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Grundprinzip

Kehler OS soll nicht aus einer einzigen unstrukturierten Anwendung bestehen.

Das System soll aus klar voneinander getrennten Ebenen bestehen.

Grundsätzlich soll zwischen folgenden Bereichen unterschieden werden:

```
Hardware
↓
Steuerung / Controller
↓
Kommunikationsschicht
↓
Backend / Systemlogik
↓
Datenmodell
↓
API / Echtzeitkommunikation
↓
Benutzeroberfläche
```

Die genaue technische Umsetzung wird später festgelegt.

⸻

## 2. Hardwareebene

Die Hardwareebene besteht aus den tatsächlichen Geräten im Fahrzeug.

Dazu können gehören:

* Siemens SPS
* Victron-System
* Raspberry Pi
* Sensoren
* Aktoren
* Kameras
* Netzwerkhardware
* weitere Steuergeräte

Kehler OS darf nicht davon ausgehen, dass alle Geräte dieselbe Kommunikationsschnittstelle verwenden.

⸻

## 3. Siemens SPS

Die SPS ist eine zentrale Steuerungskomponente des Fahrzeugs.

Im Projekt ist eine:

Siemens S7-1511-1 PN

vorgesehen.

Zusätzlich gehören zur SPS-Konfiguration unter anderem:

* digitale Eingänge
* digitale Ausgänge
* analoge Eingänge
* Netzteil

Die SPS übernimmt die Steuerung beziehungsweise Erfassung der dafür vorgesehenen Fahrzeugfunktionen.

⸻

## 4. SPS ist nicht die Benutzeroberfläche

Kehler OS soll nicht versuchen, die SPS direkt als HMI zu verwenden.

Die SPS ist eine Steuerung.

Kehler OS ist die Benutzeroberfläche und übergeordnete Systemplattform.

Daher soll die Architektur klar zwischen:

Steuerlogik

und:

Benutzeroberfläche

trennen.

⸻

## 5. Victron-System

Das Energiesystem basiert unter anderem auf Victron-Komponenten.

Dazu können gehören:

* Batterie
* MultiPlus
* Cerbo GX
* Solar
* Landstrom
* weitere Energiekomponenten

Kehler OS soll relevante Informationen des Victron-Systems zentral darstellen können.

⸻

## 6. Raspberry Pi

Der Raspberry Pi ist als wichtiger Bestandteil der Kehler-OS-Systemarchitektur vorgesehen.

Er kann beispielsweise als Plattform für:

* Backend
* Kommunikationsdienste
* Datenverarbeitung
* lokale Services
* Datenhaltung
* API
* weitere Systemkomponenten

dienen.

Die endgültige Aufgabenverteilung wird später anhand der Gesamtarchitektur entschieden.

⸻

## 7. Zentrale Abstraktion

Die Benutzeroberfläche darf nicht direkt von den physischen Hardwareadressen abhängig sein.

Beispiel:

Die UI soll nicht wissen:

```
SPS Ausgang 14
```

sondern beispielsweise nur:

```
garage.open
```

Die Kommunikationsschicht übersetzt den logischen Befehl anschließend in die tatsächlich benötigte Hardwareaktion.

⸻

## 8. Warum diese Abstraktion wichtig ist

Die Hardware kann sich später ändern.

Beispielsweise könnte ein Aktor irgendwann:

* auf einem anderen SPS-Ausgang liegen
* über ein anderes Gerät gesteuert werden
* über ein anderes Protokoll kommunizieren

Die Benutzeroberfläche soll deshalb nicht neu entwickelt werden müssen.

⸻

## 9. Logisches Gerätemodell

Kehler OS soll mit logischen Geräten und Funktionen arbeiten.

Beispiele:

```
vehicle.door.main
vehicle.garage.door
vehicle.step
vehicle.awning
vehicle.light.exterior
water.freshwater
water.greywater
energy.battery
energy.solar
climate.interior
leveling.pitch
leveling.roll
```

Diese Bezeichnungen dienen als konzeptionelle Beispiele.

Die endgültige Namenskonvention soll später einheitlich definiert werden.

⸻

## 10. Datenmodell

Alle relevanten Fahrzeugdaten sollen in einem konsistenten Datenmodell abgebildet werden.

Ein Datenpunkt sollte grundsätzlich Informationen besitzen können wie:

```
Wert
Einheit
Zeitstempel
Zustand
Quelle
Qualität
```

Beispiel:

```
Batterie
Wert: 87
Einheit: %
Zeit: 20:15
Status: ONLINE
Quelle: Victron
```

⸻

## 11. Datenqualität

Ein Wert allein reicht nicht aus.

Kehler OS muss erkennen können, ob ein Wert tatsächlich gültig ist.

Beispielsweise:

```
VALID
UNKNOWN
STALE
OFFLINE
ERROR
```

Dadurch wird verhindert, dass alte oder ungültige Werte als aktuelle Messwerte angezeigt werden.

⸻

## 12. Zeitstempel

Messwerte sollen mit einem Zeitbezug versehen werden.

Das ermöglicht unter anderem:

* historische Diagramme
* Erkennung veralteter Daten
* Fehlerdiagnose
* Protokollierung
* Ereignishistorie

⸻

## 13. Echtzeitdaten

Viele Fahrzeugdaten müssen nahezu in Echtzeit dargestellt werden.

Dazu gehören beispielsweise:

* Tankfüllstände
* Batteriestrom
* Temperatur
* Türen
* Garage
* Stufen
* Markise
* Nivellierung
* Netzwerkstatus

Die Benutzeroberfläche darf nicht ausschließlich auf manuelles Aktualisieren angewiesen sein.

⸻

## 14. Ereignisbasierte Kommunikation

Wo sinnvoll, soll das System Änderungen ereignisbasiert übertragen.

Beispiel:

Garage geschlossen

ändert sich zu:

Garage öffnet

Kehler OS soll diese Änderung möglichst unmittelbar erhalten.

⸻

## 15. Keine unnötige Abfrageflut

Das System soll nicht permanent jede Information unnötig abfragen.

Es muss zwischen:

* Echtzeitwerten
* langsam veränderlichen Daten
* historischen Daten
* Ereignissen

unterschieden werden.

Dadurch soll die Kommunikation effizient bleiben.

⸻

## 16. API

Die Benutzeroberfläche soll über eine definierte Schnittstelle mit dem Backend kommunizieren.

Die API stellt logische Funktionen und Daten bereit.

Die UI soll beispielsweise nicht direkt mit:

* SPS-Protokollen
* Victron-Protokollen
* Sensorprotokollen

arbeiten.

⸻

## 17. Lesen und Schreiben

Die Kommunikationsarchitektur muss zwischen zwei grundsätzlichen Vorgängen unterscheiden:

### Lesen

Beispiel:

Batteriestand auslesen

### Schreiben / Steuern

Beispiel:

Garage öffnen

Diese Vorgänge müssen sauber voneinander getrennt werden.

⸻

## 18. Befehle

Ein Steuerbefehl sollte nicht einfach als unkontrollierter Hardwarezugriff behandelt werden.

Beispiel:

```
garage.open
```

wird vom System verarbeitet.

Dabei können beispielsweise geprüft werden:

* Berechtigung
* aktueller Zustand
* Sicherheitsbedingungen
* Verfügbarkeit der Hardware

Erst anschließend wird der Befehl an die entsprechende Steuerung weitergegeben.

⸻

## 19. Rückmeldung

Nach einem Steuerbefehl muss die tatsächliche Rückmeldung der Hardware berücksichtigt werden.

Beispiel:

```
Benutzer:
Garage öffnen
System:
Befehl gesendet
Hardware:
Garage öffnet
System:
Garage OPENING
Hardware:
Garage vollständig geöffnet
System:
Garage OPEN
```

Dadurch bleibt die Benutzeroberfläche synchron mit dem tatsächlichen Fahrzeugzustand.

⸻

## 20. Fehler bei Befehlen

Wenn ein Befehl nicht ausgeführt werden kann, muss dies eindeutig erkannt werden.

Beispiel:

```
Garage öffnen
→ keine Verbindung zur Steuerung
→ Befehl fehlgeschlagen
```

Die UI darf nicht einfach einen erfolgreichen Zustand vortäuschen.

⸻

## 21. Kommunikationsfehler

Das System muss mit Kommunikationsfehlern umgehen können.

Mögliche Fehler:

* SPS nicht erreichbar
* Victron nicht erreichbar
* Raspberry Pi Dienst ausgefallen
* Netzwerkunterbrechung
* Sensor antwortet nicht
* Kamera offline

⸻

## 22. Teilweiser Ausfall

Ein Fehler in einem System darf nicht automatisch das gesamte Kehler OS unbrauchbar machen.

Beispiel:

Wenn eine Kamera ausfällt, sollen weiterhin funktionieren:

* Licht
* Wasser
* Energie
* Klima
* Fahrzeugstatus

Das System muss möglichst fehlertolerant aufgebaut sein.

⸻

## 23. Offline-Verhalten

Wenn ein Gerät nicht erreichbar ist, muss Kehler OS den Zustand transparent darstellen.

Beispiel:

```
Victron
OFFLINE
```

statt scheinbar aktueller Werte.

⸻

## 24. Backend

Zwischen Hardware und Benutzeroberfläche soll eine zentrale Backend-/Serviceschicht existieren.

Diese Schicht übernimmt unter anderem:

* Kommunikation
* Datenaufbereitung
* Zustandsverwaltung
* Befehlsverarbeitung
* Berechtigungen
* Automatisierungen
* Ereignisse
* Protokollierung

Die konkrete Aufteilung in einzelne Services wird später entschieden.

⸻

## 25. Keine direkte Hardwarelogik in der UI

Die Benutzeroberfläche darf keine Hardwarelogik enthalten.

Nicht:

```
Wenn SPS Ausgang 14 = 1
→ Button grün
```

Sondern:

```
Wenn garage.state = OPEN
→ Garagenstatus anzeigen
```

Die Hardwaredetails gehören in die entsprechende Abstraktionsschicht.

⸻

## 26. Trennung von Zuständen und Darstellung

Ein Systemzustand muss unabhängig von seiner Darstellung existieren.

Beispielsweise:

```
garage.state = OPEN
```

kann im Dashboard anders dargestellt werden als auf der Fahrzeugseite.

Der zugrunde liegende Zustand bleibt jedoch identisch.

⸻

## 27. Single Source of Truth

Für jeden wichtigen Systemzustand soll es eine eindeutige Quelle beziehungsweise eine eindeutig definierte Zustandsverwaltung geben.

Die UI soll nicht mehrere widersprüchliche Zustände desselben Geräts führen.

Beispiel:

Die Garage darf nicht gleichzeitig:

Dashboard → geschlossen

und:

Garage-Seite → offen

anzeigen.

⸻

## 28. Zustandsänderungen

Zustandsänderungen müssen nachvollziehbar sein.

Beispiel:

```
20:15:21
Garage → OPENING
20:15:27
Garage → OPEN
```

Diese Informationen können später für Historie und Diagnose genutzt werden.

⸻

## 29. Historische Daten

Kehler OS soll langfristig historische Daten speichern können.

Dazu gehören beispielsweise:

* Energie
* Temperaturen
* Tankfüllstände
* Systemzustände
* Ereignisse
* Warnungen
* Fehler

Die Speicherung muss so aufgebaut sein, dass sie auch über längere Zeiträume performant bleibt.

⸻

## 30. Ereignisprotokoll

Wichtige Ereignisse sollen protokolliert werden können.

Beispiele:

```
Garage geöffnet
Batterie unter 20 %
Landstrom verbunden
SPS offline
Warnung ausgelöst
Warnung behoben
```

⸻

## 31. Diagnoseprotokoll

Zusätzlich zur normalen Ereignishistorie soll es technische Logs geben können.

Diese sind primär für:

* Administratoren
* Wartung
* Fehlersuche
* Entwicklung

gedacht.

Die normale Benutzeroberfläche soll dadurch nicht unnötig kompliziert werden.

⸻

## 32. Netzwerk

Das Kehler-OS-System soll für ein lokales Fahrzeugnetzwerk ausgelegt werden.

Zum Netzwerk gehören unter anderem:

* Gigabit-Switch
* WLAN Access Point
* Raspberry Pi
* SPS
* Victron
* weitere Netzwerkgeräte

Die genaue Netzwerktopologie wird in einem späteren Kapitel behandelt.

⸻

## 33. Lokale Funktionsfähigkeit

Grundlegende Fahrzeugfunktionen sollen möglichst auch dann funktionieren, wenn keine Internetverbindung besteht.

Das Fahrzeug soll nicht davon abhängig sein, dauerhaft mit dem Internet verbunden zu sein.

⸻

## 34. Internet ist Zusatzfunktion

Eine Internetverbindung kann zusätzliche Funktionen ermöglichen.

Beispiele:

* Fernzugriff
* Updates
* Wetterdaten
* Cloud-Synchronisation
* Benachrichtigungen
* Diagnose

Die grundlegende Fahrzeugsteuerung muss jedoch lokal funktionieren.

⸻

## 35. Sicherheit

Die Kommunikation zwischen Komponenten muss abgesichert werden.

Insbesondere Steuerbefehle dürfen nicht unkontrolliert von beliebigen Geräten ausgelöst werden können.

Die konkrete Sicherheitsarchitektur wird später detailliert festgelegt.

⸻

## 36. Berechtigungen

Das System soll grundsätzlich zwischen verschiedenen Benutzerrollen unterscheiden können.

Mindestens denkbar:

```
Administrator
Benutzer
```

Der Administrator kann beispielsweise:

* Systeme konfigurieren
* Geräte verwalten
* Automatisierungen erstellen
* Diagnoseinformationen anzeigen

Normale Benutzer erhalten nur die dafür vorgesehenen Funktionen.

⸻

## 37. Zukunftssicherheit

Die Architektur soll nicht ausschließlich für den aktuellen Ausbau des Wohnmobils entwickelt werden.

Später könnten hinzukommen:

* weitere Sensoren
* weitere Aktoren
* zusätzliche Kameras
* weitere Tanks
* neue Energiekomponenten
* neue Automatisierungen
* zusätzliche Displays

Diese Erweiterungen sollen möglich sein, ohne das gesamte System neu entwickeln zu müssen.

⸻

## 38. Austauschbarkeit

Ein Hardwaregerät sollte grundsätzlich ausgetauscht werden können, ohne dass die gesamte UI neu geschrieben werden muss.

Beispiel:

Victron-Komponente A

kann später durch:

Victron-Komponente B

ersetzt werden.

Solange die logischen Daten und Funktionen weiterhin bereitgestellt werden, bleibt die UI unverändert.

⸻

## 39. Erweiterbare Gerätearchitektur

Neue Geräte sollen nach Möglichkeit über ein einheitliches Schema integriert werden.

Beispiel:

```
Gerät
→ Identität
→ Fähigkeiten
→ Zustände
→ Messwerte
→ Befehle
→ Fehler
```

Dadurch kann Kehler OS langfristig wachsen.

⸻

## 40. Fähigkeiten eines Geräts

Nicht jedes Gerät besitzt dieselben Funktionen.

Ein Gerät soll deshalb beschreiben können, welche Fähigkeiten vorhanden sind.

Beispiel:

```
Garage
Capabilities:
- open
- close
- stop
- position
```

Ein anderes Gerät könnte nur:

```
Capabilities:
- read
```

besitzen.

⸻

## 41. Keine Annahmen über Hardware

Die Software darf nicht einfach davon ausgehen, dass eine bestimmte Funktion vorhanden ist.

Wenn beispielsweise kein Dimmer angeschlossen ist, darf die UI keinen Dimmer als funktionierende Hardware darstellen.

Die Benutzeroberfläche soll sich an den tatsächlich verfügbaren Fähigkeiten orientieren.

⸻

## 42. Fehlerzustände als Teil des Systems

Fehler sind keine Ausnahme, die erst später behandelt wird.

Sie sind ein normaler Bestandteil der Systemarchitektur.

Jedes relevante System muss einen definierten Umgang mit:

* unbekannt
* offline
* Fehler
* veralteten Daten

besitzen.

⸻

## 43. Systemstart

Beim Start von Kehler OS muss das System seine Komponenten initialisieren.

Dabei soll es beispielsweise erkennen:

* welche Geräte verfügbar sind
* welche Dienste laufen
* welche Daten vorhanden sind
* welche Systeme offline sind

Die UI darf während dieser Phase keine falschen Normalwerte anzeigen.

⸻

## 44. Wiederverbindung

Wenn eine Verbindung verloren geht und später wieder verfügbar ist, soll das System automatisch versuchen, die Verbindung wiederherzustellen.

Beispiel:

```
SPS ONLINE
↓
Netzwerkfehler
↓
SPS OFFLINE
↓
Verbindung wiederhergestellt
↓
SPS ONLINE
```

Der Benutzer muss nicht zwingend manuell einen Neustart durchführen.

⸻

## 45. Neustart einzelner Komponenten

Die Architektur soll möglichst erlauben, einzelne Dienste neu zu starten oder neu zu verbinden, ohne das komplette System neu zu starten.

Dies ist besonders für Wartung und Fehlersuche wichtig.

⸻

## 46. Architekturprinzip

Das zentrale Prinzip lautet:

Die UI soll wissen, was ein System tut – aber nicht, wie die Hardware es technisch realisiert.

Beispiel:

Die UI weiß:

Garage ist offen.

Sie muss nicht wissen:

SPS → Eingang X → Netzwerkprotokoll → Datenpunkt Y

⸻

## 47. Zielarchitektur

Konzeptionell soll Kehler OS ungefähr folgende Struktur besitzen:

```
┌──────────────────────────────┐
│          KEHLER OS           │
│        Benutzeroberfläche    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        API / Realtime        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Backend / Services      │
│                              │
│  State Management            │
│  Commands                    │
│  Automation                  │
│  Events                      │
│  Permissions                 │
│  Diagnostics                 │
└───────┬───────────┬──────────┘
        │           │
        ▼           ▼
┌────────────┐ ┌──────────────┐
│    SPS     │ │   Victron    │
└────────────┘ └──────────────┘
        │
        ▼
┌──────────────────────────────┐
│ Sensoren / Aktoren / Geräte  │
└──────────────────────────────┘
```

Dies ist eine konzeptionelle Darstellung.

Die endgültige Architektur und Technologieauswahl erfolgt erst nach vollständiger Anforderungsanalyse.

⸻

## 48. Wichtig für die spätere Entwicklung

Claude soll später nicht einfach möglichst schnell eine Oberfläche programmieren.

Vor der Implementierung muss zunächst überprüft werden:

* Welche Datenquellen existieren?
* Welche Hardware ist vorhanden?
* Welche Protokolle werden verwendet?
* Welche Daten müssen in Echtzeit übertragen werden?
* Welche Daten müssen gespeichert werden?
* Welche Befehle müssen bestätigt werden?
* Welche Systeme müssen unabhängig voneinander funktionieren?
* Welche Sicherheitsanforderungen bestehen?

⸻

## 49. Keine voreilige Technologieentscheidung

Aus diesem Kapitel soll nicht automatisch abgeleitet werden:

„Wir verwenden Technologie X.“

Die Technologieauswahl soll erst erfolgen, nachdem sämtliche Anforderungen bekannt sind.

Die Lösung soll anhand von:

* Stabilität
* Performance
* Wartbarkeit
* Sicherheit
* Erweiterbarkeit
* Hardwarekompatibilität
* Offline-Fähigkeit

ausgewählt werden.

⸻

## 50. Zielbild

Die technische Architektur von Kehler OS soll genauso professionell sein wie die Benutzeroberfläche.

Für den Benutzer soll das System einfach wirken.

Im Hintergrund darf die Architektur jedoch hochgradig strukturiert und technisch anspruchsvoll sein.

Das Ziel ist:

```
Komplexes System
        ↓
klare Abstraktion
        ↓
einfache Bedienung
```

⸻

## Ende Kapitel 10

Dieses Kapitel definiert die grundlegenden Architekturprinzipien von Kehler OS.

Es legt insbesondere fest:

* Trennung von UI und Hardware
* zentrale Kommunikationsschicht
* logische Geräte und Zustände
* Echtzeitkommunikation
* Fehlerbehandlung
* historische Daten
* Ereignisse
* Offline-Fähigkeit
* Erweiterbarkeit
* Sicherheitsgrundlagen
* Hardwareabstraktion

Die konkrete Technologieauswahl wird erst nach Abschluss der gesamten Anforderungsdefinition getroffen.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf das nächste Kapitel.

Verwende Kapitel 1 bis 10 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
