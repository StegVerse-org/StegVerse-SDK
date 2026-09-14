from __future__ import annotations

import base64
import copy
import hashlib
import json
import unittest

from stegverse.publisher_return_binding import (
    PublisherReturnBindingError,
    READY_STATE,
    assemble_publisher_return,
    verify_publisher_return_binding,
)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_value(value) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def manifest():
    payload = {"native": "value"}
    route_id = "stegverse.route.example-verification.v1"
    return {
        "manifest_profile": "stegverse.ingress-manifest.v1",
        "manifest_profile_version": "1",
        "source_framework": "fixture-framework",
        "source_output_id": "fixture-output-001",
        "created_at": "2026-09-12T00:00:00Z",
        "payload": payload,
        "processing": {"capability": "verification", "route_id": route_id},
        "declared_intent": "Verify fixture",
        "requested_consequence": "NONE",
        "hashes": {"payload_sha256": sha256_value(payload)},
        "extensions": {"stegverse_route": {"route_id": route_id}},
        "return_projection": {"mode": "ALL", "transition_classes": []},
        "completion": {
            "direction": "SOUTH",
            "initiator": {"class": "external_framework", "ref": "fixture-caller"},
            "publisher": {
                "stage": "PUBLISHER",
                "required": True,
                "package_profile": "stegverse.publisher.evidence-report-package/v1",
            },
            "egress": {
                "final_stegverse_transition_surface": "LLM_ADAPTER",
                "transport": "INTERLOCK_INTR",
                "far_side_transition_required": True,
            },
        },
    }


def publisher_return_value():
    raw = b"publisher artifact"
    digest = sha256_bytes(raw)
    return {
        "schema": "stegverse.publisher.artifact-return/v1",
        "transfer_id": "transfer-001",
        "source_export_id": "export-001",
        "source_export_sha256": "sha256:" + "a" * 64,
        "generation_id": "generation-001",
        "manifest": {
            "manifest_sha256": "sha256:" + "b" * 64,
            "artifacts": [
                {"format": "json", "path": "report.json", "sha256": digest, "bytes": len(raw)}
            ],
        },
        "rendering_receipt": {"generation_id": "generation-001"},
        "artifacts": [
            {
                "format": "json",
                "path": "report.json",
                "sha256": digest,
                "bytes": len(raw),
                "content_base64": base64.b64encode(raw).decode("ascii"),
            }
        ],
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }


def publisher_return_bytes():
    return canonical_json(publisher_return_value()).encode()


def mir_capsule(value):
    return {
        "profile": "stegverse.sdk.downstream-completion-capsule/v1",
        "manifest_hash": sha256_value(value),
        "completion_hash": sha256_value(value["completion"]),
        "response_to": "stegverse-return-exit:fixture-001",
        "retained_packet_sha256": "c" * 64,
        "completion": copy.deepcopy(value["completion"]),
        "declarations": {
            "publisher_required": True,
            "publisher_package_profile": "stegverse.publisher.evidence-report-package/v1",
            "final_stegverse_side_egress_surface": "LLM_ADAPTER",
            "interlock_intr_egress_required": True,
            "far_side_transition_required": True,
        },
        "authority_effect": "NONE",
    }


def mir_publisher_return_value(value, capsule):
    returned = publisher_return_value()
    returned["roundtrip_binding"] = {
        "profile": "stegverse.publisher.mir-roundtrip-binding/v1",
        "goal_task_id": "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001",
        "cosv_id": "50000000100000",
        "publisher_transition": "PUBLISHER_ARTIFACT_RETURN_PRODUCED",
        "manifest_hash": capsule["manifest_hash"],
        "completion_hash": capsule["completion_hash"],
        "response_to": capsule["response_to"],
        "retained_packet_sha256": capsule["retained_packet_sha256"],
        "downstream_completion_capsule": copy.deepcopy(capsule),
        "sdk_processor_state": {
            "state": "SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED",
            "processor_result_observed": True,
        },
        "publisher_transition_observed": True,
        "sdk_return_binding_observed": False,
        "final_stegverse_side_egress_transition_observed": False,
        "interlock_intr_egress_observed": False,
        "far_side_transition_observed": False,
        "authentic_external_mir_endpoint_substitution_observed": False,
        "communication_complete": False,
        "authority_effect": "NONE",
        "publisher_return_schema": returned["schema"],
        "publisher_return_source_export_id": returned["source_export_id"],
        "publisher_return_source_export_sha256": returned["source_export_sha256"],
        "publisher_return_generation_id": returned["generation_id"],
        "publisher_artifact_manifest_sha256": returned["manifest"]["manifest_sha256"],
    }
    return returned


