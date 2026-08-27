"""SDK client surface for canonical StegCore production manifold governance."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping


PACKET_SCHEMA = "stegverse.sdk-manifold-governance-test.v1"
RESULT_SCHEMA = "stegverse.sdk-manifold-governance-result.v1"
PRODUCTION_RUNTIME = "stegcore.manifold_governance.govern_manifold_action"


class ManifoldGovernanceSDKError(RuntimeError):
    pass


def _components():
    try:
        from stegcore.manifold_governance import PopulationTransition, govern_manifold_action
        from stegcore.steggate import AdmissibilityRequest
    except ImportError as exc:
        raise ManifoldGovernanceSDKError(
            "Canonical StegCore governed-manifold production capability is required; "
            "the SDK provides no fallback or parallel evaluator."
        ) from exc
    return PopulationTransition, govern_manifold_action, AdmissibilityRequest


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ManifoldGovernanceSDKError(f"{name} is required")
    return text


def evaluate_manifold_governance(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Run an evaluator packet through canonical StegCore manifold governance.

    The SDK performs only packet mapping and result presentation. All transition
    dispositions and manifold action classification are produced by StegCore.
    """

    if not isinstance(packet, Mapping):
        raise ManifoldGovernanceSDKError("manifold governance packet must be an object")
    if packet.get("schema") != PACKET_SCHEMA:
        raise ManifoldGovernanceSDKError(f"unsupported packet schema; expected {PACKET_SCHEMA}")

    base_manifold_hash = _required_text(packet.get("base_manifold_hash"), "base_manifold_hash")
    rows = packet.get("transitions")
    if not isinstance(rows, list) or not rows:
        raise ManifoldGovernanceSDKError("transitions must be a non-empty array")

    PopulationTransition, govern_manifold_action, AdmissibilityRequest = _components()
    transitions = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ManifoldGovernanceSDKError(f"transitions[{index}] must be an object")
        transition_id = _required_text(row.get("transition_id"), f"transitions[{index}].transition_id")
        request_body = row.get("request")
        if not isinstance(request_body, Mapping):
            raise ManifoldGovernanceSDKError(f"transitions[{index}].request must be an object")
        try:
            request = AdmissibilityRequest.model_validate(dict(request_body))
        except Exception as exc:
            raise ManifoldGovernanceSDKError(
                f"transitions[{index}].request is not a valid canonical StegCore admissibility request: {exc}"
            ) from exc

        row_base = _required_text(
            row.get("base_manifold_hash", base_manifold_hash),
            f"transitions[{index}].base_manifold_hash",
        )
        dependencies = tuple(str(item).strip() for item in (row.get("depends_on") or []) if str(item).strip())
        conflicts = tuple(str(item).strip() for item in (row.get("conflicts_with") or []) if str(item).strip())
        bundle_id = row.get("bundle_id")
        if bundle_id is not None:
            bundle_id = _required_text(bundle_id, f"transitions[{index}].bundle_id")
        observations = row.get("observations") or {}
        if not isinstance(observations, Mapping):
            raise ManifoldGovernanceSDKError(f"transitions[{index}].observations must be an object")

        transitions.append(
            PopulationTransition(
                transition_id=transition_id,
                base_manifold_hash=row_base,
                request=request,
                depends_on=dependencies,
                conflicts_with=conflicts,
                bundle_id=bundle_id,
                observations=dict(observations),
            )
        )

    boundary_refs_raw = packet.get("authority_boundary_refs") or []
    if not isinstance(boundary_refs_raw, list):
        raise ManifoldGovernanceSDKError("authority_boundary_refs must be an array")
    boundary_refs = tuple(_required_text(item, "authority_boundary_refs[]") for item in boundary_refs_raw)

    action = govern_manifold_action(transitions, authority_boundary_refs=boundary_refs)
    action_payload = asdict(action) if is_dataclass(action) else dict(action)

    return {
        "schema": RESULT_SCHEMA,
        "sdk_role": "DEMO_TEST_CLIENT_OF_CANONICAL_PRODUCTION_GOVERNANCE",
        "production_runtime": PRODUCTION_RUNTIME,
        "parallel_evaluator": False,
        "sdk_grants_authority": False,
        "sdk_reinterprets_disposition": False,
        "external_execution_performed_by_sdk": False,
        "input_transition_count": len(transitions),
        "action": action_payload,
    }


__all__ = [
    "PACKET_SCHEMA",
    "RESULT_SCHEMA",
    "PRODUCTION_RUNTIME",
    "ManifoldGovernanceSDKError",
    "evaluate_manifold_governance",
]
