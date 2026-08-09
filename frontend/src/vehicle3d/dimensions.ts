/**
 * Die Maße des Fahrzeugs — in Metern.
 *
 * ┌──────────────────────────────────────────────────────────────────────┐
 * │  Länge und Höhe sind ANGEGEBEN (11,5 m × 4,0 m).                     │
 * │  Alles Übrige ist aus Fotos GESCHÄTZT, nicht gemessen — siehe die     │
 * │  Kennzeichnung an den einzelnen Werten und offener Punkt K1.          │
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
  /** GESCHÄTZT — 2,55 m ist das zulässige Höchstmaß und passt zu den Fotos. */
  width: 2.55,
  /** ANGEGEBEN. */
  height: 4.0,

  /* ── Fahrgestell ────────────────────────────────────────────────────── */
  wheelRadius: 0.53,
  wheelWidth: 0.3,
  /** Vorderachse, erste und zweite Hinterachse (Tandem). GESCHÄTZT.
   *  Radstand 5,4 m, Hecküberhang 3,25 m — das entspricht dem, was die
   *  Fotos zeigen, und bleibt im üblichen Verhältnis zum Radstand. */
  axles: { front: 1.5, rear1: 6.9, rear2: 8.25 },
  /** Abstand der Reifenmitten von der Fahrzeugmitte. Hinten zwillingsbereift. */
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
