# KEHLER OS

# Kapitel 7 – Designsystem und visuelle Identität

> Vorbemerkung aus der Übermittlung:
> Jetzt kommen wir zu Kapitel 7 – Designsystem. Hier legen wir fest, wie Kehler OS
> aussehen und sich anfühlen soll. Das ist wichtig, damit Claude später nicht bei
> jeder einzelnen Oberfläche eigene Designentscheidungen trifft.

WICHTIGE ANWEISUNG

Dieses Kapitel dient ausschließlich der Wissensaufnahme.

Du bist weiterhin nicht mit der Entwicklung beauftragt.

Schreibe keinen Code.

Erstelle keine Dateien.

Beginne nicht mit der Implementierung.

Treffe keine eigenständigen Designentscheidungen, die den Anforderungen dieses Dokuments widersprechen.

Verwende dieses Kapitel zusammen mit den Kapiteln 1–6 als verbindliche Grundlage.

Erst das letzte Kapitel enthält den eigentlichen Entwicklungsauftrag.

⸻

## 1. Ziel des Designs

Kehler OS soll nicht wie eine gewöhnliche Wohnmobil-App aussehen.

Es soll wie ein eigenständiges, hochwertiges Fahrzeug-Betriebssystem wirken.

Die Benutzeroberfläche soll den Eindruck vermitteln:

* technisch
* präzise
* hochwertig
* ruhig
* modern
* zuverlässig
* minimalistisch
* professionell

Das Design darf niemals billig, verspielt oder überladen wirken.

⸻

## 2. Grundgefühl

Das zentrale Gefühl von Kehler OS ist:

Kontrolle ohne Komplexität.

Im Hintergrund laufen viele Systeme gleichzeitig.

Die Benutzeroberfläche zeigt davon nur die Informationen, die im jeweiligen Moment relevant sind.

Der Benutzer soll jederzeit wissen:

* Wo bin ich?
* Was passiert gerade?
* Ist alles in Ordnung?
* Was benötigt meine Aufmerksamkeit?
* Was kann ich jetzt tun?

⸻

## 3. Dark-First

Kehler OS wird grundsätzlich als Dark-First-System entwickelt.

Die dunkle Oberfläche ist der primäre visuelle Zustand.

Das ist besonders wichtig für die Nutzung im Fahrzeug bei Nacht.

Die Oberfläche darf keine unnötig hellen Flächen besitzen.

⸻

## 4. Farben

Das Farbsystem muss bewusst und sparsam eingesetzt werden.

Die Oberfläche soll nicht aus vielen bunten Farben bestehen.

Es gibt grundsätzlich:

* Hintergrundfarben
* Oberflächenfarben
* Textfarben
* neutrale Statusfarben
* Akzentfarbe
* Warnfarbe
* Fehlerfarbe
* Erfolgsfarbe

Farben müssen semantisch verwendet werden.

⸻

## 5. Semantische Farben

Farben dürfen nicht nur dekorativ sein.

Sie müssen eine Bedeutung besitzen.

Beispiel:

Grün

Normaler beziehungsweise positiver Zustand.

Gelb

Aufmerksamkeit erforderlich.

Rot

Fehler oder kritischer Zustand.

Blau beziehungsweise Akzentfarbe

Interaktive oder informative Elemente.

Die konkrete Farbpalette wird später als Teil des finalen Designsystems definiert.

⸻

## 6. Keine unnötigen Farben

Nicht jedes Element darf eine eigene Farbe bekommen.

Ein Benutzer soll nicht das Gefühl bekommen, durch eine farbige Statuswand zu navigieren.

Die Grundoberfläche bleibt ruhig.

Akzentfarben werden gezielt eingesetzt.

⸻

## 7. Typografie

Die Typografie muss hochwertig und sehr gut lesbar sein.

Prioritäten:

1. Lesbarkeit
2. klare Hierarchie
3. Konsistenz
4. modernes Erscheinungsbild

