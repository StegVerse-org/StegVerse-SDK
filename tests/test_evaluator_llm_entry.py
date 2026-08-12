from __future__ import annotations

import copy
import unittest

from stegverse.demo_terms import accept_demo_terms
from stegverse.evaluation_relationship import resolve_evaluation_relationship
from stegverse.evaluator_llm_entry import build_evaluator_llm_request, verify_evaluator_llm_request


def catalog() -> list[dict]:
    return [{"capability_id":"llm_adapter.evaluator_interaction","title":"SDK-scoped LLM evaluation interaction","tags":["llm","model","adapter"],"interaction":"sandbox","evaluator_visible":True,"route":"sdk://StegVerse-org/LLM-adapter/evaluator-entry"}]


def relationship() -> dict:
    terms = accept_demo_terms(participant_id="evaluator:example", signer_name="Example Evaluator", signer_capacity="self", accepted=True, electronic_signature="Example Evaluator", accepted_at="2026-08-12T15:00:00Z")
    request = {"schema":"stegverse.sdk.evaluation-interest-request.v1","request_id":"eval-llm-1","objectives":["evaluate local model behavior"],"maximum_interaction":"sandbox"}
    return resolve_evaluation_relationship(request, catalog(), terms_acceptance_receipt=terms)


class EvaluatorLLMEntryTests(unittest.TestCase):
    def test_build_and_verify_bounded_request(self) -> None:
        rel = relationship()
        request = build_evaluator_llm_request(relationship=rel, request_id="llm-1", prompt="Explain the governance result.", max_output_tokens=128)
        self.assertTrue(verify_evaluator_llm_request(request, rel))
        self.assertEqual(request["evaluation_model_scope"], "local_reference_only")
        self.assertFalse(request["provider_selection_authority"])
        self.assertFalse(request["credential_access_granted"])
        self.assertFalse(request["execution_authority_granted"])
        self.assertFalse(request["repository_access_granted"])

    def test_missing_capability_or_escalation_fails(self) -> None:
        rel = relationship()
        no_capability = copy.deepcopy(rel)
        no_capability["admitted_capabilities"] = []
        with self.assertRaises(PermissionError):
            build_evaluator_llm_request(relationship=no_capability, request_id="llm-2", prompt="x")
        request = build_evaluator_llm_request(relationship=rel, request_id="llm-3", prompt="x")
        escalated = copy.deepcopy(request)
        escalated["credential_access_granted"] = True
        self.assertFalse(verify_evaluator_llm_request(escalated, rel))

    def test_output_limit_fails_closed(self) -> None:
        rel = relationship()
        with self.assertRaises(ValueError):
            build_evaluator_llm_request(relationship=rel, request_id="llm-4", prompt="x", max_output_tokens=513)


if __name__ == "__main__":
    unittest.main()
