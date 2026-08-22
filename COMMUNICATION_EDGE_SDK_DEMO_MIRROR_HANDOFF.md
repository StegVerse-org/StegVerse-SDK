# Communication Edge SDK Demo Mirror Handoff

Status: PINNED_SOURCE_VALIDATION_PENDING
Repository: StegVerse-org/StegVerse-SDK
Validation branch: test/pinned-communication-source-integration
Date: 2026-08-22

## Purpose

Provide a public SDK conformance demonstration of the KnowledgeVault-hosted StegWhisper -> StegTalk ST-031 -> ephemeral-edge communication flow without moving execution, admissibility, bearer-selection, or continuity authority into the SDK.

## Implemented SDK demo

- `stegverse/communication_edge_demo.py`
- `examples/communication_edge_demo.json`
- `tests/test_communication_edge_demo.py`
- `scripts/run_communication_edge_demo.py`
- `.github/workflows/communication-edge-demo-validation.yml`

## Already observed SDK-only validation

Pull request `#54` validated the SDK simulator on Python 3.9, 3.11, and 3.12. Workflow run `32602726148` completed all three matrix jobs successfully, including compilation, dedicated pytest coverage, execution of the sample packet, and non-authorizing boundary checks.

## Pinned live-source integration proof

The validation lane is now extended with `scripts/run_pinned_communication_source_integration.py`.

It anonymously checks out these exact public source commits:

```text
StegVerse-Labs/StegTalk
2361d13ea09818f17aef5239ebf4771a161a0dc7

StegVerse-Labs/continuity-vault-kit
35e6d7ad881e0dea60ba191c49dfd4fba86e3fd7
```

The integration proof imports and executes the real `stegtalk.cross_edge_resolver` and real `execution.vault_store` from those pinned sources. It must prove:

1. ST-031 chooses the more capable `stegtalk-ip` edge over SMS under AUTO;
2. the ordered SMS fallback is retained;
3. an execution lease binds the attempt to the selected edge;
4. ambiguous post-dispatch state produces `VERIFY_EXTERNALLY`;
5. confirmed no-side-effect failure produces `TRY_FALLBACK` to the exact ordered edge;
6. the actual ST-031 selection receipt is persisted through `KnowledgeVaultExecutionStore.append_receipt()`;
7. lease/attempt state is persisted through `append_attempt()`;
8. a fresh `KnowledgeVaultExecutionStore` instance reconstructs both receipt and lease state after restart;
9. no physical transport execution or production-authority claim is inferred from the proof.

## Authority boundary

```text
SDK demo = compatibility/conformance simulation only
Pinned source integration = source-level executable integration proof
StegWhisper = messenger posture + constraints
StegTalk ST-031 = real admissibility + scoring + edge/bearer selection
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

A successful pinned-source proof closes the source integration and restart/reconstruction test boundary. It still does not prove physical bearer execution or production activation.

## Completion condition

The pinned-source validation branch must pass the expanded Python 3.9/3.11/3.12 matrix and execute the actual StegTalk + KnowledgeVault integration proof successfully. Exact workflow evidence will replace this pending state before merge.
