# KEHLER OS

# Kapitel 9 – Fahrzeugfunktionen und Systemmodule

> Vorbemerkung aus der Übermittlung:
> Nach Dashboard und UX gehen wir jetzt auf die eigentlichen Funktionsbereiche
> des Fahrzeugs. Damit bekommt Claude ein klares Bild davon, was Kehler OS
> später können soll, ohne dass wir ihm bereits vorschreiben, wie er jede
> einzelne Seite gestalten muss.

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Treffe keine eigenständigen technischen Entscheidungen, die den bisherigen Anforderungen widersprechen.

Dieses Kapitel beschreibt die funktionalen Bereiche von Kehler OS.

Die konkrete Gestaltung der einzelnen Seiten bleibt bewusst offen.

Claude soll die Benutzeroberflächen dieser Bereiche später selbst gestalten, sofern sie dem definierten Kehler-OS-Designsystem entsprechen.

Verwende Kapitel 1–9 gemeinsam als verbindliche Grundlage.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Grundprinzip der Fahrzeugfunktionen

Kehler OS soll sämtliche wichtigen technischen Systeme des Wohnmobils in einer einheitlichen Benutzeroberfläche zusammenführen.

Der Benutzer soll nicht wissen müssen, welches physische Gerät eine Funktion ausführt.

Beispiel:

Der Benutzer möchte das Außenlicht einschalten.

Er soll einfach:

```
Außenlicht
EIN
```

sehen und bedienen können.

Ob dahinter eine SPS, ein Relais, ein Modul oder eine andere Hardware arbeitet, ist für die Benutzeroberfläche irrelevant.

⸻

## 2. Hauptmodule

Die grundlegenden Funktionsbereiche sind:

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

Weitere Module dürfen später ergänzt werden.

⸻

## 3. Licht

Das Lichtmodul verwaltet sämtliche Beleuchtung des Fahrzeugs.

Mögliche Bereiche:

* Innenbeleuchtung
* Außenbeleuchtung
* einzelne Räume
* einzelne Lichtkreise
* technische Beleuchtung
* Garage
* weitere zukünftige Lichtquellen

⸻

## 4. Lichtsteuerung

Lichtquellen müssen mindestens folgende Zustände unterstützen können:

```
EIN
AUS
UNBEKANNT
FEHLER
```

Wenn Hardware dies unterstützt, können zusätzlich Dimmer beziehungsweise Helligkeitswerte verwendet werden.

⸻

## 5. Lichtgruppen

Mehrere Lampen können logisch gruppiert werden.

Beispiele:

```
Innen
Außen
Wohnbereich
Schlafbereich
Küche
Bad
Garage
```

Die tatsächliche Gruppierung soll konfigurierbar bleiben.

⸻

## 6. Szenen für Licht

Kehler OS soll später Licht-Szenen unterstützen können.

Beispiele:

```
Abend
Nacht
Alles AUS
Außen
Camping
```

Eine Szene kann mehrere Lichtzustände gleichzeitig verändern.

⸻

## 7. Energie

Das Energiemodul bildet die zentrale Übersicht über das elektrische System des Fahrzeugs.

Es soll relevante Informationen aus den Energiekomponenten zusammenführen.

Dazu gehören insbesondere:

* Batterie
* Solar
* Wechselrichter
* Ladegeräte
* Landstrom
* Energieverbrauch
* Energieerzeugung

⸻

## 8. Batterie

Das System soll den aktuellen Batteriezustand darstellen können.

Beispiele:

* Ladezustand
* Spannung
* Strom
* Leistung
* Kapazität
* Ladezustand
* Lade-/Entladevorgang
* Warnungen

Die konkrete Datenquelle kann beispielsweise das Victron-System sein.

⸻

## 9. Energiefluss

Kehler OS soll den Energiefluss verständlich visualisieren können.

Beispielsweise:

```
Solar
  ↓
Batterie
  ↓
Verbraucher
```

oder:

