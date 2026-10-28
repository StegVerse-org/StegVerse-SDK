"""SDK-hosted Universal InTr edge-route installer, wrapper and role re-adoption.

One component replaces the per-consumer ``scripts/install_*_universal_intr_route.py``
installers of StegVerse-Labs/.github (seven at Labs main ``bfcf0318``). Each of
those splices its own route into ``workers/universal_intr_profiled_ingress.py``
and refuses with a bare ``SystemExit("FAIL_CLOSED: ...")``. Under the
Organization Role standard (StegVerse-org/.github
``docs/ORGANIZATION_ROLE_RUNTIME_REALITY_DEPLOYMENT.md``, "ORRD") such a surface
is ``ORGANIZATION_ROLE_CONFORMANCE_NOT_DECLARED`` (L63) and must be updated
(L53). This module is that update, for the SDK half:

* ``evaluate_installation`` treats an installation as a manifest-bound attempted
  state transition (ORRD L57): an explicit predecessor (the router source
  digest), a proposed successor (the transformed source digest), the manifested
  capability and route (resolved only by ``stegverse.route_resolution``), the
  governing constraints, evidence, and an ALLOW / DENY / FAIL_CLOSED
  disposition. Every non-ALLOW carries the six fields (ORRD L61).
* ``admit_edge_submission`` is the wrapper the installed branch calls. It admits
  only a payload that carries an SDK ingress manifest whose declared route is
  the consumer's published route, and answers with a submission addressed to
  the organization's own ``sdk-manifest-ingress`` capability (read from the
  organization's ``org-runtime/interlock-intr.json``, never from the payload).
  It delivers nothing and waits on nothing (ORRD L59, L60); the organization
  receipt is appended by that organization's existing manifest ingress and is
  never claimed here.
* ``role_version_file_entry`` / ``role_version_contract_digest`` compute a
  target-role-version file entry and contract digest in exactly the form
  StegVerse-Labs/.github ``resident-runtime/organization_role_conformance.py``
  ``check_target_version`` recomputes (``canon`` with default ``ensure_ascii``,
  ``git_blob_sha``), so a role version that records a shared file can be
  evaluated by every organization unchanged.
* ``plan_readoption`` derives the re-adoption transition that follows a
  conformance DENY or FAIL_CLOSED from ``organization_role_conformance.evaluate``.

Nothing here starts a listener, binds a socket, writes source in place, appends
a ledger entry, reads or carries a credential, or reads a clock. Time is the
supplied ``hb_epoch`` only, checked by the shared ``supplied_epoch_failure``
(byte-identical to StegVerse-org/.github ``organization_egress_boundary.py``,
segment sha256 ``7f36f0e6...``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import (
    PUBLISHED_ROUTES,
    STEGBROWSER_ROUTE_ID,
    canonical_sha256,
    resolve_route_declaration,
    route_from_manifest,
)

INSTALLATION_REQUEST_SCHEMA = "stegverse.universal-intr-route-installation-request/v1"
INSTALLATION_RESULT_SCHEMA = "stegverse.universal-intr-route-installation/v1"
EDGE_SUBMISSION_RESULT_SCHEMA = "stegverse.universal-intr-edge-submission/v1"
READOPTION_RESULT_SCHEMA = "stegverse.organization-role-readoption-plan/v1"
CONFORMANCE_RESULT_SCHEMA = "stegverse.organization-role-conformance-evaluation/v1"

OWNING_GOAL = "INTERLOCK-INTR-RUNTIME-INDEPENDENT-PROTOCOL-001"
ROLE_PROPAGATION_OWNER = "STEGDB-ORGANIZATION-ROLE-VERSION-PROPAGATION-002"
EXISTING_UNIVERSAL_INTR = "EXISTING_UNIVERSAL_INTR"
RECEIVER_UNAVAILABLE_DISPOSITION = "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION"
DEFAULT_ROUTER = "workers/universal_intr_profiled_ingress.py"
BOUNDARY_DOCUMENT = "org-runtime/interlock-intr.json"
MANIFEST_INGRESS_PROFILE_ID = "sdk-manifest-ingress"
MANIFEST_FIELD = "manifest"
EPOCH_PREDICATE = "SUBMISSION_CARRIES_THE_SUPPLIED_HB_EPOCH"
PARITY_PREDICATE = "REFERENCE_ADOPTION_PARITY_WITH_RECORDED_FILE_DIGESTS"

_MODULE = "stegverse/universal_intr_route_installer.py"
INSTALL_ENTRYPOINT = _MODULE + "::evaluate_installation"
SUBMISSION_ENTRYPOINT = _MODULE + "::admit_edge_submission"
READOPTION_ENTRYPOINT = _MODULE + "::plan_readoption"
CONFORMANCE_ENTRYPOINT = "resident-runtime/organization_manifest_ingress.py::receive"

#: The Labs installers this component replaces, as source facts at Labs main
#: bfcf031811caaa65bc44a48c894fce19800b5d90 (git blob ids). ``route_id`` is the
#: consumer's published SDK route, or None when ``PUBLISHED_ROUTES`` publishes
#: none for it. A route is never inferred or substituted (route_resolution L3-5).
EDGE_CONSUMERS: dict[str, dict[str, Any]] = {
    "canonical_work": {"profile": "CanonicalWork:Coordination", "route_id": None,
                       "installer": "scripts/install_canonical_work_universal_intr_route.py",
                       "installer_blob_sha": "0785706d9c56112ec56b895483f516a3377ba78c"},
    "erl_active_research": {"profile": "ERL:ActiveResearch", "route_id": None,
                            "installer": "scripts/install_erl_active_research_universal_intr_route.py",
                            "installer_blob_sha": "fd4c3f6fa5f3bbdcd29876d0fd9424b71c7af1d5"},
    "kv_ai_memory": {"profile": "KV:AI-MemoryPacketAdmission", "route_id": None,
                     "installer": "scripts/install_kv_ai_memory_universal_intr_route.py",
                     "installer_blob_sha": "01941281b16d3fe2f5a3291e1ed59ee484e55dcd"},
    "site_publication": {"profile": "StegOS:SitePublicationRuntime", "route_id": None,
                         "installer": "scripts/install_site_publication_universal_intr_route.py",
                         "installer_blob_sha": "12c8067c9c338ca4df4d194ae7752260dccd04cd"},
    "stegbrowser": {"profile": "StegBrowser:ManifestInvocation", "route_id": STEGBROWSER_ROUTE_ID,
                    "installer": "scripts/install_stegbrowser_universal_intr_route.py",
                    "installer_blob_sha": "c19b9a8d161eeadde5c985939a771912b558c915"},
    "stegsocials_bounded": {"profile": "StegSocials:BoundedSocialIngress", "route_id": None,
                            "installer": "scripts/install_stegsocials_bounded_universal_intr_route.py",
                            "installer_blob_sha": "58a6ca4913f8d0878a015d0a1f6fc501e2e4ec10"},
    "tvc_recipient_admission_sign": {"profile": "TVC:RecipientAdmissionAuthoritySign", "route_id": None,
                                     "installer": "scripts/install_tvc_recipient_admission_sign_universal_intr_route.py",
                                     "installer_blob_sha": "50a14a22d5ec57d622b34d12a25bbf14f6376899"},
}

#: The one import and the one branch this installer splices, for every consumer.
WRAPPER_IMPORT = ("from stegverse.universal_intr_route_installer import (  # noqa: E402\n"
                  "    admit_edge_submission as sdk_admit_edge_submission,\n"
                  "    is_edge_submission as sdk_is_edge_submission,\n"
                  ")\n")
_IMPORT_ANCHOR = "import serve_hil_intr_materialization_ingress as hil  # noqa: E402\n"
_DISPATCH_PREFIX = "receipt = "


def supplied_epoch_failure(hb_epoch: Any, reference: Any = None) -> tuple[str, str] | None:
    """The shared supplied-epoch rule (SUBMISSION_CARRIES_THE_SUPPLIED_HB_EPOCH).

    Byte-identical in StegVerse-org/.github#185 and StegVerse-Labs/.github#3212
    and #3213. `hb_epoch` absent (None) is HB_EPOCH_NOT_SUPPLIED. Otherwise it
    must be ASCII [0-9]+ only -- an int is read as its decimal text; a bool, a
    float or anything coerced ('+33', ' 33', '3_3', '33.0') is refused -- with
    integer value >= 32 (the HB32 anchor). `reference`, the carrier frame's
    heartbeat reference when there is one, must be an object, and a
    `derived_from_clock` it carries must be exactly false. Any failure is
    HB_EPOCH_INVALID. Returns (failure_code, detail), or None when the epoch is
    supplied. No clock is read.
    """
    if reference is not None and not isinstance(reference, dict):
        return "HB_EPOCH_INVALID", "the carrier's heartbeat reference is not an object"
    if hb_epoch is None:
        return "HB_EPOCH_NOT_SUPPLIED", "no hb_epoch was supplied and no clock is read"
    if isinstance(hb_epoch, bool):
        text = None
    elif isinstance(hb_epoch, int):
        text = str(hb_epoch)
    elif isinstance(hb_epoch, str):
        text = hb_epoch
    else:
        text = None
    if text is None or not text.isascii() or not text.isdigit():
        return "HB_EPOCH_INVALID", "hb_epoch " + repr(hb_epoch) + " is not ASCII [0-9]+"
    if int(text) < 32:
        return "HB_EPOCH_INVALID", "hb_epoch " + text + " is below the HB32 anchor (32)"
    if reference is not None and "derived_from_clock" in reference \
            and reference["derived_from_clock"] is not False:
        return "HB_EPOCH_INVALID", ("the carrier's derived_from_clock is not exactly false; "
                                    "a clock-derived epoch is not a supplied one")
    return None


# --- shared helpers -------------------------------------------------------

def _canon(value: Any) -> bytes:
    """The conformance evaluator's canonical JSON (default ensure_ascii)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_uri(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def _next_attempt(entrypoint: str, resubmit: str) -> dict[str, Any]:
    return {"entrypoint": entrypoint, "resubmit": resubmit, "awaits_an_external_machine": False}


