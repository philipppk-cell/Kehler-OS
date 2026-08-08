# KEHLER OS

# Kapitel 14 – Automatisierungen, Szenen und Fahrzeuglogik

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel beschreibt die Anforderungen an Automatisierungen, Szenen, Regeln und übergeordnete Fahrzeuglogik.

Verwende Kapitel 1–14 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel

Kehler OS soll nicht nur Fahrzeugzustände anzeigen und manuelle Befehle ausführen.

Es soll das Fahrzeug intelligent automatisieren können.

Dabei gilt:

Automatisierung soll den Benutzer unterstützen, nicht die Kontrolle übernehmen.

Der Benutzer muss jederzeit nachvollziehen können, warum eine automatische Aktion ausgeführt wurde.

⸻

## 2. Grundprinzip einer Automatisierung

Eine Automatisierung besteht logisch aus:

```
TRIGGER
↓
CONDITIONS
↓
ACTIONS
```

Beispiel:

```
TRIGGER:
Batterieladezustand verändert
CONDITION:
SOC < 20 %
ACTION:
Warnung erzeugen
```

⸻

## 3. Trigger

Ein Trigger startet die Prüfung einer Automatisierung.

Trigger können beispielsweise sein:

* Zustandsänderung
* Messwertänderung
* Ereignis
* Uhrzeit
* Datum
* Fahrzeugmodus
* Benutzeraktion
* Netzwerkzustand
* Verbindung eines Geräts

⸻

## 4. Zustandsbasierte Trigger

Beispiele:

```
door.main = OPEN
garage.state = OPEN
shore_power = CONNECTED
battery.soc < threshold
```

⸻

## 5. Zeitbasierte Trigger

Automatisierungen sollen auch zeitabhängig sein können.

Beispiele:

```
22:00 Uhr
Sonnenuntergang
jeden Morgen
```

Die konkrete Zeitlogik wird später technisch definiert.

⸻

## 6. Bedingungen

Ein Trigger allein muss nicht automatisch eine Aktion auslösen.

Zusätzliche Bedingungen können geprüft werden.

Beispiel:

```
TRIGGER:
Tür geöffnet
CONDITION:
Fahrzeugmodus = CAMPING
ACTION:
Eingangslicht einschalten
```

⸻

## 7. Mehrere Bedingungen

Eine Automatisierung soll mehrere Bedingungen kombinieren können.

Beispiel:

```
battery.soc < 20 %
AND
shore_power = DISCONNECTED
```

⸻

## 8. Logische Operatoren

Die Regelarchitektur soll grundsätzlich logische Kombinationen unterstützen können.

Beispiele:

```
AND
OR
NOT
```

Die Benutzeroberfläche soll diese später verständlich darstellen.

⸻

## 9. Aktionen

Eine Automatisierung kann eine oder mehrere Aktionen ausführen.

Beispiele:

* Licht schalten
* Wasserpumpe steuern
* Benachrichtigung erzeugen
* Szene starten
* Modus wechseln
* Sollwert verändern
* Systemstatus markieren

Nur technisch erlaubte Aktionen dürfen ausgeführt werden.

⸻

## 10. Mehrere Aktionen

Eine Regel kann mehrere Aktionen enthalten.

Beispiel:

```
Wenn Nachtmodus aktiviert:
→ Außenlicht AUS
→ Innenbeleuchtung reduzieren
→ Türen prüfen
→ Display dimmen
```

⸻

## 11. Reihenfolge von Aktionen

Bei bestimmten Automatisierungen ist die Reihenfolge wichtig.

Beispiel:

```
Szene ABFAHRT
1. Markise einfahren
2. auf Rückmeldung warten
3. Stufen einfahren
4. Verriegelungen prüfen
5. Warnungen auswerten
```

Eine Szene darf nicht grundsätzlich alle Aktionen gleichzeitig starten.

⸻

## 12. Parallele Aktionen

Andere Aktionen dürfen parallel ausgeführt werden, wenn keine Abhängigkeit besteht.

Beispiel:

```
Innenbeleuchtung AUS
Außenbeleuchtung AUS
```

