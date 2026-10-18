"""Governed-DENY negative-conformance classification (read-only, non-authorizing).

A deliberate governed-DENY trial passes when the governance boundary refuses
correctly: a recorded DENY or FAIL_CLOSED is the governance *disposition*, not
the *outcome* of the experiment that produced it. This module keeps the two
apart. It checks a supplied fixture against the Task Registry invariants the
SDK already carries (every non-ALLOW carries the six refusal fields of
``organization_ledger_evidence.REFUSAL_FIELDS``; nothing awaits an external
machine; destination liveness is not a transition predicate; an unobserved
effect stays ``NOT_AUTHENTICALLY_OBSERVED`` with a reconciliation entrypoint)
and returns a classification plus an ``ecosystem_diagnostic`` processor request
for the installed diagnostic route.

Owner: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001 / COSV 71000000101000. It
classifies supplied data only: it fetches nothing, verifies no receipt's
authenticity, executes nothing and grants no authority.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from .ecosystem_diagnostic_runtime import REQUEST_SCHEMA as DIAGNOSTIC_REQUEST_SCHEMA
from .organization_ledger_evidence import REFUSAL_FIELDS

FIXTURE_SCHEMA = "stegverse.sdk.governed-deny-negative-conformance-fixture/v1"
RESULT_SCHEMA = "stegverse.sdk.governed-deny-negative-conformance-classification/v1"
NON_ALLOW = ("DENY", "FAIL_CLOSED")
EXPERIMENT_OUTCOMES = ("NOT_FAILED", "FAILED", "INCONCLUSIVE")
PASS = "NEGATIVE_CONFORMANCE_PASS_CORRECT_REFUSAL"
FAILED_INDEPENDENTLY = "EXPERIMENT_FAILED_INDEPENDENT_OF_REFUSAL"
UNOBSERVED = "NOT_AUTHENTICALLY_OBSERVED"
#: A failure basis that is only the governance refusal itself.
REFUSAL_ONLY_BASES = frozenset({"GOVERNANCE_DENY", "GOVERNANCE_FAIL_CLOSED", "GOVERNANCE_DISPOSITION"})
RETURN_ENTRYPOINT = "stegverse.manifest_state_transition_runtime.admit_runtime_result"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != {} and value != []


def receipt_ref(receipt: Mapping[str, Any]) -> str:
    """``repository@commit:path#sha256=<hex>`` - the byte-bound reference form."""
    return f"{receipt['repository']}@{receipt['commit']}:{receipt['path']}#sha256={receipt['sha256']}"


def _check_receipts(receipts: Any) -> list[dict[str, Any]]:
    if not isinstance(receipts, list) or not receipts:
        raise ValueError("BOUND_RECEIPTS_REQUIRED")
    seen: set[str] = set()
    for row in receipts:
        if not isinstance(row, Mapping):
            raise ValueError("BOUND_RECEIPT_MUST_BE_OBJECT")
        rid = row.get("receipt_id")
        if not isinstance(rid, str) or not rid or rid in seen:
            raise ValueError("BOUND_RECEIPT_ID_REQUIRED_AND_UNIQUE")
        seen.add(rid)
        for key in ("repository", "path"):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError(f"BOUND_RECEIPT_FIELD_REQUIRED:{rid}:{key}")
        if not _HEX40.match(str(row.get("commit"))):
            raise ValueError(f"BOUND_RECEIPT_COMMIT_INVALID:{rid}")
        if not _HEX64.match(str(row.get("sha256"))):
            raise ValueError(f"BOUND_RECEIPT_SHA256_INVALID:{rid}")
    return [dict(r) for r in receipts]


