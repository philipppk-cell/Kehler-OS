import {
  useEffect,
  useState,
} from "react";

const REFRESH_MS = 60_000;

export interface ForecastMetric {
  ready: boolean;
  rate_l_day: number | null;
  remaining_days: number | null;
  observed_hours: number;
  change_l: number;
}

export interface WaterForecast {
  available: boolean;
  started_at: number | null;
  fresh: ForecastMetric;
  grey: ForecastMetric;
  black: ForecastMetric;
}

export function useWaterForecast(
  online: boolean,
): {
  forecast: WaterForecast | null;
  resetting: boolean;
  reset: () => Promise<void>;
} {
  const [forecast, setForecast] =
    useState<WaterForecast | null>(null);

  const [resetting, setResetting] =
    useState(false);

  useEffect(() => {
    if (!online) return;

    let active = true;

    async function load() {
      try {
        const response = await fetch(
          "/api/v1/water/forecast",
          { cache: "no-store" },
        );

        if (!response.ok) return;

        const data =
          await response.json() as WaterForecast;

        if (active) {
          setForecast(data);
        }
      } catch {
        // Die bestehende Anzeige bleibt stehen.
      }
    }

    void load();

    const timer = window.setInterval(
      () => void load(),
      REFRESH_MS,
    );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [online]);

  async function reset() {
    setResetting(true);

    try {
      const response = await fetch(
        "/api/v1/water/forecast/reset",
        {
          method: "POST",
        },
      );

      if (!response.ok) return;

      const data =
        await response.json() as WaterForecast;

      setForecast(data);
    } finally {
      setResetting(false);
    }
  }

  return {
    forecast,
    resetting,
    reset,
  };
}
