"""Resolve what an installed route's transport surface requires of an ingress.

A manifest declares its route. A published route declares its routing surface.
This module declares what that surface requires of a transport ingress, so a
non-ALLOW transport disposition names the next transition instead of an
unlabeled blocker.

The requirement is a state transition, not a machine. The ingress instance is
materialized by advancing the manifest-bound invocation through registered node
binding, Interlock and InTr admission, in the canonical substrate review order.
Nothing waits on an external host, a standing runtime, a hosted carrier or a
device, and no such thing is a predicate here: every machine-dependency claim
below is false, per
`data/task-registry-global-invariants.json` in StegVerse-org/.github, whose
prohibitions include NO_REMOTE_COMPUTER_AS_SECOND_MACHINE_REQUIREMENT and
NO_EVIDENCE_REACHABILITY_GAP_AS_EXTERNAL_DEVICE_REQUIREMENT.

Two authorities stay untouched: the surface is route authority (TVC), fixed by
the published route table, and the relay credential is TV/TVC. Neither is the
SDK's to supply, and resolving a profile grants nothing.

A manifest may not name its own endpoint. Endpoint, route and receiver
discovery are all disallowed, and a submitter-named endpoint would move route
authority from TVC to the submitter. The endpoint arrives with the admission,
which is why it is not a build-time field.

An absent instance reference is an unperformed admission, never a blocker:
`EVIDENCE_REACHABILITY` may remain pending and cannot establish that a
substrate is unsuitable or that anything external is required.
"""
from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urlsplit

SCHEMA = "stegverse.sdk.transport-ingress-profile/v1"
INVARIANT = (
    "ROUTE_DECLARES_SURFACE__SURFACE_DECLARES_REQUIREMENT__"
    "ADMITTED_INVOCATION_MATERIALIZES_INSTANCE"
)

INGRESS_URL_ENV = "STEGVERSE_UNIVERSAL_INTR_INGRESS_URL"
TRANSPORT_AUTHORIZATION_ENV = "STEGVERSE_TVC_RELAY_AUTHORIZATION_ID"

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
MATERIALIZATION_PATH = "/intr/materialization"

# Canonical order from stegverse.execution-substrate-resolution/v1. Single-device
# first; the external last resort is never a requirement and never a predicate.
SUBSTRATE_REVIEW_ORDER = (
    "STEG-BROWSER-RETAINED-RESIDENT-NODE",
    "STEGOS-CURRENT-DEVICE-NODE",
    "STEG-BROWSER-EPHEMERAL-LEASE",
    "SAME-DEVICE-SITE-SAFARI-SERVICE-WORKER",
    "ADMITTED-EPHEMERAL-STEGOS-NODE",
    "REMOTE-OR-EXTERNAL-DEVICE-LAST-RESORT",
)

SURFACE_UNKNOWN = "ROUTING_SURFACE_HAS_NO_PUBLISHED_INGRESS_PROFILE"
PROFILE_MATCHED = "INGRESS_INSTANCE_MATCHES_SURFACE_PROFILE"
PROFILE_MISMATCH = "UNIVERSAL_INTR_INGRESS_PROFILE_MISMATCH"
MISMATCH_SCHEME = "INGRESS_SCHEME_NOT_PERMITTED_BY_SURFACE"
MISMATCH_NON_LOOPBACK_PLAINTEXT = "NON_LOOPBACK_INGRESS_REQUIRES_TLS"
MISMATCH_PATH = "INGRESS_PATH_IS_NOT_THE_SURFACE_MATERIALIZATION_PATH"
MISMATCH_UNPARSEABLE = "INGRESS_URL_NOT_PARSEABLE"

# Every machine-dependency claim is false. These mirror the canonical task
# record's runtime_requirements rather than restating them loosely.
_NO_MACHINE_DEPENDENCY = {
    "standing_runtime_required": False,
    "external_runtime_connection_required": False,
    "generic_process_host_required": False,
    "hosted_carrier_required": False,
    "external_device_required": False,
    "second_user_operated_device_allowed": False,
    "route_discovery_allowed": False,
    "endpoint_discovery_allowed": False,
    "receiver_discovery_allowed": False,
}

