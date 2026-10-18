"""Source-only manifest path differential verification.

This module compares supplied snapshots; it does not authenticate evidence, issue
governance dispositions, run experiments, or authorize remediation.

Owning goal: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001 / COSV 71000000101000.

The finding is supplied by the caller. It is not derived here; it is checked
against what the comparison observed (the diagnostic disposition and whether
any declared path field changed) using the declared table
``FINDING_OBSERVATIONS``. A finding the table does not declare for the
observation is refused.

Every refusal is a six-field non-ALLOW carried on
``ManifestPathDifferentialRefusal.refusal``. Its disposition comes from the
declared ``REFUSAL_DISPOSITIONS`` table, keyed by (failure_code,
failed_predicate). Malformed caller input is DENY; absent state or evidence and
findings the table does not support are FAIL_CLOSED; a pair the table does not
declare is FAIL_CLOSED under MPDV_REFUSAL_DISPOSITION_NOT_DECLARED. The
exception subclasses ``ValueError`` so existing callers that catch
``ValueError`` keep working.

Relation to ``stegverse.negative_conformance`` (same owning goal): that module
classifies a governed-DENY *trial* from sha256-bound receipts (refusal is the
governance disposition, not the experiment outcome). This module compares the
declared *manifest path* of an original non-ALLOW with a diagnostic replay. The
two answer different questions, so neither reimplements the other; the shared
vocabulary is imported rather than restated: the six refusal fields are
``organization_ledger_evidence.REFUSAL_FIELDS`` and the non-ALLOW dispositions
are ``negative_conformance.NON_ALLOW``.
"""
from __future__ import annotations

from typing import Any, Mapping

from .negative_conformance import NON_ALLOW as _NON_ALLOW
from .organization_ledger_evidence import REFUSAL_FIELDS

OWNING_EXISTING_GOAL = "SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001"
RETRY_ENTRYPOINT = "stegverse/manifest_path_differential.py::compare_manifest_paths"
SCHEMA = "stegverse.mpdv-source-comparison.v1"
SIX_FIELDS = REFUSAL_FIELDS

_FIELDS = ("manifest_digest", "route_id", "component_id", "predicate_id", "policy_version", "authority_binding")
_REQUIRED = ("manifest_digest", "route_id", "predicate_id")
_DISPOSITIONS = ("ALLOW", *_NON_ALLOW)
# The only finding that may be reported without evidence on both sides: it is
# the statement that evidence is insufficient. Every other finding is a claim
# about the compared paths and must rest on locators from both snapshots.
_EVIDENCE_FREE_FINDING = "INSUFFICIENT_AUTHENTIC_EVIDENCE"

# Observation = (diagnostic disposition, any declared path field changed).
# Each finding lists the observations it is consistent with:
# - EXPECTED_GOVERNED_DENY: the replay reproduced DENY on an unchanged path.
# - REASONING_REVIEW_REQUIRED: the same path; the evaluator outcome is in question.
# - MANIFEST_BUILDER_DEFECT_CANDIDATE: the built path differs.
# - EXECUTION_PATH_DEFECT_CANDIDATE: the path differs and the replay was not DENY.
# - CAPABILITY_GAP_IDENTIFIED: the replay still fails closed for want of a capability.
# - REQUIREMENTS_AMBIGUOUS: the replay is still non-ALLOW.
# - INSUFFICIENT_AUTHENTIC_EVIDENCE: always reportable, including with no diagnostic disposition.
_ALL_OBSERVATIONS = frozenset(
    (disposition, changed) for disposition in (*_DISPOSITIONS, None) for changed in (False, True)
)
FINDING_OBSERVATIONS: dict[str, frozenset[tuple[str | None, bool]]] = {
    "EXPECTED_GOVERNED_DENY": frozenset({("DENY", False)}),
    "REASONING_REVIEW_REQUIRED": frozenset({("ALLOW", False), ("DENY", False), ("FAIL_CLOSED", False)}),
    "MANIFEST_BUILDER_DEFECT_CANDIDATE": frozenset({("ALLOW", True), ("DENY", True), ("FAIL_CLOSED", True)}),
    "EXECUTION_PATH_DEFECT_CANDIDATE": frozenset({("ALLOW", True), ("FAIL_CLOSED", True)}),
    "CAPABILITY_GAP_IDENTIFIED": frozenset({("FAIL_CLOSED", False), ("FAIL_CLOSED", True)}),
    "REQUIREMENTS_AMBIGUOUS": frozenset({("DENY", False), ("DENY", True), ("FAIL_CLOSED", False), ("FAIL_CLOSED", True)}),
    _EVIDENCE_FREE_FINDING: _ALL_OBSERVATIONS,
}
_FINDINGS = frozenset(FINDING_OBSERVATIONS)

