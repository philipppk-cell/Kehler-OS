/**
 * Demo-Schicht für Kehler OS.
 *
 * Ersetzt Netzwerk und WebSocket durch eine **Aufzeichnung des echten
 * Backends**. Die Oberfläche merkt davon nichts: Sie fragt dieselben
 * Endpunkte, bekommt dieselben Datenformen und zeigt dieselben Zustände.
 *
 * ── Warum eine Aufzeichnung und keine Nachbildung ─────────────────────────
 *
 * Es wäre möglich gewesen, die Zusammenfassungen in JavaScript neu zu rechnen
 * — Gesamtmenge Frischwasser, Laderichtung, Wärmequelle. Das wäre genau die
 * Verdopplung von Geschäftslogik, die Kapitel 18 §6 verhindern soll: Zwei
 * Umsetzungen derselben Regel laufen auseinander, und dann zeigt die Demo
 * etwas anderes als das Fahrzeug.
 *
 * Hier wird deshalb nichts gerechnet, sondern abgespielt. Jede Zahl auf dem
 * Bildschirm ist eine Zahl, die das Backend tatsächlich ausgegeben hat.
 *
 * ── Was die Demo nicht kann ───────────────────────────────────────────────
 *
 * **Sie schaltet nichts.** Jeder Befehl wird abgewiesen, mit einem Grund, der
 * das sagt. Das ist keine Einschränkung, die man wegkonfigurieren könnte: Es
 * gibt hier kein Fahrzeug, keine Steuerung und keinen Adapter — nur eine
 * Datei.
 */

(function () {
  const DATA = window.__KEHLER_DEMO__;
  if (!DATA) return;

  const frames = DATA.frames;
  const definitions = DATA.definitions;
  const started = Date.now();

  /** Das gerade gültige Einzelbild — die Aufzeichnung läuft in Schleife. */
  function frame() {
    const elapsed = Date.now() - started;
    return frames[Math.floor(elapsed / DATA.intervalMs) % frames.length];
  }

  /** Ein Zustand, ergänzt um seine Definition. */
  function entityView(entry) {
    return {
      entity_id: entry.entity_id,
      seq: entry.seq,
      link: entry.link,
      state: entry.state,
      attributes: {},
      requested: null,
      definition: definitions[entry.entity_id],
    };
  }

  function snapshot() {
    const current = frame();
    return {
      type: "snapshot",
      version: current.entities.length,
      entities: current.entities.map(entityView),
    };
  }

  /* ── HTTP ──────────────────────────────────────────────────────────────
     Die Oberfläche fragt dieselben Endpunkte wie am Fahrzeug. Ein Pfad, den
     die Aufzeichnung nicht kennt, antwortet mit 404 — nicht mit einem leeren
     Objekt, das wie eine gültige Antwort aussähe.                        */

  const realFetch = window.fetch.bind(window);

  window.fetch = function (input, init) {
    const url = typeof input === "string" ? input : input.url;
    const method = (init && init.method) || "GET";

    if (!url.includes("/api/v1")) return realFetch(input, init);

    const path = url.slice(url.indexOf("/api/v1") + "/api/v1".length);

    if (method === "POST") return json(rejectCommand(path), 409);

    const [clean, query] = path.split("?");
    const current = frame();

    if (clean === "/system") return json(current["/system"]);
    if (clean === "/water") return json(current["/water"]);
    if (clean === "/energy") return json(current["/energy"]);
    if (clean === "/heating") return json(current["/heating"]);
    if (clean === "/alerts") return json(current["/alerts"]);
    if (clean === "/diagnostics/services") return json(current["/diagnostics/services"]);
    if (DATA.static[clean]) return json(DATA.static[clean]);

    if (clean === "/entities") return json(current.entities.map(entityView));

    if (clean.startsWith("/history/")) {
      const entityId = decodeURIComponent(clean.slice("/history/".length));
      const hours = new URLSearchParams(query || "").get("hours") || "24";
      const series = DATA.history[`${entityId}:${hours}`];
      // Kein aufgezeichneter Verlauf heißt „für diesen Zeitraum liegen keine
      // Werte vor" — und nicht „Historie nicht verfügbar". Das eine ist eine
      // Aussage über den Zeitraum, das andere über die Datenhaltung.
      return json(
        series || { entity_id: entityId, available: true, resolution: "raw", points: [] },
      );
    }

    return json({ detail: "In der Demo nicht enthalten" }, 404);
  };

  function json(body, status) {
    return Promise.resolve(
      new Response(JSON.stringify(body), {
        status: status || 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
  }

  /**
   * Jeder Befehl wird abgewiesen.
   *
   * Bewusst über denselben Weg wie eine echte Ablehnung: Die Oberfläche
   * bekommt eine ordentliche Antwort mit Grund und zeigt ihre gewohnte
   * Meldung. Nichts wird stumm verschluckt (Kapitel 17 §20/§22).
   */
  function rejectCommand(path) {
    return {
      command_id: "demo",
      entity_id: "",
      verb: "",
      phase: "REJECTED",
      success: false,
      rejection: "DEMO",
      ended_state: null,
      detail: `Demo — kein Fahrzeug angebunden (${path})`,
      duration_ms: 0,
    };
  }

  /* ── WebSocket ─────────────────────────────────────────────────────────
     Die Oberfläche bekommt beim Verbinden einen Schnappschuss und danach
     bei jedem Bildwechsel einen neuen. Deltas wären sparsamer; hier zählt,
     dass der Ablauf derselbe ist und nichts nachgerechnet wird.          */

  class DemoSocket {
    constructor() {
      this.readyState = 1;
      this.onopen = null;
      this.onmessage = null;
      this.onclose = null;
      this.onerror = null;

      setTimeout(() => {
        if (this.onopen) this.onopen(new Event("open"));
        this.send_(snapshot());
        this.timer = setInterval(() => this.send_(snapshot()), DATA.intervalMs);
      }, 60);
    }

    send_(payload) {
      if (this.onmessage) {
        this.onmessage(new MessageEvent("message", { data: JSON.stringify(payload) }));
      }
    }

    send() {}

    close() {
      clearInterval(this.timer);
      this.readyState = 3;
      if (this.onclose) this.onclose(new CloseEvent("close"));
    }

    addEventListener(type, listener) {
      this["on" + type] = listener;
    }

    removeEventListener(type) {
      this["on" + type] = null;
    }
  }

  DemoSocket.OPEN = 1;
  DemoSocket.CLOSED = 3;
  window.WebSocket = DemoSocket;
})();
