/**
 * WebSocket-Verbindung zum Backend.
 *
 * Ablauf: verbinden, Snapshot empfangen, danach nur noch Änderungen.
 * Nach einem Abbruch wird mit Backoff neu verbunden und ein **neuer**
 * Snapshot angefordert — der Client arbeitet nie mit seinem alten Stand
 * weiter (Kapitel 17 §105).
 */

import { store } from "./store";
import type { ServerMessage } from "./types";

const INITIAL_BACKOFF_MS = 500;
const MAX_BACKOFF_MS = 15_000;

export class RealtimeClient {
  private socket: WebSocket | null = null;
  private backoff = INITIAL_BACKOFF_MS;
  private timer: number | null = null;
  private closed = false;

  constructor(private readonly url: string) {}

  connect(): void {
    this.closed = false;
    this.open();
  }

  disconnect(): void {
    this.closed = true;
    if (this.timer !== null) window.clearTimeout(this.timer);
    this.socket?.close();
    this.socket = null;
  }

  private open(): void {
    store.setConnection(this.backoff === INITIAL_BACKOFF_MS ? "connecting" : "reconnecting");

    const socket = new WebSocket(this.url);
    this.socket = socket;

    socket.onopen = () => {
      this.backoff = INITIAL_BACKOFF_MS;
      store.setConnection("online");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data as string) as ServerMessage;
        if (message.type === "snapshot") store.applySnapshot(message.entities);
        else if (message.type === "delta") store.applyDelta(message.entity);
      } catch {
        // Eine unlesbare Nachricht darf die Verbindung nicht beenden.
        console.warn("Unlesbare Nachricht vom Backend verworfen");
      }
    };

    socket.onclose = () => {
      this.socket = null;
      if (this.closed) return;

      // Solange keine Verbindung besteht, sind die angezeigten Werte nicht
      // mehr belastbar. Die Oberfläche sagt das (siehe Shell).
      store.setConnection("offline");
      this.scheduleReconnect();
    };

    socket.onerror = () => socket.close();
  }

  private scheduleReconnect(): void {
    this.timer = window.setTimeout(() => this.open(), this.backoff);
    this.backoff = Math.min(this.backoff * 2, MAX_BACKOFF_MS);
  }
}

export function realtimeUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/v1/realtime`;
}
