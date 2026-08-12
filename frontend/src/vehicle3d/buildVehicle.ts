/**
 * Der Aufbau des Fahrzeugmodells.
 *
 * Das Fahrzeug ist im Wesentlichen ein Körper mit konstantem Querschnitt.
 * Deshalb entsteht es hier nicht aus Einzelquadern, sondern aus **Seitenprofilen,
 * die in die Breite gezogen werden** (`ExtrudeGeometry`). Das ist genau die
 * Form, die die Fotos zeigen, kostet wenig Dreiecke und lässt sich mit den
 * Zahlen aus `dimensions.ts` unmittelbar nachvollziehen.
 *
 * **Bewegliche Teile werden getrennt gehalten.** Sie kennen dieselben vier
 * Zustände wie die SVG-Ansicht:
 *
 *   closed / open / moving   → echte, gemeldete Stellung
 *   unknown                  → Stellung nicht bekannt. Das Teil bleibt an der
 *                              geschlossenen Position, wird aber sichtbar als
 *                              unbestimmt gekennzeichnet und **nicht bewegt**
 *                              (Kapitel 18 §106).
 *   absent                   → keine Hardwarezuordnung. Das Teil wird gar
 *                              nicht erzeugt (Kapitel 18 §101).
 *
 * **Die Markise wird nicht dargestellt** — so vom Fahrzeughalter entschieden
 * (2026-08-12). Die Kassette bleibt, denn sie ist am Fahrzeug verschraubt und
 * gehört zur Silhouette; nur das ausgefahrene Tuch entfällt. Die Markise
 * bleibt dabei bedienbar, sie wird lediglich nicht gezeigt — und zwar in
 * **beiden** Ansichten, damit SVG und 3D dasselbe Fahrzeug zeigen (ADR 0008).
 */

import {
  BoxGeometry,
  BufferGeometry,
  CanvasTexture,
  CylinderGeometry,
  ExtrudeGeometry,
  Group,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  PlaneGeometry,
  Shape,
  type Material,
} from "three";

import { V } from "./dimensions";
import type { Part } from "../vehicle/VehicleView";

export interface VehicleState {
  garage: Part;
  door: Part;
  terrace: Part;
}

export interface VehicleModel {
  root: Group;
  /** Setzt die Zielstellungen. Die Bewegung dorthin macht `update`. */
  setState(state: VehicleState): void;
  /** Führt die Teile weiter. Gibt zurück, ob sich noch etwas bewegt. */
  update(dt: number): boolean;
  /** Springt sofort auf die Zielstellungen (für reduzierte Bewegung). */
  settle(): void;
  dispose(): void;
}

/* ── Werkstoffe ────────────────────────────────────────────────────────── */

/**
 * Der Lack ist **grau, nicht weiß**.
 *
 * Die ersten Fotos entstanden in praller Sonne; dort wirkt der Aufbau
 * ausgebrannt hell. Die Drohnenaufnahme mit Umgebung zeigt die tatsächliche
 * Farbe: ein mittleres Grau mit leichtem Blaustich, Fahrerhaus und Aufbau
 * gleich lackiert.
 *
 * Der Wert hier ist die Grundfarbe, nicht die Bildfarbe — Licht und
 * Tonwertabbildung heben ihn beim Rendern an.
 */
const MATERIALS = {
  paint: new MeshStandardMaterial({ color: 0x6d7982, roughness: 0.22, metalness: 0.06 }),
  paintDark: new MeshStandardMaterial({ color: 0x5e6a72, roughness: 0.28, metalness: 0.06 }),
  // Fast vollständig spiegelnd. Eine Scheibe ist keine schwarze Fläche —
  // sie zeigt den Himmel. Ohne das wird die Fahrzeugfront eine dunkle Maske.
  glass: new MeshStandardMaterial({ color: 0x131c23, roughness: 0.05, metalness: 0.95 }),
  trim: new MeshStandardMaterial({ color: 0x191e23, roughness: 0.55, metalness: 0.1 }),
  tyre: new MeshStandardMaterial({ color: 0x0f1215, roughness: 0.92, metalness: 0.0 }),
  rim: new MeshStandardMaterial({ color: 0x2b3238, roughness: 0.45, metalness: 0.65 }),
  solar: new MeshStandardMaterial({ color: 0x0d1620, roughness: 0.22, metalness: 0.35 }),
  lamp: new MeshStandardMaterial({ color: 0x5a1418, roughness: 0.35, emissive: 0x220608 }),
  /** Der Holzbelag der Terrasse — verwittertes Graubraun, matt. */
  wood: new MeshStandardMaterial({ color: 0x8a7f6d, roughness: 0.82, metalness: 0 }),
  /** Die Treppenstufen unter der Terrasse: helles Leichtmetall. */
  alu: new MeshStandardMaterial({ color: 0x9aa3ab, roughness: 0.4, metalness: 0.6 }),
};

