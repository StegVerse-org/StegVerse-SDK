# MCP Portable Authority Test Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
goal_id: SDK-MCP-PORTABLE-AUTHORITY-001
tracking_issue: #30
implementation_pull_request: #31
machine_validation_task: tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
status: SOURCE_VALIDATED_PENDING_SOVEREIGN_INTEGRATION
```

Live repository state, committed evidence, applicable broader SDK handoffs, and this file supersede chat-only claims for this goal.

## Goal

Add an MCP production-artifact test mode to the StegVerse SDK without creating a second evaluator, custody path, authority source, receipt algorithm, or credential path.

The MCP lane uses the same canonical route as ordinary governed SDK evaluation:

```text
SDK MCP test entry
-> MCP initialize + tools/list discovery (observation only)
-> exact selected tool contract + proposed call canonicalized/hashed
-> portable MCP test packet (non-authorizing evidence)
-> Core-Lite manifested route carrier / ingestion-CGE path
-> Master Records route checkpoint custody
-> canonical StegCore manifested transaction
-> canonical StegGate + commit-coherence evaluation
-> bounded MCP tools/call only when canonical consequence execution is admitted
-> MCP result captured into canonical execution observation
-> Master Records exact-run custody
-> return ingestion/CGE path
-> Master Records return custody
-> SDK caller return
```

Every manifested transition remains receipted. Master Records custody remains independent of caller projection.

## Selected-mode navigation

Inside MCP test mode the canonical five-option structure is preserved:

```text
000 -> show exactly how the MCP production-artifact test works
00  -> return/explanation preferences
0   -> ordinary governed MCP submission
1   -> replay by manifest_receipt_id
2   -> reconstruction by manifest_receipt_id
```

Option `0` supports:

```text
StegVerse General MCP -> inspectable local reference MCP server
External MCP          -> tester-provided safe stdio MCP server descriptor
```

Installed console entry point:

```text
stegverse-mcp-test --select 000|00|0|1|2
```

The generic SDK surface registry exposes aliases `mcp` and `mcp-test` for discovery and points testers to the selected-mode console.

## Invariants

```text
production artifacts under test: TRUE
special MCP-aware StegGate evaluator: PROHIBITED
special MCP receipt authority: PROHIBITED
MCP discovery grants authority: FALSE
MCP tools/list grants authority: FALSE
MCP tools/call grants authority: FALSE
portable packet grants authority: FALSE
manifest_receipt_id grants authority: FALSE
successful governed run without Master Records custody: PROHIBITED
non-TV/TVC secret/token use: PROHIBITED
GitHub runtime authority: NONE
external MCP credential authority: TV/TVC_ONLY
replay consequence reexecution: FALSE
reconstruction consequence reexecution: FALSE
```

The StegVerse General MCP reference target is an ordinary inspectable MCP implementation and contains no StegVerse admission logic.

## Implementation claim

```text
source owner: this session through PR #31 merge
sovereign validation owner: canonical sovereign SDK execution lane
machine task: SDK-MCP-CANONICAL-VALIDATION-009
source merge condition: source compile + focused token-free unit suite PASS
activation/release condition: canonical production-artifact integration + MR/MRR custody + replay/reconstruction proof PASS
```

## Installed implementation

```text
stegverse/mcp_reference_server.py
  ordinary JSON-RPC stdio MCP reference server
  inspect_state
  write_bounded_value
  create_resource
  single_use_operation

stegverse/mcp_transport.py
  MCP initialize/tools/list/tools/call client
  safe stdio descriptor parser
  caller secret/token/auth/env credential rejection
  complete stdio process/pipe cleanup

stegverse/mcp_governance.py
  deterministic discovered-tool contract hash
  deterministic proposed-call hash
  portable MCP test packet
  ordinary StegGate request binding
  MCP tools/call installed as canonical bounded consequence executor

stegverse/mcp_navigation.py
  selected-mode 000/00/0/1/2 semantics
  explicit production-artifact route explanation

stegverse/mcp_cli.py
  reference vs external MCP selection
  discovered tool selection
  option 0 governed run
  option 1 canonical replay
  option 2 canonical reconstruction

