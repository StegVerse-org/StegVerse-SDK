"""Source-bound SDK consumer for governed StegVerse edge-cell evidence.

This module validates a committed compatibility binding owned by the SDK. It
never executes the edge cell, re-evaluates runtime admissibility, grants a
conditional capability, or asserts downstream custody.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

SCHEMA_VERSION = "stegverse.sdk.edge_cell_source_binding.v1"
CANONICAL_SOURCE_REPOSITORY = "StegVerse-002/micro-node-runtime"
CANONICAL_SOURCE_COMMIT = "c9660dd0dffd97d9ececc9b7428ef165ae212419"
CANONICAL_PROFILE_ID = "stegverse.edge-cell.governed.v1"
CANONICAL_PROFILE_VERSION = "1.0.0"
CANONICAL_PROFILE_SHA256 = (
    "0a31dabd5ba8e8f5e526a087b4194eccca1456c693546c742ccf9b2fab945ab1"
)
CANONICAL_ACTIVATION_INPUT_SHA256 = (
    "a90a33fb74205e947146f2098e020a299c9e29a50ddf2c8a9cafad759646ea2c"
)
CANONICAL_ACTIVATION_RECEIPT_SHA256 = (
    "c546a4addf80eebead9cc17324fad7580d6d5050c5347e86969c91d8d9cf7299"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "source",
    "profile",
    "activation_receipt",
    "custody",
    "non_claims",
}
EXPECTED_SOURCE_KEYS = {
    "repository",
    "commit",
    "profile_path",
    "activation_evidence_path",
    "profile_sha256",
    "activation_input_sha256",
}
EXPECTED_PROFILE_KEYS = {
    "profile_id",
    "profile_version",
    "node_class",
    "authority_effect",
    "execution_pattern",
    "base_capabilities",
    "conditional_capabilities",
    "governance_controls",
    "degraded_mode",
    "federation",
}
EXPECTED_RECEIPT_KEYS = {
    "receipt_type",
    "receipt_id",
    "receipt_hash",
    "state",
    "authority_effect",
}
EXPECTED_CUSTODY_KEYS = {"status", "destination_receipt_ref"}
EXPECTED_NON_CLAIMS = {
    "sdk_acceptance_is_execution_authority": False,
    "sdk_acceptance_is_admissibility": False,
    "sdk_acceptance_is_custody": False,
    "source_receipt_is_destination_custody": False,
    "conditional_capabilities_are_activated": False,
}
EXPECTED_EXECUTION_PATTERN = [
    "PROPOSE",
    "GOVERN",
    "EXECUTE",
    "VERIFY",
    "RECEIPT",
    "RECONSTRUCT",
]
EXPECTED_BASE_CAPABILITIES = {
    "LOCAL_INFERENCE",
    "LOCAL_KNOWLEDGE_RETRIEVAL",
    "SENSOR_OBSERVATION",
    "SEGMENTED_STORAGE",
    "RECEIPT_LEDGER",
    "STORE_AND_FORWARD",
    "MESH_RELAY",
    "HEALTH_TELEMETRY",
    "CONTINUITY_RECOVERY",
}
EXPECTED_CONDITIONAL_CAPABILITIES = {
    "PHYSICAL_ACTUATION",
    "EXTERNAL_EXPORT",
    "FEDERATED_COMMIT",
}


@dataclass(frozen=True)
class EdgeCellConsumerResult:
    """Deterministic, non-authorizing SDK compatibility result."""

    accepted: bool
    status: str
    source_repository: str
    source_commit: str
    profile_id: str
    profile_version: str
    activation_state: str
    binding_sha256: str
    errors: tuple[str, ...]
    non_claims: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "status": self.status,
            "source_repository": self.source_repository,
            "source_commit": self.source_commit,
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "activation_state": self.activation_state,
            "binding_sha256": self.binding_sha256,
            "errors": list(self.errors),
            "non_claims": dict(self.non_claims),
        }


def stable_edge_cell_binding_hash(binding: Mapping[str, Any]) -> str:
    """Return the canonical JSON SHA-256 of an SDK source binding."""

    encoded = json.dumps(
        binding,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_edge_cell_source_binding(
    binding: Mapping[str, Any],
) -> EdgeCellConsumerResult:
    """Validate the accepted micro-node edge-cell source binding fail closed."""

    if not isinstance(binding, Mapping):
        return _result({}, ["edge-cell source binding must be an object"])

    errors: list[str] = []
    if set(binding) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append("top-level keys do not match the SDK edge-cell contract")

    if binding.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version is not supported")

    source = _mapping(binding.get("source"), "source", errors)
    profile = _mapping(binding.get("profile"), "profile", errors)
    receipt = _mapping(binding.get("activation_receipt"), "activation_receipt", errors)
    custody = _mapping(binding.get("custody"), "custody", errors)
    non_claims = _mapping(binding.get("non_claims"), "non_claims", errors)

    _require_exact_keys(source, EXPECTED_SOURCE_KEYS, "source", errors)
    _require_exact_keys(profile, EXPECTED_PROFILE_KEYS, "profile", errors)
    _require_exact_keys(receipt, EXPECTED_RECEIPT_KEYS, "activation_receipt", errors)
    _require_exact_keys(custody, EXPECTED_CUSTODY_KEYS, "custody", errors)

    if source.get("repository") != CANONICAL_SOURCE_REPOSITORY:
        errors.append("source.repository is not the canonical runtime")
    if source.get("commit") != CANONICAL_SOURCE_COMMIT:
        errors.append("source.commit does not match the accepted runtime commit")
    if source.get("profile_path") != "profiles/governed_edge_cell.v1.json":
        errors.append("source.profile_path is not canonical")
    if (
        source.get("activation_evidence_path")
        != "examples/edge_cell_activation_evidence.generated.json"
    ):
        errors.append("source.activation_evidence_path is not canonical")
    if source.get("profile_sha256") != CANONICAL_PROFILE_SHA256:
        errors.append("source.profile_sha256 does not match accepted evidence")
    if source.get("activation_input_sha256") != CANONICAL_ACTIVATION_INPUT_SHA256:
        errors.append("source.activation_input_sha256 does not match accepted evidence")

    if profile.get("profile_id") != CANONICAL_PROFILE_ID:
        errors.append("profile.profile_id is not canonical")
    if profile.get("profile_version") != CANONICAL_PROFILE_VERSION:
        errors.append("profile.profile_version is not supported")
    if profile.get("node_class") != "GOVERNED_EDGE_CELL":
        errors.append("profile.node_class must be GOVERNED_EDGE_CELL")
    if profile.get("authority_effect") != "NONE":
        errors.append("profile authority expansion is prohibited")
    if profile.get("execution_pattern") != EXPECTED_EXECUTION_PATTERN:
        errors.append("profile execution pattern is not canonical")
    if set(profile.get("base_capabilities", [])) != EXPECTED_BASE_CAPABILITIES:
        errors.append("profile base capabilities do not match the accepted source")
    if (
        set(profile.get("conditional_capabilities", []))
        != EXPECTED_CONDITIONAL_CAPABILITIES
    ):
        errors.append("profile conditional capabilities do not match the accepted source")

    controls = _mapping(profile.get("governance_controls"), "profile.governance_controls", errors)
    if controls.get("direct_model_actuation") != "DENY":
        errors.append("direct model actuation must remain denied")
    if controls.get("external_export_default") != "DENY":
        errors.append("external export must remain denied by default")
    if controls.get("missing_evidence_behavior") != "FAIL_CLOSED":
        errors.append("missing evidence behavior must remain fail closed")

    degraded = _mapping(profile.get("degraded_mode"), "profile.degraded_mode", errors)
    if degraded.get("authority_behavior") != "REDUCE_CAPABILITY":
        errors.append("degraded operation cannot expand authority")
    if degraded.get("network_loss_mode") != "LOCAL_ONLY":
        errors.append("network loss mode must remain local only")
    if degraded.get("receipt_integrity_failure") != "FAIL_CLOSED":
        errors.append("receipt integrity failure must fail closed")
    if degraded.get("continuity_failure") != "FAIL_CLOSED":
        errors.append("continuity failure must fail closed")

    federation = _mapping(profile.get("federation"), "profile.federation", errors)
    if federation.get("quorum_required") is not True:
        errors.append("federated commit must require quorum")
    if federation.get("single_node_unilateral_commit") is not False:
        errors.append("single-node unilateral federated commit must remain disabled")

    if receipt.get("receipt_type") != "EDGE_CELL_ACTIVATION_EVALUATION":
        errors.append("activation receipt type is not supported")
    if receipt.get("receipt_hash") != CANONICAL_ACTIVATION_RECEIPT_SHA256:
        errors.append("activation receipt hash does not match the accepted source")
    if receipt.get("receipt_id") != "edge-cell-activation:c546a4addf80eebead9cc173":
        errors.append("activation receipt id does not match the accepted source")
    if receipt.get("state") != "ACTIVE":
        errors.append("accepted source activation state must be ACTIVE")
    if receipt.get("authority_effect") != "NONE":
        errors.append("activation receipt authority expansion is prohibited")

    if custody.get("status") != "SOURCE_GENERATED_NOT_DESTINATION_ACCEPTED":
        errors.append("custody status must remain source generated and unaccepted")
    if custody.get("destination_receipt_ref") is not None:
        errors.append("SDK fixture cannot assert a destination custody receipt")

    for key, expected in EXPECTED_NON_CLAIMS.items():
        if non_claims.get(key) is not expected:
            errors.append(f"non_claims.{key} must be false")
    if set(non_claims) != set(EXPECTED_NON_CLAIMS):
        errors.append("non_claims keys do not match the SDK edge-cell contract")

    return _result(binding, errors)


def _mapping(value: Any, label: str, errors: list[str]) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    errors.append(f"{label} must be an object")
    return {}


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: set[str],
    label: str,
    errors: list[str],
) -> None:
    if set(value) != expected:
        errors.append(f"{label} keys do not match the SDK edge-cell contract")


def _result(
    binding: Mapping[str, Any],
    errors: list[str],
) -> EdgeCellConsumerResult:
    source = binding.get("source") if isinstance(binding, Mapping) else {}
    profile = binding.get("profile") if isinstance(binding, Mapping) else {}
    receipt = binding.get("activation_receipt") if isinstance(binding, Mapping) else {}
    source = source if isinstance(source, Mapping) else {}
    profile = profile if isinstance(profile, Mapping) else {}
    receipt = receipt if isinstance(receipt, Mapping) else {}
    accepted = not errors
    return EdgeCellConsumerResult(
        accepted=accepted,
        status=(
            "accepted_for_non_authorizing_sdk_consumption"
            if accepted
            else "rejected_fail_closed"
        ),
        source_repository=str(source.get("repository", "")),
        source_commit=str(source.get("commit", "")),
        profile_id=str(profile.get("profile_id", "")),
        profile_version=str(profile.get("profile_version", "")),
        activation_state=str(receipt.get("state", "")),
        binding_sha256=(stable_edge_cell_binding_hash(binding) if binding else ""),
        errors=tuple(sorted(set(errors))),
        non_claims={
            "sdk_acceptance_is_execution_authority": False,
            "sdk_acceptance_is_admissibility": False,
            "sdk_acceptance_is_custody": False,
            "source_receipt_is_destination_custody": False,
            "conditional_capabilities_are_activated": False,
        },
    )
