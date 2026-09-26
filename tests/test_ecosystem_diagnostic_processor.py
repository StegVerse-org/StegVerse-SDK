from __future__ import annotations

import unittest
from unittest.mock import patch

from stegverse.ecosystem_diagnostic_runtime import execute_manifest
from stegverse.manifest_execution import execute_manifest as sdk_run_manifest
from stegverse.manifest_state_transition_runtime import INGRESS_URL_ENV
from stegverse.manifest_builder import DIAGNOSTIC_RETURN_DEPTHS, available_processors, build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.route_resolution import ECOSYSTEM_DIAGNOSTIC_ROUTE_ID, PUBLISHED_ROUTES, route_from_manifest


def diagnostic_request(*, observation=None, expected=None):
    return {
        "schema": "stegverse.ecosystem-diagnostic-request.v1",
        "diagnostic_request_id": "diag-test-001",
        "scope": "ecosystem",
        "mutation_permitted": False,
        "expected_evidence_fields": list(expected or []),
        "tests": [
            {
                "test_id": "runtime-residency",
                "component_id": "resident-runtime",
                "predicate_id": "authorized_resident_observed",
                "authority_owner": "StegVerse resident runtime",
                "observation": observation,
            }
        ],
    }


class EcosystemDiagnosticProcessorTests(unittest.TestCase):
    def test_processor_is_installed_separately_from_governance(self):
        self.assertEqual(available_processors(), ("atomic_task_worker", "ecosystem_diagnostic", "governance", "purpose_bound_worker"))
        route = PUBLISHED_ROUTES[ECOSYSTEM_DIAGNOSTIC_ROUTE_ID]
        self.assertEqual(route["processor_capability"], "ecosystem_diagnostic")
        self.assertTrue(route["runtime_installed"])
        self.assertFalse(route["external_consequence_enabled"])
        self.assertEqual(route["containment"], "READ_ONLY_DIAGNOSTIC")

    def test_builder_does_not_require_governance_candidate(self):
        manifest = build_manifest(
            data={"source": "resident-observation-bundle"},
            source_framework="StegVerse-Healer",
            source_output_id="ece-cycle-1",
            processor_request=diagnostic_request(),
            process="ecosystem_diagnostic",
            created_at="2026-09-12T03:30:00Z",
        )
        self.assertNotIn("candidate", manifest)
        self.assertNotIn("candidate_sha256", manifest["hashes"])
        self.assertNotIn("stegverse_governance_request", manifest["extensions"])
        self.assertEqual(manifest["processing"]["capability"], "ecosystem_diagnostic")
        self.assertEqual(manifest["processing"]["route_id"], ECOSYSTEM_DIAGNOSTIC_ROUTE_ID)
        canonical = validate_ingress_manifest(manifest)
        resolved = route_from_manifest(canonical)
        self.assertFalse(resolved["route_selection_grants_authority"])

    def test_missing_observation_remains_not_observed(self):
        manifest = build_manifest(
            data={"source": "none"},
            source_framework="fixture",
            source_output_id="missing-observation",
            processor_request=diagnostic_request(observation=None),
            process="ecosystem_diagnostic",
            created_at="2026-09-12T03:30:00Z",
        )
        result = execute_manifest(manifest)
        self.assertEqual(result["results"][0]["observation_state"], "NOT_OBSERVED")
        self.assertFalse(result["mutation_performed"])
        self.assertEqual(result["authority_effect"], "NONE_DIAGNOSTIC_ONLY")
        self.assertFalse(result["continuity_state_present"])
        self.assertNotIn("continuity_state", result)
        self.assertIn("product_processing", result)
        self.assertIn("admittedcode_processing", result)
        products = {row["product_id"]: row for row in result["product_processing"]["contributions"]}
        self.assertEqual("PROCESSED", products["Ecosystem Diagnostic"]["processing_status"])
        self.assertEqual("NOT_PROCESSED", products["AdmittedCode"]["processing_status"])
        self.assertEqual("ROUTE_DID_NOT_TRAVERSE_ADMITTEDCODE", products["AdmittedCode"]["provenance_basis"])
        self.assertEqual("NOT_OBSERVED", products["Interlock/InTr"]["processing_status"])
        self.assertEqual("NOT_OBSERVED", products["StegAgents/runtime"]["processing_status"])
        self.assertEqual("NOT_OBSERVED", products["Master Records"]["processing_status"])
        self.assertEqual("NONE", result["product_processing"]["composition_authority_effect"])
        self.assertIn("result_binding_hash", result)
        self.assertIn("sdk_return_binding_hash", result)

    def test_preregistered_evidence_without_reference_fails_closed(self):
        manifest = build_manifest(
            data={"source": "claimed-observation"},
            source_framework="fixture",
            source_output_id="unbacked-pass",
            processor_request=diagnostic_request(
                expected=["resident_receipt"],
                observation={
                    "state": "PASS",
                    "observed_at": "2026-09-12T03:30:00Z",
                    "evidence_refs": [],
                    "evidence_age_seconds": 0,
                    "detail": "claimed without retained receipt",
                },
            ),
            process="ecosystem_diagnostic",
            created_at="2026-09-12T03:30:00Z",
        )
        result = execute_manifest(manifest)
        self.assertEqual(result["results"][0]["observation_state"], "PROBE_REQUIRED")
        self.assertEqual(result["results"][0]["evidence_refs"], [])

    def test_backed_observation_is_preserved_not_reinterpreted(self):
        observation = {
            "state": "DEGRADED",
            "observed_at": "2026-09-12T03:29:00Z",
            "evidence_refs": ["mr:receipt:abc"],
            "evidence_age_seconds": 60,
            "detail": "resident present; one dependency stale",
        }
        manifest = build_manifest(
            data={"source": "resident"},
            source_framework="fixture",
            source_output_id="backed-degraded",
            processor_request=diagnostic_request(expected=["resident_receipt"], observation=observation),
            process="ecosystem_diagnostic",
            return_depth="result+evidence",
            created_at="2026-09-12T03:30:00Z",
        )
        self.assertEqual(manifest["return_projection"], DIAGNOSTIC_RETURN_DEPTHS["result+evidence"])
        result = execute_manifest(manifest)
        row = result["results"][0]
        self.assertEqual(row["observation_state"], "DEGRADED")
        self.assertEqual(row["evidence_refs"], ["mr:receipt:abc"])
        self.assertEqual(row["authority_owner"], "StegVerse resident runtime")
        self.assertFalse(row["mutation_performed"])

    def test_diagnostic_request_cannot_enable_mutation(self):
        request = diagnostic_request()
        request["mutation_permitted"] = True
        with self.assertRaisesRegex(ValueError, "mutation_permitted=false"):
            build_manifest(
                data={"source": "fixture"},
                source_framework="fixture",
                source_output_id="mutation-forbidden",
                processor_request=request,
                process="ecosystem_diagnostic",
            )



