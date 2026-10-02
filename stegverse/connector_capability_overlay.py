"""Join installed SDK capability to the canonical Universal InTr connector registry.

``capability_map`` reconciles three maps that describe SDK capability from the
inside: the installed route table, the builder bindings, and the evaluator
examples. There is a fourth, and it is the authoritative one.

The canonical registry is the capability overlay on the organization set. Every
organization carries a ``.github``, which is its coordination surface and its
ingress/egress boundary; a capability is declared against the organization that
owns it, addressed as ``<org>/.github`` (optionally with a coordination locus)
or as an owning repository inside that organization. A profile names the
``{boundary, subsystem}`` pair it departs from and the pair it arrives at, and
the boundary axis is ordered, so the hops between them are a slice of that axis
rather than a route anyone chooses.

An installed route the builder cannot reach is not evaluator-invocable. A
registered capability the SDK does not bind is not invocable either, and an SDK
subsystem that appears in the registry without being declared here is a change
to the SDK's own surface that must be read, not absorbed.

The registry is passed in. The SDK does not own it, does not vendor it, and
cannot regenerate it: it belongs to ``StegVerse-Labs/StegOS`` and the orgs whose
capabilities it declares. This module reconciles against whatever registry it is
handed and reports what disagrees.

Non-authorizing. Source reconciliation only: it installs nothing, binds
nothing, admits nothing, selects no destination and observes no runtime.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

SCHEMA = "stegverse.sdk.connector-capability-overlay/v1"
REGISTRY_SCHEMA = "stegverse.universal-intr.connector-profile-registry/v1"
PROFILE_SCHEMA = "stegverse.universal-intr.connector-profile/v1"

#: The canonical registry's identity. The SDK reads it; it never writes it.
CANONICAL_REGISTRY = {
    "repository": "StegVerse-Labs/StegOS",
    "path": "specs/universal-intr-connector-profiles.v1.json",
    "generator": "StegVerse-Labs/StegOS/tools/generate_intr_connector.py",
    "observed_commit": "adceffaa6fcdf0e89bff7a091dddf92d790cc439",
    "sdk_may_write_registry": False,
    "sdk_may_regenerate_projection": False,
}

#: Ordered boundary axis. The hop sequence between two boundaries is the slice
#: of this tuple between them, reversed when the destination precedes the
#: source. Provenance: the generated connector's own BOUNDARIES constant. An
#: unrecognized boundary fails closed rather than being appended.
BOUNDARY_AXIS = (
    "SKAP_VAULT",
    "KV",
    "DEVICE_SYSTEM",
    "STEGOS_ECOSYSTEM",
    "EXTERNAL_SYSTEM",
)

SDK_SUBSYSTEM_PREFIX = "SDK:"

#: The SDK subsystems declared in the canonical registry, and the payload schema
#: each one carries. A subsystem reaching the registry outside this baseline is
#: reported, never absorbed: the SDK's own ingress/egress surface may only grow
#: by a reviewed edit here.
SDK_SUBSYSTEM_BASELINE: Mapping[str, Mapping[str, str]] = {
    "SDK:ManifestIngress": {
        "profile_id": "sdk-manifest-ingress",
        "legs": ("destination", "response.source"),
        "payload_schema": "stegverse.ingress-manifest.v1",
        "binding_module": "stegverse.manifest_contract",
        "profile_canonical_sha256": (
            "sha256:6211212f1f0fe699826fac9436ada0744d8dbebd7949115cadd5794d1ea74971"),
        "digest_provenance": "OBSERVED_AT_CANONICAL_REGISTRY_COMMIT_NOT_UPSTREAM_PROJECTED",
    },
    "SDK:EvaluatorReviewIngress": {
        "profile_id": "evaluator-read-review",
        "legs": ("destination", "response.source"),
        "payload_schema": "stegverse.evaluator_review.interlock_request.v1",
        "binding_module": "stegverse.evaluator_review_intr",
        "profile_canonical_sha256": (
            "sha256:07e22ab23438d9a3d5559c69fa76cdb098b8d81f2e7a14aa72064d0198e8c390"),
        "digest_provenance": "UPSTREAM_PINNED_IN_GENERATED_CONNECTOR",
    },
    "SDK:ReviewerEvidenceExport": {
        "profile_id": "sdk-publisher-review",
        "legs": ("source",),
        "payload_schema": "stegverse.publisher.artifact-transfer/v1",
        "binding_module": "stegverse.review_publisher_transfer",
        "profile_canonical_sha256": (
            "sha256:07631247368a6960de1ba3cd278407e97908fdf23089d73c2240030200792ffc"),
        "digest_provenance": "OBSERVED_AT_CANONICAL_REGISTRY_COMMIT_NOT_UPSTREAM_PROJECTED",
    },
    # The return leg is an SDK ingress point in its own right. It carries the
    # return schema rather than the profile's request schema, which is why a
    # subsystem declares the schema it binds instead of inheriting the
    # profile's.
    "SDK:ReviewerReturn": {
        "profile_id": "sdk-publisher-review",
        "legs": ("response.destination",),
        "payload_schema": "stegverse.publisher.artifact-return/v1",
        "binding_module": "stegverse.publisher_return_binding",
        "profile_canonical_sha256": (
            "sha256:07631247368a6960de1ba3cd278407e97908fdf23089d73c2240030200792ffc"),
        "digest_provenance": "OBSERVED_AT_CANONICAL_REGISTRY_COMMIT_NOT_UPSTREAM_PROJECTED",
    },
}

#: Every leg of a profile that names an endpoint. A capability's ingress and
#: egress points are both mapped destinations, so the return legs are scanned
#: exactly like the request legs; scanning only the request legs hides the
#: subsystem the SDK receives its return on.
PROFILE_LEGS = ("source", "destination", "response.source", "response.destination")

OVERLAY_BOUND = "REGISTERED_CAPABILITY_BOUND_IN_SDK"
REGISTERED_NOT_BOUND = "REGISTERED_CAPABILITY_NOT_BOUND_IN_SDK"
UNDECLARED_SDK_SUBSYSTEM = "UNDECLARED_SDK_SUBSYSTEM_IN_CANONICAL_REGISTRY"
DECLARED_SUBSYSTEM_ABSENT = "DECLARED_SDK_SUBSYSTEM_ABSENT_FROM_REGISTRY"
PROFILE_CONTENT_CHANGED = "REGISTERED_PROFILE_CONTENT_CHANGED_SINCE_BASELINE"
UNKNOWN_BOUNDARY = "PROFILE_NAMES_A_BOUNDARY_OUTSIDE_THE_ORDERED_AXIS"
LEG_SET_CHANGED = "REGISTERED_SUBSYSTEM_APPEARS_ON_DIFFERENT_LEGS_THAN_DECLARED"
OVERLAY_RECONCILED = "CONNECTOR_CAPABILITY_OVERLAY_RECONCILED"
STOP_OVERLAY_DRIFT = "STOP_CONNECTOR_CAPABILITY_OVERLAY_DRIFT"

OWNING_GOAL = "SDK-GENERIC-MANIFEST-ECOSYSTEM-INVARIANT-005"
RETRY_ENTRYPOINT = "stegverse.connector_capability_overlay.reconcile_overlay"

AUTHORITY_BOUNDARY = {
    "overlay_grants_authority": False,
    "overlay_selects_destination": False,
    "overlay_admits_invocation": False,
    "overlay_supplies_credential": False,
    "sdk_may_write_canonical_registry": False,
    "sdk_may_declare_its_own_capability": False,
    "reconciliation_implies_reachability": False,
    "reconciliation_implies_runtime_observation": False,
}


def _canonical(value: Any) -> Any:
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _canonical(value[key]) for key in sorted(value)}
    return value


def canonical_sha256(value: Any) -> str:
    """Digest a profile the way the canonical generator does: sorted keys, no spaces."""
    raw = json.dumps(_canonical(value), separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def boundary_path(source_boundary: Any, destination_boundary: Any) -> list[str]:
    """The ordered hops between two boundaries, as a slice of the axis.

    Raises on a boundary outside the axis. Extending the axis is a registry
    change, never an inference made here.
    """
    try:
        start = BOUNDARY_AXIS.index(str(source_boundary))
        end = BOUNDARY_AXIS.index(str(destination_boundary))
    except ValueError as exc:
        raise ValueError(UNKNOWN_BOUNDARY) from exc
    if start <= end:
        return list(BOUNDARY_AXIS[start:end + 1])
    return list(reversed(BOUNDARY_AXIS[end:start + 1]))


def _profiles(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    declared = registry.get("profiles")
    if isinstance(declared, list):
        return [dict(item) for item in declared if isinstance(item, Mapping)]
    if isinstance(declared, Mapping):
        return [dict(value, profile_id=key) for key, value in declared.items()
                if isinstance(value, Mapping)]
    raise ValueError("registry profiles must be a list or an object")


def _owner_organization(owner_ref: Any) -> str | None:
    """The organization an owner reference belongs to.

    A capability is owned by an organization, whether the reference names that
    organization's ``.github`` or a repository inside it.
    """
    text = str(owner_ref or "").strip()
    if not text or "/" not in text:
        return None
    return text.split("/", 1)[0]


def _endpoints(profile: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Every (subsystem, leg) this profile names, request and return alike."""
    found: list[tuple[str, str]] = []
    response = profile.get("response")
    for leg in PROFILE_LEGS:
        holder: Any = profile
        if leg.startswith("response."):
            holder = response
        key = leg.split(".")[-1]
        obj = holder.get(key) if isinstance(holder, Mapping) else None
        if isinstance(obj, Mapping):
            subsystem = obj.get("subsystem")
            if isinstance(subsystem, str) and subsystem:
                found.append((subsystem, leg))
    return found


