"""Guided demo/parameter/submit/replay/reconstruct navigation for governed SDK runs.

This module owns user-facing instructions and ingress validation only. It does not
implement StegGate authority. A structurally valid manifest is acceptable input
to governance; it is never an ALLOW decision.

A manifest may request both (a) which transition evidence is projected back to
the caller and (b) which explanatory labels are attached to the returned
package. Neither return control changes canonical Master Records custody.
"""
from __future__ import annotations

import hashlib
from importlib import resources
import json
import re
from typing import Any, Mapping

INGRESS_PROFILE = "stegverse.ingress-manifest.v1"
DEMO_OUTPUT_PROFILE = "stegverse.manifest-demo-output.v1"
DEMO_DATASET_PROFILE = "stegverse.000-demo-dataset.v1"
MANIFEST_LABEL_PROFILE = "stegverse.manifest-labels.v1"
RECEIPT_ID_RE = re.compile(r"^MR-[A-F0-9]{16,64}$")
RETURN_PROJECTION_MODES = {"ALL", "SELECTED", "NONE"}
MANIFEST_LABEL_MODES = {"ALL", "SELECTED", "NONE"}
GOVERNANCE_OUTCOME_STATES = ("ALLOW", "DENY", "REVIEW", "FAIL_CLOSED")

NAVIGATION = (
    ("000", "Demo test sequence without user-supplied manifest"),
    ("00", "User-defined run parameters"),
    ("0", "Submit data for governance"),
    ("1", "Replay previously run set"),
    ("2", "Reconstruct previously run set"),
)

MANIFEST_SHAPE_GUIDANCE = """MANIFEST SHAPE

Every governed run is represented by a manifest with clearly labeled sections.
The labels are themselves requested by the manifest through `manifest_labels`.
This means the same explanatory return package demonstrated by option 000 can
also be requested on an ordinary option 0 submission.

1. Profile and provenance
   fields: manifest_profile, manifest_profile_version, source_framework,
   source_instance, source_output_id, created_at, freshness
   transition classes: ingress, provenance
   receipt classes: manifest-admission, source-identity

2. Governed subject
   fields: payload OR payload_commitment, candidate, declared_intent,
   requested_consequence, context_refs
   transition classes: subject, intent, candidate
   receipt classes: input-commitment, candidate-identity, request-identity

3. Integrity and attestation
   fields: canonicalization_profile, hashes, attestation, extensions
   transition classes: canonicalization, verification
   receipt classes: hash-verification, attestation-verification

4. Governance and consequence trajectory
   generated from the actual governed run rather than user-authored authority
   transition classes: ingestion, governance, consequence, return_ingestion
   receipt classes: MANIFEST_ADMITTED, governance-decision, execution-observation,
   RESULT_INGESTED, receipt-chain verification

5. Caller-return receipt projection
   fields: return_projection.mode, return_projection.transition_classes
   transition class: disclosure_projection
   receipt class: projection-decision

6. Return-package explanatory labels
   fields: manifest_labels.profile, manifest_labels.mode,
   manifest_labels.sections and label-detail toggles
   transition class: return_label_projection
   receipt class: manifest-label-projection

`return_projection` controls which user-disclosable transition receipts are
returned. `manifest_labels` independently controls whether explanatory titles,
descriptions, class labels, editability labels, and authority-boundary labels are
attached to that return package.

Required identity, integrity, governed-subject, and routing fields cannot be set
to NONE merely to hide them from governance. They are part of the canonical run.
Optional provenance/extension fields may be null or empty only where the profile
allows it.

Receipt projection:
- return_projection.mode = ALL      -> return all user-disclosable transition evidence;
- return_projection.mode = SELECTED -> return only named transition_classes;
- return_projection.mode = NONE     -> return no transition-detail receipt projection.

Explanation-label projection:
- manifest_labels.mode = ALL      -> label/explain all returned package sections;
- manifest_labels.mode = SELECTED -> label/explain only named sections;
- manifest_labels.mode = NONE     -> return no explanatory manifest labels.

Neither NONE mode means StegVerse skipped, erased, or failed to retain underlying
state transitions. Master Records custody is independent of both caller-facing
return controls.

The manifest_receipt_id is always the canonical locator for the exact immutable
run and is not an authority token. It remains the handle for later replay or
reconstruction even when transition-detail or explanation-label projection is
NONE.
"""

