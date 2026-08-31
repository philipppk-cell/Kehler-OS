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

import { useEffect, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { Button, Card, StaleMark, Status } from "../design/primitives";
import { IconValve } from "../design/icons";
import { Stellung, brauchtBestaetigung, useAktor } from "../control/actuator";
import { useAppState, useEntity } from "../realtime/hooks";
import { renewHold, sendCommand } from "../api/client";
import { Quality } from "../realtime/types";
import { useWater, type FreshGroup, type Level, type TankView } from "../water/useWater";
import {
  useWaterForecast,
  type ForecastMetric,
  type WaterForecast,
} from "../water/useWaterForecast";
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
  const waterForecast = useWaterForecast(online);

  return (
    <div className="wasser">
      <div className="wasser__main">
        <FreshCard
          fresh={water?.fresh}
          online={online}
          forecast={waterForecast.forecast}
          resetting={waterForecast.resetting}
          onReset={waterForecast.reset}
        />
        <FreshFillCard online={online} />
        <WasteCard
          tanks={water?.waste}
          online={online}
          forecast={waterForecast.forecast}
        />

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
        <NoteCard />
      </aside>
    </div>
  );
}

/* ── Frischwasser ────────────────────────────────────────────────────────── */

function FreshCard({
  fresh,
  online,
  forecast,
  resetting,
  onReset,
}: {
  fresh?: FreshGroup;
  online: boolean;
  forecast: WaterForecast | null;
  resetting: boolean;
  onReset: () => Promise<void>;
}) {
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

      <FreshForecast
        forecast={forecast}
        resetting={resetting}
        onReset={onReset}
      />

      {!usable && <p className="wasser__hint">{t("water.totalUnknownHint")}</p>}

      <div className="wasser__tanks">
        {(fresh?.tanks ?? []).map((tank) => (
          <TankRow key={tank.entity_id} tank={tank} online={online} />
        ))}
      </div>
    </Card>
  );
}

function FreshForecast({
  forecast,
  resetting,
  onReset,
}: {
  forecast: WaterForecast | null;
  resetting: boolean;
  onReset: () => Promise<void>;
}) {
  if (forecast === null) {
    return null;
  }

  const started = forecast.started_at !== null;
  const metric = forecast.fresh;

  function reset() {
    if (
      started &&
      !window.confirm(
        t("water.forecastResetConfirm"),
      )
    ) {
      return;
    }

    void onReset();
  }

  return (
    <div className="wasser__forecast">
      <div className="wasser__forecast-copy">
        <span className="wasser__forecast-label">
          {t("water.forecastTitle")}
        </span>

        {!forecast.available ? (
          <>
            <strong>
              {t("water.forecastUnavailable")}
            </strong>
          </>
        ) : !started ? (
          <>
            <strong>
              {t("water.forecastNotStarted")}
            </strong>
            <span>
              {t("water.forecastNotStartedHint")}
            </span>
          </>
        ) : metric.ready &&
          metric.rate_l_day !== null &&
          metric.remaining_days !== null ? (
          <>
            <strong className="wasser__forecast-value">
              {t("water.forecastApprox")}{" "}
              {formatForecastDuration(
                metric.remaining_days,
              )}
            </strong>

            <span>
              Ø {formatForecastRate(metric.rate_l_day)}{" "}
              {t("water.forecastLitresPerDay")}
            </span>
          </>
        ) : (
          <>
            <strong>
              {t("water.forecastCalculating")}
            </strong>
            <span>
              {t("water.forecastNeedData")}
            </span>
          </>
        )}
      </div>

      <Button
        disabled={
          !forecast.available ||
          resetting
        }
        onClick={reset}
      >
        {resetting
          ? t("water.forecastResetting")
          : started
            ? t("water.forecastReset")
            : t("water.forecastStart")}
      </Button>
    </div>
  );
}

/* ── Befüllung großer Frischwassertank ────────────────────────────────── */

const FILL_ACTIVE_ID = "water.fill.large.active";
const FILL_START_ID = "water.fill.large.start";
const FILL_STOP_ID = "water.fill.large.stop";

