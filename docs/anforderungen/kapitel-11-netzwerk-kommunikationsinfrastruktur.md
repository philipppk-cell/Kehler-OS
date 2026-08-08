# KEHLER OS

# Kapitel 11 – Netzwerk- und Kommunikationsinfrastruktur

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel beschreibt die Netzwerk- und Kommunikationsinfrastruktur, auf der Kehler OS später betrieben wird.

Die konkrete Technologie- und Protokollauswahl wird erst nach vollständiger Analyse aller Anforderungen getroffen.

Verwende Kapitel 1–11 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Grundprinzip des Fahrzeugnetzwerks

Kehler OS benötigt ein eigenes lokales Netzwerk innerhalb des Wohnmobils.

Dieses Netzwerk verbindet die verschiedenen technischen Komponenten miteinander.

Dazu gehören insbesondere:

* Kehler-OS-Rechner
* Raspberry Pi
* Siemens SPS
* Victron-System
* Kameras
* WLAN Access Point
* Netzwerk-Switch
* zukünftige Netzwerkgeräte
* Bediengeräte

Das Fahrzeugnetzwerk soll unabhängig vom Internet funktionieren.

⸻

## 2. Lokales Netzwerk als Grundlage

Das lokale Netzwerk ist das zentrale Kommunikationsmedium des Fahrzeugs.

Die wichtigsten Systeme sollen auch dann miteinander kommunizieren können, wenn keine Internetverbindung besteht.

Beispiel:

```
Internet
   X
   │
   │ nicht erforderlich
   │
┌──▼────────────────────────────┐
│       KEHLER OS LAN           │
│                               │
│ Raspberry Pi                  │
│ SPS                           │
│ Victron                       │
│ Kameras                       │
│ HMI / iPad                    │
└───────────────────────────────┘
```

⸻

## 3. Gigabit-Switch

Im Fahrzeug ist ein Gigabit-Switch vorgesehen.

Der Switch bildet einen zentralen Punkt des kabelgebundenen Netzwerks.

Mögliche angeschlossene Komponenten:

* Raspberry Pi
* SPS
* Victron
* Kameras
* WLAN Access Point
* weitere Ethernet-Geräte

Die konkrete Anzahl der Ports muss ausreichend Reserve für zukünftige Erweiterungen besitzen.

⸻

## 4. WLAN Access Point

Ein WLAN Access Point stellt die drahtlose Verbindung für mobile Bediengeräte bereit.

Beispielsweise:

* iPad
* Smartphone
* Laptop
* weitere Tablets

Der Access Point ist Teil des lokalen Kehler-OS-Netzwerks.

⸻

## 5. WLAN und Ethernet

Kehler OS soll beide Netzwerkarten berücksichtigen:

### Ethernet

Für kritische und stationäre Komponenten:

* SPS
* Raspberry Pi
* Victron
* Kameras
* weitere Steuergeräte

### WLAN

Primär für:

* iPad
* Smartphones
* Laptops
* mobile Bediengeräte

Wenn eine Komponente technisch zuverlässig per Ethernet betrieben werden kann, soll dies für kritische Systeme bevorzugt werden.

⸻

## 6. Netzwerkstabilität

Das Fahrzeugnetzwerk muss für einen dauerhaft laufenden Betrieb ausgelegt sein.

Es soll nicht davon ausgegangen werden, dass das Netzwerk regelmäßig neu gestartet wird.

Daher sind insbesondere wichtig:

* stabile Verbindungen
* automatische Wiederverbindung
* saubere Fehlererkennung
* definierte Timeouts
* Überwachung der Netzwerkgeräte

⸻

## 7. Internetverbindung

Das Fahrzeug kann über eine externe Internetverbindung verfügen.

Diese kann beispielsweise über:

* Mobilfunk
* WLAN
* andere zukünftige Internetzugänge

bereitgestellt werden.

Die Internetverbindung ist jedoch nicht Bestandteil der grundlegenden Fahrzeugsteuerung.

⸻

## 8. Internet ist nicht Voraussetzung

Wenn das Internet ausfällt, müssen grundlegende Funktionen weiterhin funktionieren.

Beispiele:

* Licht
* Wasser
* Klima
* Fahrzeugfunktionen
* Garage
* Nivellierung
* Energieüberwachung
* lokale Kameras

sofern die jeweilige Hardware selbst verfügbar ist.

