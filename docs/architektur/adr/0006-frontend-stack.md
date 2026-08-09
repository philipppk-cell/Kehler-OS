# ADR 0006 – Frontend-Stack

**Status:** angenommen · Phase 1
**Bezug:** Kapitel 7, Kapitel 8, Kapitel 17 §107–§112, Kapitel 18 §14/§15/§86

## Entscheidung

**React + TypeScript + Vite. Motion für Animation. CSS Modules über
Design-Tokens. Alle Assets lokal.**

> **Nachtrag (Umsetzung M3/M4):** Zwei Festlegungen dieses ADR sind bei der
> Umsetzung bewusst korrigiert worden. Beide sind unten an Ort und Stelle
> begründet:
>
> 1. **React 18 statt 19.** Der Stack wird auf einer Version aufgebaut, für die
>    Motion, die Typdefinitionen und die Testwerkzeuge geprüft zusammenspielen.
>    Kehler OS braucht keine Funktion aus React 19; ein Wechsel ist jederzeit
>    möglich, wenn es einen sachlichen Anlass gibt.
> 2. **Kein Zustand, kein TanStack Query.** Siehe Abschnitt
>    „Zustandsverwaltung im Client".

## Abwägung der Basis

**React + TypeScript — gewählt.**
Nicht wegen Popularität (Kapitel 18 §87 verbietet dieses Argument
ausdrücklich), sondern wegen zweier projektspezifischer Punkte:

1. **Kapitel 17 §119/§120** verlangt, dass ein anderer qualifizierter
   Entwickler das System übernehmen kann und Kehler OS nicht von Claude
   abhängig ist. React ist die Umgebung, für die diese Person am
   wahrscheinlichsten zu finden ist.
2. **Animationsqualität.** Kapitel 8 verlangt zustandsgetriebene
   Fahrzeuganimation auf Premium-HMI-Niveau. Mit *Motion* (vormals Framer
   Motion) existiert dafür eine ausgereifte, deklarative Bibliothek, die
   Animationen direkt an Zustandswechsel bindet — genau das Modell aus
   Kapitel 18 §105.

**Svelte — ernsthaft erwogen, verworfen.** Kleinere Bundles und geringerer
Laufzeit-Overhead wären auf einem Pi-getriebenen Display ein realer Vorteil.
Verworfen wegen des schmaleren Ökosystems bei Animation und Tests und der
geringeren Verfügbarkeit von Entwicklern. Bei einem System, das über Jahre
gepflegt werden soll, wiegt das schwerer als einige hundert Kilobyte.

**Vue — verworfen.** Solide Alternative ohne entscheidenden Vorteil in diesem
Vergleich.

## Styling: Tokens statt Utility-Klassen

**CSS Modules mit CSS Custom Properties als Design-Tokens — gewählt.**