REFUSAL_DISPOSITION_NOT_DECLARED = "MPDV_REFUSAL_DISPOSITION_NOT_DECLARED"
REFUSAL_DISPOSITIONS: dict[tuple[str, str], str] = {
    # Malformed caller input: a governed refusal of the request as made.
    ("MPDV_FINDING_UNSUPPORTED", "FINDING_IS_IN_THE_DECLARED_DIAGNOSTIC_VOCABULARY"): "DENY",
    ("MPDV_SNAPSHOT_NOT_A_MAPPING", "SNAPSHOT_IS_A_MAPPING"): "DENY",
    ("MPDV_EVIDENCE_REFS_MALFORMED", "EVIDENCE_REFS_ARE_A_LIST_OF_NONEMPTY_STRINGS"): "DENY",
    ("MPDV_ORIGINAL_IS_ALLOW", "ORIGINAL_DISPOSITION_IS_DENY_OR_FAIL_CLOSED"): "DENY",
    ("MPDV_DIAGNOSTIC_DISPOSITION_UNDECLARED",
     "DIAGNOSTIC_DISPOSITION_IS_ALLOW_DENY_OR_FAIL_CLOSED_WHEN_PRESENT"): "DENY",
    # Absent state or evidence, or a finding the observation does not support.
    ("MPDV_SNAPSHOT_FIELD_ABSENT", "SNAPSHOT_CARRIES_MANIFEST_DIGEST_ROUTE_AND_PREDICATE"): "FAIL_CLOSED",
    ("MPDV_ORIGINAL_DISPOSITION_ABSENT", "ORIGINAL_DISPOSITION_IS_DENY_OR_FAIL_CLOSED"): "FAIL_CLOSED",
    ("MPDV_FINDING_NOT_DECLARED_FOR_OBSERVED_DIAGNOSTIC",
     "FINDING_IS_DECLARED_FOR_THE_OBSERVED_DIAGNOSTIC_DISPOSITION_AND_PATH"): "FAIL_CLOSED",
}


class ManifestPathDifferentialRefusal(ValueError):
    """A comparison that could not be made; ``refusal`` holds the six-field non-ALLOW."""

    def __init__(self, refusal: dict[str, Any]):
        super().__init__(f"{refusal['failure_code']}: {refusal['required_evidence_or_repair']}")
        self.refusal = refusal


def declared_refusal(fields: Mapping[str, Any]) -> dict[str, Any]:
    """The refusal record for six fields, with the disposition the table declares for their pair.

    An undeclared pair is FAIL_CLOSED under MPDV_REFUSAL_DISPOSITION_NOT_DECLARED;
    the pair it arrived with is kept under ``undeclared_refusal_*``.
    """
    fields = {field: fields[field] for field in SIX_FIELDS}
    disposition = REFUSAL_DISPOSITIONS.get((fields["failure_code"], fields["failed_predicate"]))
    if disposition is None:
        disposition = "FAIL_CLOSED"
        fields = {
            **fields,
            "failure_code": REFUSAL_DISPOSITION_NOT_DECLARED,
            "required_evidence_or_repair": (
                "declare a REFUSAL_DISPOSITIONS row for (" + str(fields["failure_code"]) + ", "
                + str(fields["failed_predicate"]) + "); the refusal it names: "
                + str(fields["required_evidence_or_repair"])),
            "undeclared_refusal_failure_code": fields["failure_code"],
            "undeclared_refusal_failed_predicate": fields["failed_predicate"],
        }
    return {"schema": SCHEMA, "disposition": disposition, **fields, "authority_effect": "NONE_REFUSAL_ONLY"}


