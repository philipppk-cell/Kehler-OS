# KEHLER OS

# Kapitel 13 – Zustandsverwaltung und Datenmodell im laufenden Betrieb

> Vorbemerkung aus der Übermittlung:
> Kapitel 13 wird jetzt die interne Zustandsverwaltung definieren. Das ist
> wichtig, weil Kehler OS jederzeit einen eindeutigen, konsistenten
> Fahrzeugzustand braucht und alle Clients denselben Stand sehen müssen.

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel beschreibt, wie Kehler OS Zustände, Messwerte, Befehle und Ereignisse logisch behandeln soll.

Verwende Kapitel 1–13 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel

Kehler OS muss jederzeit wissen, was im Fahrzeug tatsächlich passiert.

Dazu gehören unter anderem:

* aktuelle Sensorwerte
* aktuelle Gerätezustände
* Verbindungszustände
* laufende Bewegungen
* aktive Warnungen
* Benutzeraktionen
* Automatisierungen
* Hardware-Rückmeldungen

Diese Informationen müssen in einem konsistenten Systemzustand zusammengeführt werden.

⸻

## 2. Eine zentrale Wahrheit

Für jeden relevanten Zustand muss es genau eine definierte Wahrheit geben.

Beispiel:

```
garage.state = OPEN
```

Dieser Zustand darf nicht in mehreren Teilen der Software unabhängig verwaltet werden.

Dashboard, Garage-Seite und Smartphone müssen denselben Zustand sehen.

⸻

## 3. Kein lokaler UI-Zustand als Fahrzeugzustand

Die Benutzeroberfläche darf reale Fahrzeugzustände nicht selbst erfinden oder dauerhaft lokal speichern.

Beispiel:

Nicht:

```
Button gedrückt
→ UI setzt Garage sofort auf OPEN
```

Sondern:

```
Button gedrückt
→ Befehl
→ Backend
→ Steuerung
→ Rückmeldung
→ tatsächlicher Zustand
→ UI
```

⸻

## 4. Wunschzustand und tatsächlicher Zustand

Kehler OS muss unterscheiden können zwischen:

```
requested_state
```

und:

```
actual_state
```

Beispiel:

```
requested_state = OPEN
actual_state = OPENING
```

Das verhindert falsche Darstellungen.

⸻

## 5. Zustandsmaschine

Bewegliche oder komplexe Geräte sollen über definierte Zustandsmaschinen beschrieben werden können.

Beispiel Garagentor:

```
CLOSED
OPENING
OPEN
CLOSING
STOPPED
BLOCKED
ERROR
UNKNOWN
```

Nicht jeder Übergang zwischen allen Zuständen ist erlaubt.

⸻

## 6. Gültige Übergänge

Beispiel:

```
CLOSED
→ OPENING
→ OPEN
```

oder:

```
OPEN
→ CLOSING
→ CLOSED
```

Ein direkter Übergang:

```
CLOSED
→ OPEN
```

kann nur dann verwendet werden, wenn die Hardware keine Zwischenzustände liefert.

Die Zustandslogik muss sich nach den tatsächlichen Fähigkeiten der Hardware richten.

⸻

## 7. Sensorzustände

Sensoren besitzen nicht nur einen Wert.

Ein Sensor soll logisch besitzen können:

* aktueller Wert
* Einheit
* Zeitstempel
* Qualität
* Quelle
* Status

Beispiel:

```
id: tank.fresh_water.level
value: 64
unit: %
quality: VALID
source: plc
timestamp: ...
```

⸻

## 8. Datenqualität

Mindestens folgende Qualitätszustände sollen berücksichtigt werden:

```
VALID
STALE
UNKNOWN
INVALID
ERROR
```

Die konkrete spätere Implementierung darf weitere sinnvolle Zustände ergänzen.

⸻

## 9. STALE

Ein Wert ist STALE, wenn er grundsätzlich gültig war, aber länger als erwartet nicht aktualisiert wurde.

Beispiel:

Ein Temperatursensor hat zuletzt vor zehn Minuten Daten geliefert, obwohl normalerweise alle zehn Sekunden ein neuer Wert erwartet wird.

Der letzte Wert darf dann nicht einfach als aktuell behandelt werden.

⸻

## 10. UNKNOWN

UNKNOWN bedeutet:

Der tatsächliche Zustand ist derzeit nicht bekannt.

Dies darf nicht automatisch mit:

```
0
OFF
CLOSED
```

gleichgesetzt werden.

⸻

## 11. INVALID

INVALID bedeutet, dass ein Wert technisch vorhanden ist, aber nicht als gültiger Messwert verwendet werden darf.

Beispiel:

Tankfüllstand = 187 %

Wenn dies außerhalb des erlaubten Bereichs liegt, ist der Wert ungültig.

⸻

## 12. Zeitstempel

Jede relevante Zustandsänderung soll einen Zeitstempel erhalten.

Dadurch kann Kehler OS erkennen:

* wann sich ein Wert geändert hat
* wie aktuell ein Wert ist
* wie lange ein Zustand bereits besteht

⸻

## 13. Quelle eines Zustands

Für jeden Zustand soll bekannt sein, woher er stammt.

Beispiele:

```
PLC
VICTRON
SENSOR
KEHLER_OS
USER
AUTOMATION
SIMULATION
```

Die genaue spätere Namensstruktur soll einheitlich sein.

⸻

## 14. Unterschied zwischen Quelle und Auslöser

Quelle und Auslöser sind nicht immer dasselbe.

Beispiel:

```
Auslöser:
Benutzer
Quelle des tatsächlichen Zustands:
SPS
```

Der Benutzer fordert das Öffnen der Garage an.

Die SPS bestätigt den tatsächlichen Garagenzustand.

⸻

## 15. Befehle

Ein Befehl beschreibt eine gewünschte Aktion.

Beispiele:

```
light.turn_on
garage.open
water_pump.turn_off
vehicle.lock
```

Ein Befehl ist kein Zustand.

⸻

## 16. Lebenszyklus eines Befehls

Ein Befehl kann logisch mehrere Phasen besitzen.

Beispielsweise:

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

Nicht jeder Befehl muss jede Phase durchlaufen.

⸻

## 17. Befehlsergebnis

Ein Benutzer muss erkennen können, ob eine Aktion erfolgreich war.

Beispiel:

```
Garage öffnen
→ ausgeführt
```

oder:

```
Garage öffnen
→ fehlgeschlagen
→ keine Rückmeldung der Steuerung
```

⸻

## 18. Befehls-ID

Wichtige Befehle sollen eindeutig identifizierbar sein.

Dadurch kann eine spätere Rückmeldung dem ursprünglichen Befehl zugeordnet werden.

Dies ist besonders bei mehreren Clients und parallelen Aktionen wichtig.

⸻

## 19. Mehrere Clients

Kehler OS kann gleichzeitig von mehreren Geräten bedient werden.

Beispiele:

* Haupt-iPad
* Smartphone
* Laptop

Alle Clients arbeiten mit demselben zentralen Zustand.

⸻

## 20. Konflikte

Wenn zwei Benutzer nahezu gleichzeitig widersprüchliche Befehle senden, muss das Backend einen konsistenten Zustand sicherstellen.

Beispiel:

```
Client A:
Garage öffnen
Client B:
Garage schließen
```

Die UI darf diesen Konflikt nicht unabhängig lösen.

⸻

## 21. Serielle Aktionen

Für bestimmte Aktoren kann es notwendig sein, Befehle seriell zu verarbeiten.

Beispiel:

Eine Garage darf möglicherweise keinen neuen Fahrbefehl erhalten, solange ein vorheriger Bewegungsablauf noch nicht abgeschlossen oder sicher abgebrochen wurde.

⸻

## 22. Sicherheitsbedingungen

Vor bestimmten Befehlen können Bedingungen geprüft werden.

Beispiel:

Markise ausfahren

kann später an Bedingungen gekoppelt sein.

Die konkrete Sicherheitslogik wird pro Gerät definiert.

Die UI allein ist niemals die einzige Sicherheitsinstanz.

⸻

## 23. State Store

Kehler OS benötigt konzeptionell eine zentrale Zustandsverwaltung.

Diese hält den aktuellen logischen Zustand des Systems bereit.

Beispiele:

```
energy.battery.soc
water.fresh.level
garage.state
network.plc.state
climate.interior.temperature
```

Die konkrete technische Implementierung wird später entschieden.

⸻

## 24. State Store ist nicht automatisch Datenbank

