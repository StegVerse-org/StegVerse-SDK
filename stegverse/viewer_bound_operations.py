"""Viewer-bound replay/reconstruction adapter for the self-characterization lane.

Canonical replay/reconstruction remain unchanged. This adapter appends a separate
non-authorizing viewer-binding event to the same Master Records custody so each
viewer's access can be correlated and reconstructed without mutating the source run.
"""
from __future__ import annotations

from typing import Any

from .self_characterization_lane import derive_viewer_operation_id
from .sovereign_validation_runtime import _components, reconstruct_sovereign, replay_sovereign


class ViewerBoundOperationError(RuntimeError):
    pass


def _record_viewer_binding(
    *,
    manifest_receipt_id: str,
    custody_db: str,
    canonical_operation_id: str,
    canonical_operation_receipt_ids: list[str],
    viewer_node_id: str,
    operation: str,
) -> dict[str, Any]:
    binding = derive_viewer_operation_id(
        manifest_receipt_id=manifest_receipt_id,
        viewer_node_id=viewer_node_id,
        operation=operation,
    )
    (_Carrier, _build, _route, Custody, _submit, _Registry, _Request, _eval, _Ledger, _run) = _components()
    custody = Custody(custody_db)
    event = custody.record_operation_event({
        "source_manifest_receipt_id": binding["manifest_receipt_id"],
        "operation_id": canonical_operation_id,
        "operation": operation,
        "sequence": 4,
        "event_type": "VIEWER_BOUND",
        "details": {
            "viewer_binding": binding,
            "canonical_operation_receipt_ids": list(canonical_operation_receipt_ids),
            "viewer_identity_is_decision_input": False,
            "viewer_binding_grants_authority": False,
            "source_run_mutated": False,
        },
        "authority_granted": False,
    })
    return {
        **binding,
        "binding_event_receipt_id": event["event_receipt_id"],
        "canonical_operation_id": canonical_operation_id,
        "canonical_operation_receipt_ids": list(canonical_operation_receipt_ids),
        "binding_transition_custody_status": "RECORDED",
        "source_run_mutated": False,
    }


def replay_for_viewer(
    manifest_receipt_id: str,
    *,
    viewer_node_id: str,
    custody_db: str,
) -> dict[str, Any]:
    artifact = replay_sovereign(manifest_receipt_id, custody_db=custody_db)
    binding = _record_viewer_binding(
        manifest_receipt_id=artifact["manifest_receipt_id"],
        custody_db=custody_db,
        canonical_operation_id=artifact["operation_id"],
        canonical_operation_receipt_ids=list(artifact.get("operation_receipt_ids") or []),
        viewer_node_id=viewer_node_id,
        operation="REPLAY",
    )
    return {
        "schema": "stegverse.viewer-bound-replay.v1",
        "viewer_binding": binding,
        "artifact": artifact,
        "consequence_reexecuted": False,
        "original_record_mutated": False,
        "authority_effect": "NONE",
    }


def reconstruct_for_viewer(
    manifest_receipt_id: str,
    *,
    viewer_node_id: str,
    custody_db: str,
) -> dict[str, Any]:
    artifact = reconstruct_sovereign(manifest_receipt_id, custody_db=custody_db)
    rid = str(artifact.get("manifest_receipt_id") or manifest_receipt_id).strip().upper()
    binding = _record_viewer_binding(
        manifest_receipt_id=rid,
        custody_db=custody_db,
        canonical_operation_id=artifact["operation_id"],
        canonical_operation_receipt_ids=list(artifact.get("operation_receipt_ids") or []),
        viewer_node_id=viewer_node_id,
        operation="RECONSTRUCT",
    )
    return {
        "schema": "stegverse.viewer-bound-reconstruction.v1",
        "viewer_binding": binding,
        "artifact": artifact,
        "consequence_reexecuted": False,
        "original_record_mutated": False,
        "authority_effect": "NONE",
    }


__all__ = ["replay_for_viewer", "reconstruct_for_viewer", "ViewerBoundOperationError"]
