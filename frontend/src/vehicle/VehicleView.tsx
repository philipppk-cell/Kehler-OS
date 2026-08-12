/**
 * Die Fahrzeugdarstellung.
 *
 * Eine technische Seitenansicht statt einer Illustration: Sie soll Zustände
 * zeigen, nicht schmücken (Kapitel 18 §34).
 *
 * **Sie ist reine Ausgabe.** Man kann nicht auf das Fahrzeug tippen, um etwas
 * zu bewegen — gesteuert wird über die Schnellzugriffe und die Fachseiten
 * (Kapitel 8 §6).
 *
 * **Animationen entstehen aus echten Zuständen** (Kapitel 18 §105). Ist ein
 * Zustand unbekannt, wird keine Bewegung vorgetäuscht: Das Teil erscheint
 * gestrichelt statt in einer erfundenen Position (§106).
 *
 * Die Datei ist als Ganzes austauschbar — Zustände hinein, Darstellung
 * heraus (Kapitel 18 §104).
 *
 * ── Koordinatenplan ──────────────────────────────────────────────────────
 * Blickrichtung nach rechts, Fahrerhaus rechts, Aufbau links.
 *
 *   Boden           y = 252
 *   Radmitte        y = 226,  r = 27
 *   Aufbau          x 132…512,  y  56…208
 *   Fahrerhaus      x 512…664,  y 100…208
 *   Achsen          hinten x 214 / 288,  vorn x 600
 *   Garage          x 146…248  (hinten unten)
 *   Eingangstür     x 266…310  (über der ersten Tandemachse)
 *   Terrasse        x 169…333  (über dem Tandem, eingefahren unsichtbar)
 */

import "./vehicle.css";

/**
 * Wie ein bewegliches Teil dargestellt wird.
 *
 * `absent` ist etwas anderes als `unknown`: Ein unbekannter Zustand gehört zu
 * vorhandener Hardware, deren Lage das System gerade nicht kennt — er wird
 * gestrichelt gezeigt. `absent` heißt, dass die Funktion diesem Fahrzeug noch
 * gar nicht zugeordnet ist. Sie wird dann nicht gezeichnet, denn ein Umriss
 * am Fahrzeug wäre die Behauptung, das Teil sei verbaut (Kapitel 18 §101).
 */
export type Part = "closed" | "open" | "moving" | "unknown" | "absent";

export interface VehicleState {
  garage: Part;
  door: Part;
  terrace: Part;
}

const GROUND = 252;
const AXLE_Y = 226;
const AXLE_R = 27;
const AXLES = [214, 288, 600];

export function VehicleView({ state }: { state: VehicleState }) {
  return (
    <svg
      className="vehicle"
      viewBox="0 0 960 300"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Fahrzeugansicht mit Zustand der Aufbaufunktionen"
    >
      <defs>
        <linearGradient id="kv-body" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(255,255,255,0.10)" />
          <stop offset="100%" stopColor="rgba(255,255,255,0.015)" />
        </linearGradient>
        <linearGradient id="kv-ground" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="rgba(56,214,238,0)" />
          <stop offset="50%" stopColor="rgba(56,214,238,0.28)" />
          <stop offset="100%" stopColor="rgba(56,214,238,0)" />
        </linearGradient>

        {/* Das Garagentor fährt in den Aufbau. Ohne diesen Beschnitt läge es
            beim Öffnen sichtbar über dem Fenster darüber. */}
        <clipPath id="kv-garage-opening">
          <rect x="146" y="142" width="102" height="64" rx="3" />
        </clipPath>
      </defs>

      <g transform="translate(200 0)">
      <rect x="90" y={GROUND} width="600" height="1" fill="url(#kv-ground)" />

      {/* Markisenkassette. Sie ist am Fahrzeug verschraubt und deshalb Teil
          des Aufbaus, kein Zustand. Das ausgefahrene Tuch wird auf Wunsch des
          Fahrzeughalters nicht dargestellt — in beiden Ansichten gleich. */}
      <rect x="140" y="46" width="240" height="10" rx="4" className="v-panel" />

      {/* ── Aufbau ─────────────────────────────────────────────────────── */}
      <g>
        <path
          d="M132 56 H512 V208 H132 Z"
          fill="url(#kv-body)"
          stroke="var(--border-strong)"
          strokeWidth="1.5"
        />
        {/* Fenster der Einstiegsseite: zwei, eines vor und eines hinter der
            Tür. Dazwischen liegt die geschlossene Fläche über der Terrasse. */}
        {[
          [160, 64],
          [380, 70],
        ].map(([x, w]) => (
          <rect key={x} x={x} y="82" width={w} height="46" rx="4" className="v-window" />
        ))}
        {/* Trennfuge zwischen Wohn- und Garagenbereich */}
        <path d="M262 136 H512" className="v-seam" />
      </g>

      {/* ── Fahrerhaus ─────────────────────────────────────────────────── */}
      <g>
        <path
          d="M512 100 H596 L664 146 V208 H512 Z"
          fill="url(#kv-body)"
          stroke="var(--border-strong)"
          strokeWidth="1.5"
        />
        <path d="M528 112 H590 L640 146 H528 Z" className="v-window" />
        <path d="M652 176 h12" className="v-seam" />
      </g>

      {/* ── Rahmen zwischen den Achsen ─────────────────────────────────── */}
      <path d="M150 208 H648" className="v-frame" />

      <Garage state={state.garage} />
      <Door state={state.door} />
      <Terrace state={state.terrace} />

      {/* ── Räder ──────────────────────────────────────────────────────── */}
      <g>
        {AXLES.map((cx) => (
          <g key={cx}>
            <circle cx={cx} cy={AXLE_Y} r={AXLE_R} className="v-tyre" />
            <circle cx={cx} cy={AXLE_Y} r="12" className="v-rim" />
          </g>
        ))}
      </g>
      </g>
    </svg>
  );
}