stegverse/sovereign_validation_runtime.py
  backwards-compatible optional bounded consequence callback
  same canonical Core-Lite/StegCore/StegGate/Master Records route
  returns canonical execution observation result when present

stegverse/sdk_surfaces.py
  discoverable mcp-production-artifact-test surface + mcp/mcp-test aliases

pyproject.toml
  stegverse-mcp-test console entry point

inspection/examples/mcp-reference-inspect-state-arguments.json
inspection/examples/mcp-reference-write-bounded-arguments.json
inspection/examples/mcp-external-stdio-descriptor.example.json

tests/test_mcp_production_artifact.py

docs/MCP_PRODUCTION_ARTIFACT_TESTS.md
```

## Source validation evidence

```text
workflow: MCP Source Validation (Non-Authorizing)
run: 31873378300
job: 94985269686
head: e6c02cd703860275cb67f2412274402f288a8d07
result: SUCCESS
compileall: PASS
focused unit tests: 8/8 PASS
process GITHUB_TOKEN present: false
process GH_TOKEN present: false
process PYPI_API_TOKEN present: false
runtime authority: NONE
production activation role: NONE
```

The focused source suite proves:

```text
reference MCP is ordinary/inspectable
initialize -> tools/list -> tools/call works
portable contract hash is deterministic
argument mutation changes call hash
schema/tool drift changes contract hash
ordinary StegGate request binding carries exact hashes
caller auth/token/secret/env credential descriptor material is rejected
000 explains tools/list -> canonical governance -> tools/call -> Master Records -> return ingestion/CGE
MCP production-artifact test is discoverable from the generic SDK surface registry
actual MCP call is handed to the canonical bounded consequence callback rather than preexecuted by the harness
```

A preceding hosted attempt successfully ran the focused unit suite but failed while pip attempted to clone the private `master-records/orchestration` production dependency. No GitHub/private-repository credential was added to bypass that boundary. The hosted workflow was corrected to remain source-only; canonical governed integration was transferred to the sovereign machine task.

## Production-artifact integration evidence state

```text
canonical governed integration test: INSTALLED_NOT_YET_SOVEREIGN_EXECUTED
Master Records exact-run MR custody: PENDING_MACHINE_TASK
Master Records route MRR custody: PENDING_MACHINE_TASK
reference MCP exact governed tools/call observation: PENDING_MACHINE_TASK
replay no-reexecution proof: PENDING_MACHINE_TASK
reconstruction no-reexecution proof: PENDING_MACHINE_TASK
machine owner: tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
source merge: ELIGIBLE_AFTER_SOURCE_VALIDATION
release/tag: NOT_READY
activation: PENDING_SOVEREIGN_INTEGRATION
```

The implementation was checked against the pinned StegCore production transaction lifecycle. Its existing `governed_steggate_execute` reaches the supplied executor only after StegGate disposition `ALLOW` and independent commit-coherence `ALLOW`; the MCP lane injects `tools/call` at that existing consequence boundary rather than creating an MCP-specific evaluator.

## Remaining executable work

```text
StegVerse-org/StegVerse-SDK / canonical sovereign SDK execution lane:
- acquire tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
- run focused unit + governed integration suites with already-materialized canonical production packages
- run reference inspect_state through selected mode 0 and retain exact MR/MRR evidence
- replay selected mode 1 from the exact manifest_receipt_id; prove consequence_reexecuted=false
- reconstruct selected mode 2 from the exact manifest_receipt_id; prove consequence_reexecuted=false
- run bounded write reference case and retain governed result
- correct any runtime defect discovered by the sovereign run
- update issue #30, this handoff, and SDK_MIRROR_HANDOFF.md with exact evidence
- only then evaluate release/tag readiness

Cross-repository publication after release criteria are met:
- StegVerse-Labs/Site (or canonical Site/Sit successor)
- GCAT-BCAT-Engine/Publisher
- admissibility-wiki
- stegguardian-wiki
```

## Next executable action

Merge PR #31 once its source-validation check is green. The canonical sovereign SDK execution lane then acquires `SDK-MCP-CANONICAL-VALIDATION-009`; it must not use a GitHub-hosted runner or inject a private-repository/GitHub token merely to materialize Master Records.
