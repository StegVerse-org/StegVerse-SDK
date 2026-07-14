from copy import deepcopy

from stegverse.system_boundary_activation import evaluate_system_boundary_activation


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
    "required_commit": "b73d3b59803ae0443277c03aeb5801a28c34d335",
    "observed_commit": None,
    "run_id": None,
    "run_url": None,
    "result": "PENDING",
    "production_binding_enabled": False,
    "release_authorized": False,
}


def as_pass(record, repo):
    result = deepcopy(record)
    result.update(
        {
            "observed_commit": result["required_commit"],
            "run_id": f"{repo}-run-001",
            "run_url": f"https://github.com/StegVerse-org/{repo}/actions/runs/1",
            "result": "PASS",
        }
    )
    return result


def test_pending_plus_pending_is_not_verified():
    result = evaluate_system_boundary_activation(ADAPTER_PENDING, SDK_PENDING)
    assert result.accepted is True
    assert result.verified is False
    assert result.state == "PENDING"


def test_one_pass_is_still_pending():
    result = evaluate_system_boundary_activation(as_pass(ADAPTER_PENDING, "LLM-adapter"), SDK_PENDING)
    assert result.accepted is True
    assert result.verified is False
    assert result.state == "PENDING"


def test_both_exact_pass_records_are_verified():
    result = evaluate_system_boundary_activation(
        as_pass(ADAPTER_PENDING, "LLM-adapter"),
        as_pass(SDK_PENDING, "StegVerse-SDK"),
    )
    assert result.accepted is True
    assert result.verified is True
    assert result.state == "VERIFIED"


def test_failure_blocks_activation():
    sdk = deepcopy(SDK_PENDING)
    sdk.update(
        {
            "observed_commit": sdk["required_commit"],
            "run_id": "sdk-run-001",
            "run_url": "https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/1",
            "result": "FAIL",
        }
    )
    result = evaluate_system_boundary_activation(ADAPTER_PENDING, sdk)
    assert result.accepted is True
    assert result.verified is False
    assert result.state == "FAILED"


def test_authority_escalation_is_invalid_evidence():
    sdk = deepcopy(SDK_PENDING)
    sdk["release_authorized"] = True
    result = evaluate_system_boundary_activation(ADAPTER_PENDING, sdk)
    assert result.accepted is False
    assert result.verified is False
    assert result.state == "INVALID_EVIDENCE"
