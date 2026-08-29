/**
 * Die Datenformen, die das Backend liefert.
 *
 * Bewusst nah an der API gehalten: Was das Backend über die Belastbarkeit
 * eines Wertes sagt, geht hier nicht verloren.
 */

export const Quality = {
  Valid: "VALID",
  Stale: "STALE",
  Unknown: "UNKNOWN",
  Invalid: "INVALID",
  Error: "ERROR",
} as const;
export type Quality = (typeof Quality)[keyof typeof Quality];

export const Link = {
  Initializing: "INITIALIZING",
  Online: "ONLINE",
  Degraded: "DEGRADED",
  Reconnecting: "RECONNECTING",
  Offline: "OFFLINE",
  Error: "ERROR",
  Unknown: "UNKNOWN",
  NotConfigured: "NOT_CONFIGURED",
} as const;
export type Link = (typeof Link)[keyof typeof Link];

export interface StateValue {
  value: string | number | boolean | null;
  unit: string | null;
  quality: Quality;
  source: string | null;
  measured_at: string | null;
  received_at: string;
}

export interface Capability {
  verb: string;
  params: string[];
  risk: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  needs_confirmation: boolean;
  hold_to_run: boolean;
  timeout_ms: number;
}

export interface EntityDefinition {
  id: string;
  name_key: string;
  area: string | null;
  unit: string | null;
  configured: boolean;

  /**
   * Ob überhaupt bestätigt ist, dass die Funktion über die Schnittstelle
   * verfügbar ist.
   *
   * Nicht dasselbe wie `configured: false`. Dort fehlt die Zuordnung, hier
   * fehlt die Gewissheit, dass es etwas zuzuordnen gibt — bei der
   * SCHEER-Heizung liegt die Modbus-Registerliste noch nicht vor. Die
   * Oberfläche sagt deshalb „noch zu verifizieren" statt „nicht
   * konfiguriert"; das eine ist eine offene Zuordnung, das andere eine
   * offene Frage.
   */
  unverified: boolean;

  /**
   * Ob die Hardware ihren Zustand zurückmeldet.
   *
   * `false` heißt: ansteuerbar, aber nicht auslesbar — ein Ausgang ohne
   * Endlagenschalter. Der Zustand bleibt dann **dauerhaft** unbekannt, und
   * das ist kein Fehler, sondern die Eigenschaft dieser Anlage.
   *
   * Erst mit dieser Angabe lässt sich „Unbekannt" deuten. Bei einem Fühler
   * heißt es „hier stimmt etwas nicht", bei den Ablassventilen „hier war nie
   * etwas zu holen". Die Oberfläche zeigt im zweiten Fall den zuletzt
   * gesendeten Befehl statt eines Fragezeichens — und benennt ihn als
   * Befehl.
   */
  feedback: boolean;

  /**
   * Erwartetes Aktualisierungsintervall in Sekunden.
   *
   * `null` heißt: Es werden keine regelmäßigen Meldungen erwartet. Erst damit
   * lässt sich ein stehender Zeitstempel deuten — bei einem Fühler ist er ein
   * Befund, bei einem Garagentor, das sich seit gestern nicht bewegt hat, der
   * Normalzustand.
   */
  expected_interval_s: number | null;

  /** Tankkapazität in Litern. `null` heißt: keine Literangabe. */
  capacity_l: number | null;
  /** Batteriekapazität und Nennspannung. Beide nötig für den Energieinhalt. */
  capacity_ah: number | null;
  nominal_voltage: number | null;

  /** Grenzen eines einstellbaren Wertes. Ohne `max_value` gibt es keinen
   *  Befehl — und damit kein Bedienelement. */
  min_value: number | null;
  max_value: number | null;
  step: number | null;

  /** Freigegebene Zustände einer mehrwertigen Auswahl. */
  states: string[];

  warn_below: number | null;
  warn_above: number | null;
  critical_below: number | null;
  critical_above: number | null;

  capabilities: Capability[];
}

export interface EntityView {
  entity_id: string;
  seq: number;
  link: Link;
  state: StateValue;
  attributes: Record<string, StateValue>;
  /**
   * Wunschzustand aus einem Befehl — getrennt vom tatsächlichen.
   *
   * Normalerweise nur während der Ausführung gesetzt: Sobald die Hardware
   * bestätigt hat, sagt der echte Zustand mehr, und der Wunsch verschwindet.
   *
   * Bei `feedback: false` bleibt er **stehen**. Dort kommt nie eine
   * Bestätigung, und der zuletzt gesendete Befehl ist damit die einzige
   * Information, die es über das Gerät gibt. Er bleibt trotzdem ein Wunsch
   * und wird nie als Zustand ausgegeben.
   */
  requested: { value: unknown; command_id: string; since: string } | null;
  definition?: EntityDefinition;
}

export interface SystemInfo {
  version: string;
  environment: string;
  simulated: boolean;
  health: "HEALTHY" | "DEGRADED" | "WARNING" | "CRITICAL" | "INITIALIZING";
  entities: number;
  unconfigured: number;
  services: Record<string, string>;
  state_version: number;
}

export interface CommandResult {
  command_id: string;
  entity_id: string;
  verb: string;
  phase: string;
  success: boolean;
  rejection: string | null;
  /** Zustand, in dem eine Bewegung geendet ist, wenn nicht am Ziel. */
  ended_state: string | null;
  detail: string | null;
  duration_ms: number | null;
}

export type ServerMessage =
  | { type: "snapshot"; version: number; entities: EntityView[] }
  | { type: "delta"; entity: EntityView };

/** Verbindungszustand des Clients zum Backend. */
export type ConnectionState = "connecting" | "online" | "reconnecting" | "offline";
