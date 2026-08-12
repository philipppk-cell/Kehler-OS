# Fahrzeugmodell — Spezifikation für die Anfertigung

Diese Seite ist zum **Weitergeben an den Auftragnehmer** gedacht. Sie enthält
alles, was zur Anfertigung nötig ist, und nichts darüber hinaus.

---

## 1. Wozu das Modell dient

Das Modell wird **nicht gerendert und nicht animiert abgespielt**. Es ist die
Bedienoberfläche eines Fahrzeugrechners: Auf dem Dashboard steht das Fahrzeug
dreidimensional, und **es zeigt durch seine Stellung an, was gerade offen
ist** — Heckklappe, Eingangstür, Trittstufe, Markise.

Daraus folgt die wichtigste Eigenschaft, und sie ist unüblich:

> **Der Wert des Modells liegt in seiner Beweglichkeit, nicht in seinem
> Aussehen.** Ein fotorealistisches Fahrzeug, dessen Heckklappe sich nicht
> öffnen lässt, ist für diesen Zweck unbrauchbar. Ein einfaches Fahrzeug mit
> vier korrekt beweglichen Teilen erfüllt den Zweck vollständig.

Bitte den Aufwand entsprechend verteilen. Abschnitt 7 sagt ausdrücklich, wofür
**keine** Zeit aufgewendet werden soll.

---

## 2. Lieferformat

| Anforderung | Wert |
| --- | --- |
| Format | **glTF 2.0 binär (`.glb`)** |
| Dateien | **genau eine.** Texturen eingebettet, keine Nebendateien |
| Maßstab | real, in **Metern** |
| Dreiecke | **unter 50 000** für das gesamte Fahrzeug |
| Texturen | eingebettet, höchstens 2048 px; 1024 px genügen in aller Regel |
| Material | glTF-PBR (Metallic-Roughness). Keine Sonderformate, keine Erweiterungen |

`.glb` deshalb, weil die Oberfläche es ohne Umwege lädt und weil eine einzelne
Datei zur Regel passt, dass ohne Internetverbindung nichts fehlen darf.
`.fbx`, `.obj`, `.step` und `.blend` sind Konstruktionsformate — sie müssten
ohnehin zuerst gewandelt werden und sind deshalb nicht die Lieferform.

**Zum Dreiecksbudget:** Das Ziel ist ein Raspberry Pi 5. Er hat keine
dedizierte Grafikkarte, und das Fahrzeug ist nur eines von mehreren Elementen
auf der Seite. 50 000 Dreiecke sind keine willkürliche Zahl, sondern die
Grenze, unterhalb derer die Anzeige flüssig bleibt. Ein aus einem Scan
erzeugtes Netz liegt typisch bei mehreren Millionen und muss daher neu
aufgebaut, nicht nur dezimiert werden.

---

## 3. Koordinaten, Ausrichtung, Ursprung

**Die Datei wird beim Laden nicht gedreht und nicht verschoben.** Sie wird so
angezeigt, wie sie ankommt. Eine falsche Achslage bedeutet deshalb ein
Fahrzeug, das im Dashboard quer steht — bitte hier besonders genau sein.

```
                    Y  (oben)
                    │
                    │
                    │        ┌──────────────────────────┐
                    │        │        Wohnaufbau        │
             ┌──────┴──┐     │                          │
             │Fahrerhaus│    │                          │
   ──────────┴─────────┴─────┴──────────────────────────┴──────►  X
            −X                                          +X
          (vorn)              ●  Ursprung             (hinten)
                          X=0, Y=0, Z=0

   Z zeigt zur RECHTEN Fahrzeugseite —
   das ist die Seite mit Eingangstür, Trittstufe und Markise.
```

| Achse | Bedeutung |
| --- | --- |
| **X** | Fahrzeuglängsachse. **Fahrzeugfront bei −X**, Heck bei +X |
| **Y** | oben. **Y = 0 ist die Fahrbahn** (Reifenunterkante) |
| **Z** | Fahrzeugquerachse. **+Z ist die rechte Seite** (Tür, Stufe, Markise) |