```
Landstrom
  ↓
Ladegerät
  ↓
Batterie
  ↓
Verbraucher
```

Die Darstellung soll dem Benutzer verständlich machen, woher Energie kommt und wohin sie fließt.

⸻

## 10. Solar

Das System soll Solarinformationen anzeigen können.

Beispiele:

* aktuelle Leistung
* Tageserzeugung
* historische Erzeugung
* Spannung
* Strom
* Status

⸻

## 11. Landstrom

Kehler OS soll erkennen können, ob Landstrom vorhanden beziehungsweise verbunden ist.

Mögliche Zustände:

```
VERBUNDEN
NICHT VERBUNDEN
UNBEKANNT
FEHLER
```

⸻

## 12. Energiehistorie

Historische Energieinformationen sollen dargestellt werden können.

Beispiele:

* Verbrauch pro Tag
* Verbrauch pro Woche
* Verbrauch pro Monat
* Solarerzeugung
* Autarkiegrad
* Lade-/Entladeverlauf

⸻

## 13. Wasser

Das Wassermodul verwaltet die Wassersysteme des Fahrzeugs.

Mindestens relevant sind:

* Frischwasser
* Grauwasser
* Schwarzwasser

Weitere Tanks müssen später hinzugefügt werden können.

⸻

## 14. Tankfüllstände

Jeder Tank soll mindestens einen aktuellen Füllstand besitzen können.

Mögliche Darstellung:

```
64 %
320 L
```

Die konkrete Darstellung soll sich automatisch an die konfigurierte Tankgröße anpassen.

⸻

## 15. Tankwarnungen

Das System soll definierte Schwellenwerte überwachen können.

Beispiele:

Frischwasser niedrig:

WARNUNG

Grauwasser hoch:

WARNUNG

Schwarzwasser sehr hoch:

KRITISCH

Die Schwellenwerte müssen später konfigurierbar sein.

⸻

## 16. Tankhistorie

Kehler OS soll historische Tankstände speichern können.

Dadurch können beispielsweise folgende Informationen entstehen:

* Wasserverbrauch
* durchschnittlicher Verbrauch
* Füllverlauf
* Entleerungsintervalle

⸻

## 17. Wasserpumpe

Die Wasserpumpe soll über Kehler OS überwacht und, sofern hardwareseitig vorgesehen, gesteuert werden können.

Mögliche Zustände:

```
EIN
AUS
FEHLER
UNBEKANNT
```

⸻

## 18. Klima

Das Klimamodul verwaltet die klimatischen Bedingungen im Fahrzeug.

Dazu gehören beispielsweise:

* Innentemperatur
* Außentemperatur
* Solltemperatur
* Heizung
* Lüftung
* Klimatisierung
* weitere Sensoren

⸻

## 19. Temperaturzonen

Das System soll grundsätzlich mehrere Temperaturbereiche unterstützen können.

Beispiele:

```
Wohnbereich
Schlafbereich
Bad
Fahrerhaus
Außen
```

Die tatsächliche Anzahl der Zonen muss konfigurierbar sein.

⸻

## 20. Solltemperatur

Wenn die verwendete Hardware dies unterstützt, soll eine gewünschte Raumtemperatur eingestellt werden können.

Die Benutzeroberfläche soll klar zwischen:

IST

und:

SOLL

unterscheiden.

⸻

## 21. Heizung und Lüftung

Heizung und Lüftung sollen jeweils ihren aktuellen Zustand darstellen können.

Beispielsweise:

```
AUS
EIN
AUTOMATIK
FEHLER
UNBEKANNT
```

Die konkrete Steuerbarkeit hängt von der angeschlossenen Hardware ab.

⸻

## 22. Klimaautomatisierung

Später sollen automatische Regeln möglich sein.

Beispiel:

```
Wenn Innenraum < 18 °C
→ Heizung aktivieren
```

Oder:

```
Wenn Innenraum > 25 °C
→ Lüftung aktivieren
```

