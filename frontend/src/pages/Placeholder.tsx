/**
 * Platzhalter für Bereiche, die noch entstehen.
 *
 * Bewusst hochwertig gestaltet statt als „TODO“ (Kapitel 18 §101): Ein
 * unfertiger Bereich soll ruhig aussehen, nicht wie ein Baustellenschild.
 */

import { t } from "../i18n/de";
import "./placeholder.css";

export function Placeholder({ title }: { title: string }) {
  return (
    <div className="placeholder">
      <h1 className="placeholder__title">{title}</h1>
      <p className="placeholder__text">{t("page.comingSoon")}</p>
    </div>
  );
}