Es müssen definierte Schriftgrößen und Gewichtungen verwendet werden.

Beispielsweise:

* Display
* H1
* H2
* H3
* Body
* Caption
* Label
* Status

Die endgültige Schriftfamilie und Größen werden später festgelegt.

⸻

## 8. Informationshierarchie

Nicht alle Informationen besitzen dieselbe Wichtigkeit.

Die Oberfläche muss deshalb eine klare Hierarchie besitzen.

Beispiel:

```
HAUPTINFORMATION
      74 %
Batterie
```

Die wichtigste Information muss auf den ersten Blick erkennbar sein.

⸻

## 9. Weißraum

Weißraum beziehungsweise freier Raum ist ein wichtiger Bestandteil des Designs.

Elemente dürfen nicht zu eng zusammenstehen.

Die Oberfläche soll großzügig wirken.

⸻

## 10. Raster

Alle Oberflächen müssen einem konsistenten Layoutsystem folgen.

Abstände und Größen sollen nicht zufällig gewählt werden.

Es muss ein einheitliches Spacing-System geben.

Beispielsweise können Abstände auf einer festen Basiseinheit beruhen.

Die konkrete Skala wird später definiert.

⸻

## 11. Karten

Karten können verwendet werden, um Informationen zu gruppieren.

Sie dürfen jedoch nicht überall eingesetzt werden.

Karten sollen nur verwendet werden, wenn sie die Informationsstruktur verbessern.

Eine Seite darf nicht aus unzähligen kleinen Boxen bestehen.

⸻

## 12. Bedienelemente

Bedienelemente müssen eindeutig erkennbar sein.

Der Benutzer muss sofort unterscheiden können zwischen:

* Information
* Button
* Schalter
* Slider
* Auswahl
* Status
* Navigation

⸻

## 13. Touch-Bedienung

Kehler OS wird primär über Touch bedient.

Deshalb müssen interaktive Elemente ausreichend groß sein.

Besonders wichtig sind:

* Buttons
* Schalter
* Slider
* Navigation
* Notfallfunktionen

Die Oberfläche darf nicht auf winzige Desktop-Bedienelemente angewiesen sein.

⸻

## 14. Feedback

Jede Benutzeraktion muss unmittelbar visuelles Feedback geben.

Beispiel:

Benutzer drückt Licht EIN.

Die Oberfläche muss unmittelbar zeigen, dass der Befehl verarbeitet wurde.

Der tatsächliche Hardwarezustand muss anschließend bestätigt werden.

⸻

## 15. Kein falsches Feedback

Ein Button darf nicht einfach „AN“ anzeigen, wenn nur ein Befehl gesendet wurde.

Es muss zwischen:

Befehl gesendet

und:

Hardware bestätigt EIN

unterschieden werden können.

Das ist besonders bei wichtigen Funktionen entscheidend.

⸻

## 16. Zustände

UI-Komponenten müssen verschiedene Zustände darstellen können.

Beispiele:

* normal
* aktiv
* deaktiviert
* lädt
* unbekannt
* Warnung
* Fehler
* offline

⸻

## 17. Animationen

Animationen sind Bestandteil des Designs.

Sie sollen das System lebendig und hochwertig wirken lassen.

Animationen müssen jedoch funktional sein.

Keine Animation darf die Bedienung verlangsamen.

⸻

## 18. Geschwindigkeit von Animationen

Animationen sollen kurz und flüssig sein.

Keine unnötig langen Übergänge.

Die Benutzeroberfläche muss sich unmittelbar anfühlen.

⸻

## 19. Mikroanimationen

Kleine Animationen können verwendet werden für:

* Schalter
* Statusänderungen
* Navigation
* Ladezustände
* Diagramme
* Benachrichtigungen
* Übergänge

Sie müssen subtil bleiben.

⸻

## 20. Übergänge

