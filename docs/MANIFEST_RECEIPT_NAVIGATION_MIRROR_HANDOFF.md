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

Recent installation commits:

```text
22775c19e3b3cd9b95b4d06e89caaf186ff9156a  00 parameters + return projection semantics
230f0eb13b05199756c85edd7c25a622881a28f8  return-projection custody-boundary tests
e6e6aa80eef3842af03ffee59895682e11845244  CLI exposes 00 option
```

## User contract

The CLI now exposes:

```text
[00] User-defined run parameters
[0]  Submit data for governance
[1]  Replay previously run set
[2]  Reconstruct previously run set
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

## Manifest routing and recording boundary

The manifest is the canonical routing/declaration carrier for a submitted unit. It declares how the unit enters the StegVerse path and may declare how state-transition evidence is projected back to the caller.

The user-facing return projection and ecosystem custody are distinct planes:

```text
manifest routing / requested return projection
  -> controls what user-disclosable transition evidence is returned to the caller

Master Records ecosystem custody
  -> records canonical ecosystem state transitions independently of caller return projection
```

This distinction is mandatory. A manifest may request that all, selected, or no transition details be returned to the caller. A `NONE` return projection means only that no transition-detail projection is included in the user-facing result. It MUST NOT be interpreted as evidence that no state transitions occurred or that Master Records recorded nothing.

Installed return-projection modes:

```text
ALL
  return all user-disclosable transition evidence for the run

SELECTED
  return only named user-disclosable transition classes

NONE
  return no state-transition detail projection to the caller
```

Invariant fields produced by the SDK normalizer:

```text
controls_user_return_only: true
suppresses_master_records_custody: false
erases_ecosystem_transitions: false
grants_authority: false
```

The final `manifest_receipt_id` remains an exact-run locator and not an execution/admissibility authority token.

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
[done] public 00/0/1/2 navigation and pre-input guidance installed
[done] user-defined return-projection contract installed
[done] ALL / SELECTED / NONE return modes installed
[done] explicit separation of user return projection from Master Records custody installed
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
1. wire Option 00 parameters into the manifest produced/accepted by Option 0;
2. wire Option 0 execution to the canonical manifested transaction/provider path;
3. enforce return projection only after canonical governance/transition recording semantics are complete;
4. prove `NONE` suppresses caller transition detail only and does not suppress Master Records custody;
5. return the permitted user-facing result plus canonical manifest_receipt_id;
6. retain the exact full package through the shared-backing provider when an admitted transport is available;
7. wire Option 1 to replay by manifest_receipt_id only;
8. wire Option 2 to reconstruction by manifest_receipt_id only;
9. make unknown IDs fail closed with a user-readable explanation;
10. add integration tests proving one-ID/one-run identity, caller projection behavior, full Master Records retention, and original-run immutability;
11. run the sovereign/local validation path and record inspectable PASS evidence here.
```

The user should never need internal commit SHAs, repository paths, transaction IDs, or receipt filenames to operate these flows.

## Activation boundary

Master Records canonical route composition is installed but production custody activation remains gated by the Master Records repository-wide persistent-storage, backup/restore, and live-authenticated round-trip readiness requirements. The SDK must not represent installed custody code as live production custody until those conditions are evidenced.

## Validation status

Repository code and tests are installed, but no sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or product activation until the owning local validation/release path executes the relevant tests and records evidence.
