# MCP Portable Authority Test Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
goal_id: SDK-MCP-PORTABLE-AUTHORITY-001
tracking_issue: #30
initial_implementation_pull_request: #31
initial_source_merge: 79656e42aeff0ce0eeba101523854706df198b00
intake_defect_fix_pull_request: #32
intake_defect_fix_merge: 8b7d2f81591a1388277ba55e5e64210de65dc877
integration_acceptance_pull_request: #33
current_source_commit: e4733a41805bcb546b97ad079d9fa75d26ef266d
validation_task: tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
latest_diagnostic: reports/mcp-production-artifact/local-integration-diagnostic-20260815.json
machine_worker_handoff: StegVerse-Labs/.github/handoffs/SDK-MCP-CANONICAL-VALIDATION-009.json
machine_worker_merge: StegVerse-Labs/.github@2694f3e8524595c7c0591d3fa7ebe5a32f92f70d
status: SOURCE_VALIDATED_DEFECTS_CORRECTED_MACHINE_WORKER_REGISTERED_EXACT_SOVEREIGN_ARTIFACT_RUN_PENDING
```

Live repository state, committed evidence, issue #30, the validation task, the `.github` executable worker handoff, and this file supersede chat-only claims.

## Goal and canonical route

The MCP test lane exercises production StegVerse artifacts without creating a second evaluator, custody path, authority source, receipt algorithm, or credential path.

```text
SDK MCP test entry
-> MCP initialize + tools/list discovery (observation only)
-> exact selected tool contract + proposed call canonicalized/hashed
-> portable MCP test packet (non-authorizing evidence)
-> Core-Lite manifested route carrier / ingestion-CGE
-> Master Records route checkpoint custody
-> canonical StegCore manifested transaction
-> canonical StegGate + commit-coherence evaluation
-> bounded MCP tools/call only after canonical ALLOW + coherence ALLOW
-> MCP result captured into canonical execution observation
-> Master Records exact-run custody
-> return ingestion/CGE
-> Master Records return custody
-> SDK caller return
```

Every manifested transition is receipted. Master Records custody is independent of caller projection.

## Selected mode

```text
000 -> show exactly how the MCP production-artifact test works
00  -> return/explanation preferences
0   -> ordinary governed MCP submission
1   -> replay by manifest_receipt_id
2   -> reconstruction by manifest_receipt_id
```

Option `0` supports either the inspectable ordinary StegVerse General MCP or a tester-provided safe stdio MCP descriptor. Installed console entry point:

```text
stegverse-mcp-test --select 000|00|0|1|2
```

The generic SDK registry exposes `mcp` and `mcp-test` aliases.

## Governing invariants

```text
production artifacts under test: TRUE
special MCP-aware StegGate evaluator: PROHIBITED
special MCP receipt authority: PROHIBITED
MCP discovery grants authority: FALSE
MCP tools/list grants authority: FALSE
MCP tools/call grants authority: FALSE
portable packet grants authority: FALSE
manifest_receipt_id grants authority: FALSE
caller request external_consequence_enabled: FALSE
bounded consequence executor installed outside caller authority payload: TRUE
successful governed run without Master Records custody: PROHIBITED
non-TV/TVC secret/token use: PROHIBITED
GitHub runtime authority: NONE
external MCP credential authority: TV/TVC_ONLY
replay consequence reexecution: FALSE
reconstruction consequence reexecution: FALSE
hosted exact-artifact execution: PROHIBITED
manual competing worker claim: PROHIBITED
```

The StegVerse General MCP remains ordinary MCP and contains no StegVerse admission logic.

## Current merged SDK implementation

```text
stegverse/mcp_reference_server.py
stegverse/mcp_transport.py
stegverse/mcp_governance.py
stegverse/mcp_navigation.py
stegverse/mcp_cli.py
stegverse/sovereign_validation_runtime.py
stegverse/sdk_surfaces.py
pyproject.toml
inspection/examples/mcp-reference-inspect-state-arguments.json
inspection/examples/mcp-reference-write-bounded-arguments.json
inspection/examples/mcp-external-stdio-descriptor.example.json
tests/test_mcp_production_artifact.py
tests/test_mcp_request_boundary.py
docs/MCP_PRODUCTION_ARTIFACT_TESTS.md
.github/workflows/mcp-production-artifact-test.yml
reports/mcp-production-artifact/local-integration-diagnostic-20260815.json
```

## Validation history

### Initial source validation

```text
workflow: MCP Source Validation (Non-Authorizing)
run: 31873378300
job: 94985269686
result: SUCCESS
focused tests: 8/8 PASS
process GITHUB_TOKEN: absent
process GH_TOKEN: absent
process PYPI_API_TOKEN: absent
```

### Integration-boundary defects found and corrected

Testing the merged path against canonical public-inspection intake exposed two real defects:

1. `build_governed_request()` declared `external_consequence_enabled=true`, but canonical public intake correctly prohibits a caller request from enabling an external consequence.
2. The full MCP packet was placed in public `input_data`; the ordinary MCP field `descriptor_name` matched the canonical public-input forbidden fragment `script`.

PR #32 corrected the design:

```text
request external_consequence_enabled: false
public input_data: exact contract hash + exact call hash + tool label + phase only
full MCP packet: trusted bounded-consequence metadata
actual tools/call: injected canonical consequence executor only
```

Evidence:

```text
PR: #32
merge: 8b7d2f81591a1388277ba55e5e64210de65dc877
workflow run: 31889450763
job: 95023440401
result: SUCCESS
compile: PASS
tests: 9/9 PASS
credential/token environment checks: PASS / absent
```

### Integration acceptance coverage

PR #33 added executable assertions for:

```text
exact MCP contract hash survives into governed execution observation
exact proposed-call hash survives into governed execution observation
replay consequence_reexecuted=false
reconstruction consequence_reexecuted=false
replay/reconstruction operation-transition custody receipt IDs retained
bounded write write_bounded_value(42) produces retained governed UPDATED result
```

Evidence:

```text
PR: #33
merge: e4733a41805bcb546b97ad079d9fa75d26ef266d
workflow run: 31889542545
job: 95023659790
result: SUCCESS
```

## Local integration diagnostic

A credential-sanitized source-equivalent local diagnostic exercised the complete executable logic. Observed:

```text
inspect_state:
  governance: ALLOW
  Master Records custody: RECORDED
  transaction identity continuous: true
  StegCore receipt chain verified: true
  route transitions: 10
  contract/call hashes retained: true
  replay consequence_reexecuted: false
  replay MRO custody: RECORDED
  reconstruction consequence_reexecuted: false
  reconstruction MRO custody: RECORDED

