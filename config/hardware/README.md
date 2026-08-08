# Hardwarekonfiguration

Hier liegt die **einzige** Stelle im gesamten Projekt, an der Hardwareadressen
und Transportdetails stehen (Kapitel 12 §57/§58).

Wird ein Sensor auf einen anderen Eingang umgeklemmt, ändert sich genau eine
Zeile in `mapping.yaml` — kein Programmcode, keine Oberfläche, keine
Automatisierung.

## Dateien

| Datei | Inhalt |
| --- | --- |
| `devices.yaml` | physische Geräte und ihre Verbindung |
| `mapping.yaml` | Zuordnung logischer Kehler-OS-IDs zu Hardwarereferenzen |
| `calibration.yaml` | Kennlinien, insbesondere Tankkalibrierung |

Die mitgelieferten `*.example.yaml` sind **Schemabeispiele**. Sie enthalten
bewusst keine echten Adressen, IPs oder Kapazitäten (Kapitel 18 §97).

## Vorgehen

1. Die offenen Punkte in [`../../docs/OPEN_HARDWARE_REQUIREMENTS.md`](../../docs/OPEN_HARDWARE_REQUIREMENTS.md) klären
2. `*.example.yaml` nach `*.yaml` kopieren und ausfüllen
3. Kehler OS validiert beim Start gegen das Schema

## Verhalten bei fehlender Konfiguration

Ein Eintrag ohne vollständige Hardwarereferenz gilt als `NOT_CONFIGURED`. Das
zugehörige Gerät erscheint in der Oberfläche als „Nicht konfiguriert“ — es wird
kein Zustand erfunden und kein Bedienelement angeboten
(Kapitel 12 §68/§69, Kapitel 18 §101).

Solange keine `mapping.yaml` existiert, läuft das System ausschließlich
simuliert.
