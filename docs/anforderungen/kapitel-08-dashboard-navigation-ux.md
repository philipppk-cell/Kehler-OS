# KEHLER OS

# Kapitel 8 – Dashboard, Navigation und User Experience

> Hinweis zur Übermittlung:
> Zu diesem Kapitel wurde ein Dashboard-Bild als verbindliche visuelle
> Designreferenz mitgeliefert (siehe Abschnitt 2 dieses Kapitels sowie den
> Anhang „Designreferenz“ am Ende dieses Dokuments).

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Treffe noch keine endgültigen technischen Implementierungsentscheidungen.

Dieses Kapitel beschreibt das gewünschte Verhalten, die Struktur und die User Experience von Kehler OS.

Verwende Kapitel 1–8 gemeinsam als verbindliche Grundlage.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Grundidee des Dashboards

Das Dashboard ist die zentrale Startseite von Kehler OS.

Es stellt den aktuellen Zustand des gesamten Fahrzeugs auf einen Blick dar.

Der Benutzer soll nach dem Öffnen des Systems innerhalb weniger Sekunden erkennen können:

* Wie geht es dem Fahrzeug?
* Wie ist der Energiezustand?
* Wie ist die Wassersituation?
* Wie ist das Klima?
* Ist das Fahrzeug sicher?
* Gibt es Warnungen?
* Gibt es etwas, das Aufmerksamkeit benötigt?
* Welche wichtigen Funktionen können schnell bedient werden?

Das Dashboard darf nicht versuchen, sämtliche verfügbaren Informationen gleichzeitig darzustellen.

Es soll die wichtigsten Informationen priorisieren.

⸻

## 2. Verbindliche visuelle Referenz

Das vom Projektverantwortlichen bereitgestellte Dashboard-Bild ist eine verbindliche visuelle Designreferenz für Kehler OS.

Das Design soll sich grundsätzlich an dieser Richtung orientieren.

Die wesentlichen Eigenschaften sind:

* sehr dunkle Benutzeroberfläche
* hochwertige technische Optik
* Cyan als primäre Akzentfarbe
* dezente grüne Statusanzeigen
* Orange für Warnungen
* Rot für kritische Zustände
* dunkle transparente beziehungsweise halbtransparente Panels
* feine Rahmen
* abgerundete Ecken
* dezente Leuchteffekte
* hochwertige Icons
* klare Typografie
* großzügige Abstände
* hohe Informationsdichte ohne visuelle Überladung

Das System soll technisch und hochwertig wirken.

Es soll nicht wie eine gewöhnliche Smart-Home-App aussehen.

⸻

## 3. Designreferenz statt Pixelkopie

Die Referenz ist als Designrichtung und Qualitätsstandard zu verstehen.

Sie ist keine pixelgenaue Vorgabe.

Claude darf und soll die Benutzeroberfläche weiterentwickeln, wenn dadurch:

* bessere Usability
* bessere Informationshierarchie
* bessere Touch-Bedienung
* bessere Animationen
* bessere Responsivität
* bessere technische Umsetzung

erreicht werden.

Das grundlegende Erscheinungsbild darf dabei nicht verloren gehen.

⸻

## 4. Hauptaufteilung des Dashboards

Das Dashboard soll grundsätzlich die folgende Struktur besitzen.

### Kopfbereich

Der obere Bereich enthält:

* aktuelle Uhrzeit
* aktuelles Datum
* KEHLER OS Branding
* Netzwerkstatus
* Benutzerinformationen

⸻

### Linke Navigation

Die primäre Navigation befindet sich auf der linken Seite.

Sie enthält mindestens:

* Dashboard
* Licht
* Energie
* Wasser
* Klima
* Nivellierung
* Fahrzeug
* Kameras
* Garage
* Einstellungen

Die konkrete Darstellung darf von Claude innerhalb des Designsystems optimiert werden.

Die Navigation muss jedoch eindeutig und schnell verständlich bleiben.

⸻

### Zentrale Fahrzeugdarstellung

Ein zentraler Bereich zeigt das Fahrzeug.

Die Fahrzeugdarstellung ist ein wichtiges visuelles Element des Systems.

Sie soll das tatsächliche Fahrzeug möglichst realistisch beziehungsweise hochwertig repräsentieren.

⸻

### Rechte Informationsspalte

Die rechte Seite enthält unter anderem:

* Warnungen
* Schnellzugriff

Diese Bereiche müssen schnell erreichbar sein.

⸻

### Unterer Informationsbereich

Unterhalb der zentralen Fahrzeugdarstellung werden wichtige Systembereiche zusammengefasst.

Die Referenz enthält:

* Energie
* Wasser
* Klima
* Nivellierung
* Verbrauch

Diese Struktur dient als Ausgangspunkt.

