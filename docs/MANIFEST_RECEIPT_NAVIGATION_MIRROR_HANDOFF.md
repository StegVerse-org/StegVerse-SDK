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
  canonical manifest_receipt_id + evidence/replay/reconstruct provider-neutral semantics

master-records/orchestration/services/manifest_receipt_custody.py
master-records/orchestration/services/manifest_receipt_custody_api.py
  exact-run immutable custody + authenticated lookup/reconstruction primitives

StegVerse-org/LLM-adapter/llm_adapter/governed_manifest_ingress.py
  machine TEST/LIVE_STREAM ingress and governed-result egress
```

## Worker continuation boundary

The remaining SDK work is now narrowly defined. Do not create another evaluator, receipt registry, or custody store in this repository.

Next executable tasks:

```text
1. wire Option 0 execution to the canonical manifested transaction provider;
2. accept either raw SDK-manifested input or validated stegverse.ingress-manifest.v1 input;
3. return the full ordinary evidence package plus canonical manifest_receipt_id;
4. wire Option 1 to replay by manifest_receipt_id only;
5. wire Option 2 to reconstruction by manifest_receipt_id only;
6. make unknown IDs fail closed with a user-readable explanation;
7. add integration tests proving the UI guidance appears before input and the original run is not mutated;
8. run the sovereign/local validation path and record inspectable PASS evidence here.
```

The user should never need internal commit SHAs, repository paths, transaction IDs, or receipt filenames to operate these flows.

## Validation status

Repository code and tests are installed, but no sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or product activation until the owning local validation/release path executes the relevant tests and records evidence.
