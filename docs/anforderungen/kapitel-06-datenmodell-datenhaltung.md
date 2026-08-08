# KEHLER OS

# Kapitel 6 – Datenmodell und Datenhaltung

> Vorbemerkung aus der Übermittlung:
> Jetzt gehen wir an Kapitel 6 – Datenmodell & Datenbank. Das ist wichtig, weil
> hier festgelegt wird, wie Kehler OS Zustände, Messwerte, Ereignisse, Benutzer,
> Einstellungen und Historien organisiert.

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Treffe keine eigenständigen Architekturentscheidungen.

Dieses Kapitel definiert die Anforderungen an Datenmodell, Datenhaltung und Datenlebenszyklen von Kehler OS.

Verwende Kapitel 1 bis 6 gemeinsam als verbindliche Grundlage.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel

Kehler OS verarbeitet sehr große Mengen unterschiedlicher Daten.

Beispiele:

* aktuelle Sensorwerte
* historische Messwerte
* Systemzustände
* Benutzer
* Einstellungen
* Ereignisse
* Fehler
* Warnungen
* Automatisierungen
* Wartungsinformationen
* Energieverläufe
* Tankverläufe
* Temperaturen
* Netzwerkzustände
* Geräteinformationen

Diese Daten müssen strukturiert gespeichert und wieder abgerufen werden können.

⸻

## 2. Grundprinzip

Es muss zwischen verschiedenen Arten von Daten unterschieden werden.

Nicht jede Information benötigt dieselbe Speicherung.

Kehler OS soll mindestens zwischen folgenden Kategorien unterscheiden:

1. Konfigurationsdaten
2. Zustandsdaten
3. Messdaten
4. Ereignisdaten
5. Protokolldaten
6. Benutzerdaten
7. Automatisierungsdaten
8. Wartungsdaten
9. Diagnosedaten

⸻

## 3. Aktueller Systemzustand

Kehler OS benötigt jederzeit einen aktuellen Zustand des Fahrzeugs.

Beispiele:

```
battery.state
battery.soc
solar.power
tank.fresh_water.level
tank.grey_water.level
garage.door.state
door.main.state
light.living_room.state
network.internet.state
```

Der aktuelle Zustand muss schnell verfügbar sein.

Die Benutzeroberfläche darf nicht für jede Anzeige historische Daten durchsuchen müssen.

⸻

## 4. Historische Daten

Bestimmte Werte müssen über längere Zeit gespeichert werden.

Beispiele:

* Batterieladezustand
* Batteriespannung
* Batteriestrom
* Solarleistung
* Energieverbrauch
* Tankfüllstände
* Temperaturen
* Luftfeuchtigkeit
* Netzwerkqualität

Dadurch können später Diagramme und Statistiken erstellt werden.

⸻

## 5. Zeitreihen

Messwerte mit kontinuierlichen Änderungen sollen als Zeitreihen behandelt werden.

Ein Messwert benötigt logisch mindestens:

* Messzeitpunkt
* Quelle
* Messwert
* Einheit
* Qualität beziehungsweise Gültigkeit

Beispiel:

```
source: battery
metric: voltage
value: 26.1
unit: V
timestamp: ...
quality: valid
```

⸻

## 6. Einheiten

Einheiten müssen eindeutig definiert sein.

Beispiele:

* Volt
* Ampere
* Watt
* Wattstunden
* Prozent
* Grad Celsius
* Liter
* Meter
* Kilometer
* Kilometer pro Stunde

Interne Daten dürfen nicht von der aktuell gewählten Anzeigeeinheit abhängig sein.

Beispielsweise kann intern Celsius verwendet werden, während die Benutzeroberfläche später eine andere Darstellung ermöglichen kann.

⸻

## 7. Wertebereiche

Messwerte müssen plausibilisiert werden können.

Beispiel:

Ein Tanksensor darf nicht plötzlich einen physikalisch unmöglichen Wert liefern.

Ein Wert von:

-500 %

muss als fehlerhaft erkannt werden.

