from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
import zipfile

from .portable_governance_verifier import bundle_hash, verify_portable_governance_bundle

EXCHANGE_SCHEMA = "stegverse.portable-governance-evidence-exchange.v1"
MANIFEST_NAME = "EXCHANGE_MANIFEST.json"
BUNDLE_NAME = "governance_bundle.json"
REPORT_NAME = "verification_report.json"
REQUIRED_MEMBERS = (MANIFEST_NAME, BUNDLE_NAME, REPORT_NAME)


class PortableGovernanceExchangeError(ValueError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and len(path.parts) == 1


def create_exchange(bundle: Mapping[str, Any], destination: Path) -> dict[str, Any]:
    """Create a bounded, self-verifying archive from an existing published verifier bundle."""
    value = dict(bundle)
    report = verify_portable_governance_bundle(value)
    bundle_bytes = _canonical_bytes(value)
    report_bytes = _canonical_bytes(report)
    manifest = {
        "schema": EXCHANGE_SCHEMA,
        "bundle_schema": value.get("schema"),
        "verification_report_schema": report.get("schema"),
        "stage": report.get("stage"),
        "package_id": report.get("package_id"),
        "transition_id": report.get("transition_id"),
        "run_id": report.get("run_id"),
        "bundle_hash": bundle_hash(value),
        "files": {
            BUNDLE_NAME: {"sha256": _sha256(bundle_bytes), "size": len(bundle_bytes)},
            REPORT_NAME: {"sha256": _sha256(report_bytes), "size": len(report_bytes)},
        },
        "authority": {
            "exchange_authority": "NONE",
            "verification_authority": "NONE",
            "execution_authorized": False,
            "custody_installed": False,
        },
    }
    manifest_bytes = _canonical_bytes(manifest)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(MANIFEST_NAME, manifest_bytes)
        archive.writestr(BUNDLE_NAME, bundle_bytes)
        archive.writestr(REPORT_NAME, report_bytes)
    return {
        "schema": "stegverse.portable-governance-evidence-exchange-creation.v1",
        "status": "CREATED",
        "archive": str(destination),
        "archive_sha256": _sha256(destination.read_bytes()),
        "manifest": manifest,
        "authority_effect": "NONE",
    }


def verify_exchange(archive_path: Path) -> dict[str, Any]:
    """Verify archive structure, file hashes, bundle semantics, and deterministic report equivalence."""
    if not archive_path.is_file():
        raise PortableGovernanceExchangeError("archive_not_found")
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise PortableGovernanceExchangeError("duplicate_archive_member")
            if any(not _safe_member(name) for name in names):
                raise PortableGovernanceExchangeError("unsafe_archive_member")
            if set(names) != set(REQUIRED_MEMBERS):
                raise PortableGovernanceExchangeError("archive_members_mismatch")
            raw = {name: archive.read(name) for name in REQUIRED_MEMBERS}
    except zipfile.BadZipFile as exc:
        raise PortableGovernanceExchangeError("invalid_zip_archive") from exc

    try:
        manifest = json.loads(raw[MANIFEST_NAME].decode("utf-8"))
        bundle = json.loads(raw[BUNDLE_NAME].decode("utf-8"))
        retained_report = json.loads(raw[REPORT_NAME].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortableGovernanceExchangeError("invalid_exchange_json") from exc
    if not all(isinstance(value, dict) for value in (manifest, bundle, retained_report)):
        raise PortableGovernanceExchangeError("exchange_json_root_must_be_object")
    if manifest.get("schema") != EXCHANGE_SCHEMA:
        raise PortableGovernanceExchangeError("unsupported_exchange_schema")

    files = manifest.get("files")
    if not isinstance(files, dict):
        raise PortableGovernanceExchangeError("file_manifest_missing")
    for name in (BUNDLE_NAME, REPORT_NAME):
        row = files.get(name)
        if not isinstance(row, dict):
            raise PortableGovernanceExchangeError(f"file_manifest_missing:{name}")
        if row.get("size") != len(raw[name]):
            raise PortableGovernanceExchangeError(f"file_size_mismatch:{name}")
        if row.get("sha256") != _sha256(raw[name]):
            raise PortableGovernanceExchangeError(f"file_hash_mismatch:{name}")

    live_report = verify_portable_governance_bundle(bundle)
    if retained_report != live_report:
        raise PortableGovernanceExchangeError("verification_report_mismatch")
    if manifest.get("bundle_hash") != bundle_hash(bundle):
        raise PortableGovernanceExchangeError("bundle_hash_mismatch")
    for field in ("stage", "package_id", "transition_id", "run_id"):
        if manifest.get(field) != live_report.get(field):
            raise PortableGovernanceExchangeError(f"manifest_identity_mismatch:{field}")
    authority = manifest.get("authority") or {}
    if authority != {
        "exchange_authority": "NONE",
        "verification_authority": "NONE",
        "execution_authorized": False,
        "custody_installed": False,
    }:
        raise PortableGovernanceExchangeError("exchange_authority_boundary_invalid")

    return {
        "schema": "stegverse.portable-governance-evidence-exchange-verification.v1",
        "status": "PASS",
        "archive": str(archive_path),
        "archive_sha256": _sha256(archive_path.read_bytes()),
        "stage": live_report["stage"],
        "package_id": live_report["package_id"],
        "transition_id": live_report["transition_id"],
        "run_id": live_report["run_id"],
        "bundle_hash": live_report["bundle_hash"],
        "checks": [
            "ARCHIVE_STRUCTURE_VALID",
            "EXCHANGE_FILE_HASHES_VALID",
            "PORTABLE_GOVERNANCE_BUNDLE_VALID",
            "VERIFICATION_REPORT_REPRODUCED",
            "EXCHANGE_AUTHORITY_NON_TRANSFER_VALID",
        ],
        "authority": {
            "exchange_authority": "NONE",
            "verification_authority": "NONE",
            "execution_authorized": False,
            "custody_installed": False,
        },
    }


def extract_bundle(archive_path: Path, destination: Path) -> dict[str, Any]:
    """Verify first, then extract only the bounded bundle/report/manifest files."""
    verification = verify_exchange(archive_path)
    if destination.exists() and any(destination.iterdir()):
        raise PortableGovernanceExchangeError("destination_not_empty")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "r") as archive:
        for name in REQUIRED_MEMBERS:
            (destination / name).write_bytes(archive.read(name))
    return {
        "schema": "stegverse.portable-governance-evidence-exchange-extraction.v1",
        "status": "EXTRACTED_VERIFIED_NOT_IMPORTED_AS_CUSTODY",
        "destination": str(destination),
        "bundle_hash": verification["bundle_hash"],
        "custody_installed": False,
        "authority_effect": "NONE",
    }


__all__ = [
    "EXCHANGE_SCHEMA",
    "PortableGovernanceExchangeError",
    "create_exchange",
    "verify_exchange",
    "extract_bundle",
]
