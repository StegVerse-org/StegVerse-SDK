from __future__ import annotations

import copy
import unittest

from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_state_transition_runtime import derive_execution_request
from stegverse.manifest_state_transition_adapters import derive_shwp_inference_state_graph
from stegverse.route_resolution import SHWP_SOVEREIGN_INFERENCE_ROUTE_ID


def fixture():
    original = {
        "schema": "stegverse.resident-execution-request/v1",
        "request_id": "RESIDENT-EXEC-ECOSYSTEM-CHAT-PARENT-002",
        "state": "REQUESTED",
        "task_id": "SHWP-ECOSYSTEM-CHAT-INFERENCE-001",
        "mode": "DEDICATED_ECOSYSTEM_CHAT_PARENT",
        "entrypoint": "scripts/refresh_and_execute_resident_task.py",
        "fresh_fence_minimum_exclusive": 24,
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "github_token_runtime_authority": "NONE",
        "heartbeat_grants_execution_authority": False,
        "second_machine_required": False,
        "network_source_fetch_allowed": False,
        "request_granted_authority": False,
        "authority_effect": "NONE_REQUEST_ONLY",
        "note": "fixture-only unchanged original request intent",
        "requested_at": "2026-08-28T06:52:00-05:00",
    }
    route = {
        "route_id": SHWP_SOVEREIGN_INFERENCE_ROUTE_ID,
        "lane_class": "MANIFEST_BOUND_SOVEREIGN_INFERENCE",
        "routing_surface": "EXISTING_UNIVERSAL_INTR",
        "containment": "EXISTING_SHWP_PARENT_AUTHORITY_ONLY",
        "sandbox_required": False,
        "external_consequence_enabled": False,
    }
    return {
        "manifest_profile": "stegverse.ingress-manifest.v1",
        "manifest_profile_version": "1",
        "source_framework": "StegVerse-Labs/.github",
        "source_output_id": original["request_id"],
        "created_at": "2026-09-27T00:00:00Z",
        "declared_intent": "Evaluate original SHWP sovereign inference request",
        "requested_consequence": "EXISTING_SHWP_PARENT_ONLY",
        "payload": original,
        "hashes": {"payload_sha256": canonical_sha256(original)},
        "processing": {"capability": "sovereign_inference", "route_id": SHWP_SOVEREIGN_INFERENCE_ROUTE_ID},
        "extensions": {
            "stegverse_route": route,
            "stegverse_canonical_task": {
                "task_id": "SHWP-ECOSYSTEM-CHAT-INFERENCE-001",
                "correlation_id": "SHWP-ECOSYSTEM-CHAT-INFERENCE-001",
                "registry_repository": "StegVerse-Labs/.github",
                "observed_registry_generation": 267,
                "cosv_task_vector": "50000000100000",
                "authority_effect": "NONE",
            },
        },
    }


class TestOriginalShwpManifestBinding(unittest.TestCase):
    def test_manifest_selects_only_original_shwp_graph_without_authority(self):
        manifest = fixture()
        request = derive_execution_request(manifest)
        graph = request["state_graph"]
        self.assertEqual(graph["canonical_task_id"], "SHWP-ECOSYSTEM-CHAT-INFERENCE-001")
        self.assertEqual(graph["request"]["original_request_sha256"], canonical_sha256(manifest["payload"]))
        self.assertEqual(graph["request"]["observed_registry_generation"], 267)
        self.assertEqual(graph["request"]["cosv_task_vector"], "50000000100000")
        self.assertEqual(graph["processing_capability"], "sovereign_inference")
        self.assertTrue(graph["requires_workercoordinator_claim_fence"])
        self.assertFalse(graph["adapter_executes_lifecycle"])
        self.assertEqual(request["wire_manifest_sha256"], canonical_sha256(manifest))
        self.assertFalse(request["request_grants_authority"])

    def test_reject_stale_fence_even_when_manifest_payload_hash_is_valid(self):
        manifest = fixture()
        manifest["payload"]["fresh_fence_minimum_exclusive"] = 22
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with self.assertRaisesRegex(ValueError, "SHWP_UNCHANGED_REQUEST_MISMATCH:fresh_fence"):
            derive_shwp_inference_state_graph(manifest)

    def test_reject_wrong_cosv_and_registry_generation(self):
        manifest = fixture()
        manifest["extensions"]["stegverse_canonical_task"]["cosv_task_vector"] = "0" * 14
        with self.assertRaisesRegex(ValueError, "SHWP_COSV_BINDING_MISMATCH"):
            derive_shwp_inference_state_graph(manifest)
        manifest = fixture()
        manifest["extensions"]["stegverse_canonical_task"]["observed_registry_generation"] = None
        with self.assertRaisesRegex(ValueError, "SHWP_REGISTRY_GENERATION_REQUIRED"):
            derive_shwp_inference_state_graph(manifest)

    def test_reject_identity_route_substitution_and_authority_expansion(self):
        manifest = fixture()
        manifest["extensions"]["stegverse_canonical_task"]["task_id"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "SHWP_CANONICAL_TASK_ID_MISMATCH"):
            derive_shwp_inference_state_graph(manifest)
        manifest = fixture()
        manifest["extensions"]["stegverse_route"]["route_id"] = "stegverse.route.ecosystem-diagnostic.v1"
        with self.assertRaisesRegex(ValueError, "processing.route_id"):
            derive_shwp_inference_state_graph(manifest)
        manifest = fixture()
        manifest["payload"]["request_granted_authority"] = True
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with self.assertRaisesRegex(ValueError, "SHWP_UNCHANGED_REQUEST_MISMATCH:request_granted_authority"):
            derive_shwp_inference_state_graph(manifest)


if __name__ == "__main__":
    unittest.main()