Claude darf die konkrete Darstellung verbessern.

⸻

## 5. Fahrzeugdarstellung

Das Fahrzeug soll auf dem Dashboard sichtbar sein.

Es handelt sich nicht lediglich um ein statisches Hintergrundbild.

Das Fahrzeug soll auf Systemzustände reagieren können.

Beispiele:

### Türen

Tür geschlossen:

normale Darstellung

Tür geöffnet:

entsprechende Tür wird visuell geöffnet dargestellt

⸻

### Garage

Garage geschlossen:

normale Darstellung

Garage geöffnet:

Garagentor wird animiert geöffnet dargestellt

⸻

### Stufen

Stufen eingefahren:

Stufen eingefahren

Stufen ausgefahren:

Stufen ausgefahren

⸻

### Markise

Markise eingefahren:

Markise eingefahren

Markise ausgefahren:

Markise ausgefahren

⸻

### Nivellierung

Bei einer aktiven Nivellierung soll die Fahrzeugdarstellung den aktuellen Zustand beziehungsweise die Bewegung visualisieren können.

⸻

## 6. Fahrzeugdarstellung ist keine Hauptsteuerung

Das Fahrzeug selbst ist nicht als großes interaktives Bedienfeld gedacht.

Der Benutzer soll nicht beispielsweise auf die Fahrzeugtür tippen müssen, um sie zu öffnen.

Die Steuerung erfolgt über dafür vorgesehene UI-Elemente.

Das Fahrzeug dient primär als:

* visuelle Darstellung
* Statusanzeige
* Animation
* Orientierung

Dadurch bleibt das Dashboard übersichtlich.

⸻

## 7. Dashboard-Status

Das Dashboard muss einen schnellen Gesamtüberblick ermöglichen.

Ein Beispiel für einen normalen Zustand:

```
System Status
Alles in Ordnung
```

Ein Beispiel bei Problemen:

```
System Status
2 Warnungen
```

Bei kritischen Problemen muss der Zustand entsprechend deutlich dargestellt werden.

⸻

## 8. Warnungssystem

Warnungen besitzen eine hohe Priorität.

Das Dashboard muss relevante Warnungen sichtbar darstellen.

Beispiele:

* Grauwassertank zu voll
* Batterie niedrig
* Tür offen
* Wartung fällig
* Kommunikationsfehler
* Kamera offline
* SPS nicht erreichbar
* ungewöhnliche Temperatur

⸻

## 9. Priorisierung von Warnungen

Nicht jede Warnung besitzt dieselbe Wichtigkeit.

Kehler OS muss deshalb Prioritäten unterscheiden.

Mindestens:

```
INFORMATION
HINWEIS
WARNUNG
KRITISCH
```

Kritische Zustände müssen stärker hervorgehoben werden als normale Hinweise.

⸻

## 10. Dynamisches Dashboard

Das Dashboard ist nicht vollständig statisch.

Kehler OS soll erkennen können, welche Informationen momentan relevant sind.

Beispiel:

Normalzustand:

```
Energie
Wasser
Klima
Nivellierung
Verbrauch
```

Bei niedrigem Batteriestand kann der Energiebereich stärker hervorgehoben werden.

Bei geöffnetem Garagentor kann der Fahrzeugstatus entsprechend priorisiert werden.

Bei einer kritischen Warnung muss der Warnungsbereich deutlich stärker in den Vordergrund treten.

⸻

## 11. Keine Informationsüberflutung

Dynamisch bedeutet nicht, dass ständig Elemente auf dem Bildschirm herumspringen.

Das Layout soll grundsätzlich stabil bleiben.

Änderungen sollen gezielt und nachvollziehbar erfolgen.

Animationen und Hervorhebungen müssen einen funktionalen Zweck besitzen.

⸻

## 12. Schnellzugriff

Das Dashboard enthält einen Schnellzugriffsbereich.

Dieser ermöglicht die direkte Bedienung häufig verwendeter Funktionen.

Beispiele aus der Referenz:

* Außenbeleuchtung
* Markise
* Stufen
* Garage
* Wasserpumpe
* Innenbeleuchtung

Die tatsächlich verfügbaren Schnellzugriffe sollen konfigurierbar sein.

⸻

## 13. Schnellzugriffe sind keine vollständigen Funktionsseiten

Ein Schnellzugriff soll eine häufig benötigte Aktion schnell ermöglichen.

Komplexe Funktionen gehören auf die entsprechenden Fachseiten.

Beispiel:

Ein Schnellzugriff kann die Wasserpumpe ein- oder ausschalten.

Die vollständige Wasserverwaltung gehört jedoch auf die Wasser-Seite.

⸻

## 14. Energieübersicht

Das Dashboard soll einen kompakten Überblick über die Energieversorgung geben.

