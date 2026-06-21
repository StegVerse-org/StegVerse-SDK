from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline
from stegverse.ecosystem_chat_write_adapter import WriteResult


class TestWriteAdapter:
    def write(self, persistence_plan):
        return WriteResult(
            write_complete=True,
            write_id="test-write-001",
            adapter_name="TEST_WRITE_ADAPTER",
            receipt_id=persistence_plan["receipt_id"],
            errors=[],
        )


def test_pipeline_returns_all_current_stage_outputs():
    result = run_ecosystem_chat_pipeline(payload())

    assert set(result) == {
        "intake",
        "receipt_decision",
        "issuer_result",
        "record_export",
        "persistence_plan",
        "destination_binding",
        "write_result",
    }
    assert result["intake"]["accepted"] is True
    assert result["intake"]["receipt_id"] is None
    assert result["receipt_decision"]["receipt_id"] is None
    assert result["issuer_result"]["issued"] is False
    assert result["issuer_result"]["receipt_id"] is None
    assert result["record_export"]["receipt_id"] is None
    assert result["record_export"]["external_write_complete"] is False
    assert result["persistence_plan"]["external_write_complete"] is False
    assert result["destination_binding"]["binding_status"] == "DESTINATION_DISABLED"
    assert result["write_result"]["write_complete"] is False


def test_pipeline_rejects_drift_consistently_across_stages():
    data = payload()
    data["manifest"]["user_request"] = "changed"
    result = run_ecosystem_chat_pipeline(data)

    assert result["intake"]["accepted"] is False
    assert result["receipt_decision"]["errors"]
    assert result["issuer_result"]["issued"] is False
    assert result["record_export"]["errors"]
    assert result["persistence_plan"]["errors"]
    assert result["destination_binding"]["binding_status"] == "DESTINATION_DISABLED"
    assert result["write_result"]["write_complete"] is False


def test_pipeline_can_use_explicit_write_adapter():
    from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer

    result = run_ecosystem_chat_pipeline(
        payload(),
        issuer=LocalGovernedEcosystemChatIssuer(),
        write_adapter=TestWriteAdapter(),
    )

    assert result["issuer_result"]["issued"] is True
    assert result["persistence_plan"]["persistence_status"] == "PERSISTENCE_PENDING"
    assert result["write_result"]["write_complete"] is True
    assert result["write_result"]["receipt_id"] == result["issuer_result"]["receipt_id"]


def test_pipeline_accepts_destination_config():
    result = run_ecosystem_chat_pipeline(
        payload(),
        destination_config={
            "destination_name": "master-records/ecosystem-chat",
            "destination_type": "master-records",
        },
    )

    assert result["destination_binding"]["binding_status"] == "DESTINATION_READY"
    assert result["destination_binding"]["binding_hash"].startswith("sha256:")
