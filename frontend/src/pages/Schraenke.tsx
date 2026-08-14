/**
 * Schränke — die Zentralverriegelung.
 *
 * Drei Gruppen, jede auf und zu. Mehr kann die Anlage nicht, und mehr zeigt
 * diese Seite deshalb auch nicht.
 *
 * **Die Gruppen heißen „Schrankgruppe 1/2/3", weil sie so heißen.** Es gibt
 * keine Angabe darüber, welche Schränke zu welcher Gruppe gehören. „Küche"
 * oder „Bad" hinzuzuerfinden wäre bequemer zu lesen und im Zweifel falsch —
 * und falsch an einer Stelle, an der jemand vor der Abfahrt prüft, ob alles
 * zu ist (Kapitel 7 §31, Kapitel 18 §97).
 *
 * **Es gibt keine Sammelschaltfläche „alle verriegeln".** Sie würde einen
 * Zustand suggerieren, den das System nicht kennt: Ohne Rückmeldung weiß
 * Kehler OS nicht, ob eine Gruppe verriegelt ist — es weiß nur, was zuletzt
 * befohlen wurde. „Alle zu" wäre dann eine Behauptung über drei Gruppen
 * gleichzeitig (Kapitel 18 §37).
 */

import { Button, Card } from "../design/primitives";
import { IconCabinet } from "../design/icons";
import { Stellung, brauchtBestaetigung, useAktor } from "../control/actuator";
import { sendCommand } from "../api/client";
import { useAppState } from "../realtime/hooks";
import { t } from "../i18n/de";
import "./schraenke.css";

const GRUPPEN = [
  "vehicle.cabinet.group1",
  "vehicle.cabinet.group2",
  "vehicle.cabinet.group3",
];

export function Schraenke() {
  const { connection } = useAppState();
  const online = connection === "online";

  return (
    <div className="schraenke">
      <div className="schraenke__main">
        <Card title={t("cabinet.title")}>
          {GRUPPEN.map((id) => (
            <GruppenZeile key={id} entityId={id} online={online} />
          ))}
        </Card>
      </div>

      <aside className="schraenke__side">
        <Card title={t("cabinet.notesTitle")}>
          <ul className="schraenke__notes">
            <li>{t("cabinet.notePurpose")}</li>
            <li>{t("cabinet.noteNoFeedback")}</li>
            <li>{t("cabinet.noteNoAuto")}</li>
          </ul>
        </Card>
      </aside>
    </div>
  );
}

function GruppenZeile({ entityId, online }: { entityId: string; online: boolean }) {
  const aktor = useAktor(entityId);

  function schalten(verb: string) {
    if (
      brauchtBestaetigung(aktor.entity, verb) &&
      !window.confirm(t("cabinet.confirm", undefined, { name: aktor.name }))
    ) {
      return;
    }
    sendCommand(entityId, verb);
  }

  return (
    <div className="schrank">
      <span className="schrank__icon">
        <IconCabinet size={20} />
      </span>
      <span className="schrank__name">{aktor.name}</span>

      <span className="schrank__state">
        {/* Ein offener Schrank ist im Stand der Normalfall und wird nicht
            als Warnung eingefärbt. Erst bei Fahrtbeginn wäre er eine — und
            den Fahrtbeginn kennt Kehler OS nicht (Punkt J1). */}
        <Stellung aktor={aktor} offenTon="neutral" />
      </span>

      <span className="schrank__controls">
        {aktor.konfiguriert && (
          <>
            {aktor.verben.has("open") && (
              <Button disabled={!online || aktor.laeuft} onClick={() => schalten("open")}>
                {t("cabinet.unlock")}
              </Button>
            )}
            {aktor.verben.has("close") && (
              <Button
                disabled={!online || aktor.laeuft}
                onClick={() => schalten("close")}
              >
                {t("cabinet.lock")}
              </Button>
            )}
          </>
        )}
      </span>
    </div>
  );
}
