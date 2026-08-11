from __future__ import annotations

import copy
import unittest

from stegverse.evaluation_relationship import resolve_evaluation_relationship, verify_evaluation_relationship


def catalog() -> list[dict]:
    return [
        {
            "capability_id": "demo.receipts",
            "title": "Receipt verification",
            "tags": ["receipt", "replay", "verification"],
            "interaction": "deterministic_demo",
            "evaluator_visible": True,
            "route": "demo-suite/receipts",
        },
        {
            "capability_id": "sandbox.entity",
            "title": "Entity sandbox",
            "tags": ["entity", "adversarial", "sandbox"],
            "interaction": "sandbox",
            "evaluator_visible": True,
            "route": "StegGhost/entity-sandbox-runner",
        },
        {
            "capability_id": "llm.adapter",
            "title": "LLM adapter",
            "tags": ["llm", "model", "adapter"],
            "interaction": "sandbox",
            "evaluator_visible": False,
            "route": "StegVerse-org/LLM-adapter",
        },
    ]


class EvaluationRelationshipTests(unittest.TestCase):
    def test_evaluator_states_interest_and_sdk_resolves_scope(self) -> None:
        request = {
            "schema": "stegverse.sdk.evaluation-interest-request.v1",
            "request_id": "eval-1",
            "objectives": ["I want to inspect deterministic receipt verification and replay"],
            "maximum_interaction": "deterministic_demo",
        }
        result = resolve_evaluation_relationship(request, catalog())
        self.assertEqual([x["capability_id"] for x in result["admitted_capabilities"]], ["demo.receipts"])
        self.assertEqual(result["unresolved_objectives"], [])
        self.assertTrue(verify_evaluation_relationship(result))

    def test_unknown_interest_does_not_expand_scope(self) -> None:
        request = {
            "schema": "stegverse.sdk.evaluation-interest-request.v1",
            "request_id": "eval-2",
            "objectives": ["quantum aardvark control plane"],
        }
        result = resolve_evaluation_relationship(request, catalog())
        self.assertEqual(result["admitted_capabilities"], [])
        self.assertEqual(result["unresolved_objectives"], request["objectives"])

    def test_explicit_request_still_cannot_override_package_policy(self) -> None:
        request = {
            "schema": "stegverse.sdk.evaluation-interest-request.v1",
            "request_id": "eval-3",
            "objectives": ["model adapter"],
            "requested_capabilities": ["llm.adapter"],
            "maximum_interaction": "sandbox",
        }
        result = resolve_evaluation_relationship(request, catalog())
        self.assertEqual(result["admitted_capabilities"], [])
        self.assertTrue(any(x["capability_id"] == "llm.adapter" and x["reason"] == "PACKAGE_POLICY_DENIED" for x in result["denied_or_unavailable"]))

    def test_evaluator_can_narrow_own_scope(self) -> None:
        request = {
            "schema": "stegverse.sdk.evaluation-interest-request.v1",
            "request_id": "eval-4",
            "objectives": ["entity sandbox and receipt verification"],
            "exclude_capabilities": ["sandbox.entity"],
            "maximum_interaction": "sandbox",
        }
        result = resolve_evaluation_relationship(request, catalog())
        self.assertEqual([x["capability_id"] for x in result["admitted_capabilities"]], ["demo.receipts"])
        self.assertTrue(any(x["capability_id"] == "sandbox.entity" and x["reason"] == "EVALUATOR_EXCLUDED" for x in result["denied_or_unavailable"]))

    def test_receipt_tamper_fails(self) -> None:
        request = {
            "schema": "stegverse.sdk.evaluation-interest-request.v1",
            "request_id": "eval-5",
            "objectives": ["receipt verification"],
        }
        result = resolve_evaluation_relationship(request, catalog())
        tampered = copy.deepcopy(result)
        tampered["repository_access_granted"] = True
        self.assertFalse(verify_evaluation_relationship(tampered))


if __name__ == "__main__":
    unittest.main()
