"""Baut die Demo als **eine einzige HTML-Datei**.

Alles liegt darin: Oberfläche, Stile, die Fahrzeugdarstellung und die
Aufzeichnung. Kein Server, kein Internet, keine zweite Datei. Man öffnet sie
und sieht Kehler OS.

Das passt zur Anforderung, dass die Oberfläche ohne Internet nicht
auseinanderfällt (Kapitel 17 §107/§108) — hier auf die Spitze getrieben: Es
gibt gar nichts nachzuladen.

Voraussetzung: ``npm run build:demo`` im Ordner ``frontend`` hat gelaufen und
``tools/demo/recording.json`` liegt vor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "frontend/dist-demo"
DEMO = REPO / "tools/demo"

BANNER = """
<div class="demo-note">
  <strong>Demo-Ansicht &middot; {geraet}</strong>
  <span>Aufzeichnung einer laufenden Simulation vom {recorded}. Kein Fahrzeug
  angebunden — es wird nichts geschaltet.</span>
</div>
"""

# Zwei Ausgaben auf Wunsch des Fahrzeughalters. Die Oberfläche darin ist
# **dieselbe** — sie richtet sich nach der Bildschirmbreite und käme mit einer
# Datei aus. Der Unterschied liegt allein in der Beschriftung und darin, an
# welchem Gerät die jeweilige Datei geprüft wurde. Etwas anderes zu behaupten,
# wäre eine erfundene Unterscheidung.
ZIELE = {
    "ipad": "iPad Pro 13 Zoll",
    "handy": "Handy",
}

STYLE = """
/* Der Hinweis kommt **zusätzlich** zur Oberfläche, die selbst die volle Höhe
   beansprucht. Ohne diese drei Regeln addiert er sich auf 100 % Höhe darauf,
   die Seite läuft über, und die untere Navigationsleiste — auf dem Handy die
   einzige Navigation — rutscht unter den Bildschirmrand.

   Aufgefallen bei der Sichtprüfung auf Handygröße: Die Demo war nicht
   bedienbar. */
body {
  display: flex;
  flex-direction: column;
}
#root {
  flex: 1;
  min-height: 0;
}

/* Der Demo-Hinweis ist nicht wegklickbar. Kapitel 18 §66 verlangt, dass eine
   Simulation dauerhaft sichtbar bleibt und nie beiläufig wirkt — für eine
   Aufzeichnung gilt das erst recht. */
.demo-note {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 12px;
  padding: 10px 20px;
  background: #3a2a08;
  border-bottom: 1px solid rgba(245, 165, 36, 0.4);
  color: #f5d79a;
  font-family: var(--font-sans, system-ui);
  font-size: 12.5px;
  line-height: 1.45;
}
.demo-note strong { color: #f5a524; letter-spacing: 0.04em; text-transform: uppercase; }
"""


def read_one(pattern: str) -> str:
    matches = sorted(BUILD.glob(pattern))
    if len(matches) != 1:
        raise SystemExit(
            f"Erwartet genau eine Datei für '{pattern}', gefunden: {len(matches)}.\n"
            "Wurde 'npm run build:demo' ausgeführt? Die Demo braucht einen "
            "Build ohne aufgeteilte Bündel — sonst kann eine einzelne Datei "
            "die nachgeladenen Teile nicht enthalten."
        )
    return matches[0].read_text(encoding="utf-8")


def main() -> int:
    recording_path = DEMO / "recording.json"
    if not recording_path.is_file():
        raise SystemExit(f"Aufzeichnung fehlt: {recording_path}")

    recording = json.loads(recording_path.read_text(encoding="utf-8"))
    css = read_one("assets/*.css")
    script = read_one("assets/*.js")
    shim = (DEMO / "shim.js").read_text(encoding="utf-8")

    template = (REPO / "frontend/index.html").read_text(encoding="utf-8")
    head = template.split("<head>", 1)[1].split("</head>", 1)[0]
    # Der Verweis auf das Modul entfällt — es steht gleich eingebettet da.
    head = "\n".join(line for line in head.splitlines() if "<script" not in line)

    for kennung, geraet in ZIELE.items():
        write(kennung, geraet, recording, css, script, shim, head)
    return 0


def write(kennung, geraet, recording, css, script, shim, head) -> None:
    banner = BANNER.format(recorded=recording["recordedAt"][:10], geraet=geraet)

    html = f"""<!doctype html>
<html lang="de" data-night="false">
<head>
{head}
<style>{css}</style>
<style>{STYLE}</style>
</head>
<body>
{banner}
<div id="root"></div>
<script>window.__KEHLER_DEMO__ = {json.dumps(recording, separators=(",", ":"))};</script>
<script>{shim}</script>
<script type="module">{script}</script>
</body>
</html>
"""

    out = DEMO / f"kehler-os-demo-{kennung}.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out} — {out.stat().st_size / 1024 / 1024:.1f} MB ({geraet})")

    # Zweite Fassung ohne Dokumentrahmen, für Umgebungen, die den Inhalt in
    # ihr eigenes Grundgerüst einsetzen. Gleicher Inhalt, nur ohne <html>,
    # <head> und <body> — sonst stünden zwei Dokumente ineinander.
    fragment = DEMO / f"kehler-os-demo-{kennung}.fragment.html"
    fragment.write_text(
        f"""<title>Kehler OS – Demo</title>
<style>{css}</style>
<style>{STYLE}</style>
{banner}
<div id="root"></div>
<script>window.__KEHLER_DEMO__ = {json.dumps(recording, separators=(",", ":"))};</script>
<script>{shim}</script>
<script type="module">{script}</script>
""",
        encoding="utf-8",
    )
    print(f"{fragment} — {fragment.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    sys.exit(main())
