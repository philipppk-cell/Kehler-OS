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
  "nav.cabinets": "Schränke",
  // „Garage" hatte einen eigenen Reiter. Er ist entfallen: Dahinter lag genau
  // ein Tor, und das steht vollständig auf der Fahrzeugseite. Ein Reiter, der
  // eine Zeile zeigt, verspricht einen Bereich, den es nicht gibt.
  //
  // „Kameras" ebenso, und noch eindeutiger: Das Fahrzeug hat keine
  // (BESTÄTIGT 2026-08-12). Der Reiter führte auf eine leere Platzhalterseite.
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
  "alert.motionBlocked": "Bewegung blockiert — Endlage nicht erreicht",
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
  "valve.grey": "Ablassventil Grauwasser",
  "valve.black": "Ablassventil Schwarzwasser",

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
  // Ablassventile. Eigene Beschriftungen und nicht die des Fahrzeugs: Dort
  // heißt „Öffnen" eine Klappe aufzufahren, hier Wasser abzulassen. Gleiche
  // Wörter für verschiedene Vorgänge sind eine Einladung zum Vertippen.
  "water.drain": "Ablassen",
  "water.valveOpen": "Ventil öffnen",
  "water.valveClose": "Ventil schließen",
  // „Läuft ab" und die beiden „…befohlen"-Schlüssel standen hier. Sie sind
  // nach `actuator.*` gewandert: Dieselbe Aussage gilt für Ventile,
  // Schrankverriegelungen und die Heckklappe, und dreimal nebeneinander
  // wären es drei Gelegenheiten auseinanderzulaufen.
  "water.confirmDrain":
    "{name} wirklich öffnen? Der Tank entleert sich dorthin, wo das Fahrzeug gerade steht.",
  "water.valveNote":
    "Das Öffnen verlangt eine Bestätigung, das Schließen nicht — der Rückweg darf nie schwerer sein als der Hinweg.",
  "water.valveNoFeedback":
    "Die Ablassventile melden ihre Stellung nicht zurück. Angezeigt wird der zuletzt gesendete Befehl, nicht die tatsächliche Stellung — Kehler OS kann sie nicht kennen.",

  "water.notesTitle": "Hinweise",
  "water.thresholdsSet":
    "Frischwasser: Warnung unter 20 %, kritisch unter 10 %. Abwasser: Warnung über 80 %, kritisch über 90 %.",
  "water.thresholdMarks":
    "Die beiden Markierungen im Balken zeigen, wo die Stufen liegen.",
  "water.historyLater": "Verlauf entsteht in einem späteren Schritt",

  // Aktoren ohne Rückmeldung. „Befohlen" und nicht „offen": Kehler OS kennt
  // die Stellung nicht, es kennt nur den letzten Befehl (Kapitel 18 §37).
  "actuator.openCommanded": "Öffnen befohlen",
  "actuator.closeCommanded": "Schließen befohlen",

  // Schränke
  "cabinet.group1": "Schrankgruppe 1",
  "cabinet.group2": "Schrankgruppe 2",
  "cabinet.group3": "Schrankgruppe 3",
  "cabinet.title": "Zentralverriegelung",
  "cabinet.unlock": "Öffnen",
  "cabinet.lock": "Verriegeln",
  "cabinet.confirm": "{name} wirklich öffnen?",
  "cabinet.notesTitle": "Hinweise",
  "cabinet.notePurpose":
    "Die Verriegelung hält die Schränke während der Fahrt zu. Vor dem Losfahren verriegeln.",
  "cabinet.noteNoFeedback":
    "Die Verriegelung meldet ihre Stellung nicht zurück. Angezeigt wird der zuletzt gesendete Befehl, nicht der tatsächliche Zustand.",
  "cabinet.noteNoAuto":
    "Es wird nicht selbsttätig verriegelt. Kehler OS erkennt den Fahrtbeginn nicht, und eine Automatik, die nicht auslöst, ist schlimmer als keine.",

  // Zeitangaben. Unter einer Minute keine Zahl — eine gerundete Null sähe
  // aus wie eine Angabe. Ab einer Stunde die Uhrzeit statt der Dauer, damit
  // niemand rechnen muss.
  "time.justNow": "gerade eben",
  "time.minutesAgo": "vor {n} min",
  "time.at": "um {time}",

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
  "climate.cooling": "Klimaanlage LG",
  "climate.cooling_target": "Solltemperatur Klima",
  "climate.noteSeparate":
    "Klima und Heizung sind getrennte Systeme mit eigenen Geräten und eigenen Sollwerten. Was hier eingestellt wird, gilt nicht für die Heizung.",
  "climate.noteDevice":
    "Verbaut ist eine wandmontierte LG-Anlage. Sie ist noch nicht an die Steuerung angebunden — auf welchem Weg das geschehen soll, ist offen. Bis dahin gibt es hier keine Bedienung, sondern nur die Beschreibung.",
  "climate.noteRange":
    "Der einstellbare Bereich ist vorläufig und wird mit der Anbindung geprüft. Betriebsarten zeigt Kehler OS erst, wenn das Gerät sie meldet — nachgebaut wird keine.",

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

  // Fahrzeugseite
  "vehicle.title": "Fahrzeug",
  "vehicle.movingParts": "Bewegliche Teile",
  "vehicle.sensors": "Sensoren",
  "vehicle.notesTitle": "Hinweise",
  "vehicle.open": "Öffnen",
  "vehicle.close": "Schließen",
  "vehicle.stop": "Stopp",
  "vehicle.confirmMove":
    "{name} wirklich bewegen? Achte darauf, dass niemand und nichts im Weg ist.",
  "vehicle.noteStop":
    "Der Stopp wirkt jederzeit — auch mitten in der Bewegung. Er wird nie deshalb gesperrt, weil gerade etwas fährt.",
  "vehicle.noteMissing":
    "Fenster und Verriegelungen fehlen hier, weil es dafür keine angebundenen Geber gibt. Was nicht gemeldet wird, erscheint nicht.",
  "vehicle.noteNoReadiness":
    "Es gibt bewusst keine Gesamtbewertung „abfahrbereit“. Die Einzelzustände stehen vollständig da; die Ja/Nein-Zusammenfassung wäre eine Bewertung, für die Kehler OS nicht geradestehen kann.",

  // Fahrzeug
  "vehicle.garage_door": "Garage",
  "vehicle.step": "Stufen",
  "vehicle.awning": "Markise",
  "vehicle.door_main": "Eingangstür",
  "vehicle.doors": "Türen",
  "vehicle.windows": "Fenster",

  // Verbindung
  "boot.starting": "SYSTEM STARTET",
  "conn.online": "Mit dem Fahrzeug verbunden",
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
  // Nur in der Demo-Datei. Dort gibt es kein Fahrzeug, keine Steuerung und
  // keinen Adapter — jeder Befehl wird abgewiesen, und zwar über denselben
  // Weg wie eine echte Ablehnung, statt stumm zu verschwinden.
  "cmd.rejected.DEMO": "Demo-Ansicht — hier wird nichts geschaltet",
  "cmd.rejected.MISSING_CAPABILITY": "Diese Funktion ist hier nicht verfügbar",
  "cmd.rejected.DEVICE_UNAVAILABLE": "Das Gerät ist nicht erreichbar",
  "cmd.rejected.BUSY": "Es läuft bereits ein Vorgang",
  "cmd.rejected.NOT_AUTHORIZED": "Dafür fehlt die Berechtigung",
  "cmd.rejected.SAFETY_CONDITION": "Aus Sicherheitsgründen nicht möglich",
  // Die Bewegung hat geantwortet — nur nicht mit dem Ziel.
  "cmd.ended.BLOCKED": "Die Bewegung wurde blockiert und angehalten",
  "cmd.ended.STOPPED": "Die Bewegung wurde gestoppt",

  // ── Diagnose ─────────────────────────────────────────────────────────
  // Die einzige Seite, auf der technische Begriffe stehen dürfen
  // (Kapitel 7 §43). Sie werden trotzdem übersetzt: „Nicht erreichbar" ist
  // auch für den, der die Anlage baut, verständlicher als „OFFLINE" — und
  // die Kennung steht ohnehin daneben.
  "diag.system": "System",
  "diag.version": "Version",
  "diag.environment": "Betriebsart",
  "diag.health": "Zustand",
  "diag.entities": "Entities",
  "diag.unconfigured": "Nicht konfiguriert",
  "diag.unverified": "Zu verifizieren",
  "diag.stateVersion": "Zustandsversion",

  "diag.services": "Dienste",
  "diag.restarts": "{count} Neustarts",
  "diag.adapters": "Adapter",
  "diag.adapterEntities": "{count} Entities",
  "diag.noAdapters": "Kein Adapter aktiv — es fließen keine Werte",
  "diag.alerts": "Meldungen",
  "diag.alertCountHint": "Störungen von Meldungen insgesamt — der Rest sind Hinweise",

  "diag.entityList": "Entities",
  "diag.searchHint": "Nach Name oder Kennung suchen",
  "diag.scope": "Auswahl",
  "diag.scopeAll": "Alle",
  "diag.scopeIssues": "Auffällig",
  "diag.scopeOpen": "Offen",
  "diag.noMatch": "Keine Entity passt zu dieser Auswahl",

  "diag.colName": "Name",
  "diag.colId": "Kennung",
  "diag.colLink": "Verbindung",
  "diag.colQuality": "Qualität",
  "diag.colValue": "Wert",
  "diag.colSource": "Quelle",
  "diag.colLag": "Rückstand",
  "diag.lagNote":
    "Der Rückstand vergleicht den Zeitstempel eines Wertes mit dem jüngsten Zeitstempel des Systems — nicht mit der Uhr dieses Geräts. Beide Uhren gehen im Fahrzeug regelmäßig auseinander. Gedämpft heißt: Für diese Entity werden gar keine regelmäßigen Meldungen erwartet, ein stehender Zeitstempel ist dort normal. Hervorgehoben heißt: Das erwartete Intervall ist überschritten.",
  "diag.lagNoInterval": "Für diese Entity wird keine regelmäßige Meldung erwartet",
  "diag.lagExpected": "Erwartet alle {seconds} s",

  // Verbindungszustände
  "link.INITIALIZING": "Startet",
  "link.ONLINE": "Verbunden",
  "link.DEGRADED": "Eingeschränkt",
  "link.RECONNECTING": "Verbindet neu",
  "link.OFFLINE": "Nicht erreichbar",
  "link.ERROR": "Fehler",
  "link.UNKNOWN": "Unbekannt",
  "link.NOT_CONFIGURED": "Nicht konfiguriert",

  // Wertqualität
  "quality.VALID": "Gültig",
  "quality.STALE": "Veraltet",
  "quality.UNKNOWN": "Unbekannt",
  "quality.INVALID": "Unplausibel",
  "quality.ERROR": "Fehler",

  // Dienstzustände
  "service.STOPPED": "Gestoppt",
  "service.STARTING": "Startet",
  "service.RUNNING": "Läuft",
  "service.RESTARTING": "Startet neu",
  "service.FAILED": "Dauerhaft gestört",

  // Dringlichkeit
  "severity.INFO": "Hinweis",
  "severity.NOTICE": "Beachten",
  "severity.WARNING": "Warnung",
  "severity.CRITICAL": "Kritisch",

  // Betriebsarten
  "env.development": "Entwicklung",
  "env.production": "Produktivbetrieb",

  // Simulationswerkzeuge
  "diag.simTitle": "Simulation — Fehlerbilder auslösen",
  "diag.simHint":
    "Diese Werkzeuge gibt es ausschließlich in der Simulation. Sie erreichen keine reale Fahrzeughardware; im Produktivbetrieb sind sie nicht vorhanden.",
  "diag.simSelected": "Ausgewählt",
  "diag.simNoSelection": "Zeile in der Tabelle antippen",
  "diag.simFault": "Fehlerbild",
  "diag.simLevel": "Wert setzen",
  "diag.simApply": "Übernehmen",
  "diag.simDone": "Übernommen",
  "diag.simNotSimulated":
    "Diese Entity wird nicht simuliert — dafür lässt sich kein Fehlerbild auslösen.",
  "diag.simNotSettable":
    "Nur Mess- und Sollwerte lassen sich auf einen Stand setzen.",

  "sim.fault.NONE": "Zurücknehmen",
  "sim.fault.SENSOR_INVALID": "Unplausibel",
  "sim.fault.SENSOR_ERROR": "Sensorfehler",
  "sim.fault.SILENT": "Verstummt",
  "sim.fault.BLOCKED": "Blockiert",

  // ── Historie ─────────────────────────────────────────────────────────
  "history.title": "Verlauf",
  "history.metric": "Messgröße",
  "history.span": "Zeitraum",
  "history.span6h": "6 Std",
  "history.span24h": "24 Std",
  "history.span7d": "7 Tage",
  "history.span30d": "30 Tage",
  "history.loading": "Wird geladen …",
  "history.empty": "Für diesen Zeitraum liegen keine Werte vor",
  // Der Unterschied ist wesentlich: „keine Werte" ist eine Aussage über den
  // Zeitraum, „nicht verfügbar" eine über die Datenhaltung. Eine leere Kurve
  // für beides zu zeigen, hieße einen Ausfall wie Ruhe aussehen zu lassen.
  "history.unavailable": "Historie derzeit nicht verfügbar",
  "history.chartLabel": "Verlauf der ausgewählten Messgröße",
  "history.pointCount": "{count} Punkte",
  "history.resolution.raw": "Einzelwerte",
  "history.resolution.minute": "Minutenmittel",
  "history.resolution.hour": "Stundenmittel",

  // ── Einstellungen ────────────────────────────────────────────────────
  "settings.display": "Anzeige",
  "settings.displayScope":
    "Diese Einstellungen gelten für dieses Gerät und betreffen nur die Darstellung. Sie erreichen keine Fahrzeugfunktion und gelten nicht für andere Bildschirme.",

  "settings.night": "Nachtmodus",
  "settings.nightHint":
    "Dämpft Helligkeit und Leuchten. Kritische Warnungen behalten ihre Farbe und bleiben auch nachts erkennbar.",

  "settings.keepAwake": "Bildschirm wach halten",
  "settings.keepAwakeHint":
    "Verhindert, dass der Bildschirm abschaltet, solange Kehler OS sichtbar ist. Das Betriebssystem kann die Sperre jederzeit zurücknehmen — die Anzeige daneben sagt, ob sie gerade steht.",
  "settings.awake.held": "Aktiv",
  "settings.awake.idle": "Nicht aktiv",
  // Abgelehnt ist nicht dasselbe wie aus: Wer nach dem Umlegen nur „nicht
  // aktiv" liest, sucht den Fehler bei sich.
  "settings.awake.denied": "Vom Gerät abgelehnt",
  "settings.awake.unsupported": "Von diesem Browser nicht unterstützt",
  "settings.awake.insecure":
    "Nur über eine gesicherte Verbindung verfügbar (HTTPS) — siehe offener Punkt I3",

  "settings.reset": "Anzeigeeinstellungen zurücksetzen",

  "settings.vehicle": "Fahrzeug",
  "settings.vehicleScope":
    "Die Fahrzeugbeschreibung wird beim Start aus der Konfiguration gelesen und ist hier nur einsehbar. Sie ist keine Vorliebe, sondern eine Eigenschaft der Anlage — geändert wird sie in der Konfigurationsdatei.",
  "settings.vehicleName": "Bezeichnung",
  "settings.areas": "Bereiche",
  "settings.configuredValues": "Hinterlegte Werte",

  "settings.capacityL": "{value} L",
  "settings.capacityAh": "{value} Ah",
  "settings.nominalV": "{value} V nominal",
  "settings.range": "{min} bis {max} {unit}",
  "settings.warnBelow": "Warnung unter {value} %",
  "settings.warnAbove": "Warnung über {value} %",
  "settings.criticalBelow": "Kritisch unter {value} %",
  "settings.criticalAbove": "Kritisch über {value} %",

  "settings.missingTitle": "Was hier bewusst fehlt",
  "settings.missingIntro":
    "Kapitel 6 nennt eine Reihe möglicher Einstellungen. Die folgenden gibt es nicht — nicht weil sie vergessen wurden, sondern weil ein Bedienelement ohne Wirkung schlimmer ist als keines.",

  "settings.miss.language": "Sprache",
  "settings.miss.languageWhy":
    "Die Oberfläche ist vollständig über Schlüssel angebunden, ausgeliefert wird aber nur Deutsch. Eine Auswahl mit einem Eintrag ist keine Auswahl.",
  "settings.miss.units": "Einheiten",
  "settings.miss.unitsWhy":
    "Das System rechnet durchgehend metrisch. Eine zweite Einheitenwelt gibt es nicht, also auch keinen Umschalter dafür.",
  "settings.miss.brightness": "Displayhelligkeit",
  "settings.miss.brightnessWhy":
    "Die Hintergrundbeleuchtung des Tablets ist aus dem Browser nicht erreichbar. Was möglich ist, ist die gedämpfte Darstellung — das ist der Nachtmodus oben.",
  "settings.miss.theme": "Helles Thema",
  "settings.miss.themeWhy":
    "Die dunkle Oberfläche ist der vorgesehene Zustand und keine Option (Kapitel 7 §3). Ein zweites Farbschema müsste jede Farbe auf Kontrast neu belegen.",
  "settings.miss.time": "Zeitformat",
  "settings.miss.timeWhy":
    "Datum und Uhrzeit folgen der deutschen Schreibweise. Ein Umschalter auf ein Format, das hier niemand benutzt, wäre eine Einstellung um ihrer selbst willen.",
  "settings.miss.notify": "Benachrichtigungen",
  "settings.miss.notifyWhy":
    "Es gibt noch keine Zustellung außerhalb der Oberfläche. Warnungen erscheinen im Dashboard und in der Diagnose.",
  "settings.miss.network": "Netzwerk",
  "settings.miss.networkWhy":
    "Adressen und Zugangsdaten stehen in der nicht versionierten Hardwarekonfiguration und werden nicht über die Oberfläche verwaltet (Kapitel 18 §97).",
  "settings.miss.automation": "Automatisierungen",
  "settings.miss.automationWhy":
    "Entsteht als eigener Bereich mit M6 — dort gehört mehr hin als ein Schalter.",
  "settings.miss.users": "Benutzer und Berechtigungen",
  "settings.miss.usersWhy":
    "Entsteht mit M7. Bis dahin gibt es keine Benutzer, also auch keine benutzerbezogenen Einstellungen — die Anzeigeeinstellungen oben gehören deshalb dem Gerät.",

  // Bereiche des Fahrzeugs
  "area.cab": "Fahrerhaus",
  "area.living": "Wohnraum",
  "area.kitchen": "Küche",
  "area.bedroom": "Schlafbereich",
  "area.bathroom": "Bad",
  "area.garage": "Garage",
  "area.tech": "Technik",
  "area.exterior": "Außen",

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
