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
status: SOURCE_VALIDATED_DEFECTS_CORRECTED_INTEGRATION_LOGIC_DIAGNOSTIC_PASS_EXACT_SOVEREIGN_ARTIFACT_RUN_PENDING
```

Live repository state, committed evidence, issue #30, the validation task, and this handoff supersede chat-only claims.

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
```

The StegVerse General MCP remains ordinary MCP and contains no StegVerse admission logic.

## Current merged implementation

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

### Actual integration-boundary testing found two defects

Testing the merged path against the canonical public-inspection intake exposed defects that the original mocked consequence test did not catch:

1. `build_governed_request()` declared `external_consequence_enabled=true`, but canonical public intake correctly prohibits a caller request from enabling an external consequence.
2. The full MCP packet was placed in public `input_data`; the ordinary MCP field `descriptor_name` matched the canonical public-input forbidden fragment `script`.

Both defects would have blocked the sovereign production route before StegCore/Core-Lite/Master Records execution.

PR #32 corrected the design:

```text
request external_consequence_enabled: false
public input_data: exact contract hash + exact call hash + tool label + phase only
full MCP packet: retained as trusted bounded-consequence metadata
actual tools/call: still only the injected canonical consequence executor
```

Validation evidence:

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

### Integration acceptance coverage completed

PR #33 added explicit executable assertions for the remaining acceptance contract:

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

A credential-sanitized local integration diagnostic was then run through the complete executable logic using the current MCP code plus production-source-equivalent StegCore/Master Records modules and the exact pinned Core-Lite route module. The process environment contained no GitHub/token/secret credential keys.

Observed behavior:

```text
inspect_state:
  governance: ALLOW
  Master Records custody: RECORDED
  transaction identity continuous: true
  StegCore receipt chain verified: true
  route transitions: 10
  route: MANIFEST_ESTABLISHED -> SDK_ENTERED -> INGESTION_ENTERED -> CGE_ADMITTED -> CGE_ROUTED -> MODULE_ENTERED -> MODULE_RESULT -> CGE_RETURN_INGESTED -> ROUTE_CLEARED -> RETURNED
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

**Evidence-strength boundary:** this diagnostic is deliberately recorded as `SOURCE_EQUIVALENT_LOCAL_DIAGNOSTIC_NOT_CANONICAL_SOVEREIGN_PROOF`. The chat execution surface cannot materialize the private `master-records/orchestration` package through an authorized TV/TVC path. No GitHub/private-repository token was introduced to make it do so.

## Exact production-artifact integration still required

The canonical exact-artifact run remains the final activation gate:

```text
SDK source: current main e4733a41805bcb546b97ad079d9fa75d26ef266d or declared successor
StegCore: 083557adec1bdbace09ebd10fb0765eb8e9a9d08 or declared successor
Core-Lite: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8 or declared successor
Master Records: 6626c6a7f1df6bf531940c165b2f4db374e08b92 or already-materialized declared successor
```

The exact run must retain:

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
exact sovereign production-artifact execution: PENDING
canonical task: tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
credential authority: TV/TVC
GitHub/private token workaround: PROHIBITED
release/tag: NOT_READY
goal activation: INCOMPLETE
```

Repository searches did not surface a separate executable SDK worker/worker-registry implementation for `SDK-MCP-CANONICAL-VALIDATION-009`; the durable task is the canonical execution specification. Do not describe the exact run as already active merely because the task file exists.

## Completion accounting

```text
required developed MCP surfaces: 16
complete developed MCP surfaces: 16
scaffolding/stubs: 0
missing required source/test surfaces: 0
source validation gates: PASS
local executable logic diagnostic: PASS
exact sovereign artifact integration: PENDING
release/tag: PENDING exact integration
```

## Next executable action

Execute `MCPProductionArtifactGovernedIntegrationTests` on an authorized sovereign/local execution surface where the exact declared production packages are already materialized without exposing any non-TV/TVC secret/token to the SDK. Persist the exact MR/MRR/MRO result and update issue #30, this handoff, and `tasks/SDK-MCP-CANONICAL-VALIDATION-009.json`. If that run exposes another source defect, correct and revalidate it before activation.
