# Communication Edge SDK Demo Mirror Handoff

Status: VALIDATED
Repository: StegVerse-org/StegVerse-SDK
Date: 2026-08-22

## Purpose

Provide a public SDK conformance demonstration of the KnowledgeVault-hosted StegWhisper -> StegTalk ST-031 -> ephemeral-edge communication flow without moving execution, admissibility, bearer-selection, or continuity authority into the SDK.

## Implemented SDK demo

- `stegverse/communication_edge_demo.py`
- `examples/communication_edge_demo.json`
- `tests/test_communication_edge_demo.py`
- `scripts/run_communication_edge_demo.py`
- `scripts/run_pinned_communication_source_integration.py`
- `.github/workflows/communication-edge-demo-validation.yml`

## SDK-only validation evidence

Pull request `#54` validated the SDK simulator on Python 3.9, 3.11, and 3.12. Workflow run `32602726148` completed all three matrix jobs successfully, including compilation, dedicated pytest coverage, execution of the sample packet, and non-authorizing boundary checks.

## Pinned live-source integration evidence

Pull request `#55` merged the pinned-source integration proof.
Merged commit: `a0654a0b58779cb254371e7c5a3505dfc4a94239`
Validation workflow run: `32602863793`

Exact public source commits exercised:

```text
StegVerse-Labs/StegTalk
2361d13ea09818f17aef5239ebf4771a161a0dc7

StegVerse-Labs/continuity-vault-kit
35e6d7ad881e0dea60ba191c49dfd4fba86e3fd7
```

Observed matrix result:

```text
validate (3.9)  -> SUCCESS
validate (3.11) -> SUCCESS
validate (3.12) -> SUCCESS
```

Every matrix job successfully:

1. compiled the SDK communication demo and integration script;
2. ran the SDK conformance tests;
3. executed the SDK demo packet;
4. verified the SDK remained non-authorizing;
5. anonymously checked out the exact pinned StegTalk source;
6. anonymously checked out the exact pinned KnowledgeVault source;
7. imported and executed the real `stegtalk.cross_edge_resolver`;
8. imported and executed the real `execution.vault_store`;
9. selected the higher-capability `stegtalk-ip` edge over SMS under AUTO;
10. retained SMS as the ordered fallback;
11. issued an execution lease bound to the selected edge;
12. proved ambiguous post-dispatch state produces `VERIFY_EXTERNALLY`;
13. proved confirmed no-side-effect failure produces `TRY_FALLBACK` to the exact ordered edge;
14. persisted the actual ST-031 selection receipt through `KnowledgeVaultExecutionStore.append_receipt()`;
15. persisted lease/attempt state through `append_attempt()`;
16. reopened the KnowledgeVault store from a fresh instance and reconstructed both selection receipt and lease state successfully.

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
Pinned source integration = executable source-integration proof
StegWhisper = messenger posture + constraints
StegTalk ST-031 = real admissibility + scoring + edge/bearer selection
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

The tested integration performs no physical bearer transmission and grants no execution authority to the SDK. It proves that the current StegTalk ST-031 and KnowledgeVault source interoperate, persist the correct selection/lease evidence, reconstruct after restart, and preserve safe fallback semantics.

## Remaining activation boundary

The source/software integration and SDK demonstrator are now tested. Remaining work is runtime/physical proof:

- feed an actual StegWhisper v0.2 posture from a running messenger surface;
- persist a real runtime selection/lease into the connected personal KnowledgeVault rather than a temporary test vault;
- advertise at least two actual admitted device edges;
- execute through the selected physical/network bearer;
- observe delivery evidence returning to KnowledgeVault;
- restart/replace the selected edge and prove recovery against the connected vault;
- exercise the ST-029 modem/SIM path for actual SMS proof.

These runtime/physical items remain outside the SDK's authority and are not claimed complete by this validation.
