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
stegverse/demo_data/manifest_000_governance_outcomes.json
tests/test_governance_navigation.py
```

Recent installation commits:

```text
22775c19e3b3cd9b95b4d06e89caaf186ff9156a  00 parameters + return projection semantics
29a9bf4764f167499aa095c919a0f118dc3cdf78  manifest-shape guidance on every governance choice
a174af5e593380d181b6f2928b0d2f995545e9c1  000 self-describing demo output contract
b02f663ad0c7e6e80e867fe359e787c417d400d1  000 governance-outcome demo dataset
8c0ec2471529289eb2909d18a21cc59c529c0172  prepend/validate full governance outcome vocabulary
4d94ed8aac4fd558356cffd41a27fc2ecba6e92a  manifest-label projection + dataset processing contract
a271c8ad4d347805ca73b098f1eb30655b50c32a  manifest-label/dataset-processing tests
155859ca2b81128430160b683fba4bda25b4a163  outcome descriptions converted to manifest labels
```

## User contract

The CLI exposes:

```text
[000] Demo test sequence without user-supplied manifest
[00]  User-defined run parameters
[0]   Submit data for governance
[1]   Replay previously run set
[2]   Reconstruct previously run set
```

Every choice explains the manifest shape, transition/receipt classes, caller return controls, exact-run locator, and Master Records custody boundary.

## Option 000 — demo dataset is the submitted data

Option `000` uses an SDK-owned dataset with schema:

```text
stegverse.000-demo-dataset.v1
```

The dataset contains exactly one teaching example of each current governance disposition:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

Each outcome description is encoded as a `manifest_label` using:

```text
profile: stegverse.manifest-labels.v1
title
description
transition_classes
receipt_classes
editable
authority_effect
```

The examples are demo data, not actual governance decisions and not authority.

The entire dataset is embedded as:

```text
canonical_manifest_example.payload
```

and its canonical SHA-256 is placed in:

```text
canonical_manifest_example.hashes.payload_sha256
demo_dataset_processing.dataset_sha256
```

This is the required binding for making the submitted dataset evident in the final demo output.

The demo output also carries a `demo_dataset_processing` object. Until Option 000 is bound to a real canonical manifested run, it must report:

```text
canonical_processing_status: PENDING_RUNTIME_BINDING
do_not_claim_processed_until_receipts_exist: true
```

A completed runtime-bound 000 demo is not allowed to claim that the dataset was processed merely because it was embedded in the manifest. It must replace the pending status with directly inspectable runtime evidence containing at least:

```text
MANIFEST_ADMITTED
governance-decision
RESULT_INGESTED
manifest-receipt
manifest_receipt_id
receipt_chain_head
governance_state
chain_verified
```

That is the acceptance boundary for the statement "the demo dataset was submitted and processed."

## Manifest labels are an ordinary manifest return control

Explanatory descriptions are no longer a 000-only wrapper convention. They are represented by the manifest field:

```yaml
manifest_labels:
  profile: stegverse.manifest-labels.v1
  mode: ALL | SELECTED | NONE
  sections: []
  include_field_descriptions: true
  include_transition_class_labels: true
  include_receipt_class_labels: true
  include_editability_labels: true
  include_authority_boundary_labels: true
```

`manifest_labels` controls explanatory labeling of the caller-facing return package only. It does not alter governance, grant authority, suppress receipts in Master Records, or rewrite the canonical run.

Modes:

```text
ALL
  include explanatory manifest labels for all returned sections

SELECTED
  include explanatory labels only for named sections

NONE
  include no explanatory manifest labels
```

This is independent from `return_projection`:

```text
return_projection -> which user-disclosable transition receipts are returned
manifest_labels   -> how returned sections are labeled/explained
Master Records    -> canonical ecosystem custody, independent of both
```

Therefore an Option `0` machine manifest may request the same explanatory return package demonstrated by Option `000`, for example:

```yaml
return_projection:
  mode: SELECTED
  transition_classes:
    - governance
    - return_ingestion

manifest_labels:
  profile: stegverse.manifest-labels.v1
  mode: ALL
