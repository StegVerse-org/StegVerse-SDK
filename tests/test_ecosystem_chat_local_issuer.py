from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline


def test_local_issuer_generates_deterministic_receipt_id_when_injected():
    issuer = LocalGovernedEcosystemChatIssuer()

    first = run_ecosystem_chat_pipeline(payload(), issuer=issuer)
    second = run_ecosystem_chat_pipeline(payload(), issuer=issuer)

    assert first["issuer_result"]["issued"] is True
    assert first["issuer_result"]["receipt_id"] == second["issuer_result"]["receipt_id"]
    assert first["issuer_result"]["receipt_id"].startswith("ecr-local-")
    assert first["record_export"]["receipt_id"] == first["issuer_result"]["receipt_id"]
    assert first["record_export"]["external_write_complete"] is False


def test_default_pipeline_still_does_not_issue():
    result = run_ecosystem_chat_pipeline(payload())

    assert result["issuer_result"]["issued"] is False
    assert result["issuer_result"]["receipt_id"] is None
    assert result["record_export"]["receipt_id"] is None


def test_local_issuer_blocks_invalid_decision():
    data = payload()
    data["manifest"]["declared_goal"] = "changed"
    result = run_ecosystem_chat_pipeline(data, issuer=LocalGovernedEcosystemChatIssuer())

    assert result["issuer_result"]["issued"] is False
    assert result["issuer_result"]["receipt_id"] is None
    assert result["record_export"]["receipt_id"] is None
    assert result["issuer_result"]["errors"]
