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

import { Button, Card, Row, Status, Toggle } from "../design/primitives";
import { IconPump } from "../design/icons";
import { isOn, isUnknown, useAppState, useEntity } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { Quality } from "../realtime/types";
import { useWater, type FreshGroup, type TankView } from "../water/useWater";
import { t } from "../i18n/de";
import "./wasser.css";

const USABLE: readonly string[] = [Quality.Valid, Quality.Stale];

export function Wasser() {
  const water = useWater();
  const { connection } = useAppState();
  const online = connection === "online";

  return (
    <div className="wasser">
      <div className="wasser__main">
        <FreshCard fresh={water?.fresh} online={online} />
        <WasteCard tanks={water?.waste} online={online} />
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
  const usable = Boolean(fresh) && online && fresh!.litres !== null;
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
          breached={usable && fresh!.breached}
          threshold={fresh?.warn_below ?? null}
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
  const usable = USABLE.includes(tank.quality) && tank.percent !== null && online;
  const stale = tank.quality === Quality.Stale || !online;

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
        breached={usable && tank.breached}
        threshold={tank.warn_below ?? tank.warn_above ?? null}
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
        {stale && usable && <span className="tankrow__stale">{t("state.stale")}</span>}
      </div>
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
  breached = false,
  threshold = null,
}: {
  percent: number | null;
  breached?: boolean;
  threshold?: number | null;
}) {
  const width = percent === null ? 0 : Math.max(0, Math.min(100, percent));
  const mark = threshold === null ? null : Math.max(0, Math.min(100, threshold));

  return (
    <div className={`bar${percent === null ? " bar--unknown" : ""}`}>
      <div
        className={`bar__fill bar__fill--${breached ? "warn" : "accent"}`}
        style={{ width: `${width}%` }}
      />
      {mark !== null && (
        <span className="bar__mark" style={{ left: `${mark}%` }} aria-hidden="true" />
      )}
    </div>
  );
}

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