Beim Wechsel zwischen Seiten soll ein konsistenter Übergang verwendet werden.

Die Navigation darf niemals abrupt oder chaotisch wirken.

⸻

## 21. Icons

Icons müssen einem einheitlichen Stil folgen.

Keine Mischung aus:

* Outline-Icons
* 3D-Icons
* Emoji
* unterschiedlichen Icon-Sets

Das gesamte System muss visuell zusammenpassen.

⸻

## 22. Icons statt Text

Wenn ein allgemein verständliches Symbol existiert, kann es Text ergänzen.

Text darf jedoch nicht durch unklare Symbole ersetzt werden.

Verständlichkeit hat Vorrang vor Minimalismus.

⸻

## 23. Statusdarstellung

Statusinformationen müssen schnell erfassbar sein.

Beispiele:

```
● ONLINE
● NORMAL
● WARNUNG
● FEHLER
```

Die Darstellung muss auch ohne Farbe verständlich bleiben.

⸻

## 24. Barrierearme Gestaltung

Obwohl Kehler OS primär für ein bestimmtes Fahrzeug entwickelt wird, muss die Oberfläche gut lesbar sein.

Dazu gehören:

* ausreichender Kontrast
* klare Schrift
* verständliche Symbole
* ausreichende Touchflächen

⸻

## 25. Nachtbetrieb

Die Oberfläche muss für Nachtbetrieb optimiert sein.

Dabei soll:

* die Helligkeit reduziert werden können
* unnötige helle Elemente verschwinden
* wichtige Warnungen weiterhin sichtbar bleiben

Ein spezieller Night Mode kann vorgesehen werden.

⸻

## 26. Helligkeit

Die Displayhelligkeit muss softwareseitig steuerbar sein, sofern die Hardware dies unterstützt.

Die Helligkeit kann später automatisiert werden.

Beispiel:

```
Tag → hell
Abend → reduziert
Nacht → sehr dunkel
```

⸻

## 27. Hauptnavigation

Die Navigation muss immer verständlich bleiben.

Der Benutzer soll jederzeit wissen, in welchem Bereich er sich befindet.

Die wichtigsten Funktionen müssen schnell erreichbar sein.

⸻

## 28. Dashboard

Das Dashboard ist die wichtigste Oberfläche von Kehler OS.

Es zeigt den aktuellen Zustand des Fahrzeugs.

Es soll nicht jede verfügbare Information anzeigen.

Es zeigt nur die wichtigsten Informationen.

Beispiele:

* Energie
* Wasser
* Temperatur
* Türen
* Internet
* aktuelle Warnungen

⸻

## 29. Fahrzeugvisualisierung

Ein zentrales Element des Dashboards soll eine grafische Darstellung des Wohnmobils sein.

Diese Darstellung soll das tatsächliche Fahrzeug repräsentieren.

Sie soll hochwertig und modern wirken.

Die Darstellung darf animiert werden.

Wichtig:

Das Fahrzeugbild ist primär eine visuelle Statusdarstellung.

Es soll nicht automatisch zu einem riesigen interaktiven Bedienfeld werden.

Die eigentlichen Steuerfunktionen befinden sich in dafür vorgesehenen UI-Bereichen.

⸻

## 30. Räumliche Darstellung

Das Fahrzeug kann später logisch in Bereiche aufgeteilt werden.

Beispielsweise:

* Fahrerhaus
* Wohnbereich
* Küche
* Schlafzimmer
* Bad
* Garage
* Technikbereich

Diese Bereiche können für Statusinformationen verwendet werden.

⸻

## 31. Diagramme

Diagramme sollen verwendet werden, wenn sie einen Mehrwert bieten.

Beispiele:

* Batteriehistorie
* Solarleistung
* Energieverbrauch
* Tankverlauf
* Temperatur

Diagramme müssen einfach verständlich sein.

⸻