kann möglicherweise gleichzeitig erfolgen.

⸻

## 13. Abhängigkeiten

Einzelne Aktionen können Voraussetzungen besitzen.

Beispiel:

Eine Folgeaktion darf erst ausgeführt werden, wenn eine vorherige Aktion erfolgreich abgeschlossen wurde.

⸻

## 14. Fehler innerhalb einer Automatisierung

Automatisierungen müssen Fehler erkennen.

Beispiel:

```
Markise einfahren
→ TIMEOUT
```

Die Automatisierung darf nicht einfach so tun, als sei der Schritt erfolgreich.

⸻

## 15. Fehlerstrategie

Für Automatisierungen soll definiert werden können, was bei einem Fehler passiert.

Mögliche Strategien:

```
STOP
CONTINUE
RETRY
NOTIFY
ROLLBACK
```

Nicht jede Strategie ist für jede Aktion sinnvoll.

⸻

## 16. Wiederholungen

Bestimmte fehlgeschlagene Aktionen können automatisch erneut versucht werden.

Die Anzahl und Zeitabstände müssen begrenzt sein.

Es darf keine unkontrollierte Endlosschleife entstehen.

⸻

## 17. Sicherheitsrelevante Wiederholungen

Bei mechanischen Aktoren muss besonders vorsichtig mit automatischen Wiederholungen umgegangen werden.

Ein blockiertes Garagentor darf beispielsweise nicht permanent erneut angesteuert werden.

⸻

## 18. Szenen

Eine Szene fasst mehrere gewünschte Fahrzeugzustände beziehungsweise Aktionen zusammen.

Szenen sollen schnell ausführbar sein.

⸻

## 19. Mögliche Szenen

Beispiele:

```
ANKUNFT
ABFAHRT
NACHT
MORGEN
CAMPING
ALLES AUS
```

Dies sind Beispiele und keine endgültige Liste.

⸻

## 20. Szene ABFAHRT

Eine spätere Abfahrts-Szene könnte beispielsweise relevante Systeme prüfen beziehungsweise steuern.

Mögliche Punkte:

* Markise
* Stufen
* Garage
* Türen
* Fenster
* Schrankverriegelungen
* Außenbeleuchtung
* weitere aufbaurelevante Funktionen

Die endgültige Logik hängt von der realen Hardware ab.

⸻

## 21. Abfahrt als Prüfung statt blindem Befehl

Die Abfahrtsfunktion soll nicht lediglich Befehle senden.

Sie soll auch überprüfen, ob das Fahrzeug tatsächlich abfahrbereit ist.

Beispiel:

```
Markise: EINGEFAHREN
Stufen: EINGEFAHREN
Garage: GESCHLOSSEN
Fenster: ALLE GESCHLOSSEN
Schränke: VERRIEGELT
```

⸻

## 22. Abfahrbereitschaft

Kehler OS soll langfristig einen aggregierten Zustand bilden können:

```
READY_TO_DRIVE
```

oder:

```
NOT_READY_TO_DRIVE
```

Dieser Zustand wird aus realen Hardwareinformationen abgeleitet.

⸻

## 23. Fehlende Sensorik

Wenn für eine wichtige Prüfung keine Sensorik vorhanden ist, darf Kehler OS nicht behaupten, der Zustand sei sicher.

Beispiel:

Keine Rückmeldung von der Markise:

UNKNOWN

nicht:

EINGEFAHREN

⸻

## 24. Szene ANKUNFT

Eine Ankunftsszene könnte beispielsweise:

* bestimmte Beleuchtung aktivieren
* Fahrzeugmodus auf CAMPING setzen
* Systemstatus prüfen
* Klima vorbereiten

Welche Aktionen tatsächlich sinnvoll sind, soll später konfiguriert werden.

⸻

## 25. Szene NACHT

Eine Nachtszene könnte beispielsweise:

* Innenbeleuchtung reduzieren
* Außenbeleuchtung ausschalten
* Türen und Fenster prüfen
* Displayhelligkeit reduzieren
* Klima auf Nacht-Sollwert setzen

