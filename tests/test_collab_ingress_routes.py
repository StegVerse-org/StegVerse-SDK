"""SDK#368 PR-4: Ecosystem Chat, VA-scoped chat and HIL intake manifest routes.

Owner: SDK-MANIFEST-COLLAB-INGRESS-CONFORMANCE-001. Real route resolution,
Manifest Builder and runtime derivation; only the pinned organization boundary
read is replaced by its fixture so no network is touched. Source validation
only; no runtime observation is claimed.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from stegverse.capability_map import EVALUATOR_INVOCABLE, reconcile_capability_map
from stegverse.collab_ingress_processor import (
    DEFERRED_INGRESS,
    ECOSYSTEM_CHAT_REQUEST_EXTENSION,
    HIL_INTAKE_REQUEST_EXTENSION,
    OWNER_TASK_ID,
    VA_SCOPED_CHAT_REQUEST_EXTENSION,
)
from stegverse.manifest_builder import PROCESSOR_ROUTES, available_processors, build_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.manifest_plan import NOT_READY, qualify_manifest_readiness
from stegverse.manifest_state_transition_runtime import UNIVERSAL_RUNTIME_BINDING, derive_execution_request
from stegverse.route_resolution import (
    ECOSYSTEM_CHAT_ROUTE_ID,
    HIL_INTAKE_ROUTE_ID,
    PUBLISHED_ROUTES,
    VA_SCOPED_CHAT_ROUTE_ID,
    _ROUTE_FIELDS,
    resolve_route_declaration,
    validate_runtime_provenance,
)
from tests.test_manifest_destination_binding import ORGANIZATION_BOUNDARY

EXAMPLES = Path(__file__).resolve().parents[1] / "inspection" / "examples"
SOURCE = json.loads((EXAMPLES / "sdk-tt-shared-source.json").read_text(encoding="utf-8"))
CANONICAL_ENTRYPOINT = "stegverse.manifest_execution.execute_manifest"
BOUNDARY = "stegverse.manifest_execution._canonical_organization_boundary"
ROUTES = {
    "ecosystem_chat": (ECOSYSTEM_CHAT_ROUTE_ID, ECOSYSTEM_CHAT_REQUEST_EXTENSION, "sdk-ecosystem-chat.processor-request.json"),
    "va_scoped_chat": (VA_SCOPED_CHAT_ROUTE_ID, VA_SCOPED_CHAT_REQUEST_EXTENSION, "sdk-va-scoped-chat.processor-request.json"),
    "hil_intake": (HIL_INTAKE_ROUTE_ID, HIL_INTAKE_REQUEST_EXTENSION, "sdk-hil-intake.processor-request.json"),
}


def _request(capability):
    return json.loads((EXAMPLES / ROUTES[capability][2]).read_text(encoding="utf-8"))


def _build(capability, request=None):
    return build_manifest(
        data=SOURCE, source_framework="fixture-framework", source_output_id=f"{capability}-fixture",
        processor_request=request if request is not None else _request(capability), process=capability,
        created_at="2026-10-09T23:59:00Z",
    )


def _execute(manifest):
    with patch(BOUNDARY, return_value=ORGANIZATION_BOUNDARY), \
            patch("urllib.request.urlopen", side_effect=AssertionError("no network")), \
            patch("socket.create_connection", side_effect=AssertionError("no network")):
        return execute_manifest(manifest)


class PublishedRouteTests(unittest.TestCase):
    def test_routes_and_capabilities_are_published_on_the_universal_path(self):
        for capability, (route_id, _, _) in ROUTES.items():
            route = PUBLISHED_ROUTES[route_id]
            self.assertEqual(route["processor_capability"], capability)
            self.assertEqual(PROCESSOR_ROUTES[capability], route_id)
            self.assertIn(capability, available_processors())
            self.assertEqual(route["runtime_binding"], UNIVERSAL_RUNTIME_BINDING)
            self.assertEqual(route["routing_surface"], "EXISTING_UNIVERSAL_INTR")
            self.assertIs(route["external_consequence_enabled"], False)
            declaration = {field: route[field] for field in _ROUTE_FIELDS}
            self.assertEqual(resolve_route_declaration(declaration)["route_id"], route_id)
            declaration.pop("route_id")
            self.assertEqual(validate_runtime_provenance(declaration)["route_id"], route_id)

    def test_va_scope_is_policy_on_the_same_path_as_ecosystem_chat(self):
        chat, va = PUBLISHED_ROUTES[ECOSYSTEM_CHAT_ROUTE_ID], PUBLISHED_ROUTES[VA_SCOPED_CHAT_ROUTE_ID]
        for field in ("routing_surface", "containment", "runtime_binding", "state_graph_adapter_binding",
                      "sandbox_required", "external_consequence_enabled"):
            self.assertEqual(chat[field], va[field], field)

    def test_math_solver_and_wiki_are_deferred_not_published(self):
        self.assertEqual(set(DEFERRED_INGRESS), {"math_solver", "admissibility_wiki_requests"})
        published = {route["processor_capability"] for route in PUBLISHED_ROUTES.values()}
        for capability in DEFERRED_INGRESS:
            self.assertNotIn(capability, PROCESSOR_ROUTES)
            self.assertNotIn(capability, published)
            resolution = build_manifest(
                data=SOURCE, source_framework="fixture", source_output_id="deferred",
                processor_request={"schema": "x"}, process=capability,
            )
            self.assertEqual(resolution["state"], "CAPABILITY_DEVELOPMENT_REQUESTED")

    def test_capability_map_reports_routes_invocable(self):
        rows = {row["route_id"]: row for row in reconcile_capability_map()["rows"]}
        for route_id, _, _ in ROUTES.values():
            self.assertEqual(rows[route_id]["disposition"], EVALUATOR_INVOCABLE)


class ExecutionTests(unittest.TestCase):
    def test_each_route_dispatches_through_canonical_execute_manifest(self):
        for capability, (route_id, extension, _) in ROUTES.items():
            manifest = _build(capability)
            self.assertEqual(manifest["processing"], {"capability": capability, "route_id": route_id})
            self.assertEqual(manifest["extensions"][extension], _request(capability))
            self.assertNotIn(extension, manifest)
            result = _execute(manifest)
            self.assertEqual(result["disposition"], "ALLOW", capability)
            self.assertEqual(result["state"], "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF")
            lineage = result["manifest_lineage"]["run_manifest_request"]
            self.assertEqual(lineage["route_id"], route_id)
            self.assertEqual(lineage["runtime_binding"], UNIVERSAL_RUNTIME_BINDING)
            for key in ("receiver_contacted", "transport_performed_by_sdk", "consequence_committed"):
                self.assertIs(result[key], False)
            graph = derive_execution_request(manifest)["state_graph"]
            self.assertEqual(graph["owner_task_id"], OWNER_TASK_ID)
            self.assertIs(graph["adapter_executes_lifecycle"], False)
        self.assertEqual(execute_manifest.__module__ + "." + execute_manifest.__name__, CANONICAL_ENTRYPOINT)

    def test_out_of_scope_va_request_gets_governed_refusal(self):
        request = _request("va_scoped_chat")
        request["requested_topic"] = "payroll"
        result = _execute(_build("va_scoped_chat", request))
        self.assertEqual(result["disposition"], "DENY")
        self.assertIs(result["terminal"], True)
        self.assertEqual(result["failed_predicate"], "REQUESTED_TOPIC_WITHIN_MANIFEST_DECLARED_VA_SCOPE")
        self.assertEqual(result["evidence"]["policy_source"], "MANIFEST_DECLARED")
        self.assertEqual(result["evidence"]["requested_topic"], "payroll")
        self.assertNotIn("handoff_sha256", result)
        for key in ("receiver_contacted", "transport_performed_by_sdk", "consequence_committed"):
            self.assertIs(result[key], False)
        self.assertEqual(result["manifest_lineage"]["run_manifest_request"]["route_id"], VA_SCOPED_CHAT_ROUTE_ID)
        # The same request on general Ecosystem Chat carries no VA policy and is handed off.
        general = {k: v for k, v in request.items() if k != "va_scope"}
        general["schema"] = "stegverse.ecosystem-chat-request/v1"
        self.assertEqual(_execute(_build("ecosystem_chat", general))["disposition"], "ALLOW")

    def test_in_scope_va_request_records_its_scope_disposition(self):
        graph = derive_execution_request(_build("va_scoped_chat"))["state_graph"]
        self.assertEqual(graph["va_scope_disposition"]["disposition"], "ALLOW")
        self.assertNotIn("manifest_policy_refusal", graph)

    def test_hil_intake_never_decides(self):
        graph = derive_execution_request(_build("hil_intake"))["state_graph"]
        self.assertIs(graph["human_decision_required"], True)
        self.assertIs(graph["automated_consequence_permitted"], False)

    def test_malformed_requests_are_rejected_by_the_builder(self):
        cases = [
            ("ecosystem_chat", {**_request("ecosystem_chat"), "authority": "ALLOW"}, "unknown ecosystem_chat request fields"),
            ("ecosystem_chat", {**_request("ecosystem_chat"), "message": ""}, "message is required"),
            ("va_scoped_chat", {k: v for k, v in _request("va_scoped_chat").items() if k != "va_scope"}, "va_scope must be an object"),
            ("va_scoped_chat", {**_request("va_scoped_chat"), "va_scope": {**_request("va_scoped_chat")["va_scope"], "allowed_topics": []}}, "allowed_topics"),
            ("hil_intake", {**_request("hil_intake"), "schema": "other"}, "hil_intake request schema"),
        ]
        for capability, request, message in cases:
            with self.assertRaisesRegex(ValueError, message):
                _build(capability, request)

    def test_route_mismatch_is_refused(self):
        manifest = copy.deepcopy(_build("ecosystem_chat"))
        route = {field: PUBLISHED_ROUTES[HIL_INTAKE_ROUTE_ID][field] for field in _ROUTE_FIELDS}
        manifest["extensions"]["stegverse_route"] = route
        manifest["processing"]["route_id"] = HIL_INTAKE_ROUTE_ID
        with self.assertRaises(ValueError):
            derive_execution_request(manifest)

    def test_readiness_gate_applies_to_new_routes(self):
        qualification = qualify_manifest_readiness(_build("ecosystem_chat"), attempt_id="a-1")
        self.assertEqual(qualification["qualification"], NOT_READY)
        self.assertEqual(qualification["route_id"], ECOSYSTEM_CHAT_ROUTE_ID)
        self.assertIs(qualification["runtime_allow_claimed"], False)


if __name__ == "__main__":
    unittest.main()
