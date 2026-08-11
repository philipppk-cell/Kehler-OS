# Offene Hardwareanforderungen

Diese Datei sammelt alle realen Hardwareinformationen, die Kehler OS für die
produktive Integration benötigt und die aus den Kapiteln 1–18 **nicht** hervorgehen.

Grundregel (Kapitel 12 §77, Kapitel 18 §97): **Fehlende Hardwaredaten werden
niemals erfunden.** Solange ein Punkt hier offen ist, wird die betroffene
Funktion ausschließlich abstrahiert und simuliert. Eine reale mechanische oder
sicherheitsrelevante Ansteuerung wird nicht aktiviert (Kapitel 18 §136).

## Legende

| Status | Bedeutung |
| --- | --- |
| `OFFEN` | Information fehlt vollständig |
| `TEILWEISE` | Teilinformation vorhanden, Details fehlen |
| `GEKLÄRT` | beantwortet, Datum und Antwort im Abschnitt vermerkt |

| Blocker | Bedeutung |
| --- | --- |
| `BLOCKIEREND` | ohne diese Information kann die Funktion nicht real betrieben werden |
| `NICHT BLOCKIEREND` | Entwicklung läuft simuliert weiter, Nachtrag jederzeit möglich |

---

## A – Siemens S7-1511-1 PN

### A1 · Transportweg zur SPS — `GEKLÄRT` (2026-08-09)

**Antwort:** Keine OPC-UA-Lizenz. Es wird die **S7-Kommunikation (PUT/GET)
über snap7** verwendet. Details und Sicherheitsfolgen in
[ADR 0002](architektur/adr/0002-plc-transport.md).

**Daraus folgt für die SPS-Projektierung (TIA Portal):**
- „Zugriff über PUT/GET-Kommunikation durch entfernten Partner erlauben“ aktivieren
- bei allen betroffenen Datenbausteinen den **optimierten Bausteinzugriff deaktivieren**
- Verbindung über ISO-on-TCP, Port 102

**Wichtige Folge:** Dieser Weg kennt keine Verschlüsselung. Die Absicherung
liegt damit vollständig auf der Netztrennung — Punkt I3 ist dadurch
aufgewertet und nicht mehr optional.

<details>
<summary>Ursprüngliche Abwägung (historisch)</summary>


Es gibt zwei technisch saubere Wege. Die Entscheidung hat reale Kosten- und
Projektierungsfolgen und kann nicht von der Software allein getroffen werden.

**Option 1 – OPC UA (empfohlen)**
Die S7-1500 besitzt einen integrierten OPC-UA-Server. Er benötigt eine
kostenpflichtige SIMATIC-Runtime-Lizenz (Größenklasse abhängig von der Anzahl
der Nodes). Vorteile: benannte, selbstbeschreibende Nodes statt roher Adressen,
Verschlüsselung und Zertifikats-Authentifizierung, keine Notwendigkeit,
Bausteinschutz zu lockern.

**Option 2 – S7-Kommunikation (PUT/GET, via snap7)**
Kostenfrei, benötigt aber in TIA Portal:
- „Zugriff über PUT/GET-Kommunikation erlauben“ aktiviert
- den betroffenen Datenbausteinen den „optimierten Bausteinzugriff“ **deaktiviert**
- keine Transportverschlüsselung → Absicherung muss vollständig über
  Netzsegmentierung erfolgen (Kapitel 15 §47)

**Benötigte Antwort:** Welche Option? Falls OPC UA: liegt die Lizenz vor bzw.
soll sie beschafft werden?

**Zwischenlösung:** Der `PlcAdapter` ist als Interface definiert; beide
Transporte lassen sich dahinter implementieren, ohne dass Fachmodule,
State Store oder UI davon berührt werden.

</details>

### A2 · Netzwerkparameter der SPS — `OFFEN` · `BLOCKIEREND` für Phase 9

- IP-Adresse der CPU (PROFINET-Schnittstelle)
- Subnetz / Gateway
- Rack und Slot (üblicherweise Rack 0 / Slot 1 — bitte bestätigen)

### A3 · Datenpunkt-Mapping — `OFFEN` · `BLOCKIEREND` für Phase 9

**Teilweise beantwortet (2026-08-10, Foto des Schaltschranks):** Der Aufbau
ist sichtbar — CPU 1511-1 PN (6ES7511-1AL03-0AB0, im Zustand RUN), dazu
DI 16x24 V HF, DQ 8x24 V/2 A HF und DQ 16x24 V. Die Typenschlüssel stehen in
`config/hardware/devices.yaml` (ungetrackt).

> **Keine Kommunikationsbaugruppe sichtbar.** Für Modbus RTU zur Heizung wäre
> eine nötig (CM PtP); über Modbus TCP ginge es über die vorhandene
> PROFINET-Schnittstelle. Siehe Punkt G1.

Für **jede** Funktion, die real angebunden werden soll, wird benötigt:

| Feld | Beispielinhalt |
| --- | --- |
| logische Kehler-OS-ID | `vehicle.garage.door` |
| Richtung | read / write / read+write |
| SPS-Adresse | *(vom Projektverantwortlichen)* |
| Datentyp | Bool / Int / Real / Word |
| Bedeutung von TRUE/FALSE bzw. Wertebereich | z. B. TRUE = verriegelt |
| Rückmeldeadresse (falls getrennt vom Befehl) | |

