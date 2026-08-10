/**
 * Den Bildschirm wach halten.
 *
 * Ein fest verbautes Bedienpanel, das nach zwei Minuten schwarz wird, ist
 * kein Bedienpanel. Der Browser kann das verhindern — aber nur unter
 * Bedingungen, die hier nicht verschwiegen werden:
 *
 * ── Die Sperre überlebt kein Wegblenden ───────────────────────────────────
 *
 * Wechselt das Tablet die App oder sperrt sich, gibt das Betriebssystem die
 * Sperre frei. Sie muss beim Zurückkommen neu angefordert werden, sonst ist
 * die Einstellung nach dem ersten Wegblenden still wirkungslos. Genau das
 * macht der `visibilitychange`-Zweig.
 *
 * ── Sie braucht eine gesicherte Verbindung ────────────────────────────────
 *
 * Die Wake-Lock-Schnittstelle gibt es nur in einem *secure context* — also
 * über HTTPS oder auf `localhost`. Auf dem Fahrzeugrechner über einfaches
 * HTTP ist sie **nicht vorhanden**.
 *
 * Das wird nicht als „nicht unterstützt" abgetan, sondern benannt: Es ist
 * kein Mangel des Tablets, sondern eine Folge der Auslieferung, und damit ein
 * Argument für TLS im Fahrzeug (offener Punkt I3, Netzsegmentierung). Die
 * Oberfläche sagt deshalb, *warum* die Einstellung fehlt, statt sie
 * kommentarlos auszublenden.
 */

import { useEffect, useState } from "react";

export type WakeLockSupport = "available" | "insecure" | "unsupported";

interface SentinelLike {
  release: () => Promise<void>;
  addEventListener: (type: "release", listener: () => void) => void;
}

interface WakeLockLike {
  request: (type: "screen") => Promise<SentinelLike>;
}

function api(): WakeLockLike | null {
  const candidate = (navigator as Navigator & { wakeLock?: WakeLockLike }).wakeLock;
  return candidate ?? null;
}

export function wakeLockSupport(): WakeLockSupport {
  if (api() !== null) return "available";

  // Die Unterscheidung ist der Punkt: „Der Browser kann es nicht" und „diese
  // Verbindung ist ungesichert" führen zu völlig verschiedenen nächsten
  // Schritten.
  return window.isSecureContext ? "unsupported" : "insecure";
}

export type WakeLockState = "idle" | "held" | "denied";
/**
 * `denied` ist bewusst von `idle` getrennt.
 *
 * Das Betriebssystem kann die Anforderung ablehnen — etwa bei niedrigem
 * Akkustand oder im Stromsparmodus. Wer den Schalter umlegt und danach nur
 * „nicht aktiv" liest, sucht den Fehler bei sich oder bei der Software.
 * „Vom Gerät abgelehnt" benennt, wo die Entscheidung gefallen ist.
 */

/**
 * Hält den Bildschirm wach, solange `enabled` gilt und die Seite sichtbar ist.
 *
 * Gibt zurück, ob die Sperre gerade tatsächlich steht — nicht, ob sie
 * gewünscht ist. Eine Einstellung, die „ein" zeigt, während das Display
 * ausgeht, wäre eine Behauptung über einen Zustand (Kapitel 18 §37).
 */
export function useWakeLock(enabled: boolean): WakeLockState {
  const [state, setState] = useState<WakeLockState>("idle");

  useEffect(() => {
    const wakeLock = api();
    if (!enabled || wakeLock === null) {
      setState("idle");
      return;
    }

    let active = true;
    let sentinel: SentinelLike | null = null;

    async function acquire(): Promise<void> {
      if (!active || document.visibilityState !== "visible" || sentinel !== null) {
        return;
      }
      try {
        const next = await (wakeLock as WakeLockLike).request("screen");
        if (!active) {
          void next.release();
          return;
        }
        sentinel = next;
        setState("held");
        next.addEventListener("release", () => {
          sentinel = null;
          // Freigabe ist keine Ablehnung: Beim Wegblenden zieht das
          // Betriebssystem die Sperre regulär ein, und der
          // `visibilitychange`-Zweig fordert sie danach neu an.
          if (active) setState("idle");
        });
      } catch {
        // Abgelehnt — etwa bei niedrigem Akkustand. Das ist kein Fehler der
        // Oberfläche, aber auch nicht dasselbe wie „aus".
        if (active) setState("denied");
      }
    }

    function onVisibility(): void {
      if (document.visibilityState === "visible") void acquire();
    }

    void acquire();
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      active = false;
      document.removeEventListener("visibilitychange", onVisibility);
      void sentinel?.release();
      sentinel = null;
    };
  }, [enabled]);

  return state;
}
