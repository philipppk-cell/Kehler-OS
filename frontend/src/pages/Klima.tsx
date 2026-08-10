/**
 * Klima — die Kühlung.
 *
 * BESTÄTIGT (2026-08-10): Klima und Heizung laufen beide über die Steuerung,
 * sind aber **getrennte Systeme**. Deshalb dieser eigene Bereich und nicht
 * ein gemeinsamer mit Umschalter: Ein Umschalter würde behaupten, dass sich
 * die beiden ausschließen — und das ist eine Aussage über die Anlage, die
 * Kehler OS nicht treffen darf (Kapitel 18 §98).
 *
 * Die Außentemperatur steht hier, weil sie die Kühlung erklärt: Ob 24 °C
 * innen viel oder wenig sind, hängt daran, was draußen ist.
 */

import { Zone } from "./Zone";
import { t } from "../i18n/de";

export function Klima() {
  return (
    <Zone
      title={t("climate.title")}
      actualId="climate.living.temperature"
      targetId="climate.cooling.target"
      stateId="climate.cooling.state"
      extra={[{ id: "climate.outside.temperature", label: t("climate.outside") }]}
      notes={[t("climate.noteSeparate"), t("climate.noteDevice")]}
    />
  );
}
