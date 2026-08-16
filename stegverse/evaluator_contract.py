"""Public evaluator contract discovery for the installed StegVerse SDK.

This module is intentionally self-contained and non-authorizing. It exposes the
same public-inspection request vocabulary accepted by ``public_inspection.py`` so
an evaluator can discover the contract without browsing repository files first.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from .public_inspection import (
    REQUEST_PROFILES,
    REQUEST_SCHEMA_VERSION,
    RETURN_PROJECTIONS,
    SUPPORTED_EVALUATION_CAPABILITIES,
    SUPPORTED_EVIDENCE_CLASSES,
)


def evaluator_contract_schema() -> dict[str, Any]:
    """Return the evaluator-facing request contract as JSON Schema."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://stegverse.org/schemas/public-inspection-request.v1.json",
        "title": "StegVerse Public Inspection Request",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "request_id",
            "case_profile",
            "execution_provenance",
            "input",
            "return_projection",
            "authority_claim",
        ],
        "properties": {
            "schema_version": {"const": REQUEST_SCHEMA_VERSION},
            "request_id": {"type": "string", "pattern": "^[A-Za-z0-9._-]{3,80}$"},
            "requester_label": {"type": "string", "maxLength": 120},
            "case_profile": {"type": "string", "enum": sorted(REQUEST_PROFILES)},
            "evaluation_declaration": {
                "type": "object",
                "additionalProperties": False,
                "required": ["what", "how", "why"],
                "properties": {
                    "what": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "how": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "why": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "expected_observation": {"type": "string", "maxLength": 1000},
                    "requested_capabilities": {
                        "type": "array",
                        "uniqueItems": True,
                        "maxItems": 5,
                        "items": {"type": "string", "enum": sorted(SUPPORTED_EVALUATION_CAPABILITIES)},
                    },
                    "requested_evidence": {
                        "type": "array",
                        "uniqueItems": True,
                        "maxItems": 7,
                        "items": {"type": "string", "enum": sorted(SUPPORTED_EVIDENCE_CLASSES)},
                    },
                },
            },
            "execution_provenance": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "lane_class",
                    "routing_surface",
                    "containment",
                    "sandbox_required",
                    "external_consequence_enabled",
                ],
                "properties": {
                    "lane_class": {
                        "type": "string",
                        "enum": ["PRODUCTION_VALIDATION", "ENCLOSED_DEMO_TEST"],
                    },
                    "routing_surface": {
                        "type": "string",
                        "enum": ["CANONICAL_PRODUCTION", "DEMO_TEST_REPOSITORY"],
                    },
                    "containment": {
                        "type": "string",
                        "enum": ["PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE", "DEMO_REPOSITORY_CONTAINED"],
                    },
                    "sandbox_required": {"type": "boolean"},
                    "sandbox_tier": {"type": "string", "maxLength": 120},
                    "origin_surface": {"type": "string", "maxLength": 200},
                    "external_consequence_enabled": {"type": "boolean"},
                },
                "allOf": [
                    {
                        "if": {"properties": {"lane_class": {"const": "PRODUCTION_VALIDATION"}}},
                        "then": {
                            "properties": {
                                "routing_surface": {"const": "CANONICAL_PRODUCTION"},
                                "containment": {"const": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE"},
                                "external_consequence_enabled": {"const": False},
                            }
                        },
                    },
                    {
                        "if": {"properties": {"lane_class": {"const": "ENCLOSED_DEMO_TEST"}}},
                        "then": {
                            "properties": {
                                "routing_surface": {"const": "DEMO_TEST_REPOSITORY"},
                                "containment": {"const": "DEMO_REPOSITORY_CONTAINED"},
                                "sandbox_required": {"const": True},
                                "external_consequence_enabled": {"const": False},
                            }
                        },
                    },
                ],
            },
            "input": {"type": "object", "maxProperties": 50},
            "return_projection": {"type": "string", "enum": sorted(RETURN_PROJECTIONS)},
            "manifest_labels": {"type": "boolean", "default": False},
            "authority_claim": {"const": False},
            "notes": {"type": "string", "maxLength": 2000},
        },
    }


