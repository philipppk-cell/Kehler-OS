/**
 * Heizung — aktuell ausschließlich die angebundene Fußbodenheizung.
 *
 * Die SCHEER/HeatMate-Anlage bleibt im Backend beschrieben, wird auf dieser
 * Seite aber erst wieder dargestellt, wenn ihre Modbus-Anbindung tatsächlich
 * verfügbar und geprüft ist.
 *
 * Das Smart-Life-Thermostat bleibt selbst Regler. Kehler OS liest den echten
 * Zustand und setzt ausschließlich die am realen Thermostat bestätigten Werte.
 */

import { Card, Row, StaleMark, Status, Toggle, type Tone } from "../design/primitives";
import { Stepper } from "../design/stepper";
import { IconHeating } from "../design/icons";
import { useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { Quality, type EntityView } from "../realtime/types";
import { t } from "../i18n/de";
import "./heizung.css";

const USABLE: readonly string[] = [
  Quality.Valid,
  Quality.Stale,
];

export function Heizung() {
  return (
    <div className="heizung">
      <FloorThermostatCard />
    </div>
  );
}

/* ── Fußbodenheizung ───────────────────────────────────────────────────── */

function FloorThermostatCard() {
  return (
    <Card
      title={t("heating.floorThermostatTitle")}
      icon={<IconHeating size={18} />}
    >
      <div className="heizung__hero">
        <TemperatureBlock
          entityId="heating.floor.temperature.actual"
        />

        <TargetBlock
          entityId="heating.floor.temperature.target"
        />
      </div>

      <FloorDemand />

      <div className="heizung__controls">
        <SwitchRow entityId="heating.floor.state" />
        <FloorModeRow />
        <SwitchRow entityId="heating.floor.eco" />
        <SwitchRow entityId="heating.floor.child_lock" />
      </div>

      <p className="heizung__note">
        {t("heating.floorOnlyHint")}
      </p>
    </Card>
  );
}

/* ── Temperaturen ──────────────────────────────────────────────────────── */

function TemperatureBlock({
  entityId,
}: {
  entityId: string;
}) {
  const entity = useEntity(entityId);
  const { connection } = useAppState();

  const name = nameOf(entity, entityId);
  const value =
    typeof entity?.state.value === "number"
      ? entity.state.value
      : null;

  const quality = entity?.state.quality;

  const usable =
    value !== null &&
    quality !== undefined &&
    USABLE.includes(quality);

  const stale =
    quality === Quality.Stale ||
    connection !== "online";

  return (
    <div className="heizung__block">
      {usable ? (
        <span
          className={
            "heizung__temperature" +
            (stale
              ? " heizung__temperature--stale"
              : "")
          }
        >
          <span className="numeric">
            {value.toFixed(1)}
          </span>
          <span className="heizung__unit">
            °C
          </span>
        </span>
      ) : (
        <span className="heizung__temperature heizung__temperature--unknown">
          {t("state.unknown")}
        </span>
      )}

      <span className="heizung__label">
        {name}
        {quality === Quality.Stale && (
          <StaleMark />
        )}
      </span>
    </div>
  );
}

function TargetBlock({
  entityId,
}: {
  entityId: string;
}) {
  const entity = useEntity(entityId);
  const { connection } = useAppState();

  const definition = entity?.definition;
  const name = nameOf(entity, entityId);

  const quality = entity?.state.quality;

  const value =
    typeof entity?.state.value === "number" &&
    quality !== undefined &&
    USABLE.includes(quality)
      ? entity.state.value
      : null;

  const step = definition?.step ?? 0.5;

  return (
    <div className="heizung__block heizung__block--target">
      <Stepper
        entityId={entityId}
        value={value}
        min={definition?.min_value ?? null}
        max={definition?.max_value ?? null}
        step={step}
        unit="°C"
        decimals={step < 1 ? 1 : 0}
        label={name}
        stale={
          quality === Quality.Stale ||
          connection !== "online"
        }
        disabled={
          connection !== "online"
        }
      />

      <span className="heizung__label">
        {name}
      </span>
    </div>
  );
}

/* ── Heizanforderung ───────────────────────────────────────────────────── */

function FloorDemand() {
  const entity = useEntity(
    "heating.floor.demand",
  );

  const { connection } = useAppState();

  const quality = entity?.state.quality;
  const value = entity?.state.value;

  const usable =
    connection === "online" &&
    value !== null &&
    value !== undefined &&
    quality !== undefined &&
    USABLE.includes(quality);

  let tone: Tone = "unknown";
  let label = t("state.unknown");

  if (usable && value === "HEATING") {
    tone = "accent";
    label = t(
      "heating.floorDemand.HEATING",
    );
  } else if (
    usable &&
    value === "IDLE"
  ) {
    tone = "neutral";
    label = t(
      "heating.floorDemand.IDLE",
    );
  }

  return (
    <div className="heizung__demand">
      <span className="heizung__demand-label">
        {t("heating.floor_demand")}
      </span>

      <Status
        tone={tone}
        label={label}
      />
    </div>
  );
}

/* ── Ein/Aus, Eco, Kindersicherung ─────────────────────────────────────── */

function SwitchRow({
  entityId,
}: {
  entityId: string;
}) {
  const entity = useEntity(entityId);
  const { connection, pending } =
    useAppState();

  const definition = entity?.definition;
  const name = nameOf(entity, entityId);

  const quality = entity?.state.quality;

  const usable =
    entity?.state.value !== null &&
    quality !== undefined &&
    USABLE.includes(quality);

  const on =
    usable &&
    entity?.state.value === "ON";

  const canSet = (
    definition?.capabilities ?? []
  ).some(
    (capability) =>
      capability.verb === "set_state",
  );

  return (
    <Row label={name}>
      <Toggle
        on={on}
        unknown={
          !usable ||
          connection !== "online"
        }
        pending={pending.has(entityId)}
        disabled={
          connection !== "online" ||
          !canSet
        }
        label={name}
        onChange={(next) =>
          sendCommand(
            entityId,
            "set_state",
            {
              state: next
                ? "ON"
                : "OFF",
            },
          )
        }
      />
    </Row>
  );
}

/* ── Automatik / Manuell ───────────────────────────────────────────────── */

function FloorModeRow() {
  const entityId = "heating.floor.mode";

  const entity = useEntity(entityId);
  const { connection, pending } =
    useAppState();

  const definition = entity?.definition;
  const states = definition?.states ?? [];

  const quality = entity?.state.quality;

  const current =
    quality !== undefined &&
    USABLE.includes(quality) &&
    typeof entity?.state.value === "string"
      ? entity.state.value
      : null;

  const canSet = (
    definition?.capabilities ?? []
  ).some(
    (capability) =>
      capability.verb === "set_state",
  );

  const disabled =
    connection !== "online" ||
    !canSet ||
    pending.has(entityId);

  const name = nameOf(entity, entityId);

  return (
    <Row label={name}>
      <div
        className="heizung__mode"
        role="group"
        aria-label={name}
      >
        {states.map((state) => (
          <button
            key={state}
            type="button"
            className={
              "heizung__mode-option" +
              (current === state
                ? " heizung__mode-option--active"
                : "")
            }
            aria-pressed={
              current === state
            }
            disabled={disabled}
            onClick={() =>
              sendCommand(
                entityId,
                "set_state",
                { state },
              )
            }
          >
            {t(
              `heating.floorMode.${state}`,
              state,
            )}
          </button>
        ))}
      </div>
    </Row>
  );
}

/* ── Hilfsfunktionen ───────────────────────────────────────────────────── */

function nameOf(
  entity: EntityView | undefined,
  fallback: string,
): string {
  const key =
    entity?.definition?.name_key;

  return key
    ? t(key, fallback)
    : fallback;
}
