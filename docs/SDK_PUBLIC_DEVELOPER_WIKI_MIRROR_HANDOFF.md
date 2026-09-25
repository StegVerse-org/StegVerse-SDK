# SDK Public Developer Wiki Mirror Handoff

Updated: 2026-09-21
Goal Task ID: `SDK-PUBLIC-DEVELOPER-WIKI-001`
Central coordination handoff: `StegVerse-Labs/.github:docs/SDK_PUBLIC_DEVELOPER_WIKI_MIRROR_HANDOFF.md`
Target public origin: `https://sdk.stegverse.org/`
Status: `RETIRED / COMPLETE / PUBLICLY OBSERVED`

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

## Evidence reconciliation — 2026-09-21

- canonical Task Registry registration merged via `StegVerse-Labs/.github#2490` as `608c104f45db5dbe9c29d498881fb3267c562cc7`;
- SDK implementation merged via `StegVerse-org/StegVerse-SDK#300` as `e454dfa9042884939a0e6cde3c15a2fd2e386be5`;
- exact-head SDK wiki validation passed after the first deterministic heading-case defect was repaired;
- main `Publish SDK Developer Wiki` workflow ran successfully and GitHub Pages reports the site was deployed to the `github-pages` environment;
- earlier user-supplied GitHub Pages evidence showed `InvalidDNSError` while the Cloudflare CNAME incorrectly targeted `stegverse-org.stegverse.org`;
- the user corrected the existing DNS-only `sdk` CNAME to `stegverse-org.github.io`;
- subsequent user-supplied GitHub Pages evidence now reports `DNS check successful` for `sdk.stegverse.org`;
- subsequent supplied GitHub Pages evidence shows the branded root live, DNS check successful, and Enforce HTTPS enabled.

## Current manual prerequisite

None. The supplied GitHub Pages evidence shows the branded root live, DNS check successful, and Enforce HTTPS enabled.

## Site propagation

Site PR #1446 merged as `110de303b9f88922c926c4a75dbabcc86630d42e`. Its exact-head validation passed, and post-merge Site Pages deployment run `35637977873` completed successfully.

## Independent public observation closure

GitHub-hosted observation run `35649334318` performed fresh HTTPS GETs against all four required public evidence surfaces and returned `all_passed=true`. Retained observation artifact: `10661262634`.

Observed served-body evidence:

- ingress schema: HTTP 200, SHA-256 `9a2624478eb537919bfb69d189d2f8190ee66cf6de460bce94f052a9a4ee7b04`;
- external-framework example: HTTP 200, SHA-256 `e15ec3fd92da469c5c9d544784727cb00787badca7300a80d5eb2049c0237354`;
- manifest-receipt navigation: HTTP 200, SHA-256 `b70702184d02196dec7df1b6d8c5d90d393bf53763e5702f6d8d1bfe26d2d3dd`;
- Site `wikis.html`: HTTP 200, SHA-256 `b3f40d8f52d825ccf66812a67f7df0a10bc6e26062daf66b2acbb4422973afd3`.

SDK observation harness PR #305 merged as `e63aa7929e9ebac7a3c6c9d856cd4be9218cbb38`. Site closure PR #1447 merged as `d40a70e73c17f77205cf8c2884bc38d227e67a40`. Site claim/COSV terminalization PR #1448 merged as `570c2917369d8b634d33a79f63cf327b9158b45d`.

## Terminal state

```text
coordination_state: RETIRED
checkout_state: COMPLETED
completion.claimed: true
completion.validated: true
manual_user_action_required: false
```

The public wiki remains documentation/navigation only. Closure grants no governance, execution, transition, credential, custody, evidence, processor-selection, release, or publication-transition authority.

## Independent public observation harness

A repository-local observation-only harness now performs fresh HTTPS GETs from GitHub-hosted Actions to the four remaining public evidence surfaces:

- `https://sdk.stegverse.org/source/schemas/stegverse.ingress-manifest.v1.schema.json`
- `https://sdk.stegverse.org/source/inspection/examples/external-framework-generic-manifest.json`
- `https://sdk.stegverse.org/source/docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md`
- `https://stegverse.org/wikis.html`

Source: `scripts/observe_sdk_public_wiki.py`
Workflow: `.github/workflows/sdk-public-wiki-observation.yml`

