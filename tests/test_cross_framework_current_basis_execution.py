import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_cross_framework_current_basis_v04 import (
    EXPECTED_MANIFEST_SHA256,
    CrossFrameworkExecutionError,
    _load_manifest,
    _transition_receipt,
)


MANIFEST = Path("inspection/examples/cross-framework-current-basis-request.draft.json")


class CrossFrameworkExecutionHarnessTests(unittest.TestCase):
    def test_frozen_manifest_exact_identity_is_required(self):
        self.assertEqual(hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), EXPECTED_MANIFEST_SHA256)
        value = _load_manifest(MANIFEST)
        self.assertEqual(
            value["input"]["comparison_input"]["vector_schema"],
            "stegverse.cross-framework-current-basis-vector.v0.4",
        )

    def test_modified_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            path.write_bytes(MANIFEST.read_bytes() + b"\n")
            with self.assertRaisesRegex(CrossFrameworkExecutionError, "SHA-256 mismatch"):
                _load_manifest(path)

    def test_transition_receipt_is_post_observation_and_non_authorizing(self):
        vector = _load_manifest(MANIFEST)["input"]["comparison_input"]
        receipt = _transition_receipt(
            vector=vector,
            native_result={"s1_observed": True, "evaluation": {"disposition": "FAIL_CLOSED"}},
            sovereign_result={"manifest_receipt_id": "MR-EXAMPLE", "governance_state": "FAIL_CLOSED"},
        )
        self.assertEqual(receipt["receipt_timing"], "POST_OBSERVATION")
        self.assertFalse(receipt["historical_s0_receipt_required"])
        self.assertFalse(receipt["material_change_is_invalidation_input"])
        self.assertEqual(receipt["authority_effect"], "EVIDENCE_ONLY_NO_RETROACTIVE_PERMISSION")
        body = dict(receipt)
        observed_hash = body.pop("receipt_hash")
        canonical = json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
            default=str,
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), observed_hash)


if __name__ == "__main__":
    unittest.main()