Mögliche Informationen:

* Batterieladezustand
* Batteriespannung
* Strom
* Leistung
* Solarleistung
* Landstromstatus

Die Darstellung soll die wichtigsten Informationen schnell erfassbar machen.

Detailinformationen gehören auf die Energie-Seite.

⸻

## 15. Wasserübersicht

Das Dashboard soll die wichtigsten Wasserinformationen anzeigen.

Das Fahrzeug besitzt mehrere Tanks.

Mindestens relevant sind:

* Frischwasser
* Grauwasser
* Schwarzwasser

Die Anzeige soll sowohl:

* Prozentwerte
* als auch sinnvoll interpretierbare Mengen

darstellen können.

⸻

## 16. Klimaübersicht

Das Dashboard soll den aktuellen Klimazustand anzeigen.

Beispiele:

* Innentemperatur
* Außentemperatur
* gewünschte Temperatur
* Heizung
* Lüftung

Die Detailsteuerung erfolgt auf der Klima-Seite.

⸻

## 17. Nivellierungsübersicht

Das Dashboard soll den aktuellen Zustand der Nivellierung darstellen.

Dazu können gehören:

* Längsneigung
* Querneigung
* Zustand der Stützen
* Automatikstatus

Die Nivellierungsfunktion soll als wichtiger Fahrzeugzustand erkennbar sein.

⸻

## 18. Verbrauch

Kehler OS soll Energieverbrauch und Energieerzeugung visualisieren können.

Beispiele:

* Verbrauch heute
* Erzeugung heute
* Autarkiegrad

Weitere historische Daten gehören auf die Energie-Seite.

⸻

## 19. Systemstatus

Der Systemstatus muss zentral verfügbar sein.

Er kann beispielsweise Informationen über folgende Systeme zusammenfassen:

* SPS
* Raspberry Pi
* Victron
* Netzwerk
* Kameras
* Sensoren
* Speicher
* Softwaredienste

Der Benutzer soll schnell erkennen können, ob das Gesamtsystem normal funktioniert.

⸻

## 20. Navigation

Die Navigation muss sich konsistent durch das gesamte Betriebssystem ziehen.

Ein Benutzer darf nicht auf jeder Seite eine komplett andere Navigationslogik vorfinden.

⸻

## 21. Hauptbereiche

Die folgenden Bereiche sind Bestandteil der grundlegenden Informationsarchitektur:

```
Dashboard
Licht
Energie
Wasser
Klima
Nivellierung
Fahrzeug
Kameras
Garage
Einstellungen
```

Weitere Module können später ergänzt werden.

⸻

## 22. Unterseiten

Claude erhält bewusst gestalterische Freiheit bei der Entwicklung der Unterseiten.

Die Unterseiten müssen jedoch:

* zum bestehenden Designsystem passen
* dieselbe visuelle Sprache verwenden
* logisch aufgebaut sein
* touchoptimiert sein
* konsistente Komponenten verwenden
* eine klare Informationshierarchie besitzen

Es wird nicht vorgegeben, dass jede Unterseite exakt dasselbe Layout besitzen muss.

Unterschiedliche Funktionen dürfen unterschiedliche Layouts erhalten, wenn dies die Usability verbessert.

⸻

## 23. Benutzerführung

Der Benutzer soll möglichst wenig darüber nachdenken müssen, wie eine Funktion funktioniert.

Die Oberfläche soll die Funktion erklären.

Beispiel:

Nicht nur:

```
Batterie 12 %
```

sondern gegebenenfalls:

```
Batterie 12 %
Niedriger Ladezustand
Landstrom anschließen empfohlen.
```

⸻

## 24. Interaktionsfeedback

Jede Aktion benötigt unmittelbar Feedback.

Beispiel:

Benutzer aktiviert eine Lampe.

Die UI zeigt:

```
Befehl wird ausgeführt
```

Danach:

```
Lampe EIN
```

wenn die Hardware den Zustand bestätigt.

⸻

## 25. Hardwarezustand hat Vorrang

Der tatsächliche Zustand der Hardware ist immer wichtiger als der Wunschzustand des Benutzers.

Wenn ein Benutzer einen Aktor einschalten möchte, aber die Hardware dies nicht bestätigt, darf die UI nicht dauerhaft „EIN“ anzeigen.

Stattdessen muss beispielsweise:

```
Fehler
Nicht verfügbar
Keine Rückmeldung
```

angezeigt werden.

⸻

## 26. Offlinezustände

Wenn ein Gerät nicht erreichbar ist, muss die Benutzeroberfläche dies eindeutig darstellen.

Beispiel:

```
SPS
OFFLINE
```

Nicht:

```
SPS
0
```

oder ein scheinbar normaler Zustand.

⸻

