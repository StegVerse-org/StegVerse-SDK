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
29a9bf4764f167499aa095c919a0f118dc3cdf78  manifest-shape guidance on every governance choice
0eafc7f0aadb5df79560a74f6d9f7f63df7db98b  manifest-shape/projection guidance tests
```

## User contract

The CLI now exposes:

```text
[00] User-defined run parameters
[0]  Submit data for governance
[1]  Replay previously run set
[2]  Reconstruct previously run set
```

Each selection displays process guidance before requesting the next input, and every choice now also explains the shape of the manifest, which fields are part of canonical run identity/governance, and which fields control caller-facing receipt projection.

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

## Manifest shape shown in every choice

The SDK now explains the manifest as four conceptual groups:

```text
1. profile / provenance
   manifest_profile
   manifest_profile_version
   source_framework
   source_instance
   source_output_id
   created_at
   freshness

2. governed subject
   payload OR payload_commitment
   candidate
   declared_intent
   requested_consequence
   context_refs

3. integrity / attestation
   canonicalization_profile
   hashes
   attestation
   extensions

4. caller-return projection
   return_projection.mode
   return_projection.transition_classes
```

Mandatory boundary:

```text
required identity / integrity / governed-subject / routing fields
  != caller-disclosure controls
```

Required canonical fields cannot be set to `NONE` merely to hide them from governance. Optional provenance/extension fields may be null or empty only where the profile explicitly permits it.

The editable `NONE` control applies to caller-facing transition-receipt projection. For focused output under option `00`, the user should use:

```text
return_projection:
  mode: SELECTED
  transition_classes:
    - <wanted transition class>
    - <wanted transition class>
```

This is the mechanism for requesting receipts around specific transitions without receiving the whole user-disclosable receipted trajectory.

`return_projection.mode = NONE` means no transition-detail receipts are returned to that caller. It does not suppress or erase canonical ecosystem transition custody. The final `manifest_receipt_id` remains the exact-run locator even when the transition-detail projection is `NONE`.

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
[done] manifest shape is explained on every governance choice
[done] required canonical fields are distinguished from caller-return projection fields
[done] focused SELECTED transition receipt projection is documented
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
4. map SELECTED transition_classes to actual user-disclosable receipt classes without changing canonical custody;
5. prove NONE suppresses caller transition detail only and does not suppress Master Records custody;
6. return the permitted user-facing result plus canonical manifest_receipt_id;
7. retain the exact full package through the shared-backing provider when an admitted transport is available;
8. wire Option 1 to replay by manifest_receipt_id only;
9. wire Option 2 to reconstruction by manifest_receipt_id only;
10. make unknown IDs fail closed with a user-readable explanation;
11. add integration tests proving one-ID/one-run identity, focused caller projection behavior, full Master Records retention, and original-run immutability;
12. run the sovereign/local validation path and record inspectable PASS evidence here.
```

The user should never need internal commit SHAs, repository paths, transaction IDs, or receipt filenames to operate these flows.

## Activation boundary

Master Records canonical route composition is installed but production custody activation remains gated by the Master Records repository-wide persistent-storage, backup/restore, and live-authenticated round-trip readiness requirements. The SDK must not represent installed custody code as live production custody until those conditions are evidenced.

## Validation status

Repository code and tests are installed, but no sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or product activation until the owning local validation/release path executes the relevant tests and records evidence.
