/**
 * Entscheidet, wie das Fahrzeug dargestellt wird.
 *
 * **Erste Wahl:** die dreidimensionale, drehbare Ansicht.
 *
 * **Rückfallebene:** die technische SVG-Seitenansicht. Sie ist kein
 * Notbehelf, sondern eine vollwertige Darstellung derselben Zustände — sie
 * kann nur nicht gedreht werden. Sie greift, wenn kein WebGL zur Verfügung
 * steht und außerdem in der kurzen Zeitspanne, in der die 3D-Ansicht noch
 * geladen wird. Kapitel 17 §111: Die Oberfläche darf nicht auseinanderfallen,
 * nur weil ein Teil nicht verfügbar ist.
 *
 * Die 3D-Ansicht wird **getrennt nachgeladen**. Dadurch enthält das erste
 * Paket keine 3D-Bibliothek, und das Dashboard steht sofort — auch auf dem
 * Pi (Kapitel 17 §93).
 */

import {
  Component,
  Suspense,
  lazy,
  useMemo,
  type ReactNode,
} from "react";
import { VehicleView, type Part } from "../vehicle/VehicleView";
import type { VehicleState } from "./buildVehicle";
import { t } from "../i18n/de";

const VehicleScene = lazy(() =>
  import("./VehicleScene").then((module) => ({ default: module.VehicleScene })),
);

/** Einmalige Prüfung — ein Kontext pro Seitenaufruf reicht. */
let webglSupported: boolean | null = null;

function hasWebGL(): boolean {
  if (webglSupported !== null) return webglSupported;

  try {
    const canvas = document.createElement("canvas");

    /*
     * Three.js in der aktuell eingesetzten Version benötigt für den
     * WebGLRenderer WebGL 2.
     *
     * Ein Gerät, das nur WebGL 1 anbietet, darf deshalb nicht als
     * 3D-fähig gelten. Besonders Embedded-Browser auf HMIs können einen
     * WebGL-Kontext anbieten, ohne die Anforderungen der 3D-Szene zu
     * erfüllen.
     */
    webglSupported = Boolean(
      canvas.getContext("webgl2"),
    );
  } catch {
    webglSupported = false;
  }

  return webglSupported;
}

class VehicleSceneBoundary extends Component<
  {
    children: ReactNode;
    fallback: ReactNode;
  },
  {
    failed: boolean;
  }
> {
  state = {
    failed: false,
  };

  static getDerivedStateFromError() {
    return {
      failed: true,
    };
  }

  componentDidCatch(error: unknown) {
    console.warn(
      "Kehler OS · 3D-Ansicht nicht verfügbar, verwende 2D-Fallback",
      error,
    );
  }

  render() {
    if (this.state.failed) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}


export function VehicleDisplay({ state }: { state: VehicleState }) {
  const label = useMemo(() => describeForScreenReader(state), [state]);

  /*
   * Eingebettete HMI-Browser können WebGL 2 melden, obwohl der
   * Three.js-Renderer dort nicht zuverlässig funktioniert.
   *
   * Mit ?hmi=1 wird die 3D-Komponente deshalb gar nicht erst geladen.
   * Alle normalen Browser behalten weiterhin die 3D-Ansicht.
   */
  const hmiMode = /(?:^|[?&])hmi=1(?:&|$)/.test(
    window.location.search,
  );

  if (hmiMode || !hasWebGL()) {
    return <VehicleView state={state} />;
  }

  return (
    <VehicleSceneBoundary
      fallback={<VehicleView state={state} />}
    >
      <Suspense fallback={<VehicleView state={state} />}>
        <VehicleScene
          state={state}
          label={label}
          onModelReport={(report) => {
            // Bewusst ins Protokoll und nicht in die Oberfläche: Die Auskunft
            // richtet sich an den, der ein Modell hinterlegt, nicht an den,
            // der im Fahrzeug sitzt. Sie erscheint auch dann, wenn alles
            // geklappt hat — ein Modell mit fehlender Bewegung sieht sonst
            // richtig aus und ist es nicht.
            const fehlt = report.fehlend.length
              ? ` — ohne Bewegung: ${report.fehlend.join(", ")}`
              : "";
            console.info(
              `Kehler OS · Fahrzeugmodell aus ${report.quelle === "datei" ? "Datei" : "Code"}` +
                `${report.gefunden.length ? ` (${report.gefunden.join(", ")})` : ""}${fehlt}` +
                `${report.grund ? ` — ${report.grund}` : ""}`,
            );
          }}
        />
      </Suspense>
    </VehicleSceneBoundary>
  );
}

/**
 * Beschreibt den dargestellten Zustand in Worten.
 *
 * Eine 3D-Ansicht ist für Vorlesewerkzeuge eine leere Fläche. Deshalb trägt
 * sie denselben Inhalt zusätzlich als Text (Kapitel 7 §23: Der Zustand muss
 * auch ohne die grafische Darstellung verständlich sein).
 */
function describeForScreenReader(state: VehicleState): string {
  const names: [keyof VehicleState, string][] = [
    ["garage", t("vehicle.garage_door")],
    ["door", t("vehicle.door_main")],
    ["step", t("vehicle.step")],
    ["awning", t("vehicle.awning")],
  ];

  const parts = names
    .filter(([key]) => state[key] !== "absent")
    .map(([key, name]) => `${name}: ${partText(state[key])}`);

  return `${t("vehicle3d.label")}. ${parts.join(", ")}`;
}

function partText(part: Part): string {
  switch (part) {
    case "open": return t("state.open");
    case "closed": return t("state.closed");
    case "moving": return t("state.opening");
    default: return t("state.unknown");
  }
}
