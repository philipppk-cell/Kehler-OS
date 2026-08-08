# Widersprüche, Unschärfen und offene Entscheidungen

Ergebnis der Analyse der Kapitel 1–18 (Phase 1, Kapitel 18 §134.3).

Es geht hier ausschließlich um Punkte **innerhalb der Spezifikation**. Fehlende
reale Hardwaredaten stehen getrennt in
[`../OPEN_HARDWARE_REQUIREMENTS.md`](../OPEN_HARDWARE_REQUIREMENTS.md).

---

## W1 – Die Modullisten der Kapitel 2, 4, 8/9 und 18 stimmen nicht überein

| Quelle | Auffälligkeit |
| --- | --- |
| Kapitel 2 §4 | 19 Module, darunter **Heizung**, **Navigation**, **Sicherheit**, **Wartung**, **Automatisierungen**, **KI-Assistent** |
| Kapitel 4 §4 | Heizung entfällt, **Einstellungen** kommt hinzu |
| Kapitel 8 §21 / Kapitel 18 §17 | 10 Navigationspunkte, ohne Navigation, Sicherheit und Wartung; Kapitel 18 ergänzt **Diagnose** und **Automatisierungen** |

**Auflösung:** Maßgeblich ist die Liste aus Kapitel 18 §17, weil sie die
jüngste und im Entwicklungsauftrag verbindliche ist.

- **Heizung** ist keine eigene Seite, sondern Teil von *Klima* — so zeigt es
  auch die Designreferenz (Heizung/Lüfter als Schaltflächen der Klima-Karte).
- **Sicherheit** und **Wartung** werden nicht als Hauptnavigationspunkte
  geführt. Ihre Inhalte erscheinen dort, wo sie gebraucht werden: Sicherheit als
  aggregierter Status auf dem Dashboard und in Fahrzeug/Diagnose, Wartung in
  einem eigenen Bereich unter Einstellungen.
- **Navigation** (im Sinne von Kartenführung) wird zurückgestellt. Sie ist in
  keinem späteren Kapitel weiter ausgeführt, benötigt Kartendaten und
  Standortdaten, die laut Kapitel 15 §85 derzeit nicht vorausgesetzt sind.
- **KI-Assistent** ist laut Kapitel 18 §113/§117 ausdrücklich letzte Ebene.

**Status:** entschieden, dokumentiert. Rückfrage nur nötig, falls Navigation
oder ein eigener Sicherheitsbereich doch zur ersten Version gehören sollen.

---

## W2 – „Keine SPS-Adressen sichtbar“ gegen „Hardware-Mapping in der Diagnose“

Kapitel 5 §7 und Kapitel 18 §8 verbieten Hardwareadressen in der Oberfläche.
Kapitel 12 §51 und Kapitel 16 §51 verlangen, dass im Diagnose- und
Servicebereich nachvollziehbar ist, welche logische Funktion auf welchem
Datenpunkt liegt.

**Auflösung:** Kein echter Widerspruch, sondern eine Berechtigungsgrenze. Die
*normale* Oberfläche kennt ausschließlich semantische IDs. Der Diagnosebereich
ist eine getrennte, administratorpflichtige Fläche (Kapitel 16 §42,
Kapitel 15 §7). Technisch wird das durchgesetzt, indem Mapping-Informationen
nur über einen eigenen, berechtigungsgeprüften Endpunkt ausgeliefert werden —
sie sind nicht Teil des allgemeinen State-Snapshots.

**Status:** entschieden.

---

## W3 – Fahrzeugvisualisierung: animiert, aber nicht bedienbar

Kapitel 8 §5 verlangt zustandsabhängige Animation von Türen, Garage, Stufen,
Markise und Nivellierung. Kapitel 8 §6 verbietet, das Fahrzeugbild zur
Bedienfläche zu machen. Kapitel 8 §29 nennt es „primär visuelle
Statusdarstellung“.

**Auflösung:** Die Visualisierung ist ausschließlich Ausgabe. Sie nimmt keine
Berührungen entgegen. Gesteuert wird über Schnellzugriffe und die Fachseiten.

Eine bewusst getroffene Ausnahme, die die Regel nicht verletzt: Ein Tippen auf
einen Fahrzeugbereich *kann* zur zugehörigen Fachseite navigieren. Das ist
Navigation, keine Steuerung — es bewegt nichts. Ob das eingebaut wird,
entscheidet sich in Phase 5 anhand der tatsächlichen Bedienqualität.

**Status:** entschieden, Detail offen bis Phase 5.

---

## W4 – Widersprüchliche Werte in der Designreferenz

Im Referenzbild zeigt die Wasser-Karte bei Grauwasser nebeneinander `65 %` und
`85 %`; die Warnung nennt `85 %`. Bei Frischwasser steht zweimal `64 %`.

**Auflösung:** Montageartefakt der Bildvorlage, keine Anforderung. Die
Kartendarstellung führt je Tank **genau einen** Prozentwert und **eine**
Literangabe (Kapitel 18 §27). Bereits in
[`../anforderungen/referenzen/dashboard-referenz.md`](../anforderungen/referenzen/dashboard-referenz.md)
vermerkt.

**Status:** geklärt.

---

## W5 – Verhalten bei manuellem Eingriff in eine aktive Automatisierung

Kapitel 14 §39 stellt die Frage ausdrücklich und lässt sie offen: Wenn eine
Automatisierung „Außenlicht AUS“ vorsieht und der Benutzer es einschaltet —
greift die Automatisierung sofort wieder ein oder hat der manuelle Befehl
Vorrang? Kapitel 14 §40 verbietet zugleich grundloses Gegenschalten.

