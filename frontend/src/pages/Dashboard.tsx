/**
 * Das Dashboard.
 *
 * Es beantwortet die fünf Fragen aus Kapitel 7 §2 auf einen Blick: Wo bin
 * ich, was passiert gerade, ist alles in Ordnung, was braucht meine
 * Aufmerksamkeit, was kann ich jetzt tun.
 *
 * Es zeigt bewusst **nicht** alles Verfügbare. Detailtiefe gehört auf die
 * Fachseiten (Kapitel 8 §1).
 */

import { useEffect, useState } from "react";
import { Bar, Card, QuickTile, Row, Status, Value, type Tone } from "../design/primitives";
import {
  IconAwning,
  IconDoor,
  IconGarage,
  IconLight,
  IconPlug,
  IconPump,
  IconSolar,
  IconStep,
  IconWarning,
} from "../design/icons";
import { VehicleView, type Part } from "../vehicle/VehicleView";
import { isOn, isUnknown, textOf, useAppState, useEntity } from "../realtime/hooks";
import type { EntityView } from "../realtime/types";
import { sendCommand } from "../api/client";
import { t } from "../i18n/de";
import "./dashboard.css";

interface AlertItem {
  id: string;
  entity_id: string | null;
  severity: "INFO" | "NOTICE" | "WARNING" | "CRITICAL";
  message_key: string;
  params: Record<string, string>;
}

export function Dashboard() {
  const alerts = useAlerts();
  const critical = alerts.filter((a) => a.severity === "WARNING" || a.severity === "CRITICAL");

  return (
    <div className="dash">
      <section className="dash__hero">
        <div className="dash__vehicle">
          <VehicleView state={useVehicleState()} />
        </div>
        <VehicleStatusCard />
      </section>

      <aside className="dash__side">
        <AlertsCard alerts={alerts} />
        <QuickAccessCard />
      </aside>

      {/* Der Energiebereich wird hervorgehoben, wenn er Aufmerksamkeit
          braucht — ohne dass sich das Layout verschiebt (Kapitel 8 §10/§11). */}
      <div className="dash__cards">
        <EnergyCard emphasis={critical.some((a) => a.entity_id?.startsWith("energy."))} />
        <WaterCard emphasis={critical.some((a) => a.entity_id?.startsWith("water."))} />
        <ClimateCard />
      </div>
    </div>
  );
}

/* ── Fahrzeug ────────────────────────────────────────────────────────── */

function useVehicleState() {
  const garage = useEntity("vehicle.garage.door");
  const door = useEntity("vehicle.door.main");
  const step = useEntity("vehicle.step.entry");
  const awning = useEntity("vehicle.awning.main");
  const { connection } = useAppState();

  // Ohne Verbindung darf die Zeichnung keine Stellung mehr zeigen. Ein
  // angehobenes Garagentor wäre sonst eine Aussage über das Fahrzeug, die das
  // System gar nicht mehr belegen kann (Kapitel 18 §37/§106).
  const live = connection === "online";

  return {
    garage: toPart(garage, live),
    door: toPart(door, live),
    step: toPart(step, live),
    awning: toPart(awning, live),
  };
}

/** Übersetzt einen Hardwarezustand in eine Darstellung — ohne zu raten. */
function toPart(entity: EntityView | undefined, live: boolean): Part {
  // Ohne Hardwarezuordnung wird das Teil gar nicht gezeichnet. Ein
  // gestrichelter Umriss hieße „vorhanden, Lage unbekannt“ — das wäre hier
  // falsch (Kapitel 18 §101).
  if (!entity || entity.definition?.configured === false) return "absent";

  const value = textOf(entity);
  if (!live || isUnknown(entity) || !value) return "unknown";
  if (value === "OPENING" || value === "CLOSING") return "moving";
  if (value === "OPEN") return "open";
  if (value === "CLOSED" || value === "STOPPED") return "closed";
  if (value === "BLOCKED") return "unknown";
  return "unknown";
}

function VehicleStatusCard() {
  const rows: { id: string; icon: JSX.Element; label: string }[] = [
    { id: "vehicle.door.main", icon: <IconDoor size={18} />, label: t("vehicle.door_main") },
    { id: "vehicle.garage.door", icon: <IconGarage size={18} />, label: t("vehicle.garage_door") },
    { id: "vehicle.step.entry", icon: <IconStep size={18} />, label: t("vehicle.step") },
    { id: "vehicle.awning.main", icon: <IconAwning size={18} />, label: t("vehicle.awning") },
  ];

  return (
    <div className="dash__status">
      <Card title={t("dash.vehicleStatus")}>
        {rows.map((row) => (
          <StatusRow key={row.id} entityId={row.id} icon={row.icon} label={row.label} />
        ))}
      </Card>
    </div>
  );
}