Der aktuelle Systemzustand und die historische Datenbank sind unterschiedliche Aufgaben.

Der State Store dient primär dem aktuellen Zustand.

Die Datenbank dient unter anderem der Historie und Persistenz.

Beide dürfen technisch zusammenhängen, sollen aber logisch getrennt betrachtet werden.

⸻

## 25. Neustart

Nach einem Neustart darf der aktuelle Fahrzeugzustand nicht blind aus einem gespeicherten State Store wiederhergestellt werden.

Physische Zustände müssen erneut mit der Hardware synchronisiert werden.

⸻

## 26. Wiederanlauf

Beim Systemstart können Zustände zunächst sein:

```
INITIALIZING
UNKNOWN
```

Danach werden sie mit den tatsächlichen Datenquellen synchronisiert.

⸻

## 27. Teilweise Synchronisation

Kehler OS muss auch dann starten können, wenn nur ein Teil der Hardware verfügbar ist.

Beispiel:

```
SPS: ONLINE
Victron: ONLINE
Kamera 2: OFFLINE
```

Der Rest des Systems bleibt funktionsfähig.

⸻

## 28. Realtime-Verteilung

Ändert sich ein Zustand, sollen verbundene Clients die Änderung zeitnah erhalten.

Beispiel:

```
SPS
↓
garage.state = OPENING
↓
Backend State
↓
Realtime Event
↓
iPad
↓
Smartphone
```

⸻

## 29. Keine unnötigen Vollupdates

Bei einer kleinen Zustandsänderung soll nicht automatisch der gesamte Fahrzeugzustand vollständig an alle Clients übertragen werden.

Wo sinnvoll sollen gezielte Zustandsänderungen übertragen werden.

⸻

## 30. Initialer Zustand eines Clients

Wenn ein neuer Client Kehler OS öffnet, benötigt er zunächst einen konsistenten Snapshot des aktuellen Systems.

Danach können nur noch Änderungen übertragen werden.

Konzeptionell:

```
Client verbindet sich
↓
Initial Snapshot
↓
Realtime Updates
```

⸻

## 31. Versionsstand des Zustands

Für die spätere technische Umsetzung soll geprüft werden, ob Zustände oder Snapshots versioniert werden müssen.

Dies kann helfen, Reihenfolgeprobleme und veraltete Updates zu vermeiden.

⸻

## 32. Reihenfolge von Ereignissen

Bei schnellen Zustandsänderungen muss die Reihenfolge erhalten bleiben.

Beispiel:

```
CLOSED
OPENING
OPEN
```

Die UI darf nicht aufgrund von Netzwerkverzögerungen anschließend wieder OPENING anzeigen, wenn OPEN bereits bestätigt wurde.

⸻

## 33. Idempotenz

Für geeignete Befehle soll später geprüft werden, ob sie idempotent gestaltet werden können.

Beispiel:

```
light.set_state(ON)
```

ist robuster als ein reines:

```
light.toggle()
```

wenn der tatsächliche Zustand eindeutig gesteuert werden soll.

⸻

## 34. TOGGLE vorsichtig verwenden

Toggle-Befehle können problematisch sein, wenn der aktuelle Zustand nicht zuverlässig bekannt ist.

Deshalb sollen nach Möglichkeit explizite Zustände verwendet werden:

```
ON
OFF
```

statt:

```
TOGGLE
```

sofern die Hardware dies unterstützt.

⸻

## 35. Sollwerte

Bei regelbaren Systemen soll zwischen aktuellem Wert und Sollwert unterschieden werden.

Beispiel Klima:

```
actual_temperature = 21.4 °C
target_temperature = 22.0 °C
```

⸻

## 36. Prozentwerte

Prozentwerte müssen eine klar definierte Bedeutung besitzen.

Beispiel:

```
battery.soc = 87 %
```

oder:

```
tank.fresh.level = 64 %
```

Es darf nicht unklar sein, ob ein Prozentwert Rohsensorwert, berechneter Wert oder tatsächliche Kapazität beschreibt.

⸻

## 37. Physikalische Werte

Wo möglich sollen zusätzlich reale physikalische Werte verwendet werden.

Beispiel:

```
fresh_water:
64 %
320 L
```

Dadurch erhält der Benutzer sowohl eine intuitive als auch eine konkrete Information.

⸻

## 38. Abgeleitete Werte

