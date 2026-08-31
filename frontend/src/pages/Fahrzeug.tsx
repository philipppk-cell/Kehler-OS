/**
 * Fahrzeug — alles, was sich am Aufbau bewegt.
 *
 * Garagentor, Terrasse, Markise, Eingangstür. Das ist die einzige
 * Seite, auf der Kehler OS **Mechanik in Bewegung setzt**, und sie ist
 * entsprechend gebaut.
 *
 * ── Warum bewegliche Teile anders sind ────────────────────────────────────
 *
 * Ein Schalter kennt zwei Zustände, ein bewegliches Teil sechs: geschlossen,
 * öffnend, offen, schließend, gestoppt, blockiert. Vier davon sind keine
 * Endlagen. Daraus folgt fast alles auf dieser Seite:
 *
 * * **Der Stopp ist immer erreichbar.** Solange etwas fährt, ist er die
 *   wichtigste Schaltfläche auf dem Bildschirm — und er wird nie deshalb
 *   gesperrt, weil gerade eine Bewegung läuft. Das wäre genau verkehrt.
 * * **Eine Bewegung ist kein Ergebnis.** Während „öffnet" läuft, behauptet
 *   die Seite nicht „offen" (Kapitel 18 §37).
 * * **Blockiert ist ein eigener Zustand**, nicht „irgendwo dazwischen". Wo
 *   ein klemmendes Teil steht, weiß niemand — also wird es nicht gezeichnet
 *   und nicht behauptet.
 *
 * ── Was hier bewusst fehlt ────────────────────────────────────────────────
 *
 * Fenster und Verriegelungen. Kapitel 18 §17 nennt sie, aber es gibt keine
 * Entities dafür — und ohne Entity kein Bedienelement (Kapitel 18 §98).
 *
 * Ebenso fehlt eine Gesamtbewertung „abfahrbereit". Sie ist ausdrücklich
 * abbestellt (W11): Die Einzelzustände stehen hier vollständig, die
 * zusammenfassende Ja/Nein-Aussage gibt es nicht.
 */

import { useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { Button, Card, Status } from "../design/primitives";
import { IconAwning, IconDoor, IconGarage, IconStep } from "../design/icons";
import { Stellung, brauchtBestaetigung, useAktor } from "../control/actuator";
import { useAppState } from "../realtime/hooks";
import { renewHold, sendCommand } from "../api/client";
import { t } from "../i18n/de";
import "./fahrzeug.css";

/** Zustände, in denen etwas tatsächlich fährt. */
const MOVING: readonly string[] = ["OPENING", "CLOSING"];

export function Fahrzeug() {
  const { connection } = useAppState();
  const online = connection === "online";

  return (
    <div className="fahrzeug">
      <div className="fahrzeug__main">
        <Card title={t("vehicle.movingParts")}>
          <PartRow
            entityId="vehicle.garage.door"
            icon={<IconGarage size={20} />}
            online={online}
          />
          <HoldPartRow
            entityId="vehicle.terrace.main"
            icon={<IconStep size={20} />}
            online={online}
          />
          <HoldPartRow
            entityId="vehicle.awning.main"
            icon={<IconAwning size={20} />}
            online={online}
          />

          <LockRow
            entityId="vehicle.door.main.lock"
            icon={<IconDoor size={20} />}
            online={online}
          />
        </Card>
      </div>

      <aside className="fahrzeug__side">
        <Card title={t("vehicle.notesTitle")}>
          <ul className="fahrzeug__notes">
            <li>{t("vehicle.noteStop")}</li>
            <li>{t("vehicle.noteMissing")}</li>
            <li>{t("vehicle.noteNoReadiness")}</li>
          </ul>
        </Card>
      </aside>
    </div>
  );
}

/* ── Ein bewegliches Teil ────────────────────────────────────────────────── */

/**
 * Eine Zeile mit Zustand und Fahrbefehlen.
 *
 * Welche Schaltflächen erscheinen, entscheidet die Entity und nicht diese
 * Datei: Ohne `open` gibt es kein Öffnen. Bei nicht zugeordneter Hardware
 * bleibt die Zeile ruhig stehen und bietet nichts an (Kapitel 18 §101).
 */
function PartRow({
  entityId,
  icon,
  online,
}: {
  entityId: string;
  icon: JSX.Element;
  online: boolean;
}) {
  const aktor = useAktor(entityId);
  const faehrt = aktor.zustand !== null && MOVING.includes(aktor.zustand);

  function drive(verb: string) {
    // Ob eine Bestätigung nötig ist, steht in der Capability und nicht hier.
    // Die Oberfläche liest die Einstufung, sie erfindet sie nicht
    // (Kapitel 15 §21).
    if (
      brauchtBestaetigung(aktor.entity, verb) &&
      !window.confirm(t("vehicle.confirmMove", undefined, { name: aktor.name }))
    ) {
      return;
    }
    sendCommand(entityId, verb);
  }

  return (
    <div className="part">
      <span className="part__icon">{icon}</span>

      <span className="part__name">{aktor.name}</span>

      <span className="part__state">
        <Stellung aktor={aktor} />
      </span>

      <span className="part__controls">
        {aktor.konfiguriert && (
          <>
            {/* Nur Schaltflächen für Befehle, die es gibt.
                Die Heckklappe kennt seit dem 2026-08-12 nur `open` — sie wird
                von Gasdruckdämpfern aufgedrückt und von Hand zugedrückt. Eine
                ausgegraute Schaltfläche „Schließen" wäre die Behauptung, das
                ginge grundsätzlich schon und sei nur gerade gesperrt
                (Kapitel 12 §55). */}
            {aktor.verben.has("open") && (
              <Button
                disabled={!online || aktor.laeuft || faehrt}
                onClick={() => drive("open")}
              >
                {t("vehicle.open")}
              </Button>
            )}
            {aktor.verben.has("close") && (
              <Button
                disabled={!online || aktor.laeuft || faehrt}
                onClick={() => drive("close")}
              >
                {t("vehicle.close")}
              </Button>
            )}
            {/* Der Stopp ist **nicht** deshalb gesperrt, weil eine Bewegung
                läuft — das ist genau der Moment, in dem er gebraucht wird.
                Solange etwas fährt, hebt er sich zusätzlich ab. */}
            {aktor.verben.has("stop") && (
              <Button
                variant={faehrt ? "accent" : "default"}
                disabled={!online}
                onClick={() => sendCommand(entityId, "stop")}
              >
                {t("vehicle.stop")}
              </Button>
            )}
          </>
        )}
      </span>
    </div>
  );
}



/* ── Totmann-Bedienung für Hold-to-run-Aktoren ─────────────────────────────────────── */

const HOLD_HEARTBEAT_MS = 250;

function HoldPartRow({
  entityId,
  icon,
  online,
}: {
  entityId: string;
  icon: JSX.Element;
  online: boolean;
}) {
  const aktor = useAktor(entityId);
  const [pressed, setPressed] = useState<string | null>(null);

  const pressedRef = useRef<string | null>(null);
  const releasedRef = useRef(false);
  const stoppingRef = useRef(false);
  const generationRef = useRef(0);
  const heartbeatRef = useRef<number | null>(null);
  const startRef = useRef<Promise<unknown> | null>(null);

  function clearHeartbeat() {
    if (heartbeatRef.current !== null) {
      window.clearTimeout(heartbeatRef.current);
      heartbeatRef.current = null;
    }
  }

  function clearPressed() {
    pressedRef.current = null;
    setPressed(null);
  }

  function scheduleHeartbeat(verb: string, generation: number) {
    clearHeartbeat();

    heartbeatRef.current = window.setTimeout(async () => {
      if (
        releasedRef.current ||
        generationRef.current !== generation ||
        pressedRef.current !== verb
      ) {
        return;
      }

      const ok = await renewHold(entityId, verb);

      if (!ok) {
        // Keine weitere Bewegung anfordern. Der Backend-Watchdog setzt den
        // Ausgang zusätzlich selbst zurück, falls dieser Stop-Aufruf wegen
        // derselben Verbindungsstörung nicht mehr ankommt.
        releasedRef.current = true;
        generationRef.current += 1;
        clearHeartbeat();
        clearPressed();
        await sendCommand(entityId, "stop");
        return;
      }

      scheduleHeartbeat(verb, generation);
    }, HOLD_HEARTBEAT_MS);
  }

  async function startHold(
    verb: "open" | "close",
    event: ReactPointerEvent<HTMLButtonElement>,
  ) {
    if (!online || pressedRef.current !== null || stoppingRef.current) {
      return;
    }

    event.preventDefault();

    try {
      event.currentTarget.setPointerCapture(event.pointerId);
    } catch {
      // Pointer Capture ist Komfort, nicht Sicherheitsfunktion.
      // Der Backend-Watchdog bleibt unabhängig davon aktiv.
    }

    const generation = generationRef.current + 1;
    generationRef.current = generation;
    releasedRef.current = false;
    pressedRef.current = verb;
    setPressed(verb);

    const start = sendCommand(entityId, verb);
    startRef.current = start;

    const result = await start;

    if (startRef.current === start) {
      startRef.current = null;
    }

    if (
      releasedRef.current ||
      generationRef.current !== generation ||
      pressedRef.current !== verb
    ) {
      return;
    }

    if (!result?.success) {
      releasedRef.current = true;
      clearPressed();
      return;
    }

    scheduleHeartbeat(verb, generation);
  }

  async function stopHold() {
    if (
      stoppingRef.current ||
      (pressedRef.current === null && startRef.current === null)
    ) {
      return;
    }

    stoppingRef.current = true;
    releasedRef.current = true;
    generationRef.current += 1;
    clearHeartbeat();

    try {
      // Falls der Finger extrem kurz auflag, darf STOP nicht vor dem noch
      // laufenden START am Server ankommen. Erst Start beenden, dann Stop.
      const start = startRef.current;
      if (start !== null) {
        await start;
      }

      await sendCommand(entityId, "stop");
    } finally {
      startRef.current = null;
      clearPressed();
      stoppingRef.current = false;
    }
  }

  const status =
    pressed === "open"
      ? t("vehicle.extending")
      : pressed === "close"
        ? t("vehicle.retracting")
        : t("vehicle.holdIdle");

  return (
    <div className="part part--hold">
      <span className="part__icon">{icon}</span>
      <span className="part__name">{aktor.name}</span>

      <span className="part__state">
        <Status
          tone={pressed !== null ? "accent" : "unknown"}
          label={status}
          compact
        />
      </span>

      <span className="part__controls">
        {aktor.konfiguriert && (
          <>
            <Button
              variant={pressed === "open" ? "accent" : "default"}
              disabled={!online || pressed === "close"}
              onPointerDown={(event) => void startHold("open", event)}
              onPointerUp={() => void stopHold()}
              onPointerCancel={() => void stopHold()}
              onLostPointerCapture={() => void stopHold()}
            >
              {t("vehicle.extend")}
            </Button>

            <Button
              variant={pressed === "close" ? "accent" : "default"}
              disabled={!online || pressed === "open"}
              onPointerDown={(event) => void startHold("close", event)}
              onPointerUp={() => void stopHold()}
              onPointerCancel={() => void stopHold()}
              onLostPointerCapture={() => void stopHold()}
            >
              {t("vehicle.retract")}
            </Button>
          </>
        )}
      </span>
    </div>
  );
}

/* ── Eine Verriegelung ohne Stellungsrückmeldung ─────────────────────────── */

function LockRow({
  entityId,
  icon,
  online,
}: {
  entityId: string;
  icon: JSX.Element;
  online: boolean;
}) {
  const aktor = useAktor(entityId);

  function schalten(verb: string) {
    if (
      brauchtBestaetigung(aktor.entity, verb) &&
      !window.confirm(
        t("vehicle.confirmMove", undefined, { name: aktor.name }),
      )
    ) {
      return;
    }

    sendCommand(entityId, verb);
  }

  return (
    <div className="part">
      <span className="part__icon">{icon}</span>
      <span className="part__name">{aktor.name}</span>

      <span className="part__state">
        <Stellung aktor={aktor} offenTon="neutral" />
      </span>

      <span className="part__controls">
        {aktor.konfiguriert && (
          <>
            {aktor.verben.has("open") && (
              <Button
                disabled={!online || aktor.laeuft}
                onClick={() => schalten("open")}
              >
                {t("vehicle.unlock")}
              </Button>
            )}

            {aktor.verben.has("close") && (
              <Button
                disabled={!online || aktor.laeuft}
                onClick={() => schalten("close")}
              >
                {t("vehicle.lock")}
              </Button>
            )}
          </>
        )}
      </span>
    </div>
  );
}