Die Struktur dieser Tabelle ist bereits als leeres, kommentiertes
Konfigurationsschema hinterlegt (siehe `config/hardware/`). Sie wird
ausgefüllt, nicht neu erfunden.

### A4 · Ein-/Ausgangsbelegung — `OFFEN` · `NICHT BLOCKIEREND`

Vollständige Liste der bestückten DI-/DO-/AI-Baugruppen mit Kanalbelegung.
Wird für die Diagnose- und Serviceansicht benötigt, nicht für den Normalbetrieb.

### A5 · Sicherheitsverriegelungen in der SPS — `OFFEN` · `BLOCKIEREND` für Phase 11

Kapitel 12 §7 und Kapitel 15 §25 verlangen, dass sicherheitsrelevante
Bedingungen in der Steuerung selbst wirken und nicht nur in der Oberfläche.

Benötigt wird eine Aufstellung, **welche Verriegelungen die SPS bereits
selbst durchsetzt**, insbesondere:

- Darf die Hydraulik bei laufendem Motor / gelöster Handbremse fahren?
- Wird das Garagentor bei Bewegungshindernis hardwareseitig gestoppt?
- Existiert ein hardwareseitiger Not-Halt, und was schaltet er ab?
- Blockiert die SPS das Ausfahren der Stufen bzw. der Markise unter bestimmten
  Bedingungen?

> **ASSUMPTION (bis zur Klärung):** Kehler OS geht davon aus, dass **keine**
> dieser Verriegelungen existiert, und behandelt jede mechanische Bewegung als
> ungesichert. Entsprechende Befehle bleiben deaktiviert, bis die Frage
> beantwortet ist.

---

## B – Victron

### B1 · Schnittstelle des Cerbo GX — `TEILWEISE` · `BLOCKIEREND` für Phase 10

Der Cerbo GX bietet lokal zwei dokumentierte Wege:

- **MQTT** (lokaler Broker auf dem Cerbo, in den Einstellungen zu aktivieren) —
  push-basiert, damit ideal für Realtime und geringe Last. Erfordert
  regelmäßige Keepalive-Nachrichten, sonst stoppt der Broker die Publikation.
- **Modbus TCP** — dokumentierte Registerliste, polling-basiert.

**Empfehlung:** MQTT als Primärweg, Modbus TCP als Rückfallebene für einzelne
Register, die über MQTT nicht sauber verfügbar sind.

**Beantwortet (2026-08-10):** Die IP-Adresse des Cerbo GX ist bekannt und in
`config/hardware/devices.yaml` hinterlegt — ungetrackt, denn Adressen gehören
nicht ins Repository.

**Weiterhin offen:**
- Ist der lokale MQTT-Broker aktiviert? Mit oder ohne TLS/Authentifizierung?
- VRM-Portal-ID (Bestandteil aller MQTT-Topics)

> Eine eingetragene Adresse ist noch keine geprüfte Verbindung. Der
> Victron-Adapter bleibt `simulated`, bis er am realen Gerät gelaufen ist.

### B2 · Reale Gerätekonfiguration — `TEILWEISE` · `NICHT BLOCKIEREND`

**Beantwortet (2026-08-10):**

| Angabe | Wert | Wirkung |
| --- | --- | --- |
| Batteriekapazität | **900 Ah** | Energieinhalt 21,6 kWh (bei 24 V nominal) und daraus die Restlaufzeit |
| Landstromabsicherung | **16 A** | Die Eingangsstrombegrenzung ist einstellbar — 3 bis 16 A, höhere Werte weist der Command Bus ab |

**Weiterhin offen:**

- exakte MultiPlus-Variante und Nennleistung
- Batterietyp und BMS-Typ; ob die 900 Ah die *nutzbare* oder die
  *Nennkapazität* sind
- Anzahl und Typ der MPPT-Solarregler, installierte Modulleistung

**Was ohne diese Angaben fehlt — konkret:**

| Fehlt | Folge in der Oberfläche |
| --- | --- |
| installierte Modulleistung | keine Einordnung des Solarertrags („viel" oder „wenig") |
| MultiPlus-Variante | keine Lastgrenze für den Wechselrichter |

> **ASSUMPTION zur Kapazität:** Die 900 Ah werden als **Nennkapazität**
> geführt und mit 24 V Nennspannung zu 21,6 kWh gerechnet. Sollten davon nur
> ein Teil nutzbar sein, fällt die Restlaufzeit entsprechend zu günstig aus.
> Beides steht in `config/vehicle/vehicle.yaml` und ist eine Zahl, kein Code.

### B3 · Schreibzugriffe — `GEKLÄRT` (2026-08-09)

**Antwort:** Schreibend ausschließlich für **zwei** Funktionen:

1. Eingangsstrombegrenzung (Landstrom)
2. Wechselrichter ein/aus

Alles andere bleibt read-only. Umsetzung als Whitelist mit Wertebereichsprüfung,
Bestätigungspflicht beim Abschalten des Wechselrichters und vollständiger
Protokollierung — siehe [ADR 0003](architektur/adr/0003-victron-transport.md).

