/**
 * Die Energieseite.
 *
 * Sie beantwortet zwei Fragen: **Wie voll ist die Batterie, und woher kommt
 * gerade der Strom?**
 *
 * Der Energiefluss steht deshalb im Mittelpunkt. Er zeigt vier Größen und
 * die Richtung dazwischen — nicht mehr. Ein Diagramm mit zwanzig Zahlen
 * beantwortet keine Frage, es stellt neue (Kapitel 8 §1).
 *
 * **Kehler OS regelt nicht.** Victron bleibt Energiemanagement und
 * Schutzinstanz (Kapitel 12 §33). Schreibend gibt es genau zwei Funktionen,
 * beide bestätigungspflichtig — und die Strombegrenzung erscheint erst, wenn
 * die reale Absicherung des Anschlusses bekannt ist.
 */

import { Card, Row, StaleMark, Status, type Tone } from "../design/primitives";
import { Stepper } from "../design/stepper";
import { IconPlug, IconSolar } from "../design/icons";
import { useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { Quality } from "../realtime/types";
import { useEnergy, type Direction, type EnergySummary, type Reading } from "../energy/useEnergy";
import { HistoryCard } from "../history/HistoryCard";
import { t } from "../i18n/de";
import "./energie.css";

const USABLE: readonly string[] = [Quality.Valid, Quality.Stale];

export function Energie() {
  const energy = useEnergy();
  const { connection } = useAppState();
  const online = connection === "online";

  return (
    <div className="energie">
      <div className="energie__main">
        <BatteryCard energy={energy} online={online} />
        <FlowCard energy={energy} online={online} />
        <LynxBmsCard energy={energy} online={online} />
        <SolarDetailCard online={online} />

        <HistoryCard
          metrics={[
            { entityId: "energy.battery.soc" },
            { entityId: "energy.battery.voltage", decimals: 1 },
            { entityId: "energy.solar.power" },
            { entityId: "energy.consumption.power" },
          ]}
        />
      </div>

      <aside className="energie__side">
        <ShoreCard energy={energy} online={online} />
        <MultiPlusCard online={online} />
        <VictronAlarmCard online={online} />
        <NoteCard />
      </aside>
    </div>
  );
}

/* ── Batterie ────────────────────────────────────────────────────────────── */

function BatteryCard({ energy, online }: { energy: EnergySummary | null; online: boolean }) {
  const soc = pick(energy?.soc, online);
  const direction = online ? energy?.direction ?? null : null;

  return (
    <Card title={t("energy.battery")}>
      <div className="energie__hero">
        <span className={`energie__soc${soc.stale ? " energie__soc--stale" : ""}`}>
          {soc.usable ? (
            <>
              <span className="numeric">{Math.round(soc.value!)}</span>
              <span className="energie__unit">%</span>
            </>
          ) : (
            <span className="energie__soc--unknown">
              —<span className="energie__unit">%</span>
            </span>
          )}
        </span>

        <div className="energie__aside">
          <Status tone={directionTone(direction)} label={directionLabel(direction)} />
          {/* Der Ladezustand steht groß und ist damit die auffälligste Zahl
              der Seite. Sie darf nicht die einzige ohne Hinweis sein. */}
          {soc.usable && soc.marked && <StaleMark />}
          <Runtime energy={energy} online={online} />
        </div>
      </div>

      <div className="energie__split">
        <Row label={t("energy.voltage")}>
          <Number reading={energy?.voltage} online={online} unit="V" decimals={1} />
        </Row>
        <Row label={t("energy.current")}>
          <Number reading={energy?.current} online={online} unit="A" decimals={1} signed />
        </Row>
        <Row label={t("energy.batteryPower")}>
          <Number reading={energy?.battery_power} online={online} unit="W" signed />
        </Row>
        <Row label={t("energy.content")}>
          <Energy energy={energy} online={online} />
        </Row>
      </div>
    </Card>
  );
}

/**
 * Die Restlaufzeit.
 *
 * Eine Hochrechnung des augenblicklichen Verbrauchs — das steht auch dran.
 * Beim Laden und bei ruhender Batterie gibt es sie nicht: Dort liefe nichts
 * ab, und eine sehr große Zahl sähe aus wie eine Zusicherung.
 */
function Runtime({ energy, online }: { energy: EnergySummary | null; online: boolean }) {
  const hours = online ? energy?.runtime_h ?? null : null;
  if (hours === null) return null;

  const capped = energy?.runtime_capped ?? false;
  const text =
    hours < 1
      ? `${Math.round(hours * 60)} min`
      : `${hours.toFixed(hours < 10 ? 1 : 0)} h`;

  return (
    <span className="energie__runtime">
      <span className="numeric">{capped ? `> ${text}` : text}</span>
      <span className="energie__runtime-hint">{t("energy.atCurrentLoad")}</span>
    </span>
  );
}

/** Energieinhalt in Kilowattstunden — nur bei bekannter Kapazität. */
function Energy({ energy, online }: { energy: EnergySummary | null; online: boolean }) {
  const remaining = energy?.remaining_wh ?? null;
  const capacity = energy?.capacity_wh ?? null;

  if (remaining === null || capacity === null) {
    return <span className="energie__number energie__number--unknown">{t("state.unknown")}</span>;
  }

  return (
    <span className={`energie__number${online ? "" : " energie__number--stale"}`}>
      <span className="numeric">{(remaining / 1000).toFixed(1)}</span>
      <span className="energie__unit-inline">
        {`kWh ${t("energy.of")} ${(capacity / 1000).toFixed(1)}`}
      </span>
    </span>
  );
}

/**
 * Die Richtung als Ton.
 *
 * `null` ist bewusst „unbekannt" und nicht „ruht": Eine ruhende Batterie ist
 * eine Aussage, ein fehlender Messwert keine (Kapitel 18 §38).
 */
function directionTone(direction: Direction | null): Tone {
  if (direction === "charging") return "ok";
  if (direction === "discharging") return "accent";
  if (direction === "idle") return "neutral";
  return "unknown";
}

function directionLabel(direction: Direction | null): string {
  return direction ? t(`energy.dir.${direction}`) : t("state.unknown");
}

/* ── Energiefluss ────────────────────────────────────────────────────────── */

/**
 * Woher der Strom kommt und wohin er geht.
 *
 * Bewusst als Liste von Wegen und nicht als Schaubild mit Leitungen: Ein
 * Schaubild müsste behaupten, wie die Anlage verschaltet ist — und das ist
 * noch nicht bekannt (Punkt B2). Die Wege dagegen sind gemessen.
 */
function FlowCard({ energy, online }: { energy: EnergySummary | null; online: boolean }) {
  const shoreLive = online && energy?.shore_connected === true;

  return (
    <Card title={t("energy.flow")}>
      <div className="flow">
        <FlowRow
          icon={<IconSolar size={18} />}
          label={t("energy.solar")}
          reading={energy?.solar_power}
          online={online}
          tone="in"
        />
        <FlowRow
          icon={<IconPlug size={18} />}
          label={t("energy.shorePower")}
          reading={energy?.shore_power}
          online={online}
          tone="in"
          muted={!shoreLive}
        />
        <FlowRow
          label={t("energy.battery")}
          reading={energy?.battery_power}
          online={online}
          tone="battery"
          signed
        />
        <FlowRow
          label={t("energy.consumption")}
          reading={energy?.consumption}
          online={online}
          tone="out"
        />
      </div>
    </Card>
  );
}

function FlowRow({
  icon,
  label,
  reading,
  online,
  tone,
  signed = false,
  muted = false,
}: {
  icon?: JSX.Element;
  label: string;
  reading?: Reading;
  online: boolean;
  tone: "in" | "out" | "battery";
  signed?: boolean;
  muted?: boolean;
}) {
  const v = pick(reading, online);

  return (
    <div className={`flow__row${muted ? " flow__row--muted" : ""}`}>
      <span className="flow__label">
        {icon && <span className="flow__icon">{icon}</span>}
        {label}
      </span>
      <span className={`flow__bar flow__bar--${tone}`} aria-hidden="true" />
      <span className={`flow__value${v.stale ? " flow__value--stale" : ""}`}>
        {v.usable ? (
          <>
            <span className="numeric">{format(v.value!, 0, signed)}</span>
            <span className="flow__unit">W</span>
            {v.marked && <StaleMark />}
          </>
        ) : (
          <span className="flow__unknown">{t("state.unknown")}</span>
        )}
      </span>
    </div>
  );
}

/* ── Landstrom ───────────────────────────────────────────────────────────── */

function ShoreCard({ energy, online }: { energy: EnergySummary | null; online: boolean }) {
  const limit = useEntity("energy.shore.limit");
  const connected = online ? energy?.shore_connected ?? null : null;

  // Die Strombegrenzung ist einstellbar — aber nur, wenn eine Obergrenze
  // konfiguriert ist. Ohne die reale Absicherung des Anschlusses gibt es
  // keinen Befehl und damit auch kein Bedienelement (Kapitel 18 §136).
  const adjustable = (limit?.definition?.capabilities ?? []).some(
    (c) => c.verb === "set_value",
  );

  return (
    <Card title={t("energy.shorePower")}>
      <Row icon={<IconPlug size={18} />} label={t("energy.connection")}>
        <Status
          tone={connected === null ? "unknown" : connected ? "ok" : "neutral"}
          label={
            connected === null
              ? t("state.unknown")
              : connected
                ? t("energy.shoreConnected")
                : t("energy.shoreDisconnected")
          }
          compact
        />
      </Row>

      <Row label={t("energy.limit")}>
        {adjustable ? (
          <Stepper
            entityId="energy.shore.limit"
            value={typeof limit?.state.value === "number" ? limit.state.value : null}
            min={limit?.definition?.min_value ?? null}
            max={limit?.definition?.max_value ?? null}
            step={limit?.definition?.step ?? 1}
            unit="A"
            label={t("energy.limit")}
            stale={limit?.state.quality === Quality.Stale || !online}
            disabled={!online}
          />
        ) : (
          <Number reading={readingOf(limit)} online={online} unit="A" decimals={0} />
        )}
      </Row>

      {adjustable ? (
        /* Die Grenzen kommen aus der Konfiguration und werden hier
           eingesetzt. Stünden sie fest im Text, würde er bei einer
           geänderten Absicherung stillschweigend falsch. */
        <p className="energie__note">
          {t("energy.limitBounded", undefined, {
            min: String(limit?.definition?.min_value ?? "?"),
            max: String(limit?.definition?.max_value ?? "?"),
          })}
        </p>
      ) : (
        <p className="energie__note">{t("energy.limitNotAdjustable")}</p>
      )}
    </Card>
  );
}

/* ── MultiPlus ───────────────────────────────────────────────────────────── */

function MultiPlusCard({ online }: { online: boolean }) {
  const mode = useEntity("energy.inverter.state");
  const operation = useEntity("energy.inverter.operation");
  const { pending } = useAppState();

  const definition = mode?.definition;
  const states = definition?.states ?? [];
  const actual = stateString(mode, online);

  const canSet = (definition?.capabilities ?? []).some(
    (capability) => capability.verb === "set_state",
  );

  const spec = (definition?.capabilities ?? []).find(
    (capability) => capability.verb === "set_state",
  );

  const operationValue = stateString(operation, online);

  function choose(next: string) {
    if (!online || !canSet || next === actual) return;

    if (spec?.needs_confirmation) {
      const label = t(`energy.inverterMode.${next}`, next);
      const ok = window.confirm(
        t("energy.inverterModeConfirm", undefined, { mode: label }),
      );

      if (!ok) return;
    }

    sendCommand(
      "energy.inverter.state",
      "set_state",
      { state: next },
    );
  }

  return (
    <Card title={t("energy.multiPlus")}>
      <div className="energie__mode-list">
        {states.map((state) => (
          <button
            key={state}
            type="button"
            className={
              "energie__mode" +
              (actual === state ? " energie__mode--active" : "")
            }
            disabled={
              !online ||
              !canSet ||
              pending.has("energy.inverter.state")
            }
            aria-pressed={actual === state}
            onClick={() => choose(state)}
          >
            <span className="energie__mode-dot" aria-hidden="true" />
            <span>{t(`energy.inverterMode.${state}`, state)}</span>
          </button>
        ))}
      </div>

      <Row label={t("energy.operation")}>
        <Status
          tone={operationTone(operationValue)}
          label={
            operationValue
              ? t(
                  `energy.inverterOperation.${operationValue}`,
                  operationValue,
                )
              : t("state.unknown")
          }
          compact
        />
      </Row>
    </Card>
  );
}

function operationTone(value: string | null): Tone {
  if (value === null || value === "UNAVAILABLE") return "unknown";
  if (value === "FAULT") return "error";
  if (value === "INVERTING" || value === "ASSISTING") return "accent";
  if (
    value === "BULK" ||
    value === "ABSORPTION" ||
    value === "FLOAT" ||
    value === "STORAGE"
  ) {
    return "ok";
  }
  return "neutral";
}

/* ── Lynx Smart BMS ──────────────────────────────────────────────────────── */

function LynxBmsCard({
  energy,
  online,
}: {
  energy: EnergySummary | null;
  online: boolean;
}) {
  const temperature = useEntity("energy.battery.temperature");
  const consumedAh = useEntity("energy.battery.consumed_ah");
  const error = useEntity("energy.battery.error_code");

  const errorCode =
    online &&
    error &&
    USABLE.includes(error.state.quality) &&
    typeof error.state.value === "number"
      ? error.state.value
      : null;

  return (
    <Card title={t("energy.lynxBms")}>
      <div className="energie__split">
        <Row label={t("energy.battery_soc")}>
          <Number
            reading={energy?.soc}
            online={online}
            unit="%"
            decimals={0}
          />
        </Row>

        <Row label={t("energy.battery_voltage")}>
          <Number
            reading={energy?.voltage}
            online={online}
            unit="V"
            decimals={2}
          />
        </Row>

        <Row label={t("energy.battery_current")}>
          <Number
            reading={energy?.current}
            online={online}
            unit="A"
            decimals={1}
            signed
          />
        </Row>

        <Row label={t("energy.battery_power")}>
          <Number
            reading={energy?.battery_power}
            online={online}
            unit="W"
            decimals={0}
            signed
          />
        </Row>

        <Row label={t("energy.battery_temperature")}>
          <Number
            reading={readingOf(temperature)}
            online={online}
            unit="°C"
            decimals={1}
          />
        </Row>

        <Row label={t("energy.battery_consumed_ah")}>
          <Number
            reading={readingOf(consumedAh)}
            online={online}
            unit="Ah"
            decimals={1}
            signed
          />
        </Row>

        <Row label={t("energy.battery_error_code")}>
          <Status
            tone={
              errorCode === null
                ? "unknown"
                : errorCode === 0
                  ? "ok"
                  : "error"
            }
            label={
              errorCode === null
                ? t("state.unknown")
                : errorCode === 0
                  ? t("energy.noError")
                  : t("energy.errorCode", undefined, {
                      code: String(errorCode),
                    })
            }
            compact
          />
        </Row>
      </div>
    </Card>
  );
}

/* ── SmartSolar ──────────────────────────────────────────────────────────── */

function SolarDetailCard({ online }: { online: boolean }) {
  return (
    <Card title={t("energy.smartSolar")}>
      <div className="energie__mppt-head" aria-hidden="true">
        <span />
        <span>{t("energy.yieldToday")}</span>
        <span>{t("energy.pvVoltage")}</span>
        <span>{t("energy.pvCurrent")}</span>
        <span>{t("energy.power")}</span>
      </div>

      <MpptRow
        number={1}
        prefix="energy.solar.mppt1"
        online={online}
      />

      <MpptRow
        number={2}
        prefix="energy.solar.mppt2"
        online={online}
      />
    </Card>
  );
}

function MpptRow({
  number,
  prefix,
  online,
}: {
  number: number;
  prefix: string;
  online: boolean;
}) {
  const yieldToday = useEntity(`${prefix}.yield_today`);
  const voltage = useEntity(`${prefix}.pv_voltage`);
  const power = useEntity(`${prefix}.power`);

  const current = derivedPvCurrent(
    readingOf(power),
    readingOf(voltage),
  );

  return (
    <div className="energie__mppt-row">
      <div className="energie__mppt-name">
        <strong>
          {t("energy.mpptNumber", undefined, {
            number: String(number),
          })}
        </strong>
        <span>SmartSolar MPPT VE.Can 250/100 rev2</span>
      </div>

      <Number
        reading={readingOf(yieldToday)}
        online={online}
        unit="kWh"
        decimals={2}
      />

      <Number
        reading={readingOf(voltage)}
        online={online}
        unit="V"
        decimals={1}
      />

      <Number
        reading={current}
        online={online}
        unit="A"
        decimals={1}
      />

      <Number
        reading={readingOf(power)}
        online={online}
        unit="W"
        decimals={0}
      />
    </div>
  );
}

function derivedPvCurrent(
  power: Reading | undefined,
  voltage: Reading | undefined,
): Reading | undefined {
  if (
    !power ||
    !voltage ||
    typeof power.value !== "number" ||
    typeof voltage.value !== "number" ||
    voltage.value <= 0
  ) {
    return undefined;
  }

  const usablePower = USABLE.includes(power.quality);
  const usableVoltage = USABLE.includes(voltage.quality);

  if (!usablePower || !usableVoltage) return undefined;

  return {
    value: power.value / voltage.value,
    quality:
      power.quality === Quality.Stale ||
      voltage.quality === Quality.Stale
        ? Quality.Stale
        : Quality.Valid,
  };
}

/* ── Victron-Alarme ─────────────────────────────────────────────────────── */

function VictronAlarmCard({ online }: { online: boolean }) {
  const inverterOverload = useEntity(
    "energy.inverter.alarm.overload",
  );
  const inverterTemperature = useEntity(
    "energy.inverter.alarm.high_temperature",
  );
  const inverterLowBattery = useEntity(
    "energy.inverter.alarm.low_battery",
  );
  const inverterRipple = useEntity(
    "energy.inverter.alarm.ripple",
  );
  const inverterBms = useEntity(
    "energy.inverter.alarm.bms_connection",
  );

  const bmsCable = useEntity(
    "energy.battery.alarm.bms_cable",
  );
  const bmsContactor = useEntity(
    "energy.battery.alarm.contactor",
  );
  const bmsHighCurrent = useEntity(
    "energy.battery.alarm.high_current",
  );
  const bmsTemperature = useEntity(
    "energy.battery.alarm.high_temperature",
  );
  const bmsLowCell = useEntity(
    "energy.battery.alarm.low_cell_voltage",
  );
  const bmsLowSoc = useEntity(
    "energy.battery.alarm.low_soc",
  );

  const alarms = [
    inverterOverload,
    inverterTemperature,
    inverterLowBattery,
    inverterRipple,
    inverterBms,
    bmsCable,
    bmsContactor,
    bmsHighCurrent,
    bmsTemperature,
    bmsLowCell,
    bmsLowSoc,
  ];

  const active = alarms
    .map((entity) => ({
      entity,
      state: stateString(entity, online),
    }))
    .filter(
      (item) =>
        item.state === "WARNING" ||
        item.state === "ALARM",
    );

  const critical = active.some(
    (item) => item.state === "ALARM",
  );

  return (
    <Card
      title={t("energy.victronAlarms")}
      emphasis={active.length > 0}
    >
      {active.length === 0 ? (
        <Status
          tone={online ? "ok" : "unknown"}
          label={
            online
              ? t("energy.noActiveAlarms")
              : t("state.unknown")
          }
        />
      ) : (
        <div className="energie__alarm-list">
          {active.map(({ entity, state }) => {
            const name = entity?.definition?.name_key
              ? t(entity.definition.name_key)
              : entity?.entity_id ?? t("state.unknown");

            return (
              <Row
                key={entity?.entity_id ?? name}
                label={name}
              >
                <Status
                  tone={
                    state === "ALARM"
                      ? "error"
                      : "warn"
                  }
                  label={
                    state === "ALARM"
                      ? t("energy.alarm")
                      : t("energy.warning")
                  }
                  compact
                />
              </Row>
            );
          })}
        </div>
      )}

      {critical && (
        <p className="energie__note">
          {t("energy.activeAlarmHint")}
        </p>
      )}
    </Card>
  );
}

/* ── Hinweise ────────────────────────────────────────────────────────────── */

function NoteCard() {
  return (
    <Card title={t("energy.notesTitle")}>
      <ul className="energie__notes">
        <li>{t("energy.noRuntime")}</li>
        <li>{t("energy.readOnly")}</li>
      </ul>
    </Card>
  );
}

/* ── Bausteine ───────────────────────────────────────────────────────────── */

function Number({
  reading,
  online,
  unit,
  decimals = 0,
  signed = false,
}: {
  reading?: Reading;
  online: boolean;
  unit: string;
  decimals?: number;
  signed?: boolean;
}) {
  const v = pick(reading, online);

  if (!v.usable) {
    return <span className="energie__number energie__number--unknown">{t("state.unknown")}</span>;
  }

  return (
    <span className={`energie__number${v.stale ? " energie__number--stale" : ""}`}>
      <span className="numeric">{format(v.value!, decimals, signed)}</span>
      <span className="energie__unit-inline">{unit}</span>
      {v.marked && <StaleMark />}
    </span>
  );
}

/**
 * Prüft einen Messwert einmal für alle Darstellungen.
 *
 * Ohne Verbindung bleibt der zuletzt bekannte Wert stehen und wird als
 * veraltet gekennzeichnet — wie in der Komponente `Value`. Ihn zu leeren
 * ließe „Verbindung weg" genauso aussehen wie „nie einen Wert gehabt"; dass
 * die Werte nicht mehr aktuell sind, sagt das Banner über der Seite.
 */
function pick(reading: Reading | undefined, online: boolean) {
  const usable =
    Boolean(reading) && reading!.value !== null && USABLE.includes(reading!.quality);
  return {
    usable,
    value: reading?.value ?? null,
    /** Gedämpft darstellen. */
    stale: reading?.quality === Quality.Stale || !online,
    /** Zusätzlich beschriften — nur beim einzelnen verstummten Fühler. */
    marked: reading?.quality === Quality.Stale,
  };
}

/** Baut aus einer Entity dieselbe Form, die das Energie-Backend liefert. */
function readingOf(entity: ReturnType<typeof useEntity>): Reading | undefined {
  if (!entity) return undefined;
  const value = entity.state.value;
  return {
    value: typeof value === "number" ? value : null,
    quality: entity.state.quality,
  };
}

function stateString(
  entity: ReturnType<typeof useEntity>,
  online: boolean,
): string | null {
  if (!online || !entity) return null;

  if (!USABLE.includes(entity.state.quality)) {
    return null;
  }

  return typeof entity.state.value === "string"
    ? entity.state.value
    : null;
}

function format(value: number, decimals: number, signed: boolean): string {
  const text = value.toFixed(decimals);
  // Das Vorzeichen trägt hier die Aussage: + lädt, − entlädt. Ohne
  // ausgeschriebenes Plus wäre der Unterschied leicht zu übersehen.
  return signed && value > 0 ? `+${text}` : text;
}
