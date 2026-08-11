/**
 * Der Startbildschirm.
 *
 * Der Umriss des Fahrzeugs zeichnet sich in einem Zug, dann kommen die Räder,
 * dann der Schriftzug, dann die Linie, dann die Statuszeile (Entwurf 03,
 * gewählt am 2026-08-10).
 *
 * ── Wann er verschwindet ──────────────────────────────────────────────────
 *
 * Erst wenn **beides** zutrifft: Der Ablauf ist durch **und** der erste
 * Zustand ist da. Die zweite Bedingung ist die wichtige — sie ist der Grund,
 * warum es diesen Bildschirm überhaupt geben darf: Solange das System noch
 * nichts weiß, ist eine leere Oberfläche mit Strichen an allen Werten die
 * schlechtere Auskunft.
 *
 * Die erste Bedingung kostet dagegen Zeit, und das wird hier nicht
 * beschönigt: **Bis zu 3,35 Sekunden**, einmal beim Öffnen. Kommt der Zustand
 * früher, war das Warten künstlich. Ein Ablauf, der auf halber Strecke
 * abgeschnitten wird, sieht allerdings kaputt aus — und ein Startbildschirm,
 * der kaputt aussieht, ist schlimmer. Die Dauer ist eine Entscheidung des
 * Fahrzeughalters — er hat den Ablauf am 2026-08-11 ausdrücklich langsamer
 * gewünscht.
 *
 * ── Wann er sich zurückzieht ──────────────────────────────────────────────
 *
 * **Sobald die Verbindung scheitert, sofort.** Dann steht dahinter das Banner
 * „Keine Verbindung zum Fahrzeug", und das muss man sehen. Ein Startbildschirm,
 * der über einem Problem stehen bleibt, verschweigt es (Kapitel 8 §26).
 */

import { useEffect, useState } from "react";
import { useAppState } from "../realtime/hooks";
import { t } from "../i18n/de";
import "./boot.css";

/** Dauer des Ablaufs bis einschließlich Statuszeile.
 *
 * Muss zu den Zeiten in `boot.css` passen — dort steht die Aufteilung. */
const ABLAUF_MS = 3350;

/** Dauer des Ausblendens — muss zu `.boot--weg` in `boot.css` passen. */
const AUSBLENDEN_MS = 420;

export function BootScreen() {
  const { entities, connection } = useAppState();
  const [abgelaufen, setAbgelaufen] = useState(reduzierteBewegung());
  const [entfernt, setEntfernt] = useState(false);

  useEffect(() => {
    if (reduzierteBewegung()) return;
    const uhr = window.setTimeout(() => setAbgelaufen(true), ABLAUF_MS);
    return () => window.clearTimeout(uhr);
  }, []);

  // Ein Zustand ist da, sobald der erste Schnappschuss eingetroffen ist.
  const bereit = entities.size > 0;
  const gescheitert = connection === "offline";
  const fertig = gescheitert || (abgelaufen && bereit);

  useEffect(() => {
    if (!fertig) return;
    const uhr = window.setTimeout(() => setEntfernt(true), AUSBLENDEN_MS);
    return () => window.clearTimeout(uhr);
  }, [fertig]);

  if (entfernt) return null;

  return (
    <div
      className={`boot${fertig ? " boot--weg" : ""}`}
      role="status"
      aria-live="polite"
      aria-label={t("boot.starting")}
    >
      <div className="boot__buehne">
        {/* Ein geschlossener Umriss, in einem Zug gezeichnet: Front hoch,
            Scheibe, Kabinendach, Stirnseite des Aufbaus, Dach, Heck, Unterkante
            zurück.

            Vorher waren es drei Teile plus eine graue Bodenlinie. Die
            Bodenlinie war nicht bloß Zierde — sie schloss Kabine und Aufbau
            unten ab, die beide als offene Formen gezeichnet waren. Sie
            ersatzlos zu streichen hätte ein unten offenes Fahrzeug ergeben.
            Jetzt gehört die Unterkante zum Fahrzeug und hat dessen Farbe.

            `pathLength="1"` normiert die Länge: Der Ablauf rechnet mit 0 bis 1
            und nicht mit der tatsächlichen Pfadlänge. Ohne das müsste die
            Strichlänge zur Geometrie passen, und jede Änderung am Umriss
            verschöbe stillschweigend die Dauer. */}
        <svg className="boot__lkw" viewBox="0 0 220 84" aria-hidden="true">
          <path
            className="boot__strich boot__umriss"
            pathLength="1"
            d="M18 62V40l10-12h28V16h144v46z"
          />
          <circle className="boot__strich boot__rad" pathLength="1" cx="42" cy="69" r="7" />
          <circle
            className="boot__strich boot__rad boot__rad--2"
            pathLength="1"
            cx="152"
            cy="69"
            r="7"
          />
          <circle
            className="boot__strich boot__rad boot__rad--3"
            pathLength="1"
            cx="178"
            cy="69"
            r="7"
          />
        </svg>

        {/* Dieselbe Auszeichnung wie im Kopfbereich der Oberfläche: gesperrt,
            halbfett, „OS" im Akzent. Der Start soll aussehen wie der Anfang
            derselben Sache und nicht wie ein Vorspann davor. */}
        <div className="boot__marke">
          KEHLER <b>OS</b>
        </div>

        <div className="boot__linie" />

        <div className="boot__zeile">{t("boot.starting")}</div>
      </div>
    </div>
  );
}

/**
 * Ob das Betriebssystem weniger Bewegung verlangt.
 *
 * Dann gibt es keinen Ablauf: Das Zeichen steht sofort fertig da, und der
 * Startbildschirm verschwindet, sobald der Zustand eintrifft — ohne jede
 * künstliche Wartezeit.
 */
function reduzierteBewegung(): boolean {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
}
