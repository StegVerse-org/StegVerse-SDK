"""Manifest identity and routing regression gate (SDK#368, .github#98 plan step 5).

Owner task: SDK-MANIFEST-IDENTITY-ROUTING-REGRESSION-GATE-001.

For every published governed route (every route whose installed runtime binding
is the universal Interlock/InTr handoff) this gate proves, on the CLI 0A/0B
paths and on the canonical entrypoint itself:

(a) processing and runtime are selected only by the admitted manifest's route
    binding; caller-supplied route/runtime/processor fields cannot change them;
(b) every route resolves to stegverse.manifest_execution.execute_manifest and no
    alternate sovereign execution entrypoint is reachable from 0A/0B;
(c) the readiness gate runs before execute_manifest on 0A and 0B, and a
    NOT_READY manifest is never dispatched;
(d) Master Records reconstruction never gates admission;
(e) no credential is read from environment variables on these paths;
(f) no network call occurs at qualification time;
(g) an out-of-scope VA-scoped chat request returns DENY before any handoff.

Real route resolution, Manifest Builder, readiness qualification and runtime
derivation are exercised. Only the pinned organization boundary read is
replaced by its fixture at dispatch. Source validation only: every outcome is
ALLOW, DENY or FAIL_CLOSED with a predicate, and no runtime ALLOW is claimed.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import inspect
import io
import json
import os
import re
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import stegverse.cli as cli
import stegverse.manifest_builder as manifest_builder
import stegverse.manifest_execution as manifest_execution
import stegverse.manifest_plan as manifest_plan
import stegverse.manifest_state_transition_runtime as runtime
from stegverse.manifest_builder import PROCESSOR_ROUTES, build_manifest, qualify_draft_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_plan import NOT_READY, READY, derive_readiness_dag, qualify_manifest_readiness
from stegverse.manifest_state_transition_runtime import UNIVERSAL_RUNTIME_BINDING, derive_execution_request
from stegverse.route_resolution import (
    PUBLISHED_ROUTES,
    SHWP_SOVEREIGN_INFERENCE_ROUTE_ID,
    VA_SCOPED_CHAT_ROUTE_ID,
)
from tests.test_ecosystem_diagnostic_processor import diagnostic_request
from tests.test_manifest_destination_binding import ORGANIZATION_BOUNDARY
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, VERIFY, _all_ready
from tests.test_organization_batch_manifest_task_binding import canonical_request, governance_request
from tests.test_shwp_manifest_task_binding import fixture as shwp_manifest
from tests.test_universal_manifest_state_transition_runtime import complete_result

OWNER_TASK_ID = "SDK-MANIFEST-IDENTITY-ROUTING-REGRESSION-GATE-001"
CANONICAL_ENTRYPOINT = "stegverse.manifest_execution.execute_manifest"
RETURN_ENTRYPOINT = "stegverse.manifest_state_transition_runtime.admit_runtime_result"
BOUNDARY = "stegverse.manifest_execution._canonical_organization_boundary"
EXAMPLES = Path(__file__).resolve().parents[1] / "inspection" / "examples"
SHARED_SOURCE = json.loads((EXAMPLES / "sdk-tt-shared-source.json").read_text(encoding="utf-8"))
CREATED_AT = "2026-10-10T00:00:00Z"

# Published routes that do not hand off to the organization Interlock/InTr path.
# They are not governed ecosystem routes; listing them here keeps the route set
# closed, so a newly published route fails this gate until it is classified.
NON_GOVERNED_ROUTES = {
    "stegverse.route.source-native-math.v1": "SDK_INSTALLED_SOURCE_PACKAGE",
    "stegverse.route.customer-local-governed.v1": "CUSTOMER_LOCAL",
}
GOVERNED_ROUTES = tuple(sorted(r for r in PUBLISHED_ROUTES if r not in NON_GOVERNED_ROUTES))

# Example processor requests already published for builder-selectable routes.
_EXAMPLE_REQUESTS = {
    "ecosystem_chat": "sdk-ecosystem-chat.processor-request.json",
    "va_scoped_chat": "sdk-va-scoped-chat.processor-request.json",
    "hil_intake": "sdk-hil-intake.processor-request.json",
    "organization_role_conformance": "sdk-organization-role-conformance.processor-request.json",
    "svg_governance_cycle": "sdk-svg-governance-cycle.processor-request.json",
    "purpose_bound_worker": "sdk-test1-purpose-worker.processor-request.json",
    "atomic_task_worker": "sdk-test2-atomic-task-worker.processor-request.json",
    "stegbrowser": "sdk-test5-stegbrowser-llm-profile.processor-request.json",
}

# Every alternate execution entrypoint that 0A/0B must not reach. The
# per-route processors are reachable only as the manifest route binding of a
# non-governed route, never from a governed manifest.
ALTERNATE_ENTRYPOINTS = (
    "stegverse.governance_ingress_runtime.run_external_manifest",
    "stegverse.governance_ingress_runtime.external_manifest_to_public_request",
    "stegverse.sovereign_validation_runtime.run_sovereign_validation",
    "stegverse.sovereign_validation_runtime.replay_sovereign",
    "stegverse.sovereign_validation_runtime.reconstruct_sovereign",
    "stegverse.governance_fallback.execute_fallback",
    "stegverse.universal_entry_runtime.run_universal_entry",
    "stegverse.customer_local_governance.execute_manifest",
    "stegverse.native_source_math.execute_manifest",
    "stegverse.ecosystem_diagnostic_runtime.execute_manifest",
    "stegverse.purpose_bound_worker_processor.execute_manifest",
    "stegverse.atomic_task_worker_processor.execute_manifest",
    "stegverse.cli._local_enclosed_operations",
)

# Master Records replay/reconstruction libraries; admission must never call them.
MASTER_RECORDS_LIBRARIES = (
    "stegverse.sovereign_validation_runtime.replay_sovereign",
    "stegverse.sovereign_validation_runtime.reconstruct_sovereign",
)

DECOY_CREDENTIALS = {
    "GITHUB_TOKEN": "decoy-github-token-7f1c",
    "GH_TOKEN": "decoy-gh-token-7f1c",
    "STEGVERSE_TVC_DECISION_RECEIPT": "decoy-tvc-receipt-7f1c",
    "STEGVERSE_TVC_DECISION_RECEIPT_FILE": "/nonexistent/decoy-tvc-receipt-7f1c",
    "STEGVERSE_HIL_RECEIPT_KEY": "decoy-hil-key-7f1c",
    "STEGVERSE_MASTER_RECORDS_TOKEN": "decoy-mr-token-7f1c",
    "STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": "https://decoy.invalid/intr-7f1c",
    "STEGVERSE_INTR_TOKEN": "decoy-intr-token-7f1c",
    "OPENAI_API_KEY": "decoy-openai-key-7f1c",
    "ANTHROPIC_API_KEY": "decoy-anthropic-key-7f1c",
    "STEGVERSE_READINESS_HMAC_KEY": "decoy-readiness-key-7f1c",
}
CREDENTIAL_NAME = re.compile(r"TOKEN|SECRET|PASSW|CREDENTIAL|API_KEY|_KEY$|PRIVATE|RECEIPT|INGRESS_URL|AUTH", re.I)


def _processor_request(capability):
    if capability == "governance":
        return governance_request(canonical_request())
    if capability == "ecosystem_diagnostic":
        return diagnostic_request()
    return json.loads((EXAMPLES / _EXAMPLE_REQUESTS[capability]).read_text(encoding="utf-8"))


def _builder_data(capability):
    return canonical_request() if capability == "governance" else SHARED_SOURCE


def _source_output_id(capability):
    return canonical_request()["request_id"] if capability == "governance" else f"gate-{capability}"


def _source_framework(capability):
    return "StegVerse-Labs/.github" if capability == "governance" else "fixture-framework"


def build_route_manifest(route_id, request=None):
    """The admitted manifest that declares ``route_id``."""
    if route_id == SHWP_SOVEREIGN_INFERENCE_ROUTE_ID:
        return shwp_manifest()  # published route without a Manifest Builder processor
    capability = PUBLISHED_ROUTES[route_id]["processor_capability"]
    return build_manifest(
        data=_builder_data(capability),
        source_framework=_source_framework(capability),
        source_output_id=_source_output_id(capability),
        processor_request=request if request is not None else _processor_request(capability),
        process=capability,
        created_at=CREATED_AT,
    )


def builder_routes():
    return tuple(r for r in GOVERNED_ROUTES if PUBLISHED_ROUTES[r]["processor_capability"] in PROCESSOR_ROUTES)


def _fresh_evidence(manifest):
    return _all_ready(manifest, at=datetime.now(timezone.utc) - timedelta(seconds=5))


def _last_json(text):
    index = text.rfind("\n{\n")
    return json.loads(text[index + 1:] if index >= 0 else text)


class _NetworkDenied:
    """Deny and record every outbound connection attempt."""

    def __init__(self):
        self.attempts = []

    def _deny(self, label):
        def deny(*args, **_kwargs):
            self.attempts.append((label, repr(args[:2])))
            raise OSError(f"NETWORK_DENIED_BY_REGRESSION_GATE: {label}")
        return deny

    @contextlib.contextmanager
    def active(self):
        targets = (
            "urllib.request.urlopen",
            "stegverse.github_repository_fetcher.urlopen",
            "socket.create_connection",
            "socket.socket.connect",
            "socket.socket.connect_ex",
            "socket.getaddrinfo",
            "http.client.HTTPConnection.connect",
            "http.client.HTTPSConnection.connect",
        )
        with contextlib.ExitStack() as stack:
            for target in targets:
                stack.enter_context(patch(target, side_effect=self._deny(target)))
            yield self


class _RecordingEnviron(dict):
    """os.environ replacement holding decoy credentials and recording every read."""

    def __init__(self, base):
        super().__init__(base)
        self.reads = []

    def __getitem__(self, key):
        self.reads.append(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        self.reads.append(key)
        return super().get(key, default)

    def __contains__(self, key):
        self.reads.append(key)
        return super().__contains__(key)

    def copy(self):
        self.reads.append("*copy*")
        return dict(self)

    def items(self):
        self.reads.append("*items*")
        return super().items()


@contextlib.contextmanager
def _decoy_environ():
    environ = _RecordingEnviron({**os.environ, **DECOY_CREDENTIALS})
    with patch("os.environ", environ):
        yield environ


class _GateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self._counter = 0

    def _write(self, value):
        self._counter += 1
        path = Path(self.tmp.name) / f"f{self._counter}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return str(path)

    def _evidence_args(self, manifest, ready):
        if not ready:
            return []
        return [
            "--attempt-id", ATTEMPT,
            "--readiness-evidence", self._write(_fresh_evidence(manifest)),
            "--readiness-keys", self._write({KEY_ID: KEY}),
        ]

    def argv_0b(self, manifest, *, ready=True, extra=()):
        return ["governance", "--select", "0B", "--manifest", self._write(manifest),
                *self._evidence_args(manifest, ready), *extra]

    def argv_0a(self, route_id, *, ready=True, request=None):
        capability = PUBLISHED_ROUTES[route_id]["processor_capability"]
        manifest = build_route_manifest(route_id, request)
        return [
            "governance", "--select", "0A",
            "--input", self._write(_builder_data(capability)),
            "--processor-request", self._write(request if request is not None else _processor_request(capability)),
            "--process", capability,
            "--source-framework", _source_framework(capability),
            "--source-output-id", _source_output_id(capability),
            *self._evidence_args(manifest, ready),
        ]

    def run_cli(self, argv, *, boundary=ORGANIZATION_BOUNDARY):
        out = io.StringIO()
        kwargs = {"side_effect": boundary} if isinstance(boundary, BaseException) else {"return_value": boundary}
        with patch(BOUNDARY, **kwargs) as fetched, contextlib.redirect_stdout(out):
            rc = cli.main(argv)
        return rc, _last_json(out.getvalue()), fetched

    def assert_six_field_outcome(self, output):
        self.assertIn(output["disposition"], {"ALLOW", "DENY", "FAIL_CLOSED"})
        if output["disposition"] != "ALLOW":
            self.assertTrue(output["failed_predicate"])
        self.assertNotIn("WAITING", json.dumps(output["disposition"]))


@contextlib.contextmanager
def _forbid(*targets):
    def forbidden(name):
        def refuse(*_args, **_kwargs):
            raise AssertionError(f"ALTERNATE_ENTRYPOINT_REACHED: {name}")
        return refuse

    with contextlib.ExitStack() as stack:
        for target in targets:
            stack.enter_context(patch(target, side_effect=forbidden(target)))
        yield


class RouteSetTests(unittest.TestCase):
    def test_every_published_route_is_classified(self):
        for route_id, surface in NON_GOVERNED_ROUTES.items():
            self.assertEqual(PUBLISHED_ROUTES[route_id]["routing_surface"], surface)
            self.assertNotEqual(PUBLISHED_ROUTES[route_id]["runtime_binding"], UNIVERSAL_RUNTIME_BINDING)
        self.assertGreaterEqual(len(GOVERNED_ROUTES), 11)
        for route_id in GOVERNED_ROUTES:
            self.assertEqual(PUBLISHED_ROUTES[route_id]["runtime_binding"], UNIVERSAL_RUNTIME_BINDING, route_id)

    def test_every_governed_route_has_an_admitted_manifest_in_this_gate(self):
        for route_id in GOVERNED_ROUTES:
            manifest = build_route_manifest(route_id)
            self.assertEqual(manifest["processing"]["route_id"], route_id)
            self.assertEqual(validate_ingress_manifest(manifest)["processing"]["route_id"], route_id)


class SelectionByRouteBindingTests(_GateCase):
    """(a) The admitted manifest's route binding alone selects processing and runtime."""

    def _dispatch(self, manifest):
        with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY):
            return manifest_execution.execute_manifest(manifest)

    def _expected(self, route_id):
        route = PUBLISHED_ROUTES[route_id]
        return route_id, route["runtime_binding"], route["processor_capability"]

    def _selected(self, result):
        lineage = result["manifest_lineage"]["run_manifest_request"]
        return lineage["route_id"], lineage["runtime_binding"], lineage["processing_capability"]

    def test_each_route_selects_its_published_binding(self):
        for route_id in GOVERNED_ROUTES:
            result = self._dispatch(build_route_manifest(route_id))
            self.assertEqual(self._selected(result), self._expected(route_id), route_id)
            self.assertEqual(result["route_id"], route_id)

    def _tampered(self, manifest, route_id):
        other = next(r for r in GOVERNED_ROUTES if r != route_id)
        other_capability = PUBLISHED_ROUTES[other]["processor_capability"]
        foreign_binding = "stegverse.governance_ingress_runtime.run_external_manifest"
        cases = {}

        def case(name, mutate):
            tampered = copy.deepcopy(manifest)
            mutate(tampered)
            cases[name] = tampered

        for field in ("route_id", "runtime_binding", "processor", "processing_capability", "runtime"):
            case(f"top-level {field}", lambda m, f=field: m.__setitem__(f, foreign_binding if "runtime" in f else other))
        case("route declaration runtime_binding",
             lambda m: m["extensions"]["stegverse_route"].__setitem__("runtime_binding", foreign_binding))
        case("route declaration processor_capability",
             lambda m: m["extensions"]["stegverse_route"].__setitem__("processor_capability", other_capability))
        case("processing.route_id",
             lambda m: m["processing"].__setitem__("route_id", other))
        case("processing.capability",
             lambda m: m["processing"].__setitem__("capability", other_capability))
        case("processing.runtime_binding",
             lambda m: m["processing"].__setitem__("runtime_binding", foreign_binding))
        case("extensions.runtime_binding",
             lambda m: m["extensions"].__setitem__("runtime_binding", foreign_binding))
        case("extensions.stegverse_runtime",
             lambda m: m["extensions"].__setitem__("stegverse_runtime", {"runtime_binding": foreign_binding}))
        case("route declaration id swapped alone",
             lambda m: m["extensions"]["stegverse_route"].__setitem__("route_id", other))
        return cases

    def test_caller_supplied_route_runtime_processor_fields_cannot_change_selection(self):
        with _forbid(*ALTERNATE_ENTRYPOINTS):
            for route_id in GOVERNED_ROUTES:
                manifest = build_route_manifest(route_id)
                for name, tampered in self._tampered(manifest, route_id).items():
                    with self.subTest(route=route_id, injection=name):
                        try:
                            result = self._dispatch(tampered)
                        except ValueError:
                            continue  # refused: the injection selected nothing
                        self.assertEqual(self._selected(result), self._expected(route_id))

    def test_mismatched_processing_capability_is_refused_on_every_route(self):
        # Regression: stegbrowser, svg-governance-cycle and shwp-sovereign-inference
        # admitted a manifest naming another processor because only some
        # adapters checked processing.capability.
        for route_id in GOVERNED_ROUTES:
            own = PUBLISHED_ROUTES[route_id]["processor_capability"]
            for capability in sorted({r["processor_capability"] for r in PUBLISHED_ROUTES.values()} - {own}):
                tampered = copy.deepcopy(build_route_manifest(route_id))
                tampered["processing"]["capability"] = capability
                with self.subTest(route=route_id, capability=capability), self.assertRaises(ValueError):
                    self._dispatch(tampered)

    def test_cli_exposes_no_runtime_or_route_override(self):
        for flag in ("--route", "--route-id", "--runtime", "--runtime-binding", "--processor-binding", "--entrypoint"):
            with self.subTest(flag=flag), contextlib.redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit):
                cli.main(["governance", "--select", "0B", "--manifest", "m.json", flag, "x"])

    def test_0b_process_argument_cannot_reselect_a_supplied_manifest(self):
        with _forbid(*ALTERNATE_ENTRYPOINTS):
            for route_id in GOVERNED_ROUTES:
                manifest = build_route_manifest(route_id)
                other = "governance" if PUBLISHED_ROUTES[route_id]["processor_capability"] != "governance" else "hil_intake"
                rc, output, _ = self.run_cli(self.argv_0b(manifest, extra=("--process", other)))
                self.assert_six_field_outcome(output)
                self.assertEqual(output["route_id"], route_id)
                self.assertEqual(output["runtime_binding"], UNIVERSAL_RUNTIME_BINDING)
                self.assertEqual(output["runtime_selected_by"], "MANIFEST_ROUTE_RUNTIME_BINDING")
                self.assertIs(output["console_selection_selects_runtime"], False)

    def test_0a_and_0b_select_the_same_runtime_for_the_same_manifest(self):
        for route_id in builder_routes():
            _, built, _ = self.run_cli(self.argv_0a(route_id))
            _, supplied, _ = self.run_cli(self.argv_0b(built["manifest"]))
            for key in ("route_id", "runtime_binding", "canonical_manifest_sha256"):
                self.assertEqual(built[key], supplied[key], (route_id, key))
            self.assertEqual(built["route_id"], route_id)


