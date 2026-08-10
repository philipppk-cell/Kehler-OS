/**
 * Schrittweise Verstellung eines Sollwerts.
 *
 * Bewusst ein Stepper und kein Schieberegler: Im fahrenden Fahrzeug trifft
 * man eine Fläche, aber keinen Punkt (Kapitel 7 §13). Ein Regler verstellt
 * sich außerdem beim versehentlichen Wischen.
 *
 * Die Grenzen kommen aus der Entity und begrenzen hier nur die Anzeige — die
 * eigentliche Prüfung macht der Command Bus, damit ein Client, der die
 * Oberfläche umgeht, ebenfalls scheitert (Kapitel 15 §42). Was hier steht,
 * ist Bequemlichkeit; was dort steht, ist die Regel.
 *
 * Der Baustein liegt im Designsystem und nicht auf einer Seite: Strom­begrenzung
 * und Solltemperatur sind fachlich weit auseinander, aber es ist derselbe
 * Handgriff — und der muss überall gleich aussehen (Kapitel 7 §39).
 */

import { useAppState } from "../realtime/hooks";
import { sendCommand } from "../api/client";
import { t } from "../i18n/de";
import "./stepper.css";

export interface StepperProps {
  entityId: string;
  /** Aktueller Wert, `null` wenn unbekannt. */
  value: number | null;
  min: number | null;
  max: number | null;
  step: number;
  /** Einheit hinter der Zahl, bereits als Zeichen (`A`, `°C`). */
  unit: string;
  /** Nachkommastellen der Anzeige. Ein 0,5-Schritt braucht eine. */
  decimals?: number;
  /**
   * Benennt die Größe für die Sprachausgabe: „{name} erhöhen". Ohne diese
   * Angabe hieße jeder Stepper im Fahrzeug „Plus" (Kapitel 7 §31).
   */
  label: string;
  /**
   * Der Wert ist bekannt, aber nicht mehr bestätigt — veralteter Messwert
   * oder fehlende Verbindung. Er wird weiter gezeigt, aber gedämpft.
   *
   * Ohne Schriftzug: Der Stepper ist so breit wie seine beiden Tasten, und
   * ein Zusatz zwischen ihnen schöbe eine davon aus der Karte. Was gerade
   * gilt, sagt die Seite ringsum.
   */
  stale?: boolean;
  disabled?: boolean;
}

export function Stepper({
  entityId,
  value,
  min,
  max,
  step,
  unit,
  decimals = 0,
  label,
  stale = false,
  disabled,
}: StepperProps) {
  const { pending } = useAppState();
  const busy = pending.has(entityId);
  const known = value !== null;

  function change(delta: number) {
    if (!known) return;
    let next = round(value + delta);
    if (min !== null) next = Math.max(min, next);
    if (max !== null) next = Math.min(max, next);
    if (next === value) return;
    sendCommand(entityId, "set_value", { value: next });
  }

  /**
   * 20,5 + 0,5 ergibt in Gleitkomma nicht immer genau 21. Ohne Rundung
   * wanderten winzige Reste in den Befehl und von dort in die Steuerung —
   * ein Sollwert von 21,000000000000004 °C ist kein Sollwert, sondern ein
   * Rechenfehler auf Reisen.
   */
  function round(raw: number): number {
    const places = Math.max(decimals, decimalsOf(step));
    return Number(raw.toFixed(places));
  }

  const atMin = min !== null && known && value <= min;
  const atMax = max !== null && known && value >= max;

  return (
    <span className="stepper">
      <button
        type="button"
        className="stepper__btn"
        onClick={() => change(-step)}
        disabled={disabled || busy || !known || atMin}
        aria-label={t("stepper.decrease", undefined, { name: label })}
      >
        −
      </button>
      <span
        className={[
          "stepper__value",
          busy ? "stepper__value--pending" : "",
          stale && !busy ? "stepper__value--stale" : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        {known ? (
          <>
            <span className="numeric">{value.toFixed(decimals)}</span>
            <span className="stepper__unit">{unit}</span>
          </>
        ) : (
          <span className="stepper__unknown">{t("state.unknown")}</span>
        )}
      </span>
      <button
        type="button"
        className="stepper__btn"
        onClick={() => change(step)}
        disabled={disabled || busy || !known || atMax}
        aria-label={t("stepper.increase", undefined, { name: label })}
      >
        +
      </button>
    </span>
  );
}

/** Wie viele Nachkommastellen eine Schrittweite hat. */
function decimalsOf(step: number): number {
  const text = String(step);
  const dot = text.indexOf(".");
  return dot === -1 ? 0 : text.length - dot - 1;
}
