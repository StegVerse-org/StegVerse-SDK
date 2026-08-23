# Communication Edge SDK Demo Mirror Handoff

Status: VALIDATED
Repository: StegVerse-org/StegVerse-SDK
Date: 2026-08-22

## Purpose

Provide a public, non-authorizing SDK demonstration and executable source-integration proof for the KnowledgeVault-hosted StegWhisper -> StegTalk ST-031 -> ST-032 -> KnowledgeVault communication flow.

## Public SDK surface

Implemented and validated:

```text
stegverse/communication_edge_demo.py
stegverse/communication_edge_cli.py
stegverse/demo_data/communication_edge_demo.json
examples/communication_edge_demo.json
tests/test_communication_edge_demo.py
scripts/run_communication_edge_demo.py
scripts/run_pinned_communication_source_integration.py
docs/COMMUNICATION_EDGE_SDK_DEMO.md
.github/workflows/communication-edge-demo-validation.yml
installed command: stegverse-comm-demo
```

The installed command remains a conformance simulation only:

```text
sdk_simulation_only = true
authority_granted = false
execution_performed = false
```

## Current native KnowledgeVault runtime-journal proof

Pull request: `#60` — `Validate ST-032 against KnowledgeVault native runtime journal`
Workflow: `Communication Edge SDK Demo Validation`
Validated workflow run: `32608918326`

Exact source pins:

```text
StegVerse-Labs/StegTalk
72947c052467af2ba5850378dc53f7589c473d35

StegVerse-Labs/continuity-vault-kit
2f2070f94c26eed99ea87553f31579e60033eb1b
```

Observed matrix boundary:

```text
Python 3.9:
  installed SDK demo + conformance -> SUCCESS
  current StegTalk runtime proof -> intentionally skipped
  reason: current StegTalk requires Python >=3.11

Python 3.11:
  installed SDK demo + conformance -> SUCCESS
  ST-031 -> ST-032 -> native KV runtime journal -> SUCCESS

Python 3.12:
  installed SDK demo + conformance -> SUCCESS
  ST-031 -> ST-032 -> native KV runtime journal -> SUCCESS
```

The real 3.11/3.12 source chain proves:

1. ST-031 selects the higher-capability `stegtalk-ip` edge and retains SMS as ordered fallback;
2. ST-031 issues the execution lease;
3. ST-032 accepts only the exact selection/attempt/edge/bearer/lease binding;
4. ST-032 executes a callable `LOOPBACK_TEST` executor and emits a hash-bound edge-execution receipt;
5. the edge cache suppresses duplicate dispatch for the same idempotency binding;
6. ambiguous post-dispatch state produces `VERIFY_EXTERNALLY`;
7. confirmed no-side-effect failure produces the exact ordered `TRY_FALLBACK`;
8. merged KnowledgeVault `CommunicationRuntimeJournal` durably persists selection, lease, execution receipt and recovery decision;
9. durable KV semantics suppress a duplicate observation of the same execution receipt;
10. a fresh journal/store instance reconstructs selection, lease, execution receipt and recovery decision after restart.

Proof output retains:

```text
edge_runtime_callable_executed = true
edge_duplicate_dispatch_suppressed = true
kv_duplicate_execution_observation_suppressed = true
kv_selection_reconstructed_after_restart = true
kv_lease_reconstructed_after_restart = true
kv_edge_execution_receipt_reconstructed_after_restart = true
kv_recovery_decision_reconstructed_after_restart = true
loopback_test_only = true
physical_transport_proven = false
production_activation_proven = false
```

## Contract defects found and repaired by this proof

PR #60 initially failed at the real cross-repository boundary instead of being weakened to pass.

### Hash-profile defect 1

KnowledgeVault initially re-hashed StegTalk evidence under KV's generic action-envelope profile. StegTalk communication evidence uses UTF-8 canonical JSON with `ensure_ascii=false` and producer-specific SHA-256 representations.

Fixed in `continuity-vault-kit` PR #48, merge commit:

```text
6752c30209ea629afc43659da5ea094d067db983
```

### Hash-profile defect 2

The rerun exposed that ST-031 and ST-032 deliberately expose two representations:

```text
ST-031 portable selection_sha256 -> raw 64 lowercase hex
ST-032 edge receipt_sha256        -> sha256:<64 hex>
```

KnowledgeVault now verifies each producer contract separately rather than coercing both to one representation.

Fixed in `continuity-vault-kit` PR #49, merge commit:

```text
2f2070f94c26eed99ea87553f31579e60033eb1b
```

All KV recovery, security, guardrail, diagnostics and governed-action lanes passed on that fix before merge.

## Retained earlier validation

```text
SDK PR #54 / run 32602726148
  SDK-only communication conformance, Python 3.9/3.11/3.12 SUCCESS

SDK PR #55 / run 32602863793
  earlier ST-031 + KV pinned source proof SUCCESS

StegWhisper PR #15 / run 32602979304
  StegWhisper v0.2 -> ST-031 -> KV source integration SUCCESS

SDK PR #57 / runs 32605995150, 32606024322
  public evaluator guide SUCCESS

SDK PR #58 / runs 32606159922, 32606199291
  installed stegverse-comm-demo and source/installed parity SUCCESS

SDK PR #59 / runs 32608268105, 32608335253
  current ST-031 -> ST-032 -> raw KV store proof SUCCESS
```

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
Installed SDK command = non-authorizing public demo entry
Pinned source integration = executable source-integration proof
StegWhisper = messenger posture + constraints
StegTalk ST-031 = admissibility + scoring + edge/bearer selection
StegTalk ST-032 = bounded execution of the already-selected edge
KnowledgeVault CommunicationRuntimeJournal = durable selection/lease/execution/recovery persistence
Edge device = ephemeral execution capability
```

`LOOPBACK_TEST` proves actual source/runtime dispatch plumbing but is not a physical/network bearer and does not establish recipient delivery or production activation.

## Remaining activation boundary

The source path through native KV persistence is now validated. Still open:

- persist a bearer-generated runtime attempt into the connected personal KnowledgeVault;
- advertise at least two actual admitted device edges;
- execute a selected physical/network bearer;
- append observed delivery evidence into connected KV;
- restart/replace the selected physical edge and reconstruct without duplicate dispatch;
- exercise ST-029 modem/SIM outbound, +CDS delivery report, inbound correlation, and multipart partial-failure handling;
- only then claim runtime/production activation as applicable.
