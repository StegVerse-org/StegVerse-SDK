from pathlib import Path


def test_deployment_readiness_manifest_contains_required_markers():
    text = Path("docs/ECOSYSTEM_CHAT_DEPLOYMENT_READINESS.md").read_text(encoding="utf-8")

    assert "python scripts/run_ecosystem_chat_service.py" in text
    assert "stegverse.ecosystem_chat_wsgi:application" in text
    assert "POST /api/ecosystem-chat" in text
    assert "intake" in text
    assert "receipt_decision" in text
    assert "record_export" in text
    assert "Hosted service target: not selected" in text
    assert "Receipt issuer: not installed" in text
