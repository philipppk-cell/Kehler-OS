/**
 * HTTP-Zugriff auf das Backend.
 *
 * Befehle laufen über HTTP, nicht über den WebSocket — eindeutige
 * Fehlercodes und saubere Zuordnung im Audit (ADR 0005).
 */

import { store } from "../realtime/store";
import { t } from "../i18n/de";
import type { CommandResult, SystemInfo } from "../realtime/types";

const BASE = "/api/v1";

export async function fetchSystem(): Promise<SystemInfo | null> {
  try {
    const response = await fetch(`${BASE}/system`);
    if (!response.ok) return null;
    const info = (await response.json()) as SystemInfo;
    store.setSystem(info);
    return info;
  } catch {
    return null;
  }
}

/**
 * Setzt einen Befehl ab und wartet auf sein Ergebnis.
 *
 * Während der Ausführung ist die Entity als „läuft“ markiert. Die Oberfläche
 * zeigt damit Aktivität, ohne den Hardwarezustand zu behaupten — der kommt
 * ausschließlich über den WebSocket (Kapitel 18 §37).
 */
export async function sendCommand(
  entityId: string,
  verb: string,
  params: Record<string, unknown> = {},
): Promise<CommandResult | null> {
  store.setPending(entityId, verb);
  store.clearError();

  try {
    const response = await fetch(`${BASE}/commands`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entity_id: entityId, verb, params, client: "hmi" }),
    });

    const result = (await response.json()) as CommandResult;

    if (!result.success) {
      store.setError(entityId, explain(result));
    }
    return result;
  } catch {
    store.setError(entityId, t("conn.offline"));
    return null;
  } finally {
    store.setPending(entityId, null);
  }
}

/**
 * Übersetzt ein technisches Ergebnis in einen verständlichen Satz.
 *
 * Der Rohtext aus `detail` bleibt der Diagnose vorbehalten und erscheint
 * nicht in der normalen Oberfläche (Kapitel 7 §43, Kapitel 17 §22).
 */
function explain(result: CommandResult): string {
  if (result.rejection) {
    return t(`cmd.rejected.${result.rejection}`, t("cmd.failed"));
  }
  if (result.phase === "TIMEOUT") return t("cmd.timeout");
  return t("cmd.failed");
}
