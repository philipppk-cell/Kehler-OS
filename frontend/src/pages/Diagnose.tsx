/**
 * Diagnose — die Seite, auf der Kehler OS über sich selbst Auskunft gibt.
 *
 * Sie hat zwei Anlässe, und beide gehören derselben Person: Etwas wird
 * angeschlossen und soll ankommen, oder etwas stimmt nicht und man will
 * wissen, was genau.
 *
 * ── Warum diese Seite anders aussehen darf ────────────────────────────────
 *
 * Überall sonst zeigt Kehler OS übersetzte Namen und verständliche Sätze; der
 * technische Rohtext bleibt der Diagnose vorbehalten (Kapitel 7 §43). Hier
 * ist er der Inhalt: Entity-Kennungen, Qualitätsstufen, Quellen,
 * Fehlermeldungen im Wortlaut des Servers. Wer diese Seite öffnet, sucht
 * nicht nach Beruhigung.
 *
 * ── Drei Arten von Abwesenheit ────────────────────────────────────────────
 *
 * Die Tabelle hält sie auseinander, weil sie verschiedene Dinge bedeuten und
 * verschiedene nächste Schritte auslösen:
 *
 * * **Nicht konfiguriert** — die Funktion existiert, ihr fehlt die
 *   Hardwarezuordnung. Eine offene Aufgabe, keine Störung.
 * * **Noch zu verifizieren** — ob sich die Funktion über die Schnittstelle
 *   überhaupt lesen lässt, weiß niemand. Eine offene Frage.
 * * **Auffällig** — zugeordnet, angebunden, aber die Verbindung oder der Wert
 *   taugt gerade nichts. Das ist die einzige der drei, die eine Störung ist.
 *
 * Der Filter „Auffällig" schließt die ersten beiden deshalb ausdrücklich aus.
 * Stünden sie darin, bestünde die Liste dauerhaft aus offenen Punkten und
 * wäre für den einen Fall unbrauchbar, für den es sie gibt.
 */

import { useMemo, useState } from "react";
import { Button, Card, Segmented, Status, type Tone } from "../design/primitives";
import { useAppState } from "../realtime/hooks";
import { Link, Quality, type EntityView } from "../realtime/types";
import {
  useDiagnostics,
  type AlertItem,
  type ServiceStatus,
  type SimulationTools,
} from "../diagnostics/useDiagnostics";
import { injectFault, setLevel } from "../diagnostics/actions";
import { t } from "../i18n/de";
import "./diagnose.css";

type Scope = "all" | "issues" | "open";

