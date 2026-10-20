"""Fix 4: the SDK-hosted Universal InTr edge-route installer and wrapper.

Real route resolution, manifest validation and Manifest Builder; nothing is
mocked. Every non-ALLOW must carry the six fields (ORRD L61). No listener is
started, no source is written in place, no clock is read, and no receipt is
claimed.
"""
from __future__ import annotations

import ast
import hashlib
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from stegverse import universal_intr_route_installer as installer
from stegverse.manifest_builder import build_manifest
from stegverse.route_resolution import PUBLISHED_ROUTES, STEGBROWSER_ROUTE_ID, _ROUTE_FIELDS

SIX = ("failure_code", "failed_predicate", "required_evidence_or_repair",
       "retry_entrypoint", "owning_existing_goal", "next_attempt")
SEF_SHA256 = "7f36f0e697cadc91acd27af121eee3fc460b887ec67cfa258727bfccec0ca5f8"

ROUTER = (
    '#!/usr/bin/env python3\n'
    'from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\n'
    'ROOT = Path(__file__).resolve().parents[1]\n'
    'import serve_hil_intr_materialization_ingress as hil  # noqa: E402\n'
    'def profile():\n'
    '    return {\n'
    '        "profiles": ["HIL:Ingress", "SV002:PublicObservation"],\n'
    '    }\n'
    'def do_POST(self):\n'
    '                receipt = admit_sv002(runtime_root=self.server.runtime_root, body=body, headers=self.headers) '
    'if _is_sv002(payload) else hil.admit_materialization(runtime_root=self.server.runtime_root, body=body, headers=self.headers)\n'
)
BOUNDARY = {
    "organization": "StegVerse-Labs",
    "ingress": {"capability_endpoint_bindings": [{
        "profile_id": "sdk-manifest-ingress", "operation": "SUBMIT_MANIFEST",
        "payload_schema": "stegverse.ingress-manifest.v1",
        "receiving_operation": {"addressed_service": "stegverse-labs.sdk-manifest-ingress"}}]},
}


def stegbrowser_route():
    return {field: PUBLISHED_ROUTES[STEGBROWSER_ROUTE_ID][field] for field in _ROUTE_FIELDS}


def install_request(**overrides):
    request = {"schema": installer.INSTALLATION_REQUEST_SCHEMA, "consumer_id": "stegbrowser",
               "route": stegbrowser_route(), "hb_epoch": "40",
               "router": {"path": installer.DEFAULT_ROUTER,
                          "predecessor_sha256": installer.sha256_uri(ROUTER.encode())}}
    request.update(overrides)
    return request


def stegbrowser_manifest():
    return build_manifest(
        data={"edge": "stegbrowser"}, data_class="stegverse.sdk-test.v1",
        source_framework="StegVerse-SDK-Evaluator", source_output_id="fix4-edge-1",
        processor_request={
            "schema": "stegbrowser.llm-profile-request.v1", "profile": "llm.v1",
            "prompt": "Return the exact marker FIX4.", "response_marker": "FIX4", "provider": "openai",
            "journey": {
                "schema": "stegverse.packet-carried-endpoint-receipt-journey/v1", "journey_id": "fix4",
                "origin_endpoint": "stegverse:fix4-origin", "ephemeral_endpoint": "stegbrowser:ephemeral:fix4",
                "outbound_manifest_sha256": "sha256:" + "a" * 64, "return_manifest_sha256": "sha256:" + "c" * 64,
                "return_predecessor_manifest_sha256": "sha256:" + "a" * 64}},
        process="stegbrowser", return_depth="full-trace", publisher_required=False)


class Base(unittest.TestCase):
    def assertNonAllow(self, result, disposition, failure_code):
        self.assertEqual(disposition, result["disposition"], result)
        self.assertEqual(failure_code, result["failure_code"])
        for field in SIX:
            self.assertTrue(result.get(field), field)
        self.assertFalse(result["next_attempt"]["awaits_an_external_machine"])


