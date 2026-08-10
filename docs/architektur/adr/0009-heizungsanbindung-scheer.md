# ADR 0009 – Anbindung der SCHEER-Heizungsanlage

**Status:** angenommen · Anlage benannt am 2026-08-10
**Bezug:** Kapitel 2 §4, Kapitel 12 §33/§67, Kapitel 13 §60, Kapitel 18 §29/§98/§136
**Bezug intern:** [ADR 0002](0002-plc-transport.md) (Transport zur SPS),
Punkt G1 in [`OPEN_HARDWARE_REQUIREMENTS.md`](../../OPEN_HARDWARE_REQUIREMENTS.md)

## Entscheidung

**Die SCHEER HeatMate bleibt Regler und Schutzeinrichtung. Kehler OS ist
übergeordnete Bedien- und Anzeigeebene und schreibt erst, wenn eine Funktion
gegen das reale Gerät verifiziert ist.**

Die Datenkette ist:

```
SCHEER selection 10/17 kW / HeatMate V4.02
        │  Modbus (bzw. CAN)
        ▼
Siemens S7-1511-1 PN
        │  S7-Kommunikation (PUT/GET) über snap7 — ADR 0002
        ▼
Kehler OS
```

## Kontext

Verbaut ist eine **SCHEER selection 10/17 kW** mit der Steuerung **SCHEER
HeatMate V4.02** (Angabe des Fahrzeughalters vom 2026-08-10). Sie ist die
zentrale Heizungs- und Warmwasseranlage des Fahrzeugs und hat zwei
Wärmequellen: den Brenner und eine Elektroheizung.

Das ist keine Heizung mit Ein/Aus und einem Sollwert. Sie führt zwei
Heizkreise mit eigenen Umwälzpumpen — die Heizkörper im Wohnraum und die
Fußbodenheizung —, bereitet Warmwasser, kennt Nachtabsenkung, eine
Warmwasser-Plus-Funktion, Betriebsarten der Elektroheizung und eine
Wake-up-Funktion für den Wechselrichter.

Sie führt dabei **eine** Temperatur, nicht getrennt nach Kessel und
Warmwasser, und die Elektroheizung hat **drei Stufen: 1 kW, 2 kW, 3 kW**.

Die HeatMate besitzt laut Hersteller CAN und Modbus. **Die Registerliste liegt
nicht vor.**

## Warum Kehler OS nicht regelt

Kapitel 12 §67 und Kapitel 18 §29 verbieten, vorhandene Regelintelligenz
nachzubauen. Bei einer Heizung ist das mehr als eine Stilfrage: Die HeatMate
führt Temperaturbegrenzer, Brennersteuerung, Nachlauf und Abschaltungen. Diese
Kette ist Teil der Zulassung der Anlage. Eine zweite Regelung daneben wäre
nicht redundant, sondern konkurrierend — zwei Instanzen, die dasselbe Ventil
für sich beanspruchen.

Kehler OS gibt deshalb Sollwerte und Freigaben weiter und liest Zustände
zurück. Es fällt keine eigene Entscheidung darüber, ob der Brenner startet.

**Insbesondere gilt:** Keine Schutzfunktion der SCHEER-Anlage wird ersetzt,
nachgebildet oder umgangen. Es gibt keinen „Trotzdem"-Befehl, der eine
Abschaltung überstimmt (Kapitel 18 §136).

## Warum über die SPS und nicht direkt

Der Raspberry Pi könnte Modbus selbst sprechen. Dagegen sprechen drei Punkte:

1. **Eine Quelle je Gerät.** Zwei Master auf demselben Bus — Pi und SPS — sind
   eine Fehlerquelle ohne Gegenwert. Die SPS ist ohnehin die Instanz, die im
   Fahrzeug schaltet.
2. **Der Pi ist nicht die Verfügbarkeitsebene.** Fällt er aus, muss die Heizung
   weiterlaufen. Liegt die Anbindung an der SPS, ist das selbstverständlich;
   läge sie am Pi, wäre die Heizung von einem Linux-Rechner abhängig.
3. **Ein Transportweg statt zwei.** Kehler OS spricht bereits S7 mit der SPS
   (ADR 0002). Ein zweiter Weg mit eigener Fehlerbehandlung, eigenem
   Verbindungszustand und eigener Alterung wäre Aufwand ohne Nutzen.

Der Preis: Die SPS-Projektierung muss die Modbus-Werte in Datenbausteine
legen. Das ist Arbeit im TIA-Portal, aber keine Architekturfrage.

> Ob CAN gegenüber Modbus Vorteile hat, ist offen. Die Entscheidung fällt mit
> der Registerliste — sie ändert nur das erste Glied der Kette, nicht den Rest.

## Was „vorbereitet, aber unbestätigt" konkret heißt

