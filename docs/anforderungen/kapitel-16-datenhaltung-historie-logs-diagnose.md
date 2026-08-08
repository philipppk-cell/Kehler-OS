# KEHLER OS

# Kapitel 16 – Datenhaltung, Historie, Logs und Diagnose

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel beschreibt, wie Kehler OS Daten speichert, historische Informationen verwaltet, Ereignisse protokolliert und technische Diagnose ermöglicht.

Verwende Kapitel 1–16 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel

Kehler OS soll nicht nur aktuelle Zustände anzeigen.

Das System soll auch nachvollziehen können:

* was passiert ist
* wann es passiert ist
* wodurch es ausgelöst wurde
* welcher Benutzer beteiligt war
* welche Hardware betroffen war
* ob ein Fehler erneut aufgetreten ist
* wie sich technische Werte über Zeit verändert haben

Dadurch entsteht ein vollständiges technisches Gedächtnis des Fahrzeugs.

⸻

## 2. Datenarten

Die gespeicherten Informationen sollen logisch in verschiedene Kategorien getrennt werden.

Mindestens:

```
Konfiguration
Live-Zustand
Messhistorie
Ereignisse
Warnungen
Fehler
Audit Logs
System Logs
Diagnosedaten
Wartungsdaten
Automatisierungs-Historie
```

Diese Datenarten besitzen unterschiedliche Anforderungen.

⸻

## 3. Live-Zustand ist nicht Historie

Der aktuelle Zustand und historische Daten sind unterschiedliche Konzepte.

Beispiel:

```
Aktuell:
Batterie = 81 %
```

Historie:

```
18:00 → 88 %
19:00 → 85 %
20:00 → 81 %
```

Die aktuelle Zustandsverwaltung darf nicht durch die historische Datenbank ersetzt werden.

⸻

## 4. Messhistorie

Kontinuierliche Messwerte sollen historisch gespeichert werden können.

Beispiele:

* Batterieladezustand
* Batteriespannung
* Batteriestrom
* Solarleistung
* Energieverbrauch
* Frischwasserstand
* Grauwasserstand
* Schwarzwasserstand
* Temperaturen
* Luftfeuchtigkeit
* Systemtemperaturen
* weitere zukünftige Messgrößen

⸻

## 5. Zeitreihendaten

Messdaten besitzen typischerweise:

```
Quelle
Messgröße
Wert
Einheit
Zeitstempel
Qualität
```

Beispiel:

```
source: victron.battery
metric: soc
value: 81
unit: %
timestamp: ...
quality: VALID
```

⸻

## 6. Sampling

Nicht jeder Messwert muss jede Millisekunde gespeichert werden.

Die Speicherrate soll zur jeweiligen Messgröße passen.

Beispiel:

```
Nivellierung während Bewegung
→ hohe Aktualisierungsrate
Frischwasser
→ deutlich geringere Rate ausreichend
```

Die konkrete Frequenz wird später je Datenquelle definiert.

⸻

## 7. Änderungsbasierte Speicherung

Bei geeigneten Daten kann gespeichert werden, wenn sich ein Wert relevant verändert.

Beispiel:

Ein digitaler Türkontakt muss nicht jede Sekunde erneut mit:

CLOSED

gespeichert werden.

Eine Zustandsänderung reicht.

⸻

## 8. Analoge Messwerte

Bei analogen Werten soll eine sinnvolle Kombination aus:

* Zeitintervall
* Wertänderung
* Deadband

verwendet werden können.

Dadurch wird unnötige Datenmenge reduziert.

⸻

## 9. Datenauflösung

Historische Daten müssen nicht für immer mit derselben Auflösung gespeichert werden.

Beispiel:

```
letzte 24 Stunden
→ hohe Auflösung
letzte 30 Tage
→ mittlere Auflösung
mehrere Jahre
→ aggregierte Daten
```

⸻

## 10. Aggregation

Ältere Daten können zu:

* Mittelwert
* Minimum
* Maximum
* Summe
* Anzahl

verdichtet werden.

Welche Aggregation sinnvoll ist, hängt vom Messwert ab.

⸻

## 11. Beispiel Energie

Bei Energie können beispielsweise langfristig interessant sein:

```
Tagesverbrauch
Tageserzeugung
maximale Leistung
durchschnittlicher SOC
```

Die Rohdaten müssen dafür nicht zwingend unbegrenzt erhalten bleiben.

⸻

## 12. Ereignisse

Ein Ereignis beschreibt einen konkreten Vorgang.

Beispiele:

```
Garage geöffnet
Landstrom verbunden
Tür geöffnet
SPS offline
Batteriewarnung ausgelöst
Automation gestartet
```

⸻

## 13. Ereignisdatensatz

Ein Ereignis soll logisch Informationen besitzen können wie:

```
ID
Typ
Quelle
Zeitpunkt
Priorität
Beschreibung
Metadaten
```

⸻

## 14. Ereignisquelle

Die Quelle muss eindeutig sein.

Beispiele:

```
USER
AUTOMATION
SPS
VICTRON
SYSTEM
NETWORK
SENSOR
```

⸻

## 15. Ereignishistorie

Der Benutzer beziehungsweise Administrator soll relevante Ereignisse später durchsuchen können.

Beispiele:

Wann wurde die Garage gestern geöffnet?

oder:

Wann war Victron zuletzt offline?

⸻

## 16. Filter

Die Historie soll später nach Kriterien filterbar sein.

Beispiele:

* Zeitraum
* System
* Priorität
* Benutzer
* Ereignistyp
* Gerät

⸻

## 17. Warnungen

Warnungen sollen zusätzlich zur normalen Ereignishistorie verwaltet werden.

Eine Warnung besitzt einen Lebenszyklus.

Beispielsweise:

```
ACTIVE
ACKNOWLEDGED
RESOLVED
```

⸻

## 18. Warnungshistorie

Eine behobene Warnung soll nicht einfach verschwinden.

Sie soll später nachvollziehbar bleiben.

Beispiel:

```
18:12
Grauwasser > 90 %
Warnung aktiviert
18:40
Benutzer quittiert
19:03
Grauwasser entleert
Warnung behoben
```

⸻

## 19. Fehler

Technische Fehler müssen gesondert erfasst werden können.

Beispiele:

* Kommunikationsfehler
* Sensorfehler
* Datenbankfehler
* Dienst abgestürzt
* Hardware offline
* ungültige Konfiguration
* Timeout

⸻

## 20. Fehler-ID

Ein technischer Fehler soll möglichst eindeutig identifizierbar sein.

Dadurch kann ein Fehler:

* gesucht
* gruppiert
* dokumentiert
* analysiert

werden.

⸻

## 21. Fehlerkontext

Ein Fehler ist nur dann wirklich hilfreich, wenn Kontext vorhanden ist.

Beispiel:

Nicht nur:

```
TIMEOUT
```

sondern:

```
Garagentor
Befehl: OPEN
Timeout nach definierter Wartezeit
SPS weiterhin erreichbar
keine Zustandsänderung erkannt
```

⸻

## 22. Wiederkehrende Fehler

Kehler OS soll erkennen können, wenn derselbe Fehler wiederholt auftritt.

Beispiel:

```
Kamera 2 offline
12 Vorkommnisse in 24 Stunden
```

Dies kann später Diagnose und Wartung erleichtern.

⸻

## 23. Fehlergruppierung

Viele identische Fehler innerhalb kurzer Zeit sollen nicht zwingend als tausende getrennte Meldungen erscheinen.

Eine sinnvolle Gruppierung ist erwünscht.

⸻

## 24. System Logs

Neben Benutzerereignissen benötigt Kehler OS technische Logs.

Beispiele:

```
Backend gestartet
SPS Adapter verbunden
Victron Adapter getrennt
WebSocket Client verbunden
Datenbankmigration abgeschlossen
```

⸻

## 25. Log-Level

Technische Logs sollen unterschiedliche Schweregrade besitzen.

Beispielsweise:

```
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Die konkrete spätere Logging-Bibliothek wird anhand der Technologie gewählt.

⸻

## 26. Produktionsmodus

Im normalen Produktionsbetrieb sollen Debug-Logs nicht unbegrenzt große Datenmengen erzeugen.

Debug-Ausgaben können bei Bedarf aktiviert werden.

⸻

## 27. Strukturierte Logs

Logs sollen nach Möglichkeit strukturiert erzeugt werden.

Ein Logeintrag kann beispielsweise enthalten:

```
timestamp
service
level
event
message
correlation_id
metadata
```

Dies erleichtert spätere Suche und Analyse.

⸻

## 28. Correlation IDs

Komplexe Abläufe sollen gegebenenfalls eine gemeinsame Kennung besitzen.

Beispiel:

Benutzer startet Garage öffnen.

Dann entstehen:

```
API Request
Command Validation
PLC Command
PLC Response
State Change
UI Update
```

Eine gemeinsame Correlation ID kann diese Schritte zusammenführen.

⸻

## 29. Command History

Wichtige Steuerbefehle sollen nachvollziehbar sein.

Beispiel:

```
20:14:32
Command:
garage.open
Source:
Haupt-iPad
User:
Philipp
Result:
SUCCESS
```

⸻

## 30. Fehlgeschlagene Commands

Auch fehlgeschlagene Befehle müssen protokollierbar sein.

Beispiel:

```
Command:
garage.open
Result:
TIMEOUT
```

⸻

## 31. Automatisierungs-Historie

Automatisierungen benötigen eine eigene nachvollziehbare Historie.

Beispiel:

```
22:00:00
Automation "Nacht" gestartet
22:00:01
Außenlicht AUS → OK
22:00:02
Display dimmen → OK
22:00:03
Automation beendet → SUCCESS
```

⸻

## 32. Teilfehler

Wenn eine Szene teilweise fehlschlägt, muss die Historie dies korrekt darstellen.

Beispiel:

```
Szene "Abfahrt"
Markise → SUCCESS
Stufe → SUCCESS
Garage → TIMEOUT
Schränke → SUCCESS
Result:
PARTIAL_FAILURE
```

⸻

## 33. Audit Log

Das Audit Log ist von normalen technischen Logs zu unterscheiden.

Es dient der Nachvollziehbarkeit wichtiger Benutzer- und Konfigurationsaktionen.

⸻

## 34. Audit-Beispiele

```
Benutzer angelegt
Benutzerrechte geändert
Hardware-Mapping geändert
Tankkapazität geändert
Automation gelöscht
Systemkonfiguration geändert
```

⸻

## 35. Audit-Manipulation

Auditinformationen sollen nicht beliebig durch normale Benutzer verändert oder gelöscht werden können.

Die konkrete Aufbewahrungsstrategie wird später festgelegt.

⸻

## 36. Wartungshistorie

Kehler OS soll Wartungsvorgänge dokumentieren können.

Beispiele:

```
Filter gewechselt
Pumpe geprüft
Hydraulik gewartet
Batteriesystem geprüft
```

⸻

## 37. Wartungseintrag

Ein Eintrag kann logisch enthalten:

```
Datum
Komponente
Arbeit
durchgeführt von
Notiz
nächster Termin
```

⸻

## 38. Wartungsintervalle

Wartung kann ausgelöst werden durch:

* Datum
* Betriebsstunden
* Kilometer
* Anzahl Vorgänge
* manuelle Planung

sofern entsprechende Daten verfügbar sind.

⸻

## 39. Betriebsstunden

Kehler OS soll für geeignete Komponenten Betriebsstunden erfassen können.

Beispiele:

* Pumpe
* Heizung
* Klimakomponente
* weitere Verbraucher

Nur wenn dies technisch sinnvoll und zuverlässig ableitbar ist.

⸻

## 40. Schaltzyklen

Für bestimmte Aktoren kann die Anzahl der Schalt- beziehungsweise Bewegungszyklen interessant sein.

Beispiele:

```
Garagentor
Schloss
Pumpe
```

Dies kann langfristig für Wartung und Predictive Maintenance relevant sein.

⸻

## 41. Diagnose

Kehler OS benötigt eine eigene technische Diagnoseoberfläche.

Diese ist primär für:

* Administrator
* Service
* Entwicklung

gedacht.

⸻

## 42. Diagnose ist nicht Dashboard

Das normale Dashboard muss einfach bleiben.

Die Diagnoseansicht darf wesentlich technischer sein.

⸻

## 43. Diagnoseübersicht

Die Diagnose soll mindestens die wichtigsten Systemkomponenten zusammenfassen können:

```
Raspberry Pi
SPS
Victron
Netzwerk
Datenbank
Backend
Realtime
Kameras
Sensoren
```

⸻

## 44. Komponentenstatus

Für eine Komponente sollen Informationen verfügbar sein wie:

```
ONLINE
OFFLINE
DEGRADED
ERROR
INITIALIZING
```

⸻

## 45. Letzte Kommunikation

Bei Netzwerkgeräten soll sichtbar sein können:

```
Last Seen:
vor 2 Sekunden
```

oder:

```
Last Seen:
vor 14 Minuten
```

⸻

## 46. Verbindungsinformationen

Für Diagnosezwecke können relevant sein:

* Verbindungstyp
* Adresse
* Latenz
* Reconnect-Anzahl
* Fehler
* letzte erfolgreiche Kommunikation

⸻

## 47. SPS-Diagnose

Die SPS-Diagnose soll später unter anderem zeigen können:

```
Verbindungsstatus
letzte Kommunikation
Kommunikationsfehler
Adapterstatus
Datenqualität
```

Die Oberfläche darf dabei keine gefährlichen direkten SPS-Manipulationsmöglichkeiten für normale Benutzer anbieten.

⸻

## 48. Victron-Diagnose

Für Victron können beispielsweise angezeigt werden:

```
Verbindung
Cerbo GX erreichbar
letzte Daten
Alarme
Adapterstatus
```

⸻

## 49. Sensor-Diagnose

Für Sensoren sollen technische Informationen einsehbar sein.

Beispiele:

```
Name
aktueller Wert
Rohwert
skalierter Wert
Qualität
Zeitstempel
Quelle
```

Rohwerte gehören primär in Diagnose/Service, nicht in die normale UI.

⸻

## 50. Aktor-Diagnose

Ein Aktor kann beispielsweise zeigen:

```
Command State
Actual State
Last Command
Last Feedback
Error
```

⸻

## 51. Hardware-Mapping

Im Diagnose- beziehungsweise Servicebereich soll nachvollziehbar sein, welche logische Funktion welcher Hardware zugeordnet ist.

Beispiel:

```
garage.door.open
Device:
PLC
Mapping:
<konfigurierter Datenpunkt>
```

⸻

## 52. Systemressourcen

Kehler OS soll den Raspberry Pi überwachen.

Mindestens denkbar:

```
CPU
RAM
Datenträger
Temperatur
Uptime
Load
```

⸻

## 53. Datenträgerwarnung

Wenn der Speicherplatz knapp wird, muss Kehler OS dies erkennen.

Beispiel:

```
System Storage
92 % belegt
WARNUNG
```

⸻

## 54. Temperaturwarnung

Bei problematischer Raspberry-Pi-Temperatur soll das System warnen können.

⸻

## 55. Dienststatus

Die Architektur kann mehrere interne Dienste besitzen.

Der Diagnosebereich soll erkennen können, ob diese laufen.

Beispiel:

```
API Service        RUNNING
PLC Adapter        RUNNING
Victron Adapter    RUNNING
History Service    RUNNING
Automation Engine  ERROR
```

⸻

## 56. Health Checks

Interne Dienste sollen geeignete Health Checks besitzen können.

Ein laufender Prozess bedeutet nicht zwangsläufig, dass er korrekt funktioniert.

⸻

## 57. Readiness

Zusätzlich kann zwischen:

Alive

und:

Ready

unterschieden werden.

Beispiel:

Ein Dienst läuft, hat aber noch keine SPS-Verbindung.

Dann ist er technisch aktiv, aber nicht vollständig betriebsbereit.

⸻

## 58. Diagnose-Snapshot

Für Support- oder Entwicklungszwecke kann später ein Diagnose-Snapshot sinnvoll sein.

Dieser könnte relevante Informationen bündeln.

Beispiele:

* Softwareversion
* Systemstatus
* Hardwarestatus
* letzte Fehler
* Konfiguration ohne Secrets
* Logs

⸻

## 59. Keine Secrets im Diagnoseexport

Ein Diagnoseexport darf niemals ungefiltert:

* Passwörter
* Tokens
* private Schlüssel
* sensible Authentifizierungsdaten

enthalten.

⸻

## 60. Export

Historische Daten und Logs können später exportierbar sein.

Beispiele:

```
CSV
JSON
```

Die genaue Funktion hängt vom Anwendungsfall ab.

⸻

## 61. Support Bundle

Langfristig kann ein spezielles Support Bundle sinnvoll sein.

Dieses fasst technische Daten zusammen, die bei Fehlersuche helfen.

⸻

## 62. Benutzerkontrolle

Vor einem Export sensibler Diagnoseinformationen soll klar sein, welche Daten enthalten sind.

⸻

## 63. Datenbank

Die konkrete Datenbanktechnologie ist weiterhin nicht festgelegt.

Die Auswahl soll auf Basis der Anforderungen erfolgen.

Es kann sinnvoll sein, unterschiedliche Speichertechnologien für unterschiedliche Datenarten zu verwenden.

⸻

## 64. Keine Technik aus Gewohnheit wählen

Claude darf später nicht einfach eine Datenbank auswählen, weil sie populär ist.

Die Entscheidung muss zu:

* Raspberry Pi
* lokaler Nutzung
* Datenmenge
* Zeitreihen
* Backup
* Wartbarkeit
* Zuverlässigkeit

passen.

⸻

## 65. Lokal zuerst

Alle grundlegenden Daten müssen lokal im Fahrzeug gespeichert werden können.

Cloudspeicherung ist keine Voraussetzung.

⸻

## 66. Internetverlust

Ein Internetverlust darf die Speicherung lokaler Daten nicht unterbrechen.

⸻

## 67. Datenverlust vermeiden

Kehler OS soll Schreibvorgänge so behandeln, dass bei Abstürzen oder Stromproblemen möglichst keine wichtigen Konfigurationsdaten beschädigt werden.

⸻

## 68. Transaktionen

Bei zusammengehörigen Datenänderungen sollen geeignete atomare beziehungsweise transaktionale Mechanismen verwendet werden.

Beispiel:

Eine Konfigurationsänderung darf nicht zur Hälfte gespeichert werden.

⸻

## 69. Datenbankmigrationen

Softwareupdates können Änderungen am Datenmodell erfordern.

Daher muss eine Migrationsstrategie vorhanden sein.

⸻

## 70. Migration darf Daten nicht unnötig löschen

Bestehende:

* Benutzer
* Automatisierungen
* Einstellungen
* Historien

sollen bei einem normalen Update erhalten bleiben.

⸻

## 71. Migrationsversion

Das System soll erkennen können, welchen Datenbankschema-Stand es verwendet.

⸻

## 72. Backup

Datenbanken und wichtige Konfigurationsdaten müssen gesichert werden können.

⸻

## 73. Backup-Strategie

Die Backup-Strategie soll zwischen wichtigen und weniger wichtigen Daten unterscheiden können.

Besonders wichtig:

```
Konfiguration
Hardware-Mapping
Benutzer
Automatisierungen
Kalibrierung
```

Historische Messwerte können je nach Speicherbedarf eine andere Priorität besitzen.

⸻

## 74. Backup während Betrieb

Es soll geprüft werden, wie ein konsistentes Backup ohne unnötig lange Systemunterbrechung möglich ist.

⸻

## 75. Restore-Test

Ein Backup gilt erst dann als zuverlässig, wenn es grundsätzlich wiederherstellbar ist.

Die spätere Entwicklung soll Restore-Verfahren mit berücksichtigen.

⸻

## 76. Speicherbegrenzung

Das System muss verhindern, dass Logs oder Historien den gesamten Datenträger füllen.

⸻

## 77. Retention Policies

Für unterschiedliche Datenarten sollen Aufbewahrungsregeln definiert werden.

Beispiel:

```
Debug Logs
→ kurze Aufbewahrung
System Events
→ länger
Audit Logs
→ sehr langfristig
Mess-Rohdaten
→ begrenzt
aggregierte Historie
→ langfristig
```

Die genauen Zeiten werden später konfiguriert.

⸻

## 78. Log Rotation

Technische Logdateien sollen rotiert beziehungsweise begrenzt werden können.

⸻

## 79. Speicherüberwachung

Kehler OS muss den eigenen Speicherverbrauch überwachen.

Es darf nicht erst bemerken, dass der Speicher voll ist, wenn die Datenbank bereits nicht mehr schreiben kann.

⸻

## 80. Notreserve

Es kann sinnvoll sein, eine Speicherreserve zu berücksichtigen, sodass das System bei hoher Belegung weiterhin wichtige Fehler protokollieren kann.

⸻

## 81. Datenprioritäten

Im Extremfall sind nicht alle Daten gleich wichtig.

Beispielsweise ist:

kritischer Systemfehler

wichtiger als:

hochaufgelöster langfristiger Komfortmesswert

Die Architektur soll dies berücksichtigen.

⸻

## 82. Zeit

Alle Logs, Ereignisse und Messwerte benötigen konsistente Zeitstempel.

⸻

## 83. Zeitzonen

Intern gespeicherte Zeitstempel sollen so behandelt werden, dass Reisen zwischen Zeitzonen keine Historie zerstören.

Die Benutzeroberfläche kann die Zeit lokal anzeigen.

⸻

## 84. Zeitumstellung

Sommer-/Winterzeit darf nicht zu doppeldeutigen historischen Datensätzen führen.

⸻

## 85. Uhrzeit ohne Internet

Das Fahrzeug muss auch ohne Internet eine brauchbare Zeitbasis behalten.

Die konkrete Lösung hängt von der Hardware ab.

⸻

## 86. Datenintegrität

Kehler OS soll erkennen können, wenn Daten:

* fehlen
* beschädigt
* veraltet
* unplausibel

sind.

⸻

## 87. Keine stillen Datenfehler

Ein fehlgeschlagener Speichervorgang darf nicht einfach ignoriert werden.

Relevante Persistenzfehler müssen diagnostizierbar sein.

⸻

## 88. Datenbankausfall

Wenn die Historien-Datenbank ausfällt, darf dies nicht automatisch bedeuten, dass sämtliche Fahrzeugsteuerung ausfällt.

Konzeptionell:

```
History Database ERROR
```

während:

```
SPS Steuerung
Live State
Command Processing
```

weiter funktionieren können, sofern technisch möglich.

⸻

## 89. Graceful Degradation

Kehler OS soll bei Teilfehlern möglichst in einen reduzierten, aber kontrollierten Betriebszustand wechseln.

Beispiel:

```
Historie nicht verfügbar
Live-Steuerung weiterhin verfügbar
```

⸻

## 90. Benutzerinformation

Der Benutzer soll über relevante Teilausfälle verständlich informiert werden.

Beispiel:

```
Historische Daten sind momentan nicht verfügbar.
Die Fahrzeugsteuerung funktioniert weiterhin.
```

⸻

## 91. Diagnose muss selbst robust sein

Ein Fehler im Diagnosemodul darf nicht das restliche System blockieren.

⸻

## 92. Historie und UI

Historische Daten sollen in Kehler OS hochwertig visualisiert werden können.

Beispiele:

* Liniencharts
* Verbrauchsverläufe
* Tageswerte
* Vergleichswerte

Die konkrete Gestaltung bleibt Claude überlassen und muss zum definierten Designsystem passen.

⸻

## 93. Diagrammzeiträume

Typische Zeiträume können beispielsweise sein:

```
1 Stunde
24 Stunden
7 Tage
30 Tage
```

Weitere sinnvolle Zeiträume können ergänzt werden.

⸻

## 94. Tooltips und Details

Der Benutzer soll bei historischen Diagrammen genaue Werte ablesen können, ohne die Darstellung zu überladen.

⸻

## 95. Vergleich

Für geeignete Daten können Vergleiche sinnvoll sein.

Beispiel:

```
Energieverbrauch heute
vs.
gestern
```

⸻

## 96. Trends

Kehler OS kann Trends anzeigen.

Beispiel:

```
Wasserverbrauch
↓ 12 % gegenüber letzter Woche
```

Solche Werte sind abgeleitete Informationen und müssen entsprechend behandelt werden.

⸻

## 97. KI und Historie

Ein späterer KI-Assistent kann historische Daten analysieren.

Beispiele:

Warum war der Energieverbrauch gestern höher?

oder:

Wie lange reicht unser Frischwasser ungefähr?

⸻

## 98. KI darf keine Daten erfinden

Wenn historische Daten fehlen, muss die KI dies klar sagen.

Sie darf fehlende Messwerte nicht als reale Historie ausgeben.

⸻

## 99. Predictive Maintenance

Langfristig kann Kehler OS aus:

* Fehlerhäufigkeit
* Betriebsstunden
* Schaltzyklen
* Messwerttrends

Wartungsempfehlungen ableiten.

⸻

## 100. Keine falsche Sicherheit bei Prognosen

Eine Prognose ist keine tatsächliche Messung.

Kehler OS muss zwischen:

MEASURED

und:

PREDICTED

unterscheiden.

⸻

## 101. Entwicklungsdiagnose

Während der Entwicklung soll Claude tiefgehende Diagnosemöglichkeiten vorsehen.

Beispiele:

* Simulationsstatus
* API-Verbindungen
* Eventfluss
* State Updates
* Adapterstatus

⸻

## 102. Produktionsdiagnose

Im Produktionsbetrieb sollen nur sinnvolle Diagnosefunktionen sichtbar beziehungsweise aktiviert sein.

Entwicklungsdetails dürfen die normale Benutzeroberfläche nicht überladen.

⸻

## 103. Observability

Die interne Architektur soll so aufgebaut sein, dass Probleme nachvollziehbar sind.

Dazu gehören drei grundlegende Bereiche:

```
Logs
Metrics
Events
```

Diese sollen sich sinnvoll ergänzen.

⸻

## 104. Metriken

Interne Metriken können beispielsweise sein:

```
API response time
SPS latency
message rate
error rate
memory usage
CPU usage
```

⸻

## 105. Performance-Diagnose

Kehler OS soll später erkennen helfen können, wenn das System beispielsweise:

* langsam wird
* ungewöhnlich viel CPU nutzt
* zu viele Daten schreibt
* Kommunikationslatenzen erhöht sind

⸻

## 106. Benutzeroberfläche bleibt sauber

Die technische Tiefe dieses Kapitels darf nicht dazu führen, dass normale Benutzer ständig technische Details sehen.

Das normale Kehler OS bleibt:

* klar
* ruhig
* hochwertig
* verständlich

Die Tiefe befindet sich im Hintergrund beziehungsweise in Diagnose- und Servicebereichen.

⸻

## 107. Zielbild

Ein Problem tritt auf.

Beispiel:

Die Garage öffnet nicht.

Der normale Benutzer sieht:

```
Garage konnte nicht geöffnet werden.
Keine Rückmeldung von der Steuerung.
```

Ein Administrator kann anschließend tiefer gehen:

```
Command: garage.open
Result: TIMEOUT
PLC:
ONLINE
Command sent:
20:14:32.114
State before:
CLOSED
State after:
CLOSED
Feedback:
none
```

Damit ist Kehler OS sowohl einfach zu bedienen als auch professionell diagnostizierbar.

⸻

## 108. Grundsatz

Das zentrale Prinzip dieses Kapitels lautet:

Jeder wichtige Zustand und Fehler soll nachvollziehbar sein, ohne dass die technische Diagnose die normale Bedienoberfläche kompliziert macht.

⸻

## Ende Kapitel 16

Dieses Kapitel definiert:

* Messhistorie
* Zeitreihendaten
* Datenaggregation
* Ereignishistorie
* Warnungshistorie
* technische Fehler
* strukturierte Logs
* Audit Logs
* Command History
* Automatisierungs-Historie
* Wartungsdaten
* Diagnoseoberfläche
* Systemmetriken
* Datenbankmigrationen
* Backup und Restore
* Retention Policies
* Speicherüberwachung
* Graceful Degradation
* KI-Auswertung historischer Daten
* Predictive Maintenance
* Observability

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf Kapitel 17.

Verwende Kapitel 1 bis 16 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
