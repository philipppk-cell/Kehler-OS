/**
 * Texte.
 *
 * Die Oberfläche ist von Anfang an über Schlüssel angebunden, obwohl zunächst
 * nur Deutsch ausgeliefert wird. Programmlogik hängt nie an einem sichtbaren
 * Text (Kapitel 7 §35, Kapitel 13 §76).
 */

const de: Record<string, string> = {
  // Zustände
  "state.unknown": "Unbekannt",
  "state.unknownHint": "Der tatsächliche Zustand ist derzeit nicht bekannt",
  "state.stale": "Veraltet",
  "state.faulty": "Fehler",
  "state.notConfigured": "Nicht konfiguriert",
  "state.unavailable": "Nicht verfügbar",
  "state.on": "Ein",
  "state.off": "Aus",
  "state.open": "Offen",
  "state.closed": "Geschlossen",
  "state.opening": "Öffnet",
  "state.closing": "Schließt",
  "state.stopped": "Gestoppt",
  "state.blocked": "Blockiert",
  "state.extended": "Ausgefahren",
  "state.retracted": "Eingefahren",
  "state.connected": "Verbunden",
  "state.disconnected": "Getrennt",

  // Navigation
  "nav.dashboard": "Dashboard",
  "nav.light": "Licht",
  "nav.energy": "Energie",
  "nav.water": "Wasser",
  "nav.climate": "Klima",
  "nav.leveling": "Nivellierung",
  "nav.vehicle": "Fahrzeug",
  "nav.cameras": "Kameras",
  "nav.garage": "Garage",
  "nav.settings": "Einstellungen",
  "nav.diagnostics": "Diagnose",

  // Dashboard
  "dash.vehicleStatus": "Fahrzeugstatus",
  "dash.warnings": "Warnungen",
  "dash.noWarnings": "Keine Warnungen",
  "dash.warningsUnknown": "Ohne Verbindung nicht beurteilbar",

  // Warnungstexte. Sie beschreiben, was das System beobachtet hat — nicht,
  // was es vermutet. „Keine Rückmeldung" ist eine Feststellung,
  // „Sensor defekt" wäre eine Diagnose, die Kehler OS nicht stellen kann.
  "alert.notConfigured": "Für diese Funktion ist noch keine Hardware zugeordnet",
  "alert.deviceOffline": "Das Gerät ist derzeit nicht erreichbar",
  "alert.sensorFaulty": "Der gemeldete Wert ist nicht verwertbar",
  "alert.sensorStale": "Seit längerem keine Rückmeldung",
  "alert.sensorLost": "Liefert keine Werte mehr",
  "alert.levelLow": "Nur noch {value} % — Warnschwelle {threshold} %",
  "alert.levelHigh": "Bei {value} % — Warnschwelle {threshold} %",
  "alert.levelCriticalLow": "Kritisch: nur noch {value} % — Grenze {threshold} %",
  "alert.levelCriticalHigh": "Kritisch: bei {value} % — Grenze {threshold} %",

  // Fahrzeugansicht
  "vehicle3d.label": "Fahrzeugansicht mit dem Zustand der Aufbaufunktionen",
  "vehicle3d.dragHint": "Zum Drehen wischen",
  "vehicle3d.reset": "Ansicht zurücksetzen",
  "vehicle3d.resetHint": "Zurück zur Ausgangsansicht",
  "dash.quickAccess": "Schnellzugriff",
  "dash.energy": "Energie",
  "dash.water": "Wasser",
  "dash.climate": "Klima",
  "dash.systemStatus": "Systemstatus",

  // Systemzustand
  "health.HEALTHY": "Alles in Ordnung",
  "health.DEGRADED": "Eingeschränkt",
  "health.WARNING": "Aufmerksamkeit nötig",
  "health.CRITICAL": "Kritisch",
  "health.INITIALIZING": "Startet",

  // Energie
  "energy.battery": "Batterie",
  "energy.voltage": "Spannung",
  "energy.current": "Strom",
  "energy.batteryPower": "Leistung",
  "energy.solar": "Solar",
  "energy.shorePower": "Landstrom",
  "energy.consumption": "Verbrauch",
  "energy.flow": "Energiefluss",
  "energy.inverter": "Wechselrichter",
  "energy.connection": "Anschluss",
  "energy.limit": "Strombegrenzung",

  "energy.battery_soc": "Ladezustand",
  "energy.battery_voltage": "Batteriespannung",
  "energy.battery_current": "Batteriestrom",
  "energy.battery_power": "Batterieleistung",
  "energy.solar_power": "Solarleistung",
  "energy.shore_connected": "Landstromanschluss",
  "energy.shore_power": "Landstromleistung",
  "energy.shore_limit": "Eingangsstrombegrenzung",

  // Laderichtung. „Ruht" ist eine Aussage — bei fehlendem Messwert wird
  // stattdessen „Unbekannt" gezeigt.
  "energy.dir.charging": "Lädt",
  "energy.dir.discharging": "Entlädt",
  "energy.dir.idle": "Ruht",

  "energy.shoreConnected": "Verbunden",
  "energy.shoreDisconnected": "Nicht verbunden",
  "energy.limitNotAdjustable":
    "Einstellbar erst, wenn die Absicherung des Landstromanschlusses bekannt ist. Eine geratene Obergrenze könnte die Zuleitung überlasten.",
  "energy.inverterConfirm":
    "Wechselrichter wirklich abschalten? Damit entfällt die 230-V-Versorgung im gesamten Fahrzeug.",
  "energy.notesTitle": "Hinweise",
  "energy.noRuntime":
    "Eine Restlaufzeit wird nicht angezeigt — dafür fehlt die nutzbare Batteriekapazität.",
  "energy.readOnly":
    "Kehler OS liest die Anlage nur. Geregelt wird sie von Victron; schreibend gibt es ausschließlich Strombegrenzung und Wechselrichter.",

  // Wasser
  "tank.fresh": "Frischwasser",
  "tank.fresh_large": "Frischwasser groß",
  "tank.fresh_small": "Frischwasser klein",
  "tank.grey": "Grauwasser",
  "tank.black": "Schwarzwasser",
  "water.pump": "Wasserpumpe",

  // Wasserseite
  "water.title": "Wasser",
  "water.freshTotal": "Frischwasser gesamt",
  "water.waste": "Abwasser",
  "water.supply": "Versorgung",
  "water.remaining": "verfügbar",
  "water.filled": "belegt",
  "water.capacity": "Fassungsvermögen",
  "water.totalUnknown": "Gesamtstand nicht ermittelbar",
  "water.totalUnknownHint":
    "Solange ein Tank keinen belastbaren Wert liefert, wäre jede Gesamtangabe eine Schätzung.",
  "water.notesTitle": "Hinweise",
  "water.thresholdsSet":
    "Frischwasser: Warnung unter 20 %, kritisch unter 10 %. Abwasser: Warnung über 80 %, kritisch über 90 %.",
  "water.thresholdMarks":
    "Die beiden Markierungen im Balken zeigen, wo die Stufen liegen.",
  "water.historyLater": "Verlauf entsteht in einem späteren Schritt",

  // Klima
  "climate.inside": "Innen",
  "climate.outside": "Außen",
  "climate.target": "Soll",
  "climate.living_actual": "Innentemperatur",
  "climate.living_target": "Solltemperatur",

  // Licht
  "light.living": "Wohnbereich",
  "light.kitchen": "Küche",
  "light.entry": "Außenlicht",
  "light.interior": "Innenbeleuchtung",

  // Fahrzeug
  "vehicle.garage_door": "Garage",
  "vehicle.step": "Stufen",
  "vehicle.awning": "Markise",
  "vehicle.door_main": "Eingangstür",
  "vehicle.doors": "Türen",
  "vehicle.windows": "Fenster",

  // Verbindung
  "conn.connecting": "Verbindung wird aufgebaut",
  "conn.reconnecting": "Verbindung wird wiederhergestellt",
  "conn.offline": "Keine Verbindung zum Fahrzeug",
  "conn.offlineHint": "Die zuletzt bekannten Werte sind nicht mehr aktuell.",

  // Betriebsart
  "env.simulation": "Simulation",
  "env.simulationHint": "Es wird keine reale Fahrzeughardware gesteuert",

  // Befehlsergebnisse
  "cmd.failed": "Befehl konnte nicht ausgeführt werden",
  "cmd.timeout": "Keine Rückmeldung von der Steuerung",
  "cmd.rejected.NOT_CONFIGURED": "Für diese Funktion ist keine Hardware zugeordnet",
  "cmd.rejected.MISSING_CAPABILITY": "Diese Funktion ist hier nicht verfügbar",
  "cmd.rejected.DEVICE_UNAVAILABLE": "Das Gerät ist nicht erreichbar",
  "cmd.rejected.BUSY": "Es läuft bereits ein Vorgang",
  "cmd.rejected.NOT_AUTHORIZED": "Dafür fehlt die Berechtigung",
  "cmd.rejected.SAFETY_CONDITION": "Aus Sicherheitsgründen nicht möglich",

  // Platzhalter für noch nicht gebaute Seiten
  "page.comingSoon": "Dieser Bereich entsteht in einem späteren Schritt.",
};

export function t(
  key: string,
  fallback?: string,
  params?: Record<string, string>,
): string {
  const text = de[key] ?? fallback ?? key;
  if (!params) return text;

  // Platzhalter der Form {name}. Fehlt ein Wert, bleibt der Platzhalter
  // stehen — sichtbar falsch ist besser als eine Lücke, die aussieht, als
  // gehöre sie so.
  return text.replace(/\{(\w+)\}/g, (match, name: string) => params[name] ?? match);
}