**Vorschlag zur Entscheidung:** Ein manueller Befehl setzt auf der betroffenen
Entity eine zeitlich begrenzte **manuelle Übersteuerung** (Vorgabe: bis zum
nächsten Moduswechsel, längstens eine konfigurierbare Dauer). Komfortregeln
respektieren sie; Sicherheits- und Systemregeln übersteuern sie weiterhin
(Kapitel 14 §95). Die Übersteuerung ist in der Oberfläche sichtbar und
jederzeit aufhebbar — damit ist das Verhalten transparent im Sinne von §40.

**Status:** offen. Wird vor Phase 7 (Automation Engine) benötigt, blockiert die
vorherigen Phasen nicht.

---

## W6 – Bottom Navigation

Die Designreferenz zeigt eine Leiste am unteren Rand. Kapitel 8 §29 und
Kapitel 18 §21 stellen ausdrücklich klar, dass ihre Verwendung noch nicht
entschieden ist und sie nicht als verbindliche Hauptnavigation zu behandeln ist.

**Auflösung:** Die linke Spalte ist die einzige Hauptnavigation. Die Shell wird
so gebaut, dass eine untere Leiste später ohne Umbau ergänzt werden kann. Auf
kleinen Displays kann eine untere Leiste die linke Spalte ersetzen — dort ist
sie eine responsive Anpassung, keine zweite Informationsarchitektur.

**Status:** entschieden für die erste Version, endgültige Entscheidung offen.

---

## W7 – Kein universeller Fail-Safe-Zustand

Kapitel 15 §61 verbietet die Annahme „bei Fehler alles AUS“, weil AUS bei
manchen Systemen selbst problematisch sein kann. Kapitel 15 §62 verlangt
stattdessen eine Definition pro Gerät.

**Auflösung:** Das Verhalten bei Kommunikationsverlust, SPS-Neustart,
Pi-Ausfall, Sensorfehler und Stromausfall wird **je Gerät in der Konfiguration**
hinterlegt. Kehler OS trifft keine pauschale Annahme.

**Wichtig:** Der Fail-Safe-Zustand eines Aktors wird ganz überwiegend von der
**SPS** bestimmt, nicht von Kehler OS — bei Ausfall des Pi ist Kehler OS gar
nicht mehr beteiligt. Die Konfiguration hält deshalb fest, *was die SPS tut*,
damit die Diagnose es korrekt darstellen kann. Solange das nicht bestätigt ist
(offener Punkt A5), gilt es als unbekannt und wird als solches angezeigt.

**Status:** Architektur entschieden, Inhalte hängen an A5.

---

## W8 – Erwartung an die Reaktionszeit ist nicht beziffert

Kapitel 17 §4 verlangt „praktisch unmittelbar“, Kapitel 17 §93 verlangt
messbare Performance-Budgets, nennt aber keine Zahlen und überlässt sie
ausdrücklich der gewählten Architektur.

**Vorschlag als Ausgangswert** (wird in Phase 2 gemessen und dann verbindlich
festgeschrieben):

| Vorgang | Ziel |
| --- | --- |
| visuelle Reaktion auf Berührung | < 100 ms |
| Befehl abgesetzt bis Rückmeldung „wird ausgeführt“ | < 150 ms |
| Zustandsänderung Hardware → sichtbar im Client | < 300 ms |
| Seitenwechsel | < 200 ms |
| Kaltstart bis bedienbares Dashboard | < 15 s |

**Status:** Vorschlag, Bestätigung durch Messung in Phase 2.

---

## W9 – Umfang der ersten Version ist nicht abgegrenzt

Die Spezifikation beschreibt das Zielsystem über Jahre, benennt aber keinen
Lieferumfang für eine erste produktive Version. Kapitel 18 §130 gibt Meilensteine
vor, ohne den Schnitt zu setzen.

**Vorschlag:** Als „Version 1.0 produktiv“ gilt der Stand, an dem Dashboard,
Licht, Energie, Wasser, Klima, Fahrzeug, Garage, Einstellungen und Diagnose
mit **realer** SPS- und Victron-Anbindung laufen, Automatisierungen und Szenen
verfügbar sind und Backup/Restore erprobt ist. Nivellierung, Kameras und KI
folgen danach.

**Status:** offen, Vorschlag in [`../ROADMAP.md`](../ROADMAP.md) abgebildet.

---

## Bewusst von der Spezifikation offen gelassen

Diese Punkte sind keine Widersprüche, sondern ausdrücklich vertagte
Entscheidungen. Sie werden hier geführt, damit sie nicht übersehen werden:

| Thema | Vertagt in | Fällig |
| --- | --- | --- |
| Endgültige Rollenstruktur über ADMIN/USER hinaus | Kapitel 6 §12 | Phase 8 |
| Aufbewahrungsfristen je Datenart | Kapitel 6 §23, Kapitel 16 §77 | Phase 2 (Vorgaben), laufend anpassbar |
| Fahrzeugmodi: endgültige Liste | Kapitel 13 §56, Kapitel 14 §31 | Phase 7 |
| Einstufung der Funktionen nach Risikoklasse | Kapitel 15 §21 | vor Phase 9 |
| Konkrete Remote-Zugriffslösung | Kapitel 15 §38 | nach Version 1.0 |
| Lokale KI oder Cloud-KI | Kapitel 18 §116 | letzte Phase |
| Versionierungsschema | Kapitel 17 §53 | Phase 2 — Vorschlag: Semantic Versioning |
