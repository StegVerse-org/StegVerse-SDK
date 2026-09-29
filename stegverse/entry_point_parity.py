"""Whether the Chat entry point equates to a console entry.

Granular control is a property of the *entry point*, not of the builder. The
console offers submission, replay, reconstruction, and control over what the
return projects and how it is labelled. If Chat cannot reach the same
capability, someone using Chat silently gives up abilities — which is not a
hypothetical: the evaluator for Tests 1-3 was iPhone-only and another operator
had to drive the console on their behalf, and that is recorded in the run
evidence as a limit on the evidentiary claim.

Replay and reconstruction matter most here. They are how a result is verified
rather than trusted, so an entry point that can submit but cannot verify leaves
its user dependent on someone else's console.

This module states, per console capability, whether Chat reaches it. A gap may
stand only as a declared gap naming its repair and owner, so Chat can never
silently fall behind the console again.

A device is interchangeable — `physical_device_identity_gate` is
`NONE_PROHIBITED` and device identity is execution metadata only, so no
capability may ever be gated on which device is in hand. What a capability may
be conditioned on is **transportability**: a capability of a *registered node*,
conferred by registration rather than owned by any device. An entry point
reaches a transport-requiring capability when a node is registered, on whatever
device that node was established or recovered on.

Registration confers transportability and no authority. `node_user_verifier_authority`,
`device_user_verifier_authority` and `transport_user_verifier_authority` are all
NONE, and `user_verification_authority` is exclusively the KV/SKAP Vault. A node
moves data; it never vouches for anyone.

Non-authorizing. Source reconciliation only: it submits nothing, replays
nothing, reconstructs nothing and grants no execution authority.
"""
from __future__ import annotations

from datetime import date
import re
from typing import Any

SCHEMA = "stegverse.sdk.entry-point-parity/v1"

CANONICAL_TASK_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")

#: Conferred by node registration, never by a device. A capability requiring it
#: is reachable from any device on which a node is established or recovered.
TRANSPORTABILITY = "TRANSPORTABILITY"
NODE_REGISTRATION_REQUIRED = "REGISTERED_NODE_REQUIRED"

AVAILABLE = "AVAILABLE_AT_CHAT"
DECLARED_GAP = "DECLARED_GAP"
STOP_DRIFT = "STOP_ENTRY_POINT_DRIFT"

GAP_REQUIRED_FIELDS = (
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "granted_by",
    "review_by",
)

#: What a console entry offers, keyed by the selection the console presents.
#: Each row names the capability an entry point must reach to be equivalent.
CONSOLE_CAPABILITIES: dict[str, dict[str, Any]] = {
    "000": {
        "capability": "GOVERNANCE_DEMO_DATASET",
        "requires_transportability": False,
        "summary": "Run the bundled demonstration with full explanatory labels.",
    },
    "0A": {
        "capability": "SUBMIT_RAW_USER_DATA",
        "requires_transportability": True,
        "summary": "Submit raw user data and have the SDK build the governance manifest.",
    },
    "0B": {
        "capability": "SUBMIT_PREFORMATTED_MANIFEST",
        "requires_transportability": True,
        "summary": "Submit a manifest another framework already produced.",
    },
    "1": {
        "capability": "REPLAY_BY_RECEIPT_LOCATOR",
        "requires_transportability": True,
        "summary": "Replay a retained result by its manifest receipt id.",
        "verification": True,
    },
    "2": {
        "capability": "RECONSTRUCT_BY_RECEIPT_LOCATOR",
        "requires_transportability": True,
        "summary": "Reconstruct a retained result by its manifest receipt id.",
        "verification": True,
    },
    "3": {
        "capability": "COMPOSE_GOVERNED_RESPONSE",
        "requires_transportability": True,
        "summary": (
            "Compose the answers several workers returned, each from a different "
            "LLM, into one governed response and reconstruct it."
        ),
        "verification": True,
    },
    "return_projection": {
        "capability": "RETURN_PROJECTION_CONTROL",
        "requires_transportability": False,
        "summary": "Choose whether the return projects ALL, SELECTED or NONE transition classes.",
    },
    "manifest_labels": {
        "capability": "MANIFEST_LABEL_CONTROL",
        "requires_transportability": False,
        "summary": "Choose whether the returned package carries explanatory labels.",
    },
}

#: Console capabilities Chat reaches. A capability enters this set only when the
#: Chat entry contract actually carries it.
CHAT_CAPABILITIES: frozenset[str] = frozenset({
    "SUBMIT_RAW_USER_DATA",
    "SUBMIT_PREFORMATTED_MANIFEST",
    "REPLAY_BY_RECEIPT_LOCATOR",
    "RECONSTRUCT_BY_RECEIPT_LOCATOR",
    "COMPOSE_GOVERNED_RESPONSE",
    "RETURN_PROJECTION_CONTROL",
    "MANIFEST_LABEL_CONTROL",
})