```

That request means "return only these receipt classes, but explain/label every returned section." It does not mean only those transitions were recorded in Master Records.

## Option 000 self-describing output

The demo output schema remains:

```text
stegverse.manifest-demo-output.v1
```

Every output section now has a literal `manifest_label` object containing:

```text
title
description
transition_classes
receipt_classes
editable
authority_effect
```

The demo also requests:

```text
manifest_labels.mode = ALL
```

so all descriptions are part of the 000 demo's requested return package, not hidden implementation commentary.

Human/LLM purpose:

```text
human -> inspect what data was submitted, what each process section means, what receipt class proves it, and reconstruct a new manifest by hand
LLM   -> ingest the labeled return package and produce a new stegverse.ingress-manifest.v1 manifest reflecting the user's desired data, receipt projection, and explanation-label projection
```

Generated governance receipts, custody receipts, and authority claims remain non-editable observations and must not be copied into a new manifest as authority.

## Option 0 ingress modes

```text
0A raw/user data -> SDK creates manifest
0B preformatted machine manifest -> validate/canonicalize accepted ingress profile
```

Canonical external ingress profile:

```text
stegverse.ingress-manifest.v1
```

The validator now accepts and normalizes `manifest_labels` as part of that ordinary manifest profile. Structural validity still means only that the manifest is acceptable input to governance; it never means ALLOW and never grants execution authority.

## Caller projection / Master Records separation

```text
return_projection.mode = ALL | SELECTED | NONE
manifest_labels.mode   = ALL | SELECTED | NONE
```

Both are caller-return controls. Neither may suppress or erase canonical ecosystem state-transition custody. The final `manifest_receipt_id` remains the exact-run locator even when receipt projection and/or explanation-label projection is `NONE`.

## Cross-repository implementation available

```text
StegVerse-Labs/StegCore/src/stegcore/manifest_receipts.py
StegVerse-Labs/StegCore/src/stegcore/manifest_receipt_provider.py
  canonical exact-run receipt semantics + shared backing provider

master-records/orchestration/services/manifest_receipt_custody.py
master-records/orchestration/services/manifest_receipt_custody_api.py
master-records/orchestration/services/canonical_custody_app.py
  immutable exact-run custody + authenticated lookup/reconstruction

StegVerse-org/LLM-adapter/llm_adapter/governed_manifest_ingress.py
  machine TEST/LIVE_STREAM governed ingress/egress
```

## Completed handoff tasks

```text
[done] public 000/00/0/1/2 navigation installed
[done] 000 SDK-owned demo dataset contains ALLOW/DENY/REVIEW/FAIL_CLOSED teaching records
[done] 000 outcome descriptions encoded as manifest_label objects
[done] entire 000 dataset embedded as canonical demo payload
[done] dataset hash bound into canonical demo manifest + processing evidence object
[done] explicit no-false-processing-claim boundary installed
[done] manifest_labels added as ordinary stegverse.ingress-manifest.v1 return control
[done] ALL / SELECTED / NONE manifest-label modes installed
[done] option 0 external manifest validator accepts/normalizes manifest_labels
[done] every demo section carries a literal manifest_label
[done] return_projection remains independent from manifest_labels
[done] both caller-return controls remain independent from Master Records custody
[done] raw-user vs preformatted-machine ingress distinction installed
[done] StegCore canonical exact-run receipt registry/provider exists
[done] Master Records exact-run custody routes are composed into canonical deployment target
```

## Worker continuation boundary

Do not redesign receipt custody, receipt IDs, governance authority, or explanatory label semantics.

Next executable tasks:

```text
1. bind Option 000 to an actual safe canonical manifested demo run;
2. submit the ENTIRE stegverse.000-demo-dataset.v1 object as that run's payload;
3. replace PENDING_RUNTIME_BINDING with actual MANIFEST_ADMITTED / governance / RESULT_INGESTED / manifest-receipt evidence;
4. prove the returned payload hash matches the exact SDK-owned dataset hash;
5. populate the actual manifest_receipt_id and receipt_chain_head;
6. render manifest_label descriptions from manifest_labels after canonical transition recording is complete;
7. wire manifest_labels through ordinary Option 0 execution/return packaging as well as 000;
8. derive public transition/receipt classes from the canonical runtime receipt vocabulary;
9. wire return_projection SELECTED/NONE only after full canonical recording;
10. wire Options 1/2 to exact-run replay/reconstruction;
11. add end-to-end tests proving a human/LLM can use the labeled returned package to construct a fresh conforming manifest without importing generated authority;
12. run sovereign/local validation and retain inspectable PASS evidence.
```

## Activation boundary

Master Records production activation remains gated by its repository-wide persistent-storage, backup/restore, and live authenticated round-trip requirements. SDK labels and demo packaging must not be represented as proof of live custody activation.

## Validation status

The manifest-label and 000 dataset submission/processing contracts are installed with tests, but no sovereign/local test execution receipt was produced in this session. Option `000` still reports canonical processing as `PENDING_RUNTIME_BINDING`; this is intentional and prevents a false claim that the dataset was processed before real canonical receipts exist.
