import json
import tempfile
import unittest
from pathlib import Path

from scripts.package_cross_framework_current_basis_results import (
    EXPECTED_MANIFEST_BLOB_SHA1,
    EXPECTED_MANIFEST_SHA256,
    package_results,
)

MANIFEST = Path("inspection/examples/cross-framework-current-basis-request.draft.json")


class CrossFrameworkResultPackagingTests(unittest.TestCase):
    def make_result(self, root: Path):
        receipt_hash = "a" * 64
        manifest_receipt_id = "MR-CURRENT-BASIS-001"
        values = {
            "RUN_COMPLETE.json": {
                "schema": "stegverse.sdk.cross-framework-run-complete.v1",
                "status": "COMPLETE",
                "manifest_sha256": EXPECTED_MANIFEST_SHA256,
                "manifest_git_blob_sha1": EXPECTED_MANIFEST_BLOB_SHA1,
                "manifest_receipt_id": manifest_receipt_id,
                "independent_execution_complete": True,
                "counterpart_result_consumed_before_completion": False,
                "s1_observed": True,
                "transition_receipt_bound": True,
                "transition_receipt_hash": receipt_hash,
                "custody_recorded": True,
                "replay_recorded": True,
                "reconstruction_recorded": True,
                "external_side_effect": False,
                "github_actions_runtime_authority": False,
            },
            "STEGVERSE_RESULT.json": {
                "manifest_receipt_id": manifest_receipt_id,
                "master_records_custody_status": "RECORDED",
                "external_side_effect": False,
            },
            "S1_OBSERVATION.json": {
                "manifest_sha256": EXPECTED_MANIFEST_SHA256,
                "s1_observed": True,
                "counterpart_result_consumed_before_completion": False,
            },
            "S0_S1_TRANSITION_RECEIPT.json": {
                "manifest_sha256": EXPECTED_MANIFEST_SHA256,
                "receipt_timing": "POST_OBSERVATION",
                "receipt_hash": receipt_hash,
            },
            "REPLAY.json": {"operation_transition_custody_status": "RECORDED"},
            "RECONSTRUCTION.json": {"operation_transition_custody_status": "RECORDED"},
        }
        root.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (root / name).write_text(json.dumps(value) + "\n", encoding="utf-8")
        return values

    def test_complete_packet_is_packaged(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            self.make_result(result)
            index = package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)
            self.assertEqual(index["frozen_manifest_sha256"], EXPECTED_MANIFEST_SHA256)
            self.assertTrue((output / "RESULT_PACKET_INDEX.json").is_file())
            self.assertTrue((output / "run-evidence/RUN_COMPLETE.json").is_file())

    def test_external_side_effect_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            values = self.make_result(result)
            values["RUN_COMPLETE.json"]["external_side_effect"] = True
            (result / "RUN_COMPLETE.json").write_text(json.dumps(values["RUN_COMPLETE.json"]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "external_side_effect"):
                package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)

    def test_counterpart_consumption_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            values = self.make_result(result)
            values["RUN_COMPLETE.json"]["counterpart_result_consumed_before_completion"] = True
            (result / "RUN_COMPLETE.json").write_text(json.dumps(values["RUN_COMPLETE.json"]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "counterpart_result_consumed_before_completion"):
                package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)

    def test_missing_evidence_file_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            self.make_result(result)
            (result / "RECONSTRUCTION.json").unlink()
            with self.assertRaisesRegex(RuntimeError, "missing required authentic evidence"):
                package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)

    def test_pre_observation_transition_receipt_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            values = self.make_result(result)
            values["S0_S1_TRANSITION_RECEIPT.json"]["receipt_timing"] = "PRE_EXECUTION"
            (result / "S0_S1_TRANSITION_RECEIPT.json").write_text(
                json.dumps(values["S0_S1_TRANSITION_RECEIPT.json"]) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "post-observation"):
                package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)


if __name__ == "__main__":
    unittest.main()
