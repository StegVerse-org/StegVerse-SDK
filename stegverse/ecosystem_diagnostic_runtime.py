"""Read-only SDK runtime for manifested ecosystem diagnostic requests.

This processor standardizes diagnostic transport and result semantics. It does not
calculate ecosystem continuity, perform repair, acquire credentials, call providers,
or grant execution/transition authority. Missing observations remain NOT_OBSERVED.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import route_from_manifest

PROCESSING_CAPABILITY = "ecosystem_diagnostic"
ROUTE_ID = "stegverse.route.ecosystem-diagnostic.v1"
REQUEST_SCHEMA = "stegverse.ecosystem-diagnostic-request.v1"
RESULT_SCHEMA = "stegverse.ecosystem-diagnostic-result.v1"
REQUEST_EXTENSION = "stegverse_ecosystem_diagnostic_request"
AUTHORITY_EFFECT = "NONE_DIAGNOSTIC_ONLY"
OBSERVATION_STATES = {
    "PASS", "FAIL", "DEGRADED", "UNKNOWN", "NOT_OBSERVED", "STALE", "UNREACHABLE", "PROBE_REQUIRED"
}
SCOPES = {"component", "repository", "runtime", "ecosystem"}


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


def validate_diagnostic_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("ecosystem diagnostic processor_request must be an object")
    if value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"diagnostic request schema must be {REQUEST_SCHEMA}")
    request_id = _require_text(value.get("diagnostic_request_id"), "diagnostic_request_id")
    scope = value.get("scope")
    if scope not in SCOPES:
        raise ValueError("diagnostic request scope is unsupported")
    if value.get("mutation_permitted") is not False:
        raise ValueError("ecosystem diagnostic v1 requires mutation_permitted=false")
    tests = value.get("tests")
    if not isinstance(tests, list) or not tests:
        raise ValueError("diagnostic request tests must be a non-empty array")
    expected = value.get("expected_evidence_fields", [])
    if not isinstance(expected, list) or not all(isinstance(x, str) and x.strip() for x in expected):
        raise ValueError("expected_evidence_fields must be an array of non-empty strings")

    normalized_tests: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in tests:
        if not isinstance(row, Mapping):
            raise ValueError("diagnostic test entries must be objects")
        test_id = _require_text(row.get("test_id"), "test_id")
        if test_id in seen:
            raise ValueError(f"duplicate diagnostic test_id: {test_id}")
        seen.add(test_id)
        item = {
            "test_id": test_id,
            "component_id": _require_text(row.get("component_id"), "component_id"),
            "predicate_id": _require_text(row.get("predicate_id"), "predicate_id"),
            "authority_owner": _require_text(row.get("authority_owner"), "authority_owner"),
            "observation": deepcopy(row.get("observation")),
        }
        observation = item["observation"]
        if observation is not None:
            if not isinstance(observation, Mapping):
                raise ValueError(f"diagnostic observation for {test_id} must be an object or null")
            state = observation.get("state")
            if state not in OBSERVATION_STATES:
                raise ValueError(f"diagnostic observation state for {test_id} is unsupported")
            refs = observation.get("evidence_refs", [])
            if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
                raise ValueError(f"diagnostic evidence_refs for {test_id} must be strings")
            age = observation.get("evidence_age_seconds")
            if age is not None and (not isinstance(age, int) or age < 0):
                raise ValueError(f"diagnostic evidence_age_seconds for {test_id} must be non-negative")
        normalized_tests.append(item)

    return {
        "schema": REQUEST_SCHEMA,
        "diagnostic_request_id": request_id,
        "scope": scope,
        "mutation_permitted": False,
        "expected_evidence_fields": list(dict.fromkeys(x.strip() for x in expected)),
        "tests": normalized_tests,
    }


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    processing = canonical["processing"]
    if processing.get("capability") != PROCESSING_CAPABILITY:
        raise ValueError("manifest processing capability does not select ecosystem_diagnostic")
    resolved_route = route_from_manifest(canonical)
    if resolved_route.get("route_id") != ROUTE_ID:
        raise ValueError("ecosystem diagnostic manifest resolved to the wrong route")
    if resolved_route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("ecosystem diagnostic route processor binding mismatch")
    if resolved_route.get("runtime_binding") != "stegverse.ecosystem_diagnostic_runtime.execute_manifest":
        raise ValueError("ecosystem diagnostic runtime binding is unavailable")

    extensions = canonical.get("extensions") or {}
    request = validate_diagnostic_request(extensions.get(REQUEST_EXTENSION))
    expected_fields = request["expected_evidence_fields"]
    results: list[dict[str, Any]] = []
    for test in request["tests"]:
        observation = test.get("observation")
        if observation is None:
            state = "NOT_OBSERVED"
            observed_at = None
            refs: list[str] = []
            age = None
            detail = None
        else:
            state = observation.get("state")
            observed_at = observation.get("observed_at")
            refs = list(observation.get("evidence_refs") or [])
            age = observation.get("evidence_age_seconds")
            detail = observation.get("detail")
            # Pre-registered evidence expectations fail closed when a claimed
            # observation carries no evidence references. The processor does not
            # invent evidence or reinterpret the requested predicate.
            if expected_fields and state in {"PASS", "FAIL", "DEGRADED", "STALE", "UNREACHABLE"} and not refs:
                state = "PROBE_REQUIRED"
                detail = "Pre-registered evidence fields require authentic evidence references before this observation can be used."
        results.append({
            "test_id": test["test_id"],
            "component_id": test["component_id"],
            "predicate_id": test["predicate_id"],
            "observation_state": state,
            "observed_at": observed_at,
            "evidence_refs": refs,
            "evidence_age_seconds": age,
            "authority_owner": test["authority_owner"],
            "detail": detail,
            "mutation_performed": False,
        })

    return {
        "schema": RESULT_SCHEMA,
        "diagnostic_request_id": request["diagnostic_request_id"],
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "scope": request["scope"],
        "results": results,
        "mutation_performed": False,
        "authority_effect": AUTHORITY_EFFECT,
        "continuity_state_present": False,
    }


__all__ = [
    "AUTHORITY_EFFECT", "PROCESSING_CAPABILITY", "REQUEST_EXTENSION", "REQUEST_SCHEMA",
    "RESULT_SCHEMA", "ROUTE_ID", "execute_manifest", "validate_diagnostic_request",
]
