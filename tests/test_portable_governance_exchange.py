import json
from pathlib import Path
import zipfile

import pytest

from stegverse.portable_governance_exchange import (
    PortableGovernanceExchangeError,
    create_exchange,
    extract_bundle,
    verify_exchange,
)
from tests.test_portable_governance_verifier import _bundle


def test_create_verify_extract_round_trip(tmp_path: Path):
    archive = tmp_path / "governance-evidence.zip"
    created = create_exchange(_bundle(), archive)
    assert created["status"] == "CREATED"
    assert created["authority_effect"] == "NONE"

    verified = verify_exchange(archive)
    assert verified["status"] == "PASS"
    assert verified["stage"] == "PRE_STEGGATE"
    assert "VERIFICATION_REPORT_REPRODUCED" in verified["checks"]
    assert verified["authority"]["execution_authorized"] is False

    destination = tmp_path / "exchange"
    extracted = extract_bundle(archive, destination)
    assert extracted["status"] == "EXTRACTED_VERIFIED_NOT_IMPORTED_AS_CUSTODY"
    assert extracted["custody_installed"] is False
    assert (destination / "governance_bundle.json").is_file()
    assert (destination / "verification_report.json").is_file()
    assert (destination / "EXCHANGE_MANIFEST.json").is_file()


def test_tampered_bundle_member_fails_closed(tmp_path: Path):
    archive = tmp_path / "original.zip"
    create_exchange(_bundle(), archive)
    tampered = tmp_path / "tampered.zip"
    with zipfile.ZipFile(archive, "r") as source, zipfile.ZipFile(tampered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name == "governance_bundle.json":
                value = json.loads(data)
                value["run_id"] = "tampered"
                data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
            target.writestr(name, data)
    with pytest.raises(PortableGovernanceExchangeError, match="file_hash_mismatch"):
        verify_exchange(tampered)


def test_exchange_rejects_unverified_bundle(tmp_path: Path):
    bundle = _bundle()
    bundle["steggate_bridge"]["authority"]["execution_authorized"] = True
    with pytest.raises(ValueError):
        create_exchange(bundle, tmp_path / "should-not-exist.zip")
