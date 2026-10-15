"""Verify a governance decision return before SDK-MR-A claims end-to-end completion.

SDK-MR-A's sender transition is complete when the organization ledger holds it
(``organization_ledger_evidence``). Its end-to-end lifecycle is complete only
when the deciding organization's decision has come back and been verified:

- the return readback (``StegVerse-org/.github .github/workflows/
  organization-governance-return.yml``, schema
  ``stegverse.organization-governance-return-readback/v1``) names exactly one
  return for the emitted request packet, recorded once;
- that return was admitted (ALLOW, decision returned), closed the crossing
  (``ORGANIZATION_EGRESS_CLOSED``, not a refused closure), and its closure
  receipt is in the sender's organization-ledger readback chain;
- the decision is a decision: ALLOW or DENY from the decision authority. A
  FAIL_CLOSED decision is a recorded refusal, not a governance outcome;
- the deciding organization's own receipt for the decision is in an
  independent readback of the deciding organization's ledger. The sender's
  record of what the deciding organization said is not that evidence.

This checks documents. It opens no ledger, admits nothing, and no fixture can
set production completion: every input is the caller's evidence, and an ALLOW
here only says that evidence satisfies the predicates. Every non-ALLOW
carries the six fields of a refusal. Stdlib only.
"""
from __future__ import annotations

from typing import Any, Mapping

from .organization_ledger_evidence import OWNING_EXISTING_GOAL, READBACK_SCHEMA, _digest

RETURN_READBACK_SCHEMA = "stegverse.organization-governance-return-readback/v1"
ACCEPTANCE_SCHEMA = "stegverse.sdk.governance-return-acceptance/v1"
FAILURE_CODE = "END_TO_END_REQUIRES_A_VERIFIED_GOVERNANCE_DECISION_RETURN"
RETRY_ENTRYPOINT = "stegverse/governance_return_evidence.py::verify_governance_decision_return"
RETURN_ENTRYPOINT = ("StegVerse-org/.github:.github/workflows/organization-governance-return.yml "
                     "(push: .stegverse/governance-return-requests/*.json)")
CLOSED = "ORGANIZATION_EGRESS_CLOSED"
DECISIONS = ("ALLOW", "DENY")


class _Refused(Exception):
    def __init__(self, failed_predicate: str, required: str, next_attempt: str,
                 retry_entrypoint: str = RETRY_ENTRYPOINT) -> None:
        super().__init__(failed_predicate)
        self.failed_predicate = failed_predicate
        self.required = required
        self.next_attempt = next_attempt
        self.retry_entrypoint = retry_entrypoint


def _fail_closed(exc: _Refused) -> dict[str, Any]:
    return {
        "schema": ACCEPTANCE_SCHEMA,
        "disposition": "FAIL_CLOSED",
        "end_to_end_acceptance": False,
        "failure_code": FAILURE_CODE,
        "failed_predicate": exc.failed_predicate,
        "required_evidence_or_repair": exc.required,
        "retry_entrypoint": exc.retry_entrypoint,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": exc.next_attempt,
        "master_records_gating": False,
        "authority_effect": "NONE_VERIFICATION_ONLY",
    }


_RETURN = ("commit a governance return request declaring the deciding organization's published mesh "
           "and retain the run's readback")
_REFETCH = "fetch the ledger again and rerun organization_ledger_readback.py on a fresh fetch"


def _chain(readback: Any, what: str) -> set[str]:
    if not isinstance(readback, Mapping) or readback.get("schema") != READBACK_SCHEMA:
        raise _Refused(what + "_LEDGER_READBACK_PRESENT", "an organization-ledger readback (" + READBACK_SCHEMA + ") of the "
                       + what.lower().replace("_", " ") + " ledger from a fresh fetch", _REFETCH)
    if readback.get("disposition") != "ALLOW" or readback.get("every_receipt_verifies_against_its_body") is not True:
        raise _Refused(what + "_LEDGER_READBACK_ALLOWED", "readback disposition ALLOW with every receipt verified", _REFETCH)
    chain = readback.get("chain")
    if not isinstance(chain, list) or not chain:
        raise _Refused(what + "_LEDGER_READBACK_ALLOWED", "a non-empty verified chain", _REFETCH)
    if readback.get("chain_length") != len(chain):
        raise _Refused(what + "_LEDGER_CHAIN_INTEGRITY", "matching chain_length", _REFETCH)
    previous = None
    receipts = set()
    for entry in chain:
        if not isinstance(entry, Mapping):
            raise _Refused(what + "_LEDGER_CHAIN_INTEGRITY", "object chain entries", _REFETCH)
        receipt = _digest(entry.get("receipt_sha256"))
        if receipt is None or entry.get("previous_receipt_sha256") != previous or receipt in receipts:
            raise _Refused(what + "_LEDGER_CHAIN_INTEGRITY",
                           "unique valid receipts and contiguous predecessor bindings", _REFETCH)
        receipts.add(receipt)
        previous = receipt
    if readback.get("head_receipt_sha256") != previous:
        raise _Refused(what + "_LEDGER_CHAIN_INTEGRITY", "head equals final receipt", _REFETCH)
    return receipts


