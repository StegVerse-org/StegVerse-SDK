from __future__ import annotations

import pytest

from stegverse.mhia_reference_firmware import (
    ElectricalEnvelope,
    MHIAEvent,
    MHIAState,
    ReferenceFirmwareStateMachine,
    required_pin_safe_defaults,
    validate_pin_names,
)


def _admitted_machine() -> ReferenceFirmwareStateMachine:
    machine = ReferenceFirmwareStateMachine()
    machine.transition(MHIAEvent.ATTACH)
    machine.transition(MHIAEvent.ENABLE_DISCOVERY)
    machine.transition(MHIAEvent.MANIFEST_OK, module_id="mhia:module:ear-right-reference-001")
    machine.transition(
        MHIAEvent.NEGOTIATION_OK,
        envelope=ElectricalEnvelope(voltage_mv=5000, current_ma=500, thermal_limit_c=60),
    )
    machine.transition(MHIAEvent.ADMISSION_ALLOW)
    return machine


def test_vbus_stays_off_until_explicit_admission_and_enable():
    machine = ReferenceFirmwareStateMachine()
    assert machine.state is MHIAState.DETACHED
    assert not machine.vbus_enabled

    machine.transition(MHIAEvent.ATTACH)
    machine.transition(MHIAEvent.ENABLE_DISCOVERY)
    machine.transition(MHIAEvent.MANIFEST_OK, module_id="mhia:module:test")
    machine.transition(
        MHIAEvent.NEGOTIATION_OK,
        envelope=ElectricalEnvelope(voltage_mv=5000, current_ma=250, thermal_limit_c=55),
    )
    assert machine.state is MHIAState.NEGOTIATED
    assert not machine.vbus_enabled

    machine.transition(MHIAEvent.ADMISSION_ALLOW)
    assert machine.state is MHIAState.ADMITTED
    assert not machine.vbus_enabled

    machine.transition(MHIAEvent.ENABLE_VBUS)
    assert machine.state is MHIAState.VBUS_ACTIVE
    assert machine.vbus_enabled


def test_cannot_skip_discovery_manifest_negotiation_or_admission():
    machine = ReferenceFirmwareStateMachine()
    with pytest.raises(ValueError):
        machine.transition(MHIAEvent.ENABLE_VBUS)

    machine.transition(MHIAEvent.ATTACH)
    with pytest.raises(ValueError):
        machine.transition(MHIAEvent.MANIFEST_OK, module_id="mhia:module:test")


def test_invalid_manifest_returns_safe_off():
    machine = ReferenceFirmwareStateMachine()
    machine.transition(MHIAEvent.ATTACH)
    machine.transition(MHIAEvent.ENABLE_DISCOVERY)
    machine.transition(MHIAEvent.MANIFEST_INVALID)
    assert machine.state is MHIAState.SAFE_OFF
    assert not machine.vbus_enabled
    assert not machine.admitted


def test_fault_isolates_and_removes_operating_power():
    machine = _admitted_machine()
    machine.transition(MHIAEvent.ENABLE_VBUS)
    assert machine.vbus_enabled
    machine.transition(MHIAEvent.FAULT)
    assert machine.state is MHIAState.ISOLATED
    assert not machine.vbus_enabled
    assert machine.negotiated_envelope is None


def test_detach_clears_identity_and_envelope():
    machine = _admitted_machine()
    machine.transition(MHIAEvent.DETACH)
    assert machine.state is MHIAState.DETACHED
    assert machine.module_id is None
    assert machine.negotiated_envelope is None
    assert not machine.admitted


def test_reference_pin_defaults_keep_vbus_off():
    pins = required_pin_safe_defaults()
    assert pins["VBUS"] == "OFF"
    assert pins["VSAFE"] == "OFF_UNTIL_DISCOVERY"
    validate_pin_names(pins.keys())


def test_reference_pin_validation_fails_on_missing_or_extra_pin():
    pins = list(required_pin_safe_defaults())
    with pytest.raises(ValueError):
        validate_pin_names(pins[:-1])
    with pytest.raises(ValueError):
        validate_pin_names([*pins, "AUTHORITY"])