def _non_allow(base: Mapping[str, Any], disposition: str, failure_code: str, failed_predicate: str,
               detail: str, repair: str, retry_entrypoint: str, resubmit: str,
               owning_existing_goal: str = OWNING_GOAL, **extra: Any) -> dict[str, Any]:
    if disposition not in {"DENY", "FAIL_CLOSED"}:
        raise ValueError("a non-ALLOW disposition is DENY or FAIL_CLOSED")
    return {**base, "disposition": disposition, "failure_code": failure_code,
            "failed_predicate": failed_predicate, "detail": detail,
            "required_evidence_or_repair": repair, "retry_entrypoint": retry_entrypoint,
            "owning_existing_goal": owning_existing_goal,
            "next_attempt": _next_attempt(retry_entrypoint, resubmit), **extra}


def _route_not_published(base: Mapping[str, Any], consumer_id: str, entrypoint: str) -> dict[str, Any]:
    return _non_allow(
        base, "FAIL_CLOSED", "EDGE_CONSUMER_ROUTE_NOT_PUBLISHED",
        "EDGE_CONSUMER_ENTERS_THROUGH_SDK_PUBLISHED_ROUTE_WITH_ORG_LEDGER_RECEIPT",
        f"stegverse.route_resolution.PUBLISHED_ROUTES publishes no route for edge consumer {consumer_id}",
        "publish the consumer's route in stegverse/route_resolution.py PUBLISHED_ROUTES on "
        "routing_surface EXISTING_UNIVERSAL_INTR, bound to an installed runtime, with a registry "
        "service row whose admits_processing matches; then record it in EDGE_CONSUMERS",
        entrypoint, "THE_SAME_REQUEST_AFTER_THE_ROUTE_IS_PUBLISHED")


