# KEHLER OS

# Kapitel 15 – Sicherheit, Benutzer, Berechtigungen und Zugriffskontrolle

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Dieses Kapitel definiert die Sicherheitsarchitektur von Kehler OS sowie Benutzer, Rollen, Berechtigungen, lokale und externe Zugriffe und den Schutz kritischer Fahrzeugfunktionen.

Sicherheit soll dabei nicht auf Kosten der normalen Bedienbarkeit gehen. Kehler OS soll im täglichen Betrieb schnell und angenehm bedienbar bleiben.

Verwende Kapitel 1–15 gemeinsam als verbindliche Grundlage.

Erst Kapitel 18 enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Grundprinzip

Kehler OS steuert reale physische Systeme eines Fahrzeugs.

Dazu können gehören:

* Türen
* Verriegelungen
* Garage
* Beleuchtung
* Pumpen
* Klima
* hydraulische Systeme
* Energiekomponenten
* weitere Aktoren

Damit besitzt Kehler OS andere Sicherheitsanforderungen als eine normale Informations-Webseite.

Ein Softwarefehler oder unberechtigter Zugriff darf nicht ohne weitere Schutzmechanismen gefährliche physische Aktionen ermöglichen.

⸻

## 2. Mehrere Sicherheitsebenen

Die Sicherheitsarchitektur soll aus mehreren Ebenen bestehen.

Konzeptionell:

```
Benutzer
   ↓
Authentifizierung
   ↓
Berechtigungsprüfung
   ↓
Kehler-OS-Systemlogik
   ↓
Sicherheitsbedingungen
   ↓
Hardwareabstraktion
   ↓
SPS / Steuergerät
   ↓
lokale Hardware-Sicherheitslogik
   ↓
Aktor
```

Keine einzelne Ebene soll unnötig die gesamte Verantwortung tragen.

⸻

## 3. Security by Design

Sicherheit darf nicht erst nach Fertigstellung der Software hinzugefügt werden.

Sie muss von Anfang an Teil der Architektur sein.

Dies betrifft insbesondere:

* Benutzerverwaltung
* API
* Netzwerkkommunikation
* Hardwarezugriffe
* Fernzugriff
* Konfiguration
* Logs
* Updates
* Backups
* Administratorfunktionen

⸻

## 4. Benutzerfreundlichkeit

Sicherheit darf Kehler OS nicht unnötig kompliziert machen.

Das Hauptbediengerät im Fahrzeug soll im normalen Alltag schnell nutzbar sein.

Es soll nicht erforderlich sein, für jede normale Aktion ständig:

* Passwörter einzugeben
* Warnfenster zu bestätigen
* Administratorfreigaben durchzuführen

Stärkere Sicherheitsmechanismen sollen gezielt dort eingesetzt werden, wo sie tatsächlich notwendig sind.

⸻

## 5. Benutzerkonten

Kehler OS soll eine Benutzerverwaltung unterstützen können.

Ein Benutzer besitzt beispielsweise:

```
User ID
Name
Rolle
Berechtigungen
Einstellungen
Authentifizierungsinformationen
```

Die genaue technische Umsetzung wird später festgelegt.

⸻

## 6. Rollen

Mindestens soll konzeptionell zwischen folgenden Rollen unterschieden werden können:

```
ADMIN
USER
```

Weitere Rollen können später ergänzt werden, falls sie tatsächlich sinnvoll sind.

⸻

## 7. Administrator

Ein Administrator besitzt erweiterte Rechte.

Dazu können gehören:

* Systemeinstellungen
* Hardwarekonfiguration
* Benutzerverwaltung
* Automatisierungen
* Diagnose
* Netzwerk
* Updates
* Servicefunktionen
* Logs
* Backups
* Kalibrierungen

⸻

## 8. Normaler Benutzer

Ein normaler Benutzer darf die für den täglichen Fahrzeugbetrieb vorgesehenen Funktionen verwenden.

Beispiele:

* Licht
* Klima
* Wasserinformationen
* Energieinformationen
* erlaubte Fahrzeugfunktionen
* Szenen
* Statusanzeigen

Er muss keinen Zugriff auf tiefgehende technische Einstellungen erhalten.

⸻

## 9. Berechtigungen statt nur Rollen

Die Architektur soll nicht ausschließlich auf festen Rollen beruhen.

Langfristig sollen auch einzelne Berechtigungen möglich sein.

Beispiel:

```
vehicle.light.control
vehicle.garage.control
vehicle.lock.control
automation.edit
diagnostics.view
system.configure
```

Die genaue Struktur wird später definiert.

⸻

## 10. Principle of Least Privilege

