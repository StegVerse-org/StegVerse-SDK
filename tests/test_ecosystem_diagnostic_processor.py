from __future__ import annotations

import unittest

from stegverse.ecosystem_diagnostic_runtime import execute_manifest
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
        self.assertEqual(available_processors(), ("ecosystem_diagnostic", "governance"))
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


if __name__ == "__main__":
    unittest.main()
