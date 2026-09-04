from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from stegverse.mhia_reference_firmware import ElectricalEnvelope, MHIAState, ReferenceFirmwareStateMachine


class PowerPath(Protocol):
    """Hardware boundary for independently controlled discovery and operating power."""

    def set_vsafe(self, enabled: bool) -> None: ...
    def set_vbus(self, enabled: bool) -> None: ...
    def read_fault(self) -> bool: ...
    def read_current_ma(self) -> int: ...


class ModuleTransport(Protocol):
    """Non-authorizing module discovery/data transport."""

    def attached(self) -> bool: ...
    def read_passive_identity(self) -> str | None: ...
    def exchange_manifest(self) -> dict: ...


@dataclass
class HardwareBinding:
    """Reference hardware-abstraction binding for an MHIA port.

    This class only projects an already-governed firmware state onto hardware.
    It cannot create admission, credentials, or authority. Operating power is
    fail-closed unless the state machine is explicitly VBUS_ACTIVE.
    """

    machine: ReferenceFirmwareStateMachine
    power: PowerPath
    transport: ModuleTransport

    def apply_state(self) -> None:
        if self.power.read_fault():
            self.power.set_vbus(False)
            self.power.set_vsafe(False)
            return

        # Apply VBUS OFF before changing discovery power so transient state
        # changes cannot momentarily energize an unadmitted module.
        if self.machine.state is not MHIAState.VBUS_ACTIVE:
            self.power.set_vbus(False)

        self.power.set_vsafe(self.machine.vsafe_enabled)
        self.power.set_vbus(self.machine.vbus_enabled)

    def enforce_envelope(self) -> bool:
        envelope: ElectricalEnvelope | None = self.machine.negotiated_envelope
        if not self.machine.vbus_enabled or envelope is None:
            self.power.set_vbus(False)
            return False
        if self.power.read_fault() or self.power.read_current_ma() > envelope.current_ma:
            self.power.set_vbus(False)
            return False
        return True


REFERENCE_BINDING_CANDIDATES = {
    "host_soc": {
        "manufacturer": "Nordic Semiconductor",
        "part_family": "nRF5340",
        "role": "host control, BLE/LE Audio capable compute and module transport",
    },
    "power_path": {
        "manufacturer": "Texas Instruments",
        "part_family": "TPS25947",
        "role": "protected, switchable operating power/eFuse boundary",
    },
    "module_power_management": {
        "manufacturer": "Nordic Semiconductor",
        "part_family": "nPM1300",
        "role": "single-cell battery charging, regulation, fuel/system management",
    },
    "imu": {
        "manufacturer": "TDK InvenSense",
        "part_family": "ICM-42688-P",
        "role": "6-axis motion/head-tracking reference sensor",
    },
    "audio_amp": {
        "manufacturer": "Analog Devices",
        "part_family": "MAX98357A",
        "role": "I2S/TDM reference Class-D audio output stage",
    },
}