Ein Benutzer oder Dienst soll nur die Rechte erhalten, die tatsächlich benötigt werden.

Beispiel:

Ein Dienst, der lediglich Victron-Daten ausliest, benötigt nicht automatisch Schreibrechte auf die SPS.

⸻

## 11. Dienste besitzen ebenfalls Berechtigungen

Nicht nur Menschen benötigen Zugriffskontrolle.

Auch interne Dienste sollen nur die erforderlichen Rechte besitzen.

Beispiele:

```
Victron Adapter
PLC Adapter
Automation Engine
History Service
UI Backend
```

⸻

## 12. Authentifizierung

Kehler OS muss erkennen können, welcher Benutzer beziehungsweise Client auf das System zugreift.

Die konkrete Authentifizierungsmethode wird später festgelegt.

Mögliche Verfahren dürfen anhand von:

* Sicherheit
* Bedienkomfort
* Offline-Fähigkeit
* Geräteunterstützung

ausgewählt werden.

⸻

## 13. Lokaler Hauptbildschirm

Der fest beziehungsweise hauptsächlich im Fahrzeug verwendete Bildschirm benötigt eine besonders komfortable Bedienung.

Das System soll deshalb eine sichere Lösung ermöglichen, bei der normale tägliche Funktionen ohne ständige vollständige Neuanmeldung verfügbar sind.

⸻

## 14. Automatische Anmeldung

Für ein vertrauenswürdiges festes Bediengerät kann später eine kontrollierte automatische Anmeldung beziehungsweise Geräteauthentifizierung vorgesehen werden.

Dies darf jedoch nicht bedeuten, dass jedes Gerät im WLAN automatisch dieselben Rechte erhält.

⸻

## 15. Gerätekonzept

Kehler OS soll zwischen bekannten und unbekannten Clients unterscheiden können.

Beispiel:

```
Haupt-iPad
TRUSTED
unbekanntes Smartphone
UNTRUSTED
```

Die konkrete Vertrauensarchitektur wird später bestimmt.

⸻

## 16. Neue Geräte

Ein neues Gerät soll nicht automatisch vollständigen Zugriff erhalten.

Eine sichere Registrierung beziehungsweise Anmeldung ist erforderlich.

⸻

## 17. Sessions

Nach erfolgreicher Anmeldung kann eine Session verwendet werden.

Sessions müssen:

* eindeutig
* begrenzt
* widerrufbar
* sicher gespeichert

werden.

Die konkrete technische Umsetzung wird später festgelegt.

⸻

## 18. Session-Widerruf

Der Administrator soll später die Möglichkeit besitzen, ein Gerät beziehungsweise eine aktive Session zu entfernen.

Beispiel:

```
iPhone
Letzter Zugriff: heute
[ZUGRIFF ENTZIEHEN]
```

⸻

## 19. Verlorenes Gerät

Wenn ein Smartphone oder Tablet verloren geht, soll dessen Kehler-OS-Zugriff widerrufen werden können.

Dadurch muss nicht zwingend das gesamte System neu konfiguriert werden.

⸻

## 20. Kritische Funktionen

Nicht jede Funktion besitzt dasselbe Risiko.

Beispielsweise ist:

Innenlicht EIN

anders zu behandeln als:

Hydraulik bewegen

oder:

Fahrzeug entriegeln

⸻

## 21. Risikoklassen

Die Architektur soll Funktionen nach Sicherheitsrelevanz behandeln können.

Konzeptionell beispielsweise:

```
LOW
MEDIUM
HIGH
CRITICAL
```

Die endgültige Klassifizierung erfolgt später anhand der realen Funktionen.

⸻

## 22. Zusätzliche Bestätigung

Für bestimmte kritische Aktionen kann eine zusätzliche Benutzerbestätigung sinnvoll sein.

Dies darf jedoch nicht inflationär verwendet werden.

Wenn jeder Button eine Bestätigung verlangt, verliert eine Bestätigung ihre Bedeutung und verschlechtert die Bedienung.

⸻

## 23. Hold-to-Confirm

Bei bestimmten mechanischen oder kritischen Funktionen kann beispielsweise ein bewusstes längeres Drücken sinnvoller sein als ein normales Popup.

Die konkrete UX bleibt Claude überlassen.

Wichtig ist:

Kritische Aktionen müssen bewusst ausgelöst werden können, ohne die Oberfläche mit Warnfenstern zu überladen.

⸻

## 24. Keine falsche Sicherheit durch UI

Eine Bestätigung in der Benutzeroberfläche ist keine technische Sicherheitseinrichtung.

Auch nach der Bestätigung müssen:

* Systemlogik
* SPS
* Sensoren
* Hardwarefreigaben