def overlay_rows(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize the registry into the capability-over-organization overlay."""
    rows: list[dict[str, Any]] = []
    for profile in _profiles(registry):
        source = profile.get("source") or {}
        destination = profile.get("destination") or {}
        owner_ref = profile.get("downstream_owner_ref")
        row: dict[str, Any] = {
            "profile_id": profile.get("profile_id"),
            "request_class": profile.get("request_class"),
            "payload_schema": profile.get("payload_schema"),
            "operations": list(profile.get("operations") or ()),
            "source_boundary": source.get("boundary") if isinstance(source, Mapping) else None,
            "source_subsystem": source.get("subsystem") if isinstance(source, Mapping) else None,
            "destination_boundary": (
                destination.get("boundary") if isinstance(destination, Mapping) else None),
            "destination_subsystem": (
                destination.get("subsystem") if isinstance(destination, Mapping) else None),
            "owner_ref": owner_ref,
            "owner_organization": _owner_organization(owner_ref),
            "profile_canonical_sha256": canonical_sha256(profile),
        }
        try:
            row["boundary_path"] = boundary_path(
                row["source_boundary"], row["destination_boundary"])
            row["boundary_axis_recognized"] = True
        except ValueError:
            row["boundary_path"] = None
            row["boundary_axis_recognized"] = False
            row["failed_predicate"] = UNKNOWN_BOUNDARY
        row["endpoints"] = _endpoints(profile)
        row["sdk_subsystems"] = sorted({
            subsystem for subsystem, _ in row["endpoints"]
            if subsystem.startswith(SDK_SUBSYSTEM_PREFIX)})
        rows.append(row)
    rows.sort(key=lambda item: str(item["profile_id"]))
    return rows


def _unbound(subsystem: str, declared: Mapping[str, str], reason: str) -> dict[str, Any]:
    return {
        "subsystem": subsystem,
        "state": reason,
        "disposition": "FAIL_CLOSED",
        "failed_predicate": reason,
        "required_evidence_or_repair": (
            f"bind {declared.get('payload_schema')} in {declared.get('binding_module')} "
            f"and declare the binding in SDK_SUBSYSTEM_BASELINE"
            if reason == REGISTERED_NOT_BOUND else
            f"reconcile SDK_SUBSYSTEM_BASELINE against the canonical registry at "
            f"{CANONICAL_REGISTRY['repository']}:{CANONICAL_REGISTRY['path']}"),
        "retry_entrypoint": RETRY_ENTRYPOINT,
        "owning_existing_goal": OWNING_GOAL,
        "registry_repository": CANONICAL_REGISTRY["repository"],
    }


def reconcile_overlay(
    registry: Mapping[str, Any],
    *,
    bound_payload_schemas: Iterable[str],
    projected_profile_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Reconcile the SDK's declared surface against the canonical registry.

    ``bound_payload_schemas`` is what the installed SDK actually binds, supplied
    by the caller rather than discovered here. ``projected_profile_ids``, when
    given, is the set a downstream projection carries; profiles absent from it
    are reported as unprojected so a stale projection is visible rather than
    found by hand.
    """
    rows = overlay_rows(registry)
    bound = {str(schema) for schema in bound_payload_schemas}
    registry_sdk: dict[str, dict[str, Any]] = {}
    for row in rows:
        for subsystem in row["sdk_subsystems"]:
            registry_sdk[subsystem] = row

    capabilities: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for subsystem, declared in sorted(SDK_SUBSYSTEM_BASELINE.items()):
        row = registry_sdk.get(subsystem)
        if row is None:
            failures.append(_unbound(subsystem, declared, DECLARED_SUBSYSTEM_ABSENT))
            continue
        observed_legs = sorted(leg for name, leg in row["endpoints"] if name == subsystem)
        entry: dict[str, Any] = {
            "subsystem": subsystem,
            "profile_id": row["profile_id"],
            "declared_legs": list(declared["legs"]),
            "observed_legs": observed_legs,
            "payload_schema": declared["payload_schema"],
            "profile_payload_schema": row["payload_schema"],
            "binding_module": declared["binding_module"],
            "owner_ref": row["owner_ref"],
            "owner_organization": row["owner_organization"],
            "boundary_path": row["boundary_path"],
            "digest_provenance": declared["digest_provenance"],
        }
        if row["profile_canonical_sha256"] != declared["profile_canonical_sha256"]:
            entry["state"] = PROFILE_CONTENT_CHANGED
            entry["disposition"] = "FAIL_CLOSED"
            entry["failed_predicate"] = PROFILE_CONTENT_CHANGED
            entry["baseline_profile_canonical_sha256"] = declared["profile_canonical_sha256"]
            entry["observed_profile_canonical_sha256"] = row["profile_canonical_sha256"]
            entry["required_evidence_or_repair"] = (
                "read the changed profile at the canonical registry and update "
                "SDK_SUBSYSTEM_BASELINE deliberately; never auto-adopt a new digest")
            entry["retry_entrypoint"] = RETRY_ENTRYPOINT
            entry["owning_existing_goal"] = OWNING_GOAL
            failures.append(entry)
        elif sorted(declared["legs"]) != observed_legs:
            entry["state"] = LEG_SET_CHANGED
            entry["disposition"] = "FAIL_CLOSED"
            entry["failed_predicate"] = LEG_SET_CHANGED
            entry["required_evidence_or_repair"] = (
                "the registry moved this subsystem to a different leg; read the "
                "profile and update its declared legs deliberately")
            entry["retry_entrypoint"] = RETRY_ENTRYPOINT
            entry["owning_existing_goal"] = OWNING_GOAL
            failures.append(entry)
        elif str(declared["payload_schema"]) in bound:
            entry["state"] = OVERLAY_BOUND
            entry["disposition"] = "ALLOW"
        else:
            entry.update(_unbound(subsystem, declared, REGISTERED_NOT_BOUND))
            failures.append(entry)
        capabilities.append(entry)

    undeclared = sorted(set(registry_sdk) - set(SDK_SUBSYSTEM_BASELINE))
    for subsystem in undeclared:
        failures.append({
            "subsystem": subsystem,
            "profile_id": registry_sdk[subsystem]["profile_id"],
            "state": UNDECLARED_SDK_SUBSYSTEM,
            "disposition": "FAIL_CLOSED",
            "failed_predicate": UNDECLARED_SDK_SUBSYSTEM,
            "required_evidence_or_repair": (
                "read the new SDK subsystem at the canonical registry, bind its "
                "payload schema, and declare it in SDK_SUBSYSTEM_BASELINE"),
            "retry_entrypoint": RETRY_ENTRYPOINT,
            "owning_existing_goal": OWNING_GOAL,
            "registry_repository": CANONICAL_REGISTRY["repository"],
        })

    unrecognized = [row["profile_id"] for row in rows if not row["boundary_axis_recognized"]]
    for profile_id in unrecognized:
        failures.append({
            "profile_id": profile_id,
            "state": UNKNOWN_BOUNDARY,
            "disposition": "FAIL_CLOSED",
            "failed_predicate": UNKNOWN_BOUNDARY,
            "required_evidence_or_repair": (
                "the registry names a boundary outside BOUNDARY_AXIS; extend the "
                "axis only from the canonical generator, never by inference"),
            "retry_entrypoint": RETRY_ENTRYPOINT,
            "owning_existing_goal": OWNING_GOAL,
        })

    organizations = sorted({row["owner_organization"] for row in rows
                            if row["owner_organization"]})
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "state": STOP_OVERLAY_DRIFT if failures else OVERLAY_RECONCILED,
        "disposition": "FAIL_CLOSED" if failures else "ALLOW",
        "canonical_registry": dict(CANONICAL_REGISTRY),
        "registry_schema_declared": registry.get("schema"),
        "registry_state_declared": registry.get("state"),
        "registry_profile_count": len(rows),
        "overlaid_organizations": organizations,
        "sdk_capabilities": capabilities,
        "undeclared_sdk_subsystems": undeclared,
        "failures": failures,
        "authority_boundary": dict(AUTHORITY_BOUNDARY),
        "authority_effect": "NONE_SOURCE_RECONCILIATION_ONLY",
    }
    if projected_profile_ids is not None:
        projected = {str(item) for item in projected_profile_ids}
        result["projection_coverage"] = {
            "projected_profile_count": len(projected),
            "registry_profile_count": len(rows),
            "unprojected_profile_ids": sorted(
                str(row["profile_id"]) for row in rows
                if str(row["profile_id"]) not in projected),
            "projection_is_current": len(projected) == len(rows),
            "projection_owner": CANONICAL_REGISTRY["generator"],
            "sdk_may_regenerate_projection": False,
        }
    return result
