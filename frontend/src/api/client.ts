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

    // „Abgelöst" ist kein Fehler. Wer ein fahrendes Tor anhält, hat genau
    // das erreicht, was er wollte — der abgelöste Fahrbefehl ist nur
    // nebenbei zu Ende gegangen. Eine Fehlermeldung dafür wäre eine
    // Belehrung, und sie käme ausgerechnet in dem Moment, in dem jemand
    // eingegriffen hat.
    //
    // Erfolgreich ist der Befehl trotzdem nicht: Der Zustand des Teils zeigt
    // „Gestoppt" und nicht „Offen".
    if (!result.success && result.phase !== "SUPERSEDED") {
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
/**
 * Verlängert einen bereits laufenden Hold-to-run-Befehl.
 *
 * Dieser Aufruf kann selbst keine Bewegung starten. Bleibt er aus, beendet
 * der Backend-Watchdog den SPS-Eingang automatisch.
 */
export async function renewHold(
  entityId: string,
  verb: string,
): Promise<boolean> {
  try {
    const response = await fetch(`${BASE}/holds/heartbeat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entity_id: entityId, verb }),
    });

    return response.ok;
  } catch {
    return false;
  }
}

function explain(result: CommandResult): string {
  if (result.rejection) {
    return t(`cmd.rejected.${result.rejection}`, t("cmd.failed"));
  }
  if (result.phase === "TIMEOUT") return t("cmd.timeout");

  // Der Endzustand sagt, woran es lag. „Blockiert" ist eine Auskunft, mit
  // der jemand etwas anfangen kann; „Befehl konnte nicht ausgeführt werden"
  // ist keine.
  if (result.ended_state) {
    return t(`cmd.ended.${result.ended_state}`, t("cmd.failed"));
  }
  return t("cmd.failed");
}