Die konkrete Ausgestaltung bleibt konfigurierbar.

⸻

## 26. Szenen sind konfigurierbar

Szenen dürfen nicht vollständig fest im Programm verankert sein.

Sie sollen später angepasst werden können.

⸻

## 27. Standard- und Benutzerszenen

Das System soll perspektivisch unterscheiden können zwischen:

```
SYSTEM_SCENE
USER_SCENE
```

System-Szenen können wichtige vorbereitete Abläufe darstellen.

Benutzer-Szenen können individuell erstellt werden.

⸻

## 28. Automatisierungen aktivieren/deaktivieren

Jede benutzerdefinierte Automatisierung soll grundsätzlich aktiviert oder deaktiviert werden können.

Beispiel:

```
Nachtbeleuchtung
AKTIV
```

⸻

## 29. Pausieren

Es kann sinnvoll sein, Automatisierungen temporär zu pausieren.

Beispielsweise während:

* Wartung
* Reparaturen
* Tests
* Servicearbeiten

⸻

## 30. Service-Modus

Im Service-Modus sollen bestimmte Automatisierungen deaktiviert beziehungsweise anders behandelt werden können.

Dadurch wird verhindert, dass automatische Prozesse Wartungsarbeiten stören.

⸻

## 31. Fahrzeugmodi

Kehler OS soll übergeordnete Fahrzeugmodi unterstützen.

Mögliche Modi:

```
DRIVING
PARKED
CAMPING
NIGHT
SERVICE
```

Die endgültige Liste wird später festgelegt.

⸻

## 32. Modus ist mehr als eine Szene

Eine Szene führt Aktionen aus.

Ein Modus beschreibt dagegen einen länger bestehenden Betriebszustand des Fahrzeugs.

Beispiel:

CAMPING

kann mehrere Stunden oder Tage aktiv sein.

⸻

## 33. Modusabhängige Regeln

Automatisierungen können vom Fahrzeugmodus abhängig sein.

Beispiel:

```
Wenn Tür geöffnet
UND Modus = NIGHT
→ nur schwaches Eingangslicht
```

⸻

## 34. Fahrmodus

Der Fahrmodus ist besonders wichtig.

In diesem Modus können bestimmte Zustände besonders relevant sein.

Beispiele:

* Markise ausgefahren
* Stufen ausgefahren
* Garage offen
* Fenster offen
* nicht verriegelte Schränke

⸻

## 35. Keine automatische Fahrzustandsannahme

Der Fahrmodus soll später auf einer zuverlässigen Quelle beruhen.

Claude darf nicht ohne reale Datenquelle annehmen, wann das Fahrzeug fährt.

Mögliche Quellen werden erst bei der tatsächlichen Hardwareintegration festgelegt.

⸻

## 36. Automatische Warnungen im Fahrmodus

Bestimmte Zustände können im Stand normal, während der Fahrt aber kritisch sein.

Beispiel:

Garage OPEN

im Campingmodus:

möglicherweise normal.

Im Fahrmodus:

KRITISCH

⸻

## 37. Kontextabhängige Priorität

Die Priorität einer Warnung kann vom aktuellen Fahrzeugmodus abhängen.

Das Warnungssystem muss dies berücksichtigen können.

⸻

## 38. Manuelle Kontrolle bleibt erhalten

Automatisierungen dürfen die manuelle Bedienung nicht unnötig verhindern.

Wenn eine Funktion manuell bedienbar sein soll, muss der Benutzer dies weiterhin tun können.

⸻

## 39. Automatisierungs-Override

Das System soll später definieren können, wie ein manueller Eingriff mit einer aktiven Automatisierung interagiert.

Beispiel:

Automatisierung:

Außenlicht AUS

Benutzer:

Außenlicht EIN

Es muss klar sein, ob die Automatisierung sofort erneut eingreift oder der manuelle Befehl vorübergehend Vorrang erhält.

⸻

## 40. Keine unerwarteten Gegenschaltungen

