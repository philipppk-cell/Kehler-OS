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
  "energy.solar": "Solar",
  "energy.shorePower": "Landstrom",

  // Wasser
  "tank.fresh": "Frischwasser",
  "tank.grey": "Grauwasser",
  "tank.black": "Schwarzwasser",
  "water.pump": "Wasserpumpe",

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

export function t(key: string, fallback?: string): string {
  return de[key] ?? fallback ?? key;
}
