from __future__ import annotations

from copy import deepcopy
import json
import unittest
from pathlib import Path

from stegverse.governance_ingress_runtime import external_manifest_to_public_request
from stegverse.manifest_contract import validate_ingress_manifest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "inspection" / "examples" / "external-framework-generic-manifest.json"
SCHEMA = ROOT / "schemas" / "stegverse.ingress-manifest.v1.schema.json"


class GenericManifestProcessingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_external_framework_payload_retains_native_class(self) -> None:
        canonical = validate_ingress_manifest(self.manifest)
        payload = canonical["payload"]
        self.assertEqual(payload["framework"], "ELAN")
        self.assertEqual(payload["object_class"], "relational_state_observation")
        self.assertNotEqual(payload, canonical["candidate"])
        self.assertFalse(canonical["external_manifest_grants_authority"])

    def test_processing_capability_is_separate_from_route_and_payload_class(self) -> None:
        canonical = validate_ingress_manifest(self.manifest)
        self.assertEqual(canonical["processing"]["capability"], "governance")
        self.assertEqual(
            canonical["processing"]["route_id"],
            "stegverse.route.canonical-governed.v1",
        )
        request = external_manifest_to_public_request(self.manifest)
        binding = request["input"]["route_binding"]
        self.assertEqual(binding["processor_capability"], "governance")
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

    def test_non_governance_processor_manifest_does_not_require_governance_fields(self) -> None:
        manifest = {
            "manifest_profile": "stegverse.ingress-manifest.v1",
            "manifest_profile_version": "1",
            "source_framework": "fixture-verifier",
            "source_output_id": "verification-001",
            "created_at": "2026-09-08T00:00:00Z",
            "payload": {"artifact": "abc"},
            "processing": {
                "capability": "verification",
                "route_id": "stegverse.route.synthetic-verification.v1",
            },
            "declared_intent": "Verify a source artifact.",
            "requested_consequence": "Return verification evidence only.",
            "hashes": {
                "payload_sha256": "b301a5f89e0db5e3f4429f2218634077508d91b1af15cd946c7a842b06c96720"
            },
            "extensions": {
                "stegverse_route": {
                    "route_id": "stegverse.route.synthetic-verification.v1",
                    "lane_class": "TEST",
                    "routing_surface": "SYNTHETIC",
                    "containment": "NO_CONSEQUENCE",
                    "sandbox_required": False,
                    "external_consequence_enabled": False,
                }
            },
        }
        # Fix the payload hash through the same canonical implementation used by the SDK.
        from stegverse.governance_navigation import canonical_sha256

        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        canonical = validate_ingress_manifest(manifest)
        self.assertEqual(canonical["processing"]["capability"], "verification")
        self.assertNotIn("candidate", canonical)
        self.assertNotIn("stegverse_governance_request", canonical["extensions"])
        with self.assertRaisesRegex(ValueError, "unsupported manifest route"):
            external_manifest_to_public_request(manifest)

    def test_legacy_governance_v1_without_processing_is_derived_compatibly(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest.pop("processing")
        canonical = validate_ingress_manifest(manifest)
        self.assertEqual(canonical["processing"]["capability"], "governance")
        self.assertTrue(canonical["processing"]["derived_from_legacy_v1_route"])

    def test_processing_route_mismatch_fails_closed(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["processing"]["route_id"] = "stegverse.route.other.v1"
        with self.assertRaisesRegex(ValueError, "processing.route_id must match"):
            validate_ingress_manifest(manifest)

    def test_payload_commitment_requires_explicit_verification_profile(self) -> None:
        manifest = deepcopy(self.manifest)
        commitment = manifest["hashes"]["payload_sha256"]
        manifest.pop("payload")
        manifest["hashes"].pop("payload_sha256")
        manifest["payload_commitment"] = commitment
        with self.assertRaisesRegex(ValueError, "payload_commitment_profile"):
            validate_ingress_manifest(manifest)
        manifest["payload_commitment_profile"] = "sha256"
        canonical = validate_ingress_manifest(manifest)
        self.assertEqual(canonical["payload_commitment"], commitment)
        request = external_manifest_to_public_request(manifest)
        self.assertEqual(
            request["input"]["input_data"]["payload_commitment_profile"], "sha256"
        )

    def test_published_schema_is_processor_generic_and_projection_explicit(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        payload_types = set(schema["properties"]["payload"]["type"])
        self.assertEqual(
            payload_types, {"object", "array", "string", "number", "boolean", "null"}
        )
        self.assertNotIn("candidate", schema["required"])
        self.assertIn("processing", schema["properties"])
        extensions = schema["properties"]["extensions"]
        self.assertEqual(extensions["required"], ["stegverse_route"])
        route_id = extensions["properties"]["stegverse_route"]["properties"]["route_id"]
        self.assertNotIn("const", route_id)
        self.assertEqual(
            schema["properties"]["payload_commitment_profile"]["enum"], ["sha256"]
        )
        projection = schema["properties"]["return_projection"]["properties"]["mode"]["enum"]
        self.assertEqual(set(projection), {"ALL", "SELECTED", "NONE"})


if __name__ == "__main__":
    unittest.main()
