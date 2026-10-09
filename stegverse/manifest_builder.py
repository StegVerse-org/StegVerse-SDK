"""User/framework-facing builder for canonical StegVerse ingress manifests.

The builder is a construction and validation convenience layer only. It does not
perform governance, diagnostics, infer missing processor evidence, grant authority,
or alter the semantic meaning of a caller's source-native payload.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .ecosystem_diagnostic_runtime import REQUEST_EXTENSION, validate_diagnostic_request
from .purpose_bound_worker_processor import REQUEST_EXTENSION as PURPOSE_BOUND_WORKER_REQUEST_EXTENSION, validate_purpose_bound_worker_request
from .atomic_task_worker_processor import REQUEST_EXTENSION as ATOMIC_TASK_WORKER_REQUEST_EXTENSION, validate_atomic_task_worker_request
from .svg_governance_cycle_processor import REQUEST_EXTENSION as SVG_GOVERNANCE_CYCLE_REQUEST_EXTENSION, validate_svg_governance_cycle_request
from .stegbrowser_processor import REQUEST_EXTENSION as STEGBROWSER_REQUEST_EXTENSION, validate_stegbrowser_request
from .organization_role_conformance_processor import REQUEST_EXTENSION as ORGANIZATION_ROLE_CONFORMANCE_REQUEST_EXTENSION, validate_organization_role_conformance_request
from .governance_navigation import INGRESS_PROFILE, canonical_sha256
from .governance_reference_graph import (
    EXTENSION_KEY as GOVERNANCE_REFERENCE_GRAPH_EXTENSION,
    validate_governance_reference_graph,
)
from .capability_graph import (
    CLOSURE_RESOLVED,
    EXTENSION_KEY as CAPABILITY_GRAPH_EXTENSION,
    resolve_declared_capabilities,
)
from .manifest_contract import validate_ingress_manifest
from .capability_inventory import DEFAULT_MAX_EVIDENCE_AGE_SECONDS, EvidenceVerifier, hmac_evidence_verifier
from .manifest_plan import QUALIFIED_READY, qualify_manifest_readiness
from .capability_resolution import ONLINE, OFFLINE, UNKNOWN_CAPABILITY, capability_development_request, classify_capability
from .route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
    ECOSYSTEM_DIAGNOSTIC_ROUTE_ID,
    PURPOSE_BOUND_WORKER_ROUTE_ID,
    ATOMIC_TASK_WORKER_ROUTE_ID,
    SVG_GOVERNANCE_CYCLE_ROUTE_ID,
    STEGBROWSER_ROUTE_ID,
    ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID,
    PUBLISHED_ROUTES,
)

LOCAL_CONFORMANCE = "LOCAL_CONFORMANCE"
ECOSYSTEM_CONNECTED = "ECOSYSTEM_CONNECTED"
EXECUTION_PROFILES = (LOCAL_CONFORMANCE, ECOSYSTEM_CONNECTED)
GOVERNANCE_PROFILE_ROUTES = {
    LOCAL_CONFORMANCE: CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
    ECOSYSTEM_CONNECTED: CANONICAL_PRODUCTION_ROUTE_ID,
}

PROCESSOR_ROUTES = {
    "governance": CANONICAL_PRODUCTION_ROUTE_ID,
    "ecosystem_diagnostic": ECOSYSTEM_DIAGNOSTIC_ROUTE_ID,
    "purpose_bound_worker": PURPOSE_BOUND_WORKER_ROUTE_ID,
    "atomic_task_worker": ATOMIC_TASK_WORKER_ROUTE_ID,
    "svg_governance_cycle": SVG_GOVERNANCE_CYCLE_ROUTE_ID,
    "stegbrowser": STEGBROWSER_ROUTE_ID,
    "organization_role_conformance": ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID,
}

GOVERNANCE_REQUEST_FIELDS = (
    "candidate", "judgment", "signal", "execution", "capability",
    "continuity", "approval", "permission_present",
)

RETURN_DEPTHS = {
    "result-only": {"mode": "SELECTED", "transition_classes": ["governance"]},
    "result+evidence": {
        "mode": "SELECTED",
        "transition_classes": ["ingestion", "governance", "consequence", "return_ingestion", "custody"],
    },
    "full-trace": {"mode": "ALL", "transition_classes": []},
    "locator-only": {"mode": "NONE", "transition_classes": []},
}

DIAGNOSTIC_RETURN_DEPTHS = {
    "result-only": {"mode": "SELECTED", "transition_classes": ["diagnostic"]},
    "result+evidence": {"mode": "SELECTED", "transition_classes": ["ingestion", "diagnostic", "custody"]},
    "full-trace": {"mode": "ALL", "transition_classes": []},
    "locator-only": {"mode": "NONE", "transition_classes": []},
}

DEFAULT_PUBLISHER_PACKAGE_PROFILE = "stegverse.publisher.evidence-report-package/v1"
DEFAULT_FRAMEWORK_EGRESS_SURFACE = "LLM_ADAPTER"  # requester return adapter; never organization routing


_CORRECTABLE_MANIFEST_BINDING_DENIALS = frozenset({
    "canonical_manifest_sha256_binding_mismatch",
    "canonical_manifest_sha256_recompute_mismatch",
    "wire_manifest_sha256_required",
    "wire_manifest_sha256_mismatch",
    "canonical_manifest_projection_required",
    "canonical_manifest_projection_sha256_mismatch",
})


def correct_manifest_binding_deny(
    original_manifest: Mapping[str, Any],
    rejected_request: Mapping[str, Any],
    denial: Mapping[str, Any],
) -> dict[str, Any]:
    """Correct the outgoing envelope, never the frozen original manifest.

    The profile's exact DENY is diagnostic evidence only. A changed envelope
    must be submitted as a separate governed attempt to receive its own verdict.
    No retry is permitted for FAIL_CLOSED or for an unchanged envelope.
    """
    from .manifest_state_transition_runtime import derive_execution_request

    if denial.get("state") != "DENY" or denial.get("terminal") is not False:
        raise ValueError("terminal_or_non_deny_disposition_cannot_be_repaired")
    reason = denial.get("reason_code")
    if reason not in _CORRECTABLE_MANIFEST_BINDING_DENIALS:
        raise ValueError("manifest_builder_has_no_approved_repair_for_reason")
    if denial.get("transition_id") != "SDK_MANIFEST_BINDING":
        raise ValueError("denial_transition_identity_mismatch")
    if denial.get("retry_condition") != (
        "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT"
    ):
        raise ValueError("denial_does_not_permit_manifest_builder_reentry")
    wire = dict(original_manifest)
    if rejected_request.get("canonical_manifest") != wire:
        raise ValueError("denial_rejected_different_original_manifest")
    original_wire_hash = canonical_sha256(wire)
    if denial.get("original_wire_manifest_sha256") != original_wire_hash:
        raise ValueError("denial_original_wire_manifest_sha256_mismatch")
    rejected_hash = canonical_sha256(dict(rejected_request))
    if denial.get("original_request_sha256") != rejected_hash:
        raise ValueError("denial_original_request_sha256_mismatch")
    repaired = derive_execution_request(wire)
    if repaired["request_sha256"] == rejected_request.get("request_sha256"):
        raise ValueError("manifest_binding_repair_produced_unchanged_request")
    if repaired["wire_manifest_sha256"] != original_wire_hash:
        raise ValueError("manifest_builder_changed_frozen_wire_manifest")
    return repaired


def available_processors() -> tuple[str, ...]:
    installed = []
    for name, route_id in PROCESSOR_ROUTES.items():
        route = PUBLISHED_ROUTES.get(route_id) or {}
        if route.get("runtime_installed") is True and route.get("processor_capability") == name:
            installed.append(name)
    return tuple(sorted(installed))


def compatible_routes(process: str) -> tuple[dict[str, Any], ...]:
    """Expose compatible published routes without treating one as fallback for another."""
    normalized = process.strip().lower()
    if normalized != "governance":
        return ()
    candidates = []
    for profile, route_id in GOVERNANCE_PROFILE_ROUTES.items():
        route = PUBLISHED_ROUTES.get(route_id) or {}
        if route.get("processor_capability") != normalized:
            continue
        candidates.append({
            "route_id": route_id,
            "execution_profile": profile,
            "sdk_runtime_binding_installed": route.get("runtime_installed") is True,
            "operational_availability": "REQUIRES_EXECUTION_PROFILE_EVIDENCE",
            "automatic_substitution_permitted": False,
        })
    return tuple(candidates)


def _route_declaration(
    process: str, execution_profile: str = ECOSYSTEM_CONNECTED
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    normalized = process.strip().lower()
    profile = execution_profile.strip().upper()
    if profile not in EXECUTION_PROFILES:
        raise ValueError("unsupported execution_profile: " + execution_profile)
    if normalized != "governance" and profile != ECOSYSTEM_CONNECTED:
        raise ValueError("LOCAL_CONFORMANCE is currently defined only for governance")
    processor_routes = dict(PROCESSOR_ROUTES)
    if normalized == "governance":
        processor_routes["governance"] = GOVERNANCE_PROFILE_ROUTES[profile]
    resolution = classify_capability(normalized, processor_routes, PUBLISHED_ROUTES)
    if resolution["status"] != ONLINE:
        return None, resolution
    route_id = resolution["route_id"]
    published = PUBLISHED_ROUTES[route_id]
    if published.get("processor_capability") != normalized:
        raise ValueError(f"route {route_id!r} is not bound to processing capability {normalized!r}")
    return {
        "route_id": published["route_id"],
        "lane_class": published["lane_class"],
        "routing_surface": published["routing_surface"],
        "containment": published["containment"],
        "sandbox_required": published["sandbox_required"],
        "external_consequence_enabled": published["external_consequence_enabled"],
    }, resolution


def _validate_governance_request(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(
            "governance processing requires a complete processor_request object; "
            "the Manifest Builder does not synthesize governance evidence"
        )
    missing = [field for field in GOVERNANCE_REQUEST_FIELDS if field not in value]
    if missing:
        raise ValueError("processor_request is missing required governance fields: " + ", ".join(missing))
    candidate = value.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("processor_request.candidate must be an object")
    return deepcopy(dict(value))


def _projection_for(process: str, depth_key: str) -> dict[str, Any]:
    source = DIAGNOSTIC_RETURN_DEPTHS if process == "ecosystem_diagnostic" else RETURN_DEPTHS
    if depth_key not in source:
        raise ValueError(f"unsupported return_depth {depth_key!r}; choices: " + ", ".join(sorted(source)))
    return deepcopy(source[depth_key])


def _completion_contract(
    *,
    initiator_class: str,
    initiator_ref: str,
    publisher_destination: Mapping[str, Any] | None,
    publisher_package_profile: str,
    egress_surface: str,
    destination_profile: str | None,
) -> dict[str, Any]:
    for label, value in (
        ("initiator_class", initiator_class),
        ("initiator_ref", initiator_ref),
        ("publisher_package_profile", publisher_package_profile),
        ("egress_surface", egress_surface),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} is required")
    if destination_profile is not None and (
        not isinstance(destination_profile, str) or not destination_profile.strip()
    ):
        raise ValueError("destination_profile must be a non-empty string when supplied")
    # Completion return binding only. Outbound organization routing is resolved
    # from the canonical capability/connector mapping, never from this value.
    egress = {
        "final_stegverse_transition_surface": egress_surface.strip(),
        "transport": "INTERLOCK_INTR",
        "far_side_transition_required": True,
    }
    if destination_profile is not None:
        egress["destination_profile"] = destination_profile.strip()
    completion = {
        "direction": "SOUTH",
        "initiator": {"class": initiator_class.strip(), "ref": initiator_ref.strip()},
        "egress": egress,
    }
    if publisher_destination is not None:
        if not isinstance(publisher_destination, Mapping):
            raise ValueError("publisher_destination must be an object when supplied")
        completion["publisher"] = {
            "stage": "PUBLISHER",
            "package_profile": publisher_package_profile.strip(),
            "destination": deepcopy(dict(publisher_destination)),
        }
    return completion


def build_manifest(
    *,
    data: Any,
    source_framework: str,
    source_output_id: str,
    processor_request: Mapping[str, Any],
    process: str = "governance",
    execution_profile: str = ECOSYSTEM_CONNECTED,
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
    context_refs: list[str] | None = None,
    declared_intent: str | None = None,
    requested_consequence: str | None = None,
    manifest_labels: Mapping[str, Any] | None = None,
    initiator_class: str = "external_framework",
    initiator_ref: str | None = None,
    publisher_required: bool | None = None,
    publisher_destination: Mapping[str, Any] | None = None,
    external_review: bool = False,
    publisher_package_profile: str = DEFAULT_PUBLISHER_PACKAGE_PROFILE,
    egress_surface: str = DEFAULT_FRAMEWORK_EGRESS_SURFACE,
    destination_profile: str | None = None,
    governance_reference_graph: Mapping[str, Any] | None = None,
    capability_graph: Mapping[str, Any] | None = None,
    workaround_selection: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(source_framework, str) or not source_framework.strip():
        raise ValueError("source_framework is required")
    if not isinstance(source_output_id, str) or not source_output_id.strip():
        raise ValueError("source_output_id is required")

    normalized_process = process.strip().lower()
    normalized_execution_profile = execution_profile.strip().upper()
    route, capability_resolution = _route_declaration(normalized_process, normalized_execution_profile)
    if capability_resolution["status"] == UNKNOWN_CAPABILITY:
        return {
            "schema": "stegverse.manifest-build-resolution/v1",
            "state": "CAPABILITY_DEVELOPMENT_REQUESTED",
            "capability_resolution": capability_resolution,
            "capability_development_request": capability_development_request(
                capability=normalized_process, processor_request=processor_request,
                source_framework=source_framework, source_output_id=source_output_id,
            ),
            "authority_effect": "NONE_REQUEST_ONLY",
        }
    if capability_resolution["status"] == OFFLINE:
        return {
            "schema": "stegverse.manifest-build-resolution/v1",
            "state": "CAPABILITY_WORKAROUND_REQUIRED",
            "capability_resolution": capability_resolution,
            "original_processor_request": deepcopy(dict(processor_request)),
            "authority_effect": "NONE_WORKAROUND_SELECTION_REQUIRED",
        }
    assert route is not None
    extensions: dict[str, Any] = {"stegverse_route": route, "capability_resolution": capability_resolution}
    if governance_reference_graph is not None:
        extensions[GOVERNANCE_REFERENCE_GRAPH_EXTENSION] = validate_governance_reference_graph(
            governance_reference_graph
        )
    if capability_graph is not None:
        capability_closure = resolve_declared_capabilities(
            capability_graph,
            processor_routes=PROCESSOR_ROUTES,
            published_routes=PUBLISHED_ROUTES,
            source_framework=source_framework,
            source_output_id=source_output_id,
            processor_request=processor_request,
        )
        if capability_closure["root_capability"] != normalized_process:
            raise ValueError(
                "capability graph root "
                f"{capability_closure['root_capability']!r} does not match declared "
                f"processing capability {normalized_process!r}"
            )
        if capability_closure["verdict"] != CLOSURE_RESOLVED:
            return {
                "schema": "stegverse.manifest-build-resolution/v1",
                "state": "CAPABILITY_CLOSURE_UNRESOLVED",
                "capability_closure": capability_closure,
                "original_processor_request": deepcopy(dict(processor_request)),
                "authority_effect": "NONE_RESOLUTION_ONLY",
            }
        extensions[CAPABILITY_GRAPH_EXTENSION] = capability_closure
    candidate = None
    hashes: dict[str, Any] = {"payload_sha256": canonical_sha256(data)}

    if normalized_process == "governance":
        normalized_request = _validate_governance_request(processor_request)
        candidate = deepcopy(dict(normalized_request["candidate"]))
        hashes["candidate_sha256"] = canonical_sha256(candidate)
        extensions["stegverse_governance_request"] = normalized_request
    elif normalized_process == "ecosystem_diagnostic":
        normalized_request = validate_diagnostic_request(processor_request)
        extensions[REQUEST_EXTENSION] = normalized_request
    elif normalized_process == "purpose_bound_worker":
        normalized_request = validate_purpose_bound_worker_request(processor_request)
        extensions[PURPOSE_BOUND_WORKER_REQUEST_EXTENSION] = normalized_request
    elif normalized_process == "atomic_task_worker":
        normalized_request = validate_atomic_task_worker_request(processor_request)
        extensions[ATOMIC_TASK_WORKER_REQUEST_EXTENSION] = normalized_request
    elif normalized_process == "svg_governance_cycle":
        normalized_request = validate_svg_governance_cycle_request(processor_request)
        extensions[SVG_GOVERNANCE_CYCLE_REQUEST_EXTENSION] = normalized_request
    elif normalized_process == "stegbrowser":
        normalized_request = validate_stegbrowser_request(processor_request)
        extensions[STEGBROWSER_REQUEST_EXTENSION] = normalized_request
    elif normalized_process == "organization_role_conformance":
        normalized_request = validate_organization_role_conformance_request(processor_request)
        extensions[ORGANIZATION_ROLE_CONFORMANCE_REQUEST_EXTENSION] = normalized_request
    else:
        raise ValueError(f"processing capability {normalized_process!r} has no builder binding")

    depth_key = return_depth.strip().lower()
    return_projection = _projection_for(normalized_process, depth_key)
    timestamp = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    processing = {"capability": normalized_process, "route_id": route["route_id"]}
    extensions["manifest_builder"] = {
        "profile": "stegverse.manifest-builder.v1",
        "processing_capability": normalized_process,
        "capability_status": capability_resolution["status"],
        "route_id": route["route_id"],
        "return_depth": depth_key,
        "source_semantic_custody": "EXTERNAL",
        "builder_grants_authority": False,
        "external_review_requested": external_review,
        "publisher_required_by_review_default": False,
        "publisher_selected_by_destination": publisher_destination is not None,
    }
    if normalized_process == "governance":
        extensions["manifest_builder"]["execution_profile"] = normalized_execution_profile
        extensions["manifest_builder"]["compatible_routes"] = list(compatible_routes(normalized_process))
        extensions["manifest_builder"]["automatic_route_substitution_permitted"] = False
    if workaround_selection is not None:
        # Bound into the new manifest digest; a selection never rides beside it.
        extensions[WORKAROUND_SELECTION_EXTENSION] = deepcopy(dict(workaround_selection))
    if data_class is not None:
        if not isinstance(data_class, str) or not data_class.strip():
            raise ValueError("data_class must be a non-empty string when supplied")
        extensions["source_data_class"] = data_class.strip()

    manifest: dict[str, Any] = {
        "manifest_profile": INGRESS_PROFILE,
        "manifest_profile_version": "1",
        "source_framework": source_framework.strip(),
        "source_instance": source_instance,
        "source_output_id": source_output_id.strip(),
        "created_at": timestamp,
        "freshness": {},
        "payload": deepcopy(data),
        "processing": processing,
        "declared_intent": declared_intent
        or f"Process source-native manifested data through installed {normalized_process} processing.",
        "requested_consequence": requested_consequence
        or "Complete the manifested governed communication lifecycle and return the requested artifact without caller-authored authority.",
        "context_refs": list(context_refs or []),
        "canonicalization_profile": "steggate.jcs.v1",
        "hashes": hashes,
        "attestation": None,
        "extensions": extensions,
        "return_projection": return_projection,
        "completion": (
            None if normalized_execution_profile == LOCAL_CONFORMANCE
            else _completion_contract(
                initiator_class=initiator_class,
                initiator_ref=initiator_ref or source_framework,
                publisher_destination=publisher_destination,
                publisher_package_profile=publisher_package_profile,
                egress_surface=egress_surface,
                destination_profile=destination_profile,
            )
        ),
        "manifest_labels": dict(manifest_labels or {"mode": "NONE"}),
    }
    if candidate is not None:
        manifest["candidate"] = candidate

    validate_ingress_manifest(manifest)
    return manifest


WORKAROUND_SELECTION_EXTENSION = "stegverse_workaround_selection"
BUILD_QUALIFICATION_SCHEMA = "stegverse.manifest-build-qualification/v1"


def qualify_draft_manifest(
    manifest: Mapping[str, Any],
    *,
    attempt_id: str,
    readiness_evidence: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] = (),
    evidence_verifier: EvidenceVerifier | None = None,
    now: datetime | None = None,
    max_evidence_age_seconds: int = DEFAULT_MAX_EVIDENCE_AGE_SECONDS,
    alternative_routes: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    """Wrap a schema-valid draft with its non-authorizing readiness qualification.

    The draft is always preserved for editing. ``executable`` is true only when
    every required node of the manifest-selected path is READY on supplied,
    authenticated, invocation-bound evidence; this never grants authority.
    """
    qualification = qualify_manifest_readiness(
        manifest,
        attempt_id=attempt_id,
        readiness_evidence=readiness_evidence,
        evidence_verifier=evidence_verifier,
        now=now,
        max_evidence_age_seconds=max_evidence_age_seconds,
        alternative_routes=alternative_routes,
    )
    ready = qualification["qualification"] == QUALIFIED_READY
    return {
        "schema": BUILD_QUALIFICATION_SCHEMA,
        "state": "READY" if ready else "NOT_READY",
        "disposition": qualification["disposition"],
        "failed_predicate": qualification["failed_predicate"],
        "draft_manifest": deepcopy(dict(manifest)),
        "draft_manifest_sha256": qualification["manifest_sha256"],
        "executable": ready,
        "qualification": qualification,
        "builder_grants_authority": False,
        "runtime_allow_claimed": False,
        "authority_effect": "NONE_QUALIFICATION_ONLY",
    }


def build_qualified_manifest(
    *,
    attempt_id: str,
    readiness_evidence: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] = (),
    evidence_verifier: EvidenceVerifier | None = None,
    now: datetime | None = None,
    max_evidence_age_seconds: int = DEFAULT_MAX_EVIDENCE_AGE_SECONDS,
    alternative_routes: tuple[str, ...] | list[str] = (),
    **build_kwargs: Any,
) -> dict[str, Any]:
    """Build a manifest, then qualify the exact manifest-selected path."""
    built = build_manifest(**build_kwargs)
    if built.get("manifest_profile") is None:
        return {
            "schema": BUILD_QUALIFICATION_SCHEMA,
            "state": built.get("state"),
            "disposition": "FAIL_CLOSED",
            "failed_predicate": "MANIFEST_BUILDER_PRODUCED_EXECUTABLE_MANIFEST",
            "resolution": built,
            "executable": False,
            "authority_effect": "NONE_RESOLUTION_ONLY",
        }
    return qualify_draft_manifest(
        built, attempt_id=attempt_id, readiness_evidence=readiness_evidence,
        evidence_verifier=evidence_verifier, now=now,
        max_evidence_age_seconds=max_evidence_age_seconds, alternative_routes=alternative_routes,
    )


def apply_workaround_selection(
    build_result: Mapping[str, Any],
    *,
    route_id: str,
    user_selection: Mapping[str, Any],
    build_kwargs: Mapping[str, Any],
    attempt_id: str,
    readiness_evidence: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] = (),
    evidence_verifier: EvidenceVerifier | None = None,
    now: datetime | None = None,
    max_evidence_age_seconds: int = DEFAULT_MAX_EVIDENCE_AGE_SECONDS,
) -> dict[str, Any]:
    """Build a new manifest for an explicitly user-selected verified workaround.

    Only a VERIFIED candidate of a NOT_READY build may be selected, the user
    must acknowledge every degraded function, and the result is a new manifest
    (new digest) that is qualified afresh. Nothing is dispatched here.
    """
    qualification = build_result.get("qualification") or {}
    workarounds = qualification.get("workarounds") or {}
    candidate = next(
        (c for c in workarounds.get("candidates") or () if c.get("route_id") == route_id), None
    )
    if candidate is None or candidate.get("candidate_state") != "VERIFIED_REQUIRES_USER_SELECTION":
        raise ValueError("WORKAROUND_NOT_VERIFIED: only an independently READY declared alternative may be selected")
    original_sha256 = build_result.get("draft_manifest_sha256")
    if (
        not isinstance(user_selection, Mapping)
        or user_selection.get("explicit") is not True
        or user_selection.get("selected_route_id") != route_id
        or user_selection.get("original_manifest_sha256") != original_sha256
        or not isinstance(user_selection.get("selected_by"), str) or not user_selection.get("selected_by")
        or not set(candidate["degraded_functions"]) <= set(user_selection.get("acknowledged_degraded_functions") or ())
    ):
        raise ValueError("EXPLICIT_USER_SELECTION_REQUIRED: selection must name the route, original digest and every degraded function")
    profile = next((p for p, r in GOVERNANCE_PROFILE_ROUTES.items() if r == route_id), None)
    if profile is None:
        raise ValueError("WORKAROUND_ROUTE_HAS_NO_BUILDER_BINDING")
    selection = {
        "schema": "stegverse.workaround-selection/v1",
        "supersedes_manifest_sha256": original_sha256,
        "original_route_id": qualification.get("route_id"),
        "selected_route_id": route_id,
        "degraded_functions": list(candidate["degraded_functions"]),
        "user_selection": deepcopy(dict(user_selection)),
        "automatic": False,
    }
    kwargs = dict(build_kwargs)
    kwargs.update(execution_profile=profile, workaround_selection=selection)
    rebuilt = build_qualified_manifest(
        attempt_id=attempt_id, readiness_evidence=readiness_evidence,
        evidence_verifier=evidence_verifier, now=now,
        max_evidence_age_seconds=max_evidence_age_seconds, **kwargs,
    )
    if rebuilt.get("draft_manifest_sha256") in (None, original_sha256):
        raise ValueError("WORKAROUND_SELECTION_REQUIRES_NEW_MANIFEST_DIGEST")
    rebuilt["workaround_selection"] = selection
    return rebuilt


def load_readiness_inputs(evidence_path: str | None, keys_path: str | None) -> tuple[list[Any], EvidenceVerifier | None]:
    """CLI helper: evidence records and the operator-configured HMAC key set."""
    evidence = _load_json(evidence_path) if evidence_path else []
    if not isinstance(evidence, list):
        raise ValueError("readiness evidence must be a JSON array of evidence records")
    verifier = None
    if keys_path:
        keys = _load_json(keys_path)
        if not isinstance(keys, Mapping) or not all(isinstance(v, str) for v in keys.values()):
            raise ValueError("readiness keys must be a JSON object of key_id -> hex key")
        verifier = hmac_evidence_verifier(keys)
    return evidence, verifier


def _load_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def _write_json(value: Any, path: str | None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stegverse manifest", description="Build canonical StegVerse ingress manifests from source-native data.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build and validate a canonical ingress manifest")
    build.add_argument("--input", required=True, help="JSON file containing source-native data")
    build.add_argument("--processor-request", help="JSON file containing the complete selected processor request")
    build.add_argument("--governance-request", help="legacy alias for --processor-request when --process=governance")
    build.add_argument("--source-framework", required=True)
    build.add_argument("--source-output-id", required=True)
    build.add_argument("--source-instance")
    build.add_argument("--data-class")
    build.add_argument("--process", default="governance", help="requested processing capability; unknown names create a capability-development request")
    build.add_argument("--execution-profile", default=ECOSYSTEM_CONNECTED, choices=EXECUTION_PROFILES, help="governance execution scope; selects exactly one published governance route and never grants authority")
    build.add_argument("--return-depth", default="result+evidence", choices=sorted(RETURN_DEPTHS))
    build.add_argument("--initiator-class", default="external_framework")
    build.add_argument("--initiator-ref")
    publisher_selection = build.add_mutually_exclusive_group()
    publisher_selection.add_argument("--publisher-required", dest="publisher_required", action="store_true")
    publisher_selection.add_argument("--no-publisher", dest="publisher_required", action="store_false")
    build.set_defaults(publisher_required=None)
    build.add_argument("--publisher-destination-type", choices=["SDK_CONSOLE_SESSION", "ECOSYSTEM_CHAT_SESSION", "KV"])
    build.add_argument("--publisher-session-ref")
    build.add_argument("--publisher-kv-class", choices=["MyKV", "OrgKV", "OrgMemberKV", "CompanyKV", "CompanyEmployeeKV"])
    build.add_argument("--publisher-kv-context-ref")
    build.add_argument("--external-review", action="store_true", help="review-facing artifact; Publisher defaults to required unless explicitly overridden")
    build.add_argument("--publisher-package-profile", default=DEFAULT_PUBLISHER_PACKAGE_PROFILE)
    build.add_argument("--egress-surface", default=DEFAULT_FRAMEWORK_EGRESS_SURFACE)
    build.add_argument("--destination-profile")
    build.add_argument("--governance-reference-graph", help="JSON file containing a hash-bound non-authorizing Governance Reference Graph")
    build.add_argument("--created-at")
    build.add_argument("--attempt-id", help="qualify readiness for this attempt; output is a build-qualification wrapper")
    build.add_argument("--readiness-evidence", help="JSON array of authenticated invocation-bound component readiness evidence")
    build.add_argument("--readiness-keys", help="JSON object key_id -> hex HMAC key trusted for readiness evidence")
    build.add_argument("--output", help="write manifest JSON to this path; default stdout")

    args = parser.parse_args(argv)
    if args.command == "build":
        try:
            request_path = args.processor_request or args.governance_request
            if not request_path:
                raise ValueError("--processor-request is required (or --governance-request for governance compatibility)")
            if args.process != "governance" and args.governance_request and not args.processor_request:
                raise ValueError("non-governance processing requires --processor-request")
            manifest = build_manifest(
                data=_load_json(args.input),
                source_framework=args.source_framework,
                source_output_id=args.source_output_id,
                source_instance=args.source_instance,
                data_class=args.data_class,
                processor_request=_load_json(request_path),
                process=args.process,
                execution_profile=args.execution_profile,
                return_depth=args.return_depth,
                initiator_class=args.initiator_class,
                initiator_ref=args.initiator_ref,
                publisher_required=args.publisher_required,
            publisher_destination=(
                {"type": args.publisher_destination_type, **(
                    {"kv_class": args.publisher_kv_class, "kv_context_ref": args.publisher_kv_context_ref}
                    if args.publisher_destination_type == "KV" else {"session_ref": args.publisher_session_ref}
                )} if args.publisher_destination_type else None
            ),
                external_review=args.external_review,
                publisher_package_profile=args.publisher_package_profile,
                egress_surface=args.egress_surface,
                destination_profile=args.destination_profile,
                governance_reference_graph=(
                    _load_json(args.governance_reference_graph)
                    if args.governance_reference_graph
                    else None
                ),
                created_at=args.created_at,
            )
            if args.attempt_id and manifest.get("manifest_profile") is not None:
                evidence, verifier = load_readiness_inputs(args.readiness_evidence, args.readiness_keys)
                manifest = qualify_draft_manifest(
                    manifest, attempt_id=args.attempt_id, readiness_evidence=evidence, evidence_verifier=verifier,
                )
            _write_json(manifest, args.output)
            return 0
        except ValueError as exc:
            parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