DEMO_GUIDANCE = """DEMO TEST SEQUENCE WITHOUT USER-SUPPLIED MANIFEST

This option runs a safe demonstration using an SDK-owned dataset and no
user-supplied manifest.

The dataset begins with one labeled example of every active governance outcome
class: ALLOW, DENY, REVIEW, and FAIL_CLOSED. Those outcome examples are teaching
data only. They are not prior decisions, authority, or executable instructions.

For option 000 the ENTIRE demo dataset is the submitted payload. The returned
shape therefore includes a dataset hash plus the receipt classes that must prove
manifest admission, governance processing, return ingestion, and final exact-run
custody. Until the demo is bound to the canonical runtime those runtime receipt
values remain explicitly PENDING rather than being fabricated.

Option 000 also requests `manifest_labels.mode = ALL`, so every explanatory title,
description, transition class, receipt class, editability boundary, and authority
boundary is part of the demo return package.

Purpose:
- teach the complete governance outcome vocabulary;
- make it evident which dataset was submitted as the demo payload;
- show what evidence proves that payload was processed;
- show the ordinary StegVerse process end to end;
- show the final output manifest shape the user would receive;
- make the result sufficiently self-describing that a person can reconstruct a
  conforming manifest by hand;
- make the result sufficiently machine-readable that an external LLM can propose
  a new manifest from the user's stated preferences.

Important boundary:
- the 000 dataset is demo-only and is submitted as DATA, not accepted as a user
  manifest;
- the demo teaches structure and evidence semantics; it does not grant authority;
- any later manifest proposed by a user or LLM must still pass normal profile,
  hash, provenance, governance, and consequence-boundary validation.
"""

PARAMETER_GUIDANCE = """USER-DEFINED RUN PARAMETERS

Use this option to define permitted run preferences before submission, including
which transition receipts should be returned and whether the returned package
should carry explanatory manifest labels.

Important boundary:
- return_projection controls user-visible transition evidence;
- manifest_labels controls user-visible explanatory labels;
- neither controls whether ecosystem transitions occurred or were retained;
- Master Records remains the canonical ecosystem custody surface;
- a caller cannot use run parameters to suppress canonical Master Records
  recording, erase a transition, grant authority, or rewrite historical state.

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

An option 0 manifest may include `manifest_labels`. Set `manifest_labels.mode` to
ALL when you want the returned package to include the same kind of explanatory
section descriptions, transition-class labels, receipt-class labels, editability
labels, and authority-boundary labels demonstrated by option 000.

What will happen:
- input is manifested or the supplied manifest is validated and canonicalized;
- the manifest declares routing, receipt projection, and explanation-label
  projection;
- the transaction enters canonical ingestion -> StegGate governance ->
  commit/consequence boundary -> return ingestion;
- submission and manifest validity do not grant authority;
- Master Records custody is independent of caller return formatting;
- the completed run returns the permitted user-facing result and final
  manifest_receipt_id identifying the exact immutable master-record run.
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
- verification evidence subject to applicable receipt and manifest-label
  projection boundaries.
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
- reconstructed trajectory and chain verification subject to applicable
  disclosure/label projection;
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
    return MANIFEST_SHAPE_GUIDANCE


def guidance_for(selection: str) -> str:
    key = selection.strip().upper()
    if key == "000":
        specific = DEMO_GUIDANCE
    elif key == "00":
        specific = PARAMETER_GUIDANCE
    elif key in {"0", "0A", "0B"}:
        specific = SUBMIT_GUIDANCE
    elif key == "1":
        specific = REPLAY_GUIDANCE
    elif key == "2":
        specific = RECONSTRUCT_GUIDANCE
    else:
        raise ValueError("selection must be 000, 00, 0, 1, or 2")
    return specific.rstrip() + "\n\n" + MANIFEST_SHAPE_GUIDANCE


def normalize_manifest_labels(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize explanatory labels requested for the caller-facing package."""
    labels = dict(value or {})
    profile = str(labels.get("profile") or MANIFEST_LABEL_PROFILE)
    if profile != MANIFEST_LABEL_PROFILE:
        raise ValueError(f"manifest_labels.profile must be {MANIFEST_LABEL_PROFILE}")
    mode = str(labels.get("mode") or "NONE").strip().upper()
    if mode not in MANIFEST_LABEL_MODES:
        raise ValueError("manifest_labels.mode must be ALL, SELECTED, or NONE")
    sections = labels.get("sections") or []
    if not isinstance(sections, list) or not all(isinstance(item, str) and item.strip() for item in sections):
        raise ValueError("manifest_labels.sections must be a list of non-empty strings")
    sections = list(dict.fromkeys(item.strip() for item in sections))
    if mode == "SELECTED" and not sections:
        raise ValueError("SELECTED manifest_labels requires sections")
    if mode != "SELECTED" and sections:
        raise ValueError("manifest_labels.sections are only valid with SELECTED mode")
    defaults = mode != "NONE"
    return {
        "profile": MANIFEST_LABEL_PROFILE,
        "mode": mode,
        "sections": sections,
        "include_field_descriptions": bool(labels.get("include_field_descriptions", defaults)),
        "include_transition_class_labels": bool(labels.get("include_transition_class_labels", defaults)),
        "include_receipt_class_labels": bool(labels.get("include_receipt_class_labels", defaults)),
        "include_editability_labels": bool(labels.get("include_editability_labels", defaults)),
        "include_authority_boundary_labels": bool(labels.get("include_authority_boundary_labels", defaults)),
        "controls_return_explanation_only": True,
        "changes_governance_decision": False,
        "suppresses_master_records_custody": False,
        "grants_authority": False,
    }


