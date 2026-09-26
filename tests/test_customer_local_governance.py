"""Customer-local route source tests. Doubles do not establish customer authority."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from stegverse.customer_local_governance import (
    CustomerLocalRouteRefused, execute_manifest, execute_local_manifest,
)
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.route_resolution import (
    CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID, PUBLISHED_ROUTES,
    CANONICAL_PRODUCTION_ROUTE_ID, route_from_manifest,
)

FIXTURE = Path(__file__).resolve().parents[1] / (
    "inspection/examples/external-framework-generic-manifest.json"
)


def local_manifest():
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    route = PUBLISHED_ROUTES[CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID]
    value["processing"] = {
        "capability": "governance",
        "route_id": CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
    }
    value["extensions"]["stegverse_route"] = {
        key: route[key] for key in (
            "route_id", "lane_class", "routing_surface", "containment",
            "sandbox_required", "external_consequence_enabled",
        )
    }
    value.pop("completion", None)
    return value


class CustomerLocalRouteSourceTests(unittest.TestCase):
    def test_actual_installed_local_route_is_distinct_from_remote_intr(self):
        checked = validate_ingress_manifest(local_manifest())
        route = route_from_manifest(checked)
        self.assertTrue(route["route_recognized"])
        self.assertEqual(route["routing_surface"], "CUSTOMER_LOCAL")
        self.assertEqual(route["processor_capability"], "governance")
        self.assertEqual(
            route["runtime_binding"],
            "stegverse.customer_local_governance.execute_manifest",
        )
        self.assertEqual(
            PUBLISHED_ROUTES[CANONICAL_PRODUCTION_ROUTE_ID]["runtime_binding"],
            "stegverse.manifest_state_transition_runtime.execute_manifest",
        )

    def test_public_run_manifest_refuses_absent_customer_bindings(self):
        with self.assertRaisesRegex(CustomerLocalRouteRefused, "HOST_BINDINGS_REQUIRED"):
            execute_manifest(local_manifest())

    def test_local_route_requires_exact_declaration_and_no_remote_completion(self):
        manifest = local_manifest()
        manifest["processing"]["route_id"] = CANONICAL_PRODUCTION_ROUTE_ID
        with self.assertRaisesRegex(ValueError, "must match"):
            validate_ingress_manifest(manifest)
        manifest = local_manifest()
        manifest["completion"] = {
            "direction": "SOUTH",
            "initiator": {"class": "fixture", "ref": "fixture"},
            "publisher": {"stage": "PUBLISHER", "required": False,
                          "package_profile": "fixture"},
            "egress": {"final_stegverse_transition_surface": "InTr",
                       "transport": "INTERLOCK_INTR",
                       "far_side_transition_required": True},
        }
        with self.assertRaisesRegex(CustomerLocalRouteRefused, "FEDERATED_COMPLETION"):
            execute_manifest(manifest)

    def test_missing_or_rejected_customer_verifier_cannot_invoke_executor(self):
        changed = []
        manifest = local_manifest()
        kwargs = dict(
            authority_evidence={"fixture": True},
            precommit_recorder=lambda record: None,
            executor=lambda: changed.append("executed"),
            result_recorder=lambda result: None,
        )
        with self.assertRaisesRegex(CustomerLocalRouteRefused, "CALLBACKS_REQUIRED"):
            execute_local_manifest(
                manifest, authority_verifier=None, **kwargs,
            )
        with self.assertRaisesRegex(CustomerLocalRouteRefused, "AUTHORITY_NOT_ESTABLISHED"):
            execute_local_manifest(
                manifest, authority_verifier=lambda evidence, **_: {
                    "status": "missing", "target_binding": "wrong",
                }, **kwargs,
            )
        self.assertEqual(changed, [])

    def test_canonical_runtime_is_called_only_after_explicit_fixture_bindings(self):
        # Explicit doubles: this is not real StegCore or trusted customer standing.
        manifest = local_manifest()
        request = SimpleNamespace(
            candidate=SimpleNamespace(target=manifest["candidate"]["target"])
        )
        model = SimpleNamespace(model_validate=lambda value: request)
        calls = []
        def fake_runtime(candidate, executor, **kwargs):
            calls.append("canonical-runtime-double")
            kwargs["pre_execution_observer"]({"fixture": "precommit"})
            executor()
            return SimpleNamespace(
                status="executed",
                evaluation=SimpleNamespace(disposition="ALLOW",
                                           decision_state_hash="fixture"),
                executor_invoked=True, pre_state_hash="pre",
                post_state_hash="post", coherence_receipt=None,
            )
        fake_core = ModuleType("stegcore")
        fake_core.AdmissibilityRequest = model
        fake_runtime_module = ModuleType("stegcore.steggate_runtime")
        fake_runtime_module.governed_steggate_execute = fake_runtime
        with patch.dict(sys.modules, {
            "stegcore": fake_core,
            "stegcore.steggate_runtime": fake_runtime_module,
        }):
            result = execute_local_manifest(
                manifest,
                authority_evidence={"fixture_only": True},
                authority_verifier=lambda evidence, **_: {
                    "status": "valid",
                    "target_binding": manifest["candidate"]["target"],
                },
                precommit_recorder=lambda value: calls.append("precommit"),
                executor=lambda: calls.append("bounded-fixture-effect"),
                result_recorder=lambda value: calls.append("result-recorded"),
            )
        self.assertEqual(
            calls,
            ["canonical-runtime-double", "precommit",
             "bounded-fixture-effect", "result-recorded"],
        )
        self.assertEqual(result["authority_boundary"],
                         "CUSTOMER_LOCAL_NOT_STEGVERSE_MASTER_RECORDS")


if __name__ == "__main__":
    unittest.main()
