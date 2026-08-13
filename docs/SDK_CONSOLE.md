# StegVerse SDK Console

The console is the public entry point for developers, testers, evaluators, humans, and assisting LLMs.

## Install

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

## Governance navigation

```bash
stegverse governance
```

```text
[000] worked transparency/demo
[00]  user-defined return/explanation preferences
[0]   ordinary governed submission
[1]   replay by manifest_receipt_id
[2]   reconstruction by manifest_receipt_id
```

Direct help:

```bash
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
```

`000` and `00` are optional. Machines that already understand the canonical manifest profile can use ordinary governed ingress directly.

## Run the sovereign governed TEST

Install the pinned canonical test components:

```bash
python -m pip install -e ".[dev,governed-test]"
```

Run:

```bash
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
```

The default runtime is local and uses canonical pinned Core-Lite, StegCore/StegGate, and Master Records implementations. Its consequence is simulated and produces no external side effect. The test records the governance and route evidence locally before reporting success.

Default local custody file:

```text
./stegverse-master-records-validation.db
```

The sovereign evaluator path does not require a hosted evaluator or a GitHub token as runtime authority.

## Replay

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

Replay preserves the original run and does not invoke the original consequence. Its own operation history is recorded before return.

## Reconstruction

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

Reconstruction preserves the original run and does not re-execute the original consequence. Its own operation history is recorded before return.

## Frozen evaluator evidence

See:

```text
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
```

The retained T0/T1-A/T1-B validation records exact-run custody, manifested-route custody, replay custody, and reconstruction custody as PASS on the sovereign path.

## Focused subsystem tests

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

Focused surfaces include `admittedcode`, `admissibility`, `llm-admissibility`, `math-admissibility`, `universal-entry`, `bridges`, and `entry-points`.

AdmittedCode example:

```bash
stegverse demo admittedcode
```

LLM-output example:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

## Public inspection request preparation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

Preparation does not claim a governed run or produce a receipt locator.

## Authority boundary

```text
submission != execution
validation != authority
receipt locator != authority
replay != historical rewrite
reconstruction != consequence re-execution
provider output != authority
GitHub != StegVerse runtime authority
```

The current README is the primary public quick-start document and should remain synchronized with this console reference.
