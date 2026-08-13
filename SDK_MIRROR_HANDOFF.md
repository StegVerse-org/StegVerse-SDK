# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, validation evidence, scoped mirror handoffs, and this file supersede prior chat claims. Historical detail remains available in Git history.

## Goal inventory

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004: INSTALLED_PENDING_MERGE, NOT_RELEASED
```

No person-specific evaluator route is canonical.

## Governed public inspection TEST runtime

Current branch: `feat/public-inspection-governed-test-runtime`

Installed surfaces:

```text
stegverse/public_inspection_runtime.py
inspection/examples/governed-test-request.json
tests/test_public_inspection_runtime.py
pyproject.toml -> governed-test extra pinned to StegCore 8774a024ba6efe7e45d0846db70362f1836e7f36
README.md
docs/PUBLIC_INSPECTION_ENTRY.md
.github/PULL_REQUEST_TEMPLATE/public-inspection-request.md
```

A bounded public inspection request containing `input.steggate_request` can now be executed through the canonical StegCore manifested-transaction implementation in side-effect-free TEST mode. The runtime registers the exact run in StegCore's append-only local `ManifestReceiptRegistry` and returns:

```text
governance_state
manifest_receipt_id
transaction_id
chain_verified
evidence_package
reconstruction
```

This closes the prior SDK preparation-only gap for local governed testing. The returned locator is a canonical StegCore exact-run locator for the locally retained governed TEST run; it is not fabricated.

## Critical custody distinction

```text
local governed TEST retention != production Master Records custody
```

The SDK TEST runtime explicitly returns:

```text
runtime_mode: TEST
external_side_effect: false
local_exact_run_retained: true
production_master_records_custody: false
```

Production custody still requires the separately admitted `MasterRecordsManifestReceiptProvider` transport and Master Records readiness boundary.

## Public use

Python 3.11+:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

The PR template now documents both validation-only and governed TEST execution. A public PR remains a visible declarative request/discussion carrier; PR-supplied code is never used as the evaluator/runtime.

## Previous governed-binding source of truth

`docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md` records the preparation-only option `0A` binding. That preparation surface remains valid for callers who want to inspect the descriptor without executing a governed TEST.

## Cross-repository ownership

```text
Provider/runtime translation where applicable: StegVerse-org/LLM-adapter
Canonical governance and exact-run semantics: StegVerse-Labs/StegCore
Production exact-run custody: master-records/orchestration
```

## Remaining stronger integration goal

```text
goal: PUBLIC-INSPECTION-END-TO-END-CUSTODY-003
state: PRODUCTION_CUSTODY_NOT_YET_CLAIMED
```

The remaining stronger goal is not “get a governed result from the public SDK” anymore. That capability is installed in the governed TEST runtime. The remaining goal is to prove the same exact-run contract across admitted production Master Records custody, then verify replay/reconstruction through that shared backing.

## Release and propagation

The governed TEST runtime is not yet a product release. Do not cut a product tag until merge and applicable release gates are satisfied. Site/Publisher/wiki propagation is not triggered by this unmerged SDK integration.

## Archive condition

Do not archive this active SDK goal until PR review/merge and post-merge handoff reconciliation are complete.
