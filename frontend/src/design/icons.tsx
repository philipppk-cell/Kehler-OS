/**
 * Das Icon-Set.
 *
 * Ein einziger Stil: Konturen, 1.5 px Strichstärke, 24er Raster, runde
 * Enden. Kapitel 7 §21 verbietet die Mischung verschiedener Icon-Sets — und
 * genau deshalb entstehen sie hier statt aus einer Bibliothek, deren Stil
 * sich mit einem Update ändern kann.
 *
 * Alle Icons sind lokal. Kein CDN, kein Nachladen (Kapitel 17 §107).
 */

import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function Icon({ size = 22, children, ...props }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export const IconDashboard = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 10.5 12 3l9 7.5" />
    <path d="M5 9.5V20h14V9.5" />
    <path d="M9.5 20v-6h5v6" />
  </Icon>
);

export const IconEnergy = (p: IconProps) => (
  <Icon {...p}>
    <path d="M13 2 4.5 13.5H11L10 22l8.5-11.5H12L13 2Z" />
  </Icon>
);

export const IconWater = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 3s6 6.4 6 10.5a6 6 0 0 1-12 0C6 9.4 12 3 12 3Z" />
  </Icon>
);

/** Thermometer — steht für Temperatur allgemein, nicht für ein System. */
export const IconClimate = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 3v11" />
    <circle cx="12" cy="17" r="3.5" />
    <path d="M12 3a2 2 0 0 1 2 2v9" />
    <path d="M10 5a2 2 0 0 1 2-2" />
  </Icon>
);

/* Klima und Heizung sind getrennte Systeme und bekommen deshalb auch
   getrennte Zeichen. Zweimal dasselbe Thermometer in der Navigation wäre
   genau die Verwechslung, die die Trennung vermeiden soll. */

/** Schneeflocke — Klima (Kühlung). */
export const IconCooling = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 2v20" />
    <path d="M3.5 7 20.5 17" />
    <path d="M20.5 7 3.5 17" />
    <path d="m9.5 4.5 2.5 2.5 2.5-2.5" />
    <path d="m9.5 19.5 2.5-2.5 2.5 2.5" />
  </Icon>
);

/** Flamme — Heizung. */
export const IconHeating = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 2.5c3.5 3.6 5.5 6.3 5.5 9.4a5.5 5.5 0 0 1-11 0c0-1.6.6-3 1.7-4.5.5 1.1 1.2 1.8 2 2 -.2-2.3.4-4.5 1.8-6.9Z" />
    <path d="M12 20.5a2.6 2.6 0 0 1-2.6-2.6c0-1.3.9-2.3 2.6-4 1.7 1.7 2.6 2.7 2.6 4a2.6 2.6 0 0 1-2.6 2.6Z" />
  </Icon>
);

export const IconLeveling = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 14h18" />
    <path d="M6 14v4" />
    <path d="M18 14v4" />
    <path d="M4 10h16l-1.5-4h-13L4 10Z" />
  </Icon>
);

export const IconVehicle = (p: IconProps) => (
  <Icon {...p}>
    <path d="M2 16V8.5A1.5 1.5 0 0 1 3.5 7h10V16" />
    <path d="M13.5 9H17l3 3.5V16" />
    <circle cx="7" cy="17" r="2" />
    <circle cx="17" cy="17" r="2" />
    <path d="M9 17h6" />
  </Icon>
);

export const IconCamera = (p: IconProps) => (
  <Icon {...p}>
    <rect x="2.5" y="6.5" width="13" height="11" rx="2" />
    <path d="M15.5 10.5 21.5 8v8l-6-2.5" />
  </Icon>
);

export const IconGarage = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 20V9l9-5 9 5v11" />
    <path d="M6.5 20v-7h11v7" />
    <path d="M6.5 16h11" />
  </Icon>
);

export const IconSettings = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1Z" />
  </Icon>
);

export const IconDiagnostics = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 12h4l2.5-6 5 12 2.5-6h4" />
  </Icon>
);

export const IconWarning = (p: IconProps) => (
  <Icon {...p}>
    <path d="M10.3 3.9 2.4 17.2A2 2 0 0 0 4.1 20h15.8a2 2 0 0 0 1.7-2.8L13.7 3.9a2 2 0 0 0-3.4 0Z" />
    <path d="M12 9v4.5" />
    <path d="M12 17h.01" />
  </Icon>
);

export const IconDoor = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 21V4a1 1 0 0 1 1-1h11a1 1 0 0 1 1 1v17" />
    <path d="M3 21h18" />
    <path d="M13.5 12h.01" />
  </Icon>
);

export const IconWindow = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3.5" y="4" width="17" height="16" rx="1.5" />
    <path d="M12 4v16" />
    <path d="M3.5 12h17" />
  </Icon>
);

export const IconStep = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 19h5v-4h5v-4h5V7h3" />
  </Icon>
);

export const IconAwning = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 5h18" />
    <path d="M4 5c0 4 3 7 8 7s8-3 8-7" />
    <path d="M12 12v7" />
  </Icon>
);

export const IconPump = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="13" r="5.5" />
    <path d="M12 7.5V4h4" />
    <path d="M12 13l3-2.5" />
  </Icon>
);

/**
 * Ein Absperrventil — Rohr, Gehäuse, Handrad.
 *
 * Bewusst nicht der Tropfen, den man für „Wasser ablassen" erwarten würde:
 * Das Symbol steht neben einem Tankfüllstand, und zwei Wassersymbole
 * nebeneinander unterscheiden sich nicht mehr. Ein Ventil zeigt das
 * Bedienelement, nicht sein Medium.
 */
export const IconValve = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 13h4M17 13h4" />
    <path d="M7 9.5h10v7H7z" />
    <path d="M12 9.5V5" />
    <path d="M9 5h6" />
  </Icon>
);

export const IconPlug = (p: IconProps) => (
  <Icon {...p}>
    <path d="M9 3v6" />
    <path d="M15 3v6" />
    <path d="M6 9h12v3a6 6 0 0 1-6 6 6 6 0 0 1-6-6V9Z" />
    <path d="M12 18v3" />
  </Icon>
);

export const IconSolar = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" />
  </Icon>
);

export const IconWifi = (p: IconProps) => (
  <Icon {...p}>
    <path d="M2.5 9a15 15 0 0 1 19 0" />
    <path d="M5.5 12.5a10.5 10.5 0 0 1 13 0" />
    <path d="M8.5 16a6 6 0 0 1 7 0" />
    <path d="M12 19.5h.01" />
  </Icon>
);

export const IconUser = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="8" r="4" />
    <path d="M4.5 20a7.5 7.5 0 0 1 15 0" />
  </Icon>
);

export const IconChart = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 20h18" />
    <path d="M6 20v-6M11 20V8M16 20v-9M21 20V5" />
  </Icon>
);
