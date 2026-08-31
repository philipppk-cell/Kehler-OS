/**
 * Verlaufskurve mit interaktiver Messwertanzeige.
 *
 * Maus:
 *   Einfach über das Diagramm fahren.
 *
 * Touch / iPad:
 *   Finger auflegen und horizontal über den Verlauf ziehen.
 *
 * Der Cursor springt ausschließlich auf tatsächlich vorhandene Messpunkte.
 * Es wird niemals zwischen zwei Messwerten interpoliert.
 */

import { useId, useRef, useState } from "react";
import type {
  KeyboardEvent as ReactKeyboardEvent,
  PointerEvent as ReactPointerEvent,
} from "react";

import {
  gaps,
  segments,
  type HistoryPoint,
} from "./useHistory";

import { t } from "../i18n/de";
import "./chart.css";

const VIEW_W = 1000;
const VIEW_H = 260;

const PAD = {
  top: 12,
  right: 8,
  bottom: 26,
  left: 46,
};

export function Chart({
  points,
  unit,
  decimals = 0,
}: {
  points: HistoryPoint[];
  unit?: string;
  decimals?: number;
}) {
  const gradientId = useId();

  const svgRef =
    useRef<SVGSVGElement | null>(null);

  const [activeAt, setActiveAt] =
    useState<number | null>(null);

  const usable = points.filter(
    (point) => point.value !== null,
  );

  if (usable.length === 0) {
    return (
      <p className="chart__empty">
        {t("history.empty")}
      </p>
    );
  }

  const first = points[0];
  const last = points[points.length - 1];

  if (!first || !last) {
    return (
      <p className="chart__empty">
        {t("history.empty")}
      </p>
    );
  }

  const from = first.at;
  const to = last.at;
  const span = Math.max(1, to - from);

  const values = usable.map(
    (point) => point.value as number,
  );

  const { low, high } = bounds(
    Math.min(...values),
    Math.max(...values),
  );

  const x = (at: number) =>
    PAD.left +
    ((at - from) / span) *
      (VIEW_W - PAD.left - PAD.right);

  const y = (value: number) =>
    PAD.top +
    (
      1 -
      (value - low) / (high - low)
    ) *
      (
        VIEW_H -
        PAD.top -
        PAD.bottom
      );

  const parts = segments(points);
  const holes = gaps(points);

  const ticks = [
    low,
    (low + high) / 2,
    high,
  ];

  const activePoint =
    activeAt === null
      ? null
      : (
          usable.find(
            (point) =>
              point.at === activeAt,
          ) ?? null
        );

  const cursorX =
    activePoint === null
      ? null
      : x(activePoint.at);

  const cursorPercent =
    cursorX === null
      ? 0
      : (cursorX / VIEW_W) * 100;

  const tooltipAlign =
    cursorPercent < 18
      ? "start"
      : cursorPercent > 82
        ? "end"
        : "center";

  /*
   * Aus der tatsächlichen Bildschirmposition wird
   * der gewünschte Zeitpunkt im Diagramm berechnet.
   */
  function pointerTime(
    event: ReactPointerEvent<SVGSVGElement>,
  ): number | null {
    const svg = svgRef.current;

    if (svg === null) {
      return null;
    }

    const rect =
      svg.getBoundingClientRect();

    if (rect.width <= 0) {
      return null;
    }

    const relative =
      (
        event.clientX -
        rect.left
      ) / rect.width;

    const viewX =
      relative * VIEW_W;

    const plotLeft = PAD.left;

    const plotRight =
      VIEW_W - PAD.right;

    const plotRatio = Math.max(
      0,
      Math.min(
        1,
        (
          viewX -
          plotLeft
        ) /
          (
            plotRight -
            plotLeft
          ),
      ),
    );

    return (
      from +
      plotRatio * span
    );
  }

  /*
   * Findet effizient den zeitlich nächsten echten Messpunkt.
   * Keine Interpolation.
   */
  function nearestPoint(
    targetAt: number,
  ): HistoryPoint | null {
    if (usable.length === 0) {
      return null;
    }

    let lowIndex = 0;
    let highIndex =
      usable.length - 1;

    while (
      lowIndex <= highIndex
    ) {
      const middle =
        Math.floor(
          (
            lowIndex +
            highIndex
          ) / 2,
        );

      const point =
        usable[middle];

      if (!point) {
        break;
      }

      if (
        point.at < targetAt
      ) {
        lowIndex =
          middle + 1;
      } else {
        highIndex =
          middle - 1;
      }
    }

    const right =
      usable[
        Math.min(
          lowIndex,
          usable.length - 1,
        )
      ];

    const left =
      usable[
        Math.max(
          0,
          lowIndex - 1,
        )
      ];

    if (!left) {
      return right ?? null;
    }

    if (!right) {
      return left;
    }

    return (
      Math.abs(
        left.at - targetAt,
      ) <=
      Math.abs(
        right.at - targetAt,
      )
        ? left
        : right
    );
  }

  function selectPointer(
    event: ReactPointerEvent<SVGSVGElement>,
  ) {
    const at =
      pointerTime(event);

    if (at === null) {
      return;
    }

    const point =
      nearestPoint(at);

    if (point !== null) {
      setActiveAt(point.at);
    }
  }

  function handlePointerDown(
    event: ReactPointerEvent<SVGSVGElement>,
  ) {
    selectPointer(event);

    /*
     * Auf Touch-Geräten bleibt der Finger auch dann
     * unserem Diagramm zugeordnet, wenn er beim
     * Ziehen etwas außerhalb gerät.
     */
    if (
      event.pointerType !== "mouse"
    ) {
      try {
        event.currentTarget
          .setPointerCapture(
            event.pointerId,
          );
      } catch {
        // Pointer Capture ist Komfort,
        // nicht Voraussetzung.
      }
    }
  }

  function handlePointerMove(
    event: ReactPointerEvent<SVGSVGElement>,
  ) {
    /*
     * Maus braucht keinen Klick.
     * Touch bewegt sich nach PointerDown mit Capture.
     */
    if (
      event.pointerType === "mouse" ||
      event.currentTarget
        .hasPointerCapture(
          event.pointerId,
        )
    ) {
      selectPointer(event);
    }
  }

  function handlePointerUp(
    event: ReactPointerEvent<SVGSVGElement>,
  ) {
    selectPointer(event);

    if (
      event.currentTarget
        .hasPointerCapture(
          event.pointerId,
        )
    ) {
      try {
        event.currentTarget
          .releasePointerCapture(
            event.pointerId,
          );
      } catch {
        // Bereits freigegeben.
      }
    }

    /*
     * Auf Touch bleibt der letzte Wert sichtbar,
     * damit man nach dem Loslassen noch lesen kann.
     */
  }

  function handleKeyboard(
    event: ReactKeyboardEvent<SVGSVGElement>,
  ) {
    if (
      event.key !== "ArrowLeft" &&
      event.key !== "ArrowRight" &&
      event.key !== "Home" &&
      event.key !== "End"
    ) {
      return;
    }

    event.preventDefault();

    if (
      event.key === "Home"
    ) {
      setActiveAt(
        usable[0]?.at ?? null,
      );

      return;
    }

    if (
      event.key === "End"
    ) {
      setActiveAt(
        usable[
          usable.length - 1
        ]?.at ?? null,
      );

      return;
    }

    const direction =
      event.key === "ArrowRight"
        ? 1
        : -1;

    let index =
      activeAt === null
        ? (
            direction > 0
              ? -1
              : usable.length
          )
        : usable.findIndex(
            (point) =>
              point.at === activeAt,
          );

    if (index < 0) {
      index =
        direction > 0
          ? -1
          : usable.length;
    }

    index = Math.max(
      0,
      Math.min(
        usable.length - 1,
        index + direction,
      ),
    );

    setActiveAt(
      usable[index]?.at ?? null,
    );
  }

  const ariaLabel =
    activePoint === null
      ? t("history.chartLabel")
      : [
          t("history.chartLabel"),
          dateLabel(
            activePoint.at,
          ),
          timeLabel(
            activePoint.at,
          ),
          formatPointValue(
            activePoint.value as number,
            decimals,
            unit,
          ),
        ].join(", ");

  return (
    <figure className="chart">
      <div className="chart__plot">
        <svg
          ref={svgRef}
          className="chart__svg"
          viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
          preserveAspectRatio="none"
          role="img"
          tabIndex={0}
          aria-label={ariaLabel}
          onPointerDown={
            handlePointerDown
          }
          onPointerMove={
            handlePointerMove
          }
          onPointerUp={
            handlePointerUp
          }
          onPointerCancel={() =>
            setActiveAt(null)
          }
          onPointerLeave={(
            event,
          ) => {
            if (
              event.pointerType ===
              "mouse"
            ) {
              setActiveAt(null);
            }
          }}
          onKeyDown={
            handleKeyboard
          }
        >
          <defs>
            <linearGradient
              id={gradientId}
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="var(--accent)"
                stopOpacity="0.28"
              />
              <stop
                offset="100%"
                stopColor="var(--accent)"
                stopOpacity="0"
              />
            </linearGradient>
          </defs>

          {ticks.map(
            (value) => (
              <g key={value}>
                <line
                  className="chart__grid"
                  x1={PAD.left}
                  x2={
                    VIEW_W -
                    PAD.right
                  }
                  y1={y(value)}
                  y2={y(value)}
                />

                <text
                  className="chart__tick"
                  x={
                    PAD.left - 8
                  }
                  y={
                    y(value) + 4
                  }
                >
                  {value.toFixed(
                    decimals,
                  )}
                </text>
              </g>
            ),
          )}

          {holes.map(
            (hole) => (
              <rect
                key={`gap-${hole.from}`}
                className="chart__gap"
                x={x(hole.from)}
                y={PAD.top}
                width={Math.max(
                  3,
                  x(hole.to) -
                    x(hole.from),
                )}
                height={
                  VIEW_H -
                  PAD.top -
                  PAD.bottom
                }
              />
            ),
          )}

          {parts.map(
            (part) => (
              <path
                key={`area-${key(part)}`}
                className="chart__area"
                fill={`url(#${gradientId})`}
                d={areaPath(
                  part,
                  x,
                  y,
                )}
              />
            ),
          )}

          {parts.map(
            (part) => (
              <path
                key={`line-${key(part)}`}
                className="chart__line"
                d={linePath(
                  part,
                  x,
                  y,
                )}
              />
            ),
          )}

          {parts
            .flatMap(
              (part) =>
                part.length === 1
                  ? part
                  : [],
            )
            .map(
              (point) => (
                <circle
                  key={`dot-${point.at}`}
                  className="chart__dot"
                  cx={x(point.at)}
                  cy={y(
                    point.value as number,
                  )}
                  r={3}
                />
              ),
            )}

          {activePoint !== null &&
            cursorX !== null && (
              <>
                <line
                  className="chart__cursor"
                  x1={cursorX}
                  x2={cursorX}
                  y1={PAD.top}
                  y2={
                    VIEW_H -
                    PAD.bottom
                  }
                />

                <circle
                  className="chart__cursor-dot"
                  cx={cursorX}
                  cy={y(
                    activePoint.value as number,
                  )}
                  r={5}
                />
              </>
            )}
        </svg>

        {activePoint !== null && (
          <div
            className={[
              "chart__tooltip",
              `chart__tooltip--${tooltipAlign}`,
            ].join(" ")}
            style={{
              left:
                `${cursorPercent}%`,
            }}
            aria-hidden="true"
          >
            <span className="chart__tooltip-date">
              {dateLabel(
                activePoint.at,
              )}
            </span>

            <span className="chart__tooltip-time">
              {timeLabel(
                activePoint.at,
              )}
            </span>

            <strong className="chart__tooltip-value">
              {formatPointValue(
                activePoint.value as number,
                decimals,
                unit,
              )}
            </strong>
          </div>
        )}
      </div>

      <figcaption className="chart__axis">
        <span>{clock(from)}</span>

        {unit && (
          <span className="chart__unit">
            {unit}
          </span>
        )}

        <span>{clock(to)}</span>
      </figcaption>
    </figure>
  );
}

