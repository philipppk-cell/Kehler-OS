/**
 * Heizung — die SCHEER-Anlage.
 *
 * Verbaut ist eine **SCHEER selection 10/17 kW** mit der Steuerung **SCHEER
 * HeatMate V4.02**: zentrale Heizung und Warmwasserbereitung, zwei
 * Wärmequellen (Brenner und Elektroheizung), zwei Heizkreise — die
 * Heizkörper im Wohnraum und die Fußbodenheizung.
 *
 * Deshalb ist diese Seite ein Anlagen-Dashboard und kein Raumthermostat. Die
 * Frage, die sie beantworten muss, lautet nicht „wie warm hätten Sie es
 * gern", sondern **was macht die Anlage gerade** — welche Wärmequelle
 * arbeitet, welche Kreise laufen, welche Temperaturen liegen an, liegt eine
 * Störung vor.
 *
 * ── Kehler OS regelt hier nichts ──────────────────────────────────────────
 *
 * Die HeatMate bleibt Regler und Schutzeinrichtung. Temperaturbegrenzer,
 * Brennersteuerung und Abschaltungen gehören ihr und werden weder nachgebaut
 * noch umgangen (Kapitel 12 §33/§67, Kapitel 18 §29). Diese Seite bedient und
 * zeigt an.
 *
 * ── Warum fast alles „noch zu verifizieren" ist ───────────────────────────
 *
 * Die Modbus-Registerliste der HeatMate liegt nicht vor (Punkt G1). Die
 * Anlage ist in `config/vehicle/vehicle.yaml` bereits vollständig
 * beschrieben, aber jede Funktion trägt `unverified`. Der Loader gibt einer
 * unverifizierten Entity **keine Befehle** — also entsteht hier auch kein
 * Bedienelement. Die Struktur steht, die Bedienung entsteht mit der
 * Bestätigung.
 *
 * Das ist kein Platzhalter-Zustand, den man wegdrücken sollte: Er ist die
 * ehrliche Darstellung dessen, was heute bekannt ist.
 */

