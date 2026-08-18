from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stegverse.cli import main


class Tests(unittest.TestCase):
    def test_primary_cli_executes_0b_with_supplied_manifest(self):
        manifest = {
            "manifest_profile": "stegverse.ingress-manifest.v1",
            "manifest_profile_version": "1",
            "source_framework": "fixture-framework",
            "source_output_id": "fixture-output",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with patch("stegverse.governance_ingress_runtime.run_external_manifest") as run:
                run.return_value = {
                    "manifest_receipt_id": "MR-" + "A" * 64,
                    "governance_state": "ALLOW",
                    "master_records_custody_status": "RECORDED",
                }
                rc = main([
                    "governance",
                    "--select", "0B",
                    "--manifest", str(path),
                    "--custody-db", ":memory:",
                    "--host-identity", "fixture-host",
                ])

        self.assertEqual(0, rc)
        run.assert_called_once()
        args, kwargs = run.call_args
        self.assertEqual(manifest, args[0])
        self.assertEqual(":memory:", kwargs["custody_db"])
        self.assertEqual("fixture-host", kwargs["host_identity"])

    def test_primary_cli_keeps_0_as_neutral_submission_selector(self):
        rc = main(["governance", "--select", "0"])
        self.assertEqual(0, rc)

    def test_primary_cli_accepts_explicit_0a_selector(self):
        with patch("stegverse.public_inspection.load_public_inspection_request") as load:
            with patch("stegverse.sovereign_validation_runtime.run_sovereign_validation") as run:
                load.return_value = {"request_id": "fixture"}
                run.return_value = {"manifest_receipt_id": "MR-" + "B" * 64}
                rc = main(["governance", "--select", "0A", "--input", "fixture.json"])
        self.assertEqual(0, rc)
        load.assert_called_once_with("fixture.json")
        run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
