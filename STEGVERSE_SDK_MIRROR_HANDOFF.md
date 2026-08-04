# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the authoritative continuation record for
`StegVerse-org/StegVerse-SDK` until superseded. Live default-branch state, Git
history, issues, pull requests, workflow runs, artifacts, releases, and
committed receipts are authoritative over historical conversation claims.

## Repository role

```text
repository: StegVerse-org/StegVerse-SDK
default branch: main
role: user-facing, non-authorizing intake and compatibility boundary
```

The SDK prepares, transports, validates, aggregates, and hands off governed
objects. SDK validation, compatibility, submission, and ingestion are not
execution, runtime authority, navigation authority, admissibility, standing,
commit-time validation, publication, or Master-Records custody.

## Completed goals retained

```text
Goal 4 governed micro-node return-path validation: COMPLETE
Goal 5 governed-vs-recursive comparison orchestration: COMPLETE
Goal 6 entry-point role and transition-usage contracts: COMPLETE
Goal 6 coordinate-navigation consumption: COMPLETE
Goal 6 aggregate session-usage receipt: COMPLETE
```

Authoritative completed surfaces include:

```text
docs/MICRO_NODE_RETURN_PATH_SDK.md
stegverse/micro_node_return_path.py
stegverse/llm_route_comparison.py
stegverse/comparison_orchestrator.py
stegverse/entry_point_roles.py
stegverse/transition_usage.py
stegverse/coordinate_navigation.py
stegverse/session_usage_receipt.py
schemas/coordinate_navigation_consumer.schema.json
schemas/session_usage_receipt.schema.json
scripts/verify_coordinate_usage_integration.py
.github/workflows/sdk-demo-test.yml
```

Existing invariants remain binding:

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

## Active Goal 7

```text
goal id: EGC-PROP-SDK
parent goal: EGC-PROP-001
originating session goal: propagate the accepted governed edge-cell profile
                          into the SDK as a source-bound consumer contract
canonical source: StegVerse-002/micro-node-runtime
source commit: c9660dd0dffd97d9ececc9b7428ef165ae212419
source PR: StegVerse-002/micro-node-runtime#14
source receipt hash: c546a4addf80eebead9cc17324fad7580d6d5050c5347e86969c91d8d9cf7299
source propagation registry: StegVerse-002/micro-node-runtime#15
```

## Active claim

```text
state: CLAIMED_FOR_INTEGRATION
claimant: SDK edge-cell consumer lane
github actor: StegVerse
claim created: 2026-08-04T11:41:00-05:00
claim expires: 2026-08-04T17:00:00-05:00
release condition: SDK PR merged, closed, explicitly superseded, or expired
```

Claimed implementation surfaces:

```text
stegverse/edge_cell_consumer.py
tests/test_edge_cell_consumer.py
scripts/verify_edge_cell_consumer.py
examples/edge_cell_source_binding.json
docs/GOVERNED_EDGE_CELL_SDK_CONSUMER.md
stegverse/__init__.py
.github/workflows/sdk-demo-test.yml
STEGVERSE_SDK_MIRROR_HANDOFF.md
```

Collision boundaries:

```text
existing universal-entry execution routes
existing Master Records custody client
canonical micro-node activation evaluator
provider and LLM-adapter authority boundaries
release and PyPI publishing jobs
```

The SDK will consume and verify the accepted source declaration. It will not
reimplement the canonical activation evaluator or assert custody.

## Required behavior

The consumer must:

```text
verify the canonical source repository and exact source commit
verify the profile identifier and version
verify the accepted activation receipt hash
verify authority_effect == NONE
verify physical actuation, external export, and federated commit remain conditional
verify source evidence does not assert destination custody acceptance
reject source drift, authority expansion, missing bindings, and malformed evidence
return a deterministic SDK compatibility result
```

Successful SDK status is limited to:

```text
accepted_for_non_authorizing_sdk_consumption
```

## Execution inventory

| Task | Exact location | Claim state | Completion | Validation | Integration | Next action |
|---|---|---|---|---|---|---|
| SDK-EGC-1 | `stegverse/edge_cell_consumer.py` | CLAIMED_FOR_INTEGRATION | missing | pending | pending | implement source-bound validator |
| SDK-EGC-2 | `examples/edge_cell_source_binding.json` | CLAIMED_FOR_INTEGRATION | missing | pending | pending | add canonical fixture |
| SDK-EGC-3 | `tests/test_edge_cell_consumer.py` | CLAIMED_FOR_VALIDATION | missing | pending | pending | add positive and fail-closed tests |
| SDK-EGC-4 | `scripts/verify_edge_cell_consumer.py` | CLAIMED_FOR_VALIDATION | missing | pending | pending | add deterministic verifier |
| SDK-EGC-5 | `stegverse/__init__.py` | CLAIMED_FOR_INTEGRATION | not integrated | pending | pending | expose public API |
| SDK-EGC-6 | `.github/workflows/sdk-demo-test.yml` | CLAIMED_FOR_INTEGRATION | not integrated | pending | pending | add import and route verification |
| SDK-EGC-7 | `docs/GOVERNED_EDGE_CELL_SDK_CONSUMER.md` | CLAIMED_FOR_INTEGRATION | missing | pending | pending | document source and non-claims |
| SDK-EGC-8 | this handoff | CLAIMED_FOR_INTEGRATION | active | pending update | pending | record branch, PR, runs, and release |

## Automation contract

```text
trigger: existing SDK pull-request and main-branch workflow
inputs: committed source-binding fixture
outputs: deterministic SDK acceptance or fail-closed rejection
persistent state: fixture, tests, verifier output, PR workflow, handoff
missing evidence behavior: FAIL_CLOSED
runtime statuses: ACCEPTED, REJECTED
coordination statuses: CLAIMED, COMPLETE, BLOCKED, SUPERSEDED, MERGED
```

## Validation commands

```bash
pytest tests/test_edge_cell_consumer.py -v
python scripts/verify_edge_cell_consumer.py
pytest tests/ -v
python -m build
```

## Cross-repository dependencies

```text
source authority: StegVerse-002/micro-node-runtime@c9660dd0dffd97d9ececc9b7428ef165ae212419
source registry: StegVerse-002/micro-node-runtime#15
custody destination: master-records/orchestration
publication destinations: StegVerse-Labs/Site and GCAT-BCAT-Engine/Publisher
```

The SDK does not wait for downstream custody to validate source compatibility,
but it must not report downstream custody or publication acceptance.

## Completion denominator

```text
developed files: 1/8
scaffolding or stubs: 0
missing required files: 7
validation: 0/4
integration: 0/3
goal activation: 5%
```

Validation denominator:

```text
1 targeted unit tests
2 deterministic verifier
3 complete SDK suite
4 hosted workflow and package build
```

Integration denominator:

```text
1 public API and workflow wiring
2 accepted PR/default-branch merge
3 propagation receipt back to StegVerse-002/micro-node-runtime#15
```

## Exact next tasks

```text
1. Create feature/edge-cell-consumer from this handoff commit.
2. Implement the source-bound validator, fixture, tests, verifier, and docs.
3. Wire the public API and consolidated workflow.
4. Open and validate a pull request.
5. Merge, release the claim, and update the source propagation registry.
```

## Archive posture

The earlier SDK goals are durable and do not require prior conversations. The
active edge-cell consumer lane remains unique and executable.

```text
DO NOT ARCHIVE THIS SESSION — DISTINCT SUPPORT WORK REMAINS.
```
