import { useEffect, useState } from "react";
import { Shell, type PageId } from "./shell/Shell";
import { Dashboard } from "./pages/Dashboard";
import { Wasser } from "./pages/Wasser";
import { Energie } from "./pages/Energie";
import { Klima } from "./pages/Klima";
import { Heizung } from "./pages/Heizung";
import { Fahrzeug } from "./pages/Fahrzeug";
import { Diagnose } from "./pages/Diagnose";
import { Einstellungen } from "./pages/Einstellungen";
import { Placeholder } from "./pages/Placeholder";
import { BootScreen } from "./boot/BootScreen";
import { RealtimeClient, realtimeUrl } from "./realtime/client";
import { fetchSystem } from "./api/client";
import { useAppState } from "./realtime/hooks";
import { t } from "./i18n/de";
import "./app.css";

export function App() {
  const [page, setPage] = useState<PageId>("dashboard");
  const { lastError } = useAppState();

  useEffect(() => {
    const client = new RealtimeClient(realtimeUrl());
    client.connect();
    void fetchSystem();

    // Der Systemzustand ändert sich langsam; ein Intervall genügt.
    const timer = window.setInterval(() => void fetchSystem(), 5000);

    return () => {
      client.disconnect();
      window.clearInterval(timer);
    };
  }, []);

  return (
    <>
      {/* Liegt über allem und entscheidet selbst, wann es geht: sobald der
          erste Zustand da ist — oder sofort, wenn die Verbindung scheitert,
          damit das Banner dahinter sichtbar wird. */}
      <BootScreen />

      <Shell page={page} onNavigate={setPage}>
        {page === "dashboard" ? (
          <Dashboard />
        ) : page === "water" ? (
          <Wasser />
        ) : page === "energy" ? (
          <Energie />
        ) : page === "climate" ? (
          <Klima />
        ) : page === "heating" ? (
          <Heizung />
        ) : page === "vehicle" ? (
          <Fahrzeug />
        ) : page === "diagnostics" ? (
          <Diagnose />
        ) : page === "settings" ? (
          <Einstellungen />
        ) : (
          <Placeholder title={t(`nav.${page}`)} />
        )}

        {/* Fehlgeschlagene Befehle werden verständlich gemeldet — nie stumm
            verschluckt (Kapitel 17 §20/§22). */}
        {lastError && <div className="toast toast--error">{lastError.message}</div>}
      </Shell>
    </>
  );
}
