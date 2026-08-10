/**
 * Die Verlaufskarte, wie sie auf den Fachseiten steht.
 *
 * Eine Karte statt einer Kurve je Messgröße: Vier Kurven nebeneinander wären
 * vier Diagramme, die um Aufmerksamkeit konkurrieren, und auf dem iPad
 * blieben von jedem 200 Pixel übrig. Hier wird eine Größe gewählt und groß
 * gezeigt (Kapitel 8 §13).
 *
 * Was die Karte auswählbar macht, entscheidet die Seite — sie kennt ihre
 * Messgrößen. Was davon **belastbar** ist, entscheidet weiterhin das Backend.
 */

import { useState } from "react";
import { Card, Segmented, Status, formatUnit } from "../design/primitives";
import { useAppState, useEntity } from "../realtime/hooks";
import { Chart } from "./Chart";
import { SPANS, useHistory } from "./useHistory";
import { t } from "../i18n/de";

export interface Metric {
  entityId: string;
  /** Anzahl Nachkommastellen der Achsenbeschriftung. */
  decimals?: number;
}

export function HistoryCard({ metrics }: { metrics: Metric[] }) {
  const [selected, setSelected] = useState(metrics[0]?.entityId ?? null);
  const [hours, setHours] = useState<number>(24);

  const { entities } = useAppState();
  const entity = useEntity(selected ?? "");

  /* Die Namen kommen aus demselben Zustandsspiegel wie überall sonst — die
     Karte führt keine eigene Beschriftung. Ist eine Entity noch nicht
     eingetroffen, steht ihre Kennung da; erfunden wird kein Name. */
  const label = (entityId: string): string => {
    const key = entities.get(entityId)?.definition?.name_key;
    return key ? t(key, entityId) : entityId;
  };
  const history = useHistory(selected, hours);
  const metric = metrics.find((item) => item.entityId === selected);

  return (
    <Card title={t("history.title")}>
      <div className="histpick">
        <Segmented
          label={t("history.metric")}
          value={selected ?? ""}
          onChange={setSelected}
          options={metrics.map((item) => ({
            value: item.entityId,
            label: label(item.entityId),
          }))}
        />
        <Segmented
          label={t("history.span")}
          value={hours}
          onChange={setHours}
          options={SPANS.map((span) => ({ value: span.hours, label: t(span.key) }))}
        />
      </div>

      {history === null ? (
        <p className="chart__empty">{t("history.loading")}</p>
      ) : !history.available ? (
        /* „Nicht verfügbar" statt einer leeren Kurve: Eine leere Fläche sähe
           aus wie „nichts passiert" und wäre damit eine Aussage über das
           Fahrzeug statt über die Datenhaltung (Kapitel 16 §79). */
        <Status tone="unknown" label={t("history.unavailable")} />
      ) : (
        <>
          <Chart
            points={history.points}
            unit={formatUnit(entity?.definition?.unit ?? null)}
            decimals={metric?.decimals ?? 0}
          />
          <p className="chart__axis">
            <span>{t(`history.resolution.${history.resolution}`, "")}</span>
            <span>
              {t("history.pointCount", undefined, {
                count: String(history.points.length),
              })}
            </span>
          </p>
        </>
      )}
    </Card>
  );
}