> Der Maximalwert der Strombegrenzung liegt vor: **16 A** (Punkt B2). Er ist
> als `max_value` konfiguriert, und der Command Bus weist jeden höheren Wert
> ab — auch wenn ein Client die Oberfläche umgeht.

---

## C – Tanks

### C1 · Sensorik — `OFFEN` · `BLOCKIEREND` für reale Anzeige

Pro Tank — **es sind vier**: zwei Frischwasser, Grau-, Schwarzwasser:

- Sensortyp (Druck, kapazitiv, Ultraschall, resistiv, Schwimmer)
- elektrisches Signal (4–20 mA / 0–10 V / Widerstand)
- Messbereich und Kennlinie
- an welchem Analogeingang angeschlossen

### C2 · Tankgeometrie — `GEKLÄRT` (2026-08-09)

**Beantwortet (2026-08-09) — Kapazitäten:**

| Tank | Kapazität |
| --- | --- |
| Frischwasser groß | 550 l |
| Frischwasser klein | 450 l |
| **Frischwasser gesamt** | **1000 l** |
| Grauwasser | 280 l |
| Schwarzwasser | 370 l |

Damit zeigt die Oberfläche Liter statt nur Prozent. Die Werte stehen in
`config/vehicle/vehicle.yaml` und sind durch einen Test festgehalten, damit
ein Zahlendreher auffällt.

**Beantwortet — Form:** Die Tanks sind **gleichmäßig geformt**. Die
Umrechnung Prozent → Liter ist damit linear und korrekt; eine Kalibrierkurve
wird nicht benötigt (Kapitel 12 §37).

### C3 · Warnschwellen — `GEKLÄRT` (2026-08-09)

**Antwort — zwei Stufen je Tank:**

| Tank | Warnung | Kritisch |
| --- | --- | --- |
| Frischwasser (beide) | unter 20 % | unter 10 % |
| Grauwasser | über 80 % | über 90 % |
| Schwarzwasser | über 80 % | über 90 % |

Die Schwellen stehen in `config/vehicle/vehicle.yaml` und sind durch einen
Test festgehalten — insbesondere ihre **Richtung**, denn eine vertauschte
Schwelle schweigt genau dann, wenn sie gebraucht wird.

Ein Test stellt zusätzlich sicher, dass die kritische Stufe **hinter** der
Warnstufe liegt. Wären sie vertauscht, erschiene die kritische Meldung zuerst
und die Warnstufe würde nie sichtbar.

