"""Guided parameter/submit/replay/reconstruct navigation for governed SDK runs.

This module owns user-facing instructions and ingress validation only. It does not
implement StegGate authority. A structurally valid manifest is acceptable input
to governance; it is never an ALLOW decision.

A manifest may also request how transition evidence is projected back to the
caller. That user-return projection never controls Master Records custody:
ecosystem state transitions remain eligible for canonical Master Records
recording even when the caller requests selected or no transition details back.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

INGRESS_PROFILE = "stegverse.ingress-manifest.v1"
RECEIPT_ID_RE = re.compile(r"^MR-[A-F0-9]{16,64}$")
RETURN_PROJECTION_MODES = {"ALL", "SELECTED", "NONE"}

NAVIGATION = (
    ("00", "User-defined run parameters"),
    ("0", "Submit data for governance"),
    ("1", "Replay previously run set"),
    ("2", "Reconstruct previously run set"),
)

MANIFEST_SHAPE_GUIDANCE = """MANIFEST SHAPE

Every governed run is represented by a manifest with four conceptual groups:

1. Profile and provenance
   manifest_profile, manifest_profile_version, source_framework,
   source_instance, source_output_id, created_at, freshness

2. Governed subject
   payload OR payload_commitment, candidate, declared_intent,
   requested_consequence, context_refs

3. Integrity and attestation
   canonicalization_profile, hashes, attestation, extensions

4. Caller-return projection
   return_projection.mode, return_projection.transition_classes

Required identity, integrity, governed-subject, and routing fields cannot be set
to NONE merely to hide them from governance. They are part of the canonical run.
Optional provenance/extension fields may be null or empty only where the profile
allows it.

The editable NONE control applies to caller-facing receipt projection:
- return_projection.mode = ALL      -> return all user-disclosable transition evidence;
- return_projection.mode = SELECTED -> return only named transition_classes;
- return_projection.mode = NONE     -> return no transition-detail receipt projection.

For a focused receipt request under option 00, use SELECTED and name only the
transition classes wanted back, for example:

  return_projection:
    mode: SELECTED
    transition_classes:
      - steggate
      - return_ingestion

Use NONE only when no transition-detail receipts should be returned to that
caller. NONE never means that StegVerse skipped, erased, or failed to retain the
underlying state transitions. Master Records custody is independent of this
caller-facing projection.

The manifest_receipt_id is always the canonical locator for the exact immutable
run and is not an authority token. It remains the handle for later replay or
reconstruction even when transition-detail projection is NONE.
"""

PARAMETER_GUIDANCE = """USER-DEFINED RUN PARAMETERS

Use this option to define permitted run preferences before submission, including
how governed transition evidence should be projected back in the user-facing
result.

Important boundary:
- the manifest routes the submitted unit through StegVerse and declares the
  requested user-return projection for state-transition evidence;
- return projection controls what transition evidence is returned to the caller,
  not whether ecosystem transitions occurred or were retained;
- Master Records remains the canonical ecosystem custody surface and may retain
  all state transitions required by StegVerse continuity, governance, audit, and
  reconstruction semantics;
- a caller cannot use run parameters to suppress canonical Master Records
  recording, erase a transition, grant authority, or rewrite historical state.

Return projection modes:
- ALL: return all user-disclosable transition evidence for the run;
- SELECTED: return only the requested user-disclosable transition classes;
- NONE: return no transition-detail projection to the caller. This does NOT mean
  no state transitions were recorded by StegVerse or Master Records.

The final manifest_receipt_id remains a locator for the exact immutable run and
is not execution or admissibility authority.
"""

SUBMIT_GUIDANCE = """SUBMIT DATA FOR GOVERNANCE

Choose submission type:

[0A] Submit raw/user data
     The SDK will create the governance manifest for you.

[0B] Submit a preformatted machine manifest
     Use this when another system or framework already produced a manifest
     conforming to the accepted StegVerse ingress profile.

What will happen:
- input is manifested or the supplied manifest is validated and canonicalized;
- the manifest declares routing and the requested user-return projection;
- the transaction enters canonical ingestion -> StegGate governance ->
  commit/consequence boundary -> return ingestion;
- submission and manifest validity do not grant authority;
- Master Records custody is independent of how much transition evidence is
  projected back to the caller;
- the completed run returns the permitted user-facing result and a final
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
- verification evidence for the replay, subject to the applicable return
  projection and disclosure boundary.
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
- reconstructed trajectory and chain verification subject to the applicable
  disclosure/return projection;
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


def manifest_shape_guidance() -> str:
    """Return the common manifest-shape explanation shown with every choice."""
    return MANIFEST_SHAPE_GUIDANCE


def guidance_for(selection: str) -> str:
    key = selection.strip().upper()
    if key == "00":
        specific = PARAMETER_GUIDANCE
    elif key in {"0", "0A", "0B"}:
        specific = SUBMIT_GUIDANCE
    elif key == "1":
        specific = REPLAY_GUIDANCE
    elif key == "2":
        specific = RECONSTRUCT_GUIDANCE
    else:
        raise ValueError("selection must be 00, 0, 1, or 2")
    return specific.rstrip() + "\n\n" + MANIFEST_SHAPE_GUIDANCE


def validate_manifest_receipt_id(value: str) -> str:
    normalized = value.strip().upper()
    if not RECEIPT_ID_RE.fullmatch(normalized):
        raise ValueError("manifest_receipt_id must use the canonical MR-<hex> form")
    return normalized


def normalize_return_projection(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize the caller-facing transition-evidence projection.

    This is a disclosure/return contract only. It cannot suppress canonical
    ecosystem custody or alter transition history.
    """
    projection = dict(value or {})
    mode = str(projection.get("mode") or "ALL").strip().upper()
    if mode not in RETURN_PROJECTION_MODES:
        raise ValueError("return_projection.mode must be ALL, SELECTED, or NONE")
    selected = projection.get("transition_classes") or []
    if not isinstance(selected, list) or not all(isinstance(item, str) and item.strip() for item in selected):
        raise ValueError("return_projection.transition_classes must be a list of non-empty strings")
    selected = list(dict.fromkeys(item.strip() for item in selected))
    if mode == "SELECTED" and not selected:
        raise ValueError("SELECTED return projection requires transition_classes")
    if mode != "SELECTED" and selected:
        raise ValueError("transition_classes are only valid with SELECTED return projection")
    return {
        "mode": mode,
        "transition_classes": selected,
        "controls_user_return_only": True,
        "suppresses_master_records_custody": False,
        "erases_ecosystem_transitions": False,
        "grants_authority": False,
    }


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
        "hashes", "attestation", "extensions", "return_projection",
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
    canonical["return_projection"] = normalize_return_projection(manifest.get("return_projection"))
    canonical["ingress_mode"] = "external_manifest"
    canonical["external_manifest_valid"] = True
    canonical["external_manifest_grants_authority"] = False
    canonical["master_records_transition_custody_independent_of_return_projection"] = True
    canonical["canonical_manifest_sha256"] = canonical_sha256(canonical)
    return canonical


def build_raw_submission_descriptor(*, source: str, subject: str, return_projection: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not source.strip() or not subject.strip():
        raise ValueError("source and subject are required")
    return {
        "ingress_mode": "sdk_manifested_raw_data",
        "source": source,
        "subject": subject,
        "return_projection": normalize_return_projection(return_projection),
        "sdk_will_create_manifest": True,
        "submission_grants_authority": False,
        "master_records_transition_custody_independent_of_return_projection": True,
    }
