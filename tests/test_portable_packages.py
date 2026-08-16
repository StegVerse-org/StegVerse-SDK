import contextlib
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pytest

from stegverse.portable_packages import (
    PortablePackageError,
    download_package,
    inspect_package,
    install_archive,
    list_packages,
    main,
    verify_archive,
)

PACKAGE_VERSION = "0.2.0"
RELEASE_VERSION = "0.2.0"


def sovereignty_contract() -> dict:
    return {
        "physical_host_topology": "ONE_SOVEREIGN_PHYSICAL_HOST",
        "additional_physical_machine_required": False,
        "third_party_machine_required": False,
        "third_party_process_host_required": False,
        "third_party_scheduler_required": False,
        "third_party_state_host_required": False,
        "third_party_control_plane_executor_required": False,
        "third_party_platform_availability_may_block_local_operation": False,
        "independent_validation_mechanism": "SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES",
        "local_governance_replay_reconstruction_survive_third_party_absence": True,
        "external_participants_may_be_optional_inputs_not_runtime_dependencies": True,
        "credential_authority": "TV/TVC",
        "non_tv_tvc_secret_or_token_allowed": False,
    }


def make_package(
    tmp_path: Path,
    deployment_class: str = "S",
    *,
    membership_claim: bool = False,
    contract_override: dict | None = None,
    manifest_override: dict | None = None,
    package_version: str = PACKAGE_VERSION,
    release_version: str = RELEASE_VERSION,
    versioned_id_override: str | None = None,
) -> Path:
    package_id = (
        "stegverse-sdk-s-micro-ecosystem"
        if deployment_class == "S"
        else "stegverse-sdk-ns-micro-ecosystem"
    )
    versioned_package_id = versioned_id_override or f"{package_id}-v{package_version}"
    contract = sovereignty_contract()
    if contract_override:
        contract.update(contract_override)
    manifest = {
        "schema": "stegverse.micro-ecosystem.manifest.v3",
        "micro_ecosystem_id": "stegverse:micro-ecosystem:steggate-admittedcode:v0",
        "single_host_sovereignty": dict(contract),
        "authority_boundaries": {
            "requires_external_host": False,
            "requires_provider_account": False,
            "requires_non_tv_tvc_secret": False,
            "requires_additional_physical_machine": False,
            "requires_third_party_runtime_infrastructure": False,
            "ns_selection_creates_node_membership": False,
        },
    }
    if manifest_override:
        manifest.update(manifest_override)
    payload = json.dumps(manifest, sort_keys=True).encode("utf-8") + b"\n"
    receipt = {
        "schema": "stegverse.sdk.portable-package-receipt.v3",
        "channel": "SDK_EARLY_ACCESS",
        "package_id": package_id,
        "package_generation": "0",
        "package_version": package_version,
        "release_version": release_version,
        "versioned_package_id": versioned_package_id,
        "deployment_class": deployment_class,
        "source_commit": "a" * 40,
        "required_archive_formats": ["zip", "tar.gz"],
        "node_membership_claim": membership_claim,
        "node_membership_activation_required": deployment_class == "NS",
        "files": [
            {
                "path": "micro_ecosystem/manifest.json",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
            }
        ],
        "requires_provider_account": False,
        "requires_non_tv_tvc_secret": False,
        "single_host_sovereignty": dict(contract),
        "physical_additional_machine_required": False,
        "third_party_runtime_infrastructure_required": False,
    }
    archive = tmp_path / f"{versioned_package_id}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("micro_ecosystem/manifest.json", payload)
        zf.writestr("PACKAGE_RECEIPT.json", json.dumps(receipt, sort_keys=True))
    return archive


def test_catalog_exposes_stable_s_and_ns_package_families():
    rows = list_packages()
    assert [row["deployment_class"] for row in rows] == ["S", "NS"]
    assert rows[0]["package_id"] == "stegverse-sdk-s-micro-ecosystem"
    assert rows[1]["package_id"] == "stegverse-sdk-ns-micro-ecosystem"
    s = inspect_package("S")
    assert s["installation_creates_node_membership"] is False
    assert s["single_host_sovereignty"]["physical_host_topology"] == "ONE_SOVEREIGN_PHYSICAL_HOST"
    ns = inspect_package("NS")
    assert ns["node_membership_activation_required"] is True
    assert ns["download_active"] is False


def test_s_package_verifies_explicit_package_and_release_versions_and_installs_versioned(tmp_path):
    archive = make_package(tmp_path, "S")
    verification = verify_archive(archive)
    assert verification["verification_state"] == "PASS"
    assert verification["deployment_class"] == "S"
    assert verification["package_id"] == "stegverse-sdk-s-micro-ecosystem"
    assert verification["package_version"] == PACKAGE_VERSION
    assert verification["release_version"] == RELEASE_VERSION
    assert verification["versioned_package_id"] == f"stegverse-sdk-s-micro-ecosystem-v{PACKAGE_VERSION}"
    assert verification["verified_file_count"] == 1
    assert verification["authority_effect"] == "NONE"

    installed = install_archive(archive, tmp_path / "installed")
    assert installed["installation_state"] == "INSTALLED_NOT_ACTIVATED"
    assert installed["executed_after_install"] is False
    assert installed["node_membership_granted"] is False
    assert installed["package_version"] == PACKAGE_VERSION
    assert installed["release_version"] == RELEASE_VERSION
    target = Path(installed["destination"])
    assert target.name == f"stegverse-sdk-s-micro-ecosystem-v{PACKAGE_VERSION}"
    assert (target / "micro_ecosystem" / "manifest.json").is_file()
    assert (target / "INSTALLATION_RECEIPT.json").is_file()