class HeldOutManifestedReadinessSourceOnly(unittest.TestCase):
    """Four actual SDK-built diagnostic manifests; NOT the adaptive-routing trials.

    These inputs preserve the four independent research task descriptions but
    deliberately exclude all evaluator-only oracle fields. The installed SDK
    diagnostic is read-only and cannot substitute for an approved adaptive
    processing route, InTr execution or authenticated Master Records readback.
    """

    _ROUTER_INPUTS = (
        {
            "task_id": "SV-HOLDOUT-001",
            "manifest_intent": "recover committed successor state",
            "available_evidence": [
                "predecessor_hash", "complete_ordered_events", "exact_policy_version",
            ],
            "new_facts_required": False,
        },
        {
            "task_id": "SV-HOLDOUT-002",
            "manifest_intent": (
                "evaluate a previously unobserved source document and form "
                "a new evidence-grounded result"
            ),
            "available_evidence": ["unprocessed_external_document_commitment"],
            "new_facts_required": True,
        },
        {
            "task_id": "SV-HOLDOUT-003",
            "manifest_intent": "reconstruct a committed state",
            "available_evidence": ["event_log_without_required_predecessor_receipt"],
            "new_facts_required": False,
        },
        {
            "task_id": "SV-HOLDOUT-004",
            "manifest_intent": (
                "reconstruct known prefix and evaluate new evidence "
                "for unresolved suffix"
            ),
            "available_evidence": [
                "complete_known_prefix_with_predecessor",
                "unprocessed_suffix_commitment",
            ],
            "new_facts_required": True,
        },
    )

    def test_four_real_sdk_manifests_diagnose_missing_live_routing_evidence(self):
        # The four SOURCE research oracles live only in the external evaluator,
        # and cannot enter these SDK manifest payloads or processor requests.
        digests = set()
        for router_input in self._ROUTER_INPUTS:
            with self.subTest(task=router_input["task_id"]):
                manifest = build_manifest(
                    data=router_input,
                    source_framework="GCAT-BCAT-Engine/workflows",
                    source_output_id=router_input["task_id"] + ":readiness-diagnostic",
                    data_class="source_native_held_out_readiness_input",
                    processor_request={
                        "schema": "stegverse.ecosystem-diagnostic-request.v1",
                        "diagnostic_request_id": router_input["task_id"] + ":readiness",
                        "scope": "runtime",
                        "mutation_permitted": False,
                        "expected_evidence_fields": [
                            "installed_adaptive_processor",
                            "authenticated_original_route_receipt",
                            "matching_master_records_reconstruction",
                        ],
                        "tests": [
                            {
                                "test_id": "authentic-adaptive-route-readiness",
                                "component_id": "StegVerse-SDK",
                                "predicate_id": "manifested_adaptive_route_is_operational",
                                "authority_owner": "StegVerse-org/StegVerse-SDK",
                                "observation": None,
                            }
                        ],
                    },
                    process="ecosystem_diagnostic",
                    return_depth="full-trace",
                    publisher_required=False,
                    created_at="2026-09-25T21:00:00Z",
                )
                canonical = validate_ingress_manifest(manifest)
                self.assertEqual(canonical["payload"], router_input)
                self.assertNotIn("oracle", canonical["payload"])
                self.assertEqual(canonical["processing"]["capability"], "ecosystem_diagnostic")
                self.assertFalse(canonical["external_manifest_grants_authority"])
                self.assertTrue(canonical["complete_communication_manifest"])
                self.assertEqual(
                    canonical["processing"]["route_id"],
                    canonical["extensions"]["stegverse_route"]["route_id"],
                )
                digests.add(canonical["canonical_manifest_sha256"])
                # The local diagnostic helper processes the validated manifest
                # without authority. The public run-manifest deliberately routes
                # through existing Universal InTr; never mock a success there.
                result = execute_manifest(manifest)
                self.assertEqual(result["results"][0]["observation_state"], "NOT_OBSERVED")
                with patch.dict("os.environ", {INGRESS_URL_ENV: ""}):
                    with self.assertRaisesRegex(
                        ValueError, "UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED"
                    ):
                        sdk_run_manifest(manifest)
                self.assertFalse(result["mutation_performed"])
                self.assertEqual(result["authority_effect"], "NONE_DIAGNOSTIC_ONLY")
                self.assertFalse(result["continuity_state_present"])
        self.assertEqual(len(digests), 4)

    def test_adaptive_capability_not_installed_cannot_be_faked(self):
        with self.assertRaisesRegex(ValueError, "unsupported processing capability"):
            build_manifest(
                data=self._ROUTER_INPUTS[0],
                source_framework="GCAT-BCAT-Engine/workflows",
                source_output_id="SV-HOLDOUT-001:forbidden-uninstalled-processor",
                processor_request={"untrusted": "must_not_trigger_runtime"},
                process="evidence_sensitive_execution_path",
                created_at="2026-09-25T21:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
