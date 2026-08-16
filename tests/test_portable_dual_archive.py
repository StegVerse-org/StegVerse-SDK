import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

from stegverse.portable_packages import install_archive, verify_archive

PACKAGE_VERSION = "0.2.0"
RELEASE_VERSION = "0.2.0"


def sovereignty_contract():
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


def receipt_and_payload(deployment_class="S"):
    package_id = "stegverse-sdk-s-micro-ecosystem" if deployment_class == "S" else "stegverse-sdk-ns-micro-ecosystem"
    versioned_package_id = f"{package_id}-v{PACKAGE_VERSION}"
    contract = sovereignty_contract()
    manifest = {
        "schema": "stegverse.micro-ecosystem.manifest.v3",
        "single_host_sovereignty": contract,
        "authority_boundaries": {
            "requires_external_host": False,
            "requires_additional_physical_machine": False,
            "requires_third_party_runtime_infrastructure": False,
        },
    }
    payload = json.dumps(manifest, sort_keys=True).encode() + b"\n"
    receipt = {
        "schema": "stegverse.sdk.portable-package-receipt.v3",
        "channel": "SDK_EARLY_ACCESS",
        "package_id": package_id,
        "package_generation": "0",
        "package_version": PACKAGE_VERSION,
        "release_version": RELEASE_VERSION,
        "versioned_package_id": versioned_package_id,
        "deployment_class": deployment_class,
        "source_commit": "a" * 40,
        "required_archive_formats": ["zip", "tar.gz"],
        "node_membership_claim": False,
        "node_membership_activation_required": deployment_class == "NS",
        "files": [{"path": "micro_ecosystem/manifest.json", "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}],
        "requires_provider_account": False,
        "requires_non_tv_tvc_secret": False,
        "single_host_sovereignty": contract,
        "physical_additional_machine_required": False,
        "third_party_runtime_infrastructure_required": False,
    }
    return versioned_package_id, payload, json.dumps(receipt, sort_keys=True).encode()


def build_pair(tmp_path: Path, deployment_class="S"):
    versioned_package_id, payload, receipt = receipt_and_payload(deployment_class)
    zip_path = tmp_path / f"{versioned_package_id}.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("micro_ecosystem/manifest.json", payload)
        zf.writestr("PACKAGE_RECEIPT.json", receipt)
    tar_path = tmp_path / f"{versioned_package_id}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        for name, data in (("micro_ecosystem/manifest.json", payload), ("PACKAGE_RECEIPT.json", receipt)):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return zip_path, tar_path


def test_zip_and_tar_gz_verify_same_s_payload(tmp_path):
    zip_path, tar_path = build_pair(tmp_path, "S")
    zip_result = verify_archive(zip_path)
    tar_result = verify_archive(tar_path)
    assert zip_result["archive_format"] == "zip"
    assert tar_result["archive_format"] == "tar.gz"
    assert zip_result["package_id"] == tar_result["package_id"] == "stegverse-sdk-s-micro-ecosystem"
    assert zip_result["package_version"] == tar_result["package_version"] == PACKAGE_VERSION
    assert zip_result["release_version"] == tar_result["release_version"] == RELEASE_VERSION
    assert zip_result["deployment_class"] == tar_result["deployment_class"] == "S"
    assert zip_result["verified_files"] == tar_result["verified_files"]


def test_tar_gz_ns_install_remains_not_activated(tmp_path):
    _, tar_path = build_pair(tmp_path, "NS")
    installed = install_archive(tar_path, tmp_path / "installed")
    assert installed["archive_format"] == "tar.gz"
    assert installed["package_version"] == PACKAGE_VERSION
    assert installed["installation_state"] == "INSTALLED_NOT_ACTIVATED"
    assert installed["node_membership_granted"] is False
    assert installed["node_membership_activation_required"] is True
