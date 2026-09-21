# SDK Public Developer Wiki Mirror Handoff

Updated: 2026-09-21
Goal Task ID: `SDK-PUBLIC-DEVELOPER-WIKI-001`
Central coordination handoff: `StegVerse-Labs/.github:docs/SDK_PUBLIC_DEVELOPER_WIKI_MIRROR_HANDOFF.md`
Target public origin: `https://sdk.stegverse.org/`
Status: `ACTIVE / SDK SOURCE MERGED + PAGES DEPLOYED / DNS TARGET CORRECTION REQUIRED`

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
- user-supplied GitHub Pages evidence shows custom domain `sdk.stegverse.org` is configured but currently reports `InvalidDNSError` while TLS certificate provisioning is at step 1/3;
- user-supplied Cloudflare evidence shows the current DNS record is `CNAME sdk.stegverse.org -> stegverse-org.stegverse.org`, DNS only;
- required GitHub Pages target is `stegverse-org.github.io`; the current target is therefore the concrete remaining publication defect.

## Manual DNS correction

In Cloudflare DNS for `stegverse.org`, edit the existing `sdk` CNAME record:

```text
Type: CNAME
Name: sdk
Target: stegverse-org.github.io
Proxy status: DNS only
TTL: Auto
```

Do not create a second `sdk` record. Replace the current target `stegverse-org.stegverse.org`.

After saving, return to `StegVerse-org/StegVerse-SDK -> Settings -> Pages`, press **Check again**, wait for the DNS check to succeed and certificate issuance to complete, then enable **Enforce HTTPS** when GitHub makes it available.

## Next executable step

After the DNS target is corrected, observe `https://sdk.stegverse.org/` and representative schema/example/receipt/provenance resources over HTTPS, then propagate the verified SDK wiki link to Site and reconcile the central handoff/completion state.
