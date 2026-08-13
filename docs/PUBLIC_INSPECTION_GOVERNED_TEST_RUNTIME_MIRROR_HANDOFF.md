# Public Inspection Governed TEST Runtime Mirror Handoff

```text
goal_id: SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004
repository: StegVerse-org/StegVerse-SDK
branch: feat/public-inspection-governed-test-runtime
parent_handoff: docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_MERGE
release_state: NOT_RELEASED
```

This goal closes the preparation-only public testing gap.

A bounded public inspection request containing `input.steggate_request` can now execute through the canonical StegCore manifested-transaction path and return a real canonical StegCore `manifest_receipt_id`, governance state, exact-run evidence package, and reconstruction evidence.

Installed surfaces:

```text
stegverse/public_inspection_runtime.py
inspection/examples/governed-test-request.json
tests/test_public_inspection_runtime.py
pyproject.toml governed-test extra pinned to StegCore 8774a024ba6efe7e45d0846db70362f1836e7f36
README.md
SDK_README.md
docs/SDK_CONSOLE.md
docs/PUBLIC_INSPECTION_ENTRY.md
.github/PULL_REQUEST_TEMPLATE/public-inspection-request.md
```

Execution contract:

```text
public inspection request
-> bounded validation
-> canonical StegCore AdmissibilityRequest
-> run_manifested_transaction
-> canonical StegGate evaluation
-> side-effect-free TEST executor
-> ManifestReceiptRegistry
-> manifest_receipt_id + evidence + reconstruction
```

The SDK does not implement a parallel evaluator or receipt-ID algorithm.

Result boundary:

```text
runtime_mode: TEST
external_side_effect: false
local_exact_run_retained: true
production_master_records_custody: false
```

The local receipt ID is a canonical StegCore exact-run locator for the retained governed TEST run. It must not be described as production Master Records custody.

Public command, Python 3.11+:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

A public PR remains a declarative request/discussion carrier. Trusted SDK code runs the test; PR-supplied code is never used as evaluator/runtime authority.

Production continuation remains:

```text
trusted governed ingress
-> canonical StegCore governed run
-> MasterRecordsManifestReceiptProvider
-> admitted Master Records transport
-> exact-run production custody
-> caller projection
```