> **Folge für den Systemstatus:** Eine überschrittene kritische Schwelle hebt
> den Gesamtzustand auf `CRITICAL` („Kritisch"). Das ist beabsichtigt — bei
> 10 % Frischwasser ist das die dringendste Aussage, die das Fahrzeug treffen
> kann. Durch die eng gefassten Grenzen bleibt der Fall selten, und damit
> behält die Stufe ihre Bedeutung (Kapitel 13 §55).

---

## D – Nivellierung

### D1 · Neigungssensorik — `OFFEN` · `BLOCKIEREND` für Phase 11

- Sensormodell und Schnittstelle
- Anzahl der Messpunkte
- Einbaulage und Vorzeichenkonvention (welche Richtung ist „positiv“?)
- Auflösung und Genauigkeit

### D2 · Hydraulik — `OFFEN` · `BLOCKIEREND` für Phase 11

- Ventilbelegung der vier Zylinder (ausfahren/einfahren je Zylinder)
- Endlagenrückmeldung vorhanden? Pro Zylinder?
- Drucksensorik vorhanden?
- maximale zulässige Fahrzeit je Bewegung (für Timeout-Auslegung)
- Wer regelt die automatische Nivellierung — SPS oder Kehler OS?

> **Diese Gruppe wird bewusst zuletzt integriert** (Kapitel 18 §91): Hydraulik
> ist ausdrücklich **nicht** das erste reale Testobjekt.

---

## E – Aufbaufunktionen

### E1 · Garagentor — `OFFEN` · `BLOCKIEREND` für reale Steuerung

- Endschalter für AUF und ZU vorhanden? Beide?
- Ist eine Zwischenposition messbar oder nur AUF/ZU?
- Antriebsart, Laufzeit, Stopp-Möglichkeit während der Fahrt
- Hindernis-/Klemmschutz vorhanden?

Ohne Endlagenrückmeldung kann Kehler OS die Zustände `OPENING`/`CLOSING` nicht
belastbar darstellen und beschränkt sich auf `UNKNOWN` (Kapitel 18 §32, §106).

### E2 · Türen und Fenster — `OFFEN` · `NICHT BLOCKIEREND`

- Anzahl und Bezeichnung der überwachten Türen
- Anzahl und Bezeichnung der überwachten Fenster
- Kontakttyp (Öffner/Schließer)

### E3 · Verriegelungen — `OFFEN` · `BLOCKIEREND` für reale Steuerung

- Zentralverriegelung: ein Sammelsignal oder Einzelschlösser?
- **Gibt es je Schloss eine Rückmeldung?** (Kapitel 12 §46 — ohne Rückmeldung
  bleibt der Zustand `UNKNOWN`)
- Schrankverriegelungen: Anzahl, Bezeichnung, Rückmeldung vorhanden?

### E4 · Stufen und Markise — `OFFEN` · `NICHT BLOCKIEREND`

- Endlagenrückmeldung vorhanden?
- Laufzeiten
- Ist die Markise über Kehler OS steuerbar oder nur überwachbar?

---

## F – Licht

### F1 · Lichtkreise — `ENTFÄLLT` (2026-08-10)

**Antwort:** Die Beleuchtung wird **nicht** über die SPS gesteuert. Es sind
gewöhnliche Lichtschalter verbaut.

Damit gibt es keine Lichtentities, keinen Lichtbereich in der Oberfläche und
keinen Reiter. Das ist keine Lücke, die später gefüllt wird — was nicht
angebunden ist, erscheint nicht (Kapitel 12 §55, Kapitel 13 §60).

> Sollte später doch ein Lichtkreis auf die SPS geführt werden, ist der Weg
> derselbe wie bei jeder anderen Funktion: Entity in
> `config/vehicle/vehicle.yaml` eintragen, Adresse in `config/hardware/`
> ergänzen. Ein eigener Bereich in der Oberfläche lohnt sich erst, wenn es
> mehr als eine Handvoll Kreise gibt.

---

## G – Klima und Heizung

### G0 · Systemtrennung — `GEKLÄRT` (2026-08-10)

**Antwort:** Klima und Heizung laufen **beide** über die Steuerung, sind aber
**getrennte Systeme**. Die Heizung bekommt deshalb einen eigenen Bereich.

Umgesetzt ist die Trennung nicht nur in der Navigation, sondern im Datenmodell:
eigene Domäne `heating.`, eigener Schalter, eigener Sollwert
(`heating.temperature.target` neben `climate.cooling.target`). Ein gemeinsamer Sollwert
wäre die aufgeräumtere Oberfläche und die falsche Anlage — das Verstellen der
Heizung würde stillschweigend die Klimaanlage mitverstellen.

Gemeinsam bleibt allein die **gemessene** Innentemperatur: Es gibt einen
Wohnraum und einen Fühler (`climate.living.temperature`). Beide Bereiche
zeigen denselben Messwert, weil es derselbe ist.

### G1 · Heizungsanlage — `TEILWEISE` (2026-08-10) · `BLOCKIEREND` für reale Steuerung

**Beantwortet:** Verbaut ist eine **SCHEER selection 10/17 kW** mit der
Steuerung **SCHEER HeatMate V4.02**. Sie ist die zentrale Heizungs- und
Warmwasseranlage des Fahrzeugs und hat zwei Wärmequellen: Brenner und
Elektroheizung.

**Beantwortet:** Die HeatMate **behält die Regelung und alle
sicherheitsrelevanten Funktionen**. Kehler OS ist übergeordnete Bedien- und
Anzeigeebene (Details in [ADR 0009](architektur/adr/0009-heizungsanbindung-scheer.md)).

**Beantwortet:** Die Anlage besitzt CAN und Modbus. Datenkette:
SCHEER/HeatMate → Modbus → Siemens S7-1500 → Kehler OS.

**Beantwortet (2026-08-10) — der Stand der Verbindung:** An der SCHEER-Anlage
**gibt es einen Modbus-Anschluss**, er ist aber **noch nicht verdrahtet**. Die
Heizung ist derzeit gar nicht mit der SPS verbunden — weder über einen Bus
noch über Kontakte. Das soll nachgeholt werden.

> Damit ist die Reihenfolge klar: **Erst die Verdrahtung, dann die
> Registerliste.** Solange kein Draht liegt, ändert die beste Dokumentation
> nichts — es gibt keinen Weg, über den gelesen werden könnte.

**Beantwortet (2026-08-10), nachgetragen:**

| Angabe | Wert |
| --- | --- |
| Heizkreise | **zwei** — Kreis 1 Heizkörper, Kreis 2 Fußbodenheizung |
| Temperatur | **eine** — ein Ist- und ein Sollwert, Kessel und Warmwasser **nicht** getrennt |
| Elektroheizung | **drei Stufen: 1 kW, 2 kW, 3 kW** |

> Diese drei Angaben haben einen früheren Entwurf korrigiert, der drei
> Heizkreise, zwei getrennte Temperaturen und eine Leistungsstufe ohne
> bekannten Bereich vorsah. Alle drei waren Annahmen; sie sind ersetzt.

#### Was das Foto der Bedieneinheit zeigt (2026-08-10)

Die HeatMate sitzt im selben Schaltschrank wie die SPS. Zu sehen sind:

- ein **Display mit einer Temperatur in °C** (im Foto 63 °C) — passt zu der
  Angabe, dass die Anlage genau **eine** Temperatur führt
- ein **Drehknopf**, über den der Wert verstellt wird
- eine **Ein/Aus-Taste** mit grüner Leuchte
- vier **Statusleuchten** in der Kopfzeile
- fünf **Tasten mit eigener Leuchte** an der rechten Seite, darunter eine mit
  Mondsymbol (Nachtabsenkung)

Was die einzelnen Symbole bedeuten, wird aus dem Foto **nicht** abgeleitet.
Zuordnung ist Sache der Gerätedokumentation, nicht der Bildbetrachtung.

#### Weiterhin offen — **blockierend**

- **Die Verdrahtung selbst.** Der Anschluss existiert, ist aber nicht
  angeschlossen — der erste Schritt.
- **Modbus RTU oder TCP?** Am Anschluss der Anlage abzulesen: zwei bzw. drei
  Adern (RS-485) bedeuten RTU, und dann braucht die S7-1500 eine
  Kommunikationsbaugruppe, die auf dem Foto nicht zu sehen ist. Eine
  Netzwerkbuchse bedeutet TCP und käme über die vorhandene
  PROFINET-Schnittstelle. **Diese Frage entscheidet, ob Hardware fehlt.**
- **Modbus-Registerliste der HeatMate V4.02.** Welcher Wert liegt unter
  welcher Adresse, in welcher Skalierung, mit welchem Datentyp?
- **Welche Funktionen sind schreibbar?** Möglicherweise ist ein Teil der
  Anlage dauerhaft nur lesbar. Das wäre kein Mangel, sondern die Eigenschaft
  des Geräts — die Oberfläche zeigt die Funktion dann ohne Bedienelement.
- **Zuordnung Registerwert → Zustandsname.** Kehler OS führt ein eigenes
  Vokabular (`OFF`, `DEMAND`, `HEATING`, `POSTRUN`, `FAULT` …). Welcher
  Rohwert darauf abgebildet wird, entscheidet der Adapter — geraten wird
  nichts.
- **Stellbereich der Solltemperatur.** Ohne ihn gibt es keine Verstellung,
  nur die Anzeige.
- **Physikalische Anbindung an die S7-1500** (Modbus-Master-Baugruppe oder
  CM-Modul) und Aufteilung der Datenbausteine — siehe auch Punkt A3.
- **Zirkulationspumpe:** verbaut und angebunden, oder nicht vorhanden?
- **Tanküberwachung:** welcher Tank, welche Einheit?

#### Stand der Umsetzung

Die Anlage ist in `config/vehicle/vehicle.yaml` **vollständig beschrieben** —
22 Entities. Jede trägt `unverified: true`, und das ist wirksam: Eine
unverifizierte Entity bekommt keine Capabilities und damit in der Oberfläche
kein Bedienelement. Die Struktur steht, die Bedienung entsteht mit der
Bestätigung.

**Was bewusst fehlt:** Betriebsarten, ein „heizt gerade"-Zustand und
Warmwassertemperatur als eigener Wert. Alles setzt voraus, dass die Anlage es
meldet — nachgebaut wird keine Regelung (Kapitel 12 §67, Kapitel 18 §29).

### G1b · Klimagerät — `TEILWEISE` (2026-08-10) · `NICHT BLOCKIEREND`

**Beantwortet:** Es ist eine wandmontierte **LG**-Anlage.

| Angabe | Wert |
| --- | --- |
| Hersteller | **LG** |
| Modellnummer | `S3-M09JA3FA` |
| Seriennummer | `202TKYU02330` |
| Geräte-App | 5116.01 |
| Modemmodul | `clip_hna_v1.9.237_RT` |
| Firmware 1 | `SAA38690409.00000409.0` |

**Beantwortet:** **Wie das Gerät an die Steuerung kommt, ist noch nicht
entschieden** — es soll aber geschehen.

#### Was daraus für Kehler OS folgt

Die Klimaanlage ist **derzeit nicht angebunden**, und der Weg dorthin steht
nicht fest. Deshalb tragen `climate.cooling.state` und `climate.cooling.target`
seit dem 2026-08-10 `unverified: true` — dieselbe Behandlung wie die Heizung.

Das ist keine Formalie: Vorher zeigte die Klimaseite einen Schalter und einen
Sollwertsteller. Beides hätte eine Bedienung versprochen, deren Weg noch nicht
einmal ausgewählt ist. Jetzt zeigt sie die Anlage und sagt dazu, dass die
Anbindung aussteht.

Die beiden Temperaturfühler bleiben davon unberührt — sie gehören zum
Fahrzeug, nicht zum Klimagerät (Punkt G2).

#### Die offene Frage: auf welchem Weg?

Vier Möglichkeiten, mit sehr verschiedenen Folgen. Welche zutrifft, ist beim
Fachbetrieb bzw. bei LG zu klären — geraten wird nichts:

1. **Potentialfreier Kontakt an der SPS** — die Steuerung schaltet ein und
   aus, mehr nicht. Einfach und robust; Sollwert und Betriebsart blieben am
   Gerät. Kehler OS zeigte dann nur Ein/Aus, und das wäre ehrlich.
2. **Kabelgebundene Schnittstelle des Herstellers** — LG bietet für die
   Gebäudetechnik Module und Gateways an. Ob dieses Modell dafür vorbereitet
   ist und welches Modul passt, ist **beim Hersteller zu erfragen**; die
   Modellnummer oben genügt für die Anfrage.
3. **Infrarot** — die Befehle der Fernbedienung nachbilden. Funktioniert, ist
   aber blind: Es gibt keine Rückmeldung, und ohne Rückmeldung darf Kehler OS
   keinen Zustand behaupten (Kapitel 18 §37). Das wäre die schlechteste der
   vier Varianten.
4. **Über das WLAN-Modul** — die Anlage hat eines und wird darüber per App
   bedient. Läuft das über die Herstellerwolke, widerspricht es Local First
   (Kapitel 6 §31); eine rein lokale Schnittstelle wäre dagegen brauchbar.

**Empfehlung:** Zuerst Weg 2 prüfen — er ist der einzige, der Zustand *und*
Sollwert liefert, ohne von einer Wolke abzuhängen. Weg 1 als Rückfallebene.

**Vorläufig hinterlegt:** 16–30 °C, Schrittweite 0,5 K. Anders als bei der
Strombegrenzung ist ein falscher Bereich hier ungefährlich; er wird mit der
Anbindung geprüft.

Eine **Lüftung** wird nicht angenommen. Ob eine anzubindende existiert, ist
offen.

### G2 · Temperatursensoren — `TEILWEISE` (2026-08-10)

Angenommen und in der Oberfläche verwendet werden zwei Fühler: Wohnraum
(`climate.living.temperature`) und außen (`climate.outside.temperature`).
Solange nicht bekannt ist, welche Fühler tatsächlich verbaut sind, bleiben
es genau diese zwei — weitere Zonen werden nicht erfunden.

Offen: Liste der Sensoren mit Einbauort, Typ und Anschluss.

---

## H – Kameras

### H1 · Bestand — `OFFEN` · `NICHT BLOCKIEREND`

Kapitel 12 §51 und Kapitel 18 §33: Es wird **keine** installierte Kamera
angenommen. Sobald Kameras existieren, werden benötigt: Anzahl, Modell,
Stream-URL/Protokoll (RTSP/ONVIF), Auflösung, Zugangsdaten, Einbauort.

---

## I – Plattform und Netzwerk

### I1 · Speichermedium des Raspberry Pi — `GEKLÄRT` (2026-08-09)

**Antwort:** **SSD.** Damit ist die Dauerschreiblast der Zeitreihen-Datenbank
unkritisch und die Datenhaltung aus [ADR 0004](architektur/adr/0004-datenhaltung.md)
uneingeschränkt tragfähig.

Offen bleibt lediglich die Anbindung (USB 3.0 oder NVMe via HAT) — für die
Installationsdokumentation, nicht blockierend.

### I2 · Stromversorgung und Pufferung — `OFFEN` · `NICHT BLOCKIEREND`

- Wie wird der Pi versorgt (24 V → 5 V Wandler)?
- Existiert eine USV/Pufferung (Kapitel 11 §36, Kapitel 17 §40)?
- Gibt es ein Signal „Versorgung fällt gleich aus“ für ein kontrolliertes
  Herunterfahren?

### I3 · Netzwerk — `TEILWEISE` (2026-08-10) · `BLOCKIEREND` für den Produktivbetrieb

**Beantwortet:** Ein **LTE-Router mit Gigabit-Switch** verbindet alle Geräte.
Ein Netz, ein Segment, keine Trennung. Subnetz und Adressen stehen in
`config/hardware/devices.yaml` (ungetrackt).

#### Was daraus folgt — der wichtigste offene Punkt vor dem Produktivbetrieb

Die S7-Kommunikation über PUT/GET kennt **weder Verschlüsselung noch
Authentifizierung** (ADR 0002). Das war eine bewusste Entscheidung, aber sie
kam mit einer Bedingung: Die Absicherung liegt vollständig auf der
Netztrennung (Kapitel 15 §47).

**Seit dem 2026-08-10 gilt das für das gesamte System und nicht nur für die
SPS.** Der Fahrzeughalter möchte keine Benutzer und keine Berechtigungen
(Beschluss W14). Damit ist auch die Kehler-OS-API ohne Anmeldung erreichbar:
Wer im Netz ist, kann das Garagentor öffnen, die Markise ausfahren und den
Wechselrichter schalten.

Die Sicherheitslage verschiebt sich dadurch nicht — sie war für die SPS
ohnehin schon so. Aber dieser Punkt ist jetzt die **einzige** tragende
Maßnahme, und er bleibt blockierend für den Produktivbetrieb.

Diese Trennung gibt es derzeit nicht. In einem flachen Netz hinter einem
LTE-Router heißt das konkret: Wer im WLAN ist — ein Gast, ein kompromittiertes
Gerät, ein vergessenes Handy —, kann die SPS ohne Passwort ansprechen. Nicht
Kehler OS umgehen, sondern **direkt die Steuerung**.

Solange nichts real angesteuert wird, ist das folgenlos. Vor dem
Produktivbetrieb muss es gelöst sein.

**Zwei gangbare Wege:**

1. **VLAN auf dem Switch** — die SPS in ein eigenes Segment, der Pi mit einem
   Bein in beiden. Setzt einen verwalteten Switch voraus.
2. **Zweite Netzwerkschnittstelle am Pi** — die SPS hängt an einem eigenen
   Kabel direkt am Pi, sonst nichts. Braucht keinen verwalteten Switch, und
   die Trennung ist physisch statt konfiguriert.

Im Fahrzeug ist der zweite Weg meist der praktischere: ein Kabel, kein
Konfigurationsaufwand, und der Pi wird zum einzigen Weg zur SPS.

**Offen:** Modelle von Router und Switch — kann der Switch VLANs? Falls nicht,
entfällt Weg 1.

### I4 · Hauptdisplay — `GEKLÄRT` (2026-08-10)

**Antwort:** Ein **iPad Pro 13 Zoll**. Damit ist die Anzeige kein
angeschlossener Bildschirm, sondern ein eigenes Gerät im Netz — die Oberfläche
läuft in Safari und nicht als Kiosk auf dem Pi.

| Frage | Antwort |
| --- | --- |
| Auflösung | 1376 × 1032 Punkte (2× physisch), quer wie hoch |
| Anschluss | keiner — über das Netzwerk |
| Touch | die einzige Bedienung; Maus und Tastatur gibt es nicht |
| Helligkeit softwareseitig steuerbar | **nein**, das macht iPadOS |
| Ausrichtung | beide, das Gerät wird gedreht |

Beide Ausrichtungen sind gegen einen laufenden Server geprüft. Das Layout
bricht im Hochformat auf eine Spalte um, und die Statuskarte geht bereits
unterhalb von 1500 px unter das Fahrzeug statt darauf — bei 1376 px bliebe
neben ihr kein Platz für ein 11,5 m langes Fahrzeug.

**Offen, aber nicht blockierend:**

- Soll die Oberfläche als Web-App auf dem Startbildschirm liegen (Vollbild
  ohne Safari-Leiste)? Die nötigen Angaben stehen bereits in `index.html`.
- Wie kommt das iPad ins Fahrzeugnetz — über das WLAN des LTE-Routers?
- Der Bildschirm ist nicht dauerhaft an. Das entkoppelt Kehler OS von der
  Anzeige: Der Pi läuft weiter, auch wenn niemand hinsieht.

#### Nachtrag (2026-08-10): „Bildschirm wach halten" braucht HTTPS

Beim Bau der Einstellungsseite kam ein konkreter Grund für TLS dazu, der
vorher nicht auf der Liste stand.

Die Browser-Schnittstelle, mit der sich das Abschalten des Bildschirms
verhindern lässt (*Screen Wake Lock*), existiert **nur in einem gesicherten
Kontext** — also über HTTPS oder auf `localhost`. Wird die Oberfläche vom Pi
über einfaches `http://` ausgeliefert, ist sie auf dem iPad schlicht nicht
vorhanden.

Für ein fest verbautes Bedienpanel ist das spürbar: Der Bildschirm geht nach
der Zeitspanne aus, die iPadOS vorgibt, und lässt sich softwareseitig nicht
davon abhalten.

Die Oberfläche blendet die Einstellung deshalb nicht kommentarlos aus, sondern
sagt den Grund — es ist kein Mangel des Tablets, sondern eine Folge der
Auslieferung. Gelöst wird es zusammen mit I3: Wer ohnehin ein eigenes Segment
für die SPS aufbaut, kann dem Pi bei der Gelegenheit ein Zertifikat geben.

**Kein zusätzlicher Bedarf an Angaben** — nur ein Argument mehr für den
Punkt, der ohnehin vor dem Produktivbetrieb ansteht.

### I5 · Zeitbasis ohne Internet — `OFFEN` · `NICHT BLOCKIEREND`

Besitzt der Pi eine gepufferte Echtzeituhr (RTC-Modul)? Ohne RTC und ohne
Internet ist nach einem Stromausfall keine korrekte Zeit verfügbar, was die
Historie beeinträchtigt (Kapitel 16 §85).

**Bereits berücksichtigt (2026-08-10):** Die Diagnoseseite rechnet aus genau
diesem Grund keine Altersangabe gegen die Uhr des iPads. Sie vergleicht
ausschließlich Zeitstempel des Fahrzeugrechners untereinander („Rückstand").
Damit bleibt die Spalte auch dann brauchbar, wenn die beiden Uhren
auseinandergehen — was ohne RTC nach jedem Stromausfall der Fall wäre.

Für die **Historie** löst das nichts: Dort geht es um absolute Zeit, und die
braucht eine verlässliche Quelle.

---

## J – Betriebszustände

### J1 · Quelle für den Fahrmodus — `OFFEN` · `BLOCKIEREND` für fahrmodusabhängige Warnungen

Kapitel 14 §35 verbietet ausdrücklich, den Fahrzustand zu erraten.

**Benötigte Antwort:** Welches reale Signal zeigt an, dass das Fahrzeug fährt
bzw. fahrbereit ist? Denkbar wären Zündung, Handbremse, Motorlauf, Tachosignal,
Getriebestellung — aber nur, wenn eines davon tatsächlich auf die SPS geführt ist.

Ohne diese Information bleibt der Fahrzeugmodus manuell umschaltbar, und
fahrmodusabhängige Warnungen (z. B. „Garage offen während der Fahrt“) sind
inaktiv statt unzuverlässig.

---

## K – Fahrzeugdarstellung

### K1 · Abmessungen des Fahrzeugs — `TEILWEISE` · `NICHT BLOCKIEREND`

**Beantwortet (2026-08-09):** Gesamtlänge **11,5 m**, Gesamthöhe **4,0 m**.

Die dreidimensionale Fahrzeugdarstellung im Dashboard ist im Übrigen aus Fotos
nachgebildet (siehe
[Fahrzeugreferenz](anforderungen/referenzen/fahrzeug-referenz.md)). Fotos
liefern Proportionen, keine Maße. Für ein durchgehend maßhaltiges Modell
fehlen noch:

- Gesamtbreite *(derzeit mit 2,55 m angesetzt — das zulässige Höchstmaß)*
- Radstand und Achsabstand des Tandems
- Überhang vorn und hinten
- Höhe des Wohnbodens über Grund
- Reifengröße

> **ASSUMPTION (bis zur Klärung):** Die Werte in
> `frontend/src/vehicle3d/dimensions.ts` sind aus den Fotos **geschätzt**. Sie
> stehen dort an genau einer Stelle und sind als Schätzung gekennzeichnet. Die
> Korrektur ist ein Zahlenaustausch, keine Modellüberarbeitung.
>
> Das Modell ist ausschließlich Anzeige. Aus ihm wird nichts berechnet — keine
> Durchfahrtshöhe, kein Wendekreis, kein Gewicht. Ein geschätztes Maß kann
> daher zu keiner falschen Aussage über das Fahrzeug führen.

### K2 · Falls ein fertiges 3D-Modell geliefert wird — `OFFEN` · `NICHT BLOCKIEREND`

**Gefragt am 2026-08-11:** In welchem Format müsste ein Fahrzeugmodell
vorliegen?

**Zuerst die Gegenfrage:** Für ein *maßhaltiges* Fahrzeug wird **keine Datei**
gebraucht, sondern die Zahlen aus K1. Die Darstellung entsteht aus Code
(ADR 0008), die Korrektur ist ein Zahlenaustausch. Wer ein Modell erst
anfertigen lassen müsste, geht den teureren Weg zum schlechteren Ergebnis:
Eine Modelldatei lässt sich später nur mit dem passenden Programm ändern.

**Liegt aber bereits ein Modell vor** — etwa vom Aufbauhersteller —, dann:

| Anforderung | Wert |
| --- | --- |
| Format | **glTF 2.0 binär (`.glb`)** |
| Texturen | **eingebettet**, keine Nebendateien |
| Maßstab | real, in **Metern** |
| Achsen | Y oben, Z nach vorn (glTF-Standard) |
| Ursprung | Fahrzeugmitte auf Bodenhöhe |
| Dreiecke | Richtwert **unter 50 000** |
| Animationen | keine nötig |

**Die eine Anforderung, an der es steht oder fällt** — und sie ist inzwischen
gebaut und geprüft, nicht bloß gefordert:

> **Je bewegliches Teil eine glTF-Animation**, benannt `garage`, `door`,
> `step` bzw. `awning`. Sie läuft vom geschlossenen (Anfang) zum offenen Ende.

Kehler OS spielt sie **nicht ab**, sondern setzt die Stelle darin: Bei einem
halb geöffneten Tor steht die Animation in der Mitte. Den Weg, den Drehpunkt
und das Tempo bestimmt damit das Modell — geraten wird nichts. Eine Konvention
wie „das Teil heißt Tor, also dreht es sich schon um die richtige Achse" wäre
genau die Art Annahme, die dieses Projekt nicht trifft.

Ein Modell ohne solche Animationen wird **nicht verwendet**: Es kann keine
Zustände zeigen, und dann wäre es hübscher als das jetzige und nutzloser — das
Fahrzeug im Dashboard ist eine Zustandsanzeige und kein Bild. Die Oberfläche
bleibt in dem Fall bei der Code-Darstellung und schreibt den Grund ins
Diagnoseprotokoll des Browsers. Fehlt nur *ein* Teil, wird das Modell benutzt
und das fehlende Teil namentlich gemeldet.

**Wohin die Datei kommt:** `config/vehicle/model.glb`. Sie wird nicht
versioniert — sie gehört zum Fahrzeug, wie die Hardwareadressen. Liegt keine
da, greift die Code-Darstellung; das ist kein Fehlzustand.

**Geprüft am 2026-08-11** mit einem eigens erzeugten Testmodell
(`tools/model/make_test_glb.py`): Datei wird geladen, drei Teile bewegen sich,
das absichtlich fehlende vierte wird als fehlend gemeldet.

`.glb` deshalb, weil three.js es ohne Umwege lädt und weil eine einzelne Datei
mit eingebetteten Texturen zur Regel passt, dass ohne Internet nichts fehlen
darf (Kapitel 17 §107). `.fbx`, `.obj`, `.step` und `.blend` sind
Austauschformate der Konstruktion, nicht der Darstellung — sie müssten ohnehin
zuerst nach glTF gewandelt werden.

**Zu bedenken:** Ein geliefertes Modell hebt zwei Zusagen aus ADR 0008 auf.
Die Maße stünden dann nicht mehr an einer lesbaren Stelle, und im Repository
läge ein Binärartefakt, das ohne 3D-Programm niemand mehr ändern kann. Das
kann sich lohnen — aber es ist eine Entscheidung und kein reiner Zugewinn.

---

## Zusammenfassung nach Dringlichkeit

**Für die erste reale Inbetriebnahme (Phase 9) zwingend:**
A2 Netzwerkparameter · A3 Mapping der zuerst angebundenen Funktion ·
A5 vorhandene Sicherheitsverriegelungen · I3 Netztrennung

*(A1 und I1 sind geklärt.)*

**Danach, für den sinnvollen Alltagsbetrieb:**
B1 Cerbo-Schnittstelle · C1 Tanksensorik ·
E1/E3 Garagen- und Verriegelungsrückmeldungen · I4 Display

**Zuletzt und bewusst nicht zuerst:**
D1/D2 Nivellierung und Hydraulik

**Alles Übrige** läuft simuliert weiter und blockiert die Entwicklung nicht.
