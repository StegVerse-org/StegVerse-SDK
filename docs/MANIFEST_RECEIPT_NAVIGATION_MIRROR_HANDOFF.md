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
a174af5e593380d181b6f2928b0d2f995545e9c1  000 self-describing demo output contract
ca7b1c01c8ffcd2cd3235fa262e1f8f142974618  000 demo/output reconstruction tests
8bdfac96a0635d039251d88e82db87ddf2665cb6  CLI exposes 000 and prints demo output shape
```

## User contract

The CLI now exposes:

```text
[000] Demo test sequence without user-supplied manifest
[00]  User-defined run parameters
[0]   Submit data for governance
[1]   Replay previously run set
[2]   Reconstruct previously run set
```

Each selection displays process guidance before requesting the next input, and every choice explains the manifest shape, canonical vs editable fields, transition classes, receipt classes, caller-return projection, and Master Records custody boundary.

## Option 000 — self-describing demo sequence

Option `000` requires no user-supplied manifest. It emits a safe SDK-owned demonstration artifact with schema:

```text
stegverse.manifest-demo-output.v1
```

The output is deliberately self-describing. It contains:

```text
canonical_input_profile
canonical_manifest_example
sections[]
  section_id
  label
  fields
  transition_classes
  receipt_classes
  editable / generated_by
  authority boundary metadata
process_sequence[]
  order
  stage
  transition_class
  receipt_class
reconstruction_notes
  human
  llm
```

Purpose:

```text
human -> understand every part of the process and reconstruct a conforming manifest by hand
LLM   -> ingest the received demonstration outcome, understand the labeled manifest/process shape, and propose a new canonical input manifest from user preferences
```

The explanatory output wrapper is not itself a pre-authorized governance request. An LLM or user constructing a new request must output a normal `stegverse.ingress-manifest.v1` manifest, recompute required hashes, and submit it through Option `0` / the normal governed ingress path.

The demo never grants authority and never authorizes generated runtime receipts to be copied into a new input manifest.

## Manifest shape and class labeling

Every section now names both its transition classes and receipt classes.

```text
Profile / provenance
  transition classes: ingress, provenance
  receipt classes: manifest-admission, source-identity

Governed subject
  transition classes: subject, intent, candidate
  receipt classes: input-commitment, candidate-identity, request-identity

Integrity / attestation
  transition classes: canonicalization, verification
  receipt classes: hash-verification, attestation-verification

Governance / consequence trajectory
  transition classes: ingestion, governance, consequence, return_ingestion
  receipt classes: MANIFEST_ADMITTED, governance-decision,
                   execution-observation, RESULT_INGESTED,
                   receipt-chain-verification

Caller-return projection
  transition class: disclosure_projection
  receipt class: projection-decision

Exact-run locator
  transition class: custody_reference
  receipt class: manifest-receipt
```

The runtime-generated governance/consequence trajectory and exact-run locator are explicitly non-editable output sections. Their labels exist so a human or LLM can understand what happened, not so they can be asserted as authority in a future input manifest.

## Option 0 ingress modes

```text
0A raw/user data -> SDK creates manifest
0B preformatted machine manifest -> validate/canonicalize accepted ingress profile
```

Canonical external ingress profile:

```text
stegverse.ingress-manifest.v1
```

A structurally valid machine manifest means only that the machine output is acceptable for governance. It never means ALLOW and never grants execution authority.

## Caller projection / Master Records separation

The manifest is the canonical routing/declaration carrier for a submitted unit. It may request how user-disclosable state-transition evidence is projected back to the caller.

```text
return_projection.mode = ALL
  return all user-disclosable transition evidence

return_projection.mode = SELECTED
  return only named user-disclosable transition classes

return_projection.mode = NONE
  return no transition-detail receipt projection to the caller
```

`NONE` does not suppress or erase canonical ecosystem transition custody. Master Records remains independent of caller projection. The final `manifest_receipt_id` remains the exact-run locator even when caller transition projection is `NONE`.

Invariant fields produced by the SDK normalizer:

```text
controls_user_return_only: true
suppresses_master_records_custody: false
erases_ecosystem_transitions: false
grants_authority: false
```

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
[done] public 000/00/0/1/2 navigation installed
[done] 000 safe demo requires no user-supplied manifest
[done] 000 emits self-describing human/LLM-readable manifest-output shape
[done] every demo section labels fields, transition classes, and receipt classes
[done] demo differentiates editable input material from runtime-generated evidence
[done] manifest shape is explained on every governance choice
[done] user-defined ALL / SELECTED / NONE return projection installed
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

Do not create another evaluator, receipt registry, custody store, or Master Records transport authority in this repository.

Next executable tasks:

```text
1. bind Option 000 to an actual safe canonical manifested demo run, replacing placeholder generated values with real runtime values;
2. populate the final demo output from real transition receipts and the final manifest_receipt_id;
3. derive the public transition/receipt class registry from the actual canonical runtime receipt vocabulary rather than leaving labels as documentation-only mappings;
4. wire Option 00 parameters into the manifest produced/accepted by Option 0;
5. wire Option 0 execution to the canonical manifested transaction/provider path;
6. enforce return projection only after canonical governance/transition recording semantics are complete;
7. map SELECTED transition_classes to actual user-disclosable receipt classes without changing canonical custody;
8. wire Options 1 and 2 to receipt-ID replay/reconstruction;
9. add integration tests proving the 000 output can be used by a human or LLM to create a fresh conforming manifest while generated receipts/authority claims cannot be replayed as input authority;
10. run the sovereign/local validation path and record inspectable PASS evidence here.
```

## Activation boundary

Master Records canonical route composition is installed but production custody activation remains gated by the Master Records repository-wide persistent-storage, backup/restore, and live-authenticated round-trip readiness requirements. The SDK must not represent installed custody code as live production custody until those conditions are evidenced.

## Validation status

Repository code and tests are installed, but no sovereign/local test execution receipt was produced in this change session. Option `000` currently emits a self-describing demonstration shape with placeholders where an actual canonical demo run must later provide runtime-generated values. Do not claim COMPLETE, VALIDATED, RELEASED, or product activation until the owning local validation/release path executes the relevant tests and the demo is bound to the real governed runtime.