⸻

## 9. Externe Dienste

Internetabhängige Funktionen müssen klar von lokalen Funktionen getrennt werden.

Beispiele für mögliche Internetfunktionen:

* Wetter
* Fernzugriff
* Benachrichtigungen
* Cloud-Synchronisation
* Softwareupdates
* Remote-Diagnose

Fällt das Internet aus, darf dies nicht automatisch einen Fehler im gesamten Kehler OS verursachen.

⸻

## 10. Netzwerkstruktur

Die genaue Netzwerktopologie wird später festgelegt.

Konzeptionell kann sie ungefähr so aussehen:

```
                 INTERNET
                    │
             Internet Router
                    │
                    ▼
             ┌─────────────┐
             │    LAN      │
             │   Router    │
             └──────┬──────┘
                    │
             ┌──────▼──────┐
             │   GIGABIT   │
             │   SWITCH    │
             └──┬──┬──┬───┘
                │  │  │
        ┌───────┘  │  └─────────┐
        │          │            │
        ▼          ▼            ▼
    Raspberry     SPS         Victron
        │
        │
        ▼
  Kehler OS Backend
        Switch
           │
           ▼
      WLAN Access Point
           │
       ┌───┴────┐
       ▼        ▼
     iPad    Smartphone
```

Dies ist nur ein konzeptionelles Modell.

Die tatsächliche Topologie wird später bestimmt.

⸻

## 11. IP-Adressen

Die Netzwerkarchitektur soll eine strukturierte IP-Adressierung verwenden.

Geräte sollen nicht zufällig irgendwelche Adressen erhalten, die später schwer nachvollziehbar sind.

Die genaue IP-Struktur wird bei der technischen Implementierung festgelegt.

⸻

## 12. Statische Geräte

Für wichtige Infrastrukturkomponenten können feste beziehungsweise reservierte IP-Adressen vorgesehen werden.

Beispielsweise:

```
Raspberry Pi
SPS
Victron
Kameras
Netzwerkgeräte
```

Dadurch werden Verbindungen zuverlässiger und einfacher zu diagnostizieren.

⸻

## 13. DHCP

Mobile beziehungsweise normale Clients können über DHCP adressiert werden.

Beispielsweise:

* iPad
* Smartphone
* Laptop

Die genaue DHCP-Architektur wird später definiert.

⸻

## 14. Namensauflösung

Kehler OS soll nach Möglichkeit nicht ausschließlich von IP-Adressen abhängig sein.

Geräte können über eindeutige Hostnamen beziehungsweise logische Namen erreichbar sein.

Beispiel:

```
kehler-os
plc
victron
camera-rear
camera-garage
```

Die endgültige Namenskonvention wird später festgelegt.

⸻

## 15. Netzwerküberwachung

Kehler OS soll den Zustand wichtiger Netzwerkkomponenten überwachen können.

Beispiele:

```
Raspberry Pi
ONLINE
SPS
ONLINE
Victron
ONLINE
Kamera 3
OFFLINE
```

⸻

## 16. Netzwerkfehler

Ein Netzwerkfehler muss eindeutig erkannt werden.

Mögliche Zustände:

```
ONLINE
DEGRADED
OFFLINE
RECONNECTING
UNKNOWN
```

Die Benutzeroberfläche soll daraus verständliche Informationen erzeugen.

⸻

## 17. Automatische Wiederverbindung

Wenn eine Netzwerkverbindung verloren geht, soll das System automatisch versuchen, sie wiederherzustellen.

Beispiel:

```
ONLINE
   ↓
Verbindung verloren
   ↓
RECONNECTING
   ↓
Verbindung wiederhergestellt
   ↓
ONLINE
```

Der Benutzer soll nicht zwingend manuell eingreifen müssen.

⸻

## 18. Netzwerküberlastung

Das System muss vermeiden, dass einzelne Komponenten unnötig viel Netzwerkbandbreite verbrauchen.

Besonders relevant sind:

* Kamerastreams
* historische Daten
* große Dateien
* Updates

Steuerbefehle und wichtige Statusinformationen müssen gegenüber nichtkritischem Datenverkehr priorisiert werden können, sofern dies technisch erforderlich ist.

⸻

## 19. Kameranetzwerk

Kameras können erhebliche Netzwerkbandbreite benötigen.

