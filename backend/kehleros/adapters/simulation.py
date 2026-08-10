"""Hardware-Simulation.

Kehler OS muss vollständig ohne das reale Fahrzeug entwickelt und getestet
werden können (Kapitel 18 §63). Der Simulator ist deshalb kein Attrappen-Modus,
sondern eine gleichrangige Implementierung von :class:`Adapter`.

Er liefert ausdrücklich **auch Fehlerbilder** — eine Simulation, die nur den
Normalfall kennt, ist wertlos (Kapitel 18 §65). Über :meth:`inject` lassen sich
Sensorausfall, ungültige Werte, blockierte Mechanik und Verbindungsverlust
gezielt auslösen.

Alle hier erzeugten Werte tragen die Quelle ``SIMULATION`` und sind damit im
gesamten System als simuliert erkennbar (Kapitel 18 §66).
"""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass, field
from enum import StrEnum

from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..core.state_store import StateStore
from ..domain.enums import Quality, Source
from ..domain.models import Command, CommandSpec, Entity, StateValue, utcnow
from .base import Adapter

log = logging.getLogger(__name__)


class Fault(StrEnum):
    """Gezielt auslösbare Fehlerbilder."""

    NONE = "NONE"
    SENSOR_INVALID = "SENSOR_INVALID"
    """Sensor liefert physikalisch unmögliche Werte."""

    SENSOR_ERROR = "SENSOR_ERROR"
    """Sensor meldet einen Defekt, etwa Kabelbruch."""

    SILENT = "SILENT"
    """Sensor liefert gar nichts mehr — der Wert altert zu STALE und UNKNOWN."""

    BLOCKED = "BLOCKED"
    """Mechanik bleibt stehen, der Zielzustand wird nie erreicht."""


class Motion(StrEnum):
    """Zustände eines beweglichen Aufbauteils."""

    CLOSED = "CLOSED"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    STOPPED = "STOPPED"
    BLOCKED = "BLOCKED"


def _range_key(entity: Entity) -> str:
    """Ordnet einer Entity ihren plausiblen Wertebereich zu.

    Die Einheit allein genügt nicht. Solarertrag, Landstrombezug und
    Hausverbrauch sind alle drei Watt, bewegen sich aber in völlig
    verschiedenen Größenordnungen — würfelte man für alle denselben Bereich,
    entstünde ein Bild, in dem 640 W Solar auf 640 W Verbrauch treffen und
    nichts auffällt.
    """
    if entity.unit == "celsius":
        return "celsius.outside" if "outside" in entity.id else "celsius.inside"
    if entity.unit == "W":
        if "solar" in entity.id:
            return "W.solar"
        if "shore" in entity.id:
            return "W.shore"
        if "consumption" in entity.id:
            return "W.load"
    return entity.unit or ""


# Plausible Bereiche je Einheit: (min, max, Startwert, Drift pro Sekunde).
# Die Zahlen beschreiben ausschließlich die Simulation. Reale Kapazitäten,
# Schwellen und Nennwerte kommen aus der Konfiguration und werden hier
# ausdrücklich nicht vorweggenommen (Kapitel 18 §98).
_RANGES: dict[str, tuple[float, float, float, float]] = {
    "percent": (0.0, 100.0, 62.0, 0.04),
    "celsius.inside": (14.0, 28.0, 21.5, 0.004),
    "celsius.outside": (-8.0, 34.0, 12.0, 0.006),
    "V": (22.0, 29.0, 26.2, 0.002),   # 24-V-System
    "A": (-120.0, 120.0, -8.0, 0.05),
    # Zehn Module auf dem Dach; die Spitze liegt bei klarem Himmel und guter
    # Ausrichtung in dieser Größenordnung.
    "W.solar": (0.0, 2600.0, 820.0, 3.0),
    # Landstrom: begrenzt durch die Absicherung des Anschlusses. Der Bereich
    # ist eine Annahme für die Simulation, keine Aussage über die Anlage —
    # die reale Absicherung ist offener Punkt B2.
    "W.shore": (0.0, 3600.0, 1150.0, 2.0),
    "W.load": (80.0, 1800.0, 430.0, 1.5),
    "W": (0.0, 2000.0, 640.0, 1.2),
}


@dataclass
class _Device:
    """Ein simuliertes Gerät."""

    entity: Entity
    kind: str
    value: object = None
    fault: Fault = Fault.NONE
    target: object = None
    progress: float = 0.0
    travel_s: float = 6.0
    drift: float = 0.0
    bounds: tuple[float, float] = (0.0, 100.0)
    history: list[float] = field(default_factory=list)


