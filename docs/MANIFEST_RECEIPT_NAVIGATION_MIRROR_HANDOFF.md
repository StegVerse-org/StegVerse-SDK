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
25de84e1febfe021c35d4208dc84cd6a32d15edc  tests
78498596670ed1fd02943bd914c5d755ab18f211  CLI governance menu
```

## User contract

The CLI now exposes:

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

## Cross-repository dependencies

```text
StegVerse-Labs/StegCore issue #85
StegVerse-Labs/StegCore/docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md
StegVerse-org/LLM-adapter issue #139
StegVerse-org/LLM-adapter/docs/GOVERNED_MANIFEST_INGRESS_MIRROR_HANDOFF.md
master-records/orchestration durable exact-run backing remains required for production activation
```

## Validation status

Repository code and tests are installed, but no sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or product activation until the owning local validation/release path executes the relevant tests and records evidence.
