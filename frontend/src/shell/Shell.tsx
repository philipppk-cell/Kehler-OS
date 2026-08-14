/**
 * Der Rahmen, den jede Seite teilt.
 *
 * Kopfbereich, linke Navigation, Inhalt. Die untere Leiste aus der
 * Designreferenz ist bewusst nicht enthalten: Ihre Verwendung ist noch nicht
 * entschieden, und sie darf nicht als Hauptnavigation behandelt werden
 * (Kapitel 8 §29, Kapitel 18 §21). Der Aufbau lässt sie später ohne Umbau zu.
 */

import type { ReactNode } from "react";
import { useAppState } from "../realtime/hooks";
import { t } from "../i18n/de";
import { Status } from "../design/primitives";
import {
  IconCabinet,
  IconCooling,
  IconDashboard,
  IconDiagnostics,
  IconEnergy,
  IconHeating,
  IconLeveling,
  IconSettings,
  IconVehicle,
  IconWater,
  IconWifi,
} from "../design/icons";
import "./shell.css";

export type PageId =
  | "dashboard" | "energy" | "water" | "climate" | "heating"
  | "leveling" | "vehicle" | "cabinets" | "settings" | "diagnostics";

/* Klima und Heizung stehen als zwei Einträge nebeneinander, weil es zwei
   Systeme sind (BESTÄTIGT 2026-08-10). Ein Eintrag mit zwei Unterseiten
   würde sie als ein System darstellen.

   „Garage" stand hier ebenfalls und ist entfallen. Der Bereich enthielt genau
   eine Entity — das Garagentor —, und die steht mit allen Fahrbefehlen auf
   der Fahrzeugseite. Ein eigener Reiter dafür hätte einen Bereich behauptet,
   wo eine Zeile ist.

   „Kameras" ebenso, und aus dem klarsten aller Gründe: **Das Fahrzeug hat
   keine** (BESTÄTIGT 2026-08-12). Der Reiter führte auf eine Platzhalterseite
   — ein Eintrag in der Hauptnavigation, der ein ganzes Themengebiet
   ankündigte und dahinter nichts hatte. Was nicht angebunden ist, erscheint
   nicht (Kapitel 12 §55, Kapitel 13 §60, Kapitel 18 §33). */
const NAV: { id: PageId; icon: ReactNode }[] = [
  { id: "dashboard", icon: <IconDashboard /> },
  { id: "energy", icon: <IconEnergy /> },
  { id: "water", icon: <IconWater /> },
  { id: "climate", icon: <IconCooling /> },
  { id: "heating", icon: <IconHeating /> },
  { id: "leveling", icon: <IconLeveling /> },
  { id: "vehicle", icon: <IconVehicle /> },
  { id: "cabinets", icon: <IconCabinet /> },
  { id: "settings", icon: <IconSettings /> },
  { id: "diagnostics", icon: <IconDiagnostics /> },
];

export function Shell({
  page,
  onNavigate,
  children,
}: {
  page: PageId;
  onNavigate: (page: PageId) => void;
  children: ReactNode;
}) {
  const { connection, system } = useAppState();

  return (
    <div className="shell">
      <Header />

      {/* Ohne Verbindung sind die angezeigten Werte nicht mehr belastbar.
          Das wird gesagt, statt es zu verschweigen (Kapitel 8 §26). */}
      {connection !== "online" && (
        <div className={`banner banner--${connection === "offline" ? "error" : "warn"}`}>
          <strong>{t(`conn.${connection === "connecting" ? "connecting" : connection}`)}</strong>
          {connection === "offline" && <span>{t("conn.offlineHint")}</span>}
        </div>
      )}

      {/* Simulation ist dauerhaft sichtbar, nie beiläufig (Kapitel 18 §66). */}
      {system?.simulated && (
        <div className="banner banner--sim">
          <strong>{t("env.simulation")}</strong>
          <span>{t("env.simulationHint")}</span>
        </div>
      )}

      <div className="shell__main">
        <nav className="sidebar" aria-label="Hauptnavigation">
          <ul className="sidebar__list">
            {NAV.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={`navitem${page === item.id ? " navitem--active" : ""}`}
                  onClick={() => onNavigate(item.id)}
                  aria-current={page === item.id ? "page" : undefined}
                >
                  <span className="navitem__icon">{item.icon}</span>
                  <span className="navitem__label">{t(`nav.${item.id}`)}</span>
                </button>
              </li>
            ))}
          </ul>

          <SystemStatus />
        </nav>

        <main className="content">{children}</main>
      </div>
    </div>
  );
}

function Header() {
  const { connection } = useAppState();
  const now = new Date();
  return (
    <header className="header">
      <div className="header__time">
        <div className="header__clock numeric">
          {now.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}
        </div>
        <div className="header__date">
          {now.toLocaleDateString("de-DE", {
            weekday: "long", day: "numeric", month: "long", year: "numeric",
          })}
        </div>
      </div>

      <div className="header__brand">
        KEHLER <span className="header__brand-os">OS</span>
      </div>

      {/* Hier stand ein Benutzersymbol. Es ist entfallen: Es gibt keine
          Benutzer (Beschluss W14), und ein Symbol, das ein Konto andeutet,
          hinter dem keines liegt, ist ein Versprechen.

          Das Netzsymbol blieb — aber es zeigt jetzt den tatsächlichen
          Verbindungszustand, statt unverändert dazustehen. Ein Symbol, das
          wie eine Statusanzeige aussieht und keine ist, wäre Dekoration an
          genau der Stelle, an der Kapitel 7 §5 sie verbietet. */}
      <div className="header__right">
        <span
          className={`header__net header__net--${connection}`}
          title={t(`conn.${connection}`, connection)}
        >
          <IconWifi size={18} />
        </span>
      </div>
    </header>
  );
}

function SystemStatus() {
  const { system, connection } = useAppState();

  // Ohne Verbindung wird kein Gesundheitszustand behauptet.
  if (connection === "offline" || !system) {
    return (
      <div className="sysstatus">
        <div className="label">{t("dash.systemStatus")}</div>
        <Status tone="unknown" label={t("state.unknown")} />
      </div>
    );
  }

  const tone =
    system.health === "HEALTHY" ? "ok"
    : system.health === "CRITICAL" ? "error"
    : system.health === "INITIALIZING" ? "unknown"
    : "warn";

  return (
    <div className="sysstatus">
      <div className="label">{t("dash.systemStatus")}</div>
      <Status tone={tone} label={t(`health.${system.health}`)} />
    </div>
  );
}
