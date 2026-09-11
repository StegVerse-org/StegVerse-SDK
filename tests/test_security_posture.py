import copy

import pytest

from stegverse.security_posture import (
    ATTESTATION_SCHEMA,
    HEALTH_PII_HIGH_V1,
    SecurityPostureError,
    attach_security_posture,
    instantiate_task_security_posture,
    resolve_security_posture,
    select_effective_posture,
    validate_runtime_attestation,
    validate_task_security_posture_instance,
)


def _attestation(posture_id="stegverse.security.health-pii-high.v1"):
    posture = resolve_security_posture(posture_id)
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
    assert posture["tier"] == "HIGHEST"
    assert posture["upgrade_policy"]["allow_silent_downgrade"] is False
    assert posture["requirements"]["credential_authority"] == "TV/TVC"
    assert posture["requirements"]["encryption_at_rest"] is True
    assert posture["requirements"]["encryption_in_transit"] is True


def test_manifest_gets_reference_not_experiment_specific_security_fields():
    manifest = {"schema": "example", "extensions": {}, "data": {"opaque": True}}
    attached = attach_security_posture(manifest, "stegverse.security.health-pii-high.v1")
    ref = attached["extensions"]["security_posture"]
    assert ref["posture_id"] == "stegverse.security.health-pii-high.v1"
    assert ref["tier"] == "HIGHEST"
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


def test_evaluator_can_select_secure_when_no_stronger_floor_applies():
    selected = select_effective_posture(
        requested_tier="SECURE",
        organization_minimum_tier="SECURE",
        data_class="general",
        channel="SDK",
    )
    assert selected["effective_tier"] == "SECURE"
    assert selected["posture_id"] == "stegverse.security.secure.v1"


def test_organization_minimum_elevates_evaluator_request():
    selected = select_effective_posture(
        requested_tier="SECURE",
        organization_minimum_tier="HIGH",
    )
    assert selected["effective_tier"] == "HIGH"
    assert selected["posture_id"] == "stegverse.security.high.v1"


def test_sensitive_data_elevates_posture_independent_of_evaluator_request():
    pii = select_effective_posture(requested_tier="SECURE", data_class="PII")
    ephi = select_effective_posture(requested_tier="SECURE", data_class="ePHI")
    assert pii["effective_tier"] == "HIGH"
    assert ephi["effective_tier"] == "HIGHEST"


def test_kv_skap_is_unconditionally_highest():
    selected = select_effective_posture(
        requested_tier="SECURE",
        organization_minimum_tier="SECURE",
        data_class="general",
        channel="KV-SKAP",
    )
    assert selected["effective_tier"] == "HIGHEST"
    assert selected["channel_minimum_tier"] == "HIGHEST"
    assert selected["posture_id"] == "stegverse.security.health-pii-high.v1"


def test_task_posture_instance_is_ephemeral_nontransferable_and_expires():
    instance = instantiate_task_security_posture(
        task_id="TASK-EVALUATOR-1",
        requested_tier="HIGH",
        organization_minimum_tier="SECURE",
        issued_at="2026-09-10T16:00:00Z",
        ttl_seconds=900,
    )
    assert instance["effective_tier"] == "HIGH"
    assert instance["transferable"] is False
    assert instance["reusable_across_tasks"] is False
    admitted = validate_task_security_posture_instance(
        instance, task_id="TASK-EVALUATOR-1", observed_at="2026-09-10T16:14:59Z"
    )
    assert admitted["status"] == "INSTANCE_ACTIVE"

    with pytest.raises(SecurityPostureError, match="task_mismatch"):
        validate_task_security_posture_instance(
            instance, task_id="TASK-EVALUATOR-2", observed_at="2026-09-10T16:01:00Z"
        )
    with pytest.raises(SecurityPostureError, match="instance_expired"):
        validate_task_security_posture_instance(
            instance, task_id="TASK-EVALUATOR-1", observed_at="2026-09-10T16:15:00Z"
        )


def test_ephemeral_posture_ttl_is_bounded():
    with pytest.raises(SecurityPostureError, match="ttl_out_of_bounds"):
        instantiate_task_security_posture(
            task_id="TASK-EVALUATOR-1",
            issued_at="2026-09-10T16:00:00Z",
            ttl_seconds=3601,
        )