Die Datenhaltung darf fehlerhafte Werte nicht einfach als gültige Messwerte behandeln.

⸻

## 8. Datenqualität

Jeder relevante Messwert soll einen Zustand der Datenqualität besitzen können.

Beispiele:

```
VALID
UNKNOWN
STALE
INVALID
ERROR
```

Damit kann Kehler OS zwischen:

„Der Tank ist leer“

und:

„Der Tanksensor liefert momentan keine Daten“

unterscheiden.

Diese Unterscheidung ist zwingend.

⸻

## 9. Ereignisdaten

Ereignisse werden separat von kontinuierlichen Messwerten behandelt.

Beispiele:

* Tür geöffnet
* Tür geschlossen
* Landstrom angeschlossen
* Landstrom getrennt
* Batteriealarm
* System gestartet
* System heruntergefahren
* Kamera offline
* SPS-Verbindung verloren

Ein Ereignis benötigt mindestens:

* Typ
* Quelle
* Zeitpunkt
* Schweregrad
* relevante Daten

⸻

## 10. Ereignishistorie

Ereignisse müssen später durchsucht werden können.

Beispielsweise soll ein Administrator nachvollziehen können:

„Wann wurde das Garagentor gestern geöffnet?“

Oder:

„Wann ist die SPS-Verbindung zuletzt ausgefallen?“

⸻

## 11. Benutzer

Kehler OS benötigt ein Benutzerverwaltungssystem.

Benutzer besitzen mindestens:

* eindeutige Identität
* Anzeigename
* Rolle
* Einstellungen
* Berechtigungen
* Aktivierungsstatus

Sensible Authentifizierungsdaten müssen sicher gespeichert werden.

Passwörter dürfen niemals im Klartext gespeichert werden.

⸻

## 12. Rollen

Das System soll verschiedene Rollen unterstützen können.

Beispielsweise:

```
ADMIN
USER
GUEST
SERVICE
```

Die endgültige Rollenstruktur wird später definiert.

Rollen bestimmen, welche Funktionen ein Benutzer verwenden darf.

⸻

## 13. Einstellungen

Kehler OS besitzt globale Einstellungen.

Beispiele:

* Sprache
* Einheiten
* Displayhelligkeit
* Theme
* Zeitformat
* Benachrichtigungen
* Netzwerk
* Automatisierungen
* Energieeinstellungen

Benutzerspezifische Einstellungen werden von globalen Einstellungen getrennt.

⸻

## 14. Fahrzeugkonfiguration

Neben Benutzereinstellungen existiert eine Fahrzeugkonfiguration.

Diese beschreibt das konkrete Fahrzeug.

Beispiele:

* Anzahl der Tanks
* Tankgrößen
* vorhandene Kameras
* vorhandene Räume
* vorhandene Lichtkreise
* Sensoren
* SPS-Module
* Energiekomponenten
* verfügbare Funktionen

Dadurch kann Kehler OS später an unterschiedliche Fahrzeugkonfigurationen angepasst werden.

⸻

## 15. Geräte

Jedes angeschlossene Gerät soll logisch identifizierbar sein.

Beispiele:

```
SPS
Victron
Camera
Sensor
Display
NetworkDevice
```

Ein Gerät besitzt beispielsweise:

* ID
* Name
* Typ
* Hersteller
* Modell
* Kommunikationsschnittstelle
* Status
* Firmwareversion
* letzte Verbindung

⸻

## 16. Sensoren

Sensoren werden logisch von ihrer physischen Schnittstelle getrennt.

Beispiel:

Nicht:

```
AI_3 = Tank
```

sondern:

```
fresh_water.level
```

Die Hardwarezuordnung wird separat gespeichert.

Dadurch bleibt die Software verständlich.

⸻

## 17. Aktoren

Dasselbe Prinzip gilt für Aktoren.

Nicht:

```
DO_7 = 1
```

sondern:

```
living_room.light = ON
```

