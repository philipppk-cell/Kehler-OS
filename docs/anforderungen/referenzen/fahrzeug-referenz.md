# Fahrzeugreferenz

Grundlage für die dreidimensionale Fahrzeugdarstellung im Dashboard.

> **Die Originalfotos liegen nicht im Repository.** Sie wurden im Chat
> übermittelt und ließen sich von dort nicht als Datei ablegen. Diese Datei
> hält fest, **was auf ihnen zu sehen ist**, damit das Modell später ohne die
> Bilder nachvollziehbar und korrigierbar bleibt. Wenn die Fotos verfügbar
> gemacht werden, gehören sie in dieses Verzeichnis.

## Quelle

Fünf Fotos des realen Fahrzeugs (2026-08-09):

1. Front, leicht schräg, Fahrerhaus
2. Rechte Seite (Einstiegsseite), Gegenlicht
3. Heck, frontal
4. Linke Seite (Fahrerseite), nahezu orthografisch — **die beste Grundlage
   für die Proportionen**
5. Drohnenaufnahme schräg von oben, linke Seite und Dach

## Fahrzeug

**MAN TGX, Fahrerhaus weiß, 6×2-Fahrgestell mit Kofferaufbau.**

| Merkmal | Beobachtung |
| --- | --- |
| Achsen | Vorderachse einzelbereift, hinten Tandem, beide Hinterachsen doppelbereift |
| Fahrerhaus | Fernverkehrskabine mit Dachspoiler und Seitenleitblechen, Außenspiegel klassisch (kein Kamerasystem) |
| Aufbau | glatter Kofferaufbau, deutlich höher als das Fahrerhaus, keine Alkovenausformung über der Kabine |
| Aufbaufront | senkrecht, obere Vorderkante großzügig gerundet |
| Heck | leichte Dachkantenauskragung, senkrechte Heckwand |
| Farbe | Fahrerhaus und Aufbau hellgrau/weiß, hochglänzend |
| Unterbau | durchgehendes Staukastenband beidseitig, zwischen den Rädern abgesenkt, über dem Tandem flach hochgezogen |

## Aufbaufunktionen

| Funktion | Beobachtung |
| --- | --- |
| **Garage** | über **zwei Flügeltüren am Heck**, außen angeschlagen, nahezu volle Höhe und Breite der Heckwand. **Kein Rolltor.** |
| **Eingangstür** | auf der **rechten Seite** (Einstiegsseite), im vorderen Drittel, nahezu volle Aufbauhöhe, mit Fenster im oberen Bereich |
| **Markise** | Kassette auf der **rechten Dachkante**, dunkel, über nahezu die gesamte Aufbaulänge |
| **Solar** | Dach vollflächig belegt, **zwei Reihen zu je fünf Modulen** |
| **Fenster** | links vier (drei breite, ein kleines quadratisch); rechts zwei breite plus das Türfenster |
| Heckleuchten | mehrere runde Einzelleuchten in den oberen und unteren Heckecken |

## Maße

**Angegeben (2026-08-09):** Gesamtlänge **11,5 m**, Gesamthöhe **4,0 m**.

Aus Fotos lassen sich darüber hinaus Proportionen ablesen, aber keine Maße.
Damit fehlen weiterhin:

- Gesamtbreite (im Modell mit 2,55 m angesetzt — das zulässige Höchstmaß)
- Radstand und Achsabstand des Tandems
- Überhang vorn und hinten
- Höhe des Wohnbodens über Grund

Diese Angaben sind als **Punkt K1** in
[`OPEN_HARDWARE_REQUIREMENTS.md`](../../OPEN_HARDWARE_REQUIREMENTS.md)
aufgenommen. Für die Maßtabelle in `frontend/src/vehicle3d/dimensions.ts`
gilt: Jeder Wert ist dort einzeln als `ANGEGEBEN` oder `GESCHÄTZT`
gekennzeichnet. Sie steht bewusst an genau einer Stelle, damit die Korrektur
ein Zahlenaustausch ist und keine Modellüberarbeitung.

## Bewusst nicht modelliert

- **Kennzeichen.** Es ist auf den Fotos lesbar, hat im Dashboard aber keinen
  Informationswert und wäre nur ein personenbezogenes Detail auf einem
  Bildschirm, der auch Gästen gezeigt wird.
- **Herstellerschriftzüge und Embleme.** Dekoration ohne Zustandsbezug
  (Kapitel 18 §34).
- **Umgebung.** Kein Gras, kein Himmel, keine Nachbarfahrzeuge. Das Dashboard
  zeigt das Fahrzeug, nicht den Stellplatz.