def _check(return_readback: Any, sender_readback: Any, deciding_readback: Any, request_packet_id: str) -> dict[str, Any]:
    if not isinstance(request_packet_id, str) or not request_packet_id.strip():
        raise _Refused("GOVERNANCE_REQUEST_PACKET_ID_REQUIRED",
                       "a non-empty manifest-bound governance request packet ID",
                       "bind the actual emitted governance request packet before verifying its return")
    if not isinstance(return_readback, Mapping) or return_readback.get("schema") != RETURN_READBACK_SCHEMA:
        raise _Refused("GOVERNANCE_RETURN_READBACK_PRESENT", "a return readback (" + RETURN_READBACK_SCHEMA + ")",
                       _RETURN, RETURN_ENTRYPOINT)
    rows = return_readback.get("returns")
    if not isinstance(rows, list):
        raise _Refused("GOVERNANCE_RETURN_READBACK_PRESENT",
                       "a returns array in the authenticated return readback", _RETURN, RETURN_ENTRYPOINT)
    returns = [r for r in rows
               if isinstance(r, Mapping) and r.get("governance_request_packet_id") == request_packet_id]
    if not returns:
        others = sorted({str(r.get("governance_request_packet_id")) for r in rows
                         if isinstance(r, Mapping)})
        raise _Refused("GOVERNANCE_DECISION_RETURNED_FOR_THE_EMITTED_PACKET",
                       "a return for packet " + request_packet_id + ("; returns seen for " + ", ".join(others) if others
                                                                       else "; none returned yet (no answer is not a decision)"),
                       _RETURN, RETURN_ENTRYPOINT)
    # Do not hash untrusted receipt values: malformed lists or objects must
    # produce the six-field refusal rather than escaping as TypeError.
    closures = [r.get("closure_organization_receipt_sha256") for r in returns]
    if len(returns) != 1 or any(value != closures[0] for value in closures):
        raise _Refused("GOVERNANCE_RETURN_RECORDED_ONCE",
                       "exactly one closure for the packet; " + str(len(returns)) + " return records were observed",
                       "repair the replayed closure on the return path; a replay must return the closure already recorded")
    returned = returns[0]
    if returned.get("disposition") != "ALLOW" or returned.get("decision_returned") is not True:
        raise _Refused("GOVERNANCE_RETURN_ADMITTED",
                       "a return admitted by the SDK with decision_returned true; observed "
                       + str(returned.get("disposition")) + " " + str(returned.get("failed_predicate")),
                       _RETURN, RETURN_ENTRYPOINT)
    if returned.get("closure_transition_class") != CLOSED:
        raise _Refused("ANSWER_VERIFIES_AGAINST_THE_EMISSION",
                       "closure class " + CLOSED + "; observed " + str(returned.get("closure_transition_class")),
                       "the deciding organization must answer the emitted frame itself; a mismatched answer is refused at closure",
                       RETURN_ENTRYPOINT)
    closure = _digest(returned.get("closure_organization_receipt_sha256"))
    if closure is None or closure not in _chain(sender_readback, "SENDER"):
        raise _Refused("CLOSURE_RECEIPT_IS_IN_THE_SENDER_LEDGER",
                       "closure receipt " + str(closure) + " in the sender's organization-ledger readback", _REFETCH)
    decision = returned.get("governance_disposition")
    if decision not in DECISIONS:
        raise _Refused("GOVERNANCE_DECISION_IS_A_DECISION",
                       "an ALLOW or DENY from the decision authority; observed " + str(decision)
                       + " (" + str(returned.get("governance_failed_predicate")) + ")",
                       "remove the cause the deciding organization recorded and have it decide the same request again",
                       RETURN_ENTRYPOINT)
    deciding = _digest(returned.get("deciding_organization_receipt_sha256"))
    if deciding is None or deciding not in _chain(deciding_readback, "DECIDING_ORGANIZATION"):
        raise _Refused("DECIDING_ORGANIZATION_RECEIPT_READ_BACK",
                       "the deciding organization's receipt " + str(deciding)
                       + " in an independent fresh-fetch readback of the deciding organization's own ledger",
                       "publish the deciding organization's ledger on its designated custody surface and read it back")
    return {
        "schema": ACCEPTANCE_SCHEMA,
        "disposition": "ALLOW",
        "end_to_end_acceptance": True,
        "governance_request_packet_id": request_packet_id,
        "governance_disposition": decision,
        "closure_organization_receipt_sha256": closure,
        "deciding_organization_receipt_sha256": deciding,
        "response_packet_id": returned.get("response_packet_id"),
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "master_records_gating": False,
        "authority_effect": "NONE_VERIFICATION_ONLY",
    }


def verify_governance_decision_return(
    return_readback: Mapping[str, Any] | None,
    *,
    sender_readback: Mapping[str, Any] | None,
    deciding_readback: Mapping[str, Any] | None,
    request_packet_id: str,
) -> dict[str, Any]:
    """ALLOW only when every end-to-end predicate holds on the evidence given; otherwise six fields."""
    try:
        return _check(return_readback, sender_readback, deciding_readback, request_packet_id)
    except _Refused as exc:
        return _fail_closed(exc)


__all__ = [
    "ACCEPTANCE_SCHEMA",
    "RETURN_READBACK_SCHEMA",
    "verify_governance_decision_return",
]
