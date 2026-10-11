"""End-to-end acceptance for SDK-MR-A is a verified governance decision return (StegVerse-SDK#465).

Deterministic, non-authorizing: every document below is a fixture, and the
verifier only says whether the evidence it is given satisfies the predicates.
Missing decision, DENY, FAIL_CLOSED, stale packet, mismatched frame,
replayed return and an authenticated ALLOW.
"""
import copy
import hashlib
import json

from stegverse.governance_return_evidence import (
    ACCEPTANCE_SCHEMA,
    RETURN_READBACK_SCHEMA,
    verify_governance_decision_return,
)
from stegverse.organization_ledger_evidence import OWNING_EXISTING_GOAL, READBACK_SCHEMA

PACKET = "pkt-5efe4b0372bbffa4d2a356fe"
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


def _sha(label):
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


CLOSURE = _sha("closure")
DECIDED = _sha("deciding-organization-decision")


def _readback(*receipts):
    chain, previous = [], None
    for receipt in receipts:
        chain.append({"receipt_sha256": receipt, "previous_receipt_sha256": previous})
        previous = receipt
    return {"schema": READBACK_SCHEMA, "disposition": "ALLOW", "chain": chain, "chain_length": len(chain),
            "head_receipt_sha256": previous, "every_receipt_verifies_against_its_body": True}


def _return(**overrides):
    row = {"governance_request_packet_id": PACKET, "disposition": "ALLOW", "decision_returned": True,
           "closure_transition_class": "ORGANIZATION_EGRESS_CLOSED", "closure_organization_receipt_sha256": CLOSURE,
           "governance_disposition": "ALLOW", "governance_failed_predicate": None,
           "deciding_organization_receipt_sha256": DECIDED,
           "response_packet_id": "governance:abc:response:stegverse-labs"}
    row.update(overrides)
    return row


def _verify(returns=None, *, sender=None, deciding=None, packet=PACKET, document=None):
    if document is None:
        document = {"schema": RETURN_READBACK_SCHEMA, "returns": [_return()] if returns is None else returns}
    return verify_governance_decision_return(
        document,
        sender_readback=_readback(_sha("genesis"), _sha("ingress"), CLOSURE) if sender is None else sender,
        deciding_readback=_readback(_sha("labs-genesis"), DECIDED) if deciding is None else deciding,
        request_packet_id=packet)


def _refused(result, predicate):
    assert result["schema"] == ACCEPTANCE_SCHEMA
    assert result["disposition"] == "FAIL_CLOSED"
    assert result["end_to_end_acceptance"] is False
    for field in SIX_FIELDS:
        assert result[field], field
    assert result["owning_existing_goal"] == OWNING_EXISTING_GOAL
    assert result["failed_predicate"] == predicate
    assert result["master_records_gating"] is False


def test_an_authenticated_allow_decision_satisfies_end_to_end_acceptance():
    result = _verify()
    assert result["disposition"] == "ALLOW"
    assert result["end_to_end_acceptance"] is True
    assert (result["governance_disposition"], result["closure_organization_receipt_sha256"],
            result["deciding_organization_receipt_sha256"]) == ("ALLOW", CLOSURE, DECIDED)
    assert result["authority_effect"] == "NONE_VERIFICATION_ONLY"


def test_an_authenticated_deny_is_a_decision_and_satisfies_acceptance():
    result = _verify([_return(governance_disposition="DENY")])
    assert result["disposition"] == "ALLOW"
    assert result["governance_disposition"] == "DENY"


def test_a_fail_closed_decision_is_a_recorded_refusal_not_a_decision():
    result = _verify([_return(governance_disposition="FAIL_CLOSED",
                              governance_failed_predicate="GOVERNANCE_RUNTIME_STEGCORE_UNAVAILABLE")])
    _refused(result, "GOVERNANCE_DECISION_IS_A_DECISION")
    assert "GOVERNANCE_RUNTIME_STEGCORE_UNAVAILABLE" in result["required_evidence_or_repair"]


def test_a_missing_decision_is_not_completion():
    _refused(_verify([]), "GOVERNANCE_DECISION_RETURNED_FOR_THE_EMITTED_PACKET")
    _refused(_verify(document={"schema": "something-else"}), "GOVERNANCE_RETURN_READBACK_PRESENT")
    _refused(verify_governance_decision_return(None, sender_readback=None, deciding_readback=None,
                                               request_packet_id=PACKET), "GOVERNANCE_RETURN_READBACK_PRESENT")


def test_a_return_for_a_stale_or_other_packet_does_not_answer_this_one():
    result = _verify([_return(governance_request_packet_id="pkt-stale")])
    _refused(result, "GOVERNANCE_DECISION_RETURNED_FOR_THE_EMITTED_PACKET")
    assert "pkt-stale" in result["required_evidence_or_repair"]


