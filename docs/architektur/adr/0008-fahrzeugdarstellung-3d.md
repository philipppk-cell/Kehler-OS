# ADR 0008 – Dreidimensionale, drehbare Fahrzeugdarstellung

**Status:** angenommen · Phase 4
**Bezug:** Kapitel 8, Kapitel 17 §6/§93/§107–§111, Kapitel 18 §34/§104/§105/§106
**Ersetzt:** den Abschnitt „Fahrzeugvisualisierung" in
[ADR 0006](0006-frontend-stack.md)

## Entscheidung

**Das Fahrzeug wird im Dashboard als dreidimensionales Modell dargestellt und
lässt sich mit dem Finger frei drehen. Umsetzung mit three.js, Geometrie im
Code aus einer Maßtabelle erzeugt. Gerendert wird ausschließlich bei
Änderung. Ohne WebGL übernimmt die bisherige SVG-Seitenansicht.**

## Warum diese Entscheidung revidiert wurde

ADR 0006 hatte Inline-SVG gewählt und 3D ausdrücklich abgelehnt — mit zwei
Argumenten: Last auf dem Raspberry Pi und der Warnung vor dekorativem Overkill
aus Kapitel 18 §34.

**Der Fahrzeughalter hat die drehbare 3D-Ansicht ausdrücklich angefordert.**
Damit ist sie kein Schmuck mehr, sondern Anforderung: Ein Fahrzeug von 11,5 m
Länge hat vier Seiten, und die Aufbaufunktionen verteilen sich auf alle vier.
Die Garage liegt im Heck, die Eingangstür und die Markise rechts, das
Solarfeld auf dem Dach. Eine einzelne Seitenansicht kann höchstens die Hälfte
davon zeigen.

Das Leistungsargument bleibt gültig und wird technisch beantwortet statt
weggewogen — siehe unten.

## Umsetzung

### Rendern nur bei Änderung

**Das ist die tragende Entscheidung dieses ADR.** Es gibt keine
Renderschleife. Ein Bild wird angefordert, wenn

- ein Finger das Fahrzeug dreht,
- die Ansicht nach dem Loslassen ausläuft oder zurückkehrt,
- ein Zustandswechsel ein Bauteil bewegt,
- sich die Fläche ändert.

Ein Dashboard steht die meiste Zeit still. In dieser Zeit kostet die Ansicht
**nichts** — kein Bild, keine Grafiklast, keine Wärme. Eine übliche
`requestAnimationFrame`-Dauerschleife hätte dagegen 60 Bilder pro Sekunde
erzeugt, um immer dasselbe zu zeigen.

Weitere Maßnahmen: keine Schattenkarten (der Bodenschatten ist eine einmal
erzeugte Textur), Pixeldichte auf 2 begrenzt, `powerPreference: "low-power"`,
Modell aus wenigen tausend Dreiecken.

### Geometrie aus Code statt aus einer Modelldatei

Gewählt gegenüber einer glTF-Datei aus einem 3D-Programm:

- **Die Maße stehen an einer Stelle** (`vehicle3d/dimensions.ts`) und sind
  lesbar. Kommen die realen Abmessungen, ist die Korrektur ein
  Zahlenaustausch. Eine Modelldatei müsste neu gebaut werden — von jemandem
  mit dem passenden Programm.
- **Kein Binärartefakt im Repository**, das niemand mehr ändern kann.
- Das Fahrzeug ist ein Kofferaufbau mit gleichbleibendem Querschnitt. Aus
  Seitenprofilen in die Breite gezogen (`ExtrudeGeometry`) entsteht genau
  diese Form — mit wenig Aufwand und wenigen Dreiecken.

Der Preis ist Detailtiefe: Das Modell ist eine saubere technische
Nachbildung, keine Fotografie. Für ein Dashboard, das Zustände zeigen soll,
ist das die richtige Seite des Handels (Kapitel 18 §34).

### Nachgeladen, nicht mitgeliefert

three.js wird als eigenes Paket nachgeladen. Das Startpaket des Dashboards
bleibt dadurch unverändert klein, und die Oberfläche steht sofort. Bis das
3D-Paket da ist, zeigt die SVG-Seitenansicht dieselben Zustände.

Alle Ressourcen sind lokal. Die Umgebungsspiegelung ist ein im Browser
erzeugter Verlauf, keine heruntergeladene Aufnahme — ohne Internet ändert
sich nichts (Kapitel 17 §107).

### Rückfallebene

Ohne WebGL bleibt die SVG-Seitenansicht. Sie ist kein Notbehelf: Sie zeigt
dieselben Zustände nach denselben Regeln und lässt sich nur nicht drehen.

## Ehrlichkeit in drei Dimensionen

Die Regeln aus Kapitel 18 gelten unverändert; sie brauchen nur eine andere
Ausdrucksform:

| Zustand | SVG | 3D |
| --- | --- | --- |
| gemeldete Stellung | Teil in der Stellung | Teil in der Stellung |
| in Bewegung | Zwischenstellung | Zwischenstellung |
| **unbekannt** | gestrichelt an der Ruhelage | durchscheinend und schwach leuchtend an der Ruhelage, **ohne Bewegung** |
| **nicht konfiguriert** | nicht gezeichnet | nicht erzeugt |

Ein Sonderfall steht darunter: die Terrasse, die eingefahren vollständig
verschwindet.

Gestrichelte Linien gibt es in 3D nicht. Das räumliche Gegenstück ist ein
Bauteil, das sichtbar anders aussieht als jedes gemeldete — durchscheinend
statt lackiert. Entscheidend ist in beiden Fällen dasselbe: **Bei unbekannter
Stellung wird nichts bewegt und keine Position behauptet** (§106).

Die Markisenkassette ist Teil des Aufbaus und immer da; sie ist am Fahrzeug
verschraubt. Diese Trennung ist kein Detail: Sie verhindert, dass eine
fehlende Hardwarezuordnung ein real vorhandenes Bauteil verschwinden lässt.

**Das Markisentuch wird nicht dargestellt** — so vom Fahrzeughalter
entschieden (2026-08-12). Die Markise bleibt bedienbar und behält ihre
Schnellzugriffe; sie wird lediglich nicht gezeichnet, und zwar in **beiden**
Ansichten gleich. Eine Funktion nicht zu zeigen ist etwas anderes, als sie
falsch zu zeigen: Nichts zu zeichnen behauptet nichts.

### Ein Teil, das eingefahren verschwindet

Die Terrasse über dem Tandem ist der Sonderfall, den die Tabelle oben nicht
vorhergesehen hatte. Sie fährt seitlich aus der Flanke heraus — Holzbelag,
Außenschürze mit zwei Radbögen und eine Treppe, alles als **ein** Zustand.
Eingefahren ist von ihr nichts zu sehen: glatte Flanke, frei stehende Räder.

Damit greift die Regel „durchscheinend an der Ruhelage" nicht mehr von
selbst. Ein durchscheinendes Nichts wäre von einem eingefahrenen Nichts nicht
zu unterscheiden, und der Betrachter läse daraus „eingefahren" — genau die
Behauptung, die §106 verbietet. Deshalb wird bei unbekannter Stellung die
**Außenschürze bündig in der Flanke** gezeigt, durchscheinend und schwach
leuchtend. Das ist die Regel wörtlich genommen und zugleich von beiden
gemeldeten Stellungen unterscheidbar.

Wie das Ausfahren mechanisch abläuft, ist nicht bekannt. Die Zwischenstellung
ist deshalb eine gerade Bewegung nach außen und **keine Behauptung über die
Kinematik**; belegt sind allein die beiden Endlagen.

## Bedienung

Ein Finger dreht, zwei Finger ändern den Abstand. Der Blickwinkel ist nach
unten begrenzt — man schaut nie von unter der Fahrbahn auf das Fahrzeug.
Eine Schaltfläche stellt die Ausgangsansicht wieder her.

**Die Ansicht bleibt reine Ausgabe.** Ein Tippen auf ein Bauteil löst nichts
aus. Gesteuert wird über die Schnellzugriffe und die Fachseiten (Kapitel 8
§6) — eine Drehbewegung soll nie versehentlich Mechanik in Gang setzen.

Bei `prefers-reduced-motion` entfällt das Auslaufen; die Ansicht folgt dem
Finger und steht beim Loslassen.

## Maße

Länge (11,5 m) und Höhe (4,0 m) sind angegeben. Alle übrigen Maße —
Radstand, Achsabstand, Bodenhöhe, Fensterlagen — sind aus Fotos geschätzt und
als solche gekennzeichnet (offener Punkt K1).

Das ist vertretbar, weil aus diesen Zahlen **nichts berechnet wird**: keine
Durchfahrtshöhe, kein Wendekreis, keine Warnung. Sie erzeugen ein Bild zum
Wiedererkennen. Eine geratene Tankkapazität wäre etwas anderes — sie stünde
als Zahl in der Oberfläche und würde eine Aussage über das Fahrzeug treffen.
Deshalb gibt es die weiterhin nicht.

## Konsequenzen

- Das 3D-Paket ist deutlich größer als der Rest der Oberfläche. Im Fahrzeug
  wird es über LAN vom Pi selbst geliefert; die Ladezeit ist dort
  unerheblich. Getrennt nachgeladen belastet es den Start nicht.
- Die Bildrate auf dem realen Display ist zu messen, sobald die Hardware
  steht (offener Punkt I4). Sollte sie nicht genügen, sind Pixeldichte und
  Kantenglättung die ersten Stellschrauben — die SVG-Rückfallebene bleibt als
  letzte.
- Die Fahrzeugdarstellung bleibt als Ganzes austauschbar: Zustände hinein,
  Darstellung heraus (Kapitel 18 §104). Weder Dashboard noch Fachmodule
  wissen, ob gerade 3D oder SVG gezeigt wird.
