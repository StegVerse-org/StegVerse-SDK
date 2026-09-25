"""Shared existing SDK→Publisher schema compatibility, never a live InTr test."""
from __future__ import annotations
import hashlib
import tempfile
import unittest
from pathlib import Path

from stegverse.publisher_review_transfer import build_source_only_review_transfer, canonical_bytes
from stegverse.publisher_return_binding import verify_publisher_return
from stegverse.ecosystem_diagnostic_runtime import execute_manifest as diagnostic
from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest

try:
    from publisher.intr_artifact_transfer import process_artifact_transfer, verify_artifact_return
except ImportError:
    process_artifact_transfer = verify_artifact_return = None

@unittest.skipIf(process_artifact_transfer is None, "exact pinned Publisher source is not installed")
class ReviewPublisherCrossRepoTests(unittest.TestCase):
    def test_existing_publisher_consumes_actual_sdk_source_packet(self):
        m=build_exp3_manifest()
        d=diagnostic(m)
        originals={
            "experiment-one-mir-side.pdf":b"%PDF-1.4\n% partner fixture\n",
            "IMG_3282.png":b"\x89PNG\r\n\x1a\nSDK evaluation fixture",
        }
        p=build_source_only_review_transfer(
            sdk_manifest=m,diagnostic_result=d,
            original_assets=originals,
            expected_original_sha256={k:hashlib.sha256(v).hexdigest() for k,v in originals.items()},
            approval_ref="test-evaluator-only",
        )
        with tempfile.TemporaryDirectory() as td:
            produced,raw=process_artifact_transfer(canonical_bytes(p),Path(td))
            self.assertEqual(produced,verify_artifact_return(raw))
            self.assertEqual(produced,verify_publisher_return(raw))
            self.assertEqual(produced["source_export_schema"],"stegverse.publisher.evidence-report-package/v1")
            self.assertEqual(len([r for r in produced["artifacts"] if r["format"]=="source-original"]),4)
            self.assertFalse(produced["publication_authorized"])
            self.assertNotIn("roundtrip_binding",produced)
            self.assertEqual(produced["rendering_receipt"]["result"],"GENERATED_VALIDATED_NOT_PUBLISHED")

if __name__=="__main__":
    unittest.main()