Kehler OS darf Werte aus mehreren Rohdaten berechnen.

Beispiele:

* Energieverbrauch heute
* Autarkiegrad
* geschätzte verbleibende Wassermenge
* Trend

Solche Werte müssen eindeutig als berechnete Werte behandelt werden.

⸻

## 39. Quelle berechneter Werte

Ein berechneter Wert besitzt als Quelle logisch Kehler OS beziehungsweise den entsprechenden Berechnungsdienst.

Er darf nicht fälschlich als direkter Sensorwert dargestellt werden.

⸻

## 40. Trends

Kehler OS kann aus historischen Messwerten Trends ableiten.

Beispiel:

```
Frischwasser
64 %
↓ 8 % seit gestern
```

Trendberechnungen dürfen nicht mit tatsächlichen Sensorzuständen vermischt werden.

⸻

## 41. Warnungen

Warnungen sind eigene Zustandsobjekte.

Eine Warnung soll logisch Informationen enthalten können wie:

* ID
* Typ
* Quelle
* Priorität
* Zeitpunkt
* Nachricht
* Status
* Quittierung

⸻

## 42. Warnungsstatus

Eine Warnung kann beispielsweise folgende Zustände besitzen:

```
ACTIVE
ACKNOWLEDGED
RESOLVED
```

Die konkrete spätere Struktur wird im Sicherheits- und Diagnosekapitel weiter konkretisiert.

⸻

## 43. Automatische Auflösung

Eine Warnung kann automatisch behoben werden, wenn die Ursache nicht mehr besteht.

Beispiel:

```
Grauwasser > 90 %
→ Warnung aktiv
Grauwasser nach Entleerung < Grenzwert
→ Warnung behoben
```

⸻

## 44. Quittierung

Quittierung bedeutet nicht automatisch, dass ein Fehler verschwunden ist.

Beispiel:

```
Alarm aktiv
↓
Benutzer quittiert
↓
Ursache besteht weiterhin
```

Dann bleibt der technische Fehler aktiv.

⸻

## 45. Ereignisse

Ein Ereignis beschreibt etwas, das zu einem bestimmten Zeitpunkt passiert ist.

Beispiel:

```
door.opened
```

Ein Zustand dagegen beschreibt, wie etwas aktuell ist:

```
door.state = OPEN
```

Diese beiden Konzepte dürfen nicht verwechselt werden.

⸻

## 46. Event History

Wichtige Ereignisse sollen später historisch nachvollziehbar sein.

Beispiel:

```
18:44:02 Garage OPENING
18:44:08 Garage OPEN
```

⸻

## 47. Zustandsänderung als Ereignis

Eine Zustandsänderung kann automatisch ein Ereignis erzeugen.

Beispiel:

```
garage.state
CLOSED → OPENING
```

kann ein entsprechendes Event erzeugen.

⸻

## 48. Benutzeraktionen

Benutzeraktionen sollen bei wichtigen Funktionen protokollierbar sein.

Beispiel:

```
Benutzer:
Philipp
Aktion:
Außenlicht eingeschaltet
Zeit:
...
```

⸻

## 49. Automatisierte Aktionen

Dasselbe gilt für Automatisierungen.

Beispiel:

```
Quelle:
Automation "Nacht"
Aktion:
Außenlicht ausgeschaltet
```

Dadurch kann später nachvollzogen werden, warum eine Aktion ausgeführt wurde.

⸻

## 50. Szenen

Szenen lösen mehrere Befehle aus.

Beispiel:

Szene: Abfahrt

kann enthalten:

```
Markise einfahren
Stufe einfahren
Außenlicht aus
Schränke verriegeln
```

Jeder Teilbefehl muss separat erfolgreich oder fehlerhaft sein können.

⸻

## 51. Teilweise erfolgreiche Szenen

Eine Szene darf nicht automatisch als komplett erfolgreich gelten, wenn nur einige Aktionen ausgeführt wurden.

Beispiel:

```
Abfahrt
Stufen: OK
Licht: OK
Markise: FEHLER
Garage: OK
```

Das System muss den Teilfehler erkennen.

⸻

## 52. Aggregate Zustände

Kehler OS kann mehrere Einzelzustände zu einem Gesamtzustand zusammenfassen.

Beispiel:

```
vehicle.lock_state
```

kann aus mehreren Schlössern berechnet werden.

