# KEHLER OS

# Kapitel 17 – Performance, Stabilität, Fehlerbehandlung, Deployment und Zukunftssicherheit

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel definiert die nichtfunktionalen Qualitätsanforderungen von Kehler OS: Performance, Stabilität, Ausfallsicherheit, Deployment, Wartbarkeit, Updates, Testbarkeit und langfristige Erweiterbarkeit.

Verwende Kapitel 1–17 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel

Kehler OS soll nicht nur funktional sein.

Es soll dauerhaft zuverlässig laufen.

Das System soll sich so verhalten, wie man es von einem professionellen Fahrzeug-HMI erwartet.

Das bedeutet insbesondere:

* schnelle Reaktion
* stabile Dauerfunktion
* kontrolliertes Fehlerverhalten
* kurze Wiederanlaufzeit
* einfache Wartung
* klare Diagnose
* sichere Updates
* langfristige Erweiterbarkeit

⸻

## 2. Dauerbetrieb

Kehler OS ist für einen dauerhaften Betrieb im Fahrzeug vorgesehen.

Das System darf nicht davon ausgehen, dass es jeden Tag neu gestartet wird.

Ein Betrieb über:

* Tage
* Wochen
* Monate

muss möglich sein.

⸻

## 3. Keine regelmäßigen Neustarts als Lösung

Ein Neustart darf nicht als normales Mittel gegen:

* Speicherprobleme
* hängende Prozesse
* Verbindungsprobleme
* langsame Performance

verwendet werden.

Solche Ursachen müssen technisch sauber behoben werden.

⸻

## 4. Performance-Ziel

Die Benutzeroberfläche soll sich jederzeit unmittelbar anfühlen.

Normale Benutzeraktionen sollen ohne spürbare Verzögerung reagieren.

Beispiele:

```
Seite öffnen
→ praktisch unmittelbar
Licht schalten
→ sofortige UI-Rückmeldung
Statusänderung
→ zeitnah sichtbar
```

⸻

## 5. UI-Reaktionszeit

Die UI soll auf Touch-Eingaben sofort visuell reagieren.

Auch wenn die reale Hardware noch keine Rückmeldung geliefert hat, soll der Benutzer erkennen können:

Befehl wird verarbeitet

Die endgültige Zustandsanzeige erfolgt erst nach Hardwarebestätigung.

⸻

## 6. Rendering

Animationen und Übergänge müssen flüssig laufen.

Die zentrale Fahrzeugdarstellung darf nicht dazu führen, dass:

* das Dashboard ruckelt
* Touch-Eingaben verzögert werden
* andere Komponenten blockieren

⸻

## 7. Zielbild für Animationen

Animationen sollen hochwertig wirken.

Sie dürfen aber niemals wichtiger sein als:

* korrekte Daten
* schnelle Bedienung
* geringe Systemlast

Wenn eine komplexere Animation die Performance deutlich verschlechtert, muss eine leichtere Variante gewählt werden.

⸻

## 8. Progressive Enhancement

Nicht jede visuelle Funktion muss zwingend auf jedem Client identisch aufwendig dargestellt werden.

Ein leistungsstarker Hauptclient kann umfangreichere Animationen verwenden.

Ein schwächeres Gerät kann dieselben Informationen mit reduzierten Effekten anzeigen.

Die Funktionalität bleibt identisch.

⸻

## 9. Backend-Performance

Das Backend muss mehrere Aufgaben gleichzeitig verarbeiten können.

Beispiele:

* SPS-Kommunikation
* Victron-Daten
* API
* WebSockets
* Automatisierungen
* Datenbank
* Historie
* Diagnose
* mehrere Clients

Keine einzelne Aufgabe darf unnötig das gesamte System blockieren.

⸻

## 10. Asynchrone Verarbeitung

Lang laufende oder externe Vorgänge sollen, wo sinnvoll, asynchron verarbeitet werden.

Beispiele:

* Hardwarekommunikation
* Datenbankzugriffe
* Backups
* Updates
* historische Auswertungen

Die konkrete Technologie wird später ausgewählt.

⸻

## 11. Keine blockierenden Hardwareaufrufe im UI-Pfad

Wenn eine Hardwarekomponente langsam antwortet, darf dies die Benutzeroberfläche nicht einfrieren.

Konzeptionell:

```
UI
↓
Command
↓
Backend verarbeitet unabhängig
↓
Hardware
```

⸻

## 12. Ressourcen

Der Raspberry Pi besitzt begrenzte Ressourcen.

Kehler OS muss diese bewusst verwenden.

Zu berücksichtigen sind:

* CPU
* RAM
* Datenträger
* I/O
* Netzwerk
* Temperatur

⸻

## 13. Keine unnötig schwere Architektur

