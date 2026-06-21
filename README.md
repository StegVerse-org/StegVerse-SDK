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

## ECOSYSTEM CHAT SDK INTAKE

The SDK now includes a pre-backend intake validator, transport-free backend handler, and HTTP adapter for the completed Site Ecosystem Chat form gateway.

```python
from stegverse.ecosystem_chat_http import handle_ecosystem_chat_http

status, response = handle_ecosystem_chat_http(
    "POST",
    "/api/ecosystem-chat",
    request_body,
)
```

The adapter accepts the Site three-layer payload only when `fields`, `manifest`, and `receipt_window` remain distinct and internally consistent. In this stage, `receipt_id` remains `None`; receipt issuance is not installed in the Site-facing intake path.

Artifacts:

```text
stegverse/ecosystem_chat_intake.py
stegverse/ecosystem_chat_backend.py
stegverse/ecosystem_chat_http.py
docs/ECOSYSTEM_CHAT_SDK_INTAKE.md
tests/test_ecosystem_chat_intake_minimal.py
tests/test_ecosystem_chat_backend.py
tests/test_ecosystem_chat_http_minimal.py
```

---

## WHY THIS MATTERS

**Traditional flow**  
AI decides → executes → humans audit later

**StegVerse flow**  
AI proposes → evaluated at commit → executes only if admitted

This eliminates ungoverned execution at the point of irreversibility.

---

## FORMAL TESTING INGESTION ROUTE

The SDK and LLM Adapter are the user-facing intake boundary for formal testing datasets.

Correct testing data loop:

```text
User
→ StegVerse-org/StegVerse-SDK or LLM Adapter
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner ingestion/CGE return validation
→ StegVerse-org ingestion
→ User
```

Every ingestion point sends an action receipt to `master-records`.

Route artifacts:

```text
docs/FORMAL_TESTING_ROUTE.md
schemas/testing-data-loop.schema.json
schemas/testing-data-loop-handoff.schema.json
examples/testing_data_loop.json
examples/testing_data_loop_handoff.json
schemas/formal-testing-route.schema.json
schemas/formal-testing-route-result.schema.json
examples/formal_testing_route_manifest.json
examples/formal_testing_route_result_receipt.json
scripts/validate_formal_testing_route.py
tests/test_testing_data_loop.py
tests/test_testing_data_loop_handoff.py
tests/test_formal_testing_route_manifest.py
tests/test_formal_testing_route_result_receipt.py
```

Validate the corrected loop and handoff:

```bash
python scripts/validate_formal_testing_route.py --kind loop examples/testing_data_loop.json
python scripts/validate_formal_testing_route.py --kind handoff examples/testing_data_loop_handoff.json
```

Validate the legacy route manifest and route result receipt:

```bash
python scripts/validate_formal_testing_route.py examples/formal_testing_route_manifest.json
python scripts/validate_formal_testing_route.py --kind result examples/formal_testing_route_result_receipt.json
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
schemas/testing-data-loop.schema.json
schemas/testing-data-loop-handoff.schema.json
schemas/formal-testing-route.schema.json
schemas/formal-testing-route-result.schema.json
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

These packets align the SDK with the Site demo, applicability map, discipline test matrix, tester-output template, LLM bridge, math-solver bridge, Governed Admissibility Bundle exchange format, and the corrected formal testing data loop.

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
| Ecosystem Chat | Three-layer Site form payloads through SDK intake validator |
| Applicability map | Discipline routes and tester-output templates |
| LLM bridge | LLM output to dynamic admissibility packet |
| Math bridge | Formalism artifact to dynamic admissibility packet |
| GAB | Portable governed admissibility bundle exchange |
| Bundle check | Local bundle re-evaluation and posture comparison |
| Receipts | Optional admissibility receipt references |
| testing-data-loop schema | Correct user-to-sandbox-to-user route declaration |
| testing-data-loop-handoff schema | Step-to-step receipt-gated handoff shape |
| formal-testing-route schema | Legacy manifest-bound formal testing route declaration |
| formal-testing-route-result schema | Route result receipt shape |
| route validator | Local validation for loop, handoff, manifest, and result artifacts |
| entity-sandbox-runner | SDK-bound sandbox task packets and bounded result return |
| master-records | Action receipts from every ingestion point |
| stegverse-demo-suite | Receipt-bound public validation outputs |
| demo-suite-runner | Receipt-bound formal runner outputs |
| Standing-Proof-Engine | Receipt-bound standing-proof artifacts |
| Boundary-Test | Receipt-bound GLM and boundary declaration fixtures |

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
