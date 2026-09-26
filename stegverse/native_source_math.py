"""Application-neutral, source-package-installed mathematical execution for SDK manifests.

The SDK never imports a caller-chosen module or ships private source. Only an
already-installed entry point can execute, and its exact original source file
must match the declared Git blob before invocation. The resulting mathematical
candidate is never standing, admissibility or execution authority.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import inspect
import json
import re
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import NATIVE_SOURCE_MATH_ROUTE_ID, route_from_manifest

PROFILE = "stegverse.native-source-math.v1"
ENTRY_POINT_GROUP = "stegverse.native_math.v1"
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED = {
    "profile", "source_distribution", "source_version", "source_entry_point",
    "source_git_blob_sha1", "source_revision", "original_specimen_b64",
    "native_input", "expected_native_result_sha256",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _installed_entry_points() -> list[Any]:
    try:
        return list(metadata.entry_points(group=ENTRY_POINT_GROUP))
    except TypeError:  # Python 3.9 dictionary-style entry point API
        return list(metadata.entry_points().get(ENTRY_POINT_GROUP, []))


def _require_hex(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(label + " must be exact lowercase hexadecimal")
    return value


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if (route["route_id"] != NATIVE_SOURCE_MATH_ROUTE_ID
            or canonical["processing"]["capability"] != "native_source_math"):
        raise ValueError("NATIVE_SOURCE_MATH_ROUTE_REQUIRED")
    payload = canonical.get("payload")
    if not isinstance(payload, Mapping) or payload.get("profile") != PROFILE:
        raise ValueError("NATIVE_SOURCE_MATH_PAYLOAD_REQUIRED")
    extra = sorted(set(payload) - _ALLOWED)
    if extra:
        raise ValueError("unknown native source math fields: " + ", ".join(extra))
    for key in ("source_distribution", "source_version", "source_entry_point", "source_revision"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(key + " must be supplied")
    blob_sha = _require_hex(payload.get("source_git_blob_sha1"), _HEX40, "source_git_blob_sha1")
    if not isinstance(payload.get("native_input"), Mapping):
        raise ValueError("native_input must be an object")
    encoded = payload.get("original_specimen_b64")
    if not isinstance(encoded, str):
        raise ValueError("original_specimen_b64 must contain actual specimen bytes")
    try:
        specimen = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("invalid exact original specimen bytes") from exc
    if not specimen:
        raise ValueError("empty original specimen is not accepted")
    specimen_hash = "sha256:" + hashlib.sha256(specimen).hexdigest()
    native_input = dict(payload["native_input"])
    if "specimen_sha256" in native_input and native_input["specimen_sha256"] != specimen_hash:
        raise ValueError("ORIGINAL_SPECIMEN_SHA256_MISMATCH")

    matching = []
    for entry in _installed_entry_points():
        distribution = getattr(entry, "dist", None)
        if distribution is None:
            continue
        if (entry.name == payload["source_entry_point"]
                and distribution.metadata.get("Name", "").lower() == payload["source_distribution"].lower()
                and distribution.version == payload["source_version"]):
            matching.append(entry)
    if len(matching) != 1:
        raise ValueError("NATIVE_SOURCE_PACKAGE_NOT_INSTALLED_OR_AMBIGUOUS")
    source_callable = matching[0].load()
    if not callable(source_callable):
        raise ValueError("INSTALLED_NATIVE_SOURCE_NOT_CALLABLE")
    source_path = inspect.getsourcefile(source_callable)
    if not source_path:
        raise ValueError("INSTALLED_NATIVE_SOURCE_FILE_UNAVAILABLE")
    original_code = Path(source_path).read_bytes()
    actual_blob = hashlib.sha1(
        b"blob " + str(len(original_code)).encode("ascii") + b"\0" + original_code
    ).hexdigest()
    if actual_blob != blob_sha:
        raise ValueError("INSTALLED_NATIVE_SOURCE_BLOB_MISMATCH")
    # Installation/package provenance is separate from a caller-declared commit.
    # The exact on-disk original file and installed distribution are verified;
    # a source commit label alone never proves rights or installed provenance.
    native = source_callable(native_input, original_specimen_bytes=specimen)
    if not isinstance(native, Mapping):
        raise ValueError("native processor must return an object")
    native = dict(native)
    digest = native.get("result_sha256")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError("NATIVE_SOURCE_RESULT_DIGEST_MISSING")
    _require_hex(digest[7:], _HEX64, "native result hash")
    actual = "sha256:" + hashlib.sha256(
        _canonical({k: v for k, v in native.items() if k != "result_sha256"})
    ).hexdigest()
    if actual != digest:
        raise ValueError("NATIVE_SOURCE_RESULT_HASH_MISMATCH")
    expected = payload.get("expected_native_result_sha256")
    if expected is not None and digest != expected:
        raise ValueError("EXPECTED_NATIVE_RESULT_HASH_MISMATCH")
    return {
        "schema": "stegverse.native-source-math-result.v1",
        "authority_effect": "NONE_SOURCE_RESULT_ONLY",
        "governed_runtime_observed": False,
        "source_distribution": payload["source_distribution"],
        "source_version": payload["source_version"],
        "source_entry_point": payload["source_entry_point"],
        "source_revision_declared_not_attested": payload["source_revision"],
        "source_git_blob_sha1_verified": actual_blob,
        "original_specimen_sha256_verified": specimen_hash,
        "native_result_sha256_verified": digest,
        "expected_native_result_hash_matched": expected is not None,
        "native_result": native,
    }
