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


def publisher_return_bytes():
    raw = b"publisher artifact"
    digest = sha256_bytes(raw)
    value = {
        "schema": "stegverse.publisher.artifact-return/v1",
        "transfer_id": "transfer-001",
        "source_export_id": "export-001",
        "source_export_sha256": "sha256:" + "a" * 64,
        "generation_id": "generation-001",
        "manifest": {
            "artifacts": [
                {"format": "json", "path": "report.json", "sha256": digest, "bytes": len(raw)}
            ]
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
    return canonical_json(value).encode()


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
        self.assertFalse(value["final_stegverse_transition_observed"])
        self.assertFalse(value["interlock_intr_egress_observed"])
        self.assertFalse(value["far_side_transition_observed"])
        self.assertFalse(value["communication_complete"])
        self.assertEqual(value["authority_effect"], "NONE")
        self.assertEqual(verify_publisher_return_binding(value), value)

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
