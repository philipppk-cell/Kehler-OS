# Kehler OS – Daten-, Command- und Eventmodell

Stand: Phase 1
Bezug: Kapitel 5 §13/§14, Kapitel 6, Kapitel 10 §9/§39/§40, Kapitel 13, Kapitel 18 §35/§44

Dieses Dokument legt die Begriffe fest, mit denen das gesamte System arbeitet.
Sie gelten identisch in Backend, API, Automatisierung und Oberfläche.

---

## 1. Namenskonvention

### Entity-IDs

```
<domain>.<gruppe>.<name>
```

Kleinbuchstaben, `snake_case` innerhalb eines Segments, Punkt als Trenner.

| Domäne | Zweck | Beispiele |
| --- | --- | --- |
| `energy` | Energiesystem | `energy.battery.main`, `energy.solar.array`, `energy.shore_power` |
| `water` | Wassersystem | `water.tank.fresh`, `water.tank.grey`, `water.tank.black`, `water.pump.main` |
| `climate` | Klima | `climate.zone.living`, `climate.heater.main`, `climate.vent.roof` |
| `light` | Beleuchtung | `light.interior.living`, `light.exterior.entry`, `light.garage.main` |
| `vehicle` | Aufbaufunktionen | `vehicle.door.main`, `vehicle.garage.door`, `vehicle.step.entry`, `vehicle.awning.main`, `vehicle.lock.central` |
| `leveling` | Nivellierung | `leveling.jack.front_left`, `leveling.tilt.pitch`, `leveling.tilt.roll` |
| `camera` | Kameras | `camera.rear`, `camera.garage` |
| `network` | Netzwerk und Verbindungen | `network.plc`, `network.victron`, `network.internet` |
| `system` | Plattform | `system.cpu`, `system.storage`, `system.temperature` |

**Attribute** eines Entity werden angehängt, wenn ein einzelner Datenpunkt
gemeint ist (Historie, Automatisierungsbedingung):

```
water.tank.fresh.level
energy.battery.main.soc
climate.zone.living.temperature
```

Verboten in allen Schichten oberhalb der Adapter: Hardwarereferenzen jeder Art.

### Commands

```
<entity_id>.<verb>
```

Verben im Infinitiv, immer explizit statt umschaltend:

```
light.interior.living.set_state       params: { state: "ON" }
vehicle.garage.door.open
vehicle.garage.door.stop
climate.zone.living.set_target        params: { celsius: 21.5 }
```

Kein `toggle`. Begründung: Toggle setzt einen sicher bekannten Ausgangszustand
voraus, den es bei `UNKNOWN` gerade nicht gibt (Kapitel 13 §33/§34).

### Events

```
<entity_id>.<ereignis_im_perfekt>
```

```
vehicle.garage.door.opened
vehicle.door.main.closed
energy.shore_power.connected
water.tank.grey.threshold_exceeded
system.service.failed
```

Ein Event beschreibt **einen Zeitpunkt**, ein State **die Gegenwart**. Die
beiden werden nie vermischt (Kapitel 13 §45).

---

## 2. Zustandswert

Jeder Wert im State Store trägt Kontext, nicht nur eine Zahl.

| Feld | Typ | Bedeutung |
| --- | --- | --- |
| `value` | beliebig | der Wert; `null` wenn `quality` nicht `VALID` ist |
| `unit` | Text | interne Einheit, unabhängig von der Anzeige (Kapitel 6 §6) |
| `quality` | Aufzählung | siehe unten |
| `source` | Aufzählung | woher der Wert stammt |
| `measured_at` | Zeitpunkt | Messzeit der Hardware |
| `received_at` | Zeitpunkt | Systemzeit des Eintreffens |
| `seq` | Ganzzahl | monoton je Entity, für die Reihenfolgesicherung |

### Qualität

| Wert | Bedeutung |
| --- | --- |
| `VALID` | aktueller, plausibler Messwert |
| `STALE` | war gültig, aber länger nicht aktualisiert als erwartet |
| `UNKNOWN` | Zustand derzeit nicht bekannt |
| `INVALID` | Wert vorhanden, aber außerhalb des zulässigen Bereichs |
| `ERROR` | Sensor oder Kanal meldet einen Fehler |