/**
 * Kennzeichnung für „Stellung unbekannt".
 *
 * In der SVG-Ansicht wird ein unbekanntes Teil gestrichelt gezeichnet. In 3D
 * gibt es keine Strichelung, deshalb hier das räumliche Gegenstück: Das Teil
 * wird durchscheinend und leuchtet schwach in der Unbekannt-Farbe. Es sieht
 * damit erkennbar anders aus als jedes gemeldete Teil — und das ist der Zweck.
 */
const UNKNOWN_MATERIAL = new MeshStandardMaterial({
  color: 0x7d8894,
  roughness: 0.5,
  metalness: 0,
  transparent: true,
  opacity: 0.32,
  emissive: 0x2b3d47,
});

/* ── Hilfsformen ───────────────────────────────────────────────────────── */

/** Zieht ein Seitenprofil (XY) auf die gewünschte Breite und zentriert es. */
function extrude(shape: Shape, width: number, bevel = 0.025): BufferGeometry {
  const geometry = new ExtrudeGeometry(shape, {
    depth: width - 2 * bevel,
    bevelEnabled: true,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 1,
    curveSegments: 10,
  });
  // ExtrudeGeometry wächst von z = 0 nach vorn; wir wollen mittig sitzen.
  geometry.translate(0, 0, -width / 2 + bevel);
  return geometry;
}

function panel(w: number, h: number, d: number, material: Material): Mesh {
  return new Mesh(new BoxGeometry(w, h, d), material);
}

/* ── Aufbau ────────────────────────────────────────────────────────────── */

/**
 * Der Aufbau **mitsamt der Nase über dem Fahrerhaus** — ein einziges Profil.
 *
 * Zuvor waren das drei Teile: ein Kasten mit gerader Abschrägung, ein
 * aufgesetzter Dachspoiler und eine Blende dazwischen. Zusammen ergaben sie
 * genau das, was die Fotos **nicht** zeigen: Stufen und Fugen zwischen
 * Fahrerhaus und Aufbau. In Wirklichkeit ist es ein durchgehender Körper, der
 * über das Fahrerhaus nach vorn kragt, auf dessen Dach aufsetzt und in einem
 * weichen Bogen zum Dach ansteigt.
 *
 * Aus einem Profil gezogen gibt es diese Fugen gar nicht erst — die
 * Verbindung ist keine Frage sorgfältigen Aneinanderlegens mehr, sondern
 * folgt aus der Form.
 */
function buildHull(): Mesh {
  const { box, length, height, width } = V;
  const { nose } = box;
  const s = new Shape();

  // Aufbaufront, senkrecht bis zum Ansatz der Nase.
  s.moveTo(box.front, box.floor);
  s.lineTo(box.front, nose.front);
  // Unterseite der Nase: läuft nach vorn aus und setzt auf dem Kabinendach auf.
  s.quadraticCurveTo(box.front, nose.tipTop - 0.14, box.front - 0.4, nose.tipTop - 0.12);
  s.lineTo(nose.tip + 0.1, nose.tipTop - 0.12);
  s.quadraticCurveTo(nose.tip, nose.tipTop - 0.12, nose.tip, nose.tipTop);
  // Ansteigender Bogen von der Nasenspitze auf Dachhöhe. Das ist die Linie,
  // die auf den Seitenaufnahmen den Übergang bildet.
  s.quadraticCurveTo(nose.crest - 0.75, nose.tipTop + 0.5, nose.crest, height);
  // Dach bis zur gerundeten Heckkante.
  s.lineTo(length - box.rearRadius, height);
  s.quadraticCurveTo(length, height, length, height - box.rearRadius);
  s.lineTo(length, box.floor);
  s.closePath();

  return new Mesh(extrude(s, width), MATERIALS.paint);
}

