/**
 * Der Zustand des Fahrzeugs, wie ihn die Darstellung braucht.
 *
 * Die Zeichnung — ob SVG oder 3D — kennt keine Entities und keine
 * Qualitätsstufen. Sie kennt Stellungen: offen, geschlossen, in Bewegung,
 * unbekannt, gar nicht vorhanden. Diese Übersetzung findet hier statt, und
 * zwar an **einer** Stelle: Dashboard und Fahrzeugseite zeigen dasselbe
 * Fahrzeug und dürfen es nicht verschieden auslegen.
 *
 * Sie lag zuvor in `pages/Dashboard.tsx`, solange es nur einen Nutzer gab.
 * Mit der Fahrzeugseite gibt es zwei — und damit ist der gemeinsame Baustein
 * kein Vorrat auf Verdacht mehr, sondern der Schutz vor zwei Auslegungen
 * desselben Zustands.
 */

import type { Part } from "../vehicle/VehicleView";
import { isUnknown, textOf, useAppState, useEntity } from "../realtime/hooks";
import type { EntityView } from "../realtime/types";

export interface VehicleParts {
  garage: Part;
  door: Part;
  terrace: Part;
}

export function useVehicleState(): VehicleParts {
  const garage = useEntity("vehicle.garage.door");
  const door = useEntity("vehicle.door.main");
  // Die Entity heißt weiterhin `step`, weil sie einer Hardwarezuordnung
  // entspricht und eine Umbenennung Konfiguration und Mapping erfasst. Das
  // Bauteil ist eine Terrasse; die Anzeige nennt es auch so.
  const terrace = useEntity("vehicle.step.entry");
  const { connection } = useAppState();

  // Ohne Verbindung darf die Zeichnung keine Stellung mehr zeigen. Ein
  // angehobenes Garagentor wäre sonst eine Aussage über das Fahrzeug, die das
  // System gar nicht mehr belegen kann (Kapitel 18 §37/§106).
  const live = connection === "online";

  return {
    garage: toPart(garage, live),
    door: toPart(door, live),
    terrace: toPart(terrace, live),
  };
}

/** Übersetzt einen Hardwarezustand in eine Darstellung — ohne zu raten. */
export function toPart(entity: EntityView | undefined, live: boolean): Part {
  // Ohne Hardwarezuordnung wird das Teil gar nicht gezeichnet. Ein
  // gestrichelter Umriss hieße „vorhanden, Lage unbekannt“ — das wäre hier
  // falsch (Kapitel 18 §101).
  if (!entity || entity.definition?.configured === false) return "absent";

  const value = textOf(entity);
  if (!live || isUnknown(entity) || !value) return "unknown";
  if (value === "OPENING" || value === "CLOSING") return "moving";
  if (value === "OPEN") return "open";
  if (value === "CLOSED" || value === "STOPPED") return "closed";

  // Blockiert heißt: Das Teil steht irgendwo zwischen den Endlagen, und wo
  // genau, weiß niemand. „Geschlossen" zu zeichnen wäre hier die gefährliche
  // Vermutung — eine klemmende Markise sähe eingefahren aus.
  if (value === "BLOCKED") return "unknown";
  return "unknown";
}
