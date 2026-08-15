# MCP Portable Authority Test Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
goal_id: SDK-MCP-PORTABLE-AUTHORITY-001
status: ACTIVE_IMPLEMENTATION
```

Live repository state, committed evidence, applicable broader SDK handoffs, and this file supersede chat-only claims for this goal.

## Goal

Add an MCP production-artifact test mode to the existing StegVerse SDK governance navigator without creating a second evaluator, custody path, authority source, receipt algorithm, or credential path.

The MCP lane must use the same canonical route as ordinary governed SDK evaluation:

```text
SDK MCP test entry
-> Core-Lite manifested route carrier / ingestion-CGE path
-> Master Records route checkpoint custody
-> canonical StegCore manifested transaction
-> canonical StegGate + commit-coherence evaluation
-> Master Records exact-run custody
-> return ingestion/CGE path
-> Master Records return custody
-> SDK caller return
```

Every manifested transition remains receipted. Master Records custody remains independent of the caller projection.

## Selected-mode navigation

Inside MCP test mode preserve the canonical five-option structure:

```text
000 -> show exactly how the MCP test route works
00  -> return/explanation preferences
0   -> ordinary governed MCP submission
1   -> replay by manifest_receipt_id
2   -> reconstruction by manifest_receipt_id
```

Option `0` must let a tester select either:

```text
StegVerse General MCP -> inspectable local reference MCP server
External MCP          -> tester-provided MCP server descriptor
```

## Invariants

```text
production artifacts under test: TRUE
special MCP-aware StegGate evaluator: PROHIBITED
special MCP receipt authority: PROHIBITED
MCP discovery grants authority: FALSE
MCP tools/list grants authority: FALSE
MCP tools/call grants authority: FALSE
manifest_receipt_id grants authority: FALSE
successful run without Master Records custody: PROHIBITED
non-TV/TVC secret/token use: PROHIBITED
GitHub runtime authority: NONE
external MCP credential authority: TV/TVC_ONLY
```

The StegVerse General MCP reference target must remain an ordinary, inspectable MCP implementation. It must not contain StegVerse admission logic.

## Implementation claim

```text
owner: this session
claim: SDK-MCP-PORTABLE-AUTHORITY-001
created: 2026-08-15T02:48:00-05:00
release condition: source installed + tests installed + local validation evidence committed + broader SDK handoff updated
```

## Planned files

```text
stegverse/mcp_reference_server.py
stegverse/mcp_transport.py
stegverse/mcp_governance.py
stegverse/cli.py
stegverse/governance_navigation.py
inspection/examples/mcp-*.json
tests/test_mcp_governance.py
README.md
MCP_PORTABLE_AUTHORITY_MIRROR_HANDOFF.md
SDK_MIRROR_HANDOFF.md
```

## Validation requirements

Minimum source validation must prove:

```text
000 describes the production artifact route
00 preserves caller projection without suppressing custody
0 can use the StegVerse General MCP
0 can accept an external MCP descriptor without accepting caller secrets
MCP tools/list discovery is captured into the governed candidate
MCP tool/schema contract is deterministically hashed
candidate + exact arguments are evaluated through canonical sovereign runtime
Master Records custody is RECORDED on successful governed evaluation
1 replays by manifest_receipt_id without consequence reexecution
2 reconstructs by manifest_receipt_id without consequence reexecution
schema/tool drift changes the bound contract hash
non-TV/TVC auth material is rejected
```

## Current state

```text
handoff: COMPLETE
implementation: PENDING
validation: PENDING
activation: PENDING
```

## Next executable action

Implement the MCP reference server, transport/descriptor boundary, governed MCP request binding, selected-mode CLI wiring, and tests. Then run the strongest available source/local validation and update this handoff with exact evidence.
