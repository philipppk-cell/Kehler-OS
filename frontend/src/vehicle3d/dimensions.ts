/**
 * Die Maße des Fahrzeugs — in Metern.
 *
 * ┌──────────────────────────────────────────────────────────────────────┐
 * │  Die Hauptmaße sind ANGEGEBEN: Länge 11,5 m, Höhe 4,0 m,             │
 * │  Breite 2,53 m, Radstand 5,88 m, Achsabstand 1,20 m,                 │
 * │  Hecküberhang 3,00 m, Reifen 315/80 R 22.5.                          │
 * │                                                                       │
 * │  Die Aufteilung des Aufbaus — Fensterlagen, Türgröße, Dachaufbauten, │
 * │  Spurweiten — ist weiterhin aus Fotos GESCHÄTZT. Jeder Wert unten     │
 * │  trägt seine Kennzeichnung einzeln.                                   │
 * └──────────────────────────────────────────────────────────────────────┘
 *
 * Grundlage: `docs/anforderungen/referenzen/fahrzeug-referenz.md`.
 *
 * Warum eine Schätzung hier vertretbar ist, obwohl Kapitel 18 §97/§98 das
 * Erfinden von Hardwaredaten verbietet: Aus diesen Zahlen wird **nichts
 * berechnet**. Keine Durchfahrtshöhe, kein Wendekreis, kein Gewicht, keine
 * Warnung. Sie erzeugen ein Bild, dessen Zweck das Wiedererkennen ist. Eine
 * um zehn Zentimeter falsche Aufbauhöhe kann zu keiner falschen Aussage über
 * das Fahrzeug führen. Eine geratene Tankkapazität dagegen schon — deshalb
 * gibt es die nach wie vor nicht.
 *
 * ── Koordinatensystem ─────────────────────────────────────────────────────
 *   X   0 an der Fahrzeugfront, wachsend nach hinten
 *   Y   0 auf dem Boden, wachsend nach oben
 *   Z   0 in der Fahrzeugmitte, **positiv zur rechten Fahrzeugseite**
 *       (Einstiegsseite mit Tür und Markise)
 */

/**
 * Unterkante des Aufbaus — zwischen den Rädern und am Heck.
 *
 * Steht außerhalb der Tabelle, weil zwei Dinge daran hängen, die gleich
 * bleiben müssen: die Unterkante des Staukastenbandes und der **Garagenboden**.
 * Die Garage ist der überhängende Heckteil und sitzt ganz unten; ihr Boden ist
 * bündig mit der Unterkante des Aufbaus. Getrennt gepflegt würden die beiden
 * Werte früher oder später auseinanderlaufen, und dann stünde die Ladekante
 * sichtbar über oder unter der Aufbaukante.
 */
const BODY_BOTTOM = 0.72;

/**
 * Unterkante des Aufbaus **über dem Tandem** — dort ist die Schürze
 * hochgezogen, damit die Räder nicht dahinter verschwinden.
 *
 * Steht ebenfalls außerhalb der Tabelle, weil die Terrasse genau aus dieser
 * Kante herausfährt: Ihr Belag liegt bündig darauf. Zwei getrennte Zahlen
 * würden bedeuten, dass die Terrasse eines Tages neben ihrem eigenen Schlitz
 * heraussteht.
 */
const SKIRT_ARCH = 1.16;

/**
 * Achslagen ab Fahrzeugfront.
 *
 * Vorgezogen, weil zwei Bauteile daran hängen statt an eigenen Zahlen: Die
 * **Eingangstür steht über der ersten Tandemachse** und die **Terrasse über
 * dem Tandem**. Beides ist auf den Fotos so zu sehen, und beides soll
 * mitwandern, falls sich eine Achslage noch einmal ändert.
 */
const AXLES = { front: 1.42, rear1: 7.3, rear2: 8.5 };

