"""Guided submit/replay/reconstruct navigation for governed SDK runs.

This module owns user-facing instructions and ingress validation only. It does not
implement StegGate authority. A structurally valid manifest is acceptable input
to governance; it is never an ALLOW decision.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

INGRESS_PROFILE = "stegverse.ingress-manifest.v1"
RECEIPT_ID_RE = re.compile(r"^MR-[A-F0-9]{16,64}$")

NAVIGATION = (
    ("0", "Submit data for governance"),
    ("1", "Replay previously run set"),
    ("2", "Reconstruct previously run set"),
)

SUBMIT_GUIDANCE = """SUBMIT DATA FOR GOVERNANCE

Choose submission type:

[0A] Submit raw/user data
     The SDK will create the governance manifest for you.

[0B] Submit a preformatted machine manifest
     Use this when another system or framework already produced a manifest
     conforming to the accepted StegVerse ingress profile.

What will happen:
- input is manifested or the supplied manifest is validated and canonicalized;
- the transaction enters canonical ingestion -> StegGate governance ->
  commit/consequence boundary -> return ingestion;
- submission and manifest validity do not grant authority;
- the completed run returns an inspectable evidence package and a final
  manifest_receipt_id identifying the exact immutable master-record run.

For machine manifests, required identity/provenance/hash/intent/payload or
payload-commitment fields are validated before governance. Structural validity
means only that the machine output is acceptable for governance.
"""

REPLAY_GUIDANCE = """REPLAY A PREVIOUSLY RUN SET

What you provide:
- the manifest_receipt_id returned by the original governed run.

What will happen:
- the identifier resolves to exactly one immutable historical master record;
- the recorded run definition/reference state is replayed through the canonical
  governed evaluation path;
- the original historical run is never overwritten.

What you receive:
- a new replay receipt linked to the original manifest receipt;
- original-vs-replay decision/state and identity/determinism comparisons;
- verification evidence for the replay.
"""

RECONSTRUCT_GUIDANCE = """RECONSTRUCT A PREVIOUSLY RUN SET

What you provide:
- the manifest_receipt_id returned by the original governed run.

What will happen:
- the identifier resolves to exactly one immutable historical master record;
- retained manifests, hashes, receipts, state records, and lineage are used to
  rebuild the historical trajectory;
- consequential side effects are not executed again.

What you receive:
- reconstructed trajectory and chain verification;
- explicit distinction between natively persisted historical evidence and
  evidence reconstructed afterward;
- a new reconstruction receipt linked to the original manifest receipt.
"""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def navigation_text() -> str:
    lines = ["StegVerse SDK", ""]
    lines.extend(f"[{key}] {label}" for key, label in NAVIGATION)
    return "\n".join(lines)


def guidance_for(selection: str) -> str:
    key = selection.strip().upper()
    if key in {"0", "0A", "0B"}:
        return SUBMIT_GUIDANCE
    if key == "1":
        return REPLAY_GUIDANCE
    if key == "2":
        return RECONSTRUCT_GUIDANCE
    raise ValueError("selection must be 0, 1, or 2")


def validate_manifest_receipt_id(value: str) -> str:
    normalized = value.strip().upper()
    if not RECEIPT_ID_RE.fullmatch(normalized):
        raise ValueError("manifest_receipt_id must use the canonical MR-<hex> form")
    return normalized


def validate_external_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and canonicalize a machine-produced ingress manifest.

    The profile intentionally standardizes an interoperable envelope while
    allowing framework-specific metadata under ``extensions``. Unknown top-level
    fields are rejected so semantic drift is observable and versioned.
    """
    allowed = {
        "manifest_profile", "manifest_profile_version", "source_framework",
        "source_instance", "source_output_id", "created_at", "freshness",
        "payload", "payload_commitment", "candidate", "declared_intent",
        "requested_consequence", "context_refs", "canonicalization_profile",
        "hashes", "attestation", "extensions",
    }
    unknown = sorted(set(manifest) - allowed)
    if unknown:
        raise ValueError("unknown top-level manifest fields: " + ", ".join(unknown))
    if manifest.get("manifest_profile") != INGRESS_PROFILE:
        raise ValueError(f"manifest_profile must be {INGRESS_PROFILE}")
    if str(manifest.get("manifest_profile_version") or "") != "1":
        raise ValueError("manifest_profile_version must be 1")
    required_text = (
        "source_framework", "source_output_id", "created_at",
        "declared_intent", "requested_consequence",
    )
    for key in required_text:
        if not isinstance(manifest.get(key), str) or not str(manifest[key]).strip():
            raise ValueError(f"{key} is required")
    has_payload = "payload" in manifest and manifest.get("payload") is not None
    has_commitment = isinstance(manifest.get("payload_commitment"), str) and bool(str(manifest.get("payload_commitment")).strip())
    if has_payload == has_commitment:
        raise ValueError("provide exactly one of payload or payload_commitment")
    if not isinstance(manifest.get("candidate"), Mapping):
        raise ValueError("candidate must be an object")
    hashes = manifest.get("hashes")
    if not isinstance(hashes, Mapping):
        raise ValueError("hashes must be an object")
    if has_payload:
        expected = hashes.get("payload_sha256")
        actual = canonical_sha256(manifest["payload"])
        if expected != actual:
            raise ValueError("payload_sha256 does not match canonical payload")
    candidate_hash = canonical_sha256(manifest["candidate"])
    if hashes.get("candidate_sha256") != candidate_hash:
        raise ValueError("candidate_sha256 does not match canonical candidate")
    canonical = dict(manifest)
    canonical.setdefault("source_instance", None)
    canonical.setdefault("freshness", {})
    canonical.setdefault("context_refs", [])
    canonical.setdefault("canonicalization_profile", "steggate.jcs.v1")
    canonical.setdefault("attestation", None)
    canonical.setdefault("extensions", {})
    canonical["ingress_mode"] = "external_manifest"
    canonical["external_manifest_valid"] = True
    canonical["external_manifest_grants_authority"] = False
    canonical["canonical_manifest_sha256"] = canonical_sha256(canonical)
    return canonical


def build_raw_submission_descriptor(*, source: str, subject: str) -> dict[str, Any]:
    if not source.strip() or not subject.strip():
        raise ValueError("source and subject are required")
    return {
        "ingress_mode": "sdk_manifested_raw_data",
        "source": source,
        "subject": subject,
        "sdk_will_create_manifest": True,
        "submission_grants_authority": False,
    }
