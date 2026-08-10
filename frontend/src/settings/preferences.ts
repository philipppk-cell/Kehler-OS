/**
 * Anzeigeeinstellungen dieses Geräts.
 *
 * ── Warum lokal und nicht im Backend ──────────────────────────────────────
 *
 * Kapitel 6 §13 trennt globale von benutzerspezifischen Einstellungen. Ein
 * Benutzersystem gibt es noch nicht (M7), und eine Einstellungspersistenz im
 * Backend ebenso wenig — der Zustand wird nach einem Neustart bewusst nicht
 * wiederhergestellt (Kapitel 6 §44).
 *
 * Es wäre also entweder eine Erfindung („global gespeichert", ist es nicht)
 * oder eine Halbwahrheit („folgt dir", tut es nicht). Was hier steht, ist
 * genau das, was es ist: **Einstellungen dieses einen Geräts.** Das iPad im
 * Fahrzeug hat seine, ein zweites Tablet hätte eigene. Die Oberfläche sagt
 * das auch so.
 *
 * Es geht ausschließlich um Darstellung. Nichts hier erreicht Fahrzeug-
 * hardware, und nichts hier verändert einen Zustand, den ein anderer Client
 * sieht.
 */

const KEY = "kehleros.preferences.v1";

export interface Preferences {
  /** Gedämpfte Darstellung für die Nacht (`:root[data-night]`). */
  night: boolean;
  /** Den Bildschirm wach halten, solange die Oberfläche sichtbar ist. */
  keepAwake: boolean;
}

export const DEFAULTS: Preferences = { night: false, keepAwake: false };

function read(): Preferences {
  try {
    const stored = window.localStorage.getItem(KEY);
    if (!stored) return DEFAULTS;
    const parsed = JSON.parse(stored) as Partial<Preferences>;

    // Feldweise übernommen und auf den Typ geprüft. Ein fremder oder älterer
    // Eintrag darf die Oberfläche nicht in einen undefinierten Zustand
    // bringen — dieselbe Haltung wie bei der Konfiguration im Backend
    // (Kapitel 15 §76).
    return {
      night: typeof parsed.night === "boolean" ? parsed.night : DEFAULTS.night,
      keepAwake:
        typeof parsed.keepAwake === "boolean" ? parsed.keepAwake : DEFAULTS.keepAwake,
    };
  } catch {
    return DEFAULTS;
  }
}

class PreferenceStore {
  private current: Preferences = read();
  private listeners = new Set<() => void>();

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getSnapshot = (): Preferences => this.current;

  set = <K extends keyof Preferences>(key: K, value: Preferences[K]): void => {
    if (this.current[key] === value) return;
    this.current = { ...this.current, [key]: value };
    this.persist();
  };

  reset = (): void => {
    this.current = DEFAULTS;
    this.persist();
  };

  private persist(): void {
    apply(this.current);
    try {
      window.localStorage.setItem(KEY, JSON.stringify(this.current));
    } catch {
      // Ein voller oder gesperrter Speicher darf die Bedienung nicht
      // aufhalten. Die Einstellung gilt für diese Sitzung, sie überlebt nur
      // den Neustart nicht.
    }
    for (const listener of this.listeners) listener();
  }
}

/** Überträgt die Einstellungen auf das Dokument. */
function apply(preferences: Preferences): void {
  document.documentElement.dataset.night = preferences.night ? "true" : "false";
}

export const preferences = new PreferenceStore();

/**
 * Wendet die gespeicherten Einstellungen beim Start an.
 *
 * Muss vor dem ersten Rendern laufen, sonst blitzt die helle Darstellung
 * kurz auf, bevor der Nachtmodus greift — nachts im Fahrzeug genau der
 * Moment, den diese Einstellung verhindern soll.
 */
export function applyStoredPreferences(): void {
  apply(preferences.getSnapshot());
}