## 32. Keine Datenüberflutung

Ein Diagramm darf nicht mit Informationen überladen werden.

Der Benutzer soll Trends erkennen können.

Nicht jede Messung muss gleichzeitig angezeigt werden.

⸻

## 33. Benachrichtigungen

Benachrichtigungen sollen priorisiert werden.

Nicht jede Information muss den Benutzer unterbrechen.

Es muss zwischen:

* Information
* Hinweis
* Warnung
* kritischem Alarm

unterschieden werden.

⸻

## 34. Kritische Warnungen

Kritische Warnungen müssen deutlich sichtbar sein.

Sie dürfen nicht durch normale Informationen verdrängt werden.

Beispiel:

Ein niedriger Batteriestand ist wichtiger als eine normale Temperaturanzeige.

⸻

## 35. Sprache

Die Benutzeroberfläche muss grundsätzlich für Mehrsprachigkeit vorbereitet werden.

Deutsch ist die primäre Sprache.

Weitere Sprachen können später ergänzt werden.

Texte dürfen deshalb nicht fest in die Oberfläche eingebaut werden.

⸻

## 36. Einheiten

Die Darstellung von Einheiten muss zentral kontrolliert werden.

Beispiele:

* Temperatur
* Entfernung
* Geschwindigkeit
* Volumen
* Energie

Die Benutzeroberfläche darf Einheiten nicht an vielen Stellen individuell definieren.

⸻

## 37. Responsive Design

Kehler OS soll verschiedene Displaygrößen unterstützen können.

Primäres Ziel ist das zentrale Touchdisplay.

Zusätzlich soll die Architektur später unterstützen können:

* Tablet
* Smartphone
* Laptop
* weitere Displays

Die Oberfläche muss sich an die verfügbare Bildschirmgröße anpassen.

⸻

## 38. Keine klassische Website-Optik

Obwohl Kehler OS möglicherweise technisch als Webanwendung umgesetzt wird, darf es nicht wie eine gewöhnliche Website aussehen.

Der Benutzer soll das Gefühl haben, ein echtes Betriebssystem beziehungsweise Fahrzeug-HMI zu bedienen.

⸻

## 39. Designkonsistenz

Ein einmal definiertes Element muss überall gleich aussehen.

Beispiel:

Ein Button für „EIN“ darf nicht auf einer Seite anders aussehen als auf einer anderen.

Das gilt für:

* Buttons
* Schalter
* Slider
* Karten
* Überschriften
* Statusanzeigen
* Warnungen
* Dialoge

⸻

## 40. Komponentenbibliothek

Alle wiederverwendbaren UI-Komponenten sollen später zentral definiert werden.

Dadurch wird verhindert, dass Entwickler dieselbe Komponente mehrfach unterschiedlich implementieren.

⸻

## 41. Design Tokens

Farben, Abstände, Größen, Rundungen, Schatten und Typografie sollen zentral definiert werden.

Beispielsweise:

```
color.background
color.surface
color.text.primary
color.text.secondary
color.accent
color.warning
color.error
spacing.xs
spacing.sm
spacing.md
spacing.lg
radius.sm
radius.md
radius.lg
```

Die endgültige Struktur wird später festgelegt.

⸻

## 42. Keine zufälligen Werte

Entwickler dürfen nicht für jede Komponente eigene Werte erfinden.

Beispiel:

Nicht:

```
padding: 13px
```

an einer Stelle und:

```
padding: 17px
```

an einer anderen.

Stattdessen werden zentrale Designwerte verwendet.

⸻

## 43. Fehlermeldungen

Fehlermeldungen müssen verständlich sein.

Nicht:

```
Error 0x83F2
```

als einzige Information.

Stattdessen:

```
Garagentor konnte nicht geöffnet werden.
Die Steuerung antwortet nicht.
Bitte prüfen Sie die Verbindung.
```

Technische Details können zusätzlich für Administratoren verfügbar sein.