class CanonicalEntrypointTests(_GateCase):
    """(b) Every route resolves to the one canonical entrypoint."""

    def test_canonical_entrypoint_identity(self):
        function = manifest_execution.execute_manifest
        self.assertEqual(f"{function.__module__}.{function.__qualname__}", CANONICAL_ENTRYPOINT)
        self.assertEqual(cli.CANONICAL_MANIFEST_ENTRYPOINT, CANONICAL_ENTRYPOINT)
        self.assertEqual(cli.RESULT_RETURN_ENTRYPOINT, RETURN_ENTRYPOINT)

    def test_every_route_dag_names_the_universal_processor_and_return(self):
        for route_id in GOVERNED_ROUTES:
            nodes = {n["role"]: n for n in derive_readiness_dag(build_route_manifest(route_id))}
            self.assertEqual(nodes["processor"]["component"], UNIVERSAL_RUNTIME_BINDING, route_id)
            self.assertEqual(nodes["return"]["component"], RETURN_ENTRYPOINT, route_id)

    def _run_spied(self, argv):
        calls = {"canonical": 0, "runtime": 0}
        real_canonical = manifest_execution.execute_manifest
        real_runtime = runtime.execute_manifest

        def canonical(*args, **kwargs):
            calls["canonical"] += 1
            return real_canonical(*args, **kwargs)

        def inner(*args, **kwargs):
            # The universal runtime is reached only from inside the canonical entrypoint.
            self.assertEqual(calls["canonical"], 1)
            calls["runtime"] += 1
            return real_runtime(*args, **kwargs)

        with _forbid(*ALTERNATE_ENTRYPOINTS), \
                patch("stegverse.manifest_execution.execute_manifest", side_effect=canonical), \
                patch("stegverse.manifest_state_transition_runtime.execute_manifest", side_effect=inner):
            rc, output, _ = self.run_cli(argv)
        return rc, output, calls

    def test_0b_reaches_only_the_canonical_entrypoint_for_every_route(self):
        for route_id in GOVERNED_ROUTES:
            rc, output, calls = self._run_spied(self.argv_0b(build_route_manifest(route_id)))
            self.assert_six_field_outcome(output)
            self.assertEqual(calls, {"canonical": 1, "runtime": 1}, route_id)
            self.assertEqual(output["canonical_entrypoint"], CANONICAL_ENTRYPOINT)
            self.assertEqual(output["route_id"], route_id)

    def test_0a_reaches_only_the_canonical_entrypoint_for_every_builder_route(self):
        for route_id in builder_routes():
            rc, output, calls = self._run_spied(self.argv_0a(route_id))
            self.assert_six_field_outcome(output)
            self.assertEqual(calls, {"canonical": 1, "runtime": 1}, route_id)
            self.assertEqual(output["manifest_preparation"], "SDK_MANIFEST_BUILDER")
            self.assertEqual(output["route_id"], route_id)

    def test_cli_0a_0b_source_names_no_alternate_entrypoint(self):
        names = {target.rsplit(".", 1)[1] for target in ALTERNATE_ENTRYPOINTS} - {"execute_manifest"}
        for function in (cli._submit_canonical_manifest, cli._build_0a_manifest):
            tree = ast.parse(inspect.getsource(function).lstrip())
            referenced = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
            referenced |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
            imported = {
                (node.module or "", alias.name)
                for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names
            }
            self.assertFalse(referenced & names, function.__name__)
            for module, name in imported:
                if name == "execute_manifest":
                    self.assertEqual(module, "manifest_execution", function.__name__)
        self.assertNotIn("run_external_manifest", vars(cli))
        self.assertNotIn("run_sovereign_validation", vars(cli))