export function Diagnose() {
  const { system, entities, connection } = useAppState();
  const diagnostics = useDiagnostics();

  const [query, setQuery] = useState("");
  const [scope, setScope] = useState<Scope>("all");
  const [selected, setSelected] = useState<string | null>(null);

  const all = useMemo(() => [...entities.values()], [entities]);
  const newest = useMemo(() => newestTimestamp(all), [all]);
  const rows = useMemo(() => filter(all, query, scope), [all, query, scope]);

  // Die Zähler benutzen dieselben Prädikate wie der Filter. Getrennt gerechnet
  // liefen sie sofort auseinander: „Nicht konfiguriert" und „noch zu
  // verifizieren" gelten bei der Heizung **gleichzeitig**, addiert ergaben sie
  // 49 offene Punkte bei 45 Entities.
  const counts = useMemo(
    () => ({
      total: all.length,
      issues: all.filter(isIssue).length,
      // Getrennt ausgewiesen, aber niemals addiert: Bei der Heizung gilt
      // beides gleichzeitig. `open` ist deshalb die Vereinigungsmenge und
      // kommt aus demselben Prädikat wie der Filter.
      open: all.filter(isOpen).length,
      unconfigured: all.filter((e) => e.definition?.configured === false).length,
      unverified: all.filter((e) => e.definition?.unverified).length,
    }),
    [all],
  );

  return (
    <div className="diag">
      <Card title={t("diag.system")}>
        <dl className="facts">
          <Fact label={t("diag.version")} value={system?.version ?? "—"} />
          <Fact
            label={t("diag.environment")}
            value={system ? t(`env.${system.environment}`, system.environment) : "—"}
            tone={system?.simulated ? "warn" : undefined}
          />
          <Fact
            label={t("diag.health")}
            value={system ? t(`health.${system.health}`) : "—"}
          />
          <Fact label={t("diag.entities")} value={String(counts.total)} />
          <Fact
            label={t("diag.unconfigured")}
            value={String(counts.unconfigured)}
            tone={counts.unconfigured > 0 ? "warn" : undefined}
          />
          <Fact
            label={t("diag.unverified")}
            value={String(counts.unverified)}
            tone={counts.unverified > 0 ? "warn" : undefined}
          />
          <Fact
            label={t("diag.stateVersion")}
            value={system ? String(system.state_version) : "—"}
          />
        </dl>
      </Card>

      <div className="diag__pair">
        <ServicesCard services={diagnostics.services} />
        <AdaptersCard adapters={diagnostics.adapters} />
      </div>

      {/* Die Entity-Tabelle steht über den Meldungen, nicht darunter. Sie ist
          die Arbeitsfläche dieser Seite, und die Meldungsliste enthält im
          Auslieferungszustand über zwanzig Hinweise auf noch nicht zugeordnete
          Hardware — stünde sie davor, begänne jede Diagnose damit, an
          bekannten offenen Punkten vorbeizuscrollen. Was tatsächlich stört,
          steht ohnehin doppelt: hier als Filter „Auffällig" mit seiner Zahl. */}
      <Card
        title={t("diag.entityList")}
        action={<span className="diag__count">{rows.length} / {counts.total}</span>}
      >
        <div className="diag__filter">
          <input
            type="search"
            className="input"
            placeholder={t("diag.searchHint")}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            aria-label={t("diag.searchHint")}
          />
          <Segmented
            label={t("diag.scope")}
            value={scope}
            onChange={setScope}
            options={[
              { value: "all", label: t("diag.scopeAll") },
              { value: "issues", label: `${t("diag.scopeIssues")} (${counts.issues})` },
              { value: "open", label: `${t("diag.scopeOpen")} (${counts.open})` },
            ]}
          />
        </div>

        <div className="dtable" role="table">
          {/* Die Überschriften tragen dieselben Klassen wie ihre Spalten. Ohne
              das blieben sie im Hochformat stehen, während die Spalten darunter
              verschwinden — und die Kopfzeile beschriftete dann die falschen
              Werte. */}
          <div className="dtable__head" role="row">
            <span role="columnheader">{t("diag.colName")}</span>
            <span role="columnheader" className="dtable__id">{t("diag.colId")}</span>
            <span role="columnheader">{t("diag.colLink")}</span>
            <span role="columnheader">{t("diag.colQuality")}</span>
            <span role="columnheader" className="dtable__num">{t("diag.colValue")}</span>
            <span role="columnheader" className="dtable__source">{t("diag.colSource")}</span>
            <span role="columnheader" className="dtable__num">{t("diag.colLag")}</span>
          </div>

          <div className="dtable__body">
            {rows.length === 0 ? (
              <p className="diag__empty">{t("diag.noMatch")}</p>
            ) : (
              rows.map((entity) => (
                <EntityRow
                  key={entity.entity_id}
                  entity={entity}
                  newest={newest}
                  selected={selected === entity.entity_id}
                  onSelect={setSelected}
                />
              ))
            )}
          </div>
        </div>

        {/* Der Rückstand ist eine ungewöhnliche Größe und wird deshalb
            erklärt, statt kommentarlos in einer Spalte zu stehen. */}
        <p className="diag__note">{t("diag.lagNote")}</p>
      </Card>

      <AlertsCard alerts={diagnostics.alerts} online={connection === "online"} />

      {diagnostics.simulation.available && (
        <SimulationCard tools={diagnostics.simulation} selected={selected} />
      )}
    </div>
  );
}

/* ── Kennzahlen ──────────────────────────────────────────────────────────── */

