# StegVerse SDK

The StegVerse SDK is a public governance experiment and validation environment for StegGate-style admissibility, AdmittedCode receipt verification, LLM/agent outputs, governed submissions, replay, reconstruction, and inspectable request/receipt boundaries.

A request, manifest, model output, validation result, receipt, or receipt locator does **not** become execution authority merely because it validates.

## 90-second start

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse governance
```

Canonical human-facing navigation:

| Option | Meaning |
|---|---|
| `000` | Optional worked transparency/demo sequence |
| `00` | Optional return/explanation preferences |
| `0` | Ordinary governed submission |
| `1` | Replay by `manifest_receipt_id` |
| `2` | Reconstruction by `manifest_receipt_id` |

Direct help is also available:

```bash
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
```

`000` and `00` are optional human/LLM transparency surfaces. A machine that already understands `stegverse.ingress-manifest.v1` can construct an ordinary governed submission directly.

## Run the canonical governed TEST locally

The public inspection runtime is sovereign/local by default. It uses the canonical pinned Core-Lite, StegCore/StegGate, and Master Records implementations and does **not** require Render, Vercel, GitHub Actions, or another hosted runtime.

Install the pinned governed-test dependencies:

```bash
python -m pip install -e ".[dev,governed-test]"
```

Then run a governed test request:

```bash
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json
```

The default local custody file is:

```text
./stegverse-master-records-validation.db
```

You may choose another local path explicitly:

```bash
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json \
  --custody-db ./my-validation-custody.db
```

A successful run returns a canonical governance state, one continuous transaction identity, manifested-route receipts, a `manifest_receipt_id`, verified StegCore receipt-chain status, and `master_records_custody_status: RECORDED`.

The governed TEST uses a deliberately simulated consequence executor:

```text
external_side_effect: false
third_party_host_required: false
```

The governance and custody transitions are real TEST evidence; the test does not perform the proposed external consequence.

## No caller-managed protected runtime credentials

The sovereign evaluator path requires no GitHub token and no caller-managed protected Master Records credential.

```text
GitHub token runtime authority: NONE
public caller credential authority: NONE
protected runtime credential semantics: TV/TVC
```

The optional governed-test dependencies are pinned to public repository commits. GitHub is a source-distribution surface here, not StegVerse runtime authority.

## Frozen evaluator validation — T0 / T1-A / T1-B

The canonical sovereign path has already been exercised against the frozen evaluator cases. Retained validation evidence is in:

```text
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
```

Results:

```text
T0   original $420 state                                 -> ALLOW
T1-A same $420, materially changed current policy state  -> DENY
T1-B $4,200 candidate retaining earlier $420 binding     -> DENY
```

Exact-run `manifest_receipt_id` values:

```text
T0   MR-2F21EC98FB60A78DD0135E580DD80B1FE6CEC9C62B905A4F758E5567F1C666E2
T1-A MR-620DDEE41541E2F787BC2702FE56977F4BB298BC1CE34C4284203A429F5453C8
T1-B MR-804AF43FC68949F0BBC4B89E4729CA1880AB5BFA4655185C171CE5D2332487B4
```

For all three cases, retained evidence records:

```text
StegCore receipt chain verified: PASS
Master Records exact-run custody: PASS
manifested route transitions: 10/10
one transaction identity across each route: PASS
replay operation custody: PASS
reconstruction operation custody: PASS
replay/reconstruction consequence reexecution: FALSE
third-party host required: FALSE
```

The corresponding portable custody snapshot is retained by `master-records/orchestration` at `validation/evaluator-frozen-sovereign-custody-2026-08-13.zlib.b64`.

## Replay — option 1

Replay uses the exact-run locator and does not overwrite the original run or re-execute its original consequence.

```bash
python -m stegverse.public_inspection_runtime replay \
  MR-<SHA256>
```

Replay itself is new ecosystem history and records this operation trajectory before returning its artifact:

```text
REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
```

## Reconstruction — option 2

```bash
python -m stegverse.public_inspection_runtime reconstruct \
  MR-<SHA256>
```

Reconstruction does not re-execute the original consequence. Its own operation trajectory is recorded before the artifact is returned:

```text
REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

## Public inspection requests

A contributor may create a visible declarative inspection request through an ordinary pull request using:

```text
.github/PULL_REQUEST_TEMPLATE/public-inspection-request.md
inspection/request.schema.json
```

A pull request is a collaboration/request record only. It is not evaluator code, runtime authority, release authority, or custody authority.

Validate or prepare a request without executing governance:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

## Focused subsystem experiments

The five-option governance navigator is the broad experiment workflow. Focused lower-level surfaces remain available:

```bash
stegverse surfaces
stegverse capabilities
stegverse help-surface admittedcode
stegverse demo admittedcode
```

Current focused surfaces include:

```text
admittedcode
admissibility
llm-admissibility
math-admissibility
universal-entry
bridges
entry-points
```

AdmittedCode is a portable receipt-verification experiment. It is not the whole governance workflow. A valid DENY receipt can be SDK `ACCEPTED` because receipt validation preserves the underlying DENY rather than converting it into permission.

A local LLM-output posture experiment can be run without calling a hosted model:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

## Local model/runtime ownership

The former descriptive “select a local model/runtime” step is obsolete. Executable local-model discovery, launch, private serving, inference, measurement, and proof plus the formally developed `stegverse-reference-lm-v1` are complete and released in `StegVerse-002/micro-node-runtime`.

The SDK does not duplicate that model/runtime authority. LLM provider/runtime translation belongs to `StegVerse-org/LLM-adapter`; route and protected credential semantics remain with TV/TVC.

## Core invariants

```text
observation != inference
inference != intent
intent != instruction
instruction != authorization
authorization != admissibility
submission != execution
manifest validity != ALLOW
receipt acceptance != action approval
manifest_receipt_id != authority
public PR != runtime authority
replay != historical rewrite
reconstruction != consequence re-execution
provider output != authority
GitHub != runtime authority
```

## Validate the checkout

```bash
pytest tests/ -v
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
```

Full console documentation: `docs/SDK_CONSOLE.md`.

## Repository control files

Files matching `*_MIRROR_HANDOFF.md` preserve implementation continuity, validation state, task ownership, supersession, and archive conditions. They are project-control records, not evaluator commands. The public SDK should remain usable from this README plus installed console/help output without a private instruction channel.