weiterhin ihre Sicherheitsbedingungen prüfen.

⸻

## 25. Sicherheitslogik in der SPS

Zeitkritische beziehungsweise hardwareabhängige Sicherheitsbedingungen sollen auf der dafür geeigneten Steuerungsebene implementiert werden.

Beispiel:

```
Kehler OS:
Hydraulik ausfahren
↓
SPS:
Freigaben prüfen
↓
nur bei gültigen Bedingungen:
Ausgang ansteuern
```

⸻

## 26. Kehler OS darf keine SPS-Sicherheit umgehen

Es darf keinen „Force“-Befehl für normale Benutzer geben, mit dem eine Hardware-Sicherheitsbedingung einfach umgangen wird.

⸻

## 27. Servicefunktionen

Für Wartung können besondere Funktionen notwendig sein.

Diese gehören in einen getrennten:

SERVICE MODE

⸻

## 28. Service-Modus

Der Service-Modus kann beispielsweise ermöglichen:

* Sensoren einzeln prüfen
* Ausgänge testen
* Kalibrierungen durchführen
* Hardwarekommunikation prüfen
* Diagnoseinformationen anzeigen

Er ist nicht für den normalen Fahrzeugbetrieb gedacht.

⸻

## 29. Service-Modus schützen

Der Service-Modus soll nur für entsprechend berechtigte Benutzer verfügbar sein.

Ein versehentliches Aktivieren muss verhindert werden.

⸻

## 30. Service-Modus sichtbar kennzeichnen

Wenn der Service-Modus aktiv ist, muss dies deutlich erkennbar sein.

Beispiel:

```
SERVICE MODE ACTIVE
```

Der Benutzer darf nicht glauben, das System befinde sich im normalen Betriebszustand.

⸻

## 31. Testausgänge

Wenn im Service-Modus einzelne SPS-Ausgänge getestet werden können, müssen besondere Schutzmechanismen berücksichtigt werden.

Nicht jeder Ausgang darf zwangsläufig manuell geschaltet werden.

⸻

## 32. Keine Sicherheitsumgehung im Service-Modus

Auch ein Service-Modus darf grundlegende physische Schutzfunktionen nicht unkontrolliert deaktivieren.

⸻

## 33. Fernzugriff

Kehler OS soll architektonisch einen späteren sicheren Fernzugriff ermöglichen.

Der Fernzugriff ist jedoch nicht zwingend Bestandteil der ersten Version.

⸻

## 34. Mögliche Remote-Funktionen

Später könnten außerhalb des Fahrzeugs beispielsweise folgende Informationen abrufbar sein:

* Batterie
* Energie
* Temperaturen
* Tanks
* Systemstatus
* Warnungen
* Kameras, sofern vorhanden und freigegeben

⸻

## 35. Remote-Steuerung

Fernsteuerung physischer Funktionen benötigt stärkere Schutzmechanismen als reine Statusanzeige.

Beispiel:

Batteriestand ansehen

ist sicherheitstechnisch anders als:

Garage öffnen

⸻

## 36. Keine direkte Internetfreigabe der SPS

Die SPS darf nicht einfach direkt aus dem öffentlichen Internet erreichbar gemacht werden.

Nicht:

```
Internet
↓
Portfreigabe
↓
SPS
```

⸻

## 37. Kontrollierter Remote-Zugriff

Ein späterer Fernzugriff soll über eine abgesicherte Architektur erfolgen.

Konzeptionell:

```
Remote Client
↓
sichere Verbindung
↓
Kehler OS
↓
Authentifizierung
↓
Berechtigungen
↓
Command Processing
↓
SPS
```

⸻

## 38. VPN

Ein VPN kann eine mögliche Komponente der späteren Remote-Architektur sein.

Die konkrete Technologie wird erst bei der Implementierungsplanung gewählt.

Claude soll nicht allein aufgrund dieses Kapitels automatisch eine bestimmte VPN-Lösung festlegen.

⸻

## 39. Kein Vertrauen allein aufgrund des Netzwerks

Auch ein Gerät innerhalb des lokalen WLANs ist nicht automatisch vertrauenswürdig.

Grundsatz:

```
CONNECTED TO LAN
≠
AUTHORIZED
```

⸻

## 40. Netzwerksegmentierung

Für bestimmte Gerätegruppen kann später eine logische Netzwerksegmentierung sinnvoll sein.

Beispielsweise:

```
Control Network
Client Network
Camera Network
Guest Network
```

Die tatsächliche Notwendigkeit und Umsetzung wird anhand der realen Netzwerkhardware entschieden.

⸻

## 41. Gäste-WLAN