#: Console capabilities Chat does not reach. A gap is granted against an
#: existing goal and expires, exactly as a capability-map exemption does.
DECLARED_GAPS: dict[str, dict[str, Any]] = {
    "GOVERNANCE_DEMO_DATASET": {
        "failed_predicate": "CHAT_ENTRY_REACHES_CONSOLE_CAPABILITY",
        "required_evidence_or_repair": (
            "carry the bundled demonstration selection through the Chat entry "
            "contract, or record that a demo belongs to the console only"
        ),
        "retry_entrypoint": "stegverse.ecosystem_chat_entry.validate_chat_entry",
        "owning_existing_goal": "SHWP-ECOSYSTEM-CHAT-INFERENCE-001",
        "registry_repository": "StegVerse-Labs/.github",
        "observed_registry_generation": 278,
        "granted_by": "StegVerse-Labs/.github:SHWP-ECOSYSTEM-CHAT-INFERENCE-001",
        "review_by": "2026-12-31",
        "current_reachability": "CONSOLE_ONLY_BUNDLED_DEMONSTRATION",
    },
}


def _expired(review_by: Any, *, today: date | None = None) -> bool:
    """True when a gap's review date has passed; a malformed date counts as expired."""
    try:
        deadline = date.fromisoformat(str(review_by))
    except (TypeError, ValueError):
        return True
    return (today or date.today()) > deadline


def reconcile_entry_point_parity() -> dict[str, Any]:
    """Return one row per console capability, saying whether Chat reaches it."""
    rows: list[dict[str, Any]] = []
    for selection, entry in CONSOLE_CAPABILITIES.items():
        capability = entry["capability"]
        reached = capability in CHAT_CAPABILITIES
        gap = DECLARED_GAPS.get(capability)
        requires_transport = bool(entry.get("requires_transportability"))
        row: dict[str, Any] = {
            "console_selection": selection,
            "capability": capability,
            "summary": entry["summary"],
            "verification_capability": bool(entry.get("verification")),
            # Conditioned on the node, never on the device.
            "requires_transportability": requires_transport,
            "precondition": NODE_REGISTRATION_REQUIRED if requires_transport else "NONE",
            "device_identity_gate": "NONE_PROHIBITED",
            "chat_entry": AVAILABLE if reached else ("DECLARED_GAP" if gap else "ABSENT"),
            "grants_execution_authority": False,
            "evidence_ceiling": "SOURCE_RECONCILIATION_ONLY",
        }
        if reached:
            row["disposition"] = AVAILABLE
        elif gap:
            row["disposition"] = DECLARED_GAP
            row.update(gap)
            row["gap_expired"] = _expired(gap.get("review_by"))
        else:
            row["disposition"] = STOP_DRIFT
            row["failed_predicate"] = "CHAT_ENTRY_REACHES_CONSOLE_CAPABILITY"
            row["required_evidence_or_repair"] = (
                f"carry {capability} through the Chat entry contract, or declare a "
                "gap naming its repair and owner"
            )
            row["retry_entrypoint"] = "python -m unittest tests.test_entry_point_parity"
            row["owning_existing_goal"] = "SHWP-ECOSYSTEM-CHAT-INFERENCE-001"
        rows.append(row)

    verification = [r for r in rows if r["verification_capability"]]
    return {
        "schema": SCHEMA,
        "console_capability_count": len(rows),
        "available_at_chat_count": sum(1 for r in rows if r["disposition"] == AVAILABLE),
        "declared_gap_count": sum(1 for r in rows if r["disposition"] == DECLARED_GAP),
        "drift_count": sum(1 for r in rows if r["disposition"] == STOP_DRIFT),
        "expired_gap_count": sum(1 for r in rows if r.get("gap_expired") is True),
        # The point of the exercise: a mobile user must be able to verify, not
        # only submit. A verification capability is never an acceptable gap.
        "verification_capabilities": [r["capability"] for r in verification],
        # What an unregistered entry point reaches. Naming this is the point:
        # the limit is registration, which anyone may obtain, not a device.
        "requires_transportability": [
            r["capability"] for r in rows if r["requires_transportability"]
        ],
        "available_without_node_registration": [
            r["capability"] for r in rows
            if not r["requires_transportability"] and r["disposition"] == AVAILABLE
        ],
        "transportability_conferred_by": "NODE_REGISTRATION",
        "transportability_conferred_by_device": False,
        "node_confers_user_verifier_authority": False,
        "verification_available_at_chat": all(
            r["disposition"] == AVAILABLE for r in verification
        ),
        "rows": tuple(rows),
        "grants_execution_authority": False,
        "authority_effect": "NONE_RECONCILIATION_ONLY",
    }


__all__ = [
    "AVAILABLE", "CANONICAL_TASK_ID", "NODE_REGISTRATION_REQUIRED", "TRANSPORTABILITY", "CHAT_CAPABILITIES", "CONSOLE_CAPABILITIES",
    "DECLARED_GAP", "DECLARED_GAPS", "GAP_REQUIRED_FIELDS", "SCHEMA", "STOP_DRIFT",
    "reconcile_entry_point_parity",
]
