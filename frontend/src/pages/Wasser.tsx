/**
 * Die Wasserseite.
 *
 * Sie beantwortet die eine Frage, die im Alltag zählt: **Wie viel Wasser habe
 * ich noch, und wie viel Platz ist im Abwasser?**
 *
 * Deshalb steht die Gesamtmenge Frischwasser über beide Tanks oben und groß.
 * Die Einzeltanks stehen darunter — man braucht sie, wenn etwas nicht stimmt,
 * aber nicht für die Alltagsfrage (Kapitel 8 §1: Detailtiefe folgt der
 * Wichtigkeit, nicht der Verfügbarkeit).
 *
 * Gerechnet wird nichts hier. Die Summe kommt aus dem Backend, samt der Regel,
 * dass es keine Summe gibt, wenn ein Tank keinen belastbaren Wert liefert.
 */

import { Button, Card, Row, StaleMark, Status, Toggle } from "../design/primitives";
import { IconPump, IconValve } from "../design/icons";
import { isOn, isUnknown, textOf, useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { Quality } from "../realtime/types";
import { useWater, type FreshGroup, type Level, type TankView } from "../water/useWater";
import { HistoryCard } from "../history/HistoryCard";
import { t } from "../i18n/de";
import "./wasser.css";

const USABLE: readonly string[] = [Quality.Valid, Quality.Stale];

/**
 * Welcher Tank durch welches Ventil entleert wird.
 *
 * Die Zuordnung steht hier und nicht im Backend, weil sie eine Aussage über
 * die **Darstellung** ist: Ventil und Füllstand gehören nebeneinander, damit
 * man am Entsorgungsplatz beides zugleich sieht — das offene Ventil und den
 * fallenden Stand. Zwei getrennte Listen zwängen den Benutzer, sie im Kopf
 * zusammenzubringen, und das ausgerechnet in dem Moment, in dem etwas läuft.
 *
 * Fehlt zu einem Tank ein Ventil, erscheint schlicht keine Bedienung. Der
 * Eintrag ist ein Angebot, keine Zusicherung.
 */
const DRAIN_VALVES: Record<string, string> = {
  "water.tank.grey": "water.valve.grey",
  "water.tank.black": "water.valve.black",
};

export function Wasser() {
  const water = useWater();
  const { connection } = useAppState();
  const online = connection === "online";

  return (
    <div className="wasser">
      <div className="wasser__main">
        <FreshCard fresh={water?.fresh} online={online} />
        <WasteCard tanks={water?.waste} online={online} />

        {/* Der Verlauf steht unter den aktuellen Ständen und nicht daneben:
            Erst die Frage „wie viel ist drin", dann „wie schnell geht es
            weg". */}
        <HistoryCard
          metrics={[
            { entityId: "water.tank.fresh.large" },
            { entityId: "water.tank.fresh.small" },
            { entityId: "water.tank.grey" },
            { entityId: "water.tank.black" },
          ]}
        />
      </div>

      <aside className="wasser__side">
        <SupplyCard />
        <NoteCard />
      </aside>
    </div>
  );
}

/* ── Frischwasser ────────────────────────────────────────────────────────── */

function FreshCard({ fresh, online }: { fresh?: FreshGroup; online: boolean }) {
  // Ohne Verbindung bleibt der zuletzt bekannte Stand stehen und wird als
  // veraltet gekennzeichnet — wie in der Komponente `Value`. Ihn zu leeren
  // ließe „Verbindung weg" genauso aussehen wie „kein Wert vorhanden"; dass
  // die Werte nicht mehr aktuell sind, sagt das Banner über der Seite.
  const usable = Boolean(fresh) && fresh!.litres !== null;
  const stale = fresh?.quality === Quality.Stale || !online;

  return (
    <Card title={t("water.freshTotal")}>
      <div className="wasser__total">
        {usable ? (
          <>
            <span className={`wasser__litres${stale ? " wasser__litres--stale" : ""}`}>
              <span className="numeric">{Math.round(fresh!.litres!)}</span>
              <span className="wasser__unit">L</span>
            </span>
            <span className="wasser__of">
              {t("water.remaining")} · {formatL(fresh!.capacity_l)} {t("water.capacity")}
            </span>
            {/* Auch die Gesamtmenge wird gekennzeichnet, nicht nur die
                einzelnen Tanks — sonst wäre die auffälligste Zahl der Seite
                die einzige ohne Hinweis. */}
            {fresh?.quality === Quality.Stale && <StaleMark />}
          </>
        ) : (
          /* Kein Teilergebnis: Solange ein Tank nichts Belastbares meldet,
             wäre jede Gesamtzahl eine Schätzung (Kapitel 18 §38). */
          <>
            <span className="wasser__litres wasser__litres--unknown">
              —<span className="wasser__unit">L</span>
            </span>
            <span className="wasser__of">{t("water.totalUnknown")}</span>
          </>
        )}
      </div>

      <div className="wasser__totalbar">
        <RawBar
          percent={usable ? fresh!.percent : null}
          level={usable ? fresh!.level : "ok"}
          marks={[fresh?.warn_below ?? null, fresh?.critical_below ?? null]}
        />
      </div>

      {!usable && <p className="wasser__hint">{t("water.totalUnknownHint")}</p>}

      <div className="wasser__tanks">
        {(fresh?.tanks ?? []).map((tank) => (
          <TankRow key={tank.entity_id} tank={tank} online={online} />
        ))}
      </div>
    </Card>
  );
}

/* ── Abwasser ────────────────────────────────────────────────────────────── */

function WasteCard({ tanks, online }: { tanks?: TankView[]; online: boolean }) {
  return (
    <Card title={t("water.waste")}>
      <div className="wasser__tanks">
        {(tanks ?? []).map((tank) => (
          <TankRow key={tank.entity_id} tank={tank} online={online} waste />
        ))}
      </div>
    </Card>
  );
}

function TankRow({
  tank,
  online,
  waste = false,
}: {
  tank: TankView;
  online: boolean;
  /** Beim Abwasser interessiert der freie Platz, nicht der Inhalt. */
  waste?: boolean;
}) {
  const usable = USABLE.includes(tank.quality) && tank.percent !== null;
  const stale = tank.quality === Quality.Stale || !online;
  const valveId = DRAIN_VALVES[tank.entity_id];

  return (
    <div className="tankrow">
      <div className="tankrow__head">
        <span className="tankrow__name">{t(tank.name_key, tank.entity_id)}</span>
        <span className={`tankrow__value${stale && usable ? " tankrow__value--stale" : ""}`}>
          {usable ? (
            <>
              <span className="numeric">{Math.round(tank.percent!)}</span>
              <span className="tankrow__unit">%</span>
            </>
          ) : (
            <span className="tankrow__unknown">{t("state.unknown")}</span>
          )}
        </span>
      </div>

      <RawBar
        percent={usable ? tank.percent : null}
        level={usable ? tank.level : "ok"}
        marks={[
          tank.warn_below ?? tank.warn_above ?? null,
          tank.critical_below ?? tank.critical_above ?? null,
        ]}
      />

      <div className="tankrow__foot">
        {usable && tank.litres !== null ? (
          <span>
            {waste
              ? `${formatL(tank.litres)} ${t("water.filled")} · ${formatL(tank.free_l)} frei`
              : `${formatL(tank.litres)} ${t("water.remaining")}`}
          </span>
        ) : (
          <span>{formatL(tank.capacity_l)} {t("water.capacity")}</span>
        )}
        {usable && tank.quality === Quality.Stale && <StaleMark />}
      </div>

      {valveId !== undefined && <ValveRow valveId={valveId} online={online} />}
    </div>
  );
}

/* ── Ablassventil ────────────────────────────────────────────────────────── */

/**
 * Ein Ablassventil: zwei Stellungen, zwei Schaltflächen, kein Stopp.
 *
 * Der fehlende Stopp ist keine Auslassung dieser Datei — die Entity bietet
 * ihn nicht an, weil die Hardware ihn nicht hat. Deshalb wird auch hier
 * nichts fest verdrahtet: Welche Schaltfläche erscheint, entscheidet die
 * Capability (Kapitel 12 §55).
 *
 * **Ein offenes Ventil wird hervorgehoben, nicht nur benannt.** Es ist der
 * einzige Zustand auf dieser Seite, der von selbst nicht wieder weggeht und
 * dessen Vergessen etwas kostet — der Tank läuft leer, und beim Losfahren
 * fährt ein offenes Ventil mit.
 */
function ValveRow({ valveId, online }: { valveId: string; online: boolean }) {
  const valve = useEntity(valveId);
  const { pending } = useAppState();
  const definition = valve?.definition;
  const name = definition?.name_key ? t(definition.name_key) : valveId;

  if (definition === undefined) return null;

  if (definition.configured === false) {
    return (
      <div className="valve">
        <span className="valve__icon"><IconValve size={16} /></span>
        <span className="valve__label">{t("water.drain")}</span>
        <Status tone="unknown" label={t("state.notConfigured")} compact />
      </div>
    );
  }

  const verbs = new Set((definition.capabilities ?? []).map((c) => c.verb));
  const value = online ? textOf(valve) : null;
  const isOpen = value === "OPEN";
  const busy = pending.has(valveId);

  function drive(verb: string) {
    // Ob eine Bestätigung nötig ist, steht in der Capability. Der Loader
    // stuft `open` und `close` getrennt ein — die Oberfläche liest die
    // Einstufung, sie erfindet sie nicht (Kapitel 15 §21).
    const needed =
      (definition!.capabilities ?? []).find((c) => c.verb === verb)
        ?.needs_confirmation ?? false;
    if (needed && !window.confirm(t("water.confirmDrain", undefined, { name }))) {
      return;
    }
    sendCommand(valveId, verb);
  }

  return (
    <div className={`valve${isOpen ? " valve--open" : ""}`}>
      <span className="valve__icon"><IconValve size={16} /></span>
      <span className="valve__label">{t("water.drain")}</span>

      <span className="valve__state">
        {value === null ? (
          <Status tone="unknown" label={t("state.unknown")} compact />
        ) : (
          <Status
            tone={isOpen ? "warn" : "ok"}
            label={isOpen ? t("water.valveRunning") : t("state.closed")}
            compact
          />
        )}
      </span>

      <span className="valve__controls">
        <Button
          disabled={!online || busy || !verbs.has("open")}
          onClick={() => drive("open")}
        >
          {t("water.valveOpen")}
        </Button>
        {/* Schließen bleibt erreichbar, solange das Ventil offen ist — auch
            während ein Befehl läuft wäre es das Falsche, es zu sperren. Es
            ist die Handlung, die den Zustand beendet. */}
        <Button
          variant={isOpen ? "accent" : "default"}
          disabled={!online || busy || !verbs.has("close")}
          onClick={() => drive("close")}
        >
          {t("water.valveClose")}
        </Button>
      </span>
    </div>
  );
}

/**
 * Ein Balken für einen bereits geprüften Wert.
 *
 * `Bar` aus dem Designsystem arbeitet über eine Entity; hier liegt der Wert
 * schon als geprüfte Zahl aus dem Backend vor. Bei `null` bleibt der Balken
 * leer und schraffiert — er zeigt nie „0 %“.
 *
 * **Farbe nur bei überschrittener Schwelle.** Ob eine Schwelle überschritten
 * ist, entscheidet das Backend; hier wird das Ergebnis nur dargestellt. Ein
 * Wert ohne konfigurierte Schwelle bleibt neutral — die Software hat dann
 * keine Grundlage für eine Bewertung.
 *
 * Die Schwelle selbst wird als Markierung eingezeichnet. Dadurch sieht man
 * nicht nur *dass* es eng wird, sondern auch, wie weit es noch hin ist.
 */
function RawBar({
  percent,
  level = "ok",
  marks = [],
}: {
  percent: number | null;
  level?: Level;
  /** Die konfigurierten Schwellen. `null`-Einträge werden übersprungen. */
  marks?: (number | null)[];
}) {
  const width = percent === null ? 0 : Math.max(0, Math.min(100, percent));

  return (
    <div className={`bar${percent === null ? " bar--unknown" : ""}`}>
      <div
        className={`bar__fill bar__fill--${FILL[level]}`}
        style={{ width: `${width}%` }}
      />
      {marks.map((mark, index) =>
        mark === null ? null : (
          <span
            key={index}
            className="bar__mark"
            style={{ left: `${Math.max(0, Math.min(100, mark))}%` }}
            aria-hidden="true"
          />
        ),
      )}
    </div>
  );
}

/** Stufe → Balkenfarbe. Ohne überschrittene Schwelle bleibt es neutral. */
const FILL: Record<Level, string> = {
  ok: "accent",
  warn: "warn",
  critical: "error",
};

/* ── Versorgung ──────────────────────────────────────────────────────────── */

function SupplyCard() {
  const pump = useEntity("water.pump.main");
  const { pending, connection } = useAppState();
  const online = connection === "online";
  const configured = pump?.definition?.configured ?? false;
  const unknown = isUnknown(pump) || !online;

  return (
    <Card title={t("water.supply")}>
      <Row icon={<IconPump size={18} />} label={t("water.pump")}>
        {configured ? (
          <Toggle
            on={isOn(pump)}
            unknown={unknown}
            pending={pending.has("water.pump.main")}
            disabled={!online}
            label={t("water.pump")}
            onChange={(next) =>
              sendCommand("water.pump.main", "set_state", { state: next ? "ON" : "OFF" })
            }
          />
        ) : (
          <Status tone="unknown" label={t("state.notConfigured")} compact />
        )}
      </Row>
    </Card>
  );
}

/**
 * Was diese Seite (noch) nicht kann.
 *
 * Kapitel 18 §101: Fehlendes wird benannt statt verschwiegen. Beides hier
 * hängt an offenen Hardwarefragen, nicht an der Software.
 */
function NoteCard() {
  return (
    <Card title={t("water.notesTitle")}>
      <ul className="wasser__notes">
        <li>{t("water.thresholdsSet")}</li>
        <li>{t("water.thresholdMarks")}</li>
        <li>{t("water.valveNote")}</li>
      </ul>
      <Button variant="quiet" full disabled>
        {t("water.historyLater")}
      </Button>
    </Card>
  );
}

function formatL(litres: number | null): string {
  if (litres === null) return "—";
  return `${Math.round(litres)} L`;
}
