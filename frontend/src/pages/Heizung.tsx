/**
 * Heizung — eigenes System, eigener Bereich.
 *
 * Gemessen wird dieselbe Innentemperatur wie beim Klima: Es gibt nur einen
 * Wohnraum und nur einen Fühler. Der **Sollwert** dagegen ist ein anderer,
 * denn er gehört einem anderen Gerät. Beide auf denselben Wert zu legen wäre
 * die einfachere Oberfläche und die falsche Anlage (Kapitel 13 §35).
 *
 * Keine Außentemperatur: Für die Heizung erklärt sie nichts, was der Blick
 * aus dem Fenster nicht auch sagt — und eine Seite trägt nur, was sie
 * braucht (Kapitel 8 §1).
 */

import { Zone } from "./Zone";
import { t } from "../i18n/de";

export function Heizung() {
  return (
    <Zone
      title={t("heating.title")}
      actualId="climate.living.temperature"
      targetId="heating.target"
      stateId="heating.state"
      notes={[t("heating.noteSeparate"), t("heating.noteDevice")]}
    />
  );
}
