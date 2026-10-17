"""Source-only manifest path differential verification.

This module compares supplied snapshots; it does not authenticate evidence, issue
governance dispositions, run experiments, or authorize remediation.
"""
from __future__ import annotations

from typing import Any, Mapping

_FIELDS = ("manifest_digest", "route_id", "component_id", "predicate_id", "policy_version", "authority_binding")
_FINDINGS = frozenset({
    "EXPECTED_GOVERNED_DENY", "REASONING_REVIEW_REQUIRED",
    "MANIFEST_BUILDER_DEFECT_CANDIDATE", "EXECUTION_PATH_DEFECT_CANDIDATE",
    "REQUIREMENTS_AMBIGUOUS", "CAPABILITY_GAP_IDENTIFIED",
    "INSUFFICIENT_AUTHENTIC_EVIDENCE",
})


def compare_manifest_paths(
    original: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    *,
    finding: str = "INSUFFICIENT_AUTHENTIC_EVIDENCE",
) -> dict[str, Any]:
    """Compare declared paths without interpreting a refusal as experiment failure.

    Evidence references are locators, not proof of authenticated readback. A
    diagnostic finding is a non-authorizing candidate pending owner validation.
    """
    if finding not in _FINDINGS:
        raise ValueError("unsupported diagnostic finding")
    for label, snapshot in (("original", original), ("diagnostic", diagnostic)):
        if not isinstance(snapshot, Mapping):
            raise ValueError(f"{label} snapshot must be a mapping")
        for key in ("manifest_digest", "route_id", "predicate_id"):
            if not isinstance(snapshot.get(key), str) or not snapshot[key].strip():
                raise ValueError(f"{label}.{key} is required")
        refs = snapshot.get("evidence_refs", [])
        if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
            raise ValueError(f"{label}.evidence_refs must be nonempty strings")
    deltas = [
        {"field": key, "original": original.get(key), "diagnostic": diagnostic.get(key)}
        for key in _FIELDS if original.get(key) != diagnostic.get(key)
    ]
    original_disposition = original.get("disposition")
    if original_disposition not in ("DENY", "FAIL_CLOSED"):
        raise ValueError("original disposition must be DENY or FAIL_CLOSED")
    refs = list(dict.fromkeys(original.get("evidence_refs", []) + diagnostic.get("evidence_refs", [])))
    return {
        "schema": "stegverse.mpdv-source-comparison.v1",
        "original_disposition": original_disposition,
        "original_manifest_digest": original["manifest_digest"],
        "diagnostic_manifest_digest": diagnostic["manifest_digest"],
        "path_deltas": deltas,
        "finding_candidate": finding,
        "evidence_refs": refs,
        "authentic_readback_verified": False,
        "experiment_result_established": False,
        "remediation_authorized": False,
        "mutation_performed": False,
        "authority_effect": "NONE_DIAGNOSTIC_ONLY",
    }
