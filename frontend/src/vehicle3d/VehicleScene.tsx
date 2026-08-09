/**
 * Die dreidimensionale Fahrzeugansicht.
 *
 * **Sie ist reine Ausgabe.** Man kann das Fahrzeug drehen, aber nicht
 * bedienen — kein Tippen auf ein Bauteil löst etwas aus. Gesteuert wird über
 * die Schnellzugriffe und die Fachseiten (Kapitel 8 §6).
 *
 * ── Warum das auf einem Raspberry Pi vertretbar ist ───────────────────────
 *
 * **Es wird nur gerendert, wenn sich etwas ändert.** Es gibt keine
 * Dauerschleife. Ein Bild entsteht, wenn der Finger das Fahrzeug dreht, wenn
 * die Ansicht ausläuft oder wenn ein Zustand eine Bewegung auslöst. Steht das
 * Bild still, kostet die Ansicht **keine** Rechenzeit — das ist der
 * Normalfall auf einem Dashboard, das stundenlang offen ist.
 *
 * Dazu kommen: keine Schattenkarten (der Bodenschatten ist eine Textur),
 * begrenzte Pixeldichte und ein Modell aus wenigen tausend Dreiecken.
 *
 * Ohne WebGL wird nichts erzwungen — dann übernimmt die SVG-Seitenansicht.
 */

import { useEffect, useRef } from "react";
import {
  ACESFilmicToneMapping,
  CanvasTexture,
  DirectionalLight,
  EquirectangularReflectionMapping,
  HemisphereLight,
  PMREMGenerator,
  PerspectiveCamera,
  Scene,
  Vector3,
  WebGLRenderer,
} from "three";

import { buildVehicle, type VehicleModel, type VehicleState } from "./buildVehicle";
import { PIVOT, V } from "./dimensions";
import { t } from "../i18n/de";
import "./vehicle3d.css";

/** Blickwinkel beim Start und nach dem Zurücksetzen: schräg von vorn rechts. */
const HOME = { azimuth: -0.78, polar: 0.28, distance: 27 };

const LIMITS = {
  /** Nie unter die Fahrbahn schauen und nie senkrecht von oben. */
  polar: { min: 0.03, max: 1.12 },
  distance: { min: 20, max: 48 },
};

/**
 * Enger Bildwinkel, dafür größerer Abstand.
 *
 * Ein weiter Bildwinkel lässt das nahe Ende des Fahrzeugs anschwellen — bei
 * zehn Metern Länge wirkt das Fahrerhaus dann doppelt so groß, wie es ist.
 * Diese Ansicht soll das Fahrzeug zeigen, nicht dramatisieren.
 */
const FOV = { wide: 24, narrow: 30 };

