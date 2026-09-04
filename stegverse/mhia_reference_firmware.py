from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping


class MHIAState(str, Enum):
    DETACHED = "DETACHED"
    SAFE_OFF = "SAFE_OFF"
    VSAFE_DISCOVERY = "VSAFE_DISCOVERY"
    MANIFEST_VALIDATED = "MANIFEST_VALIDATED"
    NEGOTIATED = "NEGOTIATED"
    ADMITTED = "ADMITTED"
    VBUS_ACTIVE = "VBUS_ACTIVE"
    ISOLATED = "ISOLATED"


class MHIAEvent(str, Enum):
    ATTACH = "ATTACH"
    DETACH = "DETACH"
    ENABLE_DISCOVERY = "ENABLE_DISCOVERY"
    MANIFEST_OK = "MANIFEST_OK"
    MANIFEST_INVALID = "MANIFEST_INVALID"
    NEGOTIATION_OK = "NEGOTIATION_OK"
    NEGOTIATION_FAIL = "NEGOTIATION_FAIL"
    ADMISSION_ALLOW = "ADMISSION_ALLOW"
    ADMISSION_DENY = "ADMISSION_DENY"
    ENABLE_VBUS = "ENABLE_VBUS"
    FAULT = "FAULT"
    RESET = "RESET"


@dataclass(frozen=True)
class ElectricalEnvelope:
    voltage_mv: int
    current_ma: int
    thermal_limit_c: int

    def validate(self) -> None:
        if self.voltage_mv <= 0 or self.current_ma <= 0:
            raise ValueError("electrical envelope must be positive")
        if not 0 < self.thermal_limit_c <= 100:
            raise ValueError("thermal limit outside reference range")


@dataclass
class ReferenceFirmwareStateMachine:
    """Non-authorizing reference state machine for MHIA ear-module power/discovery.

    It models safe sequencing only. It does not issue credentials, perform governance,
    or convert discovery into authority.
    """

    state: MHIAState = MHIAState.DETACHED
    negotiated_envelope: ElectricalEnvelope | None = None
    module_id: str | None = None
    admitted: bool = False

    def transition(
        self,
        event: MHIAEvent,
        *,
        module_id: str | None = None,
        envelope: ElectricalEnvelope | None = None,
    ) -> MHIAState:
        if event is MHIAEvent.DETACH:
            self._clear_session()
            self.state = MHIAState.DETACHED
            return self.state

        if event is MHIAEvent.FAULT:
            self.admitted = False
            self.negotiated_envelope = None
            self.state = MHIAState.ISOLATED
            return self.state

        if event is MHIAEvent.RESET:
            self._clear_session()
            self.state = MHIAState.SAFE_OFF
            return self.state

        allowed = {
            MHIAState.DETACHED: {MHIAEvent.ATTACH: MHIAState.SAFE_OFF},
            MHIAState.SAFE_OFF: {
                MHIAEvent.ENABLE_DISCOVERY: MHIAState.VSAFE_DISCOVERY,
            },
            MHIAState.VSAFE_DISCOVERY: {
                MHIAEvent.MANIFEST_OK: MHIAState.MANIFEST_VALIDATED,
                MHIAEvent.MANIFEST_INVALID: MHIAState.SAFE_OFF,
            },
            MHIAState.MANIFEST_VALIDATED: {
                MHIAEvent.NEGOTIATION_OK: MHIAState.NEGOTIATED,
                MHIAEvent.NEGOTIATION_FAIL: MHIAState.SAFE_OFF,
            },
            MHIAState.NEGOTIATED: {
                MHIAEvent.ADMISSION_ALLOW: MHIAState.ADMITTED,
                MHIAEvent.ADMISSION_DENY: MHIAState.SAFE_OFF,
            },
            MHIAState.ADMITTED: {
                MHIAEvent.ENABLE_VBUS: MHIAState.VBUS_ACTIVE,
                MHIAEvent.ADMISSION_DENY: MHIAState.SAFE_OFF,
            },
            MHIAState.VBUS_ACTIVE: {
                MHIAEvent.ADMISSION_DENY: MHIAState.SAFE_OFF,
            },
            MHIAState.ISOLATED: {},
        }

        next_state = allowed[self.state].get(event)
        if next_state is None:
            raise ValueError(f"invalid MHIA transition: {self.state.value} + {event.value}")

        if event is MHIAEvent.MANIFEST_OK:
            if not module_id:
                raise ValueError("module_id required for MANIFEST_OK")
            self.module_id = module_id

        if event is MHIAEvent.NEGOTIATION_OK:
            if envelope is None:
                raise ValueError("electrical envelope required for NEGOTIATION_OK")
            envelope.validate()
            self.negotiated_envelope = envelope

        if event is MHIAEvent.ADMISSION_ALLOW:
            if self.module_id is None or self.negotiated_envelope is None:
                raise ValueError("validated identity and negotiated envelope required")
            self.admitted = True

        if event in {
            MHIAEvent.MANIFEST_INVALID,
            MHIAEvent.NEGOTIATION_FAIL,
            MHIAEvent.ADMISSION_DENY,
        }:
            self.admitted = False
            self.negotiated_envelope = None

        if event is MHIAEvent.ENABLE_VBUS:
            if not self.admitted or self.negotiated_envelope is None:
                raise ValueError("VBUS requires explicit admission and negotiated envelope")

        self.state = next_state
        return self.state

    @property
    def vsafe_enabled(self) -> bool:
        return self.state in {
            MHIAState.VSAFE_DISCOVERY,
            MHIAState.MANIFEST_VALIDATED,
            MHIAState.NEGOTIATED,
            MHIAState.ADMITTED,
            MHIAState.VBUS_ACTIVE,
        }

    @property
    def vbus_enabled(self) -> bool:
        return self.state is MHIAState.VBUS_ACTIVE

    def _clear_session(self) -> None:
        self.negotiated_envelope = None
        self.module_id = None
        self.admitted = False


def required_pin_safe_defaults() -> Mapping[str, str]:
    return {
        "GND": "BONDED",
        "GND_SENSE": "HIGH_IMPEDANCE",
        "DETECT_ID": "CURRENT_LIMITED_PULLUP",
        "DATA_P": "HIGH_IMPEDANCE",
        "DATA_N": "HIGH_IMPEDANCE",
        "WAKE_INT": "HIGH_IMPEDANCE",
        "VSAFE": "OFF_UNTIL_DISCOVERY",
        "VBUS": "OFF",
    }


def validate_pin_names(pin_names: Iterable[str]) -> None:
    expected = set(required_pin_safe_defaults())
    actual = set(pin_names)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"reference pin set mismatch: missing={missing}, extra={extra}")
