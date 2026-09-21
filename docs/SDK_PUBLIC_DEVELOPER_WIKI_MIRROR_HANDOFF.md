# SDK Public Developer Wiki Mirror Handoff

Updated: 2026-09-21
Goal Task ID: `SDK-PUBLIC-DEVELOPER-WIKI-001`
Central coordination handoff: `StegVerse-Labs/.github:docs/SDK_PUBLIC_DEVELOPER_WIKI_MIRROR_HANDOFF.md`
Target public origin: `https://sdk.stegverse.org/`
Status: `ACTIVE / REPOSITORY-LOCAL PUBLICATION SOURCE IMPLEMENTED ON BRANCH / VALIDATION PENDING`

## Canonical design

The SDK repository itself is the canonical content source. The public developer wiki is generated from exact source files at publication time and emits a machine-readable SHA-256 source manifest. No duplicate SDK authority repository is created.

Published source set:

- `README.md`
- `SDK_MIRROR_HANDOFF.md`
- `docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md`
- `docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md`
- `schemas/stegverse.ingress-manifest.v1.schema.json`
- `inspection/examples/external-framework-generic-manifest.json`

## Public contract

The primary public flow is:

```text
source-native manifested data
-> stegverse.ingress-manifest.v1
-> caller-selected processing capability
-> declared installed runtime route
-> processor-specific evaluation
-> canonical Master Records custody
-> caller-selected return projection
-> returned artifact + manifest_receipt_id
-> replay / reconstruction where applicable
```

The public surface explicitly separates payload class, processing capability, runtime route, authority, caller projection, and canonical custody.

## Publication implementation

- builder: `scripts/build_sdk_public_wiki.py`
- validation: `tests/test_sdk_public_developer_wiki.py`
- Pages workflow: `.github/workflows/sdk-public-developer-wiki-pages.yml`
- generated site root: `_site/` (ephemeral build output; not canonical source)
- custom-domain source: generated `_site/CNAME = sdk.stegverse.org`
- provenance: generated `_site/wiki-source-manifest.json`

The workflow validates pull requests and deploys only from `main`.

## Authority boundary

The public wiki grants no governance, execution, transition, credential, custody, evidence, processor-selection, release, or publication-transition authority. Interlock/InTr, Master Records, Publisher, and TV/TVC retain their existing authority boundaries.

## Completion gates

1. exact-head SDK validation passes;
2. SDK PR merges;
3. main-branch Pages workflow succeeds;
4. `sdk.stegverse.org` publicly resolves over HTTPS;
5. representative schema, example, receipt-navigation, and provenance resources are observable;
6. Site adds and validates the SDK public-wiki link;
7. central handoff and Task Registry completion state are reconciled only after observed public evidence.

## Next executable step

Run exact-head validation for the repository-local implementation, repair any deterministic failures, merge only on evidence, then inspect the main Pages deployment and public branded hostname.
