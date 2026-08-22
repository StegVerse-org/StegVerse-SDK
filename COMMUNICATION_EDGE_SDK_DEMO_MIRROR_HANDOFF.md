# Communication Edge SDK Demo Mirror Handoff

Status: VALIDATION_PENDING
Repository: StegVerse-org/StegVerse-SDK
Branch under validation: test/communication-edge-sdk-demo
Date: 2026-08-22

## Purpose

Provide a public SDK conformance demonstration of the KnowledgeVault-hosted StegWhisper -> StegTalk ST-031 -> ephemeral-edge communication flow without moving execution, admissibility, bearer-selection, or continuity authority into the SDK.

## Implemented source

- `stegverse/communication_edge_demo.py`
- `examples/communication_edge_demo.json`
- `tests/test_communication_edge_demo.py`
- `scripts/run_communication_edge_demo.py`
- `.github/workflows/communication-edge-demo-validation.yml`

## Demonstrated invariants

- SDK output is always `sdk_simulation_only=true`;
- SDK output grants no authority and performs no transport execution;
- a higher-capability native StegTalk path can outrank SMS under `AUTO`;
- unattested or expired edges fail closed;
- UNKNOWN recipient state can use only explicit safe fallback bearers;
- remote-edge denial keeps execution selection on the declared current edge;
- single primary edge is selected by default;
- ambiguous post-dispatch state produces `VERIFY_EXTERNALLY`, never automatic fallback;
- confirmed no-side-effect failure may advance exactly once to the first ordered fallback;
- identical packets produce identical selection receipts and hashes.

## Validation lane

`Communication Edge SDK Demo Validation` runs on Python 3.9, 3.11, and 3.12. It compiles the demo, runs the dedicated pytest file, executes the sample packet, and checks that the produced artifact remains explicitly non-authorizing.

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
StegWhisper = messenger posture + constraints
StegTalk ST-031 = real admissibility + scoring + edge/bearer selection
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

A successful SDK demo is not production activation. It proves public package behavior and invariants only.

## Completion condition

1. PR validation lane passes on all configured Python versions.
2. The runnable demonstration packet executes successfully.
3. No authority-boundary regression is introduced.
4. This handoff is merged to main with exact observed validation evidence.

Until those conditions are observed, state remains VALIDATION_PENDING.