export function VehicleScene({
  state,
  label,
}: {
  state: VehicleState;
  /** Beschreibt den dargestellten Zustand für Vorlesewerkzeuge. */
  label: string;
}) {
  const hostRef = useRef<HTMLDivElement>(null);
  const apiRef = useRef<{ setState(s: VehicleState): void; home(): void } | null>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.02;
    host.appendChild(renderer.domElement);

    const scene = new Scene();
    const camera = new PerspectiveCamera(FOV.wide, 1, 0.5, 200);
    const pivot = new Vector3(0, PIVOT.y, PIVOT.z);

    /* ── Licht ─────────────────────────────────────────────────────────
       Eine Umgebung aus einem Verlauf statt einer Bilddatei: Weißer Lack
       braucht etwas zum Spiegeln, sonst wirkt er wie Papier. Der Verlauf
       wird einmal erzeugt und kostet danach nichts.                       */
    const pmrem = new PMREMGenerator(renderer);
    const environment = pmrem.fromEquirectangular(makeStudioTexture()).texture;
    scene.environment = environment;

    // Führungslicht von vorn oben, Aufhellung von der Gegenseite und ein
    // Streiflicht von hinten. Das Streiflicht ist der eigentliche Trick:
    // Es zeichnet die Kanten nach, damit ein weißes Fahrzeug vor dunklem
    // Hintergrund nicht als Silhouette verschwindet.
    const key = new DirectionalLight(0xffffff, 2.1);
    key.position.set(-8, 11, 9);
    scene.add(key);

    const fill = new DirectionalLight(0xc6dcea, 0.5);
    fill.position.set(10, 4, -6);
    scene.add(fill);

    const rim = new DirectionalLight(0x9adcee, 1.0);
    rim.position.set(5, 4, -12);
    scene.add(rim);

    scene.add(new HemisphereLight(0xcfe6f2, 0x11161a, 0.45));

    const model: VehicleModel = buildVehicle();
    scene.add(model.root);
    model.setState(state);
    model.settle();

    /* ── Ansicht ───────────────────────────────────────────────────────── */
    const view = { ...HOME };
    const spin = { azimuth: 0, polar: 0 };
    let homing = false;

    function place() {
      const { azimuth, polar, distance } = view;
      camera.position.set(
        pivot.x + distance * Math.sin(azimuth) * Math.cos(polar),
        pivot.y + distance * Math.sin(polar),
        pivot.z + distance * Math.cos(azimuth) * Math.cos(polar),
      );
      camera.lookAt(pivot);
    }

    function resize(el: HTMLDivElement) {
      const { clientWidth: w, clientHeight: h } = el;
      if (!w || !h) return;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      // Auf schmalen Anzeigen sonst abgeschnitten: Bildwinkel mitziehen.
      camera.fov = w / h < 1.7 ? FOV.narrow : FOV.wide;

      // Das Fahrzeug wird nach rechts gerückt, damit die Statuskarte unten
      // links über freier Fläche liegt. Das geschieht über den Bildausschnitt
      // und nicht durch Verschieben des Modells — dadurch bleibt das Fahrzeug
      // beim Drehen um seine eigene Mitte und nicht um einen Punkt daneben.
      const shift = w >= 820 ? w * 0.1 : 0;
      camera.setViewOffset(w, h, -shift, 0, w, h);

      camera.updateProjectionMatrix();
      request();
    }

    /* ── Bildanforderung ───────────────────────────────────────────────
       Der Kern der Sparsamkeit: Ein Bild wird angefordert, nicht
       fortlaufend erzeugt.                                                */
    let frame = 0;
    let last = 0;

    function request() {
      if (frame) return;
      last = performance.now();
      frame = requestAnimationFrame(tick);
    }

    function tick(now: number) {
      frame = 0;
      const dt = Math.min((now - last) / 1000, 0.1);
      last = now;
      let busy = false;

      if (homing) busy = glideHome(dt) || busy;
      else busy = coast(dt) || busy;

      busy = model.update(dt) || busy;

      place();
      renderer.render(scene, camera);
      if (busy) frame = requestAnimationFrame(tick);
    }

    /** Auslaufen nach dem Loslassen. */
    function coast(dt: number): boolean {
      if (Math.abs(spin.azimuth) < 0.0015 && Math.abs(spin.polar) < 0.0015) {
        spin.azimuth = spin.polar = 0;
        return false;
      }
      view.azimuth += spin.azimuth * dt;
      view.polar = clamp(view.polar + spin.polar * dt, LIMITS.polar.min, LIMITS.polar.max);
      const damping = Math.exp(-dt * 3.4);
      spin.azimuth *= damping;
      spin.polar *= damping;
      return true;
    }

    /** Weiche Rückkehr in die Ausgangsansicht. */
    function glideHome(dt: number): boolean {
      const k = 1 - Math.exp(-dt * 7);
      let delta = HOME.azimuth - view.azimuth;
      // Immer den kurzen Weg nehmen, nie mehrfach herumdrehen.
      delta = Math.atan2(Math.sin(delta), Math.cos(delta));
      view.azimuth += delta * k;
      view.polar += (HOME.polar - view.polar) * k;
      view.distance += (HOME.distance - view.distance) * k;

      if (Math.abs(delta) < 0.002 && Math.abs(HOME.polar - view.polar) < 0.002) {
        Object.assign(view, HOME);
        homing = false;
        return false;
      }
      return true;
    }

    /* ── Finger ────────────────────────────────────────────────────────── */
    const canvas = renderer.domElement;
    const pointers = new Map<number, { x: number; y: number }>();
    let pinch = 0;

    function onDown(event: PointerEvent) {
      canvas.setPointerCapture(event.pointerId);
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      spin.azimuth = spin.polar = 0;
      homing = false;
      if (pointers.size === 2) pinch = spread();
    }

    function onMove(event: PointerEvent) {
      const previous = pointers.get(event.pointerId);
      if (!previous) return;
      const dx = event.clientX - previous.x;
      const dy = event.clientY - previous.y;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });

      if (pointers.size >= 2) {
        // Zwei Finger: Abstand ändert den Betrachtungsabstand.
        const now = spread();
        if (pinch > 0 && now > 0) {
          view.distance = clamp(
            view.distance * (pinch / now),
            LIMITS.distance.min,
            LIMITS.distance.max,
          );
        }
        pinch = now;
        request();
        return;
      }

      // Ein Finger: waagerecht dreht, senkrecht kippt.
      const perPixel = (2 * Math.PI) / Math.max(canvas.clientWidth, 1);
      view.azimuth -= dx * perPixel * 1.15;
      view.polar = clamp(view.polar - dy * perPixel * 0.9, LIMITS.polar.min, LIMITS.polar.max);

      if (!reduced) {
        // Schwung merken, damit das Fahrzeug nach dem Loslassen weiterläuft.
        spin.azimuth = -dx * perPixel * 26;
        spin.polar = 0;
      }
      request();
    }

    function onUp(event: PointerEvent) {
      pointers.delete(event.pointerId);
      if (pointers.size < 2) pinch = 0;
      if (pointers.size === 0 && !reduced) request();
    }

    function onWheel(event: WheelEvent) {
      event.preventDefault();
      view.distance = clamp(
        view.distance * (event.deltaY > 0 ? 1.08 : 0.93),
        LIMITS.distance.min,
        LIMITS.distance.max,
      );
      request();
    }

    function spread(): number {
      const [a, b] = [...pointers.values()];
      return a && b ? Math.hypot(a.x - b.x, a.y - b.y) : 0;
    }

    canvas.addEventListener("pointerdown", onDown);
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerup", onUp);
    canvas.addEventListener("pointercancel", onUp);
    canvas.addEventListener("wheel", onWheel, { passive: false });

    const observer = new ResizeObserver(() => resize(host));
    observer.observe(host);
    resize(host);
    place();
    renderer.render(scene, camera);

    apiRef.current = {
      setState(next) {
        model.setState(next);
        if (reduced) {
          model.settle();
          place();
          renderer.render(scene, camera);
        } else {
          request();
        }
      },
      home() {
        homing = true;
        spin.azimuth = spin.polar = 0;
        if (reduced) {
          Object.assign(view, HOME);
          homing = false;
          place();
          renderer.render(scene, camera);
        } else {
          request();
        }
      },
    };

    return () => {
      apiRef.current = null;
      if (frame) cancelAnimationFrame(frame);
      observer.disconnect();
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerup", onUp);
      canvas.removeEventListener("pointercancel", onUp);
      canvas.removeEventListener("wheel", onWheel);
      model.dispose();
      environment.dispose();
      pmrem.dispose();
      renderer.dispose();
      canvas.remove();
    };
    // Die Szene wird einmal aufgebaut. Zustandsänderungen laufen über
    // `apiRef`, damit nicht bei jedem Messwert alles neu entsteht.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    apiRef.current?.setState(state);
  }, [state.garage, state.door, state.step, state.awning]);

  return (
    <div className="scene">
      <div
        className="scene__canvas"
        ref={hostRef}
        role="img"
        aria-label={label}
      />
      <button
        type="button"
        className="scene__home"
        onClick={() => apiRef.current?.home()}
        title={t("vehicle3d.resetHint")}
      >
        {t("vehicle3d.reset")}
      </button>
      <span className="scene__hint" aria-hidden="true">
        {t("vehicle3d.dragHint")}
      </span>
    </div>
  );
}

