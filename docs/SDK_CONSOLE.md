# StegVerse SDK Console

The console is the generic public entry point for developers, testers, evaluators, humans, and assisting LLMs. It exposes discoverable SDK guidance and locally callable surfaces without creating person-specific routes or authority.

## Install

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

## Canonical governance navigation

```bash
stegverse governance
```

```text
[000] Demo test sequence without user-supplied manifest
[00]  User-defined run parameters
[0]   Submit data for governance
[1]   Replay previously run set
[2]   Reconstruct previously run set
```

`000` and `00` are optional. Machines or LLMs that already understand the canonical manifest profile can use ordinary governed ingress directly.

## Public inspection requests

A public PR may carry bounded declarative request data matching `inspection/request.schema.json`. The PR is a visible request/discussion record, not evaluator code or production custody.

Preparation only:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

That path intentionally stops with no runtime execution and no receipt locator.

## Actual governed TEST execution

To run the submitted test data through canonical StegCore governance and get a result back, use Python 3.11+ and install the pinned governed-test extra:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

The governed TEST command returns:

```text
governance_state
manifest_receipt_id
transaction_id
chain_verified
evidence_package
reconstruction
```

The exact run is retained in the local append-only canonical StegCore test registry and transaction ledger under `.stegverse/public-inspection/` by default. The TEST executor performs no external side effect.

The returned `manifest_receipt_id` is a real canonical StegCore exact-run locator for that locally retained governed TEST run. It is not a production Master Records custody claim.

## Production custody boundary

Production custody is a separate stronger path:

```text
trusted governed ingress
-> canonical StegCore governance
-> admitted Master Records exact-run custody
-> caller projection
-> production-custodied manifest_receipt_id
```

Do not equate local governed TEST retention with production Master Records custody.

## Replay and reconstruction

A `manifest_receipt_id` is a locator, not authority. Replay must not overwrite history or re-execute consequence. Reconstruction must distinguish retained historical evidence from later derived material.

## Lower-level surfaces

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
stegverse run <surface> [options]
```

## Validation

```bash
pytest tests/ -v
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
```

With the governed-test extra installed:

```bash
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

## Authority boundary

```text
public PR grants runtime authority: false
public PR creates production custody: false
local TEST registry equals production custody: false
manifest_receipt_id grants authority: false
return projection changes custody: false
replay overwrites history: false
reconstruction re-executes consequence: false
```
