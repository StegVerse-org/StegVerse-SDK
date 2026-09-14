from __future__ import annotations

import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from stegverse.publisher_return_binding import PublisherReturnBindingError
from stegverse.publisher_return_materialization import (
    MATERIALIZATION_RECEIPT_SCHEMA,
    PublisherReturnMaterializationError,
    canonical_json_bytes,
    materialize_publisher_return_binding,
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


class PublisherReturnMaterializationTests(unittest.TestCase):
    def test_materializes_exact_mir_binding_without_promoting_egress(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "sdk-return.json"
            receipt = materialize_publisher_return_binding(
                manifest=original_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
                downstream_completion_capsule=capsule,
                output_path=output,
            )
            retained = output.read_bytes()
            binding = json.loads(retained)
            self.assertEqual(retained, canonical_json_bytes(binding))
            self.assertEqual(receipt["schema"], MATERIALIZATION_RECEIPT_SCHEMA)
            self.assertEqual(receipt["output_sha256"], sha256_bytes(retained))
            self.assertEqual(receipt["binding_schema"], "stegverse.sdk.publisher-return-binding/v1")
            self.assertEqual(receipt["communication_state"], "READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION")
            self.assertTrue(receipt["sdk_return_binding_observed"])
            self.assertFalse(receipt["final_stegverse_transition_observed"])
            self.assertFalse(receipt["interlock_intr_egress_observed"])
            self.assertFalse(receipt["far_side_transition_observed"])
            self.assertFalse(receipt["authentic_external_mir_endpoint_substitution_observed"])
            self.assertFalse(receipt["communication_complete"])
            self.assertFalse(receipt["input_runtime_provenance_claimed"])
            self.assertFalse(receipt["authentic_mir_provenance_claimed"])
            self.assertEqual(receipt["authority_effect"], "NONE")

    def test_mir_materialization_requires_original_completion_capsule(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(PublisherReturnBindingError, "original SDK downstream completion capsule required"):
                materialize_publisher_return_binding(
                    manifest=original_manifest,
                    manifest_receipt_id="MR-0123456789ABCDEF",
                    publisher_return_bytes=canonical_json(returned).encode(),
                    output_path=Path(temp) / "sdk-return.json",
                )

    def test_existing_output_fails_closed_by_default(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "sdk-return.json"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(PublisherReturnMaterializationError, "refusing to overwrite"):
                materialize_publisher_return_binding(
                    manifest=original_manifest,
                    manifest_receipt_id="MR-0123456789ABCDEF",
                    publisher_return_bytes=canonical_json(returned).encode(),
                    downstream_completion_capsule=capsule,
                    output_path=output,
                )
            self.assertEqual(output.read_bytes(), b"existing")

    def test_explicit_overwrite_replaces_only_with_verified_canonical_binding(self):
        original_manifest = manifest()
        capsule = mir_capsule(original_manifest)
        returned = mir_publisher_return_value(original_manifest, capsule)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "sdk-return.json"
            output.write_bytes(b"existing")
            receipt = materialize_publisher_return_binding(
                manifest=original_manifest,
                manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=canonical_json(returned).encode(),
                downstream_completion_capsule=capsule,
                output_path=output,
                overwrite=True,
            )
            self.assertNotEqual(output.read_bytes(), b"existing")
            self.assertEqual(receipt["output_sha256"], sha256_bytes(output.read_bytes()))


if __name__ == "__main__":
    unittest.main()
