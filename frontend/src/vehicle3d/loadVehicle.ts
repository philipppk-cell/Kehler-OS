/**
 * Lädt ein geliefertes Fahrzeugmodell — oder baut das eigene.
 *
 * ADR 0008 baut das Fahrzeug aus Code. Das bleibt der Auslieferungsstand und
 * die Rückfallebene. Liegt aber unter `config/vehicle/model.glb` ein Modell,
 * hat es Vorrang: Der Fahrzeughalter hat sich am 2026-08-11 ausdrücklich für
 * ein echtes Modell entschieden.
 *
 * ── Die eine Frage, die ein Modell beantworten muss ───────────────────────
 *
 * Nicht „wie sieht das Fahrzeug aus", sondern **„wie bewegt sich das Tor"**.
 * Ein Dashboard-Fahrzeug ist eine Zustandsanzeige. Ein Modell, das schön
 * aussieht, aber nicht zeigen kann, dass die Garage offen steht, ist für
 * diesen Zweck wertlos.
 *
 * Geraten wird das nicht. Es gibt keine Konvention „das Teil heißt Tor, also
 * dreht es sich schon irgendwie um die richtige Achse" — Drehpunkt, Richtung
 * und Weg sind Eigenschaften des Modells und nur dort bekannt. Deshalb:
 *
 * **Je bewegliches Teil eine glTF-Animation, benannt wie der Zustand**
 * (`garage`, `door`, `step`, `awning`). Sie läuft von geschlossen (Anfang) bis
 * offen (Ende). Kehler OS setzt nur die Stelle darin — der Modellbauer
 * bestimmt den Weg.
 *
 * Fehlt eine Animation, bewegt sich das Teil nicht. Das wird **gemeldet** und
 * nicht verschwiegen: `report()` sagt, was gefunden wurde und was fehlt.
 */

import type { VehicleModel, VehicleState } from "./buildVehicle";
import { buildVehicle } from "./buildVehicle";

/** Die beweglichen Teile, in der Benennung, die ein Modell mitbringen muss. */
const TEILE = ["garage", "door", "step", "awning"] as const;
type Teil = (typeof TEILE)[number];

export interface ModelReport {
  /** `"code"` heißt: eigene Darstellung, kein geliefertes Modell. */
  quelle: "code" | "datei";
  /** Welche beweglichen Teile das Modell tatsächlich bewegen kann. */
  gefunden: Teil[];
  /** Welche fehlen — sie stehen dann still. */
  fehlend: Teil[];
  /** Warum die Datei nicht verwendet wurde, falls sie es nicht wurde. */
  grund?: string;
}

/**
 * Wie weit ein Teil offen ist: 0 = geschlossen, 1 = offen.
 *
 * Bewusst dieselbe Auslegung wie in der aus Code gebauten Darstellung, damit
 * beide Wege dasselbe zeigen. `BLOCKED` und `STOPPED` sind Zwischenstände
 * ohne bekannte Stellung — dort bleibt das Teil, wo es ist.
 */
function offenheit(part: string): number | null {
  switch (part) {
    case "open":
      return 1;
    case "closed":
      return 0;
    default:
      return null;
  }
}

/**
 * Versucht, das hinterlegte Modell zu laden.
 *
 * Schlägt irgendetwas fehl — keine Datei, kaputte Datei, kein WebGL —, kommt
 * die aus Code gebaute Darstellung zurück. Ein Fahrzeug ist in jedem Fall zu
 * sehen; die Oberfläche fällt nicht auf einen leeren Kasten zurück.
 */
