/**
 * Erzeugt einen PDF-Rundgang durch Kehler OS.
 *
 * Wozu, wenn es die Demo-Datei gibt: Zum **Weiterleiten** taugt eine 1,6-MB-
 * HTML-Datei schlecht. Der Empfänger muss sie herunterladen und öffnen, und
 * manche Messenger und Mailprogramme führen die enthaltenen Skripte nicht aus
 * — dann sieht er eine leere Seite. Ein PDF öffnet sich überall, ohne
 * Rückfrage und ohne Download-Ordner.
 *
 * Das PDF ersetzt die Demo nicht, es beantwortet eine andere Frage: „Wie sieht
 * das aus?" statt „Wie fühlt sich das an?".
 *
 * Die Bilder entstehen aus derselben Datei, die auch ausgeliefert wird — es
 * sind keine nachgestellten Entwürfe, sondern Aufnahmen der laufenden
 * Oberfläche.
 *
 *   node tools/demo/rundgang.mjs
 */

import { chromium } from "/opt/node22/lib/node_modules/playwright/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HIER = dirname(fileURLToPath(import.meta.url));
const DEMO = `file://${resolve(HIER, "kehler-os-demo.html")}`;

/* Die Reihenfolge ist die eines Rundgangs und nicht die der Navigation:
   erst der Überblick, dann die Versorgung, dann das, was noch aussteht. */
const SEITEN = [
  {
    nav: "Dashboard",
    titel: "Dashboard",
    text:
      "Der Überblick. Das Fahrzeug ist dreidimensional und lässt sich drehen. " +
      "Rechts die Warnungen — hier eine echte: Grauwasser über der Schwelle.",
  },
  {
    nav: "Energie",
    titel: "Energie",
    text:
      "Batterie, Solar, Landstrom und Verbrauch. „Lädt“ oder „entlädt“ wird nur " +
      "behauptet, wenn ein belastbarer Messwert vorliegt — sonst steht dort nichts.",
  },
  {
    nav: "Wasser",
    titel: "Wasser",
    text:
      "Vier Tanks. Die Gesamtmenge wird über Liter gebildet, nicht über Prozent, " +
      "und entfällt vollständig, sobald ein Tank keinen belastbaren Wert liefert.",
  },
  {
    nav: "Heizung",
    titel: "Heizung",
    text:
      "Die SCHEER-Anlage ist vollständig beschrieben, aber noch nicht angebunden: " +
      "Die Modbus-Registerliste liegt nicht vor. Deshalb steht überall „noch zu " +
      "verifizieren“ und es gibt bewusst kein einziges Bedienelement.",
  },
  {
    nav: "Fahrzeug",
    titel: "Fahrzeug",
    text:
      "Die beweglichen Teile. Der Stopp ist jederzeit erreichbar — auch mitten in " +
      "der Bewegung, denn genau dann wird er gebraucht.",
  },
  {
    nav: "Diagnose",
    titel: "Diagnose",
    text:
      "Für die Inbetriebnahme: jede Entity mit Verbindung, Qualität, Rohwert und " +
      "Rückstand. Die einzige Seite, auf der technische Rohdaten stehen.",
  },
  {
    nav: "Einstellungen",
    titel: "Einstellungen",
    text:
      "Bewusst kurz. Was es nicht gibt, wird benannt statt verschwiegen — jede " +
      "fehlende Einstellung mit ihrem Grund.",
  },
];

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1366, height: 1024 },
  deviceScaleFactor: 2,
});
const page = await ctx.newPage();
await page.goto(DEMO);
await page.waitForTimeout(3500);

const bilder = [];
for (const seite of SEITEN) {
  await page.getByRole("button", { name: seite.nav, exact: true }).click();
  // Warten, bis die Aufzeichnung ein Bild geliefert und die 3D-Ansicht
  // gezeichnet hat. Ohne das entstehen leere Flächen.
  await page.waitForTimeout(2500);
  const png = await page.screenshot();
  bilder.push({ ...seite, daten: png.toString("base64") });
  process.stdout.write(`  ${seite.titel}\n`);
}
await ctx.close();
// Ohne dies bleibt der Browserprozess offen und das Skript endet nie — das
// PDF war fertig, der Aufruf hing trotzdem.
await browser.close();

/* ── Das Blatt ──────────────────────────────────────────────────────────
   Ein Bild je Seite, quer, mit einer Bildunterschrift darunter. Die Farben
   stammen aus dem Designsystem des Projekts, damit das PDF nicht wie ein
   fremdes Dokument über fremden Bildern wirkt. */

