# Public Inspection Governed Binding Mirror Handoff

## Authority

```text
goal_id: SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002
repository: StegVerse-org/StegVerse-SDK
branch: feat/public-inspection-governed-binding
parent_handoff: docs/PUBLIC_INSPECTION_ENTRY_MIRROR_HANDOFF.md
repository_handoff: SDK_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_VALIDATION
release_state: NOT_RELEASED
```

## Goal

Bind the merged public inspection request format to the ordinary SDK governed submission path without creating a separate evaluator/runtime, GitHub authority path, or false custody claim.

## Installed implementation

```text
stegverse/public_inspection.py
tests/test_public_inspection_governed_binding.py
```

The adapter maps a validated public inspection request to `build_raw_submission_descriptor(...)` with ordinary governance option `0A` and `ingress_mode: sdk_manifested_raw_data`.

Preparation is explicitly non-authorizing and non-custodial:

```text
runtime_processing_status: NOT_RUN
master_records_custody_status: NOT_CLAIMED
manifest_receipt_id: null
authority_claim: false
github_grants_runtime_authority: false
```

## Documentation surfaces in this change

```text
README.md
SDK_README.md
docs/SDK_CONSOLE.md
docs/PUBLIC_INSPECTION_ENTRY.md
docs/PUBLIC_INSPECTION_ENTRY_MIRROR_HANDOFF.md
SDK_MIRROR_HANDOFF.md
```

`SDK_README.md` is retained only as a compatibility pointer so it cannot continue to publish stale legacy SDK semantics in parallel with `README.md`.

## Validation gate

Required before merge:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m stegverse.public_inspection inspection/examples/example-request.json
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
```

The prepared example must identify option `0A`, make no runtime/custody claim, and return no fabricated `manifest_receipt_id`.

## Remaining cross-repository gap

This SDK goal ends at trusted preparation for ordinary governed ingress. It does not claim that the prepared request has traversed StegCore or canonical Master Records custody.

The next integration owner sequence is:

```text
StegVerse-SDK prepared option 0A request
-> admitted ordinary ingress / LLM-adapter where applicable
-> StegCore canonical governance
-> master-records/orchestration exact-run custody
-> caller projection
-> actual manifest_receipt_id
-> optional publication of that locator back to the public PR
```

Do not mark this next cross-repository sequence complete until inspectable runtime and custody evidence exists.
