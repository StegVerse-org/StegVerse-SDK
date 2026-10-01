"""Resolve what an installed route's transport surface requires of an ingress.

A manifest declares its route. A published route declares its routing surface.
This module declares what that surface requires of a transport ingress, so a
non-ALLOW transport disposition names a repair that exists instead of an
unlabeled blocker.

It resolves requirements only. It never discovers an endpoint, starts a
listener, issues a credential, or accepts an endpoint named by a manifest.
Three separate authorities remain untouched:

- the surface is route authority (TVC), fixed by the published route table;
- the endpoint instance is a resident-local binding, supplied by the host;
- the relay credential is TV/TVC, supplied per invocation.

None of the three is the SDK's to supply, and resolving a profile grants
nothing. A manifest may not name its own endpoint: the Universal InTr ingress
is a loopback listener on an OS-assigned port, so an endpoint fixed at manifest
build time is not stable to the next host start, and a submitter-named endpoint
would move route authority from TVC to the submitter.
"""
from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urlsplit

SCHEMA = "stegverse.sdk.transport-ingress-profile/v1"
INVARIANT = (
    "ROUTE_DECLARES_SURFACE__SURFACE_DECLARES_REQUIREMENT__"
    "RESIDENT_BINDING_SUPPLIES_INSTANCE"
)

INGRESS_URL_ENV = "STEGVERSE_UNIVERSAL_INTR_INGRESS_URL"
TRANSPORT_AUTHORIZATION_ENV = "STEGVERSE_TVC_RELAY_AUTHORIZATION_ID"

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
MATERIALIZATION_PATH = "/intr/materialization"

SURFACE_UNKNOWN = "ROUTING_SURFACE_HAS_NO_PUBLISHED_INGRESS_PROFILE"
PROFILE_MATCHED = "INGRESS_INSTANCE_MATCHES_SURFACE_PROFILE"
PROFILE_MISMATCH = "UNIVERSAL_INTR_INGRESS_PROFILE_MISMATCH"
MISMATCH_SCHEME = "INGRESS_SCHEME_NOT_PERMITTED_BY_SURFACE"
MISMATCH_NON_LOOPBACK_PLAINTEXT = "NON_LOOPBACK_INGRESS_REQUIRES_TLS"
MISMATCH_PATH = "INGRESS_PATH_IS_NOT_THE_SURFACE_MATERIALIZATION_PATH"
MISMATCH_UNPARSEABLE = "INGRESS_URL_NOT_PARSEABLE"

# The one transport requirement shared by every surface whose published route
# binds the universal manifest state-transition runtime. The lane differs per
# surface; the transport does not, because all of them post through the same
# existing Universal InTr materialization ingress.
_UNIVERSAL_INTR = {
    "transport_required": True,
    "transport": "INTERLOCK_INTR",
    "transport_origin": "TVC_RELAY_EGRESS",
    "credential_authority": "TV/TVC",
    "instance_source": "RESIDENT_LOCAL_BINDING",
    "instance_bindings": (INGRESS_URL_ENV, TRANSPORT_AUTHORIZATION_ENV),
    "schemes_permitted": ("http", "https"),
    "plaintext_hosts_permitted": tuple(sorted(LOOPBACK_HOSTS)),
    "path_required": MATERIALIZATION_PATH,
    "listener_entrypoint": "scripts/serve_hil_intr_materialization_ingress.py",
    "listener_owner": "RESIDENT_SOVEREIGN_HOST",
    "listener_repository": "StegVerse-org/.github",
    "reachable_from_hosted_ci": False,
    "manifest_declarable_endpoint": False,
    "manifest_declarable_endpoint_reason": (
        "RESIDENT_LOOPBACK_OS_ASSIGNED_PORT_NOT_STABLE_AT_MANIFEST_BUILD_TIME"),
}

_LOCAL_ONLY = {
    "transport_required": False,
    "transport": None,
    "credential_authority": "TV/TVC",
    "instance_source": "NONE_REQUIRED",
    "instance_bindings": (),
    "reachable_from_hosted_ci": True,
    "manifest_declarable_endpoint": False,
    "manifest_declarable_endpoint_reason": "SURFACE_REQUIRES_NO_TRANSPORT_ENDPOINT",
}

SURFACE_PROFILES: dict[str, dict[str, Any]] = {
    "EXISTING_UNIVERSAL_INTR": {
        **_UNIVERSAL_INTR,
        "lane_note": "Existing governed StegVerse runtime owner executes the lifecycle.",
        "prepare_only_available": True,
    },
    "CANONICAL_PRODUCTION": {
        **_UNIVERSAL_INTR,
        "lane_note": "Canonical production validation; external consequence is enabled.",
        "prepare_only_available": True,
    },
    "ECOSYSTEM_DIAGNOSTIC": {
        **_UNIVERSAL_INTR,
        "lane_note": "Diagnostic observation only; still transported by existing InTr.",
        "prepare_only_available": True,
    },
    "SDK_LOCAL_SEMANTIC_DEMONSTRATION": {
        **_UNIVERSAL_INTR,
        "lane_note": (
            "Demonstration lane. Local derivation needs no transport and is reachable "
            "through external-run --prepare-only; governed closure of the demonstration "
            "still requires the resident ingress."),
        "prepare_only_available": True,
    },
    "SDK_INSTALLED_SOURCE_PACKAGE": {
        **_LOCAL_ONLY,
        "lane_note": "Computed entirely inside the installed SDK source package.",
        "prepare_only_available": True,
    },
    "CUSTOMER_LOCAL": {
        **_LOCAL_ONLY,
        "lane_note": "Executed on the customer host under customer-supplied authority evidence.",
        "prepare_only_available": True,
    },
}

AUTHORITY_BOUNDARY = {
    "profile_grants_authority": False,
    "profile_supplies_endpoint": False,
    "profile_supplies_credential": False,
    "sdk_discovers_endpoint": False,
    "sdk_starts_listener": False,
    "manifest_declares_endpoint": False,
    "resolution_implies_reachability": False,
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
    """State the repair for a transport failure in terms the profile establishes."""
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
            f"Rebind {INGRESS_URL_ENV} to the surface's materialization endpoint: "
            f"path {profile['path_required']}, plaintext permitted only on "
            f"{', '.join(profile['plaintext_hosts_permitted'])}, TLS required otherwise.")
    return (
        f"Bind {INGRESS_URL_ENV} to the existing resident Universal InTr ingress "
        f"({profile['path_required']} on "
        f"{', '.join(profile['plaintext_hosts_permitted'])}), served by "
        f"{profile['listener_entrypoint']} in {profile['listener_repository']} on the "
        f"resident host, and supply {TRANSPORT_AUTHORIZATION_ENV}. The ingress is "
        f"loopback-scoped and is not reachable from hosted CI; the SDK cannot discover "
        f"or start it.")


def validate_ingress_instance(profile: Mapping[str, Any], ingress_url: Any) -> dict[str, Any]:
    """Check a resident-supplied endpoint against its surface profile.

    This recognizes or rejects the binding the host supplied. It never rewrites
    the endpoint and never substitutes a different one.
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
