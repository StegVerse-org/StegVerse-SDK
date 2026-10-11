"""SDK#368: the readiness gate guards every manifest dispatch path, not only 0A/0B.

``stegverse run-manifest`` and ``stegverse external-run`` (and the programmatic
``manifest_external_framework_submission``) previously handed a schema-valid
manifest to an ALLOW handoff with no readiness qualification. ``stegverse ask``
(and the programmatic ``ask_governed_question`` behind the Chat entry) previously
leased and executed every branch of a schema-valid stegbrowser manifest with no
readiness qualification. A schema-valid manifest must never be described as
runnable without sufficient invocation-bound evidence. These are source tests
over caller-supplied evidence fixtures; they claim no runtime observation.

``ReadinessGateCensusTests`` pins the census of every call site in ``stegverse/``
and ``scripts/`` that dispatches an ingress manifest, so a new ungated path fails
here rather than shipping.
"""
from __future__ import annotations

import ast
import contextlib
import inspect
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from stegverse import cli, external_framework_runner, governed_llm_fan, manifest_execution
from stegverse.capability_inventory import hmac_evidence_verifier
from stegverse.ecosystem_chat_ask import ask_governed_question, build_ask_manifest, plan_ask_journey
from stegverse.ecosystem_chat_entry import ASK, SCHEMA as ENTRY_SCHEMA
from stegverse.ecosystem_chat_http import ECOSYSTEM_CHAT_PATH
from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_plan import QUALIFIED_READY
from tests.test_manifest_builder import governance_request
from tests.test_manifest_destination_binding import ORGANIZATION_BOUNDARY
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready

BOUNDARY = "stegverse.manifest_execution._canonical_organization_boundary"
HANDOFF_STATE = "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF"
REFUSAL_SCHEMA = "stegverse.sdk.run-manifest-readiness-refusal.v1"
REPO_ROOT = Path(__file__).resolve().parents[1]

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


ASK_QUESTION = "What does the readiness gate guard?"
ASK_CREATED_AT = "2026-10-02T00:00:00Z"
ASK_FAN = "FAN-READINESS"
ASK_ROUTES = [
    {"provider": "anthropic", "model": "claude", "secure_url": "https://a.example.test/chat"},
    {"provider": "openai", "model": "gpt", "secure_url": "https://b.example.test/chat"},
]
#: What run_governed_llm_fan returns when it is reached but no branch completes.
FAN_STUB = {
    "fan_journey_id": ASK_FAN, "branch_count": 2, "branches": [],
    "required_endpoint_receipts": 8, "observed_endpoint_receipts": 0,
    "complete": False, "fan_sha256": "sha256:" + "0" * 64,
    "failure": {"failure_code": "FIXTURE_FAN_NOT_RUN"},
}


def _no_branch(operation, lease):
    raise AssertionError("no branch may be leased or executed")


