# Kehler OS

# Kapitel 3 – Hardwareplattform und Systemkomponenten

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Architektur.

Treffe keine Implementierungsentscheidungen.

Analysiere ausschließlich dieses Dokument und speichere sämtliche Informationen als verbindliche Grundlage.

Warte nach diesem Kapitel auf das nächste Dokument.

⸻

## Ziel der Hardwareplattform

Die Hardware bildet das Fundament von Kehler OS.

Alle Komponenten müssen langfristig zuverlässig, wartbar und modular sein.

Es dürfen ausschließlich Komponenten verwendet werden, die professionell integriert werden können und über definierte Schnittstellen verfügen.

Das Gesamtsystem muss rund um die Uhr betrieben werden können.

⸻

## Zentrale Systemeinheit

Die Hauptrecheneinheit des Systems ist ein Raspberry Pi 5.

Der Raspberry Pi übernimmt sämtliche Aufgaben, die keine harte Echtzeit benötigen.

Dazu gehören unter anderem:

* Benutzeroberfläche
* Backend
* Datenbank
* API
* Netzwerkdienste
* Webserver
* Visualisierung
* Automatisierungen
* Protokollierung
* KI-Funktionen
* Updateverwaltung
* Konfigurationsverwaltung
* Benutzerverwaltung

Der Raspberry Pi ist das Gehirn des Systems.

Er verarbeitet Informationen.

Er trifft Entscheidungen.

Er stellt Daten bereit.

Er steuert jedoch keine sicherheitskritischen Echtzeitfunktionen direkt.

⸻

## Echtzeitsteuerung

Alle Echtzeitfunktionen werden von einer Siemens S7-1500 SPS übernommen.

Die SPS ist ausschließlich für deterministische Steuerungsaufgaben verantwortlich.

Beispiele:

* Digitale Eingänge
* Digitale Ausgänge
* Analoge Messwerte
* Beleuchtung
* Relais
* Pumpen
* Ventile
* Garagentor
* Türkontakte
* Sensoren
* Aktoren
* Sicherheitsfunktionen

Die SPS arbeitet unabhängig vom Raspberry Pi.

Fällt der Raspberry Pi aus, muss die SPS weiterhin sicher arbeiten.

⸻

## Energieverwaltung

Die komplette Energieverwaltung erfolgt über das Victron-System.

Kehler OS greift ausschließlich auf die bereitgestellten Daten zu.

Beispiele:

* Batteriespannung
* Batteriestrom
* Ladezustand
* Solarleistung
* Wechselrichterstatus
* Landstromstatus
* Ladegeräte
* Alarme
* Historische Werte

Victron bleibt für die Energie zuständig.

Kehler OS visualisiert, analysiert und automatisiert diese Informationen.

⸻

## Netzwerk

Alle Komponenten werden über ein internes Gigabit-Netzwerk verbunden.

Das Netzwerk bildet das Rückgrat des Fahrzeugs.

Folgende Geräte kommunizieren über dieses Netzwerk:

* Raspberry Pi
* Siemens SPS
* Victron
* Touchdisplay
* WLAN-Access-Point
* Kameras
* zukünftige Erweiterungen

Die Kommunikation erfolgt ausschließlich innerhalb dieses Netzwerks.

Internet ist optional.

⸻

## Touchdisplay

Das Hauptdisplay dient als zentrale Benutzeroberfläche.

Es zeigt ausschließlich Kehler OS.

Andere Anwendungen sollen für den Benutzer nicht sichtbar sein.

Das Display arbeitet dauerhaft im Vollbildmodus.

Nach dem Einschalten erscheint unmittelbar Kehler OS.

⸻

## Sensoren

Das Fahrzeug verfügt über zahlreiche Sensoren.

Beispiele:

* Tankfüllstände
* Temperatur
* Luftfeuchtigkeit
* Spannungen
* Ströme
* Türkontakte
* Fensterkontakte
* Bewegungsmelder
* Helligkeit
* Neigung
* Garagenstatus
* Internetstatus
* Batteriesensoren

Alle Sensoren liefern Rohdaten.

Die Interpretation dieser Daten erfolgt später durch Kehler OS.

⸻

## Aktoren

Kehler OS steuert verschiedene Aktoren.

Beispiele:

* Beleuchtung
* Relais
* Pumpen
* Lüfter
* Magnetventile
* Türverriegelungen
* Garagentor
* Signalgeber

Alle Aktoren werden über klar definierte Schnittstellen angesteuert.

⸻

## Kameras

Das System wird so vorbereitet, dass später mehrere Kameras integriert werden können.

Beispiele:

* Rückfahrkamera
* Seitenkameras
* Garagenkamera
* Eingangsbereich
* Technikraum

Die Kameras gehören logisch zum Betriebssystem und sollen sich nahtlos in die Benutzeroberfläche einfügen.

⸻

## Erweiterbarkeit

Bereits heute muss berücksichtigt werden, dass später zusätzliche Hardware integriert werden kann.

Beispiele:

* Wetterstation
* Luftqualitätssensoren
* Reifendrucksensoren
* weitere Displays
* zusätzliche SPS-Module
* neue Tanksensoren
* Smart-Geräte
* externe Steuerungen

Die Hardwarearchitektur darf solche Erweiterungen nicht erschweren.

⸻

## Ausfallsicherheit

Ein Defekt einzelner Komponenten darf nicht zum Ausfall des Gesamtsystems führen.

Beispiele:

* Fällt eine Kamera aus, bleibt das Fahrzeug vollständig bedienbar.
* Fällt das Internet aus, arbeitet Kehler OS ohne Einschränkungen weiter.
* Fällt der Raspberry Pi aus, übernimmt die SPS weiterhin alle sicherheitsrelevanten Steuerungsaufgaben.
* Fällt ein Sensor aus, muss das System dies erkennen und den Benutzer informieren.

Fehler werden erkannt, protokolliert und isoliert behandelt.

⸻

## Qualitätsanspruch

Die Hardware soll nicht wie eine Sammlung einzelner Geräte wirken.

Für den Benutzer entsteht der Eindruck eines einzigen, perfekt abgestimmten Gesamtsystems.

Alle Hardwarekomponenten arbeiten wie Teile eines gemeinsamen Betriebssystems.

⸻

## Ende Kapitel 3

Dieses Kapitel definiert ausschließlich die Hardwareplattform und die Aufgaben der einzelnen Systemkomponenten.

Es werden weiterhin keine Softwarearchitektur, keine Implementierungsdetails und kein Programmcode erstellt.

Warte auf Kapitel 4 und verwende alle Informationen aus den bisherigen Kapiteln als verbindliche Grundlage.