Professionell bedeutet nicht automatisch maximal komplex.

Claude soll später keine überdimensionierte Cloud-/Enterprise-Architektur bauen, wenn diese auf einem Raspberry Pi keinen sinnvollen Mehrwert bietet.

⸻

## 14. Modular, aber nicht fragmentiert

Die Software soll modular sein.

Es sollen jedoch nicht unnötig dutzende unabhängige Dienste erzeugt werden, wenn dies:

* Wartung erschwert
* Ressourcen verbraucht
* Fehlerquellen erhöht

Die Architektur muss zum realen Fahrzeug passen.

⸻

## 15. Modularer Monolith versus Services

Die endgültige Aufteilung zwischen:

* modularer Anwendung
* mehreren Prozessen
* eigenständigen Services

soll nach den tatsächlichen Anforderungen gewählt werden.

Es ist nicht vorgeschrieben, dass Kehler OS eine Microservice-Architektur verwendet.

⸻

## 16. Stabilität

Jeder Dienst muss Fehler kontrolliert behandeln.

Ein unerwarteter Fehler in einem einzelnen Prozess darf möglichst nicht das gesamte System herunterreißen.

⸻

## 17. Fehlergrenzen

Module sollen klar voneinander abgegrenzt sein.

Beispiel:

```
Kamera-Service ERROR
```

darf nicht automatisch bedeuten:

```
Lichtsteuerung ERROR
```

⸻

## 18. Graceful Degradation

Bei Teilfehlern soll Kehler OS soweit wie möglich funktionsfähig bleiben.

Beispiel:

```
Internet OFFLINE
```

aber:

```
SPS ONLINE
Victron ONLINE
Licht funktioniert
Wasser funktioniert
Klima funktioniert
```

⸻

## 19. Fehlerkaskaden vermeiden

Ein Fehler darf nicht unnötig weitere Systeme zum Absturz bringen.

Beispiel:

Eine fehlende Wetter-API darf nicht dazu führen, dass das Dashboard überhaupt nicht lädt.

⸻

## 20. Exception Handling

Fehler dürfen nicht still verschluckt werden.

Ein Fehler muss:

* erkannt
* korrekt klassifiziert
* protokolliert
* gegebenenfalls angezeigt

werden.

⸻

## 21. Benutzerfehler versus Systemfehler

Kehler OS soll zwischen verschiedenen Fehlerarten unterscheiden.

Beispiel:

Ungültige Benutzereingabe

ist etwas anderes als:

SPS-Verbindung verloren

⸻

## 22. Fehlerdarstellung

Fehlermeldungen müssen für den jeweiligen Benutzer verständlich sein.

Normaler Benutzer:

```
Garagentor konnte nicht geöffnet werden.
```

Diagnose:

```
Command timeout after X ms
PLC connection healthy
No state transition detected
```

⸻

## 23. Retry

Temporäre Fehler können automatisch erneut versucht werden.

Beispiele:

* Netzwerkverbindung
* externe API
* bestimmte Lesefunktionen

Retries müssen begrenzt und kontrolliert sein.

⸻

## 24. Exponential Backoff

Bei wiederholten Verbindungsfehlern soll geprüft werden, ob ein Backoff-Verfahren sinnvoll ist.

Dadurch wird verhindert, dass ein ausgefallenes Gerät permanent mit Anfragen überflutet wird.

⸻

## 25. Circuit Breaker

Für geeignete externe Schnittstellen kann ein Circuit-Breaker-Prinzip sinnvoll sein.

Wenn ein System dauerhaft nicht erreichbar ist, muss nicht jede Millisekunde ein neuer Verbindungsversuch erfolgen.

⸻

## 26. Hardwarebefehle

Retries bei physischen Befehlen erfordern besondere Vorsicht.

Beispiel:

```
garage.open
```

darf nicht blind mehrfach gesendet werden, wenn unklar ist, ob der erste Befehl bereits ausgeführt wurde.

⸻

## 27. Idempotente Befehle bevorzugen

Wo technisch möglich, sollen explizite Zielzustände bevorzugt werden.

Beispiel:

```
set_light_state(ON)
```

ist robuster als:

```
toggle_light()
```

⸻

## 28. Startsequenz

Der Systemstart muss kontrolliert erfolgen.

Beispiel:

```
Betriebssystem
↓
Systemdienste
↓
Datenbank
↓
Hardwareadapter
↓
State Synchronisation
↓
Automation Engine
↓
Frontend
```

Die genaue Reihenfolge wird später festgelegt.

⸻

## 29. Readiness

Kehler OS soll erst dann einen vollständig normalen Systemstatus anzeigen, wenn die dafür erforderlichen Komponenten betriebsbereit sind.

⸻

