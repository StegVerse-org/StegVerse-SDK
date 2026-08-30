import hashlib
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


def canonical_sha256(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class CrossFrameworkResultPackagingTests(unittest.TestCase):
    def make_result(self, root: Path):
        receipt_hash = "a" * 64
        manifest_receipt_id = "MR-CURRENT-BASIS-001"
        portable_reference = f"stegverse-replay:v1:{manifest_receipt_id}:{EXPECTED_MANIFEST_SHA256}"
        values = {
            "RUN_COMPLETE.json": {
                "schema": "stegverse.sdk.cross-framework-run-complete.v1",
                "status": "COMPLETE",
                "manifest_sha256": EXPECTED_MANIFEST_SHA256,
                "manifest_git_blob_sha1": EXPECTED_MANIFEST_BLOB_SHA1,
                "manifest_receipt_id": manifest_receipt_id,
                "portable_replay_reference": portable_reference,
                "replay_reference_artifact": "REPLAY_REFERENCE.txt",
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
                "transition_id": "DELTA-S0-S1",
                "receipt_hash": receipt_hash,
            },
            "REPLAY.json": {"operation_transition_custody_status": "RECORDED"},
            "RECONSTRUCTION.json": {"operation_transition_custody_status": "RECORDED"},
        }
        root.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (root / name).write_text(json.dumps(value) + "\n", encoding="utf-8")
        (root / "REPLAY_REFERENCE.txt").write_text(
            "\n".join(
                (
                    "TEST_ID=cross-framework-current-basis-001",
                    f"MANIFEST_RECEIPT_ID={manifest_receipt_id}",
                    f"MANIFEST_SHA256={EXPECTED_MANIFEST_SHA256}",
                    f"MANIFEST_GIT_BLOB_SHA1={EXPECTED_MANIFEST_BLOB_SHA1}",
                    "TRANSITION_ID=DELTA-S0-S1",
                    f"TRANSITION_RECEIPT_HASH={receipt_hash}",
                    f"STEGVERSE_RESULT_SHA256={canonical_sha256(values['STEGVERSE_RESULT.json'])}",
                    f"PORTABLE_REPLAY_REFERENCE={portable_reference}",
                    f"REPLAY_REFERENCE={manifest_receipt_id}",
                    f"RECONSTRUCTION_REFERENCE={manifest_receipt_id}",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        return values

    def test_complete_packet_is_packaged(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            self.make_result(result)
            index = package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)
            self.assertEqual(index["frozen_manifest_sha256"], EXPECTED_MANIFEST_SHA256)
            self.assertEqual(index["manifest_receipt_id"], "MR-CURRENT-BASIS-001")
            self.assertEqual(
                index["portable_replay_reference"],
                f"stegverse-replay:v1:MR-CURRENT-BASIS-001:{EXPECTED_MANIFEST_SHA256}",
            )
            self.assertEqual(index["copy_paste_reference_artifact"], "run-evidence/REPLAY_REFERENCE.txt")
            self.assertEqual(index["publication_role"], "HOST_NEUTRAL_VERIFIED_RESULT_PACKET")
            self.assertTrue(index["stegverse_native_retention_required"])
            self.assertFalse(index["third_party_distribution_required"])
            self.assertTrue(index["github_actions_distribution_optional"])
            self.assertTrue((output / "RESULT_PACKET_INDEX.json").is_file())
            self.assertTrue((output / "run-evidence/RUN_COMPLETE.json").is_file())
            self.assertTrue((output / "run-evidence/REPLAY_REFERENCE.txt").is_file())

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

    def test_missing_replay_reference_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            self.make_result(result)
            (result / "REPLAY_REFERENCE.txt").unlink()
            with self.assertRaisesRegex(RuntimeError, "missing required authentic evidence"):
                package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)

    def test_tampered_replay_reference_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            self.make_result(result)
            text = (result / "REPLAY_REFERENCE.txt").read_text(encoding="utf-8")
            (result / "REPLAY_REFERENCE.txt").write_text(
                text.replace("MANIFEST_RECEIPT_ID=MR-CURRENT-BASIS-001", "MANIFEST_RECEIPT_ID=MR-TAMPERED"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "MANIFEST_RECEIPT_ID"):
                package_results(result_dir=result, manifest_path=MANIFEST, output_dir=output)

    def test_tampered_result_hash_rejects_publication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            result = base / "result"
            output = base / "packet"
            self.make_result(result)
            text = (result / "REPLAY_REFERENCE.txt").read_text(encoding="utf-8")
            start = "STEGVERSE_RESULT_SHA256="
            lines = [
                start + ("c" * 64) if line.startswith(start) else line
                for line in text.splitlines()
            ]
            (result / "REPLAY_REFERENCE.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "STEGVERSE_RESULT_SHA256"):
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