export async function loadVehicle(): Promise<{
  model: VehicleModel;
  report: ModelReport;
}> {
  try {
    const antwort = await fetch("/api/v1/vehicle/model");
    if (!antwort.ok) {
      return { model: buildVehicle(), report: { quelle: "code", gefunden: [], fehlend: [] } };
    }

    const daten = await antwort.arrayBuffer();
    const { GLTFLoader } = await import("three/examples/jsm/loaders/GLTFLoader.js");
    const { AnimationMixer, Group, LoopOnce } = await import("three");

    const gltf = await new GLTFLoader().parseAsync(daten, "");

    const root = new Group();
    root.add(gltf.scene);

    const mixer = new AnimationMixer(gltf.scene);
    const aktionen = new Map<Teil, import("three").AnimationAction>();

    for (const clip of gltf.animations) {
      const name = clip.name.trim().toLowerCase() as Teil;
      if (!TEILE.includes(name)) continue;

      const aktion = mixer.clipAction(clip);
      // Die Animation wird nicht abgespielt, sondern **angefahren**: Kehler OS
      // setzt die Zeit direkt auf den Zustand. `paused` verhindert, dass der
      // Mixer sie selbst weiterlaufen lässt.
      aktion.play();
      aktion.paused = true;
      aktion.clampWhenFinished = true;
      aktion.setLoop(LoopOnce, 1);
      aktionen.set(name, aktion);
    }

    const gefunden = [...aktionen.keys()];
    if (gefunden.length === 0) {
      // Ein Modell ohne bewegliche Teile kann keine Zustände zeigen. Es zu
      // verwenden hieße, Bedienbarkeit gegen Aussehen zu tauschen — und der
      // ganze Zweck dieser Darstellung ist die Aussage, nicht das Bild.
      return {
        model: buildVehicle(),
        report: {
          quelle: "code",
          gefunden: [],
          fehlend: [...TEILE],
          grund: "Das Modell enthält keine Animation für ein bewegliches Teil",
        },
      };
    }

    return {
      model: geladenesModell(root, mixer, aktionen, gltf.animations),
      report: {
        quelle: "datei",
        gefunden,
        fehlend: TEILE.filter((teil) => !aktionen.has(teil)),
      },
    };
  } catch (fehler) {
    return {
      model: buildVehicle(),
      report: {
        quelle: "code",
        gefunden: [],
        fehlend: [...TEILE],
        grund: String(fehler),
      },
    };
  }
}

/** Verpackt das geladene Modell in dieselbe Schnittstelle wie das gebaute. */
function geladenesModell(
  root: import("three").Group,
  mixer: import("three").AnimationMixer,
  aktionen: Map<Teil, import("three").AnimationAction>,
  clips: import("three").AnimationClip[],
): VehicleModel {
  const ziel = new Map<Teil, number>();
  const stand = new Map<Teil, number>();
  for (const teil of aktionen.keys()) {
    ziel.set(teil, 0);
    stand.set(teil, 0);
  }

  /** Wie lange ein Teil für den vollen Weg braucht — in Sekunden. */
  const dauer = (teil: Teil) =>
    clips.find((clip) => clip.name.trim().toLowerCase() === teil)?.duration ?? 1;

  return {
    root,

    setState(state: VehicleState) {
      for (const teil of aktionen.keys()) {
        const wert = offenheit(state[teil]);
        // `null` heißt: Stellung unbekannt. Dann bleibt das Teil stehen, statt
        // eine Endlage einzunehmen, die es nicht hat (Kapitel 18 §37).
        if (wert !== null) ziel.set(teil, wert);
      }
    },

    update(dt: number): boolean {
      let bewegt = false;

      for (const [teil, aktion] of aktionen) {
        const soll = ziel.get(teil) ?? 0;
        const ist = stand.get(teil) ?? 0;
        if (Math.abs(soll - ist) < 0.001) continue;

        // Der Weg dauert so lange, wie die Animation im Modell dauert — der
        // Modellbauer bestimmt das Tempo, nicht diese Datei.
        const schritt = Math.min(Math.abs(soll - ist), dt / dauer(teil));
        const neu = ist + Math.sign(soll - ist) * schritt;
        stand.set(teil, neu);
        aktion.time = neu * dauer(teil);
        bewegt = true;
      }

      // Zeitschritt 0: übernimmt die gesetzten Zeiten, ohne selbst zu laufen.
      mixer.update(0);
      return bewegt;
    },

    settle() {
      for (const [teil, aktion] of aktionen) {
        const soll = ziel.get(teil) ?? 0;
        stand.set(teil, soll);
        aktion.time = soll * dauer(teil);
      }
      mixer.update(0);
    },

    dispose() {
      mixer.stopAllAction();
      root.traverse((objekt) => {
        const mesh = objekt as import("three").Mesh;
        mesh.geometry?.dispose?.();
        const material = mesh.material;
        if (Array.isArray(material)) material.forEach((m) => m.dispose());
        else material?.dispose?.();
      });
    },
  };
}
