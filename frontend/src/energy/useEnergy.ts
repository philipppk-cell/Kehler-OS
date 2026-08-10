/**
 * Der Energiezustand vom Backend.
 *
 * Wie beim Wasser wird hier nichts gerechnet und nichts gedeutet. Ob die
 * Batterie lädt, entlädt oder ruht — und ob dazu überhaupt eine Aussage
 * möglich ist — entscheidet `core/energy.py`.
 */

import { useEffect, useState } from "react";
import { useAppState } from "../realtime/hooks";
import type { Quality } from "../realtime/types";

export interface Reading {
  value: number | null;
  quality: Quality;
}

export type Direction = "charging" | "discharging" | "idle";

export interface EnergySummary {
  soc: Reading;
  voltage: Reading;
  current: Reading;
  battery_power: Reading;
  solar_power: Reading;
  consumption: Reading;
  shore_power: Reading;
  /** `null` heißt unbekannt — ausdrücklich nicht „nicht verbunden". */
  shore_connected: boolean | null;
  /** `null`, wenn die Richtung nicht belegbar ist. */
  direction: Direction | null;
}

export function useEnergy(): EnergySummary | null {
  const [energy, setEnergy] = useState<EnergySummary | null>(null);
  const { entities, connection } = useAppState();

  useEffect(() => {
    if (connection !== "online") return;

    let active = true;
    fetch("/api/v1/energy")
      .then((r) => (r.ok ? r.json() : null))
      .then((data: EnergySummary | null) => active && data && setEnergy(data))
      .catch(() => undefined);

    return () => {
      active = false;
    };
  }, [entities, connection]);

  return energy;
}