Mögliche Werte:

```
ALL_LOCKED
PARTIALLY_LOCKED
UNLOCKED
UNKNOWN
```

⸻

## 53. System Health

Auch der Zustand des Gesamtsystems kann aggregiert werden.

Beispiel:

```
HEALTHY
DEGRADED
WARNING
CRITICAL
```

Dieser Wert wird aus mehreren technischen Zuständen abgeleitet.

⸻

## 54. DEGRADED

DEGRADED bedeutet beispielsweise:

Das System funktioniert grundsätzlich, aber eine nichtkritische Komponente ist ausgefallen.

Beispiel:

Kamera 3 offline

während alle Steuerfunktionen funktionieren.

⸻

## 55. CRITICAL

Ein kritischer Systemzustand soll nur für wirklich relevante Probleme verwendet werden.

Zu viele kritische Meldungen machen Prioritäten unbrauchbar.

⸻

## 56. Fahrzeugmodus

Die Architektur soll später verschiedene übergeordnete Fahrzeugmodi unterstützen können.

Beispiele:

```
PARKED
CAMPING
DRIVING
SERVICE
```

Die tatsächlichen Modi werden später definiert.

⸻

## 57. Modi und Funktionen

Ein Modus kann bestimmte Regeln beeinflussen.

Beispiel:

Im Fahrmodus kann eine ausgefahrene Markise besonders relevant sein.

Solche Regeln werden jedoch im Automatisierungs- und Sicherheitskapitel detaillierter definiert.

⸻

## 58. Konfiguration und Zustand trennen

Konfiguration beschreibt:

Wie soll etwas eingerichtet sein?

Zustand beschreibt:

Wie ist es gerade?

Beispiel:

```
Konfiguration:
Frischwassertank Kapazität = 500 L
Zustand:
Frischwasser = 320 L
```

Beides darf nicht vermischt werden.

⸻

## 59. Capabilities und Zustand trennen

Capabilities beschreiben, was ein Gerät grundsätzlich kann.

Beispiel:

```
Garage:
OPEN
CLOSE
STOP
```

Der aktuelle Zustand beschreibt dagegen:

```
Garage:
CLOSED
```

⸻

## 60. Dynamische Benutzeroberfläche

Die UI darf Informationen auf Basis von Zustand und Capabilities dynamisch darstellen.

Beispiel:

Wenn eine Hardware keinen Positionswert liefert, darf die UI keinen erfundenen Positionsregler anzeigen.

⸻

## 61. Simulation

Im Simulationsmodus muss der State Store simulierte Zustände verwenden können.

Diese Zustände müssen klar von realen Daten getrennt bleiben.

⸻

## 62. Simulationskennzeichnung

Im Entwicklungs- oder Simulationsmodus muss deutlich erkennbar sein, dass keine echte Fahrzeughardware gesteuert wird.

⸻

## 63. Diagnose

Für Diagnosezwecke soll später pro Zustand sichtbar sein können:

* aktueller Wert
* Datenquelle
* letzter Updatezeitpunkt
* Datenqualität
* Fehlerstatus

Dies gehört nicht zwingend in die normale Benutzeransicht.

⸻

## 64. Performance

Die Zustandsverwaltung muss auch mit vielen Datenpunkten effizient bleiben.

Nicht jeder Wert muss mit derselben Frequenz verarbeitet oder verteilt werden.

⸻

## 65. Änderungsbasierte Updates

Wo sinnvoll sollen nur tatsächliche Änderungen Events erzeugen.

Beispiel:

Wenn ein Türkontakt 60 Sekunden lang CLOSED bleibt, muss nicht jede Sekunde ein neues Tür-geschlossen-Ereignis erzeugt werden.

⸻

## 66. Messwerte sind Sonderfall

Kontinuierliche Messwerte können auch bei kleinen Änderungen relevant sein.

Für Zeitreihen müssen daher sinnvolle Sampling- und Speicherungskonzepte verwendet werden.

⸻

## 67. Deadband

Bei analogen Messwerten kann später ein Deadband sinnvoll sein.

Beispiel:

Temperaturänderungen von:

```
21.401
→ 21.402 °C
```

müssen nicht zwingend sofort einen sichtbaren UI-Update auslösen.

Die konkrete Schwelle hängt vom Sensor und Anwendungsfall ab.