Daher soll die Architektur Kamerastreams berücksichtigen.

Die Kameraübertragung darf nicht dazu führen, dass die Kommunikation mit:

* SPS
* Victron
* Steuerung
* Backend

beeinträchtigt wird.

⸻

## 20. Echtzeitkommunikation

Nicht alle Daten benötigen dieselbe Aktualisierungsrate.

Beispielsweise:

### Sehr schnell

* Nivellierung
* Bewegungszustände
* sicherheitsrelevante Zustände

### Normal

* Licht
* Türen
* Garage
* Temperaturen

### Langsam

* Tankfüllstände
* historische Daten
* Wartungsinformationen

Die Architektur soll diese Unterschiede berücksichtigen.

⸻

## 21. Kommunikationsprotokolle

Die endgültige Auswahl der Kommunikationsprotokolle wird erst nach der Analyse der tatsächlich vorhandenen Hardware getroffen.

Mögliche Technologien können beispielsweise sein:

* Ethernet-basierte SPS-Kommunikation
* APIs
* MQTT
* WebSocket
* HTTP
* TCP/IP
* weitere geeignete Protokolle

Es soll nicht automatisch ein bestimmtes Protokoll verwendet werden, nur weil es bekannt oder einfach zu implementieren ist.

⸻

## 22. Protokollabstraktion

Die UI darf nicht wissen, welches Protokoll verwendet wird.

Beispiel:

Die UI sendet logisch:

```
garage.open
```

Die darunterliegende Kommunikationsschicht entscheidet, wie dieser Befehl übertragen wird.

⸻

## 23. Mehrere Kommunikationswege

Ein System kann gegebenenfalls mehrere Kommunikationswege besitzen.

Beispiel:

```
Kehler OS
   │
   ├── SPS
   │
   ├── Victron
   │
   └── Kamera-System
```

Jeder Kommunikationsweg darf seine eigene technische Implementierung besitzen.

Nach außen soll jedoch eine konsistente Systemarchitektur entstehen.

⸻

## 24. Kommunikation zwischen Backend und UI

Die Benutzeroberfläche soll nicht permanent Hardwaregeräte einzeln abfragen.

Stattdessen kommuniziert sie mit der zentralen Systemlogik.

Beispiel:

```
Hardware
   ↓
Backend
   ↓
aktueller Zustand
   ↓
UI
```

Dadurch bleibt die UI unabhängig von der konkreten Hardware.

⸻

## 25. Echtzeit-Updates an die UI

Wenn sich ein relevanter Zustand ändert, soll die UI möglichst unmittelbar aktualisiert werden.

Beispiel:

```
Garage CLOSED
       ↓
Sensoränderung
       ↓
Backend erkennt OPENING
       ↓
UI erhält Ereignis
       ↓
Fahrzeuganimation startet
```

⸻

## 26. Verbindung des iPads

Das iPad dient als wichtiges Bediengerät.

Es verbindet sich mit dem lokalen Kehler-OS-Netzwerk.

Das iPad soll auf die Kehler-OS-Oberfläche zugreifen können, ohne dass hierfür eine Internetverbindung notwendig ist.

⸻

## 27. Mehrere Bediengeräte

Die Architektur soll mehrere Clients ermöglichen.

Beispielsweise:

```
iPad
Smartphone
Laptop
zweites Tablet
```

Alle Clients sollen denselben tatsächlichen Fahrzeugzustand sehen.

⸻

## 28. Synchronisation

Wenn zwei Geräte gleichzeitig geöffnet sind, müssen sie konsistent bleiben.

Beispiel:

Auf dem iPad wird das Außenlicht eingeschaltet.

Das Smartphone soll anschließend ebenfalls:

```
Außenlicht
EIN
```

anzeigen.

⸻

## 29. Gleichzeitige Befehle

Wenn mehrere Clients gleichzeitig Befehle senden, muss die Systemlogik einen konsistenten Zustand gewährleisten.

Die UI darf nicht selbst versuchen, Konflikte zu lösen.

Dies gehört zur zentralen Systemlogik.

⸻

## 30. Zugriffskontrolle

Nicht jedes Netzwerkgerät soll automatisch sämtliche Steuerfunktionen ausführen dürfen.

Die Architektur muss später Möglichkeiten für:

* Authentifizierung
* Autorisierung
* Sessions
* Rollen
* sichere Verbindungen

