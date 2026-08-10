/**
 * Die Wasserstände vom Backend.
 *
 * Die Zusammenfassung — vor allem die Gesamtmenge Frischwasser über beide
 * Tanks — entsteht im Backend (`core/water.py`). Hier wird sie nur geholt.
 *
 * Das ist Absicht: Die Summe enthält zwei Regeln, die Geschäftslogik sind
 * (über Liter statt über Prozent rechnen; keine Summe, wenn ein Tank keinen
 * belastbaren Wert liefert). Solche Regeln gehören nicht in die Oberfläche
 * (Kapitel 18 §6) — sonst rechnet jede Ansicht sie neu und irgendwann eine
 * davon anders.
 */

import { useEffect, useState } from "react";
import { useAppState } from "../realtime/hooks";
import type { Quality } from "../realtime/types";

/** Wie ein Füllstand zu bewerten ist. Bewertet im Backend, nicht hier. */
export type Level = "ok" | "warn" | "critical";

export interface TankView {
  entity_id: string;
  name_key: string;
  quality: Quality;
  /** Füllstand in Prozent. `null`, wenn nicht belastbar. */
  percent: number | null;
  capacity_l: number | null;
  /** Belegter Inhalt in Litern. `null`, wenn Füllstand oder Kapazität fehlen. */
  litres: number | null;
  free_l: number | null;
  /** Konfigurierte Warnschwellen. `null` heißt: für diesen Wert wird nicht
   *  gewarnt — es gibt keine eingebauten Schwellen. */
  warn_below: number | null;
  warn_above: number | null;
  critical_below: number | null;
  critical_above: number | null;
  level: Level;
}

export interface FreshGroup {
  quality: Quality;
  capacity_l: number | null;
  litres: number | null;
  free_l: number | null;
  percent: number | null;
  warn_below: number | null;
  critical_below: number | null;
  level: Level;
  tanks: TankView[];
}

export interface WaterSummary {
  fresh: FreshGroup;
  waste: TankView[];
}

export function useWater(): WaterSummary | null {
  const [water, setWater] = useState<WaterSummary | null>(null);
  const { entities, connection } = useAppState();

  useEffect(() => {
    // Ohne Verbindung wird nichts nachgeladen. Der zuletzt geholte Stand
    // bleibt sichtbar — die Oberfläche kennzeichnet ihn als veraltet.
    if (connection !== "online") return;

    let active = true;
    fetch("/api/v1/water")
      .then((r) => (r.ok ? r.json() : null))
      .then((data: WaterSummary | null) => active && data && setWater(data))
      .catch(() => undefined);

    return () => {
      active = false;
    };
    // Bei jeder Zustandsänderung neu holen — gerechnet wird im Backend.
  }, [entities, connection]);

  return water;
}
