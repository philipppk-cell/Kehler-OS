/**
 * Die Bausteine, aus denen jede Seite von Kehler OS besteht.
 *
 * Kapitel 7 §39/§40 verlangt, dass ein einmal definiertes Element überall
 * gleich aussieht. Deshalb gibt es diese Datei — und deshalb baut keine Seite
 * eigene Buttons oder Karten.
 */

import type { CSSProperties, PointerEventHandler, ReactNode } from "react";
import { Quality, type EntityView } from "../realtime/types";
import { useAppState } from "../realtime/hooks";
import { t } from "../i18n/de";
import "./primitives.css";

/* ── Karte ───────────────────────────────────────────────────────────────
   Gruppiert Zusammengehöriges. Bewusst sparsam einzusetzen: Eine Seite darf
   nicht aus unzähligen kleinen Kästen bestehen (Kapitel 7 §11).           */

export function Card({
  title,
  icon,
  action,
  children,
  emphasis = false,
  style,
}: {
  title?: string;
  icon?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  /** Hebt die Karte hervor, wenn ihr Inhalt gerade Aufmerksamkeit braucht
   *  (Kapitel 8 §10) — ohne das Layout zu verschieben (§11). */
  emphasis?: boolean;
  style?: CSSProperties;
}) {
  return (
    <section className={`card${emphasis ? " card--emphasis" : ""}`} style={style}>
      {(title || action) && (
        <header className="card__head">
          {icon && <span className="card__icon">{icon}</span>}
          {title && <h2 className="card__title">{title}</h2>}
          {action && <div className="card__action">{action}</div>}
        </header>
      )}
      <div className="card__body">{children}</div>
    </section>
  );
}

/* ── Statuspunkt ─────────────────────────────────────────────────────────
   Trägt immer auch Text. Der Status muss ohne Farbe verständlich bleiben
   (Kapitel 7 §23) — für Sonnenlicht, Nachtmodus und Farbfehlsichtigkeit.  */

export type Tone = "ok" | "warn" | "error" | "unknown" | "accent" | "neutral";

export function Status({
  tone,
  label,
  compact = false,
}: {
  tone: Tone;
  label: string;
  compact?: boolean;
}) {
  return (
    <span className={`status status--${tone}${compact ? " status--compact" : ""}`}>
      <span className="status__dot" aria-hidden="true" />
      <span className="status__label">{label}</span>
    </span>
  );
}

/* ── Wert ────────────────────────────────────────────────────────────────
   Die wichtigste Komponente des Designsystems.

   Sie ist der einzige Ort, an dem ein Messwert dargestellt wird. Dadurch
   kann keine Seite versehentlich einen unbekannten Zustand als Zahl
   ausgeben — die Regel „UNKNOWN wird nie zu 0“ (Kapitel 18 §38) ist hier
   einmal umgesetzt statt überall wiederholt.                              */