Kehler OS soll vermeiden, dass der Benutzer ein Gerät einschaltet und es eine Sekunde später scheinbar grundlos automatisch wieder ausgeschaltet wird.

Solches Verhalten muss transparent sein.

⸻

## 41. Erklärung automatischer Aktionen

Automatische Aktionen sollen nachvollziehbar sein.

Beispiel:

```
Außenlicht wurde ausgeschaltet.
Grund:
Szene "Nacht"
```

⸻

## 42. Historie

Automatisierungen sollen in der Ereignishistorie nachvollziehbar sein.

Beispiel:

```
22:00:00
Automation "Nacht" gestartet
22:00:01
Außenlicht AUS
22:00:02
Displayhelligkeit auf 20 %
22:00:03
Automation erfolgreich abgeschlossen
```

⸻

## 43. Manuell gestartete Szene

Die Historie soll unterscheiden können:

Szene automatisch gestartet

und:

Szene durch Benutzer gestartet

⸻

## 44. Automatisierungs-ID

Jede Regel beziehungsweise Szene soll eine eindeutige Identität besitzen.

Dadurch können Logs, Fehler und Aktionen eindeutig zugeordnet werden.

⸻

## 45. Namen

Benutzer sollen Automatisierungen verständlich benennen können.

Beispiel:

Nachtmodus

statt einer internen technischen ID.

Intern muss dennoch eine stabile eindeutige Kennung existieren.

⸻

## 46. Trigger-Hysterese

Bei analogen Werten muss verhindert werden, dass eine Automatisierung ständig ein- und ausschaltet, wenn ein Wert unmittelbar um einen Grenzwert schwankt.

Beispiel:

Nicht:

```
SOC 19.9 %
→ Warnung
SOC 20.1 %
→ Warnung weg
SOC 19.9 %
→ Warnung
...
```

Hierfür können geeignete Hysterese-Mechanismen verwendet werden.

⸻

## 47. Beispiel Hysterese

Konzeptionell:

```
Warnung aktivieren:
SOC < 20 %
Warnung zurücksetzen:
SOC > 23 %
```

Die konkreten Werte sind konfigurierbar.

⸻

## 48. Debouncing

Digitale Sensoren können kurzzeitig schwanken.

Beispielsweise Türkontakte.

Das System soll bei Bedarf Debouncing unterstützen können.

⸻

## 49. Verzögerungen

Regeln können eine Verzögerung benötigen.

Beispiel:

```
Wenn Tür länger als 5 Minuten offen
→ Warnung
```

Nicht bereits beim kurzen Öffnen.

⸻

## 50. Dauerbedingungen

Eine Automatisierung muss deshalb Bedingungen wie:

Zustand besteht seit X Sekunden/Minuten

unterstützen können.

⸻

## 51. Cooldown

Für bestimmte Automatisierungen kann ein Cooldown notwendig sein.

Beispiel:

Eine Warnung soll nicht jede Sekunde erneut erzeugt werden.

⸻

## 52. Rate Limiting

Das Automatisierungssystem darf nicht hunderte identische Benachrichtigungen erzeugen.

⸻

## 53. Endlosschleifen

Das System muss verhindern beziehungsweise erkennen, dass sich Regeln gegenseitig in einer Endlosschleife auslösen.

Beispiel:

```
Regel A:
Wenn Licht AUS → Licht EIN
Regel B:
Wenn Licht EIN → Licht AUS
```

Solche Konfigurationen müssen erkannt oder begrenzt werden.

⸻

## 54. Rekursion

Automatisierungen, die Szenen oder andere Automatisierungen starten, dürfen keine unbegrenzte Rekursion erzeugen.

⸻

## 55. Prioritäten

Automatisierungen können unterschiedliche Prioritäten besitzen.

Eine sicherheitsrelevante Systemregel muss eine normale Komfortautomatisierung übersteuern können.

⸻

## 56. Beispiel Priorität

```
Komfortregel:
Markise ausfahren
Sicherheitsregel:
Markise darf nicht ausfahren
```

Die Sicherheitsregel hat Vorrang.

⸻

## 57. Systemregeln

