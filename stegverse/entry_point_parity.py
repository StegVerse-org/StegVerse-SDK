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
#: Carried by the Chat entry contract but not performed by the deployed Chat
#: surface. This distinction exists because the map once could not make it: a
#: capability read AVAILABLE_AT_CHAT while the surface served no operation at
#: all, so the report was green about something a phone could not do.
CONTRACT_ONLY = "CONTRACT_CARRIED_NOT_SERVED_BY_SURFACE"

#: What replay and reconstruction establish, and what they do not.
#:
#: They display state transition paths and make decisions verifiable from the
#: Ecosystem. That is ecosystem-side evidence, and it is what a receipt locator
#: addresses. They do not return the prose: the actual question text and the
#: actual answer text are not what custody retains.
VERIFIES_TRANSITIONS_AND_DECISIONS = ("STATE_TRANSITION_PATH", "DECISION")

#: Retaining prose is a different capability with a different owner. The
#: Ecosystem does not store the query and response text; that requires storage
#: which is user-based, and MyKV is where it lives. Chat continuity therefore
#: comes from MyKV, and the individual Ecosystem AI Assistant lives there with
#: Ecosystem Chat as its precursor. Conflating the two would suggest that
#: replaying a receipt hands a person their conversation back. It does not.
PROSE_RETENTION_STORAGE = "USER_BASED_MYKV"

#: This is not a new claim: the security postures already prohibit raw sensitive
#: data in an audit receipt. It is read from them rather than restated here,
#: because a second declaration is a second thing that can drift from what it
#: describes -- the same reason the Chat reachability claim is exercised rather
#: than trusted.
#:
#: Reading it turned up something worth surfacing rather than smoothing over: the
#: prohibition is declared at HIGH and HIGHEST but not at SECURE, whose
#: prohibitions list only undeclared_sink and runtime_secret_inheritance. So the
#: report states where it is declared instead of claiming it everywhere.
PROSE_PROHIBITION = "raw_sensitive_data_in_audit_receipt"