export function Value({
  entity,
  size = "metric",
  suffix,
  decimals = 0,
}: {
  entity: EntityView | undefined;
  size?: "metric" | "display" | "inline";
  suffix?: string;
  decimals?: number;
}) {
  const cls = `value value--${size}`;

  // Ohne Verbindung weiß die Oberfläche nicht mehr, ob ein Wert noch gilt.
  // Sie zeigt ihn weiterhin — aber sichtbar als veraltet. Alles andere wäre
  // eine Behauptung über den aktuellen Zustand (Kapitel 18 §37).
  const { connection } = useAppState();
  const disconnected = connection !== "online";

  if (!entity) {
    return <span className={`${cls} value--muted`}>{t("state.unavailable")}</span>;
  }

  // „Noch zu verifizieren" geht vor „nicht konfiguriert". Beides trifft auf
  // eine unbestätigte Funktion zu, aber nur das erste sagt, woran es liegt:
  // Nicht die Zuordnung fehlt, sondern die Gewissheit, dass es etwas
  // zuzuordnen gibt. Die Reihenfolge steht hier und nicht auf den Seiten,
  // damit Dashboard und Fachseite nicht Verschiedenes über dieselbe Entity
  // sagen.
  if (entity.definition?.unverified) {
    return (
      <span className={`${cls} value--muted`} title={t("state.unverifiedHint")}>
        {t("state.unverified")}
      </span>
    );
  }

  if (!entity.definition?.configured) {
    // Fehlende Hardware wird hochwertig dargestellt, nicht als Platzhalter
    // (Kapitel 18 §101).
    return <span className={`${cls} value--muted`}>{t("state.notConfigured")}</span>;
  }

  const { quality, value, unit } = entity.state;

  if (quality === Quality.Unknown) {
    return (
      <span className={`${cls} value--unknown`} title={t("state.unknownHint")}>
        —<span className="value__hint">{t("state.unknown")}</span>
      </span>
    );
  }

  if (quality === Quality.Invalid || quality === Quality.Error) {
    return (
      <span className={`${cls} value--error`}>
        —<span className="value__hint">{t("state.faulty")}</span>
      </span>
    );
  }

  const text =
    typeof value === "number" ? value.toFixed(decimals) : String(value ?? "—");
  const stale = quality === Quality.Stale || disconnected;

  return (
    <span className={`${cls}${stale ? " value--stale" : ""}`}>
      <span className="numeric">{text}</span>
      {(suffix ?? formatUnit(unit)) && (
        <span className="value__unit">{suffix ?? formatUnit(unit)}</span>
      )}
      {quality === Quality.Stale && (
        /* Ein veralteter Wert wird gezeigt, aber gekennzeichnet — er ist
           weder aktuell noch wertlos (Kapitel 13 §9).

           Ohne Verbindung ist ohnehin jeder Wert veraltet; dort bleibt es
           beim gedämpften Ton, und der Hinweis steht einmal im Banner statt
           hinter jeder Zahl. */
        <span className="value__hint">{t("state.stale")}</span>
      )}
    </span>
  );
}

/**
 * Der Einheitenschlüssel aus der Konfiguration als lesbares Zeichen.
 *
 * Exportiert, weil sonst jede Seite ihre eigene Zuordnung anlegt — und dann
 * steht an einer Stelle „°C" und an der nächsten „celsius". Genau das ist
 * passiert, bevor es hier stand.
 */
export function formatUnit(unit: string | null): string {
  if (!unit) return "";
  return { percent: "%", celsius: "°C", V: "V", A: "A", W: "W", l: "L" }[unit] ?? unit;
}

/* ── Balken ──────────────────────────────────────────────────────────────
   Für Füllstände. Bei unbekanntem Wert bleibt der Balken leer und wird
   schraffiert — er zeigt nicht „0 %“.                                     */

