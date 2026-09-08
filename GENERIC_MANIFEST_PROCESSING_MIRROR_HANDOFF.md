# Generic Manifest Processing Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
original_workstream: SDK-GENERIC-MANIFEST-PROCESSING-001
correction_workstream: SDK-PROCESSOR-GENERIC-MANIFEST-002
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This scoped handoff records the generalized external-framework manifest contract and the processor-generic correction that follows its original payload-class generalization. It does not supersede unrelated SDK workstreams in `SDK_MIRROR_HANDOFF.md`.

## Canonical goal

Make the SDK contract explicit and executable for external frameworks that:

1. retain their own semantic/data-class custody;
2. submit manifested data of any JSON-representable source-native class or a profiled payload commitment;
3. declare a caller-facing StegVerse processing capability independently of payload class;
4. bind that capability to an installed runtime route without conflating capability with route mechanics;
5. supply only the processor-specific evidence/state required by the selected processor;
6. choose caller-facing artifact depth without suppressing canonical Master Records custody; and
7. receive the selected processing/state-transition artifact plus `manifest_receipt_id`.

## Corrected contract

```text
external framework
-> source-native manifested data
-> stegverse.ingress-manifest.v1
-> processing.capability
-> processing.route_id == extensions.stegverse_route.route_id
-> processor-specific request/evidence
-> installed processor/runtime binding
-> canonical runtime + Master Records custody
-> return_projection
-> returned artifact + manifest_receipt_id
```

Invariants:

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance fields globally required by universal ingress: FALSE
unsupported processor/route execution: FALSE
```

## Current installed processor

```text
processing.capability: governance
processing.route_id: stegverse.route.canonical-governed.v1
processor-specific request: extensions.stegverse_governance_request
```

Governance is the currently installed executable 0B processor. It no longer defines universal manifest requirements for future processors. `candidate` and `extensions.stegverse_governance_request` are conditional governance requirements rather than global ingress requirements.

Existing v1 governance manifests that omit `processing` remain backward-compatible only when they declare `stegverse.route.canonical-governed.v1`; the SDK derives `processing.capability=governance` for that legacy case. Future/non-governance routes must declare `processing` explicitly.

## Payload commitment contract

```text
inline payload -> hashes.payload_sha256
commitment-only payload -> payload_commitment_profile + payload_commitment
currently published commitment profile -> sha256
sha256 commitment shape -> 64 lowercase hexadecimal characters
```

Opaque unprofiled commitments are not treated as independently verifiable input.

## Artifact-depth semantics

```text
governance artifact only
  -> return_projection.mode=SELECTED with governance/result classes

governance + selected transition result
  -> return_projection.mode=SELECTED with governance plus requested transition/result classes

full user-disclosable transition artifact
  -> return_projection.mode=ALL

minimal locator/no transition-detail projection
  -> return_projection.mode=NONE
```

`NONE` is not the governance-artifact-only mode. All modes preserve canonical custody.

## Original merge evidence — SDK-GENERIC-MANIFEST-PROCESSING-001

```text
PR: #124
merged: TRUE
merge commit: 4cb4c766199debe8d4a34fef3ea5f99b698c81ca
validated head: d4d7cc1bc06b66d0e8c77dd97e17afc166d21b9a

Evaluator Manifest Source Validation (Non-Authorizing)
run: 34273262341
job: 102219943870
result: SUCCESS
focused generic-manifest tests: 4/4 PASS

Evaluator Contract Console Validation
run: 34273262400
job: 102219944073
result: SUCCESS
```

That merge correctly generalized source-native payload classes and caller artifact projection but still globally required governance-specific fields and hard-coded the governance route in the schema. `SDK-PROCESSOR-GENERIC-MANIFEST-002` corrects those residual couplings without rolling back the original work.

## Processor-generic correction — SDK-PROCESSOR-GENERIC-MANIFEST-002

```text
branch: fix/processor-generic-manifest-contract
PR: #126
validated head: 771a28c7428c2adc92823b10f9bf031ecf2f710f
merge commit: cb53cb0304efbd21e5a5700677c4f3fb8ef7b874
state: COMPLETE_VALIDATED_MERGED
README impact: REQUIRED_AND_UPDATED
manual user work: NONE
```

Validation evidence for the exact merged PR head:

```text
Manifest Builder Source Validation (Non-Authorizing)
run: 34280687649
result: SUCCESS

Evaluator Manifest Source Validation (Non-Authorizing)
run: 34280687697
result: SUCCESS
focused processor-generic manifest tests: 8/8 PASS

Evaluator Contract Console Validation
run: 34280687650
result: SUCCESS

SDK Package Artifact Validation (Non-Authorizing)
run: 34280687651
result: SUCCESS
wheel build/install/smoke: PASS
```

An initial branch revision accidentally omitted the pre-existing `run_000_demo` export and exposed three stale error-message expectations. Validation caught both classes of regression. The demo entry was restored, fail-closed error compatibility was preserved without weakening the new processing contract, and the exact final PR head passed all four validation lanes before merge.

### Files changed/added

```text
stegverse/manifest_contract.py                          processor-generic structural validator
schemas/stegverse.ingress-manifest.v1.schema.json       universal/conditional processor schema
stegverse/route_resolution.py                           processor capability bound to installed route
stegverse/governance_ingress_runtime.py                 explicit capability/route verification and processor dispatch boundary
stegverse/manifest_builder.py                           emits processing capability separately from route
inspection/examples/external-framework-generic-manifest.json
tests/test_generic_manifest_processing_contract.py
tests/test_manifest_builder.py
docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md
README.md
.github/workflows/evaluator-manifest-source-validation.yml
.github/workflows/manifest-builder-source-validation.yml
GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
MANIFEST_BUILDER_MIRROR_HANDOFF.md
```

### Completed correction assertions

```text
source-native payload class survives canonicalization: PASS
payload is not coerced into candidate/action semantics: PASS
non-governance structural manifest does not require governance candidate/request: PASS
unsupported non-installed processor route fails closed before execution: PASS
processing capability and runtime route are separately declared and cross-checked: PASS
governance processing still requires complete governance request and matching candidate: PASS
legacy canonical-governed v1 manifest without processing remains compatible: PASS
payload commitment requires explicit verification profile: PASS
SELECTED/ALL/NONE projection semantics remain unchanged: PASS
manifest/processing/route selection grants authority: FALSE
Master Records custody suppression by projection: FALSE
```

## Preflight determination

- `SDK_MIRROR_HANDOFF.md` and this scoped handoff were read before mutation.
- The existing Manifest Builder handoff was inspected because the builder emits the affected manifest profile.
- No new evaluator, governance engine, credential authority, or custody path was introduced.
- README impact was material because public manifest semantics changed; README was updated in the same change set.
- Existing `stegverse.ingress-manifest.v1` identity is preserved with backward-compatible governance derivation; no silent processor substitution is permitted.
- Validation covered the generic contract, builder, route resolution, current 0B runtime, CLI, console, package artifact, and evaluator-manifest source lane before merge.

## Readiness

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
processor-generic structural ingress: COMPLETE
current executable 0B processor: governance
future processor schema coupling to governance: REMOVED
new processor installed by this workstream: NONE
release/tag required solely for this correction: NO SEPARATE TAG REQUIRED; package artifact validation PASS
```

## Next integration goal

Assess and update only where semantically pertinent:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

Do not duplicate the SDK processor or evaluator in downstream repositories. Propagate only public contract/usage semantics where those surfaces consume or document SDK interoperability.
