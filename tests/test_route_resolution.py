from __future__ import annotations

import unittest

from stegverse.route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    governance_state_hash,
    resolve_route_declaration,
    validate_runtime_provenance,
)


def canonical_route():
    return {
        "route_id": CANONICAL_PRODUCTION_ROUTE_ID,
        "lane_class": "PRODUCTION_VALIDATION",
        "routing_surface": "CANONICAL_PRODUCTION",
        "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
        "sandbox_required": False,
        "external_consequence_enabled": False,
    }


class Tests(unittest.TestCase):
    def test_explicit_published_route_resolves(self):
        resolved = resolve_route_declaration(canonical_route())
        self.assertEqual(CANONICAL_PRODUCTION_ROUTE_ID, resolved["route_id"])
        self.assertEqual("core_lite.default_validation_route", resolved["runtime_binding"])
        self.assertTrue(resolved["route_recognized"])
        self.assertFalse(resolved["route_substitution_permitted"])
        self.assertEqual(64, len(resolved["route_declaration_hash"]))

    def test_unknown_route_rejected(self):
        route = canonical_route()
        route["route_id"] = "stegverse.route.unknown.v1"
        with self.assertRaisesRegex(ValueError, "unsupported manifest route"):
            resolve_route_declaration(route)

    def test_conflicting_route_tuple_rejected(self):
        route = canonical_route()
        route["containment"] = "DEMO_REPOSITORY_CONTAINED"
        with self.assertRaisesRegex(ValueError, "conflicts with published containment"):
            resolve_route_declaration(route)

    def test_legacy_0a_tuple_resolves_only_by_exact_unique_match(self):
        route = canonical_route()
        route.pop("route_id")
        resolved = validate_runtime_provenance(route)
        self.assertEqual(CANONICAL_PRODUCTION_ROUTE_ID, resolved["route_id"])
        route["routing_surface"] = "DEMO_TEST_REPOSITORY"
        with self.assertRaisesRegex(ValueError, "exactly one published route"):
            validate_runtime_provenance(route)

    def test_bad_route_hash_rejected(self):
        provenance = canonical_route()
        provenance["route_declaration_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "does not match resolved route"):
            validate_runtime_provenance(provenance)

    def test_state_hash_changes_on_governance_state_not_declared_context(self):
        base = {
            "candidate": {"action": "inspect", "target": "fixture"},
            "judgment": {"refusal_available": True},
            "signal": {"uncertainty_state": "bounded"},
            "execution": {"policy_current": True},
            "capability": {"allowed": True},
            "continuity": {"required": False},
            "approval": {"required": False},
            "permission_present": True,
            "declared_context": {"source": "one"},
        }
        same_state = dict(base)
        same_state["declared_context"] = {"source": "two"}
        changed_state = dict(base)
        changed_state["execution"] = {"policy_current": False}
        self.assertEqual(governance_state_hash(base), governance_state_hash(same_state))
        self.assertNotEqual(governance_state_hash(base), governance_state_hash(changed_state))


if __name__ == "__main__":
    unittest.main()
