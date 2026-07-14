"""Cross-repository activation gate for system-boundary verification.

This gate combines independently validated workflow evidence from LLM-adapter and
StegVerse-SDK. It does not execute workflows, authorize release, enable production
binding, transfer custody, or determine admissibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .system_boundary_workflow_evidence import validate_workflow_evidence as validate_sdk_evidence


@dataclass(frozen=True)
class ActivationResult:
    accepted: bool
    verified: bool
    state: str
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "verified": self.verified,
            "state": self.state,
            "errors": list(self.errors),
        }


def _validate_adapter_evidence(record: Mapping[str, Any]) -> tuple[bool, bool, tuple[str, ...]]:
    required = {
        "schema_version", "repository", "workflow", "required_commit",
        "observed_commit", "run_id", "run_url", "result",
        "production_binding_enabled", "release_authorized",
    }
    errors: list[str] = []
    if not isinstance(record, Mapping) or set(record) != required:
        return False, False, ("adapter evidence keys do not match required contract",)
    if record["schema_version"] != "stegverse.system_boundary.workflow_evidence.v0.1":
        errors.append("unsupported adapter schema_version")
    if record["repository"] != "StegVerse-org/LLM-adapter":
        errors.append("adapter repository mismatch")
    if record["workflow"] != ".github/workflows/validate.yml":
        errors.append("adapter workflow mismatch")
    if record["result"] not in {"PENDING", "PASS", "FAIL"}:
        errors.append("adapter result must be PENDING, PASS, or FAIL")
    if record["production_binding_enabled"] is not False:
        errors.append("adapter production binding must remain false")
    if record["release_authorized"] is not False:
        errors.append("adapter release authorization must remain false")

    result = record.get("result")
    if result == "PENDING":
        for key in ("observed_commit", "run_id", "run_url"):
            if record.get(key) is not None:
                errors.append(f"adapter {key} must be null while PENDING")
    else:
        for key in ("observed_commit", "run_id", "run_url"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                errors.append(f"adapter {key} is required when {result}")
        if result == "PASS" and record.get("observed_commit") != record.get("required_commit"):
            errors.append("adapter PASS must be bound to required_commit")
    return not errors, not errors and result == "PASS", tuple(errors)


def evaluate_system_boundary_activation(
    adapter_evidence: Mapping[str, Any],
    sdk_evidence: Mapping[str, Any],
) -> ActivationResult:
    adapter_accepted, adapter_verified, adapter_errors = _validate_adapter_evidence(adapter_evidence)
    sdk_result = validate_sdk_evidence(sdk_evidence)

    errors = list(adapter_errors) + [f"sdk: {error}" for error in sdk_result.errors]
    if not adapter_accepted or not sdk_result.accepted:
        return ActivationResult(False, False, "INVALID_EVIDENCE", tuple(errors))
    if adapter_evidence["result"] == "FAIL" or sdk_evidence["result"] == "FAIL":
        return ActivationResult(True, False, "FAILED", ())
    if adapter_verified and sdk_result.verified:
        return ActivationResult(True, True, "VERIFIED", ())
    return ActivationResult(True, False, "PENDING", ())
