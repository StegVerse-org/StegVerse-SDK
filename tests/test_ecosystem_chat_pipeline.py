from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline


def test_pipeline_returns_all_current_stage_outputs():
    result = run_ecosystem_chat_pipeline(payload())

    assert set(result) == {"intake", "receipt_decision", "issuer_result", "record_export"}
    assert result["intake"]["accepted"] is True
    assert result["intake"]["receipt_id"] is None
    assert result["receipt_decision"]["receipt_id"] is None
    assert result["issuer_result"]["issued"] is False
    assert result["issuer_result"]["receipt_id"] is None
    assert result["record_export"]["receipt_id"] is None
    assert result["record_export"]["external_write_complete"] is False


def test_pipeline_rejects_drift_consistently_across_stages():
    data = payload()
    data["manifest"]["user_request"] = "changed"
    result = run_ecosystem_chat_pipeline(data)

    assert result["intake"]["accepted"] is False
    assert result["receipt_decision"]["errors"]
    assert result["issuer_result"]["issued"] is False
    assert result["record_export"]["errors"]
