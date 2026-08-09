/**
 * Der Client-seitige Zustandsspiegel.
 *
 * Bewusst ein *Spiegel*, kein eigener Zustand: Ein Tastendruck schreibt hier
 * nichts hinein. Er löst einen Befehl aus, und die Anzeige ändert sich, wenn
 * der Server es meldet (Kapitel 13 §3).
 *
 * Absichtlich ohne Zustandsbibliothek. Es gibt genau eine Quelle — den
 * WebSocket — und `useSyncExternalStore` bildet das ohne zusätzliche
 * Abhängigkeit ab (Kapitel 17 §81).
 */

import type { ConnectionState, EntityView, SystemInfo } from "./types";

export interface AppState {
  entities: Map<string, EntityView>;
  connection: ConnectionState;
  system: SystemInfo | null;
  /** Befehle, die gerade laufen — je Entity das Verb. */
  pending: Map<string, string>;
  /** Zuletzt fehlgeschlagener Befehl, für die Rückmeldung an den Benutzer. */
  lastError: { entityId: string; message: string; at: number } | null;
}

type Listener = () => void;

class Store {
  private state: AppState = {
    entities: new Map(),
    connection: "connecting",
    system: null,
    pending: new Map(),
    lastError: null,
  };

  private listeners = new Set<Listener>();

  subscribe = (listener: Listener): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getSnapshot = (): AppState => this.state;

  private emit(next: Partial<AppState>): void {
    this.state = { ...this.state, ...next };
    this.listeners.forEach((listener) => listener());
  }

  /** Vollständiger Ausgangszustand — ersetzt alles Bisherige. */
  applySnapshot(entities: EntityView[]): void {
    this.emit({
      entities: new Map(entities.map((entity) => [entity.entity_id, entity])),
    });
  }

  /**
   * Eine einzelne Änderung.
   *
   * Ältere Sequenznummern werden verworfen. Damit kann ein verzögertes
   * `OPENING` kein bereits bestätigtes `OPEN` überschreiben (Kapitel 13 §32).
   */
  applyDelta(entity: EntityView): void {
    const known = this.state.entities.get(entity.entity_id);
    if (known && entity.seq <= known.seq) return;

    const entities = new Map(this.state.entities);
    // Die Definition kommt nur im Snapshot mit; sie bleibt erhalten.
    entities.set(entity.entity_id, {
      ...entity,
      definition: entity.definition ?? known?.definition,
    });
    this.emit({ entities });
  }

  setConnection(connection: ConnectionState): void {
    this.emit({ connection });
  }

  setSystem(system: SystemInfo): void {
    this.emit({ system });
  }

  setPending(entityId: string, verb: string | null): void {
    const pending = new Map(this.state.pending);
    if (verb === null) pending.delete(entityId);
    else pending.set(entityId, verb);
    this.emit({ pending });
  }

  setError(entityId: string, message: string): void {
    this.emit({ lastError: { entityId, message, at: Date.now() } });
  }

  clearError(): void {
    this.emit({ lastError: null });
  }
}

export const store = new Store();
