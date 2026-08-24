from __future__ import annotations

from typing import Any, Mapping

from .interlock_transition import canonical_hash as interlock_hash
from .portable_governance_verifier import verify_portable_governance_bundle


def build_standing_execution_context(pre_steggate_bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Build the exact context consumed by canonical StegCore standing verification.

    The portable verifier is run first.  This helper does not decide standing or
    grant execution authority; it only carries already-bound PRE_STEGGATE evidence
    into the canonical StegCore runtime where it is independently re-hashed.
    """
    bundle = dict(pre_steggate_bundle)
    report = verify_portable_governance_bundle(bundle)
    if report.get("status") != "PASS" or report.get("stage") != "PRE_STEGGATE":
        raise ValueError("valid PRE_STEGGATE bundle is required")

    ingress = bundle.get("ingress_interlock")
    if not isinstance(ingress, Mapping):
        raise ValueError("ingress_interlock is required")
    connection = ingress.get("connection")
    if not isinstance(connection, Mapping):
        raise ValueError("ingress interlock connection is required")
    participant_id = str(connection.get("participant_id") or "").strip()
    if not participant_id:
        raise ValueError("participant_id is required")

    expected = {
        "package_id": bundle["package_id"],
        "transition_id": bundle["transition_id"],
        "run_id": bundle["run_id"],
        "participant_id": participant_id,
        "ingress_interlock_hash": interlock_hash(dict(ingress)),
    }
    return {
        "standing_required": True,
        "standing_evidence": {
            "required": True,
            "expected_interlock": expected,
            "spe_envelope": bundle["spe_envelope"],
            "spe_receipt": bundle["spe_receipt"],
            "steggate_bridge": bundle["steggate_bridge"],
        },
        "authority": {
            "sdk_authority": "NONE",
            "standing_decision_authority": "CANONICAL_STEGCORE_ONLY",
            "execution_authorized": False,
        },
    }


__all__ = ["build_standing_execution_context"]
