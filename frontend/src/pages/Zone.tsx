/**
 * Eine Temperaturzone — Grundlage der Seiten „Klima" und „Heizung".
 *
 * Beide Systeme sind getrennt und haben eigene Geräte, eigene Sollwerte und
 * eigene Reiter. Ihre **Darstellung** ist trotzdem dieselbe: IST, SOLL,
 * Ein/Aus. Zwei Kopien davon würden über kurz oder lang auseinanderlaufen —
 * und dann sähe ein Sollwert auf der einen Seite anders aus als auf der
 * anderen.
 *
 * Getrennt bleiben die Daten, nicht die Bausteine.
 *
 * ── Was hier bewusst fehlt ────────────────────────────────────────────────
 *
 * Kein „heizt gerade", kein Betriebsmodus, kein Warmwasser. Welche Geräte
 * verbaut sind, ist nicht bekannt (Punkt G1) — und ein Gerät mit eigener
 * Regelung darf nicht nachgebaut werden (Kapitel 12 §67, Kapitel 18 §29).
 */

import { Card, Row, StaleMark, Status, Toggle } from "../design/primitives";
import { Stepper } from "../design/stepper";
import { isOn, isUnknown, numberOf, useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { Quality } from "../realtime/types";
import { t } from "../i18n/de";
import "./zone.css";

const USABLE: readonly string[] = [Quality.Valid, Quality.Stale];

export interface ZoneProps {
  /** Überschrift der Seite. */
  title: string;
  /** Gemessene Temperatur. */
  actualId: string;
  /** Solltemperatur — einstellbar, sofern Grenzen konfiguriert sind. */
  targetId: string;
  /** Ein/Aus des Systems. */
  stateId: string;
  /** Zusätzliche Messwerte, die zu dieser Zone gehören. */
  extra?: { id: string; label: string }[];
  /** Was an dieser Stelle noch fehlt und warum. */
  notes: string[];
}

export function Zone({ title, actualId, targetId, stateId, extra = [], notes }: ZoneProps) {
  const { connection } = useAppState();
  const online = connection === "online";

  return (
    <div className="zone">
      <div className="zone__main">
        <Card title={title}>
          <div className="zone__hero">
            {/* Beide Blöcke tragen ihre Beschriftung, weil zwei Temperaturen
                nebeneinander stehen. Ohne sie wäre nicht zu sehen, welche
                gemessen und welche eingestellt ist. */}
            <MainReading entityId={actualId} online={online} />
            <TargetBlock targetId={targetId} online={online} system={title} />
          </div>

          <div className="zone__split">
            {extra.map((item) => (
              <Row key={item.id} label={item.label}>
                <Temperature entityId={item.id} online={online} inline />
              </Row>
            ))}
          </div>
        </Card>
      </div>

      <aside className="zone__side">
        <Card title={t("zone.system")}>
          <PowerRow entityId={stateId} online={online} />
        </Card>

        <Card title={t("zone.notesTitle")}>
          <ul className="zone__notes">
            {notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </Card>
      </aside>
    </div>
  );
}

/* ── Temperatur ──────────────────────────────────────────────────────────── */

/**
 * Die gemessene Temperatur mit ihrer Beschriftung.
 *
 * Die Beschriftung kommt aus der Entity und nicht aus der Seite. Damit heißt
 * derselbe Fühler auf Dashboard, Klima- und Heizungsseite gleich; stünde der
 * Text hier fest, ließe er sich an einer Stelle ändern und an zwei anderen
 * vergessen.
 */
function MainReading({ entityId, online }: { entityId: string; online: boolean }) {
  const entity = useEntity(entityId);
  const key = entity?.definition?.name_key;

  return (
    <div className="zone__block">
      <Temperature entityId={entityId} online={online} />
      <span className="zone__label">
        {key && t(key)}
        {entity?.state.quality === Quality.Stale && <StaleMark />}
      </span>
    </div>
  );
}

function Temperature({
  entityId,
  online,
  inline = false,
}: {
  entityId: string;
  online: boolean;
  inline?: boolean;
}) {
  const entity = useEntity(entityId);
  const value = numberOf(entity);
  const quality = entity?.state.quality;

  // Ohne Verbindung wird der zuletzt bekannte Wert weiter gezeigt, aber
  // sichtbar als veraltet — so hält es auch die Komponente `Value`. Ihn zu
  // leeren wäre kein Gewinn an Ehrlichkeit, sondern ein Verlust: „Verbindung
  // weg" sähe dann genauso aus wie „Fühler hat nie etwas gemeldet". Dass die
  // Werte nicht mehr aktuell sind, sagt das Banner über der Seite.
  const usable = value !== null && quality !== undefined && USABLE.includes(quality);
  const stale = quality === Quality.Stale || !online;

  const cls = inline ? "zone__inline" : "zone__reading";

  if (!usable) {
    return <span className={`${cls} ${cls}--unknown`}>{t("state.unknown")}</span>;
  }

  return (
    <span className={`${cls}${stale ? ` ${cls}--stale` : ""}`}>
      <span className="numeric">{value.toFixed(1)}</span>
      <span className="zone__unit">°C</span>
      {/* In der Zeile steht die Kennzeichnung am Wert — dort gibt es keine
          Beschriftungszeile, die sie tragen könnte. Bei getrennter
          Verbindung entfällt sie: Das sagt das Banner für die ganze Seite. */}
      {inline && quality === Quality.Stale && <StaleMark />}
    </span>
  );
}

/* ── Sollwert ────────────────────────────────────────────────────────────── */

function TargetBlock({
  targetId,
  online,
  system,
}: {
  targetId: string;
  online: boolean;
  /** Name des Systems — die Sprachausgabe soll Klima und Heizung
   *  auseinanderhalten können, auch wenn beide „Solltemperatur" heißen. */
  system: string;
}) {
  const target = useEntity(targetId);
  const definition = target?.definition;

  // Wie überall: Ohne Befehl gibt es kein Bedienelement. Bei einem Sollwert
  // heißt das konkret — ohne konfigurierte Obergrenze wird der Wert gezeigt,
  // aber nicht verstellt (Kapitel 18 §98).
  const adjustable = (definition?.capabilities ?? []).some((c) => c.verb === "set_value");
  const value = numberOf(target);
  const stale = target?.state.quality === Quality.Stale || !online;

  return (
    <div className="zone__block zone__block--target">
      {adjustable ? (
        <Stepper
          entityId={targetId}
          value={value}
          min={definition?.min_value ?? null}
          max={definition?.max_value ?? null}
          step={definition?.step ?? 1}
          unit="°C"
          decimals={1}
          label={`${system} ${t("zone.target")}`}
          stale={stale}
          disabled={!online}
        />
      ) : (
        /* Ohne konfigurierte Grenzen bleibt der Wert sichtbar, aber
           unverstellbar. */
        <Temperature entityId={targetId} online={online} inline />
      )}
      {/* Die Kennzeichnung „veraltet“ setzt der Stepper selbst — er kennt
          den Zustand seines Werts und trägt sie damit auf jeder Seite. */}
      <span className="zone__label">{t("zone.target")}</span>
    </div>
  );
}

/* ── Ein/Aus ─────────────────────────────────────────────────────────────── */

function PowerRow({ entityId, online }: { entityId: string; online: boolean }) {
  const entity = useEntity(entityId);
  const { pending, connection } = useAppState();
  const configured = entity?.definition?.configured ?? false;

  // Das Gerät benennt sich selbst: „Klimaanlage“ oder „Heizung“ steht in der
  // Konfiguration, nicht in dieser Datei. Ein bloßes „Ein/Aus“ ließe offen,
  // was da eingeschaltet wird.
  const label = entity?.definition?.name_key
    ? t(entity.definition.name_key)
    : t("zone.power");

  if (!configured) {
    return (
      <Row label={label}>
        <Status tone="unknown" label={t("state.notConfigured")} compact />
      </Row>
    );
  }

  return (
    <Row label={label}>
      <Toggle
        on={isOn(entity)}
        unknown={isUnknown(entity) || connection !== "online"}
        pending={pending.has(entityId)}
        disabled={!online}
        label={label}
        onChange={(next) =>
          sendCommand(entityId, "set_state", { state: next ? "ON" : "OFF" })
        }
      />
    </Row>
  );
}