## 30. Teilweise betriebsbereit

Während des Starts kann beispielsweise angezeigt werden:

```
KEHLER OS STARTET
SPS        ONLINE
Victron    VERBINDET
Kameras    2/4 ONLINE
```

Das System muss nicht auf jedes optionale Gerät warten, bevor es bedienbar wird.

⸻

## 31. Bootscreen

Kehler OS soll einen eigenen hochwertigen Boot-/Startbildschirm besitzen.

Das Design muss zum definierten Designsystem passen.

Er soll nicht wie ein Raspberry-Pi-Desktop oder Standard-Linux-Start wirken.

⸻

## 32. Kein Desktop im normalen Betrieb

Auf dem Hauptsystem soll der Benutzer im normalen Betrieb möglichst nie einen Linux-Desktop, Terminal oder Browser-Chrome sehen.

Kehler OS soll wie ein eigenständiges System erscheinen.

⸻

## 33. Kiosk-/App-Modus

Das Hauptdisplay soll so betrieben werden können, dass Kehler OS automatisch im vorgesehenen Vollbildmodus startet.

Die genaue technische Umsetzung wird später entschieden.

⸻

## 34. Automatischer Dienststart

Backend und andere zentrale Dienste müssen automatisch mit dem System starten.

Manuelle Terminalbefehle sind im normalen Betrieb nicht akzeptabel.

⸻

## 35. Dienstüberwachung

Zentrale Dienste sollen durch geeignete Mechanismen überwacht werden.

Wenn ein Dienst unerwartet abstürzt, kann ein automatischer kontrollierter Neustart sinnvoll sein.

⸻

## 36. Neustartgrenzen

Ein ständig abstürzender Dienst darf nicht endlos im Sekundentakt neugestartet werden.

Das System muss einen dauerhaften Fehlerzustand erkennen.

⸻

## 37. Crash Loop

Ein Crash Loop soll diagnostizierbar sein.

Beispiel:

```
Automation Engine
5 Neustarts in 2 Minuten
STATUS:
ERROR
```

⸻

## 38. Watchdog

Wo sinnvoll können Software- oder Hardware-Watchdogs verwendet werden.

Der Watchdog darf jedoch keine gefährliche Systemaktion auslösen.

⸻

## 39. Stromausfall

Kehler OS muss mit unerwartetem Spannungsverlust umgehen können.

Besonders geschützt werden sollen:

* Datenbank
* Konfiguration
* Dateisystem
* wichtige Logs

⸻

## 40. UPS beziehungsweise Pufferung

Für Raspberry Pi und zentrale Netzwerkkomponenten kann eine Strompufferung sinnvoll sein.

Wenn eine solche Hardware vorhanden ist, soll Kehler OS deren Zustand später berücksichtigen können.

⸻

## 41. Controlled Shutdown

Bei bevorstehendem Verlust der Versorgung kann das System gegebenenfalls kontrolliert herunterfahren.

Die konkrete Umsetzung hängt von der verwendeten Stromversorgung ab.

⸻

## 42. Datenkonsistenz nach Absturz

Nach einem unerwarteten Neustart muss die Software prüfen:

* Datenbankzustand
* Migrationen
* Konfiguration
* Hardwarezustand

Alte Live-Zustände dürfen nicht blind übernommen werden.

⸻

## 43. Recovery

Kehler OS soll nach einem Absturz möglichst automatisch wieder betriebsbereit werden.

Der normale Benutzer soll nicht erst:

* SSH öffnen
* Prozesse starten
* Konfigurationsdateien reparieren

müssen.

⸻

## 44. Safe Mode

Für schwere Fehler kann ein spezieller Safe-/Recovery-Modus sinnvoll sein.

Dieser könnte beispielsweise nur:

* Diagnose
* Backup
* Restore
* Updates
* grundlegende Einstellungen

bereitstellen.

⸻

## 45. Safe Mode ist kein normaler Modus

Ein solcher Zustand muss deutlich gekennzeichnet werden.

⸻

## 46. Deployment

Die Installation von Kehler OS muss reproduzierbar sein.

Das System soll nicht nur auf genau einem Raspberry Pi funktionieren, weil dort irgendwann manuell Dateien kopiert wurden.

⸻

## 47. Reproduzierbare Installation

Es soll möglich sein, einen neuen Rechner kontrolliert in denselben Softwarezustand zu bringen.

Dazu gehören:

* Betriebssystemvoraussetzungen
* Kehler-OS-Version
* Abhängigkeiten
* Dienste
* Konfiguration
* Datenbank

⸻

## 48. Konfiguration vom Code trennen

Fahrzeugspezifische Werte sollen nicht unnötig fest im Code stehen.

Beispiele:

* Tankkapazität
* SPS-Mapping
* Gerätenamen
* Sensorgrenzen
* Räume

gehören zur Konfiguration.

⸻

## 49. Umgebungsabhängige Konfiguration

Das System soll zwischen Umgebungen unterscheiden können.

Beispiele:

```
DEVELOPMENT
SIMULATION
PRODUCTION
```

⸻

## 50. Produktionskonfiguration

Die Produktionsumgebung muss klar als reale Fahrzeugumgebung erkennbar sein.

⸻

## 51. Deployment-Version

Jede installierte Kehler-OS-Version muss eindeutig identifizierbar sein.

Beispiel:

```
Kehler OS
Version 1.4.2
```

Die endgültige Versionsstrategie wird später definiert.

⸻

## 52. Versionsinformationen

Zusätzlich können intern relevant sein:

* Build
* Commit
* Datenbankschema
* Konfigurationsversion

Diese Informationen sind primär für Diagnose und Entwicklung gedacht.

⸻

## 53. Semantic Versioning

Claude soll später prüfen, ob ein etabliertes Versionierungsschema wie Semantic Versioning zum Projekt passt.

Es muss jedoch sinnvoll und konsistent angewendet werden.

⸻

## 54. Updates

Kehler OS muss aktualisierbar sein.

Ein Update soll kontrolliert und nachvollziehbar erfolgen.

⸻

## 55. Updateprüfung

Vor einem Update können Prüfungen notwendig sein.

Beispiele:

* genügend Speicher
* Stromversorgung stabil
* keine kritische Fahrzeugaktion aktiv
* Backup vorhanden
* Version kompatibel

⸻

## 56. Kein Update während kritischer Bewegung

Ein Update darf nicht mitten während einer laufenden hydraulischen oder anderen relevanten Fahrzeugaktion gestartet werden.

⸻

## 57. Update-Phasen

Konzeptionell:

```
Update gefunden
↓
Download
↓
Verifikation
↓
Backup / Checkpoint
↓
Installation
↓
Migration
↓
Neustart
↓
Health Check
↓
Erfolg oder Rollback
```

⸻

## 58. Update-Verifikation

Softwarepakete beziehungsweise Updates müssen gegen Beschädigung oder Manipulation geprüft werden können.

Die konkrete technische Methode wird später anhand der Deploymentarchitektur festgelegt.

⸻

## 59. Rollback

Wenn eine neue Version nach dem Update nicht korrekt startet, soll geprüft werden, ob ein automatischer oder manueller Rollback möglich ist.

⸻

## 60. Update-Historie

Die Diagnose soll später zeigen können:

```
Version 1.4.2
installiert am ...
Vorher:
1.4.1
Status:
SUCCESS
```

⸻

## 61. Entwicklungsupdates versus Produktionsupdates

Während der Entwicklung darf ein schnellerer Updateprozess verwendet werden.

Die finale Fahrzeuginstallation benötigt jedoch einen kontrollierten Produktionsprozess.

⸻

## 62. Tests

Kehler OS muss testbar sein.

Testing darf nicht nur bedeuten:

Im Wohnmobil ausprobieren und schauen, ob es funktioniert.

⸻

## 63. Unit Tests

Logische Komponenten sollen automatisiert getestet werden können.

Beispiele:

* Berechnungen
* Zustandsmaschinen
* Regeln
* Berechtigungen
* Datenvalidierung

⸻

## 64. Integration Tests

Die Zusammenarbeit mehrerer Komponenten muss getestet werden.

Beispiel:

```
Command API
↓
Command Processor
↓
PLC Adapter Simulation
↓
State Update
```

⸻

## 65. Hardware-Simulation

Da die reale Hardware nicht immer verfügbar sein wird, ist die bereits definierte Simulation besonders wichtig.

⸻

## 66. Simulation realistischer Fehler

Die Simulation soll nicht nur perfekte Normalzustände liefern.

Sie soll auch Fehler simulieren können.

Beispiele:

```
SPS offline
Sensor invalid
Victron timeout
Garage blocked
```

⸻

## 67. End-to-End Tests

Wichtige Benutzerabläufe sollen komplett getestet werden können.

Beispiel:

```
Benutzer drückt Außenlicht EIN
↓
Befehl
↓
simulierte SPS
↓
Rückmeldung
↓
UI zeigt EIN
```

⸻

## 68. Regression Tests

Ein neues Feature darf bestehende Funktionen nicht unbemerkt zerstören.

Wichtige Kernfunktionen sollen daher automatisierte Regressionstests besitzen.

⸻

## 69. Sicherheitskritische Tests

Sicherheitsrelevante Bedingungen müssen besonders gründlich getestet werden.

⸻

## 70. Testfälle für UNKNOWN

