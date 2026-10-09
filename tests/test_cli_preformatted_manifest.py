from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stegverse.cli import main
from tests.test_organization_batch_manifest_task_binding import fixture


HANDOFF = {
    "disposition": "ALLOW",
    "state": "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF",
    "manifest_lineage": {"run_manifest_request": {
        "route_id": "stegverse.route.canonical-governed.v1",
        "runtime_binding": "stegverse.manifest_state_transition_runtime.execute_manifest",
    }},
}

READY = {"state": "READY", "executable": True, "qualification": {"qualification": "READY"}}


class Tests(unittest.TestCase):
    # SDK#368: 0B no longer runs the local governance lifecycle. The supplied
    # manifest goes, without rebuild, to the canonical manifest-route-selected
    # entrypoint stegverse.manifest_execution.execute_manifest.
    def test_primary_cli_executes_0b_with_supplied_manifest(self):
        manifest = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with patch("stegverse.manifest_execution.execute_manifest", return_value=HANDOFF) as run, \
                    patch("stegverse.governance_ingress_runtime.run_external_manifest") as local, \
                    contextlib.redirect_stdout(io.StringIO()):
                rc = main([
                    "governance",
                    "--select", "0B",
                    "--manifest", str(path),
                    "--custody-db", ":memory:",
                    "--host-identity", "fixture-host",
                ])

        self.assertEqual(0, rc)
        run.assert_called_once_with(manifest)
        local.assert_not_called()

    def test_primary_cli_keeps_0_as_neutral_submission_selector(self):
        rc = main(["governance", "--select", "0"])
        self.assertEqual(0, rc)

    # SDK#368: 0A raw data passes through the SDK Manifest Builder, then the
    # same canonical entrypoint as 0B.
    def test_primary_cli_accepts_explicit_0a_selector(self):
        manifest = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data.json"
            data.write_text(json.dumps({"request_id": "fixture"}), encoding="utf-8")
            request = Path(tmp) / "request.json"
            request.write_text(json.dumps({"candidate": {}}), encoding="utf-8")
            with patch("stegverse.manifest_builder.build_manifest", return_value=manifest) as build, \
                    patch("stegverse.manifest_execution.execute_manifest", return_value=HANDOFF) as run, \
                    patch("stegverse.manifest_builder.qualify_draft_manifest", return_value=READY) as qualify, \
                    patch("stegverse.manifest_plan.require_ready_qualification") as require, \
                    contextlib.redirect_stdout(io.StringIO()):
                rc = main(["governance", "--select", "0A", "--input", str(data), "--processor-request", str(request)])
        self.assertEqual(0, rc)
        build.assert_called_once()
        self.assertEqual({"request_id": "fixture"}, build.call_args.kwargs["data"])
        self.assertEqual({"candidate": {}}, build.call_args.kwargs["processor_request"])
        # SDK#368: the built draft is qualified before the canonical entrypoint.
        self.assertIs(qualify.call_args.args[0], manifest)
        require.assert_called_once_with(manifest, READY["qualification"])
        run.assert_called_once_with(manifest)


if __name__ == "__main__":
    unittest.main()
