"""One-way InTr hop lane across advertised ``intr-destination`` peers.

The peer set is whatever organization checkouts advertise at
``<slug>.intr-destination`` (``profile_id`` ``intr-destination`` on the
overlay, addressed service ``organization_slug + "." + profile_id`` on the
service row). ``org-boundary/registry/federation.json`` is not a peer source
and is not read.

Each ordered pair is one one-way hop. The lane emits a manifested diagnostic
packet, resolves the destination from that advertisement, and closes on the
responded request class plus ``communication_id``. Receipts are then read
back from the sender ledger (egress emission and closure) and the destination
ledger (ingress repository receipt and the organization receipt that consumes
it). A disposition is transition evidence. Authority and time are constraints
supplied to the hop, not something this lane confers.

``fabricated`` (the CI default) uses temporary mesh and ledger roots. The
kernel and the ledger writer are a temp copy of the merged
``StegVerse-org/.github`` contract with the peer's organization identity
stamped on it. Peer checkouts are read for advertisements only, so an
in-flight ledger writer is not imported. The far side is that kernel's
``receipt`` / ``build_control_response``. That answer is not a live peer and
is not an authentic production receipt.

``live`` asks the GitHub API for each candidate organization's
``<org>/.github`` advertisement. The candidate set is the eight organizations
below. It is not ``federation.json``, and it is not a list of repositories
one machine happened to be able to clone. Public repositories are read
without a token. A token in ``FEDERATION_READ_TOKEN``, when set, is sent as a
bearer credential so a private repository can be read too. An organization
whose advertisement cannot be read stays in the peer set: every hop that
uses it is ``UNREACHABLE``. A peer whose ledger ref cannot be read is
``UNREACHABLE`` the same way. A ``PASS`` is claimed only for receipts this
process read back.

``orchestrate`` is manifest-directed and does not wait. It first reads every
organization ledger (the live readback above) and derives each ordered pair's
ledger state: ``CLOSED``, ``REFUSED``, ``OPEN`` (sent, not yet closed) or
``UNSENT``. For each pair it then records one disposition. An ``UNSENT`` pair
whose sender and destination hold no open hop is a send transition: the
sender's ``intr-destination-hop.yml`` send phase is dispatched (credential:
``FEDERATION_HOP_TOKEN``; the TV/TVC credential path is a pending owner
decision on StegVerse-Labs/.github#2897). A dispatched or ``OPEN`` hop
resolves as ``DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION`` with
``always_on_receiver_required: false``: the destination's receive and the
sender's close materialize from the dispatched events and are observed only as
receipts in the next readback. Nothing polls a ledger, sleeps, or bounds a
wait. Each organization appears in at most one dispatched hop per transition
and an organization with an open hop is not dispatched, because every
organization's ledger runs share one concurrency group and GitHub cancels a
second pending run in a group. The epoch is supplied (``--hb-epoch``); no
clock is read for it.

Every non-ALLOW outcome (``UNREACHABLE``, ``NOT_DISPATCHED``, ``FAIL``,
``CLOSURE_REFUSED``, ``DEFERRED_ORGANIZATION_LEDGER_CONCURRENCY``) carries
``failure_code``, ``failed_predicate``, ``required_evidence_or_repair``,
``retry_entrypoint``, ``owning_existing_goal`` and ``next_attempt``.

Ledger integrity separates what fails from what is reported. A receipt
committed to the ledger ref before the organization's supplied-epoch writer
reached its default branch is ``LEGACY``. Its orphan, duplicate, source, and
clock findings are reported and do not fail the lane. History is not
rewritten. Repository receipts that repeat one transition with identical
evidence are reported as identical duplicates. Divergent duplicates fail
unless every copy is legacy.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from stegverse._stdlib_http import HttpTransportError
from stegverse._stdlib_http import get as http_get
from stegverse._stdlib_http import post as http_post

PROFILE_ID = "intr-destination"
ADDRESS_FORM = "ORGANIZATION_SLUG_DOT_CAPABILITY_PROFILE_ID"
REQUEST_CLASS = "ecosystem.communication"
ACK_CLASS = "ecosystem.communication.ack"
PAYLOAD_SCHEMA = "stegverse.org-intr-destination-diagnostic/v1"
MANIFEST_SCHEMA = "stegverse.intr-hop-manifest/v1"
REPORT_SCHEMA = "stegverse.sdk.intr-destination-hop-lane/v1"
OVERLAY_RELATIVE = "org-runtime/interlock-intr.json"
REGISTRY_RELATIVE = "org-boundary/registry/services.json"
CONTRACT_RELATIVE = ".stegverse/transition-ledger/contract.json"
LEDGER_REF = "refs/stegverse/organization-ledger"
GITHUB_API = "https://api.github.com"
FEDERATION_READ_TOKEN_ENV = "FEDERATION_READ_TOKEN"
# Dispatches the hop workflow in every organization (classic PAT: repo +
# workflow). Reads fall back to it when FEDERATION_READ_TOKEN is unset.
FEDERATION_HOP_TOKEN_ENV = "FEDERATION_HOP_TOKEN"
HOP_WORKFLOW = "intr-destination-hop.yml"
WRITER_WORKFLOW = ".github/workflows/organization-ledger-transition.yml"
CLOSURE_REFUSED_CLASS = "ORGANIZATION_EGRESS_CLOSURE_REFUSED"
LEGACY = "LEGACY"
DURABLE_QUEUE = "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION"
OWNING_EXISTING_GOAL = "StegVerse-Labs/.github#2897 / StegVerse-org/.github#162 P0-runtime-and-custody"
NON_ALLOW_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
                    "retry_entrypoint", "owning_existing_goal", "next_attempt")
LANE_WORKFLOW = ".github/workflows/intr-destination-hop-lane.yml"
NOT_SENT_FINDING = "CORRELATED_RECEIPTS_NOT_IN_THE_READ_LEDGERS"
# Reported, not failing, when every receipt it names is LEGACY.
LEGACY_REPORTABLE = (
    "ORPHAN_ORGANIZATION_RECEIPT",
    "ORPHAN_REPOSITORY_RECEIPT",
    "DUPLICATE_REPOSITORY_RECEIPT",
    "SOURCE_RECEIPT_DOES_NOT_MATCH_REPOSITORY_CHAIN",
    "TIME_CONSTRAINT_DERIVED_FROM_CLOCK",
    "AUTHORITY_CONSTRAINT_IS_NOT_NONE",
)
# Live mode requests each of these organizations' `<org>/.github` advertisement.
# Membership still comes from the advertisement when it can be read. An
# organization that cannot be read is kept, and its hops are UNREACHABLE.
CANDIDATE_ORGANIZATIONS = (
    "StegVerse-org",
    "StegVerse-Labs",
    "SV-LLM",
    "SV-011",
    "GCAT-BCAT-Engine",
    "Admissible-Existence",
    "StegVerse-002",
    "StegGhost",
)
EPOCH_ORIGIN = 32
EMITTED_CLASS = "ORGANIZATION_EGRESS_EMITTED"
CLOSED_CLASS = "ORGANIZATION_EGRESS_CLOSED"
INGRESS_CLASS = "ORGANIZATION_INTR_DESTINATION_INGRESS"
REPO_SCHEMA = "stegverse.repo-transition-receipt/v1"
ORG_SCHEMA = "stegverse.organization-transition-receipt/v1"
AUTHORITY_CONSTRAINT = "NONE"
TIME_CONSTRAINT = "SUPPLIED_HB_EPOCH"
EVIDENCE_FABRICATED = "FABRICATED_NON_AUTHENTIC"
EVIDENCE_LIVE = "READ_BACK_FROM_ORGANIZATION_LEDGER_REF"
FAR_SIDE = "kernel.receipt/build_control_response"
REFERENCE_ORGANIZATION = "StegVerse-org"
REFERENCE_REPOSITORY = "StegVerse-org/.github"
REFERENCE_SLUG = "stegverse-org"

_LEDGER_ENV = ("STEGVERSE_REPO_LEDGER_ROOT", "STEGVERSE_ORG_LEDGER_ROOT", "STEGVERSE_REPO_LEDGER_HOME")

_SENDER = r"""
import inspect, json, sys
from pathlib import Path

def load(root, name, relative):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, root / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def call(fn, *args):
    # Positional arguments the merged egress records share. A checkout whose
    # signature grew an optional tail still accepts this prefix.
    return fn(*args[:len(inspect.signature(fn).parameters)])

def publish_frame(kernel, packet, mesh, epoch):
    # publish_packet on some checkouts refuses without crossing custody and
    # appends a second receipt pair. The frame the mesh actually carries is
    # carrier_frame plus publish_frame. Epoch is supplied where the kernel
    # accepts it, so the carrier does not read a clock when it can avoid it.
    params = inspect.signature(kernel.carrier_frame).parameters
    frame = kernel.carrier_frame(packet, epoch=epoch) if "epoch" in params else kernel.carrier_frame(packet)
    path = kernel.publish_frame(frame, root=mesh)
    return {"packet": packet, "frame": frame, "path": str(path)}

req = json.load(sys.stdin)
root = Path(req["root"])
mesh = Path(req["mesh"])
try:
    egress = load(root, "organization_egress_boundary", "resident-runtime/organization_egress_boundary.py")
    kernel = egress.kernel
except Exception as exc:
    print(json.dumps({"ok": False, "type": type(exc).__name__, "reason": str(exc)[:800],
                      "stage": "import"}))
    raise SystemExit(0)

results = []
for hop in req["hops"]:
    try:
        payload = hop["payload"]
        resolved = hop["resolved"]
        epoch = hop["epoch"]
        packet = kernel.build_packet(
            origin_org=hop["origin"], origin_service=hop["origin_service"],
            destination_org=resolved["destination_organization"],
            destination_service=resolved["destination_service"],
            payload=payload, standing=hop["standing"],
            transition_reference="intr-destination-hop.v1", authority_effect="NONE",
            packet_id=hop["packet_id"])
        published = publish_frame(kernel, packet, mesh, epoch)
        emission = call(egress.emission_record, resolved, hop["origin"], packet, published["frame"], payload)
        emission_receipts = egress._record(
            egress.EMITTED_CLASS + ":" + packet["packet_id"], egress.EMITTED_CLASS,
            emission["payload_sha256"], egress.sha(emission), emission, epoch)
        chain, previous = [], None
        for kind in egress.FAR_SIDE_RECEIPT_KINDS:
            receipt = kernel.receipt(kind, packet["packet_id"], packet["destination"]["service"], previous,
                                     {"payload_hash": kernel.sha(packet["payload"])})
            chain.append(receipt["receipt_id"])
            previous = receipt["receipt_id"]
        response = kernel.build_control_response(packet, {"application_result": {
            "schema": "stegverse.org-intr-destination-result/v1", "disposition": "ALLOW",
            "authority_effect": "NONE_DIAGNOSTIC_ACK_ONLY", "fabricated_non_authentic": True,
        }, "reconstruction": {"terminal_receipt_id": chain[-1]}})
        publish_frame(kernel, response, mesh, epoch + 1)
        collected = kernel.collect_ecosystem_responses(hop["origin"], payload["communication_id"], mesh_root=mesh)
        rows = [row for row in collected.get("organizations", [])
                if row.get("organization") == resolved["destination_organization"]]
        if len(rows) != 1:
            raise RuntimeError("expected one fabricated response, saw %s" % len(rows))
        findings = egress.verify_closure(resolved, packet["packet_id"], rows[0], emission)
        recomputed = egress.reconstruct_far_side_chain(
            packet["packet_id"], emission["far_side_service_id"], emission["far_side_payload_hash"])
        closure = call(egress.closure_record, resolved, hop["origin"], packet["packet_id"],
                       payload["communication_id"], rows[0], findings, recomputed)
        transition_class = egress.CLOSED_CLASS if not findings else egress.CLOSURE_REFUSED_CLASS
        closure_receipts = egress._record(
            transition_class + ":" + packet["packet_id"], transition_class,
            egress.sha({"packet_id": packet["packet_id"], "communication_id": payload["communication_id"]}),
            egress.sha(closure), closure, epoch + 2)
        results.append({
            "ok": True, "communication_id": payload["communication_id"], "packet_id": packet["packet_id"],
            "closure_findings": findings, "closure_disposition": closure.get("disposition"),
            "response_message_class": rows[0].get("message_class"),
            "far_side_terminal_receipt": chain[-1], "far_side": "kernel.receipt/build_control_response",
            "far_side_authentic": False,
            "emission_repository_receipt_sha256": emission_receipts["repository_receipt"]["receipt_sha256"],
            "emission_organization_receipt_sha256": emission_receipts["organization_receipt"]["receipt_sha256"],
            "closure_repository_receipt_sha256": closure_receipts["repository_receipt"]["receipt_sha256"],
            "closure_organization_receipt_sha256": closure_receipts["organization_receipt"]["receipt_sha256"],
            "payload_sha256": emission.get("payload_sha256"),
        })
    except Exception as exc:
        results.append({"ok": False, "type": type(exc).__name__, "reason": str(exc)[:800],
                        "communication_id": hop.get("payload", {}).get("communication_id"), "stage": "hop"})
