# Demo-Datei

Eine einzelne HTML-Datei, die Kehler OS zeigt — ohne Server, ohne Internet,
ohne Fahrzeug. Zum Anschauen, nicht zum Bedienen.

## Wie sie entsteht

```bash
# 1. Backend laufen lassen und eine Sitzung aufzeichnen
PYTHONPATH=backend python -m kehleros.main &
python tools/demo/capture.py 40 3        # 40 Bilder im Abstand von 3 s

# 2. Oberfläche als ein einziges Bündel bauen
cd frontend && npm run build:demo && cd ..

# 3. Alles in eine Datei packen
python tools/demo/build.py
```

Ergebnis: `tools/demo/kehler-os-demo.html`.

## Warum aufgezeichnet und nicht nachgebaut

Die Demo rechnet **nichts** selbst. Gesamtmenge Frischwasser, Laderichtung,
Wärmequelle — all das entsteht weiterhin im Backend und wird hier nur
abgespielt.

Die Alternative wäre gewesen, diese Deutungen in JavaScript nachzubilden. Das
ist genau die Verdopplung von Geschäftslogik, die Kapitel 18 §6 im Backend
halten will: Zwei Umsetzungen derselben Regel laufen auseinander, und dann
zeigt die Demo etwas anderes als das Fahrzeug.

Jede Zahl in der Demo ist eine Zahl, die das Backend tatsächlich ausgegeben
hat.

## Was sie nicht kann

**Sie schaltet nichts.** Jeder Befehl wird abgewiesen — über denselben Weg wie
eine echte Ablehnung, mit sichtbarer Begründung. Das ist keine Einstellung,
die sich ändern ließe: In der Datei gibt es kein Fahrzeug, keine Steuerung und
keinen Adapter.

Der Hinweis oben auf der Seite ist nicht wegklickbar. Kapitel 18 §66 verlangt,
dass eine Simulation dauerhaft sichtbar bleibt; für eine Aufzeichnung gilt das
erst recht.

## Was die Aufzeichnung enthält

Die Datei ist eine Momentaufnahme des Entwicklungsstands, keine Live-Ansicht.
Bewusst mit aufgezeichnet, weil es die interessanten Zustände sind:

* eine **Warnung** (Grauwasser über der Schwelle),
* eine **Lücke im Verlauf** aus einem kurz ausgelösten Sensorfehler,
* die **Heizung ohne Anbindung** — 24 Funktionen als „noch zu verifizieren",
  weil die Modbus-Registerliste fehlt.

Die Aufzeichnung läuft in Schleife. Nach etwa zwei Minuten beginnt sie von
vorn; dass Werte dann zurückspringen, ist keine Fehlfunktion.