def classify_governed_deny_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a governed-DENY trial; raise ``ValueError`` on a nonconforming fixture."""
    if not isinstance(fixture, Mapping) or fixture.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("NEGATIVE_CONFORMANCE_FIXTURE_SCHEMA_MISMATCH")
    receipts = _check_receipts(fixture.get("bound_receipts"))
    receipt_ids = {r["receipt_id"] for r in receipts}

    invariants = fixture.get("registry_invariants") or {}
    for key in ("external_machine_awaiting_allowed", "destination_liveness_is_transition_predicate"):
        if invariants.get(key) is not False:
            raise ValueError(f"REGISTRY_INVARIANT_VIOLATED:{key}")

    handoff = (fixture.get("sdk_handoff") or {}).get("expected") or {}
    if handoff.get("awaits_external_machine") is not False:
        raise ValueError("SDK_HANDOFF_AWAITS_EXTERNAL_MACHINE")
    if handoff.get("return_entrypoint") != RETURN_ENTRYPOINT:
        raise ValueError("SDK_HANDOFF_RETURN_ENTRYPOINT_MISMATCH")

    disposition = fixture.get("governance_disposition")
    if disposition not in NON_ALLOW:
        raise ValueError("GOVERNANCE_DISPOSITION_MUST_BE_DENY_OR_FAIL_CLOSED")
    entries = fixture.get("non_allow_entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("NON_ALLOW_ENTRIES_REQUIRED")
    current = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("NON_ALLOW_ENTRY_MUST_BE_OBJECT")
        eid = entry.get("entry_id") or "?"
        if entry.get("disposition") not in NON_ALLOW:
            raise ValueError(f"NON_ALLOW_ENTRY_DISPOSITION_INVALID:{eid}")
        for field in REFUSAL_FIELDS:
            if not _present(entry.get(field)):
                raise ValueError(f"NON_ALLOW_SIX_FIELD_ENTRY_MISSING:{eid}:{field}")
        nxt = entry["next_attempt"]
        if isinstance(nxt, Mapping) and nxt.get("awaits_an_external_machine") is not False:
            raise ValueError(f"NON_ALLOW_NEXT_ATTEMPT_AWAITS_EXTERNAL_MACHINE:{eid}")
        refs = entry.get("source_receipt_ids") or []
        if not refs or not set(refs) <= receipt_ids:
            raise ValueError(f"NON_ALLOW_ENTRY_NOT_BOUND_TO_A_RECEIPT:{eid}")
        if entry.get("status") == "CURRENT":
            current.append(entry)
    if not any(e["disposition"] == disposition for e in current):
        raise ValueError("GOVERNANCE_DISPOSITION_HAS_NO_CURRENT_SIX_FIELD_ENTRY")

    for effect in fixture.get("unobserved_effects") or []:
        if effect.get("consequence_observation") != UNOBSERVED:
            raise ValueError(f"UNOBSERVED_EFFECT_MISCLASSIFIED:{effect.get('effect')}")
        if not _present(effect.get("reconciliation_entrypoint")):
            raise ValueError(f"UNOBSERVED_EFFECT_RECONCILIATION_ENTRYPOINT_REQUIRED:{effect.get('effect')}")

    outcome = fixture.get("experiment_outcome")
    if outcome not in EXPERIMENT_OUTCOMES:
        raise ValueError("EXPERIMENT_OUTCOME_INVALID")
    classification = PASS
    if outcome == "FAILED":
        bases = [b for b in fixture.get("experiment_failure_bases") or [] if isinstance(b, Mapping)]
        independent = [b for b in bases if b.get("basis") not in REFUSAL_ONLY_BASES
                       and set(b.get("source_receipt_ids") or []) and set(b["source_receipt_ids"]) <= receipt_ids]
        if not independent:
            # A correct DENY/FAIL_CLOSED is the trial working; it is not an experiment failure.
            raise ValueError("EXPERIMENT_FAILED_INFERRED_FROM_GOVERNANCE_REFUSAL")
        classification = FAILED_INDEPENDENTLY
    if fixture.get("expected_classification") not in (None, classification):
        raise ValueError("EXPECTED_CLASSIFICATION_MISMATCH")

    return {
        "schema": RESULT_SCHEMA,
        "fixture_id": fixture.get("fixture_id"),
        "classification": classification,
        "governance_disposition": disposition,
        "experiment_outcome": outcome,
        "refusal_counted_as_experiment_failure": False,
        "current_non_allow_entry_ids": [e["entry_id"] for e in current],
        "bound_receipt_refs": [receipt_ref(r) for r in receipts],
        "awaits_external_machine": False,
        "return_entrypoint": RETURN_ENTRYPOINT,
        "authority_effect": "NONE_DIAGNOSTIC_ONLY",
    }


def diagnostic_request(fixture: Mapping[str, Any], classification: Mapping[str, Any]) -> dict[str, Any]:
    """An ``ecosystem_diagnostic`` request for the installed processor.

    Classified predicates carry receipt references; effects nobody authentically
    observed carry no observation, so the processor reports them NOT_OBSERVED.
    """
    refs = {r["receipt_id"]: receipt_ref(r) for r in fixture["bound_receipts"]}
    owner = fixture.get("owning_existing_goal", "SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001")

    def observed(test_id: str, predicate: str, ids: list[str]) -> dict[str, Any]:
        return {"test_id": test_id, "component_id": "sdk-mesh-destination-map", "predicate_id": predicate,
                "authority_owner": owner,
                "observation": {"state": "PASS", "evidence_refs": [refs[i] for i in ids]}}

    entry_receipts = sorted({i for e in fixture["non_allow_entries"] for i in e["source_receipt_ids"]})
    tests = [
        observed("governed_refusal_carries_six_fields", "NON_ALLOW_CARRIES_SIX_REFUSAL_FIELDS", entry_receipts),
        observed("refusal_is_not_experiment_failure", "GOVERNANCE_DISPOSITION_DISTINCT_FROM_EXPERIMENT_OUTCOME",
                 entry_receipts),
        observed("sdk_handoff_awaits_no_external_machine", "EXTERNAL_MACHINE_AWAITING_NOT_ALLOWED",
                 list(fixture["sdk_handoff"]["source_receipt_ids"])),
    ]
    for effect in fixture.get("unobserved_effects") or []:
        tests.append({"test_id": "unobserved:" + effect["effect"], "component_id": "organization-ledger",
                      "predicate_id": effect["effect"], "authority_owner": effect["reconciliation_entrypoint"],
                      "observation": None})
    return {
        "schema": DIAGNOSTIC_REQUEST_SCHEMA,
        "diagnostic_request_id": f"{classification['fixture_id']}:{classification['classification']}",
        "scope": "ecosystem",
        "mutation_permitted": False,
        "expected_evidence_fields": ["repository", "commit", "path", "sha256"],
        "tests": tests,
    }


__all__ = ["FIXTURE_SCHEMA", "PASS", "RESULT_SCHEMA", "classify_governed_deny_fixture",
           "diagnostic_request", "receipt_ref"]
