"""0A and 0B converge on one manifest-route-selected entrypoint (SDK#368 PR-2)."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import stegverse.manifest_builder as manifest_builder
from stegverse.cli import CANONICAL_MANIFEST_ENTRYPOINT, RESULT_RETURN_ENTRYPOINT, main
from stegverse.github_repository_fetcher import GitHubRepositoryFetcherError
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_state_transition_runtime import (
    RESULT_SCHEMA,
    UNIVERSAL_RUNTIME_BINDING,
    derive_execution_request,
    validate_runtime_result,
)
from stegverse.route_resolution import CANONICAL_PRODUCTION_ROUTE_ID, CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID
from tests.test_manifest_destination_binding import ORGANIZATION_BOUNDARY
from tests.test_organization_batch_manifest_task_binding import (
    TASK_ID,
    canonical_request,
    fixture as governance_manifest,
    governance_request,
)

BOUNDARY = "stegverse.manifest_execution._canonical_organization_boundary"


def _last_json(text):
    """The CLI prints guidance first; its JSON result is the last top-level object."""
    index = text.rfind("\n{\n")
    return json.loads(text[index + 1:] if index >= 0 else text)


def _no_local_lane(*_args, **_kwargs):
    raise AssertionError("local enclosed lifecycle must not be reachable from 0A/0B")


class ConvergenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        guards = [
            patch("stegverse.governance_ingress_runtime.run_external_manifest", side_effect=_no_local_lane),
            patch("stegverse.sovereign_validation_runtime.run_sovereign_validation", side_effect=_no_local_lane),
            # No receiver wait and no liveness probe: any outbound socket use fails the test.
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

    def _run(self, argv, boundary=ORGANIZATION_BOUNDARY):
        out = io.StringIO()
        kwargs = {"side_effect": boundary} if isinstance(boundary, BaseException) else {"return_value": boundary}
        with patch(BOUNDARY, **kwargs) as fetched, contextlib.redirect_stdout(out):
            rc = main(argv)
        text = out.getvalue()
        return rc, _last_json(text), fetched

    def _0a_args(self):
        payload = canonical_request()
        return [
            "governance", "--select", "0A",
            "--input", self._write("data.json", payload),
            "--processor-request", self._write("request.json", governance_request(payload)),
            "--source-framework", "StegVerse-Labs/.github",
            "--source-output-id", payload["request_id"],
        ]

    def _ready_0a_args(self):
        """0A dispatches only a READY draft (SDK#368 readiness gate)."""
        from datetime import datetime, timedelta, timezone
        from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready

        payload = canonical_request()
        draft = manifest_builder.build_manifest(
            data=payload, source_framework="StegVerse-Labs/.github", source_output_id=payload["request_id"],
            processor_request=governance_request(payload), process="governance",
        )
        evidence = _all_ready(draft, at=datetime.now(timezone.utc) - timedelta(seconds=5))
        return self._0a_args() + [
            "--attempt-id", ATTEMPT,
            "--readiness-evidence", self._write("evidence.json", evidence),
            "--readiness-keys", self._write("keys.json", {KEY_ID: KEY}),
        ]

    def _ready_0b_args(self, manifest, name="m.json"):
        """A supplied 0B manifest requires fresh, invocation-bound readiness too."""
        from datetime import datetime, timedelta, timezone
        from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready

        evidence = _all_ready(manifest, at=datetime.now(timezone.utc) - timedelta(seconds=5))
        return [
            "governance", "--select", "0B", "--manifest", self._write(name, manifest),
            "--attempt-id", ATTEMPT,
            "--readiness-evidence", self._write(name + ".evidence", evidence),
            "--readiness-keys", self._write(name + ".keys", {KEY_ID: KEY}),
        ]

    def test_0b_without_readiness_refuses_before_organization_handoff(self):
        manifest = governance_manifest()
        rc, output, fetched = self._run([
            "governance", "--select", "0B", "--manifest", self._write("no-ready.json", manifest)
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertEqual(output["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
        self.assertIs(output["executable"], False)
        fetched.assert_not_called()

    def test_0b_handoff_bound_to_same_manifest_digest_and_route(self):
        manifest = governance_manifest()
        rc, output, fetched = self._run(self._ready_0b_args(manifest))
        self.assertEqual(rc, 0)
        digest = validate_ingress_manifest(manifest)["canonical_manifest_sha256"]
        result = output["result"]
        self.assertEqual(output["selection"], "0B")
        self.assertEqual(output["manifest_preparation"], "SUPPLIED_MANIFEST_VALIDATED_WITHOUT_REBUILD")
        self.assertNotIn("manifest", output)
        self.assertEqual(output["canonical_entrypoint"], CANONICAL_MANIFEST_ENTRYPOINT)
        self.assertEqual(output["result_return_entrypoint"], RESULT_RETURN_ENTRYPOINT)
        self.assertEqual(result["return_entrypoint"], RESULT_RETURN_ENTRYPOINT)
        self.assertEqual(result["state"], "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF")
        self.assertEqual(output["canonical_manifest_sha256"], digest)
        self.assertEqual(result["canonical_manifest_sha256"], digest)
        self.assertEqual(result["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)
        self.assertEqual(output["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)
        self.assertEqual(output["runtime_binding"], UNIVERSAL_RUNTIME_BINDING)
        self.assertEqual(result["wire_manifest_sha256"], derive_execution_request(manifest)["wire_manifest_sha256"])
        fetched.assert_called_once()

    def test_0a_builder_digest_is_preserved_into_handoff(self):
        built = []
        real = manifest_builder.build_manifest

        def capture(**kwargs):
            built.append(real(**kwargs))
            return copy.deepcopy(built[-1])

        args = self._ready_0a_args()
        with patch("stegverse.manifest_builder.build_manifest", side_effect=capture) as builder:
            rc, output, _ = self._run(args)
        self.assertEqual(rc, 0)
        builder.assert_called_once()
        self.assertEqual(builder.call_args.kwargs["process"], "governance")
        digest = validate_ingress_manifest(built[0])["canonical_manifest_sha256"]
        self.assertEqual(output["manifest_preparation"], "SDK_MANIFEST_BUILDER")
        self.assertEqual(output["manifest"], built[0])
        self.assertEqual(output["canonical_manifest_sha256"], digest)
        self.assertEqual(output["result"]["canonical_manifest_sha256"], digest)
        self.assertEqual(output["result"]["manifest_lineage"]["canonical_manifest_sha256"], digest)
        self.assertEqual(output["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)

    def test_0a_without_processor_request_fails_closed_before_dispatch(self):
        args = [arg for arg in self._0a_args()]
        index = args.index("--processor-request")
        del args[index:index + 2]
        rc, output, fetched = self._run(args)
        self.assertEqual(rc, 2)
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertEqual(output["failed_predicate"], "MANIFEST_BUILDER_PROCESSOR_REQUEST_REQUIRED")
        fetched.assert_not_called()

    def test_console_mode_cannot_select_a_different_runtime(self):
        _, built, _ = self._run(self._ready_0a_args())
        _, supplied, _ = self._run(self._ready_0b_args(built["manifest"], "built.json"))
        self.assertEqual(built["runtime_binding"], supplied["runtime_binding"])
        self.assertEqual(built["route_id"], supplied["route_id"])
        self.assertEqual(built["canonical_manifest_sha256"], supplied["canonical_manifest_sha256"])
        for output in (built, supplied):
            self.assertEqual(output["runtime_selected_by"], "MANIFEST_ROUTE_RUNTIME_BINDING")
            self.assertIs(output["console_selection_selects_runtime"], False)

        # A manifest declaring another published route runs that route's binding
        # (here it refuses without host bindings); 0B does not swap it for the
        # canonical handoff or the local lifecycle.
        payload = canonical_request()
        local = manifest_builder.build_manifest(
            data=payload, source_framework="fixture", source_output_id="local-route",
            processor_request=governance_request(payload), process="governance",
            execution_profile=manifest_builder.LOCAL_CONFORMANCE,
        )
        self.assertEqual(local["processing"]["route_id"], CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID)
        rc, output, fetched = self._run(self._ready_0b_args(local, "local.json"))
        self.assertEqual(rc, 2)
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertEqual(output["failed_predicate"], "CUSTOMER_LOCAL_HOST_BINDINGS_REQUIRED")
        fetched.assert_not_called()

    def test_missing_organization_boundary_fails_closed(self):
        manifest = governance_manifest()
        rc, output, _ = self._run(
            self._ready_0b_args(manifest),
            boundary=GitHubRepositoryFetcherError("source unavailable"),
        )
        self.assertEqual(rc, 2)
        result = output["result"]
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "CANONICAL_ORGANIZATION_INGRESS_ENDPOINT_NOT_RESOLVED")
        self.assertEqual(output["failed_predicate"], result["failed_predicate"])
        self.assertIn("source unavailable", result["canonical_organization_boundary_unavailable"])
        self.assertIs(result["receiver_availability_consulted"], False)
        self.assertIs(result["external_machine_required"], False)
        self.assertEqual(result["canonical_manifest_sha256"], validate_ingress_manifest(manifest)["canonical_manifest_sha256"])

    def test_handoff_performs_no_receiver_wait_or_probe(self):
        _, output, _ = self._run(self._ready_0b_args(governance_manifest()))
        result = output["result"]
        for key in ("receiver_contacted", "receiver_availability_required", "awaits_external_machine",
                    "transport_performed_by_sdk", "intr_admission_observed", "consequence_committed"):
            self.assertIs(result[key], False, key)

    def test_invalid_manifest_fails_closed_with_predicate(self):
        rc, output, fetched = self._run(["governance", "--select", "0B", "--manifest", self._write("bad.json", {"manifest_profile": "x"})])
        self.assertEqual(rc, 2)
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertTrue(output["failed_predicate"])
        fetched.assert_not_called()


class LocalEnclosedResultTests(unittest.TestCase):
    def setUp(self):
        self.manifest = governance_manifest()
        self.request = derive_execution_request(self.manifest, ORGANIZATION_BOUNDARY)
        self.assertEqual(self.request["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)

    def test_local_enclosed_result_is_rejected_for_canonical_governed_route(self):
        local = {
            "manifest_receipt_id": "MR-" + "A" * 64,
            "governance_state": "ALLOW",
            "master_records_organization_record_status": "RECORDED",
            "lane": "SDK_LOCAL_ENCLOSED_VALIDATION",
            "may_be_promoted_to_canonical_closure": False,
        }
        with self.assertRaisesRegex(ValueError, "UNIVERSAL_INTR_RESULT_SCHEMA_MISMATCH"):
            validate_runtime_result(local, self.request)

    def test_local_custody_result_dressed_as_runtime_result_is_rejected(self):
        dressed = {
            "schema": RESULT_SCHEMA,
            "state": "COMPLETE",
            "disposition": "ALLOW",
            "terminal": False,
            "communication_terminal": False,
            "canonical_task_id": TASK_ID,
            "processing_capability": "governance",
            "route_id": self.request["route_id"],
            "graph_id": self.request["graph_id"],
            "request_sha256": self.request["request_sha256"],
            "wire_manifest_sha256": self.request["wire_manifest_sha256"],
            "canonical_manifest_sha256": self.request["canonical_manifest_sha256"],
            "manifest_receipt_id": "MR-" + "A" * 64,
            "custody_store_is_local": True,
        }
        with self.assertRaisesRegex(ValueError, "GOVERNANCE_RESULT_ORGANIZATION_RECORDS_REQUIRED"):
            validate_runtime_result(dressed, self.request)


class LocalOptionLabelTests(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = main(argv)
        text = out.getvalue()
        return rc, _last_json(text)

    def test_replay_and_reconstruct_are_labelled_local_and_non_canonical(self):
        from unittest.mock import Mock
        operations = Mock()
        operations.replay.return_value = {"manifest_receipt_id": "MR-A", "replay_disposition": "DENY"}
        operations.reconstruct.return_value = {"manifest_receipt_id": "MR-A", "consequence_reexecuted": False}
        with patch("stegverse.cli._local_enclosed_operations", return_value=operations):
            for select, operation in (("1", "replay"), ("2", "reconstruct")):
                rc, output = self._run(["governance", "--select", select, "--manifest-receipt-id", "MR-A"])
                self.assertEqual(rc, 0)
                self.assertEqual(output["local_operation"], operation)
                lane = output["sdk_execution_lane"]
                self.assertEqual(lane["lane"], "SDK_LOCAL_ENCLOSED_VALIDATION")
                self.assertIs(lane["canonical"], False)
                self.assertIs(lane["authorizing"], False)
                self.assertIs(lane["may_be_promoted_to_canonical_closure"], False)
                self.assertEqual(output["result"]["manifest_receipt_id"], "MR-A")

    def test_fallback_is_labelled_local_and_non_canonical(self):
        with patch("stegverse.governance_fallback.execute_fallback", return_value={"governance_state": "REVIEW"}):
            rc, output = self._run(["governance", "--fallback-operation", "run", "--fallback-target", "request.json"])
        self.assertEqual(rc, 0)
        self.assertEqual(output["result"], {"governance_state": "REVIEW"})
        self.assertEqual(output["sdk_execution_lane"]["lane"], "SDK_LOCAL_ENCLOSED_VALIDATION")
        self.assertIs(output["sdk_execution_lane"]["canonical"], False)


if __name__ == "__main__":
    unittest.main()