⸻

## 68. Rate Limiting

Die Architektur soll verhindern, dass ein fehlerhafter Sensor oder Client das System mit extrem vielen Updates oder Befehlen überlastet.

⸻

## 69. Timeout

Für Aktionen und Datenquellen müssen sinnvolle Timeouts definiert werden.

Beispiel:

Wenn nach einem Garagenbefehl innerhalb einer definierten Zeit keine Rückmeldung erfolgt, muss der Befehl als problematisch erkannt werden.

⸻

## 70. Kein universelles Timeout

Nicht alle Geräte erhalten denselben Timeout.

Eine Lampe und ein hydraulisches Nivellierungssystem besitzen unterschiedliche physikalische Reaktionszeiten.

⸻

## 71. Persistenz

Bestimmte Zustände beziehungsweise Konfigurationen können persistent gespeichert werden.

Physische Live-Zustände müssen nach einem Neustart jedoch erneut validiert werden.

⸻

## 72. Auditierbarkeit

Für relevante Aktionen soll später nachvollziehbar sein:

```
Wer?
Was?
Wann?
Warum?
Ergebnis?
```

Dies erhöht Sicherheit und Diagnosefähigkeit.

⸻

## 73. Zukunftsfähigkeit

Das Zustandsmodell muss später zusätzliche Funktionen ermöglichen.

Beispiele:

* weitere Fahrzeuge
* zusätzliche SPS
* neue Geräte
* Remote-Clients
* KI-Analyse
* Predictive Maintenance

⸻

## 74. Konsistente Semantik

Ein Begriff muss überall dieselbe Bedeutung besitzen.

Wenn OFFLINE in einem Modul „keine Kommunikation“ bedeutet, darf er in einem anderen Modul nicht etwas völlig anderes bedeuten.

⸻

## 75. Maschinenlesbar und menschenlesbar

Intern sollen Zustände eindeutig maschinenlesbar sein.

Die UI übersetzt sie in verständliche Begriffe.

Beispiel intern:

```
PARTIALLY_LOCKED
```

UI:

```
Nicht alle Verriegelungen geschlossen
```

⸻

## 76. Keine Displaytexte als interne Logik

Programmlogik darf nicht davon abhängig sein, dass ein sichtbarer deutscher Text exakt gleich bleibt.

Die UI-Texte sind Darstellung.

Die internen Zustände sind technische Identitäten.

⸻

## 77. Mehrsprachigkeit

Weil Zustände intern unabhängig von sichtbaren Texten sind, kann die Oberfläche später problemlos mehrere Sprachen unterstützen.

⸻

## 78. Grundsatz

Das Kernprinzip dieses Kapitels lautet:

Kehler OS reagiert nicht auf das, was die UI glaubt, sondern auf den zentral verwalteten, validierten tatsächlichen Systemzustand.

⸻

## 79. Zielbild

Ein Benutzer öffnet Kehler OS auf einem iPad.

Gleichzeitig ist die App auf einem Smartphone geöffnet.

Das Garagentor wird über das iPad geöffnet.

Der Ablauf ist:

```
iPad
↓
OPEN Command
↓
Backend
↓
SPS
↓
Garagentor beginnt Bewegung
↓
SPS meldet OPENING
↓
zentraler State Store
↓
iPad zeigt OPENING
↓
Smartphone zeigt OPENING
↓
Fahrzeuganimation zeigt Öffnung
↓
SPS meldet OPEN
↓
State Store = OPEN
↓
alle Clients = OPEN
```

Kein Client besitzt eine eigene konkurrierende Wahrheit.

⸻

## Ende Kapitel 13

Dieses Kapitel definiert die Zustandsverwaltung von Kehler OS.

Besonders festgelegt wurden:

* zentrale Wahrheit für aktuelle Zustände
* Trennung von gewünschtem und tatsächlichem Zustand
* Zustandsmaschinen
* Datenqualität
* Befehlslebenszyklus
* mehrere Clients
* Realtime-Synchronisation
* Events versus Zustände
* Aggregate Zustände
* Warnungszustände
* Simulation
* Neustartsynchronisation
* Trennung von Konfiguration, Capabilities und Live-Zustand
* Auditierbarkeit
* konsistente interne Semantik

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf Kapitel 14.

Verwende Kapitel 1 bis 13 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