class SharedEpochRuleTests(Base):
    def test_supplied_epoch_failure_is_byte_identical_to_the_shared_rule(self):
        source = Path(installer.__file__).read_text(encoding="utf-8")
        node = next(n for n in ast.parse(source).body
                    if isinstance(n, ast.FunctionDef) and n.name == "supplied_epoch_failure")
        segment = ast.get_source_segment(source, node) + "\n"
        self.assertEqual(SEF_SHA256, hashlib.sha256(segment.encode("utf-8")).hexdigest())

    def test_coerced_and_absent_epochs_fail_closed_with_six_fields(self):
        for value, code in ((None, "HB_EPOCH_NOT_SUPPLIED"), (" 32", "HB_EPOCH_INVALID"),
                            ("+32", "HB_EPOCH_INVALID"), ("3_2", "HB_EPOCH_INVALID"),
                            ("\u0663\u0662", "HB_EPOCH_INVALID"), ("31", "HB_EPOCH_INVALID"),
                            (True, "HB_EPOCH_INVALID")):
            result = installer.evaluate_installation(install_request(hb_epoch=value), ROUTER.encode())
            self.assertNonAllow(result, "FAIL_CLOSED", code)
            self.assertEqual(installer.EPOCH_PREDICATE, result["failed_predicate"])