/* ── Umgebung ──────────────────────────────────────────────────────────── */

/**
 * Ein Studioverlauf als Umgebung: hell oben, dunkel unten, ein heller Streifen
 * als Lichtquelle. Er ersetzt eine Umgebungsaufnahme — kein Download, keine
 * externe Datei, und ohne Internet fällt nichts aus (Kapitel 17 §107).
 */
function makeStudioTexture(): CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;

  const sky = ctx.createLinearGradient(0, 0, 0, 128);
  sky.addColorStop(0, "#f2f7fb");
  sky.addColorStop(0.46, "#b9c8d4");
  sky.addColorStop(0.52, "#4d565e");
  sky.addColorStop(1, "#14181c");
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, 256, 128);

  // Ein breites „Fenster" erzeugt den langen Glanzstreifen auf dem Lack.
  const glow = ctx.createLinearGradient(0, 0, 0, 46);
  glow.addColorStop(0, "rgba(255,255,255,0.95)");
  glow.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = glow;
  ctx.fillRect(30, 0, 120, 46);

  const texture = new CanvasTexture(canvas);
  texture.mapping = EquirectangularReflectionMapping;
  return texture;
}

function clamp(value: number, min: number, max: number): number {
  return value < min ? min : value > max ? max : value;
}

export { V as VEHICLE_DIMENSIONS };