Fehlerzustände wie:

```
UNKNOWN
OFFLINE
TIMEOUT
INVALID
```

müssen bewusst getestet werden.

Nicht nur der perfekte Normalfall.

⸻

## 71. Testdaten

Testdaten müssen eindeutig als Testdaten erkennbar sein.

⸻

## 72. Kein Test auf Produktionshardware ohne Kontrolle

Entwicklungs- und Testfunktionen dürfen nicht versehentlich reale Aktoren bewegen.

⸻

## 73. Staging

Für spätere größere Entwicklungsstände kann eine separate Test-/Staging-Umgebung sinnvoll sein.

Die konkrete Notwendigkeit soll später beurteilt werden.

⸻

## 74. Codequalität

Der Quellcode muss langfristig wartbar sein.

Dazu gehören:

* klare Namen
* sinnvolle Modularisierung
* geringe Kopplung
* Dokumentation
* einheitlicher Stil
* automatisierte Prüfungen

⸻

## 75. Keine riesigen Dateien

Claude soll vermeiden, die komplette Kehler-OS-Logik in wenige riesige Dateien zu schreiben.

Module müssen sinnvoll getrennt sein.

⸻

## 76. Keine künstliche Fragmentierung

Genauso soll nicht jede kleine Funktion eine eigene Datei oder einen eigenen Dienst erhalten.

Die Struktur soll nachvollziehbar bleiben.

⸻

## 77. Dokumentation

Wichtige Architekturentscheidungen müssen dokumentiert werden.

Insbesondere:

* Warum wurde Technologie X gewählt?
* Wie funktioniert Hardwareintegration?
* Wie wird das System installiert?
* Wie wird ein Backup wiederhergestellt?
* Wie wird eine neue Hardware integriert?

⸻

## 78. README reicht nicht allein

Für ein Projekt dieser Größe sollen relevante Bereiche eigene technische Dokumentation erhalten.

⸻

## 79. Architecture Decision Records

Claude soll später prüfen, ob kompakte Architecture Decision Records sinnvoll sind.

Damit können wichtige Entscheidungen langfristig nachvollzogen werden.

⸻

## 80. Abhängigkeiten

Externe Bibliotheken sollen bewusst ausgewählt werden.

Kriterien:

* aktiv gewartet
* stabil
* dokumentiert
* passend zur Plattform
* akzeptable Lizenz
* keine unnötige Größe

⸻

## 81. Weniger Abhängigkeiten

Nicht jede kleine Funktion braucht eine neue Bibliothek.

Unnötige Abhängigkeiten erhöhen:

* Wartungsaufwand
* Sicherheitsrisiko
* Updatekomplexität

⸻

## 82. Hardwarebibliotheken

Bei industriellen Schnittstellen sollen möglichst stabile und gut dokumentierte Lösungen verwendet werden.

⸻

## 83. Zukunftssicherheit

Kehler OS soll langfristig erweiterbar bleiben.

Neue Funktionen dürfen die Grundarchitektur nicht regelmäßig zerstören.

⸻

## 84. Plugin-/Adapter-Prinzip

Neue Hardwaretypen sollen nach Möglichkeit über Adapter integriert werden.

Beispiel:

```
Hardware Adapter Interface
├── Siemens PLC Adapter
├── Victron Adapter
├── Camera Adapter
└── Future Device Adapter
```

Die konkrete technische Umsetzung wird später definiert.

⸻

## 85. Neue Fahrzeugmodule

Neue fachliche Module sollen sich ebenfalls integrieren lassen.

Beispiele:

* Wetterstation
* Reifendruck
* Generator
* weitere Energiequellen
* zusätzliche Sicherheitssysteme

⸻

## 86. Capability-basierte UI

Wenn neue Hardware neue Fähigkeiten bereitstellt, soll die UI diese verwenden können, ohne unnötig fest auf ein bestimmtes Modell zugeschnitten zu sein.

⸻

## 87. Keine unnötige Herstellerbindung

Wo möglich soll Kehler OS über logische Modelle arbeiten.

Das bedeutet nicht, dass jede Hardware beliebig austauschbar sein muss.

Aber die gesamte Software soll nicht unnötig an Herstellerdetails gekoppelt werden.

⸻

## 88. Mehrere Fahrzeuge

Die aktuelle Priorität ist ein einziges Fahrzeug.

Die Architektur soll jedoch nicht mutwillig so gebaut werden, dass eine spätere Anpassung an ein zweites Fahrzeug unmöglich wird.

⸻

## 89. Kein Multi-Tenant-System notwendig

Daraus folgt ausdrücklich nicht, dass Kehler OS jetzt bereits ein komplexes Flottenmanagementsystem werden soll.