class InstallationTests(Base):
    def test_allow_records_the_transition_without_writing_source(self):
        result = installer.evaluate_installation(install_request(), ROUTER.encode())
        self.assertEqual("ALLOW", result["disposition"])
        transition = result["transition"]
        self.assertEqual(installer.sha256_uri(ROUTER.encode()), transition["predecessor"]["sha256"])
        self.assertEqual(installer.sha256_uri(result["successor_source"].encode()),
                         transition["proposed_successor"]["sha256"])
        self.assertEqual("stegbrowser", transition["manifested_capability"])
        self.assertEqual(STEGBROWSER_ROUTE_ID, transition["route"]["route_id"])
        self.assertEqual("40", transition["hb_epoch"])
        self.assertFalse(result["source_mutated"])
        self.assertFalse(result["listener_started"])
        self.assertFalse(result["receipt_claimed"])
        self.assertEqual("DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION",
                         transition["governing_constraints"]["receiver_unavailable_disposition"])

    def test_transform_installs_one_wrapped_branch_and_is_idempotent(self):
        once = installer.transform_router(ROUTER, "stegbrowser")
        self.assertEqual(once, installer.transform_router(once, "stegbrowser"))
        self.assertEqual(1, once.count(installer.WRAPPER_IMPORT))
        self.assertIn('"StegBrowser:ManifestInvocation"]', once)
        self.assertIn('receipt = sdk_admit_edge_submission(payload, consumer_id="stegbrowser", '
                      'organization_root=ROOT) if sdk_is_edge_submission(payload, consumer_id="stegbrowser") '
                      'else (admit_sv002(', once)
        self.assertTrue(once.rstrip().endswith("headers=self.headers))"))

    def test_consumers_without_a_published_route_fail_closed(self):
        unpublished = sorted(cid for cid, row in installer.EDGE_CONSUMERS.items() if row["route_id"] is None)
        self.assertEqual(["canonical_work", "erl_active_research", "kv_ai_memory", "site_publication",
                          "stegsocials_bounded", "tvc_recipient_admission_sign"], unpublished)
        for consumer_id in unpublished:
            result = installer.evaluate_installation(install_request(consumer_id=consumer_id), ROUTER.encode())
            self.assertNonAllow(result, "FAIL_CLOSED", "EDGE_CONSUMER_ROUTE_NOT_PUBLISHED")

    def test_route_publication_evidence_lists_exactly_the_unpublished_consumers(self):
        doc = (Path(__file__).resolve().parents[1] / "docs/UNIVERSAL_INTR_ROUTE_INSTALLER.md").read_text(encoding="utf-8")
        section = doc.split("## Route publication evidence (six consumers)", 1)[1]
        rows = sorted(line.split("`")[1] for line in section.splitlines() if line.startswith("| `"))
        unpublished = sorted(cid for cid, row in installer.EDGE_CONSUMERS.items() if row["route_id"] is None)
        self.assertEqual(unpublished, rows)
        capabilities = {row.get("processor_capability") for row in PUBLISHED_ROUTES.values()}
        for consumer_id in unpublished:
            # Publication in the SDK is distinct from installing an edge-consumer
            # binding. canonical_work is published, but its edge installer must
            # continue to FAIL_CLOSED until EDGE_CONSUMERS binds the route.
            if consumer_id == "canonical_work":
                self.assertIn(consumer_id, capabilities)
            else:
                self.assertNotIn(consumer_id, capabilities)
            self.assertIsNone(installer.EDGE_CONSUMERS[consumer_id]["route_id"])
            self.assertIn(installer.EDGE_CONSUMERS[consumer_id]["profile"], section)
        for field in ("failure_code", "failed_predicate", "required_evidence_or_repair",
                      "retry_entrypoint", "owning_existing_goal", "next_attempt"):
            self.assertIn("- " + field + ":", section)

    def test_every_declared_route_is_published_and_installed(self):
        for row in installer.EDGE_CONSUMERS.values():
            if row["route_id"] is not None:
                self.assertTrue(PUBLISHED_ROUTES[row["route_id"]]["runtime_installed"])

    def test_route_refusals_are_deny(self):
        cases = (
            (install_request(consumer_id="nope"), "EDGE_CONSUMER_NOT_DECLARED"),
            (install_request(route={**stegbrowser_route(), "route_id": "stegverse.route.unpublished.v1"}),
             "ROUTE_DECLARATION_NOT_RESOLVED"),
            (install_request(route={**stegbrowser_route(), "containment": "OTHER"}),
             "ROUTE_DECLARATION_NOT_RESOLVED"),
            (install_request(route={field: PUBLISHED_ROUTES["stegverse.route.hil-intake.v1"][field]
                                    for field in _ROUTE_FIELDS}), "ROUTE_SUBSTITUTION_REFUSED"),
            (install_request(router={"path": "workers/second_listener.py",
                                     "predecessor_sha256": installer.sha256_uri(ROUTER.encode())}),
             "ROUTER_NOT_THE_SHARED_UNIVERSAL_INTR_INGRESS"),
            ({"schema": "other"}, "INSTALLATION_REQUEST_ABSENT"),
        )
        for request, code in cases:
            self.assertNonAllow(installer.evaluate_installation(request, ROUTER.encode()), "DENY", code)

    def test_unpublished_runtime_is_deny(self):
        with mock.patch.dict(PUBLISHED_ROUTES, {STEGBROWSER_ROUTE_ID: {
                **PUBLISHED_ROUTES[STEGBROWSER_ROUTE_ID], "runtime_installed": False}}):
            result = installer.evaluate_installation(install_request(), ROUTER.encode())
        self.assertNonAllow(result, "DENY", "ROUTE_DECLARATION_NOT_RESOLVED")

    def test_predecessor_mismatch_and_anchor_drift_fail_closed(self):
        result = installer.evaluate_installation(
            install_request(router={"path": installer.DEFAULT_ROUTER, "predecessor_sha256": "sha256:" + "0" * 64}),
            ROUTER.encode())
        self.assertNonAllow(result, "FAIL_CLOSED", "ROUTER_PREDECESSOR_DIGEST_MISMATCH")
        drifted = ROUTER.replace("import serve_hil_intr_materialization_ingress as hil", "import hil")
        request = install_request(router={"path": installer.DEFAULT_ROUTER,
                                          "predecessor_sha256": installer.sha256_uri(drifted.encode())})
        self.assertNonAllow(installer.evaluate_installation(request, drifted.encode()),
                            "FAIL_CLOSED", "ROUTER_ANCHOR_DRIFT")

    def test_nothing_binds_a_socket(self):
        with mock.patch.object(socket.socket, "bind", side_effect=AssertionError("bound")), \
                mock.patch.object(socket.socket, "listen", side_effect=AssertionError("listening")):
            installer.evaluate_installation(install_request(), ROUTER.encode())
            with tempfile.TemporaryDirectory() as td:
                root = self._org_root(td)
                installer.admit_edge_submission({"manifest": stegbrowser_manifest(), "hb_epoch": "40"},
                                                consumer_id="stegbrowser", organization_root=root)

    def test_cli_never_writes_over_the_router(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._org_root(td)
            router = root / installer.DEFAULT_ROUTER
            router.parent.mkdir(parents=True)
            router.write_text(ROUTER, encoding="utf-8")
            request = Path(td) / "request.json"
            request.write_text(json.dumps(install_request()), encoding="utf-8")
            with self.assertRaises(SystemExit):
                installer.main(["evaluate-installation", "--request", str(request),
                                "--organization-root", str(root), "--successor-out", str(router)])
            self.assertEqual(ROUTER, router.read_text(encoding="utf-8"))
            out = Path(td) / "successor.py"
            with mock.patch("sys.stdout"):
                code = installer.main(["evaluate-installation", "--request", str(request),
                                       "--organization-root", str(root), "--successor-out", str(out)])
            self.assertEqual(0, code)
            self.assertEqual(installer.transform_router(ROUTER, "stegbrowser"), out.read_text(encoding="utf-8"))
            self.assertEqual(ROUTER, router.read_text(encoding="utf-8"))

    @staticmethod
    def _org_root(td):
        root = Path(td) / "org"
        (root / "org-runtime").mkdir(parents=True)
        (root / installer.BOUNDARY_DOCUMENT).write_text(json.dumps(BOUNDARY), encoding="utf-8")
        return root


class EdgeSubmissionTests(Base):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = InstallationTests._org_root(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def admit(self, payload, consumer_id="stegbrowser"):
        return installer.admit_edge_submission(payload, consumer_id=consumer_id, organization_root=self.root)

    def test_allow_addresses_the_organizations_own_manifest_ingress(self):
        manifest = stegbrowser_manifest()
        payload = {"manifest": manifest, "hb_epoch": "40"}
        self.assertTrue(installer.is_edge_submission(payload, consumer_id="stegbrowser"))
        result = self.admit(payload)
        self.assertEqual("ALLOW", result["disposition"], result)
        self.assertEqual("StegVerse-Labs", result["organization"])
        submission = result["submission"]
        self.assertEqual("stegverse-labs.sdk-manifest-ingress", submission["addressed_service"])
        self.assertEqual("SUBMIT_MANIFEST", submission["operation"])
        self.assertEqual(installer.sha256_uri(installer._canon(manifest)), submission["payload"]["manifest_sha256"])
        self.assertFalse(result["receipt_claimed"])

    def test_payload_cannot_choose_the_destination(self):
        result = self.admit({"manifest": stegbrowser_manifest(), "hb_epoch": "40",
                             "addressed_service": "elsewhere.sdk-manifest-ingress"})
        self.assertEqual("stegverse-labs.sdk-manifest-ingress", result["submission"]["addressed_service"])

    def test_raw_payload_without_a_manifest_is_deny(self):
        self.assertNonAllow(self.admit({"edge_consumer": "stegbrowser", "hb_epoch": "40"}),
                            "DENY", "INGRESS_WITHOUT_MANIFEST_DISPOSITION")

    def test_missing_epoch_fails_closed(self):
        self.assertNonAllow(self.admit({"manifest": stegbrowser_manifest()}), "FAIL_CLOSED", "HB_EPOCH_NOT_SUPPLIED")

    def test_unpublished_consumer_fails_closed(self):
        self.assertNonAllow(self.admit({"manifest": stegbrowser_manifest(), "hb_epoch": "40"}, "kv_ai_memory"),
                            "FAIL_CLOSED", "EDGE_CONSUMER_ROUTE_NOT_PUBLISHED")

    def test_invalid_manifest_is_deny(self):
        self.assertNonAllow(self.admit({"manifest": {"manifest_profile": "x"}, "hb_epoch": "40"}),
                            "DENY", "MANIFEST_NOT_ADMISSIBLE")

    def test_absent_manifest_ingress_binding_fails_closed(self):
        (self.root / installer.BOUNDARY_DOCUMENT).write_text(json.dumps({"organization": "X"}), encoding="utf-8")
        self.assertNonAllow(self.admit({"manifest": stegbrowser_manifest(), "hb_epoch": "40"}),
                            "FAIL_CLOSED", "MANIFEST_INGRESS_NOT_DECLARED")


def evaluation(**overrides):
    value = {"schema": installer.CONFORMANCE_RESULT_SCHEMA, "organization": "SV-LLM",
             "target_role_version_id": "org-role-next", "target_contract_digest": "sha256:" + "1" * 64,
             "disposition": "FAIL_CLOSED", "failed_predicate": installer.PARITY_PREDICATE,
             "required_evidence_or_repair": "adopt", "differing_files": []}
    value.update(overrides)
    return value


class RoleVersionTests(Base):
    def test_entry_and_digest_match_the_conformance_evaluator_form(self):
        raw = b"print('x')\n"
        entry = installer.role_version_file_entry("scripts/x.py", raw)
        self.assertEqual({"path": "scripts/x.py", "blob_sha": hashlib.sha1(b"blob 11\0" + raw).hexdigest(),
                          "byte_count": 11, "contract_digest": "sha256:" + hashlib.sha256(raw).hexdigest()}, entry)
        extended = installer.extend_role_version_files([], [entry])
        expected = "sha256:" + hashlib.sha256(json.dumps([entry], sort_keys=True, separators=(",", ":"))
                                              .encode("utf-8")).hexdigest()
        self.assertEqual(expected, extended["contract_digest"])
        with self.assertRaises(ValueError):
            installer.extend_role_version_files([entry], [entry])
        with self.assertRaises(ValueError):
            installer.role_version_file_entry("../x.py", raw)

    def test_readoption_after_allow_deny_and_parity(self):
        self.assertEqual("ALLOW", installer.plan_readoption(evaluation(disposition="ALLOW"))["disposition"])
        self.assertNonAllow(installer.plan_readoption(evaluation(disposition="DENY", failed_predicate="P")),
                            "DENY", "CONFORMANCE_REQUEST_DEFECT_NOT_REPAIRED_BY_ADOPTION")
        self.assertNonAllow(installer.plan_readoption(evaluation(failed_predicate="OTHER")),
                            "FAIL_CLOSED", "CONFORMANCE_FAIL_CLOSED_NOT_PARITY")
        self.assertNonAllow(installer.plan_readoption({"schema": "x"}), "DENY", "CONFORMANCE_EVALUATION_ABSENT")

    def test_readoption_preserves_organization_specific_changes(self):
        old = {"contract_digest": "sha256:" + "2" * 64, "blob_sha": "b" * 40, "byte_count": 3}
        own = {"contract_digest": "sha256:" + "3" * 64, "blob_sha": "c" * 40, "byte_count": 4}
        new = {"contract_digest": "sha256:" + "4" * 64, "blob_sha": "d" * 40, "byte_count": 5}
        rows = [{"path": "a.py", "recorded": new, "observed": "ABSENT"},
                {"path": "b.py", "recorded": new, "observed": old}]
        prior = [{"path": "b.py", **old}]
        plan = installer.plan_readoption(evaluation(differing_files=rows), predecessor_files=prior)
        self.assertEqual("ALLOW", plan["disposition"])
        self.assertEqual(["a.py", "b.py"], [step["path"] for step in plan["readopt"]])
        self.assertFalse(plan["source_mutated"])
        rows.append({"path": "c.py", "recorded": new, "observed": own})
        plan = installer.plan_readoption(evaluation(differing_files=rows), predecessor_files=prior)
        self.assertNonAllow(plan, "FAIL_CLOSED", "ORG_SPECIFIC_BEHAVIOUR_UNRECONCILED")
        self.assertEqual(["c.py"], [step["path"] for step in plan["unreconciled"]])
        self.assertEqual("STEGDB-ORGANIZATION-ROLE-VERSION-PROPAGATION-002", plan["owning_existing_goal"])


if __name__ == "__main__":
    unittest.main()
