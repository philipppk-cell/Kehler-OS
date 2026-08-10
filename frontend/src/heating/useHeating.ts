/**
 * Der zusammengefasste Zustand der Heizungsanlage.
 *
 * Wie bei Wasser und Energie entsteht die Deutung im Backend
 * (`core/heating.py`) und wird hier nur geholt. Gedeutet wird genau eine
 * Sache: **welche Wärmequelle gerade arbeitet.** Das ist eine Verknüpfung aus
 * Brennerphase und Elektroheizung — also Geschäftslogik, und die gehört nicht
 * in die Oberfläche (Kapitel 18 §6). Sonst rechnet sie jede Ansicht neu und
 * irgendwann eine davon anders.
 */

import { useEffect, useState } from "react";
import { useAppState } from "../realtime/hooks";

export type HeatSource = "burner" | "electric" | "both" | "none";

export interface HeatingSummary {
  /** `null` heißt unbekannt — ausdrücklich nicht „keine aktiv". */
  heat_source: HeatSource | null;
  /** `null` heißt: Die Anlage meldet nichts. Keine Entwarnung. */
  fault: boolean | null;
  /** Ob überhaupt eine Funktion der Anlage angebunden ist. */
  linked: boolean;
  /** Wie viele Funktionen noch auf ihre Bestätigung warten. */
  unverified: number;
}

export function useHeating(): HeatingSummary | null {
  const [heating, setHeating] = useState<HeatingSummary | null>(null);
  const { entities, connection } = useAppState();

  useEffect(() => {
    // Ohne Verbindung wird nichts nachgeladen. Der zuletzt geholte Stand
    // bleibt sichtbar — die Oberfläche kennzeichnet ihn als veraltet.
    if (connection !== "online") return;

    let active = true;
    fetch("/api/v1/heating")
      .then((r) => (r.ok ? r.json() : null))
      .then((data: HeatingSummary | null) => active && data && setHeating(data))
      .catch(() => undefined);

    return () => {
      active = false;
    };
  }, [entities, connection]);

  return heating;
}
