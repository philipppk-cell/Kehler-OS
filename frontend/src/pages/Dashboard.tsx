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
  IconPlug,
  IconSolar,
  IconStep,
  IconWarning,
} from "../design/icons";
import { VehicleDisplay } from "../vehicle3d/VehicleDisplay";
import { useVehicleState } from "../vehicle3d/useVehicleState";
import { isUnknown, textOf, useAppState, useEntity } from "../realtime/hooks";
import { Quality } from "../realtime/types";
import { useWater, type Level, type TankView as WaterTank } from "../water/useWater";
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
          <VehicleDisplay state={useVehicleState()} />
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
        <TemperatureCard />
      </div>
    </div>
  );
}

/* ── Fahrzeug ────────────────────────────────────────────────────────── */

function VehicleStatusCard() {
  const rows: { id: string; icon: JSX.Element; label: string }[] = [
    { id: "vehicle.door.main", icon: <IconDoor size={18} />, label: t("vehicle.door_main") },
    { id: "vehicle.garage.door", icon: <IconGarage size={18} />, label: t("vehicle.garage_door") },
    { id: "vehicle.terrace.main", icon: <IconStep size={18} />, label: t("vehicle.terrace") },
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
              <span className="alert__text">
                {t(alert.message_key, undefined, alert.params)}
              </span>
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
        <MoveTile entityId="vehicle.garage.door" icon={<IconGarage />} label={t("vehicle.garage_door")} />
      </div>
    </Card>
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

/**
 * Die Wasserkarte im Dashboard.
 *
 * Sie zeigt die **Gesamtmenge Frischwasser** über beide Tanks — das ist die
 * Alltagsfrage. Die Einzeltanks stehen auf der Wasserseite (Kapitel 8 §1).
 *
 * Alle Balken sind neutral eingefärbt. Orange oder Rot würde eine Bewertung
 * behaupten, die das System nicht treffen kann: Die Schwellen sind noch nicht
 * konfiguriert (offener Punkt C3). Farbe ohne Bedeutung wäre Dekoration und
 * widerspricht Kapitel 7 §5.
 */
function WaterCard({ emphasis }: { emphasis: boolean }) {
  const water = useWater();
  const { connection } = useAppState();
  const online = connection === "online";
  const fresh = water?.fresh;
  const total = online && fresh?.litres !== null && fresh !== undefined;

  return (
    <Card title={t("dash.water")} emphasis={emphasis}>
      <div className="metric">
        {total ? (
          <span className="value value--metric">
            <span className="numeric">{Math.round(fresh.litres!)}</span>
            <span className="value__unit">L</span>
          </span>
        ) : (
          <span className="value value--metric value--unknown">
            —<span className="value__hint">{t("state.unknown")}</span>
          </span>
        )}
        <span className="metric__caption">{t("water.freshTotal")}</span>
      </div>

      <div className="tanks">
        {(water?.waste ?? []).map((tank) => (
          <WasteRow key={tank.entity_id} tank={tank} online={online} />
        ))}
      </div>
    </Card>
  );
}

/** Stufe → Balkenfarbe, gleich wie auf der Wasserseite. */
const FILL: Record<Level, string> = { ok: "accent", warn: "warn", critical: "error" };

function WasteRow({ tank, online }: { tank: WaterTank; online: boolean }) {
  const usable =
    online && tank.percent !== null &&
    (tank.quality === Quality.Valid || tank.quality === Quality.Stale);
  const percent = usable ? Math.max(0, Math.min(100, tank.percent!)) : 0;

  return (
    <div className="tank">
      <div className="tank__head">
        <span className="tank__label">{t(tank.name_key, tank.entity_id)}</span>
        <span className="value value--inline">
          {usable ? (
            <>
              <span className="numeric">{Math.round(tank.percent!)}</span>
              <span className="value__unit">%</span>
            </>
          ) : (
            <span className="value--unknown">—</span>
          )}
        </span>
      </div>
      <div className={`bar${usable ? "" : " bar--unknown"}`}>
        {/* Farbe nur bei überschrittener Schwelle — bewertet vom Backend,
            damit Dashboard und Wasserseite nicht auseinanderlaufen. */}
        <div
          className={`bar__fill bar__fill--${usable ? FILL[tank.level] : "accent"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

/**
 * Temperatur auf dem Dashboard.
 *
 * Die Karte heißt nicht mehr „Klima": Klima und Heizung sind getrennte
 * Systeme (BESTÄTIGT 2026-08-10) und haben je einen eigenen Sollwert. Ein
 * gemeinsames „Soll" gibt es damit nicht mehr — es würde einen der beiden
 * Werte verschweigen.
 *
 * Bedient wird hier nichts. Wer verstellen will, geht auf die Fachseite
 * (Kapitel 8 §13).
 */
function TemperatureCard() {
  const inside = useEntity("climate.living.temperature");
  const outside = useEntity("climate.outside.temperature");
  const cooling = useEntity("climate.cooling.target");
  const heating = useEntity("heating.temperature.target");

  return (
    <Card title={t("dash.temperature")}>
      <div className="metric">
        <Value entity={inside} size="metric" decimals={1} />
        <span className="metric__caption">{t("climate.inside")}</span>
      </div>

      <div className="dash__split">
        <Row label={t("climate.outside")}>
          <Value entity={outside} size="inline" decimals={1} />
        </Row>
        <Row label={t("dash.coolingTarget")}>
          <Value entity={cooling} size="inline" decimals={1} />
        </Row>
        <Row label={t("dash.heatingTarget")}>
          <Value entity={heating} size="inline" decimals={1} />
        </Row>
      </div>
    </Card>
  );
}