class ReadinessBeforeDispatchTests(_GateCase):
    """(c) Readiness qualification precedes execute_manifest; NOT_READY never dispatches."""

    def _run_ordered(self, argv):
        events = []
        real_qualify = manifest_builder.qualify_draft_manifest
        real_require = manifest_plan.require_ready_qualification
        real_execute = manifest_execution.execute_manifest

        def qualify(*args, **kwargs):
            events.append("qualify")
            return real_qualify(*args, **kwargs)

        def require(*args, **kwargs):
            events.append("require_ready")
            return real_require(*args, **kwargs)

        def execute(*args, **kwargs):
            events.append("execute_manifest")
            return real_execute(*args, **kwargs)

        with patch("stegverse.manifest_builder.qualify_draft_manifest", side_effect=qualify), \
                patch("stegverse.manifest_plan.require_ready_qualification", side_effect=require), \
                patch("stegverse.manifest_execution.execute_manifest", side_effect=execute):
            rc, output, fetched = self.run_cli(argv)
        return rc, output, fetched, events

    def _cases(self, ready):
        for route_id in GOVERNED_ROUTES:
            yield "0B", route_id, self.argv_0b(build_route_manifest(route_id), ready=ready)
        for route_id in builder_routes():
            yield "0A", route_id, self.argv_0a(route_id, ready=ready)

    def test_ready_manifest_is_qualified_before_dispatch(self):
        for selection, route_id, argv in self._cases(ready=True):
            with self.subTest(selection=selection, route=route_id):
                rc, output, fetched, events = self._run_ordered(argv)
                self.assertEqual(events, ["qualify", "require_ready", "execute_manifest"])
                self.assertEqual(output["readiness_qualification"]["qualification"], READY)
                self.assertIs(output["executable"], True)
                self.assert_six_field_outcome(output)
                fetched.assert_called_once()

    def test_not_ready_manifest_is_never_dispatched(self):
        for selection, route_id, argv in self._cases(ready=False):
            with self.subTest(selection=selection, route=route_id):
                rc, output, fetched, events = self._run_ordered(argv)
                self.assertEqual(events, ["qualify"])
                self.assertEqual(rc, 2)
                self.assertEqual(output["disposition"], "FAIL_CLOSED")
                self.assertEqual(output["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
                self.assertIs(output["executable"], False)
                self.assertIs(output["draft_preserved"], True)
                self.assertNotIn("result", output)
                fetched.assert_not_called()

    def test_partially_evidenced_manifest_is_never_dispatched(self):
        for route_id in GOVERNED_ROUTES:
            manifest = build_route_manifest(route_id)
            partial = _all_ready(manifest, skip=("authorization",),
                                 at=datetime.now(timezone.utc) - timedelta(seconds=5))
            argv = ["governance", "--select", "0B", "--manifest", self._write(manifest),
                    "--attempt-id", ATTEMPT, "--readiness-evidence", self._write(partial),
                    "--readiness-keys", self._write({KEY_ID: KEY})]
            rc, output, fetched, events = self._run_ordered(argv)
            self.assertEqual(events, ["qualify"], route_id)
            self.assertEqual(output["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
            roles = {node["role"] for node in output["evidence"]["failing_nodes"]}
            self.assertIn("authorization", roles)
            fetched.assert_not_called()


class MasterRecordsNonGatingTests(_GateCase):
    """(d) Master Records reconstruction never gates admission."""

    def test_readiness_dag_has_no_master_records_node(self):
        for route_id in GOVERNED_ROUTES:
            for node in derive_readiness_dag(build_route_manifest(route_id)):
                self.assertNotIn("MASTER_RECORDS", json.dumps(node).upper(), (route_id, node["role"]))
                if node["role"] == "custody":
                    self.assertEqual(node["component"], "ORGANIZATION_LEDGER_CUSTODY")

    def test_admission_never_consults_master_records(self):
        with _forbid(*MASTER_RECORDS_LIBRARIES):
            for route_id in GOVERNED_ROUTES:
                manifest = build_route_manifest(route_id)
                qualification = qualify_manifest_readiness(
                    manifest, attempt_id=ATTEMPT, readiness_evidence=_fresh_evidence(manifest),
                    evidence_verifier=VERIFY,
                )
                self.assertEqual(qualification["qualification"], READY, route_id)
                rc, output, _ = self.run_cli(self.argv_0b(manifest))
                self.assert_six_field_outcome(output)
                self.assertIs(output["result"].get("master_records_reconstruction_observed", False), False)

    def test_failed_reconstruction_evidence_does_not_gate_result_admission(self):
        for route_id in GOVERNED_ROUTES:
            if PUBLISHED_ROUTES[route_id]["processor_capability"] == "governance":
                continue  # covered by tests/test_master_records_reconstruction_non_gating.py
            manifest = build_route_manifest(route_id)
            request = derive_execution_request(manifest, ORGANIZATION_BOUNDARY)
            if request["state_graph"].get("manifest_policy_refusal"):
                continue
            result = complete_result(request)
            for row in result["transition_closures"]:
                row["reconstruction_status"] = "FAIL"
                row["reconstructed_receipt_sha256"] = "f" * 64
            result["replay_status"] = result["reconstruction_status"] = "FAIL"
            with self.subTest(route=route_id):
                try:
                    checked = runtime.validate_runtime_result(result, request)
                except ValueError as exc:
                    # A refusal must name a non-Master-Records predicate.
                    self.assertNotRegex(str(exc).upper(), "MASTER_RECORDS|RECONSTRUCT|REPLAY")
                    continue
                evidence = checked["master_records_reconstruction_evidence"]
                self.assertIs(evidence["gates_admission"], False)
                self.assertEqual(evidence["evidence_status"], "FAIL")


class NoEnvironmentCredentialTests(_GateCase):
    """(e) No credential is read from environment variables on these paths."""

    def _assert_unused(self, environ, outputs):
        credential_reads = sorted({k for k in environ.reads if CREDENTIAL_NAME.search(k)})
        self.assertEqual(credential_reads, [])
        self.assertFalse(set(environ.reads) & set(DECOY_CREDENTIALS))
        self.assertNotIn("*copy*", environ.reads)
        self.assertNotIn("*items*", environ.reads)
        text = json.dumps(outputs, default=str)
        for value in DECOY_CREDENTIALS.values():
            self.assertNotIn(value, text)

    def test_0a_0b_and_canonical_dispatch_read_no_environment_credential(self):
        outputs = []
        prepared = []
        for route_id in GOVERNED_ROUTES:
            manifest = build_route_manifest(route_id)
            prepared.append(self.argv_0b(manifest))
            prepared.append(self.argv_0b(manifest, ready=False))
        for route_id in builder_routes():
            prepared.append(self.argv_0a(route_id))
            prepared.append(self.argv_0a(route_id, ready=False))
        with _decoy_environ() as environ:
            for argv in prepared:
                rc, output, _ = self.run_cli(argv)
                self.assert_six_field_outcome(output)
                outputs.append(output)
            for route_id in GOVERNED_ROUTES:
                manifest = build_route_manifest(route_id)
                qualify_manifest_readiness(manifest, attempt_id=ATTEMPT)
                with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY):
                    outputs.append(manifest_execution.execute_manifest(manifest))
        self._assert_unused(environ, outputs)

    def test_boundary_read_without_fixture_reads_no_environment_credential(self):
        # The pinned boundary read at dispatch is the one network-capable step;
        # with network denied it must fail closed without consulting a token.
        manifest = build_route_manifest(GOVERNED_ROUTES[0])
        with _decoy_environ() as environ, _NetworkDenied().active():
            result = manifest_execution.execute_manifest(manifest)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "CANONICAL_ORGANIZATION_INGRESS_ENDPOINT_NOT_RESOLVED")
        self._assert_unused(environ, [result])


class NoQualificationNetworkTests(_GateCase):
    """(f) No network call occurs at qualification time."""

    def test_build_validate_and_qualify_make_no_network_call(self):
        with _NetworkDenied().active() as network:
            for route_id in GOVERNED_ROUTES:
                manifest = build_route_manifest(route_id)
                validate_ingress_manifest(manifest)
                self.assertEqual(qualify_manifest_readiness(manifest, attempt_id=ATTEMPT)["qualification"], NOT_READY)
                ready = qualify_draft_manifest(
                    manifest, attempt_id=ATTEMPT, readiness_evidence=_fresh_evidence(manifest),
                    evidence_verifier=VERIFY,
                )
                self.assertIs(ready["executable"], True, route_id)
                derive_execution_request(manifest, ORGANIZATION_BOUNDARY)
        self.assertEqual(network.attempts, [])

    def test_cli_qualification_and_dispatch_make_no_network_call(self):
        prepared = []
        for route_id in GOVERNED_ROUTES:
            manifest = build_route_manifest(route_id)
            prepared += [self.argv_0b(manifest), self.argv_0b(manifest, ready=False)]
        for route_id in builder_routes():
            prepared += [self.argv_0a(route_id), self.argv_0a(route_id, ready=False)]
        with _NetworkDenied().active() as network:
            for argv in prepared:
                rc, output, _ = self.run_cli(argv)
                self.assert_six_field_outcome(output)
                for key in ("receiver_contacted", "transport_performed_by_sdk", "consequence_committed"):
                    if "result" in output and key in output["result"]:
                        self.assertIs(output["result"][key], False, key)
        self.assertEqual(network.attempts, [])


class VaScopeDenyBeforeHandoffTests(_GateCase):
    """(g) Out-of-scope VA-scoped chat requests are refused before any handoff."""

    def _out_of_scope_manifest(self):
        request = _processor_request("va_scoped_chat")
        allowed = set(request["va_scope"]["allowed_topics"])
        request["requested_topic"] = next(t for t in ("payroll", "medical-records", "x-off-scope") if t not in allowed)
        return build_route_manifest(VA_SCOPED_CHAT_ROUTE_ID, request), request

    def _assert_deny_before_handoff(self, result):
        self.assertEqual(result["disposition"], "DENY")
        self.assertIs(result["terminal"], True)
        self.assertEqual(result["failed_predicate"], "REQUESTED_TOPIC_WITHIN_MANIFEST_DECLARED_VA_SCOPE")
        self.assertNotIn("handoff_sha256", result)
        for key in ("receiver_contacted", "transport_performed_by_sdk", "consequence_committed"):
            self.assertIs(result[key], False, key)

    def test_canonical_dispatch_denies_without_building_a_handoff(self):
        manifest, _ = self._out_of_scope_manifest()
        for boundary in (ORGANIZATION_BOUNDARY, OSError("boundary unavailable")):
            kwargs = {"side_effect": boundary} if isinstance(boundary, BaseException) else {"return_value": boundary}
            with self.subTest(boundary=type(boundary).__name__), \
                    patch(BOUNDARY, **kwargs), \
                    _NetworkDenied().active() as network, \
                    patch("stegverse.manifest_state_transition_runtime.build_intr_handoff",
                          side_effect=AssertionError("handoff built for an out-of-scope request")):
                result = manifest_execution.execute_manifest(manifest)
            self._assert_deny_before_handoff(result)
            self.assertEqual(result["manifest_lineage"]["run_manifest_request"]["route_id"], VA_SCOPED_CHAT_ROUTE_ID)
            self.assertEqual(network.attempts, [])

    def test_cli_0a_and_0b_deny_without_building_a_handoff(self):
        manifest, request = self._out_of_scope_manifest()
        for argv in (self.argv_0b(manifest), self.argv_0a(VA_SCOPED_CHAT_ROUTE_ID, request=request)):
            with self.subTest(selection=argv[2]), \
                    patch("stegverse.manifest_state_transition_runtime.build_intr_handoff",
                          side_effect=AssertionError("handoff built for an out-of-scope request")):
                rc, output, _ = self.run_cli(argv)
            self.assertEqual(rc, 2)
            self.assertEqual(output["disposition"], "DENY")
            self.assertEqual(output["failed_predicate"], "REQUESTED_TOPIC_WITHIN_MANIFEST_DECLARED_VA_SCOPE")
            self._assert_deny_before_handoff(output["result"])

    def test_in_scope_request_is_handed_off(self):
        with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY):
            result = manifest_execution.execute_manifest(build_route_manifest(VA_SCOPED_CHAT_ROUTE_ID))
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertEqual(result["state"], "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF")
        self.assertIs(result["receiver_contacted"], False)


if __name__ == "__main__":
    unittest.main()
