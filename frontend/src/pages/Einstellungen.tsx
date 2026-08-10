/**
 * Einstellungen.
 *
 * ── Warum diese Seite kurz ist ────────────────────────────────────────────
 *
 * Kapitel 6 §13 nennt als Beispiele Sprache, Einheiten, Displayhelligkeit,
 * Theme, Zeitformat, Benachrichtigungen, Netzwerk, Automatisierungen und
 * Energieeinstellungen. Von diesen neun hat heute genau eine eine echte
 * Wirkung.
 *
 * Die anderen acht als Schalter anzubieten wäre die bequeme Lösung und die
 * falsche. Ein Regler für die Displayhelligkeit, den der Browser gar nicht
 * erreicht; eine Sprachauswahl mit einem einzigen Eintrag; ein
 * Netzwerkbereich, hinter dem keine Netzwerkverwaltung steht — jedes davon
 * verspricht etwas, das Kehler OS nicht einlöst. Dieselbe Regel wie überall
 * sonst: **kein Bedienelement ohne Wirkung** (Kapitel 18 §98/§101).
 *
 * Sie werden deshalb nicht verschwiegen, sondern benannt — unten, jeweils mit
 * dem Grund. Eine leere Stelle, die erklärt wird, ist etwas anderes als eine
 * vergessene.
 *
 * ── Zwei Arten von Einstellung ────────────────────────────────────────────
 *
 * Oben stehen die **Anzeigeeinstellungen dieses Geräts** — sie wirken sofort,
 * betreffen nur die Darstellung und liegen im Speicher dieses Tablets.
 *
 * Darunter steht die **Fahrzeugkonfiguration**, ausdrücklich nur lesend.
 * Kapitel 6 §14 trennt beides, und die Trennung ist keine Förmlichkeit: Die
 * Tankgröße ist keine Vorliebe. Sie steht in `config/vehicle/` und wird beim
 * Start gelesen (Kapitel 17 §48). Ein Eingabefeld dafür wäre eine Zusage, die
 * dieses System nicht einlöst — es gibt keine Einstellungspersistenz.
 */

import { useEffect, useMemo, useState } from "react";
import { useSyncExternalStore } from "react";
import { Button, Card, Row, Status, Toggle, formatUnit } from "../design/primitives";
import { useAppState } from "../realtime/hooks";
import type { EntityView } from "../realtime/types";
import { preferences } from "../settings/preferences";
import { useWakeLock, wakeLockSupport } from "../settings/useWakeLock";
import { t } from "../i18n/de";
import "./einstellungen.css";

interface Area {
  id: string;
  name_key: string;
}

interface Vehicle {
  name: string | null;
  areas: Area[];
}

export function Einstellungen() {
  const { entities } = useAppState();
  const prefs = useSyncExternalStore(preferences.subscribe, preferences.getSnapshot);
  const awake = useWakeLock(prefs.keepAwake);
  const support = useMemo(wakeLockSupport, []);
  const vehicle = useVehicle();

  const all = useMemo(() => [...entities.values()], [entities]);

  return (
    <div className="settings">
      <Card title={t("settings.display")}>
        <p className="settings__note">{t("settings.displayScope")}</p>

        <Row label={t("settings.night")}>
          <Toggle
            on={prefs.night}
            label={t("settings.night")}
            onChange={(next) => preferences.set("night", next)}
          />
        </Row>
        <p className="settings__hint">{t("settings.nightHint")}</p>

        {support === "available" ? (
          <>
            <Row label={t("settings.keepAwake")}>
              {/* Der Schalter zeigt den Wunsch, die Statusanzeige daneben den
                  tatsächlichen Zustand. Das Betriebssystem kann die Sperre
                  ablehnen oder wieder einziehen; „ein" zu zeigen, während das
                  Display ausgeht, wäre eine Behauptung (Kapitel 18 §37). */}
              <span className="settings__pair">
                <Status
                  tone={awake === "held" ? "ok" : awake === "denied" ? "warn" : "neutral"}
                  label={t(`settings.awake.${awake}`)}
                  compact
                />
                <Toggle
                  on={prefs.keepAwake}
                  label={t("settings.keepAwake")}
                  onChange={(next) => preferences.set("keepAwake", next)}
                />
              </span>
            </Row>
            <p className="settings__hint">{t("settings.keepAwakeHint")}</p>
          </>
        ) : (
          <Row label={t("settings.keepAwake")}>
            <Status tone="unknown" label={t(`settings.awake.${support}`)} compact />
          </Row>
        )}

        <div className="settings__actions">
          <Button variant="quiet" onClick={() => preferences.reset()}>
            {t("settings.reset")}
          </Button>
        </div>
      </Card>

      <Card title={t("settings.vehicle")}>
        <p className="settings__note">{t("settings.vehicleScope")}</p>

        <Row label={t("settings.vehicleName")}>
          <span className="settings__value">{vehicle?.name ?? "—"}</span>
        </Row>
        <Row label={t("settings.areas")}>
          <span className="settings__value">
            {vehicle === null
              ? "—"
              : vehicle.areas.map((area) => t(area.name_key, area.id)).join(" · ")}
          </span>
        </Row>

        <ConfiguredValues entities={all} />
      </Card>

      <Card title={t("settings.missingTitle")}>
        <p className="settings__note">{t("settings.missingIntro")}</p>
        <dl className="missing">
          <Missing what={t("settings.miss.language")} why={t("settings.miss.languageWhy")} />
          <Missing what={t("settings.miss.units")} why={t("settings.miss.unitsWhy")} />
          <Missing
            what={t("settings.miss.brightness")}
            why={t("settings.miss.brightnessWhy")}
          />
          <Missing what={t("settings.miss.theme")} why={t("settings.miss.themeWhy")} />
          <Missing what={t("settings.miss.time")} why={t("settings.miss.timeWhy")} />
          <Missing what={t("settings.miss.notify")} why={t("settings.miss.notifyWhy")} />
          <Missing what={t("settings.miss.network")} why={t("settings.miss.networkWhy")} />
          <Missing what={t("settings.miss.automation")} why={t("settings.miss.automationWhy")} />
          <Missing what={t("settings.miss.users")} why={t("settings.miss.usersWhy")} />
        </dl>
      </Card>
    </div>
  );
}

