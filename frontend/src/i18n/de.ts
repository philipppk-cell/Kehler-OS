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
  "nav.energy": "Energie",
  "nav.water": "Wasser",
  "nav.climate": "Klima",
  "nav.heating": "Heizung",
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
  // Die Karte fasst zwei getrennte Systeme zusammen und heißt deshalb nach
  // der Größe, nicht nach einem der beiden.
  "dash.temperature": "Temperatur",
  "dash.coolingTarget": "Soll Klima",
  "dash.heatingTarget": "Soll Heizung",
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
  "energy.content": "Energieinhalt",
  "energy.of": "von",
  "energy.atCurrentLoad": "bei aktuellem Verbrauch",
  "energy.limitBounded":
    "Begrenzt auf {min} bis {max} A — die Absicherung des Anschlusses. Höhere Werte weist das System ab.",
  "energy.limitNotAdjustable":
    "Einstellbar erst, wenn die Absicherung des Landstromanschlusses bekannt ist. Eine geratene Obergrenze könnte die Zuleitung überlasten.",
  "energy.inverterConfirm":
    "Wechselrichter wirklich abschalten? Damit entfällt die 230-V-Versorgung im gesamten Fahrzeug.",
  "energy.notesTitle": "Hinweise",
  "energy.noRuntime":
    "Die Restlaufzeit ist eine Hochrechnung des augenblicklichen Verbrauchs, keine Vorhersage. Beim Laden entfällt sie.",
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

  // Sollwertverstellung. Der Name der Größe wird eingesetzt, damit die
  // Sprachausgabe nicht bei jedem Stepper im Fahrzeug „Plus" sagt.
  "stepper.decrease": "{name} verringern",
  "stepper.increase": "{name} erhöhen",

  // Klimaseite
  "klima.system": "System",
  "klima.power": "Ein/Aus",
  "klima.target": "Solltemperatur",
  "klima.notesTitle": "Hinweise",

  // Klima
  "climate.title": "Klima",
  "climate.inside": "Innen",
  "climate.outside": "Außen",
  // Der Name der Entity steht für sich allein — ohne das „Innen" daneben
  // wäre „Außen" kein Name, sondern eine Richtung.
  "climate.outside_actual": "Außentemperatur",
  "climate.living_actual": "Innentemperatur",
  "climate.cooling": "Klimaanlage",
  "climate.cooling_target": "Solltemperatur Klima",
  "climate.noteSeparate":
    "Klima und Heizung sind getrennte Systeme mit eigenen Geräten und eigenen Sollwerten. Was hier eingestellt wird, gilt nicht für die Heizung.",
  "climate.noteDevice":
    "Der einstellbare Bereich ist vorläufig, solange das verbaute Gerät nicht bekannt ist. Betriebsarten zeigt Kehler OS erst, wenn das Gerät sie meldet — nachgebaut wird keine.",

  // ── Heizung: SCHEER selection 10/17 kW mit HeatMate V4.02 ────────────────
  "heating.title": "Heizung",
  "heating.plant": "SCHEER selection 10/17 kW",
  "heating.controller": "HeatMate V4.02",

  // Namen der Entities. Sie stehen in der Fahrzeugkonfiguration und werden
  // hier übersetzt — die Seite selbst kennt keine festen Beschriftungen.
  "heating.system": "Heizungsanlage",
  "heating.fault": "Störung",
  "heating.error_code": "Fehlercode",
  "heating.burner": "Brenner",
  "heating.burner_hours": "Brennerlaufzeit",
  "heating.service": "Wartung",

  // Eine Temperatur, ein Sollwert — Kessel und Warmwasser werden von der
  // Anlage nicht getrennt geführt. Deshalb schlicht „Temperatur": Wo der
  // Fühler sitzt, ist nicht genannt und wird nicht behauptet.
  "heating.temperature_actual": "Temperatur",
  "heating.temperature_target": "Solltemperatur",

  // Die Kreise heißen nach dem, was sie beheizen. „Heizkreis 2" steht im
  // Schaltplan, „Fußbodenheizung" im Fahrzeug (Kapitel 7 §31).
  "heating.radiators": "Heizkörper",
  "heating.floor": "Fußbodenheizung",
  "heating.pump": "Pumpe",
  "heating.night": "Nachtabsenkung",
  "heating.water": "Warmwasserbereitung",
  "heating.water_plus": "Warmwasser Plus",
  "heating.circulation": "Zirkulationspumpe",
  "heating.electric": "Elektroheizung",
  // Stufe und Leistung sind dasselbe: Stufe 2 ist 2 kW.
  "heating.electric_power": "Heizleistung",
  "heating.electric_mode": "Betriebsart",
  "heating.mains": "230-V-Versorgung",
  "heating.wakeup": "Wechselrichter-Wake-up",
  "heating.tank": "Tankfüllstand Heizung",

  // Abschnitte der Seite
  "heating.plantTitle": "Anlage",
  "heating.circuitsTitle": "Heizkreise",
  "heating.waterTitle": "Warmwasser",
  "heating.electricTitle": "Elektroheizung",
  "heating.burnerTitle": "Brenner",
  "heating.supplyTitle": "Versorgung",
  "heating.linkTitle": "Anbindung",
  "heating.notesTitle": "Hinweise",

  // Wärmequelle — die eine Frage, die die Seite beantworten soll
  "heating.source": "Wärmequelle",
  "heating.source.burner": "Brenner",
  "heating.source.electric": "Elektro",
  "heating.source.both": "Brenner und Elektro",
  "heating.source.none": "Keine aktiv",

  // Brennerphasen. Das interne Vokabular von Kehler OS — welcher Wert der
  // HeatMate darauf abgebildet wird, entscheidet der Adapter.
  "heating.phase.OFF": "Aus",
  "heating.phase.DEMAND": "Anforderung",
  "heating.phase.HEATING": "Heizt",
  "heating.phase.POSTRUN": "Nachlauf",
  "heating.phase.FAULT": "Störung",

  // Ein Versorgungskontakt ist kein Türkontakt. „Geschlossen" wäre technisch
  // richtig und trotzdem unverständlich — hier zählt, ob Strom anliegt.
  "heating.mains.CLOSED": "Vorhanden",
  "heating.mains.OPEN": "Fehlt",

  "heating.service.OK": "Keine Wartung fällig",
  "heating.service.DUE": "Wartung fällig",

  "heating.mode.SOLO": "Solo",
  "heating.mode.HYBRID": "Hybrid",
  "heating.mode.FALLBACK": "Rückfall",

  "heating.faultPresent": "Störung gemeldet",
  "heating.faultNone": "Keine Störung gemeldet",
  "heating.faultUnknown": "Ohne Anbindung nicht beurteilbar",

  // Stand der Anbindung
  "heating.notLinked": "Anlage noch nicht angebunden",
  "heating.notLinkedHint":
    "Die Anlage ist beschrieben, aber es fließen noch keine Werte. Die Modbus-Registerliste der HeatMate liegt nicht vor — welcher Wert unter welcher Adresse liegt, ist offen.",
  "heating.pendingCount": "{count} Funktionen warten auf ihre Bestätigung",
  "heating.chain": "SCHEER selection / HeatMate → Modbus → Siemens S7-1500 → Kehler OS",

  "state.unverified": "Noch zu verifizieren",
  "state.unverifiedHint":
    "Ob diese Funktion über die Schnittstelle verfügbar ist, ist nicht bestätigt",

  "heating.noteControl":
    "Die HeatMate bleibt Regler und Schutzeinrichtung. Temperaturbegrenzer, Brennersteuerung und Abschaltungen gehören ihr — Kehler OS bedient und zeigt an, es regelt nicht.",
  "heating.noteVerify":
    "Solange eine Funktion nicht bestätigt ist, gibt es dafür kein Bedienelement. Die Struktur steht bereits; ein Schalter entsteht erst, wenn das zugehörige Register bekannt und geprüft ist.",
  "heating.noteSource":
    "Welche Wärmequelle arbeitet, wird aus Brennerphase und Elektroheizung zusammen bestimmt. Ist eine von beiden unbekannt, bleibt die Aussage aus — „keine aktiv“ wäre dann eine Behauptung.",

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