function FreshFillStatus() {
  const active = useEntity(FILL_ACTIVE_ID);
  const { connection } = useAppState();

  const online = connection === "online";
  const value = active?.state.value;
  const quality = active?.state.quality;

  const filling =
    online &&
    active?.definition?.configured !== false &&
    (
      quality === Quality.Valid ||
      quality === Quality.Stale
    ) &&
    value === true;

  if (!filling) {
    return null;
  }

  return (
    <div className="tankrow__fill-status">
      <Status
        tone="accent"
        label={t("water.fillActive")}
        compact
      />

      {quality === Quality.Stale && <StaleMark />}
    </div>
  );
}

function FreshFillCard({ online }: { online: boolean }) {
  const active = useEntity(FILL_ACTIVE_ID);
  const start = useEntity(FILL_START_ID);
  const stop = useEntity(FILL_STOP_ID);
  const { pending } = useAppState();

  const startBusy = pending.has(FILL_START_ID);
  const stopBusy = pending.has(FILL_STOP_ID);

  /*
   * Während eines 100-ms-Impulses wird auch der jeweils andere Knopf kurz
   * gesperrt. Dadurch können Kehler OS selbst niemals START und STOP
   * gleichzeitig auf TRUE setzen.
   */
  const busy = startBusy || stopBusy;

  /*
   * Der angezeigte Zustand stammt ausschließlich von Relais 23.
   * Ein gesendeter Start-Befehl macht daraus noch keinen laufenden Zustand.
   */
  const activeValue = active?.state.value;
  const activeQuality = active?.state.quality;

  const filling =
    online &&
    active?.definition?.configured !== false &&
    (
      activeQuality === Quality.Valid ||
      activeQuality === Quality.Stale
    ) &&
    typeof activeValue === "boolean"
      ? activeValue
      : null;

  const startReady =
    start?.definition?.configured === true &&
    (
      start.definition.capabilities.some(
        (capability) => capability.verb === "trigger",
      )
    );

  const stopReady =
    stop?.definition?.configured === true &&
    (
      stop.definition.capabilities.some(
        (capability) => capability.verb === "trigger",
      )
    );

  function trigger(entityId: string) {
    void sendCommand(entityId, "trigger");
  }

  return (
    <Card title={t("water.fillTitle")}>
      <div className="wasser__fill">
        <div className="wasser__fill-copy">
          <strong>{t("tank.fresh_large")}</strong>

        </div>

        <div
          className="wasser__fill-controls"
          role="group"
          aria-label={t("water.fillTitle")}
        >
          <Button
            variant="accent"
            disabled={!online || !startReady || busy || filling === true}
            onClick={() => trigger(FILL_START_ID)}
          >
            {startBusy
              ? t("water.fillStarting")
              : t("water.fillStart")}
          </Button>

          <Button
            disabled={!online || !stopReady || busy}
            onClick={() => trigger(FILL_STOP_ID)}
          >
            {stopBusy
              ? t("water.fillStopping")
              : t("water.fillStop")}
          </Button>
        </div>
      </div>
    </Card>
  );
}

/* ── Abwasser ────────────────────────────────────────────────────────────── */

function WasteCard({
  tanks,
  online,
  forecast,
}: {
  tanks?: TankView[];
  online: boolean;
  forecast: WaterForecast | null;
}) {
  return (
    <Card title={t("water.waste")}>
      <div className="wasser__tanks">
        {(tanks ?? []).map((tank) => (
          <TankRow
            key={tank.entity_id}
            tank={tank}
            online={online}
            waste
            forecast={
              tank.entity_id === "water.tank.grey"
                ? forecast?.grey ?? null
                : tank.entity_id === "water.tank.black"
                  ? forecast?.black ?? null
                  : null
            }
          />
        ))}
      </div>
    </Card>
  );
}

