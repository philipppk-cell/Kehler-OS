# Fahrzeugreferenz

Grundlage für die dreidimensionale Fahrzeugdarstellung im Dashboard.

> **Die Originalfotos liegen nicht im Repository.** Sie wurden im Chat
> übermittelt und ließen sich von dort nicht als Datei ablegen. Diese Datei
> hält fest, **was auf ihnen zu sehen ist**, damit das Modell später ohne die
> Bilder nachvollziehbar und korrigierbar bleibt. Wenn die Fotos verfügbar
> gemacht werden, gehören sie in dieses Verzeichnis.

## Quelle

Sechs Fotos des realen Fahrzeugs (2026-08-09):

1. Front, leicht schräg, Fahrerhaus
2. Rechte Seite (Einstiegsseite), Gegenlicht
3. Heck, frontal — **Heckklappe geschlossen**
4. Linke Seite (Fahrerseite), nahezu orthografisch — **die beste Grundlage
   für die Proportionen**
5. Drohnenaufnahme schräg von oben, linke Seite und Dach
6. Drohnenaufnahme am Stellplatz mit Umgebung, **Heckklappe geöffnet** —
   maßgeblich für Farbe und Heckmechanik

> **Warum Bild 6 zwei Fehler korrigiert hat.** Die Bilder 1–5 entstanden alle
> in praller Sonne oder im Gegenlicht. Dort wirkt der Lack weiß, und die
> waagerechte Fuge in der Heckwand liest sich wie die Mittelteilung zweier
> Flügeltüren. Erst die Aufnahme mit Umgebung zeigt beides richtig: einen
> grauen Lack und eine Klappe, die nach oben hebt.
>
> Lehre für spätere Nachbildungen: **Fotos ohne Bezugspunkt in der Umgebung
> taugen nicht zur Farbbestimmung.**

## Fahrzeug

**MAN TGX, Fahrerhaus weiß, 6×2-Fahrgestell mit Kofferaufbau.**

| Merkmal | Beobachtung |
| --- | --- |
| Achsen | Vorderachse einzelbereift, hinten Tandem, beide Hinterachsen doppelbereift |
| Fahrerhaus | Fernverkehrskabine mit Dachspoiler und Seitenleitblechen, Außenspiegel klassisch (kein Kamerasystem) |
| Aufbau | glatter Kofferaufbau, deutlich höher als das Fahrerhaus, keine Alkovenausformung über der Kabine |
| Aufbaufront | senkrecht, obere Vorderkante **abgeschrägt** (nicht gerundet) |
| Heck | leichte Dachkantenauskragung, senkrechte Heckwand |
| Farbe | Fahrerhaus und Aufbau **mittelgrau mit leichtem Blaustich**, hochglänzend. Auf den Sonnenaufnahmen wirkt der Lack ausgebrannt hell bis weiß — die Aufnahme mit Umgebung zeigt die tatsächliche Farbe. |
| Unterbau | durchgehendes Staukastenband beidseitig, zwischen den Rädern abgesenkt, über dem Tandem flach hochgezogen |

## Aufbaufunktionen

| Funktion | Beobachtung |
| --- | --- |
| **Garage** | über **eine oben angeschlagene Heckklappe**, die nach oben hebt und geöffnet waagerecht wie ein Vordach absteht. Nahezu volle Höhe und Breite der Heckwand. **Kein Rolltor, keine Flügeltüren.** |
| **Eingangstür** | auf der **rechten Seite** (Einstiegsseite), im vorderen Drittel, nahezu volle Aufbauhöhe, mit Fenster im oberen Bereich |
| **Markise** | Kassette auf der **rechten Dachkante**, dunkel, über nahezu die gesamte Aufbaulänge |
| **Solar** | Dach vollflächig belegt, **zwei Reihen zu je fünf Modulen** |
| **Fenster** | links vier (drei breite, ein kleines quadratisch); rechts zwei breite plus das Türfenster. Kräftige dunkle Rahmen mit deutlich gerundeten Ecken, im **mittleren Drittel** der Aufbauhöhe — nicht direkt unter dem Dach. |
| Heckleuchten | mehrere runde Einzelleuchten in den oberen und unteren Heckecken |

## Maße

**Angegeben (2026-08-09):** Gesamtlänge **11,5 m**, Gesamthöhe **4,0 m**.

Aus Fotos lassen sich darüber hinaus Proportionen ablesen, aber keine Maße.
Damit fehlen weiterhin:

- Gesamtbreite (im Modell mit 2,55 m angesetzt — das zulässige Höchstmaß)
- Radstand und Achsabstand des Tandems
- Überhang vorn und hinten
- Höhe des Wohnbodens über Grund
- Reifengröße

Diese Angaben sind als **Punkt K1** in
[`OPEN_HARDWARE_REQUIREMENTS.md`](../../OPEN_HARDWARE_REQUIREMENTS.md)
aufgenommen. Für die Maßtabelle in `frontend/src/vehicle3d/dimensions.ts`
gilt: Jeder Wert ist dort einzeln als `ANGEGEBEN` oder `GESCHÄTZT`
gekennzeichnet. Sie steht bewusst an genau einer Stelle, damit die Korrektur
ein Zahlenaustausch ist und keine Modellüberarbeitung.

**Weitere Fotos ändern daran nichts** — auch nicht viele. Sie verbessern die
Form (Fensterlagen, Türgröße, Verlauf des Staukastenbandes), liefern aber
keine Meter, solange kein Maßstab mit im Bild liegt. Was Fotos leisten, was
sie nicht leisten und warum ein fotogrammetrischer Scan hier das falsche
Modell wäre, steht als **Punkt K3** in derselben Datei.

## Bewusst nicht modelliert

- **Kennzeichen.** Es ist auf den Fotos lesbar, hat im Dashboard aber keinen
  Informationswert und wäre nur ein personenbezogenes Detail auf einem
  Bildschirm, der auch Gästen gezeigt wird.
- **Herstellerschriftzüge und Embleme.** Dekoration ohne Zustandsbezug
  (Kapitel 18 §34).
- **Umgebung.** Kein Gras, kein Himmel, keine Nachbarfahrzeuge. Das Dashboard
  zeigt das Fahrzeug, nicht den Stellplatz.
