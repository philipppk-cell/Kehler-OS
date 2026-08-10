import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { applyStoredPreferences } from "./settings/preferences";
import "./design/base.css";

// Vor dem ersten Rendern. Sonst blitzt die helle Darstellung kurz auf, bevor
// der Nachtmodus greift — nachts im Fahrzeug genau der Moment, den diese
// Einstellung verhindern soll.
applyStoredPreferences();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
