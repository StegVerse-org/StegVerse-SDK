# Generic Manifest Processing Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
branch: sdk-generic-manifest-processing-contract
parent_handoff: SDK_MIRROR_HANDOFF.md
workstream: SDK-GENERIC-MANIFEST-PROCESSING-001
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This scoped handoff records the generalized external-framework manifest contract introduced from the canonical SDK state. It does not supersede unrelated SDK workstreams in `SDK_MIRROR_HANDOFF.md`.

## Goal

Make the SDK contract explicit and executable for external frameworks that:

1. retain their own semantic/data-class custody;
2. submit manifested data of any JSON-representable source-native class or a payload commitment;
3. select an installed StegVerse processing route independently of payload class;
4. for governance, supply the complete processor-specific governance evidence/state without the SDK inventing missing semantics;
5. choose the caller-facing artifact depth without suppressing canonical Master Records custody; and
6. receive the selected governance/state-transition artifact plus `manifest_receipt_id`.

## Contract

```text
external framework
-> source-native manifested data
-> stegverse.ingress-manifest.v1
-> extensions.stegverse_route
-> processor-specific request/evidence
-> canonical runtime + Master Records custody
-> return_projection
-> returned artifact + manifest_receipt_id
```

Invariant:

```text
payload class != processing class
processing selection != authority
caller projection != canonical custody
```

Current installed processing route:

```text
stegverse.route.canonical-governed.v1
```

Governance-specific complete request:

```text
extensions.stegverse_governance_request
```

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

## Files installed in this workstream

```text
README.md
schemas/stegverse.ingress-manifest.v1.schema.json
docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md
inspection/examples/external-framework-generic-manifest.json
tests/test_generic_manifest_processing_contract.py
GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
```

## Validation requirements

Before release/merge claim:

```text
python -m unittest tests.test_generic_manifest_processing_contract
python -m unittest tests.test_governance_navigation
python -m unittest tests.test_governance_ingress_runtime
python -m unittest tests.test_cli_preformatted_manifest
pytest tests/ -q
```

Required assertions:

```text
external source-native payload class survives canonicalization
payload is not coerced into candidate/action semantics
published route resolves independently of payload class
candidate remains hash-bound to governance request
SELECTED projection reaches public request
manifest grants authority: FALSE
Master Records custody suppression by projection: FALSE
```

## Readiness state

```text
README contract: IMPLEMENTED_ON_BRANCH
machine-readable 0B schema: IMPLEMENTED_ON_BRANCH
external-framework example: IMPLEMENTED_ON_BRANCH
focused contract tests: IMPLEMENTED_ON_BRANCH
canonical existing 0B runtime binding: PREEXISTING_INSTALLED
CI / source validation: PENDING_PR
merge: PENDING
release/tag: NOT YET ELIGIBLE
```

## Downstream propagation targets after merge/release readiness

Assess and update only where semantically pertinent:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

Do not duplicate the SDK processor or evaluator in downstream repositories. Propagate only public contract/usage semantics where those surfaces consume or document SDK interoperability.