def _load_000_demo_dataset() -> dict[str, Any]:
    """Load and verify the SDK-owned dataset used only by option 000."""
    try:
        text = resources.files("stegverse.demo_data").joinpath(
            "manifest_000_governance_outcomes.json"
        ).read_text(encoding="utf-8")
        dataset = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"000 demo dataset unavailable or invalid: {exc}") from exc
    if not isinstance(dataset, dict):
        raise ValueError("000 demo dataset must be an object")
    if dataset.get("schema") != DEMO_DATASET_PROFILE:
        raise ValueError("000 demo dataset schema mismatch")
    if dataset.get("demo_only") is not True or dataset.get("accepted_as_user_manifest") is not False:
        raise ValueError("000 demo dataset boundary invalid")
    examples = dataset.get("governance_outcome_examples")
    if not isinstance(examples, list):
        raise ValueError("000 demo governance outcomes missing")
    states = [str(item.get("governance_state") or "") for item in examples if isinstance(item, dict)]
    if tuple(states) != GOVERNANCE_OUTCOME_STATES:
        raise ValueError("000 demo must contain exactly one example of every active governance outcome")
    return dataset


def _manifest_label(
    *,
    title: str,
    description: str,
    transition_classes: list[str],
    receipt_classes: list[str],
    editable: Any,
    authority_effect: str,
) -> dict[str, Any]:
    return {
        "profile": MANIFEST_LABEL_PROFILE,
        "title": title,
        "description": description,
        "transition_classes": transition_classes,
        "receipt_classes": receipt_classes,
        "editable": editable,
        "authority_effect": authority_effect,
    }