**`UNKNOWN` ist niemals `0`, `OFF` oder `CLOSED`.** Ein unerreichbarer
Tanksensor bedeutet nicht „Tank leer“ (Kapitel 5 §19, Kapitel 18 §38).

Für jeden Datenpunkt ist ein erwartetes Aktualisierungsintervall konfiguriert.
Bleibt die Aktualisierung aus, wechselt die Qualität automatisch — der Wert
altert sichtbar, statt still falsch zu werden.

### Quelle

`PLC` · `VICTRON` · `SENSOR` · `KEHLER_OS` · `USER` · `AUTOMATION` · `SIMULATION`

`KEHLER_OS` kennzeichnet berechnete Werte (Autarkiegrad, Trends,
Restreichweite). Sie dürfen nie als direkte Messwerte erscheinen
(Kapitel 13 §38/§39). Prognosen werden zusätzlich als `PREDICTED` statt
`MEASURED` markiert (Kapitel 16 §100).

---

## 3. Entity

```
Entity
├── id              vehicle.garage.door
├── domain          vehicle
├── name_key        i18n-Schlüssel, kein fester Anzeigetext
├── device_id       Verweis auf das physische Gerät
├── capabilities    [ open, close, stop ]
├── actual_state    Zustandswert (aus der Hardware)
├── requested_state Wunschzustand (aus dem letzten Befehl), optional
├── attributes      weitere Zustandswerte
└── config_ref      Verweis in die Fahrzeugkonfiguration
```

**Capabilities steuern die Oberfläche.** Fehlt `set_brightness`, existiert kein
Dimmregler — nicht ausgegraut, sondern gar nicht (Kapitel 12 §55, Kapitel 13 §60).

**Konfiguration, Capability und Zustand bleiben getrennt** (Kapitel 13 §58/§59):
Kapazität 500 L ist Konfiguration, `open/close/stop` sind Capabilities, 320 L
ist Zustand.

---

## 4. Zustandsmaschinen

Bewegliche Geräte werden als Zustandsmaschine mit erlaubten Übergängen
beschrieben. Beispiel Garagentor:

```
CLOSED ──open──▶ OPENING ──▶ OPEN
                    │
                    ├─stop──▶ STOPPED
                    └────────▶ BLOCKED / ERROR

OPEN ──close──▶ CLOSING ──▶ CLOSED
UNKNOWN ──(Rückmeldung)──▶ konkreter Zustand
```

Welche Zustände tatsächlich existieren, **bestimmt die Hardware**: Ohne
Endlagenrückmeldung gibt es kein belastbares `OPENING`, und das System zeigt
`UNKNOWN` statt einer erfundenen Bewegung (Kapitel 13 §6, Kapitel 18 §32/§106).

Aggregierte Zustände fassen mehrere Entities zusammen:

```
vehicle.lock.summary  →  ALL_LOCKED | PARTIALLY_LOCKED | UNLOCKED | UNKNOWN
system.health         →  HEALTHY | DEGRADED | WARNING | CRITICAL
```

Ein einziges `UNKNOWN` unter den Bestandteilen führt niemals zu einem
zuversichtlichen Gesamtergebnis (Kapitel 14 §23).

---

## 5. Command

```
Command
├── id              eindeutig, für die Zuordnung der Rückmeldung
├── correlation_id  verbindet API-Aufruf, Adapter, Zustandsänderung, Log
├── entity_id       vehicle.garage.door
├── verb            open
├── params          { }
├── trigger         USER | AUTOMATION | SYSTEM | AI
├── actor           Benutzer- oder Automatisierungskennung
├── client          Gerätekennung des auslösenden Clients
├── requested_at    Zeitpunkt
├── phase           siehe unten
└── result          Ergebnis mit Begründung
```

### Phasen

```
REQUESTED → VALIDATING → SENT → ACKNOWLEDGED → COMPLETED
                 │         │          │
                 │         │          └──▶ TIMEOUT
                 │         └─────────────▶ FAILED
                 └───────────────────────▶ REJECTED
```

`REJECTED` entsteht vor jedem Hardwarekontakt: fehlende Berechtigung,
unbekanntes Gerät, fehlende Capability, ungültiger Parameter, unzulässiger
Zustandsübergang, laufende Bewegung, verletzte Sicherheitsbedingung.

