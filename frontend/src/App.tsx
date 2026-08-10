import { useEffect, useState } from "react";
import { Shell, type PageId } from "./shell/Shell";
import { Dashboard } from "./pages/Dashboard";
import { Wasser } from "./pages/Wasser";
import { Energie } from "./pages/Energie";
import { Klima } from "./pages/Klima";
import { Heizung } from "./pages/Heizung";
import { Fahrzeug } from "./pages/Fahrzeug";
import { Placeholder } from "./pages/Placeholder";
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
      ) : (
        <Placeholder title={t(`nav.${page}`)} />
      )}

      {/* Fehlgeschlagene Befehle werden verständlich gemeldet — nie stumm
          verschluckt (Kapitel 17 §20/§22). */}
      {lastError && <div className="toast toast--error">{lastError.message}</div>}
    </Shell>
  );
}