Diese Logik gehört zum Automatisierungssystem und soll nicht fest in die UI eingebaut werden.

⸻

## 23. Nivellierung

Das Fahrzeug besitzt ein hydraulisches Nivellierungssystem.

Kehler OS soll dieses System überwachen und bedienen können, sofern die entsprechende Steuerung vorhanden ist.

⸻

## 24. Nivellierungssensorik

Das System soll die Fahrzeugneigung erfassen können.

Vorgesehen sind Messungen für:

* Längsneigung
* Querneigung
* weitere erforderliche Messwerte

Die Sensorwerte werden an die Steuerung übertragen und anschließend von Kehler OS visualisiert.

⸻

## 25. Nivellierungszustand

Das System soll erkennen können:

```
NIVELLIERT
NICHT NIVELLIERT
NIVELLIERUNG AKTIV
FEHLER
UNBEKANNT
```

⸻

## 26. Automatische Nivellierung

Eine automatische Nivellierung soll später möglich sein.

Das System soll dabei:

1. aktuelle Neigung messen
2. Zielzustand bestimmen
3. Steuerung ausführen
4. Messwerte kontinuierlich überwachen
5. Bewegungen kontrollieren
6. den Abschluss erkennen
7. Fehler erkennen

Die eigentliche Echtzeitsteuerung verbleibt bei der dafür vorgesehenen Steuerung.

⸻

## 27. Fahrzeugmodul

Das Fahrzeugmodul fasst allgemeine Fahrzeugfunktionen zusammen.

Dazu können gehören:

* Türen
* Fenster
* Stufen
* Markise
* Verriegelung
* Fahrzeugstatus
* weitere Aufbaufunktionen

⸻

## 28. Türen

Kehler OS soll Türzustände darstellen können.

Beispielsweise:

```
GESCHLOSSEN
OFFEN
ÖFFNET
SCHLIESST
UNBEKANNT
```

⸻

## 29. Zentralverriegelung

Das System soll die zentrale Verriegelung des Aufbaus unterstützen können.

Der Benutzer soll beispielsweise einen Gesamtzustand sehen:

ALLE VERRIEGELT

oder:

NICHT ALLE VERRIEGELT

Einzelne Türen müssen gegebenenfalls separat dargestellt werden.

⸻

## 30. Fenster

Fensterkontakte sollen überwacht werden können.

Beispielsweise:

ALLE GESCHLOSSEN

oder:

2 FENSTER OFFEN

⸻

## 31. Stufen

Die elektrische beziehungsweise motorisierte Eingangsstufe soll überwacht werden können.

Mögliche Zustände:

```
EINGEFAHREN
AUSGEFAHREN
BEWEGT SICH
FEHLER
UNBEKANNT
```

⸻

## 32. Markise

Die Markise soll überwacht und, sofern technisch vorgesehen, gesteuert werden können.

Mögliche Zustände:

```
EINGEFAHREN
AUSGEFAHREN
FÄHRT AUS
FÄHRT EIN
FEHLER
UNBEKANNT
```

⸻

## 33. Garage

Das Garagenmodul verwaltet das Garagentor und zugehörige Sensoren.

Mögliche Zustände:

```
GESCHLOSSEN
ÖFFNET
OFFEN
SCHLIESST
STOPPT
FEHLER
UNBEKANNT
```

⸻

## 34. Garagensicherheit

Die Garage soll besonders deutlich darstellen, wenn sie nicht geschlossen ist.

Beispielsweise kann der Dashboard-Status anzeigen:

GARAGE OFFEN

wenn sich das Fahrzeug in einem Zustand befindet, in dem dies relevant ist.

⸻

## 35. Kameras

Das Kameramodul verwaltet die Kameras des Fahrzeugs.

Das System soll mehrere Kameras unterstützen können.

Beispiele:

* Rückfahrkamera
* Seitenkamera
* Garagenkamera
* Eingangsbereich
* weitere Kameras

⸻

## 36. Kamerastatus

