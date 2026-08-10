/**
 * Der Verlauf einer Messgröße.
 *
 * Geholt, nicht gerechnet: Auflösung, Verdichtung und Aufbewahrung entscheidet
 * das Backend (`core/history.py`). Die Oberfläche zeichnet, was sie bekommt.
 *
 * **Punkte ohne Wert werden mitgeliefert und nicht weggeworfen.** Sie sind die
 * Aussage „hier war nichts bekannt". Wer sie herausfiltert, bekommt eine
 * durchgehende Linie über eine Lücke — genau das, was Kapitel 16 §97
 * verbietet.
 */

import { useEffect, useState } from "react";

export interface HistoryPoint {
  /** Unix-Millisekunden in UTC. Umgerechnet wird erst bei der Anzeige. */
  at: number;
  /** `null` heißt: zu diesem Zeitpunkt kein belastbarer Wert. */
  value: number | null;
  quality: string;
}

export interface History {
  entity_id: string;
  /** `false`, wenn die Historie abgeschaltet ist oder nicht schreiben kann. */
  available: boolean;
  resolution: "raw" | "minute" | "hour" | null;
  points: HistoryPoint[];
}

/** Wie lange die Oberfläche zurückblicken kann. */
export const SPANS = [
  { hours: 6, key: "history.span6h" },
  { hours: 24, key: "history.span24h" },
  { hours: 24 * 7, key: "history.span7d" },
  { hours: 24 * 30, key: "history.span30d" },
] as const;

export function useHistory(entityId: string | null, hours: number): History | null {
  const [history, setHistory] = useState<History | null>(null);

  useEffect(() => {
    if (entityId === null) {
      setHistory(null);
      return;
    }

    let active = true;
    setHistory(null);

    fetch(`/api/v1/history/${encodeURIComponent(entityId)}?hours=${hours}`)
      .then((response) => (response.ok ? response.json() : null))
      .then((data: History | null) => {
        if (active && data) setHistory(data);
      })
      .catch(() => undefined);

    return () => {
      active = false;
    };
    // Bewusst **nicht** an den Live-Zustand gekoppelt: Eine Kurve über sieben
    // Tage bei jedem eintreffenden Messwert neu zu laden, hieße sie mehrmals
    // pro Sekunde neu zu holen. Der Verlauf ändert sich am rechten Rand um
    // Pixelbruchteile; die aktuelle Zahl steht ohnehin daneben.
  }, [entityId, hours]);

  return history;
}

/**
 * Zerlegt die Punkte in zusammenhängende Abschnitte.
 *
 * Das ist die Stelle, an der aus der Regel „eine Lücke bleibt eine Lücke" eine
 * gezeichnete Linie wird: Jeder Punkt ohne Wert **beendet** den laufenden
 * Abschnitt. Gezeichnet wird pro Abschnitt ein eigener Linienzug, und zwischen
 * zwei Abschnitten bleibt Papier.
 *
 * Ein einzelner Abschnitt aus genau einem Punkt bleibt erhalten — er wird als
 * Punkt gezeichnet und nicht verworfen. Ein Messwert zwischen zwei Lücken ist
 * eine Information.
 */
/**
 * Die Zeitbereiche, in denen nichts bekannt war.
 *
 * Das Weglassen der Linie allein genügt nicht: Eine kurze Lücke ist drei
 * Pixel breit und sieht aus wie ein Darstellungsfehler, nicht wie eine
 * Aussage. Deshalb wird die Lücke **gezeichnet** — als eigene Fläche, die
 * sagt „hier wusste niemand etwas".
 *
 * Ein Bereich reicht vom letzten belastbaren Wert davor bis zum ersten
 * danach. Genau dazwischen liegt die Ungewissheit: Wann der Fühler verstummte,
 * ist bekannt; wann er wieder etwas Richtiges lieferte, auch.
 */
export function gaps(points: HistoryPoint[]): { from: number; to: number }[] {
  const result: { from: number; to: number }[] = [];
  let lastValid: number | null = null;
  let pending = false;

  for (const point of points) {
    if (point.value === null) {
      pending = true;
      continue;
    }
    if (pending && lastValid !== null) {
      result.push({ from: lastValid, to: point.at });
    }
    pending = false;
    lastValid = point.at;
  }

  // Eine Lücke, die bis zum Ende des Zeitraums reicht, hat kein
  // abschließendes „danach". Sie wird trotzdem gezeigt: Dass gerade jetzt
  // nichts bekannt ist, ist die wichtigere Hälfte der Auskunft.
  const last = points[points.length - 1];
  if (pending && lastValid !== null && last) {
    result.push({ from: lastValid, to: last.at });
  }

  return result;
}

export function segments(points: HistoryPoint[]): HistoryPoint[][] {
  const result: HistoryPoint[][] = [];
  let current: HistoryPoint[] = [];

  for (const point of points) {
    if (point.value === null) {
      if (current.length > 0) result.push(current);
      current = [];
      continue;
    }
    current.push(point);
  }
  if (current.length > 0) result.push(current);

  return result;
}