function buildSkirt(): Mesh {
  const { skirt, length, box, width, axles, wheelRadius } = V;
  const tandemFrom = axles.rear1 - wheelRadius - 0.5;
  const tandemTo = axles.rear2 + wheelRadius + 0.5;
  const s = new Shape();

  s.moveTo(skirt.front, box.floor);
  s.lineTo(skirt.front, skirt.bottom);
  s.lineTo(tandemFrom - 0.18, skirt.bottom);
  s.quadraticCurveTo(tandemFrom, skirt.bottom, tandemFrom, skirt.arch);
  s.lineTo(tandemTo, skirt.arch);
  s.quadraticCurveTo(tandemTo, skirt.bottom, tandemTo + 0.18, skirt.bottom);
  s.lineTo(length, skirt.bottom);
  s.lineTo(length, box.floor);
  s.closePath();

  // Etwas schmaler als der Aufbau — die Fotos zeigen eine deutliche Kante.
  return new Mesh(extrude(s, width - 0.09), MATERIALS.paint);
}

function buildCab(): Mesh {
  const { cab, axles, wheelRadius } = V;
  const arch = { from: axles.front - wheelRadius - 0.1, to: axles.front + wheelRadius + 0.1 };
  const [sx, sy] = cab.screen.bottom;
  const [tx, ty] = cab.screen.top;
  const s = new Shape();

  // Ein TGX-Fahrerhaus ist kantig, kein Keil: fast senkrechte Front, nur
  // leicht geneigte Scheibe, flaches Dach.
  s.moveTo(0.16, cab.bottom);
  s.lineTo(sx, 1.42);
  s.lineTo(sx, sy);
  s.lineTo(tx, ty);
  s.quadraticCurveTo(tx + 0.03, cab.roof, tx + 0.2, cab.roof);
  s.lineTo(cab.rear, cab.roof);
  s.lineTo(cab.rear, cab.bottom);
  // Zurück entlang der Unterkante, mit Radlauf über der Vorderachse.
  s.lineTo(arch.to + 0.14, cab.bottom);
  s.quadraticCurveTo(arch.to, cab.bottom, arch.to, 1.2);
  s.lineTo(arch.from, 1.2);
  s.quadraticCurveTo(arch.from, cab.bottom, arch.from - 0.14, cab.bottom);
  s.closePath();

  return new Mesh(extrude(s, cab.width), MATERIALS.paint);
}


/**
 * Front des Fahrerhauses: Scheibe, Grill, Scheinwerfer, Spiegel.
 *
 * Die Frontscheibe liegt schräg. Statt die Neigung in eine Form zu rechnen,
 * wird eine dünne Platte um genau den Winkel gedreht, den die beiden
 * Scheibenpunkte aus der Maßtabelle aufspannen — dadurch bleibt sie
 * automatisch bündig, wenn die Maße korrigiert werden.
 */
function buildCabFront(): Group {
  const g = new Group();
  const { cab } = V;
  const [sx, sy] = cab.screen.bottom;
  const [tx, ty] = cab.screen.top;

  const dx = tx - sx;
  const dy = ty - sy;
  const rake = Math.atan2(dx, dy);
  const length = Math.hypot(dx, dy);

  const screen = panel(0.05, length - 0.06, cab.width - 0.2, MATERIALS.glass);
  screen.rotation.z = -rake;
  // Ein Stück entlang der Flächennormalen nach vorn, damit sie aufliegt.
  screen.position.set(
    (sx + tx) / 2 - Math.cos(rake) * 0.022,
    (sy + ty) / 2 - Math.sin(rake) * 0.022,
    0,
  );
  g.add(screen);

  // Kühlergrill — auf den Fotos ein schmales Band mit viel Lack ringsum.
  const grille = panel(0.05, 0.22, cab.width - 1.05, MATERIALS.trim);
  grille.position.set(sx - 0.01, 1.72, 0);
  g.add(grille);

  // Scheinwerfer in den unteren Ecken
  for (const side of [-1, 1]) {
    const lamp = panel(0.05, 0.18, 0.34, MATERIALS.glass);
    lamp.position.set(sx - 0.01, 1.22, side * (cab.width / 2 - 0.32));
    g.add(lamp);
  }

  // Außenspiegel — auf den Fotos markant und für das Wiedererkennen wichtig.
  for (const side of [-1, 1]) {
    const arm = panel(0.05, 0.05, 0.2, MATERIALS.trim);
    arm.position.set(0.5, 2.6, side * (cab.width / 2 + 0.1));
    g.add(arm);

    const glass = panel(0.07, 0.56, 0.22, MATERIALS.trim);
    glass.position.set(0.5, 2.3, side * (cab.width / 2 + 0.2));
    g.add(glass);
  }

  // Seitenfenster der Fahrerhaustüren. Ohne sie ist das Fahrerhaus von der
  // Seite ein Klotz — auf jeder Seitenaufnahme ist es das auffälligste
  // Merkmal der Kabine.
  for (const side of [-1, 1]) {
    const pane = new Mesh(
      extrude(roundedRect(1.02, 0.66, 0.1), 0.05, 0.012),
      MATERIALS.glass,
    );
    pane.position.set(1.28, 2.34, side * (cab.width / 2 - 0.015));
    g.add(pane);

    // Türfuge, damit die Kabinentür als solche lesbar ist.
    const seam = panel(0.03, 1.24, 0.03, MATERIALS.trim);
    seam.position.set(1.86, 1.86, side * (cab.width / 2 - 0.01));
    g.add(seam);
  }

  return g;
}

