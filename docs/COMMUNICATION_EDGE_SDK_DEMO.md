# Communication Edge SDK Demo

This demo shows how a KnowledgeVault-hosted communication request can express a messenger posture, evaluate multiple admitted edges, select the best currently admissible bearer, preserve an ordered fallback, and reconstruct selection/lease evidence after restart.

It is deliberately **non-authorizing**.

```text
SDK demo = compatibility/conformance simulation only
StegWhisper = messenger posture + constraints
StegTalk ST-031 = bearer admissibility + scoring + edge/bearer selection
KnowledgeVault = durable attempt/receipt/recovery truth
Edge device = ephemeral execution capability
```

A successful demo or test does **not** prove physical transport execution, production activation, or delivery to a real recipient.

## 60-second demo

Install the SDK from a clone:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

Then run the installed SDK command:

```bash
stegverse-comm-demo
```

No packet path is required. The command loads the deterministic packet packaged inside `stegverse.demo_data`, so the demo remains available through an installed SDK instead of depending on the repository `examples/` directory.

The repository copy remains at:

```text
examples/communication_edge_demo.json
```

The sample defines two admitted edges:

- a higher-capability `stegtalk-ip` gateway;
- an SMS-capable phone retained as fallback.

Under `AUTO`, the expected selection is `stegtalk-ip`, with SMS retained as the first ordered fallback.

The output is deterministic JSON containing the selected edge/bearer, fallback order, excluded paths and reasons, selection hash, and recovery scenarios.

Expected boundary fields include:

```text
sdk_simulation_only = true
authority_granted = false
execution_performed = false
```

For compact machine-oriented JSON:

```bash
stegverse-comm-demo --compact
```

The repository runner is retained as a source-level equivalent:

```bash
python scripts/run_communication_edge_demo.py examples/communication_edge_demo.json
```

CI verifies that the installed command and repository runner produce the same result.

## Run the conformance tests

```bash
python -m pytest tests/test_communication_edge_demo.py -q
```

The test suite currently proves:

1. native StegTalk can outrank SMS when it preserves more capability;
2. ambiguous post-dispatch state resolves to `VERIFY_EXTERNALLY` rather than automatic fallback;
3. confirmed pre-side-effect failure may use exactly the ordered fallback;
4. remote-edge denial keeps selection on the declared current edge;
5. an UNKNOWN recipient uses only explicitly declared safe fallback bearers;
6. an unattested high-scoring edge is excluded;
7. no admissible edge fails closed;
8. identical packets produce identical selections and selection hashes.

## Run a custom capability packet

Copy the sample packet and edit it:

```bash
cp examples/communication_edge_demo.json /tmp/my-communication-edge.json
```

Then run it through the installed SDK command:

```bash
stegverse-comm-demo /tmp/my-communication-edge.json
```

A packet supplies:

```text
attempt_id
posture
recipient capability state
hard/cross-edge constraints
edge advertisements
bearer availability
normalized capability metrics
```

Important recipient states:

```text
KNOWN       -> use declared accepted bearers
UNKNOWN     -> only explicit safe fallback bearers may be considered
UNREACHABLE -> fail closed; no route is fabricated
```

Important cross-edge policy:

```text
remote_edge_execution_authorized = true | false
multipath_authorized = true | false
current_edge_id = required when remote-edge execution is denied
```

Capability is multidimensional. The resolver/demo evaluates normalized dimensions including:

```text
security
privacy
recipient compatibility
reliability
receipt quality
bidirectionality
resilience
latency
bandwidth
cost
energy
metadata minimization
```

A posture changes ranking weights; it does not make an otherwise inadmissible path admissible.

## Inspect fallback safety

The demo models the same core recovery invariant used by ST-031/KnowledgeVault:

```text
DELIVERED / ACKNOWLEDGED / EXECUTED
    -> STOP

INDETERMINATE / TIMEOUT_AFTER_DISPATCH / UNKNOWN_AFTER_DISPATCH
    -> VERIFY_EXTERNALLY

FAILED without confirmed side-effect absence
    -> VERIFY_EXTERNALLY

FAILED with confirmed side-effect absence
    -> TRY_FALLBACK using the exact ordered fallback
```

Uncertainty never becomes permission to duplicate a side effect.

## Reproduce the pinned real-source integration proof

The dedicated GitHub Actions workflow goes beyond the SDK simulator. It checks out exact public StegTalk and KnowledgeVault source commits without using them as runtime authority and executes their real source together.

The same proof can be reproduced from a working SDK checkout:

```bash
git clone --no-checkout https://github.com/StegVerse-Labs/StegTalk.git /tmp/StegTalk
git -C /tmp/StegTalk checkout 2361d13ea09818f17aef5239ebf4771a161a0dc7

git clone --no-checkout https://github.com/StegVerse-Labs/continuity-vault-kit.git /tmp/continuity-vault-kit
git -C /tmp/continuity-vault-kit checkout 35e6d7ad881e0dea60ba191c49dfd4fba86e3fd7

python scripts/run_pinned_communication_source_integration.py \
  --stegtalk-repo /tmp/StegTalk \
  --kv-repo /tmp/continuity-vault-kit
```

This source-integration proof exercises the real `stegtalk.cross_edge_resolver` and the real `execution.vault_store`. It verifies:

- `stegtalk-ip` selection over SMS under the sample AUTO posture;
- exact ordered SMS fallback;
- execution lease creation;
- actual ST-031 selection receipt persistence through KnowledgeVault;
- attempt/lease persistence;
- reconstruction from a fresh KnowledgeVault store instance after restart;
- `VERIFY_EXTERNALLY` after ambiguous dispatch;
- `TRY_FALLBACK` only after confirmed no-side-effect failure.

It still deliberately reports:

```text
runtime_execution_performed = false
physical_transport_proven = false
```

## CI validation

`.github/workflows/communication-edge-demo-validation.yml` runs the installed command, repository runner, and pinned source-integration proof on:

```text
Python 3.9
Python 3.11
Python 3.12
```

The workflow installs the SDK, compiles the demo and CLI, runs the conformance suite, executes both demo entry points, requires their JSON results to be identical, verifies the SDK authority boundary, checks out the pinned real sources, executes the source-integration proof, and verifies restart/fallback invariants.

Observed validation is recorded in `COMMUNICATION_EDGE_SDK_DEMO_MIRROR_HANDOFF.md`.

## What this proves vs. what it does not

| Surface | Demonstrated here? |
|---|---|
| Installed SDK command works independently of `examples/` path | Yes, when validation is green |
| Messenger posture/cross-edge semantics | Yes |
| Deterministic best-admissible selection behavior | Yes |
| Ordered fallback and ambiguity suppression | Yes |
| Real pinned ST-031 source interoperability | Yes |
| Real pinned KnowledgeVault persistence/restart reconstruction | Yes |
| SDK grants execution authority | No — explicitly prohibited |
| Physical edge capability advertisement | No |
| Physical/network bearer transmission | No |
| Real recipient delivery | No |
| ST-029 modem/SIM activation | No |
| Production activation | No |

The next activation boundary belongs to the running StegTalk/StegWhisper/KnowledgeVault system, not the SDK: advertise actual admitted edges, originate a real connected-KnowledgeVault attempt, execute the selected bearer, return delivery evidence, and prove recovery after edge restart/replacement without duplicate dispatch.
