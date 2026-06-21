# SDK Core-Node Parallel Fanout Run Log Template

## Purpose

Use this template to capture SDK→Core-Node fanout activation evidence when connector-visible CI evidence is unavailable.

## Command

```bash
python -m pytest
```

## Required run metadata

```text
repo: StegVerse-org/StegVerse-SDK
command: python -m pytest
runner: <local | GitHub Actions | external CI>
run_time_utc: <YYYY-MM-DDTHH:MM:SSZ>
commit: <commit sha>
exit_code: 0
```

## Required pass evidence

```text
fanout_goal_validator: PASS
fanout_request_validator: PASS
unified_comparison_receipt_validator: PASS
human_readable_comparison_result_validator: PASS
activation_status_validator: PASS
handoff_validator: PASS
ci_evidence_tracker_validator: PASS
```

## Required output evidence

The run output should show every SDK fanout test passed, including:

```text
test_sdk_core_node_fanout_goal.py
test_sdk_core_node_fanout_request.py
test_sdk_core_node_unified_comparison_receipt.py
test_sdk_core_node_result.py
test_fanout_status.py
test_fanout_handoff.py
test_fanout_ci_evidence.py
```

## Activation block

```text
sdk_core_node_parallel_fanout_activation_result: <PASS | FAIL>
command_exit_code: <0 | nonzero>
commit: <commit sha>
notes: <short note>
```

## Activation update after PASS

```text
1. Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_ACTIVATION_STATUS.json status from pre-activation to activated.
2. Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_GOAL.json status from started to activated.
3. Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_CI_EVIDENCE.md with the passing commit or external run log.
4. Close issue #1 as completed.
```
