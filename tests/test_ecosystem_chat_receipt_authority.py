from stegverse.ecosystem_chat_receipt_authority import get_receipt_authority_status


def test_receipt_authority_is_pending_by_default():
    status = get_receipt_authority_status()
    assert status.authority_installed is False
    assert status.receipt_issuance_enabled is False
    assert status.authority_name == "SDK_RECEIPT_AUTHORITY_PENDING"