Einige Regeln sind Teil der internen Fahrzeuglogik und nicht normale Benutzerautomatisierungen.

Diese können beispielsweise:

* Sicherheitsprüfungen
* Systemschutz
* Zustandsüberwachung

übernehmen.

Sie dürfen nicht beliebig durch einen normalen Benutzer verändert werden.

⸻

## 58. Benutzerregeln

Benutzerregeln dienen hauptsächlich:

* Komfort
* Szenen
* Benachrichtigungen
* individuelle Abläufe

Sie müssen innerhalb der vom System erlaubten Grenzen bleiben.

⸻

## 59. Sicherheitsgrenzen

Keine benutzerdefinierte Automatisierung darf Sicherheitsbedingungen umgehen.

Beispiel:

Eine Benutzerregel darf keinen Aktor erzwingen, wenn die SPS beziehungsweise Systemlogik die Bewegung aus Sicherheitsgründen blockiert.

⸻

## 60. SPS bleibt letzte Instanz für passende Echtzeit-Sicherheitslogik

Zeitkritische und hardwareabhängige Verriegelungen gehören nicht ausschließlich in das Kehler-OS-Automatisierungssystem.

Beispiel:

```
Kehler OS
→ fordert Bewegung an
SPS
→ prüft lokale Freigaben
→ führt nur bei gültigen Bedingungen aus
```

⸻

## 61. Wetterabhängige Automatisierungen

Später könnten Wetterdaten für Komfortfunktionen verwendet werden.

Beispiel:

* Außentemperatur
* Regen
* Wind

Diese Daten können internet- oder sensorbasiert sein.

Internetbasierte Wetterdaten dürfen jedoch nicht als alleinige Sicherheitsquelle für kritische Bewegungen dienen.

⸻

## 62. Lokale Sensorik hat Vorrang für kritische Funktionen

Wenn eine Funktion physisch sicherheitsrelevant ist, muss nach Möglichkeit lokale zuverlässige Sensorik verwendet werden.

⸻

## 63. Energieautomatisierungen

Kehler OS soll Energiezustände für Automatisierungen verwenden können.

Beispiele:

```
Wenn Batterie niedrig
→ bestimmte nichtkritische Verbraucher abschalten
```

oder:

```
Wenn Landstrom angeschlossen
→ Komfortfunktionen freigeben
```

Die tatsächlich erlaubten Steuerungen hängen von der Hardware ab.

⸻

## 64. Lastmanagement

Langfristig kann Kehler OS ein Lastmanagement unterstützen.

Dabei könnten Verbraucher nach Prioritäten behandelt werden.

Beispiel:

```
Priorität 1:
kritische Systeme
Priorität 2:
Grundversorgung
Priorität 3:
Komfort
```

Die konkrete Logik wird erst definiert, wenn die realen steuerbaren Lasten bekannt sind.

⸻

## 65. Wasserautomatisierungen

Mögliche Wasserregeln:

```
Frischwasser niedrig
→ Hinweis
Grauwasser hoch
→ Warnung
```

Das System soll solche Schwellen konfigurierbar unterstützen.

⸻

## 66. Klimaautomatisierungen

Das Klimasystem kann automatisiert werden.

Beispiele:

```
Wenn Temperatur unter Sollwert
→ Heizung anfordern
Wenn Temperatur im Zielbereich
→ Regelung entsprechend anpassen
```

Die tatsächliche Regelungslogik hängt von der Hardware ab.

⸻

## 67. Keine unpassende Regelung im Backend

Wenn ein vorhandenes Heiz- oder Klimagerät bereits eine eigene geeignete Regelung besitzt, soll Kehler OS diese nicht unnötig nachbauen.

Kehler OS kann dann primär Sollwerte und Betriebsmodi vorgeben.

⸻

## 68. Lichtautomatisierungen

Licht eignet sich besonders für Komfortautomatisierungen.

Beispiele:

* Türöffnung
* Nachtmodus
* Szenen
* Uhrzeiten
* Fahrzeugmodus

⸻

## 69. Verriegelungsautomatisierungen

