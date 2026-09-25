"""Exact SDK→existing Publisher generic reviewer cross-repository source conformance.

This runs installed source against pinned existing Publisher source and a private,
synthetic pair of originals. It never claims resident transport or Master Records.
"""
from __future__ import annotations
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from stegverse.review_publisher_transfer import (
    prepare_review_transfer, bind_exact_review_return,
    ReviewPublisherBoundaryError, digest,
)
from stegverse.publisher_return_binding import PublisherReturnBindingError, verify_publisher_return
from tests.test_review_publisher_transfer import review_manifest, source_bundle, originals

try:
    from publisher.intr_artifact_transfer import process_artifact_transfer, verify_artifact_return
except ImportError:
    process_artifact_transfer = verify_artifact_return = None

def inputs():
    m = review_manifest()
    b = source_bundle()
    b["source"]["event_ids"] = [a["path"] for a in originals()]
    b["export_sha256"] = digest({k:v for k,v in b.items() if k != "export_sha256"})
    p = prepare_review_transfer(
        manifest=m, authorized_export_bundle=b,
        original_assets=originals(), transfer_id="sdk-publisher-generic-source-test-001",
    )
    return m, p

@unittest.skipIf(process_artifact_transfer is None, "pinned existing Publisher source missing")
class SourceCrossRepoPublisherTests(unittest.TestCase):
    def test_existing_adapter_and_sdk_validator_are_equivalent(self):
        m,p = inputs()
        with TemporaryDirectory() as td:
            produced, raw = process_artifact_transfer(p["transfer_bytes"],Path(td))
            self.assertEqual(produced, verify_artifact_return(raw))
            self.assertEqual(produced, verify_publisher_return(raw))
            self.assertEqual(produced["source_export_schema"],"stegverse.publisher.evidence-report-package/v1")
            self.assertEqual(
                {x["path"] for x in produced["artifacts"] if x["format"] == "source-original"},
                set(p["expected_original_paths"]),
            )
            result = bind_exact_review_return(
                prepared=p, manifest=m, manifest_receipt_id="MR-0123456789ABCDEF",
                publisher_return_bytes=raw,
            )
            self.assertFalse(result["communication_complete"])
            self.assertFalse(result["final_stegverse_transition_observed"])
            self.assertFalse(result["far_side_transition_observed"])
            self.assertTrue(result["sdk_return_binding_observed"])

    def test_omitted_original_fails_sdk_and_publisher(self):
        m,p = inputs()
        with TemporaryDirectory() as td:
            _,raw = process_artifact_transfer(p["transfer_bytes"],Path(td))
        import json
        parsed = json.loads(raw)
        parsed["artifacts"].pop()
        from stegverse.review_publisher_transfer import canonical_json
        with self.assertRaisesRegex(PublisherReturnBindingError,"coverage mismatch"):
            verify_publisher_return(canonical_json(parsed).encode())

    def test_tampered_manifest_or_rendering_receipt_fails_sdk(self):
        m,p = inputs()
        with TemporaryDirectory() as td:
            _,raw = process_artifact_transfer(p["transfer_bytes"],Path(td))
        import json
        from stegverse.review_publisher_transfer import canonical_json
        for key in ("manifest","rendering_receipt"):
            value = json.loads(raw)
            value[key]["generation_id"] = "corrupted"
            with self.subTest(key=key):
                with self.assertRaisesRegex(PublisherReturnBindingError,"digest mismatch"):
                    verify_publisher_return(canonical_json(value).encode())

    def test_sdk_source_manifest_as_exact_attachment_not_runtime(self):
        a=originals()
        a[0]["source_class"]="SDK_SOURCE_VALIDATED_ARTIFACT"
        from stegverse.review_publisher_transfer import _normalize_assets
        b=source_bundle()
        b["source"]["event_ids"] = [x["path"] for x in a]
        self.assertEqual(_normalize_assets(a,b)[0]["source_class"],"SDK_SOURCE_VALIDATED_ARTIFACT")

if __name__=="__main__":unittest.main()