def _prose_prohibition_by_posture() -> dict[str, bool]:
    """Which declared postures prohibit raw sensitive data in an audit receipt."""
    from .security_posture import POSTURES

    return {
        posture_id: bool((posture.get("prohibitions") or {}).get(PROSE_PROHIBITION))
        for posture_id, posture in POSTURES.items()
    }
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
        "verifies": VERIFIES_TRANSITIONS_AND_DECISIONS,
        "retains_prose": False,
        "summary": "Replay a retained result by its manifest receipt id.",
        "verification": True,
    },
    "2": {
        "capability": "RECONSTRUCT_BY_RECEIPT_LOCATOR",
        "requires_transportability": True,
        "verifies": VERIFIES_TRANSITIONS_AND_DECISIONS,
        "retains_prose": False,
        "summary": "Reconstruct a retained result by its manifest receipt id.",
        "verification": True,
    },
    "4": {
        "capability": "ASK_GOVERNED_QUESTION",
        "requires_transportability": True,
        "summary": (
            "Ask the ecosystem a question and get one governed answer, composed "
            "from several workers each calling a different LLM."
        ),
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
    "ASK_GOVERNED_QUESTION",
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


def _surface_served_capabilities() -> frozenset[str]:
    """Capabilities the deployed Chat surface actually performs.

    Read from the dispatcher, not declared here: a second declaration would be
    another constant to drift out of step with the surface it describes.
    """
    from .ecosystem_chat_entry import OPERATIONS
    from .ecosystem_chat_operations import SERVED_OPERATIONS

    return frozenset(
        OPERATIONS[op] for op in SERVED_OPERATIONS if op in OPERATIONS
    )


def _expired(review_by: Any, *, today: date | None = None) -> bool:
    """True when a gap's review date has passed; a malformed date counts as expired."""
    try:
        deadline = date.fromisoformat(str(review_by))
    except (TypeError, ValueError):
        return True
    return (today or date.today()) > deadline


def reconcile_entry_point_parity() -> dict[str, Any]:
    """Return one row per console capability, saying whether Chat reaches it."""
    served = _surface_served_capabilities()
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
            # Two different questions, and conflating them is what let the map
            # read green while the surface served nothing.
            "carried_by_chat_contract": reached,
            "served_by_chat_surface": capability in served,
            # What this capability makes verifiable from the Ecosystem, and
            # whether it hands back the prose. Nothing here retains prose.
            "verifies": list(entry.get("verifies") or []),
            "retains_prose": bool(entry.get("retains_prose")),
            "grants_execution_authority": False,
            "evidence_ceiling": "SOURCE_RECONCILIATION_ONLY",
        }
        if reached:
            row["disposition"] = AVAILABLE if capability in served else CONTRACT_ONLY
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
        # Carried by the contract, not performed by the surface. Counted so the
        # distance between what Chat declares and what it serves stays visible.
        "contract_only_count": sum(1 for r in rows if r["disposition"] == CONTRACT_ONLY),
        # Replay and reconstruction make transitions and decisions verifiable;
        # neither returns the prose, and the Ecosystem does not retain it.
        "capabilities_verifying_transitions": [
            r["capability"] for r in rows if r["verifies"]
        ],
        "capabilities_retaining_prose": [
            r["capability"] for r in rows if r["retains_prose"]
        ],
        # Named so a reader can check the source rather than trust this row, and
        # reported per posture because it is not declared in all of them.
        "prose_prohibited_by": PROSE_PROHIBITION,
        "prose_prohibition_by_posture": _prose_prohibition_by_posture(),
        "postures_prohibiting_prose": sorted(
            pid for pid, on in _prose_prohibition_by_posture().items() if on),
        "postures_not_declaring_prose_prohibition": sorted(
            pid for pid, on in _prose_prohibition_by_posture().items() if not on),
        "prose_retention_storage": PROSE_RETENTION_STORAGE,
        "chat_continuity_requires": PROSE_RETENTION_STORAGE,
        "contract_only_capabilities": [
            r["capability"] for r in rows if r["disposition"] == CONTRACT_ONLY
        ],
        "served_by_chat_surface": [
            r["capability"] for r in rows if r["served_by_chat_surface"]
        ],
        "declared_gap_count": sum(1 for r in rows if r["disposition"] == DECLARED_GAP),
        "drift_count": sum(1 for r in rows if r["disposition"] == STOP_DRIFT),
        "expired_gap_count": sum(1 for r in rows if r.get("gap_expired") is True),
        # The point of the exercise: a mobile user must be able to verify, not
        # only submit. A verification capability is never an acceptable gap.
        "verification_capabilities": [r["capability"] for r in verification],
        # A verification capability the contract carries but the surface does
        # not serve still leaves a phone unable to check that result.
        "verification_contract_only": [
            r["capability"] for r in verification
            if r["disposition"] == CONTRACT_ONLY
        ],

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
        # True when a phone can verify *something* end to end on the surface.
        # The per-capability picture is verification_contract_only above, which
        # is what says how much verification is still console-only.
        "verification_available_at_chat": any(
            r["served_by_chat_surface"] for r in verification
        ),
        "verification_served_by_surface": [
            r["capability"] for r in verification if r["served_by_chat_surface"]
        ],
        "rows": tuple(rows),
        "grants_execution_authority": False,
        "authority_effect": "NONE_RECONCILIATION_ONLY",
    }


__all__ = [
    "AVAILABLE", "CANONICAL_TASK_ID", "CONTRACT_ONLY",
    "PROSE_PROHIBITION", "PROSE_RETENTION_STORAGE",
    "VERIFIES_TRANSITIONS_AND_DECISIONS", "NODE_REGISTRATION_REQUIRED", "TRANSPORTABILITY", "CHAT_CAPABILITIES", "CONSOLE_CAPABILITIES",
    "DECLARED_GAP", "DECLARED_GAPS", "GAP_REQUIRED_FIELDS", "SCHEMA", "STOP_DRIFT",
    "reconcile_entry_point_parity",
]
