from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import unittest

from stegverse.governance_ingress_runtime import external_manifest_to_public_request
from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_builder import build_manifest


def governance_request(candidate: dict) -> dict:
    return {
        "candidate": deepcopy(candidate),
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["fixture:mir-judgment"],
        },
        "signal": {
            "admitted_signal_refs": ["fixture:mir-signal"],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": "a" * 64,
            "expected_reference_state_hash": "a" * 64,
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "fixture:mir-policy",
            "delegation_ref": "fixture:mir-delegation",
            "evidence_refs": ["fixture:mir-execution"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {"fixture": "manifest-relational-invariant"},
    }


def mir_manifest(output_id: str, peer_id: str, relation_type: str) -> dict:
    data = {
        "source_data": {
            "system": "MIR",
            "record_id": output_id,
            "subject_ref": "subject:shared-001",
            "observation": {"standing": "GOOD", "sequence": 42},
        },
        "relationships": [
            {
                "target_manifest_ref": peer_id,
                "type": relation_type,
                "declared_by": "MIR",
                "governance_relevant": True,
            }
        ],
    }
    candidate = {
        "actor_class": "external_system",
        "action": "evaluate_manifested_evidence",
        "target": output_id,
        "scope": "concurrency_fixture",
        "parameters": {
            "source_framework": "MIR",
            "payload_sha256": canonical_sha256(data),
        },
    }
    return build_manifest(
        data=data,
        source_framework="MIR",
        source_instance="mir-fixture-instance",
        source_output_id=output_id,
        data_class="MIR_RELATIONAL_EVIDENCE_FIXTURE",
        processor_request=governance_request(candidate),
        process="governance",
        return_depth="result+evidence",
        created_at="2026-09-11T23:30:00Z",
        context_refs=[f"manifest:{peer_id}"],
        declared_intent="Evaluate this exact MIR-manifested evidence and its declared source-native relationship without inferring relationships from transport concurrency.",
        requested_consequence="Return bounded governance evidence only; do not merge this manifest with another submission unless an explicit manifested relationship and governance context requires it.",
    )


def convert(manifest: dict) -> dict:
    return external_manifest_to_public_request(manifest)


class ManifestRelationalInvariantConcurrencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest_a = mir_manifest("mir-output-A", "mir-output-B", "CORROBORATES")
        self.manifest_b = mir_manifest("mir-output-B", "mir-output-A", "SAME_SUBJECT")

    def test_concurrent_same_route_preserves_independent_manifest_identity(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            request_a, request_b = list(pool.map(convert, [self.manifest_a, self.manifest_b]))

        identity_a = request_a["input"]["ingress_manifest_identity"]
        identity_b = request_b["input"]["ingress_manifest_identity"]

        self.assertEqual(identity_a["source_framework"], "MIR")
        self.assertEqual(identity_b["source_framework"], "MIR")
        self.assertNotEqual(identity_a["source_output_id"], identity_b["source_output_id"])
        self.assertNotEqual(identity_a["canonical_manifest_sha256"], identity_b["canonical_manifest_sha256"])
        self.assertNotEqual(request_a["request_id"], request_b["request_id"])
        self.assertEqual(
            request_a["execution_provenance"]["route_id"],
            request_b["execution_provenance"]["route_id"],
        )
        self.assertNotEqual(
            request_a["execution_provenance"]["state_binding_hash"],
            request_b["execution_provenance"]["state_binding_hash"],
        )

    def test_source_data_and_declared_relationships_survive_conversion_unchanged(self):
        request_a = convert(self.manifest_a)
        request_b = convert(self.manifest_b)

        self.assertEqual(request_a["input"]["input_data"]["payload"], self.manifest_a["payload"])
        self.assertEqual(request_b["input"]["input_data"]["payload"], self.manifest_b["payload"])
        self.assertEqual(
            request_a["input"]["input_data"]["payload"]["relationships"],
            self.manifest_a["payload"]["relationships"],
        )
        self.assertEqual(
            request_b["input"]["input_data"]["payload"]["relationships"],
            self.manifest_b["payload"]["relationships"],
        )

    def test_concurrency_does_not_inject_undeclared_relationships(self):
        manifest_c = mir_manifest("mir-output-C", "mir-output-D", "OBSERVED_WITHOUT_DEPENDENCY")
        manifest_c["payload"]["relationships"] = []
        manifest_c["hashes"]["payload_sha256"] = canonical_sha256(manifest_c["payload"])
        manifest_c["extensions"]["stegverse_governance_request"]["candidate"]["parameters"]["payload_sha256"] = manifest_c["hashes"]["payload_sha256"]
        manifest_c["candidate"]["parameters"]["payload_sha256"] = manifest_c["hashes"]["payload_sha256"]
        manifest_c["hashes"]["candidate_sha256"] = canonical_sha256(manifest_c["candidate"])

        manifest_d = mir_manifest("mir-output-D", "mir-output-C", "CORROBORATES")
        with ThreadPoolExecutor(max_workers=2) as pool:
            request_c, request_d = list(pool.map(convert, [manifest_c, manifest_d]))

        self.assertEqual(request_c["input"]["input_data"]["payload"]["relationships"], [])
        self.assertEqual(
            request_d["input"]["input_data"]["payload"]["relationships"],
            manifest_d["payload"]["relationships"],
        )

    def test_relationship_mutation_changes_manifest_identity_and_request_identity(self):
        original = self.manifest_a
        mutated = mir_manifest("mir-output-A", "mir-output-B", "CONFLICT")

        original_request = convert(original)
        mutated_request = convert(mutated)

        self.assertNotEqual(original["hashes"]["payload_sha256"], mutated["hashes"]["payload_sha256"])
        self.assertNotEqual(
            original_request["input"]["ingress_manifest_identity"]["canonical_manifest_sha256"],
            mutated_request["input"]["ingress_manifest_identity"]["canonical_manifest_sha256"],
        )
        self.assertNotEqual(original_request["request_id"], mutated_request["request_id"])

    def test_arrival_order_does_not_change_semantics(self):
        forward = [convert(self.manifest_a), convert(self.manifest_b)]
        reverse = [convert(self.manifest_b), convert(self.manifest_a)]

        by_source_forward = {
            item["input"]["ingress_manifest_identity"]["source_output_id"]: item
            for item in forward
        }
        by_source_reverse = {
            item["input"]["ingress_manifest_identity"]["source_output_id"]: item
            for item in reverse
        }

        for source_output_id in ("mir-output-A", "mir-output-B"):
            self.assertEqual(
                by_source_forward[source_output_id]["request_id"],
                by_source_reverse[source_output_id]["request_id"],
            )
            self.assertEqual(
                by_source_forward[source_output_id]["input"]["input_data"]["payload"],
                by_source_reverse[source_output_id]["input"]["input_data"]["payload"],
            )


if __name__ == "__main__":
    unittest.main()
