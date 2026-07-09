# SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 9: HPS integration owner for SDK intake and capability-window routing.

Goal 8 SDK ingestion contract for LLM-adapter free-tier trust metadata is preserved below as completed prior context. Goal 9 adds HPS as the SDK-level dynamic governor for route availability and expiration.

## Goal 9 upstream completed input

```text
Admissible-Existence/HPS
  -> Harmonic Principle of Standing formalism installed
  -> heartbeat receipt schema/verifier installed
  -> capability-window schema/verifier installed
  -> expiration receipt schema/verifier installed
  -> standing score schema/verifier installed
  -> Ecosystem Chat visualization contract/builder installed
  -> HPS Verify #12 observed successful by user screenshot
  -> 15 tests passed
```

## Goal 9 ownership decision

`StegVerse-org/StegVerse-SDK` owns the first StegVerse-org HPS integration layer because the SDK already serves as the user-facing intake boundary for:

- SDK submissions;
- LLM Adapter submissions;
- Ecosystem Chat intake validation;
- manifest-bound intake;
- receipt-bound route packages;
- downstream governance routing.

`StegVerse-org/LLM-adapter` should consume HPS capability-window decisions, but it should not own ecosystem-wide HPS integration.

## Goal 9 SDK route rule

A route may proceed only when:

```text
heartbeat is PASS;
standing class satisfies route requirement;
capability window is open;
authority is valid;
policy is current;
delegation is current;
evidence is fresh;
coordinate is valid;
reconstruction is available;
expiration triggers are empty.
```

If any required support fails, SDK must return a bounded route decision:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

## Installed for Goal 9

```text
docs/HPS_SDK_INTEGRATION.md
schemas/hps.sdk.route.schema.json
examples/hps_sdk_route_allowed.json
examples/hps_sdk_route_expired.json
examples/hps_sdk_route_fail_closed.json
scripts/verify_hps_sdk_route.py
tests/test_hps_sdk_route.py
.github/workflows/sdk-demo-test.yml updated to verify HPS SDK route fixtures
SDK_MIRROR_HANDOFF.md updated
```

## Goal 9 verification commands

```bash
python scripts/verify_hps_sdk_route.py examples/hps_sdk_route_allowed.json
python scripts/verify_hps_sdk_route.py examples/hps_sdk_route_expired.json
python scripts/verify_hps_sdk_route.py examples/hps_sdk_route_fail_closed.json
pytest tests/test_hps_sdk_route.py -v
pytest tests/ -v
```

## Goal 9 downstream sync targets

```text
StegVerse-org/LLM-adapter
  -> consume SDK HPS route contract before tool use, memory commit, publication, or execution handoff

StegVerse-Labs/Site
  -> consume HPS visualization status payload for Ecosystem Chat

StegVerse-Labs/admissibility-wiki
  -> mirror HPS formalism summary and Standing Equation

BCAT-GCAT-Engine/Publisher
  -> require HPS restored standing before publication transitions

master-records
  -> preserve HPS heartbeat and SDK route receipts
```

---

## Preserved Goal 8 context

Goal 8: SDK ingestion contract for LLM-adapter free-tier trust metadata.

Goal 4 preserved SDK validation of the `LLM-adapter` micro-node governed return-path fixtures. Goal 8 added SDK validation for `StegVerse-org/LLM-adapter` `free_tier_trust` metadata so Site, adapter, and SDK can align on bounded free-tier quota, receipt export, replay, reconstruction, retention, upgrade, and non-claim metadata.

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
  -> site-public-mirror-status-guard.yml runs the LLM free-tier checker
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
-> SDK demo workflow verification
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
stegverse/__init__.py exports validate_free_tier_metadata and FreeTierMetadataResult
tests/test_free_tier_metadata.py
scripts/verify_free_tier_metadata_ingestion.py
sdk.capabilities.json updated with free-tier metadata ingestion fields
README.md updated with free-tier metadata ingestion section
.github/workflows/sdk-demo-test.yml verifies free-tier metadata ingestion and wheel import
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
manual_demo_ingestion_trigger_required == false
```

## Verification commands

```bash
python scripts/verify_micro_node_adapter_fixture.py
pytest tests/test_micro_node_adapter_fixture.py -v
python scripts/verify_free_tier_metadata_ingestion.py
pytest tests/test_free_tier_metadata.py -v
python scripts/verify_hps_sdk_route.py examples/hps_sdk_route_allowed.json
pytest tests/test_hps_sdk_route.py -v
pytest tests/ -v
```

The SDK demo workflow runs free-tier metadata ingestion and HPS SDK route fixture verification before the test suite.

## Remaining files or modules to install

```text
StegVerse-org/StegVerse-SDK:
  - no known Goal 9 SDK-side files remain at this handoff

StegVerse-org/LLM-adapter:
  - consume SDK HPS route contract before governed adapter handoff

StegVerse-Labs/admissibility-wiki:
  - optional public documentation of the Site + LLM-adapter + SDK bounded free-tier trust chain
```

## Archive posture

This handoff preserves the SDK Goal 9 HPS integration state and the prior Goal 8 metadata ingestion state so the complete thread can be archived without needing additional context to continue.
