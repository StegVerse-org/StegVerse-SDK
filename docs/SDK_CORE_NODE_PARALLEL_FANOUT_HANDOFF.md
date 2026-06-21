# SDK Core-Node Parallel Fanout Handoff

## Current goal

SDK intake to Core-Node parallel fanout with unified comparison receipt.

## Current status

```text
status: pre-activation
repo: StegVerse-org/StegVerse-SDK
issue: #1 SDK Core-Node parallel fanout activation evidence gate
```

## User loop

```text
user_submit_package
sdk_intake_validate
core_node_fanout_request
parallel_path_execution
unified_comparison_receipt
sdk_return_human_result
```

## Witness loop

```text
package_hash_observed
fanout_receipts_observed
comparison_receipt_observed
return_receipt_observed
```

The witness loop remains independent and uses master-records receipt references only.

## Command to run

```bash
python -m pytest
```

## Required pass evidence

```text
1. python -m pytest exits 0.
2. SDK fanout goal validator passes.
3. SDK fanout request validator passes.
4. SDK unified comparison receipt validator passes.
5. SDK human-readable comparison result validator passes.
6. SDK activation status validator passes.
```

## Required artifacts

```text
docs/SDK_CORE_NODE_PARALLEL_FANOUT_GOAL.json
docs/SDK_CORE_NODE_PARALLEL_FANOUT_ACTIVATION_STATUS.json
examples/sdk_core_node_fanout_request.sample.json
examples/sdk_core_node_unified_comparison_receipt.sample.json
examples/sdk_core_node_unified_comparison_result.sample.md
```

## Activation update after evidence

Once passing evidence is available:

```text
1. Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_ACTIVATION_STATUS.json status from pre-activation to activated.
2. Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_GOAL.json status from started to activated.
3. Close issue #1 as completed.
```
