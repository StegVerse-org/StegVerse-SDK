"""Source-only review transfer tests. Never assert real InTr/Publisher runtime."""
from __future__ import annotations
import copy
import hashlib
import json
import unittest
from stegverse.publisher_review_transfer import (
    SDKReviewTransferError,build_source_only_review_transfer,canonical_bytes,
)
from stegverse.ecosystem_diagnostic_runtime import execute_manifest as diagnostic
from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest


def files():
    return {
        "experiment-one-mir-side.pdf":b"%PDF-1.4\n% bounded partner fixture\n",
        "IMG_3282.png":b"\x89PNG\r\n\x1a\n" + b"original screenshot fixture",
    }

def bundle(**override):
    manifest = build_exp3_manifest()
    result = diagnostic(manifest)
    inputs = files()
    args = {
        "sdk_manifest":manifest,"diagnostic_result":result,
        "original_assets":inputs,
        "expected_original_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in inputs.items()},
        "approval_ref":"explicit-review-instruction-test",
    }
    args.update(override)
    return build_source_only_review_transfer(**args)

class PublisherReviewTransferTests(unittest.TestCase):
    def test_review_produces_complete_existing_transfer_and_originals(self):
        value=bundle()
        self.assertEqual(value["schema"],"stegverse.publisher.artifact-transfer/v1")
        self.assertEqual(value["export_bundle"]["schema_version"],"stegverse.publisher.evidence-report-package/v1")
        self.assertEqual(value["export_bundle"]["authorization"]["purpose"],"EXTERNAL_EVALUATOR_REVIEW")
        self.assertEqual(len(value["evaluator_assets"]),4)
        self.assertEqual(len(value["export_bundle"]["document"]["sections"]),6)
        self.assertEqual({x["section_id"] for x in value["export_bundle"]["document"]["sections"][:4]},
                         {"observe","demonstrate","retain","reconstruct"})
        self.assertTrue(all("LIMITATION" in x["body"] for x in value["export_bundle"]["document"]["sections"][:4]))
        for asset in value["evaluator_assets"]:
            self.assertEqual("sha256:"+hashlib.sha256(
                __import__("base64").b64decode(asset["content_base64"])).hexdigest(),asset["sha256"])
        self.assertEqual(value["authorization_ref"],"explicit-review-instruction-test")
        self.assertFalse(value["publication_authorized"])
        self.assertFalse(value["execution_authorized"])
        self.assertNotIn("roundtrip_binding",value)

    def test_missing_exact_original_detected(self):
        originals=files()
        originals.pop("IMG_3282.png")
        with self.assertRaisesRegex(SDKReviewTransferError,"coverage mismatch"):
            bundle(original_assets=originals)

    def test_modified_original_detected(self):
        originals=files()
        originals["IMG_3282.png"]+=b"mutation"
        with self.assertRaisesRegex(SDKReviewTransferError,"SHA-256 mismatch"):
            bundle(original_assets=originals)

    def test_corrupt_sdk_result_detected(self):
        manifest=build_exp3_manifest()
        result=diagnostic(manifest)
        result["results"][0]["observation_state"]="FAIL"
        with self.assertRaisesRegex(SDKReviewTransferError,"result_binding_hash mismatch"):
            bundle(sdk_manifest=manifest,diagnostic_result=result)

    def test_review_requires_publisher_in_manifest(self):
        m=build_exp3_manifest()
        m["completion"]["publisher"]["required"]=False
        with self.assertRaisesRegex(SDKReviewTransferError,"must require Publisher"):
            bundle(sdk_manifest=m)

    def test_no_approval_reference_fails_closed(self):
        with self.assertRaisesRegex(SDKReviewTransferError,"instruction reference"):
            bundle(approval_ref="")

    def test_canonical_transfer_is_reproducible(self):
        self.assertEqual(canonical_bytes(bundle()),canonical_bytes(bundle()))

if __name__=="__main__": unittest.main()