export const V = {
  /* ── Hülle ──────────────────────────────────────────────────────────── */
  /** ANGEGEBEN. */
  length: 11.5,
  /** ANGEGEBEN (2026-08-11). */
  width: 2.53,
  /** ANGEGEBEN. */
  height: 4.0,

  /* ── Fahrgestell ────────────────────────────────────────────────────── */
  /** ANGEGEBEN über die Reifengröße **315/80 R 22.5** (2026-08-11):
   *  Felge 22,5″ = 571,5 mm, Flanke 80 % von 315 mm = 252 mm,
   *  Durchmesser 571,5 + 2 × 252 = 1075,5 mm. Nicht gemessen, sondern aus
   *  der Reifenbezeichnung gerechnet — das ist der Neureifen ohne Einfederung. */
  wheelRadius: 0.538,
  /** ANGEGEBEN — Nennbreite 315 mm aus derselben Bezeichnung. */
  wheelWidth: 0.315,
  /** Vorderachse, erste und zweite Hinterachse (Tandem), gemessen ab
   *  Fahrzeugfront. ANGEGEBEN (2026-08-11) — aus diesen Maßen aufgebaut:
   *
   *    Vorderüberhang    1,42 m   GERECHNET (Rest auf die Gesamtlänge)
   *    Radstand          5,88 m   ANGEGEBEN
   *    Achsabstand       1,20 m   ANGEGEBEN
   *    Hecküberhang      3,00 m   ANGEGEBEN
   *    ─────────────────────────
   *    Gesamtlänge      11,50 m   ANGEGEBEN, geht exakt auf
   *
   *  Der Radstand wurde zunächst mit 4,80 m genannt. Damit summierten sich
   *  die Längsmaße auf 10,45 m statt 11,50 m — und rechnete man den Rest
   *  stattdessen nach vorn, hätte die Vorderachse **hinter** dem Fahrerhaus
   *  gestanden. Die Ursache waren zwei Reifenhalbmesser: 4,80 m war von
   *  Reifenkante zu Reifenkante gemessen, nicht von Radmitte zu Radmitte.
   *  Bei 315/80 R 22.5 sind das 1,08 m Unterschied. Bestätigt am 2026-08-11.
   *
   *  Der Vorderüberhang bleibt als einziger Längswert gerechnet statt
   *  gemessen. Er trägt damit jeden Fehler der übrigen vier — fällt aber mit
   *  1,42 m genau dort hin, wo ein MAN TGX ihn serienmäßig hat. */
  axles: AXLES,
  /** Abstand der Reifenmitten von der Fahrzeugmitte. Hinten zwillingsbereift.
   *  GESCHÄTZT — die Spurweiten sind nicht genannt. Sie sind so gewählt, dass
   *  die Zwillinge mit 315 mm Reifenbreite innerhalb der 2,53 m Gesamtbreite
   *  bleiben (äußere Reifenkante bei 1,21 m, Aufbaukante bei 1,265 m). */
  track: { front: 1.02, rearInner: 0.7, rearOuter: 1.05 },

  /* ── Fahrerhaus ─────────────────────────────────────────────────────── */
  cab: {
    /** Schmaler als der Aufbau — die Fotos zeigen den Überstand deutlich. */
    width: 2.35,
    rear: 2.3,
    /** Oberkante Kabinendach ohne Spoiler. */
    roof: 2.98,
    /** Oberkante des Dachspoilers, der zum Aufbau überleitet. */
    deflector: 3.55,
    /** Unterkante Stoßfänger. */
    bottom: 0.95,
    /** Frontscheibe: Fußpunkt, Dachpunkt (in der Seitenansicht). */
    screen: { bottom: [0.06, 2.02], top: [0.26, 2.9] },
  },

  /* ── Wohnaufbau ─────────────────────────────────────────────────────── */
  box: {
    front: 2.35,
    /** Unterkante des Wohnbodens. ANGEGEBEN (2026-08-11) als „ca. 1,50 m" —
     *  gemessen, aber gerundet, deshalb keine zweite Nachkommastelle.
     *
     *  Zuvor standen hier 1,85 m aus den Fotos. Die Schätzung lag um 35 cm zu
     *  hoch, und das war der größte Fehler im ganzen Modell: Der Aufbau wird
     *  dadurch von 2,15 m auf 2,50 m Höhe größer, ohne dass sich die
     *  Gesamthöhe ändert. Türunterkante und Einstiegsstufe sind mit ihren
     *  jeweiligen Abständen zum Wohnboden mitgewandert.
     *
     *  **Der Garagenboden nicht** — die Garage ist ein eigener Raum und hängt
     *  nicht am Wohnboden, siehe `garage`. */
    floor: 1.5,
    /** Die Vorderkante ist oben **abgeschrägt**, nicht gerundet: Die Front
     *  steht bis `chamferAt` senkrecht und läuft dann schräg zum Dach.
     *  So zeigt es die Drohnenaufnahme. */
    chamferAt: 3.2,
    chamferRun: 0.6,
    rearRadius: 0.18,
  },

  /* ── Staukastenband ─────────────────────────────────────────────────── */
  skirt: {
    front: 2.25,
    /** Unterkante zwischen den Rädern — dort sitzen die tiefen Staukästen. */
    bottom: BODY_BOTTOM,
    /** Unterkante über dem Tandem. Muss über der Reifenoberkante liegen,
     *  sonst verschwinden die Räder hinter der Schürze. Zugleich der
     *  Schlitz, aus dem die Terrasse herausfährt — siehe `SKIRT_ARCH`. */
    arch: SKIRT_ARCH,
  },

  /* ── Dach ───────────────────────────────────────────────────────────── */
  roof: {
    /** Solarfeld: fünf Module längs, zwei quer. */
    solar: { from: 3.25, to: 11.0, halfWidth: 1.14, cols: 5, rows: 2 },
    /** Markisen**kassette** auf der rechten Dachkante.
     *
     *  Nur die Kassette. Das ausgefahrene Tuch wird auf Wunsch des
     *  Fahrzeughalters nicht dargestellt (2026-08-12). Die Kassette bleibt,
     *  weil sie verschraubt ist und zur Silhouette gehört — auf den
     *  Drohnenaufnahmen ein dunkler Balken über die ganze Dachlänge. */
    awning: { from: 3.4, to: 10.9, depth: 0.22, drop: 0.2 },
  },

  /* ── Öffnungen ──────────────────────────────────────────────────────── */

  /** Eingangstür, rechte Seite. Die Unterkante ist die Schwelle und liegt
   *  damit auf dem Wohnboden (`box.floor` + 0,03 m Rahmen).
   *
   *  **Die Tür steht über der ersten Tandemachse** (Fotos vom 2026-08-12).
   *  Sie saß zuvor bei 4,50 m, also im vorderen Drittel — das war aus den
   *  ersten Gegenlichtaufnahmen der rechten Seite falsch abgelesen. `x` ist
   *  die Anschlagkante, deshalb die halbe Blattbreite davor. */
  door: { x: AXLES.rear1 - 0.43, width: 0.85, bottom: 1.53, top: 3.72 },

  /** Heckklappe, oben angeschlagen. `bottom` ist der Garagenboden.
   *
   *  **Die Garage ist ein eigener Raum**, nicht der hintere Teil des
   *  Wohnbereichs (ANGEGEBEN 2026-08-11). Sie ist der überhängende Heckteil
   *  und sitzt ganz unten: Der Boden ist bündig mit der Unterkante des
   *  Aufbaus, die Raumhöhe beträgt ca. 1,65 m. Daraus folgt die Oberkante
   *  der Öffnung: 0,72 + 1,65 = 2,37 m.
   *
   *  Zuvor stand hier eine Öffnung von 1,90 m bis 3,72 m — aus den Fotos als
   *  „nahezu volle Höhe der Heckwand" gelesen und an den Wohnboden gekoppelt.
   *  Beides war falsch. Die Drohnenaufnahme zeigt die Klappe waagerecht
   *  abstehend; in dieser Stellung ist ihre Höhe nicht abzuschätzen, und die
   *  Schätzung ist zu groß ausgefallen. Die Klappe nimmt gut die Hälfte der
   *  Heckwand ein, nicht deren volle Höhe.
   *
   *  `halfWidth` bleibt GESCHÄTZT — die Breite ist nicht genannt. */
  garage: { bottom: BODY_BOTTOM, top: 2.37, halfWidth: 1.08 },

  /**
   * Die ausfahrbare **Terrasse** über dem Tandem, rechte Seite.
   *
   * Hier stand zuvor eine `step`-Größe: eine einzelne Einstiegsstufe von
   * 0,70 × 0,34 m unter der Tür. Das war falsch verstanden. Was das Fahrzeug
   * wirklich hat, ist eine Plattform mit Holzbelag über beiden Tandemrädern,
   * mit einer Außenschürze, in die zwei Radbögen geschnitten sind, und einer
   * Treppe, die darunter hervorkommt.
   *
   * **Ausgefahren ist es ein Teil, eingefahren ist nichts zu sehen.** Der
   * Fahrzeughalter hat beides fotografiert: Eingefahren ist die Flanke glatt
   * und die Tandemräder stehen frei. Die Schürze mit den Radbögen ist also
   * nicht etwa eine feste Verkleidung, sondern die Außenhaut der Terrasse.
   *
   * **Terrasse und Treppe sind ein Zustand**, nicht zwei — sie fahren
   * gemeinsam. Die Treppe hat **keinen Handlauf**.
   */
  terrace: {
    /** Längsausdehnung, an den Tandemachsen verankert: knapp 0,3 m Schürze
     *  über die Radbögen hinaus, wie es die Fotos zeigen. */
    from: AXLES.rear1 - 0.85,
    to: AXLES.rear2 + 0.85,
    /** Tiefe, um die Belag und Schürze aus der Flanke herausfahren. */
    depth: 0.85,
    /** Oberkante des Belags — bündig mit der Schürzenkante über dem Tandem,
     *  aus der die Terrasse herauskommt. */
    deck: SKIRT_ARCH,
    /** Unterkante der Außenschürze, zwischen und neben den Radbögen. */
    apron: 0.2,
    /** Radbögen in der Schürze. Der Halbmesser muss über dem Reifen
     *  (0,538 m) liegen und darf zugleich den schmalen Steg zwischen den
     *  beiden Bögen nicht auffressen — bei 1,20 m Achsabstand bleiben davon
     *  ohnehin nur 8 cm. `springLine` ist die Kämpferhöhe, ab der der Bogen
     *  rund wird; darüber bleibt bis zum Belag nur ein schmaler Rand, und
     *  genau so sieht es auf den Fotos aus. */
    archRadius: 0.56,
    archSpringLine: 0.56,
    /** Treppe unter dem Belag, fällt nach vorn ab. GESCHÄTZT — auf den Fotos
     *  sind fünf Stufen zu zählen, die Maße sind daraus abgeleitet. */
    stairs: { count: 5, width: 0.62, going: 0.26 },
  },

  /** Fenster je Seite: [x, Unterkante, Breite, Höhe].
   *
   *  Sie sitzen tiefer und sind größer, als eine erste Auswertung der
   *  Sonnenfotos ergeben hatte — die Drohnenaufnahme zeigt sie im mittleren
   *  Drittel der Aufbauhöhe, nicht direkt unter dem Dach. */
  windows: {
    left: [
      [3.35, 2.66, 1.45, 0.52],
      [5.3, 2.54, 1.3, 0.52],
      [7.15, 2.68, 0.52, 0.52],
      [8.5, 2.58, 1.55, 0.58],
    ],
    /** Rechts nach der freistehenden Aufnahme vom 2026-08-12 nachgezogen:
     *  ein breites Fenster im vorderen Drittel, ein zweites hinter der Tür.
     *  Zwischen Tür und Heckfenster bleibt eine große geschlossene Fläche —
     *  die Tür sitzt jetzt bei 6,87 m und nicht mehr bei 4,50 m. */
    right: [
      [3.8, 2.6, 1.6, 0.55],
      [9.25, 2.6, 1.35, 0.55],
    ],
  },
} as const;

/** Mittelpunkt, um den sich die Ansicht dreht. */
export const PIVOT = { x: V.length / 2, y: V.height / 2, z: 0 };
