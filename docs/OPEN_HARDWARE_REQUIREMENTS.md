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

**Benötigte Antwort:**
- IP-Adresse des Cerbo GX
- Ist der lokale MQTT-Broker aktiviert? Mit oder ohne TLS/Authentifizierung?
- VRM-Portal-ID (Bestandteil aller MQTT-Topics)

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
(`heating.target` neben `climate.cooling.target`). Ein gemeinsamer Sollwert
wäre die aufgeräumtere Oberfläche und die falsche Anlage — das Verstellen der
Heizung würde stillschweigend die Klimaanlage mitverstellen.

Gemeinsam bleibt allein die **gemessene** Innentemperatur: Es gibt einen
Wohnraum und einen Fühler (`climate.living.temperature`). Beide Bereiche
zeigen denselben Messwert, weil es derselbe ist.

### G1 · Heiz-/Klimageräte — `OFFEN` · `BLOCKIEREND` für reale Steuerung

*Der Fahrzeughalter hat die Geräteinformationen angekündigt (2026-08-10).*

- Hersteller und Modell von Heizung, Klimaanlage, Lüftung
- Schnittstelle (potentialfreier Kontakt, Bus, proprietär)
- **Besitzt das Gerät eine eigene Regelung?** (Kapitel 12 §67 / Kapitel 18 §29 —
  vorhandene Regelintelligenz soll nicht nachgebaut werden)
- ist ein Sollwert vorgebbar oder nur Ein/Aus?
- **Stellbereich und Schrittweite** je Gerät

**Vorläufig hinterlegt** (`config/vehicle/vehicle.yaml`, als `VORLÄUFIG`
markiert): Klima 16–30 °C, Heizung 5–30 °C, Schrittweite 0,5 K. Anders als bei
der Strombegrenzung (Punkt B1) ist ein falscher Bereich hier ungefährlich —
eine Solltemperatur kann keine Zuleitung überlasten. Er wird trotzdem
korrigiert, sobald die Geräte bekannt sind.

**Was bis dahin bewusst fehlt:** Betriebsarten, ein „heizt gerade"-Zustand und
Warmwasser. Alles drei setzt voraus, dass das Gerät es meldet — nachgebaut
wird keine Regelung.

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

### I3 · Netzwerk — `OFFEN` · `BLOCKIEREND` für den Produktivbetrieb

> **Durch die Entscheidung in A1 aufgewertet.** Da die S7-Kommunikation
> unverschlüsselt ist, trägt die Netztrennung die Sicherheit (Kapitel 15 §47).

- IP-Bereich des Fahrzeugnetzes
- Router-/Switch-/Access-Point-Modelle
- **Unterstützt der Switch VLANs?** Falls nein, brauchen wir eine andere
  Trennung — etwa eine zweite Netzwerkschnittstelle am Pi, an der die SPS
  allein hängt.

### I4 · Hauptdisplay — `OFFEN` · `BLOCKIEREND` für finales Layout

- Modell, Auflösung, physische Größe, Seitenverhältnis
- Anschluss (HDMI/DSI) und Touch-Anbindung (USB/I²C)
- Ist die Helligkeit softwareseitig steuerbar (Kapitel 7 §26)?

> Bis zur Klärung wird das Layout auf dem Seitenverhältnis der Designreferenz
> entwickelt und responsiv gehalten.

### I5 · Zeitbasis ohne Internet — `OFFEN` · `NICHT BLOCKIEREND`

Besitzt der Pi eine gepufferte Echtzeituhr (RTC-Modul)? Ohne RTC und ohne
Internet ist nach einem Stromausfall keine korrekte Zeit verfügbar, was die
Historie beeinträchtigt (Kapitel 16 §85).

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