Die konkrete Zuordnung zu SPS-Ausgängen gehört zur Hardwarekonfiguration.

⸻

## 18. Automatisierungen

Automatisierungen müssen als Daten gespeichert werden können.

Eine Automatisierung kann logisch bestehen aus:

```
TRIGGER
CONDITIONS
ACTIONS
```

Beispiel:

```
TRIGGER:
solar.power.changed
CONDITION:
battery.soc > 95%
ACTION:
notify("Batterie nahezu voll")
```

Die konkrete Syntax wird später definiert.

⸻

## 19. Szenen

Kehler OS soll später Szenen unterstützen.

Eine Szene kombiniert mehrere Aktionen.

Beispiel:

„Nacht“

* Wohnzimmerlicht ausschalten
* Außenbeleuchtung ausschalten
* Türen verriegeln
* bestimmte Displays dimmen
* Nachtmodus aktivieren

Szenen werden als Konfiguration gespeichert.

⸻

## 20. Benachrichtigungen

Benachrichtigungen müssen strukturiert gespeichert werden können.

Beispiele:

* Information
* Hinweis
* Warnung
* kritischer Alarm

Eine Benachrichtigung besitzt beispielsweise:

* Typ
* Zeitpunkt
* Quelle
* Nachricht
* Status
* Priorität

⸻

## 21. Fehler

Fehler müssen dauerhaft nachvollziehbar sein.

Ein Fehler soll mindestens enthalten:

* Fehler-ID
* Quelle
* Zeitpunkt
* Schweregrad
* Beschreibung
* Status
* mögliche Ursache
* Wiederholungsanzahl

Ein Fehler kann beispielsweise folgende Zustände besitzen:

```
ACTIVE
ACKNOWLEDGED
RESOLVED
```

⸻

## 22. Wartungsdaten

Kehler OS soll später Wartungsinformationen speichern können.

Beispiele:

* Filterwechsel
* Ölwechsel
* Batterieprüfung
* Reifen
* Pumpen
* Klimaanlage
* Generator
* technische Prüfungen

Jede Wartungsaufgabe kann enthalten:

* Beschreibung
* Intervall
* letzter Termin
* nächster Termin
* Status
* Notizen

⸻

## 23. Datenaufbewahrung

Nicht alle Daten müssen unbegrenzt gespeichert werden.

Die Datenhaltung muss deshalb unterschiedliche Aufbewahrungszeiten unterstützen.

Beispiele:

* aktueller Zustand: dauerhaft verfügbar
* Ereignisse: langfristig
* hochauflösende Messwerte: begrenzte Zeit
* aggregierte Messwerte: langfristig
* Debug-Logs: kürzer

Die konkreten Aufbewahrungszeiten werden später festgelegt.

⸻

## 24. Datenaggregation

Historische Messwerte können langfristig verdichtet werden.

Beispiel:

Zunächst:

Messung jede Sekunde

Später:

Durchschnitt pro Minute

und anschließend:

Durchschnitt pro Stunde

Dadurch bleibt die Datenbank performant.

Die Rohdaten müssen nicht zwingend für immer gespeichert werden.

⸻

## 25. Datenkonsistenz

Daten müssen konsistent bleiben.

Ein Zustand darf nicht gleichzeitig widersprüchliche Werte besitzen.

Beispiel:

Wenn ein Garagentor geschlossen ist, darf der Systemzustand nicht gleichzeitig „offen“ anzeigen.

Bei widersprüchlichen Informationen muss das System einen definierten Zustand verwenden, beispielsweise:

UNKNOWN

⸻

## 26. Offlinebetrieb

Daten müssen auch ohne Internet gespeichert werden können.

Kehler OS darf keine Cloud benötigen, um lokale Daten zu speichern.

Das Fahrzeug muss vollständig autark funktionieren.

⸻

## 27. Backup

Wichtige Daten müssen gesichert werden können.

Besonders wichtig:

* Konfiguration
* Benutzer
* Automatisierungen
* Fahrzeugkonfiguration
* Einstellungen
* Wartungsdaten