# The one transport requirement shared by every surface whose published route
# binds the universal manifest state-transition runtime. The lane differs per
# surface; the transport does not.
_UNIVERSAL_INTR = {
    "transport_required": True,
    "transport": "INTERLOCK_INTR",
    "transport_origin": "TVC_RELAY_EGRESS",
    "credential_authority": "TV/TVC",
    "transition_authority": "INTERLOCK_INTR",
    "instance_source": "MANIFEST_BOUND_INVOCATION_ADMISSION",
    "substrate_review_order": SUBSTRATE_REVIEW_ORDER,
    "selected_substrate_requires_intr_admission": True,
    "registered_node_binding_required": True,
    "node_interlock_binding_required_before_lease": True,
    "pending_admission_transition": (
        "REGISTERED_NODE_BINDING -> INTERLOCK -> INTR_ADMISSION -> "
        "BOUNDED_LEASE -> EVENT_EPHEMERAL_STEGOS_RUNTIME"),
    "instance_reference_bindings": (INGRESS_URL_ENV, TRANSPORT_AUTHORIZATION_ENV),
    "instance_reference_semantics": "EVIDENCE_REACHABILITY_ONLY",
    "instance_reference_absence_blocks_task_progression": False,
    "instance_reference_absence_establishes_substrate_unsuitable": False,
    "schemes_permitted": ("http", "https"),
    "plaintext_hosts_permitted": tuple(sorted(LOOPBACK_HOSTS)),
    "path_required": MATERIALIZATION_PATH,
    "manifest_declarable_endpoint": False,
    "manifest_declarable_endpoint_reason": (
        "ENDPOINT_IS_MATERIALIZED_BY_ADMISSION_NOT_DECLARED_AT_BUILD_TIME"),
    **_NO_MACHINE_DEPENDENCY,
}

_LOCAL_ONLY = {
    "transport_required": False,
    "transport": None,
    "credential_authority": "TV/TVC",
    "instance_source": "NONE_REQUIRED",
    "instance_reference_bindings": (),
    "manifest_declarable_endpoint": False,
    "manifest_declarable_endpoint_reason": "SURFACE_REQUIRES_NO_TRANSPORT_ENDPOINT",
    **_NO_MACHINE_DEPENDENCY,
}

SURFACE_PROFILES: dict[str, dict[str, Any]] = {
    "EXISTING_UNIVERSAL_INTR": {
        **_UNIVERSAL_INTR,
        "lane_note": "Existing governed StegVerse runtime owner executes the lifecycle.",
    },
    "CANONICAL_PRODUCTION": {
        **_UNIVERSAL_INTR,
        "lane_note": "Canonical production validation; external consequence is enabled.",
    },
    "ECOSYSTEM_DIAGNOSTIC": {
        **_UNIVERSAL_INTR,
        "lane_note": "Diagnostic observation only; still transported by existing InTr.",
    },
    "SDK_LOCAL_SEMANTIC_DEMONSTRATION": {
        **_UNIVERSAL_INTR,
        "lane_note": (
            "Demonstration lane. Local derivation needs no transport and is reachable "
            "through external-run --prepare-only; governed closure of the demonstration "
            "is admitted on the same manifest-bound path."),
    },
    "SDK_INSTALLED_SOURCE_PACKAGE": {
        **_LOCAL_ONLY,
        "lane_note": "Computed entirely inside the installed SDK source package.",
    },
    "CUSTOMER_LOCAL": {
        **_LOCAL_ONLY,
        "lane_note": "Executed on the customer host under customer-supplied authority evidence.",
    },
}

AUTHORITY_BOUNDARY = {
    "profile_grants_authority": False,
    "profile_supplies_endpoint": False,
    "profile_supplies_credential": False,
    "profile_selects_substrate": False,
    "sdk_discovers_endpoint": False,
    "sdk_starts_listener": False,
    "sdk_admits_invocation": False,
    "manifest_declares_endpoint": False,
    "resolution_implies_reachability": False,
    "resolution_implies_admission": False,
}


