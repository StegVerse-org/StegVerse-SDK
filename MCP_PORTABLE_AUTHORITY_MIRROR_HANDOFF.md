# MCP Portable Authority Test Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
goal_id: SDK-MCP-PORTABLE-AUTHORITY-001
tracking_issue: #30
implementation_branch: feat/mcp-portable-authority-test
status: SOURCE_IMPLEMENTED_VALIDATION_PENDING
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
owner: this session
claim: SDK-MCP-PORTABLE-AUTHORITY-001
created: 2026-08-15T02:48:00-05:00
tracking_issue: StegVerse-org/StegVerse-SDK#30
release condition: source installed + tests installed + canonical governed integration PASS + handoffs updated + merge
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

## Validation requirements

Installed tests target:

```text
000 describes the production artifact route
00 preserves caller projection semantics without suppressing custody
reference MCP initialize -> tools/list -> tools/call works
external safe stdio descriptor is accepted
caller auth/token/secret/env credential material is rejected
MCP tools/list discovery is captured into the governed candidate
MCP tool/schema contract is deterministically hashed
argument mutation changes the proposed-call hash
schema/tool drift changes the contract hash
actual MCP call is passed to canonical consequence execution rather than preexecuted
candidate + exact arguments are evaluated through canonical sovereign runtime
Master Records custody is RECORDED on successful governed evaluation
1 replays by manifest_receipt_id without consequence reexecution
2 reconstructs by manifest_receipt_id without consequence reexecution
```

## Evidence state

```text
source implementation: COMPLETE_ON_FEATURE_BRANCH
unit tests: INSTALLED_NOT_YET_EXECUTED
canonical governed integration test: INSTALLED_NOT_YET_EXECUTED
Master Records live test custody: PENDING_VALIDATION_RUN
merge: PENDING
release/tag: NOT_READY
activation: PENDING_VALIDATION_AND_MERGE
```

The implementation has been checked against the pinned StegCore transaction lifecycle source: the canonical `governed_steggate_execute` invokes the supplied executor only after StegGate disposition ALLOW and independent commit-coherence ALLOW. The MCP lane relies on that existing production artifact rather than duplicating it.

## Remaining executable work

```text
StegVerse-org/StegVerse-SDK:
- execute tests/test_mcp_production_artifact.py with dev + governed-test dependencies
- inspect exact Master Records MR/MRR custody evidence from the reference MCP run
- execute replay and reconstruction proof from that same manifest_receipt_id
- correct any runtime/interface defect found by the canonical run
- merge feature branch only after validation passes
- update SDK_MIRROR_HANDOFF.md with exact commit/run/evidence
- decide release/tag only after merged source and retained validation evidence are complete

Cross-repository publication:
- do not propagate to Site/Publisher/admissibility-wiki/stegguardian-wiki before release criteria are met
```

## Next executable action

Run the strongest available canonical validation for the feature branch and retain the exact run evidence. If runtime execution capacity is unavailable, leave validation PENDING rather than converting source inspection into a PASS.