export function Bar({
  entity,
  tone = "accent",
}: {
  entity: EntityView | undefined;
  tone?: Tone;
}) {
  const quality = entity?.state.quality;
  const usable = quality === Quality.Valid || quality === Quality.Stale;
  const percent = usable && typeof entity?.state.value === "number"
    ? Math.max(0, Math.min(100, entity.state.value))
    : 0;

  return (
    <div className={`bar${usable ? "" : " bar--unknown"}`}>
      <div
        className={`bar__fill bar__fill--${tone}`}
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}

/* ── Schalter ────────────────────────────────────────────────────────────
   Der Schalter unterscheidet drei Dinge, die oft verwechselt werden:
   den bestätigten Zustand, den laufenden Befehl und den unbekannten
   Zustand. Kapitel 7 §15 und Kapitel 18 §37: Ein gesendeter Befehl ist
   kein erreichter Zustand.                                                */

export function Toggle({
  on,
  pending,
  unknown,
  disabled,
  onChange,
  label,
}: {
  on: boolean;
  pending?: boolean;
  unknown?: boolean;
  disabled?: boolean;
  onChange: (next: boolean) => void;
  label: string;
}) {
  const cls = [
    "toggle",
    on && !unknown ? "toggle--on" : "",
    pending ? "toggle--pending" : "",
    unknown ? "toggle--unknown" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      type="button"
      className={cls}
      role="switch"
      aria-checked={unknown ? "mixed" : on}
      aria-label={label}
      disabled={disabled || pending}
      onClick={() => onChange(!on)}
    >
      <span className="toggle__track">
        <span className="toggle__knob" />
      </span>
    </button>
  );
}

/* ── Schnellzugriff ──────────────────────────────────────────────────────
   Eine Aktion, groß genug für den Finger im fahrenden Fahrzeug.
   Komplexe Funktionen gehören auf die Fachseiten (Kapitel 8 §13).         */

export function QuickTile({
  icon,
  label,
  active,
  pending,
  disabled,
  onClick,
}: {
  icon: ReactNode;
  label: string;
  active?: boolean;
  pending?: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  const cls = [
    "quick",
    active ? "quick--active" : "",
    pending ? "quick--pending" : "",
    disabled ? "quick--disabled" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button type="button" className={cls} onClick={onClick} disabled={disabled || pending}>
      <span className="quick__icon">{icon}</span>
      <span className="quick__label">{label}</span>
    </button>
  );
}

/* ── Segmentierte Auswahl ────────────────────────────────────────────────
   Wenige, gleichrangige Möglichkeiten, von denen genau eine gilt: Filter,
   Zeiträume, Messgrößen. Ein Aufklappmenü wäre hier falsch — es versteckt
   die Alternativen hinter einem Klick und braucht im fahrenden Fahrzeug
   zwei Berührungen statt einer (Kapitel 8 §13).

   Steht im Designsystem, weil Diagnose und Historie dieselbe Bedienung
   brauchen. Zwei Kopien sähen genau so lange gleich aus, bis eine geändert
   wird (Kapitel 7 §39/§40).                                                */

export function Segmented<T extends string | number>({
  options,
  value,
  onChange,
  label,
}: {
  options: readonly { value: T; label: string }[];
  value: T;
  onChange: (next: T) => void;
  label: string;
}) {
  return (
    <div className="segmented" role="group" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          className={`segmented__option${
            option.value === value ? " segmented__option--active" : ""
          }`}
          aria-pressed={option.value === value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

/* ── Weitere Bausteine ───────────────────────────────────────────────────  */

export function Row({
  icon,
  label,
  children,
}: {
  icon?: ReactNode;
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="row">
      {icon && <span className="row__icon">{icon}</span>}
      <span className="row__label">{label}</span>
      <span className="row__value">{children}</span>
    </div>
  );
}

export function Button({
  children,
  onClick,
  onPointerDown,
  onPointerUp,
  onPointerCancel,
  onLostPointerCapture,
  variant = "default",
  disabled,
  full,
}: {
  children: ReactNode;
  onClick?: () => void;
  onPointerDown?: PointerEventHandler<HTMLButtonElement>;
  onPointerUp?: PointerEventHandler<HTMLButtonElement>;
  onPointerCancel?: PointerEventHandler<HTMLButtonElement>;
  onLostPointerCapture?: PointerEventHandler<HTMLButtonElement>;
  variant?: "default" | "accent" | "quiet";
  disabled?: boolean;
  full?: boolean;
}) {
  return (
    <button
      type="button"
      className={`btn btn--${variant}${full ? " btn--full" : ""}`}
      onClick={onClick}
      onPointerDown={onPointerDown}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerCancel}
      onLostPointerCapture={onLostPointerCapture}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

/* ── Veraltet ────────────────────────────────────────────────────────────
   Ein einzelner Wert, der noch gilt, aber nicht mehr bestätigt ist.

   Bewusst Text und nicht nur eine blassere Farbe: Der Zustand muss ohne
   Farbe erkennbar bleiben (Kapitel 7 §23) — bei Sonnenlicht, im Nachtmodus
   und bei Farbfehlsichtigkeit.

   Sie gehört an Werte mit der Qualität `STALE` — also an den einen Fühler,
   der verstummt ist, während der Rest weiterläuft. **Nicht** an jeden Wert
   einer getrennten Verbindung: Dort ist ohnehin alles veraltet, das Banner
   sagt es einmal für die ganze Seite, und ein Schriftzug hinter jeder Zahl
   wäre Lärm statt Information.                                            */

export function StaleMark() {
  return <span className="stalemark">{t("state.stale")}</span>;
}

/** Kennzeichnet fehlende Hardware ruhig und hochwertig — nie als „TODO“. */
export function NotConfigured({ hint }: { hint?: string }) {
  return (
    <div className="notconfigured">
      <span className="notconfigured__label">{t("state.notConfigured")}</span>
      {hint && <span className="notconfigured__hint">{hint}</span>}
    </div>
  );
}