print(json.dumps({"ok": True, "hops": results}))
"""

_DESTINATION = r"""
import json, sys
from pathlib import Path

def load(root, name, relative):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, root / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

req = json.load(sys.stdin)
root = Path(req["root"])
try:
    ingress = load(root, "intr_destination_ingress", "resident-runtime/intr_destination_ingress.py")
    registry = json.loads((root / "org-boundary/registry/services.json").read_text(encoding="utf-8"))
except Exception as exc:
    print(json.dumps({"ok": False, "type": type(exc).__name__, "reason": str(exc)[:800], "stage": "import"}))
    raise SystemExit(0)

results = []
for hop in req["hops"]:
    try:
        result = ingress.receive(hop["payload"], registry=registry, packet_id=hop["packet_id"], hb_epoch=hop["epoch"])
        results.append({"ok": True, "communication_id": hop["payload"]["communication_id"],
                        "disposition": result.get("disposition"), "received": result.get("received"),
                        "failed_predicate": result.get("failed_predicate"), "detail": result.get("detail"),
                        "repository_receipt_sha256": result.get("repository_receipt_sha256"),
                        "organization_receipt_sha256": result.get("organization_receipt_sha256"),
                        "communication_acknowledged": result.get("communication_acknowledged")})
    except Exception as exc:
        results.append({"ok": False, "type": type(exc).__name__, "reason": str(exc)[:800],
                        "communication_id": hop.get("payload", {}).get("communication_id"), "stage": "ingress"})
print(json.dumps({"ok": True, "hops": results}))
"""


def organization_slug(organization: str) -> str:
    """The same slug the organization kernel derives for a capability address."""
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in organization).strip("-")


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: Any) -> str:
    raw = value if isinstance(value, (bytes, bytearray)) else canon(value)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _namespace_from_contract(document: Any) -> str | None:
    if not isinstance(document, dict):
        return None
    location = document.get("repository_ledger_location")
    namespace = location.get("namespace") if isinstance(location, dict) else None
    return namespace if isinstance(namespace, str) and namespace else None


def _peer_from_documents(overlay: Any, registry: Any, *, root: str | None, source: str) -> dict[str, Any] | None:
    """A peer when these two documents advertise ``<slug>.intr-destination``.

    Any other shape is not a peer. The caller has already read the documents;
    this function does not open ``federation.json``.
    """
    organization = registry.get("organization") if isinstance(registry, dict) else None
    if not isinstance(organization, str) or not organization.strip():
        return None
    slug = organization_slug(organization)
    address = slug + "." + PROFILE_ID
    bindings = ((overlay.get("ingress") or {}).get("capability_endpoint_bindings") or []) if isinstance(overlay, dict) else []
    matches = [entry for entry in bindings if isinstance(entry, dict) and entry.get("profile_id") == PROFILE_ID]
    if len(matches) != 1:
        return None
    receiving = matches[0].get("receiving_operation") or {}
    if receiving.get("addressed_service") != address:
        return None
    services = registry.get("services") or []
    row = next((item for item in services if isinstance(item, dict) and item.get("service_id") == address), None)
    if row is None or row.get("capability_profile_id") != PROFILE_ID:
        return None
    repository = row.get("repository") if isinstance(row.get("repository"), str) else None
    return {
        "organization": organization,
        "slug": slug,
        "address": address,
        "profile_id": PROFILE_ID,
        "repository": repository,
        "root": root,
        "advertisement": {
            "overlay": OVERLAY_RELATIVE,
            "registry": REGISTRY_RELATIVE,
            "address_form": ADDRESS_FORM,
        },
        "advertisement_readable": True,
        "unreadable_reason": None,
        "peer_source": source,
        "repository_namespace": None,
    }


def _unreachable_peer(organization: str, reason: str) -> dict[str, Any]:
    """Keep an organization whose advertisement could not be read.

    The address is the login slug plus the profile id. It is a placeholder
    until the advertisement is read, and hops that use it are UNREACHABLE.
    """
    slug = organization_slug(organization)
    return {
        "organization": organization,
        "slug": slug,
        "address": slug + "." + PROFILE_ID,
        "profile_id": PROFILE_ID,
        "repository": organization + "/.github",
        "root": None,
        "advertisement": None,
        "advertisement_readable": False,
        "unreadable_reason": reason,
        "peer_source": "GITHUB_API_ADVERTISEMENT_UNREADABLE",
        "repository_namespace": None,
    }


def discover_peers(roots: Iterable[Path | str]) -> list[dict[str, Any]]:
    """Peers whose own overlay and service row advertise ``<slug>.intr-destination``.

    A root that does not advertise the capability is not a peer. A name that
    appears only in a federation directory is not a peer: that file is never
    opened.
    """
    peers: list[dict[str, Any]] = []
    seen: dict[str, Path] = {}
    for raw in roots:
        root = Path(raw)
        overlay_path = root / OVERLAY_RELATIVE
        registry_path = root / REGISTRY_RELATIVE
        if not overlay_path.is_file() or not registry_path.is_file():
            continue
        try:
            overlay = _load_json(overlay_path)
            registry = _load_json(registry_path)
        except (OSError, json.JSONDecodeError):
            continue
        peer = _peer_from_documents(overlay, registry, root=str(root.resolve()), source="ADVERTISED_CAPABILITY")
        if peer is None:
            continue
        contract = root / CONTRACT_RELATIVE
        if contract.is_file():
            try:
                peer["repository_namespace"] = _namespace_from_contract(_load_json(contract))
            except (OSError, json.JSONDecodeError):
                peer["repository_namespace"] = None
        if peer["slug"] in seen:
            raise ValueError("two checkouts advertise the same intr-destination address: " + peer["address"])
        seen[peer["slug"]] = root
        peers.append(peer)
    peers.sort(key=lambda peer: peer["slug"])
    return peers


def _blank_to_none(token: str | None) -> str | None:
    if not isinstance(token, str):
        return None
    token = token.strip()
    return token or None


def github_read_file(repository: str, path: str, *, token: str | None = None,
                     getter: Callable[..., Any] | None = None) -> tuple[str, Any]:
    """Read one file from a GitHub repository's default branch.

    No token is sent unless ``token`` is non-blank. The token is a bearer
    header, never part of the URL. Status is ``ok``, ``HTTP_<code>``,
    ``TRANSPORT``, or ``NOT_JSON``. The body of an error response is discarded.
    """
    token = _blank_to_none(token)
    url = GITHUB_API + "/repos/" + repository + "/contents/" + path
    headers = {
        "Accept": "application/vnd.github.raw",
        "User-Agent": "stegverse-intr-hop-lane",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        response = (getter or http_get)(url, headers=headers, timeout=30)
    except HttpTransportError:
        return "TRANSPORT", None
    if getattr(response, "status_code", None) != 200:
        code = getattr(response, "status_code", None)
        return "HTTP_%s" % code, None
    try:
        return "ok", json.loads(response.content.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError, AttributeError):
        return "NOT_JSON", None


def _advertisement_status(status: str) -> str:
    if status == "ok":
        return "ok"
    if status.startswith("HTTP_"):
        return "ADVERTISEMENT_NOT_READABLE_" + status
    if status == "TRANSPORT":
        return "ADVERTISEMENT_NOT_READABLE_TRANSPORT"
    if status == "NOT_JSON":
        return "ADVERTISEMENT_NOT_JSON"
    return status


def discover_peers_from_github(organizations: Sequence[str] = CANDIDATE_ORGANIZATIONS, *,
                               token: str | None = None,
                               read_file: Callable[[str, str], tuple[str, Any]] | None = None,
                               ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Peers for live mode, one slot per organization whose advertisement is requested.

    ``read_file(repository, path)`` returns ``(status, document)`` using the
    same status words as ``github_read_file``. An organization whose overlay
    or service row cannot be read is still a peer. An organization that was
    read and does not advertise ``intr-destination`` is not a peer; it is
    returned in the second list. ``federation.json`` is not requested.
    """
    token = _blank_to_none(token)
    reader = read_file or (lambda repository, path: github_read_file(repository, path, token=token))
    peers: list[dict[str, Any]] = []
    silent: list[dict[str, str]] = []
    seen: dict[str, str] = {}
    for organization in organizations:
        repository = organization + "/.github"
        overlay_status, overlay = reader(repository, OVERLAY_RELATIVE)
        registry_status, registry = reader(repository, REGISTRY_RELATIVE)
        contract_status, contract = reader(repository, CONTRACT_RELATIVE)
        overlay_status = _advertisement_status(overlay_status)
        registry_status = _advertisement_status(registry_status)
        if overlay_status != "ok" or registry_status != "ok":
            reason = overlay_status if overlay_status != "ok" else registry_status
            peer = _unreachable_peer(organization, reason)
        else:
            peer = _peer_from_documents(overlay, registry, root=None, source="GITHUB_API_ADVERTISEMENT")
            if peer is None:
                silent.append({"organization": organization, "repository": repository})
                continue
            if contract_status == "ok":
                peer["repository_namespace"] = _namespace_from_contract(contract)
        if peer["slug"] in seen:
            raise ValueError("two organizations resolve to the same intr-destination address: " + peer["address"])
        seen[peer["slug"]] = organization
        peers.append(peer)
    peers.sort(key=lambda peer: peer["slug"])
    silent.sort(key=lambda item: item["organization"])
    return peers, silent


def git_auth_header(token: str) -> str:
    """The extra header git sends to github.com for ``token``."""
    basic = base64.b64encode(("x-access-token:" + token).encode("utf-8")).decode("ascii")
    return "Authorization: Basic " + basic


def materialize_remote_ledger(repository: str, dest: Path, token: str | None) -> str | None:
    """Fetch ``refs/stegverse/organization-ledger`` into ``dest``.

    Returns a reason when the ref cannot be read. The token, when set, is a
    git extra header (HTTP basic, ``x-access-token``), not part of the remote
    URL. The full ref history is fetched: the commit that added a receipt is
    what places it before or after the organization's writer.
    """
    token = _blank_to_none(token)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    if token:
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.extraheader"
        env["GIT_CONFIG_VALUE_0"] = git_auth_header(token)
    url = "https://github.com/" + repository + ".git"
    try:
        init = subprocess.run(["git", "init", "-q"], cwd=dest, env=env, capture_output=True, text=True, timeout=30)
        if init.returncode != 0:
            return "LEDGER_REF_NOT_READABLE"
        fetched = subprocess.run(
            ["git", "fetch", "--quiet", url, LEDGER_REF + ":" + LEDGER_REF],
            cwd=dest, env=env, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return "LEDGER_REF_NOT_READABLE"
    if fetched.returncode != 0:
        return "LEDGER_REF_NOT_READABLE"
    return None


def ordered_pairs(peers: Sequence[Mapping[str, Any]]) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    """Every one-way hop. A peer does not send a diagnostic to itself."""
    return [(sender, dest) for sender in peers for dest in peers if sender["slug"] != dest["slug"]]


def manifested_payload(sender: Mapping[str, Any], dest: Mapping[str, Any], communication_id: str) -> dict[str, Any]:
    """An ``ecosystem.communication`` whose body is the diagnostic schema.

    The manifest is inside the body, so the payload digest binds it. The
    request class is one the boundary answers; closure correlates on
    ``communication_id``.
    """
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "sender_organization": sender["organization"],
        "destination_organization": dest["organization"],
        "destination_service": dest["address"],
        "capability_profile_id": PROFILE_ID,
        "request_class": REQUEST_CLASS,
        "communication_id": communication_id,
        "authority_constraint": AUTHORITY_CONSTRAINT,
        "time_constraint": TIME_CONSTRAINT,
    }
    return {
        "message_class": REQUEST_CLASS,
        "communication_id": communication_id,
        "subject": "intr-destination hop diagnostic",
        "body": {
            "schema": PAYLOAD_SCHEMA,
            "probe": "intr-hop-integrity",
            "manifest_sha256": sha256(manifest),
            "manifest": manifest,
        },
    }


