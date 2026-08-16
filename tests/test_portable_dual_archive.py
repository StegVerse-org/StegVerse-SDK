import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

from stegverse.portable_packages import install_archive, verify_archive


def receipt_and_payload(deployment_class="S"):
    package_id = "stegverse-sdk-s-micro-ecosystem-v0" if deployment_class == "S" else "stegverse-sdk-ns-micro-ecosystem-v0"
    payload = b'{"fixture":"portable"}\n'
    receipt = {
        "schema": "stegverse.sdk.portable-package-receipt.v1",
        "channel": "SDK_EARLY_ACCESS",
        "package_id": package_id,
        "deployment_class": deployment_class,
        "source_commit": "a" * 40,
        "required_archive_formats": ["zip", "tar.gz"],
        "node_membership_claim": False,
        "node_membership_activation_required": deployment_class == "NS",
        "files": [{"path": "micro_ecosystem/fixture.json", "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}],
        "requires_provider_account": False,
        "requires_non_tv_tvc_secret": False,
    }
    return package_id, payload, json.dumps(receipt, sort_keys=True).encode()


def build_pair(tmp_path: Path, deployment_class="S"):
    package_id, payload, receipt = receipt_and_payload(deployment_class)
    zip_path = tmp_path / f"{package_id}.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("micro_ecosystem/fixture.json", payload)
        zf.writestr("PACKAGE_RECEIPT.json", receipt)
    tar_path = tmp_path / f"{package_id}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        for name, data in (("micro_ecosystem/fixture.json", payload), ("PACKAGE_RECEIPT.json", receipt)):
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
    assert zip_result["package_id"] == tar_result["package_id"]
    assert zip_result["deployment_class"] == tar_result["deployment_class"] == "S"
    assert zip_result["verified_files"] == tar_result["verified_files"]


def test_tar_gz_ns_install_remains_not_activated(tmp_path):
    _, tar_path = build_pair(tmp_path, "NS")
    installed = install_archive(tar_path, tmp_path / "installed")
    assert installed["archive_format"] == "tar.gz"
    assert installed["installation_state"] == "INSTALLED_NOT_ACTIVATED"
    assert installed["node_membership_granted"] is False
    assert installed["node_membership_activation_required"] is True