/* ── Einzelteile ──────────────────────────────────────────────────────── */

function Garage({ state }: { state: Part }) {
  if (state === "absent") return null;

  // Das Tor fährt nach oben auf. Bei unbekanntem Zustand bleibt es an der
  // geschlossenen Position, wird aber gestrichelt — die Lage wird nicht
  // behauptet.
  const lift = state === "open" ? 54 : state === "moving" ? 27 : 0;

  return (
    <g className={`v-part v-part--${state}`}>
      <rect x="146" y="142" width="102" height="64" rx="3" className="v-cavity" />
      <g clipPath="url(#kv-garage-opening)">
        <g className="v-animated" style={{ transform: `translateY(${-lift}px)` }}>
          <rect x="146" y="142" width="102" height="64" rx="3" className="v-panel" />
          <path d="M152 158h90M152 174h90M152 190h90" className="v-panel-line" />
        </g>
      </g>
      {/* Rahmen der Öffnung bleibt sichtbar, damit man sieht, wohin das Tor fährt */}
      <rect
        x="146" y="142" width="102" height="64" rx="3"
        className="v-opening"
      />
    </g>
  );
}

function Door({ state }: { state: Part }) {
  if (state === "absent") return null;

  // Türblatt schwenkt zum Betrachter — perspektivisch als Verschmälerung.
  const swing = state === "open" ? 0.32 : state === "moving" ? 0.66 : 1;

  return (
    <g className={`v-part v-part--${state}`}>
      {/* Die Tür steht über der ersten Tandemachse (AXLES[1] = 288). */}
      <rect x="266" y="118" width="44" height="90" rx="3" className="v-cavity" />
      <g
        className="v-animated"
        style={{ transform: `scaleX(${swing})`, transformOrigin: "266px 0" }}
      >
        <rect x="266" y="118" width="44" height="90" rx="3" className="v-panel" />
        <circle cx="302" cy="166" r="2.5" className="v-detail" />
      </g>
    </g>
  );
}

/**
 * Die ausfahrbare Terrasse über dem Tandem.
 *
 * Sie ist der einzige Teil, der eingefahren **gar nichts** hinterlässt — die
 * Fotos zeigen dann eine glatte Flanke und frei stehende Räder. Bei
 * unbekannter Stellung erscheint deshalb die Außenschürze gestrichelt an der
 * Ruhelage, also bündig in der Flanke. Ein gestricheltes Nichts wäre vom
 * eingefahrenen Nichts nicht zu unterscheiden (Kapitel 18 §106).
 */
function Terrace({ state }: { state: Part }) {
  if (state === "absent") return null;

  // Der Schlitz über dem Tandem, aus dem sie kommt — von vor der hinteren bis
  // hinter die vordere Tandemachse (AXLES[0] = 214, AXLES[1] = 288).
  const x = 169;
  const w = 164;

  if (state === "unknown") {
    return (
      <g className="v-part v-part--unknown">
        <rect x={x} y="204" width={w} height="26" rx="3" className="v-panel" />
      </g>
    );
  }

  if (state === "closed") return null;

  const out = state === "open" ? 1 : 0.5;
  const drop = out * 12;

  return (
    <g className={`v-part v-part--${state}`}>
      <g className="v-animated">
        {/* Belag. Die Seitenansicht kann das Ausfahren zum Betrachter hin
            nicht zeigen — es wird als Absetzen nach unten angedeutet. */}
        <rect x={x} y={204 + drop} width={w} height="8" rx="2" className="v-panel" />
        {/* Treppe, nach vorn abfallend. Kein Handlauf. */}
        {[0, 1, 2, 3].map((i) => (
          <rect
            key={i}
            x={x + w + i * 11}
            y={212 + drop + (i + 1) * 8}
            width="11"
            height="4"
            rx="1"
            className="v-panel"
          />
        ))}
      </g>
    </g>
  );
}

