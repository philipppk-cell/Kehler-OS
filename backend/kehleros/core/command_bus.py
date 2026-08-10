"""Die Befehlskette.

Ein Befehl ist eine *Absicht*. Er wird geprüft, an einen Adapter übergeben und
gilt erst dann als erfüllt, wenn die Hardware den Zustand bestätigt hat. Der
Befehl selbst schreibt niemals in den State Store (Kapitel 12 §67,
Kapitel 18 §35/§37).

Ablauf::

    REQUESTED → VALIDATING → SENT → ACKNOWLEDGED → COMPLETED
                     │         │          │
                     │         │          └──▶ TIMEOUT
                     │         └─────────────▶ FAILED
                     └───────────────────────▶ REJECTED
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Protocol

from ..domain.enums import (
    CommandPhase,
    LinkState,
    Quality,
    RejectionReason,
    Severity,
)
from ..domain.models import Command, CommandSpec, Entity, Event, RequestedState
from .event_bus import EventBus
from .registry import Registry
from .state_store import StateStore

log = logging.getLogger(__name__)

_CONFIRMED = object()
"""Kennzeichnet die bestätigte Ausführung — abgegrenzt von jedem Zustandsnamen."""


class AdapterError(RuntimeError):
    """Der Adapter konnte den Befehl nicht ausführen."""


class CommandTarget(Protocol):
    """Was der Command Bus von einem Adapter braucht."""

    name: str

    def owns(self, entity_id: str) -> bool: ...

    async def execute(self, command: Command, spec: CommandSpec) -> None: ...


Authorizer = Callable[[Command, Entity, CommandSpec], RejectionReason | None]
"""Gibt ``None`` zurück, wenn der Befehl erlaubt ist, sonst den Ablehnungsgrund."""

SafetyCheck = Callable[[Command, Entity, CommandSpec], str | None]
"""Gibt ``None`` zurück, wenn keine Sicherheitsbedingung entgegensteht.