def evaluator_contract_example() -> dict[str, Any]:
    """Return a ready-to-edit evaluator request example."""
    return {
        "schema_version": "1.0",
        "request_id": "evaluator-test-001",
        "requester_label": "external-evaluator",
        "case_profile": "custom-declarative",
        "evaluation_declaration": {
            "what": "Describe exactly what you want evaluated.",
            "how": "Describe how the published capabilities should be exercised.",
            "why": "Describe why this evaluation is being performed.",
            "expected_observation": "Optional expected observation; this is not a decision input.",
            "requested_capabilities": [
                "commit_time_admissibility",
                "master_records_custody",
                "replay",
                "reconstruction",
            ],
            "requested_evidence": [
                "governance_decision",
                "manifest_receipt",
                "route_receipts",
                "exact_run_custody",
            ],
        },
        "execution_provenance": {
            "lane_class": "PRODUCTION_VALIDATION",
            "routing_surface": "CANONICAL_PRODUCTION",
            "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
            "sandbox_required": False,
            "sandbox_tier": "NONE",
            "origin_surface": "external-evaluator",
            "external_consequence_enabled": False,
        },
        "input": {
            "steggate_request": {
                "candidate": {
                    "actor_class": "ai",
                    "action": "replace-with-action",
                    "target": "replace-with-target",
                    "scope": "replace-with-scope",
                    "parameters": {},
                },
                "judgment": {
                    "refusal_available": True,
                    "operator_recoverability": "available",
                    "workload_state": "supported",
                    "time_pressure": "normal",
                    "isolation_state": "supported",
                    "evidence_refs": [],
                },
                "signal": {
                    "admitted_signal_refs": [],
                    "transformations": [],
                    "missing_inputs": [],
                    "uncertainty_state": "bounded",
                    "reference_state_hash": "replace-with-state-hash",
                    "expected_reference_state_hash": "replace-with-state-hash",
                    "reconstruction_available": True,
                    "transformation_provenance_complete": True,
                },
                "execution": {
                    "actor_authority_current": True,
                    "policy_current": True,
                    "delegation_current": True,
                    "evidence_current": True,
                    "affected_entity_conditions_represented": True,
                    "recoverability_profile": "recoverable",
                    "validity_window_open": True,
                    "policy_ref": "replace-with-policy-ref",
                    "delegation_ref": "replace-with-delegation-ref",
                    "evidence_refs": [],
                },
                "capability": {"allowed": True},
                "continuity": {"required": False, "previous_receipt_verified": False},
                "approval": {"required": False},
                "permission_present": False,
            },
            "input_data": {},
        },
        "return_projection": "ALL",
        "manifest_labels": True,
        "authority_claim": False,
        "notes": "Evaluator-authored request. Purpose and expectation do not become authority.",
    }


def evaluator_contract_summary() -> dict[str, Any]:
    return {
        "contract": "stegverse.public-inspection-request.v1",
        "schema_version": REQUEST_SCHEMA_VERSION,
        "submission": "stegverse governance --select 0 --input <request.json>",
        "direct_runtime": "python -m stegverse.public_inspection_runtime run <request.json>",
        "schema_command": "stegverse contract --schema",
        "example_command": "stegverse contract --example",
        "capabilities": sorted(SUPPORTED_EVALUATION_CAPABILITIES),
        "evidence_classes": sorted(SUPPORTED_EVIDENCE_CLASSES),
        "authority_effect": "NONE",
        "configuration_not_augmentation": True,
        "evaluator_identity_is_decision_input": False,
        "expected_observation_is_decision_input": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse contract",
        description="Inspect the public evaluator request contract",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--schema", action="store_true", help="print the machine-readable request JSON Schema")
    mode.add_argument("--example", action="store_true", help="print a ready-to-edit evaluator request example")
    mode.add_argument("--all", action="store_true", help="print summary, schema, and example together")
    args = parser.parse_args(argv)

    if args.schema:
        payload: Any = evaluator_contract_schema()
    elif args.example:
        payload = evaluator_contract_example()
    elif args.all:
        payload = {
            "summary": evaluator_contract_summary(),
            "schema": evaluator_contract_schema(),
            "example": evaluator_contract_example(),
        }
    else:
        payload = evaluator_contract_summary()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