Falls das Fahrzeug später ein Gäste-WLAN besitzt, dürfen Gäste darüber keinen Zugriff auf Kehler OS erhalten.

⸻

## 42. API-Sicherheit

Die API muss unabhängig von der UI abgesichert werden.

Es darf nicht ausreichen, einen Button in der UI auszublenden.

Ein nicht berechtigter API-Aufruf muss vom Backend selbst abgelehnt werden.

⸻

## 43. Server-seitige Berechtigungsprüfung

Jeder relevante Befehl muss serverseitig geprüft werden.

Beispiel:

```
Client:
garage.open
↓
Backend:
Ist Benutzer authentifiziert?
Hat Benutzer Berechtigung?
Ist Aktion erlaubt?
Sind Bedingungen erfüllt?
↓
erst dann:
Command Processing
```

⸻

## 44. Eingabevalidierung

Alle externen Eingaben müssen validiert werden.

Dies betrifft beispielsweise:

* API-Aufrufe
* Konfigurationswerte
* Benutzereingaben
* Automatisierungen
* Netzwerkdaten
* Importdateien

⸻

## 45. Keine blinde Vertrauensannahme

Auch Daten aus internen Komponenten sollen nicht automatisch als korrekt behandelt werden, wenn sie technisch validiert werden können.

⸻

## 46. Sichere Kommunikation

Wo technisch sinnvoll, soll Kommunikation verschlüsselt beziehungsweise authentifiziert werden.

Besonders relevant sind:

* Benutzerzugriffe
* Remote-Zugriffe
* administrative Schnittstellen
* sensible Konfigurationsdaten

⸻

## 47. Lokale Protokolle

Bei industrieller Hardware kann nicht jedes vorhandene Protokoll moderne Verschlüsselung unterstützen.

In diesem Fall muss die Sicherheit durch die Gesamtarchitektur hergestellt werden.

Beispielsweise durch:

* Netzwerkisolierung
* Zugriffsbeschränkungen
* Gateway-Architektur
* keine direkte externe Erreichbarkeit

⸻

## 48. Passwörter

Passwörter dürfen niemals im Klartext gespeichert werden.

Die konkrete Passwortspeicherung soll nach aktuellen Sicherheitsstandards erfolgen.

⸻

## 49. Keine Passwörter im Quellcode

Zugangsdaten dürfen nicht direkt in den Programmcode geschrieben werden.

Nicht:

```
password = "..."
```

im normalen Quellcode.

⸻

## 50. Secrets

Zugangsdaten, Schlüssel und andere Secrets müssen getrennt von normalem Quellcode verwaltet werden.

⸻

## 51. Logs und sensible Daten

Logs dürfen keine unnötigen Geheimnisse enthalten.

Insbesondere sollen nicht protokolliert werden:

* Passwörter
* vollständige Tokens
* private Schlüssel

⸻

## 52. Audit Log

Für wichtige Aktionen soll ein Audit Log existieren können.

Es beantwortet:

```
WER?
WAS?
WANN?
VON WELCHEM CLIENT?
MIT WELCHEM ERGEBNIS?
```

⸻

## 53. Beispiel Audit Log

```
20:14:32
Benutzer:
Philipp
Gerät:
Haupt-iPad
Aktion:
Garage öffnen
Ergebnis:
SUCCESS
```

⸻

## 54. Automatisierungen im Audit

Automatische Aktionen müssen ebenfalls nachvollziehbar sein.

Beispiel:

```
20:30:00
Quelle:
Automation "Nacht"
Aktion:
Außenlicht ausschalten
Ergebnis:
SUCCESS
```

⸻

## 55. Fehlgeschlagene Zugriffe

Wichtige fehlgeschlagene Zugriffsversuche sollen protokolliert werden können.

Beispiel:

```
Unbekannter Client
→ Admin API
→ ACCESS DENIED
```

⸻

## 56. Rate Limiting

Authentifizierungs- und API-Endpunkte sollen gegen unnötig viele Anfragen geschützt werden können.

Dies verhindert sowohl technische Überlastung als auch bestimmte Angriffsversuche.

⸻

## 57. Brute-Force-Schutz

Die Authentifizierungsarchitektur soll Schutz gegen automatisierte Anmeldeversuche berücksichtigen.

⸻

## 58. Sperrmechanismen mit Augenmaß

Ein legitimer Benutzer darf nicht aufgrund eines kleinen Tippfehlers stundenlang aus dem eigenen Fahrzeugsteuerungssystem ausgesperrt werden.

Sicherheitsmechanismen müssen zum Einsatzgebiet passen.

⸻

## 59. Lokaler Notbetrieb

