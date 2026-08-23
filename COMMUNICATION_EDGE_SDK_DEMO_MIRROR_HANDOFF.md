# Communication Edge SDK Demo Mirror Handoff

Status: VALIDATED
Repository: StegVerse-org/StegVerse-SDK
Date: 2026-08-22

## Purpose

Provide a public, non-authorizing SDK demonstration and executable source-integration proof for the KnowledgeVault-hosted StegWhisper -> StegTalk ST-031 -> ST-032 -> ephemeral-edge communication flow.

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

## Current ST-031 + ST-032 + KnowledgeVault proof

Pull request: `#59` — `Extend communication proof through ST-032 runtime`
Workflow: `Communication Edge SDK Demo Validation`
Workflow run: `32608268105`

Current pinned sources exercised:

```text
StegVerse-Labs/StegTalk
72947c052467af2ba5850378dc53f7589c473d35

StegVerse-Labs/continuity-vault-kit
35e6d7ad881e0dea60ba191c49dfd4fba86e3fd7
```

Observed validation boundary:

```text
Python 3.9:
  SDK demo/install/conformance -> SUCCESS
  current StegTalk ST-031/ST-032 runtime proof -> intentionally SKIPPED
  reason: current StegTalk package declares Python >=3.11

Python 3.11:
  SDK demo/install/conformance -> SUCCESS
  current ST-031 + ST-032 + KnowledgeVault runtime-source proof -> SUCCESS

Python 3.12:
  SDK demo/install/conformance -> SUCCESS
  current ST-031 + ST-032 + KnowledgeVault runtime-source proof -> SUCCESS
```

The 3.11 and 3.12 jobs executed the real current source chain and proved:

1. ST-031 selected the higher-capability `stegtalk-ip` edge over SMS under AUTO;
2. SMS remained the exact ordered fallback;
3. ST-031 issued the execution lease;
4. ST-032 accepted only the exact selection hash, attempt, selected edge, selected bearer, and lease epoch;
5. ST-032 executed a real callable `LOOPBACK_TEST` edge executor;
6. ST-032 produced a hash-bound edge execution receipt with `DELIVERED` outcome;
7. reusing the same idempotency key and exact binding returned the cached receipt rather than redispatching;
8. ambiguous post-dispatch execution produced `VERIFY_EXTERNALLY`;
9. confirmed no-side-effect failure produced `TRY_FALLBACK` to the exact SMS fallback;
10. the real `KnowledgeVaultExecutionStore` persisted the selection receipt, lease/attempt state, edge execution receipt, and execution outcome;
11. a fresh KnowledgeVault store reconstructed the selection, lease, and edge execution receipt after restart.

The proof output explicitly retains:

```text
edge_runtime_callable_executed = true
duplicate_dispatch_suppressed = true
kv_edge_execution_receipt_reconstructed_after_restart = true
loopback_test_only = true
physical_transport_proven = false
production_activation_proven = false
```

## Earlier retained validation

```text
PR #54 / run 32602726148
  SDK-only conformance demo
  Python 3.9 / 3.11 / 3.12 SUCCESS

PR #55 / run 32602863793
  earlier pinned ST-031 + KnowledgeVault source integration
  Python 3.9 / 3.11 / 3.12 SUCCESS for that historical source pin

StegWhisper PR #15 / run 32602979304
  real StegWhisper v0.2 -> ST-031 -> KnowledgeVault source integration
  SUCCESS

PR #57 / runs 32605995150 and 32606024322
  public evaluator guide validation
  Python 3.9 / 3.11 / 3.12 SUCCESS

PR #58 / runs 32606159922 and 32606199291
  installed stegverse-comm-demo + packaged fixture + source/installed parity
  Python 3.9 / 3.11 / 3.12 SUCCESS
```

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
Installed SDK command = non-authorizing public demo entry
Pinned source integration = executable source-integration proof
StegWhisper = messenger posture + constraints
StegTalk ST-031 = admissibility + scoring + edge/bearer selection
StegTalk ST-032 = bounded execution of the already-selected edge
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

`LOOPBACK_TEST` proves runtime dispatch plumbing; it is not a physical/network bearer and cannot establish recipient delivery or production activation.

## Remaining activation boundary

Source/software selection-to-execution-to-KV persistence is now validated. Remaining work belongs to the running system:

- persist an actual bearer-generated attempt into the connected personal KnowledgeVault;
- advertise at least two actual admitted device edges;
- execute a selected physical/network bearer;
- append observed delivery evidence into connected KV;
- restart/replace the selected physical edge and reconstruct without duplicate dispatch;
- exercise ST-029 modem/SIM outbound, +CDS delivery report, inbound correlation, and multipart partial-failure handling;
- only then claim runtime/production activation as applicable.
