from dataclasses import dataclass

from stegverse.mhia_reference_firmware import ElectricalEnvelope, MHIAEvent, ReferenceFirmwareStateMachine
from stegverse.mhia_reference_hal import HardwareBinding


@dataclass
class FakePower:
    vsafe: bool = False
    vbus: bool = False
    fault: bool = False
    current_ma: int = 0

    def set_vsafe(self, enabled: bool) -> None:
        self.vsafe = enabled

    def set_vbus(self, enabled: bool) -> None:
        self.vbus = enabled

    def read_fault(self) -> bool:
        return self.fault

    def read_current_ma(self) -> int:
        return self.current_ma


class FakeTransport:
    def attached(self) -> bool:
        return True

    def read_passive_identity(self) -> str | None:
        return "module:test"

    def exchange_manifest(self) -> dict:
        return {"schema": "fixture"}


def _active_binding(current_ma: int = 100):
    machine = ReferenceFirmwareStateMachine()
    machine.transition(MHIAEvent.ATTACH)
    machine.transition(MHIAEvent.ENABLE_DISCOVERY)
    machine.transition(MHIAEvent.MANIFEST_OK, module_id="module:test")
    machine.transition(
        MHIAEvent.NEGOTIATION_OK,
        envelope=ElectricalEnvelope(voltage_mv=5000, current_ma=500, thermal_limit_c=70),
    )
    machine.transition(MHIAEvent.ADMISSION_ALLOW)
    machine.transition(MHIAEvent.ENABLE_VBUS)
    power = FakePower(current_ma=current_ma)
    binding = HardwareBinding(machine=machine, power=power, transport=FakeTransport())
    return binding, power


def test_unadmitted_state_cannot_energize_vbus():
    machine = ReferenceFirmwareStateMachine()
    machine.transition(MHIAEvent.ATTACH)
    machine.transition(MHIAEvent.ENABLE_DISCOVERY)
    power = FakePower(vbus=True)
    binding = HardwareBinding(machine=machine, power=power, transport=FakeTransport())
    binding.apply_state()
    assert power.vsafe is True
    assert power.vbus is False


def test_active_state_projects_vsafe_and_vbus():
    binding, power = _active_binding()
    binding.apply_state()
    assert power.vsafe is True
    assert power.vbus is True
    assert binding.enforce_envelope() is True


def test_overcurrent_fails_closed():
    binding, power = _active_binding(current_ma=501)
    binding.apply_state()
    assert binding.enforce_envelope() is False
    assert power.vbus is False


def test_hardware_fault_forces_all_power_off():
    binding, power = _active_binding()
    power.fault = True
    binding.apply_state()
    assert power.vsafe is False
    assert power.vbus is False


def test_non_active_state_envelope_enforcement_stays_off():
    machine = ReferenceFirmwareStateMachine()
    machine.transition(MHIAEvent.ATTACH)
    power = FakePower(vbus=True)
    binding = HardwareBinding(machine=machine, power=power, transport=FakeTransport())
    assert binding.enforce_envelope() is False
    assert power.vbus is False