vorsehen.

⸻

## 31. Lokale Sicherheit

Da Kehler OS physische Systeme steuern kann, muss die lokale Netzwerksicherheit ernst genommen werden.

Ein Gerät im Netzwerk darf nicht automatisch vollständigen Zugriff auf alle Fahrzeugfunktionen erhalten.

⸻

## 32. Trennung von Netzwerk und Berechtigungen

Netzwerkzugriff bedeutet nicht automatisch Steuerberechtigung.

Beispiel:

```
Gerät im WLAN
        ≠
Administrator
```

Die Berechtigungslogik muss separat bestehen.

⸻

## 33. Ausfallsicherheit

Ein einzelner Fehler darf möglichst keine vollständige Systemstörung verursachen.

Beispiel:

Wenn das WLAN ausfällt:

iPad nicht erreichbar

müssen trotzdem weiterhin funktionieren:

```
SPS
Victron
Backend
lokale Automatisierungen
```

sofern diese über das kabelgebundene Netzwerk erreichbar sind.

⸻

## 34. Switch-Ausfall

Wenn der zentrale Switch ausfällt, kann dies mehrere Systeme gleichzeitig betreffen.

Daher soll die Netzwerkarchitektur bei der Planung berücksichtigen:

* zuverlässige Hardware
* Stromversorgung
* Neustartverhalten
* Diagnose
* gegebenenfalls Redundanz, sofern sinnvoll

⸻

## 35. Stromversorgung des Netzwerks

Netzwerkkomponenten sind Teil der Fahrzeugtechnik und müssen entsprechend zuverlässig mit Strom versorgt werden.

Besonders relevant:

* Switch
* WLAN Access Point
* Raspberry Pi
* Router
* Kameras

Die Netzwerkkomponenten sollen bei einem normalen Fahrzeugbetrieb nicht unnötig abgeschaltet werden.

⸻

## 36. UPS

Eine unterbrechungsfreie Stromversorgung beziehungsweise entsprechende Pufferung kann für kritische Netzwerk- und Computersysteme vorgesehen werden.

Dies ist besonders relevant für:

* Raspberry Pi
* Netzwerk
* zentrale Steuerung
* Datenspeicher

Die konkrete Umsetzung wird später entschieden.

⸻

## 37. Neustartverhalten

Nach einem Stromausfall sollen die relevanten Systeme möglichst automatisch wieder hochfahren.

Die Reihenfolge muss bei der späteren Implementierung berücksichtigt werden.

Beispielsweise:

```
Stromversorgung
↓
Netzwerk
↓
Raspberry Pi
↓
Backend
↓
Kommunikationsdienste
↓
UI
```

⸻

## 38. Systemstart und Netzwerk

Kehler OS darf beim Start nicht davon ausgehen, dass sämtliche Geräte sofort verfügbar sind.

Beispielsweise kann:

Raspberry Pi ONLINE

sein, während:

SPS noch nicht erreichbar

ist.

Das System muss mit diesem Zustand umgehen können.

⸻

## 39. Netzwerkdiagnose

Eine spätere Diagnoseansicht soll Informationen wie folgende anzeigen können:

* IP-Adresse
* Verbindung
* Latenz
* Erreichbarkeit
* Verbindungsdauer
* Fehler
* Kommunikationsstatus

Diese Informationen sind primär für Diagnosezwecke gedacht.

⸻

## 40. Monitoring

Wichtige Komponenten sollen überwacht werden.

Beispielsweise:

```
SPS
ONLINE
Victron
ONLINE
Raspberry Pi
ONLINE
Kamera
OFFLINE
```

⸻

## 41. Ereignisse

Netzwerkereignisse können für die Systemhistorie relevant sein.

Beispiele:

```
18:43
Kamera 2 offline
18:44
Kamera 2 wieder online
```

Dadurch kann später nachvollzogen werden, ob ein Problem dauerhaft oder nur vorübergehend war.

⸻

## 42. Keine Abhängigkeit von Cloud-Systemen

Kehler OS soll nicht grundsätzlich auf externe Cloudserver angewiesen sein.

Die zentrale Fahrzeugsteuerung muss lokal funktionieren.

Cloud-Funktionen sind optionale Erweiterungen.

⸻

## 43. Remote-Zugriff

Ein späterer Remote-Zugriff kann vorgesehen werden.