class AskReadinessGateTests(_DispatchPathCase):
    """Path 3: ``stegverse ask``, ``ask_governed_question`` and the Chat entry.

    The stegbrowser route declares external_consequence_enabled; every branch of
    the fan is an LLM interaction performed by the StegBrowser owner. Nothing may
    be leased or executed until the ask manifest qualifies READY.
    """

    def setUp(self):
        super().setUp()
        self.journey = plan_ask_journey(ASK_QUESTION, ASK_ROUTES, fan_journey_id=ASK_FAN)
        self.manifest = build_ask_manifest(ASK_QUESTION, self.journey, created_at=ASK_CREATED_AT)
        self.digest = validate_ingress_manifest(self.manifest)["canonical_manifest_sha256"]
        self.evidence = _fresh_evidence(self.manifest)
        self.verifier = hmac_evidence_verifier({KEY_ID: KEY})

    def _ready_kwargs(self):
        return dict(created_at=ASK_CREATED_AT, attempt_id=ATTEMPT,
                    readiness_evidence=self.evidence, evidence_verifier=self.verifier)

    def _fan_recorder(self, seen):
        def fan(manifest, **kwargs):
            seen.append(validate_ingress_manifest(manifest)["canonical_manifest_sha256"])
            return dict(FAN_STUB)
        return fan

    def _entry_body(self, **extra):
        return json.dumps({"schema": ENTRY_SCHEMA, "operation": ASK, "question": ASK_QUESTION,
                           "journey": self.journey, **extra})

    def _entry_readiness(self):
        return {"created_at": ASK_CREATED_AT, "attempt_id": ATTEMPT, "readiness_evidence": self.evidence}

    def _assert_refused(self, answer):
        self.assertEqual(answer["disposition"], "FAIL_CLOSED")
        self.assertEqual(answer["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
        self.assertIs(answer["executable"], False)
        self.assertIs(answer["dispatched"], False)
        self.assertIs(answer["fan_attempted"], False)
        self.assertIs(answer["draft_preserved"], True)
        self.assertIs(answer["governed_claim"], False)
        self.assertIsNone(answer["answer"])
        self.assertIsNone(answer["composite"])
        self.assertEqual(answer["readiness_refusal_schema"], REFUSAL_SCHEMA)
        self.assertEqual(answer["canonical_manifest_sha256"], self.digest)
        self.assertEqual(answer["evidence"]["qualification"], "NOT_READY")
        self.assertTrue(answer["evidence"]["failing_nodes"])

    def test_without_evidence_fails_closed_and_executes_no_branch(self):
        answer = ask_governed_question(ASK_QUESTION, self.journey, executor=_no_branch, created_at=ASK_CREATED_AT)
        self._assert_refused(answer)

    def test_with_evidence_reaches_the_fan_bound_to_same_digest(self):
        seen = []
        with patch("stegverse.ecosystem_chat_ask.run_governed_llm_fan", side_effect=self._fan_recorder(seen)):
            answer = ask_governed_question(ASK_QUESTION, self.journey, executor=_no_branch, **self._ready_kwargs())
        self.assertEqual(seen, [self.digest])
        self.assertIs(answer["fan_attempted"], True)
        self.assertIs(answer["executable"], True)
        self.assertEqual(answer["readiness_qualification"]["qualification"], QUALIFIED_READY)
        self.assertNotEqual(answer["disposition"], "FAIL_CLOSED")

    def test_evidence_without_trust_root_is_not_ready(self):
        kwargs = self._ready_kwargs()
        kwargs.pop("evidence_verifier")
        answer = ask_governed_question(ASK_QUESTION, self.journey, executor=_no_branch, **kwargs)
        self._assert_refused(answer)
        self.assertEqual({n["failed_predicate"] for n in answer["evidence"]["failing_nodes"]}, {"EVIDENCE_AUTHENTICATED"})

    def test_evidence_bound_to_another_draft_is_not_ready(self):
        """created_at is part of the digest the evidence is bound to; a different draft is a different manifest."""
        kwargs = self._ready_kwargs()
        kwargs["created_at"] = "2026-10-03T00:00:00Z"
        answer = ask_governed_question(ASK_QUESTION, self.journey, executor=_no_branch, **kwargs)
        self.assertEqual(answer["disposition"], "FAIL_CLOSED")
        self.assertIs(answer["fan_attempted"], False)

    def test_gate_precedes_run_governed_llm_fan(self):
        events = []

        def require(m, q):
            events.append("require_ready")

        def fan(m, **kwargs):
            events.append("run_governed_llm_fan")
            return dict(FAN_STUB)

        with patch("stegverse.manifest_plan.require_ready_qualification", side_effect=require), \
                patch("stegverse.ecosystem_chat_ask.run_governed_llm_fan", side_effect=fan):
            ask_governed_question(ASK_QUESTION, self.journey, executor=_no_branch, **self._ready_kwargs())
        self.assertEqual(events, ["require_ready", "run_governed_llm_fan"])

    def test_library_run_governed_llm_fan_signature_is_unchanged(self):
        """Callers that already qualified keep calling the fan as before."""
        parameters = inspect.signature(governed_llm_fan.run_governed_llm_fan).parameters
        self.assertEqual(list(parameters), ["manifest", "executor", "requester", "lease_ttl_minutes"])

    def _console(self, argv):
        out = io.StringIO()
        with patch("stegverse.governed_llm_fan._resolve_executor",
                   side_effect=AssertionError("no executor may be resolved")), contextlib.redirect_stdout(out):
            rc = cli.main(["ask", "--question", ASK_QUESTION, "--routes", self._write("routes.json", ASK_ROUTES),
                           "--fan", ASK_FAN] + argv)
        return rc, json.loads(out.getvalue())

    def test_console_ask_without_evidence_fails_closed_with_rc_2(self):
        rc, output = self._console(["--created-at", ASK_CREATED_AT])
        self.assertEqual(rc, 2)
        self._assert_refused(output["answer"])
        self.assertEqual(output["summary"]["disposition"], "FAIL_CLOSED")
        self.assertIsNone(output["summary"]["answer"])

    def test_console_ask_with_evidence_reaches_the_fan(self):
        seen = []
        with patch("stegverse.ecosystem_chat_ask.run_governed_llm_fan", side_effect=self._fan_recorder(seen)):
            rc, output = self._console(["--created-at", ASK_CREATED_AT] + self._readiness_args(self.manifest))
        self.assertEqual(seen, [self.digest])
        self.assertNotEqual(rc, 2)
        self.assertIs(output["answer"]["fan_attempted"], True)
        self.assertEqual(output["answer"]["readiness_qualification"]["qualification"], QUALIFIED_READY)

    def test_console_plan_only_never_qualifies_or_dispatches(self):
        with patch("stegverse.manifest_execution.qualify_manifest_for_dispatch",
                   side_effect=AssertionError("planning is not dispatch")):
            rc, output = self._console(["--plan-only"])
        self.assertEqual(rc, 0)
        self.assertIn("journey", output)

    def test_chat_entry_without_host_trust_root_fails_closed_422(self):
        """Over bare HTTP the request's evidence cannot authenticate: nothing runs."""
        status, result = handle_ecosystem_chat_pipeline_http(
            "POST", ECOSYSTEM_CHAT_PATH, self._entry_body(**self._entry_readiness()), executor=_no_branch)
        self.assertEqual(status, 422)
        self.assertIs(result["served"], True)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
        self.assertIs(result["dispatched"], False)
        self.assertIs(result["draft_preserved"], True)
        self._assert_refused(result["answer"])

    def test_chat_entry_without_evidence_fails_closed_422(self):
        status, result = handle_ecosystem_chat_pipeline_http(
            "POST", ECOSYSTEM_CHAT_PATH, self._entry_body(created_at=ASK_CREATED_AT),
            executor=_no_branch, evidence_verifier=self.verifier)
        self.assertEqual(status, 422)
        self._assert_refused(result["answer"])

    def test_chat_entry_with_host_trust_root_and_evidence_reaches_the_fan(self):
        seen = []
        with patch("stegverse.ecosystem_chat_ask.run_governed_llm_fan", side_effect=self._fan_recorder(seen)):
            status, result = handle_ecosystem_chat_pipeline_http(
                "POST", ECOSYSTEM_CHAT_PATH, self._entry_body(**self._entry_readiness()),
                executor=_no_branch, evidence_verifier=self.verifier)
        self.assertEqual(seen, [self.digest])
        self.assertNotEqual(result["disposition"], "FAIL_CLOSED")
        self.assertIs(result["answer"]["fan_attempted"], True)
        self.assertNotIn("dispatched", result)

    def test_chat_entry_rejects_malformed_evidence_before_anything_runs(self):
        status, result = handle_ecosystem_chat_pipeline_http(
            "POST", ECOSYSTEM_CHAT_PATH, self._entry_body(readiness_evidence={"not": "a list"}),
            executor=_no_branch, evidence_verifier=self.verifier)
        self.assertEqual(status, 400)


# --- the census ---------------------------------------------------------------

#: Functions that hand an ingress manifest to a runtime or fan. A call to one of
#: these, by any local alias, is a dispatch site the census must classify.
DISPATCHERS = frozenset({
    "execute_manifest",
    "run_governed_llm_fan",
    "run_external_manifest",
    "run_evaluator_governance_manifest",
})
GATE = "require_ready_qualification"

GATED = "GATED"
LOCAL_ENCLOSED = "LOCAL_ENCLOSED_VALIDATION"
LOCAL_PROJECTION = "LOCAL_PROJECTION"

#: Every dispatch site at the time of this census, by ``path::function``.
#: GATED: a real dispatch entry; require_ready_qualification must precede it.
#: LOCAL_ENCLOSED_VALIDATION: the SDK's enclosed local lane (local custody
#: store, simulated consequence, labelled non-canonical; #461 left it ungated).
#: LOCAL_PROJECTION: the read-only diagnostic processor over caller-supplied
#: observations; no route runtime, no network, no mutation (#460 labelled it).
CENSUS = {
    "stegverse/cli.py::_submit_canonical_manifest": GATED,
    "stegverse/manifest_execution.py::main": GATED,
    "stegverse/external_framework_runner.py::manifest_external_framework_submission": GATED,
    "stegverse/ecosystem_chat_ask.py::ask_governed_question": GATED,
    "stegverse/external_framework_runner.py::run_external_framework": LOCAL_ENCLOSED,
    "stegverse/evaluator_governance_runtime.py::run_evaluator_governance_manifest": LOCAL_ENCLOSED,
    "stegverse/site_sdk_processing_handoff.py::execute_site_sdk_processing_handoff": LOCAL_ENCLOSED,
    "stegverse/ecosystem_diagnostic_cli.py::main": LOCAL_PROJECTION,
    "scripts/build_mir_sv_exp3_capability_documents.py::build": LOCAL_PROJECTION,
    "scripts/build_mir_sv_exp3_manifest.py::main": LOCAL_PROJECTION,
}


def _call_name(node, aliases):
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return aliases.get(func.id, func.id)
    return None


def enumerate_dispatch_sites():
    """Return {site: {"dispatch": [lineno...], "gate": [lineno...]}} for stegverse/ and scripts/."""
    sites = {}
    for top in ("stegverse", "scripts"):
        for path in sorted((REPO_ROOT / top).rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            aliases = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name in DISPATCHERS or alias.name == GATE:
                            aliases[alias.asname or alias.name] = alias.name
            rel = path.relative_to(REPO_ROOT).as_posix()
            stack = []

            class Visitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    stack.append(node.name)
                    self.generic_visit(node)
                    stack.pop()

                visit_AsyncFunctionDef = visit_FunctionDef

                def visit_ClassDef(self, node):
                    stack.append(node.name)
                    self.generic_visit(node)
                    stack.pop()

                def visit_Call(self, node):
                    name = _call_name(node, aliases)
                    if name in DISPATCHERS or name == GATE:
                        site = sites.setdefault(f"{rel}::{'.'.join(stack) or '<module>'}", {"dispatch": [], "gate": []})
                        site["gate" if name == GATE else "dispatch"].append(node.lineno)
                    self.generic_visit(node)

            Visitor().visit(tree)
    return {site: rows for site, rows in sites.items() if rows["dispatch"]}


class ReadinessGateCensusTests(unittest.TestCase):
    """The census of manifest dispatch sites is pinned; a new one must be classified here."""

    def test_every_dispatch_site_is_in_the_census(self):
        found = enumerate_dispatch_sites()
        unclassified = sorted(set(found) - set(CENSUS))
        self.assertEqual(unclassified, [], (
            "new manifest dispatch site(s) not in the SDK#368 readiness census; classify each as "
            "GATED (and call require_ready_qualification before dispatch) or as a local lane: "
            f"{unclassified}"))
        stale = sorted(set(CENSUS) - set(found))
        self.assertEqual(stale, [], f"census names dispatch site(s) that no longer dispatch: {stale}")

    def test_every_gated_site_requires_ready_qualification_before_dispatch(self):
        found = enumerate_dispatch_sites()
        for site, kind in CENSUS.items():
            if kind != GATED:
                continue
            rows = found[site]
            self.assertTrue(rows["gate"], f"{site} dispatches without calling {GATE}")
            self.assertLess(min(rows["gate"]), min(rows["dispatch"]),
                            f"{site} must call {GATE} before it dispatches")

    def test_local_lanes_are_the_only_ungated_sites(self):
        found = enumerate_dispatch_sites()
        ungated = sorted(site for site, rows in found.items() if not rows["gate"])
        self.assertEqual(ungated, sorted(site for site, kind in CENSUS.items() if kind != GATED))


if __name__ == "__main__":
    unittest.main()
