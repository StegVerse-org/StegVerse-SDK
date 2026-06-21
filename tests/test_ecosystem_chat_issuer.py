from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_issuer import IssuerResult, issue_with_governed_issuer
from stegverse.ecosystem_chat_receipt_engine import evaluate_ecosystem_chat_payload_for_receipt


class TestIssuer:
    def issue(self, receipt_decision):
        return IssuerResult(
            issued=True,
            receipt_id="test-receipt-001",
            issuer_name="TEST_ISSUER",
            errors=[],
        )


def test_default_issuer_fails_closed():
    decision = evaluate_ecosystem_chat_payload_for_receipt(payload())
    result = issue_with_governed_issuer(decision)

    assert result["issued"] is False
    assert result["receipt_id"] is None
    assert result["issuer_name"] == "DISABLED_ECOSYSTEM_CHAT_ISSUER"
    assert result["errors"]


def test_explicit_issuer_can_satisfy_interface():
    decision = evaluate_ecosystem_chat_payload_for_receipt(payload())
    result = issue_with_governed_issuer(decision, TestIssuer())

    assert result == {
        "issued": True,
        "receipt_id": "test-receipt-001",
        "issuer_name": "TEST_ISSUER",
        "errors": [],
    }
