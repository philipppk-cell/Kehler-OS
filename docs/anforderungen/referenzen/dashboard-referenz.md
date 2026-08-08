# Designreferenz – Dashboard (zu Kapitel 8, Abschnitt 2)

**Status: verbindliche visuelle Designreferenz** (Designrichtung und
Qualitätsmaßstab, ausdrücklich **keine** pixelgenaue Vorgabe – siehe Kapitel 8,
Abschnitt 3).

## Bilddatei

> **Die Originalbilddatei fehlt in diesem Verzeichnis.**
> Das Bild wurde im Chat übermittelt und konnte von dort nicht als Datei
> gespeichert werden. Es sollte als `dashboard-referenz.png` in diesem
> Verzeichnis abgelegt werden, damit die Referenz dauerhaft im Repository
> vorliegt.
>
> Bis dahin dient die folgende Beschreibung als Ersatz. Sie ist eine
> Beobachtung des Bildinhalts und **nicht** Teil des Anforderungstextes von
> Kapitel 8.

## Beschreibung des referenzierten Dashboards

Querformat, sehr dunkler Hintergrund (nahezu schwarz mit leichtem Blaustich),
Cyan als durchgehende Akzentfarbe, halbtransparente Panels mit feinen hellen
Rahmen und abgerundeten Ecken.

### Kopfzeile

* Links: Uhrzeit `20:15`, darunter `Sonntag, 25. Mai 2025`
* Mitte: Wortmarke `KEHLER OS` (gesperrte Versalien, „OS“ in Cyan abgesetzt)
* Rechts: WLAN-Symbol mit Label `WLAN`, Signalbalken mit Label `5G`,
  Benutzeravatar mit `Philipp` / `Administrator`

### Linke Navigationsspalte

Vertikale Liste mit Icon und Label, aktiver Eintrag `Dashboard` cyan
hervorgehoben mit umrandeter Fläche:

`Dashboard` · `Licht` · `Energie` · `Wasser` · `Klima` · `Nivellierung` ·
`Fahrzeug` · `Kameras` · `Garage` · `Einstellungen`

Am unteren Ende der Spalte ein abgesetztes Statusfeld mit grünem Punkt:
`System Status` / `Alles in Ordnung`

### Zentraler Hero-Bereich

* Oben links über dem Bild: Mond-Icon, `22°C`, `Klare Nacht`,
  `Außentemperatur`
* Großes, fotorealistisches nächtliches Bild des LKW-Wohnmobils (MAN-Fahrgestell,
  heller Aufbau) in Dreiviertelansicht von vorne rechts
* Darüber gelegt links unten eine Karte `Fahrzeugstatus` mit Icon-Zeilen und
  grünen Statuswerten:
  * `Türen` – `Geschlossen`
  * `Fenster` – `Geschlossen`
  * `Stufen` – `Eingefahren`
  * `Garage` – `Geschlossen`
  * `Markise` – `Eingefahren`
* Am unteren Rand des Hero-Bereichs fünf Seitenpunkte, der erste aktiv (cyan) –
  der Bereich ist offenbar als mehrseitiger Slider gedacht

### Rechte Informationsspalte

**Panel `Warnungen`** mit Warndreieck und Zähler-Badge `2`:

* `Grauwassertank` / `Füllstand hoch` – Wert `85 %`, orange hervorgehoben
  (aktive Zeile mit orangefarbenem Hintergrund und linker Akzentkante)
* `Wartung fällig` / `Nächster Service in 12 Tagen`

**Panel `Schnellzugriff`** als 3×2-Raster aus quadratischen Icon-Kacheln:

`Licht Außen` · `Markise` · `Stufen` · `Garage` · `Wasserpumpe` ·
`Innenbeleuchtung`

### Untere Kartenreihe (fünf Karten)

1. **`Energie`** – großer Wert `87 %` mit Batteriesymbol, Label `Batterie`,
   cyanfarbener Fortschrittsbalken; darunter `24.8 V`, `-3.2 A`, `79 Ah`;
   Zeile `Solar` mit `1240 W` und kleinem Verlaufsdiagramm; unten
   `Landstrom` – `Verbunden` (grün)
2. **`Wasser`** – drei Tankzeilen mit Icon, Menge, Prozentwert und Balken:
   `Frischwasser` `320 L` (cyan), `Grauwasser` `170 L` (orange),
   `Schwarzwasser` `80 L` (orange)
3. **`Klima`** – `Innen` `22.4 °C` (cyan), `Außen` `22 °C`; darunter
   Sollwertsteuerung `22.0 °C` mit runden `−`/`+`-Schaltflächen; unten zwei
   Schaltflächen `Heizung` und `Lüfter`
4. **`Nivellierung`** – schematische Fahrzeuggrafik mit grün markierten
   Stützen; `Längsneigung` `0.3 °`, `Querneigung` `0.2 °`; darunter ein
   cyan umrandeter Button `Automatik starten`
5. **`Verbrauch heute`** – Liniendiagramm (cyan) mit Tagesverlauf; Legende mit
   farbigen Punkten: `Verbrauch` `18.7 kWh`, `Erzeugung` `28.4 kWh`,
   `Autarkie` `73 %`

### Untere Navigationsleiste

Durchgehende dunkle Leiste über die volle Breite mit Icons: Zurück-Pfeil
(links), dann mittig Haus (aktiv, cyan), Liste, Raster, Glocke, und rechts
außen ein Regler-/Einstellungssymbol.

Diese Leiste ist laut Kapitel 8, Abschnitt 29 **noch nicht spezifiziert** – sie
darf nicht als endgültige Informationsarchitektur interpretiert werden.

## Beobachtete Unstimmigkeiten in der Referenz

Diese Punkte sind Eigenheiten des Referenzbildes, keine Anforderungen:

* In der Wasser-Karte steht bei `Frischwasser` zweimal `64 %`; bei
  `Grauwasser` stehen nebeneinander `65 %` und `85 %`. Die Warnung in der
  rechten Spalte nennt `85 %`. Der Wert `65 %` dürfte ein Artefakt der Montage
  sein.
* Die Wetteranzeige nennt `22 °C` Außentemperatur, die Klima-Karte ebenfalls
  `22 °C` – konsistent, aber die Innentemperatur `22.4 °C` ist nachts bei
  identischer Außentemperatur eher illustrativ zu verstehen.
