# Kehler OS

# Kapitel 2 – Gesamtarchitektur des Systems

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Erstelle keinen Code.

Erstelle keine Ordnerstruktur.

Treffe keine Implementierungsentscheidungen.

Analysiere ausschließlich die folgenden Anforderungen und verwende sie als Grundlage für alle folgenden Kapitel.

⸻

## Grundidee

Kehler OS besteht aus mehreren Ebenen.

Keine Ebene darf direkt von einer anderen abhängig sein.

Jede Ebene besitzt eine klar definierte Aufgabe.

Dadurch bleibt das System übersichtlich, wartbar und beliebig erweiterbar.

Alle zukünftigen Komponenten müssen sich in diese Architektur einfügen.

⸻

## Oberstes Ziel

Das gesamte Fahrzeug wird von einer einzigen Softwareplattform verwaltet.

Der Benutzer sieht niemals einzelne Hersteller oder Systeme.

Ob ein Sensor von Hersteller A stammt oder ein Wechselrichter von Hersteller B, spielt für die Bedienung keine Rolle.

Nach außen existiert ausschließlich Kehler OS.

⸻

## Systemebenen

Das System wird logisch in mehrere Schichten unterteilt.

### Ebene 1 – Hardware

Diese Ebene umfasst sämtliche physische Komponenten.

Beispiele:

* Raspberry Pi 5
* Siemens S7-1500 SPS
* Victron-System
* Touchdisplay
* Sensoren
* Relais
* Digitale Ein- und Ausgänge
* Analoge Sensoren
* Kameras
* GPS-Empfänger
* WLAN-Access-Point
* Netzwerk-Switch
* Temperaturfühler
* Tanksensoren
* Türkontakte
* Garagentor-Antrieb
* Beleuchtung
* Klimaanlage
* Heizung
* Weitere zukünftige Geräte

Die Hardware darf niemals direkt von der Benutzeroberfläche angesprochen werden.

⸻

### Ebene 2 – Hardware-Abstraktionsschicht

Zwischen Hardware und Software befindet sich eine Abstraktionsschicht.

Diese Schicht kennt die Besonderheiten der jeweiligen Geräte.

Alle höheren Ebenen kommunizieren ausschließlich mit dieser Schicht.

Dadurch kann später Hardware ersetzt werden, ohne die restliche Software anzupassen.

⸻

### Ebene 3 – Systemdienste

Diese Ebene enthält alle zentralen Dienste des Betriebssystems.

Beispiele:

* Kommunikationsdienst
* Benutzerverwaltung
* Rechteverwaltung
* Ereignisverwaltung
* Logging
* Benachrichtigungen
* Updateverwaltung
* Fehlerüberwachung
* Zeitverwaltung
* Konfigurationsverwaltung

Diese Dienste laufen dauerhaft im Hintergrund.

⸻

### Ebene 4 – Fachmodule

Alle Funktionen des Wohnmobils werden in eigenständigen Modulen umgesetzt.

Jedes Modul besitzt eine klar definierte Verantwortung.

Geplante Module:

* Dashboard
* Energie
* Solar
* Batterie
* Licht
* Wasser
* Tanks
* Klima
* Heizung
* Navigation
* Kameras
* Garage
* Türen
* Fenster
* Sicherheit
* Automatisierungen
* Wartung
* Diagnose
* KI-Assistent

Module dürfen möglichst unabhängig voneinander arbeiten.

⸻

### Ebene 5 – Benutzeroberfläche

Die Benutzeroberfläche ist ausschließlich für Darstellung und Bedienung verantwortlich.

Sie enthält keine Steuerungslogik.

Sie zeigt Informationen an und sendet Benutzeraktionen an die entsprechenden Systemdienste.

Dadurch bleibt die Oberfläche schlank und austauschbar.

⸻

## Kommunikation

Kommunikation erfolgt niemals zufällig.

Alle Datenflüsse besitzen definierte Schnittstellen.

Kein Modul greift direkt auf ein anderes Modul zu, wenn dafür ein Systemdienst vorgesehen ist.

Kommunikation muss nachvollziehbar, dokumentiert und erweiterbar sein.

⸻

## Ereignisorientiertes System

Kehler OS arbeitet ereignisgesteuert.

Beispiele:

* Tür geöffnet
* Batterie lädt
* Tank fast leer
* Landstrom angeschlossen
* Motor gestartet
* Wasserpumpe eingeschaltet
* Temperatur verändert
* Internet verloren
* Kamera ausgefallen

Diese Ereignisse werden zentral verarbeitet und an interessierte Module verteilt.

Dadurch entsteht ein loses, skalierbares Gesamtsystem.

⸻

## Erweiterbarkeit

Jedes neue Modul muss sich integrieren lassen, ohne bestehende Module verändern zu müssen.

Die Architektur ist deshalb modular aufgebaut.

Neue Hardware, Sensoren oder Funktionen dürfen möglichst nur neue Komponenten hinzufügen und keine bestehenden ersetzen.

⸻

## Fehlertoleranz

Ein Fehler in einem Modul darf niemals das gesamte System zum Absturz bringen.

Fällt beispielsweise das Kameramodul aus, müssen Beleuchtung, Tanks, Energie und Navigation weiterhin funktionieren.

Fehler werden isoliert behandelt.

⸻

## Wartbarkeit

Alle Komponenten müssen klar dokumentiert sein.

Jede Funktion besitzt eine eindeutige Aufgabe.

Komplexität wird vermieden.

Architekturentscheidungen müssen langfristig sinnvoll sein.

⸻

## Zukunftsfähigkeit

Bereits heute muss berücksichtigt werden, dass Kehler OS später erweitert werden kann.

Beispiele:

* zusätzliche Displays
* Fernzugriff
* Cloud-Anbindung
* weitere Sensoren
* neue Fahrzeuge
* Sprachsteuerung
* neue Energiequellen
* autonome Assistenzfunktionen

Die Architektur darf diese Erweiterungen nicht erschweren.

⸻

## Entwicklungsphilosophie

Das System soll so entwickelt werden, als würde es später in Serie produziert.

Auch wenn zunächst nur ein einziges Fahrzeug ausgestattet wird, gelten dieselben Qualitätsmaßstäbe wie bei professionellen Fahrzeugherstellern.

Jede Architekturentscheidung soll auf Stabilität, Wartbarkeit und Erweiterbarkeit ausgelegt sein.

⸻

## Ende Kapitel 2

Dieses Kapitel definiert ausschließlich die logische Gesamtarchitektur von Kehler OS.

Es werden weiterhin keine Implementierungsdetails oder Programmcodes erstellt.

Warte auf Kapitel 3 und verwende sämtliche Informationen aus Kapitel 1 und Kapitel 2 als verbindliche Grundlage.