function bounds(
  min: number,
  max: number,
): {
  low: number;
  high: number;
} {
  if (
    max - min < 1e-9
  ) {
    const pad = Math.max(
      Math.abs(max) * 0.05,
      1,
    );

    return {
      low: min - pad,
      high: max + pad,
    };
  }

  const pad =
    (max - min) * 0.12;

  return {
    low: min - pad,
    high: max + pad,
  };
}

function linePath(
  part: HistoryPoint[],
  x: (at: number) => number,
  y: (value: number) => number,
): string {
  return part
    .map(
      (point, index) => {
        const command =
          index === 0
            ? "M"
            : "L";

        return (
          `${command}` +
          `${x(point.at).toFixed(2)} ` +
          `${y(
            point.value as number,
          ).toFixed(2)}`
        );
      },
    )
    .join(" ");
}

function areaPath(
  part: HistoryPoint[],
  x: (at: number) => number,
  y: (value: number) => number,
): string {
  const head = part[0];

  const tail =
    part[
      part.length - 1
    ];

  if (!head || !tail) {
    return "";
  }

  const base =
    VIEW_H - PAD.bottom;

  return (
    `${linePath(
      part,
      x,
      y,
    )} ` +
    `L${x(tail.at).toFixed(2)} ${base} ` +
    `L${x(head.at).toFixed(2)} ${base} Z`
  );
}

function key(
  part: HistoryPoint[],
): string {
  return String(
    part[0]?.at ?? "leer",
  );
}

function clock(
  at: number,
): string {
  return new Date(
    at,
  ).toLocaleString(
    "de-DE",
    {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    },
  );
}

function dateLabel(
  at: number,
): string {
  return new Date(
    at,
  ).toLocaleDateString(
    "de-DE",
    {
      weekday: "short",
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    },
  );
}

function timeLabel(
  at: number,
): string {
  const value =
    new Date(
      at,
    ).toLocaleTimeString(
      "de-DE",
      {
        hour: "2-digit",
        minute: "2-digit",
      },
    );

  return `${value} Uhr`;
}

function formatPointValue(
  value: number,
  decimals: number,
  unit?: string,
): string {
  const formatted =
    new Intl.NumberFormat(
      "de-DE",
      {
        minimumFractionDigits:
          decimals,
        maximumFractionDigits:
          decimals,
      },
    ).format(value);

  return unit
    ? `${formatted} ${unit}`
    : formatted;
}
