"""Source-only manifest path differential verification.

This module compares supplied snapshots; it does not authenticate evidence, issue
governance dispositions, run experiments, or authorize remediation.

Owning goal: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001 / COSV 71000000101000.

Every refusal is a six-field FAIL_CLOSED carried on
``ManifestPathDifferentialRefusal.refusal``. The exception subclasses
``ValueError`` so existing callers that catch ``ValueError`` keep working.
"""
from __future__ import annotations

from typing import Any, Mapping

OWNING_EXISTING_GOAL = "SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001"
RETRY_ENTRYPOINT = "stegverse/manifest_path_differential.py::compare_manifest_paths"
SCHEMA = "stegverse.mpdv-source-comparison.v1"

_FIELDS = ("manifest_digest", "route_id", "component_id", "predicate_id", "policy_version", "authority_binding")
_REQUIRED = ("manifest_digest", "route_id", "predicate_id")
_DISPOSITIONS = ("ALLOW", "DENY", "FAIL_CLOSED")
_NON_ALLOW = ("DENY", "FAIL_CLOSED")
_FINDINGS = frozenset({
    "EXPECTED_GOVERNED_DENY", "REASONING_REVIEW_REQUIRED",
    "MANIFEST_BUILDER_DEFECT_CANDIDATE", "EXECUTION_PATH_DEFECT_CANDIDATE",
    "REQUIREMENTS_AMBIGUOUS", "CAPABILITY_GAP_IDENTIFIED",
    "INSUFFICIENT_AUTHENTIC_EVIDENCE",
})
# The only finding that may be reported with no evidence locator at all: it is
# the statement that evidence is absent. Every other finding is a claim about
# the compared paths and must name the locators it rests on.
_EVIDENCE_FREE_FINDING = "INSUFFICIENT_AUTHENTIC_EVIDENCE"


class ManifestPathDifferentialRefusal(ValueError):
    """A comparison that could not be made; ``refusal`` holds the six-field FAIL_CLOSED."""

    def __init__(self, refusal: dict[str, Any]):
        super().__init__(f"{refusal['failure_code']}: {refusal['required_evidence_or_repair']}")
        self.refusal = refusal


def _refuse(failure_code: str, failed_predicate: str, repair: str) -> ManifestPathDifferentialRefusal:
    return ManifestPathDifferentialRefusal({
        "schema": SCHEMA,
        "disposition": "FAIL_CLOSED",
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": RETRY_ENTRYPOINT,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": "re-run the comparison with the corrected snapshots; no finding is presumed until then",
        "authority_effect": "NONE_REFUSAL_ONLY",
    })


def _evidence_refs(label: str, snapshot: Mapping[str, Any]) -> list[str]:
    refs = snapshot.get("evidence_refs", [])
    if not isinstance(refs, list) or not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise _refuse(
            "MPDV_EVIDENCE_REFS_MALFORMED",
            "EVIDENCE_REFS_ARE_A_LIST_OF_NONEMPTY_STRINGS",
            f"{label}.evidence_refs must be a list of non-blank locator strings",
        )
    return refs


def compare_manifest_paths(
    original: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    *,
    finding: str = _EVIDENCE_FREE_FINDING,
) -> dict[str, Any]:
    """Compare declared paths without interpreting a refusal as experiment failure.

    Evidence references are locators, not proof of authenticated readback. A
    diagnostic finding is a non-authorizing candidate pending owner validation.
    Input checks run before any comparison; the first failing check is the one
    reported.
    """
    if finding not in _FINDINGS:
        raise _refuse(
            "MPDV_FINDING_UNSUPPORTED",
            "FINDING_IS_IN_THE_DECLARED_DIAGNOSTIC_VOCABULARY",
            "finding must be one of: " + ", ".join(sorted(_FINDINGS)),
        )
    refs_by_label: dict[str, list[str]] = {}
    for label, snapshot in (("original", original), ("diagnostic", diagnostic)):
        if not isinstance(snapshot, Mapping):
            raise _refuse(
                "MPDV_SNAPSHOT_NOT_A_MAPPING",
                "SNAPSHOT_IS_A_MAPPING",
                f"{label} snapshot must be a mapping",
            )
        for key in _REQUIRED:
            if not isinstance(snapshot.get(key), str) or not snapshot[key].strip():
                raise _refuse(
                    "MPDV_SNAPSHOT_FIELD_ABSENT",
                    "SNAPSHOT_CARRIES_MANIFEST_DIGEST_ROUTE_AND_PREDICATE",
                    f"{label}.{key} is required",
                )
        refs_by_label[label] = _evidence_refs(label, snapshot)
    original_disposition = original.get("disposition")
    if original_disposition not in _NON_ALLOW:
        raise _refuse(
            "MPDV_ORIGINAL_NOT_NON_ALLOW",
            "ORIGINAL_DISPOSITION_IS_DENY_OR_FAIL_CLOSED",
            "original.disposition must be DENY or FAIL_CLOSED; an ALLOW or absent disposition has no refusal to diagnose",
        )
    diagnostic_disposition = diagnostic.get("disposition")
    if diagnostic_disposition is not None and diagnostic_disposition not in _DISPOSITIONS:
        raise _refuse(
            "MPDV_DIAGNOSTIC_DISPOSITION_UNDECLARED",
            "DIAGNOSTIC_DISPOSITION_IS_ALLOW_DENY_OR_FAIL_CLOSED_WHEN_PRESENT",
            "diagnostic.disposition, when present, must be ALLOW, DENY or FAIL_CLOSED",
        )
    refs = list(dict.fromkeys(refs_by_label["original"] + refs_by_label["diagnostic"]))
    if not refs and finding != _EVIDENCE_FREE_FINDING:
        raise _refuse(
            "MPDV_FINDING_WITHOUT_EVIDENCE",
            "NON_ABSENCE_FINDING_NAMES_AT_LEAST_ONE_EVIDENCE_LOCATOR",
            f"finding {finding} needs at least one evidence_refs locator; with none, the only reportable finding is {_EVIDENCE_FREE_FINDING}",
        )
    deltas = [
        {"field": key, "original": original.get(key), "diagnostic": diagnostic.get(key)}
        for key in _FIELDS if original.get(key) != diagnostic.get(key)
    ]
    return {
        "schema": SCHEMA,
        # ALLOW here means only that the comparison was computed; it carries no
        # authority over the compared transition.
        "comparison_disposition": "ALLOW",
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "original_disposition": original_disposition,
        "diagnostic_disposition": diagnostic_disposition,
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
