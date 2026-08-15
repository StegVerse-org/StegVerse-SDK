from unittest.mock import Mock, patch

from stegverse.cli import main


def _ops(*, submit=None, replay=None, reconstruct=None):
    value = Mock()
    value.submit.side_effect = submit
    value.replay.side_effect = replay
    value.reconstruct.side_effect = reconstruct
    return value


def test_option_0_executes_canonical_operation_when_input_is_supplied(capsys):
    canonical = {
        "governance_state": "ALLOW",
        "manifest_receipt_id": "MR-ABCDEF0123456789",
        "transaction_id": "TX-1",
        "route_receipt_chain_head": "sha256:head",
    }
    operations = _ops(submit=lambda request: canonical)
    with patch("stegverse.cli._canonical_governed_operations", return_value=operations), patch(
        "stegverse.public_inspection.load_public_inspection_request", return_value={"schema_version": "1.0"}
    ):
        rc = main(["governance", "--select", "0", "--input", "request.json"])
    assert rc == 0
    assert '"governance_state": "ALLOW"' in capsys.readouterr().out
    operations.submit.assert_called_once_with({"schema_version": "1.0"})


def test_option_1_executes_replay_by_manifest_receipt_id(capsys):
    canonical = {
        "manifest_receipt_id": "MR-ABCDEF0123456789",
        "replay_disposition": "DENY",
        "consequence_reexecuted": False,
    }
    operations = _ops(replay=lambda receipt_id: canonical)
    with patch("stegverse.cli._canonical_governed_operations", return_value=operations):
        rc = main([
            "governance", "--select", "1",
            "--manifest-receipt-id", "MR-ABCDEF0123456789",
        ])
    assert rc == 0
    assert '"replay_disposition": "DENY"' in capsys.readouterr().out
    operations.replay.assert_called_once_with("MR-ABCDEF0123456789")


def test_option_2_executes_reconstruction_by_manifest_receipt_id(capsys):
    canonical = {
        "manifest_receipt_id": "MR-ABCDEF0123456789",
        "operation_transition_custody_status": "RECORDED",
        "consequence_reexecuted": False,
    }
    operations = _ops(reconstruct=lambda receipt_id: canonical)
    with patch("stegverse.cli._canonical_governed_operations", return_value=operations):
        rc = main([
            "governance", "--select", "2",
            "--manifest-receipt-id", "MR-ABCDEF0123456789",
        ])
    assert rc == 0
    assert '"operation_transition_custody_status": "RECORDED"' in capsys.readouterr().out
    operations.reconstruct.assert_called_once_with("MR-ABCDEF0123456789")


def test_option_0_without_input_remains_guidance_not_false_execution(capsys):
    operations = Mock()
    with patch("stegverse.cli._canonical_governed_operations", return_value=operations):
        rc = main(["governance", "--select", "0"])
    assert rc == 0
    assert "Execute current canonical 0A request" in capsys.readouterr().out
    operations.submit.assert_not_called()


def test_option_0b_is_not_invented_by_the_cli(capsys):
    rc = main(["governance", "--select", "0"])
    assert rc == 0
    assert "0B execution remains fail-closed" in capsys.readouterr().out
