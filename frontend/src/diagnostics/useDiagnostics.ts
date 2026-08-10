/**
 * Was die Diagnose über das laufende System erfährt.
 *
 * Anders als Wasser, Energie und Heizung ist das hier **keine Deutung**,
 * sondern eine Abschrift: Dienstzustände, Adapter, Meldungen und die
 * Werkzeuge, die die Simulation anbietet. Die Diagnoseseite ist die einzige
 * Stelle, an der Kehler OS technische Rohdaten zeigt (Kapitel 7 §43) — und
 * genau deshalb darf sie hier nichts glätten.
 *
 * Zwei Takte, weil sich zwei verschiedene Dinge abspielen: Dienste, Adapter
 * und Meldungen werden zyklisch geholt — wer auf diese Seite schaut, will
 * sehen, dass sich etwas bewegt, und ein Neustartzähler, der erst beim
 * nächsten Sensorwert hochspringt, wäre irreführend. Welche Werkzeuge die
 * Simulation anbietet, steht dagegen beim Start fest: Die Betriebsart ist zur
 * Laufzeit nicht umschaltbar (Kapitel 15 §96), also wird das einmal geholt
 * und nicht sekündlich neu gefragt.
 *
 * Der Takt entspricht dem Alterungsintervall des Backends. Schneller zu
 * fragen bringt keine neue Auskunft, sondern nur Last auf einem Rechner, der
 * gleichzeitig das Fahrzeug bedient.
 */

import { useEffect, useState } from "react";
import { useAppState } from "../realtime/hooks";

export interface ServiceStatus {
  state: "STOPPED" | "STARTING" | "RUNNING" | "RESTARTING" | "FAILED";
  restarts: number;
  /** Laufzeit in Sekunden. `null`, solange der Dienst nicht läuft. */
  uptime_s: number | null;
  /** Der technische Rohtext des letzten Fehlers — bleibt der Diagnose vorbehalten. */
  last_error: string | null;
}

export interface AdapterInfo {
  name: string;
  link: string;
  source: string;
  entities: number;
  poll_interval_s: number;
}

export interface AlertItem {
  id: string;
  type: string;
  entity_id: string | null;
  severity: "INFO" | "NOTICE" | "WARNING" | "CRITICAL";
  state: string;
  message_key: string;
  params: Record<string, string>;
  raised_at: string;
}

/**
 * Die Werkzeuge der Simulation — vom Backend gemeldet, nicht hier gewusst.
 *
 * Je Entity, nicht als Gesamtliste: Was geht, hängt vom Gerät ab. Ein Wert
 * lässt sich nur an Mess- und Sollwerten setzen, und „blockiert" bewirkt nur
 * an beweglichen Teilen etwas. Eine Gesamtliste müsste die Oberfläche selbst
 * auf die Entities herunterbrechen — und hätte damit eine zweite Wahrheit
 * über den Simulator.
 *
 * Eine Entity, die hier fehlt, wird gar nicht simuliert.
 */
export interface EntityTools {
  faults: string[];
  settable: boolean;
}

export interface SimulationTools {
  available: boolean;
  entities: Record<string, EntityTools>;
}

export interface Diagnostics {
  services: Record<string, ServiceStatus>;
  adapters: AdapterInfo[];
  alerts: AlertItem[];
  simulation: SimulationTools;
  /** Ob die letzte Abfrage durchgekommen ist. */
  reachable: boolean;
}

const EMPTY: Diagnostics = {
  services: {},
  adapters: [],
  alerts: [],
  simulation: { available: false, entities: {} },
  reachable: false,
};

async function get<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`/api/v1${path}`);
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function useDiagnostics(intervalMs = 2000): Diagnostics {
  const [live, setLive] = useState<Omit<Diagnostics, "simulation">>(EMPTY);
  const [simulation, setSimulation] = useState<SimulationTools>(EMPTY.simulation);
  const { connection } = useAppState();

  // Einmalig: Die Betriebsart steht beim Start fest und ist zur Laufzeit
  // nicht umschaltbar (Kapitel 15 §96). Sekündlich danach zu fragen, würde
  // eine Veränderlichkeit unterstellen, die es nicht gibt.
  useEffect(() => {
    let active = true;
    void get<SimulationTools>("/diagnostics/simulation", EMPTY.simulation).then(
      (tools) => active && setSimulation(tools),
    );
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function load(): Promise<void> {
      const [services, adapters, alerts] = await Promise.all([
        get<Record<string, ServiceStatus>>("/diagnostics/services", {}),
        get<AdapterInfo[]>("/diagnostics/adapters", []),
        get<AlertItem[]>("/alerts", []),
      ]);
      if (!active) return;

      // Kommt gar nichts zurück, wird der letzte Stand nicht als aktuell
      // ausgegeben. `reachable: false` sagt der Seite, dass sie ihn
      // kennzeichnen muss, statt ihn stillschweigend stehen zu lassen.
      setLive({
        services,
        adapters,
        alerts,
        reachable: adapters.length > 0 || Object.keys(services).length > 0,
      });
    }

    void load();
    const timer = window.setInterval(() => void load(), intervalMs);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [intervalMs, connection]);

  return { ...live, simulation };
}
