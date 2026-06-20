# STEGVERSE SDK

![PyPI](https://img.shields.io/pypi/v/stegverse-sdk)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Build](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/sdk_demo_test.yml/badge.svg)
![License](https://img.shields.io/github/license/StegVerse-org/StegVerse-SDK)

> Execution is not assumed. Execution is admitted.

StegVerse verifies every action **before** it happens and produces cryptographic proof of that decision.

---

## WHAT IT DOES

You propose an action  
→ StegVerse evaluates it  
→ Decision: **ALLOW | DENY | DEFER**  
→ If allowed: execution + receipt

Every executed action produces a verifiable receipt.

---

## WHY THIS MATTERS

**Traditional flow**  
AI decides → executes → humans audit later

**StegVerse flow**  
AI proposes → evaluated at commit → executes only if admitted

This eliminates ungoverned execution at the point of irreversibility.

---

## FORMAL TESTING INGESTION ROUTE

The SDK is the ingestion point for formal testing datasets.

All datasets, fixtures, GLM-style boundary declarations, admissibility packets, sandbox tasks, and standing-proof artifacts should be manifest-bound and receipt-bound at SDK intake before any downstream test route consumes them.

```text
Dataset / fixture / governance artifact
→ StegVerse-org/StegVerse-SDK ingestion
→ manifest binding
→ receipt binding
→ declared formal testing route
→ route-specific result receipt
```

Formal testing routes:

| Route | Repository | Purpose |
|------|------------|---------|
| Public demo validation | `StegVerse-org/stegverse-demo-suite` | Reproducible public validation and explainable demo scenarios. |
| Formal demo runner | `StegVerse-org/demo-suite-runner` | GCAT/BCAT formalism probes and deterministic runner scenarios. |
| Rigorous sandbox testing | `StegGhost/entity-sandbox-runner` | Adversarial, entity, and bounded sandbox testing without outside-sandbox authority. |
| Standing proof | `StegVerse-Labs/Standing-Proof-Engine` | Commit-time standing, stale-state replay, authority rebinding, and consequence-binding proof. |
| Boundary / GLM case | `StegVerse-Labs/Boundary-Test` | Boundary declaration, non-claim preservation, and manifest composability validation. |

Route rule:

```text
SDK ingests.
GLM declares boundaries.
Demo-suite demonstrates.
Demo-suite-runner probes formalism behavior.
Sandbox stresses.
SPE proves standing.
Receipts bind every transition.
```

Route artifacts:

```text
docs/FORMAL_TESTING_ROUTE.md
schemas/formal-testing-route.schema.json
examples/formal_testing_route_manifest.json
scripts/validate_formal_testing_route.py
tests/test_formal_testing_route_manifest.py
```

Validate the example route manifest:

```bash
python scripts/validate_formal_testing_route.py examples/formal_testing_route_manifest.json
```

---

## QUICK START

### Install

```bash
pip install stegverse-sdk
```

### Example

```python
from stegverse import StegVerseSDK

sdk = StegVerseSDK()

result = sdk.submit_intent(
    action="deploy.compute",
    target="render.cluster",
    parameters={"gpu": "A100", "count": 4}
)

print(result["decision"])   # allow | deny | defer
print(result["receipt_id"])  # verifiable receipt
```

---

## SAFETY STACK

1. **Mathematical Gate (GCAT/BCAT)**
   - Evaluates admissibility at commit-time
   - Denies unsafe transitions by default

2. **Human Review**
   - Handles ambiguous edge cases

3. **Circuit Breakers**
   - Stops execution on system instability

4. **Consensus Controls**
   - Multi-party emergency halt

5. **Fail-Safe**
   - Defaults to denial if control is lost

---

## DYNAMIC ADMISSIBILITY PACKETS

The SDK is schema-aware of the dynamic admissibility packet family used by the StegVerse Site demo and includes local evaluator, bridge, bundle, receipt-reference, verifier, and bundle-check helpers.

Dynamic admissibility asks:

```text
What is this output, artifact, instruction, transition, or claim allowed to become?
```

Packet path:

```text
tester packet
→ discipline route
→ authority / evidence / replay / consequence checks
→ admissibility decision
→ result packet
→ local admissibility reference
→ governed admissibility bundle
→ bundle check
→ optional execution receipt attachment
```

SDK-visible schemas:

```text
schemas/admissibility/tester-output.schema.json
schemas/admissibility/dynamic-demo-result.schema.json
schemas/admissibility/llm-bridge-result.schema.json
schemas/admissibility/math-bridge-result.schema.json
schemas/admissibility/bridge-registry.schema.json
schemas/admissibility/admissibility-bundle.schema.json
schemas/admissibility/replay-result.schema.json
schemas/formal-testing-route.schema.json
```

SDK helper:

```python
from stegverse.admissibility import evaluate_admissibility_packet

result = evaluate_admissibility_packet(packet)
print(result["classification"]["decision"])
print(result["classification"]["allowed_next_state"])
```

Bundle helpers:

```python
from stegverse.admissibility_bundle import build_bundle_from_bridge_result
from stegverse.admissibility_replay import replay_admissibility_bundle

bundle = build_bundle_from_bridge_result(bridge)
check = replay_admissibility_bundle(bundle)
```

Bridge and bundle examples:

```bash
python examples/dynamic_admissibility_packet.py
python examples/list_dynamic_bridges.py
python examples/llm_dynamic_admissibility.py
python examples/math_dynamic_admissibility.py
python examples/admissibility_bundle_demo.py
python examples/admissibility_bundle_check.py
```

Receipt-reference examples:

```bash
python examples/admissibility_receipt_reference.py
python examples/verify_receipt_with_admissibility_reference.py
```

Execution receipts remain backward-compatible with `receipt_id`, `decision`, and `timestamp`. They may also carry `admissibility_receipt_reference`; when present, `verify_receipt(...)` validates that reference before accepting the receipt.

Reference docs:

```text
docs/DYNAMIC_ADMISSIBILITY.md
docs/FORMAL_TESTING_ROUTE.md
```

These packets align the SDK with the Site demo, applicability map, discipline test matrix, tester-output template, LLM bridge, math-solver bridge, Governed Admissibility Bundle exchange format, and the revised formal testing route map.

---

## LLM ADAPTER

Govern any LLM output before execution:

```python
from stegverse import StegVerseLLMAdapter, LLMProvider

adapter = StegVerseLLMAdapter()

result = adapter.govern_llm_output(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    prompt="Write a risk scoring function",
    output=llm_output
)
```

Returns:
- decision (allow | deny | defer)
- receipt
- reasoning

### Ecosystem Optimization

```python
result = adapter.optimize_ecosystem(
    ecosystem_metrics={"cpu": 0.85, "memory": 0.90},
    proposed_changes={"type": "scale", "cost": 5000}
)
```

---

## THE MODEL

Legitimacy constraint:

```
Φ(x) = K · g^α · c^β · t^γ − a
```

Where:
- g = governance capacity
- c = constraints
- a = action pressure
- t = trust

Decision rule:
- Φ(x) ≥ 0 → ALLOW
- Φ(x) < 0 → DENY

---

## INTEGRATION

| Downstream | Consumes |
|------------|----------|
| TV/TVC | Ephemeral secrets via TrustVault |
| GCAT-BCAT-Engine | Deployment verification |
| demo_ingest_engine | Orchestrated ingestion |
| AaCT-E | Audit trail |
| StegDB | State monitoring |
| Site demo | Dynamic admissibility tester packets |
| Applicability map | Discipline routes and tester-output templates |
| LLM bridge | LLM output to dynamic admissibility packet |
| Math bridge | Formalism artifact to dynamic admissibility packet |
| GAB | Portable governed admissibility bundle exchange |
| Bundle check | Local bundle re-evaluation and posture comparison |
| Receipts | Optional admissibility receipt references |
| formal-testing-route schema | Manifest-bound formal testing route declaration |
| formal-testing-route validator | Local validation for SDK-bound route manifests |
| stegverse-demo-suite | SDK-bound public validation datasets |
| demo-suite-runner | SDK-bound formal runner datasets |
| entity-sandbox-runner | SDK-bound sandbox task packets |
| Standing-Proof-Engine | SDK-bound standing-proof artifacts |
| Boundary-Test | SDK-bound GLM and boundary declaration fixtures |

---

## LINKS

- Docs: https://stegverse.org/docs
- API: https://api.stegverse.org
- Issues: https://github.com/StegVerse-org/StegVerse-SDK/issues
- Ingestion: https://github.com/StegVerse-org/demo_ingest_engine
- Email: sdk@stegverse.org

---

## ONE LINE

StegVerse enforces commit-time governance with verifiable execution receipts.
