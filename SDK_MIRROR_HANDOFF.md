# SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 4: SDK validation of `LLM-adapter` micro-node governed return-path fixtures.

The SDK should treat `StegVerse-002/micro-node-runtime` as a governed runtime target and verify that adapter-originated micro-node fixtures preserve request shape, terminal decision semantics, receipt reference, and original return-path continuity.

## Upstream completed inputs

```text
StegVerse-002/micro-node-runtime
  -> transition-table-native portable micro-node runtime merged on main

StegVerse-org/core-node-runtime-demo
  -> micro-node compatibility comparison merged on main

StegVerse-org/LLM-adapter
  -> micro-node governed return-path proof merged on main
```

## Required SDK validation surface

```text
adapter request fixture
-> SDK schema/shape validation
-> terminal decision validation
-> return-path preservation validation
-> authority non-escalation validation
-> receipt reference validation
-> validation report
```

## Files to install for Goal 4

```text
docs/MICRO_NODE_RUNTIME_TARGET.md
examples/micro_node_adapter_fixture/request.json
examples/micro_node_adapter_fixture/governed_return.json
scripts/verify_micro_node_adapter_fixture.py
tests/test_micro_node_adapter_fixture.py
```

## Required invariant

```text
returned_to_origin == true
execution_authority_granted == false
provider_output_is_authority == false
decision in {ALLOW, DENY, FAIL_CLOSED}
transition_id is preserved
return_path is preserved
receipt_hash is present
```

## Verification commands

```bash
python scripts/verify_micro_node_adapter_fixture.py
pytest tests/test_micro_node_adapter_fixture.py -v
pytest tests/ -v
```

## Downstream sync targets

```text
StegVerse-Labs/admissibility-wiki
  -> document portable governed return-path proof once SDK validation is green
```

## Archive posture

This handoff preserves the current Goal 4 SDK validation state so the complete thread can be archived without needing additional context to continue.