Für jede Kamera soll mindestens bekannt sein:

```
ONLINE
OFFLINE
FEHLER
UNBEKANNT
```

⸻

## 37. Kameraansicht

Kehler OS soll eine zentrale Kameraoberfläche besitzen.

Diese soll verschiedene Kameras auswählen können.

Die konkrete Gestaltung bleibt Claude überlassen.

Sie muss jedoch zum bestehenden Designsystem passen.

⸻

## 38. Automatische Kameraanzeige

Später können situationsabhängige Kameraansichten vorgesehen werden.

Beispiel:

Beim Rückwärtsfahren kann automatisch die Rückfahrkamera angezeigt werden.

Solche Funktionen müssen jedoch sicher und nachvollziehbar umgesetzt werden.

⸻

## 39. Sicherheit

Das Sicherheitsmodul fasst sicherheitsrelevante Informationen zusammen.

Beispiele:

* Türen
* Fenster
* Garage
* technische Fehler
* Bewegungsmelder
* Systemstatus
* kritische Alarme

⸻

## 40. Sicherheitsstatus

Kehler OS soll einen übergeordneten Sicherheitsstatus darstellen können.

Beispielsweise:

```
SICHER
AUFMERKSAMKEIT
WARNUNG
KRITISCH
```

⸻

## 41. Systemdiagnose

Das Diagnosesystem soll den Zustand der technischen Infrastruktur überwachen.

Beispiele:

* Raspberry Pi
* SPS
* Victron
* Netzwerk
* Kameras
* Speicher
* Softwaredienste

⸻

## 42. Diagnose darf technisch sein

Die normale Benutzeroberfläche soll einfach bleiben.

Für Administratoren und Servicezwecke darf es jedoch eine deutlich detailliertere Diagnoseansicht geben.

Dort können beispielsweise:

* Verbindungszustände
* Fehlercodes
* Logs
* Hardwareinformationen
* Schnittstellen
* Systemmetriken

angezeigt werden.

⸻

## 43. Wartung

Kehler OS soll langfristig Wartungsinformationen verwalten können.

Beispiele:

* nächste Wartung
* Wartungsintervalle
* erledigte Wartungen
* technische Hinweise
* Servicehistorie

⸻

## 44. Automatisierungen

Die einzelnen Module müssen Automatisierungen unterstützen können.

Beispiele:

```
Wenn Landstrom angeschlossen
→ bestimmte Systeme aktivieren
Wenn Batterie unter Schwellenwert
→ Warnung anzeigen
Wenn Nacht
→ bestimmte Beleuchtung aktivieren
```

Automatisierungen müssen zentral verwaltet werden.

⸻

## 45. Szenen

Mehrere Funktionen können in Szenen zusammengefasst werden.

Beispiele:

Nacht

* Licht ausschalten
* Türen prüfen
* bestimmte Systeme aktivieren
* Display dimmen

Abfahrt

* Stufen einfahren
* Markise einfahren
* Garage schließen
* Fenster prüfen
* bestimmte Systeme prüfen

Ankunft

* bestimmte Beleuchtung aktivieren
* relevante Systeme bereitstellen

Diese Beispiele dienen nur als Funktionsidee.

Die endgültigen Szenen sollen konfigurierbar sein.

⸻

## 46. Manuell vs. automatisch

Kehler OS muss unterscheiden können, ob eine Aktion:

* manuell
* automatisch
* durch eine Szene
* durch eine Systemregel

ausgelöst wurde.

Dies soll später auch in der Historie nachvollziehbar sein.

⸻

## 47. Erweiterbarkeit

Jedes Modul muss später erweitert werden können.

Beispiel:

Heute:

3 Tanks

Später:

4 oder mehr Tanks

Oder:

Heute:

4 Kameras

Später:

8 Kameras

Die Architektur darf nicht auf eine feste Anzahl unnötig beschränkt werden.

⸻

## 48. Hardwareunabhängigkeit