class PublisherReturnBindingTests(unittest.TestCase):
    def test_binds_exact_publisher_return_to_initiator_and_egress(self):
        value = assemble_publisher_return(
            manifest=manifest(),
            manifest_receipt_id="MR-0123456789ABCDEF",
            publisher_return_bytes=publisher_return_bytes(),
        )
        self.assertEqual(value["initiator"]["ref"], "fixture-caller")
        self.assertEqual(value["egress"]["final_stegverse_transition_surface"], "LLM_ADAPTER")
        self.assertEqual(value["communication_state"], READY_STATE)
        self.assertTrue(value["sdk_return_binding_observed"])
        self.assertFalse(value["final_stegverse_transition_observed"])
        self.assertFalse(value["interlock_intr_egress_observed"])
        self.assertFalse(value["far_side_transition_observed"])
        self.assertFalse(value["communication_complete"])
        self.assertEqual(value["authority_effect"], "NONE")
        self.assertEqual(verify_publisher_return_binding(value), value)

    def test_mir_roundtrip_exact_capsule_continuity_succeeds(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        value = assemble_publisher_return(
            manifest=original_manifest,
            manifest_receipt_id="MR-0123456789ABCDEF",
            publisher_return_bytes=canonical_json(returned).encode(),
            downstream_completion_capsule=capsule,
        )
        self.assertTrue(value["publisher_transition_observed"])
        self.assertTrue(value["sdk_return_binding_observed"])
        self.assertEqual(value["mir_roundtrip"]["goal_task_id"], "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001")
        self.assertEqual(value["mir_roundtrip"]["cosv_id"], "50000000100000")
        self.assertEqual(value["mir_roundtrip"]["manifest_hash"], capsule["manifest_hash"])
        self.assertEqual(value["mir_roundtrip"]["retained_packet_sha256"], capsule["retained_packet_sha256"])
        self.assertFalse(value["authentic_external_mir_endpoint_substitution_observed"])
        self.assertEqual(verify_publisher_return_binding(value), value)

    def test_mir_return_without_original_capsule_fails_closed(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        with self.assertRaisesRegex(PublisherReturnBindingError, "original SDK downstream completion capsule required"):
            assemble_publisher_return(
                manifest=original_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
            )

    def test_mir_carried_capsule_mutation_fails_closed(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        returned["roundtrip_binding"]["downstream_completion_capsule"]["retained_packet_sha256"] = "d" * 64
        returned["roundtrip_binding"]["retained_packet_sha256"] = "d" * 64
        with self.assertRaisesRegex(PublisherReturnBindingError, "does not exactly match original SDK capsule"):
            assemble_publisher_return(
                manifest=original_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
                downstream_completion_capsule=capsule,
            )

    def test_mir_original_manifest_mutation_fails_closed(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        mutated_manifest = copy.deepcopy(original_manifest)
        mutated_manifest["declared_intent"] = "Mutated after Publisher"
        with self.assertRaisesRegex(PublisherReturnBindingError, "manifest hash does not match original manifest"):
            assemble_publisher_return(
                manifest=mutated_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
                downstream_completion_capsule=capsule,
            )

    def test_mir_publisher_identity_mutation_fails_closed(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        returned["roundtrip_binding"]["publisher_return_generation_id"] = "wrong-generation"
        with self.assertRaisesRegex(PublisherReturnBindingError, "Publisher generation binding mismatch"):
            assemble_publisher_return(
                manifest=original_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
                downstream_completion_capsule=capsule,
            )

    def test_mir_downstream_promotion_fails_closed(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        returned["roundtrip_binding"]["interlock_intr_egress_observed"] = True
        with self.assertRaisesRegex(PublisherReturnBindingError, "interlock_intr_egress_observed=false"):
            assemble_publisher_return(
                manifest=original_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
                downstream_completion_capsule=capsule,
            )

    def test_noncanonical_publisher_return_fails_closed(self):
        pretty = json.dumps(json.loads(publisher_return_bytes()), indent=2).encode()
        with self.assertRaisesRegex(PublisherReturnBindingError, "not canonical JSON"):
            assemble_publisher_return(
                manifest=manifest(),
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=pretty,
            )

    def test_artifact_mutation_fails_closed(self):
        value = json.loads(publisher_return_bytes())
        value["artifacts"][0]["content_base64"] = base64.b64encode(b"mutated").decode("ascii")
        with self.assertRaisesRegex(PublisherReturnBindingError, "digest mismatch"):
            assemble_publisher_return(
                manifest=manifest(),
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(value).encode(),
            )

    def test_manifest_without_required_publisher_stage_fails_closed(self):
        value = manifest()
        value["completion"]["publisher"]["required"] = False
        with self.assertRaises((PublisherReturnBindingError, ValueError)):
            assemble_publisher_return(
                manifest=value,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=publisher_return_bytes(),
            )

    def test_binding_cannot_be_mutated_into_completion(self):
        value = assemble_publisher_return(
            manifest=manifest(),
            manifest_receipt_id="MR-0123456789ABCDEF",
            publisher_return_bytes=publisher_return_bytes(),
        )
        value["communication_complete"] = True
        with self.assertRaises(PublisherReturnBindingError):
            verify_publisher_return_binding(value)


if __name__ == "__main__":
    unittest.main()
