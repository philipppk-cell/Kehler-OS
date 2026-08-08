# ADR 0004 – Datenhaltung

**Status:** angenommen · Phase 1
**Bezug:** Kapitel 6, Kapitel 16 §63/§64, Kapitel 18 §55/§56

## Entscheidung

**Vier getrennte Ebenen:**

| Ebene | Technik |
| --- | --- |
| Live-Zustand | Arbeitsspeicher im Backend-Prozess |
| Konfiguration und Hardware-Mapping | YAML-Dateien unter `config/`, versioniert |
| Betriebsdaten | SQLite `kehleros.db` (WAL) |
| Historie und Zeitreihen | separate SQLite `history.db` (WAL) |

## Kontext

Kapitel 16 §64 verlangt ausdrücklich, keine Datenbank aus Gewohnheit oder
Popularität zu wählen, sondern anhand von Raspberry Pi, lokalem Betrieb,
Datenmenge, Zeitreihen, Backup, Wartbarkeit und Zuverlässigkeit.

## Abwägung

**SQLite — gewählt.**

- **Wartungsfrei.** Kein Serverprozess, kein Benutzer, keine Netzwerkkonfiguration,
  kein Tuning. Das ist auf einem Fahrzeugrechner, der jahrelang unbeaufsichtigt
  läuft, der wichtigste Einzelvorteil.
- **Backup ist Dateikopie.** Kapitel 16 §72–§75 verlangt sicherbare und
  zuverlässig wiederherstellbare Daten. Mit der Online-Backup-API entsteht eine
  konsistente Kopie im laufenden Betrieb, ohne das System anzuhalten.
- **Abstürzsicher.** Mit WAL-Journal und `synchronous=FULL` für die
  Konfigurationsdatenbank übersteht SQLite Stromausfälle sehr robust — die
  zentrale Anforderung aus Kapitel 17 §39.
- **Transaktional**, erfüllt damit die Forderung nach atomaren
  Konfigurationsänderungen (Kapitel 15 §77, Kapitel 16 §68).
- Ausreichend für die erwartete Last: einige hundert Datenpunkte, ein
  schreibender Prozess, wenige lesende Clients.

**PostgreSQL — verworfen.** Ein vollwertiger Serverprozess für eine
Einzelplatzinstallation. Mehr Speicher, mehr Startzeit, mehr
Konfigurationsfläche, mehr Ausfallwege — ohne einen Gewinn, der hier zum Tragen
käme. Kapitel 18 §4 warnt genau davor.

**InfluxDB / TimescaleDB — verworfen.** Spezialisierte Zeitreihen-Engines
lohnen ab Datenraten, die dieses Fahrzeug nicht erzeugt. Influx hat auf ARM
einen spürbaren Speicherbedarf; Timescale setzt Postgres voraus. Der Gewinn
rechtfertigt die zweite Datenbanktechnologie nicht.

**Zeitreihen in SQLite** werden stattdessen durch die Struktur gelöst:
Rohtabelle plus vorberechnete Rollup-Tabellen (Minute, Stunde), erzeugt von
einem Hintergrunddienst. Das ist die Aggregationsstrategie aus Kapitel 16 §9/§10
— und weil sie explizit ist, ist sie auch nachvollziehbar und testbar.

## Warum zwei Datenbankdateien

Kapitel 16 §88 verlangt, dass ein Ausfall der Historie die Fahrzeugsteuerung
nicht mitreißt. Mit getrennten Dateien ist das strukturell erfüllt: Wächst
`history.db` zu groß, wird beschädigt oder ist der Datenträger voll, bleiben
Benutzer, Berechtigungen, Automatisierungen und Konfiguration unberührt. Die
Oberfläche meldet dann „Historische Daten sind momentan nicht verfügbar. Die
Fahrzeugsteuerung funktioniert weiterhin.“ (Kapitel 16 §90)

Zusätzlich unterscheidet sich die Sicherungswürdigkeit erheblich: Konfiguration
und Benutzer sind unersetzlich, Messhistorie ist wertvoll, aber verzichtbar.
Getrennte Dateien erlauben getrennte Backup-Strategien (Kapitel 16 §73).

## Warum Konfiguration in YAML statt in der Datenbank

Kapitel 17 §48 verlangt die Trennung von Konfiguration und Code, Kapitel 17 §119
die Verständlichkeit für andere Entwickler, Kapitel 12 §58 ein zentrales
Hardware-Mapping.

YAML-Dateien sind lesbar, diffbar, versionierbar und **auch dann editierbar,
wenn das System nicht startet** — bei einem fehlerhaften Mapping ist genau das
der Fall. Eine Datenbank, die man nur über die Anwendung ändern kann, die wegen
der Konfiguration nicht startet, wäre eine vermeidbare Falle.

Jede Konfigurationsdatei wird beim Laden gegen ein Schema validiert; ungültige
Werte verhindern die Übernahme, statt das laufende System zu beschädigen
(Kapitel 15 §76).

## Migrationen

Schemaänderungen laufen über nummerierte, vorwärtsgerichtete Migrationsskripte
mit gespeichertem Versionsstand (Kapitel 16 §69/§71). Vor jeder Migration wird
automatisch eine Sicherung angelegt. Bestehende Benutzer, Automatisierungen und
Einstellungen bleiben erhalten (Kapitel 16 §70).

## Konsequenzen

- **Der Datenträger muss eine SSD sein, keine microSD-Karte** (offener Punkt I1).
  Dauerhafte Schreiblast einer Zeitreihendatenbank überlebt eine SD-Karte nicht
  dauerhaft.
- Nur ein Prozess schreibt. Das ist bei SQLite die saubere Betriebsart und
  passt zum Prozessmodell aus ADR 0007.
- Der Speicherverbrauch beider Dateien wird aktiv überwacht, mit Reserve für
  kritische Fehlerprotokolle (Kapitel 16 §79/§80).