Die aktuelle Anwendung bleibt für das reale Fahrzeug optimiert.

⸻

## 90. Technische Schulden

Kurzfristige Lösungen dürfen verwendet werden, wenn sie bewusst dokumentiert sind und keinen kritischen Bereich betreffen.

Versteckte technische Schulden sollen vermieden werden.

⸻

## 91. TODO ist keine Architektur

Wichtige Kernbereiche dürfen nicht mit unklaren Platzhaltern wie:

```
TODO: später irgendwie absichern
```

in die Produktionsversion übernommen werden.

⸻

## 92. Observability als Entwicklungswerkzeug

Performance und Stabilität müssen messbar sein.

Beispiele:

* API-Latenzen
* Verbindungsabbrüche
* CPU
* RAM
* Fehlerquoten
* Nachrichtenraten

⸻

## 93. Performance-Budgets

Claude soll später für besonders wichtige Bereiche sinnvolle Performance-Ziele definieren.

Beispielsweise:

* UI-Interaktion
* Realtime-Updates
* API
* Startzeit

Die konkreten Zahlen sollen anhand der gewählten Architektur realistisch festgelegt werden.

⸻

## 94. Kein blindes Optimieren

Performanceoptimierung soll auf Messungen basieren.

Nicht jede theoretisch schnellere Lösung ist automatisch die bessere.

⸻

## 95. Profiling

Bei Performanceproblemen sollen geeignete Profiling- und Diagnosemethoden verwendet werden.

⸻

## 96. Speicherlecks

Da Kehler OS dauerhaft läuft, müssen Speicherlecks ernst genommen werden.

Ein langsamer RAM-Anstieg über Tage ist nicht akzeptabel.

⸻

## 97. Ressourcen-Leaks

Dasselbe gilt für:

* offene Netzwerkverbindungen
* Dateideskriptoren
* Datenbankverbindungen
* Tasks
* Threads

⸻

## 98. Verbindungspools

Wenn die spätere Technologie Verbindungspools verwendet, müssen diese sinnvoll begrenzt sein.

⸻

## 99. Kameras und Performance

Kamerastreams dürfen nicht die gesamte Plattform dominieren.

Videodaten sollen effizient und möglichst getrennt von zeitkritischen Steuerdaten behandelt werden.

⸻

## 100. KI und Performance

Ein zukünftiger KI-Assistent darf die normale Fahrzeugsteuerung nicht blockieren.

Wenn ein KI-Prozess langsam ist oder ausfällt, muss Kehler OS weiterhin normal bedienbar bleiben.

⸻

## 101. KI als optionaler Dienst

Die KI-Ebene soll deshalb logisch als optionaler Dienst behandelt werden.

```
AI OFFLINE
```

darf nicht bedeuten:

```
KEHLER OS OFFLINE
```

⸻

## 102. Externe APIs

Dasselbe gilt für:

* Wetter
* Karten
* Cloud
* andere Internetdienste

Sie sind optionale Erweiterungen.

⸻

## 103. Mobile Nutzung

Wenn Kehler OS später auf Smartphone oder Tablet verwendet wird, sollen schlechte WLAN-Verbindungen berücksichtigt werden.

⸻

## 104. Reconnect des Clients

Ein Client soll nach kurzem Verbindungsverlust automatisch wieder synchronisieren können.

⸻

## 105. Kein falscher lokaler Zustand nach Reconnect

Nach einer Wiederverbindung muss der Client den aktuellen zentralen Zustand erhalten.

Er darf nicht einfach mit seinem alten Cache weiterarbeiten.

⸻

## 106. Caching

Caching kann die Performance verbessern.

Es darf aber keine falschen Live-Zustände erzeugen.

⸻

## 107. Statische Assets

Designressourcen wie:

* Icons
* Fonts
* Grafiken

können effizient lokal bereitgestellt werden.

Kehler OS soll für sein grundlegendes Design nicht von externen CDNs abhängig sein.

⸻

## 108. Offline-UI

Auch alle für die normale Benutzeroberfläche benötigten Ressourcen müssen lokal verfügbar sein.

⸻

## 109. Schriftarten

Wenn externe Schriftarten verwendet werden, sollen diese lokal eingebunden werden können, sofern Lizenz und technische Umsetzung dies erlauben.

Das System darf nicht bei fehlendem Internet plötzlich visuell auseinanderfallen.

⸻

## 110. Zukunftige größere Displays

Die UI-Architektur soll später größere oder zusätzliche Displays unterstützen können.

⸻

## 111. Responsive versus separate HMI

Claude darf je nach Anwendungsfall entscheiden, ob:

* responsive Layouts
* spezifische Displaylayouts

technisch sinnvoller sind.

Nicht jede Bildschirmgröße muss dieselbe Informationsdichte besitzen.