function buildWheels(): Group {
  const g = new Group();
  const { axles, wheelRadius, wheelWidth, track } = V;

  const tyre = new CylinderGeometry(wheelRadius, wheelRadius, wheelWidth, 22);
  tyre.rotateX(Math.PI / 2);
  const rim = new CylinderGeometry(wheelRadius * 0.52, wheelRadius * 0.52, wheelWidth + 0.03, 14);
  rim.rotateX(Math.PI / 2);

  const place = (x: number, z: number) => {
    const wheel = new Mesh(tyre, MATERIALS.tyre);
    wheel.position.set(x, wheelRadius, z);
    g.add(wheel);
    const hub = new Mesh(rim, MATERIALS.rim);
    hub.position.set(x, wheelRadius, z * 1.03);
    g.add(hub);
  };

  // Vorderachse einzeln, Tandem zwillingsbereift.
  for (const side of [-1, 1]) {
    place(axles.front, side * track.front);
    for (const x of [axles.rear1, axles.rear2]) {
      place(x, side * track.rearInner);
      place(x, side * track.rearOuter);
    }
  }
  return g;
}

/**
 * Die Fugen.
 *
 * Weißer Lack vor dunklem Hintergrund verliert ohne sie seine Form: Aufbau,
 * Schürze und Fahrerhaus verschmelzen zu einem Klumpen. Diese schmalen
 * dunklen Streifen sitzen dort, wo das Fahrzeug real geteilt ist, und geben
 * den Volumen ihre Kanten zurück.
 */
function buildSeams(): Group {
  const g = new Group();
  const { box, length, width, skirt, cab } = V;

  // Fuge zwischen Wohnaufbau und Staukastenband
  const floor = panel(length - skirt.front, 0.045, width + 0.012, MATERIALS.trim);
  floor.position.set((skirt.front + length) / 2, box.floor, 0);
  g.add(floor);

  // Spalt zwischen Fahrerhaus und Aufbaufront
  const gap = panel(0.05, cab.roof - box.floor, cab.width - 0.06, MATERIALS.trim);
  gap.position.set(cab.rear + 0.02, (box.floor + cab.roof) / 2, 0);
  g.add(gap);

  return g;
}

function buildUnderbody(): Mesh {
  // Ein dunkler Block, damit man unter dem Fahrzeug nicht hindurchsieht.
  // Er bleibt vollständig hinter der Schürze — sonst hängt unter dem
  // Fahrzeug eine schwarze Platte in der Luft.
  const { length, skirt, box, width } = V;
  const height = box.floor - skirt.bottom;
  const mesh = panel(length - 1.2, height, width - 0.5, MATERIALS.trim);
  mesh.position.set(length / 2 + 0.3, skirt.bottom + height / 2, 0);
  return mesh;
}

/** Ein Fenster: x, Unterkante, Breite, Höhe. */
type Window = readonly [number, number, number, number];

/**
 * Rechteck mit gerundeten Ecken, liegend in der XY-Ebene.
 *
 * `rTop` gilt für die beiden oberen Ecken. Fehlt `rBottom`, sind alle vier
 * gleich — bei der Heckklappe sind die unteren aber deutlich runder als die
 * oberen, und genau das macht ihre Form auf dem Heckfoto aus.
 */
function roundedRect(w: number, h: number, rTop: number, rBottom = rTop): Shape {
  const s = new Shape();
  const x = -w / 2;
  const y = -h / 2;
  s.moveTo(x + rBottom, y);
  s.lineTo(x + w - rBottom, y);
  s.quadraticCurveTo(x + w, y, x + w, y + rBottom);
  s.lineTo(x + w, y + h - rTop);
  s.quadraticCurveTo(x + w, y + h, x + w - rTop, y + h);
  s.lineTo(x + rTop, y + h);
  s.quadraticCurveTo(x, y + h, x, y + h - rTop);
  s.lineTo(x, y + rBottom);
  s.quadraticCurveTo(x, y, x + rBottom, y);
  return s;
}