const blatt = `<!doctype html><html lang="de"><head><meta charset="utf-8">
<style>
  @page { size: 297mm 210mm; margin: 0; }
  * { box-sizing: border-box; }
  body { margin: 0; background: #06090d; color: rgba(255,255,255,0.95);
         font-family: -apple-system, "Segoe UI", Roboto, sans-serif; }
  .blatt { width: 297mm; height: 210mm; padding: 12mm 14mm 10mm;
           display: flex; flex-direction: column; gap: 6mm;
           page-break-after: always; overflow: hidden; }
  .blatt:last-child { page-break-after: auto; }

  .titelblatt { justify-content: center; align-items: flex-start; gap: 8mm; }
  .marke { font-size: 34pt; letter-spacing: 0.16em; font-weight: 300; }
  .marke b { color: #38d6ee; font-weight: 600; }
  .unterzeile { font-size: 13pt; color: rgba(255,255,255,0.62); max-width: 190mm;
                line-height: 1.6; }
  .hinweis { margin-top: 4mm; padding: 5mm 6mm; border-radius: 4mm;
             background: #3a2a08; border: 1px solid rgba(245,165,36,0.4);
             color: #f5d79a; font-size: 10pt; line-height: 1.55; max-width: 190mm; }
  .hinweis b { color: #f5a524; text-transform: uppercase; letter-spacing: 0.06em; }

  .kopf { display: flex; align-items: baseline; gap: 5mm; flex: 0 0 auto; }
  .kopf h2 { margin: 0; font-size: 15pt; font-weight: 600; }
  .kopf p { margin: 0; font-size: 9.5pt; line-height: 1.5;
            color: rgba(255,255,255,0.62); }
  .bild { flex: 1; min-height: 0; display: flex; }
  .bild img { width: 100%; height: 100%; object-fit: contain;
              object-position: top center; border-radius: 3mm;
              border: 1px solid rgba(255,255,255,0.1); }
  .fuss { flex: 0 0 auto; font-size: 7.5pt; color: rgba(255,255,255,0.3); }
</style></head><body>

<div class="blatt titelblatt">
  <div class="marke">KEHLER <b>OS</b></div>
  <div class="unterzeile">
    Das Betriebssystem für das Expeditionsmobil — Energie, Wasser, Klima,
    Heizung und die beweglichen Aufbauteile unter einer Oberfläche.
  </div>
  <div class="hinweis">
    <b>Entwicklungsstand</b> — Die Bilder zeigen eine laufende Simulation, kein
    angebundenes Fahrzeug. Was noch nicht angeschlossen ist, ist in der
    Oberfläche als solches gekennzeichnet und bietet keine Bedienung an.
  </div>
</div>

${bilder
  .map(
    (b) => `<div class="blatt">
  <div class="kopf"><h2>${b.titel}</h2><p>${b.text}</p></div>
  <div class="bild"><img src="data:image/png;base64,${b.daten}" alt="${b.titel}"></div>
  <div class="fuss">Kehler OS · Simulation · ${new Date().toLocaleDateString("de-DE")}</div>
</div>`,
  )
  .join("\n")}

</body></html>`;

const pdfBrowser = await chromium.launch();
const pdfSeite = await pdfBrowser.newPage({ viewport: { width: 1123, height: 794 } });
await pdfSeite.setContent(blatt, { waitUntil: "load" });

/* Sichtprüfung. Ein fertiges PDF lässt sich hier nicht anzeigen — Chromium
   lädt es herunter, statt es zu zeichnen. Geprüft wird deshalb die Vorlage,
   aus der es entsteht: derselbe Inhalt, dasselbe Blattmaß.
   Mit `RUNDGANG_PRUEFEN=1` aufrufen. */
if (process.env.RUNDGANG_PRUEFEN) {
  const blaetter = pdfSeite.locator(".blatt");
  for (let i = 0; i < (await blaetter.count()); i++) {
    await blaetter.nth(i).screenshot({ path: `${process.env.RUNDGANG_PRUEFEN}/blatt-${i}.png` });
  }
  console.log(`  Sichtprüfung: ${await blaetter.count()} Blätter abgelegt`);
}
const ziel = resolve(HIER, "kehler-os-rundgang.pdf");
await pdfSeite.pdf({ path: ziel, width: "297mm", height: "210mm", printBackground: true });
await pdfBrowser.close();

const groesse = readFileSync(ziel).length / 1024 / 1024;
writeFileSync(ziel, readFileSync(ziel));
console.log(`\n${ziel} — ${groesse.toFixed(1)} MB, ${bilder.length + 1} Seiten`);
