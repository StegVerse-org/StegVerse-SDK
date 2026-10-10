"""Verify an organization-ledger readback before a lane claims sovereign completion.

A validation lane is complete only when the organization ledger holds its
transition. The evidence is the readback document produced by
``StegVerse-org/.github resident-runtime/organization_ledger_readback.py`` from a
fresh fetch of ``refs/stegverse/organization-ledger`` (schema
``stegverse.organization-ledger-readback/v1``). This module checks that document;
it does not open, write or vendor a ledger, and it creates no receipt.

Local Master Records custody (``ManifestReceiptCustody`` ``RECORDED``) remains
downstream, non-gating evidence: nothing here reads it and it cannot stand in for
the readback.

Every non-ALLOW carries the six fields of a refusal. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

READBACK_SCHEMA = "stegverse.organization-ledger-readback/v1"
COMPLETION_SCHEMA = "stegverse.sdk.organization-ledger-completion/v1"
OWNING_EXISTING_GOAL = "SDK-MR-A-VALIDATION-CUSTODY-001"
RETRY_ENTRYPOINT = "stegverse/organization_ledger_evidence.py::verify_organization_ledger_readback"
# A lane run with no readback has no organization-ledger transition yet: the
# repair is a manifest-directed transition request on the organization's
# existing ingress (organization-ledger-transition.yml), not anything in the SDK.
TRANSITION_REQUEST_ENTRYPOINT = "StegVerse-org/.github:.stegverse/transition-requests/"
FAILURE_CODE = "SOVEREIGN_COMPLETION_REQUIRES_ORGANIZATION_LEDGER_READBACK"
LOCAL_RUN_STORE_ROLE = {
    "role": "DOWNSTREAM_NON_GATING_EVIDENCE",
    "completes_transition": False,
    "gates_transition": False,
}


class _Refused(Exception):
    def __init__(self, failed_predicate: str, required: str, next_attempt: str,
                 retry_entrypoint: str = RETRY_ENTRYPOINT) -> None:
        super().__init__(failed_predicate)
        self.failed_predicate = failed_predicate
        self.required = required
        self.next_attempt = next_attempt
        self.retry_entrypoint = retry_entrypoint


def _digest(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    if text.startswith("sha256:"):
        text = text[7:]
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        return None
    return "sha256:" + text


def fail_closed(
    failed_predicate: str,
    required_evidence_or_repair: str,
    next_attempt: str,
    retry_entrypoint: str = RETRY_ENTRYPOINT,
) -> dict[str, Any]:
    return {
        "schema": COMPLETION_SCHEMA,
        "disposition": "FAIL_CLOSED",
        "sovereign_completion": False,
        "failure_code": FAILURE_CODE,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": required_evidence_or_repair,
        "retry_entrypoint": retry_entrypoint,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": next_attempt,
        "master_records_gating": False,
        "authority_effect": "NONE_VERIFICATION_ONLY",
    }


_REFETCH = "fetch refs/stegverse/organization-ledger again and rerun organization_ledger_readback.py with --ingress-result"
_SUBMIT = ("commit the lane result as a transition request under StegVerse-org/.github "
           ".stegverse/transition-requests/ and retain the readback of that run "
           "(organization_ledger_readback.py --ingress-result)")


def _check(
    readback: Any,
    organization_receipt_sha256: str | None,
    canonical_manifest_sha256: str | None,
) -> dict[str, Any]:
    if not isinstance(readback, Mapping):
        raise _Refused("ORGANIZATION_LEDGER_READBACK_PRESENT",
                       "an organization-ledger readback document (" + READBACK_SCHEMA + ") for this lane's "
                       "manifest-directed transition request", _SUBMIT, TRANSITION_REQUEST_ENTRYPOINT)
    if readback.get("schema") != READBACK_SCHEMA:
        raise _Refused("ORGANIZATION_LEDGER_READBACK_SCHEMA", "readback schema " + READBACK_SCHEMA, _REFETCH)
    if readback.get("disposition") != "ALLOW":
        raise _Refused("ORGANIZATION_LEDGER_READBACK_ALLOWED",
                       "readback disposition ALLOW; observed " + str(readback.get("disposition")), _REFETCH)
    if readback.get("every_receipt_verifies_against_its_body") is not True:
        raise _Refused("ORGANIZATION_RECEIPT_VERIFIES_AGAINST_ITS_BODY",
                       "every chain receipt self-digest verified by the readback", _REFETCH)
    if readback.get("every_source_receipt_retained_and_verifies") is not True:
        raise _Refused("SOURCE_RECEIPT_RETAINED_AND_VERIFIES",
                       "every consumed source receipt retained under source-receipts/", _REFETCH)

    chain = readback.get("chain")
    if not isinstance(chain, list) or not chain or not all(isinstance(e, Mapping) for e in chain):
        raise _Refused("ORGANIZATION_LEDGER_CHAIN_IS_COMPLETE", "a non-empty receipt chain", _REFETCH)
    if readback.get("chain_length") != len(chain):
        raise _Refused("ORGANIZATION_LEDGER_CHAIN_IS_COMPLETE", "chain_length equal to the listed chain", _REFETCH)
    previous = None
    for entry in chain:
        if entry.get("previous_receipt_sha256") != previous or _digest(entry.get("receipt_sha256")) is None:
            raise _Refused("ORGANIZATION_LEDGER_CHAIN_IS_LINKED",
                           "each receipt names the one before it, from genesis (null)", _REFETCH)
        previous = entry.get("receipt_sha256")
    if readback.get("head_receipt_sha256") != previous:
        raise _Refused("ORGANIZATION_LEDGER_HEAD_IS_CHAIN_TIP", "head_receipt_sha256 equal to the chain tip", _REFETCH)
    if readback.get("genesis_receipt_sha256") != chain[0].get("receipt_sha256"):
        raise _Refused("ORGANIZATION_LEDGER_CHAIN_IS_COMPLETE", "genesis_receipt_sha256 equal to chain[0]", _REFETCH)

    receipt = readback.get("ingress_organization_receipt_sha256")
    if receipt is None or readback.get("ingress_receipt_in_chain") is not True:
        raise _Refused("INGRESS_RECEIPT_IS_IN_THE_ORGANIZATION_LEDGER",
                       "a readback run with --ingress-result for this lane's transition", _SUBMIT,
                       TRANSITION_REQUEST_ENTRYPOINT)
    if readback.get("ingress_refused") is not False:
        raise _Refused("INGRESS_RECEIPT_IS_NOT_A_REFUSAL",
                       "an admitted organization receipt; a recorded refusal is not completion", _SUBMIT,
                       TRANSITION_REQUEST_ENTRYPOINT)
    if organization_receipt_sha256 is not None and receipt != organization_receipt_sha256:
        raise _Refused("INGRESS_RECEIPT_IS_THE_EXPECTED_RECEIPT",
                       "readback of organization receipt " + organization_receipt_sha256, _REFETCH)
    entry = next((e for e in chain if e.get("receipt_sha256") == receipt), None)
    if entry is None:
        raise _Refused("INGRESS_RECEIPT_IS_IN_THE_ORGANIZATION_LEDGER", "receipt " + str(receipt) + " in the chain", _REFETCH)

    manifest = _digest(readback.get("canonical_manifest_sha256"))
    if readback.get("ingress_receipt_bound_to_manifest") is not True or manifest is None:
        raise _Refused("RECEIPT_IS_BOUND_TO_THE_SUBMITTED_MANIFEST",
                       "readback binding the receipt to the canonical manifest digest", _REFETCH)
    if entry.get("predecessor_org_state_sha256") != manifest:
        raise _Refused("RECEIPT_IS_BOUND_TO_THE_SUBMITTED_MANIFEST",
                       "receipt predecessor state equal to sha256:<canonical manifest>", _REFETCH)
    if canonical_manifest_sha256 is not None and manifest != _digest(canonical_manifest_sha256):
        raise _Refused("RECEIPT_IS_BOUND_TO_THE_EXPECTED_MANIFEST",
                       "readback for canonical manifest " + str(canonical_manifest_sha256), _SUBMIT,
                       TRANSITION_REQUEST_ENTRYPOINT)
    if readback.get("master_records_awaited") not in (None, False):
        raise _Refused("MASTER_RECORDS_NOT_AWAITED", "a readback that awaits nothing from Master Records", _REFETCH)

    return {
        "schema": COMPLETION_SCHEMA,
        "disposition": "ALLOW",
        "sovereign_completion": True,
        "organization_receipt_sha256": receipt,
        "canonical_manifest_sha256": manifest,
        "organization_transition_id": readback.get("organization_transition_id"),
        "successor_org_state_sha256": entry.get("successor_org_state_sha256"),
        "head_receipt_sha256": readback.get("head_receipt_sha256"),
        "chain_length": len(chain),
        "location": readback.get("location"),
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "master_records_gating": False,
        "authority_effect": "NONE_VERIFICATION_ONLY",
    }


def verify_organization_ledger_readback(
    readback: Mapping[str, Any] | None,
    *,
    organization_receipt_sha256: str | None = None,
    canonical_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    """ALLOW only for an ALLOW readback whose admitted receipt is in the chain and bound to the manifest."""
    try:
        return _check(readback, organization_receipt_sha256, canonical_manifest_sha256)
    except _Refused as exc:
        return fail_closed(exc.failed_predicate, exc.required, exc.next_attempt, exc.retry_entrypoint)


REFUSAL_FIELDS = (
    "failure_code",
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "next_attempt",
)


def refusal_fields(completion: Mapping[str, Any]) -> dict[str, Any]:
    """The six refusal fields of a non-ALLOW completion, for a lane to carry on its own result."""
    return {key: completion[key] for key in REFUSAL_FIELDS if key in completion}


def load_readback(path: str | Path | None) -> Any:
    """Read a readback document; an absent path or file is None, unreadable JSON is a non-readback."""
    if path is None or not Path(path).is_file():
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except ValueError:
        return {"schema": None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--readback", type=Path, default=None, help="organization-ledger readback JSON")
    parser.add_argument("--organization-receipt-sha256", default=None)
    parser.add_argument("--canonical-manifest-sha256", default=None)
    args = parser.parse_args(argv)
    readback = load_readback(args.readback)
    result = verify_organization_ledger_readback(
        readback,
        organization_receipt_sha256=args.organization_receipt_sha256,
        canonical_manifest_sha256=args.canonical_manifest_sha256,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["disposition"] == "ALLOW" else 1


__all__ = [
    "READBACK_SCHEMA",
    "COMPLETION_SCHEMA",
    "OWNING_EXISTING_GOAL",
    "TRANSITION_REQUEST_ENTRYPOINT",
    "LOCAL_RUN_STORE_ROLE",
    "REFUSAL_FIELDS",
    "fail_closed",
    "load_readback",
    "refusal_fields",
    "verify_organization_ledger_readback",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
