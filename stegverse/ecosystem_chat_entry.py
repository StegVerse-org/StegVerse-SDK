"""The Ecosystem Chat entry point, as an equal of a console entry.

Chat does not build. It interfaces with the builder: a raw submission carries
the user's data and declared goal to the Manifest Builder and names the builder
call the console would make, rather than constructing a manifest of its own. A
preformatted submission carries someone else's manifest through unchanged.

Chat also verifies. Replay and reconstruction by receipt locator are how a
result is checked rather than trusted, and an entry point that can submit but
not verify leaves its user dependent on someone else's console — which is the
position a mobile evaluator was actually left in during Tests 1-3. Both
operations are therefore first-class here, and each names the exact fields a
person has to compare, so the check is legible on a phone instead of requiring a
terminal.

Non-authorizing. This validates and normalizes a request. It builds no manifest,
submits nothing, replays nothing, reconstructs nothing, mints no receipt and
grants no execution authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from .governed_composite_response import STRATEGIES, STRATEGY_UNANIMOUS
from .governance_navigation import (
    normalize_manifest_labels,
    normalize_return_projection,
    validate_manifest_receipt_id,
)

SCHEMA = "stegverse.ecosystem-chat-entry-request/v1"

SUBMIT_RAW = "0A"
SUBMIT_MANIFEST = "0B"
REPLAY = "1"
RECONSTRUCT = "2"
COMPOSE = "3"

#: Chat's operations, named by the same selection the console presents, so the
#: two entry points are comparable rather than merely similar.
OPERATIONS: dict[str, str] = {
    SUBMIT_RAW: "SUBMIT_RAW_USER_DATA",
    SUBMIT_MANIFEST: "SUBMIT_PREFORMATTED_MANIFEST",
    REPLAY: "REPLAY_BY_RECEIPT_LOCATOR",
    RECONSTRUCT: "RECONSTRUCT_BY_RECEIPT_LOCATOR",
    COMPOSE: "COMPOSE_GOVERNED_RESPONSE",
}

VERIFICATION_OPERATIONS = frozenset({REPLAY, RECONSTRUCT})
RECEIPT_LOCATOR_OPERATIONS = frozenset({REPLAY, RECONSTRUCT})

#: What a person has to compare for a verification to mean anything. Naming
#: these on the request is what makes the check possible away from a console:
#: the equality is the verification, and it is legible at a glance.
VERIFICATION_FIELDS: tuple[str, ...] = (
    "manifest_receipt_id",
    "receipt_sha256",
    "reconstructed_receipt_sha256",
    "reconstruction_status",
    "immediate_predecessor_receipt_sha256",
    "consequence_reexecuted",
)


#: What a person compares to check a composite away from a console. A composite
#: that agrees with its own reconstruction is verified; one that does not is not,
#: and the comparison is two digests side by side.
COMPOSITION_VERIFICATION_FIELDS: tuple[str, ...] = (
    "composite_sha256",
    "reconstructed_composite_sha256",
    "reconstruction_status",
    "selected_answer_sha256",
    "distinct_answer_count",
    "unanimous",
    "disposition",
    "governed_claim",
)


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def validate_chat_entry(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize a Chat entry request into its console-equivalent form."""
    if not isinstance(payload, Mapping) or payload.get("schema") != SCHEMA:
        raise ValueError(f"chat entry schema must be {SCHEMA}")
    operation = str(payload.get("operation") or "").strip().upper()
    if operation not in OPERATIONS:
        raise ValueError(
            "operation must be one of " + ", ".join(sorted(OPERATIONS))
        )

    entry: dict[str, Any] = {
        "schema": SCHEMA,
        "entry_point": "ECOSYSTEM_CHAT",
        "operation": operation,
        "capability": OPERATIONS[operation],
        # Every entry point projects and labels its own return; neither controls
        # what custody retains.
        "return_projection": normalize_return_projection(payload.get("return_projection")),
        "manifest_labels": normalize_manifest_labels(payload.get("manifest_labels")),
        "console_equivalent_selection": operation,
        "chat_builds_manifest": False,
        "grants_execution_authority": False,
        "authority_effect": "NONE_ENTRY_REQUEST_ONLY",
    }

    if operation == SUBMIT_RAW:
        # Chat interfaces with the builder; it does not build. The raw data and
        # declared goal go to the Manifest Builder, which produces the manifest.
        entry["raw_submission"] = {
            "user_request": _text(payload.get("user_request"), "user_request"),
            "declared_goal": _text(payload.get("declared_goal"), "declared_goal"),
        }
        source_framework = payload.get("source_framework")
        entry["builder_directive"] = {
            "builder": "stegverse.manifest_builder.build_manifest",
            "source_framework": (_text(source_framework, "source_framework")
                                 if source_framework is not None else "EcosystemChat"),
            "manifest_constructed_by_chat": False,
        }
    elif operation == SUBMIT_MANIFEST:
        manifest = payload.get("manifest")
        if not isinstance(manifest, Mapping) or not manifest:
            raise ValueError("a preformatted submission requires a manifest object")
        entry["preformatted_manifest"] = dict(manifest)
        entry["builder_directive"] = {
            "builder": "stegverse.manifest_contract.validate_ingress_manifest",
            "manifest_constructed_by_chat": False,
        }
    elif operation == COMPOSE:
        # Chat poses the query and reads the composite back. It does not compose:
        # composition is deterministic over the workers' returned answers, and
        # Chat neither selects an answer nor generates one.
        components = payload.get("components")
        if not isinstance(components, list) or len(components) < 2:
            raise ValueError("a composition requires at least two worker components")
        strategy = str(payload.get("strategy") or STRATEGY_UNANIMOUS).strip().upper()
        if strategy not in STRATEGIES:
            raise ValueError("strategy must be one of " + ", ".join(sorted(STRATEGIES)))
        entry["composition_request"] = {
            "composition_id": _text(payload.get("composition_id"), "composition_id"),
            "fan_journey_id": _text(payload.get("fan_journey_id"), "fan_journey_id"),
            "strategy": strategy,
            "component_count": len(components),
            "components": [dict(c) for c in components if isinstance(c, Mapping)],
        }
        entry["composer_directive"] = {
            "composer": "stegverse.governed_composite_response.compose_governed_response",
            "composite_selected_by_chat": False,
            "answer_generated_by_chat": False,
        }
        entry["verification"] = {
            "operation": OPERATIONS[operation],
            "compare_fields": list(COMPOSITION_VERIFICATION_FIELDS),
            "consequence_reexecuted_expected": False,
            "verified_when": (
                "composite_sha256 equals reconstructed_composite_sha256 and "
                "reconstruction_status is RECONSTRUCTED"
            ),
            "legible_without_a_console": True,
        }
    else:
        entry["manifest_receipt_id"] = validate_manifest_receipt_id(
            _text(payload.get("manifest_receipt_id"), "manifest_receipt_id")
        )
        entry["verification"] = {
            "operation": OPERATIONS[operation],
            "compare_fields": list(VERIFICATION_FIELDS),
            # Reconstruction re-derives a retained receipt; it never re-executes
            # the consequence, and a returned result claiming otherwise is not a
            # verification.
            "consequence_reexecuted_expected": False,
            "verified_when": (
                "receipt_sha256 equals reconstructed_receipt_sha256 and "
                "reconstruction_status is PASS"
            ),
            "legible_without_a_console": True,
        }
    return entry