/* ── Die konfigurierten Werte ────────────────────────────────────────────── */

/**
 * Was in der Fahrzeugbeschreibung an Zahlen steht.
 *
 * Bewusst keine Wiederholung der Diagnose: Dort geht es darum, ob ein Wert
 * *ankommt*. Hier geht es darum, was *hinterlegt* ist — Kapazitäten,
 * Schwellen, Grenzen. Beim Anschließen ist das die Gegenprobe: Der Tank meldet
 * 60 %, aber sind auch 550 Liter hinterlegt?
 *
 * Nur Entities mit solchen Angaben erscheinen. Eine Zeile „keine Kapazität"
 * für jeden Schalter wäre Lärm.
 */
function ConfiguredValues({ entities }: { entities: EntityView[] }) {
  const rows = entities
    .map((entity) => ({ entity, facts: factsOf(entity) }))
    .filter((row) => row.facts.length > 0)
    .sort((a, b) => a.entity.entity_id.localeCompare(b.entity.entity_id));

  if (rows.length === 0) return null;

  return (
    <div className="confvals">
      <div className="label">{t("settings.configuredValues")}</div>
      {rows.map(({ entity, facts }) => (
        <div key={entity.entity_id} className="confval">
          <span className="confval__name">
            {entity.definition?.name_key
              ? t(entity.definition.name_key, entity.entity_id)
              : entity.entity_id}
            {/* Ein hinterlegter Wert ist keine verfügbare Funktion. Bei der
                Heizung stehen 1 bis 3 kW in der Beschreibung, ohne dass
                bestätigt wäre, dass sich die Stufen überhaupt schalten
                lassen — ohne diesen Hinweis läse sich die Zeile wie eine
                Zusage. */}
            {entity.definition?.unverified ? (
              <span className="tag tag--open">{t("state.unverified")}</span>
            ) : entity.definition?.configured === false ? (
              <span className="tag tag--open">{t("state.notConfigured")}</span>
            ) : null}
          </span>
          <span className="confval__facts">
            {facts.map((fact) => (
              <span key={fact} className="confval__fact numeric">
                {fact}
              </span>
            ))}
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * Die hinterlegten Zahlen einer Entity, als lesbare Angaben.
 *
 * `null` heißt hier durchgehend „nicht hinterlegt" und führt dazu, dass die
 * Angabe fehlt — nicht dazu, dass eine 0 erscheint (Kapitel 18 §38).
 */
function factsOf(entity: EntityView): string[] {
  const definition = entity.definition;
  if (!definition) return [];

  const facts: string[] = [];

  if (definition.capacity_l !== null) {
    facts.push(t("settings.capacityL", undefined, { value: String(definition.capacity_l) }));
  }
  if (definition.capacity_ah !== null) {
    facts.push(t("settings.capacityAh", undefined, { value: String(definition.capacity_ah) }));
  }
  if (definition.nominal_voltage !== null) {
    facts.push(t("settings.nominalV", undefined, { value: String(definition.nominal_voltage) }));
  }
  if (definition.min_value !== null && definition.max_value !== null) {
    facts.push(
      t("settings.range", undefined, {
        min: String(definition.min_value),
        max: String(definition.max_value),
        unit: formatUnit(definition.unit),
      }),
    );
  }
  for (const [key, value] of [
    ["settings.warnBelow", definition.warn_below],
    ["settings.warnAbove", definition.warn_above],
    ["settings.criticalBelow", definition.critical_below],
    ["settings.criticalAbove", definition.critical_above],
  ] as const) {
    if (value !== null) facts.push(t(key, undefined, { value: String(value) }));
  }

  return facts;
}

/* ── Was fehlt ───────────────────────────────────────────────────────────── */

function Missing({ what, why }: { what: string; why: string }) {
  return (
    <div className="missing__item">
      <dt className="missing__what">{what}</dt>
      <dd className="missing__why">{why}</dd>
    </div>
  );
}

/* ── Fahrzeugbeschreibung ────────────────────────────────────────────────── */

/**
 * Die Fahrzeugbeschreibung, einmal geholt.
 *
 * Sie wird beim Start des Backends aus der Konfiguration gelesen und ändert
 * sich zur Laufzeit nicht — zyklisch danach zu fragen würde eine
 * Veränderlichkeit unterstellen, die es nicht gibt.
 *
 * Solange sie nicht geladen ist, steht in der Oberfläche nichts. Der Name des
 * Fahrzeugs wird nicht geraten (Kapitel 18 §98).
 */
function useVehicle(): Vehicle | null {
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);

  useEffect(() => {
    let active = true;
    fetch("/api/v1/vehicle")
      .then((response) => (response.ok ? response.json() : null))
      .then((data: Vehicle | null) => {
        if (active && data) setVehicle(data);
      })
      .catch(() => undefined);
    return () => {
      active = false;
    };
  }, []);

  return vehicle;
}
