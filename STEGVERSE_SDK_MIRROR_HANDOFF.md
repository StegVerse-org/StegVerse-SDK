# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the authoritative continuation record for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goals

```text
Goal 4: governed micro-node return-path validation.
Goal 5: governed-vs-recursive comparison orchestration.
Goal 6: cross-entry roles, transition usage, coordinate navigation consumption,
and aggregate session receipt generation.
Manual user action required: false
```

## Authority boundary

The SDK prepares, transports, validates, aggregates, and hands off governed objects. It is not provider execution, runtime authority, navigation authority, admissibility, standing, commit-time validation, or Master-Records custody.

Required invariants:

```text
sdk_validation_is_execution == false
sdk_intake_is_authority == false
sdk_navigation_consumption_is_authority == false
sdk_navigation_consumption_transfers_authority == false
sdk_navigation_consumption_is_commit_time_validation == false
usage_event_is_authority == false
usage_event_is_admissibility == false
session_receipt_is_master_record_custody == false
aggregation_is_universal_cost_claim == false
returned_to_origin == true
```

## Completed Goal 4 return-path surface

Installed:

```text
docs/MICRO_NODE_RETURN_PATH_SDK.md
examples/micro_node_return_path/request.json
examples/micro_node_return_path/governed_return.json
scripts/verify_micro_node_return_path.py
scripts/verify_goal4.py
stegverse/micro_node_return_path.py
tests/test_micro_node_return_path.py
```

The SDK validates terminal governed return payloads, origin return, receipt references, and no-authority boundaries without executing the micro-node or persisting a master record.

## Completed Goal 5 comparison surface

Installed:

```text
stegverse/llm_route_comparison.py
stegverse/comparison_transport.py
stegverse/comparison_orchestrator.py
schemas/llm_route_comparison.schema.json
scripts/verify_llm_route_comparison.py
scripts/verify_comparison_orchestrator.py
tests/test_llm_route_comparison.py
tests/test_comparison_transport.py
tests/test_comparison_orchestrator.py
```

One immutable normalized request can be submitted to governed and recursive routes. Returned route identity, task identity, telemetry evidence classes, measured-only deltas, and deterministic comparison receipts are validated fail closed.

## Completed Goal 6 role and transition usage surface

Installed:

```text
schemas/entry_point_role.schema.json
schemas/transition_usage_event.schema.json
stegverse/entry_point_roles.py
stegverse/transition_usage.py
tests/test_entry_point_roles.py
tests/test_transition_usage.py
docs/ENTRY_POINT_ROLES.md
docs/TRANSITION_USAGE_LEDGER.md
```

The SDK preserves session, transition, origin-entry-point, measurement-owner, evidence-class, and receipt-reference lineage. Duplicate measurement-owner pairs are deduplicated, mixed sessions fail closed, and unavailable evidence is never silently converted into zero.

## Completed canonical coordinate navigation consumption

Installed:

```text
schemas/coordinate_navigation_consumer.schema.json
stegverse/coordinate_navigation.py
tests/test_coordinate_navigation.py
scripts/verify_coordinate_usage_integration.py
```

The consumer accepts the canonical navigation envelope and coordinate registry artifacts owned by `StegVerse-002/micro-node-runtime`.

It verifies:

```text
source coordinate resolves exactly once
destination is one declared registry edge
context references are unique and non-empty
authority_transfer = NONE
standing_transfer = NONE
delegation_transfer = NONE
data_transfer = DECLARED_REFS_ONLY
receipt_required = true
commit_time_revalidation_required = true
registry version, coordinate version, contract reference, and content hash are present
```

The resulting SDK consumer record preserves the registry and coordinate version bindings, the canonical coordinate content hash, return path, and a deterministic `consumer_sha256`.

The SDK does not claim that consuming the envelope authorizes navigation or performs commit-time revalidation.

## Completed aggregate session usage receipt

Installed:

```text
schemas/session_usage_receipt.schema.json
stegverse/session_usage_receipt.py
tests/test_session_usage_receipt.py
scripts/verify_coordinate_usage_integration.py
```

The receipt builder:

```text
re-verifies every source usage-event hash
rejects tampered events
runs canonical session aggregation
preserves measurement counts, entry points, transition IDs, totals, and exclusions
preserves measurement_id + metric_owner deduplication semantics
records unique source event hashes
emits deterministic receipt_sha256
sets custody_posture = HANDOFF_READY_NOT_CUSTODIED
```

Authority boundary:

```text
receipt_is_execution_authority = false
receipt_is_admissibility = false
receipt_is_master_record_custody = false
aggregation_is_universal_cost_claim = false
```

## Automated verification

The consolidated workflow remains:

```text
.github/workflows/sdk-demo-test.yml
```

Its complete `pytest tests/` execution automatically discovers:

```text
tests/test_coordinate_navigation.py
tests/test_session_usage_receipt.py
```

Existing comparison, role, transition usage, return-path, package-build, editable-install, and wheel-install checks remain consolidated in the same workflow. No additional workflow, manual dispatch, manual event aggregation, manual navigation inspection, manual hash calculation, or manual receipt construction is required.

Standalone verification:

```bash
python scripts/verify_goal4.py
python scripts/verify_llm_route_comparison.py
python scripts/verify_comparison_orchestrator.py
python scripts/verify_coordinate_usage_integration.py
pytest tests/ -v
```

Canonical GitHub Actions execution after these changes has not been observed here; no CI-pass claim is made.

## Current completion state

```text
Goal 4 governed return-path validation: COMPLETE
Goal 5 comparison package, transport, orchestration, deltas, and receipts: COMPLETE
Goal 6 entry-point role registry: COMPLETE
Goal 6 transition usage event contract: COMPLETE
Goal 6 cross-entry session aggregation and deduplication: COMPLETE
canonical navigation-envelope and registry consumption: COMPLETE
aggregate session usage receipt: COMPLETE
source event hash re-verification: COMPLETE
non-custodial handoff posture: COMPLETE
repository-local SDK implementation for current adjacent goals: COMPLETE
canonical GitHub Actions observation: PENDING MACHINE EVIDENCE
```

## Remaining adjacent goals owned elsewhere

```text
StegVerse-org/LLM-adapter
  -> provider-owned usage events with bounded reasoning provenance
  -> machine-readable adapter role declaration

StegVerse-Labs/Site
  -> render coordinate navigation, resident responses, entry-point roles,
     transition usage, cross-entry sessions, and benchmark comparisons

master-records/orchestration
  -> accept custody handoffs
  -> independently re-verify hashes
  -> deduplicate measurements and packages
  -> record retention policies and reconstruction pointers

StegVerse-org/core-node-runtime-demo
  -> live governed trace capture remains external evidence, not SDK implementation
```

## Archive posture

The SDK repository-local navigation consumption and session aggregation receipt goals are complete, durable, and automated. No earlier conversation context is required to continue downstream. The broader ecosystem session is not yet ready for final archival because LLM Adapter, Site, and Master-Records implementation goals remain actionable.
