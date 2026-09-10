"""Exact cryptographic projection of an ephemeral task security-posture instance.

The projection is evidence only. It does not grant transition, credential, execution,
or transport authority. It exists so downstream Interlock/InTr admission can bind the
exact posture instance bytes/structure together with an exact sensitive payload.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .security_posture import (
    _canonical_digest,
    resolve_security_posture,
    validate_task_security_posture_instance,
)

BINDING_SCHEMA = "stegverse.sdk.security-posture-instance-binding.v1"


def bind_task_security_posture_instance(
    instance: Mapping[str, Any], *, task_id: str, observed_at: str
) -> dict[str, Any]:
    """Validate and digest the exact task-scoped posture instance for downstream binding."""
    validate_task_security_posture_instance(instance, task_id=task_id, observed_at=observed_at)
    posture = resolve_security_posture(str(instance.get("posture_id")))
    exact_instance = deepcopy(dict(instance))
    return {
        "schema": BINDING_SCHEMA,
        "instance_id": instance["instance_id"],
        "instance_sha256": _canonical_digest(exact_instance),
        "task_id": task_id,
        "posture_id": posture["posture_id"],
        "posture_version": posture["version"],
        "posture_sha256": posture["posture_sha256"],
        "effective_tier": posture["tier"],
        "issued_at": instance["issued_at"],
        "expires_at": instance["expires_at"],
        "transferable": False,
        "reusable_across_tasks": False,
        "authority_effect": "NONE_ADMISSION_EVIDENCE_ONLY",
    }