Kehler OS darf nicht die einzige Möglichkeit sein, wichtige physische Fahrzeugfunktionen zu bedienen.

Für geeignete kritische Systeme sollen physische beziehungsweise unabhängige Bedienmöglichkeiten erhalten bleiben.

⸻

## 60. Beispiel

Wenn der Raspberry Pi vollständig ausfällt, darf dies nicht automatisch bedeuten, dass eine essentielle Fahrzeugfunktion überhaupt nicht mehr bedient werden kann, sofern dies technisch vermeidbar ist.

⸻

## 61. Fail-Safe

Bei Kommunikationsverlust müssen Systeme einen definierten sicheren Zustand beziehungsweise ein definiertes Verhalten besitzen.

Dieser Zustand hängt von der jeweiligen Hardware ab.

Es darf keine universelle Annahme wie:

Bei Fehler alles AUS

geben.

Bei manchen Systemen könnte „AUS“ selbst problematisch sein.

⸻

## 62. Fail-Safe pro Gerät

Für jedes relevante Gerät muss später definiert werden:

```
Was passiert bei Kommunikationsverlust?
Was passiert bei SPS-Neustart?
Was passiert bei Raspberry-Pi-Ausfall?
Was passiert bei Sensorfehler?
Was passiert bei Stromausfall?
```

⸻

## 63. Watchdog

Watchdog-Mechanismen sollen dort eingesetzt werden, wo sie technisch sinnvoll sind.

Sie können beispielsweise erkennen:

* abgestürzten Dienst
* verlorene Kommunikation
* eingefrorene Prozesse
* fehlende Heartbeats

⸻

## 64. Kein unkontrollierter Neustart

Ein Watchdog darf nicht blind ständig ein System neu starten, ohne mögliche Auswirkungen zu berücksichtigen.

Insbesondere während mechanischer Vorgänge muss das Verhalten definiert sein.

⸻

## 65. Softwareupdates

Kehler OS muss aktualisierbar sein.

Updates können enthalten:

* Sicherheitsupdates
* Fehlerbehebungen
* neue Funktionen
* Hardwareunterstützung

⸻

## 66. Update-Sicherheit

Ein Update darf das System nicht unnötig in einen unbrauchbaren Zustand versetzen.

Vor einem Update sollen geeignete Prüfungen beziehungsweise Sicherungen möglich sein.

⸻

## 67. Keine automatischen riskanten Updates

Kritische Systemupdates sollen nicht unkontrolliert während des Fahrzeugbetriebs installiert werden.

⸻

## 68. Update-Zustand

Kehler OS soll später darstellen können:

Update verfügbar

oder:

System aktuell

Die konkrete Update-Infrastruktur wird später festgelegt.

⸻

## 69. Rollback

Für wichtige Softwarekomponenten soll geprüft werden, ob ein Rollback auf eine vorherige funktionierende Version möglich sein sollte.

⸻

## 70. Backups

Wichtige Kehler-OS-Daten müssen gesichert werden können.

Dazu gehören insbesondere:

* Konfiguration
* Benutzer
* Gerätezuordnungen
* Automatisierungen
* Szenen
* Kalibrierungen
* Systemeinstellungen

⸻

## 71. Backup ist nicht Live-Zustand

Ein Backup soll nicht einfach alte physische Fahrzeugzustände wiederherstellen.

Beispiel:

Ein Backup mit:

```
garage = CLOSED
```

darf nach Wiederherstellung nicht dazu führen, dass Kehler OS behauptet, die Garage sei aktuell geschlossen.

Der Live-Zustand muss erneut von der Hardware ermittelt werden.

⸻

## 72. Backup-Verschlüsselung

Wenn Backups sensible Informationen enthalten, muss geprüft werden, ob diese verschlüsselt werden müssen.

⸻

## 73. Wiederherstellung

Ein Backup ist nur sinnvoll, wenn es zuverlässig wiederhergestellt werden kann.

Die spätere Architektur muss deshalb auch einen definierten Restore-Prozess berücksichtigen.

⸻

## 74. Konfigurationsänderungen

Wichtige Systemänderungen sollen nachvollziehbar sein.

Beispiel:

```
Tankkapazität geändert:
400 L → 500 L
```

oder:

```
Hardware Mapping geändert
```

⸻

## 75. Kritische Konfigurationsänderungen

Bestimmte Änderungen dürfen nur Administratoren durchführen.

Beispiele:

* SPS-Mapping
* Hardwaredefinition
* Sicherheitsparameter
* Benutzerrechte
* Netzwerk
* Remote-Zugriff

⸻

## 76. Validierung vor Speicherung

Konfigurationsänderungen müssen vor Übernahme validiert werden.