**Ursprung:** Fahrzeugmitte in Länge und Breite, auf Fahrbahnhöhe. Also: Das
Fahrzeug reicht von etwa X = −5,75 bis X = +5,75, von Y = 0 bis Y = 4,0 und
von Z = −1,275 bis Z = +1,275.

Einheit in der Exportdatei: **Meter** (in Blender: Szeneneinheit Meter,
Maßstab 1,0, „Apply Transform" beim glTF-Export aktiviert).

---

## 4. Die vier beweglichen Teile — daran entscheidet sich der Auftrag

Das Fahrzeug braucht **vier Animationen**. Sie sind der eigentliche
Liefergegenstand.

| Animationsname | Teil |
| --- | --- |
| `garage` | Die **zwei Heckflügeltüren** der Heckgarage, außen angeschlagen |
| `door` | Die **Eingangstür** auf der rechten Seite |
| `step` | Die **Einstiegsstufe** unter der Eingangstür (fährt aus) |
| `awning` | Das **Markisentuch** an der rechten Dachkante (fährt aus) |

### Wie die Animationen aufgebaut sein müssen

1. **Genau eine Animation je Teil**, benannt exakt wie oben —
   kleingeschrieben, ohne Zusätze wie `garage_open` oder `Action.001`.
2. Sie läuft **vom geschlossenen Zustand (Anfang) zum offenen Zustand
   (Ende)**. Länge beliebig; sie bestimmt zugleich, wie schnell sich das Teil
   in der Anzeige bewegt. 1 bis 3 Sekunden sind sinnvoll.
3. **Jede Animation bewegt ausschließlich ihr eigenes Teil.** Keine
   gemeinsamen Spuren, keine Kamerabewegung, keine Bewegung des Fahrzeugs.
4. Bei `garage` gehören **beide Flügeltüren in dieselbe Animation** — sie sind
   ein Zustand, nicht zwei.
5. Bei `awning` bleibt die **Kassette am Fahrzeug stehen**; sie ist
   festverschraubt. Nur das Tuch mit dem Ausfallprofil fährt aus.

### Warum genau so

Die Oberfläche **spielt diese Animationen nicht ab.** Sie setzt die Stelle
darin: Meldet die Sensorik eine halb geöffnete Heckklappe, steht die
`garage`-Animation in der Mitte. Damit bestimmt der Modellbauer Drehpunkt,
Richtung, Weg und Tempo — und nichts davon muss von der Software geraten
werden.

**Daraus folgt eine Anforderung an die Zwischenbilder:** Die Bewegung muss auf
*jeder* Position sinnvoll aussehen, nicht nur am Anfang und am Ende. Ein
Umschalten kurz vor Schluss („snap") ist unbrauchbar. Lineare oder sanft
ein-/ausschwingende Interpolation über die ganze Länge.

### Wenn eine Animation fehlt

Fehlt **eine einzelne**, wird das Modell verwendet und das betroffene Teil
steht still; die Software meldet es namentlich. Fehlen **alle vier**, wird das
Modell **nicht verwendet** — es könnte dann keinen Zustand anzeigen, und genau
dafür ist es da.

---

## 5. Was sonst am Fahrzeug erkennbar sein soll

Ohne eigene Beweglichkeit, aber für das Wiedererkennen:

* Fahrerhaus (MAN TGX, Fernverkehrsfahrerhaus) mit Dachspoiler, der zum
  höheren Aufbau überleitet
* Wohnaufbau mit **oben abgeschrägter Vorderkante** (nicht gerundet)
* Umlaufendes **Staukastenband** unterhalb des Wohnbodens
* **Solarfeld** auf dem Dach
* Seitenfenster (links vier, rechts zwei)
* Fahrgestell **6×2**: Vorderachse, dahinter ein Tandem aus zwei Hinterachsen,
  hinten zwillingsbereift

**Lackierung:** mittleres Grau mit leichtem Blaustich, Fahrerhaus und Aufbau
gleich lackiert. Auf Fotos in praller Sonne wirkt der Aufbau fast weiß — das
ist der Lichteindruck, nicht die Farbe.

---

## 6. Maße

**Nur zwei Maße sind bestätigt.** Alles Übrige stammt aus einer Auswertung von
Fotos und ist als Anhaltspunkt zu verstehen, nicht als Vorgabe:

| Maß | Wert | Grundlage |
| --- | --- | --- |
| Gesamtlänge | **11,50 m** | angegeben |
| Gesamthöhe | **4,00 m** | angegeben |
| Breite | 2,55 m | geschätzt (zulässiges Höchstmaß, passt zu den Fotos) |
| Radstand | 5,40 m | geschätzt |
| Hecküberhang | 3,25 m | geschätzt |
| Oberkante Fahrerhausdach | 2,98 m | geschätzt |
| Unterkante Wohnboden | 1,85 m | geschätzt |
| Eingangstür | 0,85 m breit, Unterkante 1,88 m | geschätzt |
| Heckgarage, Öffnung | 2,16 m breit, Unterkante 1,90 m | geschätzt |

**Der Auftragnehmer erhält das Fahrzeug in Fotos** (siehe Abschnitt 9). Wo die
Fotos etwas anderes zeigen als diese Tabelle, gelten die Fotos. Sollten sich
dabei belastbare Maße ergeben, bitte **mitliefern** — sie sind unabhängig vom
Modell für die Software von Wert.

---

## 7. Wofür ausdrücklich kein Aufwand entstehen soll

Das Fahrzeug wird auf einer Bedienoberfläche in Schrägansicht von vorn rechts
gezeigt, in etwa fahrzeuggroß auf dem Bildschirm, ohne Umgebung. Deshalb sind
die folgenden Dinge **nicht Teil des Auftrags** und sollen nicht berechnet
werden:

* **Innenraum** — er ist nie sichtbar
* **Motor, Fahrwerk, Unterboden** — die Ansicht geht nie unter die Fahrbahn
* **Fotorealismus**, gealterte Oberflächen, Schmutz, Kratzer
* **Beleuchtung, Umgebung, Boden, Schattenwurf** — stellt die Software selbst
* **Beschriftungen, Kennzeichen, Markenzeichen**
* **Schrauben, Scharniere, Zierleisten, Kleinteile** — sie kosten Dreiecke und
  sind in dieser Größe nicht erkennbar
* **Zusätzliche Animationen** über die vier genannten hinaus
* **Mehrere Detailstufen (LOD)** — eine genügt

---

## 8. Abnahme

Die Lieferung ist in Ordnung, wenn:

1. Die Datei ist **eine einzige `.glb`** und öffnet sich in einem
   glTF-Betrachter ohne Warnung.
2. Sie enthält **vier Animationen** mit genau den Namen `garage`, `door`,
   `step`, `awning`.
3. Jede Animation beginnt geschlossen, endet offen und sieht **auf halber
   Strecke** ebenfalls richtig aus.
4. Das Fahrzeug steht **auf Y = 0**, ist in **Metern** bemaßt, liegt mit der
   Länge auf **X** (Front bei −X) und hat die Eingangsseite bei **+Z**.
5. Das gesamte Modell bleibt **unter 50 000 Dreiecken**.

Die Prüfung auf der Zielanlage ist maschinell und dauert Sekunden: Die Datei
wird als `config/vehicle/model.glb` abgelegt, und die Software schreibt
anschließend in ihr Diagnoseprotokoll, was sie gefunden hat, zum Beispiel

```
Kehler OS · Fahrzeugmodell aus Datei (garage, door, step, awning)
```

Fehlt etwas, steht es dort namentlich. Es gibt also keine
Auslegungsdiskussion — das Ergebnis ist ablesbar.

---

## 9. Was der Auftragnehmer erhält

* Fotosatz des Fahrzeugs von allen Seiten, einschließlich Drohnenaufnahme
* Diese Spezifikation

**Bitte anfragen, falls nicht vorhanden:** Aufnahmen der vier beweglichen
Teile **in beiden Stellungen** — offen und geschlossen. Ohne sie sind
Drehpunkt und Weg nicht bestimmbar, und genau die sind der Kern des Auftrags.
