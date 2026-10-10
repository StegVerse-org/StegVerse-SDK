# MCP Production-Artifact Tests

The MCP test lane exercises the same canonical StegVerse SDK, Core-Lite and StegCore/StegGate artifacts used by the existing governed test path; its run is kept in the SDK-internal local run record (`stegverse/local_run_record.py`; non-authoritative: authority_effect NONE, completes_transition false; not Master Records authority or custody). The test environment controls the MCP target and proposed operation; it does not substitute mock governance or a second custody system.

## Install

```bash
python -m pip install -e ".[dev,governed-test]"
```

The package exposes:

```bash
stegverse-mcp-test --select 000
stegverse-mcp-test --select 00
stegverse-mcp-test --select 0
stegverse-mcp-test --select 1
stegverse-mcp-test --select 2
```

Running `stegverse-mcp-test` with no `--select` presents the same five selected-mode choices interactively.

## 000 — see exactly how it works

```bash
stegverse-mcp-test --select 000
```

This prints the production-artifact route, authority boundary, local run-record requirements (SDK-internal `stegverse/local_run_record.py`; non-authoritative, caller-supplied location), and the point at which an MCP `tools/call` may occur.

Canonical path:

```text
SDK MCP test entry
-> MCP initialize + tools/list discovery
-> exact tool contract + exact proposed call canonicalized/hashed
-> portable MCP test packet
-> canonical SDK ingress / Core-Lite manifested route
-> MRR-* checkpoint record (SDK-internal local run record; non-authoritative)
-> canonical StegCore transaction
-> canonical StegGate + commit-coherence evaluation
-> bounded MCP tools/call only at the canonical consequence boundary
-> MCP result captured as execution observation
-> MR-* exact-run record (SDK-internal local run record; not Master Records custody)
-> return ingestion/CGE
-> MRR-* return record (SDK-internal local run record; not Master Records custody)
-> same SDK caller connection
```

MCP discovery and packet construction have no authority effect.

## 00 — caller return preferences

```bash
stegverse-mcp-test --select 00
```

Caller return/explanation preferences never suppress the canonical run record.

## 0 — run an MCP production-artifact test

### StegVerse General MCP

The repository contains an ordinary, intentionally inspectable stdio MCP reference server in `stegverse/mcp_reference_server.py`. It contains no StegVerse governance/admission logic.

Inspect state:

```bash
stegverse-mcp-test --select 0 \
  --mcp-source reference \
  --tool inspect_state \
  --arguments inspection/examples/mcp-reference-inspect-state-arguments.json
```

Bounded write:

```bash
stegverse-mcp-test --select 0 \
  --mcp-source reference \
  --tool write_bounded_value \
  --arguments inspection/examples/mcp-reference-write-bounded-arguments.json
```

When `--tool` is omitted in an interactive shell, the SDK performs `tools/list` and presents the discovered tools for selection.

### External MCP

Start from the credential-free descriptor shape in:

```text
inspection/examples/mcp-external-stdio-descriptor.example.json
```

Then run:

```bash
stegverse-mcp-test --select 0 \
  --mcp-source external \
  --mcp-descriptor ./my-mcp-descriptor.json \
  --tool <exact-tool-name> \
  --arguments ./arguments.json
```

The current external transport boundary is intentionally limited to local `stdio` with a command represented as a JSON string array. The descriptor rejects caller-managed authorization headers, tokens, secrets, passwords, API keys, environment credential maps, and credential fields. Protected credential authority remains TV/TVC-only.

## Portable MCP test packet

For the selected discovered tool, the SDK binds:

```text
MCP protocol version
serverInfo
selected exact tool definition/schema
descriptor identity
canonical tool-contract SHA-256
exact proposed arguments
canonical proposed-call SHA-256
```

A tool/schema change changes the contract hash. An argument change changes the call hash. `tools/list`, `tools/call`, packet validity, and `manifest_receipt_id` do not grant authority.

The packet is converted into an ordinary canonical StegGate request. The actual MCP call is supplied as the bounded consequence callback to the existing canonical StegCore transaction lifecycle; the MCP test code does not create another evaluator.

## 1 — replay

```bash
stegverse-mcp-test --select 1 \
  --manifest-receipt-id MR-<SHA256> \
  --records-db ./my-run-record.db
```

Replay is separately receipted ecosystem history and does not resend the original MCP `tools/call`.

## 2 — reconstruction

```bash
stegverse-mcp-test --select 2 \
  --manifest-receipt-id MR-<SHA256> \
  --records-db ./my-run-record.db
```

Reconstruction rebuilds the retained trajectory from the retained run evidence in the SDK-internal local run record (`stegverse/local_run_record.py`; non-authoritative: authority_effect NONE, completes_transition false; not Master Records authority or custody). It does not resend the original MCP `tools/call`.

## Test claims

The canonical suite verifies at minimum:

```text
reference MCP is ordinary/inspectable
initialize -> tools/list -> tools/call works
contract hash is deterministic
schema/tool drift changes contract hash
argument mutation changes call hash
caller credential material is rejected
000 exposes the actual production-artifact route
MCP call is handed to the canonical consequence boundary rather than pre-executed
canonical governed integration records the run in the SDK-internal local run record (non-authoritative)
replay does not reexecute consequence
reconstruction does not reexecute consequence
```

Run unit tests:

```bash
python -m unittest tests.test_mcp_production_artifact -v
```

With the governed-test dependencies installed, the same test module also executes the full canonical Core-Lite -> StegCore/StegGate integration path, including the SDK-internal local run record (`stegverse/local_run_record.py`; non-authoritative).