Ein Backup muss später wiederherstellbar sein.

⸻

## 28. Wiederherstellung

Nach einem Hardwaredefekt muss Kehler OS möglichst schnell wiederhergestellt werden können.

Ziel:

Ein neues Raspberry-Pi-System soll mit einem Backup wieder in einen bekannten Zustand versetzt werden können.

⸻

## 29. Datenmigration

Wenn sich das Datenmodell durch zukünftige Versionen verändert, müssen vorhandene Daten migriert werden können.

Ein Update darf keine bestehenden Konfigurationen unbrauchbar machen.

⸻

## 30. Sicherheit

Daten müssen nach ihrer Sensibilität behandelt werden.

Besonders geschützt werden:

* Benutzerinformationen
* Authentifizierungsdaten
* Netzwerkdaten
* Zugangsdaten
* externe Zugriffsdaten
* Sicherheitskonfiguration

⸻

## 31. Datenschutz

Kehler OS soll grundsätzlich nach dem Prinzip:

Local First

arbeiten.

Daten bleiben möglichst lokal im Fahrzeug.

Eine Cloud ist optional.

Es dürfen keine persönlichen oder technischen Daten ohne ausdrückliche Notwendigkeit an externe Dienste übertragen werden.

⸻

## 32. API-Datenmodell

Die Daten, die über APIs bereitgestellt werden, müssen semantisch verständlich sein.

Die API darf keine internen Datenbankstrukturen direkt offenlegen.

Beispielsweise soll ein Client nicht wissen müssen, wie die Datenbank intern aufgebaut ist.

⸻

## 33. Trennung von Datenbank und Geschäftslogik

Die Geschäftslogik darf nicht direkt von konkreten Datenbanktabellen abhängig sein.

Zwischen Geschäftslogik und Datenbank muss eine geeignete Abstraktion vorhanden sein.

Dadurch kann die Datenbank später verändert werden, ohne das gesamte System neu entwickeln zu müssen.

⸻

## 34. Caching

Häufig benötigte Daten dürfen zwischengespeichert werden.

Caching darf jedoch niemals dazu führen, dass kritische Zustände veraltet dargestellt werden.

Für jeden Cache muss klar definiert sein:

* welche Daten gespeichert werden
* wie lange sie gültig sind
* wann sie aktualisiert werden
* was bei einem Fehler passiert

⸻

## 35. Zeit

Zeit muss im gesamten System konsistent behandelt werden.

Zeitstempel sollen intern eindeutig und maschinenlesbar gespeichert werden.

Die Benutzeroberfläche darf die Darstellung später an die lokale Zeitzone anpassen.

Dies ist besonders wichtig, weil das Wohnmobil international unterwegs sein kann.

⸻

## 36. Internationale Nutzung

Kehler OS muss damit umgehen können, dass sich das Fahrzeug in unterschiedlichen Ländern befindet.

Dazu gehören:

* Zeitzonen
* Sommer-/Winterzeit
* Einheiten
* Sprache
* Datumsformate
* lokale Darstellungen

Die gespeicherten Rohdaten dürfen davon nicht abhängig sein.

⸻

## 37. Datenzugriff

Nicht jedes Modul darf auf sämtliche Daten zugreifen.

Module sollen nur die Daten erhalten, die sie tatsächlich benötigen.

Dies verbessert:

* Sicherheit
* Wartbarkeit
* Übersichtlichkeit

⸻

## 38. Datenmodell als zentrale Wahrheit

Für jeden Systemwert muss eindeutig festgelegt sein, welche Komponente als Quelle der Wahrheit gilt.

Beispiel:

Die SPS ist die Quelle für einen digitalen Eingang.

Victron ist die Quelle für bestimmte Energieparameter.

Kehler OS ist die Quelle für Benutzer- und Automatisierungskonfiguration.

Es darf keine konkurrierenden Wahrheiten geben.

⸻

## 39. Zustandsänderungen