function TankRow({
  tank,
  online,
  waste = false,
  forecast = null,
}: {
  tank: TankView;
  online: boolean;
  /** Beim Abwasser interessiert der freie Platz, nicht der Inhalt. */
  waste?: boolean;
  forecast?: ForecastMetric | null;
}) {
  const usable = USABLE.includes(tank.quality) && tank.percent !== null;
  const stale = tank.quality === Quality.Stale || !online;
  const valveId = DRAIN_VALVES[tank.entity_id];

  return (
    <div className="tankrow">
      <div className="tankrow__head">
        <span className="tankrow__name">{t(tank.name_key, tank.entity_id)}</span>
        <div className="tankrow__head-right">
          {tank.entity_id === "water.tank.fresh.large" && (
            <FreshFillStatus />
          )}

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

      {waste &&
        forecast?.ready &&
        forecast.rate_l_day !== null &&
        forecast.remaining_days !== null && (
          <div className="tankrow__forecast">
            <span>
              Ø +{formatForecastRate(
                forecast.rate_l_day,
              )}{" "}
              {t("water.forecastLitresPerDay")}
            </span>

            <span>
              {t("water.forecastUntilFull")}:{" "}
              {t("water.forecastApprox")}{" "}
              {formatForecastDuration(
                forecast.remaining_days,
              )}
            </span>
          </div>
        )}

      {valveId !== undefined && <ValveRow valveId={valveId} online={online} />}
    </div>
  );
}

/* ── Ablassventil ────────────────────────────────────────────────────────── */

/**
 * Ein Ablassventil: zwei Stellungen, zwei Schaltflächen, kein Stopp.
 *
 * Zustandsanzeige und Bestätigungslogik kommen aus `control/actuator` und
 * stehen nicht mehr hier. Sie gelten für Ventile, Schrankverriegelungen und
 * die Heckklappe gleichermaßen — dreimal nebeneinander wären sie dreimal
 * Gelegenheit, auseinanderzulaufen.
 *
 * **Ein offenes Ventil wird hervorgehoben, nicht nur benannt.** Es ist der
 * einzige Zustand auf dieser Seite, der von selbst nicht wieder weggeht und
 * dessen Vergessen etwas kostet — der Tank läuft leer, und beim Losfahren
 * fährt ein offenes Ventil mit.
 */
const VALVE_HOLD_HEARTBEAT_MS = 250;
const VALVE_HOLD_ARM_MS = 8000;

