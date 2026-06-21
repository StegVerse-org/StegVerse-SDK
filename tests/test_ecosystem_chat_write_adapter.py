from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer
from stegverse.ecosystem_chat_persistence_plan import build_persistence_plan
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline
from stegverse.ecosystem_chat_write_adapter import WriteResult, write_with_adapter


class TestWriteAdapter:
    def write(self, persistence_plan):
        return WriteResult(
            write_complete=True,
            write_id="test-write-001",
            adapter_name="TEST_WRITE_ADAPTER",
            receipt_id=persistence_plan["receipt_id"],
            errors=[],
        )


def pending_plan():
    result = run_ecosystem_chat_pipeline(payload(), issuer=LocalGovernedEcosystemChatIssuer())
    return build_persistence_plan(result["record_export"]).to_dict()


def test_default_write_adapter_fails_closed():
    plan = pending_plan()
    result = write_with_adapter(plan)

    assert result["write_complete"] is False
    assert result["write_id"] is None
    assert result["adapter_name"] == "DISABLED_ECOSYSTEM_CHAT_WRITE_ADAPTER"
    assert result["receipt_id"] == plan["receipt_id"]
    assert result["errors"]


def test_explicit_write_adapter_can_satisfy_interface():
    plan = pending_plan()
    result = write_with_adapter(plan, TestWriteAdapter())

    assert result == {
        "write_complete": True,
        "write_id": "test-write-001",
        "adapter_name": "TEST_WRITE_ADAPTER",
        "receipt_id": plan["receipt_id"],
        "errors": [],
    }
