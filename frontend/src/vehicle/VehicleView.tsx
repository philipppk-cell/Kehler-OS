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
 *   Eingangstür     x 404…456
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
  step: Part;
  awning: Part;
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

      {/* Markise liegt hinter dem Aufbau, damit die Kassette bündig sitzt */}
      <Awning state={state.awning} />

      {/* ── Aufbau ─────────────────────────────────────────────────────── */}
      <g>
        <path
          d="M132 56 H512 V208 H132 Z"
          fill="url(#kv-body)"
          stroke="var(--border-strong)"
          strokeWidth="1.5"
        />
        {/* Fenster des Wohnbereichs, gleichmäßig geteilt */}
        {[172, 262, 336].map((x, i) => (
          <rect
            key={x}
            x={x}
            y="82"
            width={i === 0 ? 70 : 58}
            height="46"
            rx="4"
            className="v-window"
          />
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
      <Step state={state.step} />

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
      <rect x="404" y="118" width="52" height="90" rx="3" className="v-cavity" />
      <g
        className="v-animated"
        style={{ transform: `scaleX(${swing})`, transformOrigin: "404px 0" }}
      >
        <rect x="404" y="118" width="52" height="90" rx="3" className="v-panel" />
        <circle cx="446" cy="166" r="2.5" className="v-detail" />
      </g>
    </g>
  );
}

function Step({ state }: { state: Part }) {
  if (state === "absent") return null;

  const out = state === "open" ? 1 : state === "moving" ? 0.5 : 0;

  return (
    <g className={`v-part v-part--${state}`}>
      <g
        className="v-animated"
        style={{
          transform: `translate(${out * 22}px, ${out * 14}px)`,
          opacity: out === 0 ? 0.4 : 1,
        }}
      >
        <rect x="408" y="212" width="46" height="7" rx="2" className="v-panel" />
        <rect x="414" y="226" width="34" height="6" rx="2" className="v-panel" />
      </g>
    </g>
  );
}

function Awning({ state }: { state: Part }) {
  if (state === "absent") return null;

  const extend = state === "open" ? 1 : state === "moving" ? 0.5 : 0;
  const reach = 132 * extend;
  const drop = 30 * extend;

  return (
    <g className={`v-part v-part--${state}`}>
      {/* Kassette sitzt bündig auf der Aufbaukante */}
      <rect x="140" y="46" width="240" height="10" rx="4" className="v-panel" />
      {extend > 0 && (
        <g className="v-animated">
          <path
            d={`M144 56 L${144 - reach} ${56 + drop} L${144 - reach} ${64 + drop} L144 64 Z`}
            className="v-fabric"
          />
          <path d={`M${144 - reach} ${60 + drop} V196`} className="v-support" />
        </g>
      )}
    </g>
  );
}