def test_a_mismatched_answer_refused_at_closure_is_not_accepted():
    _refused(_verify([_return(closure_transition_class="ORGANIZATION_EGRESS_CLOSURE_REFUSED")]),
             "ANSWER_VERIFIES_AGAINST_THE_EMISSION")
    _refused(_verify([_return(disposition="FAIL_CLOSED", decision_returned=False,
                              failed_predicate="DECIDING_ORGANIZATIONS_ANSWER_VERIFIES_AGAINST_THE_EMISSION")]),
             "GOVERNANCE_RETURN_ADMITTED")


def test_a_replayed_return_with_a_second_closure_is_refused():
    replayed = _return(closure_organization_receipt_sha256=_sha("second-closure"))
    _refused(_verify([_return(), replayed]), "GOVERNANCE_RETURN_RECORDED_ONCE")


def test_a_replay_that_returns_the_recorded_closure_is_still_one_return():
    # Two observations of the same closure are one recorded return, not two.
    result = _verify([_return()])
    assert result["disposition"] == "ALLOW"


def test_the_closure_must_be_read_back_on_the_senders_ledger():
    _refused(_verify(sender=_readback(_sha("genesis"), _sha("ingress"))), "CLOSURE_RECEIPT_IS_IN_THE_SENDER_LEDGER")
    _refused(_verify(sender={"schema": READBACK_SCHEMA, "disposition": "FAIL_CLOSED"}), "SENDER_LEDGER_READBACK_ALLOWED")


def test_the_deciding_organizations_receipt_needs_its_own_independent_readback():
    _refused(_verify(deciding={}), "DECIDING_ORGANIZATION_LEDGER_READBACK_PRESENT")
    _refused(_verify(deciding=_readback(_sha("labs-genesis"))), "DECIDING_ORGANIZATION_RECEIPT_READ_BACK")
    # The sender's record of the answer is not the deciding organization's ledger.
    _refused(_verify(deciding=_readback(_sha("genesis"), _sha("ingress"), CLOSURE)),
             "DECIDING_ORGANIZATION_RECEIPT_READ_BACK")


def test_the_verifier_does_not_mutate_its_evidence():
    document = {"schema": RETURN_READBACK_SCHEMA, "returns": [_return()]}
    before = copy.deepcopy(document)
    _verify(document=document)
    assert json.dumps(document, sort_keys=True) == json.dumps(before, sort_keys=True)


def test_malformed_return_collection_fails_closed_with_six_fields():
    for rows in ("not-an-array", {"governance_request_packet_id": PACKET}, None):
        _refused(_verify(document={"schema": RETURN_READBACK_SCHEMA, "returns": rows}),
                 "GOVERNANCE_RETURN_READBACK_PRESENT")


def test_malformed_receipt_entry_does_not_crash_verification():
    sender = _readback(_sha("genesis"), _sha("ingress"))
    sender["chain"].append({"receipt_sha256": {"unhashable": "object"}})
    _refused(_verify(sender=sender), "SENDER_LEDGER_CHAIN_INTEGRITY")


def test_unhashable_replayed_closure_refuses_instead_of_raising():
    for malformed in ({"receipt": "object"}, ["not", "a", "digest"]):
        result = _verify([_return(), _return(closure_organization_receipt_sha256=malformed)])
        _refused(result, "GOVERNANCE_RETURN_RECORDED_ONCE")


def test_unhashable_single_closure_refuses_with_six_fields():
    result = _verify([_return(closure_organization_receipt_sha256={"invalid": True})])
    _refused(result, "CLOSURE_RECEIPT_IS_IN_THE_SENDER_LEDGER")


def test_sender_readback_chain_metadata_and_links_fail_closed():
    for mutation in ("length", "head", "predecessor", "duplicate"):
        sender = _readback(_sha("genesis"), _sha("ingress"), CLOSURE)
        if mutation == "length":
            sender["chain_length"] += 1
        elif mutation == "head":
            sender["head_receipt_sha256"] = _sha("unrelated")
        elif mutation == "predecessor":
            sender["chain"][2]["previous_receipt_sha256"] = _sha("unrelated")
        else:
            sender["chain"][1]["receipt_sha256"] = sender["chain"][0]["receipt_sha256"]
        _refused(_verify(sender=sender), "SENDER_LEDGER_CHAIN_INTEGRITY")


def test_deciding_organization_readback_chain_integrity_fails_closed():
    deciding = _readback(_sha("labs-genesis"), DECIDED)
    deciding["chain"][1]["previous_receipt_sha256"] = _sha("stale")
    _refused(_verify(deciding=deciding), "DECIDING_ORGANIZATION_LEDGER_CHAIN_INTEGRITY")
