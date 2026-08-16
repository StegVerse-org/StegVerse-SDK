import hashlib
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


def make_package(tmp_path: Path, deployment_class: str = "S", *, membership_claim: bool = False) -> Path:
    package_id = (
        "stegverse-sdk-s-micro-ecosystem-v0"
        if deployment_class == "S"
        else "stegverse-sdk-ns-micro-ecosystem-v0"
    )
    payload = b'{"fixture":"portable"}\n'
    receipt = {
        "schema": "stegverse.sdk.portable-package-receipt.v1",
        "channel": "SDK_EARLY_ACCESS",
        "package_id": package_id,
        "deployment_class": deployment_class,
        "source_commit": "a" * 40,
        "node_membership_claim": membership_claim,
        "node_membership_activation_required": deployment_class == "NS",
        "files": [
            {
                "path": "micro_ecosystem/fixture.json",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
            }
        ],
        "requires_provider_account": False,
        "requires_non_tv_tvc_secret": False,
    }
    archive = tmp_path / f"{package_id}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("micro_ecosystem/fixture.json", payload)
        zf.writestr("PACKAGE_RECEIPT.json", json.dumps(receipt, sort_keys=True))
    return archive


def test_catalog_exposes_explicit_s_and_ns_without_membership_claim():
    rows = list_packages()
    assert [row["deployment_class"] for row in rows] == ["S", "NS"]
    assert inspect_package("S")["installation_creates_node_membership"] is False
    ns = inspect_package("NS")
    assert ns["node_membership_activation_required"] is True
    assert ns["download_active"] is False


def test_s_package_verifies_and_installs_without_execution(tmp_path):
    archive = make_package(tmp_path, "S")
    verification = verify_archive(archive)
    assert verification["verification_state"] == "PASS"
    assert verification["deployment_class"] == "S"
    assert verification["verified_file_count"] == 1
    assert verification["authority_effect"] == "NONE"

    installed = install_archive(archive, tmp_path / "installed")
    assert installed["installation_state"] == "INSTALLED_NOT_ACTIVATED"
    assert installed["executed_after_install"] is False
    assert installed["node_membership_granted"] is False
    target = Path(installed["destination"])
    assert (target / "micro_ecosystem" / "fixture.json").is_file()
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


def test_ns_self_membership_claim_fails_closed(tmp_path):
    archive = make_package(tmp_path, "NS", membership_claim=True)
    with pytest.raises(PortablePackageError, match="node_membership_self_accreditation_prohibited"):
        verify_archive(archive)


def test_tampered_payload_fails_closed(tmp_path):
    archive = make_package(tmp_path, "S")
    with zipfile.ZipFile(archive, "a") as zf:
        zf.writestr("micro_ecosystem/fixture.json", b"tampered")
    with pytest.raises(PortablePackageError):
        verify_archive(archive)


def test_unsafe_archive_path_fails_closed(tmp_path):
    archive = make_package(tmp_path, "S")
    with zipfile.ZipFile(archive, "a") as zf:
        zf.writestr("../escape.txt", b"no")
    with pytest.raises(PortablePackageError, match="unsafe_archive_path"):
        verify_archive(archive)


def test_install_refuses_existing_target(tmp_path):
    archive = make_package(tmp_path, "S")
    destination = tmp_path / "installed"
    install_archive(archive, destination)
    with pytest.raises(PortablePackageError, match="installation_target_exists"):
        install_archive(archive, destination)


def test_download_fails_closed_until_exact_release_is_bound(tmp_path):
    with pytest.raises(PortablePackageError, match="NO_GOVERNED_RELEASE_ARTIFACT"):
        download_package("S", tmp_path / "package.zip")


def test_console_command_reports_fail_closed_download(tmp_path, capsys):
    code = main(["download", "--deployment-class", "NS", "--output", str(tmp_path / "ns.zip")])
    assert code == 2
    output = json.loads(capsys.readouterr().out)
    assert output["state"] == "FAIL_CLOSED"
    assert output["authority_effect"] == "NONE"
