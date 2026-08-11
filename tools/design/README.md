# Entwürfe

Vorlagen zur Auswahl, bevor etwas in die Oberfläche eingebaut wird.

## `bootscreen-entwuerfe.html`

Fünf animierte Entwürfe für den Startbildschirm (M3, „Bootscreen"). Im Browser
öffnen; jeder Rahmen lässt sich zum Wiederholen antippen.

Die Entwürfe stehen **außerhalb** von `frontend/`, weil sie noch keine
Software sind. Erst der ausgewählte wird als Komponente eingebaut — vier
Bausteine zu bauen, von denen vier weggeworfen werden, wäre Aufwand ohne
Nutzen.

Sie verwenden ausschließlich Farben und Schriftgrade aus
`frontend/src/design/tokens.css` und kommen ohne Bilddateien aus. Der Umzug in
die Oberfläche ist deshalb ein Kopieren und kein Nachbauen.

**Was für alle gilt und beim Einbau bindend ist:**

* Der Start wird **nicht künstlich verlängert**. Ein Bootscreen, der stehen
  bleibt, obwohl das System bereit ist, ist eine Vorführung auf Kosten des
  Benutzers. Er verschwindet, sobald der erste Zustand da ist — und bleibt,
  solange es dauert.
* `prefers-reduced-motion` wird beachtet: Dann erscheint das Zeichen fertig,
  ohne Ablauf (Kapitel 7, `tokens.css`).
