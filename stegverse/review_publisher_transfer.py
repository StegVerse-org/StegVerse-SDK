"""Prepare exact review evidence for the *existing* Publisher InTr transfer.

This SDK-side producer never transports, renders, takes custody or claims a
Publisher return. Original proof of governed execution and authorized source
exports must arrive independently from their actual owning services.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .publisher_return_binding import (
    assemble_publisher_return,
    verify_publisher_return,
    verify_publisher_return_binding,
)

TRANSFER_SCHEMA = "stegverse.publisher.artifact-transfer/v1"
EXPORT_SCHEMA = "stegverse.publisher.evidence-report-package/v1"
SAFE_ORIGINAL = re.compile(r"^evidence/[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.(?:png|jpg|jpeg|pdf|json|txt|md)$")
MEDIA_TYPES = {"image/png", "image/jpeg", "application/pdf", "application/json", "text/plain", "text/markdown"}
HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
SOURCE_CLASSES = {"USER_SUPPLIED_ORIGINAL", "COUNTERPART_SUPPLIED_ORIGINAL", "AUTHENTIC_RETAINED_EVIDENCE"}
MAX_SINGLE = 20 * 1024 * 1024
MAX_TOTAL = 80 * 1024 * 1024


class ReviewPublisherBoundaryError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return digest_bytes(canonical_json(value).encode("utf-8"))


def _normalize_assets(assets: Any, export_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(assets, list):
        raise ReviewPublisherBoundaryError("exact originals must be supplied as a list")
    seen: dict[str, dict[str, Any]] = {}
    total = 0
    for value in assets:
        if not isinstance(value, Mapping):
            raise ReviewPublisherBoundaryError("original asset must be an object")
        original = copy.deepcopy(dict(value))
        if set(original) != {"path", "media_type", "sha256", "bytes", "content_base64", "source_class"}:
            raise ReviewPublisherBoundaryError("original evidence field set mismatch")
        name = original["path"]
        if not isinstance(name, str) or not SAFE_ORIGINAL.fullmatch(name) or name in seen:
            raise ReviewPublisherBoundaryError("unsafe/duplicate evidence path")
        if original["media_type"] not in MEDIA_TYPES or original["source_class"] not in SOURCE_CLASSES:
            raise ReviewPublisherBoundaryError("original evidence class/media type invalid")
        try:
            raw = base64.b64decode(original["content_base64"], validate=True)
        except (ValueError, TypeError) as exc:
            raise ReviewPublisherBoundaryError("invalid original base64") from exc
        if not raw or len(raw) > MAX_SINGLE or len(raw) != original["bytes"] or digest_bytes(raw) != original["sha256"]:
            raise ReviewPublisherBoundaryError("original evidence exact bytes/hash mismatch")
        if original["media_type"] == "application/pdf" and not raw.startswith(b"%PDF-"):
            raise ReviewPublisherBoundaryError("PDF original signature mismatch")
        if original["media_type"] == "image/png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ReviewPublisherBoundaryError("PNG original signature mismatch")
        total += len(raw)
        if total > MAX_TOTAL:
            raise ReviewPublisherBoundaryError("original evidence exceeds bounded capacity")
        seen[name] = original

    evidence = export_bundle.get("evidence")
    if not isinstance(evidence, list):
        raise ReviewPublisherBoundaryError("source export evidence inventory required")
    expected: dict[str, dict[str, Any]] = {}
    for row in evidence:
        if not isinstance(row, Mapping):
            raise ReviewPublisherBoundaryError("invalid source evidence inventory row")
        name = row.get("path")
        if isinstance(name, str) and name.startswith("evidence/"):
            if name in expected:
                raise ReviewPublisherBoundaryError("duplicate source inventory path")
            expected[name] = dict(row)
    if set(expected) != set(seen):
        raise ReviewPublisherBoundaryError("every declared original must have exact original bytes")
    for name, row in expected.items():
        original = seen[name]
        if (row.get("content_hash") != original["sha256"]
                or row.get("bytes") != original["bytes"]
                or row.get("media_type") != original["media_type"]
                or row.get("fidelity") != "exact"
                or row.get("payload_available") is not True
                or row.get("restricted") is not False):
            raise ReviewPublisherBoundaryError("original bytes do not match source inventory")
    return [seen[name] for name in sorted(seen)]


def prepare_review_transfer(
    *,
    manifest: Mapping[str, Any],
    authorized_export_bundle: Mapping[str, Any],
    original_assets: list[Mapping[str, Any]],
    transfer_id: str,
) -> dict[str, Any]:
    """Produce Publisher's existing exact transfer envelope, not a transition.

    The admitted export must be obtained from the actual authorized source
    owner. This function validates the declared metadata and exact originals;
    it cannot establish that the authorization or retained evidence is genuine.
    """
    validated = validate_ingress_manifest(manifest)
    completion = validated.get("completion")
    publisher = completion.get("publisher") if isinstance(completion, Mapping) else None
    if not isinstance(publisher, Mapping) or publisher.get("required") is not True:
        raise ReviewPublisherBoundaryError("review transfer requires Publisher on this manifest")
    if publisher.get("package_profile") != EXPORT_SCHEMA:
        raise ReviewPublisherBoundaryError("Publisher report profile mismatch")
    bundle = copy.deepcopy(dict(authorized_export_bundle))
    if bundle.get("schema_version") != EXPORT_SCHEMA:
        raise ReviewPublisherBoundaryError("generic evaluator source export required")
    source = bundle.get("source")
    if not isinstance(source, Mapping) or source.get("verification_root") != digest(manifest):
        raise ReviewPublisherBoundaryError("source export must bind the exact original SDK manifest hash")
    supplied_hash = bundle.get("export_sha256")
    unhashed = {key:value for key,value in bundle.items() if key != "export_sha256"}
    if supplied_hash != digest(unhashed):
        raise ReviewPublisherBoundaryError("source export digest mismatch")
    authorization = bundle.get("authorization")
    if not isinstance(authorization, Mapping) or authorization.get("status") != "active" or authorization.get("revoked") is not False:
        raise ReviewPublisherBoundaryError("source export authorization must be provided as active")
    if authorization.get("destination") != "GCAT-BCAT-Engine/Publisher":
        raise ReviewPublisherBoundaryError("source export destination mismatch")
    if bundle.get("authority_effect") != "NONE" or any(bundle.get(flag) is not False for flag in ("publication_authorized","release_authorized","execution_authorized")):
        raise ReviewPublisherBoundaryError("source export expands authority")
    if not isinstance(transfer_id,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}",transfer_id):
        raise ReviewPublisherBoundaryError("safe transfer id required")
    originals = _normalize_assets(original_assets,bundle)
    formats = bundle.get("requested_formats")
    if not isinstance(formats,list) or not formats:
        raise ReviewPublisherBoundaryError("requested artifact formats required")
    transfer = {
        "schema":TRANSFER_SCHEMA,
        "transfer_id":transfer_id,
        "operation":"TRANSFER",
        "export_bundle":bundle,
        "export_sha256":supplied_hash,
        "requested_formats":formats,
        "authorization_ref":authorization.get("authority_ref"),
        "publication_authorized":False,
        "release_authorized":False,
        "execution_authorized":False,
        "authority_effect":"NONE",
        "evaluator_assets":originals,
    }
    transfer_bytes=canonical_json(transfer).encode("utf-8")
    return {
        "transfer":transfer,
        "transfer_bytes":transfer_bytes,
        "transfer_sha256":digest_bytes(transfer_bytes),
        "transfer_id":transfer_id,
        "export_sha256":supplied_hash,
        "original_manifest_sha256":digest(manifest),
        "expected_original_paths":sorted(item["path"] for item in originals),
        "state":"PREPARED_NOT_TRANSPORTED",
        "authority_effect":"NONE",
    }


def bind_exact_review_return(
    *, prepared: Mapping[str, Any], manifest: Mapping[str, Any],
    manifest_receipt_id: str, publisher_return_bytes: bytes,
) -> dict[str, Any]:
    """Bind a received Publisher packet only to the original prepared input.

    Authentic transport/custody remains separately required: a local fixture
    return is not proof the real Publisher was invoked.
    """
    parsed=verify_publisher_return(publisher_return_bytes)
    if parsed.get("transfer_id") != prepared.get("transfer_id"):
        raise ReviewPublisherBoundaryError("Publisher transfer ID mismatch")
    if parsed.get("source_export_sha256") != prepared.get("export_sha256"):
        raise ReviewPublisherBoundaryError("Publisher source export mismatch")
    if prepared.get("original_manifest_sha256") != digest(manifest):
        raise ReviewPublisherBoundaryError("original manifest changed after transfer")
    artifact_manifest = parsed.get("manifest")
    rendering_receipt = parsed.get("rendering_receipt")
    if (not isinstance(artifact_manifest, Mapping) or
        artifact_manifest.get("manifest_sha256") != digest({k:v for k,v in artifact_manifest.items() if k != "manifest_sha256"})):
        raise ReviewPublisherBoundaryError("Publisher manifest exact digest invalid")
    if (not isinstance(rendering_receipt, Mapping) or
        rendering_receipt.get("manifest_sha256") != artifact_manifest["manifest_sha256"] or
        rendering_receipt.get("receipt_sha256") != digest({k:v for k,v in rendering_receipt.items() if k != "receipt_sha256"})):
        raise ReviewPublisherBoundaryError("Publisher rendering receipt exact digest invalid")
    manifest_paths = [row.get("path") for row in artifact_manifest.get("artifacts",[]) if isinstance(row,Mapping)]
    returned_paths = [row.get("path") for row in parsed.get("artifacts",[]) if isinstance(row,Mapping)]
    if (len(manifest_paths) != len(set(manifest_paths)) or
        len(returned_paths) != len(set(returned_paths)) or
        set(manifest_paths) != set(returned_paths)):
        raise ReviewPublisherBoundaryError("Publisher return incomplete artifact coverage")
    returned={item.get("path"):item for item in parsed.get("artifacts",[]) if isinstance(item,Mapping)}
    if not set(prepared.get("expected_original_paths",[])).issubset(returned):
        raise ReviewPublisherBoundaryError("Publisher omitted an original")
    result=assemble_publisher_return(
        manifest=manifest,manifest_receipt_id=manifest_receipt_id,
        publisher_return_bytes=publisher_return_bytes,
    )
    verify_publisher_return_binding(result)
    return result