Beispielsweise könnte der Benutzer außerhalb des Fahrzeugs:

* Systemstatus überprüfen
* Warnungen sehen
* bestimmte Informationen abrufen
* Diagnoseinformationen einsehen

Die Fernsteuerung kritischer Fahrzeugfunktionen muss jedoch besonders abgesichert werden.

⸻

## 44. Sicherheitsprinzip für Remote-Zugriff

Ein späterer Fernzugriff darf nicht einfach bedeuten:

```
Internet
↓
direkter Zugriff auf SPS
```

Stattdessen muss eine kontrollierte und abgesicherte Systemarchitektur verwendet werden.

⸻

## 45. Netzwerkarchitektur muss erweiterbar sein

Das Netzwerk soll zukünftige Komponenten aufnehmen können.

Beispielsweise:

* zusätzliche Kameras
* weitere Sensoren
* zusätzliche Displays
* NAS
* neue Steuergeräte
* Diagnosegeräte

⸻

## 46. NAS

Ein NAS kann später Teil der Fahrzeugnetzwerkinfrastruktur sein.

Mögliche Aufgaben:

* Datenarchiv
* Backups
* Medien
* Kameraaufzeichnungen
* Systemdaten

Das NAS ist jedoch kein zwingender Bestandteil der grundlegenden Kehler-OS-Steuerung.

⸻

## 47. Datenverkehr priorisieren

Kritische Kommunikation muss gegenüber nichtkritischen Daten bevorzugt behandelt werden können.

Beispielsweise ist:

```
Garage → OPEN
```

wichtiger als:

```
Video-Stream → hohe Auflösung
```

Die konkrete Priorisierung wird später technisch festgelegt.

⸻

## 48. Zielarchitektur

Das konzeptionelle Ziel lautet:

```
                    INTERNET
                       │
                 ┌─────▼─────┐
                 │   Router  │
                 └─────┬─────┘
                       │
                 ┌─────▼─────┐
                 │  Switch   │
                 └─────┬─────┘
          ┌────────────┼─────────────┐
          │            │             │
          ▼            ▼             ▼
     Raspberry Pi     SPS         Victron
          │
          ├──────── Kameras
          │
          └──────── Backend
                       │
                 ┌─────▼─────┐
                 │ WLAN AP   │
                 └─────┬─────┘
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
             iPad   Smartphone  Laptop
```

Dies ist eine konzeptionelle Darstellung und keine endgültige Netzwerkkonfiguration.

⸻

## 49. Grundsatz

Das Netzwerk soll für den Benutzer unsichtbar sein.

Der Benutzer soll sich nicht darum kümmern müssen:

* ob Ethernet oder WLAN verwendet wird
* welche IP-Adresse ein Gerät besitzt
* welches Protokoll verwendet wird
* ob ein Dienst neu verbunden werden musste

Kehler OS soll diese technische Komplexität abstrahieren.

⸻

## 50. Zielbild

Das Netzwerk bildet das technische Nervensystem des Fahrzeugs.

Es verbindet:

```
Sensoren
↓
Steuerungen
↓
Backend
↓
Kehler OS
↓
Benutzer
```

Alle Komponenten müssen dabei zuverlässig, nachvollziehbar und möglichst unabhängig voneinander funktionieren.

⸻

## Ende Kapitel 11

Dieses Kapitel definiert die grundlegenden Anforderungen an das Netzwerk von Kehler OS.

Festgelegt wurden insbesondere:

* lokales Fahrzeugnetzwerk
* Gigabit-Switch
* WLAN Access Point
* Ethernet für wichtige stationäre Systeme
* WLAN für mobile Clients
* lokale Funktionsfähigkeit ohne Internet
* automatische Wiederverbindung
* Netzwerküberwachung
* mehrere Bediengeräte
* zentrale Kommunikation über das Backend
* Trennung von Netzwerkzugriff und Berechtigungen
* Erweiterbarkeit
* Ausfallsicherheit
* mögliche spätere Remote-Funktionen

Die konkrete Auswahl von:

* Router
* Switch
* Access Point
* Netzwerksegmentierung
* IP-Bereichen
* Protokollen
* Sicherheitsmechanismen
* Remote-Zugriff

wird erst nach Abschluss der vollständigen Anforderungsanalyse festgelegt.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf das nächste Kapitel.

Verwende Kapitel 1 bis 11 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
