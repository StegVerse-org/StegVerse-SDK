"""SDK#368: the readiness gate guards every CLI dispatch path, not only 0A/0B.

``stegverse run-manifest`` and ``stegverse external-run`` (and the programmatic
``manifest_external_framework_submission``) previously handed a schema-valid
manifest to an ALLOW handoff with no readiness qualification. A schema-valid
manifest must never be described as runnable without sufficient invocation-bound
evidence. These are source tests over caller-supplied evidence fixtures; they
claim no runtime observation.
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from stegverse import external_framework_runner, manifest_execution
from stegverse.capability_inventory import hmac_evidence_verifier
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_plan import QUALIFIED_READY
from tests.test_manifest_builder import governance_request
from tests.test_manifest_destination_binding import ORGANIZATION_BOUNDARY
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready

BOUNDARY = "stegverse.manifest_execution._canonical_organization_boundary"
HANDOFF_STATE = "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF"

SUBMISSION = dict(
    data={"relational_state": "ambiguous"},
    source_framework="probe_framework",
    source_output_id="probe-output-1",
    processor_request=governance_request(),
    created_at="2026-10-02T00:00:00Z",
)


def _fresh_evidence(manifest):
    return _all_ready(manifest, at=datetime.now(timezone.utc) - timedelta(seconds=5))


class _DispatchPathCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        guards = [
            patch("urllib.request.urlopen", side_effect=AssertionError("no receiver contact or probe")),
            patch("socket.create_connection", side_effect=AssertionError("no receiver contact or probe")),
        ]
        for guard in guards:
            guard.start()
            self.addCleanup(guard.stop)

    def _write(self, name, value):
        path = Path(self.tmp.name) / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return str(path)

    def _readiness_args(self, manifest):
        return [
            "--attempt-id", ATTEMPT,
            "--readiness-evidence", self._write("evidence.json", _fresh_evidence(manifest)),
            "--readiness-keys", self._write("keys.json", {KEY_ID: KEY}),
        ]


class RunManifestReadinessGateTests(_DispatchPathCase):
    """Path 1: ``stegverse run-manifest`` / ``python -m stegverse.manifest_execution``."""

    def _manifest(self):
        return external_framework_runner.prepare_external_framework_manifest(**SUBMISSION)

    def _run(self, argv):
        out = io.StringIO()
        output = Path(self.tmp.name) / "result.json"
        with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY) as fetched, contextlib.redirect_stdout(out):
            rc = manifest_execution.main(argv + ["--output", str(output)])
        return rc, json.loads(output.read_text(encoding="utf-8")), fetched

    def test_without_evidence_fails_closed_and_never_fetches_boundary(self):
        manifest = self._manifest()
        rc, output, fetched = self._run(["--manifest", self._write("m.json", manifest)])
        self.assertEqual(rc, 2)
        fetched.assert_not_called()
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertEqual(output["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
        self.assertIs(output["executable"], False)
        self.assertIs(output["draft_preserved"], True)
        self.assertEqual(output["evidence"]["qualification"], "NOT_READY")
        self.assertTrue(output["evidence"]["failing_nodes"])
        self.assertNotEqual(output.get("state"), HANDOFF_STATE)
        self.assertEqual(
            output["canonical_manifest_sha256"], validate_ingress_manifest(manifest)["canonical_manifest_sha256"]
        )

    def test_with_evidence_reaches_handoff_bound_to_same_digest(self):
        manifest = self._manifest()
        digest = validate_ingress_manifest(manifest)["canonical_manifest_sha256"]
        rc, output, fetched = self._run(["--manifest", self._write("m.json", manifest)] + self._readiness_args(manifest))
        self.assertEqual(rc, 0)
        fetched.assert_called_once()
        self.assertEqual(output["disposition"], "ALLOW")
        self.assertEqual(output["state"], HANDOFF_STATE)
        self.assertEqual(output["canonical_manifest_sha256"], digest)
        self.assertEqual(output["manifest_lineage"]["canonical_manifest_sha256"], digest)

    def test_evidence_without_trust_root_is_not_ready(self):
        manifest = self._manifest()
        argv = ["--manifest", self._write("m.json", manifest),
                "--readiness-evidence", self._write("e.json", _fresh_evidence(manifest)), "--attempt-id", ATTEMPT]
        rc, output, fetched = self._run(argv)
        self.assertEqual(rc, 2)
        fetched.assert_not_called()
        self.assertEqual({n["failed_predicate"] for n in output["evidence"]["failing_nodes"]}, {"EVIDENCE_AUTHENTICATED"})

    def test_gate_precedes_execute_manifest(self):
        manifest = self._manifest()
        events = []

        def require(m, q):
            events.append("require_ready")

        def execute(m, **kwargs):
            events.append("execute_manifest")
            return {"disposition": "ALLOW", "state": HANDOFF_STATE}

        with patch("stegverse.manifest_plan.require_ready_qualification", side_effect=require), \
                patch("stegverse.manifest_execution.execute_manifest", side_effect=execute):
            rc, _, _ = self._run(["--manifest", self._write("m.json", manifest)] + self._readiness_args(manifest))
        self.assertEqual(rc, 0)
        self.assertEqual(events, ["require_ready", "execute_manifest"])

    def test_library_execute_manifest_signature_is_unchanged(self):
        """Callers that already qualified keep calling execute_manifest as before."""
        parameters = inspect.signature(manifest_execution.execute_manifest).parameters
        self.assertEqual(list(parameters), ["manifest", "canonical_source_fetcher"])


class ExternalRunReadinessGateTests(_DispatchPathCase):
    """Path 2: ``stegverse external-run`` and ``manifest_external_framework_submission``."""

    def _cli_args(self):
        return [
            "--input", self._write("data.json", SUBMISSION["data"]),
            "--governance-request", self._write("request.json", SUBMISSION["processor_request"]),
            "--source-framework", SUBMISSION["source_framework"],
            "--source-output-id", SUBMISSION["source_output_id"],
            "--created-at", SUBMISSION["created_at"],
        ]

    def _run(self, argv):
        output = Path(self.tmp.name) / "submission.json"
        with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY) as fetched:
            rc = external_framework_runner.main(argv + ["--output", str(output)])
        return rc, json.loads(output.read_text(encoding="utf-8")), fetched

    def test_cli_without_evidence_fails_closed_and_never_fetches_boundary(self):
        rc, result, fetched = self._run(self._cli_args())
        self.assertEqual(rc, 2)
        fetched.assert_not_called()
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
        self.assertNotEqual(result["status"], "SUBMISSION_READY")
        self.assertIsNone(result["handoff"])
        self.assertIs(result["executable"], False)
        self.assertIs(result["draft_preserved"], True)
        self.assertIs(result["execution_performed"], False)
        # The draft is preserved for editing; it is not described as runnable.
        self.assertEqual(result["manifest"]["source_output_id"], SUBMISSION["source_output_id"])
        self.assertNotEqual(result["evidence_class"], "SDK_LOCAL_MANIFEST_HANDOFF")

    def test_cli_with_evidence_reaches_handoff_bound_to_same_digest(self):
        draft = external_framework_runner.prepare_external_framework_manifest(**SUBMISSION)
        digest = validate_ingress_manifest(draft)["canonical_manifest_sha256"]
        rc, result, fetched = self._run(self._cli_args() + self._readiness_args(draft))
        self.assertEqual(rc, 0)
        fetched.assert_called_once()
        self.assertEqual(result["status"], "SUBMISSION_READY")
        self.assertIs(result["executable"], True)
        self.assertEqual(result["readiness_qualification"]["qualification"], QUALIFIED_READY)
        self.assertIs(result["readiness_qualification"]["runtime_allow_claimed"], False)
        handoff = result["handoff"]
        self.assertEqual(handoff["state"], HANDOFF_STATE)
        self.assertEqual(handoff["disposition"], "ALLOW")
        self.assertEqual(handoff["canonical_manifest_sha256"], digest)
        self.assertEqual(validate_ingress_manifest(result["manifest"])["canonical_manifest_sha256"], digest)
        self.assertEqual(result["evidence_class"], "SDK_LOCAL_MANIFEST_HANDOFF")

    def test_programmatic_submission_requires_evidence(self):
        draft = external_framework_runner.prepare_external_framework_manifest(**SUBMISSION)
        with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY) as fetched:
            refused = external_framework_runner.manifest_external_framework_submission(**SUBMISSION)
            self.assertEqual(refused["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
            self.assertIsNone(refused["handoff"])
            fetched.assert_not_called()
            ready = external_framework_runner.manifest_external_framework_submission(
                **SUBMISSION,
                attempt_id=ATTEMPT,
                readiness_evidence=_fresh_evidence(draft),
                evidence_verifier=hmac_evidence_verifier({KEY_ID: KEY}),
            )
        fetched.assert_called_once()
        self.assertEqual(ready["status"], "SUBMISSION_READY")
        self.assertEqual(ready["handoff"]["state"], HANDOFF_STATE)
        self.assertEqual(ready["handoff"]["canonical_manifest_sha256"],
                         validate_ingress_manifest(draft)["canonical_manifest_sha256"])

    def test_gate_precedes_execute_manifest(self):
        draft = external_framework_runner.prepare_external_framework_manifest(**SUBMISSION)
        events = []

        def require(m, q):
            events.append("require_ready")

        def execute(m, **kwargs):
            events.append("execute_manifest")
            return {"disposition": "ALLOW", "state": HANDOFF_STATE, "destination": None}

        with patch("stegverse.manifest_plan.require_ready_qualification", side_effect=require), \
                patch("stegverse.manifest_execution.execute_manifest", side_effect=execute):
            rc, _, _ = self._run(self._cli_args() + self._readiness_args(draft))
        self.assertEqual(rc, 0)
        self.assertEqual(events, ["require_ready", "execute_manifest"])


if __name__ == "__main__":
    unittest.main()