⸻

## 112. Hauptdisplay hat Priorität

Das primäre Designziel bleibt der zentrale Kehler-OS-Bildschirm.

Mobile Ansichten sind sekundär.

⸻

## 113. Datenmigration über Jahre

Kehler OS soll Updates über längere Zeit ermöglichen.

Ein Nutzer soll nicht bei jeder größeren Version seine gesamte Fahrzeugkonfiguration neu eingeben müssen.

⸻

## 114. Deprecated Features

Falls eine alte Funktion später ersetzt wird, soll ein kontrollierter Migrationspfad vorgesehen werden.

⸻

## 115. Hardwarewechsel

Wenn ein Hardwaregerät ersetzt wird, sollen bestehende Historie und logische Geräteidentität möglichst erhalten bleiben können.

Beispiel:

Ein Tanksensor wird ausgetauscht.

Der Benutzer möchte weiterhin dieselbe:

Frischwasser-Historie

sehen.

⸻

## 116. Datensicherung vor Hardwaretausch

Hardware- und Systemkonfigurationen müssen deshalb sicherbar sein.

⸻

## 117. Dokumentierter Wiederaufbau

Im Worst Case soll es möglich sein:

```
alter Raspberry Pi defekt
↓
neuen Raspberry Pi einsetzen
↓
Kehler OS installieren
↓
Backup einspielen
↓
Hardware synchronisieren
↓
System wieder verfügbar
```

⸻

## 118. Recovery Time

Die Architektur soll einen solchen Wiederaufbau möglichst einfach machen.

Das Ziel ist nicht, dass nur der ursprüngliche Entwickler das System wiederherstellen kann.

⸻

## 119. Wartbarkeit durch andere Entwickler

Auch ein anderer qualifizierter Entwickler soll später verstehen können:

* wie das Projekt aufgebaut ist
* wie Hardware angebunden wird
* wo Konfiguration liegt
* wie das System getestet wird

⸻

## 120. Keine Claude-Abhängigkeit

Das endgültige Kehler OS darf nicht davon abhängig sein, dass ausschließlich Claude den Code versteht oder verändern kann.

Der Quellcode und die Dokumentation müssen für Menschen nachvollziehbar sein.

⸻

## 121. Keine versteckte Magie

Generierter Code soll nicht unnötig kompliziert oder „clever“ sein.

Klare Lösungen haben Vorrang vor schwer nachvollziehbaren Tricks.

⸻

## 122. Entwicklungsworkflow

Die spätere Entwicklung soll schrittweise erfolgen.

Nicht:

Alles gleichzeitig programmieren.

Sondern beispielsweise:

```
Grundarchitektur
↓
Simulation
↓
Core Backend
↓
Frontend Shell
↓
erste reale Hardware
↓
einzelne Module
↓
Tests
↓
Optimierung
```

Die genaue Reihenfolge wird in Kapitel 18 vorgegeben.

⸻

## 123. Funktionierende Zwischenschritte

Nach wichtigen Entwicklungsphasen soll eine lauffähige Version existieren.

So können Probleme früh erkannt werden.

⸻

## 124. Keine Big-Bang-Integration

Die komplette SPS, Victron, UI, Automatisierung und KI sollen nicht erst ganz am Ende zum ersten Mal gemeinsam getestet werden.

⸻

## 125. Erste Hardwareintegration

Claude soll bei der späteren Entwicklung zunächst mit einer möglichst kleinen, kontrollierten Hardwarefunktion beginnen.

Beispielsweise einem ungefährlichen digitalen Testzustand.

Erst danach werden weitere Aktoren integriert.

⸻

## 126. Safety First bei realer Integration

Bei ersten realen Tests dürfen gefährliche oder mechanisch riskante Funktionen nicht als erstes Testobjekt verwendet werden.

⸻

## 127. Testcheckliste

Vor realer Hardwareanbindung soll für jede Funktion geprüft werden:

* Mapping korrekt?
* Input/Output korrekt?
* Rückmeldung vorhanden?
* Fehlerzustand getestet?
* Timeout getestet?
* Berechtigung getestet?
* UI-Zustand korrekt?

⸻

## 128. Abnahme

Kehler OS gilt nicht als fertig, nur weil die UI optisch gut aussieht.

Die Abnahme muss auch berücksichtigen:

* Zuverlässigkeit
* Hardwarekommunikation
* Fehlerfälle
* Performance
* Neustart
* Offlinebetrieb
* Backups
* Diagnose

⸻

## 129. Qualitätsziel

Das Projekt soll den Eindruck vermitteln, dass Software und Fahrzeug gemeinsam geplant wurden.

Nicht:

```
Wohnmobil
+
nachträglich aufgesetztes Dashboard
```

