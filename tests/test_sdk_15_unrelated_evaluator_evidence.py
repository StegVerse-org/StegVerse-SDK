"""Independent SDK 1.5 source qualification for unrelated evaluator requirements.

These cases are source-only evidence packets, not authentic InTr dispositions.
"""
from stegverse.capability_inventory import qualify_requirements, installed_capability_inventory
from stegverse.manifest_plan import derive_execution_plan, verify_plan_lineage


def test_two_unrelated_evaluators_bind_distinct_exact_installed_routes():
    manifest = {"source": {"formula": "x + 1"}, "observation": {"target": "source-only"}}
    requirements = [
        {"requirement_id": "math", "capability_id": "native_source_math",
         "route_id": "stegverse.route.source-native-math.v1", "required_inputs": ["source"]},
        {"requirement_id": "diagnostic", "capability_id": "ecosystem_diagnostic",
         "route_id": "stegverse.route.ecosystem-diagnostic.v1", "required_inputs": ["observation"]},
    ]
    plan = derive_execution_plan(manifest, requirements)
    assert verify_plan_lineage(manifest, requirements, plan)
    math, diagnostic = plan["steps"]
    assert math["qualification_disposition"] == diagnostic["qualification_disposition"] == "SUPPORTED"
    assert math["adaptation"]["route_id"] != diagnostic["adaptation"]["route_id"]
    assert math["adaptation"]["bounded"] and diagnostic["adaptation"]["bounded"]
    assert plan["execution_authorized"] is False
    assert plan["runtime_execution_observed"] is False


def test_negative_controls_retain_distinct_failing_predicates():
    requirements = [
        {"requirement_id": "missing", "capability_id": "native_source_math",
         "required_inputs": ["missing_source"]},
        {"requirement_id": "unsupported", "capability_id": "unknown_evaluator"},
        {"requirement_id": "version", "capability_id": "ecosystem_diagnostic",
         "version_compatible": False},
        {"requirement_id": "probe", "capability_id": "native_source_math",
         "authentic_runtime_evidence_required": True},
    ]
    plan = derive_execution_plan({}, requirements)
    assert [step["qualification_disposition"] for step in plan["steps"]] == [
        "MISSING_INPUT", "UNSUPPORTED", "VERSION_INCOMPATIBLE", "PROBE_REQUIRED"
    ]
    assert [step["failed_predicate"] for step in plan["steps"]] == [
        "REQUIRED_INPUT_PRESENT", "CAPABILITY_INSTALLED",
        "REQUESTED_VERSION_COMPATIBLE", "AUTHENTIC_RUNTIME_EVIDENCE_OBSERVED"
    ]
    assert all(step["adaptation"] is None for step in plan["steps"])
    assert plan["steps"][-1]["runtime_probe_required"] is True
    assert plan["runtime_execution_observed"] is False


def test_wrong_route_never_substitutes_other_evaluator_route():
    result = qualify_requirements({}, [
        {"requirement_id": "cross-route", "capability_id": "native_source_math",
         "route_id": "stegverse.route.ecosystem-diagnostic.v1"}
    ])
    assert result["results"][0]["disposition"] == "UNSUPPORTED"
    assert result["results"][0]["failed_predicate"] == "EXACT_ROUTE_INSTALLED"
    assert result["route_substitution_permitted"] is False


def test_inventory_includes_both_unrelated_evaluator_capabilities():
    capabilities = {row["capability_id"] for row in installed_capability_inventory()}
    assert {"native_source_math", "ecosystem_diagnostic"} <= capabilities


def test_published_but_uninstalled_exact_route_fails_closed():
    from stegverse.route_resolution import PUBLISHED_ROUTES, NATIVE_SOURCE_MATH_ROUTE_ID
    route = PUBLISHED_ROUTES[NATIVE_SOURCE_MATH_ROUTE_ID]
    from unittest.mock import patch
    requirement = [{"requirement_id": "uninstalled", "capability_id": "native_source_math",
                    "route_id": NATIVE_SOURCE_MATH_ROUTE_ID}]
    with patch.dict(PUBLISHED_ROUTES, {NATIVE_SOURCE_MATH_ROUTE_ID: {**route, "runtime_installed": False}}):
        result = qualify_requirements({}, requirement)
        row = result["results"][0]
        assert row["disposition"] == "UNSUPPORTED"
        assert row["failed_predicate"] == "RUNTIME_BINDING_INSTALLED"
        assert row["matched"]["runtime_installed"] is False
        assert result["execution_authorized"] is False
        plan = derive_execution_plan({}, requirement)
        assert plan["steps"][0]["adaptation"] is None
        assert verify_plan_lineage({}, requirement, plan)