The observer verifies HTTP 200 plus stable served-body markers and records status, final URL, content type, byte length, and SHA-256. It has `authority_effect=NONE_OBSERVATION_ONLY` and must not substitute source/build/deployment evidence for served-body observation.

## September 25, 2026 — optional DeepWiki capture for review (not a new release)

The originally released SDK wiki remains `RETIRED / COMPLETED` as documented above. Under existing central open-source-strategy owner `ECOSYSTEM-OPEN-SOURCE-STRATEGY-001`, COSV `20010010100000`, branch `docs/deepwiki-readonly-review-20260925` proposes a **non-publishing** external generated-documentation capture: `scripts/export_deepwiki_review.py`, test `tests/test_export_deepwiki_review.py`, and PR-only/manual `.github/workflows/deepwiki-readonly-review.yml`. It requests public no-auth DeepWiki MCP `read_wiki_structure` and `read_wiki_contents` for exactly `StegVerse-org/StegVerse-SDK`, stores raw tool outputs plus text/sha256 in a short-retention CI artifact, never edits SDK source at execution, and does not replace the existing Pages builder or mutate the published wiki. Preview material is explicitly unreviewed external generated text; no completeness claim absent actual page-tree/content reconciliation. PR exact-head CI, successful real MCP retrieval, import/review and subsequent Pages publication **must be independently observed**. No `.devin/wiki.json` until the entire current wiki page tree is available; incomplete config can truncate page coverage. This is an optional future improvement adjacent to the retired developer-wiki goal, not a reopening of its completed historical work. Any reviewed publication uses existing applicable publication and propagation owners and original Pages source-of-truth, not direct third-party mutation.

### Actual read-only full-structure/content fetch — September 25, 2026

The review exporter ran successfully against public DeepWiki MCP in SDK draft [PR #322](https://github.com/StegVerse-org/StegVerse-SDK/pull/322). [Run 36104137361](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36104137361) passed all three fail-closed local exporter tests and the actual remote structure+contents requests, retaining raw JSON, Markdown and SHA-256 manifest in artifact [10850037472](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36104137361/artifacts/10850037472). The returned structure has 38 entries (8 root, 30 nested); full content has 38 uniquely labeled sections and matches every returned heading. See `docs/deepwiki-review/INDEX.md` for exact titles and hashes. This exceeds standard `.devin/wiki.json` 30-page explicit configuration limit; do **not** install one that loses coverage. CI evidence capture is **not** evidence of source code/diagram correctness, copyright reuse clearance, Master Records custody, exact-head release, reviewed Markdown import or new Pages deployment. Keep original SDK wiki completion historically unchanged. Draft PR #322 is a source-only optional enhancement, not a reopening of retired Goal Task ID.

### Exact-head review-export hardening and 90-day retention

Review-only exporter now fail-closes unless every returned hierarchical page title occurs **exactly once** in the full-content `# Page:` sections, preventing silent partial retrieval. Following the new checks, SDK PR #322 head `0a1269ecc3d9a52326c457d0fcf8aa5d5878e251` received twelve completed successful applicable pull-request workflows, including the actual no-auth DeepWiki capture, original SDK wiki PR validation and public wiki observation workflow. This is CI/source evidence, not a new main deployment. On source branch the evidence-export workflow retains subsequent review artifacts for 90 days. One recent successful run before this handoff addition is `36105012922`; new exact-head CI must be checked after this handoff change. The historic published public SDK wiki stays unchanged, and the new generated content is still unreviewed, not committed into authoritative site sources or published.

## 2026-09-25 generated citation-audit continuation

The retired original SDK wiki task remains RETIRED/COMPLETED. Under existing open-source owner ECOSYSTEM-OPEN-SOURCE-STRATEGY-001 / COSV 20010010100000, review-only SDK PR #322 retains the no-auth 38-page DeepWiki export. `docs/deepwiki-review/CITATION_AUDIT.md` now records independent exact-artifact hash readback and classification of 659 empty targets: 599 candidate numeric line locators, 41 other simple labels and 19 malformed/context-sensitive occurrences. Candidate labels are **not** source-verified, and no generated content was imported or published. Current PR head validation must be repeated after this documentation update.
