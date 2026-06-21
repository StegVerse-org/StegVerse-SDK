from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer
from stegverse.ecosystem_chat_persistence_plan import (
    PERSISTENCE_BLOCKED,
    PERSISTENCE_PENDING,
    build_persistence_plan,
)
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline


def test_persistence_plan_blocks_default_receiptless_export():
    result = run_ecosystem_chat_pipeline(payload())
    plan = build_persistence_plan(result["record_export"]).to_dict()

    assert plan["persistence_status"] == PERSISTENCE_BLOCKED
    assert plan["receipt_id"] is None
    assert plan["external_write_complete"] is False
    assert plan["errors"]


def test_persistence_plan_pending_with_injected_local_receipt():
    result = run_ecosystem_chat_pipeline(payload(), issuer=LocalGovernedEcosystemChatIssuer())
    plan = build_persistence_plan(result["record_export"]).to_dict()

    assert plan["persistence_status"] == PERSISTENCE_PENDING
    assert plan["receipt_id"] == result["issuer_result"]["receipt_id"]
    assert plan["export_hash"].startswith("sha256:")
    assert plan["persistence_hash"].startswith("sha256:")
    assert plan["external_write_complete"] is False
    assert plan["errors"] == []


def test_persistence_plan_is_deterministic():
    first_result = run_ecosystem_chat_pipeline(payload(), issuer=LocalGovernedEcosystemChatIssuer())
    second_result = run_ecosystem_chat_pipeline(payload(), issuer=LocalGovernedEcosystemChatIssuer())

    first = build_persistence_plan(first_result["record_export"]).to_dict()
    second = build_persistence_plan(second_result["record_export"]).to_dict()

    assert first["persistence_hash"] == second["persistence_hash"]