function ValveRow({ valveId, online }: { valveId: string; online: boolean }) {
  const aktor = useAktor(valveId);
  const offen = aktor.zustand === "OPEN";

  const openCapability = aktor.entity?.definition?.capabilities.find(
    (capability) => capability.verb === "open",
  );
  const openHold = openCapability?.hold_to_run ?? false;

  const [holdArmed, setHoldArmed] = useState(false);
  const [holdPressed, setHoldPressed] = useState(false);

  const armedRef = useRef(false);
  const pressedRef = useRef(false);
  const releasedRef = useRef(false);
  const stoppingRef = useRef(false);
  const generationRef = useRef(0);
  const heartbeatRef = useRef<number | null>(null);
  const armTimerRef = useRef<number | null>(null);
  const startRef = useRef<ReturnType<typeof sendCommand> | null>(null);

  useEffect(() => {
    return () => {
      if (heartbeatRef.current !== null) {
        window.clearTimeout(heartbeatRef.current);
      }
      if (armTimerRef.current !== null) {
        window.clearTimeout(armTimerRef.current);
      }
    };
  }, []);

  if (aktor.entity?.definition === undefined) return null;

  function clearHeartbeat() {
    if (heartbeatRef.current !== null) {
      window.clearTimeout(heartbeatRef.current);
      heartbeatRef.current = null;
    }
  }

  function clearArmTimer() {
    if (armTimerRef.current !== null) {
      window.clearTimeout(armTimerRef.current);
      armTimerRef.current = null;
    }
  }

  function disarmHold() {
    clearArmTimer();
    armedRef.current = false;
    setHoldArmed(false);
  }

  function clearPressed() {
    pressedRef.current = false;
    setHoldPressed(false);
  }

  function armHold() {
    armedRef.current = true;
    setHoldArmed(true);

    clearArmTimer();
    armTimerRef.current = window.setTimeout(() => {
      if (!pressedRef.current) {
        disarmHold();
      }
    }, VALVE_HOLD_ARM_MS);
  }

  function drive(verb: string) {
    disarmHold();

    if (
      brauchtBestaetigung(aktor.entity, verb) &&
      !window.confirm(t("water.confirmDrain", undefined, { name: aktor.name }))
    ) {
      return;
    }

    void sendCommand(valveId, verb);
  }

  function scheduleHeartbeat(generation: number) {
    clearHeartbeat();

    heartbeatRef.current = window.setTimeout(async () => {
      if (
        releasedRef.current ||
        generationRef.current !== generation ||
        !pressedRef.current
      ) {
        return;
      }

      const ok = await renewHold(valveId, "open");

      if (!ok) {
        releasedRef.current = true;
        generationRef.current += 1;
        clearHeartbeat();
        clearPressed();
        disarmHold();
        await sendCommand(valveId, "stop");
        return;
      }

      scheduleHeartbeat(generation);
    }, VALVE_HOLD_HEARTBEAT_MS);
  }

  async function holdPointerDown(
    event: ReactPointerEvent<HTMLButtonElement>,
  ) {
    if (
      !openHold ||
      !online ||
      pressedRef.current ||
      stoppingRef.current
    ) {
      return;
    }

    event.preventDefault();

    // Erster Druck: nur Sicherheitsfreigabe. Es wird dabei noch kein
    // SPS-Eingang gesetzt. Erst der nächste Druck startet den Hold.
    if (!armedRef.current) {
      if (
        brauchtBestaetigung(aktor.entity, "open") &&
        !window.confirm(
          t("water.confirmDrain", undefined, { name: aktor.name }),
        )
      ) {
        return;
      }

      armHold();
      return;
    }

    clearArmTimer();

    try {
      event.currentTarget.setPointerCapture(event.pointerId);
    } catch {
      // Der Backend-Watchdog bleibt unabhängig von Pointer Capture aktiv.
    }

    const generation = generationRef.current + 1;
    generationRef.current = generation;
    releasedRef.current = false;
    pressedRef.current = true;
    setHoldPressed(true);

    const start = sendCommand(valveId, "open");
    startRef.current = start;

    const result = await start;

    if (startRef.current === start) {
      startRef.current = null;
    }

    if (
      releasedRef.current ||
      generationRef.current !== generation ||
      !pressedRef.current
    ) {
      return;
    }

    if (!result?.success) {
      releasedRef.current = true;
      clearPressed();
      disarmHold();
      return;
    }

    scheduleHeartbeat(generation);
  }

  async function stopHold() {
    if (
      stoppingRef.current ||
      (!pressedRef.current && startRef.current === null)
    ) {
      return;
    }

    stoppingRef.current = true;
    releasedRef.current = true;
    generationRef.current += 1;

    clearHeartbeat();
    clearArmTimer();

    try {
      // Bei extrem kurzem Antippen darf STOP nicht vor START am Backend
      // eintreffen.
      const start = startRef.current;
      if (start !== null) {
        await start;
      }

      await sendCommand(valveId, "stop");
    } finally {
      startRef.current = null;
      clearPressed();
      disarmHold();
      stoppingRef.current = false;
    }
  }

  const holdLabel = holdPressed
    ? t("water.valveHoldOpening")
    : holdArmed
      ? t("water.valveHoldReady")
      : t("water.valveOpen");

  return (
    <div className={`valve${offen ? " valve--open" : ""}`}>
      <span className="valve__icon"><IconValve size={16} /></span>
      <span className="valve__label">{t("water.drain")}</span>

      <span className="valve__state">
        <Stellung aktor={aktor} />
      </span>

      <span className="valve__controls">
        {aktor.konfiguriert && (
          <>
            {aktor.verben.has("open") && (
              openHold ? (
                <span className="valve__hold">
                  <Button
                    variant={holdArmed || holdPressed ? "accent" : "default"}
                    disabled={
                      !online ||
                      (!holdPressed && aktor.laeuft)
                    }
                    onPointerDown={(event) => void holdPointerDown(event)}
                    onPointerUp={() => void stopHold()}
                    onPointerCancel={() => void stopHold()}
                    onLostPointerCapture={() => void stopHold()}
                  >
                    {holdLabel}
                  </Button>
                </span>
              ) : (
                <Button
                  disabled={!online || aktor.laeuft}
                  onClick={() => drive("open")}
                >
                  {t("water.valveOpen")}
                </Button>
              )
            )}

            {aktor.verben.has("close") && (
              <Button
                variant={offen ? "accent" : "default"}
                disabled={!online || aktor.laeuft || holdPressed}
                onClick={() => drive("close")}
              >
                {t("water.valveClose")}
              </Button>
            )}
          </>
        )}
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

/**
 * Was diese Seite (noch) nicht kann.
 *
 * Kapitel 18 §101: Fehlendes wird benannt statt verschwiegen. Beides hier
 * hängt an offenen Hardwarefragen, nicht an der Software.
 */
function NoteCard() {
  // Der Hinweis auf die fehlende Rückmeldung steht nur da, wenn sie
  // tatsächlich fehlt.
  const grau = useEntity("water.valve.grey");
  const ohneRueckmeldung =
    grau?.definition?.feedback === false;

  /*
   * Der Sensor-Neustart gehört fachlich zur Wasserseite:
   * Hier bemerkt der Benutzer zuerst, wenn die Tankwerte nicht
   * plausibel sind oder ein Sensor nicht mehr reagiert.
   */
  const sensorRestartId = "vehicle.sensors.restart";
  const sensorRestart = useEntity(sensorRestartId);
  const { pending, connection } = useAppState();

  const online = connection === "online";
  const busy = pending.has(sensorRestartId);

  const configured =
    sensorRestart?.definition?.configured ?? false;

  const hasTrigger =
    sensorRestart?.definition?.capabilities.some(
      (capability) =>
        capability.verb === "trigger",
    ) ?? false;

  function restartSensors() {
    if (
      brauchtBestaetigung(
        sensorRestart,
        "trigger",
      ) &&
      !window.confirm(
        t("diag.sensorRestartConfirm"),
      )
    ) {
      return;
    }

    void sendCommand(
      sensorRestartId,
      "trigger",
    );
  }

  return (
    <Card title={t("water.notesTitle")}>
      <ul className="wasser__notes">
        <li>{t("water.thresholdsSet")}</li>
        <li>{t("water.thresholdMarks")}</li>
        <li>{t("water.valveNote")}</li>

        {ohneRueckmeldung && (
          <li>{t("water.valveNoFeedback")}</li>
        )}
      </ul>

      <div className="wasser__sensor-maintenance">
        <div className="wasser__sensor-maintenance-copy">
          <strong>
            {t("diag.sensorRestart")}
          </strong>

          <span>
            {t("diag.sensorRestartHint")}
          </span>
        </div>

        <Button
          variant="accent"
          full
          disabled={
            !online ||
            !configured ||
            !hasTrigger ||
            busy
          }
          onClick={restartSensors}
        >
          {busy
            ? t("diag.sensorRestartRunning")
            : t("diag.sensorRestart")}
        </Button>
      </div>

      <Button variant="quiet" full disabled>
        {t("water.historyLater")}
      </Button>
    </Card>
  );
}

const WATER_FORECAST_NUMBER =
  new Intl.NumberFormat("de-DE", {
    maximumFractionDigits: 1,
  });

function formatForecastDuration(
  days: number,
): string {
  if (days < 1) {
    const hours = Math.max(
      1,
      Math.round(days * 24),
    );

    return `${hours} ${t("water.forecastHours")}`;
  }

  return `${WATER_FORECAST_NUMBER.format(days)} ${t("water.forecastDays")}`;
}

function formatForecastRate(
  litresPerDay: number,
): string {
  return WATER_FORECAST_NUMBER.format(
    litresPerDay,
  );
}

function formatL(litres: number | null): string {
  if (litres === null) return "—";
  return `${Math.round(litres)} L`;
}