function buildWindows(): Group {
  const g = new Group();
  const z = V.width / 2;

  // Die Fotos zeigen kräftige dunkle Rahmen mit deutlich gerundeten Ecken —
  // sie sind das auffälligste Merkmal der Seitenansicht.
  const add = (list: readonly Window[], side: number) => {
    for (const [x, y, w, h] of list) {
      const cx = x + w / 2;
      const cy = y + h / 2;

      const frame = new Mesh(
        new ExtrudeGeometry(roundedRect(w + 0.11, h + 0.11, 0.1), {
          depth: 0.035,
          bevelEnabled: false,
          curveSegments: 5,
        }),
        MATERIALS.trim,
      );
      frame.position.set(cx, cy, side * (z + 0.035));
      frame.rotation.y = side > 0 ? 0 : Math.PI;
      g.add(frame);

      const glass = new Mesh(
        new ExtrudeGeometry(roundedRect(w, h, 0.07), {
          depth: 0.03,
          bevelEnabled: false,
          curveSegments: 5,
        }),
        MATERIALS.glass,
      );
      glass.position.set(cx, cy, side * (z + 0.045));
      glass.rotation.y = side > 0 ? 0 : Math.PI;
      g.add(glass);
    }
  };

  add(V.windows.left, -1);
  add(V.windows.right, 1);
  return g;
}

function buildRoof(): Group {
  const g = new Group();
  const { solar, awning } = V.roof;

  // Solarfeld
  const spanX = (solar.to - solar.from) / solar.cols;
  const spanZ = (solar.halfWidth * 2) / solar.rows;
  for (let c = 0; c < solar.cols; c++) {
    for (let r = 0; r < solar.rows; r++) {
      const module = panel(spanX - 0.05, 0.045, spanZ - 0.05, MATERIALS.solar);
      module.position.set(
        solar.from + spanX * (c + 0.5),
        V.height + 0.025,
        -solar.halfWidth + spanZ * (r + 0.5),
      );
      g.add(module);
    }
  }

  // Markisenkassette — Bauteil des Fahrzeugs, kein Zustand.
  const cassette = panel(
    awning.to - awning.from,
    awning.drop,
    awning.depth,
    MATERIALS.trim,
  );
  cassette.position.set(
    (awning.from + awning.to) / 2,
    V.height - awning.drop / 2 + 0.06,
    V.width / 2 - awning.depth / 2 + 0.02,
  );
  g.add(cassette);

  return g;
}

function buildRearLamps(): Group {
  const g = new Group();
  const geometry = new CylinderGeometry(0.065, 0.065, 0.05, 12);
  geometry.rotateZ(Math.PI / 2);

  // Sie sitzen in dem schmalen Streifen neben der Heckklappe, so wie auf
  // dem Heckfoto.
  for (const side of [-1, 1]) {
    for (const y of [3.36, 3.16, 2.96]) {
      const lamp = new Mesh(geometry, MATERIALS.lamp);
      lamp.position.set(V.length + 0.02, y, side * (V.width / 2 - 0.09));
      g.add(lamp);
    }
  }
  return g;
}

/* ── Bewegliche Teile ──────────────────────────────────────────────────── */

/**
 * Ein bewegliches Teil.
 *
 * `apply` bekommt einen Wert zwischen 0 (geschlossen) und 1 (offen) und setzt
 * die Stellung. Damit ist die Animation vom Zustand getrennt: Der Zustand sagt,
 * *wohin*, die Schleife sorgt für den Weg dorthin.
 */
interface Movable {
  object: Group;
  apply(t: number): void;
  /** Teile, deren Werkstoff bei „unbekannt" getauscht wird. */
  meshes: Mesh[];
  current: number;
  target: number;
  unknown: boolean;
  /**
   * Für Teile, denen der Werkstoffwechsel allein nicht genügt.
   *
   * Nur die Terrasse braucht das: Sie ist in der Ruhelage unsichtbar, und ein
   * durchscheinendes Nichts wäre von einem eingefahrenen Nichts nicht zu
   * unterscheiden. Siehe `buildTerrace`.
   */
  onUnknown?(unknown: boolean): void;
}

function makeMovable(object: Group, apply: (t: number) => void): Movable {
  const meshes: Mesh[] = [];
  object.traverse((child) => {
    if (child instanceof Mesh) meshes.push(child);
  });
  return { object, apply, meshes, current: 0, target: 0, unknown: false };
}

/**
 * Die Garagenöffnung im Heck.
 *
 * Sie gehört zum Aufbau, nicht zu den Türen: Die Öffnung ist auch dann da,
 * wenn die Türen zu sind — und ohne sie ist die Heckwand eine weiße Fläche,
 * auf der man die Garage nicht findet.
 */
