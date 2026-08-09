/** Zugriff auf den Zustandsspiegel aus React-Komponenten. */

import { useSyncExternalStore } from "react";
import { store } from "./store";
import { Link, Quality, type EntityView } from "./types";

export function useAppState() {
  return useSyncExternalStore(store.subscribe, store.getSnapshot);
}

export function useEntity(entityId: string): EntityView | undefined {
  return useAppState().entities.get(entityId);
}

/** Ob für diese Entity gerade ein Befehl läuft. */
export function usePending(entityId: string): boolean {
  return useAppState().pending.has(entityId);
}

/* ── Auswertung ────────────────────────────────────────────────────────
   Kleine Helfer, die überall dieselbe Antwort geben. Ohne sie würde jede
   Karte ihre eigene Auslegung von „ist das an?“ erfinden.               */

export function isOn(entity: EntityView | undefined): boolean {
  return entity?.state.quality === Quality.Valid && entity.state.value === "ON";
}

/** Ein Zustand ist unbekannt, wenn er es ist — oder wenn niemand ihn liefert. */
export function isUnknown(entity: EntityView | undefined): boolean {
  if (!entity) return true;
  if (!entity.definition?.configured) return true;
  if (entity.link === Link.Offline || entity.link === Link.Error) return true;
  return (
    entity.state.quality === Quality.Unknown ||
    entity.state.quality === Quality.Invalid ||
    entity.state.quality === Quality.Error
  );
}

export function numberOf(entity: EntityView | undefined): number | null {
  const value = entity?.state.value;
  const usable =
    entity?.state.quality === Quality.Valid || entity?.state.quality === Quality.Stale;
  return usable && typeof value === "number" ? value : null;
}

export function textOf(entity: EntityView | undefined): string | null {
  if (isUnknown(entity)) return null;
  const value = entity?.state.value;
  return typeof value === "string" ? value : null;
}