def _refuse(failure_code: str, failed_predicate: str, repair: str) -> ManifestPathDifferentialRefusal:
    return ManifestPathDifferentialRefusal(declared_refusal({
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": RETRY_ENTRYPOINT,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": "re-run the comparison with the corrected snapshots; no finding is presumed until then",
    }))


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

    Evidence references are locators, not proof of authenticated readback. The
    caller-supplied finding is a non-authorizing candidate: it must be declared
    for the observed diagnostic disposition and path change, and a substantive
    finding without evidence on both sides is reported as
    INSUFFICIENT_AUTHENTIC_EVIDENCE. Input checks run before state checks; the
    first failing check is the one reported.
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
    if original_disposition == "ALLOW":
        raise _refuse(
            "MPDV_ORIGINAL_IS_ALLOW",
            "ORIGINAL_DISPOSITION_IS_DENY_OR_FAIL_CLOSED",
            "original.disposition is ALLOW; there is no refusal to diagnose",
        )
    if original_disposition not in _NON_ALLOW:
        raise _refuse(
            "MPDV_ORIGINAL_DISPOSITION_ABSENT",
            "ORIGINAL_DISPOSITION_IS_DENY_OR_FAIL_CLOSED",
            "original.disposition must be DENY or FAIL_CLOSED",
        )
    diagnostic_disposition = diagnostic.get("disposition")
    if diagnostic_disposition is not None and diagnostic_disposition not in _DISPOSITIONS:
        raise _refuse(
            "MPDV_DIAGNOSTIC_DISPOSITION_UNDECLARED",
            "DIAGNOSTIC_DISPOSITION_IS_ALLOW_DENY_OR_FAIL_CLOSED_WHEN_PRESENT",
            "diagnostic.disposition, when present, must be ALLOW, DENY or FAIL_CLOSED",
        )
    deltas = [
        {"field": key, "original": original.get(key), "diagnostic": diagnostic.get(key)}
        for key in _FIELDS if original.get(key) != diagnostic.get(key)
    ]
    observation = (diagnostic_disposition, bool(deltas))
    if observation not in FINDING_OBSERVATIONS[finding]:
        raise _refuse(
            "MPDV_FINDING_NOT_DECLARED_FOR_OBSERVED_DIAGNOSTIC",
            "FINDING_IS_DECLARED_FOR_THE_OBSERVED_DIAGNOSTIC_DISPOSITION_AND_PATH",
            f"finding {finding} is not declared for diagnostic disposition {diagnostic_disposition} "
            f"with path_changed={bool(deltas)}; supply a finding FINDING_OBSERVATIONS declares for that observation",
        )
    reported = finding
    downgrade_reason = None
    if finding != _EVIDENCE_FREE_FINDING and not (refs_by_label["original"] and refs_by_label["diagnostic"]):
        reported = _EVIDENCE_FREE_FINDING
        downgrade_reason = "EVIDENCE_REFS_ABSENT_ON_ONE_OR_BOTH_SIDES"
    refs = list(dict.fromkeys(refs_by_label["original"] + refs_by_label["diagnostic"]))
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
        "finding_source": "CALLER_SUPPLIED_CHECKED_AGAINST_DECLARED_OBSERVATIONS",
        "requested_finding": finding,
        "finding_candidate": reported,
        "finding_downgrade_reason": downgrade_reason,
        "evidence_refs": refs,
        "authentic_readback_verified": False,
        "experiment_result_established": False,
        "remediation_authorized": False,
        "mutation_performed": False,
        "authority_effect": "NONE_DIAGNOSTIC_ONLY",
    }
