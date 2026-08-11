# Fahrzeugmodell

Kehler OS zeigt das Fahrzeug im Dashboard dreidimensional. Standardmäßig wird
es **aus Code gebaut** (ADR 0008). Liegt unter `config/vehicle/model.glb` ein
geliefertes Modell, hat es Vorrang.

## Was ein geliefertes Modell mitbringen muss

Siehe Punkt **K2** in `docs/OPEN_HARDWARE_REQUIREMENTS.md`. Der Kern:

> Je bewegliches Teil eine glTF-Animation, benannt `garage`, `door`, `step`
> bzw. `awning`, vom geschlossenen zum offenen Ende.

Kehler OS spielt sie nicht ab, sondern setzt die Stelle darin. Der Weg gehört
dem Modell, die Stellung dem Zustand.

## Den Ladeweg prüfen, ohne ein Modell zu haben

```bash
python tools/model/make_test_glb.py config/vehicle/model.glb
```

Erzeugt vier Kästen mit Animationen für `garage`, `step` und `awning` — und
absichtlich **ohne** eine für `door`. Damit lässt sich beides prüfen: dass ein
Modell verwendet wird und dass ein fehlendes Teil auch als fehlend gemeldet
wird.

Die Meldung steht im Diagnoseprotokoll des Browsers:

```
Kehler OS · Fahrzeugmodell aus Datei (garage, step, awning) — ohne Bewegung: door
```

Danach wieder löschen — sonst zeigt das Dashboard vier Kästen statt eines
Fahrzeugs:

```bash
rm config/vehicle/model.glb
```
