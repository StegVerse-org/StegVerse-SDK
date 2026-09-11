from __future__ import annotations

import copy
import hashlib
import json
from typing import Iterable

SCHEMA_VERSION = "stegverse.shared-docs-revision-freeze/v1"
ALL_ELIGIBLE = "ALL_ELIGIBLE"
REVIEW_OPEN = "REVIEW_OPEN"
PARTIALLY_FROZEN = "PARTIALLY_FROZEN"
FROZEN = "FROZEN"
CURRENT = "CURRENT"
SUPERSEDED = "SUPERSEDED"


class SharedDocsFreezeError(ValueError):
    pass


def content_digest(content: str | bytes) -> str:
    raw = content.encode("utf-8") if isinstance(content, str) else bytes(content)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _normalize_reviewers(reviewers: Iterable[dict]) -> list[dict]:
    normalized = []
    seen = set()
    for reviewer in reviewers:
        reviewer_id = str(reviewer["reviewer_id"]).strip()
        reviewer_role = str(reviewer.get("reviewer_role", "REVIEWER")).strip()
        if not reviewer_id or reviewer_id in seen:
            raise SharedDocsFreezeError("eligible reviewers must have unique non-empty reviewer_id values")
        seen.add(reviewer_id)
        normalized.append({"reviewer_id": reviewer_id, "reviewer_role": reviewer_role})
    if not normalized:
        raise SharedDocsFreezeError("at least one eligible reviewer is required")
    return sorted(normalized, key=lambda item: item["reviewer_id"])


def create_revision(
    *,
    document_id: str,
    revision_id: str,
    review_epoch: str,
    content: str | bytes,
    eligible_reviewers: Iterable[dict],
    created_at: str,
    freeze_policy: str = ALL_ELIGIBLE,
    supersedes_revision_id: str | None = None,
) -> dict:
    if freeze_policy != ALL_ELIGIBLE:
        raise SharedDocsFreezeError("unsupported freeze policy")
    return {
        "schema": SCHEMA_VERSION,
        "document_id": document_id,
        "revision_id": revision_id,
        "review_epoch": review_epoch,
        "content_digest": content_digest(content),
        "freeze_policy": freeze_policy,
        "eligible_reviewers": _normalize_reviewers(eligible_reviewers),
        "freeze_receipts": [],
        "freeze_state": REVIEW_OPEN,
        "revision_status": CURRENT,
        "supersedes_revision_id": supersedes_revision_id,
        "created_at": created_at,
        "authority_effect": "NONE_COORDINATION_PROVENANCE_ONLY",
    }


def _eligible_ids(revision: dict) -> set[str]:
    return {item["reviewer_id"] for item in revision["eligible_reviewers"]}


def evaluate_freeze_state(revision: dict) -> str:
    frozen_ids = {item["reviewer_id"] for item in revision["freeze_receipts"]}
    eligible = _eligible_ids(revision)
    if not frozen_ids:
        return REVIEW_OPEN
    if revision["freeze_policy"] == ALL_ELIGIBLE and frozen_ids == eligible:
        return FROZEN
    return PARTIALLY_FROZEN


def _receipt_id(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "freeze:" + hashlib.sha256(canonical).hexdigest()


def freeze_revision(
    revision: dict,
    *,
    reviewer_id: str,
    frozen_at: str,
    expected_revision_id: str | None = None,
    expected_content_digest: str | None = None,
) -> dict:
    if revision.get("revision_status") != CURRENT:
        raise SharedDocsFreezeError("cannot freeze a superseded revision")
    if expected_revision_id is not None and expected_revision_id != revision["revision_id"]:
        raise SharedDocsFreezeError("stale revision")
    if expected_content_digest is not None and expected_content_digest != revision["content_digest"]:
        raise SharedDocsFreezeError("stale content digest")
    reviewers = {item["reviewer_id"]: item for item in revision["eligible_reviewers"]}
    if reviewer_id not in reviewers:
        raise SharedDocsFreezeError("reviewer is not eligible for this review epoch")
    if any(item["reviewer_id"] == reviewer_id for item in revision["freeze_receipts"]):
        raise SharedDocsFreezeError("reviewer already froze this revision")

    result = copy.deepcopy(revision)
    payload = {
        "document_id": revision["document_id"],
        "revision_id": revision["revision_id"],
        "content_digest": revision["content_digest"],
        "review_epoch": revision["review_epoch"],
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewers[reviewer_id]["reviewer_role"],
        "frozen_at": frozen_at,
        "freeze_policy": revision["freeze_policy"],
    }
    payload["freeze_receipt_id"] = _receipt_id(payload)
    result["freeze_receipts"].append(payload)
    result["freeze_receipts"] = sorted(result["freeze_receipts"], key=lambda item: item["reviewer_id"])
    result["freeze_state"] = evaluate_freeze_state(result)
    return result


def successor_revision(
    revision: dict,
    *,
    new_revision_id: str,
    new_review_epoch: str,
    created_at: str,
    content: str | bytes | None = None,
    eligible_reviewers: Iterable[dict] | None = None,
    freeze_policy: str | None = None,
) -> tuple[dict, dict]:
    prior = copy.deepcopy(revision)
    prior["revision_status"] = SUPERSEDED

    if content is None:
        digest = revision["content_digest"]
    else:
        digest = content_digest(content)

    policy = freeze_policy or revision["freeze_policy"]
    if policy != ALL_ELIGIBLE:
        raise SharedDocsFreezeError("unsupported freeze policy")
    reviewers = _normalize_reviewers(eligible_reviewers or revision["eligible_reviewers"])

    current = {
        "schema": SCHEMA_VERSION,
        "document_id": revision["document_id"],
        "revision_id": new_revision_id,
        "review_epoch": new_review_epoch,
        "content_digest": digest,
        "freeze_policy": policy,
        "eligible_reviewers": reviewers,
        "freeze_receipts": [],
        "freeze_state": REVIEW_OPEN,
        "revision_status": CURRENT,
        "supersedes_revision_id": revision["revision_id"],
        "created_at": created_at,
        "authority_effect": "NONE_COORDINATION_PROVENANCE_ONLY",
    }
    return prior, current