function buildGarageOpening(): Mesh {
  const { garage, length } = V;
  const h = garage.top - garage.bottom;
  const shape = roundedRect(garage.halfWidth * 2 + 0.07, h + 0.07, 0.36, 0.16);
  const mesh = new Mesh(extrude(shape, 0.1, 0.012), MATERIALS.trim);
  // Das Profil liegt in der XY-Ebene; für die Heckwand muss es hochkant in
  // die YZ-Ebene gedreht werden.
  mesh.rotation.y = Math.PI / 2;
  mesh.position.set(length - 0.03, (garage.bottom + garage.top) / 2, 0);
  return mesh;
}

/**
 * Die Heckklappe.
 *
 * **Ein Blatt, oben angeschlagen, hebt nach oben.** Auf dem Heckfoto war die
 * waagerechte Fuge als Mittelteilung zweier Flügeltüren zu lesen — das war
 * falsch. Die Drohnenaufnahme zeigt die Klappe geöffnet: Sie steht waagerecht
 * ab und wirkt wie ein Vordach über der Garagenöffnung.
 */
function buildTailgate(): Movable {
  const { garage, length, width } = V;
  const g = new Group();
  const h = garage.top - garage.bottom;

  // Scharnier an der Oberkante der Öffnung. Das Blatt hängt davon nach unten.
  const hinge = new Group();
  hinge.position.set(length, garage.top, 0);

  // Die Klappe ist kein Rechteck: Das Heckfoto zeigt kräftig gerundete Ecken,
  // unten deutlich stärker als oben.
  const leaf = new Mesh(
    extrude(roundedRect(garage.halfWidth * 2, h, 0.34, 0.14), 0.07, 0.014),
    MATERIALS.paintDark,
  );
  leaf.rotation.y = Math.PI / 2;
  leaf.position.set(0.045, -h / 2, 0);
  hinge.add(leaf);

  // Griff unten in der Mitte
  const handle = panel(0.05, 0.06, 0.3, MATERIALS.trim);
  handle.position.set(0.1, -h + 0.22, 0);
  hinge.add(handle);

  g.add(hinge);
  void width;

  return makeMovable(g, (t) => {
    // Bis knapp über die Waagerechte: Das Blatt hängt geschlossen nach unten
    // (lokal -Y) und soll offen nach hinten zeigen (+X). Eine Drehung um die
    // Querachse um +90° bildet genau das ab.
    hinge.rotation.z = t * 1.66;
  });
}

function buildEntryDoor(): Movable {
  const { door, width } = V;
  const g = new Group();
  const h = door.top - door.bottom;

  // Scharnier vorn, das Blatt schwenkt nach außen.
  const hinge = new Group();
  hinge.position.set(door.x, door.bottom + h / 2, width / 2);

  const leaf = panel(door.width, h, 0.06, MATERIALS.paintDark);
  leaf.position.set(door.width / 2, 0, 0.03);
  hinge.add(leaf);

  const glass = panel(door.width - 0.26, h * 0.42, 0.03, MATERIALS.glass);
  glass.position.set(door.width / 2, h * 0.24, 0.07);
  hinge.add(glass);

  const handle = panel(0.05, 0.2, 0.05, MATERIALS.trim);
  handle.position.set(door.width - 0.12, -0.08, 0.09);
  hinge.add(handle);

  g.add(hinge);

  return makeMovable(g, (t) => {
    hinge.rotation.y = -t * 1.75;
  });
}

/**
 * Die ausfahrbare Terrasse über dem Tandem.
 *
 * **Ausgefahren ein Bauteil, eingefahren nichts.** Anders als jedes andere
 * bewegliche Teil verschwindet die Terrasse vollständig — die Fotos zeigen
 * eingefahren eine glatte Flanke und frei stehende Tandemräder. Der Wagen
 * (`carriage`) fährt deshalb nicht nur heraus, er wird auch unsichtbar
 * geschaltet, sobald er drin ist. Sonst hinge die Schürze im eingefahrenen
 * Zustand sichtbar unter dem Aufbau über den Rädern.
 *
 * **Daraus folgt eine Feinheit bei „Stellung unbekannt".** Die Regel aus
 * ADR 0008 lautet: das Teil an der Ruhelage zeigen, durchscheinend. Würde man
 * dafür einfach den eingefahrenen Wagen durchscheinend schalten, käme ein
 * durchscheinendes Nichts heraus — vom eingefahrenen Nichts nicht zu
 * unterscheiden, und der Betrachter läse daraus „eingefahren". Genau das
 * verbietet §106.
 *
 * Deshalb der `ghost`: dieselbe Silhouette wie die Außenschürze, aber bündig
 * in der Flanke statt ausgefahren, und **nur bei unbekannter Stellung**
 * sichtbar. Das ist die Regel wörtlich genommen — das Teil an der Ruhelage,
 * durchscheinend — und zugleich von beiden gemeldeten Stellungen
 * unterscheidbar.
 *
 * Wie sich das Ausfahren mechanisch abspielt, ist nicht bekannt. Die
 * Zwischenstellung ist deshalb eine gerade Bewegung nach außen und **keine
 * Behauptung über die Kinematik**; belegt sind nur die beiden Endlagen.
 */
