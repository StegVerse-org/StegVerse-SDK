# StegVerse SDK Console

The console is the generic public entry point for developers, testers, evaluators, humans, and assisting LLMs. It exposes discoverable SDK guidance and callable surfaces without creating person-specific routes or authority.

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

A public PR may carry bounded declarative request data matching `inspection/request.schema.json`. The PR is a visible request/discussion record, not evaluator code or Master Records custody.

Preparation only:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

That path intentionally stops with no governed runtime execution and no receipt locator.

## Actual governed TEST execution

A governed test must be recorded in Master Records. The SDK therefore requires an admitted Master Records endpoint before it starts the canonical StegCore run, and it will not report the run as successful until exact-run custody returns `RECORDED`.

```bash
export MASTER_RECORDS_URL="<admitted-master-records-base-url>"
export MASTER_RECORDS_AUTH_TOKEN="<authorized-token>"
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json
```

A successful command returns:

```text
governance_state
manifest_receipt_id
transaction_id
chain_verified
master_records_custody_status: RECORDED
master_records_custody_receipt
```

The TEST consequence executor performs no external side effect. The canonical governance transitions are nevertheless retained in the complete exact-run Master Records evidence package.

## Local canonical Master Records for isolated testing

A tester who is not using a shared admitted deployment may run the canonical `master-records/orchestration` custody application locally. This is still the Master Records implementation; the SDK does not duplicate its storage semantics.

From a neighboring checkout, configure local test-only credentials and storage and start the canonical custody app, for example:

```bash
git clone https://github.com/master-records/orchestration.git ../master-records-orchestration
export PYTHONPATH="../master-records-orchestration:${PYTHONPATH}"
export MASTER_RECORDS_AUTH_TOKEN="local-test-token"
export MASTER_RECORDS_RECEIPT_KEY="local-test-receipt-key"
export MASTER_RECORDS_DB="$PWD/.stegverse/master-records.db"
python -m uvicorn services.canonical_custody_app:app --host 127.0.0.1 --port 8787
```

Then point the SDK at that canonical local Master Records instance:

```bash
export MASTER_RECORDS_URL="http://127.0.0.1:8787"
export MASTER_RECORDS_AUTH_TOKEN="local-test-token"
```

A local Master Records instance is not a production-activation claim; it is a canonical custody implementation used for isolated testing.

## Replay — option 1

Replay is operational, not guidance-only. It reads the retained exact-run package from Master Records, reconstructs the canonical StegCore governance request, and re-evaluates it without invoking the consequence executor:

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

The replay result reports:

```text
original_disposition
replay_disposition
deterministic_disposition_match
candidate_identity_match
consequence_reexecuted: false
original_record_mutated: false
```

Replay is read-only, so it does not create a new ecosystem state transition.

## Reconstruction — option 2

Reconstruction is operational through the canonical Master Records reconstruction route:

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

The returned reconstruction distinguishes persisted historical evidence from derived reconstruction material and must report:

```text
original_record_mutated: false
consequence_reexecuted: false
reconstruction_grants_authority: false
```

Reconstruction is read-only and therefore does not create a new ecosystem state transition.

## Custody ordering

```text
bounded request
-> canonical StegCore manifested transaction
-> complete transition chain
-> canonical manifest_receipt_id
-> full exact-run Master Records custody
-> caller result
```

Caller return projection and explanatory labels never suppress Master Records custody.

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

## Authority boundary

```text
public PR grants runtime authority: false
public PR creates custody: false
governed run success without Master Records custody: false
manifest_receipt_id grants authority: false
return projection changes custody: false
replay overwrites history: false
replay executes consequence: false
reconstruction re-executes consequence: false
```