function StatusRow({
  entityId,
  icon,
  label,
}: {
  entityId: string;
  icon: JSX.Element;
  label: string;
}) {
  const entity = useEntity(entityId);
  const { connection } = useAppState();

  // Ohne Verbindung ist der Zustand nicht mehr belastbar — dann wird er als
  // unbekannt geführt statt weiter behauptet.
  const { tone, text } =
    connection !== "online"
      ? { tone: "unknown" as Tone, text: t("state.unknown") }
      : describe(
          entity && textOf(entity),
          isUnknown(entity),
          entity?.definition?.configured,
        );

  return (
    <Row icon={icon} label={label}>
      <Status tone={tone} label={text} compact />
    </Row>
  );
}

/** Ein Hardwarezustand wird zu Ton und Text — an einer Stelle, für alle. */
function describe(
  value: string | null | undefined,
  unknown: boolean,
  configured: boolean | undefined,
): { tone: Tone; text: string } {
  if (configured === false) return { tone: "unknown", text: t("state.notConfigured") };
  if (unknown || !value) return { tone: "unknown", text: t("state.unknown") };

  switch (value) {
    case "CLOSED": return { tone: "ok", text: t("state.closed") };
    case "OPEN": return { tone: "warn", text: t("state.open") };
    case "OPENING": return { tone: "accent", text: t("state.opening") };
    case "CLOSING": return { tone: "accent", text: t("state.closing") };
    case "STOPPED": return { tone: "warn", text: t("state.stopped") };
    case "BLOCKED": return { tone: "error", text: t("state.blocked") };
    case "ON": return { tone: "ok", text: t("state.on") };
    case "OFF": return { tone: "neutral", text: t("state.off") };
    default: return { tone: "neutral", text: value };
  }
}

/* ── Warnungen ───────────────────────────────────────────────────────── */

function useAlerts(): AlertItem[] {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const { entities } = useAppState();

  useEffect(() => {
    let active = true;
    fetch("/api/v1/alerts")
      .then((r) => (r.ok ? r.json() : []))
      .then((data: AlertItem[]) => active && setAlerts(data))
      .catch(() => active && setAlerts([]));
    return () => {
      active = false;
    };
    // Bei jeder Zustandsänderung neu bewerten — die Bewertung selbst
    // geschieht im Backend.
  }, [entities]);

  return alerts;
}

