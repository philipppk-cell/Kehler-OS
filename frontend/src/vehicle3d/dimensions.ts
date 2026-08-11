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
  axles: { front: 1.42, rear1: 7.3, rear2: 8.5 },
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
    /** Unterkante des Wohnbodens. */
    floor: 1.85,
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
    bottom: 0.72,
    /** Unterkante über dem Tandem. Muss über der Reifenoberkante liegen,
     *  sonst verschwinden die Räder hinter der Schürze. */
    arch: 1.16,
  },

  /* ── Dach ───────────────────────────────────────────────────────────── */
  roof: {
    /** Solarfeld: fünf Module längs, zwei quer. */
    solar: { from: 3.25, to: 11.0, halfWidth: 1.14, cols: 5, rows: 2 },
    /** Markisenkassette auf der rechten Dachkante. */
    awning: { from: 3.4, to: 10.9, depth: 0.22, drop: 0.2 },
  },

  /* ── Öffnungen ──────────────────────────────────────────────────────── */

  /** Eingangstür, rechte Seite. */
  door: { x: 4.5, width: 0.85, bottom: 1.88, top: 3.72 },

  /** Zwei Heckflügeltüren, außen angeschlagen. */
  garage: { bottom: 1.9, top: 3.72, halfWidth: 1.08 },

  /** Einstiegsstufe unter der Tür. */
  step: { x: 4.6, width: 0.7, depth: 0.34, height: 1.42 },

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
    right: [
      [3.25, 2.62, 1.25, 0.52],
      [9.2, 2.62, 1.15, 0.52],
    ],
  },
} as const;

/** Mittelpunkt, um den sich die Ansicht dreht. */
export const PIVOT = { x: V.length / 2, y: V.height / 2, z: 0 };