def reference_root_for(peers: Sequence[Mapping[str, Any]], explicit: Path | str | None = None) -> Path:
    """The merged ledger and kernel contract. Peer checkouts advertise; they do not supply an unmerged writer."""
    if explicit:
        return Path(explicit)
    for peer in peers:
        if peer.get("organization") == REFERENCE_ORGANIZATION or peer.get("repository") == REFERENCE_REPOSITORY:
            return Path(peer["root"])
    raise ValueError("fabricated mode needs the merged " + REFERENCE_REPOSITORY + " checkout")


def _write_json(path: Path, document: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def materialize_reference(reference: Path, peer: Mapping[str, Any], dest: Path) -> Path:
    """A temp copy of the merged contract with this peer's organization identity stamped on it.

    The copy is the fabricated runtime. It is not the peer's checkout and it is
    not that organization's ledger. Advertisement still comes from the peer.
    """
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(reference, dest, ignore=shutil.ignore_patterns(".git"), symlinks=False)
    organization = peer["organization"]
    repository = peer.get("repository") or (organization + "/.github")
    slug = peer["slug"]
    contract_path = dest / ".stegverse" / "transition-ledger" / "contract.json"
    contract = _load_json(contract_path)
    contract["repository"] = repository
    location = contract.get("repository_ledger_location")
    if isinstance(location, dict):
        location["repository"] = repository
        if isinstance(location.get("namespace"), str):
            location["namespace"] = "repository-ledger/" + repository
    _write_json(contract_path, contract)
    org_contract_path = dest / ".stegverse" / "transition-ledger" / "org-contract.json"
    org_contract = _load_json(org_contract_path)
    org_contract["organization"] = organization
    org_contract["organization_ledger_repository"] = repository
    _write_json(org_contract_path, org_contract)
    registry_path = dest / REGISTRY_RELATIVE
    registry = _load_json(registry_path)
    registry["organization"] = organization
    for row in registry.get("services") or []:
        if isinstance(row, dict) and isinstance(row.get("service_id"), str) and row["service_id"].startswith(REFERENCE_SLUG + "."):
            row["service_id"] = slug + row["service_id"][len(REFERENCE_SLUG):]
            row["repository"] = repository
    _write_json(registry_path, registry)
    overlay_path = dest / OVERLAY_RELATIVE
    overlay = _load_json(overlay_path)
    bindings = (overlay.get("ingress") or {}).get("capability_endpoint_bindings") or []
    for entry in bindings:
        receiving = entry.get("receiving_operation") or {}
        addressed = receiving.get("addressed_service")
        if isinstance(addressed, str) and addressed.startswith(REFERENCE_SLUG + "."):
            receiving["addressed_service"] = slug + addressed[len(REFERENCE_SLUG):]
    proven = (overlay.get("egress") or {}).get("peer_capability_resolution") or {}
    named = proven.get("proven_on_this_organization")
    if isinstance(named, str) and named.startswith(REFERENCE_SLUG + "."):
        proven["proven_on_this_organization"] = slug + named[len(REFERENCE_SLUG):]
    elif isinstance(named, list):
        proven["proven_on_this_organization"] = [
            slug + item[len(REFERENCE_SLUG):] if isinstance(item, str) and item.startswith(REFERENCE_SLUG + ".") else item
            for item in named]
    _write_json(overlay_path, overlay)
    old_owner = 'OWNER_REPOSITORY = "' + REFERENCE_REPOSITORY + '"'
    new_owner = 'OWNER_REPOSITORY = "' + repository + '"'
    for relative in ("resident-runtime/organization_egress_boundary.py", "resident-runtime/intr_destination_ingress.py"):
        path = dest / relative
        path.write_text(path.read_text(encoding="utf-8").replace(old_owner, new_owner), encoding="utf-8")
    return dest


def destination_resolution(dest: Mapping[str, Any]) -> dict[str, Any]:
    """The address the destination advertises. Not a federation-directory lookup.

    An organization whose advertisement was not read contributes a placeholder
    address. The resolution source says so, and the hop is UNREACHABLE.
    """
    readable = dest.get("advertisement_readable", True) is not False
    return {
        "destination_organization": dest["organization"],
        "destination_service": dest["address"],
        "destination_capability_profile_id": PROFILE_ID,
        "destination_capability_address_form": ADDRESS_FORM,
        "destination_resolution_source": "ADVERTISED_CAPABILITY" if readable else "ADVERTISEMENT_NOT_READABLE",
        "destination_resolved_from_caller_argument": False,
        "destination_capability_declared_by_the_peer_directory": False,
        "peer_serves_this_capability_is_proven_here": False,
        "enumerated_in_federation_json": False,
        "advertisement_readable": readable,
    }


def _run(root: Path, ledger: Path, script: str, request: Mapping[str, Any]) -> dict[str, Any]:
    env = {key: value for key, value in os.environ.items() if key not in _LEDGER_ENV}
    env["STEGVERSE_REPO_LEDGER_ROOT"] = str(ledger / "repo")
    env["STEGVERSE_ORG_LEDGER_ROOT"] = str(ledger / "org")
    (ledger / "repo").mkdir(parents=True, exist_ok=True)
    (ledger / "org").mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, "-B", "-c", script], input=json.dumps(request),
        capture_output=True, text=True, cwd=root, env=env, timeout=180)
    parsed = None
    for line in reversed(completed.stdout.splitlines()):
        if line.startswith("{"):
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            break
    if not isinstance(parsed, dict):
        raise RuntimeError("org process produced no result rc=%s stderr=%s" % (
            completed.returncode, completed.stderr[-800:]))
    return parsed


def _walk_chain(head: Mapping[str, Any] | None, get) -> tuple[list[dict[str, Any]], list[str]]:
    """Walk HEAD backward. Findings name a broken contract; the chain is newest-last."""
    if not isinstance(head, dict) or not isinstance(head.get("receipt_sha256"), str):
        return [], ["LEDGER_HEAD_INVALID"]
    findings: list[str] = []
    chain: list[dict[str, Any]] = []
    cursor: str | None = head["receipt_sha256"]
    seen: set[str] = set()
    while cursor is not None:
        if cursor in seen:
            findings.append("LEDGER_CHAIN_CYCLE")
            break
        seen.add(cursor)
        receipt = get("receipts/" + cursor.split(":", 1)[1] + ".json")
        if not isinstance(receipt, dict):
            findings.append("LEDGER_CHAIN_MISSING_RECEIPT")
            break
        if receipt.get("receipt_sha256") != cursor or sha256(
                {key: value for key, value in receipt.items() if key != "receipt_sha256"}) != cursor:
            findings.append("RECEIPT_DOES_NOT_VERIFY_AGAINST_ITS_BODY")
            break
        chain.append(receipt)
        cursor = receipt.get("previous_receipt_sha256")
    chain.reverse()
    if chain and chain[0].get("previous_receipt_sha256") is not None and "LEDGER_CHAIN_CYCLE" not in findings:
        findings.append("LEDGER_CHAIN_DOES_NOT_BEGIN_AT_GENESIS")
    for earlier, later in zip(chain, chain[1:]):
        if later.get("previous_receipt_sha256") != earlier.get("receipt_sha256"):
            findings.append("LEDGER_CHAIN_LINK_BREAK")
            break
    if isinstance(head, dict) and chain and head.get("receipt_sha256") != chain[-1].get("receipt_sha256"):
        findings.append("LEDGER_HEAD_IS_NOT_THE_CHAIN_TIP")
    return chain, findings


def _posix_get(root: Path):
    def get(key: str) -> Any:
        path = root / key
        if not path.is_file():
            return None
        return _load_json(path)
    return get


def walk_posix(root: Path | str) -> dict[str, Any]:
    path = Path(root)
    head_path = path / "HEAD.json"
    if not head_path.is_file():
        return {"present": False, "reason": "LEDGER_HEAD_ABSENT", "location": str(path), "chain": [], "findings": []}
    head = _load_json(head_path)
    get = _posix_get(path)
    chain, findings = _walk_chain(head, get)
    receipt_dir = path / "receipts"
    if receipt_dir.is_dir():
        linked = {item["receipt_sha256"].split(":", 1)[1] + ".json" for item in chain}
        extras = sorted(item.name for item in receipt_dir.glob("*.json") if item.name not in linked)
        if extras:
            findings.append("ORPHAN_RECEIPT")
    sources = {}
    for receipt in chain:
        digest = receipt.get("source_transition_sha256")
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            continue
        source = get("source-receipts/" + digest.split(":", 1)[1] + ".json")
        sources[digest] = source
        if not isinstance(source, dict) or source.get("receipt_sha256") != digest or sha256(
                {key: value for key, value in source.items() if key != "receipt_sha256"}) != digest:
            findings.append("SOURCE_RECEIPT_NOT_RETAINED_OR_DOES_NOT_VERIFY")
    return {"present": True, "location": str(path), "chain": chain, "sources": sources,
            "findings": list(dict.fromkeys(findings)), "head_receipt_sha256": head.get("receipt_sha256")}


def _git(repo: Path, *args: str, stdin: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], input=stdin, capture_output=True, timeout=60)


def _git_blob(repo: Path, revision: str, key: str) -> Any:
    completed = _git(repo, "cat-file", "blob", revision + ":" + key)
    if completed.returncode != 0:
        return None
    try:
        return json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None