Verriegelungen benötigen erhöhte Vorsicht.

Ein automatischer Verriegelungsbefehl muss sicherstellen, dass keine ungewollte beziehungsweise gefährliche Situation entsteht.

Die konkrete Logik muss später anhand der realen Mechanik festgelegt werden.

⸻

## 70. Nivellierungsautomatik

Die automatische Nivellierung ist eine komplexe Fahrzeugautomatisierung.

Sie darf nicht als einfache Benutzerregel umgesetzt werden.

Sie benötigt eine eigene spezialisierte Steuerlogik.

⸻

## 71. Aufgaben Kehler OS bei Nivellierung

Kehler OS kann beispielsweise:

* automatische Nivellierung starten
* aktuellen Vorgang anzeigen
* Zielzustand darstellen
* Fehler anzeigen
* Abbruch anfordern

Die eigentliche Bewegung und Regelung muss auf einer dafür geeigneten Steuerungsebene erfolgen.

⸻

## 72. Abbruch

Automatisierte mechanische Abläufe benötigen grundsätzlich eine definierte Abbruchmöglichkeit, sofern technisch relevant.

⸻

## 73. Not-Stopp versus normaler Abbruch

Ein normaler Software-Abbruch ist nicht automatisch ein sicherheitstechnischer Not-Stopp.

Falls ein echter Not-Stopp erforderlich ist, muss dieser entsprechend hardwareseitig ausgelegt werden.

Kehler OS darf keinen Softwarebutton fälschlich als sicherheitszertifizierten Not-Stopp darstellen.

⸻

## 74. Simulation von Automatisierungen

Im Entwicklungsmodus sollen Automatisierungen mit simulierten Zuständen getestet werden können.

Beispiel:

```
Simuliere:
battery.soc = 15 %
```

Dann kann geprüft werden, welche Regel reagieren würde.

⸻

## 75. Dry Run

Es soll später geprüft werden, ob ein Dry-Run-Modus sinnvoll ist.

Dabei wird eine Automatisierung ausgewertet, ohne reale Aktoren zu steuern.

Beispiel:

```
Diese Regel würde ausführen:
- Außenlicht AUS
- Wasserpumpe AUS
- Nachtmodus aktivieren
```

⸻

## 76. Validierung vor Aktivierung

Eine neu erstellte Automatisierung soll vor der Aktivierung auf offensichtliche Fehler geprüft werden.

Beispiele:

* fehlender Trigger
* unbekanntes Gerät
* nicht unterstützte Aktion
* ungültiger Wert
* zirkuläre Abhängigkeit

⸻

## 77. Versionsverwaltung

Es soll später möglich sein, Änderungen an wichtigen Automatisierungen nachvollziehbar zu machen.

Die konkrete Umsetzung wird später entschieden.

⸻

## 78. Backup

Benutzerdefinierte Regeln und Szenen gehören zu den wichtigen Konfigurationsdaten und müssen durch Backups gesichert werden können.

⸻

## 79. Import und Export

Langfristig kann ein Import-/Exportmechanismus für Szenen und Automatisierungen sinnvoll sein.

Dies ist keine zwingende Funktion der ersten Version, die Architektur darf sie jedoch nicht unnötig verhindern.

⸻

## 80. Berechtigungen

Nicht jeder Benutzer darf zwangsläufig:

* neue Automatisierungen erstellen
* Systemregeln verändern
* sicherheitsrelevante Regeln deaktivieren

Die Berechtigungsarchitektur wird in Kapitel 15 weiter definiert.

⸻

## 81. UI für Automatisierungen

Die Benutzeroberfläche zur Erstellung von Regeln soll verständlich bleiben.

Der normale Benutzer soll keine Programmiersprache lernen müssen.

Konzeptionell beispielsweise:

```
WENN
Batterie
unter
20 %
DANN
Warnung anzeigen
```

Die genaue UI-Gestaltung bleibt Claude überlassen.

⸻

## 82. Expertenmodus

Für komplexere Automatisierungen kann später ein erweiterter Modus sinnvoll sein.