write_bounded_value(42):
  governance: ALLOW
  Master Records custody: RECORDED
  transaction identity continuous: true
  StegCore receipt chain verified: true
  MCP result: UPDATED / bounded_value=42
  contract/call hashes retained: true
```

Durable receipt:

```text
reports/mcp-production-artifact/local-integration-diagnostic-20260815.json
```

**Evidence-strength boundary:** the diagnostic remains `SOURCE_EQUIVALENT_LOCAL_DIAGNOSTIC_NOT_CANONICAL_SOVEREIGN_PROOF`. No GitHub/private-repository token was introduced to materialize private Master Records on a non-authorized surface.

## Machine worker installation

The prior task had a durable execution specification but no concrete StegVerse worker registration/adapter. That gap is now closed by merged `.github` PR #179.

Canonical machine path:

```text
StegVerse-Labs/.github merge: 2694f3e8524595c7c0591d3fa7ebe5a32f92f70d
handoff: handoffs/SDK-MCP-CANONICAL-VALIDATION-009.json
registry: control/worker-registry.d/sdk-mcp-canonical-validation-009.json
adapter: control/process-worker-adapters.d/sdk-mcp-canonical-validation-009.json
worker: workers/sdk_mcp_canonical_validation_worker.py
worker_id: sdk-mcp-canonical-validation-worker
adapter_ref: process:sdk-mcp-canonical-validation-v1
state: HANDOFF_READY
worker: AVAILABLE
claim: MACHINE_CLAIM_ON_EXECUTION
manual execution: false
hosted exact execution: false
credential authority: TV/TVC
GitHub token runtime authority: NONE
non-TV/TVC secret/token allowed: false
```

The worker does not clone repositories or acquire credentials. It accepts four non-secret local locators to already-materialized source trees:

```text
STEGVERSE_SDK_SOURCE_ROOT
STEGVERSE_STEGCORE_SOURCE_ROOT
STEGVERSE_CORE_LITE_SOURCE_ROOT
STEGVERSE_MASTER_RECORDS_SOURCE_ROOT
```

It fails closed on hosted execution, missing scheduler claim, missing exact source artifacts, skipped/failing governed integration, receipt/custody absence, re-execution during replay/reconstruction, or credential-boundary drift.

Source validation of the worker installation:

```text
workflow: Heartbeat Worker Project - Validation Only / No GitHub Token Authority
run: 31890771807
job: 95026592450
result: SUCCESS
anonymous checkout: PASS
no GitHub credential token: PASS
compile runtime/workers/scripts: PASS
canonical JSON parse: PASS
executable handoff validation: PASS
complete deterministic repository test suite: PASS
new MCP worker tests: 7/7 PASS
heartbeat dry-run non-persistence: PASS
ephemeral projection rebuild: PASS
workflow non-authorizing: PASS
```

A separate organization-control-plane workflow remains red because of pre-existing handoff ownership-partition defects in heartbeat documentation outside this MCP worker change. That unrelated workflow failure is not promoted to MCP validation failure; the changed MCP handoff passed the executable-handoff validator and the complete deterministic suite passed in run 31890771807.

## Exact production-artifact integration still required

The final activation gate is now concretely machine-owned rather than merely described.

Exact source identities:

```text
SDK source: current main e4733a41805bcb546b97ad079d9fa75d26ef266d or declared successor
StegCore: 083557adec1bdbace09ebd10fb0765eb8e9a9d08 or declared successor
Core-Lite: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8 or declared successor
Master Records: 6626c6a7f1df6bf531940c165b2f4db374e08b92 or already-materialized declared successor
```

The worker must retain:

```text
canonical governed integration PASS
exact MR custody
exact MRR route custody
exact MRO replay custody
exact MRO reconstruction custody
actual MCP tools/call only after StegGate ALLOW + commit-coherence ALLOW
exact contract/call hash binding
continuous transaction identity
replay no-reexecution
reconstruction no-reexecution
bounded write governed result
credential boundary proving no non-TV/TVC secret/token use
```

## Ownership / collision state

```text
source defect correction: COMPLETE_VALIDATED_MERGED
integration acceptance test implementation: COMPLETE_VALIDATED_MERGED
local source-equivalent integration diagnostic: PASS
machine worker/registry/adapter/handoff: COMPLETE_VALIDATED_MERGED
exact sovereign production-artifact execution: MACHINE_OWNED_PENDING
canonical SDK task: tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
canonical machine handoff: StegVerse-Labs/.github/handoffs/SDK-MCP-CANONICAL-VALIDATION-009.json
credential authority: TV/TVC
GitHub/private token workaround: PROHIBITED
manual competing claim: PROHIBITED
release/tag: NOT_READY
goal activation: INCOMPLETE
```

## Completion accounting

```text
required developed SDK MCP surfaces: 16
complete developed SDK MCP surfaces: 16
required worker integration surfaces: 5
complete worker integration surfaces: 5
scaffolding/stubs: 0
missing required source/test/worker surfaces: 0
source validation gates: PASS
worker registration validation: PASS
local executable logic diagnostic: PASS
exact sovereign artifact integration: PENDING
release/tag: PENDING exact integration
```

## Next executable action

The canonical sovereign scheduler must assign a collision-safe claim to `sdk-mcp-canonical-validation-worker` on an eligible non-hosted StegVerse node where the four exact canonical source roots are already materialized. The worker executes the exact integration suite and governed reference MCP inspect/replay/reconstruct/bounded-write proof, then emits `~/.stegverse/receipts/sdk-mcp-canonical-validation-009.json`. Reconcile that receipt into issue #30, this handoff, and `tasks/SDK-MCP-CANONICAL-VALIDATION-009.json`. Chat/manual execution must not create a competing claim.
