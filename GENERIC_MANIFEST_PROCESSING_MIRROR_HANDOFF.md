# Generic Manifest Processing Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
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

## Files installed

```text
README.md
schemas/stegverse.ingress-manifest.v1.schema.json
docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md
inspection/examples/external-framework-generic-manifest.json
tests/test_generic_manifest_processing_contract.py
.github/workflows/evaluator-manifest-source-validation.yml
GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
```

## Merge and validation evidence

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
existing ingress/runtime/route/CLI and evaluator-boundary suites: PASS

Evaluator Contract Console Validation
run: 34273262400
job: 102219944073
result: SUCCESS
```

The source-validation workflow explicitly ran `python -m unittest tests.test_generic_manifest_processing_contract` and retained the credential boundary:

```text
GITHUB_TOKEN absent from validation process
GH_TOKEN absent from validation process
PYPI_API_TOKEN absent from validation process
GitHub runtime authority: NONE
```

## Readiness state

```text
README contract: COMPLETE_MERGED
machine-readable 0B schema: COMPLETE_MERGED
external-framework example: COMPLETE_MERGED
focused contract tests: COMPLETE_VALIDATED_MERGED
canonical existing 0B runtime binding: INSTALLED
processing route / payload-class separation: COMPLETE_VALIDATED
caller artifact-depth semantics: COMPLETE_DOCUMENTED_VALIDATED
source validation: PASS
contract-console validation: PASS
merge: COMPLETE
release/tag: NOT_REQUIRED_FOR_THIS CONTRACT-ONLY ADDITION UNLESS PACKAGE VERSION IS INTENTIONALLY CUT
```

The SDK is ready for an external framework to prepare a conforming `stegverse.ingress-manifest.v1` and submit it through option `0B`. Actual sovereign execution remains subject to the existing canonical runtime, governance evidence, and Master Records custody requirements; a documentation/schema merge does not manufacture a runtime result.

## Downstream propagation assessment task

After this merge, assess and update only where semantically pertinent:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

Do not duplicate the SDK processor or evaluator in downstream repositories. Propagate only public contract/usage semantics where those surfaces consume or document SDK interoperability.
