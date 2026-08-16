"""Portable StegVerse S/NS package inspection, verification, and installation.

Package verification is non-authorizing. ZIP and TAR.GZ are equivalent transport
formats over the same declared payload. Installation never executes the package
and never grants Node Sovereign membership.

Package family identity is stable while package and release versions are explicit.
A valid portable package must be independently operable within its declared local
scope on one sovereign physical host. Required third-party machines, schedulers,
process/state hosts, control-plane executors, or additional validation computers
are prohibited. Independent proof uses isolated logical boundaries on that host.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile
from typing import Any, Mapping
from urllib.request import urlopen
import zipfile

CATALOG_SCHEMA = "stegverse.sdk.portable-console-catalog.v1"
INSTALL_RECEIPT_SCHEMA = "stegverse.sdk.portable-installation-receipt.v2"
PACKAGE_RECEIPT_SCHEMAS = {"stegverse.sdk.portable-package-receipt.v3"}
DEPLOYMENT_CLASSES = ("S", "NS")
ARCHIVE_FORMATS = ("zip", "tar.gz")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
SINGLE_HOST_TOPOLOGY = "ONE_SOVEREIGN_PHYSICAL_HOST"
SINGLE_HOST_VALIDATION = "SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES"
SOVEREIGN_FALSE_FIELDS = (
    "additional_physical_machine_required",
    "third_party_machine_required",
    "third_party_process_host_required",
    "third_party_scheduler_required",
    "third_party_state_host_required",
    "third_party_control_plane_executor_required",
    "third_party_platform_availability_may_block_local_operation",
    "non_tv_tvc_secret_or_token_allowed",
)

CATALOG: dict[str, Any] = {
    "schema": CATALOG_SCHEMA,
    "channel": "SDK_EARLY_ACCESS",
    "canonical_package_owner": "StegVerse-Labs/StegCore",
    "credential_authority": "TV/TVC",
    "requires_provider_account": False,
    "requires_non_tv_tvc_secret": False,
    "required_archive_formats": list(ARCHIVE_FORMATS),
    "single_host_sovereignty": {
        "physical_host_topology": SINGLE_HOST_TOPOLOGY,
        "additional_physical_machine_required": False,
        "third_party_machine_required": False,
        "third_party_process_host_required": False,
        "third_party_scheduler_required": False,
        "third_party_state_host_required": False,
        "third_party_control_plane_executor_required": False,
        "third_party_platform_availability_may_block_local_operation": False,
        "independent_validation_mechanism": SINGLE_HOST_VALIDATION,
        "local_governance_replay_reconstruction_survive_third_party_absence": True,
        "credential_authority": "TV/TVC",
        "non_tv_tvc_secret_or_token_allowed": False,
    },
    "packages": {
        "S": {
            "package_id": "stegverse-sdk-s-micro-ecosystem",
            "display_name": "StegVerse S Micro-Ecosystem",
            "deployment_class": "S",
            "sovereignty_class": "Sovereign",
            "node_membership_activation_required": False,
            "artifacts": {fmt: {"release_url": None, "archive_sha256": None} for fmt in ARCHIVE_FORMATS},
        },
        "NS": {
            "package_id": "stegverse-sdk-ns-micro-ecosystem",
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


def _validate_semver(value: Any, field: str) -> str:
    text = str(value or "")
    if not SEMVER_RE.fullmatch(text):
        raise PortablePackageError(f"invalid_{field}")
    return text


def _validate_single_host_sovereignty(value: Any, *, source: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PortablePackageError(f"single_host_sovereignty_missing:{source}")
    contract = dict(value)
    if contract.get("physical_host_topology") != SINGLE_HOST_TOPOLOGY:
        raise PortablePackageError(f"single_host_topology_invalid:{source}")
    if contract.get("independent_validation_mechanism") != SINGLE_HOST_VALIDATION:
        raise PortablePackageError(f"single_host_validation_boundary_invalid:{source}")
    if contract.get("credential_authority") != "TV/TVC":
        raise PortablePackageError(f"credential_authority_mismatch:{source}")
    for name in SOVEREIGN_FALSE_FIELDS:
        if contract.get(name) is not False:
            raise PortablePackageError(f"prohibited_sovereignty_dependency:{source}:{name}")
    if contract.get("local_governance_replay_reconstruction_survive_third_party_absence") is not True:
        raise PortablePackageError(f"local_sovereign_operation_not_proven:{source}")
    return contract


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
            "single_host_sovereignty": dict(CATALOG["single_host_sovereignty"]),
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


def _archive_filename(versioned_package_id: str, archive_format: str) -> str:
    return f"{versioned_package_id}.{archive_format}"


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


def _load_member_json(members: Mapping[str, bytes], name: str, error: str) -> Mapping[str, Any]:
    if name not in members:
        raise PortablePackageError(error)
    try:
        value = json.loads(members[name].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortablePackageError(error) from exc
    if not isinstance(value, Mapping):
        raise PortablePackageError(error)
    return value


def verify_archive(archive: Path) -> dict[str, Any]:
    if not archive.is_file():
        raise PortablePackageError("archive_not_found")
    archive_sha256 = _sha256_file(archive)
    archive_format, members = _read_archive(archive)
    receipt = _load_member_json(members, "PACKAGE_RECEIPT.json", "package_receipt_missing")
    if receipt.get("schema") not in PACKAGE_RECEIPT_SCHEMAS:
        raise PortablePackageError("unsupported_package_receipt_schema")

    deployment_class = str(receipt.get("deployment_class", "")).upper()
    if deployment_class not in DEPLOYMENT_CLASSES:
        raise PortablePackageError("unsupported_deployment_class")
    expected = CATALOG["packages"][deployment_class]
    package_id = str(receipt.get("package_id") or "")
    if package_id != expected["package_id"]:
        raise PortablePackageError("package_id_mismatch")
    package_version = _validate_semver(receipt.get("package_version"), "package_version")
    release_version = _validate_semver(receipt.get("release_version"), "release_version")
    versioned_package_id = str(receipt.get("versioned_package_id") or "")
    expected_versioned_id = f"{package_id}-v{package_version}"
    if versioned_package_id != expected_versioned_id:
        raise PortablePackageError("versioned_package_id_mismatch")
    if archive.name != _archive_filename(versioned_package_id, archive_format):
        raise PortablePackageError("versioned_archive_filename_mismatch")

    if receipt.get("requires_provider_account") is not False:
        raise PortablePackageError("provider_account_requirement_prohibited")
    if receipt.get("requires_non_tv_tvc_secret") is not False:
        raise PortablePackageError("non_tv_tvc_secret_requirement_prohibited")
    if receipt.get("physical_additional_machine_required") is not False:
        raise PortablePackageError("additional_physical_machine_requirement_prohibited")
    if receipt.get("third_party_runtime_infrastructure_required") is not False:
        raise PortablePackageError("third_party_runtime_infrastructure_prohibited")
    receipt_sovereignty = _validate_single_host_sovereignty(receipt.get("single_host_sovereignty"), source="package_receipt")

    micro_manifest = _load_member_json(members, "micro_ecosystem/manifest.json", "micro_ecosystem_manifest_missing")
    manifest_sovereignty = _validate_single_host_sovereignty(
        micro_manifest.get("single_host_sovereignty"), source="micro_ecosystem_manifest"
    )
    if manifest_sovereignty != receipt_sovereignty:
        raise PortablePackageError("single_host_sovereignty_contract_mismatch")
    boundaries = micro_manifest.get("authority_boundaries")
    if not isinstance(boundaries, Mapping):
        raise PortablePackageError("authority_boundaries_missing")
    if boundaries.get("requires_external_host") is not False:
        raise PortablePackageError("external_host_requirement_prohibited")
    if boundaries.get("requires_additional_physical_machine") is not False:
        raise PortablePackageError("additional_physical_machine_requirement_prohibited")
    if boundaries.get("requires_third_party_runtime_infrastructure") is not False:
        raise PortablePackageError("third_party_runtime_infrastructure_prohibited")

    if receipt.get("node_membership_claim") is not False:
        raise PortablePackageError("node_membership_self_accreditation_prohibited")
    if deployment_class == "NS" and receipt.get("node_membership_activation_required") is not True:
        raise PortablePackageError("ns_membership_activation_boundary_missing")
    declared_formats = receipt.get("required_archive_formats")
    if declared_formats != list(ARCHIVE_FORMATS):
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
        "schema": "stegverse.sdk.portable-package-verification.v3",
        "verification_state": "PASS",
        "archive": str(archive),
        "archive_format": archive_format,
        "archive_sha256": archive_sha256,
        "package_id": package_id,
        "package_version": package_version,
        "release_version": release_version,
        "versioned_package_id": versioned_package_id,
        "deployment_class": deployment_class,
        "source_commit": receipt.get("source_commit"),
        "verified_file_count": len(verified_files),
        "verified_files": verified_files,
        "single_host_sovereignty": receipt_sovereignty,
        "physical_additional_machine_required": False,
        "third_party_runtime_infrastructure_required": False,
        "node_membership_claim": False,
        "node_membership_activation_required": deployment_class == "NS",
        "authority_effect": "NONE",
    }


def install_archive(archive: Path, destination: Path) -> dict[str, Any]:
    verification = verify_archive(archive)
    _, members = _read_archive(archive)
    versioned_package_id = verification["versioned_package_id"]
    target = destination / versioned_package_id
    if target.exists():
        raise PortablePackageError("installation_target_exists")
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination) as temp_dir:
        stage = Path(temp_dir) / versioned_package_id
        stage.mkdir()
        for name, data in members.items():
            target_path = stage / PurePosixPath(name)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(data)
        shutil.move(str(stage), str(target))
    install_receipt = {
        "schema": INSTALL_RECEIPT_SCHEMA,
        "installation_state": "INSTALLED_NOT_ACTIVATED",
        "package_id": verification["package_id"],
        "package_version": verification["package_version"],
        "release_version": verification["release_version"],
        "versioned_package_id": versioned_package_id,
        "deployment_class": verification["deployment_class"],
        "archive_format": verification["archive_format"],
        "archive_sha256": verification["archive_sha256"],
        "source_commit": verification.get("source_commit"),
        "destination": str(target),
        "single_host_sovereignty": verification["single_host_sovereignty"],
        "physical_additional_machine_required": False,
        "third_party_runtime_infrastructure_required": False,
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
            result: Any = {
                "schema": CATALOG_SCHEMA,
                "channel": CATALOG["channel"],
                "required_archive_formats": list(ARCHIVE_FORMATS),
                "single_host_sovereignty": dict(CATALOG["single_host_sovereignty"]),
                "packages": list_packages(),
            }
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