function Fact({ label, value, tone }: { label: string; value: string; tone?: Tone }) {
  return (
    <div className="fact">
      <dt className="fact__label">{label}</dt>
      <dd className={`fact__value${tone ? ` fact__value--${tone}` : ""}`}>{value}</dd>
    </div>
  );
}

/* ── Dienste ─────────────────────────────────────────────────────────────── */

/**
 * Die Hintergrunddienste mit ihrem Neustartzähler.
 *
 * Der Zähler ist die eigentliche Information: Ein Dienst, der läuft, aber
 * viermal neu gestartet wurde, ist nicht dasselbe wie einer, der seit dem
 * Start durchläuft. Der Zustand allein verschweigt das.
 */
function ServicesCard({ services }: { services: Record<string, ServiceStatus> }) {
  const entries = Object.entries(services).sort(([a], [b]) => a.localeCompare(b));

  return (
    <Card title={t("diag.services")}>
      {entries.length === 0 ? (
        <Status tone="unknown" label={t("state.unknown")} compact />
      ) : (
        <ul className="rows">
          {entries.map(([name, service]) => {
            return (
              <li key={name} className="srow">
                <span className="srow__name mono">{name}</span>
                <Status
                  tone={serviceTone(service.state)}
                  label={t(`service.${service.state}`, service.state)}
                  compact
                />
                <span className="srow__meta numeric">
                  {service.uptime_s !== null ? duration(service.uptime_s) : "—"}
                </span>
                <span
                  className={`srow__meta numeric${service.restarts > 0 ? " srow__meta--warn" : ""}`}
                >
                  {t("diag.restarts", undefined, { count: String(service.restarts) })}
                </span>
                {service.last_error && (
                  <span className="srow__error mono">{service.last_error}</span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}

function serviceTone(state: ServiceStatus["state"]): Tone {
  switch (state) {
    case "RUNNING": return "ok";
    case "STARTING": return "accent";
    case "RESTARTING": return "warn";
    case "FAILED": return "error";
    default: return "neutral";
  }
}

/* ── Adapter ─────────────────────────────────────────────────────────────── */

/**
 * Woher die Werte kommen.
 *
 * Beim Anschließen die erste Frage überhaupt: Läuft der Adapter, und wie
 * viele Entities bedient er? Steht hier nichts, kommt auch nirgends etwas an
 * — dann lohnt kein Blick in die Entity-Tabelle.
 */
function AdaptersCard({
  adapters,
}: {
  adapters: { name: string; link: string; source: string; entities: number; poll_interval_s: number }[];
}) {
  return (
    <Card title={t("diag.adapters")}>
      {adapters.length === 0 ? (
        // Kein Adapter ist ein aussagekräftiger Zustand und keine leere
        // Liste: Im Produktivbetrieb heißt es, dass noch keine reale
        // Anbindung konfiguriert ist (offene Punkte A2/A3).
        <Status tone="warn" label={t("diag.noAdapters")} compact />
      ) : (
        <ul className="rows">
          {adapters.map((adapter) => (
            <li key={adapter.name} className="srow">
              <span className="srow__name mono">{adapter.name}</span>
              <Status
                tone={linkTone(adapter.link as Link)}
                label={t(`link.${adapter.link}`, adapter.link)}
                compact
              />
              <span className="srow__meta mono">{adapter.source}</span>
              <span className="srow__meta numeric">
                {t("diag.adapterEntities", undefined, { count: String(adapter.entities) })}
              </span>
              <span className="srow__meta numeric">{adapter.poll_interval_s} s</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

/* ── Meldungen ───────────────────────────────────────────────────────────── */

/**
 * Alle Meldungen, auch die der Stufe INFO.
 *
 * Das Dashboard blendet INFO aus — dort wäre „für diese Funktion ist noch
 * keine Hardware zugeordnet" nur Lärm. Hier ist genau das die Liste, die man
 * abarbeitet.
 */
function AlertsCard({ alerts, online }: { alerts: AlertItem[]; online: boolean }) {
  if (!online) {
    return (
      <Card title={t("diag.alerts")}>
        <Status tone="unknown" label={t("dash.warningsUnknown")} compact />
      </Card>
    );
  }

  const sorted = [...alerts].sort((a, b) => rank(b.severity) - rank(a.severity));
  const relevant = alerts.filter((alert) => alert.severity !== "INFO").length;

  return (
    <Card
      title={t("diag.alerts")}
      /* Zwei Zahlen, weil sie Verschiedenes bedeuten: Eine nackte „26" liest
         sich wie sechsundzwanzig Störungen, obwohl fünfundzwanzig davon
         Hinweise auf offene Zuordnungen sind. */
      action={
        <span className="diag__count" title={t("diag.alertCountHint")}>
          {relevant} / {alerts.length}
        </span>
      }
      emphasis={sorted.some((alert) => alert.severity === "CRITICAL")}
    >
      {sorted.length === 0 ? (
        <Status tone="ok" label={t("dash.noWarnings")} compact />
      ) : (
        <ul className="rows rows--scroll">
          {sorted.map((alert) => (
            <li key={alert.id} className="arow">
              <Status
                tone={severityTone(alert.severity)}
                label={t(`severity.${alert.severity}`, alert.severity)}
                compact
              />
              <span className="arow__entity mono">{alert.entity_id ?? "—"}</span>
              <span className="arow__text">
                {t(alert.message_key, alert.message_key, alert.params)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

function rank(severity: AlertItem["severity"]): number {
  return { INFO: 0, NOTICE: 1, WARNING: 2, CRITICAL: 3 }[severity];
}

function severityTone(severity: AlertItem["severity"]): Tone {
  switch (severity) {
    case "CRITICAL": return "error";
    case "WARNING": return "warn";
    case "NOTICE": return "accent";
    default: return "neutral";
  }
}

/* ── Entity-Tabelle ──────────────────────────────────────────────────────── */

function EntityRow({
  entity,
  newest,
  selected,
  onSelect,
}: {
  entity: EntityView;
  newest: number;
  selected: boolean;
  onSelect: (id: string) => void;
}) {
  const definition = entity.definition;
  const name = definition?.name_key ? t(definition.name_key, entity.entity_id) : entity.entity_id;
  const { quality, value, unit, source } = entity.state;

  return (
    <div
      className={`dtable__row${selected ? " dtable__row--selected" : ""}`}
      role="row"
      tabIndex={0}
      onClick={() => onSelect(entity.entity_id)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect(entity.entity_id);
        }
      }}
    >
      <span role="cell" className="dtable__name">
        {name}
        {definition?.unverified && (
          <span className="tag tag--open">{t("state.unverified")}</span>
        )}
        {definition?.configured === false && !definition?.unverified && (
          <span className="tag tag--open">{t("state.notConfigured")}</span>
        )}
      </span>

      <span role="cell" className="mono dtable__id">{entity.entity_id}</span>

      <span role="cell">
        <Status tone={linkTone(entity.link)} label={t(`link.${entity.link}`, entity.link)} compact />
      </span>

      <span role="cell">
        <Status
          tone={qualityTone(quality)}
          label={t(`quality.${quality}`, quality)}
          compact
        />
      </span>

      {/* Der Rohwert, ungerundet und unübersetzt. Ist er `null`, steht hier
          nichts — nie eine 0 (Kapitel 18 §38). */}
      <span role="cell" className="numeric dtable__num">
        {value === null || value === undefined ? "—" : `${String(value)}${unit ? ` ${unit}` : ""}`}
      </span>

      <span role="cell" className="mono dtable__source">{source ?? "—"}</span>

      <Lag receivedAt={entity.state.received_at} newest={newest} expected={definition?.expected_interval_s ?? null} />
    </div>
  );
}

/**
 * Der Rückstand, gelesen gegen das, was erwartet wird.
 *
 * Eine nackte Zahl wäre hier eine Falle. Ein Garagentor meldet sich nur, wenn
 * es fährt; sein Zeitstempel steht dann stundenlang, und das ist der
 * Normalzustand. Ein Tankfühler mit erwartetem Intervall von zehn Sekunden,
 * dessen Zeitstempel eine Minute steht, ist dagegen ein Befund.
 *
 * Dieselbe Zahl, zwei Bedeutungen — die Spalte sagt deshalb, welche gilt:
 * gedämpft, wo nichts erwartet wird, hervorgehoben, wo die Erwartung
 * verfehlt ist.
 */
function Lag({
  receivedAt,
  newest,
  expected,
}: {
  receivedAt: string;
  newest: number;
  expected: number | null;
}) {
  const seconds = lagSeconds(receivedAt, newest);
  const overdue = seconds !== null && expected !== null && seconds > expected;
  const tone = expected === null ? " dtable__lag--idle" : overdue ? " dtable__lag--overdue" : "";

  return (
    <span
      role="cell"
      className={`numeric dtable__num${tone}`}
      title={expected === null ? t("diag.lagNoInterval") : t("diag.lagExpected", undefined, { seconds: String(expected) })}
    >
      {seconds === null ? "—" : duration(seconds)}
    </span>
  );
}

/* ── Simulationswerkzeuge ────────────────────────────────────────────────── */

/**
 * Fehlerbilder auslösen und Messwerte setzen.
 *
 * Beides gibt es ausschließlich in der Simulation, und beides wird hier nur
 * dann angeboten, wenn das Backend die ausgewählte Entity dafür nennt. Die
 * Oberfläche führt keine eigene Liste darüber, was der Simulator kann —
 * sonst gäbe es zwei Wahrheiten über denselben Simulator.
 */
function SimulationCard({
  tools,
  selected,
}: {
  tools: SimulationTools;
  selected: string | null;
}) {
  const [level, setLevelInput] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  // Fehlt die Entity in der Auskunft, wird sie nicht simuliert. Es gibt dann
  // nichts anzubieten — kein leeres Formular, das nur so aussieht.
  const entityTools = selected === null ? undefined : tools.entities[selected];
  const canInject = entityTools !== undefined;
  const canSet = entityTools?.settable === true;
  const faults = entityTools?.faults ?? [];

  async function run(action: Promise<string | null>): Promise<void> {
    const error = await action;
    setFeedback(error ?? t("diag.simDone"));
  }

  return (
    <Card title={t("diag.simTitle")}>
      <p className="diag__note">{t("diag.simHint")}</p>

      <div className="sim">
        <span className="sim__label">{t("diag.simSelected")}</span>
        <span className="sim__target mono">{selected ?? t("diag.simNoSelection")}</span>
      </div>

      <div className="sim">
        <span className="sim__label">{t("diag.simFault")}</span>
        <span className="sim__controls">
          {faults.length === 0 ? (
            /* Ohne Auswahl fehlt die Angabe; mit einer nicht simulierten
               Entity gibt es nichts anzubieten — die Begründung dafür steht
               als Hinweis unter der Karte und wird hier nicht wiederholt. */
            <span className="sim__target">
              {selected === null ? t("diag.simNoSelection") : "—"}
            </span>
          ) : (
            faults.map((fault) => (
              <Button
                key={fault}
                variant={fault === "NONE" ? "quiet" : "default"}
                onClick={() => void run(injectFault(selected as string, fault))}
              >
                {t(`sim.fault.${fault}`, fault)}
              </Button>
            ))
          )}
        </span>
      </div>

      <div className="sim">
        <span className="sim__label">{t("diag.simLevel")}</span>
        <span className="sim__controls">
          <input
            type="number"
            className="input input--narrow numeric"
            value={level}
            disabled={!canSet}
            onChange={(event) => setLevelInput(event.target.value)}
            aria-label={t("diag.simLevel")}
          />
          <Button
            disabled={!canSet || level.trim() === "" || Number.isNaN(Number(level))}
            onClick={() => void run(setLevel(selected as string, Number(level)))}
          >
            {t("diag.simApply")}
          </Button>
        </span>
      </div>

      {selected !== null && !canInject && (
        <p className="diag__note">{t("diag.simNotSimulated")}</p>
      )}
      {canInject && !canSet && (
        <p className="diag__note">{t("diag.simNotSettable")}</p>
      )}
      {feedback && <p className="diag__feedback mono">{feedback}</p>}
    </Card>
  );
}

/* ── Auswertung ──────────────────────────────────────────────────────────── */

/**
 * Ob eine Entity gerade auffällig ist.
 *
 * „Nicht konfiguriert" und „noch zu verifizieren" zählen ausdrücklich nicht
 * dazu — siehe den Kopf dieser Datei.
 */
function isIssue(entity: EntityView): boolean {
  if (isOpen(entity)) return false;
  if (entity.link !== Link.Online) return true;
  return entity.state.quality !== Quality.Valid;
}

/**
 * Ob an dieser Entity noch etwas offen ist.
 *
 * Ausdrücklich ein **Oder**, kein Und und keine Summe: Bei der Heizung trifft
 * beides zugleich zu — was noch zu verifizieren ist, ist erst recht nicht
 * zugeordnet. Wer die beiden Zähler addiert, kommt auf mehr offene Punkte als
 * es Entities gibt.
 */
function isOpen(entity: EntityView): boolean {
  const definition = entity.definition;
  return definition?.unverified === true || definition?.configured === false;
}

function filter(entities: EntityView[], query: string, scope: Scope): EntityView[] {
  const needle = query.trim().toLowerCase();

  return entities
    .filter((entity) => {
      if (scope === "issues" && !isIssue(entity)) return false;
      if (scope === "open" && !isOpen(entity)) return false;
      if (needle === "") return true;

      // Gesucht wird über Kennung **und** übersetzten Namen. Wer „Garage"
      // tippt, denkt nicht an `vehicle.garage.door`; wer die Kennung kennt,
      // tippt sie.
      const name = entity.definition?.name_key ? t(entity.definition.name_key) : "";
      return (
        entity.entity_id.toLowerCase().includes(needle) ||
        name.toLowerCase().includes(needle)
      );
    })
    .sort((a, b) => a.entity_id.localeCompare(b.entity_id));
}

function linkTone(link: Link): Tone {
  switch (link) {
    case Link.Online: return "ok";
    case Link.Degraded:
    case Link.Reconnecting: return "warn";
    case Link.Offline:
    case Link.Error: return "error";
    case Link.Initializing: return "accent";
    default: return "unknown";
  }
}

function qualityTone(quality: Quality): Tone {
  switch (quality) {
    case Quality.Valid: return "ok";
    case Quality.Stale: return "warn";
    case Quality.Invalid:
    case Quality.Error: return "error";
    default: return "unknown";
  }
}

/* ── Rückstand ───────────────────────────────────────────────────────────── */

function newestTimestamp(entities: EntityView[]): number {
  let newest = 0;
  for (const entity of entities) {
    const at = Date.parse(entity.state.received_at);
    if (!Number.isNaN(at) && at > newest) newest = at;
  }
  return newest;
}

/**
 * Wie weit ein Wert hinter dem jüngsten Stand des Systems zurückliegt.
 *
 * Bewusst **nicht** gegen die Uhr des Tablets gerechnet. Der Zeitstempel
 * stammt vom Rechner im Fahrzeug, und ein Fahrzeug ohne dauerhafte
 * Internetverbindung hat regelmäßig eine abweichende Uhr. Stünde dann „vor
 * drei Stunden" an einem Wert, der gerade eben eingetroffen ist, wäre das
 * ausgerechnet auf der Diagnoseseite die schädlichste Art von Falschauskunft.
 *
 * Verglichen wird deshalb Backend-Zeit mit Backend-Zeit: gegen den jüngsten
 * Zeitstempel, den irgendeine Entity trägt. Die Spalte beantwortet damit
 * genau die Frage, die beim Anschließen zählt — bewegt sich dieser Wert mit
 * dem Rest, oder steht er?
 */
function lagSeconds(receivedAt: string, newest: number): number | null {
  const at = Date.parse(receivedAt);
  if (Number.isNaN(at) || newest === 0) return null;
  return Math.max(0, Math.round((newest - at) / 1000));
}

function duration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)} s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min`;
  return `${Math.floor(seconds / 3600)} h`;
}
