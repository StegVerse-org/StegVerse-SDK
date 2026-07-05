# SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 8: SDK ingestion contract for LLM-adapter free-tier trust metadata.

Goal 4 preserved SDK validation of the `LLM-adapter` micro-node governed return-path fixtures. Goal 8 now adds SDK validation for `StegVerse-org/LLM-adapter` `free_tier_trust` metadata so Site, adapter, and SDK can align on bounded free-tier quota, receipt export, replay, reconstruction, retention, upgrade, and non-claim metadata.

## Upstream completed inputs

```text
StegVerse-002/micro-node-runtime
  -> transition-table-native portable micro-node runtime merged on main

StegVerse-org/core-node-runtime-demo
  -> micro-node compatibility comparison merged on main

StegVerse-org/LLM-adapter
  -> micro-node governed return-path proof merged on main
  -> free_tier_trust response metadata and adapter.capabilities.json fields installed

StegVerse-Labs/Site
  -> ecosystem-chat.html display-only Bounded free-tier trust display installed
  -> scripts/check_site_llm_free_tier_trust.py installed
```

## Goal 4 SDK validation surface

```text
adapter request fixture
-> SDK schema/shape validation
-> terminal decision validation
-> return-path preservation validation
-> authority non-escalation validation
-> receipt reference validation
-> validation report
```

## Goal 8 proof path

```text
LLM-adapter free_tier_trust metadata
-> SDK metadata ingestion contract
-> deterministic validation result
-> non-authorizing SDK status
-> downstream Site / adapter compatibility signal
```

## Installed for Goal 4

```text
docs/MICRO_NODE_RUNTIME_TARGET.md
examples/micro_node_adapter_fixture/request.json
examples/micro_node_adapter_fixture/governed_return.json
scripts/verify_micro_node_adapter_fixture.py
tests/test_micro_node_adapter_fixture.py
```

## Installed for Goal 8

```text
docs/FREE_TIER_METADATA_INGESTION.md
stegverse/free_tier_metadata.py
tests/test_free_tier_metadata.py
scripts/verify_free_tier_metadata_ingestion.py
sdk.capabilities.json updated with free-tier metadata ingestion fields
README.md updated with free-tier metadata ingestion section
SDK_MIRROR_HANDOFF.md updated
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
quota_availability_is_admissibility == false
quota_availability_is_execution_authority == false
receipt_export_is_permanent_retention == false
replay_grants_commit_time_standing == false
reconstruction_grants_commit_time_standing == false
upgrade_changes_admissibility_requirements == false
sdk_ingestion_performs_side_effects == false
```

## Verification commands

```bash
python scripts/verify_micro_node_adapter_fixture.py
pytest tests/test_micro_node_adapter_fixture.py -v
python scripts/verify_free_tier_metadata_ingestion.py
pytest tests/test_free_tier_metadata.py -v
pytest tests/ -v
```

## Downstream sync targets

```text
StegVerse-Labs/Site
  -> can display free-tier trust metadata and guard static public wording

StegVerse-org/LLM-adapter
  -> remains source for free_tier_trust schema and capability manifest

StegVerse-Labs/admissibility-wiki
  -> document portable governed return-path proof once SDK validation is green
```

## Remaining files or modules to install

```text
StegVerse-org/StegVerse-SDK:
  - optional aggregate verifier/workflow wiring for scripts/verify_free_tier_metadata_ingestion.py if an appropriate SDK guard exists
```

## Archive posture

This handoff preserves the SDK Goal 8 metadata ingestion state so the complete thread can be archived without needing additional context to continue.
