from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .portable_governance_verifier import verify_portable_governance_bundle
from .post_return_evidence import complete_post_return_evidence
from .proof_release_gate import verify_release_proof_capabilities
from .public_inspection import load_public_inspection_request, validate_public_inspection_request
from .reference_bounded_consequence import reference_state_executor
from .sovereign_validation_runtime import (
    _components,
    reconstruct_sovereign,
    replay_sovereign,
    run_sovereign_validation,
)
from .spe_steggate_bridge import stable_hash
from .standing_execution_context import build_standing_execution_context

PROOF_RUNNER_SCHEMA = "stegverse.sdk.post-return-production-runner-result.v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _load_object(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    value = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{target} must contain a JSON object")
    return value


def _write_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_coherent_release_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Independently verify the aggregate receipt shape, hash, and proof capabilities."""
    value = dict(receipt)
    reasons: list[str] = []
    if value.get("schema") != "stegverse.tvc.aggregate-release-receipt.v1":
        reasons.append("aggregate_release_schema_invalid")
    release_set_id = str(value.get("release_set_id") or "").strip()
    if not release_set_id:
        reasons.append("release_set_id_missing")
    if value.get("credential_authority") != "TV/TVC":
        reasons.append("credential_authority_not_tv_tvc")
    if value.get("non_tv_tvc_credential_used") is not False:
        reasons.append("non_tv_tvc_credential_boundary_invalid")
    components = value.get("components")
    if not isinstance(components, list) or not components:
        reasons.append("release_components_missing")
    else:
        for index, component in enumerate(components):
            if not isinstance(component, Mapping):
                reasons.append(f"component_{index}_not_object")
                continue
            if not str(component.get("repository") or "").strip():
                reasons.append(f"component_{index}_repository_missing")
            if not str(component.get("tag") or "").strip():
                reasons.append(f"component_{index}_tag_missing")
            commit_sha = str(component.get("commit_sha") or "").strip().lower()
            if len(commit_sha) != 40 or any(c not in "0123456789abcdef" for c in commit_sha):
                reasons.append(f"component_{index}_commit_sha_invalid")

    claimed_hash = str(value.get("receipt_hash") or "").strip().lower()
    body = dict(value)
    body.pop("receipt_hash", None)
    expected_hash = _sha256(body)
    if claimed_hash != expected_hash:
        reasons.append("aggregate_receipt_hash_mismatch")

    capability = verify_release_proof_capabilities(value)
    if capability.get("verified") is not True:
        reasons.append("release_proof_capabilities_not_verified")

    return {
        "verified": not reasons,
        "reasons": reasons or ["ok"],
        "release_set_id": release_set_id or None,
        "receipt_hash": claimed_hash or None,
        "proof_capabilities": capability,
        "authority_effect": "NONE",
    }


def derive_three_layer_request(admissibility_request: Mapping[str, Any]) -> dict[str, Any]:
    """Project an AdmissibilityRequest into canonical StegCore three-layer semantics."""
    request = dict(admissibility_request)
    candidate = request.get("candidate")
    judgment = request.get("judgment")
    signal = request.get("signal")
    execution = request.get("execution")
    if not all(isinstance(item, Mapping) for item in (candidate, judgment, signal, execution)):
        raise ValueError("admissibility request is missing candidate/judgment/signal/execution objects")
    candidate = dict(candidate)
    judgment = dict(judgment)
    signal = dict(signal)
    execution = dict(execution)

    action = str(candidate.get("action") or "").strip()
    target = str(candidate.get("target") or "").strip()
    scope = str(candidate.get("scope") or "default").strip()
    if not action or not target or not scope:
        raise ValueError("candidate action/target/scope are required")

    return {
        "judgment_conditions": {
            "refusal_available": bool(judgment.get("refusal_available")),
            "operator_recoverability": judgment.get("operator_recoverability") or "unknown",
            "workload_state": judgment.get("workload_state") or "unknown",
            "time_pressure": judgment.get("time_pressure") or "unknown",
            "isolation_state": judgment.get("isolation_state") or "unknown",
            "evidence_refs": list(judgment.get("evidence_refs") or []),
        },
        "signal_admission": {
            "admitted_signal_refs": list(signal.get("admitted_signal_refs") or []),
            "excluded_signal_refs": list(signal.get("excluded_signal_refs") or []),
            "transformations": list(signal.get("transformations") or []),
            "missing_inputs": list(signal.get("missing_inputs") or []),
            "uncertainty_state": signal.get("uncertainty_state") or "unknown",
            "reference_state_hash": signal.get("reference_state_hash") or "",
            "expected_reference_state_hash": signal.get("expected_reference_state_hash") or "",
            "reconstruction_available": bool(signal.get("reconstruction_available")),
            "transformation_provenance_complete": bool(signal.get("transformation_provenance_complete")),
        },
        "execution_boundary": {
            "actor_authority_current": bool(execution.get("actor_authority_current")),
            "policy_current": bool(execution.get("policy_current")),
            "delegation_current": bool(execution.get("delegation_current")),
            "evidence_current": bool(execution.get("evidence_current")),
            "affected_entity_conditions_represented": bool(execution.get("affected_entity_conditions_represented")),
            "recoverability_profile": execution.get("recoverability_profile") or "unknown",
            "validity_window_open": bool(execution.get("validity_window_open")),
            "policy_ref": execution.get("policy_ref") or "",
            "delegation_ref": execution.get("delegation_ref") or "",
            "evidence_refs": list(execution.get("evidence_refs") or []),
        },
        "action": action,
        "target": target,
        "scope": scope,
    }


def verify_manifest_standing_proposition_binding(
    normalized_manifest: Mapping[str, Any],
    pre_steggate_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    input_block = normalized_manifest.get("input")
    if not isinstance(input_block, Mapping):
        raise ValueError("normalized manifest input is required")
    raw_request = input_block.get("steggate_request")
    if not isinstance(raw_request, Mapping):
        raise ValueError("normalized manifest input.steggate_request is required")

    bridge = pre_steggate_bundle.get("steggate_bridge")
    if not isinstance(bridge, Mapping):
        raise ValueError("PRE_STEGGATE bundle has no bridge")
    admissibility = bridge.get("admissibility_candidate")
    if not isinstance(admissibility, Mapping):
        raise ValueError("PRE_STEGGATE bridge has no admissibility candidate")
    bridge_request = admissibility.get("three_layer_request")
    if not isinstance(bridge_request, Mapping):
        raise ValueError("PRE_STEGGATE bridge has no three-layer request")

    derived = derive_three_layer_request(raw_request)
    derived_hash = stable_hash(derived)
    claimed_hash = str(admissibility.get("three_layer_request_hash") or "")
    if derived_hash != claimed_hash:
        raise ValueError("manifest governance request does not match PRE_STEGGATE three-layer request hash")
    if dict(bridge_request) != derived:
        raise ValueError("manifest governance request does not equal PRE_STEGGATE three-layer proposition")
    return {
        "verified": True,
        "three_layer_request_hash": derived_hash,
        "authority_effect": "NONE",
    }


def _custody_record(custody_db: str | Path, manifest_receipt_id: str) -> dict[str, Any]:
    (_Carrier, _build, _route, Custody, _submit, _Registry, _Request, _eval, _Ledger, _run) = _components()
    custody = Custody(custody_db)
    record = custody.evidence_package(manifest_receipt_id)
    if not isinstance(record, Mapping):
        raise RuntimeError("Master Records custody lookup did not return an object")
    value = dict(record)
    if str(value.get("manifest_receipt_id") or "").strip().upper() != manifest_receipt_id.strip().upper():
        raise RuntimeError("Master Records custody receipt identity mismatch")
    if not isinstance(value.get("evidence_package"), Mapping):
        raise RuntimeError("Master Records custody evidence package missing")
    return value


def run_post_return_production_proof(
    *,
    release_receipt_path: str | Path,
    manifest_path: str | Path,
    pre_steggate_bundle_path: str | Path,
    custody_db: str | Path,
    state_path: str | Path,
    exchange_path: str | Path,
    proof_path: str | Path,
    consequence_key: str = "post_return_production_proof",
    host_identity: str = "stegverse-sovereign-local",
) -> dict[str, Any]:
    release_receipt = _load_object(release_receipt_path)
    release_check = verify_coherent_release_receipt(release_receipt)
    if release_check.get("verified") is not True:
        raise RuntimeError("release_receipt_not_coherent:" + ",".join(release_check.get("reasons") or []))

    pre_bundle = _load_object(pre_steggate_bundle_path)
    pre_report = verify_portable_governance_bundle(pre_bundle)
    if pre_report.get("status") != "PASS" or pre_report.get("stage") != "PRE_STEGGATE":
        raise RuntimeError("pre_steggate_bundle_not_verified")

    manifest = load_public_inspection_request(manifest_path)
    normalized = validate_public_inspection_request(manifest)
    proposition_binding = verify_manifest_standing_proposition_binding(normalized, pre_bundle)
    standing_context = build_standing_execution_context(pre_bundle)

    run_id = str(pre_bundle.get("run_id") or "").strip()
    release_set_id = str(release_check.get("release_set_id") or "").strip()
    if not run_id:
        raise RuntimeError("pre_steggate_run_id_missing")
    idempotency_key = f"{release_set_id}:{run_id}:{consequence_key}"
    consequence_value = {
        "release_set_id": release_set_id,
        "package_id": pre_bundle.get("package_id"),
        "transition_id": pre_bundle.get("transition_id"),
        "run_id": run_id,
        "three_layer_request_hash": proposition_binding["three_layer_request_hash"],
    }
    executor = reference_state_executor(
        state_path,
        key=consequence_key,
        value=consequence_value,
        idempotency_key=idempotency_key,
    )

    sovereign_result = run_sovereign_validation(
        normalized,
        custody_db=custody_db,
        host_identity=host_identity,
        consequence_executor=executor,
        consequence_metadata={
            "schema": "stegverse.reference-bounded-consequence-request.v1",
            "key": consequence_key,
            "idempotency_key": idempotency_key,
            "external_side_effect": False,
        },
        declared_execution_context=standing_context,
        route_purpose="post-return-production-proof",
    )
    if sovereign_result.get("declared_execution_context_consumed_by_canonical_runtime") is not True:
        raise RuntimeError("canonical_runtime_did_not_consume_standing_context")
    if sovereign_result.get("governance_state") != "ALLOW":
        raise RuntimeError("canonical_governance_did_not_allow_proof_consequence")
    execution_result = sovereign_result.get("execution_result")
    if not isinstance(execution_result, Mapping) or execution_result.get("state_transition_performed") is not True:
        raise RuntimeError("bounded_sovereign_state_transition_not_performed")
    if sovereign_result.get("master_records_custody_status") != "RECORDED":
        raise RuntimeError("canonical_master_records_custody_not_recorded")

    rid = str(sovereign_result.get("manifest_receipt_id") or "").strip()
    if not rid:
        raise RuntimeError("canonical_manifest_receipt_id_missing")
    custody_record = _custody_record(custody_db, rid)
    successor_hash = str(execution_result.get("after_state_hash") or "").strip()
    if not successor_hash:
        raise RuntimeError("bounded_consequence_after_state_hash_missing")
    participant_id = str((pre_bundle.get("ingress_interlock") or {}).get("connection", {}).get("participant_id") or "participant").strip()
    successor_state_id = f"{participant_id}:successor:{run_id}"

    proof = complete_post_return_evidence(
        pre_steggate_bundle=pre_bundle,
        sovereign_result=sovereign_result,
        custody_record=custody_record,
        successor_state_id=successor_state_id,
        successor_state_hash=successor_hash,
        exchange_path=exchange_path,
        replay=lambda receipt_id: replay_sovereign(receipt_id, custody_db=custody_db),
        reconstruct=lambda receipt_id: reconstruct_sovereign(receipt_id, custody_db=custody_db),
    )
    if proof.get("status") != "PASS":
        raise RuntimeError("post_return_evidence_not_pass")

    result = {
        "schema": PROOF_RUNNER_SCHEMA,
        "status": "PASS",
        "release_set_id": release_set_id,
        "release_receipt_hash": release_check.get("receipt_hash"),
        "release_proof_capabilities": release_check["proof_capabilities"],
        "pre_steggate_verification": pre_report,
        "proposition_binding": proposition_binding,
        "manifest_receipt_id": rid,
        "transaction_id": sovereign_result.get("transaction_id"),
        "sovereign_result": sovereign_result,
        "master_records_custody": {
            "manifest_receipt_id": custody_record.get("manifest_receipt_id"),
            "master_record_sha256": custody_record.get("master_record_sha256"),
            "status": "RECORDED",
        },
        "post_return_proof": proof,
        "authority": {
            "sdk_authority": "NONE",
            "release_verification_authority": "NONE",
            "copied_exchange_is_canonical_custody": False,
        },
    }
    _write_json(proof_path, result)
    return result


__all__ = [
    "PROOF_RUNNER_SCHEMA",
    "verify_coherent_release_receipt",
    "derive_three_layer_request",
    "verify_manifest_standing_proposition_binding",
    "run_post_return_production_proof",
]