function buildTerrace(): Movable {
  const { terrace, axles, width } = V;
  const g = new Group();
  const carriage = new Group();
  g.add(carriage);

  const z0 = width / 2;
  const R = terrace.archRadius;

  // Außenschürze mit den beiden Radbögen. Wie das Staukastenband ein
  // Seitenprofil in der XY-Ebene, nur dünn gezogen: Was die Fotos zeigen,
  // ist genau diese Silhouette.
  const s = new Shape();
  s.moveTo(terrace.from, terrace.deck);
  s.lineTo(terrace.from, terrace.apron);
  for (const axle of [axles.rear1, axles.rear2]) {
    s.lineTo(axle - R, terrace.apron);
    s.lineTo(axle - R, terrace.archSpringLine);
    s.absarc(axle, terrace.archSpringLine, R, Math.PI, 0, true);
    s.lineTo(axle + R, terrace.apron);
  }
  s.lineTo(terrace.to, terrace.apron);
  s.lineTo(terrace.to, terrace.deck);
  s.closePath();

  const apronGeometry = extrude(s, 0.05, 0.012);
  const apron = new Mesh(apronGeometry, MATERIALS.paint);
  apron.position.z = z0 + terrace.depth;
  carriage.add(apron);

  // Der Holzbelag. Er liegt bündig auf der Schürzenkante über dem Tandem und
  // reicht von dort bis an die Außenschürze.
  const deck = panel(terrace.to - terrace.from, 0.06, terrace.depth, MATERIALS.wood);
  deck.position.set(
    (terrace.from + terrace.to) / 2,
    terrace.deck - 0.03,
    z0 + terrace.depth / 2,
  );
  carriage.add(deck);

  // Die Treppe kommt unter dem Belag hervor und fällt nach vorn ab.
  // Kein Handlauf — ausdrücklich bestätigt.
  const { count, width: treadWidth, going } = terrace.stairs;
  const rise = terrace.deck / (count + 1);
  const stairZ = z0 + terrace.depth - treadWidth / 2 - 0.08;
  for (let i = 1; i <= count; i += 1) {
    const tread = panel(going, 0.04, treadWidth, MATERIALS.alu);
    tread.position.set(terrace.from - (i - 0.5) * going, terrace.deck - i * rise, stairZ);
    carriage.add(tread);
  }
  // Die beiden Wangen. Sie tragen die Stufen und sind auf den Fotos deutlich
  // zu sehen — ein Handlauf ist das nicht, den hat die Treppe ausdrücklich
  // nicht. Ohne sie schweben die Stufen frei in der Luft.
  const run = count * going;
  const fall = count * rise;
  for (const side of [-1, 1]) {
    const stringer = panel(Math.hypot(run, fall) + 0.12, 0.07, 0.04, MATERIALS.alu);
    stringer.position.set(
      terrace.from - run / 2,
      terrace.deck - fall / 2 - 0.05,
      stairZ + side * (treadWidth / 2),
    );
    stringer.rotation.z = Math.atan2(fall, run);
    carriage.add(stringer);
  }

  /**
   * Die Terrasse an der Ruhelage, nur bei unbekannter Stellung sichtbar.
   *
   * Dieselbe Silhouette wie die Außenschürze, aber bündig in der Flanke statt
   * ausgefahren — genau das, was ADR 0008 für „unbekannt" vorsieht: das Teil
   * an der Ruhelage, durchscheinend und schwach leuchtend. Belag und Treppe
   * bleiben weg, die stäken sonst durch den Aufbau.
   */
  const ghost = new Mesh(apronGeometry, MATERIALS.paint);
  ghost.position.z = z0;
  ghost.visible = false;
  g.add(ghost);

  let unknown = false;
  const movable = makeMovable(g, (t) => {
    carriage.position.z = (t - 1) * terrace.depth;
    carriage.visible = !unknown && t > 0.02;
    ghost.visible = unknown;
  });
  movable.onUnknown = (value) => {
    unknown = value;
    movable.apply(movable.current);
  };
  return movable;
}

