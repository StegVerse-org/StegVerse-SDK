"""Build a bounded downstream status packet from joint activation evidence.

This module does not publish, mirror, release, enable production binding, transfer
custody, determine admissibility, or grant authority. It only produces a status
packet whose propagation flag is true when the joint activation gate is VERIFIED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .system_boundary_activation import evaluate_system_boundary_activation

DOWNSTREAM_TARGETS = (
    "StegVerse-Labs/Site",
    "GCAT-BCAT-Engine/Publisher",
    "StegVerse-Labs/admissibility-wiki",
    "StegVerse-002/stegguardian-wiki",
)


@dataclass(frozen=True)
class DownstreamStatusResult:
    accepted: bool
    packet: dict[str, Any]
    errors: tuple[str, ...]


def build_downstream_status_packet(
    adapter_evidence: Mapping[str, Any],
    sdk_evidence: Mapping[str, Any],
) -> DownstreamStatusResult:
    activation = evaluate_system_boundary_activation(adapter_evidence, sdk_evidence)
    if not activation.accepted:
        return DownstreamStatusResult(False, {}, activation.errors)

    propagation_allowed = activation.verified and activation.state == "VERIFIED"
    packet = {
        "schema_version": "stegverse.system_boundary.downstream_status.v0.1",
        "activation_state": activation.state,
        "verified": activation.verified,
        "downstream_propagation_allowed": propagation_allowed,
        "targets": list(DOWNSTREAM_TARGETS),
        "status_only": True,
        "production_binding_enabled": False,
        "release_authorized": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
    }
    return DownstreamStatusResult(True, packet, ())
