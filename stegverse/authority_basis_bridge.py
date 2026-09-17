from __future__ import annotations

"""SDK binding to a canonical, non-authorizing authority-basis resolver.

The SDK preserves structured authority/delegation evidence and binds the resolver
output into the exact governance request. It does not interpret role policy,
issue authority, verify credentials, or implement an authority engine.
"""

from copy import deepcopy
from typing import Any, Callable, Mapping

AUTHORITY_BASIS_REQUEST_SCHEMA = "stegcore.authority-basis-request.v1"
AUTHORITY_BASIS_RESULT_SCHEMA = "stegcore.authority-basis-resolution.v1"
AUTHORITY_BASIS_REQUEST_EXTENSION = "authority_basis_request"
AUTHORITY_BASIS_BINDING_EXTENSION = "authority_basis_resolution_binding"

Resolver = Callable[..., Mapping[str, Any]]


class AuthorityBasisBridgeError(ValueError):
    pass


def _candidate_projection(value: Mapping[str, Any]) -> dict[str, str]:
    projected: dict[str, str] = {}
    for field in ("action", "target", "scope"):
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            raise AuthorityBasisBridgeError(f"candidate.{field} is required")
        projected[field] = item.strip()
    return projected


def _validate_request_envelope(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AuthorityBasisBridgeError("authority_basis_request must be an object")
    request = deepcopy(dict(value))
    if request.get("schema") != AUTHORITY_BASIS_REQUEST_SCHEMA:
        raise AuthorityBasisBridgeError("invalid authority_basis_request schema")
    task_id = request.get("task_id")
    actor_identity = request.get("actor_identity")
    if not isinstance(task_id, str) or not task_id.strip():
        raise AuthorityBasisBridgeError("authority_basis_request.task_id is required")
    if not isinstance(actor_identity, str) or not actor_identity.strip():
        raise AuthorityBasisBridgeError("authority_basis_request.actor_identity is required")
    request["candidate"] = _candidate_projection(request.get("candidate") or {})
    if request.get("authority_effect") != "NONE_TEST_EVIDENCE_ONLY":
        raise AuthorityBasisBridgeError("authority_basis_request must be non-authorizing")
    if not isinstance(request.get("authority_assertions"), list):
        raise AuthorityBasisBridgeError("authority_basis_request.authority_assertions must be an array")
    if not isinstance(request.get("delegation_assertions"), list):
        raise AuthorityBasisBridgeError("authority_basis_request.delegation_assertions must be an array")
    if not isinstance(request.get("delegation_required"), bool):
        raise AuthorityBasisBridgeError("authority_basis_request.delegation_required must be boolean")
    return request


def _validate_resolution(
    value: Any,
    *,
    request: Mapping[str, Any],
    candidate: Mapping[str, str],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AuthorityBasisBridgeError("authority basis resolver must return an object")
    result = deepcopy(dict(value))
    if result.get("schema") != AUTHORITY_BASIS_RESULT_SCHEMA:
        raise AuthorityBasisBridgeError("invalid authority basis resolution schema")
    if result.get("task_id") != request["task_id"]:
        raise AuthorityBasisBridgeError("authority basis resolution task mismatch")
    if _candidate_projection(result.get("candidate") or {}) != dict(candidate):
        raise AuthorityBasisBridgeError("authority basis resolution candidate mismatch")
    if result.get("authority_effect") != "NONE_RESOLUTION_ONLY":
        raise AuthorityBasisBridgeError("authority basis resolution must be non-authorizing")
    if result.get("role_label_used_as_authority") is not False:
        raise AuthorityBasisBridgeError("role label must not be used as authority")
    if result.get("role_policy_interpreted") is not False:
        raise AuthorityBasisBridgeError("SDK authority basis path must not interpret role policy")
    if result.get("authority_issued") is not False:
        raise AuthorityBasisBridgeError("authority basis resolver must not issue authority")
    if result.get("credential_verified") is not False:
        raise AuthorityBasisBridgeError("authority basis resolver must not claim credential verification")
    if result.get("disposition") not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        raise AuthorityBasisBridgeError("unsupported authority basis disposition")
    for field in ("actor_authority_current", "delegation_current"):
        if result.get(field) not in {True, False, None}:
            raise AuthorityBasisBridgeError(f"{field} must be boolean or null")
    refs = result.get("evidence_refs", [])
    if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
        raise AuthorityBasisBridgeError("authority basis evidence_refs must be strings")
    return result


def resolve_governance_authority_basis(
    *,
    governance_request: Mapping[str, Any],
    authority_basis_request: Mapping[str, Any],
    resolver: Resolver,
    observed_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Resolve structured basis and bind only currentness facts into StegGate input."""

    if not isinstance(governance_request, Mapping):
        raise AuthorityBasisBridgeError("governance_request must be an object")
    source = deepcopy(dict(governance_request))
    candidate_raw = source.get("candidate")
    if not isinstance(candidate_raw, Mapping):
        raise AuthorityBasisBridgeError("governance_request.candidate must be an object")
    candidate = _candidate_projection(candidate_raw)
    request = _validate_request_envelope(authority_basis_request)
    if request["candidate"] != candidate:
        raise AuthorityBasisBridgeError("authority_basis_request candidate must match governance_request candidate")

    execution = source.get("execution")
    if not isinstance(execution, Mapping):
        raise AuthorityBasisBridgeError("governance_request.execution must be an object")
    execution = deepcopy(dict(execution))
    for field in ("actor_authority_current", "delegation_current"):
        if execution.get(field) is not None:
            raise AuthorityBasisBridgeError(
                f"{field} must be null/unestablished before structured authority basis resolution"
            )

    try:
        resolved_raw = resolver(deepcopy(request), observed_at=observed_at)
    except TypeError as exc:
        raise AuthorityBasisBridgeError(
            "authority basis resolver must accept (request, observed_at=...)"
        ) from exc
    result = _validate_resolution(resolved_raw, request=request, candidate=candidate)

    execution["actor_authority_current"] = result["actor_authority_current"]
    execution["delegation_current"] = result["delegation_current"]
    refs = list(execution.get("evidence_refs") or [])
    for ref in result.get("evidence_refs") or []:
        if ref not in refs:
            refs.append(ref)
    execution["evidence_refs"] = refs
    selected_delegation = result.get("selected_delegation_assertion_id")
    if selected_delegation:
        execution["delegation_ref"] = selected_delegation
    source["execution"] = execution

    context = source.get("declared_context")
    if context is None:
        context = {}
    if not isinstance(context, Mapping):
        raise AuthorityBasisBridgeError("governance_request.declared_context must be an object when supplied")
    context = deepcopy(dict(context))
    if "sdk_authority_basis_binding" in context:
        raise AuthorityBasisBridgeError("governance_request already contains sdk_authority_basis_binding")
    binding = {
        "schema": "stegverse.sdk.authority-basis-binding.v1",
        "task_id": request["task_id"],
        "actor_identity": request["actor_identity"],
        "actor_role": request.get("actor_role"),
        "candidate": dict(candidate),
        "observed_at": result.get("observed_at"),
        "disposition": result["disposition"],
        "actor_authority_current": result["actor_authority_current"],
        "delegation_current": result["delegation_current"],
        "selected_authority_assertion_id": result.get("selected_authority_assertion_id"),
        "selected_delegation_assertion_id": result.get("selected_delegation_assertion_id"),
        "evidence_refs": list(result.get("evidence_refs") or []),
        "resolution_authority": result.get("resolution_authority"),
        "role_label_used_as_authority": False,
        "role_policy_interpreted": False,
        "authority_issued": False,
        "credential_verified": False,
        "sdk_resolved_authority": False,
        "authority_effect": "NONE_VERIFICATION_AND_BINDING_ONLY",
    }
    context["sdk_authority_basis_binding"] = deepcopy(binding)
    source["declared_context"] = context
    return source, binding


__all__ = [
    "AUTHORITY_BASIS_BINDING_EXTENSION",
    "AUTHORITY_BASIS_REQUEST_EXTENSION",
    "AUTHORITY_BASIS_REQUEST_SCHEMA",
    "AUTHORITY_BASIS_RESULT_SCHEMA",
    "AuthorityBasisBridgeError",
    "resolve_governance_authority_basis",
]
