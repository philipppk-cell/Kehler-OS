"""Erkundet den OPC-UA-Server der SPS und schreibt einen Bericht.

Dieses Werkzeug läuft **im Fahrzeugnetz**, nicht auf dem Entwicklungsrechner.
Es beantwortet die beiden Punkte, die eine reale Anbindung noch blockieren:

* **A2 — Zugang.** Welche Sicherheitsrichtlinien bietet der Server an, welche
  Anmeldeverfahren akzeptiert er? Das lässt sich **ohne Anmeldung** abfragen;
  OPC UA sieht dafür einen eigenen Weg vor.
* **A3 — Bedeutung.** Welche Knoten gibt es, wie heißen sie, welchen Datentyp
  haben sie, sind sie schreibbar? Das ersetzt die handgeschriebene Adressliste,
  die es bei PUT/GET noch gebraucht hätte.

Was es **nicht** tut: schreiben. Es liest ausschließlich. Ein Erkundungslauf
darf ein Fahrzeug nicht bewegen.

    pip install asyncua
    python tools/opcua/erkunden.py <endpunkt>

Der Endpunkt steht in `config/hardware/devices.yaml` — Adressen gehören zum
Fahrzeug und nicht in den Quelltext (Kapitel 17 §48).

Der Bericht landet in `opcua-bericht.txt` neben dem Skript und kann
weitergegeben werden. **Zugangsdaten stehen nicht darin** — siehe `_zensiert`.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# asyncua meldet betriebliche Kleinigkeiten auf WARNING — ausgehandelte
# Sitzungszeiten und Ähnliches. In einem Bericht, den jemand lesen soll,
# stehen sie mitten in der Ausgabe und sehen aus wie Befunde. Echte Fehler
# kommen ohnehin als Ausnahme zurück und werden unten behandelt.
logging.getLogger("asyncua").setLevel(logging.ERROR)

try:
    from asyncua import Client, ua
except ImportError:  # pragma: no cover - Hinweis für den Anwender
    print("Fehlt: asyncua.  Installieren mit:  pip install asyncua", file=sys.stderr)
    raise SystemExit(2) from None


# Der Standard-Namensraum ist auf jedem OPC-UA-Server derselbe und enthält
# tausende Knoten der Spezifikation selbst. Ihn mitzudrucken hieße, die zehn
# interessanten Einträge in zehntausend uninteressanten zu vergraben.
STANDARD_NAMESPACE = 0

#: Wie tief gesucht wird. Reicht für die üblichen Datenbausteinstrukturen und
#: verhindert, dass ein Zyklus im Adressraum das Werkzeug endlos laufen lässt.
MAX_TIEFE = 6

#: Wie lange auf den Server gewartet wird, bevor er als nicht erreichbar gilt.
ANTWORTZEIT_S = 10.0


def _fehlertext(fehler: BaseException) -> str:
    """Macht aus einer Ausnahme eine Zeile, die auch etwas aussagt.

    Manche Netzwerkausnahmen tragen keinen Text. `str()` liefert dann eine
    leere Zeichenkette, und im Bericht stünde „Der Server ist nicht
    erreichbar:" — mit nichts dahinter. Der Klassenname ist in dem Fall die
    einzige verbliebene Information und deshalb besser als Schweigen.
    """
    text = str(fehler).strip()
    if isinstance(fehler, asyncio.TimeoutError) and not text:
        return f"keine Antwort innerhalb von {ANTWORTZEIT_S:.0f} s"
    return f"{type(fehler).__name__}: {text}" if text else type(fehler).__name__


class Bericht:
    """Sammelt Zeilen für Bildschirm und Datei zugleich."""

    def __init__(self) -> None:
        self.zeilen: list[str] = []

    def __call__(self, text: str = "") -> None:
        print(text)
        self.zeilen.append(text)

    def schreiben(self, pfad: Path) -> None:
        pfad.write_text("\n".join(self.zeilen) + "\n", encoding="utf-8")


def _zensiert(text: str) -> str:
    """Entfernt Zugangsdaten aus einer Endpunkt-URL.

    Ein Bericht wird weitergegeben. Stünde ein Passwort darin, wäre es genau
    dann öffentlich, wenn jemand hilfsbereit ist (Kapitel 15 §49/§50).
    """
    if "@" not in text:
        return text
    schema, _, rest = text.partition("://")
    _, _, host = rest.rpartition("@")
    return f"{schema}://<zugangsdaten entfernt>@{host}"


# ── Stufe 1: Was bietet der Server an? ──────────────────────────────────────


async def endpunkte_zeigen(url: str, aus: Bericht) -> list:
    """Fragt die Endpunkte ab — ohne Anmeldung und ohne Sitzung.

    Das ist der eigentliche Trick dieses Werkzeugs: OPC UA erlaubt genau diese
    eine Abfrage ungesichert, damit ein Client überhaupt herausfinden kann,
    wie er sich sicher verbinden soll.
    """
    aus("═" * 74)
    aus("STUFE 1 · Was der Server anbietet   (Punkt A2)")
    aus("═" * 74)
    aus()

    client = Client(url=url)
    # Ohne eigene Zeitgrenze bleibt der Aufruf an einer toten Adresse hängen,
    # bis das Betriebssystem die TCP-Verbindung aufgibt — je nach System
    # Minuten. Wer ein Werkzeug startet und nichts sieht, hält es für kaputt.
    endpunkte = await asyncio.wait_for(
        client.connect_and_get_server_endpoints(), timeout=ANTWORTZEIT_S
    )

    aus(f"Der Server meldet {len(endpunkte)} Endpunkt(e).")
    aus()

    unsicher_vorhanden = False

    for nummer, endpunkt in enumerate(endpunkte, start=1):
        policy = endpunkt.SecurityPolicyUri.rsplit("#", 1)[-1]
        # asyncua nennt den Aufzählungswert `None_`, weil `None` in Python
        # belegt ist. Im Bericht steht, was in TIA Portal steht.
        modus = endpunkt.SecurityMode.name.rstrip("_")
        tokens = [t.TokenType.name for t in (endpunkt.UserIdentityTokens or [])]

        if policy == "None" or modus == "None":
            unsicher_vorhanden = True

        aus(f"  [{nummer}] Richtlinie   {policy}")
        aus(f"      Modus        {modus}")
        aus(f"      Anmeldung    {', '.join(tokens) or 'keine angegeben'}")
        aus(f"      URL          {_zensiert(endpunkt.EndpointUrl)}")
        aus()

    aus("─" * 74)
    aus("Bewertung")
    aus("─" * 74)

    brauchbar = [
        e
        for e in endpunkte
        if e.SecurityMode == ua.MessageSecurityMode.SignAndEncrypt
        and "None" not in e.SecurityPolicyUri
    ]

    if brauchbar:
        aus("  ✓ Es gibt mindestens einen Endpunkt mit SignAndEncrypt.")
        aus("    Kehler OS wird genau einen solchen verwenden (ADR 0010).")
    else:
        aus("  ✗ KEIN Endpunkt mit SignAndEncrypt.")
        aus("    Der Server ist dann so offen wie das alte PUT/GET — nur dass")
        aus("    er sicher aussieht. In TIA Portal ist die Sicherheit des")
        aus("    OPC-UA-Servers zu aktivieren, bevor real angebunden wird.")

    if unsicher_vorhanden:
        aus()
        aus("  ! Es gibt zusätzlich einen Endpunkt OHNE Sicherheit.")
        aus("    Der gehört abgeschaltet, sobald die gesicherte Verbindung")
        aus("    steht — sonst bleibt die Hintertür neben der Vordertür offen.")

    anonym = any(
        t.TokenType == ua.UserTokenType.Anonymous
        for e in endpunkte
        for t in (e.UserIdentityTokens or [])
    )
    if anonym:
        aus()
        aus("  ! Anonyme Anmeldung ist erlaubt.")
        aus("    Für den Produktivbetrieb abschalten: Verschlüsselung ohne")
        aus("    Anmeldung schützt gegen Mitlesen, nicht gegen fremde Clients.")

    aus()
    return endpunkte


# ── Stufe 2: Was liegt im Adressraum? ───────────────────────────────────────


async def _knoten_zeile(knoten, tiefe: int) -> str | None:
    """Beschreibt einen Knoten in einer Zeile — oder gar nicht.

    Fehler beim Lesen einzelner Attribute werden **nicht** verschluckt, aber
    sie brechen auch nicht den Lauf ab: Ein Knoten ohne Leserecht ist eine
    Information und kein Grund aufzuhören.
    """
    einzug = "  " * tiefe

    try:
        name = (await knoten.read_browse_name()).Name
    except Exception as fehler:
        return f"{einzug}· {knoten.nodeid.to_string()}  <nicht lesbar: {fehler}>"

    try:
        klasse = await knoten.read_node_class()
    except Exception:
        klasse = None

    if klasse is not ua.NodeClass.Variable:
        return f"{einzug}▸ {name}"

    teile: list[str] = []

    try:
        typ = await knoten.read_data_type_as_variant_type()
        teile.append(typ.name)
    except Exception:
        teile.append("Typ?")

    try:
        zugriff = await knoten.read_attribute(ua.AttributeIds.AccessLevel)
        stufe = zugriff.Value.Value
        rechte = ""
        if stufe & ua.AccessLevel.CurrentRead.mask:
            rechte += "r"
        if stufe & ua.AccessLevel.CurrentWrite.mask:
            rechte += "w"
        teile.append(rechte or "-")
    except Exception:
        teile.append("?")

    # Der aktuelle Wert samt Qualität und Messzeitpunkt.
    #
    # `raise_on_bad_status=False` ist hier wesentlich und kein Detail: Sonst
    # wirft asyncua bei einem defekten Fühler eine Ausnahme, und der Bericht
    # meldete „nicht lesbar" — obwohl der Knoten sehr wohl lesbar ist und
    # exakt das sagt, worauf es ankommt. Ein schlechter StatusCode ist eine
    # **Antwort** und kein Fehler des Werkzeugs (ADR 0010).
    try:
        datenwert = await knoten.read_attribute(
            ua.AttributeIds.Value, raise_on_bad_status=False
        )
        güte = datenwert.StatusCode.name
        if güte == "Good":
            teile.append(f"= {datenwert.Value.Value!r}")
        else:
            # Bei schlechter Qualität liefert der Server keinen Wert. Das ist
            # genau die Regel, nach der auch Kehler OS arbeitet: Was nicht
            # belastbar ist, trägt keine Zahl (Kapitel 18 §38).
            teile.append(f"[{güte}] — kein Wert")
        if datenwert.SourceTimestamp is not None:
            teile.append(f"({datenwert.SourceTimestamp:%H:%M:%S})")
    except Exception as fehler:
        teile.append(f"<nicht lesbar: {type(fehler).__name__}>")

    return f"{einzug}· {name:<28} {knoten.nodeid.to_string():<34} {'  '.join(teile)}"


async def adressraum_zeigen(knoten, aus: Bericht, tiefe: int = 0) -> int:
    """Läuft den Adressraum ab und zählt die gefundenen Variablen."""
    if tiefe > MAX_TIEFE:
        aus("  " * tiefe + "… (Tiefenbegrenzung erreicht)")
        return 0

    gefunden = 0
    try:
        kinder = await knoten.get_children()
    except Exception as fehler:
        aus("  " * tiefe + f"<Kinder nicht lesbar: {fehler}>")
        return 0

    for kind in kinder:
        # Der Standard-Namensraum wird übersprungen. Er ist auf jedem Server
        # gleich und würde das Interessante zudecken.
        if kind.nodeid.NamespaceIndex == STANDARD_NAMESPACE:
            continue

        zeile = await _knoten_zeile(kind, tiefe)
        if zeile is not None:
            aus(zeile)
            if zeile.lstrip().startswith("·"):
                gefunden += 1

        gefunden += await adressraum_zeigen(kind, aus, tiefe + 1)

    return gefunden


# ── Ablauf ──────────────────────────────────────────────────────────────────


async def main(args: argparse.Namespace) -> int:
    aus = Bericht()
    aus(f"Kehler OS · OPC-UA-Erkundung   {datetime.now():%Y-%m-%d %H:%M}")
    aus(f"Ziel: {args.url}")
    aus()

    try:
        endpunkte = await endpunkte_zeigen(args.url, aus)
    except Exception as fehler:
        aus(f"Der Server ist nicht erreichbar — {_fehlertext(fehler)}")
        aus()
        aus("Zu prüfen:")
        aus("  · Ist dieser Rechner im selben Netz wie die SPS?")
        aus("  · Läuft der OPC-UA-Server, und ist er in TIA aktiviert?")
        aus("  · Stimmt der Port? Siemens verwendet üblicherweise 4840.")
        aus.schreiben(args.ausgabe)
        return 1

    aus("═" * 74)
    aus("STUFE 2 · Der Adressraum   (Punkt A3)")
    aus("═" * 74)
    aus()

    client = Client(url=args.url)

    if args.benutzer:
        client.set_user(args.benutzer)
        if args.passwort:
            client.set_password(args.passwort)

    if args.sicherheit:
        await client.set_security_string(args.sicherheit)
    elif not args.unsicher:
        # Kein stiller Rückfall auf eine ungesicherte Verbindung. Ohne diese
        # Regel würde das Werkzeug im Zweifel das Bequeme tun, und niemand
        # merkte, dass die Verschlüsselung nie in Betrieb war (ADR 0010).
        aus("Ohne --sicherheit wird nicht verschlüsselt verbunden.")
        aus()
        aus("Das ist für einen reinen Lesevorgang im eigenen Netz vertretbar,")
        aus("aber es ist eine bewusste Entscheidung und keine Voreinstellung.")
        aus("Wiederholen mit einem von beiden:")
        aus()
        aus("  --unsicher           nur lesen, ohne Verschlüsselung")
        aus('  --sicherheit "Basic256Sha256,SignAndEncrypt,client.der,client.pem"')
        aus()
        aus("Stufe 1 oben genügt bereits, um Punkt A2 zu beantworten —")
        aus("dieser Bericht ist also auch so schon brauchbar.")
        aus.schreiben(args.ausgabe)
        return 0

    try:
        async with client:
            namensraeume = await client.get_namespace_array()
            aus("Namensräume:")
            for index, uri in enumerate(namensraeume):
                markierung = "  (Standard)" if index == STANDARD_NAMESPACE else ""
                aus(f"  ns={index}  {uri}{markierung}")
            aus()

            aus("Adressraum unterhalb von Objects (Standard-Namensraum ausgelassen):")
            aus()
            anzahl = await adressraum_zeigen(client.nodes.objects, aus)
            aus()
            aus(f"{anzahl} Variable(n) gefunden.")
    except Exception as fehler:
        aus(f"Verbindung fehlgeschlagen — {_fehlertext(fehler)}")
        aus()
        if any(
            t.TokenType == ua.UserTokenType.UserName
            for e in endpunkte
            for t in (e.UserIdentityTokens or [])
        ):
            aus("Der Server verlangt eine Anmeldung. Erneut versuchen mit:")
            aus("  --benutzer <name> --passwort <passwort>")
        aus.schreiben(args.ausgabe)
        return 1

    aus()
    aus("─" * 74)
    aus("Was jetzt noch fehlt — und nicht aus dem Adressraum hervorgeht")
    aus("─" * 74)
    aus("  Die **Bedeutung** der Werte. Dass ein Bit `Tor_Auf` heißt, sagt")
    aus('  nicht, ob TRUE „ist offen" oder „fahre auf" bedeutet. Diese')
    aus("  Zuordnung steht im SPS-Programm und wird nicht geraten")
    aus("  (Kapitel 18 §97).")

    aus.schreiben(args.ausgabe)
    return 0


def parse(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Erkundet den OPC-UA-Server der SPS. Liest ausschließlich.",
    )
    p.add_argument(
        "url",
        help="Endpunkt aus config/hardware/devices.yaml, Form opc.tcp://<host>:4840",
    )
    p.add_argument("--benutzer", help="Benutzername, falls der Server einen verlangt")
    p.add_argument("--passwort", help="Passwort — erscheint nicht im Bericht")
    p.add_argument(
        "--sicherheit",
        help="Sicherheitszeichenkette von asyncua, z. B. "
        '"Basic256Sha256,SignAndEncrypt,client.der,client.pem"',
    )
    p.add_argument(
        "--unsicher",
        action="store_true",
        help="Ausdrücklich ohne Verschlüsselung verbinden (nur lesend)",
    )
    p.add_argument(
        "--ausgabe",
        type=Path,
        default=Path(__file__).with_name("opcua-bericht.txt"),
        help="Wohin der Bericht geschrieben wird",
    )
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse(sys.argv[1:])
    code = asyncio.run(main(args))
    print(f"\nBericht geschrieben: {args.ausgabe}")
    raise SystemExit(code)
