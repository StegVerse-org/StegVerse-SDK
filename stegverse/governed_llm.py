"""Governed LLM reconstruction contracts for StegVerse.

This module defines the transport-free packet and receipt helpers shared by
LLM adapters, continuity search, and SDK intake paths.  It intentionally does
not call a model provider.  The LLM produces candidates; this module records
what evidence, policy standing, and output hash are required for future
reconstruction.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "stegverse.governed_llm.v0.1"


LOW_RISK = "LOW"
MEDIUM_RISK = "MEDIUM"
HIGH_RISK = "HIGH"
CRITICAL_RISK = "CRITICAL"


READ_ONLY_PURPOSES = frozenset({"answer", "summarize", "explain", "classify"})
ACTION_PURPOSES = frozenset({"publish", "commit", "send", "execute", "mutate_memory"})


def utc_now_iso() -> str:
    """Return a deterministic UTC timestamp shape for receipts."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_json(value: Any) -> str:
    """Serialize a value into stable JSON for hashing and receipts."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    """Return a sha256 hash for a JSON-serializable value."""

    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidencePointer:
    """Pointer to evidence used by a governed LLM response.

    Full source payloads should not be copied into every receipt.  Store the
    minimum pointer, freshness state, and content hash needed for later
    reconstruction.
    """

    source_type: str
    pointer: str
    content_hash: str
    retrieved_at: str
    freshness: str = "current"
    authority_scope: str = "read"
    notes: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class GovernedQueryPacket:
    """Admissible evidence packet prepared before model response generation."""

    query: str
    purpose: str
    transition_class: str
    risk_tier: str
    allowed_sources: tuple[str, ...]
    evidence: tuple[EvidencePointer, ...] = field(default_factory=tuple)
    policy_hash: str = "unresolved"
    delegation_hash: str = "unresolved"
    created_at: str = field(default_factory=utc_now_iso)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "query": self.query,
            "purpose": self.purpose,
            "transition_class": self.transition_class,
            "risk_tier": self.risk_tier,
            "allowed_sources": list(self.allowed_sources),
            "evidence": [item.to_dict() for item in self.evidence],
            "policy_hash": self.policy_hash,
            "delegation_hash": self.delegation_hash,
        }

    @property
    def packet_hash(self) -> str:
        return stable_hash(self.to_dict())


@dataclass(frozen=True)
class GovernedResponseReceipt:
    """Receipt proving what the adapter emitted and what standing was checked."""

    query_packet_hash: str
    output_hash: str
    model_provider: str
    model_name: str
    decision: str
    admissibility_status: str
    reconstruction_status: str
    emitted_at: str = field(default_factory=utc_now_iso)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @property
    def receipt_hash(self) -> str:
        return stable_hash(self.to_dict())


def classify_query_purpose(query: str, requested_purpose: str | None = None) -> str:
    """Classify query purpose with simple deterministic rules.

    Provider-specific semantic classification can replace this later.  The SDK
    default stays deterministic so tests and downstream route checks are stable.
    """

    if requested_purpose:
        return requested_purpose.lower().strip()

    lowered = query.lower()
    if any(word in lowered for word in ("commit", "publish", "send", "execute")):
        return "execute"
    if any(word in lowered for word in ("remember", "store", "memory")):
        return "mutate_memory"
    if any(word in lowered for word in ("summarize", "explain", "what", "how", "why")):
        return "answer"
    return "classify"


def classify_risk_tier(purpose: str, allowed_sources: Sequence[str]) -> str:
    """Return the minimum governance tier for a purpose/source combination."""

    normalized_sources = {source.lower() for source in allowed_sources}
    if purpose in ACTION_PURPOSES:
        return HIGH_RISK
    if {"private_connector", "memory", "repo_write"} & normalized_sources:
        return MEDIUM_RISK
    if "external_publication" in normalized_sources:
        return HIGH_RISK
    return LOW_RISK


def build_query_packet(
    query: str,
    *,
    allowed_sources: Sequence[str] = ("model_knowledge",),
    purpose: str | None = None,
    transition_class: str = "candidate_response",
    evidence: Sequence[EvidencePointer] = (),
    policy: Mapping[str, Any] | None = None,
    delegation: Mapping[str, Any] | None = None,
) -> GovernedQueryPacket:
    """Build a receipt-ready query packet for governed retrieval."""

    resolved_purpose = classify_query_purpose(query, purpose)
    source_tuple = tuple(allowed_sources)
    return GovernedQueryPacket(
        query=query,
        purpose=resolved_purpose,
        transition_class=transition_class,
        risk_tier=classify_risk_tier(resolved_purpose, source_tuple),
        allowed_sources=source_tuple,
        evidence=tuple(evidence),
        policy_hash=stable_hash(policy or {"policy": "unresolved"}),
        delegation_hash=stable_hash(delegation or {"delegation": "unresolved"}),
    )


def build_response_receipt(
    query_packet: GovernedQueryPacket,
    output: str,
    *,
    model_provider: str,
    model_name: str,
    decision: str,
    admissibility_status: str,
    reconstruction_status: str = "reconstructable",
) -> GovernedResponseReceipt:
    """Build the output receipt for a governed LLM response."""

    return GovernedResponseReceipt(
        query_packet_hash=query_packet.packet_hash,
        output_hash=stable_hash({"output": output}),
        model_provider=model_provider,
        model_name=model_name,
        decision=decision.upper(),
        admissibility_status=admissibility_status,
        reconstruction_status=reconstruction_status,
    )


def reconstruction_summary(
    query_packet: GovernedQueryPacket,
    receipt: GovernedResponseReceipt,
) -> dict[str, Any]:
    """Return the minimum reconstruction map for downstream records."""

    return {
        "schema_version": SCHEMA_VERSION,
        "query_packet_hash": query_packet.packet_hash,
        "response_receipt_hash": receipt.receipt_hash,
        "policy_hash": query_packet.policy_hash,
        "delegation_hash": query_packet.delegation_hash,
        "evidence_hashes": [item.content_hash for item in query_packet.evidence],
        "risk_tier": query_packet.risk_tier,
        "decision": receipt.decision,
        "admissibility_status": receipt.admissibility_status,
        "reconstruction_status": receipt.reconstruction_status,
    }


__all__ = [
    "SCHEMA_VERSION",
    "LOW_RISK",
    "MEDIUM_RISK",
    "HIGH_RISK",
    "CRITICAL_RISK",
    "EvidencePointer",
    "GovernedQueryPacket",
    "GovernedResponseReceipt",
    "build_query_packet",
    "build_response_receipt",
    "classify_query_purpose",
    "classify_risk_tier",
    "reconstruction_summary",
    "stable_hash",
    "stable_json",
    "utc_now_iso",
]
