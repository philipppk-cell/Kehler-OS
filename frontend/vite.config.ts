import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Das Frontend wird zu statischen Dateien gebaut und vom Backend ausgeliefert.
// Dadurch braucht das Fahrzeug keinen zweiten Webserver (ADR 0006).
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../backend/kehleros/api/static",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", ws: true },
    },
  },
});