Wenn sich ein Zustand verändert, soll dies nachvollziehbar sein.

Beispiel:

```
garage.door
CLOSED
↓
OPENING
↓
OPEN
```

Die Zwischenzustände müssen berücksichtigt werden, wenn die Hardware dies unterstützt.

⸻

## 40. Historische Nachvollziehbarkeit

Bei wichtigen Systemzuständen muss später nachvollziehbar sein:

* welcher Zustand bestand
* wann er bestand
* wodurch er geändert wurde
* ob die Änderung automatisch oder manuell erfolgte

Beispiel:

```
Licht eingeschaltet
Quelle:
Benutzer
Benutzer:
Philipp
Zeit:
...
Aktion:
living_room.light = ON
```

⸻

## 41. Systemmetriken

Kehler OS soll interne Betriebsdaten erfassen können.

Beispiele:

* CPU-Auslastung
* RAM
* Speicherplatz
* Temperatur des Raspberry Pi
* Netzwerkverkehr
* Prozessstatus
* Neustarts
* Fehleranzahl

Diese Daten dienen Diagnose und Wartung.

⸻

## 42. Datenbankausfall

Die Anwendung muss einen Datenbankfehler erkennen.

Ein Datenbankausfall darf nicht automatisch zum Absturz des gesamten Systems führen.

Systemfunktionen müssen soweit möglich kontrolliert weiterarbeiten.

⸻

## 43. Neustart

Nach einem Neustart muss Kehler OS seinen persistenten Zustand wiederherstellen können.

Dabei darf kein gefährlicher Zustand automatisch übernommen werden.

Besonders bei Aktoren muss zwischen:

* gespeichertem Zustand
* tatsächlichem Hardwarezustand
* unbekanntem Zustand

unterschieden werden.

⸻

## 44. Keine gefährlichen Annahmen

Das System darf niemals davon ausgehen:

„Der letzte gespeicherte Zustand ist weiterhin der aktuelle Zustand.“

Beispiel:

Vor dem Neustart war ein Garagentor geschlossen.

Nach dem Neustart darf Kehler OS nicht automatisch annehmen, dass es weiterhin geschlossen ist.

Der aktuelle Zustand muss erneut festgestellt werden.

⸻

## 45. Zukunft

Das Datenmodell muss später folgende Erweiterungen ermöglichen:

* mehrere Fahrzeuge
* mehrere SPS
* zusätzliche Energiekomponenten
* weitere Benutzer
* Fernzugriff
* Cloud-Synchronisation
* KI-Analysen
* erweiterte Statistiken
* Predictive Maintenance

Diese Funktionen müssen später hinzugefügt werden können, ohne die Grundstruktur zu zerstören.

⸻

## 46. Grundsatz für zukünftige Entwickler

Daten dürfen niemals nur deshalb gespeichert werden, weil es technisch möglich ist.

Für jede Datenart muss geklärt werden:

* Warum wird sie gespeichert?
* Wie lange?
* Wer benötigt sie?
* Wie sensibel ist sie?
* Wie wird sie gelöscht?
* Wie wird sie gesichert?
* Wie wird sie migriert?

⸻

## 47. Zielbild

Die Datenarchitektur von Kehler OS soll dafür sorgen, dass das gesamte Fahrzeug jederzeit als konsistenter digitaler Zustand dargestellt werden kann.

Kehler OS soll wissen:

* Was passiert gerade?
* Was ist vorher passiert?
* Was ist geplant?
* Was ist fehlerhaft?
* Was wurde verändert?
* Wer hat etwas verändert?
* Welche Hardware ist verfügbar?
* Welche Daten sind zuverlässig?

⸻

## Ende Kapitel 6

Dieses Kapitel definiert die Anforderungen an Datenmodell und Datenhaltung.

Es wurde bewusst noch keine konkrete Datenbanktechnologie verbindlich festgelegt.

Die technische Auswahl muss später anhand der Anforderungen bewertet werden.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf Kapitel 7.

Verwende Kapitel 1 bis 6 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