## 27. Ladezustände

Wenn Daten noch nicht verfügbar sind, muss ein sinnvoller Ladezustand angezeigt werden.

Keine falschen Werte.

Keine zufälligen Platzhalter.

⸻

## 28. Animation und Systemzustand

Animationen dürfen echte Systemzustände visualisieren.

Beispiel:

Garagentor:

```
CLOSED
↓
OPENING
↓
OPEN
```

Die Animation soll dem tatsächlichen Zustand entsprechen.

Sie darf nicht nur eine dekorative Animation sein.

⸻

## 29. Bottom Navigation

Die Referenz enthält zusätzlich eine Navigation am unteren Bildschirmrand.

Diese Navigation wird noch nicht endgültig spezifiziert.

Die Entscheidung darüber wird bewusst auf einen späteren Zeitpunkt verschoben.

Claude soll sie deshalb zunächst als möglichen Bestandteil der Gesamtarchitektur berücksichtigen, aber keine endgültige Informationsarchitektur daraus ableiten.

⸻

## 30. Responsive Verhalten

Das Dashboard muss auf dem vorgesehenen Hauptdisplay optimal funktionieren.

Gleichzeitig soll die Architektur spätere weitere Bildschirmgrößen ermöglichen.

Bei kleineren Displays darf die Informationsstruktur verändert werden.

Es darf nicht einfach alles proportional verkleinert werden.

⸻

## 31. Touch-Optimierung

Das Dashboard wird primär per Touch bedient.

Alle interaktiven Elemente müssen:

* ausreichend groß
* eindeutig
* schnell erreichbar
* fehlertolerant

sein.

⸻

## 32. Nachtbetrieb

Das Dashboard muss nachts angenehm nutzbar sein.

Die bestehende dunkle Designrichtung ist dafür besonders wichtig.

Die Helligkeit und visuelle Intensität müssen reduziert werden können.

Kritische Warnungen müssen trotzdem sichtbar bleiben.

⸻

## 33. Performance

Das Dashboard muss sich jederzeit flüssig anfühlen.

Insbesondere:

* Fahrzeuganimation
* Diagramme
* Statusänderungen
* Navigation
* Übergänge

dürfen die Benutzeroberfläche nicht blockieren.

⸻

## 34. Kein dekorativer Overkill

Das System soll hochwertig aussehen.

Es darf aber nicht versuchen, durch möglichst viele:

* Glows
* Animationen
* Partikel
* Effekte
* 3D-Elemente

„futuristisch“ zu wirken.

Jeder Effekt muss einen Zweck besitzen.

⸻

## 35. Claude erhält Designfreiheit

Claude soll innerhalb der in diesem Projekt definierten Grenzen eigene Designentscheidungen treffen.

Insbesondere darf Claude:

* Layouts optimieren
* Komponenten gestalten
* Animationen entwickeln
* Unterseiten strukturieren
* Informationshierarchien verbessern
* responsive Lösungen entwickeln
* sinnvolle UI-Patterns auswählen

Solange das Ergebnis mit der definierten Kehler-OS-Designsprache übereinstimmt.

⸻

## 36. Qualitätsmaßstab

Das Ergebnis soll sich wie ein professionelles Produkt anfühlen.

Nicht wie:

* ein Hobbyprojekt
* eine einfache Web-App
* eine SPS-Visualisierung
* ein Raspberry-Pi-Dashboard
* eine Standard-Admin-Oberfläche

⸻

## 37. Designziel

Das ideale Ergebnis soll den Eindruck vermitteln:

Ein eigenes digitales Betriebssystem für ein hochwertiges Expeditionsfahrzeug.

Das System soll technisch komplex sein, sich für den Benutzer aber einfach anfühlen.

⸻

## 38. Zielbild

Der Benutzer startet Kehler OS.

Innerhalb weniger Sekunden sieht er:

* das Fahrzeug
* den aktuellen Systemzustand
* Energie
* Wasser
* Klima
* Warnungen
* wichtige Schnellzugriffe

Er kann anschließend ohne Umwege in die gewünschte Funktion wechseln.

Die Oberfläche fühlt sich dabei wie ein zusammenhängendes Betriebssystem an und nicht wie eine Sammlung einzelner Apps.

⸻

## Ende Kapitel 8

Dieses Kapitel definiert Dashboard, Navigation und zentrale UX-Prinzipien von Kehler OS.

Die konkrete Gestaltung einzelner Unterseiten bleibt bewusst offen.

Claude soll innerhalb des definierten Designsystems selbst hochwertige und funktionale Lösungen entwickeln.

Die bereitgestellte Designreferenz ist als verbindlicher visueller Maßstab zu verwenden.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf das nächste Kapitel.

Verwende Kapitel 1 bis 8 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