def console_equivalent_request(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Project a validated Chat entry onto the console's own operation shape.

    The console and Chat hand the same request to the same handlers; only the
    entry point differs. This returns what a console selection would produce so
    neither path can drift into its own dialect.
    """
    operation = entry["operation"]
    request: dict[str, Any] = {
        "selection": operation,
        "capability": entry["capability"],
        "return_projection": entry["return_projection"],
        "manifest_labels": entry["manifest_labels"],
        "originating_entry_point": entry["entry_point"],
    }
    if operation in RECEIPT_LOCATOR_OPERATIONS:
        request["manifest_receipt_id"] = entry["manifest_receipt_id"]
    elif operation == COMPOSE:
        request["composition"] = dict(entry["composition_request"])
    elif operation == SUBMIT_RAW:
        request["raw_submission"] = dict(entry["raw_submission"])
    else:
        request["manifest"] = dict(entry["preformatted_manifest"])
    return request


__all__ = [
    "COMPOSE", "COMPOSITION_VERIFICATION_FIELDS", "OPERATIONS",
    "RECEIPT_LOCATOR_OPERATIONS", "RECONSTRUCT", "REPLAY", "SCHEMA",
    "SUBMIT_MANIFEST",
    "SUBMIT_RAW", "VERIFICATION_FIELDS", "VERIFICATION_OPERATIONS",
    "console_equivalent_request", "validate_chat_entry",
]
