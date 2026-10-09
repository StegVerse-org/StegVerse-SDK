from unittest.mock import Mock, patch

from stegverse.cli import main


def _ops(*, submit=None, replay=None, reconstruct=None):
    value = Mock()
    value.submit.side_effect = submit
    value.replay.side_effect = replay
    value.reconstruct.side_effect = reconstruct
    return value


def test_option_0_builds_manifest_and_submits_through_canonical_entrypoint(capsys):
    # SDK#368: option 0/0A input is raw data for the SDK Manifest Builder; the
    # built manifest goes to the canonical manifest-route-selected entrypoint.
    built = {"manifest_profile": "stegverse.ingress-manifest.v1"}
    handoff = {"disposition": "ALLOW", "state": "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF"}
    with patch("stegverse.cli._build_0a_manifest", return_value=built), patch(
        "stegverse.manifest_contract.validate_ingress_manifest", return_value={"canonical_manifest_sha256": "a" * 64}
    ), patch(
        # SDK#368: the draft is qualified before dispatch; readiness is covered
        # by tests/test_manifest_readiness_gate.py.
        "stegverse.manifest_builder.qualify_draft_manifest",
        return_value={"state": "READY", "executable": True, "qualification": {"qualification": "READY"}},
    ), patch("stegverse.manifest_plan.require_ready_qualification"), patch(
        "stegverse.manifest_execution.execute_manifest", return_value=handoff
    ) as execute:
        rc = main(["governance", "--select", "0", "--input", "request.json"])
    assert rc == 0
    output = capsys.readouterr().out
    assert '"state": "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF"' in output
    assert '"canonical_entrypoint": "stegverse.manifest_execution.execute_manifest"' in output
    execute.assert_called_once_with(built)


def test_option_1_executes_replay_by_manifest_receipt_id(capsys):
    canonical = {
        "manifest_receipt_id": "MR-ABCDEF0123456789",
        "replay_disposition": "DENY",
        "consequence_reexecuted": False,
    }
    operations = _ops(replay=lambda receipt_id: canonical)
    with patch("stegverse.cli._local_enclosed_operations", return_value=operations):
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
    with patch("stegverse.cli._local_enclosed_operations", return_value=operations):
        rc = main([
            "governance", "--select", "2",
            "--manifest-receipt-id", "MR-ABCDEF0123456789",
        ])
    assert rc == 0
    assert '"operation_transition_custody_status": "RECORDED"' in capsys.readouterr().out
    operations.reconstruct.assert_called_once_with("MR-ABCDEF0123456789")


def test_option_0_without_input_remains_guidance_not_false_execution(capsys):
    operations = Mock()
    with patch("stegverse.cli._local_enclosed_operations", return_value=operations):
        rc = main(["governance", "--select", "0"])
    assert rc == 0
    assert "Execute current canonical 0A request" in capsys.readouterr().out
    operations.submit.assert_not_called()


def test_option_0b_is_not_invented_by_the_cli(capsys):
    rc = main(["governance", "--select", "0"])
    assert rc == 0
    assert "0B execution remains fail-closed" in capsys.readouterr().out