Die Module dürfen nicht direkt von einzelnen SPS-Adressen oder Hardwaredetails abhängig sein.

Die Software soll mit logischen Geräten arbeiten.

Beispiel:

```
garage.door
```

statt:

```
SPS DO 14
```

Die konkrete Hardwarezuordnung gehört zur Hardware- und Kommunikationsschicht.

⸻

## 49. Einheitliche Zustände

Alle Module sollen ein konsistentes Zustandsmodell verwenden.

Ein Zustand kann beispielsweise sein:

```
ON
OFF
ACTIVE
INACTIVE
OPEN
CLOSED
MOVING
ONLINE
OFFLINE
UNKNOWN
ERROR
WARNING
```

Nicht jedes Modul benötigt jeden Zustand.

Die Semantik muss jedoch eindeutig bleiben.

⸻

## 50. Benutzerrechte

Nicht jede Funktion muss für jeden Benutzer verfügbar sein.

Beispielsweise können bestimmte Diagnose- und Systemeinstellungen ausschließlich Administratoren zugänglich sein.

Normale Bedienfunktionen sollen dagegen schnell erreichbar bleiben.

⸻

## 51. Sicherheitsrelevante Bedienung

Bestimmte Aktionen können eine zusätzliche Bestätigung benötigen.

Beispiele:

* sicherheitsrelevante Aktionen
* potenziell gefährliche Bewegungen
* bestimmte Wartungsfunktionen

Die konkrete Einstufung muss später pro Funktion definiert werden.

⸻

## 52. Benutzerfreundlichkeit

Trotz der technischen Komplexität soll die Bedienung einfach bleiben.

Der Benutzer soll nicht verstehen müssen:

* welche SPS-Adresse verwendet wird
* welches Protokoll läuft
* welcher Datenpunkt angesprochen wird
* welcher Dienst dahinter arbeitet

Kehler OS abstrahiert diese Komplexität vollständig.

⸻

## 53. Gemeinsames System

Die einzelnen Module dürfen nicht wie separate Apps wirken.

Der Benutzer soll jederzeit das Gefühl haben:

Ich bediene Kehler OS.

Nicht:

Ich öffne jetzt eine Licht-App.

⸻

## 54. Claude erhält Gestaltungsfreiheit

Dieses Kapitel definiert die Funktionen.

Es schreibt Claude jedoch nicht vor, wie die einzelnen Funktionsseiten pixelgenau aussehen müssen.

Claude soll selbst entscheiden, welche UI-Struktur für:

* Licht
* Energie
* Wasser
* Klima
* Nivellierung
* Fahrzeug
* Kameras
* Garage
* Einstellungen

am sinnvollsten ist.

Dabei müssen die Entscheidungen mit allen bisherigen Kapiteln vereinbar sein.

⸻

## 55. Qualitätsmaßstab

Jedes Modul soll sich anfühlen, als wäre es Bestandteil desselben professionellen Systems.

Die Benutzeroberfläche soll:

* schnell
* logisch
* hochwertig
* touchoptimiert
* visuell konsistent
* verständlich

sein.

⸻

## 56. Zielbild

Am Ende soll Kehler OS sämtliche relevanten technischen Systeme des Wohnmobils unter einer einzigen Oberfläche zusammenführen.

Der Benutzer soll:

sehen können, was passiert.

verstehen können, warum es passiert.

eingreifen können, wenn es notwendig ist.

Automatisierungen definieren können, wenn gewünscht.

Dabei bleibt die technische Komplexität im Hintergrund.

⸻

## Ende Kapitel 9

Dieses Kapitel definiert die funktionalen Fahrzeugmodule von Kehler OS.

Es legt fest, was das System können soll.

Es legt bewusst nicht im Detail fest, wie Claude jede einzelne Benutzeroberfläche implementieren oder gestalten muss.

Die Gestaltung muss innerhalb des bereits definierten Kehler-OS-Designsystems erfolgen.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf das nächste Kapitel.

Verwende Kapitel 1 bis 9 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
