"""Portable StegVerse S/NS package inspection, verification, and installation.

Package verification is non-authorizing. ZIP and TAR.GZ are equivalent transport
formats over the same declared payload. Installation never executes the package
and never grants Node Sovereign membership.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile
from typing import Any, Mapping
from urllib.request import urlopen
import zipfile

CATALOG_SCHEMA = "stegverse.sdk.portable-console-catalog.v1"
INSTALL_RECEIPT_SCHEMA = "stegverse.sdk.portable-installation-receipt.v1"
PACKAGE_RECEIPT_SCHEMA = "stegverse.sdk.portable-package-receipt.v1"
DEPLOYMENT_CLASSES = ("S", "NS")
ARCHIVE_FORMATS = ("zip", "tar.gz")

CATALOG: dict[str, Any] = {
    "schema": CATALOG_SCHEMA,
    "channel": "SDK_EARLY_ACCESS",
    "canonical_package_owner": "StegVerse-Labs/StegCore",
    "credential_authority": "TV/TVC",
    "requires_provider_account": False,
    "requires_non_tv_tvc_secret": False,
    "required_archive_formats": list(ARCHIVE_FORMATS),
    "packages": {
        "S": {
            "package_id": "stegverse-sdk-s-micro-ecosystem-v0",
            "display_name": "StegVerse S Micro-Ecosystem",
            "deployment_class": "S",
            "sovereignty_class": "Sovereign",
            "node_membership_activation_required": False,
            "artifacts": {fmt: {"release_url": None, "archive_sha256": None} for fmt in ARCHIVE_FORMATS},
        },
        "NS": {
            "package_id": "stegverse-sdk-ns-micro-ecosystem-v0",
            "display_name": "StegVerse NS Micro-Ecosystem",
            "deployment_class": "NS",
            "sovereignty_class": "Node Sovereign",
            "node_membership_activation_required": True,
            "artifacts": {fmt: {"release_url": None, "archive_sha256": None} for fmt in ARCHIVE_FORMATS},
        },
    },
}


class PortablePackageError(ValueError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_packages() -> list[dict[str, Any]]:
    return [dict(CATALOG["packages"][key]) for key in DEPLOYMENT_CLASSES]


def inspect_package(deployment_class: str) -> dict[str, Any]:
    key = deployment_class.upper().strip()
    if key not in DEPLOYMENT_CLASSES:
        raise PortablePackageError("unsupported_deployment_class")
    package = dict(CATALOG["packages"][key])
    package.update(
        {
            "channel": CATALOG["channel"],
            "required_archive_formats": list(ARCHIVE_FORMATS),
            "download_active": all(
                package["artifacts"][fmt].get("release_url") and package["artifacts"][fmt].get("archive_sha256")
                for fmt in ARCHIVE_FORMATS
            ),
            "installation_creates_node_membership": False,
            "authority_effect": "NONE",
        }
    )
    return package


def _safe_member_name(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "" not in path.parts


def _archive_format(path: Path) -> str:
    lower = path.name.lower()
    if lower.endswith(".tar.gz") or lower.endswith(".tgz"):
        return "tar.gz"
    if lower.endswith(".zip"):
        return "zip"
    raise PortablePackageError("unsupported_archive_format")


def _read_archive(path: Path) -> tuple[str, dict[str, bytes]]:
    fmt = _archive_format(path)
    members: dict[str, bytes] = {}
    if fmt == "zip":
        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = zf.namelist()
                if len(names) != len(set(names)):
                    raise PortablePackageError("duplicate_archive_member")
                for name in names:
                    if not _safe_member_name(name):
                        raise PortablePackageError("unsafe_archive_path")
                    members[name] = zf.read(name)
        except zipfile.BadZipFile as exc:
            raise PortablePackageError("invalid_zip_archive") from exc
    else:
        try:
            with tarfile.open(path, "r:gz") as tf:
                names = tf.getnames()
                if len(names) != len(set(names)):
                    raise PortablePackageError("duplicate_archive_member")
                for member in tf.getmembers():
                    name = member.name
                    if not _safe_member_name(name):
                        raise PortablePackageError("unsafe_archive_path")
                    if not member.isfile():
                        raise PortablePackageError("non_file_archive_member")
                    handle = tf.extractfile(member)
                    if handle is None:
                        raise PortablePackageError(f"unreadable_archive_member:{name}")
                    members[name] = handle.read()
        except (tarfile.TarError, OSError) as exc:
            raise PortablePackageError("invalid_tar_gz_archive") from exc
    return fmt, members


def verify_archive(archive: Path) -> dict[str, Any]:
    if not archive.is_file():
        raise PortablePackageError("archive_not_found")
    archive_sha256 = _sha256_file(archive)
    archive_format, members = _read_archive(archive)
    if "PACKAGE_RECEIPT.json" not in members:
        raise PortablePackageError("package_receipt_missing")
    try:
        receipt = json.loads(members["PACKAGE_RECEIPT.json"].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortablePackageError("invalid_package_receipt") from exc
    if not isinstance(receipt, Mapping):
        raise PortablePackageError("invalid_package_receipt")
    if receipt.get("schema") != PACKAGE_RECEIPT_SCHEMA:
        raise PortablePackageError("unsupported_package_receipt_schema")

    deployment_class = str(receipt.get("deployment_class", "")).upper()
    if deployment_class not in DEPLOYMENT_CLASSES:
        raise PortablePackageError("unsupported_deployment_class")
    expected = CATALOG["packages"][deployment_class]
    if receipt.get("package_id") != expected["package_id"]:
        raise PortablePackageError("package_id_mismatch")
    if receipt.get("requires_provider_account") is not False:
        raise PortablePackageError("provider_account_requirement_prohibited")
    if receipt.get("requires_non_tv_tvc_secret") is not False:
        raise PortablePackageError("non_tv_tvc_secret_requirement_prohibited")
    if receipt.get("node_membership_claim") is not False:
        raise PortablePackageError("node_membership_self_accreditation_prohibited")
    if deployment_class == "NS" and receipt.get("node_membership_activation_required") is not True:
        raise PortablePackageError("ns_membership_activation_boundary_missing")
    declared_formats = receipt.get("required_archive_formats")
    if declared_formats is not None and declared_formats != list(ARCHIVE_FORMATS):
        raise PortablePackageError("required_archive_formats_mismatch")

    file_rows = receipt.get("files")
    if not isinstance(file_rows, list) or not file_rows:
        raise PortablePackageError("package_file_manifest_missing")
    expected_names = {"PACKAGE_RECEIPT.json"}
    verified_files: list[dict[str, Any]] = []
    for row in file_rows:
        if not isinstance(row, Mapping):
            raise PortablePackageError("invalid_package_file_manifest")
        name = str(row.get("path", ""))
        if not _safe_member_name(name) or name == "PACKAGE_RECEIPT.json":
            raise PortablePackageError("invalid_package_file_path")
        expected_names.add(name)
        if name not in members:
            raise PortablePackageError(f"package_file_missing:{name}")
        data = members[name]
        if len(data) != int(row.get("size", -1)):
            raise PortablePackageError(f"package_file_size_mismatch:{name}")
        observed_hash = _sha256_bytes(data)
        if observed_hash != row.get("sha256"):
            raise PortablePackageError(f"package_file_hash_mismatch:{name}")
        verified_files.append({"path": name, "sha256": observed_hash, "size": len(data)})
    extras = set(members) - expected_names
    if extras:
        raise PortablePackageError("undeclared_archive_members:" + ",".join(sorted(extras)))

    return {
        "schema": "stegverse.sdk.portable-package-verification.v1",
        "verification_state": "PASS",
        "archive": str(archive),
        "archive_format": archive_format,
        "archive_sha256": archive_sha256,
        "package_id": receipt["package_id"],
        "deployment_class": deployment_class,
        "source_commit": receipt.get("source_commit"),
        "verified_file_count": len(verified_files),
        "verified_files": verified_files,
        "node_membership_claim": False,
        "node_membership_activation_required": deployment_class == "NS",
        "authority_effect": "NONE",
    }


def install_archive(archive: Path, destination: Path) -> dict[str, Any]:
    verification = verify_archive(archive)
    _, members = _read_archive(archive)
    package_id = verification["package_id"]
    target = destination / package_id
    if target.exists():
        raise PortablePackageError("installation_target_exists")
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination) as temp_dir:
        stage = Path(temp_dir) / package_id
        stage.mkdir()
        for name, data in members.items():
            target_path = stage / PurePosixPath(name)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(data)
        shutil.move(str(stage), str(target))
    install_receipt = {
        "schema": INSTALL_RECEIPT_SCHEMA,
        "installation_state": "INSTALLED_NOT_ACTIVATED",
        "package_id": package_id,
        "deployment_class": verification["deployment_class"],
        "archive_format": verification["archive_format"],
        "archive_sha256": verification["archive_sha256"],
        "source_commit": verification.get("source_commit"),
        "destination": str(target),
        "executed_after_install": False,
        "node_membership_granted": False,
        "node_membership_activation_required": verification["deployment_class"] == "NS",
        "authority_effect": "NONE",
    }
    (target / "INSTALLATION_RECEIPT.json").write_text(
        json.dumps(install_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return install_receipt


def download_package(deployment_class: str, output: Path, archive_format: str | None = None) -> dict[str, Any]:
    package = inspect_package(deployment_class)
    fmt = archive_format or _archive_format(output)
    if fmt not in ARCHIVE_FORMATS:
        raise PortablePackageError("unsupported_archive_format")
    artifact = package["artifacts"][fmt]
    url = artifact.get("release_url")
    expected_hash = artifact.get("archive_sha256")
    if not url or not expected_hash:
        raise PortablePackageError("NO_GOVERNED_RELEASE_ARTIFACT")
    output.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(str(url), timeout=30) as response:  # nosec B310 - governed catalog only
        data = response.read()
    observed_hash = _sha256_bytes(data)
    if observed_hash != expected_hash:
        raise PortablePackageError("download_archive_hash_mismatch")
    output.write_bytes(data)
    verification = verify_archive(output)
    if verification["archive_format"] != fmt:
        raise PortablePackageError("download_archive_format_mismatch")
    return {"download_state": "DOWNLOADED_VERIFIED_NOT_INSTALLED", "output": str(output), "verification": verification}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stegverse-portable", description="Inspect, verify, install, or download governed StegVerse portable packages.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    inspect_cmd = sub.add_parser("inspect")
    inspect_cmd.add_argument("--deployment-class", choices=DEPLOYMENT_CLASSES, required=True)
    verify_cmd = sub.add_parser("verify")
    verify_cmd.add_argument("--archive", type=Path, required=True)
    install_cmd = sub.add_parser("install")
    install_cmd.add_argument("--archive", type=Path, required=True)
    install_cmd.add_argument("--destination", type=Path, required=True)
    download_cmd = sub.add_parser("download")
    download_cmd.add_argument("--deployment-class", choices=DEPLOYMENT_CLASSES, required=True)
    download_cmd.add_argument("--format", choices=ARCHIVE_FORMATS)
    download_cmd.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "list":
            result: Any = {"schema": CATALOG_SCHEMA, "channel": CATALOG["channel"], "required_archive_formats": list(ARCHIVE_FORMATS), "packages": list_packages()}
        elif args.command == "inspect":
            result = inspect_package(args.deployment_class)
        elif args.command == "verify":
            result = verify_archive(args.archive)
        elif args.command == "install":
            result = install_archive(args.archive, args.destination)
        elif args.command == "download":
            result = download_package(args.deployment_class, args.output, args.format)
        else:
            return 2
    except (OSError, PortablePackageError, ValueError) as exc:
        print(json.dumps({"state": "FAIL_CLOSED", "error": str(exc), "authority_effect": "NONE"}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
