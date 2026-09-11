from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Iterable, Mapping

from .shared_docs_freeze import CURRENT, SharedDocsFreezeError, successor_revision

PROVIDER_OBSERVATION_SCHEMA = "stegverse.shared-docs-provider-observation/v1"
PROVIDER_BINDING_SCHEMA = "stegverse.shared-docs-provider-revision-binding/v1"
FREEZE_PROJECTION_SCHEMA = "stegverse.shared-docs-provider-freeze-projection/v1"


class SharedDocsProviderFreezeError(SharedDocsFreezeError):
    pass


def _sha256_canonical(value: Mapping[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise SharedDocsProviderFreezeError(f"{label} invalid")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise SharedDocsProviderFreezeError(f"{label} invalid") from exc
    return value.lower()


def create_provider_observation(
    *,
    provider: str,
    provider_document_id: str,
    provider_version_id: str,
    content_digest: str,
    observed_at: str,
    observation_ref: str,
    provider_authority: str = "TV/TVC",
) -> dict[str, Any]:
    payload = {
        "schema": PROVIDER_OBSERVATION_SCHEMA,
        "provider": str(provider).strip(),
        "provider_document_id": str(provider_document_id).strip(),
        "provider_version_id": str(provider_version_id).strip(),
        "content_digest": _require_sha256(content_digest, "provider content digest"),
        "observed_at": str(observed_at).strip(),
        "observation_ref": str(observation_ref).strip(),
        "provider_authority": str(provider_authority).strip(),
        "provider_mutation_performed": False,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    if not all(payload[key] for key in ("provider", "provider_document_id", "provider_version_id", "observed_at", "observation_ref")):
        raise SharedDocsProviderFreezeError("provider observation identity fields required")
    if payload["provider_authority"] != "TV/TVC":
        raise SharedDocsProviderFreezeError("provider authority must remain TV/TVC")
    payload["observation_sha256"] = _sha256_canonical(payload)
    return payload


def validate_provider_observation(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise SharedDocsProviderFreezeError("provider observation must be an object")
    observation = copy.deepcopy(dict(value))
    if observation.get("schema") != PROVIDER_OBSERVATION_SCHEMA:
        raise SharedDocsProviderFreezeError("provider observation schema invalid")
    if observation.get("provider_authority") != "TV/TVC":
        raise SharedDocsProviderFreezeError("provider authority must remain TV/TVC")
    if observation.get("provider_mutation_performed") is not False:
        raise SharedDocsProviderFreezeError("provider observation may not claim mutation")
    if observation.get("authority_effect") != "NONE_EVIDENCE_ONLY":
        raise SharedDocsProviderFreezeError("provider observation must remain evidence-only")
    for key in ("provider", "provider_document_id", "provider_version_id", "observed_at", "observation_ref"):
        if not isinstance(observation.get(key), str) or not observation[key].strip():
            raise SharedDocsProviderFreezeError(f"provider observation {key} required")
    observation["content_digest"] = _require_sha256(observation.get("content_digest"), "provider content digest")
    supplied = _require_sha256(observation.get("observation_sha256"), "provider observation hash")
    preimage = dict(observation)
    preimage.pop("observation_sha256", None)
    if supplied != _sha256_canonical(preimage):
        raise SharedDocsProviderFreezeError("provider observation hash mismatch")
    return observation


def bind_provider_revision(revision: Mapping[str, Any], observation: Mapping[str, Any]) -> dict[str, Any]:
    observed = validate_provider_observation(observation)
    if revision.get("content_digest") != observed["content_digest"]:
        raise SharedDocsProviderFreezeError("provider content digest does not match revision")
    payload = {
        "schema": PROVIDER_BINDING_SCHEMA,
        "document_id": revision.get("document_id"),
        "revision_id": revision.get("revision_id"),
        "review_epoch": revision.get("review_epoch"),
        "revision_status": revision.get("revision_status"),
        "freeze_state": revision.get("freeze_state"),
        "content_digest": revision.get("content_digest"),
        "provider": observed["provider"],
        "provider_document_id": observed["provider_document_id"],
        "provider_version_id": observed["provider_version_id"],
        "provider_observed_at": observed["observed_at"],
        "provider_observation_ref": observed["observation_ref"],
        "provider_observation_sha256": observed["observation_sha256"],
        "provider_authority": "TV/TVC",
        "transition_authority": "Interlock/InTr",
        "authority_effect": "NONE_BINDING_PROVENANCE_ONLY",
    }
    if not payload["document_id"] or not payload["revision_id"] or not payload["review_epoch"]:
        raise SharedDocsProviderFreezeError("revision identity incomplete")
    payload["binding_sha256"] = _sha256_canonical(payload)
    return payload


def project_freeze_metadata(revision: Mapping[str, Any], binding: Mapping[str, Any]) -> dict[str, Any]:
    if binding.get("schema") != PROVIDER_BINDING_SCHEMA:
        raise SharedDocsProviderFreezeError("provider binding schema invalid")
    for field in ("document_id", "revision_id", "review_epoch", "content_digest"):
        if binding.get(field) != revision.get(field):
            raise SharedDocsProviderFreezeError("provider binding does not match revision")
    projection = {
        "schema": FREEZE_PROJECTION_SCHEMA,
        "document_id": revision["document_id"],
        "revision_id": revision["revision_id"],
        "review_epoch": revision["review_epoch"],
        "content_digest": revision["content_digest"],
        "freeze_state": revision["freeze_state"],
        "revision_status": revision["revision_status"],
        "provider": binding["provider"],
        "provider_document_id": binding["provider_document_id"],
        "provider_version_id": binding["provider_version_id"],
        "reviewed_bytes_mutated": False,
        "provider_write_performed": False,
        "authority_effect": "NONE_METADATA_PROJECTION_ONLY",
    }
    projection["projection_sha256"] = _sha256_canonical(projection)
    return projection


def successor_from_admitted_provider_edit(
    revision: Mapping[str, Any],
    prior_binding: Mapping[str, Any],
    new_observation: Mapping[str, Any],
    *,
    new_revision_id: str,
    new_review_epoch: str,
    created_at: str,
    admitted_transition_ref: str,
    eligible_reviewers: Iterable[dict] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if revision.get("revision_status") != CURRENT:
        raise SharedDocsProviderFreezeError("provider edit requires current revision")
    if prior_binding.get("schema") != PROVIDER_BINDING_SCHEMA:
        raise SharedDocsProviderFreezeError("prior provider binding schema invalid")
    for field in ("document_id", "revision_id", "review_epoch", "content_digest"):
        if prior_binding.get(field) != revision.get(field):
            raise SharedDocsProviderFreezeError("prior provider binding does not match current revision")
    if prior_binding.get("provider_authority") != "TV/TVC" or prior_binding.get("transition_authority") != "Interlock/InTr":
        raise SharedDocsProviderFreezeError("provider or transition authority drift")
    if not isinstance(admitted_transition_ref, str) or not admitted_transition_ref.strip():
        raise SharedDocsProviderFreezeError("admitted Interlock/InTr transition reference required")

    observed = validate_provider_observation(new_observation)
    if observed["provider"] != prior_binding["provider"] or observed["provider_document_id"] != prior_binding["provider_document_id"]:
        raise SharedDocsProviderFreezeError("provider document identity changed")
    if observed["provider_version_id"] == prior_binding["provider_version_id"]:
        raise SharedDocsProviderFreezeError("provider version did not advance")
    if observed["content_digest"] == revision["content_digest"]:
        raise SharedDocsProviderFreezeError("provider edit did not change reviewed content digest")

    prior, current = successor_revision(
        dict(revision),
        new_revision_id=new_revision_id,
        new_review_epoch=new_review_epoch,
        created_at=created_at,
        content=None,
        eligible_reviewers=eligible_reviewers,
    )
    current["content_digest"] = observed["content_digest"]
    current["provider_edit_transition_ref"] = admitted_transition_ref.strip()
    current["provider_authority"] = "TV/TVC"
    current["transition_authority"] = "Interlock/InTr"
    binding = bind_provider_revision(current, observed)
    return prior, current, binding


__all__ = [
    "PROVIDER_OBSERVATION_SCHEMA",
    "PROVIDER_BINDING_SCHEMA",
    "FREEZE_PROJECTION_SCHEMA",
    "SharedDocsProviderFreezeError",
    "create_provider_observation",
    "validate_provider_observation",
    "bind_provider_revision",
    "project_freeze_metadata",
    "successor_from_admitted_provider_edit",
]