Ungültige Werte dürfen das laufende System nicht beschädigen.

⸻

## 77. Atomare Konfiguration

Wo sinnvoll, soll eine Konfigurationsänderung vollständig oder gar nicht übernommen werden.

Ein teilweise gespeicherter Konfigurationszustand soll vermieden werden.

⸻

## 78. Konfigurationsversion

Es soll später geprüft werden, ob Konfigurationen versioniert werden.

Dadurch können Änderungen nachvollzogen und gegebenenfalls zurückgesetzt werden.

⸻

## 79. Physische Sicherheit und Cybersecurity

Kehler OS verbindet zwei Bereiche:

```
IT Security
+
Physical Safety
```

Ein Cybersecurity-Problem kann physische Auswirkungen besitzen.

Deshalb müssen beide Bereiche gemeinsam betrachtet werden.

⸻

## 80. Kameras

Falls Kameras später integriert werden, benötigen sie besondere Datenschutz- und Zugriffskontrollen.

Nicht jeder Benutzer muss automatisch Zugriff auf alle Kamerastreams erhalten.

⸻

## 81. Kamera-Fernzugriff

Remote-Kamerazugriff muss besonders abgesichert werden.

Kamerastreams dürfen nicht öffentlich erreichbar sein.

⸻

## 82. Keine standardmäßige Cloudpflicht

Kehler OS soll nicht gezwungen sein, sensible Fahrzeugdaten dauerhaft an einen externen Cloudanbieter zu übertragen.

Lokaler Betrieb bleibt das Grundprinzip.

⸻

## 83. Telemetrie

Falls später Telemetrie für Diagnose oder Entwicklung verwendet wird, soll transparent sein:

* welche Daten übertragen werden
* warum sie übertragen werden
* wohin sie übertragen werden

⸻

## 84. Datenschutz

Kehler OS soll nur Daten speichern, die für Funktionen, Diagnose, Historie oder Sicherheit tatsächlich sinnvoll sind.

⸻

## 85. Standortdaten

Falls Kehler OS später Standortinformationen integriert, müssen diese als sensible Fahrzeugdaten behandelt werden.

Die konkrete Integration ist derzeit nicht vorausgesetzt.

⸻

## 86. Sicherheit der Automatisierungen

Benutzerautomatisierungen dürfen nur Befehle ausführen, für die sie autorisiert sind.

Eine Automation darf nicht als Umweg verwendet werden, um Berechtigungen zu umgehen.

⸻

## 87. Ersteller versus Ausführung

Bei Automatisierungen muss später definiert werden, unter welcher Berechtigung sie ausgeführt werden.

Das System muss verhindern, dass ein Benutzer eine Automation erstellt, die ihm indirekt Administratorrechte verschafft.

⸻

## 88. Systemautomatisierungen

Interne Systemregeln können besondere Berechtigungen besitzen.

Sie müssen klar von normalen Benutzerregeln getrennt sein.

⸻

## 89. KI-Assistent

Falls später ein KI-Assistent in Kehler OS integriert wird, erhält auch dieser keinen unbegrenzten Hardwarezugriff.

⸻

## 90. KI-Berechtigungen

Der KI-Assistent soll nur die Funktionen aufrufen können, die ausdrücklich über eine kontrollierte Schnittstelle freigegeben wurden.

Nicht:

```
KI
↓
direkter SPS-Zugriff
```

Sondern:

```
KI
↓
Kehler OS Command API
↓
Berechtigung
↓
Validierung
↓
Sicherheitslogik
↓
Hardware
```

⸻

## 91. KI und kritische Aktionen

Bei kritischen Aktionen kann zusätzliche Benutzerbestätigung erforderlich sein.

Beispiel:

Benutzer sagt:

Öffne die Garage.

Der Assistent darf die Aktion nur entsprechend der definierten Berechtigungs- und Sicherheitsregeln ausführen.

⸻

## 92. Prompt Injection und externe Daten

Falls ein zukünftiger KI-Assistent Informationen aus externen Quellen verarbeitet, dürfen solche Inhalte niemals automatisch als autorisierte Fahrzeugbefehle behandelt werden.

Externe Daten sind Daten.

Sie sind keine Steuerbefehle.

⸻

## 93. Entwicklerzugriff

Entwicklungs- und Debugschnittstellen dürfen im normalen Produktionsbetrieb nicht unnötig offen sein.

⸻

## 94. Produktionsmodus

Die endgültige Installation im Wohnmobil soll einen klaren Produktionsmodus besitzen.

Debugfunktionen, Simulation und Testwerkzeuge müssen davon getrennt sein.

⸻

## 95. Simulation

Im Simulationsmodus dürfen keine realen Aktoren versehentlich angesteuert werden.