⸻

## 44. Dialoge

Dialoge sollen sparsam eingesetzt werden.

Nicht jede Aktion benötigt eine Bestätigung.

Eine Bestätigung ist sinnvoll, wenn eine Aktion:

* gefährlich
* schwer rückgängig zu machen
* sicherheitsrelevant

ist.

⸻

## 45. Benutzerführung

Kehler OS soll möglichst viele Informationen kontextbezogen anzeigen.

Wenn beispielsweise eine Batterie einen kritischen Zustand erreicht, soll nicht nur eine rote Zahl erscheinen.

Das System soll erklären:

* Was ist passiert?
* Warum ist es relevant?
* Was kann der Benutzer tun?

⸻

## 46. Professioneller Anspruch

Das Design soll nicht versuchen, möglichst futuristisch auszusehen.

„Futuristisch“ bedeutet nicht automatisch hochwertig.

Die Oberfläche soll vielmehr wirken wie ein Produkt, das tatsächlich existieren könnte.

Modern, aber glaubwürdig.

⸻

## 47. Referenzgefühl

Das visuelle Qualitätsniveau soll sich an hochwertigen technischen Produkten orientieren.

Als Inspiration können dienen:

* moderne Fahrzeug-HMIs
* Premium-Fahrzeuge
* hochwertige Industrie-HMIs
* professionelle Leitstände
* moderne Betriebssysteme

Kehler OS darf jedoch keine bestehende Benutzeroberfläche kopieren.

Es benötigt eine eigene visuelle Identität.

⸻

## 48. Logo

Kehler OS erhält eine eigene visuelle Identität und ein eigenes Logo.

Das Logo wird separat entwickelt.

Es soll später in:

* Bootscreen
* Login
* Ladebildschirm
* Systeminformationen

verwendet werden können.

⸻

## 49. Keine übermäßige Branding-Nutzung

Das Logo muss nicht auf jedem Bildschirm sichtbar sein.

Kehler OS soll sich über sein gesamtes Design identifizieren.

⸻

## 50. Designentscheidung

Wenn zwei Designlösungen möglich sind, gilt:

Die Lösung mit besserer:

1. Verständlichkeit
2. Lesbarkeit
3. Bedienbarkeit
4. visueller Konsistenz
5. Performance

hat Vorrang.

Reine Dekoration hat die niedrigste Priorität.

⸻

## 51. Zielbild

Der Benutzer soll beim ersten Start sofort verstehen:

Das ist Kehler OS.

Die Oberfläche soll eigenständig wirken.

Sie soll nicht wie:

* eine Standard-Webseite
* ein Raspberry-Pi-Projekt
* eine SPS-Visualisierung
* eine Smart-Home-App

aussehen.

⸻

## 52. Designsystem als verbindliche Grundlage

Sobald das endgültige Designsystem definiert wurde, müssen alle zukünftigen Module dieses System verwenden.

Ein neues Modul darf kein eigenes Designsystem einführen.

⸻

## Ende Kapitel 7

Dieses Kapitel definiert die Anforderungen an die visuelle Identität und das Designsystem von Kehler OS.

Die konkreten Farben, Schriftarten, Maße und Komponenten werden in späteren Kapiteln weiter spezifiziert.

Es wird weiterhin kein Code geschrieben.

Es wird weiterhin keine Software entwickelt.

Warte auf Kapitel 8.

Verwende Kapitel 1 bis 7 als gemeinsame, verbindliche Grundlage für alle folgenden Kapitel.

⸻

> Nachbemerkung aus der Übermittlung:
> Als Nächstes kommt Kapitel 8: das komplette Dashboard. Dort gehen wir erstmals
> Bildschirm für Bildschirm durch: Aufbau, Navigation, Fahrzeugdarstellung,
> Energie, Wasser, Warnungen, Statusanzeigen und Bedienlogik.
