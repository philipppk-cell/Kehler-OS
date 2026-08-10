/**
 * Die Eingriffe, die es ausschließlich in der Simulation gibt.
 *
 * Kapitel 18 §65: Eine Simulation ohne auslösbare Fehlerbilder ist wertlos —
 * die Zustände, die im Alltag am seltensten auftreten, sind im Ernstfall die
 * wichtigsten. Ohne diesen Weg ließen sie sich nur prüfen, indem man auf sie
 * wartet.
 *
 * Im Produktivbetrieb existieren diese Endpunkte nicht. Das ist die
 * eigentliche Absicherung und sie liegt im Backend (Kapitel 15 §96); die
 * Oberfläche blendet die Werkzeuge zusätzlich aus, weil eine Schaltfläche,
 * die nur eine Fehlermeldung erzeugt, keine Bedienung ist.
 */

const BASE = "/api/v1/diagnostics/simulation";

async function post(path: string, body: unknown): Promise<string | null> {
  try {
    const response = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (response.ok) return null;

    // Auf der Diagnoseseite ist der Rohtext des Servers die richtige
    // Antwort — sie ist der eine Ort, an dem technische Begründungen
    // hingehören (Kapitel 7 §43).
    const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
    return detail?.detail ?? `HTTP ${response.status}`;
  } catch (error) {
    return String(error);
  }
}

/** Löst ein Fehlerbild aus oder nimmt es mit `NONE` zurück. */
export function injectFault(entityId: string, fault: string): Promise<string | null> {
  return post("/fault", { entity_id: entityId, fault });
}

/** Setzt einen simulierten Messwert auf einen bestimmten Stand. */
export function setLevel(entityId: string, value: number): Promise<string | null> {
  return post("/level", { entity_id: entityId, value });
}