def resolve_ledger_ref(repository: Path, ref: str = LEDGER_REF, *, fetch: bool = False) -> str | None:
    """The commit a ledger ref names, or None when the organization has no such ref."""
    if not (repository / ".git").exists() and not (repository / "HEAD").is_file():
        return None
    if _git(repository, "rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode != 0 and fetch:
        _git(repository, "fetch", "--quiet", "origin", ref + ":" + ref)
    completed = _git(repository, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if completed.returncode != 0:
        return None
    return completed.stdout.decode().strip() or None


def walk_git(repository: Path | str, ref: str = LEDGER_REF, namespace: str | None = None, *,
             fetch: bool = False) -> dict[str, Any]:
    repo = Path(repository)
    revision = resolve_ledger_ref(repo, ref, fetch=fetch)
    location = "git+" + str(repo) + "#" + ref + ((":" + namespace) if namespace else "")
    if revision is None:
        return {"present": False, "reason": "LEDGER_REF_ABSENT", "location": location, "ref": ref, "chain": [], "findings": []}
    prefix = (namespace.rstrip("/") + "/") if namespace else ""
    head = _git_blob(repo, revision, prefix + "HEAD.json")
    if head is None:
        return {"present": False, "reason": "LEDGER_HEAD_ABSENT", "location": location, "ref": ref,
                "revision": revision, "chain": [], "findings": []}

    def get(key: str) -> Any:
        return _git_blob(repo, revision, prefix + key)

    chain, findings = _walk_chain(head, get)
    sources = {}
    for receipt in chain:
        digest = receipt.get("source_transition_sha256")
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            continue
        source = get("source-receipts/" + digest.split(":", 1)[1] + ".json")
        sources[digest] = source
        if not isinstance(source, dict) or sha256(
                {key: value for key, value in source.items() if key != "receipt_sha256"}) != digest:
            findings.append("SOURCE_RECEIPT_NOT_RETAINED_OR_DOES_NOT_VERIFY")
    return {"present": True, "location": location, "ref": ref, "revision": revision, "chain": chain,
            "sources": sources, "findings": list(dict.fromkeys(findings)),
            "head_receipt_sha256": head.get("receipt_sha256"),
            "introduced_at": ledger_introductions(repo, revision, prefix)}


def ledger_introductions(repo: Path, revision: str, prefix: str = "") -> dict[str, int]:
    """Receipt digest -> committer time (unix seconds) of the ledger commit that added it.

    Read from the ledger ref's own history. A shallow history names only what
    it holds; a receipt it cannot place is absent here and is not LEGACY.
    """
    completed = _git(repo, "log", "--reverse", "--diff-filter=A", "--format=@%ct", "--name-only",
                     revision, "--", prefix + "receipts/")
    if completed.returncode != 0:
        return {}
    found: dict[str, int] = {}
    stamp: int | None = None
    for line in completed.stdout.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("@"):
            try:
                stamp = int(line[1:])
            except ValueError:
                stamp = None
            continue
        if not line or stamp is None or not line.startswith(prefix + "receipts/") or not line.endswith(".json"):
            continue
        name = line[len(prefix + "receipts/"):-len(".json")]
        if "/" in name:
            continue
        found.setdefault("sha256:" + name, stamp)
    return found


def repository_namespace(root: Path) -> str | None:
    """The merged contract's repository-ledger subtree, when this checkout publishes one."""
    path = root / ".stegverse" / "transition-ledger" / "contract.json"
    if not path.is_file():
        return None
    try:
        contract = _load_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    namespace = ((contract.get("repository_ledger_location") or {}).get("namespace")
                 if isinstance(contract, dict) else None)
    return namespace if isinstance(namespace, str) and namespace else None


def _evidence(receipt: Mapping[str, Any]) -> dict[str, Any]:
    evidence = receipt.get("evidence")
    return evidence if isinstance(evidence, dict) else {}


def _by_class(chain: Sequence[Mapping[str, Any]], transition_class: str) -> list[Mapping[str, Any]]:
    return [receipt for receipt in chain if receipt.get("schema") == REPO_SCHEMA
            and receipt.get("transition_class") == transition_class]


def _duplicate_key(receipt: Mapping[str, Any]) -> bytes:
    return canon({key: receipt.get(key) for key in (
        "repository", "transition_id", "transition_class", "predecessor_state_sha256",
        "successor_state_sha256", "evidence", "authority_effect")})


def integrity_report(repo: Mapping[str, Any], org: Mapping[str, Any], *,
                     writer_introduction: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Hash chain and source retention for one organization's two ledger levels.

    ``findings`` fail the lane. ``reported`` are findings on LEGACY receipts
    (added to the ref before ``writer_introduction``), identical duplicates,
    and organization receipts that name no source receipt. Chain-shape
    findings always fail. Nothing is rewritten.
    """
    findings = list(repo.get("findings") or []) + list(org.get("findings") or [])
    reported: list[dict[str, Any]] = []
    if not repo.get("present"):
        findings.append("REPOSITORY_LEDGER_ABSENT")
    if not org.get("present"):
        findings.append("ORGANIZATION_LEDGER_ABSENT")
    cutoff = (writer_introduction or {}).get("committed_at_unix")
    cutoff = cutoff if isinstance(cutoff, int) else None
    introduced = {"repository": repo.get("introduced_at") or {}, "organization": org.get("introduced_at") or {}}

    def legacy(level: str, digest: Any) -> bool:
        stamp = introduced[level].get(digest) if isinstance(digest, str) else None
        return cutoff is not None and isinstance(stamp, int) and stamp < cutoff

    def note(finding: str, level: str, digests: Sequence[Any]) -> None:
        if digests and all(legacy(level, digest) for digest in digests):
            reported.append({"finding": finding, "classification": LEGACY, "level": level,
                             "receipt_sha256": list(digests)})
        else:
            findings.append(finding)

    repo_chain = repo.get("chain") or []
    org_chain = org.get("chain") or []
    groups: dict[Any, list[Mapping[str, Any]]] = {}
    for receipt in repo_chain:
        groups.setdefault(receipt.get("transition_id"), []).append(receipt)
    for transition_id, group in groups.items():
        if len(group) < 2:
            continue
        digests = [item.get("receipt_sha256") for item in group]
        if len({_duplicate_key(item) for item in group}) == 1:
            reported.append({"finding": "IDENTICAL_DUPLICATE_REPOSITORY_RECEIPT",
                             "classification": LEGACY if all(legacy("repository", d) for d in digests) else "REPORTED",
                             "level": "repository", "transition_id": transition_id, "receipt_sha256": digests})
        else:
            note("DUPLICATE_REPOSITORY_RECEIPT", "repository", digests)
    consumed: dict[str, int] = {}
    for receipt in org_chain:
        if receipt.get("schema") != ORG_SCHEMA:
            findings.append("ORGANIZATION_RECEIPT_SCHEMA")
            continue
        digest = receipt.get("repo_receipt_sha256")
        if not isinstance(digest, str):
            findings.append("ORGANIZATION_RECEIPT_DOES_NOT_NAME_A_REPOSITORY_RECEIPT")
            continue
        consumed[digest] = consumed.get(digest, 0) + 1
        match = next((item for item in repo_chain if item.get("receipt_sha256") == digest), None)
        if match is None:
            note("ORPHAN_ORGANIZATION_RECEIPT", "organization", [receipt.get("receipt_sha256")])
            continue
        named = receipt.get("source_transition_sha256")
        if named is None:
            # The repository receipt it names is on the chain; there is no
            # retained source copy to compare.
            reported.append({"finding": "ORGANIZATION_RECEIPT_NAMES_NO_SOURCE_RECEIPT",
                             "classification": "REPORTED", "level": "organization",
                             "receipt_sha256": [receipt.get("receipt_sha256")]})
            continue
        if (org.get("sources") or {}).get(named) != match:
            note("SOURCE_RECEIPT_DOES_NOT_MATCH_REPOSITORY_CHAIN", "organization", [receipt.get("receipt_sha256")])
    for receipt in repo_chain:
        if consumed.get(receipt.get("receipt_sha256"), 0) != 1:
            note("ORPHAN_REPOSITORY_RECEIPT", "repository", [receipt.get("receipt_sha256")])
    for receipt in repo_chain:
        reference = receipt.get("hb_reference") or {}
        if reference.get("derived_from_clock") is True:
            note("TIME_CONSTRAINT_DERIVED_FROM_CLOCK", "repository", [receipt.get("receipt_sha256")])
        if reference.get("authority_effect") not in (None, "NONE"):
            note("AUTHORITY_CONSTRAINT_IS_NOT_NONE", "repository", [receipt.get("receipt_sha256")])
    legacy_count = sum(1 for level, chain in (("repository", repo_chain), ("organization", org_chain))
                       for receipt in chain if legacy(level, receipt.get("receipt_sha256")))
    return {
        "findings": list(dict.fromkeys(findings)),
        "reported": reported,
        "writer_introduction": dict(writer_introduction) if writer_introduction else None,
        "legacy_receipt_count": legacy_count,
        "receipt_count": len(repo_chain) + len(org_chain),
    }


def integrity_findings(repo: Mapping[str, Any], org: Mapping[str, Any], *,
                       writer_introduction: Mapping[str, Any] | None = None) -> list[str]:
    """The failing part of ``integrity_report``."""
    return integrity_report(repo, org, writer_introduction=writer_introduction)["findings"]


def writer_marker(text: str | None) -> bool:
    """The writer takes ``hb_epoch`` as a dispatch input and runs the self-closure."""
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    takes_epoch = any(line.strip() == "hb_epoch:" for line in text.splitlines())
    return takes_epoch and ("self-clos" in lowered or "self_clos" in lowered)


def writer_introduction_local(root: Path | str, revision: str = "HEAD") -> dict[str, Any] | None:
    """Earliest commit on ``revision`` whose writer workflow carries ``writer_marker``."""
    repo = Path(root)
    listed = _git(repo, "log", "--reverse", "--format=%H %ct", revision, "--", WRITER_WORKFLOW)
    if listed.returncode != 0:
        return None
    for line in listed.stdout.decode("utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        shown = _git(repo, "show", parts[0] + ":" + WRITER_WORKFLOW)
        if shown.returncode == 0 and writer_marker(shown.stdout.decode("utf-8", errors="replace")):
            return {"commit": parts[0], "committed_at_unix": int(parts[1]), "source": "LOCAL_CHECKOUT_HISTORY"}
    return None


def _github_get(url: str, token: str | None, accept: str,
                getter: Callable[..., Any] | None = None) -> tuple[int | None, bytes]:
    headers = {"Accept": accept, "User-Agent": "stegverse-intr-hop-lane", "X-GitHub-Api-Version": "2022-11-28"}
    token = _blank_to_none(token)
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        response = (getter or http_get)(url, headers=headers, timeout=30)
    except HttpTransportError:
        return None, b""
    return getattr(response, "status_code", None), getattr(response, "content", b"") or b""


def _iso_to_unix(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    from datetime import datetime
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def writer_introduction_from_github(repository: str, *, token: str | None = None,
                                    getter: Callable[..., Any] | None = None,
                                    max_pages: int = 10) -> dict[str, Any] | None:
    """Earliest default-branch commit whose writer workflow carries ``writer_marker``.

    Lists the commits that touched the workflow, oldest first, and reads the
    file at each one until the marker appears. None when it never does or the
    history cannot be read.
    """
    commits: list[tuple[str, int]] = []
    for page in range(1, max_pages + 1):
        status, body = _github_get(
            GITHUB_API + "/repos/" + repository + "/commits?path=" + WRITER_WORKFLOW
            + "&per_page=100&page=" + str(page), token, "application/vnd.github+json", getter)
        if status != 200:
            return None
        try:
            listed = json.loads(body.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        if not isinstance(listed, list) or not listed:
            break
        for item in listed:
            sha = item.get("sha") if isinstance(item, dict) else None
            stamp = _iso_to_unix((((item.get("commit") or {}).get("committer") or {}).get("date"))
                                 if isinstance(item, dict) else None)
            if isinstance(sha, str) and stamp is not None:
                commits.append((sha, stamp))
        if len(listed) < 100:
            break
    for sha, stamp in reversed(commits):
        status, body = _github_get(
            GITHUB_API + "/repos/" + repository + "/contents/" + WRITER_WORKFLOW + "?ref=" + sha,
            token, "application/vnd.github.raw", getter)
        if status == 200 and writer_marker(body.decode("utf-8", errors="replace")):
            return {"commit": sha, "committed_at_unix": stamp, "source": "GITHUB_API_DEFAULT_BRANCH_HISTORY"}
    return None


def parse_writer_overrides(items: Sequence[str]) -> dict[str, dict[str, Any]]:
    """``ORGANIZATION=<unix seconds | ISO 8601>`` from the command line."""
    found: dict[str, dict[str, Any]] = {}
    for item in items:
        organization, separator, value = item.partition("=")
        if not separator or not organization or not value:
            raise ValueError("--writer-introduced expects ORGANIZATION=<unix seconds or ISO 8601>: " + item)
        stamp = int(value) if value.isdigit() else _iso_to_unix(value)
        if stamp is None:
            raise ValueError("--writer-introduced time is not readable: " + item)
        found[organization] = {"commit": None, "committed_at_unix": stamp, "source": "COMMAND_LINE_OVERRIDE"}
    return found


def hop_receipt_findings(hop: Mapping[str, Any], sender_repo: Sequence[Mapping[str, Any]],
                         sender_org: Sequence[Mapping[str, Any]], dest_repo: Sequence[Mapping[str, Any]],
                         dest_org: Sequence[Mapping[str, Any]]) -> list[str]:
    """Sender egress and destination ingress for one communication, read off the chains."""
    findings: list[str] = []
    packet_id = hop["packet_id"]
    communication_id = hop["communication_id"]
    destination = hop["destination_organization"]
    address = hop["destination_service"]
    emitted = [receipt for receipt in _by_class(sender_repo, EMITTED_CLASS)
               if _evidence(receipt).get("packet_id") == packet_id]
    closed = [receipt for receipt in _by_class(sender_repo, CLOSED_CLASS)
              if _evidence(receipt).get("communication_id") == communication_id]
    ingress = [receipt for receipt in _by_class(dest_repo, INGRESS_CLASS)
               if _evidence(receipt).get("communication_id") == communication_id]
    if len(emitted) != 1:
        findings.append("SENDER_EGRESS_RECEIPT_MISSING" if not emitted else "DUPLICATE_SENDER_EGRESS_RECEIPT")
    if len(closed) != 1:
        findings.append("SENDER_CLOSURE_RECEIPT_MISSING" if not closed else "DUPLICATE_SENDER_CLOSURE_RECEIPT")
    if len(ingress) != 1:
        findings.append("DESTINATION_INGRESS_RECEIPT_MISSING" if not ingress else "DUPLICATE_DESTINATION_INGRESS_RECEIPT")
    if findings:
        return findings
    emission, closure, arrived = emitted[0], closed[0], ingress[0]
    emission_evidence, closure_evidence, ingress_evidence = _evidence(emission), _evidence(closure), _evidence(arrived)
    if emission_evidence.get("destination_organization") != destination or emission_evidence.get("destination_service") != address:
        findings.append("EGRESS_DESTINATION_DOES_NOT_MATCH_THE_ADVERTISED_ADDRESS")
    if emission_evidence.get("payload_sha256") != hop.get("payload_sha256"):
        findings.append("EGRESS_PAYLOAD_DIGEST_DOES_NOT_MATCH_THE_MANIFESTED_PACKET")
    if closure_evidence.get("request_packet_id") != packet_id:
        findings.append("CLOSURE_DOES_NOT_NAME_THE_EMITTED_PACKET")
    if closure_evidence.get("communication_id") != communication_id or ingress_evidence.get("communication_id") != communication_id:
        findings.append("COMMUNICATION_ID_MISMATCH")
    if closure_evidence.get("response_message_class") != ACK_CLASS:
        findings.append("CLOSURE_IS_NOT_THE_RESPONDED_REQUEST_CLASS")
    if closure_evidence.get("destination_organization") != destination:
        findings.append("CLOSURE_DESTINATION_MISMATCH")
    if ingress_evidence.get("profile_id") != PROFILE_ID or ingress_evidence.get("disposition") != "ALLOW":
        findings.append("DESTINATION_INGRESS_IS_NOT_AN_ACKNOWLEDGED_DIAGNOSTIC")
    if closure_evidence.get("disposition") != "ALLOW":
        findings.append("CLOSURE_DISPOSITION_IS_NOT_ALLOW")
    for receipt, chain in ((emission, sender_org), (closure, sender_org), (arrived, dest_org)):
        digest = receipt["receipt_sha256"]
        holders = [item for item in chain if item.get("repo_receipt_sha256") == digest]
        if len(holders) != 1:
            findings.append("ORGANIZATION_RECEIPT_MISSING" if not holders else "DUPLICATE_ORGANIZATION_RECEIPT")
    reference = emission.get("hb_reference") or {}
    if hop.get("hb_epoch") is not None and reference.get("epoch") != hop["hb_epoch"]:
        findings.append("TIME_CONSTRAINT_NOT_THE_SUPPLIED_EPOCH")
    if reference.get("derived_from_clock") is True:
        findings.append("TIME_CONSTRAINT_DERIVED_FROM_CLOCK")
    return list(dict.fromkeys(findings))


def non_allow_fields(failure_code: str, failed_predicate: str, required_evidence_or_repair: str,
                     retry_entrypoint: str, next_attempt: str) -> dict[str, Any]:
    """The six fields every non-ALLOW outcome carries."""
    return {
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": required_evidence_or_repair,
        "retry_entrypoint": retry_entrypoint,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": next_attempt,
    }


def durable_queue_fields() -> dict[str, Any]:
    """An unavailable or not-yet-run receiver is the protocol's own disposition, not a blocker."""
    return {
        "always_on_receiver_required": False,
        "receiver_wait": False,
        **non_allow_fields(
            DURABLE_QUEUE, "DESTINATION_ARRIVED_AND_SENDER_CLOSED_RECEIPTS_IN_THE_READ_LEDGERS",
            "none from a receiver: the destination receive and sender close materialize from the dispatched "
            "events and are observed only as organization-ledger receipts",
            LANE_WORKFLOW + " mode=live (readback)",
            "the next readback evaluates the receipts present then; nothing waits or polls"),
    }


def hop_outcome_fields(status: str, findings: Sequence[str], unreachable: Mapping[str, Any] | None,
                       mode: str) -> dict[str, Any]:
    """Six fields for a non-ALLOW hop status; the durable-queue fields for an open hop."""
    if status == "UNREACHABLE":
        reasons = ", ".join("%s: %s" % (side, reason) for side, reason in sorted((unreachable or {}).items()) if reason)
        return non_allow_fields(
            "INTR_HOP_ADVERTISEMENT_OR_LEDGER_REF_UNREADABLE",
            "SENDER_AND_DESTINATION_ADVERTISEMENT_AND_LEDGER_REF_ARE_READABLE",
            "a readable <org>/.github advertisement and " + LEDGER_REF + " for each side (" + (reasons or "unread") + ")",
            LANE_WORKFLOW + " mode=" + mode,
            "read again once the read credential reaches the organization; the hop stays in the matrix")
    if status == "FAIL":
        listed = list(findings) or ["HOP_RECEIPT_FINDINGS"]
        if listed == [NOT_SENT_FINDING]:
            return non_allow_fields(
                "INTR_HOP_NOT_SENT_IN_READ_LEDGERS", NOT_SENT_FINDING,
                "a send transition for this ordered pair; no emission, arrival or closure is in the read ledgers",
                LANE_WORKFLOW + " mode=orchestrate",
                "orchestrate dispatches the send transition at a supplied hb_epoch; the next readback evaluates it")
        return non_allow_fields(
            "INTR_HOP_RECEIPT_FINDINGS", ",".join(listed),
            "sender and destination ledger receipts that clear: " + ", ".join(listed),
            LANE_WORKFLOW + " mode=" + mode,
            "repair the named receipts or ledger writer, then read again; LEGACY receipts are reported, not failing")
    if status == DURABLE_QUEUE:
        return durable_queue_fields()
    return {}


def pair_ledger_state(sender_repo: Sequence[Mapping[str, Any]], destination_organization: str, address: str) -> str:
    """``OPEN``, ``CLOSED``, ``REFUSED`` or ``UNSENT`` for one ordered pair, read off the sender's chain.

    ``OPEN`` is an emission to the destination's address whose packet has no
    closure or refused closure yet. It is a state of the hop, not a blocker.
    """
    terminal: dict[str, str] = {}
    for receipt in sender_repo:
        klass = receipt.get("transition_class")
        if klass not in (CLOSED_CLASS, CLOSURE_REFUSED_CLASS):
            continue
        evidence = _evidence(receipt)
        if evidence.get("destination_organization") != destination_organization:
            continue
        packet = evidence.get("request_packet_id")
        if isinstance(packet, str):
            terminal[packet] = klass
    emitted = [_evidence(receipt).get("packet_id") for receipt in _by_class(sender_repo, EMITTED_CLASS)
               if _evidence(receipt).get("destination_service") == address]
    if any(packet not in terminal for packet in emitted):
        return "OPEN"
    if CLOSED_CLASS in terminal.values():
        return "CLOSED"
    if CLOSURE_REFUSED_CLASS in terminal.values():
        return "REFUSED"
    return "UNSENT"


def _status(findings: Sequence[str], *, unreachable: str | None = None) -> str:
    if unreachable:
        return "UNREACHABLE"
    return "FAIL" if findings else "PASS"


def run_fabricated(peers: Sequence[Mapping[str, Any]], *, mesh_root: Path, ledger_home: Path,
                   epoch_origin: int = EPOCH_ORIGIN, reference_root: Path | str | None = None) -> dict[str, Any]:
    """Exercise every ordered pair against temporary roots and read the receipts back.

    Each peer's checkout is the advertisement. The hop itself runs on a temp
    copy of the merged organization contract with that peer's identity stamped
    on it, so an in-flight ledger writer is not imported.
    """
    reference = reference_root_for(peers, reference_root)
    mesh_root.mkdir(parents=True, exist_ok=True)
    runtimes = {peer["slug"]: materialize_reference(reference, peer, ledger_home / "runtimes" / peer["slug"])
                for peer in peers}
    standing = {"mode": "ESTABLISH_GENESIS", "node_ref": "intr-destination-hop-lane", "predecessor": None}
    hops: list[dict[str, Any]] = []
    by_sender: dict[str, list[dict[str, Any]]] = {}
    for index, (sender, dest) in enumerate(ordered_pairs(peers)):
        epoch = epoch_origin + index * 4
        communication_id = "intr-hop:" + sender["slug"] + ":" + dest["slug"]
        packet_id = "intr-hop-packet:" + sender["slug"] + ":" + dest["slug"]
        payload = manifested_payload(sender, dest, communication_id)
        hop = {
            "sender_organization": sender["organization"],
            "sender_slug": sender["slug"],
            "destination_organization": dest["organization"],
            "destination_slug": dest["slug"],
            "destination_service": dest["address"],
            "communication_id": communication_id,
            "packet_id": packet_id,
            "request_class": REQUEST_CLASS,
            "responded_request_class": REQUEST_CLASS,
            "acknowledgement_class": ACK_CLASS,
            "payload_sha256": sha256(payload),
            "manifest_sha256": payload["body"]["manifest_sha256"],
            "hb_epoch": epoch,
            "time_constraint": TIME_CONSTRAINT,
            "authority_constraint": AUTHORITY_CONSTRAINT,
            "payload": payload,
            "resolved": destination_resolution(dest),
            "origin_service": sender["address"],
        }
        hops.append(hop)
        by_sender.setdefault(sender["slug"], []).append(hop)

    writer_by_id: dict[str, dict[str, Any]] = {}
    for sender in peers:
        batch = by_sender.get(sender["slug"]) or []
        if not batch:
            continue
        request = {"root": str(runtimes[sender["slug"]]), "mesh": str(mesh_root), "hops": [{
            "payload": hop["payload"], "resolved": hop["resolved"], "epoch": hop["hb_epoch"],
            "origin": hop["sender_organization"], "origin_service": hop["origin_service"],
            "packet_id": hop["packet_id"], "standing": standing,
        } for hop in batch]}
        try:
            answer = _run(runtimes[sender["slug"]], ledger_home / sender["slug"], _SENDER, request)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            answer = {"ok": False, "reason": str(exc)[:800], "stage": "sender-process"}
        if not answer.get("ok"):
            for hop in batch:
                writer_by_id[hop["communication_id"]] = {"sender_ok": False, "sender_reason": answer.get("reason") or answer.get("type")}
            continue
        for item in answer.get("hops") or []:
            writer_by_id[item.get("communication_id")] = {"sender": item, "sender_ok": bool(item.get("ok"))}

    by_dest: dict[str, list[dict[str, Any]]] = {}
    for hop in hops:
        by_dest.setdefault(hop["destination_slug"], []).append(hop)
    for dest in peers:
        batch = by_dest.get(dest["slug"]) or []
        if not batch:
            continue
        request = {"root": str(runtimes[dest["slug"]]), "hops": [{
            "payload": hop["payload"], "packet_id": hop["packet_id"], "epoch": hop["hb_epoch"] + 3,
        } for hop in batch]}
        try:
            answer = _run(runtimes[dest["slug"]], ledger_home / dest["slug"], _DESTINATION, request)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            answer = {"ok": False, "reason": str(exc)[:800]}
        if not answer.get("ok"):
            for hop in batch:
                writer_by_id.setdefault(hop["communication_id"], {})["destination_ok"] = False
                writer_by_id[hop["communication_id"]]["destination_reason"] = answer.get("reason")
            continue
        for item in answer.get("hops") or []:
            slot = writer_by_id.setdefault(item.get("communication_id"), {})
            slot["destination"] = item
            slot["destination_ok"] = bool(item.get("ok")) and item.get("disposition") == "ALLOW"

    views = {}
    integrity = {}
    for peer in peers:
        repo = walk_posix(ledger_home / peer["slug"] / "repo")
        org = walk_posix(ledger_home / peer["slug"] / "org")
        views[peer["slug"]] = (repo, org)
        integrity[peer["slug"]] = integrity_findings(repo, org)

    rendered = []
    for hop in hops:
        sender_repo, sender_org = views[hop["sender_slug"]]
        dest_repo, dest_org = views[hop["destination_slug"]]
        findings = list(integrity[hop["sender_slug"]]) + list(integrity[hop["destination_slug"]])
        findings.extend(hop_receipt_findings(
            hop, sender_repo.get("chain") or [], sender_org.get("chain") or [],
            dest_repo.get("chain") or [], dest_org.get("chain") or []))
        writer = writer_by_id.get(hop["communication_id"]) or {}
        sender_writer = writer.get("sender") or {}
        if sender_writer.get("closure_disposition") not in (None, "ALLOW") or sender_writer.get("closure_findings"):
            findings.append("FABRICATED_CLOSURE_DID_NOT_RECOMPUTE")
        if writer.get("sender_ok") is False:
            findings.append("SENDER_EGRESS_DID_NOT_RECORD")
        if writer.get("destination_ok") is False:
            findings.append("DESTINATION_INGRESS_DID_NOT_ACKNOWLEDGE")
        findings = list(dict.fromkeys(findings))
        rendered.append(_public_hop(hop, status=_status(findings), findings=findings, writer=writer,
                                    sender_ledger=sender_org, destination_ledger=dest_org, mode="fabricated"))
    report = _report(peers, rendered, mode="fabricated", mesh_root=mesh_root, ledger_home=ledger_home)
    report["execution_runtime"] = {
        "role": "MERGED_REFERENCE_CONTRACT_IDENTITY_STAMPED_PER_PEER",
        "reference_repository": REFERENCE_REPOSITORY,
        "reference_root": str(reference),
        "peer_checkout_role": "ADVERTISEMENT_ONLY",
        "peer_ledger_writer_used": False,
    }
    return report


def _correlated_live(sender_repo: Sequence[Mapping[str, Any]], dest_repo: Sequence[Mapping[str, Any]],
                     destination_organization: str, address: str) -> tuple[list[str], list[str]]:
    """Communication ids read from both ledgers that close as this ordered pair."""
    findings: list[str] = []
    matched: list[str] = []
    closures = _by_class(sender_repo, CLOSED_CLASS)
    by_id: dict[str, list[Mapping[str, Any]]] = {}
    for receipt in closures:
        evidence = _evidence(receipt)
        if evidence.get("destination_organization") != destination_organization:
            continue
        if evidence.get("response_message_class") != ACK_CLASS:
            continue
        identifier = evidence.get("communication_id")
        if not isinstance(identifier, str) or not identifier:
            findings.append("CLOSURE_WITHOUT_COMMUNICATION_ID")
            continue
        by_id.setdefault(identifier, []).append(receipt)
    for identifier, group in by_id.items():
        if len(group) != 1:
            findings.append("DUPLICATE_SENDER_CLOSURE_RECEIPT")
            continue
        closure = group[0]
        packet_id = _evidence(closure).get("request_packet_id")
        emitted = [receipt for receipt in _by_class(sender_repo, EMITTED_CLASS)
                   if _evidence(receipt).get("packet_id") == packet_id
                   and _evidence(receipt).get("destination_service") == address]
        arrived = [receipt for receipt in _by_class(dest_repo, INGRESS_CLASS)
                   if _evidence(receipt).get("communication_id") == identifier
                   and _evidence(receipt).get("profile_id") == PROFILE_ID
                   and _evidence(receipt).get("disposition") == "ALLOW"]
        if len(emitted) == 1 and len(arrived) == 1 and _evidence(closure).get("disposition") == "ALLOW":
            matched.append(identifier)
        elif emitted or arrived:
            findings.append("CORRELATED_RECEIPTS_DO_NOT_MATCH")
    if not matched and "DUPLICATE_SENDER_CLOSURE_RECEIPT" not in findings and "CORRELATED_RECEIPTS_DO_NOT_MATCH" not in findings:
        findings.append("CORRELATED_RECEIPTS_NOT_IN_THE_READ_LEDGERS")
    return matched, findings


def _absent_ledger(reason: str, location: str | None = None) -> dict[str, Any]:
    return {"present": False, "reason": reason, "location": location, "chain": [], "findings": [], "sources": {}}


def run_live(peers: Sequence[Mapping[str, Any]], *, fetch: bool = False, token: str | None = None,
            ledger_cache: Path | None = None,
            writer_introduction: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
            ) -> dict[str, Any]:
    """Read each peer's organization-ledger ref. Do not append.

    A peer whose advertisement was not read is UNREACHABLE and its ledger is
    not fetched. A readable peer with no local checkout is read from
    ``refs/stegverse/organization-ledger`` on ``https://github.com/<repo>``
    when ``fetch`` is set. A ref that cannot be read is UNREACHABLE.

    ``writer_introduction(peer)`` names when the peer's supplied-epoch writer
    reached its default branch. Receipts added to the ref before it are
    LEGACY: reported, not failing. Without it nothing is LEGACY.
    """
    token = _blank_to_none(token)
    views = {}
    unreachable: dict[str, str] = {}
    integrity: dict[str, list[str]] = {}
    ledger_integrity: dict[str, dict[str, Any]] = {}
    owned_cache: tempfile.TemporaryDirectory | None = None
    try:
        for peer in peers:
            slug = peer["slug"]
            if peer.get("advertisement_readable", True) is False:
                reason = peer.get("unreadable_reason") or "ADVERTISEMENT_NOT_READABLE"
                unreachable[slug] = reason
                views[slug] = (_absent_ledger(reason), _absent_ledger(reason))
                integrity[slug] = []
                continue
            root = Path(peer["root"]) if peer.get("root") else None
            remote_repository = None
            if root is None and fetch:
                if ledger_cache is None and owned_cache is None:
                    owned_cache = tempfile.TemporaryDirectory(prefix="intr-hop-ledger-")
                    ledger_cache = Path(owned_cache.name)
                repository = peer.get("repository") or (peer["organization"] + "/.github")
                fetch_reason = materialize_remote_ledger(repository, ledger_cache / slug, token)
                if fetch_reason:
                    unreachable[slug] = fetch_reason
                    views[slug] = (_absent_ledger(fetch_reason), _absent_ledger(fetch_reason))
                    integrity[slug] = []
                    continue
                root = ledger_cache / slug
                remote_repository = repository
            if root is None:
                reason = "LEDGER_CHECKOUT_ABSENT"
                unreachable[slug] = reason
                views[slug] = (_absent_ledger(reason), _absent_ledger(reason))
                integrity[slug] = []
                continue
            org = walk_git(root, LEDGER_REF, fetch=fetch and remote_repository is None)
            namespace = peer.get("repository_namespace") or repository_namespace(root)
            repo = walk_git(root, LEDGER_REF, namespace, fetch=False) if namespace and org.get("present") else {
                "present": False, "reason": "REPOSITORY_LEDGER_NAMESPACE_ABSENT" if org.get("present") else org.get("reason"),
                "chain": [], "findings": [], "location": org.get("location"),
            }
            if remote_repository:
                base = "git+https://github.com/" + remote_repository + "#" + LEDGER_REF
                org["location"] = base
                repo["location"] = base + ((":" + namespace) if namespace else "")
            views[slug] = (repo, org)
            if not org.get("present"):
                unreachable[slug] = org.get("reason") or "LEDGER_REF_ABSENT"
                integrity[slug] = []
            elif not repo.get("present"):
                integrity[slug] = ["REPOSITORY_LEDGER_CHAIN_ABSENT"]
            else:
                introduced = writer_introduction(peer) if writer_introduction else None
                detail = integrity_report(repo, org, writer_introduction=introduced)
                integrity[slug] = detail["findings"]
                ledger_integrity[slug] = {"organization": peer["organization"], **detail}
    finally:
        if owned_cache is not None:
            owned_cache.cleanup()

    rendered = []
    for sender, dest in ordered_pairs(peers):
        communication_id = "intr-hop:" + sender["slug"] + ":" + dest["slug"]
        hop = {
            "sender_organization": sender["organization"], "sender_slug": sender["slug"],
            "destination_organization": dest["organization"], "destination_slug": dest["slug"],
            "destination_service": dest["address"], "communication_id": communication_id,
            "packet_id": None, "request_class": REQUEST_CLASS, "responded_request_class": REQUEST_CLASS,
            "acknowledgement_class": ACK_CLASS, "payload_sha256": None, "manifest_sha256": None,
            "hb_epoch": None, "time_constraint": TIME_CONSTRAINT, "authority_constraint": AUTHORITY_CONSTRAINT,
            "payload": None, "resolved": destination_resolution(dest), "origin_service": sender["address"],
        }
        sender_reason = unreachable.get(sender["slug"])
        dest_reason = unreachable.get(dest["slug"])
        sender_repo, sender_org = views[sender["slug"]]
        dest_repo, dest_org = views[dest["slug"]]
        if sender_reason or dest_reason:
            reason = {"sender": sender_reason, "destination": dest_reason}
            public = _public_hop(
                hop, status="UNREACHABLE", findings=[], writer={}, sender_ledger=sender_org,
                destination_ledger=dest_org, mode="live", unreachable=reason)
            public["ledger_state"] = "UNREACHABLE"
            rendered.append(public)
            continue
        state = pair_ledger_state(sender_repo.get("chain") or [], dest["organization"], dest["address"])
        findings = list(integrity[sender["slug"]]) + list(integrity[dest["slug"]])
        matched, correlation = _correlated_live(
            sender_repo.get("chain") or [], dest_repo.get("chain") or [], dest["organization"], dest["address"])
        findings.extend(correlation)
        # Organization receipts must still hold each correlated repository receipt.
        for identifier in matched:
            synthetic = {
                **hop, "communication_id": identifier, "packet_id": _request_packet(sender_repo.get("chain") or [], identifier),
                "payload_sha256": _payload_sha(sender_repo.get("chain") or [], identifier), "hb_epoch": None,
            }
            findings.extend(item for item in hop_receipt_findings(
                synthetic, sender_repo.get("chain") or [], sender_org.get("chain") or [],
                dest_repo.get("chain") or [], dest_org.get("chain") or [])
                if item != "TIME_CONSTRAINT_NOT_THE_SUPPLIED_EPOCH")
        findings = list(dict.fromkeys(findings))
        status = _status(findings)
        if not matched and state == "OPEN" and findings == [NOT_SENT_FINDING]:
            # Sent and not yet closed. The receiver materializes from the
            # dispatched event; its absence here is not a failure.
            status, findings = DURABLE_QUEUE, []
        public = _public_hop(hop, status=status, findings=findings, writer={},
                             sender_ledger=sender_org, destination_ledger=dest_org, mode="live")
        public["ledger_state"] = state
        public["communication_ids_read_back"] = matched
        rendered.append(public)
    report = _report(peers, rendered, mode="live")
    report["ledger_integrity"] = ledger_integrity
    return report


def hop_waves(peers: Sequence[Mapping[str, Any]]) -> list[list[tuple[Mapping[str, Any], Mapping[str, Any]]]]:
    """Every ordered pair, in waves where no organization appears twice.

    Round-robin (circle) pairing: ``n - 1`` rounds of ``n // 2`` disjoint
    pairs, each round run once forward and once reversed. Eight peers give
    14 waves of 4 hops. An odd peer count leaves one organization idle per
    wave.
    """
    ordered = sorted(peers, key=lambda peer: peer["slug"])
    slots: list[Mapping[str, Any] | None] = list(ordered)
    if len(slots) % 2:
        slots.append(None)
    count = len(slots)
    waves: list[list[tuple[Mapping[str, Any], Mapping[str, Any]]]] = []
    for _round in range(max(count - 1, 0)):
        pairs = [(slots[index], slots[count - 1 - index]) for index in range(count // 2)]
        pairs = [(left, right) for left, right in pairs if left is not None and right is not None]
        waves.append([(left, right) for left, right in pairs])
        waves.append([(right, left) for left, right in pairs])
        slots = [slots[0], slots[-1], *slots[1:-1]]
    return [wave for wave in waves if wave]


HB_EPOCH_FAILURE_CODE = "DISPATCH_HB_EPOCH_INVALID"
HB_EPOCH_PREDICATE = "HB_EPOCH_IS_SUPPLIED_AS_A_NON_NEGATIVE_INTEGER"


def parse_hb_epoch(value: Any) -> int | None:
    """``hb_epoch`` in the form the org hop workflow and the ledger writer take it.

    Both take a ``workflow_dispatch`` string input named ``hb_epoch`` and accept
    ASCII decimal digits only (a non-negative integer). A non-negative ``int``
    is the same value. Anything else (absent, blank, signed, spaced, ``1e3``,
    ``1_000``, non-ASCII digits, bool) is malformed and returns ``None``.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and value and value.isascii() and value.isdigit():
        return int(value)
    return None


def hb_epoch_fail_closed(value: Any) -> dict[str, Any]:
    """The orchestrate transition when ``hb_epoch`` is missing or malformed. Nothing is dispatched."""
    missing = value is None or (isinstance(value, str) and not value.strip())
    finding = "MISSING" if missing else "MALFORMED"
    return {
        "disposition": "FAIL_CLOSED", "hb_epoch_finding": finding,
        "supplied_hb_epoch": None if value is None else repr(value),
        **non_allow_fields(
            HB_EPOCH_FAILURE_CODE, HB_EPOCH_PREDICATE,
            "a supplied hb_epoch of ASCII decimal digits (a non-negative integer); the org hop workflow and "
            "the organization-ledger writer take it as the workflow_dispatch input hb_epoch (hb_epoch was "
            + finding.lower() + ")",
            LANE_WORKFLOW + " mode=orchestrate",
            "re-dispatch mode=orchestrate with a supplied hb_epoch"),
        "consequence_committed": False, "dispatched": 0, "hops": [], "outcomes": {},
        "hb_epoch": None, "time_constraint": TIME_CONSTRAINT, "receiver_wait": False,
        "always_on_receiver_required": False,
    }


def hop_communication_id(sender: Mapping[str, Any], dest: Mapping[str, Any], epoch: int) -> str:
    return "intr-hop:%s:%s:%d" % (sender["slug"], dest["slug"], epoch)


def dispatch_send_hop(sender: Mapping[str, Any], dest: Mapping[str, Any], *, communication_id: str,
                      hb_epoch: int, token: str, ref: str = "main",
                      poster: Callable[..., Any] | None = None) -> tuple[bool, str]:
    """Dispatch ``phase=send`` of the sender's hop workflow. The token is a header only."""
    epoch = parse_hb_epoch(hb_epoch)
    if epoch is None:
        return False, "HB_EPOCH_INVALID"
    repository = sender.get("repository") or (sender["organization"] + "/.github")
    url = GITHUB_API + "/repos/" + repository + "/actions/workflows/" + HOP_WORKFLOW + "/dispatches"
    body = {"ref": ref, "inputs": {
        "phase": "send", "destination_slug": dest["slug"], "communication_id": communication_id,
        "hb_epoch": str(epoch), "forward": "true",
    }}
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "stegverse-intr-hop-lane",
               "X-GitHub-Api-Version": "2022-11-28", "Authorization": "Bearer " + token}
    try:
        response = (poster or http_post)(url, json=body, headers=headers, timeout=30)
    except HttpTransportError:
        return False, "DISPATCH_TRANSPORT"
    status = getattr(response, "status_code", None)
    return (status == 204, "DISPATCHED" if status == 204 else "DISPATCH_HTTP_%s" % status)


def run_orchestrate(peers: Sequence[Mapping[str, Any]], *, hb_epoch: int, token: str,
                    ledger_state: Mapping[tuple[str, str], str] | None = None,
                    dispatcher: Callable[..., tuple[bool, str]] | None = None) -> dict[str, Any]:
    """Record one manifest-directed disposition per ordered pair. Never wait.

    ``ledger_state[(sender_slug, destination_slug)]`` is what the readback
    found (``pair_ledger_state``); a pair it does not name is ``UNSENT``. An
    ``UNSENT`` pair whose organizations hold no open hop, and are not already
    in a hop dispatched by this transition, is dispatched at the supplied
    ``hb_epoch``. A dispatched or ``OPEN`` hop is ``DURABLE_QUEUE``; the
    readback that follows a later transition evaluates whatever receipts exist
    then. A peer whose advertisement was not read is not dispatched; its hops
    are ``UNREACHABLE``.

    A missing or malformed ``hb_epoch`` resolves the whole transition to
    ``FAIL_CLOSED`` with the six fields, and nothing is dispatched.
    """
    epoch = parse_hb_epoch(hb_epoch)
    if epoch is None:
        return hb_epoch_fail_closed(hb_epoch)
    hb_epoch = epoch
    token = _blank_to_none(token)
    if token is None:
        raise ValueError(FEDERATION_HOP_TOKEN_ENV + " is required to dispatch hops")
    send = dispatcher or (lambda sender, dest, **kw: dispatch_send_hop(sender, dest, token=token, **kw))
    states = dict(ledger_state or {})
    readable = [peer for peer in peers if peer.get("advertisement_readable", True) is not False]
    unread = sorted(peer["slug"] for peer in peers if peer.get("advertisement_readable", True) is False)
    busy = {slug for (sender, dest), state in states.items() if state == "OPEN" for slug in (sender, dest)}
    order = [pair for wave in hop_waves(readable) for pair in wave]
    order += [(sender, dest) for sender, dest in ordered_pairs(peers)
              if sender["slug"] in unread or dest["slug"] in unread]
    hops: list[dict[str, Any]] = []
    outcomes: dict[str, int] = {}
    dispatched = 0
    retry = ".github/workflows/intr-destination-hop.yml phase=send"
    for sender, dest in order:
        pair = (sender["slug"], dest["slug"])
        state = "UNREACHABLE" if (pair[0] in unread or pair[1] in unread) else states.get(pair, "UNSENT")
        hop: dict[str, Any] = {"sender_slug": pair[0], "destination_slug": pair[1], "ledger_state": state,
                               "hb_epoch": None, "communication_id": None, "dispatch": None}
        if state == "UNREACHABLE":
            hop["outcome"] = "UNREACHABLE"
            hop.update(non_allow_fields(
                "INTR_HOP_ADVERTISEMENT_UNREADABLE", "SENDER_AND_DESTINATION_ADVERTISEMENTS_ARE_READABLE",
                "a readable <org>/.github advertisement for: " + ", ".join(slug for slug in pair if slug in unread),
                LANE_WORKFLOW + " mode=orchestrate",
                "the next orchestrate transition dispatches it once the advertisement is read"))
        elif state == "CLOSED":
            hop["outcome"] = "CLOSED_IN_READ_LEDGERS"
        elif state == "OPEN":
            hop["outcome"] = DURABLE_QUEUE
            hop.update(durable_queue_fields())
        elif state == "REFUSED":
            hop["outcome"] = "CLOSURE_REFUSED"
            hop.update(non_allow_fields(
                "INTR_HOP_CLOSURE_REFUSED_IN_SENDER_LEDGER", "SENDER_CLOSURE_VERIFIES_THE_DESTINATION_ACKNOWLEDGEMENT",
                "the refused closure's findings repaired at the sender or destination; the refusal stays recorded",
                retry + " at " + (sender.get("repository") or sender["organization"] + "/.github"),
                "an owner-directed send with a new communication_id; orchestrate does not repeat a recorded refusal"))
        elif pair[0] in busy or pair[1] in busy:
            hop["outcome"] = "DEFERRED_ORGANIZATION_LEDGER_CONCURRENCY"
            hop.update(non_allow_fields(
                "ORGANIZATION_LEDGER_CONCURRENCY_GROUP_OCCUPIED",
                "SENDER_AND_DESTINATION_HOLD_NO_OPEN_OR_DISPATCHED_HOP",
                "no open hop at " + pair[0] + " or " + pair[1] + " in the read ledgers and none dispatched by this transition",
                LANE_WORKFLOW + " mode=orchestrate",
                "the next orchestrate transition, at a later supplied hb_epoch, selects it from ledger state"))
        else:
            communication_id = hop_communication_id(sender, dest, hb_epoch)
            ok, detail = send(sender, dest, communication_id=communication_id, hb_epoch=hb_epoch)
            hop.update(hb_epoch=hb_epoch, communication_id=communication_id, dispatch=detail)
            if ok:
                dispatched += 1
                busy.update(pair)
                hop["outcome"] = DURABLE_QUEUE
                hop["send_transition_disposition"] = "ALLOW"
                hop.update(durable_queue_fields())
            else:
                hop["outcome"] = "NOT_DISPATCHED"
                hop.update(non_allow_fields(
                    "INTR_HOP_SEND_DISPATCH_" + detail, "SEND_PHASE_DISPATCH_ACCEPTED",
                    "an accepted workflow_dispatch of " + HOP_WORKFLOW + " phase=send at "
                    + (sender.get("repository") or sender["organization"] + "/.github") + " (" + detail + ")",
                    retry, "the next orchestrate transition dispatches it again at a later supplied hb_epoch"))
        outcomes[hop["outcome"]] = outcomes.get(hop["outcome"], 0) + 1
        hops.append(hop)
    return {"hops": hops, "dispatched": dispatched, "outcomes": outcomes,
            "not_dispatched_unread_advertisement": unread, "hb_epoch": hb_epoch,
            "time_constraint": TIME_CONSTRAINT, "receiver_wait": False,
            "always_on_receiver_required": False, "ledger_state_source": "LIVE_READBACK_BEFORE_DISPATCH"}


def _request_packet(chain: Sequence[Mapping[str, Any]], communication_id: str) -> str | None:
    for receipt in _by_class(chain, CLOSED_CLASS):
        if _evidence(receipt).get("communication_id") == communication_id:
            return _evidence(receipt).get("request_packet_id")
    return None


def _payload_sha(chain: Sequence[Mapping[str, Any]], communication_id: str) -> str | None:
    packet_id = _request_packet(chain, communication_id)
    for receipt in _by_class(chain, EMITTED_CLASS):
        if _evidence(receipt).get("packet_id") == packet_id:
            return _evidence(receipt).get("payload_sha256")
    return None


def _public_hop(hop: Mapping[str, Any], *, status: str, findings: Sequence[str], writer: Mapping[str, Any],
                sender_ledger: Mapping[str, Any], destination_ledger: Mapping[str, Any], mode: str,
                unreachable: Mapping[str, Any] | None = None) -> dict[str, Any]:
    sender_writer = writer.get("sender") or {}
    dest_writer = writer.get("destination") or {}
    authentic = mode == "live" and status == "PASS"
    return {
        "sender": hop["sender_organization"],
        "destination": hop["destination_organization"],
        "sender_slug": hop["sender_slug"],
        "destination_slug": hop["destination_slug"],
        "destination_service": hop["destination_service"],
        "resolution_source": (hop.get("resolved") or {}).get("destination_resolution_source") or "ADVERTISED_CAPABILITY",
        "communication_id": hop["communication_id"],
        "packet_id": hop["packet_id"],
        "closure": {
            "responded_request_class": REQUEST_CLASS,
            "acknowledgement_class": ACK_CLASS,
            "communication_id": hop["communication_id"],
        },
        "manifest_sha256": hop.get("manifest_sha256"),
        "payload_sha256": hop.get("payload_sha256"),
        "hb_epoch": hop.get("hb_epoch"),
        "time_constraint": TIME_CONSTRAINT,
        "authority_constraint": AUTHORITY_CONSTRAINT,
        "disposition_role": "TRANSITION_EVIDENCE_ONLY",
        "status": status,
        "findings": list(findings),
        "unreachable": unreachable,
        "sender_ledger_ref": sender_ledger.get("location"),
        "sender_ledger_head": sender_ledger.get("head_receipt_sha256"),
        "destination_ledger_ref": destination_ledger.get("location"),
        "destination_ledger_head": destination_ledger.get("head_receipt_sha256"),
        "sender_egress_repository_receipt_sha256": sender_writer.get("emission_repository_receipt_sha256"),
        "sender_closure_repository_receipt_sha256": sender_writer.get("closure_repository_receipt_sha256"),
        "destination_ingress_repository_receipt_sha256": dest_writer.get("repository_receipt_sha256"),
        "destination_ingress_organization_receipt_sha256": dest_writer.get("organization_receipt_sha256"),
        "far_side": FAR_SIDE if mode == "fabricated" else None,
        "far_side_authentic": False if mode == "fabricated" else None,
        "evidence_class": EVIDENCE_FABRICATED if mode == "fabricated" else EVIDENCE_LIVE,
        "authenticity_claimed": authentic,
        "authenticity_basis": (destination_ledger.get("location") if authentic else None),
        **hop_outcome_fields(status, findings, unreachable, mode),
    }


def matrix(hops: Sequence[Mapping[str, Any]], peers: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, str]]:
    slugs = [peer["slug"] for peer in peers]
    table = {slug: {other: "—" for other in slugs} for slug in slugs}
    for hop in hops:
        table[hop["sender_slug"]][hop["destination_slug"]] = hop["status"]
    return table


def _public_peer(peer: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "organization": peer["organization"],
        "slug": peer["slug"],
        "address": peer["address"],
        "repository": peer.get("repository"),
        "profile_id": peer.get("profile_id", PROFILE_ID),
        "peer_source": peer.get("peer_source"),
        "advertisement_readable": peer.get("advertisement_readable", True) is not False,
        "unreadable_reason": peer.get("unreadable_reason"),
    }


def _report(peers: Sequence[Mapping[str, Any]], hops: Sequence[Mapping[str, Any]], *, mode: str,
            mesh_root: Path | None = None, ledger_home: Path | None = None) -> dict[str, Any]:
    counts = {"PASS": 0, "FAIL": 0, "UNREACHABLE": 0, DURABLE_QUEUE: 0}
    for hop in hops:
        counts[hop["status"]] = counts.get(hop["status"], 0) + 1
    return {
        "schema": REPORT_SCHEMA,
        "mode": mode,
        "evidence_class": EVIDENCE_FABRICATED if mode == "fabricated" else EVIDENCE_LIVE,
        "authenticity_claimed": mode == "live" and any(hop["status"] == "PASS" for hop in hops) and all(
            hop["authenticity_claimed"] for hop in hops if hop["status"] == "PASS"),
        "peer_source": "ADVERTISED_CAPABILITY_SLUG_DOT_PROFILE_ID",
        "federation_json_is_a_peer_source": False,
        "authority_constraint": AUTHORITY_CONSTRAINT,
        "time_constraint": TIME_CONSTRAINT,
        "disposition_role": "TRANSITION_EVIDENCE_ONLY",
        "routing_in_scope": False,
        "governance_in_scope": False,
        "authority_effect": "NONE_DIAGNOSTIC_ONLY",
        "far_side": FAR_SIDE if mode == "fabricated" else None,
        "far_side_authentic": False if mode == "fabricated" else None,
        "mesh_root": str(mesh_root) if mesh_root else None,
        "ledger_home": str(ledger_home) if ledger_home else None,
        "ledger_ref": LEDGER_REF if mode == "live" else None,
        "peers": [_public_peer(peer) for peer in peers],
        "advertisements_not_readable": [
            {"organization": peer["organization"], "reason": peer.get("unreadable_reason"), "kept_in_peer_set": True}
            for peer in peers if peer.get("advertisement_readable") is False
        ],
        "hop_count": len(hops),
        "counts": counts,
        "matrix": matrix(hops, peers),
        "hops": list(hops),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """A matrix a person can read, plus one block per hop."""
    peers = report["peers"]
    slugs = [peer["slug"] for peer in peers]
    lines = [
        "# InTr destination hop lane",
        "",
        "Diagnostic of one-way InTr integrity and organization-ledger receipt integrity.",
        "Dispositions below are transition evidence. Authority is the constraint `"
        + report["authority_constraint"] + "`. Time is the constraint `" + report["time_constraint"] + "`.",
        "",
        "- Mode: `" + report["mode"] + "`",
        "- Evidence class: `" + report["evidence_class"] + "`",
        "- Peer source: `" + str(report.get("peer_source")) + "`",
        "- Hops: %d (PASS %d, FAIL %d, UNREACHABLE %d, %s %d)" % (
            report["hop_count"], report["counts"].get("PASS", 0), report["counts"].get("FAIL", 0),
            report["counts"].get("UNREACHABLE", 0), DURABLE_QUEUE, report["counts"].get(DURABLE_QUEUE, 0)),
    ]
    if report["mode"] == "fabricated":
        lines.append("- Far side: `" + FAR_SIDE + "`, labeled non-authentic. Temporary mesh and ledger roots.")
    else:
        lines.append("- Live read of `" + LEDGER_REF + "`. Authenticity is claimed only for a hop whose receipts were read back.")
        queried = report.get("organizations_queried") or []
        if queried:
            lines.append("- Organizations queried: " + ", ".join(queried))
        token_env = report.get("federation_read_token_env") or FEDERATION_READ_TOKEN_ENV
        token_state = "set" if report.get("federation_read_token_present") else "not set"
        lines.append("- Optional token `%s` is %s (reads fall back to `%s`). Public repositories are read without it." % (
            token_env, token_state, report.get("federation_hop_token_env") or FEDERATION_HOP_TOKEN_ENV))
    unread = report.get("advertisements_not_readable") or []
    if unread:
        lines.append("- Advertisements not read (kept in the peer set; their hops are UNREACHABLE): " + ", ".join(
            "%s (%s)" % (item.get("organization", "?"), item.get("reason")) for item in unread))
    silent = report.get("organizations_read_without_intr_destination") or []
    if silent:
        lines.append("- Read, and do not advertise `%s`: %s" % (
            PROFILE_ID, ", ".join(item.get("organization", "?") for item in silent)))
    lines.extend(["", "## Matrix", "", "| sender \\\\ destination | " + " | ".join(slugs) + " |",
                  "| --- | " + " | ".join("---" for _ in slugs) + " |"])
    table = report["matrix"]
    for slug in slugs:
        lines.append("| " + slug + " | " + " | ".join(table[slug][other] for other in slugs) + " |")
    lines.extend(["", "## Hops", ""])
    for hop in report["hops"]:
        lines.append("### %s → %s — %s" % (hop["sender_slug"], hop["destination_slug"], hop["status"]))
        lines.append("")
        lines.append("- Address: `%s`" % hop["destination_service"])
        lines.append("- Closure: request class `%s`, acknowledgement `%s`, communication_id `%s`" % (
            hop["closure"]["responded_request_class"], hop["closure"]["acknowledgement_class"], hop["communication_id"]))
        lines.append("- Sender ledger: `%s`" % hop.get("sender_ledger_ref"))
        lines.append("- Destination ledger: `%s`" % hop.get("destination_ledger_ref"))
        if hop["status"] == "PASS" and report["mode"] == "live":
            lines.append("- Authenticity basis: read back from the destination ledger ref above.")
        elif hop["status"] == "UNREACHABLE":
            lines.append("- Unreachable: `%s`" % json.dumps(hop.get("unreachable"), sort_keys=True))
        elif hop["status"] == DURABLE_QUEUE:
            lines.append("- Sent, not yet closed: `always_on_receiver_required: false`; the next readback evaluates it.")
        elif hop["findings"]:
            lines.append("- Findings: " + ", ".join("`%s`" % item for item in hop["findings"]))
        if hop.get("failure_code"):
            lines.append("- Non-ALLOW: `%s` / `%s`; repair: %s; retry: `%s`; goal: %s; next: %s" % (
                hop["failure_code"], hop["failed_predicate"], hop["required_evidence_or_repair"],
                hop["retry_entrypoint"], hop["owning_existing_goal"], hop["next_attempt"]))
        if hop.get("sender_ledger_head"):
            lines.append("- Sender head: `%s`" % hop["sender_ledger_head"])
        if hop.get("destination_ledger_head"):
            lines.append("- Destination head: `%s`" % hop["destination_ledger_head"])
        lines.append("")
    integrity = report.get("ledger_integrity") or {}
    if integrity:
        lines.extend(["## Ledger integrity", ""])
        for slug in sorted(integrity):
            item = integrity[slug]
            writer = item.get("writer_introduction") or {}
            lines.append("### " + slug)
            lines.append("")
            lines.append("- Writer introduction: %s" % (
                "`%s` at %s (%s)" % (writer.get("commit"), writer.get("committed_at_unix"), writer.get("source"))
                if writer else "not found; no receipt is classified LEGACY"))
            lines.append("- Receipts: %d, LEGACY: %d" % (item.get("receipt_count", 0), item.get("legacy_receipt_count", 0)))
            counts: dict[str, int] = {}
            for entry in item.get("reported") or []:
                key = entry["finding"] + " (" + entry["classification"] + ")"
                counts[key] = counts.get(key, 0) + 1
            if counts:
                lines.append("- Reported, not failing: " + ", ".join(
                    "`%s` ×%d" % (key, value) for key, value in sorted(counts.items())))
            if item.get("findings"):
                lines.append("- Failing: " + ", ".join("`%s`" % finding for finding in item["findings"]))
            lines.append("")
    orchestration = report.get("orchestration")
    if orchestration:
        lines.extend(["## Orchestration", "",
                      "- Supplied hb_epoch: %s, send transitions dispatched: %d (no receiver wait)" % (
                          orchestration.get("hb_epoch"), orchestration.get("dispatched", 0)),
                      "- Outcomes: " + ", ".join("%s %d" % (key, value) for key, value in sorted(
                          (orchestration.get("outcomes") or {}).items())), ""])
    lines.append("Routing and governance are out of scope for this lane.")
    lines.append("")
    return "\n".join(lines)


def write_report(report: Mapping[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "intr-destination-hop-lane.json"
    md_path = out_dir / "intr-destination-hop-lane.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def _roots_from_env_and_args(args: argparse.Namespace) -> list[Path]:
    roots = [Path(item) for item in args.org_root]
    if args.org_dir:
        roots.extend(path for path in Path(args.org_dir).iterdir() if path.is_dir())
    env = os.environ.get("INTR_HOP_ORG_ROOTS")
    if env:
        roots.extend(Path(item) for item in env.split(os.pathsep) if item)
    # Stable and unique.
    found: list[Path] = []
    seen = set()
    for root in roots:
        key = str(root.resolve()) if root.exists() else str(root)
        if key not in seen:
            seen.add(key)
            found.append(root)
    return found


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="InTr destination hop lane: integrity diagnostic for one-way hops and ledger receipts.")
    parser.add_argument("--mode", choices=("fabricated", "live", "orchestrate"), default="fabricated")
    parser.add_argument("--org-root", action="append", default=[], help="organization checkout to discover peers from")
    parser.add_argument("--org-dir", help="directory whose children are organization checkouts")
    parser.add_argument("--mesh-root", type=Path)
    parser.add_argument("--ledger-home", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--epoch-origin", type=int, default=EPOCH_ORIGIN)
    parser.add_argument("--reference-root", type=Path,
                        help="merged StegVerse-org/.github checkout used as the fabricated ledger and kernel contract")
    parser.add_argument("--fetch-ledger-refs", action="store_true",
                        help="live mode: fetch refs/stegverse/organization-ledger when it is not already local")
    parser.add_argument("--organization", action="append", default=[],
                        help="GitHub organization whose .github advertisement live mode reads. "
                             "Defaults to the eight candidate organizations. An organization that "
                             "cannot be read stays in the hop matrix.")
    parser.add_argument("--hb-epoch", default=None,
                        help="orchestrate: supplied epoch of this transition's send dispatches "
                             "(ASCII decimal digits, a non-negative integer)")
    parser.add_argument("--writer-introduced", action="append", default=[],
                        help="ORGANIZATION=<unix seconds or ISO 8601>: receipts added before it are LEGACY. "
                             "Overrides the default-branch history lookup for that organization.")
    parser.add_argument("--no-writer-lookup", action="store_true",
                        help="live: do not look up writer introductions; nothing is LEGACY unless overridden")
    args = parser.parse_args(argv)
    overrides = parse_writer_overrides(args.writer_introduced)
    local_peers = discover_peers(_roots_from_env_and_args(args))
    if args.mode == "fabricated":
        peers = local_peers
        mesh = args.mesh_root or (args.out_dir / "mesh")
        ledger_home = args.ledger_home or (args.out_dir / "ledgers")
        report = run_fabricated(peers, mesh_root=mesh, ledger_home=ledger_home, epoch_origin=args.epoch_origin,
                                reference_root=args.reference_root)
    else:
        names = list(args.organization) or list(CANDIDATE_ORGANIZATIONS)
        hop_token = _blank_to_none(os.environ.get(FEDERATION_HOP_TOKEN_ENV))
        token = _blank_to_none(os.environ.get(FEDERATION_READ_TOKEN_ENV)) or hop_token
        if args.mode == "orchestrate":
            if parse_hb_epoch(args.hb_epoch) is None:
                # Resolved before any read or dispatch: nothing is sent.
                refusal = hb_epoch_fail_closed(args.hb_epoch)
                args.out_dir.mkdir(parents=True, exist_ok=True)
                (args.out_dir / "intr-destination-hop-lane.json").write_text(
                    json.dumps({"mode": "orchestrate", "orchestration": refusal}, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
                print(json.dumps(refusal, sort_keys=True))
                return 1
            if hop_token is None:
                parser.error("--mode orchestrate needs " + FEDERATION_HOP_TOKEN_ENV)
        peers, silent = discover_peers_from_github(names, token=token)
        by_slug = {peer["slug"]: peer for peer in local_peers}
        for peer in peers:
            local = by_slug.get(peer["slug"])
            if local and peer.get("advertisement_readable", True):
                peer["root"] = local["root"]
                if not peer.get("repository_namespace"):
                    peer["repository_namespace"] = local.get("repository_namespace") or repository_namespace(Path(local["root"]))

        def introduction(peer: Mapping[str, Any]) -> Mapping[str, Any] | None:
            if peer["organization"] in overrides:
                return overrides[peer["organization"]]
            if args.no_writer_lookup:
                return None
            if peer.get("root"):
                local = writer_introduction_local(Path(peer["root"]))
                if local:
                    return local
            repository = peer.get("repository") or (peer["organization"] + "/.github")
            return writer_introduction_from_github(repository, token=token)

        # The readback reads whatever receipts exist now. Orchestrate derives
        # each pair's ledger state from it, then records its dispositions.
        report = run_live(peers, fetch=args.fetch_ledger_refs or args.mode == "orchestrate", token=token,
                          writer_introduction=introduction)
        if args.mode == "orchestrate":
            states = {(hop["sender_slug"], hop["destination_slug"]): hop.get("ledger_state", "UNSENT")
                      for hop in report["hops"]}
            report["mode"] = "orchestrate"
            report["orchestration"] = run_orchestrate(peers, hb_epoch=parse_hb_epoch(args.hb_epoch), token=hop_token,
                                                      ledger_state=states)
        report["organizations_queried"] = names
        report["organizations_read_without_intr_destination"] = silent
        report["peer_source"] = "GITHUB_API_ORG_DOTGITHUB_ADVERTISEMENT"
        report["federation_read_token_env"] = FEDERATION_READ_TOKEN_ENV
        report["federation_read_token_present"] = token is not None
        report["federation_hop_token_env"] = FEDERATION_HOP_TOKEN_ENV
    write_report(report, args.out_dir)
    print(render_markdown(report))
    if args.mode == "orchestrate":
        outcomes = (report.get("orchestration") or {}).get("outcomes") or {}
        failing = [hop for hop in report["hops"] if hop["status"] == "FAIL" and hop["findings"] != [NOT_SENT_FINDING]]
        return 1 if outcomes.get("NOT_DISPATCHED") or failing else 0
    if args.mode == "live":
        return 1 if report["counts"].get("FAIL") else 0
    if not peers:
        return 1
    return 0 if report["counts"].get("FAIL", 0) == 0 and report["counts"].get("PASS", 0) == report["hop_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