Die Trennung zwischen:

```
SIMULATION
```

und:

```
REAL HARDWARE
```

muss eindeutig sein.

⸻

## 96. Übergang Simulation → Real

Ein Wechsel vom Simulationsmodus auf reale Hardware darf nicht unbemerkt erfolgen.

Der Benutzer beziehungsweise Entwickler muss eindeutig erkennen, dass nun echte Fahrzeugfunktionen gesteuert werden.

⸻

## 97. Sicherheitsstatus

Kehler OS kann später einen übergeordneten Sicherheitsstatus darstellen.

Beispielsweise:

```
SYSTEM SECURITY
Local Access       OK
Remote Access      DISABLED
Unknown Clients    0
Critical Alerts    0
```

Die genaue Gestaltung bleibt Claude überlassen.

⸻

## 98. Keine überladene Security-Seite

Die normale Benutzeroberfläche soll nicht wie ein Server-Administrationspanel wirken.

Technische Security-Informationen gehören primär in:

```
Settings
Administration
Diagnostics
```

Das Hauptdashboard bleibt klar und fahrzeugorientiert.

⸻

## 99. Sicherheitsmeldungen

Relevante Sicherheitsmeldungen sollen verständlich sein.

Nicht nur:

```
AUTH_ERROR_0xA184
```

Sondern beispielsweise:

```
Unbekanntes Gerät hat versucht,
auf Kehler OS zuzugreifen.
```

Technische Details können zusätzlich in der Diagnose vorhanden sein.

⸻

## 100. Prioritäten

Sicherheitsmeldungen benötigen unterschiedliche Prioritäten.

Nicht jedes fehlgeschlagene Login ist ein kritischer Fahrzeugalarm.

Das System muss zwischen:

* Information
* Warnung
* Sicherheitsproblem
* kritischem Problem

unterscheiden können.

⸻

## 101. Alarmmüdigkeit vermeiden

Wenn Kehler OS ständig unnötige Sicherheitswarnungen zeigt, werden echte Probleme irgendwann ignoriert.

Nur relevante Informationen sollen prominent dargestellt werden.

⸻

## 102. Schutz gegen Fehlbedienung

Sicherheit bedeutet nicht nur Schutz vor Angreifern.

Kehler OS muss auch vor versehentlicher Fehlbedienung schützen.

Beispiele:

* unbeabsichtigtes Öffnen
* versehentliches Löschen
* falsche Kalibrierung
* gefährliche Serviceaktionen

⸻

## 103. Undo

Bei ungefährlichen Konfigurationsaktionen kann eine Undo-Funktion sinnvoll sein.

Bei physischen Aktionen ist „Undo“ jedoch nicht automatisch möglich.

Beispiel:

Garage öffnen

kann nicht einfach als Datenbankänderung rückgängig gemacht werden.

Es benötigt einen neuen realen Hardwarebefehl.

⸻

## 104. Kritische Löschvorgänge

Das Löschen wichtiger Konfigurationen, Benutzer oder Automatisierungen soll bewusst bestätigt werden.

⸻

## 105. Werkseinstellungen

Falls Kehler OS später eine Reset-Funktion besitzt, muss genau unterschieden werden zwischen:

* UI-Einstellungen zurücksetzen
* Benutzerkonfiguration zurücksetzen
* vollständiger Systemreset

Ein vollständiger Reset darf nicht versehentlich ausgelöst werden.

⸻

## 106. Sicherheitsarchitektur muss wartbar bleiben

Zu komplexe Sicherheit kann selbst Fehler verursachen.

Die Architektur soll deshalb:

* klar
* dokumentiert
* modular
* nachvollziehbar

sein.

⸻

## 107. Keine selbstgebauten Kryptoverfahren

Claude soll später keine eigenen Verschlüsselungs- oder Passwortalgorithmen erfinden.

Es sollen etablierte, geprüfte Verfahren und Bibliotheken verwendet werden.

⸻

## 108. Abhängigkeiten

Sicherheitsrelevante externe Bibliotheken sollen bewusst ausgewählt und aktuell gehalten werden.

Unnötige Abhängigkeiten sollen vermieden werden.

⸻

## 109. Security Updates

Sicherheitsupdates der verwendeten Plattform und Bibliotheken müssen langfristig installierbar sein.

⸻

## 110. Raspberry Pi

Der Raspberry Pi ist ein besonders wichtiger Sicherheitsknoten.

Er verbindet:

```
Clients
Backend
SPS
Victron
Daten
Remote-Funktionen
```

Daher muss seine Systemkonfiguration entsprechend geschützt werden.

⸻

## 111. Betriebssystem