Dies ist **keine** technische Schutzfunktion. Die eigentliche Verriegelung
gehört in die Steuerung; diese Prüfung verhindert lediglich, dass Kehler OS
offensichtlich Unzulässiges überhaupt erst absetzt (Kapitel 12 §7,
Kapitel 15 §24).
"""


def _allow_all(
    command: Command, entity: Entity, spec: CommandSpec
) -> RejectionReason | None:
    """Vorgabe bis zur Benutzerverwaltung in M7.

    Der Haken existiert bewusst von Anfang an: Kapitel 18 §120 verbietet,
    erst zu bauen und später abzusichern.
    """
    return None


def _no_safety_condition(
    command: Command, entity: Entity, spec: CommandSpec
) -> str | None:
    return None


class CommandBus:
    """Nimmt Befehle entgegen, prüft sie und verfolgt ihr Ergebnis."""

    def __init__(
        self,
        registry: Registry,
        state_store: StateStore,
        event_bus: EventBus,
        *,
        authorizer: Authorizer | None = None,
        safety_check: SafetyCheck | None = None,
    ) -> None:
        self._registry = registry
        self._state = state_store
        self._events = event_bus
        self._authorize = authorizer or _allow_all
        self._safety = safety_check or _no_safety_condition
        self._targets: list[CommandTarget] = []
        self._locks: dict[str, asyncio.Lock] = {}

    def register_target(self, target: CommandTarget) -> None:
        self._targets.append(target)

    # ── Öffentliche Schnittstelle ───────────────────────────────────────────

    async def submit(self, command: Command) -> Command:
        """Führt einen Befehl vollständig aus und gibt ihn beendet zurück."""
        command.phase = CommandPhase.VALIDATING

        checked = self._validate(command)
        if checked is None:
            await self._announce(command)
            return command

        entity, spec, target = checked
        lock = self._locks.setdefault(command.entity_id, asyncio.Lock())

        # Solange eine Bewegung läuft, wird ein zweiter Fahrbefehl abgewiesen
        # statt überlagert (Kapitel 13 §21).
        #
        # **Außer beim Stopp.** Ihn abzuweisen, weil eine Bewegung läuft, kehrt
        # den Sinn um: Ein Stopp ist kein zweiter Fahrbefehl, sondern das Ende
        # des ersten. Er nimmt deshalb die Sperre nicht und wartet nicht — er
        # geht sofort durch, und der laufende Befehl merkt am Zustand, dass er
        # abgelöst wurde.
        if lock.locked() and not spec.preempts:
            command.reject(
                RejectionReason.BUSY,
                f"Für {command.entity_id} läuft bereits ein Befehl",
            )
            await self._announce(command)
            return command

        if spec.preempts:
            await self._dispatch(command, entity, spec, target)
        else:
            async with lock:
                await self._dispatch(command, entity, spec, target)

        await self._announce(command)
        return command

    # ── Prüfung ─────────────────────────────────────────────────────────────

    def _validate(
        self, command: Command
    ) -> tuple[Entity, CommandSpec, CommandTarget] | None:
        """Alle Prüfungen vor dem ersten Hardwarekontakt.

        Serverseitig und unabhängig davon, was die Oberfläche anzeigt — ein
        ausgeblendeter Knopf ist keine Zugriffskontrolle (Kapitel 15 §42).
        """
        entity = self._registry.get(command.entity_id)
        if entity is None:
            command.reject(
                RejectionReason.UNKNOWN_ENTITY,
                f"Entity '{command.entity_id}' ist nicht registriert",
            )
            return None

        if not entity.configured:
            command.reject(
                RejectionReason.NOT_CONFIGURED,
                f"Für '{entity.id}' ist keine Hardware zugeordnet",
            )
            return None

        spec = entity.spec_for(command.verb)
        if spec is None:
            command.reject(
                RejectionReason.MISSING_CAPABILITY,
                f"'{entity.id}' kann '{command.verb}' nicht "
                f"(verfügbar: {', '.join(entity.capabilities) or 'keine'})",
            )
            return None

        unexpected = set(command.params) - set(spec.params)
        if unexpected:
            command.reject(
                RejectionReason.INVALID_PARAMS,
                f"Unerwartete Parameter: {', '.join(sorted(unexpected))}",
            )
            return None

        invalid = _check_value(command, entity, spec)
        if invalid is not None:
            command.reject(RejectionReason.INVALID_PARAMS, invalid)
            return None

        denial = self._authorize(command, entity, spec)
        if denial is not None:
            command.reject(denial, "Berechtigungsprüfung fehlgeschlagen")
            return None

        blocked = self._safety(command, entity, spec)
        if blocked is not None:
            command.reject(RejectionReason.SAFETY_CONDITION, blocked)
            return None

        target = self._target_for(entity.id)
        if target is None:
            command.reject(
                RejectionReason.DEVICE_UNAVAILABLE,
                f"Kein Adapter zuständig für '{entity.id}'",
            )
            return None

        current = self._state.get(entity.id)
        if current is not None and current.link in _UNREACHABLE:
            command.reject(
                RejectionReason.DEVICE_UNAVAILABLE,
                f"Gerät nicht erreichbar ({current.link.value})",
            )
            return None

        return entity, spec, target

    def _target_for(self, entity_id: str) -> CommandTarget | None:
        for target in self._targets:
            if target.owns(entity_id):
                return target
        return None

    # ── Ausführung ──────────────────────────────────────────────────────────

    async def _dispatch(
        self,
        command: Command,
        entity: Entity,
        spec: CommandSpec,
        target: CommandTarget,
    ) -> None:
        # Erst zuhören, dann senden — sonst kann eine sehr schnelle
        # Rückmeldung verpasst werden.
        subscription = self._state.subscribe()
        baseline = self._state.require(entity.id).seq

        self._state.set_requested(
            entity.id,
            RequestedState(value=spec.expected_value(command), command_id=command.id),
        )

        try:
            command.phase = CommandPhase.SENT
            try:
                await target.execute(command, spec)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.warning("Adapter %s lehnte %s ab: %s", target.name, command.name, exc)
                command.fail(CommandPhase.FAILED, str(exc))
                return

            command.phase = CommandPhase.ACKNOWLEDGED

            ended = await self._await_confirmation(
                subscription, entity.id, spec, command, baseline
            )
            if ended is _CONFIRMED:
                command.complete()
            elif ended in spec.superseded_states:
                command.ended_state = str(ended)
                # Kein Fehler: Wer ein fahrendes Tor anhält, hat erreicht, was
                # er wollte. Erfolgreich ist dieser Befehl trotzdem nicht — er
                # hat sein Ziel nicht erreicht.
                command.fail(
                    CommandPhase.SUPERSEDED,
                    f"Abgelöst — Endzustand '{ended}'",
                )
            elif ended in spec.failure_states:
                command.ended_state = str(ended)
                # Die Hardware hat geantwortet, nur eben schlecht. Das sofort
                # zu melden ist der Punkt: Sonst stünde der Benutzer die volle
                # Timeout-Zeit vor einem klemmenden Tor und erführe danach
                # „keine Rückmeldung" — die falsche Auskunft.
                command.fail(CommandPhase.FAILED, f"Endzustand '{ended}'")
            else:
                # Kein Erfolg vortäuschen: Ohne Bestätigung bleibt offen, was
                # die Hardware getan hat (Kapitel 18 §20/§37).
                command.fail(
                    CommandPhase.TIMEOUT,
                    f"Keine Rückmeldung innerhalb von {spec.timeout_ms} ms",
                )
        finally:
            self._state.unsubscribe(subscription)
            self._state.set_requested(entity.id, None)

    async def _await_confirmation(
        self,
        subscription,
        entity_id: str,
        spec: CommandSpec,
        command: Command,
        baseline_seq: int,
    ) -> object:
        """Wartet, bis die Hardware antwortet.

        Zwischenzustände sind ausdrücklich erlaubt: Ein Garagentor darf über
        ``OPENING`` nach ``OPEN`` laufen. Gewartet wird auf den Zielzustand,
        nicht auf die erste beste Änderung.

        Rückgabe: ``_CONFIRMED`` bei Erfolg, sonst der Zustandsname, in dem
        die Bewegung tatsächlich geendet ist, oder ``None`` bei Zeitablauf.
        Diese drei sind verschiedene Dinge und werden nicht zu einem
        ``False`` zusammengefasst — sonst hieße jedes Ende „keine
        Rückmeldung".
        """
        if self._satisfies(entity_id, spec, command, baseline_seq):
            return _CONFIRMED

        timeout = spec.timeout_ms / 1000
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                return None
            try:
                delta = await asyncio.wait_for(subscription.get(), timeout=remaining)
            except TimeoutError:
                return None
            if delta.entity_id != entity_id:
                continue
            if self._satisfies(entity_id, spec, command, baseline_seq):
                return _CONFIRMED
            ended = self._ended_elsewhere(entity_id, spec, baseline_seq)
            if ended is not None:
                return ended

    def _ended_elsewhere(
        self, entity_id: str, spec: CommandSpec, baseline_seq: int
    ) -> str | None:
        """Ob die Bewegung in einem anderen Endzustand steht.

        Nur Zustände **nach** dem Ausgangsstand zählen. Sonst schlüge ein
        `open` sofort fehl, wenn das Tor vorher schon gestoppt war — der alte
        Zustand ist kein Ergebnis des neuen Befehls.
        """
        current = self._state.get(entity_id)
        if current is None or current.seq <= baseline_seq:
            return None
        if current.state.quality is not Quality.VALID:
            return None
        value = current.state.value
        if value in spec.superseded_states or value in spec.failure_states:
            return str(value)
        return None

    def _satisfies(
        self,
        entity_id: str,
        spec: CommandSpec,
        command: Command,
        baseline_seq: int,
    ) -> bool:
        current = self._state.get(entity_id)
        if current is None:
            return False
        value = current.state
        if value.quality is not Quality.VALID:
            return False

        expected = spec.expected_value(command)
        if expected is None:
            # Kein vorhersagbarer Zielzustand: Eine bestätigte Änderung genügt.
            return current.seq > baseline_seq
        return value.value == expected

    # ── Nachbereitung ───────────────────────────────────────────────────────

    async def _announce(self, command: Command) -> None:
        """Meldet das Ergebnis als Ereignis — Grundlage für Audit und Historie."""
        severity = Severity.INFO if command.phase.is_success else Severity.WARNING
        await self._events.publish(
            Event(
                type=f"command.{command.phase.value.lower()}",
                entity_id=command.entity_id,
                severity=severity,
                correlation_id=command.correlation_id,
                data={
                    "command_id": command.id,
                    "verb": command.verb,
                    "params": dict(command.params),
                    "trigger": command.trigger.value,
                    "actor": command.actor,
                    "client": command.client,
                    "phase": command.phase.value,
                    "rejection": command.rejection.value if command.rejection else None,
                    "detail": command.detail,
                    "duration_ms": command.duration_ms,
                },
            )
        )


_UNREACHABLE = frozenset(
    {
        LinkState.OFFLINE,
        LinkState.ERROR,
        LinkState.NOT_CONFIGURED,
    }
)


def _check_value(command: Command, entity: Entity, spec: CommandSpec) -> str | None:
    """Prüft den Zielwert eines Befehls gegen die Grenzen der Entity.

    **Das ist die eigentliche Schutzfunktion bei einstellbaren Werten** — nicht
    ein Bestätigungsdialog in der Oberfläche. Ein Client, der die Oberfläche
    umgeht, muss hier scheitern (Kapitel 15 §42: ein ausgeblendeter Knopf ist
    keine Zugriffskontrolle).

    Konkret verhindert das, dass jemand die Eingangsstrombegrenzung über die
    Absicherung des Landstromanschlusses hinaus stellt.

    Zurückgegeben wird die Begründung oder ``None``, wenn alles stimmt.
    """
    if spec.expects_param is None:
        return None

    if spec.expects_param not in command.params:
        # Ein Befehl, der seinen Zielwert nicht mitbringt, hat keinen —
        # er würde ins Leere laufen und im Timeout enden.
        return f"Parameter '{spec.expects_param}' fehlt"

    value = command.params[spec.expects_param]

    if entity.min_value is None and entity.max_value is None:
        return None

    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return f"'{spec.expects_param}' muss ein Zahlenwert sein"

    if entity.min_value is not None and value < entity.min_value:
        return f"{value} liegt unter dem Mindestwert {entity.min_value}"

    if entity.max_value is not None and value > entity.max_value:
        return f"{value} liegt über dem Höchstwert {entity.max_value}"

    return None
