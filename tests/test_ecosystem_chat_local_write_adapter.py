from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer
from stegverse.ecosystem_chat_local_write_adapter import LocalEcosystemChatWriteAdapter
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline


def test_local_write_adapter_completes_when_injected():
    first = run_ecosystem_chat_pipeline(
        payload(),
        issuer=LocalGovernedEcosystemChatIssuer(),
        write_adapter=LocalEcosystemChatWriteAdapter(),
    )
    second = run_ecosystem_chat_pipeline(
        payload(),
        issuer=LocalGovernedEcosystemChatIssuer(),
        write_adapter=LocalEcosystemChatWriteAdapter(),
    )

    assert first["issuer_result"]["issued"] is True
    assert first["write_result"]["write_complete"] is True
    assert first["write_result"]["write_id"] == second["write_result"]["write_id"]
    assert first["write_result"]["write_id"].startswith("ecw-local-")
    assert first["write_result"]["receipt_id"] == first["issuer_result"]["receipt_id"]


def test_default_pipeline_still_does_not_write():
    result = run_ecosystem_chat_pipeline(payload())

    assert result["write_result"]["write_complete"] is False
    assert result["write_result"]["write_id"] is None


def test_local_write_adapter_blocks_invalid_payload():
    data = payload()
    data["manifest"]["user_request"] = "changed"
    result = run_ecosystem_chat_pipeline(
        data,
        issuer=LocalGovernedEcosystemChatIssuer(),
        write_adapter=LocalEcosystemChatWriteAdapter(),
    )

    assert result["write_result"]["write_complete"] is False
    assert result["write_result"]["write_id"] is None
    assert result["write_result"]["errors"]
