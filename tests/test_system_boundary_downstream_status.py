from copy import deepcopy

from stegverse.system_boundary_downstream_status import build_downstream_status_packet


ADAPTER_PENDING = {
    "schema_version": "stegverse.system_boundary.workflow_evidence.v0.1",
    "repository": "StegVerse-org/LLM-adapter",
    "workflow": ".github/workflows/validate.yml",
    "required_commit": "cf5bbe3b9b343600d27c249a02a40fe96c37e61e",
    "observed_commit": None,
    "run_id": None,
    "run_url": None,
    "result": "PENDING",
    "production_binding_enabled": False,
    "release_authorized": False,
}

SDK_PENDING = {
    "schema_version": "stegverse.system_boundary.workflow_evidence.v0.1",
    "repository": "StegVerse-org/StegVerse-SDK",
    "workflow": ".github/workflows/sdk-demo-test.yml",
    "required_commit": "1e1d58d8da3327c2e7efd1f33c43eca3810cce07",
    "observed_commit": None,
    "run_id": None,
    "run_url": None,
    "result": "PENDING",
    "production_binding_enabled": False,
    "release_authorized": False,
}


def as_pass(record, run_id):
    result = deepcopy(record)
    result.update(
        {
            "observed_commit": result["required_commit"],
            "run_id": run_id,
            "run_url": f"https://github.com/StegVerse-org/run/{run_id}",
            "result": "PASS",
        }
    )
    return result


def test_pending_packet_is_status_only_and_not_propagating():
    result = build_downstream_status_packet(ADAPTER_PENDING, SDK_PENDING)
    assert result.accepted is True
    assert result.packet["activation_state"] == "PENDING"
    assert result.packet["verified"] is False
    assert result.packet["downstream_propagation_allowed"] is False
    assert result.packet["status_only"] is True


def test_one_pass_cannot_enable_propagation():
    result = build_downstream_status_packet(as_pass(ADAPTER_PENDING, "adapter-1"), SDK_PENDING)
    assert result.accepted is True
    assert result.packet["downstream_propagation_allowed"] is False


def test_both_pass_enable_status_propagation_only():
    result = build_downstream_status_packet(
        as_pass(ADAPTER_PENDING, "adapter-1"),
        as_pass(SDK_PENDING, "sdk-1"),
    )
    assert result.accepted is True
    assert result.packet["activation_state"] == "VERIFIED"
    assert result.packet["verified"] is True
    assert result.packet["downstream_propagation_allowed"] is True
    assert result.packet["status_only"] is True
    assert result.packet["production_binding_enabled"] is False
    assert result.packet["release_authorized"] is False
    assert result.packet["execution_authority_granted"] is False
    assert result.packet["custody_transferred"] is False
    assert result.packet["admissibility_determined"] is False


def test_invalid_evidence_emits_no_packet():
    invalid = deepcopy(SDK_PENDING)
    invalid["release_authorized"] = True
    result = build_downstream_status_packet(ADAPTER_PENDING, invalid)
    assert result.accepted is False
    assert result.packet == {}
