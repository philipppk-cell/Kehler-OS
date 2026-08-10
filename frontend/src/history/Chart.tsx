/**
 * Eine Verlaufskurve.
 *
 * Bewusst als SVG von Hand und ohne Diagrammbibliothek: Gebraucht wird eine
 * Linie, eine Achse und die Fähigkeit, **Lücken als Lücken** zu zeichnen. Das
 * Letzte ist genau der Punkt, an dem fertige Bibliotheken standardmäßig das
 * Falsche tun — sie verbinden über fehlende Werte hinweg. Eine Abhängigkeit
 * mitzunehmen, um ihr Standardverhalten anschließend abzuschalten, wäre der
 * schlechtere Handel (Kapitel 18 §4).
 *
 * ── Was diese Kurve nicht tut ─────────────────────────────────────────────
 *
 * Sie **interpoliert nicht über Lücken**. Ein Abschnitt endet, wo der letzte
 * belastbare Wert steht, und der nächste beginnt, wo wieder einer vorliegt.
 * Dazwischen ist nichts — kein Strich, keine gestrichelte Linie, keine
 * Schätzung.
 *
 * Sie **beginnt nicht bei null**, wenn die Werte es nicht tun. Ein
 * Ladezustand zwischen 58 % und 62 % gegen eine Achse ab 0 % gezeichnet ist
 * eine flache Linie, die nichts zeigt. Der Bereich folgt den Daten; die Achse
 * ist beschriftet, damit niemand die Skala rät.
 */

import { useId } from "react";
import { gaps, segments, type HistoryPoint } from "./useHistory";
import { t } from "../i18n/de";
import "./chart.css";

const VIEW_W = 1000;
const VIEW_H = 260;
const PAD = { top: 12, right: 8, bottom: 26, left: 46 };

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
  const usable = points.filter((point) => point.value !== null);

  if (usable.length === 0) {
    return <p className="chart__empty">{t("history.empty")}</p>;
  }

  const first = points[0];
  const last = points[points.length - 1];
  if (!first || !last) return <p className="chart__empty">{t("history.empty")}</p>;

  const from = first.at;
  const to = last.at;
  const span = Math.max(1, to - from);

  const values = usable.map((point) => point.value as number);
  const { low, high } = bounds(Math.min(...values), Math.max(...values));

  const x = (at: number) =>
    PAD.left + ((at - from) / span) * (VIEW_W - PAD.left - PAD.right);
  const y = (value: number) =>
    PAD.top + (1 - (value - low) / (high - low)) * (VIEW_H - PAD.top - PAD.bottom);

  const parts = segments(points);
  const holes = gaps(points);
  const ticks = [low, (low + high) / 2, high];

  return (
    <figure className="chart">
      <svg
        className="chart__svg"
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        preserveAspectRatio="none"
        role="img"
        aria-label={t("history.chartLabel")}
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.28" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {ticks.map((value) => (
          <g key={value}>
            <line
              className="chart__grid"
              x1={PAD.left}
              x2={VIEW_W - PAD.right}
              y1={y(value)}
              y2={y(value)}
            />
            <text className="chart__tick" x={PAD.left - 8} y={y(value) + 4}>
              {value.toFixed(decimals)}
            </text>
          </g>
        ))}

        {/* Lücken werden gezeichnet, nicht nur ausgelassen. Eine kurze Lücke
            ist wenige Pixel breit und sähe sonst aus wie ein
            Darstellungsfehler statt wie eine Aussage. Sie liegt hinter der
            Kurve, damit sie den Verlauf nicht überdeckt. Mindestens drei
            Pixel breit, sonst wäre sie unsichtbar. */}
        {holes.map((hole) => (
          <rect
            key={`gap-${hole.from}`}
            className="chart__gap"
            x={x(hole.from)}
            y={PAD.top}
            width={Math.max(3, x(hole.to) - x(hole.from))}
            height={VIEW_H - PAD.top - PAD.bottom}
          />
        ))}

        {/* Je Abschnitt eine eigene Fläche und eine eigene Linie. Ein
            durchgehender Pfad über alle Punkte wäre genau die Interpolation
            über Lücken, die hier nicht stattfinden darf. */}
        {parts.map((part) => (
          <path
            key={`area-${key(part)}`}
            className="chart__area"
            fill={`url(#${gradientId})`}
            d={areaPath(part, x, y)}
          />
        ))}
        {parts.map((part) => (
          <path key={`line-${key(part)}`} className="chart__line" d={linePath(part, x, y)} />
        ))}

        {/* Ein Abschnitt aus einem einzigen Wert hätte keine Linie. Er wird
            als Punkt gezeichnet, statt zu verschwinden — ein Messwert
            zwischen zwei Lücken ist eine Information. */}
        {parts
          .flatMap((part) => (part.length === 1 ? part : []))
          .map((point) => (
            <circle
              key={`dot-${point.at}`}
              className="chart__dot"
              cx={x(point.at)}
              cy={y(point.value as number)}
              r={3}
            />
          ))}
      </svg>

      <figcaption className="chart__axis">
        <span>{clock(from)}</span>
        {unit && <span className="chart__unit">{unit}</span>}
        <span>{clock(to)}</span>
      </figcaption>
    </figure>
  );
}

/**
 * Der dargestellte Wertebereich.
 *
 * Mit etwas Luft nach oben und unten, damit die Kurve nicht am Rand klebt —
 * und mit einer Mindesthöhe: Bei einem über Stunden konstanten Wert wäre
 * `high - low` sonst null, und die Linie läge entweder außerhalb des Bildes
 * oder mitten auf einer Rasterlinie mit drei identischen Achsenbeschriftungen.
 */
function bounds(min: number, max: number): { low: number; high: number } {
  if (max - min < 1e-9) {
    const pad = Math.max(Math.abs(max) * 0.05, 1);
    return { low: min - pad, high: max + pad };
  }
  const pad = (max - min) * 0.12;
  return { low: min - pad, high: max + pad };
}

function linePath(
  part: HistoryPoint[],
  x: (at: number) => number,
  y: (value: number) => number,
): string {
  return part
    .map((point, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command}${x(point.at).toFixed(2)} ${y(point.value as number).toFixed(2)}`;
    })
    .join(" ");
}

function areaPath(
  part: HistoryPoint[],
  x: (at: number) => number,
  y: (value: number) => number,
): string {
  const head = part[0];
  const tail = part[part.length - 1];
  if (!head || !tail) return "";

  const base = VIEW_H - PAD.bottom;
  return (
    `${linePath(part, x, y)} ` +
    `L${x(tail.at).toFixed(2)} ${base} L${x(head.at).toFixed(2)} ${base} Z`
  );
}

/** Ein stabiler Schlüssel je Abschnitt — sein erster Zeitstempel. */
function key(part: HistoryPoint[]): string {
  return String(part[0]?.at ?? "leer");
}

function clock(at: number): string {
  return new Date(at).toLocaleString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
