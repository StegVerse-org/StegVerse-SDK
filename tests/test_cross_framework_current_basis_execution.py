import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_cross_framework_current_basis_v04 import (
    EXPECTED_MANIFEST_GIT_BLOB_SHA1,
    EXPECTED_MANIFEST_SHA256,
    CrossFrameworkExecutionError,
    _load_manifest,
    _portable_replay_reference,
    _replay_reference_text,
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

    def test_replay_reference_is_plain_text_copy_safe_and_bound(self):
        manifest_receipt_id = "MR-EXAMPLE-001"
        transition = {
            "transition_id": "DELTA-S0-S1",
            "receipt_hash": "a" * 64,
        }
        result = {
            "manifest_receipt_id": manifest_receipt_id,
            "master_records_custody_status": "RECORDED",
        }
        text = _replay_reference_text(
            manifest_receipt_id=manifest_receipt_id,
            transition_receipt=transition,
            sovereign_result=result,
        )
        lines = text.splitlines()
        self.assertTrue(lines)
        self.assertTrue(all("=" in line for line in lines))
        values = dict(line.split("=", 1) for line in lines)
        self.assertEqual(values["TEST_ID"], "cross-framework-current-basis-001")
        self.assertEqual(values["MANIFEST_RECEIPT_ID"], manifest_receipt_id)
        self.assertEqual(values["MANIFEST_SHA256"], EXPECTED_MANIFEST_SHA256)
        self.assertEqual(values["MANIFEST_GIT_BLOB_SHA1"], EXPECTED_MANIFEST_GIT_BLOB_SHA1)
        self.assertEqual(values["TRANSITION_RECEIPT_HASH"], "a" * 64)
        self.assertEqual(values["REPLAY_REFERENCE"], manifest_receipt_id)
        self.assertEqual(values["RECONSTRUCTION_REFERENCE"], manifest_receipt_id)
        self.assertEqual(values["PORTABLE_REPLAY_REFERENCE"], _portable_replay_reference(manifest_receipt_id))
        self.assertEqual(
            values["PORTABLE_REPLAY_REFERENCE"],
            f"stegverse-replay:v1:{manifest_receipt_id}:{EXPECTED_MANIFEST_SHA256}",
        )


if __name__ == "__main__":
    unittest.main()
