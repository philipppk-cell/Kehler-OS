# Photos

Ablage für eigene Fotos vom Fahrzeug.

Diese Datei ist zunächst nur da, damit der Ordner überhaupt existiert: Git
kennt keine leeren Ordner. Sobald hier Bilder liegen, hat sie diesen Zweck
erfüllt und darf bleiben oder gehen.

## Wozu Fotos hier nützlich sind

Mehrere offene Punkte in `docs/OPEN_HARDWARE_REQUIREMENTS.md` sind mit einem
Foto beantwortet und ohne eines gar nicht:

* **Typenschilder** — Wechselrichter, Heizung, Batterie, Ladegerät. Was darauf
  steht, ist die Angabe. Kehler OS erfindet keine Gerätedaten (Kapitel 18 §97);
  ein lesbares Schild ist die Antwort, keine Schätzung.
* **Schaltschrank und Klemmen** — für die Zuordnung von Signalen zu Funktionen.
* **Maße am Fahrzeug** — Punkt K1, sofern etwas mit Zollstock im Bild ist.
* **Anzeigen im Ist-Zustand** — Displays, Bedienteile, vorhandene Panels.

Ein Foto ist eine Angabe des Fahrzeughalters, keine Annahme. Genau deshalb
darf daraus gearbeitet werden.

## Was hier nicht hinein gehört

Was einmal committet ist, bleibt in der Historie — auch nach dem Löschen der
Datei. Deshalb:

* keine Zugangsdaten, Passwörter, WLAN-Schlüssel, auch nicht auf einem Zettel
  im Bildhintergrund (Kapitel 15 §49/§50),
* keine Kennzeichen, Fahrgestellnummern oder Standorte, wenn das Repository
  je über den eigenen Kreis hinaus geteilt werden soll,
* keine Videos oder Rohformate. Ein Repository ist kein Bildarchiv; große
  Binärdateien bläht man nicht ohne Not in die Historie.

Sind Fotos dabei, die nicht dauerhaft versioniert sein sollen, sag Bescheid —
dann kommt ein Muster für diesen Ordner in `.gitignore`, so wie es
`config/hardware/` und `config/vehicle/model.glb` bereits haben.