def _resolve_consumer_route(consumer_id: Any, declaration: Any, base: Mapping[str, Any],
                            entrypoint: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """(resolved route, None) or (None, the non-ALLOW it earns)."""
    consumer = EDGE_CONSUMERS.get(consumer_id) if isinstance(consumer_id, str) else None
    if consumer is None:
        return None, _non_allow(
            base, "DENY", "EDGE_CONSUMER_NOT_DECLARED", "EDGE_CONSUMER_IS_A_DECLARED_UNIVERSAL_INTR_CONSUMER",
            f"{consumer_id!r} is not one of {sorted(EDGE_CONSUMERS)}",
            "name a declared edge consumer, or declare the consumer in EDGE_CONSUMERS with its published route",
            entrypoint, "A_REQUEST_NAMING_A_DECLARED_CONSUMER")
    if consumer["route_id"] is None:
        return None, _route_not_published(base, consumer_id, entrypoint)
    try:
        resolved = resolve_route_declaration(declaration)
    except ValueError as exc:
        return None, _non_allow(
            base, "DENY", "ROUTE_DECLARATION_NOT_RESOLVED", "MANIFEST_DECLARES_A_PUBLISHED_INSTALLED_ROUTE",
            str(exc), "declare the consumer's published route exactly as stegverse.route_resolution publishes it",
            entrypoint, "THE_REQUEST_WITH_THE_PUBLISHED_ROUTE_DECLARATION")
    if resolved["route_id"] != consumer["route_id"]:
        return None, _non_allow(
            base, "DENY", "ROUTE_SUBSTITUTION_REFUSED", "DECLARED_ROUTE_IS_THE_CONSUMERS_PUBLISHED_ROUTE",
            f"{consumer_id} enters on {consumer['route_id']}, the request declares {resolved['route_id']}",
            "declare " + consumer["route_id"] + "; a route is never substituted",
            entrypoint, "THE_REQUEST_WITH_THE_CONSUMERS_ROUTE")
    if resolved["routing_surface"] != EXISTING_UNIVERSAL_INTR:
        return None, _non_allow(
            base, "DENY", "ROUTE_NOT_ON_EXISTING_UNIVERSAL_INTR", "ROUTE_ROUTING_SURFACE_IS_EXISTING_UNIVERSAL_INTR",
            f"{resolved['route_id']} routes on {resolved['routing_surface']}",
            "publish the consumer's route on routing_surface EXISTING_UNIVERSAL_INTR",
            entrypoint, "THE_REQUEST_AFTER_THE_ROUTE_IS_REPUBLISHED")
    return resolved, None


# --- installation (source transformation, evaluated as a transition) -----

class AnchorDrift(ValueError):
    """The router source no longer carries an anchor this installer splices at."""


def transform_router(source: str, consumer_id: str) -> str:
    """The router source with this consumer's wrapped branch installed. Idempotent."""
    consumer = EDGE_CONSUMERS[consumer_id]
    result = source
    if WRAPPER_IMPORT not in result:
        if result.count(_IMPORT_ANCHOR) != 1:
            raise AnchorDrift("shared router import anchor drift")
        result = result.replace(_IMPORT_ANCHOR, _IMPORT_ANCHOR + WRAPPER_IMPORT, 1)
    token = json.dumps(consumer["profile"])
    lines = result.splitlines(keepends=True)
    if token not in result:
        rows = [i for i, line in enumerate(lines) if '"profiles": [' in line and "]," in line]
        if len(rows) != 1:
            raise AnchorDrift("profile-list anchor drift")
        line = lines[rows[0]]
        cut = line.rfind("],")
        lines[rows[0]] = line[:cut] + ", " + token + line[cut:]
    marker = f'sdk_is_edge_submission(payload, consumer_id="{consumer_id}")'
    if marker not in "".join(lines):
        rows = [i for i, line in enumerate(lines)
                if line.lstrip().startswith(_DISPATCH_PREFIX) and "payload" in line and "admit" in line]
        if len(rows) != 1:
            raise AnchorDrift("router dispatch expression anchor drift")
        line = lines[rows[0]]
        indent = line[: len(line) - len(line.lstrip())]
        newline = "\n" if line.endswith("\n") else ""
        expression = line.strip()[len(_DISPATCH_PREFIX):]
        lines[rows[0]] = (indent + _DISPATCH_PREFIX
                          + f'sdk_admit_edge_submission(payload, consumer_id="{consumer_id}", organization_root=ROOT) '
                          + f"if {marker} else (" + expression + ")" + newline)
    result = "".join(lines)
    if "ThreadingHTTPServer" not in result or "ROOT = " not in result:
        raise AnchorDrift("shared router invariant missing")
    return result


def evaluate_installation(request: Any, router_source: bytes) -> dict[str, Any]:
    """The disposition one installation attempt earns. Never writes source."""
    base: dict[str, Any] = {"schema": INSTALLATION_RESULT_SCHEMA, "source_mutated": False,
                            "listener_started": False, "receipt_claimed": False,
                            "authority_effect": "NONE_EVALUATION_ONLY"}
    if not isinstance(request, Mapping) or request.get("schema") != INSTALLATION_REQUEST_SCHEMA:
        return _non_allow(base, "DENY", "INSTALLATION_REQUEST_ABSENT", "REQUEST_IS_ONE_INSTALLATION_REQUEST",
                          "no " + INSTALLATION_REQUEST_SCHEMA + " request",
                          "submit a " + INSTALLATION_REQUEST_SCHEMA + " request", INSTALL_ENTRYPOINT,
                          "A_WELL_FORMED_INSTALLATION_REQUEST")
    consumer_id = request.get("consumer_id")
    router = request.get("router") if isinstance(request.get("router"), Mapping) else {}
    base.update({"consumer_id": consumer_id, "router_path": router.get("path"),
                 "hb_epoch": request.get("hb_epoch")})
    epoch = supplied_epoch_failure(request.get("hb_epoch"))
    if epoch is not None:
        return _non_allow(base, "FAIL_CLOSED", epoch[0], EPOCH_PREDICATE, epoch[1],
                          "supply hb_epoch as ASCII [0-9]+ >= 32 from the heartbeat carrier; no clock is read",
                          INSTALL_ENTRYPOINT, "THE_SAME_REQUEST_WITH_THE_SUPPLIED_HB_EPOCH")
    resolved, refused = _resolve_consumer_route(consumer_id, request.get("route"), base, INSTALL_ENTRYPOINT)
    if refused is not None:
        return refused
    path = router.get("path")
    if path != DEFAULT_ROUTER:
        return _non_allow(base, "DENY", "ROUTER_NOT_THE_SHARED_UNIVERSAL_INTR_INGRESS",
                          "INSTALLATION_TARGETS_THE_EXISTING_SHARED_ROUTER",
                          f"router {path!r} is not {DEFAULT_ROUTER}; no second listener is created",
                          "name " + DEFAULT_ROUTER, INSTALL_ENTRYPOINT, "THE_REQUEST_NAMING_THE_SHARED_ROUTER")
    predecessor = sha256_uri(router_source)
    if router.get("predecessor_sha256") != predecessor:
        return _non_allow(base, "FAIL_CLOSED", "ROUTER_PREDECESSOR_DIGEST_MISMATCH",
                          "INSTALLATION_PREDECESSOR_IS_THE_OBSERVED_ROUTER_SOURCE",
                          f"declared {router.get('predecessor_sha256')}, observed {predecessor}",
                          "declare the router's current sha256 as predecessor_sha256",
                          INSTALL_ENTRYPOINT, "THE_REQUEST_WITH_THE_OBSERVED_PREDECESSOR",
                          predecessor_observed=predecessor)
    try:
        successor = transform_router(router_source.decode("utf-8"), consumer_id).encode("utf-8")
    except (AnchorDrift, UnicodeDecodeError) as exc:
        return _non_allow(base, "FAIL_CLOSED", "ROUTER_ANCHOR_DRIFT", "ROUTER_CARRIES_THE_INSTALLATION_ANCHORS",
                          str(exc), "reconcile the shared router with its anchors under its owner, "
                          "then resubmit with the new predecessor", INSTALL_ENTRYPOINT,
                          "THE_REQUEST_AFTER_THE_ROUTER_IS_RECONCILED")
    transition = {
        "predecessor": {"path": path, "sha256": predecessor},
        "proposed_successor": {"path": path, "sha256": sha256_uri(successor)},
        "manifested_capability": resolved["processor_capability"],
        "route": {"route_id": resolved["route_id"], "route_declaration_hash": resolved["route_declaration_hash"]},
        "governing_constraints": {
            "second_listener_created": False, "source_written_in_place": False,
            "credential_carried": False, "clock_read": False, "external_machine_awaited": False,
            "receiver_unavailable_disposition": RECEIVER_UNAVAILABLE_DISPOSITION},
        "evidence": {"successor_byte_count": len(successor), "noop": successor == router_source,
                     "replaces_installer": EDGE_CONSUMERS[consumer_id]["installer"],
                     "replaces_installer_blob_sha": EDGE_CONSUMERS[consumer_id]["installer_blob_sha"]},
        "hb_epoch": request["hb_epoch"],
    }
    return {**base, "disposition": "ALLOW", "transition": transition,
            "transition_sha256": canonical_sha256(transition),
            "organization_receipt": "APPENDED_BY_THE_RECEIVING_ORGANIZATION_NOT_CLAIMED_HERE",
            "successor_source": successor.decode("utf-8")}


# --- the installed wrapper ------------------------------------------------

def manifest_ingress_address(organization_root: Path) -> dict[str, Any] | None:
    """The organization's own manifest-ingress capability, from its boundary document."""
    try:
        boundary = json.loads((Path(organization_root) / BOUNDARY_DOCUMENT).read_text(encoding="utf-8"))
        rows = [row for row in boundary["ingress"]["capability_endpoint_bindings"]
                if row.get("profile_id") == MANIFEST_INGRESS_PROFILE_ID]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    if len(rows) != 1 or not isinstance(rows[0].get("receiving_operation"), Mapping):
        return None
    operation = rows[0]["receiving_operation"]
    service = operation.get("addressed_service")
    if not isinstance(boundary.get("organization"), str) or not isinstance(service, str):
        return None
    return {"organization": boundary["organization"], "addressed_service": service,
            "operation": rows[0].get("operation"), "payload_schema": rows[0].get("payload_schema")}


def is_edge_submission(payload: Any, *, consumer_id: str) -> bool:
    """True when the payload names this consumer or carries a manifest on its route."""
    if not isinstance(payload, Mapping):
        return False
    if payload.get("edge_consumer") == consumer_id:
        return True
    manifest = payload.get(MANIFEST_FIELD)
    route = ((manifest.get("extensions") or {}).get("stegverse_route")
             if isinstance(manifest, Mapping) and isinstance(manifest.get("extensions"), Mapping) else None)
    published = EDGE_CONSUMERS.get(consumer_id, {}).get("route_id")
    return isinstance(route, Mapping) and published is not None and route.get("route_id") == published


def admit_edge_submission(payload: Any, *, consumer_id: str, organization_root: Path) -> dict[str, Any]:
    """The disposition of one edge submission. Delivers nothing; awaits nothing."""
    base: dict[str, Any] = {"schema": EDGE_SUBMISSION_RESULT_SCHEMA, "consumer_id": consumer_id,
                            "receipt_claimed": False, "authority_effect": "NONE_DISPOSITION_ONLY"}
    if not isinstance(payload, Mapping) or not isinstance(payload.get(MANIFEST_FIELD), Mapping):
        return _non_allow(base, "DENY", "INGRESS_WITHOUT_MANIFEST_DISPOSITION", "SUBMISSION_CARRIES_A_MANIFEST",
                          "the payload declares no " + MANIFEST_FIELD,
                          "submit an SDK stegverse.ingress-manifest.v1 declaring the consumer's published route",
                          SUBMISSION_ENTRYPOINT, "A_MANIFEST_BEARING_SUBMISSION")
    epoch = supplied_epoch_failure(payload.get("hb_epoch"))
    if epoch is not None:
        return _non_allow(base, "FAIL_CLOSED", epoch[0], EPOCH_PREDICATE, epoch[1],
                          "supply hb_epoch as ASCII [0-9]+ >= 32 from the heartbeat carrier; no clock is read",
                          SUBMISSION_ENTRYPOINT, "THE_SAME_SUBMISSION_WITH_THE_SUPPLIED_HB_EPOCH")
    try:
        canonical = validate_ingress_manifest(payload[MANIFEST_FIELD])
        declaration = (canonical.get("extensions") or {}).get("stegverse_route")
    except ValueError as exc:
        return _non_allow(base, "DENY", "MANIFEST_NOT_ADMISSIBLE", "MANIFEST_IS_A_VALID_INGRESS_MANIFEST",
                          str(exc), "submit a manifest the SDK manifest contract admits",
                          SUBMISSION_ENTRYPOINT, "A_VALID_MANIFEST")
    resolved, refused = _resolve_consumer_route(consumer_id, declaration, base, SUBMISSION_ENTRYPOINT)
    if refused is not None:
        return refused
    route_from_manifest(canonical)  # the same resolution the receiving ingress repeats
    if (canonical.get("processing") or {}).get("capability") != resolved["processor_capability"]:
        return _non_allow(base, "DENY", "MANIFEST_CAPABILITY_ROUTE_MISMATCH",
                          "MANIFEST_PROCESSING_CAPABILITY_IS_THE_ROUTES_CAPABILITY",
                          "processing.capability does not select " + resolved["processor_capability"],
                          "declare processing.capability " + resolved["processor_capability"],
                          SUBMISSION_ENTRYPOINT, "THE_MANIFEST_WITH_THE_ROUTES_CAPABILITY")
    address = manifest_ingress_address(organization_root)
    if address is None:
        return _non_allow(base, "FAIL_CLOSED", "MANIFEST_INGRESS_NOT_DECLARED",
                          "ORGANIZATION_DECLARES_ONE_SDK_MANIFEST_INGRESS",
                          f"{BOUNDARY_DOCUMENT} declares no single {MANIFEST_INGRESS_PROFILE_ID} binding",
                          "declare the organization's sdk-manifest-ingress binding in " + BOUNDARY_DOCUMENT,
                          SUBMISSION_ENTRYPOINT, "THE_SAME_SUBMISSION_AFTER_THE_BINDING_IS_DECLARED")
    manifest_sha256 = sha256_uri(_canon(dict(payload[MANIFEST_FIELD])))
    return {**base, "disposition": "ALLOW", "organization": address["organization"],
            "submission": {"addressed_service": address["addressed_service"],
                           "operation": address["operation"], "payload_schema": address["payload_schema"],
                           "payload": {MANIFEST_FIELD: dict(payload[MANIFEST_FIELD]),
                                       "manifest_sha256": manifest_sha256},
                           "hb_epoch": payload["hb_epoch"]},
            "route": {"route_id": resolved["route_id"], "route_declaration_hash": resolved["route_declaration_hash"]},
            "receiver_unavailable_disposition": RECEIVER_UNAVAILABLE_DISPOSITION,
            "organization_receipt": "APPENDED_BY_THE_RECEIVING_ORGANIZATION_NOT_CLAIMED_HERE"}


# --- role-version recording and re-adoption -------------------------------

def _safe_relative(path: Any) -> str | None:
    if not isinstance(path, str) or not path or "\\" in path:
        return None
    pure = PurePosixPath(path)
    return None if pure.is_absolute() or ".." in pure.parts else str(pure)


def role_version_file_entry(path: str, raw: bytes) -> dict[str, Any]:
    """One target-role-version file entry, in the form check_target_version admits."""
    if _safe_relative(path) is None:
        raise ValueError(f"not a safe relative path: {path!r}")
    return {"path": path, "blob_sha": git_blob_sha(raw), "byte_count": len(raw),
            "contract_digest": sha256_uri(raw)}


def role_version_contract_digest(files: list[Mapping[str, Any]]) -> str:
    return sha256_uri(_canon(list(files)))


def extend_role_version_files(files: list[Mapping[str, Any]], entries: list[Mapping[str, Any]]) -> dict[str, Any]:
    """A successor files list with ``entries`` recorded, and its contract digest."""
    paths = [entry["path"] for entry in files]
    for entry in entries:
        if entry["path"] in paths:
            raise ValueError("already recorded: " + entry["path"])
        paths.append(entry["path"])
    successor = [dict(entry) for entry in files] + [dict(entry) for entry in entries]
    return {"files": successor, "contract_digest": role_version_contract_digest(successor),
            "digest_scope": "SHA256_OF_CANONICAL_JSON_OF_FILES_LIST (each file: UTF8_FILE_BYTES)"}


def plan_readoption(evaluation: Any, *, predecessor_files: list[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """The re-adoption transition that follows one conformance evaluation.

    A file is re-adopted whole only where that preserves the organization's own
    valid changes: it is absent here, or its bytes here equal a recorded file of
    the predecessor version (the organization changed nothing). Any other
    difference is organization-specific behaviour and is not overwritten.
    """
    base: dict[str, Any] = {"schema": READOPTION_RESULT_SCHEMA, "source_mutated": False,
                            "receipt_claimed": False, "authority_effect": "NONE_PLAN_ONLY"}
    if not isinstance(evaluation, Mapping) or evaluation.get("schema") != CONFORMANCE_RESULT_SCHEMA:
        return _non_allow(base, "DENY", "CONFORMANCE_EVALUATION_ABSENT", "PLAN_FOLLOWS_ONE_CONFORMANCE_EVALUATION",
                          "no " + CONFORMANCE_RESULT_SCHEMA, "evaluate the organization first",
                          CONFORMANCE_ENTRYPOINT, "THE_PLAN_WITH_THE_EVALUATION", ROLE_PROPAGATION_OWNER)
    base.update({"organization": evaluation.get("organization"),
                 "target_role_version_id": evaluation.get("target_role_version_id"),
                 "target_contract_digest": evaluation.get("target_contract_digest")})
    disposition = evaluation.get("disposition")
    if disposition == "ALLOW":
        return {**base, "disposition": "ALLOW", "readopt": [], "detail": "already conforming"}
    if disposition == "DENY":
        return _non_allow(base, "DENY", "CONFORMANCE_REQUEST_DEFECT_NOT_REPAIRED_BY_ADOPTION",
                          str(evaluation.get("failed_predicate")),
                          "the evaluation refused the request itself; adopting source does not repair it",
                          "the issuer reissues the conformance request with the refused predicate satisfied",
                          CONFORMANCE_ENTRYPOINT, "A_REISSUED_CONFORMANCE_REQUEST", ROLE_PROPAGATION_OWNER)
    if disposition != "FAIL_CLOSED" or evaluation.get("failed_predicate") != PARITY_PREDICATE:
        return _non_allow(base, "FAIL_CLOSED", "CONFORMANCE_FAIL_CLOSED_NOT_PARITY",
                          str(evaluation.get("failed_predicate")),
                          "only a parity FAIL_CLOSED names files to re-adopt",
                          str(evaluation.get("required_evidence_or_repair") or "repair the named predicate"),
                          CONFORMANCE_ENTRYPOINT, "THE_SAME_MANIFEST_AFTER_THE_REPAIR", ROLE_PROPAGATION_OWNER)
    prior = {(entry.get("path"), entry.get("contract_digest")) for entry in predecessor_files or []}
    readopt, unreconciled = [], []
    for row in evaluation.get("differing_files") or []:
        observed = row.get("observed")
        step = {"path": row.get("path"), "predecessor": observed, "proposed_successor": row.get("recorded")}
        if observed == "ABSENT" or (isinstance(observed, Mapping)
                                    and (row.get("path"), observed.get("contract_digest")) in prior):
            readopt.append(step)
        else:
            unreconciled.append(step)
    if unreconciled:
        return _non_allow(base, "FAIL_CLOSED", "ORG_SPECIFIC_BEHAVIOUR_UNRECONCILED",
                          "READOPTION_PRESERVES_THE_ORGANIZATIONS_OWN_VALID_CHANGES",
                          "differs from both the target and the predecessor version: "
                          + ", ".join(sorted(str(step["path"]) for step in unreconciled)),
                          "a function-level port of the target's changes into the organization's file, "
                          "then re-evaluate", READOPTION_ENTRYPOINT,
                          "THE_PLAN_AFTER_THE_PORT", ROLE_PROPAGATION_OWNER,
                          readopt=readopt, unreconciled=unreconciled)
    return {**base, "disposition": "ALLOW", "readopt": readopt,
            "next_transition": "A_SEPARATE_MANIFEST_BOUND_SOURCE_TRANSITION_PER_FILE_UNDER_" + ROLE_PROPAGATION_OWNER,
            "then": _next_attempt(CONFORMANCE_ENTRYPOINT, "THE_SAME_MANIFEST_AFTER_THE_SOURCE_TRANSITION")}


# --- CLI (evaluation only) -------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    install = sub.add_parser("evaluate-installation")
    install.add_argument("--request", type=Path, required=True)
    install.add_argument("--organization-root", type=Path, required=True)
    install.add_argument("--successor-out", type=Path,
                         help="write the proposed successor here; the router itself is never written")
    entry = sub.add_parser("role-version-entry")
    entry.add_argument("--organization-root", type=Path, required=True)
    entry.add_argument("--path", required=True)
    plan = sub.add_parser("plan-readoption")
    plan.add_argument("--evaluation", type=Path, required=True)
    plan.add_argument("--predecessor-files", type=Path)
    args = parser.parse_args(argv)
    if args.command == "evaluate-installation":
        request = json.loads(args.request.read_text(encoding="utf-8"))
        router = args.organization_root / DEFAULT_ROUTER
        result = evaluate_installation(request, router.read_bytes() if router.is_file() else b"")
        successor = result.pop("successor_source", None)
        if successor is not None and args.successor_out is not None:
            if args.successor_out.resolve() == router.resolve():
                raise SystemExit("the successor is never written over the router")
            args.successor_out.write_text(successor, encoding="utf-8")
    elif args.command == "role-version-entry":
        result = role_version_file_entry(args.path, (args.organization_root / args.path).read_bytes())
    else:
        prior = json.loads(args.predecessor_files.read_text(encoding="utf-8")) if args.predecessor_files else None
        result = plan_readoption(json.loads(args.evaluation.read_text(encoding="utf-8")), predecessor_files=prior)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("disposition", "ALLOW") == "ALLOW" else 2


__all__ = [
    "EDGE_CONSUMERS", "INSTALLATION_REQUEST_SCHEMA", "WRAPPER_IMPORT", "AnchorDrift",
    "admit_edge_submission", "evaluate_installation", "extend_role_version_files", "is_edge_submission",
    "manifest_ingress_address", "plan_readoption", "role_version_contract_digest", "role_version_file_entry",
    "supplied_epoch_failure", "transform_router",
]

if __name__ == "__main__":
    sys.exit(main())
