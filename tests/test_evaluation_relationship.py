from __future__ import annotations

import copy
import unittest

from stegverse.demo_terms import accept_demo_terms
from stegverse.evaluation_relationship import resolve_evaluation_relationship, verify_evaluation_relationship


def catalog() -> list[dict]:
    return [
        {"capability_id":"demo.receipts","title":"Receipt verification","tags":["receipt","replay","verification"],"interaction":"deterministic_demo","evaluator_visible":True,"route":"bundle://receipts"},
        {"capability_id":"sandbox.entity","title":"Entity sandbox","tags":["entity","adversarial","sandbox"],"interaction":"sandbox","evaluator_visible":True,"route":"sdk://StegGhost/entity-sandbox-runner"},
        {"capability_id":"llm_adapter.evaluator_interaction","title":"SDK-scoped LLM evaluation interaction","tags":["llm","model","adapter","provider"],"interaction":"sandbox","evaluator_visible":True,"route":"sdk://StegVerse-org/LLM-adapter/evaluator-entry"},
        {"capability_id":"private.hidden","title":"Private hidden capability","tags":["private"],"interaction":"sandbox","evaluator_visible":False,"route":"private://"},
    ]


def accepted_terms() -> dict:
    return accept_demo_terms(participant_id="evaluator:example", signer_name="Example Evaluator", signer_capacity="self", accepted=True, electronic_signature="Example Evaluator", accepted_at="2026-08-12T15:00:00Z")


class EvaluationRelationshipTests(unittest.TestCase):
    def test_terms_receipt_is_required(self) -> None:
        request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-0","objectives":["receipt verification"]}
        with self.assertRaises(PermissionError):
            resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt={})

    def test_evaluator_states_interest_and_sdk_resolves_scope(self) -> None:
        request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-1","objectives":["I want to inspect deterministic receipt verification and replay"],"maximum_interaction":"deterministic_demo"}
        result = resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt=accepted_terms())
        self.assertEqual([x["capability_id"] for x in result["admitted_capabilities"]], ["demo.receipts"])
        self.assertEqual(result["participant_id"], "evaluator:example")
        self.assertTrue(verify_evaluation_relationship(result))

    def test_llm_adapter_is_available_only_as_sdk_scoped_capability(self) -> None:
        request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-2","objectives":["evaluate LLM provider behavior"],"maximum_interaction":"sandbox"}
        result = resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt=accepted_terms())
        admitted = {x["capability_id"]: x for x in result["admitted_capabilities"]}
        self.assertIn("llm_adapter.evaluator_interaction", admitted)
        self.assertEqual(admitted["llm_adapter.evaluator_interaction"]["route"], "sdk://StegVerse-org/LLM-adapter/evaluator-entry")
        self.assertFalse(result["credential_authority_granted"])

    def test_unknown_or_hidden_interest_does_not_expand_scope(self) -> None:
        request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-3","objectives":["quantum aardvark control plane"],"requested_capabilities":["private.hidden","missing.capability"],"maximum_interaction":"sandbox"}
        result = resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt=accepted_terms())
        self.assertEqual(result["admitted_capabilities"], [])
        reasons = {x["capability_id"]: x["reason"] for x in result["denied_or_unavailable"]}
        self.assertEqual(reasons["private.hidden"], "PACKAGE_POLICY_DENIED")
        self.assertEqual(reasons["missing.capability"], "NOT_IN_PACKAGE_CATALOG")

    def test_evaluator_can_narrow_own_scope(self) -> None:
        request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-4","objectives":["entity sandbox and receipt verification"],"exclude_capabilities":["sandbox.entity"],"maximum_interaction":"sandbox"}
        result = resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt=accepted_terms())
        self.assertEqual([x["capability_id"] for x in result["admitted_capabilities"]], ["demo.receipts"])
        self.assertTrue(any(x["capability_id"] == "sandbox.entity" and x["reason"] == "EVALUATOR_EXCLUDED" for x in result["denied_or_unavailable"]))

    def test_receipt_tamper_fails(self) -> None:
        request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-5","objectives":["receipt verification"]}
        result = resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt=accepted_terms())
        tampered = copy.deepcopy(result)
        tampered["repository_access_granted"] = True
        self.assertFalse(verify_evaluation_relationship(tampered))


if __name__ == "__main__":
    unittest.main()
