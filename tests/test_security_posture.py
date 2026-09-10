import copy

import pytest

from stegverse.security_posture import (
    ATTESTATION_SCHEMA,
    HEALTH_PII_HIGH_V1,
    SecurityPostureError,
    attach_security_posture,
    resolve_security_posture,
    validate_runtime_attestation,
)


def _attestation():
    posture = resolve_security_posture("stegverse.security.health-pii-high.v1")
    return {
        "schema": ATTESTATION_SCHEMA,
        "posture_id": posture["posture_id"],
        "posture_sha256": posture["posture_sha256"],
        "observed_requirements": copy.deepcopy(posture["requirements"]),
        "observed_prohibitions": copy.deepcopy(posture["prohibitions"]),
    }


def test_current_health_pii_posture_is_resolvable_and_versioned():
    posture = resolve_security_posture("stegverse.security.health-pii-high.v1")
    assert posture["version"] == 1
    assert posture["upgrade_policy"]["allow_silent_downgrade"] is False
    assert posture["requirements"]["credential_authority"] == "TV/TVC"
    assert posture["requirements"]["encryption_at_rest"] is True
    assert posture["requirements"]["encryption_in_transit"] is True


def test_manifest_gets_reference_not_experiment_specific_security_fields():
    manifest = {"schema": "example", "extensions": {}, "data": {"opaque": True}}
    attached = attach_security_posture(manifest, "stegverse.security.health-pii-high.v1")
    ref = attached["extensions"]["security_posture"]
    assert ref["posture_id"] == "stegverse.security.health-pii-high.v1"
    assert "requirements" not in ref
    assert attached["data"] == {"opaque": True}


def test_full_attestation_is_admitted():
    result = validate_runtime_attestation("stegverse.security.health-pii-high.v1", _attestation())
    assert result["status"] == "POSTURE_SATISFIED"
    assert result["silent_downgrade_allowed"] is False


@pytest.mark.parametrize(
    "field",
    [
        "minimum_necessary_manifest",
        "payload_digest_binding",
        "encryption_in_transit",
        "encryption_at_rest",
        "audit_receipt_required",
        "automatic_disposition",
        "fresh_runtime_root",
        "predecessor_authority_rejected",
    ],
)
def test_required_control_failure_is_fail_closed(field):
    value = _attestation()
    value["observed_requirements"][field] = False
    with pytest.raises(SecurityPostureError, match=f"posture_requirement_unsatisfied:{field}"):
        validate_runtime_attestation("stegverse.security.health-pii-high.v1", value)


def test_longer_retention_is_rejected_but_stronger_shorter_retention_is_allowed():
    value = _attestation()
    value["observed_requirements"]["retention_max_hours"] = 25
    with pytest.raises(SecurityPostureError, match="retention_max_hours"):
        validate_runtime_attestation("stegverse.security.health-pii-high.v1", value)

    value = _attestation()
    value["observed_requirements"]["retention_max_hours"] = 1
    assert validate_runtime_attestation("stegverse.security.health-pii-high.v1", value)["status"] == "POSTURE_SATISFIED"


def test_unenforced_prohibition_and_unknown_posture_fail_closed():
    value = _attestation()
    value["observed_prohibitions"]["model_training"] = False
    with pytest.raises(SecurityPostureError, match="posture_prohibition_not_enforced:model_training"):
        validate_runtime_attestation("stegverse.security.health-pii-high.v1", value)

    with pytest.raises(SecurityPostureError, match="unsupported_security_posture"):
        resolve_security_posture("stegverse.security.health-pii-high.v99")