**Ein Command schreibt niemals in den State Store.** Nur eine bestätigte
Rückmeldung der Hardware tut das (Kapitel 12 §67, Kapitel 18 §37).

Befehle je Entity werden serialisiert: Solange eine Bewegung läuft, wird ein
zweiter Fahrbefehl abgewiesen statt überlagert (Kapitel 13 §21).

---

## 6. Event

```
Event
├── id
├── type            vehicle.garage.door.opened
├── entity_id
├── source          PLC | VICTRON | USER | AUTOMATION | SYSTEM | NETWORK | SENSOR
├── severity        INFO | NOTICE | WARNING | CRITICAL
├── occurred_at     Ereigniszeit
├── recorded_at     Systemzeit
├── correlation_id
└── data            vorheriger Wert, neuer Wert, Kontext
```

Ereignisse entstehen aus echten Änderungen, nicht aus wiederholten gleichen
Messungen: Ein 60 Sekunden geschlossener Türkontakt erzeugt ein Event, nicht
sechzig (Kapitel 13 §65).

---

## 7. Alert

```
Alert
├── id
├── type            water.tank.grey.level_high
├── entity_id
├── severity        INFO | NOTICE | WARNING | CRITICAL
├── state           ACTIVE | ACKNOWLEDGED | RESOLVED
├── raised_at / acknowledged_at / resolved_at
├── acknowledged_by
├── message_key     i18n-Schlüssel
└── params          Werte für die Meldung
```

**Quittieren ist nicht Beheben.** Ein quittierter Alarm bleibt technisch aktiv,
solange die Ursache besteht (Kapitel 13 §44).

**Hysterese ist Pflicht** bei analogen Schwellen: Auslösen bei Unterschreiten
der Warnschwelle, Zurücksetzen erst bei deutlichem Überschreiten — sonst
flattert die Warnung um den Grenzwert (Kapitel 14 §46/§47).

**Die Priorität kann vom Fahrzeugmodus abhängen.** `vehicle.garage.door = OPEN`
ist im Campingmodus möglicherweise normal und im Fahrmodus kritisch
(Kapitel 14 §36/§37).

---

## 8. Device

```
Device
├── id / name / kind          PLC | VICTRON | CAMERA | SENSOR_BUS | NETWORK
├── vendor / model / firmware
├── connection                Transport und Adresse (nur hier sichtbar)
├── link_state                ONLINE | DEGRADED | RECONNECTING | OFFLINE | INITIALIZING | ERROR | UNKNOWN
├── last_seen
├── error_count / reconnects
└── capabilities              was dieses Gerät bereitstellt
```

Ein Gerät ohne vollständige Konfiguration gilt als `NOT_CONFIGURED`, eines mit
unbekanntem Typ als `UNSUPPORTED`. In beiden Fällen werden keine Funktionen
erfunden (Kapitel 12 §68/§69).

---

## 9. Einheiten

Intern gelten feste Einheiten, unabhängig von der Anzeige:

| Größe | intern |
| --- | --- |
| Temperatur | °C |
| Volumen | Liter |
| Spannung / Strom / Leistung / Energie | V · A · W · Wh |
| Füllstand | Prozent **und** Liter, beide geführt |
| Winkel | Grad |
| Zeitstempel | UTC, monoton gespeichert |

Die Umrechnung für die Darstellung geschieht ausschließlich an einer zentralen
Stelle in der Oberfläche (Kapitel 7 §36). Zeitstempel werden in UTC gespeichert
und lokal dargestellt, damit ein Zeitzonenwechsel die Historie nicht
beschädigt (Kapitel 16 §83/§84).

---

## 10. Rückverfolgbarkeit

Jede zustandsverändernde Aktion beantwortet fünf Fragen (Kapitel 13 §72,
Kapitel 15 §52):

```
Wer      actor + client
Was      entity_id + verb + params
Wann     requested_at / occurred_at
Warum    trigger (USER, AUTOMATION, SYSTEM, AI) + Regel-ID
Ergebnis phase + result
```

Verknüpft über die `correlation_id` ergibt das eine durchgehende Kette von der
Berührung des Displays bis zur Hardwarequittung.
