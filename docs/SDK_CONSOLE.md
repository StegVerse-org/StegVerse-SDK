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

A governed test must be recorded in Master Records. The SDK requires an admitted Master Records endpoint before it starts the canonical StegCore run and will not report success until exact-run custody returns `RECORDED`.

```bash
export MASTER_RECORDS_URL="<admitted-master-records-base-url>"
export MASTER_RECORDS_AUTH_TOKEN="<authorized-token>"
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
```

The TEST consequence executor performs no external side effect. Canonical governance transitions are still ecosystem transitions and are retained in the exact-run Master Records evidence package.

## Replay — option 1

Replay is operational. It does not rewrite the original exact-run record or invoke its consequence executor. The replay operation itself creates a new ecosystem trajectory that is recorded before the artifact is returned:

```text
REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
```

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

A successful replay result includes an `operation_id`, original/replay comparisons, `consequence_reexecuted: false`, `original_record_mutated: false`, `operation_transition_custody_status: RECORDED`, and the Master Records operation-event receipts.

If any replay transition cannot be recorded, the SDK fails closed and does not return a successful replay artifact.

## Reconstruction — option 2

Reconstruction does not rewrite the original exact-run record or re-execute its consequence. Its own request/derivation/return path is recorded:

```text
REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

The reconstruction artifact distinguishes persisted historical evidence from derived material and includes its `operation_id`, `operation_transition_custody_status: RECORDED`, and Master Records operation-event receipts.

## State-transition rule

```text
original record is immutable
original consequence is not re-executed by replay/reconstruction
replay/reconstruction still create operation state transitions
all such transitions are recorded in Master Records
caller artifact is returned only after RETURNED is RECORDED
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
replay overwrites original history: false
replay executes original consequence: false
replay transitions bypass Master Records: false
reconstruction re-executes original consequence: false
reconstruction transitions bypass Master Records: false
```
