from __future__ import annotations

import json
import unittest
from pathlib import Path

from stegverse.governance_ingress_runtime import external_manifest_to_public_request
from stegverse.governance_navigation import validate_external_manifest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "inspection" / "examples" / "external-framework-generic-manifest.json"
SCHEMA = ROOT / "schemas" / "stegverse.ingress-manifest.v1.schema.json"


class GenericManifestProcessingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_external_framework_payload_retains_native_class(self) -> None:
        canonical = validate_external_manifest(self.manifest)
        payload = canonical["payload"]
        self.assertEqual(payload["framework"], "ELAN")
        self.assertEqual(payload["object_class"], "relational_state_observation")
        self.assertNotEqual(payload, canonical["candidate"])
        self.assertFalse(canonical["external_manifest_grants_authority"])

    def test_processing_route_is_separate_from_payload_class(self) -> None:
        request = external_manifest_to_public_request(self.manifest)
        binding = request["input"]["route_binding"]
        self.assertEqual(binding["route_id"], "stegverse.route.canonical-governed.v1")
        self.assertEqual(
            request["input"]["input_data"]["payload"]["object_class"],
            "relational_state_observation",
        )
        self.assertEqual(request["return_projection"], "SELECTED")
        self.assertFalse(request["authority_claim"])

    def test_governance_request_candidate_is_hash_bound_without_redefining_payload(self) -> None:
        request = external_manifest_to_public_request(self.manifest)
        governance_candidate = request["input"]["steggate_request"]["candidate"]
        self.assertEqual(governance_candidate, self.manifest["candidate"])
        self.assertNotIn("events", governance_candidate)
        self.assertIn("events", request["input"]["input_data"]["payload"])

    def test_published_schema_declares_arbitrary_payload_and_artifact_projection(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        payload_types = set(schema["properties"]["payload"]["type"])
        self.assertEqual(payload_types, {"object", "array", "string", "number", "boolean", "null"})
        projection = schema["properties"]["return_projection"]["properties"]["mode"]["enum"]
        self.assertEqual(set(projection), {"ALL", "SELECTED", "NONE"})
        route = schema["properties"]["extensions"]["properties"]["stegverse_route"]
        self.assertEqual(
            route["properties"]["route_id"]["const"],
            "stegverse.route.canonical-governed.v1",
        )


if __name__ == "__main__":
    unittest.main()
