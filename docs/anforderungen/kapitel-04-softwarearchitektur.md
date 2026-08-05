# Kehler OS

# Kapitel 4 – Softwarearchitektur

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Du darfst keinen Code schreiben.

Du darfst keine Dateien erzeugen.

Du darfst keine Architektur verändern.

Analysiere ausschließlich dieses Dokument und verwende es als verbindliche Grundlage für alle folgenden Kapitel.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## Ziel

Kehler OS ist kein einzelnes Programm.

Kehler OS besteht aus vielen eigenständigen Softwarekomponenten, die gemeinsam ein Betriebssystem bilden.

Jede Komponente besitzt eine klar definierte Aufgabe.

Keine Komponente darf mehrere Verantwortlichkeiten gleichzeitig übernehmen.

Alle Komponenten kommunizieren ausschließlich über definierte Schnittstellen.

⸻

## Architekturprinzip

Die gesamte Software basiert auf einer modularen Architektur.

Jedes Modul kann unabhängig entwickelt, getestet, erweitert oder ersetzt werden.

Neue Funktionen dürfen niemals bestehende Module verändern müssen.

Dadurch bleibt Kehler OS langfristig wartbar.

⸻

## Zentrale Dienste

Bestimmte Funktionen werden nicht von einzelnen Modulen übernommen.

Sie gehören zum Kern des Betriebssystems.

Diese Systemdienste laufen dauerhaft im Hintergrund.

Beispiele:

* Konfigurationsdienst
* Kommunikationsdienst
* Ereignisdienst
* Benutzerverwaltung
* Rechteverwaltung
* Benachrichtigungssystem
* Protokollierung
* Fehlerüberwachung
* Updateverwaltung
* Diagnosesystem
* Zeitverwaltung
* Speicherverwaltung

Alle Module greifen auf diese Dienste zurück.

Es dürfen keine doppelten Implementierungen entstehen.

⸻

## Fachmodule

Die eigentlichen Fahrzeugfunktionen werden als eigenständige Module umgesetzt.

Jedes Modul besitzt eine klar definierte Verantwortung.

Geplante Module:

* Dashboard
* Energie
* Solar
* Batterie
* Licht
* Klima
* Wasser
* Tanks
* Garage
* Türen
* Fenster
* Navigation
* Kameras
* Sicherheit
* Wartung
* Diagnose
* Automatisierungen
* KI-Assistent
* Einstellungen

Kein Modul darf intern Aufgaben eines anderen Moduls übernehmen.

⸻

## Frontend

Das Frontend dient ausschließlich der Darstellung.

Es zeigt Informationen an.

Es verarbeitet Benutzereingaben.

Es besitzt keine Geschäftslogik.

Alle Entscheidungen werden vom Backend getroffen.

Dadurch kann später dieselbe Logik auf mehreren Geräten verwendet werden.

Beispiele:

* Touchdisplay
* Tablet
* Smartphone
* Notebook
* zukünftige Displays

Alle Oberflächen greifen auf dieselben Daten zu.

⸻

## Backend

Das Backend bildet das Herz der Software.

Es verarbeitet sämtliche Informationen.

Es verwaltet den Systemzustand.

Es steuert die Kommunikation zwischen den Modulen.

Es entscheidet über Automatisierungen.

Es verarbeitet Ereignisse.

Es verwaltet Benutzer.

Es stellt APIs bereit.

Es kommuniziert mit der SPS.

Es kommuniziert mit Victron.

Es speichert Daten.

Es führt Diagnosen durch.

Es erzeugt Benachrichtigungen.

Es organisiert sämtliche Abläufe.

⸻

## Datenhaltung

Alle dauerhaft benötigten Informationen werden zentral gespeichert.

Beispiele:

* Einstellungen
* Benutzer
* Rollen
* Tankhistorie
* Batterieverlauf
* Temperaturen
* Fehlerspeicher
* Automatisierungen
* Wartungsdaten
* Ereignisprotokolle

Kein Modul speichert dauerhaft eigene Daten außerhalb der zentralen Datenhaltung.

⸻

## Kommunikationsmodell

Die Kommunikation zwischen Modulen erfolgt niemals direkt.

Module senden Ereignisse.

Andere Module reagieren auf diese Ereignisse.

Dadurch entstehen möglichst wenige direkte Abhängigkeiten.

Das System bleibt flexibel.

⸻

## Ereignisse

Typische Ereignisse:

Tank voll.

Tank leer.

Tür geöffnet.

Tür geschlossen.

Landstrom angeschlossen.

Landstrom entfernt.

Batterie niedrig.

Solarleistung verändert.

Temperatur gestiegen.

Garagentor geöffnet.

Internet verloren.

Kamera offline.

Update verfügbar.

Benutzer angemeldet.

Benutzer abgemeldet.

Alle Ereignisse besitzen eine eindeutige Struktur.

Sie werden zentral verarbeitet.

⸻

## Fehlerbehandlung

Fehler gehören zum normalen Betrieb.

Deshalb müssen sie strukturiert behandelt werden.

Jeder Fehler erhält:

* Zeitpunkt
* Quelle
* Schweregrad
* Beschreibung
* betroffene Komponenten
* mögliche Ursache
* mögliche Lösung

Fehler dürfen niemals unbemerkt bleiben.

⸻

## Protokollierung

Alle wichtigen Vorgänge werden protokolliert.

Beispiele:

Benutzeraktionen.

Systemstarts.

Sensorfehler.

Kommunikationsfehler.

Automatisierungen.

Warnungen.

Updates.

Neustarts.

Dadurch kann jedes Problem später nachvollzogen werden.

⸻

## Hintergrundprozesse

Mehrere Prozesse laufen dauerhaft.

Beispiele:

Sensorüberwachung.

Netzwerküberwachung.

Systemdiagnose.

Automatisierungen.

Updateprüfung.

Datensicherung.

Leistungsüberwachung.

Synchronisation.

Diese Prozesse arbeiten unabhängig voneinander.

⸻

## Performance

Kehler OS muss dauerhaft flüssig arbeiten.

Die Benutzeroberfläche darf niemals einfrieren.

Lange Berechnungen dürfen die Bedienung nicht beeinträchtigen.

Alle aufwendigen Aufgaben werden im Hintergrund verarbeitet.

⸻

## Skalierbarkeit

Neue Module müssen jederzeit ergänzt werden können.

Neue Hardware.

Neue Sensoren.

Neue Benutzeroberflächen.

Neue Dienste.

Neue Automatisierungen.

Die Softwarearchitektur darf dadurch nicht verändert werden müssen.

⸻

## Entwicklungsphilosophie

Die Software wird so entwickelt, als würde sie später in mehreren hundert Fahrzeugen eingesetzt.

Auch wenn zunächst nur ein Fahrzeug existiert, gelten dieselben Qualitätsmaßstäbe wie bei professionellen Fahrzeugherstellern.

⸻

## Ende Kapitel 4

Dieses Kapitel definiert ausschließlich die interne Softwarearchitektur von Kehler OS.

Es wird weiterhin keine Software entwickelt.

Es werden keine Dateien erzeugt.

Es wird kein Programmcode geschrieben.

Warte auf Kapitel 5 und verwende alle bisherigen Kapitel als verbindliche Grundlage für sämtliche zukünftigen Entscheidungen.