def demo_output_manifest_shape() -> dict[str, Any]:
    """Return the self-describing option-000 demo envelope.

    The entire SDK-owned dataset is embedded as the example manifest payload so
    the final runtime-bound demo can prove which exact dataset was admitted and
    processed. Runtime processing evidence remains explicitly pending until the
    canonical demo execution is wired.
    """
    demo_dataset = _load_000_demo_dataset()
    dataset_hash = canonical_sha256(demo_dataset)
    canonical_manifest = {
        "manifest_profile": INGRESS_PROFILE,
        "manifest_profile_version": "1",
        "source_framework": "stegverse-sdk-demo",
        "source_instance": "local-demo",
        "source_output_id": "DEMO-OUTPUT-001",
        "created_at": "<generated-at-run-time>",
        "freshness": {"status": "demo"},
        "payload": demo_dataset,
        "candidate": dict(demo_dataset["demo_input"]["candidate"]),
        "declared_intent": demo_dataset["demo_input"]["declared_intent"],
        "requested_consequence": demo_dataset["demo_input"]["requested_consequence"],
        "context_refs": [],
        "canonicalization_profile": "steggate.jcs.v1",
        "hashes": {
            "payload_sha256": dataset_hash,
            "candidate_sha256": canonical_sha256(demo_dataset["demo_input"]["candidate"]),
        },
        "attestation": None,
        "extensions": {},
        "return_projection": {"mode": "ALL", "transition_classes": []},
        "manifest_labels": normalize_manifest_labels({"mode": "ALL"}),
    }

    section_specs = [
        (
            "profile_provenance", "Profile and provenance",
            "Identifies the manifest profile, source, run instance, source output, and freshness context.",
            ["manifest_profile", "manifest_profile_version", "source_framework", "source_instance", "source_output_id", "created_at", "freshness"],
            ["ingress", "provenance"], ["manifest-admission", "source-identity"], True, "NONE",
        ),
        (
            "governed_subject", "Governed subject",
            "Identifies the exact submitted data, candidate action, declared intent, requested consequence, and context.",
            ["payload|payload_commitment", "candidate", "declared_intent", "requested_consequence", "context_refs"],
            ["subject", "intent", "candidate"], ["input-commitment", "candidate-identity", "request-identity"], True, "NONE",
        ),
        (
            "integrity_attestation", "Integrity and attestation",
            "Shows canonicalization, hashes, attestations, and bounded extensions used to verify what was submitted.",
            ["canonicalization_profile", "hashes", "attestation", "extensions"],
            ["canonicalization", "verification"], ["hash-verification", "attestation-verification"], "profile-bounded", "NONE",
        ),
        (
            "governed_trajectory", "Governance and consequence trajectory",
            "Shows runtime-generated admission, governance, consequence observation, and return-ingestion evidence.",
            ["generated_transition_receipts", "governance_state", "consequence_executed", "receipt_chain_head"],
            ["ingestion", "governance", "consequence", "return_ingestion"], ["MANIFEST_ADMITTED", "governance-decision", "execution-observation", "RESULT_INGESTED", "receipt-chain-verification"], False, "OBSERVATION_ONLY",
        ),
        (
            "caller_return_projection", "Caller-return receipt projection",
            "Explains which user-disclosable transition receipts were requested for the returned package.",
            ["return_projection.mode", "return_projection.transition_classes"],
            ["disclosure_projection"], ["projection-decision"], True, "NONE",
        ),
        (
            "return_manifest_labels", "Return-package manifest labels",
            "Explains which human/LLM-readable titles, descriptions, class labels, and boundary labels were requested on return.",
            ["manifest_labels.profile", "manifest_labels.mode", "manifest_labels.sections"],
            ["return_label_projection"], ["manifest-label-projection"], True, "NONE",
        ),
        (
            "exact_run_locator", "Exact-run locator",
            "Identifies the final immutable run handle used for later replay and reconstruction.",
            ["manifest_receipt_id"], ["custody_reference"], ["manifest-receipt"], False, "LOCATOR_ONLY",
        ),
    ]
    sections = []
    for section_id, title, description, fields, transition_classes, receipt_classes, editable, authority_effect in section_specs:
        sections.append(
            {
                "section_id": section_id,
                "fields": fields,
                "manifest_label": _manifest_label(
                    title=title,
                    description=description,
                    transition_classes=transition_classes,
                    receipt_classes=receipt_classes,
                    editable=editable,
                    authority_effect=authority_effect,
                ),
            }
        )

    return {
        "schema": DEMO_OUTPUT_PROFILE,
        "purpose": "self-describing manifest example for human or LLM-assisted reconstruction",
        "000_governance_outcome_dataset": demo_dataset,
        "demo_dataset_processing": {
            "dataset_schema": DEMO_DATASET_PROFILE,
            "dataset_sha256": dataset_hash,
            "submitted_as": "canonical_manifest_example.payload",
            "dataset_loaded_into_demo_manifest": True,
            "canonical_processing_status": "PENDING_RUNTIME_BINDING",
            "required_processing_receipt_classes": [
                "MANIFEST_ADMITTED",
                "governance-decision",
                "RESULT_INGESTED",
                "manifest-receipt",
            ],
            "required_final_fields": [
                "manifest_receipt_id",
                "receipt_chain_head",
                "governance_state",
                "chain_verified",
            ],
            "do_not_claim_processed_until_receipts_exist": True,
        },
        "canonical_input_profile": INGRESS_PROFILE,
        "canonical_manifest_example": canonical_manifest,
        "sections": sections,
        "process_sequence": [
            {"order": 0, "stage": "manifestation", "transition_class": "ingress", "receipt_class": "manifest-admission"},
            {"order": 1, "stage": "ingestion", "transition_class": "ingestion", "receipt_class": "MANIFEST_ADMITTED"},
            {"order": 2, "stage": "steggate", "transition_class": "governance", "receipt_class": "governance-decision"},
            {"order": 3, "stage": "consequence_boundary", "transition_class": "consequence", "receipt_class": "execution-observation"},
            {"order": 4, "stage": "return_ingestion", "transition_class": "return_ingestion", "receipt_class": "RESULT_INGESTED"},
            {"order": 5, "stage": "master_records", "transition_class": "custody", "receipt_class": "manifest-receipt"},
            {"order": 6, "stage": "caller_projection", "transition_class": "disclosure_projection", "receipt_class": "projection-decision"},
            {"order": 7, "stage": "return_labeling", "transition_class": "return_label_projection", "receipt_class": "manifest-label-projection"},
        ],
        "reconstruction_notes": {
            "human": "Verify demo_dataset_processing first. Then copy canonical_manifest_example, replace editable values, recompute required hashes, choose receipt/label projections, and submit through the normal manifest path.",
            "llm": "Treat manifest_label objects as explanatory metadata requested by the manifest. Produce a new stegverse.ingress-manifest.v1 object; preserve or modify manifest_labels according to the user's desired return explanations, and never copy demo governance outcomes as authority.",
            "master_records_custody_independent_of_caller_projection": True,
        },
        "demo_grants_authority": False,
    }


