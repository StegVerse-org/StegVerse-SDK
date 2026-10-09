"""stegverse.route.organization-role-conformance.v1 is a published route.

Real route resolution, manifest validation, Manifest Builder and runtime
derivation; nothing is mocked. The conformance request rides
``extensions.stegverse_organization_role_conformance_request`` beside the
``extensions.stegverse_route`` declaration and is never a top-level field.
Source validation only. No authority effect is claimed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request
from stegverse.organization_role_conformance_processor import (
    PROCESSING_CAPABILITY,
    REQUEST_EXTENSION,
    REQUEST_SCHEMA,
    validate_organization_role_conformance_request,
)
from stegverse.route_resolution import (
    ECOSYSTEM_DIAGNOSTIC_ROUTE_ID,
    ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID,
    PUBLISHED_ROUTES,
    _ROUTE_FIELDS,
    resolve_route_declaration,
    route_from_manifest,
    validate_runtime_provenance,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "inspection" / "examples"
REQUEST = json.loads(
    (EXAMPLES / "sdk-organization-role-conformance.processor-request.json").read_text(encoding="utf-8")
)

#: Every route published before this one, with its declaration hash. The whole
#: pre-existing table hashes to PRE_EXISTING_ROUTES_SHA256 at be6352d.
PRE_EXISTING_ROUTE_HASHES = {
    "stegverse.route.stegbrowser.v1": "db36dde96bf309dea28a3774931cbffb925428d49c22d327067330622160503f",
    "stegverse.route.svg-governance-cycle.v1": "ca2d18d0499a890f4236cf1c12c4e825878007db7d6f5e28c469cf3c4b6af7d6",
    "stegverse.route.shwp-sovereign-inference.v1": "5e473017da1569440a5917eb6e9faeba97bb4220c90954ff2abd311dd1e477ea",
    "stegverse.route.source-native-math.v1": "7942f2037db143091883bcb176874a1fdaa9f624f4abbb7c37ee7b6699a7c624",
    "stegverse.route.customer-local-governed.v1": "a33a92da8bfec67ba30ded1b6ed9040b53fb6869f59626785dd0aafca4cf3b53",
    "stegverse.route.canonical-governed.v1": "38ebd0b634a30d0397558dadac7a737694854aa336d0bd7d0c61049d7c61cff0",
    "stegverse.route.ecosystem-diagnostic.v1": "3cc2d8e14e6c770dd745ad8be4b6d125845f36cfa67fc6cb92164d3a229c88f8",
    "stegverse.route.purpose-bound-worker.v1": "d26ef5e0a322c9d7ad06e15ed57e77bcfe5b4038636076c37f0188f18aa36b2a",
    "stegverse.route.atomic-task-worker.v1": "9d42074cc4f1407453fa9416f040e6dfc5656d0ff84a56549095b2af2ba44946",
}
PRE_EXISTING_ROUTES_SHA256 = "349eef31690afbac7958d3deb8142be0a09603bd7c23faa865ad182e7e0a27c9"
#: Published later by SDK#368 PR-4 (SDK-MANIFEST-COLLAB-INGRESS-CONFORMANCE-001).
COLLAB_INGRESS_ROUTE_IDS = {
    "stegverse.route.ecosystem-chat.v1",
    "stegverse.route.va-scoped-chat.v1",
    "stegverse.route.hil-intake.v1",
}


def conformance_route():
    return {field: PUBLISHED_ROUTES[ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID][field] for field in _ROUTE_FIELDS}


def conformance_manifest(request=None):
    return build_manifest(
        data={"source": "role-version-propagation"},
        processor_request=copy.deepcopy(REQUEST if request is None else request),
        source_framework="StegDB",
        source_output_id="role-conformance-1",
        process=PROCESSING_CAPABILITY,
        created_at="2026-10-09T00:00:00Z",
    )


class OrganizationRoleConformanceRouteTests(unittest.TestCase):
    # (a) ALLOW through extensions.stegverse_route
    def test_published_route_resolves_with_its_capability(self):
        resolved = resolve_route_declaration(conformance_route())
        self.assertEqual(ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID, resolved["route_id"])
        self.assertEqual("organization_role_conformance", resolved["processor_capability"])
        self.assertEqual("stegverse.manifest_state_transition_runtime.execute_manifest", resolved["runtime_binding"])
        self.assertEqual(
            "stegverse.organization_role_conformance_processor.derive_state_graph",
            resolved["state_graph_adapter_binding"],
        )
        self.assertTrue(resolved["route_recognized"])
        self.assertFalse(resolved["route_substitution_permitted"])
        self.assertFalse(resolved["route_selection_grants_authority"])

    def test_manifest_declaring_the_route_validates_and_derives(self):
        manifest = conformance_manifest()
        self.assertEqual(conformance_route(), manifest["extensions"]["stegverse_route"])
        self.assertEqual(REQUEST, manifest["extensions"][REQUEST_EXTENSION])
        self.assertNotIn("organization_role_conformance", manifest)
        canonical = validate_ingress_manifest(manifest)
        self.assertTrue(canonical["external_manifest_valid"])
        self.assertFalse(canonical["external_manifest_grants_authority"])
        self.assertEqual(ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID, route_from_manifest(canonical)["route_id"])

        request = derive_execution_request(manifest)
        self.assertEqual(ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID, request["route_id"])
        self.assertEqual(PROCESSING_CAPABILITY, request["processing_capability"])
        graph = request["state_graph"]
        self.assertEqual(REQUEST, graph["request"])
        self.assertEqual(REQUEST["issuer"]["owner_task_id"], request["canonical_task_id"])
        self.assertFalse(request["requires_workercoordinator_claim_fence"])
        self.assertFalse(graph["adapter_executes_lifecycle"])
        self.assertFalse(request["request_grants_authority"])

    def test_runtime_provenance_resolves_by_id_and_by_unique_legacy_tuple(self):
        route = conformance_route()
        expected = resolve_route_declaration(route)["route_declaration_hash"]
        by_id = validate_runtime_provenance(dict(route, processor_capability=PROCESSING_CAPABILITY,
                                                 route_declaration_hash=expected))
        self.assertEqual(ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID, by_id["route_id"])
        route.pop("route_id")
        self.assertEqual(ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID, validate_runtime_provenance(route)["route_id"])

    # (b) unknown or misspelled route id
    def test_misspelled_route_id_is_refused(self):
        route = conformance_route()
        route["route_id"] = "stegverse.route.organisation-role-conformance.v1"
        with self.assertRaisesRegex(ValueError, "unsupported manifest route"):
            resolve_route_declaration(route)
        manifest = conformance_manifest()
        manifest["extensions"]["stegverse_route"]["route_id"] = route["route_id"]
        manifest["processing"]["route_id"] = route["route_id"]
        canonical = validate_ingress_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "unsupported manifest route"):
            route_from_manifest(canonical)
        with self.assertRaisesRegex(ValueError, "unsupported manifest route"):
            derive_execution_request(manifest)

    def test_conflicting_route_tuple_is_refused(self):
        route = conformance_route()
        route["external_consequence_enabled"] = True
        with self.assertRaisesRegex(ValueError, "conflicts with published external_consequence_enabled"):
            resolve_route_declaration(route)

    # (c) the request as a top-level field
    def test_request_as_top_level_field_is_refused(self):
        manifest = conformance_manifest()
        manifest["organization_role_conformance"] = manifest["extensions"].pop(REQUEST_EXTENSION)
        with self.assertRaisesRegex(ValueError, "unknown top-level manifest fields: organization_role_conformance"):
            validate_ingress_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "unknown top-level manifest fields"):
            derive_execution_request(manifest)

    def test_route_without_the_request_extension_is_refused(self):
        manifest = conformance_manifest()
        manifest["extensions"].pop(REQUEST_EXTENSION)
        with self.assertRaisesRegex(ValueError, "processor_request must be an object"):
            derive_execution_request(manifest)

    def test_request_schema_and_shape_are_exact(self):
        for mutate, message in (
            (lambda r: r.update(schema="stegverse.organization-role-conformance-request/v2"), "schema must be"),
            (lambda r: r.update(disposition="ALLOW"), "unknown organization_role_conformance request fields"),
            (lambda r: r.update(issuer="StegVerse-Labs/StegDB"), "issuer must be an object"),
            (lambda r: r["issuer"].pop("owner_task_id"), "issuer.owner_task_id is required"),
            (lambda r: r.update(destination_organization=""), "destination_organization is required"),
            (lambda r: r.pop("target_role_version"), "target_role_version must be an object"),
        ):
            request = copy.deepcopy(REQUEST)
            mutate(request)
            with self.assertRaisesRegex(ValueError, message):
                validate_organization_role_conformance_request(request)
        self.assertEqual(REQUEST_SCHEMA, validate_organization_role_conformance_request(REQUEST)["schema"])

    # (d) capability mismatch
    def test_capability_mismatch_is_refused(self):
        manifest = conformance_manifest()
        manifest["processing"]["capability"] = "ecosystem_diagnostic"
        with self.assertRaisesRegex(ValueError, "does not select organization_role_conformance"):
            derive_execution_request(manifest)

        provenance = dict(conformance_route(), processor_capability="ecosystem_diagnostic")
        with self.assertRaisesRegex(ValueError, "processor_capability conflicts with resolved route"):
            validate_runtime_provenance(provenance)

        # The capability on another published route does not borrow that route.
        manifest = conformance_manifest()
        diagnostic = {field: PUBLISHED_ROUTES[ECOSYSTEM_DIAGNOSTIC_ROUTE_ID][field] for field in _ROUTE_FIELDS}
        manifest["extensions"]["stegverse_route"] = diagnostic
        manifest["processing"]["route_id"] = ECOSYSTEM_DIAGNOSTIC_ROUTE_ID
        with self.assertRaisesRegex(ValueError, "does not select ecosystem_diagnostic"):
            derive_execution_request(manifest)

    # (e) compatibility guard
    def test_every_pre_existing_route_resolves_unchanged(self):
        self.assertEqual(
            set(PRE_EXISTING_ROUTE_HASHES) | {ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID} | COLLAB_INGRESS_ROUTE_IDS,
            set(PUBLISHED_ROUTES),
        )
        before = {route_id: PUBLISHED_ROUTES[route_id] for route_id in PRE_EXISTING_ROUTE_HASHES}
        self.assertEqual(
            PRE_EXISTING_ROUTES_SHA256, hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
        )
        for route_id, route_hash in PRE_EXISTING_ROUTE_HASHES.items():
            declaration = {field: PUBLISHED_ROUTES[route_id][field] for field in _ROUTE_FIELDS}
            self.assertEqual(route_hash, resolve_route_declaration(declaration)["route_declaration_hash"])
            declaration.pop("route_id")
            self.assertEqual(route_id, validate_runtime_provenance(declaration)["route_id"])


if __name__ == "__main__":
    unittest.main()