Das Betriebssystem des Raspberry Pi soll für den Produktionsbetrieb möglichst minimal und kontrolliert konfiguriert werden.

Nicht benötigte Dienste sollen nicht unnötig laufen.

⸻

## 112. Administrative Zugänge

Administrative Systemzugänge zum Raspberry Pi sollen nicht offen beziehungsweise mit unsicheren Standardzugangsdaten betrieben werden.

⸻

## 113. Physischer Zugriff

Bei einem Wohnmobil ist physischer Zugriff auf Hardware grundsätzlich möglich.

Die Architektur darf deshalb nicht ausschließlich davon ausgehen, dass Netzwerkgeräte physisch unerreichbar sind.

⸻

## 114. SPS-Zugriff

Die SPS-Kommunikation soll nur für die Komponenten zugänglich sein, die sie tatsächlich benötigen.

Das Haupt-iPad soll beispielsweise nicht direkt SPS-Datenpunkte schreiben.

⸻

## 115. Backend als kontrollierter Zugangspunkt

Konzeptionell:

```
iPad
   │
   ▼
Kehler OS Backend
   │
   ├── Berechtigungen
   ├── Validierung
   ├── Sicherheitslogik
   ├── Logging
   │
   ▼
Hardware Adapter
   │
   ▼
SPS
```

Dadurch existiert ein kontrollierter Weg zur Hardware.

⸻

## 116. Sicherheitsgrundsatz

Der zentrale Grundsatz lautet:

Kein Benutzer, Client, Dienst, Automatisierung oder KI-Assistent erhält mehr Zugriff auf die reale Fahrzeughardware als für seine Aufgabe erforderlich.

⸻

## 117. Zweiter Sicherheitsgrundsatz

Eine schöne Benutzeroberfläche darf niemals einen Zustand als sicher darstellen, wenn die Hardware diesen Zustand nicht bestätigt hat.

⸻

## 118. Dritter Sicherheitsgrundsatz

Cloud, Internet und KI sind Erweiterungen. Die grundlegende sichere Fahrzeugfunktion bleibt lokal und deterministisch.

⸻

## 119. Zielbild

Für den normalen Benutzer bleibt Kehler OS sehr einfach:

```
LICHT
KLIMA
WASSER
ENERGIE
FAHRZEUG
```

Im Hintergrund arbeitet jedoch:

```
Authentication
      ↓
Authorization
      ↓
Command Validation
      ↓
Safety Logic
      ↓
Hardware Abstraction
      ↓
SPS / Victron
      ↓
Physical Hardware
```

Diese Komplexität soll der Benutzer im normalen Betrieb nicht sehen.

⸻

## 120. Ziel für Claude

Wenn später mit der tatsächlichen Entwicklung begonnen wird, darf Claude Sicherheit nicht mit folgendem Ansatz behandeln:

Wir bauen zuerst alles
und sichern es später ab.

Stattdessen müssen:

* Architektur
* APIs
* Benutzerverwaltung
* Hardwarekommunikation
* Automatisierungen
* Remote-Zugriff

von Anfang an mit den entsprechenden Sicherheitsgrenzen entwickelt werden.

Gleichzeitig soll Claude keine unnötig komplizierte Enterprise-Infrastruktur für ein einzelnes Wohnmobil bauen.

Die Lösung muss zum tatsächlichen Projekt passen.

Das Ziel ist:

```
HOHE SICHERHEIT
+
HOHE ZUVERLÄSSIGKEIT
+
EINFACHE BEDIENUNG
```

⸻

## Ende Kapitel 15

Dieses Kapitel definiert die grundlegende Sicherheitsarchitektur von Kehler OS.

Festgelegt wurden insbesondere:

* Benutzer und Rollen
* granulare Berechtigungen
* vertrauenswürdige Bediengeräte
* Sessions
* Schutz kritischer Funktionen
* Service-Modus
* serverseitige Berechtigungsprüfung
* sichere API
* lokaler und späterer Remote-Zugriff
* keine direkte Internetfreigabe der SPS
* Audit Logs
* Fail-Safe-Verhalten
* Updates und Backups
* Schutz der Automatisierungen
* kontrollierter KI-Zugriff
* Trennung von Simulation und realer Hardware
* Schutz des Raspberry Pi
* Backend als kontrollierter Zugang zur Hardware

Sicherheit soll stark sein, aber die tägliche Bedienung von Kehler OS nicht unnötig kompliziert machen.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Noch 3 Kapitel: 16, 17 und anschließend Kapitel 18 mit dem finalen Entwicklungsauftrag.

Warte auf Kapitel 16.

Verwende Kapitel 1 bis 15 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.