def test_ns_package_verifies_but_does_not_self_accredit_membership(tmp_path):
    archive = make_package(tmp_path, "NS")
    verification = verify_archive(archive)
    assert verification["deployment_class"] == "NS"
    assert verification["node_membership_claim"] is False
    assert verification["node_membership_activation_required"] is True
    installed = install_archive(archive, tmp_path / "installed")
    assert installed["node_membership_granted"] is False
    assert installed["node_membership_activation_required"] is True


def test_versioned_package_id_mismatch_fails_closed(tmp_path):
    archive = make_package(tmp_path, versioned_id_override="stegverse-sdk-s-micro-ecosystem-v9.9.9")
    with pytest.raises(PortablePackageError, match="versioned_package_id_mismatch"):
        verify_archive(archive)


def test_invalid_package_version_fails_closed(tmp_path):
    archive = make_package(tmp_path, package_version="not-semver")
    with pytest.raises(PortablePackageError, match="invalid_package_version"):
        verify_archive(archive)


def test_archive_filename_is_part_of_version_contract(tmp_path):
    archive = make_package(tmp_path)
    wrong_name = tmp_path / "renamed.zip"
    archive.rename(wrong_name)
    with pytest.raises(PortablePackageError, match="versioned_archive_filename_mismatch"):
        verify_archive(wrong_name)


def test_ns_self_membership_claim_fails_closed(tmp_path):
    archive = make_package(tmp_path, "NS", membership_claim=True)
    with pytest.raises(PortablePackageError, match="node_membership_self_accreditation_prohibited"):
        verify_archive(archive)


@pytest.mark.parametrize(
    "field",
    [
        "additional_physical_machine_required",
        "third_party_machine_required",
        "third_party_process_host_required",
        "third_party_scheduler_required",
        "third_party_state_host_required",
        "third_party_control_plane_executor_required",
        "third_party_platform_availability_may_block_local_operation",
        "non_tv_tvc_secret_or_token_allowed",
    ],
)
def test_any_required_non_sovereign_dependency_fails_closed(tmp_path, field):
    archive = make_package(tmp_path, "S", contract_override={field: True})
    with pytest.raises(PortablePackageError, match="prohibited_sovereignty_dependency"):
        verify_archive(archive)


def test_receipt_and_manifest_sovereignty_must_match(tmp_path):
    archive = make_package(
        tmp_path,
        "S",
        manifest_override={"single_host_sovereignty": {**sovereignty_contract(), "credential_authority": "OTHER"}},
    )
    with pytest.raises(PortablePackageError, match="credential_authority_mismatch"):
        verify_archive(archive)


def test_missing_single_host_contract_fails_closed(tmp_path):
    archive = make_package(tmp_path, "S")
    with zipfile.ZipFile(archive, "r") as zf:
        members = {name: zf.read(name) for name in zf.namelist()}
    receipt = json.loads(members["PACKAGE_RECEIPT.json"])
    del receipt["single_host_sovereignty"]
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("micro_ecosystem/manifest.json", members["micro_ecosystem/manifest.json"])
        zf.writestr("PACKAGE_RECEIPT.json", json.dumps(receipt, sort_keys=True))
    with pytest.raises(PortablePackageError, match="single_host_sovereignty_missing"):
        verify_archive(archive)


def test_tampered_payload_fails_closed(tmp_path):
    archive = make_package(tmp_path, "S")
    with zipfile.ZipFile(archive, "a") as zf:
        zf.writestr("micro_ecosystem/manifest.json", b"tampered")
    with pytest.raises(PortablePackageError):
        verify_archive(archive)


def test_unsafe_archive_path_fails_closed(tmp_path):
    archive = make_package(tmp_path, "S")
    with zipfile.ZipFile(archive, "a") as zf:
        zf.writestr("../escape.txt", b"no")
    with pytest.raises(PortablePackageError, match="unsafe_archive_path"):
        verify_archive(archive)


def test_install_refuses_same_version_existing_target(tmp_path):
    archive = make_package(tmp_path, "S")
    destination = tmp_path / "installed"
    install_archive(archive, destination)
    with pytest.raises(PortablePackageError, match="installation_target_exists"):
        install_archive(archive, destination)


def test_download_fails_closed_until_exact_release_is_bound(tmp_path):
    with pytest.raises(PortablePackageError, match="NO_GOVERNED_RELEASE_ARTIFACT"):
        download_package("S", tmp_path / "package.zip")


def test_console_command_reports_fail_closed_download(tmp_path):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = main(["download", "--deployment-class", "NS", "--output", str(tmp_path / "ns.zip")])
    assert code == 2
    output = json.loads(stream.getvalue())
    assert output["state"] == "FAIL_CLOSED"
    assert output["authority_effect"] == "NONE"
