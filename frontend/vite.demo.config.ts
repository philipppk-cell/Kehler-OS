import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Build für die Demo-Datei.
 *
 * Unterschied zum normalen Build: **ein einziges Bündel.** Im Fahrzeug wird
 * die Fahrzeugdarstellung bewusst nachgeladen, damit die erste Seite schnell
 * steht — in einer einzelnen HTML-Datei gibt es aber nichts nachzuladen. Ohne
 * `inlineDynamicImports` bliebe die 3D-Ansicht ein zweiter Brocken, den die
 * Datei nicht enthalten kann, und das Fahrzeug erschiene nie.
 *
 * Der reguläre Build in `vite.config.ts` bleibt davon unberührt.
 */
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist-demo",
    emptyOutDir: true,
    rollupOptions: {
      output: { inlineDynamicImports: true },
    },
    // Die Datei wird ohnehin am Stück ausgeliefert; die Warnschwelle für
    // Bündelgrößen sagt hier nichts aus.
    chunkSizeWarningLimit: 2000,
  },
});