**Tailwind wurde bewusst verworfen.** Kapitel 7 §41/§42 verlangt zentrale
Design-Tokens und verbietet ausdrücklich frei erfundene Werte
(„nicht `padding: 13px` hier und `17px` dort"). Utility-Klassen laden zwar zur
Konsistenz ein, machen aber das Abweichen genauso leicht wie das Einhalten. Ein
Token-Layer, in dem es die abweichenden Werte schlicht nicht gibt, setzt die
Anforderung strukturell durch statt durch Disziplin.

Zusätzlich erfüllen CSS Custom Properties die Nachtmodus- und
Helligkeitsanforderung (Kapitel 7 §25/§26) elegant: Ein Themenwechsel tauscht
Tokenwerte, ohne dass eine Komponente davon weiß.

## Zustandsverwaltung im Client

Klare Trennung, die direkt aus Kapitel 13 §3 folgt:

| Art | Lösung |
| --- | --- |
| Fahrzeugzustand | ausschließlich aus dem WebSocket-Snapshot/Delta, im Realtime-Store gehalten, **nie lokal erzeugt oder überschrieben** |
| Abfragedaten (Historie, Konfiguration, Logs) | `fetch` mit definierter Gültigkeit, an den Realtime-Store gekoppelt |
| reine UI-Zustände (offene Dialoge, Auswahl) | lokaler React-State |

**Korrektur gegenüber der ursprünglichen Fassung: weder Zustand noch TanStack
Query werden eingesetzt.** Ursprünglich waren beide vorgesehen. Beim Bau des
Realtime-Store hat sich gezeigt, dass sie hier nichts beitragen:

- Der Fahrzeugzustand kommt vollständig über **einen** WebSocket. Es gibt keine
  Abfragen zu cachen, zu deduplizieren, zu invalidieren oder erneut zu holen —
  genau die Aufgaben, für die TanStack Query existiert. Der Snapshot beim
  Verbindungsaufbau ersetzt jede Cache-Strategie.
- Der Store ist ein einziges, vom Server geschriebenes Objekt. Dafür genügt
  Reacts eingebautes `useSyncExternalStore`, das für exakt diesen Fall
  vorgesehen ist. Es liefert zudem die Garantie, die hier zählt: keine
  zerrissenen Zwischenzustände beim Rendern.

Das folgt Kapitel 17 §81 — jede Abhängigkeit muss sich rechtfertigen. Zwei
Bibliotheken, die dauerhaft gepflegt, aktualisiert und beim Übernehmen des
Systems verstanden werden müssten, ohne dass sie ein reales Problem lösen,
wären eine Belastung und kein Gewinn. Die Entscheidung ist umkehrbar: Sobald
echte Abfragedaten mit Cache-Bedarf dazukommen (Historie in M-später), wird
sie neu bewertet.

Der Realtime-Store ist bewusst ein **Spiegel**, kein eigenständiger Zustand.
Ein Tastendruck schreibt dort nichts hinein; er löst einen Befehl aus, und die
Anzeige ändert sich, wenn der Server es meldet. Der laufende Befehl wird separat
als „in Ausführung“ geführt, damit die UI sofort reagieren kann, ohne den
Hardwarezustand zu behaupten (Kapitel 7 §15, Kapitel 18 §37).

## Fahrzeugvisualisierung

**Inline-SVG mit benannten Ebenen, gesteuert über Zustandswerte.**

Gewählt gegenüber Canvas oder 3D (Three.js), weil:

- Zustände lassen sich direkt an Ebenen binden (`vehicle.garage.door = OPENING`
  → Öffnungsanimation der Garagenebene)
- geringe Last, keine WebGL-Abhängigkeit auf dem Pi (Kapitel 17 §6)
- die Grafik ist eine austauschbare Datei mit fester Ebenenkonvention, damit
  später ersetzbar, ohne das Dashboard anzufassen (Kapitel 18 §104)
- Kapitel 18 §34 warnt vor dekorativem Overkill; 3D wäre genau das

Ist ein Zwischenzustand aus der Hardware nicht ableitbar, wird **keine
Bewegungsanimation** gezeigt, sondern der unbekannte Zustand dargestellt
(Kapitel 18 §106).

## Assets und Offline

Schriften, Icons und Grafiken werden **lokal gebündelt**. Kein CDN, keine
externe Schriftquelle. Kapitel 17 §107–§109: Das System darf ohne Internet
nicht visuell auseinanderfallen. Die Icon-Bibliothek wird als ein einziges,
stilistisch einheitliches Set eingebunden (Kapitel 7 §21).

## Mehrsprachigkeit

Sämtliche sichtbaren Texte laufen über eine i18n-Schicht mit Schlüsseln;
ausgeliefert wird zunächst nur Deutsch. Programmlogik hängt nie an einem
Anzeigetext (Kapitel 13 §76, Kapitel 7 §35).

## Tests

Vitest plus Testing Library für Komponenten und Zustandslogik, Playwright für
die durchgehenden Bedienabläufe (Kapitel 18 §70). Gezielt getestet werden
`UNKNOWN`, `OFFLINE`, `TIMEOUT`, `ERROR` und „nicht konfiguriert“ — nicht nur
der Normalfall (Kapitel 18 §71).

## Konsequenzen

- Das Frontend wird zu statischen Dateien gebaut und vom Backend ausgeliefert;
  dadurch entfällt ein separater Webserver im Normalbetrieb.
- Bundle-Größe und Startzeit werden gemessen und gegen ein Budget geprüft
  (Kapitel 17 §93).
- Das endgültige Layout hängt am Seitenverhältnis des Hauptdisplays
  (offener Punkt I4); bis dahin wird responsiv entwickelt.
