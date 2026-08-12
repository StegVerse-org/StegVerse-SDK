# Manifest Receipt Navigation Mirror Handoff

## Authority

```text
goal_id: SDK-MANIFEST-RECEIPT-NAVIGATION-001
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
issue: #16
implementation_state: INSTALLED_UNVALIDATED
release_state: NOT_RELEASED
```

## Installed surfaces

```text
stegverse/governance_navigation.py
stegverse/cli.py
tests/test_governance_navigation.py
```

Installation commits:

```text
f36f9e10c558c22e6668e98bdc4614503b6bd160  navigation + ingress profile contract
25de84e1febfe021c35d4208dc84cd6a32d15edc  initial tests
78498596670ed1fd02943bd914c5d755ab18f211  CLI governance menu
b49a313705fec266b825bce77e2668cf4231a2eb  guidance test correction
```

## User contract

The CLI exposes:

```text
[0] Submit data for governance
[1] Replay previously run set
[2] Reconstruct previously run set
```

Each selection displays process guidance before requesting the next input.

Option 0 explicitly supports:

```text
0A raw/user data -> SDK creates manifest
0B preformatted machine manifest -> validate/canonicalize accepted ingress profile
```

Canonical external ingress profile:

```text
stegverse.ingress-manifest.v1
```

A structurally valid machine manifest means only that the machine output is acceptable for governance. It never means ALLOW and never grants execution authority.

## Cross-repository implementation now available

```text
StegVerse-Labs/StegCore/src/stegcore/manifest_receipts.py
StegVerse-Labs/StegCore/src/stegcore/manifest_receipt_provider.py
  canonical manifest_receipt_id + evidence/replay/reconstruct semantics and shared-backing contract

master-records/orchestration/services/manifest_receipt_custody.py
master-records/orchestration/services/manifest_receipt_custody_api.py
master-records/orchestration/services/canonical_custody_app.py
master-records/orchestration/render-custody.yaml
  exact-run immutable custody + authenticated lookup/reconstruction composed into canonical custody deployment

StegVerse-org/LLM-adapter/llm_adapter/governed_manifest_ingress.py
  machine TEST/LIVE_STREAM ingress and governed-result egress
```

## Completed handoff tasks

```text
[done] public 0/1/2 navigation and pre-input guidance installed
[done] raw-user vs preformatted-machine ingress distinction installed
[done] versioned external ingress profile installed
[done] receipt-ID validation contract installed
[done] StegCore canonical exact-run receipt registry exists
[done] StegCore shared-backing provider contract exists
[done] Master Records exact-run custody API exists
[done] Master Records exact-run routes are composed into its canonical deployment target
```

## Worker continuation boundary

The remaining SDK work is narrowly defined. Do not create another evaluator, receipt registry, custody store, or Master Records transport authority in this repository.

Next executable tasks:

```text
1. wire Option 0 execution to the canonical manifested transaction/provider path;
2. accept either raw SDK-manifested input or validated stegverse.ingress-manifest.v1 input;
3. return the full ordinary evidence package plus canonical manifest_receipt_id;
4. retain the exact package through the shared-backing provider when an admitted transport is available;
5. wire Option 1 to replay by manifest_receipt_id only;
6. wire Option 2 to reconstruction by manifest_receipt_id only;
7. make unknown IDs fail closed with a user-readable explanation;
8. add integration tests proving guidance precedes input, shared backing preserves one-ID/one-run identity, and the original run is not mutated;
9. run the sovereign/local validation path and record inspectable PASS evidence here.
```

The user should never need internal commit SHAs, repository paths, transaction IDs, or receipt filenames to operate these flows.

## Activation boundary

Master Records canonical route composition is installed but production custody activation remains gated by the Master Records repository-wide persistent-storage, backup/restore, and live-authenticated round-trip readiness requirements. The SDK must not represent installed custody code as live production custody until those conditions are evidenced.

## Validation status

Repository code and tests are installed, but no sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or product activation until the owning local validation/release path executes the relevant tests and records evidence.
