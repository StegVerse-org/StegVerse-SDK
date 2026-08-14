import pytest

from stegverse.governed_operations import GovernedOperationError, GovernedOperations


class Recorder:
    def __init__(self):
        self.calls = []

    def __call__(self, choice_code, **kwargs):
        self.calls.append((choice_code, kwargs))


def test_submit_records_only_after_run_identity_is_present():
    recorder = Recorder()
    result = {
        "manifest_receipt_id": "MR-ABCDEF0123456789",
        "transaction_id": "TX-1",
        "receipt_chain_head": "sha256:head",
    }
    operations = GovernedOperations(
        submit_handler=lambda value: result,
        replay_handler=lambda value: {},
        reconstruct_handler=lambda value: {},
        usage_recorder=recorder,
    )
    assert operations.submit({"payload": "x"}) == result
    code, call = recorder.calls[-1]
    assert code == "0"
    assert call["phase"] == "COMPLETED"
    assert call["manifest_receipt_id"] == result["manifest_receipt_id"]
    assert call["transaction_id"] == result["transaction_id"]
    assert call["receipt_chain_head"] == result["receipt_chain_head"]


def test_submit_failure_is_not_counted_as_completed():
    recorder = Recorder()
    operations = GovernedOperations(
        submit_handler=lambda value: {"manifest_receipt_id": "MR-X"},
        replay_handler=lambda value: {},
        reconstruct_handler=lambda value: {},
        usage_recorder=recorder,
    )
    with pytest.raises(GovernedOperationError):
        operations.submit({"payload": "x"})
    assert recorder.calls == [("0", {"phase": "FAILED", "source": "sdk-governed-operations:submit"})]


def test_replay_requires_same_locator_and_no_consequence_reexecution():
    recorder = Recorder()
    locator = "MR-ABCDEF0123456789"
    replay_result = {
        "original_manifest_receipt_id": locator,
        "original_transaction_id": "TX-1",
        "original_receipt_chain_head": "sha256:head",
        "consequence_reexecuted": False,
    }
    operations = GovernedOperations(
        submit_handler=lambda value: {},
        replay_handler=lambda value: replay_result,
        reconstruct_handler=lambda value: {},
        usage_recorder=recorder,
    )
    assert operations.replay(locator.lower()) == replay_result
    code, call = recorder.calls[-1]
    assert code == "1"
    assert call["phase"] == "COMPLETED"
    assert call["manifest_receipt_id"] == locator
    assert call["consequence_reexecuted"] is False


def test_replay_mismatch_fails_and_records_failed_only():
    recorder = Recorder()
    operations = GovernedOperations(
        submit_handler=lambda value: {},
        replay_handler=lambda value: {
            "original_manifest_receipt_id": "MR-DIFFERENT",
            "consequence_reexecuted": False,
        },
        reconstruct_handler=lambda value: {},
        usage_recorder=recorder,
    )
    with pytest.raises(GovernedOperationError):
        operations.replay("MR-ABCDEF0123456789")
    assert len(recorder.calls) == 1
    assert recorder.calls[0][0] == "1"
    assert recorder.calls[0][1]["phase"] == "FAILED"


def test_reconstruction_requires_non_reexecution_proof():
    recorder = Recorder()
    locator = "MR-ABCDEF0123456789"
    operations = GovernedOperations(
        submit_handler=lambda value: {},
        replay_handler=lambda value: {},
        reconstruct_handler=lambda value: {
            "original_manifest_receipt_id": locator,
            "transaction_id": "TX-1",
            "consequence_reexecuted": False,
        },
        usage_recorder=recorder,
    )
    result = operations.reconstruct(locator)
    assert result["consequence_reexecuted"] is False
    assert recorder.calls[-1][0] == "2"
    assert recorder.calls[-1][1]["phase"] == "COMPLETED"
    assert recorder.calls[-1][1]["consequence_reexecuted"] is False


def test_reconstruction_claiming_side_effect_reexecution_fails_closed():
    recorder = Recorder()
    locator = "MR-ABCDEF0123456789"
    operations = GovernedOperations(
        submit_handler=lambda value: {},
        replay_handler=lambda value: {},
        reconstruct_handler=lambda value: {
            "original_manifest_receipt_id": locator,
            "transaction_id": "TX-1",
            "consequence_reexecuted": True,
        },
        usage_recorder=recorder,
    )
    with pytest.raises(GovernedOperationError):
        operations.reconstruct(locator)
    assert len(recorder.calls) == 1
    assert recorder.calls[0][0] == "2"
    assert recorder.calls[0][1]["phase"] == "FAILED"
    assert recorder.calls[0][1]["consequence_reexecuted"] is False