Sondern:

```
Fahrzeug und Kehler OS
=
ein Gesamtsystem
```

⸻

## 130. Kerngrundsatz

Das zentrale Prinzip dieses Kapitels lautet:

Kehler OS muss nicht nur heute funktionieren, sondern auch nach tausenden Betriebsstunden, vielen Updates, neuen Funktionen und mehreren Hardwareänderungen noch wartbar und zuverlässig sein.

⸻

## 131. Qualitätsreihenfolge

Bei technischen Entscheidungen gilt weiterhin:

1. Sicherheit
2. Zuverlässigkeit
3. korrekter tatsächlicher Zustand
4. Wartbarkeit
5. Benutzerfreundlichkeit
6. Performance
7. Erweiterbarkeit
8. visuelle Effekte

Alle Bereiche sind wichtig.

Die Reihenfolge beschreibt, was im Konfliktfall Vorrang erhält.

⸻

## 132. Was Claude später vermeiden soll

Claude soll insbesondere folgende Anti-Patterns vermeiden:

```
riesige monolithische Code-Dateien
direkter Hardwarezugriff aus der UI
Hardcoding von SPS-Adressen überall
unnötige Cloudabhängigkeit
fehlende Timeouts
fehlende Fehlerbehandlung
unbegrenzte Logs
unsichere Secrets
blindes Retry von Aktoren
unnötige Microservices
Copy-Paste-Komponenten
mehrere konkurrierende State Stores
```

⸻

## 133. Was Claude später anstreben soll

Stattdessen:

```
klare Module
zentraler State
Hardwareadapter
typed/validierte Datenmodelle
definierte Commands
Events
gute Diagnose
Simulation
automatisierte Tests
reproduzierbares Deployment
konfigurierbare Hardware
saubere Dokumentation
```

Die tatsächliche technische Umsetzung soll nach vollständiger Analyse ausgewählt werden.

⸻

## 134. Zielbild

Im normalen Betrieb passiert beispielsweise ein interner Dienstfehler.

Der Benutzer merkt im Idealfall nur:

```
Kamera momentan nicht verfügbar.
Wiederverbindung läuft.
```

Während Kehler OS im Hintergrund:

```
Fehler erkennt
↓
protokolliert
↓
Dienst kontrolliert neu verbindet
↓
Status überwacht
↓
nach Wiederherstellung synchronisiert
```

Die restlichen Fahrzeugfunktionen laufen weiter.

⸻

## 135. Zweites Zielbild

Nach mehreren Jahren wird ein neuer Sensor eingebaut.

Der Entwickler soll:

```
neuen Adapter / Mapping konfigurieren
↓
Capability registrieren
↓
logischen Zustand bereitstellen
```

können.

Er soll nicht:

```
Dashboard neu schreiben
Automation Engine ändern
Datenbank neu entwickeln
alle bestehenden Module anpassen
```

müssen.

⸻

## 136. Drittes Zielbild

Der Raspberry Pi fällt vollständig aus.

Nach Austausch der Hardware soll ein dokumentierter Prozess ermöglichen:

```
System installieren
↓
Backup wiederherstellen
↓
Konfiguration laden
↓
reale Hardware neu synchronisieren
↓
Kehler OS wieder betriebsbereit
```

Historische gespeicherte Zustände dürfen dabei nicht mit den aktuellen realen Hardwarezuständen verwechselt werden.

⸻

## 137. Ende der Anforderungsphase

Mit Kapitel 17 sind die wesentlichen:

* funktionalen
* technischen
* visuellen
* sicherheitsbezogenen
* betrieblichen

Anforderungen beschrieben.

Das nächste Kapitel ist kein weiteres normales Anforderungskapitel.

Kapitel 18 wird der finale Entwicklungsauftrag.

Dort wird festgelegt:

* wie Claude alle Kapitel auswerten soll
* wie mit Widersprüchen umzugehen ist
* welche Technologien erst jetzt ausgewählt werden dürfen
* welche Projektstruktur entstehen soll
* in welcher Reihenfolge entwickelt wird
* wann nach Hardwaredetails gefragt werden muss
* wie Simulation und reale Hardware getrennt werden
* welche Qualitätsprüfungen vor jeder Phase erforderlich sind
* und ab welchem Punkt tatsächlich Code geschrieben werden darf

⸻

## Ende Kapitel 17

Es wird weiterhin kein Code geschrieben.

Es werden weiterhin keine Projektdateien erstellt.

Beginne weiterhin nicht mit der Entwicklung.

Warte auf Kapitel 18 – Finaler Entwicklungsauftrag.

Verwende Kapitel 1 bis 17 vollständig als gemeinsame und verbindliche Projektspezifikation.