def resolve_ingress_profile(routing_surface: Any) -> dict[str, Any]:
    """Return the published ingress requirement for a routing surface.

    An unrecognized surface is reported as unresolved. It is never defaulted to
    a transport profile, because defaulting would assert a transport the route
    authority never published.
    """
    surface = routing_surface if isinstance(routing_surface, str) else ""
    profile = SURFACE_PROFILES.get(surface)
    if profile is None:
        return {
            "schema": SCHEMA,
            "invariant": INVARIANT,
            "routing_surface": surface or None,
            "resolved": False,
            "failed_predicate": SURFACE_UNKNOWN,
            "required_evidence_or_repair": (
                "Publish an ingress profile for this routing surface in "
                "stegverse.transport_ingress_profile.SURFACE_PROFILES, or declare a "
                "route whose surface already has one."),
            "authority_boundary": dict(AUTHORITY_BOUNDARY),
        }
    resolved = {
        "schema": SCHEMA,
        "invariant": INVARIANT,
        "routing_surface": surface,
        "resolved": True,
        "authority_boundary": dict(AUTHORITY_BOUNDARY),
    }
    for key, value in profile.items():
        resolved[key] = list(value) if isinstance(value, tuple) else value
    return resolved


def ingress_repair_instruction(profile: Mapping[str, Any], failure: str) -> str:
    """State the next transition for a transport failure, never a machine to await."""
    if not profile.get("resolved"):
        return str(profile.get("required_evidence_or_repair") or SURFACE_UNKNOWN)
    if not profile.get("transport_required"):
        return (
            "This routing surface requires no transport ingress; the failure indicates "
            "the route was dispatched through the universal transport runtime in error.")
    if failure == "TV_TVC_RELAY_AUTHORIZATION_REQUIRED":
        return (
            f"Supply the existing authorized TV/TVC relay credential in "
            f"{TRANSPORT_AUTHORIZATION_ENV} for this invocation. TV/TVC issues it; the "
            f"SDK neither mints nor discovers it.")
    if failure == PROFILE_MISMATCH:
        return (
            f"The admitted instance reference does not match the surface: path must be "
            f"{profile['path_required']}, plaintext permitted only on "
            f"{', '.join(profile['plaintext_hosts_permitted'])}, TLS required otherwise. "
            f"Rebind it to the instance the admission materialized; do not substitute a "
            f"discovered endpoint.")
    # The denials stay in the profile's structured fields, where a machine reads
    # them. Naming a machine here even to deny it invites it back as a predicate.
    return (
        f"Advance the manifest-bound invocation through its admission transition "
        f"({profile['pending_admission_transition']}), which materializes the ingress "
        f"instance and its {profile['path_required']} reference. Resolve the substrate "
        f"in the canonical order, single-device first. The absent reference is an "
        f"unperformed admission, not a blocker.")


def validate_ingress_instance(profile: Mapping[str, Any], ingress_url: Any) -> dict[str, Any]:
    """Recognize an instance reference that an admission materialized.

    This recognizes or rejects a reference already bound for this invocation. It
    never discovers an endpoint, substitutes a different one, or treats an
    unrecognized reference as evidence about a substrate.
    """
    outcome: dict[str, Any] = {
        "schema": SCHEMA,
        "routing_surface": profile.get("routing_surface"),
        "checked_endpoint_path": None,
        "authority_boundary": dict(AUTHORITY_BOUNDARY),
    }
    if not profile.get("resolved") or not profile.get("transport_required"):
        outcome.update(matched=False, failed_predicate=SURFACE_UNKNOWN)
        return outcome
    try:
        parts = urlsplit(str(ingress_url or "").strip())
        scheme = (parts.scheme or "").lower()
        host = (parts.hostname or "").lower()
        path = parts.path or ""
    except ValueError:
        outcome.update(matched=False, failed_predicate=PROFILE_MISMATCH,
                       mismatch_reason=MISMATCH_UNPARSEABLE)
        return outcome
    outcome["checked_endpoint_path"] = path
    if scheme not in set(profile["schemes_permitted"]):
        outcome.update(matched=False, failed_predicate=PROFILE_MISMATCH,
                       mismatch_reason=MISMATCH_SCHEME)
        return outcome
    if scheme == "http" and host not in set(profile["plaintext_hosts_permitted"]):
        outcome.update(matched=False, failed_predicate=PROFILE_MISMATCH,
                       mismatch_reason=MISMATCH_NON_LOOPBACK_PLAINTEXT)
        return outcome
    if path != profile["path_required"]:
        outcome.update(matched=False, failed_predicate=PROFILE_MISMATCH,
                       mismatch_reason=MISMATCH_PATH)
        return outcome
    outcome.update(matched=True, state=PROFILE_MATCHED)
    return outcome
