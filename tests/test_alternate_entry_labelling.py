"""Alternate module entries cannot bypass the canonical manifest entrypoint unlabelled (SDK#368).

Two secondary CLIs sat beside ``stegverse governance``:

* ``python -m stegverse.governance_ingress_cli 0B`` ran the local sovereign lane
  without readiness qualification and printed the result unlabelled.
* ``stegverse-diagnostic`` hardwired the diagnostic runtime, bypassing the
  route's published ``runtime_binding``, and printed the result unlabelled.

The first now refuses 0B and points at the canonical console entry; the second
carries the same explicit local-lane label as options 1/2 and the fallback.
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stegverse import ecosystem_diagnostic_cli, governance_ingress_cli
from stegverse.cli import CANONICAL_MANIFEST_ENTRYPOINT, LOCAL_ENCLOSED_LANE
from stegverse.ecosystem_diagnostic_runtime import execute_manifest as run_diagnostic
from stegverse.manifest_builder import build_manifest
from tests.test_ecosystem_diagnostic_processor import diagnostic_request
from tests.test_organization_batch_manifest_task_binding import fixture as governance_manifest


def _no_local_lane(*_args, **_kwargs):
    raise AssertionError("local sovereign lane must not be reachable from the module 0B entry")


def _run(main, argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = main(argv)
    return rc, json.loads(out.getvalue())


class GovernanceIngressModuleEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.manifest_path = str(Path(self.tmp.name) / "manifest.json")
        Path(self.manifest_path).write_text(json.dumps(governance_manifest()), encoding="utf-8")
        for guard in (
            patch("stegverse.governance_ingress_runtime.run_external_manifest", side_effect=_no_local_lane),
            patch("stegverse.sovereign_validation_runtime.run_sovereign_validation", side_effect=_no_local_lane),
        ):
            guard.start()
            self.addCleanup(guard.stop)

    def test_explicit_0b_is_refused_with_six_field_pointer_to_canonical_entry(self):
        for spelling in ("0B", "0b"):
            with self.subTest(option=spelling):
                rc, output = _run(governance_ingress_cli.main, [spelling, self.manifest_path])
                self.assertEqual(rc, 2)
                self.assertEqual(len(output), 6, output)
                self.assertEqual(output["status"], "REFUSED")
                self.assertEqual(output["failed_predicate"], "NON_CONVERGENT_0B_MODULE_ENTRY")
                self.assertEqual(output["canonical_entrypoint"], CANONICAL_MANIFEST_ENTRYPOINT)
                self.assertTrue(output["canonical_entry"].startswith("stegverse governance --select 0B --manifest"))
                self.assertEqual(output["authority_effect"], "NONE")
                self.assertIn("run_external_manifest", output["error"])

    def test_0b_is_refused_before_the_manifest_is_read_or_options_parsed(self):
        # No manifest operand, custody flags first: still the structured refusal,
        # never an argparse usage error and never a lane invocation.
        rc, output = _run(governance_ingress_cli.main, ["--records-db", "x.db", "0B"])
        self.assertEqual(rc, 2)
        self.assertEqual(output["failed_predicate"], "NON_CONVERGENT_0B_MODULE_ENTRY")
        rc, output = _run(governance_ingress_cli.main, ["0B", "/nonexistent/manifest.json"])
        self.assertEqual(rc, 2)
        self.assertEqual(output["failed_predicate"], "NON_CONVERGENT_0B_MODULE_ENTRY")

    def test_0b_is_not_an_advertised_choice(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as stop:
            governance_ingress_cli.main(["--help"])
        self.assertEqual(stop.exception.code, 0)
        text = out.getvalue()
        usage, _, rest = text.partition("\n\n")
        self.assertIn("{000}", usage)
        self.assertNotIn("0B", usage)
        # The only mention of 0B is the pointer to the canonical console entry.
        self.assertNotIn("0B", rest.split("positional arguments:", 1)[1])
        self.assertNotIn("0b", text)
        self.assertIn("stegverse governance --select 0B", rest)

    def test_000_contract_is_unchanged(self):
        with patch("stegverse.governance_ingress_cli.run_000_demo", return_value={"demo": True}) as demo:
            rc, output = _run(governance_ingress_cli.main, ["000", "--records-db", "x.db"])
        self.assertEqual(rc, 0)
        self.assertEqual(output, {"demo": True})
        demo.assert_called_once_with(custody_db="x.db", host_identity="stegverse-sovereign-local")
        rc, output = _run(governance_ingress_cli.main, ["000", self.manifest_path])
        self.assertEqual(rc, 2)
        self.assertEqual(output["status"], "INVALID_REQUEST")


class EcosystemDiagnosticCliLabelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.manifest = build_manifest(
            data={"source": "none"},
            source_framework="fixture",
            source_output_id="cli-label",
            processor_request=diagnostic_request(observation=None),
            process="ecosystem_diagnostic",
            created_at="2026-09-12T03:30:00Z",
        )
        self.manifest_path = str(Path(self.tmp.name) / "diag.json")
        Path(self.manifest_path).write_text(json.dumps(self.manifest), encoding="utf-8")

    def _assert_labelled(self, output):
        lane = output["sdk_execution_lane"]
        self.assertEqual(lane, LOCAL_ENCLOSED_LANE)
        self.assertEqual(lane["lane"], "SDK_LOCAL_ENCLOSED_VALIDATION")
        self.assertIs(lane["canonical"], False)
        self.assertIs(lane["authorizing"], False)
        self.assertIs(lane["selected_by_manifest_route"], False)
        self.assertEqual(output["canonical_entrypoint"], CANONICAL_MANIFEST_ENTRYPOINT)
        self.assertEqual(output["local_operation"], "ecosystem_diagnostic")
        result = output["result"]
        self.assertEqual(result["authority_effect"], "NONE_DIAGNOSTIC_ONLY")
        self.assertFalse(result["mutation_performed"])
        self.assertEqual(result["results"][0]["observation_state"], "NOT_OBSERVED")
        return result

    def test_stdout_result_is_labelled_local_and_non_canonical(self):
        rc, output = _run(ecosystem_diagnostic_cli.main, ["--manifest", self.manifest_path])
        self.assertEqual(rc, 0)
        result = self._assert_labelled(output)
        # The processor's own result is carried through unchanged, not re-shaped.
        direct = run_diagnostic(self.manifest)
        self.assertEqual(result["results"], direct["results"])
        self.assertEqual(result["result_binding_hash"], direct["result_binding_hash"])

    def test_output_file_carries_the_same_label(self):
        target = Path(self.tmp.name) / "out.json"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = ecosystem_diagnostic_cli.main(["--manifest", self.manifest_path, "--output", str(target)])
        self.assertEqual(rc, 0)
        self.assertEqual(out.getvalue(), "")
        self._assert_labelled(json.loads(target.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