Die normale Bedienoberfläche muss dadurch nicht komplizierter werden.

⸻

## 83. KI und Automatisierungen

Ein zukünftiger KI-Assistent kann dem Benutzer helfen, Regeln zu erstellen.

Beispiel Benutzer:

Wenn nachts die Tür geöffnet wird,
mach das Eingangslicht für fünf Minuten an.

Kehler OS könnte daraus eine Regel vorschlagen.

Die KI darf eine sicherheitsrelevante Automatisierung jedoch nicht unkontrolliert aktivieren.

⸻

## 84. KI erzeugt Vorschlag, System validiert

Langfristig gilt:

```
Benutzer
↓
KI interpretiert Wunsch
↓
Regelvorschlag
↓
Validierung
↓
Benutzerbestätigung
↓
Aktivierung
```

⸻

## 85. Transparenz

Der Benutzer muss jederzeit sehen können:

* welche Automatisierungen aktiv sind
* welche gerade ausgeführt werden
* welche zuletzt ausgelöst wurden
* welche fehlerhaft sind

⸻

## 86. Systemstatus einer Automation

Eine Automation kann beispielsweise besitzen:

```
ACTIVE
DISABLED
RUNNING
ERROR
PAUSED
```

⸻

## 87. Letzte Ausführung

Für Diagnose und Transparenz sollen Informationen verfügbar sein wie:

```
Letzte Ausführung:
Heute 22:00
Ergebnis:
Erfolgreich
```

⸻

## 88. Fehlerdarstellung

Wenn eine Automation fehlschlägt, soll der Benutzer verstehen können, warum.

Nicht nur:

```
Automation Error 0x39
```

Sondern beispielsweise:

```
Szene "Abfahrt" konnte nicht vollständig ausgeführt werden.
Markise:
Keine Rückmeldung.
```

⸻

## 89. Keine Alarmmüdigkeit

Automatisierungen dürfen nicht zu einer Flut unwichtiger Meldungen führen.

Benachrichtigungen müssen priorisiert und sinnvoll eingesetzt werden.

⸻

## 90. Ereigniszusammenfassung

Wenn mehrere ähnliche Ereignisse auftreten, kann eine sinnvolle Zusammenfassung besser sein als viele einzelne Meldungen.

⸻

## 91. Offlinebetrieb

Lokale Automatisierungen müssen ohne Internet funktionieren.

Beispiele:

* Licht
* Tanks
* Verriegelungen
* Warnungen
* lokale Sensorregeln

dürfen nicht von Cloudservices abhängig sein.

⸻

## 92. Internetabhängige Regeln

Falls eine Regel externe Daten benötigt, muss klar erkennbar sein, dass sie bei fehlender Internetverbindung gegebenenfalls nicht vollständig funktioniert.

⸻

## 93. Fail-Safe-Verhalten

Wenn eine benötigte Datenquelle ausfällt, darf das System keine gefährlichen Annahmen treffen.

Beispiel:

Winddaten UNKNOWN

darf nicht automatisch bedeuten:

Wind = 0

⸻

## 94. UNKNOWN in Automatisierungen

Regeln müssen explizit mit unbekannten Zuständen umgehen können.

Ein UNKNOWN darf nicht automatisch als FALSE, 0 oder OFF interpretiert werden, wenn dadurch ein unsicheres Verhalten entstehen könnte.

⸻

## 95. Priorität der Sicherheit

Bei Konflikten gilt:

```
Sicherheit
>
Systemschutz
>
Benutzerbefehl
>
Komfortautomation
```

Die konkrete Prioritätsstruktur kann später verfeinert werden.

⸻

## 96. Automatisierungen als separater Systemdienst

Das Automatisierungssystem soll logisch von UI und Hardwaretreibern getrennt sein.

Konzeptionell:

```
Sensoren / State
      ↓
Automation Engine
      ↓
Commands
      ↓
Command Processing
      ↓
Hardware
```

⸻

## 97. Automation Engine arbeitet mit logischen Zuständen

Eine Regel darf nicht direkt auf SPS-Adressen zugreifen.

Nicht:

```
DB10.DBX4.2 = 1
```

Sondern:

```
garage.state = OPEN
```

⸻

## 98. Hardwareabstraktion bleibt erhalten

Damit kann eine Automatisierung auch dann weiter funktionieren, wenn die dahinterliegende Hardware später geändert wird.

⸻

## 99. Performance

Die Automatisierungsengine muss viele Regeln verarbeiten können, ohne die Bedienoberfläche oder Hardwarekommunikation zu blockieren.

⸻

## 100. Deterministisches Verhalten

Bei identischen Zuständen und Regeln soll die Automation Engine nachvollziehbar reagieren.

Automatisierungen dürfen nicht zufällig unterschiedliche Entscheidungen treffen.

⸻

## 101. Kein generatives KI-Modell im kritischen Echtzeitpfad

Ein KI-Modell darf nicht die einzige Instanz sein, die in Echtzeit entscheidet, ob ein sicherheitsrelevanter Aktor bewegt werden darf.

Solche Regeln müssen deterministisch definiert sein.

⸻

## 102. KI als Komfort- und Assistenzebene

KI kann:

* Vorschläge machen
* Informationen erklären
* Trends erkennen
* Regeln generieren
* Diagnose unterstützen

Die tatsächliche Freigabe sicherheitsrelevanter Vorgänge bleibt bei deterministischer Logik.

⸻

## 103. Zielbild

Der Benutzer soll Kehler OS beispielsweise sagen beziehungsweise konfigurieren können:

Wenn wir nachts campen und die Eingangstür geöffnet wird,
schalte das Eingangslicht für fünf Minuten ein.

Kehler OS übersetzt dies in eine nachvollziehbare Regel:

```
TRIGGER:
main_door → OPEN
CONDITIONS:
vehicle_mode = NIGHT
ACTIONS:
entry_light = ON
wait 5 min
entry_light = OFF
```

Der Benutzer kann sehen:

* was die Regel macht
* wann sie aktiv ist
* wann sie zuletzt lief
* ob sie erfolgreich war

⸻

## 104. Zweites Zielbild: Abfahrt

Der Benutzer wählt:

ABFAHRT

Kehler OS prüft und steuert nacheinander die relevanten Aufbausysteme.

Am Ende wird nicht einfach „Fertig“ angezeigt.

Stattdessen entsteht beispielsweise:

```
ABFAHRTSCHECK
Markise              ✓
Stufen               ✓
Garage               ✓
Fenster              ✓
Schrankverriegelung  ✓
FAHRZEUG BEREIT
```

Wenn etwas nicht stimmt:

```
ABFAHRTSCHECK
Markise              ✓
Stufen               ✓
Garage               ✕
Fenster               ✓
NICHT ABFAHRBEREIT
Garage konnte nicht als geschlossen bestätigt werden.
```

Der reale Hardwarezustand ist entscheidend.

⸻

## 105. Grundsatz

Das zentrale Prinzip lautet:

Kehler OS darf intelligent automatisieren, muss aber immer nachvollziehbar, deterministisch und sicher bleiben.

Komfort darf niemals die technische Sicherheit verdrängen.

⸻

## Ende Kapitel 14

Dieses Kapitel definiert die Anforderungen an:

* Automatisierungsregeln
* Trigger
* Bedingungen
* Aktionen
* Szenen
* Fahrzeugmodi
* Abfahrtscheck
* Fehlerbehandlung
* Hysterese
* Debouncing
* Cooldowns
* Konfliktauflösung
* Prioritäten
* lokale Offline-Automatisierungen
* Sicherheit
* Simulation
* KI-Unterstützung
* Transparenz und Historie

Automatisierungen arbeiten ausschließlich mit logischen Kehler-OS-Zuständen und Befehlen.

Direkter Zugriff auf SPS-Adressen oder andere Hardwaredetails ist nicht zulässig.

Zeitkritische und sicherheitsrelevante Schutzlogik verbleibt auf der dafür geeigneten Steuerungsebene.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf Kapitel 15.

Verwende Kapitel 1 bis 14 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