def validate_manifest_receipt_id(value: str) -> str:
    normalized = value.strip().upper()
    if not RECEIPT_ID_RE.fullmatch(normalized):
        raise ValueError("manifest_receipt_id must use the canonical MR-<hex> form")
    return normalized


def normalize_return_projection(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize the caller-facing transition-evidence projection."""
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
    """Validate and canonicalize a machine-produced ingress manifest."""
    allowed = {
        "manifest_profile", "manifest_profile_version", "source_framework",
        "source_instance", "source_output_id", "created_at", "freshness",
        "payload", "payload_commitment", "candidate", "declared_intent",
        "requested_consequence", "context_refs", "canonicalization_profile",
        "hashes", "attestation", "extensions", "return_projection",
        "manifest_labels",
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
    canonical["manifest_labels"] = normalize_manifest_labels(manifest.get("manifest_labels"))
    canonical["ingress_mode"] = "external_manifest"
    canonical["external_manifest_valid"] = True
    canonical["external_manifest_grants_authority"] = False
    canonical["master_records_transition_custody_independent_of_return_projection"] = True
    canonical["manifest_labels_change_governance"] = False
    canonical["canonical_manifest_sha256"] = canonical_sha256(canonical)
    return canonical


def build_raw_submission_descriptor(
    *,
    source: str,
    subject: str,
    return_projection: Mapping[str, Any] | None = None,
    manifest_labels: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not source.strip() or not subject.strip():
        raise ValueError("source and subject are required")
    return {
        "ingress_mode": "sdk_manifested_raw_data",
        "source": source,
        "subject": subject,
        "return_projection": normalize_return_projection(return_projection),
        "manifest_labels": normalize_manifest_labels(manifest_labels),
        "sdk_will_create_manifest": True,
        "submission_grants_authority": False,
        "master_records_transition_custody_independent_of_return_projection": True,
    }
