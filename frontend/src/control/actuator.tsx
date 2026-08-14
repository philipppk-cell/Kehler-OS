/**
 * Bedienung eines Aktors — an einer Stelle, für alle Seiten.
 *
 * Ventile, Schrankverriegelungen und die Heckklappe sind verschiedene Dinge,
 * verhalten sich in der Oberfläche aber gleich: Sie nehmen Befehle an und
 * melden **nichts** zurück (bestätigt 2026-08-12 für alle beweglichen Teile
 * des Fahrzeugs).
 *
 * Daraus folgt eine Regel, die überall gleich gelten muss und deshalb hier
 * steht statt dreimal nebeneinander:
 *
 * > **Ohne Rückmeldung wird keine Stellung behauptet.** Angezeigt wird der
 * > zuletzt gesendete Befehl, als Befehl beschriftet und mit Zeitpunkt
 * > (Kapitel 13 §4, Kapitel 18 §37).
 *
 * Die zweite Regel ist ebenso wichtig: **Welche Schaltflächen erscheinen,
 * entscheidet die Entity.** Die Heckklappe kennt nur `open` — sie wird von
 * Gasdruckdämpfern aufgedrückt und von Hand zugedrückt. Eine ausgegraute
 * Schaltfläche „Schließen" wäre die Behauptung, das ginge grundsätzlich schon
 * (Kapitel 12 §55).
 */

import { Status, type Tone } from "../design/primitives";
import { textOf, useAppState, useEntity } from "../realtime/hooks";
import { t } from "../i18n/de";
import type { EntityView } from "../realtime/types";

/** Zustände, in denen etwas tatsächlich fährt. */
export const FAEHRT: readonly string[] = ["OPENING", "CLOSING"];

export interface Aktor {
  entity: EntityView | undefined;
  name: string;
  /** `false` heißt: keine Hardwarezuordnung — dann gibt es keine Bedienung. */
  konfiguriert: boolean;
  /** Welche Befehle es wirklich gibt. */
  verben: Set<string>;
  /** Ob gerade ein Befehl läuft. */
  laeuft: boolean;
  /** Der anzuzeigende Zustand: gemeldet, sonst befohlen, sonst `null`. */
  zustand: string | null;
  /** Gesetzt, wenn `zustand` aus einem Befehl stammt und nicht aus Messung. */
  befohlenSeit: string | null;
  /** Ob eine Rückmeldung überhaupt zu erwarten ist. */
  meldetZurueck: boolean;
}

export function useAktor(entityId: string): Aktor {
  const entity = useEntity(entityId);
  const { pending, connection } = useAppState();
  const online = connection === "online";
  const definition = entity?.definition;

  const meldetZurueck = definition?.feedback !== false;
  const gemeldet = online ? textOf(entity) : null;

  // Der Wunschzustand wird nur dann als Zustand herangezogen, wenn keine
  // Rückmeldung zu erwarten ist. Bei einem Gerät mit Rückmeldung steht er
  // während der Ausführung und sagt „wird gerade getan" — daraus einen
  // Zustand zu machen hieße, den Befehl für die Wirkung zu halten.
  const befohlen = online && !meldetZurueck ? (entity?.requested ?? null) : null;

  return {
    entity,
    name: definition?.name_key ? t(definition.name_key) : entityId,
    konfiguriert: definition?.configured !== false,
    verben: new Set((definition?.capabilities ?? []).map((c) => c.verb)),
    laeuft: pending.has(entityId),
    zustand: gemeldet ?? ((befohlen?.value as string | undefined) ?? null),
    befohlenSeit: befohlen ? befohlen.since : null,
    meldetZurueck,
  };
}

/** Ob ein Verb vor der Ausführung eine Bestätigung verlangt. */
export function brauchtBestaetigung(
  entity: EntityView | undefined,
  verb: string,
): boolean {
  return (
    (entity?.definition?.capabilities ?? []).find((c) => c.verb === verb)
      ?.needs_confirmation ?? false
  );
}

/**
 * Die Zustandsanzeige eines Aktors.
 *
 * Drei Fälle, drei verschiedene Aussagen — und keine davon ist geraten:
 *
 * * **nicht konfiguriert** — die Funktion existiert, ihr fehlt die Zuordnung
 * * **befohlen** — es gibt keine Rückmeldung, das hier ist der letzte Befehl
 * * **gemeldet** — die Hardware sagt es selbst
 */
export function Stellung({
  aktor,
  offenTon = "warn",
}: {
  aktor: Aktor;
  /** Farbe für „offen". Beim Schrank ist offen normal, beim Ventil nicht. */
  offenTon?: Tone;
}) {
  if (!aktor.konfiguriert) {
    return <Status tone="unknown" label={t("state.notConfigured")} compact />;
  }

  if (aktor.zustand === null) {
    return <Status tone="unknown" label={t("state.unknown")} compact />;
  }

  const offen = aktor.zustand === "OPEN";
  const faehrt = FAEHRT.includes(aktor.zustand);

  if (aktor.befohlenSeit !== null) {
    return (
      <span className="stellung">
        <Status
          tone={offen ? offenTon : "neutral"}
          label={offen ? t("actuator.openCommanded") : t("actuator.closeCommanded")}
          compact
        />
        <span className="stellung__seit">{seit(aktor.befohlenSeit)}</span>
      </span>
    );
  }

  const ton: Tone =
    aktor.zustand === "BLOCKED" ? "error"
    : faehrt ? "accent"
    : offen ? offenTon
    : aktor.zustand === "STOPPED" ? "neutral"
    : "ok";

  return (
    <Status
      tone={ton}
      label={t(`state.${aktor.zustand.toLowerCase()}`, aktor.zustand)}
      compact
    />
  );
}

/**
 * Wie lange ein Befehl her ist.
 *
 * Unter einer Minute steht „gerade eben" statt „vor 0 min": Eine Null ist
 * hier keine Information, sondern eine Rundung, die wie eine aussieht.
 *
 * Ab einer Stunde die Uhrzeit statt der Dauer — „vor 3 Std" zwingt zum
 * Kopfrechnen.
 */
export function seit(iso: string): string {
  const zeitpunkt = new Date(iso);
  const minuten = Math.floor((Date.now() - zeitpunkt.getTime()) / 60000);

  if (!Number.isFinite(minuten) || minuten < 0) return "";
  if (minuten < 1) return t("time.justNow");
  if (minuten < 60) return t("time.minutesAgo", undefined, { n: String(minuten) });
  return t("time.at", undefined, {
    time: zeitpunkt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }),
  });
}
