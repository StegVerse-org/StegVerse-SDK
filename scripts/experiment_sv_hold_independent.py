"""Independent SV HOLD qualification through the installed public SDK path.

This is the StegVerse side's independently authored experimental input. No ELAN
output, comparison result, fabricated grant or private runtime is consumed.
Source qualification and a real Universal InTr run are different evidence gates.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.manifest_state_transition_runtime import (
    INGRESS_URL_ENV, TRANSPORT_AUTHORIZATION_ENV, derive_execution_request,
)

EXPERIMENT_ID = "SV-HOLD-INDEPENDENT-BASELINE-20260926"
# Relative times are preregistered test positions, NOT observed wall-clock times.
CONDITIONS = (
    ("T0", "PRE_HOLD", True, True, True, True),
    ("T1", "HOLD_ENTERED", False, True, False, False),
    ("T2", "HOLD_PERSISTENCE_AFTER_TIME_ADVANCE", False, False, False, False),
    ("T3", "RESUME_PROPOSED_WITHOUT_FRESH_DELEGATION", True, True, False, True),
    ("T4", "RESUME_PROPOSED_WITH_NEW_DECLARED_DELEGATION", True, True, True, True),
)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def build_condition(row: tuple) -> tuple[dict, dict]:
    step, condition, actor_current, window_open, delegation_current, permission = row
    # These values are MANIFEST DECLARATIONS, not original attested authority.
    data = {
        "experiment_id": EXPERIMENT_ID,
        "evidence_class": "INDEPENDENT_SV_EXPERIMENT_DESIGN_NOT_NATIVE_RUNTIME",
        "condition_id": condition,
        "relative_time": step,
        "temporal_sampling": "EXPERIMENT_RELATIVE_ONLY_NOT_MEASURED",
        "protected_operation": "bounded_no_external_side_effect_test",
        "authority_declaration": {
            "actor_current": actor_current,
            "delegation_current": delegation_current,
            "permission_present": permission,
            "validity_window_open": window_open,
            "authenticated_grant_observed": False,
        },
        "native_stev_inference": None,
        "other_framework_output_consumed": False,
        "expected_evidence": [
            "actual_intr_admissibility_snapshot",
            "original_protected_operation_effect_or_prevention",
            "predecessor_linked_organization_receipts",
            "applicable_master_records_reconstruction",
        ],
    }
    input_hash = canonical_hash(data)
    evidence_ref = "sv-hold:source-design:" + input_hash
    request = {
        "candidate": {
            "actor_class": "sdk_evaluator",
            "action": "evaluate_bounded_hold_operation",
            "target": EXPERIMENT_ID + ":" + condition,
            "scope": "isolated_experiment",
            "parameters": {"external_side_effect": False, "relative_time": step},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": [evidence_ref],
        },
        "signal": {
            "admitted_signal_refs": [evidence_ref],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": ["authenticated_current_grant", "authentic_runtime_evidence"],
            "uncertainty_state": "unknown",
            "reference_state_hash": input_hash,
            "expected_reference_state_hash": input_hash,
            "reconstruction_available": False,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": actor_current,
            "policy_current": True,
            "delegation_current": delegation_current,
            "evidence_current": False,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": window_open,
            "policy_ref": "sv-hold:proposed-test-policy:not-runtime-authenticated",
            "delegation_ref": "sv-hold:proposed-test-delegation:not-runtime-authenticated",
            "evidence_refs": [evidence_ref],
        },
        "capability": {"allowed": True},
        "continuity": {"required": True},
        "approval": {"required": True},
        "permission_present": permission,
        "declared_context": {
            "source_only": True,
            "relative_time": step,
            "condition_id": condition,
            "no_external_effect": True,
            "authority_evidence_status": "NOT_AUTHENTICATED",
            "semantic_status": "UNRESOLVED",
            "other_framework_evidence_used": False,
        },
    }
    return data, request


def run(*, output_dir: Path, attempt_runtime: bool = True) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "type": "SV_INDEPENDENT_HOLD_SOURCE_QUALIFICATION",
        "other_framework_evidence_consumed": False,
        "live_execution_claim": False,
        "master_records_closure_claim": False,
        "conditions": [],
    }
    for row in CONDITIONS:
        data, request = build_condition(row)
        step, condition = row[0], row[1]
        manifest = build_manifest(
            data=data,
            processor_request=request,
            process="governance",
            source_framework="StegVerse-independent-evaluator",
            source_output_id=EXPERIMENT_ID + ":" + condition,
            data_class="sv.hold.independent.source-only.v1",
            return_depth="full-trace",
            created_at="2026-09-26T00:00:00Z",  # source fixture identity, NOT live invocation time
            declared_intent="Independently qualify a proposed governed HOLD transition",
            requested_consequence="Observe actual disposition and protected effect only if genuinely admitted",
            publisher_required=False,
        )
        canonical = validate_ingress_manifest(manifest)
        derived = derive_execution_request(manifest)
        assert canonical["payload"] == data
        assert derived["request_grants_authority"] is False
        assert derived["sdk_executes_lifecycle"] is False
        assert derived["canonical_manifest_sha256"] == canonical["canonical_manifest_sha256"]
        assert derived["state_graph"]["processing_capability"] == "governance"
        (output_dir / f"{step}-input.json").write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output_dir / f"{step}-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output_dir / f"{step}-derived-request.json").write_text(
            json.dumps(derived, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        trial = {
            "condition": condition,
            "relative_time": step,
            "canonical_manifest_sha256": canonical["canonical_manifest_sha256"],
            "derived_request_sha256": derived["request_sha256"],
            "source_validation": "PASS",
            "runtime_disposition": "NOT_ATTEMPTED",
            "actual_effect_observed": False,
            "master_records_reconstruction_observed": False,
        }
        if attempt_runtime:
            if os.environ.get(INGRESS_URL_ENV) and os.environ.get(TRANSPORT_AUTHORIZATION_ENV):
                # A generic CI workflow must not turn latent credentials into authority.
                trial["runtime_disposition"] = "REQUIRES_SEPARATELY_AUTHORIZED_LIVE_CALLER"
            else:
                try:
                    result = execute_manifest(manifest)
                except ValueError as exc:
                    trial["runtime_disposition"] = "SOURCE_LOCAL_EXECUTION_REFUSED"
                    trial["runtime_reason_code"] = str(exc)
                else:
                    # The SDK validates actual runtime responses; preserve original,
                    # do not invent consequences or use a self-assigned PASS marker.
                    (output_dir / f"{step}-runtime-response.json").write_text(
                        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                    )
                    trial["runtime_disposition"] = "RUNTIME_RESULT_RETURNED_REQUIRES_INDEPENDENT_READBACK"
        summary["conditions"].append(trial)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--skip-runtime-attempt", action="store_true")
    args = p.parse_args()
    result = run(
        output_dir=Path(args.output_dir),
        attempt_runtime=not args.skip_runtime_attempt,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
