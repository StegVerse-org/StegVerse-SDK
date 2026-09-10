import copy

import pytest

from stegverse.security_posture import instantiate_task_security_posture
from stegverse.security_posture_binding import bind_task_security_posture_instance


def instance():
    return instantiate_task_security_posture(
        task_id="INTR-SENSITIVE-1",
        requested_tier="SECURE",
        organization_minimum_tier="SECURE",
        data_class="ePHI",
        issued_at="2026-09-10T16:00:00Z",
        ttl_seconds=900,
    )


def test_binding_projects_exact_active_posture_instance_and_definition_version():
    value = instance()
    binding = bind_task_security_posture_instance(
        value, task_id="INTR-SENSITIVE-1", observed_at="2026-09-10T16:01:00Z"
    )
    assert binding["schema"] == "stegverse.sdk.security-posture-instance-binding.v1"
    assert binding["instance_id"] == value["instance_id"]
    assert len(binding["instance_sha256"]) == 64
    assert binding["posture_id"] == "stegverse.security.health-pii-high.v1"
    assert binding["posture_version"] == 1
    assert binding["effective_tier"] == "HIGHEST"
    assert binding["transferable"] is False
    assert binding["reusable_across_tasks"] is False
    assert binding["authority_effect"] == "NONE_ADMISSION_EVIDENCE_ONLY"


def test_mutated_instance_produces_different_exact_binding_digest():
    first = instance()
    second = copy.deepcopy(first)
    second["channel"] = "SDK-ALT"
    a = bind_task_security_posture_instance(
        first, task_id="INTR-SENSITIVE-1", observed_at="2026-09-10T16:01:00Z"
    )
    b = bind_task_security_posture_instance(
        second, task_id="INTR-SENSITIVE-1", observed_at="2026-09-10T16:01:00Z"
    )
    assert a["instance_sha256"] != b["instance_sha256"]


def test_cross_task_and_expired_instances_fail_closed_before_binding():
    value = instance()
    with pytest.raises(ValueError, match="task_mismatch"):
        bind_task_security_posture_instance(
            value, task_id="OTHER-TASK", observed_at="2026-09-10T16:01:00Z"
        )
    with pytest.raises(ValueError, match="instance_expired"):
        bind_task_security_posture_instance(
            value, task_id="INTR-SENSITIVE-1", observed_at="2026-09-10T16:15:00Z"
        )
