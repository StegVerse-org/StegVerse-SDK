# Communication Edge SDK Demo Mirror Handoff

Status: VALIDATED
Repository: StegVerse-org/StegVerse-SDK
Date: 2026-08-22

## Purpose

Provide a public SDK conformance demonstration of the KnowledgeVault-hosted StegWhisper -> StegTalk ST-031 -> ephemeral-edge communication flow without moving execution, admissibility, bearer-selection, or continuity authority into the SDK.

## Implemented SDK demo

- `stegverse/communication_edge_demo.py`
- `stegverse/communication_edge_cli.py`
- `stegverse/demo_data/communication_edge_demo.json`
- `examples/communication_edge_demo.json`
- `tests/test_communication_edge_demo.py`
- `scripts/run_communication_edge_demo.py`
- `scripts/run_pinned_communication_source_integration.py`
- `docs/COMMUNICATION_EDGE_SDK_DEMO.md`
- `.github/workflows/communication-edge-demo-validation.yml`
- installed console command: `stegverse-comm-demo`

## Installed evaluator command

The SDK package now exposes:

```bash
stegverse-comm-demo
stegverse-comm-demo --compact
stegverse-comm-demo /path/to/custom-packet.json
```

When no packet path is supplied, the CLI loads the deterministic packet from packaged `stegverse.demo_data`, so the evaluator does not depend on a repository-relative `examples/` path after installation.

### Installed-command validation evidence

Pull request `#58` — `Validate installed communication edge SDK command`
Validated head: `0845ce5387a8c3877249d900c2ab176615d22aa9`
Workflow: `Communication Edge SDK Demo Validation`
Workflow run: `32606159922`

Observed jobs:

```text
validate (3.9)  -> SUCCESS
validate (3.11) -> SUCCESS
validate (3.12) -> SUCCESS
```

Every configured Python version successfully:

1. installed the SDK;
2. compiled the communication-edge simulator and installed CLI;
3. ran the conformance tests;
4. ran the repository demo fixture;
5. ran `stegverse-comm-demo` using packaged demo data;
6. required installed-command JSON to equal repository-runner JSON exactly;
7. re-verified `sdk_simulation_only=true`, `authority_granted=false`, and `execution_performed=false`;
8. anonymously checked out pinned StegTalk and KnowledgeVault sources;
9. executed the real pinned ST-031 + KnowledgeVault integration proof;
10. re-verified selection, lease persistence, restart reconstruction, ambiguity suppression, and confirmed-safe fallback.

The CLI was corrected before validation to avoid Python 3.10-only union syntax; Python 3.9 is observed passing.

## Public evaluator guide

`docs/COMMUNICATION_EDGE_SDK_DEMO.md` is the human-facing entry for this demo. It now makes `stegverse-comm-demo` the primary demonstration path and documents the repository runner as an equivalent source-level path. It also documents conformance tests, custom packets, recipient states, cross-edge policy, capability dimensions, fallback safety, pinned-source reproduction, and the physical/runtime claim boundary.

### Public-guide validation evidence

Pull request `#57` — `Validate public communication edge demo guide`
Workflow runs `32605995150` and `32606024322`
Python 3.9 / 3.11 / 3.12: SUCCESS

The full SDK demo and pinned-source integration lane remained green with the public guide and final evidence handoff present.

## Earlier SDK-only validation evidence

Pull request `#54`
Workflow run `32602726148`
Python 3.9 / 3.11 / 3.12: SUCCESS

This validated the SDK simulator, dedicated conformance tests, default packet, and non-authorizing boundary.

## Pinned real-source integration evidence

Pull request `#55`
Merged commit: `a0654a0b58779cb254371e7c5a3505dfc4a94239`
Workflow run: `32602863793`
Python 3.9 / 3.11 / 3.12: SUCCESS

Exact public source commits exercised:

```text
StegVerse-Labs/StegTalk
2361d13ea09818f17aef5239ebf4771a161a0dc7

StegVerse-Labs/continuity-vault-kit
35e6d7ad881e0dea60ba191c49dfd4fba86e3fd7
```

The workflow imported and executed the real `stegtalk.cross_edge_resolver` and `execution.vault_store`, selected `stegtalk-ip` over SMS under AUTO, retained SMS as ordered fallback, issued an execution lease, persisted the actual selection receipt and attempt/lease state, reopened a fresh KnowledgeVault store, reconstructed both after restart, produced `VERIFY_EXTERNALLY` for ambiguous post-dispatch state, and produced `TRY_FALLBACK` only after confirmed no-side-effect failure.

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
Installed SDK command = public non-authorizing demo entry
Pinned source integration = executable source-integration proof
StegWhisper = messenger posture + constraints
StegTalk ST-031 = real admissibility + scoring + edge/bearer selection
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

The validated SDK paths perform no physical bearer transmission and grant no execution authority to the SDK.

## Remaining activation boundary

The source/software integration, installed SDK demonstrator, public evaluator guide, and pinned-source restart/fallback proof are tested. Remaining work is runtime/physical proof:

- feed an actual StegWhisper v0.2 posture from a running messenger surface;
- persist a real runtime selection/lease into the connected personal KnowledgeVault;
- advertise at least two actual admitted device edges;
- execute through the selected physical/network bearer;
- observe delivery evidence returning to KnowledgeVault;
- restart/replace the selected edge and prove connected-vault recovery without duplicate dispatch;
- exercise the ST-029 modem/SIM path for actual SMS proof.

These runtime/physical items remain outside the SDK's authority and are not claimed complete by this validation.
