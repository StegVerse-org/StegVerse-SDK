import pytest

from stegverse.security_posture import SecurityPostureError
from stegverse.security_posture_stack import build_security_posture_request, project_intr_posture_resolution, select_posture_stack

TASK = "FEDERAL-HEALTH-PII-EXCEEDANCE-HARDENING-001"


def test_sdk_request_carries_inputs_not_authoritative_final_posture():
    result = build_security_posture_request(task_id=TASK, selected_tier="HIGHEST", data_class="PII", channel="KV-SKAP")
    assert result["selected_tier"] == "HIGHEST"
    assert result["authoritative_automatic_posture"] is None
    assert result["authoritative_effective_posture"] is None
    assert result["resolution_authority"] == "INTERLOCK_INTR"
    assert result["authority_effect"] == "NONE_REQUEST_INPUT_ONLY"


def test_preview_does_not_compute_automatic_or_effective_posture():
    result = select_posture_stack(task_id=TASK, data_class="PII", selected_tier="HIGHEST")
    assert result["automatic_posture"] is None
    assert result["effective_posture"] is None
    assert result["selected_posture"]["tier"] == "HIGHEST"
    assert result["resolution_required_from"] == "INTERLOCK_INTR"


def test_projection_preserves_intr_result_without_reinterpretation():
    resolution = {
        "schema": "stegos.intr-security-posture-resolution.v1",
        "automatic_posture": {"tier": "HIGH", "posture_id": "stegverse.security.high.v1"},
        "selected_posture": {"tier": "HIGHEST", "posture_id": "stegverse.security.health-pii-high.v1"},
        "effective_posture": {"tier": "HIGHEST", "posture_id": "stegverse.security.health-pii-high.v1"},
        "posture_instance": {"instance_id": "INTR-SP-example", "instance_sha256": "abc"},
        "resolution_authority": "INTERLOCK_INTR",
        "credential_authority": "TV/TVC",
    }
    projected = project_intr_posture_resolution(resolution)
    assert projected["automatic_posture"]["tier"] == "HIGH"
    assert projected["selected_posture"]["tier"] == "HIGHEST"
    assert projected["effective_posture"]["tier"] == "HIGHEST"
    assert projected["sdk_reinterpreted_posture"] is False


def test_projection_rejects_invalid_downgrade_from_intr_result():
    resolution = {
        "schema": "stegos.intr-security-posture-resolution.v1",
        "automatic_posture": {"tier": "HIGHEST", "posture_id": "stegverse.security.health-pii-high.v1"},
        "selected_posture": {"tier": "HIGH", "posture_id": "stegverse.security.high.v1"},
        "effective_posture": {"tier": "HIGHEST", "posture_id": "stegverse.security.health-pii-high.v1"},
        "posture_instance": {},
        "resolution_authority": "INTERLOCK_INTR",
    }
    with pytest.raises(SecurityPostureError, match="contains_downgrade"):
        project_intr_posture_resolution(resolution)