Die Anlage ist in `config/vehicle/vehicle.yaml` **vollständig beschrieben**:
Brenner, Temperatur und Sollwert, Betriebsstunden, zwei Heizkreise mit
Pumpen, Warmwasser samt Plus-Funktion und Zirkulation, Elektroheizung mit
Heizleistung und Betriebsart, 230-V-Versorgung, Wake-up, Tanküberwachung,
Störmeldung, Fehlercode, Wartung.

Jede dieser Entities trägt `unverified: true`. Das ist **kein Kommentar,
sondern wirksam**: Der Loader vergibt an eine unverifizierte Entity keine
Capabilities, und ohne Capability entsteht in der Oberfläche kein
Bedienelement. Die Struktur steht, die Bedienung entsteht mit der Bestätigung.

Ohne diese Regel wäre die Konfiguration eine Wunschliste, aus der die
Oberfläche Schalter baut, hinter denen nichts liegt.

### Drei Zustände, die auseinandergehalten werden

| Kennzeichnung | Bedeutung | Oberfläche |
| --- | --- | --- |
| `unverified: true` | Ob die Funktion über die Schnittstelle verfügbar ist, ist offen | „Noch zu verifizieren", keine Bedienung |
| `configured: false` | Die Funktion existiert, ihr fehlt die Zuordnung | „Nicht konfiguriert", keine Bedienung |
| beides `false` | angebunden | Wert und, wo vorgesehen, Bedienung |

## Der neue Entity-Typ `status`

Der Brenner meldet keine zwei Zustände, sondern eine Betriebsphase: aus,
Anforderung, heizen, Nachlauf, Störung. Ein `contact` könnte „Nachlauf" nicht
von „aus" unterscheiden; ein `switch` würde behaupten, Kehler OS könne die
Phase setzen.

Deshalb `status`: mehrwertig, lesend, ohne Befehle.

Die Zustandsnamen (`HEATING`, `POSTRUN`, …) sind das **interne Vokabular von
Kehler OS**, nicht das der HeatMate. Welcher Registerwert auf welchen Namen
abgebildet wird, entscheidet der Adapter, sobald die Registerliste vorliegt.
Sie stehen in der Konfiguration unter `states`, damit die Simulation sie
kennt — ein Zustand ohne diese Liste wird **nicht** simuliert, weil der
Simulator sonst raten müsste.

## Was daraus für die Oberfläche folgt

Die Seite „Heizung" ist ein Anlagen-Dashboard und kein Raumthermostat. Sie
beantwortet: Welche Wärmequelle arbeitet, welche Kreise laufen, welche
Temperaturen liegen an, liegt eine Störung vor.

Gedeutet wird genau eine Sache — **welche Wärmequelle gerade arbeitet** —, und
zwar im Backend (`core/heating.py`), weil sie zwei Werte verknüpft. Ist eine
der beiden unbekannt, bleibt die Aussage aus: „keine aktiv" wäre dann eine
Behauptung und keine Feststellung (Kapitel 18 §38).

Der Fehlercode wird weitergegeben, nicht gedeutet. Kehler OS stellt keine
Diagnose über eine fremde Anlage (Kapitel 13 §60).

## Konsequenzen

**Positiv**

* Die Trennung von Regelung und Bedienung ist strukturell und nicht nur
  vereinbart — die Software kann gar nicht regeln.
* Die vollständige Anlagenbeschreibung liegt vor, bevor die Registerliste da
  ist. Deren Eintreffen ist eine Konfigurationsänderung, kein Umbau.
* Der Ausfall von Kehler OS lässt die Heizung unberührt.

**Negativ**

* Solange die Registerliste fehlt, zeigt die Seite eine Struktur ohne Werte.
  Das ist ehrlich, aber es sieht nach wenig aus.
* Jeder Wert braucht einen Platz im SPS-Datenbaustein. Die Anbindung ist damit
  aufwendiger als ein direkter Modbus-Zugriff.
* Die Zuordnung Registerwert → Zustandsname muss beim Eintreffen der
  Registerliste sorgfältig gemacht werden. Ein vertauschter Wert wäre hier
  besonders unangenehm, weil er wie ein plausibler Anlagenzustand aussähe.

## Offen

* Modbus-Registerliste der HeatMate V4.02 (Punkt G1) — **blockierend**
* Entscheidung CAN gegen Modbus
* Physikalische Anbindung an die S7-1500 (Modbus-Master-Baugruppe oder
  CM-Modul) und die Aufteilung der Datenbausteine (Punkt A3)
* Welche Funktionen die HeatMate **schreibend** freigibt. Möglicherweise ist
  ein Teil der Anlage dauerhaft nur lesbar — das ist dann kein Mangel,
  sondern die Eigenschaft des Geräts.
