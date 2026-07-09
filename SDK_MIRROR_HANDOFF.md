# SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 10: corrected HPS sibling-input alignment for SDK intake.

Goal 9 SDK HPS route fixtures are preserved below as installed prior context. Goal 10 corrects the architectural wording: the SDK is not the HPS integration owner for the ecosystem and is not upstream authority for the LLM adapter. The SDK is one sibling input nest that consumes HPS-runtime, hybrid-collab-bridge, and Ecosystem-Delegation contracts.

## Goal 10 corrected architecture

```text
Admissible-Existence/HPS
  -> standing-vector formalism

StegVerse-org/HPS-runtime
  -> executable runtime state, standing-vector registers, phases, epochs, capability windows

SDK input            \
LLM-adapter input     \
Site input             -> StegVerse-Labs/hybrid-collab-bridge -> StegVerse-Labs/Ecosystem-Delegation -> next governed boundary
External adapter      /
Manual review        /

master-records/orchestration
  -> cycle state, receipts, participant records, reconstruction references
```

## Goal 10 SDK role

```text
StegVerse-org/StegVerse-SDK is an SDK-origin input nest.
It may emit SDK-origin HPS route candidates.
It may validate SDK-facing HPS route fixtures.
It does not grant execution authority.
It does not grant delegation authority.
It does not make LLM-adapter subordinate to SDK.
It does not own ecosystem-wide HPS orchestration.
```

## Goal 10 consumption rule

SDK-origin requests should consume:

```text
StegVerse-org/HPS-runtime
  -> runtime state and standing-vector registers

StegVerse-Labs/hybrid-collab-bridge
  -> sibling input route normalization

StegVerse-Labs/Ecosystem-Delegation
  -> governed authority delegation decision

master-records/orchestration
  -> receipts, observation state, reconstruction references
```

`ALLOW` or `ALLOW_NEXT_BOUNDARY` only permits the SDK-origin route to continue to the next governed boundary. It is not execution authority.

## Goal 10 installed by handoff update

```text
SDK_MIRROR_HANDOFF.md updated to correct SDK role from ecosystem HPS owner to sibling input consumer.
```

## Goal 10 remaining work

```text
- Update docs/HPS_SDK_INTEGRATION.md to match the corrected sibling-input architecture.
- Update schemas/examples later only if bridge/delegation runtime contracts require a different SDK-origin route shape.
- Observe SDK workflow/test result and replace pending observation receipt.
```

---

## Preserved Goal 9 context

Goal 9: HPS integration layer for SDK intake and capability-window routing.

Goal 8 SDK ingestion contract for LLM-adapter free-tier trust metadata is preserved below as completed prior context. Goal 9 added HPS route fixtures and verification at the SDK level.

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

## Superseded Goal 9 ownership note

The prior wording treated `StegVerse-org/StegVerse-SDK` as the first StegVerse-org HPS integration owner. That is now superseded by the corrected architecture:

```text
HPS-runtime owns executable runtime semantics.
hybrid-collab-bridge owns sibling route normalization.
Ecosystem-Delegation owns governed delegation evaluation.
SDK is one sibling input nest.
LLM-adapter is one sibling input nest.
master-records/orchestration owns ecosystem cycle records and receipts.
```

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

## Corrected downstream sync targets

```text
StegVerse-org/HPS-runtime
  -> supplies runtime state and standing-vector registers

StegVerse-Labs/hybrid-collab-bridge
  -> consumes SDK-origin route candidates as sibling input

StegVerse-Labs/Ecosystem-Delegation
  -> evaluates governed authority delegation after bridge normalization

StegVerse-Labs/Site
  -> consumes HPS visualization status payload for Ecosystem Chat

StegVerse-Labs/admissibility-wiki
  -> mirrors HPS formalism and public explanation

master-records/orchestration
  -> preserves HPS runtime, bridge, delegation, SDK, adapter, Site, and mirror receipts
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
sdk_hps_route_allow_is_execution_authority == false
sdk_hps_route_allow_is_delegation_authority == false
sdk_and_llm_adapter_are_sibling_input_nests == true
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
  - docs/HPS_SDK_INTEGRATION.md wording alignment to corrected sibling-input architecture
  - observed SDK HPS workflow/test receipt

StegVerse-org/LLM-adapter:
  - aligned handoff/docs so it consumes runtime + bridge + delegation as sibling input, not SDK route authority

master-records/orchestration:
  - replace pending SDK observation receipt when workflow/test output is observed
```

## Archive posture

This handoff preserves SDK Goal 10 corrected HPS sibling-input alignment, Goal 9 HPS route fixtures, and Goal 8 metadata ingestion state so the complete thread can be archived without needing additional context to continue.
