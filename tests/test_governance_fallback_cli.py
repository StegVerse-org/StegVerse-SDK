from unittest.mock import patch

from stegverse.cli import main


def test_governance_cli_exposes_canonical_fallback_without_rewriting_result(capsys):
    canonical = {
        "governance_state": "REVIEW",
        "manifest_receipt_id": "MR-ABCDEF0123456789",
        "transaction_id": "TX-1",
        "route_receipt_chain_head": "sha256:head",
    }
    with patch("stegverse.governance_fallback.execute_fallback", return_value=canonical) as execute:
        rc = main([
            "governance",
            "--fallback-operation", "run",
            "--fallback-target", "request.json",
        ])
    assert rc == 0
    output = capsys.readouterr().out
    assert '"governance_state": "REVIEW"' in output
    assert '"manifest_receipt_id": "MR-ABCDEF0123456789"' in output
    execute.assert_called_once()


def test_governance_cli_requires_fallback_target(capsys):
    rc = main(["governance", "--fallback-operation", "run"])
    assert rc == 2
    assert "--fallback-target is required" in capsys.readouterr().out
