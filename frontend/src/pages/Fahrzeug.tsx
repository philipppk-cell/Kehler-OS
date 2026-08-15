/**
 * Fahrzeug — alles, was sich am Aufbau bewegt.
 *
 * Garagentor, Einstiegsstufe, Markise, Eingangstür. Das ist die einzige
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

import { Button, Card, Row, Status } from "../design/primitives";
import { IconAwning, IconDoor, IconGarage, IconStep } from "../design/icons";
import { VehicleDisplay } from "../vehicle3d/VehicleDisplay";
import { useVehicleState } from "../vehicle3d/useVehicleState";
import { Stellung, brauchtBestaetigung, useAktor } from "../control/actuator";
import { textOf, useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
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
        <Card title={t("vehicle.title")}>
          <div className="fahrzeug__scene">
            <VehicleDisplay state={useVehicleState()} />
          </div>
        </Card>

        <Card title={t("vehicle.movingParts")}>
          <PartRow
            entityId="vehicle.garage.door"
            icon={<IconGarage size={20} />}
            online={online}
          />
          <PartRow
            entityId="vehicle.step.entry"
            icon={<IconStep size={20} />}
            online={online}
          />
          <PartRow
            entityId="vehicle.awning.main"
            icon={<IconAwning size={20} />}
            online={online}
          />
        </Card>

        <Card title={t("vehicle.locks")}>
          <LockRow
            entityId="vehicle.door.main.lock"
            icon={<IconDoor size={20} />}
            online={online}
          />
        </Card>
      </div>

      <aside className="fahrzeug__side">
        <Card title={t("vehicle.sensors")}>
          <ContactRow entityId="vehicle.door.main" icon={<IconDoor size={18} />} />
        </Card>

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

/* ── Ein Kontakt ─────────────────────────────────────────────────────────── */

/**
 * Ein Sensor ohne Bedienung.
 *
 * Die Eingangstür meldet ihren Zustand, sie lässt sich nicht fahren. Deshalb
 * steht sie unter „Sensoren" und nicht bei den beweglichen Teilen — eine Tür
 * mit Schaltflächen, die nichts tun, wäre ein Versprechen.
 */
function ContactRow({ entityId, icon }: { entityId: string; icon: JSX.Element }) {
  const entity = useEntity(entityId);
  const { connection } = useAppState();
  const name = entity?.definition?.name_key ? t(entity.definition.name_key) : entityId;
  const value = connection === "online" ? textOf(entity) : null;

  return (
    <Row icon={icon} label={name}>
      {value === null ? (
        <Status tone="unknown" label={t("state.unknown")} compact />
      ) : (
        <Status
          tone={value === "CLOSED" ? "ok" : "warn"}
          label={t(`state.${value.toLowerCase()}`, value)}
          compact
        />
      )}
    </Row>
  );
}