import { createContext, useContext, type ReactNode } from "react";
import { Card, Row, StaleMark, Status, Toggle, type Tone } from "../design/primitives";
import { Stepper } from "../design/stepper";
import { IconHeating, IconPlug, IconWarning } from "../design/icons";
import { useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { Quality, type EntityView } from "../realtime/types";
import { useHeating, type HeatingSummary } from "../heating/useHeating";
import { t } from "../i18n/de";
import "./heizung.css";

const USABLE: readonly string[] = [Quality.Valid, Quality.Stale];

/**
 * Was jedes Feld dieser Seite wissen muss.
 *
 * Als Kontext und nicht als Prop, weil die Seite rund zwanzig Felder hat und
 * dieselben zwei Angaben sonst durch jede Zwischenebene gereicht würden.
 *
 * `explain` ist die Antwort auf ein Problem, das erst sichtbar wurde, als die
 * Seite lief: Ist **die ganze Anlage** unbestätigt, stand hinter jeder Zeile
 * „Noch zu verifizieren" — zweiundzwanzigmal derselbe Satz. Gesagt wird er
 * dann einmal in der Karte „Anbindung"; die Zeilen bleiben ruhig. Sobald ein
 * Teil der Anlage angebunden ist, kehrt der Hinweis an die Zeilen zurück, wo
 * er dann tatsächlich unterscheidet.
 */
const Plant = createContext<{ online: boolean; explain: boolean }>({
  online: false,
  explain: true,
});

export function Heizung() {
  const heating = useHeating();
  const { connection } = useAppState();
  const online = connection === "online";

  // Ist die ganze Anlage unbestätigt, erklärt das die Karte „Anbindung" —
  // dann bleiben die Zeilen ruhig.
  const explain = heating?.linked ?? false;

  return (
    <Plant.Provider value={{ online, explain }}>
      <div className="heizung">
        <div className="heizung__main">
          <PlantCard heating={heating} />
          <CircuitsCard />
          <WaterCard />
          <ElectricCard />
        </div>

        <aside className="heizung__side">
          <LinkCard heating={heating} />
          <BurnerCard />
          <SupplyCard />
          <NoteCard />
        </aside>
      </div>
    </Plant.Provider>
  );
}

/* ── Anlage ──────────────────────────────────────────────────────────────── */

/**
 * Der Kopf der Seite: Was macht die Anlage gerade?
 *
 * Die Wärmequelle steht groß, weil sie die Frage beantwortet, mit der man auf
 * diese Seite kommt. Sie kommt aus dem Backend und ist dort aus zwei Werten
 * zusammengesetzt — hier wird sie nur angezeigt.
 */
function PlantCard({ heating }: { heating: HeatingSummary | null }) {
  const { online } = useContext(Plant);
  const source = online ? heating?.heat_source ?? null : null;

  return (
    <Card title={t("heating.plantTitle")} icon={<IconHeating size={18} />}>
      <div className="heizung__hero">
        <div className="heizung__block">
          <span className={`heizung__source${source ? "" : " heizung__source--unknown"}`}>
            {source ? t(`heating.source.${source}`) : t("state.unknown")}
          </span>
          <span className="heizung__label">{t("heating.source")}</span>
        </div>

        {/* Eine Temperatur, ein Sollwert. Die Anlage führt Kessel und
            Warmwasser nicht getrennt (BESTÄTIGT 2026-08-10) — zwei Werte
            anzuzeigen hieße, eine Genauigkeit zu behaupten, die sie nicht
            hat. */}
        <Field entityId="heating.temperature.actual" size="metric" />
        <Field entityId="heating.temperature.target" size="metric" />
      </div>

      <div className="heizung__split">
        <FieldRow entityId="heating.burner.state" prefix="heating.phase" />
        <FieldRow entityId="heating.system.state" />
        <FieldRow entityId="heating.night.state" />
      </div>

      <FaultLine heating={heating} />
    </Card>
  );
}

/**
 * Die Störmeldung.
 *
 * Drei Antworten, nicht zwei: gemeldet, nicht gemeldet, unbekannt. Solange
 * die Anlage nichts sagt, ist „keine Störung" die gefährlichere der beiden
 * Behauptungen (Kapitel 18 §38).
 */
function FaultLine({ heating }: { heating: HeatingSummary | null }) {
  const { online } = useContext(Plant);
  const fault = online ? heating?.fault ?? null : null;
  const tone: Tone = fault === null ? "unknown" : fault ? "error" : "ok";
  const label =
    fault === null
      ? t("heating.faultUnknown")
      : fault
        ? t("heating.faultPresent")
        : t("heating.faultNone");

  return (
    <div className="heizung__fault">
      <Status tone={tone} label={label} />
      {fault === true && <ErrorCode />}
    </div>
  );
}

/**
 * Der Fehlercode der Anlage — nur, wenn es einen gibt.
 *
 * Er steht neben der Störmeldung und nicht als eigene Zeile: Ohne Störung
 * gibt es nichts zu zeigen, und eine dauerhaft leere Zeile „Fehlercode" wäre
 * eine Frage, die die Seite nie beantwortet.
 *
 * Kehler OS deutet ihn nicht. Was die HeatMate meldet, wird weitergegeben —
 * eine eigene Diagnose zu stellen, steht der Software nicht zu
 * (Kapitel 13 §60).
 */
function ErrorCode() {
  const entity = useEntity("heating.system.error_code");
  const { quality, value } = entity?.state ?? {};
  if (value === null || value === undefined || !USABLE.includes(quality ?? "")) {
    return null;
  }
  return <span className="heizung__value">{String(value)}</span>;
}

/* ── Heizkreise ──────────────────────────────────────────────────────────── */

/**
 * Die beiden Kreise mit ihren Pumpen.
 *
 * Kreis und Pumpe stehen getrennt, weil sie es an der Anlage auch sind: Ein
 * angeforderter Kreis mit stehender Pumpe ist genau der Fall, den man sehen
 * will. Ob die HeatMate die Pumpen einzeln zurückmeldet, klärt erst die
 * Registerliste.
 */
function CircuitsCard() {
  return (
    <Card title={t("heating.circuitsTitle")}>
      <div className="heizung__split">
        <CircuitRow stateId="heating.radiators.state" pumpId="heating.radiators.pump" />
        <CircuitRow stateId="heating.floor.state" pumpId="heating.floor.pump" />
      </div>
    </Card>
  );
}

function CircuitRow({ stateId, pumpId }: { stateId: string; pumpId: string }) {
  const circuit = useEntity(stateId);

  return (
    <div className="circuit">
      <span className="circuit__name">{nameOf(circuit, stateId)}</span>
      <span className="circuit__pump">
        <span className="circuit__pumplabel">{t("heating.pump")}</span>
        <Field entityId={pumpId} />
      </span>
      <span className="circuit__state">
        <Field entityId={stateId} />
      </span>
    </div>
  );
}

/* ── Warmwasser ──────────────────────────────────────────────────────────── */

function WaterCard() {
  return (
    <Card title={t("heating.waterTitle")}>
      <div className="heizung__split">
        <FieldRow entityId="heating.water.state" />
        <FieldRow entityId="heating.water.plus" />
        <FieldRow entityId="heating.water.circulation" />
      </div>
    </Card>
  );
}

/* ── Elektroheizung ──────────────────────────────────────────────────────── */

function ElectricCard() {
  return (
    <Card title={t("heating.electricTitle")} icon={<IconPlug size={18} />}>
      <div className="heizung__split">
        <FieldRow entityId="heating.electric.state" />
        <FieldRow entityId="heating.electric.mode" prefix="heating.mode" />
        {/* Stufe und Leistung sind dasselbe: Stufe 2 ist 2 kW. */}
        <FieldRow entityId="heating.electric.power" />
      </div>
    </Card>
  );
}

/* ── Brenner ─────────────────────────────────────────────────────────────── */

function BurnerCard() {
  return (
    <Card title={t("heating.burnerTitle")}>
      <div className="heizung__split">
        <FieldRow entityId="heating.burner.hours" />
        <FieldRow entityId="heating.service.due" prefix="heating.service" />
      </div>
    </Card>
  );
}

/* ── Versorgung ──────────────────────────────────────────────────────────── */

/**
 * Woran die Elektroheizung hängt.
 *
 * Ob sie arbeiten kann, ist keine Frage an die Heizung, sondern an die
 * 230-V-Versorgung — deshalb steht sie hier und nicht nur auf der
 * Energieseite.
 */
function SupplyCard() {
  return (
    <Card title={t("heating.supplyTitle")}>
      <div className="heizung__split">
        <FieldRow entityId="heating.supply.mains" prefix="heating.mains" />
        <FieldRow entityId="heating.supply.wakeup" />
        <FieldRow entityId="heating.tank.level" />
      </div>
    </Card>
  );
}

/* ── Anbindung ───────────────────────────────────────────────────────────── */

/**
 * Der Stand der Integration — einmal erklärt statt zwanzigmal angedeutet.
 *
 * Ohne diese Karte wäre die Seite eine Liste unerklärter Leerstellen. Mit ihr
 * ist sie eine ehrliche Aussage: Die Anlage ist beschrieben, die Werte fehlen,
 * und der Grund dafür steht dabei.
 */
function LinkCard({ heating }: { heating: HeatingSummary | null }) {
  const linked = heating?.linked ?? false;
  const pending = heating?.unverified ?? 0;

  if (linked) return null;

  return (
    <Card title={t("heating.linkTitle")} icon={<IconWarning size={18} />} emphasis>
      <div className="heizung__link">
        <Status tone="warn" label={t("heating.notLinked")} />
        <p className="heizung__linkhint">{t("heating.notLinkedHint")}</p>
        {pending > 0 && (
          <p className="heizung__pending">
            {t("heating.pendingCount", undefined, { count: String(pending) })}
          </p>
        )}
        <p className="heizung__chain">{t("heating.chain")}</p>
      </div>
    </Card>
  );
}

/* ── Hinweise ────────────────────────────────────────────────────────────── */

function NoteCard() {
  return (
    <Card title={t("heating.notesTitle")}>
      <p className="heizung__plant">
        {t("heating.plant")} · {t("heating.controller")}
      </p>
      <ul className="heizung__notes">
        <li>{t("heating.noteControl")}</li>
        <li>{t("heating.noteVerify")}</li>
        <li>{t("heating.noteSource")}</li>
      </ul>
    </Card>
  );
}

/* ── Ein Wert der Anlage ─────────────────────────────────────────────────── */

/**
 * Eine Zeile mit Namen und Wert.
 *
 * Der Name kommt aus der Entity und nicht aus der Seite — sonst hieße
 * derselbe Wert hier anders als im Dashboard.
 */
function FieldRow({ entityId, prefix }: { entityId: string; prefix?: string }) {
  const entity = useEntity(entityId);

  return (
    <Row label={nameOf(entity, entityId)}>
      <Field entityId={entityId} prefix={prefix} />
    </Row>
  );
}

/**
 * Der Wert selbst — in der Form, die die Entity zulässt.
 *
 * Was hier erscheint, entscheidet **nicht** diese Datei, sondern die Entity:
 * Ein Schalter entsteht nur, wenn ein `set_state` existiert, ein Stepper nur
 * bei `set_value` mit Grenzen. Solange eine Funktion nicht bestätigt ist,
 * erzeugt der Loader keine Befehle — und hier erscheint folgerichtig kein
 * Bedienelement, sondern der Hinweis, dass die Bestätigung aussteht.
 *
 * Die drei Abwesenheiten werden auseinandergehalten, weil sie verschiedene
 * Dinge bedeuten:
 *
 *   nicht vorhanden        Die Entity gibt es in dieser Konfiguration nicht.
 *   noch zu verifizieren   Ob die Funktion über die Schnittstelle verfügbar
 *                          ist, ist offen (Punkt G1).
 *   nicht konfiguriert     Die Funktion gibt es, ihr fehlt die Zuordnung.
 */
function Field({
  entityId,
  prefix,
  size = "inline",
}: {
  entityId: string;
  prefix?: string;
  size?: "inline" | "metric";
}) {
  const { online, explain } = useContext(Plant);
  const entity = useEntity(entityId);
  const { pending } = useAppState();
  const definition = entity?.definition;
  const name = nameOf(entity, entityId);

  const absent = (label: string, title?: string) => (
    <Absent label={label} title={title} size={size} name={name} explain={explain} />
  );

  /* Ein Bedienelement im Kopfbereich trägt dieselbe Beschriftung wie ein
     Wert an derselben Stelle. Ohne sie stünde dort ein Stepper ohne Angabe,
     was er verstellt — und die leere Fassung derselben Stelle hätte eine
     Beschriftung, die bebilderte nicht. */
  const framed = (control: ReactNode) =>
    size === "metric" ? (
      <div className="heizung__block">
        {control}
        <span className="heizung__label">{name}</span>
      </div>
    ) : (
      control
    );

  if (!definition) return absent(t("state.unavailable"));

  if (definition.unverified) {
    return absent(t("state.unverified"), t("state.unverifiedHint"));
  }

  if (!definition.configured) return absent(t("state.notConfigured"));

  const capabilities = definition.capabilities ?? [];
  const { quality, value } = entity.state;
  const usable = value !== null && USABLE.includes(quality);
  const stale = quality === Quality.Stale || !online;

  if (capabilities.some((c) => c.verb === "set_state")) {
    return framed(
      <Toggle
        on={usable && value === "ON"}
        unknown={!usable || !online}
        pending={pending.has(entityId)}
        disabled={!online}
        label={name}
        onChange={(next) =>
          sendCommand(entityId, "set_state", { state: next ? "ON" : "OFF" })
        }
      />,
    );
  }

  if (capabilities.some((c) => c.verb === "set_value")) {
    return framed(
      <Stepper
        entityId={entityId}
        value={typeof value === "number" && usable ? value : null}
        min={definition.min_value}
        max={definition.max_value}
        step={definition.step ?? 1}
        unit={unitOf(definition.unit)}
        decimals={definition.step && definition.step < 1 ? 1 : 0}
        label={name}
        stale={stale}
        disabled={!online}
      />,
    );
  }

  if (!usable) return absent(t("state.unknown"));

  const cls = size === "metric" ? "heizung__metric" : "heizung__value";
  const numeric = typeof value === "number";

  return (
    <span className={`${cls}${stale ? ` ${cls}--stale` : ""}`}>
      <span className={numeric ? "numeric" : undefined}>
        {numeric
          ? value.toFixed(definition.unit === "celsius" ? 1 : 0)
          : label(String(value), prefix)}
      </span>
      {numeric && <span className="heizung__unit">{unitOf(definition.unit)}</span>}
      {size === "metric" && <span className="heizung__label">{name}</span>}
      {quality === Quality.Stale && <StaleMark />}
    </span>
  );
}

/**
 * Eine Stelle ohne Wert — ruhig und hochwertig, nie als „TODO"
 * (Kapitel 18 §101).
 *
 * `explain` entscheidet, ob der Grund danebensteht. Ist die ganze Anlage
 * unbestätigt, steht er einmal in der Karte „Anbindung"; ihn zusätzlich an
 * zwanzig Zeilen zu schreiben, macht die Seite nicht ehrlicher, nur lauter.
 * Über den Tooltip bleibt er in beiden Fällen erreichbar.
 *
 * Ein großer Wert behält auch in seiner Abwesenheit die Beschriftung —
 * sonst stünde dort ein Strich, von dem niemand wüsste, wofür er steht.
 */
function Absent({
  label,
  title,
  size,
  name,
  explain,
}: {
  label: string;
  title?: string;
  size: "inline" | "metric";
  name: string;
  explain: boolean;
}): ReactNode {
  const cls = size === "metric" ? "heizung__metric" : "heizung__value";

  if (size === "metric") {
    return (
      <div className="heizung__block">
        <span className={`${cls} ${cls}--absent`} title={title ?? label}>
          {explain ? label : "—"}
        </span>
        <span className="heizung__label">{name}</span>
      </div>
    );
  }

  return (
    <span
      className={`${cls} ${cls}--absent${explain ? " heizung__pendingmark" : ""}`}
      title={title ?? label}
    >
      {explain ? label : "—"}
    </span>
  );
}

/* ── Kleinkram ───────────────────────────────────────────────────────────── */

/** Der Name einer Entity, notfalls ihre Kennung. */
function nameOf(entity: EntityView | undefined, fallback: string): string {
  const key = entity?.definition?.name_key;
  return key ? t(key, fallback) : fallback;
}

/** Ein Zustandswort in seiner übersetzten Form, notfalls im Original. */
function label(value: string, prefix?: string): string {
  if (prefix) return t(`${prefix}.${value}`, value);
  if (value === "ON") return t("state.on");
  if (value === "OFF") return t("state.off");
  if (value === "OPEN") return t("state.open");
  if (value === "CLOSED") return t("state.closed");
  return value;
}

function unitOf(unit: string | null): string {
  if (!unit) return "";
  return { celsius: "°C", percent: "%", W: "W", h: "h", V: "V", A: "A" }[unit] ?? unit;
}