/* ── Boden ─────────────────────────────────────────────────────────────── */

function buildShadow(): Mesh {
  // Ein weicher Fleck statt einer echten Schattenberechnung. Schattenkarten
  // kosten auf dem Pi jedes Bild Rechenzeit; dieser Fleck kostet einmalig
  // eine kleine Textur und sieht bei einem stehenden Fahrzeug genauso gut aus.
  const size = 128;
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  gradient.addColorStop(0, "rgba(0,0,0,0.42)");
  gradient.addColorStop(0.55, "rgba(0,0,0,0.2)");
  gradient.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);

  const mesh = new Mesh(
    new PlaneGeometry(V.length * 1.2, V.width * 1.6),
    new MeshBasicMaterial({
      map: new CanvasTexture(canvas),
      transparent: true,
      depthWrite: false,
    }),
  );
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.set(V.length / 2, 0.004, 0);
  return mesh;
}

/* ── Zusammenbau ───────────────────────────────────────────────────────── */

export function buildVehicle(): VehicleModel {
  const root = new Group();
  const body = new Group();

  body.add(buildUnderbody());
  body.add(buildSkirt());
  body.add(buildCab());
  body.add(buildHull());
  body.add(buildCabFront());
  body.add(buildSeams());
  body.add(buildWheels());
  body.add(buildWindows());
  body.add(buildRoof());
  body.add(buildGarageOpening());
  body.add(buildRearLamps());
  root.add(body);
  root.add(buildShadow());

  // Der Ursprung liegt an der Fahrzeugfront; fürs Drehen soll er in der Mitte
  // liegen. Statt jede Zahl umzurechnen, wird das Ganze einmal verschoben.
  root.position.x = -V.length / 2;

  const builders: Record<keyof VehicleState, () => Movable> = {
    garage: buildTailgate,
    door: buildEntryDoor,
    terrace: buildTerrace,
  };

  const parts = new Map<keyof VehicleState, Movable>();
  const originals = new Map<Mesh, Material | Material[]>();

  function ensure(name: keyof VehicleState): Movable {
    let part = parts.get(name);
    if (!part) {
      part = builders[name]();
      part.apply(0);
      for (const mesh of part.meshes) originals.set(mesh, mesh.material);
      body.add(part.object);
      parts.set(name, part);
    }
    return part;
  }

  function drop(name: keyof VehicleState) {
    const part = parts.get(name);
    if (!part) return;
    body.remove(part.object);
    for (const mesh of part.meshes) {
      mesh.geometry.dispose();
      originals.delete(mesh);
    }
    parts.delete(name);
  }

  return {
    root,

    setState(state) {
      for (const name of Object.keys(builders) as (keyof VehicleState)[]) {
        const value = state[name];

        // Ohne Hardwarezuordnung existiert das Teil im Modell nicht.
        if (value === "absent") {
          drop(name);
          continue;
        }

        const part = ensure(name);

        // Bei unbekannter Stellung wird nichts bewegt und nichts behauptet.
        part.unknown = value === "unknown";
        part.onUnknown?.(part.unknown);
        part.target = value === "open" ? 1 : value === "moving" ? 0.45 : 0;

        for (const mesh of part.meshes) {
          const original = originals.get(mesh);
          mesh.material = part.unknown ? UNKNOWN_MATERIAL : original ?? mesh.material;
        }
      }
    },

    update(dt) {
      let moving = false;
      for (const part of parts.values()) {
        const delta = part.target - part.current;
        if (Math.abs(delta) < 0.001) {
          if (part.current !== part.target) {
            part.current = part.target;
            part.apply(part.current);
          }
          continue;
        }
        // Zeitbasierte Annäherung: gleiches Verhalten bei jeder Bildrate.
        part.current += delta * (1 - Math.exp(-dt * 4.5));
        part.apply(part.current);
        moving = true;
      }
      return moving;
    },

    settle() {
      for (const part of parts.values()) {
        part.current = part.target;
        part.apply(part.current);
      }
    },

    dispose() {
      root.traverse((child) => {
        if (child instanceof Mesh) {
          child.geometry.dispose();
          const material = child.material;
          // Die gemeinsamen Werkstoffe leben modulweit weiter; nur die
          // eigens erzeugten (Bodenfleck) werden hier freigegeben.
          if (material instanceof MeshBasicMaterial) {
            material.map?.dispose();
            material.dispose();
          }
        }
      });
    },
  };
}