class SimulationAdapter(Adapter):
    """Erzeugt plausible Fahrzeugzustände und auf Wunsch Fehlerbilder."""

    name = "simulation"
    source = Source.SIMULATION

    def __init__(
        self,
        state: StateStore,
        events: EventBus,
        registry: Registry,
        *,
        entity_ids: list[str] | None = None,
        seed: int | None = None,
        poll_interval_s: float = 1.0,
    ) -> None:
        ids = entity_ids if entity_ids is not None else [e.id for e in registry]
        super().__init__(state, events, entity_ids=ids, poll_interval_s=poll_interval_s)
        self._registry = registry
        self._random = random.Random(seed)
        self._devices: dict[str, _Device] = {}
        self._last_tick = utcnow()

    # ── Aufbau ──────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        for entity_id in self.entity_ids:
            entity = self._registry.get(entity_id)
            if entity is None or not entity.configured:
                continue
            self._devices[entity_id] = self._build(entity)
        log.info("Simulation gestartet mit %d Geräten", len(self._devices))

    def _build(self, entity: Entity) -> _Device:
        """Leitet das Verhalten aus den Fähigkeiten der Entity ab.

        Bewusst aus den Capabilities abgeleitet und nicht fest verdrahtet:
        Damit verhält sich der Simulator automatisch richtig, wenn später
        eine Entity dazukommt.
        """
        caps = set(entity.capabilities)

        if {"open", "close"} <= caps:
            return _Device(entity=entity, kind="motion", value=Motion.CLOSED.value)

        if "set_state" in caps:
            return _Device(entity=entity, kind="switch", value="OFF")

        if "set_target" in caps:
            return _Device(
                entity=entity, kind="setpoint", value=20.0, bounds=(5.0, 30.0)
            )

        # Ein Kontakt ist binär, kein Zahlenwert.
        if entity.unit is None and not caps:
            return _Device(entity=entity, kind="contact", value="CLOSED")

        # Ein Sollwert steht, er driftet nicht. Erkennbar an den
        # konfigurierten Grenzen — auch dann, wenn er mangels bekannter
        # Obergrenze (noch) keinen Befehl hat und deshalb wie ein Messwert
        # aussieht.
        if entity.min_value is not None or entity.step is not None:
            # Der Startwert ist eine Zahl für die Simulation, keine Antwort
            # auf eine offene Hardwarefrage. Dass die Strombegrenzung hier
            # einen plausiblen Wert zeigt, heißt nicht, dass die reale
            # Absicherung bekannt wäre — sie ist weiterhin Punkt B2.
            start = entity.min_value if entity.min_value is not None else 0.0
            return _Device(
                entity=entity,
                kind="setpoint",
                value=float(entity.max_value or start + 13),
                bounds=(
                    float(entity.min_value if entity.min_value is not None else 0),
                    float(entity.max_value or 63),
                ),
            )

        # Messwerte richten sich nach ihrer Einheit. Ein Simulator, der für
        # Temperatur, Spannung und Füllstand denselben Bereich würfelt,
        # erzeugt unbrauchbare Bilder — und verdeckt damit genau die
        # Darstellungsfehler, die er sichtbar machen soll.
        low, high, start, drift = _RANGES.get(
            _range_key(entity), (0.0, 100.0, 55.0, 0.05)
        )
        return _Device(
            entity=entity,
            kind="measure",
            value=start + self._random.uniform(-2.0, 2.0),
            drift=drift,
            bounds=(low, high),
        )

    # ── Zyklus ──────────────────────────────────────────────────────────────

    async def poll(self) -> None:
        now = utcnow()
        elapsed = (now - self._last_tick).total_seconds()
        self._last_tick = now

        for device in self._devices.values():
            if device.fault is Fault.SILENT:
                # Nichts senden. Der Wert altert im State Store von selbst zu
                # STALE und dann UNKNOWN — genau wie bei einem echten
                # verstummten Sensor.
                continue

            value = self._advance(device, elapsed)
            self._state.apply(device.entity.id, value)

        self._couple_energy()

    def _couple_energy(self) -> None:
        """Bringt die Energiewerte miteinander in Einklang.

        Würde jeder Wert für sich driften, zeigte der Energiefluss eine
        Anlage, in der Solar, Landstrom, Batterie und Verbrauch nichts
        miteinander zu tun haben. Genau die Darstellungsfehler, die ein
        Energiefluss sichtbar machen soll, wären dann nicht mehr von der
        Unordnung der Simulation zu unterscheiden.

        Physik ist hier bewusst einfach gehalten:

            Batterie = Solar + Landstrom − Verbrauch

        Positive Batterieleistung heißt laden. Der Batteriestrom folgt aus
        Leistung und Spannung — dieselbe Beziehung wie in der Anlage.
        """
        power = self._number("energy.solar.power")
        load = self._number("energy.consumption.power")
        voltage = self._number("energy.battery.voltage")
        if power is None or load is None or voltage is None or voltage <= 0:
            return

        shore = self._devices.get("energy.shore.power")
        connected = self._devices.get("energy.shore.connected")
        if shore is not None:
            # Ohne Landstromverbindung fließt kein Landstrom. Das ist keine
            # Vereinfachung, sondern der einzige physikalisch mögliche Wert.
            live = connected is None or connected.value == "CLOSED"
            drifted = self._number("energy.shore.power") or 0.0
            shore.value = max(0.0, drifted) if live else 0.0
            self._publish(shore)

        shore_w = (shore.value if shore is not None else 0.0) or 0.0

        battery = self._devices.get("energy.battery.power")
        if battery is not None:
            battery.value = round(power + float(shore_w) - load, 1)
            self._publish(battery)

            current = self._devices.get("energy.battery.current")
            if current is not None:
                current.value = round(float(battery.value) / voltage, 2)
                self._publish(current)

    def _number(self, entity_id: str) -> float | None:
        device = self._devices.get(entity_id)
        if device is None or device.fault is not Fault.NONE:
            return None
        return device.value if isinstance(device.value, (int, float)) else None

    def _publish(self, device: _Device) -> None:
        self._state.apply(
            device.entity.id,
            StateValue.valid(device.value, unit=device.entity.unit, source=self.source),
        )

    def _advance(self, device: _Device, elapsed: float) -> StateValue:
        if device.fault is Fault.SENSOR_ERROR:
            return StateValue.error(unit=device.entity.unit, source=self.source)
        if device.fault is Fault.SENSOR_INVALID:
            return StateValue.invalid(unit=device.entity.unit, source=self.source)

        if device.kind == "motion":
            value = self._advance_motion(device, elapsed)
        elif device.kind == "measure":
            value = self._advance_measure(device, elapsed)
        else:
            value = device.value

        return StateValue.valid(
            value, unit=device.entity.unit, source=self.source
        )

    def _advance_motion(self, device: _Device, elapsed: float) -> str:
        """Bewegt ein Aufbauteil über die Zwischenzustände zum Ziel.

        Zwischenzustände sind echt und nicht dekorativ: Die Animation in der
        Oberfläche folgt genau diesem Verlauf (Kapitel 18 §105).
        """
        current = device.value

        if current not in (Motion.OPENING.value, Motion.CLOSING.value):
            return current

        if device.fault is Fault.BLOCKED:
            device.value = Motion.BLOCKED.value
            device.progress = 0.0
            log.info("Simulation: %s blockiert", device.entity.id)
            return device.value

        device.progress += elapsed
        if device.progress < device.travel_s:
            return current

        device.progress = 0.0
        device.value = (
            Motion.OPEN.value if current == Motion.OPENING.value else Motion.CLOSED.value
        )
        return device.value

    def _advance_measure(self, device: _Device, elapsed: float) -> float:
        """Lässt einen Messwert langsam und plausibel wandern.

        Nahe an den Bereichsgrenzen kehrt die Drift um, damit der Wert nicht
        an der Grenze klebt.
        """
        low, high = device.bounds
        current = float(device.value)
        span = high - low

        if current <= low + span * 0.05:
            device.drift = -abs(device.drift)
        elif current >= high - span * 0.05:
            device.drift = abs(device.drift)

        step = device.drift * elapsed + self._random.uniform(-0.01, 0.01) * span * 0.01
        device.value = max(low, min(high, current - step))
        return round(float(device.value), 1)

    # ── Befehle ─────────────────────────────────────────────────────────────

    async def execute(self, command: Command, spec: CommandSpec) -> None:
        device = self._devices.get(command.entity_id)
        if device is None:
            raise RuntimeError(f"Kein simuliertes Gerät für '{command.entity_id}'")

        if device.fault in (Fault.SENSOR_ERROR, Fault.SILENT):
            raise RuntimeError("Gerät antwortet nicht")

        # Eine kleine Verzögerung, damit sich der Ablauf realistisch anfühlt
        # und die Oberfläche ihren Zwischenzustand tatsächlich zeigt.
        await asyncio.sleep(0.05)

        if device.kind == "motion":
            self._start_motion(device, command.verb)
        elif device.kind == "switch":
            device.value = command.params.get("state", spec.expects)
        elif device.kind == "setpoint":
            # Der Parametername steht in der Capability — `celsius` bei einer
            # Klimazone, `value` bei einer Strombegrenzung. Ihn hier fest zu
            # verdrahten hieße, den Simulator bei jedem neuen Sollwert
            # nachzuziehen.
            key = spec.expects_param or "value"
            device.value = float(command.params.get(key, spec.expects or 0.0))
        else:
            raise RuntimeError(f"'{command.verb}' ist hier nicht ausführbar")

        # Sofort melden, damit der Zwischenzustand nicht bis zum nächsten
        # Zyklus wartet.
        self._state.apply(
            device.entity.id,
            StateValue.valid(
                device.value, unit=device.entity.unit, source=self.source
            ),
        )

    def _start_motion(self, device: _Device, verb: str) -> None:
        if verb == "stop":
            device.value = Motion.STOPPED.value
            device.progress = 0.0
            return
        device.progress = 0.0
        device.value = (
            Motion.OPENING.value if verb == "open" else Motion.CLOSING.value
        )

    # ── Fehlerinjektion ─────────────────────────────────────────────────────

    def inject(self, entity_id: str, fault: Fault) -> None:
        """Löst ein Fehlerbild aus oder nimmt es zurück.

        Damit lassen sich die Zustände testen, die im Alltag am seltensten und
        im Ernstfall am wichtigsten sind (Kapitel 18 §71).
        """
        device = self._devices.get(entity_id)
        if device is None:
            raise KeyError(f"Kein simuliertes Gerät für '{entity_id}'")
        device.fault = fault
        log.info("Simulation: %s → %s", entity_id, fault.value)

        if fault is Fault.SENSOR_ERROR:
            self._state.apply(
                entity_id,
                StateValue.error(unit=device.entity.unit, source=self.source),
            )
        elif fault is Fault.SENSOR_INVALID:
            self._state.apply(
                entity_id,
                StateValue.invalid(unit=device.entity.unit, source=self.source),
            )

    def set_level(self, entity_id: str, value: float) -> None:
        """Setzt einen simulierten Messwert auf einen bestimmten Stand.

        Ohne das ließen sich Schwellenwarnungen nur prüfen, indem man wartet,
        bis der Simulator zufällig dorthin driftet — bei einem Tank, der um
        60 % pendelt, also nie. Der Wert driftet danach normal weiter.

        Wie die Fehlerinjektion existiert dieser Weg ausschließlich in der
        Simulation.
        """
        device = self._devices.get(entity_id)
        if device is None:
            raise KeyError(f"Kein simuliertes Gerät für '{entity_id}'")
        if device.kind not in ("measure", "setpoint"):
            raise ValueError(f"'{entity_id}' ist kein Messwert")

        low, high = device.bounds
        device.value = max(low, min(high, float(value)))
        log.info("Simulation: %s auf %.1f gesetzt", entity_id, device.value)

        self._state.apply(
            entity_id,
            StateValue.valid(device.value, unit=device.entity.unit, source=self.source),
            force=True,
        )

    def clear_faults(self) -> None:
        for device in self._devices.values():
            device.fault = Fault.NONE

    @property
    def faults(self) -> dict[str, str]:
        """Aktive Fehlerbilder, für die Diagnoseansicht."""
        return {
            entity_id: device.fault.value
            for entity_id, device in self._devices.items()
            if device.fault is not Fault.NONE
        }

    def set_value(self, entity_id: str, value: object) -> None:
        """Setzt einen simulierten Wert direkt — für Tests und Vorführungen."""
        device = self._devices.get(entity_id)
        if device is None:
            raise KeyError(f"Kein simuliertes Gerät für '{entity_id}'")
        device.value = value
        self._state.apply(
            entity_id,
            StateValue.valid(value, unit=device.entity.unit, source=self.source),
        )

    @staticmethod
    def quality_of(value: StateValue) -> Quality:
        return value.quality