function AlertsCard({ alerts }: { alerts: AlertItem[] }) {
  const relevant = alerts.filter((a) => a.severity !== "INFO");
  const { connection } = useAppState();

  // „Keine Warnungen“ ist eine Entwarnung. Sie darf nur ausgesprochen werden,
  // solange das System den Zustand wirklich kennt — sonst beruhigt die
  // Oberfläche, obwohl sie nichts weiß (Kapitel 18 §37).
  if (connection !== "online") {
    return (
      <Card title={t("dash.warnings")} icon={<IconWarning size={18} />}>
        <Status tone="unknown" label={t("dash.warningsUnknown")} />
      </Card>
    );
  }

  return (
    <Card
      title={t("dash.warnings")}
      icon={<IconWarning size={18} />}
      action={
        relevant.length > 0 ? <span className="dash__badge">{relevant.length}</span> : null
      }
      emphasis={relevant.some((a) => a.severity === "CRITICAL")}
    >
      {relevant.length === 0 ? (
        <Status tone="ok" label={t("dash.noWarnings")} />
      ) : (
        <ul className="alerts">
          {relevant.slice(0, 4).map((alert) => (
            <li key={alert.id} className={`alert alert--${alert.severity.toLowerCase()}`}>
              <span className="alert__title">
                {t(alert.params.name_key ?? "", alert.entity_id ?? "")}
              </span>
              <span className="alert__text">{t(alert.message_key)}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

/* ── Schnellzugriff ──────────────────────────────────────────────────── */

function QuickAccessCard() {
  return (
    <Card title={t("dash.quickAccess")}>
      <div className="quickgrid">
        <SwitchTile entityId="light.exterior.entry" icon={<IconLight />} label={t("light.entry")} />
        <SwitchTile entityId="light.interior.living" icon={<IconLight />} label={t("light.living")} />
        <SwitchTile entityId="water.pump.main" icon={<IconPump />} label={t("water.pump")} />
        <MoveTile entityId="vehicle.garage.door" icon={<IconGarage />} label={t("vehicle.garage_door")} />
        <MoveTile entityId="vehicle.step.entry" icon={<IconStep />} label={t("vehicle.step")} />
        <MoveTile entityId="vehicle.awning.main" icon={<IconAwning />} label={t("vehicle.awning")} />
      </div>
    </Card>
  );
}

function SwitchTile({
  entityId,
  icon,
  label,
}: {
  entityId: string;
  icon: JSX.Element;
  label: string;
}) {
  const entity = useEntity(entityId);
  const { pending, connection } = useAppState();
  const on = isOn(entity);
  const configured = entity?.definition?.configured ?? false;

  return (
    <QuickTile
      icon={icon}
      label={label}
      active={on && connection === "online"}
      pending={pending.has(entityId)}
      // Ohne Verbindung erreicht kein Befehl das Fahrzeug. Ein bedienbarer
      // Schalter würde Handlungsfähigkeit vortäuschen (Kapitel 8 §12).
      disabled={!configured || connection !== "online"}
      onClick={() => sendCommand(entityId, "set_state", { state: on ? "OFF" : "ON" })}
    />
  );
}

function MoveTile({
  entityId,
  icon,
  label,
}: {
  entityId: string;
  icon: JSX.Element;
  label: string;
}) {
  const entity = useEntity(entityId);
  const { pending, connection } = useAppState();
  const online = connection === "online";
  const value = entity && textOf(entity);
  const open = value === "OPEN";
  const moving = value === "OPENING" || value === "CLOSING";
  const configured = entity?.definition?.configured ?? false;

  return (
    <QuickTile
      icon={icon}
      label={label}
      active={open && online}
      pending={pending.has(entityId) || (moving && online)}
      // Siehe SwitchTile: ohne Verbindung gibt es nichts zu bedienen.
      disabled={!configured || !online}
      onClick={() => sendCommand(entityId, open ? "close" : "open")}
    />
  );
}

/* ── Bereichskarten ──────────────────────────────────────────────────── */

function EnergyCard({ emphasis }: { emphasis: boolean }) {
  const soc = useEntity("energy.battery.soc");
  const voltage = useEntity("energy.battery.voltage");
  const solar = useEntity("energy.solar.power");

  return (
    <Card title={t("dash.energy")} icon={<IconPlug size={18} />} emphasis={emphasis}>
      <div className="metric">
        <Value entity={soc} size="metric" />
        <span className="metric__caption">{t("energy.battery")}</span>
      </div>
      <Bar entity={soc} tone={socTone(soc?.state.value)} />

      <div className="dash__split">
        <Row icon={<IconSolar size={16} />} label={t("energy.solar")}>
          <Value entity={solar} size="inline" />
        </Row>
        <Row label={t("energy.voltage")}>
          <Value entity={voltage} size="inline" decimals={1} />
        </Row>
      </div>
    </Card>
  );
}

function socTone(value: unknown): Tone {
  if (typeof value !== "number") return "unknown";
  if (value < 20) return "error";
  if (value < 40) return "warn";
  return "ok";
}

function WaterCard({ emphasis }: { emphasis: boolean }) {
  // Alle Tanks werden neutral dargestellt. Orange oder Rot würde eine
  // Bewertung behaupten, die das System nicht treffen kann: Die Schwellen
  // sind noch nicht konfiguriert (offener Punkt C3). Farbe ohne Bedeutung
  // wäre Dekoration und widerspricht Kapitel 7 §5.
  const tanks = [
    { id: "water.tank.fresh", label: t("tank.fresh") },
    { id: "water.tank.grey", label: t("tank.grey") },
    { id: "water.tank.black", label: t("tank.black") },
  ];

  return (
    <Card title={t("dash.water")} emphasis={emphasis}>
      <div className="tanks">
        {tanks.map((tank) => (
          <TankRow key={tank.id} id={tank.id} label={tank.label} />
        ))}
      </div>
    </Card>
  );
}

function TankRow({ id, label }: { id: string; label: string }) {
  const entity = useEntity(id);

  return (
    <div className="tank">
      <div className="tank__head">
        <span className="tank__label">{label}</span>
        <Value entity={entity} size="inline" />
      </div>
      <Bar entity={entity} tone="accent" />
      {/* Liter werden erst gezeigt, wenn eine Kapazität konfiguriert ist.
          Sie wird nicht geraten (Kapitel 18 §98, offener Punkt C2). */}
    </div>
  );
}

function ClimateCard() {
  const inside = useEntity("climate.living.temperature");
  const outside = useEntity("climate.outside.temperature");
  const target = useEntity("climate.living.target");

  return (
    <Card title={t("dash.climate")}>
      <div className="metric">
        <Value entity={inside} size="metric" decimals={1} />
        <span className="metric__caption">{t("climate.inside")}</span>
      </div>

      <div className="dash__split">
        <Row label={t("climate.outside")}>
          <Value entity={outside} size="inline" decimals={1} />
        </Row>
        <Row label={t("climate.target")}>
          <Value entity={target} size="inline" decimals={1} />
        </Row>
      </div>
    </Card>
  );
}
