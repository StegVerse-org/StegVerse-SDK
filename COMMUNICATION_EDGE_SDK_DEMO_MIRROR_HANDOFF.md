# Communication Edge SDK Demo Mirror Handoff

Status: VALIDATED
Repository: StegVerse-org/StegVerse-SDK
Validation branch: test/communication-edge-sdk-demo
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

## Observed validation evidence

Pull request: `#54` — `Validate communication edge SDK demo`
Validated head: `5fa91a81d78b5325445466b2c3a1d183bd9f5dff`
Workflow: `Communication Edge SDK Demo Validation`
Workflow run: `32602726148`

Observed jobs:

```text
validate (3.9)  -> SUCCESS
validate (3.11) -> SUCCESS
validate (3.12) -> SUCCESS
```

Every matrix job successfully completed:

```text
checkout
Python setup
SDK/test dependency installation
communication-edge module/test compilation
pytest tests/test_communication_edge_demo.py
execution of examples/communication_edge_demo.json
non-authorizing output verification
```

The executed demonstration verified that the preferred sample route is `stegtalk-ip`, an ambiguous post-dispatch outcome resolves to `VERIFY_EXTERNALLY`, a confirmed pre-side-effect failure resolves to `TRY_FALLBACK`, and the demo remains explicitly non-authorizing.

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
StegWhisper = messenger posture + constraints
StegTalk ST-031 = real admissibility + scoring + edge/bearer selection
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

A successful SDK demo is not production activation. It proves public package behavior and invariants only.

## Completion state

The SDK demonstration source and its dedicated validation lane are implemented and observed passing on all configured Python versions. This handoff may be merged to main as durable validation evidence.

Remaining work belongs to the live integration boundary, not this SDK demo: real StegWhisper posture input, live ST-031 selection/lease, actual KnowledgeVault receipt persistence/reconstruction, real admitted edges, and physical bearer execution.
